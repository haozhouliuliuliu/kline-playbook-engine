"""江河真实模型 provider 的离线 CANDIDATE 合同。

只定义可审计请求/响应证据，不包含 HTTP、SDK、密钥读取或真实调用。所有 artifact
compound identity 均由本模块重算；任何 caller 声明不一致都会失败闭合。
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field, fields
from datetime import datetime, timezone
from enum import Enum
from hashlib import sha256
import json
import re
from typing import Any, Mapping, Sequence

from src.jianghe_ai_trader import JiangheObservation, canonical_visual_artifact_identity
from src.jianghe_fidelity_evaluation import InputEvidence
from src.jianghe_response_normalizer import (
    EvaluatorSideJudgment,
    JiangheResponseNormalizer,
    NormalizedJiangheDecision,
    build_fidelity_response_payload,
    extract_runtime_fidelity_evidence,
)
from src.jianghe_visual_renderer import (
    ARTIFACT_KIND as INTEGRATED_VISUAL_ARTIFACT_KIND,
    PNG_MIME as INTEGRATED_PNG_MIME,
    RENDERER_VERSION as INTEGRATED_RENDERER_VERSION,
    JiangheVisualRenderer,
    VisualObservationSpec,
    panels_from_observation_bars,
)


CONTRACT_VERSION = "JIANGHE_MODEL_PROVIDER_CONTRACT_V0_3"
STRUCTURED_ARTIFACT_KIND = "JIANGHE_STRUCTURED_OBSERVATION_V0_1"
VISUAL_ARTIFACT_KIND = "JIANGHE_VISUAL_OBSERVATION_V0_1"
PNG_MIME = "image/png"


class FidelityTrack(str, Enum):
    SEMANTIC = "SEMANTIC"
    VISUAL = "VISUAL"
    STRUCTURED = "STRUCTURED"
    DUAL_INPUT = "DUAL_INPUT"
    OPERATIONAL_PROVIDER = "OPERATIONAL_PROVIDER"


class CandidateStatus(str, Enum):
    CANDIDATE = "CANDIDATE"
    VERIFIED = "VERIFIED"
    ADOPTED = "ADOPTED"


class VersionBinding(str, Enum):
    EXACT_SNAPSHOT_PINNED = "EXACT_SNAPSHOT_PINNED"
    PROVIDER_RESOLVED_RESPONSE = "PROVIDER_RESOLVED_RESPONSE"
    MUTABLE_ALIAS_CANDIDATE_ONLY = "MUTABLE_ALIAS_CANDIDATE_ONLY"


class ModelDriftPolicy(str, Enum):
    EXACT_SNAPSHOT_REQUIRED = "EXACT_SNAPSHOT_REQUIRED"
    ALIAS_MAY_DRIFT = "ALIAS_MAY_DRIFT"
    PROVIDER_UNDOCUMENTED = "PROVIDER_UNDOCUMENTED"


class LiveInvocationDisabledError(RuntimeError):
    pass


_ENVIRONMENT_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")
_SHA256_IDENTITY = re.compile(r"^[0-9a-f]{64}$")
_FORBIDDEN_FIELDS = frozenset({
    "outcome", "candidate_outcome", "pnl", "profit", "profits", "loss", "losses",
    "win_rate", "winrate", "sharpe", "expectancy", "future_price", "future_return",
    "return", "returns", "equity_curve",
})


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(
            value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
        )
    except (TypeError, ValueError) as error:
        raise ValueError("provider contract 数据必须是 JSON 兼容值") from error


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} 必须是非空字符串")
    return value


def _require_identity(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not _SHA256_IDENTITY.fullmatch(value):
        raise ValueError(f"{field_name} 必须是 lowercase 64 位 sha256 identity")
    return value


def _require_aware(value: object, field_name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} 必须是带时区的时间")
    return value


def _strict_bool(value: object, field_name: str) -> bool:
    if type(value) is not bool:
        raise ValueError(f"{field_name} 必须是严格布尔值")
    return value


def _scan_forbidden(value: object, path: str) -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} 的键必须是字符串")
            normalized = key.lower().replace("-", "_").replace(" ", "_")
            if normalized in _FORBIDDEN_FIELDS:
                raise ValueError(f"{path} 不得包含结果字段: {key}")
            _scan_forbidden(nested, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _scan_forbidden(nested, f"{path}[{index}]")


def _mapping(value: object, field_name: str, *, allow_empty: bool = False) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or (not value and not allow_empty):
        raise ValueError(f"{field_name} 必须是 JSON 对象")
    if any(not isinstance(key, str) or not key for key in value):
        raise ValueError(f"{field_name} 的键必须是非空字符串")
    _canonical_json(value)
    _scan_forbidden(value, field_name)
    return value


def _sorted_unique_text(values: Sequence[str], field_name: str) -> tuple[str, ...]:
    if any(not isinstance(value, str) or not value for value in values):
        raise ValueError(f"{field_name} 必须是去重后的非空字符串")
    result = tuple(sorted(values))
    if len(set(result)) != len(result):
        raise ValueError(f"{field_name} 必须是去重后的非空字符串")
    return result


@dataclass(frozen=True)
class ProviderIdentity:
    provider_id: str
    api_surface: str
    api_version: str
    endpoint_semantics_identity: str
    official_documentation_urls: tuple[str, ...]
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("provider_id", "api_surface", "api_version", "endpoint_semantics_identity"):
            _require_text(getattr(self, name), name)
        urls = _sorted_unique_text(self.official_documentation_urls, "official_documentation_urls")
        if any(not url.startswith("https://") for url in urls):
            raise ValueError("official_documentation_urls 必须使用 https")
        object.__setattr__(self, "official_documentation_urls", urls)
        object.__setattr__(self, "identity", _hash({
            "provider_id": self.provider_id,
            "api_surface": self.api_surface,
            "api_version": self.api_version,
            "endpoint_semantics_identity": self.endpoint_semantics_identity,
        }))


@dataclass(frozen=True)
class RequestedModelSelectorIdentity:
    provider_identity: str
    selector: str
    version_binding: VersionBinding
    model_drift_policy: ModelDriftPolicy
    exact_snapshot: str | None = None
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.provider_identity, "requested_model.provider_identity")
        _require_text(self.selector, "requested_model.selector")
        if self.version_binding is VersionBinding.EXACT_SNAPSHOT_PINNED:
            _require_text(self.exact_snapshot, "requested_model.exact_snapshot")
            if self.model_drift_policy is not ModelDriftPolicy.EXACT_SNAPSHOT_REQUIRED:
                raise ValueError("exact snapshot 必须使用 EXACT_SNAPSHOT_REQUIRED 漂移策略")
        elif self.exact_snapshot is not None:
            raise ValueError("非 exact selector 不得伪装 exact_snapshot")
        object.__setattr__(self, "identity", _hash({
            "provider_identity": self.provider_identity,
            "selector": self.selector,
            "version_binding": self.version_binding.value,
            "model_drift_policy": self.model_drift_policy.value,
            "exact_snapshot": self.exact_snapshot,
        }))


@dataclass(frozen=True)
class ResolvedProviderModelIdentity:
    provider_identity: str
    resolved_model_id: str
    resolved_version_or_snapshot: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.provider_identity, "resolved_model.provider_identity")
        _require_text(self.resolved_model_id, "resolved_model.resolved_model_id")
        _require_text(self.resolved_version_or_snapshot, "resolved_model.resolved_version_or_snapshot")
        object.__setattr__(self, "identity", _hash({
            "provider_identity": self.provider_identity,
            "resolved_model_id": self.resolved_model_id,
            "resolved_version_or_snapshot": self.resolved_version_or_snapshot,
            "reported_by": "PROVIDER_RESPONSE",
        }))


@dataclass(frozen=True)
class InvocationConfig:
    inference_parameters: tuple[tuple[str, str], ...] = ()
    credential_environment_variable: str | None = None
    require_resolved_model_identity: bool = True
    live_calls_enabled: bool = False

    def __post_init__(self) -> None:
        if any(
            not isinstance(item, tuple)
            or len(item) != 2
            or not isinstance(item[0], str)
            or not item[0]
            or not isinstance(item[1], str)
            for item in self.inference_parameters
        ):
            raise ValueError("inference_parameters 必须是去重的字符串键值对")
        parameters = tuple(sorted(self.inference_parameters))
        if len({name for name, _ in parameters}) != len(parameters):
            raise ValueError("inference_parameters 的名称必须唯一")
        if self.credential_environment_variable is not None and not _ENVIRONMENT_NAME.fullmatch(
            self.credential_environment_variable
        ):
            raise ValueError("credential_environment_variable 必须是大写环境变量名")
        _strict_bool(self.require_resolved_model_identity, "require_resolved_model_identity")
        _strict_bool(self.live_calls_enabled, "live_calls_enabled")
        if self.live_calls_enabled:
            raise ValueError("pre-live provider contract 禁止真实调用")
        object.__setattr__(self, "inference_parameters", parameters)


@dataclass(frozen=True)
class PromptArtifact:
    prompt_kind: str
    content: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.prompt_kind, "prompt_kind")
        _require_text(self.content, "prompt.content")
        object.__setattr__(self, "identity", _hash({
            "prompt_kind": self.prompt_kind,
            "content_utf8_sha256": sha256(self.content.encode("utf-8")).hexdigest(),
        }))


@dataclass(frozen=True)
class VisualArtifact:
    """最新 integrated renderer 产物及其 canonical observation 来源桥。"""

    observation_identity: str
    renderer_identity: str
    renderer_config_identity: str
    content: bytes = field(repr=False)
    visual_observation_identity: str | None = None
    artifact_kind: str = VISUAL_ARTIFACT_KIND
    mime_type: str = PNG_MIME
    integrated_renderer_verified: bool = False
    declared_png_sha256: str | None = field(default=None, repr=False)
    declared_visual_artifact_identity: str | None = field(default=None, repr=False)
    png_sha256: str = field(init=False)
    visual_artifact_identity: str = field(init=False)

    @classmethod
    def from_png(
        cls,
        *,
        observation_identity: str,
        renderer_identity: str,
        renderer_config_identity: str,
        content: bytes,
        visual_observation_identity: str | None = None,
        artifact_kind: str = VISUAL_ARTIFACT_KIND,
        declared_png_sha256: str | None = None,
        declared_visual_artifact_identity: str | None = None,
    ) -> "VisualArtifact":
        return cls(
            observation_identity=observation_identity,
            renderer_identity=renderer_identity,
            renderer_config_identity=renderer_config_identity,
            content=content,
            visual_observation_identity=visual_observation_identity,
            artifact_kind=artifact_kind,
            declared_png_sha256=declared_png_sha256,
            declared_visual_artifact_identity=declared_visual_artifact_identity,
        )

    @classmethod
    def from_canonical_observation(
        cls,
        *,
        observation: JiangheObservation,
        renderer: JiangheVisualRenderer,
    ) -> "VisualArtifact":
        """从正式 observation 经 integrated renderer 生成唯一受支持的视觉路径。"""
        if not isinstance(observation, JiangheObservation):
            raise TypeError("observation 必须是 canonical JiangheObservation")
        if not isinstance(renderer, JiangheVisualRenderer):
            raise TypeError("renderer 必须是 integrated JiangheVisualRenderer")
        spec = VisualObservationSpec(
            product=observation.identity.product,
            concrete_contract=observation.identity.concrete_contract,
            as_of=observation.identity.decision_time,
            panels=panels_from_observation_bars(observation.bars),
        )
        rendered = renderer.render(spec)
        manifest = rendered.manifest
        image = manifest.get("image")
        if not isinstance(image, Mapping) or image.get("mime") != INTEGRATED_PNG_MIME:
            raise ValueError("integrated renderer manifest 缺少 canonical image/png MIME")
        return cls(
            observation_identity=observation.identity.identity,
            visual_observation_identity=rendered.input_observation_identity,
            renderer_identity=str(manifest.get("renderer_version")),
            renderer_config_identity=rendered.renderer_config_identity,
            content=rendered.png_bytes,
            artifact_kind=str(manifest.get("artifact")),
            mime_type=str(image.get("mime")),
            integrated_renderer_verified=True,
            declared_png_sha256=rendered.png_sha256,
            declared_visual_artifact_identity=rendered.visual_artifact_identity,
        )

    def __post_init__(self) -> None:
        _require_identity(self.observation_identity, "visual_artifact.observation_identity")
        _require_identity(
            self.renderer_config_identity,
            "visual_artifact.renderer_config_identity",
        )
        _require_text(self.renderer_identity, "visual_artifact.renderer_identity")
        _require_text(self.artifact_kind, "visual_artifact.artifact_kind")
        visual_observation_identity = (
            self.visual_observation_identity or self.observation_identity
        )
        _require_identity(
            visual_observation_identity,
            "visual_artifact.visual_observation_identity",
        )
        _strict_bool(self.integrated_renderer_verified, "integrated_renderer_verified")
        if self.mime_type != PNG_MIME:
            raise ValueError("视觉输入 MIME 固定为 image/png")
        if not isinstance(self.content, bytes) or not self.content.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("视觉输入必须是带 PNG signature 的非空 bytes")
        png_hash = sha256(self.content).hexdigest()
        if self.declared_png_sha256 is not None and self.declared_png_sha256 != png_hash:
            raise ValueError("caller png_sha256 与实际 PNG bytes 不一致")
        artifact_identity = canonical_visual_artifact_identity(
            artifact_kind=self.artifact_kind,
            renderer_identity=self.renderer_identity,
            renderer_config_identity=self.renderer_config_identity,
            source_observation_identity=visual_observation_identity,
            content_sha256=png_hash,
            mime_type=self.mime_type,
        )
        if (
            self.declared_visual_artifact_identity is not None
            and self.declared_visual_artifact_identity != artifact_identity
        ):
            raise ValueError("caller visual_artifact_identity 与 canonical identity 不一致")
        if self.integrated_renderer_verified and (
            self.artifact_kind != INTEGRATED_VISUAL_ARTIFACT_KIND
            or self.renderer_identity != INTEGRATED_RENDERER_VERSION
            or self.mime_type != INTEGRATED_PNG_MIME
            or self.declared_png_sha256 is None
            or self.declared_visual_artifact_identity is None
        ):
            raise ValueError("integrated renderer provenance 声明不完整或版本不匹配")
        object.__setattr__(self, "visual_observation_identity", visual_observation_identity)
        object.__setattr__(self, "png_sha256", png_hash)
        object.__setattr__(self, "visual_artifact_identity", artifact_identity)


@dataclass(frozen=True)
class StructuredInputArtifact:
    observation_identity: str
    schema_identity: str
    payload: Mapping[str, Any]
    artifact_kind: str = STRUCTURED_ARTIFACT_KIND
    declared_content_sha256: str | None = field(default=None, repr=False)
    declared_artifact_identity: str | None = field(default=None, repr=False)
    content_sha256: str = field(init=False)
    artifact_identity: str = field(init=False)

    @classmethod
    def from_payload(
        cls,
        *,
        observation_identity: str,
        schema_identity: str,
        payload: Mapping[str, Any],
        declared_content_sha256: str | None = None,
        declared_artifact_identity: str | None = None,
    ) -> "StructuredInputArtifact":
        return cls(
            observation_identity=observation_identity,
            schema_identity=schema_identity,
            payload=payload,
            declared_content_sha256=declared_content_sha256,
            declared_artifact_identity=declared_artifact_identity,
        )

    def __post_init__(self) -> None:
        _require_identity(self.observation_identity, "structured_input.observation_identity")
        _require_identity(self.schema_identity, "structured_input.schema_identity")
        _require_text(self.artifact_kind, "structured_input.artifact_kind")
        payload = _mapping(self.payload, "structured_input.payload")
        if payload.get("observation_identity") != self.observation_identity:
            raise ValueError("structured payload 必须声明同一 canonical observation identity")
        content_hash = _hash(payload)
        if self.declared_content_sha256 is not None and self.declared_content_sha256 != content_hash:
            raise ValueError("caller structured content hash 与实际 payload 不一致")
        artifact_identity = _hash({
            "artifact": self.artifact_kind,
            "schema_identity": self.schema_identity,
            "observation_identity": self.observation_identity,
            "content_sha256": content_hash,
        })
        if self.declared_artifact_identity is not None and self.declared_artifact_identity != artifact_identity:
            raise ValueError("caller structured artifact identity 与 canonical identity 不一致")
        object.__setattr__(self, "content_sha256", content_hash)
        object.__setattr__(self, "artifact_identity", artifact_identity)


@dataclass(frozen=True)
class CapabilityDeclaration:
    provider_identity: ProviderIdentity
    declared_at: datetime
    supported_tracks: tuple[FidelityTrack, ...]
    supports_visual_input: bool
    supports_structured_input: bool
    supports_structured_output: bool
    supports_dual_input: bool
    supports_raw_response_capture: bool
    supports_usage_metadata: bool
    supports_resolved_model_reporting: bool
    supports_timing: bool
    supports_environment_credential: bool
    repeatability_controls: tuple[str, ...]
    model_drift_policy: ModelDriftPolicy
    status: CandidateStatus = CandidateStatus.CANDIDATE
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.provider_identity, ProviderIdentity):
            raise TypeError("provider_identity 必须是 ProviderIdentity")
        _require_aware(self.declared_at, "declared_at")
        if not self.supported_tracks or any(
            not isinstance(track, FidelityTrack) for track in self.supported_tracks
        ):
            raise ValueError("supported_tracks 必须是非空去重 FidelityTrack")
        tracks = tuple(sorted(self.supported_tracks, key=lambda track: track.value))
        if len(set(tracks)) != len(tracks):
            raise ValueError("supported_tracks 必须是非空去重 FidelityTrack")
        bool_names = (
            "supports_visual_input", "supports_structured_input", "supports_structured_output",
            "supports_dual_input", "supports_raw_response_capture", "supports_usage_metadata",
            "supports_resolved_model_reporting", "supports_timing",
            "supports_environment_credential",
        )
        for name in bool_names:
            _strict_bool(getattr(self, name), name)
        if FidelityTrack.VISUAL in tracks and not self.supports_visual_input:
            raise ValueError("VISUAL track 需要 visual INPUT capability")
        if FidelityTrack.STRUCTURED in tracks and not self.supports_structured_input:
            raise ValueError("STRUCTURED track 需要 structured INPUT capability")
        if FidelityTrack.DUAL_INPUT in tracks and not (
            self.supports_dual_input and self.supports_visual_input and self.supports_structured_input
        ):
            raise ValueError("DUAL_INPUT 需要 visual + structured INPUT capability")
        if FidelityTrack.OPERATIONAL_PROVIDER in tracks and not (
            self.supports_raw_response_capture and self.supports_timing
        ):
            raise ValueError("OPERATIONAL_PROVIDER 需要 raw capture 与 timing")
        controls = _sorted_unique_text(self.repeatability_controls, "repeatability_controls")
        if self.status is not CandidateStatus.CANDIDATE:
            raise ValueError("pre-live declaration 只能是 CANDIDATE")
        object.__setattr__(self, "supported_tracks", tracks)
        object.__setattr__(self, "repeatability_controls", controls)
        object.__setattr__(self, "identity", _hash({
            "provider_identity": self.provider_identity.identity,
            "declared_at": _utc(self.declared_at),
            "supported_tracks": [track.value for track in tracks],
            **{name: getattr(self, name) for name in bool_names},
            "repeatability_controls": controls,
            "model_drift_policy": self.model_drift_policy.value,
            "status": self.status.value,
        }))


@dataclass(frozen=True)
class JiangheModelRequest:
    provider_identity: ProviderIdentity
    requested_model_selector: RequestedModelSelectorIdentity
    capability_declaration: CapabilityDeclaration
    invocation_config: InvocationConfig
    system_prompt: PromptArtifact
    decision_prompt: PromptArtifact
    prompt_package_identity: str
    context_selection_policy_identity: str
    response_schema_identity: str
    runtime_normalizer_identity: str
    evaluation_extractor_identity: str
    observation_identity: str
    observation_available_at: datetime
    model_request_at: datetime
    fidelity_track: FidelityTrack
    visual_artifact: VisualArtifact | None = None
    structured_input: StructuredInputArtifact | None = None
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.capability_declaration.provider_identity.identity != self.provider_identity.identity:
            raise ValueError("request provider 与 capability provider 不一致")
        if self.requested_model_selector.provider_identity != self.provider_identity.identity:
            raise ValueError("requested model selector 与 provider 不一致")
        for name in (
            "prompt_package_identity",
            "context_selection_policy_identity",
            "response_schema_identity",
            "runtime_normalizer_identity",
            "evaluation_extractor_identity",
        ):
            _require_identity(getattr(self, name), name)
        _require_identity(self.observation_identity, "observation_identity")
        available = _require_aware(self.observation_available_at, "observation_available_at")
        requested = _require_aware(self.model_request_at, "model_request_at")
        if available > requested:
            raise ValueError("observation_available_at 不能晚于 model_request_at")
        if self.fidelity_track not in self.capability_declaration.supported_tracks:
            raise ValueError("capability 不支持请求的 fidelity track")
        if self.invocation_config.require_resolved_model_identity and not (
            self.capability_declaration.supports_resolved_model_reporting
        ):
            raise ValueError("无法治理 resolved model identity，provider request 失败闭合")
        if self.fidelity_track is FidelityTrack.VISUAL and self.visual_artifact is None:
            raise ValueError("VISUAL 请求必须提供 visual artifact")
        if self.fidelity_track is FidelityTrack.STRUCTURED and self.structured_input is None:
            raise ValueError("STRUCTURED 请求必须提供 structured input")
        if self.fidelity_track is FidelityTrack.DUAL_INPUT and (
            self.visual_artifact is None or self.structured_input is None
        ):
            raise ValueError("DUAL_INPUT 必须同时提供视觉与结构化输入")
        for artifact in (self.visual_artifact, self.structured_input):
            if artifact is not None and artifact.observation_identity != self.observation_identity:
                raise ValueError("所有 request artifacts 必须绑定同一 canonical observation identity")
        if self.visual_artifact is not None and not self.visual_artifact.integrated_renderer_verified:
            raise ValueError("视觉请求必须使用最新 integrated JiangheVisualRenderer provenance")
        object.__setattr__(self, "identity", _hash({
            "contract_version": CONTRACT_VERSION,
            "provider_identity": self.provider_identity.identity,
            "requested_model_selector_identity": self.requested_model_selector.identity,
            "capability_identity": self.capability_declaration.identity,
            "inference_parameters": self.invocation_config.inference_parameters,
            "system_prompt_identity": self.system_prompt.identity,
            "decision_prompt_identity": self.decision_prompt.identity,
            "prompt_package_identity": self.prompt_package_identity,
            "context_selection_policy_identity": self.context_selection_policy_identity,
            "response_schema_identity": self.response_schema_identity,
            "runtime_normalizer_identity": self.runtime_normalizer_identity,
            "evaluation_extractor_identity": self.evaluation_extractor_identity,
            "observation_identity": self.observation_identity,
            "observation_available_at": _utc(available),
            "model_request_at": _utc(requested),
            "fidelity_track": self.fidelity_track.value,
            "visual_artifact_identity": None if self.visual_artifact is None else self.visual_artifact.visual_artifact_identity,
            "structured_artifact_identity": None if self.structured_input is None else self.structured_input.artifact_identity,
        }))

    def build_transport_payload(self) -> dict[str, Any]:
        inputs: list[dict[str, Any]] = [{
            "type": "semantic_prompts",
            "system": {"identity": self.system_prompt.identity, "content": self.system_prompt.content},
            "decision": {"identity": self.decision_prompt.identity, "content": self.decision_prompt.content},
        }]
        if self.visual_artifact is not None:
            inputs.append({
                "type": "visual_artifact",
                "mime_type": self.visual_artifact.mime_type,
                "observation_identity": self.visual_artifact.observation_identity,
                "visual_observation_identity": self.visual_artifact.visual_observation_identity,
                "visual_artifact_identity": self.visual_artifact.visual_artifact_identity,
                "renderer_identity": self.visual_artifact.renderer_identity,
                "renderer_config_identity": self.visual_artifact.renderer_config_identity,
                "png_sha256": self.visual_artifact.png_sha256,
                "content_base64": base64.b64encode(self.visual_artifact.content).decode("ascii"),
            })
        if self.structured_input is not None:
            inputs.append({
                "type": "structured_input",
                "observation_identity": self.structured_input.observation_identity,
                "artifact_identity": self.structured_input.artifact_identity,
                "schema_identity": self.structured_input.schema_identity,
                "content_sha256": self.structured_input.content_sha256,
                "payload": dict(self.structured_input.payload),
            })
        return {
            "contract_version": CONTRACT_VERSION,
            "request_identity": self.identity,
            "provider_identity": self.provider_identity.identity,
            "requested_model_selector": self.requested_model_selector.selector,
            "requested_model_selector_identity": self.requested_model_selector.identity,
            "fidelity_track": self.fidelity_track.value,
            "prompt_package_identity": self.prompt_package_identity,
            "context_selection_policy_identity": self.context_selection_policy_identity,
            "response_schema_identity": self.response_schema_identity,
            "runtime_normalizer_identity": self.runtime_normalizer_identity,
            "evaluation_extractor_identity": self.evaluation_extractor_identity,
            "observation_identity": self.observation_identity,
            "inputs": inputs,
        }

    def to_input_evidence(
        self,
        response_evidence: "JiangheModelResponseEvidence | None" = None,
    ) -> InputEvidence:
        """无损映射到 integrated evaluator 的唯一 typed provenance interface。"""
        if response_evidence is not None:
            if response_evidence.request_identity != self.identity:
                raise ValueError("response evidence 不属于当前 provider invocation")
            if response_evidence.provider_identity.identity != self.provider_identity.identity:
                raise ValueError("response evidence provider 与 request 不一致")
            if response_evidence.capability_identity != self.capability_declaration.identity:
                raise ValueError("response evidence capability 与 request 不一致")
        has_visual = self.visual_artifact is not None
        has_structured = self.structured_input is not None
        return InputEvidence(
            observation_identity=self.observation_identity,
            # evaluator 的 visual/structured observation 字段表达共同 canonical 来源；
            # renderer projection identity 仍保留在 VisualArtifact 与 request identity 中。
            visual_observation_identity=self.observation_identity if has_visual else None,
            structured_observation_identity=self.observation_identity if has_structured else None,
            visual_artifact_identity=(
                self.visual_artifact.visual_artifact_identity if has_visual else None
            ),
            renderer_config_identity=(
                self.visual_artifact.renderer_config_identity if has_visual else None
            ),
            structured_input_identity=(
                self.structured_input.artifact_identity if has_structured else None
            ),
            provider_invocation_identity=self.identity,
            provider_response_identity=(
                response_evidence.identity if response_evidence is not None else None
            ),
            normalizer_identity=self.runtime_normalizer_identity,
            evaluation_extractor_identity=self.evaluation_extractor_identity,
            prompt_package_identity=self.prompt_package_identity,
            model_provider_identity=self.provider_identity.identity,
        )


@dataclass(frozen=True)
class InvocationTiming:
    observation_available_at: datetime
    model_request_at: datetime
    model_response_at: datetime
    normalized_decision_at: datetime

    def __post_init__(self) -> None:
        values = tuple(_require_aware(getattr(self, name), name) for name in (
            "observation_available_at", "model_request_at", "model_response_at", "normalized_decision_at"
        ))
        if any(later < earlier for earlier, later in zip(values, values[1:])):
            raise ValueError("provider invocation 时间线不能倒流")

    @property
    def latency_ms(self) -> int:
        return int((self.model_response_at - self.model_request_at).total_seconds() * 1000)


@dataclass(frozen=True)
class JiangheModelResponseEvidence:
    request_identity: str
    provider_identity: ProviderIdentity
    capability_identity: str
    requested_model_selector: RequestedModelSelectorIdentity
    resolved_model: ResolvedProviderModelIdentity
    provider_response_id: str
    raw_response: str
    normalized_decision: NormalizedJiangheDecision
    usage_metadata: Mapping[str, Any]
    timing: InvocationTiming
    raw_response_sha256: str = field(init=False)
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_identity(self.request_identity, "request_identity")
        _require_identity(self.capability_identity, "capability_identity")
        _require_text(self.provider_response_id, "provider_response_id")
        _require_text(self.raw_response, "raw_response")
        usage = _mapping(self.usage_metadata, "usage_metadata")
        if self.requested_model_selector.provider_identity != self.provider_identity.identity:
            raise ValueError("response requested selector provider 不一致")
        if self.resolved_model.provider_identity != self.provider_identity.identity:
            raise ValueError("response resolved model provider 不一致")
        raw_hash = sha256(self.raw_response.encode("utf-8")).hexdigest()
        object.__setattr__(self, "raw_response_sha256", raw_hash)
        object.__setattr__(self, "identity", _hash({
            "request_identity": self.request_identity,
            "provider_identity": self.provider_identity.identity,
            "capability_identity": self.capability_identity,
            "requested_model_selector_identity": self.requested_model_selector.identity,
            "resolved_provider_model_identity": self.resolved_model.identity,
            "provider_response_id": self.provider_response_id,
            "model_request_at": _utc(self.timing.model_request_at),
            "model_response_at": _utc(self.timing.model_response_at),
            "normalized_decision_at": _utc(self.timing.normalized_decision_at),
            "latency_ms": self.timing.latency_ms,
            "raw_response_sha256": raw_hash,
            "normalized_response_identity": self.normalized_decision.identity,
            "usage_identity": _hash(usage),
        }))


@dataclass(frozen=True)
class ProviderEvaluationRecordResult:
    """provider adapter 构造的 evaluator record；失败永远保持 non-scoreable。"""

    record: Mapping[str, Any]
    response_evidence: JiangheModelResponseEvidence | None
    failure_reason: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.record, Mapping):
            raise TypeError("record 必须是 mapping")
        call_success = self.record.get("call_success")
        if type(call_success) is not bool:
            raise ValueError("record.call_success 必须是严格布尔值")
        if call_success and (self.response_evidence is None or self.failure_reason is not None):
            raise ValueError("成功 record 必须有 response evidence 且不能有 failure_reason")
        if not call_success and (self.response_evidence is not None or not self.failure_reason):
            raise ValueError("失败 record 必须保留 failure_reason 且不得伪造 response evidence")


def _input_evidence_payload(evidence: InputEvidence) -> dict[str, str]:
    return {
        item.name: value
        for item in fields(InputEvidence)
        if (value := getattr(evidence, item.name)) is not None
    }


def _empty_fidelity_response_payload() -> dict[str, object]:
    return {
        "family": None,
        "action": None,
        "direction": None,
        "acknowledged_principles": [],
        "violated_principles": [],
        "declared_unknown": [],
        "invented_thresholds": [],
        "outcome_reference": False,
        "raw_text": None,
    }


class CandidateProviderAdapter:
    def __init__(self, capability_declaration: CapabilityDeclaration) -> None:
        if capability_declaration.status is not CandidateStatus.CANDIDATE:
            raise ValueError("adapter 只接受 CANDIDATE declaration")
        self.capability_declaration = capability_declaration

    @property
    def live_invocation_disabled(self) -> bool:
        return True

    def build_request_payload(self, request: JiangheModelRequest) -> dict[str, Any]:
        if request.capability_declaration.identity != self.capability_declaration.identity:
            raise ValueError("adapter capability 与 request 不一致")
        return request.build_transport_payload()

    def invoke(self, request: JiangheModelRequest) -> JiangheModelResponseEvidence:
        del request
        raise LiveInvocationDisabledError("pre-live candidate adapter 禁止任何真实 provider 调用")

    def parse_mocked_response(
        self,
        *,
        request: JiangheModelRequest,
        raw_provider_payload: Mapping[str, Any],
        model_response_at: datetime,
        normalized_decision_at: datetime,
        normalizer: JiangheResponseNormalizer,
    ) -> JiangheModelResponseEvidence:
        if request.capability_declaration.identity != self.capability_declaration.identity:
            raise ValueError("adapter capability 与 request 不一致")
        if normalizer.identity != request.runtime_normalizer_identity:
            raise ValueError("request 与实际 runtime normalizer identity 不一致")
        payload = _mapping(raw_provider_payload, "raw_provider_payload")
        expected_fields = frozenset({
            "provider", "resolved_model_id", "resolved_version_or_snapshot", "response_id",
            "output_text", "usage_metadata",
        })
        if frozenset(payload) != expected_fields:
            raise ValueError("provider response 必须使用严格字段集合")
        if payload["provider"] != request.provider_identity.provider_id:
            raise ValueError("provider response provider 不一致")
        resolved = ResolvedProviderModelIdentity(
            provider_identity=request.provider_identity.identity,
            resolved_model_id=_require_text(payload["resolved_model_id"], "resolved_model_id"),
            resolved_version_or_snapshot=_require_text(
                payload["resolved_version_or_snapshot"], "resolved_version_or_snapshot"
            ),
        )
        selector = request.requested_model_selector
        if selector.version_binding is VersionBinding.EXACT_SNAPSHOT_PINNED and (
            resolved.resolved_model_id != selector.selector
            or resolved.resolved_version_or_snapshot != selector.exact_snapshot
        ):
            raise ValueError("exact pinned selector 与 provider resolved model 不一致")
        normalized = normalizer.normalize(_require_text(payload["output_text"], "output_text"))
        if normalized.response_schema_identity != request.response_schema_identity:
            raise ValueError("normalized response schema identity 与 request 不一致")
        timing = InvocationTiming(
            request.observation_available_at,
            request.model_request_at,
            model_response_at,
            normalized_decision_at,
        )
        return JiangheModelResponseEvidence(
            request_identity=request.identity,
            provider_identity=request.provider_identity,
            capability_identity=request.capability_declaration.identity,
            requested_model_selector=selector,
            resolved_model=resolved,
            provider_response_id=_require_text(payload["response_id"], "response_id"),
            raw_response=_canonical_json(payload),
            normalized_decision=normalized,
            usage_metadata=_mapping(payload["usage_metadata"], "usage_metadata"),
            timing=timing,
        )

    def build_mocked_evaluation_record(
        self,
        *,
        request: JiangheModelRequest,
        raw_provider_payload: Mapping[str, Any],
        model_response_at: datetime,
        normalized_decision_at: datetime,
        normalizer: JiangheResponseNormalizer,
        evaluator_judgment: EvaluatorSideJudgment,
        record_id: str,
        candidate_label: str,
        corpus_id: str,
        fixture_id: str,
    ) -> ProviderEvaluationRecordResult:
        """统一 provider→evaluator seam；malformed provider 永不升级成成功记录。"""
        if not isinstance(evaluator_judgment, EvaluatorSideJudgment):
            raise TypeError("evaluator_judgment 必须是 EvaluatorSideJudgment")
        for name, value in (
            ("record_id", record_id),
            ("candidate_label", candidate_label),
            ("corpus_id", corpus_id),
            ("fixture_id", fixture_id),
        ):
            _require_text(value, name)
        timing = InvocationTiming(
            request.observation_available_at,
            request.model_request_at,
            model_response_at,
            normalized_decision_at,
        )
        base_record: dict[str, Any] = {
            "record_id": record_id,
            "candidate_label": candidate_label,
            "corpus_id": corpus_id,
            "fixture_id": fixture_id,
            "track": request.fidelity_track.value,
            "latency_ms": timing.latency_ms,
        }
        try:
            response_evidence = self.parse_mocked_response(
                request=request,
                raw_provider_payload=raw_provider_payload,
                model_response_at=model_response_at,
                normalized_decision_at=normalized_decision_at,
                normalizer=normalizer,
            )
        except (TypeError, ValueError) as error:
            failure_record = {
                **base_record,
                "call_success": False,
                "response": _empty_fidelity_response_payload(),
                "input_evidence": _input_evidence_payload(request.to_input_evidence()),
            }
            return ProviderEvaluationRecordResult(
                record=failure_record,
                response_evidence=None,
                failure_reason=f"{type(error).__name__}: {error}",
            )

        if evaluator_judgment.evaluation_extractor_identity != request.evaluation_extractor_identity:
            raise ValueError("evaluator judgment 与 request extractor identity 不一致")
        runtime_evidence = extract_runtime_fidelity_evidence(
            response_evidence.normalized_decision
        )
        success_record = {
            **base_record,
            "call_success": True,
            "response": build_fidelity_response_payload(
                runtime_evidence,
                evaluator_judgment,
            ),
            "input_evidence": _input_evidence_payload(
                request.to_input_evidence(response_evidence)
            ),
        }
        return ProviderEvaluationRecordResult(
            record=success_record,
            response_evidence=response_evidence,
            failure_reason=None,
        )


def contract_field_names() -> frozenset[str]:
    names: set[str] = set()
    for contract_type in (JiangheModelRequest, JiangheModelResponseEvidence, InvocationTiming):
        names.update(item.name for item in fields(contract_type))
    return frozenset(names)


__all__ = [
    "CONTRACT_VERSION", "CapabilityDeclaration", "CandidateProviderAdapter", "CandidateStatus",
    "FidelityTrack", "InvocationConfig", "InvocationTiming", "JiangheModelRequest",
    "JiangheModelResponseEvidence", "LiveInvocationDisabledError", "ModelDriftPolicy",
    "PNG_MIME", "PromptArtifact", "ProviderEvaluationRecordResult", "ProviderIdentity", "RequestedModelSelectorIdentity",
    "ResolvedProviderModelIdentity", "StructuredInputArtifact", "VersionBinding", "VisualArtifact",
    "contract_field_names",
]

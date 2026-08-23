"""江河真实模型 Provider 的中立调用合同（预备阶段）。

本模块只定义未来真实模型调用需要留存的身份、输入、时间和审计数据。
它不包含 HTTP 客户端、第三方 SDK、密钥读取或网络访问。当前唯一的 adapter
只能构造请求并解析测试提供的模拟回复；``invoke`` 永远失败闭合。

该边界服务于非结果的五条忠实度轨道：SEMANTIC、VISUAL、STRUCTURED、
DUAL_INPUT、OPERATIONAL_PROVIDER。它不定义也不保存收益、未来价格、胜负或
其他 candidate-outcome 字段。
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field, fields
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json
import re
from typing import Any, Mapping, Sequence


CONTRACT_VERSION = "JIANGHE_MODEL_PROVIDER_CONTRACT_V0_1"


class FidelityTrack(str, Enum):
    """真实模型忠实度的必经能力轨道。"""

    SEMANTIC = "SEMANTIC"
    VISUAL = "VISUAL"
    STRUCTURED = "STRUCTURED"
    DUAL_INPUT = "DUAL_INPUT"
    OPERATIONAL_PROVIDER = "OPERATIONAL_PROVIDER"


class CandidateStatus(str, Enum):
    """Provider 生命周期状态；本预备分支只允许 CANDIDATE。"""

    CANDIDATE = "CANDIDATE"
    VERIFIED = "VERIFIED"
    ADOPTED = "ADOPTED"


class VersionBinding(str, Enum):
    """模型版本在研究对象中的绑定方式。"""

    PINNED = "PINNED"
    RESPONSE_RECORDED = "RESPONSE_RECORDED"
    UNSPECIFIED = "UNSPECIFIED"


class ModelDriftPolicy(str, Enum):
    """官方资料所述的模型漂移语义，未知时必须保守处理。"""

    PINNED_MODEL_ID = "PINNED_MODEL_ID"
    ALIAS_MAY_DRIFT = "ALIAS_MAY_DRIFT"
    PROVIDER_UNDOCUMENTED = "PROVIDER_UNDOCUMENTED"


class LiveInvocationDisabledError(RuntimeError):
    """阻止此预备包向真实 Provider 发送请求。"""


_ENVIRONMENT_NAME = re.compile(r"^[A-Z][A-Z0-9_]*$")
_FORBIDDEN_OUTCOME_FIELDS = frozenset({
    "outcome",
    "candidate_outcome",
    "pnl",
    "profit",
    "profits",
    "loss",
    "losses",
    "win_rate",
    "winrate",
    "sharpe",
    "expectancy",
    "future_price",
    "future_return",
    "return",
    "returns",
    "equity_curve",
})


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} 必须是非空字符串")
    return value


def _require_aware(value: object, field_name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} 必须是带时区的时间")
    return value


def _canonical_json(value: object) -> str:
    """将 JSON 兼容数据固定编码，用于审计哈希。"""
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as error:
        raise ValueError("数据必须是 JSON 兼容值") from error


def _hash_json(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _validate_mapping(value: object, field_name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or not value:
        raise ValueError(f"{field_name} 必须是非空 JSON 对象")
    if any(not isinstance(key, str) or not key for key in value):
        raise ValueError(f"{field_name} 的键必须是非空字符串")
    _canonical_json(value)
    return value


def _validate_no_outcome_fields(value: object, field_name: str) -> None:
    """拒绝把 candidate outcome 作为本合同的结构化字段传递或留存。"""
    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{field_name} 的键必须是字符串")
            normalized_key = key.lower().replace("-", "_").replace(" ", "_")
            if normalized_key in _FORBIDDEN_OUTCOME_FIELDS:
                raise ValueError(f"{field_name} 不得包含结果字段: {key}")
            _validate_no_outcome_fields(nested_value, f"{field_name}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, nested_value in enumerate(value):
            _validate_no_outcome_fields(nested_value, f"{field_name}[{index}]")


def _sorted_unique(values: Sequence[str], field_name: str) -> tuple[str, ...]:
    normalized = tuple(values)
    if any(not isinstance(value, str) or not value.strip() for value in normalized):
        raise ValueError(f"{field_name} 只能包含非空字符串")
    if tuple(sorted(set(normalized))) != normalized:
        raise ValueError(f"{field_name} 必须去重并按字典序排列")
    return normalized


@dataclass(frozen=True)
class ProviderIdentity:
    """Provider 的稳定标识，不包含账号、密钥或 UI 可见模型名。"""

    provider_id: str
    api_surface: str
    official_documentation_urls: tuple[str, ...]

    def __post_init__(self) -> None:
        _require_text(self.provider_id, "provider_id")
        _require_text(self.api_surface, "api_surface")
        urls = _sorted_unique(self.official_documentation_urls, "official_documentation_urls")
        if any(not url.startswith("https://") for url in urls):
            raise ValueError("官方文档链接必须使用 https")
        object.__setattr__(self, "official_documentation_urls", urls)


@dataclass(frozen=True)
class ModelIdentity:
    """请求模型和可复核版本/快照的标识。"""

    model_id: str
    version_or_snapshot: str | None = None
    version_binding: VersionBinding = VersionBinding.UNSPECIFIED

    def __post_init__(self) -> None:
        _require_text(self.model_id, "model_id")
        if self.version_or_snapshot is not None:
            _require_text(self.version_or_snapshot, "version_or_snapshot")
        if self.version_binding is VersionBinding.PINNED and not self.version_or_snapshot:
            raise ValueError("PINNED 模型必须提供 version_or_snapshot")

    @property
    def identity(self) -> str:
        return _hash_json({
            "model_id": self.model_id,
            "version_or_snapshot": self.version_or_snapshot,
            "version_binding": self.version_binding.value,
        })


@dataclass(frozen=True)
class InvocationConfig:
    """一次调用的推理与凭证引用配置。

    ``credential_environment_variable`` 只记录未来允许采用的环境变量名称。
    本模块绝不读取该变量，默认并且强制禁止真实网络调用。
    """

    inference_parameters: tuple[tuple[str, str], ...] = ()
    credential_environment_variable: str | None = None
    require_version_identity: bool = True
    live_calls_enabled: bool = False

    def __post_init__(self) -> None:
        parameters = tuple(self.inference_parameters)
        if any(
            not isinstance(name, str) or not name.strip() or not isinstance(value, str)
            for name, value in parameters
        ):
            raise ValueError("inference_parameters 必须是 (非空名称, 字符串值) 对")
        if tuple(sorted(parameters)) != parameters or len({name for name, _ in parameters}) != len(parameters):
            raise ValueError("inference_parameters 必须按名称排序且不得重复")
        if self.credential_environment_variable is not None:
            if not _ENVIRONMENT_NAME.fullmatch(self.credential_environment_variable):
                raise ValueError("credential_environment_variable 必须是大写环境变量名")
        if self.live_calls_enabled:
            raise ValueError("当前 Provider 预备合同禁止启用真实网络调用")
        object.__setattr__(self, "inference_parameters", parameters)


@dataclass(frozen=True)
class PromptArtifact:
    """可发送文本和其受治理身份必须同时存在。"""

    identity: str
    content: str

    def __post_init__(self) -> None:
        _require_text(self.identity, "prompt.identity")
        _require_text(self.content, "prompt.content")


@dataclass(frozen=True)
class VisualArtifact:
    """标准化 K 线视觉输入及其内容哈希。"""

    identity: str
    renderer_identity: str
    mime_type: str
    content: bytes = field(repr=False)
    content_sha256: str
    available_at: datetime

    def __post_init__(self) -> None:
        _require_text(self.identity, "visual_artifact.identity")
        _require_text(self.renderer_identity, "visual_artifact.renderer_identity")
        if not isinstance(self.mime_type, str) or not self.mime_type.startswith("image/"):
            raise ValueError("visual_artifact.mime_type 必须是 image/*")
        if not isinstance(self.content, bytes) or not self.content:
            raise ValueError("visual_artifact.content 必须是非空 bytes")
        if sha256(self.content).hexdigest() != self.content_sha256:
            raise ValueError("visual_artifact.content_sha256 与内容不一致")
        _require_aware(self.available_at, "visual_artifact.available_at")


@dataclass(frozen=True)
class StructuredInputArtifact:
    """点时结构化行情/观察输入及其 schema、内容身份。"""

    identity: str
    schema_identity: str
    payload: Mapping[str, Any]
    content_sha256: str
    available_at: datetime

    def __post_init__(self) -> None:
        _require_text(self.identity, "structured_input.identity")
        _require_text(self.schema_identity, "structured_input.schema_identity")
        payload = _validate_mapping(self.payload, "structured_input.payload")
        _validate_no_outcome_fields(payload, "structured_input.payload")
        if _hash_json(payload) != self.content_sha256:
            raise ValueError("structured_input.content_sha256 与内容不一致")
        _require_aware(self.available_at, "structured_input.available_at")


@dataclass(frozen=True)
class CapabilityDeclaration:
    """官方资料支持、但尚未经过本项目真实探针验证的能力声明。"""

    provider_identity: ProviderIdentity
    declared_at: datetime
    supported_tracks: tuple[FidelityTrack, ...]
    supports_image_input: bool
    supports_structured_json_output: bool
    supports_response_model_identity: bool
    supports_usage_metadata: bool
    supports_environment_credential: bool
    repeatability_controls: tuple[str, ...]
    model_drift_policy: ModelDriftPolicy
    status: CandidateStatus = CandidateStatus.CANDIDATE
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_aware(self.declared_at, "declared_at")
        tracks = tuple(self.supported_tracks)
        if not tracks or len(set(tracks)) != len(tracks):
            raise ValueError("supported_tracks 必须非空且不重复")
        if any(not isinstance(track, FidelityTrack) for track in tracks):
            raise ValueError("supported_tracks 只能包含 FidelityTrack")
        if FidelityTrack.DUAL_INPUT in tracks and not (
            self.supports_image_input and self.supports_structured_json_output
        ):
            raise ValueError("DUAL_INPUT 需要图像输入和结构化 JSON 输出能力")
        controls = _sorted_unique(self.repeatability_controls, "repeatability_controls")
        if self.status is not CandidateStatus.CANDIDATE:
            raise ValueError("本预备分支的能力声明只能是 CANDIDATE")
        object.__setattr__(self, "supported_tracks", tracks)
        object.__setattr__(self, "repeatability_controls", controls)
        object.__setattr__(self, "identity", _hash_json({
            "provider_id": self.provider_identity.provider_id,
            "api_surface": self.provider_identity.api_surface,
            "declared_at": self.declared_at.isoformat(),
            "supported_tracks": [track.value for track in tracks],
            "supports_image_input": self.supports_image_input,
            "supports_structured_json_output": self.supports_structured_json_output,
            "supports_response_model_identity": self.supports_response_model_identity,
            "supports_usage_metadata": self.supports_usage_metadata,
            "supports_environment_credential": self.supports_environment_credential,
            "repeatability_controls": controls,
            "model_drift_policy": self.model_drift_policy.value,
            "status": self.status.value,
        }))


@dataclass(frozen=True)
class JiangheModelRequest:
    """一个待发送、但在本分支永不实际发送的受治理请求。"""

    provider_identity: ProviderIdentity
    model_identity: ModelIdentity
    capability_declaration: CapabilityDeclaration
    invocation_config: InvocationConfig
    system_prompt: PromptArtifact
    decision_prompt: PromptArtifact
    observation_identity: str
    observation_available_at: datetime
    model_request_at: datetime
    fidelity_track: FidelityTrack
    visual_artifact: VisualArtifact | None = None
    structured_input: StructuredInputArtifact | None = None
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.capability_declaration.provider_identity.provider_id != self.provider_identity.provider_id:
            raise ValueError("请求 Provider 与能力声明 Provider 不一致")
        _require_text(self.observation_identity, "observation_identity")
        _require_aware(self.observation_available_at, "observation_available_at")
        _require_aware(self.model_request_at, "model_request_at")
        if self.observation_available_at > self.model_request_at:
            raise ValueError("observation_available_at 不能晚于 model_request_at")
        if self.invocation_config.require_version_identity and not self.model_identity.version_or_snapshot:
            raise ValueError("该调用要求可复核的 model version/snapshot")
        if self.fidelity_track not in self.capability_declaration.supported_tracks:
            raise ValueError("能力声明不支持该 fidelity track")
        if self.fidelity_track is FidelityTrack.VISUAL and self.visual_artifact is None:
            raise ValueError("VISUAL 请求必须带 visual_artifact")
        if self.fidelity_track is FidelityTrack.STRUCTURED and self.structured_input is None:
            raise ValueError("STRUCTURED 请求必须带 structured_input")
        if self.fidelity_track is FidelityTrack.DUAL_INPUT and (
            self.visual_artifact is None or self.structured_input is None
        ):
            raise ValueError("DUAL_INPUT 请求必须同时带 visual_artifact 和 structured_input")
        if self.visual_artifact is not None and self.visual_artifact.available_at > self.model_request_at:
            raise ValueError("视觉输入在请求时尚不可用")
        if self.structured_input is not None and self.structured_input.available_at > self.model_request_at:
            raise ValueError("结构化输入在请求时尚不可用")
        object.__setattr__(self, "identity", _hash_json({
            "contract_version": CONTRACT_VERSION,
            "provider_id": self.provider_identity.provider_id,
            "model_identity": self.model_identity.identity,
            "capability_declaration": self.capability_declaration.identity,
            "inference_parameters": self.invocation_config.inference_parameters,
            "system_prompt_identity": self.system_prompt.identity,
            "decision_prompt_identity": self.decision_prompt.identity,
            "observation_identity": self.observation_identity,
            "observation_available_at": self.observation_available_at.isoformat(),
            "model_request_at": self.model_request_at.isoformat(),
            "fidelity_track": self.fidelity_track.value,
            "visual_artifact_identity": None if self.visual_artifact is None else self.visual_artifact.identity,
            "visual_artifact_hash": None if self.visual_artifact is None else self.visual_artifact.content_sha256,
            "structured_input_identity": None if self.structured_input is None else self.structured_input.identity,
            "structured_input_hash": None if self.structured_input is None else self.structured_input.content_sha256,
        }))

    def build_transport_payload(self) -> dict[str, Any]:
        """构造中立且可供未来 adapter 转换的请求内容；绝不发送网络请求。"""
        inputs: list[dict[str, Any]] = [{
            "type": "semantic_prompts",
            "system_prompt_identity": self.system_prompt.identity,
            "system_prompt": self.system_prompt.content,
            "decision_prompt_identity": self.decision_prompt.identity,
            "decision_prompt": self.decision_prompt.content,
        }]
        if self.visual_artifact is not None:
            inputs.append({
                "type": "visual_artifact",
                "identity": self.visual_artifact.identity,
                "renderer_identity": self.visual_artifact.renderer_identity,
                "mime_type": self.visual_artifact.mime_type,
                "content_sha256": self.visual_artifact.content_sha256,
                "content_base64": base64.b64encode(self.visual_artifact.content).decode("ascii"),
            })
        if self.structured_input is not None:
            inputs.append({
                "type": "structured_input",
                "identity": self.structured_input.identity,
                "schema_identity": self.structured_input.schema_identity,
                "content_sha256": self.structured_input.content_sha256,
                "payload": dict(self.structured_input.payload),
            })
        return {
            "contract_version": CONTRACT_VERSION,
            "request_identity": self.identity,
            "provider": self.provider_identity.provider_id,
            "model": {
                "model_id": self.model_identity.model_id,
                "version_or_snapshot": self.model_identity.version_or_snapshot,
                "version_binding": self.model_identity.version_binding.value,
            },
            "inference_parameters": dict(self.invocation_config.inference_parameters),
            "fidelity_track": self.fidelity_track.value,
            "observation": {
                "identity": self.observation_identity,
                "available_at": self.observation_available_at.isoformat(),
            },
            "inputs": inputs,
        }


@dataclass(frozen=True)
class InvocationTiming:
    """一次调用的本地可信时间链，禁止延迟把决定倒填进过去。"""

    observation_available_at: datetime
    model_request_at: datetime
    model_response_at: datetime
    normalized_decision_at: datetime

    def __post_init__(self) -> None:
        names = (
            "observation_available_at",
            "model_request_at",
            "model_response_at",
            "normalized_decision_at",
        )
        values = tuple(_require_aware(getattr(self, name), name) for name in names)
        if any(later < earlier for earlier, later in zip(values, values[1:])):
            raise ValueError("调用时间线不能倒流，禁止产生过去成交")

    @property
    def latency_ms(self) -> int:
        return int((self.model_response_at - self.model_request_at).total_seconds() * 1000)


@dataclass(frozen=True)
class JiangheModelResponse:
    """模拟或未来真实响应的审计记录；不含交易结果字段。"""

    request_identity: str
    provider_identity: ProviderIdentity
    model_identity: ModelIdentity
    provider_response_id: str
    raw_response: str
    normalized_response: Mapping[str, Any]
    usage_metadata: Mapping[str, Any]
    timing: InvocationTiming
    raw_response_sha256: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.request_identity, "request_identity")
        _require_text(self.provider_response_id, "provider_response_id")
        _require_text(self.raw_response, "raw_response")
        normalized = _validate_mapping(self.normalized_response, "normalized_response")
        usage = _validate_mapping(self.usage_metadata, "usage_metadata")
        _validate_no_outcome_fields(normalized, "normalized_response")
        _validate_no_outcome_fields(usage, "usage_metadata")
        object.__setattr__(self, "raw_response_sha256", sha256(self.raw_response.encode("utf-8")).hexdigest())


class CandidateProviderAdapter:
    """仅用于准备与测试的 Provider adapter。

    它没有 HTTP、socket 或 SDK 依赖。``invoke`` 始终抛错；测试只能调用
    ``build_request_payload`` 和 ``parse_mocked_response``。
    """

    def __init__(self, capability_declaration: CapabilityDeclaration) -> None:
        if capability_declaration.status is not CandidateStatus.CANDIDATE:
            raise ValueError("只允许 CANDIDATE 能力声明创建预备 adapter")
        self.capability_declaration = capability_declaration

    @property
    def live_invocation_disabled(self) -> bool:
        return True

    def build_request_payload(self, request: JiangheModelRequest) -> dict[str, Any]:
        if request.provider_identity.provider_id != self.capability_declaration.provider_identity.provider_id:
            raise ValueError("adapter 与请求 Provider 不一致")
        return request.build_transport_payload()

    def invoke(self, request: JiangheModelRequest) -> JiangheModelResponse:
        """硬性失败闭合：此预备分支不得触发真实网络或消费。"""
        del request
        raise LiveInvocationDisabledError("真实 Provider 调用默认禁用；本分支不允许网络请求")

    def parse_mocked_response(
        self,
        *,
        request: JiangheModelRequest,
        raw_provider_payload: Mapping[str, Any],
        model_response_at: datetime,
        normalized_decision_at: datetime,
    ) -> JiangheModelResponse:
        """解析测试提供的模拟响应；缺字段、身份不符或版本缺失一律失败闭合。"""
        payload = _validate_mapping(raw_provider_payload, "raw_provider_payload")
        _validate_no_outcome_fields(payload, "raw_provider_payload")
        if payload.get("provider") != request.provider_identity.provider_id:
            raise ValueError("模拟回复的 provider 与请求不一致")
        if payload.get("model_id") != request.model_identity.model_id:
            raise ValueError("模拟回复的 model_id 与请求不一致")
        response_version = payload.get("version_or_snapshot")
        if request.invocation_config.require_version_identity and not response_version:
            raise ValueError("模拟回复缺少 version_or_snapshot")
        if response_version != request.model_identity.version_or_snapshot:
            raise ValueError("模拟回复的 version_or_snapshot 与请求不一致")
        response_id = payload.get("response_id")
        normalized = payload.get("normalized_response")
        usage = payload.get("usage_metadata")
        if not isinstance(response_id, str) or not response_id:
            raise ValueError("模拟回复缺少 response_id")
        _validate_mapping(normalized, "raw_provider_payload.normalized_response")
        _validate_mapping(usage, "raw_provider_payload.usage_metadata")
        timing = InvocationTiming(
            observation_available_at=request.observation_available_at,
            model_request_at=request.model_request_at,
            model_response_at=model_response_at,
            normalized_decision_at=normalized_decision_at,
        )
        return JiangheModelResponse(
            request_identity=request.identity,
            provider_identity=request.provider_identity,
            model_identity=request.model_identity,
            provider_response_id=response_id,
            raw_response=_canonical_json(payload),
            normalized_response=normalized,
            usage_metadata=usage,
            timing=timing,
        )


def contract_field_names() -> frozenset[str]:
    """供测试/审查证明合同公开字段没有 candidate-outcome 数据。"""
    names: set[str] = set()
    for contract_type in (JiangheModelRequest, JiangheModelResponse, InvocationTiming):
        names.update(field.name for field in fields(contract_type))
    return frozenset(names)

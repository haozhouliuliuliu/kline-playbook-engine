"""V0.3 capability-first Jianghe matched model comparison runtime (offline closure).

This module is the only V0.3 spend-eligible transport surface. It implements:

* the provider-neutral common capability-exam identity (SAME_MATERIAL / SAME_QUESTION /
  SAME_PNG_BYTES / SAME_STRUCTURED_OBSERVATION / SAME_POINT_IN_TIME);
* provider-specific inference-config identities (model, reasoning controls, output
  headroom, network timeout, image wire syntax, stream, tools, response-format policy);
* the V0.3 attempt identity binding the common exam + provider inference config + slot;
* the headed capability-answer contract shared verbatim by DeepSeek / MiniMax / Kimi;
* a format-only capability adapter (never repairs semantics; never guesses);
* a shared CNY100 budget ledger that carries the historical 0.270021 CNY forward and
  records PRECALL_CONSERVATIVE_RESERVATION_CNY / POSTCALL_CALCULATED_CNY /
  PROVIDER_REPORTED_BILLED_CNY / ACCOUNTED_CNY_FOR_HARD_CAP;
* a mockable transport with a full V0.3 terminal-status taxonomy and no automatic retry;
* durable evidence that preserves MODEL_RAW_FINAL_ANSWER while never persisting
  reasoning_content / reasoning_details / hidden chain-of-thought.

No function here performs a real provider call unless invoked with an explicit
http_post seam AND a matching repository-bound Owner authorization; the test suite
always injects a fake HTTP seam. Real provider calls remain forbidden to this worker.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from enum import Enum
from hashlib import sha256
import json
import os
import re
import time
from typing import Callable, Mapping, Sequence
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from src.jianghe_prespend_runtime import (
    HARD_PROJECT_CAP_CNY,
    CanonicalStructuredObservationArtifact,
    KIMI_K3_SPEC,
    MINIMAX_M3_SPEC,
    SelectedJiangheContextArtifact,
    VisualInputArtifact,
    load_current_repository_rate_card,
)
from src.jianghe_source_only_verification import (
    ROOT as REPOSITORY_ROOT,
    _repository_blob_bytes,
)
from src.jianghe_stage_a_runtime import StageAStimulus


V03_RUNTIME_VERSION = "JIANGHE_V03_CAPABILITY_RUNTIME_V0_1"
V03_CAPABILITY_ANSWER_CONTRACT_VERSION = "JIANGHE_V03_CAPABILITY_ANSWER_CONTRACT_V0_1"
V03_COMMON_EXAM_VERSION = "JIANGHE_V03_COMMON_EXAM_IDENTITY_V0_1"
V03_INFERENCE_CONFIG_VERSION = "JIANGHE_V03_PROVIDER_INFERENCE_CONFIG_V0_1"
V03_ATTEMPT_VERSION = "JIANGHE_V03_ATTEMPT_IDENTITY_V0_1"
V03_BUDGET_LEDGER_VERSION = "JIANGHE_V03_SHARED_CNY_BUDGET_LEDGER_V0_1"
V03_EVIDENCE_VERSION = "JIANGHE_V03_PROVIDER_INVOCATION_EVIDENCE_V0_1"
V03_PLAN_VERSION = "JIANGHE_STAGE_A_FROZEN_PLAN_V0_3"
V03_PROTOCOL_VERSION = "JIANGHE_STAGE_A_V0_3_CAPABILITY_FIRST_PROTOCOL"
V03_QUALIFICATION_FIXTURE_ID = "JH-FIX-C-001"
V03_REMOTE_REF = "refs/heads/stage-a-live-state-v0-3"

HISTORICAL_PROJECT_ACCOUNTED_CNY = Decimal("0.270021")
HISTORICAL_DEEPSEEK_CNY = Decimal("0.219222")
HISTORICAL_MINIMAX_CNY = Decimal("0.050799")
HISTORICAL_KIMI_CNY = Decimal("0")

# Provider-specific V0.3 completion headroom and network timeout (first-party basis).
V03_MAX_OUTPUT_TOKENS = 131072
V03_NETWORK_TIMEOUT_SECONDS = 900

# Allowed capability-answer enum spaces (shared verbatim by all three providers).
FAMILY_ALLOWED = ("A", "B", "C", "D", "NONE", "UNKNOWN")
ACTION_ALLOWED = ("WAIT", "NO_TRADE", "ENTER", "MANAGE", "EXIT")
DIRECTION_ALLOWED = ("LONG", "SHORT", "NONE", "UNKNOWN")

# The exact shared final-answer headings contract (SAME_QUESTION across providers).
CAPABILITY_ANSWER_HEADINGS = (
    "MARKET_INTERPRETATION",
    "FAMILY",
    "SETUP_OR_NO_SETUP",
    "ACTION",
    "DIRECTION_IF_APPLICABLE",
    "EVIDENCE",
    "INVALIDATION_OR_UNCERTAINTY",
    "JIANGHE_PRINCIPLES_USED",
    "VISUAL_OBSERVATIONS",
    "STRUCTURED_OBSERVATIONS",
    "CONTRADICTIONS",
    "DECLARED_UNKNOWN",
)

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_HEADING_LINE = re.compile(
    r"^\s*\*{0,2}([A-Z][A-Z0-9_]{2,})\*{0,2}:\s*(.*)$"
)
_CANT_JUDGE = (
    "无法判断", "无法确定", "无法判定", "cannot determine", "cannot judge",
    "cannot tell", "uncertain", "不确定",
)


class V03TerminalStatus(str, Enum):
    INFRASTRUCTURE_FAILURE = "INFRASTRUCTURE_FAILURE"
    TRANSPORT_FAILURE = "TRANSPORT_FAILURE"
    TRANSPORT_HTTP_ERROR = "TRANSPORT_HTTP_ERROR"
    PROVIDER_RESPONSE_MALFORMED = "PROVIDER_RESPONSE_MALFORMED"
    PROVIDER_MODEL_MISMATCH = "PROVIDER_MODEL_MISMATCH"
    OUTPUT_EMPTY = "OUTPUT_EMPTY"
    OUTPUT_TRUNCATED = "OUTPUT_TRUNCATED"
    COMPLETE_CAPABILITY_ANSWER = "COMPLETE_CAPABILITY_ANSWER"
    FORMAT_ADAPTER_INCOMPATIBLE = "FORMAT_ADAPTER_INCOMPATIBLE"
    CAPABILITY_SCOREABLE = "CAPABILITY_SCOREABLE"
    CAPABILITY_NOT_SCOREABLE = "CAPABILITY_NOT_SCOREABLE"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _hash_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def _require_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value


def _require_sha256(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise ValueError(f"{name} must be a lowercase sha256")
    return value


def _require_aware(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _utc(value: datetime) -> str:
    return _require_aware(value, "datetime").astimezone(timezone.utc).isoformat(
        timespec="microseconds"
    )


def _decimal(value: object, name: str, *, positive: bool = False) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{name} must be a finite Decimal") from None
    if not result.is_finite() or (positive and result <= 0) or (not positive and result < 0):
        raise ValueError(f"{name} has invalid Decimal value")
    return result


def _decimal_text(value: Decimal | None) -> str | None:
    if value is None:
        return None
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _scan_forbidden(value: object, path: str = "$") -> None:
    forbidden = frozenset({
        "outcome", "candidate_outcome", "pnl", "profit", "profits", "loss", "losses",
        "win_rate", "winrate", "sharpe", "expectancy", "future_price", "future_return",
        "return", "returns", "equity_curve",
    })
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} key must be text")
            normalized = key.lower().replace("-", "_").replace(" ", "_")
            if normalized in forbidden:
                raise ValueError(f"{path} contains forbidden outcome/future field {key}")
            _scan_forbidden(nested, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _scan_forbidden(nested, f"{path}[{index}]")


@dataclass(frozen=True)
class V03ProviderInferenceConfig:
    """Provider-specific wire/reasoning/headroom configuration (V0.3)."""

    provider_id: str
    model_id: str
    endpoint: str
    api_key_env: str
    payload_style: str
    thinking: Mapping[str, object] | None
    reasoning_effort: str | None
    reasoning_split: bool | None
    max_output_field: str
    max_output_tokens: int
    network_timeout_seconds: int
    stream: bool
    tools: tuple[str, ...]
    response_format_policy: str
    image_wire_syntax: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        for name in ("provider_id", "model_id", "endpoint", "api_key_env", "payload_style"):
            _require_text(getattr(self, name), name)
        if not self.endpoint.startswith("https://"):
            raise ValueError("provider endpoint must be https")
        if self.max_output_field not in {"max_tokens", "max_completion_tokens"}:
            raise ValueError("unsupported max-output field")
        if not isinstance(self.max_output_tokens, int) or self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be positive")
        if not isinstance(self.network_timeout_seconds, int) or self.network_timeout_seconds <= 0:
            raise ValueError("network_timeout_seconds must be positive")
        if type(self.stream) is not bool:
            raise ValueError("stream must be strict bool")
        if self.response_format_policy != "NONE":
            raise ValueError("V0.3 capability pass forbids response-format forcing")
        if self.image_wire_syntax != "OPENAI_IMAGE_URL_BASE64":
            raise ValueError("V0.3 visual wire syntax is frozen to base64 image_url")
        object.__setattr__(self, "identity", _hash({
            "version": V03_INFERENCE_CONFIG_VERSION,
            "provider_id": self.provider_id,
            "model_id": self.model_id,
            "endpoint": self.endpoint,
            "api_key_env": self.api_key_env,
            "payload_style": self.payload_style,
            "thinking": self.thinking,
            "reasoning_effort": self.reasoning_effort,
            "reasoning_split": self.reasoning_split,
            "max_output_field": self.max_output_field,
            "max_output_tokens": self.max_output_tokens,
            "network_timeout_seconds": self.network_timeout_seconds,
            "stream": self.stream,
            "tools": tuple(sorted(self.tools)),
            "response_format_policy": self.response_format_policy,
            "image_wire_syntax": self.image_wire_syntax,
        }))


DEEPSEEK_V03_CONFIG = V03ProviderInferenceConfig(
    provider_id="DEEPSEEK",
    model_id="deepseek-v4-flash-vision-exp",
    endpoint="https://api.deepseek.com/chat/completions",
    api_key_env="DEEPSEEK_API_KEY",
    payload_style="DEEPSEEK_OPENAI",
    thinking={"type": "enabled"},
    reasoning_effort="max",
    reasoning_split=None,
    max_output_field="max_tokens",
    max_output_tokens=V03_MAX_OUTPUT_TOKENS,
    network_timeout_seconds=V03_NETWORK_TIMEOUT_SECONDS,
    stream=False,
    tools=(),
    response_format_policy="NONE",
    image_wire_syntax="OPENAI_IMAGE_URL_BASE64",
)

MINIMAX_V03_CONFIG = V03ProviderInferenceConfig(
    provider_id="MINIMAX",
    model_id="MiniMax-M3",
    endpoint="https://api.minimaxi.com/v1/chat/completions",
    api_key_env="MINIMAX_API_KEY",
    payload_style="MINIMAX_V2",
    thinking={"type": "adaptive"},
    reasoning_effort=None,
    reasoning_split=True,
    max_output_field="max_completion_tokens",
    max_output_tokens=V03_MAX_OUTPUT_TOKENS,
    network_timeout_seconds=V03_NETWORK_TIMEOUT_SECONDS,
    stream=False,
    tools=(),
    response_format_policy="NONE",
    image_wire_syntax="OPENAI_IMAGE_URL_BASE64",
)

KIMI_V03_CONFIG = V03ProviderInferenceConfig(
    provider_id="KIMI",
    model_id="kimi-k3",
    endpoint="https://api.moonshot.cn/v1/chat/completions",
    api_key_env="MOONSHOT_API_KEY",
    payload_style="KIMI_OPENAI",
    thinking=None,
    reasoning_effort="max",
    reasoning_split=None,
    max_output_field="max_completion_tokens",
    max_output_tokens=V03_MAX_OUTPUT_TOKENS,
    network_timeout_seconds=V03_NETWORK_TIMEOUT_SECONDS,
    stream=False,
    tools=(),
    response_format_policy="NONE",
    image_wire_syntax="OPENAI_IMAGE_URL_BASE64",
)

V03_PROVIDER_CONFIGS = (DEEPSEEK_V03_CONFIG, MINIMAX_V03_CONFIG, KIMI_V03_CONFIG)
V03_EXECUTION_ORDER = ("DEEPSEEK", "MINIMAX", "KIMI")


def v03_slot_identity(provider_id: str, sequence: int = 1) -> str:
    _require_text(provider_id, "provider_id")
    if provider_id not in V03_EXECUTION_ORDER:
        raise ValueError("unsupported V0.3 provider slot")
    if type(sequence) is not int or sequence < 1 or sequence > 999:
        raise ValueError("V0.3 slot sequence must be an integer from 1 to 999")
    return f"V0_3:{provider_id}:CAPABILITY_MATCHED_{sequence:03d}"


def v03_capability_answer_contract_payload() -> dict[str, object]:
    return {
        "version": V03_CAPABILITY_ANSWER_CONTRACT_VERSION,
        "headings": list(CAPABILITY_ANSWER_HEADINGS),
        "family_allowed": list(FAMILY_ALLOWED),
        "action_allowed": list(ACTION_ALLOWED),
        "direction_allowed": list(DIRECTION_ALLOWED),
        "production_json_required": False,
        "hint_expected_answer": False,
        "output_format": "CLEAR_HEADED_TEXT",
    }


def v03_capability_answer_contract_identity() -> str:
    return _hash(v03_capability_answer_contract_payload())


@dataclass(frozen=True)
class V03CommonExamIdentity:
    """Provider-neutral identity proving SAME_MATERIAL/SAME_QUESTION across models."""

    fixture_id: str
    stimulus_identity: str
    source_observation_identity: str
    point_in_time: str
    system_prompt_sha256: str
    decision_prompt_sha256: str
    capability_answer_contract_identity: str
    selected_context_identity: str
    model_context_identity: str
    structured_observation_identity: str
    png_sha256: str
    visual_artifact_identity: str
    renderer_config_identity: str
    outcome_future_ban: bool = True
    tools_search_ban: bool = True
    production_json_ban: bool = True
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.fixture_id, "fixture_id")
        _require_text(self.point_in_time, "point_in_time")
        for name in (
            "stimulus_identity", "source_observation_identity",
            "system_prompt_sha256", "decision_prompt_sha256",
            "capability_answer_contract_identity", "selected_context_identity",
            "model_context_identity", "structured_observation_identity",
            "png_sha256", "visual_artifact_identity", "renderer_config_identity",
        ):
            _require_sha256(getattr(self, name), name)
        for name in ("outcome_future_ban", "tools_search_ban", "production_json_ban"):
            if type(getattr(self, name)) is not bool:
                raise ValueError(f"{name} must be strict bool")
        object.__setattr__(self, "identity", _hash({
            "version": V03_COMMON_EXAM_VERSION,
            "fixture_id": self.fixture_id,
            "stimulus_identity": self.stimulus_identity,
            "source_observation_identity": self.source_observation_identity,
            "point_in_time": self.point_in_time,
            "system_prompt_sha256": self.system_prompt_sha256,
            "decision_prompt_sha256": self.decision_prompt_sha256,
            "capability_answer_contract_identity": self.capability_answer_contract_identity,
            "selected_context_identity": self.selected_context_identity,
            "model_context_identity": self.model_context_identity,
            "structured_observation_identity": self.structured_observation_identity,
            "png_sha256": self.png_sha256,
            "visual_artifact_identity": self.visual_artifact_identity,
            "renderer_config_identity": self.renderer_config_identity,
            "outcome_future_ban": self.outcome_future_ban,
            "tools_search_ban": self.tools_search_ban,
            "production_json_ban": self.production_json_ban,
        }))


@dataclass(frozen=True)
class V03AttemptIdentity:
    common_exam_identity: str
    provider_inference_config_identity: str
    slot_identity: str
    model_request_at: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "common_exam_identity", "provider_inference_config_identity",
        ):
            _require_sha256(getattr(self, name), name)
        _require_text(self.slot_identity, "slot_identity")
        _require_text(self.model_request_at, "model_request_at")
        object.__setattr__(self, "identity", _hash({
            "version": V03_ATTEMPT_VERSION,
            "common_exam_identity": self.common_exam_identity,
            "provider_inference_config_identity": self.provider_inference_config_identity,
            "slot_identity": self.slot_identity,
            "model_request_at": self.model_request_at,
        }))


@dataclass(frozen=True)
class V03CapabilityAnswer:
    """Format-only normalized capability view. Never invents or repairs semantics."""

    raw_final_answer: str
    headings: Mapping[str, str]
    missing_headings: tuple[str, ...]
    duplicate_headings: tuple[str, ...]
    family: str | None
    action: str | None
    direction: str | None
    declared_unknown: tuple[str, ...]
    invalid_enum_fields: tuple[str, ...]
    truncated: bool
    adapter_identity: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.raw_final_answer, "raw_final_answer")
        for name in (
            "missing_headings", "duplicate_headings", "declared_unknown",
            "invalid_enum_fields",
        ):
            if any(not isinstance(value, str) or not value for value in getattr(self, name)):
                raise ValueError(f"{name} must contain non-empty strings")
            if tuple(sorted(set(getattr(self, name)))) != getattr(self, name):
                raise ValueError(f"{name} must be sorted and unique")
        for name in ("family", "action", "direction"):
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"{name} must be text or null")
        if type(self.truncated) is not bool:
            raise ValueError("truncated must be strict bool")
        object.__setattr__(self, "identity", _hash({
            "version": V03_CAPABILITY_ANSWER_CONTRACT_VERSION,
            "raw_final_answer_sha256": sha256(self.raw_final_answer.encode("utf-8")).hexdigest(),
            "headings": {key: value for key, value in sorted(self.headings.items())},
            "missing_headings": self.missing_headings,
            "duplicate_headings": self.duplicate_headings,
            "family": self.family,
            "action": self.action,
            "direction": self.direction,
            "declared_unknown": self.declared_unknown,
            "invalid_enum_fields": self.invalid_enum_fields,
            "truncated": self.truncated,
            "adapter_identity": self.adapter_identity,
        }))

    @property
    def scoreable(self) -> bool:
        required = {
            "MARKET_INTERPRETATION": self.headings.get("MARKET_INTERPRETATION"),
            "FAMILY": self.family,
            "ACTION": self.action,
            "EVIDENCE": self.headings.get("EVIDENCE"),
        }
        if self.truncated:
            return False
        if self.invalid_enum_fields:
            return False
        return all(value not in (None, "") for value in required.values())


V03_ADAPTER_VERSION = "JIANGHE_V03_FORMAT_ONLY_CAPABILITY_ADAPTER_V0_1"
V03_ADAPTER_IDENTITY = _hash({
    "version": V03_ADAPTER_VERSION,
    "semantics": "FORMAT_ONLY__NO_COMPLETION__NO_CORRECTION__NO_REINTERPRETATION__NO_GUESSING",
    "family_inference_from_prose": "FORBIDDEN",
    "action_inference_from_prose": "FORBIDDEN",
    "duplicate_heading_policy": "MARK_DUPLICATE",
    "missing_heading_policy": "MARK_MISSING",
    "truncation_policy": "NEVER_COMPLETE",
    "invented_threshold_policy": "PRESERVE_VERBATIM",
})


def unwrap_markdown_json(raw: str) -> str:
    """Representation-only unwrap of a single fenced JSON block; no semantic change."""
    text = raw.strip()
    if text.startswith("```"):
        match = re.fullmatch(r"```(?:json)?\s*\n(.*?)\n```", text, flags=re.DOTALL)
        if match is not None:
            candidate = match.group(1).strip()
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                return raw
            if isinstance(parsed, dict):
                return candidate
    return raw


class V03CapabilityAdapter:
    """Format-only adapter. It may only change representation, never model meaning."""

    identity = V03_ADAPTER_IDENTITY

    def adapt(self, raw_final_answer: str, *, truncated: bool = False) -> V03CapabilityAnswer:
        _require_text(raw_final_answer, "raw_final_answer")
        if type(truncated) is not bool:
            raise ValueError("truncated must be strict bool")
        unwrapped = unwrap_markdown_json(raw_final_answer)
        sections: dict[str, list[str]] = {}
        order: list[str] = []
        current: str | None = None
        for line in unwrapped.splitlines():
            match = _HEADING_LINE.match(line)
            if match is not None:
                heading, inline = match.group(1), match.group(2).strip()
                if heading in CAPABILITY_ANSWER_HEADINGS:
                    current = heading
                    if current not in sections:
                        sections[current] = []
                        order.append(current)
                    if inline:
                        sections[current].append(inline)
                    continue
            if current is not None:
                stripped = line.strip()
                if stripped:
                    sections[current].append(stripped)
        headings = {heading: "\n".join(lines).strip() for heading, lines in sections.items()}
        counts = {heading: sum(1 for _ in [1]) for heading in sections}
        duplicate_headings = tuple(
            heading for heading, lines in sections.items()
            if len(lines) == 0 and heading in headings
        )
        # Recompute duplicates by counting heading occurrences in the raw text.
        raw_upper = unwrapped.upper()
        duplicates: list[str] = []
        for heading in CAPABILITY_ANSWER_HEADINGS:
            pattern = re.compile(
                rf"^\s*\*{{0,2}}{re.escape(heading)}\*{{0,2}}:",
                flags=re.MULTILINE,
            )
            if len(pattern.findall(unwrapped)) > 1:
                duplicates.append(heading)
        missing_headings = tuple(sorted(
            heading for heading in CAPABILITY_ANSWER_HEADINGS
            if heading not in headings
        ))

        def enum_value(heading: str, allowed: Sequence[str]) -> tuple[str | None, bool]:
            raw_value = (headings.get(heading) or "").strip().splitlines()[0].strip() if headings.get(heading) else ""
            token = raw_value.strip(" *-•\t") .upper().rstrip(".")
            lower_raw = raw_value.lower()
            if token in allowed:
                return token, False
            if any(marker in lower_raw for marker in _CANT_JUDGE):
                return None, False
            if token:
                return None, True
            return None, False

        family, family_invalid = enum_value("FAMILY", FAMILY_ALLOWED)
        action, action_invalid = enum_value("ACTION", ACTION_ALLOWED)
        direction, direction_invalid = enum_value("DIRECTION_IF_APPLICABLE", DIRECTION_ALLOWED)
        invalid_fields = tuple(
            name for name, invalid in (
                ("FAMILY", family_invalid), ("ACTION", action_invalid),
                ("DIRECTION_IF_APPLICABLE", direction_invalid),
            )
            if invalid
        )
        declared_unknown = tuple(sorted({
            marker for marker in _CANT_JUDGE if marker in unwrapped.lower()
        }))
        # Declared_unknown also surfaces explicit unknown tokens in enum fields.
        unknown_tokens = ("UNKNOWN", "NONE")
        if any(headings.get(heading, "").upper() in unknown_tokens for heading in ("FAMILY", "DIRECTION_IF_APPLICABLE")):
            declared_unknown = tuple(sorted(set((*declared_unknown, "DECLARED_UNKNOWN_TOKEN"))))
        return V03CapabilityAnswer(
            raw_final_answer=raw_final_answer,
            headings=headings,
            missing_headings=missing_headings,
            duplicate_headings=tuple(sorted(set(duplicates))),
            family=family,
            action=action,
            direction=direction,
            declared_unknown=declared_unknown,
            invalid_enum_fields=invalid_fields,
            truncated=truncated,
            adapter_identity=self.identity,
        )


@dataclass(frozen=True)
class V03Request:
    system_prompt: str
    decision_prompt: str
    context: SelectedJiangheContextArtifact
    structured_observation: CanonicalStructuredObservationArtifact
    visual: VisualInputArtifact
    common_exam_identity: V03CommonExamIdentity
    provider_config: V03ProviderInferenceConfig
    attempt_identity: V03AttemptIdentity
    point_in_time: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.system_prompt, "system_prompt")
        _require_text(self.decision_prompt, "decision_prompt")
        _require_text(self.point_in_time, "point_in_time")
        for artifact in (self.context, self.structured_observation, self.visual):
            if not isinstance(artifact, (SelectedJiangheContextArtifact,
                                         CanonicalStructuredObservationArtifact,
                                         VisualInputArtifact)):
                raise TypeError("V0.3 request artifacts are typed")
        if self.structured_observation.source_observation_identity != self.visual.source_observation_identity:
            raise ValueError("structured and visual inputs must bind the same observation")
        if self.attempt_identity.common_exam_identity != self.common_exam_identity.identity:
            raise ValueError("attempt does not bind the common exam identity")
        if self.attempt_identity.provider_inference_config_identity != self.provider_config.identity:
            raise ValueError("attempt does not bind the provider inference config")
        object.__setattr__(self, "identity", _hash({
            "version": V03_RUNTIME_VERSION,
            "system_prompt_sha256": sha256(self.system_prompt.encode("utf-8")).hexdigest(),
            "decision_prompt_sha256": sha256(self.decision_prompt.encode("utf-8")).hexdigest(),
            "selected_context_identity": self.context.identity,
            "model_context_identity": self.context.model_payload()["model_context_identity"],
            "structured_observation_identity": self.structured_observation.identity,
            "visual_identity": self.visual.identity,
            "png_sha256": self.visual.content_sha256,
            "common_exam_identity": self.common_exam_identity.identity,
            "provider_inference_config_identity": self.provider_config.identity,
            "attempt_identity": self.attempt_identity.identity,
            "point_in_time": self.point_in_time,
        }))

    def common_model_text(self) -> str:
        return _canonical_json({
            "jianghe_context": self.context.model_payload(),
            "canonical_observation": self.structured_observation.payload(),
            "decision_instruction": self.decision_prompt,
        })


@dataclass(frozen=True)
class V03TokenUsage:
    prompt_tokens: int
    cached_input_tokens: int
    image_tokens: int
    reasoning_tokens: int | None
    completion_tokens: int

    def __post_init__(self) -> None:
        for name in ("prompt_tokens", "cached_input_tokens", "image_tokens", "completion_tokens"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.reasoning_tokens is not None and (
            isinstance(self.reasoning_tokens, bool)
            or not isinstance(self.reasoning_tokens, int)
            or self.reasoning_tokens < 0
        ):
            raise ValueError("reasoning_tokens must be a non-negative integer or null")


@dataclass(frozen=True)
class V03InvocationEvidence:
    request_identity: str
    common_exam_identity: str
    provider_inference_config_identity: str
    attempt_identity: str
    slot_identity: str
    provider_id: str
    requested_model_id: str
    resolved_model_id: str
    provider_request_id: str
    finish_reason: str | None
    final_content_state: str
    model_raw_final_answer: str | None
    final_content_sha256: str | None
    usage: V03TokenUsage | None
    reasoning_present: bool
    reasoning_length: int | None
    reasoning_sha256: str | None
    latency_ms: int
    terminal_status: str
    precall_conservative_reservation_cny: str
    postcall_calculated_cny: str
    calculated_is_conservative: bool
    provider_reported_billed_cny: str | None
    accounted_cny_for_hard_cap: str
    rate_card_identity: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "request_identity", "common_exam_identity", "provider_inference_config_identity",
            "attempt_identity", "requested_model_id", "resolved_model_id",
            "provider_request_id", "precall_conservative_reservation_cny",
            "postcall_calculated_cny", "accounted_cny_for_hard_cap",
        ):
            _require_text(getattr(self, name), name)
        for name in ("common_exam_identity", "provider_inference_config_identity",
                     "attempt_identity"):
            _require_sha256(getattr(self, name), name)
        if self.model_raw_final_answer is not None and (
            self.final_content_sha256 is None
            or sha256(self.model_raw_final_answer.encode("utf-8")).hexdigest() != self.final_content_sha256
        ):
            raise ValueError("raw final answer hash mismatch")
        if self.model_raw_final_answer is None and self.final_content_sha256 is not None:
            raise ValueError("final hash without raw final answer")
        if type(self.reasoning_present) is not bool:
            raise ValueError("reasoning_present must be strict bool")
        if self.reasoning_present and (
            self.reasoning_length is None or self.reasoning_sha256 is None
        ):
            raise ValueError("reasoning metadata required when reasoning present")
        if not self.reasoning_present and any(
            value is not None for value in (self.reasoning_length, self.reasoning_sha256)
        ):
            raise ValueError("reasoning metadata without reasoning_present")
        if not isinstance(self.latency_ms, int) or self.latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")
        object.__setattr__(self, "identity", _hash({
            "version": V03_EVIDENCE_VERSION,
            "request_identity": self.request_identity,
            "common_exam_identity": self.common_exam_identity,
            "provider_inference_config_identity": self.provider_inference_config_identity,
            "attempt_identity": self.attempt_identity,
            "slot_identity": self.slot_identity,
            "provider_id": self.provider_id,
            "requested_model_id": self.requested_model_id,
            "resolved_model_id": self.resolved_model_id,
            "provider_request_id": self.provider_request_id,
            "finish_reason": self.finish_reason,
            "final_content_state": self.final_content_state,
            "model_raw_final_answer_sha256": (
                None if self.model_raw_final_answer is None
                else sha256(self.model_raw_final_answer.encode("utf-8")).hexdigest()
            ),
            "usage": None if self.usage is None else {
                "prompt_tokens": self.usage.prompt_tokens,
                "cached_input_tokens": self.usage.cached_input_tokens,
                "image_tokens": self.usage.image_tokens,
                "reasoning_tokens": self.usage.reasoning_tokens,
                "completion_tokens": self.usage.completion_tokens,
            },
            "reasoning_present": self.reasoning_present,
            "reasoning_length": self.reasoning_length,
            "reasoning_sha256": self.reasoning_sha256,
            "latency_ms": self.latency_ms,
            "terminal_status": self.terminal_status,
            "precall_conservative_reservation_cny": self.precall_conservative_reservation_cny,
            "postcall_calculated_cny": self.postcall_calculated_cny,
            "calculated_is_conservative": self.calculated_is_conservative,
            "provider_reported_billed_cny": self.provider_reported_billed_cny,
            "accounted_cny_for_hard_cap": self.accounted_cny_for_hard_cap,
            "rate_card_identity": self.rate_card_identity,
        }))

    def to_durable(self, *, redact: Sequence[str] = ()) -> dict[str, object]:
        """Secret-safe durable evidence: raw final answer preserved, reasoning text never."""
        payload: dict[str, object] = {
            "artifact_schema_version": V03_EVIDENCE_VERSION,
            "evidence_identity": self.identity,
            "request_identity": self.request_identity,
            "common_exam_identity": self.common_exam_identity,
            "provider_inference_config_identity": self.provider_inference_config_identity,
            "attempt_identity": self.attempt_identity,
            "slot_identity": self.slot_identity,
            "provider_id": self.provider_id,
            "requested_model_id": self.requested_model_id,
            "resolved_model_id": self.resolved_model_id,
            "provider_request_id": self.provider_request_id,
            "finish_reason": self.finish_reason,
            "final_content_state": self.final_content_state,
            "model_raw_final_answer": self.model_raw_final_answer,
            "final_content_sha256": self.final_content_sha256,
            "usage": None if self.usage is None else {
                "prompt_tokens": self.usage.prompt_tokens,
                "cached_input_tokens": self.usage.cached_input_tokens,
                "image_tokens": self.usage.image_tokens,
                "reasoning_tokens": self.usage.reasoning_tokens,
                "completion_tokens": self.usage.completion_tokens,
            },
            "reasoning_present": self.reasoning_present,
            "reasoning_length": self.reasoning_length,
            "reasoning_sha256": self.reasoning_sha256,
            "latency_ms": self.latency_ms,
            "terminal_status": self.terminal_status,
            "precall_conservative_reservation_cny": self.precall_conservative_reservation_cny,
            "postcall_calculated_cny": self.postcall_calculated_cny,
            "calculated_is_conservative": self.calculated_is_conservative,
            "provider_reported_billed_cny": self.provider_reported_billed_cny,
            "accounted_cny_for_hard_cap": self.accounted_cny_for_hard_cap,
            "rate_card_identity": self.rate_card_identity,
            "hidden_reasoning_persisted": False,
            "raw_provider_body_persisted": False,
        }
        serialized = _canonical_json(payload)
        for secret in redact:
            if secret:
                serialized = serialized.replace(secret, "<REDACTED>")
        return json.loads(serialized)


class V03BudgetLedger:
    """Shared CNY hard-cap ledger carrying the historical 0.270021 CNY forward."""

    def __init__(
        self,
        *,
        cap_cny: Decimal = HARD_PROJECT_CAP_CNY,
        historical_accounted_cny: Decimal = HISTORICAL_PROJECT_ACCOUNTED_CNY,
    ) -> None:
        cap = _decimal(cap_cny, "cap_cny", positive=True)
        if cap > HARD_PROJECT_CAP_CNY:
            raise ValueError("project hard cap cannot exceed CNY 100")
        historical = _decimal(historical_accounted_cny, "historical_accounted_cny")
        if historical > cap:
            raise ValueError("historical accounted spend exceeds the hard cap")
        self._cap = cap
        self._spent = historical
        self._historical = historical
        self._outstanding: dict[str, object] | None = None

    @property
    def cap_cny(self) -> Decimal:
        return self._cap

    @property
    def spent_cny(self) -> Decimal:
        return self._spent

    @property
    def historical_accounted_cny(self) -> Decimal:
        return self._historical

    @property
    def remaining_cny(self) -> Decimal:
        outstanding = Decimal("0")
        if self._outstanding is not None:
            outstanding = _decimal(self._outstanding["reserved_cny"], "reserved_cny")
        return self._cap - self._spent - outstanding

    def reserve(
        self,
        *,
        provider_config: V03ProviderInferenceConfig,
        rate_card,
        max_text_input_tokens: int,
        max_image_tokens: int,
        now: datetime,
    ) -> dict[str, object]:
        if self._outstanding is not None:
            raise ValueError("previous reservation must be reconciled before another call")
        if rate_card.provider_id != provider_config.provider_id:
            raise ValueError("rate card does not match provider config")
        if not rate_card.image_tokens_billed_as_input:
            raise ValueError("unknown image billing semantics fail closed")
        million = Decimal("1000000")
        worst = (
            Decimal(max_text_input_tokens + max_image_tokens) * _decimal(rate_card.input_per_million, "input")
            + Decimal(provider_config.max_output_tokens) * _decimal(rate_card.output_per_million, "output")
        ) / million
        if worst <= 0:
            raise ValueError("worst-case reservation must be positive")
        if self._spent + worst > self._cap:
            raise ValueError("next call would exceed the shared CNY hard cap")
        reservation_id = _hash({
            "version": V03_BUDGET_LEDGER_VERSION,
            "provider_id": provider_config.provider_id,
            "model_id": provider_config.model_id,
            "rate_card_identity": rate_card.identity,
            "max_text_input_tokens": max_text_input_tokens,
            "max_image_tokens": max_image_tokens,
            "max_output_tokens": provider_config.max_output_tokens,
            "reserved_cny": _decimal_text(worst),
            "spent_before": _decimal_text(self._spent),
            "created_at": _utc(now),
        })
        self._outstanding = {
            "reservation_id": reservation_id,
            "provider_config": provider_config,
            "rate_card": rate_card,
            "reserved_cny": worst,
            "max_text_input_tokens": max_text_input_tokens,
            "max_image_tokens": max_image_tokens,
        }
        return {
            "reservation_id": reservation_id,
            "precall_conservative_reservation_cny": _decimal_text(worst),
        }

    def reconcile(
        self,
        *,
        usage: V03TokenUsage,
        provider_reported_billed_cny: Decimal | None,
        now: datetime,
    ) -> dict[str, object]:
        if self._outstanding is None:
            raise ValueError("no outstanding reservation to reconcile")
        reservation = self._outstanding
        rate_card = reservation["rate_card"]
        reserved = _decimal(reservation["reserved_cny"], "reserved_cny")
        bound_text = int(reservation["max_text_input_tokens"])
        bound_image = int(reservation["max_image_tokens"])
        total_input = usage.prompt_tokens + usage.image_tokens
        if total_input > bound_text + bound_image or usage.completion_tokens > int(
            reservation["provider_config"].max_output_tokens
        ):
            self._spent += reserved
            self._outstanding = None
            return {
                "postcall_calculated_cny": _decimal_text(reserved),
                "calculated_is_conservative": True,
                "provider_reported_billed_cny": None,
                "accounted_cny_for_hard_cap": _decimal_text(reserved),
                "bounds_breach": True,
            }
        million = Decimal("1000000")
        calculated = (
            Decimal(total_input) * _decimal(rate_card.input_per_million, "input")
            + Decimal(usage.completion_tokens) * _decimal(rate_card.output_per_million, "output")
        ) / million
        # Cache discount cannot be computed exactly from the committed pricing
        # authority (no cache rate fields), so the calculated figure is labeled
        # conservative: cached input tokens are NOT discounted.
        accounted = max(calculated, Decimal("0"))
        self._spent += accounted
        self._outstanding = None
        return {
            "postcall_calculated_cny": _decimal_text(calculated),
            "calculated_is_conservative": True,
            "provider_reported_billed_cny": (
                None if provider_reported_billed_cny is None
                else _decimal_text(provider_reported_billed_cny)
            ),
            "accounted_cny_for_hard_cap": _decimal_text(accounted),
            "bounds_breach": False,
        }

    def cancel_before_network(self, *, reason: str) -> None:
        if self._outstanding is None:
            raise ValueError("no outstanding reservation to cancel")
        _require_text(reason, "reason")
        self._outstanding = None

    def consume_full_reservation_on_unknown_usage(self) -> None:
        if self._outstanding is None:
            raise ValueError("no outstanding reservation to consume")
        reserved = _decimal(self._outstanding["reserved_cny"], "reserved_cny")
        self._spent += reserved
        self._outstanding = None


@dataclass(frozen=True)
class V03HttpResponse:
    status_code: int
    body: bytes


V03HttpPost = Callable[[str, Mapping[str, str], bytes, float], V03HttpResponse]


def _default_http_post(
    url: str, headers: Mapping[str, str], body: bytes, timeout: float
) -> V03HttpResponse:
    req = urllib_request.Request(url=url, data=body, headers=dict(headers), method="POST")
    try:
        with urllib_request.urlopen(req, timeout=timeout) as response:
            return V03HttpResponse(int(response.status), response.read())
    except HTTPError as error:
        return V03HttpResponse(int(error.code), error.read())
    except URLError as error:
        raise RuntimeError(f"provider transport failed: {error.reason}") from error


class V03ProviderTransport:
    """V0.3 mockable transport. No retry, no tools, no response-format forcing."""

    def __init__(
        self,
        config: V03ProviderInferenceConfig,
        *,
        http_post: V03HttpPost | None = None,
    ) -> None:
        if config not in V03_PROVIDER_CONFIGS:
            raise ValueError("provider is outside the V0.3 implementation target set")
        self.config = config
        self._http_post = http_post or _default_http_post

    def build_payload(self, request: V03Request) -> dict[str, object]:
        if request.provider_config.identity != self.config.identity:
            raise ValueError("request provider config differs from transport")
        text = request.common_model_text()
        multimodal_content: list[dict[str, object]] = [{"type": "text", "text": text}]
        multimodal_content.append({
            "type": "image_url",
            "image_url": {"url": request.visual.data_url()},
        })
        payload: dict[str, object] = {
            "model": self.config.model_id,
            "messages": [
                {"role": "system", "content": request.system_prompt},
                {"role": "user", "content": multimodal_content},
            ],
            "stream": self.config.stream,
            "tools": list(self.config.tools),
        }
        payload[self.config.max_output_field] = self.config.max_output_tokens
        if self.config.thinking is not None:
            payload["thinking"] = dict(self.config.thinking)
        if self.config.reasoning_effort is not None:
            payload["reasoning_effort"] = self.config.reasoning_effort
        if self.config.reasoning_split is not None:
            payload["reasoning_split"] = self.config.reasoning_split
        return payload

    def payload_bytes(self, request: V03Request) -> bytes:
        return _canonical_json(self.build_payload(request)).encode("utf-8")

    def conservative_text_input_token_bound(self, request: V03Request) -> int:
        return len(self.payload_bytes(request)) * 2 + 8192

    @staticmethod
    def _extract_mechanical(
        decoded: Mapping[str, object],
    ) -> tuple[str | None, str, Mapping[str, object], str | None, str | None, str | None]:
        choices = decoded.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], Mapping):
            raise ValueError("provider response has no choices")
        choice = choices[0]
        message = choice.get("message")
        if not isinstance(message, Mapping):
            raise ValueError("provider choice has no message")
        content = message.get("content")
        if content is None:
            content_state = "NULL"
        elif isinstance(content, str):
            content_state = "TEXT_NONEMPTY" if content else "TEXT_EMPTY"
        else:
            content_state = "NON_TEXT"
        final_text = content if isinstance(content, str) and content else None
        reasoning = message.get("reasoning_content")
        details = message.get("reasoning_details")
        reasoning_present = bool(reasoning) or bool(details)
        reasoning_bytes: bytes | None = None
        if isinstance(reasoning, str) and reasoning:
            reasoning_bytes = reasoning.encode("utf-8")
        elif isinstance(details, list) and details:
            reasoning_bytes = _canonical_json(details).encode("utf-8")
        usage_raw = decoded.get("usage")
        if not isinstance(usage_raw, Mapping):
            raise ValueError("provider response has no auditable usage")
        prompt = usage_raw.get("prompt_tokens")
        completion = usage_raw.get("completion_tokens")
        if not isinstance(prompt, int) or isinstance(prompt, bool) or prompt < 0:
            raise ValueError("prompt token usage is unavailable")
        if not isinstance(completion, int) or isinstance(completion, bool) or completion < 0:
            raise ValueError("completion token usage is unavailable")
        image = usage_raw.get("image_tokens", 0)
        if not isinstance(image, int) or isinstance(image, bool) or image < 0:
            image = 0
        cached = 0
        details_raw = usage_raw.get("prompt_tokens_details")
        if isinstance(details_raw, Mapping):
            cached_raw = details_raw.get("cached_tokens", 0)
            if isinstance(cached_raw, int) and not isinstance(cached_raw, bool) and cached_raw >= 0:
                cached = cached_raw
        reasoning_tokens: int | None = None
        completion_details = usage_raw.get("completion_tokens_details")
        if isinstance(completion_details, Mapping):
            rt = completion_details.get("reasoning_tokens")
            if isinstance(rt, int) and not isinstance(rt, bool) and rt >= 0:
                reasoning_tokens = rt
                if reasoning_tokens > 0:
                    reasoning_present = True
        finish = choice.get("finish_reason")
        resolved = decoded.get("model")
        request_id = decoded.get("id")
        mechanical: dict[str, object] = {
            "final_text": final_text,
            "content_state": content_state,
            "usage": V03TokenUsage(
                prompt_tokens=prompt,
                cached_input_tokens=cached,
                image_tokens=image,
                reasoning_tokens=reasoning_tokens,
                completion_tokens=completion,
            ),
            "reasoning_present": reasoning_present,
            "reasoning_length": None if reasoning_bytes is None else len(reasoning_bytes),
            "reasoning_sha256": None if reasoning_bytes is None else sha256(reasoning_bytes).hexdigest(),
        }
        return (
            final_text,
            content_state,
            mechanical,
            finish if isinstance(finish, str) and finish else None,
            resolved if isinstance(resolved, str) and resolved else None,
            request_id if isinstance(request_id, str) and request_id else None,
        )

    def invoke(
        self,
        request: V03Request,
        *,
        budget: V03BudgetLedger,
        rate_card,
        max_image_tokens: int,
        now: datetime,
        api_key: str | None = None,
        http_post: V03HttpPost | None = None,
    ) -> V03InvocationEvidence:
        if budget is None or not isinstance(budget, V03BudgetLedger):
            raise TypeError("budget must be V03BudgetLedger")
        if rate_card.provider_id != self.config.provider_id:
            raise ValueError("rate card does not match provider")
        post = http_post or self._http_post
        payload_bytes = self.payload_bytes(request)
        text_bound = self.conservative_text_input_token_bound(request)
        reservation = budget.reserve(
            provider_config=self.config,
            rate_card=rate_card,
            max_text_input_tokens=text_bound,
            max_image_tokens=max_image_tokens,
            now=now,
        )
        resolved_key = api_key if api_key is not None else os.environ.get(self.config.api_key_env)
        if not resolved_key:
            budget.cancel_before_network(reason="MISSING_CREDENTIAL")
            raise RuntimeError("provider credential is unavailable")
        headers = {
            "Authorization": f"Bearer {resolved_key}",
            "Content-Type": "application/json",
        }
        started = time.monotonic()
        try:
            response = post(
                self.config.endpoint, headers, payload_bytes, float(self.config.network_timeout_seconds)
            )
        except Exception:
            budget.consume_full_reservation_on_unknown_usage()
            raise
        latency_ms = max(0, int((time.monotonic() - started) * 1000))
        status: str
        if response.status_code < 200 or response.status_code >= 300:
            budget.consume_full_reservation_on_unknown_usage()
            raise RuntimeError(f"provider returned HTTP {response.status_code}")
        try:
            raw_body = response.body.decode("utf-8")
            decoded = json.loads(raw_body)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            budget.consume_full_reservation_on_unknown_usage()
            raise ValueError("provider returned malformed JSON") from error
        if not isinstance(decoded, Mapping):
            budget.consume_full_reservation_on_unknown_usage()
            raise ValueError("provider response top level must be an object")
        try:
            final_text, content_state, mechanical, finish, resolved_model, provider_request_id = (
                self._extract_mechanical(decoded)
            )
        except ValueError:
            budget.consume_full_reservation_on_unknown_usage()
            raise
        if resolved_model != self.config.model_id:
            budget.consume_full_reservation_on_unknown_usage()
            raise V03ModelMismatchError(resolved_model, self.config.model_id)
        if provider_request_id is None:
            budget.consume_full_reservation_on_unknown_usage()
            raise ValueError("provider request id is missing")

        usage = mechanical["usage"]
        if content_state in {"NULL", "TEXT_EMPTY", "NON_TEXT"}:
            status = V03TerminalStatus.OUTPUT_EMPTY.value
            final_for_evidence = None
            final_hash = None
            reconciled = budget.reconcile(
                usage=usage, provider_reported_billed_cny=None, now=now
            )
        else:
            status = (
                V03TerminalStatus.OUTPUT_TRUNCATED.value
                if finish == "length"
                else V03TerminalStatus.COMPLETE_CAPABILITY_ANSWER.value
            )
            assert final_text is not None
            final_for_evidence = final_text
            final_hash = sha256(final_text.encode("utf-8")).hexdigest()
            reconciled = budget.reconcile(
                usage=usage, provider_reported_billed_cny=None, now=now
            )
        return V03InvocationEvidence(
            request_identity=request.identity,
            common_exam_identity=request.common_exam_identity.identity,
            provider_inference_config_identity=self.config.identity,
            attempt_identity=request.attempt_identity.identity,
            slot_identity=request.attempt_identity.slot_identity,
            provider_id=self.config.provider_id,
            requested_model_id=self.config.model_id,
            resolved_model_id=resolved_model,
            provider_request_id=provider_request_id,
            finish_reason=finish,
            final_content_state=content_state,
            model_raw_final_answer=final_for_evidence,
            final_content_sha256=final_hash,
            usage=usage,
            reasoning_present=bool(mechanical["reasoning_present"]),
            reasoning_length=mechanical["reasoning_length"],
            reasoning_sha256=mechanical["reasoning_sha256"],
            latency_ms=latency_ms,
            terminal_status=status,
            precall_conservative_reservation_cny=str(reservation["precall_conservative_reservation_cny"]),
            postcall_calculated_cny=str(reconciled["postcall_calculated_cny"]),
            calculated_is_conservative=bool(reconciled["calculated_is_conservative"]),
            provider_reported_billed_cny=reconciled["provider_reported_billed_cny"],
            accounted_cny_for_hard_cap=str(reconciled["accounted_cny_for_hard_cap"]),
            rate_card_identity=rate_card.identity,
        )


class V03ModelMismatchError(RuntimeError):
    def __init__(self, resolved: str | None, requested: str) -> None:
        super().__init__(f"provider-resolved model '{resolved}' differs from requested '{requested}'")
        self.resolved_model = resolved
        self.requested_model = requested


__all__ = [
    "ACTION_ALLOWED", "CAPABILITY_ANSWER_HEADINGS", "DEEPSEEK_V03_CONFIG",
    "DIRECTION_ALLOWED", "FAMILY_ALLOWED", "HISTORICAL_DEEPSEEK_CNY",
    "HISTORICAL_KIMI_CNY", "HISTORICAL_MINIMAX_CNY", "HISTORICAL_PROJECT_ACCOUNTED_CNY",
    "KIMI_V03_CONFIG", "MINIMAX_V03_CONFIG", "V03_ADAPTER_IDENTITY", "V03AttemptIdentity",
    "V03BudgetLedger", "V03CapabilityAdapter", "V03CapabilityAnswer",
    "V03CommonExamIdentity", "V03HttpResponse", "V03InvocationEvidence",
    "V03ModelMismatchError", "V03NETWORK_TIMEOUT_SECONDS", "V03_MAX_OUTPUT_TOKENS",
    "V03ProviderInferenceConfig", "V03ProviderTransport", "V03Request",
    "V03TerminalStatus", "V03TokenUsage", "V03_EXECUTION_ORDER", "V03_PROVIDER_CONFIGS",
    "V03_REMOTE_REF", "V03_RUNTIME_VERSION", "load_current_repository_rate_card",
    "v03_capability_answer_contract_identity", "v03_capability_answer_contract_payload",
    "v03_slot_identity",
]

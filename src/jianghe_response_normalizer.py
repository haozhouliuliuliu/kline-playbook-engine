"""江河模型原始回复的严格、版本化、确定性 runtime normalizer。

本模块只记录模型实际输出的客观字段。违规原则、发明阈值等 fidelity 裁决必须由
评价侧结合 fixture 约束生成，不能由模型自评后直接成为评分事实。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from src.jianghe_ai_trader import AttentionMode, DecisionAction, Direction, StrategyFamily


NORMALIZER_VERSION = "JIANGHE_RUNTIME_RESPONSE_NORMALIZER_V0_1"
RESPONSE_SCHEMA_VERSION = "JIANGHE_RUNTIME_RESPONSE_V0_1"

_TOP_LEVEL_FIELDS = frozenset({
    "schema_version",
    "family",
    "action",
    "direction",
    "attention_mode",
    "decision_state",
    "rationale",
    "declared_unknown",
    "principle_references",
    "source_references",
    "numeric_claims",
})
_NUMERIC_CLAIM_FIELDS = frozenset({"claim", "value", "unit", "source_reference"})
_FORBIDDEN_OUTCOME_FIELDS = frozenset({
    "outcome", "candidate_outcome", "pnl", "profit", "profits", "loss", "losses",
    "win_rate", "winrate", "sharpe", "expectancy", "future_price", "future_return",
    "return", "returns", "equity_curve",
})
_FORBIDDEN_SELF_EVALUATION_FIELDS = frozenset({
    "violated_principles", "invented_thresholds", "no_violations", "no_inventions",
    "fidelity_score", "self_score", "is_faithful",
})


def _canonical_json(value: object) -> str:
    try:
        return json.dumps(
            value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
        )
    except (TypeError, ValueError) as error:
        raise ValueError("normalizer 数据必须是 JSON 兼容值") from error


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


RESPONSE_SCHEMA_IDENTITY = _hash({
    "schema_version": RESPONSE_SCHEMA_VERSION,
    "top_level_fields": sorted(_TOP_LEVEL_FIELDS),
    "numeric_claim_fields": sorted(_NUMERIC_CLAIM_FIELDS),
    "unknown_fields": "REJECT",
    "type_coercion": "FORBIDDEN",
})
NORMALIZER_IDENTITY = _hash({
    "normalizer_version": NORMALIZER_VERSION,
    "response_schema_identity": RESPONSE_SCHEMA_IDENTITY,
    "self_evaluation_fields": "REJECT",
    "outcome_fields": "REJECT_RECURSIVE",
})
EVALUATION_EXTRACTOR_VERSION = "JIANGHE_EVALUATOR_SIDE_EVIDENCE_EXTRACTOR_V0_1"
EVALUATION_EXTRACTOR_IDENTITY = _hash({
    "extractor_version": EVALUATION_EXTRACTOR_VERSION,
    "runtime_source": "NORMALIZED_JIANGHE_DECISION_OBJECTIVE_FIELDS_ONLY",
    "judgment_source": "EVALUATOR_SIDE_FIXTURE_CONSTRAINTS",
    "target_schema": "JIANGHE_FIDELITY_RESPONSE_STRICT_V0_1",
    "model_self_evaluation": "FORBIDDEN",
})


def _require_text(value: object, field_name: str, *, nullable: bool = False) -> str | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} 必须是非空字符串")
    return value


def _strict_string_list(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} 必须是 JSON 数组")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{field_name} 只能包含非空字符串")
    return tuple(sorted(set(value)))


def _scan_forbidden_fields(value: object, path: str = "response") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} 的键必须是字符串")
            normalized = key.lower().replace("-", "_").replace(" ", "_")
            if normalized in _FORBIDDEN_OUTCOME_FIELDS:
                raise ValueError(f"{path} 不得包含 outcome 字段: {key}")
            if normalized in _FORBIDDEN_SELF_EVALUATION_FIELDS:
                raise ValueError(f"{path} 不得包含模型自评字段: {key}")
            _scan_forbidden_fields(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            _scan_forbidden_fields(nested, f"{path}[{index}]")


def _enum(enum_type: type[Any], value: object, field_name: str) -> Any:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} 必须是字符串枚举")
    try:
        return enum_type(value)
    except ValueError:
        raise ValueError(f"{field_name} 不是受支持的枚举值") from None


@dataclass(frozen=True)
class NumericClaim:
    claim: str
    value: str
    unit: str | None
    source_reference: str | None

    def __post_init__(self) -> None:
        _require_text(self.claim, "numeric_claim.claim")
        _require_text(self.value, "numeric_claim.value")
        if self.value != self.value.strip():
            raise ValueError("numeric_claim.value 不得含首尾空白")
        try:
            parsed = Decimal(self.value)
        except InvalidOperation:
            raise ValueError("numeric_claim.value 必须是 Decimal 字符串") from None
        if not parsed.is_finite():
            raise ValueError("numeric_claim.value 不能是 NaN 或 Infinity")
        _require_text(self.unit, "numeric_claim.unit", nullable=True)
        _require_text(self.source_reference, "numeric_claim.source_reference", nullable=True)

    def to_payload(self) -> dict[str, str | None]:
        return {
            "claim": self.claim,
            "value": self.value,
            "unit": self.unit,
            "source_reference": self.source_reference,
        }


@dataclass(frozen=True)
class NormalizedJiangheDecision:
    family: StrategyFamily
    action: DecisionAction
    direction: Direction
    attention_mode: AttentionMode
    decision_state: str
    rationale: str
    raw_text: str
    declared_unknown: tuple[str, ...]
    principle_references: tuple[str, ...]
    source_references: tuple[str, ...]
    numeric_claims: tuple[NumericClaim, ...]
    normalizer_identity: str = NORMALIZER_IDENTITY
    response_schema_identity: str = RESPONSE_SCHEMA_IDENTITY
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.decision_state, "decision_state")
        _require_text(self.rationale, "rationale")
        _require_text(self.raw_text, "raw_text")
        if self.action is DecisionAction.NO_TRADE and self.direction is not Direction.NONE:
            raise ValueError("NO_TRADE 必须使用 NONE 方向")
        if self.action is DecisionAction.ENTER and self.direction is Direction.NONE:
            raise ValueError("ENTER 必须明确 LONG 或 SHORT")
        payload = {
            "normalizer_identity": self.normalizer_identity,
            "response_schema_identity": self.response_schema_identity,
            "family": self.family.value,
            "action": self.action.value,
            "direction": self.direction.value,
            "attention_mode": self.attention_mode.value,
            "decision_state": self.decision_state,
            "rationale": self.rationale,
            "raw_response_sha256": sha256(self.raw_text.encode("utf-8")).hexdigest(),
            "declared_unknown": self.declared_unknown,
            "principle_references": self.principle_references,
            "source_references": self.source_references,
            "numeric_claims": [claim.to_payload() for claim in self.numeric_claims],
        }
        object.__setattr__(self, "identity", _hash(payload))


class JiangheResponseNormalizer:
    """严格解析 raw provider text；未知字段、宽松类型和污染一律拒绝。"""

    identity = NORMALIZER_IDENTITY

    def normalize(self, raw_response: str) -> NormalizedJiangheDecision:
        if not isinstance(raw_response, str) or not raw_response.strip():
            raise ValueError("raw_response 必须是非空字符串")
        try:
            payload = json.loads(raw_response)
        except json.JSONDecodeError as error:
            raise ValueError("raw_response 必须是合法 JSON 对象") from error
        if not isinstance(payload, dict):
            raise ValueError("raw_response 顶层必须是 JSON 对象")
        _scan_forbidden_fields(payload)
        if frozenset(payload) != _TOP_LEVEL_FIELDS:
            missing = sorted(_TOP_LEVEL_FIELDS - frozenset(payload))
            unknown = sorted(frozenset(payload) - _TOP_LEVEL_FIELDS)
            raise ValueError(f"runtime response 字段不匹配；missing={missing}, unknown={unknown}")
        if payload["schema_version"] != RESPONSE_SCHEMA_VERSION:
            raise ValueError("runtime response schema_version 不受支持")
        numeric_payload = payload["numeric_claims"]
        if not isinstance(numeric_payload, list):
            raise ValueError("numeric_claims 必须是 JSON 数组")
        numeric_claims: list[NumericClaim] = []
        for item in numeric_payload:
            if not isinstance(item, dict) or frozenset(item) != _NUMERIC_CLAIM_FIELDS:
                raise ValueError("numeric_claim 必须使用严格字段集合")
            numeric_claims.append(NumericClaim(
                claim=item["claim"],
                value=item["value"],
                unit=item["unit"],
                source_reference=item["source_reference"],
            ))
        numeric_claims.sort(key=lambda claim: (
            claim.claim, claim.value, claim.unit or "", claim.source_reference or ""
        ))
        return NormalizedJiangheDecision(
            family=_enum(StrategyFamily, payload["family"], "family"),
            action=_enum(DecisionAction, payload["action"], "action"),
            direction=_enum(Direction, payload["direction"], "direction"),
            attention_mode=_enum(AttentionMode, payload["attention_mode"], "attention_mode"),
            decision_state=_require_text(payload["decision_state"], "decision_state"),
            rationale=_require_text(payload["rationale"], "rationale"),
            raw_text=raw_response,
            declared_unknown=_strict_string_list(payload["declared_unknown"], "declared_unknown"),
            principle_references=_strict_string_list(
                payload["principle_references"], "principle_references"
            ),
            source_references=_strict_string_list(payload["source_references"], "source_references"),
            numeric_claims=tuple(numeric_claims),
        )


@dataclass(frozen=True)
class RuntimeFidelityEvidence:
    """runtime 可确定抽取的事实；故意不含 violation/no-invention 裁决。"""

    normalized_decision_identity: str
    normalizer_identity: str
    response_schema_identity: str
    evaluation_extractor_identity: str
    family: str
    action: str
    direction: str
    declared_unknown: tuple[str, ...]
    principle_references: tuple[str, ...]
    source_references: tuple[str, ...]
    numeric_claims: tuple[tuple[str, str, str | None, str | None], ...]
    raw_text: str
    evaluator_judgment_required: bool = True


def extract_runtime_fidelity_evidence(
    decision: NormalizedJiangheDecision,
) -> RuntimeFidelityEvidence:
    if not isinstance(decision, NormalizedJiangheDecision):
        raise TypeError("decision 必须是 NormalizedJiangheDecision")
    return RuntimeFidelityEvidence(
        normalized_decision_identity=decision.identity,
        normalizer_identity=decision.normalizer_identity,
        response_schema_identity=decision.response_schema_identity,
        evaluation_extractor_identity=EVALUATION_EXTRACTOR_IDENTITY,
        family=decision.family.value,
        action=decision.action.value,
        direction=decision.direction.value,
        declared_unknown=decision.declared_unknown,
        principle_references=decision.principle_references,
        source_references=decision.source_references,
        numeric_claims=tuple(
            (claim.claim, claim.value, claim.unit, claim.source_reference)
            for claim in decision.numeric_claims
        ),
        raw_text=decision.raw_text,
    )


@dataclass(frozen=True)
class EvaluatorSideJudgment:
    """由 evaluator + fixture 约束产生，绝不从模型 self-report 复制。"""

    normalized_decision_identity: str
    violated_principles: tuple[str, ...]
    invented_thresholds: tuple[str, ...]
    evaluation_extractor_identity: str = EVALUATION_EXTRACTOR_IDENTITY

    def __post_init__(self) -> None:
        _require_text(self.normalized_decision_identity, "normalized_decision_identity")
        if self.evaluation_extractor_identity != EVALUATION_EXTRACTOR_IDENTITY:
            raise ValueError("evaluation_extractor_identity 与当前 evaluator-side extractor 不一致")
        for values, name in (
            (self.violated_principles, "violated_principles"),
            (self.invented_thresholds, "invented_thresholds"),
        ):
            if any(not isinstance(value, str) or not value for value in values):
                raise ValueError(f"{name} 必须去重排序并包含非空字符串")
            if tuple(sorted(set(values))) != values:
                raise ValueError(f"{name} 必须去重排序并包含非空字符串")


def build_neutral_fidelity_adapter_payload(
    runtime_evidence: RuntimeFidelityEvidence,
    evaluator_judgment: EvaluatorSideJudgment,
) -> dict[str, object]:
    """形成 scorer-neutral integration seam；不依赖 DS-owned scorer 类型。"""
    if runtime_evidence.normalized_decision_identity != evaluator_judgment.normalized_decision_identity:
        raise ValueError("evaluator judgment 与 normalized decision identity 不一致")
    return {
        "normalized_decision_identity": runtime_evidence.normalized_decision_identity,
        "family": runtime_evidence.family,
        "action": runtime_evidence.action,
        "direction": runtime_evidence.direction,
        "declared_unknown": list(runtime_evidence.declared_unknown),
        "principle_references": list(runtime_evidence.principle_references),
        "source_references": list(runtime_evidence.source_references),
        "numeric_claims": [list(claim) for claim in runtime_evidence.numeric_claims],
        "violated_principles": list(evaluator_judgment.violated_principles),
        "invented_thresholds": list(evaluator_judgment.invented_thresholds),
        "judgment_source": "EVALUATOR_SIDE_FIXTURE_CONSTRAINTS",
    }


def build_fidelity_response_payload(
    runtime_evidence: RuntimeFidelityEvidence,
    evaluator_judgment: EvaluatorSideJudgment,
) -> dict[str, object]:
    """映射到 integrated fidelity evaluator 的严格 response schema。

    runtime evidence 只贡献模型实际输出；violated/invented 字段只能来自带当前
    extractor identity 的 evaluator-side judgment。
    """
    if runtime_evidence.normalized_decision_identity != evaluator_judgment.normalized_decision_identity:
        raise ValueError("evaluator judgment 与 normalized decision identity 不一致")
    if (
        runtime_evidence.evaluation_extractor_identity
        != evaluator_judgment.evaluation_extractor_identity
    ):
        raise ValueError("runtime evidence 与 evaluator judgment 的 extractor identity 不一致")
    return {
        "family": None if runtime_evidence.family == "NONE" else runtime_evidence.family,
        "action": runtime_evidence.action,
        "direction": None if runtime_evidence.direction == "NONE" else runtime_evidence.direction,
        "acknowledged_principles": list(runtime_evidence.principle_references),
        "violated_principles": list(evaluator_judgment.violated_principles),
        "declared_unknown": list(runtime_evidence.declared_unknown),
        "invented_thresholds": list(evaluator_judgment.invented_thresholds),
        "outcome_reference": False,
        "raw_text": runtime_evidence.raw_text,
    }


__all__ = [
    "EVALUATION_EXTRACTOR_IDENTITY",
    "EVALUATION_EXTRACTOR_VERSION",
    "EvaluatorSideJudgment",
    "JiangheResponseNormalizer",
    "NORMALIZER_IDENTITY",
    "NORMALIZER_VERSION",
    "NormalizedJiangheDecision",
    "NumericClaim",
    "RESPONSE_SCHEMA_IDENTITY",
    "RESPONSE_SCHEMA_VERSION",
    "RuntimeFidelityEvidence",
    "build_neutral_fidelity_adapter_payload",
    "build_fidelity_response_payload",
    "extract_runtime_fidelity_evidence",
]

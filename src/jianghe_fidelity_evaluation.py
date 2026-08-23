"""江河 AI 忠实度评估 harness（provider-neutral，完全离线，fail-closed）。

本模块只负责把未来真实模型产生的规范化 response records 送进现有
`src/jianghe_fidelity_scoring`，并生成确定性的 evaluation report。

证据链完整性要求（pre-live gate audit repair，见
`docs/reviews/JIANGHE_PRE_LIVE_FIDELITY_GATE_AUDIT_V0_1.md`）：

- 任何 outcome contamination（response.outcome_reference=True / raw_text 命中 /
  metadata 命中）都强制 evaluation 进入 PROCESSING_STATUS=ERROR 与
  EVIDENCE_ELIGIBILITY=INELIGIBLE，绝不评分；禁止“violation 存在但 status=OK”。
- 严格 canonical response schema：未知字段直接 ERROR，不静默忽略。
- 每条 record.corpus_id 必须严格等于被评估 corpus 的 corpus_id；不匹配 ERROR 且不评分。
- call_success 必须是真正 bool；False 时 NON_SCOREABLE，不进入 evaluate_fixture。
- 禁止宽松 coercion（bool("false") / str(任意对象) / int(坏延迟) 等）。
- typed input provenance（provider-neutral）：按 track 严格要求所需 identity，
  视觉/结构化/双输入/运行提供者各自绑定证据；不复制第二套 provider 实现。
- metadata 严格 JSON-safe + allowlist + 递归 contamination scan，不开放任意隐藏数据通道。
- 确定性 report_identity（canonical 序列化后 SHA-256，自身从 hash input 排除）。
- 三态分离：processing_status / evidence_completeness / evidence_eligibility。
  不建立模型通过率门槛，不自动 ADOPT。

禁止：
- 调用任何真实模型 API / 网络请求
- 访问 P&L、outcome、future price
- 排名模型或设置 acceptance threshold
- 自动补数据
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping

from src.jianghe_fidelity_scoring import (
    CORPUS_ID,
    CORPUS_PATH,
    OUTCOME_CONTAMINATION_PATTERNS,
    FidelityResponse,
    evaluate_fixture,
    load_corpus,
    validate_corpus,
)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

ALLOWED_TRACKS = (
    "SEMANTIC",
    "VISUAL",
    "STRUCTURED",
    "DUAL_INPUT",
    "OPERATIONAL_PROVIDER",
)

_ALLOWED_TRACK_SET = frozenset(ALLOWED_TRACKS)

# canonical response 字段 allowlist：任何其它字段都视为未知并 ERROR。
_CANONICAL_RESPONSE_FIELDS = frozenset({
    "family",
    "action",
    "direction",
    "acknowledged_principles",
    "violated_principles",
    "declared_unknown",
    "invented_thresholds",
    "outcome_reference",
    "raw_text",
})

# 三态值域
PROCESSING_OK = "OK"
PROCESSING_ERROR = "ERROR"
COMPLETENESS_COMPLETE = "COMPLETE"
COMPLETENESS_INCOMPLETE = "INCOMPLETE"
ELIGIBILITY_ELIGIBLE = "ELIGIBLE"
ELIGIBILITY_INELIGIBLE = "INELIGIBLE"

# artifact identity 必须是 lowercase 64 位 sha256 hex
_SHA256_HEX_RE = re.compile(r"^[0-9a-f]{64}$")

# typed input provenance 字段（provider-neutral；Codex provider 实现在另一并行 branch）
_INPUT_EVIDENCE_FIELDS = frozenset({
    "observation_identity",
    "visual_observation_identity",
    "structured_observation_identity",
    "visual_artifact_identity",
    "renderer_config_identity",
    "structured_input_identity",
    "provider_invocation_identity",
    "provider_response_identity",
    "normalizer_identity",
    "evaluation_extractor_identity",
    "prompt_package_identity",
    "model_provider_identity",
})

# 每个 track 严格要求的最小 identity 集合
TRACK_REQUIRED_EVIDENCE: dict[str, frozenset[str]] = {
    "SEMANTIC": frozenset({
        "prompt_package_identity",
        "evaluation_extractor_identity",
    }),
    "VISUAL": frozenset({
        "visual_artifact_identity",
        "renderer_config_identity",
    }),
    "STRUCTURED": frozenset({
        "structured_input_identity",
        "observation_identity",
    }),
    "DUAL_INPUT": frozenset({
        "visual_artifact_identity",
        "renderer_config_identity",
        "structured_input_identity",
        "observation_identity",
    }),
    "OPERATIONAL_PROVIDER": frozenset({
        "provider_invocation_identity",
        "provider_response_identity",
        "model_provider_identity",
    }),
}

# metadata allowlist：重要 provenance 一律走 typed fields，这里只允许极少数
# 非证据的运维标签，且值必须是 JSON-safe scalar。
_ALLOWED_METADATA_KEYS = frozenset({
    "probe_session_id",
    "engine_version",
})

_JSON_SCALAR_TYPES = (str, int, float, bool, type(None))


# ---------------------------------------------------------------------------
# 数据类型
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class InputEvidence:
    """provider-neutral 的 typed input provenance。

    所有 identity 字段（非 None 时）必须是 lowercase 64 位 sha256 hex。
    根据 track 严格要求部分字段；具体见 ``TRACK_REQUIRED_EVIDENCE``。
    """

    observation_identity: str | None = None
    visual_observation_identity: str | None = None
    structured_observation_identity: str | None = None
    visual_artifact_identity: str | None = None
    renderer_config_identity: str | None = None
    structured_input_identity: str | None = None
    provider_invocation_identity: str | None = None
    provider_response_identity: str | None = None
    normalizer_identity: str | None = None
    evaluation_extractor_identity: str | None = None
    prompt_package_identity: str | None = None
    model_provider_identity: str | None = None

    def present_identities(self) -> frozenset[str]:
        return frozenset(
            name
            for name in _INPUT_EVIDENCE_FIELDS
            if getattr(self, name) is not None
        )


@dataclass(frozen=True)
class EvaluationRecord:
    """一条规范化后的模型响应记录。

    不含任何 outcome、future price、PnL 字段。provenance 走 typed
    ``input_evidence``，不再接受 arbitrary string reference 冒充证据。
    """

    record_id: str
    candidate_label: str
    corpus_id: str
    fixture_id: str
    track: str
    response: FidelityResponse
    call_success: bool = True
    latency_ms: int | None = None
    input_evidence: InputEvidence | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class ScoreDetail:
    """单个 fixture × track 的评分明细（仅限被 admit 的 record）。"""

    fixture_id: str
    track: str
    record_id: str
    verdict: str
    satisfied_paths: tuple[str, ...]
    triggered_failures: tuple[str, ...]
    reasons: tuple[str, ...]
    invented_thresholds: tuple[str, ...]
    declared_unknown: tuple[str, ...]
    outcome_reference: bool


# ---------------------------------------------------------------------------
# 记录解析（严格类型，禁止 coercion）
# ---------------------------------------------------------------------------


def _require_non_empty_str(value: Any, field_name: str) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} 必须是字符串，得到 {type(value).__name__}")
    if not value.strip():
        raise ValueError(f"{field_name} 不能为空字符串")
    return value


def _to_string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    """把 JSON 中的列表/null 转换为字符串元组；元素必须是 str，禁止 coercion。"""
    if value is None:
        return ()
    if isinstance(value, list):
        for item in value:
            if not isinstance(item, str):
                raise ValueError(
                    f"{field_name} 的元素必须是字符串，得到 {type(item).__name__}"
                )
        return tuple(value)
    raise ValueError(f"{field_name} 必须是列表或 null，得到 {type(value).__name__}")


def _strict_latency(value: Any) -> int | None:
    """latency_ms：必须是整数 >= 0 或 null；禁止 bool/float/负数。"""
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"latency_ms 必须是整数 >= 0 或 null，得到 {type(value).__name__}"
        )
    if value < 0:
        raise ValueError(f"latency_ms 不能为负数: {value}")
    return value


def parse_input_evidence(raw: Any) -> InputEvidence:
    """解析 typed input provenance；未知字段或非法 identity 直接 ValueError。"""
    if raw is None:
        return InputEvidence()
    if not isinstance(raw, Mapping):
        raise ValueError("input_evidence 必须是对象或 null")

    unknown = set(raw) - _INPUT_EVIDENCE_FIELDS
    if unknown:
        raise ValueError(f"input_evidence 包含未知字段: {sorted(unknown)}")

    kwargs: dict[str, str | None] = {}
    for name in sorted(_INPUT_EVIDENCE_FIELDS):
        value = raw.get(name)
        if value is None:
            kwargs[name] = None
            continue
        if not isinstance(value, str) or not _SHA256_HEX_RE.match(value):
            raise ValueError(
                f"input_evidence.{name} 必须是 lowercase 64 位 sha256 hex"
            )
        kwargs[name] = value
    return InputEvidence(**kwargs)


def parse_metadata(raw: Any) -> Mapping[str, Any] | None:
    """metadata：可选；必须 JSON-safe + allowlist + 仅 scalar 值。"""
    if raw is None:
        return None
    if not isinstance(raw, Mapping):
        raise ValueError("metadata 必须是对象或 null")

    unknown = set(raw) - _ALLOWED_METADATA_KEYS
    if unknown:
        raise ValueError(f"metadata 包含未授权字段: {sorted(unknown)}")

    for key, value in raw.items():
        if not isinstance(key, str):
            raise ValueError(f"metadata 键必须是字符串，得到 {type(key).__name__}")
        if not isinstance(value, _JSON_SCALAR_TYPES):
            raise ValueError(
                f"metadata.{key} 的值必须是 JSON-safe scalar，得到 {type(value).__name__}"
            )
    return dict(raw)


def parse_fidelity_response(payload: Mapping[str, Any]) -> FidelityResponse:
    """严格解析 canonical response；未知字段直接 ERROR，不静默忽略。

    所有非 null 字段必须是精确类型；列表元素必须是 str（禁止 coercion）。
    """
    if not isinstance(payload, Mapping):
        raise ValueError("response 必须是 JSON 对象")

    unknown = set(payload) - _CANONICAL_RESPONSE_FIELDS
    if unknown:
        raise ValueError(f"response 包含未知字段: {sorted(unknown)}")

    family = payload.get("family")
    action = payload.get("action")
    direction = payload.get("direction")

    # 显式拒绝 null 以外的非字符串值，避免隐式转换导致意外。
    for name, value in (("family", family), ("action", action), ("direction", direction)):
        if value is not None and not isinstance(value, str):
            raise ValueError(f"{name} 必须是字符串或 null")

    raw_text = payload.get("raw_text")
    if raw_text is not None and not isinstance(raw_text, str):
        raise ValueError("raw_text 必须是字符串或 null")

    outcome_reference = payload.get("outcome_reference", False)
    if not isinstance(outcome_reference, bool):
        raise ValueError("outcome_reference 必须是布尔值")

    return FidelityResponse(
        family=family,
        action=action,
        direction=direction,
        acknowledged_principles=_to_string_tuple(
            payload.get("acknowledged_principles", []), "acknowledged_principles"
        ),
        violated_principles=_to_string_tuple(
            payload.get("violated_principles", []), "violated_principles"
        ),
        declared_unknown=_to_string_tuple(
            payload.get("declared_unknown", []), "declared_unknown"
        ),
        invented_thresholds=_to_string_tuple(
            payload.get("invented_thresholds", []), "invented_thresholds"
        ),
        outcome_reference=outcome_reference,
        raw_text=raw_text,
    )


def parse_record(raw: Mapping[str, Any]) -> EvaluationRecord:
    """严格解析单条记录；非法 track / 缺失字段 / 宽松值都会 ValueError。

    类型要求（禁止 coercion）：
    - record_id / candidate_label / corpus_id / fixture_id: 非空 str
    - track: 精确枚举 str
    - call_success: 真正 bool（缺省 True）
    - latency_ms: 整数 >= 0 或 null
    - response: 严格 canonical schema
    - input_evidence: typed InputEvidence
    - metadata: JSON-safe + allowlist
    """
    if not isinstance(raw, Mapping):
        raise ValueError("record 必须是 JSON 对象")

    required = ("record_id", "candidate_label", "corpus_id", "fixture_id", "track", "response")
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"缺少必填字段: {', '.join(missing)}")

    track = _require_non_empty_str(raw["track"], "track")
    if track not in _ALLOWED_TRACK_SET:
        raise ValueError(f"非法 track: {track!r}，允许 {ALLOWED_TRACKS}")

    call_success = raw.get("call_success", True)
    if not isinstance(call_success, bool):
        raise ValueError("call_success 必须是真正布尔值")

    return EvaluationRecord(
        record_id=_require_non_empty_str(raw["record_id"], "record_id"),
        candidate_label=_require_non_empty_str(raw["candidate_label"], "candidate_label"),
        corpus_id=_require_non_empty_str(raw["corpus_id"], "corpus_id"),
        fixture_id=_require_non_empty_str(raw["fixture_id"], "fixture_id"),
        track=track,
        response=parse_fidelity_response(raw["response"]),
        call_success=call_success,
        latency_ms=_strict_latency(raw.get("latency_ms")),
        input_evidence=parse_input_evidence(raw.get("input_evidence")),
        metadata=parse_metadata(raw.get("metadata")),
    )


def load_response_records(path: Path) -> list[dict[str, Any]]:
    """读取 JSON 或 JSONL 响应记录文件（容忍可选 UTF-8 BOM）。"""
    text = path.read_text(encoding="utf-8-sig")
    if not text.strip():
        return []

    # 先尝试作为整体 JSON（数组或单个对象）。
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        parsed = None

    if parsed is not None:
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            return [parsed]
        raise ValueError(f"记录文件顶层必须是对象或数组，得到 {type(parsed).__name__}")

    # 否则按 JSONL 解析。
    records: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"第 {line_no} 行 JSONL 解析失败: {exc}") from exc
    return records


# ---------------------------------------------------------------------------
# 证据扫描
# ---------------------------------------------------------------------------


def _scan_text_for_outcome_contamination(text: str) -> list[tuple[str, str]]:
    """对文本复用 scorer 的污染模式扫描，返回命中的 (label, pattern)。"""
    if not text:
        return []
    hits: list[tuple[str, str]] = []
    lowered = text.lower()
    for label, pattern in OUTCOME_CONTAMINATION_PATTERNS:
        if re.search(pattern, lowered):
            hits.append((label, pattern))
    return hits


def _scan_raw_text_for_outcome_contamination(
    raw_text: str | None,
) -> list[tuple[str, str]]:
    return _scan_text_for_outcome_contamination(raw_text or "")


def _scan_metadata_for_outcome_contamination(
    metadata: Mapping[str, Any] | None,
) -> list[tuple[str, str]]:
    """递归扫描 metadata 全部 scalar 值；命中任意污染词即返回 hits。"""
    if not metadata:
        return []
    hits: list[tuple[str, str]] = []
    for key, value in metadata.items():
        if isinstance(value, bool):
            text = "true" if value else "false"
        elif value is None:
            text = ""
        else:
            text = str(value)
        for label, pattern in _scan_text_for_outcome_contamination(text):
            hits.append((label, pattern))
    return hits


def _track_evidence_requirements(evidence: InputEvidence, track: str) -> list[str]:
    """返回 track 缺失的必要 identity 字段名（满足即空列表）。"""
    required = TRACK_REQUIRED_EVIDENCE[track]
    present = evidence.present_identities()
    return sorted(required - present)


def _dual_observation_consistency(evidence: InputEvidence) -> str | None:
    """DUAL_INPUT 的 observation 一致性：所有提供的 observation 引用必须相同。

    返回不一致描述；None 表示一致（或没有冲突的引用）。
    """
    refs = {
        value
        for value in (
            evidence.observation_identity,
            evidence.visual_observation_identity,
            evidence.structured_observation_identity,
        )
        if value is not None
    }
    if len(refs) > 1:
        return f"observation 引用不一致: {sorted(refs)}"
    return None


# ---------------------------------------------------------------------------
# 报告构造
# ---------------------------------------------------------------------------


def _input_evidence_to_dict(evidence: InputEvidence | None) -> dict[str, str | None]:
    if evidence is None:
        return {}
    return {
        name: getattr(evidence, name)
        for name in sorted(_INPUT_EVIDENCE_FIELDS)
        if getattr(evidence, name) is not None
    }


def _response_to_dict(response: FidelityResponse) -> dict[str, Any]:
    return {
        "family": response.family,
        "action": response.action,
        "direction": response.direction,
        "acknowledged_principles": list(response.acknowledged_principles),
        "violated_principles": list(response.violated_principles),
        "declared_unknown": list(response.declared_unknown),
        "invented_thresholds": list(response.invented_thresholds),
        "outcome_reference": response.outcome_reference,
        "raw_text": response.raw_text,
    }


def _latency_summary(latencies: list[int]) -> dict[str, Any]:
    if not latencies:
        return {"count": 0}
    total = sum(latencies)
    return {
        "count": len(latencies),
        "min_ms": min(latencies),
        "max_ms": max(latencies),
        "mean_ms": round(total / len(latencies), 6),
    }


def _score_detail_to_dict(detail: ScoreDetail) -> dict[str, Any]:
    return {
        "fixture_id": detail.fixture_id,
        "track": detail.track,
        "record_id": detail.record_id,
        "verdict": detail.verdict,
        "satisfied_paths": list(detail.satisfied_paths),
        "triggered_failures": list(detail.triggered_failures),
        "reasons": list(detail.reasons),
        "invented_thresholds": list(detail.invented_thresholds),
        "declared_unknown": list(detail.declared_unknown),
        "outcome_reference": detail.outcome_reference,
    }


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _compute_report_identity(report_without_identity: Mapping[str, Any]) -> str:
    """对排除 report_identity 字段后的报告做 canonical 序列化后 SHA-256。"""
    return hashlib.sha256(
        _canonical_json(report_without_identity).encode("utf-8")
    ).hexdigest()


def _finalize_report(report: dict[str, Any]) -> dict[str, Any]:
    """在报告上追加确定性 report_identity（自身从 hash input 排除）。"""
    report["report_identity"] = _compute_report_identity(report)
    return report


def _empty_track_counts() -> dict[str, int]:
    return {"PASS": 0, "FAIL": 0, "MISSING": 0, "ERROR": 0, "INELIGIBLE": 0}


def _error_report(errors: list[str]) -> dict[str, Any]:
    """corpus 校验失败等早期错误返回的失败报告。"""
    report: dict[str, Any] = {
        "candidate_label": None,
        "corpus_id": None,
        "corpus_identity": None,
        "fixture_total": 0,
        "response_total": 0,
        "admitted_record_total": 0,
        "non_scoreable_record_total": 0,
        "track_coverage_counts": {track: 0 for track in ALLOWED_TRACKS},
        "per_track_fixture_counts": {
            track: _empty_track_counts() for track in ALLOWED_TRACKS
        },
        "per_fixture_scores": [],
        "admitted_records": [],
        "missing_response_records": [],
        "incomplete_tracks": [],
        "duplicate_records": [],
        "invalid_track_records": [],
        "unknown_fixture_records": [],
        "malformed_response_records": [],
        "corpus_mismatch_records": [],
        "failed_call_records": [],
        "provenance_ineligible_records": [],
        "metadata_violations": [],
        "outcome_contamination_violations": [],
        "invented_threshold_flags": [],
        "unknown_declaration_evidence": [],
        "latency_observations_ms": {"count": 0},
        "errors": errors,
        "processing_status": PROCESSING_ERROR,
        "evidence_completeness": COMPLETENESS_INCOMPLETE,
        "evidence_eligibility": ELIGIBILITY_INELIGIBLE,
        "status": PROCESSING_ERROR,
    }
    return _finalize_report(report)


def evaluate_response_records(
    corpus: Mapping[str, Any],
    raw_records: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """把原始响应记录集评估为确定性报告（fail-closed）。

    过程：
    1. 校验 corpus（失败则报告 ERROR / INCOMPLETE / INELIGIBLE）。
    2. 逐条严格解析；任何畸形 / 未知 response 字段 / 非法 track / 未知
       fixture / 重复 / corpus 不匹配 / call_success=False / 证据不完整 /
       metadata 违规 / outcome contamination 都会使该 record 不被 admit，
       并进入对应拒绝清单（不评分）。
    3. 仅对被 admit 的 record 用现有 ``evaluate_fixture`` 评分。
    4. 汇总 processing_status / evidence_completeness / evidence_eligibility
       与确定性 report_identity。
    """
    errors: list[str] = []

    corpus_errors = validate_corpus(corpus)
    if corpus_errors:
        errors.extend(corpus_errors)
        return _error_report(errors)

    corpus_id = corpus.get("corpus_id", CORPUS_ID)
    fixtures = corpus["fixtures"]
    fixture_total = len(fixtures)
    fixture_ids = {fixture["fixture_id"] for fixture in fixtures}

    # 逐条解析
    admitted_records: list[EvaluationRecord] = []
    invalid_track_records: list[str] = []
    malformed_records: list[str] = []
    unknown_fixture_records: list[str] = []
    duplicate_record_ids: list[str] = []
    corpus_mismatch_records: list[str] = []
    failed_call_records: list[dict[str, Any]] = []
    provenance_ineligible_records: list[dict[str, Any]] = []
    metadata_violations: list[dict[str, Any]] = []
    outcome_violations: list[dict[str, Any]] = []
    invented_flags: list[dict[str, Any]] = []
    unknown_declarations: list[dict[str, Any]] = []
    latencies: list[int] = []

    seen_keys: set[tuple[str, str, str]] = set()
    candidate_label: str | None = None

    for index, raw in enumerate(raw_records, start=1):
        try:
            record_id = _require_non_empty_str(
                raw.get("record_id", f"<index:{index}>"), "record_id"
            )
        except ValueError:
            record_id = f"<index:{index}>"
        try:
            record = parse_record(raw)
        except ValueError as exc:
            # 无法解析时尽量区分是非法 track 还是 response/record 格式错误。
            if "非法 track" in str(exc):
                invalid_track_records.append(record_id)
            else:
                malformed_records.append(record_id)
            errors.append(f"记录 {record_id} 解析失败: {exc}")
            continue

        if record.fixture_id not in fixture_ids:
            unknown_fixture_records.append(record.record_id)
            errors.append(
                f"记录 {record.record_id} 引用未知 fixture_id: {record.fixture_id!r}"
            )
            continue

        key = (record.candidate_label, record.fixture_id, record.track)
        if key in seen_keys:
            duplicate_record_ids.append(record.record_id)
            errors.append(
                f"重复记录 candidate={record.candidate_label!r} fixture={record.fixture_id!r} "
                f"track={record.track!r} (record_id={record.record_id})"
            )
            continue
        seen_keys.add(key)

        if candidate_label is None:
            candidate_label = record.candidate_label
        elif record.candidate_label != candidate_label:
            errors.append(
                f"记录 {record.record_id} 的 candidate_label {record.candidate_label!r} "
                f"与首条记录 {candidate_label!r} 不一致"
            )
            continue

        # 强 corpus 绑定：每条 record.corpus_id 必须严格等于当前 corpus_id。
        if record.corpus_id != corpus_id:
            corpus_mismatch_records.append(record.record_id)
            errors.append(
                f"记录 {record.record_id} 的 corpus_id {record.corpus_id!r} "
                f"与当前 corpus_id {corpus_id!r} 不匹配"
            )
            continue

        # call_success=False：NON_SCOREABLE，不进入评分。
        if not record.call_success:
            failed_call_records.append({
                "record_id": record.record_id,
                "fixture_id": record.fixture_id,
                "track": record.track,
            })
            errors.append(
                f"记录 {record.record_id} call_success=False，不可评分"
            )
            continue

        # typed input provenance：按 track 严格要求。
        evidence = record.input_evidence or InputEvidence()
        missing_evidence = _track_evidence_requirements(evidence, record.track)
        if missing_evidence:
            provenance_ineligible_records.append({
                "record_id": record.record_id,
                "fixture_id": record.fixture_id,
                "track": record.track,
                "missing_identities": missing_evidence,
            })
            errors.append(
                f"记录 {record.record_id} track={record.track} 缺少必要 provenance: "
                f"{missing_evidence}"
            )
            continue

        if record.track == "DUAL_INPUT":
            inconsistency = _dual_observation_consistency(evidence)
            if inconsistency is not None:
                provenance_ineligible_records.append({
                    "record_id": record.record_id,
                    "fixture_id": record.fixture_id,
                    "track": record.track,
                    "missing_identities": [],
                    "inconsistency": inconsistency,
                })
                errors.append(
                    f"记录 {record.record_id} DUAL_INPUT {inconsistency}"
                )
                continue

        # metadata：JSON-safe + allowlist 已在 parse 阶段校验；这里做污染扫描。
        metadata_hits = _scan_metadata_for_outcome_contamination(record.metadata)
        if metadata_hits:
            metadata_violations.append({
                "record_id": record.record_id,
                "fixture_id": record.fixture_id,
                "track": record.track,
                "hits": [label for label, _pattern in metadata_hits],
            })
            for label, _pattern in metadata_hits:
                outcome_violations.append({
                    "record_id": record.record_id,
                    "fixture_id": record.fixture_id,
                    "track": record.track,
                    "source": "metadata",
                    "matched_label": label,
                })
            errors.append(
                f"记录 {record.record_id} metadata 含 outcome contamination: "
                f"{[label for label, _p in metadata_hits]}"
            )
            continue

        # outcome contamination：任何命中都 fail-closed（不评分）。
        if record.response.outcome_reference:
            outcome_violations.append({
                "record_id": record.record_id,
                "fixture_id": record.fixture_id,
                "track": record.track,
                "source": "outcome_reference_flag",
            })
            errors.append(
                f"记录 {record.record_id} outcome_reference=True，拒绝评分"
            )
            continue

        raw_text_hits = _scan_raw_text_for_outcome_contamination(record.response.raw_text)
        if raw_text_hits:
            for matched_label, _pattern in raw_text_hits:
                outcome_violations.append({
                    "record_id": record.record_id,
                    "fixture_id": record.fixture_id,
                    "track": record.track,
                    "source": "raw_text",
                    "matched_label": matched_label,
                })
            errors.append(
                f"记录 {record.record_id} raw_text 含 outcome contamination，拒绝评分"
            )
            continue

        # 其余字段的 evidence flag 收集（仅在 admit 时）。
        admitted_records.append(record)

        if record.latency_ms is not None and record.call_success:
            latencies.append(record.latency_ms)

        if record.response.invented_thresholds:
            invented_flags.append({
                "record_id": record.record_id,
                "fixture_id": record.fixture_id,
                "track": record.track,
                "invented_thresholds": list(record.response.invented_thresholds),
            })

        if record.response.declared_unknown:
            unknown_declarations.append({
                "record_id": record.record_id,
                "fixture_id": record.fixture_id,
                "track": record.track,
                "declared_unknown": list(record.response.declared_unknown),
            })

    # 评分与汇总（只对被 admit 的 record）
    record_map = {(record.fixture_id, record.track): record for record in admitted_records}

    track_coverage_counts = {track: 0 for track in ALLOWED_TRACKS}
    per_track_counts = {track: _empty_track_counts() for track in ALLOWED_TRACKS}
    score_details: list[ScoreDetail] = []
    missing_records: list[str] = []
    incomplete_tracks: list[dict[str, Any]] = []

    for fixture in fixtures:
        fixture_id = fixture["fixture_id"]
        present_tracks: set[str] = set()
        has_any_record = False

        for track in ALLOWED_TRACKS:
            record = record_map.get((fixture_id, track))
            if record is None:
                per_track_counts[track]["MISSING"] += 1
                continue

            present_tracks.add(track)
            track_coverage_counts[track] += 1
            has_any_record = True

            try:
                score = evaluate_fixture(fixture, record.response)
            except Exception as exc:  # pragma: no cover - scoring should not raise, but fail-closed
                per_track_counts[track]["ERROR"] += 1
                errors.append(f"fixture {fixture_id}/{track} 评分异常: {exc}")
                detail = ScoreDetail(
                    fixture_id=fixture_id,
                    track=track,
                    record_id=record.record_id,
                    verdict="ERROR",
                    satisfied_paths=(),
                    triggered_failures=(),
                    reasons=(f"评分异常: {exc}",),
                    invented_thresholds=tuple(record.response.invented_thresholds),
                    declared_unknown=tuple(record.response.declared_unknown),
                    outcome_reference=record.response.outcome_reference,
                )
            else:
                per_track_counts[track]["PASS" if score.passed else "FAIL"] += 1
                detail = ScoreDetail(
                    fixture_id=fixture_id,
                    track=track,
                    record_id=record.record_id,
                    verdict=score.verdict,
                    satisfied_paths=score.satisfied_paths,
                    triggered_failures=score.triggered_failures,
                    reasons=score.reasons,
                    invented_thresholds=tuple(record.response.invented_thresholds),
                    declared_unknown=tuple(record.response.declared_unknown),
                    outcome_reference=record.response.outcome_reference,
                )
            score_details.append(detail)

        if not has_any_record:
            missing_records.append(fixture_id)

        missing_track_set = set(ALLOWED_TRACKS) - present_tracks
        if missing_track_set:
            incomplete_tracks.append({
                "fixture_id": fixture_id,
                "missing_tracks": tuple(sorted(missing_track_set)),
            })

    non_scoreable_total = (
        len(invalid_track_records)
        + len(malformed_records)
        + len(unknown_fixture_records)
        + len(duplicate_record_ids)
        + len(corpus_mismatch_records)
        + len(failed_call_records)
        + len(provenance_ineligible_records)
        + len(metadata_violations)
        + len(outcome_violations)
    )

    processing_status = PROCESSING_ERROR if errors else PROCESSING_OK
    evidence_completeness = (
        COMPLETENESS_COMPLETE
        if not incomplete_tracks and not missing_records
        else COMPLETENESS_INCOMPLETE
    )
    evidence_eligibility = (
        ELIGIBILITY_ELIGIBLE if non_scoreable_total == 0 else ELIGIBILITY_INELIGIBLE
    )

    report: dict[str, Any] = {
        "candidate_label": candidate_label,
        "corpus_id": corpus_id,
        "corpus_identity": {
            "knowledge_pack_reference": corpus.get("knowledge_pack_reference"),
            "knowledge_pack_identity": corpus.get("knowledge_pack_identity"),
            "baseline_commit": corpus.get("baseline_commit"),
            "version": corpus.get("version"),
        },
        "fixture_total": fixture_total,
        "response_total": len(admitted_records),
        "admitted_record_total": len(admitted_records),
        "non_scoreable_record_total": non_scoreable_total,
        "track_coverage_counts": track_coverage_counts,
        "per_track_fixture_counts": per_track_counts,
        "per_fixture_scores": [_score_detail_to_dict(d) for d in score_details],
        "admitted_records": [
            {
                "record_id": record.record_id,
                "candidate_label": record.candidate_label,
                "corpus_id": record.corpus_id,
                "fixture_id": record.fixture_id,
                "track": record.track,
                "call_success": record.call_success,
                "latency_ms": record.latency_ms,
                "input_evidence": _input_evidence_to_dict(record.input_evidence),
                "response": _response_to_dict(record.response),
            }
            for record in admitted_records
        ],
        "missing_response_records": missing_records,
        "incomplete_tracks": incomplete_tracks,
        "duplicate_records": sorted(set(duplicate_record_ids)),
        "invalid_track_records": sorted(set(invalid_track_records)),
        "unknown_fixture_records": sorted(set(unknown_fixture_records)),
        "malformed_response_records": sorted(set(malformed_records)),
        "corpus_mismatch_records": sorted(set(corpus_mismatch_records)),
        "failed_call_records": failed_call_records,
        "provenance_ineligible_records": provenance_ineligible_records,
        "metadata_violations": metadata_violations,
        "outcome_contamination_violations": outcome_violations,
        "invented_threshold_flags": invented_flags,
        "unknown_declaration_evidence": unknown_declarations,
        "latency_observations_ms": _latency_summary(latencies),
        "errors": errors,
        "processing_status": processing_status,
        "evidence_completeness": evidence_completeness,
        "evidence_eligibility": evidence_eligibility,
        "status": processing_status,
    }
    return _finalize_report(report)


def render_report(report: Mapping[str, Any]) -> str:
    """把报告序列化为确定性 JSON 字符串（排序键、保持列表顺序）。"""
    return json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

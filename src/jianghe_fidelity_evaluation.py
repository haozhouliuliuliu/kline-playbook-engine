"""江河 AI 忠实度评估 harness（provider-neutral，完全离线）。

本模块只负责把未来真实模型产生的规范化 response records 送进现有
`src/jianghe_fidelity_scoring`，并生成确定性的 evaluation report。

禁止：
- 调用任何真实模型 API / 网络请求
- 访问 P&L、outcome、future price
- 排名模型或设置 acceptance threshold
- 自动补数据
"""

from __future__ import annotations

from dataclasses import dataclass
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


# ---------------------------------------------------------------------------
# 数据类型
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EvaluationRecord:
    """一条规范化后的模型响应记录。

    不含任何 outcome、future price、PnL 字段。
    """

    record_id: str
    candidate_label: str
    corpus_id: str
    fixture_id: str
    track: str
    response: FidelityResponse
    latency_ms: int | None = None
    call_success: bool = True
    input_artifact_reference: str | None = None
    metadata: Mapping[str, Any] | None = None


@dataclass(frozen=True)
class ScoreDetail:
    """单个 fixture × track 的评分明细。"""

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
# 记录解析
# ---------------------------------------------------------------------------


def _to_string_tuple(value: Any, field_name: str) -> tuple[str, ...]:
    """把 JSON 中的列表/null 转换为字符串元组。"""
    if value is None:
        return ()
    if isinstance(value, list):
        return tuple(str(item) for item in value)
    raise ValueError(f"{field_name} 必须是列表或 null，得到 {type(value).__name__}")


def parse_fidelity_response(payload: Mapping[str, Any]) -> FidelityResponse:
    """把 JSON 中的 response 对象解析为 ``FidelityResponse``。

    未知字段会被忽略，但类型错误会抛出 ``ValueError``。
    """
    if not isinstance(payload, Mapping):
        raise ValueError("response 必须是 JSON 对象")

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
            payload.get("acknowledged_principles", ()), "acknowledged_principles"
        ),
        violated_principles=_to_string_tuple(
            payload.get("violated_principles", ()), "violated_principles"
        ),
        declared_unknown=_to_string_tuple(
            payload.get("declared_unknown", ()), "declared_unknown"
        ),
        invented_thresholds=_to_string_tuple(
            payload.get("invented_thresholds", ()), "invented_thresholds"
        ),
        outcome_reference=outcome_reference,
        raw_text=raw_text,
    )


def parse_record(raw: Mapping[str, Any]) -> EvaluationRecord:
    """解析单条记录；非法 track 或字段缺失会抛出 ``ValueError``。"""
    required = ("record_id", "candidate_label", "corpus_id", "fixture_id", "track", "response")
    missing = [key for key in required if key not in raw]
    if missing:
        raise ValueError(f"缺少必填字段: {', '.join(missing)}")

    track = raw["track"]
    if track not in ALLOWED_TRACKS:
        raise ValueError(f"非法 track: {track!r}，允许 {ALLOWED_TRACKS}")

    latency_ms = raw.get("latency_ms")
    if latency_ms is not None:
        if isinstance(latency_ms, bool) or not isinstance(latency_ms, (int, float)):
            raise ValueError("latency_ms 必须是数字或 null")
        latency_ms = int(latency_ms)

    metadata = raw.get("metadata")
    if metadata is not None and not isinstance(metadata, Mapping):
        raise ValueError("metadata 必须是对象或 null")

    return EvaluationRecord(
        record_id=str(raw["record_id"]),
        candidate_label=str(raw["candidate_label"]),
        corpus_id=str(raw["corpus_id"]),
        fixture_id=str(raw["fixture_id"]),
        track=track,
        response=parse_fidelity_response(raw["response"]),
        latency_ms=latency_ms,
        call_success=bool(raw.get("call_success", True)),
        input_artifact_reference=raw.get("input_artifact_reference"),
        metadata=metadata,
    )


def load_response_records(path: Path) -> list[dict[str, Any]]:
    """读取 JSON 或 JSONL 响应记录文件。"""
    text = path.read_text(encoding="utf-8")
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
# 报告构造
# ---------------------------------------------------------------------------


def _scan_raw_text_for_outcome_contamination(raw_text: str | None) -> list[tuple[str, str]]:
    """对 raw_text 复用 scorer 的污染模式扫描，返回命中的 (label, pattern)。"""
    if not raw_text:
        return []
    hits: list[tuple[str, str]] = []
    lowered = raw_text.lower()
    for label, pattern in OUTCOME_CONTAMINATION_PATTERNS:
        if re.search(pattern, lowered):
            hits.append((label, pattern))
    return hits


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


def _error_report(errors: list[str]) -> dict[str, Any]:
    """corpus 校验失败等早期错误返回的失败报告。"""
    return {
        "candidate_label": None,
        "corpus_id": None,
        "corpus_identity": None,
        "fixture_total": 0,
        "response_total": 0,
        "track_coverage_counts": {track: 0 for track in ALLOWED_TRACKS},
        "per_track_fixture_counts": {
            track: {"PASS": 0, "FAIL": 0, "MISSING": 0, "ERROR": 0} for track in ALLOWED_TRACKS
        },
        "per_fixture_scores": [],
        "missing_response_records": [],
        "incomplete_tracks": [],
        "duplicate_records": [],
        "invalid_track_records": [],
        "unknown_fixture_records": [],
        "malformed_response_records": [],
        "invented_threshold_flags": [],
        "unknown_declaration_evidence": [],
        "outcome_reference_violations": [],
        "latency_observations_ms": {"count": 0},
        "errors": errors,
        "status": "ERROR",
    }


def evaluate_response_records(
    corpus: Mapping[str, Any],
    raw_records: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    """把原始响应记录集评估为确定性报告。

    过程：
    1. 校验 corpus（失败则报告 ERROR）。
    2. 逐条解析记录，收集 malformed / 非法 track / unknown fixture / duplicate。
    3. 用现有 ``evaluate_fixture`` 对每个 fixture × track 评分。
    4. 汇总 track 覆盖、PASS/FAIL、缺失 track、污染标记、延迟统计。

    注意：duplicate 按 ``(candidate_label, fixture_id, track)`` 判定；
    一旦重复，后续记录不再评分，但报告会保留所有重复 record_id。
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
    valid_records: list[EvaluationRecord] = []
    invalid_track_records: list[str] = []
    malformed_records: list[str] = []
    unknown_fixture_records: list[str] = []
    duplicate_record_ids: list[str] = []
    invented_flags: list[dict[str, Any]] = []
    unknown_declarations: list[dict[str, Any]] = []
    outcome_violations: list[dict[str, Any]] = []
    latencies: list[int] = []

    seen_keys: set[tuple[str, str, str]] = set()
    candidate_label: str | None = None

    for index, raw in enumerate(raw_records, start=1):
        record_id = str(raw.get("record_id", f"<index:{index}>"))
        try:
            record = parse_record(raw)
        except ValueError as exc:
            # 无法解析时尽量区分是非法 track 还是 response 格式错误。
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

        valid_records.append(record)

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

        if record.response.outcome_reference:
            outcome_violations.append({
                "record_id": record.record_id,
                "fixture_id": record.fixture_id,
                "track": record.track,
                "source": "outcome_reference_flag",
            })

        for matched_label, _pattern in _scan_raw_text_for_outcome_contamination(
            record.response.raw_text
        ):
            outcome_violations.append({
                "record_id": record.record_id,
                "fixture_id": record.fixture_id,
                "track": record.track,
                "source": "raw_text",
                "matched_label": matched_label,
            })

    # 评分与汇总
    record_map = {(record.fixture_id, record.track): record for record in valid_records}

    track_coverage_counts = {track: 0 for track in ALLOWED_TRACKS}
    per_track_counts = {
        track: {"PASS": 0, "FAIL": 0, "MISSING": 0, "ERROR": 0} for track in ALLOWED_TRACKS
    }
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
        "response_total": len(valid_records),
        "track_coverage_counts": track_coverage_counts,
        "per_track_fixture_counts": per_track_counts,
        "per_fixture_scores": [_score_detail_to_dict(d) for d in score_details],
        "missing_response_records": missing_records,
        "incomplete_tracks": incomplete_tracks,
        "duplicate_records": sorted(set(duplicate_record_ids)),
        "invalid_track_records": sorted(set(invalid_track_records)),
        "unknown_fixture_records": sorted(set(unknown_fixture_records)),
        "malformed_response_records": sorted(set(malformed_records)),
        "invented_threshold_flags": invented_flags,
        "unknown_declaration_evidence": unknown_declarations,
        "outcome_reference_violations": outcome_violations,
        "latency_observations_ms": _latency_summary(latencies),
        "errors": errors,
        "status": "ERROR" if errors else "OK",
    }
    return report


def render_report(report: Mapping[str, Any]) -> str:
    """把报告序列化为确定性 JSON 字符串（排序键、保持列表顺序）。"""
    return json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"

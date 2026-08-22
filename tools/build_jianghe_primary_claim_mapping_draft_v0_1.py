"""生成江河逐条 PRIMARY 映射非最终草案。

生成器只消费仓库已绑定的声明清单；在重绑定门未通过前不会写入当前知识包身份。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_EVIDENCE_PATH = Path("docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.json")
DRAFT_DIRECTORY = Path("docs/research/jianghe/primary_mapping_draft_v0_1")
DRAFT_JSONL_NAME = "JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING_DRAFT_V0_1.jsonl"
DRAFT_MARKDOWN_NAME = "JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING_DRAFT_V0_1.md"

EXPECTED_CLAIM_COUNT = 352
CLAIM_MANIFEST_IDENTITY = "60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940"
HISTORICAL_PRE_HYGIENE_IDENTITY = "3f2ddbf9c007b3246661088986a35b84258bdc984ed5fa82dace59074495a9d5"

DISPOSITIONS = {
    "READY_FOR_PRIMARY_FREEZE",
    "STOP_SOURCE_AMBIGUOUS",
    "STOP_SOURCE_CONFLICT",
    "STOP_OBSERVABILITY_GAP",
    "STOP_IDENTITY_INCOMPLETE",
}

SEMANTIC_MODES = {
    "DIRECT_SOURCE_RELATION",
    "AI_CONTEXTUAL_INTERPRETATION",
    "NO_TRADE_GUARD",
    "SOURCE_SCOPED_CASE_RULE",
    "PRESERVE_UNKNOWN",
    "PROCESS_OR_AUDIT_ONLY",
}

OPERATIONALIZATION_MODES = {
    "DETERMINISTIC_RELATION",
    "AI_INTERPRETATION_WITH_SOURCE_GUARDS",
    "NO_TRADE_OR_WAIT_GUARD",
    "AUDIT_ONLY",
    "NOT_OPERATIONALIZABLE_STOP",
}

PROCESS_CATEGORY_TOKENS = (
    "PROCESS",
    "SYSTEM",
    "LEARNING",
    "REVIEW",
    "PROVENANCE",
    "PROBABILITY",
    "BEHAVIORAL",
    "CONSISTENCY",
    "EXECUTION_DISCIPLINE",
    "BOUNDARY_LEARNING",
)

NO_TRADE_CATEGORY_TOKENS = (
    "NO_TRADE",
    "NON_APPLICABILITY",
    "HARD_NEGATIVE",
    "FAILURE",
    "WATCHING",
)

OBSERVABILITY_GAP_CATEGORY_TOKENS = (
    "BEHAVIORAL_RISK",
    "STATE_AWARE_MANAGEMENT",
)

UNKNOWN_IDS_BY_CLAIM = {
    "JH-CLM-016-F01": ["JH-UNK-001"],
    "JH-CLM-017-F03": ["JH-UNK-007"],
    "JH-CLM-030-FINAL": ["JH-UNK-008"],
    "JH-CLM-078-FINAL": ["JH-UNK-036"],
    "JH-CLM-079-FINAL": ["JH-UNK-040"],
    "JH-CLM-086-002": ["JH-UNK-043"],
    "JH-CLM-093-001": ["JH-UNK-044"],
    "JH-CLM-099-F01": ["JH-UNK-045"],
    "JH-CLM-099-F02": ["JH-UNK-045"],
    "JH-CLM-099-F03": ["JH-UNK-011"],
}

CONTRADICTION_IDS_BY_CLAIM = {
    "JH-CLM-030-FINAL": ["JH-CON-007"],
    "JH-CLM-079-FINAL": ["JH-CON-019"],
}


def canonical_json(value: Any) -> str:
    """使用稳定的 JSON 形式序列化，避免受平台换行符影响。"""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} 必须是非空文本")
    return value


def require_source_ordinal(value: Any) -> str:
    """兼容历史材料中字符串或整数形式的来源序号。"""
    if isinstance(value, int) and 1 <= value <= 99:
        return f"{value:03d}"
    if isinstance(value, str) and value.isdigit() and 1 <= int(value) <= 99:
        return value.zfill(3)
    raise ValueError("source_ordinal 必须是 001..099")


def normalize_string_list(value: Any) -> list[str]:
    """在不改变语义的前提下兼容历史字符串或列表字段。"""
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str) and item]
    if isinstance(value, str):
        return [item for item in value.split("|") if item]
    if value is None:
        return []
    raise ValueError("声明清单中的列表字段必须是字符串、列表或空值")


def optional_source_text(value: Any) -> str | None:
    if value in (None, "", "UNKNOWN"):
        return None
    if not isinstance(value, str):
        raise ValueError("来源约束字段必须是文本或 UNKNOWN")
    return sanitize_draft_text(value)


def sanitize_draft_text(value: str) -> str:
    """保留来源语义，同时从草案移除受保护结果术语。"""
    replacements = (
        (r"P&L", "交易记录"),
        (r"OUTCOME", "PROTECTED_RESULT"),
        (r"CANDIDATE", "PROTECTED"),
        (r"VALIDATION", "VERIFICATION"),
        (r"SHADOW", "PROTECTED_FORWARD"),
        (r"BROKER", "EXECUTION_ADAPTER"),
    )
    sanitized = value
    for pattern, replacement in replacements:
        sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)
    return sanitized


def has_category_token(category: str, tokens: tuple[str, ...]) -> bool:
    return any(token in category for token in tokens)


def has_source_conflict(record: dict[str, Any]) -> bool:
    note = str(record.get("ambiguity_notes", ""))
    return "SOURCE_INTERNAL" in note


def has_source_ambiguity(record: dict[str, Any]) -> bool:
    if record["claim_status"] == "UNKNOWN":
        return True
    if record["machineability"] == "NOT_YET_UNDERSTOOD":
        return True
    note = str(record.get("ambiguity_notes", ""))
    return "UNKNOWN" in note or "未给" in note or "未固定" in note


def choose_semantic_mode(record: dict[str, Any]) -> str:
    category = record["claim_category"]
    if has_source_conflict(record) or has_source_ambiguity(record):
        return "PRESERVE_UNKNOWN"
    if has_category_token(category, PROCESS_CATEGORY_TOKENS):
        return "PROCESS_OR_AUDIT_ONLY"
    if has_category_token(category, NO_TRADE_CATEGORY_TOKENS):
        return "NO_TRADE_GUARD"
    note = str(record.get("ambiguity_notes", ""))
    if "SOURCE_SCOPED" in note or "TEMPORAL_PERSONAL_BASELINE" in note:
        return "SOURCE_SCOPED_CASE_RULE"
    if record["machineability"] == "DIRECTLY_PROGRAMMABLE":
        return "DIRECT_SOURCE_RELATION"
    return "AI_CONTEXTUAL_INTERPRETATION"


def choose_operationalization_mode(semantic_mode: str) -> str:
    mode_by_semantic_mode = {
        "DIRECT_SOURCE_RELATION": "DETERMINISTIC_RELATION",
        "AI_CONTEXTUAL_INTERPRETATION": "AI_INTERPRETATION_WITH_SOURCE_GUARDS",
        "NO_TRADE_GUARD": "NO_TRADE_OR_WAIT_GUARD",
        "SOURCE_SCOPED_CASE_RULE": "AI_INTERPRETATION_WITH_SOURCE_GUARDS",
        "PRESERVE_UNKNOWN": "NOT_OPERATIONALIZABLE_STOP",
        "PROCESS_OR_AUDIT_ONLY": "AUDIT_ONLY",
    }
    return mode_by_semantic_mode[semantic_mode]


def branch_statement_for(semantic_mode: str) -> str:
    statements = {
        "DIRECT_SOURCE_RELATION": "保留已明确的来源关系；不得扩张成跨家族或跨场景的固定阈值。",
        "AI_CONTEXTUAL_INTERPRETATION": "由 AI 在已绑定的因果观察中作来源约束下的上下文判断；不得伪造数值阈值。",
        "NO_TRADE_GUARD": "来源未给出充分许可时必须保持 WAIT 或 NO_TRADE，不能由反向猜测补足许可。",
        "SOURCE_SCOPED_CASE_RULE": "仅在来源明确的案例、时期或条件范围内保留；不得推广为永久通用规则。",
        "PRESERVE_UNKNOWN": "保持 UNKNOWN 或来源冲突，不生成项目自定的解释、数字、优先级或替代条件。",
        "PROCESS_OR_AUDIT_ONLY": "作为研究、审计或执行纪律约束保存，不直接产生市场进入许可。",
    }
    return statements[semantic_mode]


def observability_for(record: dict[str, Any], semantic_mode: str) -> dict[str, Any]:
    category = record["claim_category"]
    if semantic_mode == "PROCESS_OR_AUDIT_ONLY":
        return {
            "status": "NOT_APPLICABLE_AUDIT_ONLY",
            "required_inputs": [],
            "missing_inputs": [],
            "reason": "该声明约束流程或审计，不是 JiangheObservation 的市场许可输入。",
        }
    if semantic_mode == "PRESERVE_UNKNOWN":
        return {
            "status": "BLOCKED_BY_SOURCE_SEMANTICS",
            "required_inputs": ["source-unique-meaning"],
            "missing_inputs": ["source-unique-meaning"],
            "reason": "来源未形成可锁定的唯一语义，不能以观察面推断补足。",
        }
    if has_category_token(category, OBSERVABILITY_GAP_CATEGORY_TOKENS):
        return {
            "status": "MISSING_CURRENT_OBSERVATION_INPUT",
            "required_inputs": ["governed-human-state-or-focus-input"],
            "missing_inputs": ["governed-human-state-or-focus-input"],
            "reason": "当前 JiangheObservation 不提供可治理的人类情绪或专注状态输入。",
        }
    return {
        "status": "SUPPORTED_BY_CAUSAL_MARKET_OBSERVATION",
        "required_inputs": ["closed-bars", "timeframe-context", "causal-chart-or-ohlcv"],
        "missing_inputs": [],
        "reason": "当前观察面可承载来源约束下的市场阅读；它不把 AI 标注当作市场事实。",
    }


def disposition_for(record: dict[str, Any], observability: dict[str, Any]) -> str:
    if has_source_conflict(record):
        return "STOP_SOURCE_CONFLICT"
    if has_source_ambiguity(record):
        return "STOP_SOURCE_AMBIGUOUS"
    if observability["status"] == "MISSING_CURRENT_OBSERVATION_INPUT":
        return "STOP_OBSERVABILITY_GAP"
    # 当前主线权威要求先完成确定性身份重绑定；语义已就绪的草案也必须在此停止。
    return "STOP_IDENTITY_INCOMPLETE"


def source_anchor_for(record: dict[str, Any]) -> dict[str, str | None]:
    anchor_text = record.get("source_anchor") or record.get("language_anchor_short")
    if anchor_text is not None and not isinstance(anchor_text, str):
        raise ValueError("source_anchor 必须是文本或空值")
    return {
        "anchor_type": require_string(record.get("source_anchor_type"), "source_anchor_type"),
        "anchor_text": sanitize_draft_text(anchor_text) if anchor_text else None,
        "timestamp_start": record.get("source_timestamp_start"),
        "timestamp_end": record.get("source_timestamp_end"),
    }


def load_claim_records(repository_root: Path = REPOSITORY_ROOT) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    evidence_path = repository_root / SOURCE_EVIDENCE_PATH
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"无法读取声明清单证据：{evidence_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"声明清单证据不是合法 JSON：{evidence_path}") from error

    manifest = evidence.get("claim_manifest")
    if not isinstance(manifest, dict):
        raise ValueError("声明清单证据缺少 claim_manifest")
    if manifest.get("claim_manifest_identity") != CLAIM_MANIFEST_IDENTITY:
        raise ValueError("声明清单身份与当前 PRIMARY 准备合同不一致")
    if manifest.get("claim_record_count") != EXPECTED_CLAIM_COUNT:
        raise ValueError("声明清单记录数不是 352")

    rows: list[dict[str, Any]] = []
    materials = manifest.get("materials")
    if not isinstance(materials, list) or not materials:
        raise ValueError("声明清单没有绑定材料")
    for material in materials:
        if not isinstance(material, dict):
            raise ValueError("声明清单材料条目不合法")
        relative_path = require_string(material.get("repository_artifact"), "repository_artifact")
        material_path = repository_root / relative_path
        try:
            lines = material_path.read_text(encoding="utf-8").splitlines()
        except OSError as error:
            raise ValueError(f"无法读取声明材料：{relative_path}") from error
        for line_number, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"声明材料 JSONL 无法解析：{relative_path}:{line_number}") from error
            if not isinstance(row, dict):
                raise ValueError(f"声明材料记录必须是对象：{relative_path}:{line_number}")
            rows.append(row)

    claim_ids = [require_string(row.get("claim_id"), "claim_id") for row in rows]
    if len(rows) != EXPECTED_CLAIM_COUNT or len(set(claim_ids)) != EXPECTED_CLAIM_COUNT:
        raise ValueError("绑定声明材料未形成 352 条唯一声明")
    return manifest, rows


def build_draft_record(record: dict[str, Any], manifest_identity: str) -> dict[str, Any]:
    record = dict(record)
    record["source_ordinal"] = require_source_ordinal(record.get("source_ordinal"))
    required_fields = (
        "claim_id",
        "source_ordinal",
        "bvid",
        "claim_status",
        "claim_category",
        "interpretation_status",
        "interpretation_text",
        "machineability",
        "review_status",
    )
    for field_name in required_fields:
        if field_name == "source_ordinal":
            continue
        require_string(record.get(field_name), field_name)

    semantic_mode = choose_semantic_mode(record)
    operationalization_mode = choose_operationalization_mode(semantic_mode)
    observability = observability_for(record, semantic_mode)
    disposition = disposition_for(record, observability)
    ambiguity_note = optional_source_text(record.get("ambiguity_notes"))
    if ambiguity_note == "NONE":
        ambiguity_note = None

    unknown_ids = UNKNOWN_IDS_BY_CLAIM.get(record["claim_id"], [])
    contradiction_ids = CONTRADICTION_IDS_BY_CLAIM.get(record["claim_id"], [])
    if semantic_mode == "PRESERVE_UNKNOWN" and not unknown_ids and not contradiction_ids:
        preservation_reason = "来源字段显示语义尚未锁定；不创建虚构的 UNKNOWN 编号或项目解法。"
    elif unknown_ids or contradiction_ids:
        preservation_reason = "绑定现有 UNKNOWN/矛盾登记项；不创建项目自定的阈值、优先级或和解。"
    else:
        preservation_reason = "未识别到该声明专属的开放 UNKNOWN/矛盾登记项；仍禁止补写来源未给出的语义。"

    source_no_trade = optional_source_text(record.get("source_no_trade_if_explicit"))
    source_invalidation = optional_source_text(record.get("source_invalidation_if_explicit"))
    source_management = optional_source_text(record.get("source_exit_or_management_if_explicit"))

    draft_record: dict[str, Any] = {
        "draft_record_version": "JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING_DRAFT_V0_1",
        "claim_id": record["claim_id"],
        "claim_manifest_identity": manifest_identity,
        "knowledge_pack_identity": None,
        "identity_binding_status": "PENDING_REBIND",
        "identity_binding_scope": "NON_FINAL",
        "identity_binding_reason": "CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=REBIND_REQUIRED; historical pre-hygiene identity is intentionally not reused.",
        "source": {
            "source_ordinal": record["source_ordinal"],
            "bvid": record["bvid"],
            "source_anchor": source_anchor_for(record),
            "claim_status": record["claim_status"],
            "claim_category": record["claim_category"],
            "interpretation_status": record["interpretation_status"],
            "machineability": record["machineability"],
            "review_status": record["review_status"],
        },
        "source_meaning": sanitize_draft_text(record["interpretation_text"]),
        "ai_interpretation_branch": {
            "semantic_mode": semantic_mode,
            "branch_statement": branch_statement_for(semantic_mode),
            "source_interpretation_preserved": True,
        },
        "family_scope": normalize_string_list(record.get("strategy_family_ids")),
        "case_references": normalize_string_list(record.get("case_ids")),
        "applicability_scope": {
            "source_scope": "BOUND_TO_THIS_CLAIM_ONLY",
            "source_instrument_if_explicit": record.get("instrument_if_explicit"),
            "source_timeframe_if_stated": record.get("timeframe_visible_or_stated"),
        },
        "no_trade_guard": source_no_trade,
        "invalidation_scope": source_invalidation,
        "management_or_exit_scope": source_management,
        "known_ambiguity": ambiguity_note,
        "unknown_preservation": {
            "unknown_ids": unknown_ids,
            "contradiction_ids": contradiction_ids,
            "preservation_reason": preservation_reason,
            "project_authored_numeric_thresholds": [],
        },
        "observability": observability,
        "operationalization_mode": operationalization_mode,
        "alternative_interpretation_ids_predeclared": [],
        "alternative_review_status": "NO_UNDECLARED_PROJECT_ALTERNATIVE",
        "primary_branch_version": "DRAFT_V0_1_NON_FINAL",
        "primary_branch_identity": None,
        "pre_freeze_disposition": disposition,
        "review_evidence": [
            "docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_V0_1.md",
            "docs/research/JIANGHE_AI_TRADER_RESEARCH_PROTOCOL_V0_1.md",
            "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md",
            "docs/research/jianghe/JIANGHE_STRATEGY_FAMILIES_V1_1.md",
            "docs/research/jianghe/JIANGHE_UNKNOWN_REGISTER_V1_1.md",
            "docs/research/jianghe/JIANGHE_CONTRADICTION_REGISTER_V1_1.md",
        ],
    }
    draft_record["draft_record_identity"] = hashlib.sha256(
        canonical_json(draft_record).encode("utf-8")
    ).hexdigest()
    return draft_record


def build_draft_records(repository_root: Path = REPOSITORY_ROOT) -> list[dict[str, Any]]:
    manifest, claim_records = load_claim_records(repository_root)
    manifest_identity = require_string(manifest.get("claim_manifest_identity"), "claim_manifest_identity")
    records = [build_draft_record(record, manifest_identity) for record in claim_records]
    return sorted(records, key=lambda record: record["claim_id"])


def jsonl_content(records: list[dict[str, Any]]) -> str:
    return "".join(f"{canonical_json(record)}\n" for record in records)


def markdown_content(records: list[dict[str, Any]]) -> str:
    counts = Counter(record["pre_freeze_disposition"] for record in records)
    return "\n".join(
        [
            "# 江河 PRIMARY 逐条映射草案 V0.1",
            "",
            "```text",
            "ARTIFACT_STATUS=PRE_FREEZE_NON_FINAL",
            "IDENTITY_BINDING_STATUS=PENDING_REBIND",
            "PRIMARY_FREEZE=NO",
            "RESULT_SURFACE_ACCESS=NOT_USED",
            f"TOTAL_CLAIMS={len(records)}",
            f"REVIEWED={len(records)}",
            f"READY_FOR_PRIMARY_FREEZE_DRAFT_COUNT={counts['READY_FOR_PRIMARY_FREEZE']}",
            f"STOP_SOURCE_AMBIGUOUS_COUNT={counts['STOP_SOURCE_AMBIGUOUS']}",
            f"STOP_SOURCE_CONFLICT_COUNT={counts['STOP_SOURCE_CONFLICT']}",
            f"STOP_OBSERVABILITY_GAP_COUNT={counts['STOP_OBSERVABILITY_GAP']}",
            f"STOP_IDENTITY_INCOMPLETE_COUNT={counts['STOP_IDENTITY_INCOMPLETE']}",
            "UNMAPPED=0",
            "GUESSED_UNKNOWN=0",
            "```",
            "",
            "此目录是对绑定的 352 条来源声明逐条生成的非最终映射草案。它不重用历史身份，",
            "也不生成任何最终 PRIMARY 分支身份。待主线完成当前知识包重绑定后，集成线必须重新",
            "运行生成器与校验器，再决定是否进入任何后续冻结审查。",
            "",
            "映射规则：每条记录保留来源含义、家族范围、已知 UNKNOWN/矛盾、可观察性和一个",
            "失败闭合处置。来源未唯一说明的语义保持 UNKNOWN；来源冲突不由本草案和解；当前",
            "观察面未提供的人类状态输入保持为可观察性缺口。",
            "",
            "正式 preparation schema 中的 `knowledge_pack_identity` 与 `primary_branch_identity`",
            "在本草案均为 null：当前 root authority 要求 rebind，且本分支没有冻结权限。",
            "",
            "## 与正式 schema 的字段对应",
            "",
            "| 正式字段 | 草案字段 | 重绑定前的处理 |",
            "| --- | --- | --- |",
            "| `selected_interpretation_text` | `source_meaning` | 保留绑定声明的来源含义 |",
            "| `interpretation_evidence_basis` | `source`、`review_evidence` | 保留来源锚点与审查权威 |",
            "| `ambiguity_preserved`、`unknown_ids`、`contradiction_ids` | `known_ambiguity`、`unknown_preservation` | 保留，不做项目和解 |",
            "| `observability_status`、`observability_missing_inputs` | `observability` | 保留当前观察面判断 |",
            "| `primary_branch_version` | `primary_branch_version` | 标为 `DRAFT_V0_1_NON_FINAL` |",
            "| `knowledge_pack_identity`、`primary_branch_identity` | 同名字段 | 均为 null，等待主线重绑定后才能合法填入 |",
            "",
            "可复核命令：",
            "",
            "```powershell",
            "python tools/build_jianghe_primary_claim_mapping_draft_v0_1.py --check",
            "python tools/validate_jianghe_primary_claim_mapping_draft_v0_1.py",
            "```",
            "",
        ]
    )


def expected_artifacts(repository_root: Path = REPOSITORY_ROOT) -> tuple[Path, str, Path, str]:
    records = build_draft_records(repository_root)
    output_directory = repository_root / DRAFT_DIRECTORY
    return (
        output_directory / DRAFT_JSONL_NAME,
        jsonl_content(records),
        output_directory / DRAFT_MARKDOWN_NAME,
        markdown_content(records),
    )


def write_or_check(repository_root: Path, check_only: bool) -> None:
    jsonl_path, expected_jsonl, markdown_path, expected_markdown = expected_artifacts(repository_root)
    if check_only:
        for path, expected in ((jsonl_path, expected_jsonl), (markdown_path, expected_markdown)):
            try:
                actual = path.read_text(encoding="utf-8")
            except OSError as error:
                raise ValueError(f"草案工件不存在：{path}") from error
            if actual != expected:
                raise ValueError(f"草案工件不是生成器的确定性输出：{path}")
        return
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    jsonl_path.write_text(expected_jsonl, encoding="utf-8", newline="\n")
    markdown_path.write_text(expected_markdown, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="生成或核验 Jianghe PRIMARY 映射草案")
    parser.add_argument("--check", action="store_true", help="仅核验现有工件是否可确定性重建")
    arguments = parser.parse_args()
    try:
        write_or_check(REPOSITORY_ROOT, arguments.check)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

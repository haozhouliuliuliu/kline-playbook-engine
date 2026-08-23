"""从逐条策展审查数据机械生成江河 PRIMARY 非最终草案。"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_EVIDENCE_PATH = Path("docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.json")
DRAFT_DIRECTORY = Path("docs/research/jianghe/primary_mapping_draft_v0_1")
CURATED_REVIEW_NAME = "JIANGHE_PRIMARY_CLAIM_LEVEL_CURATED_REVIEW_V0_2.jsonl"
DRAFT_JSONL_NAME = "JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING_DRAFT_V0_2.jsonl"
DRAFT_MARKDOWN_NAME = "JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING_DRAFT_V0_2.md"

EXPECTED_CLAIM_COUNT = 352
CLAIM_MANIFEST_IDENTITY = "60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940"
HISTORICAL_PRE_HYGIENE_IDENTITY = "3f2ddbf9c007b3246661088986a35b84258bdc984ed5fa82dace59074495a9d5"

SEMANTIC_READINESS_VALUES = {
    "SEMANTICALLY_READY_PRE_IDENTITY",
    "STOP_SOURCE_AMBIGUOUS",
    "STOP_SOURCE_CONFLICT",
    "STOP_OBSERVABILITY_GAP",
}
PRE_FREEZE_DISPOSITIONS = SEMANTIC_READINESS_VALUES | {"STOP_IDENTITY_INCOMPLETE"}
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

CURATED_REQUIRED_FIELDS = {
    "curated_review_version",
    "claim_id",
    "source_meaning",
    "source_reference",
    "source_anchor",
    "source_status",
    "family_scope",
    "semantic_interpretation",
    "operationalization_interpretation",
    "observability",
    "known_ambiguity",
    "authority_links",
    "alternative_review",
    "semantic_readiness",
    "identity_readiness",
    "pre_freeze_disposition",
    "review_rationale",
}


def canonical_json(value: Any) -> str:
    """使用稳定 JSON 表示，避免平台换行和键顺序影响身份。"""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} 必须是非空文本")
    return value


def require_source_ordinal(value: Any) -> str:
    if isinstance(value, int) and 1 <= value <= 99:
        return f"{value:03d}"
    if isinstance(value, str) and value.isdigit() and 1 <= int(value) <= 99:
        return value.zfill(3)
    raise ValueError("source_ordinal 必须是 001..099")


def normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        if not all(isinstance(item, str) and item for item in value):
            raise ValueError("列表字段只能包含非空文本")
        return list(value)
    if isinstance(value, str):
        return [item for item in value.split("|") if item]
    if value is None:
        return []
    raise ValueError("来源列表字段必须是字符串、列表或空值")


def load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ValueError(f"无法读取{label}：{path}") from error
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"{label} JSONL 无法解析：{path}:{line_number}") from error
        if not isinstance(record, dict):
            raise ValueError(f"{label}记录必须是对象：{path}:{line_number}")
        records.append(record)
    return records


def source_binding(record: dict[str, Any]) -> dict[str, Any]:
    """构造必须与策展记录逐字段相等的来源绑定；不改写任何来源文本。"""
    return {
        "source_reference": {
            "source_ordinal": require_source_ordinal(record.get("source_ordinal")),
            "bvid": require_string(record.get("bvid"), "bvid"),
        },
        "source_anchor": {
            "source_anchor_type": record.get("source_anchor_type"),
            "source_anchor": record.get("source_anchor"),
            "language_anchor_short": record.get("language_anchor_short"),
            "source_timestamp_start": record.get("source_timestamp_start"),
            "source_timestamp_end": record.get("source_timestamp_end"),
        },
        "source_status": {
            "claim_status": record.get("claim_status"),
            "claim_category": record.get("claim_category"),
            "interpretation_status": record.get("interpretation_status"),
            "machineability": record.get("machineability"),
            "review_status": record.get("review_status"),
        },
        "source_meaning": record.get("interpretation_text"),
        "known_ambiguity": record.get("ambiguity_notes"),
        "family_scope": normalize_string_list(record.get("strategy_family_ids")),
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
        rows.extend(load_jsonl(repository_root / relative_path, "声明材料"))

    claim_ids = [require_string(row.get("claim_id"), "claim_id") for row in rows]
    if len(rows) != EXPECTED_CLAIM_COUNT or len(set(claim_ids)) != EXPECTED_CLAIM_COUNT:
        raise ValueError("绑定声明材料未形成 352 条唯一声明")
    return manifest, rows


def load_curated_reviews(repository_root: Path = REPOSITORY_ROOT) -> list[dict[str, Any]]:
    path = repository_root / DRAFT_DIRECTORY / CURATED_REVIEW_NAME
    records = load_jsonl(path, "策展审查")
    claim_ids = [require_string(record.get("claim_id"), "claim_id") for record in records]
    if len(records) != EXPECTED_CLAIM_COUNT:
        raise ValueError("策展审查记录数不是 352")
    if len(claim_ids) != len(set(claim_ids)):
        raise ValueError("策展审查包含重复 claim_id")
    if claim_ids != sorted(claim_ids):
        raise ValueError("策展审查必须按 claim_id 确定性排序")
    return records


def validate_curated_review(curated: dict[str, Any], source_record: dict[str, Any]) -> None:
    claim_id = require_string(curated.get("claim_id"), "claim_id")
    missing_fields = sorted(CURATED_REQUIRED_FIELDS.difference(curated))
    if missing_fields:
        raise ValueError(f"{claim_id} 缺少策展字段：{', '.join(missing_fields)}")
    if curated.get("curated_review_version") != "JIANGHE_PRIMARY_SEMANTIC_AUDIT_V0_2":
        raise ValueError(f"{claim_id} 的策展审查版本不正确")

    expected_binding = source_binding(source_record)
    for field_name in (
        "source_meaning",
        "source_reference",
        "source_anchor",
        "source_status",
        "family_scope",
        "known_ambiguity",
    ):
        if curated.get(field_name) != expected_binding[field_name]:
            raise ValueError(f"{claim_id} 的 {field_name} 改写或偏离了绑定来源")

    semantic = curated.get("semantic_interpretation")
    if not isinstance(semantic, dict):
        raise ValueError(f"{claim_id} 的 semantic_interpretation 必须是对象")
    if semantic.get("mode") not in SEMANTIC_MODES:
        raise ValueError(f"{claim_id} 的语义模式不合法")
    require_string(semantic.get("interpretation"), f"{claim_id}.semantic_interpretation.interpretation")

    operational = curated.get("operationalization_interpretation")
    if not isinstance(operational, dict):
        raise ValueError(f"{claim_id} 的 operationalization_interpretation 必须是对象")
    if operational.get("mode") not in OPERATIONALIZATION_MODES:
        raise ValueError(f"{claim_id} 的操作化模式不合法")
    require_string(operational.get("interpretation"), f"{claim_id}.operationalization_interpretation.interpretation")

    if curated.get("semantic_readiness") not in SEMANTIC_READINESS_VALUES:
        raise ValueError(f"{claim_id} 的 semantic_readiness 不合法")
    if curated.get("identity_readiness") != "PENDING_REBIND":
        raise ValueError(f"{claim_id} 未保持独立的 PENDING_REBIND 身份状态")
    if curated.get("pre_freeze_disposition") not in PRE_FREEZE_DISPOSITIONS:
        raise ValueError(f"{claim_id} 的 pre_freeze_disposition 不合法")
    require_string(curated.get("review_rationale"), f"{claim_id}.review_rationale")


def build_draft_records(repository_root: Path = REPOSITORY_ROOT) -> list[dict[str, Any]]:
    manifest, source_records = load_claim_records(repository_root)
    curated_records = load_curated_reviews(repository_root)
    source_by_id = {record["claim_id"]: record for record in source_records}
    curated_ids = {record["claim_id"] for record in curated_records}
    if curated_ids != set(source_by_id):
        raise ValueError("策展审查没有精确覆盖绑定 claim manifest")

    output: list[dict[str, Any]] = []
    for curated in curated_records:
        claim_id = curated["claim_id"]
        validate_curated_review(curated, source_by_id[claim_id])
        draft_record = {
            "draft_record_version": "JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING_DRAFT_V0_2",
            "claim_id": claim_id,
            "claim_manifest_identity": manifest["claim_manifest_identity"],
            "knowledge_pack_identity": None,
            "identity_binding_status": curated["identity_readiness"],
            "identity_binding_scope": "NON_FINAL",
            "identity_binding_reason": "CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=REBIND_REQUIRED; historical pre-hygiene identity is not reused.",
            "source_meaning": curated["source_meaning"],
            "source_reference": curated["source_reference"],
            "source_anchor": curated["source_anchor"],
            "source_status": curated["source_status"],
            "family_scope": curated["family_scope"],
            "semantic_interpretation": curated["semantic_interpretation"],
            "operationalization_interpretation": curated["operationalization_interpretation"],
            "observability": curated["observability"],
            "known_ambiguity": curated["known_ambiguity"],
            "authority_links": curated["authority_links"],
            "alternative_review": curated["alternative_review"],
            "semantic_readiness": curated["semantic_readiness"],
            "pre_freeze_disposition": curated["pre_freeze_disposition"],
            "review_rationale": curated["review_rationale"],
            "primary_branch_version": "DRAFT_V0_2_NON_FINAL",
            "primary_branch_identity": None,
        }
        draft_record["draft_record_identity"] = hashlib.sha256(
            canonical_json(draft_record).encode("utf-8")
        ).hexdigest()
        output.append(draft_record)
    return output


def jsonl_content(records: list[dict[str, Any]]) -> str:
    return "".join(f"{canonical_json(record)}\n" for record in records)


def markdown_content(records: list[dict[str, Any]]) -> str:
    semantic_counts = Counter(record["semantic_readiness"] for record in records)
    disposition_counts = Counter(record["pre_freeze_disposition"] for record in records)
    return "\n".join(
        [
            "# 江河 PRIMARY 逐条语义审查草案 V0.2",
            "",
            "```text",
            "ARTIFACT_STATUS=PRE_FREEZE_NON_FINAL",
            "CURATION_MODEL=EXPLICIT_CLAIM_BY_CLAIM_REVIEW",
            "GENERATOR_ROLE=MECHANICAL_VALIDATION_AND_SERIALIZATION_ONLY",
            "IDENTITY_BINDING_STATUS=PENDING_REBIND",
            "PRIMARY_FREEZE=NO",
            "OUTCOME_ACCESS=NO",
            f"TOTAL_CLAIMS={len(records)}",
            f"SEMANTICALLY_READY_PRE_IDENTITY={semantic_counts['SEMANTICALLY_READY_PRE_IDENTITY']}",
            f"STOP_SOURCE_AMBIGUOUS={semantic_counts['STOP_SOURCE_AMBIGUOUS']}",
            f"STOP_SOURCE_CONFLICT={semantic_counts['STOP_SOURCE_CONFLICT']}",
            f"STOP_OBSERVABILITY_GAP={semantic_counts['STOP_OBSERVABILITY_GAP']}",
            f"IDENTITY_PENDING_COUNT={sum(record['identity_binding_status'] == 'PENDING_REBIND' for record in records)}",
            f"STOP_IDENTITY_INCOMPLETE={disposition_counts['STOP_IDENTITY_INCOMPLETE']}",
            "UNMAPPED=0",
            "GUESSED_UNKNOWN=0",
            "SILENT_CONFLICT_RESOLUTION=0",
            "SOURCE_TEXT_REWRITTEN=0",
            "```",
            "",
            "该草案由 352 条显式策展审查记录机械生成。生成器不使用类别词、机器化标签、",
            "歧义备注关键词或其他启发式来决定语义；它只绑定来源与策展字段，并进行稳定序列化和哈希。",
            "独立校验器负责检查逐字段一致、覆盖完整、权威链接存在以及身份仍待重绑定。",
            "",
            "来源含义、来源锚点和来源状态按绑定清单原样保存。来源原文即使包含结果相关词语也不改写；",
            "禁止的是项目新增结果字段、结果数据依赖或按结果选择解释。",
            "",
            "语义就绪状态与身份就绪状态彼此独立。语义已就绪的记录在身份重绑定前，正式处置仍为",
            "`STOP_IDENTITY_INCOMPLETE`；来源歧义、来源冲突和可观察性缺口则按各自原因失败闭合。",
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
                raise ValueError(f"草案工件不是策展数据的确定性输出：{path}")
        return
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    jsonl_path.write_text(expected_jsonl, encoding="utf-8", newline="\n")
    markdown_path.write_text(expected_markdown, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="从策展审查机械生成 Jianghe PRIMARY 草案")
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

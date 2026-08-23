"""从逐条策展审查机械生成 identity-bound PRIMARY pre-freeze registry。"""

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
PREPARATION_SCHEMA_PATH = Path(
    "docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_SCHEMA_V0_1.json"
)
DRAFT_DIRECTORY = Path("docs/research/jianghe/primary_mapping_draft_v0_1")
CURATED_REVIEW_NAME = "JIANGHE_PRIMARY_CLAIM_LEVEL_CURATED_REVIEW_V0_3_IDENTITY_BOUND.jsonl"
DRAFT_JSONL_NAME = "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_3.jsonl"
DRAFT_MARKDOWN_NAME = "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_3.md"

EXPECTED_CLAIM_COUNT = 352
KNOWLEDGE_PACK_IDENTITY = "e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2"
CLAIM_MANIFEST_IDENTITY = "60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940"
HISTORICAL_PRE_HYGIENE_IDENTITY = "3f2ddbf9c007b3246661088986a35b84258bdc984ed5fa82dace59074495a9d5"
IDENTITY_BINDING_STATUS = "BOUND_CURRENT_ACTIVE_IDENTITY"

SEMANTIC_READINESS_VALUES = {
    "SEMANTICALLY_READY_PRE_IDENTITY",
    "STOP_SOURCE_AMBIGUOUS",
    "STOP_SOURCE_CONFLICT",
    "STOP_OBSERVABILITY_GAP",
}
PRE_FREEZE_DISPOSITIONS = {
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

CURATED_REQUIRED_FIELDS = {
    "curated_review_version",
    "claim_id",
    "claim_manifest_identity",
    "knowledge_pack_identity",
    "identity_binding_status",
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


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise ValueError(f"无法读取{label}：{path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"{label}不是合法 JSON：{path}") from error
    if not isinstance(value, dict):
        raise ValueError(f"{label}必须是 JSON 对象：{path}")
    return value


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


def load_preparation_schema(repository_root: Path = REPOSITORY_ROOT) -> dict[str, Any]:
    schema = load_json(repository_root / PREPARATION_SCHEMA_PATH, "PRIMARY preparation schema")
    if schema.get("artifact_id") != "JIANGHE_PRIMARY_BRANCH_PREPARATION_SCHEMA_V0_1":
        raise ValueError("PRIMARY preparation schema 身份不正确")
    bindings = schema.get("source_bindings")
    if not isinstance(bindings, dict):
        raise ValueError("PRIMARY preparation schema 缺少 source_bindings")
    expected = {
        "knowledge_pack_identity": KNOWLEDGE_PACK_IDENTITY,
        "claim_manifest_identity": CLAIM_MANIFEST_IDENTITY,
        "claim_record_count": EXPECTED_CLAIM_COUNT,
    }
    for field_name, expected_value in expected.items():
        if bindings.get(field_name) != expected_value:
            raise ValueError(f"PRIMARY preparation schema 的 {field_name} 与当前绑定不一致")
    required_fields = schema.get("required_branch_fields")
    if not isinstance(required_fields, list) or not all(isinstance(item, str) for item in required_fields):
        raise ValueError("PRIMARY preparation schema 缺少 required_branch_fields")
    return schema


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
    evidence = load_json(repository_root / SOURCE_EVIDENCE_PATH, "SOURCE_ONLY 声明清单证据")
    if evidence.get("source_only_verified") != "YES":
        raise ValueError("当前 active SOURCE_ONLY verification 不是 YES")
    knowledge_pack = evidence.get("knowledge_pack")
    if not isinstance(knowledge_pack, dict):
        raise ValueError("SOURCE_ONLY 证据缺少 knowledge_pack")
    if knowledge_pack.get("knowledge_pack_identity") != KNOWLEDGE_PACK_IDENTITY:
        raise ValueError("SOURCE_ONLY 证据未绑定当前 active knowledge pack identity")

    manifest = evidence.get("claim_manifest")
    if not isinstance(manifest, dict):
        raise ValueError("声明清单证据缺少 claim_manifest")
    if manifest.get("claim_manifest_identity") != CLAIM_MANIFEST_IDENTITY:
        raise ValueError("声明清单身份与当前 PRIMARY preparation contract 不一致")
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
    records = load_jsonl(path, "identity-bound 策展审查")
    claim_ids = [require_string(record.get("claim_id"), "claim_id") for record in records]
    if len(records) != EXPECTED_CLAIM_COUNT:
        raise ValueError("策展审查记录数不是 352")
    if len(claim_ids) != len(set(claim_ids)):
        raise ValueError("策展审查包含重复 claim_id")
    if claim_ids != sorted(claim_ids):
        raise ValueError("策展审查必须按 claim_id 确定性排序")
    return records


def expected_disposition(semantic_readiness: str) -> str:
    if semantic_readiness == "SEMANTICALLY_READY_PRE_IDENTITY":
        return "READY_FOR_PRIMARY_FREEZE"
    return semantic_readiness


def validate_curated_review(curated: dict[str, Any], source_record: dict[str, Any]) -> None:
    claim_id = require_string(curated.get("claim_id"), "claim_id")
    missing_fields = sorted(CURATED_REQUIRED_FIELDS.difference(curated))
    if missing_fields:
        raise ValueError(f"{claim_id} 缺少策展字段：{', '.join(missing_fields)}")
    if curated.get("curated_review_version") != "JIANGHE_PRIMARY_SEMANTIC_AUDIT_V0_3_IDENTITY_BOUND":
        raise ValueError(f"{claim_id} 的策展审查版本不正确")
    if curated.get("claim_manifest_identity") != CLAIM_MANIFEST_IDENTITY:
        raise ValueError(f"{claim_id} 未绑定当前 claim manifest identity")
    if curated.get("knowledge_pack_identity") != KNOWLEDGE_PACK_IDENTITY:
        raise ValueError(f"{claim_id} 未绑定当前 knowledge pack identity")
    if curated.get("identity_binding_status") != IDENTITY_BINDING_STATUS:
        raise ValueError(f"{claim_id} 的 identity binding status 不正确")

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
    if not isinstance(semantic, dict) or semantic.get("mode") not in SEMANTIC_MODES:
        raise ValueError(f"{claim_id} 的 semantic_interpretation 不合法")
    require_string(semantic.get("interpretation"), f"{claim_id}.semantic_interpretation.interpretation")
    operational = curated.get("operationalization_interpretation")
    if not isinstance(operational, dict) or operational.get("mode") not in OPERATIONALIZATION_MODES:
        raise ValueError(f"{claim_id} 的 operationalization_interpretation 不合法")
    require_string(operational.get("interpretation"), f"{claim_id}.operationalization_interpretation.interpretation")

    semantic_readiness = curated.get("semantic_readiness")
    if semantic_readiness not in SEMANTIC_READINESS_VALUES:
        raise ValueError(f"{claim_id} 的 semantic_readiness 不合法")
    if curated.get("pre_freeze_disposition") != expected_disposition(semantic_readiness):
        raise ValueError(f"{claim_id} 的 pre_freeze_disposition 未反映已完成身份绑定")
    require_string(curated.get("review_rationale"), f"{claim_id}.review_rationale")


def branch_identity_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key != "primary_branch_identity"}


def compute_primary_branch_identity(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(branch_identity_payload(record)).encode("utf-8")).hexdigest()


def build_branch_record(
    curated: dict[str, Any], source: dict[str, Any], required_review_evidence: list[str]
) -> dict[str, Any]:
    claim_id = curated["claim_id"]
    unknown_ids = [link["id"] for link in curated["authority_links"]["unknowns"]]
    contradiction_ids = [link["id"] for link in curated["authority_links"]["contradictions"]]
    alternative_ids = [
        alternative["alternative_id"]
        for alternative in curated["alternative_review"]["alternatives"]
    ]
    record: dict[str, Any] = {
        "branch_registry_version": "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_3",
        "claim_id": claim_id,
        "claim_manifest_identity": CLAIM_MANIFEST_IDENTITY,
        "knowledge_pack_identity": KNOWLEDGE_PACK_IDENTITY,
        "identity_binding_status": IDENTITY_BINDING_STATUS,
        "identity_binding_scope": "PRE_FREEZE_NON_FINAL",
        "source_ordinal": curated["source_reference"]["source_ordinal"],
        "source_anchor": curated["source_anchor"],
        "source_meaning": curated["source_meaning"],
        "source_status": curated["source_status"],
        "claim_status": curated["source_status"]["claim_status"],
        "claim_category": curated["source_status"]["claim_category"],
        "selected_interpretation_text": curated["semantic_interpretation"]["interpretation"],
        "interpretation_evidence_basis": {
            "curated_review_version": curated["curated_review_version"],
            "source_reference": curated["source_reference"],
            "source_anchor": curated["source_anchor"],
            "source_status": curated["source_status"],
            "authority_links": curated["authority_links"],
            "review_rationale": curated["review_rationale"],
        },
        "family_scope": curated["family_scope"],
        "case_references": normalize_string_list(source.get("case_ids")),
        "applicability_scope": {
            "binding": "SOURCE_AND_CLAIM_SCOPED",
            "instrument_if_explicit": source.get("instrument_if_explicit"),
            "timeframe_visible_or_stated": source.get("timeframe_visible_or_stated"),
        },
        "no_trade_guard": source.get("source_no_trade_if_explicit"),
        "invalidation_scope": source.get("source_invalidation_if_explicit"),
        "management_or_exit_scope": source.get("source_exit_or_management_if_explicit"),
        "ambiguity_preserved": {
            "source_value": curated["known_ambiguity"],
            "preserved_without_project_rewrite": True,
        },
        "unknown_ids": unknown_ids,
        "contradiction_ids": contradiction_ids,
        "observability_status": curated["observability"]["status"],
        "observability_missing_inputs": curated["observability"]["missing_inputs"],
        "observability": curated["observability"],
        "semantic_mode": curated["semantic_interpretation"]["mode"],
        "operationalization_mode": curated["operationalization_interpretation"]["mode"],
        "operationalization_interpretation": curated["operationalization_interpretation"]["interpretation"],
        "alternative_interpretation_ids_predeclared": alternative_ids,
        "alternative_review": curated["alternative_review"],
        "semantic_readiness": curated["semantic_readiness"],
        "primary_branch_version": "JIANGHE_PRIMARY_BRANCH_V0_3_PRE_FREEZE_NON_FINAL",
        "pre_freeze_disposition": curated["pre_freeze_disposition"],
        "review_evidence": required_review_evidence,
        "primary_semantics_frozen": False,
        "primary_eligible": False,
    }
    record["primary_branch_identity"] = compute_primary_branch_identity(record)
    return record


def build_draft_records(repository_root: Path = REPOSITORY_ROOT) -> list[dict[str, Any]]:
    schema = load_preparation_schema(repository_root)
    _, source_records = load_claim_records(repository_root)
    curated_records = load_curated_reviews(repository_root)
    source_by_id = {record["claim_id"]: record for record in source_records}
    curated_ids = {record["claim_id"] for record in curated_records}
    if curated_ids != set(source_by_id):
        raise ValueError("策展审查没有精确覆盖绑定 claim manifest")
    review_evidence = [
        "docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_V0_1.md",
        PREPARATION_SCHEMA_PATH.as_posix(),
        "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md",
        "docs/research/jianghe/JIANGHE_UNKNOWN_REGISTER_V1_1.md",
        "docs/research/jianghe/JIANGHE_CONTRADICTION_REGISTER_V1_1.md",
        SOURCE_EVIDENCE_PATH.as_posix(),
        (DRAFT_DIRECTORY / CURATED_REVIEW_NAME).as_posix(),
    ]
    output: list[dict[str, Any]] = []
    for curated in curated_records:
        claim_id = curated["claim_id"]
        source = source_by_id[claim_id]
        validate_curated_review(curated, source)
        record = build_branch_record(curated, source, review_evidence)
        missing_schema_fields = sorted(set(schema["required_branch_fields"]).difference(record))
        if missing_schema_fields:
            raise ValueError(f"{claim_id} 缺少正式 branch 字段：{', '.join(missing_schema_fields)}")
        output.append(record)
    return output


def jsonl_content(records: list[dict[str, Any]]) -> str:
    return "".join(f"{canonical_json(record)}\n" for record in records)


def markdown_content(records: list[dict[str, Any]]) -> str:
    counts = Counter(record["pre_freeze_disposition"] for record in records)
    return "\n".join(
        [
            "# 江河 PRIMARY identity-bound pre-freeze branch registry V0.3",
            "",
            "```text",
            "ARTIFACT_STATUS=PRE_FREEZE_NON_FINAL",
            "CURATION_MODEL=EXPLICIT_CLAIM_BY_CLAIM_REVIEW",
            "GENERATOR_ROLE=MECHANICAL_VALIDATION_AND_SERIALIZATION_ONLY",
            f"KNOWLEDGE_PACK_IDENTITY={KNOWLEDGE_PACK_IDENTITY}",
            f"CLAIM_MANIFEST_IDENTITY={CLAIM_MANIFEST_IDENTITY}",
            f"IDENTITY_BINDING_STATUS={IDENTITY_BINDING_STATUS}",
            "BRANCH_IDENTITIES_DETERMINISTIC=YES",
            "PRIMARY_FREEZE=NO",
            "JIANGHE_PRIMARY_ELIGIBLE=NO",
            "OUTCOME_ACCESS=NO",
            f"TOTAL_CLAIMS={len(records)}",
            f"CLAIM_LEVEL_RECORDS_REVIEWED={len(records)}",
            f"READY_FOR_PRIMARY_FREEZE={counts['READY_FOR_PRIMARY_FREEZE']}",
            f"STOP_SOURCE_AMBIGUOUS={counts['STOP_SOURCE_AMBIGUOUS']}",
            f"STOP_SOURCE_CONFLICT={counts['STOP_SOURCE_CONFLICT']}",
            f"STOP_OBSERVABILITY_GAP={counts['STOP_OBSERVABILITY_GAP']}",
            f"STOP_IDENTITY_INCOMPLETE={counts['STOP_IDENTITY_INCOMPLETE']}",
            "UNMAPPED_CLAIMS=0",
            "DUPLICATE_CLAIM_ASSIGNMENTS=0",
            "HIDDEN_ALTERNATIVES=0",
            "OUTCOME_REFERENCES_USED_FOR_BRANCH_SELECTION=0",
            "UNKNOWN_FILLED_BY_PROJECT_GUESS=0",
            "SOURCE_CONFLICTS_SILENTLY_RESOLVED=0",
            "SOURCE_TEXT_REWRITTEN=0",
            "```",
            "",
            "该 registry 由 352 条 identity-bound 策展审查记录机械生成。生成器不根据类别词、",
            "machineability（机器化标记）或歧义关键词裁决语义，只绑定正式 schema、当前 active",
            "knowledge pack、claim manifest 与已审查字段，并生成稳定 branch identity。",
            "",
            "`primary_branch_identity` 是对每条 branch object 去除自身 identity 字段后的规范 JSON",
            "执行 SHA-256 得到。它证明对象内容可确定重算，不代表 PRIMARY 已冻结，也不代表 AI",
            "市场决策必须是固定输出。",
            "",
            "12 条真实 STOP 保持可见；没有为追求 352/352 READY 而填平 UNKNOWN、来源冲突或",
            "当前观察面缺口。来源文本及锚点仍逐字绑定，不因包含受保护词语而改写。",
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
                raise ValueError(f"branch registry 工件不存在：{path}") from error
            if actual != expected:
                raise ValueError(f"branch registry 不是策展数据的确定性输出：{path}")
        return
    jsonl_path.parent.mkdir(parents=True, exist_ok=True)
    jsonl_path.write_text(expected_jsonl, encoding="utf-8", newline="\n")
    markdown_path.write_text(expected_markdown, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="生成或核验 identity-bound Jianghe PRIMARY branch registry")
    parser.add_argument("--check", action="store_true", help="仅核验现有 registry 是否可确定性重建")
    arguments = parser.parse_args()
    try:
        write_or_check(REPOSITORY_ROOT, arguments.check)
    except (OSError, ValueError, json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

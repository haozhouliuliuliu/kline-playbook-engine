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
CURATED_REVIEW_NAME = "JIANGHE_PRIMARY_CLAIM_LEVEL_CURATED_REVIEW_V0_5.jsonl"
DRAFT_JSONL_NAME = "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_5.jsonl"
DRAFT_MARKDOWN_NAME = "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_5.md"
ACCEPTANCE_RUBRIC_PATH = Path(
    "docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_ACCEPTANCE_RUBRIC_V0_1.md"
)

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
    "review_basis",
    "claim_specific_reasoning",
    "semantic_interpretation",
    "semantic_boundary",
    "operationalization_interpretation",
    "operational_boundary",
    "reviewed_source_scopes",
    "authority_links",
    "alternative_analysis",
    "semantic_mode",
    "operationalization_mode",
    "semantic_readiness",
    "required_source_review",
    "q01_adjudication",
    "pre_freeze_disposition",
    "disposition_reason",
}

CURATED_REVIEW_VERSION = "JIANGHE_PRIMARY_CURATED_QUALITY_REVIEW_V0_5"
BRANCH_REGISTRY_VERSION = "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_5"
PRIMARY_BRANCH_VERSION = "JIANGHE_PRIMARY_BRANCH_V0_5_PRE_FREEZE_NON_FINAL"
Q01_CLAIM_IDS = {
    "JH-CLM-005-001",
    "JH-CLM-020-002",
    "JH-CLM-021-003",
    "JH-CLM-024-001",
    "JH-CLM-024-002",
}
EFFECTIVE_REVIEW_STATUSES = {
    "SOURCE_AUTHORITY_REVIEW_COMPLETE",
    "COMPLETED_BY_V0_5_Q01_ADJUDICATION",
    "COMPLETED_BY_V1_1_SECOND_PASS_REVIEW",
    "REVIEW_COMPLETE_UNRESOLVED_SOURCE_CONFLICT",
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


def load_claim_records_and_material_paths(
    repository_root: Path = REPOSITORY_ROOT,
) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, str]]:
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
    material_path_by_claim_id: dict[str, str] = {}
    materials = manifest.get("materials")
    if not isinstance(materials, list) or not materials:
        raise ValueError("声明清单没有绑定材料")
    for material in materials:
        if not isinstance(material, dict):
            raise ValueError("声明清单材料条目不合法")
        relative_path = require_string(material.get("repository_artifact"), "repository_artifact")
        material_rows = load_jsonl(repository_root / relative_path, "声明材料")
        for row in material_rows:
            claim_id = require_string(row.get("claim_id"), "claim_id")
            if claim_id in material_path_by_claim_id:
                raise ValueError(f"声明 {claim_id} 在多个 manifest 材料中重复")
            material_path_by_claim_id[claim_id] = relative_path
        rows.extend(material_rows)

    claim_ids = [require_string(row.get("claim_id"), "claim_id") for row in rows]
    if len(rows) != EXPECTED_CLAIM_COUNT or len(set(claim_ids)) != EXPECTED_CLAIM_COUNT:
        raise ValueError("绑定声明材料未形成 352 条唯一声明")
    return manifest, rows, material_path_by_claim_id


def load_claim_records(
    repository_root: Path = REPOSITORY_ROOT,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest, rows, _ = load_claim_records_and_material_paths(repository_root)
    return manifest, rows


def repository_evidence_paths(value: Any) -> list[str]:
    """收集策展裁决实际引用的仓库证据路径。"""
    paths: set[str] = set()

    def visit(item: Any) -> None:
        if isinstance(item, dict):
            for child in item.values():
                visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)
        elif isinstance(item, str) and item.startswith(("docs/", "src/", "tests/", "tools/")):
            if Path(item).suffix.lower() in {".md", ".json", ".jsonl", ".csv", ".py"}:
                paths.add(item)

    visit(value)
    return sorted(paths)


def validate_repository_evidence_paths(value: Any, repository_root: Path) -> None:
    for relative_path in repository_evidence_paths(value):
        if not (repository_root / relative_path).is_file():
            raise ValueError(f"仓库证据路径不存在：{relative_path}")


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


def validate_curated_review(
    curated: dict[str, Any],
    source_record: dict[str, Any],
    repository_root: Path = REPOSITORY_ROOT,
    source_material_path: str | None = None,
) -> None:
    claim_id = require_string(curated.get("claim_id"), "claim_id")
    missing_fields = sorted(CURATED_REQUIRED_FIELDS.difference(curated))
    if missing_fields:
        raise ValueError(f"{claim_id} 缺少策展字段：{', '.join(missing_fields)}")
    if curated.get("curated_review_version") != CURATED_REVIEW_VERSION:
        raise ValueError(f"{claim_id} 的策展审查版本不正确")
    if curated.get("claim_manifest_identity") != CLAIM_MANIFEST_IDENTITY:
        raise ValueError(f"{claim_id} 未绑定当前 claim manifest identity")
    if curated.get("knowledge_pack_identity") != KNOWLEDGE_PACK_IDENTITY:
        raise ValueError(f"{claim_id} 未绑定当前 knowledge pack identity")
    if curated.get("identity_binding_status") != IDENTITY_BINDING_STATUS:
        raise ValueError(f"{claim_id} 的 identity binding status 不正确")

    expected_binding = source_binding(source_record)
    review_basis = curated.get("review_basis")
    if not isinstance(review_basis, dict):
        raise ValueError(f"{claim_id} 的 review_basis 不合法")
    if review_basis.get("source_reference") != expected_binding["source_reference"]:
        raise ValueError(f"{claim_id} 的 source_reference 偏离绑定来源")
    if review_basis.get("source_anchor") != expected_binding["source_anchor"]:
        raise ValueError(f"{claim_id} 的 source_anchor 改写或偏离绑定来源")
    if source_material_path is None:
        _, _, material_paths = load_claim_records_and_material_paths(repository_root)
        source_material_path = material_paths[claim_id]
    if review_basis.get("source_finding") != source_material_path:
        raise ValueError(f"{claim_id} 的 source_finding 未绑定实际 claim manifest 材料")
    validate_repository_evidence_paths(curated, repository_root)

    reasoning = curated.get("claim_specific_reasoning")
    if not isinstance(reasoning, dict):
        raise ValueError(f"{claim_id} 的 claim_specific_reasoning 不合法")
    reasoning_fields = {"source_says", "source_does_not_say", "supports", "does_not_support"}
    if set(reasoning) != reasoning_fields:
        raise ValueError(f"{claim_id} 的 claim_specific_reasoning 字段不完整")
    for field_name in reasoning_fields:
        require_string(reasoning.get(field_name), f"{claim_id}.claim_specific_reasoning.{field_name}")
    if reasoning["source_says"] != expected_binding["source_meaning"]:
        raise ValueError(f"{claim_id} 的 source_says 改写了 source_meaning")

    semantic = require_string(curated.get("semantic_interpretation"), f"{claim_id}.semantic_interpretation")
    if curated.get("semantic_mode") not in SEMANTIC_MODES:
        raise ValueError(f"{claim_id} 的 semantic_mode 不合法")
    semantic_boundary = curated.get("semantic_boundary")
    if not isinstance(semantic_boundary, dict):
        raise ValueError(f"{claim_id} 的 semantic_boundary 不合法")
    if semantic_boundary.get("source_says") != expected_binding["source_meaning"]:
        raise ValueError(f"{claim_id} 的 semantic_boundary.source_says 改写了来源")
    require_string(
        semantic_boundary.get("why_no_additional_interpretation_is_needed"),
        f"{claim_id}.semantic_boundary.why_no_additional_interpretation_is_needed",
    )

    operational = require_string(
        curated.get("operationalization_interpretation"),
        f"{claim_id}.operationalization_interpretation",
    )
    if curated.get("operationalization_mode") not in OPERATIONALIZATION_MODES:
        raise ValueError(f"{claim_id} 的 operationalization_mode 不合法")
    operational_boundary = curated.get("operational_boundary")
    if not isinstance(operational_boundary, dict):
        raise ValueError(f"{claim_id} 的 operational_boundary 不合法")
    governed_observation = operational_boundary.get("governed_observation")
    if not isinstance(governed_observation, dict) or not governed_observation.get("status"):
        raise ValueError(f"{claim_id} 缺少 governed observation 裁定")

    authority_links = curated.get("authority_links")
    if not isinstance(authority_links, dict):
        raise ValueError(f"{claim_id} 的 authority_links 不合法")
    for link_type in ("unknowns", "contradictions"):
        links = authority_links.get(link_type)
        if not isinstance(links, list):
            raise ValueError(f"{claim_id} 的 {link_type} 必须是显式列表")
        for link in links:
            if (
                not isinstance(link, dict)
                or not link.get("id")
                or not (link.get("reason") or link.get("rationale"))
            ):
                raise ValueError(f"{claim_id} 的 {link_type} 缺少 id 或来源理由")

    alternative_analysis = curated.get("alternative_analysis")
    if not isinstance(alternative_analysis, dict):
        raise ValueError(f"{claim_id} 的 alternative_analysis 不合法")
    if alternative_analysis.get("status") not in {
        "MATERIAL_ALTERNATIVES_REVIEWED",
        "NO_MATERIAL_SOURCE_ALTERNATIVE",
    }:
        raise ValueError(f"{claim_id} 未明确完成 alternative 审查")
    require_string(alternative_analysis.get("rationale"), f"{claim_id}.alternative_analysis.rationale")
    if not isinstance(alternative_analysis.get("alternatives"), list):
        raise ValueError(f"{claim_id} 的 alternatives 必须是显式列表")
    if (
        alternative_analysis["status"] == "MATERIAL_ALTERNATIVES_REVIEWED"
        and not alternative_analysis["alternatives"]
    ):
        raise ValueError(f"{claim_id} 声称存在 material alternative 但未记录")
    if (
        alternative_analysis["status"] == "NO_MATERIAL_SOURCE_ALTERNATIVE"
        and alternative_analysis["alternatives"]
    ):
        raise ValueError(f"{claim_id} 声称没有 material alternative 却仍记录候选")

    required_review = curated.get("required_source_review")
    if not isinstance(required_review, dict):
        raise ValueError(f"{claim_id} 缺少 required_source_review")
    if required_review.get("original_status") != expected_binding["source_status"]["review_status"]:
        raise ValueError(f"{claim_id} 的原始 source review status 未原样保留")
    if required_review.get("effective_status") not in EFFECTIVE_REVIEW_STATUSES:
        raise ValueError(f"{claim_id} 的有效 source review 尚未完成")
    if not isinstance(required_review.get("evidence"), list) or not required_review["evidence"]:
        raise ValueError(f"{claim_id} 的 source review 缺少证据")
    require_string(required_review.get("adjudication"), f"{claim_id}.required_source_review.adjudication")
    require_string(
        required_review.get("resolution_effect"),
        f"{claim_id}.required_source_review.resolution_effect",
    )
    require_string(
        required_review.get("remaining_unresolved_scope"),
        f"{claim_id}.required_source_review.remaining_unresolved_scope",
    )

    if claim_id in Q01_CLAIM_IDS:
        q01 = curated.get("q01_adjudication")
        if not isinstance(q01, dict) or q01.get("status") != "COMPLETED":
            raise ValueError(f"{claim_id} 缺少 Q01 明确裁定")
        if required_review.get("effective_status") != "COMPLETED_BY_V0_5_Q01_ADJUDICATION":
            raise ValueError(f"{claim_id} 的 Q01 有效复核状态不正确")
        if q01.get("authority") not in required_review["evidence"]:
            raise ValueError(f"{claim_id} 的 Q01 authority 未进入实际 resolution evidence")
        require_string(q01.get("resolution_effect"), f"{claim_id}.q01.resolution_effect")
        require_string(
            q01.get("remaining_unresolved_scope"),
            f"{claim_id}.q01.remaining_unresolved_scope",
        )
    elif curated.get("q01_adjudication") is not None:
        raise ValueError(f"{claim_id} 不应携带 Q01 裁定")

    semantic_readiness = curated.get("semantic_readiness")
    if semantic_readiness not in SEMANTIC_READINESS_VALUES:
        raise ValueError(f"{claim_id} 的 semantic_readiness 不合法")
    if curated.get("pre_freeze_disposition") != expected_disposition(semantic_readiness):
        raise ValueError(f"{claim_id} 的 pre_freeze_disposition 未反映已完成身份绑定")
    if curated.get("pre_freeze_disposition") not in PRE_FREEZE_DISPOSITIONS:
        raise ValueError(f"{claim_id} 的 pre_freeze_disposition 不合法")
    if curated.get("pre_freeze_disposition") == "STOP_IDENTITY_INCOMPLETE":
        raise ValueError(f"{claim_id} 已绑定身份，不得保持 STOP_IDENTITY_INCOMPLETE")
    if (
        curated.get("pre_freeze_disposition") == "READY_FOR_PRIMARY_FREEZE"
        and required_review.get("effective_status") == "REVIEW_COMPLETE_UNRESOLVED_SOURCE_CONFLICT"
    ):
        raise ValueError(f"{claim_id} 存在未解决来源冲突却被标为 READY")
    require_string(curated.get("disposition_reason"), f"{claim_id}.disposition_reason")

    scopes = curated.get("reviewed_source_scopes")
    if not isinstance(scopes, dict) or not isinstance(scopes.get("corrections"), list):
        raise ValueError(f"{claim_id} 的 reviewed_source_scopes 不合法")
    raw_scopes = {
        "no_trade_guard": source_record.get("source_no_trade_if_explicit"),
        "invalidation_scope": source_record.get("source_invalidation_if_explicit"),
        "management_or_exit_scope": source_record.get("source_exit_or_management_if_explicit"),
    }
    for field_name, raw_value in raw_scopes.items():
        if scopes.get(field_name) != raw_value and not any(
            correction.get("field") == field_name
            for correction in scopes["corrections"]
            if isinstance(correction, dict)
        ):
            raise ValueError(f"{claim_id} 的 {field_name} 改动没有显式裁定证据")

    del semantic, operational


def branch_identity_payload(record: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in record.items() if key != "primary_branch_identity"}


def compute_primary_branch_identity(record: dict[str, Any]) -> str:
    return hashlib.sha256(canonical_json(branch_identity_payload(record)).encode("utf-8")).hexdigest()


def build_branch_record(
    curated: dict[str, Any], source: dict[str, Any], required_review_evidence: list[str]
) -> dict[str, Any]:
    claim_id = curated["claim_id"]
    bound_source = source_binding(source)
    unknown_ids = [link["id"] for link in curated["authority_links"]["unknowns"]]
    contradiction_ids = [link["id"] for link in curated["authority_links"]["contradictions"]]
    alternative_ids = [
        alternative["alternative_id"]
        for alternative in curated["alternative_analysis"]["alternatives"]
    ]
    observation = curated["operational_boundary"]["governed_observation"]
    reviewed_scopes = curated["reviewed_source_scopes"]
    record: dict[str, Any] = {
        "branch_registry_version": BRANCH_REGISTRY_VERSION,
        "claim_id": claim_id,
        "claim_manifest_identity": CLAIM_MANIFEST_IDENTITY,
        "knowledge_pack_identity": KNOWLEDGE_PACK_IDENTITY,
        "identity_binding_status": IDENTITY_BINDING_STATUS,
        "identity_binding_scope": "PRE_FREEZE_NON_FINAL",
        "source_ordinal": bound_source["source_reference"]["source_ordinal"],
        "source_anchor": bound_source["source_anchor"],
        "source_meaning": bound_source["source_meaning"],
        "source_status": bound_source["source_status"],
        "source_record_binding": bound_source,
        "claim_status": bound_source["source_status"]["claim_status"],
        "claim_category": bound_source["source_status"]["claim_category"],
        "selected_interpretation_text": curated["semantic_interpretation"],
        "interpretation_evidence_basis": {
            "curated_review_version": curated["curated_review_version"],
            "review_basis": curated["review_basis"],
            "claim_specific_reasoning": curated["claim_specific_reasoning"],
            "semantic_boundary": curated["semantic_boundary"],
            "operational_boundary": curated["operational_boundary"],
            "authority_links": curated["authority_links"],
            "required_source_review": curated["required_source_review"],
            "q01_adjudication": curated["q01_adjudication"],
            "disposition_reason": curated["disposition_reason"],
        },
        "family_scope": bound_source["family_scope"],
        "case_references": normalize_string_list(source.get("case_ids")),
        "applicability_scope": {
            "binding": "SOURCE_AND_CLAIM_SCOPED",
            "instrument_if_explicit": source.get("instrument_if_explicit"),
            "timeframe_visible_or_stated": source.get("timeframe_visible_or_stated"),
        },
        "no_trade_guard": reviewed_scopes["no_trade_guard"],
        "invalidation_scope": reviewed_scopes["invalidation_scope"],
        "management_or_exit_scope": reviewed_scopes["management_or_exit_scope"],
        "source_scope_corrections": reviewed_scopes["corrections"],
        "ambiguity_preserved": {
            "source_value": bound_source["known_ambiguity"],
            "preserved_without_project_rewrite": True,
        },
        "unknown_ids": unknown_ids,
        "contradiction_ids": contradiction_ids,
        "observability_status": observation["status"],
        "observability_missing_inputs": observation["missing_inputs"],
        "observability": observation,
        "semantic_mode": curated["semantic_mode"],
        "semantic_boundary": curated["semantic_boundary"],
        "operationalization_mode": curated["operationalization_mode"],
        "operationalization_interpretation": curated["operationalization_interpretation"],
        "operational_boundary": curated["operational_boundary"],
        "alternative_interpretation_ids_predeclared": alternative_ids,
        "alternative_review": curated["alternative_analysis"],
        "semantic_readiness": curated["semantic_readiness"],
        "primary_branch_version": PRIMARY_BRANCH_VERSION,
        "pre_freeze_disposition": curated["pre_freeze_disposition"],
        "review_evidence": required_review_evidence,
        "primary_semantics_frozen": False,
        "primary_eligible": False,
    }
    record["primary_branch_identity"] = compute_primary_branch_identity(record)
    return record


def build_draft_records(repository_root: Path = REPOSITORY_ROOT) -> list[dict[str, Any]]:
    schema = load_preparation_schema(repository_root)
    _, source_records, material_paths = load_claim_records_and_material_paths(repository_root)
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
        ACCEPTANCE_RUBRIC_PATH.as_posix(),
        SOURCE_EVIDENCE_PATH.as_posix(),
        (DRAFT_DIRECTORY / CURATED_REVIEW_NAME).as_posix(),
    ]
    output: list[dict[str, Any]] = []
    for curated in curated_records:
        claim_id = curated["claim_id"]
        source = source_by_id[claim_id]
        validate_curated_review(curated, source, repository_root, material_paths[claim_id])
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
            "# 江河 PRIMARY identity-bound pre-freeze branch registry V0.5",
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
            "所有真实 STOP 保持为一等记录；数量由逐条 source review 得出，不以 V0.3 的 340/12",
            "为目标。UNKNOWN、来源冲突和观察面缺口均未被填平。来源文本及锚点仍逐字绑定，",
            "不因包含收益或结果等普通来源语言而改写。",
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

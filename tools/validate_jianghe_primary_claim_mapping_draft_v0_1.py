"""identity-bound Jianghe PRIMARY pre-freeze branch registry 的独立机械校验。"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import build_jianghe_primary_claim_mapping_draft_v0_1 as draft_builder


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
UNKNOWN_REGISTER_PATH = Path("docs/research/jianghe/JIANGHE_UNKNOWN_REGISTER_V1_1.md")
CONTRADICTION_REGISTER_PATH = Path("docs/research/jianghe/JIANGHE_CONTRADICTION_REGISTER_V1_1.md")

DISALLOWED_FIELD_NAMES = {
    "candidate",
    "outcome",
    "pnl",
    "performance",
    "validation",
    "final_holdout",
    "shadow",
    "broker",
    "real_money",
}
DISALLOWED_PROJECT_VALUE_TERMS = (
    "candidate outcome",
    "candidate-outcome",
    "validation data",
    "final holdout",
    "shadow result",
    "broker result",
    "real money",
    "selected by outcome",
    "按结果选择",
    "结果选优",
)


def find_disallowed_field_names(value: Any, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            if key.lower() in DISALLOWED_FIELD_NAMES:
                findings.append(child_path)
            findings.extend(find_disallowed_field_names(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_disallowed_field_names(child, f"{path}[{index}]"))
    return findings


def find_disallowed_project_terms(value: Any, path: str = "") -> list[str]:
    """只检查项目新增判断；绑定来源文本允许原样包含来源词语。"""
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            findings.extend(find_disallowed_project_terms(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_disallowed_project_terms(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        if any(term in lowered for term in DISALLOWED_PROJECT_VALUE_TERMS):
            findings.append(path)
    return findings


def load_register_rows(path: Path, id_prefix: str) -> dict[str, list[str]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ValueError(f"无法读取权威登记：{path}") from error
    rows: dict[str, list[str]] = {}
    for line in lines:
        if not line.startswith(f"| {id_prefix}"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 4:
            raise ValueError(f"权威登记行结构不合法：{line}")
        rows[cells[0]] = cells
    if not rows:
        raise ValueError(f"权威登记未找到 {id_prefix} 记录")
    return rows


def source_reference_contains(source_references: str, ordinal: str) -> bool:
    target = int(ordinal)
    for token in source_references.replace("–", "-").split(","):
        token = token.strip().removeprefix("V")
        if token.isdigit() and int(token) == target:
            return True
        match = re.fullmatch(r"(\d{1,3})-(\d{1,3})", token)
        if match and int(match.group(1)) <= target <= int(match.group(2)):
            return True
    return False


def contradiction_row_mentions_source(cells: list[str], ordinal: str) -> bool:
    return re.search(rf"\bV0*{int(ordinal)}\b", " ".join(cells), flags=re.IGNORECASE) is not None


def require_link_list(
    claim_id: str,
    source_ordinal: str,
    links: Any,
    authority_rows: dict[str, list[str]],
    check_source_reference: bool,
) -> list[str]:
    if not isinstance(links, list):
        raise ValueError(f"{claim_id} 的权威链接必须是列表")
    linked_ids: list[str] = []
    for link in links:
        if not isinstance(link, dict):
            raise ValueError(f"{claim_id} 的权威链接条目必须是对象")
        authority_id = draft_builder.require_string(link.get("id"), f"{claim_id}.authority_id")
        draft_builder.require_string(link.get("rationale"), f"{claim_id}.{authority_id}.rationale")
        if authority_id not in authority_rows:
            raise ValueError(f"{claim_id} 关联了不存在的权威编号 {authority_id}")
        if check_source_reference and not source_reference_contains(authority_rows[authority_id][3], source_ordinal):
            raise ValueError(f"{claim_id} 的来源 V{source_ordinal} 未被 {authority_id} 权威行列为相关来源")
        if not check_source_reference and not contradiction_row_mentions_source(
            authority_rows[authority_id], source_ordinal
        ):
            raise ValueError(f"{claim_id} 的来源 V{source_ordinal} 未被 {authority_id} 权威行引用")
        linked_ids.append(authority_id)
    if len(linked_ids) != len(set(linked_ids)):
        raise ValueError(f"{claim_id} 包含重复权威链接")
    return linked_ids


def validate_alternative_review(claim_id: str, review: Any) -> tuple[str, list[str]]:
    if not isinstance(review, dict):
        raise ValueError(f"{claim_id} 的 alternative_review 必须是对象")
    status = review.get("status")
    if status not in {"MATERIAL_ALTERNATIVES_REVIEWED", "NO_MATERIAL_SOURCE_ALTERNATIVE"}:
        raise ValueError(f"{claim_id} 的替代解释审查状态不合法")
    rationale = draft_builder.require_string(review.get("rationale"), f"{claim_id}.alternative_review.rationale")
    alternatives = review.get("alternatives")
    if not isinstance(alternatives, list):
        raise ValueError(f"{claim_id} 的 alternatives 必须是列表")
    if status == "MATERIAL_ALTERNATIVES_REVIEWED" and not alternatives:
        raise ValueError(f"{claim_id} 声称已审查替代解释但未记录候选")
    if status == "NO_MATERIAL_SOURCE_ALTERNATIVE" and alternatives:
        raise ValueError(f"{claim_id} 声称没有来源支持的替代解释却记录了候选")
    alternative_ids: list[str] = []
    for alternative in alternatives:
        if not isinstance(alternative, dict):
            raise ValueError(f"{claim_id} 的替代解释必须是对象")
        alternative_id = draft_builder.require_string(
            alternative.get("alternative_id"), f"{claim_id}.alternative_id"
        )
        draft_builder.require_string(alternative.get("interpretation"), f"{alternative_id}.interpretation")
        draft_builder.require_string(alternative.get("decision"), f"{alternative_id}.decision")
        draft_builder.require_string(alternative.get("reason"), f"{alternative_id}.reason")
        alternative_ids.append(alternative_id)
    if len(alternative_ids) != len(set(alternative_ids)):
        raise ValueError(f"{claim_id} 的替代解释编号重复")
    return rationale, alternative_ids


def validate(repository_root: Path = REPOSITORY_ROOT) -> dict[str, int | str]:
    schema = draft_builder.load_preparation_schema(repository_root)
    jsonl_path = repository_root / draft_builder.DRAFT_DIRECTORY / draft_builder.DRAFT_JSONL_NAME
    records = draft_builder.load_jsonl(jsonl_path, "identity-bound branch registry")
    curated_records = draft_builder.load_curated_reviews(repository_root)
    _, source_records = draft_builder.load_claim_records(repository_root)
    curated_by_id = {record["claim_id"]: record for record in curated_records}
    source_by_id = {record["claim_id"]: record for record in source_records}
    expected_ids = set(source_by_id)
    branch_ids = [record.get("claim_id") for record in records]

    if len(records) != draft_builder.EXPECTED_CLAIM_COUNT:
        raise ValueError("branch registry 记录数不是 352")
    if len(branch_ids) != len(set(branch_ids)):
        raise ValueError("branch registry 包含重复 claim_id")
    if set(branch_ids) != expected_ids:
        raise ValueError("branch registry 没有精确覆盖绑定 claim manifest")
    if branch_ids != sorted(branch_ids):
        raise ValueError("branch registry 没有按 claim_id 确定性排序")

    unknown_rows = load_register_rows(repository_root / UNKNOWN_REGISTER_PATH, "JH-UNK-")
    contradiction_rows = load_register_rows(repository_root / CONTRADICTION_REGISTER_PATH, "JH-CON-")
    disposition_counts: Counter[str] = Counter()
    alternative_statuses: Counter[str] = Counter()
    primary_branch_identities: set[str] = set()
    schema_required_fields = set(schema["required_branch_fields"])

    for record in records:
        claim_id = record["claim_id"]
        curated = curated_by_id[claim_id]
        source = source_by_id[claim_id]
        draft_builder.validate_curated_review(curated, source)
        missing_fields = sorted(schema_required_fields.difference(record))
        if missing_fields:
            raise ValueError(f"{claim_id} 缺少正式 branch 字段：{', '.join(missing_fields)}")

        if record.get("claim_manifest_identity") != draft_builder.CLAIM_MANIFEST_IDENTITY:
            raise ValueError(f"{claim_id} 未绑定当前 claim manifest identity")
        if record.get("knowledge_pack_identity") != draft_builder.KNOWLEDGE_PACK_IDENTITY:
            raise ValueError(f"{claim_id} 未绑定当前 knowledge pack identity")
        if record.get("identity_binding_status") != draft_builder.IDENTITY_BINDING_STATUS:
            raise ValueError(f"{claim_id} 的 identity binding status 不正确")
        if record.get("identity_binding_scope") != "PRE_FREEZE_NON_FINAL":
            raise ValueError(f"{claim_id} 未保持 PRE_FREEZE_NON_FINAL")
        serialized_record = draft_builder.canonical_json(record)
        if "PENDING_REBIND" in serialized_record:
            raise ValueError(f"{claim_id} 仍残留 PENDING_REBIND")
        if draft_builder.HISTORICAL_PRE_HYGIENE_IDENTITY in serialized_record:
            raise ValueError(f"{claim_id} 非法重用了历史 pre-hygiene identity")

        expected_source = draft_builder.source_binding(source)
        if record.get("source_meaning") != expected_source["source_meaning"]:
            raise ValueError(f"{claim_id} 改写了 source meaning")
        if record.get("source_anchor") != expected_source["source_anchor"]:
            raise ValueError(f"{claim_id} 改写了 source anchor")
        if record.get("source_ordinal") != expected_source["source_reference"]["source_ordinal"]:
            raise ValueError(f"{claim_id} 的 source ordinal 不正确")
        if record.get("source_status") != expected_source["source_status"]:
            raise ValueError(f"{claim_id} 改写了 source status")
        if record.get("source_record_binding") != expected_source:
            raise ValueError(f"{claim_id} 未完整保留原始 source binding")
        if record.get("selected_interpretation_text") != curated["semantic_interpretation"]:
            raise ValueError(f"{claim_id} 的 selected interpretation 未按策展记录绑定")
        if record.get("family_scope") != expected_source["family_scope"]:
            raise ValueError(f"{claim_id} 的 family scope 未按策展记录绑定")
        if record.get("semantic_mode") != curated["semantic_mode"]:
            raise ValueError(f"{claim_id} 的 semantic mode 未按策展记录绑定")
        if record.get("operationalization_mode") != curated["operationalization_mode"]:
            raise ValueError(f"{claim_id} 的 operationalization mode 未按策展记录绑定")

        disposition = record.get("pre_freeze_disposition")
        if disposition not in draft_builder.PRE_FREEZE_DISPOSITIONS:
            raise ValueError(f"{claim_id} 的 pre-freeze disposition 不合法")
        expected_disposition = draft_builder.expected_disposition(curated["semantic_readiness"])
        if disposition != expected_disposition:
            raise ValueError(f"{claim_id} 的 disposition 未正确反映 identity-bound 状态")
        disposition_counts[disposition] += 1
        if record.get("semantic_readiness") != curated["semantic_readiness"]:
            raise ValueError(f"{claim_id} 改写了 V0.2 semantic readiness")

        observability = curated["operational_boundary"].get("governed_observation")
        if record.get("observability_status") != observability.get("status"):
            raise ValueError(f"{claim_id} 的 observability status 未按策展记录绑定")
        if record.get("observability_missing_inputs") != observability.get("missing_inputs"):
            raise ValueError(f"{claim_id} 的 observability missing inputs 未按策展记录绑定")
        if observability.get("status") == "MISSING_CURRENT_OBSERVATION_INPUT" and disposition != "STOP_OBSERVABILITY_GAP":
            raise ValueError(f"{claim_id} 的 observability gap 未失败闭合")

        authority_links = curated.get("authority_links")
        if not isinstance(authority_links, dict):
            raise ValueError(f"{claim_id} 的 authority_links 必须是对象")
        ordinal = draft_builder.require_source_ordinal(source.get("source_ordinal"))
        unknown_ids = require_link_list(
            claim_id,
            ordinal,
            authority_links.get("unknowns"),
            unknown_rows,
            check_source_reference=True,
        )
        contradiction_ids = require_link_list(
            claim_id,
            ordinal,
            authority_links.get("contradictions"),
            contradiction_rows,
            check_source_reference=False,
        )
        if record.get("unknown_ids") != unknown_ids:
            raise ValueError(f"{claim_id} 的 UNKNOWN links 未按权威策展记录绑定")
        if record.get("contradiction_ids") != contradiction_ids:
            raise ValueError(f"{claim_id} 的 contradiction links 未按权威策展记录绑定")
        no_link_rationale = authority_links.get("no_link_rationale")
        if unknown_ids or contradiction_ids:
            if no_link_rationale is not None:
                raise ValueError(f"{claim_id} 有权威链接时不得声称无链接")
        else:
            draft_builder.require_string(no_link_rationale, f"{claim_id}.no_link_rationale")
        if contradiction_ids and disposition != "STOP_SOURCE_CONFLICT":
            raise ValueError(f"{claim_id} 关联来源矛盾却未失败闭合")
        source_conflict = (
            source.get("interpretation_status") == "SOURCE_INTERNAL_CONFLICT"
            or str(source.get("ambiguity_notes", "")).startswith("SOURCE_INTERNAL_")
        )
        if source_conflict and disposition != "STOP_SOURCE_CONFLICT":
            raise ValueError(f"{claim_id} 静默和解了来源内部冲突")
        if source.get("claim_status") == "UNKNOWN" and not contradiction_ids and disposition != "STOP_SOURCE_AMBIGUOUS":
            raise ValueError(f"{claim_id} 的来源 UNKNOWN 未按歧义失败闭合")

        alternative_rationale, alternative_ids = validate_alternative_review(
            claim_id, curated.get("alternative_analysis")
        )
        if record.get("alternative_review") != curated.get("alternative_analysis"):
            raise ValueError(f"{claim_id} 的替代解释审查未完整绑定")
        if record.get("alternative_interpretation_ids_predeclared") != alternative_ids:
            raise ValueError(f"{claim_id} 存在隐藏或漏报的 alternative interpretation")
        alternative_statuses[curated["alternative_analysis"]["status"]] += 1

        primary_identity = record.get("primary_branch_identity")
        if not isinstance(primary_identity, str) or len(primary_identity) != 64:
            raise ValueError(f"{claim_id} 缺少 deterministic primary branch identity")
        if primary_identity != draft_builder.compute_primary_branch_identity(record):
            raise ValueError(f"{claim_id} 的 primary branch identity 无法确定性重算")
        if primary_identity in primary_branch_identities:
            raise ValueError(f"{claim_id} 与其他 claim 共用了 primary branch identity")
        primary_branch_identities.add(primary_identity)
        if record.get("primary_semantics_frozen") is not False:
            raise ValueError(f"{claim_id} 非法宣称 PRIMARY 已冻结")
        if record.get("primary_eligible") is not False:
            raise ValueError(f"{claim_id} 非法宣称 PRIMARY eligible")

        disallowed_fields = find_disallowed_field_names(record)
        if disallowed_fields:
            raise ValueError(f"{claim_id} 包含禁止的项目结果字段：{', '.join(disallowed_fields)}")
        project_authored_surface = {
            "operationalization_interpretation": record["operationalization_interpretation"],
            "semantic_boundary": record["semantic_boundary"],
            "operational_boundary": record["operational_boundary"],
            "observability": record["observability"],
            "authority_links": authority_links,
            "alternative_review": record["alternative_review"],
            "claim_specific_reasoning": curated["claim_specific_reasoning"],
            "disposition_reason": curated["disposition_reason"],
        }
        disallowed_terms = find_disallowed_project_terms(project_authored_surface)
        if disallowed_terms:
            raise ValueError(f"{claim_id} 的项目判断依赖禁止结果面：{', '.join(disallowed_terms)}")

    if set(alternative_statuses) != {
        "MATERIAL_ALTERNATIVES_REVIEWED",
        "NO_MATERIAL_SOURCE_ALTERNATIVE",
    }:
        raise ValueError("替代解释审查被压成了单一统一默认值")
    if disposition_counts["STOP_IDENTITY_INCOMPLETE"] != 0:
        raise ValueError("identity binding 完成后仍存在 STOP_IDENTITY_INCOMPLETE")

    draft_builder.write_or_check(repository_root, check_only=True)
    return {
        "TOTAL_CLAIMS": len(records),
        "CLAIM_LEVEL_RECORDS_REVIEWED": len(records),
        "READY_FOR_PRIMARY_FREEZE": disposition_counts["READY_FOR_PRIMARY_FREEZE"],
        "STOP_SOURCE_AMBIGUOUS": disposition_counts["STOP_SOURCE_AMBIGUOUS"],
        "STOP_SOURCE_CONFLICT": disposition_counts["STOP_SOURCE_CONFLICT"],
        "STOP_OBSERVABILITY_GAP": disposition_counts["STOP_OBSERVABILITY_GAP"],
        "STOP_IDENTITY_INCOMPLETE": disposition_counts["STOP_IDENTITY_INCOMPLETE"],
        "KNOWLEDGE_PACK_IDENTITY_BOUND": "YES",
        "CLAIM_MANIFEST_IDENTITY_BOUND": "YES",
        "BRANCH_IDENTITIES_DETERMINISTIC": "YES",
        "UNMAPPED": 0,
        "UNMAPPED_CLAIMS": 0,
        "DUPLICATES": 0,
        "DUPLICATE_CLAIM_ASSIGNMENTS": 0,
        "HIDDEN_ALTERNATIVES": 0,
        "GUESSED_UNKNOWN": 0,
        "UNKNOWN_FILLED_BY_PROJECT_GUESS": 0,
        "SILENT_CONFLICT_RESOLUTION": 0,
        "SOURCE_CONFLICTS_SILENTLY_RESOLVED": 0,
        "OUTCOME_REFERENCES_USED_FOR_BRANCH_SELECTION": 0,
    }


def main() -> int:
    try:
        counts = validate()
    except (OSError, ValueError, json.JSONDecodeError, KeyError, TypeError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    print("PRIMARY_MAPPING_IDENTITY_BOUND_VALID=YES")
    for label, count in counts.items():
        print(f"{label}={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

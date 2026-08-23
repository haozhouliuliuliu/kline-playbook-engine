"""江河 PRIMARY 逐条策展数据与非最终草案的独立机械校验。"""

from __future__ import annotations

import hashlib
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

REQUIRED_DRAFT_FIELDS = {
    "draft_record_version",
    "claim_id",
    "claim_manifest_identity",
    "knowledge_pack_identity",
    "identity_binding_status",
    "identity_binding_scope",
    "identity_binding_reason",
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
    "primary_branch_version",
    "primary_branch_identity",
    "draft_record_identity",
}


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
    """只检查项目新增判断；绑定来源文本允许原样包含任意来源词语。"""
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


def validate_alternative_review(claim_id: str, review: Any) -> str:
    if not isinstance(review, dict):
        raise ValueError(f"{claim_id} 的 alternative_review 必须是对象")
    status = review.get("status")
    if status not in {"ALTERNATIVES_REVIEWED", "NO_SOURCE_JUSTIFIED_ALTERNATIVE_FOUND"}:
        raise ValueError(f"{claim_id} 的替代解释审查状态不合法")
    rationale = draft_builder.require_string(review.get("rationale"), f"{claim_id}.alternative_review.rationale")
    alternatives = review.get("alternatives")
    if not isinstance(alternatives, list):
        raise ValueError(f"{claim_id} 的 alternatives 必须是列表")
    if status == "ALTERNATIVES_REVIEWED" and not alternatives:
        raise ValueError(f"{claim_id} 声称已审查替代解释但未记录候选")
    if status == "NO_SOURCE_JUSTIFIED_ALTERNATIVE_FOUND" and alternatives:
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
    return rationale


def validate(repository_root: Path = REPOSITORY_ROOT) -> dict[str, int]:
    jsonl_path = repository_root / draft_builder.DRAFT_DIRECTORY / draft_builder.DRAFT_JSONL_NAME
    records = draft_builder.load_jsonl(jsonl_path, "映射草案")
    curated_records = draft_builder.load_curated_reviews(repository_root)
    _, source_records = draft_builder.load_claim_records(repository_root)
    curated_by_id = {record["claim_id"]: record for record in curated_records}
    source_by_id = {record["claim_id"]: record for record in source_records}
    expected_ids = set(source_by_id)
    draft_ids = [record.get("claim_id") for record in records]

    if len(records) != draft_builder.EXPECTED_CLAIM_COUNT:
        raise ValueError("映射草案记录数不是 352")
    if len(draft_ids) != len(set(draft_ids)):
        raise ValueError("映射草案包含重复 claim_id")
    if set(draft_ids) != expected_ids:
        raise ValueError("映射草案没有精确覆盖绑定 claim manifest")
    if draft_ids != sorted(draft_ids):
        raise ValueError("映射草案没有按 claim_id 确定性排序")

    unknown_rows = load_register_rows(repository_root / UNKNOWN_REGISTER_PATH, "JH-UNK-")
    contradiction_rows = load_register_rows(repository_root / CONTRADICTION_REGISTER_PATH, "JH-CON-")
    readiness_counts: Counter[str] = Counter()
    alternative_statuses: Counter[str] = Counter()
    alternative_rationales: set[str] = set()

    for record in records:
        claim_id = record["claim_id"]
        missing_fields = sorted(REQUIRED_DRAFT_FIELDS.difference(record))
        if missing_fields:
            raise ValueError(f"{claim_id} 缺少映射字段：{', '.join(missing_fields)}")
        curated = curated_by_id[claim_id]
        source = source_by_id[claim_id]
        draft_builder.validate_curated_review(curated, source)

        for field_name in (
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
        ):
            if record.get(field_name) != curated.get(field_name):
                raise ValueError(f"{claim_id} 的 {field_name} 未按策展记录机械绑定")

        if record.get("claim_manifest_identity") != draft_builder.CLAIM_MANIFEST_IDENTITY:
            raise ValueError(f"{claim_id} 的 claim manifest identity 不正确")
        if record.get("identity_binding_status") != "PENDING_REBIND":
            raise ValueError(f"{claim_id} 未保持 PENDING_REBIND")
        if record.get("identity_binding_scope") != "NON_FINAL":
            raise ValueError(f"{claim_id} 未保持 NON_FINAL")
        if record.get("knowledge_pack_identity") is not None:
            raise ValueError(f"{claim_id} 在重绑定前写入了 knowledge pack identity")
        if record.get("primary_branch_identity") is not None:
            raise ValueError(f"{claim_id} 在重绑定前写入了 final branch identity")
        if draft_builder.HISTORICAL_PRE_HYGIENE_IDENTITY in draft_builder.canonical_json(record):
            raise ValueError(f"{claim_id} 非法重用了历史 pre-hygiene identity")

        readiness = record.get("semantic_readiness")
        if readiness not in draft_builder.SEMANTIC_READINESS_VALUES:
            raise ValueError(f"{claim_id} 的 semantic_readiness 不合法")
        readiness_counts[readiness] += 1
        expected_disposition = (
            "STOP_IDENTITY_INCOMPLETE"
            if readiness == "SEMANTICALLY_READY_PRE_IDENTITY"
            else readiness
        )
        if record.get("pre_freeze_disposition") != expected_disposition:
            raise ValueError(f"{claim_id} 混淆了语义就绪与身份就绪处置")

        observability = record.get("observability")
        if not isinstance(observability, dict):
            raise ValueError(f"{claim_id} 的 observability 必须是对象")
        if observability.get("status") == "MISSING_CURRENT_OBSERVATION_INPUT" and readiness != "STOP_OBSERVABILITY_GAP":
            raise ValueError(f"{claim_id} 的可观察性缺口未失败闭合")

        authority_links = record.get("authority_links")
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
        no_link_rationale = authority_links.get("no_link_rationale")
        if unknown_ids or contradiction_ids:
            if no_link_rationale is not None:
                raise ValueError(f"{claim_id} 有权威链接时不得声称无链接")
        else:
            draft_builder.require_string(no_link_rationale, f"{claim_id}.no_link_rationale")
        if contradiction_ids and readiness != "STOP_SOURCE_CONFLICT":
            raise ValueError(f"{claim_id} 关联来源矛盾却未失败闭合")
        source_conflict = (
            source.get("interpretation_status") == "SOURCE_INTERNAL_CONFLICT"
            or str(source.get("ambiguity_notes", "")).startswith("SOURCE_INTERNAL_")
        )
        if source_conflict and readiness != "STOP_SOURCE_CONFLICT":
            raise ValueError(f"{claim_id} 静默和解了来源内部冲突")
        if source.get("claim_status") == "UNKNOWN" and not contradiction_ids and readiness != "STOP_SOURCE_AMBIGUOUS":
            raise ValueError(f"{claim_id} 的来源 UNKNOWN 未按歧义失败闭合")

        alternative_rationale = validate_alternative_review(claim_id, record.get("alternative_review"))
        alternative_statuses[record["alternative_review"]["status"]] += 1
        alternative_rationales.add(alternative_rationale)

        identity = record.get("draft_record_identity")
        if not isinstance(identity, str) or len(identity) != 64:
            raise ValueError(f"{claim_id} 缺少草案记录确定性身份")
        record_without_identity = dict(record)
        del record_without_identity["draft_record_identity"]
        expected_identity = hashlib.sha256(
            draft_builder.canonical_json(record_without_identity).encode("utf-8")
        ).hexdigest()
        if identity != expected_identity:
            raise ValueError(f"{claim_id} 的草案记录身份无法确定性重算")

        disallowed_fields = find_disallowed_field_names(record)
        if disallowed_fields:
            raise ValueError(f"{claim_id} 包含禁止的项目结果字段：{', '.join(disallowed_fields)}")
        project_authored_surface = {
            "semantic_interpretation": record["semantic_interpretation"],
            "operationalization_interpretation": record["operationalization_interpretation"],
            "observability": record["observability"],
            "authority_links": record["authority_links"],
            "alternative_review": record["alternative_review"],
            "review_rationale": record["review_rationale"],
        }
        disallowed_terms = find_disallowed_project_terms(project_authored_surface)
        if disallowed_terms:
            raise ValueError(f"{claim_id} 的项目判断依赖禁止结果面：{', '.join(disallowed_terms)}")

    if set(alternative_statuses) != {
        "ALTERNATIVES_REVIEWED",
        "NO_SOURCE_JUSTIFIED_ALTERNATIVE_FOUND",
    }:
        raise ValueError("替代解释审查被压成了单一统一默认值")
    if len(alternative_rationales) != draft_builder.EXPECTED_CLAIM_COUNT:
        raise ValueError("替代解释审查理由不是逐 claim 明确记录")

    draft_builder.write_or_check(repository_root, check_only=True)
    result = {name: readiness_counts[name] for name in sorted(draft_builder.SEMANTIC_READINESS_VALUES)}
    result["IDENTITY_PENDING_COUNT"] = sum(
        record["identity_binding_status"] == "PENDING_REBIND" for record in records
    )
    result["CURATED_CLAIMS"] = len(curated_records)
    return result


def main() -> int:
    try:
        counts = validate()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    print("PRIMARY_MAPPING_SEMANTIC_AUDIT_VALID=YES")
    for label, count in counts.items():
        print(f"{label}={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

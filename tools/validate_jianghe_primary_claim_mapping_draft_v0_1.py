"""江河非最终映射草案的独立机械校验。"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import build_jianghe_primary_claim_mapping_draft_v0_1 as draft_builder


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DISALLOWED_FIELD_NAMES = {
    "candidate",
    "outcome",
    "pnl",
    "performance",
    "validation",
    "shadow",
    "broker",
    "real_money",
}

DISALLOWED_VALUE_TERMS = (
    "p&l",
    "candidate outcome",
    "candidate-outcome",
    "project outcome",
    "outcome-test",
    "future result",
    "future-result",
    "未来结果",
)

REQUIRED_DRAFT_FIELDS = {
    "draft_record_version",
    "claim_id",
    "claim_manifest_identity",
    "knowledge_pack_identity",
    "identity_binding_status",
    "identity_binding_scope",
    "identity_binding_reason",
    "source",
    "source_meaning",
    "ai_interpretation_branch",
    "family_scope",
    "case_references",
    "applicability_scope",
    "no_trade_guard",
    "invalidation_scope",
    "management_or_exit_scope",
    "known_ambiguity",
    "unknown_preservation",
    "observability",
    "operationalization_mode",
    "alternative_interpretation_ids_predeclared",
    "alternative_review_status",
    "primary_branch_version",
    "primary_branch_identity",
    "pre_freeze_disposition",
    "review_evidence",
    "draft_record_identity",
}

REQUIRED_SOURCE_FIELDS = {
    "source_ordinal",
    "bvid",
    "source_anchor",
    "claim_status",
    "claim_category",
    "interpretation_status",
    "machineability",
    "review_status",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        raise ValueError(f"无法读取映射草案：{path}") from error
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"映射草案 JSONL 无法解析：{path}:{line_number}") from error
        if not isinstance(record, dict):
            raise ValueError(f"映射草案记录必须是对象：{path}:{line_number}")
        records.append(record)
    return records


def find_disallowed_field_names(value: Any, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            lower_key = key.lower()
            if lower_key in DISALLOWED_FIELD_NAMES:
                findings.append(child_path)
            findings.extend(find_disallowed_field_names(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_disallowed_field_names(child, f"{path}[{index}]"))
    return findings


def find_disallowed_value_terms(value: Any, path: str = "") -> list[str]:
    findings: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            findings.extend(find_disallowed_value_terms(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            findings.extend(find_disallowed_value_terms(child, f"{path}[{index}]"))
    elif isinstance(value, str):
        lowered = value.lower()
        if any(term in lowered for term in DISALLOWED_VALUE_TERMS):
            findings.append(path)
    return findings


def validate(repository_root: Path = REPOSITORY_ROOT) -> dict[str, int]:
    jsonl_path = repository_root / draft_builder.DRAFT_DIRECTORY / draft_builder.DRAFT_JSONL_NAME
    records = load_jsonl(jsonl_path)
    _, claim_records = draft_builder.load_claim_records(repository_root)
    source_records_by_id = {record["claim_id"]: record for record in claim_records}
    manifest_claim_ids = {record["claim_id"] for record in claim_records}
    draft_claim_ids = [record.get("claim_id") for record in records]

    if len(records) != draft_builder.EXPECTED_CLAIM_COUNT:
        raise ValueError("映射草案记录数不是 352")
    if len(draft_claim_ids) != len(set(draft_claim_ids)):
        raise ValueError("映射草案包含重复 claim_id")
    if set(draft_claim_ids) != manifest_claim_ids:
        raise ValueError("映射草案没有精确覆盖绑定的 claim manifest")

    sorted_claim_ids = sorted(draft_claim_ids)
    if draft_claim_ids != sorted_claim_ids:
        raise ValueError("映射草案序列化顺序不是按 claim_id 确定性排序")

    dispositions = Counter()
    for record in records:
        claim_id = record["claim_id"]
        missing_fields = sorted(REQUIRED_DRAFT_FIELDS.difference(record))
        if missing_fields:
            raise ValueError(f"{claim_id} 缺少映射字段：{', '.join(missing_fields)}")
        source = record.get("source")
        if not isinstance(source, dict):
            raise ValueError(f"{claim_id} 的 source 必须是对象")
        missing_source_fields = sorted(REQUIRED_SOURCE_FIELDS.difference(source))
        if missing_source_fields:
            raise ValueError(f"{claim_id} 缺少来源字段：{', '.join(missing_source_fields)}")
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

        disposition = record.get("pre_freeze_disposition")
        if disposition not in draft_builder.DISPOSITIONS:
            raise ValueError(f"{claim_id} 的 disposition 不在合法枚举中")
        dispositions[disposition] += 1
        original_source_record = source_records_by_id[claim_id]
        if draft_builder.has_source_conflict(original_source_record) and disposition != "STOP_SOURCE_CONFLICT":
            raise ValueError(f"{claim_id} 静默和解了来源冲突")
        if record.get("ai_interpretation_branch", {}).get("semantic_mode") not in draft_builder.SEMANTIC_MODES:
            raise ValueError(f"{claim_id} 的 semantic_mode 不在合法枚举中")
        if record.get("operationalization_mode") not in draft_builder.OPERATIONALIZATION_MODES:
            raise ValueError(f"{claim_id} 的 operationalization_mode 不在合法枚举中")

        unknown_preservation = record.get("unknown_preservation")
        if not isinstance(unknown_preservation, dict):
            raise ValueError(f"{claim_id} 缺少 UNKNOWN preservation")
        if unknown_preservation.get("project_authored_numeric_thresholds") != []:
            raise ValueError(f"{claim_id} 对 UNKNOWN 写入了项目数值阈值")
        if not isinstance(unknown_preservation.get("unknown_ids"), list):
            raise ValueError(f"{claim_id} 的 unknown_ids 必须是列表")
        if not isinstance(unknown_preservation.get("contradiction_ids"), list):
            raise ValueError(f"{claim_id} 的 contradiction_ids 必须是列表")
        if record.get("alternative_review_status") != "NO_UNDECLARED_PROJECT_ALTERNATIVE":
            raise ValueError(f"{claim_id} 的替代解释审查状态不合法")
        if record.get("alternative_interpretation_ids_predeclared") != []:
            raise ValueError(f"{claim_id} 不能在非最终草案中隐藏或追加未审查替代解释")

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
            raise ValueError(f"{claim_id} 包含禁止的结果字段：{', '.join(disallowed_fields)}")
        disallowed_values = find_disallowed_value_terms(record)
        if disallowed_values:
            raise ValueError(f"{claim_id} 包含禁止的结果语义：{', '.join(disallowed_values)}")

    draft_builder.write_or_check(repository_root, check_only=True)
    return {name: dispositions[name] for name in sorted(draft_builder.DISPOSITIONS)}


def main() -> int:
    try:
        counts = validate()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"错误：{error}", file=sys.stderr)
        return 1
    print("PRIMARY_MAPPING_DRAFT_VALID=YES")
    for disposition, count in counts.items():
        print(f"{disposition}={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

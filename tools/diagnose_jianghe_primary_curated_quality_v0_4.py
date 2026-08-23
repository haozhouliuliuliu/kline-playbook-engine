"""V0.4 curated review 的透明质量风险诊断；不裁决任何 claim 语义。"""

from __future__ import annotations

import inspect
import re
from collections import Counter
from pathlib import Path

import build_jianghe_primary_claim_mapping_draft_v0_1 as builder


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OLD_TEMPLATE_MARKERS = (
    "逐条核对 JH-CLM-",
    "按来源原意保留 JH-CLM-",
    "未用统一默认值代替审查",
    "已审查一个可能的过度精确化解释",
)
FORBIDDEN_SEMANTIC_DECIDERS = (
    "choose_semantic_mode",
    "has_category_token",
    "has_source_ambiguity",
    "has_source_conflict",
    "UNKNOWN_IDS_BY_CLAIM",
    "CONTRADICTION_IDS_BY_CLAIM",
    "sanitize_draft_text",
)


def diagnose(repository_root: Path = REPOSITORY_ROOT) -> dict[str, int | str]:
    records = builder.load_curated_reviews(repository_root)
    serialized_records = [builder.canonical_json(record) for record in records]
    template_marker_matches = sum(
        any(marker in serialized for marker in OLD_TEMPLATE_MARKERS)
        for serialized in serialized_records
    )
    wrapper_echoes = sum(
        bool(re.match(r"^按来源原意保留\s+JH-CLM-", record["semantic_interpretation"]))
        for record in records
    )
    blanket_alternatives = sum(
        record["alternative_analysis"]["status"]
        in {"NO_UNDECLARED_PROJECT_ALTERNATIVE", "NO_SOURCE_JUSTIFIED_ALTERNATIVE_FOUND"}
        for record in records
    )
    unresolved_ready = sum(
        record["pre_freeze_disposition"] == "READY_FOR_PRIMARY_FREEZE"
        and record["required_source_review"]["effective_status"]
        == "REVIEW_COMPLETE_UNRESOLVED_SOURCE_CONFLICT"
        for record in records
    )
    operation_counts = Counter(record["operationalization_interpretation"] for record in records)
    exact_operation_clusters = sum(count > 1 for count in operation_counts.values())
    max_operation_cluster = max(operation_counts.values(), default=0)
    builder_source = inspect.getsource(builder)
    semantic_deciders = sum(name in builder_source for name in FORBIDDEN_SEMANTIC_DECIDERS)

    return {
        "TOTAL_RECORDS_SCANNED": len(records),
        "OLD_TEMPLATE_MARKER_RECORDS": template_marker_matches,
        "SOURCE_WRAPPER_ECHOES": wrapper_echoes,
        "BLANKET_ALTERNATIVE_DEFAULTS": blanket_alternatives,
        "UNRESOLVED_REVIEW_PLUS_READY": unresolved_ready,
        "IDENTICAL_OPERATIONALIZATION_CLUSTERS": exact_operation_clusters,
        "MAX_IDENTICAL_OPERATIONALIZATION_CLUSTER": max_operation_cluster,
        "MECHANICAL_BUILDER_SEMANTIC_DECIDERS": semantic_deciders,
        "DIAGNOSTIC_ROLE": "RISK_DETECTION_ONLY_NO_SEMANTIC_DECISION",
    }


def main() -> int:
    for key, value in diagnose().items():
        print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

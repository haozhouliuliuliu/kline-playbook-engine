"""Generate CANONICAL_D01_D02_116_FAILURE_ROOT_CAUSE_REVIEW_V0_1.json.

Read-only: recomputes every cited aggregate from the accepted manifest, raw
files, and committed evidence, then writes the review JSON artifact.
"""
from __future__ import annotations

import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

DATA_ROOT = Path(r"C:/Users/H/Documents/kline-playbook-engine/data")
MANIFEST = DATA_ROOT / "canonical" / "manifest.json"
REV = Path("docs/evidence/CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json")
QUAL = Path("docs/evidence/CANONICAL_D01_D02_TARGETED_REPAIR_QUALIFICATION_V0_1.json")
UNIVERSE = Path("docs/evidence/CANONICAL_CONTRACT_UNIVERSE.json")
OUT = Path("docs/reviews/CANONICAL_D01_D02_116_FAILURE_ROOT_CAUSE_REVIEW_V0_1.json")
ZONE = ZoneInfo("Asia/Shanghai")


def chash(value) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parts = manifest["partitions"]
    rev = json.loads(REV.read_text(encoding="utf-8"))
    qual = json.loads(QUAL.read_text(encoding="utf-8"))
    universe = json.loads(UNIVERSE.read_text(encoding="utf-8"))
    ftd = {e["concrete_contract"]: e["first_trading_day"] for e in universe["contracts"]}
    fails = rev["failure_partitions"]
    diag = qual["diagnostics"]

    by_cc: dict[str, set[str]] = defaultdict(set)
    for p in parts:
        by_cc[p["contract"]].add(p["trading_day"])

    # per-failure structural flags
    per_failure = []
    for f in sorted(fails, key=lambda x: x["partition_identity"]):
        c, d = f["contract"], f["trading_day"]
        rs = datetime.fromisoformat(f["returned_start"])
        dd = next(x for x in diag if x["partition_identity"] == f["partition_identity"])
        per_failure.append({
            "partition_identity": f["partition_identity"],
            "contract": c,
            "product": dd["product"],
            "trading_day": d,
            "is_first_manifest_partition": d == min(by_cc[c]),
            "is_governed_first_trading_day": ftd.get(c) == d,
            "requested_start_is_prev_day_2100": f["requested_start"].endswith("T21:00:00+08:00"),
            "requested_start": f["requested_start"],
            "returned_start": f["returned_start"],
            "returned_start_in_night_window": (rs.hour >= 21 or rs.hour < 9),
            "missing_region_shape": dd["missing_region_shape"],
            "missing_session_class": dd["missing_session_class"],
            "missing_expected_bars": dd["missing_expected_bar_count"],
            "missing_regions": dd["missing_regions"],
        })

    truncated = [p for p in parts if p["returned_coverage_start"] != p["requested_coverage_start"]]
    truncated_non_first_day = [
        p for p in truncated
        if not (ftd.get(p["contract"]) == p["trading_day"] and p["trading_day"] == min(by_cc[p["contract"]]))
    ]
    req21_exact = sum(
        1 for p in parts
        if p["requested_coverage_start"].endswith("T21:00:00+08:00") and p["returned_coverage_start"] == p["requested_coverage_start"]
    )
    req21_trunc = sum(
        1 for p in parts
        if p["requested_coverage_start"].endswith("T21:00:00+08:00") and p["returned_coverage_start"] != p["requested_coverage_start"]
    )

    fail_keys = {(f["contract"], f["trading_day"]) for f in fails}
    old_q = dict(Counter(p["quality_status"] for p in parts if (p["contract"], p["trading_day"]) in fail_keys))

    clean_first = []
    for p in parts:
        c, d = p["contract"], p["trading_day"]
        if ftd.get(c) == d and d > "2024-01-02" and p["returned_coverage_start"] == p["requested_coverage_start"]:
            clean_first.append(c)

    # second partition cleanliness
    ok2 = 0
    for f in fails:
        c, d = f["contract"], f["trading_day"]
        days = sorted(by_cc[c])
        idx = days.index(d)
        if idx + 1 < len(days):
            d2 = days[idx + 1]
            p2 = next(p for p in parts if p["contract"] == c and p["trading_day"] == d2)
            ok2 += p2["returned_coverage_start"] == p2["requested_coverage_start"]

    result = {
        "schema_version": "canonical-d01-d02-116-failure-root-cause-review-v0.1",
        "review_date": "2026-08-21",
        "review_branch": "review/canonical-116-root-cause-v01",
        "baseline_evidence_commits": {
            "revalidate": "a9e306550c5dc47695e4c27c1812de4c3cad5641",
            "qualify": "e98df52a427a23c85fac70125a1f20dbd5f2a353",
        },
        "constraints": {
            "no_main_writes": True,
            "no_tqsdk_login": True,
            "no_redownload": True,
            "no_outcome_access": True,
        },
        "verdict": {
            "root_cause_verdict": "MIXED_ROOT_CAUSES",
            "primary": "PROVIDER_REPEATABLE_TRUNCATION",
            "secondary": [
                "LISTING_SESSION_AUTHORITY_DEFECT",
                "ACQUISITION_PLANNER_DEFECT",
            ],
        },
        "counts": {
            "failure_count": len(fails),
            "distinct_failed_contracts": len({f["contract"] for f in fails}),
            "distinct_failed_partition_keys": len({(f["contract"], f["trading_day"]) for f in fails}),
            "first_partition_failure_count": sum(1 for x in per_failure if x["is_first_manifest_partition"]),
            "first_listing_day_count": sum(1 for x in per_failure if x["is_governed_first_trading_day"]),
            "night_boundary_pattern_count": sum(1 for x in per_failure if x["requested_start_is_prev_day_2100"]),
            "truncated_partitions_total": len(truncated),
            "truncated_partitions_not_first_day": len(truncated_non_first_day),
            "requested_2100_exact_return": req21_exact,
            "requested_2100_truncated_return": req21_trunc,
            "clean_second_partition_for_failed_contracts": ok2,
            "clean_newly_listed_first_day_contracts": len(clean_first),
            "returned_start_in_night_window": sum(1 for x in per_failure if x["returned_start_in_night_window"]),
            "returned_start_at_or_after_day": sum(1 for x in per_failure if not x["returned_start_in_night_window"]),
            "missing_region_shape": dict(Counter(x["missing_region_shape"] for x in per_failure)),
            "missing_session_class": dict(Counter(x["missing_session_class"] for x in per_failure)),
            "failures_by_product": dict(sorted(Counter(x["product"] for x in per_failure).items())),
            "multiple_regions_by_product": dict(sorted(Counter(x["product"] for x in per_failure if x["missing_region_shape"] == "MULTIPLE_REGIONS").items())),
            "old_manifest_quality_status_of_failures": old_q,
        },
        "offset_distribution": {
            "distinct_minutes": len({(datetime.fromisoformat(f["returned_start"]) - datetime.fromisoformat(f["requested_start"])).total_seconds() // 60 for f in fails}),
            "min_minutes": min((datetime.fromisoformat(f["returned_start"]) - datetime.fromisoformat(f["requested_start"])).total_seconds() // 60 for f in fails),
            "max_minutes": max((datetime.fromisoformat(f["returned_start"]) - datetime.fromisoformat(f["requested_start"])).total_seconds() // 60 for f in fails),
            "lt300": sum(1 for f in fails if (datetime.fromisoformat(f["returned_start"]) - datetime.fromisoformat(f["requested_start"])).total_seconds() // 60 < 300),
            "range300_900": sum(1 for f in fails if 300 <= (datetime.fromisoformat(f["returned_start"]) - datetime.fromisoformat(f["requested_start"])).total_seconds() // 60 < 900),
            "ge900": sum(1 for f in fails if (datetime.fromisoformat(f["returned_start"]) - datetime.fromisoformat(f["requested_start"])).total_seconds() // 60 >= 900),
        },
        "hypothesis_evaluation": {
            "RANDOM_ACQUISITION_TRUNCATION": "REJECTED",
            "PROVIDER_FIXED_TRUNCATION": "PARTIAL_PROVIDER_SIDE_BUT_RAGGED_NOT_FIXED",
            "LISTING_BOUNDARY_ALONE": "PARTIAL_CONTEXT_NOT_SUFFICIENT",
            "LISTING_SESSION_AUTHORITY_DEFECT": "PARTIAL_REAL_SECONDARY_DEFECT",
            "ACQUISITION_PLANNER_DEFECT": "PARTIAL_REAL_SECONDARY_DEFECT",
        },
        "code_defects": [
            {
                "id": "ROOTCAUSE-1",
                "file": "src/metadata_authority.py",
                "symbol": "session_windows_for_trading_day",
                "severity": "HIGH",
                "description": "No listing-boundary (first_trading_day) awareness; unconditionally emits the first trading day's preceding-night window.",
                "fix_requirement": "Accept a governed listing/effective-start boundary and suppress the night window for any trading day whose preceding-night session falls before the contract's effective start.",
            },
            {
                "id": "ROOTCAUSE-2",
                "file": "tools/build_canonical_dataset.py",
                "symbol": "build_contract_configs",
                "severity": "HIGH",
                "description": "Builds SessionMetadata over the full spec effective period (2024-01-01..2025-12-31), not the contract's governed first_trading_day..last_trading_day; pre-listing windows enter the metadata identity.",
                "fix_requirement": "Pass the governed universe bounds into build_session_metadata so session windows respect the contract's listing window.",
            },
            {
                "id": "ROOTCAUSE-3",
                "file": "tools/build_canonical_dataset.py",
                "symbol": "build_requests",
                "severity": "HIGH",
                "description": "No first-trading-day handling; requests prev 21:00 -> day 15:00 for the first trading day unconditionally.",
                "fix_requirement": "For the contract's first trading day, either request day-session-only (09:00-15:00) or bind first-night existence to verified authority before requesting it.",
            },
            {
                "id": "ROOTCAUSE-4",
                "file": "src/historical_acquisition.py",
                "symbol": "DatasetBuilder._acquire_partition (historical)",
                "severity": "CRITICAL",
                "description": "Old acquisition builder masked truncation as PASS for all 116 first-day partitions; repaired _acquire_partition now flags returned_coverage_truncated but the accepted corpus still holds the masked records.",
                "fix_requirement": "Governance action: re-classify the 116 accepted partitions or re-acquire under corrected scope; never re-introduce PASS masking.",
            },
        ],
        "critical_findings": [
            "All 116 failures are the contract's first manifest partition on the governed first trading day; zero regular-day partitions are truncated (0/31980 at 21:00 requests).",
            "The provider's stored historical data for these first trading days is incomplete (ragged, product-clustered, including day-session gaps e.g. al2501 missing 09:00-10:44, ni2511 = 1 bar); no planner or authority change can recover day-session data the provider does not store.",
        ],
        "high_findings": [
            "28 newly-listed contracts have clean first trading days, so first-day truncation is not universal and not a fixed listing rule.",
            "Truncation and clean first days are fully interleaved in acquisition time (retrospective 2026-08-16/17), ruling out network/batch artifacts; re-download is inferred to reproduce the truncation.",
            "29 MULTIPLE_REGIONS failures (ni:15, al:8, cu:5, rb:1) have the entire first night session and part of the first day session absent; au/ag have no such cases.",
            "Old manifest recorded all 116 failures as PASS (truncation masked), and the session authority/planner lack listing-boundary awareness (over-generated first-day night expected coverage).",
        ],
        "recommended_repair": "RE_AUTHORIZE_TARGETED_REACQUISITION_WITH_FIRST_DAY_SCOPE_OR_GOVERNED_EXCEPTION",
        "per_failure": per_failure,
        "review_identity": None,  # filled below
    }
    result["review_identity"] = chash(result)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    print(f"review_identity={result['review_identity']}")


if __name__ == "__main__":
    main()

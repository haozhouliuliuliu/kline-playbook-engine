"""Final comprehensive verification for the 116-failure root-cause review.

Read-only. Emits a deterministic evidence table used by the review document.
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
ZONE = ZoneInfo("Asia/Shanghai")


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parts = manifest["partitions"]
    rev = json.loads(REV.read_text(encoding="utf-8"))
    qual = json.loads(QUAL.read_text(encoding="utf-8"))
    universe = json.loads(UNIVERSE.read_text(encoding="utf-8"))
    ftd = {e["concrete_contract"]: e["first_trading_day"] for e in universe["contracts"]}
    fails = rev["failure_partitions"]
    diag = qual["diagnostics"]

    print("=== A. Manifest inventory ===")
    print(f"total partitions: {len(parts)}")
    by_cc = defaultdict(set)
    for p in parts:
        by_cc[p["contract"]].add(p["trading_day"])
    dup = sum(1 for c, days in by_cc.items() if len(days) != sum(1 for p in parts if p["contract"] == c))
    print(f"contracts with duplicate trading-day partitions: {dup}")
    print(f"distinct contracts in manifest: {len(by_cc)}")

    print("\n=== B. Failure set identity ===")
    print(f"failure_partitions count: {len(fails)}")
    print(f"distinct failed contracts: {len(set(f['contract'] for f in fails))}")
    print(f"distinct failed (contract,trading_day): {len(set((f['contract'], f['trading_day']) for f in fails))}")

    print("\n=== C. Per-failure structural checks ===")
    first_manifest = 0
    ftd_match = 0
    req_21 = 0
    for f in fails:
        c, d = f["contract"], f["trading_day"]
        first_manifest += d == min(by_cc[c])
        ftd_match += ftd.get(c) == d
        req_21 += f["requested_start"].endswith("T21:00:00+08:00")
    print(f"failure == first manifest partition: {first_manifest}/{len(fails)}")
    print(f"failure == governed first trading day: {ftd_match}/{len(fails)}")
    print(f"failure requested_start == prev-day 21:00: {req_21}/{len(fails)}")

    print("\n=== D. All truncated partitions (any day) ===")
    truncated = [p for p in parts if p["returned_coverage_start"] != p["requested_coverage_start"]]
    print(f"all partitions with returned_start != requested_start: {len(truncated)}")
    truncated_non_first = [
        p for p in truncated
        if not (ftd.get(p["contract"]) == p["trading_day"] and p["trading_day"] == min(by_cc[p["contract"]]))
    ]
    print(f"  of those, NOT (first manifest partition AND first trading day): {len(truncated_non_first)}")
    req21_exact = sum(1 for p in parts if p["requested_coverage_start"].endswith("T21:00:00+08:00") and p["returned_coverage_start"] == p["requested_coverage_start"])
    req21_trunc = sum(1 for p in parts if p["requested_coverage_start"].endswith("T21:00:00+08:00") and p["returned_coverage_start"] != p["requested_coverage_start"])
    print(f"requested at 21:00 -> exact return: {req21_exact}, truncated return: {req21_trunc}")

    print("\n=== E. Missing-region / session classes ===")
    print(f"missing_region_shape: {dict(Counter(dd['missing_region_shape'] for dd in diag))}")
    print(f"missing_session_class: {dict(Counter(dd['missing_session_class'] for dd in diag))}")
    print(f"session_class: {dict(Counter(dd['session_class'] for dd in diag))}")
    print(f"truncation_shape: {dict(Counter(dd['truncation_shape'] for dd in diag))}")
    print(f"listing coverage: {dict(Counter(dd['listing_effective_coverage'] for dd in diag))}")
    print(f"missing_starts_at_requested_boundary: {dict(Counter(dd['missing_starts_at_requested_boundary'] for dd in diag))}")

    print("\n=== F. By product ===")
    by_prod = Counter(dd["product"] for dd in diag)
    by_prod_multi = Counter(dd["product"] for dd in diag if dd["missing_region_shape"] == "MULTIPLE_REGIONS")
    print(f"failures by product: {dict(sorted(by_prod.items()))}")
    print(f"MULTIPLE_REGIONS by product: {dict(sorted(by_prod_multi.items()))}")

    print("\n=== G. Returned-start offsets ===")
    offsets = []
    for f in fails:
        rs = datetime.fromisoformat(f["returned_start"])
        rq = datetime.fromisoformat(f["requested_start"])
        offsets.append(int((rs - rq).total_seconds() // 60))
    print(f"distinct offset values: {len(set(offsets))}")
    print(f"offset min/max minutes: {min(offsets)} / {max(offsets)}")
    print(f"offsets < 300: {sum(1 for o in offsets if o < 300)}")
    print(f"offsets 300..900: {sum(1 for o in offsets if 300 <= o < 900)}")
    print(f"offsets >= 900: {sum(1 for o in offsets if o >= 900)}")

    print("\n=== H. Night-bar presence in raw ===")
    # night bar presence is a per-contract property of raw data; approximate from returned_start
    ret_during_night = 0
    for f in fails:
        rs = datetime.fromisoformat(f["returned_start"])
        if rs.hour >= 21 or rs.hour < 9:
            ret_during_night += 1
    print(f"returned_start within night window (hour>=21 or <9): {ret_during_night}")
    print(f"returned_start at/after day 09:00: {len(fails) - ret_during_night}")

    print("\n=== I. Clean newly-listed first-day partitions ===")
    clean = 0
    clean_list = []
    for p in parts:
        c, d = p["contract"], p["trading_day"]
        if ftd.get(c) == d and d > "2024-01-02" and p["returned_coverage_start"] == p["requested_coverage_start"]:
            clean += 1
            clean_list.append(c)
    print(f"clean newly-listed first-day partitions (returned==requested): {clean}")
    print(f"clean contracts: {sorted(clean_list)}")

    print("\n=== J. Old-manifest quality of failures ===")
    fail_keys = {(f["contract"], f["trading_day"]) for f in fails}
    old_q = Counter(p["quality_status"] for p in parts if (p["contract"], p["trading_day"]) in fail_keys)
    print(f"old manifest quality_status for the 116 failures: {dict(old_q)}")

    print("\n=== K. Second partition of failed contracts ===")
    ok2 = 0
    for f in fails:
        c, d = f["contract"], f["trading_day"]
        days = sorted(by_cc[c])
        idx = days.index(d)
        if idx + 1 >= len(days):
            continue
        d2 = days[idx + 1]
        p2 = next(p for p in parts if p["contract"] == c and p["trading_day"] == d2)
        if p2["returned_coverage_start"] == p2["requested_coverage_start"]:
            ok2 += 1
    print(f"failed contracts with clean 2nd trading-day partition: {ok2}/{len(fails)}")

    print("\n=== L. Session authority windows for a first trading day ===")
    dd = next(x for x in diag if x["contract"] == "SHFE.cu2504")
    print("cu2504 current_session_windows:")
    for w in dd["current_session_windows"]:
        print(f"   {w['session_class']} {w['start']} .. {w['end']} (trading_day={w['trading_day']})")


if __name__ == "__main__":
    main()

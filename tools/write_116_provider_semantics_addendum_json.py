"""Generate CANONICAL_D01_D02_116_FAILURE_PROVIDER_SEMANTICS_ADDENDUM_V0_1.json.

Deterministic companion to the addendum markdown. Read-only; writes only the
review addendum JSON artifact.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

OUT = Path("docs/reviews/CANONICAL_D01_D02_116_FAILURE_PROVIDER_SEMANTICS_ADDENDUM_V0_1.json")


def chash(value) -> str:
    return hashlib.sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def main() -> None:
    result = {
        "schema_version": "canonical-d01-d02-116-failure-provider-semantics-addendum-v0.1",
        "review_date": "2026-08-21",
        "review_branch": "review/canonical-116-root-cause-v01",
        "supersedes": None,
        "scope": "TqSdk official/first-party materials only",
        "constraints": {
            "no_main_writes": True,
            "no_tqsdk_login": True,
            "no_install": True,
            "no_download": True,
            "no_32980_recompute": True,
            "no_candidate_outcome_research": True,
        },
        "evidence_sources": [
            {"id": "DOC-INTRO", "url": "https://doc.shinnytech.com/tqsdk/latest/intro.html"},
            {"id": "DOC-MDDATAS", "url": "https://doc.shinnytech.com/tqsdk/latest/usage/mddatas.html"},
            {"id": "DOC-API", "url": "https://doc.shinnytech.com/tqsdk/latest/reference/tqsdk.api.html"},
            {"id": "DOC-DOWNLOAD", "url": "https://doc.shinnytech.com/tqsdk/latest/reference/tqsdk.tools.download.html"},
            {"id": "SRC-API", "url": "https://github.com/shinnytech/tqsdk-python/tree/master/tqsdk/api.py"},
            {"id": "SRC-DATA_SERIES", "url": "https://github.com/shinnytech/tqsdk-python/tree/master/tqsdk/data_series.py"},
            {"id": "SRC-DEMO-VWAP", "url": "https://github.com/shinnytech/tqsdk-python/tree/master/tqsdk/demo/example/vwap.py"},
        ],
        "official_evidence_base": [
            {
                "id": "E1",
                "statement": "TqSdk provides all tick/K-line data '从上市开始' (from listing) for all currently tradable contracts.",
                "source": "DOC-INTRO",
            },
            {
                "id": "E2",
                "statement": "Non-trading periods produce no K-line bars (e.g. cu1805 13:00-13:30 not trading -> its K-line data in that period is skipped).",
                "source": "DOC-DOWNLOAD",
            },
            {
                "id": "E3",
                "statement": "When a contract has no data at a time, that bar is skipped and K-lines can be non-continuous.",
                "source": "DOC-MDDATAS / SRC-API",
            },
            {
                "id": "E4",
                "statement": "get_kline_data_series returns only the bars the server stores within [start_dt, end_dt); download pages by K-line id without synthesizing missing minutes.",
                "source": "SRC-DATA_SERIES / SRC-API",
            },
            {
                "id": "E5",
                "statement": "Official example explicitly handles days whose trading-time slots are not fully filled (bars can be missing for parts of a period).",
                "source": "SRC-DEMO-VWAP",
            },
        ],
        "answers": {
            "Q1_zero_volume_bars_before_first_trade": {
                "verdict": "PARTIAL_OFFICIAL_STRONG_INFERENCE",
                "summary": "Official docs do not verbatim-state the first-session boundary; official semantics (E1/E2/E3/E4) imply the series starts at the first available bar and emits no bars before it. Observed corpus (cu2504 night from 21:11 vol=1, zero-volume bars only after) is consistent.",
            },
            "Q2_returned_start_later_than_requested_start": {
                "verdict": "OFFICIALLY_SUPPORTED",
                "summary": "Direct consequence of E2 + E4 + E1: no-trade periods produce no bars, data starts from listing, and the API returns only stored bars in the range; a newly listed contract with a late first trade has returned_start later than requested_start.",
            },
            "Q3_bar_every_minute_guarantee": {
                "verdict": "NO_OFFICIALLY_SUPPORTED",
                "summary": "E2 (skip on no trade), E3 (non-continuous K-lines), E5 (missing time slots) together show TqSdk does not guarantee a bar per minute.",
            },
            "Q4_range_vs_availability_semantics": {
                "verdict": "OFFICIALLY_DOCUMENTED_FILTER_SEMANTICS",
                "summary": "start_dt/end_dt define a filter window; the API returns the provider's stored bars inside it; full population is not guaranteed.",
            },
            "Q5_no_bars_before_listing_first_trade": {
                "verdict": "OFFICIALLY_SUPPORTED",
                "summary": "E1 ('从上市开始' - from listing) plus E2/E3: historical series has no bars before listing/first trade.",
            },
        },
        "original_phrase_refinement": {
            "original": "provider data is incomplete/truncated (PROVIDER_REPEATABLE_TRUNCATION)",
            "refined": "NO_BAR_BEFORE_FIRST_AVAILABLE_TRADE",
            "rationale": "Official TqSdk semantics (E1/E2/E3/E4) say no-trade/no-listing periods have no bars and the series starts at the first available bar; leading missing minutes are absent by design, not lost or randomly truncated.",
            "rejected_candidates": {
                "PROVIDER_DATA_INCOMPLETE": "implies data loss the official semantics do not support",
                "UNRESOLVED_PROVIDER_AVAILABILITY_SEMANTICS": "used only as a residual note for the exact first-session leading-edge rule",
            },
        },
        "original_verdict_impact": {
            "verdict": "NO_CONFLICT",
            "detail": "MIXED_ROOT_CAUSES stands; primary component re-characterized as NO_BAR_BEFORE_FIRST_AVAILABLE_TRADE; secondary listing-boundary authority/planner findings are reinforced.",
        },
        "residual_gap": "INSUFFICIENT_OFFICIAL_EVIDENCE for the verbatim mechanism of the first-session leading edge only; overall semantic direction is unambiguous.",
        "recommended_repair": "UNCHANGED - re-request reproduces leading-absent bars; re-scope first-day expected coverage or use another authoritative source for genuinely-traded leading minutes.",
        "review_identity": None,
    }
    result["review_identity"] = chash(result)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    print(f"review_identity={result['review_identity']}")


if __name__ == "__main__":
    main()

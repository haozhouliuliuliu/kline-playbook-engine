"""Write deterministic Path-C evidence from the completed provider probe."""

from __future__ import annotations

import json
from pathlib import Path


PROBE_PATH = Path("docs/evidence/CANONICAL_FIRST_DAY_PROVIDER_PROBE_V0_1.json")
JSON_OUTPUT = Path("docs/evidence/CANONICAL_FIRST_DAY_SCOPE_ADJUDICATION_V0_1.json")
MARKDOWN_OUTPUT = Path("docs/evidence/CANONICAL_FIRST_DAY_SCOPE_ADJUDICATION_V0_1.md")
ROOT_CAUSE_REVIEW_COMMIT = "2f49603fe5dafb4bd8293ba817db8291df6faba8"
PROVIDER_SEMANTICS_ADDENDUM_COMMIT = "d9f685fa604515509093e764652948df76b055d6"
PROVIDER_SEMANTICS_ADDENDUM_IDENTITY = "4250d993048c12f019be9735c4fb14edf15872afda2932792f7340b104c9fa8d"


def build_adjudication(probe: dict) -> dict:
    if probe.get("result") != "FIRST_DAY_PROVIDER_DATA_UNAVAILABLE":
        raise ValueError("scope adjudication requires the completed Path-C provider probe")
    totals = probe.get("totals")
    if not isinstance(totals, dict):
        raise ValueError("probe totals are required")
    required = {
        "ORIGINAL_REQUEST_REPEATABLE_TRUNCATION": 6,
        "DAY_ONLY_COMPLETE": 3,
        "DAY_ONLY_STILL_TRUNCATED": 3,
        "OVERLAPPING_OHLC_MISMATCH_COUNT": 0,
    }
    if any(totals.get(key) != value for key, value in required.items()):
        raise ValueError("probe totals do not support the recorded Path-C adjudication")
    return {
        "schema_version": "canonical-first-day-scope-adjudication-v0.1",
        "source_evidence": {
            "provider_probe": str(PROBE_PATH).replace("\\", "/"),
            "root_cause_review_commit": ROOT_CAUSE_REVIEW_COMMIT,
            "provider_semantics_addendum_commit": PROVIDER_SEMANTICS_ADDENDUM_COMMIT,
            "provider_semantics_addendum_identity": PROVIDER_SEMANTICS_ADDENDUM_IDENTITY,
        },
        "live_probe_facts": {
            "selected_targets": probe["selected_target_count"],
            "original_request_repeatable_truncation": totals["ORIGINAL_REQUEST_REPEATABLE_TRUNCATION"],
            "day_only_complete": totals["DAY_ONLY_COMPLETE"],
            "day_only_still_truncated": totals["DAY_ONLY_STILL_TRUNCATED"],
            "overlapping_ohlc_values_compared": totals["OVERLAPPING_OHLC_VALUES_COMPARED"],
            "overlapping_ohlc_mismatch_count": totals["OVERLAPPING_OHLC_MISMATCH_COUNT"],
        },
        "case_adjudication": {
            "CASE_A": "TqSdk official semantics support no bars before the first available bar, but do not independently establish each contract's first available minute.",
            "CASE_B": "The live provider probe repeats the original leading gaps and, for three severe representatives, cannot supply complete day-session bars even for a day-only request.",
            "CASE_C": "Current SessionMetadata expects scheduled session minutes; CANONICAL_CONTRACT_UNIVERSE first_trading_day is a date and does not express a contract-specific intraday trading start.",
        },
        "production_defect_adjudication": {
            "contract_config_session_scope": "FIXED_TO_GOVERNED_CONCRETE_LISTING_BOUNDS",
            "first_day_night_session_rule": "AUTHORITY_GAP_NO_AUTOMATIC_CHANGE",
            "first_day_request_planner_rule": "AUTHORITY_GAP_NO_AUTOMATIC_CHANGE",
            "legacy_session_identity": "EXPLICIT_REVALIDATION_REQUIRED_NO_AUTOMATIC_MIGRATION",
        },
        "result": "CANONICAL_FIRST_DAY_AVAILABILITY_AUTHORITY_UNRESOLVED",
        "targeted_116_reacquisition_permitted": False,
        "repaired_corpus_materialization_permitted": False,
        "d02_non_laundering": "Provider observed/returned coverage is not used to shorten expected coverage or create PASS.",
        "historical_accepted_corpus_modified": False,
        "outcome_access_used": False,
    }


def main() -> None:
    probe = json.loads(PROBE_PATH.read_text(encoding="utf-8"))
    evidence = build_adjudication(probe)
    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MARKDOWN_OUTPUT.write_text("\n".join([
        "# Canonical first-day scope adjudication v0.1", "",
        f"- RESULT: `{evidence['result']}`",
        "- 116 targeted reacquisition: `NOT_PERMITTED`",
        "- repaired corpus materialization: `NOT_PERMITTED`",
        "- D02: provider observations do not shorten expected coverage.", "",
    ]), encoding="utf-8")


if __name__ == "__main__":
    main()

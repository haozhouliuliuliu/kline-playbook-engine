"""Verify the E07 source-governed mapping machinery (API-independent prep).

Produces ``docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_PREP_V0_1.json``
deterministically.

Guarantees of this tool:
  - NO login, NO network access, NO outcome data, NO TqSdk import;
  - implements NO TqSdk decode adapter (``BLOCKED_API_CONTRACT_NOT_PINNED``);
  - the demo records are synthetic fixtures that exercise the machinery only;
    they are NOT candidate mapping authority and are never applied to any corpus.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from src.source_governed_mapping import (
    BLOCKED_API_CONTRACT_NOT_PINNED,
    MappingConflictError,
    MappingProvenance,
    MappingSubstitutionForbidden,
    MappingUnavailableError,
    PseudoMainBarForbidden,
    SourceGovernedMappingError,
    SourceGovernedMappingRecord,
    SourceGovernedMappingSchedule,
)

ZONE = ZoneInfo("Asia/Shanghai")
UNIVERSE = Path("docs/evidence/CANONICAL_CONTRACT_UNIVERSE.json")
OUT = Path("docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_PREP_V0_1.json")
SCHEMA_VERSION = "e07-source-governed-tqsdk-main-mapping-prep-v0.1"
WINDOW_START = "2024-01-01"
WINDOW_END = "2025-12-31"


def at(day: date, hour: int, minute: int) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=ZONE)


def provenance(version: str, session_id: str) -> MappingProvenance:
    return MappingProvenance(
        provider_identity="TQSDK",
        interface_identity="TqApi.query_his_cont_quotes",
        retrieval_session_id=session_id,
        retrieved_at=at(date(2026, 8, 20), 8, 0),
        source_artifact_identity=None,
        exact_bytes_bound=False,
        mapping_version=version,
        provenance_notes=("synthetic-machinery-fixture-not-candidate-mapping-authority",),
    )


def demo_record(research: str, source: str, concrete: str, day: date, prov: MappingProvenance):
    return SourceGovernedMappingRecord(
        research_symbol=research,
        source_symbol=source,
        concrete_instrument_id=concrete,
        effective_trading_date=day,
        effective_at=at(day, 9, 0),
        available_at=at(day, 9, 0) - timedelta(minutes=30),
        provenance=prov,
    )


def main() -> None:
    universe_doc = json.loads(UNIVERSE.read_text(encoding="utf-8"))
    products = list(universe_doc["products"])
    members = [entry["concrete_contract"] for entry in universe_doc["contracts"]]
    member_set = set(members)

    # ---- deterministic normalization / identity / PIT resolution demo ----
    prov = provenance("synthetic-demo-v1", "synthetic-demo-session")
    day_1 = date(2024, 1, 2)
    day_2 = date(2024, 1, 15)
    records = (
        demo_record("MAIN:SHFE:cu", "KQ.m@SHFE.cu", "SHFE.cu2401", day_1, prov),
        demo_record("MAIN:SHFE:cu", "KQ.m@SHFE.cu", "SHFE.cu2402", day_2, prov),
    )
    schedule = SourceGovernedMappingSchedule("synthetic-demo-v1", ("MAIN:SHFE:cu",), records)
    resolution = schedule.resolve("MAIN:SHFE:cu", at(day_1, 10, 0))
    resolution_later = schedule.resolve("MAIN:SHFE:cu", at(day_2, 10, 0))
    membership = schedule.validate_canonical_membership(member_set)

    # ---- fail-closed checks (synthetic, no real mapping) ----
    fail_closed: dict[str, str] = {}
    try:
        SourceGovernedMappingRecord(
            research_symbol="MAIN:SHFE:cu",
            source_symbol="KQ.m@SHFE.cu",
            concrete_instrument_id="SHFE.cu2401",
            effective_trading_date=day_1,
            effective_at=at(day_1, 9, 0),
            available_at=at(day_1, 8, 30),
            provenance=prov,
            derivation="PREVIOUS_DAY_OI_MAX",
        )
        fail_closed["substitution"] = "NOT_RAISED"
    except MappingSubstitutionForbidden:
        fail_closed["substitution"] = "MappingSubstitutionForbidden"
    try:
        demo_record("MAIN:SHFE:cu", "KQ.m@SHFE.cu", "KQ.m@SHFE.cu", day_1, prov)
        fail_closed["pseudo_main"] = "NOT_RAISED"
    except PseudoMainBarForbidden:
        fail_closed["pseudo_main"] = "PseudoMainBarForbidden"
    try:
        SourceGovernedMappingSchedule(
            "conflict-demo-v1",
            ("MAIN:SHFE:cu",),
            (
                demo_record("MAIN:SHFE:cu", "KQ.m@SHFE.cu", "SHFE.cu2401", day_1, prov),
                demo_record("MAIN:SHFE:cu", "KQ.m@SHFE.cu", "SHFE.cu2402", day_1, prov),
            ),
        )
        fail_closed["conflict"] = "NOT_RAISED"
    except MappingConflictError:
        fail_closed["conflict"] = "MappingConflictError"
    try:
        schedule.resolve("MAIN:SHFE:cu", at(date(2023, 12, 1), 9, 0))
        fail_closed["missing"] = "NOT_RAISED"
    except MappingUnavailableError:
        fail_closed["missing"] = "MappingUnavailableError"
    try:
        schedule.resolve("MAIN:SHFE:al", at(day_1, 9, 0))
        fail_closed["unknown_symbol"] = "NOT_RAISED"
    except MappingUnavailableError:
        fail_closed["unknown_symbol"] = "MappingUnavailableError"

    document = {
        "schema_version": SCHEMA_VERSION,
        "task": "E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_PREP_V0_1",
        "created_at": "2026-08-21",
        "role": "API-independent engineering prep ONLY. No login, no network, no outcome, no TqSdk decode.",
        "binding": "SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_APPLIED_TO_CANONICAL_CONCRETE_BARS",
        "source_policy": "FREE_PUBLIC_UNAUTHENTICATED_FIRST",
        "login_used": "NO",
        "network_used": "NO",
        "outcome_data_used": "NO",
        "tqsdk_import_used": "NO",
        "decode_adapter_implemented": "NO",
        "blocked_api_contract_not_pinned": BLOCKED_API_CONTRACT_NOT_PINNED,
        "status": {
            "TQSDK_HISTORY_ACCESS": "LOGIN_REQUIRED",
            "E07_MAPPING_COMPLETENESS": "INCOMPLETE",
            "E07_RUNTIME_MAPPING_STATUS": "FAIL_CLOSED_PREREQUISITE",
            "E07_PSEUDO_MAIN_PRICE_BARS": "FORBIDDEN",
            "E07_PROJECT_AUTHORED_SUBSTITUTE": "FORBIDDEN",
        },
        "canonical_universe": {
            "products": products,
            "concrete_contract_count": len(members),
            "window_start": WINDOW_START,
            "window_end": WINDOW_END,
        },
        "implemented_machinery": [
            "source-governed mapping record schema (SourceGovernedMappingRecord)",
            "provenance (MappingProvenance; exact-bytes-bound consistency)",
            "effective timestamp/date (source-defined next-trading-day switch day)",
            "deterministic normalization (canonical ordering / dedup)",
            "mapping identity (content sha256 over normalized fields)",
            "fail-closed missing (MappingUnavailableError) and conflict (MappingConflictError)",
            "canonical-contract membership validation (MAPPING_CONTRACT_NOT_IN_CANONICAL_UNIVERSE)",
            "terminal-only auth capture interface (TerminalOnlyAuthCapture / TerminalAuthCapture)",
            "no pseudo-main price bars (PseudoMainBarForbidden)",
            "no project-authored mapping substitution (MappingSubstitutionForbidden)",
        ],
        "not_implemented": [
            "TqSdk query_his_cont_quotes decode adapter (BLOCKED_API_CONTRACT_NOT_PINNED)",
            "runtime ContractMappingSchedule wiring (future Owner-gated package)",
        ],
        "demo_schedule": {
            "version": schedule.version,
            "research_symbols": list(schedule.research_symbols),
            "records": [
                {
                    "research_symbol": r.research_symbol,
                    "source_symbol": r.source_symbol,
                    "concrete_instrument_id": r.concrete_instrument_id,
                    "effective_trading_date": r.effective_trading_date.isoformat(),
                    "record_identity_id": r.identity_id,
                }
                for r in schedule.records
            ],
            "schedule_identity_id": schedule.identity_id,
        },
        "demo_resolution": {
            "on_first_effective_day": {
                "concrete_instrument_id": resolution.concrete_instrument_id,
                "effective_trading_date": resolution.effective_trading_date.isoformat(),
                "resolution_identity_id": resolution.identity_id,
            },
            "after_second_switch": {
                "concrete_instrument_id": resolution_later.concrete_instrument_id,
                "effective_trading_date": resolution_later.effective_trading_date.isoformat(),
                "resolution_identity_id": resolution_later.identity_id,
            },
        },
        "demo_membership_validation": {
            "member_target_count": len(schedule.records),
            "violation_count": len(membership),
            "violations": [
                {
                    "research_symbol": v.research_symbol,
                    "concrete_instrument_id": v.concrete_instrument_id,
                    "effective_trading_date": v.effective_trading_date.isoformat(),
                    "fact": v.fact,
                }
                for v in membership
            ],
        },
        "fail_closed_checks": fail_closed,
        "disclaimer": (
            "Demo records are synthetic machinery fixtures only and are NOT candidate "
            "mapping authority. They are never applied to any corpus. A real mapping "
            "requires an Owner-authorized authenticated TqSdk retrieval whose exact "
            "response contract is first pinned by evidence."
        ),
    }

    OUT.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"wrote {OUT}")
    print(f"  products={products}")
    print(f"  concrete_contract_count={len(members)}")
    print(f"  schedule_identity={schedule.identity_id}")
    print(f"  membership_violations={len(membership)}")
    print(f"  fail_closed={fail_closed}")


if __name__ == "__main__":
    main()

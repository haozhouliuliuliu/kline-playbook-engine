"""Build the source-governed E07 schedule from the authenticated TqSdk capture.

The input contains only TqSdk's daily continuous-to-concrete contract mapping.
It contains no OHLCV prices and no candidate outcome metric.  A row's mapping is
made effective at the next captured trading day's 09:00 Asia/Shanghai, matching
the project-owned, source-governed next-trading-day switch convention.
"""

from __future__ import annotations

from datetime import date, datetime
from hashlib import sha256
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from src.source_governed_mapping import (
    MappingProvenance,
    SourceGovernedMappingRecord,
    SourceGovernedMappingSchedule,
    decode_tqsdk_query_his_cont_quotes_payload,
)


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "docs" / "evidence" / "E07_TQSDK_QUERY_HIS_CONT_QUOTES_RAW_V0_1.json"
UNIVERSE = ROOT / "docs" / "evidence" / "CANONICAL_CONTRACT_UNIVERSE.json"
OUT = ROOT / "docs" / "evidence" / "E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json"
ZONE = ZoneInfo("Asia/Shanghai")
WINDOW_START = date(2024, 1, 1)
WINDOW_END = date(2025, 12, 31)
RESEARCH_SYMBOLS = {
    "KQ.m@SHFE.cu": "MAIN:SHFE:cu",
    "KQ.m@SHFE.al": "MAIN:SHFE:al",
    "KQ.m@SHFE.ni": "MAIN:SHFE:ni",
    "KQ.m@SHFE.au": "MAIN:SHFE:au",
    "KQ.m@SHFE.ag": "MAIN:SHFE:ag",
    "KQ.m@SHFE.rb": "MAIN:SHFE:rb",
}


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _at_open(day: date) -> datetime:
    return datetime(day.year, day.month, day.day, 9, 0, tzinfo=ZONE)


def _records() -> tuple[SourceGovernedMappingRecord, ...]:
    payload = json.loads(RAW.read_text(encoding="utf-8"))
    symbols = tuple(RESEARCH_SYMBOLS)
    rows = decode_tqsdk_query_his_cont_quotes_payload(payload, required_symbols=symbols)
    raw_sha = _file_hash(RAW)
    provenance = MappingProvenance(
        provider_identity="TQSDK_3_10_1",
        interface_identity="TqApi.query_his_cont_quotes",
        retrieval_session_id="E07_SCHEMA_PROBE_DONE_2026_08_21",
        retrieved_at=datetime(2026, 8, 21, 9, 0, 24, tzinfo=ZONE),
        source_artifact_identity=raw_sha,
        exact_bytes_bound=True,
        mapping_version="E07_SOURCE_GOVERNED_TQSDK_MAPPING_V0_1",
        provenance_notes=(
            "authenticated hidden-terminal schema probe",
            "TqSdk 3.10.1 source and docstring pinned date-plus-symbol-column schema",
            "row mapping becomes effective at next captured trading-day open",
        ),
    )
    all_records: list[SourceGovernedMappingRecord] = []
    for index in range(len(rows) - 1):
        row_day, row = rows[index]
        next_day, _ = rows[index + 1]
        previous = rows[index - 1][1] if index else None
        for source_symbol, research_symbol in RESEARCH_SYMBOLS.items():
            if previous is not None and previous[source_symbol] == row[source_symbol]:
                continue
            effective_at = _at_open(next_day)
            all_records.append(
                SourceGovernedMappingRecord(
                    research_symbol=research_symbol,
                    source_symbol=source_symbol,
                    concrete_instrument_id=row[source_symbol],
                    effective_trading_date=next_day,
                    effective_at=effective_at,
                    available_at=effective_at,
                    provenance=provenance,
                )
            )
    selected: list[SourceGovernedMappingRecord] = []
    for research_symbol in RESEARCH_SYMBOLS.values():
        candidates = [record for record in all_records if record.research_symbol == research_symbol]
        before_window = [record for record in candidates if record.effective_trading_date < WINDOW_START]
        if not before_window:
            raise ValueError(f"no source-governed mapping exists before the window for {research_symbol}")
        selected.append(max(before_window, key=lambda record: record.effective_at))
        selected.extend(
            record
            for record in candidates
            if WINDOW_START <= record.effective_trading_date <= WINDOW_END
        )
    return tuple(selected)


def build_payload() -> dict[str, object]:
    universe = json.loads(UNIVERSE.read_text(encoding="utf-8"))
    canonical_contracts = {entry["concrete_contract"] for entry in universe["contracts"]}
    records = _records()
    schedule = SourceGovernedMappingSchedule(
        "E07_SOURCE_GOVERNED_TQSDK_MAPPING_V0_1", tuple(RESEARCH_SYMBOLS.values()), records
    )
    violations = schedule.validate_canonical_membership(canonical_contracts)
    if violations:
        raise SystemExit("E07 mapping target is not in canonical universe")
    return {
        "artifact": "E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1",
        "window": {"start": WINDOW_START.isoformat(), "end": WINDOW_END.isoformat()},
        "source": {
            "provider": "TqSdk",
            "version": "3.10.1",
            "interface": "TqApi.query_his_cont_quotes",
            "raw_capture_path": "docs/evidence/E07_TQSDK_QUERY_HIS_CONT_QUOTES_RAW_V0_1.json",
            "raw_capture_sha256": _file_hash(RAW),
            "schema": "TQSDK_3_10_1_PANDAS_DATE_PLUS_SYMBOL_COLUMNS",
            "authenticated_probe": "YES",
        },
        "semantics": {
            "derivation": "SOURCE_GOVERNED",
            "switch": "NEXT_CAPTURED_TRADING_DAY_OPEN_ASIA_SHANGHAI",
            "pit_availability": "AVAILABLE_AT_EFFECTIVE_OPEN_NO_LOOKAHEAD",
            "pseudo_main_price_bars": "FORBIDDEN",
            "project_authored_substitute": "FORBIDDEN",
        },
        "schedule_identity": schedule.identity_id,
        "record_count": len(schedule.records),
        "canonical_membership_violations": [],
        "records": [
            {
                "research_symbol": record.research_symbol,
                "source_symbol": record.source_symbol,
                "concrete_instrument_id": record.concrete_instrument_id,
                "effective_trading_date": record.effective_trading_date.isoformat(),
                "effective_at": record.effective_at.isoformat(),
                "available_at": record.available_at.isoformat(),
                "record_identity": record.identity_id,
                "provenance_identity": record.provenance.identity_id,
            }
            for record in schedule.records
        ],
        "candidate_outcome_data_used": "NO",
        "price_data_used": "NO",
    }


def main() -> None:
    document = build_payload()
    OUT.write_text(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"records={document['record_count']} schedule={document['schedule_identity']}")


if __name__ == "__main__":
    main()

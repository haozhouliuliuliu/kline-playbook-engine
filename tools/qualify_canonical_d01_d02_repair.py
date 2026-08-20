"""Qualify only the recorded D01/D02 repair candidates.

This tool intentionally never rebuilds the accepted corpus.  Its input target
set is the committed revalidation evidence, and any future provider payload is
written only below a separate, ignored repair directory.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, timedelta
import json
import os
from pathlib import Path
import sys
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from src.historical_acquisition import (
    AcquisitionRequest,
    AcquisitionResult,
    TqSdkSourceAdapter,
    credentials_from_terminal,
)
from tools.build_canonical_dataset import (
    build_contract_configs,
    load_calendar,
    load_schedules,
    load_specs,
    load_universe,
    load_universe_bounds,
)
from tools.revalidate_canonical_corpus import _parse_datetime, _raw_filename, _timestamp_from_tqsdk


SOURCE_FAILURE_EVIDENCE_COMMIT = "a9e306550c5dc47695e4c27c1812de4c3cad5641"
EXPECTED_TARGET_COUNT = 116
EVIDENCE_SCHEMA_VERSION = "canonical-d01-d02-targeted-repair-qualification-v0.1"
DEFAULT_INPUT = Path("docs/evidence/CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json")
DEFAULT_JSON_OUTPUT = Path("docs/evidence/CANONICAL_D01_D02_TARGETED_REPAIR_QUALIFICATION_V0_1.json")
DEFAULT_MARKDOWN_OUTPUT = Path("docs/evidence/CANONICAL_D01_D02_TARGETED_REPAIR_QUALIFICATION_V0_1.md")


def _product(contract: str) -> str:
    code = contract.split(".", 1)[-1]
    return "".join(char for char in code if char.isalpha()).lower()


def _counter_dict(values: Iterable[str]) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def load_failure_inventory(path: Path) -> list[dict[str, Any]]:
    """Load exactly the already-recorded failures; never inspect a corpus here."""
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    failures = document.get("failure_partitions")
    if document.get("revalidation_result") != "FAIL_REPAIRED_COMPLETENESS":
        raise ValueError("failure evidence does not record repaired-completeness failure")
    if not isinstance(failures, list) or len(failures) != EXPECTED_TARGET_COUNT:
        raise ValueError(f"failure evidence must contain exactly {EXPECTED_TARGET_COUNT} failures")
    target_ids: set[str] = set()
    inventory: list[dict[str, Any]] = []
    for item in failures:
        if not isinstance(item, dict):
            raise ValueError("failure inventory contains a non-object item")
        identity = item.get("partition_identity")
        if not isinstance(identity, str) or not identity or identity in target_ids:
            raise ValueError("failure inventory has missing or duplicate partition identity")
        reasons = item.get("reasons")
        if not isinstance(reasons, list) or "D01_RETURNED_COVERAGE_TRUNCATED" not in reasons or "D02_MISSING_EXPECTED_BARS" not in reasons:
            raise ValueError("repair inventory may contain only recorded D01/D02 failures")
        target_ids.add(identity)
        inventory.append(dict(item))
    return sorted(inventory, key=lambda item: str(item["partition_identity"]))


def _expected_starts(sessions, exchange: str, contract: str, start: datetime, end: datetime, interval: timedelta) -> list[datetime]:
    return list(sessions.expected_bar_starts_between(exchange, contract, start, end, interval))


def _windows_for_request(sessions, start: datetime, end: datetime) -> list[dict[str, str]]:
    selected = []
    for window in sessions._windows:  # SessionMetadata is immutable; this is a read-only diagnostic index.
        if window.start < end and window.end > start:
            kind = "NIGHT" if window.start.hour >= 20 or window.end.hour <= 3 else "DAY"
            selected.append({
                "trading_day": window.trading_day.isoformat(),
                "start": window.start.isoformat(),
                "end": window.end.isoformat(),
                "session_class": kind,
            })
    return sorted(selected, key=lambda item: (item["start"], item["end"]))


def _ranges(starts: list[datetime], interval: timedelta) -> list[tuple[datetime, datetime, int]]:
    if not starts:
        return []
    groups: list[tuple[datetime, datetime, int]] = []
    group_start = prior = starts[0]
    count = 1
    for current in starts[1:]:
        if current == prior + interval:
            count += 1
        else:
            groups.append((group_start, prior, count))
            group_start, count = current, 1
        prior = current
    groups.append((group_start, prior, count))
    return groups


def _missing_shape(missing: list[datetime], expected: list[datetime], interval: timedelta) -> tuple[str, list[dict[str, object]]]:
    groups = _ranges(missing, interval)
    regions = [{"start": start.isoformat(), "end": end.isoformat(), "bar_count": count} for start, end, count in groups]
    if not groups:
        return "NONE", regions
    first, last = expected[0], expected[-1]
    prefix = groups[0][0] == first
    suffix = groups[-1][1] == last
    if len(groups) > 1:
        return "MULTIPLE_REGIONS", regions
    if prefix:
        return "PREFIX_ONLY", regions
    if suffix:
        return "SUFFIX_ONLY", regions
    return "INTERIOR", regions


def _truncation_shape(request_start: datetime, request_end: datetime, returned_start: datetime, returned_end: datetime) -> str:
    leading = returned_start != request_start
    trailing = returned_end != request_end
    if leading and trailing:
        return "BOTH_ENDS"
    if leading:
        return "START_ONLY"
    if trailing:
        return "END_ONLY"
    return "NONE"


def _session_class_for_starts(starts: list[datetime], windows: list[dict[str, str]]) -> str:
    classes: set[str] = set()
    for start in starts:
        for window in windows:
            window_start = _parse_datetime(window["start"], "session window start")
            window_end = _parse_datetime(window["end"], "session window end")
            if window_start <= start < window_end:
                classes.add(str(window["session_class"]))
                break
    if classes == {"DAY", "NIGHT"}:
        return "BOTH_DAY_AND_NIGHT"
    if classes == {"DAY"}:
        return "DAY_ONLY"
    if classes == {"NIGHT"}:
        return "NIGHT_ONLY"
    return "NO_CURRENT_WINDOW"


def diagnose_failure(failure: dict[str, Any], config, bounds: tuple[date, date]) -> dict[str, Any]:
    """Classify one recorded failure against current authority before download."""
    contract = str(failure["contract"])
    exchange = contract.split(".", 1)[0]
    request_start = _parse_datetime(failure.get("requested_start"), "requested_start")
    request_end = _parse_datetime(failure.get("requested_end"), "requested_end")
    returned_start = _parse_datetime(failure.get("returned_start"), "returned_start")
    returned_end = _parse_datetime(failure.get("returned_end"), "returned_end")
    interval = timedelta(seconds=60)
    expected = _expected_starts(config.sessions, exchange, contract, request_start, request_end, interval)
    missing = sorted(_parse_datetime(value, "missing_expected_bar_starts") for value in failure.get("missing_expected_bar_starts", []))
    authority_reasons: list[str] = []
    if not expected:
        authority_reasons.append("NO_CURRENT_EXPECTED_SESSION_BARS")
    else:
        if expected[0] != request_start:
            authority_reasons.append("REQUEST_START_DIFFERS_FROM_CURRENT_EXPECTED_START")
        if expected[-1] + interval != request_end:
            authority_reasons.append("REQUEST_END_DIFFERS_FROM_CURRENT_EXPECTED_END")
    trading_day = date.fromisoformat(str(failure["trading_day"]))
    first_day, last_day = bounds
    coverage = "WITHIN_GOVERNED_LISTING_COVERAGE" if first_day <= trading_day <= last_day else "OUTSIDE_GOVERNED_LISTING_COVERAGE"
    windows = _windows_for_request(config.sessions, request_start, request_end)
    classes = {item["session_class"] for item in windows}
    session_class = "BOTH_DAY_AND_NIGHT" if classes == {"DAY", "NIGHT"} else (next(iter(classes)) + "_ONLY" if classes else "NO_CURRENT_WINDOW")
    missing_shape, regions = _missing_shape(missing, expected, interval) if expected else ("UNCLASSIFIED", [])
    if len(missing) != int(failure.get("missing_expected_bars", 0)) or len(missing) != len(set(missing)):
        authority_reasons.append("RECORDED_MISSING_BAR_INVENTORY_IS_INCONSISTENT")
    if expected and not set(missing).issubset(set(expected)):
        authority_reasons.append("RECORDED_MISSING_BARS_OUTSIDE_CURRENT_EXPECTED_SESSION")
    return {
        "partition_identity": failure["partition_identity"],
        "product": _product(contract),
        "contract": contract,
        "trading_day": trading_day.isoformat(),
        "calendar_month": trading_day.strftime("%Y-%m"),
        "provider": "TQSDK",
        "granularity_seconds": 60,
        "requested_start": request_start.isoformat(),
        "requested_end": request_end.isoformat(),
        "returned_start": returned_start.isoformat(),
        "returned_end": returned_end.isoformat(),
        "missing_expected_bar_count": int(failure.get("missing_expected_bars", 0)),
        "truncation_shape": _truncation_shape(request_start, request_end, returned_start, returned_end),
        "missing_region_shape": missing_shape,
        "missing_regions": regions,
        "current_session_windows": windows,
        "session_class": session_class,
        "missing_session_class": _session_class_for_starts(missing, windows),
        "missing_starts_at_requested_boundary": bool(missing and missing[0] == request_start),
        "listing_effective_coverage": coverage,
        "listing_first_trading_day": first_day.isoformat(),
        "listing_last_trading_day": last_day.isoformat(),
        "authority_boundary_reasons": authority_reasons,
        "qualification_status": "NOT_ATTEMPTED",
    }


def diagnose_inventory(inventory: list[dict[str, Any]]) -> list[dict[str, Any]]:
    bounds_by_product = load_universe_bounds()
    configs = build_contract_configs(load_calendar(), load_universe(), bounds_by_product, load_specs(), load_schedules())
    diagnostics = []
    for failure in inventory:
        contract = str(failure["contract"])
        product = _product(contract)
        if contract not in configs or contract not in bounds_by_product.get(product, {}):
            raise ValueError(f"current authority lacks contract {contract}")
        diagnostics.append(diagnose_failure(failure, configs[contract], bounds_by_product[product][contract]))
    return sorted(diagnostics, key=lambda item: str(item["partition_identity"]))


def validate_repair_storage(repair_root: Path, historical_root: Path) -> Path:
    """Reject any candidate directory that could overwrite accepted raw data."""
    repair = Path(repair_root).resolve()
    historical = Path(historical_root).resolve()
    if repair == historical or repair in historical.parents or historical in repair.parents:
        raise ValueError("repair raw root must be disjoint from historical accepted raw root")
    return repair


def _records_by_start(payload: bytes, timezone: str, contract: str) -> dict[datetime, dict[str, Any]]:
    parsed = json.loads(payload.decode("utf-8"))
    if not isinstance(parsed, list) or not parsed:
        raise ValueError("raw payload must be a non-empty JSON list")
    result: dict[datetime, dict[str, Any]] = {}
    zone = ZoneInfo(timezone)
    for record in parsed:
        if not isinstance(record, dict) or record.get("symbol") not in (None, contract):
            raise ValueError("raw payload has an invalid record or contract")
        start = _timestamp_from_tqsdk(record.get("datetime"), zone)
        if start in result:
            raise ValueError("raw payload contains duplicate timestamps")
        result[start] = record
    return result


def compare_overlapping_values(old_payload: bytes, new_payload: bytes, timezone: str, contract: str) -> dict[str, int]:
    """Compare shared raw records without coercing nullable volume to zero."""
    old_records = _records_by_start(old_payload, timezone, contract)
    new_records = _records_by_start(new_payload, timezone, contract)
    ohlc_compared = ohlc_mismatches = value_mismatches = 0
    nullable_compared = nullable_mismatches = volume_compared = volume_mismatches = 0
    for timestamp in sorted(set(old_records) & set(new_records)):
        old, new = old_records[timestamp], new_records[timestamp]
        for field in ("open", "high", "low", "close"):
            ohlc_compared += 1
            if old.get(field) != new.get(field):
                ohlc_mismatches += 1
        for field in ("volume", "open_oi", "close_oi"):
            old_value, new_value = old.get(field), new.get(field)
            if old_value is None or new_value is None:
                continue
            nullable_compared += 1
            if old_value != new_value:
                nullable_mismatches += 1
                if field == "volume":
                    volume_mismatches += 1
            if field == "volume":
                volume_compared += 1
    value_mismatches = ohlc_mismatches + nullable_mismatches
    return {
        "overlapping_timestamps": len(set(old_records) & set(new_records)),
        "overlapping_ohlc_values_compared": ohlc_compared,
        "overlapping_ohlc_mismatch_count": ohlc_mismatches,
        "nullable_values_compared": nullable_compared,
        "nullable_value_mismatch_count": nullable_mismatches,
        "nullable_volume_values_compared": volume_compared,
        "nullable_volume_mismatch_count": volume_mismatches,
        "total_value_mismatch_count": value_mismatches,
    }


def has_historical_provider_value_drift(comparison: dict[str, int]) -> bool:
    """Only an OHLC disagreement creates the prohibited provider-drift class."""
    return comparison["overlapping_ohlc_mismatch_count"] > 0


def qualify_candidate(diagnostic: dict[str, Any], result: AcquisitionResult, sessions) -> str:
    """Apply D01 then D02 to a single successful candidate response."""
    request = result.request
    if result.returned_start != request.requested_start or result.returned_end != request.requested_end:
        return "STILL_D01_TRUNCATED"
    try:
        observed = set(_records_by_start(result.payload, request.timezone, request.concrete_instrument))
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return "RAW_INVALID"
    expected = set(_expected_starts(sessions, request.exchange, request.concrete_instrument, request.requested_start, request.requested_end, timedelta(seconds=request.granularity_seconds)))
    if observed - expected:
        return "RAW_INVALID"
    if expected - observed:
        return "STILL_D02_MISSING"
    return "REPAIRED_PASS"


def _summaries(diagnostics: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    return {
        "failures_by_product": _counter_dict(str(item["product"]) for item in diagnostics),
        "failures_by_contract": _counter_dict(str(item["contract"]) for item in diagnostics),
        "failures_by_month": _counter_dict(str(item["calendar_month"]) for item in diagnostics),
        "failure_shape_counts": _counter_dict(str(item["truncation_shape"]) for item in diagnostics),
        "missing_region_shape_counts": _counter_dict(str(item["missing_region_shape"]) for item in diagnostics),
        "session_class_counts": _counter_dict(str(item["session_class"]) for item in diagnostics),
        "missing_session_class_counts": _counter_dict(str(item["missing_session_class"]) for item in diagnostics),
    }


def _request_from_diagnostic(diagnostic: dict[str, Any]) -> AcquisitionRequest:
    contract = str(diagnostic["contract"])
    return AcquisitionRequest(
        exchange=contract.split(".", 1)[0],
        concrete_instrument=contract,
        trading_day=date.fromisoformat(str(diagnostic["trading_day"])),
        granularity_seconds=int(diagnostic["granularity_seconds"]),
        requested_start=_parse_datetime(diagnostic["requested_start"], "requested_start"),
        requested_end=_parse_datetime(diagnostic["requested_end"], "requested_end"),
    )


def targeted_reacquire(
    diagnostics: list[dict[str, Any]],
    *,
    repair_root: Path,
    historical_root: Path,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """One normal production request per recorded target, into a disjoint root."""
    repair_root = validate_repair_storage(repair_root, historical_root)
    configs = build_contract_configs(load_calendar(), load_universe(), load_universe_bounds(), load_specs(), load_schedules())
    adapter = TqSdkSourceAdapter(credentials_from_terminal)
    totals: Counter[str] = Counter()
    try:
        for diagnostic in diagnostics:
            request = _request_from_diagnostic(diagnostic)
            raw_path = repair_root / request.raw_file_name("TQSDK")
            if raw_path.exists():
                diagnostic["qualification_status"] = "ACQUISITION_FAILED"
                diagnostic["acquisition_error"] = "repair candidate already exists; no repeat fetch performed"
                totals["acquisition_failed_count"] += 1
                continue
            try:
                acquired = adapter.acquire(request)
            except Exception as error:  # Provider/auth failures are evidence, never retried blindly.
                diagnostic["qualification_status"] = "ACQUISITION_FAILED"
                diagnostic["acquisition_error"] = type(error).__name__
                totals["acquisition_failed_count"] += 1
                continue
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            partial_path = raw_path.with_suffix(raw_path.suffix + ".partial")
            partial_path.write_bytes(acquired.payload)
            os.replace(partial_path, raw_path)
            status = qualify_candidate(diagnostic, acquired, configs[request.concrete_instrument].sessions)
            diagnostic["qualification_status"] = status
            diagnostic["candidate_raw_path"] = str(raw_path).replace("\\", "/")
            diagnostic["candidate_returned_start"] = acquired.returned_start.isoformat()
            diagnostic["candidate_returned_end"] = acquired.returned_end.isoformat()
            totals["targeted_reacquisition_success_count"] += 1
            totals[status.lower() + "_count"] += 1
            old_path = historical_root / request.raw_file_name("TQSDK")
            if old_path.is_file():
                try:
                    comparison = compare_overlapping_values(old_path.read_bytes(), acquired.payload, request.timezone, request.concrete_instrument)
                except (OSError, UnicodeDecodeError, ValueError, json.JSONDecodeError) as error:
                    diagnostic["comparison_error"] = type(error).__name__
                else:
                    diagnostic["overlap_comparison"] = comparison
                    totals["overlapping_ohlc_values_compared"] += comparison["overlapping_ohlc_values_compared"]
                    totals["overlapping_ohlc_mismatch_count"] += comparison["overlapping_ohlc_mismatch_count"]
                    if has_historical_provider_value_drift(comparison):
                        diagnostic["historical_provider_value_drift"] = True
                        totals["historical_provider_value_drift_count"] += 1
    finally:
        adapter.close()
    return diagnostics, dict(totals)


def build_evidence(diagnostics: list[dict[str, Any]], *, blocker: str | None, attempted: bool = False, totals: dict[str, int] | None = None) -> dict[str, Any]:
    summaries = _summaries(diagnostics)
    totals = totals or {}
    authority_inconsistency = any(item["authority_boundary_reasons"] for item in diagnostics)
    if authority_inconsistency:
        result = "AUTHORITY_BOUNDARY_INCONSISTENCY"
    elif not attempted:
        result = "BLOCKED"
    elif totals.get("historical_provider_value_drift_count", 0):
        result = "HISTORICAL_PROVIDER_VALUE_DRIFT"
    elif totals.get("repaired_pass_count", 0) == EXPECTED_TARGET_COUNT:
        result = "ALL_116_REPLACEMENTS_QUALIFIED"
    elif totals.get("repaired_pass_count", 0):
        result = "PARTIAL_REPLACEMENTS_QUALIFIED"
    else:
        result = "PROVIDER_RETURNS_SAME_TRUNCATION"
    effective_blocker = "AUTHORITY_BOUNDARY_INCONSISTENCY" if authority_inconsistency else blocker
    return {
        "schema_version": EVIDENCE_SCHEMA_VERSION,
        "source_failure_evidence_commit": SOURCE_FAILURE_EVIDENCE_COMMIT,
        "source_failure_evidence_path": str(DEFAULT_INPUT).replace("\\", "/"),
        "target_partition_count": len(diagnostics),
        "target_selection_rule": "exact failure_partitions from committed revalidation evidence only",
        "outcome_access_used": False,
        "historical_accepted_corpus_modified": False,
        "targeted_reacquisition_attempted": attempted,
        "targeted_reacquisition_success_count": totals.get("targeted_reacquisition_success_count", 0),
        "repaired_pass_count": totals.get("repaired_pass_count", 0),
        "still_d01_truncated_count": totals.get("still_d01_truncated_count", 0),
        "still_d02_missing_count": totals.get("still_d02_missing_count", 0),
        "acquisition_failed_count": totals.get("acquisition_failed_count", 0),
        "authority_mismatch_count": totals.get("authority_mismatch_count", 0),
        "overlapping_ohlc_values_compared": totals.get("overlapping_ohlc_values_compared", 0),
        "overlapping_ohlc_mismatch_count": totals.get("overlapping_ohlc_mismatch_count", 0),
        "historical_provider_value_drift_count": totals.get("historical_provider_value_drift_count", 0),
        "result": result,
        "blocker": effective_blocker,
        "systematic_pattern_observations": {
            "all_returned_starts_later_than_requested": all(item["returned_start"] > item["requested_start"] for item in diagnostics),
            "all_returned_ends_earlier_than_requested": all(item["returned_end"] < item["requested_end"] for item in diagnostics),
            "targets_with_missing_at_requested_boundary": sum(bool(item["missing_starts_at_requested_boundary"]) for item in diagnostics),
            "targets_with_night_session_missing_bars": sum(item["missing_session_class"] in ("NIGHT_ONLY", "BOTH_DAY_AND_NIGHT") for item in diagnostics),
            "all_targets_within_listing_coverage": all(item["listing_effective_coverage"] == "WITHIN_GOVERNED_LISTING_COVERAGE" for item in diagnostics),
            "interpretation": "Descriptive counts only; no causal explanation is inferred.",
        },
        "summaries": summaries,
        "diagnostics": diagnostics,
    }


def _markdown(evidence: dict[str, Any]) -> str:
    summaries = evidence["summaries"]
    lines = [
        "# Canonical D01/D02 targeted repair qualification v0.1",
        "",
        f"- SOURCE_FAILURE_EVIDENCE_COMMIT: `{evidence['source_failure_evidence_commit']}`",
        f"- TARGET_PARTITION_COUNT: `{evidence['target_partition_count']}`",
        f"- RESULT: `{evidence['result']}`",
        f"- BLOCKER: `{evidence['blocker']}`",
        f"- TARGETED_REACQUISITION_ATTEMPTED: `{evidence['targeted_reacquisition_attempted']}`",
        "",
        "## Deterministic diagnostic summary",
        "",
    ]
    for name, values in summaries.items():
        lines.append(f"- {name}: `{json.dumps(values, ensure_ascii=False, sort_keys=True)}`")
    lines.extend([
        "",
        "The JSON companion records all 116 exact targets, request/return boundaries, current authority windows, missing regions, listing coverage, and the no-download blocking decision. No accepted artifact was modified.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose recorded D01/D02 repair targets without touching the accepted corpus")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    parser.add_argument("--repair-raw-root", type=Path, default=Path("data/revalidation_repair_v01/raw/historical"))
    parser.add_argument("--historical-raw-root", type=Path, default=Path(r"C:\\Users\\H\\Documents\\kline-playbook-engine\\data\\raw\\historical"))
    parser.add_argument("--attempt-reacquisition", action="store_true", help="requires existing interactive TqSdk terminal authentication")
    args = parser.parse_args()
    validate_repair_storage(args.repair_raw_root, args.historical_raw_root)
    inventory = load_failure_inventory(args.input)
    diagnostics = diagnose_inventory(inventory)
    # Production authentication is intentionally terminal-only and is not
    # available from this non-interactive bounded run.  Do not prompt or send
    # blank credentials, and do not create a new credentials configuration.
    blocker = "TQSDK_EXISTING_AUTH_NOT_AVAILABLE"
    attempted = False
    totals: dict[str, int] = {}
    if args.attempt_reacquisition and not any(item["authority_boundary_reasons"] for item in diagnostics):
        if sys.stdin.isatty():
            diagnostics, totals = targeted_reacquire(diagnostics, repair_root=args.repair_raw_root, historical_root=args.historical_raw_root)
            attempted = True
            blocker = None
    evidence = build_evidence(diagnostics, blocker=blocker, attempted=attempted, totals=totals)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(_markdown(evidence), encoding="utf-8")
    print(f"RESULT={evidence['result']}")
    print(f"TARGET_PARTITIONS={evidence['target_partition_count']}")
    print(f"BLOCKER={evidence['blocker']}")


if __name__ == "__main__":
    main()

"""Minimal authenticated provider probe for the recorded first-day failures.

The probe intentionally samples only deterministic representatives.  It never
changes canonical request semantics, accepted raw artifacts, or the 116-target
qualification evidence.
"""

from __future__ import annotations

import argparse
from collections import Counter
from datetime import date, datetime, time, timedelta
import json
import os
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from src.historical_acquisition import AcquisitionRequest, AcquisitionResult, TqSdkSourceAdapter, credentials_from_terminal
from tools.build_canonical_dataset import build_contract_configs, load_calendar, load_schedules, load_specs, load_universe, load_universe_bounds
from tools.qualify_canonical_d01_d02_repair import (
    DEFAULT_JSON_OUTPUT as QUALIFICATION_EVIDENCE,
    compare_overlapping_values,
    has_historical_provider_value_drift,
)


PROBE_SCHEMA_VERSION = "canonical-first-day-provider-probe-v0.1"
DEFAULT_JSON_OUTPUT = Path("docs/evidence/CANONICAL_FIRST_DAY_PROVIDER_PROBE_V0_1.json")
DEFAULT_MARKDOWN_OUTPUT = Path("docs/evidence/CANONICAL_FIRST_DAY_PROVIDER_PROBE_V0_1.md")
DEFAULT_PROBE_ROOT = Path("data/revalidation_repair_v01/provider_probe")
DEFAULT_HISTORICAL_RAW_ROOT = Path(r"C:\Users\H\Documents\kline-playbook-engine\data\raw\historical")
CN = ZoneInfo("Asia/Shanghai")


def select_probe_targets(qualification_path: Path, limit_per_shape: int = 3) -> list[dict[str, Any]]:
    """Choose three representatives per shape, one per product before repeats."""
    document = json.loads(Path(qualification_path).read_text(encoding="utf-8"))
    diagnostics = document.get("diagnostics")
    if document.get("target_partition_count") != 116 or not isinstance(diagnostics, list):
        raise ValueError("qualification evidence must contain the recorded 116 diagnostics")
    selected: list[dict[str, Any]] = []
    for shape in ("PREFIX_ONLY", "MULTIPLE_REGIONS"):
        candidates = sorted(
            (item for item in diagnostics if item.get("missing_region_shape") == shape),
            key=lambda item: (str(item["product"]), str(item["contract"]), str(item["trading_day"])),
        )
        by_product: dict[str, dict[str, Any]] = {}
        for candidate in candidates:
            by_product.setdefault(str(candidate["product"]), candidate)
        picks = [by_product[product] for product in sorted(by_product)][:limit_per_shape]
        if len(picks) != limit_per_shape:
            raise ValueError(f"not enough deterministic {shape} representatives")
        for candidate in picks:
            selected.append({**candidate, "probe_shape": shape})
    products = {str(item["product"]) for item in selected}
    if len(products) < 3:
        raise ValueError("probe selection must cover multiple products")
    return selected


def _request_for(target: dict[str, Any], kind: str) -> AcquisitionRequest:
    contract = str(target["contract"])
    exchange = contract.split(".", 1)[0]
    trading_day = date.fromisoformat(str(target["trading_day"]))
    if kind == "A":
        start = datetime.fromisoformat(str(target["requested_start"]))
        end = datetime.fromisoformat(str(target["requested_end"]))
    elif kind == "B":
        start = datetime.combine(trading_day, time(9, 0), tzinfo=CN)
        end = datetime.combine(trading_day, time(15, 0), tzinfo=CN)
    else:
        raise ValueError("probe request kind must be A or B")
    return AcquisitionRequest(exchange, contract, trading_day, 60, start, end)


def _observed_starts(payload: bytes, timezone: str, contract: str) -> set[datetime]:
    records = json.loads(payload.decode("utf-8"))
    if not isinstance(records, list) or not records:
        raise ValueError("provider payload must be a non-empty list")
    zone = ZoneInfo(timezone)
    starts: set[datetime] = set()
    for record in records:
        if not isinstance(record, dict) or record.get("symbol") not in (None, contract):
            raise ValueError("provider payload contains invalid contract record")
        timestamp = record.get("datetime")
        if isinstance(timestamp, bool):
            raise ValueError("provider timestamp is invalid")
        seconds = int(timestamp) // 1_000_000_000
        start = datetime.fromtimestamp(seconds, tz=zone)
        if start in starts:
            raise ValueError("provider payload contains duplicate bar starts")
        starts.add(start)
    return starts


def _qualify(result: AcquisitionResult, sessions) -> tuple[bool, int, int]:
    request = result.request
    interval = timedelta(seconds=request.granularity_seconds)
    try:
        observed = _observed_starts(result.payload, request.timezone, request.concrete_instrument)
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return False, 0, 0
    expected = set(sessions.expected_bar_starts_between(request.exchange, request.concrete_instrument, request.requested_start, request.requested_end, interval))
    exact_boundary = result.returned_start == request.requested_start and result.returned_end == request.requested_end
    return exact_boundary and not (expected - observed) and not (observed - expected), len(observed), len(expected - observed)


def _safe_candidate_path(probe_root: Path, request: AcquisitionRequest, kind: str, historical_raw_root: Path) -> Path:
    root = Path(probe_root).resolve()
    historical = Path(historical_raw_root).resolve()
    if root == historical or root in historical.parents or historical in root.parents:
        raise ValueError("provider probe root must be disjoint from accepted historical raw root")
    return root / kind / request.raw_file_name("TQSDK")


def _save_payload(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    temporary.write_bytes(payload)
    os.replace(temporary, path)


def run_probe(targets: list[dict[str, Any]], adapter, *, probe_root: Path, historical_raw_root: Path) -> tuple[list[dict[str, Any]], dict[str, int], str]:
    """Run at most two requests for each selected target, stopping on OHLC drift."""
    configs = build_contract_configs(load_calendar(), load_universe(), load_universe_bounds(), load_specs(), load_schedules())
    records: list[dict[str, Any]] = []
    totals: Counter[str] = Counter()
    result = "PROBE_COMPLETED"
    for target in targets:
        record: dict[str, Any] = {"partition_identity": target["partition_identity"], "contract": target["contract"], "product": target["product"], "trading_day": target["trading_day"], "probe_shape": target["probe_shape"], "requests": []}
        for kind in ("A", "B"):
            request = _request_for(target, kind)
            entry: dict[str, Any] = {"kind": kind, "requested_start": request.requested_start.isoformat(), "requested_end": request.requested_end.isoformat()}
            try:
                acquired = adapter.acquire(request)
                path = _safe_candidate_path(probe_root, request, kind, historical_raw_root)
                _save_payload(path, acquired.payload)
                complete, observed_bars, missing_bars = _qualify(acquired, configs[request.concrete_instrument].sessions)
                entry.update({"returned_start": acquired.returned_start.isoformat(), "returned_end": acquired.returned_end.isoformat(), "observed_bars": observed_bars, "missing_expected_bars": missing_bars, "raw_path": str(path).replace("\\", "/")})
                entry["classification"] = ("ORIGINAL_REQUEST_NOW_COMPLETE" if complete else "ORIGINAL_REQUEST_REPEATABLE_TRUNCATION") if kind == "A" else ("DAY_ONLY_COMPLETE" if complete else "DAY_ONLY_STILL_TRUNCATED")
                totals[entry["classification"]] += 1
                old_path = Path(historical_raw_root) / _request_for(target, "A").raw_file_name("TQSDK")
                if old_path.is_file():
                    comparison = compare_overlapping_values(old_path.read_bytes(), acquired.payload, request.timezone, request.concrete_instrument)
                    entry["overlap_comparison"] = comparison
                    totals["OVERLAPPING_OHLC_VALUES_COMPARED"] += comparison["overlapping_ohlc_values_compared"]
                    totals["OVERLAPPING_OHLC_MISMATCH_COUNT"] += comparison["overlapping_ohlc_mismatch_count"]
                    if has_historical_provider_value_drift(comparison):
                        entry["provider_value_drift"] = True
                        totals["PROVIDER_VALUE_DRIFT"] += 1
                        result = "HISTORICAL_PROVIDER_VALUE_DRIFT"
            except Exception as error:  # Provider/runtime faults are recorded once; no repeat gambling.
                entry.update({"classification": "ACQUISITION_FAILED", "error_type": type(error).__name__})
                totals["ACQUISITION_FAILED"] += 1
            record["requests"].append(entry)
            if result == "HISTORICAL_PROVIDER_VALUE_DRIFT":
                break
        records.append(record)
        if result == "HISTORICAL_PROVIDER_VALUE_DRIFT":
            break
    if result == "PROBE_COMPLETED":
        originals = [entry for record in records for entry in record["requests"] if entry["kind"] == "A"]
        day_only = [entry for record in records for entry in record["requests"] if entry["kind"] == "B"]
        severe_day_failures = [entry for record in records if record["probe_shape"] == "MULTIPLE_REGIONS" for entry in record["requests"] if entry["kind"] == "B" and entry["classification"] == "DAY_ONLY_STILL_TRUNCATED"]
        if severe_day_failures:
            result = "FIRST_DAY_PROVIDER_DATA_UNAVAILABLE"
        elif originals and all(entry["classification"] == "ORIGINAL_REQUEST_NOW_COMPLETE" for entry in originals):
            result = "REPRESENTATIVE_ORIGINAL_REQUESTS_COMPLETE"
        elif any(entry["classification"] == "ORIGINAL_REQUEST_REPEATABLE_TRUNCATION" for entry in originals):
            result = "PROVIDER_REPEATABILITY_CONFIRMED"
    return records, dict(totals), result


def build_evidence(targets: list[dict[str, Any]], records: list[dict[str, Any]], totals: dict[str, int], result: str) -> dict[str, Any]:
    return {
        "schema_version": PROBE_SCHEMA_VERSION,
        "target_selection_rule": "for each shape, select the first representative per product ordered by product, contract, trading day; take the first three products",
        "selected_target_count": len(targets),
        "selected_targets": [{"partition_identity": item["partition_identity"], "product": item["product"], "contract": item["contract"], "trading_day": item["trading_day"], "shape": item["probe_shape"]} for item in targets],
        "outcome_access_used": False,
        "historical_accepted_corpus_modified": False,
        "result": result,
        "totals": dict(sorted(totals.items())),
        "probe_records": records,
    }


def _markdown(evidence: dict[str, Any]) -> str:
    return "\n".join([
        "# Canonical first-day provider probe v0.1", "",
        f"- RESULT: `{evidence['result']}`",
        f"- SELECTED_TARGET_COUNT: `{evidence['selected_target_count']}`",
        f"- TOTALS: `{json.dumps(evidence['totals'], ensure_ascii=False, sort_keys=True)}`",
        "", "The JSON companion preserves both request forms and their classifications. Probe raw files are isolated under the ignored repair area; no accepted artifact was overwritten.", "",
    ])


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a minimal, authenticated first-day TqSdk provider probe")
    parser.add_argument("--execute", action="store_true", help="prompt for terminal-hidden TqSdk authentication and run the six representative probes")
    parser.add_argument("--qualification-evidence", type=Path, default=QUALIFICATION_EVIDENCE)
    parser.add_argument("--probe-root", type=Path, default=DEFAULT_PROBE_ROOT)
    parser.add_argument("--historical-raw-root", type=Path, default=DEFAULT_HISTORICAL_RAW_ROOT)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_JSON_OUTPUT)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_MARKDOWN_OUTPUT)
    args = parser.parse_args()
    if not args.execute:
        raise SystemExit("EXECUTION_REQUIRES_TERMINAL_HIDDEN_TQSDK_AUTH")
    targets = select_probe_targets(args.qualification_evidence)
    adapter = TqSdkSourceAdapter(credentials_from_terminal)
    try:
        records, totals, result = run_probe(targets, adapter, probe_root=args.probe_root, historical_raw_root=args.historical_raw_root)
    finally:
        adapter.close()
    evidence = build_evidence(targets, records, totals, result)
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.markdown_output.write_text(_markdown(evidence), encoding="utf-8")
    print(f"RESULT={result}")


if __name__ == "__main__":
    main()

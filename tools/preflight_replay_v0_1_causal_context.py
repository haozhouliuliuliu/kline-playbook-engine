#!/usr/bin/env python3
"""Seal the exact V0.1 slice and preflight causal 4H/1H/15m/5m context over the
real canonical corpus. Pure local computation: zero provider calls.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from datetime import date
from decimal import Decimal
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.replay_v0_1_canonical_feed import (
    ReplayMinuteBar,
    build_fixed_5m_preflight,
    governed_windows_for_days,
)
from src.replay_v0_1_canonical_steps import build_governed_wake_step
from src.replay_v0_1_causal_context import (
    CONTEXT_WINDOW_COUNTS,
    FOUR_HOUR_AGGREGATION_VERSION,
    LOWER_AGGREGATION_VERSION,
    CanonicalCausalContextIndex,
    context_policy_identity,
)
from src.replay_v0_1_exact_slice import _parse_calendar, select_and_seal_exact_v0_1_slice


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Seal exact V0.1 slice and preflight causal multi-timeframe context."
    )
    parser.add_argument("--manifest", type=Path, default=REPO_ROOT / "data/canonical/manifest.json")
    parser.add_argument("--parquet-root", type=Path, default=REPO_ROOT / "data/canonical/parquet")
    parser.add_argument("--output", type=Path, default=None)
    return parser


def _load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def _load_rows(*, parquet_root: Path, seal, sessions: dict):
    try:
        import pyarrow.dataset as ds  # noqa: PLC0415
    except ImportError as error:
        raise RuntimeError("this preflight requires the pinned canonical pyarrow environment") from error
    if not parquet_root.is_dir():
        raise ValueError("canonical parquet root does not exist")
    all_bound_days = (
        seal.slice.prior_history_days + seal.slice.burn_in_days + seal.slice.measurement_days
    )
    partition_by_day = dict(zip(all_bound_days, seal.slice.partition_identities, strict=True))
    authority_identity = sessions[seal.slice.product]["identity"]
    dataset = ds.dataset(str(parquet_root), format="parquet", partitioning="hive")
    expression = (ds.field("product") == seal.slice.product) & (
        ds.field("concrete_contract") == seal.slice.concrete_contract
    )
    table = dataset.to_table(
        columns=[
            "product", "concrete_contract", "trading_day", "bar_start", "bar_end",
            "historical_available_at", "open", "high", "low", "close", "volume",
            "session_metadata_identity",
        ],
        filter=expression,
    )
    wanted = set(all_bound_days)
    row_session_ids: dict[date, set[str]] = defaultdict(set)
    rows: list[ReplayMinuteBar] = []
    for raw in table.to_pylist():
        day = raw["trading_day"]
        if day not in wanted:
            continue
        if raw["volume"] is None:
            raise ValueError("selected minute has missing canonical volume")
        row_session_id = raw["session_metadata_identity"]
        if not isinstance(row_session_id, str) or not row_session_id:
            raise ValueError("selected minute has no canonical session_metadata_identity")
        row_session_ids[day].add(row_session_id)
        rows.append(ReplayMinuteBar(
            product=raw["product"], concrete_contract=raw["concrete_contract"], trading_day=day,
            start=raw["bar_start"], end=raw["bar_end"], available_at=raw["historical_available_at"],
            open=raw["open"], high=raw["high"], low=raw["low"], close=raw["close"],
            volume=Decimal(raw["volume"]), partition_identity=partition_by_day[day],
            session_authority_identity=authority_identity,
        ))
    missing_days = wanted - set(row_session_ids)
    if missing_days:
        raise ValueError(f"canonical parquet has no rows for {len(missing_days)} bound days")
    if any(len(values) != 1 for values in row_session_ids.values()):
        raise ValueError("canonical row session metadata identity changes within a bound trading day")
    serializable = {day.isoformat(): sorted(values) for day, values in sorted(row_session_ids.items())}
    return tuple(sorted(rows, key=lambda item: item.start)), serializable


def main() -> int:
    args = _parser().parse_args()
    calendar_path = REPO_ROOT / "docs/evidence/CANONICAL_TRADING_CALENDAR.json"
    sessions_path = REPO_ROOT / "docs/evidence/CANONICAL_SESSION_SCHEDULES.json"
    e07_path = REPO_ROOT / "docs/evidence/E07_SOURCE_GOVERNED_TQSDK_MAIN_MAPPING_V0_1.json"
    corpus_path = REPO_ROOT / "docs/evidence/CANONICAL_CORPUS_IDENTITY.json"
    seal = select_and_seal_exact_v0_1_slice(
        manifest_path=args.manifest,
        trading_calendar_path=calendar_path,
        session_schedule_path=sessions_path,
        e07_path=e07_path,
        corpus_identity_path=corpus_path,
    )
    calendar_payload = _load_json(calendar_path)
    session_payload = _load_json(sessions_path)
    calendar, night_closed, _ = _parse_calendar(calendar_payload)
    sessions = session_payload["products"]

    prior = seal.slice.prior_history_days
    burn_in = seal.slice.burn_in_days
    measurement = seal.slice.measurement_days
    replay_days = burn_in + measurement
    all_bound_days = prior + replay_days

    windows = governed_windows_for_days(
        product=seal.slice.product,
        replay_days=all_bound_days,
        trading_calendar=calendar,
        night_closed_days=night_closed,
        session_schedule=sessions,
    )
    rows, row_session_ids = _load_rows(parquet_root=args.parquet_root, seal=seal, sessions=sessions)
    replay_windows = tuple(item for item in windows if item.trading_day in replay_days)
    replay_rows = tuple(item for item in rows if item.trading_day in replay_days)
    preflight = build_fixed_5m_preflight(
        product=seal.slice.product,
        concrete_contract=seal.slice.concrete_contract,
        replay_days=replay_days,
        windows=replay_windows,
        minute_bars=replay_rows,
    )
    index = CanonicalCausalContextIndex.build(
        product=seal.slice.product,
        concrete_contract=seal.slice.concrete_contract,
        windows=windows,
        minute_bars=rows,
    )

    step_count = 0
    first_wake_time = None
    last_wake_time = None
    for wake in preflight.wake_bars:
        context = index.context_for_wake(wake)
        build_governed_wake_step(wake, context_bars=context)
        step_count += 1
        if first_wake_time is None:
            first_wake_time = wake.available_at
        last_wake_time = wake.available_at
    if step_count != preflight.expected_wake_count:
        raise ValueError(
            f"governed step count {step_count} != governed wake count {preflight.expected_wake_count}"
        )

    payload = {
        "status": "PASS",
        "exact_slice_seal_identity": seal.identity,
        "slice_identity": seal.slice.identity,
        "canonical_corpus_identity": seal.canonical_corpus_identity,
        "raw_manifest_root_identity": seal.raw_manifest_root_identity,
        "trading_calendar_identity": seal.trading_calendar_identity,
        "session_authority_root_identity": seal.session_authority_root_identity,
        "e07_schedule_identity": seal.e07_schedule_identity,
        "product": seal.slice.product,
        "concrete_contract": seal.slice.concrete_contract,
        "prior_history_days": [item.isoformat() for item in prior],
        "burn_in_days": [item.isoformat() for item in burn_in],
        "measurement_days": [item.isoformat() for item in measurement],
        "canonical_fixed_5m_preflight_identity": preflight.identity,
        "context_policy_identity": index.policy_identity,
        "context_index_identity": index.identity,
        "four_hour_aggregation_version": FOUR_HOUR_AGGREGATION_VERSION,
        "lower_aggregation_version": LOWER_AGGREGATION_VERSION,
        "context_window_counts": CONTEXT_WINDOW_COUNTS,
        "constructed_bar_counts": index.bar_counts(),
        "governed_wake_count": preflight.expected_wake_count,
        "governed_step_count": step_count,
        "first_wake_time": first_wake_time.isoformat() if first_wake_time is not None else None,
        "last_wake_time": last_wake_time.isoformat() if last_wake_time is not None else None,
        "provider_call_authorized": False,
        "canonical_row_session_metadata_identities": row_session_ids,
    }
    encoded = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        partial = output.with_name(output.name + ".partial")
        try:
            partial.write_text(encoded, encoding="utf-8")
            partial.replace(output)
        finally:
            if partial.exists():
                partial.unlink()
    sys.stdout.write(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

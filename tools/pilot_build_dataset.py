"""Pilot dataset acquisition runner for kline-playbook-engine.

PILOT_ONLY: this builds a small real candidate dataset to prove the reusable
acquisition boundary.  It is NOT the formal
CANONICAL_RESEARCH_DATASET_BUILD_AND_SOURCE_ACCEPTANCE_PACKAGE.

Run with the isolated reversible TqSdk venv from the repo root:

    $env:PROBE_VENV = "$env:LOCALAPPDATA\\Temp\\kline-playbook-tqsdk-probe"
    & "$env:PROBE_VENV\\Scripts\\python.exe" -m tools.pilot_build_dataset

Credentials are entered locally (hidden password) and exist only in memory.
No broker/order API is used.  Raw data is written only to the ignored
`data/raw/historical/` location.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.data_substrate import SessionMetadata, SessionWindow  # noqa: E402
from src.historical_acquisition import (  # noqa: E402
    AcquisitionRequest,
    ContractConfig,
    DatasetBuilder,
    TqSdkSourceAdapter,
    credentials_from_terminal,
)
from src.historical_data import NormalizerIdentity  # noqa: E402

CN = ZoneInfo("Asia/Shanghai")

EXCHANGE = "SHFE"
GRANULARITY = 60
NORMALIZER = NormalizerIdentity(
    "tqsdk-3.10.1-fixed-bar-adapter-v1",
    "completed-historical-bar-v1",
    "bar-start-plus-duration-v1",
)
SCHEMA_VERSION = "kline-playbook-dataset-manifest-v1"

# Pilot selection justified only by data availability, concrete-contract
# lifecycle, session coverage, official cross-check availability, and
# engineering diversity (different tick size and night-session length).
PILOT_CONTRACTS = {
    "SHFE.ni2509": {"tick": "10", "night_end_hour": 1, "meta": "shfe-ni2509-contract-v1"},
    "SHFE.rb2510": {"tick": "1", "night_end_hour": 23, "meta": "shfe-rb2510-contract-v1"},
}

PILOT_TRADING_DAYS = [
    date(2025, 6, 16),
    date(2025, 6, 17),
    date(2025, 6, 18),
    date(2025, 6, 19),
    date(2025, 6, 20),
]


def _prior_evening(trading_day: date) -> date:
    # Monday night session is the prior Friday evening.
    if trading_day.weekday() == 0:
        return trading_day - timedelta(days=3)
    return trading_day - timedelta(days=1)


def _build_windows(contract: str, trading_day: date, night_end_hour: int):
    prior = _prior_evening(trading_day)
    night_start = datetime.combine(prior, time(21, 0), tzinfo=CN)
    if night_end_hour == 1:
        night_end = datetime.combine(prior + timedelta(days=1), time(1, 0), tzinfo=CN)
    else:
        night_end = datetime.combine(prior, time(night_end_hour, 0), tzinfo=CN)
    windows = [SessionWindow(EXCHANGE, contract, trading_day, night_start, night_end, "night")]
    for (h1, m1, h2, m2) in ((9, 0, 10, 15), (10, 30, 11, 30), (13, 30, 15, 0)):
        windows.append(
            SessionWindow(
                EXCHANGE,
                contract,
                trading_day,
                datetime.combine(trading_day, time(h1, m1), tzinfo=CN),
                datetime.combine(trading_day, time(h2, m2), tzinfo=CN),
                "day",
            )
        )
    return windows


def build_pilot() -> tuple[list[AcquisitionRequest], dict[str, ContractConfig]]:
    requests: list[AcquisitionRequest] = []
    contract_configs: dict[str, ContractConfig] = {}
    for contract, spec in PILOT_CONTRACTS.items():
        all_windows: list[SessionWindow] = []
        for trading_day in PILOT_TRADING_DAYS:
            windows = _build_windows(contract, trading_day, spec["night_end_hour"])
            all_windows.extend(windows)
            night_start = windows[0].start
            request = AcquisitionRequest(
                exchange=EXCHANGE,
                concrete_instrument=contract,
                trading_day=trading_day,
                granularity_seconds=GRANULARITY,
                requested_start=night_start,
                requested_end=datetime.combine(trading_day, time(15, 0), tzinfo=CN),
            )
            requests.append(request)
        sessions = SessionMetadata(f"{contract}-pilot-session-v1", all_windows)
        contract_configs[contract] = ContractConfig(
            concrete_instrument=contract,
            minimum_price_tick=Decimal(spec["tick"]),
            contract_metadata_identity=spec["meta"],
            sessions=sessions,
        )
    return requests, contract_configs


def main() -> int:
    parser = argparse.ArgumentParser(description="Pilot dataset acquisition")
    parser.add_argument(
        "--raw-dir",
        default=str(REPO_ROOT / "data" / "raw" / "historical"),
        help="ignored raw storage location",
    )
    parser.add_argument(
        "--manifest",
        default=str(REPO_ROOT / "docs" / "evidence" / "HISTORICAL_DATASET_PILOT.manifest.json"),
        help="committed manifest output path",
    )
    parser.add_argument("--fresh", action="store_true", help="remove existing pilot manifest before building")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    manifest_path = Path(args.manifest)
    if args.fresh and manifest_path.exists():
        manifest_path.unlink()

    requests, contracts = build_pilot()
    adapter = TqSdkSourceAdapter(credentials_from_terminal)
    try:
        builder = DatasetBuilder(
            adapter=adapter,
            raw_dir=raw_dir,
            manifest_path=manifest_path,
            schema_version=SCHEMA_VERSION,
            normalizer=NORMALIZER,
            contracts=contracts,
        )
        manifest = builder.build(requests)
    finally:
        adapter.close()

    print("PILOT_MANIFEST_IDENTITY=" + manifest.identity())
    print(f"PILOT_PARTITIONS={len(manifest.partitions)}")
    for partition in manifest.partitions:
        print(
            f"  {partition.contract} {partition.returned_start.date()} "
            f"rows_cov={partition.returned_start.isoformat()}..{partition.returned_end.isoformat()} "
            f"quality={partition.quality_status} data_version={partition.data_version_id[:12]}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

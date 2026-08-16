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

Session/trading-day facts come ONLY from the explicit, versioned pilot session
fixture (classified PILOT_FIXTURE); no weekday/weekend/holiday inference occurs
at runtime.  Contract metadata is bound to that fixture via
`ContractMetadataFact` (evidence-bound deterministic identity).
"""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime
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
    ContractMetadataFact,
    DatasetBuilder,
    TqSdkSourceAdapter,
    credentials_from_terminal,
)

CN = ZoneInfo("Asia/Shanghai")

EXCHANGE = "SHFE"
GRANULARITY = 60
SCHEMA_VERSION = "kline-playbook-dataset-manifest-v2"
DEFAULT_FIXTURE = REPO_ROOT / "docs" / "evidence" / "HISTORICAL_DATASET_PILOT.sessions.json"


def load_pilot_fixture(fixture_path: Path) -> dict:
    data = json.loads(Path(fixture_path).read_text(encoding="utf-8"))
    if data.get("classification") != "PILOT_FIXTURE":
        raise ValueError("pilot session fixture must be classified PILOT_FIXTURE")
    return data


def build_pilot(
    fixture_path: Path,
) -> tuple[list[AcquisitionRequest], dict[str, ContractConfig]]:
    fixture = load_pilot_fixture(fixture_path)
    requests: list[AcquisitionRequest] = []
    contract_configs: dict[str, ContractConfig] = {}
    for contract, cdata in fixture["contracts"].items():
        all_windows: list[SessionWindow] = []
        for day_str, day_data in cdata["trading_days"].items():
            trading_day = date.fromisoformat(day_str)
            requested_start = datetime.fromisoformat(day_data["requested_start"])
            requested_end = datetime.fromisoformat(day_data["requested_end"])
            for window in day_data["windows"]:
                all_windows.append(
                    SessionWindow(
                        EXCHANGE,
                        contract,
                        trading_day,
                        datetime.fromisoformat(window["start"]),
                        datetime.fromisoformat(window["end"]),
                        window["kind"],
                    )
                )
            requests.append(
                AcquisitionRequest(
                    exchange=EXCHANGE,
                    concrete_instrument=contract,
                    trading_day=trading_day,
                    granularity_seconds=GRANULARITY,
                    requested_start=requested_start,
                    requested_end=requested_end,
                )
            )
        sessions = SessionMetadata(cdata["session_metadata_version"], all_windows)
        tick = Decimal(cdata["minimum_price_tick"])
        metadata_fact = ContractMetadataFact(
            exchange=EXCHANGE,
            concrete_instrument=contract,
            minimum_price_tick=tick,
            session_metadata_version=cdata["session_metadata_version"],
            effective_start=date.fromisoformat(cdata["effective_start"]),
            effective_end=date.fromisoformat(cdata["effective_end"]),
            evidence_reference=fixture["evidence_reference"],
            evidence_classification=fixture["classification"],
        )
        contract_configs[contract] = ContractConfig(
            concrete_instrument=contract,
            minimum_price_tick=tick,
            metadata_fact=metadata_fact,
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
    parser.add_argument(
        "--fixture",
        default=str(DEFAULT_FIXTURE),
        help="explicit pilot session fixture (PILOT_FIXTURE)",
    )
    parser.add_argument("--fresh", action="store_true", help="remove existing pilot manifest before building")
    args = parser.parse_args()

    raw_dir = Path(args.raw_dir)
    manifest_path = Path(args.manifest)
    if args.fresh and manifest_path.exists():
        manifest_path.unlink()

    requests, contracts = build_pilot(Path(args.fixture))
    adapter = TqSdkSourceAdapter(credentials_from_terminal)
    try:
        builder = DatasetBuilder(
            adapter=adapter,
            raw_dir=raw_dir,
            manifest_path=manifest_path,
            schema_version=SCHEMA_VERSION,
            contracts=contracts,
        )
        manifest = builder.build(requests)
    finally:
        adapter.close()

    print("PILOT_MANIFEST_IDENTITY=" + manifest.identity())
    print(f"PILOT_PARTITIONS={len(manifest.partitions)}")
    for partition in manifest.partitions:
        print(
            f"  {partition.contract} {partition.trading_day} "
            f"rows_cov={partition.returned_start.isoformat()}..{partition.returned_end.isoformat()} "
            f"quality={partition.quality_status} data_version={partition.data_version_id[:12]}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
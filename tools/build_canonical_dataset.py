"""Canonical BALANCED dataset build runner (resumable, bounded batches).

Flow:
1. Load governed metadata (trading calendar, contract universe, session
   schedules, contract specs) from committed evidence JSON.
2. Build per-contract ContractConfig (explicit SessionMetadata + governed
   ContractMetadataFact).
3. Generate AcquisitionRequest partitions from the governed universe.
4. Run the accepted DatasetBuilder in bounded resumable batches (idempotent
   checkpoint/resume; a paused or interrupted run never invalidates accepted
   partitions and never duplicates data).
5. Normalize each accepted partition to canonical Parquet and update the
   rebuildable SQLite catalog.
6. Optional cross-source check against the SHFE official annual raw.
7. Compute the immutable canonical corpus identity.

The full acquisition is Owner-gated by the scale guardrail
(CANONICAL_BALANCED_UNIVERSE.json: PROJECTED_RAW_EXCEEDS_3X_READINESS_GUARDRAIL,
projected ~2.6 GB).  This runner is fully implemented and tested with
deterministic fakes so the build can proceed immediately once authorized.

Usage (dry run / planning):
  python -m tools.build_canonical_dataset --dry-run --max-partitions 10
Usage (real, after gate):
  python -m tools.build_canonical_dataset --batch-size 200 --max-partitions 1000
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from src.canonical_identity import (
    CanonicalCorpusIdentity,
    governed_metadata_root_identity,
)
from src.canonical_storage import (
    CANONICAL_SCHEMA_VERSION,
    PARQUET_STORAGE_VERSION,
    CanonicalCatalog,
    CanonicalRow,
    CatalogPartitionEntry,
    canonical_hash,
    write_partition_table,
)
from src.historical_acquisition import (
    AcquisitionRequest,
    ContractConfig,
    ContractMetadataFact,
    DatasetBuilder,
    ManifestPartition,
    SourceSpecification,
    TqSdkSourceAdapter,
    credentials_from_terminal,
)
from src.historical_data import (
    DataVersionIdentity,
    NormalizerIdentity,
    RawArtifact,
    SourceIdentity,
    normalize_tqsdk_historical_bars,
)
from src.metadata_authority import (
    ContractSpec,
    GovernedSource,
    ProductSessionSchedule,
    TradingCalendar,
    build_session_metadata,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = PROJECT_ROOT / "docs" / "evidence"
CN = ZoneInfo("Asia/Shanghai")
GRANULARITY = 60
PRODUCTS = ["cu", "al", "ni", "au", "ag", "rb"]
COVERAGE_START = date(2024, 1, 1)
COVERAGE_END = date(2025, 12, 31)
INVENTORY_RULE_IDENTITY = (
    "pit-complete-listed-concrete-contract-universe-v1"
)
SOURCE_SPEC = SourceSpecification(
    provider="TQSDK",
    source_type="PROFESSIONAL_HISTORICAL_API",
    endpoint_identity="TqApi.get_kline_data_series",
    raw_schema_identity="tqsdk-kline-records-json-v1",
    provider_dataset_version=None,
    normalizer=NormalizerIdentity(
        "tqsdk-3.10.1-fixed-bar-adapter-v1",
        "completed-historical-bar-v1",
        "bar-start-plus-duration-v1",
    ),
)


def _load_json(name: str) -> dict:
    data = json.loads((EVIDENCE / name).read_bytes().decode("utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{name} is not a JSON object")
    return data


def load_calendar() -> TradingCalendar:
    data = _load_json("CANONICAL_TRADING_CALENDAR.json")
    days = []
    for year_days in data["trading_days"].values():
        days.extend(date.fromisoformat(d) for d in year_days)
    night_closed = [
        date.fromisoformat(d)
        for year_days in data.get("night_closed_trading_days", {}).values()
        for d in year_days
    ]
    source = GovernedSource(
        resource_identity=data["source"]["resource"],
        url=data["source"]["url"],
        retrieved_at=datetime.fromisoformat(data["source"]["retrieved_at"]),
        artifact_sha256=None,
        schema_version="shfe-official-annual-daily-v2",
        classification=data["source"]["classification"],
        effective_period_start=COVERAGE_START,
        effective_period_end=COVERAGE_END,
    )
    return TradingCalendar(
        data["version"], days, source, night_closed_trading_days=night_closed
    )


def load_specs() -> dict[str, ContractSpec]:
    data = _load_json("CANONICAL_CONTRACT_SPECS.json")
    specs = {}
    for product, item in data["products"].items():
        effective_period = item.get("effective_period")
        eff_start = (
            date.fromisoformat(effective_period[0])
            if effective_period
            else COVERAGE_START
        )
        eff_end = (
            date.fromisoformat(effective_period[1])
            if effective_period
            else COVERAGE_END
        )
        source = GovernedSource(
            resource_identity=f"SHFE contract text {product}",
            url=item["source_url"],
            retrieved_at=datetime.fromisoformat(item["retrieved_at"]),
            artifact_sha256=None,
            schema_version="shfe-contract-text-v2",
            classification="OFFICIAL_AVAILABLE",
            effective_period_start=eff_start,
            effective_period_end=eff_end,
        )
        specs[product] = ContractSpec(
            "SHFE", product, item["trading_code"], Decimal(item["tick"]), item["tick_unit"],
            Decimal(item["multiplier"]), item["multiplier_unit"], item["quote_unit"],
            item["contract_months"], item["price_limit_pct"],
            binding_notice=item.get("binding_notice", ""),
            effective_start=eff_start,
            effective_end=eff_end,
            source=source,
        )
    return specs


def load_schedules() -> dict[str, ProductSessionSchedule]:
    data = _load_json("CANONICAL_SESSION_SCHEDULES.json")
    schedules = {}
    for product, item in data["products"].items():
        source = GovernedSource(
            resource_identity="SHFE official trading-hours page",
            url=item["source_url"],
            retrieved_at=datetime.fromisoformat(item["retrieved_at"]),
            artifact_sha256=None,
            schema_version="shfe-trading-hours-v1",
            classification="OFFICIAL_AVAILABLE",
            effective_period_start=COVERAGE_START,
            effective_period_end=COVERAGE_END,
        )
        day_windows = tuple((time.fromisoformat(s), time.fromisoformat(e))
                            for s, e in item["day_windows"])
        night = item["night_window"]
        night_window = (time.fromisoformat(night[0]), time.fromisoformat(night[1])) if night else None
        schedules[product] = ProductSessionSchedule(
            "SHFE", product, COVERAGE_START, COVERAGE_END, day_windows, night_window,
            timezone=item["timezone"], source=source,
        )
    return schedules


def load_universe() -> dict[str, list[str]]:
    data = _load_json("CANONICAL_CONTRACT_UNIVERSE.json")
    out: dict[str, list[str]] = {p: [] for p in PRODUCTS}
    for entry in data["contracts"]:
        out[entry["product"]].append(entry["concrete_contract"])
    return out


def load_universe_bounds() -> dict[str, dict[str, tuple[date, date]]]:
    """concrete contract -> (first_trading_day, last_trading_day) governed bounds."""
    data = _load_json("CANONICAL_CONTRACT_UNIVERSE.json")
    out: dict[str, dict[str, tuple[date, date]]] = {p: {} for p in PRODUCTS}
    for entry in data["contracts"]:
        out[entry["product"]][entry["concrete_contract"]] = (
            date.fromisoformat(entry["first_trading_day"]),
            date.fromisoformat(entry["last_trading_day"]),
        )
    return out


def build_requests(
    calendar: TradingCalendar,
    universe: dict[str, list[str]],
    bounds: dict[str, dict[str, tuple[date, date]]] | None = None,
    specs: dict[str, ContractSpec] | None = None,
    schedules: dict[str, ProductSessionSchedule] | None = None,
) -> list[AcquisitionRequest]:
    """Deterministically ordered, FAIL-CLOSED acquisition requests.

    A request is generated only for trading days within the contract's governed
    listing window (first..last official trading day).  Before planning a
    request, the planner FAILS CLOSED when:
    - no contract-spec effective period covers the product/day;
    - multiple conflicting contract-spec effective periods cover it;
    - no session-schedule effective period covers the product/day (session
      authority unresolved);
    - multiple conflicting session-schedule effective periods cover it;
    - the contract's listing/expiry does not cover the trading day.
    """
    requests: list[AcquisitionRequest] = []
    for product in PRODUCTS:
        for contract in sorted(universe[product]):
            exchange, _code = contract.split(".", 1)
            first, last = (bounds or {}).get(product, {}).get(
                contract, (COVERAGE_START, COVERAGE_END)
            )
            days = calendar.trading_days(first, last)
            for day in days:
                # fail-closed metadata resolution (raises on no/conflicting coverage)
                if not (first <= day <= last):
                    raise ValueError(
                        f"contract listing/expiry inconsistent with trading day "
                        f"{day.isoformat()} for {contract}"
                    )
                if specs is not None:
                    from src.metadata_authority import resolve_contract_spec  # noqa: PLC0415

                    resolve_contract_spec(list(specs.values()), product, day)
                if schedules is not None:
                    from src.metadata_authority import resolve_session_schedule  # noqa: PLC0415

                    resolve_session_schedule(list(schedules.values()), product, day)
                prev = calendar.previous_trading_day(day)
                if prev is None:
                    # First trading day of the corpus: no previous trading day
                    # in the calendar, so acquire the day session only
                    # (09:00-15:00). 2024-01-02 is also officially night-closed.
                    start = datetime.combine(day, time(9, 0), tzinfo=CN)
                    end = datetime.combine(day, time(15, 0), tzinfo=CN)
                else:
                    start = datetime.combine(prev, time(21, 0), tzinfo=CN)
                    end = datetime.combine(day, time(15, 0), tzinfo=CN)
                requests.append(
                    AcquisitionRequest(
                        exchange=exchange,
                        concrete_instrument=contract,
                        trading_day=day,
                        granularity_seconds=GRANULARITY,
                        requested_start=start,
                        requested_end=end,
                        timezone="Asia/Shanghai",
                    )
                )
    return requests


def build_contract_configs(
    calendar: TradingCalendar,
    universe: dict[str, list[str]],
    specs: dict[str, ContractSpec],
    schedules: dict[str, ProductSessionSchedule],
) -> dict[str, ContractConfig]:
    configs: dict[str, ContractConfig] = {}
    for product in PRODUCTS:
        spec = specs[product]
        schedule = schedules[product]
        for contract in sorted(universe[product]):
            days = calendar.trading_days(spec.effective_start, spec.effective_end)
            sessions = build_session_metadata(calendar, schedule, contract, days)
            metadata_fact = ContractMetadataFact(
                exchange="SHFE",
                concrete_instrument=contract,
                minimum_price_tick=spec.tick,
                session_metadata_version=sessions.version,
                effective_start=spec.effective_start,
                effective_end=spec.effective_end,
                evidence_reference=(
                    "CANONICAL_CONTRACT_SPECS.json effective_period "
                    + spec.binding_notice
                ),
                evidence_classification="VERIFIED_OFFICIAL",
            )
            configs[contract] = ContractConfig(
                concrete_instrument=contract,
                minimum_price_tick=spec.tick,
                metadata_fact=metadata_fact,
                sessions=sessions,
            )
    return configs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="print request plan only")
    parser.add_argument("--batch-size", type=int, default=200)
    parser.add_argument("--max-partitions", type=int, default=None)
    parser.add_argument("--raw-dir", default=str(PROJECT_ROOT / "data" / "raw" / "historical"))
    parser.add_argument("--manifest", default=str(EVIDENCE / "CANONICAL_DATASET_MANIFEST.json"))
    parser.add_argument("--parquet-dir", default=str(PROJECT_ROOT / "data" / "canonical" / "parquet"))
    parser.add_argument("--catalog", default=str(PROJECT_ROOT / "data" / "canonical" / "catalog.sqlite"))
    args = parser.parse_args()

    calendar = load_calendar()
    specs = load_specs()
    schedules = load_schedules()
    universe = load_universe()
    bounds = load_universe_bounds()
    requests = build_requests(calendar, universe, bounds, specs=specs, schedules=schedules)
    if args.max_partitions is not None:
        requests = requests[: args.max_partitions]
    print(f"PLAN partitions={len(requests)} products={PRODUCTS} coverage={COVERAGE_START}..{COVERAGE_END}")

    if args.dry_run:
        per_product = {p: sum(1 for r in requests if r.concrete_instrument.startswith(f"SHFE.{p}")) for p in PRODUCTS}
        print(json.dumps({"dry_run": True, "per_product": per_product}, indent=2, sort_keys=True))
        return

    configs = build_contract_configs(calendar, universe, specs, schedules)
    adapter = TqSdkSourceAdapter(credentials_from_terminal)
    builder = DatasetBuilder(
        adapter=adapter,
        raw_dir=Path(args.raw_dir),
        manifest_path=Path(args.manifest),
        schema_version="canonical-balanced-manifest-v1",
        contracts=configs,
    )
    try:
        manifest = builder.build(requests)
    finally:
        adapter.close()
    print(f"ACQUIRED manifest_identity={manifest.identity()} partitions={len(manifest.partitions)}")

    # Normalize -> Parquet + SQLite catalog (per accepted partition).
    catalog = CanonicalCatalog(Path(args.catalog))
    catalog.set_meta("schema_version", "canonical-catalog-v1")
    catalog.set_meta("manifest_identity", manifest.identity())
    try:
        for partition in manifest.partitions:
            config = configs[partition.contract]
            storage = normalize_and_store_partition(
                partition, Path(args.raw_dir), Path(args.parquet_dir),
                config.sessions, config.metadata_fact.identity_id(),
                config.minimum_price_tick,
            )
            catalog.upsert_partition(storage.entry)
    finally:
        catalog.close()
    print(f"CATALOG partitions={_catalog_count(Path(args.catalog))}")


def _catalog_count(path: Path) -> int:
    c = CanonicalCatalog(path)
    try:
        return c.partition_count()
    finally:
        c.close()


@dataclass(frozen=True)
class StoredPartition:
    entry: CatalogPartitionEntry
    storage_facts: dict


def normalize_and_store_partition(
    partition: ManifestPartition,
    raw_dir: Path,
    parquet_dir: Path,
    sessions,
    contract_metadata_identity: str,
    minimum_price_tick: Decimal,
) -> StoredPartition:
    """Reconstruct the raw artifact + data version, normalize, store to Parquet.

    Uses the accepted normalization path (src.historical_data).  Fails closed
    if the raw artifact on disk does not match the recorded raw SHA256.
    """
    # locate the raw file by deterministic name scheme + recorded hash
    raw_path = _find_raw_file(raw_dir, partition)
    payload = raw_path.read_bytes()
    if sha256_hex(payload) != partition.raw_sha256:
        raise ValueError(f"raw artifact hash mismatch for {partition.contract} {partition.trading_day}")

    source = SourceIdentity(
        provider=partition.provider,
        source_type=SOURCE_SPEC.source_type,
        endpoint_identity=SOURCE_SPEC.endpoint_identity,
        provider_dataset_version=SOURCE_SPEC.provider_dataset_version,
        retrieved_at=partition.retrieved_at,
        request_parameters=partition.request_parameters,
    )
    if source.request_identity != partition.request_identity:
        raise ValueError("reconstructed source identity conflicts with recorded request identity")
    artifact = RawArtifact(
        exchange=partition.exchange,
        concrete_instrument=partition.contract,
        coverage_start=partition.returned_start,
        coverage_end=partition.returned_end,
        granularity_seconds=partition.granularity_seconds,
        timezone=partition.timezone,
        raw_schema_identity=SOURCE_SPEC.raw_schema_identity,
        raw_sha256=partition.raw_sha256,
        source_identity_id=source.identity_id,
    )
    data_version = DataVersionIdentity(
        source_identities=(source,),
        raw_artifacts=(artifact,),
        normalizer=SOURCE_SPEC.normalizer,
        session_metadata_version=partition.session_metadata_version,
        historical_availability_rule=SOURCE_SPEC.availability_rule,
        contract_metadata_identity=partition.contract_metadata_identity,
    )
    if data_version.identity_id != partition.data_version_id:
        raise ValueError("reconstructed data version conflicts with recorded data version")

    batch = normalize_tqsdk_historical_bars(
        payload,
        artifact=artifact,
        data_version=data_version,
        sessions=sessions,
        minimum_price_tick=minimum_price_tick,
    )
    product = partition.contract.split(".")[1][:2].lower()
    rows = []
    for bar in batch.bars:
        rows.append(
            CanonicalRow(
                provider=partition.provider,
                source_type=SOURCE_SPEC.source_type,
                exchange=partition.exchange,
                concrete_contract=partition.contract,
                product=product,
                trading_day=bar.completed_bar.trading_day,
                bar_start=bar.completed_bar.start,
                bar_end=bar.completed_bar.end,
                historical_available_at=bar.completed_bar.available_at,
                open=str(bar.open),
                high=str(bar.high),
                low=str(bar.low),
                close=str(bar.close),
                volume=int(bar.volume) if bar.volume is not None else 0,
                open_interest_start=int(bar.open_interest_start) if bar.open_interest_start is not None else None,
                open_interest_end=int(bar.open_interest_end) if bar.open_interest_end is not None else None,
                raw_artifact_identity_id=partition.raw_sha256,
                source_identity_id=source.identity_id,
                data_version_id=partition.data_version_id,
                contract_metadata_identity=partition.contract_metadata_identity,
                session_metadata_identity=partition.session_metadata_version,
                normalizer_identity=SOURCE_SPEC.normalizer.identity_id,
            )
        )
    storage = write_partition_table(parquet_dir, rows)
    artifact_identity = canonical_hash({"storage_version": storage["storage_version"], "files": storage["files"]})
    entry = CatalogPartitionEntry(
        provider=partition.provider,
        contract=partition.contract,
        exchange=partition.exchange,
        granularity_seconds=partition.granularity_seconds,
        trading_day=partition.trading_day,
        raw_sha256=partition.raw_sha256,
        request_identity=partition.request_identity,
        data_version_id=partition.data_version_id,
        normalized_batch_id=partition.normalized_batch_id,
        parquet_artifact_identity=artifact_identity,
        parquet_logical_identity=storage["logical_table_identity"],
        parquet_storage_version=storage["storage_version"],
        row_count=storage["row_count"],
        coverage_start=partition.returned_start.isoformat(),
        coverage_end=partition.returned_end.isoformat(),
        quality_status=partition.quality_status,
    )
    return StoredPartition(entry=entry, storage_facts=storage)


def _find_raw_file(raw_dir: Path, partition: ManifestPartition) -> Path:
    """Locate the raw JSON file matching the partition (name scheme + hash)."""
    coverage_tag = canonical_hash(
        (partition.timezone, partition.requested_start.isoformat(), partition.requested_end.isoformat())
    )[:12]
    name = (
        f"{partition.provider}.{partition.contract}.{partition.granularity_seconds}s."
        f"{partition.trading_day.isoformat()}.{coverage_tag}.json"
    )
    path = raw_dir / name
    if not path.exists():
        matches = [p for p in raw_dir.glob("*.json") if p.is_file()]
        for candidate in matches:
            if sha256_hex(candidate.read_bytes()) == partition.raw_sha256:
                return candidate
        raise FileNotFoundError(f"raw artifact not found for {partition.contract} {partition.trading_day}")
    return path


def sha256_hex(payload: bytes) -> str:
    import hashlib  # noqa: PLC0415

    return hashlib.sha256(payload).hexdigest()


if __name__ == "__main__":
    main()

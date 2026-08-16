"""Small project-owned historical-data acquisition boundary (pilot).

Vendor-neutral request, storage, resume, and manifest logic is separated from
the TqSdk-specific source adapter.  TqSdk is imported lazily and only inside
the adapter, so the project runtime never depends on it.

Safety:
- concrete contracts only; pseudo MAIN/CONTINUOUS symbols are rejected;
- credentials are supplied only at runtime (hidden local password input);
- no credential is stored in the repo, config, evidence, logs, or manifests;
- no broker or order functionality is exposed.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
import getpass
import json
import math
import os
import re
from pathlib import Path
from typing import Callable, Iterable
from zoneinfo import ZoneInfo

from src.data_substrate import SessionMetadata
from src.historical_data import (
    DataVersionIdentity,
    NormalizerIdentity,
    RawArtifact,
    SourceIdentity,
    normalize_tqsdk_historical_bars,
)
from src.historical_manifest import DatasetManifest, ManifestPartition

_RAW_SCHEMA_IDENTITY = "tqsdk-kline-records-json-v1"
_AVAILABILITY_RULE = "bar-start-plus-duration-v1"
_PROVIDER = "TQSDK"
_SOURCE_TYPE = "PROFESSIONAL_HISTORICAL_API"
_ENDPOINT = "TqApi.get_kline_data_series"

_CONCRETE = re.compile(r"^[A-Z]+\.[A-Za-z]+[0-9]{3,4}$")
_PSEUDO = re.compile(r"MAIN|CONTINUOUS|KQ\.m@|KQ\.i@|888|000", re.IGNORECASE)


class AcquisitionError(Exception):
    """Base acquisition error."""


class RawPartitionConflictError(AcquisitionError):
    """Existing raw content conflicts with the recorded manifest."""


class InvalidConcreteSymbolError(AcquisitionError):
    """Pseudo MAIN/CONTINUOUS or non-concrete symbols are forbidden."""


def validate_concrete_symbol(symbol: str) -> str:
    """Reject pseudo MAIN/CONTINUOUS or non-concrete contract symbols."""
    if not isinstance(symbol, str) or not symbol.strip():
        raise InvalidConcreteSymbolError("concrete instrument is required")
    if not _CONCRETE.fullmatch(symbol):
        raise InvalidConcreteSymbolError(f"symbol {symbol!r} is not a concrete contract")
    if _PSEUDO.search(symbol):
        raise InvalidConcreteSymbolError(f"pseudo MAIN/CONTINUOUS symbol {symbol!r} is forbidden")
    return symbol


@dataclass(frozen=True)
class AcquisitionRequest:
    """One concrete-contract/date partition request (no credentials)."""

    exchange: str
    concrete_instrument: str
    trading_day: date
    granularity_seconds: int
    requested_start: datetime
    requested_end: datetime
    timezone: str = "Asia/Shanghai"

    def __post_init__(self) -> None:
        if not self.exchange.strip():
            raise ValueError("exchange is required")
        validate_concrete_symbol(self.concrete_instrument)
        if not self.concrete_instrument.startswith(self.exchange + "."):
            raise ValueError("exchange and concrete instrument disagree")
        if self.requested_start.tzinfo is None or self.requested_end.tzinfo is None:
            raise ValueError("requested coverage must be timezone-aware")
        if self.requested_end <= self.requested_start:
            raise ValueError("requested coverage end must follow its start")
        if type(self.granularity_seconds) is not int or self.granularity_seconds <= 0:
            raise ValueError("granularity must be positive whole seconds")

    @property
    def partition_key(self) -> tuple:
        # Must match ManifestPartition.partition_key so resume matching works.
        return (self.concrete_instrument, self.granularity_seconds, self.requested_start.isoformat())

    @property
    def raw_file_name(self) -> str:
        return f"{self.concrete_instrument}.{self.granularity_seconds}s.{self.trading_day.isoformat()}.json"


@dataclass(frozen=True)
class AcquisitionResult:
    """Raw acquisition result (in-memory only; no credentials)."""

    request: AcquisitionRequest
    payload: bytes
    returned_start: datetime
    returned_end: datetime  # last bar end = last bar start + granularity
    rows: int
    provider_version: str


@dataclass(frozen=True)
class ContractConfig:
    """Contract-specific facts for normalization (no strategy semantics)."""

    concrete_instrument: str
    minimum_price_tick: Decimal
    contract_metadata_identity: str
    sessions: SessionMetadata


class SourceAdapter(ABC):
    """Acquisition boundary.  Concrete adapters must not expose order APIs."""

    @abstractmethod
    def acquire(self, request: AcquisitionRequest) -> AcquisitionResult:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


def _to_int(value: object) -> int:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        raise AcquisitionError("missing or NaN integer field in source response")
    return int(value)


def _to_price(value: object) -> float:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        raise AcquisitionError("missing or NaN price field in source response")
    return float(value)


def dataframe_to_records(frame, symbol: str) -> list[dict]:
    """Convert a TqSdk K-line DataFrame to the project raw JSON records."""
    records: list[dict] = []
    for row in frame.itertuples(index=False):
        records.append(
            {
                "id": _to_int(row.id),
                "datetime": _to_int(row.datetime),
                "open": _to_price(row.open),
                "high": _to_price(row.high),
                "low": _to_price(row.low),
                "close": _to_price(row.close),
                "volume": _to_int(row.volume),
                "open_oi": _to_int(row.open_oi),
                "close_oi": _to_int(row.close_oi),
                "symbol": symbol,
            }
        )
    return records


class TqSdkSourceAdapter(SourceAdapter):
    """TqSdk-backed adapter.  TqSdk is imported lazily and only here.

    Credentials come from a runtime provider (e.g. hidden terminal input) and
    exist only in memory; TqAuth is constructed per connection and disappears
    when the process exits.  No broker/order API is used.
    """

    def __init__(
        self,
        credentials_provider: Callable[[], tuple[str, str]],
        *,
        max_connect_attempts: int = 3,
    ) -> None:
        self._credentials_provider = credentials_provider
        self._max_connect_attempts = max_connect_attempts
        self._api = None
        self._version: str | None = None

    def _connect(self) -> None:
        if self._api is not None:
            return
        import tqsdk  # lazy: project runtime does not depend on TqSdk
        from tqsdk import TqApi, TqAuth

        account, password = self._credentials_provider()
        if not account or not password:
            raise AcquisitionError("credentials are required at runtime")
        auth = TqAuth(account, password)  # in-memory only
        last_error: Exception | None = None
        for attempt in range(1, self._max_connect_attempts + 1):
            try:
                self._api = TqApi(auth=auth, disable_print=True)  # data server only
                break
            except Exception as exc:  # noqa: BLE001 - bounded transient retry
                last_error = exc
                self._api = None
                if attempt < self._max_connect_attempts:
                    continue
        if self._api is None:
            raise AcquisitionError(f"TqSdk connection failed: {last_error!r}")
        self._version = getattr(tqsdk, "__version__", "UNKNOWN")

    def acquire(self, request: AcquisitionRequest) -> AcquisitionResult:
        self._connect()
        if self._api is None:
            raise AcquisitionError("TqSdk connection is unavailable")
        frame = self._api.get_kline_data_series(
            request.concrete_instrument,
            duration_seconds=request.granularity_seconds,
            start_dt=request.requested_start,
            end_dt=request.requested_end,
        )
        if frame is None or len(frame) == 0:
            raise AcquisitionError(f"no rows returned for {request.concrete_instrument}")
        records = dataframe_to_records(frame, request.concrete_instrument)
        payload = json.dumps(records, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
        zone = ZoneInfo(request.timezone)
        returned_start = datetime.fromtimestamp(records[0]["datetime"] / 1_000_000_000, tz=zone)
        returned_end = datetime.fromtimestamp(records[-1]["datetime"] / 1_000_000_000, tz=zone) + timedelta(
            seconds=request.granularity_seconds
        )
        return AcquisitionResult(
            request=request,
            payload=payload,
            returned_start=returned_start,
            returned_end=returned_end,
            rows=len(records),
            provider_version=self._version or "UNKNOWN",
        )

    def close(self) -> None:
        if self._api is not None:
            try:
                self._api.close()
            finally:
                self._api = None


def credentials_from_terminal() -> tuple[str, str]:
    """Runtime-only hidden credential input; nothing is persisted."""
    account = input("TqSdk account: ").strip()
    if not account:
        raise AcquisitionError("no account entered")
    password = getpass.getpass("TqSdk password (hidden): ")
    if not password:
        raise AcquisitionError("no password entered")
    return account, password


class DatasetBuilder:
    """Small idempotent dataset builder for the pilot.

    Resume semantics (no download manager):
    - manifest entry + on-disk raw hash match  -> skip (idempotent);
    - manifest entry + on-disk raw hash differ -> fail closed (conflict);
    - manifest entry + on-disk raw missing     -> acquire (explicit new version);
    - no manifest entry                        -> acquire; a `.partial` file is
      never accepted and is replaced.
    """

    def __init__(
        self,
        *,
        adapter: SourceAdapter,
        raw_dir: Path,
        manifest_path: Path,
        schema_version: str,
        normalizer: NormalizerIdentity,
        contracts: dict[str, ContractConfig],
        retrieved_at_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._adapter = adapter
        self._raw_dir = Path(raw_dir)
        self._manifest_path = Path(manifest_path)
        self._schema_version = schema_version
        self._normalizer = normalizer
        self._contracts = dict(contracts)
        self._retrieved_at_provider = retrieved_at_provider or (
            lambda: datetime.now(ZoneInfo("UTC"))
        )

    def build(self, requests: Iterable[AcquisitionRequest]) -> DatasetManifest:
        request_list = list(requests)
        if not request_list:
            raise AcquisitionError("no acquisition requests supplied")
        for request in request_list:
            if request.concrete_instrument not in self._contracts:
                raise AcquisitionError(
                    f"no contract config for {request.concrete_instrument}"
                )

        existing = self._load_existing_entries()
        entries: dict[tuple, ManifestPartition] = dict(existing)
        for request in sorted(request_list, key=lambda r: r.partition_key):
            key = request.partition_key
            raw_path = self._raw_dir / request.raw_file_name
            partial_path = raw_path.with_suffix(raw_path.suffix + ".partial")
            prior = entries.get(key)
            if prior is not None and raw_path.exists():
                on_disk_hash = sha256(raw_path.read_bytes()).hexdigest()
                if on_disk_hash == prior.raw_sha256:
                    continue  # idempotent skip
                raise RawPartitionConflictError(
                    f"raw partition {key} conflicts with recorded manifest "
                    f"(recorded {prior.raw_sha256}, on disk {on_disk_hash})"
                )
            # acquire (or re-acquire): partial files are never accepted
            if partial_path.exists():
                partial_path.unlink()
            entry = self._acquire_partition(request, raw_path, partial_path)
            entries[key] = entry
            self._save_manifest_entries(entries)
        return self._save_manifest_entries(entries)

    def _load_existing_entries(self) -> dict[tuple, ManifestPartition]:
        if not self._manifest_path.exists():
            return {}
        manifest = DatasetManifest.load(self._manifest_path)
        return {item.partition_key: item for item in manifest.partitions}

    def _acquire_partition(
        self, request: AcquisitionRequest, raw_path: Path, partial_path: Path
    ) -> ManifestPartition:
        result = self._adapter.acquire(request)
        payload = result.payload
        raw_path.parent.mkdir(parents=True, exist_ok=True)
        partial_path.write_bytes(payload)
        os.replace(partial_path, raw_path)  # atomic: never a partial final file
        config = self._contracts[request.concrete_instrument]
        retrieved_at = self._retrieved_at_provider()
        source = SourceIdentity(
            provider=_PROVIDER,
            source_type=_SOURCE_TYPE,
            endpoint_identity=_ENDPOINT,
            provider_dataset_version=None,
            retrieved_at=retrieved_at,
            request_parameters=(
                ("duration_seconds", str(request.granularity_seconds)),
                ("end_dt", request.requested_end.isoformat()),
                ("start_dt", request.requested_start.isoformat()),
                ("symbol", request.concrete_instrument),
            ),
        )
        artifact = RawArtifact.from_bytes(
            payload=payload,
            exchange=request.exchange,
            concrete_instrument=request.concrete_instrument,
            coverage_start=result.returned_start,
            coverage_end=result.returned_end,
            granularity_seconds=request.granularity_seconds,
            timezone=request.timezone,
            raw_schema_identity=_RAW_SCHEMA_IDENTITY,
            source_identity_id=source.identity_id,
        )
        data_version = DataVersionIdentity(
            source_identities=(source,),
            raw_artifacts=(artifact,),
            normalizer=self._normalizer,
            session_metadata_version=config.sessions.version,
            historical_availability_rule=_AVAILABILITY_RULE,
            contract_metadata_identity=config.contract_metadata_identity,
        )
        batch = normalize_tqsdk_historical_bars(
            payload,
            artifact=artifact,
            data_version=data_version,
            sessions=config.sessions,
            minimum_price_tick=config.minimum_price_tick,
        )
        quality = (
            "PASS"
            if not batch.missing_expected_starts
            else f"ANOMALY:missing_expected_starts={len(batch.missing_expected_starts)}"
        )
        return ManifestPartition(
            provider=_PROVIDER,
            api_version=result.provider_version,
            contract=request.concrete_instrument,
            exchange=request.exchange,
            granularity_seconds=request.granularity_seconds,
            requested_start=request.requested_start,
            requested_end=request.requested_end,
            returned_start=result.returned_start,
            returned_end=result.returned_end,
            retrieved_at=retrieved_at,
            raw_bytes=len(payload),
            raw_sha256=sha256(payload).hexdigest(),
            request_identity=source.request_identity,
            normalizer_identity=self._normalizer.identity_id,
            session_metadata_version=config.sessions.version,
            data_version_id=data_version.identity_id,
            normalized_batch_id=batch.identity_id,
            quality_status=quality,
        )

    def _save_manifest_entries(
        self, entries: dict[tuple, ManifestPartition]
    ) -> DatasetManifest:
        manifest = DatasetManifest(self._schema_version, tuple(entries.values()))
        self._manifest_path.parent.mkdir(parents=True, exist_ok=True)
        temp = self._manifest_path.with_suffix(self._manifest_path.suffix + ".tmp")
        temp.write_bytes(manifest.to_json_bytes())
        os.replace(temp, self._manifest_path)
        return manifest

"""Project-owned historical-data acquisition boundary (hardened).

Vendor-neutral acquisition, storage, resume, and manifest behavior is separated
from source/provider-specific facts.  A `SourceAdapter` exposes an immutable
`SourceSpecification` (provider, source type, endpoint, raw schema, version,
normalizer, availability rule) and the decoding behavior; the generic
`DatasetBuilder` never assumes a specific provider.

Safety:
- concrete contracts only; pseudo MAIN/CONTINUOUS symbols are rejected;
- credentials are supplied only at runtime (hidden local password input);
- no credential is stored in the repo, config, evidence, logs, or manifests;
- no broker or order functionality is exposed;
- only clearly transient transport/network errors are retried (bounded);
- session/trading-day facts are never inferred; explicit, versioned
  `SessionMetadata` is required from project authority.
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
    NormalizedHistoricalBatch,
    RawArtifact,
    SourceIdentity,
)
from src.historical_manifest import DatasetManifest, ManifestPartition, canonical_hash

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
        # Every outcome-affecting request dimension (excluding provider, which
        # the builder prepends from the adapter's SourceSpecification).
        return (
            self.concrete_instrument,
            self.granularity_seconds,
            self.timezone,
            self.trading_day.isoformat(),
            self.requested_start.isoformat(),
            self.requested_end.isoformat(),
        )

    def raw_file_name(self, provider: str) -> str:
        # Collision-safe for distinguishable logical requests: provider plus a
        # coverage tag derived from timezone/requested coverage.
        coverage_tag = canonical_hash(
            (self.timezone, self.requested_start.isoformat(), self.requested_end.isoformat())
        )[:12]
        return (
            f"{provider}.{self.concrete_instrument}.{self.granularity_seconds}s."
            f"{self.trading_day.isoformat()}.{coverage_tag}.json"
        )


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
class SourceSpecification:
    """Immutable source/provider facts owned by the adapter, not the builder."""

    provider: str
    source_type: str
    endpoint_identity: str
    raw_schema_identity: str
    provider_dataset_version: str | None
    normalizer: NormalizerIdentity
    request_parameter_names: tuple[str, ...] = (
        "duration_seconds",
        "end_dt",
        "start_dt",
        "symbol",
    )
    availability_rule: str = "bar-start-plus-duration-v1"

    def __post_init__(self) -> None:
        for value, name in (
            (self.provider, "source provider"),
            (self.source_type, "source type"),
            (self.endpoint_identity, "source endpoint identity"),
            (self.raw_schema_identity, "source raw schema identity"),
            (self.availability_rule, "source availability rule"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        if self.provider_dataset_version is not None and not str(self.provider_dataset_version).strip():
            raise ValueError("provider dataset version must be non-empty")
        if not isinstance(self.normalizer, NormalizerIdentity):
            raise ValueError("source specification requires a NormalizerIdentity")
        names = tuple(self.request_parameter_names)
        if names != tuple(sorted(names)) or len(names) != len(set(names)):
            raise ValueError("source request parameter names must be sorted and unique")
        for name in names:
            if not isinstance(name, str) or not name.strip():
                raise ValueError("source request parameter names must be non-empty strings")


def build_request_parameters(
    request: AcquisitionRequest, parameter_names: tuple[str, ...]
) -> tuple[tuple[str, str], ...]:
    """Map source-declared parameter names to non-secret request values."""
    mapping = {
        "duration_seconds": str(request.granularity_seconds),
        "start_dt": request.requested_start.isoformat(),
        "end_dt": request.requested_end.isoformat(),
        "symbol": request.concrete_instrument,
    }
    return tuple((name, mapping[name]) for name in parameter_names)


@dataclass(frozen=True)
class ContractMetadataFact:
    """Deterministic, evidence-bound contract/session metadata fact.

    Binds exchange, concrete-contract applicability, minimum tick, effective
    period, session metadata version, and the source/evidence reference so the
    resulting identity is not an arbitrary label.  Classification is honest:
    `VERIFIED_OFFICIAL` or `PILOT_FIXTURE`.
    """

    exchange: str
    concrete_instrument: str
    minimum_price_tick: Decimal
    session_metadata_version: str
    effective_start: date
    effective_end: date
    evidence_reference: str
    evidence_classification: str
    source_artifact_sha256: str | None = None

    def __post_init__(self) -> None:
        for value, name in (
            (self.exchange, "metadata exchange"),
            (self.concrete_instrument, "metadata concrete instrument"),
            (self.session_metadata_version, "metadata session metadata version"),
            (self.evidence_reference, "metadata evidence reference"),
            (self.evidence_classification, "metadata evidence classification"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} is required")
        validate_concrete_symbol(self.concrete_instrument)
        if not self.concrete_instrument.startswith(self.exchange + "."):
            raise ValueError("metadata exchange and contract disagree")
        if type(self.minimum_price_tick) is not Decimal or self.minimum_price_tick <= 0:
            raise ValueError("metadata minimum price tick must be a positive Decimal")
        if self.effective_end < self.effective_start:
            raise ValueError("metadata effective period is reversed")
        if self.evidence_classification not in ("VERIFIED_OFFICIAL", "PILOT_FIXTURE"):
            raise ValueError("metadata evidence classification must be VERIFIED_OFFICIAL or PILOT_FIXTURE")
        if self.source_artifact_sha256 is not None and not re.fullmatch(r"[0-9a-f]{64}", self.source_artifact_sha256):
            raise ValueError("metadata source artifact SHA256 must be 64 lowercase hexadecimal characters")

    def identity_id(self) -> str:
        return canonical_hash(
            {
                "exchange": self.exchange,
                "concrete_instrument": self.concrete_instrument,
                "minimum_price_tick": str(self.minimum_price_tick),
                "session_metadata_version": self.session_metadata_version,
                "effective_start": self.effective_start.isoformat(),
                "effective_end": self.effective_end.isoformat(),
                "evidence_reference": self.evidence_reference,
                "evidence_classification": self.evidence_classification,
                "source_artifact_sha256": self.source_artifact_sha256,
            }
        )


@dataclass(frozen=True)
class ContractConfig:
    """Contract-specific facts for normalization (no strategy semantics)."""

    concrete_instrument: str
    minimum_price_tick: Decimal
    metadata_fact: ContractMetadataFact
    sessions: SessionMetadata

    def __post_init__(self) -> None:
        if self.metadata_fact.concrete_instrument != self.concrete_instrument:
            raise ValueError("contract config and metadata fact disagree on contract")
        if self.metadata_fact.minimum_price_tick != self.minimum_price_tick:
            raise ValueError("contract config and metadata fact disagree on minimum tick")
        if self.metadata_fact.session_metadata_version != self.sessions.version:
            raise ValueError("contract config and metadata fact disagree on session metadata version")

    @property
    def contract_metadata_identity(self) -> str:
        return self.metadata_fact.identity_id()


class SourceAdapter(ABC):
    """Acquisition boundary.  Concrete adapters must not expose order APIs."""

    @property
    @abstractmethod
    def source_specification(self) -> SourceSpecification:
        raise NotImplementedError

    @abstractmethod
    def acquire(self, request: AcquisitionRequest) -> AcquisitionResult:
        raise NotImplementedError

    @abstractmethod
    def decode(
        self,
        payload: bytes,
        *,
        artifact: RawArtifact,
        data_version: DataVersionIdentity,
        sessions: SessionMetadata,
        minimum_price_tick: Decimal | None,
    ) -> NormalizedHistoricalBatch:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError


# --- transient retry classification ----------------------------------------

_TRANSIENT_ERROR_FQN = frozenset(
    {
        "requests.exceptions.SSLError",
        "requests.exceptions.ConnectionError",
        "requests.exceptions.Timeout",
        "requests.exceptions.ConnectTimeout",
        "requests.exceptions.ReadTimeout",
        "requests.exceptions.ChunkedEncodingError",
        "urllib3.exceptions.SSLError",
        "urllib3.exceptions.ConnectionError",
        "urllib3.exceptions.ProtocolError",
        "urllib3.exceptions.NewConnectionError",
        "urllib3.exceptions.MaxRetryError",
        "urllib3.exceptions.ReadTimeoutError",
        "urllib3.exceptions.ConnectTimeoutError",
        "socket.timeout",
    }
)


def is_transient_network_error(exc: BaseException) -> bool:
    """True only for clearly transient transport/network failures."""
    fqn = f"{type(exc).__module__}.{type(exc).__name__}"
    if fqn in _TRANSIENT_ERROR_FQN:
        return True
    return isinstance(exc, (ConnectionError, TimeoutError, OSError))


def retry_decision(attempt: int, max_attempts: int, error: BaseException) -> tuple[bool, str]:
    """Bounded retry only for transient network errors; otherwise fail closed."""
    if not is_transient_network_error(error):
        return (False, f"non-transient error {type(error).__name__}")
    if attempt >= max_attempts:
        return (False, "max attempts reached")
    return (True, "transient network error")


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
    when the process exits.  No broker/order API is used.  Only clearly
    transient transport/network errors receive bounded retry; authentication,
    entitlement, and configuration failures fail closed immediately.
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

    @property
    def source_specification(self) -> SourceSpecification:
        return SourceSpecification(
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

    def _open_api(self, auth):
        """Open a data-only TqApi.  Overridable for deterministic tests."""
        import tqsdk  # lazy: project runtime does not depend on TqSdk
        from tqsdk import TqApi

        self._version = getattr(tqsdk, "__version__", "UNKNOWN")
        return TqApi(auth=auth, disable_print=True)

    def _build_auth(self, account: str, password: str):
        """Build an in-memory TqAuth.  Overridable for deterministic tests."""
        from tqsdk import TqAuth  # lazy import, only reached for real connections

        return TqAuth(account, password)

    def _connect(self) -> None:
        if self._api is not None:
            return
        account, password = self._credentials_provider()
        if not account or not password:
            raise AcquisitionError("credentials are required at runtime")
        auth = self._build_auth(account, password)  # in-memory only
        last_error: Exception | None = None
        stop_reason = "connection not attempted"
        for attempt in range(1, self._max_connect_attempts + 1):
            try:
                self._api = self._open_api(auth)  # data server only
                break
            except Exception as exc:  # noqa: BLE001 - classified below
                self._api = None
                last_error = exc
                should_retry, stop_reason = retry_decision(
                    attempt, self._max_connect_attempts, exc
                )
                if not should_retry:
                    break
        if self._api is None:
            raise AcquisitionError(
                f"TqSdk connection failed ({stop_reason}): {type(last_error).__name__}"
            )

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

    def decode(
        self,
        payload: bytes,
        *,
        artifact: RawArtifact,
        data_version: DataVersionIdentity,
        sessions: SessionMetadata,
        minimum_price_tick: Decimal | None,
    ) -> NormalizedHistoricalBatch:
        from src.historical_data import normalize_tqsdk_historical_bars  # provider-specific decode

        return normalize_tqsdk_historical_bars(
            payload,
            artifact=artifact,
            data_version=data_version,
            sessions=sessions,
            minimum_price_tick=minimum_price_tick,
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
    """Generic idempotent dataset builder.

    Owns acquisition/storage/manifest/idempotency behavior only.  All
    source/provider-specific facts and decoding behavior come from the
    adapter's `SourceSpecification` and `decode`; the builder never assumes a
    provider.

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
        contracts: dict[str, ContractConfig],
        retrieved_at_provider: Callable[[], datetime] | None = None,
    ) -> None:
        self._adapter = adapter
        self._spec = adapter.source_specification
        self._raw_dir = Path(raw_dir)
        self._manifest_path = Path(manifest_path)
        self._schema_version = schema_version
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
        provider = self._spec.provider
        for request in sorted(request_list, key=lambda r: r.partition_key):
            key = (provider,) + request.partition_key
            raw_path = self._raw_dir / request.raw_file_name(provider)
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
        spec = self._spec
        retrieved_at = self._retrieved_at_provider()
        request_parameters = build_request_parameters(request, spec.request_parameter_names)
        source = SourceIdentity(
            provider=spec.provider,
            source_type=spec.source_type,
            endpoint_identity=spec.endpoint_identity,
            provider_dataset_version=spec.provider_dataset_version,
            retrieved_at=retrieved_at,
            request_parameters=request_parameters,
        )
        artifact = RawArtifact.from_bytes(
            payload=payload,
            exchange=request.exchange,
            concrete_instrument=request.concrete_instrument,
            coverage_start=result.returned_start,
            coverage_end=result.returned_end,
            granularity_seconds=request.granularity_seconds,
            timezone=request.timezone,
            raw_schema_identity=spec.raw_schema_identity,
            source_identity_id=source.identity_id,
        )
        data_version = DataVersionIdentity(
            source_identities=(source,),
            raw_artifacts=(artifact,),
            normalizer=spec.normalizer,
            session_metadata_version=config.sessions.version,
            historical_availability_rule=spec.availability_rule,
            contract_metadata_identity=config.contract_metadata_identity,
        )
        batch = self._adapter.decode(
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
            provider=spec.provider,
            api_version=result.provider_version,
            contract=request.concrete_instrument,
            exchange=request.exchange,
            granularity_seconds=request.granularity_seconds,
            timezone=request.timezone,
            trading_day=request.trading_day,
            requested_start=request.requested_start,
            requested_end=request.requested_end,
            returned_start=result.returned_start,
            returned_end=result.returned_end,
            retrieved_at=retrieved_at,
            raw_bytes=len(payload),
            raw_sha256=sha256(payload).hexdigest(),
            request_identity=source.request_identity,
            request_parameters=request_parameters,
            normalizer_identity=spec.normalizer.identity_id,
            session_metadata_version=config.sessions.version,
            contract_metadata_identity=config.contract_metadata_identity,
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

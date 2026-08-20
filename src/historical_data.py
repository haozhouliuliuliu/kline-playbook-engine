"""Vendor-neutral provenance identities for real historical market data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import re
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from src.data_substrate import BarQuality, CompletedBar, SessionMetadata


_CONCRETE_INSTRUMENT = re.compile(r"^[A-Z]+\.[A-Za-z]+[0-9]{3,4}$")
_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_SENSITIVE_PARAMETER = re.compile(r"password|username|secret|token|credential|auth", re.IGNORECASE)


def _canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _required_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


@dataclass(frozen=True)
class SourceIdentity:
    provider: str
    source_type: str
    endpoint_identity: str
    provider_dataset_version: str | None
    retrieved_at: datetime
    request_parameters: tuple[tuple[str, str], ...]

    def __post_init__(self) -> None:
        for value, name in (
            (self.provider, "source provider"),
            (self.source_type, "source type"),
            (self.endpoint_identity, "source endpoint identity"),
        ):
            _required_text(value, name)
        if self.provider_dataset_version is not None:
            _required_text(self.provider_dataset_version, "provider dataset version")
        if self.retrieved_at.tzinfo is None:
            raise ValueError("source retrieval timestamp must be timezone-aware")
        if not self.request_parameters:
            raise ValueError("source request parameters are required")
        names = tuple(name for name, _ in self.request_parameters)
        if names != tuple(sorted(names)) or len(names) != len(set(names)):
            raise ValueError("source request parameters must be sorted and unique")
        for name, value in self.request_parameters:
            _required_text(name, "request parameter name")
            if _SENSITIVE_PARAMETER.search(name):
                raise ValueError("credentials and authentication parameters must not enter provenance")
            if not isinstance(value, str):
                raise ValueError("request parameter values must be strings")

    @property
    def request_identity(self) -> str:
        return _canonical_hash(self.request_parameters)

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "provider": self.provider,
                "source_type": self.source_type,
                "endpoint_identity": self.endpoint_identity,
                "provider_dataset_version": self.provider_dataset_version,
                "retrieved_at": self.retrieved_at.isoformat(),
                "request_identity": self.request_identity,
            }
        )


@dataclass(frozen=True)
class RawArtifact:
    exchange: str
    concrete_instrument: str
    coverage_start: datetime
    coverage_end: datetime
    granularity_seconds: int
    timezone: str
    raw_schema_identity: str
    raw_sha256: str
    source_identity_id: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.exchange, "raw artifact exchange"),
            (self.timezone, "raw artifact timezone"),
            (self.raw_schema_identity, "raw schema identity"),
            (self.source_identity_id, "raw artifact source identity"),
        ):
            _required_text(value, name)
        if not _CONCRETE_INSTRUMENT.fullmatch(self.concrete_instrument):
            raise ValueError("raw artifact requires a concrete contract identifier")
        if not self.concrete_instrument.startswith(self.exchange + "."):
            raise ValueError("raw artifact exchange and contract identifier disagree")
        if self.coverage_start.tzinfo is None or self.coverage_end.tzinfo is None:
            raise ValueError("raw artifact coverage must be timezone-aware")
        if self.coverage_end <= self.coverage_start:
            raise ValueError("raw artifact coverage end must follow its start")
        if type(self.granularity_seconds) is not int or self.granularity_seconds <= 0:
            raise ValueError("raw artifact granularity must be positive whole seconds")
        if not _SHA256.fullmatch(self.raw_sha256):
            raise ValueError("raw artifact SHA256 must be 64 lowercase hexadecimal characters")

    @classmethod
    def from_bytes(
        cls,
        *,
        payload: bytes,
        exchange: str,
        concrete_instrument: str,
        coverage_start: datetime,
        coverage_end: datetime,
        granularity_seconds: int,
        timezone: str,
        raw_schema_identity: str,
        source_identity_id: str,
    ) -> "RawArtifact":
        if not isinstance(payload, bytes):
            raise ValueError("raw artifact payload must be bytes")
        return cls(
            exchange,
            concrete_instrument,
            coverage_start,
            coverage_end,
            granularity_seconds,
            timezone,
            raw_schema_identity,
            sha256(payload).hexdigest(),
            source_identity_id,
        )

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "exchange": self.exchange,
                "concrete_instrument": self.concrete_instrument,
                "coverage_start": self.coverage_start.isoformat(),
                "coverage_end": self.coverage_end.isoformat(),
                "granularity_seconds": self.granularity_seconds,
                "timezone": self.timezone,
                "raw_schema_identity": self.raw_schema_identity,
                "raw_sha256": self.raw_sha256,
                "source_identity_id": self.source_identity_id,
            }
        )


@dataclass(frozen=True)
class NormalizerIdentity:
    adapter_version: str
    normalized_schema_version: str
    availability_rule_version: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.adapter_version, "normalizer adapter version"),
            (self.normalized_schema_version, "normalized schema version"),
            (self.availability_rule_version, "availability rule version"),
        ):
            _required_text(value, name)

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "adapter_version": self.adapter_version,
                "normalized_schema_version": self.normalized_schema_version,
                "availability_rule_version": self.availability_rule_version,
            }
        )


@dataclass(frozen=True)
class DataVersionIdentity:
    source_identities: tuple[SourceIdentity, ...]
    raw_artifacts: tuple[RawArtifact, ...]
    normalizer: NormalizerIdentity
    session_metadata_version: str
    historical_availability_rule: str
    contract_metadata_identity: str | None = None

    def __post_init__(self) -> None:
        if any(not isinstance(item, SourceIdentity) for item in self.source_identities):
            raise ValueError("data-version sources must be SourceIdentity values")
        if any(not isinstance(item, RawArtifact) for item in self.raw_artifacts):
            raise ValueError("data-version artifacts must be RawArtifact values")
        if not isinstance(self.normalizer, NormalizerIdentity):
            raise ValueError("data version requires a NormalizerIdentity")
        if not self.source_identities or not self.raw_artifacts:
            raise ValueError("data version requires source identities and raw artifacts")
        _required_text(self.session_metadata_version, "session metadata version")
        _required_text(self.historical_availability_rule, "historical availability rule")
        if self.contract_metadata_identity is not None:
            _required_text(self.contract_metadata_identity, "contract metadata identity")
        if self.normalizer.availability_rule_version != self.historical_availability_rule:
            raise ValueError("normalizer and data-version availability rules must agree")
        source_ids = {item.identity_id for item in self.source_identities}
        if len(source_ids) != len(self.source_identities):
            raise ValueError("duplicate source identities are not allowed")
        if len({item.identity_id for item in self.raw_artifacts}) != len(self.raw_artifacts):
            raise ValueError("duplicate raw artifacts are not allowed")
        if any(item.source_identity_id not in source_ids for item in self.raw_artifacts):
            raise ValueError("every raw artifact must bind a declared source identity")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "source_identities": sorted(item.identity_id for item in self.source_identities),
                "raw_artifacts": sorted(item.identity_id for item in self.raw_artifacts),
                "concrete_instruments": sorted({item.concrete_instrument for item in self.raw_artifacts}),
                "coverage": sorted(
                    (item.coverage_start.isoformat(), item.coverage_end.isoformat())
                    for item in self.raw_artifacts
                ),
                "granularities": sorted({item.granularity_seconds for item in self.raw_artifacts}),
                "timezones": sorted({item.timezone for item in self.raw_artifacts}),
                "normalizer_identity": self.normalizer.identity_id,
                "session_metadata_version": self.session_metadata_version,
                "historical_availability_rule": self.historical_availability_rule,
                "contract_metadata_identity": self.contract_metadata_identity,
            }
        )


@dataclass(frozen=True)
class NormalizedHistoricalBar:
    exchange: str
    concrete_instrument: str
    source_event_at: datetime
    source_retrieved_at: datetime
    completed_bar: CompletedBar
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None
    open_interest_start: Decimal | None
    open_interest_end: Decimal | None
    raw_artifact_identity_id: str
    data_version_id: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.exchange, "normalized bar exchange"),
            (self.concrete_instrument, "normalized bar concrete instrument"),
            (self.raw_artifact_identity_id, "normalized bar raw artifact identity"),
            (self.data_version_id, "normalized bar data-version identity"),
        ):
            _required_text(value, name)
        if self.source_event_at.tzinfo is None or self.source_retrieved_at.tzinfo is None:
            raise ValueError("normalized bar source timestamps must be timezone-aware")
        if self.completed_bar.instrument != self.concrete_instrument:
            raise ValueError("normalized and completed bar contract identities must agree")
        prices = (self.open, self.high, self.low, self.close)
        if any(type(value) is not Decimal or not value.is_finite() or value <= 0 for value in prices):
            raise ValueError("normalized bar OHLC must be positive finite Decimals")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close) or self.low > self.high:
            raise ValueError("normalized bar OHLC values are inconsistent")
        optional_values = (self.volume, self.open_interest_start, self.open_interest_end)
        if any(
            value is not None and (type(value) is not Decimal or not value.is_finite() or value < 0)
            for value in optional_values
        ):
            raise ValueError("normalized bar volume and open interest must be non-negative finite Decimals")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "exchange": self.exchange,
                "concrete_instrument": self.concrete_instrument,
                "source_event_at": self.source_event_at.isoformat(),
                "source_retrieved_at": self.source_retrieved_at.isoformat(),
                "bar_start": self.completed_bar.start.isoformat(),
                "bar_end": self.completed_bar.end.isoformat(),
                "historical_pit_available_at": self.completed_bar.available_at.isoformat(),
                "trading_day": self.completed_bar.trading_day.isoformat(),
                "open": str(self.open),
                "high": str(self.high),
                "low": str(self.low),
                "close": str(self.close),
                "volume": None if self.volume is None else str(self.volume),
                "open_interest_start": None if self.open_interest_start is None else str(self.open_interest_start),
                "open_interest_end": None if self.open_interest_end is None else str(self.open_interest_end),
                "raw_artifact_identity_id": self.raw_artifact_identity_id,
                "data_version_id": self.data_version_id,
            }
        )


@dataclass(frozen=True)
class NormalizedHistoricalBatch:
    bars: tuple[NormalizedHistoricalBar, ...]
    missing_expected_starts: tuple[datetime, ...]
    raw_artifact_identity_id: str
    data_version_id: str

    def __post_init__(self) -> None:
        if not self.bars:
            raise ValueError("normalized historical batch requires at least one bar")
        if any(not isinstance(item, NormalizedHistoricalBar) for item in self.bars):
            raise ValueError("normalized historical batch contains an invalid bar")
        _required_text(self.raw_artifact_identity_id, "batch raw artifact identity")
        _required_text(self.data_version_id, "batch data-version identity")
        starts = tuple(item.completed_bar.start for item in self.bars)
        if any(left >= right for left, right in zip(starts, starts[1:])):
            raise ValueError("normalized historical bars must be strictly ordered")
        if len(set(starts)) != len(starts):
            raise ValueError("normalized historical bars must not contain duplicates")
        if any(
            item.raw_artifact_identity_id != self.raw_artifact_identity_id
            or item.data_version_id != self.data_version_id
            for item in self.bars
        ):
            raise ValueError("normalized historical batch identities are inconsistent")
        if any(item.tzinfo is None for item in self.missing_expected_starts):
            raise ValueError("missing expected starts must be timezone-aware, sorted, and unique")
        if tuple(sorted(set(self.missing_expected_starts))) != self.missing_expected_starts:
            raise ValueError("missing expected starts must be timezone-aware, sorted, and unique")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "bars": [item.identity_id for item in self.bars],
                "missing_expected_starts": [item.isoformat() for item in self.missing_expected_starts],
                "raw_artifact_identity_id": self.raw_artifact_identity_id,
                "data_version_id": self.data_version_id,
            }
        )


def _decimal(value: Any, name: str, *, optional: bool = False) -> Decimal | None:
    if value is None and optional:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not result.is_finite():
        raise ValueError(f"{name} must be a finite number")
    return result


def _tqsdk_timestamp(value: Any, timezone: ZoneInfo) -> datetime:
    if isinstance(value, bool):
        raise ValueError("TqSdk bar datetime must be integer nanoseconds")
    try:
        nanoseconds = int(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("TqSdk bar datetime must be integer nanoseconds") from error
    if str(nanoseconds) != str(value):
        raise ValueError("TqSdk bar datetime must be integer nanoseconds")
    seconds, remainder = divmod(nanoseconds, 1_000_000_000)
    try:
        return datetime.fromtimestamp(seconds, tz=timezone) + timedelta(microseconds=remainder // 1_000)
    except (OSError, OverflowError, ValueError) as error:
        raise ValueError("TqSdk bar datetime is outside the supported range") from error


def normalize_tqsdk_historical_bars(
    raw_payload: bytes,
    *,
    artifact: RawArtifact,
    data_version: DataVersionIdentity,
    sessions: SessionMetadata,
    minimum_price_tick: Decimal | None = None,
) -> NormalizedHistoricalBatch:
    """Normalize one concrete-contract TqSdk fixed-duration raw response."""
    if not isinstance(raw_payload, bytes):
        raise ValueError("raw TqSdk payload must be bytes")
    if sha256(raw_payload).hexdigest() != artifact.raw_sha256:
        raise ValueError("raw TqSdk payload does not match its artifact hash")
    if artifact.identity_id not in {item.identity_id for item in data_version.raw_artifacts}:
        raise ValueError("raw artifact is not bound to the supplied data version")
    if sessions.version != data_version.session_metadata_version:
        raise ValueError("session metadata version does not match the data version")
    if data_version.historical_availability_rule != "bar-start-plus-duration-v1":
        raise ValueError("unsupported historical availability rule")
    if minimum_price_tick is not None:
        if type(minimum_price_tick) is not Decimal or minimum_price_tick <= 0:
            raise ValueError("minimum price tick must be a positive Decimal")
        if data_version.contract_metadata_identity is None:
            raise ValueError("price-tick checks require a contract metadata identity")
    try:
        timezone = ZoneInfo(artifact.timezone)
    except ZoneInfoNotFoundError as error:
        raise ValueError("raw artifact timezone is unavailable") from error
    try:
        records = json.loads(raw_payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("raw TqSdk payload must be valid UTF-8 JSON") from error
    if not isinstance(records, list) or not records:
        raise ValueError("raw TqSdk payload must contain a non-empty record list")

    source = next(
        (item for item in data_version.source_identities if item.identity_id == artifact.source_identity_id),
        None,
    )
    if source is None:
        raise ValueError("raw artifact source identity is missing")
    interval = timedelta(seconds=artifact.granularity_seconds)
    bars: list[NormalizedHistoricalBar] = []
    prior_start: datetime | None = None
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("each raw TqSdk bar must be an object")
        start = _tqsdk_timestamp(record.get("datetime"), timezone)
        if prior_start is not None and start <= prior_start:
            message = "duplicate" if start == prior_start else "out-of-order"
            raise ValueError(f"raw TqSdk bar timestamps contain {message} data")
        prior_start = start
        end = start + interval
        if start < artifact.coverage_start or end > artifact.coverage_end:
            raise ValueError("raw TqSdk bar falls outside claimed coverage")
        trading_day = sessions.trading_day_at(artifact.exchange, artifact.concrete_instrument, start)
        if trading_day is None:
            raise ValueError("raw TqSdk bar falls outside published sessions")
        row_symbol = record.get("symbol")
        if row_symbol is not None and row_symbol != artifact.concrete_instrument:
            raise ValueError("raw TqSdk bar contract identity disagrees with its artifact")
        open_price = _decimal(record.get("open"), "open")
        high_price = _decimal(record.get("high"), "high")
        low_price = _decimal(record.get("low"), "low")
        close_price = _decimal(record.get("close"), "close")
        assert open_price is not None and high_price is not None and low_price is not None and close_price is not None
        if min(open_price, high_price, low_price, close_price) <= 0:
            raise ValueError("OHLC prices must be positive")
        if low_price > min(open_price, close_price) or high_price < max(open_price, close_price) or low_price > high_price:
            raise ValueError("OHLC values are inconsistent")
        if minimum_price_tick is not None and any(
            price % minimum_price_tick != 0 for price in (open_price, high_price, low_price, close_price)
        ):
            raise ValueError("OHLC price is incompatible with the contract minimum tick")
        volume = _decimal(record.get("volume"), "volume", optional=True)
        open_oi = _decimal(record.get("open_oi"), "open_oi", optional=True)
        close_oi = _decimal(record.get("close_oi"), "close_oi", optional=True)
        if any(value is not None and value < 0 for value in (volume, open_oi, close_oi)):
            raise ValueError("volume and open interest must be non-negative")
        completed = CompletedBar(
            artifact.concrete_instrument,
            trading_day,
            start,
            end,
            end,
            BarQuality(),
        )
        bars.append(
            NormalizedHistoricalBar(
                artifact.exchange,
                artifact.concrete_instrument,
                start,
                source.retrieved_at,
                completed,
                open_price,
                high_price,
                low_price,
                close_price,
                volume,
                open_oi,
                close_oi,
                artifact.identity_id,
                data_version.identity_id,
            )
        )
    # Completeness is derived from the authoritative session windows over the
    # whole declared artifact coverage, NOT from the set of days that happen to
    # have observed bars.  An entirely absent session window inside the claimed
    # coverage therefore still contributes missing expected starts.
    expected = sessions.expected_bar_starts_between(
        artifact.exchange,
        artifact.concrete_instrument,
        artifact.coverage_start,
        artifact.coverage_end,
        interval,
    )
    observed = {bar.completed_bar.start for bar in bars}
    missing = sorted(set(expected) - observed)
    return NormalizedHistoricalBatch(
        tuple(bars),
        tuple(sorted(missing)),
        artifact.identity_id,
        data_version.identity_id,
    )

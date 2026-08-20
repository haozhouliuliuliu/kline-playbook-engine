"""Deterministic point-in-time aggregation and generic EMA/ADX features.

The module consumes the existing SessionMetadata and NormalizedHistoricalBar
authorities.  It does not choose any Holy Grail semantic, period, price basis,
or numeric policy.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable

from src.data_substrate import SessionMetadata
from src.historical_data import NormalizedHistoricalBar
from src.strategy_evidence import ArtifactBinding


AGGREGATION_SCHEMA_VERSION = "session-authority-aggregation-v0.2"
FEATURE_SCHEMA_VERSION = "pit-technical-feature-v0.2"
EMA_ALGORITHM_VERSION = "generic-ema-v0.2"
ADX_ALGORITHM_VERSION = "generic-wilder-adx-v0.2"

STATUS_READY = "READY"
STATUS_INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
STATUS_UNDEFINED = "UNDEFINED"

VOLUME_STATUS_COMPLETE = "COMPLETE"
VOLUME_STATUS_UNKNOWN = "UNKNOWN"
PRICE_FIELDS = ("open", "high", "low", "close")


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _require_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


FEATURE_IMPLEMENTATION_BINDING = ArtifactBinding.from_file(
    artifact_kind="feature",
    artifact_reference="src/technical_features.py",
    path=str(Path(__file__).resolve()),
    declared_version=FEATURE_SCHEMA_VERSION,
)


@dataclass(frozen=True)
class FeatureNumericPolicy:
    """Explicit generic arithmetic choices; no default policy exists."""

    ema_seed_method: str
    adx_initialization_method: str
    internal_precision_policy: str
    output_quantum: Decimal
    rounding_mode: str

    def __post_init__(self) -> None:
        if self.ema_seed_method != "SMA":
            raise ValueError("unsupported EMA seed method")
        if self.adx_initialization_method != "WILDER_SMA_DX":
            raise ValueError("unsupported ADX initialization method")
        if self.internal_precision_policy not in ("FULL_DECIMAL", "QUANTIZE_EACH_STEP"):
            raise ValueError("unsupported internal precision policy")
        if self.rounding_mode not in ("ROUND_HALF_UP", "ROUND_HALF_EVEN"):
            raise ValueError("unsupported feature rounding mode")
        if (
            type(self.output_quantum) is not Decimal
            or not self.output_quantum.is_finite()
            or self.output_quantum <= 0
        ):
            raise ValueError("feature output quantum must be a positive finite Decimal")

    @property
    def identity_id(self) -> str:
        return canonical_hash(
            {
                "ema_seed_method": self.ema_seed_method,
                "adx_initialization_method": self.adx_initialization_method,
                "internal_precision_policy": self.internal_precision_policy,
                "output_quantum": str(self.output_quantum),
                "rounding_mode": self.rounding_mode,
            }
        )

    def quantize(self, value: Decimal) -> Decimal:
        rounding = {
            "ROUND_HALF_UP": ROUND_HALF_UP,
            "ROUND_HALF_EVEN": ROUND_HALF_EVEN,
        }[self.rounding_mode]
        return value.quantize(self.output_quantum, rounding=rounding)

    def internal(self, value: Decimal) -> Decimal:
        if self.internal_precision_policy == "QUANTIZE_EACH_STEP":
            return self.quantize(value)
        return value


@dataclass(frozen=True)
class TimeframeSpec:
    name: str
    kind: str
    interval_seconds: int | None
    aggregation_version: str

    def __post_init__(self) -> None:
        _require_text(self.name, "timeframe name")
        _require_text(self.aggregation_version, "aggregation version")
        if self.kind not in ("INTRADAY", "DAILY"):
            raise ValueError("timeframe kind must be INTRADAY or DAILY")
        if self.kind == "INTRADAY":
            if type(self.interval_seconds) is not int or self.interval_seconds <= 0:
                raise ValueError("intraday timeframe requires positive whole seconds")
        elif self.interval_seconds is not None:
            raise ValueError("daily timeframe must not declare an interval")

    @property
    def identity_id(self) -> str:
        return canonical_hash(
            {
                "name": self.name,
                "kind": self.kind,
                "interval_seconds": self.interval_seconds,
                "aggregation_version": self.aggregation_version,
                "schema_version": AGGREGATION_SCHEMA_VERSION,
            }
        )


def _bucket_identity(
    *,
    exchange: str,
    concrete_instrument: str,
    trading_day: date,
    timeframe_spec: TimeframeSpec,
    session_metadata_version: str,
    session_window_identity: str,
    start: datetime,
    end: datetime,
    timeframe_duration_seconds: int,
    expected_constituent_starts: tuple[datetime, ...],
) -> str:
    return canonical_hash(
        {
            "exchange": exchange,
            "concrete_instrument": concrete_instrument,
            "trading_day": trading_day.isoformat(),
            "timeframe_spec_identity": timeframe_spec.identity_id,
            "session_metadata_version": session_metadata_version,
            "session_window_identity": session_window_identity,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "timeframe_duration_seconds": timeframe_duration_seconds,
            "expected_constituent_starts": [item.isoformat() for item in expected_constituent_starts],
        }
    )


@dataclass(frozen=True)
class AggregatedBar:
    exchange: str
    concrete_instrument: str
    trading_day: date
    timeframe_spec: TimeframeSpec
    session_metadata_version: str
    session_window_identity: str
    start: datetime
    end: datetime
    timeframe_duration_seconds: int
    expected_constituent_starts: tuple[datetime, ...]
    actual_constituent_starts: tuple[datetime, ...]
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None
    volume_status: str
    available_at: datetime
    source_bar_identities: tuple[str, ...]

    def __post_init__(self) -> None:
        for value, name in (
            (self.exchange, "aggregate exchange"),
            (self.concrete_instrument, "aggregate concrete instrument"),
            (self.session_metadata_version, "session metadata version"),
            (self.session_window_identity, "session window identity"),
        ):
            _require_text(value, name)
        if any(item.tzinfo is None for item in (self.start, self.end, self.available_at)):
            raise ValueError("aggregate timestamps must be timezone-aware")
        if self.end <= self.start or self.available_at < self.end:
            raise ValueError("aggregate chronology is invalid")
        if type(self.timeframe_duration_seconds) is not int or self.timeframe_duration_seconds <= 0:
            raise ValueError("aggregate timeframe duration must be positive whole seconds")
        if not self.expected_constituent_starts:
            raise ValueError("aggregate requires expected constituent starts")
        if self.actual_constituent_starts != self.expected_constituent_starts:
            raise ValueError("complete aggregate actual starts must exactly equal expected starts")
        if len(self.source_bar_identities) != len(self.expected_constituent_starts):
            raise ValueError("aggregate source identities must cover every constituent")
        if len(set(self.source_bar_identities)) != len(self.source_bar_identities):
            raise ValueError("aggregate source identities must be unique")
        prices = (self.open, self.high, self.low, self.close)
        if any(type(value) is not Decimal or not value.is_finite() or value <= 0 for value in prices):
            raise ValueError("aggregate OHLC must be positive finite Decimals")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close):
            raise ValueError("aggregate OHLC values are inconsistent")
        if self.volume_status not in (VOLUME_STATUS_COMPLETE, VOLUME_STATUS_UNKNOWN):
            raise ValueError("aggregate volume status is invalid")
        if self.volume is None and self.volume_status != VOLUME_STATUS_UNKNOWN:
            raise ValueError("missing aggregate volume must be UNKNOWN")
        if self.volume is not None and (
            type(self.volume) is not Decimal
            or not self.volume.is_finite()
            or self.volume < 0
            or self.volume_status != VOLUME_STATUS_COMPLETE
        ):
            raise ValueError("aggregate volume is invalid")

    @property
    def bucket_identity(self) -> str:
        return _bucket_identity(
            exchange=self.exchange,
            concrete_instrument=self.concrete_instrument,
            trading_day=self.trading_day,
            timeframe_spec=self.timeframe_spec,
            session_metadata_version=self.session_metadata_version,
            session_window_identity=self.session_window_identity,
            start=self.start,
            end=self.end,
            timeframe_duration_seconds=self.timeframe_duration_seconds,
            expected_constituent_starts=self.expected_constituent_starts,
        )

    @property
    def identity_id(self) -> str:
        return canonical_hash(
            {
                "bucket_identity": self.bucket_identity,
                "actual_constituent_starts": [item.isoformat() for item in self.actual_constituent_starts],
                "open": str(self.open),
                "high": str(self.high),
                "low": str(self.low),
                "close": str(self.close),
                "volume": None if self.volume is None else str(self.volume),
                "volume_status": self.volume_status,
                "available_at": self.available_at.isoformat(),
                "source_bar_identities": self.source_bar_identities,
            }
        )

    def is_visible_at(self, timestamp: datetime) -> bool:
        if timestamp.tzinfo is None:
            raise ValueError("visibility timestamp must be timezone-aware")
        return timestamp >= self.available_at


@dataclass(frozen=True)
class IncompleteBucket:
    exchange: str
    concrete_instrument: str
    trading_day: date
    timeframe_spec: TimeframeSpec
    session_metadata_version: str
    session_window_identity: str
    start: datetime
    end: datetime
    timeframe_duration_seconds: int
    expected_constituent_starts: tuple[datetime, ...]
    actual_constituent_starts: tuple[datetime, ...]
    missing_constituent_starts: tuple[datetime, ...]
    boundary_shortened: bool

    def __post_init__(self) -> None:
        if not self.expected_constituent_starts:
            raise ValueError("incomplete bucket requires expected starts")
        if tuple(sorted(set(self.expected_constituent_starts))) != self.expected_constituent_starts:
            raise ValueError("expected starts must be sorted and unique")
        if tuple(sorted(set(self.actual_constituent_starts))) != self.actual_constituent_starts:
            raise ValueError("actual starts must be sorted and unique")
        expected = set(self.expected_constituent_starts)
        actual = set(self.actual_constituent_starts)
        if not actual <= expected:
            raise ValueError("incomplete bucket contains an unexpected constituent")
        if self.missing_constituent_starts != tuple(sorted(expected - actual)):
            raise ValueError("incomplete bucket missing evidence is inconsistent")
        if not self.missing_constituent_starts and not self.boundary_shortened:
            raise ValueError("incomplete bucket requires a gap or shortened boundary")
        if type(self.boundary_shortened) is not bool:
            raise ValueError("boundary-shortened state must be explicit")

    @property
    def present_constituent_count(self) -> int:
        return len(self.actual_constituent_starts)

    @property
    def bucket_identity(self) -> str:
        return _bucket_identity(
            exchange=self.exchange,
            concrete_instrument=self.concrete_instrument,
            trading_day=self.trading_day,
            timeframe_spec=self.timeframe_spec,
            session_metadata_version=self.session_metadata_version,
            session_window_identity=self.session_window_identity,
            start=self.start,
            end=self.end,
            timeframe_duration_seconds=self.timeframe_duration_seconds,
            expected_constituent_starts=self.expected_constituent_starts,
        )

    @property
    def evidence_identity(self) -> str:
        return canonical_hash(
            {
                "bucket_identity": self.bucket_identity,
                "actual_constituent_starts": [item.isoformat() for item in self.actual_constituent_starts],
                "missing_constituent_starts": [item.isoformat() for item in self.missing_constituent_starts],
                "boundary_shortened": self.boundary_shortened,
            }
        )


@dataclass(frozen=True, init=False)
class AggregationResult:
    """Unforgeable-by-normal-construction completeness envelope for features."""

    aggregates: tuple[AggregatedBar, ...]
    incomplete_buckets: tuple[IncompleteBucket, ...]
    expected_bucket_identities: tuple[str, ...]
    exchange: str
    concrete_instrument: str
    timeframe_spec: TimeframeSpec
    session_metadata_version: str
    coverage_start: datetime
    coverage_end: datetime

    @classmethod
    def _from_aggregation(
        cls,
        *,
        aggregates: tuple[AggregatedBar, ...],
        incomplete_buckets: tuple[IncompleteBucket, ...],
        expected_bucket_identities: tuple[str, ...],
        exchange: str,
        concrete_instrument: str,
        timeframe_spec: TimeframeSpec,
        session_metadata_version: str,
        coverage_start: datetime,
        coverage_end: datetime,
    ) -> "AggregationResult":
        result = object.__new__(cls)
        for name, value in (
            ("aggregates", aggregates),
            ("incomplete_buckets", incomplete_buckets),
            ("expected_bucket_identities", expected_bucket_identities),
            ("exchange", exchange),
            ("concrete_instrument", concrete_instrument),
            ("timeframe_spec", timeframe_spec),
            ("session_metadata_version", session_metadata_version),
            ("coverage_start", coverage_start),
            ("coverage_end", coverage_end),
        ):
            object.__setattr__(result, name, value)
        result.__post_init__()
        return result

    def __post_init__(self) -> None:
        evidence_ids = tuple(
            item.bucket_identity for item in (*self.aggregates, *self.incomplete_buckets)
        )
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("aggregation result contains duplicate bucket evidence")
        if set(evidence_ids) != set(self.expected_bucket_identities):
            raise ValueError("aggregation result does not cover every expected bucket")
        if len(self.expected_bucket_identities) != len(set(self.expected_bucket_identities)):
            raise ValueError("expected aggregation bucket identities must be unique")
        if self.coverage_start.tzinfo is None or self.coverage_end.tzinfo is None:
            raise ValueError("aggregation coverage must be timezone-aware")
        if self.coverage_end <= self.coverage_start:
            raise ValueError("aggregation coverage end must follow start")

    @property
    def complete(self) -> bool:
        return not self.incomplete_buckets

    @property
    def feature_stream_identity(self) -> str:
        """Static stream authority only; never binds future aggregate contents."""
        return canonical_hash(
            {
                "exchange": self.exchange,
                "concrete_instrument": self.concrete_instrument,
                "timeframe_spec_identity": self.timeframe_spec.identity_id,
                "session_metadata_version": self.session_metadata_version,
            }
        )

    @property
    def identity_id(self) -> str:
        return canonical_hash(
            {
                "aggregates": [item.identity_id for item in self.aggregates],
                "incomplete": [item.evidence_identity for item in self.incomplete_buckets],
                "expected_bucket_identities": self.expected_bucket_identities,
                "exchange": self.exchange,
                "concrete_instrument": self.concrete_instrument,
                "timeframe_spec_identity": self.timeframe_spec.identity_id,
                "session_metadata_version": self.session_metadata_version,
                "coverage_start": self.coverage_start.isoformat(),
                "coverage_end": self.coverage_end.isoformat(),
            }
        )


class TimeframeAggregator:
    def __init__(self, sessions: SessionMetadata, base_interval_seconds: int = 60) -> None:
        if not isinstance(sessions, SessionMetadata):
            raise ValueError("timeframe aggregation requires SessionMetadata")
        if type(base_interval_seconds) is not int or base_interval_seconds <= 0:
            raise ValueError("base interval must be positive whole seconds")
        self._sessions = sessions
        self._base_seconds = base_interval_seconds
        self._base_interval = timedelta(seconds=base_interval_seconds)

    @property
    def session_metadata_version(self) -> str:
        return self._sessions.version

    def aggregate(
        self,
        bars: Iterable[NormalizedHistoricalBar],
        *,
        spec: TimeframeSpec,
        exchange: str,
        concrete_instrument: str,
        coverage_start: datetime,
        coverage_end: datetime,
    ) -> AggregationResult:
        if not isinstance(spec, TimeframeSpec):
            raise ValueError("aggregation requires a TimeframeSpec")
        _require_text(exchange, "aggregation exchange")
        _require_text(concrete_instrument, "aggregation concrete instrument")
        if coverage_start.tzinfo is None or coverage_end.tzinfo is None:
            raise ValueError("aggregation coverage must be timezone-aware")
        if coverage_end <= coverage_start:
            raise ValueError("aggregation coverage end must follow start")
        if spec.kind == "INTRADAY" and spec.interval_seconds % self._base_seconds != 0:
            raise ValueError("intraday duration must be an exact multiple of the base interval")

        normalized = tuple(bars)
        if any(not isinstance(item, NormalizedHistoricalBar) for item in normalized):
            raise ValueError("aggregation requires NormalizedHistoricalBar values")
        starts = tuple(item.completed_bar.start for item in normalized)
        if any(left >= right for left, right in zip(starts, starts[1:])):
            raise ValueError("aggregation bars must be strictly ordered")
        if len(starts) != len(set(starts)):
            raise ValueError("aggregation bars must not contain duplicate starts")

        coverage_expected = self._sessions.expected_bar_starts_between(
            exchange,
            concrete_instrument,
            coverage_start,
            coverage_end,
            self._base_interval,
        )
        if not coverage_expected:
            raise ValueError("aggregation coverage contains no published expected bars")
        trading_days = tuple(
            sorted(
                {
                    trading_day
                    for start in coverage_expected
                    if (trading_day := self._sessions.trading_day_at(exchange, concrete_instrument, start))
                    is not None
                }
            )
        )
        expected_by_day = {
            trading_day: self._sessions.expected_bar_starts(
                exchange, concrete_instrument, trading_day, self._base_interval
            )
            for trading_day in trading_days
        }
        expected_all = {start for expected in expected_by_day.values() for start in expected}

        by_start: dict[datetime, NormalizedHistoricalBar] = {}
        for item in normalized:
            completed = item.completed_bar
            if item.exchange != exchange or item.concrete_instrument != concrete_instrument:
                raise ValueError("aggregation stream must match one exchange and concrete instrument")
            if completed.start < coverage_start or completed.end > coverage_end:
                raise ValueError("source bar falls outside the declared aggregation coverage")
            if completed.end - completed.start != self._base_interval:
                raise ValueError("every source bar duration must equal the declared base interval")
            authority_day = self._sessions.trading_day_at(exchange, concrete_instrument, completed.start)
            if authority_day is None or authority_day != completed.trading_day:
                raise ValueError("source bar trading day disagrees with SessionMetadata")
            if completed.start not in expected_all:
                raise ValueError("source bar start is outside the authoritative aggregation coverage")
            by_start[completed.start] = item

        # For every fully covered official trading day, delegate the missing-set
        # decision to the existing SessionMetadata authority. Partial point-in-
        # time coverage deliberately excludes future starts rather than calling
        # them gaps.
        for trading_day, expected in expected_by_day.items():
            full_day_covered = (
                expected[0] >= coverage_start
                and expected[-1] + self._base_interval <= coverage_end
            )
            if not full_day_covered:
                continue
            observed_starts = tuple(start for start in expected if start in by_start)
            authority_missing = self._sessions.missing_bar_starts(
                exchange,
                concrete_instrument,
                trading_day,
                self._base_interval,
                observed_starts,
            )
            calculated_missing = tuple(sorted(set(expected) - set(observed_starts)))
            if authority_missing != calculated_missing:
                raise ValueError("aggregation missing-bar evidence disagrees with SessionMetadata")

        if spec.kind == "DAILY":
            buckets = self._daily_buckets(
                expected_by_day,
                by_start,
                spec,
                exchange,
                concrete_instrument,
                coverage_start,
                coverage_end,
            )
        else:
            buckets = self._intraday_buckets(
                expected_by_day,
                by_start,
                spec,
                exchange,
                concrete_instrument,
                coverage_start,
                coverage_end,
            )
        aggregates, incomplete, expected_ids = buckets
        return AggregationResult._from_aggregation(
            aggregates=tuple(aggregates),
            incomplete_buckets=tuple(incomplete),
            expected_bucket_identities=tuple(expected_ids),
            exchange=exchange,
            concrete_instrument=concrete_instrument,
            timeframe_spec=spec,
            session_metadata_version=self._sessions.version,
            coverage_start=coverage_start,
            coverage_end=coverage_end,
        )

    def _window_runs(self, starts: tuple[datetime, ...]) -> tuple[tuple[datetime, ...], ...]:
        runs: list[list[datetime]] = []
        for start in starts:
            if not runs or start != runs[-1][-1] + self._base_interval:
                runs.append([start])
            else:
                runs[-1].append(start)
        return tuple(tuple(run) for run in runs)

    def _intraday_buckets(
        self,
        expected_by_day: dict[date, tuple[datetime, ...]],
        by_start: dict[datetime, NormalizedHistoricalBar],
        spec: TimeframeSpec,
        exchange: str,
        concrete_instrument: str,
        coverage_start: datetime,
        coverage_end: datetime,
    ) -> tuple[list[AggregatedBar], list[IncompleteBucket], list[str]]:
        constituents_per_bucket = spec.interval_seconds // self._base_seconds
        aggregates: list[AggregatedBar] = []
        incomplete: list[IncompleteBucket] = []
        expected_ids: list[str] = []
        for trading_day in sorted(expected_by_day):
            for run in self._window_runs(expected_by_day[trading_day]):
                window_identity = canonical_hash(
                    {
                        "session_metadata_version": self._sessions.version,
                        "trading_day": trading_day.isoformat(),
                        "expected_window_starts": [item.isoformat() for item in run],
                    }
                )
                for index in range(0, len(run), constituents_per_bucket):
                    expected = run[index : index + constituents_per_bucket]
                    start = expected[0]
                    end = start + timedelta(seconds=spec.interval_seconds)
                    # The official window defines bucket alignment, while the
                    # declared coverage defines which already-observable buckets
                    # are audited. Future buckets are not gaps.
                    if start < coverage_start or expected[-1] + self._base_interval > coverage_end:
                        continue
                    actual_bars = tuple(by_start[item] for item in expected if item in by_start)
                    actual_starts = tuple(item.completed_bar.start for item in actual_bars)
                    shortened = len(expected) != constituents_per_bucket
                    bucket = self._bucket_evidence(
                        trading_day=trading_day,
                        spec=spec,
                        exchange=exchange,
                        concrete_instrument=concrete_instrument,
                        session_window_identity=window_identity,
                        start=start,
                        end=end,
                        timeframe_duration_seconds=spec.interval_seconds,
                        expected=expected,
                        actual_bars=actual_bars,
                        actual_starts=actual_starts,
                        boundary_shortened=shortened,
                    )
                    if isinstance(bucket, AggregatedBar):
                        aggregates.append(bucket)
                    else:
                        incomplete.append(bucket)
                    expected_ids.append(bucket.bucket_identity)
        return aggregates, incomplete, expected_ids

    def _daily_buckets(
        self,
        expected_by_day: dict[date, tuple[datetime, ...]],
        by_start: dict[datetime, NormalizedHistoricalBar],
        spec: TimeframeSpec,
        exchange: str,
        concrete_instrument: str,
        coverage_start: datetime,
        coverage_end: datetime,
    ) -> tuple[list[AggregatedBar], list[IncompleteBucket], list[str]]:
        aggregates: list[AggregatedBar] = []
        incomplete: list[IncompleteBucket] = []
        expected_ids: list[str] = []
        for trading_day in sorted(expected_by_day):
            expected = expected_by_day[trading_day]
            if expected[0] < coverage_start or expected[-1] + self._base_interval > coverage_end:
                continue
            actual_bars = tuple(by_start[item] for item in expected if item in by_start)
            actual_starts = tuple(item.completed_bar.start for item in actual_bars)
            window_identity = canonical_hash(
                {
                    "session_metadata_version": self._sessions.version,
                    "trading_day": trading_day.isoformat(),
                    "daily_expected_starts": [item.isoformat() for item in expected],
                }
            )
            bucket = self._bucket_evidence(
                trading_day=trading_day,
                spec=spec,
                exchange=exchange,
                concrete_instrument=concrete_instrument,
                session_window_identity=window_identity,
                start=expected[0],
                end=expected[-1] + self._base_interval,
                timeframe_duration_seconds=len(expected) * self._base_seconds,
                expected=expected,
                actual_bars=actual_bars,
                actual_starts=actual_starts,
                boundary_shortened=False,
            )
            if isinstance(bucket, AggregatedBar):
                aggregates.append(bucket)
            else:
                incomplete.append(bucket)
            expected_ids.append(bucket.bucket_identity)
        return aggregates, incomplete, expected_ids

    def _bucket_evidence(
        self,
        *,
        trading_day: date,
        spec: TimeframeSpec,
        exchange: str,
        concrete_instrument: str,
        session_window_identity: str,
        start: datetime,
        end: datetime,
        timeframe_duration_seconds: int,
        expected: tuple[datetime, ...],
        actual_bars: tuple[NormalizedHistoricalBar, ...],
        actual_starts: tuple[datetime, ...],
        boundary_shortened: bool,
    ) -> AggregatedBar | IncompleteBucket:
        missing = tuple(sorted(set(expected) - set(actual_starts)))
        common = {
            "exchange": exchange,
            "concrete_instrument": concrete_instrument,
            "trading_day": trading_day,
            "timeframe_spec": spec,
            "session_metadata_version": self._sessions.version,
            "session_window_identity": session_window_identity,
            "start": start,
            "end": end,
            "timeframe_duration_seconds": timeframe_duration_seconds,
            "expected_constituent_starts": expected,
            "actual_constituent_starts": actual_starts,
        }
        if missing or boundary_shortened:
            return IncompleteBucket(
                **common,
                missing_constituent_starts=missing,
                boundary_shortened=boundary_shortened,
            )
        volumes = tuple(item.volume for item in actual_bars)
        volume = None
        volume_status = VOLUME_STATUS_UNKNOWN
        if all(item is not None for item in volumes):
            volume = sum((item for item in volumes if item is not None), Decimal(0))
            volume_status = VOLUME_STATUS_COMPLETE
        return AggregatedBar(
            **common,
            open=actual_bars[0].open,
            high=max(item.high for item in actual_bars),
            low=min(item.low for item in actual_bars),
            close=actual_bars[-1].close,
            volume=volume,
            volume_status=volume_status,
            available_at=max(item.completed_bar.available_at for item in actual_bars),
            source_bar_identities=tuple(item.identity_id for item in actual_bars),
        )


def visible_aggregates(
    aggregates: Iterable[AggregatedBar], timestamp: datetime
) -> tuple[AggregatedBar, ...]:
    if timestamp.tzinfo is None:
        raise ValueError("visibility timestamp must be timezone-aware")
    return tuple(item for item in aggregates if item.available_at <= timestamp)


def _validated_feature_input(result: AggregationResult) -> tuple[AggregatedBar, ...]:
    if not isinstance(result, AggregationResult):
        raise ValueError("feature computation requires an AggregationResult completeness envelope")
    if result.incomplete_buckets:
        raise ValueError("feature continuity is blocked by incomplete aggregation buckets")
    bars = result.aggregates
    if not bars:
        raise ValueError("feature computation requires at least one complete aggregate")
    starts = tuple(item.start for item in bars)
    if any(left >= right for left, right in zip(starts, starts[1:])):
        raise ValueError("feature aggregates must be strictly ordered")
    if any(left.end > right.start for left, right in zip(bars, bars[1:])):
        raise ValueError("feature aggregates must not overlap")
    if tuple(item.bucket_identity for item in bars) != result.expected_bucket_identities:
        raise ValueError("feature input discarded or reordered completeness evidence")
    if any(
        item.exchange != result.exchange
        or item.concrete_instrument != result.concrete_instrument
        or item.timeframe_spec.identity_id != result.timeframe_spec.identity_id
        or item.session_metadata_version != result.session_metadata_version
        for item in bars
    ):
        raise ValueError(
            "one feature series must be homogeneous in exchange, concrete instrument, timeframe, and session authority"
        )
    return bars


def _dependency_prefixes(bars: tuple[AggregatedBar, ...]) -> tuple[str, ...]:
    prefixes: list[str] = []
    previous = canonical_hash({"dependency_prefix": "ROOT"})
    for item in bars:
        previous = canonical_hash(
            {
                "previous_dependency_prefix": previous,
                "source_aggregate_identity": item.identity_id,
            }
        )
        prefixes.append(previous)
    return tuple(prefixes)


def _prefix_availability(bars: tuple[AggregatedBar, ...]) -> tuple[datetime, ...]:
    values: list[datetime] = []
    latest = bars[0].available_at
    for item in bars:
        latest = max(latest, item.available_at)
        values.append(latest)
    return tuple(values)


@dataclass(frozen=True)
class FeatureValue:
    feature_type: str
    algorithm_version: str
    parameters: tuple[tuple[str, object], ...]
    feature_version: str
    numeric_policy_identity: str
    implementation_artifact_identity: str
    timeframe_aggregation_identity: str
    source_aggregate_identity: str
    dependency_prefix_identity: str
    available_at: datetime
    status: str
    value: Decimal | None

    @property
    def feature_identity(self) -> str:
        return canonical_hash(
            {
                "feature_type": self.feature_type,
                "algorithm_version": self.algorithm_version,
                "parameters": [
                    [name, str(value) if isinstance(value, Decimal) else value]
                    for name, value in self.parameters
                ],
                "feature_version": self.feature_version,
                "numeric_policy_identity": self.numeric_policy_identity,
                "implementation_artifact_identity": self.implementation_artifact_identity,
                "timeframe_aggregation_identity": self.timeframe_aggregation_identity,
                "source_aggregate_identity": self.source_aggregate_identity,
                "dependency_prefix_identity": self.dependency_prefix_identity,
                "available_at": self.available_at.isoformat(),
                "status": self.status,
                "value": None if self.value is None else str(self.value),
            }
        )


@dataclass(frozen=True)
class ADXValue:
    feature_type: str
    algorithm_version: str
    parameters: tuple[tuple[str, object], ...]
    feature_version: str
    numeric_policy_identity: str
    implementation_artifact_identity: str
    timeframe_aggregation_identity: str
    source_aggregate_identity: str
    dependency_prefix_identity: str
    available_at: datetime
    status: str
    adx: Decimal | None
    plus_di: Decimal | None
    minus_di: Decimal | None
    dx: Decimal | None

    @property
    def feature_identity(self) -> str:
        return canonical_hash(
            {
                "feature_type": self.feature_type,
                "algorithm_version": self.algorithm_version,
                "parameters": [[name, value] for name, value in self.parameters],
                "feature_version": self.feature_version,
                "numeric_policy_identity": self.numeric_policy_identity,
                "implementation_artifact_identity": self.implementation_artifact_identity,
                "timeframe_aggregation_identity": self.timeframe_aggregation_identity,
                "source_aggregate_identity": self.source_aggregate_identity,
                "dependency_prefix_identity": self.dependency_prefix_identity,
                "available_at": self.available_at.isoformat(),
                "status": self.status,
                "adx": None if self.adx is None else str(self.adx),
                "plus_di": None if self.plus_di is None else str(self.plus_di),
                "minus_di": None if self.minus_di is None else str(self.minus_di),
                "dx": None if self.dx is None else str(self.dx),
            }
        )


def compute_ema(
    aggregation: AggregationResult,
    *,
    period: int,
    price_field: str,
    numeric_policy: FeatureNumericPolicy,
    feature_version: str,
) -> tuple[FeatureValue, ...]:
    bars = _validated_feature_input(aggregation)
    if type(period) is not int or period <= 0:
        raise ValueError("EMA period must be a positive integer")
    if price_field not in PRICE_FIELDS:
        raise ValueError("EMA price field must be open, high, low, or close")
    if not isinstance(numeric_policy, FeatureNumericPolicy):
        raise ValueError("EMA requires an explicit FeatureNumericPolicy")
    _require_text(feature_version, "feature version")
    prices = tuple(getattr(item, price_field) for item in bars)
    dependencies = _dependency_prefixes(bars)
    availability = _prefix_availability(bars)
    parameters = (("period", period), ("price_field", price_field))

    def emit(index: int, status: str, value: Decimal | None) -> FeatureValue:
        return FeatureValue(
            feature_type="EMA",
            algorithm_version=EMA_ALGORITHM_VERSION,
            parameters=parameters,
            feature_version=feature_version,
            numeric_policy_identity=numeric_policy.identity_id,
            implementation_artifact_identity=FEATURE_IMPLEMENTATION_BINDING.identity_id,
            timeframe_aggregation_identity=aggregation.feature_stream_identity,
            source_aggregate_identity=bars[index].identity_id,
            dependency_prefix_identity=dependencies[index],
            available_at=availability[index],
            status=status,
            value=value,
        )

    results: list[FeatureValue] = []
    for index in range(min(period - 1, len(bars))):
        results.append(emit(index, STATUS_INSUFFICIENT_HISTORY, None))
    if len(bars) < period:
        return tuple(results)
    ema = numeric_policy.internal(sum(prices[:period], Decimal(0)) / Decimal(period))
    results.append(emit(period - 1, STATUS_READY, numeric_policy.quantize(ema)))
    alpha = Decimal(2) / Decimal(period + 1)
    for index in range(period, len(bars)):
        ema = numeric_policy.internal(alpha * prices[index] + (Decimal(1) - alpha) * ema)
        results.append(emit(index, STATUS_READY, numeric_policy.quantize(ema)))
    return tuple(results)


def _directional_movement(
    bars: tuple[AggregatedBar, ...],
) -> tuple[list[Decimal | None], list[Decimal | None], list[Decimal | None]]:
    tr: list[Decimal | None] = [None] * len(bars)
    plus_dm: list[Decimal | None] = [None] * len(bars)
    minus_dm: list[Decimal | None] = [None] * len(bars)
    for index in range(1, len(bars)):
        current = bars[index]
        previous = bars[index - 1]
        tr[index] = max(
            current.high - current.low,
            abs(current.high - previous.close),
            abs(current.low - previous.close),
        )
        up_move = current.high - previous.high
        down_move = previous.low - current.low
        plus_dm[index] = up_move if up_move > down_move and up_move > 0 else Decimal(0)
        minus_dm[index] = down_move if down_move > up_move and down_move > 0 else Decimal(0)
    return tr, plus_dm, minus_dm


def compute_adx(
    aggregation: AggregationResult,
    *,
    period: int,
    numeric_policy: FeatureNumericPolicy,
    feature_version: str,
) -> tuple[ADXValue, ...]:
    bars = _validated_feature_input(aggregation)
    if type(period) is not int or period <= 0:
        raise ValueError("ADX period must be a positive integer")
    if not isinstance(numeric_policy, FeatureNumericPolicy):
        raise ValueError("ADX requires an explicit FeatureNumericPolicy")
    _require_text(feature_version, "feature version")
    count = len(bars)
    tr, plus_dm, minus_dm = _directional_movement(bars)
    dependencies = _dependency_prefixes(bars)
    availability = _prefix_availability(bars)
    s_tr: list[Decimal | None] = [None] * count
    s_plus: list[Decimal | None] = [None] * count
    s_minus: list[Decimal | None] = [None] * count
    if count > period:
        s_tr[period] = sum((item for item in tr[1 : period + 1] if item is not None), Decimal(0))
        s_plus[period] = sum((item for item in plus_dm[1 : period + 1] if item is not None), Decimal(0))
        s_minus[period] = sum((item for item in minus_dm[1 : period + 1] if item is not None), Decimal(0))
        denominator = Decimal(period)
        for index in range(period + 1, count):
            s_tr[index] = numeric_policy.internal(
                s_tr[index - 1] - s_tr[index - 1] / denominator + tr[index]
            )
            s_plus[index] = numeric_policy.internal(
                s_plus[index - 1] - s_plus[index - 1] / denominator + plus_dm[index]
            )
            s_minus[index] = numeric_policy.internal(
                s_minus[index - 1] - s_minus[index - 1] / denominator + minus_dm[index]
            )

    plus_di: list[Decimal | None] = [None] * count
    minus_di: list[Decimal | None] = [None] * count
    dx: list[Decimal | None] = [None] * count
    for index in range(count):
        if s_tr[index] is None or s_tr[index] == 0:
            continue
        plus_di[index] = Decimal(100) * s_plus[index] / s_tr[index]
        minus_di[index] = Decimal(100) * s_minus[index] / s_tr[index]
        dm_sum = s_plus[index] + s_minus[index]
        if dm_sum != 0:
            dx[index] = Decimal(100) * abs(s_plus[index] - s_minus[index]) / dm_sum

    first_adx_index = 2 * period - 1
    adx: list[Decimal | None] = [None] * count
    if count > first_adx_index:
        seed = dx[period : first_adx_index + 1]
        if all(item is not None for item in seed):
            adx[first_adx_index] = numeric_policy.internal(
                sum((item for item in seed if item is not None), Decimal(0)) / Decimal(period)
            )
            for index in range(first_adx_index + 1, count):
                if dx[index] is not None and adx[index - 1] is not None:
                    adx[index] = numeric_policy.internal(
                        (adx[index - 1] * Decimal(period - 1) + dx[index]) / Decimal(period)
                    )

    results: list[ADXValue] = []
    for index in range(count):
        ready = adx[index] is not None
        status = STATUS_READY if ready else (
            STATUS_INSUFFICIENT_HISTORY if index < first_adx_index else STATUS_UNDEFINED
        )
        results.append(
            ADXValue(
                feature_type="ADX",
                algorithm_version=ADX_ALGORITHM_VERSION,
                parameters=(("period", period),),
                feature_version=feature_version,
                numeric_policy_identity=numeric_policy.identity_id,
                implementation_artifact_identity=FEATURE_IMPLEMENTATION_BINDING.identity_id,
                timeframe_aggregation_identity=aggregation.feature_stream_identity,
                source_aggregate_identity=bars[index].identity_id,
                dependency_prefix_identity=dependencies[index],
                available_at=availability[index],
                status=status,
                adx=None if adx[index] is None else numeric_policy.quantize(adx[index]),
                plus_di=None if plus_di[index] is None else numeric_policy.quantize(plus_di[index]),
                minus_di=None if minus_di[index] is None else numeric_policy.quantize(minus_di[index]),
                dx=None if dx[index] is None else numeric_policy.quantize(dx[index]),
            )
        )
    return tuple(results)


def visible_features(
    features: Iterable[FeatureValue | ADXValue], timestamp: datetime
) -> tuple[FeatureValue | ADXValue, ...]:
    if timestamp.tzinfo is None:
        raise ValueError("visibility timestamp must be timezone-aware")
    return tuple(item for item in features if item.available_at <= timestamp)

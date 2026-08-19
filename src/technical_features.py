"""Generic point-in-time technical feature layer (Lane G).

Generic, candidate-independent infrastructure over ``NormalizedHistoricalBar``
and governed session metadata:

- deterministic session-aware aggregation from 1-minute bars to higher
  timeframes (explicit interval specifications; no session-break bridging);
- official trading-day identity (never civil-date inference);
- aggregate availability derived deterministically from constituent
  availability facts (no future leakage);
- deterministic EMA (documented initialization rule);
- deterministic Welles Wilder ADX (documented TR/+DM/-DM/smoothing/DI/DX/
  initialization semantics);
- versioned feature specification and identity bindings.

ENGINEERING FEATURE SEMANTICS
----------------------------
This module defines machine conventions for deterministic feature
computation.  These conventions are project engineering semantics, NOT claims
about any human trading source (``SOURCE CLAIM != PROJECT/AI INTERPRETATION
!= MACHINE OPERATIONALIZATION``).  No candidate parameter is selected or
tuned here; periods and price fields are always explicit caller inputs.  The
Raschke source (20 EMA / 14 ADX) is a later contract input, never hard-coded
research selection in this engine.

Numeric policy
--------------
- OHLCV aggregation is exact ``Decimal`` arithmetic (no rounding).
- Derived EMA/ADX ratios use ``Decimal`` with an explicit, documented output
  quantization (``FEATURE_QUANTUM`` = 6 decimal places, ``ROUND_HALF_UP``).
  Quantization is an engineering convention for deterministic, reproducible
  output; it is not market-data rounding and never touches stored prices.

Input policy
------------
- All input series are strictly ordered and timezone-aware; ambiguous
  chronology is rejected, never silently reordered.
- All tests use synthetic/non-candidate bars.  This module never reads the
  canonical real candidate corpus.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
import json
from typing import Iterable

from src.data_substrate import SessionMetadata, SessionWindow
from src.historical_data import NormalizedHistoricalBar

# ---------------------------------------------------------------------------
# Versions / semantics constants
# ---------------------------------------------------------------------------

AGGREGATION_SCHEMA_VERSION = "session-aware-pit-aggregation-v1"
FEATURE_SCHEMA_VERSION = "pit-technical-feature-v1"

FEATURE_QUANTUM = Decimal("0.000001")  # 6 decimal places
FEATURE_ROUNDING = ROUND_HALF_UP

FEATURE_TYPE_EMA = "EMA"
FEATURE_TYPE_ADX = "ADX"
EMA_ALGORITHM_VERSION = "sma-seed-recursive-v1"
ADX_ALGORITHM_VERSION = "wilder-directional-movement-v1"

STATUS_READY = "READY"
STATUS_INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"
STATUS_UNDEFINED = "UNDEFINED"
STATUS_UNKNOWN = "UNKNOWN"

VOLUME_STATUS_COMPLETE = "COMPLETE"
VOLUME_STATUS_UNKNOWN = "UNKNOWN"

PRICE_FIELDS = ("open", "high", "low", "close")


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _required_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


def _quantize(value: Decimal) -> Decimal:
    return value.quantize(FEATURE_QUANTUM, rounding=FEATURE_ROUNDING)


def _parameter_scalar(value: object) -> object:
    return str(value) if isinstance(value, Decimal) else value


# ---------------------------------------------------------------------------
# Timeframe specification
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TimeframeSpec:
    """Explicit, versioned aggregation specification.

    ``kind`` is ``"INTRADAY"`` (fixed ``interval_seconds`` buckets aligned
    from each explicit session-window start) or ``"DAILY"`` (one aggregate per
    official trading day over all of its valid session windows).  The engine
    supports arbitrary positive intraday intervals and daily aggregation; the
    commonly tested 5m/15m/30m/60m/120m/daily are not hard-coded limits.
    """

    name: str
    kind: str
    interval_seconds: int | None
    aggregation_version: str

    def __post_init__(self) -> None:
        _required_text(self.name, "timeframe name")
        if self.kind not in ("INTRADAY", "DAILY"):
            raise ValueError("timeframe kind must be INTRADAY or DAILY")
        if self.kind == "INTRADAY":
            if type(self.interval_seconds) is not int or self.interval_seconds <= 0:
                raise ValueError("intraday timeframe requires positive whole interval seconds")
        else:
            if self.interval_seconds is not None:
                raise ValueError("daily timeframe must not carry an interval")
        _required_text(self.aggregation_version, "timeframe aggregation version")

    @property
    def identity_id(self) -> str:
        return canonical_hash(
            {
                "name": self.name,
                "kind": self.kind,
                "interval_seconds": self.interval_seconds,
                "aggregation_version": self.aggregation_version,
                "aggregation_schema_version": AGGREGATION_SCHEMA_VERSION,
            }
        )


# ---------------------------------------------------------------------------
# Aggregated bar
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class AggregatedBar:
    """One point-in-time aggregate over completed normalized bars.

    ``available_at`` is derived deterministically as the latest constituent
    ``available_at``: the aggregate is never visible before all of its
    constituents are.  ``source_bar_identities`` binds every constituent
    normalized-bar identity so equivalent evidence produces the same identity
    and changed source evidence changes it.
    """

    exchange: str
    concrete_instrument: str
    trading_day: date
    timeframe_spec: TimeframeSpec
    session_metadata_version: str
    session_kind: str | None
    start: datetime
    end: datetime
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
            (self.session_metadata_version, "aggregate session metadata version"),
        ):
            _required_text(value, name)
        if not isinstance(self.timeframe_spec, TimeframeSpec):
            raise ValueError("aggregate requires a TimeframeSpec")
        for value, name in (
            (self.start, "aggregate start"),
            (self.end, "aggregate end"),
            (self.available_at, "aggregate available_at"),
        ):
            if value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware")
        if self.end <= self.start:
            raise ValueError("aggregate end must follow its start")
        if self.available_at < self.end:
            raise ValueError("unfinished aggregate cannot be visible as completed")
        prices = (self.open, self.high, self.low, self.close)
        if any(type(value) is not Decimal or not value.is_finite() or value <= 0 for value in prices):
            raise ValueError("aggregate OHLC must be positive finite Decimals")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close) or self.low > self.high:
            raise ValueError("aggregate OHLC values are inconsistent")
        if self.volume is not None and (
            type(self.volume) is not Decimal or not self.volume.is_finite() or self.volume < 0
        ):
            raise ValueError("aggregate volume must be a non-negative finite Decimal or None")
        if self.volume_status not in (VOLUME_STATUS_COMPLETE, VOLUME_STATUS_UNKNOWN):
            raise ValueError("aggregate volume status is not recognized")
        if self.volume is None and self.volume_status != VOLUME_STATUS_UNKNOWN:
            raise ValueError("a missing aggregate volume must be marked UNKNOWN")
        if self.volume is not None and self.volume_status != VOLUME_STATUS_COMPLETE:
            raise ValueError("a present aggregate volume must be marked COMPLETE")
        if not self.source_bar_identities:
            raise ValueError("aggregate requires at least one constituent bar identity")

    def is_visible_at(self, timestamp: datetime) -> bool:
        if timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return timestamp >= self.available_at

    @property
    def identity_id(self) -> str:
        return canonical_hash(
            {
                "exchange": self.exchange,
                "concrete_instrument": self.concrete_instrument,
                "trading_day": self.trading_day.isoformat(),
                "timeframe_spec_identity": self.timeframe_spec.identity_id,
                "session_metadata_version": self.session_metadata_version,
                "session_kind": self.session_kind,
                "start": self.start.isoformat(),
                "end": self.end.isoformat(),
                "open": str(self.open),
                "high": str(self.high),
                "low": str(self.low),
                "close": str(self.close),
                "volume": None if self.volume is None else str(self.volume),
                "volume_status": self.volume_status,
                "available_at": self.available_at.isoformat(),
                "source_bar_identities": sorted(self.source_bar_identities),
            }
        )


@dataclass(frozen=True)
class IncompleteBucket:
    """A bucket that failed closed because required constituent bars are absent."""

    trading_day: date
    session_kind: str
    start: datetime
    end: datetime
    missing_constituent_starts: tuple[datetime, ...]
    present_constituent_count: int

    def __post_init__(self) -> None:
        _required_text(self.session_kind, "incomplete bucket session kind")
        for value, name in (
            (self.start, "incomplete bucket start"),
            (self.end, "incomplete bucket end"),
        ):
            if value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware")
        if self.end <= self.start:
            raise ValueError("incomplete bucket end must follow its start")


@dataclass(frozen=True)
class AggregationResult:
    aggregates: tuple[AggregatedBar, ...]
    incomplete_buckets: tuple[IncompleteBucket, ...]

    def __post_init__(self) -> None:
        if any(not isinstance(item, AggregatedBar) for item in self.aggregates):
            raise ValueError("aggregation result contains an invalid aggregate")
        if any(not isinstance(item, IncompleteBucket) for item in self.incomplete_buckets):
            raise ValueError("aggregation result contains an invalid incomplete bucket")


# ---------------------------------------------------------------------------
# Session-aware timeframe aggregation
# ---------------------------------------------------------------------------


class TimeframeAggregator:
    """Deterministic session-aware aggregation from completed normalized bars.

    Intraday rules:
    - buckets align from each explicit session-window start;
    - buckets never bridge an exchange session break;
    - lunch/night breaks are never bridged to fill a bucket;
    - a bucket is emitted only when every required constituent bar exists.

    Daily rules:
    - one aggregate per official ``trading_day`` over all of its valid
      session windows (night + day belong to the same official day);
    - never uses the civil calendar date as the daily grouping key.

    Aggregates use the existing ``NormalizedHistoricalBar`` /
    ``CompletedBar`` / ``SessionWindow`` / ``SessionMetadata`` structures;
    no second historical-data model is introduced.
    """

    def __init__(self, sessions: SessionMetadata, base_interval_seconds: int = 60) -> None:
        if not isinstance(sessions, SessionMetadata):
            raise ValueError("timeframe aggregation requires SessionMetadata")
        if type(base_interval_seconds) is not int or base_interval_seconds <= 0:
            raise ValueError("base interval must be positive whole seconds")
        self._sessions = sessions
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
    ) -> AggregationResult:
        if not isinstance(spec, TimeframeSpec):
            raise ValueError("aggregation requires a TimeframeSpec")
        normalized = tuple(bars)
        if not normalized:
            raise ValueError("aggregation requires at least one bar")
        if any(not isinstance(item, NormalizedHistoricalBar) for item in normalized):
            raise ValueError("aggregation requires NormalizedHistoricalBar values")
        _required_text(exchange, "aggregation exchange")
        _required_text(concrete_instrument, "aggregation concrete instrument")
        starts = tuple(item.completed_bar.start for item in normalized)
        for item in normalized:
            if item.exchange != exchange or item.concrete_instrument != concrete_instrument:
                raise ValueError("aggregation bars must match the declared exchange/instrument")
            for value, name in (
                (item.completed_bar.start, "aggregation bar start"),
                (item.completed_bar.end, "aggregation bar end"),
                (item.completed_bar.available_at, "aggregation bar available_at"),
            ):
                if value.tzinfo is None:
                    raise ValueError(f"{name} must be timezone-aware")
        if len(set(starts)) != len(starts):
            raise ValueError("aggregation bars must not contain duplicate starts")
        if any(left >= right for left, right in zip(starts, starts[1:])):
            raise ValueError("aggregation bars must be strictly ordered by start")

        # Validate session membership and published expected starts (fail closed).
        expected_by_day: dict[date, set[datetime]] = {}
        by_trading_day: dict[date, list[NormalizedHistoricalBar]] = {}
        for item in normalized:
            by_trading_day.setdefault(item.completed_bar.trading_day, []).append(item)
        for trading_day, day_bars in by_trading_day.items():
            expected = set(
                self._sessions.expected_bar_starts(
                    exchange, concrete_instrument, trading_day, self._base_interval
                )
            )
            expected_by_day[trading_day] = expected
            for item in day_bars:
                window = self._sessions.window_at(exchange, concrete_instrument, item.completed_bar.start)
                if window is None:
                    raise ValueError("aggregation bar falls outside published sessions")
                if window.trading_day != item.completed_bar.trading_day:
                    raise ValueError("aggregation bar trading day disagrees with session metadata")
                if item.completed_bar.end > window.end:
                    raise ValueError("aggregation bar extends beyond its session window")
                if item.completed_bar.start not in expected:
                    raise ValueError("aggregation bar start is not a published expected bar start")

        if spec.kind == "DAILY":
            return self._aggregate_daily(normalized, spec, exchange, concrete_instrument)
        return self._aggregate_intraday(normalized, spec, exchange, concrete_instrument, expected_by_day)

    # -- helpers ------------------------------------------------------------

    def _aggregate_intraday(
        self,
        bars: tuple[NormalizedHistoricalBar, ...],
        spec: TimeframeSpec,
        exchange: str,
        concrete_instrument: str,
        expected_by_day: dict[date, set[datetime]],
    ) -> AggregationResult:
        interval = timedelta(seconds=spec.interval_seconds)
        window_groups: dict[SessionWindow, list[NormalizedHistoricalBar]] = {}
        for item in bars:
            window = self._sessions.window_at(exchange, concrete_instrument, item.completed_bar.start)
            assert window is not None
            window_groups.setdefault(window, []).append(item)

        aggregates: list[AggregatedBar] = []
        incomplete: list[IncompleteBucket] = []
        for window, group in sorted(window_groups.items(), key=lambda kv: (kv[0].trading_day, kv[0].start)):
            ordered = sorted(group, key=lambda item: item.completed_bar.start)
            bucket_start = window.start
            while bucket_start + interval <= window.end:
                bucket_end = bucket_start + interval
                constituents = [
                    item
                    for item in ordered
                    if bucket_start <= item.completed_bar.start < bucket_end
                ]
                required = {
                    start
                    for start in expected_by_day[window.trading_day]
                    if bucket_start <= start and start + self._base_interval <= bucket_end
                }
                present_starts = {item.completed_bar.start for item in constituents}
                if required and present_starts == required:
                    aggregates.append(
                        self._build_aggregate(constituents, window, bucket_start, bucket_end, spec)
                    )
                else:
                    missing = tuple(sorted(required - present_starts))
                    incomplete.append(
                        IncompleteBucket(
                            window.trading_day,
                            window.kind,
                            bucket_start,
                            bucket_end,
                            missing,
                            len(constituents),
                        )
                    )
                bucket_start = bucket_end
        aggregates.sort(key=lambda aggregate: aggregate.start)
        incomplete.sort(key=lambda bucket: (bucket.trading_day, bucket.start))
        return AggregationResult(tuple(aggregates), tuple(incomplete))

    def _aggregate_daily(
        self,
        bars: tuple[NormalizedHistoricalBar, ...],
        spec: TimeframeSpec,
        exchange: str,
        concrete_instrument: str,
    ) -> AggregationResult:
        by_day: dict[date, list[NormalizedHistoricalBar]] = {}
        for item in bars:
            by_day.setdefault(item.completed_bar.trading_day, []).append(item)
        aggregates: list[AggregatedBar] = []
        for trading_day in sorted(by_day):
            ordered = sorted(by_day[trading_day], key=lambda item: item.completed_bar.start)
            volumes = [item.volume for item in ordered]
            volume: Decimal | None = None
            volume_status = VOLUME_STATUS_UNKNOWN
            if all(value is not None for value in volumes):
                volume = sum(value for value in volumes if value is not None)
                volume_status = VOLUME_STATUS_COMPLETE
            aggregates.append(
                AggregatedBar(
                    exchange=exchange,
                    concrete_instrument=concrete_instrument,
                    trading_day=trading_day,
                    timeframe_spec=spec,
                    session_metadata_version=self._sessions.version,
                    session_kind=None,
                    start=ordered[0].completed_bar.start,
                    end=ordered[-1].completed_bar.end,
                    open=ordered[0].open,
                    high=max(item.high for item in ordered),
                    low=min(item.low for item in ordered),
                    close=ordered[-1].close,
                    volume=volume,
                    volume_status=volume_status,
                    available_at=max(item.completed_bar.available_at for item in ordered),
                    source_bar_identities=tuple(sorted(item.identity_id for item in ordered)),
                )
            )
        return AggregationResult(tuple(aggregates), ())

    def _build_aggregate(
        self,
        constituents: list[NormalizedHistoricalBar],
        window: SessionWindow,
        bucket_start: datetime,
        bucket_end: datetime,
        spec: TimeframeSpec,
    ) -> AggregatedBar:
        ordered = sorted(constituents, key=lambda item: item.completed_bar.start)
        volumes = [item.volume for item in ordered]
        volume: Decimal | None = None
        volume_status = VOLUME_STATUS_UNKNOWN
        if all(value is not None for value in volumes):
            volume = sum(value for value in volumes if value is not None)
            volume_status = VOLUME_STATUS_COMPLETE
        return AggregatedBar(
            exchange=ordered[0].exchange,
            concrete_instrument=ordered[0].concrete_instrument,
            trading_day=window.trading_day,
            timeframe_spec=spec,
            session_metadata_version=self._sessions.version,
            session_kind=window.kind,
            start=bucket_start,
            end=bucket_end,
            open=ordered[0].open,
            high=max(item.high for item in ordered),
            low=min(item.low for item in ordered),
            close=ordered[-1].close,
            volume=volume,
            volume_status=volume_status,
            available_at=max(item.completed_bar.available_at for item in ordered),
            source_bar_identities=tuple(sorted(item.identity_id for item in ordered)),
        )


def visible_aggregates(
    aggregates: Iterable[AggregatedBar], timestamp: datetime
) -> tuple[AggregatedBar, ...]:
    """Aggregates whose availability boundary is at or before ``timestamp``."""
    if timestamp.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return tuple(item for item in aggregates if item.available_at <= timestamp)


# ---------------------------------------------------------------------------
# Series validation shared by feature computations
# ---------------------------------------------------------------------------


def _validated_aggregate_series(aggregates: Iterable[AggregatedBar]) -> tuple[AggregatedBar, ...]:
    bars = tuple(aggregates)
    if not bars:
        raise ValueError("feature computation requires at least one aggregate")
    if any(not isinstance(item, AggregatedBar) for item in bars):
        raise ValueError("feature computation requires AggregatedBar values")
    for item in bars:
        for value, name in (
            (item.start, "aggregate start"),
            (item.end, "aggregate end"),
            (item.available_at, "aggregate available_at"),
        ):
            if value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware")
    starts = tuple(item.start for item in bars)
    if any(left >= right for left, right in zip(starts, starts[1:])):
        raise ValueError("feature input aggregates must be strictly ordered by start")
    if any(left.end > right.start for left, right in zip(bars, bars[1:])):
        raise ValueError("feature input aggregates must not overlap")
    timeframe_identity = bars[0].timeframe_spec.identity_id
    session_version = bars[0].session_metadata_version
    if any(
        item.timeframe_spec.identity_id != timeframe_identity
        or item.session_metadata_version != session_version
        for item in bars
    ):
        raise ValueError("feature input aggregates must share one timeframe aggregation identity")
    return bars


def _prefix_max_availability(bars: tuple[AggregatedBar, ...]) -> list[datetime]:
    result: list[datetime] = []
    current: datetime | None = None
    for item in bars:
        current = item.available_at if current is None else max(current, item.available_at)
        result.append(current)
    return result


def _series_timeframe_identity(bars: tuple[AggregatedBar, ...]) -> str:
    return canonical_hash(
        {
            "timeframe_spec_identity": bars[0].timeframe_spec.identity_id,
            "session_metadata_version": bars[0].session_metadata_version,
        }
    )


# ---------------------------------------------------------------------------
# Feature identity
# ---------------------------------------------------------------------------


def _feature_identity_core(
    *,
    feature_type: str,
    algorithm_version: str,
    parameters: tuple[tuple[str, object], ...],
    feature_version: str,
    timeframe_aggregation_identity: str,
    source_aggregate_identity: str,
    available_at: datetime,
    status: str,
    value_payload: object,
) -> str:
    return canonical_hash(
        {
            "feature_type": feature_type,
            "algorithm_version": algorithm_version,
            "parameters": [[name, _parameter_scalar(value)] for name, value in parameters],
            "feature_version": feature_version,
            "timeframe_aggregation_identity": timeframe_aggregation_identity,
            "source_aggregate_identity": source_aggregate_identity,
            "available_at": available_at.isoformat(),
            "status": status,
            "value": value_payload,
        }
    )


@dataclass(frozen=True)
class FeatureValue:
    """One emitted feature value with its full identity binding."""

    feature_type: str
    algorithm_version: str
    parameters: tuple[tuple[str, object], ...]
    feature_version: str
    timeframe_aggregation_identity: str
    source_aggregate_identity: str
    available_at: datetime
    status: str
    value: Decimal | None

    def __post_init__(self) -> None:
        _required_text(self.feature_type, "feature type")
        _required_text(self.algorithm_version, "algorithm version")
        _required_text(self.feature_version, "feature version")
        _required_text(self.timeframe_aggregation_identity, "timeframe aggregation identity")
        _required_text(self.source_aggregate_identity, "source aggregate identity")
        if self.available_at.tzinfo is None:
            raise ValueError("feature availability must be timezone-aware")
        if self.status not in (STATUS_READY, STATUS_INSUFFICIENT_HISTORY, STATUS_UNDEFINED, STATUS_UNKNOWN):
            raise ValueError("feature status is not recognized")
        if self.status == STATUS_READY and self.value is None:
            raise ValueError("a READY feature must carry a value")
        if self.status != STATUS_READY and self.value is not None:
            raise ValueError("a non-READY feature must not carry a value")
        names = tuple(name for name, _ in self.parameters)
        if len(names) != len(set(names)):
            raise ValueError("feature parameters must be unique")

    @property
    def feature_identity(self) -> str:
        return _feature_identity_core(
            feature_type=self.feature_type,
            algorithm_version=self.algorithm_version,
            parameters=self.parameters,
            feature_version=self.feature_version,
            timeframe_aggregation_identity=self.timeframe_aggregation_identity,
            source_aggregate_identity=self.source_aggregate_identity,
            available_at=self.available_at,
            status=self.status,
            value_payload=None if self.value is None else str(self.value),
        )


# ---------------------------------------------------------------------------
# EMA
# ---------------------------------------------------------------------------


def compute_ema(
    aggregates: Iterable[AggregatedBar],
    *,
    period: int,
    price_field: str,
    feature_version: str = "v1",
) -> tuple[FeatureValue, ...]:
    """Deterministic EMA over a point-in-time aggregate series.

    Initialization rule (ENGINEERING FEATURE SEMANTICS, not a Raschke claim):

    - first EMA = simple average (SMA) of the first ``period`` observations;
    - subsequent: ``alpha = 2 / (period + 1)``,
      ``EMA_t = alpha * price_t + (1 - alpha) * EMA_(t-1)``;
    - before ``period`` observations the status is ``INSUFFICIENT_HISTORY``
      (never a silent zero/NaN treated as a feature).

    The EMA at index ``i`` depends on the whole prefix ``0..i``, so its
    availability boundary is the latest ``available_at`` over that prefix.
    """
    bars = _validated_aggregate_series(aggregates)
    if type(period) is not int or period <= 0:
        raise ValueError("EMA period must be a positive integer")
    if price_field not in PRICE_FIELDS:
        raise ValueError("EMA price field must be one of open/high/low/close")
    _required_text(feature_version, "feature version")
    prices = tuple(getattr(item, price_field) for item in bars)
    prefix_availability = _prefix_max_availability(bars)
    timeframe_identity = _series_timeframe_identity(bars)
    parameters = (("period", period), ("price_field", price_field))

    def emit(index: int, status: str, value: Decimal | None) -> FeatureValue:
        return FeatureValue(
            feature_type=FEATURE_TYPE_EMA,
            algorithm_version=EMA_ALGORITHM_VERSION,
            parameters=parameters,
            feature_version=feature_version,
            timeframe_aggregation_identity=timeframe_identity,
            source_aggregate_identity=bars[index].identity_id,
            available_at=prefix_availability[index],
            status=status,
            value=value,
        )

    results: list[FeatureValue] = []
    if len(bars) < period:
        for index in range(len(bars)):
            results.append(emit(index, STATUS_INSUFFICIENT_HISTORY, None))
        return tuple(results)

    for index in range(period - 1):
        results.append(emit(index, STATUS_INSUFFICIENT_HISTORY, None))

    ema = _quantize(sum(prices[:period]) / Decimal(period))
    results.append(emit(period - 1, STATUS_READY, ema))

    alpha = Decimal(2) / Decimal(period + 1)
    one_minus_alpha = Decimal(1) - alpha
    for index in range(period, len(bars)):
        ema = _quantize(alpha * prices[index] + one_minus_alpha * ema)
        results.append(emit(index, STATUS_READY, ema))
    return tuple(results)


# ---------------------------------------------------------------------------
# Welles Wilder ADX
# ---------------------------------------------------------------------------


def wilder_directional_movement(
    aggregates: Iterable[AggregatedBar],
) -> tuple[tuple[Decimal | None, ...], tuple[Decimal | None, ...], tuple[Decimal | None, ...]]:
    """Raw True Range, +DM and -DM for each aggregate (all ``None`` for the first).

    Definitions (ENGINEERING FEATURE SEMANTICS):

    - ``TR = max(high - low, |high - prev_close|, |low - prev_close|)``;
    - ``+DM = high - prev_high`` when that is positive and strictly greater
      than ``prev_low - low``, otherwise 0;
    - ``-DM = prev_low - low`` when that is positive and strictly greater
      than ``high - prev_high``, otherwise 0.
    """
    bars = _validated_aggregate_series(aggregates)
    count = len(bars)
    tr: list[Decimal | None] = [None] * count
    plus_dm: list[Decimal | None] = [None] * count
    minus_dm: list[Decimal | None] = [None] * count
    for index in range(1, count):
        high = bars[index].high
        low = bars[index].low
        prev_high = bars[index - 1].high
        prev_low = bars[index - 1].low
        prev_close = bars[index - 1].close
        tr[index] = max(high - low, abs(high - prev_close), abs(low - prev_close))
        up_move = high - prev_high
        down_move = prev_low - low
        if up_move > down_move and up_move > 0:
            plus_dm[index] = up_move
        else:
            plus_dm[index] = Decimal(0)
        if down_move > up_move and down_move > 0:
            minus_dm[index] = down_move
        else:
            minus_dm[index] = Decimal(0)
    return (tuple(tr), tuple(plus_dm), tuple(minus_dm))


@dataclass(frozen=True)
class ADXValue:
    """One ADX feature value with DI/DX diagnostics and full identity binding."""

    feature_type: str
    algorithm_version: str
    parameters: tuple[tuple[str, object], ...]
    feature_version: str
    timeframe_aggregation_identity: str
    source_aggregate_identity: str
    available_at: datetime
    status: str
    adx: Decimal | None
    plus_di: Decimal | None
    minus_di: Decimal | None
    dx: Decimal | None

    def __post_init__(self) -> None:
        _required_text(self.feature_type, "feature type")
        _required_text(self.algorithm_version, "algorithm version")
        _required_text(self.feature_version, "feature version")
        _required_text(self.timeframe_aggregation_identity, "timeframe aggregation identity")
        _required_text(self.source_aggregate_identity, "source aggregate identity")
        if self.available_at.tzinfo is None:
            raise ValueError("feature availability must be timezone-aware")
        if self.status not in (STATUS_READY, STATUS_INSUFFICIENT_HISTORY, STATUS_UNDEFINED):
            raise ValueError("ADX feature status is not recognized")
        if self.status == STATUS_READY and self.adx is None:
            raise ValueError("a READY ADX feature must carry an ADX value")
        if self.status != STATUS_READY and self.adx is not None:
            raise ValueError("a non-READY ADX feature must not carry an ADX value")
        names = tuple(name for name, _ in self.parameters)
        if len(names) != len(set(names)):
            raise ValueError("ADX feature parameters must be unique")

    @property
    def feature_identity(self) -> str:
        return _feature_identity_core(
            feature_type=self.feature_type,
            algorithm_version=self.algorithm_version,
            parameters=self.parameters,
            feature_version=self.feature_version,
            timeframe_aggregation_identity=self.timeframe_aggregation_identity,
            source_aggregate_identity=self.source_aggregate_identity,
            available_at=self.available_at,
            status=self.status,
            value_payload={
                "adx": None if self.adx is None else str(self.adx),
                "plus_di": None if self.plus_di is None else str(self.plus_di),
                "minus_di": None if self.minus_di is None else str(self.minus_di),
                "dx": None if self.dx is None else str(self.dx),
            },
        )


def compute_adx(
    aggregates: Iterable[AggregatedBar],
    *,
    period: int,
    feature_version: str = "v1",
) -> tuple[ADXValue, ...]:
    """Deterministic Welles Wilder ADX over a point-in-time aggregate series.

    Documented semantics (ENGINEERING FEATURE SEMANTICS):

    - True Range / +DM / -DM per ``wilder_directional_movement``;
    - Wilder smoothing: the first smoothed value is the simple sum of the
      first ``period`` raw values; subsequent
      ``S_t = S_(t-1) - S_(t-1)/period + raw_t`` (never an EMA-style
      substitution);
    - ``+DI = 100 * S_plus / S_tr``, ``-DI = 100 * S_minus / S_tr``;
    - ``DX = 100 * |S_plus - S_minus| / (S_plus + S_minus)`` (equivalent to
      the DI ratio form; computed from the Wilder-smoothed values so it does
      not inherit DI output quantization);
    - ADX initialization: first ADX = simple average of the first ``period``
      DX values;
    - recursive ADX update:
      ``ADX_t = (ADX_(t-1) * (period - 1) + DX_t) / period``.

    Warmup rule (off-by-one exact): with ``period`` P, raw TR/+DM/-DM exist
    from aggregate index 1; smoothed values from index P; DX from index P; the
    first ADX exists at aggregate index ``2*P - 1`` (after ``P`` DX values).
    Before that, status is ``INSUFFICIENT_HISTORY``.  When a denominator is
    zero (degenerate input), DI/DX/ADX are ``UNDEFINED`` (fail closed), never
    fabricated.

    The ADX at index ``i`` depends on the whole prefix ``0..i``, so its
    availability boundary is the latest ``available_at`` over that prefix.
    """
    bars = _validated_aggregate_series(aggregates)
    if type(period) is not int or period <= 0:
        raise ValueError("ADX period must be a positive integer")
    _required_text(feature_version, "feature version")
    count = len(bars)
    tr, plus_dm, minus_dm = wilder_directional_movement(bars)
    prefix_availability = _prefix_max_availability(bars)
    timeframe_identity = _series_timeframe_identity(bars)
    parameters = (("period", period),)

    # Wilder smoothing.
    s_tr: list[Decimal | None] = [None] * count
    s_plus: list[Decimal | None] = [None] * count
    s_minus: list[Decimal | None] = [None] * count
    if count > period:
        s_tr[period] = sum(value for value in tr[1 : period + 1] if value is not None)
        s_plus[period] = sum(value for value in plus_dm[1 : period + 1] if value is not None)
        s_minus[period] = sum(value for value in minus_dm[1 : period + 1] if value is not None)
        wilder_denominator = Decimal(period)
        for index in range(period + 1, count):
            s_tr[index] = s_tr[index - 1] - s_tr[index - 1] / wilder_denominator + tr[index]
            s_plus[index] = (
                s_plus[index - 1] - s_plus[index - 1] / wilder_denominator + plus_dm[index]
            )
            s_minus[index] = (
                s_minus[index - 1] - s_minus[index - 1] / wilder_denominator + minus_dm[index]
            )

    def di(index: int) -> tuple[Decimal | None, Decimal | None]:
        tr_value = s_tr[index]
        if tr_value is None or tr_value == 0:
            return (None, None)
        return (
            _quantize(Decimal(100) * s_plus[index] / tr_value),
            _quantize(Decimal(100) * s_minus[index] / tr_value),
        )

    def dx(index: int) -> Decimal | None:
        plus_value = s_plus[index]
        minus_value = s_minus[index]
        if plus_value is None or minus_value is None:
            return None
        denominator = plus_value + minus_value
        if denominator == 0:
            return None
        return _quantize(Decimal(100) * abs(plus_value - minus_value) / denominator)

    # ADX initialization / recursive update.
    first_adx_index = 2 * period - 1
    adx: list[Decimal | None] = [None] * count
    if count > first_adx_index:
        seed = tuple(dx(index) for index in range(period, first_adx_index + 1))
        if all(value is not None for value in seed):
            adx[first_adx_index] = _quantize(sum(seed) / Decimal(period))
            for index in range(first_adx_index + 1, count):
                dx_value = dx(index)
                if dx_value is None:
                    adx[index] = None
                else:
                    previous = adx[index - 1]
                    if previous is None:
                        adx[index] = None
                    else:
                        adx[index] = _quantize(
                            (previous * Decimal(period - 1) + dx_value) / Decimal(period)
                        )

    results: list[ADXValue] = []
    for index in range(count):
        plus_di, minus_di = di(index)
        dx_value = dx(index)
        adx_value = adx[index]
        if adx_value is not None:
            status = STATUS_READY
        elif index < first_adx_index:
            status = STATUS_INSUFFICIENT_HISTORY
        else:
            status = STATUS_UNDEFINED
        results.append(
            ADXValue(
                feature_type=FEATURE_TYPE_ADX,
                algorithm_version=ADX_ALGORITHM_VERSION,
                parameters=parameters,
                feature_version=feature_version,
                timeframe_aggregation_identity=timeframe_identity,
                source_aggregate_identity=bars[index].identity_id,
                available_at=prefix_availability[index],
                status=status,
                adx=adx_value,
                plus_di=plus_di,
                minus_di=minus_di,
                dx=dx_value,
            )
        )
    return tuple(results)


def visible_features(
    features: Iterable[FeatureValue | ADXValue], timestamp: datetime
) -> tuple[FeatureValue | ADXValue, ...]:
    """Feature values whose availability boundary is at or before ``timestamp``."""
    if timestamp.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return tuple(item for item in features if item.available_at <= timestamp)

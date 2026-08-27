"""Broker-neutral real-time closed-bar normalization for future PAPER.

No network access or TqSdk import occurs here. Raw TqSdk-like kline rows are
injected by a transport and become visible only after their bar end has passed.
Bootstrap establishes a watermark without emitting historical wakes.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Any, Mapping, Protocol
from zoneinfo import ZoneInfo

from src.data_substrate import BarQuality, CompletedBar

LIVE_MARKET_DATA_SCHEMA_VERSION = "KPE_LIVE_CLOSED_BAR_V0_1"

class LiveSessionResolver(Protocol):
    def trading_day_at(self, exchange: str, instrument: str, timestamp: datetime) -> date | None: ...
    def expected_bar_starts_between(
        self, exchange: str, instrument: str, coverage_start: datetime,
        coverage_end: datetime, interval: timedelta,
    ) -> tuple[datetime, ...]: ...

def _hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()

def _decimal(value: object, field_name: str, *, optional: bool = False) -> Decimal | None:
    if value is None and optional:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be a finite number")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{field_name} must be a finite number") from error
    if not parsed.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return parsed

def tqsdk_nanoseconds_to_datetime(value: object, timezone: ZoneInfo) -> datetime:
    if isinstance(value, bool):
        raise ValueError("TqSdk kline datetime must be integer nanoseconds")
    try:
        nanoseconds = int(value)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError("TqSdk kline datetime must be integer nanoseconds") from error
    try:
        if Decimal(str(value)) != Decimal(nanoseconds):
            raise ValueError("TqSdk kline datetime must be integer nanoseconds")
    except InvalidOperation as error:
        raise ValueError("TqSdk kline datetime must be integer nanoseconds") from error
    seconds, remainder = divmod(nanoseconds, 1_000_000_000)
    try:
        return datetime.fromtimestamp(seconds, tz=timezone) + timedelta(microseconds=remainder // 1_000)
    except (OSError, OverflowError, ValueError) as error:
        raise ValueError("TqSdk kline datetime is outside supported range") from error

@dataclass(frozen=True)
class LiveClosedBar:
    exchange: str
    concrete_instrument: str
    completed_bar: CompletedBar
    observed_at: datetime
    source: str
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal | None
    open_interest_start: Decimal | None
    open_interest_end: Decimal | None

    def __post_init__(self) -> None:
        if not self.exchange or not self.concrete_instrument or not self.source:
            raise ValueError("live bar requires exchange, instrument and source identities")
        if self.completed_bar.instrument != self.concrete_instrument:
            raise ValueError("live bar instrument identity mismatch")
        if self.observed_at.tzinfo is None:
            raise ValueError("live bar observed_at must be timezone-aware")
        if self.observed_at < self.completed_bar.end:
            raise ValueError("unfinished bar cannot be represented as LiveClosedBar")
        prices = (self.open, self.high, self.low, self.close)
        if any(type(value) is not Decimal or not value.is_finite() or value <= 0 for value in prices):
            raise ValueError("live bar OHLC must be positive finite Decimals")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close) or self.low > self.high:
            raise ValueError("live bar OHLC values are inconsistent")
        for value in (self.volume, self.open_interest_start, self.open_interest_end):
            if value is not None and (type(value) is not Decimal or not value.is_finite() or value < 0):
                raise ValueError("live volume/open interest must be non-negative finite Decimals")

    @property
    def identity_id(self) -> str:
        return _hash({
            "schema_version": LIVE_MARKET_DATA_SCHEMA_VERSION,
            "exchange": self.exchange,
            "concrete_instrument": self.concrete_instrument,
            "bar_start": self.completed_bar.start.isoformat(),
            "bar_end": self.completed_bar.end.isoformat(),
            "available_at": self.completed_bar.available_at.isoformat(),
            "trading_day": self.completed_bar.trading_day.isoformat(),
            "observed_at": self.observed_at.isoformat(),
            "source": self.source,
            "open": str(self.open), "high": str(self.high), "low": str(self.low), "close": str(self.close),
            "volume": None if self.volume is None else str(self.volume),
            "open_interest_start": None if self.open_interest_start is None else str(self.open_interest_start),
            "open_interest_end": None if self.open_interest_end is None else str(self.open_interest_end),
        })

def normalize_tqsdk_live_kline_row(
    row: Mapping[str, Any], *, exchange: str, concrete_instrument: str,
    duration_seconds: int, timezone: str, observed_at: datetime,
    sessions: LiveSessionResolver, source: str = "TQSDK_PAPER_CANDIDATE",
) -> LiveClosedBar:
    if not isinstance(row, Mapping):
        raise ValueError("live TqSdk kline row must be a mapping")
    if type(duration_seconds) is not int or duration_seconds <= 0:
        raise ValueError("live bar duration must be a positive integer")
    if observed_at.tzinfo is None:
        raise ValueError("live observed_at must be timezone-aware")
    tz = ZoneInfo(timezone)
    start = tqsdk_nanoseconds_to_datetime(row.get("datetime"), tz)
    end = start + timedelta(seconds=duration_seconds)
    if end > observed_at.astimezone(tz):
        raise ValueError("LIVE_BAR_NOT_CLOSED")
    trading_day = sessions.trading_day_at(exchange, concrete_instrument, start)
    if trading_day is None:
        raise ValueError("live bar falls outside governed session metadata")
    row_symbol = row.get("symbol")
    if row_symbol is not None and row_symbol != concrete_instrument:
        raise ValueError("live TqSdk row contract identity mismatch")
    open_price = _decimal(row.get("open"), "open")
    high_price = _decimal(row.get("high"), "high")
    low_price = _decimal(row.get("low"), "low")
    close_price = _decimal(row.get("close"), "close")
    assert open_price is not None and high_price is not None and low_price is not None and close_price is not None
    volume = _decimal(row.get("volume"), "volume", optional=True)
    open_oi = _decimal(row.get("open_oi"), "open_oi", optional=True)
    close_oi = _decimal(row.get("close_oi"), "close_oi", optional=True)
    completed = CompletedBar(
        instrument=concrete_instrument, trading_day=trading_day, start=start, end=end,
        available_at=observed_at.astimezone(tz), quality=BarQuality(),
    )
    return LiveClosedBar(
        exchange=exchange, concrete_instrument=concrete_instrument, completed_bar=completed,
        observed_at=observed_at.astimezone(tz), source=source,
        open=open_price, high=high_price, low=low_price, close=close_price,
        volume=volume, open_interest_start=open_oi, open_interest_end=close_oi,
    )

class TqSdkClosedBarTracker:
    """Stateful closed-bar watermark with bootstrap suppression and gap checks."""

    def __init__(self, *, exchange: str, concrete_instrument: str, duration_seconds: int,
                 timezone: str, sessions: LiveSessionResolver) -> None:
        if type(duration_seconds) is not int or duration_seconds <= 0:
            raise ValueError("tracker duration must be a positive integer")
        self.exchange = exchange
        self.concrete_instrument = concrete_instrument
        self.duration_seconds = duration_seconds
        self.timezone = timezone
        self.sessions = sessions
        self._watermark_start: datetime | None = None

    @property
    def watermark_start(self) -> datetime | None:
        return self._watermark_start

    def _closed_rows(self, rows: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
                     observed_at: datetime) -> tuple[LiveClosedBar, ...]:
        tz = ZoneInfo(self.timezone)
        interval = timedelta(seconds=self.duration_seconds)
        result: list[LiveClosedBar] = []
        prior_start: datetime | None = None
        for row in rows:
            if not isinstance(row, Mapping):
                raise ValueError("live kline serial must contain mapping rows")
            start = tqsdk_nanoseconds_to_datetime(row.get("datetime"), tz)
            if prior_start is not None and start <= prior_start:
                reason = "duplicate" if start == prior_start else "out-of-order"
                raise ValueError(f"live kline serial contains {reason} timestamps")
            prior_start = start
            if start + interval > observed_at.astimezone(tz):
                continue
            result.append(normalize_tqsdk_live_kline_row(
                row, exchange=self.exchange, concrete_instrument=self.concrete_instrument,
                duration_seconds=self.duration_seconds, timezone=self.timezone,
                observed_at=observed_at, sessions=self.sessions,
            ))
        return tuple(result)

    def bootstrap(self, rows: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...], *,
                  observed_at: datetime) -> tuple[LiveClosedBar, ...]:
        closed = self._closed_rows(rows, observed_at)
        if closed:
            self._watermark_start = closed[-1].completed_bar.start
        return ()

    def poll(self, rows: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...], *,
             observed_at: datetime) -> tuple[LiveClosedBar, ...]:
        closed = self._closed_rows(rows, observed_at)
        if not closed:
            return ()
        if self._watermark_start is None:
            raise RuntimeError("LIVE_TRACKER_NOT_BOOTSTRAPPED")
        candidates = tuple(bar for bar in closed if bar.completed_bar.start > self._watermark_start)
        if not candidates:
            return ()
        interval = timedelta(seconds=self.duration_seconds)
        expected = self.sessions.expected_bar_starts_between(
            self.exchange, self.concrete_instrument, self._watermark_start + interval,
            candidates[-1].completed_bar.end, interval,
        )
        observed = tuple(bar.completed_bar.start for bar in candidates)
        if observed != expected:
            missing = sorted(set(expected) - set(observed))
            unexpected = sorted(set(observed) - set(expected))
            raise ValueError(
                f"LIVE_BAR_SEQUENCE_MISMATCH missing={[x.isoformat() for x in missing]} "
                f"unexpected={[x.isoformat() for x in unexpected]}"
            )
        self._watermark_start = candidates[-1].completed_bar.start
        return candidates

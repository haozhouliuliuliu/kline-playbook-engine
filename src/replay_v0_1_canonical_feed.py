"""Canonical 1-minute -> fixed-5m replay preflight for V0.1.

This module deliberately stops before 15m/1H/4H resampling. Current authority
freezes those timeframes and the role of 4H, but does not freeze exact higher-
timeframe bucket anchors. The mechanics implemented here are already governed:
accepted canonical 1m rows, official session windows, night-closed trading days,
and one wake per newly closed 5m bar.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo

FEED_VERSION = "KPE_REPLAY_V0_1_CANONICAL_FIXED_5M_PREFLIGHT_V0_1"
_SHANGHAI = ZoneInfo("Asia/Shanghai")
_ONE_MINUTE = timedelta(minutes=1)
_FIVE_MINUTES = timedelta(minutes=5)


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value.strip()


def _aware(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _decimal_text(value: Decimal) -> str:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError("OHLCV values must be finite Decimal values")
    return format(value, "f")


@dataclass(frozen=True)
class ReplayMinuteBar:
    product: str
    concrete_contract: str
    trading_day: date
    start: datetime
    end: datetime
    available_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    partition_identity: str
    session_authority_identity: str

    def __post_init__(self) -> None:
        _require_text(self.product, "product")
        _require_text(self.concrete_contract, "concrete_contract")
        _require_text(self.partition_identity, "partition_identity")
        _require_text(self.session_authority_identity, "session_authority_identity")
        _aware(self.start, "minute start")
        _aware(self.end, "minute end")
        _aware(self.available_at, "minute available_at")
        if self.end - self.start != _ONE_MINUTE:
            raise ValueError("canonical replay input must contain exact 1-minute bars")
        if self.available_at < self.end:
            raise ValueError("minute bar cannot be historically available before it closes")
        values = (self.open, self.high, self.low, self.close, self.volume)
        if any(not isinstance(item, Decimal) or not item.is_finite() for item in values):
            raise ValueError("canonical replay OHLCV must be finite Decimal values")
        if min(self.open, self.high, self.low, self.close) <= 0:
            raise ValueError("canonical replay OHLC must be positive")
        if self.volume < 0:
            raise ValueError("canonical replay volume must be non-negative")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close) or self.low > self.high:
            raise ValueError("canonical replay OHLC is inconsistent")


@dataclass(frozen=True)
class GovernedSessionWindow:
    trading_day: date
    kind: str
    ordinal: int
    start: datetime
    end: datetime
    session_authority_identity: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.kind not in {"night", "day"}:
            raise ValueError("governed session kind must be night or day")
        if type(self.ordinal) is not int or self.ordinal < 0:
            raise ValueError("session ordinal must be a non-negative integer")
        _aware(self.start, "session start")
        _aware(self.end, "session end")
        _require_text(self.session_authority_identity, "session authority identity")
        if self.end <= self.start:
            raise ValueError("session end must follow session start")
        duration = self.end - self.start
        if duration % _ONE_MINUTE != timedelta(0) or duration % _FIVE_MINUTES != timedelta(0):
            raise ValueError("V0.1 governed session duration must be divisible by 5 minutes")
        object.__setattr__(self, "identity", _hash({
            "feed_version": FEED_VERSION,
            "trading_day": self.trading_day.isoformat(),
            "kind": self.kind,
            "ordinal": self.ordinal,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "session_authority_identity": self.session_authority_identity,
        }))

    @property
    def expected_minute_count(self) -> int:
        return int((self.end - self.start) / _ONE_MINUTE)

    @property
    def expected_wake_count(self) -> int:
        return int((self.end - self.start) / _FIVE_MINUTES)


@dataclass(frozen=True)
class ReplayFiveMinuteBar:
    product: str
    concrete_contract: str
    trading_day: date
    session_window_identity: str
    start: datetime
    end: datetime
    available_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    partition_identity: str
    source_minute_starts: tuple[datetime, ...]
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.end - self.start != _FIVE_MINUTES:
            raise ValueError("replay wake bar must be exactly 5 minutes")
        if self.available_at > self.end:
            raise ValueError("5m wake would use a constituent minute unavailable at bar close")
        if len(self.source_minute_starts) != 5:
            raise ValueError("5m wake must bind exactly five canonical minute bars")
        expected = tuple(self.start + index * _ONE_MINUTE for index in range(5))
        if self.source_minute_starts != expected:
            raise ValueError("5m wake source minutes are not exact and contiguous")
        object.__setattr__(self, "identity", _hash({
            "feed_version": FEED_VERSION,
            "product": self.product,
            "concrete_contract": self.concrete_contract,
            "trading_day": self.trading_day.isoformat(),
            "session_window_identity": self.session_window_identity,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "available_at": self.available_at.isoformat(),
            "open": _decimal_text(self.open),
            "high": _decimal_text(self.high),
            "low": _decimal_text(self.low),
            "close": _decimal_text(self.close),
            "volume": _decimal_text(self.volume),
            "partition_identity": self.partition_identity,
            "source_minute_starts": [item.isoformat() for item in self.source_minute_starts],
        }))


@dataclass(frozen=True)
class CanonicalFiveMinutePreflight:
    product: str
    concrete_contract: str
    replay_days: tuple[date, ...]
    windows: tuple[GovernedSessionWindow, ...]
    wake_bars: tuple[ReplayFiveMinuteBar, ...]
    minute_count: int
    expected_minute_count: int
    expected_wake_count: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.minute_count != self.expected_minute_count:
            raise ValueError("canonical minute count does not equal governed expected count")
        if len(self.wake_bars) != self.expected_wake_count:
            raise ValueError("fixed-5m wake count does not equal governed expected count")
        if tuple(sorted(set(self.replay_days))) != self.replay_days:
            raise ValueError("replay days must be strictly increasing and unique")
        starts = tuple(item.start for item in self.wake_bars)
        if tuple(sorted(set(starts))) != starts:
            raise ValueError("5m wake bars must be strictly increasing and unique")
        object.__setattr__(self, "identity", _hash({
            "feed_version": FEED_VERSION,
            "product": self.product,
            "concrete_contract": self.concrete_contract,
            "replay_days": [item.isoformat() for item in self.replay_days],
            "window_identities": [item.identity for item in self.windows],
            "wake_identities": [item.identity for item in self.wake_bars],
            "minute_count": self.minute_count,
            "expected_minute_count": self.expected_minute_count,
            "expected_wake_count": self.expected_wake_count,
        }))

    def summary(self) -> dict[str, object]:
        by_day: dict[str, int] = {day.isoformat(): 0 for day in self.replay_days}
        for bar in self.wake_bars:
            by_day[bar.trading_day.isoformat()] += 1
        return {
            "feed_version": FEED_VERSION,
            "preflight_identity": self.identity,
            "product": self.product,
            "concrete_contract": self.concrete_contract,
            "replay_start": self.replay_days[0].isoformat(),
            "replay_end": self.replay_days[-1].isoformat(),
            "replay_day_count": len(self.replay_days),
            "governed_session_window_count": len(self.windows),
            "minute_count": self.minute_count,
            "expected_minute_count": self.expected_minute_count,
            "wake_count": len(self.wake_bars),
            "expected_wake_count": self.expected_wake_count,
            "wake_count_by_trading_day": by_day,
            "provider_call_authorized": False,
        }


def governed_windows_for_days(*, product: str, replay_days: Sequence[date], trading_calendar: Sequence[date], night_closed_days: frozenset[date], session_schedule: Mapping[str, Any]) -> tuple[GovernedSessionWindow, ...]:
    calendar = tuple(trading_calendar)
    calendar_index = {day: index for index, day in enumerate(calendar)}
    if len(calendar_index) != len(calendar):
        raise ValueError("trading calendar must be unique")
    record = session_schedule.get(product)
    if not isinstance(record, Mapping):
        raise ValueError(f"session authority has no product {product}")
    if record.get("timezone") != "Asia/Shanghai":
        raise ValueError("V0.1 session timezone must be Asia/Shanghai")
    authority_identity = _require_text(record.get("identity"), "product session authority identity")
    raw_day_windows = record.get("day_windows")
    raw_night_window = record.get("night_window")
    if not isinstance(raw_day_windows, list) or not raw_day_windows:
        raise ValueError("session authority requires day windows")
    if not isinstance(raw_night_window, list) or len(raw_night_window) != 2:
        raise ValueError("session authority requires one night window")
    windows: list[GovernedSessionWindow] = []
    for day in replay_days:
        if day not in calendar_index:
            raise ValueError("replay day is outside governed trading calendar")
        ordinal = 0
        if day not in night_closed_days:
            index = calendar_index[day]
            if index == 0:
                raise ValueError("cannot resolve night session without previous trading day")
            previous = calendar[index - 1]
            night_start_t = time.fromisoformat(raw_night_window[0])
            night_end_t = time.fromisoformat(raw_night_window[1])
            night_start = datetime.combine(previous, night_start_t, tzinfo=_SHANGHAI)
            end_day = previous + timedelta(days=1) if night_end_t <= night_start_t else previous
            night_end = datetime.combine(end_day, night_end_t, tzinfo=_SHANGHAI)
            windows.append(GovernedSessionWindow(day, "night", ordinal, night_start, night_end, authority_identity))
            ordinal += 1
        for raw_window in raw_day_windows:
            if not isinstance(raw_window, list) or len(raw_window) != 2:
                raise ValueError("day session window must be [start, end]")
            start = datetime.combine(day, time.fromisoformat(raw_window[0]), tzinfo=_SHANGHAI)
            end = datetime.combine(day, time.fromisoformat(raw_window[1]), tzinfo=_SHANGHAI)
            windows.append(GovernedSessionWindow(day, "day", ordinal, start, end, authority_identity))
            ordinal += 1
    return tuple(windows)


def expected_fixed_5m_wake_count(windows: Sequence[GovernedSessionWindow]) -> int:
    return sum(item.expected_wake_count for item in windows)


def build_fixed_5m_preflight(*, product: str, concrete_contract: str, replay_days: Sequence[date], windows: Sequence[GovernedSessionWindow], minute_bars: Iterable[ReplayMinuteBar]) -> CanonicalFiveMinutePreflight:
    replay_days_tuple = tuple(replay_days)
    window_tuple = tuple(windows)
    bars = tuple(sorted(minute_bars, key=lambda item: item.start))
    if not replay_days_tuple or not window_tuple or not bars:
        raise ValueError("preflight requires replay days, governed windows and canonical minute bars")
    if any(item.product != product or item.concrete_contract != concrete_contract for item in bars):
        raise ValueError("canonical minute row disagrees with sealed product/contract")
    by_start: dict[datetime, ReplayMinuteBar] = {}
    for bar in bars:
        if bar.start in by_start:
            raise ValueError("duplicate canonical minute start")
        if bar.trading_day not in replay_days_tuple:
            raise ValueError("canonical minute row is outside sealed replay days")
        by_start[bar.start] = bar
    expected_all_starts: set[datetime] = set()
    wake_bars: list[ReplayFiveMinuteBar] = []
    for window in window_tuple:
        if window.trading_day not in replay_days_tuple:
            raise ValueError("governed window is outside sealed replay days")
        minute_starts = tuple(window.start + index * _ONE_MINUTE for index in range(window.expected_minute_count))
        expected_all_starts.update(minute_starts)
        missing = [item for item in minute_starts if item not in by_start]
        if missing:
            raise ValueError(f"canonical replay partition is missing {len(missing)} governed minute bars in {window.trading_day.isoformat()} {window.kind}#{window.ordinal}")
        for offset in range(0, len(minute_starts), 5):
            source_starts = minute_starts[offset:offset + 5]
            source = tuple(by_start[item] for item in source_starts)
            partition_ids = {item.partition_identity for item in source}
            session_ids = {item.session_authority_identity for item in source}
            trading_days = {item.trading_day for item in source}
            if len(partition_ids) != 1 or len(session_ids) != 1 or trading_days != {window.trading_day}:
                raise ValueError("5m source minutes cross a partition/session/trading-day boundary")
            if session_ids != {window.session_authority_identity}:
                raise ValueError("canonical row session identity disagrees with governed session authority")
            bucket_start, bucket_end = source[0].start, source[-1].end
            available_at = max(item.available_at for item in source)
            if available_at > bucket_end:
                raise ValueError("historical 1m availability would leak past the fixed 5m wake close")
            wake_bars.append(ReplayFiveMinuteBar(product, concrete_contract, window.trading_day, window.identity, bucket_start, bucket_end, available_at, source[0].open, max(item.high for item in source), min(item.low for item in source), source[-1].close, sum((item.volume for item in source), Decimal(0)), source[0].partition_identity, source_starts))
    unexpected = set(by_start) - expected_all_starts
    if unexpected:
        raise ValueError(f"canonical replay input contains {len(unexpected)} minute bars outside governed sessions")
    return CanonicalFiveMinutePreflight(product, concrete_contract, replay_days_tuple, window_tuple, tuple(wake_bars), len(bars), sum(item.expected_minute_count for item in window_tuple), expected_fixed_5m_wake_count(window_tuple))


def load_canonical_minute_bars_from_parquet(*, parquet_root: Path, product: str, concrete_contract: str, replay_days: Sequence[date], partition_identity_by_day: Mapping[date, str], session_authority_identity_by_day: Mapping[date, str]) -> tuple[ReplayMinuteBar, ...]:
    try:
        import pyarrow.dataset as ds  # noqa: PLC0415
    except ImportError as error:  # pragma: no cover
        raise RuntimeError("canonical replay Parquet preflight requires the pinned pyarrow environment") from error
    root = Path(parquet_root)
    if not root.is_dir():
        raise ValueError("canonical parquet root does not exist")
    days = tuple(replay_days)
    if set(days) != set(partition_identity_by_day) or set(days) != set(session_authority_identity_by_day):
        raise ValueError("sealed replay days must have exact partition and session identity bindings")
    dataset = ds.dataset(str(root), format="parquet", partitioning="hive")
    expression = (ds.field("product") == product) & (ds.field("concrete_contract") == concrete_contract)
    table = dataset.to_table(columns=["product", "concrete_contract", "trading_day", "bar_start", "bar_end", "historical_available_at", "open", "high", "low", "close", "volume", "session_metadata_identity"], filter=expression)
    wanted = set(days)
    result: list[ReplayMinuteBar] = []
    for row in table.to_pylist():
        trading_day = row["trading_day"]
        if trading_day not in wanted:
            continue
        if row["volume"] is None:
            raise ValueError("selected canonical replay minute has missing volume")
        row_session_identity = _require_text(row["session_metadata_identity"], "canonical session metadata identity")
        expected_session_identity = session_authority_identity_by_day[trading_day]
        if row_session_identity != expected_session_identity:
            raise ValueError("canonical Parquet session identity disagrees with sealed manifest binding")
        result.append(ReplayMinuteBar(product=row["product"], concrete_contract=row["concrete_contract"], trading_day=trading_day, start=row["bar_start"], end=row["bar_end"], available_at=row["historical_available_at"], open=row["open"], high=row["high"], low=row["low"], close=row["close"], volume=Decimal(row["volume"]), partition_identity=partition_identity_by_day[trading_day], session_authority_identity=expected_session_identity))
    return tuple(sorted(result, key=lambda item: item.start))


__all__ = ["CanonicalFiveMinutePreflight", "FEED_VERSION", "GovernedSessionWindow", "ReplayFiveMinuteBar", "ReplayMinuteBar", "build_fixed_5m_preflight", "expected_fixed_5m_wake_count", "governed_windows_for_days", "load_canonical_minute_bars_from_parquet"]

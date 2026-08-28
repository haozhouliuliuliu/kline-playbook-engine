"""Causal 4H/1H/15m/5m context wiring for SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1.

This module restores the Owner-approved session-aware lower-timeframe semantics
and the formal ``SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1`` 4H representation on top
of the accepted canonical 1-minute corpus. It builds a deterministic closed-bar
index and serves a bounded causal context per governed 5m wake.

Restored / frozen semantics (Owner authority, not invented here):

- 15m / 1H (``SESSION_AUTHORITY_CONTIGUOUS_WINDOW_GRID_V0_1``)
  - each contiguous official session window starts a fresh bucket;
  - a session break disconnects immediately (no K-line bridges a break);
  - the bucket starts at the continuous official window start;
  - a shortened trailing bucket is never a complete bar.
- 4H (``SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1``)
  - Asia/Shanghai civil 4-hour grid, local hour ``floor(hour / 4) * 4``;
  - only official trading minutes of one official trading day inside that grid;
  - lunch-break minutes are not missing minutes;
  - no cross official trading day;
  - a bar is complete only when all its official minutes have ended and are
    causally visible;
  - ``open_time`` = first official trading minute, ``close_time`` = last
    official trading minute end;
  - 4H role: ``BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY``
    (no exact cross-timeframe volume reconciliation with 4H).

Bounded context window counts (Owner-approved four-timeframe input shape):

    4H = 2, 1H = 3, 15m = 12, 5m = 36

This module makes no model/provider call and never emits a provider request.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal
from hashlib import sha256
import json
from typing import Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo

from src.jianghe_ai_trader import ObservationBar
from src.replay_v0_1_canonical_feed import (
    GovernedSessionWindow,
    ReplayFiveMinuteBar,
    ReplayMinuteBar,
)
from src.replay_v0_1_canonical_steps import canonical_5m_to_observation_bar
from src.causal_context_semantics import (
    ACTIVE_TIMEFRAMES,
    CONTEXT_WINDOW_COUNTS,
    FOUR_HOUR_AGGREGATION_VERSION,
    FOUR_HOUR_CIVIL_GRID_HOURS,
    FOUR_HOUR_ROLE,
    LOWER_AGGREGATION_VERSION,
    LOWER_TIMEFRAME_PERIODS,
)

CONTEXT_VERSION = "KPE_REPLAY_V0_1_CAUSAL_CONTEXT_V0_1"

_SHANGHAI = ZoneInfo("Asia/Shanghai")
_ONE_MINUTE = timedelta(minutes=1)


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _aware(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _decimal_text(value: Decimal) -> str:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError("canonical OHLCV must be finite Decimal values")
    if value == 0:
        return "0"
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def context_policy_document() -> dict[str, object]:
    """The serializable frozen causal-context policy document.

    Binds aggregation versions, context window counts, the lower bucket rule,
    the 4H civil-grid rule, the 4H role and ``provider_call_authorized=False``.
    """
    return {
        "context_version": CONTEXT_VERSION,
        "lower_aggregation_version": LOWER_AGGREGATION_VERSION,
        "four_hour_aggregation_version": FOUR_HOUR_AGGREGATION_VERSION,
        "context_window_counts": CONTEXT_WINDOW_COUNTS,
        "lower_bucket_rule": "SESSION_AUTHORITY_CONTIGUOUS_WINDOW_GRID",
        "four_hour_rule": "SESSION_AUTHORITY_CIVIL_4H_GRID",
        "four_hour_role": FOUR_HOUR_ROLE,
        "provider_call_authorized": False,
    }


def context_policy_identity() -> str:
    """Stable identity over the frozen causal-context policy."""
    return _hash(context_policy_document())


@dataclass(frozen=True)
class CausalContextBar:
    """One deterministic closed aggregation bar with attributable provenance."""

    timeframe: str
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
    source_minute_starts: tuple[datetime, ...]
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.timeframe not in ACTIVE_TIMEFRAMES:
            raise ValueError(f"unknown causal context timeframe {self.timeframe!r}")
        _aware(self.start, "bar start")
        _aware(self.end, "bar end")
        _aware(self.available_at, "bar available_at")
        if self.end <= self.start:
            raise ValueError("bar end must follow bar start")
        if self.available_at < self.end:
            raise ValueError("closed bar cannot be available before it closes")
        if not isinstance(self.partition_identity, str) or not self.partition_identity:
            raise ValueError("bar partition identity must be non-empty")
        if not isinstance(self.session_authority_identity, str) or not self.session_authority_identity:
            raise ValueError("bar session authority identity must be non-empty")
        if not self.source_minute_starts or tuple(sorted(set(self.source_minute_starts))) != self.source_minute_starts:
            raise ValueError("bar source minutes must be strictly increasing and unique")
        for value, name in (
            (self.open, "open"), (self.high, "high"),
            (self.low, "low"), (self.close, "close"),
        ):
            if not isinstance(value, Decimal) or not value.is_finite() or value <= 0:
                raise ValueError(f"bar {name} must be a positive finite Decimal")
        if not isinstance(self.volume, Decimal) or not self.volume.is_finite() or self.volume < 0:
            raise ValueError("bar volume must be a non-negative finite Decimal")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close) or self.low > self.high:
            raise ValueError("bar OHLC is inconsistent")
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "context_version": CONTEXT_VERSION,
                    "timeframe": self.timeframe,
                    "trading_day": self.trading_day.isoformat(),
                    "start": self.start.isoformat(),
                    "end": self.end.isoformat(),
                    "available_at": self.available_at.isoformat(),
                    "open": _decimal_text(self.open),
                    "high": _decimal_text(self.high),
                    "low": _decimal_text(self.low),
                    "close": _decimal_text(self.close),
                    "volume": _decimal_text(self.volume),
                    "partition_identity": self.partition_identity,
                    "session_authority_identity": self.session_authority_identity,
                    "source_minute_starts": [item.isoformat() for item in self.source_minute_starts],
                }
            ),
        )

    def to_observation_bar(self) -> ObservationBar:
        return ObservationBar(
            timeframe=self.timeframe,
            open_time=self.start,
            close_time=self.end,
            available_at=self.available_at,
            open_price=_decimal_text(self.open),
            high_price=_decimal_text(self.high),
            low_price=_decimal_text(self.low),
            close_price=_decimal_text(self.close),
            volume=_decimal_text(self.volume),
            is_closed=True,
        )


def _bar_from_minutes(
    *,
    timeframe: str,
    minutes: Sequence[ReplayMinuteBar],
    contiguous: bool,
) -> CausalContextBar:
    if not minutes:
        raise ValueError(f"{timeframe} bar requires at least one canonical minute")
    ordered = tuple(sorted(minutes, key=lambda item: item.start))
    if tuple(sorted(set(item.start for item in ordered))) != tuple(item.start for item in ordered):
        raise ValueError(f"{timeframe} bar minutes must be unique")
    if len({item.trading_day for item in ordered}) != 1:
        raise ValueError(f"{timeframe} bar minutes must belong to one trading day")
    if len({item.partition_identity for item in ordered}) != 1:
        raise ValueError(f"{timeframe} bar minutes must belong to one partition")
    if len({item.session_authority_identity for item in ordered}) != 1:
        raise ValueError(f"{timeframe} bar minutes must belong to one session authority")
    if contiguous:
        for before, after in zip(ordered, ordered[1:]):
            if after.start - before.end != timedelta(0):
                raise ValueError(f"{timeframe} bar minutes must be contiguous")
    start = ordered[0].start
    end = ordered[-1].end
    if end - start < timedelta(minutes=1):
        raise ValueError(f"{timeframe} bar must span at least one minute")
    available_at = max(item.available_at for item in ordered)
    return CausalContextBar(
        timeframe=timeframe,
        trading_day=ordered[0].trading_day,
        start=start,
        end=end,
        available_at=available_at,
        open=ordered[0].open,
        high=max(item.high for item in ordered),
        low=min(item.low for item in ordered),
        close=ordered[-1].close,
        volume=sum((item.volume for item in ordered), Decimal(0)),
        partition_identity=ordered[0].partition_identity,
        session_authority_identity=ordered[0].session_authority_identity,
        source_minute_starts=tuple(item.start for item in ordered),
    )


def _civil_grid_anchor(value: datetime) -> datetime:
    local = _aware(value, "grid minute").astimezone(_SHANGHAI)
    grid_hour = (local.hour // FOUR_HOUR_CIVIL_GRID_HOURS) * FOUR_HOUR_CIVIL_GRID_HOURS
    return local.replace(hour=grid_hour, minute=0, second=0, microsecond=0)


@dataclass(frozen=True)
class CanonicalCausalContextIndex:
    """Deterministic closed 5m/15m/1H/4H index over one sealed slice's corpus."""

    product: str
    concrete_contract: str
    windows: tuple[GovernedSessionWindow, ...]
    five_minute_bars: tuple[CausalContextBar, ...]
    fifteen_minute_bars: tuple[CausalContextBar, ...]
    one_hour_bars: tuple[CausalContextBar, ...]
    four_hour_bars: tuple[CausalContextBar, ...]
    policy_identity: str = field(default_factory=context_policy_identity)
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if not isinstance(self.product, str) or not self.product:
            raise ValueError("product must be non-empty")
        if not isinstance(self.concrete_contract, str) or not self.concrete_contract:
            raise ValueError("concrete_contract must be non-empty")
        if not self.windows:
            raise ValueError("causal index requires governed windows")
        if not self.policy_identity:
            raise ValueError("causal index requires a context policy identity")
        for name in ("five_minute_bars", "fifteen_minute_bars", "one_hour_bars", "four_hour_bars"):
            bars = getattr(self, name)
            if any(not isinstance(item, CausalContextBar) for item in bars):
                raise ValueError(f"{name} must contain CausalContextBar values")
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "context_version": CONTEXT_VERSION,
                    "policy_identity": self.policy_identity,
                    "product": self.product,
                    "concrete_contract": self.concrete_contract,
                    "window_identities": [item.identity for item in self.windows],
                    "five_minute_bars": [item.identity for item in self.five_minute_bars],
                    "fifteen_minute_bars": [item.identity for item in self.fifteen_minute_bars],
                    "one_hour_bars": [item.identity for item in self.one_hour_bars],
                    "four_hour_bars": [item.identity for item in self.four_hour_bars],
                }
            ),
        )

    @classmethod
    def build(
        cls,
        *,
        product: str,
        concrete_contract: str,
        windows: Sequence[GovernedSessionWindow],
        minute_bars: Sequence[ReplayMinuteBar],
    ) -> "CanonicalCausalContextIndex":
        window_tuple = tuple(windows)
        rows = tuple(minute_bars)
        if not window_tuple or not rows:
            raise ValueError("causal index requires governed windows and canonical minutes")
        if any(item.product != product or item.concrete_contract != concrete_contract for item in rows):
            raise ValueError("canonical minute row disagrees with sealed product/contract")
        by_start: dict[datetime, ReplayMinuteBar] = {}
        for row in rows:
            if row.start in by_start:
                raise ValueError("duplicate canonical minute start")
            by_start[row.start] = row
        expected_all: set[datetime] = set()
        for window in window_tuple:
            minute_starts = tuple(
                window.start + index * _ONE_MINUTE for index in range(window.expected_minute_count)
            )
            expected_all.update(minute_starts)
            missing = [item for item in minute_starts if item not in by_start]
            if missing:
                raise ValueError(
                    f"causal index is missing {len(missing)} governed 1m bars in "
                    f"{window.trading_day.isoformat()} {window.kind}#{window.ordinal}"
                )
        unexpected = set(by_start) - expected_all
        if unexpected:
            raise ValueError(f"causal index contains {len(unexpected)} 1m bars outside governed windows")

        five: list[CausalContextBar] = []
        fifteen: list[CausalContextBar] = []
        one_hour: list[CausalContextBar] = []
        for window in window_tuple:
            minute_starts = tuple(
                window.start + index * _ONE_MINUTE for index in range(window.expected_minute_count)
            )
            for timeframe, period in (
                ("5m", 5), ("15m", 15), ("1H", 60),
            ):
                target = {"5m": five, "15m": fifteen, "1H": one_hour}[timeframe]
                offset = 0
                while offset + period <= len(minute_starts):
                    bucket = minute_starts[offset:offset + period]
                    source = tuple(by_start[item] for item in bucket)
                    target.append(
                        _bar_from_minutes(
                            timeframe=timeframe,
                            minutes=source,
                            contiguous=True,
                        )
                    )
                    offset += period
        four_hour = _build_four_hour_bars(windows=window_tuple, by_start=by_start)
        return cls(
            product=product,
            concrete_contract=concrete_contract,
            windows=window_tuple,
            five_minute_bars=tuple(five),
            fifteen_minute_bars=tuple(fifteen),
            one_hour_bars=tuple(one_hour),
            four_hour_bars=four_hour,
        )

    def bar_counts(self) -> dict[str, int]:
        return {
            "4H": len(self.four_hour_bars),
            "1H": len(self.one_hour_bars),
            "15m": len(self.fifteen_minute_bars),
            "5m": len(self.five_minute_bars),
        }

    def _visible_bars(
        self,
        bars: tuple[CausalContextBar, ...],
        *,
        timeframe: str,
        wake_available_at: datetime,
    ) -> tuple[CausalContextBar, ...]:
        return tuple(
            item
            for item in bars
            if item.timeframe == timeframe
            and item.available_at <= wake_available_at
            and item.end <= wake_available_at
        )

    def context_for_wake(self, wake: ReplayFiveMinuteBar) -> tuple[ObservationBar, ...]:
        """Serve a bounded causal 4H/1H/15m/5m context for one governed wake.

        Fails closed if any active timeframe lacks the required window count,
        if the newest 5m bar is not the governed wake, or if the newest 5m bar
        disagrees with the canonical wake observation.
        """
        if not isinstance(wake, ReplayFiveMinuteBar):
            raise TypeError("wake must be ReplayFiveMinuteBar")
        if wake.product != self.product or wake.concrete_contract != self.concrete_contract:
            raise ValueError("wake disagrees with the sealed causal index product/contract")
        available = wake.available_at
        four = self._visible_bars(self.four_hour_bars, timeframe="4H", wake_available_at=available)[-CONTEXT_WINDOW_COUNTS["4H"]:]
        one = self._visible_bars(self.one_hour_bars, timeframe="1H", wake_available_at=available)[-CONTEXT_WINDOW_COUNTS["1H"]:]
        fifteen = self._visible_bars(self.fifteen_minute_bars, timeframe="15m", wake_available_at=available)[-CONTEXT_WINDOW_COUNTS["15m"]:]
        five = self._visible_bars(self.five_minute_bars, timeframe="5m", wake_available_at=available)[-CONTEXT_WINDOW_COUNTS["5m"]:]
        expected_counts = CONTEXT_WINDOW_COUNTS
        actual_counts = {"4H": len(four), "1H": len(one), "15m": len(fifteen), "5m": len(five)}
        if any(actual_counts[item] < expected_counts[item] for item in ACTIVE_TIMEFRAMES):
            raise ValueError(
                "causal context is short of closed active-stack history at the governed wake; "
                f"required {expected_counts}, got {actual_counts}"
            )
        wake_observation = canonical_5m_to_observation_bar(wake)
        newest_five = five[-1]
        if newest_five.start != wake.start or newest_five.end != wake.end:
            raise ValueError("newest 5m context bar is not the governed wake bar")
        if newest_five.to_observation_bar() != wake_observation:
            raise ValueError("newest 5m context bar disagrees with the canonical wake observation")
        return tuple(
            [item.to_observation_bar() for item in four]
            + [item.to_observation_bar() for item in one]
            + [item.to_observation_bar() for item in fifteen]
            + [item.to_observation_bar() for item in five[:-1]]
            + [wake_observation]
        )


def _build_four_hour_bars(
    *,
    windows: Sequence[GovernedSessionWindow],
    by_start: Mapping[datetime, ReplayMinuteBar],
) -> tuple[CausalContextBar, ...]:
    groups: dict[tuple[date, datetime], list[ReplayMinuteBar]] = {}
    for window in windows:
        for index in range(window.expected_minute_count):
            minute = by_start[window.start + index * _ONE_MINUTE]
            anchor = _civil_grid_anchor(minute.start)
            groups.setdefault((window.trading_day, anchor), []).append(minute)
    bars: list[CausalContextBar] = []
    for (trading_day, anchor) in sorted(groups):
        minutes = tuple(sorted(groups[(trading_day, anchor)], key=lambda item: item.start))
        bars.append(
            _bar_from_minutes(
                timeframe="4H",
                minutes=minutes,
                contiguous=False,
            )
        )
    return tuple(bars)


__all__ = [
    "ACTIVE_TIMEFRAMES",
    "CONTEXT_VERSION",
    "CONTEXT_WINDOW_COUNTS",
    "CanonicalCausalContextIndex",
    "CausalContextBar",
    "FOUR_HOUR_AGGREGATION_VERSION",
    "FOUR_HOUR_ROLE",
    "LOWER_AGGREGATION_VERSION",
    "context_policy_document",
    "context_policy_identity",
]

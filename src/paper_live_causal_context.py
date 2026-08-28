"""Streaming causal live 1m -> 5m/15m/1H/4H context builder for future PAPER.

OFFLINE ONLY. This module performs no provider, broker, account, credential or
network action. It consumes broker-neutral closed 1-minute bars (already
normalized, e.g. ``LiveClosedBar``) and builds a governed, session-aware,
deterministic causal context: a closed 5m wake plus closed 15m / 1H / 4H
context, with stable identities, bootstrap suppression, restart/reconnect
continuity and a durable wake-journal integration seam.

Aggregation semantics
---------------------
This is outcome-independent PAPER prebuild engineering. It mechanically reuses
the frozen Jianghe four-timeframe session rules (contiguous-window grid for
5m/15m/1H and the Asia/Shanghai civil 4H grid) but keeps the aggregation behind
an explicit PAPER-specific policy identity (``KPE_PAPER_LIVE_AGGREGATION_POLICY_V0_1``)
that is NOT an Owner-approved permanent PAPER policy.

- 5m / 15m / 1H: each contiguous official session window starts a fresh bucket;
  a session break disconnects immediately; a shortened trailing bucket is never
  a complete bar.
- 4H: Asia/Shanghai civil 4-hour grid (``floor(hour/4)*4``); only official
  trading minutes of one official trading day inside that grid; lunch-break
  minutes are not missing minutes; no cross official trading day; a bar is
  complete only when every governed minute of that grid has ended and is
  causally available.

Invariants proven here
----------------------
- timezone-aware timestamps only;
- explicit exchange and concrete contract identity;
- official trading-day/session attribution from canonical calendar authority;
- only completely closed 1m bars are admitted;
- finite valid OHLCV;
- causal ``available_at`` (never before bar close, never in the future);
- no future bar;
- no duplicate minute; no out-of-order minute; no unexplained missing minute;
- no cross-contract aggregation; no cross-trading-day contamination;
- session breaks are never filled or bridged;
- incomplete higher-timeframe buckets are never emitted;
- deterministic 5m wake: no wake before close, no duplicate wake on repeated
  polling, no bootstrap storm, stable identity, exact restart duplicate
  prevention.

Bootstrap / restart / reconnect
-------------------------------
- ``bootstrap`` absorbs a historical closed-bar serial to establish state and
  watermark WITHOUT emitting historical wakes; only newly completed governed 5m
  bars after bootstrap can produce new live wakes.
- ``snapshot`` / ``from_checkpoint`` provide a serializable checkpoint
  (admitted minutes, watermark, processed/emitted 5m bar ends, last emitted
  wake) so a restart restores deterministically.
- ``observe`` is the single admission point used for live streaming and for
  reconnect catch-up. If a governed minute is missing (an unexplained gap) it
  FAILS CLOSED with ``LIVE_CAUSAL_MINUTE_GAP`` and mutates no state.
- Already-accepted minutes are never re-dispatched, and an accepted 5m wake is
  never emitted twice (even after restart).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Iterable, Mapping, Sequence
from zoneinfo import ZoneInfo

from src.data_substrate import BarQuality, CompletedBar
from src.replay_v0_1_canonical_feed import governed_windows_for_days
from src.causal_context_semantics import (
    ACTIVE_TIMEFRAMES,
    CONTEXT_WINDOW_COUNTS,
    FOUR_HOUR_AGGREGATION_VERSION,
    FOUR_HOUR_CIVIL_GRID_HOURS,
    FOUR_HOUR_ROLE,
    LOWER_AGGREGATION_VERSION,
    LOWER_TIMEFRAME_PERIODS,
)

PAPER_LIVE_CAUSAL_CONTEXT_VERSION = "KPE_PAPER_LIVE_CAUSAL_CONTEXT_V0_1"
PAPER_LIVE_AGGREGATION_POLICY_VERSION = "KPE_PAPER_LIVE_AGGREGATION_POLICY_V0_1"
PAPER_LIVE_CAUSAL_CHECKPOINT_VERSION = "KPE_PAPER_LIVE_CAUSAL_CHECKPOINT_V0_1"

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


def _require_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value.strip()


def _decimal_text(value: Decimal) -> str:
    if not isinstance(value, Decimal) or not value.is_finite():
        raise ValueError("OHLCV values must be finite Decimal values")
    if value == 0:
        return "0"
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _parse_decimal(value: object, name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a finite number")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{name} must be a finite number") from error
    if not parsed.is_finite():
        raise ValueError(f"{name} must be finite")
    return parsed


def paper_live_aggregation_policy_document() -> dict[str, object]:
    """Serializable PAPER-specific live aggregation policy document.

    Explicitly labeled as NOT an Owner-approved permanent PAPER aggregation
    policy. No provider call is authorized by this policy.
    """
    return {
        "policy_version": PAPER_LIVE_AGGREGATION_POLICY_VERSION,
        "lower_aggregation_rule": LOWER_AGGREGATION_VERSION,
        "four_hour_rule": FOUR_HOUR_AGGREGATION_VERSION,
        "four_hour_role": FOUR_HOUR_ROLE,
        "context_window_counts": CONTEXT_WINDOW_COUNTS,
        "bootstrap_rule": "SUPPRESS_HISTORICAL_WAKES",
        "duplicate_rule": "NEVER_REDISPATCH_ACCEPTED_WAKE",
        "gap_rule": "FAIL_CLOSED_ON_UNEXPLAINED_MISSING_MINUTE",
        "owner_approved_permanent_paper_policy": False,
        "provider_call_authorized": False,
    }


def paper_live_aggregation_policy_identity() -> str:
    """Stable identity over the PAPER-specific live aggregation policy."""
    return _hash(paper_live_aggregation_policy_document())


@dataclass(frozen=True)
class LiveSessionWindow:
    """One governed session window for a concrete live instrument."""

    trading_day: date
    kind: str
    ordinal: int
    start: datetime
    end: datetime
    session_authority_identity: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.kind not in {"night", "day"}:
            raise ValueError("live session kind must be night or day")
        if type(self.ordinal) is not int or self.ordinal < 0:
            raise ValueError("live session ordinal must be a non-negative integer")
        _aware(self.start, "live session start")
        _aware(self.end, "live session end")
        _require_text(self.session_authority_identity, "live session authority identity")
        if self.end <= self.start:
            raise ValueError("live session end must follow its start")
        if (self.end - self.start) % _ONE_MINUTE != timedelta(0):
            raise ValueError("live session duration must be a whole number of minutes")
        object.__setattr__(self, "identity", _hash({
            "schema_version": PAPER_LIVE_CAUSAL_CONTEXT_VERSION,
            "trading_day": self.trading_day.isoformat(),
            "kind": self.kind,
            "ordinal": self.ordinal,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "session_authority_identity": self.session_authority_identity,
        }))

    def contains(self, timestamp: datetime) -> bool:
        local = _aware(timestamp, "live session check").astimezone(_SHANGHAI)
        return self.start <= local < self.end


class LiveSessionCalendar:
    """Session-aware resolver built from canonical calendar + schedule authority.

    Reuses ``governed_windows_for_days`` for governed window construction and
    provides the live context with: official trading-day attribution, expected
    governed 1-minute starts, next-expected-minute continuity and per-trading-day
    session windows. Construction is offline and performs no I/O beyond the
    supplied in-memory authority payloads.
    """

    def __init__(
        self,
        *,
        product: str,
        trading_calendar: Iterable[date],
        night_closed_days: Iterable[date],
        session_schedule: Mapping[str, object],
        calendar_authority_identity: str | None = None,
        calendar_verified_at: datetime | None = None,
        timezone: str = "Asia/Shanghai",
    ) -> None:
        if timezone != "Asia/Shanghai":
            raise ValueError("live session calendar timezone must be Asia/Shanghai")
        self._product = _require_text(product, "live session product")
        self._calendar = tuple(sorted(set(trading_calendar)))
        if not self._calendar:
            raise ValueError("live session calendar requires trading days")
        self._calendar_index = {day: index for index, day in enumerate(self._calendar)}
        if len(self._calendar_index) != len(self._calendar):
            raise ValueError("live session trading calendar must be unique")
        self._night_closed = frozenset(night_closed_days)
        if not self._night_closed.issubset(set(self._calendar)):
            raise ValueError("night-closed days must belong to the governed trading calendar")
        if not isinstance(session_schedule, Mapping):
            raise ValueError("live session schedule must be a mapping")
        record = session_schedule.get(product)
        if not isinstance(record, Mapping):
            raise ValueError(f"live session authority has no product {product}")
        if record.get("timezone") != "Asia/Shanghai":
            raise ValueError("live session timezone must be Asia/Shanghai")
        self._schedule = record
        self._session_authority_identity = _require_text(
            record.get("identity"), "live session authority identity"
        )
        if calendar_authority_identity is not None:
            self._calendar_authority_identity = _require_text(
                calendar_authority_identity, "live calendar authority identity"
            )
        else:
            self._calendar_authority_identity = None
        if calendar_verified_at is not None:
            self._calendar_verified_at = _aware(
                calendar_verified_at, "live calendar verification time"
            )
        else:
            self._calendar_verified_at = None
        self._tz = ZoneInfo(timezone)
        self._cache: dict[date, tuple[LiveSessionWindow, ...]] = {}
        self._identity = _hash({
            "schema_version": PAPER_LIVE_CAUSAL_CONTEXT_VERSION,
            "product": self._product,
            "session_authority_identity": self._session_authority_identity,
            "calendar_authority_identity": self._calendar_authority_identity,
            "calendar_verified_at": (
                None if self._calendar_verified_at is None else self._calendar_verified_at.isoformat()
            ),
            "trading_calendar": [day.isoformat() for day in self._calendar],
            "night_closed_days": [day.isoformat() for day in sorted(self._night_closed)],
            "session_schedule": self._schedule,
        })

    @property
    def product(self) -> str:
        return self._product

    @property
    def trading_days(self) -> tuple[date, ...]:
        return self._calendar

    @property
    def session_authority_identity(self) -> str:
        return self._session_authority_identity

    @property
    def calendar_authority_identity(self) -> str | None:
        return self._calendar_authority_identity

    @property
    def calendar_verified_at(self) -> datetime | None:
        return self._calendar_verified_at

    @property
    def coverage_start(self) -> date:
        return self._calendar[0]

    @property
    def coverage_end(self) -> date:
        return self._calendar[-1]

    @property
    def identity(self) -> str:
        return self._identity

    def require_current_authority(self, at: datetime) -> None:
        """Fail closed unless an explicit verified calendar covers ``at``."""
        local_day = _aware(at, "live calendar assessment time").astimezone(self._tz).date()
        if self._calendar_authority_identity is None or self._calendar_verified_at is None:
            raise PermissionError("LIVE_CALENDAR_AUTHORITY_UNVERIFIED")
        if self._calendar_verified_at > at:
            raise PermissionError("LIVE_CALENDAR_AUTHORITY_VERIFICATION_IN_FUTURE")
        if not (self.coverage_start <= local_day <= self.coverage_end):
            raise PermissionError("LIVE_CALENDAR_AUTHORITY_OUT_OF_COVERAGE")

    @property
    def timezone(self) -> ZoneInfo:
        return self._tz

    def next_trading_day_after(self, trading_day: date) -> date | None:
        """The next trading day strictly after ``trading_day`` in the calendar."""
        index = self._calendar_index.get(trading_day)
        if index is None:
            raise ValueError(f"live session trading day {trading_day.isoformat()} is outside the calendar")
        if index + 1 >= len(self._calendar):
            return None
        return self._calendar[index + 1]

    def previous_trading_day_before(self, trading_day: date) -> date | None:
        """The previous trading day strictly before ``trading_day`` in the calendar."""
        index = self._calendar_index.get(trading_day)
        if index is None:
            raise ValueError(f"live session trading day {trading_day.isoformat()} is outside the calendar")
        if index == 0:
            return None
        return self._calendar[index - 1]

    def session_windows_for(self, trading_day: date) -> tuple[LiveSessionWindow, ...]:
        cached = self._cache.get(trading_day)
        if cached is not None:
            return cached
        windows = self._build_windows(trading_day)
        self._cache[trading_day] = windows
        return windows

    def _build_windows(self, trading_day: date) -> tuple[LiveSessionWindow, ...]:
        if trading_day not in self._calendar_index:
            raise ValueError(f"live session trading day {trading_day.isoformat()} is outside the calendar")
        governed = governed_windows_for_days(
            product=self._product,
            replay_days=(trading_day,),
            trading_calendar=self._calendar,
            night_closed_days=self._night_closed,
            session_schedule={self._product: self._schedule},
        )
        return tuple(
            LiveSessionWindow(
                trading_day=item.trading_day,
                kind=item.kind,
                ordinal=item.ordinal,
                start=item.start,
                end=item.end,
                session_authority_identity=item.session_authority_identity,
            )
            for item in governed
        )

    def trading_day_at(self, timestamp: datetime) -> date | None:
        """Official trading day containing the timestamp, or None if not governed."""
        local = _aware(timestamp, "live session timestamp").astimezone(self._tz)
        civil = local.date()
        candidates: list[date] = []
        if civil in self._calendar_index:
            candidates.append(civil)
            index = self._calendar_index[civil]
            if index + 1 < len(self._calendar):
                candidates.append(self._calendar[index + 1])
        else:
            for day in self._calendar:
                if day > civil:
                    candidates.append(day)
                    break
        for trading_day in candidates:
            for window in self.session_windows_for(trading_day):
                if window.contains(local):
                    return trading_day
        return None

    def expected_minute_starts_between(
        self, coverage_start: datetime, coverage_end: datetime
    ) -> tuple[datetime, ...]:
        """Every governed 1m bar start in ``[coverage_start, coverage_end)``.

        Enumerated directly from governed windows, so an absent session window
        still yields expected starts. Session breaks produce no expected starts
        and are therefore never filled or bridged.

        The scan bounds are trading-day-aware: a night session of trading day
        ``D`` starts on the previous trading day's evening and ends at ``D 01:00``,
        so ``D`` can be several civil days after ``coverage_end``'s calendar date
        across weekends/holidays. Using the nearest trading days (not civil
        ``+/- 1 day``) guarantees the governing night window is always visited and
        matches the frozen replay index's per-window enumeration.
        """
        start_local = _aware(coverage_start, "live coverage start").astimezone(self._tz)
        end_local = _aware(coverage_end, "live coverage end").astimezone(self._tz)
        if end_local <= start_local:
            raise ValueError("live coverage end must follow its start")
        result: list[datetime] = []
        lower = self._trading_day_at_or_before(start_local.date())
        last_before_end = self._trading_day_at_or_before(end_local.date())
        # A night session of trading day D spans [prev(D) 21:00, D 01:00), so D
        # can be the next trading day after the last trading day at/before the
        # coverage end (weekends/holidays make that more than one civil day).
        upper = None if last_before_end is None else self.next_trading_day_after(last_before_end)
        for day in self._calendar:
            if lower is not None and day < lower:
                continue
            if upper is not None and day > upper:
                break
            for window in self.session_windows_for(day):
                lo = max(window.start, start_local)
                hi = min(window.end, end_local)
                if hi <= lo:
                    continue
                cursor = lo
                while cursor < hi:
                    result.append(cursor)
                    cursor += _ONE_MINUTE
        return tuple(sorted(result))

    def _trading_day_at_or_before(self, civil: date) -> date | None:
        """Last trading day at or before a civil date, if any."""
        selected: date | None = None
        for day in self._calendar:
            if day > civil:
                break
            selected = day
        return selected

    def next_expected_minute_start_after(self, timestamp: datetime) -> datetime | None:
        """Immediately next governed 1m bar start after ``timestamp``, if any."""
        _aware(timestamp, "live next-expected timestamp")
        after = timestamp + _ONE_MINUTE
        horizon = timestamp + timedelta(days=14)
        starts = self.expected_minute_starts_between(after, horizon)
        if not starts:
            return None
        return starts[0]

    def civil_grid_anchor(self, value: datetime) -> datetime:
        """Asia/Shanghai civil 4-hour grid anchor for a timestamp."""
        local = _aware(value, "live grid minute").astimezone(self._tz)
        grid_hour = (local.hour // FOUR_HOUR_CIVIL_GRID_HOURS) * FOUR_HOUR_CIVIL_GRID_HOURS
        return local.replace(hour=grid_hour, minute=0, second=0, microsecond=0)


@dataclass(frozen=True)
class _AdmittedMinute:
    """One accepted closed 1m bar held inside the builder state."""

    trading_day: date
    start: datetime
    end: datetime
    available_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal

    def __post_init__(self) -> None:
        if self.end - self.start != _ONE_MINUTE:
            raise ValueError("live causal substrate must contain exact 1-minute bars")
        _aware(self.start, "minute start")
        _aware(self.end, "minute end")
        _aware(self.available_at, "minute available_at")
        if self.available_at < self.end:
            raise ValueError("admitted minute cannot be available before it closes")
        values = (self.open, self.high, self.low, self.close, self.volume)
        if any(not isinstance(value, Decimal) or not value.is_finite() for value in values):
            raise ValueError("admitted minute OHLCV must be finite Decimal values")
        if min(self.open, self.high, self.low, self.close) <= 0:
            raise ValueError("admitted minute OHLC must be positive")
        if self.volume < 0:
            raise ValueError("admitted minute volume must be non-negative")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close) or self.low > self.high:
            raise ValueError("admitted minute OHLC is inconsistent")


@dataclass(frozen=True)
class LiveCausalBar:
    """One deterministic closed live aggregation bar with attributable provenance."""

    concrete_instrument: str
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
    policy_identity: str
    session_authority_identity: str
    source_minute_starts: tuple[datetime, ...]
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.concrete_instrument, "live bar concrete instrument")
        if self.timeframe not in ACTIVE_TIMEFRAMES:
            raise ValueError(f"unknown live causal timeframe {self.timeframe!r}")
        _aware(self.start, "live bar start")
        _aware(self.end, "live bar end")
        _aware(self.available_at, "live bar available_at")
        if self.end <= self.start:
            raise ValueError("live bar end must follow its start")
        if self.available_at < self.end:
            raise ValueError("closed live bar cannot be available before it closes")
        _require_text(self.policy_identity, "live bar policy identity")
        _require_text(self.session_authority_identity, "live bar session authority identity")
        if not self.source_minute_starts or tuple(sorted(set(self.source_minute_starts))) != self.source_minute_starts:
            raise ValueError("live bar source minutes must be strictly increasing and unique")
        for value, name in (
            (self.open, "open"), (self.high, "high"),
            (self.low, "low"), (self.close, "close"),
        ):
            if not isinstance(value, Decimal) or not value.is_finite() or value <= 0:
                raise ValueError(f"live bar {name} must be a positive finite Decimal")
        if not isinstance(self.volume, Decimal) or not self.volume.is_finite() or self.volume < 0:
            raise ValueError("live bar volume must be a non-negative finite Decimal")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close) or self.low > self.high:
            raise ValueError("live bar OHLC is inconsistent")
        object.__setattr__(self, "identity", _hash({
            "schema_version": PAPER_LIVE_CAUSAL_CONTEXT_VERSION,
            "concrete_instrument": self.concrete_instrument,
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
            "policy_identity": self.policy_identity,
            "session_authority_identity": self.session_authority_identity,
            "source_minute_starts": [item.isoformat() for item in self.source_minute_starts],
        }))

    @property
    def completed_bar(self) -> CompletedBar:
        """CompletedBar view so downstream ``MarketContext``-style consumers can bind it."""
        return CompletedBar(
            instrument=self.concrete_instrument,
            trading_day=self.trading_day,
            start=self.start,
            end=self.end,
            available_at=self.available_at,
            quality=BarQuality(),
        )


@dataclass(frozen=True)
class LiveCausalWake:
    """One newly completed governed 5m wake emitted by the live context builder."""

    bar: LiveCausalBar
    observed_at: datetime
    policy_identity: str
    bar_identity: str = field(init=False)
    logical_wake_selection_identity: str = field(init=False)
    wake_identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.bar.timeframe != "5m":
            raise ValueError("live causal wake bar must be a 5m bar")
        _aware(self.observed_at, "live wake observed_at")
        if self.observed_at < self.bar.available_at:
            raise ValueError("LIVE_WAKE_BEFORE_AVAILABLE")
        object.__setattr__(self, "bar_identity", _hash({
            "schema_version": PAPER_LIVE_CAUSAL_CONTEXT_VERSION,
            "wake_kind": "LIVE_CLOSED_5M",
            "policy_identity": self.policy_identity,
            "trading_day": self.bar.trading_day.isoformat(),
            "start": self.bar.start.isoformat(),
            "end": self.bar.end.isoformat(),
            "source_minute_starts": [item.isoformat() for item in self.bar.source_minute_starts],
        }))
        object.__setattr__(self, "logical_wake_selection_identity", _hash({
            "wake_rule": "COMPLETE_GOVERNED_5M_WAKE",
            "policy_identity": self.policy_identity,
            "bar_identity": self.bar_identity,
        }))
        object.__setattr__(self, "wake_identity", _hash({
            "schema_version": PAPER_LIVE_CAUSAL_CONTEXT_VERSION,
            "bar_identity": self.bar_identity,
            "observed_at": self.observed_at.isoformat(),
        }))

    def to_serializable(self) -> dict[str, object]:
        return {
            "bar": {
                "concrete_instrument": self.bar.concrete_instrument,
                "timeframe": self.bar.timeframe,
                "trading_day": self.bar.trading_day.isoformat(),
                "start": self.bar.start.isoformat(),
                "end": self.bar.end.isoformat(),
                "available_at": self.bar.available_at.isoformat(),
                "open": _decimal_text(self.bar.open),
                "high": _decimal_text(self.bar.high),
                "low": _decimal_text(self.bar.low),
                "close": _decimal_text(self.bar.close),
                "volume": _decimal_text(self.bar.volume),
                "policy_identity": self.bar.policy_identity,
                "session_authority_identity": self.bar.session_authority_identity,
                "source_minute_starts": [item.isoformat() for item in self.bar.source_minute_starts],
            },
            "observed_at": self.observed_at.isoformat(),
            "policy_identity": self.policy_identity,
            "bar_identity": self.bar_identity,
            "logical_wake_selection_identity": self.logical_wake_selection_identity,
            "wake_identity": self.wake_identity,
        }


class LiveCausalContextBuilder:
    """Streaming causal 1m -> 5m/15m/1H/4H builder with bootstrap/restart support.

    The builder is the market/context-layer owner of causal completeness. It
    never touches the wake journal directly; callers use ``admit_wake_to_journal``
    / ``wake_already_journaled`` to bind a durable ``PaperWakeJournal`` seam.
    """

    def __init__(
        self,
        *,
        exchange: str,
        concrete_instrument: str,
        product: str,
        calendar: LiveSessionCalendar,
        policy_identity: str | None = None,
    ) -> None:
        self.exchange = _require_text(exchange, "live context exchange")
        self.concrete_instrument = _require_text(concrete_instrument, "live context concrete instrument")
        self.product = _require_text(product, "live context product")
        if not isinstance(calendar, LiveSessionCalendar):
            raise ValueError("live context requires a LiveSessionCalendar")
        self._calendar = calendar
        if calendar.product != product:
            raise ValueError("live context product disagrees with the session calendar")
        self._policy_identity = (
            policy_identity if policy_identity is not None else paper_live_aggregation_policy_identity()
        )
        if not isinstance(self._policy_identity, str) or not self._policy_identity:
            raise ValueError("live context policy identity must be non-empty")
        self._admitted: dict[datetime, _AdmittedMinute] = {}
        self._last_accepted_start: datetime | None = None
        self._processed_5m_ends: set[datetime] = set()
        self._emitted_5m_ends: set[datetime] = set()
        self._last_emitted_wake_bar_end: datetime | None = None
        self._last_emitted_wake_observed_at: datetime | None = None
        self._bootstrap_done = False

    # ------------------------------------------------------------------ public

    @property
    def calendar(self) -> LiveSessionCalendar:
        return self._calendar

    @property
    def policy_identity(self) -> str:
        return self._policy_identity

    @property
    def last_accepted_minute_start(self) -> datetime | None:
        return self._last_accepted_start

    @property
    def watermark_start(self) -> datetime | None:
        return self._last_accepted_start

    @property
    def accepted_minute_count(self) -> int:
        return len(self._admitted)

    @property
    def bootstrap_done(self) -> bool:
        return self._bootstrap_done

    @property
    def last_emitted_wake(self) -> LiveCausalWake | None:
        if self._last_emitted_wake_bar_end is None or self._last_emitted_wake_observed_at is None:
            return None
        return self._wake_for_bar_end(
            self._last_emitted_wake_bar_end, self._last_emitted_wake_observed_at
        )

    @property
    def emitted_wake_count(self) -> int:
        return len(self._emitted_5m_ends)

    def bootstrap(self, bars: Sequence[object], *, observed_at: datetime) -> None:
        """Absorb a historical closed-bar serial; never emits historical wakes."""
        _aware(observed_at, "bootstrap observed_at")
        if self._admitted:
            raise RuntimeError("LIVE_CAUSAL_ALREADY_BOOTSTRAPPED")
        self._admit_batch(bars, observed_at)
        for bar in self._complete_bars():
            if bar.timeframe == "5m":
                self._processed_5m_ends.add(bar.end)
        self._bootstrap_done = True

    def observe(self, bars: Sequence[object], *, observed_at: datetime) -> tuple[LiveCausalWake, ...]:
        """Admit newly closed 1m bars and emit any newly completed 5m wakes.

        Used for live streaming and reconnect catch-up. Raises and mutates
        nothing on an unexplained governed-minute gap (fail closed).
        """
        _aware(observed_at, "observe observed_at")
        self._admit_batch(bars, observed_at)
        wakes: list[LiveCausalWake] = []
        for bar in self._complete_bars():
            if bar.timeframe != "5m":
                continue
            if bar.end in self._processed_5m_ends:
                continue
            self._processed_5m_ends.add(bar.end)
            self._emitted_5m_ends.add(bar.end)
            wake = LiveCausalWake(
                bar=bar, observed_at=observed_at, policy_identity=self._policy_identity
            )
            wakes.append(wake)
            self._last_emitted_wake_bar_end = bar.end
            self._last_emitted_wake_observed_at = observed_at
        return tuple(wakes)

    def context_for_wake(self, wake: LiveCausalWake) -> tuple[LiveCausalBar, ...]:
        """Bounded causal 4H/1H/15m/5m context for one live wake.

        Fails closed if any active timeframe lacks the required closed window
        count, or if the newest 5m bar is not the wake bar.
        """
        if not isinstance(wake, LiveCausalWake):
            raise TypeError("live context requires a LiveCausalWake")
        available = wake.bar.available_at
        bars = self._complete_bars()

        def visible(timeframe: str) -> tuple[LiveCausalBar, ...]:
            return tuple(
                item
                for item in bars
                if item.timeframe == timeframe
                and item.available_at <= available
                and item.end <= available
            )

        four = visible("4H")[-CONTEXT_WINDOW_COUNTS["4H"]:]
        one = visible("1H")[-CONTEXT_WINDOW_COUNTS["1H"]:]
        fifteen = visible("15m")[-CONTEXT_WINDOW_COUNTS["15m"]:]
        five = visible("5m")[-CONTEXT_WINDOW_COUNTS["5m"]:]
        counts = {"4H": len(four), "1H": len(one), "15m": len(fifteen), "5m": len(five)}
        if any(counts[timeframe] < CONTEXT_WINDOW_COUNTS[timeframe] for timeframe in ACTIVE_TIMEFRAMES):
            raise ValueError(
                "LIVE_CAUSAL_CONTEXT_INSUFFICIENT_HISTORY required="
                f"{CONTEXT_WINDOW_COUNTS} actual={counts}"
            )
        if not five or five[-1].identity != wake.bar.identity:
            raise ValueError("LIVE_CAUSAL_CONTEXT_WAKE_MISMATCH")
        return tuple(list(four) + list(one) + list(fifteen) + list(five[:-1]) + [wake.bar])

    def context_identity(self, context: Sequence[LiveCausalBar]) -> str:
        """Stable identity over a served causal context snapshot."""
        return _hash({
            "schema_version": PAPER_LIVE_CAUSAL_CONTEXT_VERSION,
            "policy_identity": self._policy_identity,
            "bar_identities": [item.identity for item in context],
        })

    def complete_bars(self) -> tuple[LiveCausalBar, ...]:
        """All currently complete closed aggregation bars (deterministic)."""
        return self._complete_bars()

    # ------------------------------------------------------------ checkpoint

    def snapshot(self) -> dict[str, object]:
        """Serializable checkpoint sufficient for deterministic restart."""
        return {
            "schema_version": PAPER_LIVE_CAUSAL_CHECKPOINT_VERSION,
            "exchange": self.exchange,
            "concrete_instrument": self.concrete_instrument,
            "product": self.product,
            "policy_identity": self._policy_identity,
            "session_authority_identity": self._calendar.session_authority_identity,
            "calendar_identity": self._calendar.identity,
            "last_accepted_minute_start": (
                None if self._last_accepted_start is None else self._last_accepted_start.isoformat()
            ),
            "admitted_minutes": [
                self._minute_to_dict(item)
                for item in sorted(self._admitted.values(), key=lambda minute: minute.start)
            ],
            "processed_5m_bar_ends": sorted(end.isoformat() for end in self._processed_5m_ends),
            "emitted_5m_bar_ends": sorted(end.isoformat() for end in self._emitted_5m_ends),
            "last_emitted_wake_bar_end": (
                None if self._last_emitted_wake_bar_end is None else self._last_emitted_wake_bar_end.isoformat()
            ),
            "last_emitted_wake_observed_at": (
                None if self._last_emitted_wake_observed_at is None else self._last_emitted_wake_observed_at.isoformat()
            ),
            "bootstrap_done": self._bootstrap_done,
            "accepted_minute_count": len(self._admitted),
        }

    @classmethod
    def from_checkpoint(
        cls,
        checkpoint: Mapping[str, object],
        *,
        calendar: LiveSessionCalendar,
    ) -> "LiveCausalContextBuilder":
        builder = cls(
            exchange=_require_text(checkpoint.get("exchange"), "checkpoint exchange"),
            concrete_instrument=_require_text(
                checkpoint.get("concrete_instrument"), "checkpoint concrete instrument"
            ),
            product=_require_text(checkpoint.get("product"), "checkpoint product"),
            calendar=calendar,
            policy_identity=_require_text(checkpoint.get("policy_identity"), "checkpoint policy identity"),
        )
        builder._restore(checkpoint)
        return builder

    # -------------------------------------------------------- journal seam

    def wake_already_journaled(self, wake: LiveCausalWake, *, journal: object) -> bool:
        """Idempotency seam: has this 5m bar already been journaled?"""
        has_bar = getattr(journal, "has_bar", None)
        if not callable(has_bar):
            raise ValueError("live wake journal seam requires PaperWakeJournal.has_bar")
        return bool(has_bar(wake.bar_identity))

    def admit_wake_to_journal(
        self,
        wake: LiveCausalWake,
        *,
        journal: object,
        trader_identity: str,
        concrete_contract_id: str,
    ) -> object:
        """Durable journal integration seam (PaperWakeJournal.observe contract).

        Deduplication is delegated to the journal (bar identity is unique). A
        conflicting re-observation raises ``PAPER_WAKE_IDENTITY_CONFLICT`` and is
        never silently swallowed.
        """
        observe = getattr(journal, "observe", None)
        if not callable(observe):
            raise ValueError("live wake journal seam requires PaperWakeJournal.observe")
        return observe(
            wake_identity=wake.wake_identity,
            trader_identity=trader_identity,
            concrete_contract_id=concrete_contract_id,
            bar_identity=wake.bar_identity,
            bar_start=wake.bar.start,
            bar_end=wake.bar.end,
            observed_at=wake.observed_at,
        )

    # ------------------------------------------------------------- internal

    def _admit_batch(self, bars: Sequence[object], observed_at: datetime) -> None:
        prepared: list[_AdmittedMinute] = []
        last = self._last_accepted_start
        prior: datetime | None = None
        batch_minutes: dict[datetime, _AdmittedMinute] = {}
        for bar in bars:
            minute = self._minute_of(bar, observed_at)
            if prior is not None and minute.start < prior:
                raise ValueError("LIVE_CAUSAL_OUT_OF_ORDER")
            prior = minute.start
            existing = self._admitted.get(minute.start)
            if existing is not None:
                if self._minute_equal(existing, minute):
                    continue
                raise ValueError("LIVE_CAUSAL_DUPLICATE_MINUTE_CONFLICT")
            # The batch commits atomically below, so a second delivery of the
            # same start inside this batch is not yet in ``_admitted``; detect
            # it here to keep the fail-closed duplicate signal precise (identical
            # re-delivery is still idempotently deduped, as across calls).
            batch_existing = batch_minutes.get(minute.start)
            if batch_existing is not None:
                if self._minute_equal(batch_existing, minute):
                    continue
                raise ValueError("LIVE_CAUSAL_DUPLICATE_MINUTE_CONFLICT")
            batch_minutes[minute.start] = minute
            if last is not None:
                expected = self._calendar.next_expected_minute_start_after(last)
                if expected is None or minute.start != expected:
                    raise ValueError("LIVE_CAUSAL_MINUTE_GAP")
            prepared.append(minute)
            last = minute.start
        # All validated; commit atomically (fail-closed on any prior error).
        for minute in prepared:
            self._admitted[minute.start] = minute
            self._last_accepted_start = minute.start

    def _minute_of(self, bar: object, observed_at: datetime) -> _AdmittedMinute:
        completed = getattr(bar, "completed_bar", None)
        if not isinstance(completed, CompletedBar):
            raise ValueError("LIVE_CAUSAL_SUBSTRATE_REQUIRES_COMPLETED_BAR")
        if completed.end - completed.start != _ONE_MINUTE:
            raise ValueError("LIVE_CAUSAL_SUBSTRATE_MUST_BE_1M")
        if completed.end > observed_at:
            raise ValueError("LIVE_MINUTE_NOT_CLOSED")
        if completed.available_at > observed_at:
            raise ValueError("LIVE_MINUTE_NOT_YET_CAUSAL")
        instrument = getattr(bar, "concrete_instrument", None) or completed.instrument
        if instrument != self.concrete_instrument:
            raise ValueError("LIVE_CAUSAL_CROSS_CONTRACT")
        trading_day = self._calendar.trading_day_at(completed.start)
        if trading_day is None:
            raise ValueError("LIVE_MINUTE_OUTSIDE_GOVERNED_SESSION")
        if completed.trading_day != trading_day:
            raise ValueError("LIVE_CAUSAL_TRADING_DAY_MISMATCH")
        return _AdmittedMinute(
            trading_day=trading_day,
            start=completed.start,
            end=completed.end,
            available_at=completed.available_at,
            open=_parse_decimal(getattr(bar, "open", None), "open"),
            high=_parse_decimal(getattr(bar, "high", None), "high"),
            low=_parse_decimal(getattr(bar, "low", None), "low"),
            close=_parse_decimal(getattr(bar, "close", None), "close"),
            volume=_parse_decimal(getattr(bar, "volume", None), "volume"),
        )

    @staticmethod
    def _minute_equal(left: _AdmittedMinute, right: _AdmittedMinute) -> bool:
        return (
            left.trading_day == right.trading_day
            and left.start == right.start
            and left.end == right.end
            and left.available_at == right.available_at
            and left.open == right.open
            and left.high == right.high
            and left.low == right.low
            and left.close == right.close
            and left.volume == right.volume
        )

    def _complete_bars(self) -> tuple[LiveCausalBar, ...]:
        if not self._admitted:
            return ()
        by_day: dict[date, list[_AdmittedMinute]] = {}
        for minute in self._admitted.values():
            by_day.setdefault(minute.trading_day, []).append(minute)
        bars: list[LiveCausalBar] = []
        for trading_day in sorted(by_day):
            minutes = by_day[trading_day]
            starts = {minute.start for minute in minutes}
            for window in self._calendar.session_windows_for(trading_day):
                window_minutes = [
                    minute for minute in minutes if window.start <= minute.start < window.end
                ]
                if not window_minutes:
                    continue
                for timeframe, period in LOWER_TIMEFRAME_PERIODS.items():
                    delta = timedelta(minutes=period)
                    offset = timedelta(0)
                    while window.start + offset + delta <= window.end:
                        bucket_start = window.start + offset
                        bucket_end = bucket_start + delta
                        expected = self._calendar.expected_minute_starts_between(bucket_start, bucket_end)
                        if expected and all(item in starts for item in expected):
                            bucket = [
                                minute
                                for minute in window_minutes
                                if bucket_start <= minute.start < bucket_end
                            ]
                            bars.append(
                                self._bar_from_minutes(
                                    timeframe=timeframe,
                                    minutes=bucket,
                                    session_authority_identity=window.session_authority_identity,
                                )
                            )
                        offset += delta
            for grid_start, grid_end in self._civil_grids(trading_day, minutes):
                expected = self._calendar.expected_minute_starts_between(grid_start, grid_end)
                if expected and all(item in starts for item in expected):
                    grid_minutes = [
                        minute for minute in minutes if grid_start <= minute.start < grid_end
                    ]
                    bars.append(
                        self._bar_from_minutes(
                            timeframe="4H",
                            minutes=grid_minutes,
                            session_authority_identity=self._calendar.session_authority_identity,
                        )
                    )
        return tuple(sorted(bars, key=lambda item: (item.timeframe, item.start)))

    def _civil_grids(
        self, trading_day: date, minutes: Sequence[_AdmittedMinute]
    ) -> tuple[tuple[datetime, datetime], ...]:
        grids: set[tuple[datetime, datetime]] = set()
        for minute in minutes:
            anchor = self._calendar.civil_grid_anchor(minute.start)
            grids.add((anchor, anchor + timedelta(hours=FOUR_HOUR_CIVIL_GRID_HOURS)))
        return tuple(sorted(grids))

    def _bar_from_minutes(
        self,
        *,
        timeframe: str,
        minutes: Sequence[_AdmittedMinute],
        session_authority_identity: str,
    ) -> LiveCausalBar:
        ordered = tuple(sorted(minutes, key=lambda minute: minute.start))
        if not ordered:
            raise ValueError(f"{timeframe} bar requires at least one source minute")
        if len({minute.trading_day for minute in ordered}) != 1:
            raise ValueError(f"{timeframe} bar minutes must belong to one trading day")
        start = ordered[0].start
        end = ordered[-1].end
        available_at = max(minute.available_at for minute in ordered)
        return LiveCausalBar(
            concrete_instrument=self.concrete_instrument,
            timeframe=timeframe,
            trading_day=ordered[0].trading_day,
            start=start,
            end=end,
            available_at=available_at,
            open=ordered[0].open,
            high=max(minute.high for minute in ordered),
            low=min(minute.low for minute in ordered),
            close=ordered[-1].close,
            volume=sum((minute.volume for minute in ordered), Decimal(0)),
            policy_identity=self._policy_identity,
            session_authority_identity=session_authority_identity,
            source_minute_starts=tuple(minute.start for minute in ordered),
        )

    def _wake_for_bar_end(self, bar_end: datetime, observed_at: datetime) -> LiveCausalWake:
        for bar in self._complete_bars():
            if bar.timeframe == "5m" and bar.end == bar_end:
                return LiveCausalWake(
                    bar=bar, observed_at=observed_at, policy_identity=self._policy_identity
                )
        raise ValueError("LIVE_CAUSAL_LAST_WAKE_BAR_MISSING_FROM_STATE")

    def _restore(self, checkpoint: Mapping[str, object]) -> None:
        if checkpoint.get("schema_version") != PAPER_LIVE_CAUSAL_CHECKPOINT_VERSION:
            raise ValueError("unsupported live causal checkpoint schema")
        for key, expected in (
            ("exchange", self.exchange),
            ("concrete_instrument", self.concrete_instrument),
            ("product", self.product),
            ("policy_identity", self._policy_identity),
            ("session_authority_identity", self._calendar.session_authority_identity),
            ("calendar_identity", self._calendar.identity),
        ):
            if checkpoint.get(key) != expected:
                raise ValueError(f"live causal checkpoint {key} mismatch")
        admitted_raw = checkpoint.get("admitted_minutes")
        if not isinstance(admitted_raw, list):
            raise ValueError("live causal checkpoint admitted_minutes must be a list")
        admitted: list[_AdmittedMinute] = []
        seen: set[datetime] = set()
        for item in admitted_raw:
            if not isinstance(item, Mapping):
                raise ValueError("live causal checkpoint minute must be a mapping")
            minute = self._minute_from_dict(item)
            if minute.start in seen:
                raise ValueError("live causal checkpoint contains a duplicate minute")
            trading_day = self._calendar.trading_day_at(minute.start)
            if trading_day is None:
                raise ValueError("live causal checkpoint minute is outside governed sessions")
            if minute.trading_day != trading_day:
                raise ValueError("live causal checkpoint minute trading-day mismatch")
            admitted.append(minute)
            seen.add(minute.start)
        admitted.sort(key=lambda minute: minute.start)
        last: datetime | None = None
        for minute in admitted:
            if last is not None:
                expected = self._calendar.next_expected_minute_start_after(last)
                if expected is None or minute.start != expected:
                    raise ValueError("LIVE_CAUSAL_CHECKPOINT_GAP")
            last = minute.start
        checkpoint_last = checkpoint.get("last_accepted_minute_start")
        if (checkpoint_last is None) != (last is None):
            raise ValueError("live causal checkpoint watermark mismatch")
        if checkpoint_last is not None and datetime.fromisoformat(str(checkpoint_last)) != last:
            raise ValueError("live causal checkpoint watermark mismatch")
        self._admitted = {minute.start: minute for minute in admitted}
        self._last_accepted_start = last

        processed_raw = checkpoint.get("processed_5m_bar_ends")
        if not isinstance(processed_raw, list):
            raise ValueError("live causal checkpoint processed_5m_bar_ends must be a list")
        processed: set[datetime] = set()
        for value in processed_raw:
            processed.add(datetime.fromisoformat(str(value)))
        self._processed_5m_ends = processed

        emitted_raw = checkpoint.get("emitted_5m_bar_ends")
        if not isinstance(emitted_raw, list):
            raise ValueError("live causal checkpoint emitted_5m_bar_ends must be a list")
        emitted: set[datetime] = set()
        for value in emitted_raw:
            emitted.add(datetime.fromisoformat(str(value)))
        if not emitted.issubset(processed):
            raise ValueError("live causal checkpoint emitted ends must be a subset of processed ends")
        self._emitted_5m_ends = emitted

        end_raw = checkpoint.get("last_emitted_wake_bar_end")
        observed_raw = checkpoint.get("last_emitted_wake_observed_at")
        if (end_raw is None) != (observed_raw is None):
            raise ValueError("live causal checkpoint last wake fields must be consistent")
        self._last_emitted_wake_bar_end = None if end_raw is None else datetime.fromisoformat(str(end_raw))
        self._last_emitted_wake_observed_at = (
            None if observed_raw is None else datetime.fromisoformat(str(observed_raw))
        )
        if self._last_emitted_wake_bar_end is not None and self._last_emitted_wake_bar_end not in processed:
            raise ValueError("live causal checkpoint last wake is not recorded as processed")
        if self._last_emitted_wake_bar_end is not None and self._last_emitted_wake_bar_end not in emitted:
            raise ValueError("live causal checkpoint last wake is not recorded as emitted")
        self._bootstrap_done = bool(checkpoint.get("bootstrap_done", False))

    @staticmethod
    def _minute_to_dict(minute: _AdmittedMinute) -> dict[str, object]:
        return {
            "trading_day": minute.trading_day.isoformat(),
            "start": minute.start.isoformat(),
            "end": minute.end.isoformat(),
            "available_at": minute.available_at.isoformat(),
            "open": _decimal_text(minute.open),
            "high": _decimal_text(minute.high),
            "low": _decimal_text(minute.low),
            "close": _decimal_text(minute.close),
            "volume": _decimal_text(minute.volume),
        }

    @staticmethod
    def _minute_from_dict(item: Mapping[str, object]) -> _AdmittedMinute:
        return _AdmittedMinute(
            trading_day=date.fromisoformat(str(item["trading_day"])),
            start=datetime.fromisoformat(str(item["start"])),
            end=datetime.fromisoformat(str(item["end"])),
            available_at=datetime.fromisoformat(str(item["available_at"])),
            open=_parse_decimal(item.get("open"), "open"),
            high=_parse_decimal(item.get("high"), "high"),
            low=_parse_decimal(item.get("low"), "low"),
            close=_parse_decimal(item.get("close"), "close"),
            volume=_parse_decimal(item.get("volume"), "volume"),
        )


__all__ = [
    "ACTIVE_TIMEFRAMES",
    "CONTEXT_WINDOW_COUNTS",
    "FOUR_HOUR_AGGREGATION_VERSION",
    "FOUR_HOUR_ROLE",
    "LiveCausalBar",
    "LiveCausalContextBuilder",
    "LiveCausalWake",
    "LiveSessionCalendar",
    "LiveSessionWindow",
    "LOWER_AGGREGATION_VERSION",
    "PAPER_LIVE_AGGREGATION_POLICY_VERSION",
    "PAPER_LIVE_CAUSAL_CHECKPOINT_VERSION",
    "PAPER_LIVE_CAUSAL_CONTEXT_VERSION",
    "paper_live_aggregation_policy_document",
    "paper_live_aggregation_policy_identity",
]

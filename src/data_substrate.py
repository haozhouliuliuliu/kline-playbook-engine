"""Minimum normalized data semantics for Skeleton v1.0.

This module has no exchange connection or strategy logic.  It represents only
the explicit session facts and causal visibility boundaries downstream code
must preserve.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Iterable


@dataclass(frozen=True)
class SessionWindow:
    exchange: str
    instrument: str
    trading_day: date
    start: datetime
    end: datetime
    kind: str

    def __post_init__(self) -> None:
        if not all((self.exchange, self.instrument, self.kind)):
            raise ValueError("session exchange, instrument, and kind are required")
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("session timestamps must be timezone-aware")
        if self.end <= self.start:
            raise ValueError("session end must be after start")

    def contains(self, timestamp: datetime) -> bool:
        if timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return self.start <= timestamp < self.end


class SessionMetadata:
    """Versioned, explicit exchange session facts; no weekday inference."""

    def __init__(self, version: str, windows: Iterable[SessionWindow]) -> None:
        if not version.strip():
            raise ValueError("session metadata version is required")
        self.version = version
        self._windows = tuple(windows)
        # Overlap check is O(n log n) (group by instrument, then adjacent
        # windows in start order) instead of O(n^2); semantically identical:
        # any overlapping pair would appear adjacent to its earliest-starting
        # member in the sorted order.
        by_instrument: dict[tuple[str, str], list[SessionWindow]] = {}
        for window in self._windows:
            by_instrument.setdefault((window.exchange, window.instrument), []).append(window)
        for group in by_instrument.values():
            ordered = sorted(group, key=lambda w: (w.start, w.end))
            for left, right in zip(ordered, ordered[1:]):
                if (
                    left.start < right.end
                    and right.start < left.end
                ):
                    raise ValueError("overlapping session windows are not allowed")

    def trading_day_at(self, exchange: str, instrument: str, timestamp: datetime) -> date | None:
        matches = [
            window
            for window in self._windows
            if window.exchange == exchange and window.instrument == instrument and window.contains(timestamp)
        ]
        if not matches:
            return None
        return matches[0].trading_day

    def window_at(self, exchange: str, instrument: str, timestamp: datetime) -> SessionWindow | None:
        """The explicit session window containing ``timestamp``, or ``None``.

        The metadata is validated to be non-overlapping per instrument, so at
        most one window can contain any timestamp.  Callers that must align
        intraday buckets from the session-window start use this accessor; no
        exchange session is ever inferred from weekday/civil time here.
        """
        if timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        matches = [
            window
            for window in self._windows
            if window.exchange == exchange and window.instrument == instrument and window.contains(timestamp)
        ]
        if not matches:
            return None
        return matches[0]

    def trading_week_at(self, exchange: str, instrument: str, timestamp: datetime) -> tuple[int, int] | None:
        """ISO (year, week) of the official trading day containing the timestamp.

        Weekly attribution is derived from the authoritative trading-day
        identity returned by ``trading_day_at``, never from the raw civil
        timestamp.  A night session that crosses civil midnight is therefore
        attributed to the week of the official trading day it opens for.
        """
        trading_day = self.trading_day_at(exchange, instrument, timestamp)
        if trading_day is None:
            return None
        iso = trading_day.isocalendar()
        return (iso[0], iso[1])

    def expected_bar_starts(
        self, exchange: str, instrument: str, trading_day: date, interval: timedelta
    ) -> tuple[datetime, ...]:
        if interval <= timedelta(0):
            raise ValueError("bar interval must be positive")
        starts: list[datetime] = []
        for window in self._windows:
            if (window.exchange, window.instrument, window.trading_day) != (exchange, instrument, trading_day):
                continue
            start = window.start
            while start + interval <= window.end:
                starts.append(start)
                start += interval
        return tuple(sorted(starts))

    def missing_bar_starts(
        self,
        exchange: str,
        instrument: str,
        trading_day: date,
        interval: timedelta,
        observed_starts: Iterable[datetime],
    ) -> tuple[datetime, ...]:
        expected = set(self.expected_bar_starts(exchange, instrument, trading_day, interval))
        observed = set(observed_starts)
        if any(item.tzinfo is None for item in observed):
            raise ValueError("observed bar timestamps must be timezone-aware")
        unexpected = observed - expected
        if unexpected:
            raise ValueError("observed bar starts outside published sessions")
        return tuple(sorted(expected - observed))


@dataclass(frozen=True)
class BarQuality:
    partial: bool = False
    reconnect_gap: bool = False


@dataclass(frozen=True)
class CompletedBar:
    instrument: str
    trading_day: date
    start: datetime
    end: datetime
    available_at: datetime
    quality: BarQuality = BarQuality()

    def __post_init__(self) -> None:
        if not self.instrument:
            raise ValueError("bar instrument is required")
        if any(item.tzinfo is None for item in (self.start, self.end, self.available_at)):
            raise ValueError("bar timestamps must be timezone-aware")
        if self.end <= self.start:
            raise ValueError("bar end must be after start")
        if self.available_at < self.end:
            raise ValueError("unfinished bar cannot be visible as completed")

    def is_visible_at(self, timestamp: datetime) -> bool:
        if timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return timestamp >= self.available_at

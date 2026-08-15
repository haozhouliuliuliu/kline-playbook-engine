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
        for index, left in enumerate(self._windows):
            for right in self._windows[index + 1 :]:
                if (
                    left.exchange == right.exchange
                    and left.instrument == right.instrument
                    and left.start < right.end
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

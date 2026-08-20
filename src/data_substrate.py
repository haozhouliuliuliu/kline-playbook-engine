"""Minimum normalized data semantics for Skeleton v1.0.

This module has no exchange connection or strategy logic.  It represents only
the explicit session facts and causal visibility boundaries downstream code
must preserve.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from hashlib import sha256
import json
from typing import Any, Iterable


def canonical_hash(value: Any) -> str:
    """Deterministic JSON-stable SHA256 (matches repository identity style)."""
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


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
    """Versioned, explicit exchange session facts; no weekday inference.

    ``version`` is a deterministic content identity computed from the
    ``authority_reference`` and the exact canonical session windows
    ``(exchange, instrument, trading_day, start, end, kind)``.  The same
    caller label with different windows (or different calendar/schedule
    authority facts bound into the reference) can therefore never yield the
    same ``version``.
    """

    def __init__(self, authority_reference: str, windows: Iterable[SessionWindow]) -> None:
        if not authority_reference.strip():
            raise ValueError("session metadata authority reference is required")
        self.authority_reference = authority_reference
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
        self.version = self._content_identity()

    def _content_identity(self) -> str:
        return canonical_hash(
            {
                "authority_reference": self.authority_reference,
                "windows": sorted(
                    (
                        window.exchange,
                        window.instrument,
                        window.trading_day.isoformat(),
                        window.start.isoformat(),
                        window.end.isoformat(),
                        window.kind,
                    )
                    for window in self._windows
                ),
            }
        )

    @property
    def identity(self) -> str:
        """Public identity alias of the computed content ``version``."""
        return self.version

    def trading_day_at(self, exchange: str, instrument: str, timestamp: datetime) -> date | None:
        matches = [
            window
            for window in self._windows
            if window.exchange == exchange and window.instrument == instrument and window.contains(timestamp)
        ]
        if not matches:
            return None
        return matches[0].trading_day

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

    def expected_bar_starts_between(
        self,
        exchange: str,
        instrument: str,
        coverage_start: datetime,
        coverage_end: datetime,
        interval: timedelta,
    ) -> tuple[datetime, ...]:
        """Every expected complete bar start within ``[coverage_start, coverage_end)``.

        Enumerated directly from the authoritative session windows, not from
        any observed bars, so an entirely absent session window that the
        declared coverage claims to cover still yields expected starts.  A bar
        is expected only when its whole ``[start, start + interval)`` span lies
        inside both its session window and the declared coverage range.
        """
        if interval <= timedelta(0):
            raise ValueError("bar interval must be positive")
        if coverage_start.tzinfo is None or coverage_end.tzinfo is None:
            raise ValueError("coverage must be timezone-aware")
        if coverage_end <= coverage_start:
            raise ValueError("coverage end must follow its start")
        starts: list[datetime] = []
        for window in self._windows:
            if (window.exchange, window.instrument) != (exchange, instrument):
                continue
            start = window.start
            while start + interval <= window.end:
                if coverage_start <= start and start + interval <= coverage_end:
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

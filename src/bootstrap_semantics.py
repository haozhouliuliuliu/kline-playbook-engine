"""Minimal deterministic feasibility fixtures for Skeleton v1.0.

This module is deliberately not a production trading engine. It exists only to
verify that the architecture's time/session, broker-event, TradingState, and
Ledger boundaries can be represented without adopting a third-party framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Dict, Iterable, Tuple

from src.data_substrate import SessionMetadata, SessionWindow


class SessionConflict(ValueError):
    """Legacy feasibility-fixture exception.

    Retained only for API compatibility.  Trading-day conflicts now fail
    closed inside ``SessionMetadata`` at construction time (overlapping
    windows are rejected), so no lookup can reach a conflicting state.
    """


@dataclass(frozen=True)
class TradingSession:
    exchange: str
    instrument: str
    trading_day: date
    start: datetime
    end: datetime
    kind: str  # e.g. "continuous" or "day"

    def __post_init__(self) -> None:
        if self.start.tzinfo is None or self.end.tzinfo is None:
            raise ValueError("session timestamps must be timezone-aware")
        if self.end <= self.start:
            raise ValueError("session end must be after start")

    def contains(self, ts: datetime) -> bool:
        if ts.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return self.start <= ts < self.end


class NormalizedSessionCalendar:
    """Explicit point-in-time session mapping; no weekday/night inference.

    This feasibility fixture deliberately delegates trading-day and
    trading-week attribution to the single authoritative ``SessionMetadata``
    semantics in ``src.data_substrate``.  The fixture therefore contains no
    competing trading-day algorithm and can never become a second
    business-logic owner of trading-day determination (TD-001).
    """

    def __init__(self, sessions: Iterable[TradingSession]):
        self._sessions: Tuple[TradingSession, ...] = tuple(sessions)
        windows = tuple(
            SessionWindow(
                session.exchange,
                session.instrument,
                session.trading_day,
                session.start,
                session.end,
                session.kind,
            )
            for session in self._sessions
        )
        # SessionMetadata fails closed on overlapping windows, so one
        # timestamp can never silently map to two different trading days.
        self._metadata = SessionMetadata("bootstrap-feasibility-fixture-v1", windows)

    def trading_day_at(self, exchange: str, instrument: str, ts: datetime) -> date | None:
        return self._metadata.trading_day_at(exchange, instrument, ts)

    def trading_week_at(self, exchange: str, instrument: str, ts: datetime) -> tuple[int, int] | None:
        return self._metadata.trading_week_at(exchange, instrument, ts)


@dataclass(frozen=True)
class BrokerEvent:
    event_id: str
    trading_day: date
    sequence: int
    instrument: str
    quantity_delta: int

    def __post_init__(self) -> None:
        if not self.event_id:
            raise ValueError("event_id is required")
        if self.sequence < 1:
            raise ValueError("sequence must start at 1 within a trading day")


@dataclass(frozen=True)
class PositionTransition:
    event_id: str
    trading_day: date
    sequence: int
    instrument: str
    quantity_before: int
    quantity_after: int


@dataclass(frozen=True)
class IngestResult:
    duplicate: bool
    buffered: bool
    applied: Tuple[PositionTransition, ...]


class EventIdentityConflict(ValueError):
    pass


class SequenceConflict(ValueError):
    pass


class TradingState:
    """Only mutable real-time owner in this feasibility fixture.

    Out-of-order policy: future sequence numbers are buffered until gaps arrive.
    Duplicate event IDs with identical payload are ignored. Conflicting reuse of
    an event ID or sequence fails closed.
    """

    def __init__(self) -> None:
        self._positions: Dict[str, int] = {}
        self._expected_sequence: Dict[date, int] = {}
        self._seen_events: Dict[str, BrokerEvent] = {}
        self._buffered_by_sequence: Dict[tuple[date, int], BrokerEvent] = {}
        self._applied_event_ids: set[str] = set()

    def position(self, instrument: str) -> int:
        return self._positions.get(instrument, 0)

    def last_sequence(self, trading_day: date) -> int:
        return self._expected_sequence.get(trading_day, 1) - 1

    def ingest(self, event: BrokerEvent) -> IngestResult:
        seen = self._seen_events.get(event.event_id)
        if seen is not None:
            if seen != event:
                raise EventIdentityConflict("event_id reused with different payload")
            return IngestResult(duplicate=True, buffered=event.event_id not in self._applied_event_ids, applied=())

        key = (event.trading_day, event.sequence)
        occupied = self._buffered_by_sequence.get(key)
        if occupied is not None and occupied != event:
            raise SequenceConflict("same trading_day/sequence received with different event")

        expected = self._expected_sequence.setdefault(event.trading_day, 1)
        if event.sequence < expected:
            raise SequenceConflict("stale sequence with unseen event_id")

        self._seen_events[event.event_id] = event
        self._buffered_by_sequence[key] = event

        if event.sequence > expected:
            return IngestResult(duplicate=False, buffered=True, applied=())

        applied: list[PositionTransition] = []
        while True:
            next_seq = self._expected_sequence[event.trading_day]
            next_key = (event.trading_day, next_seq)
            next_event = self._buffered_by_sequence.get(next_key)
            if next_event is None:
                break
            before = self.position(next_event.instrument)
            after = before + next_event.quantity_delta
            self._positions[next_event.instrument] = after
            self._applied_event_ids.add(next_event.event_id)
            del self._buffered_by_sequence[next_key]
            applied.append(
                PositionTransition(
                    event_id=next_event.event_id,
                    trading_day=next_event.trading_day,
                    sequence=next_event.sequence,
                    instrument=next_event.instrument,
                    quantity_before=before,
                    quantity_after=after,
                )
            )
            self._expected_sequence[event.trading_day] = next_seq + 1

        return IngestResult(duplicate=False, buffered=False, applied=tuple(applied))


@dataclass(frozen=True)
class LedgerRecord:
    event_id: str
    trading_day: date
    sequence: int
    instrument: str
    quantity_before: int
    quantity_after: int


class Ledger:
    """Append-only factual history; it does not own or mutate TradingState."""

    def __init__(self) -> None:
        self._records: list[LedgerRecord] = []
        self._event_ids: set[str] = set()

    @property
    def records(self) -> Tuple[LedgerRecord, ...]:
        return tuple(self._records)

    def append_transition(self, transition: PositionTransition) -> None:
        if transition.event_id in self._event_ids:
            raise ValueError("ledger duplicate event_id")
        self._records.append(
            LedgerRecord(
                event_id=transition.event_id,
                trading_day=transition.trading_day,
                sequence=transition.sequence,
                instrument=transition.instrument,
                quantity_before=transition.quantity_before,
                quantity_after=transition.quantity_after,
            )
        )
        self._event_ids.add(transition.event_id)

"""Canonical completed round-trip evidence ledger (mandatory generic infrastructure).

This module materializes a canonical completed-trade evidence unit from the
existing authoritative position lifecycle.  It does NOT invent a second position
lifecycle: it consumes the exact ``CapitalTransition`` / ``CapitalSnapshot``
records produced by ``src.validation_runner`` (and consumed by
``src.portfolio_semantics``).

Binding identity rule
---------------------

    ONE position_id  ==  ONE completed round trip

Adds and partial closes are parts of the SAME round trip.  Each partial close
is NOT counted as a separate trade, so downstream sample-size (N) based
statistics are not inflated.

What this module is NOT
-----------------------

- strategy research;
- a candidate backtest;
- statistical inference;
- Playbook semantic design;
- performance ranking logic (no ranking, thresholds, or cross-trade comparison).

Authoritative sources of truth (do not double count)
----------------------------------------------------

- Gross realized PnL      : sum of ``CapitalTransition.realized_pnl_change``
                            over the reducing/closing transitions of the round
                            trip.  Slippage is already embedded in the fill
                            price / realized PnL; it is NOT an additive fee.
- Additive charged costs  : ``CapitalTransition.required_cost`` is the SINGLE
                            authoritative additive-cost path.  Each transition
                            is charged exactly once.  ``ExecutionOutcome.total_cost``
                            (constrained) equals ``required_cost`` for filled
                            outcomes and is used only as a cross-check, never
                            as a second summation source.
- Official trading day    : ``SessionMetadata.trading_day_at`` is the single
                            trusted trading-day authority (TD-001 resolved).
                            Weekly attribution derives from the official
                            trading-day identity, never from the raw civil
                            timestamp.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime
from decimal import Decimal
from hashlib import sha256
import json
from typing import Iterable

from src.contract_semantics import PositionDirection
from src.data_substrate import SessionMetadata
from src.validation_runner import CapitalTransition, ExecutionOutcome, FillStatus


def _round_trip_hash(value: object) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


TERMINAL_REASON_FULL_CLOSE = "FULL_CLOSE"
TERMINAL_REASON_FORCED_LIQUIDATION = "FORCED_LIQUIDATION"


@dataclass(frozen=True)
class CompletedRoundTrip:
    """Immutable canonical record of one completed round trip."""

    position_id: str
    instrument: str
    direction: PositionDirection
    opened_at: datetime
    terminal_closed_at: datetime
    terminal_reason: str
    forced_liquidation: bool
    opening_transition_references: tuple[str, ...]
    reducing_transition_references: tuple[str, ...]
    source_transition_references: tuple[str, ...]
    source_outcome_references: tuple[str, ...]
    total_opened_quantity: Decimal
    total_closed_quantity: Decimal
    average_open_price: Decimal
    gross_realized_pnl: Decimal
    charged_costs: Decimal
    entry_official_trading_day: date
    exit_official_trading_day: date
    entry_official_trading_week: tuple[int, int]
    exit_official_trading_week: tuple[int, int]
    active_official_trading_days: tuple[date, ...]
    ledger_identity: str
    concrete_contract_id: str | None = None

    def __post_init__(self) -> None:
        if not self.position_id or not self.instrument:
            raise ValueError("a completed round trip requires position_id and instrument")
        if not isinstance(self.direction, PositionDirection):
            raise ValueError("round trip direction must be an explicit position direction")
        if self.opened_at.tzinfo is None or self.terminal_closed_at.tzinfo is None:
            raise ValueError("round trip timestamps must be timezone-aware")
        if self.terminal_closed_at < self.opened_at:
            raise ValueError("terminal close cannot precede the opening")
        if self.terminal_reason not in {TERMINAL_REASON_FULL_CLOSE, TERMINAL_REASON_FORCED_LIQUIDATION}:
            raise ValueError("unsupported terminal reason")
        if self.forced_liquidation != (self.terminal_reason == TERMINAL_REASON_FORCED_LIQUIDATION):
            raise ValueError("forced_liquidation flag must agree with the terminal reason")
        quantity_values = (self.total_opened_quantity, self.total_closed_quantity)
        if any(type(value) is not Decimal or value <= 0 for value in quantity_values):
            raise ValueError("round trip opened/closed quantities must be positive Decimals")
        if self.total_closed_quantity != self.total_opened_quantity:
            raise ValueError("a completed round trip must have a balanced opened/closed quantity identity")
        if type(self.average_open_price) is not Decimal or self.average_open_price <= 0:
            raise ValueError("round trip average open price must be a positive Decimal")
        if type(self.gross_realized_pnl) is not Decimal or type(self.charged_costs) is not Decimal:
            raise ValueError("round trip PnL and cost values must be Decimals")
        if self.charged_costs < 0:
            raise ValueError("round trip charged costs cannot be negative")
        if not self.entry_official_trading_day or not self.exit_official_trading_day:
            raise ValueError("round trip requires official entry and exit trading days")
        if not self.entry_official_trading_week or not self.exit_official_trading_week:
            raise ValueError("round trip requires official entry and exit trading weeks")
        if not all(day for day in self.active_official_trading_days):
            raise ValueError("round trip active trading days cannot contain empty identities")
        if len(self.ledger_identity) != 64:
            raise ValueError("round trip ledger identity must be a sha256 hex digest")

    @property
    def net_realized_result(self) -> Decimal:
        """Net realized result directly derivable from authoritative fields.

        ``gross_realized_pnl`` is fill-price gross (slippage already embedded);
        ``charged_costs`` is the additive cost charged exactly once.  The net
        realized result is their difference and is NOT a new authority.
        """
        return self.gross_realized_pnl - self.charged_costs

    @property
    def source_references(self) -> tuple[str, ...]:
        return self.source_transition_references + self.source_outcome_references


@dataclass(frozen=True)
class RoundTripLedger:
    """Immutable container of completed round trips for a position stream."""

    completed_round_trips: tuple[CompletedRoundTrip, ...] = ()
    open_position_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.completed_round_trips, tuple) or not isinstance(self.open_position_ids, tuple):
            raise ValueError("round-trip ledger requires tuples")
        if len({trip.position_id for trip in self.completed_round_trips}) != len(self.completed_round_trips):
            raise ValueError("one position_id can produce at most one completed round trip")
        completed_ids = {trip.position_id for trip in self.completed_round_trips}
        if completed_ids.intersection(self.open_position_ids):
            raise ValueError("a position_id cannot be both completed and still open")
        ordered_ids = tuple(trip.position_id for trip in self.completed_round_trips)
        if tuple(sorted(ordered_ids)) != ordered_ids:
            raise ValueError("completed round trips must be ordered by position_id")

    @property
    def completed_count(self) -> int:
        return len(self.completed_round_trips)

    def round_trips_for(self, position_id: str) -> tuple[CompletedRoundTrip, ...]:
        return tuple(trip for trip in self.completed_round_trips if trip.position_id == position_id)

    @property
    def identity_id(self) -> str:
        return _round_trip_hash(
            {
                "completed": [trip.ledger_identity for trip in self.completed_round_trips],
                "open_position_ids": self.open_position_ids,
            }
        )


class _RoundTripAccumulator:
    """Internal grouping state for one position_id (implementation detail)."""

    __slots__ = (
        "position_id",
        "instrument",
        "direction",
        "concrete_contract_id",
        "open_transition",
        "terminal_transition",
        "opening_refs",
        "reducing_refs",
        "source_transition_refs",
        "source_outcome_refs",
        "total_opened",
        "total_closed",
        "gross_realized",
        "charged_costs",
        "transition_official_days",
        "completed",
    )

    def __init__(self, position_id: str) -> None:
        self.position_id = position_id
        self.instrument: str | None = None
        self.direction: PositionDirection | None = None
        self.concrete_contract_id: str | None = None
        self.open_transition: CapitalTransition | None = None
        self.terminal_transition: CapitalTransition | None = None
        self.opening_refs: list[str] = []
        self.reducing_refs: list[str] = []
        self.source_transition_refs: list[str] = []
        self.source_outcome_refs: list[str] = []
        self.total_opened = Decimal("0")
        self.total_closed = Decimal("0")
        self.gross_realized = Decimal("0")
        self.charged_costs = Decimal("0")
        self.transition_official_days: set[date] = set()
        self.completed = False

    @property
    def is_completed(self) -> bool:
        return self.completed


class RoundTripMaterializer:
    """Materializes completed round trips from authoritative capital transitions.

    Parameters
    ----------
    session_metadata:
        Optional ``SessionMetadata`` used as the single trusted official
        trading-day/week authority (TD-001).  When provided together with
        ``exchange``, every lifecycle timestamp is mapped through
        ``trading_day_at`` / ``trading_week_at`` and must agree with the
        snapshot's ``position_trading_day``; timestamps outside a published
        session window fail closed instead of guessing.
    exchange:
        Required together with ``session_metadata``; used to resolve windows.
    """

    def __init__(
        self,
        session_metadata: SessionMetadata | None = None,
        exchange: str | None = None,
    ) -> None:
        if (session_metadata is None) != (exchange is None):
            raise ValueError("session metadata and exchange must be provided together")
        self._session_metadata = session_metadata
        self._exchange = exchange

    # -- public API ---------------------------------------------------------

    def materialize(
        self,
        capital_transitions: Iterable[CapitalTransition],
        execution_outcomes: Iterable[ExecutionOutcome] = (),
    ) -> RoundTripLedger:
        """Group authoritative transitions by ``position_id`` into round trips.

        Incomplete (still-open) positions are returned in
        ``RoundTripLedger.open_position_ids`` and are NOT materialized as
        completed round trips.
        """
        ordered = tuple(capital_transitions)
        outcomes_by_request = {outcome.request_id: outcome for outcome in execution_outcomes}
        self._validate_lifecycle_order(ordered)
        accumulators: dict[str, _RoundTripAccumulator] = {}
        completed: list[CompletedRoundTrip] = []
        completed_position_ids: set[str] = set()

        for transition in ordered:
            position_id = self._position_id_of(transition)
            if position_id is None:
                self._validate_flat_noop(transition)
                continue
            if position_id in completed_position_ids:
                raise ValueError(
                    "a position_id cannot start a second round trip after completion "
                    "(ONE position_id == ONE completed round trip)"
                )
            accumulator = accumulators.get(position_id)
            if accumulator is None:
                accumulator = self._begin(transition, position_id)
                accumulators[position_id] = accumulator
            else:
                self._continuation_guard(transition, accumulator)
            self._apply_transition(transition, outcomes_by_request, accumulator)
            if accumulator.is_completed:
                completed.append(self._finalize(accumulator))
                completed_position_ids.add(position_id)
                del accumulators[position_id]

        open_ids = tuple(sorted(accumulators))
        completed_sorted = tuple(sorted(completed, key=lambda trip: trip.position_id))
        return RoundTripLedger(completed_round_trips=completed_sorted, open_position_ids=open_ids)

    # -- private helpers ----------------------------------------------------

    @staticmethod
    def _position_id_of(transition: CapitalTransition) -> str | None:
        return transition.after.position_id or transition.before.position_id

    @staticmethod
    def _state_at(transition: CapitalTransition) -> datetime | None:
        if transition.after.state_at is not None:
            return transition.after.state_at
        return transition.before.state_at

    @staticmethod
    def _validate_lifecycle_order(ordered: tuple[CapitalTransition, ...]) -> None:
        previous: datetime | None = None
        for transition in ordered:
            state_at = RoundTripMaterializer._state_at(transition)
            if state_at is None:
                continue
            if previous is not None and state_at < previous:
                raise ValueError("round-trip transitions must be in lifecycle (chronological) order")
            previous = state_at

    @staticmethod
    def _validate_flat_noop(transition: CapitalTransition) -> None:
        # A transition with no position identity must be a no-op on a flat
        # state: it cannot charge cost, realize PnL, or change quantity.
        if transition.quantity_change != 0 or transition.required_cost != 0 or transition.realized_pnl_change != 0:
            raise ValueError("a flat no-op transition cannot carry quantity, cost, or realized PnL changes")

    def _begin(self, transition: CapitalTransition, position_id: str) -> _RoundTripAccumulator:
        if transition.before.position_quantity != 0 or transition.quantity_change <= 0:
            raise ValueError("a new position_id must begin with an OPEN from a flat state")
        instrument = transition.after.position_instrument or transition.before.position_instrument
        direction = transition.after.position_direction or transition.before.position_direction
        if not instrument or not isinstance(direction, PositionDirection):
            raise ValueError("an OPEN transition must carry instrument and direction identity")
        accumulator = _RoundTripAccumulator(position_id)
        accumulator.instrument = instrument
        accumulator.direction = direction
        accumulator.concrete_contract_id = transition.after.concrete_contract_id or transition.before.concrete_contract_id
        accumulator.open_transition = transition
        return accumulator

    @staticmethod
    def _continuation_guard(transition: CapitalTransition, accumulator: _RoundTripAccumulator) -> None:
        if transition.after.position_id is not None and transition.after.position_id != accumulator.position_id:
            raise ValueError("a transition cannot move between position identities")
        before_instrument = transition.before.position_instrument or transition.after.position_instrument
        if before_instrument != accumulator.instrument:
            raise ValueError("a round trip cannot silently merge unrelated contract positions")
        after_instrument = transition.after.position_instrument
        if after_instrument is not None and after_instrument != accumulator.instrument:
            raise ValueError("a round trip cannot silently merge unrelated contract positions")
        before_direction = transition.before.position_direction or transition.after.position_direction
        if before_direction is not accumulator.direction:
            raise ValueError("a round trip cannot change direction")
        after_direction = transition.after.position_direction
        if after_direction is not None and after_direction is not accumulator.direction:
            raise ValueError("a round trip cannot change direction")
        if transition.transition_type == "FORCED_LIQUIDATION" and transition.quantity_change > 0:
            raise ValueError("forced liquidation cannot increase a position")

    def _apply_transition(
        self,
        transition: CapitalTransition,
        outcomes_by_request: dict[str, ExecutionOutcome],
        accumulator: _RoundTripAccumulator,
    ) -> None:
        accumulator.source_transition_refs.append(transition.reference_id)
        outcome = outcomes_by_request.get(transition.request_id)
        if outcome is not None:
            accumulator.source_outcome_refs.append(outcome.reference_id)
        self._cross_check_cost(transition, outcome)
        official_day, _ = self._official_day_week(transition)
        accumulator.transition_official_days.add(official_day)

        if transition.quantity_change > 0:
            accumulator.total_opened += transition.quantity_change
            accumulator.charged_costs += transition.required_cost
            accumulator.opening_refs.append(transition.reference_id)
            return
        if transition.quantity_change < 0:
            accumulator.total_closed += -transition.quantity_change
            accumulator.gross_realized += transition.realized_pnl_change
            accumulator.charged_costs += transition.required_cost
            accumulator.reducing_refs.append(transition.reference_id)
            if transition.after.position_quantity == 0:
                if accumulator.total_closed != accumulator.total_opened:
                    raise ValueError("a completed round trip must have a balanced quantity identity")
                if transition.transition_type not in {"POSITION_CLOSE", "FORCED_LIQUIDATION"}:
                    raise ValueError("a terminal close must be a POSITION_CLOSE or FORCED_LIQUIDATION transition")
                accumulator.terminal_transition = transition
                accumulator.completed = True
            return
        # quantity_change == 0: lifecycle no-op (e.g. an order that did not
        # fill while a position remained open).  It adds no quantity, PnL, or
        # cost, but is retained in the source references and official days.
        if transition.required_cost != 0 or transition.realized_pnl_change != 0:
            raise ValueError("a no-op round-trip transition cannot charge cost or realize PnL")

    @staticmethod
    def _cross_check_cost(transition: CapitalTransition, outcome: ExecutionOutcome | None) -> None:
        if outcome is None or outcome.status is not FillStatus.FILLED or outcome.total_cost is None:
            return
        if outcome.total_cost != transition.required_cost:
            raise ValueError(
                "execution outcome total_cost must agree with the single additive-cost "
                "authority CapitalTransition.required_cost"
            )

    def _official_day_week(self, transition: CapitalTransition) -> tuple[date, tuple[int, int]]:
        instrument = transition.after.position_instrument or transition.before.position_instrument
        timestamp = self._state_at(transition)
        snapshot_day = (
            transition.after.position_trading_day or transition.before.position_trading_day
        )
        if self._session_metadata is not None:
            if timestamp is None or instrument is None or self._exchange is None:
                raise ValueError("session-based official trading day requires a timestamp and instrument")
            day = self._session_metadata.trading_day_at(self._exchange, instrument, timestamp)
            if day is None:
                raise ValueError(
                    "official trading day cannot be derived from published session windows; "
                    "fail closed instead of guessing a missing day"
                )
            if snapshot_day is not None and day != snapshot_day:
                raise ValueError("SessionMetadata trading day is inconsistent with the snapshot trading day")
            week = self._session_metadata.trading_week_at(self._exchange, instrument, timestamp)
            if week is None:
                raise ValueError(
                    "official trading week cannot be derived from published session windows; "
                    "fail closed instead of guessing a missing week"
                )
            return day, week
        if snapshot_day is None:
            raise ValueError(
                "official trading day is not derivable without SessionMetadata and snapshot identity; "
                "fail closed instead of guessing"
            )
        iso = snapshot_day.isocalendar()
        return snapshot_day, (iso[0], iso[1])

    def _finalize(self, accumulator: _RoundTripAccumulator) -> CompletedRoundTrip:
        if accumulator.open_transition is None or accumulator.terminal_transition is None:
            raise ValueError("a completed round trip requires an OPEN and a terminal close transition")
        entry_day, entry_week = self._official_day_week(accumulator.open_transition)
        exit_day, exit_week = self._official_day_week(accumulator.terminal_transition)
        terminal_transition = accumulator.terminal_transition
        forced = terminal_transition.transition_type == "FORCED_LIQUIDATION"
        terminal_reason = TERMINAL_REASON_FORCED_LIQUIDATION if forced else TERMINAL_REASON_FULL_CLOSE
        terminal_closed_at = self._state_at(terminal_transition)
        opened_at = self._state_at(accumulator.open_transition)
        if terminal_closed_at is None or opened_at is None:
            raise ValueError("a completed round trip requires open and terminal timestamps")
        average_open_price = terminal_transition.before.average_open_price
        ordered_refs = tuple(accumulator.source_transition_refs)
        ordered_outcome_refs = tuple(accumulator.source_outcome_refs)
        identity_input = {
            "position_id": accumulator.position_id,
            "terminal_reason": terminal_reason,
            "forced_liquidation": forced,
            "ordered_transition_references": ordered_refs,
            "ordered_outcome_references": ordered_outcome_refs,
        }
        return CompletedRoundTrip(
            position_id=accumulator.position_id,
            instrument=accumulator.instrument,
            direction=accumulator.direction,
            opened_at=opened_at,
            terminal_closed_at=terminal_closed_at,
            terminal_reason=terminal_reason,
            forced_liquidation=forced,
            opening_transition_references=tuple(accumulator.opening_refs),
            reducing_transition_references=tuple(accumulator.reducing_refs),
            source_transition_references=ordered_refs,
            source_outcome_references=ordered_outcome_refs,
            total_opened_quantity=accumulator.total_opened,
            total_closed_quantity=accumulator.total_closed,
            average_open_price=average_open_price,
            gross_realized_pnl=accumulator.gross_realized,
            charged_costs=accumulator.charged_costs,
            entry_official_trading_day=entry_day,
            exit_official_trading_day=exit_day,
            entry_official_trading_week=entry_week,
            exit_official_trading_week=exit_week,
            active_official_trading_days=tuple(sorted(accumulator.transition_official_days)),
            ledger_identity=_round_trip_hash(identity_input),
            concrete_contract_id=accumulator.concrete_contract_id,
        )

"""Generic versioned stop-trigger observation layer (Lane H).

This module converts a RESTING STOP ORDER plus future completed OHLC bars into
an existing-compatible ``ExecutionObservation``.  It is deliberately generic:
entry stops and protective exit stops share the exact same trigger mechanism,
and it makes NO candidate-specific decisions (no swing-low identification, no
trailing-stop movement, no profit-target logic, no Holy Grail logic).

What this module is NOT
-----------------------

- candidate strategy logic;
- trailing-stop strategy design;
- a backtest;
- outcome inspection;
- a second capital/position lifecycle;
- a second cost authority;
- a second price-limit authority.

Existing pipeline ownership (do not duplicate)
----------------------------------------------

- ``OrderSpecification`` / ``ExecutionObservation`` / ``ExecutionOutcome`` /
  ``CapitalTransition`` / position lifecycle: ``src.validation_runner``.
- Contract resolution, minimum tick, price-limit facts, session metadata:
  ``src.contract_semantics`` and ``src.data_substrate``.
- Slippage and fee: ``ExecutionAssumptions.synthetic_slippage`` /
  ``synthetic_fee`` applied downstream in the runner.  This module never adds
  slippage; the deterministic reference price from this layer is what enters
  the existing slippage layer exactly once.

Trigger model (ENGINEERING EXECUTION ASSUMPTION, versioned)
-----------------------------------------------------------

``STOP_MARKET_TRIGGER_MODEL_V0_1`` records a deterministic STOP-MARKET bar rule.
It is a machine/engineering convention, NOT a human-source semantic claim.

Point-in-time activation
------------------------

A stop order may only evaluate bars occurring AFTER it became active.  Bars
already completed/known before ``active_at`` can never trigger the stop.

- ``bar.end <= active_at``            -> bar already finished before activation
                                         -> NOT ELIGIBLE (skipped).
- ``active_at < bar.start``           -> order strictly active before the bar's
                                         trigger interval -> ELIGIBLE.
- ``bar.start <= active_at < bar.end``-> order became active INSIDE this bar.
                                         If the threshold was crossed somewhere
                                         in the bar, OHLC alone cannot establish
                                         whether it was crossed before or after
                                         activation -> FAIL CLOSED with
                                         ``AMBIGUOUS_INTRABAR_SEQUENCE``.
                                         If the threshold was never crossed, the
                                         stop could not have triggered in the
                                         bar at any point -> no ambiguity, and
                                         evaluation continues.

Reference price rule (STOP-MARKET, gap-through explicit)
--------------------------------------------------------

BUY_STOP:
  - if bar.open >= stop_price: reference execution price = bar.open
  - elif bar.high >= stop_price: reference execution price = stop_price
  - else: no trigger
SELL_STOP:
  - if bar.open <= stop_price: reference execution price = bar.open
  - elif bar.low <= stop_price: reference execution price = stop_price
  - else: no trigger

No intrabar tick sequence is fabricated.  OHLC does not identify the exact
intrabar path, so the trigger evidence preserves bar start / end / available_at,
trigger side, stop level, reference execution price, and sequence certainty, and
never invents an exact intra-minute timestamp.

OCO / bracket group ambiguity
-----------------------------

If two resting stops in the same OCO/bracket group both trigger inside the same
minimum-resolution bar and there is no finer path, this layer FAILS CLOSED with
``AMBIGUOUS_INTRABAR_SEQUENCE`` instead of arbitrarily choosing one.  It does
not implement one-cancels-other cancellation semantics; it only detects the
same-bar ambiguity that makes the group outcome unknowable.

Higher-timeframe strategies
---------------------------

The project owns 1-minute bars.  A future 30m/60m strategy should use the
underlying 1-minute path for stop triggering when that path is available.  This
module consumes generic ordered ``NormalizedHistoricalBar`` inputs (1-minute or
otherwise) and remains independently usable without any higher-timeframe
aggregation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Iterable

from src.contract_semantics import ContractSpecification
from src.historical_data import NormalizedHistoricalBar
from src.validation_runner import ExecutionObservation


# Versioned machine/engineering STOP-MARKET bar rule (not human-source semantics).
STOP_MARKET_TRIGGER_MODEL_V0_1 = "STOP_MARKET_TRIGGER_MODEL_V0_1"


class StopSide(str, Enum):
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"


class StopTriggerOutcome(str, Enum):
    TRIGGERED = "TRIGGERED"
    NOT_TRIGGERED = "NOT_TRIGGERED"
    AMBIGUOUS_INTRABAR_SEQUENCE = "AMBIGUOUS_INTRABAR_SEQUENCE"


class SequenceCertainty(str, Enum):
    UNAMBIGUOUS = "UNAMBIGUOUS"
    AMBIGUOUS_INTRABAR_SEQUENCE = "AMBIGUOUS_INTRABAR_SEQUENCE"


def _stop_trigger_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RestingStopOrder:
    """An explicitly specified resting stop order with point-in-time activation."""

    request_id: str
    side: StopSide
    stop_price: Decimal
    active_at: datetime
    trigger_model_version: str
    instrument: str
    concrete_contract_id: str | None = None
    oco_group_id: str | None = None

    def __post_init__(self) -> None:
        if not self.request_id or not self.instrument or not self.trigger_model_version:
            raise ValueError("stop order requires request_id, instrument, and trigger model version")
        if not isinstance(self.side, StopSide):
            raise ValueError("stop order side must be an explicit stop side")
        if type(self.stop_price) is not Decimal or self.stop_price <= 0:
            raise ValueError("stop price must be a positive Decimal")
        if self.active_at.tzinfo is None:
            raise ValueError("stop order active_at must be timezone-aware")

    @property
    def bound_instrument(self) -> str:
        """The concrete instrument space this order is bound to."""
        return self.concrete_contract_id if self.concrete_contract_id is not None else self.instrument

    @property
    def identity_id(self) -> str:
        return _stop_trigger_hash(
            {
                "request_id": self.request_id,
                "side": self.side.value,
                "stop_price": str(self.stop_price),
                "active_at": self.active_at.isoformat(),
                "trigger_model_version": self.trigger_model_version,
                "instrument": self.instrument,
                "concrete_contract_id": self.concrete_contract_id,
                "oco_group_id": self.oco_group_id,
            }
        )


@dataclass(frozen=True)
class StopTriggerResult:
    """Deterministic result of evaluating one resting stop against eligible bars."""

    request_id: str
    side: StopSide
    stop_price: Decimal
    trigger_model_version: str
    outcome: StopTriggerOutcome
    sequence_certainty: SequenceCertainty
    instrument: str
    concrete_contract_id: str | None = None
    bar_start: datetime | None = None
    bar_end: datetime | None = None
    bar_available_at: datetime | None = None
    reference_execution_price: Decimal | None = None
    oco_group_id: str | None = None
    ambiguity_with: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.request_id or not self.instrument or not self.trigger_model_version:
            raise ValueError("stop trigger result requires identity and model version")
        if not isinstance(self.side, StopSide):
            raise ValueError("stop trigger result side must be an explicit stop side")
        if not isinstance(self.outcome, StopTriggerOutcome):
            raise ValueError("stop trigger result outcome must be an explicit outcome")
        if not isinstance(self.sequence_certainty, SequenceCertainty):
            raise ValueError("stop trigger result certainty must be explicit")
        if type(self.stop_price) is not Decimal or self.stop_price <= 0:
            raise ValueError("stop trigger result requires a positive Decimal stop price")
        if self.outcome is StopTriggerOutcome.TRIGGERED:
            if self.sequence_certainty is not SequenceCertainty.UNAMBIGUOUS:
                raise ValueError("a triggered stop must have unambiguous sequence certainty")
            if type(self.reference_execution_price) is not Decimal or self.reference_execution_price <= 0:
                raise ValueError("a triggered stop requires a positive reference execution price")
            if self.bar_start is None or self.bar_end is None or self.bar_available_at is None:
                raise ValueError("a triggered stop requires the triggering bar identity")
        elif self.outcome is StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE:
            if self.sequence_certainty is not SequenceCertainty.AMBIGUOUS_INTRABAR_SEQUENCE:
                raise ValueError("an ambiguous stop must have ambiguous sequence certainty")
            if self.reference_execution_price is not None:
                raise ValueError("an ambiguous stop cannot claim a reference execution price")
            if self.bar_start is None or self.bar_end is None or self.bar_available_at is None:
                raise ValueError("an ambiguous stop requires the ambiguous bar identity")
        else:
            if self.sequence_certainty is not SequenceCertainty.UNAMBIGUOUS:
                raise ValueError("a non-triggered stop without ambiguity must be unambiguous")
            if self.reference_execution_price is not None:
                raise ValueError("a non-triggered stop cannot claim a reference execution price")
        if self.ambiguity_with and self.outcome is not StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE:
            raise ValueError("ambiguity references are only valid on an ambiguous result")
        if any(item.tzinfo is None for item in (self.bar_start, self.bar_end, self.bar_available_at) if item is not None):
            raise ValueError("trigger bar timestamps must be timezone-aware")
        if (
            self.bar_start is not None
            and self.bar_end is not None
            and (self.bar_end <= self.bar_start or (self.bar_available_at is not None and self.bar_available_at < self.bar_end))
        ):
            raise ValueError("trigger bar timestamps are inconsistent")

    @property
    def identity_id(self) -> str:
        return _stop_trigger_hash(
            {
                "request_id": self.request_id,
                "side": self.side.value,
                "stop_price": str(self.stop_price),
                "trigger_model_version": self.trigger_model_version,
                "outcome": self.outcome.value,
                "sequence_certainty": self.sequence_certainty.value,
                "instrument": self.instrument,
                "concrete_contract_id": self.concrete_contract_id,
                "bar_start": self.bar_start.isoformat() if self.bar_start else None,
                "bar_end": self.bar_end.isoformat() if self.bar_end else None,
                "bar_available_at": self.bar_available_at.isoformat() if self.bar_available_at else None,
                "reference_execution_price": (
                    str(self.reference_execution_price) if self.reference_execution_price is not None else None
                ),
                "oco_group_id": self.oco_group_id,
                "ambiguity_with": sorted(self.ambiguity_with),
            }
        )


def _validate_ordered_bars(bars: tuple[NormalizedHistoricalBar, ...]) -> None:
    starts = tuple(bar.completed_bar.start for bar in bars)
    if any(left >= right for left, right in zip(starts, starts[1:])):
        raise ValueError("stop trigger bars must be strictly ordered by start")


def _validate_order_bars_binding(order: RestingStopOrder, bars: tuple[NormalizedHistoricalBar, ...]) -> None:
    bound = order.bound_instrument
    for bar in bars:
        if bar.concrete_instrument != bound:
            raise ValueError("stop order instrument disagrees with the supplied bar sequence")


def _validate_order_contract_binding(order: RestingStopOrder, contract: ContractSpecification) -> None:
    if contract.instrument_id != order.bound_instrument:
        raise ValueError("stop order contract binding disagrees with supplied contract metadata")
    if not contract.is_on_tick(order.stop_price):
        raise ValueError(
            f"off-tick stop price {order.stop_price} rejected for minimum tick {contract.minimum_price_tick}"
        )


def _bar_eligibility(order: RestingStopOrder, bar: NormalizedHistoricalBar) -> str:
    """Classify one bar: NOT_ELIGIBLE / ELIGIBLE / NO_TRIGGER_STRADDLING /
    AMBIGUOUS_INTRABAR_SEQUENCE.

    A bar that straddles ``active_at`` only fails closed when the threshold was
    actually crossed somewhere inside the bar (``high >= stop`` for BUY_STOP,
    ``low <= stop`` for SELL_STOP).  If the threshold was never crossed, the
    stop could not have triggered in that bar at any point, so there is no
    ambiguity and evaluation may continue.
    """
    active_at = order.active_at
    start = bar.completed_bar.start
    if bar.completed_bar.end <= active_at:
        return "NOT_ELIGIBLE"
    if active_at < start:
        return "ELIGIBLE"
    if active_at == start:
        # Activation exactly at the bar's trigger-interval start: the open
        # print is coincident with activation.  If the OPEN crossed the
        # threshold we cannot establish whether the order was already resting
        # before the open print -> fail closed.  Otherwise any later high/low
        # crossing is strictly after activation and is a genuine trigger.
        open_crossed = (
            (order.side is StopSide.BUY_STOP and bar.open >= order.stop_price)
            or (order.side is StopSide.SELL_STOP and bar.open <= order.stop_price)
        )
        if open_crossed:
            return "AMBIGUOUS_INTRABAR_SEQUENCE"
        return "ELIGIBLE"
    crossed = (
        (order.side is StopSide.BUY_STOP and bar.high >= order.stop_price)
        or (order.side is StopSide.SELL_STOP and bar.low <= order.stop_price)
    )
    if crossed:
        return "AMBIGUOUS_INTRABAR_SEQUENCE"
    return "NO_TRIGGER_STRADDLING"


def _reference_execution_price(order: RestingStopOrder, bar: NormalizedHistoricalBar) -> Decimal | None:
    """STOP_MARKET_TRIGGER_MODEL_V0_1 gap-through reference price for an eligible bar."""
    if order.side is StopSide.BUY_STOP:
        if bar.open >= order.stop_price:
            return bar.open
        if bar.high >= order.stop_price:
            return order.stop_price
        return None
    if bar.open <= order.stop_price:
        return bar.open
    if bar.low <= order.stop_price:
        return order.stop_price
    return None


def _result_for_bar(
    order: RestingStopOrder,
    bar: NormalizedHistoricalBar,
    outcome: StopTriggerOutcome,
    reference_price: Decimal | None,
    ambiguity_with: tuple[str, ...] = (),
) -> StopTriggerResult:
    certainty = (
        SequenceCertainty.AMBIGUOUS_INTRABAR_SEQUENCE
        if outcome is StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE
        else SequenceCertainty.UNAMBIGUOUS
    )
    return StopTriggerResult(
        request_id=order.request_id,
        side=order.side,
        stop_price=order.stop_price,
        trigger_model_version=order.trigger_model_version,
        outcome=outcome,
        sequence_certainty=certainty,
        instrument=order.instrument,
        concrete_contract_id=order.concrete_contract_id,
        bar_start=bar.completed_bar.start,
        bar_end=bar.completed_bar.end,
        bar_available_at=bar.completed_bar.available_at,
        reference_execution_price=reference_price,
        oco_group_id=order.oco_group_id,
        ambiguity_with=ambiguity_with,
    )


def evaluate_stop_order(
    order: RestingStopOrder,
    bars: Iterable[NormalizedHistoricalBar],
    *,
    contract: ContractSpecification | None = None,
    cutoff_at: datetime | None = None,
) -> StopTriggerResult:
    """Evaluate one resting stop against an ordered sequence of completed bars.

    The first eligible trigger wins.  Bars are only evaluated after the order
    became active; a bar that straddles ``active_at`` fails closed with
    ``AMBIGUOUS_INTRABAR_SEQUENCE``.  When ``cutoff_at`` is provided, bars not
    yet available by that time are not visible and cannot trigger.
    """
    if cutoff_at is not None and cutoff_at.tzinfo is None:
        raise ValueError("stop trigger cutoff must be timezone-aware")
    if contract is not None:
        _validate_order_contract_binding(order, contract)
    ordered_bars = tuple(bars)
    _validate_ordered_bars(ordered_bars)
    _validate_order_bars_binding(order, ordered_bars)
    if cutoff_at is not None:
        ordered_bars = tuple(bar for bar in ordered_bars if bar.completed_bar.available_at <= cutoff_at)

    last_eligible: NormalizedHistoricalBar | None = None
    for bar in ordered_bars:
        eligibility = _bar_eligibility(order, bar)
        if eligibility in ("NOT_ELIGIBLE", "NO_TRIGGER_STRADDLING"):
            continue
        if eligibility == "AMBIGUOUS_INTRABAR_SEQUENCE":
            return _result_for_bar(order, bar, StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE, None)
        last_eligible = bar
        reference_price = _reference_execution_price(order, bar)
        if reference_price is not None:
            return _result_for_bar(order, bar, StopTriggerOutcome.TRIGGERED, reference_price)

    if last_eligible is not None:
        return _result_for_bar(order, last_eligible, StopTriggerOutcome.NOT_TRIGGERED, None)
    return StopTriggerResult(
        request_id=order.request_id,
        side=order.side,
        stop_price=order.stop_price,
        trigger_model_version=order.trigger_model_version,
        outcome=StopTriggerOutcome.NOT_TRIGGERED,
        sequence_certainty=SequenceCertainty.UNAMBIGUOUS,
        instrument=order.instrument,
        concrete_contract_id=order.concrete_contract_id,
        oco_group_id=order.oco_group_id,
    )


def _ambiguous_result_for(triggered: StopTriggerResult, ambiguity_with: tuple[str, ...]) -> StopTriggerResult:
    return StopTriggerResult(
        request_id=triggered.request_id,
        side=triggered.side,
        stop_price=triggered.stop_price,
        trigger_model_version=triggered.trigger_model_version,
        outcome=StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE,
        sequence_certainty=SequenceCertainty.AMBIGUOUS_INTRABAR_SEQUENCE,
        instrument=triggered.instrument,
        concrete_contract_id=triggered.concrete_contract_id,
        bar_start=triggered.bar_start,
        bar_end=triggered.bar_end,
        bar_available_at=triggered.bar_available_at,
        reference_execution_price=None,
        oco_group_id=triggered.oco_group_id,
        ambiguity_with=ambiguity_with,
    )


def evaluate_stop_group(
    orders: Iterable[RestingStopOrder],
    bars: Iterable[NormalizedHistoricalBar],
    *,
    contract: ContractSpecification | None = None,
    cutoff_at: datetime | None = None,
) -> tuple[StopTriggerResult, ...]:
    """Evaluate a set of resting stops, failing closed on same-bar OCO ambiguity.

    When all orders share a non-None ``oco_group_id``, if two or more orders in
    the group trigger inside the same minimum-resolution bar, those triggers
    (and any trigger at or after that bar) are returned as
    ``AMBIGUOUS_INTRABAR_SEQUENCE`` instead of arbitrarily choosing one.
    Orders with no ``oco_group_id`` are evaluated independently with no
    cross-order ambiguity.
    """
    ordered_orders = tuple(orders)
    if not ordered_orders:
        raise ValueError("stop group evaluation requires at least one resting stop order")
    group_ids = {order.oco_group_id for order in ordered_orders}
    if len(group_ids) > 1:
        raise ValueError("a stop group evaluation cannot mix different oco/bracket group identities")
    results = tuple(
        evaluate_stop_order(order, bars, contract=contract, cutoff_at=cutoff_at) for order in ordered_orders
    )
    group_id = next(iter(group_ids))
    if group_id is None:
        return results

    by_bar: dict[datetime, list[tuple[StopTriggerResult, int]]] = {}
    for index, result in enumerate(results):
        if result.outcome is StopTriggerOutcome.TRIGGERED and result.bar_start is not None:
            by_bar.setdefault(result.bar_start, []).append((result, index))
    conflict_bar = None
    for bar_start in sorted(by_bar):
        if len(by_bar[bar_start]) >= 2:
            conflict_bar = bar_start
            break
    if conflict_bar is None:
        return results

    conflict_ids = tuple(result.request_id for result, _ in by_bar[conflict_bar])
    final = list(results)
    for index, result in enumerate(results):
        if (
            result.outcome is StopTriggerOutcome.TRIGGERED
            and result.bar_start is not None
            and result.bar_start >= conflict_bar
        ):
            final[index] = _ambiguous_result_for(result, conflict_ids)
    return tuple(final)


def stop_trigger_result_to_execution_observation(result: StopTriggerResult) -> ExecutionObservation:
    """Bridge an unambiguous trigger into the existing ``ExecutionObservation``.

    The observation carries the authoritative bar availability timestamp and the
    deterministic reference execution price.  Slippage and cost are NOT applied
    here; ``ExecutionAssumptions.synthetic_slippage`` / ``synthetic_fee`` remain
    the downstream runner's single authority (no double slippage / no double
    cost).
    """
    if result.outcome is not StopTriggerOutcome.TRIGGERED:
        raise ValueError("only an unambiguous trigger converts to an execution observation")
    if result.bar_available_at is None or result.reference_execution_price is None:
        raise ValueError("a triggered result requires availability and reference price")
    return ExecutionObservation(
        request_id=result.request_id,
        observed_at=result.bar_available_at,
        available_at=result.bar_available_at,
        price=result.reference_execution_price,
        tradable=True,
        concrete_contract_id=result.concrete_contract_id,
    )

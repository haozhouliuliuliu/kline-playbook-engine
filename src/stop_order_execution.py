"""Deterministic completed-bar stop triggering with minimal OCO lifecycle.

The executed model observes evidence only when a completed bar is available.
It never claims exchange-resting intrabar chronology and does not select this
generic engineering model as Holy Grail PRIMARY semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from pathlib import Path
from typing import Iterable

from src.contract_semantics import ContractSpecification
from src.historical_data import NormalizedHistoricalBar
from src.strategy_evidence import ArtifactBinding
from src.validation_runner import ExecutionObservation


SUPPORTED_TRIGGER_MODEL_VERSION = "COMPLETED_BAR_STOP_TRIGGER_V0_2"
COMPLETED_BAR_AVAILABILITY_CONSERVATIVE = "COMPLETED_BAR_AVAILABILITY_CONSERVATIVE"
STOP_TRIGGER_SCHEMA_VERSION = "stop-trigger-execution-v0.2"


def _canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


STOP_TRIGGER_IMPLEMENTATION_BINDING = ArtifactBinding.from_file(
    artifact_kind="code",
    artifact_reference="src/stop_order_execution.py",
    path=str(Path(__file__).resolve()),
    declared_version=STOP_TRIGGER_SCHEMA_VERSION,
)


class StopSide(str, Enum):
    BUY_STOP = "BUY_STOP"
    SELL_STOP = "SELL_STOP"


class StopTriggerOutcome(str, Enum):
    TRIGGERED = "TRIGGERED"
    NOT_TRIGGERED = "NOT_TRIGGERED"
    AMBIGUOUS_INTRABAR_SEQUENCE = "AMBIGUOUS_INTRABAR_SEQUENCE"
    CANCELLED = "CANCELLED"


class SequenceCertainty(str, Enum):
    UNAMBIGUOUS = "UNAMBIGUOUS"
    AMBIGUOUS_INTRABAR_SEQUENCE = "AMBIGUOUS_INTRABAR_SEQUENCE"


def _sequence_identity(bar_identities: tuple[str, ...]) -> str:
    identity = _canonical_hash({"evaluated_sequence": "ROOT"})
    for bar_identity in bar_identities:
        identity = _canonical_hash(
            {
                "previous_evaluated_sequence_identity": identity,
                "bar_identity": bar_identity,
            }
        )
    return identity


@dataclass(frozen=True)
class RestingStopOrder:
    request_id: str
    side: StopSide
    stop_price: Decimal
    active_at: datetime
    trigger_model_version: str
    instrument: str
    concrete_contract_id: str | None = None
    oco_group_id: str | None = None

    def __post_init__(self) -> None:
        if not self.request_id or not self.instrument:
            raise ValueError("stop order requires request_id and instrument")
        if not isinstance(self.side, StopSide):
            raise ValueError("stop order side must be explicit")
        if type(self.stop_price) is not Decimal or not self.stop_price.is_finite() or self.stop_price <= 0:
            raise ValueError("stop price must be a positive finite Decimal")
        if self.active_at.tzinfo is None:
            raise ValueError("stop order activation must be timezone-aware")
        if self.trigger_model_version != SUPPORTED_TRIGGER_MODEL_VERSION:
            raise ValueError("trigger model version does not match the executed implementation")

    @property
    def bound_instrument(self) -> str:
        return self.concrete_contract_id or self.instrument

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "request_id": self.request_id,
                "side": self.side.value,
                "stop_price": str(self.stop_price),
                "active_at": self.active_at.isoformat(),
                "trigger_model_version": self.trigger_model_version,
                "trigger_model_artifact_identity": STOP_TRIGGER_IMPLEMENTATION_BINDING.identity_id,
                "observation_model": COMPLETED_BAR_AVAILABILITY_CONSERVATIVE,
                "instrument": self.instrument,
                "concrete_contract_id": self.concrete_contract_id,
                "oco_group_id": self.oco_group_id,
            }
        )


@dataclass(frozen=True)
class StopTriggerResult:
    request_id: str
    order_identity: str
    side: StopSide
    stop_price: Decimal
    trigger_model_version: str
    trigger_model_artifact_identity: str
    observation_model: str
    exchange_resting_chronology_claimed: bool
    outcome: StopTriggerOutcome
    sequence_certainty: SequenceCertainty
    instrument: str
    concrete_contract_id: str | None
    oco_group_id: str | None
    evaluated_bar_identities: tuple[str, ...]
    evaluated_sequence_identity: str
    triggering_bar_identity: str | None = None
    bar_start: datetime | None = None
    bar_end: datetime | None = None
    bar_available_at: datetime | None = None
    reference_execution_price: Decimal | None = None
    ambiguity_with: tuple[str, ...] = ()
    cancelled_by_request_id: str | None = None
    cancellation_evidence_identity: str | None = None

    def __post_init__(self) -> None:
        if self.trigger_model_version != SUPPORTED_TRIGGER_MODEL_VERSION:
            raise ValueError("result trigger model version is not the executed model")
        if self.trigger_model_artifact_identity != STOP_TRIGGER_IMPLEMENTATION_BINDING.identity_id:
            raise ValueError("result must bind the actual stop implementation artifact")
        if self.observation_model != COMPLETED_BAR_AVAILABILITY_CONSERVATIVE:
            raise ValueError("unsupported stop observation model")
        if self.exchange_resting_chronology_claimed:
            raise ValueError("completed-bar evidence cannot claim exchange-resting chronology")
        if self.evaluated_sequence_identity != _sequence_identity(self.evaluated_bar_identities):
            raise ValueError("evaluated stop sequence identity is inconsistent")
        if self.outcome is StopTriggerOutcome.TRIGGERED:
            if self.sequence_certainty is not SequenceCertainty.UNAMBIGUOUS:
                raise ValueError("triggered stop must be unambiguous")
            if self.triggering_bar_identity is None or self.triggering_bar_identity not in self.evaluated_bar_identities:
                raise ValueError("triggered stop must bind its triggering bar")
            if type(self.reference_execution_price) is not Decimal or self.reference_execution_price <= 0:
                raise ValueError("triggered stop requires a positive reference price")
        elif self.outcome is StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE:
            if self.sequence_certainty is not SequenceCertainty.AMBIGUOUS_INTRABAR_SEQUENCE:
                raise ValueError("ambiguous result must preserve ambiguity")
            if self.triggering_bar_identity is None or self.reference_execution_price is not None:
                raise ValueError("ambiguous result must bind a bar without claiming a price")
        elif self.outcome is StopTriggerOutcome.CANCELLED:
            if not self.cancelled_by_request_id or not self.cancellation_evidence_identity:
                raise ValueError("cancelled result requires cancellation evidence")
            if self.reference_execution_price is not None:
                raise ValueError("cancelled result cannot claim an execution price")
        else:
            if self.reference_execution_price is not None or self.triggering_bar_identity is not None:
                raise ValueError("not-triggered result cannot claim trigger evidence")
        if self.outcome is not StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE and self.ambiguity_with:
            raise ValueError("ambiguity references require an ambiguous result")
        timestamps = tuple(
            item for item in (self.bar_start, self.bar_end, self.bar_available_at) if item is not None
        )
        if any(item.tzinfo is None for item in timestamps):
            raise ValueError("stop result timestamps must be timezone-aware")
        if self.bar_start is not None and self.bar_end is not None:
            if self.bar_end <= self.bar_start or (
                self.bar_available_at is not None and self.bar_available_at < self.bar_end
            ):
                raise ValueError("stop result bar chronology is invalid")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "request_id": self.request_id,
                "order_identity": self.order_identity,
                "side": self.side.value,
                "stop_price": str(self.stop_price),
                "trigger_model_version": self.trigger_model_version,
                "trigger_model_artifact_identity": self.trigger_model_artifact_identity,
                "observation_model": self.observation_model,
                "exchange_resting_chronology_claimed": self.exchange_resting_chronology_claimed,
                "outcome": self.outcome.value,
                "sequence_certainty": self.sequence_certainty.value,
                "instrument": self.instrument,
                "concrete_contract_id": self.concrete_contract_id,
                "oco_group_id": self.oco_group_id,
                "evaluated_bar_identities": self.evaluated_bar_identities,
                "evaluated_sequence_identity": self.evaluated_sequence_identity,
                "triggering_bar_identity": self.triggering_bar_identity,
                "bar_start": None if self.bar_start is None else self.bar_start.isoformat(),
                "bar_end": None if self.bar_end is None else self.bar_end.isoformat(),
                "bar_available_at": None if self.bar_available_at is None else self.bar_available_at.isoformat(),
                "reference_execution_price": (
                    None if self.reference_execution_price is None else str(self.reference_execution_price)
                ),
                "ambiguity_with": self.ambiguity_with,
                "cancelled_by_request_id": self.cancelled_by_request_id,
                "cancellation_evidence_identity": self.cancellation_evidence_identity,
            }
        )


@dataclass(frozen=True)
class CancellationEvidence:
    oco_group_id: str
    cancelled_request_id: str
    cancelled_order_identity: str
    cancelled_by_request_id: str
    triggering_result_identity: str
    cancelled_at: datetime
    evaluated_sequence_identity: str

    def __post_init__(self) -> None:
        if not all(
            (
                self.oco_group_id,
                self.cancelled_request_id,
                self.cancelled_order_identity,
                self.cancelled_by_request_id,
                self.triggering_result_identity,
                self.evaluated_sequence_identity,
            )
        ):
            raise ValueError("cancellation evidence requires complete identities")
        if self.cancelled_at.tzinfo is None:
            raise ValueError("cancellation time must be timezone-aware")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "oco_group_id": self.oco_group_id,
                "cancelled_request_id": self.cancelled_request_id,
                "cancelled_order_identity": self.cancelled_order_identity,
                "cancelled_by_request_id": self.cancelled_by_request_id,
                "triggering_result_identity": self.triggering_result_identity,
                "cancelled_at": self.cancelled_at.isoformat(),
                "evaluated_sequence_identity": self.evaluated_sequence_identity,
            }
        )


@dataclass(frozen=True)
class StopGroupResult:
    results: tuple[StopTriggerResult, ...]
    cancellation_evidence: tuple[CancellationEvidence, ...]
    evaluated_bar_identities: tuple[str, ...]
    evaluated_sequence_identity: str
    trigger_model_artifact_identity: str

    def __post_init__(self) -> None:
        if not self.results:
            raise ValueError("stop group result requires member results")
        request_ids = tuple(item.request_id for item in self.results)
        if len(request_ids) != len(set(request_ids)):
            raise ValueError("stop group result request ids must be unique")
        if self.evaluated_sequence_identity != _sequence_identity(self.evaluated_bar_identities):
            raise ValueError("stop group evaluated sequence identity is inconsistent")
        if self.trigger_model_artifact_identity != STOP_TRIGGER_IMPLEMENTATION_BINDING.identity_id:
            raise ValueError("stop group must bind actual implementation bytes")
        evidence_ids = {item.identity_id for item in self.cancellation_evidence}
        if any(
            result.outcome is StopTriggerOutcome.CANCELLED
            and result.cancellation_evidence_identity not in evidence_ids
            for result in self.results
        ):
            raise ValueError("cancelled group member is missing cancellation evidence")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "results": [item.identity_id for item in self.results],
                "cancellation_evidence": [item.identity_id for item in self.cancellation_evidence],
                "evaluated_bar_identities": self.evaluated_bar_identities,
                "evaluated_sequence_identity": self.evaluated_sequence_identity,
                "trigger_model_artifact_identity": self.trigger_model_artifact_identity,
            }
        )


def _validate_ordered_bars(bars: tuple[NormalizedHistoricalBar, ...]) -> None:
    if any(not isinstance(item, NormalizedHistoricalBar) for item in bars):
        raise ValueError("stop evaluation requires NormalizedHistoricalBar values")
    starts = tuple(item.completed_bar.start for item in bars)
    if any(left >= right for left, right in zip(starts, starts[1:])):
        raise ValueError("stop trigger bars must be strictly ordered by start")
    if len(starts) != len(set(starts)):
        raise ValueError("stop trigger bars must not contain duplicate starts")


def _validate_order_binding(
    order: RestingStopOrder,
    bars: tuple[NormalizedHistoricalBar, ...],
    contract: ContractSpecification | None,
) -> None:
    if any(item.concrete_instrument != order.bound_instrument for item in bars):
        raise ValueError("stop order instrument disagrees with its evaluated bar sequence")
    if contract is not None:
        if contract.instrument_id != order.bound_instrument:
            raise ValueError("stop order contract binding disagrees with contract metadata")
        if not contract.is_on_tick(order.stop_price):
            raise ValueError("stop price is off the governed minimum price tick")


def _bar_event(
    order: RestingStopOrder, bar: NormalizedHistoricalBar
) -> tuple[str, Decimal | None]:
    start = bar.completed_bar.start
    end = bar.completed_bar.end
    crossed = (
        bar.high >= order.stop_price
        if order.side is StopSide.BUY_STOP
        else bar.low <= order.stop_price
    )
    if end <= order.active_at:
        return "NONE", None
    if start < order.active_at < end:
        return ("AMBIGUOUS", None) if crossed else ("NONE", None)
    if order.active_at == start:
        open_crossed = (
            bar.open >= order.stop_price
            if order.side is StopSide.BUY_STOP
            else bar.open <= order.stop_price
        )
        if open_crossed:
            return "AMBIGUOUS", None
    if order.active_at > start:
        return "NONE", None
    if order.side is StopSide.BUY_STOP:
        if bar.open >= order.stop_price:
            return "TRIGGER", bar.open
        if bar.high >= order.stop_price:
            return "TRIGGER", order.stop_price
    else:
        if bar.open <= order.stop_price:
            return "TRIGGER", bar.open
        if bar.low <= order.stop_price:
            return "TRIGGER", order.stop_price
    return "NONE", None


def _make_result(
    order: RestingStopOrder,
    *,
    outcome: StopTriggerOutcome,
    evaluated_bar_identities: tuple[str, ...],
    bar: NormalizedHistoricalBar | None = None,
    reference_price: Decimal | None = None,
    ambiguity_with: tuple[str, ...] = (),
    cancelled_by_request_id: str | None = None,
    cancellation_evidence_identity: str | None = None,
) -> StopTriggerResult:
    ambiguous = outcome is StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE
    return StopTriggerResult(
        request_id=order.request_id,
        order_identity=order.identity_id,
        side=order.side,
        stop_price=order.stop_price,
        trigger_model_version=SUPPORTED_TRIGGER_MODEL_VERSION,
        trigger_model_artifact_identity=STOP_TRIGGER_IMPLEMENTATION_BINDING.identity_id,
        observation_model=COMPLETED_BAR_AVAILABILITY_CONSERVATIVE,
        exchange_resting_chronology_claimed=False,
        outcome=outcome,
        sequence_certainty=(
            SequenceCertainty.AMBIGUOUS_INTRABAR_SEQUENCE
            if ambiguous
            else SequenceCertainty.UNAMBIGUOUS
        ),
        instrument=order.instrument,
        concrete_contract_id=order.concrete_contract_id,
        oco_group_id=order.oco_group_id,
        evaluated_bar_identities=evaluated_bar_identities,
        evaluated_sequence_identity=_sequence_identity(evaluated_bar_identities),
        triggering_bar_identity=(bar.identity_id if bar is not None and outcome in (
            StopTriggerOutcome.TRIGGERED,
            StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE,
        ) else None),
        bar_start=None if bar is None else bar.completed_bar.start,
        bar_end=None if bar is None else bar.completed_bar.end,
        bar_available_at=None if bar is None else bar.completed_bar.available_at,
        reference_execution_price=reference_price,
        ambiguity_with=tuple(sorted(set(ambiguity_with))),
        cancelled_by_request_id=cancelled_by_request_id,
        cancellation_evidence_identity=cancellation_evidence_identity,
    )


def _visible_bars(
    bars: tuple[NormalizedHistoricalBar, ...], cutoff_at: datetime | None
) -> tuple[NormalizedHistoricalBar, ...]:
    if cutoff_at is not None and cutoff_at.tzinfo is None:
        raise ValueError("stop trigger cutoff must be timezone-aware")
    if cutoff_at is None:
        return bars
    return tuple(item for item in bars if item.completed_bar.available_at <= cutoff_at)


def _evaluate_materialized_order(
    order: RestingStopOrder,
    bars: tuple[NormalizedHistoricalBar, ...],
) -> StopTriggerResult:
    evaluated: list[str] = []
    for item in bars:
        evaluated.append(item.identity_id)
        event, price = _bar_event(order, item)
        prefix = tuple(evaluated)
        if event == "AMBIGUOUS":
            return _make_result(
                order,
                outcome=StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE,
                evaluated_bar_identities=prefix,
                bar=item,
                ambiguity_with=(order.request_id,),
            )
        if event == "TRIGGER":
            return _make_result(
                order,
                outcome=StopTriggerOutcome.TRIGGERED,
                evaluated_bar_identities=prefix,
                bar=item,
                reference_price=price,
            )
    return _make_result(
        order,
        outcome=StopTriggerOutcome.NOT_TRIGGERED,
        evaluated_bar_identities=tuple(evaluated),
    )


def evaluate_stop_order(
    order: RestingStopOrder,
    bars: Iterable[NormalizedHistoricalBar],
    *,
    contract: ContractSpecification | None = None,
    cutoff_at: datetime | None = None,
) -> StopTriggerResult:
    if not isinstance(order, RestingStopOrder):
        raise ValueError("stop evaluation requires a RestingStopOrder")
    materialized = tuple(bars)
    _validate_ordered_bars(materialized)
    _validate_order_binding(order, materialized, contract)
    return _evaluate_materialized_order(order, _visible_bars(materialized, cutoff_at))


def evaluate_stop_group(
    orders: Iterable[RestingStopOrder],
    bars: Iterable[NormalizedHistoricalBar],
    *,
    contract: ContractSpecification | None = None,
    cutoff_at: datetime | None = None,
) -> StopGroupResult:
    ordered_orders = tuple(orders)
    if not ordered_orders or any(not isinstance(item, RestingStopOrder) for item in ordered_orders):
        raise ValueError("stop group requires resting stop orders")
    request_ids = tuple(item.request_id for item in ordered_orders)
    if len(request_ids) != len(set(request_ids)):
        raise ValueError("stop group request ids must be unique")
    group_ids = {item.oco_group_id for item in ordered_orders}
    if len(group_ids) != 1:
        raise ValueError("stop group cannot mix OCO group identities")

    # L-13: materialize and validate the bar iterable exactly once. Every member
    # receives the same immutable ordered tuple.
    materialized = tuple(bars)
    _validate_ordered_bars(materialized)
    for item in ordered_orders:
        _validate_order_binding(item, materialized, contract)
    visible = _visible_bars(materialized, cutoff_at)
    group_id = next(iter(group_ids))

    if group_id is None:
        results = tuple(_evaluate_materialized_order(item, visible) for item in ordered_orders)
        evaluated_ids = tuple(item.identity_id for item in visible)
        return StopGroupResult(
            results=results,
            cancellation_evidence=(),
            evaluated_bar_identities=evaluated_ids,
            evaluated_sequence_identity=_sequence_identity(evaluated_ids),
            trigger_model_artifact_identity=STOP_TRIGGER_IMPLEMENTATION_BINDING.identity_id,
        )

    evaluated: list[str] = []
    for bar in visible:
        evaluated.append(bar.identity_id)
        prefix = tuple(evaluated)
        events: list[tuple[RestingStopOrder, str, Decimal | None]] = []
        for item in ordered_orders:
            event, price = _bar_event(item, bar)
            if event != "NONE":
                events.append((item, event, price))
        if not events:
            continue

        touched_ids = tuple(sorted(item.request_id for item, _, _ in events))
        if len(events) > 1 or any(event == "AMBIGUOUS" for _, event, _ in events):
            results = tuple(
                _make_result(
                    item,
                    outcome=StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE,
                    evaluated_bar_identities=prefix,
                    bar=bar,
                    ambiguity_with=touched_ids,
                )
                for item in ordered_orders
            )
            return StopGroupResult(
                results=results,
                cancellation_evidence=(),
                evaluated_bar_identities=prefix,
                evaluated_sequence_identity=_sequence_identity(prefix),
                trigger_model_artifact_identity=STOP_TRIGGER_IMPLEMENTATION_BINDING.identity_id,
            )

        winner, _, price = events[0]
        winner_result = _make_result(
            winner,
            outcome=StopTriggerOutcome.TRIGGERED,
            evaluated_bar_identities=prefix,
            bar=bar,
            reference_price=price,
        )
        cancellations: list[CancellationEvidence] = []
        results_by_request = {winner.request_id: winner_result}
        for sibling in ordered_orders:
            if sibling.request_id == winner.request_id:
                continue
            evidence = CancellationEvidence(
                oco_group_id=group_id,
                cancelled_request_id=sibling.request_id,
                cancelled_order_identity=sibling.identity_id,
                cancelled_by_request_id=winner.request_id,
                triggering_result_identity=winner_result.identity_id,
                cancelled_at=bar.completed_bar.available_at,
                evaluated_sequence_identity=_sequence_identity(prefix),
            )
            cancellations.append(evidence)
            results_by_request[sibling.request_id] = _make_result(
                sibling,
                outcome=StopTriggerOutcome.CANCELLED,
                evaluated_bar_identities=prefix,
                bar=bar,
                cancelled_by_request_id=winner.request_id,
                cancellation_evidence_identity=evidence.identity_id,
            )
        results = tuple(results_by_request[item.request_id] for item in ordered_orders)
        return StopGroupResult(
            results=results,
            cancellation_evidence=tuple(cancellations),
            evaluated_bar_identities=prefix,
            evaluated_sequence_identity=_sequence_identity(prefix),
            trigger_model_artifact_identity=STOP_TRIGGER_IMPLEMENTATION_BINDING.identity_id,
        )

    evaluated_ids = tuple(evaluated)
    results = tuple(
        _make_result(
            item,
            outcome=StopTriggerOutcome.NOT_TRIGGERED,
            evaluated_bar_identities=evaluated_ids,
        )
        for item in ordered_orders
    )
    return StopGroupResult(
        results=results,
        cancellation_evidence=(),
        evaluated_bar_identities=evaluated_ids,
        evaluated_sequence_identity=_sequence_identity(evaluated_ids),
        trigger_model_artifact_identity=STOP_TRIGGER_IMPLEMENTATION_BINDING.identity_id,
    )


def stop_trigger_result_to_execution_observation(
    result: StopTriggerResult,
) -> ExecutionObservation:
    if result.outcome is not StopTriggerOutcome.TRIGGERED:
        raise ValueError("only an unambiguous trigger can become an execution observation")
    if result.bar_available_at is None or result.reference_execution_price is None:
        raise ValueError("trigger result lacks completed-bar availability evidence")
    if result.observation_model != COMPLETED_BAR_AVAILABILITY_CONSERVATIVE:
        raise ValueError("unsupported trigger chronology")
    return ExecutionObservation(
        request_id=result.request_id,
        observed_at=result.bar_available_at,
        available_at=result.bar_available_at,
        price=result.reference_execution_price,
        tradable=True,
        concrete_contract_id=result.concrete_contract_id,
    )

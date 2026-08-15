"""Minimum deterministic validation connection semantics for Skeleton v1.0."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json
from typing import Iterable

from src.data_substrate import CompletedBar
from src.strategy_evidence import (
    DatasetClass,
    EvidenceLedger,
    EvidenceRecord,
    ExperimentIdentity,
    FinalUnseenFirewall,
    StrategyIdentity,
)


class ChronologyError(ValueError):
    pass


class ValidationMode(str, Enum):
    FAST = "FAST"
    CONFIRMATORY = "CONFIRMATORY"


class ValidationDisposition(str, Enum):
    REJECTED = "REJECTED"
    CONFIRMED = "CONFIRMED"


class FillStatus(str, Enum):
    FILLED = "FILLED"
    NOT_FILLED = "NOT_FILLED"


@dataclass(frozen=True)
class OrderSpecification:
    request_id: str
    quantity: Decimal

    def __post_init__(self) -> None:
        if not self.request_id or type(self.quantity) is not Decimal or self.quantity <= 0:
            raise ValueError("order request_id and positive Decimal quantity are required")


@dataclass(frozen=True)
class CapitalMarginAssumptions:
    model_version: str
    contract_multiplier: Decimal
    initial_margin_rate: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not self.model_version or not self.currency:
            raise ValueError("capital/margin model version and currency are required")
        if type(self.contract_multiplier) is not Decimal or self.contract_multiplier <= 0:
            raise ValueError("contract multiplier must be a positive Decimal")
        if type(self.initial_margin_rate) is not Decimal or not Decimal("0") < self.initial_margin_rate <= Decimal("1"):
            raise ValueError("initial margin rate must be a Decimal in (0, 1]")

    @property
    def identity_id(self) -> str:
        return _execution_hash(
            {
                "model_version": self.model_version,
                "contract_multiplier": str(self.contract_multiplier),
                "initial_margin_rate": str(self.initial_margin_rate),
                "currency": self.currency,
            }
        )


@dataclass(frozen=True)
class CapitalSnapshot:
    starting_capital: Decimal
    reserved_margin: Decimal = Decimal("0")
    charged_costs: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        values = (self.starting_capital, self.reserved_margin, self.charged_costs)
        if any(type(value) is not Decimal or value < 0 for value in values):
            raise ValueError("capital values must be non-negative Decimals")
        if self.available_capital < 0:
            raise ValueError("capital snapshot cannot have negative available capital")

    @property
    def available_capital(self) -> Decimal:
        return self.starting_capital - self.reserved_margin - self.charged_costs


@dataclass(frozen=True)
class CapitalTransition:
    request_id: str
    before: CapitalSnapshot
    after: CapitalSnapshot
    required_margin: Decimal
    required_cost: Decimal


def _execution_hash(value: object) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ExecutionAssumptions:
    execution_model_version: str
    synthetic_slippage: Decimal
    synthetic_fee: Decimal
    fill_rule: str = "NEXT_TRADABLE_OBSERVATION"

    def __post_init__(self) -> None:
        if not self.execution_model_version or not self.fill_rule:
            raise ValueError("execution model version and fill rule are required")
        if self.synthetic_slippage < 0 or self.synthetic_fee < 0:
            raise ValueError("synthetic execution costs cannot be negative")

    @property
    def identity_id(self) -> str:
        return _execution_hash(
            {
                "execution_model_version": self.execution_model_version,
                "synthetic_slippage": str(self.synthetic_slippage),
                "synthetic_fee": str(self.synthetic_fee),
                "fill_rule": self.fill_rule,
            }
        )


@dataclass(frozen=True)
class ExecutionObservation:
    request_id: str
    observed_at: datetime
    available_at: datetime
    price: Decimal
    tradable: bool = True

    def __post_init__(self) -> None:
        if not self.request_id or self.observed_at.tzinfo is None or self.available_at.tzinfo is None:
            raise ValueError("execution observation requires request_id and timezone-aware timestamps")
        if self.available_at < self.observed_at:
            raise ValueError("execution observation cannot be available before it is observed")
        if self.price <= 0:
            raise ValueError("execution observation price must be positive")


@dataclass(frozen=True)
class ExecutionOutcome:
    request_id: str
    status: FillStatus
    evaluated_at: datetime
    execution_assumption_id: str
    fill_price: Decimal | None
    total_cost: Decimal | None
    reason: str
    capital_assumption_id: str | None = None


@dataclass(frozen=True)
class ValidationInput:
    request_id: str
    bar: CompletedBar
    decision_at: datetime

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("validation request_id is required")
        if self.decision_at.tzinfo is None:
            raise ValueError("decision timestamp must be timezone-aware")


@dataclass(frozen=True)
class ExecutionEvent:
    timestamp: datetime
    event_type: str
    request_id: str


@dataclass(frozen=True)
class ValidationRunResult:
    allowed: bool
    events: tuple[ExecutionEvent, ...]
    access_record: EvidenceRecord
    validation_record: EvidenceRecord | None
    execution_outcomes: tuple[ExecutionOutcome, ...] = ()
    capital_transitions: tuple[CapitalTransition, ...] = ()


class ChronologicalValidationRunner:
    """A neutral visible-input -> intent -> order -> fill feasibility runner."""

    _EVENT_ORDER = {
        "VISIBLE_MARKET_INPUT": 0,
        "STRATEGY_INTENT": 1,
        "ORDER_CREATED": 2,
        "FILL_ELIGIBLE": 3,
        "FILLED": 4,
        "NOT_FILLED": 4,
    }

    def __init__(self, ledger: EvidenceLedger, firewall: FinalUnseenFirewall) -> None:
        self._ledger = ledger
        self._firewall = firewall

    @staticmethod
    def _validate_binding(
        strategy: StrategyIdentity,
        experiment: ExperimentIdentity,
        artifact_identity_id: str,
        artifact_code_hash: str,
    ) -> None:
        if artifact_identity_id != strategy.identity_id or artifact_code_hash != strategy.code_hash:
            raise ValueError("strategy artifact does not match strategy identity")
        expected = ExperimentIdentity.from_strategy(
            strategy, experiment.data_version, experiment.dataset_exposure_reference
        )
        if expected != experiment:
            raise ValueError("experiment is not bound to the supplied strategy identity")

    @classmethod
    def _ordered_events(cls, inputs: Iterable[ValidationInput]) -> tuple[ExecutionEvent, ...]:
        ordered_inputs = tuple(inputs)
        previous_key: tuple[datetime, str] | None = None
        for item in ordered_inputs:
            if not item.bar.is_visible_at(item.decision_at):
                raise ChronologyError("strategy intent cannot use an unavailable completed bar")
            key = (item.decision_at, item.request_id)
            if previous_key is not None and key <= previous_key:
                raise ChronologyError("validation inputs must be strictly chronological by decision time and request_id")
            previous_key = key

        events: list[ExecutionEvent] = []
        for item in ordered_inputs:
            events.extend(
                (
                    ExecutionEvent(item.bar.available_at, "VISIBLE_MARKET_INPUT", item.request_id),
                    ExecutionEvent(item.decision_at, "STRATEGY_INTENT", item.request_id),
                    ExecutionEvent(item.decision_at, "ORDER_CREATED", item.request_id),
                    ExecutionEvent(item.decision_at, "FILL_ELIGIBLE", item.request_id),
                )
            )
        return tuple(sorted(events, key=lambda event: (event.timestamp, cls._EVENT_ORDER[event.event_type], event.request_id)))

    @staticmethod
    def _ordered_observations(observations: Iterable[ExecutionObservation]) -> dict[str, ExecutionObservation]:
        ordered = tuple(observations)
        previous_key: tuple[datetime, str] | None = None
        by_request: dict[str, ExecutionObservation] = {}
        for observation in ordered:
            key = (observation.available_at, observation.request_id)
            if previous_key is not None and key <= previous_key:
                raise ChronologyError("execution observations must be strictly chronological by availability and request_id")
            if observation.request_id in by_request:
                raise ChronologyError("execution observation request_id must be unique")
            previous_key = key
            by_request[observation.request_id] = observation
        return by_request

    def _evaluate_execution(
        self,
        inputs: tuple[ValidationInput, ...],
        observations: Iterable[ExecutionObservation],
        cutoff_at: datetime,
        assumptions: ExecutionAssumptions,
    ) -> tuple[ExecutionOutcome, ...]:
        if cutoff_at.tzinfo is None:
            raise ValueError("execution cutoff must be timezone-aware")
        observations_by_request = self._ordered_observations(observations)
        outcomes: list[ExecutionOutcome] = []
        for item in inputs:
            if cutoff_at < item.decision_at:
                raise ChronologyError("execution cutoff cannot precede fill eligibility")
            observation = observations_by_request.get(item.request_id)
            if observation is None:
                outcomes.append(ExecutionOutcome(item.request_id, FillStatus.NOT_FILLED, cutoff_at, assumptions.identity_id, None, None, "NO_OBSERVATION"))
                continue
            if observation.available_at <= item.decision_at:
                raise ChronologyError("same-decision execution observation is not independently available")
            if observation.available_at > cutoff_at:
                outcomes.append(ExecutionOutcome(item.request_id, FillStatus.NOT_FILLED, cutoff_at, assumptions.identity_id, None, None, "OBSERVATION_AFTER_CUTOFF"))
                continue
            if not observation.tradable:
                outcomes.append(ExecutionOutcome(item.request_id, FillStatus.NOT_FILLED, observation.available_at, assumptions.identity_id, None, None, "NOT_TRADABLE"))
                continue
            outcomes.append(
                ExecutionOutcome(
                    item.request_id,
                    FillStatus.FILLED,
                    observation.available_at,
                    assumptions.identity_id,
                    observation.price + assumptions.synthetic_slippage,
                    assumptions.synthetic_fee,
                    "TRADABLE_OBSERVATION",
                )
            )
        return tuple(outcomes)

    @staticmethod
    def _apply_capital_constraints(
        outcomes: tuple[ExecutionOutcome, ...],
        specifications: Iterable[OrderSpecification],
        snapshot: CapitalSnapshot,
        assumptions: CapitalMarginAssumptions,
    ) -> tuple[tuple[ExecutionOutcome, ...], tuple[CapitalTransition, ...]]:
        specifications = tuple(specifications)
        if tuple(spec.request_id for spec in specifications) != tuple(outcome.request_id for outcome in outcomes):
            raise ValueError("order specifications must bind exactly to execution requests in order")
        current = snapshot
        constrained: list[ExecutionOutcome] = []
        transitions: list[CapitalTransition] = []
        for outcome, specification in zip(outcomes, specifications):
            if outcome.status is not FillStatus.FILLED:
                transitions.append(CapitalTransition(specification.request_id, current, current, Decimal("0"), Decimal("0")))
                constrained.append(replace(outcome, capital_assumption_id=assumptions.identity_id))
                continue
            required_margin = outcome.fill_price * specification.quantity * assumptions.contract_multiplier * assumptions.initial_margin_rate
            required_cost = outcome.total_cost
            if current.available_capital < required_margin + required_cost:
                constrained.append(ExecutionOutcome(specification.request_id, FillStatus.NOT_FILLED, outcome.evaluated_at, outcome.execution_assumption_id, None, None, "INSUFFICIENT_MARGIN", assumptions.identity_id))
                transitions.append(CapitalTransition(specification.request_id, current, current, required_margin, required_cost))
                continue
            next_snapshot = CapitalSnapshot(current.starting_capital, current.reserved_margin + required_margin, current.charged_costs + required_cost)
            constrained.append(replace(outcome, capital_assumption_id=assumptions.identity_id))
            transitions.append(CapitalTransition(specification.request_id, current, next_snapshot, required_margin, required_cost))
            current = next_snapshot
        return tuple(constrained), tuple(transitions)

    def run(
        self,
        *,
        mode: ValidationMode,
        strategy: StrategyIdentity,
        experiment: ExperimentIdentity,
        artifact_identity_id: str,
        artifact_code_hash: str,
        dataset_class: DatasetClass,
        inputs: Iterable[ValidationInput],
        disposition: ValidationDisposition | None = None,
        execution_observations: Iterable[ExecutionObservation] = (),
        execution_cutoff_at: datetime | None = None,
        execution_assumptions: ExecutionAssumptions | None = None,
        order_specifications: Iterable[OrderSpecification] = (),
        capital_snapshot: CapitalSnapshot | None = None,
        capital_margin_assumptions: CapitalMarginAssumptions | None = None,
    ) -> ValidationRunResult:
        self._validate_binding(strategy, experiment, artifact_identity_id, artifact_code_hash)
        if mode is ValidationMode.FAST and disposition is ValidationDisposition.CONFIRMED:
            raise ValueError("FAST mode cannot establish confirmatory validity")
        if dataset_class is DatasetClass.FINAL_UNSEEN:
            access = self._firewall.request_access(experiment, dataset_class)
            return ValidationRunResult(False, (), access.record, None)
        inputs = tuple(inputs)
        if mode is ValidationMode.CONFIRMATORY and disposition is ValidationDisposition.CONFIRMED:
            if execution_cutoff_at is None or execution_assumptions is None:
                raise ValueError("confirmatory validity requires execution assumptions and evaluation")
            if not inputs:
                raise ValueError("confirmatory validity requires at least one execution evaluation")
            if capital_snapshot is None or capital_margin_assumptions is None:
                raise ValueError("confirmatory validity requires capital/margin assumptions and snapshot")

        access = self._firewall.request_access(experiment, dataset_class)
        if not access.allowed:
            return ValidationRunResult(False, (), access.record, None)

        events = self._ordered_events(inputs)
        execution_outcomes: tuple[ExecutionOutcome, ...] = ()
        capital_transitions: tuple[CapitalTransition, ...] = ()
        if mode is ValidationMode.CONFIRMATORY and disposition is ValidationDisposition.CONFIRMED:
            execution_outcomes = self._evaluate_execution(inputs, execution_observations, execution_cutoff_at, execution_assumptions)
            execution_outcomes, capital_transitions = self._apply_capital_constraints(execution_outcomes, order_specifications, capital_snapshot, capital_margin_assumptions)
            assumption_reference = f"execution:{execution_assumptions.identity_id};capital:{capital_margin_assumptions.identity_id}"
            for outcome in execution_outcomes:
                event_type = "EXECUTION_FILLED" if outcome.status is FillStatus.FILLED else "EXECUTION_NOT_FILLED"
                self._ledger.append(EvidenceRecord(event_type, experiment, dataset_class, outcome.reason, evidence_reference=assumption_reference))
                events += (ExecutionEvent(outcome.evaluated_at, outcome.status.value, outcome.request_id),)
            events = tuple(sorted(events, key=lambda event: (event.timestamp, self._EVENT_ORDER[event.event_type], event.request_id)))
        validation_record = None
        if disposition is ValidationDisposition.REJECTED:
            validation_record = self._ledger.append(
                EvidenceRecord("VALIDATION_REJECTED", experiment, dataset_class, "REJECTED")
            )
        elif disposition is ValidationDisposition.CONFIRMED:
            validation_record = self._ledger.append(EvidenceRecord("VALIDATION_CONFIRMED", experiment, dataset_class, "CONFIRMED", evidence_reference=assumption_reference))
        return ValidationRunResult(True, events, access.record, validation_record, execution_outcomes, capital_transitions)

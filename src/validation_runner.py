"""Minimum deterministic validation connection semantics for Skeleton v1.0."""

from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from datetime import date, datetime
from enum import Enum
from hashlib import sha256
import json
from typing import Iterable

from src.contract_semantics import (
    CloseOffset,
    ContractMappingSchedule,
    ContractMaster,
    ContractResolution,
    ContractResolver,
    OffsetCostAssumptions,
    OrderAction,
    PositionDirection,
    PriceLimitFact,
)
from src.data_substrate import CompletedBar, SessionMetadata
from src.research_firewall import Cohort, ResearchFirewall
from src.strategy_evidence import (
    DatasetClass,
    EvidenceLedger,
    EvidenceRecord,
    ExperimentIdentity,
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
    action: OrderAction = OrderAction.OPEN
    close_offset: CloseOffset | None = None
    direction: PositionDirection = PositionDirection.LONG

    def __post_init__(self) -> None:
        if not self.request_id or type(self.quantity) is not Decimal or self.quantity <= 0:
            raise ValueError("order request_id and positive Decimal quantity are required")
        if self.action is OrderAction.OPEN and self.close_offset is not None:
            raise ValueError("open order cannot specify a close offset")
        if self.action is OrderAction.CLOSE and self.close_offset is None:
            raise ValueError("close order requires an explicit close offset")
        if not isinstance(self.direction, PositionDirection):
            raise ValueError("order direction must be an explicit position direction")


@dataclass(frozen=True)
class CapitalMarginAssumptions:
    model_version: str
    contract_multiplier: Decimal
    initial_margin_rate: Decimal
    currency: str
    maintenance_margin_rate: Decimal = Decimal("0.05")
    breach_rule: str = "EQUITY_BELOW_MAINTENANCE_REQUIREMENT"
    liquidation_rule_version: str = "FULL_POSITION_NEXT_TRADABLE_OBSERVATION_V1"

    def __post_init__(self) -> None:
        if not self.model_version or not self.currency:
            raise ValueError("capital/margin model version and currency are required")
        if type(self.contract_multiplier) is not Decimal or self.contract_multiplier <= 0:
            raise ValueError("contract multiplier must be a positive Decimal")
        if type(self.initial_margin_rate) is not Decimal or not Decimal("0") < self.initial_margin_rate <= Decimal("1"):
            raise ValueError("initial margin rate must be a Decimal in (0, 1]")
        if type(self.maintenance_margin_rate) is not Decimal or not Decimal("0") < self.maintenance_margin_rate <= self.initial_margin_rate:
            raise ValueError("maintenance margin rate must be a Decimal in (0, initial margin rate]")
        if self.breach_rule != "EQUITY_BELOW_MAINTENANCE_REQUIREMENT":
            raise ValueError("unsupported synthetic maintenance breach rule")
        if self.liquidation_rule_version != "FULL_POSITION_NEXT_TRADABLE_OBSERVATION_V1":
            raise ValueError("unsupported synthetic liquidation rule")

    @property
    def identity_id(self) -> str:
        return _execution_hash(
            {
                "model_version": self.model_version,
                "contract_multiplier": str(self.contract_multiplier),
                "initial_margin_rate": str(self.initial_margin_rate),
                "currency": self.currency,
                "maintenance_margin_rate": str(self.maintenance_margin_rate),
                "breach_rule": self.breach_rule,
                "liquidation_rule_version": self.liquidation_rule_version,
            }
        )


@dataclass(frozen=True)
class CapitalSnapshot:
    starting_capital: Decimal
    reserved_margin: Decimal = Decimal("0")
    charged_costs: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")
    unrealized_pnl: Decimal = Decimal("0")
    position_quantity: Decimal = Decimal("0")
    average_open_price: Decimal = Decimal("0")
    position_instrument: str | None = None
    position_id: str | None = None
    position_request_id: str | None = None
    execution_assumption_id: str | None = None
    capital_assumption_id: str | None = None
    state_at: datetime | None = None
    latest_mark_reference: str | None = None
    concrete_contract_id: str | None = None
    contract_identity_id: str | None = None
    contract_master_identity_id: str | None = None
    mapping_schedule_identity_id: str | None = None
    mapping_entry_identity_id: str | None = None
    position_trading_day: date | None = None
    today_quantity: Decimal = Decimal("0")
    previous_quantity: Decimal = Decimal("0")
    position_direction: PositionDirection | None = None

    def __post_init__(self) -> None:
        non_negative = (
            self.starting_capital,
            self.reserved_margin,
            self.charged_costs,
            self.position_quantity,
            self.average_open_price,
            self.today_quantity,
            self.previous_quantity,
        )
        if any(type(value) is not Decimal or value < 0 for value in non_negative):
            raise ValueError("capital, position, and price values must be non-negative Decimals")
        if type(self.realized_pnl) is not Decimal or type(self.unrealized_pnl) is not Decimal:
            raise ValueError("PnL values must be Decimals")
        if self.state_at is not None and self.state_at.tzinfo is None:
            raise ValueError("capital snapshot state timestamp must be timezone-aware")
        active_bindings = (
            self.position_instrument,
            self.position_id,
            self.position_request_id,
            self.execution_assumption_id,
            self.capital_assumption_id,
            self.position_direction,
        )
        if self.position_quantity == 0:
            if self.average_open_price != 0 or self.reserved_margin != 0 or self.unrealized_pnl != 0:
                raise ValueError("a flat snapshot cannot retain price, margin, or unrealized PnL")
            if any(value is not None for value in active_bindings):
                raise ValueError("a flat snapshot cannot retain active position bindings")
            contract_bindings = (
                self.concrete_contract_id,
                self.contract_identity_id,
                self.contract_master_identity_id,
                self.mapping_schedule_identity_id,
                self.mapping_entry_identity_id,
                self.position_trading_day,
            )
            if self.today_quantity != 0 or self.previous_quantity != 0 or any(
                value is not None for value in contract_bindings
            ):
                raise ValueError("a flat snapshot cannot retain contract or position-bucket bindings")
        elif self.average_open_price <= 0 or any(not value for value in active_bindings):
            raise ValueError("an open position requires price and complete identity bindings")
        elif self.today_quantity + self.previous_quantity != self.position_quantity:
            raise ValueError("today and previous position buckets must reconcile to total quantity")
        elif self.concrete_contract_id is not None:
            required_contract_bindings = (
                self.contract_identity_id,
                self.contract_master_identity_id,
                self.position_trading_day,
            )
            if any(not value for value in required_contract_bindings):
                raise ValueError("a contract-bound position requires complete contract identity and trading day")

    @property
    def available_capital(self) -> Decimal:
        return self.cash_balance - self.reserved_margin

    @property
    def cash_balance(self) -> Decimal:
        return self.starting_capital + self.realized_pnl - self.charged_costs

    @property
    def equity(self) -> Decimal:
        return self.cash_balance + self.unrealized_pnl

    @property
    def available_resources(self) -> Decimal:
        return self.equity - self.reserved_margin

    @property
    def reference_id(self) -> str:
        return _execution_hash(
            {
                "starting_capital": str(self.starting_capital),
                "reserved_margin": str(self.reserved_margin),
                "charged_costs": str(self.charged_costs),
                "realized_pnl": str(self.realized_pnl),
                "unrealized_pnl": str(self.unrealized_pnl),
                "position_quantity": str(self.position_quantity),
                "average_open_price": str(self.average_open_price),
                "position_instrument": self.position_instrument,
                "position_id": self.position_id,
                "position_request_id": self.position_request_id,
                "execution_assumption_id": self.execution_assumption_id,
                "capital_assumption_id": self.capital_assumption_id,
                "state_at": self.state_at.isoformat() if self.state_at else None,
                "latest_mark_reference": self.latest_mark_reference,
                "concrete_contract_id": self.concrete_contract_id,
                "contract_identity_id": self.contract_identity_id,
                "contract_master_identity_id": self.contract_master_identity_id,
                "mapping_schedule_identity_id": self.mapping_schedule_identity_id,
                "mapping_entry_identity_id": self.mapping_entry_identity_id,
                "position_trading_day": self.position_trading_day.isoformat() if self.position_trading_day else None,
                "today_quantity": str(self.today_quantity),
                "previous_quantity": str(self.previous_quantity),
                "position_direction": self.position_direction.value if self.position_direction else None,
            }
        )


@dataclass(frozen=True)
class CapitalTransition:
    request_id: str
    before: CapitalSnapshot
    after: CapitalSnapshot
    required_margin: Decimal
    required_cost: Decimal
    quantity_change: Decimal = Decimal("0")
    realized_pnl_change: Decimal = Decimal("0")
    released_margin: Decimal = Decimal("0")
    transition_type: str = "ORDER_EXECUTION"
    aged_quantity: Decimal = Decimal("0")
    resolved_close_offset: CloseOffset | None = None
    contract_resolution_id: str | None = None
    offset_cost_assumption_id: str | None = None

    def __post_init__(self) -> None:
        decimal_values = (
            self.required_margin,
            self.required_cost,
            self.quantity_change,
            self.realized_pnl_change,
            self.released_margin,
            self.aged_quantity,
        )
        if not self.request_id or not self.transition_type or any(type(value) is not Decimal for value in decimal_values):
            raise ValueError("capital transition requires an identity and Decimal arithmetic")
        if self.required_margin < 0 or self.required_cost < 0 or self.released_margin < 0:
            raise ValueError("margin, cost, and release values cannot be negative")

    @property
    def reference_id(self) -> str:
        return _execution_hash(
            {
                "request_id": self.request_id,
                "before": self.before.reference_id,
                "after": self.after.reference_id,
                "required_margin": str(self.required_margin),
                "required_cost": str(self.required_cost),
                "quantity_change": str(self.quantity_change),
                "realized_pnl_change": str(self.realized_pnl_change),
                "released_margin": str(self.released_margin),
                "transition_type": self.transition_type,
                "aged_quantity": str(self.aged_quantity),
                "resolved_close_offset": self.resolved_close_offset.value if self.resolved_close_offset else None,
                "contract_resolution_id": self.contract_resolution_id,
                "offset_cost_assumption_id": self.offset_cost_assumption_id,
            }
        )


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
        if type(self.synthetic_slippage) is not Decimal or type(self.synthetic_fee) is not Decimal:
            raise ValueError("synthetic execution costs must be Decimals")
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
    concrete_contract_id: str | None = None

    def __post_init__(self) -> None:
        if not self.request_id or self.observed_at.tzinfo is None or self.available_at.tzinfo is None:
            raise ValueError("execution observation requires request_id and timezone-aware timestamps")
        if self.available_at < self.observed_at:
            raise ValueError("execution observation cannot be available before it is observed")
        if type(self.price) is not Decimal or self.price <= 0:
            raise ValueError("execution observation price must be a positive Decimal")


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
    contract_resolution_id: str | None = None
    concrete_contract_id: str | None = None
    contract_identity_id: str | None = None
    contract_master_identity_id: str | None = None
    mapping_schedule_identity_id: str | None = None
    mapping_entry_identity_id: str | None = None
    price_limit_fact_id: str | None = None
    resolved_close_offset: CloseOffset | None = None
    offset_cost_assumption_id: str | None = None

    @property
    def reference_id(self) -> str:
        return _execution_hash(
            {
                "request_id": self.request_id,
                "status": self.status.value,
                "evaluated_at": self.evaluated_at.isoformat(),
                "execution_assumption_id": self.execution_assumption_id,
                "fill_price": str(self.fill_price) if self.fill_price is not None else None,
                "total_cost": str(self.total_cost) if self.total_cost is not None else None,
                "reason": self.reason,
                "capital_assumption_id": self.capital_assumption_id,
                "contract_resolution_id": self.contract_resolution_id,
                "concrete_contract_id": self.concrete_contract_id,
                "contract_identity_id": self.contract_identity_id,
                "contract_master_identity_id": self.contract_master_identity_id,
                "mapping_schedule_identity_id": self.mapping_schedule_identity_id,
                "mapping_entry_identity_id": self.mapping_entry_identity_id,
                "price_limit_fact_id": self.price_limit_fact_id,
                "resolved_close_offset": self.resolved_close_offset.value if self.resolved_close_offset else None,
                "offset_cost_assumption_id": self.offset_cost_assumption_id,
            }
        )


@dataclass(frozen=True)
class MarkObservation:
    observation_id: str
    position_id: str
    position_request_id: str
    instrument: str
    observed_at: datetime
    available_at: datetime
    price: Decimal

    def __post_init__(self) -> None:
        required = (self.observation_id, self.position_id, self.position_request_id, self.instrument)
        if not all(required) or self.observed_at.tzinfo is None or self.available_at.tzinfo is None:
            raise ValueError("mark observation requires identities and timezone-aware timestamps")
        if self.available_at < self.observed_at:
            raise ValueError("mark observation cannot be available before it is observed")
        if type(self.price) is not Decimal or self.price <= 0:
            raise ValueError("mark price must be a positive Decimal")

    @property
    def reference_id(self) -> str:
        return _execution_hash(
            {
                "observation_id": self.observation_id,
                "position_id": self.position_id,
                "position_request_id": self.position_request_id,
                "instrument": self.instrument,
                "observed_at": self.observed_at.isoformat(),
                "available_at": self.available_at.isoformat(),
                "price": str(self.price),
            }
        )


@dataclass(frozen=True)
class MarkToMarketTransition:
    observation: MarkObservation
    before: CapitalSnapshot
    after: CapitalSnapshot
    maintenance_requirement: Decimal
    breached: bool

    @property
    def reference_id(self) -> str:
        return _execution_hash(
            {
                "mark": self.observation.reference_id,
                "before": self.before.reference_id,
                "after": self.after.reference_id,
                "maintenance_requirement": str(self.maintenance_requirement),
                "breached": self.breached,
            }
        )


@dataclass(frozen=True)
class ForcedLiquidationRequirement:
    request_id: str
    position_id: str
    instrument: str
    quantity: Decimal
    breach_at: datetime
    eligible_at: datetime
    mark_reference: str
    capital_assumption_id: str
    contract_identity_id: str | None = None
    contract_master_identity_id: str | None = None
    mapping_entry_identity_id: str | None = None

    @property
    def reference_id(self) -> str:
        return _execution_hash(
            {
                "request_id": self.request_id,
                "position_id": self.position_id,
                "instrument": self.instrument,
                "quantity": str(self.quantity),
                "breach_at": self.breach_at.isoformat(),
                "eligible_at": self.eligible_at.isoformat(),
                "mark_reference": self.mark_reference,
                "capital_assumption_id": self.capital_assumption_id,
                "contract_identity_id": self.contract_identity_id,
                "contract_master_identity_id": self.contract_master_identity_id,
                "mapping_entry_identity_id": self.mapping_entry_identity_id,
            }
        )


@dataclass(frozen=True)
class ForcedLiquidationOutcome:
    requirement: ForcedLiquidationRequirement
    execution_outcome: ExecutionOutcome
    capital_transition: CapitalTransition | None

    @property
    def reference_id(self) -> str:
        return _execution_hash(
            {
                "requirement": self.requirement.reference_id,
                "execution_outcome": self.execution_outcome.reference_id,
                "capital_transition": self.capital_transition.reference_id if self.capital_transition else None,
            }
        )


@dataclass(frozen=True)
class ValidationInput:
    request_id: str
    bar: CompletedBar
    decision_at: datetime
    data_version_id: str

    def __post_init__(self) -> None:
        if not self.request_id:
            raise ValueError("validation request_id is required")
        if not self.data_version_id:
            raise ValueError("validation input data_version_id is required")
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
    mark_transitions: tuple[MarkToMarketTransition, ...] = ()
    liquidation_requirement: ForcedLiquidationRequirement | None = None
    liquidation_outcome: ForcedLiquidationOutcome | None = None
    final_capital_snapshot: CapitalSnapshot | None = None
    contract_resolutions: tuple[ContractResolution, ...] = ()


class ChronologicalValidationRunner:
    """A neutral visible-input -> intent -> order -> fill feasibility runner."""

    _EVENT_ORDER = {
        "VISIBLE_MARKET_INPUT": 0,
        "STRATEGY_INTENT": 1,
        "CONTRACT_RESOLVED": 2,
        "ORDER_CREATED": 3,
        "FILL_ELIGIBLE": 4,
        "FILLED": 5,
        "NOT_FILLED": 5,
        "POSITION_TRANSITION": 6,
        "MARK_TO_MARKET": 7,
        "MAINTENANCE_MARGIN_HEALTHY": 8,
        "MAINTENANCE_MARGIN_BREACH": 8,
        "FORCED_LIQUIDATION_REQUIRED": 9,
        "FORCED_LIQUIDATION_FILLED": 10,
        "FORCED_LIQUIDATION_NOT_FILLED": 10,
    }

    def __init__(self, ledger: EvidenceLedger, firewall: ResearchFirewall) -> None:
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
        experiment.validate_strategy(strategy)

    @staticmethod
    def _validate_data_version_binding(
        experiment: ExperimentIdentity,
        inputs: tuple[ValidationInput, ...],
    ) -> None:
        """F-05: every actual input must be bound to the experiment data version."""
        for item in inputs:
            if item.data_version_id != experiment.data_version:
                raise ValueError(
                    "validation input data_version does not match the experiment data version"
                )

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

    @staticmethod
    def _resolve_contracts(
        inputs: tuple[ValidationInput, ...],
        strategy: StrategyIdentity,
        master: ContractMaster,
        schedule: ContractMappingSchedule,
        sessions: SessionMetadata,
        capital_assumptions: CapitalMarginAssumptions,
    ) -> tuple[ContractResolution, ...]:
        resolver = ContractResolver(master, schedule)
        resolutions: list[ContractResolution] = []
        for item in inputs:
            if item.bar.instrument not in strategy.applicable_instruments:
                raise ValueError("validation request symbol is not bound to the strategy identity")
            resolution = resolver.resolve(item.request_id, item.bar.instrument, item.decision_at)
            contract = master.get(resolution.concrete_instrument_id)
            if contract is None or contract.contract_multiplier != capital_assumptions.contract_multiplier:
                raise ValueError("contract multiplier is inconsistent with capital assumptions")
            trading_day = sessions.trading_day_at(
                contract.exchange,
                contract.instrument_id,
                item.decision_at,
            )
            if trading_day != item.bar.trading_day:
                raise ValueError("completed-bar trading day is inconsistent with explicit contract session metadata")
            resolutions.append(resolution)
        return tuple(resolutions)

    @staticmethod
    def _visible_limit_fact(
        facts: tuple[PriceLimitFact, ...],
        contract_identity_id: str,
        concrete_contract_id: str,
        trading_day: date,
        rule_identity: str,
        available_at: datetime,
    ) -> PriceLimitFact:
        matches = [
            fact
            for fact in facts
            if fact.concrete_instrument_id == concrete_contract_id
            and fact.contract_identity_id == contract_identity_id
            and fact.trading_day == trading_day
            and fact.rule_identity == rule_identity
            and fact.available_at <= available_at
        ]
        if len(matches) != 1:
            raise ValueError("required price-limit metadata must resolve point-in-time to exactly one fact")
        return matches[0]

    def _evaluate_execution(
        self,
        inputs: tuple[ValidationInput, ...],
        observations: Iterable[ExecutionObservation],
        cutoff_at: datetime,
        assumptions: ExecutionAssumptions,
        specifications: tuple[OrderSpecification, ...],
        resolutions: tuple[ContractResolution, ...],
        contract_master: ContractMaster | None,
        session_metadata: SessionMetadata | None,
        price_limit_facts: tuple[PriceLimitFact, ...],
    ) -> tuple[ExecutionOutcome, ...]:
        if cutoff_at.tzinfo is None:
            raise ValueError("execution cutoff must be timezone-aware")
        if tuple(spec.request_id for spec in specifications) != tuple(item.request_id for item in inputs):
            raise ValueError("order specifications must bind exactly to validation requests in order")
        if resolutions and tuple(item.request_id for item in resolutions) != tuple(item.request_id for item in inputs):
            raise ValueError("contract resolutions must bind exactly to validation requests in order")
        observations_by_request = self._ordered_observations(observations)
        resolutions_by_request = {item.request_id: item for item in resolutions}
        specifications_by_request = {item.request_id: item for item in specifications}
        outcomes: list[ExecutionOutcome] = []
        for item in inputs:
            if cutoff_at < item.decision_at:
                raise ChronologyError("execution cutoff cannot precede fill eligibility")
            specification = specifications_by_request[item.request_id]
            resolution = resolutions_by_request.get(item.request_id)
            contract_fields = {
                "contract_resolution_id": resolution.identity_id if resolution else None,
                "concrete_contract_id": resolution.concrete_instrument_id if resolution else None,
                "contract_identity_id": resolution.contract_identity_id if resolution else None,
                "contract_master_identity_id": resolution.contract_master_identity_id if resolution else None,
                "mapping_schedule_identity_id": resolution.mapping_schedule_identity_id if resolution else None,
                "mapping_entry_identity_id": resolution.mapping_entry_identity_id if resolution else None,
            }
            observation = observations_by_request.get(item.request_id)
            if observation is None:
                outcomes.append(
                    ExecutionOutcome(
                        item.request_id,
                        FillStatus.NOT_FILLED,
                        cutoff_at,
                        assumptions.identity_id,
                        None,
                        None,
                        "NO_OBSERVATION",
                        **contract_fields,
                    )
                )
                continue
            if observation.available_at <= item.decision_at:
                raise ChronologyError("same-decision execution observation is not independently available")
            if observation.available_at > cutoff_at:
                outcomes.append(
                    ExecutionOutcome(
                        item.request_id,
                        FillStatus.NOT_FILLED,
                        cutoff_at,
                        assumptions.identity_id,
                        None,
                        None,
                        "OBSERVATION_AFTER_CUTOFF",
                        **contract_fields,
                    )
                )
                continue
            if not observation.tradable:
                outcomes.append(
                    ExecutionOutcome(
                        item.request_id,
                        FillStatus.NOT_FILLED,
                        observation.available_at,
                        assumptions.identity_id,
                        None,
                        None,
                        "NOT_TRADABLE",
                        **contract_fields,
                    )
                )
                continue
            buy_side = (
                specification.action is OrderAction.OPEN
                and specification.direction is PositionDirection.LONG
            ) or (
                specification.action is OrderAction.CLOSE
                and specification.direction is PositionDirection.SHORT
            )
            fill_price = (
                observation.price + assumptions.synthetic_slippage
                if buy_side
                else observation.price - assumptions.synthetic_slippage
            )
            limit_fact = None
            if resolution is not None:
                if contract_master is None or session_metadata is None:
                    raise ValueError("contract-bound execution requires master and session metadata")
                contract = contract_master.get(resolution.concrete_instrument_id)
                if contract is None or contract.identity_id != resolution.contract_identity_id:
                    raise ValueError("resolved contract identity is inconsistent with the contract master")
                if observation.concrete_contract_id != contract.instrument_id:
                    raise ValueError("execution observation must bind the resolved concrete contract, not a pseudo-symbol")
                if not contract.is_active_at(observation.available_at):
                    raise ValueError("concrete contract is inactive at execution observation time")
                trading_day = session_metadata.trading_day_at(
                    contract.exchange,
                    contract.instrument_id,
                    observation.observed_at,
                )
                if trading_day != item.bar.trading_day:
                    raise ValueError("execution observation is outside the bound contract trading day")
                if not contract.is_on_tick(observation.price) or fill_price <= 0 or not contract.is_on_tick(fill_price):
                    outcomes.append(
                        ExecutionOutcome(
                            item.request_id,
                            FillStatus.NOT_FILLED,
                            observation.available_at,
                            assumptions.identity_id,
                            None,
                            None,
                            "OFF_TICK_PRICE",
                            **contract_fields,
                        )
                    )
                    continue
                if contract.price_limit_rule_identity is not None:
                    limit_fact = self._visible_limit_fact(
                        price_limit_facts,
                        contract.identity_id,
                        contract.instrument_id,
                        trading_day,
                        contract.price_limit_rule_identity,
                        observation.available_at,
                    )
                    if not contract.is_on_tick(limit_fact.lower_price) or not contract.is_on_tick(limit_fact.upper_price):
                        raise ValueError("price-limit bounds must conform to the contract minimum tick")
                    if limit_fact.locked:
                        outcomes.append(
                            ExecutionOutcome(
                                item.request_id,
                                FillStatus.NOT_FILLED,
                                observation.available_at,
                                assumptions.identity_id,
                                None,
                                None,
                                "LOCKED_PRICE_LIMIT",
                                price_limit_fact_id=limit_fact.identity_id,
                                **contract_fields,
                            )
                        )
                        continue
                    if not (
                        limit_fact.lower_price <= observation.price <= limit_fact.upper_price
                        and limit_fact.lower_price <= fill_price <= limit_fact.upper_price
                    ):
                        outcomes.append(
                            ExecutionOutcome(
                                item.request_id,
                                FillStatus.NOT_FILLED,
                                observation.available_at,
                                assumptions.identity_id,
                                None,
                                None,
                                "OUTSIDE_PRICE_LIMIT",
                                price_limit_fact_id=limit_fact.identity_id,
                                **contract_fields,
                            )
                        )
                        continue
            outcomes.append(
                ExecutionOutcome(
                    item.request_id,
                    FillStatus.FILLED,
                    observation.available_at,
                    assumptions.identity_id,
                    fill_price,
                    assumptions.synthetic_fee,
                    "TRADABLE_OBSERVATION",
                    price_limit_fact_id=limit_fact.identity_id if limit_fact else None,
                    **contract_fields,
                )
            )
        return tuple(outcomes)

    @staticmethod
    def _apply_capital_constraints(
        outcomes: tuple[ExecutionOutcome, ...],
        specifications: Iterable[OrderSpecification],
        inputs: tuple[ValidationInput, ...],
        snapshot: CapitalSnapshot,
        capital_assumptions: CapitalMarginAssumptions,
        execution_assumptions: ExecutionAssumptions,
        resolutions: tuple[ContractResolution, ...] = (),
        offset_cost_assumptions: OffsetCostAssumptions | None = None,
        contract_master: ContractMaster | None = None,
    ) -> tuple[tuple[ExecutionOutcome, ...], tuple[CapitalTransition, ...]]:
        specifications = tuple(specifications)
        if tuple(spec.request_id for spec in specifications) != tuple(outcome.request_id for outcome in outcomes):
            raise ValueError("order specifications must bind exactly to execution requests in order")
        if tuple(item.request_id for item in inputs) != tuple(outcome.request_id for outcome in outcomes):
            raise ValueError("validation inputs must bind exactly to execution requests in order")
        if resolutions and tuple(item.request_id for item in resolutions) != tuple(outcome.request_id for outcome in outcomes):
            raise ValueError("contract resolutions must bind exactly to execution requests in order")
        resolutions_by_request = {item.request_id: item for item in resolutions}
        current = snapshot
        constrained: list[ExecutionOutcome] = []
        transitions: list[CapitalTransition] = []
        for outcome, specification, item in zip(outcomes, specifications, inputs):
            transition_before = current
            aged_quantity = Decimal("0")
            if current.state_at is not None and item.decision_at <= current.state_at:
                raise ChronologyError("order decision must follow the prior capital state")
            if current.position_quantity > 0 and current.position_trading_day is not None:
                if item.bar.trading_day < current.position_trading_day:
                    raise ChronologyError("position trading day cannot move backwards")
                if item.bar.trading_day > current.position_trading_day:
                    aged_quantity = current.today_quantity
                    current = replace(
                        current,
                        today_quantity=Decimal("0"),
                        previous_quantity=current.previous_quantity + current.today_quantity,
                        position_trading_day=item.bar.trading_day,
                        state_at=item.decision_at,
                    )
            resolution = resolutions_by_request.get(specification.request_id)
            if outcome.status is not FillStatus.FILLED:
                transitions.append(
                    CapitalTransition(
                        specification.request_id,
                        transition_before,
                        current,
                        Decimal("0"),
                        Decimal("0"),
                        aged_quantity=aged_quantity,
                        contract_resolution_id=outcome.contract_resolution_id,
                    )
                )
                constrained.append(replace(outcome, capital_assumption_id=capital_assumptions.identity_id))
                continue
            if outcome.fill_price is None or outcome.total_cost is None:
                raise ValueError("filled execution outcome requires price and cost")
            if current.state_at is not None and outcome.evaluated_at <= current.state_at:
                raise ChronologyError("position fill must follow the prior capital snapshot")
            concrete_instrument = resolution.concrete_instrument_id if resolution else item.bar.instrument
            if current.position_quantity > 0:
                if current.execution_assumption_id != execution_assumptions.identity_id:
                    raise ValueError("execution assumption identity changed inside an open position")
                if current.capital_assumption_id != capital_assumptions.identity_id:
                    raise ValueError("capital assumption identity changed inside an open position")
                if current.latest_mark_reference is not None:
                    raise ValueError("cannot add to a position after mark-to-market in the minimum lifecycle")
                if current.position_instrument != concrete_instrument:
                    raise ValueError("a mapping roll cannot silently change the concrete contract of an open position")
                if current.position_direction is not specification.direction:
                    raise ValueError("an order cannot change the direction of an existing position")

            if specification.action is OrderAction.CLOSE:
                if current.position_quantity <= 0:
                    raise ValueError("close order requires an existing position")
                if offset_cost_assumptions is None:
                    raise ValueError("close order requires versioned synthetic offset-cost assumptions")
                if resolution is not None and contract_master is not None:
                    contract = contract_master.get(resolution.concrete_instrument_id)
                    if contract is None or contract.offset_fee_metadata_identity != offset_cost_assumptions.identity_id:
                        raise ValueError("offset-cost assumption identity is inconsistent with contract metadata")
                resolved_offset = specification.close_offset
                if resolved_offset is CloseOffset.CLOSE:
                    if current.today_quantity >= specification.quantity:
                        resolved_offset = CloseOffset.CLOSE_TODAY
                    elif current.previous_quantity >= specification.quantity:
                        resolved_offset = CloseOffset.CLOSE_PREVIOUS
                    else:
                        raise ValueError("generic close cannot deterministically resolve across position buckets")
                if resolved_offset is CloseOffset.CLOSE_TODAY:
                    if current.today_quantity < specification.quantity:
                        raise ValueError("CLOSE_TODAY quantity exceeds today's position bucket")
                    next_today = current.today_quantity - specification.quantity
                    next_previous = current.previous_quantity
                    offset_fee = offset_cost_assumptions.close_today_fee_per_unit * specification.quantity
                elif resolved_offset is CloseOffset.CLOSE_PREVIOUS:
                    if current.previous_quantity < specification.quantity:
                        raise ValueError("CLOSE_PREVIOUS quantity exceeds the previous-day position bucket")
                    next_today = current.today_quantity
                    next_previous = current.previous_quantity - specification.quantity
                    offset_fee = offset_cost_assumptions.close_previous_fee_per_unit * specification.quantity
                else:
                    raise ValueError("close order has an unsupported offset")
                total_cost = outcome.total_cost + offset_fee
                pnl_sign = Decimal("1") if current.position_direction is PositionDirection.LONG else Decimal("-1")
                realized_pnl_change = (
                    (outcome.fill_price - current.average_open_price)
                    * specification.quantity
                    * capital_assumptions.contract_multiplier
                    * pnl_sign
                )
                released_margin = (
                    current.reserved_margin * specification.quantity / current.position_quantity
                )
                remaining_quantity = current.position_quantity - specification.quantity
                if remaining_quantity == 0:
                    next_snapshot = CapitalSnapshot(
                        starting_capital=current.starting_capital,
                        charged_costs=current.charged_costs + total_cost,
                        realized_pnl=current.realized_pnl + realized_pnl_change,
                        state_at=outcome.evaluated_at,
                        latest_mark_reference=current.latest_mark_reference,
                    )
                else:
                    # TD-002: after a partial close the remaining position is
                    # re-marked at the close fill price (the explicit mark
                    # price of this transition), so its unrealized PnL is
                    # deterministic and nonzero where mathematically
                    # appropriate, instead of being temporarily cleared to
                    # zero until a later mark observation.
                    remaining_unrealized_pnl = (
                        (outcome.fill_price - current.average_open_price)
                        * remaining_quantity
                        * capital_assumptions.contract_multiplier
                        * pnl_sign
                    )
                    next_snapshot = replace(
                        current,
                        reserved_margin=current.reserved_margin - released_margin,
                        charged_costs=current.charged_costs + total_cost,
                        realized_pnl=current.realized_pnl + realized_pnl_change,
                        unrealized_pnl=remaining_unrealized_pnl,
                        position_quantity=remaining_quantity,
                        position_request_id=specification.request_id,
                        state_at=outcome.evaluated_at,
                        today_quantity=next_today,
                        previous_quantity=next_previous,
                    )
                constrained_outcome = replace(
                    outcome,
                    total_cost=total_cost,
                    capital_assumption_id=capital_assumptions.identity_id,
                    resolved_close_offset=resolved_offset,
                    offset_cost_assumption_id=offset_cost_assumptions.identity_id,
                )
                constrained.append(constrained_outcome)
                transitions.append(
                    CapitalTransition(
                        specification.request_id,
                        transition_before,
                        next_snapshot,
                        Decimal("0"),
                        total_cost,
                        quantity_change=-specification.quantity,
                        realized_pnl_change=realized_pnl_change,
                        released_margin=released_margin,
                        transition_type="POSITION_CLOSE",
                        aged_quantity=aged_quantity,
                        resolved_close_offset=resolved_offset,
                        contract_resolution_id=outcome.contract_resolution_id,
                        offset_cost_assumption_id=offset_cost_assumptions.identity_id,
                    )
                )
                current = next_snapshot
                continue

            required_margin = outcome.fill_price * specification.quantity * capital_assumptions.contract_multiplier * capital_assumptions.initial_margin_rate
            required_cost = outcome.total_cost
            if current.available_capital < required_margin + required_cost:
                constrained.append(
                    replace(
                        outcome,
                        status=FillStatus.NOT_FILLED,
                        fill_price=None,
                        total_cost=None,
                        reason="INSUFFICIENT_MARGIN",
                        capital_assumption_id=capital_assumptions.identity_id,
                    )
                )
                transitions.append(
                    CapitalTransition(
                        specification.request_id,
                        transition_before,
                        current,
                        required_margin,
                        required_cost,
                        aged_quantity=aged_quantity,
                        contract_resolution_id=outcome.contract_resolution_id,
                    )
                )
                continue
            next_quantity = current.position_quantity + specification.quantity
            weighted_cost = current.average_open_price * current.position_quantity + outcome.fill_price * specification.quantity
            position_id = current.position_id or _execution_hash(
                {
                    "instrument": concrete_instrument,
                    "request_id": specification.request_id,
                    "quantity": str(specification.quantity),
                    "fill_price": str(outcome.fill_price),
                    "execution_assumption_id": execution_assumptions.identity_id,
                    "capital_assumption_id": capital_assumptions.identity_id,
                    "contract_resolution_id": resolution.identity_id if resolution else None,
                    "position_direction": specification.direction.value,
                }
            )
            next_snapshot = CapitalSnapshot(
                starting_capital=current.starting_capital,
                reserved_margin=current.reserved_margin + required_margin,
                charged_costs=current.charged_costs + required_cost,
                realized_pnl=current.realized_pnl,
                unrealized_pnl=Decimal("0"),
                position_quantity=next_quantity,
                average_open_price=weighted_cost / next_quantity,
                position_instrument=concrete_instrument,
                position_id=position_id,
                position_request_id=specification.request_id,
                execution_assumption_id=execution_assumptions.identity_id,
                capital_assumption_id=capital_assumptions.identity_id,
                state_at=outcome.evaluated_at,
                concrete_contract_id=resolution.concrete_instrument_id if resolution else None,
                contract_identity_id=resolution.contract_identity_id if resolution else None,
                contract_master_identity_id=resolution.contract_master_identity_id if resolution else None,
                mapping_schedule_identity_id=(
                    current.mapping_schedule_identity_id
                    if current.position_quantity > 0
                    else resolution.mapping_schedule_identity_id if resolution else None
                ),
                mapping_entry_identity_id=(
                    current.mapping_entry_identity_id
                    if current.position_quantity > 0
                    else resolution.mapping_entry_identity_id if resolution else None
                ),
                position_trading_day=item.bar.trading_day,
                today_quantity=current.today_quantity + specification.quantity,
                previous_quantity=current.previous_quantity,
                position_direction=specification.direction,
            )
            constrained.append(replace(outcome, capital_assumption_id=capital_assumptions.identity_id))
            transitions.append(
                CapitalTransition(
                    specification.request_id,
                    current,
                    next_snapshot,
                    required_margin,
                    required_cost,
                    quantity_change=specification.quantity,
                    aged_quantity=aged_quantity,
                    contract_resolution_id=outcome.contract_resolution_id,
                )
            )
            current = next_snapshot
        return tuple(constrained), tuple(transitions)

    @staticmethod
    def _ordered_marks(marks: Iterable[MarkObservation]) -> tuple[MarkObservation, ...]:
        ordered = tuple(marks)
        previous_key: tuple[datetime, str] | None = None
        seen_ids: set[str] = set()
        for mark in ordered:
            key = (mark.available_at, mark.observation_id)
            if previous_key is not None and key <= previous_key:
                raise ChronologyError("mark observations must be strictly chronological by availability and identity")
            if mark.observation_id in seen_ids:
                raise ChronologyError("mark observation identity must be unique")
            previous_key = key
            seen_ids.add(mark.observation_id)
        return ordered

    @staticmethod
    def _apply_marks(
        marks: Iterable[MarkObservation],
        snapshot: CapitalSnapshot,
        cutoff_at: datetime,
        assumptions: CapitalMarginAssumptions,
    ) -> tuple[tuple[MarkToMarketTransition, ...], ForcedLiquidationRequirement | None]:
        if snapshot.position_quantity <= 0:
            raise ValueError("mark-to-market requires a valid prior filled position")
        if snapshot.capital_assumption_id != assumptions.identity_id:
            raise ValueError("mark-to-market capital assumption identity does not match the position")
        current = snapshot
        transitions: list[MarkToMarketTransition] = []
        requirement = None
        for mark in ChronologicalValidationRunner._ordered_marks(marks):
            if requirement is not None:
                raise ValueError("no further marks are allowed after a maintenance breach")
            if mark.position_id != current.position_id or mark.position_request_id != current.position_request_id:
                raise ValueError("mark observation does not bind to the active position request")
            if mark.instrument != current.position_instrument:
                raise ValueError("mark observation instrument does not match the active position")
            if current.state_at is None or mark.observed_at <= current.state_at or mark.available_at <= current.state_at:
                raise ChronologyError("mark observation must be independently observed and available after the position state")
            if mark.available_at > cutoff_at:
                raise ChronologyError("mark observation is unavailable by the lifecycle cutoff")
            pnl_sign = Decimal("1") if current.position_direction is PositionDirection.LONG else Decimal("-1")
            unrealized_pnl = (
                (mark.price - current.average_open_price)
                * current.position_quantity
                * assumptions.contract_multiplier
                * pnl_sign
            )
            next_snapshot = replace(
                current,
                unrealized_pnl=unrealized_pnl,
                state_at=mark.available_at,
                latest_mark_reference=mark.reference_id,
            )
            maintenance_requirement = (
                mark.price
                * current.position_quantity
                * assumptions.contract_multiplier
                * assumptions.maintenance_margin_rate
            )
            breached = next_snapshot.equity < maintenance_requirement
            transition = MarkToMarketTransition(mark, current, next_snapshot, maintenance_requirement, breached)
            transitions.append(transition)
            current = next_snapshot
            if breached:
                request_id = "forced-liquidation-" + _execution_hash(
                    {
                        "position_id": current.position_id,
                        "mark_reference": mark.reference_id,
                        "capital_assumption_id": assumptions.identity_id,
                    }
                )[:20]
                requirement = ForcedLiquidationRequirement(
                    request_id,
                    current.position_id,
                    current.position_instrument,
                    current.position_quantity,
                    mark.available_at,
                    mark.available_at,
                    mark.reference_id,
                    assumptions.identity_id,
                    current.contract_identity_id,
                    current.contract_master_identity_id,
                    current.mapping_entry_identity_id,
                )
        return tuple(transitions), requirement

    @staticmethod
    def _evaluate_forced_liquidation(
        requirement: ForcedLiquidationRequirement,
        observations: Iterable[ExecutionObservation],
        snapshot: CapitalSnapshot,
        cutoff_at: datetime,
        execution_assumptions: ExecutionAssumptions,
        capital_assumptions: CapitalMarginAssumptions,
        contract_master: ContractMaster | None = None,
        session_metadata: SessionMetadata | None = None,
        price_limit_facts: tuple[PriceLimitFact, ...] = (),
    ) -> ForcedLiquidationOutcome:
        observations = tuple(observations)
        if len(observations) > 1:
            raise ValueError("the minimum lifecycle accepts at most one forced-liquidation observation")
        if snapshot.position_id != requirement.position_id or snapshot.position_quantity != requirement.quantity:
            raise ValueError("forced-liquidation requirement does not match the active position")
        if snapshot.execution_assumption_id != execution_assumptions.identity_id:
            raise ValueError("forced-liquidation execution assumption identity does not match the position")
        if snapshot.capital_assumption_id != capital_assumptions.identity_id:
            raise ValueError("forced-liquidation capital assumption identity does not match the position")
        if requirement.contract_identity_id != snapshot.contract_identity_id:
            raise ValueError("forced-liquidation requirement contract identity does not match the position")
        contract_fields = {
            "concrete_contract_id": snapshot.concrete_contract_id,
            "contract_identity_id": snapshot.contract_identity_id,
            "contract_master_identity_id": snapshot.contract_master_identity_id,
            "mapping_schedule_identity_id": snapshot.mapping_schedule_identity_id,
            "mapping_entry_identity_id": snapshot.mapping_entry_identity_id,
        }
        if not observations:
            outcome = ExecutionOutcome(
                requirement.request_id,
                FillStatus.NOT_FILLED,
                cutoff_at,
                execution_assumptions.identity_id,
                None,
                None,
                "NO_OBSERVATION",
                capital_assumptions.identity_id,
                **contract_fields,
            )
            return ForcedLiquidationOutcome(requirement, outcome, None)
        observation = observations[0]
        if observation.request_id != requirement.request_id:
            raise ValueError("forced-liquidation observation request does not match the requirement")
        if observation.observed_at <= requirement.eligible_at or observation.available_at <= requirement.eligible_at:
            raise ChronologyError("forced-liquidation observation must be later than the maintenance breach")
        if observation.available_at > cutoff_at:
            outcome = ExecutionOutcome(
                requirement.request_id,
                FillStatus.NOT_FILLED,
                cutoff_at,
                execution_assumptions.identity_id,
                None,
                None,
                "OBSERVATION_AFTER_CUTOFF",
                capital_assumptions.identity_id,
                **contract_fields,
            )
            return ForcedLiquidationOutcome(requirement, outcome, None)
        if not observation.tradable:
            outcome = ExecutionOutcome(
                requirement.request_id,
                FillStatus.NOT_FILLED,
                observation.available_at,
                execution_assumptions.identity_id,
                None,
                None,
                "NOT_TRADABLE",
                capital_assumptions.identity_id,
                **contract_fields,
            )
            return ForcedLiquidationOutcome(requirement, outcome, None)
        fill_price = (
            observation.price - execution_assumptions.synthetic_slippage
            if snapshot.position_direction is PositionDirection.LONG
            else observation.price + execution_assumptions.synthetic_slippage
        )
        if fill_price <= 0:
            raise ValueError("synthetic liquidation slippage produces an invalid fill price")
        limit_fact = None
        if snapshot.concrete_contract_id is not None:
            if contract_master is None or session_metadata is None:
                raise ValueError("contract-bound forced liquidation requires master and session metadata")
            contract = contract_master.get(snapshot.concrete_contract_id)
            if contract is None or contract.identity_id != snapshot.contract_identity_id:
                raise ValueError("forced-liquidation contract identity is inconsistent with the contract master")
            if observation.concrete_contract_id != snapshot.concrete_contract_id:
                raise ValueError("forced-liquidation observation does not bind the position's concrete contract")
            if not contract.is_active_at(observation.available_at):
                raise ValueError("forced-liquidation contract is inactive at execution observation time")
            trading_day = session_metadata.trading_day_at(
                contract.exchange,
                contract.instrument_id,
                observation.observed_at,
            )
            if trading_day != snapshot.position_trading_day:
                raise ValueError("forced-liquidation observation is outside the position trading day")
            if not contract.is_on_tick(observation.price) or not contract.is_on_tick(fill_price):
                outcome = ExecutionOutcome(
                    requirement.request_id,
                    FillStatus.NOT_FILLED,
                    observation.available_at,
                    execution_assumptions.identity_id,
                    None,
                    None,
                    "OFF_TICK_PRICE",
                    capital_assumptions.identity_id,
                    **contract_fields,
                )
                return ForcedLiquidationOutcome(requirement, outcome, None)
            if contract.price_limit_rule_identity is not None:
                limit_fact = ChronologicalValidationRunner._visible_limit_fact(
                    price_limit_facts,
                    contract.identity_id,
                    contract.instrument_id,
                    trading_day,
                    contract.price_limit_rule_identity,
                    observation.available_at,
                )
                if not contract.is_on_tick(limit_fact.lower_price) or not contract.is_on_tick(limit_fact.upper_price):
                    raise ValueError("forced-liquidation price-limit bounds must conform to minimum tick")
                if limit_fact.locked or not (
                    limit_fact.lower_price <= observation.price <= limit_fact.upper_price
                    and limit_fact.lower_price <= fill_price <= limit_fact.upper_price
                ):
                    reason = "LOCKED_PRICE_LIMIT" if limit_fact.locked else "OUTSIDE_PRICE_LIMIT"
                    outcome = ExecutionOutcome(
                        requirement.request_id,
                        FillStatus.NOT_FILLED,
                        observation.available_at,
                        execution_assumptions.identity_id,
                        None,
                        None,
                        reason,
                        capital_assumptions.identity_id,
                        price_limit_fact_id=limit_fact.identity_id,
                        **contract_fields,
                    )
                    return ForcedLiquidationOutcome(requirement, outcome, None)
        pnl_sign = Decimal("1") if snapshot.position_direction is PositionDirection.LONG else Decimal("-1")
        realized_pnl_change = (
            (fill_price - snapshot.average_open_price)
            * snapshot.position_quantity
            * capital_assumptions.contract_multiplier
            * pnl_sign
        )
        outcome = ExecutionOutcome(
            requirement.request_id,
            FillStatus.FILLED,
            observation.available_at,
            execution_assumptions.identity_id,
            fill_price,
            execution_assumptions.synthetic_fee,
            "FORCED_LIQUIDATION_TRADABLE_OBSERVATION",
            capital_assumptions.identity_id,
            price_limit_fact_id=limit_fact.identity_id if limit_fact else None,
            **contract_fields,
        )
        next_snapshot = CapitalSnapshot(
            starting_capital=snapshot.starting_capital,
            charged_costs=snapshot.charged_costs + execution_assumptions.synthetic_fee,
            realized_pnl=snapshot.realized_pnl + realized_pnl_change,
            state_at=observation.available_at,
            latest_mark_reference=snapshot.latest_mark_reference,
        )
        transition = CapitalTransition(
            requirement.request_id,
            snapshot,
            next_snapshot,
            Decimal("0"),
            execution_assumptions.synthetic_fee,
            quantity_change=-snapshot.position_quantity,
            realized_pnl_change=realized_pnl_change,
            released_margin=snapshot.reserved_margin,
            transition_type="FORCED_LIQUIDATION",
        )
        return ForcedLiquidationOutcome(requirement, outcome, transition)

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
        hypothesis_test_id: str | None = None,
        synthetic_fixture: bool = False,
        execution_observations: Iterable[ExecutionObservation] = (),
        execution_cutoff_at: datetime | None = None,
        execution_assumptions: ExecutionAssumptions | None = None,
        order_specifications: Iterable[OrderSpecification] = (),
        capital_snapshot: CapitalSnapshot | None = None,
        capital_margin_assumptions: CapitalMarginAssumptions | None = None,
        mark_observations: Iterable[MarkObservation] = (),
        forced_liquidation_observations: Iterable[ExecutionObservation] = (),
        contract_master: ContractMaster | None = None,
        contract_mapping_schedule: ContractMappingSchedule | None = None,
        session_metadata: SessionMetadata | None = None,
        price_limit_facts: Iterable[PriceLimitFact] = (),
        offset_cost_assumptions: OffsetCostAssumptions | None = None,
        defer_confirmation: bool = False,
    ) -> ValidationRunResult:
        self._validate_binding(strategy, experiment, artifact_identity_id, artifact_code_hash)
        if mode is ValidationMode.FAST and disposition is ValidationDisposition.CONFIRMED:
            raise ValueError("FAST mode cannot establish confirmatory validity")
        if dataset_class is DatasetClass.FINAL_UNSEEN:
            access = self._firewall.legacy_request_access(experiment, dataset_class)
            return ValidationRunResult(False, (), access.record, None)
        inputs = tuple(inputs)
        order_specifications = tuple(order_specifications)
        price_limit_facts = tuple(price_limit_facts)
        contract_components = (contract_master, contract_mapping_schedule, session_metadata)
        contract_enabled = any(component is not None for component in contract_components)
        if contract_enabled and any(component is None for component in contract_components):
            raise ValueError("contract execution requires master, mapping schedule, and session metadata together")
        if mode is ValidationMode.CONFIRMATORY and disposition is ValidationDisposition.CONFIRMED:
            if execution_cutoff_at is None or execution_assumptions is None:
                raise ValueError("confirmatory validity requires execution assumptions and evaluation")
            if not inputs:
                raise ValueError("confirmatory validity requires at least one execution evaluation")
            if capital_snapshot is None or capital_margin_assumptions is None:
                raise ValueError("confirmatory validity requires capital/margin assumptions and snapshot")
            if capital_snapshot.position_quantity != 0:
                raise ValueError("initial offline capital snapshot must be flat; a position requires a valid fill")

        if mode is ValidationMode.FAST:
            # FAST remains a reject-only fixture / engine-sanity path. It uses the
            # same firewall's legacy coarse access (never a candidate grant) and
            # cannot establish CONFIRMED validity (guarded above).
            access = self._firewall.legacy_request_access(experiment, dataset_class)
        else:
            # CONFIRMATORY: the authoritative candidate pre-outcome gate.
            # F-05: bind every actual input to the experiment data version first.
            self._validate_data_version_binding(experiment, inputs)
            # F-04: the security cohort is derived from the actual input dates;
            # dataset_class is only a declaration used for consistency, never an
            # access authority.
            data_dates = tuple(item.bar.trading_day for item in inputs)
            derived_cohort = self._firewall.cohort_for_dates(data_dates)
            if derived_cohort is not Cohort.OUT_OF_SCOPE:
                if self._firewall.dataset_class_for_cohort(derived_cohort) is not dataset_class:
                    raise ValueError("caller dataset_class does not match the actual input data cohort")
            access = self._firewall.request_candidate_outcome_access(
                data_dates=data_dates,
                experiment=experiment,
                hypothesis_test_id=hypothesis_test_id,
                synthetic_fixture=synthetic_fixture,
            )
        if not access.allowed:
            return ValidationRunResult(False, (), access.record, None)

        events = self._ordered_events(inputs)
        execution_outcomes: tuple[ExecutionOutcome, ...] = ()
        capital_transitions: tuple[CapitalTransition, ...] = ()
        mark_transitions: tuple[MarkToMarketTransition, ...] = ()
        liquidation_requirement = None
        liquidation_outcome = None
        final_capital_snapshot = capital_snapshot
        contract_resolutions: tuple[ContractResolution, ...] = ()
        if mode is ValidationMode.CONFIRMATORY and disposition is ValidationDisposition.CONFIRMED:
            if contract_enabled:
                contract_resolutions = self._resolve_contracts(
                    inputs,
                    strategy,
                    contract_master,
                    contract_mapping_schedule,
                    session_metadata,
                    capital_margin_assumptions,
                )
                for resolution in contract_resolutions:
                    resolution_reference = (
                        f"contract:{resolution.contract_identity_id};master:{resolution.contract_master_identity_id};"
                        f"mapping_schedule:{resolution.mapping_schedule_identity_id};"
                        f"mapping_entry:{resolution.mapping_entry_identity_id}"
                    )
                    self._ledger.append(
                        EvidenceRecord(
                            "CONTRACT_RESOLVED",
                            experiment,
                            dataset_class,
                            resolution.concrete_instrument_id,
                            evidence_reference=resolution_reference,
                            fact_reference=resolution.identity_id,
                        )
                    )
                    events += (
                        ExecutionEvent(
                            resolution.resolved_at,
                            "CONTRACT_RESOLVED",
                            resolution.request_id,
                        ),
                    )
            execution_outcomes = self._evaluate_execution(
                inputs,
                execution_observations,
                execution_cutoff_at,
                execution_assumptions,
                order_specifications,
                contract_resolutions,
                contract_master,
                session_metadata,
                price_limit_facts,
            )
            execution_outcomes, capital_transitions = self._apply_capital_constraints(
                execution_outcomes,
                order_specifications,
                inputs,
                capital_snapshot,
                capital_margin_assumptions,
                execution_assumptions,
                contract_resolutions,
                offset_cost_assumptions,
                contract_master,
            )
            assumption_reference = f"execution:{execution_assumptions.identity_id};capital:{capital_margin_assumptions.identity_id}"
            if offset_cost_assumptions is not None:
                assumption_reference += f";offset_cost:{offset_cost_assumptions.identity_id}"
            contract_lifecycle_references: list[str] = []
            for outcome, transition in zip(execution_outcomes, capital_transitions):
                event_type = "EXECUTION_FILLED" if outcome.status is FillStatus.FILLED else "EXECUTION_NOT_FILLED"
                execution_reference = assumption_reference
                if outcome.contract_resolution_id is not None:
                    execution_reference += (
                        f";contract:{outcome.contract_identity_id};resolution:{outcome.contract_resolution_id};"
                        f"master:{outcome.contract_master_identity_id};"
                        f"mapping_schedule:{outcome.mapping_schedule_identity_id};"
                        f"mapping_entry:{outcome.mapping_entry_identity_id};"
                        f"limit:{outcome.price_limit_fact_id};close_offset:"
                        f"{outcome.resolved_close_offset.value if outcome.resolved_close_offset else None}"
                    )
                    contract_lifecycle_references.append(f"resolution:{outcome.contract_resolution_id}")
                self._ledger.append(
                    EvidenceRecord(
                        event_type,
                        experiment,
                        dataset_class,
                        outcome.reason,
                        evidence_reference=execution_reference,
                        fact_reference=outcome.reference_id,
                    )
                )
                events += (ExecutionEvent(outcome.evaluated_at, outcome.status.value, outcome.request_id),)
                if transition.quantity_change != 0:
                    self._ledger.append(
                        EvidenceRecord(
                            "POSITION_TRANSITION",
                            experiment,
                            dataset_class,
                            "CREATED_OR_INCREASED" if transition.quantity_change > 0 else "CLOSED_OR_REDUCED",
                            evidence_reference=execution_reference,
                            fact_reference=transition.reference_id,
                        )
                    )

            final_capital_snapshot = capital_transitions[-1].after if capital_transitions else capital_snapshot
            marks = tuple(mark_observations)
            liquidation_observations = tuple(forced_liquidation_observations)
            lifecycle_references: list[str] = []
            if marks:
                mark_transitions, liquidation_requirement = self._apply_marks(
                    marks,
                    final_capital_snapshot,
                    execution_cutoff_at,
                    capital_margin_assumptions,
                )
                for transition in mark_transitions:
                    mark_reference = f"{assumption_reference};mark:{transition.observation.reference_id};position:{transition.after.position_id}"
                    self._ledger.append(
                        EvidenceRecord(
                            "MARK_TO_MARKET",
                            experiment,
                            dataset_class,
                            "MARKED",
                            evidence_reference=mark_reference,
                            fact_reference=transition.reference_id,
                        )
                    )
                    margin_event = "MAINTENANCE_MARGIN_BREACH" if transition.breached else "MAINTENANCE_MARGIN_HEALTHY"
                    self._ledger.append(
                        EvidenceRecord(
                            margin_event,
                            experiment,
                            dataset_class,
                            "BREACHED" if transition.breached else "HEALTHY",
                            evidence_reference=mark_reference,
                            fact_reference=transition.reference_id,
                        )
                    )
                    events += (
                        ExecutionEvent(transition.observation.available_at, "MARK_TO_MARKET", transition.observation.observation_id),
                        ExecutionEvent(transition.observation.available_at, margin_event, transition.observation.observation_id),
                    )
                    lifecycle_references.append(f"mark:{transition.observation.reference_id}")
                final_capital_snapshot = mark_transitions[-1].after
            if liquidation_requirement is None and liquidation_observations:
                raise ValueError("forced-liquidation observation cannot exist without a maintenance breach")
            if liquidation_requirement is not None:
                requirement_reference = (
                    f"{assumption_reference};mark:{liquidation_requirement.mark_reference};"
                    f"position:{liquidation_requirement.position_id};requirement:{liquidation_requirement.reference_id}"
                )
                self._ledger.append(
                    EvidenceRecord(
                        "FORCED_LIQUIDATION_REQUIRED",
                        experiment,
                        dataset_class,
                        "REQUIRED",
                        evidence_reference=requirement_reference,
                        fact_reference=liquidation_requirement.reference_id,
                    )
                )
                events += (
                    ExecutionEvent(
                        liquidation_requirement.eligible_at,
                        "FORCED_LIQUIDATION_REQUIRED",
                        liquidation_requirement.request_id,
                    ),
                )
                liquidation_outcome = self._evaluate_forced_liquidation(
                    liquidation_requirement,
                    liquidation_observations,
                    final_capital_snapshot,
                    execution_cutoff_at,
                    execution_assumptions,
                    capital_margin_assumptions,
                    contract_master,
                    session_metadata,
                    price_limit_facts,
                )
                liquidation_event = (
                    "FORCED_LIQUIDATION_FILLED"
                    if liquidation_outcome.execution_outcome.status is FillStatus.FILLED
                    else "FORCED_LIQUIDATION_NOT_FILLED"
                )
                liquidation_reference = f"{requirement_reference};outcome:{liquidation_outcome.reference_id}"
                self._ledger.append(
                    EvidenceRecord(
                        liquidation_event,
                        experiment,
                        dataset_class,
                        liquidation_outcome.execution_outcome.reason,
                        evidence_reference=liquidation_reference,
                        fact_reference=liquidation_outcome.reference_id,
                    )
                )
                events += (
                    ExecutionEvent(
                        liquidation_outcome.execution_outcome.evaluated_at,
                        liquidation_event,
                        liquidation_requirement.request_id,
                    ),
                )
                lifecycle_references.append(f"liquidation:{liquidation_outcome.reference_id}")
                if liquidation_outcome.capital_transition is not None:
                    capital_transitions += (liquidation_outcome.capital_transition,)
                    final_capital_snapshot = liquidation_outcome.capital_transition.after
                    self._ledger.append(
                        EvidenceRecord(
                            "POSITION_TRANSITION",
                            experiment,
                            dataset_class,
                            "FORCED_LIQUIDATION_CLOSED",
                            evidence_reference=liquidation_reference,
                            fact_reference=liquidation_outcome.capital_transition.reference_id,
                        )
                    )
            if lifecycle_references:
                assumption_reference += ";" + ";".join(lifecycle_references)
            if contract_lifecycle_references:
                assumption_reference += ";" + ";".join(contract_lifecycle_references)
            events = tuple(sorted(events, key=lambda event: (event.timestamp, self._EVENT_ORDER[event.event_type], event.request_id)))
        validation_record = None
        if disposition is ValidationDisposition.REJECTED:
            validation_record = self._ledger.append(
                EvidenceRecord("VALIDATION_REJECTED", experiment, dataset_class, "REJECTED")
            )
        elif disposition is ValidationDisposition.CONFIRMED and not defer_confirmation:
            validation_record = self._ledger.append(EvidenceRecord("VALIDATION_CONFIRMED", experiment, dataset_class, "CONFIRMED", evidence_reference=assumption_reference))
        return ValidationRunResult(
            True,
            events,
            access.record,
            validation_record,
            execution_outcomes,
            capital_transitions,
            mark_transitions,
            liquidation_requirement,
            liquidation_outcome,
            final_capital_snapshot,
            contract_resolutions,
        )

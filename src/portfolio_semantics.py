"""Deterministic offline multi-strategy portfolio coordination semantics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Iterable

from src.contract_semantics import (
    ContractMappingSchedule,
    ContractMaster,
    ContractResolution,
    ContractResolver,
    OffsetCostAssumptions,
    OrderAction,
    PositionDirection,
    PriceLimitFact,
)
from src.data_substrate import SessionMetadata
from src.strategy_evidence import (
    DatasetClass,
    EvidenceLedger,
    EvidenceRecord,
    ExperimentIdentity,
    FinalUnseenFirewall,
    StrategyIdentity,
)
from src.validation_runner import (
    CapitalMarginAssumptions,
    CapitalTransition,
    ExecutionAssumptions,
    ExecutionObservation,
    ExecutionOutcome,
    FillStatus,
    OrderSpecification,
    ValidationInput,
    ValidationMode,
)


def _portfolio_hash(value: object) -> str:
    encoded = json.dumps(value, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PortfolioMember:
    strategy: StrategyIdentity
    experiment: ExperimentIdentity

    def __post_init__(self) -> None:
        self.experiment.validate_strategy(self.strategy)

    @property
    def binding(self) -> tuple[str, str]:
        return self.strategy.identity_id, self.experiment.experiment_id


@dataclass(frozen=True)
class PortfolioConflictPolicy:
    policy_version: str
    simultaneous_order_rule: str = "STRATEGY_ID_THEN_REQUEST_ID"
    opposing_open_rule: str = "FIRST_DIRECTION_WINS"
    same_direction_rule: str = "ALLOW_SEPARATE"
    duplicate_request_rule: str = "FAIL_CLOSED"
    shared_capital_order_rule: str = "ARBITRATION_ORDER"
    strategy_attribution_rule: str = "SEPARATE_SLEEVES"

    def __post_init__(self) -> None:
        expected = (
            self.simultaneous_order_rule == "STRATEGY_ID_THEN_REQUEST_ID",
            self.opposing_open_rule == "FIRST_DIRECTION_WINS",
            self.same_direction_rule == "ALLOW_SEPARATE",
            self.duplicate_request_rule == "FAIL_CLOSED",
            self.shared_capital_order_rule == "ARBITRATION_ORDER",
            self.strategy_attribution_rule == "SEPARATE_SLEEVES",
        )
        if not self.policy_version or not all(expected):
            raise ValueError("unsupported or incomplete synthetic portfolio conflict policy")

    @property
    def identity_id(self) -> str:
        return _portfolio_hash(
            {
                "policy_version": self.policy_version,
                "simultaneous_order_rule": self.simultaneous_order_rule,
                "opposing_open_rule": self.opposing_open_rule,
                "same_direction_rule": self.same_direction_rule,
                "duplicate_request_rule": self.duplicate_request_rule,
                "shared_capital_order_rule": self.shared_capital_order_rule,
                "strategy_attribution_rule": self.strategy_attribution_rule,
            }
        )


@dataclass(frozen=True)
class SharedCapitalPolicy:
    policy_version: str
    allocation_rule: str = "SEQUENTIAL_AVAILABLE_CAPITAL"
    consumption_rule: str = "RESERVED_MARGIN_PLUS_COST"

    def __post_init__(self) -> None:
        if (
            not self.policy_version
            or self.allocation_rule != "SEQUENTIAL_AVAILABLE_CAPITAL"
            or self.consumption_rule != "RESERVED_MARGIN_PLUS_COST"
        ):
            raise ValueError("unsupported or incomplete synthetic shared-capital policy")

    @property
    def identity_id(self) -> str:
        return _portfolio_hash(
            {
                "policy_version": self.policy_version,
                "allocation_rule": self.allocation_rule,
                "consumption_rule": self.consumption_rule,
            }
        )


@dataclass(frozen=True, init=False)
class PortfolioEvaluationBindings:
    dataset_class: DatasetClass
    contract_master_identity_id: str
    mapping_schedule_identity_id: str
    session_metadata_version: str
    execution_assumption_id: str
    capital_binding_ids: tuple[str, ...]
    price_limit_fact_ids: tuple[str, ...]
    offset_cost_assumption_id: str

    def __init__(
        self,
        dataset_class: DatasetClass,
        contract_master_identity_id: str,
        mapping_schedule_identity_id: str,
        session_metadata_version: str,
        execution_assumption_id: str,
        capital_binding_ids: Iterable[str],
        price_limit_fact_ids: Iterable[str],
        offset_cost_assumption_id: str,
    ) -> None:
        required = (
            contract_master_identity_id,
            mapping_schedule_identity_id,
            session_metadata_version,
            execution_assumption_id,
            offset_cost_assumption_id,
        )
        capital_bindings = tuple(sorted(capital_binding_ids))
        facts = tuple(sorted(price_limit_fact_ids))
        if not isinstance(dataset_class, DatasetClass) or not all(required) or any(not fact for fact in facts):
            raise ValueError("portfolio evaluation requires complete existing assumption bindings")
        if not capital_bindings or any(not item for item in capital_bindings):
            raise ValueError("portfolio evaluation requires non-empty capital bindings")
        if len(set(capital_bindings)) != len(capital_bindings):
            raise ValueError("portfolio capital binding identities must be unique")
        if len(set(facts)) != len(facts):
            raise ValueError("portfolio price-limit fact identities must be unique")
        object.__setattr__(self, "dataset_class", dataset_class)
        object.__setattr__(self, "contract_master_identity_id", contract_master_identity_id)
        object.__setattr__(self, "mapping_schedule_identity_id", mapping_schedule_identity_id)
        object.__setattr__(self, "session_metadata_version", session_metadata_version)
        object.__setattr__(self, "execution_assumption_id", execution_assumption_id)
        object.__setattr__(self, "capital_binding_ids", capital_bindings)
        object.__setattr__(self, "price_limit_fact_ids", facts)
        object.__setattr__(self, "offset_cost_assumption_id", offset_cost_assumption_id)

    @property
    def identity_id(self) -> str:
        return _portfolio_hash(
            {
                "dataset_class": self.dataset_class.value,
                "contract_master_identity_id": self.contract_master_identity_id,
                "mapping_schedule_identity_id": self.mapping_schedule_identity_id,
                "session_metadata_version": self.session_metadata_version,
                "execution_assumption_id": self.execution_assumption_id,
                "capital_binding_ids": self.capital_binding_ids,
                "price_limit_fact_ids": self.price_limit_fact_ids,
                "offset_cost_assumption_id": self.offset_cost_assumption_id,
            }
        )


@dataclass(frozen=True)
class PortfolioEvaluationIdentity:
    member_bindings: tuple[tuple[str, str], ...]
    conflict_policy_identity_id: str
    shared_capital_policy_identity_id: str
    evaluation_bindings_identity_id: str

    def __post_init__(self) -> None:
        required = (
            self.conflict_policy_identity_id,
            self.shared_capital_policy_identity_id,
            self.evaluation_bindings_identity_id,
        )
        strategy_ids = tuple(item[0] for item in self.member_bindings)
        experiment_ids = tuple(item[1] for item in self.member_bindings)
        if (
            len(self.member_bindings) < 2
            or self.member_bindings != tuple(sorted(self.member_bindings))
            or any(not all(item) for item in self.member_bindings)
            or len(set(strategy_ids)) != len(strategy_ids)
            or len(set(experiment_ids)) != len(experiment_ids)
            or not all(required)
        ):
            raise ValueError("portfolio evaluation identity has invalid or duplicate member bindings")

    @classmethod
    def create(
        cls,
        members: Iterable[PortfolioMember],
        conflict_policy: PortfolioConflictPolicy,
        shared_capital_policy: SharedCapitalPolicy,
        bindings: PortfolioEvaluationBindings,
    ) -> "PortfolioEvaluationIdentity":
        ordered = tuple(sorted((member.binding for member in members)))
        if len(ordered) < 2:
            raise ValueError("portfolio evaluation requires at least two strategy members")
        strategy_ids = tuple(item[0] for item in ordered)
        experiment_ids = tuple(item[1] for item in ordered)
        if len(set(strategy_ids)) != len(strategy_ids) or len(set(experiment_ids)) != len(experiment_ids):
            raise ValueError("duplicate strategy or experiment portfolio membership")
        return cls(
            ordered,
            conflict_policy.identity_id,
            shared_capital_policy.identity_id,
            bindings.identity_id,
        )

    @property
    def identity_id(self) -> str:
        return _portfolio_hash(
            {
                "member_bindings": self.member_bindings,
                "conflict_policy_identity_id": self.conflict_policy_identity_id,
                "shared_capital_policy_identity_id": self.shared_capital_policy_identity_id,
                "evaluation_bindings_identity_id": self.evaluation_bindings_identity_id,
            }
        )


class CandidateDecision(str, Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED_CONFLICT = "REJECTED_CONFLICT"


@dataclass(frozen=True)
class PortfolioCandidate:
    strategy_identity_id: str
    experiment_id: str
    validation_input: ValidationInput
    order_specification: OrderSpecification
    execution_observation: ExecutionObservation | None
    direction: PositionDirection
    execution_assumption_id: str
    capital_assumption_id: str

    def __post_init__(self) -> None:
        required = (
            self.strategy_identity_id,
            self.experiment_id,
            self.execution_assumption_id,
            self.capital_assumption_id,
        )
        if not all(required):
            raise ValueError("portfolio candidate requires complete strategy and assumption attribution")
        request_ids = [
            self.validation_input.request_id,
            self.order_specification.request_id,
        ]
        if self.execution_observation is not None:
            request_ids.append(self.execution_observation.request_id)
        if len(set(request_ids)) != 1:
            raise ValueError("portfolio candidate request identities must agree")
        if self.order_specification.action is not OrderAction.OPEN:
            raise ValueError("the minimum portfolio coordination path accepts opening candidates only")
        if self.order_specification.direction is not self.direction:
            raise ValueError("portfolio candidate direction must match its attributed order")
        if not isinstance(self.direction, PositionDirection):
            raise ValueError("portfolio candidate requires an explicit position direction")

    @property
    def request_id(self) -> str:
        return self.validation_input.request_id

    @property
    def decision_at(self) -> datetime:
        return self.validation_input.decision_at

    @property
    def requested_symbol(self) -> str:
        return self.validation_input.bar.instrument


@dataclass(frozen=True)
class PortfolioCapitalBinding:
    """Per-member, per-resolved-concrete-contract capital assumptions binding.

    E-05: capital/margin assumptions are bound to the resolved concrete
    contract of a specific portfolio member. There is no global multiplier, no
    unconstrained multiplier-map fallback, and no default/first-assumption
    backdoor.
    """

    strategy_identity_id: str
    concrete_contract_id: str
    capital_assumptions: CapitalMarginAssumptions

    def __post_init__(self) -> None:
        if not self.strategy_identity_id or not self.concrete_contract_id:
            raise ValueError("portfolio capital binding requires strategy and concrete contract attribution")
        if not isinstance(self.capital_assumptions, CapitalMarginAssumptions):
            raise ValueError("portfolio capital binding requires explicit capital margin assumptions")

    @property
    def key(self) -> tuple[str, str]:
        return (self.strategy_identity_id, self.concrete_contract_id)

    @property
    def identity_id(self) -> str:
        return _portfolio_hash(
            {
                "strategy_identity_id": self.strategy_identity_id,
                "concrete_contract_id": self.concrete_contract_id,
                "capital_assumptions_identity_id": self.capital_assumptions.identity_id,
            }
        )


@dataclass(frozen=True)
class PortfolioRequest:
    mode: ValidationMode
    dataset_class: DatasetClass
    members: tuple[PortfolioMember, ...]
    candidates: tuple[PortfolioCandidate, ...]
    starting_capital: Decimal
    conflict_policy: PortfolioConflictPolicy
    shared_capital_policy: SharedCapitalPolicy
    contract_master: ContractMaster
    contract_mapping_schedule: ContractMappingSchedule
    session_metadata: SessionMetadata
    price_limit_facts: tuple[PriceLimitFact, ...]
    execution_assumptions: ExecutionAssumptions
    capital_bindings: tuple[PortfolioCapitalBinding, ...]
    offset_cost_assumptions: OffsetCostAssumptions
    execution_cutoff_at: datetime

    def __post_init__(self) -> None:
        if type(self.starting_capital) is not Decimal or self.starting_capital <= 0:
            raise ValueError("portfolio starting capital must be a positive Decimal")
        if self.execution_cutoff_at.tzinfo is None:
            raise ValueError("portfolio execution cutoff must be timezone-aware")
        if not self.candidates:
            raise ValueError("portfolio evaluation requires at least one attributed candidate")
        if not self.capital_bindings:
            raise ValueError("portfolio evaluation requires at least one capital binding")
        if self.capital_bindings != tuple(sorted(self.capital_bindings, key=lambda item: item.key)):
            raise ValueError("portfolio capital bindings must be canonical sorted")
        binding_keys = tuple(item.key for item in self.capital_bindings)
        if len(set(binding_keys)) != len(binding_keys):
            raise ValueError("portfolio capital bindings must be unique by strategy and concrete contract")
        member_strategy_ids = {member.strategy.identity_id for member in self.members}
        bound_strategy_ids = {item.strategy_identity_id for item in self.capital_bindings}
        if not member_strategy_ids.issubset(bound_strategy_ids):
            raise ValueError("every portfolio member requires at least one capital binding (no global fallback)")

    @property
    def bindings(self) -> PortfolioEvaluationBindings:
        return PortfolioEvaluationBindings(
            self.dataset_class,
            self.contract_master.identity_id,
            self.contract_mapping_schedule.identity_id,
            self.session_metadata.version,
            self.execution_assumptions.identity_id,
            (item.identity_id for item in self.capital_bindings),
            (fact.identity_id for fact in self.price_limit_facts),
            self.offset_cost_assumptions.identity_id,
        )


@dataclass(frozen=True)
class PortfolioConflict:
    decision_at: datetime
    concrete_contract_id: str
    accepted_request_ids: tuple[str, ...]
    rejected_request_ids: tuple[str, ...]
    policy_identity_id: str

    def __post_init__(self) -> None:
        all_requests = self.accepted_request_ids + self.rejected_request_ids
        if (
            self.decision_at.tzinfo is None
            or not self.concrete_contract_id
            or not self.policy_identity_id
            or not self.accepted_request_ids
            or not self.rejected_request_ids
            or len(set(all_requests)) != len(all_requests)
        ):
            raise ValueError("portfolio conflict requires disjoint accepted and rejected attribution")

    @property
    def reference_id(self) -> str:
        return _portfolio_hash(
            {
                "decision_at": self.decision_at.isoformat(),
                "concrete_contract_id": self.concrete_contract_id,
                "accepted_request_ids": self.accepted_request_ids,
                "rejected_request_ids": self.rejected_request_ids,
                "policy_identity_id": self.policy_identity_id,
            }
        )


@dataclass(frozen=True)
class CandidateOutcome:
    strategy_identity_id: str
    experiment_id: str
    request_id: str
    direction: PositionDirection
    decision: CandidateDecision
    reason: str
    resolution: ContractResolution
    execution_outcome: ExecutionOutcome | None = None
    capital_transition: CapitalTransition | None = None

    def __post_init__(self) -> None:
        required = (self.strategy_identity_id, self.experiment_id, self.request_id, self.reason)
        if not all(required) or self.resolution.request_id != self.request_id:
            raise ValueError("portfolio candidate outcome has incomplete attribution")
        if self.execution_outcome is not None and self.execution_outcome.request_id != self.request_id:
            raise ValueError("portfolio execution outcome request attribution mismatch")
        if self.capital_transition is not None and self.capital_transition.request_id != self.request_id:
            raise ValueError("portfolio capital transition request attribution mismatch")
        if self.decision is CandidateDecision.REJECTED_CONFLICT:
            if self.execution_outcome is not None or self.capital_transition is not None:
                raise ValueError("a rejected portfolio candidate cannot reach execution or capital mutation")
        elif self.execution_outcome is None or self.capital_transition is None:
            raise ValueError("an accepted portfolio candidate requires an attributed execution evaluation")

    @property
    def reference_id(self) -> str:
        return _portfolio_hash(
            {
                "strategy_identity_id": self.strategy_identity_id,
                "experiment_id": self.experiment_id,
                "request_id": self.request_id,
                "direction": self.direction.value,
                "decision": self.decision.value,
                "reason": self.reason,
                "resolution": self.resolution.identity_id,
                "execution_outcome": (
                    self.execution_outcome.reference_id if self.execution_outcome else None
                ),
                "capital_transition": (
                    self.capital_transition.reference_id if self.capital_transition else None
                ),
            }
        )


@dataclass(frozen=True)
class AttributedPosition:
    strategy_identity_id: str
    experiment_id: str
    request_id: str
    concrete_contract_id: str
    contract_identity_id: str
    direction: PositionDirection
    quantity: Decimal
    reserved_margin: Decimal
    charged_costs: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    execution_assumption_id: str
    capital_assumption_id: str
    snapshot_reference_id: str

    def __post_init__(self) -> None:
        required = (
            self.strategy_identity_id,
            self.experiment_id,
            self.request_id,
            self.concrete_contract_id,
            self.contract_identity_id,
            self.execution_assumption_id,
            self.capital_assumption_id,
            self.snapshot_reference_id,
        )
        decimals = (
            self.quantity,
            self.reserved_margin,
            self.charged_costs,
            self.realized_pnl,
            self.unrealized_pnl,
        )
        if not all(required) or not isinstance(self.direction, PositionDirection):
            raise ValueError("portfolio position requires complete strategy and contract attribution")
        if any(type(value) is not Decimal for value in decimals):
            raise ValueError("portfolio position accounting must use Decimal arithmetic")
        if self.quantity <= 0 or self.reserved_margin < 0 or self.charged_costs < 0:
            raise ValueError("portfolio position quantity and consumed resources cannot be negative")

    @property
    def reference_id(self) -> str:
        return _portfolio_hash(
            {
                "strategy_identity_id": self.strategy_identity_id,
                "experiment_id": self.experiment_id,
                "request_id": self.request_id,
                "concrete_contract_id": self.concrete_contract_id,
                "contract_identity_id": self.contract_identity_id,
                "direction": self.direction.value,
                "quantity": str(self.quantity),
                "reserved_margin": str(self.reserved_margin),
                "charged_costs": str(self.charged_costs),
                "realized_pnl": str(self.realized_pnl),
                "unrealized_pnl": str(self.unrealized_pnl),
                "execution_assumption_id": self.execution_assumption_id,
                "capital_assumption_id": self.capital_assumption_id,
                "snapshot_reference_id": self.snapshot_reference_id,
            }
        )


@dataclass(frozen=True)
class StrategySleeve:
    strategy_identity_id: str
    experiment_id: str
    positions: tuple[AttributedPosition, ...]
    reserved_margin: Decimal
    charged_costs: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal

    def __post_init__(self) -> None:
        if not self.strategy_identity_id or not self.experiment_id:
            raise ValueError("strategy sleeve requires strategy and experiment attribution")
        if any(
            position.strategy_identity_id != self.strategy_identity_id
            or position.experiment_id != self.experiment_id
            for position in self.positions
        ):
            raise ValueError("a strategy sleeve cannot receive another strategy's position")
        request_ids = tuple(position.request_id for position in self.positions)
        expected = (
            sum((item.reserved_margin for item in self.positions), Decimal("0")),
            sum((item.charged_costs for item in self.positions), Decimal("0")),
            sum((item.realized_pnl for item in self.positions), Decimal("0")),
            sum((item.unrealized_pnl for item in self.positions), Decimal("0")),
        )
        if len(set(request_ids)) != len(request_ids) or (
            self.reserved_margin,
            self.charged_costs,
            self.realized_pnl,
            self.unrealized_pnl,
        ) != expected:
            raise ValueError("strategy sleeve totals must reconcile to its attributed positions")

    @classmethod
    def from_positions(
        cls,
        strategy_identity_id: str,
        experiment_id: str,
        positions: Iterable[AttributedPosition],
    ) -> "StrategySleeve":
        ordered = tuple(sorted(positions, key=lambda item: item.request_id))
        return cls(
            strategy_identity_id,
            experiment_id,
            ordered,
            sum((item.reserved_margin for item in ordered), Decimal("0")),
            sum((item.charged_costs for item in ordered), Decimal("0")),
            sum((item.realized_pnl for item in ordered), Decimal("0")),
            sum((item.unrealized_pnl for item in ordered), Decimal("0")),
        )


@dataclass(frozen=True)
class SharedCapitalState:
    starting_capital: Decimal
    reserved_margin: Decimal = Decimal("0")
    charged_costs: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")
    unrealized_pnl: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        values = (
            self.starting_capital,
            self.reserved_margin,
            self.charged_costs,
            self.realized_pnl,
            self.unrealized_pnl,
        )
        if any(type(value) is not Decimal for value in values):
            raise ValueError("shared portfolio capital values must use Decimal arithmetic")
        if self.starting_capital <= 0 or self.reserved_margin < 0 or self.charged_costs < 0:
            raise ValueError("shared portfolio capital cannot be non-positive or over-released")
        if self.available_capital < 0:
            raise ValueError("shared portfolio capital cannot be spent twice")

    @property
    def available_capital(self) -> Decimal:
        return self.starting_capital + self.realized_pnl - self.reserved_margin - self.charged_costs


@dataclass(frozen=True)
class PortfolioReconciliation:
    shared_reserved_margin: Decimal
    sleeve_reserved_margin: Decimal
    shared_charged_costs: Decimal
    sleeve_charged_costs: Decimal
    shared_realized_pnl: Decimal
    sleeve_realized_pnl: Decimal
    shared_unrealized_pnl: Decimal
    sleeve_unrealized_pnl: Decimal
    position_count: int

    def __post_init__(self) -> None:
        pairs = (
            (self.shared_reserved_margin, self.sleeve_reserved_margin),
            (self.shared_charged_costs, self.sleeve_charged_costs),
            (self.shared_realized_pnl, self.sleeve_realized_pnl),
            (self.shared_unrealized_pnl, self.sleeve_unrealized_pnl),
        )
        if any(type(value) is not Decimal for pair in pairs for value in pair):
            raise ValueError("portfolio reconciliation values must use Decimal arithmetic")
        if any(left != right for left, right in pairs) or self.position_count < 0:
            raise ValueError("portfolio reconciliation cannot represent mismatched totals")

    @property
    def reference_id(self) -> str:
        return _portfolio_hash(
            {
                "shared_reserved_margin": str(self.shared_reserved_margin),
                "sleeve_reserved_margin": str(self.sleeve_reserved_margin),
                "shared_charged_costs": str(self.shared_charged_costs),
                "sleeve_charged_costs": str(self.sleeve_charged_costs),
                "shared_realized_pnl": str(self.shared_realized_pnl),
                "sleeve_realized_pnl": str(self.sleeve_realized_pnl),
                "shared_unrealized_pnl": str(self.shared_unrealized_pnl),
                "sleeve_unrealized_pnl": str(self.sleeve_unrealized_pnl),
                "position_count": self.position_count,
            }
        )


def reconcile_portfolio(
    state: SharedCapitalState,
    sleeves: Iterable[StrategySleeve],
    outcomes: Iterable[CandidateOutcome],
) -> PortfolioReconciliation:
    sleeves = tuple(sleeves)
    outcomes = tuple(outcomes)
    positions = tuple(position for sleeve in sleeves for position in sleeve.positions)
    outcome_requests = tuple(outcome.request_id for outcome in outcomes)
    if len(set(outcome_requests)) != len(outcome_requests):
        raise ValueError("a portfolio candidate request cannot appear more than once")
    totals = (
        sum((sleeve.reserved_margin for sleeve in sleeves), Decimal("0")),
        sum((sleeve.charged_costs for sleeve in sleeves), Decimal("0")),
        sum((sleeve.realized_pnl for sleeve in sleeves), Decimal("0")),
        sum((sleeve.unrealized_pnl for sleeve in sleeves), Decimal("0")),
    )
    if (state.reserved_margin, state.charged_costs, state.realized_pnl, state.unrealized_pnl) != totals:
        raise ValueError("shared capital does not reconcile to strategy-attributed sleeves")
    position_requests = {position.request_id for position in positions}
    if len(position_requests) != len(positions):
        raise ValueError("a portfolio position request cannot be attributed twice")
    for outcome in outcomes:
        filled = outcome.execution_outcome is not None and outcome.execution_outcome.status is FillStatus.FILLED
        if outcome.decision is CandidateDecision.REJECTED_CONFLICT and filled:
            raise ValueError("a rejected portfolio candidate cannot also be filled")
        if filled != (outcome.request_id in position_requests):
            raise ValueError("every portfolio fill must have exactly one attributed position")
    return PortfolioReconciliation(
        state.reserved_margin,
        totals[0],
        state.charged_costs,
        totals[1],
        state.realized_pnl,
        totals[2],
        state.unrealized_pnl,
        totals[3],
        len(positions),
    )


@dataclass(frozen=True)
class PortfolioEvaluationResult:
    allowed: bool
    confirmed: bool
    evaluation_identity: PortfolioEvaluationIdentity
    candidate_outcomes: tuple[CandidateOutcome, ...]
    conflicts: tuple[PortfolioConflict, ...]
    sleeves: tuple[StrategySleeve, ...]
    shared_capital: SharedCapitalState
    reconciliation: PortfolioReconciliation | None

    def __post_init__(self) -> None:
        if self.confirmed and (not self.allowed or self.reconciliation is None):
            raise ValueError("portfolio confirmation requires access and completed reconciliation")
        if not self.allowed and (
            self.confirmed or self.candidate_outcomes or self.conflicts or self.sleeves
        ):
            raise ValueError("a denied portfolio evaluation cannot expose execution results")


@dataclass(frozen=True)
class _ResolvedCandidate:
    candidate: PortfolioCandidate
    member: PortfolioMember
    resolution: ContractResolution


class PortfolioCoordinator:
    """Deep module for deterministic offline portfolio coordination."""

    def __init__(self, ledger: EvidenceLedger, firewall: FinalUnseenFirewall) -> None:
        self._ledger = ledger
        self._firewall = firewall

    def _record(
        self,
        event_type: str,
        member: PortfolioMember,
        dataset_class: DatasetClass,
        outcome: str,
        evidence_reference: str,
        fact_reference: str,
    ) -> None:
        self._ledger.append(
            EvidenceRecord(
                event_type,
                member.experiment,
                dataset_class,
                outcome,
                evidence_reference=evidence_reference,
                fact_reference=fact_reference,
            )
        )

    @staticmethod
    def _members_by_strategy(
        members: tuple[PortfolioMember, ...],
    ) -> dict[str, PortfolioMember]:
        return {member.strategy.identity_id: member for member in members}

    @staticmethod
    def _resolve_candidates(
        request: PortfolioRequest,
        members_by_strategy: dict[str, PortfolioMember],
    ) -> tuple[_ResolvedCandidate, ...]:
        request_ids = tuple(candidate.request_id for candidate in request.candidates)
        if len(set(request_ids)) != len(request_ids):
            raise ValueError("duplicate portfolio request ownership")
        resolver = ContractResolver(request.contract_master, request.contract_mapping_schedule)
        bindings_by_key = {item.key: item for item in request.capital_bindings}
        resolved: list[_ResolvedCandidate] = []
        for candidate in request.candidates:
            # 1. find member
            member = members_by_strategy.get(candidate.strategy_identity_id)
            if member is None or member.experiment.experiment_id != candidate.experiment_id:
                raise ValueError("portfolio candidate has ambiguous or inconsistent strategy attribution")
            if candidate.execution_assumption_id != request.execution_assumptions.identity_id:
                raise ValueError("portfolio candidate execution assumption identity mismatch")
            if candidate.requested_symbol not in member.strategy.applicable_instruments:
                raise ValueError("portfolio candidate symbol is not bound to its originating strategy")
            # 2. resolve concrete contract first
            resolution = resolver.resolve(
                candidate.request_id,
                candidate.requested_symbol,
                candidate.decision_at,
            )
            # 3. find the unique binding for this member + resolved contract
            binding = bindings_by_key.get(
                (candidate.strategy_identity_id, resolution.concrete_instrument_id)
            )
            if binding is None:
                raise ValueError("portfolio candidate has no capital binding for its resolved concrete contract")
            # 4. candidate capital assumption identity must equal the binding's
            contract = request.contract_master.get(resolution.concrete_instrument_id)
            if contract is None:
                raise ValueError("portfolio resolved concrete contract is missing from the contract master")
            if candidate.capital_assumption_id != binding.capital_assumptions.identity_id:
                raise ValueError("portfolio candidate capital assumption identity mismatch")
            # 5. resolved contract multiplier must equal the binding's assumptions
            if contract.contract_multiplier != binding.capital_assumptions.contract_multiplier:
                raise ValueError("portfolio contract multiplier is inconsistent with capital assumptions")
            trading_day = request.session_metadata.trading_day_at(
                contract.exchange,
                contract.instrument_id,
                candidate.decision_at,
            )
            if trading_day != candidate.validation_input.bar.trading_day:
                raise ValueError("portfolio candidate trading day is inconsistent with session metadata")
            resolved.append(_ResolvedCandidate(candidate, member, resolution))
        return tuple(
            sorted(
                resolved,
                key=lambda item: (
                    item.candidate.decision_at,
                    item.candidate.strategy_identity_id,
                    item.candidate.request_id,
                ),
            )
        )

    @staticmethod
    def _arbitrate(
        resolved: tuple[_ResolvedCandidate, ...],
        policy: PortfolioConflictPolicy,
    ) -> tuple[dict[str, CandidateDecision], tuple[PortfolioConflict, ...]]:
        decisions = {item.candidate.request_id: CandidateDecision.ACCEPTED for item in resolved}
        groups: dict[tuple[datetime, str], list[_ResolvedCandidate]] = {}
        for item in resolved:
            groups.setdefault(
                (item.candidate.decision_at, item.resolution.concrete_instrument_id),
                [],
            ).append(item)
        conflicts: list[PortfolioConflict] = []
        for (decision_at, concrete_contract_id), group in sorted(groups.items()):
            directions = {item.candidate.direction for item in group}
            if len(directions) <= 1:
                continue
            winning_direction = group[0].candidate.direction
            accepted = tuple(
                item.candidate.request_id
                for item in group
                if item.candidate.direction is winning_direction
            )
            rejected = tuple(
                item.candidate.request_id
                for item in group
                if item.candidate.direction is not winning_direction
            )
            for request_id in rejected:
                decisions[request_id] = CandidateDecision.REJECTED_CONFLICT
            conflicts.append(
                PortfolioConflict(
                    decision_at,
                    concrete_contract_id,
                    accepted,
                    rejected,
                    policy.identity_id,
                )
            )
        return decisions, tuple(conflicts)

    def evaluate(self, request: PortfolioRequest) -> PortfolioEvaluationResult:
        if request.mode is not ValidationMode.CONFIRMATORY:
            raise ValueError("FAST portfolio evaluation remains reject-only and cannot confirm")
        evaluation_identity = PortfolioEvaluationIdentity.create(
            request.members,
            request.conflict_policy,
            request.shared_capital_policy,
            request.bindings,
        )
        members = tuple(sorted(request.members, key=lambda item: item.strategy.identity_id))
        members_by_strategy = self._members_by_strategy(members)
        # Structural request validation still fails closed with its precise cause.
        self._resolve_candidates(request, members_by_strategy)
        # Package A: the CONFIRMATORY portfolio candidate-outcome path is closed.
        # There is no identity-bound portfolio candidate authority yet, and the
        # legacy coarse-grant route is a removed bypass. Fail closed before any
        # execution / candidate outcome / reconciliation-confirmed record exists.
        raise ValueError("PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED")

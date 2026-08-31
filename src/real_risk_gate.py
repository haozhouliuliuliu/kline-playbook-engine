"""Deterministic REAL risk gate (decision-only, fail-closed).

This module owns the *decision* side of the REAL risk/safety primitives. It
consumes a bound ``RealRiskPolicy``, the current ``RealSafetyState`` and one
bundle of runtime facts (current/proposed position, account cash/margin/headroom,
proposed stop/invalidation risk, realized/unrealized/daily/drawdown facts,
duplicate/unresolved orders, reconciliation/market/provider/broker health,
external mutation, kill switch, no-new-risk) and returns a deterministic,
reason-coded decision:

- action classification ``RISK_INCREASING`` / ``RISK_REDUCING`` / ``NEUTRAL`` /
  ``UNKNOWN``;
- decision ``ALLOW`` / ``DENY`` / ``INSUFFICIENT_OR_UNKNOWN``.

Fail-closed rules:
- risk increase is denied when any required binding is UNBOUND, the product or
  contract is not authorized, a ceiling is exceeded or unprovable, add-on is not
  explicitly allowed, margin/headroom is unproven, an order is unresolved,
  reconciliation/market/provider/broker health is UNHEALTHY or UNKNOWN, an
  external/manual mutation is unresolved, the kill switch is tripped, or
  no-new-risk is active;
- there is no blanket "close always allowed": an action is only classified
  RISK_REDUCING when broker/account/position identity, direction and quantity
  are sufficiently known and the resulting exposure is demonstrably lower;
- UNKNOWN truth fails closed (INSUFFICIENT_OR_UNKNOWN / DENY), never ALLOW;
- KILL and UNKNOWN safety modes never allow risk increase.

This gate only returns decisions. It never places an order or contacts any
broker, provider, account or external system.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Any

from src.contract_semantics import PositionDirection
from src.real_risk_policy import BindingStatus, PolicyBinding, RealRiskPolicy
from src.real_safety_state import (
    ExternalMutationStatus,
    HealthState,
    RealSafetyState,
    SafetyMode,
)

REAL_RISK_GATE_SCHEMA_VERSION = "real-risk-gate-v0.1"


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class ProposedAction(str, Enum):
    """Explicit proposed action (UNKNOWN fails closed)."""

    OPEN = "OPEN"
    CLOSE = "CLOSE"
    HOLD = "HOLD"
    UNKNOWN = "UNKNOWN"


class ActionRiskClassification(str, Enum):
    """Deterministic risk classification of the proposed action."""

    RISK_INCREASING = "RISK_INCREASING"
    RISK_REDUCING = "RISK_REDUCING"
    NEUTRAL = "NEUTRAL"
    UNKNOWN = "UNKNOWN"


class RiskDecision(str, Enum):
    """Deterministic gate decision (UNKNOWN truth never ALLOWs)."""

    ALLOW = "ALLOW"
    DENY = "DENY"
    INSUFFICIENT_OR_UNKNOWN = "INSUFFICIENT_OR_UNKNOWN"


class ReasonCode(str, Enum):
    """Structured, stable reason-code vocabulary."""

    ALLOWED = "ALLOWED"
    NEUTRAL_NO_RISK = "NEUTRAL_NO_RISK"
    ACTION_CLASSIFICATION_UNKNOWN = "ACTION_CLASSIFICATION_UNKNOWN"
    KILL_SWITCH_TRIPPED = "KILL_SWITCH_TRIPPED"
    SAFETY_MODE_UNKNOWN = "SAFETY_MODE_UNKNOWN"
    NO_NEW_RISK_ACTIVE = "NO_NEW_RISK_ACTIVE"
    HARD_INCONSISTENCY_LATCHED = "HARD_INCONSISTENCY_LATCHED"
    EXTERNAL_MUTATION_UNRESOLVED = "EXTERNAL_MUTATION_UNRESOLVED"
    EXTERNAL_MUTATION_UNKNOWN = "EXTERNAL_MUTATION_UNKNOWN"
    UNRESOLVED_ORDER = "UNRESOLVED_ORDER"
    UNRESOLVED_ORDER_UNKNOWN = "UNRESOLVED_ORDER_UNKNOWN"
    RECONCILIATION_UNHEALTHY = "RECONCILIATION_UNHEALTHY"
    RECONCILIATION_UNKNOWN = "RECONCILIATION_UNKNOWN"
    MARKET_DATA_UNHEALTHY = "MARKET_DATA_UNHEALTHY"
    MARKET_DATA_UNKNOWN = "MARKET_DATA_UNKNOWN"
    PROVIDER_RUNTIME_UNHEALTHY = "PROVIDER_RUNTIME_UNHEALTHY"
    PROVIDER_RUNTIME_UNKNOWN = "PROVIDER_RUNTIME_UNKNOWN"
    BROKER_SESSION_UNHEALTHY = "BROKER_SESSION_UNHEALTHY"
    BROKER_SESSION_UNKNOWN = "BROKER_SESSION_UNKNOWN"
    POSITION_TRUTH_UNKNOWN = "POSITION_TRUTH_UNKNOWN"
    PROPOSED_DIRECTION_UNKNOWN = "PROPOSED_DIRECTION_UNKNOWN"
    PROPOSED_QUANTITY_UNKNOWN = "PROPOSED_QUANTITY_UNKNOWN"
    PRODUCT_FAMILY_UNKNOWN = "PRODUCT_FAMILY_UNKNOWN"
    PRODUCT_WHITELIST_UNBOUND = "PRODUCT_WHITELIST_UNBOUND"
    PRODUCT_NOT_WHITELISTED = "PRODUCT_NOT_WHITELISTED"
    CONTRACT_ID_UNKNOWN = "CONTRACT_ID_UNKNOWN"
    CONTRACT_AUTHORIZATION_UNBOUND = "CONTRACT_AUTHORIZATION_UNBOUND"
    CONTRACT_NOT_AUTHORIZED = "CONTRACT_NOT_AUTHORIZED"
    MAX_POSITION_UNBOUND = "MAX_POSITION_UNBOUND"
    MAX_POSITION_EXCEEDED = "MAX_POSITION_EXCEEDED"
    ADD_ON_UNBOUND = "ADD_ON_UNBOUND"
    ADD_ON_NOT_ALLOWED = "ADD_ON_NOT_ALLOWED"
    PER_TRADE_RISK_UNBOUND = "PER_TRADE_RISK_UNBOUND"
    PER_TRADE_RISK_UNKNOWN = "PER_TRADE_RISK_UNKNOWN"
    PER_TRADE_RISK_EXCEEDED = "PER_TRADE_RISK_EXCEEDED"
    DAILY_LOSS_CEILING_UNBOUND = "DAILY_LOSS_CEILING_UNBOUND"
    DAILY_LOSS_UNKNOWN = "DAILY_LOSS_UNKNOWN"
    DAILY_LOSS_CEILING_EXCEEDED = "DAILY_LOSS_CEILING_EXCEEDED"
    DAILY_RISK_CEILING_UNBOUND = "DAILY_RISK_CEILING_UNBOUND"
    DAILY_RISK_UNKNOWN = "DAILY_RISK_UNKNOWN"
    DAILY_RISK_CEILING_EXCEEDED = "DAILY_RISK_CEILING_EXCEEDED"
    CUMULATIVE_LOSS_CEILING_UNBOUND = "CUMULATIVE_LOSS_CEILING_UNBOUND"
    CUMULATIVE_LOSS_UNKNOWN = "CUMULATIVE_LOSS_UNKNOWN"
    CUMULATIVE_LOSS_CEILING_EXCEEDED = "CUMULATIVE_LOSS_CEILING_EXCEEDED"
    DRAWDOWN_CEILING_UNBOUND = "DRAWDOWN_CEILING_UNBOUND"
    DRAWDOWN_UNKNOWN = "DRAWDOWN_UNKNOWN"
    DRAWDOWN_CEILING_EXCEEDED = "DRAWDOWN_CEILING_EXCEEDED"
    MINIMUM_MARGIN_HEADROOM_UNBOUND = "MINIMUM_MARGIN_HEADROOM_UNBOUND"
    MARGIN_HEADROOM_UNPROVEN = "MARGIN_HEADROOM_UNPROVEN"
    MARGIN_HEADROOM_INSUFFICIENT = "MARGIN_HEADROOM_INSUFFICIENT"
    RESERVE_HEADROOM_UNPROVEN = "RESERVE_HEADROOM_UNPROVEN"
    RESERVE_HEADROOM_INSUFFICIENT = "RESERVE_HEADROOM_INSUFFICIENT"


_SEVERITY: dict[RiskDecision, int] = {
    RiskDecision.ALLOW: 0,
    RiskDecision.INSUFFICIENT_OR_UNKNOWN: 1,
    RiskDecision.DENY: 2,
}


def _positive_decimal(value: Decimal, name: str) -> None:
    if type(value) is not Decimal or not value.is_finite() or value <= 0:
        raise ValueError(f"{name} must be a positive finite Decimal")


def _non_negative_integer(value: int, name: str) -> None:
    if type(value) is not int or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")


def _optional_decimal(value: Decimal | None, name: str) -> None:
    if value is not None and (type(value) is not Decimal or not value.is_finite()):
        raise ValueError(f"{name} must be a finite Decimal or None")


@dataclass(frozen=True)
class RealRiskRuntimeFacts:
    """One deterministic bundle of runtime facts for the REAL risk gate.

    A ``None`` value means the fact is UNKNOWN (fail closed when it is needed).
    Explicit health states and the external-mutation status are always required
    so callers cannot omit them accidentally.
    """

    proposed_action: ProposedAction
    reconciliation_health: HealthState
    market_data_health: HealthState
    provider_runtime_health: HealthState
    broker_session_health: HealthState
    external_mutation_status: ExternalMutationStatus
    concrete_contract_id: str | None = None
    product_family: str | None = None
    proposed_direction: PositionDirection | None = None
    proposed_quantity: Decimal | None = None
    current_position_direction: PositionDirection | None = None
    current_position_quantity: Decimal | None = None
    account_cash: Decimal | None = None
    account_margin: Decimal | None = None
    account_headroom: Decimal | None = None
    proposed_stop_risk: Decimal | None = None
    realized_pnl: Decimal | None = None
    unrealized_pnl: Decimal | None = None
    daily_loss: Decimal | None = None
    daily_risk_used: Decimal | None = None
    drawdown: Decimal | None = None
    cumulative_loss: Decimal | None = None
    unresolved_order_count: int | None = None
    kill_switch_tripped: bool | None = None
    no_new_risk_requested: bool | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.proposed_action, ProposedAction):
            raise ValueError("proposed action must be a ProposedAction")
        for name in (
            "reconciliation_health",
            "market_data_health",
            "provider_runtime_health",
            "broker_session_health",
        ):
            if not isinstance(getattr(self, name), HealthState):
                raise ValueError(f"{name} must be a HealthState")
        if not isinstance(self.external_mutation_status, ExternalMutationStatus):
            raise ValueError("external mutation status must be an ExternalMutationStatus")
        for name in ("concrete_contract_id", "product_family"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be a non-empty string or None")
        if self.proposed_direction is not None and not isinstance(self.proposed_direction, PositionDirection):
            raise ValueError("proposed direction must be a PositionDirection or None")
        if self.current_position_direction is not None and not isinstance(
            self.current_position_direction, PositionDirection
        ):
            raise ValueError("current position direction must be a PositionDirection or None")
        for name in ("proposed_quantity",):
            value = getattr(self, name)
            if value is not None:
                _positive_decimal(value, name)
        # Current position quantity: 0 means a known-flat position; None means
        # the position truth is UNKNOWN (fail closed).
        if self.current_position_quantity is not None and (
            type(self.current_position_quantity) is not Decimal
            or not self.current_position_quantity.is_finite()
            or self.current_position_quantity < 0
        ):
            raise ValueError("current position quantity must be a non-negative finite Decimal or None")
        for name in (
            "account_cash",
            "account_margin",
            "account_headroom",
            "proposed_stop_risk",
            "realized_pnl",
            "unrealized_pnl",
            "daily_loss",
            "daily_risk_used",
            "drawdown",
            "cumulative_loss",
        ):
            _optional_decimal(getattr(self, name), name)
        if self.unresolved_order_count is not None:
            _non_negative_integer(self.unresolved_order_count, "unresolved order count")
        for name in ("kill_switch_tripped", "no_new_risk_requested"):
            value = getattr(self, name)
            if value is not None and type(value) is not bool:
                raise ValueError(f"{name} must be a bool or None")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "proposed_action": self.proposed_action.value,
                "reconciliation_health": self.reconciliation_health.value,
                "market_data_health": self.market_data_health.value,
                "provider_runtime_health": self.provider_runtime_health.value,
                "broker_session_health": self.broker_session_health.value,
                "external_mutation_status": self.external_mutation_status.value,
                "concrete_contract_id": self.concrete_contract_id,
                "product_family": self.product_family,
                "proposed_direction": None if self.proposed_direction is None else self.proposed_direction.value,
                "proposed_quantity": None if self.proposed_quantity is None else str(self.proposed_quantity),
                "current_position_direction": (
                    None if self.current_position_direction is None else self.current_position_direction.value
                ),
                "current_position_quantity": (
                    None if self.current_position_quantity is None else str(self.current_position_quantity)
                ),
                "account_cash": None if self.account_cash is None else str(self.account_cash),
                "account_margin": None if self.account_margin is None else str(self.account_margin),
                "account_headroom": None if self.account_headroom is None else str(self.account_headroom),
                "proposed_stop_risk": (
                    None if self.proposed_stop_risk is None else str(self.proposed_stop_risk)
                ),
                "realized_pnl": None if self.realized_pnl is None else str(self.realized_pnl),
                "unrealized_pnl": None if self.unrealized_pnl is None else str(self.unrealized_pnl),
                "daily_loss": None if self.daily_loss is None else str(self.daily_loss),
                "daily_risk_used": None if self.daily_risk_used is None else str(self.daily_risk_used),
                "drawdown": None if self.drawdown is None else str(self.drawdown),
                "cumulative_loss": None if self.cumulative_loss is None else str(self.cumulative_loss),
                "unresolved_order_count": self.unresolved_order_count,
                "kill_switch_tripped": self.kill_switch_tripped,
                "no_new_risk_requested": self.no_new_risk_requested,
            }
        )


@dataclass(frozen=True)
class RealRiskDecision:
    """Deterministic reason-coded decision (decision only; no execution)."""

    decision: RiskDecision
    action_classification: ActionRiskClassification
    reason_codes: tuple[ReasonCode, ...]
    detail: str
    evaluated_at: datetime
    policy_id: str
    policy_version: str
    safety_mode: SafetyMode

    def __post_init__(self) -> None:
        if not isinstance(self.decision, RiskDecision):
            raise ValueError("decision must be a RiskDecision")
        if not isinstance(self.action_classification, ActionRiskClassification):
            raise ValueError("action classification must be an ActionRiskClassification")
        if not isinstance(self.reason_codes, tuple) or not self.reason_codes:
            raise ValueError("decision requires a non-empty tuple of reason codes")
        if any(not isinstance(item, ReasonCode) for item in self.reason_codes):
            raise ValueError("decision reason codes must be ReasonCode values")
        if not self.detail or not self.policy_id or not self.policy_version:
            raise ValueError("decision requires a detail, policy id and policy version")
        if self.evaluated_at.tzinfo is None:
            raise ValueError("decision timestamp must be timezone-aware")
        if not isinstance(self.safety_mode, SafetyMode):
            raise ValueError("decision safety mode must be a SafetyMode")

    def allowed(self) -> bool:
        return self.decision is RiskDecision.ALLOW

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "decision": self.decision.value,
                "action_classification": self.action_classification.value,
                "reason_codes": [item.value for item in self.reason_codes],
                "detail": self.detail,
                "evaluated_at": self.evaluated_at.isoformat(),
                "policy_id": self.policy_id,
                "policy_version": self.policy_version,
                "safety_mode": self.safety_mode.value,
            }
        )


def _opposite(direction: PositionDirection) -> PositionDirection:
    if direction is PositionDirection.LONG:
        return PositionDirection.SHORT
    if direction is PositionDirection.SHORT:
        return PositionDirection.LONG
    raise ValueError("unknown position direction")


def classify_action(facts: RealRiskRuntimeFacts) -> ActionRiskClassification:
    """Deterministic action classification (UNKNOWN truth fails closed).

    A CLOSE is only classified RISK_REDUCING when the current position
    identity/direction/quantity and the proposed direction/quantity are
    sufficiently known and the resulting exposure is demonstrably lower.
    """
    if not isinstance(facts, RealRiskRuntimeFacts):
        raise ValueError("classification requires RealRiskRuntimeFacts")
    if facts.proposed_action is ProposedAction.UNKNOWN:
        return ActionRiskClassification.UNKNOWN
    if facts.proposed_action is ProposedAction.HOLD:
        return ActionRiskClassification.NEUTRAL
    if facts.proposed_action is ProposedAction.OPEN:
        return ActionRiskClassification.RISK_INCREASING
    # CLOSE ----------------------------------------------------------------
    if facts.current_position_direction is None or facts.current_position_quantity is None:
        return ActionRiskClassification.UNKNOWN
    if facts.proposed_direction is None or facts.proposed_quantity is None:
        return ActionRiskClassification.UNKNOWN
    if facts.proposed_quantity <= 0:
        return ActionRiskClassification.UNKNOWN
    if facts.proposed_direction is not _opposite(facts.current_position_direction):
        return ActionRiskClassification.UNKNOWN
    resulting = facts.current_position_quantity - facts.proposed_quantity
    if resulting < 0:
        resulting = Decimal("0")
    if resulting >= facts.current_position_quantity:
        return ActionRiskClassification.UNKNOWN
    return ActionRiskClassification.RISK_REDUCING


class _Accumulator:
    """Collects all fail-closed reasons with the most severe decision."""

    def __init__(self) -> None:
        self._decision = RiskDecision.ALLOW
        self._reasons: list[ReasonCode] = []

    @property
    def decision(self) -> RiskDecision:
        return self._decision

    @property
    def reasons(self) -> tuple[ReasonCode, ...]:
        return tuple(self._reasons)

    def add(self, decision: RiskDecision, reason: ReasonCode) -> None:
        if _SEVERITY[decision] > _SEVERITY[self._decision]:
            self._decision = decision
        self._reasons.append(reason)


class RealRiskGate:
    """Deterministic REAL risk gate (decision only, no execution)."""

    def evaluate(
        self,
        policy: RealRiskPolicy,
        safety_state: RealSafetyState,
        facts: RealRiskRuntimeFacts,
        evaluated_at: datetime,
    ) -> RealRiskDecision:
        if not isinstance(policy, RealRiskPolicy):
            raise ValueError("RealRiskGate requires a RealRiskPolicy")
        if not isinstance(safety_state, RealSafetyState):
            raise ValueError("RealRiskGate requires a RealSafetyState")
        if not isinstance(facts, RealRiskRuntimeFacts):
            raise ValueError("RealRiskGate requires RealRiskRuntimeFacts")
        if evaluated_at.tzinfo is None:
            raise ValueError("gate evaluation timestamp must be timezone-aware")

        classification = classify_action(facts)
        acc = _Accumulator()

        # Common fail-closed safety checks (apply to every action).
        if safety_state.mode is SafetyMode.KILL:
            acc.add(RiskDecision.DENY, ReasonCode.KILL_SWITCH_TRIPPED)
        if facts.kill_switch_tripped is True:
            acc.add(RiskDecision.DENY, ReasonCode.KILL_SWITCH_TRIPPED)
        if safety_state.mode is SafetyMode.UNKNOWN:
            acc.add(RiskDecision.DENY, ReasonCode.SAFETY_MODE_UNKNOWN)
        if safety_state.hard_inconsistency_latched:
            acc.add(RiskDecision.DENY, ReasonCode.HARD_INCONSISTENCY_LATCHED)
        # Persistent safety state owns the latched mutation truth.  Transient
        # facts may add a stricter observation, but can never resolve or
        # override the durable state supplied by the safety controller.
        mutation_statuses = {
            safety_state.external_mutation_status,
            facts.external_mutation_status,
        }
        if ExternalMutationStatus.UNRESOLVED in mutation_statuses:
            acc.add(RiskDecision.DENY, ReasonCode.EXTERNAL_MUTATION_UNRESOLVED)
        elif ExternalMutationStatus.UNKNOWN in mutation_statuses:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.EXTERNAL_MUTATION_UNKNOWN)

        if classification is ActionRiskClassification.UNKNOWN:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.ACTION_CLASSIFICATION_UNKNOWN)
        elif classification is ActionRiskClassification.RISK_REDUCING:
            self._apply_reducing_checks(acc, facts)
        elif classification is ActionRiskClassification.RISK_INCREASING:
            self._apply_increasing_checks(acc, policy, safety_state, facts)
        # NEUTRAL (HOLD): no order, no risk; no additional checks.

        if acc.decision is RiskDecision.ALLOW:
            reason = (
                ReasonCode.NEUTRAL_NO_RISK
                if classification is ActionRiskClassification.NEUTRAL
                else ReasonCode.ALLOWED
            )
            acc.add(RiskDecision.ALLOW, reason)

        return RealRiskDecision(
            decision=acc.decision,
            action_classification=classification,
            reason_codes=acc.reasons,
            detail=_build_detail(acc.decision, classification, acc.reasons),
            evaluated_at=evaluated_at,
            policy_id=policy.policy_id,
            policy_version=policy.version,
            safety_mode=safety_state.mode,
        )

    @staticmethod
    def _add_health(
        acc: _Accumulator,
        state: HealthState,
        unhealthy: ReasonCode,
        unknown: ReasonCode,
    ) -> None:
        if state is HealthState.UNHEALTHY:
            acc.add(RiskDecision.DENY, unhealthy)
        elif state is HealthState.UNKNOWN:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, unknown)

    def _apply_reducing_checks(self, acc: _Accumulator, facts: RealRiskRuntimeFacts) -> None:
        # Position truth is already guaranteed by the RISK_REDUCING classification.
        # A close still needs trustworthy position truth and a working session.
        self._add_health(
            acc, facts.reconciliation_health, ReasonCode.RECONCILIATION_UNHEALTHY, ReasonCode.RECONCILIATION_UNKNOWN
        )
        self._add_health(
            acc, facts.broker_session_health, ReasonCode.BROKER_SESSION_UNHEALTHY, ReasonCode.BROKER_SESSION_UNKNOWN
        )

    def _apply_increasing_checks(
        self,
        acc: _Accumulator,
        policy: RealRiskPolicy,
        safety_state: RealSafetyState,
        facts: RealRiskRuntimeFacts,
    ) -> None:
        # -- no-new-risk / pause --------------------------------------------
        if safety_state.mode is SafetyMode.NO_NEW_RISK:
            acc.add(RiskDecision.DENY, ReasonCode.NO_NEW_RISK_ACTIVE)
        if facts.no_new_risk_requested is True:
            acc.add(RiskDecision.DENY, ReasonCode.NO_NEW_RISK_ACTIVE)
        # -- duplicate / unresolved orders ----------------------------------
        if facts.unresolved_order_count is None:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.UNRESOLVED_ORDER_UNKNOWN)
        elif facts.unresolved_order_count > 0:
            acc.add(RiskDecision.DENY, ReasonCode.UNRESOLVED_ORDER)
        # -- health ----------------------------------------------------------
        self._add_health(
            acc, facts.reconciliation_health, ReasonCode.RECONCILIATION_UNHEALTHY, ReasonCode.RECONCILIATION_UNKNOWN
        )
        self._add_health(
            acc, facts.market_data_health, ReasonCode.MARKET_DATA_UNHEALTHY, ReasonCode.MARKET_DATA_UNKNOWN
        )
        self._add_health(
            acc, facts.provider_runtime_health, ReasonCode.PROVIDER_RUNTIME_UNHEALTHY, ReasonCode.PROVIDER_RUNTIME_UNKNOWN
        )
        self._add_health(
            acc, facts.broker_session_health, ReasonCode.BROKER_SESSION_UNHEALTHY, ReasonCode.BROKER_SESSION_UNKNOWN
        )
        # -- position/order truth for the traded contract ---------------------
        if facts.current_position_quantity is None:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.POSITION_TRUTH_UNKNOWN)
        if facts.proposed_direction is None:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.PROPOSED_DIRECTION_UNKNOWN)
        if facts.proposed_quantity is None:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.PROPOSED_QUANTITY_UNKNOWN)
        # -- product whitelist ------------------------------------------------
        if policy.binding_status(PolicyBinding.PRODUCT_WHITELIST) is BindingStatus.UNBOUND:
            acc.add(RiskDecision.DENY, ReasonCode.PRODUCT_WHITELIST_UNBOUND)
        elif facts.product_family is None:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.PRODUCT_FAMILY_UNKNOWN)
        elif facts.product_family not in policy.product_whitelist:
            acc.add(RiskDecision.DENY, ReasonCode.PRODUCT_NOT_WHITELISTED)
        # -- contract authorization -------------------------------------------
        if policy.binding_status(PolicyBinding.CONTRACT_AUTHORIZATION) is BindingStatus.UNBOUND:
            acc.add(RiskDecision.DENY, ReasonCode.CONTRACT_AUTHORIZATION_UNBOUND)
        elif facts.concrete_contract_id is None:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.CONTRACT_ID_UNKNOWN)
        elif facts.concrete_contract_id not in policy.contract_authorization:
            acc.add(RiskDecision.DENY, ReasonCode.CONTRACT_NOT_AUTHORIZED)
        # -- max position -----------------------------------------------------
        if policy.binding_status(PolicyBinding.MAX_POSITION_QUANTITY) is BindingStatus.UNBOUND:
            acc.add(RiskDecision.DENY, ReasonCode.MAX_POSITION_UNBOUND)
        elif facts.proposed_quantity is not None:
            resulting = _resulting_position_quantity(facts)
            if resulting > policy.max_position_quantity:
                acc.add(RiskDecision.DENY, ReasonCode.MAX_POSITION_EXCEEDED)
        # -- add-on / pyramiding ----------------------------------------------
        if _is_add_on(facts):
            if policy.binding_status(PolicyBinding.ALLOW_ADD_ON) is BindingStatus.UNBOUND:
                acc.add(RiskDecision.DENY, ReasonCode.ADD_ON_UNBOUND)
            elif policy.allow_add_on is not True:
                acc.add(RiskDecision.DENY, ReasonCode.ADD_ON_NOT_ALLOWED)
        # -- per-trade risk ceiling -------------------------------------------
        if policy.binding_status(PolicyBinding.PER_TRADE_RISK_CEILING) is BindingStatus.UNBOUND:
            acc.add(RiskDecision.DENY, ReasonCode.PER_TRADE_RISK_UNBOUND)
        elif facts.proposed_stop_risk is None:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.PER_TRADE_RISK_UNKNOWN)
        elif facts.proposed_stop_risk > policy.per_trade_risk_ceiling:
            acc.add(RiskDecision.DENY, ReasonCode.PER_TRADE_RISK_EXCEEDED)
        # -- daily loss ceiling ------------------------------------------------
        if policy.binding_status(PolicyBinding.DAILY_LOSS_CEILING) is BindingStatus.UNBOUND:
            acc.add(RiskDecision.DENY, ReasonCode.DAILY_LOSS_CEILING_UNBOUND)
        elif facts.daily_loss is None:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.DAILY_LOSS_UNKNOWN)
        elif facts.daily_loss > policy.daily_loss_ceiling:
            acc.add(RiskDecision.DENY, ReasonCode.DAILY_LOSS_CEILING_EXCEEDED)
        # -- daily risk ceiling -------------------------------------------------
        if policy.binding_status(PolicyBinding.DAILY_RISK_CEILING) is BindingStatus.UNBOUND:
            acc.add(RiskDecision.DENY, ReasonCode.DAILY_RISK_CEILING_UNBOUND)
        elif facts.daily_risk_used is None or facts.proposed_stop_risk is None:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.DAILY_RISK_UNKNOWN)
        elif facts.daily_risk_used + facts.proposed_stop_risk > policy.daily_risk_ceiling:
            acc.add(RiskDecision.DENY, ReasonCode.DAILY_RISK_CEILING_EXCEEDED)
        # -- cumulative loss ceiling ---------------------------------------------
        if policy.binding_status(PolicyBinding.CUMULATIVE_LOSS_CEILING) is BindingStatus.UNBOUND:
            acc.add(RiskDecision.DENY, ReasonCode.CUMULATIVE_LOSS_CEILING_UNBOUND)
        elif facts.cumulative_loss is None:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.CUMULATIVE_LOSS_UNKNOWN)
        elif facts.cumulative_loss > policy.cumulative_loss_ceiling:
            acc.add(RiskDecision.DENY, ReasonCode.CUMULATIVE_LOSS_CEILING_EXCEEDED)
        # -- drawdown ceiling ------------------------------------------------------
        if policy.binding_status(PolicyBinding.DRAWDOWN_CEILING) is BindingStatus.UNBOUND:
            acc.add(RiskDecision.DENY, ReasonCode.DRAWDOWN_CEILING_UNBOUND)
        elif facts.drawdown is None:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.DRAWDOWN_UNKNOWN)
        elif facts.drawdown > policy.drawdown_ceiling:
            acc.add(RiskDecision.DENY, ReasonCode.DRAWDOWN_CEILING_EXCEEDED)
        # -- minimum margin headroom ------------------------------------------------
        if policy.binding_status(PolicyBinding.MINIMUM_MARGIN_HEADROOM) is BindingStatus.UNBOUND:
            acc.add(RiskDecision.DENY, ReasonCode.MINIMUM_MARGIN_HEADROOM_UNBOUND)
        elif facts.account_headroom is None or facts.account_cash is None or facts.account_margin is None:
            acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.MARGIN_HEADROOM_UNPROVEN)
        elif facts.account_headroom < policy.minimum_margin_headroom:
            acc.add(RiskDecision.DENY, ReasonCode.MARGIN_HEADROOM_INSUFFICIENT)
        # -- operational reserve headroom (optional; enforced only when supplied) ---
        if policy.binding_status(PolicyBinding.OPERATIONAL_RESERVE_HEADROOM) is BindingStatus.BOUND:
            if facts.account_headroom is None:
                acc.add(RiskDecision.INSUFFICIENT_OR_UNKNOWN, ReasonCode.RESERVE_HEADROOM_UNPROVEN)
            elif facts.account_headroom < policy.operational_reserve_headroom:
                acc.add(RiskDecision.DENY, ReasonCode.RESERVE_HEADROOM_INSUFFICIENT)


def _resulting_position_quantity(facts: RealRiskRuntimeFacts) -> Decimal:
    """Resulting position quantity in the proposed direction after an OPEN."""
    current = Decimal("0")
    if (
        facts.current_position_direction is not None
        and facts.current_position_direction == facts.proposed_direction
        and facts.current_position_quantity is not None
    ):
        current = facts.current_position_quantity
    return current + facts.proposed_quantity


def _is_add_on(facts: RealRiskRuntimeFacts) -> bool:
    """True when the OPEN adds to an existing same-direction position."""
    return (
        facts.proposed_direction is not None
        and facts.current_position_direction is not None
        and facts.proposed_direction == facts.current_position_direction
        and facts.current_position_quantity is not None
        and facts.current_position_quantity > 0
    )


def _build_detail(
    decision: RiskDecision,
    classification: ActionRiskClassification,
    reasons: tuple[ReasonCode, ...],
) -> str:
    if decision is RiskDecision.ALLOW:
        return f"{classification.value} allowed"
    joined = "; ".join(item.value for item in reasons)
    return f"{classification.value} {decision.value}: {joined}"

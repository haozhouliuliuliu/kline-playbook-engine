"""RiskGate for the Shadow Runtime Foundation (deterministic, FIXTURE-ONLY).

Skeleton v1.0 §5 gives RiskGate ownership of versioned risk rules. In this
foundation package the rule numbers are explicit TEST/FIXTURE numbers only;
they are NOT permanent real-money risk limits. No permanent risk rule is frozen
here (freezing real-money risk limits remains an Owner gate).

The gate evaluates one approved intent against the current ``TradingState`` and
deterministically approves or rejects it, and when approved returns the exact
quantity the OMS should submit.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
import json
from typing import Any

from src.contract_semantics import PositionDirection
from src.intent import IntentAction, StrategyIntent
from src.market_context import MarketContext
from src.trading_state import TradingState

RISK_GATE_SCHEMA_VERSION = "shadow-runtime-risk-gate-v0.1"

FIXTURE_ONLY_WARNING = (
    "FIXTURE-ONLY synthetic rule numbers; NOT permanent real-money risk limits."
)


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RiskRuleSet:
    """Versioned deterministic risk rules (FIXTURE-ONLY, no real money)."""

    ruleset_id: str
    version: str
    max_order_quantity: Decimal | None = None
    max_position_quantity: Decimal | None = None
    max_open_positions: int | None = None
    allow_opposite_direction_flip: bool = False
    allow_open_when_disconnected: bool = False
    allow_open_when_stale: bool = False

    def __post_init__(self) -> None:
        if not self.ruleset_id or not self.version:
            raise ValueError("risk ruleset requires an id and version")
        for value, name in (
            (self.max_order_quantity, "max order quantity"),
            (self.max_position_quantity, "max position quantity"),
        ):
            if value is not None and (
                type(value) is not Decimal or not value.is_finite() or value <= 0
            ):
                raise ValueError(f"{name} must be a positive finite Decimal or None")
        if self.max_open_positions is not None and (
            type(self.max_open_positions) is not int or self.max_open_positions <= 0
        ):
            raise ValueError("max open positions must be a positive integer or None")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "ruleset_id": self.ruleset_id,
                "version": self.version,
                "max_order_quantity": (
                    None if self.max_order_quantity is None else str(self.max_order_quantity)
                ),
                "max_position_quantity": (
                    None if self.max_position_quantity is None else str(self.max_position_quantity)
                ),
                "max_open_positions": self.max_open_positions,
                "allow_opposite_direction_flip": self.allow_opposite_direction_flip,
                "allow_open_when_disconnected": self.allow_open_when_disconnected,
                "allow_open_when_stale": self.allow_open_when_stale,
            }
        )


@dataclass(frozen=True)
class RiskDecision:
    """Deterministic risk evaluation of one intent."""

    approved: bool
    reason: str
    ruleset_id: str
    decision_at: datetime
    quantity_for_order: Decimal | None = None

    def __post_init__(self) -> None:
        if not self.ruleset_id or not self.reason:
            raise ValueError("risk decision requires a ruleset id and reason")
        if self.decision_at.tzinfo is None:
            raise ValueError("risk decision timestamp must be timezone-aware")
        if self.quantity_for_order is not None and (
            type(self.quantity_for_order) is not Decimal
            or not self.quantity_for_order.is_finite()
            or self.quantity_for_order <= 0
        ):
            raise ValueError("risk decision order quantity must be a positive finite Decimal")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "approved": self.approved,
                "reason": self.reason,
                "ruleset_id": self.ruleset_id,
                "decision_at": self.decision_at.isoformat(),
                "quantity_for_order": (
                    None if self.quantity_for_order is None else str(self.quantity_for_order)
                ),
            }
        )


class RiskGate:
    """Deterministic risk gate over a FIXTURE-ONLY RiskRuleSet."""

    def __init__(self, ruleset: RiskRuleSet) -> None:
        if not isinstance(ruleset, RiskRuleSet):
            raise ValueError("RiskGate requires a RiskRuleSet")
        self._ruleset = ruleset

    @property
    def ruleset(self) -> RiskRuleSet:
        return self._ruleset

    def evaluate(
        self,
        intent: StrategyIntent,
        state: TradingState,
        context: MarketContext,
        *,
        safety_blocking: bool,
        connection_connected: bool,
    ) -> RiskDecision:
        if not isinstance(intent, StrategyIntent):
            raise ValueError("RiskGate requires a StrategyIntent")
        if not isinstance(state, TradingState):
            raise ValueError("RiskGate requires a TradingState")
        if not isinstance(context, MarketContext):
            raise ValueError("RiskGate requires a MarketContext")
        if intent.action is IntentAction.HOLD:
            return RiskDecision(
                approved=False,
                reason="HOLD requires no order",
                ruleset_id=self._ruleset.ruleset_id,
                decision_at=intent.decision_at,
            )

        existing = state.position_for(intent.concrete_contract_id, intent.direction)
        opposite = state.position_for(intent.concrete_contract_id, _opposite(intent.direction))

        # Intent-quantity resolution (CLOSE with no explicit quantity = close all).
        if intent.action is IntentAction.OPEN:
            quantity_for_order = intent.quantity
            if quantity_for_order is None:
                return RiskDecision(
                    approved=False,
                    reason="OPEN intent has no quantity",
                    ruleset_id=self._ruleset.ruleset_id,
                    decision_at=intent.decision_at,
                )
            if opposite is not None and not self._ruleset.allow_opposite_direction_flip:
                return RiskDecision(
                    approved=False,
                    reason="OPPOSITE_DIRECTION_POSITION_FLIP_DISALLOWED",
                    ruleset_id=self._ruleset.ruleset_id,
                    decision_at=intent.decision_at,
                )
            resulting_quantity = (existing.quantity if existing else Decimal("0")) + quantity_for_order
        else:  # CLOSE
            if existing is None or existing.quantity == 0:
                return RiskDecision(
                    approved=False,
                    reason="CLOSE_WITHOUT_POSITION",
                    ruleset_id=self._ruleset.ruleset_id,
                    decision_at=intent.decision_at,
                )
            if intent.quantity is None:
                quantity_for_order = existing.quantity
            else:
                quantity_for_order = min(intent.quantity, existing.quantity)
            resulting_quantity = existing.quantity - quantity_for_order

        # Order-quantity rule.
        limit = self._ruleset.max_order_quantity
        if limit is not None and quantity_for_order > limit:
            return RiskDecision(
                approved=False,
                reason="ORDER_QUANTITY_EXCEEDS_RULE_LIMIT",
                ruleset_id=self._ruleset.ruleset_id,
                decision_at=intent.decision_at,
            )
        # Resulting position rule.
        limit = self._ruleset.max_position_quantity
        if limit is not None and resulting_quantity > limit:
            return RiskDecision(
                approved=False,
                reason="RESULTING_POSITION_EXCEEDS_RULE_LIMIT",
                ruleset_id=self._ruleset.ruleset_id,
                decision_at=intent.decision_at,
            )
        # Open-position count rule.
        if intent.action is IntentAction.OPEN and self._ruleset.max_open_positions is not None:
            open_count = len(state.positions)
            if existing is None and open_count + 1 > self._ruleset.max_open_positions:
                return RiskDecision(
                    approved=False,
                    reason="MAX_OPEN_POSITIONS_EXCEEDED",
                    ruleset_id=self._ruleset.ruleset_id,
                    decision_at=intent.decision_at,
                )
        # Connection rule.
        if intent.action is IntentAction.OPEN and not connection_connected and not self._ruleset.allow_open_when_disconnected:
            return RiskDecision(
                approved=False,
                reason="BROKER_DISCONNECTED_OPEN_DISALLOWED",
                ruleset_id=self._ruleset.ruleset_id,
                decision_at=intent.decision_at,
            )
        # Stale-data rule.
        if intent.action is IntentAction.OPEN and context.is_stale(intent.decision_at) and not self._ruleset.allow_open_when_stale:
            return RiskDecision(
                approved=False,
                reason="STALE_MARKET_DATA_OPEN_DISALLOWED",
                ruleset_id=self._ruleset.ruleset_id,
                decision_at=intent.decision_at,
            )
        # Safety-blocking rule (Safety overrides strategies).
        if safety_blocking:
            return RiskDecision(
                approved=False,
                reason="SAFETY_BLOCKING",
                ruleset_id=self._ruleset.ruleset_id,
                decision_at=intent.decision_at,
            )

        return RiskDecision(
            approved=True,
            reason="APPROVED",
            ruleset_id=self._ruleset.ruleset_id,
            decision_at=intent.decision_at,
            quantity_for_order=quantity_for_order,
        )


def _opposite(direction: PositionDirection) -> PositionDirection:
    if direction is PositionDirection.LONG:
        return PositionDirection.SHORT
    if direction is PositionDirection.SHORT:
        return PositionDirection.LONG
    raise ValueError("unknown position direction")

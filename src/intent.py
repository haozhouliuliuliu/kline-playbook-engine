"""Strategy intent and deterministic conflict resolution (Shadow Runtime).

A strategy (TEST_ONLY fake strategy in tests; later a real Playbook-bound
strategy behind a research gate) produces a deterministic ``StrategyIntent``
from a ``MarketContext``. ``ConflictResolver`` resolves a batch of intents
deterministically BEFORE the RiskGate: identical intents collapse, and distinct
conflicting intents for the same contract fail closed instead of silently
choosing one.

This is ordinary engineering under Skeleton v1.0 "deterministic conflict
resolution" in the Trading Loop. No candidate outcome, no real money.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Iterable

from src.broker_adapter import OrderRole, OrderType, StopTriggerCondition
from src.contract_semantics import CloseOffset, PositionDirection

INTENT_SCHEMA_VERSION = "shadow-runtime-intent-v0.1"


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class IntentAction(str, Enum):
    """Deterministic intent vocabulary of the runtime chain."""

    OPEN = "OPEN"
    CLOSE = "CLOSE"
    HOLD = "HOLD"


class IntentDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED_CONFLICT = "REJECTED_CONFLICT"
    NEUTRAL = "NEUTRAL"


@dataclass(frozen=True)
class CloseExecutionChild:
    """One explicit later-policy result for a logical close."""

    offset: CloseOffset
    quantity: Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.offset, CloseOffset):
            raise ValueError("close child requires explicit offset")
        if (
            type(self.quantity) is not Decimal
            or not self.quantity.is_finite()
            or self.quantity <= 0
        ):
            raise ValueError("close child quantity must be positive finite Decimal")

    @property
    def identity_id(self) -> str:
        return _canonical_hash({"offset": self.offset.value, "quantity": str(self.quantity)})


@dataclass(frozen=True)
class StrategyIntent:
    """One deterministic strategy intent computed from a MarketContext."""

    intent_id: str
    strategy_identity_id: str
    instrument: str
    concrete_contract_id: str
    action: IntentAction
    decision_at: datetime
    context_identity: str
    direction: PositionDirection | None = None
    quantity: Decimal | None = None
    limit_price: Decimal | None = None
    order_type: OrderType | None = None
    trigger_price: Decimal | None = None
    trigger_condition: StopTriggerCondition | None = None
    triggered_order_type: OrderType | None = None
    triggered_limit_price: Decimal | None = None
    order_role: OrderRole = OrderRole.GENERIC
    parent_order_id: str | None = None
    oco_group_id: str | None = None
    replace_generation: int = 0
    source_directive_identity: str | None = None
    close_children: tuple[CloseExecutionChild, ...] = ()
    reason: str | None = None

    def __post_init__(self) -> None:
        if not self.intent_id or not self.strategy_identity_id:
            raise ValueError("intent requires intent and strategy identities")
        if not self.instrument or not self.concrete_contract_id:
            raise ValueError("intent requires instrument and concrete contract identities")
        if not isinstance(self.action, IntentAction):
            raise ValueError("intent action must be an IntentAction")
        if self.decision_at.tzinfo is None:
            raise ValueError("intent decision timestamp must be timezone-aware")
        if not self.context_identity:
            raise ValueError("intent must bind a market context identity")
        if self.direction is not None and not isinstance(self.direction, PositionDirection):
            raise ValueError("intent direction must be a PositionDirection")
        if self.quantity is not None:
            if type(self.quantity) is not Decimal or not self.quantity.is_finite() or self.quantity <= 0:
                raise ValueError("intent quantity must be a positive finite Decimal")
        if self.limit_price is not None:
            if type(self.limit_price) is not Decimal or not self.limit_price.is_finite() or self.limit_price <= 0:
                raise ValueError("intent limit price must be a positive finite Decimal")
        if self.order_type is not None and not isinstance(self.order_type, OrderType):
            raise ValueError("intent order type must be explicit when supplied")
        if not isinstance(self.order_role, OrderRole):
            raise ValueError("intent order role must be explicit")
        if type(self.replace_generation) is not int or self.replace_generation < 0:
            raise ValueError("intent replace generation must be non-negative")
        for value, name in (
            (self.parent_order_id, "parent order"),
            (self.oco_group_id, "OCO group"),
            (self.source_directive_identity, "source directive"),
        ):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"intent {name} identity must be non-empty")
        if self.order_type is OrderType.STOP_MARKET:
            if (
                type(self.trigger_price) is not Decimal
                or not self.trigger_price.is_finite()
                or self.trigger_price <= 0
            ):
                raise ValueError("STOP_MARKET intent requires a positive trigger price")
            if not isinstance(self.trigger_condition, StopTriggerCondition):
                raise ValueError("STOP_MARKET intent requires an explicit trigger condition")
            if self.triggered_order_type not in {OrderType.MARKET, OrderType.LIMIT}:
                raise ValueError("STOP_MARKET intent requires a triggered executable order type")
            if self.triggered_order_type is OrderType.LIMIT:
                if (
                    type(self.triggered_limit_price) is not Decimal
                    or not self.triggered_limit_price.is_finite()
                    or self.triggered_limit_price <= 0
                ):
                    raise ValueError("triggered LIMIT intent requires a positive price")
            elif self.triggered_limit_price is not None:
                raise ValueError("triggered limit price is only valid for triggered LIMIT")
        elif any(
            value is not None
            for value in (
                self.trigger_price,
                self.trigger_condition,
                self.triggered_order_type,
                self.triggered_limit_price,
            )
        ):
            raise ValueError("trigger facts are only valid for STOP_MARKET intent")
        if self.action is IntentAction.OPEN:
            if self.direction is None or self.quantity is None:
                raise ValueError("an OPEN intent requires direction and quantity")
            if self.quantity <= 0:
                raise ValueError("an OPEN intent requires positive quantity")
        elif self.action is IntentAction.CLOSE:
            if self.direction is None:
                raise ValueError("a CLOSE intent requires a direction")
        elif self.action is IntentAction.HOLD:
            if (
                self.direction is not None
                or self.quantity is not None
                or self.limit_price is not None
                or self.order_type is not None
                or self.order_role is not OrderRole.GENERIC
            ):
                raise ValueError("a HOLD intent cannot carry order facts")
        if self.close_children:
            if self.action is not IntentAction.CLOSE or self.quantity is None:
                raise ValueError("explicit close children require a quantified CLOSE intent")
            if any(not isinstance(item, CloseExecutionChild) for item in self.close_children):
                raise ValueError("close children must be CloseExecutionChild values")
            offsets = tuple(item.offset for item in self.close_children)
            if len(offsets) != len(set(offsets)):
                raise ValueError("duplicate close child offsets are forbidden")
            if sum((item.quantity for item in self.close_children), Decimal("0")) != self.quantity:
                raise ValueError("close child quantities must equal logical close quantity")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "schema_version": INTENT_SCHEMA_VERSION,
                "intent_id": self.intent_id,
                "strategy_identity_id": self.strategy_identity_id,
                "instrument": self.instrument,
                "concrete_contract_id": self.concrete_contract_id,
                "action": self.action.value,
                "decision_at": self.decision_at.isoformat(),
                "context_identity": self.context_identity,
                "direction": None if self.direction is None else self.direction.value,
                "quantity": None if self.quantity is None else str(self.quantity),
                "limit_price": None if self.limit_price is None else str(self.limit_price),
                "order_type": None if self.order_type is None else self.order_type.value,
                "trigger_price": None if self.trigger_price is None else str(self.trigger_price),
                "trigger_condition": None if self.trigger_condition is None else self.trigger_condition.value,
                "triggered_order_type": None if self.triggered_order_type is None else self.triggered_order_type.value,
                "triggered_limit_price": None if self.triggered_limit_price is None else str(self.triggered_limit_price),
                "order_role": self.order_role.value,
                "parent_order_id": self.parent_order_id,
                "oco_group_id": self.oco_group_id,
                "replace_generation": self.replace_generation,
                "source_directive_identity": self.source_directive_identity,
                "close_children": [item.identity_id for item in self.close_children],
                "reason": self.reason,
            }
        )


@dataclass(frozen=True)
class IntentResolution:
    """Deterministic outcome for one intent after conflict resolution."""

    intent: StrategyIntent
    decision: IntentDecision
    reason: str
    resolved_identity: str

    def __post_init__(self) -> None:
        if not isinstance(self.intent, StrategyIntent):
            raise ValueError("intent resolution requires a StrategyIntent")
        if not isinstance(self.decision, IntentDecision):
            raise ValueError("intent resolution decision must be an IntentDecision")
        if not self.reason:
            raise ValueError("intent resolution requires a reason")
        if self.decision is IntentDecision.APPROVED and self.intent.action is IntentAction.HOLD:
            raise ValueError("a HOLD intent can only resolve NEUTRAL")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "intent": self.intent.identity_id,
                "decision": self.decision.value,
                "reason": self.reason,
            }
        )


@dataclass(frozen=True)
class ConflictResolution:
    """Full deterministic resolution of one intent batch."""

    resolutions: tuple[IntentResolution, ...]
    resolution_identity: str

    def __post_init__(self) -> None:
        intent_ids = tuple(item.intent.intent_id for item in self.resolutions)
        if len(intent_ids) != len(set(intent_ids)):
            raise ValueError("conflict resolution intent ids must be unique")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "resolutions": [item.identity_id for item in self.resolutions],
            }
        )


class ConflictResolver:
    """Deterministic batch conflict resolution (fail closed, no arbitration)."""

    def resolve(self, intents: Iterable[StrategyIntent]) -> ConflictResolution:
        """Resolve an intent batch deterministically.

        Rules (all deterministic, fail closed):
        - intents are processed in ``intent_id`` order;
        - identical duplicate intents (same ``intent_id``) collapse to one;
        - HOLD intents resolve ``NEUTRAL`` and never conflict;
        - two distinct non-HOLD intents for the SAME ``(strategy,
          concrete_contract_id)`` in one batch are conflicting and BOTH are
          rejected (``REJECTED_CONFLICT``) rather than silently picking one;
        - all other intents resolve ``APPROVED``.
        """
        ordered = tuple(sorted(intents, key=lambda item: item.intent_id))
        if any(not isinstance(item, StrategyIntent) for item in ordered):
            raise ValueError("conflict resolution requires StrategyIntent values")
        if not ordered:
            # A no-op cycle (no intents) is legitimate; resolve to an empty batch.
            empty_identity = _canonical_hash({"resolutions": []})
            return ConflictResolution(resolutions=(), resolution_identity=empty_identity)
        seen: dict[str, str] = {}
        unique: list[StrategyIntent] = []
        for intent in ordered:
            prior_identity = seen.get(intent.intent_id)
            if prior_identity is None:
                unique.append(intent)
                seen[intent.intent_id] = intent.identity_id
                continue
            if prior_identity != intent.identity_id:
                raise ValueError(
                    "same intent_id with different canonical content is not idempotent"
                )

        # Group distinct non-HOLD intents by (strategy, concrete contract).
        groups: dict[tuple[str, str], list[StrategyIntent]] = {}
        for intent in unique:
            if intent.action is IntentAction.HOLD:
                continue
            groups.setdefault((intent.strategy_identity_id, intent.concrete_contract_id), []).append(intent)

        conflicting: set[str] = set()
        for group in groups.values():
            if len(group) > 1:
                conflicting.update(item.intent_id for item in group)

        resolutions: list[IntentResolution] = []
        for intent in unique:
            if intent.action is IntentAction.HOLD:
                resolutions.append(
                    IntentResolution(intent, IntentDecision.NEUTRAL, "HOLD", intent.identity_id)
                )
            elif intent.intent_id in conflicting:
                resolutions.append(
                    IntentResolution(
                        intent,
                        IntentDecision.REJECTED_CONFLICT,
                        "DUPLICATE_STRATEGY_INTENT_CONFLICT",
                        intent.identity_id,
                    )
                )
            else:
                resolutions.append(
                    IntentResolution(intent, IntentDecision.APPROVED, "NO_CONFLICT", intent.identity_id)
                )

        return ConflictResolution(
            resolutions=tuple(resolutions),
            resolution_identity=_canonical_hash(
                {
                    "resolutions": [item.identity_id for item in resolutions],
                }
            ),
        )

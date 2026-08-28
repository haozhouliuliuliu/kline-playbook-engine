"""Canonical deterministic execution chain for the external PAPER runtime.

This module reuses the project-owned Jianghe bridge, conflict resolver,
``RiskGate``, OMS, ``SafetyGate`` and immutable runtime ledger.  Broker/account
facts are inputs, never inferred from model output or local fills.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from hashlib import sha256
import json

from src.broker_adapter import (
    BrokerAccountSnapshot,
    BrokerOrderInstruction,
    BrokerOrderSnapshot,
    BrokerPositionSnapshot,
    OrderRole,
    OrderType,
)
from src.contract_semantics import CloseOffset, OrderAction
from src.intent import ConflictResolver, IntentAction
from src.jianghe_ai_trader import Direction, PositionFact
from src.jianghe_execution_bridge import ExecutionSemanticsRequired, JiangheExecutionBridge
from src.jianghe_response_normalizer import NormalizedJiangheDecision
from src.order_management import OrderManagementSystem, OrderRequest
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_live_causal_context import LiveCausalBar, LiveCausalWake
from src.risk_gate import RiskGate
from src.runtime_events import BrokerConnectionState, BrokerEvent
from src.runtime_ledger import RuntimeLedger, RuntimeLedgerRecordKind, ledger_pairs
from src.safety import SafetyGate

PAPER_EXECUTION_CHAIN_VERSION = "KPE_PAPER_EXECUTION_CHAIN_V0_1"
_ACTIVE_ORDER_STATUSES = frozenset({"LIVE", "PARTIALLY_FILLED"})


def _hash(value: object) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
    ).hexdigest()


@dataclass(frozen=True)
class PaperProjectState:
    """Project projection rebuilt only from a complete broker mirror."""

    account: BrokerAccountSnapshot
    positions: tuple[BrokerPositionSnapshot, ...]
    orders: tuple[BrokerOrderSnapshot, ...]
    snapshot_at: datetime

    @classmethod
    def from_mirror(cls, mirror: PaperBrokerTruthMirror) -> "PaperProjectState":
        if not isinstance(mirror, PaperBrokerTruthMirror):
            raise TypeError("paper project state requires PaperBrokerTruthMirror")
        if mirror.account is None or mirror.snapshot_at is None:
            raise RuntimeError("PAPER_PROJECT_STATE_REQUIRES_COMPLETE_BROKER_TRUTH")
        return cls(
            account=mirror.account,
            positions=mirror.positions,
            orders=mirror.orders,
            snapshot_at=mirror.snapshot_at,
        )

    def position_for(self, concrete_contract_id: str, direction):
        for position in self.positions:
            if (
                position.concrete_contract_id == concrete_contract_id
                and position.direction is direction
            ):
                return position
        return None

    @property
    def identity_id(self) -> str:
        return _hash({
            "version": PAPER_EXECUTION_CHAIN_VERSION,
            "account": self.account.identity_id,
            "positions": [item.identity_id for item in self.positions],
            "orders": [item.identity_id for item in self.orders],
            "snapshot_at": self.snapshot_at.isoformat(),
        })

    def model_visible_positions(self, concrete_contract_id: str) -> tuple[PositionFact, ...]:
        active_orders = tuple(
            item
            for item in self.orders
            if item.concrete_contract_id == concrete_contract_id
            and item.status in _ACTIVE_ORDER_STATUSES
        )
        facts: list[PositionFact] = []
        for position in self.positions:
            if position.concrete_contract_id != concrete_contract_id:
                continue
            direction = (
                Direction.LONG if position.direction.value == "LONG" else Direction.SHORT
            )
            related = tuple(
                item.order_id for item in active_orders if item.direction is position.direction
            )
            protective = tuple(
                item.order_id
                for item in active_orders
                if item.direction is position.direction
                and item.order_role in {OrderRole.PROTECTIVE_STOP, OrderRole.EXIT_STOP}
            )
            facts.append(PositionFact(
                direction=direction,
                quantity=str(position.quantity),
                entry_facts=(
                    ("average_price", str(position.average_price)),
                    ("broker_snapshot_at", position.snapshot_at.isoformat()),
                ),
                protective_orders=protective,
                active_order_ids=related,
            ))
        return tuple(facts)


@dataclass(frozen=True)
class PaperRiskMarketContext:
    latest_bar: LiveCausalBar
    max_age_seconds: int

    def __post_init__(self) -> None:
        if not isinstance(self.latest_bar, LiveCausalBar):
            raise TypeError("paper risk context requires LiveCausalBar")
        if type(self.max_age_seconds) is not int or self.max_age_seconds <= 0:
            raise ValueError("paper risk context requires positive freshness age")

    def is_stale(self, at: datetime) -> bool:
        if not isinstance(at, datetime) or at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("paper risk assessment time must be timezone-aware")
        age = at - self.latest_bar.available_at
        return age.total_seconds() < 0 or age > timedelta(seconds=self.max_age_seconds)


@dataclass(frozen=True)
class PaperExecutionPlan:
    intent_identity: str
    risk_identity: str
    instruction: BrokerOrderInstruction
    logical_execution_identity: str | None = None
    logical_quantity: Decimal | None = None
    logical_intent_identity: str | None = None


class PaperDeterministicExecutionChain:
    """Deep module owning decision -> intent -> risk -> OMS -> audit planning."""

    canonical_execution_chain = True

    def __init__(
        self,
        *,
        strategy_identity: str,
        instrument: str,
        concrete_contract_id: str,
        bridge: JiangheExecutionBridge,
        risk_gate: RiskGate,
        max_market_age_seconds: int,
        oms: OrderManagementSystem | None = None,
        safety_gate: SafetyGate | None = None,
        ledger: RuntimeLedger | None = None,
    ) -> None:
        for value, name in (
            (strategy_identity, "strategy identity"),
            (instrument, "instrument"),
            (concrete_contract_id, "concrete contract"),
        ):
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"paper execution {name} must be non-empty")
        if not isinstance(bridge, JiangheExecutionBridge):
            raise TypeError("paper execution chain requires JiangheExecutionBridge")
        if not isinstance(risk_gate, RiskGate):
            raise TypeError("paper execution chain requires RiskGate")
        if type(max_market_age_seconds) is not int or max_market_age_seconds <= 0:
            raise ValueError("paper execution chain requires positive market freshness age")
        self.strategy_identity = strategy_identity
        self.instrument = instrument
        self.concrete_contract_id = concrete_contract_id
        self.bridge = bridge
        self.risk_gate = risk_gate
        self.max_market_age_seconds = max_market_age_seconds
        self.oms = oms or OrderManagementSystem()
        self.safety_gate = safety_gate or SafetyGate()
        self.ledger = ledger or RuntimeLedger()
        self._conflicts = ConflictResolver()
        self._state: PaperProjectState | None = None

    @property
    def identity_id(self) -> str:
        return _hash({
            "version": PAPER_EXECUTION_CHAIN_VERSION,
            "strategy_identity": self.strategy_identity,
            "instrument": self.instrument,
            "concrete_contract_id": self.concrete_contract_id,
            "bridge_identity": self.bridge.identity_id,
            "risk_identity": self.risk_gate.identity_id,
            "max_market_age_seconds": self.max_market_age_seconds,
        })

    @property
    def project_state(self) -> PaperProjectState:
        if self._state is None:
            raise RuntimeError("PAPER_PROJECT_STATE_NOT_RECONCILED")
        return self._state

    def reconcile_broker_truth(
        self, mirror: PaperBrokerTruthMirror, *, at: datetime
    ) -> PaperProjectState:
        state = PaperProjectState.from_mirror(mirror)
        self._state = state
        self.ledger.append(
            RuntimeLedgerRecordKind.RECONCILIATION,
            state.identity_id,
            ledger_pairs(
                account_id=state.account.account_id,
                broker_snapshot_at=state.snapshot_at.isoformat(),
                position_count=len(state.positions),
                order_count=len(state.orders),
            ),
            at,
        )
        return state

    def model_visible_positions(self) -> tuple[PositionFact, ...]:
        return self.project_state.model_visible_positions(self.concrete_contract_id)

    def apply_broker_events(self, events: tuple[BrokerEvent, ...], *, at: datetime) -> None:
        for event in events:
            self.oms.apply_broker_event(event)
            self.ledger.append(
                RuntimeLedgerRecordKind.BROKER_EVENT,
                event.event_id,
                ledger_pairs(event_type=event.event_type.value, occurred_at=event.occurred_at.isoformat()),
                at,
            )

    def plan(
        self,
        *,
        wake: LiveCausalWake,
        context: tuple[LiveCausalBar, ...],
        decision: NormalizedJiangheDecision,
        connection_state: BrokerConnectionState,
    ) -> tuple[PaperExecutionPlan, ...]:
        if not isinstance(decision, NormalizedJiangheDecision):
            raise TypeError("paper execution chain requires normalized Jianghe decision")
        if not context:
            raise ValueError("paper execution chain requires causal context")
        state = self.project_state
        context_identity = _hash([item.identity for item in context])
        resolution = self.bridge.resolve(
            decision,
            strategy_identity_id=self.strategy_identity,
            instrument=self.instrument,
            concrete_contract_id=self.concrete_contract_id,
            decision_at=wake.observed_at,
            context_identity=context_identity,
        )
        conflict = self._conflicts.resolve(resolution.intents)
        risk_context = PaperRiskMarketContext(
            latest_bar=context[-1], max_age_seconds=self.max_market_age_seconds
        )
        plans: list[PaperExecutionPlan] = []
        for item in conflict.resolutions:
            intent = item.intent
            self.ledger.append(
                RuntimeLedgerRecordKind.INTENT,
                intent.identity_id,
                ledger_pairs(
                    action=intent.action.value,
                    conflict_decision=item.decision.value,
                    decision_identity=decision.identity,
                ),
                wake.observed_at,
            )
            if intent.action is IntentAction.HOLD or item.decision.value != "APPROVED":
                continue
            risk = self.risk_gate.evaluate(
                intent,
                state,
                risk_context,
                safety_blocking=self.safety_gate.is_blocking(),
                connection_connected=connection_state is BrokerConnectionState.CONNECTED,
            )
            self.ledger.append(
                RuntimeLedgerRecordKind.SAFETY if not risk.approved else RuntimeLedgerRecordKind.INTENT,
                risk.identity_id,
                ledger_pairs(approved=risk.approved, reason=risk.reason),
                wake.observed_at,
            )
            if not risk.approved or risk.quantity_for_order is None:
                continue
            order_type = intent.order_type or (
                OrderType.LIMIT if intent.limit_price is not None else OrderType.MARKET
            )
            logical_identity = _hash({
                "version": PAPER_EXECUTION_CHAIN_VERSION,
                "wake_identity": wake.wake_identity,
                "decision_identity": decision.identity,
                "intent_identity": intent.identity_id,
                "risk_identity": risk.identity_id,
            })
            action = (
                OrderAction.OPEN if intent.action is IntentAction.OPEN else OrderAction.CLOSE
            )
            if action is OrderAction.CLOSE:
                if intent.close_children:
                    if risk.quantity_for_order != intent.quantity:
                        raise ExecutionSemanticsRequired(
                            "EXPLICIT_CLOSE_CHILDREN_DISAGREE_WITH_RISK_QUANTITY"
                        )
                    children = tuple(
                        (item.offset, item.quantity) for item in intent.close_children
                    )
                elif self.concrete_contract_id.split(".", 1)[0] in {"SHFE", "INE"}:
                    raise ExecutionSemanticsRequired(
                        "SHFE_INE_CLOSE_OFFSET_POLICY_RESULT_REQUIRED"
                    )
                else:
                    children = ((CloseOffset.CLOSE, risk.quantity_for_order),)
            else:
                children = ((None, risk.quantity_for_order),)
            for ordinal, (close_offset, child_quantity) in enumerate(children):
                request_id = _hash({
                    "logical_execution_identity": logical_identity,
                    "child_ordinal": ordinal,
                    "close_offset": None if close_offset is None else close_offset.value,
                    "quantity": str(child_quantity),
                })
                child_intent_identity = _hash({
                    "logical_intent_identity": intent.identity_id,
                    "client_request_id": request_id,
                })
                request = OrderRequest(
                    client_request_id=request_id,
                    client_order_id=request_id,
                    concrete_contract_id=intent.concrete_contract_id,
                    direction=intent.direction,
                    action=action,
                    order_type=order_type,
                    quantity=child_quantity,
                    close_offset=close_offset,
                    limit_price=intent.limit_price,
                    trigger_price=intent.trigger_price,
                    trigger_condition=intent.trigger_condition,
                    triggered_order_type=intent.triggered_order_type,
                    triggered_limit_price=intent.triggered_limit_price,
                    order_role=intent.order_role,
                    strategy_identity_id=intent.strategy_identity_id,
                    available_at=wake.observed_at,
                    parent_order_id=intent.parent_order_id,
                    oco_group_id=intent.oco_group_id,
                    replace_generation=intent.replace_generation,
                    source_directive_identity=(
                        intent.source_directive_identity or intent.identity_id
                    ),
                )
                order = self.oms.create_order(request, wake.observed_at)
                instruction = BrokerOrderInstruction(
                    client_request_id=request.client_request_id,
                    client_order_id=request.client_order_id,
                    concrete_contract_id=request.concrete_contract_id,
                    direction=request.direction,
                    action=request.action,
                    order_type=request.order_type,
                    quantity=request.quantity,
                    close_offset=request.close_offset,
                    limit_price=request.limit_price,
                    trigger_price=request.trigger_price,
                    trigger_condition=request.trigger_condition,
                    triggered_order_type=request.triggered_order_type,
                    triggered_limit_price=request.triggered_limit_price,
                    order_role=request.order_role,
                    strategy_identity_id=request.strategy_identity_id,
                    available_at=request.available_at,
                    parent_order_id=request.parent_order_id,
                    oco_group_id=request.oco_group_id,
                    replace_generation=request.replace_generation,
                    source_directive_identity=request.source_directive_identity,
                )
                self.ledger.append(
                    RuntimeLedgerRecordKind.ORDER,
                    order.identity_id,
                    ledger_pairs(
                        client_request_id=request_id,
                        intent_identity=intent.identity_id,
                        risk_identity=risk.identity_id,
                        logical_execution_identity=logical_identity,
                    ),
                    wake.observed_at,
                )
                plans.append(PaperExecutionPlan(
                    child_intent_identity,
                    risk.identity_id,
                    instruction,
                    logical_execution_identity=logical_identity,
                    logical_quantity=risk.quantity_for_order,
                    logical_intent_identity=intent.identity_id,
                ))
        return tuple(plans)


__all__ = [
    "PAPER_EXECUTION_CHAIN_VERSION",
    "PaperDeterministicExecutionChain",
    "PaperExecutionPlan",
    "PaperProjectState",
    "PaperRiskMarketContext",
]

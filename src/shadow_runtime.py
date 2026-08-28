"""Shadow Runtime orchestrator — wires the deterministic paper trading chain.

This module composes the full Skeleton v1.0 Trading Loop into one deterministic,
broker-agnostic runtime for the foundation package:

    CompletedBar -> MarketContext -> Strategy.intent -> conflict resolution
    -> RiskGate -> OMS -> BrokerAdapter (PaperBrokerAdapter) -> broker events
    -> reconciliation -> TradingState -> Safety -> RuntimeLedger

It is fully synthetic: no real broker, no network, no candidate strategy
outcome, no real money. The strategy is an injected TEST_ONLY fake strategy
(lives in the test fixture, not in src). Risk/margin/cost numbers are
FIXTURE-ONLY and never permanent real-money limits.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from hashlib import sha256
import json
from typing import Any, Protocol
from zoneinfo import ZoneInfo

from src.broker_adapter import (
    BrokerOrderInstruction,
    OrderRole,
    OrderType,
    StopTriggerCondition,
)
from src.contract_semantics import ContractSpecification, OrderAction
from src.historical_data import NormalizedHistoricalBar
from src.intent import (
    ConflictResolution,
    ConflictResolver,
    IntentAction,
    IntentDecision,
    StrategyIntent,
)
from src.market_context import MarketContext
from src.order_management import Order, OrderManagementSystem, OrderRequest
from src.paper_broker import PaperBrokerAdapter, PaperFillPolicy
from src.reconciliation import ReconciliationReport, reconcile_runtime
from src.risk_gate import RiskDecision, RiskGate, RiskRuleSet
from src.runtime_ledger import RuntimeLedger, RuntimeLedgerRecordKind, ledger_pairs
from src.runtime_recovery import RuntimePersistedState, rebuild_trading_state
from src.safety import SafetyAssessment, SafetyGate
from src.trading_state import (
    EventApplicationResult,
    RuntimeAccountingAssumptions,
    TradingState,
)

SHADOW_RUNTIME_SCHEMA_VERSION = "shadow-runtime-orchestrator-v0.1"


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class RuntimeStrategy(Protocol):
    """TEST_ONLY strategy interface: produce deterministic intents from context."""

    def intents(self, context: MarketContext) -> tuple[StrategyIntent, ...]:
        raise NotImplementedError


@dataclass(frozen=True)
class RuntimeConfiguration:
    """Deterministic runtime configuration (FIXTURE-ONLY numbers, no money)."""

    runtime_id: str
    runtime_version: str
    timezone: str
    starting_capital: Decimal
    contract_specs: tuple[ContractSpecification, ...]
    accounting: RuntimeAccountingAssumptions
    risk_ruleset: RiskRuleSet
    staleness_threshold: timedelta
    broker_id: str = "paper-broker-fixture"
    fill_policy: PaperFillPolicy = PaperFillPolicy.IMMEDIATE_MARKET_AT_REFERENCE

    def __post_init__(self) -> None:
        if not self.runtime_id or not self.runtime_version or not self.timezone:
            raise ValueError("runtime configuration requires id, version and timezone")
        if type(self.starting_capital) is not Decimal or not self.starting_capital.is_finite() or self.starting_capital <= 0:
            raise ValueError("runtime configuration starting capital must be a positive finite Decimal")
        ZoneInfo(self.timezone)
        if not isinstance(self.accounting, RuntimeAccountingAssumptions):
            raise ValueError("runtime configuration requires accounting assumptions")
        if not isinstance(self.risk_ruleset, RiskRuleSet):
            raise ValueError("runtime configuration requires a risk ruleset")
        if not isinstance(self.fill_policy, PaperFillPolicy):
            raise ValueError("runtime configuration requires a PaperFillPolicy")
        if self.staleness_threshold < timedelta(0):
            raise ValueError("runtime configuration staleness threshold cannot be negative")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "runtime_id": self.runtime_id,
                "runtime_version": self.runtime_version,
                "timezone": self.timezone,
                "starting_capital": str(self.starting_capital),
                "contract_specs": [item.identity_id for item in self.contract_specs],
                "accounting": self.accounting.identity_id,
                "risk_ruleset": self.risk_ruleset.identity_id,
                "staleness_threshold": int(self.staleness_threshold.total_seconds()),
                "broker_id": self.broker_id,
                "fill_policy": self.fill_policy.value,
            }
        )


@dataclass(frozen=True)
class RuntimeCycleResult:
    """Deterministic result of one completed-bar runtime cycle."""

    cycle_sequence: int
    context_identity: str
    intents: tuple[StrategyIntent, ...]
    conflict_resolution: ConflictResolution
    risk_decisions: tuple[RiskDecision, ...]
    orders_created: tuple[Order, ...]
    event_applications: tuple[EventApplicationResult, ...]
    reconciliation: ReconciliationReport
    safety: SafetyAssessment
    ledger_tail_identity: str

    def __post_init__(self) -> None:
        if type(self.cycle_sequence) is not int or self.cycle_sequence < 0:
            raise ValueError("cycle sequence must be a non-negative integer")
        if not self.context_identity:
            raise ValueError("cycle result requires a context identity")
        if not isinstance(self.conflict_resolution, ConflictResolution):
            raise ValueError("cycle result requires a conflict resolution")
        if not isinstance(self.reconciliation, ReconciliationReport):
            raise ValueError("cycle result requires a reconciliation report")
        if not isinstance(self.safety, SafetyAssessment):
            raise ValueError("cycle result requires a safety assessment")
        if not self.ledger_tail_identity:
            raise ValueError("cycle result requires a ledger tail identity")


class ShadowRuntime:
    """Deterministic composition of the paper trading chain."""

    def __init__(
        self,
        config: RuntimeConfiguration,
        strategy: RuntimeStrategy,
        *,
        ledger: RuntimeLedger | None = None,
        created_at: datetime | None = None,
        broker: PaperBrokerAdapter | None = None,
        append_start_record: bool = True,
    ) -> None:
        if not isinstance(config, RuntimeConfiguration):
            raise ValueError("ShadowRuntime requires a RuntimeConfiguration")
        if not hasattr(strategy, "intents"):
            raise ValueError("ShadowRuntime requires a strategy with an intents(context) method")
        self._config = config
        self._strategy = strategy
        self._clock_now = created_at if created_at is not None else datetime.now(ZoneInfo(config.timezone))
        if self._clock_now.tzinfo is None:
            raise ValueError("runtime clock must be timezone-aware")

        self._ledger = ledger if ledger is not None else RuntimeLedger()
        self._ledger.append(
            RuntimeLedgerRecordKind.RUNTIME_START,
            config.identity_id,
            ledger_pairs(
                runtime_id=config.runtime_id,
                runtime_version=config.runtime_version,
                created_at=self._clock_now.isoformat(),
            ),
            self._clock_now,
        )

        self._broker = broker if broker is not None else PaperBrokerAdapter(
            broker_id=config.broker_id,
            contract_specs=config.contract_specs,
            accounting=config.accounting,
            starting_capital=config.starting_capital,
            currency=config.accounting.currency,
            fill_policy=config.fill_policy,
            timezone=config.timezone,
        )
        self._state = TradingState(
            runtime_id=config.runtime_id,
            runtime_version=config.runtime_version,
            created_at=self._clock_now,
            starting_capital=config.starting_capital,
            contract_specs=config.contract_specs,
            accounting=config.accounting,
            ledger=self._ledger,
        )
        self._oms = OrderManagementSystem()
        self._risk_gate = RiskGate(config.risk_ruleset)
        self._conflict_resolver = ConflictResolver()
        self._safety_gate = SafetyGate()
        self._cycle_sequence = 0
        self._last_reconciliation: ReconciliationReport | None = None
        self._last_safety: SafetyAssessment | None = None
        self._directive_order_ids: dict[str, str] = {}
        self._protective_pending: set[tuple[str, str, str]] = set()
        self._protective_replacement_in_progress: set[tuple[str, str, str]] = set()

    # -- component access ------------------------------------------------------

    @property
    def config(self) -> RuntimeConfiguration:
        return self._config

    @property
    def ledger(self) -> RuntimeLedger:
        return self._ledger

    @property
    def broker(self) -> PaperBrokerAdapter:
        return self._broker

    @property
    def state(self) -> TradingState:
        return self._state

    @property
    def oms(self) -> OrderManagementSystem:
        return self._oms

    @property
    def risk_gate(self) -> RiskGate:
        return self._risk_gate

    @property
    def safety_gate(self) -> SafetyGate:
        return self._safety_gate

    @property
    def last_reconciliation(self) -> ReconciliationReport | None:
        return self._last_reconciliation

    @property
    def last_safety(self) -> SafetyAssessment | None:
        return self._last_safety

    def trip_kill_switch(self, reason: str, at: datetime) -> None:
        self._safety_gate.trip_kill_switch(reason, at)
        self._ledger.append(
            RuntimeLedgerRecordKind.KILL_SWITCH,
            reason,
            ledger_pairs(kill_switch_action="TRIP", reason=reason, at=at.isoformat()),
            at,
        )

    def disarm_kill_switch(self, reason: str, at: datetime) -> None:
        self._safety_gate.disarm_kill_switch(reason, at)
        self._ledger.append(
            RuntimeLedgerRecordKind.KILL_SWITCH,
            reason,
            ledger_pairs(kill_switch_action="DISARM", reason=reason, at=at.isoformat()),
            at,
        )

    # -- main cycle ------------------------------------------------------------

    def on_completed_bar(self, bar: NormalizedHistoricalBar) -> RuntimeCycleResult:
        """Run one deterministic cycle for one completed bar (full chain)."""
        if not isinstance(bar, NormalizedHistoricalBar):
            raise ValueError("runtime cycle requires a NormalizedHistoricalBar")
        cycle_sequence = self._cycle_sequence
        self._cycle_sequence += 1
        now = bar.completed_bar.available_at

        # 1. MarketContext.
        context = MarketContext(
            instrument=bar.completed_bar.instrument,
            concrete_contract_id=bar.concrete_instrument,
            last_completed_bar=bar,
            observed_at=now,
            staleness_threshold=self._config.staleness_threshold,
            contract_spec=self._state.contract_spec(bar.concrete_instrument),
            session_metadata_version=None,
        )
        self._ledger.append(
            RuntimeLedgerRecordKind.BROKER_EVENT,
            context.identity_id,
            ledger_pairs(
                cycle_sequence=str(cycle_sequence),
                market_context_identity=context.identity_id,
                bar_start=context.completed_bar.start.isoformat(),
                bar_available_at=context.available_at.isoformat(),
                observed_at=context.observed_at.isoformat(),
            ),
            now,
        )

        # 2. Strategy.intent (TEST_ONLY fake strategy).
        intents = self._strategy.intents(context)
        orders_created: list[Order] = []
        # A real strategy adapter may additionally expose machine directives that
        # are not reducible to the current generic MARKET intent vocabulary
        # (for example a protective-stop pending/replace fact).  Record them
        # losslessly in the ledger; never silently translate them into a fill.
        directives_at = getattr(self._strategy, "directives_at", None)
        if callable(directives_at):
            for directive in directives_at(context.available_at):
                self._ledger.append(
                    RuntimeLedgerRecordKind.INTENT,
                    directive.identity_id,
                    ledger_pairs(
                        directive_event_type=directive.event_type,
                        directive_available_at=directive.available_at.isoformat(),
                        directive_reference_price=(
                            "" if directive.reference_price is None else str(directive.reference_price)
                        ),
                        directive_oco_group_id=directive.oco_group_id or "",
                    ),
                    now,
                )
                self._apply_execution_directive(directive, context, orders_created)

        # 3. Deterministic conflict resolution.
        conflict = self._conflict_resolver.resolve(intents)
        for resolution in conflict.resolutions:
            self._ledger.append(
                RuntimeLedgerRecordKind.INTENT,
                resolution.identity_id,
                ledger_pairs(
                    intent_id=resolution.intent.intent_id,
                    strategy_identity_id=resolution.intent.strategy_identity_id,
                    concrete_contract_id=resolution.intent.concrete_contract_id,
                    action=resolution.intent.action.value,
                    decision=resolution.decision.value,
                    reason=resolution.reason,
                ),
                now,
            )

        # 4. RiskGate + Safety gate (Safety overrides strategies).
        risk_decisions: list[RiskDecision] = []
        blocking = self._safety_gate.is_blocking() or bool(self._protective_pending) or bool(self._protective_replacement_in_progress)
        for resolution in conflict.resolutions:
            intent = resolution.intent
            if intent.action is IntentAction.HOLD:
                continue
            if resolution.decision is not IntentDecision.APPROVED:
                continue
            decision = self._risk_gate.evaluate(
                intent,
                self._state,
                context,
                safety_blocking=blocking,
                connection_connected=self._broker.connection_state.value == "CONNECTED",
            )
            risk_decisions.append(decision)
            if not decision.approved or decision.quantity_for_order is None:
                continue
            self._submit_order(intent, decision.quantity_for_order, now, context, orders_created)

        # 5. Broker event flow (fills / resting evaluation).
        if self._config.fill_policy is PaperFillPolicy.RESTING_ON_COMPLETED_BAR or any(
            order.order_type is OrderType.STOP_MARKET for order in self._oms.open_orders()
        ):
            self._broker.ingest_completed_bar(bar, at=now)
        event_applications = self.drain_and_apply_events(now)

        # 6. Reconciliation (fail closed on mismatch).
        reconciliation = self.reconcile(now)
        self._ledger.append(
            RuntimeLedgerRecordKind.RECONCILIATION,
            reconciliation.identity_id,
            ledger_pairs(
                ok="true" if reconciliation.ok else "false",
                account_match="true" if reconciliation.account_match else "false",
                position_match="true" if reconciliation.position_match else "false",
                order_match="true" if reconciliation.order_match else "false",
                mismatches=";".join(reconciliation.mismatches),
            ),
            now,
        )

        # 7. Safety.
        safety = self._safety_gate.assess(
            state=self._state,
            clock_now=now,
            context=context,
            connection_state=self._broker.connection_state,
            reconciliation=reconciliation,
            protective_stop_pending=bool(self._protective_pending),
            protective_stop_replacement_in_progress=bool(self._protective_replacement_in_progress),
        )
        self._last_safety = safety
        for violation in safety.violations:
            self._ledger.append(
                RuntimeLedgerRecordKind.SAFETY,
                violation.identity_id,
                ledger_pairs(
                    kind=violation.kind.value,
                    detail=violation.detail,
                    observed_at=violation.observed_at.isoformat(),
                    blocking="true" if safety.blocking else "false",
                ),
                now,
            )

        # Only clear after broker events and the safety observation are both
        # durably recorded; an unresolved ambiguity has already become a
        # persistent Safety violation through TradingState.
        self._protective_replacement_in_progress.clear()

        return RuntimeCycleResult(
            cycle_sequence=cycle_sequence,
            context_identity=context.identity_id,
            intents=tuple(intents),
            conflict_resolution=conflict,
            risk_decisions=tuple(risk_decisions),
            orders_created=tuple(orders_created),
            event_applications=tuple(event_applications),
            reconciliation=reconciliation,
            safety=safety,
            ledger_tail_identity=self._ledger.tail_identity,
        )

    def _apply_execution_directive(self, directive: Any, context: MarketContext, orders_created: list[Order]) -> None:
        """Translate the real Holy Grail machine facts into generic OMS orders.

        This seam deliberately understands only the adapter's stable directive
        fields; generic OMS/PaperBroker remain strategy agnostic.
        """
        event = directive.event_type
        key = (directive.strategy_identity_id, directive.concrete_contract_id, directive.direction.value)
        if event == "ENTRY_ORDER_RESTING":
            if directive.machine_event_identity in self._directive_order_ids:
                return
            self._submit_execution_order(
                directive=directive, action=OrderAction.OPEN, role=OrderRole.ENTRY_STOP,
                trigger_price=directive.reference_price, parent_order_id=None,
                replace_generation=0, orders_created=orders_created,
            )
            return
        if event == "PROTECTIVE_STOP_PENDING":
            self._protective_pending.add(key)
            return
        if event == "PROTECTIVE_STOP_ACTIVE":
            self._protective_pending.discard(key)
            if directive.machine_event_identity in self._directive_order_ids:
                return
            parent = self._latest_entry_order_id(key)
            self._submit_execution_order(
                directive=directive, action=OrderAction.CLOSE, role=OrderRole.PROTECTIVE_STOP,
                trigger_price=directive.reference_price, parent_order_id=parent,
                replace_generation=0, orders_created=orders_created,
            )
            return
        if event == "STOP_REPLACED":
            active = self._active_protective_order(key)
            if active is None or directive.reference_price is None:
                return
            self._protective_replacement_in_progress.add(key)
            if self._stop_crossed_in_current_completed_bar(active, context):
                self._broker.mark_order_ambiguous(
                    active.order_id, "STOP_REPLACE_TRIGGER_AMBIGUOUS_INTRABAR_SEQUENCE",
                    at=context.available_at,
                )
                return
            self._oms.cancel(active.order_id, context.available_at)
            self._broker.cancel_order(active.order_id, at=context.available_at)
            self._submit_execution_order(
                directive=directive, action=OrderAction.CLOSE, role=OrderRole.PROTECTIVE_STOP,
                trigger_price=directive.reference_price, parent_order_id=active.parent_order_id,
                replace_generation=active.replace_generation + 1, orders_created=orders_created,
            )

    @staticmethod
    def _stop_crossed_in_current_completed_bar(order: Order, context: MarketContext) -> bool:
        if order.trigger_price is None:
            return False
        buy_stop = (order.action is OrderAction.OPEN and order.direction.value == "LONG") or (order.action is OrderAction.CLOSE and order.direction.value == "SHORT")
        return context.last_completed_bar.high >= order.trigger_price if buy_stop else context.last_completed_bar.low <= order.trigger_price

    def _latest_entry_order_id(self, key: tuple[str, str, str]) -> str | None:
        strategy, contract, _ = key
        entries = [order for order in self._oms.orders() if order.strategy_identity_id == strategy and order.concrete_contract_id == contract and order.order_role is OrderRole.ENTRY_STOP]
        return max(entries, key=lambda item: item.created_at or self._clock_now).order_id if entries else None

    def _active_protective_order(self, key: tuple[str, str, str]) -> Order | None:
        strategy, contract, _ = key
        candidates = [order for order in self._oms.open_orders() if order.strategy_identity_id == strategy and order.concrete_contract_id == contract and order.order_role is OrderRole.PROTECTIVE_STOP]
        return max(candidates, key=lambda item: item.replace_generation) if candidates else None

    def _submit_execution_order(self, *, directive: Any, action: OrderAction, role: OrderRole, trigger_price: Decimal | None, parent_order_id: str | None, replace_generation: int, orders_created: list[Order]) -> Order:
        if trigger_price is None:
            raise ValueError("machine stop directive requires a trigger price")
        buy_stop = (
            (action is OrderAction.OPEN and directive.direction.value == "LONG")
            or (action is OrderAction.CLOSE and directive.direction.value == "SHORT")
        )
        trigger_condition = (
            StopTriggerCondition.AT_OR_ABOVE
            if buy_stop
            else StopTriggerCondition.AT_OR_BELOW
        )
        request_id = _canonical_hash({"runtime": self._config.runtime_id, "directive": directive.machine_event_identity, "role": role.value, "replace_generation": replace_generation})
        request = OrderRequest(
            client_request_id=request_id, client_order_id=request_id,
            concrete_contract_id=directive.concrete_contract_id, direction=directive.direction,
            action=action, order_type=OrderType.STOP_MARKET, quantity=directive.quantity,
            strategy_identity_id=directive.strategy_identity_id, trigger_price=trigger_price,
            trigger_condition=trigger_condition, triggered_order_type=OrderType.MARKET,
            order_role=role, available_at=directive.available_at, parent_order_id=parent_order_id,
            oco_group_id=directive.oco_group_id, replace_generation=replace_generation,
            source_directive_identity=directive.machine_event_identity,
        )
        order = self._oms.create_order(request, directive.available_at)
        instruction = BrokerOrderInstruction(
            client_request_id=request.client_request_id, client_order_id=request.client_order_id,
            concrete_contract_id=request.concrete_contract_id, direction=request.direction,
            action=request.action, order_type=request.order_type, quantity=request.quantity,
            trigger_price=request.trigger_price, trigger_condition=request.trigger_condition,
            triggered_order_type=request.triggered_order_type,
            triggered_limit_price=request.triggered_limit_price, order_role=request.order_role,
            strategy_identity_id=request.strategy_identity_id, available_at=request.available_at,
            parent_order_id=request.parent_order_id, oco_group_id=request.oco_group_id,
            replace_generation=request.replace_generation, source_directive_identity=request.source_directive_identity,
        )
        self._broker.submit_order(instruction, at=directive.available_at)
        self._directive_order_ids[directive.machine_event_identity] = order.order_id
        orders_created.append(order)
        return order

    def drain_and_apply_events(self, at: datetime | None = None) -> tuple[EventApplicationResult, ...]:
        """Drain pending broker events and apply them to TradingState + OMS."""
        results: list[EventApplicationResult] = []
        for event in self._broker.drain_events():
            result = self._state.apply_broker_event(event)
            results.append(result)
            if result.applied:
                self._oms.apply_broker_event(event)
        return tuple(results)

    def reconcile(self, at: datetime) -> ReconciliationReport:
        """Reconcile local TradingState against the paper broker snapshot."""
        report = reconcile_runtime(
            self._state,
            self._broker.fetch_account_snapshot(),
            self._broker.fetch_position_snapshot(),
            self._broker.fetch_order_snapshot(),
            at,
        )
        self._last_reconciliation = report
        return report

    def _submit_order(
        self,
        intent: StrategyIntent,
        quantity: Decimal,
        now: datetime,
        context: MarketContext,
        orders_created: list[Order],
    ) -> Order:
        client_request_id = _canonical_hash(
            {
                "runtime_id": self._config.runtime_id,
                "intent_id": intent.intent_id,
                "quantity": str(quantity),
                "decision_at": intent.decision_at.isoformat(),
            }
        )
        request = OrderRequest(
            client_request_id=client_request_id,
            concrete_contract_id=intent.concrete_contract_id,
            direction=intent.direction,
            action=(
                OrderAction.OPEN if intent.action is IntentAction.OPEN else OrderAction.CLOSE
            ),
            order_type=OrderType.MARKET,
            quantity=quantity,
            strategy_identity_id=intent.strategy_identity_id,
        )
        order = self._oms.create_order(request, created_at=now)
        instruction = BrokerOrderInstruction(
            client_request_id=request.client_request_id,
            concrete_contract_id=request.concrete_contract_id,
            direction=request.direction,
            action=request.action,
            order_type=request.order_type,
            quantity=request.quantity,
            limit_price=request.limit_price,
        )
        self._broker.submit_order(instruction, reference_price=context.latest_price(), at=now)
        self._ledger.append(
            RuntimeLedgerRecordKind.ORDER,
            order.order_id,
            ledger_pairs(
                order_id=order.order_id,
                client_request_id=order.client_request_id,
                concrete_contract_id=order.concrete_contract_id,
                direction=order.direction.value,
                action=order.action.value,
                quantity=str(quantity),
            ),
            now,
        )
        orders_created.append(order)
        return order

    # -- crash / restart recovery ----------------------------------------------

    def capture_persisted_state(self, at: datetime) -> RuntimePersistedState:
        from src.runtime_recovery import capture_persisted_state as _capture

        return _capture(self._state, at)

    @classmethod
    def rebuild(
        cls,
        persisted: RuntimePersistedState,
        config: RuntimeConfiguration,
        strategy: RuntimeStrategy,
        ledger: RuntimeLedger,
        broker_snapshot: Any,
        recovery_recorded_at: datetime,
    ) -> "ShadowRuntime":
        """Rebuild a runtime from persisted facts (fail closed on mismatch).

        The paper broker first restores its deterministic snapshot fixture, the
        local state is rebuilt from the persisted projection without re-applying
        old events, and the caller reconciles the rebuilt state against the
        broker snapshot.
        """
        broker = PaperBrokerAdapter(
            broker_id=config.broker_id,
            contract_specs=config.contract_specs,
            accounting=config.accounting,
            starting_capital=config.starting_capital,
            currency=config.accounting.currency,
            fill_policy=config.fill_policy,
            timezone=config.timezone,
        )
        broker.restore_snapshot(broker_snapshot)
        restored_state = rebuild_trading_state(
            persisted,
            contract_specs=config.contract_specs,
            accounting=config.accounting,
            ledger=ledger,
            recovery_recorded_at=recovery_recorded_at,
        )
        runtime = cls(
            config,
            strategy,
            ledger=ledger,
            created_at=persisted.created_at,
            broker=broker,
            append_start_record=False,
        )
        runtime._state = restored_state
        restored_orders: list[Order] = []
        for item in broker_snapshot.orders:
            restored_orders.append(Order(
                order_id=item.order_id, client_request_id=item.client_request_id,
                concrete_contract_id=item.concrete_contract_id, direction=item.direction,
                action=item.action, order_type=item.order_type, quantity=item.quantity,
                status=item.status, strategy_identity_id=item.strategy_identity_id,
                limit_price=item.limit_price, trigger_price=item.trigger_price,
                order_role=item.order_role, client_order_id=item.client_order_id,
                available_at=item.available_at, parent_order_id=item.parent_order_id,
                oco_group_id=item.oco_group_id, replace_generation=item.replace_generation,
                source_directive_identity=item.source_directive_identity,
                filled_quantity=item.filled_quantity, average_fill_price=item.average_fill_price,
                created_at=item.created_at, updated_at=item.updated_at,
            ))
        runtime._oms.restore_orders(restored_orders)
        runtime._directive_order_ids = {
            item.source_directive_identity: item.order_id
            for item in restored_orders if item.source_directive_identity
        }
        return runtime

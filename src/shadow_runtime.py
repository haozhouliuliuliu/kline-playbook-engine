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

from src.broker_adapter import BrokerOrderInstruction, OrderType
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
        orders_created: list[Order] = []
        blocking = self._safety_gate.is_blocking()
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
        if self._config.fill_policy is PaperFillPolicy.RESTING_ON_COMPLETED_BAR:
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

    def drain_and_apply_events(self, at: datetime | None = None) -> tuple[EventApplicationResult, ...]:
        """Drain pending broker events and apply them to TradingState + OMS."""
        results: list[EventApplicationResult] = []
        for event in self._broker.drain_events():
            self._oms.apply_broker_event(event)
            results.append(self._state.apply_broker_event(event))
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
        return runtime

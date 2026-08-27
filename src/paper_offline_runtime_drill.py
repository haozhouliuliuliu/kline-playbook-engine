"""Offline-only PAPER composition/fault-injection harness.

This module is deliberately TEST/ENGINEERING ONLY. It composes the project-owned
live causal context, wake journal, PAPER readiness supervisor, broker mirror and
order-recovery journal without creating credentials, provider requests or a real
broker session.

The harness does not freeze sizing, execution-price, close-offset, product or
permanent risk policy. A caller must inject a trader callback and a deterministic
risk planner. Tests may use explicit fixture-only policies; production PAPER
activation remains behind separate Owner/tool/machine authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from typing import Protocol, Sequence

from src.broker_adapter import BrokerOrderInstruction
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_live_causal_context import LiveCausalBar, LiveCausalContextBuilder, LiveCausalWake
from src.paper_order_journal import BROKER_ORDER_ID_KNOWN, PREPARED, PaperOrderJournal
from src.paper_supervisor import PaperRuntimeSupervisor, PaperSupervisorAssessment
from src.paper_wake_journal import PaperWakeJournal
from src.runtime_events import BrokerConnectionState

PAPER_OFFLINE_RUNTIME_DRILL_VERSION = "KPE_PAPER_OFFLINE_RUNTIME_DRILL_V0_1"


def _hash(payload: object) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _aware(value: datetime, name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")
    return value


def _text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty")
    return value.strip()


@dataclass(frozen=True)
class OfflinePaperTraderDecision:
    """One fake/offline cognition result; contains no execution policy."""

    decision_identity: str
    summary: str = "OFFLINE_TEST_ONLY"

    def __post_init__(self) -> None:
        _text(self.decision_identity, "offline decision identity")
        _text(self.summary, "offline decision summary")


@dataclass(frozen=True)
class OfflinePaperOrderPlan:
    """Fixture/adapter result after deterministic risk admission."""

    intent_identity: str
    risk_identity: str
    instruction: BrokerOrderInstruction

    def __post_init__(self) -> None:
        _text(self.intent_identity, "offline intent identity")
        _text(self.risk_identity, "offline risk identity")
        if not isinstance(self.instruction, BrokerOrderInstruction):
            raise ValueError("offline order plan requires BrokerOrderInstruction")


@dataclass(frozen=True)
class OfflinePaperWakeResult:
    wake_identity: str
    decision_identity: str
    client_request_id: str | None
    broker_order_id: str | None


class OfflinePaperTrader(Protocol):
    def decide(self, *, wake: LiveCausalWake,
               context: tuple[LiveCausalBar, ...]) -> OfflinePaperTraderDecision: ...


class OfflinePaperRiskPlanner(Protocol):
    def plan(self, *, wake: LiveCausalWake, context: tuple[LiveCausalBar, ...],
             decision: OfflinePaperTraderDecision) -> OfflinePaperOrderPlan | None: ...


class OfflineJournaledPaperBroker(Protocol):
    """Extra contract required by this drill to prevent accidental real use."""

    offline_test_only: bool
    journal_managed_execution: bool

    @property
    def connection_state(self) -> BrokerConnectionState: ...

    def set_observed_at(self, at: datetime) -> None: ...
    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
    def submit_order(self, instruction: BrokerOrderInstruction) -> str: ...
    def cancel_order(self, order_id: str) -> None: ...
    def fetch_account_snapshot(self): ...
    def fetch_position_snapshot(self): ...
    def fetch_order_snapshot(self): ...


class PaperOfflineRuntimeDrill:
    """Project-owned startup + wake + fake execution composition drill."""

    def __init__(
        self, *, trader_identity: str, concrete_contract_id: str,
        context_builder: LiveCausalContextBuilder, wake_journal: PaperWakeJournal,
        order_journal: PaperOrderJournal, broker_mirror: PaperBrokerTruthMirror,
        supervisor: PaperRuntimeSupervisor, broker: OfflineJournaledPaperBroker,
        trader: OfflinePaperTrader, risk_planner: OfflinePaperRiskPlanner,
        max_broker_snapshot_age_seconds: int = 30,
    ) -> None:
        self.trader_identity = _text(trader_identity, "offline trader identity")
        self.concrete_contract_id = _text(concrete_contract_id, "offline concrete contract")
        if not isinstance(context_builder, LiveCausalContextBuilder):
            raise ValueError("offline drill requires LiveCausalContextBuilder")
        if not isinstance(wake_journal, PaperWakeJournal):
            raise ValueError("offline drill requires PaperWakeJournal")
        if not isinstance(order_journal, PaperOrderJournal):
            raise ValueError("offline drill requires PaperOrderJournal")
        if not isinstance(broker_mirror, PaperBrokerTruthMirror):
            raise ValueError("offline drill requires PaperBrokerTruthMirror")
        if not isinstance(supervisor, PaperRuntimeSupervisor):
            raise ValueError("offline drill requires PaperRuntimeSupervisor")
        if getattr(broker, "offline_test_only", False) is not True:
            raise PermissionError("OFFLINE_PAPER_DRILL_REQUIRES_FAKE_BROKER")
        if getattr(broker, "journal_managed_execution", False) is not True:
            raise ValueError("offline drill requires journal-managed fake broker")
        if type(max_broker_snapshot_age_seconds) is not int or max_broker_snapshot_age_seconds < 0:
            raise ValueError("offline broker snapshot age must be non-negative integer")
        self.context_builder = context_builder
        self.wake_journal = wake_journal
        self.order_journal = order_journal
        self.broker_mirror = broker_mirror
        self.supervisor = supervisor
        self.broker = broker
        self.trader = trader
        self.risk_planner = risk_planner
        self.max_broker_snapshot_age_seconds = max_broker_snapshot_age_seconds
        self.market_bootstrapped = context_builder.bootstrap_done
        self.market_sequence_ok = context_builder.bootstrap_done
        self.trader_runtime_ready = False

    def _set_clock(self, at: datetime) -> None:
        _aware(at, "offline drill clock")
        self.broker.set_observed_at(at)

    def assess(self, *, at: datetime,
               concrete_contract_id: str | None = None) -> PaperSupervisorAssessment:
        return self.supervisor.assess(
            assessed_at=_aware(at, "offline drill assessment time"),
            market_bootstrapped=self.market_bootstrapped,
            market_sequence_ok=self.market_sequence_ok,
            trader_runtime_ready=self.trader_runtime_ready,
            max_broker_snapshot_age_seconds=self.max_broker_snapshot_age_seconds,
            concrete_contract_id=concrete_contract_id,
        )

    def connect(self, *, at: datetime) -> PaperSupervisorAssessment:
        """Prove authority -> connect -> broker-truth bootstrap ordering."""
        self._set_clock(at)
        before = self.assess(at=at)
        if not before.can_connect:
            raise PermissionError("OFFLINE_PAPER_CONNECT_NOT_READY:" + ";".join(before.connect_blockers))
        self.broker.connect()
        self.broker_mirror.set_connection_state(self.broker.connection_state)
        self.refresh_broker_truth(at=at)
        return self.assess(at=at)

    def disconnect(self, *, at: datetime) -> None:
        self._set_clock(at)
        self.broker.disconnect()
        self.broker_mirror.set_connection_state(self.broker.connection_state)

    def bootstrap_market(self, bars: Sequence[object], *, observed_at: datetime) -> None:
        """Bootstrap causal market state only after broker truth is available."""
        _aware(observed_at, "offline market bootstrap time")
        if self.broker.connection_state is not BrokerConnectionState.CONNECTED:
            raise RuntimeError("OFFLINE_PAPER_BOOTSTRAP_REQUIRES_CONNECTED_BROKER")
        if self.broker_mirror.snapshot is None:
            raise RuntimeError("OFFLINE_PAPER_BOOTSTRAP_REQUIRES_BROKER_TRUTH")
        self.context_builder.bootstrap(bars, observed_at=observed_at)
        self.market_bootstrapped = True
        self.market_sequence_ok = True

    def mark_trader_runtime_ready(self, ready: bool = True) -> None:
        if type(ready) is not bool:
            raise ValueError("trader runtime readiness must be bool")
        self.trader_runtime_ready = ready

    def mark_market_sequence_broken(self) -> None:
        self.market_sequence_ok = False

    def refresh_broker_truth(self, *, at: datetime) -> tuple[str, ...]:
        """Refresh account/position/order truth and reconcile durable attempts."""
        self._set_clock(at)
        self.broker_mirror.set_connection_state(self.broker.connection_state)
        if self.broker.connection_state is not BrokerConnectionState.CONNECTED:
            return ("BROKER_DISCONNECTED",)
        account = self.broker.fetch_account_snapshot()
        positions = tuple(self.broker.fetch_position_snapshot())
        orders = tuple(self.broker.fetch_order_snapshot())
        self.broker_mirror.refresh(account=account, positions=positions, orders=orders, observed_at=at)
        return self.order_journal.reconcile_broker_orders(orders, observed_at=at)

    def process_closed_minutes(self, bars: Sequence[object], *, observed_at: datetime
                               ) -> tuple[OfflinePaperWakeResult, ...]:
        """Drive live closed minutes through wake -> fake cognition -> fake PAPER."""
        _aware(observed_at, "offline live observation time")
        if not self.market_bootstrapped or not self.market_sequence_ok:
            raise RuntimeError("OFFLINE_PAPER_MARKET_NOT_READY")
        if not self.trader_runtime_ready:
            raise RuntimeError("OFFLINE_PAPER_TRADER_NOT_READY")
        self._set_clock(observed_at)
        results: list[OfflinePaperWakeResult] = []
        for wake in self.context_builder.observe(bars, observed_at=observed_at):
            context = self.context_builder.context_for_wake(wake)
            self.context_builder.admit_wake_to_journal(
                wake, journal=self.wake_journal, trader_identity=self.trader_identity,
                concrete_contract_id=self.concrete_contract_id)
            self.assess(at=observed_at).require_observation_ready()
            request_id = _hash({"schema_version": PAPER_OFFLINE_RUNTIME_DRILL_VERSION,
                                "kind": "OFFLINE_TRADER_DISPATCH",
                                "trader_identity": self.trader_identity,
                                "wake_identity": wake.wake_identity})
            self.wake_journal.mark_dispatch_started(wake.wake_identity, request_id=request_id, at=observed_at)
            decision = self.trader.decide(wake=wake, context=context)
            if not isinstance(decision, OfflinePaperTraderDecision):
                raise TypeError("offline trader returned an invalid decision")
            self.wake_journal.mark_decision_committed(
                wake.wake_identity, decision_identity=decision.decision_identity, at=observed_at)
            plan = self.risk_planner.plan(wake=wake, context=context, decision=decision)
            if plan is None:
                results.append(OfflinePaperWakeResult(wake.wake_identity, decision.decision_identity, None, None))
                continue
            if not isinstance(plan, OfflinePaperOrderPlan):
                raise TypeError("offline risk planner returned an invalid order plan")
            instruction = plan.instruction
            if instruction.concrete_contract_id != self.concrete_contract_id:
                raise ValueError("OFFLINE_PAPER_ORDER_CONTRACT_MISMATCH")
            self.assess(at=observed_at, concrete_contract_id=self.concrete_contract_id).require_order_ready()
            self.order_journal.prepare(
                client_request_id=instruction.client_request_id,
                trader_identity=self.trader_identity, wake_identity=wake.wake_identity,
                decision_identity=decision.decision_identity, intent_identity=plan.intent_identity,
                risk_identity=plan.risk_identity, concrete_contract_id=self.concrete_contract_id,
                prepared_at=observed_at)
            broker_order_id = self.broker.submit_order(instruction)
            if self.order_journal.get(instruction.client_request_id).status == PREPARED:
                raise RuntimeError("FAKE_BROKER_FAILED_TO_JOURNAL_SUBMIT_ATTEMPT")
            blockers = self.refresh_broker_truth(at=observed_at)
            if blockers:
                raise RuntimeError("OFFLINE_PAPER_RECOVERY_BLOCKED:" + ";".join(blockers))
            results.append(OfflinePaperWakeResult(
                wake.wake_identity, decision.decision_identity,
                instruction.client_request_id, broker_order_id))
        return tuple(results)

    def cancel_order(self, client_request_id: str, *, at: datetime) -> tuple[str, ...]:
        """Risk-reducing cancel remains separate from new-risk readiness."""
        attempt = self.order_journal.get(_text(client_request_id, "offline cancel client request id"))
        if attempt.status != BROKER_ORDER_ID_KNOWN or not attempt.broker_order_id:
            raise RuntimeError("OFFLINE_PAPER_CANCEL_REQUIRES_KNOWN_ORDER")
        self._set_clock(at)
        self.broker.cancel_order(attempt.broker_order_id)
        return self.refresh_broker_truth(at=at)

    def cancel_then_replace(
        self, *, original_client_request_id: str, child_plan: OfflinePaperOrderPlan,
        wake_identity: str, decision_identity: str, replacement_generation: int,
        at: datetime,
    ) -> str:
        """Safe composite replace: durable child -> cancel -> broker truth -> one child submit."""
        original = self.order_journal.get(_text(original_client_request_id, "replace original request id"))
        _text(wake_identity, "replace wake identity")
        _text(decision_identity, "replace decision identity")
        if not isinstance(child_plan, OfflinePaperOrderPlan):
            raise ValueError("replace requires OfflinePaperOrderPlan")
        if type(replacement_generation) is not int or replacement_generation <= 0:
            raise ValueError("replacement generation must be positive integer")
        if original.status != BROKER_ORDER_ID_KNOWN or not original.broker_order_id:
            raise RuntimeError("OFFLINE_PAPER_REPLACE_REQUIRES_KNOWN_ORIGINAL")
        instruction = child_plan.instruction
        if instruction.concrete_contract_id != self.concrete_contract_id:
            raise ValueError("OFFLINE_PAPER_REPLACE_CONTRACT_MISMATCH")
        self.order_journal.prepare(
            client_request_id=instruction.client_request_id, trader_identity=self.trader_identity,
            wake_identity=wake_identity, decision_identity=decision_identity,
            intent_identity=child_plan.intent_identity, risk_identity=child_plan.risk_identity,
            concrete_contract_id=self.concrete_contract_id, prepared_at=at)
        cancel = self.order_journal.prepare_cancel_for_broker_order(original.broker_order_id, at=at)
        replace_id = _hash({"schema_version": PAPER_OFFLINE_RUNTIME_DRILL_VERSION,
                            "kind": "CANCEL_THEN_REPLACE",
                            "original_client_request_id": original_client_request_id,
                            "child_client_request_id": instruction.client_request_id,
                            "replacement_generation": replacement_generation,
                            "replacement_intent_identity": child_plan.intent_identity})
        self.order_journal.prepare_replace(
            replace_operation_id=replace_id, original_client_request_id=original_client_request_id,
            replacement_generation=replacement_generation,
            replacement_intent_identity=child_plan.intent_identity,
            cancel_operation_id=cancel.cancel_operation_id,
            child_client_request_id=instruction.client_request_id, prepared_at=at)
        self._set_clock(at)
        self.broker.cancel_order(original.broker_order_id)
        self.refresh_broker_truth(at=at)
        resolved_cancel = self.order_journal.get_cancel(cancel.cancel_operation_id)
        if resolved_cancel.status != "CANCEL_RESOLVED" or resolved_cancel.final_order_status != "CANCELLED":
            raise RuntimeError("OFFLINE_PAPER_REPLACE_CANCEL_UNRESOLVED")
        self.order_journal.authorize_replacement_child(replace_id, at=at)
        self.assess(at=at, concrete_contract_id=self.concrete_contract_id).require_order_ready()
        broker_order_id = self.broker.submit_order(instruction)
        if self.order_journal.get(instruction.client_request_id).status == PREPARED:
            raise RuntimeError("FAKE_BROKER_FAILED_TO_JOURNAL_REPLACEMENT_SUBMIT")
        blockers = self.refresh_broker_truth(at=at)
        if blockers:
            raise RuntimeError("OFFLINE_PAPER_REPLACEMENT_RECOVERY_BLOCKED:" + ";".join(blockers))
        return broker_order_id

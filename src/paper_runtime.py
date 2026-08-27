"""Broker-neutral realtime PAPER runtime coordinator.

This module composes the project-owned live causal context, durable wake/order
journals, readiness supervisor, broker-truth mirror, trader callback and
project-owned deterministic risk planner. It performs no provider, credential or
network work by import or construction.

External effects occur only through an injected broker adapter when a caller
explicitly invokes connect/submit/cancel and the existing PAPER authority,
activation-profile and runtime gates permit the action.

Strategy-result-dependent sizing, execution-price, close-offset, permanent risk
and product policy are deliberately not defined here; callers must inject an
explicit planner/policy under the applicable authority.
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

PAPER_RUNTIME_COORDINATOR_VERSION = "KPE_PAPER_RUNTIME_COORDINATOR_V0_1"


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
class PaperTraderDecision:
    decision_identity: str
    summary: str = ""

    def __post_init__(self) -> None:
        _text(self.decision_identity, "paper decision identity")
        if not isinstance(self.summary, str):
            raise ValueError("paper decision summary must be text")


@dataclass(frozen=True)
class PaperOrderPlan:
    intent_identity: str
    risk_identity: str
    instruction: BrokerOrderInstruction

    def __post_init__(self) -> None:
        _text(self.intent_identity, "paper intent identity")
        _text(self.risk_identity, "paper risk identity")
        if not isinstance(self.instruction, BrokerOrderInstruction):
            raise ValueError("paper order plan requires BrokerOrderInstruction")


@dataclass(frozen=True)
class PaperWakeResult:
    wake_identity: str
    decision_identity: str
    client_request_id: str | None
    broker_order_id: str | None


class PaperTrader(Protocol):
    def decide(self, *, wake: LiveCausalWake,
               context: tuple[LiveCausalBar, ...]) -> PaperTraderDecision: ...


class PaperRiskPlanner(Protocol):
    def plan(self, *, wake: LiveCausalWake, context: tuple[LiveCausalBar, ...],
             decision: PaperTraderDecision) -> PaperOrderPlan | None: ...


class JournalManagedPaperBroker(Protocol):
    """Minimal broker contract required by the project-owned coordinator.

    Replacement is intentionally absent: the project coordinator owns safe
    cancel -> broker-truth -> child-submit semantics and never delegates atomic
    replacement to a third-party convenience API.
    """

    journal_managed_execution: bool

    @property
    def broker_id(self) -> str: ...

    @property
    def order_journal(self) -> PaperOrderJournal: ...

    @property
    def connection_state(self) -> BrokerConnectionState: ...

    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
    def submit_order(self, instruction: BrokerOrderInstruction) -> str: ...
    def cancel_order(self, order_id: str) -> None: ...
    def fetch_account_snapshot(self): ...
    def fetch_position_snapshot(self): ...
    def fetch_order_snapshot(self): ...


class PaperRuntimeCoordinator:
    """Project-owned startup, wake, execution and reconciliation composition."""

    def __init__(
        self, *, trader_identity: str, concrete_contract_id: str,
        context_builder: LiveCausalContextBuilder, wake_journal: PaperWakeJournal,
        order_journal: PaperOrderJournal, broker_mirror: PaperBrokerTruthMirror,
        supervisor: PaperRuntimeSupervisor, broker: JournalManagedPaperBroker,
        trader: PaperTrader, risk_planner: PaperRiskPlanner,
        max_broker_snapshot_age_seconds: int = 30,
    ) -> None:
        self.trader_identity = _text(trader_identity, "paper trader identity")
        self.concrete_contract_id = _text(concrete_contract_id, "paper concrete contract")
        if not isinstance(context_builder, LiveCausalContextBuilder):
            raise ValueError("paper runtime requires LiveCausalContextBuilder")
        if not isinstance(wake_journal, PaperWakeJournal):
            raise ValueError("paper runtime requires PaperWakeJournal")
        if not isinstance(order_journal, PaperOrderJournal):
            raise ValueError("paper runtime requires PaperOrderJournal")
        if not isinstance(broker_mirror, PaperBrokerTruthMirror):
            raise ValueError("paper runtime requires PaperBrokerTruthMirror")
        if not isinstance(supervisor, PaperRuntimeSupervisor):
            raise ValueError("paper runtime requires PaperRuntimeSupervisor")
        if getattr(broker, "journal_managed_execution", False) is not True:
            raise ValueError("paper runtime requires journal-managed broker execution")
        if getattr(broker, "order_journal", None) is not order_journal:
            raise ValueError("PAPER_RUNTIME_BROKER_JOURNAL_MISMATCH")
        broker_id = getattr(broker, "broker_id", None)
        if not isinstance(broker_id, str) or not broker_id.strip():
            raise ValueError("paper runtime broker requires stable broker_id")
        if broker_mirror.broker_id != broker_id:
            raise ValueError("PAPER_RUNTIME_BROKER_MIRROR_IDENTITY_MISMATCH")
        if type(max_broker_snapshot_age_seconds) is not int or max_broker_snapshot_age_seconds < 0:
            raise ValueError("paper broker snapshot age must be non-negative integer")
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

    def _before_external_action(self, at: datetime) -> None:
        _aware(at, "paper runtime clock")

    def assess(self, *, at: datetime,
               concrete_contract_id: str | None = None) -> PaperSupervisorAssessment:
        return self.supervisor.assess(
            assessed_at=_aware(at, "paper runtime assessment time"),
            market_bootstrapped=self.market_bootstrapped,
            market_sequence_ok=self.market_sequence_ok,
            trader_runtime_ready=self.trader_runtime_ready,
            max_broker_snapshot_age_seconds=self.max_broker_snapshot_age_seconds,
            concrete_contract_id=concrete_contract_id,
        )

    def connect(self, *, at: datetime) -> PaperSupervisorAssessment:
        """Authority -> connect -> complete broker truth/reconciliation."""
        self._before_external_action(at)
        before = self.assess(at=at)
        if not before.can_connect:
            raise PermissionError("PAPER_CONNECT_NOT_READY:" + ";".join(before.connect_blockers))
        self.broker.connect()
        self.broker_mirror.set_connection_state(self.broker.connection_state)
        blockers = self.refresh_broker_truth(at=at)
        if blockers:
            raise RuntimeError("PAPER_CONNECT_RECONCILIATION_BLOCKED:" + ";".join(blockers))
        return self.assess(at=at)

    def disconnect(self, *, at: datetime) -> None:
        self._before_external_action(at)
        self.broker.disconnect()
        self.broker_mirror.set_connection_state(self.broker.connection_state)

    def bootstrap_market(self, bars: Sequence[object], *, observed_at: datetime) -> None:
        """Bootstrap causal market state only after complete broker truth exists."""
        _aware(observed_at, "paper market bootstrap time")
        if self.broker.connection_state is not BrokerConnectionState.CONNECTED:
            raise RuntimeError("PAPER_BOOTSTRAP_REQUIRES_CONNECTED_BROKER")
        if self.broker_mirror.account is None or self.broker_mirror.snapshot_at is None:
            raise RuntimeError("PAPER_BOOTSTRAP_REQUIRES_BROKER_TRUTH")
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
        """Reconstruct account/position/order truth and reconcile durable attempts."""
        self._before_external_action(at)
        self.broker_mirror.set_connection_state(self.broker.connection_state)
        if self.broker.connection_state is not BrokerConnectionState.CONNECTED:
            self.broker_mirror.invalidate_truth()
            return ("BROKER_DISCONNECTED",)
        self.broker_mirror.invalidate_truth()
        try:
            account = self.broker.fetch_account_snapshot()
            positions = tuple(self.broker.fetch_position_snapshot())
            orders = tuple(self.broker.fetch_order_snapshot())
        except Exception:
            self.broker_mirror.set_connection_state(self.broker.connection_state)
            raise
        if self.broker.connection_state is not BrokerConnectionState.CONNECTED:
            self.broker_mirror.set_connection_state(self.broker.connection_state)
            return ("BROKER_DISCONNECTED",)
        self.broker_mirror.refresh(account=account, positions=positions, orders=orders, observed_at=at)
        return self.order_journal.reconcile_broker_orders(orders, observed_at=at)

    def process_closed_minutes(self, bars: Sequence[object], *, observed_at: datetime
                               ) -> tuple[PaperWakeResult, ...]:
        """Drive closed 1m updates through wake -> trader -> governed execution."""
        _aware(observed_at, "paper live observation time")
        if not self.market_bootstrapped or not self.market_sequence_ok:
            raise RuntimeError("PAPER_MARKET_NOT_READY")
        if not self.trader_runtime_ready:
            raise RuntimeError("PAPER_TRADER_NOT_READY")
        blockers = self.refresh_broker_truth(at=observed_at)
        if blockers:
            raise RuntimeError("PAPER_RECOVERY_BLOCKED:" + ";".join(blockers))
        results: list[PaperWakeResult] = []
        for wake in self.context_builder.observe(bars, observed_at=observed_at):
            context = self.context_builder.context_for_wake(wake)
            self.context_builder.admit_wake_to_journal(
                wake, journal=self.wake_journal, trader_identity=self.trader_identity,
                concrete_contract_id=self.concrete_contract_id)
            self.assess(at=observed_at).require_observation_ready()
            request_id = _hash({"schema_version": PAPER_RUNTIME_COORDINATOR_VERSION,
                                "kind": "TRADER_DISPATCH",
                                "trader_identity": self.trader_identity,
                                "wake_identity": wake.wake_identity})
            self.wake_journal.mark_dispatch_started(wake.wake_identity, request_id=request_id, at=observed_at)
            decision = self.trader.decide(wake=wake, context=context)
            if not isinstance(decision, PaperTraderDecision):
                raise TypeError("paper trader returned invalid decision")
            self.wake_journal.mark_decision_committed(
                wake.wake_identity, decision_identity=decision.decision_identity, at=observed_at)
            plan = self.risk_planner.plan(wake=wake, context=context, decision=decision)
            if plan is None:
                results.append(PaperWakeResult(wake.wake_identity, decision.decision_identity, None, None))
                continue
            if not isinstance(plan, PaperOrderPlan):
                raise TypeError("paper risk planner returned invalid order plan")
            instruction = plan.instruction
            if instruction.concrete_contract_id != self.concrete_contract_id:
                raise ValueError("PAPER_ORDER_CONTRACT_MISMATCH")
            self.assess(at=observed_at, concrete_contract_id=self.concrete_contract_id).require_order_ready()
            self.order_journal.prepare(
                client_request_id=instruction.client_request_id,
                trader_identity=self.trader_identity, wake_identity=wake.wake_identity,
                decision_identity=decision.decision_identity, intent_identity=plan.intent_identity,
                risk_identity=plan.risk_identity, concrete_contract_id=self.concrete_contract_id,
                prepared_at=observed_at)
            self._before_external_action(observed_at)
            broker_order_id = self.broker.submit_order(instruction)
            if self.order_journal.get(instruction.client_request_id).status == PREPARED:
                raise RuntimeError("BROKER_FAILED_TO_JOURNAL_SUBMIT_ATTEMPT")
            blockers = self.refresh_broker_truth(at=observed_at)
            if blockers:
                raise RuntimeError("PAPER_RECOVERY_BLOCKED:" + ";".join(blockers))
            results.append(PaperWakeResult(
                wake.wake_identity, decision.decision_identity,
                instruction.client_request_id, broker_order_id))
        return tuple(results)

    def cancel_order(self, client_request_id: str, *, at: datetime) -> tuple[str, ...]:
        """Risk-reducing cancel through project-owned durable identity."""
        attempt = self.order_journal.get(_text(client_request_id, "paper cancel client request id"))
        if attempt.status != BROKER_ORDER_ID_KNOWN or not attempt.broker_order_id:
            raise RuntimeError("PAPER_CANCEL_REQUIRES_KNOWN_ORDER")
        self._before_external_action(at)
        self.broker.cancel_order(attempt.broker_order_id)
        return self.refresh_broker_truth(at=at)

    def cancel_then_replace(
        self, *, original_client_request_id: str, child_plan: PaperOrderPlan,
        wake_identity: str, decision_identity: str, replacement_generation: int,
        at: datetime,
    ) -> str:
        """Safe replacement: durable child -> cancel -> exact truth -> one submit."""
        original = self.order_journal.get(_text(original_client_request_id, "replace original request id"))
        _text(wake_identity, "replace wake identity")
        _text(decision_identity, "replace decision identity")
        if not isinstance(child_plan, PaperOrderPlan):
            raise ValueError("replace requires PaperOrderPlan")
        if type(replacement_generation) is not int or replacement_generation <= 0:
            raise ValueError("replacement generation must be positive integer")
        if original.status != BROKER_ORDER_ID_KNOWN or not original.broker_order_id:
            raise RuntimeError("PAPER_REPLACE_REQUIRES_KNOWN_ORIGINAL")
        instruction = child_plan.instruction
        if instruction.concrete_contract_id != self.concrete_contract_id:
            raise ValueError("PAPER_REPLACE_CONTRACT_MISMATCH")
        self.order_journal.prepare(
            client_request_id=instruction.client_request_id, trader_identity=self.trader_identity,
            wake_identity=wake_identity, decision_identity=decision_identity,
            intent_identity=child_plan.intent_identity, risk_identity=child_plan.risk_identity,
            concrete_contract_id=self.concrete_contract_id, prepared_at=at)
        cancel = self.order_journal.prepare_cancel_for_broker_order(original.broker_order_id, at=at)
        replace_id = _hash({"schema_version": PAPER_RUNTIME_COORDINATOR_VERSION,
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
        self._before_external_action(at)
        self.broker.cancel_order(original.broker_order_id)
        blockers = self.refresh_broker_truth(at=at)
        if blockers:
            raise RuntimeError("PAPER_REPLACEMENT_RECOVERY_BLOCKED:" + ";".join(blockers))
        resolved_cancel = self.order_journal.get_cancel(cancel.cancel_operation_id)
        if resolved_cancel.status != "CANCEL_RESOLVED" or resolved_cancel.final_order_status != "CANCELLED":
            raise RuntimeError("PAPER_REPLACE_CANCEL_UNRESOLVED")
        self.order_journal.authorize_replacement_child(replace_id, at=at)
        self.assess(at=at, concrete_contract_id=self.concrete_contract_id).require_order_ready()
        self._before_external_action(at)
        broker_order_id = self.broker.submit_order(instruction)
        if self.order_journal.get(instruction.client_request_id).status == PREPARED:
            raise RuntimeError("BROKER_FAILED_TO_JOURNAL_REPLACEMENT_SUBMIT")
        blockers = self.refresh_broker_truth(at=at)
        if blockers:
            raise RuntimeError("PAPER_REPLACEMENT_RECOVERY_BLOCKED:" + ";".join(blockers))
        return broker_order_id


__all__ = [
    "JournalManagedPaperBroker",
    "PAPER_RUNTIME_COORDINATOR_VERSION",
    "PaperOrderPlan",
    "PaperRiskPlanner",
    "PaperRuntimeCoordinator",
    "PaperTrader",
    "PaperTraderDecision",
    "PaperWakeResult",
]

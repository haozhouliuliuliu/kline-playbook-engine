"""Broker-neutral realtime PAPER runtime coordinator.

The coordinator composes project-owned causal market context, durable wake/order
journals, readiness gates, broker truth, trader cognition and deterministic risk.
It performs no provider, credential or network work by import/construction.

External effects occur only through an injected broker when an explicit runtime
method is called and the existing PAPER authority/profile gates allow it.
Result-dependent sizing, price, close-offset, permanent risk and product policy
are deliberately injected rather than defined here.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
import json
from typing import Protocol, Sequence

from src.broker_adapter import (
    BrokerOrderInstruction,
    OrderRole,
    OrderType,
    StopTriggerCondition,
)
from src.contract_semantics import CloseOffset, OrderAction, PositionDirection
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_execution_authority import PaperAuthoritySource
from src.paper_execution_chain import PaperDeterministicExecutionChain
from src.jianghe_response_normalizer import NormalizedJiangheDecision
from src.paper_live_causal_context import LiveCausalBar, LiveCausalContextBuilder, LiveCausalWake
from src.paper_order_journal import (
    BROKER_ORDER_ID_KNOWN,
    PREPARED,
    TERMINAL,
    PaperOrderJournal,
)
from src.paper_supervisor import PaperRuntimeSupervisor, PaperSupervisorAssessment
from src.paper_wake_journal import PaperWakeJournal
from src.runtime_events import BrokerConnectionState

PAPER_RUNTIME_COORDINATOR_VERSION = "KPE_PAPER_RUNTIME_COORDINATOR_V0_1"


def _hash(payload: object) -> str:
    return sha256(json.dumps(payload, ensure_ascii=False, separators=(",", ":"),
                             sort_keys=True).encode("utf-8")).hexdigest()


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
    normalized_decision: NormalizedJiangheDecision | None = None

    def __post_init__(self) -> None:
        _text(self.decision_identity, "paper decision identity")
        if not isinstance(self.summary, str):
            raise ValueError("paper decision summary must be text")
        if self.normalized_decision is not None:
            if not isinstance(self.normalized_decision, NormalizedJiangheDecision):
                raise TypeError("paper trader decision requires normalized Jianghe decision")
            if self.normalized_decision.identity != self.decision_identity:
                raise ValueError("PAPER_NORMALIZED_DECISION_IDENTITY_MISMATCH")


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
    """Minimal broker surface. Atomic replacement is intentionally absent."""

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
        trader: PaperTrader, risk_planner: PaperRiskPlanner | None = None,
        execution_chain: PaperDeterministicExecutionChain | None = None,
        authority_source: PaperAuthoritySource | None = None,
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
        if supervisor.order_journal is not order_journal:
            raise ValueError("PAPER_RUNTIME_SUPERVISOR_ORDER_JOURNAL_MISMATCH")
        if supervisor.wake_journal is not wake_journal:
            raise ValueError("PAPER_RUNTIME_SUPERVISOR_WAKE_JOURNAL_MISMATCH")
        if supervisor.broker_mirror is not broker_mirror:
            raise ValueError("PAPER_RUNTIME_SUPERVISOR_BROKER_MIRROR_MISMATCH")
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
        if risk_planner is None and execution_chain is None:
            raise ValueError("paper runtime requires one deterministic planning path")
        if risk_planner is not None and execution_chain is not None:
            raise ValueError("PAPER_RUNTIME_PARALLEL_EXECUTION_PATH_FORBIDDEN")
        self.risk_planner = risk_planner
        self.execution_chain = execution_chain
        self.authority_source = authority_source or supervisor.authority_source
        if self.authority_source is not supervisor.authority_source:
            raise ValueError("PAPER_RUNTIME_AUTHORITY_SOURCE_MISMATCH")
        self.max_broker_snapshot_age_seconds = max_broker_snapshot_age_seconds
        self.market_bootstrapped = context_builder.bootstrap_done
        self.market_sequence_ok = context_builder.bootstrap_done
        self.trader_runtime_ready = False

    def _before_external_action(self, at: datetime, *, action: str) -> None:
        at = _aware(at, "paper runtime clock")
        authority = self.authority_source.current()
        legacy = self.authority_source.source_identity == "STATIC_LEGACY_AUTHORITY_SOURCE"
        broker_account_identity = getattr(self.broker, "account_identity", None)
        identities = {
            "at": None if legacy else at,
            "broker_identity": None if legacy else self.broker.broker_id,
            "account_identity": None if legacy else broker_account_identity,
        }
        if action == "CONNECT":
            authority.require_connect(**identities)
        elif action == "SUBMIT":
            authority.require_order_submit(self.concrete_contract_id, **identities)
        elif action == "CANCEL":
            authority.require_order_cancel(**identities)
        elif action == "REPLACE":
            authority.require_order_replace(**identities)
        else:
            raise ValueError("unknown PAPER external action")

    def _before_broker_read(self, at: datetime) -> None:
        _aware(at, "paper broker read time")

    def _require_recovery_submission_ready(
        self, *, at: datetime, allowed_recovery_blocker: str
    ) -> None:
        assessment = self.assess(
            at=at, concrete_contract_id=self.concrete_contract_id
        )
        allowed = {
            "PAPER_ORDER_RECOVERY:" + allowed_recovery_blocker,
            "LIVE_MARKET_NOT_BOOTSTRAPPED",
            "LIVE_MARKET_SEQUENCE_NOT_CLEAN",
            "TRADER_RUNTIME_NOT_READY",
        }
        blockers = tuple(item for item in assessment.order_blockers if item not in allowed)
        if blockers:
            raise PermissionError("PAPER_ORDER_NOT_READY:" + ";".join(blockers))

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
        self._before_external_action(at, action="CONNECT")
        before = self.assess(at=at)
        if not before.can_connect:
            raise PermissionError("PAPER_CONNECT_NOT_READY:" + ";".join(before.connect_blockers))
        self.broker.connect()
        try:
            self.broker_mirror.set_connection_state(self.broker.connection_state)
            blockers = self.refresh_broker_truth(at=at)
            if (
                self.order_journal.unresolved_replace_operations()
                or self.order_journal.triggered_conditionals()
                or self.order_journal.pending_execution_batches()
            ):
                blockers = self.resume_order_recovery(at=at)
            if blockers:
                raise RuntimeError("PAPER_CONNECT_RECONCILIATION_BLOCKED:" + ";".join(blockers))
        except Exception:
            try:
                self.broker.disconnect()
            finally:
                self.broker_mirror.set_connection_state(self.broker.connection_state)
            raise
        return self.assess(at=at)

    def disconnect(self, *, at: datetime) -> None:
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
        _aware(at, "paper broker truth refresh time")
        self._before_broker_read(at)
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
        self.broker_mirror.refresh(account=account, positions=positions,
                                   orders=orders, observed_at=at)
        blockers = self.order_journal.reconcile_broker_orders(orders, observed_at=at)
        if self.execution_chain is not None:
            self.execution_chain.reconcile_broker_truth(self.broker_mirror, at=at)
        return blockers

    def pump_broker_updates(self, *, at: datetime) -> tuple[object, ...]:
        """Advance the injected broker driver once and reconcile exact truth."""
        _aware(at, "paper broker pump time")
        pump = getattr(self.broker, "pump_events", None)
        events = tuple(pump() if callable(pump) else ())
        if self.execution_chain is not None and events:
            self.execution_chain.apply_broker_events(events, at=at)
        self.refresh_broker_truth(at=at)
        return events

    def _prepare_if_missing(
        self,
        *,
        instruction: BrokerOrderInstruction,
        trader_identity: str,
        wake_identity: str,
        decision_identity: str,
        intent_identity: str,
        risk_identity: str,
        at: datetime,
    ) -> None:
        try:
            existing = self.order_journal.get(instruction.client_request_id)
        except KeyError:
            self.order_journal.prepare(
                client_request_id=instruction.client_request_id,
                trader_identity=trader_identity,
                wake_identity=wake_identity,
                decision_identity=decision_identity,
                intent_identity=intent_identity,
                risk_identity=risk_identity,
                concrete_contract_id=instruction.concrete_contract_id,
                instruction=instruction,
                prepared_at=at,
            )
            return
        if (
            existing.status != PREPARED
            and existing.status not in {BROKER_ORDER_ID_KNOWN, TERMINAL}
        ):
            raise RuntimeError("PAPER_ORDER_ATTEMPT_NOT_SAFE_TO_RESUME")
        if existing.expected_source_directive_identity != instruction.source_directive_identity:
            raise RuntimeError("PAPER_ORDER_RESUME_ENVELOPE_MISMATCH")

    @staticmethod
    def _triggered_child_instruction(
        instruction: BrokerOrderInstruction,
    ) -> BrokerOrderInstruction:
        if instruction.order_type is not OrderType.STOP_MARKET:
            raise ValueError("triggered child requires STOP_MARKET directive")
        child_request_id = _hash({
            "schema_version": PAPER_RUNTIME_COORDINATOR_VERSION,
            "kind": "PROJECT_TRIGGERED_STOP_CHILD",
            "directive_client_request_id": instruction.client_request_id,
            "directive_identity": instruction.identity_id,
        })
        return BrokerOrderInstruction(
            client_request_id=child_request_id,
            client_order_id=child_request_id,
            concrete_contract_id=instruction.concrete_contract_id,
            direction=instruction.direction,
            action=instruction.action,
            order_type=instruction.triggered_order_type,
            quantity=instruction.quantity,
            close_offset=instruction.close_offset,
            limit_price=instruction.triggered_limit_price,
            order_role=instruction.order_role,
            strategy_identity_id=instruction.strategy_identity_id,
            available_at=instruction.available_at,
            parent_order_id=instruction.parent_order_id,
            oco_group_id=instruction.oco_group_id,
            replace_generation=instruction.replace_generation,
            source_directive_identity=instruction.client_request_id,
        )

    def _resume_triggered_conditionals(self, *, at: datetime) -> list[str]:
        blockers: list[str] = []
        for conditional in self.order_journal.triggered_conditionals():
            directive = self.order_journal.get(conditional.directive_client_request_id)
            self._prepare_if_missing(
                instruction=conditional.child_instruction,
                trader_identity=directive.trader_identity,
                wake_identity=directive.wake_identity,
                decision_identity=directive.decision_identity,
                intent_identity=_hash({
                    "directive_intent_identity": directive.intent_identity,
                    "conditional_child": conditional.child_client_request_id,
                }),
                risk_identity=directive.risk_identity,
                at=at,
            )
            child = self.order_journal.get(conditional.child_client_request_id)
            if child.status == PREPARED:
                self._require_recovery_submission_ready(
                    at=at,
                    allowed_recovery_blocker="CONDITIONAL_TRIGGER_PENDING_SUBMIT",
                )
                self._before_external_action(at, action="SUBMIT")
                self.broker.submit_order(conditional.child_instruction)
                child = self.order_journal.get(conditional.child_client_request_id)
            if child.status not in {BROKER_ORDER_ID_KNOWN, TERMINAL}:
                blockers.append("CONDITIONAL_CHILD_SUBMISSION_UNRESOLVED")
                continue
            self.order_journal.resolve_conditional(
                conditional.directive_client_request_id, at=at
            )
        return blockers

    def process_conditional_orders(
        self, bar: LiveCausalBar, *, observed_at: datetime
    ) -> tuple[str, ...]:
        """Evaluate armed STOP directives from one governed current closed bar."""
        observed_at = _aware(observed_at, "conditional observation time")
        armed = self.order_journal.armed_conditionals()
        if not armed:
            return ()
        if not isinstance(bar, LiveCausalBar) or bar.timeframe != "1m":
            raise ValueError("conditional evaluation requires governed closed 1m bar")
        if bar.concrete_instrument != self.concrete_contract_id.split(".", 1)[-1]:
            raise ValueError("PAPER_CONDITIONAL_CONTRACT_MISMATCH")
        if bar.available_at > observed_at:
            raise RuntimeError("PAPER_CONDITIONAL_FUTURE_MARKET_DATA")
        max_age = (
            self.execution_chain.max_market_age_seconds
            if self.execution_chain is not None
            else 0
        )
        age = (observed_at - bar.available_at).total_seconds()
        if age < 0 or max_age <= 0 or age > max_age:
            raise RuntimeError("PAPER_CONDITIONAL_STALE_MARKET_DATA")
        triggered: list[str] = []
        for conditional in armed:
            directive = self.order_journal.get(conditional.directive_client_request_id)
            condition = StopTriggerCondition(directive.expected_trigger_condition)
            trigger_price = Decimal(directive.expected_trigger_price or "0")
            self.order_journal.record_conditional_evaluation(
                conditional.directive_client_request_id,
                bar_identity=bar.identity,
                bar_end=bar.end,
                at=observed_at,
            )
            crossed = (
                bar.high >= trigger_price
                if condition is StopTriggerCondition.AT_OR_ABOVE
                else bar.low <= trigger_price
            )
            if crossed:
                self.order_journal.mark_conditional_triggered(
                    conditional.directive_client_request_id, at=observed_at
                )
                triggered.append(conditional.directive_client_request_id)
        if triggered:
            blockers = self._resume_triggered_conditionals(at=observed_at)
            if blockers:
                raise RuntimeError("PAPER_CONDITIONAL_RECOVERY_BLOCKED:" + ";".join(blockers))
            blockers = self.refresh_broker_truth(at=observed_at)
            if blockers:
                raise RuntimeError("PAPER_CONDITIONAL_RECONCILIATION_BLOCKED:" + ";".join(blockers))
        return tuple(triggered)

    def _resume_execution_batches(self, *, at: datetime) -> list[str]:
        blockers: list[str] = []
        for batch in self.order_journal.pending_execution_batches():
            for child in batch.children:
                self._prepare_if_missing(
                    instruction=child.instruction,
                    trader_identity=batch.trader_identity,
                    wake_identity=batch.wake_identity,
                    decision_identity=batch.decision_identity,
                    intent_identity=child.intent_identity,
                    risk_identity=child.risk_identity,
                    at=at,
                )
                attempt = self.order_journal.get(child.instruction.client_request_id)
                if attempt.status == PREPARED:
                    self._require_recovery_submission_ready(
                        at=at,
                        allowed_recovery_blocker="EXECUTION_BATCH_PENDING_SUBMIT",
                    )
                    self._before_external_action(at, action="SUBMIT")
                    self.broker.submit_order(child.instruction)
                    attempt = self.order_journal.get(child.instruction.client_request_id)
                if attempt.status not in {BROKER_ORDER_ID_KNOWN, TERMINAL}:
                    blockers.append("EXECUTION_BATCH_CHILD_SUBMISSION_UNRESOLVED")
                    break
            if blockers:
                break
            refreshed = self.refresh_broker_truth(at=at)
            if refreshed:
                blockers.extend(refreshed)
                break
            self.order_journal.resolve_execution_batch(batch.batch_identity, at=at)
        return blockers

    def resume_order_recovery(self, *, at: datetime) -> tuple[str, ...]:
        blockers = list(self.resume_replacement_recovery(at=at))
        if blockers:
            return tuple(sorted(set(blockers)))
        blockers.extend(self._resume_triggered_conditionals(at=at))
        if blockers:
            return tuple(sorted(set(blockers)))
        blockers.extend(self._resume_execution_batches(at=at))
        return tuple(sorted(set(blockers)))

    def process_closed_minutes(self, bars: Sequence[object], *, observed_at: datetime
                               ) -> tuple[PaperWakeResult, ...]:
        """Drive closed 1m updates through wake -> trader -> governed execution.

        Order-recovery blockers do not stop market observation/cognition. They
        remain durable and are enforced by ``require_order_ready`` immediately
        before any new-risk submission. Broker/mirror/data failures still block
        observation through the supervisor.
        """
        _aware(observed_at, "paper live observation time")
        if not self.market_bootstrapped or not self.market_sequence_ok:
            raise RuntimeError("PAPER_MARKET_NOT_READY")
        if not self.trader_runtime_ready:
            raise RuntimeError("PAPER_TRADER_NOT_READY")
        self.refresh_broker_truth(at=observed_at)
        self.assess(at=observed_at).require_observation_ready()
        results: list[PaperWakeResult] = []
        wakes = self.context_builder.observe(bars, observed_at=observed_at)
        for minute in self.context_builder.newly_admitted_one_minute_bars:
            self.process_conditional_orders(minute, observed_at=observed_at)
        for wake in wakes:
            context = self.context_builder.context_for_wake(wake)
            self.context_builder.admit_wake_to_journal(
                wake, journal=self.wake_journal, trader_identity=self.trader_identity,
                concrete_contract_id=self.concrete_contract_id)
            self.assess(at=observed_at).require_observation_ready()
            request_id = _hash({
                "schema_version": PAPER_RUNTIME_COORDINATOR_VERSION,
                "kind": "TRADER_DISPATCH",
                "trader_identity": self.trader_identity,
                "wake_identity": wake.wake_identity,
            })
            self.wake_journal.mark_dispatch_started(
                wake.wake_identity, request_id=request_id, at=observed_at)
            if self.execution_chain is None:
                decision = self.trader.decide(wake=wake, context=context)
            else:
                decision = self.trader.decide(
                    wake=wake,
                    context=context,
                    positions=self.execution_chain.model_visible_positions(),
                    account=self.execution_chain.project_state.account,
                )
            if not isinstance(decision, PaperTraderDecision):
                raise TypeError("paper trader returned invalid decision")
            self.wake_journal.mark_decision_committed(
                wake.wake_identity, decision_identity=decision.decision_identity, at=observed_at)
            if self.execution_chain is None:
                assert self.risk_planner is not None
                legacy_plan = self.risk_planner.plan(wake=wake, context=context, decision=decision)
                plans = () if legacy_plan is None else (legacy_plan,)
            else:
                if decision.normalized_decision is None:
                    raise RuntimeError("PAPER_NORMALIZED_JIANGHE_DECISION_REQUIRED")
                plans = tuple(self.execution_chain.plan(
                    wake=wake,
                    context=context,
                    decision=decision.normalized_decision,
                    connection_state=self.broker.connection_state,
                ))
            if not plans:
                results.append(PaperWakeResult(
                    wake.wake_identity, decision.decision_identity, None, None))
                continue
            if any(
                plan.instruction.concrete_contract_id != self.concrete_contract_id
                for plan in plans
            ):
                raise ValueError("PAPER_ORDER_CONTRACT_MISMATCH")
            self.assess(at=observed_at,
                        concrete_contract_id=self.concrete_contract_id).require_order_ready()

            if all(plan.instruction.order_type is OrderType.STOP_MARKET for plan in plans):
                for plan in plans:
                    instruction = plan.instruction
                    self.order_journal.prepare(
                        client_request_id=instruction.client_request_id,
                        trader_identity=self.trader_identity,
                        wake_identity=wake.wake_identity,
                        decision_identity=decision.decision_identity,
                        intent_identity=plan.intent_identity,
                        risk_identity=plan.risk_identity,
                        concrete_contract_id=self.concrete_contract_id,
                        instruction=instruction,
                        prepared_at=observed_at,
                    )
                    self.order_journal.arm_conditional(
                        directive_client_request_id=instruction.client_request_id,
                        child_instruction=self._triggered_child_instruction(instruction),
                        at=observed_at,
                    )
                    results.append(PaperWakeResult(
                        wake.wake_identity,
                        decision.decision_identity,
                        instruction.client_request_id,
                        None,
                    ))
                continue
            if any(plan.instruction.order_type is OrderType.STOP_MARKET for plan in plans):
                raise RuntimeError("PAPER_MIXED_CONDITIONAL_AND_IMMEDIATE_BATCH_FORBIDDEN")

            if len(plans) > 1 or plans[0].instruction.close_offset is not None:
                batch_ids = {getattr(plan, "logical_execution_identity", None) for plan in plans}
                logical_quantities = {getattr(plan, "logical_quantity", None) for plan in plans}
                logical_intents = {getattr(plan, "logical_intent_identity", None) for plan in plans}
                if (
                    None in batch_ids
                    or None in logical_quantities
                    or None in logical_intents
                    or len(batch_ids) != 1
                    or len(logical_quantities) != 1
                    or len(logical_intents) != 1
                ):
                    raise RuntimeError("PAPER_EXECUTION_BATCH_IDENTITY_INCOMPLETE")
                batch_identity = next(iter(batch_ids))
                logical_quantity = next(iter(logical_quantities))
                logical_intent_identity = next(iter(logical_intents))
                self.order_journal.authorize_execution_batch(
                    batch_identity=batch_identity,
                    trader_identity=self.trader_identity,
                    wake_identity=wake.wake_identity,
                    decision_identity=decision.decision_identity,
                    logical_intent_identity=logical_intent_identity,
                    risk_identity=plans[0].risk_identity,
                    concrete_contract_id=self.concrete_contract_id,
                    logical_quantity=logical_quantity,
                    children=tuple(
                        (plan.intent_identity, plan.risk_identity, plan.instruction)
                        for plan in plans
                    ),
                    at=observed_at,
                )
                blockers = self._resume_execution_batches(at=observed_at)
                if blockers:
                    raise RuntimeError(
                        "PAPER_EXECUTION_BATCH_RECOVERY_BLOCKED:" + ";".join(blockers)
                    )
                for plan in plans:
                    attempt = self.order_journal.get(plan.instruction.client_request_id)
                    results.append(PaperWakeResult(
                        wake.wake_identity,
                        decision.decision_identity,
                        plan.instruction.client_request_id,
                        attempt.broker_order_id,
                    ))
                continue

            plan = plans[0]
            instruction = plan.instruction
            self.order_journal.prepare(
                client_request_id=instruction.client_request_id,
                trader_identity=self.trader_identity,
                wake_identity=wake.wake_identity,
                decision_identity=decision.decision_identity,
                intent_identity=plan.intent_identity,
                risk_identity=plan.risk_identity,
                concrete_contract_id=self.concrete_contract_id,
                instruction=instruction,
                prepared_at=observed_at,
            )
            self._before_external_action(observed_at, action="SUBMIT")
            self.broker.submit_order(instruction)
            attempt = self.order_journal.get(instruction.client_request_id)
            if attempt.status == PREPARED:
                raise RuntimeError("BROKER_FAILED_TO_JOURNAL_SUBMIT_ATTEMPT")
            self.refresh_broker_truth(at=observed_at)
            attempt = self.order_journal.get(instruction.client_request_id)
            confirmed_id = attempt.broker_order_id if attempt.status == BROKER_ORDER_ID_KNOWN else None
            results.append(PaperWakeResult(
                wake.wake_identity, decision.decision_identity,
                instruction.client_request_id, confirmed_id))
        return tuple(results)

    def cancel_order(self, client_request_id: str, *, at: datetime) -> tuple[str, ...]:
        """Risk-reducing cancel through project-owned durable identity."""
        attempt = self.order_journal.get(
            _text(client_request_id, "paper cancel client request id"))
        if attempt.status != BROKER_ORDER_ID_KNOWN or not attempt.broker_order_id:
            raise RuntimeError("PAPER_CANCEL_REQUIRES_KNOWN_ORDER")
        self._before_external_action(at, action="CANCEL")
        self.broker.cancel_order(attempt.broker_order_id)
        return self.refresh_broker_truth(at=at)

    def cancel_then_replace(
        self, *, original_client_request_id: str, child_plan: PaperOrderPlan,
        wake_identity: str, decision_identity: str, replacement_generation: int,
        at: datetime,
    ) -> str:
        """Safe replacement: clean state -> cancel -> exact truth -> one child submit."""
        original_client_request_id = _text(
            original_client_request_id, "replace original request id")
        _text(wake_identity, "replace wake identity")
        _text(decision_identity, "replace decision identity")
        if not isinstance(child_plan, PaperOrderPlan):
            raise ValueError("replace requires PaperOrderPlan")
        if type(replacement_generation) is not int or replacement_generation <= 0:
            raise ValueError("replacement generation must be positive integer")
        instruction = child_plan.instruction
        if instruction.concrete_contract_id != self.concrete_contract_id:
            raise ValueError("PAPER_REPLACE_CONTRACT_MISMATCH")

        self._before_external_action(at, action="REPLACE")
        # A replacement may not begin while some older execution ambiguity is
        # already unresolved. Refresh first, then re-read the original attempt.
        pre_blockers = self.refresh_broker_truth(at=at)
        if pre_blockers:
            raise RuntimeError("PAPER_REPLACEMENT_RECOVERY_BLOCKED:" +
                               ";".join(pre_blockers))
        self.assess(at=at,
                    concrete_contract_id=self.concrete_contract_id).require_order_ready()
        original = self.order_journal.get(original_client_request_id)
        if original.status != BROKER_ORDER_ID_KNOWN or not original.broker_order_id:
            raise RuntimeError("PAPER_REPLACE_REQUIRES_KNOWN_ORIGINAL")
        matching = tuple(
            item for item in self.broker_mirror.orders
            if item.order_id == original.broker_order_id
        )
        if len(matching) != 1:
            raise RuntimeError("PAPER_REPLACE_REQUIRES_EXACT_BROKER_ORDER")
        broker_order = matching[0]
        remaining = broker_order.requested_quantity - broker_order.filled_quantity
        if remaining <= 0 or instruction.quantity > remaining:
            raise RuntimeError("PAPER_REPLACEMENT_QUANTITY_EXCEEDS_BROKER_REMAINING")

        self.order_journal.prepare(
            client_request_id=instruction.client_request_id,
            trader_identity=self.trader_identity,
            wake_identity=wake_identity,
            decision_identity=decision_identity,
            intent_identity=child_plan.intent_identity,
            risk_identity=child_plan.risk_identity,
            concrete_contract_id=self.concrete_contract_id,
            instruction=instruction,
            prepared_at=at,
        )
        cancel = self.order_journal.prepare_cancel_for_broker_order(
            original.broker_order_id, at=at)
        replace_id = _hash({
            "schema_version": PAPER_RUNTIME_COORDINATOR_VERSION,
            "kind": "CANCEL_THEN_REPLACE",
            "original_client_request_id": original_client_request_id,
            "child_client_request_id": instruction.client_request_id,
            "replacement_generation": replacement_generation,
            "replacement_intent_identity": child_plan.intent_identity,
        })
        self.order_journal.prepare_replace(
            replace_operation_id=replace_id,
            original_client_request_id=original_client_request_id,
            replacement_generation=replacement_generation,
            replacement_intent_identity=child_plan.intent_identity,
            cancel_operation_id=cancel.cancel_operation_id,
            child_client_request_id=instruction.client_request_id,
            prepared_at=at,
        )
        self._before_external_action(at, action="CANCEL")
        self.broker.cancel_order(original.broker_order_id)

        # WAITING_FOR_CANCEL is intentionally a temporary recovery blocker. The
        # exact cancel record, not the generic blocker list, decides whether the
        # replacement child may proceed.
        self.refresh_broker_truth(at=at)
        resolved_cancel = self.order_journal.get_cancel(cancel.cancel_operation_id)
        if (resolved_cancel.status != "CANCEL_RESOLVED" or
                resolved_cancel.final_order_status != "CANCELLED"):
            raise RuntimeError("PAPER_REPLACE_CANCEL_UNRESOLVED")

        cancelled_orders = tuple(
            item for item in self.broker_mirror.orders
            if item.order_id == original.broker_order_id
        )
        if len(cancelled_orders) != 1:
            raise RuntimeError("PAPER_REPLACE_CANCELLED_ORDER_TRUTH_MISSING")
        remaining_after_cancel = (
            cancelled_orders[0].requested_quantity
            - cancelled_orders[0].filled_quantity
        )
        if (
            remaining_after_cancel <= 0
            or instruction.quantity > remaining_after_cancel
        ):
            raise RuntimeError(
                "PAPER_REPLACEMENT_QUANTITY_EXCEEDS_BROKER_REMAINING_AFTER_CANCEL"
            )

        self.order_journal.authorize_replacement_child(replace_id, at=at)
        mirror_assessment = self.broker_mirror.assess(
            expected_client_request_ids=self.order_journal.expected_client_request_ids(),
            assessed_at=at,
            max_snapshot_age_seconds=self.max_broker_snapshot_age_seconds,
        )
        if not mirror_assessment.ok:
            raise RuntimeError(
                "PAPER_REPLACEMENT_BROKER_TRUTH_BLOCKED:"
                + ";".join(mirror_assessment.reasons)
            )
        self._before_external_action(at, action="REPLACE")
        self._before_external_action(at, action="SUBMIT")
        self.broker.submit_order(instruction)
        child = self.order_journal.get(instruction.client_request_id)
        if child.status == PREPARED:
            raise RuntimeError("BROKER_FAILED_TO_JOURNAL_REPLACEMENT_SUBMIT")
        blockers = self.refresh_broker_truth(at=at)
        if blockers:
            raise RuntimeError("PAPER_REPLACEMENT_RECOVERY_BLOCKED:" +
                               ";".join(blockers))
        child = self.order_journal.get(instruction.client_request_id)
        if child.status != BROKER_ORDER_ID_KNOWN or not child.broker_order_id:
            raise RuntimeError("PAPER_REPLACEMENT_CHILD_NOT_CONFIRMED")
        return child.broker_order_id

    def resume_replacement_recovery(self, *, at: datetime) -> tuple[str, ...]:
        """Resume only broker-proven, never-attempted replacement children.

        An ambiguous cancel or child submission is only reported; it is never
        retried.  A durably AUTHORIZED child is safe to submit because the
        journal proves ATTEMPT_STARTED was never committed.
        """
        at = _aware(at, "replacement recovery time")
        blockers = [
            blocker
            for blocker in self.refresh_broker_truth(at=at)
            if blocker not in {
                "UNKNOWN_REPLACE",
                "CONDITIONAL_TRIGGER_PENDING_SUBMIT",
                "EXECUTION_BATCH_PENDING_SUBMIT",
            }
        ]
        for operation in self.order_journal.unresolved_replace_operations():
            cancel = self.order_journal.get_cancel(operation.cancel_operation_id)
            if operation.status == "REPLACE_WAITING_FOR_CANCEL":
                if cancel.status == "CANCEL_RESOLVED" and cancel.final_order_status == "CANCELLED":
                    self._before_external_action(at, action="REPLACE")
                    operation = self.order_journal.authorize_replacement_child(
                        operation.replace_operation_id, at=at
                    )
                else:
                    blockers.append("REPLACEMENT_CANCEL_NOT_BROKER_RESOLVED")
                    continue
            if operation.status != "REPLACE_CHILD_SUBMIT_AUTHORIZED":
                blockers.append("AMBIGUOUS_REPLACEMENT_MUTATION")
                continue
            child = self.order_journal.get(operation.child_client_request_id)
            if child.status != PREPARED:
                blockers.append("REPLACEMENT_CHILD_NOT_PROVABLY_NOT_SENT")
                continue
            original = self.order_journal.get(operation.original_client_request_id)
            snapshots = tuple(
                item for item in self.broker_mirror.orders
                if item.order_id == original.broker_order_id
            )
            if len(snapshots) != 1:
                blockers.append("REPLACEMENT_ORIGINAL_BROKER_TRUTH_MISSING")
                continue
            remaining = snapshots[0].requested_quantity - snapshots[0].filled_quantity
            quantity = Decimal(child.expected_quantity or "0")
            if remaining <= 0 or quantity <= 0 or quantity > remaining:
                blockers.append("REPLACEMENT_QUANTITY_EXCEEDS_BROKER_REMAINING")
                continue
            instruction = BrokerOrderInstruction(
                client_request_id=child.client_request_id,
                client_order_id=child.expected_client_order_id,
                concrete_contract_id=child.concrete_contract_id,
                direction=PositionDirection(child.expected_direction),
                action=OrderAction(child.expected_action),
                order_type=OrderType(child.expected_order_type),
                quantity=quantity,
                close_offset=(
                    None if child.expected_close_offset is None
                    else CloseOffset(child.expected_close_offset)
                ),
                limit_price=(
                    None if child.expected_limit_price is None
                    else Decimal(child.expected_limit_price)
                ),
                trigger_price=(
                    None if child.expected_trigger_price is None
                    else Decimal(child.expected_trigger_price)
                ),
                trigger_condition=(
                    None if child.expected_trigger_condition is None
                    else StopTriggerCondition(child.expected_trigger_condition)
                ),
                triggered_order_type=(
                    None if child.expected_triggered_order_type is None
                    else OrderType(child.expected_triggered_order_type)
                ),
                triggered_limit_price=(
                    None if child.expected_triggered_limit_price is None
                    else Decimal(child.expected_triggered_limit_price)
                ),
                order_role=OrderRole(child.expected_order_role),
                strategy_identity_id=child.expected_strategy_identity,
                parent_order_id=child.expected_parent_order_id,
                oco_group_id=child.expected_oco_group_id,
                replace_generation=child.expected_replace_generation or 0,
                source_directive_identity=child.expected_source_directive_identity,
            )
            self._before_external_action(at, action="REPLACE")
            self._before_external_action(at, action="SUBMIT")
            self.broker.submit_order(instruction)
            blockers.extend(self.refresh_broker_truth(at=at))
        return tuple(sorted(set(blockers)))


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

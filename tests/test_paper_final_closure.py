from __future__ import annotations

import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from zoneinfo import ZoneInfo

from src.broker_adapter import (
    BrokerAccountSnapshot,
    BrokerOrderInstruction,
    BrokerPositionSnapshot,
    OrderRole,
    OrderType,
    StopTriggerCondition,
)
from src.contract_semantics import CloseOffset, OrderAction, PositionDirection
from src.intent import CloseExecutionChild, IntentAction, StrategyIntent
from src.jianghe_ai_trader import AttentionMode, DecisionAction, Direction, StrategyFamily
from src.jianghe_execution_bridge import JiangheExecutionBridge
from src.jianghe_response_normalizer import NormalizedJiangheDecision
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_execution_chain import PaperDeterministicExecutionChain
from src.paper_live_causal_context import LiveCausalBar, LiveCausalWake
from src.paper_order_journal import (
    BATCH_AUTHORIZED,
    CONDITIONAL_ARMED,
    CONDITIONAL_TRIGGERED,
    PaperOrderJournal,
)

from src.paper_runtime_bindings import (
    PaperToolRoleBinding,
    PaperToolRoleStatus,
)
from src.paper_tool_role_authority import current_tqsdk_paper_role_authority
from src.paper_preflight import EXTERNAL, run_paper_preflight
from src.paper_runtime_config import PaperRuntimeConfig
from src.paper_runtime_layout import PaperRuntimeLayout
from src.paper_runtime import PaperRuntimeCoordinator
from src.paper_supervisor import PaperRuntimeSupervisor
from src.paper_wake_journal import PaperWakeJournal
from src.risk_gate import RiskGate, RiskRuleSet
from src.runtime_events import BrokerConnectionState
from tests.test_paper_live_causal_context import _new_builder
from tests.test_paper_offline_runtime_drill import (
    FakeJournaledPaperBroker,
    _authority as offline_authority,
    _profile as offline_profile,
)


def _protective_stop_instruction() -> BrokerOrderInstruction:
    return BrokerOrderInstruction(
        client_request_id="protective-directive",
        concrete_contract_id="SHFE.rb9999",
        direction=PositionDirection.LONG,
        action=OrderAction.CLOSE,
        order_type=OrderType.STOP_MARKET,
        quantity=Decimal("1"),
        close_offset=CloseOffset.CLOSE_TODAY,
        trigger_price=Decimal("3490"),
        trigger_condition=StopTriggerCondition.AT_OR_BELOW,
        triggered_order_type=OrderType.MARKET,
        order_role=OrderRole.PROTECTIVE_STOP,
        strategy_identity_id="strategy",
        parent_order_id="entry-order",
        oco_group_id="exit-oco",
        source_directive_identity="jianghe-directive",
    )


def _triggered_child_instruction(
    directive: BrokerOrderInstruction,
) -> BrokerOrderInstruction:
    return BrokerOrderInstruction(
        client_request_id="protective-trigger-child",
        concrete_contract_id=directive.concrete_contract_id,
        direction=directive.direction,
        action=directive.action,
        order_type=OrderType.MARKET,
        quantity=directive.quantity,
        close_offset=directive.close_offset,
        order_role=directive.order_role,
        strategy_identity_id=directive.strategy_identity_id,
        parent_order_id=directive.parent_order_id,
        oco_group_id=directive.oco_group_id,
        source_directive_identity=directive.client_request_id,
    )


def _five_minute_bar(
    *, instrument: str, end: datetime, low: Decimal
) -> LiveCausalBar:
    start = end - timedelta(minutes=5)
    return LiveCausalBar(
        concrete_instrument=instrument,
        timeframe="5m",
        trading_day=end.date(),
        start=start,
        end=end,
        available_at=end,
        open=Decimal("3500"),
        high=Decimal("3510"),
        low=low,
        close=Decimal("3505"),
        volume=Decimal("10"),
        policy_identity="policy",
        session_authority_identity="calendar",
        source_minute_starts=tuple(start + timedelta(minutes=value) for value in range(5)),
    )


class CanonicalPaperToolRoleAuthorityTests(unittest.TestCase):
    def test_caller_adopted_claim_cannot_override_canonical_registry(self) -> None:
        authority = current_tqsdk_paper_role_authority()
        forged = PaperToolRoleBinding(
            tool_name="TqSdk",
            role="EXTERNAL_PAPER",
            status=PaperToolRoleStatus.ADOPTED,
            runtime_version="3.10.1",
            evidence_identity="caller-invented-evidence",
        )

        verification = authority.verify(
            forged,
            executable_runtime_version="3.10.1",
        )

        self.assertFalse(verification.adopted)
        self.assertIn("CANONICAL_PAPER_ROLE_NOT_ADOPTED", verification.blockers)
        self.assertIn("PAPER_ROLE_EVIDENCE_MISMATCH", verification.blockers)

    def test_current_registry_blocks_external_preflight_even_with_credentials_and_install(self) -> None:
        authority = current_tqsdk_paper_role_authority()
        forged = PaperToolRoleBinding(
            tool_name="TqSdk",
            role="EXTERNAL_PAPER",
            status=PaperToolRoleStatus.ADOPTED,
            runtime_version=authority.runtime_version,
            evidence_identity=authority.evidence_identity,
        )
        with TemporaryDirectory() as tmp:
            config = PaperRuntimeConfig(
                config_id="canonical-role-test",
                state_root=Path(tmp),
                trader_identity="trader",
                concrete_contract_id="SHFE.rb9999",
                product="rb",
                exchange="SHFE",
                tqsdk_runtime_version=authority.runtime_version,
                broker_kind="TQSDK_CANDIDATE",
                account_kind="TQSDK_PAPER",
                paper_tool_role=forged,
                symbol="SHFE.rb9999",
                max_source_age_seconds=30,
            )
            layout = PaperRuntimeLayout(
                state_root=config.state_root,
                trader_identity=config.trader_identity,
                concrete_contract_id=config.concrete_contract_id,
                config_identity=config.stable_identity,
            )
            with patch.dict("os.environ", {"TQSDK_USERNAME": "present"}), patch(
                "os.getenv", side_effect=AssertionError("credential read forbidden")
            ), patch(
                "importlib.metadata.version", side_effect=AssertionError("install check forbidden")
            ):
                report = run_paper_preflight(
                    config=config,
                    layout=layout,
                    mode=EXTERNAL,
                )
        role_check = next(
            item
            for item in report.checks
            if item.name == "EXTERNAL_PAPER_ROLE_NOT_SILENTLY_ADOPTED"
        )
        self.assertEqual("BLOCK", role_check.status)
        self.assertIn("CANONICAL_PAPER_ROLE_NOT_ADOPTED", role_check.detail)

    def test_executable_runtime_must_match_governed_role_evidence(self) -> None:
        authority = current_tqsdk_paper_role_authority()
        binding = PaperToolRoleBinding(
            tool_name=authority.tool_name,
            role=authority.role,
            status=authority.status,
            runtime_version=authority.runtime_version,
            evidence_identity=authority.evidence_identity,
        )
        verification = authority.verify(
            binding,
            executable_runtime_version="different-runtime",
        )
        self.assertFalse(verification.adopted)
        self.assertIn(
            "PAPER_EXECUTABLE_RUNTIME_VERSION_MISMATCH",
            verification.blockers,
        )


class ProtectiveDirectiveTests(unittest.TestCase):
    def test_strategy_intent_preserves_explicit_stop_semantics(self) -> None:
        at = datetime(2026, 8, 28, 9, 5, tzinfo=ZoneInfo("Asia/Shanghai"))
        intent = StrategyIntent(
            intent_id="protective-stop",
            strategy_identity_id="strategy",
            instrument="rb9999",
            concrete_contract_id="SHFE.rb9999",
            action=IntentAction.CLOSE,
            decision_at=at,
            context_identity="context",
            direction=PositionDirection.LONG,
            quantity=Decimal("1"),
            order_type=OrderType.STOP_MARKET,
            trigger_price=Decimal("3490"),
            trigger_condition=StopTriggerCondition.AT_OR_BELOW,
            triggered_order_type=OrderType.MARKET,
            order_role=OrderRole.PROTECTIVE_STOP,
            parent_order_id="entry-order",
            oco_group_id="position-exit-oco",
            source_directive_identity="jianghe-directive",
        )

        self.assertIs(OrderType.STOP_MARKET, intent.order_type)
        self.assertEqual(Decimal("3490"), intent.trigger_price)
        self.assertIs(StopTriggerCondition.AT_OR_BELOW, intent.trigger_condition)
        self.assertIs(OrderRole.PROTECTIVE_STOP, intent.order_role)
        self.assertEqual("jianghe-directive", intent.source_directive_identity)

    def test_conditional_directive_and_trigger_child_survive_restart(self) -> None:
        at = datetime(2026, 8, 28, 9, 5, tzinfo=ZoneInfo("Asia/Shanghai"))
        directive = _protective_stop_instruction()
        child = _triggered_child_instruction(directive)
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "orders.sqlite3"
            journal = PaperOrderJournal(path, require_full_envelope=True)
            journal.prepare(
                client_request_id=directive.client_request_id,
                trader_identity="trader",
                wake_identity="wake",
                decision_identity="decision",
                intent_identity="intent",
                risk_identity="risk",
                concrete_contract_id=directive.concrete_contract_id,
                instruction=directive,
                prepared_at=at,
            )
            armed = journal.arm_conditional(
                directive_client_request_id=directive.client_request_id,
                child_instruction=child,
                at=at,
            )
            self.assertEqual(CONDITIONAL_ARMED, armed.status)
            journal.record_conditional_evaluation(
                directive.client_request_id,
                bar_identity="bar-1",
                bar_end=at,
                at=at,
            )
            with self.assertRaisesRegex(RuntimeError, "OUT_OF_ORDER"):
                journal.record_conditional_evaluation(
                    directive.client_request_id,
                    bar_identity="older-bar",
                    bar_end=at - timedelta(minutes=5),
                    at=at,
                )
            journal.mark_conditional_triggered(directive.client_request_id, at=at)
            journal.close()

            reopened = PaperOrderJournal(path, require_full_envelope=True)
            try:
                triggered = reopened.get_conditional(directive.client_request_id)
                self.assertEqual(CONDITIONAL_TRIGGERED, triggered.status)
                self.assertEqual(child.identity_id, triggered.child_instruction.identity_id)
                self.assertIn(
                    "CONDITIONAL_TRIGGER_PENDING_SUBMIT",
                    reopened.recovery_blockers(),
                )
            finally:
                reopened.close()

    def test_project_trigger_submits_once_only_after_current_causal_cross(self) -> None:
        at = datetime(2024, 4, 10, 9, 20, tzinfo=ZoneInfo("Asia/Shanghai"))
        contract = "SHFE.cu2406"
        directive = BrokerOrderInstruction(
            client_request_id="protective-directive",
            concrete_contract_id=contract,
            direction=PositionDirection.LONG,
            action=OrderAction.CLOSE,
            order_type=OrderType.STOP_MARKET,
            quantity=Decimal("1"),
            close_offset=CloseOffset.CLOSE_TODAY,
            trigger_price=Decimal("3490"),
            trigger_condition=StopTriggerCondition.AT_OR_BELOW,
            triggered_order_type=OrderType.MARKET,
            order_role=OrderRole.PROTECTIVE_STOP,
            strategy_identity_id="strategy",
            source_directive_identity="jianghe-directive",
        )
        child = BrokerOrderInstruction(
            client_request_id="protective-trigger-child",
            concrete_contract_id=contract,
            direction=directive.direction,
            action=directive.action,
            order_type=OrderType.MARKET,
            quantity=directive.quantity,
            close_offset=directive.close_offset,
            order_role=directive.order_role,
            strategy_identity_id=directive.strategy_identity_id,
            source_directive_identity=directive.client_request_id,
        )

        class Broker(FakeJournaledPaperBroker):
            @property
            def order_journal(self):
                return self.journal

        class Trader:
            def decide(self, **kwargs):
                raise AssertionError("conditional trigger must not invoke trader/provider")

        with TemporaryDirectory() as tmp:
            order_journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3")
            wake_journal = PaperWakeJournal(Path(tmp) / "wakes.sqlite3")
            try:
                builder = _new_builder()
                mirror = PaperBrokerTruthMirror(broker_id="OFFLINE_FAKE_BROKER")
                broker = Broker(order_journal)
                supervisor = PaperRuntimeSupervisor(
                    actual_tqsdk_runtime_version="3.10.1",
                    authority=offline_authority(),
                    activation_profile=offline_profile(),
                    broker_mirror=mirror,
                    order_journal=order_journal,
                    wake_journal=wake_journal,
                )
                chain = PaperDeterministicExecutionChain(
                    strategy_identity="strategy",
                    instrument="cu2406",
                    concrete_contract_id=contract,
                    bridge=JiangheExecutionBridge(),
                    risk_gate=RiskGate(RiskRuleSet(
                        ruleset_id="risk", version="test-only",
                        max_order_quantity=Decimal("1"),
                    )),
                    max_market_age_seconds=60,
                )
                runtime = PaperRuntimeCoordinator(
                    trader_identity="trader",
                    concrete_contract_id=contract,
                    context_builder=builder,
                    wake_journal=wake_journal,
                    order_journal=order_journal,
                    broker_mirror=mirror,
                    supervisor=supervisor,
                    broker=broker,
                    trader=Trader(),
                    execution_chain=chain,
                )
                runtime.connect(at=at)
                runtime.market_bootstrapped = True
                runtime.market_sequence_ok = True
                runtime.mark_trader_runtime_ready()
                order_journal.prepare(
                    client_request_id=directive.client_request_id,
                    trader_identity="trader",
                    wake_identity="wake",
                    decision_identity="decision",
                    intent_identity="intent",
                    risk_identity="risk",
                    concrete_contract_id=contract,
                    instruction=directive,
                    prepared_at=at,
                )
                order_journal.arm_conditional(
                    directive_client_request_id=directive.client_request_id,
                    child_instruction=child,
                    at=at,
                )
                safe_bar = _five_minute_bar(
                    instrument="cu2406", end=at, low=Decimal("3500")
                )
                with self.assertRaisesRegex(
                    RuntimeError, "PAPER_CONDITIONAL_STALE_MARKET_DATA"
                ):
                    runtime.process_conditional_orders(
                        safe_bar, observed_at=at + timedelta(minutes=2)
                    )
                self.assertEqual(0, broker.submit_calls)
                self.assertEqual((), runtime.process_conditional_orders(
                    safe_bar, observed_at=at
                ))
                self.assertEqual(0, broker.submit_calls)

                crossed_at = at + timedelta(minutes=5)
                crossed_bar = _five_minute_bar(
                    instrument="cu2406", end=crossed_at, low=Decimal("3480")
                )
                broker.set_observed_at(crossed_at)
                runtime.refresh_broker_truth(at=crossed_at)
                self.assertEqual(
                    (directive.client_request_id,),
                    runtime.process_conditional_orders(crossed_bar, observed_at=crossed_at),
                )
                self.assertEqual(1, broker.submit_calls)
                self.assertEqual((), runtime.process_conditional_orders(
                    crossed_bar, observed_at=crossed_at
                ))
                self.assertEqual(1, broker.submit_calls)
            finally:
                order_journal.close()
                wake_journal.close()

    def test_restart_resumes_durable_trigger_without_duplicate_submission(self) -> None:
        at = datetime(2024, 4, 10, 9, 20, tzinfo=ZoneInfo("Asia/Shanghai"))
        contract = "SHFE.cu2406"
        directive = BrokerOrderInstruction(
            client_request_id="restart-stop",
            concrete_contract_id=contract,
            direction=PositionDirection.LONG,
            action=OrderAction.CLOSE,
            order_type=OrderType.STOP_MARKET,
            quantity=Decimal("1"),
            close_offset=CloseOffset.CLOSE_TODAY,
            trigger_price=Decimal("3490"),
            trigger_condition=StopTriggerCondition.AT_OR_BELOW,
            triggered_order_type=OrderType.MARKET,
            order_role=OrderRole.PROTECTIVE_STOP,
            strategy_identity_id="strategy",
            source_directive_identity="jianghe-directive",
        )
        child = BrokerOrderInstruction(
            client_request_id="restart-stop-child",
            concrete_contract_id=contract,
            direction=directive.direction,
            action=directive.action,
            order_type=OrderType.MARKET,
            quantity=directive.quantity,
            close_offset=directive.close_offset,
            order_role=directive.order_role,
            strategy_identity_id=directive.strategy_identity_id,
            source_directive_identity=directive.client_request_id,
        )

        class Broker(FakeJournaledPaperBroker):
            @property
            def order_journal(self):
                return self.journal

        class NoOp:
            def decide(self, **kwargs):
                raise AssertionError("recovery must not invoke trader")

            def plan(self, **kwargs):
                raise AssertionError("recovery must not invoke planner")

        with TemporaryDirectory() as tmp:
            order_path = Path(tmp) / "orders.sqlite3"
            wake_path = Path(tmp) / "wakes.sqlite3"
            first = PaperOrderJournal(order_path)
            first.prepare(
                client_request_id=directive.client_request_id,
                trader_identity="trader",
                wake_identity="wake",
                decision_identity="decision",
                intent_identity="intent",
                risk_identity="risk",
                concrete_contract_id=contract,
                instruction=directive,
                prepared_at=at,
            )
            first.arm_conditional(
                directive_client_request_id=directive.client_request_id,
                child_instruction=child,
                at=at,
            )
            first.mark_conditional_triggered(directive.client_request_id, at=at)
            first.close()

            reopened = PaperOrderJournal(order_path)
            wakes = PaperWakeJournal(wake_path)
            try:
                mirror = PaperBrokerTruthMirror(broker_id="OFFLINE_FAKE_BROKER")
                broker = Broker(reopened)
                supervisor = PaperRuntimeSupervisor(
                    actual_tqsdk_runtime_version="3.10.1",
                    authority=offline_authority(),
                    activation_profile=offline_profile(),
                    broker_mirror=mirror,
                    order_journal=reopened,
                    wake_journal=wakes,
                )
                runtime = PaperRuntimeCoordinator(
                    trader_identity="trader",
                    concrete_contract_id=contract,
                    context_builder=_new_builder(),
                    wake_journal=wakes,
                    order_journal=reopened,
                    broker_mirror=mirror,
                    supervisor=supervisor,
                    broker=broker,
                    trader=NoOp(),
                    risk_planner=NoOp(),
                )
                runtime.connect(at=at)
                self.assertEqual(1, broker.submit_calls)
                self.assertEqual((), runtime.resume_order_recovery(at=at))
                self.assertEqual(1, broker.submit_calls)
            finally:
                reopened.close()
                wakes.close()


class ExplicitCloseChildrenTests(unittest.TestCase):
    def test_split_close_requires_exact_positive_unique_total(self) -> None:
        at = datetime(2026, 8, 28, 9, 5, tzinfo=ZoneInfo("Asia/Shanghai"))
        intent = StrategyIntent(
            intent_id="split-close",
            strategy_identity_id="strategy",
            instrument="rb9999",
            concrete_contract_id="SHFE.rb9999",
            action=IntentAction.CLOSE,
            decision_at=at,
            context_identity="context",
            direction=PositionDirection.LONG,
            quantity=Decimal("3"),
            close_children=(
                CloseExecutionChild(CloseOffset.CLOSE_TODAY, Decimal("1")),
                CloseExecutionChild(CloseOffset.CLOSE_PREVIOUS, Decimal("2")),
            ),
        )
        self.assertEqual(Decimal("3"), sum(
            (item.quantity for item in intent.close_children), Decimal("0")
        ))

        with self.assertRaisesRegex(ValueError, "equal logical close quantity"):
            StrategyIntent(
                intent_id="bad-total",
                strategy_identity_id="strategy",
                instrument="rb9999",
                concrete_contract_id="SHFE.rb9999",
                action=IntentAction.CLOSE,
                decision_at=at,
                context_identity="context",
                direction=PositionDirection.LONG,
                quantity=Decimal("3"),
                close_children=(
                    CloseExecutionChild(CloseOffset.CLOSE_TODAY, Decimal("1")),
                ),
            )

    def test_canonical_chain_expands_explicit_shfe_close_children(self) -> None:
        at = datetime(2026, 8, 28, 9, 5, tzinfo=ZoneInfo("Asia/Shanghai"))

        class Policy:
            identity_id = "explicit-close-policy"

            def translate(self, decision, **kwargs):
                return (StrategyIntent(
                    intent_id="split-close",
                    strategy_identity_id=kwargs["strategy_identity_id"],
                    instrument=kwargs["instrument"],
                    concrete_contract_id=kwargs["concrete_contract_id"],
                    action=IntentAction.CLOSE,
                    decision_at=kwargs["decision_at"],
                    context_identity=kwargs["context_identity"],
                    direction=PositionDirection.LONG,
                    quantity=Decimal("3"),
                    close_children=(
                        CloseExecutionChild(CloseOffset.CLOSE_TODAY, Decimal("1")),
                        CloseExecutionChild(CloseOffset.CLOSE_PREVIOUS, Decimal("2")),
                    ),
                ),)

        chain = PaperDeterministicExecutionChain(
            strategy_identity="strategy",
            instrument="rb9999",
            concrete_contract_id="SHFE.rb9999",
            bridge=JiangheExecutionBridge(Policy()),
            risk_gate=RiskGate(RiskRuleSet(
                ruleset_id="risk",
                version="test-only",
                max_order_quantity=Decimal("3"),
            )),
            max_market_age_seconds=60,
        )
        mirror = PaperBrokerTruthMirror(broker_id="broker", expected_account_id="account")
        mirror.set_connection_state(BrokerConnectionState.CONNECTED)
        account = BrokerAccountSnapshot(
            account_id="account",
            snapshot_at=at,
            cash_balance=Decimal("100000"),
            reserved_margin=Decimal("0"),
            charged_costs=Decimal("0"),
            realized_pnl=Decimal("0"),
            unrealized_pnl=Decimal("0"),
            currency="CNY",
        )
        position = BrokerPositionSnapshot(
            concrete_contract_id="SHFE.rb9999",
            direction=PositionDirection.LONG,
            quantity=Decimal("3"),
            average_price=Decimal("3500"),
            snapshot_at=at,
        )
        mirror.refresh(account=account, positions=(position,), orders=(), observed_at=at)
        chain.reconcile_broker_truth(mirror, at=at)
        bar = LiveCausalBar(
            concrete_instrument="rb9999",
            timeframe="5m",
            trading_day=date(2026, 8, 28),
            start=at - timedelta(minutes=5),
            end=at,
            available_at=at,
            open=Decimal("3500"),
            high=Decimal("3510"),
            low=Decimal("3490"),
            close=Decimal("3505"),
            volume=Decimal("10"),
            policy_identity="policy",
            session_authority_identity="calendar",
            source_minute_starts=tuple(
                at - timedelta(minutes=value) for value in range(5, 0, -1)
            ),
        )
        wake = LiveCausalWake(bar=bar, observed_at=at, policy_identity="policy")
        decision = NormalizedJiangheDecision(
            family=StrategyFamily.NONE,
            action=DecisionAction.EXIT,
            direction=Direction.LONG,
            attention_mode=AttentionMode.IN_POSITION,
            decision_state="EXIT_REQUIRED",
            rationale="test",
            raw_text="{}",
            declared_unknown=(),
            principle_references=(),
            source_references=(),
            numeric_claims=(),
        )

        plans = chain.plan(
            wake=wake,
            context=(bar,),
            decision=decision,
            connection_state=BrokerConnectionState.CONNECTED,
        )

        self.assertEqual(2, len(plans))
        self.assertEqual(
            {CloseOffset.CLOSE_TODAY, CloseOffset.CLOSE_PREVIOUS},
            {item.instruction.close_offset for item in plans},
        )
        self.assertEqual(Decimal("3"), sum(
            (item.instruction.quantity for item in plans), Decimal("0")
        ))
        self.assertEqual(1, len({item.logical_execution_identity for item in plans}))

    def test_explicit_close_batch_is_durable_before_any_child_attempt(self) -> None:
        at = datetime(2026, 8, 28, 9, 5, tzinfo=ZoneInfo("Asia/Shanghai"))
        children = (
            BrokerOrderInstruction(
                client_request_id="child-today",
                concrete_contract_id="SHFE.rb9999",
                direction=PositionDirection.LONG,
                action=OrderAction.CLOSE,
                order_type=OrderType.MARKET,
                quantity=Decimal("1"),
                close_offset=CloseOffset.CLOSE_TODAY,
            ),
            BrokerOrderInstruction(
                client_request_id="child-previous",
                concrete_contract_id="SHFE.rb9999",
                direction=PositionDirection.LONG,
                action=OrderAction.CLOSE,
                order_type=OrderType.MARKET,
                quantity=Decimal("2"),
                close_offset=CloseOffset.CLOSE_PREVIOUS,
            ),
        )
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "orders.sqlite3"
            journal = PaperOrderJournal(path, require_full_envelope=True)
            batch = journal.authorize_execution_batch(
                batch_identity="batch",
                trader_identity="trader",
                wake_identity="wake",
                decision_identity="decision",
                logical_intent_identity="logical-intent",
                risk_identity="risk",
                concrete_contract_id="SHFE.rb9999",
                logical_quantity=Decimal("3"),
                children=(
                    ("intent-today", "risk", children[0]),
                    ("intent-previous", "risk", children[1]),
                ),
                at=at,
            )
            self.assertEqual(BATCH_AUTHORIZED, batch.status)
            self.assertEqual(0, journal.total_count())
            journal.close()

            reopened = PaperOrderJournal(path, require_full_envelope=True)
            try:
                pending = reopened.pending_execution_batches()
                self.assertEqual(1, len(pending))
                self.assertEqual(
                    (CloseOffset.CLOSE_TODAY, CloseOffset.CLOSE_PREVIOUS),
                    tuple(item.instruction.close_offset for item in pending[0].children),
                )
            finally:
                reopened.close()

    def test_restart_submits_each_authorized_close_child_once(self) -> None:
        at = datetime(2024, 4, 10, 9, 20, tzinfo=ZoneInfo("Asia/Shanghai"))
        contract = "SHFE.cu2406"
        children = (
            BrokerOrderInstruction(
                client_request_id="batch-today",
                concrete_contract_id=contract,
                direction=PositionDirection.LONG,
                action=OrderAction.CLOSE,
                order_type=OrderType.MARKET,
                quantity=Decimal("1"),
                close_offset=CloseOffset.CLOSE_TODAY,
            ),
            BrokerOrderInstruction(
                client_request_id="batch-previous",
                concrete_contract_id=contract,
                direction=PositionDirection.LONG,
                action=OrderAction.CLOSE,
                order_type=OrderType.MARKET,
                quantity=Decimal("2"),
                close_offset=CloseOffset.CLOSE_PREVIOUS,
            ),
        )

        class Broker(FakeJournaledPaperBroker):
            @property
            def order_journal(self):
                return self.journal

        class NoOp:
            def decide(self, **kwargs):
                raise AssertionError("batch recovery must not invoke trader")

            def plan(self, **kwargs):
                raise AssertionError("batch recovery must not invoke planner")

        with TemporaryDirectory() as tmp:
            order_path = Path(tmp) / "orders.sqlite3"
            wake_path = Path(tmp) / "wakes.sqlite3"
            first = PaperOrderJournal(order_path)
            first.authorize_execution_batch(
                batch_identity="batch",
                trader_identity="trader",
                wake_identity="wake",
                decision_identity="decision",
                logical_intent_identity="logical-intent",
                risk_identity="risk",
                concrete_contract_id=contract,
                logical_quantity=Decimal("3"),
                children=(
                    ("intent-today", "risk", children[0]),
                    ("intent-previous", "risk", children[1]),
                ),
                at=at,
            )
            first.close()

            reopened = PaperOrderJournal(order_path)
            wakes = PaperWakeJournal(wake_path)
            try:
                mirror = PaperBrokerTruthMirror(broker_id="OFFLINE_FAKE_BROKER")
                broker = Broker(reopened)
                supervisor = PaperRuntimeSupervisor(
                    actual_tqsdk_runtime_version="3.10.1",
                    authority=offline_authority(),
                    activation_profile=offline_profile(),
                    broker_mirror=mirror,
                    order_journal=reopened,
                    wake_journal=wakes,
                )
                runtime = PaperRuntimeCoordinator(
                    trader_identity="trader",
                    concrete_contract_id=contract,
                    context_builder=_new_builder(),
                    wake_journal=wakes,
                    order_journal=reopened,
                    broker_mirror=mirror,
                    supervisor=supervisor,
                    broker=broker,
                    trader=NoOp(),
                    risk_planner=NoOp(),
                )
                runtime.connect(at=at)
                self.assertEqual(2, broker.submit_calls)
                self.assertEqual((), runtime.resume_order_recovery(at=at))
                self.assertEqual(2, broker.submit_calls)
                self.assertEqual((), reopened.pending_execution_batches())
            finally:
                reopened.close()
                wakes.close()


if __name__ == "__main__":
    unittest.main()

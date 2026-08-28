"""Offline end-to-end PAPER composition/fault-injection tests.

TEST ONLY: no provider, credentials, network, external PAPER account or real money.
Fixture authority/profile/policies below are deliberately non-canonical.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.broker_adapter import BrokerAccountSnapshot, BrokerOrderInstruction, BrokerOrderSnapshot, OrderType
from src.contract_semantics import OrderAction, PositionDirection
from src.paper_activation_profile import PaperActivationProfile, PaperActivationStatus
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_execution_authority import PaperAuthorityStatus, PaperExecutionAuthority
from src.paper_live_causal_context import LiveCausalContextBuilder
from src.paper_offline_runtime_drill import OfflinePaperOrderPlan, OfflinePaperTraderDecision, PaperOfflineRuntimeDrill
from src.paper_order_journal import BROKER_ORDER_ID_KNOWN, UNKNOWN_AFTER_SUBMIT, PaperOrderJournal
from src.paper_supervisor import PaperRuntimeSupervisor
from src.paper_wake_journal import DECISION_COMMITTED, PaperWakeJournal
from src.runtime_events import BrokerConnectionState
from tests.test_paper_live_causal_context import (
    CONTRACT, TARGET_DAY, TZ, _CALENDAR, _minutes_for_days, _morning_until,
    _new_builder, _prior_days,
)

AT_0920 = datetime(TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 20, tzinfo=TZ)
AT_0925 = datetime(TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 25, tzinfo=TZ)


class FakeJournaledPaperBroker:
    offline_test_only = True
    journal_managed_execution = True

    def __init__(self, journal: PaperOrderJournal) -> None:
        self.journal = journal
        self.state = BrokerConnectionState.DISCONNECTED
        self.at = AT_0920
        self.orders: dict[str, BrokerOrderSnapshot] = {}
        self.submit_calls = 0
        self.cancel_calls = 0
        self.fail_after_submit = False
        self.fail_order_snapshot = False
        self.cancel_stuck = False
        self.fill_during_cancel = Decimal("0")

    @property
    def broker_id(self):
        return "OFFLINE_FAKE_BROKER"

    @property
    def connection_state(self):
        return self.state

    def set_observed_at(self, at):
        self.at = at

    def connect(self):
        self.state = BrokerConnectionState.CONNECTED

    def disconnect(self):
        self.state = BrokerConnectionState.DISCONNECTED

    def _connected(self):
        if self.state is not BrokerConnectionState.CONNECTED:
            raise RuntimeError("FAKE_BROKER_NOT_CONNECTED")

    def submit_order(self, instruction):
        self._connected()
        self.submit_calls += 1
        self.journal.mark_attempt_started(instruction.client_request_id, at=self.at)
        if self.fail_after_submit:
            self.journal.mark_unknown_after_submit(
                instruction.client_request_id,
                safe_reason="OFFLINE_FAULT_AFTER_SUBMIT_BOUNDARY", at=self.at)
            raise TimeoutError("OFFLINE_FAULT_AFTER_SUBMIT_BOUNDARY")
        order_id = "broker:" + instruction.client_request_id
        self.journal.mark_broker_order_known(
            instruction.client_request_id, broker_order_id=order_id, at=self.at)
        self.orders[order_id] = BrokerOrderSnapshot(
            order_id=order_id, client_request_id=instruction.client_request_id,
            concrete_contract_id=instruction.concrete_contract_id,
            direction=instruction.direction, action=instruction.action, status="LIVE",
            requested_quantity=instruction.quantity, filled_quantity=Decimal("0"),
            snapshot_at=self.at)
        return order_id

    def cancel_order(self, order_id):
        self._connected()
        self.cancel_calls += 1
        operation = self.journal.prepare_cancel_for_broker_order(order_id, at=self.at)
        self.journal.mark_cancel_attempt_started(operation.cancel_operation_id, at=self.at)
        if self.cancel_stuck:
            return
        current = self.orders[order_id]
        self.orders[order_id] = BrokerOrderSnapshot(
            order_id=current.order_id, client_request_id=current.client_request_id,
            concrete_contract_id=current.concrete_contract_id,
            direction=current.direction, action=current.action, status="CANCELLED",
            requested_quantity=current.requested_quantity,
            filled_quantity=current.filled_quantity + self.fill_during_cancel,
            snapshot_at=self.at)

    def replace_order(self, order_id, new_quantity):
        raise AssertionError("project cancel-then-replace must be used")

    def drain_events(self):
        return ()

    def fetch_account_snapshot(self):
        self._connected()
        return BrokerAccountSnapshot(
            account_id="OFFLINE_FAKE_ACCOUNT", snapshot_at=self.at,
            cash_balance=Decimal("100000"), reserved_margin=Decimal("0"),
            charged_costs=Decimal("0"), realized_pnl=Decimal("0"),
            unrealized_pnl=Decimal("0"), currency="CNY")

    def fetch_position_snapshot(self):
        self._connected()
        return ()

    def fetch_order_snapshot(self):
        self._connected()
        if self.fail_order_snapshot:
            raise RuntimeError("OFFLINE_FAULT_FETCH_ORDER_SNAPSHOT")
        return tuple(sorted(self.orders.values(), key=lambda item: item.order_id))


class FakeTrader:
    def __init__(self):
        self.calls = 0
        self.fail = False

    def decide(self, *, wake, context):
        self.calls += 1
        if self.fail:
            raise RuntimeError("OFFLINE_TRADER_FAULT")
        return OfflinePaperTraderDecision(decision_identity="decision:" + wake.wake_identity)


class FixtureRiskPlanner:
    """TEST_ONLY fixed lot/price; never a project PAPER policy."""

    def plan(self, *, wake, context, decision):
        return _plan("request:" + wake.bar.end.strftime("%Y%m%dT%H%M"), wake.wake_identity, 0)


def _plan(
    request_id: str,
    wake_identity: str,
    generation: int,
    quantity: Decimal = Decimal("1"),
) -> OfflinePaperOrderPlan:
    return OfflinePaperOrderPlan(
        intent_identity="fixture-intent:" + request_id,
        risk_identity="fixture-risk:" + request_id,
        instruction=BrokerOrderInstruction(
            client_request_id=request_id, concrete_contract_id=CONTRACT,
            direction=PositionDirection.LONG, action=OrderAction.OPEN,
            order_type=OrderType.LIMIT, quantity=quantity,
            limit_price=Decimal("70000"), strategy_identity_id="OFFLINE_FIXTURE_ONLY",
            replace_generation=generation, source_directive_identity=wake_identity))


def _authority(**changes):
    values = dict(
        authority_id="OFFLINE_FIXTURE_AUTHORITY_NOT_PROJECT_AUTHORITY",
        broker_kind="OFFLINE_FAKE", account_kind="OFFLINE_FAKE",
        status=PaperAuthorityStatus.ACTIVE, allow_connect=True,
        allow_order_submit=True, allow_order_cancel=True, allow_order_replace=True,
        allowed_contracts=(CONTRACT,))
    values.update(changes)
    return PaperExecutionAuthority(**values)


def _profile():
    return PaperActivationProfile(
        profile_id="OFFLINE_FIXTURE_PROFILE_NOT_PROJECT_POLICY",
        status=PaperActivationStatus.ACTIVE, execution_mode="PAPER",
        tqsdk_runtime_version="3.10.1",
        live_data_policy_identity="OFFLINE_FIXTURE_LIVE_POLICY",
        sizing_policy_identity="OFFLINE_FIXTURE_SIZING_POLICY",
        execution_price_policy_identity="OFFLINE_FIXTURE_PRICE_POLICY",
        close_offset_policy_identity="OFFLINE_FIXTURE_OFFSET_POLICY",
        risk_policy_identity="OFFLINE_FIXTURE_RISK_POLICY",
        broker_adapter_identity="OFFLINE_FAKE_BROKER", allowed_contracts=(CONTRACT,))


class PaperOfflineRuntimeDrillTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        root = Path(self.temp.name)
        self.order_path = root / "orders.sqlite3"
        self.wake_path = root / "wakes.sqlite3"
        self.order_journal = PaperOrderJournal(self.order_path)
        self.wake_journal = PaperWakeJournal(self.wake_path)
        self.builder = _new_builder()
        self.mirror = PaperBrokerTruthMirror(broker_id="OFFLINE_FAKE_BROKER")
        self.broker = FakeJournaledPaperBroker(self.order_journal)
        self.trader = FakeTrader()
        self.planner = FixtureRiskPlanner()
        self.runtime = self._runtime(self.builder, self.order_journal, self.wake_journal,
                                     self.broker, self.trader)

    def tearDown(self):
        try:
            self.order_journal.close()
        except Exception:
            pass
        try:
            self.wake_journal.close()
        except Exception:
            pass
        self.temp.cleanup()

    def _runtime(self, builder, orders, wakes, broker, trader, authority=None):
        supervisor = PaperRuntimeSupervisor(
            actual_tqsdk_runtime_version="3.10.1", authority=authority or _authority(),
            activation_profile=_profile(), broker_mirror=self.mirror,
            order_journal=orders, wake_journal=wakes)
        return PaperOfflineRuntimeDrill(
            trader_identity="OFFLINE_FIXTURE_TRADER", concrete_contract_id=CONTRACT,
            context_builder=builder, wake_journal=wakes, order_journal=orders,
            broker_mirror=self.mirror, supervisor=supervisor, broker=broker,
            trader=trader, risk_planner=self.planner)

    @staticmethod
    def _bootstrap_bars():
        days = _prior_days(_CALENDAR.trading_days, 3) + (TARGET_DAY,)
        return _minutes_for_days(days, until=_morning_until())

    @staticmethod
    def _slice(start, end):
        return [bar for bar in _minutes_for_days((TARGET_DAY,), until=end)
                if bar.completed_bar.start >= start]

    def _start(self):
        self.runtime.connect(at=_morning_until())
        self.runtime.bootstrap_market(self._bootstrap_bars(), observed_at=_morning_until())
        self.runtime.mark_trader_runtime_ready()

    def test_fake_end_to_end_wake_to_order_and_reconciliation(self):
        self._start()
        result = self.runtime.process_closed_minutes(
            self._slice(_morning_until(), AT_0920), observed_at=AT_0920)[0]
        self.assertEqual(1, self.trader.calls)
        self.assertEqual(1, self.broker.submit_calls)
        self.assertEqual(DECISION_COMMITTED, self.wake_journal.get(result.wake_identity).status)
        self.assertEqual(BROKER_ORDER_ID_KNOWN,
                         self.order_journal.get(result.client_request_id).status)
        assessment = self.runtime.assess(at=AT_0920, concrete_contract_id=CONTRACT)
        self.assertTrue(assessment.can_observe)
        self.assertTrue(assessment.can_submit_order)
        self.assertEqual((), self.order_journal.recovery_blockers())

    def test_trader_fault_survives_restart_and_blocks_next_dispatch(self):
        self.trader.fail = True
        self._start()
        with self.assertRaisesRegex(RuntimeError, "OFFLINE_TRADER_FAULT"):
            self.runtime.process_closed_minutes(
                self._slice(_morning_until(), AT_0920), observed_at=AT_0920)
        self.assertEqual(1, len(self.wake_journal.unresolved_dispatches()))
        checkpoint = self.builder.snapshot()
        self.order_journal.close()
        self.wake_journal.close()
        self.order_journal = PaperOrderJournal(self.order_path)
        self.wake_journal = PaperWakeJournal(self.wake_path)
        restored = LiveCausalContextBuilder.from_checkpoint(checkpoint, calendar=_CALENDAR)
        broker = FakeJournaledPaperBroker(self.order_journal)
        trader = FakeTrader()
        self.mirror = PaperBrokerTruthMirror(broker_id="OFFLINE_FAKE_BROKER")
        self.runtime = self._runtime(restored, self.order_journal, self.wake_journal, broker, trader)
        self.runtime.connect(at=AT_0920)
        self.runtime.mark_trader_runtime_ready()
        with self.assertRaisesRegex(PermissionError, "PAPER_OBSERVATION_NOT_READY"):
            self.runtime.process_closed_minutes(self._slice(AT_0920, AT_0925), observed_at=AT_0925)
        self.assertEqual(0, trader.calls)

    def test_unknown_submit_blocks_later_new_risk_without_retry(self):
        self._start()
        self.broker.fail_after_submit = True
        with self.assertRaisesRegex(TimeoutError, "OFFLINE_FAULT_AFTER_SUBMIT_BOUNDARY"):
            self.runtime.process_closed_minutes(
                self._slice(_morning_until(), AT_0920), observed_at=AT_0920)
        self.assertEqual(UNKNOWN_AFTER_SUBMIT,
                         self.order_journal.get("request:20240410T0920").status)
        self.assertEqual(1, self.broker.submit_calls)
        self.broker.fail_after_submit = False
        with self.assertRaisesRegex(PermissionError, "PAPER_ORDER_NOT_READY"):
            self.runtime.process_closed_minutes(self._slice(AT_0920, AT_0925), observed_at=AT_0925)
        self.assertEqual(1, self.broker.submit_calls)

    def test_failed_truth_refresh_invalidates_previous_snapshot(self):
        self._start()
        self.broker.fail_order_snapshot = True
        with self.assertRaisesRegex(RuntimeError, "OFFLINE_FAULT_FETCH_ORDER_SNAPSHOT"):
            self.runtime.refresh_broker_truth(at=_morning_until())
        assessment = self.runtime.assess(
            at=_morning_until(), concrete_contract_id=CONTRACT)
        self.assertFalse(assessment.can_observe)
        self.assertFalse(assessment.can_submit_order)
        self.assertIn("BROKER_MIRROR:BROKER_SNAPSHOT_MISSING",
                      assessment.observation_blockers)

    def test_cancel_then_replace_waits_for_cancelled_broker_truth(self):
        self._start()
        result = self.runtime.process_closed_minutes(
            self._slice(_morning_until(), AT_0920), observed_at=AT_0920)[0]
        child = _plan("request:replacement:1", result.wake_identity, 1)
        child_broker = self.runtime.cancel_then_replace(
            original_client_request_id=result.client_request_id, child_plan=child,
            wake_identity=result.wake_identity, decision_identity=result.decision_identity,
            replacement_generation=1, at=AT_0920 + timedelta(seconds=1))
        self.assertEqual("broker:request:replacement:1", child_broker)
        self.assertEqual(2, self.broker.submit_calls)
        self.assertEqual(1, self.broker.cancel_calls)
        self.assertEqual((), self.order_journal.unresolved_replace_operations())

    def test_stuck_cancel_never_submits_replacement_child(self):
        self._start()
        result = self.runtime.process_closed_minutes(
            self._slice(_morning_until(), AT_0920), observed_at=AT_0920)[0]
        self.broker.cancel_stuck = True
        child = _plan("request:replacement:stuck", result.wake_identity, 1)
        with self.assertRaisesRegex(RuntimeError, "REPLACE_CANCEL_UNRESOLVED"):
            self.runtime.cancel_then_replace(
                original_client_request_id=result.client_request_id, child_plan=child,
                wake_identity=result.wake_identity, decision_identity=result.decision_identity,
                replacement_generation=1, at=AT_0920 + timedelta(seconds=1))
        self.assertEqual(1, self.broker.submit_calls)
        self.assertTrue(self.order_journal.recovery_blockers())

    def test_partial_fill_caps_replacement_against_broker_remaining(self):
        self._start()
        result = self.runtime.process_closed_minutes(
            self._slice(_morning_until(), AT_0920), observed_at=AT_0920)[0]
        order_id = "broker:" + result.client_request_id
        current = self.broker.orders[order_id]
        self.broker.orders[order_id] = BrokerOrderSnapshot(
            order_id=current.order_id,
            client_request_id=current.client_request_id,
            concrete_contract_id=current.concrete_contract_id,
            direction=current.direction,
            action=current.action,
            status="PARTIALLY_FILLED",
            requested_quantity=current.requested_quantity,
            filled_quantity=Decimal("0.5"),
            snapshot_at=AT_0920,
        )
        child = _plan(
            "request:replacement:too-large",
            result.wake_identity,
            1,
            Decimal("0.75"),
        )
        with self.assertRaisesRegex(
            RuntimeError, "REPLACEMENT_QUANTITY_EXCEEDS_BROKER_REMAINING"
        ):
            self.runtime.cancel_then_replace(
                original_client_request_id=result.client_request_id,
                child_plan=child,
                wake_identity=result.wake_identity,
                decision_identity=result.decision_identity,
                replacement_generation=1,
                at=AT_0920 + timedelta(seconds=1),
            )
        self.assertEqual(0, self.broker.cancel_calls)
        self.assertEqual(1, self.broker.submit_calls)

    def test_fill_during_cancel_rechecks_replacement_remaining(self):
        self._start()
        result = self.runtime.process_closed_minutes(
            self._slice(_morning_until(), AT_0920), observed_at=AT_0920)[0]
        self.broker.fill_during_cancel = Decimal("0.5")
        child = _plan(
            "request:replacement:cancel-race",
            result.wake_identity,
            1,
            Decimal("0.75"),
        )
        with self.assertRaisesRegex(
            RuntimeError, "BROKER_REMAINING_AFTER_CANCEL"
        ):
            self.runtime.cancel_then_replace(
                original_client_request_id=result.client_request_id,
                child_plan=child,
                wake_identity=result.wake_identity,
                decision_identity=result.decision_identity,
                replacement_generation=1,
                at=AT_0920 + timedelta(seconds=1),
            )
        self.assertEqual(1, self.broker.cancel_calls)
        self.assertEqual(1, self.broker.submit_calls)

    def test_replace_permission_is_checked_before_cancel(self):
        runtime = self._runtime(
            self.builder,
            self.order_journal,
            self.wake_journal,
            self.broker,
            self.trader,
            authority=_authority(allow_order_replace=False),
        )
        self.runtime = runtime
        self._start()
        result = self.runtime.process_closed_minutes(
            self._slice(_morning_until(), AT_0920), observed_at=AT_0920)[0]
        child = _plan("request:replacement:forbidden", result.wake_identity, 1)
        with self.assertRaisesRegex(PermissionError, "REPLACE_NOT_AUTHORIZED"):
            self.runtime.cancel_then_replace(
                original_client_request_id=result.client_request_id,
                child_plan=child,
                wake_identity=result.wake_identity,
                decision_identity=result.decision_identity,
                replacement_generation=1,
                at=AT_0920 + timedelta(seconds=1),
            )
        self.assertEqual(0, self.broker.cancel_calls)
        self.assertEqual(1, self.broker.submit_calls)

    def test_connect_truth_failure_disconnects_broker(self):
        self.broker.fail_order_snapshot = True
        with self.assertRaisesRegex(RuntimeError, "OFFLINE_FAULT_FETCH_ORDER_SNAPSHOT"):
            self.runtime.connect(at=_morning_until())
        self.assertIs(BrokerConnectionState.DISCONNECTED, self.broker.connection_state)
        self.assertIs(BrokerConnectionState.DISCONNECTED, self.mirror.connection_state)

    def test_restart_connect_resumes_only_authorized_unsent_replacement(self):
        self._start()
        result = self.runtime.process_closed_minutes(
            self._slice(_morning_until(), AT_0920), observed_at=AT_0920)[0]
        original = self.order_journal.get(result.client_request_id)
        child = _plan("request:replacement:restart", result.wake_identity, 1)
        instruction = child.instruction
        recovery_at = AT_0920 + timedelta(seconds=1)
        self.order_journal.prepare(
            client_request_id=instruction.client_request_id,
            trader_identity="OFFLINE_FIXTURE_TRADER",
            wake_identity=result.wake_identity,
            decision_identity=result.decision_identity,
            intent_identity=child.intent_identity,
            risk_identity=child.risk_identity,
            concrete_contract_id=CONTRACT,
            instruction=instruction,
            prepared_at=recovery_at,
        )
        cancel = self.order_journal.prepare_cancel_for_broker_order(
            original.broker_order_id, at=recovery_at
        )
        self.order_journal.mark_cancel_attempt_started(
            cancel.cancel_operation_id, at=recovery_at
        )
        replace_id = "replace:restart"
        self.order_journal.prepare_replace(
            replace_operation_id=replace_id,
            original_client_request_id=original.client_request_id,
            replacement_generation=1,
            replacement_intent_identity=child.intent_identity,
            cancel_operation_id=cancel.cancel_operation_id,
            child_client_request_id=instruction.client_request_id,
            prepared_at=recovery_at,
        )
        current = self.broker.orders[original.broker_order_id]
        self.broker.orders[original.broker_order_id] = BrokerOrderSnapshot(
            order_id=current.order_id,
            client_request_id=current.client_request_id,
            concrete_contract_id=current.concrete_contract_id,
            direction=current.direction,
            action=current.action,
            status="CANCELLED",
            requested_quantity=current.requested_quantity,
            filled_quantity=current.filled_quantity,
            snapshot_at=recovery_at,
        )
        self.runtime.disconnect(at=recovery_at)

        self.runtime.connect(at=recovery_at)

        self.assertEqual(2, self.broker.submit_calls)
        self.assertEqual(
            BROKER_ORDER_ID_KNOWN,
            self.order_journal.get(instruction.client_request_id).status,
        )
        self.assertEqual((), self.order_journal.unresolved_replace_operations())

    def test_market_bootstrap_requires_broker_truth_first(self):
        with self.assertRaisesRegex(RuntimeError, "BOOTSTRAP_REQUIRES_CONNECTED_BROKER"):
            self.runtime.bootstrap_market(self._bootstrap_bars(), observed_at=_morning_until())

    def test_non_fake_broker_is_rejected(self):
        class NotFake:
            offline_test_only = False
            journal_managed_execution = True
        supervisor = PaperRuntimeSupervisor(
            actual_tqsdk_runtime_version="3.10.1", authority=_authority(),
            activation_profile=_profile(), broker_mirror=self.mirror,
            order_journal=self.order_journal, wake_journal=self.wake_journal)
        with self.assertRaisesRegex(PermissionError, "REQUIRES_FAKE_BROKER"):
            PaperOfflineRuntimeDrill(
                trader_identity="fixture", concrete_contract_id=CONTRACT,
                context_builder=self.builder, wake_journal=self.wake_journal,
                order_journal=self.order_journal, broker_mirror=self.mirror,
                supervisor=supervisor, broker=NotFake(), trader=self.trader,
                risk_planner=self.planner)


if __name__ == "__main__":
    unittest.main()

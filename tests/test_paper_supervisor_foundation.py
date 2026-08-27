from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

from src.broker_adapter import BrokerAccountSnapshot
from src.paper_activation_profile import PaperActivationProfile, PaperActivationStatus
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_execution_authority import PaperAuthorityStatus, PaperExecutionAuthority
from src.paper_order_journal import PaperOrderJournal
from src.paper_supervisor import PaperRuntimeSupervisor
from src.paper_wake_journal import (
    DECISION_COMMITTED,
    DISPATCH_STARTED,
    OBSERVED,
    PaperWakeJournal,
)
from src.runtime_events import BrokerConnectionState

_SH = ZoneInfo("Asia/Shanghai")


class PaperSupervisorFoundationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.order_journal = PaperOrderJournal(root / "orders.sqlite3")
        self.wake_journal = PaperWakeJournal(root / "wakes.sqlite3")
        self.now = datetime(2026, 8, 27, 14, 30, tzinfo=_SH)
        self.contract = "SHFE.rb2610"
        self.mirror = PaperBrokerTruthMirror(broker_id="tqsdk-paper")
        self.mirror.set_connection_state(BrokerConnectionState.CONNECTED)
        self.mirror.refresh(
            account=BrokerAccountSnapshot(
                account_id="paper-account",
                snapshot_at=self.now,
                cash_balance=Decimal("100000"),
                reserved_margin=Decimal("0"),
                charged_costs=Decimal("0"),
                realized_pnl=Decimal("0"),
                unrealized_pnl=Decimal("0"),
                currency="CNY",
            ),
            positions=(),
            orders=(),
            observed_at=self.now,
        )

    def tearDown(self) -> None:
        self.order_journal.close()
        self.wake_journal.close()
        self.temp.cleanup()

    @staticmethod
    def _authority(*, order: bool) -> PaperExecutionAuthority:
        return PaperExecutionAuthority(
            authority_id="paper-authority-test",
            broker_kind="TQSDK",
            account_kind="PAPER",
            status=PaperAuthorityStatus.ACTIVE,
            allow_connect=True,
            allow_order_submit=order,
            allowed_contracts=("SHFE.rb2610",),
        )

    @staticmethod
    def _pending_profile() -> PaperActivationProfile:
        return PaperActivationProfile(
            profile_id="paper-profile-pending",
            status=PaperActivationStatus.PENDING,
            execution_mode="PAPER",
            tqsdk_runtime_version="3.10.2",
            live_data_policy_identity=None,
            sizing_policy_identity=None,
            execution_price_policy_identity=None,
            close_offset_policy_identity=None,
            risk_policy_identity=None,
            broker_adapter_identity=None,
        )

    @staticmethod
    def _active_profile() -> PaperActivationProfile:
        return PaperActivationProfile(
            profile_id="paper-profile-active",
            status=PaperActivationStatus.ACTIVE,
            execution_mode="PAPER",
            tqsdk_runtime_version="3.10.2",
            live_data_policy_identity="live-policy",
            sizing_policy_identity="sizing-policy",
            execution_price_policy_identity="price-policy",
            close_offset_policy_identity="offset-policy",
            risk_policy_identity="risk-policy",
            broker_adapter_identity="tqsdk-adapter",
            allowed_contracts=("SHFE.rb2610",),
        )

    def _supervisor(
        self, *, order: bool, active_profile: bool = False, version: str = "3.10.2"
    ) -> PaperRuntimeSupervisor:
        return PaperRuntimeSupervisor(
            actual_tqsdk_runtime_version=version,
            authority=self._authority(order=order),
            activation_profile=(self._active_profile() if active_profile else self._pending_profile()),
            broker_mirror=self.mirror,
            order_journal=self.order_journal,
            wake_journal=self.wake_journal,
        )

    def _assess(self, supervisor: PaperRuntimeSupervisor):
        return supervisor.assess(
            assessed_at=self.now,
            market_bootstrapped=True,
            market_sequence_ok=True,
            trader_runtime_ready=True,
            max_broker_snapshot_age_seconds=30,
            concrete_contract_id=self.contract,
        )

    def test_pending_activation_can_connect_and_observe_but_not_order(self) -> None:
        assessment = self._assess(self._supervisor(order=False, active_profile=False))
        self.assertTrue(assessment.can_connect)
        self.assertTrue(assessment.can_observe)
        self.assertFalse(assessment.can_submit_order)
        self.assertIn("PAPER_ACTIVATION_PROFILE_NOT_ACTIVE", assessment.order_blockers)
        self.assertIn("PAPER_ORDER_SUBMIT_NOT_AUTHORIZED", assessment.order_blockers)

    def test_active_profile_and_order_authority_can_reach_order_ready(self) -> None:
        assessment = self._assess(self._supervisor(order=True, active_profile=True))
        self.assertTrue(assessment.can_connect)
        self.assertTrue(assessment.can_observe)
        self.assertTrue(assessment.can_submit_order)
        assessment.require_observation_ready()
        assessment.require_order_ready()

    def test_unresolved_order_attempt_blocks_new_risk_but_not_observation(self) -> None:
        self.order_journal.prepare(
            client_request_id="request-1",
            trader_identity="trader-1",
            wake_identity="wake-1",
            decision_identity="decision-1",
            intent_identity="intent-1",
            risk_identity="risk-1",
            concrete_contract_id=self.contract,
            prepared_at=self.now,
        )
        self.order_journal.mark_attempt_started("request-1", at=self.now)
        assessment = self._assess(self._supervisor(order=True, active_profile=True))
        self.assertTrue(assessment.can_observe)
        self.assertFalse(assessment.can_submit_order)
        self.assertIn("UNRESOLVED_PAPER_ORDER_SUBMISSION", assessment.order_blockers)

    def test_unresolved_model_dispatch_blocks_observation_and_orders(self) -> None:
        start = self.now - timedelta(minutes=5)
        self.wake_journal.observe(
            wake_identity="wake-1",
            trader_identity="trader-1",
            concrete_contract_id=self.contract,
            bar_identity="bar-1",
            bar_start=start,
            bar_end=self.now,
            observed_at=self.now,
        )
        record = self.wake_journal.mark_dispatch_started(
            "wake-1", request_id="provider-request-1", at=self.now
        )
        self.assertEqual(DISPATCH_STARTED, record.status)
        assessment = self._assess(self._supervisor(order=True, active_profile=True))
        self.assertFalse(assessment.can_observe)
        self.assertFalse(assessment.can_submit_order)
        self.assertIn("UNRESOLVED_TRADER_WAKE_DISPATCH", assessment.observation_blockers)

    def test_tqsdk_runtime_version_mismatch_blocks_all_external_progress(self) -> None:
        assessment = self._assess(
            self._supervisor(order=True, active_profile=True, version="3.10.1")
        )
        self.assertFalse(assessment.can_connect)
        self.assertFalse(assessment.can_observe)
        self.assertFalse(assessment.can_submit_order)
        self.assertIn("TQSDK_RUNTIME_VERSION_MISMATCH", assessment.connect_blockers)

    def test_wake_observation_is_idempotent_but_identity_conflicts_fail_closed(self) -> None:
        start = self.now - timedelta(minutes=5)
        first = self.wake_journal.observe(
            wake_identity="wake-1",
            trader_identity="trader-1",
            concrete_contract_id=self.contract,
            bar_identity="bar-1",
            bar_start=start,
            bar_end=self.now,
            observed_at=self.now,
        )
        second = self.wake_journal.observe(
            wake_identity="wake-1",
            trader_identity="trader-1",
            concrete_contract_id=self.contract,
            bar_identity="bar-1",
            bar_start=start,
            bar_end=self.now,
            observed_at=self.now + timedelta(seconds=1),
        )
        self.assertEqual(OBSERVED, first.status)
        self.assertEqual(first, second)
        with self.assertRaisesRegex(ValueError, "PAPER_WAKE_IDENTITY_CONFLICT"):
            self.wake_journal.observe(
                wake_identity="wake-2",
                trader_identity="trader-1",
                concrete_contract_id=self.contract,
                bar_identity="bar-1",
                bar_start=start,
                bar_end=self.now,
                observed_at=self.now,
            )

    def test_committed_decision_clears_unresolved_dispatch(self) -> None:
        start = self.now - timedelta(minutes=5)
        self.wake_journal.observe(
            wake_identity="wake-1",
            trader_identity="trader-1",
            concrete_contract_id=self.contract,
            bar_identity="bar-1",
            bar_start=start,
            bar_end=self.now,
            observed_at=self.now,
        )
        self.wake_journal.mark_dispatch_started(
            "wake-1", request_id="provider-request-1", at=self.now
        )
        committed = self.wake_journal.mark_decision_committed(
            "wake-1", decision_identity="decision-1", at=self.now
        )
        self.assertEqual(DECISION_COMMITTED, committed.status)
        self.assertEqual((), self.wake_journal.unresolved_dispatches())
        self.assertTrue(self._assess(self._supervisor(order=True, active_profile=True)).can_observe)


if __name__ == "__main__":
    unittest.main()

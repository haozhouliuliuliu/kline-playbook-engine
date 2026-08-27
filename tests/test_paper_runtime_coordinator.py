from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_execution_authority import PaperAuthorityStatus, PaperExecutionAuthority
from src.paper_order_journal import PaperOrderJournal
from src.paper_runtime import PaperRuntimeCoordinator
from src.paper_supervisor import PaperRuntimeSupervisor
from src.paper_wake_journal import PaperWakeJournal
from src.tqsdk_paper_candidate import TqSdkPaperBrokerAdapter
from src.tqsdk_paper_driver import TqSdkPaperExecutionDriver
from tests.test_paper_live_causal_context import CONTRACT, _new_builder
from tests.test_paper_offline_runtime_drill import (
    FakeJournaledPaperBroker,
    FakeTrader,
    FixtureRiskPlanner,
    _authority,
    _profile,
)


class GenericJournaledFakeBroker(FakeJournaledPaperBroker):
    """Non-offline marker: proves the coordinator itself is not fake-only."""

    offline_test_only = False

    @property
    def order_journal(self) -> PaperOrderJournal:
        return self.journal


class PaperRuntimeCoordinatorTests(unittest.TestCase):
    def test_generic_coordinator_accepts_journal_managed_non_offline_broker(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            orders = PaperOrderJournal(root / "orders.sqlite3")
            wakes = PaperWakeJournal(root / "wakes.sqlite3")
            try:
                builder = _new_builder()
                mirror = PaperBrokerTruthMirror(broker_id="OFFLINE_FAKE_BROKER")
                broker = GenericJournaledFakeBroker(orders)
                supervisor = PaperRuntimeSupervisor(
                    actual_tqsdk_runtime_version="3.10.1",
                    authority=_authority(), activation_profile=_profile(),
                    broker_mirror=mirror, order_journal=orders, wake_journal=wakes,
                )
                runtime = PaperRuntimeCoordinator(
                    trader_identity="GENERIC_TEST_TRADER",
                    concrete_contract_id=CONTRACT,
                    context_builder=builder, wake_journal=wakes,
                    order_journal=orders, broker_mirror=mirror,
                    supervisor=supervisor, broker=broker,
                    trader=FakeTrader(), risk_planner=FixtureRiskPlanner(),
                )
                self.assertIs(runtime.order_journal, broker.order_journal)
                self.assertFalse(broker.offline_test_only)
            finally:
                orders.close()
                wakes.close()

    def test_generic_coordinator_rejects_split_brain_order_journal(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            runtime_orders = PaperOrderJournal(root / "runtime.sqlite3")
            broker_orders = PaperOrderJournal(root / "broker.sqlite3")
            wakes = PaperWakeJournal(root / "wakes.sqlite3")
            try:
                builder = _new_builder()
                mirror = PaperBrokerTruthMirror(broker_id="OFFLINE_FAKE_BROKER")
                broker = GenericJournaledFakeBroker(broker_orders)
                supervisor = PaperRuntimeSupervisor(
                    actual_tqsdk_runtime_version="3.10.1",
                    authority=_authority(), activation_profile=_profile(),
                    broker_mirror=mirror, order_journal=runtime_orders, wake_journal=wakes,
                )
                with self.assertRaisesRegex(ValueError, "PAPER_RUNTIME_BROKER_JOURNAL_MISMATCH"):
                    PaperRuntimeCoordinator(
                        trader_identity="GENERIC_TEST_TRADER",
                        concrete_contract_id=CONTRACT,
                        context_builder=builder, wake_journal=wakes,
                        order_journal=runtime_orders, broker_mirror=mirror,
                        supervisor=supervisor, broker=broker,
                        trader=FakeTrader(), risk_planner=FixtureRiskPlanner(),
                    )
            finally:
                runtime_orders.close()
                broker_orders.close()
                wakes.close()

    def test_tqsdk_candidate_exposes_exact_driver_order_journal(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3")
            try:
                driver = TqSdkPaperExecutionDriver(
                    broker_id="tqsdk-paper", account_identity="paper-account",
                    session_factory=lambda: None, order_journal=journal,
                )
                authority = PaperExecutionAuthority(
                    authority_id="test-pending", broker_kind="TQSDK", account_kind="PAPER",
                    status=PaperAuthorityStatus.PENDING, allow_connect=False,
                    allow_order_submit=False,
                )
                adapter = TqSdkPaperBrokerAdapter(driver=driver, authority=authority)
                self.assertTrue(adapter.journal_managed_execution)
                self.assertIs(adapter.order_journal, journal)
            finally:
                journal.close()


if __name__ == "__main__":
    unittest.main()

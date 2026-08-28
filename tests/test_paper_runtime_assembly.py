"""Deterministic offline tests for the PAPER runtime assembly seam.

Proves ``assemble_paper_runtime`` composes the existing project runtime objects
from explicit injected dependencies with ZERO side effects (no connect, no
credential read, no provider call, no order), that the injected source is not
touched until an explicit runtime action, and that the assembled transport
drives newly completed 1m data through the generic coordinator. All brokers,
sources and authorities are offline fixtures; no external PAPER action occurs.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_order_journal import PaperOrderJournal
from src.paper_runtime_assembly import (
    PaperRuntimeAssemblyInputs,
    assemble_paper_runtime,
)
from src.paper_runtime import PaperRuntimeCoordinator
from src.paper_supervisor import PaperRuntimeSupervisor
from src.paper_wake_journal import PaperWakeJournal
from src.runtime_events import BrokerConnectionState
from tests.test_paper_live_causal_context import (
    CONTRACT,
    EXCHANGE,
    INSTRUMENT,
    PRODUCT,
    TZ,
    _CALENDAR,
    _morning_until,
    _new_builder,
    _prior_days,
)
from tests.test_paper_live_transport import (
    FakeLiveOneMinuteSource,
    _history_rows,
)
from tests.test_paper_offline_runtime_drill import (
    FakeTrader,
    FixtureRiskPlanner,
    _authority,
    _profile,
)
from tests.test_paper_runtime_coordinator import GenericJournaledFakeBroker

AT_0915 = _morning_until()
AT_0920 = datetime(2024, 4, 10, 9, 20, tzinfo=TZ)
BROKER_ID = "OFFLINE_FAKE_BROKER"


class _Harness:
    """One offline wiring harness with temp journals and fixture objects."""

    def __init__(self) -> None:
        self.temp = TemporaryDirectory()
        root = Path(self.temp.name)
        self.order_journal = PaperOrderJournal(root / "orders.sqlite3")
        self.wake_journal = PaperWakeJournal(root / "wakes.sqlite3")
        self.builder = _new_builder()
        self.mirror = PaperBrokerTruthMirror(broker_id=BROKER_ID)
        self.broker = GenericJournaledFakeBroker(self.order_journal)
        self.trader = FakeTrader()
        self.planner = FixtureRiskPlanner()
        self.source = FakeLiveOneMinuteSource(_history_rows(until=AT_0915))
        self.authority = _authority()
        self.profile = _profile()

    def inputs(self, *, supervisor=None, product=PRODUCT, exchange=EXCHANGE):
        return PaperRuntimeAssemblyInputs(
            trader_identity="OFFLINE_FIXTURE_TRADER",
            concrete_contract_id=CONTRACT,
            exchange=exchange,
            product=product,
            actual_tqsdk_runtime_version="3.10.1",
            authority=self.authority,
            activation_profile=self.profile,
            sessions=_CALENDAR,
            context_builder=self.builder,
            wake_journal=self.wake_journal,
            order_journal=self.order_journal,
            broker_mirror=self.mirror,
            broker=self.broker,
            trader=self.trader,
            risk_planner=self.planner,
            source=self.source,
            supervisor=supervisor,
        )

    def close(self) -> None:
        try:
            self.order_journal.close()
        except Exception:
            pass
        try:
            self.wake_journal.close()
        except Exception:
            pass
        self.temp.cleanup()


class AssemblySideEffectTests(unittest.TestCase):
    def test_assembly_has_no_side_effects(self) -> None:
        harness = _Harness()
        try:
            before = harness.source.read_calls
            assembly = assemble_paper_runtime(harness.inputs())
            # construction did not touch the source, broker, trader or journals
            self.assertEqual(harness.source.read_calls, before)
            self.assertIs(harness.broker.state, BrokerConnectionState.DISCONNECTED)
            self.assertEqual(harness.broker.submit_calls, 0)
            self.assertEqual(harness.broker.cancel_calls, 0)
            self.assertEqual(harness.trader.calls, 0)
            self.assertFalse(assembly.coordinator.market_bootstrapped)
            self.assertFalse(assembly.coordinator.trader_runtime_ready)
        finally:
            harness.close()

    def test_assembly_wires_transport_to_coordinator(self) -> None:
        harness = _Harness()
        try:
            assembly = assemble_paper_runtime(harness.inputs())
            self.assertIsInstance(assembly.coordinator, PaperRuntimeCoordinator)
            self.assertIsInstance(assembly.supervisor, PaperRuntimeSupervisor)
            self.assertIs(assembly.transport.consumer, assembly.coordinator)
            self.assertIs(assembly.coordinator.context_builder, harness.builder)
            self.assertIs(assembly.coordinator.broker, harness.broker)
            self.assertEqual(assembly.concrete_contract_id, CONTRACT)
            self.assertTrue(assembly.assembly_identity)
            self.assertEqual(assembly.assembly_identity, assembly.assembly_identity)
        finally:
            harness.close()

    def test_assembly_supervisor_built_when_not_injected(self) -> None:
        harness = _Harness()
        try:
            assembly = assemble_paper_runtime(harness.inputs(supervisor=None))
            self.assertIsInstance(assembly.supervisor, PaperRuntimeSupervisor)
        finally:
            harness.close()

    def test_assembly_accepts_injected_supervisor(self) -> None:
        harness = _Harness()
        try:
            supervisor = PaperRuntimeSupervisor(
                actual_tqsdk_runtime_version="3.10.1",
                authority=harness.authority,
                activation_profile=harness.profile,
                broker_mirror=harness.mirror,
                order_journal=harness.order_journal,
                wake_journal=harness.wake_journal,
            )
            assembly = assemble_paper_runtime(harness.inputs(supervisor=supervisor))
            self.assertIs(assembly.supervisor, supervisor)
        finally:
            harness.close()

    def test_assembly_fails_closed_on_identity_mismatch(self) -> None:
        harness = _Harness()
        try:
            with self.assertRaisesRegex(ValueError, "product disagrees"):
                assemble_paper_runtime(harness.inputs(product="rb"))
        finally:
            harness.close()

    def test_assembly_startup_steps_are_informational_only(self) -> None:
        harness = _Harness()
        try:
            assembly = assemble_paper_runtime(harness.inputs())
            steps = assembly.startup_steps()
            self.assertTrue(steps)
            self.assertIn("construct", steps[0])
            # the informational method must not execute anything
            self.assertEqual(harness.broker.submit_calls, 0)
            self.assertEqual(harness.trader.calls, 0)
            self.assertFalse(assembly.coordinator.market_bootstrapped)
        finally:
            harness.close()


class AssemblyEndToEndTests(unittest.TestCase):
    def test_new_closed_minutes_reach_coordinator_end_to_end(self) -> None:
        harness = _Harness()
        try:
            assembly = assemble_paper_runtime(harness.inputs())
            coordinator = assembly.coordinator
            transport = assembly.transport

            # explicit activation sequence (construct != connect != observe)
            harness.broker.set_observed_at(AT_0915)
            coordinator.connect(at=AT_0915)
            self.assertFalse(coordinator.market_bootstrapped)
            transport.bootstrap(observed_at=AT_0915)
            self.assertTrue(coordinator.market_bootstrapped)
            coordinator.mark_trader_runtime_ready(True)

            harness.broker.set_observed_at(AT_0920)
            harness.source.extend(_history_rows(until=AT_0920))
            result = transport.poll(observed_at=AT_0920)
            self.assertEqual(len(result.bars), 5)
            # one newly closed 5m wake reached the trader and one governed order
            self.assertEqual(harness.trader.calls, 1)
            self.assertEqual(harness.broker.submit_calls, 1)
            wake_results = result.consumer_result
            self.assertEqual(len(wake_results), 1)
            self.assertIsNotNone(wake_results[0].broker_order_id)

            # repeated poll with no new data must not duplicate the wake/order
            second = transport.poll(observed_at=AT_0920)
            self.assertEqual(second.bars, ())
            self.assertEqual(harness.trader.calls, 1)
            self.assertEqual(harness.broker.submit_calls, 1)
        finally:
            harness.close()

    def test_assembly_does_not_submit_before_explicit_observe(self) -> None:
        harness = _Harness()
        try:
            assembly = assemble_paper_runtime(harness.inputs())
            # connect + bootstrap + trader-ready do NOT themselves submit orders
            harness.broker.set_observed_at(AT_0915)
            assembly.coordinator.connect(at=AT_0915)
            assembly.transport.bootstrap(observed_at=AT_0915)
            assembly.coordinator.mark_trader_runtime_ready(True)
            self.assertEqual(harness.broker.submit_calls, 0)
            self.assertEqual(harness.trader.calls, 0)
        finally:
            harness.close()


if __name__ == "__main__":
    unittest.main()

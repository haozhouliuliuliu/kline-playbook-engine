"""Deterministic offline tests for the PAPER runtime controller / loop shell.

Proves construction has zero external side effects, construct != connect !=
preflight != observe, graceful stop/shutdown, checkpoint persistence, and that
the loop uses the existing transport -> coordinator path rather than
reimplementing trading logic.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_live_causal_context import LiveCausalContextBuilder
from src.paper_offline_activation_rehearsal import (
    AT_0920,
    BROKER_ID,
    CONTRACT,
    EXCHANGE,
    INSTRUMENT,
    MORNING_UNTIL,
    PRODUCT,
    RUNTIME_VERSION,
    TRADER_IDENTITY,
    RehearsalFakeBroker,
    RehearsalFakeRiskPlanner,
    RehearsalFakeTrader,
    RehearsalLiveSource,
    _history_rows,
    build_rehearsal_calendar,
    rehearsal_authority,
    rehearsal_profile,
)
from src.paper_order_journal import PaperOrderJournal
from src.paper_runtime_assembly import PaperRuntimeAssemblyInputs, assemble_paper_runtime
from src.paper_runtime_config import PaperRuntimeConfig
from src.paper_runtime_controller import PaperRuntimeController
from src.paper_runtime_layout import PaperRuntimeLayout
from src.paper_wake_journal import PaperWakeJournal
from src.runtime_events import BrokerConnectionState


def _config(state_root: Path) -> PaperRuntimeConfig:
    return (
        PaperRuntimeConfig(
            config_id="CONTROLLER_CONFIG",
            state_root=state_root,
            trader_identity=TRADER_IDENTITY,
            concrete_contract_id=CONTRACT,
            product=PRODUCT,
            exchange=EXCHANGE,
            tqsdk_runtime_version=RUNTIME_VERSION,
            broker_kind="TQSDK_CANDIDATE",
            account_kind="TQSDK_PAPER",
            symbol=INSTRUMENT,
        )
        .bind_activation_profile(rehearsal_profile())
        .bind_authority(rehearsal_authority())
    )


class _Harness:
    def __init__(self, state_root: Path) -> None:
        self.config = _config(state_root)
        self.layout = PaperRuntimeLayout(
            state_root=self.config.state_root,
            trader_identity=self.config.trader_identity,
            concrete_contract_id=self.config.concrete_contract_id,
            config_identity=self.config.stable_identity,
        )
        self.layout.ensure_initialized()
        self.order_journal = PaperOrderJournal(self.layout.order_journal_path)
        self.wake_journal = PaperWakeJournal(self.layout.wake_journal_path)
        self.mirror = PaperBrokerTruthMirror(broker_id=BROKER_ID)
        self.calendar = build_rehearsal_calendar()
        self.builder = LiveCausalContextBuilder(
            exchange=EXCHANGE, concrete_instrument=INSTRUMENT, product=PRODUCT, calendar=self.calendar
        )
        self.broker = RehearsalFakeBroker(self.order_journal)
        self.source = RehearsalLiveSource(_history_rows(self.calendar, until=MORNING_UNTIL))
        self.trader = RehearsalFakeTrader()
        self.planner = RehearsalFakeRiskPlanner()
        self.assembly = assemble_paper_runtime(
            PaperRuntimeAssemblyInputs(
                trader_identity=self.config.trader_identity,
                concrete_contract_id=self.config.concrete_contract_id,
                exchange=EXCHANGE,
                product=PRODUCT,
                actual_tqsdk_runtime_version=RUNTIME_VERSION,
                authority=self.config.authority,
                activation_profile=self.config.activation_profile,
                sessions=self.calendar,
                context_builder=self.builder,
                wake_journal=self.wake_journal,
                order_journal=self.order_journal,
                broker_mirror=self.mirror,
                broker=self.broker,
                trader=self.trader,
                risk_planner=self.planner,
                source=self.source,
                symbol=INSTRUMENT,
            )
        )
        self.controller = PaperRuntimeController(
            config=self.config, layout=self.layout, assembly=self.assembly
        )

    def close(self) -> None:
        try:
            self.order_journal.close()
        except Exception:  # noqa: BLE001
            pass
        try:
            self.wake_journal.close()
        except Exception:  # noqa: BLE001
            pass


class PaperRuntimeControllerTests(unittest.TestCase):
    def test_construction_has_zero_external_side_effects(self) -> None:
        with TemporaryDirectory() as tmp:
            harness = _Harness(Path(tmp))
            try:
                # construction did not connect, bootstrap, submit or observe
                self.assertIs(harness.broker.state, BrokerConnectionState.DISCONNECTED)
                self.assertEqual(harness.broker.submit_calls, 0)
                self.assertEqual(harness.broker.cancel_calls, 0)
                self.assertEqual(harness.trader.calls, 0)
                self.assertFalse(harness.controller.coordinator.market_bootstrapped)
                self.assertFalse(harness.controller.coordinator.trader_runtime_ready)
                self.assertFalse(harness.controller.closed)
            finally:
                harness.close()

    def test_controller_rejects_identity_mismatch(self) -> None:
        with TemporaryDirectory() as tmp:
            harness = _Harness(Path(tmp))
            try:
                config2 = PaperRuntimeConfig(
                    config_id="OTHER",
                    state_root=Path(tmp),
                    trader_identity="OTHER_TRADER",
                    concrete_contract_id=CONTRACT,
                    product=PRODUCT,
                    exchange=EXCHANGE,
                    tqsdk_runtime_version=RUNTIME_VERSION,
                    broker_kind="TQSDK_CANDIDATE",
                    account_kind="TQSDK_PAPER",
                    symbol=INSTRUMENT,
                )
                with self.assertRaisesRegex(ValueError, "PAPER_CONTROLLER_TRADER_IDENTITY_MISMATCH"):
                    PaperRuntimeController(
                        config=config2, layout=harness.layout, assembly=harness.assembly
                    )
            finally:
                harness.close()

    def test_preflight_is_read_only_and_before_connect(self) -> None:
        with TemporaryDirectory() as tmp:
            harness = _Harness(Path(tmp))
            try:
                report = harness.controller.preflight(mode="OFFLINE_REHEARSAL")
                self.assertTrue(report.ready)
                # preflight did not connect the broker
                self.assertIs(harness.broker.state, BrokerConnectionState.DISCONNECTED)
                self.assertEqual(harness.broker.submit_calls, 0)
            finally:
                harness.close()

    def test_full_lifecycle_construct_connect_bootstrap_ready_observe(self) -> None:
        with TemporaryDirectory() as tmp:
            harness = _Harness(Path(tmp))
            try:
                controller = harness.controller
                # construct != connect
                self.assertIs(harness.broker.state, BrokerConnectionState.DISCONNECTED)
                harness.broker.set_observed_at(MORNING_UNTIL)
                controller.connect(at=MORNING_UNTIL)
                self.assertIs(harness.broker.state, BrokerConnectionState.CONNECTED)
                # bootstrap seeds market context (no historical wake)
                controller.bootstrap(observed_at=MORNING_UNTIL)
                self.assertTrue(controller.coordinator.market_bootstrapped)
                # mark trader ready then observe (observe != submit before ready)
                self.assertEqual(harness.broker.submit_calls, 0)
                controller.mark_trader_ready(True)
                harness.broker.set_observed_at(AT_0920)
                harness.source.extend(_history_rows(harness.calendar, until=AT_0920))
                result = controller.poll(observed_at=AT_0920)
                self.assertEqual(len(result.bars), 5)
                self.assertEqual(harness.trader.calls, 1)
                self.assertEqual(harness.broker.submit_calls, 1)
            finally:
                harness.close()

    def test_observe_does_not_submit_before_trader_ready(self) -> None:
        with TemporaryDirectory() as tmp:
            harness = _Harness(Path(tmp))
            try:
                controller = harness.controller
                harness.broker.set_observed_at(MORNING_UNTIL)
                controller.connect(at=MORNING_UNTIL)
                controller.bootstrap(observed_at=MORNING_UNTIL)
                # do NOT mark trader ready; poll must not reach the trader
                harness.broker.set_observed_at(AT_0920)
                harness.source.extend(_history_rows(harness.calendar, until=AT_0920))
                with self.assertRaisesRegex(RuntimeError, "PAPER_TRADER_NOT_READY"):
                    controller.poll(observed_at=AT_0920)
                self.assertEqual(harness.trader.calls, 0)
                self.assertEqual(harness.broker.submit_calls, 0)
            finally:
                harness.close()

    def test_graceful_stop_via_should_stop(self) -> None:
        with TemporaryDirectory() as tmp:
            harness = _Harness(Path(tmp))
            try:
                controller = harness.controller
                harness.broker.set_observed_at(MORNING_UNTIL)
                controller.connect(at=MORNING_UNTIL)
                controller.bootstrap(observed_at=MORNING_UNTIL)
                controller.mark_trader_ready(True)
                stats = controller.run_loop(
                    observed_at_provider=lambda: MORNING_UNTIL,
                    should_stop=lambda: True,
                )
                self.assertEqual(stats.polls, 0)
            finally:
                harness.close()

    def test_graceful_stop_via_max_polls(self) -> None:
        with TemporaryDirectory() as tmp:
            harness = _Harness(Path(tmp))
            try:
                controller = harness.controller
                harness.broker.set_observed_at(MORNING_UNTIL)
                controller.connect(at=MORNING_UNTIL)
                controller.bootstrap(observed_at=MORNING_UNTIL)
                controller.mark_trader_ready(True)
                stats = controller.run_loop(
                    observed_at_provider=lambda: MORNING_UNTIL,
                    max_polls=3,
                )
                self.assertEqual(stats.polls, 3)
            finally:
                harness.close()

    def test_shutdown_disconnects_persists_checkpoint_and_closes(self) -> None:
        with TemporaryDirectory() as tmp:
            harness = _Harness(Path(tmp))
            try:
                controller = harness.controller
                harness.broker.set_observed_at(MORNING_UNTIL)
                controller.connect(at=MORNING_UNTIL)
                controller.bootstrap(observed_at=MORNING_UNTIL)
                controller.shutdown(at=MORNING_UNTIL, persist_checkpoint=True)
                self.assertTrue(controller.closed)
                self.assertIs(harness.broker.state, BrokerConnectionState.DISCONNECTED)
                self.assertTrue(harness.layout.causal_checkpoint_path.exists())
                # shutdown is idempotent
                controller.shutdown(at=MORNING_UNTIL)
            finally:
                harness.close()

    def test_operations_after_shutdown_fail_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            harness = _Harness(Path(tmp))
            try:
                controller = harness.controller
                controller.shutdown(at=MORNING_UNTIL, persist_checkpoint=False)
                with self.assertRaisesRegex(RuntimeError, "PAPER_CONTROLLER_CLOSED"):
                    controller.connect(at=MORNING_UNTIL)
                with self.assertRaisesRegex(RuntimeError, "PAPER_CONTROLLER_CLOSED"):
                    controller.poll(observed_at=MORNING_UNTIL)
                with self.assertRaisesRegex(RuntimeError, "PAPER_CONTROLLER_CLOSED"):
                    controller.bootstrap(observed_at=MORNING_UNTIL)
            finally:
                harness.close()

    def test_loop_rejects_invalid_arguments(self) -> None:
        with TemporaryDirectory() as tmp:
            harness = _Harness(Path(tmp))
            try:
                controller = harness.controller
                with self.assertRaises(TypeError):
                    controller.run_loop(observed_at_provider=None)
                with self.assertRaises(ValueError):
                    controller.run_loop(observed_at_provider=lambda: MORNING_UNTIL, max_polls=-1)
            finally:
                harness.close()


if __name__ == "__main__":
    unittest.main()

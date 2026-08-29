"""Offline end-to-end proof for the REAL CTP execution composition seam."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from src.fangzheng_ctp_candidate import (
    CtpCallback,
    CtpCallbackType,
    CtpOrderRecord,
    CtpOrderAcknowledgement,
    CtpPositionRecord,
    CtpSessionState,
    CtpTradeRecord,
    CtpTradeFill,
    FangzhengCtpBrokerAdapter,
)
from src.fangzheng_ctp_fake import FakeCtpOperation, FakeCtpStep, ScriptedCtpTransport
from src.real_execution_composition import (
    RealExecutionComposition,
    RealExecutionInconsistencyError,
    RealOrderLifecycle,
)
from src.real_safety_state import RealSafetyController
from src.runtime_events import BrokerConnectionState
from src.runtime_ledger import RuntimeLedger
from src.trading_state import OrderStatus, TradingState
from tests.runtime_synthetic_fixture import (
    DEFAULT_STARTING_CAPITAL,
    make_accounting,
    make_contract_spec,
)
from tests.test_fangzheng_ctp_candidate import CONTRACT, instruction, profile
from tests.test_fangzheng_ctp_fake import callback, establish_ready, ready_steps


NOW = datetime(2026, 8, 29, 1, 2, tzinfo=timezone.utc)
TRADING_DAY = "20260829"


def _trading_state() -> TradingState:
    return TradingState(
        runtime_id="real-composition-fixture",
        runtime_version="test-v0.1",
        created_at=NOW,
        starting_capital=DEFAULT_STARTING_CAPITAL,
        contract_specs=(make_contract_spec(instrument=CONTRACT),),
        accounting=make_accounting(),
        ledger=RuntimeLedger(),
        connection_state=BrokerConnectionState.CONNECTED,
    )


def _ready_query_steps(
    *, orders: tuple[CtpOrderRecord, ...] = (), trades: tuple[object, ...] = (), positions=()
) -> tuple[FakeCtpStep, ...]:
    steps = list(ready_steps())
    steps[4] = replace(
        steps[4],
        callbacks=(callback("positions", CtpCallbackType.POSITION_SNAPSHOT, positions,
                            trading_day=TRADING_DAY),),
    )
    steps[5] = replace(
        steps[5],
        callbacks=(callback("orders", CtpCallbackType.ORDER_SNAPSHOT, orders,
                            trading_day=TRADING_DAY),),
    )
    steps[6] = replace(
        steps[6],
        callbacks=(callback("trades", CtpCallbackType.TRADE_SNAPSHOT, trades,
                            trading_day=TRADING_DAY),),
    )
    return tuple(steps)


class RealExecutionCompositionTests(unittest.TestCase):
    def test_disconnect_before_ack_restarts_and_complete_query_recovers_open(self) -> None:
        with TemporaryDirectory() as tmp:
            transport = ScriptedCtpTransport(ready_steps() + (
                FakeCtpStep(
                    FakeCtpOperation.SUBMIT,
                    (callback("disconnect", CtpCallbackType.DISCONNECTED),),
                    expected_project_order_id="project-order-1",
                ),
            ))
            adapter = FangzhengCtpBrokerAdapter(transport, profile())
            establish_ready(adapter)
            composition = RealExecutionComposition(
                path=Path(tmp) / "real-execution.sqlite3",
                adapter=adapter,
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-20260829",
                safety_controller=RealSafetyController(NOW),
            )

            composition.submit_order(instruction(), submitted_at=NOW)
            composition.consume_adapter_events()

            pending = composition.order_for("project-order-1")
            self.assertIs(pending.lifecycle, RealOrderLifecycle.UNKNOWN)
            self.assertFalse(composition.new_risk_allowed)
            self.assertEqual(
                composition.trading_state.order_for("project-order-1").status,
                OrderStatus.PENDING_SUBMIT,
            )
            self.assertEqual(len(transport.submits), 1)

            broker_order = CtpOrderRecord(
                "project-order-1", "request-1", "broker-order-1", CONTRACT,
                instruction().direction, instruction().action, "LIVE",
                Decimal("2"), Decimal("0"), NOW,
            )
            restarted_transport = ScriptedCtpTransport(
                _ready_query_steps(orders=(broker_order,))
            )
            restarted_adapter = FangzhengCtpBrokerAdapter(restarted_transport, profile())
            establish_ready(restarted_adapter)
            restarted = RealExecutionComposition(
                path=Path(tmp) / "real-execution.sqlite3",
                adapter=restarted_adapter,
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-20260829",
                safety_controller=RealSafetyController(NOW),
            )
            report = restarted.reconcile_adapter_truth(
                round_id="round-open",
                requested_at=NOW,
                observed_at=NOW,
                expected_account=restarted_adapter.fetch_account_snapshot(),
                expected_positions=(),
            )

            recovered = restarted.order_for("project-order-1")
            self.assertTrue(report.broker_truth_complete)
            self.assertIs(recovered.lifecycle, RealOrderLifecycle.OPEN)
            self.assertEqual(recovered.broker_order_id, "broker-order-1")
            self.assertEqual(
                restarted.trading_state.order_for("project-order-1").status,
                OrderStatus.LIVE,
            )
            restarted.submit_order(instruction(), submitted_at=NOW)
            self.assertEqual(restarted_transport.submits, ())
            self.assertIs(restarted_adapter.session_state, CtpSessionState.READY_FOR_RECONCILIATION)

    def test_complete_query_recovers_filled_once_with_economic_effect(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "real-execution.sqlite3"
            first_transport = ScriptedCtpTransport(ready_steps() + (
                FakeCtpStep(
                    FakeCtpOperation.SUBMIT,
                    (callback("disconnect", CtpCallbackType.DISCONNECTED),),
                    expected_project_order_id="project-order-1",
                ),
            ))
            first_adapter = FangzhengCtpBrokerAdapter(first_transport, profile())
            establish_ready(first_adapter)
            first = RealExecutionComposition(
                path=path,
                adapter=first_adapter,
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-20260829",
            )
            first.submit_order(instruction(), submitted_at=NOW)
            first.consume_adapter_events()

            broker_order = CtpOrderRecord(
                "project-order-1", "request-1", "broker-order-1", CONTRACT,
                instruction().direction, instruction().action, "FILLED",
                Decimal("2"), Decimal("2"), NOW,
            )
            broker_position = CtpPositionRecord(
                CONTRACT, instruction().direction, Decimal("2"), Decimal("3500"), NOW
            )
            broker_trade = CtpTradeRecord(
                "trade-1", "project-order-1", "broker-order-1",
                Decimal("2"), Decimal("3500"), NOW,
            )
            restarted_transport = ScriptedCtpTransport(_ready_query_steps(
                orders=(broker_order,), trades=(broker_trade,), positions=(broker_position,)
            ))
            restarted_adapter = FangzhengCtpBrokerAdapter(restarted_transport, profile())
            establish_ready(restarted_adapter)
            restarted = RealExecutionComposition(
                path=path,
                adapter=restarted_adapter,
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-20260829",
            )

            report = restarted.reconcile_adapter_truth(
                round_id="round-filled",
                requested_at=NOW,
                observed_at=NOW,
                expected_account=restarted_adapter.fetch_account_snapshot(),
                expected_positions=(),
            )

            recovered = restarted.order_for("project-order-1")
            runtime_order = restarted.trading_state.order_for("project-order-1")
            self.assertTrue(report.new_risk_allowed)
            self.assertIs(recovered.lifecycle, RealOrderLifecycle.FILLED)
            self.assertEqual(recovered.filled_quantity, Decimal("2"))
            self.assertEqual(runtime_order.status, OrderStatus.FILLED)
            self.assertEqual(runtime_order.filled_quantity, Decimal("2"))
            self.assertEqual(restarted.trading_state.positions[0].quantity, Decimal("2"))

    def test_incomplete_query_preserves_unknown_and_blocks_new_risk(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "real-execution.sqlite3"
            transport = ScriptedCtpTransport(ready_steps() + (
                FakeCtpStep(
                    FakeCtpOperation.SUBMIT,
                    (callback("disconnect", CtpCallbackType.DISCONNECTED),),
                    expected_project_order_id="project-order-1",
                ),
            ))
            adapter = FangzhengCtpBrokerAdapter(transport, profile())
            establish_ready(adapter)
            composition = RealExecutionComposition(
                path=path, adapter=adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
            )
            composition.submit_order(instruction(), submitted_at=NOW)
            composition.consume_adapter_events()

            incomplete_steps = list(_ready_query_steps())
            incomplete_steps[4] = FakeCtpStep(FakeCtpOperation.QUERY_POSITIONS)
            restarted_transport = ScriptedCtpTransport(tuple(incomplete_steps))
            restarted_adapter = FangzhengCtpBrokerAdapter(restarted_transport, profile())
            establish_ready(restarted_adapter)
            restarted = RealExecutionComposition(
                path=path, adapter=restarted_adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
            )

            report = restarted.reconcile_adapter_truth(
                round_id="round-incomplete", requested_at=NOW, observed_at=NOW,
                expected_account=restarted_adapter.fetch_account_snapshot(),
                expected_positions=(),
            )

            self.assertFalse(report.broker_truth_complete)
            self.assertFalse(report.new_risk_allowed)
            self.assertIn("POSITION_QUERY_UNKNOWN", report.blockers)
            self.assertIs(
                restarted.order_for("project-order-1").lifecycle,
                RealOrderLifecycle.UNKNOWN,
            )

    def test_fill_before_ack_and_identical_restart_replay_apply_economics_once(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "real-execution.sqlite3"
            transport = ScriptedCtpTransport(ready_steps() + (
                FakeCtpStep(FakeCtpOperation.SUBMIT,
                            expected_project_order_id="project-order-1"),
            ))
            adapter = FangzhengCtpBrokerAdapter(transport, profile())
            establish_ready(adapter)
            composition = RealExecutionComposition(
                path=path, adapter=adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
            )
            composition.submit_order(instruction(), submitted_at=NOW)
            fill = CtpTradeFill(
                "project-order-1", "request-1", "broker-order-1", "trade-1",
                Decimal("1"), Decimal("3500"),
            )
            transport.inject_callbacks((callback(
                "fill-first", CtpCallbackType.TRADE_FILLED, fill,
                trading_day=TRADING_DAY,
            ),))
            composition.consume_adapter_events()
            self.assertEqual(composition.trading_state.positions[0].quantity, Decimal("1"))
            transport.inject_callbacks((callback(
                "ack-after-fill",
                CtpCallbackType.ORDER_ACKNOWLEDGED,
                CtpOrderAcknowledgement(
                    "project-order-1", "request-1", "broker-order-1", "cancel-token"
                ),
                trading_day=TRADING_DAY,
            ),))
            composition.consume_adapter_events()
            self.assertEqual(
                composition.trading_state.order_for("project-order-1").status,
                OrderStatus.PARTIALLY_FILLED,
            )
            self.assertEqual(
                composition.trading_state.order_for("project-order-1").filled_quantity,
                Decimal("1"),
            )

            restarted_transport = ScriptedCtpTransport(ready_steps())
            restarted_adapter = FangzhengCtpBrokerAdapter(restarted_transport, profile())
            establish_ready(restarted_adapter)
            restarted = RealExecutionComposition(
                path=path, adapter=restarted_adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
            )
            restarted_transport.inject_callbacks((callback(
                "fill-replayed-after-restart", CtpCallbackType.TRADE_FILLED, fill,
                trading_day=TRADING_DAY,
            ),))

            results = restarted.consume_adapter_events()

            self.assertEqual(results, ())
            self.assertEqual(
                restarted.order_for("project-order-1").filled_quantity, Decimal("1")
            )
            runtime_order = restarted.trading_state.order_for("project-order-1")
            self.assertEqual(runtime_order.filled_quantity, Decimal("1"))
            self.assertEqual(runtime_order.concrete_contract_id, CONTRACT)
            self.assertEqual(runtime_order.direction, instruction().direction)
            self.assertEqual(runtime_order.action, instruction().action)
            self.assertEqual(restarted.trading_state.positions[0].quantity, Decimal("1"))

    def test_conflicting_trade_identity_latches_hard_inconsistency(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "real-execution.sqlite3"
            transport = ScriptedCtpTransport(ready_steps() + (
                FakeCtpStep(FakeCtpOperation.SUBMIT,
                            expected_project_order_id="project-order-1"),
            ))
            adapter = FangzhengCtpBrokerAdapter(transport, profile())
            establish_ready(adapter)
            composition = RealExecutionComposition(
                path=path, adapter=adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
            )
            composition.submit_order(instruction(), submitted_at=NOW)
            first_fill = CtpTradeFill(
                "project-order-1", "request-1", "broker-order-1", "trade-1",
                Decimal("1"), Decimal("3500"),
            )
            transport.inject_callbacks((callback(
                "first", CtpCallbackType.TRADE_FILLED, first_fill,
                trading_day=TRADING_DAY,
            ),))
            composition.consume_adapter_events()

            restarted_transport = ScriptedCtpTransport(ready_steps())
            restarted_adapter = FangzhengCtpBrokerAdapter(restarted_transport, profile())
            establish_ready(restarted_adapter)
            safety = RealSafetyController(NOW)
            restarted = RealExecutionComposition(
                path=path, adapter=restarted_adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
                safety_controller=safety,
            )
            conflicting = replace(first_fill, quantity=Decimal("0.5"))
            restarted_transport.inject_callbacks((callback(
                "conflicting", CtpCallbackType.TRADE_FILLED, conflicting,
                trading_day=TRADING_DAY,
            ),))

            with self.assertRaisesRegex(
                RealExecutionInconsistencyError, "DUPLICATE_EXTERNAL_FACT_DIFFERENT_CONTENT"
            ):
                restarted.consume_adapter_events()

            self.assertIs(
                restarted.order_for("project-order-1").lifecycle,
                RealOrderLifecycle.INCONSISTENT,
            )
            self.assertTrue(safety.state.hard_inconsistency_latched)
            self.assertFalse(restarted.new_risk_allowed)

    def test_external_order_latches_persist_until_verified_clean_reconciliation(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "real-execution.sqlite3"
            external_order = CtpOrderRecord(
                "manual-order", "manual-request", "broker-manual-1", CONTRACT,
                instruction().direction, instruction().action, "LIVE",
                Decimal("1"), Decimal("0"), NOW,
            )
            transport = ScriptedCtpTransport(_ready_query_steps(orders=(external_order,)))
            adapter = FangzhengCtpBrokerAdapter(transport, profile())
            establish_ready(adapter)
            safety = RealSafetyController(NOW)
            composition = RealExecutionComposition(
                path=path, adapter=adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
                safety_controller=safety,
            )

            report = composition.reconcile_adapter_truth(
                round_id="round-external", requested_at=NOW, observed_at=NOW,
                expected_account=adapter.fetch_account_snapshot(), expected_positions=(),
            )

            self.assertFalse(report.new_risk_allowed)
            self.assertIn("EXTERNAL_MUTATION_UNRESOLVED", composition.active_blockers())
            self.assertIs(
                safety.state.external_mutation_status,
                safety.state.external_mutation_status.UNRESOLVED,
            )

            clean_transport = ScriptedCtpTransport(_ready_query_steps())
            clean_adapter = FangzhengCtpBrokerAdapter(clean_transport, profile())
            establish_ready(clean_adapter)
            restored_safety = RealSafetyController(NOW)
            restored = RealExecutionComposition(
                path=path, adapter=clean_adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
                safety_controller=restored_safety,
            )
            self.assertFalse(restored.new_risk_allowed)
            clean_report = restored.reconcile_adapter_truth(
                round_id="round-clean", requested_at=NOW, observed_at=NOW,
                expected_account=clean_adapter.fetch_account_snapshot(), expected_positions=(),
                confirm_external_resolution=True,
            )

            self.assertFalse(clean_report.new_risk_allowed)
            self.assertNotIn("EXTERNAL_MUTATION_UNRESOLVED", restored.active_blockers())
            restored_safety.resume("explicit resume after verified reconciliation", NOW)
            self.assertTrue(restored.new_risk_allowed)

    def test_old_session_fill_cannot_establish_current_order_truth(self) -> None:
        with TemporaryDirectory() as tmp:
            transport = ScriptedCtpTransport(ready_steps() + (
                FakeCtpStep(FakeCtpOperation.SUBMIT,
                            expected_project_order_id="project-order-1"),
            ))
            adapter = FangzhengCtpBrokerAdapter(transport, profile())
            establish_ready(adapter)
            composition = RealExecutionComposition(
                path=Path(tmp) / "real-execution.sqlite3",
                adapter=adapter,
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-20260829",
                safety_controller=RealSafetyController(NOW),
            )
            composition.submit_order(instruction(), submitted_at=NOW)
            transport.inject_callbacks((callback(
                "old-session-fill",
                CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "project-order-1", "request-1", "broker-order-1", "trade-old",
                    Decimal("1"), Decimal("3500"),
                ),
                trading_day="20260828",
            ),))

            with self.assertRaisesRegex(ValueError, "TRADING_DAY_MISMATCH"):
                composition.consume_adapter_events()

            self.assertIs(
                composition.order_for("project-order-1").lifecycle,
                RealOrderLifecycle.UNKNOWN,
            )
            self.assertEqual(
                composition.trading_state.order_for("project-order-1").filled_quantity,
                Decimal("0"),
            )
            self.assertFalse(composition.new_risk_allowed)

    def test_complete_query_cancelled_terminal_state_survives_restart(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "real-execution.sqlite3"
            transport = ScriptedCtpTransport(ready_steps() + (
                FakeCtpStep(
                    FakeCtpOperation.SUBMIT,
                    (callback("disconnect", CtpCallbackType.DISCONNECTED),),
                    expected_project_order_id="project-order-1",
                ),
            ))
            adapter = FangzhengCtpBrokerAdapter(transport, profile())
            establish_ready(adapter)
            first = RealExecutionComposition(
                path=path, adapter=adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
            )
            first.submit_order(instruction(), submitted_at=NOW)
            first.consume_adapter_events()

            cancelled = CtpOrderRecord(
                "project-order-1", "request-1", "broker-order-1", CONTRACT,
                instruction().direction, instruction().action, "CANCELLED",
                Decimal("2"), Decimal("0"), NOW,
            )
            query_transport = ScriptedCtpTransport(_ready_query_steps(orders=(cancelled,)))
            query_adapter = FangzhengCtpBrokerAdapter(query_transport, profile())
            establish_ready(query_adapter)
            recovered = RealExecutionComposition(
                path=path, adapter=query_adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
            )
            recovered.reconcile_adapter_truth(
                round_id="round-cancelled", requested_at=NOW, observed_at=NOW,
                expected_account=query_adapter.fetch_account_snapshot(), expected_positions=(),
            )
            self.assertEqual(
                recovered.trading_state.order_for("project-order-1").status,
                OrderStatus.CANCELLED,
            )

            final_transport = ScriptedCtpTransport(ready_steps())
            final_adapter = FangzhengCtpBrokerAdapter(final_transport, profile())
            establish_ready(final_adapter)
            final = RealExecutionComposition(
                path=path, adapter=final_adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
            )
            self.assertIs(
                final.order_for("project-order-1").lifecycle,
                RealOrderLifecycle.CANCELLED,
            )
            self.assertEqual(
                final.trading_state.order_for("project-order-1").status,
                OrderStatus.CANCELLED,
            )

    def test_unknown_submit_is_reconstructed_in_a_fresh_child_process(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "real-execution.sqlite3"
            transport = ScriptedCtpTransport(ready_steps() + (
                FakeCtpStep(
                    FakeCtpOperation.SUBMIT,
                    (callback("disconnect", CtpCallbackType.DISCONNECTED),),
                    expected_project_order_id="project-order-1",
                ),
            ))
            adapter = FangzhengCtpBrokerAdapter(transport, profile())
            establish_ready(adapter)
            composition = RealExecutionComposition(
                path=path, adapter=adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-20260829",
            )
            composition.submit_order(instruction(), submitted_at=NOW)
            composition.consume_adapter_events()

            script = """
import sys
from src.fangzheng_ctp_candidate import FangzhengCtpBrokerAdapter
from src.fangzheng_ctp_fake import ScriptedCtpTransport
from src.real_execution_composition import RealExecutionComposition
from tests.test_fangzheng_ctp_candidate import profile
from tests.test_real_execution_composition import _trading_state
composition = RealExecutionComposition(
    path=sys.argv[1],
    adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
    trading_state=_trading_state(),
    expected_trading_day="20260829",
    session_identity="session-20260829",
)
print(composition.order_for("project-order-1").lifecycle.value)
print(composition.trading_state.order_for("project-order-1").status.value)
"""
            completed = subprocess.run(
                [sys.executable, "-c", script, str(path)],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(
                completed.stdout.strip().splitlines(),
                ["UNKNOWN", "PENDING_SUBMIT"],
            )


if __name__ == "__main__":
    unittest.main()

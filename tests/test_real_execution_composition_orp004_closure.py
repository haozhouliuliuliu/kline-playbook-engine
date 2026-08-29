"""Focused regressions for the final bounded ORP-004 REAL repair."""

from __future__ import annotations

from contextlib import closing
from dataclasses import replace
from datetime import timedelta
from decimal import Decimal
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from src.fangzheng_ctp_candidate import (
    CtpCancelAcknowledgement,
    CtpCallbackType,
    CtpOrderAcknowledgement,
    CtpOrderRecord,
    CtpOrderRejection,
    CtpTradeFill,
    CtpTruthState,
    FangzhengCtpBrokerAdapter,
)
from src.fangzheng_ctp_fake import FakeCtpOperation, FakeCtpStep, ScriptedCtpTransport
from src.contract_semantics import OrderAction, PositionDirection
from src.real_execution_composition import (
    RealExecutionComposition,
    RealOrderLifecycle,
)
from src.runtime_events import BrokerConnectionState, BrokerEvent, BrokerEventType, event_pairs
from src.runtime_ledger import RuntimeLedger
from src.trading_state import OrderStatus, TradingState
from tests.test_fangzheng_ctp_candidate import CONTRACT, instruction, profile
from tests.test_fangzheng_ctp_fake import callback, establish_ready, ready_steps
from tests.test_real_execution_composition import (
    NOW,
    TRADING_DAY,
    _ready_query_steps,
    _trading_state,
)
from tests.runtime_synthetic_fixture import (
    DEFAULT_STARTING_CAPITAL,
    make_accounting,
    make_contract_spec,
)


def _ready_adapter(
    *,
    orders: tuple[CtpOrderRecord, ...] = (),
    trades: tuple[object, ...] = (),
    extra_steps: tuple[FakeCtpStep, ...] = (),
) -> tuple[FangzhengCtpBrokerAdapter, ScriptedCtpTransport]:
    transport = ScriptedCtpTransport(
        _ready_query_steps(orders=orders, trades=trades) + extra_steps
    )
    adapter = FangzhengCtpBrokerAdapter(transport, profile())
    establish_ready(adapter)
    return adapter, transport


def _clean_reconcile(composition: RealExecutionComposition, *, round_id: str = "clean"):
    return composition.reconcile_adapter_truth(
        round_id=round_id,
        requested_at=NOW,
        observed_at=NOW,
        expected_account=composition.adapter.fetch_account_snapshot(),
        expected_positions=(),
    )


def _runtime_state_with_order(
    *,
    client_request_id: str = "request-1",
    concrete_contract_id: str = CONTRACT,
    direction=None,
    action=None,
    requested_quantity: Decimal = Decimal("2"),
    fills: tuple[tuple[Decimal, Decimal], ...] = (),
):
    if concrete_contract_id == CONTRACT:
        state = _trading_state()
    else:
        state = TradingState(
            runtime_id="real-composition-divergent-fixture",
            runtime_version="test-v0.1",
            created_at=NOW,
            starting_capital=DEFAULT_STARTING_CAPITAL,
            contract_specs=(
                make_contract_spec(instrument=CONTRACT),
                make_contract_spec(instrument=concrete_contract_id),
            ),
            accounting=make_accounting(),
            ledger=RuntimeLedger(),
            connection_state=BrokerConnectionState.CONNECTED,
        )
    order_instruction = instruction()
    direction = order_instruction.direction if direction is None else direction
    action = order_instruction.action if action is None else action
    state.apply_broker_event(BrokerEvent(
        event_id="fixture-submit",
        event_type=BrokerEventType.ORDER_SUBMITTED,
        occurred_at=NOW,
        stream_id="fixture-stream",
        sequence=0,
        order_id="project-order-1",
        client_request_id=client_request_id,
        payload=event_pairs(
            concrete_contract_id=concrete_contract_id,
            direction=direction,
            action=action,
            quantity=requested_quantity,
            lifecycle_status=OrderStatus.LIVE,
        ),
    ))
    for index, (quantity, price) in enumerate(fills, start=1):
        state.apply_broker_event(BrokerEvent(
            event_id=f"fixture-fill-{index}",
            event_type=BrokerEventType.ORDER_FILLED,
            occurred_at=NOW + timedelta(seconds=index),
            stream_id="fixture-stream",
            sequence=index,
            order_id="project-order-1",
            client_request_id=client_request_id,
            payload=event_pairs(
                concrete_contract_id=concrete_contract_id,
                direction=direction,
                action=action,
                quantity=quantity,
                price=price,
            ),
        ))
    return state


class CurrentReconciliationProofTests(unittest.TestCase):
    def test_fresh_disconnected_and_ready_without_reconcile_both_block(self) -> None:
        with TemporaryDirectory() as tmp:
            disconnected = RealExecutionComposition(
                path=Path(tmp) / "disconnected.sqlite3",
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-disconnected",
            )
            self.assertFalse(disconnected.new_risk_allowed)
            self.assertIsNone(disconnected.reconciliation_proof)

            adapter, _ = _ready_adapter()
            ready = RealExecutionComposition(
                path=Path(tmp) / "ready.sqlite3",
                adapter=adapter,
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-ready",
            )
            self.assertTrue(adapter.ready)
            self.assertFalse(ready.new_risk_allowed)

    def test_clean_reconcile_establishes_instance_bound_proof_and_restart_drops_it(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "proof.sqlite3"
            adapter, _ = _ready_adapter()
            first = RealExecutionComposition(
                path=path, adapter=adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-proof",
            )
            report = _clean_reconcile(first, round_id="round-1")
            proof = first.reconciliation_proof
            self.assertTrue(report.new_risk_allowed)
            self.assertIsNotNone(proof)
            self.assertEqual(proof.round_id, "round-1")
            self.assertEqual(proof.composition_instance_id, first.composition_instance_id)

            restarted_adapter, _ = _ready_adapter()
            restarted = RealExecutionComposition(
                path=path, adapter=restarted_adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-proof",
            )
            self.assertNotEqual(first.composition_instance_id, restarted.composition_instance_id)
            self.assertIsNone(restarted.reconciliation_proof)
            self.assertFalse(restarted.new_risk_allowed)
            self.assertTrue(_clean_reconcile(restarted, round_id="round-2").new_risk_allowed)

    def test_disconnect_submit_and_lifecycle_callbacks_invalidate_proof(self) -> None:
        scenarios = ("disconnect", "submit", "ack", "fill", "cancel", "reject")
        for scenario in scenarios:
            with self.subTest(scenario=scenario), TemporaryDirectory() as tmp:
                broker_order = CtpOrderRecord(
                    "project-order-1", "request-1", "broker-order-1", CONTRACT,
                    instruction().direction, instruction().action, "LIVE",
                    Decimal("2"), Decimal("0"), NOW,
                )
                submit_callbacks = ()
                query_orders = ()
                if scenario in {"ack", "fill", "cancel", "reject"}:
                    submit_callbacks = (callback(
                        "initial-ack", CtpCallbackType.ORDER_ACKNOWLEDGED,
                        CtpOrderAcknowledgement(
                            "project-order-1", "request-1", "broker-order-1", "cancel-token"
                        ), trading_day=TRADING_DAY,
                    ),)
                    query_orders = (broker_order,)
                adapter, transport = _ready_adapter(
                    orders=query_orders,
                    extra_steps=(FakeCtpStep(
                        FakeCtpOperation.SUBMIT,
                        submit_callbacks,
                        expected_project_order_id="project-order-1",
                    ),),
                )
                composition = RealExecutionComposition(
                    path=Path(tmp) / "events.sqlite3", adapter=adapter,
                    trading_state=_trading_state(), expected_trading_day=TRADING_DAY,
                    session_identity="session-events",
                )
                if scenario in {"ack", "fill", "cancel", "reject"}:
                    composition.submit_order(instruction(), submitted_at=NOW)
                    composition.consume_adapter_events()
                self.assertTrue(_clean_reconcile(composition).new_risk_allowed)

                if scenario == "disconnect":
                    transport.inject_callbacks((callback("disconnect", CtpCallbackType.DISCONNECTED),))
                    composition.consume_adapter_events()
                elif scenario == "submit":
                    composition.submit_order(instruction(), submitted_at=NOW)
                elif scenario == "ack":
                    composition._acknowledge(
                        composition.order_for("project-order-1"),
                        "broker-order-1",
                        NOW,
                        fact_key="late-ack:broker-order-1",
                    )
                elif scenario == "fill":
                    transport.inject_callbacks((callback(
                        "fill", CtpCallbackType.TRADE_FILLED,
                        CtpTradeFill(
                            "project-order-1", "request-1", "broker-order-1", "trade-1",
                            Decimal("1"), Decimal("3500"),
                        ), trading_day=TRADING_DAY,
                    ),))
                    composition.consume_adapter_events()
                else:
                    callback_type = (
                        CtpCallbackType.CANCEL_ACKNOWLEDGED
                        if scenario == "cancel" else CtpCallbackType.ORDER_REJECTED
                    )
                    callback_data = (
                        CtpCancelAcknowledgement(
                            "project-order-1", "request-1", "broker-order-1"
                        )
                        if scenario == "cancel"
                        else CtpOrderRejection(
                            "project-order-1", "request-1", "reject-code", "rejected"
                        )
                    )
                    transport.inject_callbacks((callback(
                        scenario, callback_type, callback_data, trading_day=TRADING_DAY,
                    ),))
                    composition.consume_adapter_events()
                self.assertFalse(composition.new_risk_allowed)
                self.assertIsNone(composition.reconciliation_proof)

    def test_incomplete_query_and_old_trading_day_invalidate_prior_proof(self) -> None:
        with TemporaryDirectory() as tmp:
            adapter, _ = _ready_adapter()
            composition = RealExecutionComposition(
                path=Path(tmp) / "incomplete.sqlite3", adapter=adapter,
                trading_state=_trading_state(), expected_trading_day=TRADING_DAY,
                session_identity="session-incomplete",
            )
            self.assertTrue(_clean_reconcile(composition).new_risk_allowed)
            adapter._truth["trades"] = CtpTruthState.UNKNOWN
            report = _clean_reconcile(composition, round_id="incomplete")
            self.assertFalse(report.new_risk_allowed)
            self.assertIsNone(composition.reconciliation_proof)

            adapter._truth["trades"] = CtpTruthState.KNOWN
            self.assertTrue(_clean_reconcile(composition, round_id="restored").new_risk_allowed)
            adapter._trading_day = "20260828"
            stale = _clean_reconcile(composition, round_id="old-day")
            self.assertFalse(stale.new_risk_allowed)
            self.assertFalse(stale.broker_truth_complete)


class FillDurabilityTests(unittest.TestCase):
    def test_failed_order_aggregate_update_rolls_back_new_fill_fact(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "atomic.sqlite3"
            adapter, transport = _ready_adapter(extra_steps=(FakeCtpStep(
                FakeCtpOperation.SUBMIT,
                expected_project_order_id="project-order-1",
            ),))
            composition = RealExecutionComposition(
                path=path, adapter=adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-atomic",
            )
            composition.submit_order(instruction(), submitted_at=NOW)
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute(
                    """CREATE TRIGGER fail_fill_aggregate BEFORE UPDATE OF filled_quantity
                       ON real_execution_orders
                       WHEN NEW.filled_quantity <> OLD.filled_quantity
                       BEGIN SELECT RAISE(ABORT, 'injected aggregate failure'); END"""
                )
            transport.inject_callbacks((callback(
                "fill-crash-boundary", CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "project-order-1", "request-1", "broker-order-1", "trade-atomic",
                    Decimal("1"), Decimal("3500"),
                ), trading_day=TRADING_DAY,
            ),))
            with self.assertRaisesRegex(sqlite3.IntegrityError, "injected aggregate failure"):
                composition.consume_adapter_events()
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute("DROP TRIGGER fail_fill_aggregate")
                self.assertEqual(connection.execute(
                    "SELECT COUNT(*) FROM real_execution_facts WHERE fact_type='FILL'"
                ).fetchone()[0], 0)
                self.assertEqual(connection.execute(
                    "SELECT filled_quantity FROM real_execution_orders"
                ).fetchone()[0], "0")
            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=_trading_state(), expected_trading_day=TRADING_DAY,
                session_identity="session-atomic",
            )
            self.assertEqual(reopened.order_for("project-order-1").filled_quantity, Decimal("0"))
            self.assertFalse(reopened.new_risk_allowed)

    def test_legacy_split_brain_is_rebuilt_from_canonical_fill_facts(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy.sqlite3"
            adapter, transport = _ready_adapter(extra_steps=(FakeCtpStep(
                FakeCtpOperation.SUBMIT,
                expected_project_order_id="project-order-1",
            ),))
            first = RealExecutionComposition(
                path=path, adapter=adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-legacy",
            )
            first.submit_order(instruction(), submitted_at=NOW)
            transport.inject_callbacks((callback(
                "legacy-fill", CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "project-order-1", "request-1", "broker-order-1", "trade-legacy",
                    Decimal("1"), Decimal("3500"),
                ), trading_day=TRADING_DAY,
            ),))
            first.consume_adapter_events()
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute(
                    """UPDATE real_execution_orders SET lifecycle='OPEN',filled_quantity='0',
                       average_fill_price=NULL"""
                )

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=_trading_state(), expected_trading_day=TRADING_DAY,
                session_identity="session-legacy",
            )
            order = reopened.order_for("project-order-1")
            self.assertIs(order.lifecycle, RealOrderLifecycle.PARTIALLY_FILLED)
            self.assertEqual(order.filled_quantity, Decimal("1"))
            self.assertEqual(order.average_fill_price, Decimal("3500"))
            self.assertEqual(
                reopened.trading_state.position_for(CONTRACT, instruction().direction).quantity,
                Decimal("1"),
            )

    def test_partial_then_second_fill_across_restart_is_exactly_once(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "two-fills.sqlite3"
            adapter, transport = _ready_adapter(extra_steps=(FakeCtpStep(
                FakeCtpOperation.SUBMIT,
                expected_project_order_id="project-order-1",
            ),))
            first = RealExecutionComposition(
                path=path, adapter=adapter, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-two-fills",
            )
            first.submit_order(instruction(), submitted_at=NOW)
            transport.inject_callbacks((callback(
                "fill-one", CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "project-order-1", "request-1", "broker-order-1", "trade-one",
                    Decimal("1"), Decimal("3500"),
                ), trading_day=TRADING_DAY,
            ),))
            first.consume_adapter_events()

            adapter2, transport2 = _ready_adapter()
            second = RealExecutionComposition(
                path=path, adapter=adapter2, trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY, session_identity="session-two-fills",
            )
            transport2.inject_callbacks((callback(
                "fill-two", CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "project-order-1", "request-1", "broker-order-1", "trade-two",
                    Decimal("1"), Decimal("3600"),
                ), trading_day=TRADING_DAY,
            ),))
            second.consume_adapter_events()
            order = second.order_for("project-order-1")
            position = second.trading_state.position_for(CONTRACT, instruction().direction)
            self.assertIs(order.lifecycle, RealOrderLifecycle.FILLED)
            self.assertEqual(order.filled_quantity, Decimal("2"))
            self.assertEqual(order.average_fill_price, Decimal("3550"))
            self.assertEqual(position.quantity, Decimal("2"))
            self.assertEqual(position.average_open_price, Decimal("3550"))

            script = """
import sys
from src.fangzheng_ctp_candidate import FangzhengCtpBrokerAdapter
from src.fangzheng_ctp_fake import ScriptedCtpTransport
from src.real_execution_composition import RealExecutionComposition
from tests.test_fangzheng_ctp_candidate import profile
from tests.test_real_execution_composition import _trading_state
c = RealExecutionComposition(
    path=sys.argv[1], adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
    trading_state=_trading_state(), expected_trading_day='20260829',
    session_identity='session-two-fills')
o = c.order_for('project-order-1')
print(o.lifecycle.value, o.filled_quantity, o.average_fill_price)
print(c.trading_state.positions[0].quantity, c.trading_state.positions[0].average_open_price)
"""
            completed = subprocess.run(
                [sys.executable, "-c", script, str(path)], check=True,
                capture_output=True, text=True,
            )
            self.assertEqual(
                completed.stdout.strip().splitlines(),
                ["FILLED 2 3550", "2 3550"],
            )


class ExistingTradingStateReconciliationTests(unittest.TestCase):
    def _durable_path(self, directory: str, *, filled: bool) -> Path:
        path = Path(directory) / "durable.sqlite3"
        adapter, transport = _ready_adapter(extra_steps=(FakeCtpStep(
            FakeCtpOperation.SUBMIT,
            expected_project_order_id="project-order-1",
        ),))
        composition = RealExecutionComposition(
            path=path, adapter=adapter, trading_state=_trading_state(),
            expected_trading_day=TRADING_DAY, session_identity="session-state-check",
        )
        composition.submit_order(instruction(), submitted_at=NOW)
        if filled:
            transport.inject_callbacks((callback(
                "durable-fill", CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "project-order-1", "request-1", "broker-order-1", "trade-durable",
                    Decimal("2"), Decimal("3500"),
                ), trading_day=TRADING_DAY,
            ),))
            composition.consume_adapter_events()
        return path

    def _reopen(self, path: Path, state):
        return RealExecutionComposition(
            path=path,
            adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
            trading_state=state, expected_trading_day=TRADING_DAY,
            session_identity="session-state-check",
        )

    def test_exact_consistent_existing_state_is_accepted(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "exact.sqlite3"
            adapter, transport = _ready_adapter(extra_steps=(FakeCtpStep(
                FakeCtpOperation.SUBMIT,
                expected_project_order_id="project-order-1",
            ),))
            state = _trading_state()
            first = RealExecutionComposition(
                path=path, adapter=adapter, trading_state=state,
                expected_trading_day=TRADING_DAY, session_identity="session-state-check",
            )
            first.submit_order(instruction(), submitted_at=NOW)
            transport.inject_callbacks((callback(
                "exact-fill", CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "project-order-1", "request-1", "broker-order-1", "trade-exact",
                    Decimal("2"), Decimal("3500"),
                ), trading_day=TRADING_DAY,
            ),))
            first.consume_adapter_events()
            reopened = self._reopen(path, state)
            self.assertNotIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertEqual(reopened.trading_state.orders[0].filled_quantity, Decimal("2"))
            self.assertFalse(reopened.new_risk_allowed)

    def test_same_id_with_wrong_envelope_hard_blocks(self) -> None:
        mutations = {
            "client": {"client_request_id": "different-request"},
            "contract": {"concrete_contract_id": "OTHER.contract"},
            "direction": {"direction": PositionDirection.SHORT},
            "action": {"action": OrderAction.CLOSE},
            "quantity": {"requested_quantity": Decimal("1")},
        }
        for name, arguments in mutations.items():
            with self.subTest(name=name), TemporaryDirectory() as tmp:
                path = self._durable_path(tmp, filled=False)
                state = _runtime_state_with_order(**arguments)
                reopened = self._reopen(path, state)
                self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
                self.assertFalse(reopened.new_risk_allowed)

    def test_filled_quantity_behind_and_ahead_both_hard_block(self) -> None:
        with TemporaryDirectory() as tmp:
            filled_path = self._durable_path(tmp, filled=True)
            behind = self._reopen(filled_path, _runtime_state_with_order())
            self.assertIn("HARD_EXECUTION_INCONSISTENCY", behind.active_blockers())

        with TemporaryDirectory() as tmp:
            open_path = self._durable_path(tmp, filled=False)
            ahead = self._reopen(
                open_path,
                _runtime_state_with_order(fills=((Decimal("2"), Decimal("3500")),)),
            )
            self.assertIn("HARD_EXECUTION_INCONSISTENCY", ahead.active_blockers())

    def test_average_fill_and_position_divergence_hard_block(self) -> None:
        with TemporaryDirectory() as tmp:
            path = self._durable_path(tmp, filled=True)
            wrong_average = _runtime_state_with_order(
                fills=((Decimal("2"), Decimal("3600")),)
            )
            average_result = self._reopen(path, wrong_average)
            self.assertIn("HARD_EXECUTION_INCONSISTENCY", average_result.active_blockers())

        with TemporaryDirectory() as tmp:
            path = self._durable_path(tmp, filled=True)
            stale_position = _runtime_state_with_order(
                fills=((Decimal("2"), Decimal("3500")),)
            )
            key = (CONTRACT, instruction().direction)
            stale_position._positions[key] = replace(
                stale_position._positions[key], quantity=Decimal("1")
            )
            position_result = self._reopen(path, stale_position)
            self.assertIn("HARD_EXECUTION_INCONSISTENCY", position_result.active_blockers())

    def test_fresh_empty_state_still_rehydrates_filled_order(self) -> None:
        with TemporaryDirectory() as tmp:
            path = self._durable_path(tmp, filled=True)
            reopened = self._reopen(path, _trading_state())
            order = reopened.trading_state.order_for("project-order-1")
            self.assertIs(order.status, OrderStatus.FILLED)
            self.assertEqual(order.filled_quantity, Decimal("2"))
            self.assertEqual(reopened.trading_state.positions[0].quantity, Decimal("2"))


if __name__ == "__main__":
    unittest.main()

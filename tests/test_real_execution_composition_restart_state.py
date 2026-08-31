"""Regression coverage for exact REAL composition restart state."""

from __future__ import annotations

from contextlib import closing
from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from src.broker_adapter import BrokerOrderInstruction, BrokerPositionSnapshot, OrderType
from src.contract_semantics import CloseOffset, OrderAction, PositionDirection
from src.fangzheng_ctp_candidate import (
    CtpCallbackType,
    CtpOrderRecord,
    CtpPositionRecord,
    CtpTradeRecord,
    CtpTradeFill,
    CtpTranslationProfile,
    FangzhengCtpBrokerAdapter,
)
from src.fangzheng_ctp_fake import FakeCtpOperation, FakeCtpStep, ScriptedCtpTransport
from src.real_execution_composition import RealExecutionComposition
from src.runtime_events import BrokerEvent, BrokerEventType, event_pairs
from src.trading_state import OrderStatus
from tests.test_fangzheng_ctp_candidate import CONTRACT, instruction, profile
from tests.test_fangzheng_ctp_fake import callback, establish_ready
from tests.test_real_execution_composition import (
    NOW,
    TRADING_DAY,
    _ready_query_steps,
    _trading_state,
)
from tests.test_real_execution_composition_orp004_closure import (
    _ready_adapter,
    _runtime_state_with_order,
)


def _close_profile() -> CtpTranslationProfile:
    return CtpTranslationProfile(
        instruments=((CONTRACT, "opaque-instrument"),),
        sides=((PositionDirection.LONG, OrderAction.CLOSE, "opaque-sell"),),
        offsets=((OrderAction.CLOSE, CloseOffset.CLOSE, "opaque-close"),),
        order_types=((OrderType.LIMIT, "opaque-limit"),),
    )


def _close_instruction(*, quantity: Decimal = Decimal("1")) -> BrokerOrderInstruction:
    return BrokerOrderInstruction(
        client_request_id="close-request-1",
        client_order_id="close-order-1",
        strategy_identity_id="carried-position-close",
        concrete_contract_id=CONTRACT,
        direction=PositionDirection.LONG,
        action=OrderAction.CLOSE,
        close_offset=CloseOffset.CLOSE,
        order_type=OrderType.LIMIT,
        quantity=quantity,
        limit_price=Decimal("3600"),
    )


def _state_with_real_fill_lineage(
    *,
    session_identity: str,
    fills: tuple[tuple[str, Decimal, Decimal], ...],
    occurred_at_by_trade: dict[str, datetime] | None = None,
):
    state = _trading_state()
    stream_id = "real-execution-composition:" + session_identity
    state.apply_broker_event(BrokerEvent(
        event_id="real-submit:project-order-1",
        event_type=BrokerEventType.ORDER_SUBMITTED,
        occurred_at=NOW,
        stream_id=stream_id,
        sequence=0,
        order_id="project-order-1",
        client_request_id="request-1",
        payload=event_pairs(
            concrete_contract_id=CONTRACT,
            direction=instruction().direction,
            action=instruction().action,
            quantity=Decimal("2"),
            lifecycle_status=OrderStatus.PENDING_SUBMIT,
            broker_order_id=None,
            trading_day=TRADING_DAY,
            session_identity=session_identity,
        ),
    ))
    for sequence, (trade_id, quantity, price) in enumerate(fills, start=1):
        state.apply_broker_event(BrokerEvent(
            event_id="real-fill:" + trade_id,
            event_type=BrokerEventType.ORDER_FILLED,
            occurred_at=(occurred_at_by_trade or {}).get(trade_id, NOW),
            stream_id=stream_id,
            sequence=sequence,
            order_id="project-order-1",
            client_request_id="request-1",
            payload=event_pairs(
                broker_order_id="broker-order-1",
                broker_trade_id=trade_id,
                concrete_contract_id=CONTRACT,
                direction=instruction().direction,
                action=instruction().action,
                quantity=quantity,
                price=price,
                trading_day=TRADING_DAY,
                session_identity=session_identity,
            ),
        ))
    return state


def _create_durable_open_fills(
    path: Path,
    *,
    session_identity: str,
    fills: tuple[tuple[str, Decimal, Decimal], ...],
    occurred_at_by_trade: dict[str, datetime] | None = None,
):
    adapter, transport = _ready_adapter(extra_steps=(FakeCtpStep(
        FakeCtpOperation.SUBMIT,
        expected_project_order_id="project-order-1",
    ),))
    state = _trading_state()
    composition = RealExecutionComposition(
        path=path,
        adapter=adapter,
        trading_state=state,
        expected_trading_day=TRADING_DAY,
        session_identity=session_identity,
    )
    composition.submit_order(instruction(), submitted_at=NOW)
    transport.inject_callbacks(tuple(
        replace(
            callback(
                "fill-" + trade_id,
                CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "project-order-1",
                    "request-1",
                    "broker-order-1",
                    trade_id,
                    quantity,
                    price,
                ),
                trading_day=TRADING_DAY,
            ),
            occurred_at=(occurred_at_by_trade or {}).get(trade_id, NOW),
        )
        for trade_id, quantity, price in fills
    ))
    composition.consume_adapter_events()
    return composition, state


def _create_carried_partial_close(path: Path, *, session_identity: str):
    state = _runtime_state_with_order(fills=((Decimal("2"), Decimal("3500")),))
    transport = ScriptedCtpTransport(
        _ready_query_steps()
        + (
            FakeCtpStep(
                FakeCtpOperation.SUBMIT,
                expected_project_order_id="close-order-1",
            ),
        )
    )
    adapter = FangzhengCtpBrokerAdapter(transport, _close_profile())
    establish_ready(adapter)
    composition = RealExecutionComposition(
        path=path,
        adapter=adapter,
        trading_state=state,
        expected_trading_day=TRADING_DAY,
        session_identity=session_identity,
    )
    composition.submit_order(_close_instruction(), submitted_at=NOW)
    transport.inject_callbacks((callback(
        "close-fill",
        CtpCallbackType.TRADE_FILLED,
        CtpTradeFill(
            "close-order-1",
            "close-request-1",
            "broker-close-1",
            "trade-close-1",
            Decimal("1"),
            Decimal("3600"),
        ),
        trading_day=TRADING_DAY,
    ),))
    composition.consume_adapter_events()
    return state


class ExecutionLineageRestartTests(unittest.TestCase):
    def test_equal_aggregate_but_different_fill_lineage_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "lineage.sqlite3"
            adapter, transport = _ready_adapter(extra_steps=(FakeCtpStep(
                FakeCtpOperation.SUBMIT,
                expected_project_order_id="project-order-1",
            ),))
            first = RealExecutionComposition(
                path=path,
                adapter=adapter,
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-lineage",
            )
            first.submit_order(instruction(), submitted_at=NOW)
            transport.inject_callbacks((callback(
                "canonical-fill",
                CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "project-order-1",
                    "request-1",
                    "broker-order-1",
                    "trade-canonical",
                    Decimal("2"),
                    Decimal("3500"),
                ),
                trading_day=TRADING_DAY,
            ),))
            first.consume_adapter_events()

            divergent = _runtime_state_with_order(
                fills=(
                    (Decimal("1"), Decimal("3500")),
                    (Decimal("1"), Decimal("3500")),
                )
            )
            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=divergent,
                expected_trading_day=TRADING_DAY,
                session_identity="session-lineage",
            )

            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertFalse(reopened.new_risk_allowed)

    def test_same_aggregate_with_changed_trade_identity_count_or_prices_fails_closed(self) -> None:
        scenarios = (
            (
                "trade-identity",
                (("trade-canonical", Decimal("2"), Decimal("3500")),),
                (("trade-other", Decimal("2"), Decimal("3500")),),
            ),
            (
                "fill-count",
                (("trade-canonical", Decimal("2"), Decimal("3500")),),
                (
                    ("trade-a", Decimal("1"), Decimal("3500")),
                    ("trade-b", Decimal("1"), Decimal("3500")),
                ),
            ),
            (
                "price-sequence",
                (
                    ("trade-a", Decimal("1"), Decimal("3400")),
                    ("trade-b", Decimal("1"), Decimal("3600")),
                ),
                (
                    ("trade-a", Decimal("1"), Decimal("3500")),
                    ("trade-b", Decimal("1"), Decimal("3500")),
                ),
            ),
        )
        for name, durable_fills, runtime_fills in scenarios:
            with self.subTest(name=name), TemporaryDirectory() as tmp:
                path = Path(tmp) / "lineage-variants.sqlite3"
                _create_durable_open_fills(
                    path,
                    session_identity="session-lineage-variants",
                    fills=durable_fills,
                )
                divergent = _state_with_real_fill_lineage(
                    session_identity="session-lineage-variants",
                    fills=runtime_fills,
                )

                reopened = RealExecutionComposition(
                    path=path,
                    adapter=FangzhengCtpBrokerAdapter(
                        ScriptedCtpTransport(()), profile()
                    ),
                    trading_state=divergent,
                    expected_trading_day=TRADING_DAY,
                    session_identity="session-lineage-variants",
                )

                self.assertIn(
                    "HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers()
                )

    def test_exact_multi_fill_lineage_restarts_and_duplicate_remains_idempotent(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "exact-multi-fill.sqlite3"
            fills = (
                ("trade-a", Decimal("1"), Decimal("3400")),
                ("trade-b", Decimal("1"), Decimal("3600")),
            )
            _, state = _create_durable_open_fills(
                path,
                session_identity="session-exact-multi-fill",
                fills=fills,
            )
            adapter, transport = _ready_adapter()
            reopened = RealExecutionComposition(
                path=path,
                adapter=adapter,
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-exact-multi-fill",
            )
            before_position = state.position_for(CONTRACT, PositionDirection.LONG)
            before_costs = state.account.charged_costs

            transport.inject_callbacks((callback(
                "duplicate-trade-a",
                CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "project-order-1",
                    "request-1",
                    "broker-order-1",
                    "trade-a",
                    Decimal("1"),
                    Decimal("3400"),
                ),
                trading_day=TRADING_DAY,
            ),))
            results = reopened.consume_adapter_events()

            self.assertNotIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertEqual(results, ())
            self.assertEqual(
                state.position_for(CONTRACT, PositionDirection.LONG), before_position
            )
            self.assertEqual(state.account.charged_costs, before_costs)

    def test_same_fills_with_materially_different_occurrence_order_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "lineage-order.sqlite3"
            fills = (
                ("trade-a", Decimal("1"), Decimal("3400")),
                ("trade-b", Decimal("1"), Decimal("3600")),
            )
            _create_durable_open_fills(
                path,
                session_identity="session-lineage-order",
                fills=fills,
                occurred_at_by_trade={
                    "trade-a": NOW + timedelta(seconds=1),
                    "trade-b": NOW + timedelta(seconds=2),
                },
            )
            divergent = _state_with_real_fill_lineage(
                session_identity="session-lineage-order",
                fills=fills,
                occurred_at_by_trade={
                    "trade-a": NOW + timedelta(seconds=2),
                    "trade-b": NOW + timedelta(seconds=1),
                },
            )

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=divergent,
                expected_trading_day=TRADING_DAY,
                session_identity="session-lineage-order",
            )

            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())


class PositionBaselineRestartTests(unittest.TestCase):
    def test_exact_restart_after_closing_carried_position_remains_coherent(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "carried-close.sqlite3"
            state = _runtime_state_with_order(
                fills=((Decimal("2"), Decimal("3500")),)
            )
            transport = ScriptedCtpTransport(
                _ready_query_steps()
                + (
                    FakeCtpStep(
                        FakeCtpOperation.SUBMIT,
                        expected_project_order_id="close-order-1",
                    ),
                )
            )
            adapter = FangzhengCtpBrokerAdapter(transport, _close_profile())
            establish_ready(adapter)
            first = RealExecutionComposition(
                path=path,
                adapter=adapter,
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-carried-close",
            )
            first.submit_order(_close_instruction(), submitted_at=NOW)
            transport.inject_callbacks((callback(
                "close-fill",
                CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "close-order-1",
                    "close-request-1",
                    "broker-close-1",
                    "trade-close-1",
                    Decimal("1"),
                    Decimal("3600"),
                ),
                trading_day=TRADING_DAY,
            ),))
            first.consume_adapter_events()
            self.assertEqual(
                state.position_for(CONTRACT, PositionDirection.LONG).quantity,
                Decimal("1"),
            )
            self.assertEqual(
                state.position_for(CONTRACT, PositionDirection.LONG).average_open_price,
                Decimal("3500"),
            )

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-carried-close",
            )

            self.assertNotIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertFalse(reopened.new_risk_allowed)

    def test_carried_position_partial_then_final_close_across_restart_is_exact(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "carried-close-across-restart.sqlite3"
            state = _runtime_state_with_order(
                fills=((Decimal("2"), Decimal("3500")),)
            )
            first_transport = ScriptedCtpTransport(
                _ready_query_steps()
                + (
                    FakeCtpStep(
                        FakeCtpOperation.SUBMIT,
                        expected_project_order_id="close-order-1",
                    ),
                )
            )
            first_adapter = FangzhengCtpBrokerAdapter(first_transport, _close_profile())
            establish_ready(first_adapter)
            first = RealExecutionComposition(
                path=path,
                adapter=first_adapter,
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-carried-two-closes",
            )
            first.submit_order(
                _close_instruction(quantity=Decimal("2")), submitted_at=NOW
            )
            first_transport.inject_callbacks((callback(
                "close-fill-one",
                CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "close-order-1",
                    "close-request-1",
                    "broker-close-1",
                    "trade-close-1",
                    Decimal("1"),
                    Decimal("3600"),
                ),
                trading_day=TRADING_DAY,
            ),))
            first.consume_adapter_events()

            second_transport = ScriptedCtpTransport(_ready_query_steps())
            second_adapter = FangzhengCtpBrokerAdapter(second_transport, _close_profile())
            establish_ready(second_adapter)
            second = RealExecutionComposition(
                path=path,
                adapter=second_adapter,
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-carried-two-closes",
            )
            self.assertNotIn("HARD_EXECUTION_INCONSISTENCY", second.active_blockers())
            second_transport.inject_callbacks((callback(
                "close-fill-two",
                CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "close-order-1",
                    "close-request-1",
                    "broker-close-1",
                    "trade-close-2",
                    Decimal("1"),
                    Decimal("3650"),
                ),
                trading_day=TRADING_DAY,
            ),))
            second.consume_adapter_events()

            self.assertIsNone(state.position_for(CONTRACT, PositionDirection.LONG))
            final = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-carried-two-closes",
            )
            self.assertNotIn("HARD_EXECUTION_INCONSISTENCY", final.active_blockers())

    def test_position_baseline_quantity_average_or_identity_tampering_fails_closed(self) -> None:
        mutations = (
            ("quantity", "3"),
            ("quantity", "not-a-decimal"),
            ("average_open_price", "3600"),
            ("baseline_identity", "0" * 64),
        )
        for field, value in mutations:
            with self.subTest(field=field, value=value), TemporaryDirectory() as tmp:
                path = Path(tmp) / "baseline-tamper.sqlite3"
                state = _runtime_state_with_order(
                    fills=((Decimal("2"), Decimal("3500")),)
                )
                RealExecutionComposition(
                    path=path,
                    adapter=FangzhengCtpBrokerAdapter(
                        ScriptedCtpTransport(()), profile()
                    ),
                    trading_state=state,
                    expected_trading_day=TRADING_DAY,
                    session_identity="session-baseline-tamper",
                )
                with closing(sqlite3.connect(path)) as connection, connection:
                    if field == "baseline_identity":
                        connection.execute(
                            "UPDATE real_position_baseline SET baseline_identity=?",
                            (value,),
                        )
                    else:
                        raw = connection.execute(
                            "SELECT positions_json FROM real_position_baseline"
                        ).fetchone()[0]
                        positions = json.loads(raw)
                        positions[0][field] = value
                        connection.execute(
                            "UPDATE real_position_baseline SET positions_json=?",
                            (json.dumps(positions, sort_keys=True, separators=(",", ":")),),
                        )

                reopened = RealExecutionComposition(
                    path=path,
                    adapter=FangzhengCtpBrokerAdapter(
                        ScriptedCtpTransport(()), profile()
                    ),
                    trading_state=state,
                    expected_trading_day=TRADING_DAY,
                    session_identity="session-baseline-tamper",
                )

                self.assertIn("POSITION_BASELINE_INVALID", reopened.active_blockers())
                self.assertIn(
                    "HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers()
                )
                self.assertFalse(reopened.new_risk_allowed)

    def test_nonempty_legacy_journal_without_baseline_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy-nonempty.sqlite3"
            adapter, _ = _ready_adapter(extra_steps=(FakeCtpStep(
                FakeCtpOperation.SUBMIT,
                expected_project_order_id="project-order-1",
            ),))
            state = _trading_state()
            first = RealExecutionComposition(
                path=path,
                adapter=adapter,
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-legacy-nonempty",
            )
            first.submit_order(instruction(), submitted_at=NOW)
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute("DELETE FROM real_position_baseline")
                connection.execute(
                    "UPDATE real_execution_meta SET value=? WHERE key='schema_version'",
                    ("KPE_REAL_EXECUTION_COMPOSITION_V0_1",),
                )

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-legacy-nonempty",
            )

            self.assertIn("POSITION_BASELINE_MISSING", reopened.active_blockers())
            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())

    def test_empty_legacy_journal_captures_once_and_restart_cannot_replace_baseline(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "legacy-empty.sqlite3"
            RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-legacy-empty",
            )
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute("DELETE FROM real_position_baseline")
                connection.execute("DROP TABLE real_journal_start_checkpoint")
                connection.execute("DROP TABLE real_execution_ledger_lineage")
                connection.execute("DROP TABLE real_execution_economic_events")
                connection.execute(
                    "UPDATE real_execution_meta SET value=? WHERE key='schema_version'",
                    ("KPE_REAL_EXECUTION_COMPOSITION_V0_1",),
                )

            carried = _runtime_state_with_order(
                fills=((Decimal("2"), Decimal("3500")),)
            )
            migrated = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=carried,
                expected_trading_day=TRADING_DAY,
                session_identity="session-legacy-empty",
            )
            self.assertNotIn("HARD_EXECUTION_INCONSISTENCY", migrated.active_blockers())
            with closing(sqlite3.connect(path)) as connection, connection:
                captured = connection.execute(
                    "SELECT positions_json FROM real_position_baseline"
                ).fetchone()[0]

            divergent = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-legacy-empty",
            )
            with closing(sqlite3.connect(path)) as connection, connection:
                after_restart = connection.execute(
                    "SELECT positions_json FROM real_position_baseline"
                ).fetchone()[0]

            self.assertEqual(after_restart, captured)
            self.assertNotIn(
                "HARD_EXECUTION_INCONSISTENCY", divergent.active_blockers()
            )
            self.assertEqual(
                divergent.trading_state.position_for(
                    CONTRACT, PositionDirection.LONG
                ).quantity,
                Decimal("2"),
            )

    def test_current_empty_journal_missing_baseline_cannot_recapture_from_caller(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "current-empty-missing.sqlite3"
            RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-current-empty-missing",
            )
            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute("DELETE FROM real_position_baseline")

            caller_state = _runtime_state_with_order(
                fills=((Decimal("2"), Decimal("3500")),)
            )
            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=caller_state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-current-empty-missing",
            )
            with closing(sqlite3.connect(path)) as connection:
                baseline_count = connection.execute(
                    "SELECT COUNT(*) FROM real_position_baseline"
                ).fetchone()[0]

            self.assertEqual(baseline_count, 0)
            self.assertIn("POSITION_BASELINE_MISSING", reopened.active_blockers())
            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())

    def test_stale_flat_opposite_or_extra_final_position_fails_closed(self) -> None:
        mutations = ("stale", "flat", "opposite", "extra")
        for mutation in mutations:
            with self.subTest(mutation=mutation), TemporaryDirectory() as tmp:
                path = Path(tmp) / "position-divergence.sqlite3"
                state = _create_carried_partial_close(
                    path, session_identity="session-position-divergence"
                )
                long_key = (CONTRACT, PositionDirection.LONG)
                long_position = state._positions[long_key]
                if mutation == "stale":
                    state._positions[long_key] = replace(
                        long_position, quantity=Decimal("2")
                    )
                elif mutation == "flat":
                    state._positions.pop(long_key)
                elif mutation == "opposite":
                    state._positions.pop(long_key)
                    state._positions[(CONTRACT, PositionDirection.SHORT)] = replace(
                        long_position, direction=PositionDirection.SHORT
                    )
                else:
                    state._positions[(CONTRACT, PositionDirection.SHORT)] = replace(
                        long_position,
                        direction=PositionDirection.SHORT,
                        quantity=Decimal("1"),
                    )

                reopened = RealExecutionComposition(
                    path=path,
                    adapter=FangzhengCtpBrokerAdapter(
                        ScriptedCtpTransport(()), _close_profile()
                    ),
                    trading_state=state,
                    expected_trading_day=TRADING_DAY,
                    session_identity="session-position-divergence",
                )

                self.assertIn(
                    "HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers()
                )

    def test_baseline_scope_cannot_be_reused_for_another_session(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "baseline-scope.sqlite3"
            RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=_trading_state(),
                expected_trading_day=TRADING_DAY,
                session_identity="session-original",
            )

            with self.assertRaisesRegex(
                ValueError, "REAL_EXECUTION_COMPOSITION_BINDING_MISMATCH:session_identity"
            ):
                RealExecutionComposition(
                    path=path,
                    adapter=FangzhengCtpBrokerAdapter(
                        ScriptedCtpTransport(()), profile()
                    ),
                    trading_state=_trading_state(),
                    expected_trading_day=TRADING_DAY,
                    session_identity="session-different",
                )

    def test_complete_broker_reconciliation_accepts_baseline_plus_close_delta(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "baseline-reconcile.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-baseline-reconcile"
            )
            broker_order = CtpOrderRecord(
                "close-order-1",
                "close-request-1",
                "broker-close-1",
                CONTRACT,
                PositionDirection.LONG,
                OrderAction.CLOSE,
                "FILLED",
                Decimal("1"),
                Decimal("1"),
                NOW,
            )
            broker_position = CtpPositionRecord(
                CONTRACT,
                PositionDirection.LONG,
                Decimal("1"),
                Decimal("3500"),
                NOW,
            )
            broker_trade = CtpTradeRecord(
                "trade-close-1",
                "close-order-1",
                "broker-close-1",
                Decimal("1"),
                Decimal("3600"),
                NOW,
            )
            transport = ScriptedCtpTransport(_ready_query_steps(
                orders=(broker_order,),
                trades=(broker_trade,),
                positions=(broker_position,),
            ))
            adapter = FangzhengCtpBrokerAdapter(transport, _close_profile())
            establish_ready(adapter)
            reopened = RealExecutionComposition(
                path=path,
                adapter=adapter,
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-baseline-reconcile",
            )

            report = reopened.reconcile_adapter_truth(
                round_id="baseline-clean",
                requested_at=NOW,
                observed_at=NOW,
                expected_account=adapter.fetch_account_snapshot(),
                expected_positions=(BrokerPositionSnapshot(
                    CONTRACT,
                    PositionDirection.LONG,
                    Decimal("1"),
                    Decimal("3500"),
                    NOW,
                ),),
            )

            self.assertTrue(report.broker_truth_complete)
            self.assertTrue(report.new_risk_allowed)
            self.assertTrue(reopened.new_risk_allowed)

    def test_carried_close_restart_is_coherent_in_fresh_child_process(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "baseline-child.sqlite3"
            _create_carried_partial_close(
                path, session_identity="session-baseline-child"
            )
            script = r'''
import sys
from decimal import Decimal
from src.contract_semantics import OrderAction, PositionDirection
from src.fangzheng_ctp_candidate import FangzhengCtpBrokerAdapter
from src.fangzheng_ctp_fake import ScriptedCtpTransport
from src.real_execution_composition import RealExecutionComposition
from src.runtime_events import BrokerEvent, BrokerEventType, event_pairs
from src.trading_state import OrderStatus
from tests.test_fangzheng_ctp_candidate import CONTRACT
from tests.test_real_execution_composition import NOW, TRADING_DAY
from tests.test_real_execution_composition_orp004_closure import _runtime_state_with_order
from tests.test_real_execution_composition_restart_state import _close_profile

state = _runtime_state_with_order(fills=((Decimal("2"), Decimal("3500")),))
stream = "real-execution-composition:session-baseline-child"
state.apply_broker_event(BrokerEvent(
    event_id="real-submit:close-order-1",
    event_type=BrokerEventType.ORDER_SUBMITTED,
    occurred_at=NOW,
    stream_id=stream,
    sequence=0,
    order_id="close-order-1",
    client_request_id="close-request-1",
    payload=event_pairs(
        concrete_contract_id=CONTRACT,
        direction=PositionDirection.LONG,
        action=OrderAction.CLOSE,
        quantity=Decimal("1"),
        lifecycle_status=OrderStatus.PENDING_SUBMIT,
        broker_order_id=None,
        trading_day=TRADING_DAY,
        session_identity="session-baseline-child",
    ),
))
state.apply_broker_event(BrokerEvent(
    event_id="real-fill:trade-close-1",
    event_type=BrokerEventType.ORDER_FILLED,
    occurred_at=NOW,
    stream_id=stream,
    sequence=1,
    order_id="close-order-1",
    client_request_id="close-request-1",
    payload=event_pairs(
        broker_order_id="broker-close-1",
        broker_trade_id="trade-close-1",
        concrete_contract_id=CONTRACT,
        direction=PositionDirection.LONG,
        action=OrderAction.CLOSE,
        quantity=Decimal("1"),
        price=Decimal("3600"),
        trading_day=TRADING_DAY,
        session_identity="session-baseline-child",
    ),
))
composition = RealExecutionComposition(
    path=sys.argv[1],
    adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), _close_profile()),
    trading_state=state,
    expected_trading_day=TRADING_DAY,
    session_identity="session-baseline-child",
)
position = state.position_for(CONTRACT, PositionDirection.LONG)
print(composition.active_blockers())
print(position.quantity, position.average_open_price)
print(composition.new_risk_allowed)
'''
            completed = subprocess.run(
                [sys.executable, "-c", script, str(path)],
                check=True,
                capture_output=True,
                text=True,
            )

            self.assertEqual(
                completed.stdout.strip().splitlines(),
                ["()", "1 3500", "False"],
            )


if __name__ == "__main__":
    unittest.main()

"""Independent project-brain adversarial revalidation for PR #80.

Audit instrumentation only.  These tests are deliberately outside the repair
worker's production regression file.  They first re-run the two findings from
PR #79 and then probe two adjacent restart-state integrity boundaries that are
not established merely by terminal order/position aggregates.
"""

from __future__ import annotations

from contextlib import closing
from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import sqlite3
from tempfile import TemporaryDirectory
import unittest

from src.contract_semantics import PositionDirection
from src.fangzheng_ctp_candidate import (
    CtpCallbackType,
    CtpTradeFill,
    FangzhengCtpBrokerAdapter,
)
from src.fangzheng_ctp_fake import FakeCtpOperation, FakeCtpStep, ScriptedCtpTransport
from src.real_execution_composition import RealExecutionComposition
from tests.test_fangzheng_ctp_candidate import CONTRACT, instruction, profile
from tests.test_fangzheng_ctp_fake import callback, establish_ready
from tests.test_real_execution_composition import NOW, TRADING_DAY, _ready_query_steps, _trading_state
from tests.test_real_execution_composition_orp004_closure import (
    _ready_adapter,
    _runtime_state_with_order,
)
from tests.test_real_execution_composition_restart_state import (
    _close_instruction,
    _close_profile,
    _create_carried_partial_close,
)


class ProjectBrainPriorFindingRevalidationTests(unittest.TestCase):
    def test_prior_equal_aggregate_different_fill_lineage_now_fails_closed(self) -> None:
        """Exact behavioral reproduction of PB2-REAL-001 from PR #79."""
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
            runtime_order = divergent.order_for("project-order-1")
            durable_order = first.order_for("project-order-1")
            self.assertEqual(runtime_order.filled_quantity, durable_order.filled_quantity)
            self.assertEqual(runtime_order.average_fill_price, durable_order.average_fill_price)

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=divergent,
                expected_trading_day=TRADING_DAY,
                session_identity="session-lineage",
            )
            self.assertIn("HARD_EXECUTION_INCONSISTENCY", reopened.active_blockers())
            self.assertFalse(reopened.new_risk_allowed)

    def test_prior_carried_position_close_now_restarts_without_self_invalidating(self) -> None:
        """Behavioral reproduction of PB2-REAL-002 from PR #79."""
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


class ProjectBrainAdjacentRestartIntegrityTests(unittest.TestCase):
    def test_missing_schema_and_baseline_on_nonempty_journal_must_not_recapture_caller_state(self) -> None:
        """A damaged nonempty journal must not become a new journal by losing metadata.

        The journal already owns a pending current-session order and originally
        captured LONG 2 as its start baseline.  Removing both schema metadata and
        the baseline simulates durable-state loss/tamper.  A divergent caller
        position must not be silently recaptured as the new baseline.
        """
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "missing-schema-baseline.sqlite3"
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
                session_identity="session-missing-schema-baseline",
            )
            first.submit_order(_close_instruction(), submitted_at=NOW)

            # Make the supplied mutable state disagree with the baseline that
            # was durably captured at journal creation, while keeping the
            # current-journal order/event lineage intact.
            key = (CONTRACT, PositionDirection.LONG)
            original = state._positions[key]
            state._positions[key] = replace(original, quantity=Decimal("3"))

            with closing(sqlite3.connect(path)) as connection, connection:
                connection.execute("DELETE FROM real_position_baseline")
                connection.execute(
                    "DELETE FROM real_execution_meta WHERE key='schema_version'"
                )
                order_count = connection.execute(
                    "SELECT COUNT(*) FROM real_execution_orders"
                ).fetchone()[0]
            self.assertGreater(order_count, 0)

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-missing-schema-baseline",
            )

            self.assertIn(
                "HARD_EXECUTION_INCONSISTENCY",
                reopened.active_blockers(),
                "nonempty journal silently recaptured a divergent caller position after schema+baseline loss",
            )
            self.assertFalse(reopened.new_risk_allowed)

    def test_exact_fill_lineage_with_tampered_position_economics_must_fail_closed(self) -> None:
        """Exact qty/average is not exact TradingState economic continuity.

        A close fill changes realized PnL, margin/mark economics and account
        projections.  Altering a position economic field while preserving exact
        order lineage, quantity and average must not be accepted as an exact
        restart state.
        """
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "position-economics.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-position-economics"
            )
            key = (CONTRACT, PositionDirection.LONG)
            exact = state._positions[key]
            state._positions[key] = replace(
                exact,
                realized_pnl=exact.realized_pnl + Decimal("1"),
            )
            # Quantity/average and the complete current-journal fill event log
            # remain untouched; only economic state is divergent.
            self.assertEqual(state._positions[key].quantity, exact.quantity)
            self.assertEqual(
                state._positions[key].average_open_price,
                exact.average_open_price,
            )

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-position-economics",
            )

            self.assertIn(
                "HARD_EXECUTION_INCONSISTENCY",
                reopened.active_blockers(),
                "restart accepted exact fill lineage and terminal qty/average despite divergent position economics",
            )
            self.assertFalse(reopened.new_risk_allowed)


if __name__ == "__main__":
    unittest.main()

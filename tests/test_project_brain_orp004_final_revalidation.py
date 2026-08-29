"""Independent project-brain adversarial revalidation for PR #78.

Audit instrumentation only.  This file intentionally checks a state-equivalence
case not authored by the repair worker: equal order/position aggregates with a
different durable fill lineage must not be accepted as an exact restart state.
"""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.fangzheng_ctp_candidate import (
    CtpCallbackType,
    CtpTradeFill,
    FangzhengCtpBrokerAdapter,
)
from src.fangzheng_ctp_fake import FakeCtpOperation, FakeCtpStep, ScriptedCtpTransport
from src.real_execution_composition import RealExecutionComposition
from tests.test_fangzheng_ctp_candidate import instruction, profile
from tests.test_fangzheng_ctp_fake import callback
from tests.test_real_execution_composition import NOW, TRADING_DAY, _trading_state
from tests.test_real_execution_composition_orp004_closure import (
    _ready_adapter,
    _runtime_state_with_order,
)


class ProjectBrainOrp004FinalRevalidationTests(unittest.TestCase):
    def test_equal_aggregate_but_different_fill_lineage_must_fail_closed(self) -> None:
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

            # Same final order and position aggregates, but produced by two
            # different fill events instead of the one canonical durable fill.
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
            self.assertEqual(
                divergent.position_for(instruction().concrete_contract_id, instruction().direction).quantity,
                Decimal("2"),
            )

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), profile()),
                trading_state=divergent,
                expected_trading_day=TRADING_DAY,
                session_identity="session-lineage",
            )

            self.assertIn(
                "HARD_EXECUTION_INCONSISTENCY",
                reopened.active_blockers(),
                "restart accepted an aggregate-equal TradingState whose fill lineage differs from durable REAL facts",
            )
            self.assertFalse(reopened.new_risk_allowed)


if __name__ == "__main__":
    unittest.main()

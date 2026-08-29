from __future__ import annotations

from dataclasses import replace
import unittest

from src.real_reconciliation import QueryCompleteness
from src.real_runtime_recovery import RecoveredOrderState, recover_real_runtime
from tests.test_real_reconciliation import (
    TRADING_DAY,
    broker_order,
    complete_query,
    local_order,
    local_state,
    position,
)


class RealRuntimeRecoveryTests(unittest.TestCase):
    def test_submit_disconnect_restart_query_open_uses_broker_truth(self) -> None:
        recovery = recover_real_runtime(
            local_state(orders=(local_order(),)),
            complete_query(orders=(broker_order(status="LIVE"),)),
            expected_trading_day=TRADING_DAY,
        )

        self.assertTrue(recovery.broker_truth_complete)
        self.assertTrue(recovery.new_risk_allowed)
        self.assertEqual(RecoveredOrderState.OPEN, recovery.orders[0].state)
        self.assertEqual("broker-order-1", recovery.orders[0].broker_order_id)

    def test_submit_disconnect_restart_query_filled_uses_broker_truth(self) -> None:
        recovery = recover_real_runtime(
            local_state(orders=(local_order(),)),
            complete_query(
                positions=(position("2"),),
                orders=(broker_order(status="FILLED", filled="2"),),
            ),
            expected_trading_day=TRADING_DAY,
        )

        self.assertEqual(RecoveredOrderState.FILLED, recovery.orders[0].state)
        self.assertEqual("2", str(recovery.orders[0].filled_quantity))
        self.assertTrue(recovery.new_risk_allowed)
        self.assertEqual((), recovery.reconciliation.external_mutations)

    def test_incomplete_restart_query_preserves_unknown_and_blocks_new_risk(self) -> None:
        incomplete = replace(
            complete_query(orders=(broker_order(status="LIVE"),)),
            order_status=QueryCompleteness.INCOMPLETE,
        )

        recovery = recover_real_runtime(
            local_state(orders=(local_order(),)),
            incomplete,
            expected_trading_day=TRADING_DAY,
        )

        self.assertFalse(recovery.broker_truth_complete)
        self.assertFalse(recovery.new_risk_allowed)
        self.assertEqual(RecoveredOrderState.UNKNOWN, recovery.orders[0].state)
        self.assertIn("ORDER_QUERY_INCOMPLETE", recovery.blockers)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import unittest

from src.broker_adapter import BrokerAccountSnapshot, BrokerPositionSnapshot
from src.contract_semantics import OrderAction, PositionDirection
from src.real_reconciliation import (
    QueryCompleteness,
    RealBrokerOrder,
    RealBrokerQueryRound,
    RealLocalExecutionState,
    RealLocalOrder,
    reconcile_real_runtime,
)


NOW = datetime(2026, 8, 29, 1, 2, tzinfo=timezone.utc)
TRADING_DAY = "20260829"
CONTRACT = "SHFE.rb2601"


def account(cash: str = "100000") -> BrokerAccountSnapshot:
    return BrokerAccountSnapshot(
        account_id="account-opaque",
        snapshot_at=NOW,
        cash_balance=Decimal(cash),
        reserved_margin=Decimal("0"),
        charged_costs=Decimal("0"),
        realized_pnl=Decimal("0"),
        unrealized_pnl=Decimal("0"),
        currency="CNY",
    )


def local_state(*, orders: tuple[RealLocalOrder, ...] = (), positions=()) -> RealLocalExecutionState:
    return RealLocalExecutionState(
        trading_day=TRADING_DAY,
        expected_account=account(),
        expected_positions=tuple(positions),
        project_orders=orders,
    )


def local_order(*, broker_order_id: str | None = None) -> RealLocalOrder:
    return RealLocalOrder(
        project_order_id="project-order-1",
        client_request_id="request-1",
        broker_order_id=broker_order_id,
        concrete_contract_id=CONTRACT,
        direction=PositionDirection.LONG,
        action=OrderAction.OPEN,
        requested_quantity=Decimal("2"),
    )


def broker_order(
    *,
    broker_order_id: str = "broker-order-1",
    project_order_id: str | None = "project-order-1",
    client_request_id: str | None = "request-1",
    status: str = "LIVE",
    filled: str = "0",
) -> RealBrokerOrder:
    return RealBrokerOrder(
        broker_order_id=broker_order_id,
        project_order_id=project_order_id,
        client_request_id=client_request_id,
        concrete_contract_id=CONTRACT,
        direction=PositionDirection.LONG,
        action=OrderAction.OPEN,
        status=status,
        requested_quantity=Decimal("2"),
        filled_quantity=Decimal(filled),
        snapshot_at=NOW,
    )


def complete_query(*, positions=(), orders=(), broker_account=None) -> RealBrokerQueryRound:
    return RealBrokerQueryRound(
        round_id="round-complete",
        trading_day=TRADING_DAY,
        requested_at=NOW,
        observed_at=NOW,
        account_status=QueryCompleteness.COMPLETE,
        position_status=QueryCompleteness.COMPLETE,
        order_status=QueryCompleteness.COMPLETE,
        account=broker_account or account(),
        positions=tuple(positions),
        orders=tuple(orders),
    )


def position(quantity: str, price: str = "3500") -> BrokerPositionSnapshot:
    return BrokerPositionSnapshot(
        concrete_contract_id=CONTRACT,
        direction=PositionDirection.LONG,
        quantity=Decimal(quantity),
        average_price=Decimal(price),
        snapshot_at=NOW,
    )


class RealReconciliationTests(unittest.TestCase):
    def test_incomplete_query_round_never_establishes_broker_truth(self) -> None:
        query_round = RealBrokerQueryRound(
            round_id="round-1",
            trading_day=TRADING_DAY,
            requested_at=NOW,
            observed_at=NOW,
            account_status=QueryCompleteness.COMPLETE,
            position_status=QueryCompleteness.INCOMPLETE,
            order_status=QueryCompleteness.COMPLETE,
            account=account(),
            positions=(),
            orders=(),
        )

        report = reconcile_real_runtime(local_state(), query_round, expected_trading_day=TRADING_DAY)

        self.assertFalse(report.broker_truth_complete)
        self.assertFalse(report.new_risk_allowed)
        self.assertIn("POSITION_QUERY_INCOMPLETE", report.blockers)
        self.assertEqual((), report.external_mutations)

    def test_each_noncomplete_query_state_remains_distinct_and_fail_closed(self) -> None:
        for status in (
            QueryCompleteness.INCOMPLETE,
            QueryCompleteness.STALE,
            QueryCompleteness.FAILED,
            QueryCompleteness.UNKNOWN,
        ):
            with self.subTest(status=status.value):
                query_round = RealBrokerQueryRound(
                    round_id=f"round-{status.value.lower()}",
                    trading_day=TRADING_DAY,
                    requested_at=NOW,
                    observed_at=NOW,
                    account_status=status,
                    position_status=QueryCompleteness.COMPLETE,
                    order_status=QueryCompleteness.COMPLETE,
                    account=account(),
                    positions=(),
                    orders=(),
                )
                report = reconcile_real_runtime(
                    local_state(), query_round, expected_trading_day=TRADING_DAY,
                )
                self.assertFalse(report.new_risk_allowed)
                self.assertIn(f"ACCOUNT_QUERY_{status.value}", report.blockers)

    def test_old_trading_day_query_cannot_establish_current_truth(self) -> None:
        old_round = RealBrokerQueryRound(
            round_id="old-round",
            trading_day="20260828",
            requested_at=NOW,
            observed_at=NOW,
            account_status=QueryCompleteness.COMPLETE,
            position_status=QueryCompleteness.COMPLETE,
            order_status=QueryCompleteness.COMPLETE,
            account=account(),
            positions=(),
            orders=(),
        )

        report = reconcile_real_runtime(
            local_state(), old_round, expected_trading_day=TRADING_DAY,
        )

        self.assertFalse(report.broker_truth_complete)
        self.assertIn("BROKER_QUERY_TRADING_DAY_MISMATCH", report.blockers)

    def test_complete_query_resolves_uncertain_project_order_from_broker_truth(self) -> None:
        report = reconcile_real_runtime(
            local_state(orders=(local_order(),)),
            complete_query(orders=(broker_order(status="LIVE"),)),
            expected_trading_day=TRADING_DAY,
        )

        self.assertTrue(report.broker_truth_complete)
        self.assertTrue(report.new_risk_allowed)
        self.assertEqual("project-order-1", report.order_resolutions[0].project_order_id)
        self.assertEqual("broker-order-1", report.order_resolutions[0].broker_order.broker_order_id)
        self.assertEqual("LIVE", report.order_resolutions[0].status)

    def test_unknown_broker_order_is_classified_as_external_mutation(self) -> None:
        external_order = broker_order(
            broker_order_id="manual-broker-order",
            project_order_id=None,
            client_request_id=None,
        )

        report = reconcile_real_runtime(
            local_state(),
            complete_query(orders=(external_order,)),
            expected_trading_day=TRADING_DAY,
        )

        self.assertFalse(report.new_risk_allowed)
        self.assertEqual("EXTERNAL_ORDER", report.external_mutations[0].kind.value)
        self.assertEqual("manual-broker-order", report.external_mutations[0].subject_id)

    def test_broker_position_reduction_is_external_and_blocks_new_risk(self) -> None:
        report = reconcile_real_runtime(
            local_state(positions=(position("2"),)),
            complete_query(positions=(position("1"),)),
            expected_trading_day=TRADING_DAY,
        )

        self.assertFalse(report.new_risk_allowed)
        self.assertEqual("POSITION_REDUCED", report.external_mutations[0].kind.value)
        self.assertEqual(f"{CONTRACT}:LONG", report.external_mutations[0].subject_id)

    def test_broker_position_not_represented_locally_is_external(self) -> None:
        report = reconcile_real_runtime(
            local_state(),
            complete_query(positions=(position("1"),)),
            expected_trading_day=TRADING_DAY,
        )

        self.assertFalse(report.new_risk_allowed)
        self.assertEqual("POSITION_APPEARED", report.external_mutations[0].kind.value)

    def test_local_known_order_missing_from_complete_broker_query_remains_unknown(self) -> None:
        report = reconcile_real_runtime(
            local_state(orders=(local_order(broker_order_id="broker-order-1"),)),
            complete_query(),
            expected_trading_day=TRADING_DAY,
        )

        self.assertFalse(report.new_risk_allowed)
        self.assertEqual("LOCAL_ORDER_MISSING", report.external_mutations[0].kind.value)
        self.assertEqual("UNKNOWN", report.order_resolutions[0].status)

    def test_filled_project_order_conflicting_with_broker_position_blocks_recovery(self) -> None:
        report = reconcile_real_runtime(
            local_state(orders=(local_order(),)),
            complete_query(orders=(broker_order(status="FILLED", filled="2"),)),
            expected_trading_day=TRADING_DAY,
        )

        self.assertFalse(report.new_risk_allowed)
        self.assertTrue(any(
            item.kind.value == "PROJECT_ORDER_POSITION_CONFLICT"
            for item in report.external_mutations
        ))

    def test_unexplained_account_change_is_typed_and_not_silently_absorbed(self) -> None:
        report = reconcile_real_runtime(
            local_state(),
            complete_query(broker_account=account("99999")),
            expected_trading_day=TRADING_DAY,
        )

        self.assertFalse(report.new_risk_allowed)
        self.assertEqual("ACCOUNT_STATE_CHANGED", report.external_mutations[0].kind.value)
        self.assertIn("cash_balance", report.external_mutations[0].detail)


if __name__ == "__main__":
    unittest.main()

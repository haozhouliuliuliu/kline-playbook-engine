"""Fail-closed REAL restart/reconnect recovery primitives.

Recovery is driven only by one broker query round that has already passed the
REAL reconciliation checks.  Reconnect by itself is never treated as restored
truth, and a missing or incomplete broker fact preserves ``UNKNOWN``.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from src.real_reconciliation import (
    RealBrokerQueryRound,
    RealLocalExecutionState,
    RealReconciliationReport,
    reconcile_real_runtime,
)


class RecoveredOrderState(str, Enum):
    UNKNOWN = "UNKNOWN"
    OPEN = "OPEN"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


_BROKER_STATUS_TO_RECOVERY = {
    "LIVE": RecoveredOrderState.OPEN,
    "PARTIALLY_FILLED": RecoveredOrderState.PARTIALLY_FILLED,
    "FILLED": RecoveredOrderState.FILLED,
    "CANCELLED": RecoveredOrderState.CANCELLED,
    "REJECTED": RecoveredOrderState.REJECTED,
}


@dataclass(frozen=True)
class RecoveredRealOrder:
    project_order_id: str
    broker_order_id: str | None
    state: RecoveredOrderState
    filled_quantity: Decimal | None

    def __post_init__(self) -> None:
        if not isinstance(self.project_order_id, str) or not self.project_order_id.strip():
            raise ValueError("recovered order requires project order id")
        if self.broker_order_id is not None and (
            not isinstance(self.broker_order_id, str) or not self.broker_order_id.strip()
        ):
            raise ValueError("recovered broker order id must be non-empty")
        if not isinstance(self.state, RecoveredOrderState):
            raise ValueError("recovered order state must be explicit")
        if self.filled_quantity is not None and (
            type(self.filled_quantity) is not Decimal
            or not self.filled_quantity.is_finite()
            or self.filled_quantity < 0
        ):
            raise ValueError("recovered fill quantity must be non-negative finite Decimal")


@dataclass(frozen=True)
class RealRuntimeRecoveryReport:
    reconciliation: RealReconciliationReport
    orders: tuple[RecoveredRealOrder, ...]
    broker_truth_complete: bool
    new_risk_allowed: bool
    blockers: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.reconciliation, RealReconciliationReport):
            raise ValueError("REAL recovery requires reconciliation evidence")
        if not isinstance(self.orders, tuple) or any(
            not isinstance(item, RecoveredRealOrder) for item in self.orders
        ):
            raise ValueError("REAL recovery orders must be RecoveredRealOrder values")
        if type(self.broker_truth_complete) is not bool or type(self.new_risk_allowed) is not bool:
            raise ValueError("REAL recovery flags must be bool")
        if self.blockers != tuple(sorted(set(self.blockers))):
            raise ValueError("REAL recovery blockers must be sorted and unique")
        if self.broker_truth_complete != self.reconciliation.broker_truth_complete:
            raise ValueError("REAL recovery completeness must match reconciliation")
        if self.new_risk_allowed != (
            self.reconciliation.new_risk_allowed
            and not self.blockers
            and all(item.state is not RecoveredOrderState.UNKNOWN for item in self.orders)
        ):
            raise ValueError("REAL recovery new-risk flag must fail closed on UNKNOWN")


def recover_real_runtime(
    local_state: RealLocalExecutionState,
    query_round: RealBrokerQueryRound,
    *,
    expected_trading_day: str,
) -> RealRuntimeRecoveryReport:
    """Resolve persisted project orders from explicit broker query truth."""
    reconciliation = reconcile_real_runtime(
        local_state,
        query_round,
        expected_trading_day=expected_trading_day,
    )
    recovered_orders = []
    blockers = list(reconciliation.blockers)
    for resolution in reconciliation.order_resolutions:
        broker_order = resolution.broker_order
        state = _BROKER_STATUS_TO_RECOVERY.get(resolution.status, RecoveredOrderState.UNKNOWN)
        if broker_order is None:
            recovered = RecoveredRealOrder(
                project_order_id=resolution.project_order_id,
                broker_order_id=None,
                state=RecoveredOrderState.UNKNOWN,
                filled_quantity=None,
            )
        else:
            recovered = RecoveredRealOrder(
                project_order_id=resolution.project_order_id,
                broker_order_id=broker_order.broker_order_id,
                state=state,
                filled_quantity=broker_order.filled_quantity,
            )
        if recovered.state is RecoveredOrderState.UNKNOWN:
            blockers.append(f"ORDER_RECOVERY_UNKNOWN:{recovered.project_order_id}")
        recovered_orders.append(recovered)

    sorted_orders = tuple(sorted(recovered_orders, key=lambda item: item.project_order_id))
    sorted_blockers = tuple(sorted(set(blockers)))
    return RealRuntimeRecoveryReport(
        reconciliation=reconciliation,
        orders=sorted_orders,
        broker_truth_complete=reconciliation.broker_truth_complete,
        new_risk_allowed=reconciliation.new_risk_allowed and not sorted_blockers and all(
            item.state is not RecoveredOrderState.UNKNOWN for item in sorted_orders
        ),
        blockers=sorted_blockers,
    )

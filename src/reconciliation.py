"""Deterministic reconciliation for the Shadow Runtime Foundation.

Skeleton v1.0 §5: broker/exchange facts override local inference, and the
runtime must rebuild state from persistent facts plus broker reconciliation.
This module compares the local authoritative ``TradingState`` against a broker
snapshot (account / positions / orders) and FAILS CLOSED on any mismatch: the
report exposes deterministic mismatch reasons and ``ok`` is only true when every
compared fact agrees exactly (Decimal equality).

No real broker, no network, no candidate outcome, no real money.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
import json
from typing import Any, Iterable

from src.broker_adapter import (
    BrokerAccountSnapshot,
    BrokerOrderSnapshot,
    BrokerPositionSnapshot,
)
from src.contract_semantics import PositionDirection
from src.trading_state import PositionState, RuntimeOrderState, TradingState

RECONCILIATION_SCHEMA_VERSION = "shadow-runtime-reconciliation-v0.1"


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _position_key(item: PositionState | BrokerPositionSnapshot) -> tuple[str, str]:
    return (item.concrete_contract_id, item.direction.value)


@dataclass(frozen=True)
class ReconciliationReport:
    reconciled_at: datetime
    account_match: bool
    position_match: bool
    order_match: bool
    mismatches: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.reconciled_at.tzinfo is None:
            raise ValueError("reconciliation timestamp must be timezone-aware")
        for value, name in (
            (self.account_match, "account match"),
            (self.position_match, "position match"),
            (self.order_match, "order match"),
        ):
            if type(value) is not bool:
                raise ValueError(f"reconciliation {name} must be a bool")
        if not isinstance(self.mismatches, tuple):
            raise ValueError("reconciliation mismatches must be a tuple")
        if self.mismatches != tuple(sorted(set(self.mismatches))):
            raise ValueError("reconciliation mismatches must be sorted and unique")

    @property
    def ok(self) -> bool:
        """Fail closed: only true when every compared fact agrees."""
        return self.account_match and self.position_match and self.order_match and not self.mismatches

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "reconciled_at": self.reconciled_at.isoformat(),
                "account_match": self.account_match,
                "position_match": self.position_match,
                "order_match": self.order_match,
                "mismatches": self.mismatches,
            }
        )


def reconcile_runtime(
    state: TradingState,
    broker_account: BrokerAccountSnapshot,
    broker_positions: Iterable[BrokerPositionSnapshot],
    broker_orders: Iterable[BrokerOrderSnapshot],
    reconciled_at: datetime,
) -> ReconciliationReport:
    """Compare local ``TradingState`` against a broker snapshot; fail closed."""
    if not isinstance(state, TradingState):
        raise ValueError("reconciliation requires a TradingState")
    if not isinstance(broker_account, BrokerAccountSnapshot):
        raise ValueError("reconciliation requires a BrokerAccountSnapshot")
    if reconciled_at.tzinfo is None:
        raise ValueError("reconciliation timestamp must be timezone-aware")

    mismatches: list[str] = []

    # -- account ---------------------------------------------------------------
    local_account = state.account
    account_checks = (
        ("ACCOUNT_CASH_MISMATCH", local_account.cash_balance, broker_account.cash_balance),
        ("ACCOUNT_RESERVED_MARGIN_MISMATCH", local_account.reserved_margin, broker_account.reserved_margin),
        ("ACCOUNT_REALIZED_PNL_MISMATCH", local_account.realized_pnl, broker_account.realized_pnl),
        ("ACCOUNT_UNREALIZED_PNL_MISMATCH", local_account.unrealized_pnl, broker_account.unrealized_pnl),
        ("ACCOUNT_CHARGED_COSTS_MISMATCH", local_account.charged_costs, broker_account.charged_costs),
    )
    account_match = True
    for reason, local, broker in account_checks:
        if local != broker:
            account_match = False
            mismatches.append(reason)

    # -- positions -------------------------------------------------------------
    local_positions = {
        _position_key(item): (item.quantity, item.average_open_price)
        for item in state.positions
    }
    broker_position_list = tuple(broker_positions)
    if any(not isinstance(item, BrokerPositionSnapshot) for item in broker_position_list):
        raise ValueError("broker positions must be BrokerPositionSnapshot values")
    broker_positions_map = {
        _position_key(item): (item.quantity, item.average_price) for item in broker_position_list
    }
    position_match = True
    for key in sorted(set(local_positions) | set(broker_positions_map)):
        local_value = local_positions.get(key)
        broker_value = broker_positions_map.get(key)
        if local_value is None:
            position_match = False
            mismatches.append(f"POSITION_UNKNOWN_BROKER:{key[0]}:{key[1]}")
        elif broker_value is None:
            position_match = False
            mismatches.append(f"POSITION_UNKNOWN_LOCAL:{key[0]}:{key[1]}")
        elif local_value != broker_value:
            position_match = False
            if local_value[0] != broker_value[0]:
                mismatches.append(f"POSITION_QUANTITY_MISMATCH:{key[0]}:{key[1]}")
            if local_value[1] != broker_value[1]:
                mismatches.append(f"POSITION_AVERAGE_PRICE_MISMATCH:{key[0]}:{key[1]}")

    # -- orders ----------------------------------------------------------------
    local_orders = {item.order_id: item for item in state.orders}
    broker_order_list = tuple(broker_orders)
    if any(not isinstance(item, BrokerOrderSnapshot) for item in broker_order_list):
        raise ValueError("broker orders must be BrokerOrderSnapshot values")
    broker_orders_map = {item.order_id: item for item in broker_order_list}
    order_match = True
    for order_id in sorted(set(local_orders) | set(broker_orders_map)):
        local_order = local_orders.get(order_id)
        broker_order = broker_orders_map.get(order_id)
        if local_order is None:
            order_match = False
            mismatches.append(f"ORDER_UNKNOWN_LOCAL:{order_id}")
        elif broker_order is None:
            order_match = False
            mismatches.append(f"ORDER_UNKNOWN_BROKER:{order_id}")
        else:
            if local_order.status.value != broker_order.status:
                order_match = False
                mismatches.append(f"ORDER_STATUS_MISMATCH:{order_id}")
            if local_order.filled_quantity != broker_order.filled_quantity:
                order_match = False
                mismatches.append(f"ORDER_FILLED_QUANTITY_MISMATCH:{order_id}")
            if local_order.requested_quantity != broker_order.requested_quantity:
                order_match = False
                mismatches.append(f"ORDER_REQUESTED_QUANTITY_MISMATCH:{order_id}")

    return ReconciliationReport(
        reconciled_at=reconciled_at,
        account_match=account_match,
        position_match=position_match,
        order_match=order_match,
        mismatches=tuple(sorted(set(mismatches))),
    )


def position_map(positions: Iterable[PositionState]) -> tuple[tuple[str, str, str, str], ...]:
    """Deterministic canonical position projection (contract, direction, qty, avg)."""
    return tuple(
        (item.concrete_contract_id, item.direction.value, str(item.quantity), str(item.average_open_price))
        for item in sorted(positions, key=lambda value: (value.concrete_contract_id, value.direction.value))
    )

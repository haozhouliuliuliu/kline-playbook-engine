"""Outcome-independent REAL broker-truth reconciliation primitives.

This module performs no broker connection and mutates no local execution
state.  It accepts one explicitly classified broker query round and compares
it with project-owned expectations.  Partial, stale, failed, unknown or
cross-trading-day input never becomes authoritative completion.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

from src.broker_adapter import BrokerAccountSnapshot, BrokerPositionSnapshot
from src.contract_semantics import OrderAction, PositionDirection


class QueryCompleteness(str, Enum):
    COMPLETE = "COMPLETE"
    INCOMPLETE = "INCOMPLETE"
    STALE = "STALE"
    FAILED = "FAILED"
    UNKNOWN = "UNKNOWN"


class ExternalMutationKind(str, Enum):
    EXTERNAL_ORDER = "EXTERNAL_ORDER"
    LOCAL_ORDER_MISSING = "LOCAL_ORDER_MISSING"
    ORDER_IDENTITY_CONFLICT = "ORDER_IDENTITY_CONFLICT"
    POSITION_APPEARED = "POSITION_APPEARED"
    POSITION_INCREASED = "POSITION_INCREASED"
    POSITION_REDUCED = "POSITION_REDUCED"
    POSITION_CLOSED = "POSITION_CLOSED"
    POSITION_PRICE_CHANGED = "POSITION_PRICE_CHANGED"
    PROJECT_ORDER_POSITION_CONFLICT = "PROJECT_ORDER_POSITION_CONFLICT"
    ACCOUNT_STATE_CHANGED = "ACCOUNT_STATE_CHANGED"


def _required_text(value: str, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _validate_trading_day(value: str) -> None:
    if not isinstance(value, str) or len(value) != 8 or not value.isdigit():
        raise ValueError("trading day must use YYYYMMDD")


def _positive_decimal(value: Decimal, name: str) -> None:
    if type(value) is not Decimal or not value.is_finite() or value <= 0:
        raise ValueError(f"{name} must be a positive finite Decimal")


@dataclass(frozen=True)
class RealBrokerOrder:
    """Broker order fact with project and broker identities kept separate."""

    broker_order_id: str
    project_order_id: str | None
    client_request_id: str | None
    concrete_contract_id: str
    direction: PositionDirection
    action: OrderAction
    status: str
    requested_quantity: Decimal
    filled_quantity: Decimal
    snapshot_at: datetime

    def __post_init__(self) -> None:
        for value, name in (
            (self.broker_order_id, "broker order id"),
            (self.concrete_contract_id, "contract id"),
            (self.status, "broker order status"),
        ):
            _required_text(value, name)
        for value, name in (
            (self.project_order_id, "project order id"),
            (self.client_request_id, "client request id"),
        ):
            if value is not None:
                _required_text(value, name)
        if not isinstance(self.direction, PositionDirection) or not isinstance(self.action, OrderAction):
            raise ValueError("broker order requires explicit direction and action")
        _positive_decimal(self.requested_quantity, "broker requested quantity")
        if (
            type(self.filled_quantity) is not Decimal
            or not self.filled_quantity.is_finite()
            or self.filled_quantity < 0
            or self.filled_quantity > self.requested_quantity
        ):
            raise ValueError("broker filled quantity must be finite and within requested quantity")
        if not isinstance(self.snapshot_at, datetime) or self.snapshot_at.tzinfo is None:
            raise ValueError("broker order timestamp must be timezone-aware")


@dataclass(frozen=True)
class RealLocalOrder:
    project_order_id: str
    client_request_id: str
    broker_order_id: str | None
    concrete_contract_id: str
    direction: PositionDirection
    action: OrderAction
    requested_quantity: Decimal
    locally_applied_filled_quantity: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        for value, name in (
            (self.project_order_id, "project order id"),
            (self.client_request_id, "client request id"),
            (self.concrete_contract_id, "contract id"),
        ):
            _required_text(value, name)
        if self.broker_order_id is not None:
            _required_text(self.broker_order_id, "broker order id")
        if not isinstance(self.direction, PositionDirection) or not isinstance(self.action, OrderAction):
            raise ValueError("local order requires explicit direction and action")
        _positive_decimal(self.requested_quantity, "local requested quantity")
        if (
            type(self.locally_applied_filled_quantity) is not Decimal
            or not self.locally_applied_filled_quantity.is_finite()
            or self.locally_applied_filled_quantity < 0
            or self.locally_applied_filled_quantity > self.requested_quantity
        ):
            raise ValueError("locally applied fill quantity must be within requested quantity")


@dataclass(frozen=True)
class RealLocalExecutionState:
    trading_day: str
    expected_account: BrokerAccountSnapshot
    expected_positions: tuple[BrokerPositionSnapshot, ...]
    project_orders: tuple[RealLocalOrder, ...]

    def __post_init__(self) -> None:
        _validate_trading_day(self.trading_day)
        if not isinstance(self.expected_account, BrokerAccountSnapshot):
            raise ValueError("local state requires BrokerAccountSnapshot")
        if not isinstance(self.expected_positions, tuple) or any(
            not isinstance(item, BrokerPositionSnapshot) for item in self.expected_positions
        ):
            raise ValueError("local positions must be BrokerPositionSnapshot values")
        if not isinstance(self.project_orders, tuple) or any(
            not isinstance(item, RealLocalOrder) for item in self.project_orders
        ):
            raise ValueError("local orders must be RealLocalOrder values")
        if len({(item.concrete_contract_id, item.direction) for item in self.expected_positions}) != len(
            self.expected_positions
        ):
            raise ValueError("local state rejects duplicate position identities")
        if len({item.project_order_id for item in self.project_orders}) != len(self.project_orders):
            raise ValueError("local state rejects duplicate project order ids")
        if len({item.client_request_id for item in self.project_orders}) != len(self.project_orders):
            raise ValueError("local state rejects duplicate client request ids")
        broker_order_ids = tuple(
            item.broker_order_id for item in self.project_orders if item.broker_order_id is not None
        )
        if len(set(broker_order_ids)) != len(broker_order_ids):
            raise ValueError("local state rejects duplicate broker order ids")


@dataclass(frozen=True)
class RealBrokerQueryRound:
    round_id: str
    trading_day: str
    requested_at: datetime
    observed_at: datetime
    account_status: QueryCompleteness
    position_status: QueryCompleteness
    order_status: QueryCompleteness
    account: BrokerAccountSnapshot | None
    positions: tuple[BrokerPositionSnapshot, ...]
    orders: tuple[RealBrokerOrder, ...]

    def __post_init__(self) -> None:
        _required_text(self.round_id, "query round id")
        _validate_trading_day(self.trading_day)
        for value in (self.requested_at, self.observed_at):
            if not isinstance(value, datetime) or value.tzinfo is None:
                raise ValueError("query round timestamps must be timezone-aware")
        if self.observed_at < self.requested_at:
            raise ValueError("query round cannot complete before it was requested")
        for status in (self.account_status, self.position_status, self.order_status):
            if not isinstance(status, QueryCompleteness):
                raise ValueError("query completeness must be explicit")
        if self.account_status is QueryCompleteness.COMPLETE and not isinstance(
            self.account, BrokerAccountSnapshot
        ):
            raise ValueError("complete account query requires an account snapshot")
        if self.account is not None and not isinstance(self.account, BrokerAccountSnapshot):
            raise ValueError("query account must be BrokerAccountSnapshot or None")
        if not isinstance(self.positions, tuple) or any(
            not isinstance(item, BrokerPositionSnapshot) for item in self.positions
        ):
            raise ValueError("query positions must be BrokerPositionSnapshot values")
        if not isinstance(self.orders, tuple) or any(not isinstance(item, RealBrokerOrder) for item in self.orders):
            raise ValueError("query orders must be RealBrokerOrder values")
        if len({(item.concrete_contract_id, item.direction) for item in self.positions}) != len(self.positions):
            raise ValueError("query round rejects duplicate position identities")
        if len({item.broker_order_id for item in self.orders}) != len(self.orders):
            raise ValueError("query round rejects duplicate broker order ids")
        for snapshot in ((self.account,) if self.account is not None else ()) + self.positions + self.orders:
            if snapshot.snapshot_at > self.observed_at:
                raise ValueError("query round rejects future broker facts")

    @property
    def complete(self) -> bool:
        return all(
            status is QueryCompleteness.COMPLETE
            for status in (self.account_status, self.position_status, self.order_status)
        )


@dataclass(frozen=True)
class ExternalMutation:
    kind: ExternalMutationKind
    subject_id: str
    detail: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ExternalMutationKind):
            raise ValueError("external mutation kind must be explicit")
        _required_text(self.subject_id, "external mutation subject")
        _required_text(self.detail, "external mutation detail")


@dataclass(frozen=True)
class RealOrderResolution:
    project_order_id: str
    broker_order: RealBrokerOrder | None
    status: str

    def __post_init__(self) -> None:
        _required_text(self.project_order_id, "resolved project order id")
        _required_text(self.status, "resolved order status")
        if self.broker_order is not None and not isinstance(self.broker_order, RealBrokerOrder):
            raise ValueError("order resolution broker fact must be RealBrokerOrder or None")


@dataclass(frozen=True)
class RealReconciliationReport:
    query_round: RealBrokerQueryRound
    broker_truth_complete: bool
    new_risk_allowed: bool
    blockers: tuple[str, ...]
    external_mutations: tuple[ExternalMutation, ...]
    order_resolutions: tuple[RealOrderResolution, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.query_round, RealBrokerQueryRound):
            raise ValueError("reconciliation report requires its query round")
        if type(self.broker_truth_complete) is not bool or type(self.new_risk_allowed) is not bool:
            raise ValueError("reconciliation report flags must be bool")
        if self.blockers != tuple(sorted(set(self.blockers))):
            raise ValueError("reconciliation blockers must be sorted and unique")
        if not isinstance(self.external_mutations, tuple) or not isinstance(self.order_resolutions, tuple):
            raise ValueError("reconciliation report collections must be tuples")
        if any(not isinstance(item, ExternalMutation) for item in self.external_mutations):
            raise ValueError("reconciliation mutations must be ExternalMutation values")
        if any(not isinstance(item, RealOrderResolution) for item in self.order_resolutions):
            raise ValueError("reconciliation resolutions must be RealOrderResolution values")
        if self.new_risk_allowed != (
            self.broker_truth_complete
            and not self.blockers
            and not self.external_mutations
        ):
            raise ValueError("new-risk flag must match complete unblocked broker truth")


def _query_blockers(query_round: RealBrokerQueryRound) -> tuple[str, ...]:
    blockers = []
    for label, status in (
        ("ACCOUNT", query_round.account_status),
        ("POSITION", query_round.position_status),
        ("ORDER", query_round.order_status),
    ):
        if status is not QueryCompleteness.COMPLETE:
            blockers.append(f"{label}_QUERY_{status.value}")
    return tuple(sorted(blockers))


def _matching_broker_orders(
    local_order: RealLocalOrder,
    broker_orders: tuple[RealBrokerOrder, ...],
) -> tuple[RealBrokerOrder, ...]:
    return tuple(
        item
        for item in broker_orders
        if (
            item.project_order_id == local_order.project_order_id
            or item.client_request_id == local_order.client_request_id
            or (
                local_order.broker_order_id is not None
                and item.broker_order_id == local_order.broker_order_id
            )
        )
    )


def _order_envelope_matches(local_order: RealLocalOrder, broker_order: RealBrokerOrder) -> bool:
    return (
        broker_order.project_order_id in (None, local_order.project_order_id)
        and broker_order.client_request_id in (None, local_order.client_request_id)
        and (
            local_order.broker_order_id is None
            or broker_order.broker_order_id == local_order.broker_order_id
        )
        and broker_order.concrete_contract_id == local_order.concrete_contract_id
        and broker_order.direction is local_order.direction
        and broker_order.action is local_order.action
        and broker_order.requested_quantity == local_order.requested_quantity
    )


def reconcile_real_runtime(
    local_state: RealLocalExecutionState,
    query_round: RealBrokerQueryRound,
    *,
    expected_trading_day: str,
) -> RealReconciliationReport:
    """Compare one broker query round without mutating or guessing local state."""
    if not isinstance(local_state, RealLocalExecutionState):
        raise ValueError("REAL reconciliation requires RealLocalExecutionState")
    if not isinstance(query_round, RealBrokerQueryRound):
        raise ValueError("REAL reconciliation requires RealBrokerQueryRound")
    _validate_trading_day(expected_trading_day)

    blockers = list(_query_blockers(query_round))
    if local_state.trading_day != expected_trading_day:
        blockers.append("LOCAL_TRADING_DAY_MISMATCH")
    if query_round.trading_day != expected_trading_day:
        blockers.append("BROKER_QUERY_TRADING_DAY_MISMATCH")
    broker_truth_complete = query_round.complete and not any(
        item.endswith("TRADING_DAY_MISMATCH") for item in blockers
    )
    if not broker_truth_complete:
        return RealReconciliationReport(
            query_round=query_round,
            broker_truth_complete=False,
            new_risk_allowed=False,
            blockers=tuple(sorted(set(blockers))),
            external_mutations=(),
            order_resolutions=tuple(
                RealOrderResolution(item.project_order_id, None, "UNKNOWN")
                for item in local_state.project_orders
            ),
        )

    mutations: list[ExternalMutation] = []
    if query_round.account is None:
        raise ValueError("complete REAL reconciliation requires broker account truth")
    account_fields = (
        "account_id",
        "cash_balance",
        "reserved_margin",
        "charged_costs",
        "realized_pnl",
        "unrealized_pnl",
        "currency",
    )
    changed_account_fields = tuple(
        field
        for field in account_fields
        if getattr(local_state.expected_account, field) != getattr(query_round.account, field)
    )
    if changed_account_fields:
        mutations.append(ExternalMutation(
            ExternalMutationKind.ACCOUNT_STATE_CHANGED,
            query_round.account.account_id,
            "changed fields=" + ",".join(changed_account_fields),
        ))
        blockers.append("ACCOUNT_STATE_CHANGED")

    local_positions = {
        (item.concrete_contract_id, item.direction): item
        for item in local_state.expected_positions
    }
    broker_positions = {
        (item.concrete_contract_id, item.direction): item
        for item in query_round.positions
    }
    explained_position_deltas: dict[tuple[str, PositionDirection], Decimal] = {}
    for local_order in local_state.project_orders:
        matches = _matching_broker_orders(local_order, query_round.orders)
        if len(matches) != 1 or not _order_envelope_matches(local_order, matches[0]):
            continue
        newly_broker_confirmed = matches[0].filled_quantity - local_order.locally_applied_filled_quantity
        if newly_broker_confirmed < 0:
            continue
        signed_delta = (
            newly_broker_confirmed
            if local_order.action is OrderAction.OPEN
            else -newly_broker_confirmed
        )
        if signed_delta == 0:
            continue
        key = (local_order.concrete_contract_id, local_order.direction)
        explained_position_deltas[key] = explained_position_deltas.get(key, Decimal("0")) + signed_delta

    position_keys = set(local_positions) | set(broker_positions) | set(explained_position_deltas)
    for key in sorted(position_keys, key=lambda item: (item[0], item[1].value)):
        local_position = local_positions.get(key)
        broker_position = broker_positions.get(key)
        subject_id = f"{key[0]}:{key[1].value}"
        local_quantity = Decimal("0") if local_position is None else local_position.quantity
        broker_quantity = Decimal("0") if broker_position is None else broker_position.quantity
        explained_delta = explained_position_deltas.get(key, Decimal("0"))
        if explained_delta != 0 and broker_quantity == local_quantity + explained_delta:
            # The broker position is explained by a matching project order;
            # broker quantity/price is authoritative recovery input, not a
            # manual/external mutation.
            continue
        if explained_delta != 0:
            expected_quantity = local_quantity + explained_delta
            mutations.append(ExternalMutation(
                ExternalMutationKind.PROJECT_ORDER_POSITION_CONFLICT,
                subject_id,
                f"expected_from_project_orders={expected_quantity}:broker={broker_quantity}",
            ))
            blockers.append(f"PROJECT_ORDER_POSITION_CONFLICT:{subject_id}")
            continue
        if local_position is None:
            mutation = ExternalMutation(
                ExternalMutationKind.POSITION_APPEARED,
                subject_id,
                "broker position has no matching project position",
            )
            mutations.append(mutation)
            blockers.append(f"POSITION_APPEARED:{subject_id}")
            continue
        if broker_position is None:
            mutation = ExternalMutation(
                ExternalMutationKind.POSITION_CLOSED,
                subject_id,
                "project position is absent from the complete broker query",
            )
            mutations.append(mutation)
            blockers.append(f"POSITION_CLOSED:{subject_id}")
            continue
        if broker_position.quantity != local_position.quantity:
            kind = (
                ExternalMutationKind.POSITION_INCREASED
                if broker_position.quantity > local_position.quantity
                else ExternalMutationKind.POSITION_REDUCED
            )
            mutations.append(ExternalMutation(
                kind,
                subject_id,
                f"project={local_position.quantity}:broker={broker_position.quantity}",
            ))
            blockers.append(f"{kind.value}:{subject_id}")
        if broker_position.average_price != local_position.average_price:
            mutations.append(ExternalMutation(
                ExternalMutationKind.POSITION_PRICE_CHANGED,
                subject_id,
                f"project={local_position.average_price}:broker={broker_position.average_price}",
            ))
            blockers.append(f"POSITION_PRICE_CHANGED:{subject_id}")

    resolutions: list[RealOrderResolution] = []
    matched_broker_order_ids: set[str] = set()
    for local_order in local_state.project_orders:
        matches = _matching_broker_orders(local_order, query_round.orders)
        if len(matches) != 1:
            kind = (
                ExternalMutationKind.LOCAL_ORDER_MISSING
                if not matches
                else ExternalMutationKind.ORDER_IDENTITY_CONFLICT
            )
            detail = "broker query did not contain this project order" if not matches else (
                "multiple broker orders matched one project order"
            )
            mutations.append(ExternalMutation(kind, local_order.project_order_id, detail))
            blockers.append(f"{kind.value}:{local_order.project_order_id}")
            resolutions.append(RealOrderResolution(local_order.project_order_id, None, "UNKNOWN"))
            continue
        broker_order = matches[0]
        matched_broker_order_ids.add(broker_order.broker_order_id)
        if not _order_envelope_matches(local_order, broker_order):
            mutations.append(ExternalMutation(
                ExternalMutationKind.ORDER_IDENTITY_CONFLICT,
                local_order.project_order_id,
                "broker order envelope conflicts with project order identity",
            ))
            blockers.append(f"ORDER_IDENTITY_CONFLICT:{local_order.project_order_id}")
            resolutions.append(RealOrderResolution(local_order.project_order_id, broker_order, "UNKNOWN"))
            continue
        resolutions.append(RealOrderResolution(
            local_order.project_order_id,
            broker_order,
            broker_order.status,
        ))

    for broker_order in query_round.orders:
        if broker_order.broker_order_id not in matched_broker_order_ids:
            mutations.append(ExternalMutation(
                ExternalMutationKind.EXTERNAL_ORDER,
                broker_order.broker_order_id,
                "broker order has no matching project action",
            ))
            blockers.append(f"EXTERNAL_ORDER:{broker_order.broker_order_id}")

    sorted_mutations = tuple(sorted(
        mutations,
        key=lambda item: (item.kind.value, item.subject_id, item.detail),
    ))
    sorted_blockers = tuple(sorted(set(blockers)))
    return RealReconciliationReport(
        query_round=query_round,
        broker_truth_complete=True,
        new_risk_allowed=not sorted_blockers,
        blockers=sorted_blockers,
        external_mutations=sorted_mutations,
        order_resolutions=tuple(sorted(resolutions, key=lambda item: item.project_order_id)),
    )

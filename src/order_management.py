"""Order Management System (OMS) for the Shadow Runtime Foundation.

The OMS owns the deterministic client-side order lifecycle (intent through
broker confirmation). It produces orders from intents, tracks the intended
status transitions (submit / cancel / replace), and applies broker events so
broker/exchange facts override local inference (Skeleton v1.0 §5).

Broker-confirmed facts are mirrored inside ``TradingState`` (``RuntimeOrderState``)
as well; the OMS here is the client-side order book that also consumes broker
events, while ``TradingState`` remains the authoritative accounting owner.

No real broker, no network, no candidate outcome, no real money.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from hashlib import sha256
import json
from typing import Any, Iterable

from src.broker_adapter import OrderType
from src.contract_semantics import OrderAction, PositionDirection
from src.runtime_events import BrokerEvent, BrokerEventType
from src.trading_state import OrderStatus

OMS_SCHEMA_VERSION = "shadow-runtime-oms-v0.1"


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def deterministic_order_id(client_request_id: str) -> str:
    """Deterministic engine-side order identity derived from the request."""
    return _canonical_hash({"client_request_id": client_request_id, "oms": OMS_SCHEMA_VERSION})


@dataclass(frozen=True)
class OrderRequest:
    """One deterministic order request produced from an approved intent."""

    client_request_id: str
    concrete_contract_id: str
    direction: PositionDirection
    action: OrderAction
    order_type: OrderType
    quantity: Decimal
    strategy_identity_id: str | None = None
    limit_price: Decimal | None = None

    def __post_init__(self) -> None:
        if not self.client_request_id or not self.concrete_contract_id:
            raise ValueError("order request requires client and contract identities")
        if not isinstance(self.direction, PositionDirection) or not isinstance(self.action, OrderAction):
            raise ValueError("order request requires explicit direction and action")
        if not isinstance(self.order_type, OrderType):
            raise ValueError("order request requires an explicit order type")
        if type(self.quantity) is not Decimal or not self.quantity.is_finite() or self.quantity <= 0:
            raise ValueError("order request quantity must be a positive finite Decimal")
        if self.limit_price is not None:
            if type(self.limit_price) is not Decimal or not self.limit_price.is_finite() or self.limit_price <= 0:
                raise ValueError("order request limit price must be a positive finite Decimal")
            if self.order_type is not OrderType.LIMIT:
                raise ValueError("limit price is only valid for a LIMIT order")
        elif self.order_type is OrderType.LIMIT:
            raise ValueError("a LIMIT order request requires a limit price")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "client_request_id": self.client_request_id,
                "strategy_identity_id": self.strategy_identity_id,
                "concrete_contract_id": self.concrete_contract_id,
                "direction": self.direction.value,
                "action": self.action.value,
                "order_type": self.order_type.value,
                "quantity": str(self.quantity),
                "limit_price": None if self.limit_price is None else str(self.limit_price),
            }
        )


@dataclass(frozen=True)
class Order:
    """One deterministic order with a tracked lifecycle."""

    order_id: str
    client_request_id: str
    concrete_contract_id: str
    direction: PositionDirection
    action: OrderAction
    order_type: OrderType
    quantity: Decimal
    status: OrderStatus
    strategy_identity_id: str | None = None
    limit_price: Decimal | None = None
    filled_quantity: Decimal = Decimal("0")
    average_fill_price: Decimal | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_event_id: str | None = None

    def __post_init__(self) -> None:
        required = (self.order_id, self.client_request_id, self.concrete_contract_id)
        if not all(required):
            raise ValueError("order requires complete identities")
        if not isinstance(self.direction, PositionDirection) or not isinstance(self.action, OrderAction):
            raise ValueError("order requires explicit direction and action")
        if not isinstance(self.order_type, OrderType):
            raise ValueError("order requires an explicit order type")
        if not isinstance(self.status, OrderStatus):
            raise ValueError("order requires an OrderStatus")
        if type(self.quantity) is not Decimal or not self.quantity.is_finite() or self.quantity <= 0:
            raise ValueError("order quantity must be a positive finite Decimal")
        if type(self.filled_quantity) is not Decimal or not self.filled_quantity.is_finite() or self.filled_quantity < 0:
            raise ValueError("order filled quantity must be a non-negative finite Decimal")
        if self.filled_quantity > self.quantity:
            raise ValueError("order cannot be filled beyond its quantity")
        if self.average_fill_price is not None and (
            type(self.average_fill_price) is not Decimal
            or not self.average_fill_price.is_finite()
            or self.average_fill_price <= 0
        ):
            raise ValueError("order average fill price must be a positive finite Decimal")
        for field in (self.created_at, self.updated_at):
            if field is not None and field.tzinfo is None:
                raise ValueError("order timestamps must be timezone-aware")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "order_id": self.order_id,
                "client_request_id": self.client_request_id,
                "strategy_identity_id": self.strategy_identity_id,
                "concrete_contract_id": self.concrete_contract_id,
                "direction": self.direction.value,
                "action": self.action.value,
                "order_type": self.order_type.value,
                "quantity": str(self.quantity),
                "limit_price": None if self.limit_price is None else str(self.limit_price),
                "status": self.status.value,
                "filled_quantity": str(self.filled_quantity),
                "average_fill_price": (
                    None if self.average_fill_price is None else str(self.average_fill_price)
                ),
                "created_at": None if self.created_at is None else self.created_at.isoformat(),
                "updated_at": None if self.updated_at is None else self.updated_at.isoformat(),
                "last_event_id": self.last_event_id,
            }
        )


def _now(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("OMS timestamps must be timezone-aware")
    return value


class OrderManagementSystem:
    """Client-side deterministic order lifecycle owner."""

    def __init__(self) -> None:
        self._orders: dict[str, Order] = {}
        self._by_request: dict[str, str] = {}

    # -- queries ---------------------------------------------------------------

    def get(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def order_by_request(self, client_request_id: str) -> Order | None:
        order_id = self._by_request.get(client_request_id)
        if order_id is None:
            return None
        return self._orders.get(order_id)

    def orders(self) -> tuple[Order, ...]:
        return tuple(sorted(self._orders.values(), key=lambda item: item.order_id))

    def open_orders(self) -> tuple[Order, ...]:
        return tuple(
            order
            for order in self.orders()
            if order.status
            in (OrderStatus.PENDING_SUBMIT, OrderStatus.LIVE, OrderStatus.PARTIALLY_FILLED)
        )

    # -- lifecycle -------------------------------------------------------------

    def create_order(self, request: OrderRequest, created_at: datetime) -> Order:
        if not isinstance(request, OrderRequest):
            raise ValueError("OMS create requires an OrderRequest")
        at = _now(created_at)
        if request.client_request_id in self._by_request:
            raise ValueError(f"duplicate client_request_id: {request.client_request_id}")
        order = Order(
            order_id=deterministic_order_id(request.client_request_id),
            client_request_id=request.client_request_id,
            concrete_contract_id=request.concrete_contract_id,
            direction=request.direction,
            action=request.action,
            order_type=request.order_type,
            quantity=request.quantity,
            status=OrderStatus.PENDING_SUBMIT,
            strategy_identity_id=request.strategy_identity_id,
            limit_price=request.limit_price,
            created_at=at,
            updated_at=at,
        )
        self._orders[order.order_id] = order
        self._by_request[order.client_request_id] = order.order_id
        return order

    def cancel(self, order_id: str, requested_at: datetime) -> Order:
        order = self._require(order_id)
        at = _now(requested_at)
        if order.status not in (OrderStatus.LIVE, OrderStatus.PARTIALLY_FILLED, OrderStatus.PENDING_SUBMIT):
            raise ValueError(f"order {order_id} cannot be cancelled from {order.status.value}")
        updated = self._replace(order, status=OrderStatus.CANCEL_PENDING, updated_at=at)
        self._orders[order_id] = updated
        return updated

    def replace(self, order_id: str, new_quantity: Decimal, requested_at: datetime) -> Order:
        order = self._require(order_id)
        at = _now(requested_at)
        if type(new_quantity) is not Decimal or not new_quantity.is_finite() or new_quantity <= 0:
            raise ValueError("replace quantity must be a positive finite Decimal")
        if new_quantity < order.filled_quantity:
            raise ValueError("replace cannot reduce below the already-filled quantity")
        if order.status not in (OrderStatus.LIVE, OrderStatus.PARTIALLY_FILLED, OrderStatus.PENDING_SUBMIT):
            raise ValueError(f"order {order_id} cannot be replaced from {order.status.value}")
        updated = self._replace(
            order,
            status=OrderStatus.REPLACE_PENDING,
            quantity=new_quantity,
            updated_at=at,
        )
        self._orders[order_id] = updated
        return updated

    def apply_broker_event(self, event: BrokerEvent) -> Order | None:
        """Apply broker facts to the client-side order lifecycle.

        Returns the updated ``Order`` when the event concerns a tracked order,
        else ``None``. Broker facts override local inference; invalid lifecycle
        transitions fail closed with ``ValueError``.
        """
        if not isinstance(event, BrokerEvent):
            raise ValueError("OMS requires a BrokerEvent")
        if event.order_id is None:
            return None
        order = self._orders.get(event.order_id)
        if order is None and event.client_request_id is not None:
            order = self.order_by_request(event.client_request_id)
        if order is None:
            # An event for an order the OMS never created is a broker anomaly; the
            # authoritative TradingState rejects it and Safety flags it. The OMS
            # stays resilient and does not hard-crash the runtime here.
            return None
        at = _now(event.occurred_at)

        if event.event_type is BrokerEventType.ORDER_SUBMITTED:
            updated = self._replace(order, status=OrderStatus.LIVE, updated_at=at, last_event_id=event.event_id)
        elif event.event_type is BrokerEventType.ORDER_REJECTED:
            updated = self._replace(order, status=OrderStatus.REJECTED, updated_at=at, last_event_id=event.event_id)
        elif event.event_type is BrokerEventType.ORDER_CANCELLED:
            updated = self._replace(order, status=OrderStatus.CANCELLED, updated_at=at, last_event_id=event.event_id)
        elif event.event_type is BrokerEventType.ORDER_REPLACED:
            updated = self._replace(order, status=OrderStatus.REPLACED, updated_at=at, last_event_id=event.event_id)
        elif event.event_type is BrokerEventType.ORDER_FILLED:
            updated = self._apply_fill(order, event)
        else:
            return None
        self._orders[updated.order_id] = updated
        self._by_request[updated.client_request_id] = updated.order_id
        return updated

    def _apply_fill(self, order: Order, event: BrokerEvent) -> Order:
        if order.status not in (OrderStatus.LIVE, OrderStatus.PARTIALLY_FILLED):
            raise ValueError(f"order {order.order_id} cannot receive a fill from {order.status.value}")
        payload = dict(event.payload)
        if "quantity" not in payload or "price" not in payload:
            raise ValueError("ORDER_FILLED event requires quantity and price payload")
        quantity = Decimal(payload["quantity"])
        price = Decimal(payload["price"])
        if quantity <= 0 or price <= 0:
            raise ValueError("fill quantity and price must be positive")
        new_filled = order.filled_quantity + quantity
        if new_filled > order.quantity:
            raise ValueError("fill would over-fill the order")
        previous_avg = order.average_fill_price
        if previous_avg is None:
            new_avg = price
        else:
            new_avg = (previous_avg * order.filled_quantity + price * quantity) / new_filled
        new_status = OrderStatus.FILLED if new_filled == order.quantity else OrderStatus.PARTIALLY_FILLED
        return self._replace(
            order,
            status=new_status,
            filled_quantity=new_filled,
            average_fill_price=new_avg,
            updated_at=event.occurred_at,
            last_event_id=event.event_id,
        )

    def _require(self, order_id: str) -> Order:
        order = self._orders.get(order_id)
        if order is None:
            raise ValueError(f"unknown order id: {order_id}")
        return order

    @staticmethod
    def _replace(order: Order, **changes: Any) -> Order:
        return Order(
            order_id=changes.get("order_id", order.order_id),
            client_request_id=changes.get("client_request_id", order.client_request_id),
            concrete_contract_id=changes.get("concrete_contract_id", order.concrete_contract_id),
            direction=changes.get("direction", order.direction),
            action=changes.get("action", order.action),
            order_type=changes.get("order_type", order.order_type),
            quantity=changes.get("quantity", order.quantity),
            status=changes.get("status", order.status),
            strategy_identity_id=changes.get("strategy_identity_id", order.strategy_identity_id),
            limit_price=changes.get("limit_price", order.limit_price),
            filled_quantity=changes.get("filled_quantity", order.filled_quantity),
            average_fill_price=changes.get("average_fill_price", order.average_fill_price),
            created_at=changes.get("created_at", order.created_at),
            updated_at=changes.get("updated_at", order.updated_at),
            last_event_id=changes.get("last_event_id", order.last_event_id),
        )


def orders_by_contract(orders: Iterable[Order], concrete_contract_id: str) -> tuple[Order, ...]:
    return tuple(
        order for order in sorted(orders, key=lambda item: item.order_id)
        if order.concrete_contract_id == concrete_contract_id
    )

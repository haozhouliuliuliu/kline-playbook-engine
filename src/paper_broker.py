"""Deterministic PaperBrokerAdapter for the Shadow Runtime Foundation.

``PaperBrokerAdapter`` is the project-owned, deterministic paper (synthetic)
implementation of ``BrokerAdapter``. It:

- never connects to any external network or real broker;
- does NOT mimic any real broker's private API (no TqSdk/CTP/SimNow);
- is fully deterministic: the same sequence of instructions/bars produces the
  same broker event stream and the same broker-side snapshot;
- maintains a broker-side mirror (orders/positions/account) so reconciliation
  has a real broker-side truth to compare against;
- supports deterministic snapshot capture/restore for crash/restart recovery;
- exposes an explicit ``inject_events`` TEST hook so tests can craft duplicate,
  out-of-order and other failure events (the paper broker itself never emits
  duplicates or out-of-order events in normal operation).

Fill policies
-------------
``IMMEDIATE_MARKET_AT_REFERENCE``:
    market orders fill immediately at the ``reference_price`` the caller passes
    (the primary E2E path: fill at the completed-bar price that generated the
    intent).
``RESTING_ON_COMPLETED_BAR``:
    orders rest and are filled deterministically by ``ingest_completed_bar``
    (market at bar open; limit at the limit price when the bar trades through,
    conservative completed-bar model - no intrabar chronology claim).

No real money, no candidate strategy outcome.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Iterable
from zoneinfo import ZoneInfo

from src.broker_adapter import (
    BrokerAccountSnapshot,
    BrokerAdapter,
    BrokerOrderInstruction,
    BrokerOrderSnapshot,
    BrokerPositionSnapshot,
    OrderType,
)
from src.contract_semantics import ContractSpecification, OrderAction, PositionDirection
from src.historical_data import NormalizedHistoricalBar
from src.runtime_events import (
    BrokerConnectionState,
    BrokerEvent,
    BrokerEventType,
    event_pairs,
)
from src.trading_state import OrderStatus, RuntimeAccountingAssumptions

PAPER_BROKER_SCHEMA_VERSION = "shadow-runtime-paper-broker-v0.1"

DEFAULT_STREAM_ID = "paper-broker"


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class PaperFillPolicy(str, Enum):
    IMMEDIATE_MARKET_AT_REFERENCE = "IMMEDIATE_MARKET_AT_REFERENCE"
    RESTING_ON_COMPLETED_BAR = "RESTING_ON_COMPLETED_BAR"


@dataclass(frozen=True)
class PaperBrokerOrder:
    """Broker-side order record inside the paper broker."""

    order_id: str
    client_request_id: str
    concrete_contract_id: str
    direction: PositionDirection
    action: OrderAction
    order_type: OrderType
    quantity: Decimal
    limit_price: Decimal | None
    status: OrderStatus
    filled_quantity: Decimal
    average_fill_price: Decimal | None
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        required = (self.order_id, self.client_request_id, self.concrete_contract_id)
        if not all(required):
            raise ValueError("paper broker order requires complete identities")
        if not isinstance(self.direction, PositionDirection) or not isinstance(self.action, OrderAction):
            raise ValueError("paper broker order requires explicit direction and action")
        if not isinstance(self.order_type, OrderType) or not isinstance(self.status, OrderStatus):
            raise ValueError("paper broker order requires explicit order type and status")
        if type(self.quantity) is not Decimal or not self.quantity.is_finite() or self.quantity <= 0:
            raise ValueError("paper broker order quantity must be a positive finite Decimal")
        if type(self.filled_quantity) is not Decimal or not self.filled_quantity.is_finite() or self.filled_quantity < 0:
            raise ValueError("paper broker order filled quantity must be a non-negative finite Decimal")
        if self.filled_quantity > self.quantity:
            raise ValueError("paper broker order cannot be over-filled")
        if self.average_fill_price is not None and (
            type(self.average_fill_price) is not Decimal
            or not self.average_fill_price.is_finite()
            or self.average_fill_price <= 0
        ):
            raise ValueError("paper broker order average fill price must be a positive finite Decimal")
        if self.created_at.tzinfo is None or self.updated_at.tzinfo is None:
            raise ValueError("paper broker order timestamps must be timezone-aware")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "order_id": self.order_id,
                "client_request_id": self.client_request_id,
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
                "created_at": self.created_at.isoformat(),
                "updated_at": self.updated_at.isoformat(),
            }
        )


@dataclass(frozen=True)
class PaperBrokerSnapshot:
    """Deterministic broker-side snapshot fixture for restart recovery.

    ``positions`` is the public reconciliation view; ``mirror_positions`` is
    the exact raw broker mirror (contract, direction, quantity, average,
    realized, last-mark as canonical strings) so restore is byte-exact.
    """

    broker_id: str
    snapshot_at: datetime
    connection_state: BrokerConnectionState
    stream_id: str
    next_sequence: int
    orders: tuple[PaperBrokerOrder, ...]
    positions: tuple[BrokerPositionSnapshot, ...]
    mirror_positions: tuple[tuple[str, str, str, str, str, str], ...]
    account: BrokerAccountSnapshot
    pending_outbox_events: tuple[BrokerEvent, ...]

    def __post_init__(self) -> None:
        if not self.broker_id or not self.stream_id:
            raise ValueError("paper broker snapshot requires broker and stream identities")
        if self.snapshot_at.tzinfo is None:
            raise ValueError("paper broker snapshot timestamp must be timezone-aware")
        if type(self.next_sequence) is not int or self.next_sequence < 0:
            raise ValueError("paper broker snapshot next sequence must be a non-negative integer")
        if not isinstance(self.connection_state, BrokerConnectionState):
            raise ValueError("paper broker snapshot connection state must be explicit")
        if not isinstance(self.account, BrokerAccountSnapshot):
            raise ValueError("paper broker snapshot requires a broker account snapshot")
        for value in (self.orders, self.positions, self.mirror_positions, self.pending_outbox_events):
            if not isinstance(value, tuple):
                raise ValueError("paper broker snapshot collections must be tuples")
        if len(self.mirror_positions) != len(self.positions):
            raise ValueError("paper broker snapshot mirror and public positions must agree in count")
        for entry in self.mirror_positions:
            if len(entry) != 6 or not all(isinstance(item, str) for item in entry):
                raise ValueError("paper broker snapshot mirror entries must be 6 canonical strings")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "broker_id": self.broker_id,
                "snapshot_at": self.snapshot_at.isoformat(),
                "connection_state": self.connection_state.value,
                "stream_id": self.stream_id,
                "next_sequence": self.next_sequence,
                "orders": [item.identity_id for item in self.orders],
                "positions": [item.identity_id for item in self.positions],
                "mirror_positions": self.mirror_positions,
                "account": self.account.identity_id,
                "pending_outbox_events": [item.identity_id for item in self.pending_outbox_events],
            }
        )


class PaperBrokerAdapter(BrokerAdapter):
    """Deterministic paper broker (synthetic only, no network)."""

    def __init__(
        self,
        *,
        broker_id: str,
        contract_specs: Iterable[ContractSpecification],
        accounting: RuntimeAccountingAssumptions,
        starting_capital: Decimal,
        currency: str,
        fill_policy: PaperFillPolicy = PaperFillPolicy.IMMEDIATE_MARKET_AT_REFERENCE,
        stream_id: str = DEFAULT_STREAM_ID,
        timezone: str = "Asia/Shanghai",
    ) -> None:
        if not broker_id or not currency:
            raise ValueError("paper broker requires broker and currency identities")
        if type(starting_capital) is not Decimal or not starting_capital.is_finite() or starting_capital <= 0:
            raise ValueError("paper broker starting capital must be a positive finite Decimal")
        if not isinstance(accounting, RuntimeAccountingAssumptions):
            raise ValueError("paper broker requires RuntimeAccountingAssumptions")
        if not isinstance(fill_policy, PaperFillPolicy):
            raise ValueError("paper broker requires a PaperFillPolicy")
        ZoneInfo(timezone)  # fail fast on an unknown timezone
        specs = tuple(contract_specs)
        if not specs or any(not isinstance(item, ContractSpecification) for item in specs):
            raise ValueError("paper broker requires ContractSpecification values")

        self._broker_id = broker_id
        self._contract_specs = {item.instrument_id: item for item in specs}
        self._accounting = accounting
        self._starting_capital = starting_capital
        self._currency = currency
        self._fill_policy = fill_policy
        self._stream_id = stream_id
        self._timezone = timezone

        self._connection_state = BrokerConnectionState.CONNECTED
        self._next_sequence = 0
        self._orders: dict[str, PaperBrokerOrder] = {}
        self._positions: dict[tuple[str, PositionDirection], tuple[Decimal, Decimal, Decimal, Decimal]] = {}
        self._realized_accumulator = Decimal("0")
        self._account = BrokerAccountSnapshot(
            account_id=f"{broker_id}:account",
            snapshot_at=datetime.now(ZoneInfo(timezone)),
            cash_balance=starting_capital,
            reserved_margin=Decimal("0"),
            charged_costs=Decimal("0"),
            realized_pnl=Decimal("0"),
            unrealized_pnl=Decimal("0"),
            currency=currency,
        )
        self._outbox: list[BrokerEvent] = []

    # -- identity / connection -------------------------------------------------

    @property
    def broker_id(self) -> str:
        return self._broker_id

    @property
    def stream_id(self) -> str:
        return self._stream_id

    @property
    def connection_state(self) -> BrokerConnectionState:
        return self._connection_state

    def connect(self) -> None:
        self._connection_state = BrokerConnectionState.CONNECTED
        self._emit(BrokerEventType.CONNECTION_STATE, connection_state=self._connection_state.value)

    def disconnect(self) -> None:
        self._connection_state = BrokerConnectionState.DISCONNECTED
        self._emit(BrokerEventType.CONNECTION_STATE, connection_state=self._connection_state.value)

    # -- order submission ------------------------------------------------------

    def submit_order(
        self,
        instruction: BrokerOrderInstruction,
        *,
        reference_price: Decimal | None = None,
        at: datetime | None = None,
    ) -> str:
        if not isinstance(instruction, BrokerOrderInstruction):
            raise ValueError("paper broker requires a BrokerOrderInstruction")
        timestamp = self._clock(at)
        order_id = _canonical_hash(
            {"client_request_id": instruction.client_request_id, "paper_broker": self._broker_id}
        )
        if order_id in self._orders:
            raise ValueError(f"duplicate paper broker order: {order_id}")
        if instruction.concrete_contract_id not in self._contract_specs:
            raise ValueError("paper broker order references an unknown concrete contract")
        if self._connection_state is BrokerConnectionState.DISCONNECTED:
            raise ValueError("paper broker is disconnected; order rejected")

        order = PaperBrokerOrder(
            order_id=order_id,
            client_request_id=instruction.client_request_id,
            concrete_contract_id=instruction.concrete_contract_id,
            direction=instruction.direction,
            action=instruction.action,
            order_type=instruction.order_type,
            quantity=instruction.quantity,
            limit_price=instruction.limit_price,
            status=OrderStatus.LIVE,
            filled_quantity=Decimal("0"),
            average_fill_price=None,
            created_at=timestamp,
            updated_at=timestamp,
        )
        self._orders[order_id] = order
        self._emit(
            BrokerEventType.ORDER_SUBMITTED,
            order_id=order_id,
            client_request_id=instruction.client_request_id,
            quantity=str(instruction.quantity),
            direction=instruction.direction.value,
            action=instruction.action.value,
            order_type=instruction.order_type.value,
            concrete_contract_id=instruction.concrete_contract_id,
            limit_price=(
                None if instruction.limit_price is None else str(instruction.limit_price)
            ),
        )

        if self._fill_policy is PaperFillPolicy.IMMEDIATE_MARKET_AT_REFERENCE:
            if reference_price is None:
                raise ValueError(
                    "IMMEDIATE_MARKET_AT_REFERENCE policy requires a reference_price"
                )
            self._fill_order(order_id, reference_price, timestamp)
        return order_id

    def cancel_order(self, order_id: str, at: datetime | None = None) -> None:
        order = self._require_order(order_id)
        timestamp = self._clock(at)
        if order.status not in (OrderStatus.LIVE, OrderStatus.PARTIALLY_FILLED):
            raise ValueError(f"paper broker order {order_id} cannot be cancelled from {order.status.value}")
        self._orders[order_id] = self._with_status(order, OrderStatus.CANCELLED, timestamp)
        self._emit(
            BrokerEventType.ORDER_CANCELLED,
            order_id=order_id,
            client_request_id=order.client_request_id,
        )

    def replace_order(self, order_id: str, new_quantity: Decimal, at: datetime | None = None) -> None:
        order = self._require_order(order_id)
        timestamp = self._clock(at)
        if type(new_quantity) is not Decimal or not new_quantity.is_finite() or new_quantity <= 0:
            raise ValueError("replace quantity must be a positive finite Decimal")
        if new_quantity < order.filled_quantity:
            raise ValueError("replace cannot reduce below the already-filled quantity")
        if order.status not in (OrderStatus.LIVE, OrderStatus.PARTIALLY_FILLED):
            raise ValueError(f"paper broker order {order_id} cannot be replaced from {order.status.value}")
        self._orders[order_id] = PaperBrokerOrder(
            order_id=order.order_id,
            client_request_id=order.client_request_id,
            concrete_contract_id=order.concrete_contract_id,
            direction=order.direction,
            action=order.action,
            order_type=order.order_type,
            quantity=new_quantity,
            limit_price=order.limit_price,
            status=OrderStatus.REPLACED,
            filled_quantity=order.filled_quantity,
            average_fill_price=order.average_fill_price,
            created_at=order.created_at,
            updated_at=timestamp,
        )
        self._emit(
            BrokerEventType.ORDER_REPLACED,
            order_id=order_id,
            client_request_id=order.client_request_id,
            new_quantity=str(new_quantity),
        )

    # -- completed-bar driven fills (resting policy) ---------------------------

    def ingest_completed_bar(self, bar: NormalizedHistoricalBar, at: datetime | None = None) -> tuple[BrokerEvent, ...]:
        """Deterministically fill resting orders from one completed bar.

        Conservative completed-bar model: a market order fills at the bar open;
        a limit order fills at its limit price when the bar trades through it.
        No intrabar chronology is claimed. Returns the events generated.
        """
        if not isinstance(bar, NormalizedHistoricalBar):
            raise ValueError("ingest requires a NormalizedHistoricalBar")
        timestamp = self._clock(at)
        before = self._next_sequence
        for order in self._resting_orders():
            if order.concrete_contract_id != bar.concrete_instrument:
                continue
            fill_price: Decimal | None = None
            if order.order_type is OrderType.MARKET:
                fill_price = bar.open
            else:
                limit = order.limit_price
                if limit is not None:
                    if order.direction is PositionDirection.LONG and bar.low <= limit:
                        fill_price = limit
                    elif order.direction is PositionDirection.SHORT and bar.high >= limit:
                        fill_price = limit
            if fill_price is not None:
                self._fill_order(order.order_id, fill_price, timestamp)
        return tuple(event for event in self._outbox if self._sequence_of(event) >= before)

    def _resting_orders(self) -> tuple[PaperBrokerOrder, ...]:
        return tuple(
            order
            for order in sorted(self._orders.values(), key=lambda item: item.order_id)
            if order.status in (OrderStatus.LIVE, OrderStatus.PARTIALLY_FILLED)
        )

    # -- event outbox ----------------------------------------------------------

    def drain_events(self) -> tuple[BrokerEvent, ...]:
        events = tuple(self._outbox)
        self._outbox.clear()
        return events

    def inject_events(self, events: Iterable[BrokerEvent]) -> None:
        """TEST-ONLY hook to inject crafted events (duplicate/out-of-order/etc.).

        The paper broker never produces such events in normal operation; this
        hook exists so deterministic failure scenarios can be exercised through
        the normal drain/apply path.
        """
        for event in events:
            if not isinstance(event, BrokerEvent):
                raise ValueError("inject_events requires BrokerEvent values")
            self._outbox.append(event)

    # -- snapshots -------------------------------------------------------------

    def fetch_account_snapshot(self) -> BrokerAccountSnapshot:
        return self._account

    def fetch_position_snapshot(self) -> tuple[BrokerPositionSnapshot, ...]:
        now = self._account.snapshot_at
        return tuple(
            BrokerPositionSnapshot(
                concrete_contract_id=contract,
                direction=direction,
                quantity=quantity,
                average_price=average,
                snapshot_at=now,
            )
            for (contract, direction), (quantity, average, _, _) in sorted(
                self._positions.items(), key=lambda item: (item[0][0], item[0][1].value)
            )
        )

    def fetch_order_snapshot(self) -> tuple[BrokerOrderSnapshot, ...]:
        now = self._account.snapshot_at
        return tuple(
            BrokerOrderSnapshot(
                order_id=order.order_id,
                client_request_id=order.client_request_id,
                concrete_contract_id=order.concrete_contract_id,
                direction=order.direction,
                action=order.action,
                status=order.status.value,
                requested_quantity=order.quantity,
                filled_quantity=order.filled_quantity,
                snapshot_at=now,
            )
            for order in sorted(self._orders.values(), key=lambda item: item.order_id)
        )

    def capture_snapshot(self, at: datetime | None = None) -> PaperBrokerSnapshot:
        return PaperBrokerSnapshot(
            broker_id=self._broker_id,
            snapshot_at=self._clock(at),
            connection_state=self._connection_state,
            stream_id=self._stream_id,
            next_sequence=self._next_sequence,
            orders=tuple(sorted(self._orders.values(), key=lambda item: item.order_id)),
            positions=self.fetch_position_snapshot(),
            mirror_positions=tuple(
                (
                    contract,
                    direction.value,
                    str(quantity),
                    str(average),
                    str(realized),
                    str(last_mark),
                )
                for (contract, direction), (quantity, average, realized, last_mark) in sorted(
                    self._positions.items(), key=lambda item: (item[0][0], item[0][1].value)
                )
            ),
            account=self._account,
            pending_outbox_events=tuple(self._outbox),
        )

    def restore_snapshot(self, snapshot: PaperBrokerSnapshot) -> None:
        if not isinstance(snapshot, PaperBrokerSnapshot):
            raise ValueError("paper broker restore requires a PaperBrokerSnapshot")
        if snapshot.broker_id != self._broker_id:
            raise ValueError("paper broker snapshot belongs to a different broker")
        self._connection_state = snapshot.connection_state
        self._next_sequence = snapshot.next_sequence
        self._orders = {item.order_id: item for item in snapshot.orders}
        self._positions = {
            (contract, PositionDirection(direction)): (
                Decimal(quantity),
                Decimal(average),
                Decimal(realized),
                Decimal(last_mark),
            )
            for contract, direction, quantity, average, realized, last_mark in snapshot.mirror_positions
        }
        self._realized_accumulator = snapshot.account.realized_pnl
        self._account = snapshot.account
        self._outbox = list(snapshot.pending_outbox_events)

    # -- internals -------------------------------------------------------------

    def _emit(self, event_type: BrokerEventType, **payload: Any) -> BrokerEvent:
        event = BrokerEvent(
            event_id=self._event_id(),
            event_type=event_type,
            occurred_at=self._clock(None),
            stream_id=self._stream_id,
            sequence=self._next_sequence,
            order_id=payload.pop("order_id", None),
            client_request_id=payload.pop("client_request_id", None),
            payload=event_pairs(**payload),
        )
        self._next_sequence += 1
        self._outbox.append(event)
        return event

    def _event_id(self) -> str:
        return _canonical_hash(
            {
                "broker_id": self._broker_id,
                "stream_id": self._stream_id,
                "sequence": self._next_sequence,
            }
        )

    @staticmethod
    def _sequence_of(event: BrokerEvent) -> int:
        return event.sequence

    def _clock(self, at: datetime | None) -> datetime:
        if at is not None:
            if at.tzinfo is None:
                raise ValueError("paper broker timestamps must be timezone-aware")
            return at
        return datetime.now(ZoneInfo(self._timezone))

    def _require_order(self, order_id: str) -> PaperBrokerOrder:
        order = self._orders.get(order_id)
        if order is None:
            raise ValueError(f"unknown paper broker order: {order_id}")
        return order

    @staticmethod
    def _with_status(order: PaperBrokerOrder, status: OrderStatus, at: datetime) -> PaperBrokerOrder:
        return PaperBrokerOrder(
            order_id=order.order_id,
            client_request_id=order.client_request_id,
            concrete_contract_id=order.concrete_contract_id,
            direction=order.direction,
            action=order.action,
            order_type=order.order_type,
            quantity=order.quantity,
            limit_price=order.limit_price,
            status=status,
            filled_quantity=order.filled_quantity,
            average_fill_price=order.average_fill_price,
            created_at=order.created_at,
            updated_at=at,
        )

    def _fill_order(self, order_id: str, price: Decimal, at: datetime) -> None:
        order = self._require_order(order_id)
        if type(price) is not Decimal or not price.is_finite() or price <= 0:
            raise ValueError("paper broker fill price must be a positive finite Decimal")
        remaining = order.quantity - order.filled_quantity
        fill_quantity = remaining
        new_filled = order.filled_quantity + fill_quantity
        previous_avg = order.average_fill_price
        if previous_avg is None:
            new_avg = price
        else:
            new_avg = (previous_avg * order.filled_quantity + price * fill_quantity) / new_filled
        new_status = OrderStatus.FILLED if new_filled == order.quantity else OrderStatus.PARTIALLY_FILLED
        self._orders[order_id] = PaperBrokerOrder(
            order_id=order.order_id,
            client_request_id=order.client_request_id,
            concrete_contract_id=order.concrete_contract_id,
            direction=order.direction,
            action=order.action,
            order_type=order.order_type,
            quantity=order.quantity,
            limit_price=order.limit_price,
            status=new_status,
            filled_quantity=new_filled,
            average_fill_price=new_avg,
            created_at=order.created_at,
            updated_at=at,
        )
        self._mirror_fill(order, price, fill_quantity, at)
        self._emit(
            BrokerEventType.ORDER_FILLED,
            order_id=order_id,
            client_request_id=order.client_request_id,
            price=str(price),
            quantity=str(fill_quantity),
            direction=order.direction.value,
            action=order.action.value,
            concrete_contract_id=order.concrete_contract_id,
        )

    def _mirror_fill(
        self,
        order: PaperBrokerOrder,
        price: Decimal,
        quantity: Decimal,
        at: datetime,
    ) -> None:
        spec = self._contract_specs[order.concrete_contract_id]
        multiplier = spec.contract_multiplier
        margin_rate = self._accounting.initial_margin_rate
        key = (order.concrete_contract_id, order.direction)
        held = self._positions.get(key)
        old_quantity = Decimal("0") if held is None else held[0]
        old_average = Decimal("0") if held is None else held[1]
        old_realized = Decimal("0") if held is None else held[2]

        if order.action is OrderAction.OPEN:
            new_quantity = old_quantity + quantity
            new_average = (old_average * old_quantity + price * quantity) / new_quantity
            realized_change = Decimal("0")
        else:
            if quantity > old_quantity:
                raise ValueError("paper broker close exceeds held position quantity")
            new_quantity = old_quantity - quantity
            if order.direction is PositionDirection.LONG:
                realized_change = (price - old_average) * multiplier * quantity
            else:
                realized_change = (old_average - price) * multiplier * quantity
            new_average = old_average if new_quantity > 0 else Decimal("0")
        new_realized = old_realized + realized_change

        if new_quantity > 0:
            self._positions[key] = (new_quantity, new_average, new_realized, price)
        else:
            self._positions.pop(key, None)

        total_reserved = sum(
            (qty * avg * multiplier * margin_rate for _, (qty, avg, _, _) in self._positions.items()),
            Decimal("0"),
        )
        self._realized_accumulator += realized_change
        total_realized = self._realized_accumulator
        total_unrealized = Decimal("0")
        for (contract, direction), (qty, avg, _, last_mark) in self._positions.items():
            spec_i = self._contract_specs[contract]
            if direction is PositionDirection.LONG:
                total_unrealized += (last_mark - avg) * spec_i.contract_multiplier * qty
            else:
                total_unrealized += (avg - last_mark) * spec_i.contract_multiplier * qty
        charged = self._account.charged_costs + self._accounting.additive_cost_per_fill
        self._account = BrokerAccountSnapshot(
            account_id=self._account.account_id,
            snapshot_at=at,
            cash_balance=self._starting_capital + total_realized - charged,
            reserved_margin=total_reserved,
            charged_costs=charged,
            realized_pnl=total_realized,
            unrealized_pnl=total_unrealized,
            currency=self._account.currency,
        )

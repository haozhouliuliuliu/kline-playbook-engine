"""Project-owned BrokerAdapter interface (Shadow Runtime Foundation).

Skeleton v1.0 section 5 requires external execution frameworks to sit behind a
thin project-owned Broker Adapter, so core business logic never binds directly
to a third-party private data structure. This module is that project-owned
interface plus the deterministic snapshot vocabulary used for reconciliation.

The interface is deliberately generic and broker-agnostic: no real TqSdk, CTP,
SimNow, credentials, or network. ``PaperBrokerAdapter`` (``src.paper_broker``)
is the deterministic paper implementation. A future real broker adapter remains
``EXTERNAL_BROKER_GATED``.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Iterable

from src.contract_semantics import OrderAction, PositionDirection
from src.runtime_events import BrokerConnectionState, BrokerEvent

BROKER_ADAPTER_SCHEMA_VERSION = "shadow-runtime-broker-adapter-v0.1"


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def canonical_decimal(value: Decimal) -> str:
    """Canonical finite Decimal text used in durable execution identities."""
    if type(value) is not Decimal or not value.is_finite():
        raise ValueError("canonical decimal requires a finite Decimal")
    normalized = value.normalize()
    text = format(normalized, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in {"-0", ""} else text


class OrderType(str, Enum):
    """Deterministic generic order type vocabulary (broker-agnostic)."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_MARKET = "STOP_MARKET"


class OrderRole(str, Enum):
    """Business role is deliberately separate from the generic order type."""

    GENERIC = "GENERIC"
    ENTRY_STOP = "ENTRY_STOP"
    PROTECTIVE_STOP = "PROTECTIVE_STOP"
    EXIT_STOP = "EXIT_STOP"


@dataclass(frozen=True)
class BrokerOrderInstruction:
    """Deterministic instruction submitted to a broker adapter."""

    client_request_id: str
    concrete_contract_id: str
    direction: PositionDirection
    action: OrderAction
    order_type: OrderType
    quantity: Decimal
    limit_price: Decimal | None = None
    trigger_price: Decimal | None = None
    order_role: OrderRole = OrderRole.GENERIC
    strategy_identity_id: str | None = None
    client_order_id: str | None = None
    created_at: datetime | None = None
    available_at: datetime | None = None
    parent_order_id: str | None = None
    oco_group_id: str | None = None
    replace_generation: int = 0
    source_directive_identity: str | None = None

    def __post_init__(self) -> None:
        if not self.client_request_id or not self.concrete_contract_id:
            raise ValueError("order instruction requires client and contract identities")
        if not isinstance(self.direction, PositionDirection) or not isinstance(self.action, OrderAction):
            raise ValueError("order instruction requires explicit direction and action")
        if not isinstance(self.order_type, OrderType):
            raise ValueError("order instruction requires an explicit order type")
        if type(self.quantity) is not Decimal or not self.quantity.is_finite() or self.quantity <= 0:
            raise ValueError("order instruction quantity must be a positive finite Decimal")
        if self.limit_price is not None:
            if type(self.limit_price) is not Decimal or not self.limit_price.is_finite() or self.limit_price <= 0:
                raise ValueError("order instruction limit price must be a positive finite Decimal")
            if self.order_type is not OrderType.LIMIT:
                raise ValueError("limit price is only valid for a LIMIT order")
        elif self.order_type is OrderType.LIMIT:
            raise ValueError("a LIMIT order requires a limit price")
        if self.trigger_price is not None:
            if type(self.trigger_price) is not Decimal or not self.trigger_price.is_finite() or self.trigger_price <= 0:
                raise ValueError("order trigger price must be a positive finite Decimal")
            if self.order_type is not OrderType.STOP_MARKET:
                raise ValueError("trigger price is only valid for a STOP_MARKET order")
        elif self.order_type is OrderType.STOP_MARKET:
            raise ValueError("a STOP_MARKET order requires a trigger price")
        if not isinstance(self.order_role, OrderRole):
            raise ValueError("order instruction requires an explicit order role")
        if self.order_role is not OrderRole.GENERIC and self.order_type is not OrderType.STOP_MARKET:
            raise ValueError("stop order roles require STOP_MARKET execution type")
        if type(self.replace_generation) is not int or self.replace_generation < 0:
            raise ValueError("replace generation must be a non-negative integer")
        for name, value in (
            ("strategy identity", self.strategy_identity_id),
            ("client order", self.client_order_id),
            ("parent order", self.parent_order_id),
            ("OCO group", self.oco_group_id),
            ("source directive", self.source_directive_identity),
        ):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} identity must be non-empty when supplied")
        for value in (self.created_at, self.available_at):
            if value is not None and value.tzinfo is None:
                raise ValueError("order instruction timestamps must be timezone-aware")
        if self.created_at is not None and self.available_at is not None and self.available_at < self.created_at:
            raise ValueError("order availability cannot precede creation")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "client_request_id": self.client_request_id,
                "concrete_contract_id": self.concrete_contract_id,
                "direction": self.direction.value,
                "action": self.action.value,
                "order_type": self.order_type.value,
                "quantity": canonical_decimal(self.quantity),
                "limit_price": None if self.limit_price is None else canonical_decimal(self.limit_price),
                "trigger_price": None if self.trigger_price is None else canonical_decimal(self.trigger_price),
                "order_role": self.order_role.value,
                "strategy_identity_id": self.strategy_identity_id,
                "client_order_id": self.client_order_id or self.client_request_id,
                "created_at": None if self.created_at is None else self.created_at.isoformat(),
                "available_at": None if self.available_at is None else self.available_at.isoformat(),
                "parent_order_id": self.parent_order_id,
                "oco_group_id": self.oco_group_id,
                "replace_generation": self.replace_generation,
                "source_directive_identity": self.source_directive_identity,
            }
        )


@dataclass(frozen=True)
class BrokerAccountSnapshot:
    """Broker-side account truth used for reconciliation."""

    account_id: str
    snapshot_at: datetime
    cash_balance: Decimal
    reserved_margin: Decimal
    charged_costs: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not self.account_id or not self.currency:
            raise ValueError("broker account snapshot requires account and currency identities")
        if self.snapshot_at.tzinfo is None:
            raise ValueError("broker account snapshot timestamp must be timezone-aware")
        values = (
            self.cash_balance,
            self.reserved_margin,
            self.charged_costs,
            self.realized_pnl,
            self.unrealized_pnl,
        )
        if any(type(value) is not Decimal or not value.is_finite() for value in values):
            raise ValueError("broker account snapshot values must be finite Decimals")
        if self.cash_balance < 0 or self.reserved_margin < 0 or self.charged_costs < 0:
            raise ValueError("broker account snapshot cannot have negative cash, margin or costs")

    @property
    def equity(self) -> Decimal:
        return self.cash_balance + self.unrealized_pnl

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "account_id": self.account_id,
                "snapshot_at": self.snapshot_at.isoformat(),
                "cash_balance": str(self.cash_balance),
                "reserved_margin": str(self.reserved_margin),
                "charged_costs": str(self.charged_costs),
                "realized_pnl": str(self.realized_pnl),
                "unrealized_pnl": str(self.unrealized_pnl),
                "currency": self.currency,
            }
        )


@dataclass(frozen=True)
class BrokerPositionSnapshot:
    """Broker-side position truth used for reconciliation."""

    concrete_contract_id: str
    direction: PositionDirection
    quantity: Decimal
    average_price: Decimal
    snapshot_at: datetime

    def __post_init__(self) -> None:
        if not self.concrete_contract_id or not isinstance(self.direction, PositionDirection):
            raise ValueError("broker position snapshot requires contract and direction identity")
        if self.snapshot_at.tzinfo is None:
            raise ValueError("broker position snapshot timestamp must be timezone-aware")
        if type(self.quantity) is not Decimal or not self.quantity.is_finite() or self.quantity <= 0:
            raise ValueError("broker position quantity must be a positive finite Decimal")
        if type(self.average_price) is not Decimal or not self.average_price.is_finite() or self.average_price <= 0:
            raise ValueError("broker position average price must be a positive finite Decimal")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "concrete_contract_id": self.concrete_contract_id,
                "direction": self.direction.value,
                "quantity": str(self.quantity),
                "average_price": str(self.average_price),
                "snapshot_at": self.snapshot_at.isoformat(),
            }
        )


@dataclass(frozen=True)
class BrokerOrderSnapshot:
    """Broker-side order status truth used for reconciliation."""

    order_id: str
    client_request_id: str
    concrete_contract_id: str
    direction: PositionDirection
    action: OrderAction
    status: str
    requested_quantity: Decimal
    filled_quantity: Decimal
    snapshot_at: datetime
    order_type: OrderType | None = None
    limit_price: Decimal | None = None
    trigger_price: Decimal | None = None
    order_role: OrderRole | None = None
    strategy_identity_id: str | None = None
    client_order_id: str | None = None
    parent_order_id: str | None = None
    oco_group_id: str | None = None
    replace_generation: int | None = None
    source_directive_identity: str | None = None

    def __post_init__(self) -> None:
        required = (self.order_id, self.client_request_id, self.concrete_contract_id, self.status)
        if not all(required):
            raise ValueError("broker order snapshot requires complete identities")
        if not isinstance(self.direction, PositionDirection) or not isinstance(self.action, OrderAction):
            raise ValueError("broker order snapshot requires explicit direction and action")
        if self.status not in {"LIVE", "PARTIALLY_FILLED", "FILLED", "CANCELLED", "REJECTED"}:
            raise ValueError("broker order snapshot has an unknown lifecycle status")
        if self.snapshot_at.tzinfo is None:
            raise ValueError("broker order snapshot timestamp must be timezone-aware")
        if type(self.requested_quantity) is not Decimal or not self.requested_quantity.is_finite() or self.requested_quantity <= 0:
            raise ValueError("broker order requested quantity must be a positive finite Decimal")
        if type(self.filled_quantity) is not Decimal or not self.filled_quantity.is_finite() or self.filled_quantity < 0:
            raise ValueError("broker order filled quantity must be a non-negative finite Decimal")
        if self.filled_quantity > self.requested_quantity:
            raise ValueError("broker order filled quantity cannot exceed requested quantity")
        if self.order_type is not None and not isinstance(self.order_type, OrderType):
            raise ValueError("broker order snapshot order type must be explicit when supplied")
        for value, name in ((self.limit_price, "limit price"), (self.trigger_price, "trigger price")):
            if value is not None and (
                type(value) is not Decimal or not value.is_finite() or value <= 0
            ):
                raise ValueError(f"broker order snapshot {name} must be positive finite Decimal")
        if self.order_role is not None and not isinstance(self.order_role, OrderRole):
            raise ValueError("broker order snapshot role must be explicit when supplied")
        if self.replace_generation is not None and (
            type(self.replace_generation) is not int or self.replace_generation < 0
        ):
            raise ValueError("broker order snapshot replace generation must be non-negative")
        for value, name in (
            (self.strategy_identity_id, "strategy identity"),
            (self.client_order_id, "client order identity"),
            (self.parent_order_id, "parent order identity"),
            (self.oco_group_id, "OCO identity"),
            (self.source_directive_identity, "source directive identity"),
        ):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"broker order snapshot {name} must be non-empty when supplied")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "order_id": self.order_id,
                "client_request_id": self.client_request_id,
                "concrete_contract_id": self.concrete_contract_id,
                "direction": self.direction.value,
                "action": self.action.value,
                "status": self.status,
                "requested_quantity": canonical_decimal(self.requested_quantity),
                "filled_quantity": canonical_decimal(self.filled_quantity),
                "snapshot_at": self.snapshot_at.isoformat(),
                "order_type": None if self.order_type is None else self.order_type.value,
                "limit_price": None if self.limit_price is None else canonical_decimal(self.limit_price),
                "trigger_price": None if self.trigger_price is None else canonical_decimal(self.trigger_price),
                "order_role": None if self.order_role is None else self.order_role.value,
                "strategy_identity_id": self.strategy_identity_id,
                "client_order_id": self.client_order_id,
                "parent_order_id": self.parent_order_id,
                "oco_group_id": self.oco_group_id,
                "replace_generation": self.replace_generation,
                "source_directive_identity": self.source_directive_identity,
            }
        )


class BrokerAdapter(ABC):
    """Thin project-owned broker interface (deterministic, no network).

    A real broker implementation (TqSdk/CTP/SimNow/credentials) is out of scope
    for this foundation package and remains EXTERNAL_BROKER_GATED. The paper
    adapter must implement this exact surface so core logic never binds to a
    third-party private structure.
    """

    @property
    @abstractmethod
    def broker_id(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def connection_state(self) -> BrokerConnectionState:
        raise NotImplementedError

    @abstractmethod
    def connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def disconnect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def submit_order(self, instruction: BrokerOrderInstruction) -> str:
        """Submit one order; returns the broker-assigned ``order_id``."""
        raise NotImplementedError

    @abstractmethod
    def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def replace_order(self, order_id: str, new_quantity: Decimal) -> None:
        raise NotImplementedError

    @abstractmethod
    def drain_events(self) -> tuple[BrokerEvent, ...]:
        """Return and clear the pending deterministic broker event outbox."""
        raise NotImplementedError

    @abstractmethod
    def fetch_account_snapshot(self) -> BrokerAccountSnapshot:
        raise NotImplementedError

    @abstractmethod
    def fetch_position_snapshot(self) -> tuple[BrokerPositionSnapshot, ...]:
        raise NotImplementedError

    @abstractmethod
    def fetch_order_snapshot(self) -> tuple[BrokerOrderSnapshot, ...]:
        raise NotImplementedError

    @abstractmethod
    def capture_snapshot(self) -> Any:
        """Deterministic broker-side snapshot fixture for restart recovery."""
        raise NotImplementedError

    @abstractmethod
    def restore_snapshot(self, snapshot: Any) -> None:
        raise NotImplementedError


def iterate_snapshots(positions: Iterable[BrokerPositionSnapshot]) -> tuple[BrokerPositionSnapshot, ...]:
    """Deterministic ordering helper for broker position snapshots."""
    return tuple(sorted(positions, key=lambda item: (item.concrete_contract_id, item.direction.value)))

"""TradingState — the sole authoritative mutable real-time state owner.

Skeleton v1.0 section 5 (Trading Loop) requires:

- ``TradingState`` is the only authoritative mutable local real-time state
  owner; strategies receive immutable snapshots for intent computation;
- broker events require unique ``event_id``, idempotent application,
  deduplication, defined out-of-order handling and sequence/stream conventions;
- broker/exchange facts override local inference;
- crash/restart rebuilds state from persistent facts plus broker reconciliation.

This module implements exactly that, in a deterministic, broker-agnostic way.
It owns the mutable account, positions, broker-known order statuses, the applied
broker event log, sequence discipline and connection state. It writes immutable
records to the injected ``RuntimeLedger`` (the ledger records what happened; it
does not own live state).

No real broker, no network, no candidate outcome, no real money. The accounting
uses the same Decimal/timezone/identity conventions as the rest of the project.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Iterable

from src.contract_semantics import ContractSpecification, OrderAction, PositionDirection
from src.runtime_events import (
    BrokerConnectionState,
    BrokerEvent,
    BrokerEventLog,
    BrokerEventType,
    BrokerEventViolation,
    BrokerEventViolationKind,
    event_pairs,
)
from src.runtime_ledger import (
    RuntimeLedger,
    RuntimeLedgerRecord,
    RuntimeLedgerRecordKind,
    ledger_pairs,
)

TRADING_STATE_SCHEMA_VERSION = "shadow-runtime-trading-state-v0.1"

# ORDER_FILLED / ORDER_SUBMITTED payload keys.
PAYLOAD_ACTION = "action"
PAYLOAD_DIRECTION = "direction"
PAYLOAD_QUANTITY = "quantity"
PAYLOAD_PRICE = "price"
PAYLOAD_CONTRACT = "concrete_contract_id"
PAYLOAD_ORDER_TYPE = "order_type"
PAYLOAD_LIMIT_PRICE = "limit_price"
PAYLOAD_NEW_QUANTITY = "new_quantity"
PAYLOAD_CONNECTION_STATE = "connection_state"


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class OrderStatus(str, Enum):
    """Deterministic order lifecycle status (client + broker-confirmed view)."""

    PENDING_SUBMIT = "PENDING_SUBMIT"
    RESTING = "RESTING"
    TRIGGERED = "TRIGGERED"
    LIVE = "LIVE"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    REPLACED = "REPLACED"
    CANCEL_PENDING = "CANCEL_PENDING"
    REPLACE_PENDING = "REPLACE_PENDING"
    AMBIGUOUS = "AMBIGUOUS_INTRABAR_SEQUENCE"


class EventApplicationOutcome(str, Enum):
    """Deterministic outcome of one broker event application attempt."""

    APPLIED = "APPLIED"
    APPLIED_ALREADY_NOOP = "APPLIED_ALREADY_NOOP"
    REJECTED_DUPLICATE_EVENT_ID_DIFFERENT_CONTENT = (
        "REJECTED_DUPLICATE_EVENT_ID_DIFFERENT_CONTENT"
    )
    REJECTED_OUT_OF_ORDER = "REJECTED_OUT_OF_ORDER"
    REJECTED_SEQUENCE_GAP = "REJECTED_SEQUENCE_GAP"
    REJECTED_INVALID_CONTENT = "REJECTED_INVALID_CONTENT"


@dataclass(frozen=True)
class RuntimeAccountingAssumptions:
    """Versioned deterministic paper accounting facts (FIXTURE-ONLY, no money).

    These are generic synthetic engineering numbers used by the deterministic
    paper runtime. They are explicitly NOT permanent real-money risk limits or
    real fee/margin schedules.
    """

    model_version: str
    initial_margin_rate: Decimal
    maintenance_margin_rate: Decimal
    additive_cost_per_fill: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not self.model_version or not self.currency:
            raise ValueError("accounting model version and currency are required")
        values = (self.initial_margin_rate, self.maintenance_margin_rate, self.additive_cost_per_fill)
        if any(type(value) is not Decimal or not value.is_finite() or value < 0 for value in values):
            raise ValueError("accounting rates and costs must be non-negative finite Decimals")
        if not Decimal("0") < self.initial_margin_rate <= Decimal("1"):
            raise ValueError("initial margin rate must be a Decimal in (0, 1]")
        if not Decimal("0") < self.maintenance_margin_rate <= self.initial_margin_rate:
            raise ValueError("maintenance margin rate must be a Decimal in (0, initial margin rate]")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "model_version": self.model_version,
                "initial_margin_rate": str(self.initial_margin_rate),
                "maintenance_margin_rate": str(self.maintenance_margin_rate),
                "additive_cost_per_fill": str(self.additive_cost_per_fill),
                "currency": self.currency,
            }
        )


@dataclass(frozen=True)
class AccountState:
    """Immutable account projection (replaced on each mutation)."""

    starting_capital: Decimal
    reserved_margin: Decimal
    charged_costs: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    updated_at: datetime

    def __post_init__(self) -> None:
        values = (
            self.starting_capital,
            self.reserved_margin,
            self.charged_costs,
            self.realized_pnl,
            self.unrealized_pnl,
        )
        if any(type(value) is not Decimal or not value.is_finite() for value in values):
            raise ValueError("account state values must be finite Decimals")
        if self.starting_capital <= 0 or self.reserved_margin < 0 or self.charged_costs < 0:
            raise ValueError("account state cannot be non-positive or over-reserved")
        if self.updated_at.tzinfo is None:
            raise ValueError("account state timestamp must be timezone-aware")

    @property
    def cash_balance(self) -> Decimal:
        return self.starting_capital + self.realized_pnl - self.charged_costs

    @property
    def equity(self) -> Decimal:
        return self.cash_balance + self.unrealized_pnl

    @property
    def available_capital(self) -> Decimal:
        return self.cash_balance - self.reserved_margin

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "starting_capital": str(self.starting_capital),
                "reserved_margin": str(self.reserved_margin),
                "charged_costs": str(self.charged_costs),
                "realized_pnl": str(self.realized_pnl),
                "unrealized_pnl": str(self.unrealized_pnl),
                "updated_at": self.updated_at.isoformat(),
            }
        )


@dataclass(frozen=True)
class PositionState:
    """Immutable per-(contract, direction) position projection."""

    concrete_contract_id: str
    direction: PositionDirection
    quantity: Decimal
    average_open_price: Decimal
    reserved_margin: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    last_mark_price: Decimal
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.concrete_contract_id or not isinstance(self.direction, PositionDirection):
            raise ValueError("position state requires contract and direction identity")
        if self.updated_at.tzinfo is None:
            raise ValueError("position state timestamp must be timezone-aware")
        if type(self.quantity) is not Decimal or not self.quantity.is_finite() or self.quantity <= 0:
            raise ValueError("position quantity must be a positive finite Decimal")
        if type(self.average_open_price) is not Decimal or not self.average_open_price.is_finite() or self.average_open_price <= 0:
            raise ValueError("position average open price must be a positive finite Decimal")
        if type(self.last_mark_price) is not Decimal or not self.last_mark_price.is_finite() or self.last_mark_price <= 0:
            raise ValueError("position last mark price must be a positive finite Decimal")
        for value in (self.reserved_margin, self.realized_pnl, self.unrealized_pnl):
            if type(value) is not Decimal or not value.is_finite():
                raise ValueError("position accounting values must be finite Decimals")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "concrete_contract_id": self.concrete_contract_id,
                "direction": self.direction.value,
                "quantity": str(self.quantity),
                "average_open_price": str(self.average_open_price),
                "reserved_margin": str(self.reserved_margin),
                "realized_pnl": str(self.realized_pnl),
                "unrealized_pnl": str(self.unrealized_pnl),
                "last_mark_price": str(self.last_mark_price),
                "updated_at": self.updated_at.isoformat(),
            }
        )


@dataclass(frozen=True)
class RuntimeOrderState:
    """Broker-confirmed order facts mirrored inside TradingState."""

    order_id: str
    client_request_id: str
    concrete_contract_id: str
    direction: PositionDirection
    action: OrderAction
    status: OrderStatus
    requested_quantity: Decimal
    filled_quantity: Decimal
    average_fill_price: Decimal | None
    last_event_id: str
    updated_at: datetime

    def __post_init__(self) -> None:
        required = (self.order_id, self.client_request_id, self.concrete_contract_id, self.last_event_id)
        if not all(required):
            raise ValueError("runtime order state requires complete identities")
        if not isinstance(self.direction, PositionDirection) or not isinstance(self.action, OrderAction):
            raise ValueError("runtime order state requires explicit direction and action")
        if not isinstance(self.status, OrderStatus):
            raise ValueError("runtime order state requires an OrderStatus")
        if self.updated_at.tzinfo is None:
            raise ValueError("runtime order state timestamp must be timezone-aware")
        if type(self.requested_quantity) is not Decimal or not self.requested_quantity.is_finite() or self.requested_quantity <= 0:
            raise ValueError("runtime order requested quantity must be a positive finite Decimal")
        if type(self.filled_quantity) is not Decimal or not self.filled_quantity.is_finite() or self.filled_quantity < 0:
            raise ValueError("runtime order filled quantity must be a non-negative finite Decimal")
        if self.filled_quantity > self.requested_quantity:
            raise ValueError("runtime order cannot be filled beyond its requested quantity")
        if self.average_fill_price is not None and (
            type(self.average_fill_price) is not Decimal or not self.average_fill_price.is_finite() or self.average_fill_price <= 0
        ):
            raise ValueError("runtime order average fill price must be a positive finite Decimal")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "order_id": self.order_id,
                "client_request_id": self.client_request_id,
                "concrete_contract_id": self.concrete_contract_id,
                "direction": self.direction.value,
                "action": self.action.value,
                "status": self.status.value,
                "requested_quantity": str(self.requested_quantity),
                "filled_quantity": str(self.filled_quantity),
                "average_fill_price": (
                    None if self.average_fill_price is None else str(self.average_fill_price)
                ),
                "last_event_id": self.last_event_id,
                "updated_at": self.updated_at.isoformat(),
            }
        )


@dataclass(frozen=True)
class EventApplicationResult:
    """Deterministic result of applying one broker event to TradingState."""

    outcome: EventApplicationOutcome
    event: BrokerEvent
    ledger_record_identities: tuple[str, ...] = ()
    violation: BrokerEventViolation | None = None
    applied_event_log_identity: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.outcome, EventApplicationOutcome):
            raise ValueError("event application outcome must be an EventApplicationOutcome")
        if not isinstance(self.event, BrokerEvent):
            raise ValueError("event application result requires a BrokerEvent")
        if not isinstance(self.ledger_record_identities, tuple):
            raise ValueError("ledger record identities must be a tuple")

    @property
    def applied(self) -> bool:
        return self.outcome is EventApplicationOutcome.APPLIED


def _payload_value(payload: tuple[tuple[str, str], ...], key: str) -> str | None:
    for name, value in payload:
        if name == key:
            return value
    return None


def _require_payload(payload: tuple[tuple[str, str], ...], key: str) -> str:
    value = _payload_value(payload, key)
    if value is None:
        raise ValueError(f"broker event payload missing required key: {key}")
    return value


def _payload_decimal(payload: tuple[tuple[str, str], ...], key: str) -> Decimal:
    value = _require_payload(payload, key)
    try:
        return Decimal(value)
    except Exception as exc:  # noqa: BLE001 - deterministic conversion guard
        raise ValueError(f"broker event payload {key} is not a Decimal") from exc


class TradingState:
    """Sole authoritative mutable local real-time state owner (deterministic).

    Mutable state here:
    - account (immutable ``AccountState`` projections, replaced on mutation);
    - positions (per ``(concrete_contract_id, direction)``);
    - broker-confirmed order statuses (``RuntimeOrderState``);
    - applied broker event log + per-stream sequence high water;
    - broker connection state.

    Broker event application is idempotent and deduplicated by ``event_id`` and
    strictly sequenced per stream; any violation is recorded (and surfaced to
    Safety) instead of corrupting state.
    """

    def __init__(
        self,
        *,
        runtime_id: str,
        runtime_version: str,
        created_at: datetime,
        starting_capital: Decimal,
        contract_specs: Iterable[ContractSpecification],
        accounting: RuntimeAccountingAssumptions,
        ledger: RuntimeLedger,
        connection_state: BrokerConnectionState = BrokerConnectionState.CONNECTED,
    ) -> None:
        if not runtime_id or not runtime_version:
            raise ValueError("runtime id and version are required")
        if created_at.tzinfo is None:
            raise ValueError("runtime created timestamp must be timezone-aware")
        if type(starting_capital) is not Decimal or not starting_capital.is_finite() or starting_capital <= 0:
            raise ValueError("starting capital must be a positive finite Decimal")
        if not isinstance(accounting, RuntimeAccountingAssumptions):
            raise ValueError("runtime requires RuntimeAccountingAssumptions")
        if not isinstance(ledger, RuntimeLedger):
            raise ValueError("runtime requires a RuntimeLedger")
        if not isinstance(connection_state, BrokerConnectionState):
            raise ValueError("connection state must be a BrokerConnectionState")
        specs = tuple(contract_specs)
        if not specs or any(not isinstance(item, ContractSpecification) for item in specs):
            raise ValueError("runtime requires ContractSpecification values")
        if len({item.instrument_id for item in specs}) != len(specs):
            raise ValueError("runtime contract specifications must have unique instrument ids")

        self._runtime_id = runtime_id
        self._runtime_version = runtime_version
        self._created_at = created_at
        self._starting_capital = starting_capital
        self._contract_specs = {item.instrument_id: item for item in specs}
        self._accounting = accounting
        self._ledger = ledger
        self._connection_state = connection_state

        self._account = AccountState(
            starting_capital=starting_capital,
            reserved_margin=Decimal("0"),
            charged_costs=Decimal("0"),
            realized_pnl=Decimal("0"),
            unrealized_pnl=Decimal("0"),
            updated_at=created_at,
        )
        self._positions: dict[tuple[str, PositionDirection], PositionState] = {}
        self._orders: dict[str, RuntimeOrderState] = {}
        self._applied: dict[str, BrokerEvent] = {}
        self._applied_order: list[BrokerEvent] = []
        self._high_water: dict[str, int] = {}
        self._violations: list[BrokerEventViolation] = []
        self._realized_accumulator = Decimal("0")
        self._last_account_snapshot: tuple[tuple[str, str], ...] | None = None
        self._last_position_snapshots: tuple[tuple[tuple[str, str], ...], ...] = ()
        self._last_order_snapshots: tuple[tuple[tuple[str, str], ...], ...] = ()

    # -- read-only views ------------------------------------------------------

    @property
    def runtime_id(self) -> str:
        return self._runtime_id

    @property
    def runtime_version(self) -> str:
        return self._runtime_version

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def starting_capital(self) -> Decimal:
        return self._starting_capital

    @property
    def accounting(self) -> RuntimeAccountingAssumptions:
        return self._accounting

    @property
    def account(self) -> AccountState:
        return self._account

    @property
    def positions(self) -> tuple[PositionState, ...]:
        return tuple(sorted(self._positions.values(), key=lambda item: (item.concrete_contract_id, item.direction.value)))

    def position_for(self, concrete_contract_id: str, direction: PositionDirection) -> PositionState | None:
        return self._positions.get((concrete_contract_id, direction))

    @property
    def orders(self) -> tuple[RuntimeOrderState, ...]:
        return tuple(sorted(self._orders.values(), key=lambda item: item.order_id))

    def order_for(self, order_id: str) -> RuntimeOrderState | None:
        return self._orders.get(order_id)

    @property
    def connection_state(self) -> BrokerConnectionState:
        return self._connection_state

    @property
    def ledger_tail_identity(self) -> str:
        return self._ledger.tail_identity

    def contract_spec(self, concrete_contract_id: str) -> ContractSpecification | None:
        return self._contract_specs.get(concrete_contract_id)

    @property
    def contract_specifications(self) -> tuple[ContractSpecification, ...]:
        return tuple(
            self._contract_specs[key] for key in sorted(self._contract_specs)
        )

    def runtime_ledger_records(self) -> tuple[RuntimeLedgerRecord, ...]:
        """Read-only immutable ledger projection for restart-integrity checks."""
        return self._ledger.records()

    def runtime_ledger_chain_valid(self) -> bool:
        return self._ledger.verify_chain()

    @property
    def runtime_ledger_next_sequence(self) -> int:
        return self._ledger.next_sequence

    @property
    def runtime_ledger_anchor(self) -> tuple[int, str]:
        return self._ledger.anchor_sequence, self._ledger.anchor_identity

    def is_genuinely_fresh(self) -> bool:
        return (
            not self._positions
            and not self._orders
            and not self._applied
            and not self._violations
            and self._ledger.count() == 0
            and self._ledger.anchor_sequence == 0
            and self._account
            == AccountState(
                starting_capital=self._starting_capital,
                reserved_margin=Decimal("0"),
                charged_costs=Decimal("0"),
                realized_pnl=Decimal("0"),
                unrealized_pnl=Decimal("0"),
                updated_at=self._created_at,
            )
        )

    def restore_journal_start_checkpoint(
        self,
        *,
        account: AccountState,
        positions: Iterable[PositionState],
        ledger_anchor_sequence: int,
        ledger_anchor_identity: str,
    ) -> None:
        """Restore a proven journal-start checkpoint into a fresh state only."""
        if not self.is_genuinely_fresh():
            raise ValueError("journal checkpoint restore requires genuinely fresh state")
        if not isinstance(account, AccountState):
            raise ValueError("journal checkpoint restore requires AccountState")
        restored_positions = tuple(positions)
        if any(not isinstance(item, PositionState) for item in restored_positions):
            raise ValueError("journal checkpoint restore requires PositionState values")
        position_keys = {
            (item.concrete_contract_id, item.direction) for item in restored_positions
        }
        if len(position_keys) != len(restored_positions):
            raise ValueError("journal checkpoint positions must have unique identities")
        if account.starting_capital != self._starting_capital:
            raise ValueError("journal checkpoint starting capital conflicts with runtime")
        self._ledger.restore_anchor(
            sequence=ledger_anchor_sequence,
            identity=ledger_anchor_identity,
        )
        self._account = account
        self._realized_accumulator = account.realized_pnl
        self._positions = {
            (item.concrete_contract_id, item.direction): item
            for item in restored_positions
        }

    def applied_event_ids(self) -> tuple[str, ...]:
        return tuple(event.event_id for event in self._applied_order)

    def applied_events(self) -> tuple[BrokerEvent, ...]:
        return tuple(self._applied_order)

    def stream_high_water(self) -> tuple[tuple[str, int], ...]:
        return tuple(sorted(self._high_water.items()))

    def event_violations(self) -> tuple[BrokerEventViolation, ...]:
        return tuple(self._violations)

    def event_log_projection(self) -> BrokerEventLog:
        """Immutable deterministic projection of the applied event log."""
        return BrokerEventLog(
            applied_events=tuple(self._applied_order),
            event_violations=tuple(self._violations),
        )

    @property
    def last_account_snapshot(self) -> tuple[tuple[str, str], ...] | None:
        return self._last_account_snapshot

    @property
    def last_position_snapshots(self) -> tuple[tuple[tuple[str, str], ...], ...]:
        return self._last_position_snapshots

    @property
    def last_order_snapshots(self) -> tuple[tuple[tuple[str, str], ...], ...]:
        return self._last_order_snapshots

    # -- crash / restart recovery ---------------------------------------------

    @classmethod
    def restore(
        cls,
        *,
        runtime_id: str,
        runtime_version: str,
        created_at: datetime,
        starting_capital: Decimal,
        contract_specs: Iterable[ContractSpecification],
        accounting: RuntimeAccountingAssumptions,
        ledger: RuntimeLedger,
        account: AccountState,
        positions: Iterable[PositionState],
        orders: Iterable[RuntimeOrderState],
        applied_events: Iterable[BrokerEvent],
        event_violations: Iterable[BrokerEventViolation],
        connection_state: BrokerConnectionState,
    ) -> "TradingState":
        """Rebuild a ``TradingState`` from persisted facts WITHOUT re-applying
        events (Skeleton v1.0 §5: crash/restart rebuilds from persistent facts
        plus broker reconciliation). The restored state continues the event log
        from the persisted applied events / high-water marks, so new broker
        events keep strict dedup and sequence discipline.
        """
        restored = cls(
            runtime_id=runtime_id,
            runtime_version=runtime_version,
            created_at=created_at,
            starting_capital=starting_capital,
            contract_specs=contract_specs,
            accounting=accounting,
            ledger=ledger,
            connection_state=connection_state,
        )
        restored._account = account
        restored._realized_accumulator = account.realized_pnl
        restored._positions = {
            (item.concrete_contract_id, item.direction): item for item in positions
        }
        restored._orders = {item.order_id: item for item in orders}
        applied = tuple(applied_events)
        restored._applied = {event.event_id: event for event in applied}
        restored._applied_order = list(applied)
        restored._high_water = {}
        for event in applied:
            previous = restored._high_water.get(event.stream_id, -1)
            restored._high_water[event.stream_id] = max(previous, event.sequence)
        restored._violations = list(event_violations)
        return restored

    # -- broker event application --------------------------------------------

    def apply_broker_event(self, event: BrokerEvent) -> EventApplicationResult:
        """Apply one broker event idempotently and deterministically."""
        if not isinstance(event, BrokerEvent):
            raise ValueError("TradingState requires a BrokerEvent")

        # 1. Deduplication by event_id.
        existing = self._applied.get(event.event_id)
        if existing is not None:
            if existing.identity_id == event.identity_id:
                return EventApplicationResult(
                    outcome=EventApplicationOutcome.APPLIED_ALREADY_NOOP,
                    event=event,
                    applied_event_log_identity=self.event_log_projection().identity_id,
                )
            return self._reject(
                event,
                BrokerEventViolationKind.DUPLICATE_EVENT_ID_DIFFERENT_CONTENT,
                "event_id already applied with different content",
                EventApplicationOutcome.REJECTED_DUPLICATE_EVENT_ID_DIFFERENT_CONTENT,
            )

        # 2. Per-stream strict sequence discipline.
        high_water = self._high_water.get(event.stream_id, -1)
        if event.sequence <= high_water:
            return self._reject(
                event,
                BrokerEventViolationKind.OUT_OF_ORDER,
                f"sequence {event.sequence} <= high water {high_water} for stream {event.stream_id}",
                EventApplicationOutcome.REJECTED_OUT_OF_ORDER,
            )
        if event.sequence > high_water + 1:
            return self._reject(
                event,
                BrokerEventViolationKind.SEQUENCE_GAP,
                f"sequence {event.sequence} > high water {high_water} + 1 for stream {event.stream_id}",
                EventApplicationOutcome.REJECTED_SEQUENCE_GAP,
            )

        # 3. Content application (fail closed into an INVALID_CONTENT violation).
        try:
            ledger_ids = self._dispatch(event)
        except ValueError as exc:
            return self._reject(
                event,
                BrokerEventViolationKind.INVALID_CONTENT,
                str(exc),
                EventApplicationOutcome.REJECTED_INVALID_CONTENT,
            )

        # 4. Commit the event to the applied log (only after successful apply).
        self._applied[event.event_id] = event
        self._applied_order.append(event)
        self._high_water[event.stream_id] = event.sequence
        ledger_ids.append(
            self._ledger.append(
                RuntimeLedgerRecordKind.BROKER_EVENT,
                event.event_id,
                ledger_pairs(
                    event_type=event.event_type.value,
                    stream_id=event.stream_id,
                    sequence=event.sequence,
                    occurred_at=event.occurred_at.isoformat(),
                    order_id=event.order_id,
                    client_request_id=event.client_request_id,
                    event_identity=event.identity_id,
                ),
                event.occurred_at,
            ).identity_id
        )
        return EventApplicationResult(
            outcome=EventApplicationOutcome.APPLIED,
            event=event,
            ledger_record_identities=tuple(ledger_ids),
            applied_event_log_identity=self.event_log_projection().identity_id,
        )

    def _reject(
        self,
        event: BrokerEvent,
        kind: BrokerEventViolationKind,
        detail: str,
        outcome: EventApplicationOutcome,
    ) -> EventApplicationResult:
        violation = BrokerEventViolation(
            violation_id=_canonical_hash(
                {
                    "event": event.identity_id,
                    "kind": kind.value,
                    "detail": detail,
                    "detected_at": event.occurred_at.isoformat(),
                }
            ),
            event=event,
            kind=kind,
            detail=detail,
            detected_at=event.occurred_at,
        )
        self._violations.append(violation)
        return EventApplicationResult(
            outcome=outcome,
            event=event,
            violation=violation,
            applied_event_log_identity=self.event_log_projection().identity_id,
        )

    def _dispatch(self, event: BrokerEvent) -> list[str]:
        """Apply event content; returns ledger record identities appended."""
        handler = {
            BrokerEventType.ORDER_SUBMITTED: self._apply_order_submitted,
            BrokerEventType.ORDER_TRIGGERED: self._apply_order_triggered,
            BrokerEventType.ORDER_AMBIGUOUS: self._apply_order_ambiguous,
            BrokerEventType.ORDER_FILLED: self._apply_order_filled,
            BrokerEventType.ORDER_CANCELLED: self._apply_order_cancelled,
            BrokerEventType.ORDER_REJECTED: self._apply_order_rejected,
            BrokerEventType.ORDER_REPLACED: self._apply_order_replaced,
            BrokerEventType.CONNECTION_STATE: self._apply_connection_state,
            BrokerEventType.ACCOUNT_SNAPSHOT: self._apply_account_snapshot,
            BrokerEventType.POSITION_SNAPSHOT: self._apply_position_snapshot,
            BrokerEventType.ORDER_SNAPSHOT: self._apply_order_snapshot,
        }
        handler_fn = handler.get(event.event_type)
        if handler_fn is None:
            raise ValueError(f"unsupported broker event type: {event.event_type.value}")
        return handler_fn(event)

    # -- per-type application -------------------------------------------------

    def _apply_order_submitted(self, event: BrokerEvent) -> list[str]:
        if event.order_id is None or event.client_request_id is None:
            raise ValueError("ORDER_SUBMITTED requires order_id and client_request_id")
        contract = _require_payload(event.payload, PAYLOAD_CONTRACT)
        if contract not in self._contract_specs:
            raise ValueError("ORDER_SUBMITTED references an unknown concrete contract")
        direction = PositionDirection(_require_payload(event.payload, PAYLOAD_DIRECTION))
        action = OrderAction(_require_payload(event.payload, PAYLOAD_ACTION))
        quantity = _payload_decimal(event.payload, PAYLOAD_QUANTITY)
        if quantity <= 0:
            raise ValueError("ORDER_SUBMITTED requires positive quantity")
        existing = self._orders.get(event.order_id)
        if existing is not None:
            if (
                existing.client_request_id != event.client_request_id
                or existing.concrete_contract_id != contract
                or existing.direction is not direction
                or existing.action is not action
                or existing.requested_quantity != quantity
            ):
                raise ValueError("ORDER_SUBMITTED acknowledgement conflicts with existing order")
            acknowledged_status = OrderStatus(
                _payload_value(event.payload, "lifecycle_status") or OrderStatus.LIVE.value
            )
            status = (
                existing.status
                if existing.status in {OrderStatus.PARTIALLY_FILLED, OrderStatus.FILLED}
                else acknowledged_status
            )
            self._orders[event.order_id] = RuntimeOrderState(
                order_id=existing.order_id,
                client_request_id=existing.client_request_id,
                concrete_contract_id=existing.concrete_contract_id,
                direction=existing.direction,
                action=existing.action,
                status=status,
                requested_quantity=existing.requested_quantity,
                filled_quantity=existing.filled_quantity,
                average_fill_price=existing.average_fill_price,
                last_event_id=event.event_id,
                updated_at=event.occurred_at,
            )
            return [
                self._ledger.append(
                    RuntimeLedgerRecordKind.ORDER,
                    event.order_id,
                    ledger_pairs(
                        order_id=event.order_id,
                        client_request_id=event.client_request_id,
                        status=status.value,
                    ),
                    event.occurred_at,
                ).identity_id
            ]
        self._orders[event.order_id] = RuntimeOrderState(
            order_id=event.order_id,
            client_request_id=event.client_request_id,
            concrete_contract_id=contract,
            direction=direction,
            action=action,
            status=OrderStatus(_payload_value(event.payload, "lifecycle_status") or OrderStatus.LIVE.value),
            requested_quantity=quantity,
            filled_quantity=Decimal("0"),
            average_fill_price=None,
            last_event_id=event.event_id,
            updated_at=event.occurred_at,
        )
        return [
            self._ledger.append(
                RuntimeLedgerRecordKind.ORDER,
                event.order_id,
                ledger_pairs(
                    order_id=event.order_id,
                    client_request_id=event.client_request_id,
                    concrete_contract_id=contract,
                    direction=direction.value,
                    action=action.value,
                    requested_quantity=str(quantity),
                    status=(_payload_value(event.payload, "lifecycle_status") or OrderStatus.LIVE.value),
                ),
                event.occurred_at,
            ).identity_id
        ]

    def _apply_order_filled(self, event: BrokerEvent) -> list[str]:
        if event.order_id is None:
            raise ValueError("ORDER_FILLED requires order_id")
        order = self._orders.get(event.order_id)
        if order is None:
            raise ValueError("ORDER_FILLED references an unknown order")
        contract = _require_payload(event.payload, PAYLOAD_CONTRACT)
        if contract != order.concrete_contract_id:
            raise ValueError("ORDER_FILLED contract disagrees with the order")
        direction = PositionDirection(_require_payload(event.payload, PAYLOAD_DIRECTION))
        if direction is not order.direction:
            raise ValueError("ORDER_FILLED direction disagrees with the order")
        action = OrderAction(_require_payload(event.payload, PAYLOAD_ACTION))
        if action is not order.action:
            raise ValueError("ORDER_FILLED action disagrees with the order")
        price = _payload_decimal(event.payload, PAYLOAD_PRICE)
        quantity = _payload_decimal(event.payload, PAYLOAD_QUANTITY)
        if price <= 0 or quantity <= 0:
            raise ValueError("ORDER_FILLED requires positive price and quantity")
        new_filled = order.filled_quantity + quantity
        if new_filled > order.requested_quantity:
            raise ValueError("ORDER_FILLED would over-fill the order")
        previous_avg = order.average_fill_price
        if previous_avg is None:
            new_avg = price
        else:
            new_avg = (previous_avg * order.filled_quantity + price * quantity) / new_filled
        if new_filled == order.requested_quantity:
            new_status = OrderStatus.FILLED
        else:
            new_status = OrderStatus.PARTIALLY_FILLED

        ledger_ids = self._apply_position_effect(
            contract=order.concrete_contract_id,
            direction=order.direction,
            action=order.action,
            price=price,
            quantity=quantity,
            event=event,
        )
        # Single additive-cost authority: exactly one fixture cost is charged
        # per filled order event (FIXTURE-ONLY number, not a permanent fee).
        cost = self._accounting.additive_cost_per_fill
        if cost > 0:
            self._account = AccountState(
                starting_capital=self._account.starting_capital,
                reserved_margin=self._account.reserved_margin,
                realized_pnl=self._account.realized_pnl,
                unrealized_pnl=self._account.unrealized_pnl,
                charged_costs=self._account.charged_costs + cost,
                updated_at=event.occurred_at,
            )
        ledger_ids.append(
            self._ledger.append(
                RuntimeLedgerRecordKind.FILL,
                event.event_id,
                ledger_pairs(
                    order_id=order.order_id,
                    client_request_id=order.client_request_id,
                    concrete_contract_id=contract,
                    direction=direction.value,
                    action=action.value,
                    price=str(price),
                    quantity=str(quantity),
                    additive_cost=str(cost),
                    fill_status=new_status.value,
                ),
                event.occurred_at,
            ).identity_id
        )
        self._orders[order.order_id] = RuntimeOrderState(
            order_id=order.order_id,
            client_request_id=order.client_request_id,
            concrete_contract_id=order.concrete_contract_id,
            direction=order.direction,
            action=order.action,
            status=new_status,
            requested_quantity=order.requested_quantity,
            filled_quantity=new_filled,
            average_fill_price=new_avg,
            last_event_id=event.event_id,
            updated_at=event.occurred_at,
        )
        return ledger_ids

    def _apply_order_triggered(self, event: BrokerEvent) -> list[str]:
        if event.order_id is None:
            raise ValueError("ORDER_TRIGGERED requires order_id")
        order = self._orders.get(event.order_id)
        if order is None or order.status not in (OrderStatus.RESTING, OrderStatus.LIVE):
            raise ValueError("ORDER_TRIGGERED requires a resting order")
        self._orders[event.order_id] = RuntimeOrderState(
            order_id=order.order_id, client_request_id=order.client_request_id,
            concrete_contract_id=order.concrete_contract_id, direction=order.direction,
            action=order.action, status=OrderStatus.TRIGGERED,
            requested_quantity=order.requested_quantity, filled_quantity=order.filled_quantity,
            average_fill_price=order.average_fill_price, last_event_id=event.event_id,
            updated_at=event.occurred_at,
        )
        return [self._ledger.append(RuntimeLedgerRecordKind.ORDER, event.order_id,
            ledger_pairs(order_id=event.order_id, status=OrderStatus.TRIGGERED.value), event.occurred_at).identity_id]

    def _apply_order_ambiguous(self, event: BrokerEvent) -> list[str]:
        if event.order_id is None:
            raise ValueError("ORDER_AMBIGUOUS requires order_id")
        order = self._orders.get(event.order_id)
        if order is None:
            raise ValueError("ORDER_AMBIGUOUS references an unknown order")
        self._orders[event.order_id] = RuntimeOrderState(
            order_id=order.order_id, client_request_id=order.client_request_id,
            concrete_contract_id=order.concrete_contract_id, direction=order.direction,
            action=order.action, status=OrderStatus.AMBIGUOUS,
            requested_quantity=order.requested_quantity, filled_quantity=order.filled_quantity,
            average_fill_price=order.average_fill_price, last_event_id=event.event_id,
            updated_at=event.occurred_at,
        )
        return [self._ledger.append(RuntimeLedgerRecordKind.SAFETY, event.order_id,
            ledger_pairs(order_id=event.order_id, status=OrderStatus.AMBIGUOUS.value,
                         reason=_payload_value(event.payload, "reason") or "AMBIGUOUS_INTRABAR_SEQUENCE"), event.occurred_at).identity_id]

    def _apply_position_effect(
        self,
        *,
        contract: str,
        direction: PositionDirection,
        action: OrderAction,
        price: Decimal,
        quantity: Decimal,
        event: BrokerEvent,
    ) -> list[str]:
        """Apply the accounting effect of one fill; returns ledger identities."""
        spec = self._contract_specs[contract]
        multiplier = spec.contract_multiplier
        margin_rate = self._accounting.initial_margin_rate
        key = (contract, direction)
        before = self._positions.get(key)
        if before is None:
            old_quantity = Decimal("0")
            old_average = Decimal("0")
            old_realized = Decimal("0")
            old_reserved = Decimal("0")
        else:
            old_quantity = before.quantity
            old_average = before.average_open_price
            old_realized = before.realized_pnl
            old_reserved = before.reserved_margin

        if action is OrderAction.OPEN:
            new_quantity = old_quantity + quantity
            new_average = (old_average * old_quantity + price * quantity) / new_quantity
            realized_change = Decimal("0")
            if new_quantity == 0:
                raise ValueError("an OPEN fill cannot result in zero quantity")
        else:  # CLOSE
            if quantity > old_quantity:
                raise ValueError("a CLOSE fill cannot exceed the held position quantity")
            new_quantity = old_quantity - quantity
            if direction is PositionDirection.LONG:
                realized_change = (price - old_average) * multiplier * quantity
            else:
                realized_change = (old_average - price) * multiplier * quantity
            if new_quantity > 0:
                new_average = old_average
            else:
                new_average = Decimal("0")

        if new_quantity > 0:
            new_reserved = new_quantity * new_average * multiplier * margin_rate
            if direction is PositionDirection.LONG:
                unrealized = (price - new_average) * multiplier * new_quantity
            else:
                unrealized = (new_average - price) * multiplier * new_quantity
        else:
            new_reserved = Decimal("0")
            unrealized = Decimal("0")
        new_realized = old_realized + realized_change
        self._realized_accumulator += realized_change

        if new_quantity > 0:
            after = PositionState(
                concrete_contract_id=contract,
                direction=direction,
                quantity=new_quantity,
                average_open_price=new_average,
                reserved_margin=new_reserved,
                realized_pnl=new_realized,
                unrealized_pnl=unrealized,
                last_mark_price=price,
                updated_at=event.occurred_at,
            )
            self._positions[key] = after
        else:
            self._positions.pop(key, None)
            after = None

        self._refresh_account(event.occurred_at)
        transition_ref = _canonical_hash(
            {
                "event": event.identity_id,
                "contract": contract,
                "direction": direction.value,
                "action": action.value,
                "price": str(price),
                "quantity": str(quantity),
                "before": None if before is None else before.identity_id,
                "after": None if after is None else after.identity_id,
            }
        )
        return [
            self._ledger.append(
                RuntimeLedgerRecordKind.POSITION_TRANSITION,
                transition_ref,
                ledger_pairs(
                    event_id=event.event_id,
                    concrete_contract_id=contract,
                    direction=direction.value,
                    action=action.value,
                    price=str(price),
                    quantity=str(quantity),
                    realized_change=str(realized_change),
                    before_identity=None if before is None else before.identity_id,
                    after_identity=None if after is None else after.identity_id,
                ),
                event.occurred_at,
            ).identity_id
        ]

    def _apply_order_cancelled(self, event: BrokerEvent) -> list[str]:
        if event.order_id is None:
            raise ValueError("ORDER_CANCELLED requires order_id")
        order = self._orders.get(event.order_id)
        if order is None:
            raise ValueError("ORDER_CANCELLED references an unknown order")
        if order.status in (OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.REPLACED):
            raise ValueError("ORDER_CANCELLED cannot act on a terminal order")
        self._orders[event.order_id] = RuntimeOrderState(
            order_id=order.order_id,
            client_request_id=order.client_request_id,
            concrete_contract_id=order.concrete_contract_id,
            direction=order.direction,
            action=order.action,
            status=OrderStatus.CANCELLED,
            requested_quantity=order.requested_quantity,
            filled_quantity=order.filled_quantity,
            average_fill_price=order.average_fill_price,
            last_event_id=event.event_id,
            updated_at=event.occurred_at,
        )
        return [
            self._ledger.append(
                RuntimeLedgerRecordKind.CANCEL,
                event.order_id,
                ledger_pairs(order_id=event.order_id, status=OrderStatus.CANCELLED.value),
                event.occurred_at,
            ).identity_id
        ]

    def _apply_order_rejected(self, event: BrokerEvent) -> list[str]:
        if event.order_id is None:
            raise ValueError("ORDER_REJECTED requires order_id")
        order = self._orders.get(event.order_id)
        if order is None:
            raise ValueError("ORDER_REJECTED references an unknown order")
        self._orders[event.order_id] = RuntimeOrderState(
            order_id=order.order_id,
            client_request_id=order.client_request_id,
            concrete_contract_id=order.concrete_contract_id,
            direction=order.direction,
            action=order.action,
            status=OrderStatus.REJECTED,
            requested_quantity=order.requested_quantity,
            filled_quantity=order.filled_quantity,
            average_fill_price=order.average_fill_price,
            last_event_id=event.event_id,
            updated_at=event.occurred_at,
        )
        return [
            self._ledger.append(
                RuntimeLedgerRecordKind.ORDER,
                event.order_id,
                ledger_pairs(order_id=event.order_id, status=OrderStatus.REJECTED.value),
                event.occurred_at,
            ).identity_id
        ]

    def _apply_order_replaced(self, event: BrokerEvent) -> list[str]:
        if event.order_id is None:
            raise ValueError("ORDER_REPLACED requires order_id")
        order = self._orders.get(event.order_id)
        if order is None:
            raise ValueError("ORDER_REPLACED references an unknown order")
        new_quantity = _payload_decimal(event.payload, PAYLOAD_NEW_QUANTITY)
        if new_quantity <= 0:
            raise ValueError("ORDER_REPLACED requires positive new quantity")
        if order.filled_quantity > new_quantity:
            raise ValueError("ORDER_REPLACED cannot reduce below the already-filled quantity")
        self._orders[event.order_id] = RuntimeOrderState(
            order_id=order.order_id,
            client_request_id=order.client_request_id,
            concrete_contract_id=order.concrete_contract_id,
            direction=order.direction,
            action=order.action,
            status=OrderStatus.REPLACED,
            requested_quantity=new_quantity,
            filled_quantity=order.filled_quantity,
            average_fill_price=order.average_fill_price,
            last_event_id=event.event_id,
            updated_at=event.occurred_at,
        )
        return [
            self._ledger.append(
                RuntimeLedgerRecordKind.REPLACE,
                event.order_id,
                ledger_pairs(
                    order_id=event.order_id,
                    new_quantity=str(new_quantity),
                    status=OrderStatus.REPLACED.value,
                ),
                event.occurred_at,
            ).identity_id
        ]

    def _apply_connection_state(self, event: BrokerEvent) -> list[str]:
        raw = _require_payload(event.payload, PAYLOAD_CONNECTION_STATE)
        new_state = BrokerConnectionState(raw)
        self._connection_state = new_state
        return [
            self._ledger.append(
                RuntimeLedgerRecordKind.BROKER_EVENT,
                event.event_id,
                ledger_pairs(connection_state=new_state.value),
                event.occurred_at,
            ).identity_id
        ]

    def _apply_account_snapshot(self, event: BrokerEvent) -> list[str]:
        # Broker account snapshot is a reconciliation input, not an overwrite of
        # local accounting. Stored for reconciliation and fail-closed checks.
        self._last_account_snapshot = event.payload
        return []

    def _apply_position_snapshot(self, event: BrokerEvent) -> list[str]:
        self._last_position_snapshots = self._last_position_snapshots + (event.payload,)
        return []

    def _apply_order_snapshot(self, event: BrokerEvent) -> list[str]:
        self._last_order_snapshots = self._last_order_snapshots + (event.payload,)
        return []

    # -- marking / accounting refresh ----------------------------------------

    def mark_position(
        self,
        concrete_contract_id: str,
        direction: PositionDirection,
        price: Decimal,
        observed_at: datetime,
    ) -> PositionState | None:
        """Deterministically re-mark one position (unrealized PnL update)."""
        if observed_at.tzinfo is None:
            raise ValueError("mark observation timestamp must be timezone-aware")
        if type(price) is not Decimal or not price.is_finite() or price <= 0:
            raise ValueError("mark price must be a positive finite Decimal")
        key = (concrete_contract_id, direction)
        before = self._positions.get(key)
        if before is None:
            return None
        spec = self._contract_specs.get(concrete_contract_id)
        if spec is None:
            raise ValueError("mark references an unknown concrete contract")
        multiplier = spec.contract_multiplier
        if direction is PositionDirection.LONG:
            unrealized = (price - before.average_open_price) * multiplier * before.quantity
        else:
            unrealized = (before.average_open_price - price) * multiplier * before.quantity
        after = PositionState(
            concrete_contract_id=concrete_contract_id,
            direction=direction,
            quantity=before.quantity,
            average_open_price=before.average_open_price,
            reserved_margin=before.reserved_margin,
            realized_pnl=before.realized_pnl,
            unrealized_pnl=unrealized,
            last_mark_price=price,
            updated_at=observed_at,
        )
        self._positions[key] = after
        self._refresh_account(observed_at)
        transition_ref = _canonical_hash(
            {
                "kind": "MARK",
                "contract": concrete_contract_id,
                "direction": direction.value,
                "price": str(price),
                "before": before.identity_id,
                "after": after.identity_id,
            }
        )
        self._ledger.append(
            RuntimeLedgerRecordKind.POSITION_TRANSITION,
            transition_ref,
            ledger_pairs(
                kind="MARK",
                concrete_contract_id=concrete_contract_id,
                direction=direction.value,
                price=str(price),
                before_identity=before.identity_id,
                after_identity=after.identity_id,
            ),
            observed_at,
        )
        return after

    def _refresh_account(self, updated_at: datetime) -> None:
        reserved = sum((item.reserved_margin for item in self._positions.values()), Decimal("0"))
        unrealized = sum((item.unrealized_pnl for item in self._positions.values()), Decimal("0"))
        self._account = AccountState(
            starting_capital=self._starting_capital,
            reserved_margin=reserved,
            realized_pnl=self._realized_accumulator,
            unrealized_pnl=unrealized,
            charged_costs=self._account.charged_costs,
            updated_at=updated_at,
        )

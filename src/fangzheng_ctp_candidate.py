"""Offline Fangzheng/CTP broker-adapter candidate.

This module deliberately imports no vendor SDK and performs no network or
credential work.  A future CTP runtime must be injected through ``CtpTransport``.
All values whose exact Fangzheng/CTP spelling is not project-authoritative are
opaque, caller-supplied strings.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Protocol

from src.broker_adapter import (
    BrokerAccountSnapshot,
    BrokerAdapter,
    BrokerOrderInstruction,
    BrokerOrderSnapshot,
    BrokerPositionSnapshot,
    OrderType,
    canonical_decimal,
)
from src.contract_semantics import CloseOffset, OrderAction, PositionDirection
from src.runtime_events import (
    BrokerConnectionState,
    BrokerEvent,
    BrokerEventType,
    event_pairs,
)


FANGZHENG_CTP_CANDIDATE_VERSION = "KPE_FANGZHENG_CTP_CANDIDATE_V0_1"
_SENSITIVE_NAMES = ("password", "secret", "credential", "api_key", "auth_code")


def _required_text(value: str, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _finite_decimal(value: Decimal, name: str, *, non_negative: bool = False) -> Decimal:
    if type(value) is not Decimal or not value.is_finite():
        raise ValueError(f"{name} must be a finite Decimal")
    if non_negative and value < 0:
        raise ValueError(f"{name} must be non-negative")
    return value


def _reject_sensitive_names(names: tuple[str, ...]) -> None:
    for name in names:
        lowered = name.lower()
        if any(token in lowered for token in _SENSITIVE_NAMES):
            raise ValueError("CTP candidate refuses secret-bearing fields")


def _canonical(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return canonical_decimal(value)
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, tuple):
        return [_canonical(item) for item in value]
    if hasattr(value, "__dataclass_fields__"):
        return {
            name: _canonical(getattr(value, name))
            for name in value.__dataclass_fields__
        }
    return value


def _fingerprint(value: Any) -> str:
    encoded = json.dumps(_canonical(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(encoded.encode("utf-8")).hexdigest()


class CtpSessionState(str, Enum):
    DISCONNECTED = "DISCONNECTED"
    CONNECTING = "CONNECTING"
    CONNECTED_UNAUTHENTICATED = "CONNECTED_UNAUTHENTICATED"
    AUTHENTICATING = "AUTHENTICATING"
    AUTHENTICATED = "AUTHENTICATED"
    LOGGING_IN = "LOGGING_IN"
    LOGGED_IN_PENDING_TRADING_DAY = "LOGGED_IN_PENDING_TRADING_DAY"
    READY_FOR_RECONCILIATION = "READY_FOR_RECONCILIATION"
    RECONNECTING = "RECONNECTING"
    UNKNOWN = "UNKNOWN"


class CtpTruthState(str, Enum):
    UNKNOWN = "UNKNOWN"
    REQUESTED = "REQUESTED"
    KNOWN = "KNOWN"


class CtpCallbackType(str, Enum):
    FRONT_CONNECTED = "FRONT_CONNECTED"
    AUTHENTICATED = "AUTHENTICATED"
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    LOGIN_SUCCEEDED = "LOGIN_SUCCEEDED"
    LOGIN_FAILED = "LOGIN_FAILED"
    TRADING_DAY = "TRADING_DAY"
    ORDER_ACKNOWLEDGED = "ORDER_ACKNOWLEDGED"
    ORDER_REJECTED = "ORDER_REJECTED"
    TRADE_FILLED = "TRADE_FILLED"
    CANCEL_ACKNOWLEDGED = "CANCEL_ACKNOWLEDGED"
    CANCEL_REJECTED = "CANCEL_REJECTED"
    ACCOUNT_SNAPSHOT = "ACCOUNT_SNAPSHOT"
    POSITION_SNAPSHOT = "POSITION_SNAPSHOT"
    ORDER_SNAPSHOT = "ORDER_SNAPSHOT"
    TRADE_SNAPSHOT = "TRADE_SNAPSHOT"
    DISCONNECTED = "DISCONNECTED"
    ERROR = "ERROR"
    UNKNOWN = "UNKNOWN"


class BrokerTruthUnknownError(RuntimeError):
    """Raised when a caller asks the adapter to claim unestablished truth."""


@dataclass(frozen=True)
class CtpSessionFailure:
    error_code: str
    reason: str

    def __post_init__(self) -> None:
        _required_text(self.error_code, "CTP session error code")
        _required_text(self.reason, "CTP session failure reason")


@dataclass(frozen=True)
class CtpSubmitRequest:
    project_order_id: str
    client_request_id: str
    instruction_identity: str
    instrument_id: str
    direction_field: str
    offset_field: str
    order_type_field: str
    quantity: str
    limit_price: str | None

    def __post_init__(self) -> None:
        values = (
            self.project_order_id,
            self.client_request_id,
            self.instruction_identity,
            self.instrument_id,
            self.direction_field,
            self.offset_field,
            self.order_type_field,
            self.quantity,
        )
        if not all(isinstance(value, str) and value.strip() for value in values):
            raise ValueError("CTP submit translation requires complete opaque fields")

    @property
    def identity_id(self) -> str:
        return _fingerprint(self)


@dataclass(frozen=True)
class CtpCancelRequest:
    project_order_id: str
    client_request_id: str
    broker_order_id: str
    cancel_token: str

    def __post_init__(self) -> None:
        if not all(
            isinstance(value, str) and value.strip()
            for value in (
                self.project_order_id,
                self.client_request_id,
                self.broker_order_id,
                self.cancel_token,
            )
        ):
            raise ValueError("CTP cancel translation requires complete mapped identities")

    @property
    def identity_id(self) -> str:
        return _fingerprint(self)


@dataclass(frozen=True)
class CtpTranslationProfile:
    """Injected opaque mapping; this candidate does not guess vendor constants."""

    instruments: tuple[tuple[str, str], ...]
    sides: tuple[tuple[PositionDirection, OrderAction, str], ...]
    offsets: tuple[tuple[OrderAction, CloseOffset | None, str], ...]
    order_types: tuple[tuple[OrderType, str], ...]

    def __post_init__(self) -> None:
        if not all((self.instruments, self.sides, self.offsets, self.order_types)):
            raise ValueError("CTP translation profile must explicitly map every field family")
        flattened_names = tuple(value for pair in self.instruments for value in pair)
        flattened_names += tuple(item[2] for item in self.sides)
        flattened_names += tuple(item[2] for item in self.offsets)
        flattened_names += tuple(item[1] for item in self.order_types)
        _reject_sensitive_names(flattened_names)

    @staticmethod
    def _lookup(items: tuple[tuple[Any, ...], ...], key: tuple[Any, ...], name: str) -> str:
        matches = tuple(item[-1] for item in items if item[:-1] == key)
        if len(matches) != 1 or not isinstance(matches[0], str) or not matches[0].strip():
            raise ValueError(f"CTP translation is missing one unambiguous {name} mapping")
        return matches[0]

    def translate_submit(self, instruction: BrokerOrderInstruction) -> CtpSubmitRequest:
        if not isinstance(instruction, BrokerOrderInstruction):
            raise ValueError("CTP submit translation requires BrokerOrderInstruction")
        if instruction.order_type is OrderType.STOP_MARKET:
            raise ValueError("CTP_STOP_ORDER_SEMANTICS_NOT_ESTABLISHED")
        project_order_id = instruction.client_order_id or instruction.client_request_id
        return CtpSubmitRequest(
            project_order_id=project_order_id,
            client_request_id=instruction.client_request_id,
            instruction_identity=instruction.identity_id,
            instrument_id=self._lookup(self.instruments, (instruction.concrete_contract_id,), "instrument"),
            direction_field=self._lookup(self.sides, (instruction.direction, instruction.action), "side"),
            offset_field=self._lookup(self.offsets, (instruction.action, instruction.close_offset), "offset"),
            order_type_field=self._lookup(self.order_types, (instruction.order_type,), "order type"),
            quantity=canonical_decimal(instruction.quantity),
            limit_price=None if instruction.limit_price is None else canonical_decimal(instruction.limit_price),
        )


@dataclass(frozen=True)
class CtpOrderAcknowledgement:
    project_order_id: str
    client_request_id: str
    broker_order_id: str
    cancel_token: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.project_order_id, "project order id"),
            (self.client_request_id, "client request id"),
            (self.broker_order_id, "broker order id"),
            (self.cancel_token, "cancel token"),
        ):
            _required_text(value, name)


@dataclass(frozen=True)
class CtpOrderRejection:
    project_order_id: str
    client_request_id: str
    error_code: str
    reason: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.project_order_id, "project order id"),
            (self.client_request_id, "client request id"),
            (self.error_code, "error code"),
            (self.reason, "rejection reason"),
        ):
            _required_text(value, name)


@dataclass(frozen=True)
class CtpTradeFill:
    project_order_id: str
    client_request_id: str
    broker_order_id: str
    broker_trade_id: str
    quantity: Decimal
    price: Decimal

    def __post_init__(self) -> None:
        for value, name in (
            (self.project_order_id, "project order id"),
            (self.client_request_id, "client request id"),
            (self.broker_order_id, "broker order id"),
            (self.broker_trade_id, "broker trade id"),
        ):
            _required_text(value, name)
        _finite_decimal(self.quantity, "fill quantity")
        _finite_decimal(self.price, "fill price")
        if self.quantity <= 0 or self.price <= 0:
            raise ValueError("CTP fill quantity and price must be positive")


@dataclass(frozen=True)
class CtpCancelAcknowledgement:
    project_order_id: str
    client_request_id: str
    broker_order_id: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.project_order_id, "project order id"),
            (self.client_request_id, "client request id"),
            (self.broker_order_id, "broker order id"),
        ):
            _required_text(value, name)


@dataclass(frozen=True)
class CtpCancelRejection:
    project_order_id: str
    client_request_id: str
    broker_order_id: str
    error_code: str
    reason: str

    def __post_init__(self) -> None:
        for value, name in (
            (self.project_order_id, "project order id"),
            (self.client_request_id, "client request id"),
            (self.broker_order_id, "broker order id"),
            (self.error_code, "cancel rejection error code"),
            (self.reason, "cancel rejection reason"),
        ):
            _required_text(value, name)


@dataclass(frozen=True)
class CtpAccountRecord:
    account_id: str
    snapshot_at: datetime
    cash_balance: Decimal
    reserved_margin: Decimal
    charged_costs: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    currency: str


@dataclass(frozen=True)
class CtpPositionRecord:
    concrete_contract_id: str
    direction: PositionDirection
    quantity: Decimal
    average_price: Decimal
    snapshot_at: datetime


@dataclass(frozen=True)
class CtpOrderRecord:
    project_order_id: str
    client_request_id: str
    broker_order_id: str
    concrete_contract_id: str
    direction: PositionDirection
    action: OrderAction
    status: str
    requested_quantity: Decimal
    filled_quantity: Decimal
    snapshot_at: datetime


@dataclass(frozen=True)
class CtpTradeRecord:
    broker_trade_id: str
    project_order_id: str
    broker_order_id: str
    quantity: Decimal
    price: Decimal
    occurred_at: datetime

    def __post_init__(self) -> None:
        for value, name in (
            (self.broker_trade_id, "broker trade id"),
            (self.project_order_id, "project order id"),
            (self.broker_order_id, "broker order id"),
        ):
            _required_text(value, name)
        _finite_decimal(self.quantity, "trade quantity")
        _finite_decimal(self.price, "trade price")
        if self.quantity <= 0 or self.price <= 0:
            raise ValueError("CTP trade quantity and price must be positive")
        if self.occurred_at.tzinfo is None:
            raise ValueError("CTP trade timestamp must be timezone-aware")


@dataclass(frozen=True)
class CtpCallback:
    callback_id: str
    callback_type: CtpCallbackType
    occurred_at: datetime
    data: Any = None
    trading_day: str | None = None

    def __post_init__(self) -> None:
        _required_text(self.callback_id, "CTP callback id")
        if not isinstance(self.callback_type, CtpCallbackType):
            raise ValueError("CTP callback type must be explicit")
        if not isinstance(self.occurred_at, datetime) or self.occurred_at.tzinfo is None:
            raise ValueError("CTP callback timestamp must be timezone-aware")
        if isinstance(self.data, dict):
            _reject_sensitive_names(tuple(str(name) for name in self.data))
        if self.trading_day is not None:
            if (
                not isinstance(self.trading_day, str)
                or len(self.trading_day) != 8
                or not self.trading_day.isdigit()
            ):
                raise ValueError("CTP callback trading day must use YYYYMMDD")

    @property
    def identity_id(self) -> str:
        return _fingerprint(self)


class CtpTransport(Protocol):
    """Injected session seam. Implementations keep credentials entirely private."""

    @property
    def broker_id(self) -> str: ...

    def connect(self) -> None: ...
    def disconnect(self) -> None: ...
    def authenticate(self) -> None: ...
    def login(self) -> None: ...
    def submit_order(self, request: CtpSubmitRequest) -> None: ...
    def cancel_order(self, request: CtpCancelRequest) -> None: ...
    def request_account(self) -> None: ...
    def request_positions(self) -> None: ...
    def request_orders(self) -> None: ...
    def request_trades(self) -> None: ...
    def drain_callbacks(self) -> tuple[CtpCallback, ...]: ...


class FangzhengCtpBrokerAdapter(BrokerAdapter):
    """Offline-testable CTP candidate behind the existing broker abstraction."""

    def __init__(self, transport: CtpTransport, translation_profile: CtpTranslationProfile) -> None:
        broker_id = getattr(transport, "broker_id", "")
        _required_text(broker_id, "CTP broker id")
        if not isinstance(translation_profile, CtpTranslationProfile):
            raise ValueError("CTP adapter requires an explicit translation profile")
        self._transport = transport
        self._translation = translation_profile
        self._session_state = CtpSessionState.DISCONNECTED
        self._trading_day: str | None = None
        self._truth = {name: CtpTruthState.UNKNOWN for name in ("account", "positions", "orders", "trades")}
        self._account: BrokerAccountSnapshot | None = None
        self._positions: tuple[BrokerPositionSnapshot, ...] = ()
        self._orders: tuple[BrokerOrderSnapshot, ...] = ()
        self._ctp_orders: tuple[CtpOrderRecord, ...] = ()
        self._trades: tuple[CtpTradeRecord, ...] = ()
        self._outbox: list[BrokerEvent] = []
        self._seen_callbacks: dict[str, str] = {}
        self._seen_lifecycle_facts: set[str] = set()
        self._seen_trade_ids: dict[str, str] = {}
        self._sequence = 0
        self._submitted: dict[str, CtpSubmitRequest] = {}
        self._broker_mapping: dict[str, tuple[str, str, str]] = {}

    @property
    def broker_id(self) -> str:
        return self._transport.broker_id

    @property
    def connection_state(self) -> BrokerConnectionState:
        if self._session_state is CtpSessionState.DISCONNECTED:
            return BrokerConnectionState.DISCONNECTED
        if self._session_state is CtpSessionState.READY_FOR_RECONCILIATION:
            return BrokerConnectionState.CONNECTED
        return BrokerConnectionState.RECONNECTING

    @property
    def session_state(self) -> CtpSessionState:
        return self._session_state

    @property
    def trading_day(self) -> str | None:
        return self._trading_day

    @property
    def truth_state(self) -> tuple[tuple[str, CtpTruthState], ...]:
        return tuple(sorted(self._truth.items()))

    @property
    def ready(self) -> bool:
        return self._session_state is CtpSessionState.READY_FOR_RECONCILIATION and all(
            state is CtpTruthState.KNOWN for state in self._truth.values()
        )

    def connect(self) -> None:
        if self._session_state not in {CtpSessionState.DISCONNECTED, CtpSessionState.RECONNECTING}:
            raise RuntimeError("CTP_CONNECT_INVALID_SESSION_STATE")
        self._mark_truth_unknown()
        self._session_state = CtpSessionState.CONNECTING
        self._transport.connect()

    def disconnect(self) -> None:
        self._transport.disconnect()
        self._session_state = CtpSessionState.DISCONNECTED
        self._trading_day = None
        self._mark_truth_unknown()

    def request_authentication(self) -> None:
        if self._session_state is not CtpSessionState.CONNECTED_UNAUTHENTICATED:
            raise RuntimeError("CTP_AUTHENTICATE_INVALID_SESSION_STATE")
        self._session_state = CtpSessionState.AUTHENTICATING
        self._transport.authenticate()

    def request_login(self) -> None:
        if self._session_state is not CtpSessionState.AUTHENTICATED:
            raise RuntimeError("CTP_LOGIN_INVALID_SESSION_STATE")
        self._session_state = CtpSessionState.LOGGING_IN
        self._transport.login()

    def refresh_broker_truth(self) -> None:
        if self._session_state is not CtpSessionState.READY_FOR_RECONCILIATION:
            raise RuntimeError("CTP_SESSION_NOT_READY_FOR_QUERY")
        self._truth = {name: CtpTruthState.REQUESTED for name in self._truth}
        self._transport.request_account()
        self._transport.request_positions()
        self._transport.request_orders()
        self._transport.request_trades()

    def submit_order(self, instruction: BrokerOrderInstruction) -> str:
        if not self.ready:
            raise BrokerTruthUnknownError("CTP_BROKER_TRUTH_NOT_READY")
        request = self._translation.translate_submit(instruction)
        previous = self._submitted.get(request.project_order_id)
        if previous is not None:
            if previous != request:
                raise ValueError("CTP_PROJECT_ORDER_ID_REUSED_WITH_DIFFERENT_CONTENT")
            return request.project_order_id
        # Persist the project-side attempt identity before crossing the
        # transport seam.  An exception may occur after the broker received the
        # request, so the same project order must never be blindly submitted
        # again and all broker truth becomes unknown until reconciliation.
        self._submitted[request.project_order_id] = request
        try:
            self._transport.submit_order(request)
        except Exception:
            self._session_state = CtpSessionState.UNKNOWN
            self._trading_day = None
            self._mark_truth_unknown()
            raise
        return request.project_order_id

    def cancel_order(self, order_id: str) -> None:
        _required_text(order_id, "project order id")
        if not self.ready:
            raise BrokerTruthUnknownError("CTP_BROKER_TRUTH_NOT_READY")
        mapping = self._broker_mapping.get(order_id)
        if mapping is None:
            raise BrokerTruthUnknownError("CTP_CANCEL_MAPPING_UNKNOWN")
        client_request_id, broker_order_id, cancel_token = mapping
        self._transport.cancel_order(CtpCancelRequest(order_id, client_request_id, broker_order_id, cancel_token))

    def replace_order(self, order_id: str, new_quantity: Decimal) -> None:
        raise RuntimeError("CTP_ATOMIC_REPLACE_NOT_ESTABLISHED")

    def pump_callbacks(self) -> tuple[BrokerEvent, ...]:
        for callback in self._transport.drain_callbacks():
            self._apply_callback(callback)
        return self.drain_events()

    def drain_events(self) -> tuple[BrokerEvent, ...]:
        events = tuple(self._outbox)
        self._outbox.clear()
        return events

    def fetch_account_snapshot(self) -> BrokerAccountSnapshot:
        if self._truth["account"] is not CtpTruthState.KNOWN or self._account is None:
            raise BrokerTruthUnknownError("CTP_ACCOUNT_TRUTH_UNKNOWN")
        return self._account

    def fetch_position_snapshot(self) -> tuple[BrokerPositionSnapshot, ...]:
        self._require_known("positions")
        return self._positions

    def fetch_order_snapshot(self) -> tuple[BrokerOrderSnapshot, ...]:
        self._require_known("orders")
        return self._orders

    def fetch_ctp_order_snapshot(self) -> tuple[CtpOrderRecord, ...]:
        """Return lossless project/broker identities for REAL composition."""
        self._require_known("orders")
        return self._ctp_orders

    def fetch_trade_snapshot(self) -> tuple[CtpTradeRecord, ...]:
        self._require_known("trades")
        return self._trades

    def capture_snapshot(self) -> Any:
        raise RuntimeError("CTP_LIVE_SESSION_SNAPSHOT_RESTORE_NOT_ESTABLISHED")

    def restore_snapshot(self, snapshot: Any) -> None:
        raise RuntimeError("CTP_LIVE_SESSION_SNAPSHOT_RESTORE_NOT_ESTABLISHED")

    def _require_known(self, name: str) -> None:
        if self._truth[name] is not CtpTruthState.KNOWN:
            raise BrokerTruthUnknownError(f"CTP_{name.upper()}_TRUTH_UNKNOWN")

    def _mark_truth_unknown(self) -> None:
        self._truth = {name: CtpTruthState.UNKNOWN for name in self._truth}
        self._account = None
        self._positions = ()
        self._orders = ()
        self._ctp_orders = ()
        self._trades = ()

    def _emit(self, callback: CtpCallback, event_type: BrokerEventType, *, order_id: str | None = None,
              client_request_id: str | None = None, **payload: Any) -> None:
        self._outbox.append(BrokerEvent(
            event_id=f"ctp:{callback.callback_id}",
            event_type=event_type,
            occurred_at=callback.occurred_at,
            stream_id=f"ctp:{self.broker_id}",
            sequence=self._sequence,
            order_id=order_id,
            client_request_id=client_request_id,
            payload=event_pairs(**payload),
        ))
        self._sequence += 1

    def _invalidate(self, callback: CtpCallback, reason: str) -> None:
        self._session_state = CtpSessionState.UNKNOWN
        self._trading_day = None
        self._mark_truth_unknown()
        self._emit(callback, BrokerEventType.CONNECTION_STATE, state="UNKNOWN", reason=reason)

    def _apply_callback(self, callback: CtpCallback) -> None:
        if not isinstance(callback, CtpCallback):
            raise ValueError("CTP transport returned a non-CtpCallback value")
        if (
            callback.callback_type is not CtpCallbackType.TRADING_DAY
            and callback.trading_day is not None
            and self._trading_day is not None
            and callback.trading_day != self._trading_day
        ):
            self._invalidate(callback, "CTP_CALLBACK_TRADING_DAY_MISMATCH")
            raise ValueError("CTP_CALLBACK_TRADING_DAY_MISMATCH")
        fingerprint = callback.identity_id
        previous = self._seen_callbacks.get(callback.callback_id)
        if previous is not None:
            if previous != fingerprint:
                self._session_state = CtpSessionState.UNKNOWN
                self._trading_day = None
                self._mark_truth_unknown()
                raise ValueError("CTP_DUPLICATE_CALLBACK_ID_DIFFERENT_CONTENT")
            return
        self._seen_callbacks[callback.callback_id] = fingerprint

        kind = callback.callback_type
        data = callback.data
        lifecycle_kinds = {
            CtpCallbackType.ORDER_ACKNOWLEDGED,
            CtpCallbackType.ORDER_REJECTED,
            CtpCallbackType.TRADE_FILLED,
            CtpCallbackType.CANCEL_ACKNOWLEDGED,
            CtpCallbackType.CANCEL_REJECTED,
        }
        if kind in lifecycle_kinds:
            lifecycle_fingerprint = _fingerprint((kind, data))
            if lifecycle_fingerprint in self._seen_lifecycle_facts:
                return
            if kind is CtpCallbackType.TRADE_FILLED and isinstance(data, CtpTradeFill):
                prior_trade = self._seen_trade_ids.get(data.broker_trade_id)
                if prior_trade is not None and prior_trade != lifecycle_fingerprint:
                    self._invalidate(callback, "BROKER_TRADE_ID_REUSED_WITH_DIFFERENT_CONTENT")
                    raise ValueError("CTP_BROKER_TRADE_ID_REUSED_WITH_DIFFERENT_CONTENT")
                self._seen_trade_ids[data.broker_trade_id] = lifecycle_fingerprint
            self._seen_lifecycle_facts.add(lifecycle_fingerprint)
        if kind is CtpCallbackType.FRONT_CONNECTED and self._session_state in {
            CtpSessionState.CONNECTING, CtpSessionState.RECONNECTING
        }:
            self._session_state = CtpSessionState.CONNECTED_UNAUTHENTICATED
            self._emit(callback, BrokerEventType.CONNECTION_STATE, state=self._session_state.value)
        elif kind is CtpCallbackType.AUTHENTICATED and self._session_state is CtpSessionState.AUTHENTICATING:
            self._session_state = CtpSessionState.AUTHENTICATED
        elif (kind is CtpCallbackType.AUTHENTICATION_FAILED
              and self._session_state is CtpSessionState.AUTHENTICATING
              and isinstance(data, CtpSessionFailure)):
            self._invalidate(callback, data.reason)
        elif kind is CtpCallbackType.LOGIN_SUCCEEDED and self._session_state is CtpSessionState.LOGGING_IN:
            self._session_state = CtpSessionState.LOGGED_IN_PENDING_TRADING_DAY
        elif (kind is CtpCallbackType.LOGIN_FAILED
              and self._session_state is CtpSessionState.LOGGING_IN
              and isinstance(data, CtpSessionFailure)):
            self._invalidate(callback, data.reason)
        elif kind is CtpCallbackType.TRADING_DAY and self._session_state is CtpSessionState.LOGGED_IN_PENDING_TRADING_DAY:
            self._trading_day = _required_text(data, "CTP trading day")
            self._session_state = CtpSessionState.READY_FOR_RECONCILIATION
            self._emit(callback, BrokerEventType.CONNECTION_STATE, state=self._session_state.value,
                       trading_day=self._trading_day)
        elif kind is CtpCallbackType.TRADING_DAY and self._session_state is CtpSessionState.READY_FOR_RECONCILIATION:
            next_trading_day = _required_text(data, "CTP trading day")
            if next_trading_day != self._trading_day:
                self._trading_day = next_trading_day
                self._mark_truth_unknown()
                self._emit(
                    callback,
                    BrokerEventType.CONNECTION_STATE,
                    state=self._session_state.value,
                    trading_day=self._trading_day,
                    reason="TRADING_DAY_ROLLOVER_REQUIRES_FRESH_QUERY",
                )
        elif kind is CtpCallbackType.ORDER_ACKNOWLEDGED and isinstance(data, CtpOrderAcknowledgement):
            self._broker_mapping[data.project_order_id] = (
                data.client_request_id, data.broker_order_id, data.cancel_token
            )
            self._emit(callback, BrokerEventType.ORDER_SUBMITTED, order_id=data.project_order_id,
                       client_request_id=data.client_request_id, broker_order_id=data.broker_order_id,
                       lifecycle_status="LIVE")
        elif kind is CtpCallbackType.ORDER_REJECTED and isinstance(data, CtpOrderRejection):
            self._emit(callback, BrokerEventType.ORDER_REJECTED, order_id=data.project_order_id,
                       client_request_id=data.client_request_id, error_code=data.error_code, reason=data.reason)
        elif kind is CtpCallbackType.TRADE_FILLED and isinstance(data, CtpTradeFill):
            self._emit(callback, BrokerEventType.ORDER_FILLED, order_id=data.project_order_id,
                       client_request_id=data.client_request_id, broker_order_id=data.broker_order_id,
                       broker_trade_id=data.broker_trade_id, quantity=data.quantity, price=data.price)
        elif kind is CtpCallbackType.CANCEL_ACKNOWLEDGED and isinstance(data, CtpCancelAcknowledgement):
            self._emit(callback, BrokerEventType.ORDER_CANCELLED, order_id=data.project_order_id,
                       client_request_id=data.client_request_id, broker_order_id=data.broker_order_id)
        elif kind is CtpCallbackType.CANCEL_REJECTED and isinstance(data, CtpCancelRejection):
            self._mark_truth_unknown()
            self._emit(
                callback,
                BrokerEventType.ORDER_AMBIGUOUS,
                order_id=data.project_order_id,
                client_request_id=data.client_request_id,
                broker_order_id=data.broker_order_id,
                error_code=data.error_code,
                reason=data.reason,
            )
        elif (kind is CtpCallbackType.ACCOUNT_SNAPSHOT
              and self._truth["account"] is CtpTruthState.REQUESTED
              and isinstance(data, CtpAccountRecord)):
            self._account = BrokerAccountSnapshot(**data.__dict__)
            self._truth["account"] = CtpTruthState.KNOWN
        elif (kind is CtpCallbackType.POSITION_SNAPSHOT
              and self._truth["positions"] is CtpTruthState.REQUESTED
              and isinstance(data, tuple)) and all(
            isinstance(item, CtpPositionRecord) for item in data
        ):
            self._positions = tuple(BrokerPositionSnapshot(**item.__dict__) for item in data)
            self._truth["positions"] = CtpTruthState.KNOWN
        elif (kind is CtpCallbackType.ORDER_SNAPSHOT
              and self._truth["orders"] is CtpTruthState.REQUESTED
              and isinstance(data, tuple)) and all(
            isinstance(item, CtpOrderRecord) for item in data
        ):
            self._ctp_orders = data
            self._orders = tuple(BrokerOrderSnapshot(
                order_id=item.project_order_id,
                client_request_id=item.client_request_id,
                concrete_contract_id=item.concrete_contract_id,
                direction=item.direction,
                action=item.action,
                status=item.status,
                requested_quantity=item.requested_quantity,
                filled_quantity=item.filled_quantity,
                snapshot_at=item.snapshot_at,
            ) for item in data)
            for item in data:
                previous_mapping = self._broker_mapping.get(item.project_order_id)
                if previous_mapping is not None:
                    self._broker_mapping[item.project_order_id] = (
                        item.client_request_id, item.broker_order_id, previous_mapping[2]
                    )
            self._truth["orders"] = CtpTruthState.KNOWN
        elif (kind is CtpCallbackType.TRADE_SNAPSHOT
              and self._truth["trades"] is CtpTruthState.REQUESTED
              and isinstance(data, tuple)) and all(
            isinstance(item, CtpTradeRecord) for item in data
        ):
            self._trades = data
            self._truth["trades"] = CtpTruthState.KNOWN
        elif kind is CtpCallbackType.DISCONNECTED:
            self._session_state = CtpSessionState.RECONNECTING
            self._trading_day = None
            self._mark_truth_unknown()
            self._emit(callback, BrokerEventType.CONNECTION_STATE, state=self._session_state.value)
        elif kind is CtpCallbackType.ERROR:
            if isinstance(data, CtpOrderRejection):
                self._emit(callback, BrokerEventType.ORDER_AMBIGUOUS, order_id=data.project_order_id,
                           client_request_id=data.client_request_id, error_code=data.error_code,
                           reason=data.reason)
            self._mark_truth_unknown()
        else:
            self._invalidate(callback, "UNEXPECTED_OR_UNSUPPORTED_CALLBACK")

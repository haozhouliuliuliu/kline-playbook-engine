"""Offline-testable TqSdk PAPER execution driver and pure object translators.

The module imports no TqSdk package and reads no credentials. A session factory is
invoked only by connect(), which itself remains behind PaperExecutionAuthority in
TqSdkPaperBrokerAdapter. Native TqSdk objects are injected and translated into
project-owned broker snapshots/events.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
from typing import Any, Callable, Mapping, Protocol
from zoneinfo import ZoneInfo

from src.broker_adapter import (
    BrokerAccountSnapshot, BrokerOrderInstruction, BrokerOrderSnapshot,
    BrokerPositionSnapshot, OrderType,
)
from src.contract_semantics import OrderAction, PositionDirection
from src.paper_order_journal import PREPARED, PaperOrderJournal
from src.paper_execution_authority import PaperExecutionAuthority
from src.runtime_events import BrokerConnectionState, BrokerEvent, BrokerEventType, event_pairs

TQSDK_PAPER_DRIVER_VERSION = "KPE_TQSDK_PAPER_DRIVER_V0_1"
_SHFE_STYLE = frozenset({"SHFE", "INE"})

class TqSdkSession(Protocol):
    def insert_order(self, **kwargs: Any) -> Any: ...
    def cancel_order(self, order_or_id: Any) -> None: ...
    def wait_update(self) -> bool: ...
    def get_account(self) -> Any: ...
    def get_positions(self) -> Mapping[str, Any]: ...
    def get_orders(self) -> Mapping[str, Any]: ...
    def get_trades(self) -> Mapping[str, Any]: ...
    def close(self) -> None: ...

@dataclass(frozen=True)
class TqSdkCloseChild:
    offset: str
    volume: int
    def __post_init__(self) -> None:
        if self.offset not in ("CLOSE", "CLOSETODAY"):
            raise ValueError("TqSdk close child offset must be CLOSE or CLOSETODAY")
        if type(self.volume) is not int or self.volume <= 0:
            raise ValueError("TqSdk close child volume must be positive integer")

class TqSdkCloseOffsetPolicy(Protocol):
    identity_id: str
    def resolve(self, instruction: BrokerOrderInstruction,
                position: Any | None) -> tuple[TqSdkCloseChild, ...]: ...

class TqSdkExecutionPricePolicy(Protocol):
    identity_id: str
    def resolve_limit_price(self, instruction: BrokerOrderInstruction,
                            session: TqSdkSession) -> Decimal: ...

def _field(value: Any, name: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(name, default)
    return getattr(value, name, default)

def _decimal(value: Any, field_name: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(f"{field_name} must be numeric")
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as error:
        raise ValueError(f"{field_name} must be numeric") from error
    if not parsed.is_finite():
        raise ValueError(f"{field_name} must be finite")
    return parsed

def _positive_int_quantity(quantity: Decimal) -> int:
    if type(quantity) is not Decimal or not quantity.is_finite() or quantity <= 0:
        raise ValueError("TqSdk order quantity must be a positive finite Decimal")
    integral = quantity.to_integral_value()
    if integral != quantity:
        raise ValueError("TqSdk futures order quantity must be whole lots")
    return int(integral)

def _exchange(concrete_contract_id: str) -> str:
    if "." not in concrete_contract_id:
        raise ValueError("TqSdk concrete contract must include exchange prefix")
    return concrete_contract_id.split(".", 1)[0]

def project_order_to_tqsdk_direction(instruction: BrokerOrderInstruction) -> str:
    if instruction.action is OrderAction.OPEN:
        return "BUY" if instruction.direction is PositionDirection.LONG else "SELL"
    return "SELL" if instruction.direction is PositionDirection.LONG else "BUY"

def _project_side_from_tq(direction: str, offset: str) -> tuple[PositionDirection, OrderAction]:
    if direction not in ("BUY", "SELL"):
        raise ValueError("unsupported TqSdk order direction")
    if offset == "OPEN":
        return (PositionDirection.LONG if direction == "BUY" else PositionDirection.SHORT,
                OrderAction.OPEN)
    if offset in ("CLOSE", "CLOSETODAY"):
        return (PositionDirection.SHORT if direction == "BUY" else PositionDirection.LONG,
                OrderAction.CLOSE)
    raise ValueError("unsupported TqSdk order offset")

def _snapshot_time(value: Any, fallback: datetime) -> datetime:
    for name in ("last_msg_time", "insert_date_time", "trade_date_time"):
        raw = _field(value, name)
        if raw not in (None, "", 0, "0"):
            try:
                ns = int(raw)
                seconds, remainder = divmod(ns, 1_000_000_000)
                return datetime.fromtimestamp(seconds, tz=ZoneInfo("Asia/Shanghai")).replace(
                    microsecond=remainder // 1_000)
            except (TypeError, ValueError, OSError, OverflowError):
                pass
    return fallback

def map_tqsdk_account(raw: Any, *, account_id: str,
                       snapshot_at: datetime) -> BrokerAccountSnapshot:
    if snapshot_at.tzinfo is None:
        raise ValueError("account snapshot time must be timezone-aware")
    balance = _decimal(_field(raw, "balance"), "account.balance")
    float_profit = _decimal(_field(raw, "float_profit", 0), "account.float_profit")
    cash_balance = balance - float_profit
    if cash_balance < 0:
        raise ValueError("mapped broker cash balance cannot be negative")
    return BrokerAccountSnapshot(
        account_id=account_id, snapshot_at=snapshot_at, cash_balance=cash_balance,
        reserved_margin=max(Decimal("0"), _decimal(_field(raw, "margin", 0), "account.margin")),
        charged_costs=max(Decimal("0"), _decimal(_field(raw, "commission", 0), "account.commission")),
        realized_pnl=_decimal(_field(raw, "close_profit", 0), "account.close_profit"),
        unrealized_pnl=float_profit, currency="CNY",
    )

def map_tqsdk_positions(raw_positions: Mapping[str, Any], *,
                         snapshot_at: datetime) -> tuple[BrokerPositionSnapshot, ...]:
    if snapshot_at.tzinfo is None:
        raise ValueError("position snapshot time must be timezone-aware")
    result: list[BrokerPositionSnapshot] = []
    for symbol, raw in sorted(raw_positions.items()):
        if not isinstance(symbol, str) or "." not in symbol:
            continue
        long_qty = _decimal(_field(raw, "pos_long", 0), "position.pos_long")
        short_qty = _decimal(_field(raw, "pos_short", 0), "position.pos_short")
        if long_qty > 0:
            result.append(BrokerPositionSnapshot(
                concrete_contract_id=symbol, direction=PositionDirection.LONG,
                quantity=long_qty,
                average_price=_decimal(_field(raw, "open_price_long"), "position.open_price_long"),
                snapshot_at=snapshot_at,
            ))
        if short_qty > 0:
            result.append(BrokerPositionSnapshot(
                concrete_contract_id=symbol, direction=PositionDirection.SHORT,
                quantity=short_qty,
                average_price=_decimal(_field(raw, "open_price_short"), "position.open_price_short"),
                snapshot_at=snapshot_at,
            ))
    return tuple(result)

def _project_order_status(raw: Any) -> str:
    status = str(_field(raw, "status", ""))
    original = _decimal(_field(raw, "volume_orign"), "order.volume_orign")
    left = _decimal(_field(raw, "volume_left"), "order.volume_left")
    if original <= 0 or left < 0 or left > original:
        raise ValueError("invalid TqSdk order volumes")
    if status == "ALIVE":
        return "PARTIALLY_FILLED" if left < original else "LIVE"
    if status != "FINISHED":
        raise ValueError("unsupported TqSdk order status")
    if left == 0:
        return "FILLED"
    if bool(_field(raw, "is_error", False)):
        return "REJECTED"
    return "CANCELLED"

def map_tqsdk_orders(raw_orders: Mapping[str, Any], *,
                      snapshot_at: datetime) -> tuple[BrokerOrderSnapshot, ...]:
    if snapshot_at.tzinfo is None:
        raise ValueError("order snapshot time must be timezone-aware")
    result: list[BrokerOrderSnapshot] = []
    for key, raw in sorted(raw_orders.items()):
        native_order_id = _field(raw, "order_id", key)
        order_id = native_order_id if isinstance(native_order_id, str) else ""
        exchange_id = str(_field(raw, "exchange_id", ""))
        instrument_id = str(_field(raw, "instrument_id", ""))
        symbol = f"{exchange_id}.{instrument_id}" if exchange_id and instrument_id else str(_field(raw, "symbol", ""))
        project_direction, action = _project_side_from_tq(
            str(_field(raw, "direction", "")), str(_field(raw, "offset", "")))
        original = _decimal(_field(raw, "volume_orign"), "order.volume_orign")
        left = _decimal(_field(raw, "volume_left"), "order.volume_left")
        native_client_request_id = _field(raw, "client_request_id", order_id)
        client_request_id = native_client_request_id if isinstance(native_client_request_id, str) else ""
        if not order_id.strip() or not client_request_id.strip() or not symbol or "." not in symbol:
            raise ValueError("TqSdk order is missing stable identity")
        result.append(BrokerOrderSnapshot(
            order_id=order_id,
            client_request_id=client_request_id,
            concrete_contract_id=symbol, direction=project_direction, action=action,
            status=_project_order_status(raw), requested_quantity=original,
            filled_quantity=original-left, snapshot_at=snapshot_at,
        ))
    if len({item.order_id for item in result}) != len(result):
        raise ValueError("TqSdk snapshot contains duplicate broker order id")
    return tuple(result)

class TqSdkPaperExecutionDriver:
    """Injected-session driver used behind TqSdkPaperBrokerAdapter."""

    def __init__(self, *, broker_id: str, account_identity: str,
                 session_factory: Callable[[], TqSdkSession], order_journal: PaperOrderJournal,
                 authority: PaperExecutionAuthority,
                 close_offset_policy: TqSdkCloseOffsetPolicy | None = None,
                 execution_price_policy: TqSdkExecutionPricePolicy | None = None) -> None:
        if not broker_id or not account_identity:
            raise ValueError("TqSdk driver requires broker and account identities")
        if not isinstance(order_journal, PaperOrderJournal):
            raise ValueError("TqSdk driver requires PaperOrderJournal")
        if not isinstance(authority, PaperExecutionAuthority):
            raise ValueError("TqSdk driver requires PaperExecutionAuthority")
        self._broker_id = broker_id
        self._account_identity = account_identity
        self._factory = session_factory
        self._journal = order_journal
        self._authority = authority
        self._close_offset_policy = close_offset_policy
        self._execution_price_policy = execution_price_policy
        self._session: TqSdkSession | None = None
        self._connection_state = BrokerConnectionState.DISCONNECTED
        self._outbox: list[BrokerEvent] = []
        self._sequence = 0
        self._seen_orders: set[str] = set()
        self._seen_trades: set[str] = set()
        self._terminal_events: set[str] = set()
        self._last_snapshot_at: datetime | None = None

    @property
    def broker_id(self) -> str:
        return self._broker_id
    @property
    def connection_state(self) -> BrokerConnectionState:
        return self._connection_state
    @property
    def authority(self) -> PaperExecutionAuthority:
        return self._authority

    def _emit(self, event_type: BrokerEventType, *, occurred_at: datetime,
              order_id: str | None = None, client_request_id: str | None = None,
              **payload: Any) -> None:
        event_id = sha256(json.dumps({
            "broker": self._broker_id, "sequence": self._sequence, "type": event_type.value,
            "order_id": order_id, "client_request_id": client_request_id, "payload": payload,
        }, ensure_ascii=False, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()
        self._outbox.append(BrokerEvent(
            event_id=event_id, event_type=event_type, occurred_at=occurred_at,
            stream_id=f"{self._broker_id}:paper", sequence=self._sequence,
            order_id=order_id, client_request_id=client_request_id, payload=event_pairs(**payload),
        ))
        self._sequence += 1

    def connect(self) -> None:
        self._authority.require_connect()
        if self._session is not None:
            return
        session = self._factory()
        if session is None:
            raise RuntimeError("TQSDK_SESSION_FACTORY_RETURNED_NONE")
        self._session = session
        self._connection_state = BrokerConnectionState.CONNECTED
        self._emit(BrokerEventType.CONNECTION_STATE,
                   occurred_at=datetime.now(ZoneInfo("Asia/Shanghai")),
                   connection_state=BrokerConnectionState.CONNECTED.value)

    def disconnect(self) -> None:
        if self._session is not None:
            self._session.close()
        self._session = None
        self._connection_state = BrokerConnectionState.DISCONNECTED
        self._emit(BrokerEventType.CONNECTION_STATE,
                   occurred_at=datetime.now(ZoneInfo("Asia/Shanghai")),
                   connection_state=BrokerConnectionState.DISCONNECTED.value)

    def _require_session(self) -> TqSdkSession:
        if self._session is None or self._connection_state is not BrokerConnectionState.CONNECTED:
            raise RuntimeError("TQSDK_PAPER_NOT_CONNECTED")
        return self._session

    def _resolve_offset(self, instruction: BrokerOrderInstruction) -> str:
        if instruction.action is OrderAction.OPEN:
            return "OPEN"
        exchange = _exchange(instruction.concrete_contract_id)
        if exchange not in _SHFE_STYLE:
            return "CLOSE"
        if self._close_offset_policy is None:
            raise RuntimeError("SHFE_CLOSE_OFFSET_POLICY_REQUIRED")
        position = self._require_session().get_positions().get(instruction.concrete_contract_id)
        children = self._close_offset_policy.resolve(instruction, position)
        quantity = _positive_int_quantity(instruction.quantity)
        if len(children) != 1 or children[0].volume != quantity:
            raise RuntimeError("COMPOUND_SHFE_CLOSE_REQUIRES_EXPLICIT_CHILD_ORDER_ENVELOPES")
        return children[0].offset

    def _resolve_limit_price(self, instruction: BrokerOrderInstruction,
                             session: TqSdkSession) -> Decimal:
        if instruction.order_type is OrderType.STOP_MARKET:
            raise RuntimeError("TQSDK_STOP_MARKET_MUST_BE_PROJECT_TRIGGERED_BEFORE_SUBMIT")
        if instruction.order_type is OrderType.LIMIT:
            if instruction.limit_price is None:
                raise ValueError("LIMIT instruction requires limit price")
            return instruction.limit_price
        if self._execution_price_policy is None:
            raise RuntimeError("PAPER_EXECUTION_PRICE_POLICY_REQUIRED")
        price = self._execution_price_policy.resolve_limit_price(instruction, session)
        if type(price) is not Decimal or not price.is_finite() or price <= 0:
            raise ValueError("execution price policy must return positive finite Decimal")
        return price

    def submit_order(self, instruction: BrokerOrderInstruction) -> str:
        if not isinstance(instruction, BrokerOrderInstruction):
            raise ValueError("TqSdk driver requires BrokerOrderInstruction")
        self._authority.require_order_submit(instruction.concrete_contract_id)
        session = self._require_session()
        entry = self._journal.get(instruction.client_request_id)
        if entry.status != PREPARED:
            raise RuntimeError("PAPER_ORDER_MUST_BE_DURABLY_PREPARED_BEFORE_SUBMIT")
        volume = _positive_int_quantity(instruction.quantity)
        offset = self._resolve_offset(instruction)
        direction = project_order_to_tqsdk_direction(instruction)
        limit_price = self._resolve_limit_price(instruction, session)
        self._journal.mark_attempt_started(instruction.client_request_id,
                                           at=datetime.now(ZoneInfo("Asia/Shanghai")))
        try:
            raw_order = session.insert_order(
                symbol=instruction.concrete_contract_id, direction=direction, offset=offset,
                volume=volume, limit_price=float(limit_price),
                order_id=instruction.client_request_id,
            )
        except Exception as error:
            self._journal.mark_unknown_after_submit(
                instruction.client_request_id, safe_reason=type(error).__name__,
                at=datetime.now(ZoneInfo("Asia/Shanghai")))
            raise
        order_id = str(_field(raw_order, "order_id", instruction.client_request_id))
        if not order_id:
            self._journal.mark_unknown_after_submit(
                instruction.client_request_id, safe_reason="MISSING_ORDER_ID_AFTER_INSERT",
                at=datetime.now(ZoneInfo("Asia/Shanghai")))
            raise RuntimeError("TQSDK_INSERT_RETURNED_NO_ORDER_ID")
        self._journal.mark_broker_order_known(
            instruction.client_request_id, broker_order_id=order_id,
            at=datetime.now(ZoneInfo("Asia/Shanghai")))
        return order_id

    def cancel_order(self, order_id: str) -> None:
        if not isinstance(order_id, str) or not order_id.strip():
            raise ValueError("cancel requires order id")
        self._authority.require_order_cancel()
        session = self._require_session()
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        operation = self._journal.prepare_cancel_for_broker_order(order_id, at=now)
        self._journal.mark_cancel_attempt_started(operation.cancel_operation_id, at=now)
        try:
            session.cancel_order(order_id)
        except Exception as error:
            self._journal.mark_unknown_cancel(
                operation.cancel_operation_id,
                safe_reason=type(error).__name__,
                at=datetime.now(ZoneInfo("Asia/Shanghai")),
            )
            raise

    def replace_order(self, order_id: str, new_quantity: Decimal) -> None:
        raise RuntimeError("TQSDK_REPLACE_REQUIRES_PROJECT_CANCEL_REPLACE_POLICY")

    def poll(self) -> bool:
        session = self._require_session()
        updated = bool(session.wait_update())
        now = datetime.now(ZoneInfo("Asia/Shanghai"))
        self._last_snapshot_at = now
        raw_orders = session.get_orders()
        raw_trades = session.get_trades()
        snapshots = map_tqsdk_orders(raw_orders, snapshot_at=now)
        recovery_blockers = self._journal.reconcile_broker_orders(snapshots, observed_at=now)
        if recovery_blockers:
            raise RuntimeError("PAPER_ORDER_RECOVERY_BLOCKED:" + ";".join(recovery_blockers))
        known_requests = set(self._journal.expected_client_request_ids())
        snapshot_by_order_id = {item.order_id: item for item in snapshots}
        raw_by_order_id = {
            str(_field(raw, "order_id", order_key)): raw
            for order_key, raw in raw_orders.items()
        }
        for snapshot in snapshots:
            if snapshot.client_request_id not in known_requests or snapshot.order_id in self._seen_orders:
                continue
            self._emit(BrokerEventType.ORDER_SUBMITTED, occurred_at=snapshot.snapshot_at,
                       order_id=snapshot.order_id, client_request_id=snapshot.client_request_id,
                       concrete_contract_id=snapshot.concrete_contract_id, direction=snapshot.direction.value,
                       action=snapshot.action.value, quantity=str(snapshot.requested_quantity),
                       order_type=OrderType.LIMIT.value, lifecycle_status="LIVE")
            self._seen_orders.add(snapshot.order_id)
        trades: list[tuple[str, Any]] = []
        for trade_key, raw in raw_trades.items():
            trade_id = str(_field(raw, "trade_id", trade_key))
            order_id = str(_field(raw, "order_id", ""))
            snapshot = snapshot_by_order_id.get(order_id)
            if trade_id not in self._seen_trades and snapshot is not None and snapshot.client_request_id in known_requests:
                trades.append((trade_id, raw))
        trades.sort(key=lambda item: (_snapshot_time(item[1], now), item[0]))
        for trade_id, raw in trades:
            order_id = str(_field(raw, "order_id", ""))
            order = raw_by_order_id.get(order_id)
            if order is None:
                raise RuntimeError("TQSDK_TRADE_REFERENCES_UNKNOWN_ORDER")
            snapshot = snapshot_by_order_id[order_id]
            self._emit(BrokerEventType.ORDER_FILLED, occurred_at=_snapshot_time(raw, now),
                       order_id=order_id, client_request_id=snapshot.client_request_id,
                       concrete_contract_id=snapshot.concrete_contract_id, direction=snapshot.direction.value,
                       action=snapshot.action.value,
                       price=str(_decimal(_field(raw, "price"), "trade.price")),
                       quantity=str(_decimal(_field(raw, "volume"), "trade.volume")))
            self._seen_trades.add(trade_id)
        for snapshot in snapshots:
            if snapshot.client_request_id not in known_requests or snapshot.order_id in self._terminal_events:
                continue
            status = snapshot.status
            if status not in ("CANCELLED", "REJECTED"):
                continue
            event_type = BrokerEventType.ORDER_REJECTED if status == "REJECTED" else BrokerEventType.ORDER_CANCELLED
            self._emit(event_type, occurred_at=snapshot.snapshot_at,
                       order_id=snapshot.order_id, client_request_id=snapshot.client_request_id)
            self._terminal_events.add(snapshot.order_id)
        return updated

    def drain_events(self) -> tuple[BrokerEvent, ...]:
        events = tuple(self._outbox)
        self._outbox.clear()
        return events

    def fetch_account_snapshot(self) -> BrokerAccountSnapshot:
        session = self._require_session()
        now = self._last_snapshot_at or datetime.now(ZoneInfo("Asia/Shanghai"))
        return map_tqsdk_account(session.get_account(), account_id=self._account_identity,
                                 snapshot_at=now)
    def fetch_position_snapshot(self) -> tuple[BrokerPositionSnapshot, ...]:
        session = self._require_session()
        now = self._last_snapshot_at or datetime.now(ZoneInfo("Asia/Shanghai"))
        return map_tqsdk_positions(session.get_positions(), snapshot_at=now)
    def fetch_order_snapshot(self) -> tuple[BrokerOrderSnapshot, ...]:
        session = self._require_session()
        now = self._last_snapshot_at or datetime.now(ZoneInfo("Asia/Shanghai"))
        return map_tqsdk_orders(session.get_orders(), snapshot_at=now)
    def capture_snapshot(self) -> Any:
        return {"schema_version": TQSDK_PAPER_DRIVER_VERSION,
                "account": self.fetch_account_snapshot(),
                "positions": self.fetch_position_snapshot(),
                "orders": self.fetch_order_snapshot(),
                "connection_state": self._connection_state}
    def restore_snapshot(self, snapshot: Any) -> None:
        raise RuntimeError("EXTERNAL_BROKER_TRUTH_CANNOT_BE_RESTORED_FROM_LOCAL_SNAPSHOT")

class TqSdkApiSession:
    """Thin wrapper around an already-created TqApi + TqKq/TqSim account.

    Creating TqApi/account (including authentication) is deliberately outside
    this class and belongs to the later account-login boundary.
    """
    def __init__(self, api: Any, account: Any) -> None:
        if api is None or account is None:
            raise ValueError("native TqSdk session requires api and account objects")
        self._api = api
        self._account = account
    def insert_order(self, **kwargs: Any) -> Any:
        return self._api.insert_order(account=self._account, **kwargs)
    def cancel_order(self, order_or_id: Any) -> None:
        self._api.cancel_order(order_or_id, account=self._account)
    def wait_update(self) -> bool:
        return bool(self._api.wait_update())
    def get_account(self) -> Any:
        return self._api.get_account(account=self._account)
    def get_positions(self) -> Mapping[str, Any]:
        value = self._api.get_position(account=self._account)
        if not isinstance(value, Mapping):
            raise RuntimeError("TQSDK_GET_POSITION_ALL_DID_NOT_RETURN_MAPPING")
        return value
    def get_orders(self) -> Mapping[str, Any]:
        value = self._api.get_order(account=self._account)
        if not isinstance(value, Mapping):
            raise RuntimeError("TQSDK_GET_ORDER_ALL_DID_NOT_RETURN_MAPPING")
        return value
    def get_trades(self) -> Mapping[str, Any]:
        value = self._api.get_trade(account=self._account)
        if not isinstance(value, Mapping):
            raise RuntimeError("TQSDK_GET_TRADE_ALL_DID_NOT_RETURN_MAPPING")
        return value
    def close(self) -> None:
        self._api.close()

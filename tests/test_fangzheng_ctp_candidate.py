from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import json
import subprocess
import sys
import unittest

from src.broker_adapter import BrokerOrderInstruction, OrderType
from src.contract_semantics import CloseOffset, OrderAction, PositionDirection
from src.fangzheng_ctp_candidate import (
    BrokerTruthUnknownError,
    CtpAccountRecord,
    CtpCallback,
    CtpCallbackType,
    CtpCancelAcknowledgement,
    CtpOrderAcknowledgement,
    CtpOrderRecord,
    CtpOrderRejection,
    CtpPositionRecord,
    CtpSessionState,
    CtpSubmitRequest,
    CtpTradeFill,
    CtpTradeRecord,
    CtpTranslationProfile,
    FangzhengCtpBrokerAdapter,
)
from src.order_management import OrderManagementSystem, OrderRequest, OrderStatus
from src.runtime_events import BrokerConnectionState, BrokerEventType


NOW = datetime(2026, 8, 29, 1, 2, tzinfo=timezone.utc)
CONTRACT = "SHFE.rb2601"


class FakeCtpTransport:
    broker_id = "fangzheng-ctp-offline-fake"

    def __init__(self) -> None:
        self.calls: list[str] = []
        self.submits: list[CtpSubmitRequest] = []
        self.cancels = []
        self.callbacks: list[CtpCallback] = []

    def connect(self): self.calls.append("connect")
    def disconnect(self): self.calls.append("disconnect")
    def authenticate(self): self.calls.append("authenticate")
    def login(self): self.calls.append("login")
    def submit_order(self, request): self.submits.append(request)
    def cancel_order(self, request): self.cancels.append(request)
    def request_account(self): self.calls.append("account")
    def request_positions(self): self.calls.append("positions")
    def request_orders(self): self.calls.append("orders")
    def request_trades(self): self.calls.append("trades")
    def drain_callbacks(self):
        result = tuple(self.callbacks)
        self.callbacks.clear()
        return result

    def emit(self, callback_id, callback_type, data=None):
        self.callbacks.append(CtpCallback(callback_id, callback_type, NOW, data))


def profile() -> CtpTranslationProfile:
    return CtpTranslationProfile(
        instruments=((CONTRACT, "opaque-instrument"),),
        sides=((PositionDirection.LONG, OrderAction.OPEN, "opaque-buy"),),
        offsets=((OrderAction.OPEN, None, "opaque-open"),),
        order_types=((OrderType.LIMIT, "opaque-limit"),),
    )


def instruction() -> BrokerOrderInstruction:
    return BrokerOrderInstruction(
        client_request_id="request-1",
        client_order_id="project-order-1",
        strategy_identity_id="decision-risk-order-chain",
        concrete_contract_id=CONTRACT,
        direction=PositionDirection.LONG,
        action=OrderAction.OPEN,
        order_type=OrderType.LIMIT,
        quantity=Decimal("2"),
        limit_price=Decimal("3500"),
    )


class FangzhengCtpCandidateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.transport = FakeCtpTransport()
        self.adapter = FangzhengCtpBrokerAdapter(self.transport, profile())

    def emit_and_pump(self, callback_id, callback_type, data=None):
        self.transport.emit(callback_id, callback_type, data)
        return self.adapter.pump_callbacks()

    def establish_session(self) -> None:
        self.adapter.connect()
        self.emit_and_pump("c1", CtpCallbackType.FRONT_CONNECTED)
        self.adapter.request_authentication()
        self.emit_and_pump("c2", CtpCallbackType.AUTHENTICATED)
        self.adapter.request_login()
        self.emit_and_pump("c3", CtpCallbackType.LOGIN_SUCCEEDED)
        self.emit_and_pump("c4", CtpCallbackType.TRADING_DAY, "20260829")

    def establish_truth(self) -> None:
        self.adapter.refresh_broker_truth()
        self.emit_and_pump("q1", CtpCallbackType.ACCOUNT_SNAPSHOT, CtpAccountRecord(
            "account-opaque", NOW, Decimal("100000"), Decimal("0"), Decimal("0"),
            Decimal("0"), Decimal("0"), "CNY"))
        self.emit_and_pump("q2", CtpCallbackType.POSITION_SNAPSHOT, ())
        self.emit_and_pump("q3", CtpCallbackType.ORDER_SNAPSHOT, ())
        self.emit_and_pump("q4", CtpCallbackType.TRADE_SNAPSHOT, ())

    def test_import_has_no_external_ctp_dependency(self) -> None:
        script = (
            "import json,sys; before=set(sys.modules); "
            "import src.fangzheng_ctp_candidate; "
            "print(json.dumps(sorted(set(sys.modules)-before)))"
        )
        completed = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            text=True,
        )
        added = json.loads(completed.stdout)
        self.assertFalse(any(
            "ctp" in name.lower() and name != "src.fangzheng_ctp_candidate"
            for name in added
        ))

    def test_session_order_and_truth_are_explicit(self) -> None:
        self.establish_session()
        self.assertEqual(self.adapter.session_state, CtpSessionState.READY_FOR_RECONCILIATION)
        self.assertEqual(self.adapter.connection_state, BrokerConnectionState.CONNECTED)
        self.assertEqual(self.adapter.trading_day, "20260829")
        self.assertFalse(self.adapter.ready)
        with self.assertRaises(BrokerTruthUnknownError):
            self.adapter.fetch_account_snapshot()
        self.establish_truth()
        self.assertTrue(self.adapter.ready)
        self.assertEqual(self.transport.calls, ["connect", "authenticate", "login", "account", "positions", "orders", "trades"])

    def test_out_of_order_login_fails_closed(self) -> None:
        self.adapter.connect()
        self.emit_and_pump("bad", CtpCallbackType.LOGIN_SUCCEEDED)
        self.assertEqual(self.adapter.session_state, CtpSessionState.UNKNOWN)
        self.assertFalse(self.adapter.ready)

    def test_submit_translation_is_deterministic_and_idempotent(self) -> None:
        self.establish_session()
        self.establish_truth()
        first_id = self.adapter.submit_order(instruction())
        second_id = self.adapter.submit_order(instruction())
        self.assertEqual(first_id, "project-order-1")
        self.assertEqual(first_id, second_id)
        self.assertEqual(len(self.transport.submits), 1)
        translated = self.transport.submits[0]
        self.assertEqual(translated.instrument_id, "opaque-instrument")
        self.assertEqual(translated.limit_price, "3500")
        self.assertEqual(translated.identity_id, profile().translate_submit(instruction()).identity_id)

    def test_ack_partial_full_fill_and_duplicate_callback_are_idempotent(self) -> None:
        self.establish_session()
        self.establish_truth()
        self.adapter.submit_order(instruction())
        ack = CtpOrderAcknowledgement("project-order-1", "request-1", "broker-order-x", "opaque-cancel-token")
        events = self.emit_and_pump("ack", CtpCallbackType.ORDER_ACKNOWLEDGED, ack)
        self.assertEqual(events[0].event_type, BrokerEventType.ORDER_SUBMITTED)
        duplicate = self.emit_and_pump("ack", CtpCallbackType.ORDER_ACKNOWLEDGED, ack)
        self.assertEqual(duplicate, ())
        replayed = self.emit_and_pump("ack-replayed", CtpCallbackType.ORDER_ACKNOWLEDGED, ack)
        self.assertEqual(replayed, ())

        oms = OrderManagementSystem()
        oms.create_order(OrderRequest(
            client_request_id="request-1", client_order_id="project-order-1",
            concrete_contract_id=CONTRACT, direction=PositionDirection.LONG,
            action=OrderAction.OPEN, order_type=OrderType.LIMIT, quantity=Decimal("2"),
            limit_price=Decimal("3500")), NOW)
        oms.apply_broker_event(events[0])
        partial = self.emit_and_pump("fill-1", CtpCallbackType.TRADE_FILLED,
            CtpTradeFill("project-order-1", "request-1", "broker-order-x", "trade-1", Decimal("1"), Decimal("3500")))[0]
        replayed_fill = self.emit_and_pump("fill-1-replayed", CtpCallbackType.TRADE_FILLED,
            CtpTradeFill("project-order-1", "request-1", "broker-order-x", "trade-1", Decimal("1"), Decimal("3500")))
        self.assertEqual(replayed_fill, ())
        full = self.emit_and_pump("fill-2", CtpCallbackType.TRADE_FILLED,
            CtpTradeFill("project-order-1", "request-1", "broker-order-x", "trade-2", Decimal("1"), Decimal("3501")))[0]
        self.assertEqual(oms.apply_broker_event(partial).status, OrderStatus.PARTIALLY_FILLED)
        self.assertEqual(oms.apply_broker_event(full).status, OrderStatus.FILLED)

    def test_reject_cancel_and_unknown_error(self) -> None:
        self.establish_session()
        self.establish_truth()
        self.adapter.submit_order(instruction())
        rejected = self.emit_and_pump("reject", CtpCallbackType.ORDER_REJECTED,
            CtpOrderRejection("project-order-1", "request-1", "opaque-code", "rejected"))[0]
        self.assertEqual(rejected.event_type, BrokerEventType.ORDER_REJECTED)

        ack = CtpOrderAcknowledgement("project-order-1", "request-1", "broker-order-x", "opaque-token")
        self.emit_and_pump("ack-cancel", CtpCallbackType.ORDER_ACKNOWLEDGED, ack)
        self.adapter.cancel_order("project-order-1")
        self.assertEqual(self.transport.cancels[0].broker_order_id, "broker-order-x")
        cancelled = self.emit_and_pump("cancel", CtpCallbackType.CANCEL_ACKNOWLEDGED,
            CtpCancelAcknowledgement("project-order-1", "request-1", "broker-order-x"))[0]
        self.assertEqual(cancelled.event_type, BrokerEventType.ORDER_CANCELLED)

        self.emit_and_pump("error", CtpCallbackType.ERROR,
            CtpOrderRejection("project-order-1", "request-1", "unknown", "ambiguous"))
        self.assertFalse(self.adapter.ready)
        with self.assertRaises(BrokerTruthUnknownError):
            self.adapter.submit_order(instruction())

    def test_disconnect_reconnect_requires_fresh_queries(self) -> None:
        self.establish_session()
        self.establish_truth()
        self.emit_and_pump("disconnect", CtpCallbackType.DISCONNECTED)
        self.assertEqual(self.adapter.connection_state, BrokerConnectionState.RECONNECTING)
        self.emit_and_pump("reconnected", CtpCallbackType.FRONT_CONNECTED)
        self.assertFalse(self.adapter.ready)
        with self.assertRaises(BrokerTruthUnknownError):
            self.adapter.fetch_order_snapshot()

    def test_unsolicited_stale_snapshot_cannot_restore_truth(self) -> None:
        self.establish_session()
        account = CtpAccountRecord("account", NOW, Decimal("10"), Decimal("0"), Decimal("0"), Decimal("0"), Decimal("0"), "CNY")
        self.emit_and_pump("stale-account", CtpCallbackType.ACCOUNT_SNAPSHOT, account)
        self.assertEqual(self.adapter.session_state, CtpSessionState.UNKNOWN)
        with self.assertRaises(BrokerTruthUnknownError):
            self.adapter.fetch_account_snapshot()

    def test_query_snapshots_map_to_project_contract(self) -> None:
        self.establish_session()
        self.adapter.refresh_broker_truth()
        account = CtpAccountRecord("account", NOW, Decimal("10"), Decimal("1"), Decimal("0"), Decimal("0"), Decimal("0"), "CNY")
        position = CtpPositionRecord(CONTRACT, PositionDirection.LONG, Decimal("1"), Decimal("3500"), NOW)
        order = CtpOrderRecord("project-order-1", "request-1", "broker-order-x", CONTRACT,
            PositionDirection.LONG, OrderAction.OPEN, "PARTIALLY_FILLED", Decimal("2"), Decimal("1"), NOW)
        trade = CtpTradeRecord("trade-1", "project-order-1", "broker-order-x", Decimal("1"), Decimal("3500"), NOW)
        self.emit_and_pump("a", CtpCallbackType.ACCOUNT_SNAPSHOT, account)
        self.emit_and_pump("p", CtpCallbackType.POSITION_SNAPSHOT, (position,))
        self.emit_and_pump("o", CtpCallbackType.ORDER_SNAPSHOT, (order,))
        self.emit_and_pump("t", CtpCallbackType.TRADE_SNAPSHOT, (trade,))
        self.assertTrue(self.adapter.ready)
        self.assertEqual(self.adapter.fetch_order_snapshot()[0].order_id, "project-order-1")
        self.assertEqual(self.adapter.fetch_trade_snapshot(), (trade,))

    def test_sensitive_fields_are_rejected_and_not_serialized(self) -> None:
        with self.assertRaisesRegex(ValueError, "secret-bearing"):
            CtpCallback("secret", CtpCallbackType.UNKNOWN, NOW, {"password": "do-not-store"})
        rendered = repr(instruction()) + repr(profile()) + repr(self.adapter)
        self.assertNotIn("password", rendered.lower())
        self.assertNotIn("credential", rendered.lower())


if __name__ == "__main__":
    unittest.main()

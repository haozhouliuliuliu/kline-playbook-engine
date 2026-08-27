from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zoneinfo import ZoneInfo

from src.broker_adapter import BrokerAccountSnapshot, BrokerOrderInstruction, BrokerOrderSnapshot, OrderType
from src.contract_semantics import OrderAction, PositionDirection
from src.data_substrate import SessionMetadata, SessionWindow
from src.live_market_data import TqSdkClosedBarTracker
from src.market_context import MarketContext
from src.paper_activation_profile import PaperActivationProfile, PaperActivationStatus
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_execution_authority import PaperAuthorityStatus, PaperExecutionAuthority
from src.paper_order_journal import BROKER_ORDER_ID_KNOWN, PREPARED, UNKNOWN_AFTER_SUBMIT, PaperOrderJournal
from src.runtime_events import BrokerConnectionState
from src.tqsdk_paper_candidate import TqSdkPaperBrokerAdapter
from src.tqsdk_paper_driver import TqSdkPaperExecutionDriver, map_tqsdk_account, map_tqsdk_orders, map_tqsdk_positions

TZ = ZoneInfo("Asia/Shanghai")
SYMBOL = "SHFE.rb9999"

def _dt(hour: int, minute: int) -> datetime:
    return datetime(2026, 8, 27, hour, minute, tzinfo=TZ)

def _ns(value: datetime) -> int:
    return int(value.timestamp()) * 1_000_000_000

def _sessions() -> SessionMetadata:
    return SessionMetadata("TEST_ONLY_LIVE_SESSION", (SessionWindow(
        exchange="SHFE", instrument=SYMBOL, trading_day=date(2026, 8, 27),
        start=_dt(9, 0), end=_dt(10, 0), kind="DAY",
    ),))

def _row(minute: int, price: str = "3500") -> dict[str, object]:
    value = Decimal(price)
    return {"datetime": _ns(_dt(9, minute)), "symbol": SYMBOL,
            "open": value, "high": value+Decimal("5"), "low": value-Decimal("5"),
            "close": value+Decimal("1"), "volume": 100, "open_oi": 1000, "close_oi": 1001}

def _prepare(journal: PaperOrderJournal, request_id: str = "req-1") -> None:
    journal.prepare(client_request_id=request_id, trader_identity="trader",
                    wake_identity=f"wake-{request_id}", decision_identity=f"decision-{request_id}",
                    intent_identity=f"intent-{request_id}", risk_identity=f"risk-{request_id}",
                    concrete_contract_id=SYMBOL, prepared_at=_dt(9, 0))

class LiveMarketDataTests(unittest.TestCase):
    def test_bootstrap_suppresses_history_and_emits_only_new_closed_bar(self) -> None:
        tracker = TqSdkClosedBarTracker(exchange="SHFE", concrete_instrument=SYMBOL,
            duration_seconds=300, timezone="Asia/Shanghai", sessions=_sessions())
        self.assertEqual(tracker.bootstrap([_row(0), _row(5), _row(10)], observed_at=_dt(9, 12)), ())
        self.assertEqual(tracker.watermark_start, _dt(9, 5))
        emitted = tracker.poll([_row(0), _row(5), _row(10)], observed_at=_dt(9, 16))
        self.assertEqual(len(emitted), 1)
        self.assertEqual(emitted[0].completed_bar.start, _dt(9, 10))
        context = MarketContext(instrument=SYMBOL, concrete_contract_id=SYMBOL,
            last_completed_bar=emitted[0], observed_at=_dt(9, 16),
            staleness_threshold=timedelta(minutes=5))
        self.assertEqual(context.latest_price(), Decimal("3501"))

    def test_gap_is_fail_closed(self) -> None:
        tracker = TqSdkClosedBarTracker(exchange="SHFE", concrete_instrument=SYMBOL,
            duration_seconds=300, timezone="Asia/Shanghai", sessions=_sessions())
        tracker.bootstrap([_row(0)], observed_at=_dt(9, 6))
        with self.assertRaisesRegex(ValueError, "LIVE_BAR_SEQUENCE_MISMATCH"):
            tracker.poll([_row(0), _row(10)], observed_at=_dt(9, 16))

class ActivationAndJournalTests(unittest.TestCase):
    def test_active_profile_requires_every_binding(self) -> None:
        pending = PaperActivationProfile(profile_id="paper-v1", status=PaperActivationStatus.PENDING,
            execution_mode="PAPER", tqsdk_runtime_version="3.10.2",
            live_data_policy_identity=None, sizing_policy_identity=None,
            execution_price_policy_identity=None, close_offset_policy_identity=None,
            risk_policy_identity=None, broker_adapter_identity=None)
        with self.assertRaises(PermissionError): pending.require_active_for(SYMBOL)
        with self.assertRaisesRegex(ValueError, "every execution policy binding"):
            PaperActivationProfile(profile_id="paper-v1", status=PaperActivationStatus.ACTIVE,
                execution_mode="PAPER", tqsdk_runtime_version="3.10.2",
                live_data_policy_identity="live", sizing_policy_identity=None,
                execution_price_policy_identity="price", close_offset_policy_identity="offset",
                risk_policy_identity="risk", broker_adapter_identity="adapter", allowed_contracts=(SYMBOL,))

    def test_journal_survives_restart_and_preserves_unknown(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "orders.sqlite3"
            journal = PaperOrderJournal(path); _prepare(journal)
            with self.assertRaisesRegex(ValueError, "DUPLICATE_PAPER_ORDER_IDENTITY"): _prepare(journal)
            journal.mark_attempt_started("req-1", at=_dt(9, 1)); journal.close()
            journal = PaperOrderJournal(path)
            self.assertEqual(len(journal.unresolved_attempts()), 1)
            journal.mark_unknown_after_submit("req-1", safe_reason="TEST_TRANSPORT_FAILURE", at=_dt(9, 2))
            self.assertEqual(journal.get("req-1").status, UNKNOWN_AFTER_SUBMIT); journal.close()

class BrokerMirrorTests(unittest.TestCase):
    def test_unknown_broker_order_blocks_mirror(self) -> None:
        now = _dt(9, 30); mirror = PaperBrokerTruthMirror(broker_id="tqkq")
        mirror.set_connection_state(BrokerConnectionState.CONNECTED)
        account = BrokerAccountSnapshot(account_id="paper-account", snapshot_at=now,
            cash_balance=Decimal("100000"), reserved_margin=Decimal("0"), charged_costs=Decimal("0"),
            realized_pnl=Decimal("0"), unrealized_pnl=Decimal("0"), currency="CNY")
        order = BrokerOrderSnapshot(order_id="manual-order", client_request_id="manual-order",
            concrete_contract_id=SYMBOL, direction=PositionDirection.LONG, action=OrderAction.OPEN,
            status="LIVE", requested_quantity=Decimal("1"), filled_quantity=Decimal("0"), snapshot_at=now)
        mirror.refresh(account=account, positions=(), orders=(order,), observed_at=now)
        assessment = mirror.assess(expected_client_request_ids=(), assessed_at=now, max_snapshot_age_seconds=10)
        self.assertFalse(assessment.ok)
        self.assertTrue(any(reason.startswith("UNKNOWN_BROKER_ORDER") for reason in assessment.reasons))

class FakeSession:
    def __init__(self, *, fail_insert: bool = False) -> None:
        self.fail_insert = fail_insert; self.insert_calls: list[dict[str, object]] = []
        self.orders: dict[str, object] = {}; self.trades: dict[str, object] = {}; self.positions: dict[str, object] = {}
        self.account = {"balance": 100000, "float_profit": 0, "margin": 0, "commission": 0, "close_profit": 0}
    def insert_order(self, **kwargs: object) -> object:
        self.insert_calls.append(dict(kwargs))
        if self.fail_insert: raise RuntimeError("fake submit failure")
        order_id = str(kwargs["order_id"])
        raw = {"order_id": order_id, "exchange_id": "SHFE", "instrument_id": "rb9999",
               "direction": kwargs["direction"], "offset": kwargs["offset"],
               "volume_orign": kwargs["volume"], "volume_left": kwargs["volume"],
               "status": "ALIVE", "is_error": False}
        self.orders[order_id] = raw; return raw
    def cancel_order(self, order_or_id: object) -> None: pass
    def wait_update(self) -> bool: return True
    def get_account(self) -> object: return self.account
    def get_positions(self) -> dict[str, object]: return self.positions
    def get_orders(self) -> dict[str, object]: return self.orders
    def get_trades(self) -> dict[str, object]: return self.trades
    def close(self) -> None: pass

class TqSdkDriverTests(unittest.TestCase):
    def test_pending_authority_prevents_session_factory_invocation(self) -> None:
        with TemporaryDirectory() as tmp:
            calls = {"count": 0}
            def factory() -> FakeSession:
                calls["count"] += 1; return FakeSession()
            journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3")
            driver = TqSdkPaperExecutionDriver(broker_id="tq", account_identity="paper",
                session_factory=factory, order_journal=journal)
            authority = PaperExecutionAuthority(authority_id="pending", broker_kind="TQSDK", account_kind="TQKQ",
                status=PaperAuthorityStatus.PENDING, allow_connect=False, allow_order_submit=False)
            adapter = TqSdkPaperBrokerAdapter(driver=driver, authority=authority)
            with self.assertRaises(PermissionError): adapter.connect()
            self.assertEqual(calls["count"], 0); journal.close()

    def test_submit_uses_durable_request_as_tqsdk_order_id(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3"); _prepare(journal); session = FakeSession()
            driver = TqSdkPaperExecutionDriver(broker_id="tq", account_identity="paper",
                session_factory=lambda: session, order_journal=journal); driver.connect()
            instruction = BrokerOrderInstruction(client_request_id="req-1", concrete_contract_id=SYMBOL,
                direction=PositionDirection.LONG, action=OrderAction.OPEN, order_type=OrderType.LIMIT,
                quantity=Decimal("1"), limit_price=Decimal("3500"))
            self.assertEqual(driver.submit_order(instruction), "req-1")
            self.assertEqual(session.insert_calls[0]["order_id"], "req-1")
            self.assertEqual(session.insert_calls[0]["direction"], "BUY")
            self.assertEqual(session.insert_calls[0]["offset"], "OPEN")
            self.assertEqual(journal.get("req-1").status, BROKER_ORDER_ID_KNOWN); journal.close()

    def test_shfe_close_without_offset_policy_fails_before_attempt(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3"); _prepare(journal)
            driver = TqSdkPaperExecutionDriver(broker_id="tq", account_identity="paper",
                session_factory=FakeSession, order_journal=journal); driver.connect()
            instruction = BrokerOrderInstruction(client_request_id="req-1", concrete_contract_id=SYMBOL,
                direction=PositionDirection.LONG, action=OrderAction.CLOSE, order_type=OrderType.LIMIT,
                quantity=Decimal("1"), limit_price=Decimal("3500"))
            with self.assertRaisesRegex(RuntimeError, "SHFE_CLOSE_OFFSET_POLICY_REQUIRED"): driver.submit_order(instruction)
            self.assertEqual(journal.get("req-1").status, PREPARED); journal.close()

    def test_market_order_without_price_policy_fails_before_attempt(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3"); _prepare(journal)
            driver = TqSdkPaperExecutionDriver(broker_id="tq", account_identity="paper",
                session_factory=FakeSession, order_journal=journal); driver.connect()
            instruction = BrokerOrderInstruction(client_request_id="req-1", concrete_contract_id=SYMBOL,
                direction=PositionDirection.LONG, action=OrderAction.OPEN, order_type=OrderType.MARKET, quantity=Decimal("1"))
            with self.assertRaisesRegex(RuntimeError, "PAPER_EXECUTION_PRICE_POLICY_REQUIRED"): driver.submit_order(instruction)
            self.assertEqual(journal.get("req-1").status, PREPARED); journal.close()

    def test_insert_failure_becomes_unknown_after_submit(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3"); _prepare(journal)
            driver = TqSdkPaperExecutionDriver(broker_id="tq", account_identity="paper",
                session_factory=lambda: FakeSession(fail_insert=True), order_journal=journal); driver.connect()
            instruction = BrokerOrderInstruction(client_request_id="req-1", concrete_contract_id=SYMBOL,
                direction=PositionDirection.LONG, action=OrderAction.OPEN, order_type=OrderType.LIMIT,
                quantity=Decimal("1"), limit_price=Decimal("3500"))
            with self.assertRaises(RuntimeError): driver.submit_order(instruction)
            self.assertEqual(journal.get("req-1").status, UNKNOWN_AFTER_SUBMIT); journal.close()

    def test_pure_tqsdk_snapshot_mapping(self) -> None:
        now = _dt(9, 30)
        account = map_tqsdk_account({"balance": 100100, "float_profit": 100, "margin": 5000,
            "commission": 3, "close_profit": 20}, account_id="paper", snapshot_at=now)
        self.assertEqual(account.cash_balance, Decimal("100000"))
        positions = map_tqsdk_positions({SYMBOL: {"pos_long": 1, "open_price_long": 3500,
            "pos_short": 0, "open_price_short": 0}}, snapshot_at=now)
        self.assertEqual(positions[0].quantity, Decimal("1"))
        orders = map_tqsdk_orders({"req-1": {"order_id": "req-1", "exchange_id": "SHFE",
            "instrument_id": "rb9999", "direction": "BUY", "offset": "OPEN",
            "volume_orign": 1, "volume_left": 1, "status": "ALIVE", "is_error": False}}, snapshot_at=now)
        self.assertEqual(orders[0].status, "LIVE")

if __name__ == "__main__": unittest.main()

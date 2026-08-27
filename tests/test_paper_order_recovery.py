from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zoneinfo import ZoneInfo

from src.broker_adapter import BrokerOrderInstruction, BrokerOrderSnapshot, OrderType
from src.contract_semantics import OrderAction, PositionDirection
from src.paper_order_journal import (
    BROKER_ORDER_ID_KNOWN,
    CANCEL_ATTEMPT_STARTED,
    CANCEL_RESOLVED,
    REPLACE_CHILD_SUBMIT_AUTHORIZED,
    REPLACE_RESOLVED,
    UNKNOWN_AFTER_SUBMIT,
    UNKNOWN_BROKER_ORDER,
    UNKNOWN_CANCEL,
    PaperOrderJournal,
)
from src.paper_execution_authority import PaperAuthorityStatus, PaperExecutionAuthority
from src.tqsdk_paper_driver import TqSdkPaperExecutionDriver, map_tqsdk_orders


TZ = ZoneInfo("Asia/Shanghai")
SYMBOL = "SHFE.rb9999"


def _at(minute: int) -> datetime:
    return datetime(2026, 8, 27, 9, minute, tzinfo=TZ)


def _prepare(journal: PaperOrderJournal, request_id: str, *, intent: str | None = None) -> None:
    instruction = BrokerOrderInstruction(
        client_request_id=request_id, concrete_contract_id=SYMBOL,
        direction=PositionDirection.LONG, action=OrderAction.OPEN,
        order_type=OrderType.LIMIT, quantity=Decimal("2"), limit_price=Decimal("1"),
    )
    journal.prepare(
        client_request_id=request_id,
        trader_identity="trader-1",
        wake_identity="wake-" + request_id,
        decision_identity="decision-" + request_id,
        intent_identity=intent or "intent-" + request_id,
        risk_identity="risk-" + request_id,
        concrete_contract_id=SYMBOL,
        instruction=instruction,
        prepared_at=_at(0),
    )


def _authority() -> PaperExecutionAuthority:
    return PaperExecutionAuthority(
        authority_id="test-authority", broker_kind="TEST", account_kind="PAPER",
        status=PaperAuthorityStatus.ACTIVE, allow_connect=True,
        allow_order_submit=True, allow_order_cancel=True,
        allowed_contracts=(SYMBOL,),
    )


def _snapshot(request_id: str, status: str, *, order_id: str | None = None,
              filled: str = "0") -> BrokerOrderSnapshot:
    return BrokerOrderSnapshot(
        order_id=order_id or request_id,
        client_request_id=request_id,
        concrete_contract_id=SYMBOL,
        direction=PositionDirection.LONG,
        action=OrderAction.OPEN,
        status=status,
        requested_quantity=Decimal("2"),
        filled_quantity=Decimal(filled),
        snapshot_at=_at(5),
    )


class FailingCancelSession:
    def __init__(self) -> None:
        self.cancel_calls = 0

    def insert_order(self, **kwargs: object) -> object:
        raise AssertionError("submit is not expected in this test")

    def cancel_order(self, order_or_id: object) -> None:
        self.cancel_calls += 1
        raise TimeoutError("test timeout after external boundary")

    def wait_update(self) -> bool:
        return True

    def get_account(self) -> object:
        return {"balance": 1, "float_profit": 0, "margin": 0, "commission": 0, "close_profit": 0}

    def get_positions(self) -> dict[str, object]:
        return {}

    def get_orders(self) -> dict[str, object]:
        return {}

    def get_trades(self) -> dict[str, object]:
        return {}

    def close(self) -> None:
        pass


class PaperOrderRecoveryTests(unittest.TestCase):
    def test_attempt_without_result_survives_restart_and_absence_is_not_not_sent(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "orders.sqlite3"
            journal = PaperOrderJournal(path)
            _prepare(journal, "request-1")
            journal.mark_attempt_started("request-1", at=_at(1))
            journal.close()

            journal = PaperOrderJournal(path)
            blockers = journal.reconcile_broker_orders((), observed_at=_at(2))
            self.assertIn("UNKNOWN_BROKER_ORDER", blockers)
            self.assertEqual(UNKNOWN_BROKER_ORDER, journal.get("request-1").status)
            with self.assertRaisesRegex(RuntimeError, "PAPER_ORDER_ILLEGAL_TRANSITION"):
                journal.mark_attempt_started("request-1", at=_at(3))
            journal.close()

    def test_cancel_timeout_is_durable_unknown_and_cannot_be_retried(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3")
            _prepare(journal, "request-1")
            journal.mark_attempt_started("request-1", at=_at(1))
            journal.mark_broker_order_known("request-1", broker_order_id="broker-1", at=_at(2))
            session = FailingCancelSession()
            driver = TqSdkPaperExecutionDriver(
                broker_id="fake", account_identity="paper", session_factory=lambda: session,
                order_journal=journal, authority=_authority(),
            )
            driver.connect()
            with self.assertRaises(TimeoutError):
                driver.cancel_order("broker-1")
            cancel = journal.get_cancel("cancel:request-1:broker-1")
            self.assertEqual(UNKNOWN_CANCEL, cancel.status)
            with self.assertRaisesRegex(RuntimeError, "PAPER_CANCEL_ILLEGAL_TRANSITION"):
                driver.cancel_order("broker-1")
            self.assertEqual(1, session.cancel_calls)
            journal.close()

    def test_reconnect_snapshot_resolves_cancel_and_is_idempotent(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3")
            _prepare(journal, "request-1")
            journal.mark_attempt_started("request-1", at=_at(1))
            journal.mark_broker_order_known("request-1", broker_order_id="broker-1", at=_at(2))
            operation = journal.prepare_cancel_for_broker_order("broker-1", at=_at(3))
            journal.mark_cancel_attempt_started(operation.cancel_operation_id, at=_at(3))
            self.assertEqual(CANCEL_ATTEMPT_STARTED, journal.get_cancel(operation.cancel_operation_id).status)
            self.assertEqual((), journal.reconcile_broker_orders((_snapshot("request-1", "CANCELLED", order_id="broker-1"),), observed_at=_at(5)))
            self.assertEqual(CANCEL_RESOLVED, journal.get_cancel(operation.cancel_operation_id).status)
            self.assertEqual((), journal.reconcile_broker_orders((_snapshot("request-1", "CANCELLED", order_id="broker-1"),), observed_at=_at(6)))
            journal.close()

    def test_partial_fill_does_not_resolve_cancel(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3")
            _prepare(journal, "request-1")
            journal.mark_attempt_started("request-1", at=_at(1))
            journal.mark_broker_order_known("request-1", broker_order_id="broker-1", at=_at(2))
            cancel = journal.prepare_cancel_for_broker_order("broker-1", at=_at(3))
            journal.mark_cancel_attempt_started(cancel.cancel_operation_id, at=_at(3))
            blockers = journal.reconcile_broker_orders((_snapshot("request-1", "PARTIALLY_FILLED", order_id="broker-1", filled="1"),), observed_at=_at(5))
            self.assertIn("UNKNOWN_CANCEL", blockers)
            self.assertEqual(CANCEL_ATTEMPT_STARTED, journal.get_cancel(cancel.cancel_operation_id).status)
            journal.close()

    def test_broker_order_envelope_mismatch_becomes_unknown_and_blocks_risk(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3")
            _prepare(journal, "request-1")
            journal.mark_attempt_started("request-1", at=_at(1))
            mismatched = BrokerOrderSnapshot(
                order_id="broker-1", client_request_id="request-1",
                concrete_contract_id="SHFE.ag9999", direction=PositionDirection.LONG,
                action=OrderAction.OPEN, status="LIVE", requested_quantity=Decimal("2"),
                filled_quantity=Decimal("0"), snapshot_at=_at(5),
            )
            blockers = journal.reconcile_broker_orders((mismatched,), observed_at=_at(5))
            self.assertIn("ORDER_ENVELOPE_MISMATCH", blockers)
            self.assertEqual(UNKNOWN_BROKER_ORDER, journal.get("request-1").status)
            journal.close()

    def test_replacement_child_requires_resolved_cancel_and_is_single_use(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3")
            _prepare(journal, "old-request")
            _prepare(journal, "child-request", intent="replacement-intent")
            journal.mark_attempt_started("old-request", at=_at(1))
            journal.mark_broker_order_known("old-request", broker_order_id="old-broker", at=_at(2))
            cancel = journal.prepare_cancel_for_broker_order("old-broker", at=_at(3))
            journal.mark_cancel_attempt_started(cancel.cancel_operation_id, at=_at(3))
            replacement = journal.prepare_replace(
                replace_operation_id="replace:old:1", original_client_request_id="old-request",
                replacement_generation=1, replacement_intent_identity="replacement-intent",
                cancel_operation_id=cancel.cancel_operation_id, child_client_request_id="child-request",
                prepared_at=_at(3),
            )
            with self.assertRaisesRegex(RuntimeError, "CANCEL_NOT_SAFELY_RESOLVED"):
                journal.authorize_replacement_child(replacement.replace_operation_id, at=_at(4))
            journal.resolve_cancel(cancel.cancel_operation_id, final_order_status="CANCELLED", at=_at(5))
            journal.authorize_replacement_child(replacement.replace_operation_id, at=_at(5))
            self.assertEqual(REPLACE_CHILD_SUBMIT_AUTHORIZED, journal.get_replace(replacement.replace_operation_id).status)
            journal.mark_attempt_started("child-request", at=_at(6))
            with self.assertRaisesRegex(RuntimeError, "PAPER_ORDER_ILLEGAL_TRANSITION"):
                journal.mark_attempt_started("child-request", at=_at(6))
            journal.mark_broker_order_known("child-request", broker_order_id="child-broker", at=_at(7))
            self.assertEqual(REPLACE_RESOLVED, journal.get_replace(replacement.replace_operation_id).status)
            journal.close()

    def test_unknown_cancel_prevents_replacement_child_submission(self) -> None:
        with TemporaryDirectory() as tmp:
            journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3")
            _prepare(journal, "old-request")
            _prepare(journal, "child-request", intent="replacement-intent")
            journal.mark_attempt_started("old-request", at=_at(1))
            journal.mark_broker_order_known("old-request", broker_order_id="old-broker", at=_at(2))
            cancel = journal.prepare_cancel_for_broker_order("old-broker", at=_at(3))
            journal.mark_cancel_attempt_started(cancel.cancel_operation_id, at=_at(3))
            journal.mark_unknown_cancel(cancel.cancel_operation_id, safe_reason="TIMEOUT", at=_at(4))
            replacement = journal.prepare_replace(
                replace_operation_id="replace:old:1", original_client_request_id="old-request",
                replacement_generation=1, replacement_intent_identity="replacement-intent",
                cancel_operation_id=cancel.cancel_operation_id, child_client_request_id="child-request",
                prepared_at=_at(4),
            )
            with self.assertRaisesRegex(RuntimeError, "CANCEL_NOT_SAFELY_RESOLVED"):
                journal.authorize_replacement_child(replacement.replace_operation_id, at=_at(5))
            with self.assertRaisesRegex(RuntimeError, "PAPER_REPLACEMENT_CHILD_NOT_AUTHORIZED"):
                journal.mark_attempt_started("child-request", at=_at(5))
            journal.close()

    def test_native_mapping_rejects_duplicate_ids_and_impossible_quantities(self) -> None:
        raw = {
            "one": {"order_id": "same", "exchange_id": "SHFE", "instrument_id": "rb9999", "direction": "BUY", "offset": "OPEN", "volume_orign": 1, "volume_left": 1, "status": "ALIVE"},
            "two": {"order_id": "same", "exchange_id": "SHFE", "instrument_id": "rb9999", "direction": "BUY", "offset": "OPEN", "volume_orign": 1, "volume_left": 1, "status": "ALIVE"},
        }
        with self.assertRaisesRegex(ValueError, "duplicate broker order id"):
            map_tqsdk_orders(raw, snapshot_at=_at(5))
        malformed = {"one": {"order_id": "one", "exchange_id": "SHFE", "instrument_id": "rb9999", "direction": "BUY", "offset": "OPEN", "volume_orign": 1, "volume_left": 2, "status": "ALIVE"}}
        with self.assertRaisesRegex(ValueError, "invalid TqSdk order volumes"):
            map_tqsdk_orders(malformed, snapshot_at=_at(5))


if __name__ == "__main__":
    unittest.main()

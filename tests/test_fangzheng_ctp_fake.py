from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal
import unittest

from src.fangzheng_ctp_candidate import (
    BrokerTruthUnknownError,
    CtpAccountRecord,
    CtpCallback,
    CtpCallbackType,
    CtpCancelRejection,
    CtpOrderAcknowledgement,
    CtpSessionFailure,
    CtpSessionState,
    CtpTradeFill,
    FangzhengCtpBrokerAdapter,
)
from src.fangzheng_ctp_fake import (
    FakeCtpOperation,
    FakeCtpStep,
    ScriptedCtpTransport,
)
from src.runtime_events import BrokerEventType
from tests.test_fangzheng_ctp_candidate import instruction, profile


NOW = datetime(2026, 8, 29, 1, 2, tzinfo=timezone.utc)


def callback(
    callback_id: str,
    callback_type: CtpCallbackType,
    data: object = None,
    *,
    trading_day: str | None = None,
) -> CtpCallback:
    return CtpCallback(callback_id, callback_type, NOW, data, trading_day=trading_day)


def ready_steps() -> tuple[FakeCtpStep, ...]:
    return (
        FakeCtpStep(FakeCtpOperation.CONNECT, (callback("connected", CtpCallbackType.FRONT_CONNECTED),)),
        FakeCtpStep(FakeCtpOperation.AUTHENTICATE, (callback("authenticated", CtpCallbackType.AUTHENTICATED),)),
        FakeCtpStep(FakeCtpOperation.LOGIN, (
            callback("login", CtpCallbackType.LOGIN_SUCCEEDED),
            callback("day", CtpCallbackType.TRADING_DAY, "20260829"),
        )),
        FakeCtpStep(FakeCtpOperation.QUERY_ACCOUNT, (callback(
            "account",
            CtpCallbackType.ACCOUNT_SNAPSHOT,
            CtpAccountRecord(
                "account", NOW, Decimal("100000"), Decimal("0"), Decimal("0"),
                Decimal("0"), Decimal("0"), "CNY",
            ),
            trading_day="20260829",
        ),)),
        FakeCtpStep(FakeCtpOperation.QUERY_POSITIONS, (callback(
            "positions", CtpCallbackType.POSITION_SNAPSHOT, (), trading_day="20260829",
        ),)),
        FakeCtpStep(FakeCtpOperation.QUERY_ORDERS, (callback(
            "orders", CtpCallbackType.ORDER_SNAPSHOT, (), trading_day="20260829",
        ),)),
        FakeCtpStep(FakeCtpOperation.QUERY_TRADES, (callback(
            "trades", CtpCallbackType.TRADE_SNAPSHOT, (), trading_day="20260829",
        ),)),
    )


def establish_ready(adapter: FangzhengCtpBrokerAdapter) -> None:
    adapter.connect()
    adapter.pump_callbacks()
    adapter.request_authentication()
    adapter.pump_callbacks()
    adapter.request_login()
    adapter.pump_callbacks()
    adapter.refresh_broker_truth()
    adapter.pump_callbacks()


class ScriptedCtpTransportTests(unittest.TestCase):
    def test_connection_authentication_and_login_are_fully_scripted(self) -> None:
        transport = ScriptedCtpTransport((
            FakeCtpStep(FakeCtpOperation.CONNECT, (callback("connected", CtpCallbackType.FRONT_CONNECTED),)),
            FakeCtpStep(FakeCtpOperation.AUTHENTICATE, (callback("authenticated", CtpCallbackType.AUTHENTICATED),)),
            FakeCtpStep(FakeCtpOperation.LOGIN, (
                callback("login", CtpCallbackType.LOGIN_SUCCEEDED),
                callback("day", CtpCallbackType.TRADING_DAY, "20260829"),
            )),
        ))
        adapter = FangzhengCtpBrokerAdapter(transport, profile())

        adapter.connect()
        adapter.pump_callbacks()
        adapter.request_authentication()
        adapter.pump_callbacks()
        adapter.request_login()
        adapter.pump_callbacks()

        self.assertEqual(CtpSessionState.READY_FOR_RECONCILIATION, adapter.session_state)
        self.assertEqual("20260829", adapter.trading_day)
        self.assertEqual(
            (FakeCtpOperation.CONNECT, FakeCtpOperation.AUTHENTICATE, FakeCtpOperation.LOGIN),
            transport.operations,
        )
        transport.assert_exhausted()

    def test_authentication_failure_is_injected_and_fails_closed(self) -> None:
        transport = ScriptedCtpTransport((
            FakeCtpStep(FakeCtpOperation.CONNECT, (callback("connected", CtpCallbackType.FRONT_CONNECTED),)),
            FakeCtpStep(FakeCtpOperation.AUTHENTICATE, (
                callback(
                    "auth-failed",
                    CtpCallbackType.AUTHENTICATION_FAILED,
                    CtpSessionFailure("opaque-auth-code", "authentication rejected"),
                ),
            )),
        ))
        adapter = FangzhengCtpBrokerAdapter(transport, profile())

        adapter.connect()
        adapter.pump_callbacks()
        adapter.request_authentication()
        events = adapter.pump_callbacks()

        self.assertEqual(CtpSessionState.UNKNOWN, adapter.session_state)
        self.assertFalse(adapter.ready)
        self.assertEqual("authentication rejected", dict(events[0].payload)["reason"])

    def test_login_failure_is_injected_and_fails_closed(self) -> None:
        transport = ScriptedCtpTransport((
            FakeCtpStep(FakeCtpOperation.CONNECT, (callback("connected", CtpCallbackType.FRONT_CONNECTED),)),
            FakeCtpStep(FakeCtpOperation.AUTHENTICATE, (callback("authenticated", CtpCallbackType.AUTHENTICATED),)),
            FakeCtpStep(FakeCtpOperation.LOGIN, (callback(
                "login-failed",
                CtpCallbackType.LOGIN_FAILED,
                CtpSessionFailure("opaque-login-code", "login rejected"),
            ),)),
        ))
        adapter = FangzhengCtpBrokerAdapter(transport, profile())

        adapter.connect()
        adapter.pump_callbacks()
        adapter.request_authentication()
        adapter.pump_callbacks()
        adapter.request_login()
        events = adapter.pump_callbacks()

        self.assertEqual(CtpSessionState.UNKNOWN, adapter.session_state)
        self.assertEqual("login rejected", dict(events[0].payload)["reason"])

    def test_old_session_callback_after_trading_day_rollover_fails_closed(self) -> None:
        transport = ScriptedCtpTransport(ready_steps())
        adapter = FangzhengCtpBrokerAdapter(transport, profile())
        establish_ready(adapter)
        self.assertTrue(adapter.ready)

        transport.inject_callbacks((callback(
            "rollover", CtpCallbackType.TRADING_DAY, "20260830",
        ),))
        adapter.pump_callbacks()
        self.assertEqual("20260830", adapter.trading_day)
        self.assertFalse(adapter.ready)

        transport.inject_callbacks((callback(
            "old-ack",
            CtpCallbackType.ORDER_ACKNOWLEDGED,
            CtpOrderAcknowledgement("project-order-1", "request-1", "broker-order-1", "token"),
            trading_day="20260829",
        ),))
        with self.assertRaisesRegex(ValueError, "TRADING_DAY_MISMATCH"):
            adapter.pump_callbacks()
        self.assertEqual(CtpSessionState.UNKNOWN, adapter.session_state)

    def test_disconnect_before_submit_prevents_request_from_leaving_project(self) -> None:
        transport = ScriptedCtpTransport(ready_steps())
        adapter = FangzhengCtpBrokerAdapter(transport, profile())
        establish_ready(adapter)

        transport.inject_callbacks((callback("disconnect", CtpCallbackType.DISCONNECTED),))
        adapter.pump_callbacks()
        with self.assertRaises(BrokerTruthUnknownError):
            adapter.submit_order(instruction())

        self.assertEqual((), transport.submits)

    def test_disconnect_immediately_after_submit_is_observable_as_unknown_truth(self) -> None:
        transport = ScriptedCtpTransport(ready_steps() + (
            FakeCtpStep(
                FakeCtpOperation.SUBMIT,
                (callback("disconnect-after-submit", CtpCallbackType.DISCONNECTED),),
                expected_project_order_id="project-order-1",
            ),
        ))
        adapter = FangzhengCtpBrokerAdapter(transport, profile())
        establish_ready(adapter)

        self.assertEqual("project-order-1", adapter.submit_order(instruction()))
        adapter.pump_callbacks()

        self.assertEqual(1, len(transport.submits))
        self.assertEqual(CtpSessionState.RECONNECTING, adapter.session_state)
        self.assertFalse(adapter.ready)

    def test_reconnect_requires_and_accepts_a_new_complete_query_round(self) -> None:
        second_round = tuple(
            replace(step, callbacks=tuple(
                replace(callback_item, callback_id=f"second-{callback_item.callback_id}")
                for callback_item in step.callbacks
            ))
            for step in ready_steps()
        )
        transport = ScriptedCtpTransport(ready_steps() + second_round)
        adapter = FangzhengCtpBrokerAdapter(transport, profile())
        establish_ready(adapter)
        transport.inject_callbacks((callback("disconnect", CtpCallbackType.DISCONNECTED),))
        adapter.pump_callbacks()
        self.assertFalse(adapter.ready)

        establish_ready(adapter)

        self.assertTrue(adapter.ready)
        transport.assert_exhausted()

    def test_failure_after_submit_effect_records_that_request_crossed_transport_seam(self) -> None:
        transport = ScriptedCtpTransport(ready_steps() + (
            FakeCtpStep(
                FakeCtpOperation.SUBMIT,
                expected_project_order_id="project-order-1",
                failure_after_effect="injected timeout after submit effect",
            ),
        ))
        adapter = FangzhengCtpBrokerAdapter(transport, profile())
        establish_ready(adapter)

        with self.assertRaisesRegex(RuntimeError, "timeout after submit effect"):
            adapter.submit_order(instruction())

        self.assertEqual(1, len(transport.submits))
        self.assertEqual(CtpSessionState.UNKNOWN, adapter.session_state)
        with self.assertRaises(BrokerTruthUnknownError):
            adapter.submit_order(instruction())
        self.assertEqual(1, len(transport.submits))

    def test_cancel_reject_is_explicitly_ambiguous_until_fresh_query(self) -> None:
        acknowledgement = CtpOrderAcknowledgement(
            "project-order-1", "request-1", "broker-order-1", "cancel-token",
        )
        transport = ScriptedCtpTransport(ready_steps() + (
            FakeCtpStep(
                FakeCtpOperation.SUBMIT,
                (callback(
                    "ack", CtpCallbackType.ORDER_ACKNOWLEDGED, acknowledgement,
                    trading_day="20260829",
                ),),
                expected_project_order_id="project-order-1",
            ),
            FakeCtpStep(
                FakeCtpOperation.CANCEL,
                (callback(
                    "cancel-rejected",
                    CtpCallbackType.CANCEL_REJECTED,
                    CtpCancelRejection(
                        "project-order-1", "request-1", "broker-order-1",
                        "opaque-cancel-code", "cancel rejected",
                    ),
                    trading_day="20260829",
                ),),
                expected_project_order_id="project-order-1",
            ),
        ))
        adapter = FangzhengCtpBrokerAdapter(transport, profile())
        establish_ready(adapter)
        adapter.submit_order(instruction())
        adapter.pump_callbacks()

        adapter.cancel_order("project-order-1")
        events = adapter.pump_callbacks()

        self.assertEqual(BrokerEventType.ORDER_AMBIGUOUS, events[0].event_type)
        self.assertFalse(adapter.ready)

    def test_missing_query_callback_leaves_truth_incomplete(self) -> None:
        steps = list(ready_steps())
        steps[4] = FakeCtpStep(FakeCtpOperation.QUERY_POSITIONS)
        transport = ScriptedCtpTransport(tuple(steps))
        adapter = FangzhengCtpBrokerAdapter(transport, profile())

        establish_ready(adapter)

        self.assertFalse(adapter.ready)
        with self.assertRaisesRegex(BrokerTruthUnknownError, "POSITIONS_TRUTH_UNKNOWN"):
            adapter.fetch_position_snapshot()

    def test_out_of_order_fill_duplicate_and_conflict_are_deterministic(self) -> None:
        transport = ScriptedCtpTransport(ready_steps() + (
            FakeCtpStep(
                FakeCtpOperation.SUBMIT,
                expected_project_order_id="project-order-1",
            ),
        ))
        adapter = FangzhengCtpBrokerAdapter(transport, profile())
        establish_ready(adapter)
        adapter.submit_order(instruction())
        fill = CtpTradeFill(
            "project-order-1", "request-1", "broker-order-1", "trade-1",
            Decimal("1"), Decimal("3500"),
        )
        out_of_order = callback(
            "fill-before-ack", CtpCallbackType.TRADE_FILLED, fill,
            trading_day="20260829",
        )

        transport.inject_callbacks((out_of_order, out_of_order))
        events = adapter.pump_callbacks()
        self.assertEqual(1, len(events))
        self.assertEqual(BrokerEventType.ORDER_FILLED, events[0].event_type)

        conflicting = replace(
            out_of_order,
            data=replace(fill, quantity=Decimal("2")),
        )
        transport.inject_callbacks((conflicting,))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_CALLBACK_ID_DIFFERENT_CONTENT"):
            adapter.pump_callbacks()
        self.assertEqual(CtpSessionState.UNKNOWN, adapter.session_state)


if __name__ == "__main__":
    unittest.main()

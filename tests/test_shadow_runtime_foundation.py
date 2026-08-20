"""Focused tests for the Shadow Runtime Foundation (SHADOW_RUNTIME_FOUNDATION_V0_1).

Synthetic only: no real broker, no network, no canonical corpus, no candidate
strategy outcome, no real money. All strategies are TEST_ONLY fake strategies.
"""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.broker_adapter import (
    BrokerAccountSnapshot,
    BrokerOrderInstruction,
    BrokerOrderSnapshot,
    BrokerPositionSnapshot,
    OrderType,
)
from src.contract_semantics import OrderAction, PositionDirection
from src.intent import (
    ConflictResolver,
    IntentAction,
    IntentDecision,
    StrategyIntent,
)
from src.market_context import MarketContext
from src.order_management import OrderManagementSystem, OrderRequest
from src.paper_broker import PaperBrokerAdapter, PaperFillPolicy
from src.reconciliation import reconcile_runtime
from src.risk_gate import RiskGate
from src.runtime_events import (
    BrokerConnectionState,
    BrokerEvent,
    BrokerEventLog,
    BrokerEventType,
    BrokerEventViolationKind,
    event_pairs,
)
from src.runtime_ledger import RuntimeLedger, RuntimeLedgerRecordKind
from src.runtime_recovery import capture_persisted_state, rebuild_trading_state
from src.safety import SafetyGate, SafetyViolationKind
from src.shadow_runtime import ShadowRuntime
from src.trading_state import (
    EventApplicationOutcome,
    OrderStatus,
    RuntimeAccountingAssumptions,
    TradingState,
)

from tests.runtime_synthetic_fixture import (
    TEST_STRATEGY_ID,
    TZ,
    ConflictStrategy,
    NoopStrategy,
    OpenLongStrategy,
    OpenThenCloseStrategy,
    intent_from,
    make_accounting,
    make_bar,
    make_config,
    make_contract_spec,
    make_ruleset,
    run_bars,
)

START_AT = datetime(2024, 6, 17, 9, 0, tzinfo=TZ)


def _submit_event(sequence, *, order_id="o1", client_request_id="r1", quantity="1", action="OPEN", at=None):
    return BrokerEvent(
        event_id=f"ev-submit-{sequence}",
        event_type=BrokerEventType.ORDER_SUBMITTED,
        occurred_at=at or START_AT,
        stream_id="paper-broker",
        sequence=sequence,
        order_id=order_id,
        client_request_id=client_request_id,
        payload=event_pairs(
            concrete_contract_id="TEST.IF9999",
            direction="LONG",
            action=action,
            quantity=quantity,
            order_type="MARKET",
        ),
    )


def _fill_event(sequence, *, order_id="o1", price="4000", quantity="1", action="OPEN", at=None):
    return BrokerEvent(
        event_id=f"ev-fill-{sequence}",
        event_type=BrokerEventType.ORDER_FILLED,
        occurred_at=at or START_AT,
        stream_id="paper-broker",
        sequence=sequence,
        order_id=order_id,
        client_request_id="r1",
        payload=event_pairs(
            concrete_contract_id="TEST.IF9999",
            direction="LONG",
            action=action,
            price=price,
            quantity=quantity,
        ),
    )


def _make_state():
    ledger = RuntimeLedger()
    return TradingState(
        runtime_id="t",
        runtime_version="v1",
        created_at=START_AT,
        starting_capital=Decimal("1000000"),
        contract_specs=(make_contract_spec(),),
        accounting=make_accounting(),
        ledger=ledger,
    ), ledger


class BrokerEventTests(unittest.TestCase):
    def test_event_identity_deterministic(self):
        a = _submit_event(0)
        b = _submit_event(0)
        self.assertEqual(a.identity_id, b.identity_id)

    def test_event_identity_sensitive_to_content(self):
        a = _submit_event(0)
        changed = BrokerEvent(
            event_id="ev-submit-0",
            event_type=BrokerEventType.ORDER_SUBMITTED,
            occurred_at=START_AT,
            stream_id="paper-broker",
            sequence=0,
            order_id="o1",
            client_request_id="r1",
            payload=event_pairs(
                concrete_contract_id="TEST.IF9999",
                direction="LONG",
                action="OPEN",
                quantity="2",
                order_type="MARKET",
            ),
        )
        self.assertNotEqual(a.identity_id, changed.identity_id)

    def test_event_validation_fail_closed(self):
        with self.assertRaises(ValueError):
            BrokerEvent(
                event_id="", event_type=BrokerEventType.ORDER_SUBMITTED,
                occurred_at=START_AT, stream_id="s", sequence=0,
            )
        with self.assertRaises(ValueError):
            BrokerEvent(
                event_id="e", event_type=BrokerEventType.ORDER_SUBMITTED,
                occurred_at=datetime(2024, 1, 1), stream_id="s", sequence=0,
            )
        with self.assertRaises(ValueError):
            BrokerEvent(
                event_id="e", event_type=BrokerEventType.ORDER_SUBMITTED,
                occurred_at=START_AT, stream_id="s", sequence=-1,
            )
        with self.assertRaises(ValueError):
            BrokerEvent(
                event_id="e", event_type=BrokerEventType.ORDER_SUBMITTED,
                occurred_at=START_AT, stream_id="s", sequence=0,
                payload=(("b", "1"), ("a", "1")),
            )

    def test_event_log_projection(self):
        log = BrokerEventLog(applied_events=(_submit_event(0), _fill_event(1)))
        self.assertEqual(log.applied_event_ids, ("ev-submit-0", "ev-fill-1"))
        self.assertEqual(log.stream_high_water, (("paper-broker", 1),))

    def test_event_log_rejects_duplicate_ids(self):
        with self.assertRaises(ValueError):
            BrokerEventLog(applied_events=(_submit_event(0), _submit_event(0)))

    def test_event_log_rejects_non_monotonic(self):
        with self.assertRaises(ValueError):
            BrokerEventLog(applied_events=(_fill_event(1), _submit_event(0)))


class TradingStateTests(unittest.TestCase):
    def test_open_fill_accounting(self):
        state, _ = _make_state()
        r1 = state.apply_broker_event(_submit_event(0))
        self.assertTrue(r1.applied)
        r2 = state.apply_broker_event(_fill_event(1, price="4000"))
        self.assertTrue(r2.applied)
        pos = state.position_for("TEST.IF9999", PositionDirection.LONG)
        self.assertIsNotNone(pos)
        self.assertEqual(pos.quantity, Decimal("1"))
        self.assertEqual(pos.average_open_price, Decimal("4000"))
        # reserved = 1 * 4000 * 300 * 0.10
        self.assertEqual(state.account.reserved_margin, Decimal("120000"))
        self.assertEqual(state.account.charged_costs, Decimal("5"))
        self.assertEqual(state.account.cash_balance, Decimal("999995"))
        self.assertEqual(state.orders[0].status, OrderStatus.FILLED)

    def test_duplicate_event_idempotent_noop(self):
        state, _ = _make_state()
        state.apply_broker_event(_submit_event(0))
        state.apply_broker_event(_fill_event(1, price="4000"))
        snapshot = state.event_log_projection().identity_id
        result = state.apply_broker_event(_fill_event(1, price="4000"))
        self.assertEqual(result.outcome, EventApplicationOutcome.APPLIED_ALREADY_NOOP)
        self.assertEqual(state.event_log_projection().identity_id, snapshot)
        self.assertEqual(state.position_for("TEST.IF9999", PositionDirection.LONG).quantity, Decimal("1"))
        self.assertEqual(state.account.charged_costs, Decimal("5"))

    def test_duplicate_event_id_different_content_rejected(self):
        state, _ = _make_state()
        state.apply_broker_event(_submit_event(0))
        state.apply_broker_event(_fill_event(1, price="4000"))
        dup = BrokerEvent(
            event_id="ev-fill-1",
            event_type=BrokerEventType.ORDER_FILLED,
            occurred_at=START_AT,
            stream_id="paper-broker",
            sequence=1,
            order_id="o1",
            client_request_id="r1",
            payload=event_pairs(
                concrete_contract_id="TEST.IF9999",
                direction="LONG",
                action="OPEN",
                price="9999",
                quantity="1",
            ),
        )
        result = state.apply_broker_event(dup)
        self.assertEqual(
            result.outcome,
            EventApplicationOutcome.REJECTED_DUPLICATE_EVENT_ID_DIFFERENT_CONTENT,
        )
        self.assertEqual(
            state.event_violations()[0].kind,
            BrokerEventViolationKind.DUPLICATE_EVENT_ID_DIFFERENT_CONTENT,
        )
        # The rejected event must not change state.
        self.assertEqual(state.position_for("TEST.IF9999", PositionDirection.LONG).average_open_price, Decimal("4000"))

    def test_out_of_order_rejected(self):
        state, _ = _make_state()
        state.apply_broker_event(_submit_event(0))
        late = _submit_event(0)  # same event id -> duplicate no-op
        self.assertEqual(state.apply_broker_event(late).outcome, EventApplicationOutcome.APPLIED_ALREADY_NOOP)
        # A genuinely new event with an older sequence is out-of-order.
        out_of_order = BrokerEvent(
            event_id="ev-submit-old",
            event_type=BrokerEventType.ORDER_SUBMITTED,
            occurred_at=START_AT,
            stream_id="paper-broker",
            sequence=0,
            order_id="o-old",
            client_request_id="r-old",
            payload=event_pairs(
                concrete_contract_id="TEST.IF9999",
                direction="LONG",
                action="OPEN",
                quantity="1",
                order_type="MARKET",
            ),
        )
        result = state.apply_broker_event(out_of_order)
        self.assertEqual(result.outcome, EventApplicationOutcome.REJECTED_OUT_OF_ORDER)
        self.assertEqual(state.event_violations()[-1].kind, BrokerEventViolationKind.OUT_OF_ORDER)
        self.assertIsNone(state.order_for("o-old"))

    def test_sequence_gap_rejected(self):
        state, _ = _make_state()
        state.apply_broker_event(_submit_event(0))
        gap = _submit_event(2, order_id="o-gap", client_request_id="r-gap")
        result = state.apply_broker_event(gap)
        self.assertEqual(result.outcome, EventApplicationOutcome.REJECTED_SEQUENCE_GAP)
        self.assertEqual(state.event_violations()[-1].kind, BrokerEventViolationKind.SEQUENCE_GAP)

    def test_invalid_content_rejected(self):
        state, _ = _make_state()
        bad = BrokerEvent(
            event_id="ev-bad",
            event_type=BrokerEventType.ORDER_SUBMITTED,
            occurred_at=START_AT,
            stream_id="paper-broker",
            sequence=0,
            order_id="o-bad",
            client_request_id="r-bad",
            payload=event_pairs(
                concrete_contract_id="TEST.UNKNOWN",
                direction="LONG",
                action="OPEN",
                quantity="1",
                order_type="MARKET",
            ),
        )
        result = state.apply_broker_event(bad)
        self.assertEqual(result.outcome, EventApplicationOutcome.REJECTED_INVALID_CONTENT)
        self.assertEqual(state.event_violations()[-1].kind, BrokerEventViolationKind.INVALID_CONTENT)

    def test_close_realizes_pnl(self):
        state, ledger = _make_state()
        state.apply_broker_event(_submit_event(0))
        state.apply_broker_event(_fill_event(1, price="4000"))
        state.apply_broker_event(_submit_event(2, order_id="o2", client_request_id="r2", action="CLOSE"))
        close = BrokerEvent(
            event_id="ev-close-3",
            event_type=BrokerEventType.ORDER_FILLED,
            occurred_at=START_AT,
            stream_id="paper-broker",
            sequence=3,
            order_id="o2",
            client_request_id="r2",
            payload=event_pairs(
                concrete_contract_id="TEST.IF9999",
                direction="LONG",
                action="CLOSE",
                price="4010",
                quantity="1",
            ),
        )
        state.apply_broker_event(close)
        self.assertIsNone(state.position_for("TEST.IF9999", PositionDirection.LONG))
        self.assertEqual(state.account.realized_pnl, Decimal("3000"))
        self.assertEqual(state.account.charged_costs, Decimal("10"))
        # cash = 1,000,000 + 3,000 - 10
        self.assertEqual(state.account.cash_balance, Decimal("1002990"))
        self.assertTrue(ledger.verify_chain())

    def test_over_close_fails_closed(self):
        state, _ = _make_state()
        state.apply_broker_event(_submit_event(0))
        state.apply_broker_event(_fill_event(1, price="4000"))
        state.apply_broker_event(_submit_event(2, order_id="o2", client_request_id="r2", action="CLOSE"))
        over = BrokerEvent(
            event_id="ev-over-3",
            event_type=BrokerEventType.ORDER_FILLED,
            occurred_at=START_AT,
            stream_id="paper-broker",
            sequence=3,
            order_id="o2",
            client_request_id="r2",
            payload=event_pairs(
                concrete_contract_id="TEST.IF9999",
                direction="LONG",
                action="CLOSE",
                price="4010",
                quantity="5",
            ),
        )
        result = state.apply_broker_event(over)
        self.assertEqual(result.outcome, EventApplicationOutcome.REJECTED_INVALID_CONTENT)

    def test_mark_position_updates_unrealized(self):
        state, _ = _make_state()
        state.apply_broker_event(_submit_event(0))
        state.apply_broker_event(_fill_event(1, price="4000"))
        state.mark_position("TEST.IF9999", PositionDirection.LONG, Decimal("4050"), START_AT)
        pos = state.position_for("TEST.IF9999", PositionDirection.LONG)
        self.assertEqual(pos.unrealized_pnl, Decimal("15000"))
        self.assertEqual(state.account.unrealized_pnl, Decimal("15000"))

    def test_ledger_records_kinds(self):
        state, ledger = _make_state()
        state.apply_broker_event(_submit_event(0))
        state.apply_broker_event(_fill_event(1, price="4000"))
        kinds = [record.record_kind for record in ledger.records()]
        self.assertIn(RuntimeLedgerRecordKind.ORDER, kinds)
        self.assertIn(RuntimeLedgerRecordKind.FILL, kinds)
        self.assertIn(RuntimeLedgerRecordKind.POSITION_TRANSITION, kinds)
        self.assertIn(RuntimeLedgerRecordKind.BROKER_EVENT, kinds)
        self.assertTrue(ledger.verify_chain())


class OMSTests(unittest.TestCase):
    def _order(self):
        oms = OrderManagementSystem()
        request = OrderRequest(
            client_request_id="r1",
            concrete_contract_id="TEST.IF9999",
            direction=PositionDirection.LONG,
            action=OrderAction.OPEN,
            order_type=OrderType.MARKET,
            quantity=Decimal("1"),
            strategy_identity_id=TEST_STRATEGY_ID,
        )
        return oms, oms.create_order(request, START_AT)

    def test_create_and_lifecycle(self):
        oms, order = self._order()
        self.assertEqual(order.status, OrderStatus.PENDING_SUBMIT)
        order = oms.apply_broker_event(_submit_event(0, order_id=order.order_id, client_request_id="r1"))
        self.assertEqual(order.status, OrderStatus.LIVE)
        order = oms.apply_broker_event(_fill_event(1, order_id=order.order_id, price="4000"))
        self.assertEqual(order.status, OrderStatus.FILLED)
        self.assertEqual(order.average_fill_price, Decimal("4000"))

    def test_duplicate_client_request_rejected(self):
        oms, order = self._order()
        with self.assertRaises(ValueError):
            oms.create_order(
                OrderRequest(
                    client_request_id="r1",
                    concrete_contract_id="TEST.IF9999",
                    direction=PositionDirection.LONG,
                    action=OrderAction.OPEN,
                    order_type=OrderType.MARKET,
                    quantity=Decimal("1"),
                ),
                START_AT,
            )

    def test_cancel_lifecycle(self):
        oms, order = self._order()
        oms.apply_broker_event(_submit_event(0, order_id=order.order_id, client_request_id="r1"))
        pending = oms.cancel(order.order_id, START_AT)
        self.assertEqual(pending.status, OrderStatus.CANCEL_PENDING)
        cancelled = oms.apply_broker_event(
            BrokerEvent(
                event_id="ev-cancel-1",
                event_type=BrokerEventType.ORDER_CANCELLED,
                occurred_at=START_AT,
                stream_id="paper-broker",
                sequence=1,
                order_id=order.order_id,
                client_request_id="r1",
            )
        )
        self.assertEqual(cancelled.status, OrderStatus.CANCELLED)

    def test_replace_lifecycle(self):
        oms, order = self._order()
        oms.apply_broker_event(_submit_event(0, order_id=order.order_id, client_request_id="r1"))
        pending = oms.replace(order.order_id, Decimal("3"), START_AT)
        self.assertEqual(pending.status, OrderStatus.REPLACE_PENDING)
        replaced = oms.apply_broker_event(
            BrokerEvent(
                event_id="ev-replace-1",
                event_type=BrokerEventType.ORDER_REPLACED,
                occurred_at=START_AT,
                stream_id="paper-broker",
                sequence=1,
                order_id=order.order_id,
                client_request_id="r1",
                payload=event_pairs(new_quantity="3"),
            )
        )
        self.assertEqual(replaced.status, OrderStatus.REPLACED)
        self.assertEqual(replaced.quantity, Decimal("3"))


class PaperBrokerTests(unittest.TestCase):
    def _broker(self, policy=PaperFillPolicy.IMMEDIATE_MARKET_AT_REFERENCE):
        return PaperBrokerAdapter(
            broker_id="paper-1",
            contract_specs=(make_contract_spec(),),
            accounting=make_accounting(),
            starting_capital=Decimal("1000000"),
            currency="CNY",
            fill_policy=policy,
        )

    def _instruction(self, *, action=OrderAction.OPEN, direction=PositionDirection.LONG, order_type=OrderType.MARKET, quantity=Decimal("1"), limit_price=None, client_request_id="r1"):
        return BrokerOrderInstruction(
            client_request_id=client_request_id,
            concrete_contract_id="TEST.IF9999",
            direction=direction,
            action=action,
            order_type=order_type,
            quantity=quantity,
            limit_price=limit_price,
        )

    def test_immediate_market_fill_events(self):
        broker = self._broker()
        order_id = broker.submit_order(self._instruction(), reference_price=Decimal("4000"), at=START_AT)
        events = broker.drain_events()
        self.assertEqual([e.event_type for e in events], [BrokerEventType.ORDER_SUBMITTED, BrokerEventType.ORDER_FILLED])
        self.assertEqual([e.sequence for e in events], [0, 1])
        self.assertEqual([e.identity_id for e in events], [e.identity_id for e in events])
        snap = broker.fetch_position_snapshot()
        self.assertEqual(len(snap), 1)
        self.assertEqual(snap[0].quantity, Decimal("1"))

    def test_deterministic_sequence(self):
        broker = self._broker()
        broker.submit_order(self._instruction(), reference_price=Decimal("4000"), at=START_AT)
        broker.drain_events()
        broker.submit_order(self._instruction(client_request_id="r2"), reference_price=Decimal("4010"), at=START_AT)
        events = broker.drain_events()
        self.assertEqual([e.sequence for e in events], [2, 3])

    def test_resting_policy_market_fill_at_open(self):
        broker = self._broker(policy=PaperFillPolicy.RESTING_ON_COMPLETED_BAR)
        broker.submit_order(self._instruction(), at=START_AT)
        broker.drain_events()
        events = broker.ingest_completed_bar(make_bar(0, Decimal("4000")), at=START_AT + timedelta(minutes=1))
        fills = [e for e in events if e.event_type is BrokerEventType.ORDER_FILLED]
        self.assertEqual(len(fills), 1)
        self.assertEqual(dict(fills[0].payload)["price"], "4000")

    def test_resting_policy_limit_fill_when_crossed(self):
        broker = self._broker(policy=PaperFillPolicy.RESTING_ON_COMPLETED_BAR)
        broker.submit_order(
            self._instruction(order_type=OrderType.LIMIT, limit_price=Decimal("4000")),
            at=START_AT,
        )
        broker.drain_events()
        events = broker.ingest_completed_bar(make_bar(0, Decimal("3990")), at=START_AT + timedelta(minutes=1))
        fills = [e for e in events if e.event_type is BrokerEventType.ORDER_FILLED]
        self.assertEqual(len(fills), 1)
        self.assertEqual(dict(fills[0].payload)["price"], "4000")

    def test_cancel_and_replace_events(self):
        broker = self._broker(policy=PaperFillPolicy.RESTING_ON_COMPLETED_BAR)
        order_id = broker.submit_order(self._instruction(), at=START_AT)
        broker.drain_events()
        broker.cancel_order(order_id, at=START_AT)
        events = broker.drain_events()
        self.assertEqual([e.event_type for e in events], [BrokerEventType.ORDER_CANCELLED])
        with self.assertRaises(ValueError):
            broker.cancel_order(order_id, at=START_AT)

    def test_snapshot_capture_restore(self):
        broker = self._broker()
        broker.submit_order(self._instruction(), reference_price=Decimal("4000"), at=START_AT)
        broker.drain_events()
        snapshot = broker.capture_snapshot(at=START_AT + timedelta(minutes=1))
        restored = self._broker()
        restored.restore_snapshot(snapshot)
        self.assertEqual(restored.capture_snapshot(at=START_AT + timedelta(minutes=1)).identity_id, snapshot.identity_id)

    def test_disconnect_blocks_submit(self):
        broker = self._broker()
        broker.disconnect()
        with self.assertRaises(ValueError):
            broker.submit_order(self._instruction(), reference_price=Decimal("4000"), at=START_AT)


class ConflictResolutionTests(unittest.TestCase):
    def test_hold_neutral(self):
        context = MarketContext(
            instrument="TEST.IF9999",
            concrete_contract_id="TEST.IF9999",
            last_completed_bar=make_bar(0, Decimal("4000")),
            observed_at=START_AT,
            staleness_threshold=timedelta(minutes=5),
        )
        hold = intent_from(context, action=IntentAction.HOLD, marker="hold-1")
        resolution = ConflictResolver().resolve((hold,))
        self.assertEqual(resolution.resolutions[0].decision, IntentDecision.NEUTRAL)

    def test_duplicate_intent_collapses(self):
        context = MarketContext(
            instrument="TEST.IF9999",
            concrete_contract_id="TEST.IF9999",
            last_completed_bar=make_bar(0, Decimal("4000")),
            observed_at=START_AT,
            staleness_threshold=timedelta(minutes=5),
        )
        one = intent_from(context, action=IntentAction.OPEN, direction=PositionDirection.LONG, quantity=Decimal("1"), marker="same")
        dup = intent_from(context, action=IntentAction.OPEN, direction=PositionDirection.LONG, quantity=Decimal("1"), marker="same")
        resolution = ConflictResolver().resolve((one, dup))
        self.assertEqual(len(resolution.resolutions), 1)
        self.assertEqual(resolution.resolutions[0].decision, IntentDecision.APPROVED)

    def test_conflicting_intents_both_rejected(self):
        context = MarketContext(
            instrument="TEST.IF9999",
            concrete_contract_id="TEST.IF9999",
            last_completed_bar=make_bar(0, Decimal("4000")),
            observed_at=START_AT,
            staleness_threshold=timedelta(minutes=5),
        )
        a = intent_from(context, action=IntentAction.OPEN, direction=PositionDirection.LONG, quantity=Decimal("1"), marker="a")
        b = intent_from(context, action=IntentAction.OPEN, direction=PositionDirection.LONG, quantity=Decimal("2"), marker="b")
        resolution = ConflictResolver().resolve((a, b))
        self.assertEqual(
            {item.decision for item in resolution.resolutions},
            {IntentDecision.REJECTED_CONFLICT},
        )


class RiskGateTests(unittest.TestCase):
    def _context(self):
        return MarketContext(
            instrument="TEST.IF9999",
            concrete_contract_id="TEST.IF9999",
            last_completed_bar=make_bar(0, Decimal("4000")),
            observed_at=START_AT,
            staleness_threshold=timedelta(minutes=5),
        )

    def _intent(self, quantity=Decimal("1")):
        context = self._context()
        return intent_from(context, action=IntentAction.OPEN, direction=PositionDirection.LONG, quantity=quantity, marker="risk")

    def _state(self):
        ledger = RuntimeLedger()
        return TradingState(
            runtime_id="t", runtime_version="v1", created_at=START_AT,
            starting_capital=Decimal("1000000"), contract_specs=(make_contract_spec(),),
            accounting=make_accounting(), ledger=ledger,
        )

    def test_approve_within_limits(self):
        gate = RiskGate(make_ruleset())
        decision = gate.evaluate(self._intent(), self._state(), self._context(), safety_blocking=False, connection_connected=True)
        self.assertTrue(decision.approved)
        self.assertEqual(decision.quantity_for_order, Decimal("1"))

    def test_reject_over_max_order_quantity(self):
        gate = RiskGate(make_ruleset(max_order_quantity=Decimal("5")))
        decision = gate.evaluate(self._intent(quantity=Decimal("6")), self._state(), self._context(), safety_blocking=False, connection_connected=True)
        self.assertFalse(decision.approved)
        self.assertIn("ORDER_QUANTITY", decision.reason)

    def test_reject_resulting_position_over_limit(self):
        state = self._state()
        state.apply_broker_event(_submit_event(0, quantity="8"))
        state.apply_broker_event(_fill_event(1, price="4000", quantity="8"))
        gate = RiskGate(make_ruleset(max_position_quantity=Decimal("8")))
        decision = gate.evaluate(self._intent(quantity=Decimal("1")), state, self._context(), safety_blocking=False, connection_connected=True)
        self.assertFalse(decision.approved)
        self.assertIn("RESULTING_POSITION", decision.reason)

    def test_reject_opposite_direction_flip(self):
        state = self._state()
        state.apply_broker_event(_submit_event(0))
        state.apply_broker_event(_fill_event(1, price="4000"))
        gate = RiskGate(make_ruleset(allow_opposite_direction_flip=False))
        context = self._context()
        short_intent = intent_from(context, action=IntentAction.OPEN, direction=PositionDirection.SHORT, quantity=Decimal("1"), marker="flip")
        decision = gate.evaluate(short_intent, state, context, safety_blocking=False, connection_connected=True)
        self.assertFalse(decision.approved)
        self.assertIn("OPPOSITE_DIRECTION", decision.reason)

    def test_reject_max_open_positions(self):
        gate = RiskGate(make_ruleset(max_open_positions=1))
        # State with two concrete contracts so a second NEW position is possible.
        ledger = RuntimeLedger()
        state = TradingState(
            runtime_id="t", runtime_version="v1", created_at=START_AT,
            starting_capital=Decimal("1000000"),
            contract_specs=(
                make_contract_spec(),
                make_contract_spec(instrument="TEST.RB9999", multiplier=Decimal("10"), tick=Decimal("1")),
            ),
            accounting=make_accounting(), ledger=ledger,
        )
        # First open on TEST.IF9999 is fine (count becomes 1).
        decision = gate.evaluate(self._intent(), state, self._context(), safety_blocking=False, connection_connected=True)
        self.assertTrue(decision.approved)
        state.apply_broker_event(_submit_event(0))
        state.apply_broker_event(_fill_event(1, price="4000"))
        # Opening a SECOND position on a different contract exceeds max open positions.
        context2 = MarketContext(
            instrument="TEST.RB9999", concrete_contract_id="TEST.RB9999",
            last_completed_bar=make_bar(1, Decimal("4000")), observed_at=START_AT + timedelta(minutes=1),
            staleness_threshold=timedelta(minutes=5),
        )
        intent2 = intent_from(context2, action=IntentAction.OPEN, direction=PositionDirection.LONG, quantity=Decimal("1"), marker="second")
        decision2 = gate.evaluate(intent2, state, context2, safety_blocking=False, connection_connected=True)
        self.assertFalse(decision2.approved)
        self.assertIn("MAX_OPEN_POSITIONS", decision2.reason)

    def test_reject_stale_open(self):
        old_context = MarketContext(
            instrument="TEST.IF9999", concrete_contract_id="TEST.IF9999",
            last_completed_bar=make_bar(0, Decimal("4000")), observed_at=START_AT,
            staleness_threshold=timedelta(minutes=1),
        )
        # Evaluate at a much later time so the context is stale.
        intent = intent_from(old_context, action=IntentAction.OPEN, direction=PositionDirection.LONG, quantity=Decimal("1"), marker="stale")
        intent = StrategyIntent(
            intent_id=intent.intent_id, strategy_identity_id=intent.strategy_identity_id,
            instrument=intent.instrument, concrete_contract_id=intent.concrete_contract_id,
            action=intent.action, decision_at=START_AT + timedelta(hours=2),
            context_identity=intent.context_identity, direction=intent.direction,
            quantity=intent.quantity, reason=intent.reason,
        )
        gate = RiskGate(make_ruleset(allow_open_when_stale=False))
        decision = gate.evaluate(intent, self._state(), old_context, safety_blocking=False, connection_connected=True)
        self.assertFalse(decision.approved)
        self.assertIn("STALE", decision.reason)

    def test_reject_safety_blocking(self):
        gate = RiskGate(make_ruleset())
        decision = gate.evaluate(self._intent(), self._state(), self._context(), safety_blocking=True, connection_connected=True)
        self.assertFalse(decision.approved)
        self.assertIn("SAFETY_BLOCKING", decision.reason)


class ReconciliationTests(unittest.TestCase):
    def _state_with_long(self, quantity=Decimal("1")):
        state, _ = _make_state()
        state.apply_broker_event(_submit_event(0))
        state.apply_broker_event(_fill_event(1, price="4000", quantity=str(quantity)))
        return state

    def _broker_snapshots(self, state, *, account_overrides=None, position_delta=None, order_status=None):
        account = BrokerAccountSnapshot(
            account_id="acc",
            snapshot_at=START_AT,
            cash_balance=state.account.cash_balance,
            reserved_margin=state.account.reserved_margin,
            charged_costs=state.account.charged_costs,
            realized_pnl=state.account.realized_pnl,
            unrealized_pnl=state.account.unrealized_pnl,
            currency="CNY",
        )
        if account_overrides:
            for key, value in account_overrides.items():
                account = BrokerAccountSnapshot(
                    account_id=account.account_id, snapshot_at=account.snapshot_at,
                    cash_balance=value if key == "cash_balance" else account.cash_balance,
                    reserved_margin=value if key == "reserved_margin" else account.reserved_margin,
                    charged_costs=value if key == "charged_costs" else account.charged_costs,
                    realized_pnl=value if key == "realized_pnl" else account.realized_pnl,
                    unrealized_pnl=value if key == "unrealized_pnl" else account.unrealized_pnl,
                    currency=account.currency,
                )
        positions = [
            BrokerPositionSnapshot(
                concrete_contract_id=p.concrete_contract_id,
                direction=p.direction,
                quantity=p.quantity + (position_delta or Decimal("0")),
                average_price=p.average_open_price,
                snapshot_at=START_AT,
            )
            for p in state.positions
        ]
        orders = [
            BrokerOrderSnapshot(
                order_id=o.order_id,
                client_request_id=o.client_request_id,
                concrete_contract_id=o.concrete_contract_id,
                direction=o.direction,
                action=o.action,
                status=o.status.value if order_status is None else order_status,
                requested_quantity=o.requested_quantity,
                filled_quantity=o.filled_quantity,
                snapshot_at=START_AT,
            )
            for o in state.orders
        ]
        return account, positions, orders

    def test_consistent_state_ok(self):
        state = self._state_with_long()
        account, positions, orders = self._broker_snapshots(state)
        report = reconcile_runtime(state, account, positions, orders, START_AT)
        self.assertTrue(report.ok)
        self.assertEqual(report.mismatches, ())

    def test_account_mismatch_fails_closed(self):
        state = self._state_with_long()
        account, positions, orders = self._broker_snapshots(state, account_overrides={"cash_balance": Decimal("1")})
        report = reconcile_runtime(state, account, positions, orders, START_AT)
        self.assertFalse(report.ok)
        self.assertIn("ACCOUNT_CASH_MISMATCH", report.mismatches)

    def test_position_mismatch_fails_closed(self):
        state = self._state_with_long()
        account, positions, orders = self._broker_snapshots(state, position_delta=Decimal("1"))
        report = reconcile_runtime(state, account, positions, orders, START_AT)
        self.assertFalse(report.ok)
        self.assertTrue(any("POSITION" in item for item in report.mismatches))

    def test_order_mismatch_fails_closed(self):
        state = self._state_with_long()
        account, positions, orders = self._broker_snapshots(state, order_status="CANCELLED")
        report = reconcile_runtime(state, account, positions, orders, START_AT)
        self.assertFalse(report.ok)
        self.assertTrue(any("ORDER_STATUS" in item for item in report.mismatches))


class SafetyGateTests(unittest.TestCase):
    def _state(self):
        ledger = RuntimeLedger()
        return TradingState(
            runtime_id="t", runtime_version="v1", created_at=START_AT,
            starting_capital=Decimal("1000000"), contract_specs=(make_contract_spec(),),
            accounting=make_accounting(), ledger=ledger,
        )

    def _context(self, observed_at=None):
        bar = make_bar(0, Decimal("4000"))
        return MarketContext(
            instrument="TEST.IF9999",
            concrete_contract_id="TEST.IF9999",
            last_completed_bar=bar,
            observed_at=observed_at or bar.completed_bar.available_at,
            staleness_threshold=timedelta(minutes=5),
        )

    def _stale_context(self, now):
        # A completed bar whose evidence is older than the staleness threshold.
        old_end = now - timedelta(hours=1)
        bar = make_bar(0, Decimal("4000"), session_start=old_end - timedelta(minutes=1))
        return MarketContext(
            instrument="TEST.IF9999",
            concrete_contract_id="TEST.IF9999",
            last_completed_bar=bar,
            observed_at=bar.completed_bar.available_at,
            staleness_threshold=timedelta(minutes=5),
        )

    def test_nominal(self):
        gate = SafetyGate()
        clock_now = START_AT + timedelta(minutes=1)  # bar0 available_at
        assessment = gate.assess(
            state=self._state(), clock_now=clock_now, context=self._context(),
            connection_state=BrokerConnectionState.CONNECTED, reconciliation=None,
        )
        self.assertTrue(assessment.nominal)
        self.assertFalse(assessment.blocking)

    def test_stale_data(self):
        gate = SafetyGate()
        clock_now = START_AT + timedelta(minutes=1)
        context = self._stale_context(clock_now)
        assessment = gate.assess(
            state=self._state(), clock_now=clock_now, context=context,
            connection_state=BrokerConnectionState.CONNECTED, reconciliation=None,
        )
        self.assertTrue(any(v.kind is SafetyViolationKind.STALE_MARKET_DATA for v in assessment.violations))

    def test_broker_disconnect(self):
        gate = SafetyGate()
        clock_now = START_AT + timedelta(minutes=1)
        assessment = gate.assess(
            state=self._state(), clock_now=clock_now, context=self._context(),
            connection_state=BrokerConnectionState.DISCONNECTED, reconciliation=None,
        )
        self.assertTrue(any(v.kind is SafetyViolationKind.BROKER_DISCONNECT for v in assessment.violations))

    def test_kill_switch_blocks(self):
        gate = SafetyGate()
        gate.trip_kill_switch("test", START_AT)
        clock_now = START_AT + timedelta(minutes=1)
        assessment = gate.assess(
            state=self._state(), clock_now=clock_now, context=self._context(),
            connection_state=BrokerConnectionState.CONNECTED, reconciliation=None,
        )
        self.assertTrue(assessment.blocking)
        self.assertTrue(any(v.kind is SafetyViolationKind.KILL_SWITCH_TRIPPED for v in assessment.violations))
        self.assertTrue(gate.is_blocking())

    def test_clock_anomaly(self):
        gate = SafetyGate()
        clock_now = START_AT + timedelta(minutes=1)
        context = self._context(observed_at=clock_now + timedelta(minutes=5))
        assessment = gate.assess(
            state=self._state(), clock_now=clock_now, context=context,
            connection_state=BrokerConnectionState.CONNECTED, reconciliation=None,
        )
        self.assertTrue(any(v.kind is SafetyViolationKind.CLOCK_SESSION_ANOMALY for v in assessment.violations))


class RuntimeLedgerTests(unittest.TestCase):
    def test_chain_integrity(self):
        ledger = RuntimeLedger()
        ledger.append(RuntimeLedgerRecordKind.RUNTIME_START, "a", (), START_AT)
        ledger.append(RuntimeLedgerRecordKind.INTENT, "b", event_pairs(action="OPEN"), START_AT)
        self.assertTrue(ledger.verify_chain())
        self.assertEqual(ledger.count(), 2)
        self.assertEqual(ledger.replay(), ledger.records())

    def test_tamper_breaks_chain(self):
        ledger = RuntimeLedger()
        ledger.append(RuntimeLedgerRecordKind.RUNTIME_START, "a", (), START_AT)
        ledger.append(RuntimeLedgerRecordKind.INTENT, "b", event_pairs(action="OPEN"), START_AT)
        ledger.append(RuntimeLedgerRecordKind.FILL, "c", event_pairs(price="4000"), START_AT)
        # Simulate a silently dropped record (audit-detected tampering).
        ledger._records.pop(1)
        self.assertFalse(ledger.verify_chain())


class ShadowRuntimeEndToEndTests(unittest.TestCase):
    def _runtime(self, strategy, **overrides):
        return ShadowRuntime(
            make_config(**overrides),
            strategy,
            created_at=START_AT,
        )

    def test_full_open_close_round_trip(self):
        runtime = self._runtime(OpenThenCloseStrategy())
        bars = [make_bar(0, Decimal("4000")), make_bar(1, Decimal("4010"))]
        r0 = runtime.on_completed_bar(bars[0])
        self.assertEqual(runtime.state.position_for("TEST.IF9999", PositionDirection.LONG).quantity, Decimal("1"))
        self.assertTrue(r0.reconciliation.ok)
        self.assertTrue(r0.safety.nominal)
        r1 = runtime.on_completed_bar(bars[1])
        self.assertIsNone(runtime.state.position_for("TEST.IF9999", PositionDirection.LONG))
        # realized = (4010-4000)*300*1 = 3000; costs = 2*5 = 10
        self.assertEqual(runtime.state.account.realized_pnl, Decimal("3000"))
        self.assertEqual(runtime.state.account.charged_costs, Decimal("10"))
        self.assertTrue(r1.reconciliation.ok)
        self.assertTrue(runtime.ledger.verify_chain())
        kinds = [record.record_kind for record in runtime.ledger.records()]
        for kind in (
            RuntimeLedgerRecordKind.RUNTIME_START,
            RuntimeLedgerRecordKind.INTENT,
            RuntimeLedgerRecordKind.ORDER,
            RuntimeLedgerRecordKind.FILL,
            RuntimeLedgerRecordKind.POSITION_TRANSITION,
            RuntimeLedgerRecordKind.RECONCILIATION,
        ):
            self.assertIn(kind, kinds)

    def test_duplicate_fill_idempotent(self):
        runtime = self._runtime(OpenThenCloseStrategy())
        runtime.on_completed_bar(make_bar(0, Decimal("4000")))
        # Replay the exact same fill event through the TEST hook: idempotent no-op.
        fill_event = BrokerEvent(
            event_id="ev-fill-replay",
            event_type=BrokerEventType.ORDER_FILLED,
            occurred_at=START_AT,
            stream_id="paper-broker",
            sequence=999,
            order_id=runtime.oms.orders()[0].order_id,
            client_request_id=runtime.oms.orders()[0].client_request_id,
            payload=event_pairs(
                concrete_contract_id="TEST.IF9999",
                direction="LONG",
                action="OPEN",
                price="4000",
                quantity="1",
            ),
        )
        # Sequence 999 is a gap, so it is rejected as a gap BEFORE content apply.
        result = runtime.state.apply_broker_event(fill_event)
        self.assertIn(result.outcome, (EventApplicationOutcome.REJECTED_SEQUENCE_GAP,))
        # The genuine idempotent duplicate path (same event_id, same content) is a no-op:
        original = runtime.state.applied_events()[1]
        replay = runtime.state.apply_broker_event(original)
        self.assertEqual(replay.outcome, EventApplicationOutcome.APPLIED_ALREADY_NOOP)
        self.assertEqual(runtime.state.position_for("TEST.IF9999", PositionDirection.LONG).quantity, Decimal("1"))

    def test_out_of_order_event_blocks(self):
        runtime = self._runtime(OpenThenCloseStrategy())
        runtime.on_completed_bar(make_bar(0, Decimal("4000")))
        # Inject an out-of-order event: a new event with an old sequence.
        out_of_order = BrokerEvent(
            event_id="ev-o3",
            event_type=BrokerEventType.ORDER_SUBMITTED,
            occurred_at=START_AT,
            stream_id="paper-broker",
            sequence=0,
            order_id="o-ooo",
            client_request_id="r-ooo",
            payload=event_pairs(
                concrete_contract_id="TEST.IF9999", direction="LONG", action="OPEN",
                quantity="1", order_type="MARKET",
            ),
        )
        runtime.broker.inject_events((out_of_order,))
        results = runtime.drain_and_apply_events(START_AT)
        self.assertEqual(results[0].outcome, EventApplicationOutcome.REJECTED_OUT_OF_ORDER)
        # Safety now flags the sequence violation and blocks further opens.
        safety = runtime.safety_gate.assess(
            state=runtime.state, clock_now=START_AT, context=None,
            connection_state=runtime.broker.connection_state, reconciliation=None,
        )
        self.assertTrue(safety.blocking)

    def test_disconnect_blocks_new_orders(self):
        runtime = self._runtime(OpenLongStrategy())
        runtime.on_completed_bar(make_bar(0, Decimal("4000")))
        runtime.broker.disconnect()
        result = runtime.on_completed_bar(make_bar(1, Decimal("4010")))
        # Safety flags BROKER_DISCONNECT; RiskGate blocks the new open.
        self.assertEqual(len(result.orders_created), 0)
        self.assertTrue(any(v.kind is SafetyViolationKind.BROKER_DISCONNECT for v in result.safety.violations))

    def test_kill_switch_halts_trading(self):
        runtime = self._runtime(OpenLongStrategy())
        runtime.on_completed_bar(make_bar(0, Decimal("4000")))
        runtime.trip_kill_switch("test scenario", START_AT)
        result = runtime.on_completed_bar(make_bar(1, Decimal("4010")))
        self.assertEqual(len(result.orders_created), 0)
        self.assertTrue(result.safety.blocking)
        self.assertTrue(any(v.kind is SafetyViolationKind.KILL_SWITCH_TRIPPED for v in result.safety.violations))
        # Even after disarm, normal operation can resume.
        runtime.disarm_kill_switch("recovered", START_AT + timedelta(minutes=1))
        result = runtime.on_completed_bar(make_bar(2, Decimal("4020")))
        self.assertEqual(len(result.orders_created), 1)
        self.assertFalse(result.safety.blocking)

    def test_restart_recovery(self):
        runtime = self._runtime(OpenThenCloseStrategy())
        runtime.on_completed_bar(make_bar(0, Decimal("4000")))
        persisted = runtime.capture_persisted_state(START_AT + timedelta(hours=1))
        broker_snapshot = runtime.broker.capture_snapshot(at=START_AT + timedelta(hours=1))
        rebuilt = ShadowRuntime.rebuild(
            persisted,
            make_config(),
            OpenThenCloseStrategy(start_index=1),
            runtime.ledger,
            broker_snapshot,
            START_AT + timedelta(hours=1, minutes=1),
        )
        report = rebuilt.reconcile(START_AT + timedelta(hours=1, minutes=1))
        self.assertTrue(report.ok)
        self.assertEqual(
            rebuilt.state.position_for("TEST.IF9999", PositionDirection.LONG).quantity,
            Decimal("1"),
        )
        self.assertTrue(rebuilt.ledger.verify_chain())
        # Continue after restart with a fresh bar.
        result = rebuilt.on_completed_bar(make_bar(1, Decimal("4010")))
        self.assertIsNone(rebuilt.state.position_for("TEST.IF9999", PositionDirection.LONG))
        self.assertTrue(result.reconciliation.ok)

    def test_rebuild_rejects_ledger_tail_mismatch(self):
        runtime = self._runtime(OpenLongStrategy())
        runtime.on_completed_bar(make_bar(0, Decimal("4000")))
        persisted = runtime.capture_persisted_state(START_AT + timedelta(hours=1))
        broker_snapshot = runtime.broker.capture_snapshot(at=START_AT + timedelta(hours=1))
        wrong_ledger = RuntimeLedger()  # a different, empty ledger -> tail mismatch
        with self.assertRaises(ValueError):
            rebuild_trading_state(
                persisted,
                contract_specs=make_config().contract_specs,
                accounting=make_accounting(),
                ledger=wrong_ledger,
                recovery_recorded_at=START_AT + timedelta(hours=1, minutes=1),
            )

    def test_conflict_strategy_produces_no_orders(self):
        runtime = self._runtime(ConflictStrategy())
        result = runtime.on_completed_bar(make_bar(0, Decimal("4000")))
        self.assertEqual(len(result.orders_created), 0)
        self.assertEqual(
            {item.decision for item in result.conflict_resolution.resolutions},
            {IntentDecision.REJECTED_CONFLICT},
        )

    def test_noop_strategy_no_state_change(self):
        runtime = self._runtime(NoopStrategy())
        result = runtime.on_completed_bar(make_bar(0, Decimal("4000")))
        self.assertEqual(len(result.orders_created), 0)
        self.assertEqual(runtime.state.positions, ())
        self.assertTrue(result.reconciliation.ok)


class PaperBrokerReconciliationIntegrationTests(unittest.TestCase):
    def test_local_and_broker_agree_after_fills(self):
        runtime = ShadowRuntime(make_config(), OpenLongStrategy(), created_at=START_AT)
        run_bars(runtime, 3, [Decimal("4000"), Decimal("4010"), Decimal("4020")])
        report = runtime.reconcile(START_AT + timedelta(hours=1))
        self.assertTrue(report.ok)
        self.assertEqual(runtime.state.account.cash_balance, runtime.broker.fetch_account_snapshot().cash_balance)


if __name__ == "__main__":
    unittest.main()

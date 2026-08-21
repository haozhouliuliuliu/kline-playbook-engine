"""Synthetic adversarial checks for V0.3 stop/OCO and authority machinery.

These fixtures exercise only project-owned deterministic paper semantics.  They
do not read candidate bars, connect a broker, or authorize Shadow.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
import unittest

from src.broker_adapter import BrokerOrderInstruction, OrderRole, OrderType
from src.contract_semantics import OrderAction, PositionDirection
from src.paper_broker import PaperBrokerAdapter, PaperFillPolicy
from src.pre_shadow_gate import PreShadowGateV02Inputs, PreShadowTechnicalGateV02
from src.prospective_execution_authority import (
    ProspectiveExecutionAuthorityError,
    ProspectiveExecutionAuthorityStore,
    ProspectiveFeeMarginFact,
    ProspectivePriceLimitFact,
    ProspectiveSlippagePolicy,
)
from src.runtime_events import BrokerEventType
from src.trading_state import OrderStatus
from tests.runtime_synthetic_fixture import TZ, make_accounting, make_bar, make_contract_spec


AT = datetime(2024, 6, 17, 9, 0, tzinfo=TZ)


def _broker() -> PaperBrokerAdapter:
    return PaperBrokerAdapter(
        broker_id="v03-paper", contract_specs=(make_contract_spec(),),
        accounting=make_accounting(), starting_capital=Decimal("1000000"),
        currency="CNY", fill_policy=PaperFillPolicy.RESTING_ON_COMPLETED_BAR,
    )


def _stop(request: str, trigger: str, *, role: OrderRole = OrderRole.ENTRY_STOP, oco: str | None = None) -> BrokerOrderInstruction:
    return BrokerOrderInstruction(
        client_request_id=request, client_order_id=f"client-{request}",
        concrete_contract_id="TEST.IF9999", direction=PositionDirection.LONG,
        action=OrderAction.OPEN, order_type=OrderType.STOP_MARKET,
        order_role=role, quantity=Decimal("1"), trigger_price=Decimal(trigger),
        strategy_identity_id="synthetic-strategy", available_at=AT,
        oco_group_id=oco, source_directive_identity=f"directive-{request}",
    )


class StopOcoPaperSemanticsTests(unittest.TestCase):
    def test_entry_resting_trigger_fill_and_duplicate_trigger_is_impossible(self):
        broker = _broker()
        order_id = broker.submit_order(_stop("entry", "102"), at=AT)
        self.assertEqual(broker.fetch_order_snapshot()[0].status, OrderStatus.RESTING.value)
        events = broker.ingest_completed_bar(make_bar(1, Decimal("101")), at=AT + timedelta(minutes=2))
        self.assertEqual([event.event_type for event in events], [BrokerEventType.ORDER_TRIGGERED, BrokerEventType.ORDER_FILLED])
        self.assertEqual(broker.fetch_order_snapshot()[0].status, OrderStatus.FILLED.value)
        self.assertEqual((), broker.ingest_completed_bar(make_bar(2, Decimal("105")), at=AT + timedelta(minutes=3)))
        self.assertEqual(order_id, broker.fetch_order_snapshot()[0].order_id)

    def test_cancel_before_trigger_and_restart_while_resting(self):
        broker = _broker()
        order_id = broker.submit_order(_stop("cancel", "110"), at=AT)
        snapshot = broker.capture_snapshot(at=AT)
        restored = _broker()
        restored.restore_snapshot(snapshot)
        restored.cancel_order(order_id, at=AT + timedelta(minutes=1))
        self.assertEqual(restored.fetch_order_snapshot()[0].status, OrderStatus.CANCELLED.value)
        self.assertEqual((), restored.ingest_completed_bar(make_bar(2, Decimal("120")), at=AT + timedelta(minutes=3)))

    def test_oco_full_fill_cancels_active_sibling_and_same_bar_race_is_ambiguous(self):
        broker = _broker()
        first = broker.submit_order(_stop("oco-first", "102", oco="group-1"), at=AT)
        second = broker.submit_order(_stop("oco-second", "104", oco="group-1"), at=AT)
        events = broker.ingest_completed_bar(make_bar(1, Decimal("101")), at=AT + timedelta(minutes=2))
        self.assertIn(BrokerEventType.ORDER_FILLED, [event.event_type for event in events])
        self.assertIn(BrokerEventType.ORDER_CANCELLED, [event.event_type for event in events])
        states = {item.order_id: item.status for item in broker.fetch_order_snapshot()}
        self.assertEqual(OrderStatus.FILLED.value, states[first])
        self.assertEqual(OrderStatus.CANCELLED.value, states[second])
        race = _broker()
        race.submit_order(_stop("race-a", "102", oco="group-race"), at=AT)
        race.submit_order(_stop("race-b", "101", oco="group-race"), at=AT)
        race_events = race.ingest_completed_bar(make_bar(1, Decimal("101")), at=AT + timedelta(minutes=2))
        self.assertTrue(all(event.event_type is BrokerEventType.ORDER_AMBIGUOUS for event in race_events))

    def test_same_bar_activation_is_ambiguous_not_filled(self):
        broker = _broker()
        available = AT + timedelta(seconds=30)
        instruction = _stop("same-bar", "102")
        instruction = BrokerOrderInstruction(**{**instruction.__dict__, "available_at": available})
        broker.submit_order(instruction, at=AT)
        events = broker.ingest_completed_bar(make_bar(0, Decimal("101")), at=AT + timedelta(minutes=1))
        self.assertEqual(BrokerEventType.ORDER_AMBIGUOUS, events[-1].event_type)


class ProspectiveAuthorityStoreTests(unittest.TestCase):
    def test_append_only_pit_and_conflict_fail_closed(self):
        store = ProspectiveExecutionAuthorityStore()
        fee = ProspectiveFeeMarginFact("TEST.IF9999", AT, AT, "fee-source", Decimal("1"), Decimal("0.1"), provenance="official", source_bytes_sha256="a" * 64)
        limit = ProspectivePriceLimitFact("TEST.IF9999", date(2024, 6, 17), AT, AT, "limit-source", Decimal("90"), Decimal("110"), provenance="official", source_bytes_sha256="b" * 64)
        policy = ProspectiveSlippagePolicy("policy", "TEST.IF9999", "v1", AT, AT, "policy-source", "pre-registered", "c" * 64, "CONFIGURED", "SYNTHETIC_ONLY_REFERENCE")
        for fact in (fee, limit, policy):
            store.append(fact, AT)
        authority = store.authority_at(AT, concrete_contract_id="TEST.IF9999")
        self.assertEqual("fee-source", authority.require_fee_margin("TEST.IF9999", AT).source_identity)
        self.assertTrue(authority.require_slippage().configured)
        with self.assertRaises(ProspectiveExecutionAuthorityError):
            store.append(ProspectiveFeeMarginFact("TEST.IF9999", AT, AT, "different", Decimal("2"), Decimal("0.1")), AT)

    def test_future_fact_and_unresolved_policy_deny(self):
        store = ProspectiveExecutionAuthorityStore()
        future = AT + timedelta(days=1)
        store.append(ProspectiveFeeMarginFact("TEST.IF9999", future, future, "fee", Decimal("1"), Decimal("0.1")), AT)
        authority = store.authority_at(AT, concrete_contract_id="TEST.IF9999")
        with self.assertRaises(ProspectiveExecutionAuthorityError):
            authority.require_fee_margin("TEST.IF9999", AT)
        with self.assertRaises(ProspectiveExecutionAuthorityError):
            authority.require_slippage()


class PreShadowGateV02Tests(unittest.TestCase):
    def test_engineering_ready_is_independent_from_research_and_authorization(self):
        inputs = PreShadowGateV02Inputs(*([True] * 9), False, False, False, False, False, False, True, True)
        decision = PreShadowTechnicalGateV02().evaluate(inputs)
        self.assertTrue(decision.engineering_ready)
        self.assertFalse(decision.research_method_ready)
        self.assertFalse(decision.authorized_to_start)


if __name__ == "__main__":
    unittest.main()

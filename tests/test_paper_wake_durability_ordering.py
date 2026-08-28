from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.jianghe_ai_trader import AttentionMode, DecisionAction, Direction, StrategyFamily
from src.jianghe_execution_bridge import JiangheExecutionBridge
from src.jianghe_response_normalizer import NormalizedJiangheDecision
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_execution_chain import PaperDeterministicExecutionChain
from src.paper_order_journal import CONDITIONAL_TRIGGERED, UNKNOWN_AFTER_SUBMIT, PaperOrderJournal
from src.paper_runtime import PaperRuntimeCoordinator, PaperTraderDecision
from src.paper_supervisor import PaperRuntimeSupervisor
from src.paper_wake_journal import DECISION_COMMITTED, OBSERVED, PaperWakeJournal
from src.risk_gate import RiskGate, RiskRuleSet
from tests.test_paper_final_closure import _protective_stop_instruction, _triggered_child_instruction
from tests.test_paper_live_causal_context import (
    CONTRACT,
    INSTRUMENT,
    TARGET_DAY,
    TZ,
    _CALENDAR,
    _live_minute,
    _minutes_for_days,
    _new_builder,
    _prior_days,
)
from tests.test_paper_offline_runtime_drill import FakeJournaledPaperBroker, _authority, _profile


class WakeDurabilityOrderingRegressionTests(unittest.TestCase):
    def test_stop_submit_unknown_cannot_eat_same_boundary_cognition_wake(self) -> None:
        bootstrap_at = datetime(
            TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 19, tzinfo=TZ
        )
        wake_at = bootstrap_at + timedelta(minutes=1)

        class Broker(FakeJournaledPaperBroker):
            @property
            def order_journal(self):
                return self.journal

        class WaitingTrader:
            def __init__(self) -> None:
                self.calls = 0

            def decide(self, *, wake, context, positions, account):
                self.calls += 1
                normalized = NormalizedJiangheDecision(
                    family=StrategyFamily.NONE,
                    action=DecisionAction.WAIT,
                    direction=Direction.NONE,
                    attention_mode=AttentionMode.WATCH,
                    decision_state="TEST_ONLY_WAIT",
                    rationale="TEST_ONLY",
                    raw_text="{}",
                    declared_unknown=(),
                    principle_references=(),
                    source_references=(),
                    numeric_claims=(),
                )
                return PaperTraderDecision(
                    decision_identity=normalized.identity,
                    normalized_decision=normalized,
                )

        with TemporaryDirectory() as tmp:
            order_journal = PaperOrderJournal(Path(tmp) / "orders.sqlite3")
            wake_journal = PaperWakeJournal(Path(tmp) / "wakes.sqlite3")
            try:
                builder = _new_builder()
                mirror = PaperBrokerTruthMirror(broker_id="OFFLINE_FAKE_BROKER")
                broker = Broker(order_journal)
                broker.set_observed_at(bootstrap_at)
                trader = WaitingTrader()
                supervisor = PaperRuntimeSupervisor(
                    actual_tqsdk_runtime_version="3.10.1",
                    authority=_authority(),
                    activation_profile=_profile(),
                    broker_mirror=mirror,
                    order_journal=order_journal,
                    wake_journal=wake_journal,
                )
                chain = PaperDeterministicExecutionChain(
                    strategy_identity="strategy",
                    instrument=INSTRUMENT,
                    concrete_contract_id=CONTRACT,
                    bridge=JiangheExecutionBridge(),
                    risk_gate=RiskGate(
                        RiskRuleSet(
                            ruleset_id="risk",
                            version="test-only",
                            max_order_quantity=Decimal("1"),
                        )
                    ),
                    max_market_age_seconds=60,
                )
                runtime = PaperRuntimeCoordinator(
                    trader_identity="trader",
                    concrete_contract_id=CONTRACT,
                    context_builder=builder,
                    wake_journal=wake_journal,
                    order_journal=order_journal,
                    broker_mirror=mirror,
                    supervisor=supervisor,
                    broker=broker,
                    trader=trader,
                    execution_chain=chain,
                )
                runtime.connect(at=bootstrap_at)
                runtime.bootstrap_market(
                    _minutes_for_days(
                        _prior_days(_CALENDAR.trading_days, 3) + (TARGET_DAY,),
                        until=bootstrap_at,
                    ),
                    observed_at=bootstrap_at,
                )
                runtime.mark_trader_runtime_ready()

                directive = replace(
                    _protective_stop_instruction(), concrete_contract_id=CONTRACT
                )
                child = _triggered_child_instruction(directive)
                order_journal.prepare(
                    client_request_id=directive.client_request_id,
                    trader_identity="trader",
                    wake_identity="prior-wake",
                    decision_identity="prior-decision",
                    intent_identity="prior-intent",
                    risk_identity="prior-risk",
                    concrete_contract_id=CONTRACT,
                    instruction=directive,
                    prepared_at=bootstrap_at,
                )
                order_journal.arm_conditional(
                    directive_client_request_id=directive.client_request_id,
                    child_instruction=child,
                    at=bootstrap_at,
                )

                bars = (_live_minute(bootstrap_at, price="3489"),)
                broker.set_observed_at(wake_at)
                broker.fail_after_submit = True
                with self.assertRaisesRegex(
                    TimeoutError, "OFFLINE_FAULT_AFTER_SUBMIT_BOUNDARY"
                ):
                    runtime.process_closed_minutes(bars, observed_at=wake_at)

                self.assertEqual(1, broker.submit_calls)
                self.assertEqual(0, trader.calls)
                pending = wake_journal.pending_observations()
                self.assertEqual(1, len(pending))
                self.assertEqual(OBSERVED, pending[0].status)
                self.assertEqual((), wake_journal.unresolved_dispatches())
                self.assertEqual(
                    UNKNOWN_AFTER_SUBMIT,
                    order_journal.get(child.client_request_id).status,
                )
                self.assertEqual(
                    CONDITIONAL_TRIGGERED,
                    order_journal.get_conditional(directive.client_request_id).status,
                )

                broker.fail_after_submit = False
                recovered = runtime.process_closed_minutes(bars, observed_at=wake_at)
                self.assertEqual(1, len(recovered))
                self.assertEqual(1, trader.calls)
                self.assertEqual(1, broker.submit_calls)
                self.assertEqual((), wake_journal.pending_observations())
                self.assertEqual(
                    DECISION_COMMITTED,
                    wake_journal.get(recovered[0].wake_identity).status,
                )

                self.assertEqual(
                    (), runtime.process_closed_minutes(bars, observed_at=wake_at)
                )
                self.assertEqual(1, trader.calls)
                self.assertEqual(1, broker.submit_calls)
            finally:
                order_journal.close()
                wake_journal.close()


if __name__ == "__main__":
    unittest.main()

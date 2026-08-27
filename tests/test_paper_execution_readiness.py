from __future__ import annotations

from datetime import datetime
from decimal import Decimal
import unittest

from src.broker_adapter import BrokerOrderInstruction, OrderType
from src.contract_semantics import OrderAction, PositionDirection
from src.jianghe_ai_trader import AttentionMode, DecisionAction, Direction, StrategyFamily
from src.jianghe_execution_bridge import ExecutionSemanticsRequired, JiangheExecutionBridge
from src.jianghe_response_normalizer import NormalizedJiangheDecision
from src.paper_broker import PaperBrokerAdapter, PaperFillPolicy
from src.paper_execution_authority import PaperAuthorityStatus, PaperExecutionAuthority
from src.shadow_runtime import ShadowRuntime
from src.tqsdk_paper_candidate import TqSdkPaperBrokerAdapter
from tests.runtime_synthetic_fixture import (
    OpenLongStrategy,
    TZ,
    make_accounting,
    make_bar,
    make_config,
    make_contract_spec,
)


class PaperExecutionReadinessTests(unittest.TestCase):
    def test_restored_runtime_executes_local_paper_chain(self) -> None:
        runtime = ShadowRuntime(make_config(), OpenLongStrategy())
        result = runtime.on_completed_bar(make_bar(0, Decimal("100")))
        self.assertEqual(1, len(result.orders_created))
        self.assertTrue(result.reconciliation.ok)
        positions = runtime.broker.fetch_position_snapshot()
        self.assertEqual(1, len(positions))
        self.assertEqual(Decimal("1"), positions[0].quantity)

    def _authority(
        self,
        *,
        status: PaperAuthorityStatus,
        allow_connect: bool,
        allow_order_submit: bool,
        allow_order_cancel: bool = False,
    ) -> PaperExecutionAuthority:
        return PaperExecutionAuthority(
            authority_id="test-paper-authority",
            broker_kind="TQSDK_CANDIDATE",
            account_kind="TEST_ONLY_FAKE",
            status=status,
            allow_connect=allow_connect,
            allow_order_submit=allow_order_submit,
            allow_order_cancel=allow_order_cancel,
            credential_env_names=("TEST_ONLY_AUTH_USER_ENV", "TEST_ONLY_AUTH_PASSWORD_ENV"),
            allowed_contracts=("TEST.IF9999",),
        )

    def _driver(self) -> PaperBrokerAdapter:
        return PaperBrokerAdapter(
            broker_id="fake-tqsdk-driver",
            contract_specs=(make_contract_spec(),),
            accounting=make_accounting(),
            starting_capital=Decimal("1000000"),
            currency="CNY",
            fill_policy=PaperFillPolicy.RESTING_ON_COMPLETED_BAR,
            timezone="Asia/Shanghai",
        )

    def _instruction(self) -> BrokerOrderInstruction:
        return BrokerOrderInstruction(
            client_request_id="request-1",
            concrete_contract_id="TEST.IF9999",
            direction=PositionDirection.LONG,
            action=OrderAction.OPEN,
            order_type=OrderType.MARKET,
            quantity=Decimal("1"),
        )

    def test_external_candidate_connect_and_order_are_separately_gated(self) -> None:
        blocked = TqSdkPaperBrokerAdapter(
            self._driver(),
            self._authority(
                status=PaperAuthorityStatus.PENDING,
                allow_connect=False,
                allow_order_submit=False,
            ),
        )
        with self.assertRaisesRegex(PermissionError, "PAPER_CONNECT_NOT_AUTHORIZED"):
            blocked.connect()
        with self.assertRaisesRegex(PermissionError, "PAPER_ORDER_SUBMIT_NOT_AUTHORIZED"):
            blocked.submit_order(self._instruction())

        connect_only = TqSdkPaperBrokerAdapter(
            self._driver(),
            self._authority(
                status=PaperAuthorityStatus.ACTIVE,
                allow_connect=True,
                allow_order_submit=False,
            ),
        )
        connect_only.connect()
        with self.assertRaisesRegex(PermissionError, "PAPER_ORDER_SUBMIT_NOT_AUTHORIZED"):
            connect_only.submit_order(self._instruction())
        with self.assertRaisesRegex(PermissionError, "PAPER_ORDER_CANCEL_NOT_AUTHORIZED"):
            connect_only.cancel_order("known-order")

        order_enabled = TqSdkPaperBrokerAdapter(
            self._driver(),
            self._authority(
                status=PaperAuthorityStatus.ACTIVE,
                allow_connect=True,
                allow_order_submit=True,
                allow_order_cancel=True,
            ),
        )
        order_enabled.connect()
        order_id = order_enabled.submit_order(self._instruction())
        self.assertTrue(order_id)
        self.assertEqual(1, len(order_enabled.fetch_order_snapshot()))
        order_enabled.cancel_order(order_id)

    def _decision(self, action: DecisionAction, direction: Direction = Direction.NONE) -> NormalizedJiangheDecision:
        return NormalizedJiangheDecision(
            family=StrategyFamily.NONE,
            action=action,
            direction=direction,
            attention_mode=AttentionMode.WATCH,
            decision_state="TEST_ONLY",
            rationale="TEST_ONLY",
            raw_text='{"test":"raw"}',
            declared_unknown=(),
            principle_references=(),
            source_references=(),
            numeric_claims=(),
        )

    def test_jianghe_non_execution_actions_never_create_orders(self) -> None:
        bridge = JiangheExecutionBridge()
        for action in (
            DecisionAction.WAIT,
            DecisionAction.NO_TRADE,
            DecisionAction.WATCH,
            DecisionAction.CANDIDATE,
        ):
            resolution = bridge.resolve(
                self._decision(action),
                strategy_identity_id="jianghe-test",
                instrument="cu",
                concrete_contract_id="SHFE.cu2406",
                decision_at=datetime(2024, 1, 1, 9, 0, tzinfo=TZ),
                context_identity="context-test",
            )
            self.assertFalse(resolution.executable)
            self.assertEqual(1, len(resolution.intents))
            self.assertEqual("HOLD", resolution.intents[0].action.value)

    def test_jianghe_enter_fails_closed_without_execution_semantics(self) -> None:
        bridge = JiangheExecutionBridge()
        with self.assertRaisesRegex(ExecutionSemanticsRequired, "REQUIRES_EXPLICIT_EXECUTION_POLICY"):
            bridge.resolve(
                self._decision(DecisionAction.ENTER, Direction.LONG),
                strategy_identity_id="jianghe-test",
                instrument="cu",
                concrete_contract_id="SHFE.cu2406",
                decision_at=datetime(2024, 1, 1, 9, 0, tzinfo=TZ),
                context_identity="context-test",
            )

    def test_authority_rejects_secret_values_and_order_without_connect(self) -> None:
        with self.assertRaises(ValueError):
            PaperExecutionAuthority(
                authority_id="bad",
                broker_kind="TQSDK",
                account_kind="TQKQ",
                status=PaperAuthorityStatus.ACTIVE,
                allow_connect=False,
                allow_order_submit=True,
            )
        with self.assertRaisesRegex(ValueError, "never values"):
            PaperExecutionAuthority(
                authority_id="bad-secret",
                broker_kind="TQSDK",
                account_kind="TQKQ",
                status=PaperAuthorityStatus.PENDING,
                allow_connect=False,
                allow_order_submit=False,
                credential_env_names=("PASSWORD=secret",),
            )


if __name__ == "__main__":
    unittest.main()

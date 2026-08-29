"""Project-brain reproduction for carried-position restart semantics in PR #78."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.broker_adapter import BrokerOrderInstruction, OrderType
from src.contract_semantics import CloseOffset, OrderAction, PositionDirection
from src.fangzheng_ctp_candidate import (
    CtpCallbackType,
    CtpTradeFill,
    CtpTranslationProfile,
    FangzhengCtpBrokerAdapter,
)
from src.fangzheng_ctp_fake import FakeCtpOperation, FakeCtpStep, ScriptedCtpTransport
from src.real_execution_composition import RealExecutionComposition
from tests.test_fangzheng_ctp_candidate import CONTRACT
from tests.test_fangzheng_ctp_fake import callback, establish_ready
from tests.test_real_execution_composition import NOW, TRADING_DAY, _ready_query_steps
from tests.test_real_execution_composition_orp004_closure import _runtime_state_with_order


def _close_profile() -> CtpTranslationProfile:
    return CtpTranslationProfile(
        instruments=((CONTRACT, "opaque-instrument"),),
        sides=((PositionDirection.LONG, OrderAction.CLOSE, "opaque-sell"),),
        offsets=((OrderAction.CLOSE, CloseOffset.CLOSE, "opaque-close"),),
        order_types=((OrderType.LIMIT, "opaque-limit"),),
    )


def _close_instruction() -> BrokerOrderInstruction:
    return BrokerOrderInstruction(
        client_request_id="close-request-1",
        client_order_id="close-order-1",
        strategy_identity_id="carried-position-close",
        concrete_contract_id=CONTRACT,
        direction=PositionDirection.LONG,
        action=OrderAction.CLOSE,
        close_offset=CloseOffset.CLOSE,
        order_type=OrderType.LIMIT,
        quantity=Decimal("1"),
        limit_price=Decimal("3600"),
    )


class ProjectBrainCarriedPositionRevalidationTests(unittest.TestCase):
    def test_exact_restart_after_closing_carried_position_must_not_self_invalidate(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "carried-close.sqlite3"

            # This pre-existing position is legitimate project state from before
            # the current REAL-composition journal/trading-day scope.
            state = _runtime_state_with_order(
                fills=((Decimal("2"), Decimal("3500")),)
            )
            self.assertEqual(
                state.position_for(CONTRACT, PositionDirection.LONG).quantity,
                Decimal("2"),
            )

            transport = ScriptedCtpTransport(
                _ready_query_steps()
                + (
                    FakeCtpStep(
                        FakeCtpOperation.SUBMIT,
                        expected_project_order_id="close-order-1",
                    ),
                )
            )
            adapter = FangzhengCtpBrokerAdapter(transport, _close_profile())
            establish_ready(adapter)
            first = RealExecutionComposition(
                path=path,
                adapter=adapter,
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-carried-close",
            )
            first.submit_order(_close_instruction(), submitted_at=NOW)
            transport.inject_callbacks((callback(
                "close-fill",
                CtpCallbackType.TRADE_FILLED,
                CtpTradeFill(
                    "close-order-1",
                    "close-request-1",
                    "broker-close-1",
                    "trade-close-1",
                    Decimal("1"),
                    Decimal("3600"),
                ),
                trading_day=TRADING_DAY,
            ),))
            first.consume_adapter_events()
            self.assertEqual(
                state.position_for(CONTRACT, PositionDirection.LONG).quantity,
                Decimal("1"),
            )

            # Reopening with the exact state produced by the first composition
            # should not become a hard inconsistency merely because the opening
            # position predated this trading-day/session journal.
            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(ScriptedCtpTransport(()), _close_profile()),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-carried-close",
            )

            self.assertNotIn(
                "HARD_EXECUTION_INCONSISTENCY",
                reopened.active_blockers(),
                "restart treated a legitimate carried-position baseline as zero and rejected the exact state it had produced",
            )
            self.assertFalse(reopened.new_risk_allowed)


if __name__ == "__main__":
    unittest.main()

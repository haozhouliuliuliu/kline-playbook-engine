"""Independent project-brain probe for REAL restart account economics in PR #80."""

from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.fangzheng_ctp_candidate import FangzhengCtpBrokerAdapter
from src.fangzheng_ctp_fake import ScriptedCtpTransport
from src.real_execution_composition import RealExecutionComposition
from tests.test_real_execution_composition import TRADING_DAY
from tests.test_real_execution_composition_restart_state import (
    _close_profile,
    _create_carried_partial_close,
)


class ProjectBrainAccountEconomicContinuityTests(unittest.TestCase):
    def test_exact_fill_and_position_projection_with_tampered_account_economics_must_fail_closed(self) -> None:
        """Account economics are part of exact mutable TradingState continuity."""
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "account-economics.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-account-economics"
            )
            exact = state.account
            state._account = replace(
                exact,
                charged_costs=exact.charged_costs + Decimal("1"),
            )
            self.assertEqual(state.account.realized_pnl, exact.realized_pnl)
            self.assertNotEqual(state.account.charged_costs, exact.charged_costs)

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-account-economics",
            )

            self.assertIn(
                "HARD_EXECUTION_INCONSISTENCY",
                reopened.active_blockers(),
                "restart accepted exact execution lineage/position aggregates despite divergent account economics",
            )
            self.assertFalse(reopened.new_risk_allowed)


if __name__ == "__main__":
    unittest.main()

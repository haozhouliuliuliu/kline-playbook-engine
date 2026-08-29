"""Independent project-brain probe for REAL restart RuntimeLedger coherence in PR #80."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.fangzheng_ctp_candidate import FangzhengCtpBrokerAdapter
from src.fangzheng_ctp_fake import ScriptedCtpTransport
from src.real_execution_composition import RealExecutionComposition
from src.runtime_ledger import RuntimeLedger
from tests.test_real_execution_composition import TRADING_DAY
from tests.test_real_execution_composition_restart_state import (
    _close_profile,
    _create_carried_partial_close,
)


class ProjectBrainRuntimeLedgerCoherenceTests(unittest.TestCase):
    def test_exact_applied_events_with_replaced_empty_runtime_ledger_must_fail_closed(self) -> None:
        """Applied-event lineage cannot stand in for the immutable audit ledger.

        Preserve the exact order, position, account and applied BrokerEvent history
        produced by the composition, but replace its RuntimeLedger with a fresh
        empty ledger.  Restart exactness must reject this split-brain state rather
        than treating the applied-event list alone as sufficient evidence.
        """
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "ledger-coherence.sqlite3"
            state = _create_carried_partial_close(
                path, session_identity="session-ledger-coherence"
            )
            self.assertGreater(len(state.applied_events()), 0)
            original_tail = state.ledger_tail_identity

            state._ledger = RuntimeLedger()
            self.assertNotEqual(state.ledger_tail_identity, original_tail)
            self.assertEqual(state._ledger.count(), 0)

            reopened = RealExecutionComposition(
                path=path,
                adapter=FangzhengCtpBrokerAdapter(
                    ScriptedCtpTransport(()), _close_profile()
                ),
                trading_state=state,
                expected_trading_day=TRADING_DAY,
                session_identity="session-ledger-coherence",
            )

            self.assertIn(
                "HARD_EXECUTION_INCONSISTENCY",
                reopened.active_blockers(),
                "restart accepted exact applied events with a replaced empty immutable RuntimeLedger",
            )
            self.assertFalse(reopened.new_risk_allowed)


if __name__ == "__main__":
    unittest.main()

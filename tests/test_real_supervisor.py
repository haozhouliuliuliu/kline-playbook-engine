"""Deterministic offline tests for the REAL health/readiness supervisor.

Proves UNKNOWN/UNHEALTHY inputs fail closed to no-new-risk, kill/restart flags
stop new risk, reconciliation/persistence UNKNOWN force restart, DEGRADED is
recorded but non-blocking, revoked/expired authority stops new risk, and the
supervisor never computes risk.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import unittest

from src.real_execution_authority import MutableRealAuthoritySource
from src.real_supervisor import RealHealthInput, RealRuntimeSupervisor, RealSupervisorAssessment
from tests.real_synthetic_fixture import ASSESSED_AT, synthetic_authority

REPO_ROOT = Path(__file__).resolve().parents[1]

TZ = ASSESSED_AT.tzinfo


class RealSupervisorTests(unittest.TestCase):
    def _supervisor(self, authority=None) -> RealRuntimeSupervisor:
        if authority is None:
            authority = synthetic_authority()
        return RealRuntimeSupervisor(
            authority_source=MutableRealAuthoritySource(authority, source_identity="SUPERVISOR_TEST")
        )

    def test_all_healthy_no_new_risk(self) -> None:
        assessment = self._supervisor().assess(assessed_at=ASSESSED_AT)
        self.assertFalse(assessment.no_new_risk)
        self.assertTrue(assessment.can_observe)
        self.assertFalse(assessment.restart_required)
        self.assertEqual(assessment.no_new_risk_blockers, ())

    def test_unknown_fails_closed_to_no_new_risk(self) -> None:
        for name in (
            "market_data_health",
            "provider_health",
            "broker_session_health",
            "reconciliation_health",
            "persistence_health",
            "heartbeat",
        ):
            assessment = self._supervisor().assess(
                assessed_at=ASSESSED_AT, **{name: RealHealthInput.UNKNOWN}
            )
            self.assertTrue(assessment.no_new_risk, name)
            self.assertIn(name.upper() + "_UNKNOWN", assessment.no_new_risk_blockers)

    def test_unhealthy_fails_closed_to_no_new_risk(self) -> None:
        assessment = self._supervisor().assess(
            assessed_at=ASSESSED_AT, provider_health=RealHealthInput.UNHEALTHY
        )
        self.assertTrue(assessment.no_new_risk)
        self.assertIn("PROVIDER_HEALTH_UNHEALTHY", assessment.no_new_risk_blockers)

    def test_degraded_is_recorded_but_not_a_hard_blocker(self) -> None:
        assessment = self._supervisor().assess(
            assessed_at=ASSESSED_AT, market_data_health=RealHealthInput.DEGRADED
        )
        self.assertFalse(assessment.no_new_risk)
        self.assertTrue(assessment.can_observe)

    def test_kill_no_new_risk_blocks(self) -> None:
        assessment = self._supervisor().assess(assessed_at=ASSESSED_AT, kill_no_new_risk=True)
        self.assertTrue(assessment.no_new_risk)
        self.assertIn("KILL_NO_NEW_RISK", assessment.no_new_risk_blockers)

    def test_restart_requested_stops_new_risk(self) -> None:
        assessment = self._supervisor().assess(assessed_at=ASSESSED_AT, restart_requested=True)
        self.assertTrue(assessment.no_new_risk)
        self.assertTrue(assessment.restart_required)
        self.assertIn("RESTART_REQUESTED", assessment.restart_blockers)

    def test_unknown_reconciliation_forces_restart(self) -> None:
        assessment = self._supervisor().assess(
            assessed_at=ASSESSED_AT, reconciliation_health=RealHealthInput.UNKNOWN
        )
        self.assertTrue(assessment.no_new_risk)
        self.assertTrue(assessment.restart_required)
        self.assertIn("RECONCILIATION_REQUIRES_RESTART", assessment.restart_blockers)

    def test_unhealthy_persistence_forces_restart(self) -> None:
        assessment = self._supervisor().assess(
            assessed_at=ASSESSED_AT, persistence_health=RealHealthInput.UNHEALTHY
        )
        self.assertTrue(assessment.no_new_risk)
        self.assertTrue(assessment.restart_required)
        self.assertIn("PERSISTENCE_REQUIRES_RESTART", assessment.restart_blockers)

    def test_revoked_authority_stops_new_risk(self) -> None:
        revoked = synthetic_authority().revoked()
        assessment = self._supervisor(authority=revoked).assess(assessed_at=ASSESSED_AT)
        self.assertTrue(assessment.no_new_risk)
        self.assertFalse(assessment.authority_current)
        self.assertIn("REAL_AUTHORITY_NOT_CURRENT", assessment.no_new_risk_blockers)

    def test_mismatched_authority_identity_stops_new_risk(self) -> None:
        authority = synthetic_authority()
        supervisor = RealRuntimeSupervisor(
            authority_source=MutableRealAuthoritySource(
                authority, source_identity="SUPERVISOR_TEST"
            ),
            expected_authority_identity="SOME_OTHER_EXPECTED_IDENTITY",
        )
        assessment = supervisor.assess(assessed_at=ASSESSED_AT)
        self.assertTrue(assessment.no_new_risk)
        self.assertIn("REAL_AUTHORITY_IDENTITY_MISMATCH", assessment.no_new_risk_blockers)

    def test_expired_authority_stops_new_risk(self) -> None:
        authority = synthetic_authority()
        assessment = self._supervisor().assess(assessed_at=datetime(2027, 1, 1, tzinfo=TZ))
        self.assertTrue(assessment.no_new_risk)
        self.assertIn("REAL_AUTHORITY_NOT_CURRENT", assessment.no_new_risk_blockers)

    def test_input_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, "RealHealthInput"):
            self._supervisor().assess(assessed_at=ASSESSED_AT, heartbeat="HEALTHY")
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            self._supervisor().assess(assessed_at=datetime(2026, 6, 1, 9, 0))
        with self.assertRaisesRegex(ValueError, "booleans"):
            self._supervisor().assess(assessed_at=ASSESSED_AT, kill_no_new_risk="yes")

    def test_identity_deterministic_and_public_lines(self) -> None:
        one = self._supervisor().assess(assessed_at=ASSESSED_AT)
        two = self._supervisor().assess(assessed_at=ASSESSED_AT)
        self.assertEqual(one.identity_id, two.identity_id)
        lines = one.public_lines()
        self.assertIn("REAL_SUPERVISOR_NO_NEW_RISK=False", lines)
        text = "\n".join(lines)
        self.assertNotIn("password", text.lower())
        self.assertNotIn("DEEPSEEK_API_KEY", text)

    def test_supervisor_never_computes_risk(self) -> None:
        source = (REPO_ROOT / "src" / "real_supervisor.py").read_text(encoding="utf-8")
        for forbidden in (
            "risk_percent",
            "stop_loss",
            "max_drawdown",
            "margin_rate",
            "position_size",
            "0.01",
            "0.02",
        ):
            self.assertNotIn(forbidden, source)


if __name__ == "__main__":
    unittest.main()

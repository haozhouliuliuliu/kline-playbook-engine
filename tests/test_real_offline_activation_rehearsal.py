"""Deterministic offline tests for the REAL offline activation rehearsal.

Proves every rehearsal scenario passes, the report is deterministic and
machine-readable, and report type validation fails closed.
"""

from __future__ import annotations

import unittest

from src.real_offline_activation_rehearsal import (
    REAL_OFFLINE_ACTIVATION_REHEARSAL_VERSION,
    RealRehearsalReport,
    RealRehearsalScenario,
    run_real_offline_rehearsal,
)

REQUIRED_SCENARIOS = (
    "MISSING_GATES_LOCK",
    "STRUCTURAL_FIXTURE_REACHES_TEST_READY_ONLY",
    "AUTHORITY_EXPIRY_MID_SESSION_STOPS_NEW_RISK",
    "UNKNOWN_RECONCILIATION_BLOCKS",
    "RESTART_REQUIRES_FRESH_PREFLIGHT",
)


class RealOfflineActivationRehearsalTests(unittest.TestCase):
    def test_rehearsal_overall_passes(self) -> None:
        report = run_real_offline_rehearsal()
        self.assertEqual(report.overall, "PASS")
        self.assertTrue(report.passed)

    def test_rehearsal_covers_all_required_scenarios(self) -> None:
        report = run_real_offline_rehearsal()
        names = {scenario.name for scenario in report.scenarios}
        self.assertEqual(names, set(REQUIRED_SCENARIOS))
        for scenario in report.scenarios:
            self.assertEqual(scenario.status, "PASS", scenario.name + ": " + scenario.detail)

    def test_rehearsal_report_is_deterministic(self) -> None:
        one = run_real_offline_rehearsal()
        two = run_real_offline_rehearsal()
        self.assertEqual(one.public_lines(), two.public_lines())
        self.assertEqual(len(one.scenarios), len(REQUIRED_SCENARIOS))

    def test_rehearsal_public_lines_leak_no_secret(self) -> None:
        report = run_real_offline_rehearsal()
        text = "\n".join(report.public_lines())
        self.assertIn("REAL_REHEARSAL_OVERALL=PASS", text)
        self.assertNotIn("DEEPSEEK_API_KEY", text)
        self.assertNotIn("password", text.lower())

    def test_report_type_validation(self) -> None:
        with self.assertRaises(ValueError):
            RealRehearsalScenario(name="X", status="BAD", detail="d")
        with self.assertRaises(ValueError):
            RealRehearsalReport(
                version=REAL_OFFLINE_ACTIVATION_REHEARSAL_VERSION,
                overall="PASS",
                scenarios=(
                    RealRehearsalScenario(name="X", status="FAIL", detail="d"),
                ),
            )
        with self.assertRaises(ValueError):
            RealRehearsalReport(
                version=REAL_OFFLINE_ACTIVATION_REHEARSAL_VERSION,
                overall="FAIL",
                scenarios=(),
            )


if __name__ == "__main__":
    unittest.main()

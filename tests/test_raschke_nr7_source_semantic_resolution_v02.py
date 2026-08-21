"""Regression protection for the NR7 V0.2 bounded negative source resolution.

This test deliberately validates evidence and fail-closed boundaries only.  NR7
has no machine module because the source still leaves substantive strategy
semantics unpinned.
"""

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RESOLUTION_PATH = (
    REPO_ROOT
    / "docs"
    / "reviews"
    / "RASCHKE_NR7_SOURCE_SEMANTIC_RESOLUTION_V0_2.json"
)


class RaschkeNr7SourceResolutionV02Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(RESOLUTION_PATH.read_text(encoding="utf-8"))
        self.by_field = {
            entry["field"]: entry for entry in self.payload["field_audit"]
        }

    def test_audit_is_complete_and_uses_only_the_declared_classes(self) -> None:
        self.assertEqual(23, len(self.by_field))
        allowed = {
            "PINNED_SOURCE_EXPLICIT",
            "PINNED_SOURCE_INFERRED",
            "PROJECT_INFERRED_VERSIONED_NON_OUTCOME",
            "UNKNOWN_SOURCE_SEMANTIC",
            "MACHINE_DETAIL_OPEN",
            "UNOBSERVABLE_WITH_CURRENT_DATA",
        }
        self.assertTrue(
            {entry["classification"] for entry in self.by_field.values()} <= allowed
        )

    def test_substantive_unpinned_fields_remain_fail_closed(self) -> None:
        self.assertEqual("UNKNOWN_SOURCE_SEMANTIC", self.by_field["INITIAL_STOP"]["classification"])
        self.assertEqual(
            "UNKNOWN_SOURCE_SEMANTIC",
            self.by_field["POST_ENTRY_INVALIDATION"]["classification"],
        )
        self.assertEqual("NO", self.payload["machine_ready"])
        self.assertEqual("NO", self.payload["primary_freeze_ready"])
        self.assertEqual("NO", self.payload["strategy_identity_created"])

    def test_minimal_blockers_and_no_outcome_access_are_recorded(self) -> None:
        self.assertEqual(
            [
                "NR7_LOOKBACK_ALIGNMENT",
                "EARLY_MORNING_RANGE_PRIMARY",
                "INITIAL_STOP",
                "POST_ENTRY_INVALIDATION",
                "DETERMINISTIC_EXIT_AND_TIME_EXIT",
            ],
            self.payload["blocking_fields"],
        )
        self.assertEqual("YES", self.payload["no_candidate_outcome_used"])
        self.assertEqual("NOT_USED", self.payload["bounded_search"]["paid_or_authenticated_access"])
        self.assertEqual("YES", self.payload["bounded_search"]["stopping_condition_met"])

    def test_general_stop_material_is_not_mislabeled_as_nr7_source_semantics(self) -> None:
        conclusion = self.payload["bounded_search"]["conclusion"]
        self.assertIn("NR7_SPECIFIC_INITIAL_STOP", conclusion)
        self.assertIn("POST_ENTRY_INVALIDATION", conclusion)
        self.assertNotEqual(
            "PINNED_SOURCE_EXPLICIT", self.by_field["INITIAL_STOP"]["classification"]
        )


if __name__ == "__main__":
    unittest.main()

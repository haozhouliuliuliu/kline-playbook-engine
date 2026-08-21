"""Regression checks for the bounded Grimes pre-outcome negative resolution."""

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEW = ROOT / "docs/reviews/GRIMES_FREE_PUBLIC_PLAYBOOK_PROMOTION_V0_1.json"
SESSION = ROOT / "docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_GRIMES_FAILURE_TEST_SEMANTIC_V0_1.json"


class GrimesFreePublicPlaybookPromotionV01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.review = json.loads(REVIEW.read_text(encoding="utf-8"))
        self.session = json.loads(SESSION.read_text(encoding="utf-8"))

    def test_selected_family_is_fail_closed_without_machine_artifacts(self) -> None:
        self.assertEqual("GRIMES_FAILURE_TEST_FAILED_BREAKOUT_REVERSAL", self.review["selected_family"])
        self.assertEqual("ONE_FAMILY_SOURCE_SEMANTIC_INSUFFICIENT", self.review["final_result"])
        self.assertEqual("NO", self.review["machine_ready"])
        self.assertEqual("NO", self.review["primary_freeze_ready"])
        self.assertEqual("NO", self.review["strategy_identity_created"])

    def test_minimal_source_semantic_blockers_remain_closed(self) -> None:
        self.assertEqual(
            [
                "REFERENCE_LEVEL_SEMANTICS",
                "REVERSAL_TIMING_WINDOW",
                "POST_ENTRY_INVALIDATION",
                "REMAINDER_EXIT_AND_TIME_EXIT",
            ],
            self.review["blocking_fields"],
        )
        fields = {claim["semantic_field"]: claim for claim in self.session["claims"]}
        for field in ("REFERENCE_LEVEL_SEMANTICS", "REVERSAL_TIMING_WINDOW", "POST_ENTRY_INVALIDATION", "REMAINDER_EXIT", "TIME_EXIT"):
            self.assertEqual("UNKNOWN_SOURCE_SEMANTIC", fields[field]["semantic_classification"])

    def test_source_only_and_access_boundaries_are_recorded(self) -> None:
        self.assertTrue(self.session["is_verified"])
        self.assertEqual("DENIED", self.session["technical_denial"]["outcome"])
        self.assertEqual("SOURCE_ONLY_TECHNICAL_DENIAL", self.session["technical_denial"]["reason"])
        self.assertEqual("YES", self.review["no_candidate_outcome_used"])
        self.assertEqual("NOT_USED", self.review["access"]["paid_or_authenticated_access"])
        self.assertEqual(0, self.review["future_multiplicity"]["outcome_tested_claim_count_added"])


if __name__ == "__main__":
    unittest.main()

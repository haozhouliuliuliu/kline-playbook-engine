"""Regression tests for the Owner-ratified statistical acceptance route policy.

Covers `COMMON_STATISTICAL_PROFILE_ROUTE_A_D_OWNER_RATIFICATION_V0_1`:

- historical-v1 path cannot fabricate a general-domain positive PASS;
- `INSUFFICIENT_EVIDENCE` and `FAIL` remain legal historical dispositions;
- strong-FWER remains binding (not weakened);
- the future-positive path (Route D) does NOT auto-authorize Shadow/Forward;
- VALIDATION / historical-final locks are not released;
- outcome-calibrated thresholds remain forbidden;
- a corrupted/weakened policy record fails the fail-closed `validate()` check;
- the firewall profile registry still refuses to lock a real (non-TEST_ONLY)
  profile, so no fabricated PASS can flow through the existing firewall gate.
"""

import unittest

from src.research_firewall import CommonStatisticalProfile, StatisticalProfileRegistry
from src.statistical_acceptance_policy import (
    ADOPTED_STATISTICAL_ACCEPTANCE_ROUTE_POLICY,
    DISPOSITION_FAIL,
    DISPOSITION_INSUFFICIENT_EVIDENCE,
    StatisticalAcceptanceRoutePolicy,
)


class AdoptedPolicyInvariantTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy = ADOPTED_STATISTICAL_ACCEPTANCE_ROUTE_POLICY

    def test_adopted_policy_validates(self) -> None:
        # The ratified record must satisfy every acceptance boundary.
        self.assertIs(self.policy.validate(), self.policy)

    def test_route_is_a_now_plus_d_forward(self) -> None:
        self.assertEqual(
            self.policy.route, "ROUTE_A_NOW_PLUS_ROUTE_D_FORWARD"
        )
        self.assertEqual(self.policy.historical_chronology, "KEEP_FROZEN_12_6_6")

    def test_historical_path_cannot_fabricate_positive_pass(self) -> None:
        # Historical-v1 must never claim a general-domain positive PASS.
        self.assertFalse(self.policy.historical_positive_pass_claimable())
        self.assertEqual(
            self.policy.historical_positive_pass_claim,
            "NOT_REQUIRED_NOT_CLAIMED",
        )
        # The adopted policy never pretends old rejected PROFILE_0_4 became PASS:
        # no positive-PASS inference claim is attached anywhere on the record.
        self.assertNotIn("PASS", (self.policy.historical_positive_pass_claim,))

    def test_insufficient_evidence_is_legal(self) -> None:
        self.assertTrue(self.policy.insufficient_evidence_is_legal())
        self.assertIn(
            DISPOSITION_INSUFFICIENT_EVIDENCE,
            self.policy.historical_allowed_dispositions,
        )

    def test_fail_is_legal(self) -> None:
        self.assertTrue(self.policy.fail_is_legal())
        self.assertIn(DISPOSITION_FAIL, self.policy.historical_allowed_dispositions)

    def test_strong_fwer_still_binding(self) -> None:
        self.assertTrue(self.policy.strong_fwer_is_kept())
        self.assertEqual(self.policy.strong_fwer, "KEEP")

    def test_future_positive_path_does_not_authorize_shadow(self) -> None:
        # Route D designates future forward evidence as the acceptance path but
        # is NOT an authorization of Shadow/Forward now.
        self.assertEqual(
            self.policy.positive_acceptance_path,
            "FUTURE_GENUINELY_UNSEEN_PROSPECTIVE_SHADOW_FORWARD",
        )
        self.assertFalse(self.policy.future_positive_path_authorizes_shadow())
        self.assertEqual(self.policy.prospective_shadow_forward, "NOT_AUTHORIZED")

    def test_validation_and_final_locks_not_released(self) -> None:
        self.assertTrue(self.policy.validation_is_locked())
        self.assertEqual(self.policy.validation_access, "LOCKED")
        self.assertTrue(self.policy.final_holdout_is_locked())
        self.assertEqual(self.policy.historical_final_holdout_access, "LOCKED")
        self.assertEqual(self.policy.candidate_outcome_backtest, "NOT_AUTHORIZED")

    def test_outcome_tuning_still_forbidden(self) -> None:
        self.assertTrue(self.policy.outcome_tuning_is_forbidden())
        self.assertEqual(self.policy.outcome_calibrated_thresholds_status, "FORBIDDEN")
        self.assertEqual(self.policy.route_e_status, "FORBIDDEN")


class WeakenedPolicyRejectionTests(unittest.TestCase):
    """A corrupted or weakened record must fail the fail-closed validate()."""

    def _policy(self, **overrides) -> StatisticalAcceptanceRoutePolicy:
        base = {
            "route": "ROUTE_A_NOW_PLUS_ROUTE_D_FORWARD",
            "historical_chronology": "KEEP_FROZEN_12_6_6",
            "strong_fwer": "KEEP",
            "historical_positive_pass_claim": "NOT_REQUIRED_NOT_CLAIMED",
            "historical_allowed_dispositions": (
                DISPOSITION_FAIL,
                DISPOSITION_INSUFFICIENT_EVIDENCE,
            ),
            "positive_acceptance_path": (
                "FUTURE_GENUINELY_UNSEEN_PROSPECTIVE_SHADOW_FORWARD"
            ),
            "route_e_status": "FORBIDDEN",
            "outcome_calibrated_thresholds_status": "FORBIDDEN",
            "protocol_version_change_required": "NO",
            "new_historical_data_required": "NO",
            "prospective_shadow_forward": "NOT_AUTHORIZED",
            "candidate_outcome_backtest": "NOT_AUTHORIZED",
            "validation_access": "LOCKED",
            "historical_final_holdout_access": "LOCKED",
        }
        base.update(overrides)
        return StatisticalAcceptanceRoutePolicy(**base)

    def test_fabricated_historical_positive_pass_is_rejected(self) -> None:
        policy = self._policy(historical_positive_pass_claim="POSITIVE_PASS")
        with self.assertRaisesRegex(ValueError, "NOT_REQUIRED_NOT_CLAIMED"):
            policy.validate()

    def test_weakened_strong_fwer_is_rejected(self) -> None:
        policy = self._policy(strong_fwer="WEAKENED")
        with self.assertRaisesRegex(ValueError, "STRONG_FWER"):
            policy.validate()

    def test_shadow_auto_authorization_is_rejected(self) -> None:
        policy = self._policy(prospective_shadow_forward="AUTHORIZED")
        with self.assertRaisesRegex(ValueError, "PROSPECTIVE_SHADOW_FORWARD"):
            policy.validate()

    def test_validation_unlock_is_rejected(self) -> None:
        policy = self._policy(validation_access="UNLOCKED")
        with self.assertRaisesRegex(ValueError, "VALIDATION_ACCESS"):
            policy.validate()

    def test_final_holdout_unlock_is_rejected(self) -> None:
        policy = self._policy(historical_final_holdout_access="UNLOCKED")
        with self.assertRaisesRegex(ValueError, "HISTORICAL_FINAL_HOLDOUT_ACCESS"):
            policy.validate()

    def test_outcome_calibrated_thresholds_are_rejected(self) -> None:
        policy = self._policy(outcome_calibrated_thresholds_status="ALLOWED")
        with self.assertRaisesRegex(ValueError, "OUTCOME_CALIBRATED_THRESHOLDS"):
            policy.validate()

    def test_route_e_is_rejected(self) -> None:
        policy = self._policy(route_e_status="OPTIONAL")
        with self.assertRaisesRegex(ValueError, "ROUTE_E"):
            policy.validate()

    def test_removing_ie_disposition_is_rejected(self) -> None:
        policy = self._policy(
            historical_allowed_dispositions=(DISPOSITION_FAIL,)
        )
        with self.assertRaisesRegex(ValueError, "INSUFFICIENT_EVIDENCE"):
            policy.validate()


class FirewallCrossCheckTests(unittest.TestCase):
    """The firewall registry still refuses a real (non-TEST_ONLY) profile lock.

    This is the existing code-enforced guard that makes a fabricated historical
    positive PASS structurally impossible on the historical path, independent of
    the declarative policy record.
    """

    def _real_profile(self, profile_id: str = "profile-real-route-v1") -> CommonStatisticalProfile:
        return CommonStatisticalProfile(
            profile_id=profile_id,
            profile_version="1.0",
            uncertainty_precision_method="METHOD",
            evidence_sufficiency_procedure="PROCEDURE",
            dependence_handling="HANDLING",
            multiplicity_decision_rule="RULE",
            common_acceptance_procedure="PROCEDURE_NOT_SPECIFIED",
        )

    def test_real_profile_cannot_be_locked(self) -> None:
        registry = StatisticalProfileRegistry()
        profile = registry.register(self._real_profile())
        with self.assertRaisesRegex(ValueError, "REAL_STATISTICAL_PROFILE_NOT_ADOPTED"):
            registry.lock(profile.profile_id)
        self.assertFalse(registry.is_locked(profile.profile_id))

    def test_no_real_profile_is_adopted(self) -> None:
        # The adopted policy has no real positive-PASS profile: locking any real
        # profile stays forbidden, so historical-v1 cannot emit a PASS.
        registry = StatisticalProfileRegistry()
        self.assertEqual(registry.locked_profile_ids, ())
        registry.register(self._real_profile("profile-real-route-v2"))
        self.assertEqual(registry.locked_profile_ids, ())


if __name__ == "__main__":
    unittest.main()

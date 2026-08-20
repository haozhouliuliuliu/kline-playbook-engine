"""Owner-ratified statistical acceptance route policy (machine-readable).

Authority (binding, adopted 2026-08-21):
- ``docs/evidence/COMMON_STATISTICAL_PROFILE_ROUTE_A_D_OWNER_APPROVAL_2026-08-21.md``
- adopted ``docs/research/HUMAN_PLAYBOOK_STATISTICAL_ACCEPTANCE_ROUTE_POLICY_V1_0.md``
- prior decision package ``docs/reviews/COMMON_STATISTICAL_PROFILE_OWNER_DECISION_PACKAGE_V0_1.md``
  (branch ``preoutcome/stat-profile-owner-decision-v01``)
- frozen ``docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md``
- frozen ``docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md``

This module is a minimal, versioned, machine-readable record of the binding Owner
ratification:

``STATISTICAL_ACCEPTANCE_ROUTE=ROUTE_A_NOW_PLUS_ROUTE_D_FORWARD``

It is NOT a numerical statistical standard. It does NOT unlock candidate-outcome
access, does NOT weaken strong-FWER, and does NOT authorize Shadow/Forward now.
Frozen Protocol v1.0 and the frozen 12/6/6 chronology remain unchanged. The
machine-readable record exists so the acceptance-boundary invariants (historical
positive-PASS not claimable; IE and FAIL legal; strong-FWER kept; future-positive
path not an automatic Shadow grant; VALIDATION / historical-final locks intact;
outcome-calibrated thresholds forbidden) are verifiable in code.
"""

from __future__ import annotations

from dataclasses import dataclass

# Owner-ratified route identity (COMMON_STATISTICAL_PROFILE_ROUTE_A_D_OWNER_RATIFICATION_V0_1).
ROUTE_A_NOW_PLUS_ROUTE_D_FORWARD = "ROUTE_A_NOW_PLUS_ROUTE_D_FORWARD"

# Frozen chronology / FWER dispositions (unchanged by the ratification).
KEEP_FROZEN_12_6_6 = "KEEP_FROZEN_12_6_6"
KEEP = "KEEP"
NOT_REQUIRED_NOT_CLAIMED = "NOT_REQUIRED_NOT_CLAIMED"
FUTURE_GENUINELY_UNSEEN_PROSPECTIVE_SHADOW_FORWARD = (
    "FUTURE_GENUINELY_UNSEEN_PROSPECTIVE_SHADOW_FORWARD"
)
FORBIDDEN = "FORBIDDEN"
NOT_AUTHORIZED = "NOT_AUTHORIZED"
LOCKED = "LOCKED"
NO = "NO"

# Historical split dispositions that remain legitimate under the ratified route.
DISPOSITION_FAIL = "FAIL"
DISPOSITION_INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
DISPOSITION_GOVERNED_DIAGNOSTICS = "GOVERNED_DIAGNOSTICS"


@dataclass(frozen=True)
class StatisticalAcceptanceRoutePolicy:
    """Versioned machine-readable record of the Owner-ratified acceptance route.

    Every field encodes one binding fact from the ratified Owner decision. The
    invariant helpers below expose the acceptance boundaries in a way tests and
    downstream tooling can verify deterministically.
    """

    route: str
    historical_chronology: str
    strong_fwer: str
    historical_positive_pass_claim: str
    historical_allowed_dispositions: tuple[str, ...]
    positive_acceptance_path: str
    route_e_status: str
    outcome_calibrated_thresholds_status: str
    protocol_version_change_required: str
    new_historical_data_required: str
    prospective_shadow_forward: str
    candidate_outcome_backtest: str
    validation_access: str
    historical_final_holdout_access: str
    policy_version: str = "1.0"

    # --- acceptance-boundary invariants -------------------------------

    def historical_positive_pass_claimable(self) -> bool:
        """Historical-v1 must never fabricate a general-domain positive PASS.

        The frozen 12/6/6 cohorts keep governed roles (negative evidence, IE,
        diagnostics, integrity exam) but are not a general-domain acceptance gate.
        """
        return False

    def insufficient_evidence_is_legal(self) -> bool:
        return DISPOSITION_INSUFFICIENT_EVIDENCE in self.historical_allowed_dispositions

    def fail_is_legal(self) -> bool:
        return DISPOSITION_FAIL in self.historical_allowed_dispositions

    def strong_fwer_is_kept(self) -> bool:
        return self.strong_fwer == KEEP

    def future_positive_path_authorizes_shadow(self) -> bool:
        """Route D designates forward evidence as the acceptance path but is not
        itself a Shadow/Forward authorization grant."""
        return False

    def validation_is_locked(self) -> bool:
        return self.validation_access == LOCKED

    def final_holdout_is_locked(self) -> bool:
        return self.historical_final_holdout_access == LOCKED

    def outcome_tuning_is_forbidden(self) -> bool:
        return self.outcome_calibrated_thresholds_status == FORBIDDEN

    def validate(self) -> "StatisticalAcceptanceRoutePolicy":
        """Fail-closed invariant check.

        Raises ``ValueError`` if any ratified acceptance boundary is violated, so
        a corrupted or weakened policy record cannot be treated as adopted.
        """
        if self.route != ROUTE_A_NOW_PLUS_ROUTE_D_FORWARD:
            raise ValueError("STATISTICAL_ACCEPTANCE_ROUTE must be ROUTE_A_NOW_PLUS_ROUTE_D_FORWARD")
        if self.historical_chronology != KEEP_FROZEN_12_6_6:
            raise ValueError("HISTORICAL_CHRONOLOGY must keep frozen 12/6/6")
        if self.strong_fwer != KEEP:
            raise ValueError("STRONG_FWER must be KEEP")
        if self.historical_positive_pass_claim != NOT_REQUIRED_NOT_CLAIMED:
            raise ValueError(
                "HISTORICAL_GENERAL_DOMAIN_POSITIVE_PASS must be NOT_REQUIRED_NOT_CLAIMED"
            )
        if not self.insufficient_evidence_is_legal():
            raise ValueError("INSUFFICIENT_EVIDENCE must remain a legal historical disposition")
        if not self.fail_is_legal():
            raise ValueError("FAIL must remain a legal historical disposition")
        if self.positive_acceptance_path != FUTURE_GENUINELY_UNSEEN_PROSPECTIVE_SHADOW_FORWARD:
            raise ValueError(
                "POSITIVE_ACCEPTANCE_PATH must be FUTURE_GENUINELY_UNSEEN_PROSPECTIVE_SHADOW_FORWARD"
            )
        if self.route_e_status != FORBIDDEN:
            raise ValueError("ROUTE_E must be FORBIDDEN")
        if self.outcome_calibrated_thresholds_status != FORBIDDEN:
            raise ValueError("OUTCOME_CALIBRATED_THRESHOLDS must be FORBIDDEN")
        if self.protocol_version_change_required != NO:
            raise ValueError("PROTOCOL_VERSION_CHANGE_REQUIRED must be NO")
        if self.new_historical_data_required != NO:
            raise ValueError("NEW_HISTORICAL_DATA_REQUIRED must be NO")
        if self.prospective_shadow_forward != NOT_AUTHORIZED:
            raise ValueError("PROSPECTIVE_SHADOW_FORWARD must remain NOT_AUTHORIZED")
        if self.candidate_outcome_backtest != NOT_AUTHORIZED:
            raise ValueError("CANDIDATE_OUTCOME_BACKTEST must remain NOT_AUTHORIZED")
        if self.validation_access != LOCKED:
            raise ValueError("VALIDATION_ACCESS must remain LOCKED")
        if self.historical_final_holdout_access != LOCKED:
            raise ValueError("HISTORICAL_FINAL_HOLDOUT_ACCESS must remain LOCKED")
        return self


# The single adopted instance of the ratified route policy. Every other value is
# a test-only construction and must fail ``validate()`` if it weakens a boundary.
ADOPTED_STATISTICAL_ACCEPTANCE_ROUTE_POLICY = StatisticalAcceptanceRoutePolicy(
    route=ROUTE_A_NOW_PLUS_ROUTE_D_FORWARD,
    historical_chronology=KEEP_FROZEN_12_6_6,
    strong_fwer=KEEP,
    historical_positive_pass_claim=NOT_REQUIRED_NOT_CLAIMED,
    historical_allowed_dispositions=(
        DISPOSITION_FAIL,
        DISPOSITION_INSUFFICIENT_EVIDENCE,
        DISPOSITION_GOVERNED_DIAGNOSTICS,
    ),
    positive_acceptance_path=FUTURE_GENUINELY_UNSEEN_PROSPECTIVE_SHADOW_FORWARD,
    route_e_status=FORBIDDEN,
    outcome_calibrated_thresholds_status=FORBIDDEN,
    protocol_version_change_required=NO,
    new_historical_data_required=NO,
    prospective_shadow_forward=NOT_AUTHORIZED,
    candidate_outcome_backtest=NOT_AUTHORIZED,
    validation_access=LOCKED,
    historical_final_holdout_access=LOCKED,
)

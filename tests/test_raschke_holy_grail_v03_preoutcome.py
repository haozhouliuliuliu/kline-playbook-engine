"""Focused pre-outcome tests for the Holy Grail V0.3 Playbook Contract draft.

These tests prove that V0.3:

- preserves the immutable V0.2 artifacts untouched;
- preserves the existing source-claim corpus/provenance from V0.2 / SOURCE_ONLY;
- keeps SOURCE CLAIM != PROJECT INTERPRETATION != MACHINE OPERATIONALIZATION;
- encodes ONLY the Owner-approved F/G/H decisions, with every still-open
  operationalization prerequisite explicit and fail-closed;
- remains NOT_MACHINE_READY and performs no candidate outcome registration/access.
"""

import ast
import json
import unittest
from pathlib import Path

from src.playbook_contract import MachineReadiness, validate_contract
from tools.build_raschke_holy_grail_playbook_contract_draft import (
    build_payload as build_v0_2_payload,
)
from tools.build_raschke_holy_grail_playbook_contract_draft_v0_3 import (
    FGH_APPROVED_DECISIONS,
    OPEN_PREREQUISITES,
    build_contract,
    build_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = REPO_ROOT / "docs" / "evidence"

V0_2_JSON = EVIDENCE_DIR / "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_2.json"
V0_2_MD = EVIDENCE_DIR / "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_2.md"
V0_2_STATUS_MD = EVIDENCE_DIR / "RASCHKE_HOLY_GRAIL_INTERPRETATION_STATUS_V0_2.md"
V0_3_JSON = EVIDENCE_DIR / "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_3.json"
V0_3_BUILDER = (
    REPO_ROOT / "tools" / "build_raschke_holy_grail_playbook_contract_draft_v0_3.py"
)

EXPECTED_BLOCKERS = {
    "UNRESOLVED_CRITICAL_AMBIGUITY",
    "CLAIM_PRIMARY_MISSING",
    "REQUIRED_INPUT_NOT_FULLY_OBSERVABLE",
    "MACHINE_OPERATIONALIZATION_MISSING",
    "MULTIPLE_TIMEFRAMES_UNRESOLVED",
}

EXPECTED_OPEN_PREREQUISITES = {
    "HOLY_GRAIL_BASE_TO_MACHINE_INTERVAL": "OPEN",
    "HOLY_GRAIL_ADX_RISING_WINDOW": "OPEN_VERSIONED_NON_OUTCOME_CHOICE",
    "HOLY_GRAIL_SWING_CONFIRMATION_COUNTS": "OPEN_VERSIONED_NON_OUTCOME_CHOICE",
    "HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION": "NOT_ADOPTED",
}


class RaschkeHolyGrailV03PreOutcomeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_payload()
        cls.contract = build_contract()
        cls.checked_in = json.loads(V0_3_JSON.read_text(encoding="utf-8"))
        cls.v0_2 = json.loads(V0_2_JSON.read_text(encoding="utf-8"))

    # ---- V0.2 immutability ----
    def test_v0_2_artifacts_are_untouched(self):
        self.assertTrue(V0_2_JSON.is_file())
        self.assertTrue(V0_2_MD.is_file())
        self.assertTrue(V0_2_STATUS_MD.is_file())
        # V0.2 builder still deterministically reproduces the checked-in V0.2
        # JSON (byte-for-byte), proving no V0.2 evidence was rewritten.
        self.assertEqual(build_v0_2_payload(), json.loads(V0_2_JSON.read_text(encoding="utf-8")))
        self.assertEqual(
            "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_2",
            self.v0_2["artifact"],
        )
        self.assertEqual("PC-RASCHKE-HOLY-GRAIL-PULLBACK-DRAFT-V0-2", self.v0_2["contract_id"])
        self.assertIn("V0_2", V0_2_MD.read_text(encoding="utf-8"))
        self.assertIn("V0_2", V0_2_STATUS_MD.read_text(encoding="utf-8"))

    # ---- Source-claim preservation ----
    def test_v0_3_preserves_v0_2_source_claim_corpus(self):
        self.assertEqual(self.v0_2["source_claims"], self.payload["source_claims"])
        self.assertEqual(27, self.payload["source_evidence_recorded_claim_count"])
        self.assertEqual(
            27,
            len({claim["claim_id"] for claim in self.payload["source_claims"]}),
        )
        by_id = {claim["claim_id"]: claim for claim in self.payload["source_claims"]}
        # Source anchors/provenance are preserved verbatim (same order as V0.2).
        self.assertEqual(
            "SR-V0-M05:toolbox:section:HOLY_GRAIL_SETUP; "
            "SR-V0-M01:august1997:section:HOLY_GRAIL_RULES",
            by_id["C-RAS-HG-SEM-001"]["source_anchor"],
        )
        # No UNKNOWN claim is filled with a guess and no INFERRED is relabeled EXPLICIT.
        self.assertEqual("UNKNOWN", by_id["C-RAS-HG-SEM-007"]["claim_status"])
        self.assertEqual("UNKNOWN", by_id["C-RAS-HG-SEM-020"]["claim_status"])
        self.assertEqual("UNKNOWN", by_id["C-RAS-HG-SEM-021"]["claim_status"])
        self.assertEqual("UNKNOWN", by_id["C-RAS-HG-SEM-026"]["claim_status"])
        self.assertEqual("INFERRED", by_id["C-RAS-HG-SEM-027"]["claim_status"])

    def test_source_pinned_interpretation_branches_are_preserved(self):
        v0_2_branches = {b["branch_id"]: b for b in self.v0_2["interpretations"]}
        v0_3_branches = {b["branch_id"]: b for b in self.payload["interpretations"]}
        for branch_id in (
            "SOURCE-PINNED-ADX-EMA-CONCEPTS",
            "SOURCE-PINNED-ENTRY-RISK-EXIT-CONCEPTS",
            "SOURCE-PINNED-MULTI-TIMEFRAME-CONCEPT",
        ):
            self.assertIn(branch_id, v0_3_branches)
            self.assertEqual(v0_2_branches[branch_id], v0_3_branches[branch_id])

    # ---- Layer separation ----
    def test_source_interpretation_machine_layers_remain_distinct(self):
        branches = {b["branch_id"]: b for b in self.payload["interpretations"]}
        # Source-pinned branches stay EXPLICIT; Owner-approved conventions are
        # never relabeled EXPLICIT (they are project INFERRED machine conventions).
        for branch_id, branch in branches.items():
            if branch_id.startswith("SOURCE-PINNED-"):
                self.assertEqual("EXPLICIT", branch["transfer_status"], branch_id)
            else:
                self.assertEqual("INFERRED", branch["transfer_status"], branch_id)
        # No machine layer is adopted.
        self.assertIsNone(self.payload["machine_operationalization"])
        self.assertIsNone(self.contract.machine)
        # No PRIMARY is selected.
        self.assertFalse(any(b["primary_selected"] for b in branches.values()))

    # ---- EMA touch ----
    def test_prior_completed_bar_ema_convention_is_encoded(self):
        ema = self.payload["fgh_approved_decisions"]["EMA_TOUCH"]
        self.assertEqual("20", ema["EMA_PERIOD"])
        self.assertEqual("PROJECT_INFERRED_CLOSE", ema["EMA_PRICE_BASIS"])
        self.assertEqual("PRIOR_COMPLETED_BAR_AVAILABLE", ema["EMA_REFERENCE"])
        self.assertEqual("BAR_LOW_LE_EMA_PRIOR_LE_BAR_HIGH", ema["TOUCH_RULE"])
        ema_branch = next(
            b for b in self.payload["interpretations"]
            if b["branch_id"] == "FGH-DECIDED-EMA-TOUCH-CONVENTION"
        )
        self.assertIn("PRIOR_COMPLETED_BAR_AVAILABLE", ema_branch["source_basis"])
        self.assertIn("PROJECT_INFERRED_CLOSE", ema_branch["source_basis"])
        self.assertIn("not a source claim", ema_branch["source_basis"])

    def test_current_bar_close_lookahead_is_forbidden(self):
        ema = self.payload["fgh_approved_decisions"]["EMA_TOUCH"]
        self.assertEqual("FORBIDDEN", ema["CURRENT_BAR_CLOSE_LOOKAHEAD"])
        ema_branch = next(
            b for b in self.payload["interpretations"]
            if b["branch_id"] == "FGH-DECIDED-EMA-TOUCH-CONVENTION"
        )
        self.assertIn("CURRENT_BAR_CLOSE_LOOKAHEAD=FORBIDDEN", ema_branch["source_basis"])
        self.assertNotIn("CURRENT_BAR_CLOSE_LOOKAHEAD=ALLOWED", ema_branch["source_basis"])

    # ---- ADX ----
    def test_adx_pre_pullback_semantics_are_encoded(self):
        adx = self.payload["fgh_approved_decisions"]["ADX"]
        self.assertEqual("14", adx["ADX_PERIOD"])
        self.assertEqual(">30", adx["ADX_THRESHOLD"])
        self.assertEqual("INITIAL_PRE_PULLBACK", adx["ADX_CONTEXT"])
        self.assertEqual("NO", adx["TOUCH_BAR_RISING_REQUIRED"])
        self.assertEqual("NOT_AUTHORITY", adx["OLD_TOUCH_BAR_ONE_STEP_RULE"])

    def test_adx_rising_window_remains_unresolved(self):
        adx = self.payload["fgh_approved_decisions"]["ADX"]
        self.assertEqual("OPEN_VERSIONED_NON_OUTCOME_CHOICE", adx["ADX_RISING_WINDOW"])
        self.assertEqual(
            "OPEN_VERSIONED_NON_OUTCOME_CHOICE",
            self.payload["open_prerequisites"]["HOLY_GRAIL_ADX_RISING_WINDOW"],
        )
        adx_branch = next(
            b for b in self.payload["interpretations"]
            if b["branch_id"] == "FGH-DECIDED-ADX-PRE-PULLBACK-CONTEXT"
        )
        self.assertIn("OPEN_VERSIONED_NON_OUTCOME_CHOICE", adx_branch["source_basis"])

    # ---- Numeric policy ----
    def test_numeric_policy_is_exactly_the_owner_approved_policy(self):
        policy = self.payload["fgh_approved_decisions"]["NUMERIC_POLICY"]
        self.assertEqual(
            {
                "EMA_SEED": "SMA",
                "ADX_INITIALIZATION": "WILDER_SMA_DX",
                "ARITHMETIC": "DECIMAL",
                "QUANTIZATION": "6DP_ROUND_HALF_UP",
                "NUMERIC_POLICY": "VERSIONED_IDENTITY_BOUND",
            },
            policy,
        )
        self.assertNotEqual("ROUND_HALF_EVEN", policy["QUANTIZATION"])

    # ---- Same-bar touch -> entry ----
    def test_same_bar_touch_entry_remains_fail_closed(self):
        decision = self.payload["fgh_approved_decisions"]["SAME_BAR_TOUCH_ENTRY"]
        self.assertEqual("AMBIGUOUS_INTRABAR_SEQUENCE", decision["SAME_BAR_TOUCH_ENTRY"])
        self.assertEqual("YES", decision["FAIL_CLOSED"])
        chronology_surface = next(
            s for s in self.payload["observation_surfaces"]
            if s["surface_id"] == "ENTRY_AND_PROTECTIVE_STOP_CHRONOLOGY"
        )
        self.assertEqual("PARTIALLY_OBSERVABLE", chronology_surface["observability_status"])
        self.assertEqual(["intrabar_ordering_at_one_minute"], chronology_surface["missing_inputs"])

    # ---- Same-bar fill -> protective stop ----
    def test_same_bar_fill_stop_remains_fail_closed(self):
        decision = self.payload["fgh_approved_decisions"]["FILL_PROTECTIVE_STOP_CHRONOLOGY"]
        self.assertEqual("COMPLETED_BAR_AVAILABILITY_CONSERVATIVE", decision["CHRONOLOGY"])
        self.assertEqual("NO", decision["EXCHANGE_RESTING_CLAIM"])
        self.assertEqual("AMBIGUOUS_INTRABAR_SEQUENCE", decision["SAME_BAR_FILL_STOP"])
        self.assertEqual("REJECTED", decision["NEXT_BAR_ONLY_STOP_ACTIVATION_DEFAULT"])
        self.assertEqual("NOT_OBSERVABLE_AT_1M", decision["INTRABAR_ORDERING"])

    # ---- Timeframe ----
    def test_base_is_primary_branch_without_concrete_interval(self):
        timeframe = self.payload["fgh_approved_decisions"]["TIMEFRAME"]
        self.assertEqual("BASE", timeframe["PRIMARY_TIMEFRAME_BRANCH"])
        self.assertEqual("30MIN,60MIN,120MIN", timeframe["SOURCE_ALTERNATIVES"])
        self.assertEqual("OPEN", timeframe["BASE_TO_MACHINE_INTERVAL"])
        self.assertEqual(
            "OPEN",
            self.payload["open_prerequisites"]["HOLY_GRAIL_BASE_TO_MACHINE_INTERVAL"],
        )
        # Source timeframes remain explicit; no concrete interval is selected.
        self.assertEqual(["120MIN", "30MIN", "60MIN", "BASE"], self.payload["timeframe_scope"])
        self.assertIn("MULTIPLE_TIMEFRAMES_UNRESOLVED", self.payload["machine_readiness_blockers"])

    # ---- Swing low/high ----
    def test_pivot_right_confirmation_semantics_exist_counts_unresolved(self):
        swing = self.payload["fgh_approved_decisions"]["SWING_LOW_HIGH"]
        self.assertEqual("FRACTAL_PIVOT_EXPLICIT_CONFIRMATION", swing["SWING_DEFINITION"])
        self.assertEqual("YES", swing["RIGHT_SIDE_CONFIRMATION_REQUIRED"])
        self.assertEqual("NO", swing["SAME_BAR_AVAILABILITY"])
        self.assertEqual("MIRROR_SWING_HIGH", swing["SHORT_SIDE"])
        self.assertEqual(
            "OPEN_VERSIONED_NON_OUTCOME_CHOICE", swing["SWING_CONFIRMATION_COUNTS"]
        )
        self.assertEqual(
            "OPEN_VERSIONED_NON_OUTCOME_CHOICE",
            self.payload["open_prerequisites"]["HOLY_GRAIL_SWING_CONFIRMATION_COUNTS"],
        )
        swing_surface = next(
            s for s in self.payload["observation_surfaces"]
            if s["surface_id"] == "SWING_LOW_CONFIRMATION"
        )
        self.assertEqual(["swing_confirmation_counts"], swing_surface["missing_inputs"])

    # ---- Trailing stop ----
    def test_no_trailing_algorithm_is_present(self):
        trailing = self.payload["fgh_approved_decisions"]["TRAILING_STOP"]
        self.assertEqual("NOT_ADOPTED", trailing["TRAILING_STOP_MACHINE_DEFINITION"])
        self.assertEqual("PRESERVE", trailing["MACHINE_READY_BLOCKER"])
        self.assertEqual("FORBIDDEN", trailing["OUTCOME_TUNING_FOR_TRAILING"])
        self.assertEqual(
            "NOT_ADOPTED",
            self.payload["open_prerequisites"]["HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION"],
        )
        trailing_branch = next(
            b for b in self.payload["interpretations"]
            if b["branch_id"] == "FGH-DECIDED-TRAILING-STOP-NOT-ADOPTED"
        )
        # The branch explicitly refuses to authorize any concrete trailing
        # mechanism, so none is selected as a machine algorithm.
        self.assertIn("does not authorize", trailing_branch["source_basis"])
        self.assertIn("NOT_ADOPTED", trailing_branch["source_basis"])
        # No machine layer exists in which a trailing rule could be operationalized.
        self.assertIsNone(self.payload["machine_operationalization"])

    # ---- Exit on push to new highs ----
    def test_new_high_exit_is_optional_not_primary(self):
        exit_decision = self.payload["fgh_approved_decisions"]["EXIT_ON_PUSH_TO_NEW_HIGHS"]
        self.assertEqual("OPTIONAL_VERSIONED_VARIANT", exit_decision["EXIT_ON_PUSH_TO_NEW_HIGHS"])
        self.assertEqual("NO", exit_decision["PRIMARY_EXIT_REPLACED"])
        self.assertEqual("FORBIDDEN", exit_decision["OUTCOME_RESCUE"])
        self.assertFalse(any(b["primary_selected"] for b in self.payload["interpretations"]))
        exit_branch = next(
            b for b in self.payload["interpretations"]
            if b["branch_id"] == "FGH-DECIDED-EXIT-NEW-HIGHS-OPTIONAL"
        )
        self.assertIn("OPTIONAL_VERSIONED_VARIANT", exit_branch["source_basis"])
        self.assertIn("not the Holy Grail PRIMARY exit", exit_branch["source_basis"])

    # ---- Readiness ----
    def test_readiness_remains_no(self):
        self.assertEqual(MachineReadiness.NOT_MACHINE_READY, validate_contract(self.contract).readiness)
        self.assertEqual("NOT_MACHINE_READY", self.payload["machine_readiness"])
        self.assertIsNone(self.payload["machine_operationalization"])
        self.assertEqual(
            {"MACHINE_READY": "NO", "PRIMARY_FREEZE_READY": "NO",
             "STRATEGY_IDENTITY_CREATED": "NO", "OUTCOME_TEST_REGISTERED": "NO",
             "CANDIDATE_OUTCOME_DATA_USED": "NO"},
            self.payload["final_decision"],
        )
        self.assertEqual(
            {"UNRESOLVED_CRITICAL_AMBIGUITY", "CLAIM_PRIMARY_MISSING",
             "REQUIRED_INPUT_NOT_FULLY_OBSERVABLE", "MACHINE_OPERATIONALIZATION_MISSING",
             "MULTIPLE_TIMEFRAMES_UNRESOLVED"},
            set(self.payload["machine_readiness_blockers"]),
        )
        self.assertEqual(EXPECTED_OPEN_PREREQUISITES, self.payload["open_prerequisites"])
        self.assertEqual(
            [
                "BASE_TO_MACHINE_INTERVAL",
                "ADX_RISING_WINDOW",
                "SWING_CONFIRMATION_COUNTS",
                "TRAILING_STOP_MACHINE_DEFINITION",
            ],
            self.payload["unresolved_machine_definitions"],
        )

    def test_checked_in_v0_3_artifact_is_deterministic(self):
        self.assertEqual(self.payload, self.checked_in)
        self.assertEqual("RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_3", self.checked_in["artifact"])
        self.assertEqual("PC-RASCHKE-HOLY-GRAIL-PULLBACK-DRAFT-V0-3", self.checked_in["contract_id"])
        self.assertEqual("PC-RASCHKE-HOLY-GRAIL-PULLBACK-DRAFT-V0-2", self.checked_in["parent_contract_id"])

    # ---- No candidate outcome registration/access ----
    def test_no_candidate_outcome_registration_or_access(self):
        self.assertEqual("NO", self.payload["final_decision"]["CANDIDATE_OUTCOME_DATA_USED"])
        self.assertEqual("NO", self.payload["final_decision"]["OUTCOME_TEST_REGISTERED"])
        self.assertEqual("NO", self.payload["final_decision"]["STRATEGY_IDENTITY_CREATED"])
        source = V0_3_BUILDER.read_text(encoding="utf-8")
        # The V0.3 builder imports ONLY the generic playbook-contract layer and
        # stdlib. It must never import outcome/firewall/validation machinery or
        # call any outcome-registration / candidate-outcome-access surface.
        tree = ast.parse(source)
        imported: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imported.append(node.module or "")
        for module in imported:
            self.assertNotIn(
                module,
                {
                    "src.research_firewall",
                    "src.strategy_evidence",
                    "src.validation_runner",
                    "src.round_trip_ledger",
                    "src.portfolio_semantics",
                },
            )
        self.assertTrue(any(module == "src.playbook_contract" for module in imported))
        for forbidden in (
            "register_outcome_test",
            "request_candidate_outcome_access",
            "bridge_to_strategy_identity",
        ):
            self.assertNotIn(forbidden, source)
        # No machine layer exists in which an outcome test could be registered.
        self.assertIsNone(self.payload["machine_operationalization"])
        # The decisions are exactly the Owner-approved set; nothing extra is invented.
        self.assertEqual(
            {
                "EMA_TOUCH", "ADX", "NUMERIC_POLICY", "SAME_BAR_TOUCH_ENTRY",
                "FILL_PROTECTIVE_STOP_CHRONOLOGY", "TIMEFRAME", "SWING_LOW_HIGH",
                "TRAILING_STOP", "EXIT_ON_PUSH_TO_NEW_HIGHS",
            },
            set(FGH_APPROVED_DECISIONS),
        )
        self.assertEqual(FGH_APPROVED_DECISIONS, self.payload["fgh_approved_decisions"])
        self.assertEqual(OPEN_PREREQUISITES, self.payload["open_prerequisites"])


if __name__ == "__main__":
    unittest.main()

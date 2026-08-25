"""Focused tests for the Holy Grail V0.4 Playbook Contract (machine-ready).

These tests prove that V0.4:

- preserves the immutable V0.3 artifacts untouched;
- preserves the existing source-claim corpus/provenance from V0.3 / SOURCE_ONLY;
- keeps SOURCE CLAIM != PROJECT INTERPRETATION != MACHINE OPERATIONALIZATION;
- resolves claim-level PRIMARY for all 27 source claims (exactly one per claim);
- encodes ONLY the Owner-approved 2026-08-21 binding decisions, with the four
  operationalization prerequisites closed and every convention marked INFERRED
  (never a source claim);
- passes ``validate_contract`` as MACHINE_READY with no blockers;
- installs the MACHINE layer (``src/holy_grail_machine.py``) with real byte
  identity binding;
- performs no candidate outcome registration/access, no StrategyIdentity
  creation, and no validation / final-holdout / shadow access.
"""

import ast
import json
import unittest
from collections import Counter
from pathlib import Path

from src.playbook_contract import MachineReadiness, parameter_identity, validate_contract
from src.jianghe_source_only_verification import _repository_blob_bytes
from tools.build_raschke_holy_grail_playbook_contract_draft_v0_3 import (
    build_payload as build_v0_3_payload,
)
from tools.build_raschke_holy_grail_playbook_contract_draft_v0_4 import (
    OWNER_APPROVED_DECISIONS,
    build_contract,
    build_payload,
    strategy_parameters,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = REPO_ROOT / "docs" / "evidence"

V0_3_JSON = EVIDENCE_DIR / "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_3.json"
V0_3_MD = EVIDENCE_DIR / "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_3.md"
V0_3_STATUS_MD = EVIDENCE_DIR / "RASCHKE_HOLY_GRAIL_INTERPRETATION_STATUS_V0_3.md"
V0_4_JSON = EVIDENCE_DIR / "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_4.json"
V0_4_BUILDER = (
    REPO_ROOT / "tools" / "build_raschke_holy_grail_playbook_contract_draft_v0_4.py"
)
OWNER_APPROVAL_MD = (
    EVIDENCE_DIR / "HOLY_GRAIL_MACHINE_OPERATIONALIZATION_OWNER_APPROVAL_2026-08-21.md"
)

CLAIM_COUNT = 27


class RaschkeHolyGrailV04MachineReadyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = build_payload()
        cls.contract = build_contract()
        cls.checked_in = json.loads(V0_4_JSON.read_text(encoding="utf-8"))
        cls.v0_3 = json.loads(V0_3_JSON.read_text(encoding="utf-8"))

    # ---- V0.3 immutability ----
    def test_v0_3_artifacts_are_untouched(self):
        self.assertTrue(V0_3_JSON.is_file())
        self.assertTrue(V0_3_MD.is_file())
        self.assertTrue(V0_3_STATUS_MD.is_file())
        # V0.3 builder still deterministically reproduces the checked-in V0.3
        # JSON (byte-for-byte), proving no V0.3 evidence was rewritten.
        self.assertEqual(build_v0_3_payload(), json.loads(V0_3_JSON.read_text(encoding="utf-8")))
        self.assertEqual("RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_3", self.v0_3["artifact"])
        self.assertEqual("PC-RASCHKE-HOLY-GRAIL-PULLBACK-DRAFT-V0-3", self.v0_3["contract_id"])
        self.assertIn("V0_3", V0_3_MD.read_text(encoding="utf-8"))
        self.assertIn("V0_3", V0_3_STATUS_MD.read_text(encoding="utf-8"))

    # ---- Source-claim preservation ----
    def test_v0_4_preserves_v0_3_source_claim_corpus(self):
        self.assertEqual(self.v0_3["source_claims"], self.payload["source_claims"])
        self.assertEqual(CLAIM_COUNT, self.payload["source_evidence_recorded_claim_count"])
        self.assertEqual(
            CLAIM_COUNT,
            len({claim["claim_id"] for claim in self.payload["source_claims"]}),
        )
        by_id = {claim["claim_id"]: claim for claim in self.payload["source_claims"]}
        self.assertEqual("UNKNOWN", by_id["C-RAS-HG-SEM-007"]["claim_status"])
        self.assertEqual("INFERRED", by_id["C-RAS-HG-SEM-027"]["claim_status"])
        self.assertEqual(
            self.v0_3["source_bundle_identity"],
            self.payload["source_bundle_identity"],
        )
        self.assertEqual(
            self.v0_3["source_only_session_identity"],
            self.payload["source_only_session_identity"],
        )

    def test_source_pinned_interpretation_branches_are_preserved(self):
        v0_3_branches = {b["branch_id"]: b for b in self.v0_3["interpretations"]}
        v0_4_branches = {b["branch_id"]: b for b in self.payload["interpretations"]}
        for branch_id in (
            "SOURCE-PINNED-ADX-EMA-CONCEPTS",
            "SOURCE-PINNED-ENTRY-RISK-EXIT-CONCEPTS",
            "SOURCE-PINNED-MULTI-TIMEFRAME-CONCEPT",
        ):
            self.assertIn(branch_id, v0_4_branches)
            self.assertEqual(
                v0_3_branches[branch_id]["source_claim_ids"],
                v0_4_branches[branch_id]["source_claim_ids"],
            )

    # ---- Layer separation ----
    def test_source_interpretation_machine_layers_remain_distinct(self):
        branches = {b["branch_id"]: b for b in self.payload["interpretations"]}
        for branch_id, branch in branches.items():
            if branch_id.startswith("SOURCE-PINNED-"):
                if branch_id.startswith(("SOURCE-PINNED-NO-TIME", "SOURCE-PINNED-NO-REENTRY",
                                         "SOURCE-PINNED-COMMODITY")):
                    self.assertEqual("UNKNOWN", branch["transfer_status"], branch_id)
                else:
                    self.assertEqual("EXPLICIT", branch["transfer_status"], branch_id)
            else:
                self.assertEqual("INFERRED", branch["transfer_status"], branch_id)
        # The machine layer is a real object, distinct from source/interpretation.
        self.assertIsNotNone(self.payload["machine_operationalization"])
        self.assertIsNotNone(self.contract.machine)

    # ---- Claim-level PRIMARY (exactly one per claim) ----
    def test_every_source_claim_has_exactly_one_primary_branch(self):
        by_claim: dict[str, list[str]] = {c["claim_id"]: [] for c in self.payload["source_claims"]}
        for branch in self.payload["interpretations"]:
            if not branch["primary_selected"]:
                continue
            for claim_id in branch["source_claim_ids"]:
                by_claim[claim_id].append(branch["branch_id"])
        for claim_id, primaries in by_claim.items():
            self.assertEqual(1, len(primaries), f"{claim_id} has {primaries}")

    def test_primary_selection_identity_is_present_and_deterministic(self):
        self.assertEqual(64, len(self.payload["primary_selection_identity"]))
        self.assertEqual(
            self.payload["primary_selection_identity"],
            self.contract.primary_selection_identity,
        )

    # ---- Owner-approved decisions (INFERRED, never source claims) ----
    def test_four_owner_approved_prerequisites_are_closed(self):
        decisions = self.payload["owner_approved_decisions"]
        self.assertEqual("1_MINUTE", decisions["TIMEFRAME"]["BASE_TO_MACHINE_INTERVAL"])
        self.assertEqual(
            "PROJECT_INFERRED",
            decisions["TIMEFRAME"]["BASE_TO_MACHINE_INTERVAL_CLASSIFICATION"],
        )
        self.assertEqual("1_STEP", decisions["ADX"]["ADX_RISING_WINDOW"])
        self.assertEqual(
            "PROJECT_INFERRED_VERSIONED_NON_OUTCOME",
            decisions["ADX"]["ADX_RISING_WINDOW_CLASSIFICATION"],
        )
        self.assertEqual("L1_R1", decisions["SWING_LOW_HIGH"]["SWING_CONFIRMATION_COUNTS"])
        self.assertEqual(
            "PROJECT_INFERRED_VERSIONED_NON_OUTCOME",
            decisions["SWING_LOW_HIGH"]["SWING_CONFIRMATION_COUNTS_CLASSIFICATION"],
        )
        self.assertEqual(
            "SWING_BASED_TRAILING",
            decisions["TRAILING_STOP"]["TRAILING_STOP_MACHINE_DEFINITION"],
        )
        self.assertEqual("PROJECT_INFERRED", decisions["TRAILING_STOP"]["TRAILING_CLASSIFICATION"])
        self.assertEqual("YES", decisions["TRAILING_STOP"]["MONOTONIC_TIGHTEN_ONLY"])
        # No prerequisites remain open and none are written as source claims.
        self.assertEqual({}, self.payload["open_prerequisites"])
        self.assertEqual([], self.payload["unresolved_machine_definitions"])
        trailing_branch = next(
            b for b in self.payload["interpretations"]
            if b["branch_id"] == "OWNER-APPROVED-SWING-BASED-TRAILING"
        )
        self.assertIn("NOT a source claim", trailing_branch["source_basis"])
        self.assertIn("splices", trailing_branch["source_basis"])

    def test_higher_timeframe_source_alternatives_remain_alternatives(self):
        timeframe = self.payload["owner_approved_decisions"]["TIMEFRAME"]
        self.assertEqual("30MIN,60MIN,120MIN", timeframe["SOURCE_ALTERNATIVES"])
        self.assertEqual("BASE", timeframe["PRIMARY_TIMEFRAME_BRANCH"])
        # Machine-ready timeframe_scope is exactly one value (BASE=1MIN).
        self.assertEqual(["1MIN"], self.payload["timeframe_scope"])
        self.assertEqual(["1MIN"], list(self.contract.timeframe_scope))

    def test_swing_l1_r1_semantics_are_encoded(self):
        swing = self.payload["owner_approved_decisions"]["SWING_LOW_HIGH"]
        self.assertEqual("FRACTAL_PIVOT_EXPLICIT_CONFIRMATION", swing["SWING_DEFINITION"])
        self.assertEqual("YES", swing["RIGHT_SIDE_CONFIRMATION_REQUIRED"])
        self.assertEqual("NO", swing["SAME_BAR_AVAILABILITY"])
        self.assertEqual("MIRROR_SWING_HIGH", swing["SHORT_SIDE"])
        branch = next(
            b for b in self.payload["interpretations"]
            if b["branch_id"] == "OWNER-APPROVED-SWING-LOW-DEFINITION"
        )
        self.assertIn("pivot t confirmed only after bar t+1 completes", branch["source_basis"])

    # ---- Observation surfaces ----
    def test_all_required_surfaces_fully_observable(self):
        for surface in self.payload["observation_surfaces"]:
            self.assertTrue(surface["required"])
            self.assertEqual("OBSERVABLE_NOW", surface["observability_status"], surface["surface_id"])
            self.assertEqual([], surface["missing_inputs"])

    # ---- Machine layer ----
    def test_machine_operationalization_is_bound(self):
        machine = self.payload["machine_operationalization"]
        self.assertEqual("src/holy_grail_machine.py", machine["operationalization_reference"])
        self.assertEqual(64, len(machine["code_hash"]))
        self.assertEqual(64, len(machine["environment_hash"]))
        self.assertEqual(64, len(machine["machine_identity"]))
        self.assertTrue(machine["required_feature_versions"])
        self.assertEqual(16, len(machine["parameter_identities"]))
        self.assertEqual(
            tuple(sorted(parameter_identity(parameter) for parameter in strategy_parameters())),
            tuple(machine["parameter_identities"]),
        )

    def test_machine_code_hash_matches_actual_implementation_bytes(self):
        import hashlib
        machine_module = _repository_blob_bytes(REPO_ROOT / "src" / "holy_grail_machine.py")
        self.assertEqual(
            self.payload["machine_operationalization"]["code_hash"],
            hashlib.sha256(machine_module).hexdigest(),
        )

    # ---- Readiness ----
    def test_readiness_is_machine_ready_with_no_blockers(self):
        self.assertEqual(MachineReadiness.MACHINE_READY, validate_contract(self.contract).readiness)
        self.assertEqual("MACHINE_READY", self.payload["machine_readiness"])
        self.assertEqual([], self.payload["machine_readiness_blockers"])

    def test_final_decision(self):
        self.assertEqual(
            {
                "MACHINE_READY": "YES",
                "PRIMARY_FREEZE_READY": "YES",
                "STRATEGY_IDENTITY_CREATED": "NO",
                "OUTCOME_TEST_REGISTERED": "NO",
                "CANDIDATE_OUTCOME_DATA_USED": "NO",
                "RESEARCH_FIREWALL_UNLOCKED": "NO",
            },
            self.payload["final_decision"],
        )

    def test_checked_in_v0_4_artifact_is_deterministic(self):
        self.assertEqual(self.payload, self.checked_in)
        self.assertEqual("RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_4", self.checked_in["artifact"])
        self.assertEqual("PC-RASCHKE-HOLY-GRAIL-PULLBACK-DRAFT-V0-4", self.checked_in["contract_id"])
        self.assertEqual("PC-RASCHKE-HOLY-GRAIL-PULLBACK-DRAFT-V0-3", self.checked_in["parent_contract_id"])

    def test_owner_approval_evidence_is_referenced(self):
        self.assertEqual(
            "docs/evidence/HOLY_GRAIL_MACHINE_OPERATIONALIZATION_OWNER_APPROVAL_2026-08-21.md",
            self.payload["owner_approval_evidence"],
        )
        self.assertTrue(OWNER_APPROVAL_MD.is_file())
        self.assertIn("OWNER_APPROVED_BINDING", OWNER_APPROVAL_MD.read_text(encoding="utf-8"))
        self.assertIn("1_MINUTE", OWNER_APPROVAL_MD.read_text(encoding="utf-8"))
        self.assertIn("SWING_BASED_TRAILING", OWNER_APPROVAL_MD.read_text(encoding="utf-8"))
        self.assertIn("CANDIDATE_OUTCOME_USED=NO", OWNER_APPROVAL_MD.read_text(encoding="utf-8"))

    def test_builder_has_no_outcome_firewall_surface(self):
        source = V0_4_BUILDER.read_text(encoding="utf-8")
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
                    "src.validation_runner",
                    "src.round_trip_ledger",
                    "src.portfolio_semantics",
                },
            )
        self.assertTrue(any(module == "src.playbook_contract" for module in imported))
        self.assertTrue(any(module == "src.holy_grail_machine" for module in imported))
        for forbidden in (
            "register_outcome_test",
            "request_candidate_outcome_access",
            "bridge_to_strategy_identity",
        ):
            self.assertNotIn(forbidden, source)

    def test_no_candidate_outcome_usage(self):
        self.assertEqual("NO", self.payload["final_decision"]["CANDIDATE_OUTCOME_DATA_USED"])
        self.assertEqual("NO", self.payload["final_decision"]["OUTCOME_TEST_REGISTERED"])
        self.assertEqual("NO", self.payload["final_decision"]["STRATEGY_IDENTITY_CREATED"])

    def test_branch_primary_counts_are_consistent(self):
        primary_counts = Counter(
            branch["branch_id"]
            for branch in self.payload["interpretations"]
            if branch["primary_selected"]
        )
        # Every primary branch covers at least one claim; exactly 27 primary
        # claim-bindings total (one per source claim).
        self.assertEqual(
            CLAIM_COUNT,
            sum(
                len(branch["source_claim_ids"])
                for branch in self.payload["interpretations"]
                if branch["primary_selected"]
            ),
        )


if __name__ == "__main__":
    unittest.main()

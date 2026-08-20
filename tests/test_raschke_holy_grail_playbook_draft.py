import json
import unittest
from dataclasses import replace
from pathlib import Path

from src.playbook_contract import (
    AmbiguityStatus,
    MachineOperationalization,
    MachineReadiness,
    validate_contract,
)
from tools.build_raschke_holy_grail_playbook_contract_draft import (
    build_contract,
    build_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class RaschkeHolyGrailDraftTests(unittest.TestCase):
    def test_unresolved_semantic_gates_keep_draft_not_machine_ready(self):
        contract = build_contract()
        result = validate_contract(contract)

        self.assertEqual(MachineReadiness.NOT_MACHINE_READY, result.readiness)
        self.assertIsNone(contract.machine)
        self.assertIn("UNRESOLVED_CRITICAL_AMBIGUITY", result.blockers)
        self.assertIn("CLAIM_PRIMARY_MISSING", result.blockers)
        self.assertIn("MULTIPLE_TIMEFRAMES_UNRESOLVED", result.blockers)
        self.assertIn("REQUIRED_INPUT_NOT_FULLY_OBSERVABLE", result.blockers)
        self.assertIn("MACHINE_OPERATIONALIZATION_MISSING", result.blockers)
        self.assertFalse(any(branch.primary_selected for branch in contract.interpretations))

    def test_adding_machine_labels_cannot_bypass_unresolved_semantic_gates(self):
        contract = build_contract()
        attempted_bypass = replace(
            contract,
            ambiguity_status=AmbiguityStatus.RESOLVED,
            machine=MachineOperationalization(
                operationalization_reference="TEST_ONLY_ATTEMPTED_BYPASS",
                code_hash="test-only-code",
                environment_hash="test-only-environment",
                required_feature_versions=(),
                parameter_identities=(),
            ),
        )

        result = validate_contract(attempted_bypass)

        self.assertEqual(MachineReadiness.NOT_MACHINE_READY, result.readiness)
        self.assertIn("CLAIM_PRIMARY_MISSING", result.blockers)
        self.assertIn("REQUIRED_INPUT_NOT_FULLY_OBSERVABLE", result.blockers)
        self.assertIn("MULTIPLE_TIMEFRAMES_UNRESOLVED", result.blockers)

    def test_checked_in_v0_2_artifact_is_deterministic_and_exposes_all_gates(self):
        output_path = (
            REPO_ROOT
            / "docs"
            / "evidence"
            / "RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_2.json"
        )
        checked_in = json.loads(output_path.read_text(encoding="utf-8"))
        payload = build_payload()

        self.assertEqual(payload, checked_in)
        self.assertEqual("NO", payload["final_decision"]["MACHINE_READY"])
        self.assertEqual("NO", payload["final_decision"]["PRIMARY_FREEZE_READY"])
        self.assertEqual(
            [f"FGH-GATE-{number:02d}" for number in range(1, 7)],
            payload["unresolved_owner_gates"],
        )
        self.assertEqual(
            [
                "EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION",
                "NEWLY_FORMED_SWING_LOW_MACHINE_DEFINITION",
                "TRAILING_STOP_MACHINE_DEFINITION",
            ],
            payload["unresolved_machine_definitions"],
        )
        self.assertEqual("NO", payload["final_decision"]["STRATEGY_IDENTITY_CREATED"])
        self.assertEqual("NO", payload["final_decision"]["OUTCOME_TEST_REGISTERED"])
        self.assertEqual("NO", payload["final_decision"]["CANDIDATE_OUTCOME_DATA_USED"])


if __name__ == "__main__":
    unittest.main()

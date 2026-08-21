"""Regression protection for the China-first V0.1 bounded negative selection."""

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = REPO_ROOT / "docs" / "reviews" / "CHINA_FIRST_PLAYBOOK_PROMOTION_WAVE_V0_1.json"


class ChinaFirstPlaybookPromotionWaveV01Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
        self.leads = {lead["lead"]: lead for lead in self.payload["lead_audit"]}

    def test_predeclared_leads_are_exhausted_in_order(self) -> None:
        self.assertEqual(["A_FU_AIMIN", "B_WANG_SHAODUO", "C_ZHANG_YANAN"], self.payload["sequential_stopping"]["order"])
        self.assertEqual("YES", self.payload["sequential_stopping"]["final_stopping_condition_met"])
        self.assertEqual("NONE", self.payload["selected_source"])

    def test_no_lead_is_promoted_without_the_dual_condition(self) -> None:
        self.assertEqual("YES_SOURCE_LEVEL_ONLY", self.leads["A_FU_AIMIN"]["source_dossier_admissible"])
        for lead in self.leads.values():
            self.assertEqual("NO", lead["current_data_compatible_playbook_family_candidate"])

    def test_derivative_material_is_not_upgraded_to_original(self) -> None:
        for lead_name in ("B_WANG_SHAODUO", "C_ZHANG_YANAN"):
            self.assertEqual("NO", self.leads[lead_name]["source_dossier_admissible"])
            self.assertEqual("DERIVATIVE", self.leads[lead_name]["materials"][0]["classification"])

    def test_negative_result_remains_pre_outcome_and_has_no_fake_machine_artifact(self) -> None:
        self.assertEqual("YES", self.payload["no_candidate_outcome_used"])
        self.assertEqual("NOT_AUTHORIZED", self.payload["candidate_outcome_backtest"])
        self.assertIn("PLAYBOOK_CONTRACT", self.payload["artifacts_not_created"])
        self.assertIn("MACHINE_IMPLEMENTATION", self.payload["artifacts_not_created"])
        self.assertIn("STRATEGY_IDENTITY", self.payload["artifacts_not_created"])


if __name__ == "__main__":
    unittest.main()

"""Deterministic source-fidelity regression for the JH-CLM-034-002 smoke finding.

Covers the memory-fidelity repair requirement that the known three-call smoke
misuse (a canonical MANAGEMENT claim used as a PRE_ENTRY_REQUIREMENT) remains
detectable as an evaluator-side source-faithfulness finding, and that the active
prompt tells the trader not to extend a Jianghe claim beyond its supplied
canonical meaning/category.
"""

from __future__ import annotations

import json
from pathlib import Path
import unittest

from src.jianghe_source_fidelity_evaluation import (
    JH_CLM_034_002_FIDELITY_FIXTURE,
    JH_CLM_034_002_SMOKE_FINDING_EVIDENCE,
    JH_CLM_034_002_SMOKE_OBSERVED_USE_CATEGORY,
    SOURCE_FIDELITY_EVALUATOR_VERSION,
    SOURCE_FIDELITY_OK,
    SOURCE_FAITHFULNESS_FINDING,
    SourceClaimFidelityFixture,
    adjudicate_source_fidelity,
    load_source_claim_registry,
)
from src.jianghe_trading_only_prompt import SYSTEM_PROMPT_V0_3, DECISION_PROMPT_V0_3

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = (
    REPO_ROOT
    / "docs/research/jianghe/primary_mapping_draft_v0_1"
    / "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_5.jsonl"
)


class JiangheSourceFidelityRegressionTests(unittest.TestCase):
    def test_fixture_is_grounded_in_canonical_registry(self) -> None:
        registry = load_source_claim_registry(REGISTRY_PATH)
        self.assertIn("JH-CLM-034-002", registry)
        JH_CLM_034_002_FIDELITY_FIXTURE.assert_registry_consistent(registry["JH-CLM-034-002"])
        self.assertEqual(JH_CLM_034_002_FIDELITY_FIXTURE.canonical_category, "MANAGEMENT")

    def test_known_smoke_misuse_classified_as_source_faithfulness_finding(self) -> None:
        finding = adjudicate_source_fidelity(
            JH_CLM_034_002_FIDELITY_FIXTURE,
            observed_use_category=JH_CLM_034_002_SMOKE_OBSERVED_USE_CATEGORY,
            finding_evidence=JH_CLM_034_002_SMOKE_FINDING_EVIDENCE,
        )
        self.assertEqual(finding.finding_type, SOURCE_FAITHFULNESS_FINDING)
        self.assertEqual(finding.claim_id, "JH-CLM-034-002")
        self.assertEqual(finding.canonical_category, "MANAGEMENT")
        self.assertEqual(finding.observed_use_category, "PRE_ENTRY_REQUIREMENT")
        self.assertEqual(finding.fixture_identity, JH_CLM_034_002_FIDELITY_FIXTURE.identity)
        self.assertEqual(finding.source_fidelity_evaluator_version, SOURCE_FIDELITY_EVALUATOR_VERSION)
        # Deterministic identity and JSON-compatible payload.
        self.assertEqual(
            finding.identity,
            adjudicate_source_fidelity(
                JH_CLM_034_002_FIDELITY_FIXTURE,
                observed_use_category=JH_CLM_034_002_SMOKE_OBSERVED_USE_CATEGORY,
                finding_evidence=JH_CLM_034_002_SMOKE_FINDING_EVIDENCE,
            ).identity,
        )
        json.dumps(finding.to_payload(), ensure_ascii=False)

    def test_compliant_canonical_use_is_not_a_finding(self) -> None:
        finding = adjudicate_source_fidelity(
            JH_CLM_034_002_FIDELITY_FIXTURE,
            observed_use_category="MANAGEMENT",
            finding_evidence=(
                "Use stays inside the canonical management meaning: advancing the stop "
                "with a new defensive structure.",
            ),
        )
        self.assertEqual(finding.finding_type, SOURCE_FIDELITY_OK)

    def test_active_prompt_forbids_claim_extension_beyond_canonical_meaning(self) -> None:
        normalized_system = " ".join(SYSTEM_PROMPT_V0_3.split())
        self.assertIn("Never extend a Jianghe claim beyond the meaning and category", normalized_system)
        self.assertIn(
            "Do not convert a management/exit observation into a pre-entry requirement",
            normalized_system,
        )
        normalized_decision = " ".join(DECISION_PROMPT_V0_3.split())
        self.assertIn("Never extend a Jianghe claim beyond its supplied canonical meaning/category", normalized_decision)

    def test_fixture_rejects_registry_mismatch(self) -> None:
        wrong_record = {"claim_id": "JH-CLM-034-002", "claim_category": "ENTRY"}
        with self.assertRaises(ValueError):
            JH_CLM_034_002_FIDELITY_FIXTURE.assert_registry_consistent(wrong_record)

    def test_allowed_categories_must_include_canonical_category(self) -> None:
        with self.assertRaises(ValueError):
            SourceClaimFidelityFixture(
                claim_id="JH-CLM-034-002",
                canonical_category="MANAGEMENT",
                canonical_proposition="p",
                allowed_use_categories=("ENTRY",),
                fixture_id="bad-fixture",
            )


if __name__ == "__main__":
    unittest.main()

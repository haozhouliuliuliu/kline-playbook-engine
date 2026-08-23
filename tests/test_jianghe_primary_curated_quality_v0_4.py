"""江河 PRIMARY V0.4 curated quality repair 回归测试。"""

from __future__ import annotations

import sys
import unittest
from collections import Counter
from copy import deepcopy
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIRECTORY = REPOSITORY_ROOT / "tools"
if str(TOOLS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIRECTORY))

import build_jianghe_primary_claim_mapping_draft_v0_1 as draft_builder
import diagnose_jianghe_primary_curated_quality_v0_4 as quality_diagnostic
import validate_jianghe_primary_claim_mapping_draft_v0_1 as draft_validator


class JianghePrimaryCuratedQualityV04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.curated_path = (
            REPOSITORY_ROOT / draft_builder.DRAFT_DIRECTORY / draft_builder.CURATED_REVIEW_NAME
        )
        cls.curated_records = draft_builder.load_jsonl(cls.curated_path, "V0.4 curated review")
        _, cls.source_records = draft_builder.load_claim_records(REPOSITORY_ROOT)
        cls.curated_by_id = {record["claim_id"]: record for record in cls.curated_records}
        cls.source_by_id = {record["claim_id"]: record for record in cls.source_records}

    def test_v04_uses_new_artifacts_and_preserves_v03_history(self) -> None:
        draft_directory = REPOSITORY_ROOT / draft_builder.DRAFT_DIRECTORY

        self.assertEqual(
            draft_builder.CURATED_REVIEW_NAME,
            "JIANGHE_PRIMARY_CLAIM_LEVEL_CURATED_REVIEW_V0_4_QUALITY_REPAIRED.jsonl",
        )
        self.assertEqual(
            draft_builder.DRAFT_JSONL_NAME,
            "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_4.jsonl",
        )
        self.assertEqual(
            draft_builder.DRAFT_MARKDOWN_NAME,
            "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_4.md",
        )
        self.assertTrue(
            (draft_directory / "JIANGHE_PRIMARY_CLAIM_LEVEL_CURATED_REVIEW_V0_3_IDENTITY_BOUND.jsonl").is_file()
        )
        self.assertTrue(
            (draft_directory / "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_3.jsonl").is_file()
        )
        self.assertTrue(
            (draft_directory / "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_3.md").is_file()
        )

    def test_v04_curated_data_reviews_every_claim_once_with_substantive_fields(self) -> None:
        records = draft_builder.load_jsonl(self.curated_path, "V0.4 curated review")
        _, source_records = draft_builder.load_claim_records(REPOSITORY_ROOT)
        claim_ids = [record["claim_id"] for record in records]

        self.assertEqual(len(records), 352)
        self.assertEqual(len(set(claim_ids)), 352)
        self.assertEqual(claim_ids, sorted(claim_ids))
        self.assertEqual(set(claim_ids), {record["claim_id"] for record in source_records})

        required_fields = {
            "curated_review_version",
            "claim_id",
            "claim_manifest_identity",
            "knowledge_pack_identity",
            "review_basis",
            "claim_specific_reasoning",
            "semantic_interpretation",
            "semantic_boundary",
            "operationalization_interpretation",
            "operational_boundary",
            "authority_links",
            "alternative_analysis",
            "semantic_mode",
            "operationalization_mode",
            "required_source_review",
            "q01_adjudication",
            "pre_freeze_disposition",
            "disposition_reason",
        }
        alternative_statuses: Counter[str] = Counter()
        for record in records:
            claim_id = record["claim_id"]
            self.assertEqual(required_fields.difference(record), set(), claim_id)
            reasoning = record["claim_specific_reasoning"]
            self.assertEqual(
                set(reasoning),
                {
                    "source_says",
                    "source_does_not_say",
                    "supports",
                    "does_not_support",
                },
                claim_id,
            )
            self.assertGreaterEqual(sum(len(value) for value in reasoning.values()), 80, claim_id)
            self.assertGreaterEqual(len(record["semantic_interpretation"]), 8, claim_id)
            self.assertGreaterEqual(len(record["disposition_reason"]), 20, claim_id)
            self.assertEqual(
                set(record["semantic_boundary"]),
                {
                    "source_says",
                    "source_does_not_say",
                    "ai_interpretation_constraint",
                    "why_no_additional_interpretation_is_needed",
                },
                claim_id,
            )
            self.assertEqual(
                set(record["operational_boundary"]),
                {
                    "machine_checkable",
                    "ai_discretion",
                    "governed_observation",
                    "unknown_or_subjective",
                    "future_observation_capability",
                },
                claim_id,
            )
            alternative_statuses[record["alternative_analysis"]["status"]] += 1

        self.assertGreater(alternative_statuses["MATERIAL_ALTERNATIVES_REVIEWED"], 0)
        self.assertGreater(alternative_statuses["NO_MATERIAL_SOURCE_ALTERNATIVE"], 0)

    def test_all_q01_claims_have_evidence_backed_completed_adjudication(self) -> None:
        expected_fragments = {
            "JH-CLM-005-001": "排斥",
            "JH-CLM-020-002": "不是固定止盈",
            "JH-CLM-021-003": "0.5 × REGULAR_POSITION_SIZE",
            "JH-CLM-024-001": "至少四根连续同向",
            "JH-CLM-024-002": "至少三根连续同向回调",
        }
        for claim_id, fragment in expected_fragments.items():
            curated = self.curated_by_id[claim_id]
            source = self.source_by_id[claim_id]
            self.assertEqual(source["review_status"], "SOL_REVIEW_REQUIRED", claim_id)
            self.assertEqual(
                curated["required_source_review"]["original_status"],
                "SOL_REVIEW_REQUIRED",
                claim_id,
            )
            self.assertEqual(
                curated["required_source_review"]["effective_status"],
                "COMPLETED_BY_V0_4_Q01_ADJUDICATION",
                claim_id,
            )
            self.assertEqual(curated["q01_adjudication"]["status"], "COMPLETED", claim_id)
            self.assertIn(fragment, curated["semantic_interpretation"], claim_id)
            self.assertEqual(curated["pre_freeze_disposition"], "READY_FOR_PRIMARY_FREEZE")

    def test_q01_management_correction_preserves_raw_source_metadata(self) -> None:
        claim_id = "JH-CLM-020-002"
        source = self.source_by_id[claim_id]
        curated = self.curated_by_id[claim_id]
        branch = {record["claim_id"]: record for record in draft_builder.build_draft_records()}[
            claim_id
        ]
        self.assertEqual(source["source_exit_or_management_if_explicit"], "案例中固定到 1:1 止盈")
        self.assertEqual(
            branch["source_record_binding"]["source_status"]["review_status"],
            "SOL_REVIEW_REQUIRED",
        )
        self.assertEqual(
            curated["reviewed_source_scopes"]["management_or_exit_scope"],
            "该案例未预设止盈，1:1 仅为当时空间预期",
        )
        self.assertEqual(branch["management_or_exit_scope"], "该案例未预设止盈，1:1 仅为当时空间预期")
        self.assertEqual(len(branch["source_scope_corrections"]), 1)

    def test_no_ready_claim_has_an_unresolved_required_source_review(self) -> None:
        for record in self.curated_records:
            if record["pre_freeze_disposition"] == "READY_FOR_PRIMARY_FREEZE":
                self.assertNotEqual(
                    record["required_source_review"]["effective_status"],
                    "REVIEW_COMPLETE_UNRESOLVED_SOURCE_CONFLICT",
                    record["claim_id"],
                )
        unresolved = self.curated_by_id["JH-CLM-030-001"]
        self.assertEqual(
            unresolved["required_source_review"]["effective_status"],
            "REVIEW_COMPLETE_UNRESOLVED_SOURCE_CONFLICT",
        )
        self.assertEqual(unresolved["pre_freeze_disposition"], "STOP_SOURCE_CONFLICT")

    def test_builder_copies_curated_semantics_without_category_selection(self) -> None:
        curated = deepcopy(self.curated_records[0])
        source = deepcopy(self.source_by_id[curated["claim_id"]])
        curated["semantic_interpretation"] = "测试专用的策展语义，必须由构建器逐字复制。"
        curated["operationalization_interpretation"] = "测试专用操作边界，必须由构建器逐字复制。"
        branch = draft_builder.build_branch_record(curated, source, ["test-evidence"])
        self.assertEqual(branch["selected_interpretation_text"], curated["semantic_interpretation"])
        self.assertEqual(
            branch["operationalization_interpretation"],
            curated["operationalization_interpretation"],
        )
        source["claim_category"] = "TEST_CATEGORY_MUST_NOT_SELECT_SEMANTICS"
        second_branch = draft_builder.build_branch_record(curated, source, ["test-evidence"])
        self.assertEqual(
            second_branch["selected_interpretation_text"], branch["selected_interpretation_text"]
        )
        self.assertEqual(
            second_branch["pre_freeze_disposition"], branch["pre_freeze_disposition"]
        )

    def test_authority_links_are_explicit_curated_data_and_not_guessed(self) -> None:
        branch_by_id = {
            record["claim_id"]: record for record in draft_builder.build_draft_records(REPOSITORY_ROOT)
        }
        linked_unknowns = 0
        linked_contradictions = 0
        for curated in self.curated_records:
            claim_id = curated["claim_id"]
            unknowns = curated["authority_links"]["unknowns"]
            contradictions = curated["authority_links"]["contradictions"]
            linked_unknowns += len(unknowns)
            linked_contradictions += len(contradictions)
            self.assertEqual(branch_by_id[claim_id]["unknown_ids"], [item["id"] for item in unknowns])
            self.assertEqual(
                branch_by_id[claim_id]["contradiction_ids"],
                [item["id"] for item in contradictions],
            )
            for link in [*unknowns, *contradictions]:
                self.assertTrue(link.get("rationale") or link.get("reason"), claim_id)
        self.assertGreater(linked_unknowns, 0)
        self.assertGreater(linked_contradictions, 0)
        validation = draft_validator.validate(REPOSITORY_ROOT)
        self.assertEqual(validation["GUESSED_UNKNOWN"], 0)
        self.assertEqual(validation["SILENT_CONFLICT_RESOLUTION"], 0)

    def test_quality_diagnostic_reports_risks_without_deciding_semantics(self) -> None:
        findings = quality_diagnostic.diagnose(REPOSITORY_ROOT)
        self.assertEqual(findings["TOTAL_RECORDS_SCANNED"], 352)
        self.assertEqual(findings["OLD_TEMPLATE_MARKER_RECORDS"], 0)
        self.assertEqual(findings["SOURCE_WRAPPER_ECHOES"], 0)
        self.assertEqual(findings["BLANKET_ALTERNATIVE_DEFAULTS"], 0)
        self.assertEqual(findings["UNRESOLVED_REVIEW_PLUS_READY"], 0)
        self.assertEqual(findings["MECHANICAL_BUILDER_SEMANTIC_DECIDERS"], 0)
        self.assertEqual(findings["DIAGNOSTIC_ROLE"], "RISK_DETECTION_ONLY_NO_SEMANTIC_DECISION")

    def test_source_text_and_non_final_flags_survive_repeated_byte_identical_builds(self) -> None:
        first_records = draft_builder.build_draft_records(REPOSITORY_ROOT)
        second_records = draft_builder.build_draft_records(REPOSITORY_ROOT)
        self.assertEqual(draft_builder.jsonl_content(first_records), draft_builder.jsonl_content(second_records))
        source_by_id = self.source_by_id
        dispositions = Counter(record["pre_freeze_disposition"] for record in first_records)
        self.assertGreater(dispositions["READY_FOR_PRIMARY_FREEZE"], 0)
        self.assertGreater(sum(value for key, value in dispositions.items() if key.startswith("STOP_")), 0)
        for branch in first_records:
            self.assertEqual(branch["source_meaning"], source_by_id[branch["claim_id"]]["interpretation_text"])
            self.assertIs(branch["primary_semantics_frozen"], False)
            self.assertIs(branch["primary_eligible"], False)


if __name__ == "__main__":
    unittest.main()

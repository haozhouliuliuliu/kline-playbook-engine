"""江河 PRIMARY 逐条语义审查草案 V0.2 回归测试。"""

from __future__ import annotations

import inspect
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIRECTORY = REPOSITORY_ROOT / "tools"
if str(TOOLS_DIRECTORY) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIRECTORY))

import build_jianghe_primary_claim_mapping_draft_v0_1 as draft_builder
import validate_jianghe_primary_claim_mapping_draft_v0_1 as draft_validator


class JianghePrimaryClaimMappingDraftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        _, cls.source_records = draft_builder.load_claim_records(REPOSITORY_ROOT)
        cls.curated_records = draft_builder.load_curated_reviews(REPOSITORY_ROOT)
        cls.draft_records = draft_builder.build_draft_records(REPOSITORY_ROOT)
        cls.source_by_id = {record["claim_id"]: record for record in cls.source_records}
        cls.curated_by_id = {record["claim_id"]: record for record in cls.curated_records}

    def run_command(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, *arguments],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_curated_review_has_exact_unique_352_claim_coverage(self) -> None:
        source_ids = [record["claim_id"] for record in self.source_records]
        curated_ids = [record["claim_id"] for record in self.curated_records]
        self.assertEqual(len(curated_ids), 352)
        self.assertEqual(len(set(curated_ids)), 352)
        self.assertEqual(set(curated_ids), set(source_ids))
        self.assertEqual(curated_ids, sorted(curated_ids))

    def test_generator_contains_no_semantic_category_heuristic(self) -> None:
        generator_source = inspect.getsource(draft_builder)
        forbidden_deciders = (
            "choose_semantic_mode",
            "has_category_token",
            "has_source_ambiguity",
            "has_source_conflict",
            "sanitize_draft_text",
            "UNKNOWN_IDS_BY_CLAIM",
            "CONTRADICTION_IDS_BY_CLAIM",
        )
        for name in forbidden_deciders:
            self.assertNotIn(name, generator_source)
        self.assertIn('curated["semantic_interpretation"]', generator_source)
        self.assertIn('curated["semantic_readiness"]', generator_source)

    def test_source_meaning_anchor_status_and_family_are_unchanged(self) -> None:
        for curated in self.curated_records:
            claim_id = curated["claim_id"]
            expected = draft_builder.source_binding(self.source_by_id[claim_id])
            self.assertEqual(curated["source_meaning"], expected["source_meaning"], claim_id)
            self.assertEqual(curated["source_reference"], expected["source_reference"], claim_id)
            self.assertEqual(curated["source_anchor"], expected["source_anchor"], claim_id)
            self.assertEqual(curated["source_status"], expected["source_status"], claim_id)
            self.assertEqual(curated["family_scope"], expected["family_scope"], claim_id)
            self.assertEqual(curated["known_ambiguity"], expected["known_ambiguity"], claim_id)

    def test_source_pnl_text_is_preserved_not_censored(self) -> None:
        claim_id = "JH-CLM-096-002"
        source_text = self.source_by_id[claim_id]["interpretation_text"]
        self.assertIn("P&L", source_text)
        self.assertEqual(self.curated_by_id[claim_id]["source_meaning"], source_text)
        draft_by_id = {record["claim_id"]: record for record in self.draft_records}
        self.assertEqual(draft_by_id[claim_id]["source_meaning"], source_text)

    def test_alternatives_are_explicit_not_blanket_default(self) -> None:
        statuses = Counter(record["alternative_review"]["status"] for record in self.curated_records)
        self.assertGreater(statuses["ALTERNATIVES_REVIEWED"], 0)
        self.assertGreater(statuses["NO_SOURCE_JUSTIFIED_ALTERNATIVE_FOUND"], 0)
        rationales = [record["alternative_review"]["rationale"] for record in self.curated_records]
        self.assertEqual(len(set(rationales)), 352)
        for record in self.curated_records:
            review = record["alternative_review"]
            if review["status"] == "ALTERNATIVES_REVIEWED":
                self.assertTrue(review["alternatives"], record["claim_id"])
            else:
                self.assertEqual(review["alternatives"], [], record["claim_id"])

    def test_semantic_and_identity_readiness_are_separate(self) -> None:
        counts = Counter(record["semantic_readiness"] for record in self.curated_records)
        self.assertEqual(counts["SEMANTICALLY_READY_PRE_IDENTITY"], 340)
        self.assertEqual(counts["STOP_SOURCE_AMBIGUOUS"], 2)
        self.assertEqual(counts["STOP_SOURCE_CONFLICT"], 5)
        self.assertEqual(counts["STOP_OBSERVABILITY_GAP"], 5)
        for record in self.curated_records:
            self.assertEqual(record["identity_readiness"], "PENDING_REBIND")
            expected_disposition = (
                "STOP_IDENTITY_INCOMPLETE"
                if record["semantic_readiness"] == "SEMANTICALLY_READY_PRE_IDENTITY"
                else record["semantic_readiness"]
            )
            self.assertEqual(record["pre_freeze_disposition"], expected_disposition)

    def test_unknown_links_exist_in_authority_and_match_source_reference(self) -> None:
        unknown_rows = draft_validator.load_register_rows(
            REPOSITORY_ROOT / draft_validator.UNKNOWN_REGISTER_PATH, "JH-UNK-"
        )
        for record in self.curated_records:
            ordinal = draft_builder.require_source_ordinal(
                self.source_by_id[record["claim_id"]]["source_ordinal"]
            )
            for link in record["authority_links"]["unknowns"]:
                self.assertIn(link["id"], unknown_rows, record["claim_id"])
                self.assertTrue(
                    draft_validator.source_reference_contains(unknown_rows[link["id"]][3], ordinal),
                    f"{record['claim_id']} -> {link['id']}",
                )

    def test_linked_and_source_internal_contradictions_fail_closed(self) -> None:
        contradiction_rows = draft_validator.load_register_rows(
            REPOSITORY_ROOT / draft_validator.CONTRADICTION_REGISTER_PATH, "JH-CON-"
        )
        for record in self.curated_records:
            source = self.source_by_id[record["claim_id"]]
            linked = record["authority_links"]["contradictions"]
            ordinal = draft_builder.require_source_ordinal(source["source_ordinal"])
            for link in linked:
                self.assertIn(link["id"], contradiction_rows, record["claim_id"])
                self.assertTrue(
                    draft_validator.contradiction_row_mentions_source(
                        contradiction_rows[link["id"]], ordinal
                    ),
                    f"{record['claim_id']} -> {link['id']}",
                )
            source_internal = (
                source.get("interpretation_status") == "SOURCE_INTERNAL_CONFLICT"
                or str(source.get("ambiguity_notes", "")).startswith("SOURCE_INTERNAL_")
            )
            if linked or source_internal:
                self.assertEqual(
                    record["semantic_readiness"],
                    "STOP_SOURCE_CONFLICT",
                    record["claim_id"],
                )

    def test_project_authored_surface_has_no_result_fields_or_dependencies(self) -> None:
        for record in self.draft_records:
            self.assertEqual(draft_validator.find_disallowed_field_names(record), [], record["claim_id"])
            project_authored_surface = {
                "semantic_interpretation": record["semantic_interpretation"],
                "operationalization_interpretation": record["operationalization_interpretation"],
                "observability": record["observability"],
                "authority_links": record["authority_links"],
                "alternative_review": record["alternative_review"],
                "review_rationale": record["review_rationale"],
            }
            self.assertEqual(
                draft_validator.find_disallowed_project_terms(project_authored_surface),
                [],
                record["claim_id"],
            )

    def test_identity_remains_pending_and_no_final_branch_identity_exists(self) -> None:
        for record in self.draft_records:
            self.assertIsNone(record["knowledge_pack_identity"], record["claim_id"])
            self.assertEqual(record["identity_binding_status"], "PENDING_REBIND", record["claim_id"])
            self.assertIsNone(record["primary_branch_identity"], record["claim_id"])
            self.assertNotIn(
                draft_builder.HISTORICAL_PRE_HYGIENE_IDENTITY,
                draft_builder.canonical_json(record),
                record["claim_id"],
            )

    def test_draft_is_deterministically_rebuildable(self) -> None:
        first = draft_builder.jsonl_content(draft_builder.build_draft_records(REPOSITORY_ROOT))
        second = draft_builder.jsonl_content(draft_builder.build_draft_records(REPOSITORY_ROOT))
        self.assertEqual(first, second)
        result = self.run_command(
            "tools/build_jianghe_primary_claim_mapping_draft_v0_1.py", "--check"
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_draft_passes_independent_mechanical_validation(self) -> None:
        result = self.run_command("tools/validate_jianghe_primary_claim_mapping_draft_v0_1.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("PRIMARY_MAPPING_SEMANTIC_AUDIT_VALID=YES", result.stdout)
        self.assertIn("CURATED_CLAIMS=352", result.stdout)


if __name__ == "__main__":
    unittest.main()

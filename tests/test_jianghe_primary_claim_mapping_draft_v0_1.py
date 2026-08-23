"""江河 PRIMARY identity-bound pre-freeze branch registry 回归测试。"""

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
        cls.schema = draft_builder.load_preparation_schema(REPOSITORY_ROOT)
        _, cls.source_records = draft_builder.load_claim_records(REPOSITORY_ROOT)
        cls.curated_records = draft_builder.load_curated_reviews(REPOSITORY_ROOT)
        cls.branch_records = draft_builder.build_draft_records(REPOSITORY_ROOT)
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
        branch_ids = [record["claim_id"] for record in self.branch_records]
        self.assertEqual(len(curated_ids), 352)
        self.assertEqual(len(set(curated_ids)), 352)
        self.assertEqual(set(curated_ids), set(source_ids))
        self.assertEqual(curated_ids, sorted(curated_ids))
        self.assertEqual(branch_ids, curated_ids)

    def test_every_branch_satisfies_formal_preparation_schema(self) -> None:
        required_fields = set(self.schema["required_branch_fields"])
        for record in self.branch_records:
            self.assertEqual(required_fields.difference(record), set(), record["claim_id"])

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
        self.assertIn('curated["pre_freeze_disposition"]', generator_source)

    def test_source_meaning_anchor_status_and_family_are_unchanged(self) -> None:
        branch_by_id = {record["claim_id"]: record for record in self.branch_records}
        for curated in self.curated_records:
            claim_id = curated["claim_id"]
            expected = draft_builder.source_binding(self.source_by_id[claim_id])
            branch = branch_by_id[claim_id]
            self.assertEqual(curated["source_meaning"], expected["source_meaning"], claim_id)
            self.assertEqual(curated["source_reference"], expected["source_reference"], claim_id)
            self.assertEqual(curated["source_anchor"], expected["source_anchor"], claim_id)
            self.assertEqual(curated["source_status"], expected["source_status"], claim_id)
            self.assertEqual(curated["family_scope"], expected["family_scope"], claim_id)
            self.assertEqual(curated["known_ambiguity"], expected["known_ambiguity"], claim_id)
            self.assertEqual(branch["source_meaning"], expected["source_meaning"], claim_id)
            self.assertEqual(branch["source_anchor"], expected["source_anchor"], claim_id)

    def test_source_pnl_text_is_preserved_not_censored(self) -> None:
        claim_id = "JH-CLM-096-002"
        source_text = self.source_by_id[claim_id]["interpretation_text"]
        self.assertIn("P&L", source_text)
        self.assertEqual(self.curated_by_id[claim_id]["source_meaning"], source_text)
        branch_by_id = {record["claim_id"]: record for record in self.branch_records}
        self.assertEqual(branch_by_id[claim_id]["source_meaning"], source_text)

    def test_alternatives_are_explicit_and_none_are_hidden(self) -> None:
        statuses = Counter(record["alternative_review"]["status"] for record in self.curated_records)
        self.assertGreater(statuses["ALTERNATIVES_REVIEWED"], 0)
        self.assertGreater(statuses["NO_SOURCE_JUSTIFIED_ALTERNATIVE_FOUND"], 0)
        rationales = [record["alternative_review"]["rationale"] for record in self.curated_records]
        self.assertEqual(len(set(rationales)), 352)
        for branch in self.branch_records:
            curated = self.curated_by_id[branch["claim_id"]]
            expected_ids = [
                alternative["alternative_id"]
                for alternative in curated["alternative_review"]["alternatives"]
            ]
            self.assertEqual(branch["alternative_interpretation_ids_predeclared"], expected_ids)
            self.assertEqual(branch["alternative_review"], curated["alternative_review"])

    def test_identity_complete_dispositions_preserve_real_stops(self) -> None:
        counts = Counter(record["pre_freeze_disposition"] for record in self.branch_records)
        self.assertEqual(counts["READY_FOR_PRIMARY_FREEZE"], 340)
        self.assertEqual(counts["STOP_SOURCE_AMBIGUOUS"], 2)
        self.assertEqual(counts["STOP_SOURCE_CONFLICT"], 5)
        self.assertEqual(counts["STOP_OBSERVABILITY_GAP"], 5)
        self.assertEqual(counts["STOP_IDENTITY_INCOMPLETE"], 0)

    def test_current_identities_are_bound_on_all_curated_and_branch_records(self) -> None:
        for record in [*self.curated_records, *self.branch_records]:
            self.assertEqual(
                record["knowledge_pack_identity"], draft_builder.KNOWLEDGE_PACK_IDENTITY
            )
            self.assertEqual(
                record["claim_manifest_identity"], draft_builder.CLAIM_MANIFEST_IDENTITY
            )
            self.assertEqual(
                record["identity_binding_status"], draft_builder.IDENTITY_BINDING_STATUS
            )
            serialized = draft_builder.canonical_json(record)
            self.assertNotIn("PENDING_REBIND", serialized)
            self.assertNotIn(draft_builder.HISTORICAL_PRE_HYGIENE_IDENTITY, serialized)

    def test_primary_branch_identities_are_unique_and_deterministic(self) -> None:
        identities = [record["primary_branch_identity"] for record in self.branch_records]
        self.assertEqual(len(identities), 352)
        self.assertEqual(len(set(identities)), 352)
        for record in self.branch_records:
            self.assertEqual(
                record["primary_branch_identity"],
                draft_builder.compute_primary_branch_identity(record),
                record["claim_id"],
            )

    def test_branch_identity_binds_both_current_parent_identities(self) -> None:
        record = dict(self.branch_records[0])
        original_identity = record["primary_branch_identity"]
        record["knowledge_pack_identity"] = "0" * 64
        self.assertNotEqual(draft_builder.compute_primary_branch_identity(record), original_identity)
        record = dict(self.branch_records[0])
        record["claim_manifest_identity"] = "0" * 64
        self.assertNotEqual(draft_builder.compute_primary_branch_identity(record), original_identity)

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
                    record["pre_freeze_disposition"],
                    "STOP_SOURCE_CONFLICT",
                    record["claim_id"],
                )

    def test_project_authored_surface_has_no_result_fields_or_dependencies(self) -> None:
        for record in self.branch_records:
            self.assertEqual(draft_validator.find_disallowed_field_names(record), [], record["claim_id"])
            curated = self.curated_by_id[record["claim_id"]]
            project_authored_surface = {
                "operationalization_interpretation": record["operationalization_interpretation"],
                "observability": record["observability"],
                "authority_links": curated["authority_links"],
                "alternative_review": record["alternative_review"],
                "review_rationale": curated["review_rationale"],
            }
            self.assertEqual(
                draft_validator.find_disallowed_project_terms(project_authored_surface),
                [],
                record["claim_id"],
            )

    def test_registry_never_claims_primary_freeze_or_eligibility(self) -> None:
        for record in self.branch_records:
            self.assertIs(record["primary_semantics_frozen"], False, record["claim_id"])
            self.assertIs(record["primary_eligible"], False, record["claim_id"])

    def test_registry_is_deterministically_rebuildable(self) -> None:
        first = draft_builder.jsonl_content(draft_builder.build_draft_records(REPOSITORY_ROOT))
        second = draft_builder.jsonl_content(draft_builder.build_draft_records(REPOSITORY_ROOT))
        self.assertEqual(first, second)
        result = self.run_command(
            "tools/build_jianghe_primary_claim_mapping_draft_v0_1.py", "--check"
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_registry_passes_independent_mechanical_validation(self) -> None:
        result = self.run_command("tools/validate_jianghe_primary_claim_mapping_draft_v0_1.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("PRIMARY_MAPPING_IDENTITY_BOUND_VALID=YES", result.stdout)
        self.assertIn("READY_FOR_PRIMARY_FREEZE=340", result.stdout)
        self.assertIn("STOP_IDENTITY_INCOMPLETE=0", result.stdout)
        self.assertIn("CLAIM_LEVEL_RECORDS_REVIEWED=352", result.stdout)
        self.assertIn("OUTCOME_REFERENCES_USED_FOR_BRANCH_SELECTION=0", result.stdout)


if __name__ == "__main__":
    unittest.main()

"""江河 V1.1 material-bound SOURCE_ONLY verification 的回归检查。"""

from __future__ import annotations

import json
import unittest
from hashlib import sha256
from pathlib import Path

from src.jianghe_source_only_verification import (
    FOUNDATION_PATH,
    ROOT,
    SESSION_ID,
    _repository_blob_bytes,
    build_verification_payload,
)


ARTIFACT = ROOT / "docs" / "evidence" / "JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.json"


class JiangheSourceOnlyVerificationTests(unittest.TestCase):
    def test_live_project_session_is_material_bound_and_verified(self):
        payload = build_verification_payload()
        session = payload["session"]
        self.assertEqual(payload["source_only_verified"], "YES")
        self.assertEqual(session["session_id"], SESSION_ID)
        self.assertTrue(session["is_project_issued_verified"])
        self.assertEqual(session["knowledge_pack_identity"], payload["knowledge_pack"]["knowledge_pack_identity"])
        self.assertEqual(session["claim_manifest_identity"], payload["claim_manifest"]["manifest_identity"])
        self.assertEqual(session["case_manifest_identity"], payload["case_manifest"]["manifest_identity"])
        self.assertEqual(payload["source_material_manifest"]["binding_status"], "EXACT_REPOSITORY_ARTIFACT_BYTES_BOUND")

    def test_all_protected_project_surfaces_are_denied_and_audited(self):
        payload = build_verification_payload()
        denials = payload["technical_denials"]
        self.assertEqual(
            [item["requested_surface"] for item in denials],
            [
                "CANDIDATE_OUTCOME_RUNNER",
                "CANDIDATE_PNL",
                "VALIDATION",
                "FINAL",
                "OUTCOME_ARTIFACT",
            ],
        )
        self.assertTrue(all(item["outcome"] == "DENIED" for item in denials))
        self.assertTrue(all(item["reason"] == "SOURCE_ONLY_TECHNICAL_DENIAL" for item in denials))
        self.assertTrue(all(item["opened_artifact"] == "NO" for item in denials))

    def test_v11_claim_case_unknown_and_family_evidence_is_preserved(self):
        payload = build_verification_payload()
        self.assertEqual(payload["claim_manifest"]["claim_record_count"], 352)
        self.assertEqual(payload["claim_manifest"]["unique_claim_id_count"], 352)
        self.assertEqual(payload["claim_manifest"]["claim_statuses"], ["EXPLICIT", "INFERRED", "UNKNOWN"])
        self.assertEqual(payload["case_manifest"]["case_record_count"], 80)
        self.assertEqual(payload["case_manifest"]["unique_case_id_count"], 80)
        self.assertEqual(payload["source_coverage"]["source_total"], 99)
        self.assertEqual(payload["source_coverage"]["accessible_source_count"], 98)
        self.assertEqual(payload["semantic_verification"]["new_claims_created"], 0)
        self.assertEqual(payload["semantic_verification"]["new_cases_created"], 0)
        self.assertEqual(payload["semantic_verification"]["family_consistency"], "PASS__JH_FAMILY_A_B_C_D_ONLY")

    def test_material_hashes_bind_exact_committed_git_blob_bytes(self):
        payload = build_verification_payload()
        for section in ("source_material_manifest", "claim_manifest", "case_manifest"):
            for material in payload[section]["materials"]:
                path = ROOT / material["repository_artifact"]
                blob = _repository_blob_bytes(path)
                self.assertEqual(material["content_sha256"], sha256(blob).hexdigest())
                self.assertEqual(material["byte_size"], len(blob))

    def test_committed_evidence_matches_current_material_bindings(self):
        self.assertTrue(FOUNDATION_PATH.is_file())
        self.assertTrue(ARTIFACT.is_file())
        stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        current = build_verification_payload()
        self.assertEqual(stored["artifact"], current["artifact"])
        self.assertEqual(stored["source_only_verified"], "YES")
        self.assertEqual(stored["primary_eligible"], "NO")
        for key in ("knowledge_pack", "source_material_manifest", "claim_manifest", "case_manifest", "source_coverage"):
            self.assertEqual(stored[key], current[key])
        self.assertEqual(stored["session"]["session_identity"], current["session"]["session_identity"])
        self.assertTrue(stored["session"]["verification_evidence"])


if __name__ == "__main__":
    unittest.main()

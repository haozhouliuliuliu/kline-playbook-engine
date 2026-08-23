"""Pre-live prompt package 的 deterministic identity 与非结果边界测试。"""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import unittest

from src.jianghe_model_provider import PromptArtifact
from src.jianghe_response_normalizer import (
    EVALUATION_EXTRACTOR_IDENTITY,
    NORMALIZER_IDENTITY,
    RESPONSE_SCHEMA_IDENTITY,
)


PACKAGE_PATH = (
    Path(__file__).resolve().parents[1]
    / "docs" / "research" / "jianghe" / "JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_1.json"
)


class JianghePromptPackageTests(unittest.TestCase):
    def test_prompt_package_identities_match_exact_checked_in_content(self):
        package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
        identities = package["identities"]
        self.assertEqual(package["status"], "CANDIDATE_PRE_LIVE_NON_OUTCOME")
        self.assertEqual(package["adoption_status"], "NOT_ADOPTED_FOR_PAID_PROBE")
        self.assertEqual(
            identities["system_prompt_identity"],
            PromptArtifact("SYSTEM", package["system_prompt"]).identity,
        )
        self.assertEqual(
            identities["decision_prompt_identity"],
            PromptArtifact("DECISION", package["decision_prompt"]).identity,
        )
        self.assertEqual(identities["response_schema_identity"], RESPONSE_SCHEMA_IDENTITY)
        self.assertEqual(identities["normalizer_identity"], NORMALIZER_IDENTITY)
        self.assertEqual(
            identities["evaluation_extractor_identity"], EVALUATION_EXTRACTOR_IDENTITY
        )
        context_json = json.dumps(
            package["context_selection"], ensure_ascii=False, separators=(",", ":"), sort_keys=True
        )
        self.assertEqual(
            identities["context_selection_identity"],
            sha256(context_json.encode("utf-8")).hexdigest(),
        )
        package_identity_payload = {
            "package_version": package["package_version"],
            "system_prompt_identity": identities["system_prompt_identity"],
            "decision_prompt_identity": identities["decision_prompt_identity"],
            "response_schema_identity": identities["response_schema_identity"],
            "context_selection_identity": identities["context_selection_identity"],
            "normalizer_identity": identities["normalizer_identity"],
        }
        canonical = json.dumps(
            package_identity_payload,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
        self.assertEqual(
            identities["prompt_package_identity"],
            sha256(canonical.encode("utf-8")).hexdigest(),
        )

    def test_prompt_package_allows_unknown_and_forbids_outcome_access(self):
        package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
        combined = package["system_prompt"] + package["decision_prompt"]
        self.assertIn("UNKNOWN", combined)
        self.assertIn("NO_TRADE", combined)
        self.assertEqual(package["authorization"]["live_calls"], 0)
        self.assertEqual(package["authorization"]["paid_spend"], 0)
        self.assertEqual(package["authorization"]["outcome_access"], "NO")
        self.assertEqual(package["context_selection"]["fixture_answer_access"], "DENIED")
        self.assertEqual(package["context_selection"]["future_data_access"], "DENIED")

    def test_primary_scope_rebound_to_v0_5_not_v0_3(self):
        """V0.5 mechanical rebind: old V0.3 scope/identity is no longer the
        current candidate prompt context authority."""
        package = json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))
        identities = package["identities"]
        # V0.3 旧 scope 字符串不得再作为 current candidate prompt context authority。
        self.assertEqual(
            package["context_selection"]["knowledge_scope"],
            "CURRENT_ACTIVE_JIANGHE_V1_1_PLUS_PRIMARY_REGISTRY_V0_5",
        )
        self.assertNotEqual(
            package["context_selection"]["knowledge_scope"],
            "CURRENT_ACTIVE_JIANGHE_V1_1_PLUS_PRIMARY_REGISTRY_V0_3",
        )
        # V0.3 旧 identity 不得继续作为 current candidate prompt context authority。
        self.assertNotEqual(
            identities["context_selection_identity"],
            "646f8f96335227a08d7560a8e0cc30ec3ad64b18eea390ce9d19957fe025c912",
        )
        self.assertNotEqual(
            identities["prompt_package_identity"],
            "beedb7e8189d0c649b39683d57fec6e8e937c0ac8f3a1b793cf4929df2e88b3b",
        )
        # 受 V0.3 -> V0.5 身份变化影响的身份集合之外的语义内容身份不得漂移。
        self.assertEqual(
            identities["system_prompt_identity"],
            "cc43823730723f2089267f55cd87594ce4a026ded82b8298a913d11aed9e826a",
        )
        self.assertEqual(
            identities["decision_prompt_identity"],
            "95bba6d4d9e3d7152fd234a19501efca0d5bc8439b3a0bb557fb5929b41049d9",
        )
        self.assertEqual(identities["response_schema_identity"], RESPONSE_SCHEMA_IDENTITY)
        self.assertEqual(identities["normalizer_identity"], NORMALIZER_IDENTITY)
        self.assertEqual(
            identities["evaluation_extractor_identity"], EVALUATION_EXTRACTOR_IDENTITY
        )


if __name__ == "__main__":
    unittest.main()

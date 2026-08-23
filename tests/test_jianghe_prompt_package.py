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


if __name__ == "__main__":
    unittest.main()

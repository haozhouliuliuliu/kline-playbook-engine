from __future__ import annotations

import unittest

from src.jianghe_ai_trader import AttentionMode, DecisionAction, Direction, StrategyFamily
from src.jianghe_response_normalizer import RESPONSE_SCHEMA_VERSION
from src.jianghe_trading_only_prompt import (
    DECISION_PROMPT,
    MODEL_COGNITIVE_SCOPE,
    SYSTEM_PROMPT,
    TRADING_ONLY_PROMPT_CONTRACT,
    TradingOnlyPromptContract,
)


class TradingOnlyPromptContractTests(unittest.TestCase):
    def test_scope_is_single_purpose_and_operational_work_is_explicitly_outside_model_job(self) -> None:
        self.assertEqual(MODEL_COGNITIVE_SCOPE, "TRADING_ONLY")
        self.assertIn("single-purpose China-futures trader", SYSTEM_PROMPT)
        for phrase in (
            "when you wake",
            "contract/main-contract mapping",
            "chart construction",
            "API/provider routing",
            "software engineering",
            "broker/account plumbing",
            "project governance",
        ):
            self.assertIn(phrase, SYSTEM_PROMPT)
        self.assertIn("Those are deterministic project responsibilities", SYSTEM_PROMPT)

    def test_prompt_keeps_model_on_trading_evidence_and_unknown_handling(self) -> None:
        normalized_prompt = " ".join(SYSTEM_PROMPT.split())
        for phrase in (
            "current market state across 4H / 1H / 15m / 5m",
            "expected trigger and invalidation",
            "Never seek, infer, invent, or assume future bars",
            "do not invent a system fix and do not guess",
            "declared_unknown",
        ):
            self.assertIn(phrase, normalized_prompt)
        self.assertIn("4H only as background state, key-zone position, and remaining space", normalized_prompt)
        self.assertIn("Do not use or request floating PnL", normalized_prompt)

    def test_decision_prompt_binds_existing_strict_schema_and_enums(self) -> None:
        self.assertIn(RESPONSE_SCHEMA_VERSION, DECISION_PROMPT)
        for field in (
            "schema_version",
            "family",
            "action",
            "direction",
            "attention_mode",
            "decision_state",
            "rationale",
            "declared_unknown",
            "principle_references",
            "source_references",
            "numeric_claims",
        ):
            self.assertIn(f"- {field}", DECISION_PROMPT)
        for enum_type in (StrategyFamily, DecisionAction, Direction, AttentionMode):
            for item in enum_type:
                self.assertIn(item.value, DECISION_PROMPT)
        self.assertIn("No markdown", DECISION_PROMPT)
        self.assertIn("no extra keys", DECISION_PROMPT)

    def test_prompt_identity_changes_when_prompt_text_changes(self) -> None:
        altered = TradingOnlyPromptContract(system_prompt=SYSTEM_PROMPT + "\nEXTRA")
        self.assertNotEqual(altered.identity, TRADING_ONLY_PROMPT_CONTRACT.identity)
        self.assertNotEqual(altered.system_prompt_sha256, TRADING_ONLY_PROMPT_CONTRACT.system_prompt_sha256)
        self.assertEqual(altered.decision_prompt_sha256, TRADING_ONLY_PROMPT_CONTRACT.decision_prompt_sha256)

    def test_default_contract_is_deterministic(self) -> None:
        rebuilt = TradingOnlyPromptContract()
        self.assertEqual(rebuilt.identity, TRADING_ONLY_PROMPT_CONTRACT.identity)
        self.assertEqual(rebuilt.system_prompt_sha256, TRADING_ONLY_PROMPT_CONTRACT.system_prompt_sha256)
        self.assertEqual(rebuilt.decision_prompt_sha256, TRADING_ONLY_PROMPT_CONTRACT.decision_prompt_sha256)


if __name__ == "__main__":
    unittest.main()

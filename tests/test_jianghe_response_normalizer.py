"""江河 runtime response normalizer 的纯离线合同测试。"""

from __future__ import annotations

import json
import unittest

from src.jianghe_ai_trader import AttentionMode, DecisionAction, Direction, StrategyFamily
from src.jianghe_response_normalizer import (
    EVALUATION_EXTRACTOR_IDENTITY,
    EvaluatorSideJudgment,
    NORMALIZER_IDENTITY,
    RESPONSE_SCHEMA_IDENTITY,
    JiangheResponseNormalizer,
    build_neutral_fidelity_adapter_payload,
    build_fidelity_response_payload,
    extract_runtime_fidelity_evidence,
)


def valid_payload() -> dict[str, object]:
    return {
        "schema_version": "JIANGHE_RUNTIME_RESPONSE_V0_1",
        "family": "NONE",
        "action": "WAIT",
        "direction": "NONE",
        "attention_mode": "SCAN",
        "decision_state": "TRIGGER_NOT_READY",
        "rationale": "位置存在，但没有看到来源支持的触发。",
        "declared_unknown": ["低周期主动性不足"],
        "principle_references": ["JH-PRINC-002"],
        "source_references": ["JH-CLAIM-001"],
        "numeric_claims": [
            {"claim": "观察价", "value": "100.5", "unit": "PRICE", "source_reference": None}
        ],
    }


def grounding_corpus() -> tuple[dict[str, object], dict[str, object]]:
    fixture = {
        "fixture_id": "TEST-FIXTURE-BSP003",
        "rubric": {
            "pass_paths": [
                {
                    "name": "grounded-principle",
                    "constraints": [
                        {"type": "principle_acknowledged", "values": ["JH-PRINC-002"]}
                    ],
                }
            ],
            "fail_conditions": [],
        },
    }
    return {"corpus_id": "TEST-CORPUS-BSP003", "fixtures": [fixture]}, fixture


class JiangheResponseNormalizerTests(unittest.TestCase):
    def test_normalizes_only_objective_model_output_with_stable_identity(self):
        raw = json.dumps(valid_payload(), ensure_ascii=False)
        first = JiangheResponseNormalizer().normalize(raw)
        second = JiangheResponseNormalizer().normalize(raw)
        self.assertEqual(first.family, StrategyFamily.NONE)
        self.assertEqual(first.action, DecisionAction.WAIT)
        self.assertEqual(first.direction, Direction.NONE)
        self.assertEqual(first.attention_mode, AttentionMode.SCAN)
        self.assertEqual(first.normalizer_identity, NORMALIZER_IDENTITY)
        self.assertEqual(first.response_schema_identity, RESPONSE_SCHEMA_IDENTITY)
        self.assertEqual(first.identity, second.identity)

    def test_machine_enums_require_exact_values_without_prose_or_normalization(self):
        mutations = (
            ("family", "A because breakout"),
            ("action", "WAIT because trigger is not ready"),
            ("direction", "LONG with confirmation"),
            ("attention_mode", "WATCH pending retest"),
            ("family", "a"),
            ("action", " wait "),
            ("direction", "long"),
            ("attention_mode", "scan"),
        )
        for field_name, value in mutations:
            payload = valid_payload()
            payload[field_name] = value
            with self.subTest(field_name=field_name, value=value):
                with self.assertRaises(ValueError):
                    JiangheResponseNormalizer().normalize(json.dumps(payload, ensure_ascii=False))

    def test_rejects_unknown_self_evaluation_and_outcome_fields_recursively(self):
        for field_name, value in (
            ("unexpected", "x"),
            ("violated_principles", []),
            ("invented_thresholds", []),
            ("metadata", {"pnl": "forbidden"}),
        ):
            payload = valid_payload()
            payload[field_name] = value
            with self.subTest(field_name=field_name):
                with self.assertRaises(ValueError):
                    JiangheResponseNormalizer().normalize(json.dumps(payload, ensure_ascii=False))

    def test_rejects_bool_string_and_number_coercion(self):
        for field_name, value in (
            ("family", True),
            ("declared_unknown", "UNKNOWN"),
            ("numeric_claims", [{"claim": "价", "value": 100.5, "unit": None, "source_reference": None}]),
        ):
            payload = valid_payload()
            payload[field_name] = value
            with self.subTest(field_name=field_name):
                with self.assertRaises(ValueError):
                    JiangheResponseNormalizer().normalize(json.dumps(payload, ensure_ascii=False))

    def test_model_self_report_cannot_supply_fidelity_judgment(self):
        decision = JiangheResponseNormalizer().normalize(
            json.dumps(valid_payload(), ensure_ascii=False)
        )
        evidence = extract_runtime_fidelity_evidence(decision)
        self.assertTrue(evidence.evaluator_judgment_required)
        self.assertFalse(hasattr(evidence, "violated_principles"))
        self.assertFalse(hasattr(evidence, "invented_thresholds"))
        corpus, fixture = grounding_corpus()
        judgment = EvaluatorSideJudgment.from_fixture(
            decision.identity,
            corpus=corpus,
            fixture=fixture,
            principle_adjudications={
                "JH-PRINC-002": {
                    "status": "NOT_EVIDENCED",
                    "evidence": "the rationale does not demonstrate the principle",
                }
            },
            invented_thresholds=("100.5",),
            evaluator_evidence=("normalized rationale and fixture rubric reviewed",),
        )
        adapted = build_neutral_fidelity_adapter_payload(evidence, judgment)
        self.assertEqual(adapted["judgment_source"], "EVALUATOR_SIDE_FIXTURE_CONSTRAINTS")
        self.assertEqual(adapted["invented_thresholds"], ["100.5"])
        self.assertEqual(adapted["principle_references"], ["JH-PRINC-002"])

        scorer_payload = build_fidelity_response_payload(evidence, judgment)
        self.assertEqual(scorer_payload["acknowledged_principles"], [])
        self.assertEqual(scorer_payload["violated_principles"], [])
        self.assertEqual(scorer_payload["invented_thresholds"], ["100.5"])
        self.assertFalse(scorer_payload["outcome_reference"])
        self.assertNotIn("numeric_claims", scorer_payload)
        self.assertEqual(judgment.evaluation_extractor_identity, EVALUATION_EXTRACTOR_IDENTITY)
        self.assertTrue(judgment.grounded)

    def test_accepts_strict_array_shaped_numeric_claims(self):
        raw = json.dumps(valid_payload(), ensure_ascii=False)
        decision = JiangheResponseNormalizer().normalize(raw)
        self.assertEqual(len(decision.numeric_claims), 1)
        claim = decision.numeric_claims[0]
        self.assertEqual(claim.claim, "观察价")
        self.assertEqual(claim.value, "100.5")
        self.assertEqual(claim.unit, "PRICE")
        self.assertIsNone(claim.source_reference)
        # Zero numeric claims must normalize to an empty tuple.
        payload = valid_payload()
        payload["numeric_claims"] = []
        decision = JiangheResponseNormalizer().normalize(json.dumps(payload, ensure_ascii=False))
        self.assertEqual(decision.numeric_claims, ())

    def test_rejects_object_shaped_numeric_claims(self):
        payload = valid_payload()
        payload["numeric_claims"] = {
            "latest_5m_close": 76780,
            "latest_5m_high": 76810,
        }
        with self.assertRaisesRegex(ValueError, "numeric_claims 必须是 JSON 数组"):
            JiangheResponseNormalizer().normalize(json.dumps(payload, ensure_ascii=False))

    def test_rejects_numeric_claim_value_as_json_number(self):
        payload = valid_payload()
        payload["numeric_claims"] = [
            {"claim": "观察价", "value": 100.5, "unit": "PRICE", "source_reference": None}
        ]
        with self.assertRaises(ValueError):
            JiangheResponseNormalizer().normalize(json.dumps(payload, ensure_ascii=False))

    def test_rejects_extra_and_missing_numeric_claim_keys(self):
        extra = valid_payload()
        extra["numeric_claims"] = [
            {"claim": "观察价", "value": "100.5", "unit": "PRICE", "source_reference": None, "extra": "x"}
        ]
        with self.assertRaises(ValueError):
            JiangheResponseNormalizer().normalize(json.dumps(extra, ensure_ascii=False))
        missing = valid_payload()
        missing["numeric_claims"] = [
            {"claim": "观察价", "value": "100.5", "unit": "PRICE"}
        ]
        with self.assertRaises(ValueError):
            JiangheResponseNormalizer().normalize(json.dumps(missing, ensure_ascii=False))

    def test_fidelity_response_payload_requires_evaluator_side_identity_match(self):
        decision = JiangheResponseNormalizer().normalize(
            json.dumps(valid_payload(), ensure_ascii=False)
        )
        evidence = extract_runtime_fidelity_evidence(decision)
        corpus, fixture = grounding_corpus()
        judgment = EvaluatorSideJudgment.from_fixture(
            "other-normalized-decision",
            corpus=corpus,
            fixture=fixture,
            principle_adjudications={
                "JH-PRINC-002": {"status": "NOT_EVIDENCED", "evidence": "not evidenced"}
            },
            evaluator_evidence=("fixture reviewed",),
        )
        with self.assertRaises(ValueError):
            build_fidelity_response_payload(evidence, judgment)

    def test_normalized_identity_changes_with_objective_decision_content(self):
        first_payload = valid_payload()
        changed_payload = valid_payload()
        changed_payload["action"] = "NO_TRADE"
        first = JiangheResponseNormalizer().normalize(json.dumps(first_payload, ensure_ascii=False))
        changed = JiangheResponseNormalizer().normalize(json.dumps(changed_payload, ensure_ascii=False))
        self.assertNotEqual(first.identity, changed.identity)


if __name__ == "__main__":
    unittest.main()

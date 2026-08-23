"""Adversarial regressions for BSP-003, RSP-001 and RSP-002."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import json
from types import SimpleNamespace
import unittest

from src.contract_semantics import PositionDirection
from src.intent import ConflictResolver, IntentAction, StrategyIntent
from src.jianghe_fidelity_scoring import FidelityResponse, evaluate_fixture
from src.jianghe_response_normalizer import (
    EvaluatorSideJudgment,
    JiangheResponseNormalizer,
    build_fidelity_response_payload,
    extract_runtime_fidelity_evidence,
)
from src.shadow_runtime import ShadowRuntime


UTC = timezone.utc


def _runtime_payload(principles: list[str]) -> dict[str, object]:
    return {
        "schema_version": "JIANGHE_RUNTIME_RESPONSE_V0_1",
        "family": "NONE",
        "action": "WAIT",
        "direction": "NONE",
        "attention_mode": "SCAN",
        "decision_state": "TRIGGER_NOT_READY",
        "rationale": "没有足够证据确认触发。",
        "declared_unknown": [],
        "principle_references": principles,
        "source_references": [],
        "numeric_claims": [],
    }


def _fixture() -> tuple[dict[str, object], dict[str, object]]:
    fixture = {
        "fixture_id": "BSP003-ADVERSARIAL",
        "rubric": {
            "pass_paths": [
                {
                    "name": "requires-grounded-principle",
                    "constraints": [
                        {"type": "principle_acknowledged", "values": ["JH-PRINC-002"]}
                    ],
                }
            ],
            "fail_conditions": [],
        },
    }
    return {"corpus_id": "BSP003-CORPUS", "fixtures": [fixture]}, fixture


def _intent(*, quantity: str = "1", reason: str = "same", context: str = "ctx") -> StrategyIntent:
    return StrategyIntent(
        intent_id="same-intent-id",
        strategy_identity_id="strategy-v1",
        instrument="cu",
        concrete_contract_id="cu2403",
        action=IntentAction.OPEN,
        decision_at=datetime(2026, 8, 24, 0, 0, tzinfo=UTC),
        context_identity=context,
        direction=PositionDirection.LONG,
        quantity=Decimal(quantity),
        reason=reason,
    )


class Bsp003GroundedScoringTests(unittest.TestCase):
    def test_model_declaring_principle_cannot_self_award_acknowledgement(self):
        decision = JiangheResponseNormalizer().normalize(
            json.dumps(_runtime_payload(["JH-PRINC-001", "JH-PRINC-002", "JH-PRINC-999"]))
        )
        evidence = extract_runtime_fidelity_evidence(decision)
        corpus, fixture = _fixture()
        judgment = EvaluatorSideJudgment.from_fixture(
            decision.identity,
            corpus=corpus,
            fixture=fixture,
            principle_adjudications={
                "JH-PRINC-002": {
                    "status": "NOT_EVIDENCED",
                    "evidence": "rationale does not substantiate the rubric principle",
                }
            },
            evaluator_evidence=("fixture and normalized rationale reviewed",),
        )
        scorer_payload = build_fidelity_response_payload(evidence, judgment)
        self.assertEqual(evidence.principle_references, ("JH-PRINC-001", "JH-PRINC-002", "JH-PRINC-999"))
        self.assertEqual(scorer_payload["acknowledged_principles"], [])
        response = FidelityResponse(**scorer_payload)
        self.assertEqual(evaluate_fixture(fixture, response).verdict, "FAIL")

    def test_incomplete_or_empty_fixture_adjudication_fails_closed(self):
        decision = JiangheResponseNormalizer().normalize(json.dumps(_runtime_payload(["JH-PRINC-002"])))
        corpus, fixture = _fixture()
        with self.assertRaises(ValueError):
            EvaluatorSideJudgment.from_fixture(
                decision.identity,
                corpus=corpus,
                fixture=fixture,
                principle_adjudications={},
                evaluator_evidence=("reviewed",),
            )
        with self.assertRaises(ValueError):
            EvaluatorSideJudgment.from_fixture(
                decision.identity,
                corpus=corpus,
                fixture=fixture,
                principle_adjudications={
                    "JH-PRINC-002": {"status": "NOT_EVIDENCED", "evidence": "not evidenced"}
                },
                evaluator_evidence=(),
            )

    def test_grounding_identity_binds_fixture_corpus_decision_and_evidence(self):
        decision = JiangheResponseNormalizer().normalize(json.dumps(_runtime_payload(["JH-PRINC-002"])))
        corpus, fixture = _fixture()
        kwargs = dict(
            corpus=corpus,
            fixture=fixture,
            principle_adjudications={
                "JH-PRINC-002": {"status": "ACKNOWLEDGED", "evidence": "explicit rationale evidence"}
            },
            evaluator_evidence=("reviewed exact normalized decision",),
        )
        first = EvaluatorSideJudgment.from_fixture(decision.identity, **kwargs)
        second = EvaluatorSideJudgment.from_fixture(decision.identity, **kwargs)
        self.assertEqual(first.identity, second.identity)
        changed_fixture = dict(fixture)
        changed_fixture["fixture_id"] = "BSP003-ADVERSARIAL-CHANGED"
        changed_corpus = {"corpus_id": "BSP003-CORPUS", "fixtures": [changed_fixture]}
        changed = EvaluatorSideJudgment.from_fixture(
            decision.identity,
            corpus=changed_corpus,
            fixture=changed_fixture,
            principle_adjudications=kwargs["principle_adjudications"],
            evaluator_evidence=kwargs["evaluator_evidence"],
        )
        self.assertNotEqual(first.identity, changed.identity)


class Rsp002IntentIdempotencyTests(unittest.TestCase):
    def test_identical_same_id_collapses_idempotently(self):
        intent = _intent()
        result = ConflictResolver().resolve((intent, intent))
        self.assertEqual(len(result.resolutions), 1)

    def test_same_id_different_content_fails_closed(self):
        for changed in (
            _intent(quantity="2"),
            _intent(reason="different"),
            _intent(context="different-context"),
        ):
            with self.subTest(identity=changed.identity_id):
                with self.assertRaises(ValueError):
                    ConflictResolver().resolve((_intent(), changed))


class Rsp001TradingStateAdmissionTests(unittest.TestCase):
    def _runtime(self, applied: bool, calls: list[str]) -> ShadowRuntime:
        runtime = object.__new__(ShadowRuntime)
        event = object()

        class Broker:
            def drain_events(self):
                calls.append("broker-drain")
                return (event,)

        class State:
            def apply_broker_event(self, value):
                assert value is event
                calls.append("state-admission")
                return SimpleNamespace(applied=applied)

        class Oms:
            def apply_broker_event(self, value):
                assert value is event
                calls.append("oms-side-effect")

        runtime._broker = Broker()
        runtime._state = State()
        runtime._oms = Oms()
        return runtime

    def test_rejected_event_never_mutates_oms(self):
        calls: list[str] = []
        results = self._runtime(False, calls).drain_and_apply_events()
        self.assertEqual(len(results), 1)
        self.assertEqual(calls, ["broker-drain", "state-admission"])

    def test_applied_event_reaches_oms_only_after_state_admission(self):
        calls: list[str] = []
        self._runtime(True, calls).drain_and_apply_events()
        self.assertEqual(calls, ["broker-drain", "state-admission", "oms-side-effect"])


if __name__ == "__main__":
    unittest.main()

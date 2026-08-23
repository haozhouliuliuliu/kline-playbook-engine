from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTENT = ROOT / "src" / "intent.py"
SHADOW = ROOT / "src" / "shadow_runtime.py"
NORMALIZER = ROOT / "src" / "jianghe_response_normalizer.py"
NORMALIZER_TEST = ROOT / "tests" / "test_jianghe_response_normalizer.py"
NEW_TEST = ROOT / "tests" / "test_prespend_missing_repairs.py"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{path}: expected one exact replacement, found {count}: {old[:120]!r}"
        )
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


# RSP-002: identical duplicate ids are idempotent; same id with different content is corruption.
replace_once(
    INTENT,
    '''        seen: set[str] = set()
        unique: list[StrategyIntent] = []
        for intent in ordered:
            if intent.intent_id not in seen:
                unique.append(intent)
                seen.add(intent.intent_id)
''',
    '''        seen: dict[str, str] = {}
        unique: list[StrategyIntent] = []
        for intent in ordered:
            prior_identity = seen.get(intent.intent_id)
            if prior_identity is None:
                unique.append(intent)
                seen[intent.intent_id] = intent.identity_id
                continue
            if prior_identity != intent.identity_id:
                raise ValueError(
                    "same intent_id with different canonical content is not idempotent"
                )
''',
)

# RSP-001: TradingState is the authoritative admission gate before any OMS side effect.
replace_once(
    SHADOW,
    '''        for event in self._broker.drain_events():
            self._oms.apply_broker_event(event)
            results.append(self._state.apply_broker_event(event))
''',
    '''        for event in self._broker.drain_events():
            result = self._state.apply_broker_event(event)
            results.append(result)
            if result.applied:
                self._oms.apply_broker_event(event)
''',
)

# BSP-003: replace caller-supplied positive principle promotion with fixture/corpus-bound adjudication.
old_judgment = '''@dataclass(frozen=True)
class EvaluatorSideJudgment:
    """由 evaluator + fixture 约束产生，绝不从模型 self-report 复制。"""

    normalized_decision_identity: str
    violated_principles: tuple[str, ...]
    invented_thresholds: tuple[str, ...]
    evaluation_extractor_identity: str = EVALUATION_EXTRACTOR_IDENTITY

    def __post_init__(self) -> None:
        _require_text(self.normalized_decision_identity, "normalized_decision_identity")
        if self.evaluation_extractor_identity != EVALUATION_EXTRACTOR_IDENTITY:
            raise ValueError("evaluation_extractor_identity 与当前 evaluator-side extractor 不一致")
        for values, name in (
            (self.violated_principles, "violated_principles"),
            (self.invented_thresholds, "invented_thresholds"),
        ):
            if any(not isinstance(value, str) or not value for value in values):
                raise ValueError(f"{name} 必须去重排序并包含非空字符串")
            if tuple(sorted(set(values))) != values:
                raise ValueError(f"{name} 必须去重排序并包含非空字符串")
'''
new_judgment = '''@dataclass(frozen=True)
class EvaluatorSideJudgment:
    """Fixture/corpus-bound evaluator adjudication; model self-report is never grading authority."""

    normalized_decision_identity: str
    violated_principles: tuple[str, ...]
    invented_thresholds: tuple[str, ...]
    evaluation_extractor_identity: str = EVALUATION_EXTRACTOR_IDENTITY
    acknowledged_principles: tuple[str, ...] = ()
    corpus_id: str | None = None
    corpus_identity: str | None = None
    fixture_id: str | None = None
    fixture_identity: str | None = None
    principle_adjudications: tuple[tuple[str, str, str], ...] = ()
    evaluator_evidence: tuple[str, ...] = ()
    identity: str = field(init=False)

    @classmethod
    def from_fixture(
        cls,
        normalized_decision_identity: str,
        *,
        corpus: Mapping[str, object],
        fixture: Mapping[str, object],
        principle_adjudications: Mapping[str, Mapping[str, str]],
        invented_thresholds: Sequence[str] = (),
        evaluator_evidence: Sequence[str] = (),
    ) -> "EvaluatorSideJudgment":
        if not isinstance(corpus, Mapping) or not isinstance(fixture, Mapping):
            raise TypeError("corpus and fixture must be mappings")
        corpus_id = _require_text(corpus.get("corpus_id"), "corpus.corpus_id")
        fixture_id = _require_text(fixture.get("fixture_id"), "fixture.fixture_id")
        fixtures = corpus.get("fixtures")
        fixture_identity = _hash(fixture)
        if not isinstance(fixtures, list) or not any(
            isinstance(item, Mapping) and _hash(item) == fixture_identity for item in fixtures
        ):
            raise ValueError("fixture is not a member of the bound corpus")

        rubric = fixture.get("rubric")
        if not isinstance(rubric, Mapping):
            raise ValueError("fixture rubric must be a mapping")
        required_principles: set[str] = set()
        for section in ("pass_paths", "fail_conditions"):
            entries = rubric.get(section)
            if not isinstance(entries, list):
                raise ValueError("fixture rubric sections must be lists")
            for entry in entries:
                if not isinstance(entry, Mapping):
                    raise ValueError("fixture rubric entry must be a mapping")
                constraints = entry.get("constraints")
                if not isinstance(constraints, list):
                    raise ValueError("fixture constraints must be a list")
                for constraint in constraints:
                    if not isinstance(constraint, Mapping):
                        raise ValueError("fixture constraint must be a mapping")
                    if constraint.get("type") not in {
                        "principle_acknowledged", "principle_violated"
                    }:
                        continue
                    values = constraint.get("values")
                    if not isinstance(values, list) or any(
                        not isinstance(value, str) or not value for value in values
                    ):
                        raise ValueError("fixture principle constraint values must be strings")
                    required_principles.update(values)

        if set(principle_adjudications) != required_principles:
            raise ValueError(
                "evaluator must explicitly adjudicate every fixture principle and no others"
            )
        normalized_adjudications: list[tuple[str, str, str]] = []
        acknowledged: list[str] = []
        violated: list[str] = []
        for principle in sorted(required_principles):
            raw = principle_adjudications[principle]
            if not isinstance(raw, Mapping) or set(raw) != {"status", "evidence"}:
                raise ValueError("principle adjudication requires status and evidence")
            status = raw["status"]
            evidence = raw["evidence"]
            if status not in {"ACKNOWLEDGED", "VIOLATED", "NOT_EVIDENCED"}:
                raise ValueError("unknown principle adjudication status")
            _require_text(evidence, "principle_adjudication.evidence")
            normalized_adjudications.append((principle, status, evidence))
            if status == "ACKNOWLEDGED":
                acknowledged.append(principle)
            elif status == "VIOLATED":
                violated.append(principle)

        evidence_items = tuple(sorted(set(evaluator_evidence)))
        if not evidence_items or any(
            not isinstance(value, str) or not value.strip() for value in evidence_items
        ):
            raise ValueError("grounded evaluator judgment requires explicit evidence")
        invented = tuple(sorted(set(invented_thresholds)))
        if any(not isinstance(value, str) or not value for value in invented):
            raise ValueError("invented_thresholds must contain non-empty strings")
        return cls(
            normalized_decision_identity=normalized_decision_identity,
            violated_principles=tuple(violated),
            invented_thresholds=invented,
            acknowledged_principles=tuple(acknowledged),
            corpus_id=corpus_id,
            corpus_identity=_hash(corpus),
            fixture_id=fixture_id,
            fixture_identity=fixture_identity,
            principle_adjudications=tuple(normalized_adjudications),
            evaluator_evidence=evidence_items,
        )

    def __post_init__(self) -> None:
        _require_text(self.normalized_decision_identity, "normalized_decision_identity")
        if self.evaluation_extractor_identity != EVALUATION_EXTRACTOR_IDENTITY:
            raise ValueError("evaluation_extractor_identity 与当前 evaluator-side extractor 不一致")
        for values, name in (
            (self.acknowledged_principles, "acknowledged_principles"),
            (self.violated_principles, "violated_principles"),
            (self.invented_thresholds, "invented_thresholds"),
        ):
            if any(not isinstance(value, str) or not value for value in values):
                raise ValueError(f"{name} 必须去重排序并包含非空字符串")
            if tuple(sorted(set(values))) != values:
                raise ValueError(f"{name} 必须去重排序并包含非空字符串")
        if set(self.acknowledged_principles) & set(self.violated_principles):
            raise ValueError("a principle cannot be both acknowledged and violated")

        grounding = (
            self.corpus_id,
            self.corpus_identity,
            self.fixture_id,
            self.fixture_identity,
        )
        any_grounding = any(value is not None for value in grounding)
        all_grounding = all(value is not None for value in grounding)
        if any_grounding and not all_grounding:
            raise ValueError("evaluator judgment grounding must be complete")
        if not all_grounding:
            if self.acknowledged_principles or self.principle_adjudications or self.evaluator_evidence:
                raise ValueError("positive/evidentiary judgment requires fixture/corpus grounding")
        else:
            assert self.corpus_id is not None
            assert self.corpus_identity is not None
            assert self.fixture_id is not None
            assert self.fixture_identity is not None
            _require_text(self.corpus_id, "corpus_id")
            _require_text(self.fixture_id, "fixture_id")
            for value, name in (
                (self.corpus_identity, "corpus_identity"),
                (self.fixture_identity, "fixture_identity"),
            ):
                if len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value):
                    raise ValueError(f"{name} must be lowercase sha256")
            if not self.evaluator_evidence:
                raise ValueError("grounded evaluator judgment requires evidence")
            if tuple(sorted(set(self.evaluator_evidence))) != self.evaluator_evidence:
                raise ValueError("evaluator_evidence must be sorted and unique")
            if any(not isinstance(value, str) or not value.strip() for value in self.evaluator_evidence):
                raise ValueError("evaluator_evidence must contain non-empty strings")
            if tuple(sorted(self.principle_adjudications)) != self.principle_adjudications:
                raise ValueError("principle_adjudications must be sorted")
            if len({item[0] for item in self.principle_adjudications}) != len(
                self.principle_adjudications
            ):
                raise ValueError("principle_adjudications must be unique by principle")
            derived_ack = tuple(
                item[0] for item in self.principle_adjudications if item[1] == "ACKNOWLEDGED"
            )
            derived_viol = tuple(
                item[0] for item in self.principle_adjudications if item[1] == "VIOLATED"
            )
            if derived_ack != self.acknowledged_principles or derived_viol != self.violated_principles:
                raise ValueError("principle verdict sets must be derived from adjudications")
            for principle, status, evidence in self.principle_adjudications:
                _require_text(principle, "principle_adjudication.principle")
                if status not in {"ACKNOWLEDGED", "VIOLATED", "NOT_EVIDENCED"}:
                    raise ValueError("unknown principle adjudication status")
                _require_text(evidence, "principle_adjudication.evidence")

        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "normalized_decision_identity": self.normalized_decision_identity,
                    "evaluation_extractor_identity": self.evaluation_extractor_identity,
                    "acknowledged_principles": self.acknowledged_principles,
                    "violated_principles": self.violated_principles,
                    "invented_thresholds": self.invented_thresholds,
                    "corpus_id": self.corpus_id,
                    "corpus_identity": self.corpus_identity,
                    "fixture_id": self.fixture_id,
                    "fixture_identity": self.fixture_identity,
                    "principle_adjudications": self.principle_adjudications,
                    "evaluator_evidence": self.evaluator_evidence,
                }
            ),
        )

    @property
    def grounded(self) -> bool:
        return all(
            value is not None
            for value in (self.corpus_id, self.corpus_identity, self.fixture_id, self.fixture_identity)
        )
'''
replace_once(NORMALIZER, old_judgment, new_judgment)

replace_once(
    NORMALIZER,
    '''        "violated_principles": list(evaluator_judgment.violated_principles),
        "invented_thresholds": list(evaluator_judgment.invented_thresholds),
        "judgment_source": "EVALUATOR_SIDE_FIXTURE_CONSTRAINTS",
''',
    '''        "acknowledged_principles": list(evaluator_judgment.acknowledged_principles),
        "violated_principles": list(evaluator_judgment.violated_principles),
        "invented_thresholds": list(evaluator_judgment.invented_thresholds),
        "judgment_identity": evaluator_judgment.identity,
        "corpus_identity": evaluator_judgment.corpus_identity,
        "fixture_identity": evaluator_judgment.fixture_identity,
        "judgment_source": "EVALUATOR_SIDE_FIXTURE_CONSTRAINTS",
''',
)
replace_once(
    NORMALIZER,
    '''    if (
        runtime_evidence.evaluation_extractor_identity
        != evaluator_judgment.evaluation_extractor_identity
    ):
        raise ValueError("runtime evidence 与 evaluator judgment 的 extractor identity 不一致")
    return {
''',
    '''    if (
        runtime_evidence.evaluation_extractor_identity
        != evaluator_judgment.evaluation_extractor_identity
    ):
        raise ValueError("runtime evidence 与 evaluator judgment 的 extractor identity 不一致")
    if not evaluator_judgment.grounded:
        raise ValueError("scoring requires fixture/corpus-bound evaluator judgment")
    return {
''',
)
replace_once(
    NORMALIZER,
    '        "acknowledged_principles": list(runtime_evidence.principle_references),\n',
    '        "acknowledged_principles": list(evaluator_judgment.acknowledged_principles),\n',
)

insert_helper = '''

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
'''
replace_once(
    NORMALIZER_TEST,
    '\n\nclass JiangheResponseNormalizerTests(unittest.TestCase):\n',
    insert_helper + '\n\nclass JiangheResponseNormalizerTests(unittest.TestCase):\n',
)
old_test = '''        judgment = EvaluatorSideJudgment(decision.identity, (), ("100.5",))
        adapted = build_neutral_fidelity_adapter_payload(evidence, judgment)
        self.assertEqual(adapted["judgment_source"], "EVALUATOR_SIDE_FIXTURE_CONSTRAINTS")
        self.assertEqual(adapted["invented_thresholds"], ["100.5"])

        scorer_payload = build_fidelity_response_payload(evidence, judgment)
        self.assertEqual(scorer_payload["acknowledged_principles"], ["JH-PRINC-002"])
        self.assertEqual(scorer_payload["violated_principles"], [])
        self.assertEqual(scorer_payload["invented_thresholds"], ["100.5"])
        self.assertFalse(scorer_payload["outcome_reference"])
        self.assertNotIn("numeric_claims", scorer_payload)
        self.assertEqual(judgment.evaluation_extractor_identity, EVALUATION_EXTRACTOR_IDENTITY)
'''
new_test = '''        corpus, fixture = grounding_corpus()
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
'''
replace_once(NORMALIZER_TEST, old_test, new_test)

old_mismatch = '''        with self.assertRaises(ValueError):
            build_fidelity_response_payload(
                evidence,
                EvaluatorSideJudgment("other-normalized-decision", (), ()),
            )
'''
new_mismatch = '''        corpus, fixture = grounding_corpus()
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
'''
replace_once(NORMALIZER_TEST, old_mismatch, new_mismatch)

NEW_TEST.write_text(
    '''"""Adversarial regressions for BSP-003, RSP-001 and RSP-002."""

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
''',
    encoding="utf-8",
    newline="\n",
)

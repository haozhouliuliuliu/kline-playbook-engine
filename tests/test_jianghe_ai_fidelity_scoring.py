"""测试：江河 AI 忠实度夹具语料 V0.1 与评分核心。

只测试合成、无结果的忠实度语义；不读取真实行情、不计算收益。

覆盖：
1. 语料结构校验（schema / 覆盖 / 硬负例 / 无污染 / 锚点）。
2. 评分语义：同一夹具允许多个合理答案都 PASS；反例 FAIL。
3. 每个夹具：合法答案 PASS、违反硬负例 FAIL、引用结果 FAIL。
4. `FidelityResponse.from_decision` 与 `JiangheDecision` 的互操作。
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from src.jianghe_ai_trader import AttentionMode, DecisionAction, Direction, JiangheDecision, StrategyFamily
from src.jianghe_fidelity_scoring import (
    CORPUS_ID,
    CORPUS_PATH,
    FidelityResponse,
    evaluate_corpus,
    evaluate_fixture,
    scan_outcome_contamination,
    validate_corpus,
)

ROOT = Path(__file__).resolve().parents[1]
JH = ROOT / "docs" / "research" / "jianghe"
SALVAGE = JH / "second_pass_salvage"


def load_corpus() -> dict:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def resp(
    *,
    family: str | None = None,
    action: str | None = None,
    direction: str | None = None,
    acknowledged: tuple[str, ...] = (),
    violated: tuple[str, ...] = (),
    declared_unknown: tuple[str, ...] = (),
    invented: tuple[str, ...] = (),
    outcome_reference: bool = False,
) -> FidelityResponse:
    return FidelityResponse(
        family=family, action=action, direction=direction,
        acknowledged_principles=acknowledged, violated_principles=violated,
        declared_unknown=declared_unknown, invented_thresholds=invented,
        outcome_reference=outcome_reference,
    )


class CorpusStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_corpus_id_and_fixture_count(self):
        self.assertEqual(self.corpus["corpus_id"], CORPUS_ID)
        self.assertGreaterEqual(len(self.corpus["fixtures"]), 16)
        self.assertEqual(len({f["fixture_id"] for f in self.corpus["fixtures"]}), len(self.corpus["fixtures"]))

    def test_structural_validation_passes(self):
        errors = validate_corpus(self.corpus)
        self.assertEqual(errors, [])

    def test_coverage_includes_all_families_and_no_trade(self):
        coverage = {f["coverage"] for f in self.corpus["fixtures"]}
        self.assertEqual(coverage, {"A", "B", "C", "D", "NONE"})

    def test_all_required_hard_negatives_are_tagged(self):
        required = {"HN-001", "HN-002", "HN-003", "HN-004", "HN-005", "HN-006", "HN-007", "HN-008", "HN-009"}
        tagged = {tag for f in self.corpus["fixtures"] for tag in f.get("hard_negative_tags", [])}
        self.assertEqual(required - tagged, set())

    def test_no_outcome_contamination_in_graded_content(self):
        hits = scan_outcome_contamination(self.corpus)
        self.assertEqual(hits, [])

    def test_every_fixture_is_self_contained_for_grading(self):
        for fixture in self.corpus["fixtures"]:
            for key in ("fixture_id", "coverage", "source_anchors", "visible_information", "hidden_future_information",
                        "expected", "rubric"):
                self.assertIn(key, fixture, f"{fixture['fixture_id']} 缺少 {key}")
            self.assertTrue(fixture["expected"]["acceptable_ambiguity"], f"{fixture['fixture_id']} 缺少可接受歧义说明")

    def test_anchor_existence_against_v1_1_artifacts(self):
        claim_ids = set()
        for path in sorted(JH.glob("JIANGHE_CLAIM_LEDGER*.jsonl")) + sorted(
            SALVAGE.glob("JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.part*.jsonl")
        ):
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    claim_ids.add(json.loads(line)["claim_id"])
        case_ids = set()
        for path in sorted(JH.glob("JIANGHE_CASE_LIBRARY*.md")) + [JH / "JIANGHE_SECOND_PASS_CASE_LIBRARY_DELTA_V1_1.md"]:
            case_ids.update(re.findall(r"^## (JH-CASE-[A-Z0-9-]+)", path.read_text(encoding="utf-8"), flags=re.MULTILINE))
        unknown_ids = set(re.findall(
            r"\b(JH-UNK-\d{3})\b", (JH / "JIANGHE_UNKNOWN_REGISTER_V1_1.md").read_text(encoding="utf-8")))
        contradiction_ids = set(re.findall(
            r"\b(JH-CON-\d{3})\b", (JH / "JIANGHE_CONTRADICTION_REGISTER_V1_1.md").read_text(encoding="utf-8")))

        registers = {"claims": claim_ids, "cases": case_ids, "unknowns": unknown_ids, "contradictions": contradiction_ids}
        for fixture in self.corpus["fixtures"]:
            anchors = fixture.get("source_anchors", {})
            for category, known in registers.items():
                for anchor in anchors.get(category, []):
                    self.assertIn(anchor, known, f"{fixture['fixture_id']} 锚点 {anchor} 不存在")
            for unknown in fixture["expected"].get("explicit_unknown", []):
                self.assertIn(unknown, unknown_ids, f"{fixture['fixture_id']} UNKNOWN {unknown} 不存在")


class ScoringSemanticsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()
        cls.by_id = {f["fixture_id"]: f for f in cls.corpus["fixtures"]}

    def _score(self, fixture_id: str, response: FidelityResponse):
        return evaluate_fixture(self.by_id[fixture_id], response)

    def test_family_a_wait_and_a_candidate_no_trade_are_both_pass(self):
        # “识别为A并等待确认”
        answer_a = resp(family="A", action="WAIT", acknowledged=("JH-PRINC-002",))
        # “A候选但NO_TRADE，因为触发未完成”
        answer_b = resp(family="A", action="NO_TRADE", acknowledged=("JH-PRINC-015",))
        self.assertTrue(self._score("JH-FIX-A-001", answer_a).passed)
        self.assertTrue(self._score("JH-FIX-A-001", answer_b).passed)

    def test_family_a_engulf_alone_immediate_long_fails(self):
        # 反例：仅看到吞没就直接 LONG
        bad = resp(family="A", action="ENTER", direction="LONG", violated=("JH-PRINC-001", "JH-PRINC-002"))
        score = self._score("JH-FIX-A-001", bad)
        self.assertFalse(score.passed)
        self.assertIn("engulf_or_pattern_alone_immediate_long", score.triggered_failures)

    def test_family_a_countertrend_short_fails(self):
        bad = resp(family="A", action="ENTER", direction="SHORT")
        self.assertFalse(self._score("JH-FIX-A-001", bad).passed)

    def test_family_a_confirmed_entry_pass_and_pattern_alone_fail(self):
        good = resp(family="A", action="ENTER", direction="LONG", acknowledged=("JH-PRINC-015",))
        self.assertTrue(self._score("JH-FIX-A-002", good).passed)
        pattern_alone = resp(family="A", action="ENTER", direction="LONG", violated=("JH-PRINC-001",))
        self.assertFalse(self._score("JH-FIX-A-002", pattern_alone).passed)

    def test_family_a_deep_pullback_no_trade(self):
        good = resp(action="NO_TRADE", acknowledged=("JH-PRINC-010",))
        self.assertTrue(self._score("JH-FIX-A-003", good).passed)
        # 即便说出 A 家族，只要 NO_TRADE 仍通过
        good_a_named = resp(family="A", action="NO_TRADE", acknowledged=("JH-PRINC-001",))
        self.assertTrue(self._score("JH-FIX-A-003", good_a_named).passed)
        self.assertFalse(self._score("JH-FIX-A-003", resp(action="ENTER", direction="LONG")).passed)

    def test_family_b_weakening_not_reversal(self):
        good = resp(action="WAIT", acknowledged=("JH-PRINC-003",))
        self.assertTrue(self._score("JH-FIX-B-001", good).passed)
        short_on_weakening = resp(action="ENTER", direction="SHORT", violated=("JH-PRINC-003",))
        self.assertFalse(self._score("JH-FIX-B-001", short_on_weakening).passed)
        self.assertFalse(self._score("JH-FIX-B-001", resp(family="B", action="ENTER")).passed)

    def test_family_b_takeover_entry_pass(self):
        good = resp(family="B", action="ENTER", direction="SHORT", acknowledged=("JH-PRINC-003",))
        self.assertTrue(self._score("JH-FIX-B-002", good).passed)
        pattern_alone = resp(family="B", action="ENTER", direction="SHORT", violated=("JH-PRINC-001",))
        self.assertFalse(self._score("JH-FIX-B-002", pattern_alone).passed)

    def test_family_b_intact_trend_no_blind_reversal(self):
        good = resp(action="NO_TRADE", acknowledged=("JH-PRINC-017",))
        self.assertTrue(self._score("JH-FIX-B-003", good).passed)
        short_top = resp(action="ENTER", direction="SHORT", violated=("JH-PRINC-017", "JH-PRINC-003"))
        self.assertFalse(self._score("JH-FIX-B-003", short_top).passed)

    def test_family_c_false_breakout_no_trade(self):
        good = resp(action="NO_TRADE", acknowledged=("JH-PRINC-006",))
        self.assertTrue(self._score("JH-FIX-C-001", good).passed)
        long_poke = resp(action="ENTER", direction="LONG", violated=("JH-PRINC-006", "JH-PRINC-013"))
        self.assertFalse(self._score("JH-FIX-C-001", long_poke).passed)
        self.assertFalse(self._score("JH-FIX-C-001", resp(family="C", action="ENTER")).passed)

    def test_family_c_confirmed_breakout_pass(self):
        good = resp(family="C", action="ENTER", direction="LONG", acknowledged=("JH-PRINC-013",))
        self.assertTrue(self._score("JH-FIX-C-002", good).passed)
        self.assertFalse(self._score("JH-FIX-C-002", resp(family="C", action="ENTER", direction="SHORT")).passed)

    def test_family_c_to_a_mechanism_switch(self):
        good = resp(family="A", action="WAIT", acknowledged=("JH-PRINC-016",))
        self.assertTrue(self._score("JH-FIX-C-003", good).passed)
        self.assertFalse(self._score("JH-FIX-C-003", resp(action="ENTER", direction="SHORT")).passed)

    def test_family_d_range_middle_no_trade(self):
        good = resp(action="NO_TRADE", acknowledged=("JH-PRINC-004",))
        self.assertTrue(self._score("JH-FIX-D-001", good).passed)
        middle_swing = resp(action="ENTER", direction="LONG", violated=("JH-PRINC-004",))
        self.assertFalse(self._score("JH-FIX-D-001", middle_swing).passed)
        self.assertFalse(self._score("JH-FIX-D-001", resp(family="D", action="ENTER")).passed)

    def test_family_d_second_push_failure_entry_pass(self):
        good = resp(family="D", action="ENTER", direction="SHORT", acknowledged=("JH-PRINC-014",))
        self.assertTrue(self._score("JH-FIX-D-002", good).passed)
        first_counter = resp(family="D", action="ENTER", direction="SHORT", violated=("JH-PRINC-001",))
        self.assertFalse(self._score("JH-FIX-D-002", first_counter).passed)

    def test_family_d_boundary_arrival_wait(self):
        good = resp(family="D", action="WAIT", acknowledged=("JH-PRINC-002",))
        self.assertTrue(self._score("JH-FIX-D-003", good).passed)
        first_counter_short = resp(action="ENTER", direction="SHORT", violated=("JH-PRINC-002",))
        self.assertFalse(self._score("JH-FIX-D-003", first_counter_short).passed)

    def test_family_d_genuine_breakout_switch_to_c(self):
        good = resp(family="C", action="ENTER", direction="LONG", acknowledged=("JH-PRINC-016",))
        self.assertTrue(self._score("JH-FIX-D-004", good).passed)
        kept_short = resp(action="ENTER", direction="SHORT", violated=("JH-PRINC-016", "JH-PRINC-006"))
        self.assertFalse(self._score("JH-FIX-D-004", kept_short).passed)
        self.assertFalse(self._score("JH-FIX-D-004", resp(family="D", action="ENTER")).passed)

    def test_none_contest_unresolved_wait(self):
        good = resp(action="WAIT", acknowledged=("JH-PRINC-005",))
        self.assertTrue(self._score("JH-FIX-NONE-001", good).passed)
        self.assertFalse(self._score("JH-FIX-NONE-001", resp(action="ENTER", direction="LONG", violated=("JH-PRINC-005",))).passed)

    def test_none_location_without_reaction(self):
        good = resp(action="NO_TRADE", acknowledged=("JH-PRINC-002",))
        self.assertTrue(self._score("JH-FIX-NONE-002", good).passed)
        self.assertFalse(self._score("JH-FIX-NONE-002", resp(action="ENTER", direction="SHORT", violated=("JH-PRINC-002",))).passed)

    def test_none_same_tf_internal_structure(self):
        good = resp(action="NO_TRADE", acknowledged=("JH-PRINC-007",))
        self.assertTrue(self._score("JH-FIX-NONE-003", good).passed)
        internal_entry = resp(action="ENTER", direction="LONG", violated=("JH-PRINC-007",))
        self.assertFalse(self._score("JH-FIX-NONE-003", internal_entry).passed)

    def test_none_long_invalid_not_short_valid(self):
        good = resp(action="NO_TRADE", acknowledged=("JH-PRINC-008",))
        self.assertTrue(self._score("JH-FIX-NONE-004", good).passed)
        flip_short = resp(action="ENTER", direction="SHORT", violated=("JH-PRINC-008", "JH-PRINC-003"))
        self.assertFalse(self._score("JH-FIX-NONE-004", flip_short).passed)
        self.assertFalse(self._score("JH-FIX-NONE-004", resp(action="ENTER", direction="LONG")).passed)

    def test_none_unknown_no_invention(self):
        good = resp(
            action="NO_TRADE",
            acknowledged=("JH-PRINC-009",),
            declared_unknown=("JH-UNK-003",),
        )
        self.assertTrue(self._score("JH-FIX-NONE-005", good).passed)
        invented = resp(
            action="NO_TRADE",
            acknowledged=("JH-PRINC-009",),
            declared_unknown=("JH-UNK-003",),
            invented=("回调深度 0.382",),
        )
        score = self._score("JH-FIX-NONE-005", invented)
        self.assertFalse(score.passed)
        self.assertIn("invented_a_threshold", score.triggered_failures)

    def test_none_stop_out_needs_new_independent_setup(self):
        good = resp(action="NO_TRADE", acknowledged=("JH-PRINC-018",))
        self.assertTrue(self._score("JH-FIX-NONE-006", good).passed)
        self.assertFalse(self._score("JH-FIX-NONE-006", resp(action="ENTER", direction="SHORT", violated=("JH-PRINC-018",))).passed)

    def test_none_bias_is_not_trigger(self):
        good = resp(action="WAIT", acknowledged=("JH-PRINC-002",))
        self.assertTrue(self._score("JH-FIX-NONE-007", good).passed)
        self.assertFalse(self._score("JH-FIX-NONE-007", resp(action="ENTER", direction="SHORT", violated=("JH-PRINC-002",))).passed)

    def test_outcome_reference_is_always_fail(self):
        # 即便结构化答案满足 PASS 路径，引用未来价格/结果也判 FAIL。
        good_but_outcome = resp(
            family="A", action="WAIT", acknowledged=("JH-PRINC-002",), outcome_reference=True,
        )
        self.assertFalse(self._score("JH-FIX-A-001", good_but_outcome).passed)

    def test_corpus_batch_scoring(self):
        responses = {
            "JH-FIX-A-001": resp(family="A", action="WAIT", acknowledged=("JH-PRINC-002",)),
            "JH-FIX-B-001": resp(action="WAIT", acknowledged=("JH-PRINC-003",)),
            "JH-FIX-C-001": resp(action="NO_TRADE", acknowledged=("JH-PRINC-006",)),
            "JH-FIX-D-001": resp(action="NO_TRADE", acknowledged=("JH-PRINC-004",)),
            "JH-FIX-NONE-001": resp(action="WAIT", acknowledged=("JH-PRINC-005",)),
        }
        scores = evaluate_corpus(self.corpus, responses)
        for fixture_id, score in scores.items():
            if fixture_id in responses:
                self.assertTrue(score.passed, f"{fixture_id}: {score.reasons}")
            else:
                self.assertFalse(score.passed)
                self.assertIn("缺少回复记录", score.reasons)


class DecisionInteropTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()
        cls.by_id = {f["fixture_id"]: f for f in cls.corpus["fixtures"]}

    def test_from_decision_maps_janghe_decision_fields(self):
        decision = JiangheDecision(
            attention_mode=AttentionMode.WATCH,
            family=StrategyFamily.A,
            direction=Direction.NONE,
            action=DecisionAction.WAIT,
            uncertainty="触发未完成",
        )
        response = FidelityResponse.from_decision(decision, acknowledged_principles=("JH-PRINC-002",))
        self.assertEqual(response.family, "A")
        self.assertEqual(response.action, "WAIT")
        self.assertEqual(response.direction, None)
        self.assertEqual(response.acknowledged_principles, ("JH-PRINC-002",))
        score = evaluate_fixture(self.by_id["JH-FIX-A-001"], response)
        self.assertTrue(score.passed)


if __name__ == "__main__":
    unittest.main()

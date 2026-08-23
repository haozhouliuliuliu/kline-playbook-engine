"""江河 AI 忠实度评估 harness 的测试。

验证：
- 规范化 response records 可被解析并送入现有 scorer；
- 报告包含要求的全部字段，且行为 fail-closed；
- 不涉及任何 provider / 网络 / outcome 访问。
"""

from __future__ import annotations

import importlib
import inspect
import json
import sys
import tempfile
import unittest
from pathlib import Path

from src.jianghe_fidelity_evaluation import (
    ALLOWED_TRACKS,
    CORPUS_PATH,
    EvaluationRecord,
    evaluate_response_records,
    load_corpus,
    load_response_records,
    parse_record,
    render_report,
)
from src.jianghe_fidelity_scoring import FidelityResponse, evaluate_fixture

ROOT = Path(__file__).resolve().parents[1]


def _response_payload(**kwargs) -> dict:
    defaults = {
        "family": None,
        "action": None,
        "direction": None,
        "acknowledged_principles": [],
        "violated_principles": [],
        "declared_unknown": [],
        "invented_thresholds": [],
        "outcome_reference": False,
        "raw_text": None,
    }
    defaults.update(kwargs)
    return defaults


def _make_record(
    fixture_id: str,
    track: str,
    candidate: str = "candidate-x",
    response: dict | None = None,
    record_id: str | None = None,
    **kwargs,
) -> dict:
    rec = {
        "record_id": record_id or f"{candidate}-{fixture_id}-{track}",
        "candidate_label": candidate,
        "corpus_id": "JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1",
        "fixture_id": fixture_id,
        "track": track,
        "response": response if response is not None else _response_payload(),
    }
    rec.update(kwargs)
    return rec


def _passing_response(fixture_id: str) -> dict:
    """返回若干个已知可 PASS 的 fixture 的 response payload。"""
    mapping = {
        "JH-FIX-A-001": _response_payload(
            family="A", action="WAIT", acknowledged_principles=["JH-PRINC-002", "JH-PRINC-015"]
        ),
        "JH-FIX-A-002": _response_payload(
            family="A",
            action="ENTER",
            direction="LONG",
            acknowledged_principles=["JH-PRINC-015", "JH-PRINC-001"],
        ),
        "JH-FIX-B-001": _response_payload(
            action="WAIT", acknowledged_principles=["JH-PRINC-003", "JH-PRINC-005", "JH-PRINC-008"]
        ),
        "JH-FIX-C-001": _response_payload(
            action="NO_TRADE", acknowledged_principles=["JH-PRINC-006", "JH-PRINC-013"]
        ),
        "JH-FIX-D-001": _response_payload(
            action="NO_TRADE", acknowledged_principles=["JH-PRINC-004", "JH-PRINC-010"]
        ),
        "JH-FIX-NONE-001": _response_payload(
            action="WAIT", acknowledged_principles=["JH-PRINC-005", "JH-PRINC-010"]
        ),
        "JH-FIX-NONE-005": _response_payload(
            action="NO_TRADE",
            acknowledged_principles=["JH-PRINC-009", "JH-PRINC-010"],
            declared_unknown=["JH-UNK-003"],
        ),
    }
    if fixture_id not in mapping:
        raise ValueError(f"test helper 未配置 {fixture_id}")
    return mapping[fixture_id]


class RecordParsingTests(unittest.TestCase):
    def test_parse_valid_record(self):
        rec = _make_record("JH-FIX-A-001", "SEMANTIC", response=_passing_response("JH-FIX-A-001"))
        parsed = parse_record(rec)
        self.assertEqual(parsed.record_id, "candidate-x-JH-FIX-A-001-SEMANTIC")
        self.assertEqual(parsed.track, "SEMANTIC")
        self.assertIsInstance(parsed.response, FidelityResponse)
        self.assertTrue(parsed.call_success)

    def test_invalid_track_raises(self):
        rec = _make_record("JH-FIX-A-001", "UNKNOWN_TRACK")
        with self.assertRaises(ValueError) as ctx:
            parse_record(rec)
        self.assertIn("非法 track", str(ctx.exception))

    def test_malformed_response_raises_on_bad_family(self):
        rec = _make_record("JH-FIX-A-001", "SEMANTIC", response=_response_payload(family="Z"))
        with self.assertRaises(ValueError):
            parse_record(rec)

    def test_outcome_reference_must_be_bool(self):
        rec = _make_record(
            "JH-FIX-A-001", "SEMANTIC", response=_response_payload(outcome_reference="yes")
        )
        with self.assertRaises(ValueError):
            parse_record(rec)


class FileLoadingTests(unittest.TestCase):
    def test_load_json_array(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump([_make_record("JH-FIX-A-001", "SEMANTIC")], f)
            path = Path(f.name)
        try:
            loaded = load_response_records(path)
            self.assertEqual(len(loaded), 1)
        finally:
            path.unlink()

    def test_load_json_single_object(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(_make_record("JH-FIX-A-001", "SEMANTIC"), f)
            path = Path(f.name)
        try:
            loaded = load_response_records(path)
            self.assertEqual(len(loaded), 1)
        finally:
            path.unlink()

    def test_load_jsonl(self):
        recs = [
            _make_record("JH-FIX-A-001", "SEMANTIC"),
            _make_record("JH-FIX-B-001", "SEMANTIC"),
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False, encoding="utf-8") as f:
            for rec in recs:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            path = Path(f.name)
        try:
            loaded = load_response_records(path)
            self.assertEqual(len(loaded), 2)
        finally:
            path.unlink()


class ValidSemanticEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_valid_semantic_records_pass(self):
        fixture_ids = ["JH-FIX-A-001", "JH-FIX-A-002", "JH-FIX-B-001", "JH-FIX-C-001", "JH-FIX-D-001", "JH-FIX-NONE-001"]
        records = [
            _make_record(fid, "SEMANTIC", response=_passing_response(fid))
            for fid in fixture_ids
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["status"], "OK")
        self.assertEqual(report["errors"], [])
        semantic_counts = report["per_track_fixture_counts"]["SEMANTIC"]
        self.assertEqual(semantic_counts["PASS"], len(fixture_ids))
        self.assertEqual(semantic_counts["FAIL"], 0)

    def test_existing_scorer_remains_authority(self):
        """Harness 的 fixture 评结果必须与直接调用 scorer 一致。"""
        fixture = next(f for f in self.corpus["fixtures"] if f["fixture_id"] == "JH-FIX-A-001")
        response = FidelityResponse(
            family="A",
            action="WAIT",
            acknowledged_principles=("JH-PRINC-002", "JH-PRINC-015"),
        )
        direct_score = evaluate_fixture(fixture, response)

        records = [
            _make_record("JH-FIX-A-001", "SEMANTIC", response=_passing_response("JH-FIX-A-001"))
        ]
        report = evaluate_response_records(self.corpus, records)
        detail = report["per_fixture_scores"][0]
        self.assertEqual(detail["verdict"], direct_score.verdict)
        self.assertEqual(detail["satisfied_paths"], list(direct_score.satisfied_paths))
        self.assertEqual(detail["triggered_failures"], list(direct_score.triggered_failures))


class TrackCoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_all_five_track_labels_supported(self):
        fixture_id = "JH-FIX-A-001"
        records = [
            _make_record(fixture_id, track, response=_passing_response(fixture_id))
            for track in ALLOWED_TRACKS
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["status"], "OK")
        self.assertEqual(report["response_total"], len(ALLOWED_TRACKS))
        for track in ALLOWED_TRACKS:
            self.assertEqual(report["track_coverage_counts"][track], 1)
            self.assertEqual(report["per_track_fixture_counts"][track]["PASS"], 1)


class DeterminismTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_report_identity_is_deterministic(self):
        fixture_ids = ["JH-FIX-A-001", "JH-FIX-B-001", "JH-FIX-C-001"]
        records = [
            _make_record(fid, "SEMANTIC", response=_passing_response(fid))
            for fid in fixture_ids
        ]
        report_a = evaluate_response_records(self.corpus, records)
        report_b = evaluate_response_records(self.corpus, records)
        self.assertEqual(render_report(report_a), render_report(report_b))


class FailClosedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_duplicate_candidate_fixture_track_is_error(self):
        fixture_id = "JH-FIX-A-001"
        base = _make_record(fixture_id, "SEMANTIC", response=_passing_response(fixture_id))
        records = [base, base.copy()]
        records[1]["record_id"] = "duplicate-id"
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["status"], "ERROR")
        self.assertTrue(any("重复" in e for e in report["errors"]))
        self.assertIn("duplicate-id", report["duplicate_records"])

    def test_malformed_response_record_is_error(self):
        records = [
            _make_record("JH-FIX-A-001", "SEMANTIC", response=_response_payload(family="INVALID"))
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["status"], "ERROR")
        self.assertTrue(len(report["malformed_response_records"]) > 0)

    def test_unknown_fixture_is_error(self):
        records = [_make_record("JH-FIX-NOT-REAL", "SEMANTIC")]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["status"], "ERROR")
        self.assertTrue(len(report["unknown_fixture_records"]) > 0)

    def test_invalid_track_record_is_error(self):
        records = [_make_record("JH-FIX-A-001", "NOT_A_TRACK")]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["status"], "ERROR")
        self.assertTrue(len(report["invalid_track_records"]) > 0)

    def test_corpus_validation_failure_is_error(self):
        bad_corpus = {
            "corpus_id": "WRONG_ID",
            "fixtures": [],
            "principles": [],
            "hard_negatives": [],
            "unknown_register_ids": [],
        }
        report = evaluate_response_records(bad_corpus, [])
        self.assertEqual(report["status"], "ERROR")
        self.assertTrue(any("corpus_id" in e for e in report["errors"]))


class EvidenceSurvivalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_invented_threshold_survives_in_report(self):
        response = _passing_response("JH-FIX-NONE-005")
        response["invented_thresholds"] = ["回调深度 0.382"]
        records = [_make_record("JH-FIX-NONE-005", "SEMANTIC", response=response)]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(len(report["invented_threshold_flags"]), 1)
        self.assertEqual(
            report["invented_threshold_flags"][0]["invented_thresholds"],
            ["回调深度 0.382"],
        )

    def test_unknown_declaration_survives_in_report(self):
        response = _passing_response("JH-FIX-NONE-005")
        records = [_make_record("JH-FIX-NONE-005", "SEMANTIC", response=response)]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(len(report["unknown_declaration_evidence"]), 1)
        self.assertEqual(
            report["unknown_declaration_evidence"][0]["declared_unknown"],
            ["JH-UNK-003"],
        )

    def test_outcome_reference_violation_is_recorded(self):
        response = _passing_response("JH-FIX-A-001")
        response["outcome_reference"] = True
        records = [_make_record("JH-FIX-A-001", "SEMANTIC", response=response)]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(len(report["outcome_reference_violations"]), 1)
        self.assertEqual(report["per_track_fixture_counts"]["SEMANTIC"]["FAIL"], 1)

    def test_outcome_contamination_in_raw_text_is_recorded(self):
        response = _passing_response("JH-FIX-A-001")
        response["raw_text"] = "这笔交易最终盈利很多。"
        records = [_make_record("JH-FIX-A-001", "SEMANTIC", response=response)]
        report = evaluate_response_records(self.corpus, records)
        raw_text_hits = [
            v for v in report["outcome_reference_violations"] if v.get("source") == "raw_text"
        ]
        self.assertTrue(len(raw_text_hits) > 0)


class MissingTrackReportingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_missing_tracks_reported_per_fixture(self):
        # 只为部分 fixture 提供 SEMANTIC track 记录。
        fixture_ids = ["JH-FIX-A-001", "JH-FIX-B-001"]
        records = [
            _make_record(fid, "SEMANTIC", response=_passing_response(fid))
            for fid in fixture_ids
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["status"], "OK")
        # 其余 fixture 没有任何记录，应进入 missing_response_records。
        self.assertIn("JH-FIX-A-002", report["missing_response_records"])
        # 有记录的 fixture 缺少其余 4 个 track。
        incomplete = {item["fixture_id"]: item["missing_tracks"] for item in report["incomplete_tracks"]}
        self.assertIn("JH-FIX-A-001", incomplete)
        self.assertEqual(set(incomplete["JH-FIX-A-001"]), {"VISUAL", "STRUCTURED", "DUAL_INPUT", "OPERATIONAL_PROVIDER"})

    def test_missing_response_records_listed(self):
        # 只给一个 fixture 记录，其余全部缺失。
        records = [_make_record("JH-FIX-A-001", "SEMANTIC", response=_passing_response("JH-FIX-A-001"))]
        report = evaluate_response_records(self.corpus, records)
        self.assertIn("JH-FIX-B-001", report["missing_response_records"])


class NoProviderNetworkTests(unittest.TestCase):
    def test_harness_does_not_import_network_libraries(self):
        """通过源码检查确认 harness 不引入网络/模型 provider 依赖。"""
        import src.jianghe_fidelity_evaluation as harness

        source = inspect.getsource(harness)
        forbidden = ["import requests", "import urllib", "import openai", "import httpx"]
        for token in forbidden:
            self.assertNotIn(token, source, f"harness 源码不应包含 {token}")

    def test_runner_does_not_import_network_libraries(self):
        import tools.run_jianghe_fidelity_evaluation_v0_1 as runner

        source = inspect.getsource(runner)
        forbidden = ["import requests", "import urllib", "import openai", "import httpx"]
        for token in forbidden:
            self.assertNotIn(token, source, f"runner 源码不应包含 {token}")


if __name__ == "__main__":
    unittest.main()

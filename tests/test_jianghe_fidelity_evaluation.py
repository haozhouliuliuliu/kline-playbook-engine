"""江河 AI 忠实度评估 harness 的测试。

验证（fail-closed）：
- 规范化 response records 可被严格解析（禁止 coercion）并送入现有 scorer；
- 未知 response 字段 / corpus 不匹配 / call_success=False / 证据不完整 /
  outcome contamination / metadata 违规 都使 record 不被 admit，绝不评分；
- 报告包含 processing_status / evidence_completeness / evidence_eligibility
  三态与确定性 report_identity；
- 不涉及任何 provider / 网络 / outcome 访问。
"""

from __future__ import annotations

import hashlib
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
    COMPLETENESS_COMPLETE,
    COMPLETENESS_INCOMPLETE,
    ELIGIBILITY_ELIGIBLE,
    ELIGIBILITY_INELIGIBLE,
    PROCESSING_ERROR,
    PROCESSING_OK,
    EvaluationRecord,
    InputEvidence,
    TRACK_REQUIRED_EVIDENCE,
    evaluate_response_records,
    load_corpus,
    load_response_records,
    parse_input_evidence,
    parse_record,
    render_report,
)
from src.jianghe_fidelity_scoring import FidelityResponse, evaluate_fixture

ROOT = Path(__file__).resolve().parents[1]


def _hex_id(seed: str) -> str:
    """确定性 64 位 sha256 hex，作为测试用 artifact identity。"""
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _input_evidence(track: str, **overrides) -> dict:
    """按 track 提供最小合法 typed input provenance。"""
    base = {
        "SEMANTIC": {
            "prompt_package_identity": _hex_id("prompt-semantic"),
            "evaluation_extractor_identity": _hex_id("eval-extractor-semantic"),
        },
        "VISUAL": {
            "visual_artifact_identity": _hex_id("visual-artifact"),
            "renderer_config_identity": _hex_id("renderer-config"),
        },
        "STRUCTURED": {
            "structured_input_identity": _hex_id("structured-input"),
            "observation_identity": _hex_id("observation-1"),
        },
        "DUAL_INPUT": {
            "visual_artifact_identity": _hex_id("visual-artifact"),
            "renderer_config_identity": _hex_id("renderer-config"),
            "structured_input_identity": _hex_id("structured-input"),
            "observation_identity": _hex_id("observation-1"),
        },
        "OPERATIONAL_PROVIDER": {
            "provider_invocation_identity": _hex_id("provider-invocation"),
            "provider_response_identity": _hex_id("provider-response"),
            "model_provider_identity": _hex_id("model-provider"),
        },
    }
    evidence = dict(base.get(track, {}))
    evidence.update(overrides)
    return evidence


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
    input_evidence: dict | None = None,
    **kwargs,
) -> dict:
    rec = {
        "record_id": (
            record_id if record_id is not None else f"{candidate}-{fixture_id}-{track}"
        ),
        "candidate_label": candidate,
        "corpus_id": "JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1",
        "fixture_id": fixture_id,
        "track": track,
        "response": response if response is not None else _response_payload(),
        "input_evidence": (
            input_evidence if input_evidence is not None else _input_evidence(track)
        ),
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

    def test_missing_optional_response_fields_default_to_empty(self):
        rec = _make_record("JH-FIX-A-001", "SEMANTIC")
        rec["response"] = {"family": "A", "action": "WAIT"}
        parsed = parse_record(rec)
        self.assertEqual(parsed.response.violated_principles, ())
        self.assertEqual(parsed.response.acknowledged_principles, ())
        self.assertEqual(parsed.response.invented_thresholds, ())
        self.assertEqual(parsed.response.declared_unknown, ())


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

    def test_outcome_reference_flag_is_fail_closed(self):
        response = _passing_response("JH-FIX-A-001")
        response["outcome_reference"] = True
        records = [_make_record("JH-FIX-A-001", "SEMANTIC", response=response)]
        report = evaluate_response_records(self.corpus, records)
        # 之前允许 violation 存在但 status=OK / FAIL 评分；现在必须 fail-closed。
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(report["evidence_eligibility"], ELIGIBILITY_INELIGIBLE)
        self.assertEqual(len(report["outcome_contamination_violations"]), 1)
        self.assertEqual(
            report["outcome_contamination_violations"][0]["source"],
            "outcome_reference_flag",
        )
        self.assertEqual(report["admitted_record_total"], 0)
        self.assertEqual(report["per_fixture_scores"], [])
        self.assertEqual(report["per_track_fixture_counts"]["SEMANTIC"]["PASS"], 0)
        self.assertEqual(report["per_track_fixture_counts"]["SEMANTIC"]["FAIL"], 0)

    def test_outcome_contamination_in_raw_text_is_fail_closed(self):
        response = _passing_response("JH-FIX-A-001")
        response["raw_text"] = "这笔交易最终盈利很多。"
        records = [_make_record("JH-FIX-A-001", "SEMANTIC", response=response)]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(report["evidence_eligibility"], ELIGIBILITY_INELIGIBLE)
        raw_text_hits = [
            v
            for v in report["outcome_contamination_violations"]
            if v.get("source") == "raw_text"
        ]
        self.assertTrue(len(raw_text_hits) > 0)
        self.assertEqual(report["admitted_record_total"], 0)
        self.assertEqual(report["per_fixture_scores"], [])


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


class StrictResponseSchemaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_unknown_response_field_is_rejected(self):
        response = _passing_response("JH-FIX-A-001")
        response["future_price"] = "later went up"
        records = [_make_record("JH-FIX-A-001", "SEMANTIC", response=response)]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertTrue(len(report["malformed_response_records"]) > 0)
        self.assertTrue(any("未知字段" in e for e in report["errors"]))

    def test_unknown_response_field_never_scored(self):
        response = _passing_response("JH-FIX-A-001")
        response["extra_field"] = "x"
        records = [_make_record("JH-FIX-A-001", "SEMANTIC", response=response)]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(report["admitted_record_total"], 0)
        self.assertEqual(report["per_fixture_scores"], [])


class CorpusBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_corpus_mismatch_is_rejected(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                corpus_id="SOME_OTHER_CORPUS",
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(report["evidence_eligibility"], ELIGIBILITY_INELIGIBLE)
        self.assertEqual(len(report["corpus_mismatch_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)
        self.assertEqual(report["per_fixture_scores"], [])


class FailedCallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_call_success_false_is_non_scoreable(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                call_success=False,
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["failed_call_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)
        self.assertEqual(report["per_fixture_scores"], [])

    def test_call_success_must_be_real_bool(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                call_success="true",
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertTrue(len(report["malformed_response_records"]) > 0)


class StrictTypeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_record_id_must_be_non_empty_str(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                record_id="",
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)

    def test_negative_latency_is_rejected(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                latency_ms=-5,
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertTrue(len(report["malformed_response_records"]) > 0)

    def test_float_latency_is_rejected(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                latency_ms=1.5,
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)

    def test_latency_bool_is_rejected(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                latency_ms=True,
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)

    def test_no_str_coercion_for_principles(self):
        response = _passing_response("JH-FIX-A-001")
        response["acknowledged_principles"] = [123]
        records = [_make_record("JH-FIX-A-001", "SEMANTIC", response=response)]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)


class TrackProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_visual_without_visual_provenance_is_rejected(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "VISUAL",
                response=_passing_response("JH-FIX-A-001"),
                input_evidence=_input_evidence("SEMANTIC"),
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["provenance_ineligible_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_structured_without_structured_provenance_is_rejected(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "STRUCTURED",
                response=_passing_response("JH-FIX-A-001"),
                input_evidence=_input_evidence("SEMANTIC"),
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["provenance_ineligible_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_semantic_cannot_use_visual_evidence(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                input_evidence=_input_evidence("VISUAL"),
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["provenance_ineligible_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_dual_missing_structured_input_is_rejected(self):
        dual = _input_evidence("DUAL_INPUT")
        dual.pop("structured_input_identity")
        records = [
            _make_record(
                "JH-FIX-A-001",
                "DUAL_INPUT",
                response=_passing_response("JH-FIX-A-001"),
                input_evidence=dual,
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["provenance_ineligible_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_dual_inconsistent_observation_identities_is_rejected(self):
        dual = _input_evidence("DUAL_INPUT")
        dual["structured_observation_identity"] = _hex_id("observation-2")
        records = [
            _make_record(
                "JH-FIX-A-001",
                "DUAL_INPUT",
                response=_passing_response("JH-FIX-A-001"),
                input_evidence=dual,
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["provenance_ineligible_records"]), 1)
        self.assertTrue(any("不一致" in e for e in report["errors"]))

    def test_operational_provider_without_provider_evidence_is_rejected(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "OPERATIONAL_PROVIDER",
                response=_passing_response("JH-FIX-A-001"),
                input_evidence=_input_evidence("SEMANTIC"),
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["provenance_ineligible_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_identity_must_be_64_hex(self):
        bad = _input_evidence("SEMANTIC")
        bad["prompt_package_identity"] = "not-a-sha256"
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                input_evidence=bad,
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertTrue(len(report["malformed_response_records"]) > 0)

    def test_input_evidence_unknown_field_is_rejected(self):
        bad = _input_evidence("SEMANTIC")
        bad["arbitrary_provenance_string"] = _hex_id("x")
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                input_evidence=bad,
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertTrue(len(report["malformed_response_records"]) > 0)


class MetadataGovernanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_metadata_contamination_is_rejected(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                metadata={"probe_session_id": "session-with-胜率-claim"},
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(report["evidence_eligibility"], ELIGIBILITY_INELIGIBLE)
        self.assertEqual(len(report["metadata_violations"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)
        metadata_hits = [
            v
            for v in report["outcome_contamination_violations"]
            if v.get("source") == "metadata"
        ]
        self.assertTrue(len(metadata_hits) > 0)

    def test_metadata_unknown_key_is_rejected(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                metadata={"hidden_outcome_channel": "胜率 0.6"},
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertTrue(len(report["malformed_response_records"]) > 0)

    def test_metadata_non_scalar_is_rejected(self):
        records = [
            _make_record(
                "JH-FIX-A-001",
                "SEMANTIC",
                response=_passing_response("JH-FIX-A-001"),
                metadata={"probe_session_id": {"nested": "object"}},
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertTrue(len(report["malformed_response_records"]) > 0)


class ReportIdentityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def _records(self, response=None):
        fixture_id = "JH-FIX-A-001"
        return [
            _make_record(
                fixture_id,
                "SEMANTIC",
                response=response or _passing_response(fixture_id),
            )
        ]

    def test_report_identity_is_deterministic(self):
        report_a = evaluate_response_records(self.corpus, self._records())
        report_b = evaluate_response_records(self.corpus, self._records())
        self.assertEqual(report_a["report_identity"], report_b["report_identity"])

    def test_report_identity_changes_on_evidence_mutation(self):
        base = evaluate_response_records(self.corpus, self._records())
        mutated = self._records()
        mutated[0]["response"]["raw_text"] = "额外的不同内容。"
        changed = evaluate_response_records(self.corpus, mutated)
        self.assertNotEqual(base["report_identity"], changed["report_identity"])

    def test_report_identity_binds_corpus_and_track_provenance(self):
        base = evaluate_response_records(self.corpus, self._records())
        changed_evidence = self._records()
        changed_evidence[0]["input_evidence"]["prompt_package_identity"] = _hex_id(
            "other-prompt"
        )
        changed = evaluate_response_records(self.corpus, changed_evidence)
        self.assertNotEqual(base["report_identity"], changed["report_identity"])


class ThreeStateSeparationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_full_valid_semantic_run_ok_eligible(self):
        fixture_ids = ["JH-FIX-A-001", "JH-FIX-B-001", "JH-FIX-C-001"]
        records = [
            _make_record(fid, "SEMANTIC", response=_passing_response(fid))
            for fid in fixture_ids
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_OK)
        self.assertEqual(report["evidence_eligibility"], ELIGIBILITY_ELIGIBLE)
        self.assertEqual(report["status"], PROCESSING_OK)

    def test_partial_coverage_is_incomplete_but_ok(self):
        records = [
            _make_record(
                "JH-FIX-A-001", "SEMANTIC", response=_passing_response("JH-FIX-A-001")
            )
        ]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_OK)
        self.assertEqual(report["evidence_completeness"], COMPLETENESS_INCOMPLETE)
        self.assertEqual(report["evidence_eligibility"], ELIGIBILITY_ELIGIBLE)

    def test_contamination_sets_all_states_fail_closed(self):
        response = _passing_response("JH-FIX-A-001")
        response["outcome_reference"] = True
        records = [_make_record("JH-FIX-A-001", "SEMANTIC", response=response)]
        report = evaluate_response_records(self.corpus, records)
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(report["evidence_completeness"], COMPLETENESS_INCOMPLETE)
        self.assertEqual(report["evidence_eligibility"], ELIGIBILITY_INELIGIBLE)


if __name__ == "__main__":
    unittest.main()

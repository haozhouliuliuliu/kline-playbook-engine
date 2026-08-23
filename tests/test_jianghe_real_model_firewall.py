"""Real-model firewall tests：证明 pre-live fidelity 路径在真实模型 probe 前 fail closed。

覆盖（PART 5 / JIANGHE_PRE_LIVE_FIDELITY_GATE_AUDIT_V0_1）：
- fidelity response 未知 outcome 字段 -> rejected；
- raw_text outcome contamination -> rejected；
- metadata contamination -> rejected；
- call_success=False -> NON_SCOREABLE；
- corpus mismatch -> rejected；
- VISUAL 无 visual provenance -> rejected；
- STRUCTURED 无 structured provenance -> rejected；
- DUAL 少任一输入 -> rejected；
- DUAL observation identities 不一致 -> rejected；
- OPERATIONAL_PROVIDER 无 provider evidence -> rejected；
- 不读取 protected candidate/Validation/Final artifact；
- evaluator / renderer 无 network；
- 无 paid/live call。

本测试不打开任何 protected artifact，不发起任何真实模型调用。
"""

from __future__ import annotations

import hashlib
import inspect
import unittest

from src.jianghe_fidelity_evaluation import (
    ELIGIBILITY_INELIGIBLE,
    PROCESSING_ERROR,
    evaluate_response_records,
    load_corpus,
)
import src.jianghe_visual_renderer as visual_module


def _hex_id(seed: str) -> str:
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()


def _response(**kwargs) -> dict:
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


def _evidence(track: str, **overrides) -> dict:
    base = {
        "SEMANTIC": {
            "prompt_package_identity": _hex_id("prompt"),
            "evaluation_extractor_identity": _hex_id("eval"),
        },
        "VISUAL": {
            "visual_artifact_identity": _hex_id("va"),
            "renderer_config_identity": _hex_id("rc"),
        },
        "STRUCTURED": {
            "structured_input_identity": _hex_id("si"),
            "observation_identity": _hex_id("obs1"),
        },
        "DUAL_INPUT": {
            "visual_artifact_identity": _hex_id("va"),
            "renderer_config_identity": _hex_id("rc"),
            "structured_input_identity": _hex_id("si"),
            "observation_identity": _hex_id("obs1"),
        },
        "OPERATIONAL_PROVIDER": {
            "provider_invocation_identity": _hex_id("pi"),
            "provider_response_identity": _hex_id("pr"),
            "model_provider_identity": _hex_id("mp"),
        },
    }
    evidence = dict(base.get(track, {}))
    evidence.update(overrides)
    return evidence


def _record(
    fixture_id: str = "JH-FIX-A-001",
    track: str = "SEMANTIC",
    response: dict | None = None,
    corpus_id: str = "JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1",
    **kwargs,
) -> dict:
    rec = {
        "record_id": f"fw-{fixture_id}-{track}",
        "candidate_label": "candidate-x",
        "corpus_id": corpus_id,
        "fixture_id": fixture_id,
        "track": track,
        "response": response if response is not None else _response(),
        "input_evidence": _evidence(track),
    }
    rec.update(kwargs)
    return rec


class FidelityResponseFirewallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_unknown_outcome_field_rejected(self):
        response = _response()
        response["future_price"] = "went up"
        report = evaluate_response_records(
            self.corpus, [_record("JH-FIX-A-001", "SEMANTIC", response=response)]
        )
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_raw_outcome_contamination_rejected(self):
        response = _response(raw_text="该交易最终盈利了。")
        report = evaluate_response_records(
            self.corpus, [_record("JH-FIX-A-001", "SEMANTIC", response=response)]
        )
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(report["evidence_eligibility"], ELIGIBILITY_INELIGIBLE)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_metadata_contamination_rejected(self):
        report = evaluate_response_records(
            self.corpus,
            [
                _record(
                    "JH-FIX-A-001",
                    "SEMANTIC",
                    metadata={"probe_session_id": "session-胜率-claim"},
                )
            ],
        )
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(report["evidence_eligibility"], ELIGIBILITY_INELIGIBLE)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_call_success_false_is_non_scoreable(self):
        report = evaluate_response_records(
            self.corpus,
            [_record("JH-FIX-A-001", "SEMANTIC", call_success=False)],
        )
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["failed_call_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_corpus_mismatch_rejected(self):
        report = evaluate_response_records(
            self.corpus,
            [_record("JH-FIX-A-001", "SEMANTIC", corpus_id="OTHER_CORPUS")],
        )
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["corpus_mismatch_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)


class TrackProvenanceFirewallTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.corpus = load_corpus()

    def test_visual_without_visual_provenance_rejected(self):
        report = evaluate_response_records(
            self.corpus,
            [_record("JH-FIX-A-001", "VISUAL", input_evidence=_evidence("SEMANTIC"))],
        )
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["provenance_ineligible_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_structured_without_structured_provenance_rejected(self):
        report = evaluate_response_records(
            self.corpus,
            [_record("JH-FIX-A-001", "STRUCTURED", input_evidence=_evidence("SEMANTIC"))],
        )
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["provenance_ineligible_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_dual_missing_either_input_rejected(self):
        ev = _evidence("DUAL_INPUT")
        ev.pop("visual_artifact_identity")
        report = evaluate_response_records(
            self.corpus,
            [_record("JH-FIX-A-001", "DUAL_INPUT", input_evidence=ev)],
        )
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["provenance_ineligible_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_dual_observation_identities_inconsistent_rejected(self):
        ev = _evidence("DUAL_INPUT")
        ev["structured_observation_identity"] = _hex_id("obs2")
        report = evaluate_response_records(
            self.corpus,
            [_record("JH-FIX-A-001", "DUAL_INPUT", input_evidence=ev)],
        )
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["provenance_ineligible_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)

    def test_operational_provider_without_provider_evidence_rejected(self):
        report = evaluate_response_records(
            self.corpus,
            [
                _record(
                    "JH-FIX-A-001",
                    "OPERATIONAL_PROVIDER",
                    input_evidence=_evidence("SEMANTIC"),
                )
            ],
        )
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(len(report["provenance_ineligible_records"]), 1)
        self.assertEqual(report["admitted_record_total"], 0)


class NoProtectedAccessFirewallTests(unittest.TestCase):
    """源码级防火墙：不读取 protected 产物、无网络、无 paid/live 调用。"""

    @staticmethod
    def _sources() -> str:
        import src.jianghe_fidelity_evaluation as ev
        import tools.run_jianghe_fidelity_evaluation_v0_1 as runner

        return (
            inspect.getsource(ev)
            + "\n"
            + inspect.getsource(runner)
            + "\n"
            + inspect.getsource(visual_module)
        )

    def test_no_protected_candidate_validation_final_reads(self):
        source = self._sources()
        # 这些 token 若出现，意味着模块可能把 protected 产物当作数据源读取。
        for token in (
            "candidate_outcome",
            "validation",
            "final_holdout",
            "shadow",
            "broker",
            "real_money",
            "round_trip",
        ):
            self.assertNotIn(token, source.lower(), f"来源不应引用 protected: {token}")

    def test_evaluator_and_renderer_no_network(self):
        source = self._sources()
        for token in ("socket", "urllib", "requests", "urlopen", "httpx",
                      "openai", "anthropic", "http.client"):
            self.assertNotIn(token, source.lower(), f"来源不应含网络依赖: {token}")

    def test_no_random_or_system_clock(self):
        source = self._sources()
        for token in ("random", "uuid", "datetime.now", "datetime.utcnow",
                      "time.time", "time_ns", "monotonic"):
            self.assertNotIn(token, source.lower(), f"来源不应含随机/时钟: {token}")

    def test_no_paid_or_live_call_apis(self):
        source = self._sources()
        for token in ("api_key", "apikey", "authorization", "bearer",
                      "billing", "payment", "credentials"):
            self.assertNotIn(token, source.lower(), f"来源不应含 paid/live 调用: {token}")


if __name__ == "__main__":
    unittest.main()

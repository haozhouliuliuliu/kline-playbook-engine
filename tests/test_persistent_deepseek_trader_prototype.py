from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from src.jianghe_ai_trader import (
    ChartRender,
    Direction,
    JiangheAITraderIdentity,
    JiangheObservation,
    ObservationBar,
    ObservationIdentity,
)
from src.jianghe_canon_retrieval import JiangheCanonRetriever
from src.persistent_deepseek_runtime import (
    ACTIVE_TIMEFRAMES,
    CURRENT_MODEL,
    DeepSeekHarnessRuntimeContract,
    PersistentDeepSeekTraderPrototype,
    ProjectToolRegistry,
    observation_to_context_payload,
)
from src.persistent_trader_store import PersistentTraderStore


SYSTEM_PROMPT = "You are the governed Jianghe DeepSeek futures trader."
DECISION_PROMPT = "Return only the strict Jianghe runtime decision schema."


def _identity(tool_names: tuple[str, ...] = ("jianghe_kline_snapshot",)) -> JiangheAITraderIdentity:
    return JiangheAITraderIdentity(
        knowledge_pack_identity="knowledge-v1",
        primary_branch_registry_identity="primary-v1",
        interpretation_set_identity="interpretation-v1",
        model_provider="deepseek",
        model_id_version=CURRENT_MODEL,
        system_prompt_identity=sha256(SYSTEM_PROMPT.encode()).hexdigest(),
        decision_prompt_identity=sha256(DECISION_PROMPT.encode()).hexdigest(),
        context_selection_policy_identity="bounded-context-v1",
        memory_policy_identity="project-persistent-memory-v1",
        chart_renderer_identity="renderer-v1",
        observation_schema_version="JIANGHE_OBSERVATION_V0_1",
        wake_policy_version="wake-v1",
        decision_schema_version="JIANGHE_RUNTIME_RESPONSE_V0_2",
        runtime_normalizer_identity="normalizer-v1",
        hard_execution_envelope_identity="hard-envelope-v1",
        inference_configuration=(("max_retries", "0"),),
        tool_capability_set=tool_names,
        source_family_scope=("A", "B", "C", "D"),
    )


def _observation() -> JiangheObservation:
    now = datetime(2026, 1, 5, 8, 0, tzinfo=timezone.utc)
    durations = {
        "4H": timedelta(hours=4),
        "1H": timedelta(hours=1),
        "15m": timedelta(minutes=15),
        "5m": timedelta(minutes=5),
    }
    bars = []
    charts = []
    for index, timeframe in enumerate(ACTIVE_TIMEFRAMES):
        duration = durations[timeframe]
        bars.append(
            ObservationBar(
                timeframe=timeframe,
                open_time=now - duration,
                close_time=now,
                available_at=now,
                open_price=str(100 + index),
                high_price=str(102 + index),
                low_price=str(99 + index),
                close_price=str(101 + index),
                volume=str(1000 + index),
                is_closed=True,
            )
        )
        charts.append(
            ChartRender(
                renderer_identity="renderer-v1",
                timeframe=timeframe,
                window_definition="prototype-fixture",
                current_time=now,
                render_content_hash=sha256(f"chart:{timeframe}".encode()).hexdigest(),
                partial_bar_marked=False,
                renderer_config_identity="renderer-config-v1",
                artifact_kind="JIANGHE_VISUAL_OBSERVATION_V0_1",
                mime_type="image/png",
            )
        )
    identity = ObservationIdentity(
        decision_time=now,
        exchange_time=now,
        product="rb",
        concrete_contract="SHFE.rb2605",
        mapping_identity="mapping-v1",
        session_identity="session-v1",
    )
    return JiangheObservation(identity=identity, bars=tuple(bars), charts=tuple(charts))


def _valid_response() -> str:
    return json.dumps(
        {
            "schema_version": "JIANGHE_RUNTIME_RESPONSE_V0_2",
            "family": "NONE",
            "action": "WAIT",
            "direction": "NONE",
            "attention_mode": "SCAN",
            "decision_state": "wait_for_better_location",
            "rationale": "No governed setup is confirmed by the current observation.",
            "declared_unknown": [],
            "principle_references": [],
            "source_references": [],
            "numeric_claims": [],
            "current_market_hypothesis": None,
            "timeframe_trend_view": [],
            "key_location_hypotheses": [],
            "expected_trigger": None,
            "invalidation_hypothesis": None,
            "open_questions": [],
        },
        ensure_ascii=False,
    )


class PersistentDeepSeekTraderPrototypeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        canon_dir = self.root / "docs" / "research" / "jianghe"
        canon_dir.mkdir(parents=True)
        self.canon_path = canon_dir / "JIANGHE_CURRENT_VIEW_V1_1.md"
        self.canon_path.write_text(
            "# Jianghe fixture\n"
            "趋势中的关键位置应等待确认，不因单根K线猜测。\n"
            "UNKNOWN 必须保留为 UNKNOWN，不能强行猜测。\n"
            "突破需要确认，未确认时允许 WAIT。\n",
            encoding="utf-8",
        )
        self.identity = _identity()
        self.db_path = self.root / "state" / "trader.sqlite3"
        self.store = PersistentTraderStore(self.db_path, trader_identity=self.identity.identity)
        self.retriever = JiangheCanonRetriever(
            self.root,
            allowed_paths=("docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md",),
            max_results=3,
            max_chars=1000,
            context_lines=0,
        )
        self.tools = ProjectToolRegistry(self.store)
        self.tools.register(
            "jianghe_kline_snapshot",
            lambda args: {
                "symbol": args["symbol"],
                "timeframe": args.get("timeframe", "5m"),
                "source": "PROJECT_CAUSAL_FIXTURE",
                "close": "3130",
            },
        )
        self.contract = DeepSeekHarnessRuntimeContract.from_prompts(
            system_prompt=SYSTEM_PROMPT,
            decision_prompt=DECISION_PROMPT,
        )
        self.runtime = PersistentDeepSeekTraderPrototype(
            trader_identity=self.identity,
            store=self.store,
            retriever=self.retriever,
            tools=self.tools,
            runtime_contract=self.contract,
        )

    def tearDown(self) -> None:
        self.store.close()
        self.temp.cleanup()

    def test_runtime_contract_is_exact_and_provider_execution_stays_locked(self) -> None:
        payload = self.contract.to_payload()
        self.assertEqual(payload["model_id"], CURRENT_MODEL)
        self.assertEqual(payload["harness_version"], "0.1.1-rc.2")
        self.assertEqual(payload["harness_commit"], "b150a551b8d465e31e418e1b2eaf5e79bbb7d28e")
        self.assertEqual(payload["general_max_retries"], 0)
        self.assertFalse(payload["provider_call_authorized"])
        with self.assertRaises(ValueError):
            DeepSeekHarnessRuntimeContract(
                self.contract.system_prompt_sha256,
                self.contract.decision_prompt_sha256,
                model_id="some-other-model",
            )
        with self.assertRaises(ValueError):
            DeepSeekHarnessRuntimeContract(
                self.contract.system_prompt_sha256,
                self.contract.decision_prompt_sha256,
                general_max_retries=1,
            )
        with self.assertRaises(ValueError):
            DeepSeekHarnessRuntimeContract(
                self.contract.system_prompt_sha256,
                self.contract.decision_prompt_sha256,
                provider_call_authorized=True,
            )
        with self.assertRaises(ValueError):
            self.contract.assert_prompts_unchanged(
                system_prompt=SYSTEM_PROMPT + " mutated",
                decision_prompt=DECISION_PROMPT,
            )
        self.assertFalse(hasattr(self.runtime, "send_model_request"))
        self.assertFalse(hasattr(self.runtime, "call_provider"))

    def test_observation_exposes_exact_four_timeframe_stack_and_chart_provenance(self) -> None:
        observation = _observation()
        payload = observation_to_context_payload(observation)
        self.assertEqual(payload["timeframes"], list(ACTIVE_TIMEFRAMES))
        self.assertEqual(len(payload["charts"]), 4)
        self.assertTrue(all(item["visual_artifact_identity"] for item in payload["charts"]))
        self.assertEqual(
            payload["four_hour_role"],
            "BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY",
        )

    def test_working_memory_survives_process_style_reopen_with_mutation_audit(self) -> None:
        observation = _observation()
        self.runtime.mutate_working_memory(
            field_name="current_market_hypothesis",
            new_value="waiting for confirmed pullback",
            reason="PROTOTYPE_TEST",
            observation_identity=observation.identity.identity,
        )
        self.store.close()
        reopened = PersistentTraderStore(self.db_path, trader_identity=self.identity.identity)
        try:
            memory = reopened.load_working_memory()
            self.assertEqual(memory.current_market_hypothesis, "waiting for confirmed pullback")
            self.assertEqual(len(memory.mutation_history), 1)
            self.assertEqual(memory.mutation_history[0].reason, "PROTOTYPE_TEST")
            self.assertIn("DS_WORKING_MEMORY_MUTATION", [event.event_kind for event in reopened.list_audit()])
        finally:
            reopened.close()
        self.store = PersistentTraderStore(self.db_path, trader_identity=self.identity.identity)

    def test_jianghe_retrieval_is_bounded_read_only_and_attributable(self) -> None:
        hits = self.retriever.search("UNKNOWN")
        self.assertGreaterEqual(len(hits), 1)
        self.assertLessEqual(len(hits), 3)
        self.assertLessEqual(sum(len(hit.excerpt) for hit in hits), 1000)
        hit = hits[0]
        self.assertEqual(hit.document_path, "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md")
        self.assertEqual(hit.document_sha256, sha256(self.canon_path.read_bytes()).hexdigest())
        self.assertGreaterEqual(hit.start_line, 1)
        self.assertEqual(len(hit.retrieval_identity), 64)
        self.assertFalse(hasattr(self.retriever, "write"))
        self.assertFalse(hasattr(self.retriever, "update"))
        with self.assertRaises(ValueError):
            JiangheCanonRetriever(self.root, allowed_paths=("../outside.md",))

    def test_project_kline_tool_is_audited_and_4h_reconciliation_fails_closed(self) -> None:
        result = self.tools.call(
            "jianghe_kline_snapshot",
            {"symbol": "SHFE.rb2605", "timeframe": "5m"},
            observation_identity=_observation().identity.identity,
        )
        self.assertEqual(result["source"], "PROJECT_CAUSAL_FIXTURE")
        kinds = [event.event_kind for event in self.store.list_audit()]
        self.assertEqual(kinds[-2:], ["TOOL_CALL", "TOOL_RESULT"])

        self.tools.register(
            "forbidden_4h_reconciliation",
            lambda _args: {
                "timeframe": "4H",
                "volume_reconciliation": {"component_volume_sum": "123"},
            },
        )
        with self.assertRaises(ValueError):
            self.tools.call("forbidden_4h_reconciliation", {})
        self.assertEqual(self.store.list_audit()[-1].event_kind, "TOOL_ERROR")

    def test_journal_and_hypothesis_memory_are_separate_and_non_executable(self) -> None:
        journal_identity = self.runtime.append_journal(
            entry_id="journal-1",
            body="I may be overweighting the latest bar; re-check source conditions.",
            tags=("reflection",),
        )
        hypothesis_identity = self.runtime.put_hypothesis(
            hypothesis_id="hyp-1",
            statement="A confirmed pullback near a key zone may outperform immediate chase entries.",
            falsifier="Comparable confirmed cases fail to show the claimed conditional difference.",
            evidence_references=("JH-FIXTURE",),
        )
        journal = self.store.list_journal()[0]
        hypothesis = self.store.list_hypotheses()[0]
        self.assertEqual(journal.identity, journal_identity)
        self.assertEqual(hypothesis.identity, hypothesis_identity)
        self.assertFalse(hypothesis.executable_policy)
        self.assertNotEqual(journal.body, hypothesis.statement)
        with self.assertRaises(ValueError):
            self.runtime.put_hypothesis(
                hypothesis_id="hyp-illegal",
                statement="self promote",
                falsifier="none",
                status="PROJECT_VALIDATED_POLICY",
            )

    def test_context_assembles_bounded_semantic_layers_without_policy_leakage(self) -> None:
        self.runtime.append_journal(entry_id="journal-ctx", body="reflection only")
        self.runtime.put_hypothesis(
            hypothesis_id="hyp-ctx",
            statement="candidate only",
            falsifier="counterexample",
        )
        context, hits = self.runtime.assemble_context(
            observation=_observation(),
            retrieval_query="确认",
        )
        self.assertGreaterEqual(len(hits), 1)
        self.assertEqual(context["knowledge"]["project_validated_policy"], [])
        self.assertEqual(
            context["knowledge"]["jianghe_canon"][0]["semantic_class"],
            "JIANGHE_CANON_READ_ONLY_SOURCE_TRUTH",
        )
        self.assertEqual(
            context["ds_journal"][0]["semantic_class"],
            "DS_JOURNAL_REFLECTION_NOT_FACT_OR_POLICY",
        )
        self.assertFalse(context["ds_hypothesis_memory"][0]["executable_policy"])

    def test_model_request_is_fully_reconstructable_and_never_sent(self) -> None:
        request = self.runtime.prepare_model_request(
            observation=_observation(),
            retrieval_query="确认",
            system_prompt=SYSTEM_PROMPT,
            decision_prompt=DECISION_PROMPT,
        )
        events = self.store.audit_for_request(request.request_id)
        self.assertEqual(len(events), 1)
        event = events[0]
        self.assertEqual(event.event_kind, "MODEL_REQUEST_PREPARED_OFFLINE")
        self.assertEqual(event.payload["model"], CURRENT_MODEL)
        self.assertFalse(event.payload["provider_call_authorized"])
        self.assertEqual(event.payload["system_prompt"], SYSTEM_PROMPT)
        self.assertEqual(event.payload["decision_prompt"], DECISION_PROMPT)
        self.assertEqual(event.payload["context_sha256"], request.context_sha256)
        self.assertEqual(event.payload["context"], request.context)
        self.assertEqual(len(event.payload["visual_artifact_identities"]), 4)

    def test_raw_response_and_strict_normalization_are_reconstructable(self) -> None:
        request = self.runtime.prepare_model_request(
            observation=_observation(),
            retrieval_query="UNKNOWN",
            system_prompt=SYSTEM_PROMPT,
            decision_prompt=DECISION_PROMPT,
        )
        normalized = self.runtime.record_model_response(request_id=request.request_id, raw_response=_valid_response())
        self.assertEqual(normalized.action.value, "WAIT")
        events = self.store.audit_for_request(request.request_id)
        self.assertEqual(
            [event.event_kind for event in events],
            ["MODEL_REQUEST_PREPARED_OFFLINE", "MODEL_RESPONSE_RAW", "MODEL_RESPONSE_NORMALIZED"],
        )
        self.assertEqual(events[1].payload["raw_response"], _valid_response())
        self.assertTrue(events[2].payload["strict_output_enum_enforcement"])

    def test_invalid_output_enum_is_recorded_then_rejected(self) -> None:
        request = self.runtime.prepare_model_request(
            observation=_observation(),
            retrieval_query="UNKNOWN",
            system_prompt=SYSTEM_PROMPT,
            decision_prompt=DECISION_PROMPT,
        )
        invalid = json.loads(_valid_response())
        invalid["action"] = "HOLD"
        with self.assertRaises(ValueError):
            self.runtime.record_model_response(request_id=request.request_id, raw_response=json.dumps(invalid))
        events = self.store.audit_for_request(request.request_id)
        self.assertEqual(events[-1].event_kind, "MODEL_RESPONSE_REJECTED")
        self.assertTrue(events[-1].payload["strict_output_enum_enforcement"])

    def test_portable_export_contains_project_state_not_harness_opaque_state(self) -> None:
        observation = _observation()
        self.runtime.mutate_working_memory(
            field_name="directional_bias",
            new_value=Direction.LONG,
            reason="PORTABILITY_FIXTURE",
            observation_identity=observation.identity.identity,
        )
        self.runtime.append_journal(entry_id="journal-export", body="reflection")
        self.runtime.put_hypothesis(
            hypothesis_id="hyp-export",
            statement="candidate",
            falsifier="counterexample",
        )
        exported = self.runtime.portable_export()
        self.assertFalse(exported["harness_opaque_state_included"])
        self.assertEqual(exported["trader_identity"], self.identity.identity)
        self.assertEqual(exported["working_memory"]["directional_bias"], "LONG")
        self.assertEqual(exported["journal"][0]["semantic_class"], "DS_JOURNAL_REFLECTION_NOT_FACT_OR_POLICY")
        self.assertFalse(exported["hypotheses"][0]["executable_policy"])
        encoded = json.dumps(exported, ensure_ascii=False, sort_keys=True)
        self.assertNotIn("harness_session", encoded)
        self.assertNotIn("opaque_session", encoded)

    def test_database_rejects_a_different_trader_identity(self) -> None:
        with self.assertRaises(ValueError):
            PersistentTraderStore(self.db_path, trader_identity="different-trader")


if __name__ == "__main__":
    unittest.main()

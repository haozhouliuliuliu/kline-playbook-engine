"""合成测试：江河 AI 交易员基础不读取真实行情或候选结果。"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import os
import unittest

from src.jianghe_ai_trader import (
    AITraderProvider,
    AttentionMode,
    ChartRender,
    ConstrainedTradeIntent,
    DecisionAction,
    DecisionAuditRecord,
    Direction,
    JiangheAITraderIdentity,
    JiangheDecision,
    JiangheMarketReplay,
    JiangheObservation,
    JiangheWorkingMemory,
    KnowledgePackIdentity,
    ObservationBar,
    ObservationIdentity,
    PositionFact,
    ReplayClock,
    StrategyFamily,
    UnavailableAITraderProvider,
    WatchRegion,
    validate_transition,
)
from tools.build_jianghe_knowledge_pack_v0_1 import build_payload


UTC = timezone.utc
T0 = datetime(2026, 8, 23, 9, 31, tzinfo=UTC)


def make_bar(*, timeframe: str = "1m", closed: bool = True, available_at: datetime | None = None,
             close_time: datetime | None = None) -> ObservationBar:
    close = close_time or T0
    actual_available_at = available_at if available_at is not None else close
    return ObservationBar(
        timeframe=timeframe, open_time=close - timedelta(minutes=1), close_time=close,
        available_at=actual_available_at, open_price="100", high_price="101", low_price="99",
        close_price="100", volume="10", is_closed=closed,
    )


def make_observation(*, bars: tuple[ObservationBar, ...] | None = None, decision_time: datetime = T0,
                     exchange_time: datetime = T0) -> JiangheObservation:
    return JiangheObservation(
        identity=ObservationIdentity(decision_time, exchange_time, "cu", "SHFE.cu2609", "mapping-v1", "session-v1"),
        bars=bars or (make_bar(),),
        charts=(ChartRender("renderer-v1", "1m", "last-100-closed-bars", exchange_time, "render-hash", False),),
    )


def make_identity() -> JiangheAITraderIdentity:
    knowledge = KnowledgePackIdentity.from_documents("V1_1", {"dossier": "江河", "unknown": "UNKNOWN"})
    return JiangheAITraderIdentity(
        knowledge_pack_identity=knowledge.identity,
        primary_branch_registry_identity="primary-registry-v0-3",
        interpretation_set_identity="interpretation-set-v0-3",
        model_provider="CANDIDATE_PROVIDER", model_id_version="candidate-v1",
        system_prompt_identity="system-v1", decision_prompt_identity="decision-v1",
        context_selection_policy_identity="context-v1", memory_policy_identity="memory-v1",
        chart_renderer_identity="renderer-v1", observation_schema_version="V0_1", wake_policy_version="V0_1",
        decision_schema_version="V0_1", runtime_normalizer_identity="normalizer-v0-1",
        hard_execution_envelope_identity="risk-oms-safety-v1",
        inference_configuration=(("temperature", "0"),),
        tool_capability_set=("STRUCTURED_OBSERVATION",), source_family_scope=("A", "B", "C", "D"),
    )


def decision(action: DecisionAction, mode: AttentionMode, *, direction: Direction = Direction.NONE) -> JiangheDecision:
    intent = ConstrainedTradeIntent(direction, "ENTRY", "JH-CASE-SYNTHETIC") if action is DecisionAction.ENTER else None
    return JiangheDecision(mode, StrategyFamily.NONE, direction, action, "UNKNOWN_IS_ALLOWED", trade_intent=intent)


class JiangheAITraderFoundationTests(unittest.TestCase):
    def test_observation_identity_changes_when_one_ohlc_field_changes(self):
        original = make_observation()
        changed_bar = replace(original.bars[0], close_price="100.5")
        changed = make_observation(bars=(changed_bar,))
        self.assertNotEqual(original.identity.identity, changed.identity.identity)

    def test_position_and_order_facts_change_observation_identity(self):
        base = make_observation()
        with_position = JiangheObservation(
            identity=ObservationIdentity(T0, T0, "cu", "SHFE.cu2609", "mapping-v1", "session-v1"),
            bars=(make_bar(),),
            positions=(PositionFact(Direction.LONG, "1", (("entry_price", "100"),), ("stop-1",), ("order-1",)),),
            active_order_ids=("order-1",),
        )
        different_order = replace(with_position, active_order_ids=("order-2",))
        self.assertNotEqual(base.identity.identity, with_position.identity.identity)
        self.assertNotEqual(with_position.identity.identity, different_order.identity.identity)

    def test_all_material_bar_fields_are_identity_bound(self):
        original = make_observation(decision_time=T0 + timedelta(seconds=1))
        mutations = (
            {"volume": "11"},
            {"is_closed": False},
            {"available_at": T0 + timedelta(seconds=1)},
        )
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                changed = make_observation(
                    bars=(replace(original.bars[0], **mutation),),
                    decision_time=T0 + timedelta(seconds=1),
                )
                self.assertNotEqual(original.identity.identity, changed.identity.identity)

    def test_observation_order_is_canonical_and_same_content_is_stable(self):
        one_minute = make_bar(timeframe="1m")
        five_minute = make_bar(timeframe="5m")
        first = make_observation(bars=(one_minute, five_minute))
        reordered = make_observation(bars=(five_minute, one_minute))
        repeated = make_observation(bars=(one_minute, five_minute))
        self.assertEqual(first.bars, reordered.bars)
        self.assertEqual(first.identity.identity, reordered.identity.identity)
        self.assertEqual(first.identity.identity, repeated.identity.identity)

    def test_decimal_text_representation_is_preserved_in_observation_identity(self):
        first = make_observation(bars=(make_bar(),))
        second = make_observation(bars=(replace(
            make_bar(),
            open_price="100.00",
            high_price="101.000",
            low_price="99.0",
            close_price="1E+2",
            volume="10.0000",
        ),))
        self.assertEqual(first.bars[0].open_price, "100")
        self.assertEqual(second.bars[0].open_price, "100.00")
        self.assertNotEqual(first.identity.identity, second.identity.identity)

    def test_position_and_order_collection_order_is_not_semantic(self):
        first_position = PositionFact(
            Direction.LONG, "1", (("entry_price", "100"),),
            ("stop-2", "stop-1"), ("order-2", "order-1"),
        )
        second_position = PositionFact(
            Direction.SHORT, "2", (("entry_price", "101"),),
            ("stop-3",), ("order-3",),
        )
        first = JiangheObservation(
            ObservationIdentity(T0, T0, "cu", "SHFE.cu2609", "mapping-v1", "session-v1"),
            (make_bar(),), (first_position, second_position), ("order-3", "order-1"),
        )
        reordered = JiangheObservation(
            ObservationIdentity(T0, T0, "cu", "SHFE.cu2609", "mapping-v1", "session-v1"),
            (make_bar(),),
            (
                second_position,
                PositionFact(
                    Direction.LONG, "1", (("entry_price", "100"),),
                    ("stop-1", "stop-2"), ("order-1", "order-2"),
                ),
            ),
            ("order-1", "order-3"),
        )
        self.assertEqual(first.identity.identity, reordered.identity.identity)

    def test_observation_bar_preserves_numeric_domain_values_for_renderer_audit(self):
        for field_name, value in (
            ("open_price", "NaN"),
            ("high_price", "99.5"),
            ("low_price", "100.5"),
            ("volume", "-0.1"),
        ):
            with self.subTest(field_name=field_name, value=value):
                changed = replace(make_bar(), **{field_name: value})
                self.assertEqual(getattr(changed, field_name), value)
        for value in (100.0, "", " 100"):
            with self.subTest(invalid_transport_value=value):
                with self.assertRaises(ValueError):
                    replace(make_bar(), close_price=value)

    def test_observation_bar_enforces_closed_and_partial_availability(self):
        with self.assertRaises(ValueError):
            make_bar(closed=True, available_at=T0 - timedelta(seconds=1))
        with self.assertRaises(ValueError):
            make_bar(closed=False, available_at=T0 - timedelta(seconds=1))
        self.assertFalse(make_bar(closed=False).is_closed)

    def test_future_bar_and_wrong_available_at_are_denied(self):
        with self.assertRaises(ValueError):
            make_observation(bars=(make_bar(available_at=T0 + timedelta(seconds=1)),))
        with self.assertRaises(ValueError):
            make_observation(bars=(make_bar(close_time=T0 + timedelta(minutes=1), available_at=T0 + timedelta(minutes=1)),))

    def test_multi_timeframe_causal_cutoff_and_partial_marking(self):
        observation = make_observation(bars=(
            make_bar(timeframe="1m"), make_bar(timeframe="5m"),
            make_bar(timeframe="15m"), make_bar(timeframe="1h"),
        ))
        self.assertEqual(observation.timeframes, ("15m", "1h", "1m", "5m"))
        partial = make_bar(closed=False)
        self.assertFalse(partial.is_closed)
        with self.assertRaises(ValueError):
            JiangheMarketReplay(ReplayClock(T0 - timedelta(minutes=1))).accept_observation(make_observation(bars=(partial,)))

    def test_observation_hides_pnl_but_keeps_position_and_order_facts(self):
        observation = JiangheObservation(
            identity=ObservationIdentity(T0, T0, "cu", "SHFE.cu2609", "mapping-v1", "session-v1"),
            bars=(make_bar(),),
            positions=(PositionFact(Direction.LONG, "1", (("entry_price", "100"),), ("stop-1",), ("order-1",)),),
            active_order_ids=("order-1",),
        )
        self.assertFalse(hasattr(observation, "pnl"))
        self.assertEqual(observation.positions[0].protective_orders, ("stop-1",))
        self.assertEqual(observation.active_order_ids, ("order-1",))

    def test_knowledge_identity_changes_only_with_content_or_version(self):
        first = KnowledgePackIdentity.from_documents("V1_1", {"a": "same", "b": "same"})
        reordered = KnowledgePackIdentity.from_documents("V1_1", {"b": "same", "a": "same"})
        changed = KnowledgePackIdentity.from_documents("V1_1", {"a": "changed", "b": "same"})
        self.assertEqual(first.identity, reordered.identity)
        self.assertNotEqual(first.identity, changed.identity)
        old_cwd = os.getcwd()
        try:
            os.chdir(os.path.dirname(old_cwd))
            self.assertEqual(first.identity, KnowledgePackIdentity.from_documents("V1_1", {"a": "same", "b": "same"}).identity)
        finally:
            os.chdir(old_cwd)

    def test_knowledge_pack_builder_matches_checked_in_artifact(self):
        import json
        from pathlib import Path

        artifact = Path(__file__).resolve().parents[1] / "docs" / "evidence" / "JIANGHE_AI_TRADER_FOUNDATION_V0_1.json"
        self.assertEqual(build_payload(), json.loads(artifact.read_text(encoding="utf-8")))

    def test_provider_and_inference_configuration_are_identity_bound(self):
        first = make_identity()
        changed = JiangheAITraderIdentity(
            knowledge_pack_identity=first.knowledge_pack_identity,
            primary_branch_registry_identity=first.primary_branch_registry_identity,
            interpretation_set_identity=first.interpretation_set_identity,
            model_provider="CANDIDATE_PROVIDER", model_id_version="candidate-v2",
            system_prompt_identity="system-v1", decision_prompt_identity="decision-v1",
            context_selection_policy_identity="context-v1", memory_policy_identity="memory-v1",
            chart_renderer_identity="renderer-v1", observation_schema_version="V0_1", wake_policy_version="V0_1",
            decision_schema_version="V0_1", runtime_normalizer_identity=first.runtime_normalizer_identity,
            hard_execution_envelope_identity=first.hard_execution_envelope_identity,
            inference_configuration=(("temperature", "0"),),
            tool_capability_set=("STRUCTURED_OBSERVATION",), source_family_scope=("A", "B", "C", "D"),
        )
        self.assertNotEqual(first.identity, changed.identity)

    def test_ai_identity_binds_primary_registry_normalizer_and_execution_envelope(self):
        identity = make_identity()
        self.assertTrue(identity.primary_branch_registry_identity)
        self.assertTrue(identity.interpretation_set_identity)
        self.assertTrue(identity.runtime_normalizer_identity)
        self.assertTrue(identity.hard_execution_envelope_identity)
        for field_name in (
            "primary_branch_registry_identity",
            "interpretation_set_identity",
            "runtime_normalizer_identity",
            "hard_execution_envelope_identity",
        ):
            with self.subTest(field_name=field_name):
                self.assertNotEqual(
                    identity.identity,
                    replace(identity, **{field_name: f"changed-{field_name}"}).identity,
                )
        with self.assertRaises(ValueError):
            replace(identity, source_family_scope=())
        with self.assertRaises(ValueError):
            replace(identity, inference_configuration=(("temperature", "0"), ("temperature", "1")))

    def test_memory_mutation_is_append_only_and_watch_region_expires(self):
        identity = make_identity()
        region = WatchRegion("watch-1", "99", "101", T0, T0 + timedelta(minutes=2), "synthetic")
        memory = JiangheWorkingMemory().mutate(field_name="watch_regions", new_value=(region,), reason="CREATE", timestamp=T0,
                                                observation_identity="obs-1", ai_trader_identity=identity.identity)
        expired = memory.expire_watch_regions(T0 + timedelta(minutes=3), "obs-2", identity.identity)
        self.assertEqual(memory.watch_regions, (region,))
        self.assertEqual(expired.watch_regions, ())
        self.assertEqual(len(expired.mutation_history), 2)
        with self.assertRaises(ValueError):
            expired.mutate(field_name="directional_bias", new_value=Direction.LONG, reason="bad time", timestamp=T0,
                           observation_identity="obs-3", ai_trader_identity=identity.identity)

    def test_state_transitions_and_unknown_no_trade_are_legal(self):
        self.assertEqual(validate_transition(AttentionMode.SCAN, decision(DecisionAction.WATCH, AttentionMode.WATCH)), AttentionMode.WATCH)
        self.assertEqual(validate_transition(AttentionMode.WATCH, decision(DecisionAction.CANDIDATE, AttentionMode.CANDIDATE)), AttentionMode.CANDIDATE)
        self.assertEqual(validate_transition(AttentionMode.CANDIDATE, decision(DecisionAction.WAIT, AttentionMode.WATCH)), AttentionMode.WATCH)
        self.assertEqual(validate_transition(AttentionMode.CANDIDATE, decision(DecisionAction.ENTER, AttentionMode.IN_POSITION, direction=Direction.LONG)), AttentionMode.IN_POSITION)
        self.assertEqual(validate_transition(AttentionMode.IN_POSITION, decision(DecisionAction.MANAGE, AttentionMode.IN_POSITION)), AttentionMode.IN_POSITION)
        self.assertEqual(validate_transition(AttentionMode.IN_POSITION, decision(DecisionAction.EXIT, AttentionMode.SCAN)), AttentionMode.SCAN)
        self.assertEqual(validate_transition(AttentionMode.SCAN, decision(DecisionAction.NO_TRADE, AttentionMode.SCAN)), AttentionMode.SCAN)

    def test_annotations_are_not_market_facts(self):
        chart = ChartRender("renderer-v1", "1m", "window", T0, "hash", False, (("AI_WATCH_REGION", "99-101"),))
        self.assertEqual(chart.annotations[0][0], "AI_WATCH_REGION")
        self.assertFalse(hasattr(make_bar(), "annotations"))

    def test_chart_render_is_bound_to_source_observation_and_artifact_identity(self):
        observation = make_observation()
        chart = observation.charts[0]
        self.assertEqual(chart.source_observation_identity, observation.identity.identity)
        self.assertEqual(chart.renderer_config_identity, "renderer-v1")
        self.assertTrue(chart.visual_artifact_identity)
        with self.assertRaises(ValueError):
            ChartRender(
                "renderer-v1", "1m", "window", T0, "render-hash", False,
                source_observation_identity=observation.identity.identity,
                renderer_config_identity="renderer-config-v1",
                visual_artifact_identity="caller-forged-compound-identity",
            )

    def test_model_latency_sets_earliest_intent_and_replay_never_rewinds(self):
        replay = JiangheMarketReplay(ReplayClock(T0 - timedelta(minutes=1)))
        observation = make_observation()
        replay.accept_observation(observation)
        record = DecisionAuditRecord(
            observation.identity.identity, make_identity().identity, "synthetic raw", decision(DecisionAction.WATCH, AttentionMode.WATCH),
            T0, T0 + timedelta(seconds=1), T0 + timedelta(seconds=4), T0 + timedelta(seconds=4), T0 + timedelta(seconds=4),
        )
        replay.record_decision(record)
        self.assertEqual(replay.clock.current_time, T0 + timedelta(seconds=4))
        with self.assertRaises(ValueError):
            replay.accept_observation(make_observation(decision_time=T0, exchange_time=T0))

    def test_replay_rejects_unaccepted_stale_or_unrelated_observation_decisions(self):
        replay = JiangheMarketReplay(ReplayClock(T0 - timedelta(minutes=1)))
        accepted = make_observation()
        unrelated = make_observation(bars=(replace(make_bar(), volume="11"),))

        def record_for(observation_identity: str) -> DecisionAuditRecord:
            return DecisionAuditRecord(
                observation_identity, make_identity().identity, "synthetic raw",
                decision(DecisionAction.WATCH, AttentionMode.WATCH),
                T0, T0 + timedelta(seconds=1), T0 + timedelta(seconds=2),
                T0 + timedelta(seconds=2), T0 + timedelta(seconds=2),
            )

        with self.assertRaises(ValueError):
            replay.record_decision(record_for(accepted.identity.identity))
        replay.accept_observation(accepted)
        with self.assertRaises(ValueError):
            replay.record_decision(record_for(unrelated.identity.identity))

    def test_real_provider_is_absent_and_fails_closed(self):
        provider: AITraderProvider = UnavailableAITraderProvider()
        with self.assertRaises(RuntimeError):
            provider.decide(make_observation(), JiangheWorkingMemory())


if __name__ == "__main__":
    unittest.main()

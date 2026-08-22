"""合成测试：江河 AI 交易员基础不读取真实行情或候选结果。"""

from __future__ import annotations

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
    return ObservationBar(
        timeframe=timeframe, open_time=close - timedelta(minutes=1), close_time=close,
        available_at=available_at or close, open_price="100", high_price="101", low_price="99",
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
        knowledge_pack_identity=knowledge.identity, model_provider="CANDIDATE_PROVIDER", model_id_version="candidate-v1",
        system_prompt_identity="system-v1", decision_prompt_identity="decision-v1",
        context_selection_policy_identity="context-v1", memory_policy_identity="memory-v1",
        chart_renderer_identity="renderer-v1", observation_schema_version="V0_1", wake_policy_version="V0_1",
        decision_schema_version="V0_1", inference_configuration=(("temperature", "0"),),
        tool_capability_set=("STRUCTURED_OBSERVATION",), source_family_scope=("A", "B", "C", "D"),
    )


def decision(action: DecisionAction, mode: AttentionMode, *, direction: Direction = Direction.NONE) -> JiangheDecision:
    intent = ConstrainedTradeIntent(direction, "ENTRY", "JH-CASE-SYNTHETIC") if action is DecisionAction.ENTER else None
    return JiangheDecision(mode, StrategyFamily.NONE, direction, action, "UNKNOWN_IS_ALLOWED", trade_intent=intent)


class JiangheAITraderFoundationTests(unittest.TestCase):
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
            knowledge_pack_identity=first.knowledge_pack_identity, model_provider="CANDIDATE_PROVIDER", model_id_version="candidate-v2",
            system_prompt_identity="system-v1", decision_prompt_identity="decision-v1",
            context_selection_policy_identity="context-v1", memory_policy_identity="memory-v1",
            chart_renderer_identity="renderer-v1", observation_schema_version="V0_1", wake_policy_version="V0_1",
            decision_schema_version="V0_1", inference_configuration=(("temperature", "0"),),
            tool_capability_set=("STRUCTURED_OBSERVATION",), source_family_scope=("A", "B", "C", "D"),
        )
        self.assertNotEqual(first.identity, changed.identity)

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

    def test_real_provider_is_absent_and_fails_closed(self):
        provider: AITraderProvider = UnavailableAITraderProvider()
        with self.assertRaises(RuntimeError):
            provider.decide(make_observation(), JiangheWorkingMemory())


if __name__ == "__main__":
    unittest.main()

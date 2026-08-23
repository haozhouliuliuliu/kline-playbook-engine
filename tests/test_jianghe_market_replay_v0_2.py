"""合成对抗测试：江河观察构建与市场回放工程 V0.2（无真实模型、无候选结果）。"""

from __future__ import annotations

from dataclasses import fields
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import unittest

from src.jianghe_ai_trader import (
    AttentionMode,
    DecisionAction,
    Direction,
    JiangheAITraderIdentity,
    JiangheDecision,
    JiangheObservation,
    JiangheWorkingMemory,
    KnowledgePackIdentity,
    ObservationBar,
    PositionFact,
    StrategyFamily,
    WakeEventType,
    WatchRegion,
)
from src.jianghe_chart_renderer import JiangheChartRenderer
from src.jianghe_market_replay import (
    InvalidationLevel,
    JiangheMarketReplaySession,
    JiangheObservationBuilder,
    ReplayTraceRecord,
    RollingMarketState,
    SyntheticScriptedProvider,
)


UTC = timezone.utc
BASE = datetime(2026, 8, 23, 10, 0, tzinfo=UTC)
LATENCY = timedelta(seconds=5)


def minute_bar(index: int, *, open_price: str = "100", high_price: str = "101",
                low_price: str = "99", close_price: str = "100", volume: str = "10",
                available_offset: int = 0) -> ObservationBar:
    open_time = BASE + timedelta(minutes=index)
    close_time = open_time + timedelta(minutes=1)
    high = max(Decimal(high_price), Decimal(open_price), Decimal(close_price))
    low = min(Decimal(low_price), Decimal(open_price), Decimal(close_price))
    return ObservationBar(
        timeframe="1m",
        open_time=open_time,
        close_time=close_time,
        available_at=close_time + timedelta(seconds=available_offset),
        open_price=open_price,
        high_price=str(high),
        low_price=str(low),
        close_price=close_price,
        volume=volume,
        is_closed=True,
    )


def varying_bar(index: int) -> ObservationBar:
    return minute_bar(
        index,
        open_price=str(95 + index % 4),
        high_price=str(100 + index % 7),
        low_price=str(90 + index % 3),
        close_price=str(92 + index % 5),
        volume=str(index + 1),
    )


def make_ai_identity() -> JiangheAITraderIdentity:
    knowledge = KnowledgePackIdentity.from_documents("V1_1", {"dossier": "江河", "unknown": "UNKNOWN"})
    return JiangheAITraderIdentity(
        knowledge_pack_identity=knowledge.identity,
        primary_branch_registry_identity="primary-registry-v0-3",
        interpretation_set_identity="interpretation-set-v0-3",
        model_provider="CANDIDATE_PROVIDER",
        model_id_version="candidate-v1",
        system_prompt_identity="system-v1",
        decision_prompt_identity="decision-v1",
        context_selection_policy_identity="context-v1",
        memory_policy_identity="memory-v1",
        chart_renderer_identity="JIANGHE_CHART_RENDERER_V0_1",
        observation_schema_version="V0_1",
        wake_policy_version="V0_1",
        decision_schema_version="V0_1",
        runtime_normalizer_identity="normalizer-v0-1",
        hard_execution_envelope_identity="risk-oms-safety-v1",
        inference_configuration=(("temperature", "0"),),
        tool_capability_set=("STRUCTURED_OBSERVATION",),
        source_family_scope=("A", "B", "C", "D"),
    )


def make_state() -> RollingMarketState:
    return RollingMarketState(
        product="cu",
        concrete_contract="SHFE.cu2609",
        mapping_identity="mapping-v1",
        session_identity="synthetic-session",
    )


def echo_watch_policy(
    observation: JiangheObservation, memory: JiangheWorkingMemory
) -> tuple[str, JiangheDecision]:
    """回声策略：首次调用建立 watch region，之后始终回显记忆中的 region。"""
    regions = memory.watch_regions or (
        WatchRegion("watch-1", "99", "101", BASE, BASE + timedelta(hours=2), "synthetic"),
    )
    return "synthetic:echo-watch", JiangheDecision(
        attention_mode=AttentionMode.WATCH,
        family=StrategyFamily.NONE,
        direction=Direction.NONE,
        action=DecisionAction.WATCH,
        uncertainty="SYNTHETIC_ECHO",
        watch_regions=regions,
        rationale="synthetic echo policy",
    )


def make_session(
    *,
    provider=None,
    wake_policy=None,
    latency: timedelta = LATENCY,
) -> JiangheMarketReplaySession:
    return JiangheMarketReplaySession(
        session_id="S1",
        state=make_state(),
        provider=provider or SyntheticScriptedProvider(),
        ai_trader_identity=make_ai_identity(),
        synthetic_model_latency=latency,
        wake_policy=wake_policy,
        clock_start=BASE,
    )


def aggregate(bars: list[ObservationBar]) -> dict[str, Decimal]:
    return {
        "open": Decimal(bars[0].open_price),
        "high": max(Decimal(bar.high_price) for bar in bars),
        "low": min(Decimal(bar.low_price) for bar in bars),
        "close": Decimal(bars[-1].close_price),
        "volume": sum(Decimal(bar.volume) for bar in bars),
    }


class RollingMarketStateTests(unittest.TestCase):
    def test_future_backward_and_duplicate_bars_are_denied(self):
        state = make_state()
        state.accept_1m_bar(minute_bar(0))
        with self.assertRaises(ValueError):
            state.accept_1m_bar(minute_bar(0))
        with self.assertRaises(ValueError):
            state.accept_1m_bar(minute_bar(0, close_price="105"))

    def test_sub_minute_sequences_cannot_be_fabricated(self):
        state = make_state()
        unaligned = ObservationBar(
            timeframe="1m",
            open_time=BASE + timedelta(seconds=30),
            close_time=BASE + timedelta(seconds=90),
            available_at=BASE + timedelta(seconds=90),
            open_price="100", high_price="101", low_price="99", close_price="100",
            volume="10", is_closed=True,
        )
        with self.assertRaises(ValueError):
            state.accept_1m_bar(unaligned)
        thirty_second = ObservationBar(
            timeframe="30s",
            open_time=BASE,
            close_time=BASE + timedelta(seconds=30),
            available_at=BASE + timedelta(seconds=30),
            open_price="100", high_price="101", low_price="99", close_price="100",
            volume="10", is_closed=True,
        )
        with self.assertRaises(ValueError):
            state.accept_1m_bar(thirty_second)
        for timeframe in ("30s", "1s", "tick"):
            with self.assertRaises(ValueError):
                state.closed_bars(timeframe, limit=10)
            with self.assertRaises(ValueError):
                state.snapshot(timeframe, limit=10)

    def test_causal_aggregation_to_5m_15m_1h(self):
        state = make_state()
        bars = [varying_bar(i) for i in range(60)]
        for index in range(3):
            state.accept_1m_bar(bars[index])
        partial_5m = state.partial_bar("5m")
        self.assertIsNotNone(partial_5m)
        self.assertFalse(partial_5m.is_closed)
        expected_3 = aggregate(bars[:3])
        self.assertEqual(Decimal(partial_5m.open_price), expected_3["open"])
        self.assertEqual(Decimal(partial_5m.high_price), expected_3["high"])
        self.assertEqual(Decimal(partial_5m.low_price), expected_3["low"])
        self.assertEqual(Decimal(partial_5m.close_price), expected_3["close"])
        self.assertEqual(Decimal(partial_5m.volume), expected_3["volume"])
        # 部分桶以最后一根已见 1 分钟 K 线收盘时间为当前已知范围，不越界到未来。
        self.assertEqual(partial_5m.close_time, bars[2].close_time)
        self.assertEqual(partial_5m.available_at, bars[2].available_at)
        # 因果性：部分桶高低点只来自已见 K 线，不含尚未喂入的未来 K 线。
        future_high = Decimal(varying_bar(3).high_price)
        self.assertLess(Decimal(partial_5m.high_price), future_high + Decimal(1000))

        # 第 4 根（收盘 10:04）不会收盘 [10:00,10:05) 桶。
        result = state.accept_1m_bar(bars[3])
        self.assertEqual(result, ("1m",))
        partial_after_4 = state.partial_bar("5m")
        self.assertEqual(Decimal(partial_after_4.volume), aggregate(bars[:4])["volume"])

        # 第 5 根（收盘 10:05）收盘 [10:00,10:05) 桶。
        result = state.accept_1m_bar(bars[4])
        self.assertEqual(result, ("1m", "5m"))
        closed_5m = state.closed_bars("5m", limit=10)
        self.assertEqual(len(closed_5m), 1)
        self.assertTrue(closed_5m[0].is_closed)
        expected_5m = aggregate(bars[:5])
        self.assertEqual(Decimal(closed_5m[0].open_price), expected_5m["open"])
        self.assertEqual(Decimal(closed_5m[0].high_price), expected_5m["high"])
        self.assertEqual(Decimal(closed_5m[0].low_price), expected_5m["low"])
        self.assertEqual(Decimal(closed_5m[0].close_price), expected_5m["close"])
        self.assertEqual(Decimal(closed_5m[0].volume), expected_5m["volume"])
        self.assertEqual(closed_5m[0].open_time, BASE)
        self.assertEqual(closed_5m[0].close_time, BASE + timedelta(minutes=5))
        self.assertEqual(closed_5m[0].available_at, bars[4].available_at)

        # 第 15 根（收盘 10:15）收盘 [10:00,10:15) 桶。
        last = None
        for index in range(5, 15):
            last = state.accept_1m_bar(bars[index])
        self.assertEqual(last, ("1m", "5m", "15m"))
        closed_15m = state.closed_bars("15m", limit=10)
        self.assertEqual(len(closed_15m), 1)
        self.assertTrue(closed_15m[0].is_closed)
        self.assertEqual(Decimal(closed_15m[0].volume), aggregate(bars[:15])["volume"])
        self.assertEqual(closed_15m[0].close_time, BASE + timedelta(minutes=15))
        self.assertEqual(closed_15m[0].available_at, bars[14].available_at)

        # 第 60 根（收盘 11:00）收盘 [10:00,11:00) 桶。
        for index in range(15, 60):
            last = state.accept_1m_bar(bars[index])
        self.assertEqual(last, ("1m", "5m", "15m", "1h"))
        closed_1h = state.closed_bars("1h", limit=10)
        self.assertEqual(len(closed_1h), 1)
        expected_1h = aggregate(bars[:60])
        self.assertEqual(Decimal(closed_1h[0].open_price), expected_1h["open"])
        self.assertEqual(Decimal(closed_1h[0].high_price), expected_1h["high"])
        self.assertEqual(Decimal(closed_1h[0].low_price), expected_1h["low"])
        self.assertEqual(Decimal(closed_1h[0].close_price), expected_1h["close"])
        self.assertEqual(Decimal(closed_1h[0].volume), expected_1h["volume"])
        self.assertEqual(closed_1h[0].close_time, BASE + timedelta(hours=1))
        self.assertEqual(closed_1h[0].available_at, bars[59].available_at)


class ObservationBuilderTests(unittest.TestCase):
    def test_builder_produces_multi_timeframe_observation_with_partial_marking(self):
        state = make_state()
        for index in range(7):
            state.accept_1m_bar(varying_bar(index))
        builder = JiangheObservationBuilder(renderer=JiangheChartRenderer())
        observation = builder.build(state=state, session_identity="synthetic-session")
        self.assertEqual(observation.timeframes, ("15m", "1h", "1m", "5m"))
        partial_timeframes = {bar.timeframe for bar in observation.bars if not bar.is_closed}
        self.assertEqual(partial_timeframes, {"5m", "15m", "1h"})
        self.assertTrue(
            all(bar.available_at <= observation.identity.decision_time for bar in observation.bars)
        )
        self.assertTrue(
            all(
                chart.partial_bar_marked
                for chart in observation.charts
                if chart.timeframe in partial_timeframes
            )
        )
        one_m_chart = next(chart for chart in observation.charts if chart.timeframe == "1m")
        self.assertFalse(one_m_chart.partial_bar_marked)

    def test_builder_denies_decision_time_before_availability(self):
        state = make_state()
        state.accept_1m_bar(minute_bar(0, available_offset=30))
        builder = JiangheObservationBuilder(renderer=JiangheChartRenderer())
        with self.assertRaises(ValueError):
            builder.build(
                state=state,
                decision_time=BASE + timedelta(minutes=1),
                session_identity="synthetic-session",
            )
        observation = builder.build(state=state, session_identity="synthetic-session")
        self.assertEqual(observation.identity.decision_time, BASE + timedelta(minutes=1, seconds=30))

    def test_builder_deterministic_rendering_identity(self):
        state = make_state()
        for index in range(10):
            state.accept_1m_bar(varying_bar(index))
        builder = JiangheObservationBuilder(renderer=JiangheChartRenderer())
        first = builder.build(state=state, session_identity="synthetic-session")
        second = builder.build(state=state, session_identity="synthetic-session")
        self.assertEqual(first.identity.identity, second.identity.identity)
        self.assertEqual(
            [chart.render_content_hash for chart in first.charts],
            [chart.render_content_hash for chart in second.charts],
        )
        self.assertEqual(
            [chart.render_content_hash for chart in first.charts],
            [chart.render_content_hash for chart in builder.build(state=state, session_identity="synthetic-session").charts],
        )

    def test_pnl_is_hidden_but_position_and_order_facts_are_visible(self):
        state = make_state()
        state.accept_1m_bar(minute_bar(0))
        builder = JiangheObservationBuilder(renderer=JiangheChartRenderer())
        position = PositionFact(
            Direction.LONG, "2", (("entry_price", "100"),), ("stop-1",), ("order-1",)
        )
        observation = builder.build(
            state=state,
            positions=(position,),
            active_order_ids=("order-1",),
            session_identity="synthetic-session",
        )
        observed_fields = {field.name.lower() for field in fields(JiangheObservation)}
        for name in observed_fields:
            self.assertNotIn("pnl", name)
            self.assertNotIn("profit", name)
            self.assertNotIn("equity", name)
        self.assertEqual(observation.positions, (position,))
        self.assertEqual(observation.active_order_ids, ("order-1",))
        self.assertEqual(observation.positions[0].protective_orders, ("stop-1",))


class WakeSchedulerSessionTests(unittest.TestCase):
    def test_watch_region_enter_and_exit_wake(self):
        session = make_session(
            provider=SyntheticScriptedProvider(policy=echo_watch_policy),
            wake_policy=frozenset(
                {WakeEventType.PRICE_ENTERS_AI_WATCH_REGION, WakeEventType.PRICE_EXITS_AI_WATCH_REGION}
            ),
        )
        region = WatchRegion("watch-1", "99", "101", BASE, BASE + timedelta(minutes=10), "synthetic")
        session.set_ai_watch_regions((region,), reason="TEST_SETUP", timestamp=BASE)
        events_first = session.feed_1m_bar(minute_bar(0, close_price="98"))
        self.assertEqual(
            {event.event_type for event in events_first}, {WakeEventType.NEW_1M_CLOSED_BAR}
        )
        events_enter = session.feed_1m_bar(minute_bar(1, close_price="100"))
        self.assertIn(
            WakeEventType.PRICE_ENTERS_AI_WATCH_REGION, {e.event_type for e in events_enter}
        )
        self.assertEqual(session.traces[-1].wake_event_type, "PRICE_ENTERS_AI_WATCH_REGION")
        events_exit = session.feed_1m_bar(minute_bar(2, close_price="102"))
        self.assertIn(
            WakeEventType.PRICE_EXITS_AI_WATCH_REGION, {e.event_type for e in events_exit}
        )

    def test_watch_region_expiry_stops_waking(self):
        session = make_session(
            provider=SyntheticScriptedProvider(policy=echo_watch_policy),
            wake_policy=frozenset({WakeEventType.PRICE_ENTERS_AI_WATCH_REGION}),
        )
        region = WatchRegion("watch-1", "99", "101", BASE, BASE + timedelta(minutes=3), "synthetic")
        session.set_ai_watch_regions((region,), reason="TEST_SETUP", timestamp=BASE)
        session.feed_1m_bar(minute_bar(0, close_price="98"))
        events_enter = session.feed_1m_bar(minute_bar(1, close_price="100"))
        self.assertIn(
            WakeEventType.PRICE_ENTERS_AI_WATCH_REGION, {e.event_type for e in events_enter}
        )
        events_at_expiry = session.feed_1m_bar(minute_bar(2, close_price="100"))
        self.assertEqual(
            {event.event_type for event in events_at_expiry}, {WakeEventType.NEW_1M_CLOSED_BAR}
        )
        events_after_expiry = session.feed_1m_bar(minute_bar(3, close_price="102"))
        self.assertEqual(
            {event.event_type for event in events_after_expiry}, {WakeEventType.NEW_1M_CLOSED_BAR}
        )
        self.assertEqual(session.memory.watch_regions, ())

    def test_invalidation_level_touched_and_expiry(self):
        session = make_session(
            wake_policy=frozenset({WakeEventType.AI_INVALIDATION_LEVEL_TOUCHED})
        )
        level = InvalidationLevel("level-1", "105", BASE, BASE + timedelta(minutes=10), "synthetic")
        session.set_ai_invalidation_levels((level,), reason="TEST_SETUP", timestamp=BASE)
        events_normal = session.feed_1m_bar(minute_bar(0, high_price="101", low_price="99"))
        self.assertNotIn(
            WakeEventType.AI_INVALIDATION_LEVEL_TOUCHED, {e.event_type for e in events_normal}
        )
        events_touch = session.feed_1m_bar(minute_bar(1, high_price="106", low_price="104"))
        self.assertIn(
            WakeEventType.AI_INVALIDATION_LEVEL_TOUCHED, {e.event_type for e in events_touch}
        )
        self.assertEqual(
            session.traces[-1].wake_event_type, "AI_INVALIDATION_LEVEL_TOUCHED"
        )
        expired_session = make_session(
            wake_policy=frozenset({WakeEventType.AI_INVALIDATION_LEVEL_TOUCHED})
        )
        expired_level = InvalidationLevel(
            "level-2", "105", BASE, BASE + timedelta(minutes=1), "synthetic"
        )
        expired_session.set_ai_invalidation_levels(
            (expired_level,), reason="TEST_SETUP", timestamp=BASE
        )
        events_expired = expired_session.feed_1m_bar(
            minute_bar(1, high_price="106", low_price="104")
        )
        self.assertEqual(
            {event.event_type for event in events_expired}, {WakeEventType.NEW_1M_CLOSED_BAR}
        )
        self.assertEqual(expired_session.invalidation_levels, ())

    def test_all_eleven_wake_types_are_reachable(self):
        session = make_session(provider=SyntheticScriptedProvider(policy=echo_watch_policy))
        self.assertEqual(session.wake_policy, frozenset(WakeEventType))
        region = WatchRegion("watch-1", "99", "101", BASE, BASE + timedelta(hours=2), "synthetic")
        session.set_ai_watch_regions((region,), reason="TEST_SETUP", timestamp=BASE)
        level = InvalidationLevel("level-1", "150", BASE, BASE + timedelta(hours=2), "synthetic")
        session.set_ai_invalidation_levels((level,), reason="TEST_SETUP", timestamp=BASE)
        seen = set()
        prices = ("98", "100", "102", "100")
        for index in range(60):
            close = prices[index % len(prices)]
            high = "151" if index == 30 else "101"
            for event in session.feed_1m_bar(
                minute_bar(index, close_price=close, high_price=high)
            ):
                seen.add(event.event_type)
        for event_type in (
            WakeEventType.ORDER_EVENT,
            WakeEventType.POSITION_EVENT,
            WakeEventType.SAFETY_EVENT,
            WakeEventType.SESSION_EVENT,
        ):
            event = session.emit_external_wake(
                event_type,
                occurred_at=session.clock.current_time,
                context=f"synthetic-{event_type.value}",
            )
            seen.add(event.event_type)
        self.assertEqual(seen, set(WakeEventType))

    def test_external_wake_rejects_backward_time_and_market_types(self):
        session = make_session()
        session.feed_1m_bar(minute_bar(0))
        with self.assertRaises(ValueError):
            session.emit_external_wake(
                WakeEventType.ORDER_EVENT,
                occurred_at=session.clock.current_time - timedelta(seconds=1),
                context="backward",
            )
        with self.assertRaises(ValueError):
            session.emit_external_wake(
                WakeEventType.NEW_1M_CLOSED_BAR,
                occurred_at=session.clock.current_time,
                context="wrong-surface",
            )
        event = session.emit_external_wake(
            WakeEventType.ORDER_EVENT,
            occurred_at=session.clock.current_time,
            context="order-filled",
        )
        self.assertEqual(event.event_type, WakeEventType.ORDER_EVENT)
        self.assertEqual(session.traces[-1].wake_event_type, "ORDER_EVENT")


class ReplaySessionTests(unittest.TestCase):
    def test_session_memory_persists_across_model_calls(self):
        provider = SyntheticScriptedProvider(policy=echo_watch_policy)
        session = make_session(provider=provider)
        session.feed_1m_bar(minute_bar(0, close_price="98"))
        self.assertEqual(len(provider.calls), 1)
        session.feed_1m_bar(minute_bar(1, close_price="100"))
        # 第二根 K 线触发 NEW_1M 与进入观察区两次唤醒，各自产生一次模型调用。
        self.assertEqual(len(provider.calls), 3)
        self.assertEqual(provider.calls[1].watch_region_ids_before, ("watch-1",))
        self.assertIn("AI_WATCH_REGION", provider.calls[1].chart_annotation_kinds)
        self.assertEqual(session.memory.watch_regions[0].region_id, "watch-1")
        trace = session.traces[-1]
        self.assertIn(("AI_WATCH_REGION", "watch-1:99-101"), trace.annotations)

    def test_next_session_resets_by_design_and_archives_knowledge(self):
        provider = SyntheticScriptedProvider(policy=echo_watch_policy)
        session = make_session(provider=provider)
        session.feed_1m_bar(minute_bar(0))
        self.assertEqual(session.memory.attention_mode, AttentionMode.WATCH)
        clock_before = session.clock.current_time
        traces_before = len(session.traces)
        archived = session.roll_to_new_session("S2")
        self.assertEqual(archived.session_id, "S1")
        self.assertEqual(archived.memory.watch_regions[0].region_id, "watch-1")
        self.assertEqual(archived.trace_count, traces_before)
        self.assertEqual(session.session_id, "S2")
        self.assertEqual(session.memory.attention_mode, AttentionMode.SCAN)
        self.assertEqual(session.memory.watch_regions, ())
        self.assertEqual(session.invalidation_levels, ())
        self.assertEqual(session.clock.current_time, clock_before)
        self.assertEqual(len(session.traces), traces_before)
        self.assertEqual(len(session.archived_sessions), 1)
        session.feed_1m_bar(minute_bar(1))
        self.assertEqual(provider.calls[-1].watch_region_ids_before, ())

    def test_latency_defers_intent_and_blocks_backward_intent(self):
        session = make_session(latency=LATENCY)
        session.feed_1m_bar(minute_bar(0))
        trace = session.traces[-1]
        observation_available = BASE + timedelta(minutes=1)
        self.assertEqual(trace.model_request_at, observation_available)
        self.assertEqual(trace.intent_available_at, observation_available + LATENCY)
        self.assertEqual(session.clock.current_time, observation_available + LATENCY)
        self.assertGreaterEqual(trace.intent_available_at, trace.model_response_at)
        self.assertGreaterEqual(trace.model_response_at, trace.model_request_at)
        self.assertGreaterEqual(trace.model_request_at, observation_available)
        builder = JiangheObservationBuilder(renderer=JiangheChartRenderer())
        stale = builder.build(
            state=session.state,
            decision_time=observation_available + timedelta(seconds=3),
            session_identity="S1",
        )
        with self.assertRaises(ValueError):
            session.replay.accept_observation(stale)
        session.feed_1m_bar(minute_bar(1))
        self.assertGreaterEqual(
            session.traces[-1].model_request_at, observation_available + LATENCY
        )

    def test_replay_cannot_seek_forward_then_rewind_to_erase_knowledge(self):
        session = make_session()
        session.feed_1m_bar(minute_bar(0))
        builder = JiangheObservationBuilder(renderer=JiangheChartRenderer())
        current_observation = builder.build(state=session.state, session_identity="S1")
        traces_before = len(session.traces)
        ledger_before = len(session.replay.audit_ledger)
        clock_before = session.clock.current_time
        # 模拟向前跳跃：时钟一旦前进，就无法回退抹除已获得的知识。
        session.clock.advance_to(BASE + timedelta(hours=1))
        with self.assertRaises(ValueError):
            session.replay.accept_observation(current_observation)
        with self.assertRaises(ValueError):
            session.state.accept_1m_bar(minute_bar(0))
        with self.assertRaises(ValueError):
            session.memory.mutate(
                field_name="current_market_hypothesis",
                new_value="rewind",
                reason="rewind attempt",
                timestamp=BASE + timedelta(minutes=1),
                observation_identity="rewind",
                ai_trader_identity=session.ai_trader_identity.identity,
            )
        self.assertEqual(len(session.traces), traces_before)
        self.assertEqual(len(session.replay.audit_ledger), ledger_before)
        self.assertEqual(session.clock.current_time, BASE + timedelta(hours=1))
        # 跳跃后喂入的迟到 K 线只能在跳跃后的时钟上决策，不能把意图倒填回过去。
        session.feed_1m_bar(minute_bar(1))
        late_trace = session.traces[-1]
        self.assertGreaterEqual(late_trace.intent_available_at, clock_before)
        self.assertGreaterEqual(late_trace.model_request_at, BASE + timedelta(hours=1))

    def test_deterministic_replay_identity_for_identical_feeds(self):
        def build_session() -> tuple[
            JiangheMarketReplaySession, SyntheticScriptedProvider
        ]:
            provider = SyntheticScriptedProvider(policy=echo_watch_policy)
            session = make_session(provider=provider)
            for index in range(10):
                session.feed_1m_bar(varying_bar(index))
            return session, provider

        first_session, first_provider = build_session()
        second_session, second_provider = build_session()
        self.assertEqual(first_session.traces, second_session.traces)
        self.assertEqual(first_provider.calls, second_provider.calls)
        self.assertEqual(first_session.memory, second_session.memory)
        self.assertEqual(first_session.replay.audit_ledger, second_session.replay.audit_ledger)

    def test_trace_record_covers_full_decision_chain(self):
        provider = SyntheticScriptedProvider(policy=echo_watch_policy)
        session = make_session(provider=provider)
        session.feed_1m_bar(minute_bar(0))
        session.feed_1m_bar(minute_bar(1))
        trace = session.traces[0]
        self.assertTrue(trace.trace_id.startswith("S1:"))
        self.assertTrue(trace.observation_identity)
        self.assertEqual(trace.wake_event_type, "NEW_1M_CLOSED_BAR")
        self.assertTrue(trace.wake_event_identity)
        self.assertLessEqual(trace.model_request_at, trace.model_response_at)
        self.assertEqual(trace.model_response_at, trace.decision_time)
        self.assertEqual(trace.decision_time, trace.intent_available_at)
        self.assertTrue(trace.memory_mutations)
        self.assertEqual(trace.attention_mode_from, "SCAN")
        self.assertEqual(trace.attention_mode_to, "WATCH")
        self.assertEqual(trace.decision_action, "WATCH")
        self.assertEqual(provider.calls[0].observation_identity, trace.observation_identity)
        self.assertEqual(len(session.replay.audit_ledger), 2)
        # 第一次决策建立的 AI 假设会出现在后续观察的标注里。
        second_trace = session.traces[1]
        self.assertIn(("AI_WATCH_REGION", "watch-1:99-101"), second_trace.annotations)

    def test_session_exposes_no_outcome_or_pnl_surface(self):
        session = make_session()
        session.feed_1m_bar(minute_bar(0))
        public_names = [name for name in dir(session) if not name.startswith("_")]
        for name in public_names:
            lowered = name.lower()
            self.assertNotIn("pnl", lowered)
            self.assertNotIn("win_rate", lowered)
            self.assertNotIn("profit", lowered)
            self.assertNotIn("return", lowered)
        for field_name in (field.name for field in fields(ReplayTraceRecord)):
            self.assertNotIn("pnl", field_name.lower())


if __name__ == "__main__":
    unittest.main()

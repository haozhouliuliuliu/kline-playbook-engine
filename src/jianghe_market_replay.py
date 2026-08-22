"""江河 AI 观察与市场回放工程 V0.2（厂商中立、非结果）。

本模块建立在 ``src/jianghe_ai_trader.py`` 的 V0.1 冻结基础之上，绝不重复造第二套
模型层：

- ``RollingMarketState``：连续接收已收盘 1 分钟 K 线，因果聚合到 5m/15m/1h；
  每根 K 线带 ``available_at`` / ``is_closed``（部分桶以当前已见范围作为收盘边界）。
- ``JiangheObservationBuilder``：生成统一多周期时间点观察；持仓与订单事实可见，
  金额盈亏从不进入观察。
- ``WakeScheduler``：把行情、AI 假设与外部事件映射为 V0.1 的十一种唤醒类型。
- ``JiangheMarketReplaySession``：单向前进的历史回放会话；会话内保留 Working
  Memory；模型延迟把最早 ``intent_available_at`` 推迟到响应之后；追踪记录只追加。

本模块不连接真实模型、券商或账户，也不计算任何 PnL、胜率或收益。
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from typing import Callable, Mapping, Sequence

from src.jianghe_ai_trader import (
    AITraderProvider,
    AttentionMode,
    ChartRender,
    DecisionAction,
    DecisionAuditRecord,
    Direction,
    JiangheAITraderIdentity,
    JiangheDecision,
    JiangheMarketReplay,
    JiangheObservation,
    JiangheWorkingMemory,
    MemoryMutation,
    ObservationBar,
    ObservationIdentity,
    PositionFact,
    ReplayClock,
    StrategyFamily,
    WakeEvent,
    WakeEventType,
    WatchRegion,
    validate_transition,
)
from src.jianghe_chart_renderer import (
    DEFAULT_WINDOW_SIZES,
    ChartOverlay,
    JiangheChartRenderer,
    SUPPORTED_TIMEFRAMES,
)


_TIMEFRAME_SECONDS: dict[str, int] = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600}
_AGGREGATED_TIMEFRAMES: tuple[str, ...] = ("5m", "15m", "1h")
_EXTERNAL_WAKE_EVENTS: frozenset[WakeEventType] = frozenset(
    {
        WakeEventType.ORDER_EVENT,
        WakeEventType.POSITION_EVENT,
        WakeEventType.SAFETY_EVENT,
        WakeEventType.SESSION_EVENT,
    }
)
DEFAULT_WAKE_POLICY: frozenset[WakeEventType] = frozenset(WakeEventType)
SYNTHETIC_MODEL_LATENCY_DEFAULT = timedelta(seconds=2)


def _require_aware(value: datetime, field_name: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} 必须是带时区的时间")


def _decimal(value: str, field_name: str) -> Decimal:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} 必须是非空数字字符串")
    try:
        result = Decimal(value)
    except InvalidOperation:
        raise ValueError(f"{field_name} 不是有效数字字符串: {value!r}") from None
    if not result.is_finite():
        raise ValueError(f"{field_name} 必须是有限数字: {value!r}")
    return result


def _format_decimal(value: Decimal) -> str:
    return format(value.normalize(), "f")


def _floor_epoch(value: datetime, seconds: int) -> datetime:
    epoch = int(value.timestamp())
    floored = (epoch // seconds) * seconds
    return datetime.fromtimestamp(floored, tz=value.tzinfo)


@dataclass
class _BucketAccumulator:
    """某个高周期桶的因果累积器；只包含已经收到的 1 分钟成分。"""

    timeframe: str
    open_time: datetime
    close_time: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: Decimal
    constituent_count: int
    last_constituent_close: datetime
    available_at: datetime
    is_closed: bool = False

    def accept_constituent(self, bar: ObservationBar) -> None:
        high = _decimal(bar.high_price, "high_price")
        low = _decimal(bar.low_price, "low_price")
        close = _decimal(bar.close_price, "close_price")
        volume = _decimal(bar.volume, "volume")
        self.high_price = max(self.high_price, high)
        self.low_price = min(self.low_price, low)
        self.close_price = close
        self.volume = self.volume + volume
        self.constituent_count += 1
        self.last_constituent_close = bar.close_time
        self.available_at = max(self.available_at, bar.available_at)

    def mark_closed(self, closed_by_bar: ObservationBar) -> None:
        self.is_closed = True
        self.available_at = max(self.available_at, closed_by_bar.available_at)

    def as_observation_bar(self) -> ObservationBar:
        close_time = self.close_time if self.is_closed else self.last_constituent_close
        return ObservationBar(
            timeframe=self.timeframe,
            open_time=self.open_time,
            close_time=close_time,
            available_at=self.available_at,
            open_price=_format_decimal(self.open_price),
            high_price=_format_decimal(self.high_price),
            low_price=_format_decimal(self.low_price),
            close_price=_format_decimal(self.close_price),
            volume=_format_decimal(self.volume),
            is_closed=self.is_closed,
        )


class RollingMarketState:
    """连续接收已收盘 1 分钟 K 线并因果聚合到 5m/15m/1h；禁止未来数据。

    高周期桶只有在回放时钟（最近已见 1 分钟收盘时间）到达桶边界后才标记为已收盘；
    未收盘桶以最后一根成分 K 线的收盘时间作为当前已知范围（部分 K 线）。
    """

    def __init__(
        self,
        *,
        product: str,
        concrete_contract: str,
        mapping_identity: str,
        session_identity: str,
        window_sizes: Mapping[str, int] | None = None,
    ) -> None:
        for name, value in (
            ("product", product),
            ("concrete_contract", concrete_contract),
            ("mapping_identity", mapping_identity),
            ("session_identity", session_identity),
        ):
            if not value:
                raise ValueError(f"{name} 不能为空")
        merged = dict(DEFAULT_WINDOW_SIZES)
        if window_sizes is not None:
            for timeframe, size in window_sizes.items():
                if timeframe not in SUPPORTED_TIMEFRAMES:
                    raise ValueError(f"不支持或低于 1 分钟基线的周期: {timeframe}")
                if not isinstance(size, int) or size < 1:
                    raise ValueError("窗口大小必须是正整数")
                merged[timeframe] = size
        self.product = product
        self.concrete_contract = concrete_contract
        self.mapping_identity = mapping_identity
        self.session_identity = session_identity
        self.window_sizes: dict[str, int] = {tf: merged[tf] for tf in SUPPORTED_TIMEFRAMES}
        self._one_m_bars: list[ObservationBar] = []
        self._buckets: dict[str, dict[datetime, _BucketAccumulator]] = {
            tf: {} for tf in _AGGREGATED_TIMEFRAMES
        }
        self._closed_buckets: dict[str, list[_BucketAccumulator]] = {
            tf: [] for tf in _AGGREGATED_TIMEFRAMES
        }

    @property
    def current_time(self) -> datetime | None:
        return self._one_m_bars[-1].close_time if self._one_m_bars else None

    def accept_1m_bar(self, bar: ObservationBar) -> tuple[str, ...]:
        """接收一根已收盘 1 分钟 K 线；返回本次随之收盘的周期集合。"""
        if not isinstance(bar, ObservationBar):
            raise TypeError("bar 必须是 ObservationBar")
        if bar.timeframe != "1m":
            raise ValueError("滚动市场状态只接受 1 分钟 K 线")
        if not bar.is_closed:
            raise ValueError("1 分钟基线只接受已收盘 K 线；不伪造盘中或亚分钟状态")
        if bar.open_time.second or bar.open_time.microsecond or bar.close_time.second or bar.close_time.microsecond:
            raise ValueError("1 分钟 K 线必须对齐到分钟边界；不能伪造亚分钟序列")
        if bar.close_time - bar.open_time != timedelta(minutes=1):
            raise ValueError("1 分钟 K 线必须恰好跨越一分钟")
        if self._one_m_bars and bar.close_time <= self._one_m_bars[-1].close_time:
            raise ValueError("滚动市场状态拒绝倒退或重复的 1 分钟 K 线")
        self._one_m_bars.append(bar)
        for timeframe in _AGGREGATED_TIMEFRAMES:
            seconds = _TIMEFRAME_SECONDS[timeframe]
            bucket_start = _floor_epoch(bar.open_time, seconds)
            bucket = self._buckets[timeframe].get(bucket_start)
            if bucket is None:
                bucket = _BucketAccumulator(
                    timeframe=timeframe,
                    open_time=bucket_start,
                    close_time=bucket_start + timedelta(seconds=seconds),
                    open_price=_decimal(bar.open_price, "open_price"),
                    high_price=_decimal(bar.high_price, "high_price"),
                    low_price=_decimal(bar.low_price, "low_price"),
                    close_price=_decimal(bar.close_price, "close_price"),
                    volume=_decimal(bar.volume, "volume"),
                    constituent_count=1,
                    last_constituent_close=bar.close_time,
                    available_at=bar.available_at,
                )
                self._buckets[timeframe][bucket_start] = bucket
            else:
                bucket.accept_constituent(bar)
        newly_closed: list[str] = ["1m"]
        for timeframe in _AGGREGATED_TIMEFRAMES:
            closable = sorted(
                (
                    bucket
                    for bucket in self._buckets[timeframe].values()
                    if not bucket.is_closed and bucket.close_time <= bar.close_time
                ),
                key=lambda bucket: bucket.close_time,
            )
            for bucket in closable:
                bucket.mark_closed(bar)
                self._closed_buckets[timeframe].append(bucket)
                if timeframe not in newly_closed:
                    newly_closed.append(timeframe)
        return tuple(newly_closed)

    def closed_bars(self, timeframe: str, *, limit: int) -> tuple[ObservationBar, ...]:
        if timeframe not in _TIMEFRAME_SECONDS:
            raise ValueError(f"不支持或低于 1 分钟基线的周期: {timeframe}")
        if not isinstance(limit, int) or limit < 1:
            raise ValueError("limit 必须是正整数")
        if timeframe == "1m":
            return tuple(self._one_m_bars[-limit:])
        return tuple(bucket.as_observation_bar() for bucket in self._closed_buckets[timeframe][-limit:])

    def partial_bar(self, timeframe: str) -> ObservationBar | None:
        if timeframe not in _TIMEFRAME_SECONDS:
            raise ValueError(f"不支持或低于 1 分钟基线的周期: {timeframe}")
        if timeframe == "1m":
            return None
        open_buckets = [bucket for bucket in self._buckets[timeframe].values() if not bucket.is_closed]
        if not open_buckets:
            return None
        latest = max(open_buckets, key=lambda bucket: bucket.open_time)
        return latest.as_observation_bar()

    def snapshot(self, timeframe: str, *, limit: int) -> tuple[ObservationBar, ...]:
        bars = list(self.closed_bars(timeframe, limit=limit))
        partial = self.partial_bar(timeframe)
        if partial is not None:
            bars.append(partial)
        return tuple(bars)


@dataclass(frozen=True)
class InvalidationLevel:
    """AI 失效位假设（数值层级）；与市场事实严格分离。"""

    level_id: str
    price: str
    created_at: datetime
    expires_at: datetime
    reason: str

    def __post_init__(self) -> None:
        _require_aware(self.created_at, "created_at")
        _require_aware(self.expires_at, "expires_at")
        if not self.level_id or not self.price or not self.reason:
            raise ValueError("失效位字段不能为空")
        if self.expires_at <= self.created_at:
            raise ValueError("失效位有效期无效")
        _decimal(self.price, "price")

    @property
    def price_value(self) -> Decimal:
        return Decimal(self.price)

    def is_active(self, at: datetime) -> bool:
        return self.created_at <= at < self.expires_at


class WakeScheduler:
    """把行情事实、AI 假设与外部事件映射为 V0.1 唤醒类型；不含任何结果语义。"""

    def __init__(self) -> None:
        self._last_close_price: Decimal | None = None

    @staticmethod
    def _identity(event_type: WakeEventType, occurred_at: datetime, context: str) -> str:
        return f"{event_type.value}:{occurred_at.isoformat()}:{context}"

    def evaluate_market_wake(
        self,
        *,
        bar: ObservationBar,
        newly_closed_timeframes: Sequence[str],
        watch_regions: Sequence[WatchRegion],
        invalidation_levels: Sequence[InvalidationLevel],
    ) -> tuple[WakeEvent, ...]:
        occurred = bar.available_at
        events: list[WakeEvent] = []
        for timeframe in SUPPORTED_TIMEFRAMES:
            if timeframe in newly_closed_timeframes:
                event_type = WakeEventType[f"NEW_{timeframe.upper()}_CLOSED_BAR"]
                events.append(
                    WakeEvent(
                        event_type,
                        occurred,
                        self._identity(event_type, occurred, f"bar_close={bar.close_time.isoformat()}"),
                    )
                )
        price = _decimal(bar.close_price, "close_price")
        previous = self._last_close_price
        if previous is not None:
            for region in sorted(watch_regions, key=lambda item: item.region_id):
                if not (region.created_at <= occurred < region.expires_at):
                    continue
                lower = _decimal(region.lower_bound, "lower_bound")
                upper = _decimal(region.upper_bound, "upper_bound")
                inside_before = lower <= previous <= upper
                inside_now = lower <= price <= upper
                if inside_now and not inside_before:
                    event_type = WakeEventType.PRICE_ENTERS_AI_WATCH_REGION
                    events.append(
                        WakeEvent(
                            event_type,
                            occurred,
                            self._identity(event_type, occurred, f"region={region.region_id}"),
                        )
                    )
                elif inside_before and not inside_now:
                    event_type = WakeEventType.PRICE_EXITS_AI_WATCH_REGION
                    events.append(
                        WakeEvent(
                            event_type,
                            occurred,
                            self._identity(event_type, occurred, f"region={region.region_id}"),
                        )
                    )
        bar_low = _decimal(bar.low_price, "low_price")
        bar_high = _decimal(bar.high_price, "high_price")
        for level in sorted(invalidation_levels, key=lambda item: item.level_id):
            if not level.is_active(occurred):
                continue
            if bar_low <= level.price_value <= bar_high:
                event_type = WakeEventType.AI_INVALIDATION_LEVEL_TOUCHED
                events.append(
                    WakeEvent(
                        event_type,
                        occurred,
                        self._identity(event_type, occurred, f"level={level.level_id}"),
                    )
                )
        self._last_close_price = price
        return tuple(events)

    def emit_external(self, *, event_type: WakeEventType, occurred_at: datetime, context: str) -> WakeEvent:
        if event_type not in _EXTERNAL_WAKE_EVENTS:
            raise ValueError("外部唤醒只允许 ORDER/POSITION/SAFETY/SESSION 事件")
        _require_aware(occurred_at, "occurred_at")
        if not context:
            raise ValueError("外部唤醒上下文不能为空")
        return WakeEvent(event_type, occurred_at, self._identity(event_type, occurred_at, context))


class JiangheObservationBuilder:
    """从滚动市场状态构建统一多周期时间点观察；金额盈亏从不进入观察。"""

    def __init__(
        self,
        *,
        renderer: JiangheChartRenderer,
        schema_version: str = "JIANGHE_OBSERVATION_V0_1",
    ) -> None:
        if not isinstance(renderer, JiangheChartRenderer):
            raise TypeError("renderer 必须是 JiangheChartRenderer")
        if not schema_version:
            raise ValueError("观察模式版本不能为空")
        self.renderer = renderer
        self.schema_version = schema_version

    def earliest_decision_time(self, state: RollingMarketState) -> datetime:
        """给定窗口下最早合法决策时间：不早于任何已选 K 线的可用时间。"""
        current = state.current_time
        if current is None:
            raise ValueError("滚动市场状态还没有已收盘的 1 分钟 K 线")
        latest_availability = current
        for timeframe in SUPPORTED_TIMEFRAMES:
            for bar in state.snapshot(timeframe, limit=self.renderer.window_sizes[timeframe]):
                if bar.available_at > latest_availability:
                    latest_availability = bar.available_at
        return latest_availability

    def build(
        self,
        *,
        state: RollingMarketState,
        decision_time: datetime | None = None,
        exchange_time: datetime | None = None,
        positions: Sequence[PositionFact] = (),
        active_order_ids: Sequence[str] = (),
        session_identity: str,
        overlays: Sequence[ChartOverlay] = (),
    ) -> JiangheObservation:
        if not session_identity:
            raise ValueError("会话身份不能为空")
        earliest = self.earliest_decision_time(state)
        if decision_time is None:
            decision = earliest
        else:
            _require_aware(decision_time, "decision_time")
            if decision_time < earliest:
                raise ValueError("观察决策时间早于 K 线可用时间；不能使用未来数据")
            decision = decision_time
        exchange = exchange_time if exchange_time is not None else state.current_time
        _require_aware(exchange, "exchange_time")
        if exchange > decision:
            raise ValueError("交易所时间不能晚于决策时间")
        bars: list[ObservationBar] = []
        charts: list[ChartRender] = []
        for timeframe in SUPPORTED_TIMEFRAMES:
            timeframe_bars = state.snapshot(timeframe, limit=self.renderer.window_sizes[timeframe])
            if not timeframe_bars:
                continue
            rendered = self.renderer.render(
                timeframe=timeframe,
                bars=timeframe_bars,
                product=state.product,
                concrete_contract=state.concrete_contract,
                current_time=exchange,
                overlays=overlays,
            )
            charts.append(rendered.to_chart_render())
            bars.extend(timeframe_bars)
        identity = ObservationIdentity(
            decision,
            exchange,
            state.product,
            state.concrete_contract,
            state.mapping_identity,
            session_identity,
        )
        return JiangheObservation(
            identity=identity,
            bars=tuple(bars),
            positions=tuple(positions),
            active_order_ids=tuple(active_order_ids),
            charts=tuple(charts),
            schema_version=self.schema_version,
        )


@dataclass
class JiangheMarketReplayV0_2(JiangheMarketReplay):
    """V0.2 回放：允许由已收盘 1 分钟 K 线因果聚合出的高周期部分桶进入观察。

    V0.1 的 ``accept_observation`` 拒绝一切部分 K 线，用于防止伪造盘中状态；V0.2
    的观察工程明确要求高周期部分桶带部分标记进入观察（研究协议 V0.1：观察包含
    每根 K 线的部分/完整标志）。两者共享同一单向时钟、决策校验和审计账本语义；
    1 分钟基线本身仍然只接受已收盘 K 线（由 ``RollingMarketState`` 强制），不从
    OHLCV 伪造亚分钟序列。
    """

    def accept_observation(self, observation: JiangheObservation) -> None:
        for bar in observation.bars:
            if bar.timeframe == "1m" and not bar.is_closed:
                raise ValueError("1 分钟基线不接受部分 1 分钟 K 线")
        if observation.identity.decision_time < self.clock.current_time:
            raise ValueError("回放不能接受过去的观察")
        self.clock.advance_to(observation.identity.decision_time)


@dataclass(frozen=True)
class SyntheticProviderCall:
    """合成提供者每次调用所见内容的审计快照。"""

    observation_identity: str
    attention_mode_before: str
    watch_region_ids_before: tuple[str, ...]
    chart_annotation_kinds: tuple[str, ...]
    raw_response: str


class SyntheticScriptedProvider:
    """合成脚本提供者：没有真实模型，决策来自确定性的脚本策略。"""

    provider_identity = "SYNTHETIC_SCRIPTED_V0_1"

    def __init__(
        self,
        policy: Callable[[JiangheObservation, JiangheWorkingMemory], tuple[str, JiangheDecision]] | None = None,
    ) -> None:
        self._policy = policy if policy is not None else self._default_policy
        self.calls: list[SyntheticProviderCall] = []

    @staticmethod
    def _default_policy(
        observation: JiangheObservation, memory: JiangheWorkingMemory
    ) -> tuple[str, JiangheDecision]:
        return "synthetic:default-wait", JiangheDecision(
            attention_mode=AttentionMode.SCAN,
            family=StrategyFamily.NONE,
            direction=Direction.NONE,
            action=DecisionAction.WAIT,
            uncertainty="SYNTHETIC_DEFAULT",
        )

    def decide(self, observation: JiangheObservation, memory: JiangheWorkingMemory) -> tuple[str, JiangheDecision]:
        raw, decision = self._policy(observation, memory)
        self.calls.append(
            SyntheticProviderCall(
                observation_identity=observation.identity.identity,
                attention_mode_before=memory.attention_mode.value,
                watch_region_ids_before=tuple(sorted(region.region_id for region in memory.watch_regions)),
                chart_annotation_kinds=tuple(
                    sorted({kind for chart in observation.charts for kind, _ in chart.annotations})
                ),
                raw_response=raw,
            )
        )
        return raw, decision


@dataclass(frozen=True)
class ReplayTraceRecord:
    """一次模型调用的回放追踪记录：观察、唤醒、延迟链、记忆与注意力迁移。"""

    trace_id: str
    session_id: str
    observation_identity: str
    wake_event_type: str
    wake_event_identity: str
    model_request_at: datetime
    model_response_at: datetime
    decision_time: datetime
    intent_available_at: datetime
    memory_mutations: tuple[MemoryMutation, ...]
    annotations: tuple[tuple[str, str], ...]
    attention_mode_from: str
    attention_mode_to: str
    decision_action: str


@dataclass(frozen=True)
class ArchivedReplaySession:
    """会话切换后归档的会话记忆快照；知识只追加，不抹除。"""

    session_id: str
    memory: JiangheWorkingMemory
    trace_count: int
    ended_at: datetime


class JiangheMarketReplaySession:
    """单向前进的市场回放会话。

    时间只能向前：回放时钟只通过已接受的观察与决策推进；模型延迟把最早
    ``intent_available_at`` 推迟到响应时间之后。会话内保留 Working Memory，
    AI 可通过决策留下/修改 watch regions 与失效位。追踪记录与会话归档只追加。
    本类不提供任何 PnL、胜率或收益计算。
    """

    def __init__(
        self,
        *,
        session_id: str,
        state: RollingMarketState,
        provider: AITraderProvider,
        ai_trader_identity: JiangheAITraderIdentity,
        renderer: JiangheChartRenderer | None = None,
        synthetic_model_latency: timedelta = SYNTHETIC_MODEL_LATENCY_DEFAULT,
        wake_policy: frozenset[WakeEventType] = DEFAULT_WAKE_POLICY,
        clock_start: datetime | None = None,
    ) -> None:
        if not session_id:
            raise ValueError("会话身份不能为空")
        if not isinstance(state, RollingMarketState):
            raise TypeError("state 必须是 RollingMarketState")
        if not hasattr(provider, "decide"):
            raise TypeError("provider 必须实现 decide")
        if not isinstance(ai_trader_identity, JiangheAITraderIdentity):
            raise TypeError("ai_trader_identity 必须是 JiangheAITraderIdentity")
        if not isinstance(synthetic_model_latency, timedelta) or synthetic_model_latency < timedelta(0):
            raise ValueError("合成模型延迟必须是非负时间差")
        if wake_policy is None:
            wake_policy = DEFAULT_WAKE_POLICY
        if not all(isinstance(event_type, WakeEventType) for event_type in wake_policy):
            raise ValueError("唤醒策略只能包含 WakeEventType 成员")
        start = clock_start if clock_start is not None else state.current_time
        if start is None:
            raise ValueError("滚动市场状态为空时必须提供 clock_start")
        _require_aware(start, "clock_start")
        self.session_id = session_id
        self.state = state
        self.provider = provider
        self.ai_trader_identity = ai_trader_identity
        self.renderer = renderer if renderer is not None else JiangheChartRenderer()
        self.builder = JiangheObservationBuilder(renderer=self.renderer)
        self.synthetic_model_latency = synthetic_model_latency
        self.wake_policy = frozenset(wake_policy)
        self.replay = JiangheMarketReplayV0_2(ReplayClock(start))
        self.scheduler = WakeScheduler()
        self.invalidation_levels: tuple[InvalidationLevel, ...] = ()
        self.position_facts: tuple[PositionFact, ...] = ()
        self.active_order_ids: tuple[str, ...] = ()
        self.traces: list[ReplayTraceRecord] = []
        self.archived_sessions: tuple[ArchivedReplaySession, ...] = ()
        self._trace_counter = 0

    @property
    def memory(self) -> JiangheWorkingMemory:
        return self.replay.memory

    @property
    def clock(self) -> ReplayClock:
        return self.replay.clock

    def feed_1m_bar(self, bar: ObservationBar) -> tuple[WakeEvent, ...]:
        """喂入一根已收盘 1 分钟 K 线；返回本次产生的唤醒事件。"""
        newly_closed = self.state.accept_1m_bar(bar)
        expire_at = max(bar.available_at, self.replay.clock.current_time)
        self._expire_hypotheses(at=expire_at, marker=f"BAR_1M:{bar.open_time.isoformat()}")
        events = self.scheduler.evaluate_market_wake(
            bar=bar,
            newly_closed_timeframes=newly_closed,
            watch_regions=self.replay.memory.watch_regions,
            invalidation_levels=self.invalidation_levels,
        )
        for event in events:
            if event.event_type in self.wake_policy:
                self._run_decision_cycle(event)
        return events

    def emit_external_wake(
        self, event_type: WakeEventType, *, occurred_at: datetime, context: str
    ) -> WakeEvent:
        """注入 ORDER/POSITION/SAFETY/SESSION 外部事件；时间不得早于回放时钟。"""
        _require_aware(occurred_at, "occurred_at")
        if occurred_at < self.replay.clock.current_time:
            raise ValueError("外部唤醒事件时间不能早于回放时钟")
        event = self.scheduler.emit_external(
            event_type=event_type, occurred_at=occurred_at, context=context
        )
        if event.event_type in self.wake_policy:
            self._run_decision_cycle(event)
        return event

    def set_ai_watch_regions(
        self, regions: Sequence[WatchRegion], *, reason: str, timestamp: datetime | None = None
    ) -> None:
        at = timestamp if timestamp is not None else self.replay.clock.current_time
        _require_aware(at, "timestamp")
        self.replay.memory = self.replay.memory.mutate(
            field_name="watch_regions",
            new_value=tuple(regions),
            reason=reason or "AI_SET_WATCH_REGIONS",
            timestamp=at,
            observation_identity=f"SESSION:{self.session_id}",
            ai_trader_identity=self.ai_trader_identity.identity,
        )

    def set_ai_invalidation_levels(
        self, levels: Sequence[InvalidationLevel], *, reason: str, timestamp: datetime | None = None
    ) -> None:
        at = timestamp if timestamp is not None else self.replay.clock.current_time
        _require_aware(at, "timestamp")
        levels = tuple(levels)
        summary = ";".join(f"{level.level_id}@{level.price}" for level in levels) or "NONE"
        self.invalidation_levels = levels
        self.replay.memory = self.replay.memory.mutate(
            field_name="invalidation_hypothesis",
            new_value=summary,
            reason=reason or "AI_SET_INVALIDATION_LEVELS",
            timestamp=at,
            observation_identity=f"SESSION:{self.session_id}",
            ai_trader_identity=self.ai_trader_identity.identity,
        )

    def update_position_facts(
        self,
        *,
        positions: Sequence[PositionFact] = (),
        active_order_ids: Sequence[str] = (),
    ) -> None:
        """由确定性外部系统更新持仓/订单事实；不引入任何金额盈亏。"""
        self.position_facts = tuple(positions)
        self.active_order_ids = tuple(active_order_ids)

    def roll_to_new_session(self, new_session_id: str) -> ArchivedReplaySession:
        """归档当前会话记忆并按设计重置：新会话从 SCAN 重新开始，时钟继续前进。"""
        if not new_session_id:
            raise ValueError("新会话身份不能为空")
        archived = ArchivedReplaySession(
            session_id=self.session_id,
            memory=self.replay.memory,
            trace_count=len(self.traces),
            ended_at=self.replay.clock.current_time,
        )
        self.archived_sessions = self.archived_sessions + (archived,)
        self.session_id = new_session_id
        self.replay.memory = JiangheWorkingMemory()
        self.scheduler = WakeScheduler()
        self.invalidation_levels = ()
        return archived

    def _expire_hypotheses(self, *, at: datetime, marker: str) -> None:
        memory = self.replay.memory.expire_watch_regions(
            at, marker, self.ai_trader_identity.identity
        )
        if memory is not self.replay.memory:
            self.replay.memory = memory
        active_levels = tuple(level for level in self.invalidation_levels if level.expires_at > at)
        if active_levels != self.invalidation_levels:
            self.invalidation_levels = active_levels
            summary = ";".join(f"{level.level_id}@{level.price}" for level in active_levels) or "NONE"
            self.replay.memory = self.replay.memory.mutate(
                field_name="invalidation_hypothesis",
                new_value=summary,
                reason="INVALIDATION_LEVEL_EXPIRED",
                timestamp=at,
                observation_identity=marker,
                ai_trader_identity=self.ai_trader_identity.identity,
            )

    def _current_overlays(self) -> tuple[ChartOverlay, ...]:
        overlays = [
            ChartOverlay(
                kind="AI_WATCH_REGION",
                lower_bound=region.lower_bound,
                upper_bound=region.upper_bound,
                label=region.region_id,
            )
            for region in self.replay.memory.watch_regions
        ]
        overlays.extend(
            ChartOverlay(
                kind="AI_DEFENSE_INTERPRETATION",
                lower_bound=level.price,
                upper_bound=level.price,
                label=level.level_id,
            )
            for level in self.invalidation_levels
        )
        return tuple(sorted(overlays, key=lambda overlay: (overlay.kind, overlay.label)))

    def _run_decision_cycle(self, wake_event: WakeEvent) -> ReplayTraceRecord:
        decision_time = max(
            self.builder.earliest_decision_time(self.state),
            self.replay.clock.current_time,
        )
        observation = self.builder.build(
            state=self.state,
            decision_time=decision_time,
            positions=self.position_facts,
            active_order_ids=self.active_order_ids,
            session_identity=self.session_id,
            overlays=self._current_overlays(),
        )
        self.replay.accept_observation(observation)
        attention_from = self.replay.memory.attention_mode
        request_at = max(
            observation.identity.decision_time,
            self.replay.clock.current_time,
            wake_event.occurred_at,
        )
        response_at = request_at + self.synthetic_model_latency
        decision_at = response_at
        intent_at = response_at
        raw, decision = self.provider.decide(observation, self.replay.memory)
        new_mode = validate_transition(attention_from, decision)
        mutations: list[MemoryMutation] = []
        memory = self.replay.memory

        def apply(field_name: str, new_value: object, reason: str) -> None:
            nonlocal memory
            if getattr(memory, field_name) != new_value:
                memory = memory.mutate(
                    field_name=field_name,
                    new_value=new_value,
                    reason=reason,
                    timestamp=intent_at,
                    observation_identity=observation.identity.identity,
                    ai_trader_identity=self.ai_trader_identity.identity,
                )
                mutations.append(memory.mutation_history[-1])

        apply("attention_mode", decision.attention_mode, f"DECISION_{decision.action.value}")
        apply("watch_regions", decision.watch_regions, "DECISION_WATCH_REGIONS")
        apply("last_meaningful_decision", decision.action.value, "DECISION_ACTION")
        apply("transition_reason", decision.rationale, "DECISION_RATIONALE")
        self.replay.memory = memory
        audit = DecisionAuditRecord(
            observation_identity=observation.identity.identity,
            ai_trader_identity=self.ai_trader_identity.identity,
            raw_response=raw,
            normalized_decision=decision,
            observation_available_at=observation.identity.decision_time,
            model_request_at=request_at,
            model_response_at=response_at,
            normalized_decision_at=decision_at,
            intent_available_at=intent_at,
        )
        self.replay.record_decision(audit)
        annotations = tuple(
            sorted({(kind, note) for chart in observation.charts for kind, note in chart.annotations})
        )
        self._trace_counter += 1
        trace = ReplayTraceRecord(
            trace_id=f"{self.session_id}:{self._trace_counter:06d}",
            session_id=self.session_id,
            observation_identity=observation.identity.identity,
            wake_event_type=wake_event.event_type.value,
            wake_event_identity=wake_event.identity,
            model_request_at=request_at,
            model_response_at=response_at,
            decision_time=decision_at,
            intent_available_at=intent_at,
            memory_mutations=tuple(mutations),
            annotations=annotations,
            attention_mode_from=attention_from.value,
            attention_mode_to=new_mode.value,
            decision_action=decision.action.value,
        )
        self.traces.append(trace)
        return trace

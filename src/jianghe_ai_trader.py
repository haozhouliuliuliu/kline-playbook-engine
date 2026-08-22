"""江河 AI 交易员的非结果基础类型。

本模块只定义可审计的观察、记忆、决策和历史回放边界。它不连接模型、行情、
券商或账户，也不计算任何候选策略的收益结果。
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from enum import Enum
from hashlib import sha256
import json
from typing import Mapping, Protocol, Sequence


def _canonical_hash(value: object) -> str:
    """用稳定 JSON 生成身份，故不依赖工作目录、文件路径或修改时间。"""
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _require_aware(value: datetime, field_name: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} 必须是带时区的时间")


class AttentionMode(str, Enum):
    SCAN = "SCAN"
    WATCH = "WATCH"
    CANDIDATE = "CANDIDATE"
    IN_POSITION = "IN_POSITION"
    COOLDOWN = "COOLDOWN"
    SUSPENDED = "SUSPENDED"


class WakeEventType(str, Enum):
    NEW_1M_CLOSED_BAR = "NEW_1M_CLOSED_BAR"
    NEW_5M_CLOSED_BAR = "NEW_5M_CLOSED_BAR"
    NEW_15M_CLOSED_BAR = "NEW_15M_CLOSED_BAR"
    NEW_1H_CLOSED_BAR = "NEW_1H_CLOSED_BAR"
    PRICE_ENTERS_AI_WATCH_REGION = "PRICE_ENTERS_AI_WATCH_REGION"
    PRICE_EXITS_AI_WATCH_REGION = "PRICE_EXITS_AI_WATCH_REGION"
    AI_INVALIDATION_LEVEL_TOUCHED = "AI_INVALIDATION_LEVEL_TOUCHED"
    ORDER_EVENT = "ORDER_EVENT"
    POSITION_EVENT = "POSITION_EVENT"
    SAFETY_EVENT = "SAFETY_EVENT"
    SESSION_EVENT = "SESSION_EVENT"


class DecisionAction(str, Enum):
    WAIT = "WAIT"
    NO_TRADE = "NO_TRADE"
    WATCH = "WATCH"
    CANDIDATE = "CANDIDATE"
    ENTER = "ENTER"
    MANAGE = "MANAGE"
    EXIT = "EXIT"


class Direction(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"
    NONE = "NONE"


class StrategyFamily(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    NONE = "NONE"


@dataclass(frozen=True)
class KnowledgePackIdentity:
    """由知识文件内容而非存放位置生成的江河知识包身份。"""

    pack_version: str
    document_hashes: tuple[tuple[str, str], ...]
    identity: str

    @classmethod
    def from_documents(cls, pack_version: str, documents: Mapping[str, str]) -> "KnowledgePackIdentity":
        if not pack_version or not documents:
            raise ValueError("知识包版本和文档内容不能为空")
        hashes = tuple(sorted((name, sha256(content.encode("utf-8")).hexdigest()) for name, content in documents.items()))
        if any(not name for name, _ in hashes):
            raise ValueError("知识包文档名不能为空")
        identity = _canonical_hash({"pack_version": pack_version, "document_hashes": hashes})
        return cls(pack_version=pack_version, document_hashes=hashes, identity=identity)


@dataclass(frozen=True)
class JiangheAITraderIdentity:
    """影响输出的 AI 交易员配置身份；所有模型厂商仍只是候选。"""

    knowledge_pack_identity: str
    model_provider: str
    model_id_version: str
    system_prompt_identity: str
    decision_prompt_identity: str
    context_selection_policy_identity: str
    memory_policy_identity: str
    chart_renderer_identity: str
    observation_schema_version: str
    wake_policy_version: str
    decision_schema_version: str
    inference_configuration: tuple[tuple[str, str], ...]
    tool_capability_set: tuple[str, ...]
    source_family_scope: tuple[str, ...]
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        required = (
            self.knowledge_pack_identity, self.model_provider, self.model_id_version,
            self.system_prompt_identity, self.decision_prompt_identity,
            self.context_selection_policy_identity, self.memory_policy_identity,
            self.chart_renderer_identity, self.observation_schema_version,
            self.wake_policy_version, self.decision_schema_version,
        )
        if not all(required):
            raise ValueError("AI 交易员身份字段不能为空")
        if set(self.source_family_scope) - {"A", "B", "C", "D"}:
            raise ValueError("来源家族范围只能是 A/B/C/D")
        if tuple(sorted(set(self.tool_capability_set))) != self.tool_capability_set:
            raise ValueError("工具能力必须排序且不重复")
        if tuple(sorted(set(self.inference_configuration))) != self.inference_configuration:
            raise ValueError("推理配置必须排序且不重复")
        object.__setattr__(self, "identity", _canonical_hash({
            "knowledge_pack_identity": self.knowledge_pack_identity,
            "model_provider": self.model_provider,
            "model_id_version": self.model_id_version,
            "system_prompt_identity": self.system_prompt_identity,
            "decision_prompt_identity": self.decision_prompt_identity,
            "context_selection_policy_identity": self.context_selection_policy_identity,
            "memory_policy_identity": self.memory_policy_identity,
            "chart_renderer_identity": self.chart_renderer_identity,
            "observation_schema_version": self.observation_schema_version,
            "wake_policy_version": self.wake_policy_version,
            "decision_schema_version": self.decision_schema_version,
            "inference_configuration": self.inference_configuration,
            "tool_capability_set": self.tool_capability_set,
            "source_family_scope": self.source_family_scope,
        }))


@dataclass(frozen=True)
class ObservationBar:
    timeframe: str
    open_time: datetime
    close_time: datetime
    available_at: datetime
    open_price: str
    high_price: str
    low_price: str
    close_price: str
    volume: str
    is_closed: bool

    def __post_init__(self) -> None:
        for field_name in ("open_time", "close_time", "available_at"):
            _require_aware(getattr(self, field_name), field_name)
        if not self.timeframe or self.close_time <= self.open_time:
            raise ValueError("K线周期或时间范围无效")
        if self.available_at < self.close_time:
            raise ValueError("K线 available_at 不能早于收盘时间")
        if not all(isinstance(value, str) and value for value in (
            self.open_price, self.high_price, self.low_price, self.close_price, self.volume
        )):
            raise ValueError("OHLCV 必须以非空字符串明确提供")


@dataclass(frozen=True)
class PositionFact:
    direction: Direction
    quantity: str
    entry_facts: tuple[tuple[str, str], ...]
    protective_orders: tuple[str, ...]
    active_order_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.direction is Direction.NONE or not self.quantity:
            raise ValueError("持仓必须有方向和数量")


@dataclass(frozen=True)
class ChartRender:
    """标准化图表元数据；图表事实与 AI 标注在不同字段中保存。"""

    renderer_identity: str
    timeframe: str
    window_definition: str
    current_time: datetime
    render_content_hash: str
    partial_bar_marked: bool
    annotations: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        _require_aware(self.current_time, "current_time")
        if not all((self.renderer_identity, self.timeframe, self.window_definition, self.render_content_hash)):
            raise ValueError("图表渲染元数据不能为空")
        allowed = {"AI_HYPOTHESIS_KEY_ZONE", "AI_WATCH_REGION", "AI_DEFENSE_INTERPRETATION"}
        if any(kind not in allowed for kind, _ in self.annotations):
            raise ValueError("图表标注必须是受支持的 AI 假设类型")


@dataclass(frozen=True)
class ObservationIdentity:
    decision_time: datetime
    exchange_time: datetime
    product: str
    concrete_contract: str
    mapping_identity: str
    session_identity: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_aware(self.decision_time, "decision_time")
        _require_aware(self.exchange_time, "exchange_time")
        if self.exchange_time > self.decision_time:
            raise ValueError("决策时间不能早于交易所时间")
        if not all((self.product, self.concrete_contract, self.mapping_identity, self.session_identity)):
            raise ValueError("观察身份字段不能为空")
        object.__setattr__(self, "identity", _canonical_hash({
            "decision_time": self.decision_time.isoformat(), "exchange_time": self.exchange_time.isoformat(),
            "product": self.product, "concrete_contract": self.concrete_contract,
            "mapping_identity": self.mapping_identity, "session_identity": self.session_identity,
        }))


@dataclass(frozen=True)
class JiangheObservation:
    identity: ObservationIdentity
    bars: tuple[ObservationBar, ...]
    positions: tuple[PositionFact, ...] = ()
    active_order_ids: tuple[str, ...] = ()
    charts: tuple[ChartRender, ...] = ()
    schema_version: str = "JIANGHE_OBSERVATION_V0_1"

    def __post_init__(self) -> None:
        if not self.bars:
            raise ValueError("观察至少需要一根 K 线")
        for bar in self.bars:
            if bar.available_at > self.identity.decision_time:
                raise ValueError("观察中包含当时不可用的未来 K 线")
            if bar.close_time > self.identity.exchange_time:
                raise ValueError("观察中包含超过交易所世界时钟的 K 线")
        for chart in self.charts:
            if chart.current_time > self.identity.exchange_time:
                raise ValueError("图表不得显示未来时间")
        # 金额盈亏故意不属于该类型；AI 只得到持仓和订单事实。

    @property
    def timeframes(self) -> tuple[str, ...]:
        return tuple(sorted({bar.timeframe for bar in self.bars}))


@dataclass(frozen=True)
class WakeEvent:
    event_type: WakeEventType
    occurred_at: datetime
    identity: str

    def __post_init__(self) -> None:
        _require_aware(self.occurred_at, "occurred_at")
        if not self.identity:
            raise ValueError("唤醒事件身份不能为空")


@dataclass(frozen=True)
class WatchRegion:
    region_id: str
    lower_bound: str
    upper_bound: str
    created_at: datetime
    expires_at: datetime
    reason: str

    def __post_init__(self) -> None:
        _require_aware(self.created_at, "created_at")
        _require_aware(self.expires_at, "expires_at")
        if not all((self.region_id, self.lower_bound, self.upper_bound, self.reason)) or self.expires_at <= self.created_at:
            raise ValueError("观察区间字段或有效期无效")


@dataclass(frozen=True)
class MemoryMutation:
    timestamp: datetime
    field_name: str
    previous_value: str | None
    new_value: str | None
    reason: str
    observation_identity: str
    ai_trader_identity: str

    def __post_init__(self) -> None:
        _require_aware(self.timestamp, "timestamp")
        if not all((self.field_name, self.reason, self.observation_identity, self.ai_trader_identity)):
            raise ValueError("记忆变更审计字段不能为空")


@dataclass(frozen=True)
class JiangheWorkingMemory:
    attention_mode: AttentionMode = AttentionMode.SCAN
    current_market_hypothesis: str | None = None
    timeframe_trend_view: tuple[tuple[str, str], ...] = ()
    directional_bias: Direction = Direction.NONE
    watch_regions: tuple[WatchRegion, ...] = ()
    key_location_hypotheses: tuple[str, ...] = ()
    active_family_hypothesis: StrategyFamily = StrategyFamily.NONE
    expected_trigger: str | None = None
    invalidation_hypothesis: str | None = None
    last_meaningful_decision: str | None = None
    open_questions: tuple[str, ...] = ()
    annotation_history: tuple[tuple[str, str], ...] = ()
    transition_reason: str | None = None
    review_at: datetime | None = None
    mutation_history: tuple[MemoryMutation, ...] = ()

    def mutate(
        self, *, field_name: str, new_value: object, reason: str, timestamp: datetime,
        observation_identity: str, ai_trader_identity: str,
    ) -> "JiangheWorkingMemory":
        if field_name not in self.__dataclass_fields__ or field_name == "mutation_history":
            raise ValueError("不允许变更未知或审计字段")
        _require_aware(timestamp, "timestamp")
        if self.mutation_history and timestamp < self.mutation_history[-1].timestamp:
            raise ValueError("记忆变更时间不能倒流")
        previous = getattr(self, field_name)
        mutation = MemoryMutation(timestamp, field_name, repr(previous), repr(new_value), reason, observation_identity, ai_trader_identity)
        return replace(self, **{field_name: new_value, "mutation_history": self.mutation_history + (mutation,)})

    def expire_watch_regions(self, at: datetime, observation_identity: str, ai_trader_identity: str) -> "JiangheWorkingMemory":
        _require_aware(at, "at")
        active = tuple(region for region in self.watch_regions if region.expires_at > at)
        if active == self.watch_regions:
            return self
        return self.mutate(field_name="watch_regions", new_value=active, reason="WATCH_REGION_EXPIRED", timestamp=at,
                           observation_identity=observation_identity, ai_trader_identity=ai_trader_identity)


@dataclass(frozen=True)
class ConstrainedTradeIntent:
    """AI 只能提出意图；数量、风控上限和订单生命周期仍归确定性系统。"""

    direction: Direction
    intent_type: str
    rationale_reference: str

    def __post_init__(self) -> None:
        if self.direction is Direction.NONE or not self.intent_type or not self.rationale_reference:
            raise ValueError("交易意图必须含方向、类型和理由引用")


@dataclass(frozen=True)
class JiangheDecision:
    attention_mode: AttentionMode
    family: StrategyFamily
    direction: Direction
    action: DecisionAction
    uncertainty: str
    watch_regions: tuple[WatchRegion, ...] = ()
    invalidation: str | None = None
    next_review: datetime | None = None
    referenced_jianghe_claims: tuple[str, ...] = ()
    referenced_cases: tuple[str, ...] = ()
    rationale: str | None = None
    trade_intent: ConstrainedTradeIntent | None = None

    def __post_init__(self) -> None:
        if not self.uncertainty:
            raise ValueError("决策必须明确不确定性")
        if self.next_review is not None:
            _require_aware(self.next_review, "next_review")
        if self.action is DecisionAction.NO_TRADE and self.direction is not Direction.NONE:
            raise ValueError("NO_TRADE 必须允许 NONE 方向")
        if self.action is DecisionAction.ENTER and (self.direction is Direction.NONE or self.trade_intent is None):
            raise ValueError("ENTER 必须带方向和受约束交易意图")
        if self.trade_intent is not None and self.trade_intent.direction is not self.direction:
            raise ValueError("交易意图方向必须与决策一致")


@dataclass(frozen=True)
class DecisionAuditRecord:
    observation_identity: str
    ai_trader_identity: str
    raw_response: str
    normalized_decision: JiangheDecision
    observation_available_at: datetime
    model_request_at: datetime
    model_response_at: datetime
    normalized_decision_at: datetime
    intent_available_at: datetime

    def __post_init__(self) -> None:
        for field_name in ("observation_available_at", "model_request_at", "model_response_at", "normalized_decision_at", "intent_available_at"):
            _require_aware(getattr(self, field_name), field_name)
        if not self.observation_identity or not self.ai_trader_identity:
            raise ValueError("决策审计必须绑定观察和 AI 身份")
        ordered = (self.observation_available_at, self.model_request_at, self.model_response_at,
                   self.normalized_decision_at, self.intent_available_at)
        if any(later < earlier for earlier, later in zip(ordered, ordered[1:])):
            raise ValueError("决策审计时间线不能倒流")


class AITraderProvider(Protocol):
    """厂商中立接口；本包没有任何真实模型实现。"""

    provider_identity: str

    def decide(self, observation: JiangheObservation, memory: JiangheWorkingMemory) -> tuple[str, JiangheDecision]:
        """返回原始回复和规范化决策；实现必须由后续评测包验证。"""


class UnavailableAITraderProvider:
    """默认失败闭合，防止本基础包意外向任意模型厂商发请求。"""

    provider_identity = "NO_REAL_MODEL_PROVIDER"

    def decide(self, observation: JiangheObservation, memory: JiangheWorkingMemory) -> tuple[str, JiangheDecision]:
        raise RuntimeError("本基础包未接入真实模型；仅允许合成测试提供者")


def validate_transition(current: AttentionMode, decision: JiangheDecision) -> AttentionMode:
    """校验注意力状态转移，禁止把任何状态强迫成多空二选一。"""
    if decision.action in (DecisionAction.NO_TRADE, DecisionAction.WAIT):
        if current is AttentionMode.CANDIDATE and decision.attention_mode not in (AttentionMode.WATCH, AttentionMode.SCAN):
            raise ValueError("CANDIDATE 的等待必须降回 WATCH 或 SCAN")
        return decision.attention_mode
    expected = {
        DecisionAction.WATCH: AttentionMode.WATCH,
        DecisionAction.CANDIDATE: AttentionMode.CANDIDATE,
        DecisionAction.ENTER: AttentionMode.IN_POSITION,
        DecisionAction.MANAGE: AttentionMode.IN_POSITION,
        DecisionAction.EXIT: AttentionMode.SCAN,
    }[decision.action]
    if decision.attention_mode is not expected:
        raise ValueError("决策动作与注意力状态不一致")
    allowed = {
        AttentionMode.SCAN: {DecisionAction.WATCH},
        AttentionMode.WATCH: {DecisionAction.CANDIDATE, DecisionAction.WATCH},
        AttentionMode.CANDIDATE: {DecisionAction.ENTER, DecisionAction.WATCH, DecisionAction.CANDIDATE},
        AttentionMode.IN_POSITION: {DecisionAction.MANAGE, DecisionAction.EXIT},
        AttentionMode.COOLDOWN: {DecisionAction.WATCH},
        AttentionMode.SUSPENDED: set(),
    }
    if decision.action not in allowed[current]:
        raise ValueError("当前注意力状态不允许该决策动作")
    return expected


@dataclass
class ReplayClock:
    """历史回放单向时钟：最低可靠粒度为已完成的 1 分钟 K 线。"""

    current_time: datetime
    baseline_granularity: timedelta = timedelta(minutes=1)

    def __post_init__(self) -> None:
        _require_aware(self.current_time, "current_time")
        if self.baseline_granularity != timedelta(minutes=1):
            raise ValueError("历史江河回放基线固定为已完成 1 分钟 K 线")

    def advance_to(self, value: datetime) -> None:
        _require_aware(value, "value")
        if value < self.current_time:
            raise ValueError("历史回放时钟不能倒流")
        self.current_time = value


@dataclass
class JiangheMarketReplay:
    clock: ReplayClock
    memory: JiangheWorkingMemory = field(default_factory=JiangheWorkingMemory)
    audit_ledger: list[DecisionAuditRecord] = field(default_factory=list)

    def accept_observation(self, observation: JiangheObservation) -> None:
        if any(not bar.is_closed for bar in observation.bars):
            raise ValueError("历史 1 分钟回放不接受部分 K 线来伪造盘中状态")
        if observation.identity.decision_time < self.clock.current_time:
            raise ValueError("回放不能接受过去的观察")
        self.clock.advance_to(observation.identity.decision_time)

    def record_decision(self, record: DecisionAuditRecord) -> None:
        if record.observation_available_at < self.clock.current_time:
            raise ValueError("回放不能在当前时钟之前生成决策")
        validate_transition(self.memory.attention_mode, record.normalized_decision)
        self.clock.advance_to(record.intent_available_at)
        self.audit_ledger.append(record)
        self.memory = replace(self.memory, attention_mode=record.normalized_decision.attention_mode,
                              last_meaningful_decision=record.normalized_decision.action.value,
                              watch_regions=record.normalized_decision.watch_regions,
                              transition_reason=record.normalized_decision.rationale)

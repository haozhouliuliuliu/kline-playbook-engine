# ADR：江河 AI 交易员决策层 V0.1

状态：已采纳（Owner 方向决定，2026-08-23）

## 决定

Skeleton v1.0 保留为历史接受的基础架构。本 ADR 只替换其中“实时关键链路不得依赖自由裁量 LLM”的产品边界：江河 AI 可以提出受约束的交易意图，但不能拥有风险、账户、订单或券商事实。

```text
Market Data
-> Rolling Market State
-> Multi-Timeframe Observation
-> Jianghe AI Decision Layer
-> constrained TradeIntent
-> deterministic RiskGate
-> OMS
-> Execution
-> Broker Reports
-> Reconciliation
-> Safety
-> Ledger
```

`TradingState` 仍是唯一可变实时状态所有者。`RiskGate` 仍拥有硬风险上限；OMS、STOP/OCO、Broker Adapter、Safety、reconciliation 和 Ledger 的既有责任不变。AI 不可修改资金真相、持仓真相、券商真相、硬风险限制、订单生命周期或安全覆盖。

## 范围与边界

- 江河 V1.1 是短中期唯一交易知识源；广泛扩张来源暂停。
- AI 依据多周期观察判断势、位、态和低周期实际行为，输出 A/B/C/D 或 NONE，以及 WAIT、NO_TRADE、WATCH、CANDIDATE、ENTER、MANAGE、EXIT。
- UNKNOWN、矛盾、来源外行情或不熟悉状态必须允许并优先 `NO_TRADE`；不得设计成强制多/空二分类。
- 历史基线最低可靠粒度是已完成的 1 分钟 K 线。不得从 OHLC 伪造秒级顺序、先高后低或 tick 序列。
- 图表与结构化 OHLCV 双输入都必须是时间点可得的；AI 标注是“假设”，不属于市场事实。
- 本 ADR 不授权候选收益、Validation、Final、真实 Shadow、Broker、真钱、API 密钥或任一模型厂商的采纳。

## 版本与可审计性

知识包内容变化、模型/提示词/上下文/记忆/图表/唤醒/决策模式/推理配置/工具能力/家族范围变化，均生成新的 `JiangheAITraderIdentity`。每次真实模型调用未来都须记录原始回复、规范化决策、观察身份和完整延迟链。

现阶段 `src/jianghe_ai_trader.py` 仅提供无厂商的类型与失败闭合默认提供者，供合成回放和后续忠实度评测使用。

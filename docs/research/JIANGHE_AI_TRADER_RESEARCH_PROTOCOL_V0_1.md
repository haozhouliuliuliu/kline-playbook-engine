# 江河 AI 交易员研究协议 V0.1

状态：已采纳的架构研究协议；不替代冻结的 `HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`。

## 研究对象

江河 AI 交易员是带随机性的、版本化的自由裁量研究对象，而不是“某个模型名称”。一次 pre-outcome freeze 至少绑定：

```text
knowledge pack + model/provider/version + system/decision prompt
+ context-selection + memory policy + chart renderer + observation schema
+ wake policy + decision schema + normalizer + inference configuration
+ tool capabilities + Jianghe A/B/C/D scope
```

其中任一会影响结果的变化，均创建新版本/后代，并继承已发生的数据暴露。不能以换提示词、换模型或追加案例后仍自称为原研究对象。

## 观察、记忆与回放

`JiangheObservation` 是每次唤醒的时间点世界快照，包含多周期已知 OHLCV、每根 K 的 `available_at`、部分/完整标志、仓位和订单事实；不包含当期金额 PnL、日 PnL 或权益曲线。图表固定布局、固定窗口和时间标签，不得显示未来或按未来自动缩放。

Working Memory 必须以追加式变更记录保存假设、趋势看法、偏向、观察区、关键位置、家族、触发、失效、未知项、标注和状态迁移原因。每条变更绑定时间、旧值、新值、原因、观察身份和 AI 身份。

`JiangheMarketReplay` 只能向前推进。历史基础回放只消费已完成的 1 分钟 K 线；若未来实时能力使用盘中/亚分钟信息，必须成为不同 capability/version，不能宣称等价通过 1 分钟历史回放。

## 决策和审计

普通 SCAN/WAIT 应为紧凑结构。发生状态迁移、ENTER、MANAGE、EXIT、重大失效、UNKNOWN/矛盾时才要求充分理由。每次模型调用未来必须记录：

```text
observation_available_at <= model_request_at <= model_response_at
<= normalized_decision_at <= intent_available_at
```

因此模型延迟不得产生过去成交。AI 输出的 `ConstrainedTradeIntent` 仍必须经过确定性 RiskGate 和 OMS。

## 随机性与未来评测门

任何候选结果试验之前，必须另行冻结并审查：重复调用规则、单次与 ensemble 语义、可控时的 temperature/seed、供应商模型漂移策略、API 模型版本漂移策略，以及如何统计决策稳定性。V0.1 不臆造统计阈值，也不锁定模型厂商。

`PROSPECTIVE_PROCESS_ASSUMPTION_DESIGN=NO_GOVERNABLE_A_B_ASSUMPTION_FOUND` 仍是全局候选验证阻塞，不阻止无结果的观察/回放/忠实度基础工程。

## 当前权限

```text
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
FINAL=LOCKED
REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
REPLAY_SCOPE=SYNTHETIC_NON_OUTCOME_ONLY
```

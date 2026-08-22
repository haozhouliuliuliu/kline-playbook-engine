# 江河 AI 交易员研究协议 V0.1

状态：已采纳的架构研究协议；不替代冻结的 `HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`。

本文件定义稳定的 AI Trader 研究语义。**当前权限、当前 provider、SOURCE_ONLY / PRIMARY 状态和下一步只以 `CURRENT_STATE.md` 为准，不在本协议重复。**

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

`JiangheObservation` 是每次唤醒的时间点世界快照，包含多周期已知 OHLCV、每根 K 的 `available_at`、部分/完整标志、仓位和订单事实；默认不向 AI 交易脑暴露当期金额 PnL、日 PnL 或权益曲线。图表固定布局、固定窗口和时间标签，不得显示未来或按未来自动缩放。

Working Memory 必须以追加式变更记录保存假设、趋势看法、偏向、观察区、关键位置、家族、触发、失效、未知项、标注和状态迁移原因。每条变更绑定时间、旧值、新值、原因、观察身份和 AI 身份。

`JiangheMarketReplay` 只能向前推进。历史基础回放只消费已完成的 1 分钟 K 线；若未来实时能力使用盘中/亚分钟信息，必须成为不同 capability/version，不能宣称等价通过 1 分钟历史回放。

## 注意力 / 唤醒语义

AI 不需要每个 tick 输出长篇解释。系统允许持续市场状态 + 事件唤醒：

```text
SCAN
WATCH
CANDIDATE
IN_POSITION
```

普通 SCAN/WAIT 只需紧凑机器状态。进入 WATCH/CANDIDATE、提出 ENTER、发生 MANAGE/EXIT、重大失效、UNKNOWN/矛盾时才要求充分理由。

合法 wake event 可包括：新完成 K 线、价格进入/离开 AI watch region、失效位触碰、订单/持仓/Safety/session 事件。实时亚分钟 wake 若使用历史 1m 回放不存在的信息，必须单独版本化。

## 决策和审计

AI 必须允许：

```text
A / B / C / D / NONE
WAIT / NO_TRADE / WATCH / CANDIDATE / ENTER / MANAGE / EXIT
```

`NO_TRADE` 是一等合法决策。UNKNOWN、来源矛盾、不熟悉行情、位置无触发、对抗未解决等情况不得被强制转成多/空选择。

每次真实模型调用未来必须记录：

```text
observation_available_at <= model_request_at <= model_response_at
<= normalized_decision_at <= intent_available_at
```

因此模型延迟不得产生过去成交。AI 输出的 `ConstrainedTradeIntent` 仍必须经过确定性 RiskGate 和 OMS。

## Jianghe Fidelity 先于结果评价

初始模型/provider 比较首先回答“是否像江河”，而不是“是否赚钱”。

Fidelity 评价至少覆盖：

- 市场状态 / 周期纪律；
- A/B/C/D/NONE；
- `location != trigger`；
- `weakening != reversal`；
- 真/假突破；
- no-trade 纪律；
- UNKNOWN/contradiction 不脑补；
- 决策稳定性；
- 无依据发明率。

候选 PnL、未来价格、胜率、Sharpe、expectancy 等不得作为初始模型选择标签。

## 随机性与未来评测门

任何候选结果试验之前，必须另行冻结并审查：重复调用规则、单次与 ensemble 语义、可控时的 temperature/seed、供应商模型漂移策略、API 模型版本漂移策略，以及如何统计决策稳定性。

本协议不臆造统计阈值，也不锁定模型厂商。

## 与冻结 Human Playbook 协议的关系

冻结的 `HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` 继续拥有：

- SOURCE / AI interpretation / implementation separation；
- provenance；
- SOURCE_ONLY；
- PRIMARY branch；
- lineage / exposure；
- chronological split；
- outcome firewall / multiplicity / protected holdout semantics。

本协议只补充 AI Trader 作为随机、版本化决策对象时的 observation / memory / identity / fidelity / latency / provider-drift 语义。

## 权限边界

本协议本身不授权：

- candidate outcome backtest；
- Development performance inspection；
- Validation / historical Final；
- Shadow/Forward；
- broker；
- real money；
- 任一真实模型/provider 的采用。

当前权限和 readiness 必须从当前 `main` 的 `PROJECT_BRAIN_RUNTIME_BRIEF.md` / `CURRENT_STATE.md` 获取，禁止从本协议中的历史版本文字推断。

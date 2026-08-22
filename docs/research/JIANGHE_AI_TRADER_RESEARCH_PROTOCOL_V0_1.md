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

## 与冻结 Human Playbook PRIMARY 语义的兼容解释

`HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` 是在早期机械策略架构下冻结的，因此使用了 `MACHINE OPERATIONALIZATION`、`deterministic operationalization identity/hash` 等措辞。当前 Owner 已采纳 Jianghe AI Trader 决策层；**这些旧措辞不得被解释成“必须把江河判断重新压成固定阈值/死规则策略”。**

对 Jianghe AI Trader，冻结协议中的稳定要求按以下方式满足：

```text
PRIMARY_BRANCH
=
source-justified interpretation branch inside Jianghe A/B/C/D knowledge boundary

DETERMINISTIC_OPERATIONALIZATION_IDENTITY
=
deterministic identity/hash of the full AI Trader research object and hard execution envelope
NOT deterministic market decision output
```

也就是说：
- PRIMARY 要锁的是“我们到底采用哪一种来源可支持的解释/边界”，不是把每次市场判断写成固定公式；
- AI 运行本身可以是随机/自由裁量的，但其 knowledge pack、模型版本、prompt、context policy、memory、renderer、observation、wake、decision schema、inference config、tool capability、family scope 等必须形成稳定可复现的 `JiangheAITraderIdentity`；
- 确定性 RiskGate / OMS / STOP-OCO / Safety 等硬执行包络继续独立版本化；
- outcome-bearing test 之前锁定的是上述完整研究对象身份 + PRIMARY branch 身份，而不是要求 AI 每次对同一行情输出机械相同的买卖结论；
- UNKNOWN / contradiction 不能为了满足“可机械化”而被项目虚构阈值填平。

如果未来需要修改冻结协议本身的统计/暴露/PRIMARY 核心语义，仍属于 Owner-gated protocol change；本节只是使其与已采纳 AI Trader 架构保持一致。

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

### 真实交易脑必须同时通过“眼睛”能力

真实模型 Fidelity 不能只做文本问答。候选交易脑至少要分别证明：

1. **知识/语义 Fidelity**：能按江河 claims/cases/hard negatives 正确推理；
2. **视觉 Observation Fidelity**：能读取标准化多周期 K 线图，识别图中当前可见结构，不把 AI annotation 当市场事实；
3. **结构化行情 Fidelity**：能正确消费 point-in-time OHLCV/timestamp/closed-partial 信息；
4. **双输入一致性**：标准化图表与结构化数据表达同一 observation 时，不应出现无依据的重大冲突；
5. **运行可用性**：有项目可治理的调用方式、可识别 provider/model/version、可记录延迟与原始回复，并能绑定到 `JiangheAITraderIdentity`。

WorkBuddy 或其他 UI 中“能选择某模型”本身只证明交互可访问性，**不等于该模型已经具备项目可编程调用/API、版本固定或实盘 provider 可用性。**

模型必须在上述非结果能力上形成证据后，才可从 `CANDIDATE` 晋级 `VERIFIED`；仍不得用候选收益补救 Fidelity 缺陷。

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

本协议补充并专门解释 AI Trader 作为随机、版本化决策对象时的 PRIMARY operationalization、observation / memory / identity / fidelity / latency / provider-drift 语义。

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

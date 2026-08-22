# 江河 AI 忠实度基准 V0.1

```text
DESIGN=COMPLETE
FIXTURE_CORPUS=INTEGRATED_NON_OUTCOME
SCORING_CORE=INTEGRATED
REAL_MODEL_EVALUATION=NOT_STARTED
```

当前 readiness / SOURCE_ONLY / PRIMARY / outcome 权限只以 `CURRENT_STATE.md` 为准。

## 目的

先评价“是否像江河地理解市场”，而不是“哪个模型历史收益最高”。基准只可使用江河 V1.1 的 claims、案例、硬负例、no-trade、UNKNOWN、矛盾记录，以及合成的非结果夹具。

禁止使用候选未来收益、PnL、Sharpe、胜率、期望值、权益曲线或“后来价格怎么走”进行初始模型选择。

## 当前正式夹具

Machine-readable corpus:
`docs/evidence/JIANGHE_AI_FIDELITY_FIXTURES_V0_1.json`

Evidence/review:
- `docs/evidence/JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1.md`
- `docs/reviews/JIANGHE_AI_FIDELITY_AND_REPLAY_INTEGRATION_REVIEW_V0_1.md`

当前 corpus 覆盖 A/B/C/D/NONE、no-trade 和 9 类 hard negative；允许多个语义上合理的答案，不要求复述固定文字。

## 评分维度

| 维度 | 合格含义 |
|---|---|
| 市场状态与多周期纪律 | 明确周期；不把低周期形态脱离高周期语境。 |
| 家族与方向许可 | 仅在 A/B/C/D/NONE 的江河边界内分类；偏向不等于触发。 |
| NO_TRADE | 能拒绝震荡中部、无反应位置、对抗未决、空间差、不熟悉和未知状态。 |
| 关键位与触发分离 | 不把到位、形态、弱化或单根 K 自动升级为入场。 |
| 反转/突破语义 | 弱化不等于反转；真突破与刺破/快速回原空间必须区分。 |
| UNKNOWN 与矛盾诚实性 | 未被来源唯一钉死的概念不虚构阈值或风险参数。 |
| 稳定性与幻觉 | 相同固定输入的变化可测；无依据的江河断言计入不当发明。 |

## 真实模型 Fidelity 必须分轨评测

真实交易脑不能只通过文字语义题。至少要分别形成以下非结果证据：

### A. Knowledge / semantic track
使用现有 claims / cases / hard negatives / UNKNOWN / contradiction fixture，测试江河语义忠实度。

### B. Visual observation track
使用 `JiangheChartRenderer` 基于合成/非结果 causal observation 生成的标准化多周期 K 线图，测试模型是否能：
- 正确区分周期；
- 读取当前可见结构、位置、强弱/跟随；
- 区分 closed / partial；
- 不把 AI watch/key/invalidation annotation 当市场客观事实；
- 不引用图中不存在或未来才出现的信息。

### C. Structured observation track
对与视觉图完全对应的 point-in-time OHLCV / timestamps / metadata 输入，测试时间、bar 状态、多周期关系和 causal cutoff 理解。

### D. Dual-input consistency track
当标准化图和结构化数据代表同一个 `JiangheObservation` 时，比较两种输入得到的核心市场判断。允许合理措辞差异，但无依据的 family / direction / permission 重大冲突必须计入 Fidelity 缺陷。

### E. Operational provider track
记录并验证：
- provider/model/version 可识别；
- 实际项目调用方式可治理；
- raw response 可保存；
- latency 可测；
- inference configuration 可绑定；
- 能形成稳定 `JiangheAITraderIdentity`。

仅能在 WorkBuddy/其他 UI 里点选某模型，不等于该模型已经通过 Operational provider track，也不证明存在项目可编程 API。

## 模型评价记录

每个模型评测必须绑定版本化 `JiangheAITraderIdentity`，至少保存：

- knowledge-pack identity；
- provider/model/version；
- prompt / context / memory / renderer / observation / wake / normalizer identities；
- inference configuration；
- fixture id / observation identity；
- input track（semantic / visual / structured / dual）；
- raw response；
- normalized decision；
- semantic/visual constraint score + violation reasons；
- latency；
- repeated-run stability evidence when the protocol requires it.

## 选择规则

Provider/model 初始状态都是 `CANDIDATE`。

晋级依据是：

```text
JIANGHE_FIDELITY
+ VISUAL_OBSERVATION_FIDELITY
+ STRUCTURED_OBSERVATION_FIDELITY
+ DUAL_INPUT_CONSISTENCY
+ NO_TRADE_DISCIPLINE
+ UNKNOWN_HONESTY
+ DECISION_STABILITY
+ LOW_UNJUSTIFIED_INVENTION
+ GOVERNABLE_PROVIDER_CALLABILITY
+ ACCEPTABLE_LATENCY_FOR_INTENDED_WAKE_MODE
```

不是收益。

完成真实模型基准并形成项目证据后，才能讨论 `VERIFIED`；只有正式项目决定后才能成为 `ADOPTED_JIANGHE_DECISION_MODEL`。

本基准本身不改变 SOURCE_ONLY / PRIMARY 状态，也不授权 candidate outcome、Validation、Final、Shadow、Broker 或 real money。

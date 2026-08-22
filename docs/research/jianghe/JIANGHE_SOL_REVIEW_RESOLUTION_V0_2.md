# 江河交易员 Sol 复核结论 V0.2

本文件记录 GPT-5.6 Sol 对 V0.1 `JIANGHE_EVIDENCE_REVIEW_QUEUE_V0_1.csv` 七项待确认内容的原视频复核结果。它只解决已经明确列入队列的问题，不扩大为新的来源语义。

## JH-REV-001 — Video 001 “应变交易理念”

- source: `001 / BV1yxebzoERD`
- exact anchor: `00:04:44.490–00:04:47.810`
- V0.1 SRT 候选文字：`应变教育理念`
- 原视频同时间烧录字幕经 Sol 复查：`我的一个应变交易理念`
- resolution: `RESOLVED_VIDEO_OVERRIDES_SRT`
- formal source wording: `应变交易理念`
- note: 保留 `SOURCE_TEXT_CONFLICT`，但不再把错误 SRT 当语义权威。

## JH-REV-002 — Video 024 ABC 的 B 回调根数

- source: `024 / BV1oWqDBbEuh`
- anchor A: `约 00:09:59.280–00:10:08.150`
- source rule: B 的形成过程中若出现 **连续三根或以上同方向的回调 K 线**，来源明确要求放弃此次 ABC 交易机会。
- anchor B: `约 00:10:19.310–00:10:29.890`
- source rule: 若 B 在 **三根或更少 K 线**内快速回到、触及或破坏 A 的起始区域，视为 B 过深/过快并否定 A，放弃机会。
- resolution: `RESOLVED_SOURCE_EXPLICIT`
- important boundary: 不得反推“B 总长度最多只能两根”。混合方向的 B 可以持续更久，只要来源禁止条件没有被触发。

## JH-REV-003 — Video 020 的 1:1

- source: `020 / BV1nDU8B6EjV`
- anchor: `00:00:17.790–00:00:31.750`
- source first states: 当时 **不预设止盈**，后续根据价格反应决定。
- later says: `至少拿个一比一应该不是问题`。
- resolution: `RESOLVED_CASE_EXPECTATION_NOT_UNIVERSAL_RULE`
- meaning: 1:1 是该订单当时对可达空间/收益的估计，不是固定 TP，也不是全部 Family 的统一硬门槛。
- correction to V0.1 `JH-CLM-020-002`: `source_exit_or_management_if_explicit` 不应写成“案例中固定到 1:1 止盈”；正确语义是“该案例未预设止盈，1:1 仅为当时空间预期”。

## JH-REV-004 — Video 021 震荡半仓

- source: `021 / BV1fT2iBjEeE`
- anchor: `约 00:06:11–00:06:24`
- source wording meaning: 江河明确说其做震荡时 **永远用常规仓位的一半/留下半仓去做**。
- resolution: `RESOLVED_EXPLICIT_RELATIVE_SIZING`
- formal rule for this source/system version: `RANGE_POSITION_SIZE = 0.5 × REGULAR_POSITION_SIZE`
- machineability: `DIRECTLY_PROGRAMMABLE` as a relative sizing rule.
- boundary: 不证明未来所有版本永远不变，也不定义“常规仓位”的账户级绝对数值。

## JH-REV-005 — Video 005 “排斥反应”视觉指代

- source: `005 / BV16fxYzGEA3`
- anchor: `约 00:06:57–00:07:10`
- Sol visual review: 价格进入上方黄色关键区域后出现明显向下反应；随后回到下方黄色区域又出现向上反应，并继续向上突破。
- resolution: `RESOLVED_VISUAL_REFERENT_VERIFIED`
- claim `JH-CLM-005-001` may be `READY` for the existence/location of rejection behavior.
- boundary: “排斥有多强才算合格”的统一机器阈值仍 `UNKNOWN`。

## JH-REV-006 — Video 024 A 段数字适用范围

- source: `024 / BV1oWqDBbEuh`
- A definition anchor: `约 00:05:30–00:06:29`
- source explicitly covers bullish and bearish direction: 连续至少 4 根同方向 K 线；4 根中至少 2 根趋势型 K 线。
- applicability anchor: `约 00:03:36–00:04:40`
- source says method applies to **流动性足够好的市场**，举例期货、外汇、加密货币，并称可用于不同时间周期。
- resolution: `RESOLVED_SOURCE_EXPLICIT_SCOPE`
- boundary: “超大 K 可构成 A 的变形”仍缺精确数值，不因本复核而机器化。

## JH-REV-007 — 固定目标 vs 动态结构离场

- source: `017 / BV1NBy5BfEYF`
- `约 00:01:25–00:01:45`: 来源讨论固定盈亏比（例 1:1），并指出可能在趋势继续时过早拿走利润。
- `约 00:01:52`: 第二类是按事先规划的空间/位置离场。
- `约 00:01:58+`: 第三类是跟随市场条件/市场脚步动态离场；江河明确表示 **自己更喜欢第三种**。
- resolution: `RESOLVED_CONTEXTUAL_ALTERNATIVES`
- fixed RR、fixed target/space、dynamic market-following 是不同退出方法，不构成逻辑矛盾。
- Jianghe personal preference in this source: dynamic/market-following exit.
- together with REV-003: Video 020 的 1:1 也不是固定 TP。

## 复核后的状态变化

```text
V0_1_REVIEW_ITEMS=7
RESOLVED=7
UNRESOLVED_FROM_V0_1=0
```

仍然保持 UNKNOWN 的内容包括：排斥强度的统一阈值、完整评分公式、统一账户风险比例、关键区/防守位机器画法、强弱趋势及趋势阶段的机器阈值等。解决 review item 不等于这些更大的机器化问题已经解决。

# 江河交易员策略家族规格 V0.7（001–083）

本文件是来源化研究规格，不是机器策略或交易授权。核心 Family 仍只有 A–D。`UNKNOWN` 不得自行补参数。

## JH-FAMILY-A：趋势关键位回调延续

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 已识别趋势/突破后的延续环境；V075再次明确弱趋势更适合回调，强势市场回调可能很浅甚至不给深回调 |
| preconditions | 外部方向/偏向明确；原推动质量足够；反向回调相对弱，不能快速深度否定原推动 |
| location | 趋势防守/发力位、回调区、突破后回踩区；V077/V081弱空以最后空头发力点作为高空位置 |
| trigger | 顺向确认K、吞没、二推失败后恢复；V079正式给出“强→弱回调→原方向再强”链 |
| no_trade | 回调过深、逆向K不弱、对抗态未解决、位置差/空间不足；弱趋势禁止追空/追多 |
| stop_or_invalidation | 回调/入场结构极值外；防守失守；原推动被持续反向跟随否认 |
| management | 趋势有效可动态持有；弱趋势/微波段可使用前低/前高或反方发力区有限目标 |
| position_risk | 以损定仓母规则；允许计划内分仓进入；统一账户风险仍UNKNOWN |
| timeframes | 高周期/主周期定方向和位置，小周期优化触发；V074/V077/V081均有5m→1m |
| explicit_numeric_rules | 既有ABC数字边界；V078趋势K实体≥约50%的来源定义用于动能解释，不等于Family A独立入场阈值 |
| human_discretion_fields | 回调深浅、发力点、强弱K相对比较、空间、对抗态结果 |
| unknown_fields | 统一回调阈值、发力点机器算法、账户风险比例、强弱K跨波动环境标准 |

## JH-FAMILY-B：趋势衰弱反转 / 高周期回调

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 原趋势末期/衰弱，或高周期关键区中的低周期反向机会 |
| preconditions | 原方向明确减弱；位置有价值；新方向仍需真实增强/跟随，不能只见旧方向变弱 |
| location | 高周期关键/参考位、原趋势防守区、震荡边界 |
| trigger | 原方向强→弱 + 新方向弱→强，或原方向强→弱后新方向直接强；可等第二次博弈确认 |
| no_trade | 原方向未减弱而新方向也很强的对抗态；只到位置没有真实强弱转换 |
| stop_or_invalidation | 新方向无法延续、原方向重新恢复；结构另一侧止损 |
| management | 根据订单模式和下一关键区管理；非核心剥头皮可更快退出 |
| position_risk | 左侧/低质量可缩仓；统一比例UNKNOWN |
| timeframes | 高周期给位置，低周期给强弱/触发；V077给出5m宽震荡下区→1m强弱转换多 |
| explicit_numeric_rules | 无统一反转数字阈值 |
| human_discretion_fields | 强弱转换质量、对抗态是否解决、位置价值、二次博弈 |
| unknown_fields | 反转阶段算法、强弱阈值、统一仓位模型 |

## JH-FAMILY-C：多周期确认突破

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 强势/失衡市场或结构/震荡空间真实突破；V075明确强势市场更适合突破 |
| preconditions | 价格离开旧空间；同向推进/跟随足够；回调浅弱或根本不给深回调 |
| location | 大结构/震荡边界、突破后回踩区、前方参考空间 |
| trigger | 真突破+跟随+低周期确认；对抗态若连续同向跟随分出胜负后可跟随 |
| no_trade | 影线刺破、无跟随、快速收回旧空间；弱趋势中机械追突破；对抗态未分胜负 |
| stop_or_invalidation | 重新进入旧空间、原突破结构失效、结构另一侧 |
| management | 新发力/结构形成后可推进止损；跟随消失/二推失败可退出 |
| position_risk | 可分阶段进入；以损定仓控制总风险；统一Family仓位UNKNOWN |
| timeframes | 高周期边界/节奏 + 低周期确认；不同周期是同一价格过程的不同聚合表达 |
| explicit_numeric_rules | 无统一突破距离/跟随强度数字 |
| human_discretion_fields | “接近直线”、拉开距离、跟随质量、浅回调、对抗态胜负 |
| unknown_fields | 距离阈值、跟随阈值、强势市场量化标准 |

## JH-FAMILY-D：震荡边界反转

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 已确认平衡/震荡/宽幅震荡；允许外部震荡同时存在内部弱多/弱空偏向 |
| preconditions | 波段只在外部边界；历史区间只给位置参考，必须等当下反向行为 |
| location | 外部上沿/下沿；中间不做主周期边界单 |
| trigger | 边界二推/多推失败、吞没、强弱转换；V077下区为1m空头减弱+多头增强 |
| no_trade | 只到边界无确认、真突破后仍坚持反转、震荡中间主周期反转单 |
| stop_or_invalidation | 外部边界真实突破并持续跟随；结构另一侧 |
| management | 可主动保护/不要求拿满区间；订单模式决定利润尺度 |
| position_risk | 既有0.5×常规仓位source-version保持；以损定仓是更高层风险框架候选 |
| timeframes | 外部主周期定区间，小周期优化边界触发；同周期内部结构不得冒充更小周期外部结构 |
| explicit_numeric_rules | 既有`0.5×REGULAR_POSITION_SIZE`仅保留来源范围，不外推所有震荡单 |
| human_discretion_fields | 边界、排斥/二推质量、内部偏向、强弱转换 |
| unknown_fields | 区间边界机器算法、0.5×适用范围、统一退出公式 |

## Family间切换与市场节奏

- V075正式强化：`MARKET_RHYTHM → METHOD_SELECTION`。强势/失衡市场更偏C；弱趋势更偏A；平衡/震荡更偏D。
- D真突破并产生真实跟随后可切C。
- A/B之间不能只靠“反向K很大”切换；必须判断旧方向是否减弱、新方向是否真正接管。
- V078的`对抗态`属于暂停区：双方均强、尚未分胜负时不应强行归入B或C，等第二次博弈结果。
- 发力点是位置/市场状态信息，不是第五个Family。

## NON-FAMILY：SCALPING_EXECUTION_MODE

仍为 `NON_CORE_EXECUTION_MODE`。V074再次明确江河本人主做仍是日内波段/微波段；大量剥头皮视频更多与直播/内容展示效率有关。因此：

```text
SCALPING_STATUS=NON_CORE_EXECUTION_MODE
FAMILY_E=NO
PRIMARY_SELF_REPORTED_STYLE=INTRADAY_SWING_MICRO_SWING
```

## AUXILIARY_TOOL_USAGE：均线/其他指标

V078解决了此前“裸K vs 均线”的表面冲突：江河明确说K线/价格是主要直接信息，指标只是辅助工具，不是决策依据，并明确自己有时会使用均线、某些环境甚至会利用指标的滞后。

```text
INDICATOR_STATUS=AUXILIARY_TOOL_USAGE
MA_STATUS=AUXILIARY_TOOL_USAGE
CORE_REQUIRED=NO
FAMILY_E=NO
```

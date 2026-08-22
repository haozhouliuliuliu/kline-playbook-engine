# 江河交易员 Case Library Delta V0.8（084–093）

本文件只记录来源案例，不把盈利结果当作策略有效性证据。所有图表依赖案例均已用原视频时间范围复查。

## JH-CASE-084-001 — 宽幅震荡前兆 + 5m顺空的超短线
- source: V084 / BV1m47q6cEdH
- range: 00:00:33–00:02:24
- case_type: POSITIVE_EXAMPLE
- market_context: 暴跌后暴涨，1m进入宽幅震荡前兆；5m仍偏下跌
- setup: 1m高位与5m空方向同时支持空
- trigger: 第一向下推动后弱回调结束，参与第二推动
- stop/invalidation: 上方结构
- management/exit: 明确只拿短目标；到目标离场；5手仅属该案例，不升级统一仓位
- family: JH-FAMILY-A / JH-FAMILY-D
- linked_claims: JH-CLM-084-001

## JH-CASE-084-002 — 宽幅震荡下沿强弱转换多
- source: V084 / BV1m47q6cEdH
- range: 00:03:30–00:08:20
- case_type: POSITIVE_EXAMPLE
- market_context: 暴跌与暴涨后形成明确宽幅震荡
- location: 最近下跌发力点与上涨发力点定义上下边界
- trigger: 下沿反应后，1m空头阴线减弱、多头阳线重新发力
- stop/invalidation: 下方结构
- management: 目标瞄定上方区域；推进止损；未到目标也可保护利润
- family: JH-FAMILY-D
- linked_claims: JH-CLM-084-002|003|004

## JH-CASE-084-003 — 盈利结果下的执行失败复盘
- source: V084 / BV1m47q6cEdH
- range: 00:09:13–00:11:16
- case_type: OTHER
- outcome: 小幅盈利
- process_problem: 持仓过程中去跑步，注意力分散；江河明确认为当天做得不好
- lesson: 分仓入场、后续新增风险动作需要区分；过程质量不能被最终盈利掩盖
- family: NONE
- linked_claims: JH-CLM-084-005

## JH-CASE-086-001 — 碾压式突破后的强弱强短多
- source: V086 / BV1p2TF64EQp
- range: 00:04:19–00:10:21
- case_type: POSITIVE_EXAMPLE
- market_context: 5m原下跌减弱，无法继续创新低
- location: 最近空头发力点
- setup: 发力点被实体向上突破，随后有强阳跟随；来源称碾压式突破
- trigger: 强推动后很弱阴线回调，没有阴线跟随，马上被阳线实体吞没
- stop/invalidation: 下方短期结构
- management: 到预期区域无停滞则继续观察并推止损；通过压缩进场成本提高RR
- note: 最终高R为来源自述结果，只作case content
- family: JH-FAMILY-A / JH-FAMILY-C
- linked_claims: JH-CLM-086-001|002|003|004|005

## JH-CASE-088-001 — 宽幅震荡下沿多 + 动态推止损
- source: V088 / BV1jBMt68Erc
- range: 00:00:27–00:04:24
- case_type: POSITIVE_EXAMPLE
- market_context: 强上涨被强下跌局部否认后，双向创新形成宽幅震荡
- location: 外部下沿
- trigger: 来源在下沿用更小周期细化进场
- management: 新结构/发力点形成后推进止损；进入多头区域时先过滤空信号而不是直接做多
- family: JH-FAMILY-D
- linked_claims: JH-CLM-088-001|002|003|004

## JH-CASE-090-001 — 1H弱多 + 5m震荡下沿重叠许可
- source: V090 / BV1Y3N16cEor
- range: 00:00:20–00:04:55
- case_type: POSITIVE_EXAMPLE
- higher_tf: 1H上涨被内部空头N削弱但尚未否认
- execution_tf: 5m震荡下沿 + 1m精细进场
- location: 1H最后多头发力点，同时是5m低多区域
- trigger: 错过第一次后，第一上推的回调结束作为第二次机会
- management: 上移止损，最终仅拿局部利润；新条件出现仍可重新尝试
- family: JH-FAMILY-A / JH-FAMILY-D
- linked_claims: JH-CLM-090-001|002

## JH-CASE-090-002 — 弱上涨重分类震荡后的上沿空
- source: V090 / BV1Y3N16cEor
- range: 00:05:49–00:10:08
- case_type: POSITIVE_EXAMPLE
- market_context: 1H弱上涨出现内部空头N、结构扩散、上方不能创新高延续 → 重分类震荡
- location: 震荡上沿
- trigger: 错过第一空点后，第一向下推动的回调结束参与第二推动
- management: 因时间晚/状态差，不愿长时间持有；睡前设置固定止盈
- family: JH-FAMILY-D
- linked_claims: JH-CLM-090-003|004

## JH-CASE-090-003 — 影线假破下沿后的宽幅震荡多
- source: V090 / BV1Y3N16cEor
- range: 00:10:37–00:11:42
- case_type: POSITIVE_EXAMPLE
- market_context: 5m宽幅震荡
- hard_negative: 前低被影线刺破，但没有实体突破、没有跟随，不视为真破
- trigger: 1m强阴转弱后多头再次发力
- entry: 分仓进入，同一交易计划
- family: JH-FAMILY-D
- linked_claims: JH-CLM-090-005

## JH-CASE-093-001 — 宽幅震荡上沿二次确认空 + 无延续主动退出
- source: V093 / BV11Sge6AEnT
- range: 00:00:20–00:04:59
- case_type: NEAR_MISS
- market_context: 强下跌 + 强上涨且双方缺乏后续延续 → 宽幅震荡
- location: 上沿关键高位（来源解释为盈亏转换交界）
- first_signal: 两根强阴否认上涨
- no_trade_initially: 因此前上涨很强，不直接在第一反向信号入场
- trigger: 等反抽/回调结束，再切1m取得更明确空信号
- exit: 后续迟迟不能继续向下突破/推进，主动退出
- family: JH-FAMILY-D
- linked_claims: JH-CLM-093-001|002|003

## JH-CASE-093-002 — 强势市场改预案后的浅回调续多
- source: V093 / BV11Sge6AEnT
- range: 00:05:37–00:09:47
- case_type: POSITIVE_EXAMPLE
- market_context: 原计划突破后等深回踩；实际突破后直线强拉、几乎不回头 → 重分类强势市场
- setup: 左侧“真空区域”缺少明显关键阻力；第一推动强；回调K实体由大变小
- trigger: 1m强阳收K进入第一份；5m收K后进入第二份
- stop/invalidation: 下方回调结构
- management: 该趋势已非初期，降低利润预期；不能创新高则考虑离场；达到预期后上推止损
- family: JH-FAMILY-A / JH-FAMILY-C
- linked_claims: JH-CLM-093-004|005|006

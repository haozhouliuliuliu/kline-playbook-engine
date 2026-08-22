# 江河案例库增量 V0.9（094–098）

> 本文件只记录来源案例，不把盈利结果当作edge证据。

## JH-CASE-095-001 — 高周期宽震荡下方区域 → 低周期等待反向许可

- source: 095 / `BV1LCG36dEsR`
- approximate range: `00:00:20–00:08:20`
- case_type: `POSITIVE_EXAMPLE / MARKET_RECLASSIFICATION`
- market_context: 4H由强转弱，无法继续创新高，转为宽幅震荡/高抛低吸框架。
- location: 高周期下方关键区域。
- lower_timeframe: 1H→5m，必要时继续到1m。
- setup: 5m仍有明确向下推进，但已接近高周期下方区域。
- no_trade: 不在关键区域附近继续机械追空。
- trigger: 等待低周期企稳/反向结构与多周期许可形成。
- linked_claims: JH-CLM-095-001..004
- family: JH-FAMILY-D / JH-FAMILY-B overlap
- review_status: SOL_VERIFIED_FROM_BURNED_SUBTITLE_AND_CHART

## JH-CASE-095-002 — 主周期逻辑 + 1m细化执行案例一

- source: 095 / `BV1LCG36dEsR`
- approximate range: `00:08:20–00:13:30`
- case_type: `POSITIVE_EXAMPLE`
- market_context: 已由高周期位置与主周期方向确定可参与条件。
- execution: 5m作为主交易周期，1m用于细化进场。
- management: 预期位、结构和止损调整共同管理。
- outcome: 来源展示实际订单结果；仅作为source case content。
- linked_claims: JH-CLM-095-005
- family: JH-FAMILY-A / JH-FAMILY-D
- review_status: SOL_VERIFIED_FROM_BURNED_SUBTITLE_AND_CHART

## JH-CASE-095-003 — 主周期逻辑 + 1m细化执行案例二

- source: 095 / `BV1LCG36dEsR`
- approximate range: `00:13:30–00:17:00`
- case_type: `POSITIVE_EXAMPLE`
- setup: 再次从高周期/主周期区域开始，切低周期执行。
- management: 展示止损调整、预期与订单结果。
- hard_negative: 不根据单笔盈利金额推导策略有效性。
- linked_claims: JH-CLM-095-005
- family: JH-FAMILY-A / JH-FAMILY-D
- review_status: SOL_VERIFIED_FROM_BURNED_SUBTITLE_AND_CHART

## JH-CASE-098-001 — 关键区到达后企稳 + 第二次发力

- source: 098 / `BV1rpgP6gE8T`
- approximate range: `00:00:20–00:04:00`
- case_type: `POSITIVE_EXAMPLE`
- location: 图表灰色关键区域。
- setup: 快速推进到关键区域后没有直接交易。
- behavior: 等待企稳，随后观察第二次发力/确认。
- no_trade: 第一次触碰关键区域本身不是交易许可。
- ambiguity: 本轮无独立SRT，只保留画面+烧录字幕可确认的保守语义；具体订单方向/触发K后续可由本地SRT/ASR精确化。
- linked_claims: JH-CLM-098-001
- family: JH-FAMILY-B / JH-FAMILY-D
- review_status: SOL_VERIFIED_CONSERVATIVE

## JH-CASE-098-002 — 区间位置 → 小周期细化执行

- source: 098 / `BV1rpgP6gE8T`
- approximate range: `00:04:20–00:08:50`
- case_type: `POSITIVE_EXAMPLE`
- market_context: 区间/震荡结构。
- location: 区间边界/关键区域。
- execution: 主周期确定交易区域，随后通过更小周期和订单窗口细化执行。
- no_trade: 位置不到或小周期没有行为确认时不执行。
- ambiguity: 完整语音细节待本地字幕审计后可继续精确化。
- linked_claims: JH-CLM-098-002, JH-CLM-098-003
- family: JH-FAMILY-D
- review_status: SOL_VERIFIED_CONSERVATIVE

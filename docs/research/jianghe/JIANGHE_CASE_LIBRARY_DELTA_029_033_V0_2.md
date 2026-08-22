# 江河交易员案例库增量 029–033 V0.2

仅保存来源语义和边界；案例盈利/R 倍数不属于策略有效性证据。

## JH-CASE-029-001 — 多周期右侧多单与成功突破

| 字段 | 内容 |
|---|---|
| source | 029 / BV12AqNBjEgN / 约 00:01:42–00:07:10 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 高周期上涨，低周期内部结构修复 |
| setup | 内部空头 N 被打破形成多头 N，回踩防守位企稳 |
| trigger | K 线信号后偏右侧进场 |
| stop | 内部防守位下方；随后按新 N 防守逐步上移 |
| management | 成功突破后继续持有；新防守形成则移动止损锁利润 |
| exit | 市场节奏转弱，连续空头推进 + 多头恢复不利时离场 |
| linked_claim_ids | JH-CLM-029-001,002,003,004 |
| family | JH-FAMILY-A / JH-FAMILY-C |
| hard_negative | 仅突破但无跟随/未离开原空间，不具同样成功突破语义 |

## JH-CASE-029-002 — 强上涨弱化后的轻仓区间多

| 字段 | 内容 |
|---|---|
| source | 029 / BV12AqNBjEgN / 约 00:08:27–00:09:29 |
| case_type | OTHER |
| market_context | 之前强上涨，节奏转弱，来源假设更可能转震荡而非直接反转 |
| location | 大周期/原上涨 N 防守附近 |
| trigger | 打到防守位出现排斥后进场 |
| risk | 仓位非常轻；来源明确不建议模仿 |
| management | 预设约 1:1.5 的局部目标；仅该案例语境 |
| linked_claim_ids | JH-CLM-029-005 |
| family | JH-FAMILY-D（过渡/震荡假设） |
| ambiguity | 这是较激进、轻仓的情境案例，不升级为标准震荡规则 |

## JH-CASE-029-003 — 大周期回调逆势单边界

| 字段 | 内容 |
|---|---|
| source | 029 / BV12AqNBjEgN / 约 00:13:22–00:14:02 |
| case_type | NO_TRADE |
| market_context | 强上涨后的大周期回调/空头发力 |
| source_semantics | 这种高周期逆主趋势回调单属于逆势，江河只愿小盈亏比、小赚，不太贪，更倾向等待下方防守位再做主方向 |
| linked_claim_ids | JH-CLM-029-006 |
| family | JH-FAMILY-B |
| boundary | “小盈亏比”未给统一数字 |

## JH-CASE-031-001 — 错误反转空被否定，重新分类并低边找多

| 字段 | 内容 |
|---|---|
| source | 031 / BV1WQ6UBVECE / 约 00:01:50–00:07:02 |
| case_type | WRONG_CONTEXT_LOOKALIKE |
| initial_lookalike | 局部结构看似出现更低高/低点，学生考虑反转做空 |
| rejection_reason | 原强上涨主要发力/防守仍未破；市场只是动能和节奏变弱 |
| reclassification | 更可能弱震荡或弱上涨，而非立即高周期反转 |
| location | 原趋势防守可能成为后续震荡底边 |
| trigger | 到底部候选后等待实体收回/吞没向上行为 |
| management | 不预设静态 TP；至少等反向 K 后再结合强弱退出 |
| linked_claim_ids | JH-CLM-031-001,002,003 |
| family | JH-FAMILY-A / JH-FAMILY-D |

## JH-CASE-032-001 — 左侧轻仓多单与“分段拿利润”

| 字段 | 内容 |
|---|---|
| source | 032 / BV1FfkKBxEE3 / 约 00:00:24–00:05:42 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 强背景下的区间/震荡交易，来源允许更早左侧介入 |
| entry | 偏左侧；因此相应缩小仓位 |
| stop | 预设结构止损，短暂浮亏不提前慌张离场 |
| exit | 因现实时间约束预设前高上半部目标，约 1:2.33/2.34；仅案例，不是统一规则 |
| transition | 原震荡单完成后市场出现强突破；来源明确说后续再按突破逻辑做，可把行情/利润分段获取 |
| linked_claim_ids | JH-CLM-032-001,002 |
| family | JH-FAMILY-D → JH-FAMILY-C |

## JH-CASE-032-002 — 宽幅震荡上沿空单

| 字段 | 内容 |
|---|---|
| source | 032 / BV1FfkKBxEE3 / 约 00:06:34–00:09:59 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 标准宽幅震荡：外部不创新高低，内部可创新内部高低 |
| location | 只关注上、下边界；本单在上边缘 |
| trigger | 到边界后不直接进；多次向上推动未创新高，阴线收 K 后做空 |
| stop | 上方结构另一侧 |
| management | 不预设 TP；价格到内部关键/发力点后不全平，而把止损下移到内部关键点，使剩余仓位不再亏损 |
| exit | 到宽幅震荡下边缘离场 |
| linked_claim_ids | JH-CLM-032-003,004,005 |
| family | JH-FAMILY-D |

## JH-CASE-033-001 — 第三方学生“做强舍弱”案例

| 字段 | 内容 |
|---|---|
| source | 033 / BV1MjzzBpErm / 约 00:00:44–00:01:48 |
| case_type | OTHER |
| provenance | ATTRIBUTED_THIRD_PARTY |
| student_system | 做强舍弱；结构突破、强势市场压缩回调；若进场后不能快速按预期运行则快速砍仓 |
| jianghe_statement | 江河明确说“进场逻辑基本上都跟我一样” |
| transfer_boundary | 只能记录该相似性评价；学生的快速时间/动能退出、具体风险习惯不得升级为江河本人 EXPLICIT 管理规则 |
| linked_claim_ids | JH-CLM-033-001 |
| family | NONE — 不作为江河 Family 的独立证据 |
| outcome_boundary | 1万到30万等结果叙事只属于 SOURCE_CASE_CONTENT，不是 validity evidence |

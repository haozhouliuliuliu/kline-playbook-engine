# 江河交易员案例库 V0.1

案例用于保留来源语义和反例边界。任何“盈利”“止盈”文字仅说明视频中的案例内容，绝非经济优势或有效性证据。

## JH-CASE-005-001

| 字段 | 内容 |
|---|---|
| source_ordinal / BVID / 时间 | 005 / BV16fxYzGEA3 / 00:00:30–00:11:00 |
| case_type | OTHER |
| market_context / 高周期 | 关键位互动；高周期 UNKNOWN |
| execution_timeframe | 5m（画关键位） |
| location / setup | 关键位，上方关键位的价格反应 |
| trigger / entry | 等待排斥/回踩确认；精确触发 UNKNOWN |
| stop_or_invalidation | 案例口述止损在下方 |
| management / exit | 当时不预设止盈；价格反应不利时可尽快离场 |
| why_valid / why_invalid_if_failed | 仅在关键位与反应共同出现时才有语境；无反应则不是完整许可 |
| linked_claim_ids / family | JH-CLM-005-001, JH-CLM-005-002 / JH-FAMILY-A, JH-FAMILY-B |
| ambiguity / review | 排斥强弱和画区边界待复核 / SOL_REVIEW_REQUIRED |

## JH-CASE-012-001

| 字段 | 内容 |
|---|---|
| source_ordinal / BVID / 时间 | 012 / BV1Gv1fBYEp9 / 00:05:27–00:05:59 |
| case_type | INVALIDATION |
| market_context / 高周期 | 空头趋势衰弱；15m 口述趋势变化 |
| execution_timeframe | 15m |
| location / setup | 空头防守位与前低附近 |
| trigger / entry | 未创新低后出现原防守位被破；精确入场 UNKNOWN |
| stop_or_invalidation | 原空头防守位被打破 |
| management / exit | 案例已有主动止盈离场说明 |
| why_valid / why_invalid_if_failed | 保留“未创新低 + 防守位破”的结构链；不把它单独量化为反转算法 |
| linked_claim_ids / family | JH-CLM-012-001 / JH-FAMILY-B |
| ambiguity / review | 防守位精确画法 UNKNOWN / READY |

## JH-CASE-020-001

| 字段 | 内容 |
|---|---|
| source_ordinal / BVID / 时间 | 020 / BV1nDU8B6EjV / 00:00:36–00:01:22 |
| case_type | OTHER |
| market_context / 高周期 | 15m 宽震荡 |
| execution_timeframe | 15m |
| location / setup | 震荡空间上沿、长上影线语境 |
| trigger / entry | 订单挂在所述 K 线低点；精确触发需看原画面 |
| stop_or_invalidation | 前阳线高点上方 |
| management / exit | 仓位较轻、可能加仓；同片段另有 1:1 目标语境 |
| why_valid / why_invalid_if_failed | 位置位于边界而非中间；1:1 不可外推为统一目标 |
| linked_claim_ids / family | JH-CLM-020-001, JH-CLM-020-002 / JH-FAMILY-D |
| ambiguity / review | 目标与仓位比例范围待复核 / SOL_REVIEW_REQUIRED |

## JH-CASE-021-001

| 字段 | 内容 |
|---|---|
| source_ordinal / BVID / 时间 | 021 / BV1fT2iBjEeE / 00:02:38–00:06:22 |
| case_type | POSITIVE_EXAMPLE |
| market_context / 高周期 | 震荡；高周期 UNKNOWN |
| execution_timeframe | UNKNOWN |
| location / setup | 震荡上/下边界，等待二推 |
| trigger / entry | 二推动能不足、第二次不能创新高后等待反向确认 |
| stop_or_invalidation | 所指结构位置上方 |
| management / exit | 当时止盈不预设 |
| why_valid / why_invalid_if_failed | 边界 + 二推反证共同构成语境；震荡中间不做 |
| linked_claim_ids / family | JH-CLM-021-001, JH-CLM-021-002, JH-CLM-021-003 / JH-FAMILY-D |
| ambiguity / review | 动能不足定义、仓位比例待固定 / SOL_REVIEW_REQUIRED |

## JH-CASE-023-001

| 字段 | 内容 |
|---|---|
| source_ordinal / BVID / 时间 | 023 / BV1RKmmB6EFW / 00:02:16–00:03:50 |
| case_type | WRONG_CONTEXT_LOOKALIKE |
| market_context / 高周期 | 原震荡空间后的突破候选 |
| execution_timeframe | 更小级别周期（数值 UNKNOWN） |
| location / setup | 原震荡边界 |
| trigger / entry | 真突破需离开原空间，并转小周期复查 |
| stop_or_invalidation | 快速回到原空间为失败线索 |
| management / exit | 趋势订单管理取决于后续趋势结构 |
| why_valid / why_invalid_if_failed | 仅刺破边界或未拉开距离属于相似但不合格情形 |
| linked_claim_ids / family | JH-CLM-023-001 / JH-FAMILY-C |
| ambiguity / review | 距离/跟随阈值 UNKNOWN / READY |

## JH-CASE-024-001

| 字段 | 内容 |
|---|---|
| source_ordinal / BVID / 时间 | 024 / BV1oWqDBbEuh / 00:06:23–00:12:37 |
| case_type | OTHER |
| market_context / 高周期 | 趋势中的 ABC 回调延续；高周期 UNKNOWN |
| execution_timeframe | UNKNOWN |
| location / setup | A 段之后的弱 B 回调 |
| trigger / entry | 顺向确认 K 收盘或突破其高/低点条件单 |
| stop_or_invalidation | 回调/入场结构极值之外或 A 起始点之外的宽止损语境 |
| management / exit | 最多两次加仓、风险分份为来源局部证据 |
| why_valid / why_invalid_if_failed | A 的已确认数量条件可记录；B 过深/连续回调边界未补参数 |
| linked_claim_ids / family | JH-CLM-024-001, JH-CLM-024-002 / JH-FAMILY-A |
| ambiguity / review | B 根数与数字适用范围 / SOL_REVIEW_REQUIRED |

## JH-CASE-027-001

| 字段 | 内容 |
|---|---|
| source_ordinal / BVID / 时间 | 027 / BV1bivsBBEW7 / 00:01:59–00:06:19 |
| case_type | FAILED_EXAMPLE |
| market_context / 高周期 | 宽幅震荡 |
| execution_timeframe | UNKNOWN |
| location / setup | 震荡边缘、二推回撤 |
| trigger / entry | 二推未创新高构成反转线索 |
| stop_or_invalidation | 案例被止损；成功突破后震荡逻辑失效 |
| management / exit | 初始仓轻、震荡中不贪、可提前离场 |
| why_valid / why_invalid_if_failed | 止损不自动否定后续独立条件；成功突破要求重新分类 |
| linked_claim_ids / family | JH-CLM-027-001, JH-CLM-027-002 / JH-FAMILY-D（突破后可切换 JH-FAMILY-C） |
| ambiguity / review | 真突破阈值仍 UNKNOWN / READY |

## JH-CASE-027-002

| 字段 | 内容 |
|---|---|
| source_ordinal / BVID / 时间 | 027 / BV1bivsBBEW7 / 00:06:07–00:06:20 |
| case_type | INVALIDATION |
| market_context / 高周期 | 原宽幅震荡 |
| execution_timeframe | UNKNOWN |
| location / setup | 震荡空间边缘后的成功突破候选 |
| trigger / entry | 成功突破后重新分类；不沿用原震荡逻辑 |
| stop_or_invalidation | 原震荡假设被突破否认 |
| management / exit | UNKNOWN |
| why_valid / why_invalid_if_failed | 是震荡反转模型的硬负例与机制切换点 |
| linked_claim_ids / family | JH-CLM-027-002 / JH-FAMILY-D → JH-FAMILY-C |
| ambiguity / review | 成功突破仍需 C 家族的距离/跟随条件 / READY |

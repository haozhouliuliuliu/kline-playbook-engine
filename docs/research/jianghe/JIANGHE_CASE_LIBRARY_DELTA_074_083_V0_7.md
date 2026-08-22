# 江河交易员案例库增量 074–083 V0.7

仅保存来源语义和边界；盈利金额、R倍数与账户结果只属于 `SOURCE_CASE_CONTENT`，不是策略有效性证据。

## JH-CASE-074-001 — 弱空微波段：5m逻辑→1m优化进场

| 字段 | 内容 |
|---|---|
| source | 074 / BV1KjLz6fEav / 约 00:03:55–00:05:18 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 原下跌被上涨打破，上涨延续很乱并很快再次被下跌破坏，重新形成弱空结构 |
| higher_timeframe_context | 5m 为交易主周期 |
| execution_timeframe | 1m 仅用于拿更优点位 |
| location | 空头结构防守位 / 发力点 |
| setup | 弱空结构成立，价格回到防守/发力位置 |
| trigger | 低周期优化后的做空执行；精确K线触发仍依原视频 |
| stop_or_invalidation | 上方结构 |
| management | 未预设固定TP，按微波段持有 |
| exit | 下方预期区域附近结束；具体结果仅为source case content |
| linked_claim_ids | JH-CLM-074-002, JH-CLM-074-003 |
| family | JH-FAMILY-A |

## JH-CASE-077-001 — 1H弱空/宽震荡上区→5m弱空顺势空

| 字段 | 内容 |
|---|---|
| source | 077 / BV14vGQ6WEFF / 约 00:00:30–00:01:50 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 1H可合理解释为宽幅震荡或弱空，两种分类都指向上方高价值区域 |
| higher_timeframe_context | 1H 定位上方区域 |
| execution_timeframe | 5m |
| location | 上方区域内最近弱空发力点 |
| setup | 到位后5m出现转折并形成弱空结构 |
| trigger | 回到最近发力位做空 |
| stop_or_invalidation | 上方结构；具体距离未统一 |
| management | 顺着下跌推动持有 |
| family | JH-FAMILY-A / JH-FAMILY-D 的共享许可语境 |
| linked_claim_ids | JH-CLM-077-001 |
| hard_negative | 1H到上方区域即直接空，而没有5m真实转折 |

## JH-CASE-077-002 — 5m宽震荡下区→1m强弱转换左侧多→新信号重进

| 字段 | 内容 |
|---|---|
| source | 077 / BV14vGQ6WEFF / 约 00:02:28–00:07:54 |
| case_type | POSITIVE_EXAMPLE / REENTRY |
| market_context | 强下跌后整体动能明显减弱、横向化，按宽幅震荡处理 |
| higher_timeframe_context | 5m下方关键区域 |
| execution_timeframe | 1m优化进场 |
| setup | 1m空头由趋势型K转非趋势型K减弱，随后多头连续增强 |
| trigger | 偏左侧多单 |
| second_entry | 同一5m关键区域后来出现新的独立进场信号，再次进多 |
| stop_or_invalidation | 下方结构 |
| management | 盈利后把止损向上推进，最终由移动止损退出 |
| family | JH-FAMILY-D / JH-FAMILY-B |
| linked_claim_ids | JH-CLM-077-002, JH-CLM-077-003 |
| hard_negative | 同一区域无新信号时仅因上一单/旧理由重进 |

## JH-CASE-077-003 — 弱空防守位与次级关键高点顺空

| 字段 | 内容 |
|---|---|
| source | 077 / BV14vGQ6WEFF / 约 00:08:04–00:08:57 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 弱空趋势 |
| location | 最初发力点/防守位；推动中衍生的两个次级关键高点 |
| setup | 价格回抽到次级关键高点 |
| trigger | 顺空捕捉 |
| management | 止损随盈利向下调整；预期下方区域 |
| family | JH-FAMILY-A |
| linked_claim_ids | JH-CLM-077-004 |

## JH-CASE-079-001 — 发力点上移背景中的强弱转换多单

| 字段 | 内容 |
|---|---|
| source | 079 / BV1W37165EEZ / 约 00:08:10–00:11:51 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 发力点持续向上移动，多军持续掌控 |
| location | 最近多头发力点 |
| setup | 空头回调来到多头发力点后，趋势型K转非趋势型K、实体减弱；随后强阳否认空头 |
| trigger | 强阳收K后做多 |
| stop_or_invalidation | 下方结构低点 |
| management | 微波段；目标上方空头发力点区域 |
| exit | 到上方目标区域后止盈 |
| family | JH-FAMILY-A |
| linked_claim_ids | JH-CLM-079-004 |

## JH-CASE-079-002 — 强弱强的有效/无效对照组

| 字段 | 内容 |
|---|---|
| source | 079 / BV1W37165EEZ / 约 00:11:56–00:16:55 |
| case_type | POSITIVE_EXAMPLE + WRONG_CONTEXT_LOOKALIKE |
| market_context | 原方向发力点持续移动、趋势仍由原方向掌控 |
| valid_setup | 强原方向推动 → 微弱逆向回调K/非趋势K → 原方向实体饱满K重新增强 |
| invalid_setup | 逆向K本身并不弱，随后直接出现原方向K；双方更像对抗态而非“强-弱-强” |
| trigger | 有效案例中原方向强K收K后进入 |
| stop_or_invalidation | 结构另一侧 |
| family | JH-FAMILY-A |
| linked_claim_ids | JH-CLM-079-005 |

## JH-CASE-081-001 — 弱空高空：计划10手拆成5+5分批进入

| 字段 | 内容 |
|---|---|
| source | 081 / BV1WvER6kEeZ / 约 00:00:24–00:04:50 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 5m下跌仍有效但动能减弱、回调频率增加 |
| location | 最近空头发力点构成相对高位 |
| setup | 只做高空，不追空 |
| entry | 原计划总量10手拆成5手+5手：第一笔按信号，第二笔争取更优价格；不是新增风险意义上的加仓 |
| stop_or_invalidation | 上方结构 |
| exit | 微波段拿到下方前低预期区 |
| family | JH-FAMILY-A |
| linked_claim_ids | JH-CLM-081-001, JH-CLM-081-002, JH-CLM-081-003 |

## JH-CASE-081-002 — 5m弱空发力位→1m多头强转弱→空

| 字段 | 内容 |
|---|---|
| source | 081 / BV1WvER6kEeZ / 约 00:04:56–00:06:24 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 5m弱空趋势，只允许高空 |
| higher_timeframe_context | 5m最后空头发力点定位相对高位 |
| execution_timeframe | 1m |
| setup | 价格到发力点后，1m多头由强转弱，随后空头发力 |
| trigger | 空头发力确认后进空 |
| stop_or_invalidation | 上方结构 |
| exit | 弱空利润尺度，目标下方多头发力点 |
| family | JH-FAMILY-A |
| linked_claim_ids | JH-CLM-081-004 |

V078/V080/V082/V083主要提供系统定义、风险/学习/执行原则与hard negatives，不因缺少单一完整订单而强行创建case。

# 江河交易员表面矛盾登记 V0.8（001–093）

`RESOLVED_*` 只表示来源语境足以解释，不代表相关机器阈值已经完成。

| contradiction_id | 主题 | 当前状态 | 来源化结论 |
|---|---|---|---|
| JH-CON-001 | 固定止盈 vs 动态结构离场 | RESOLVED_CONTEXTUAL_ALTERNATIVES | 退出方式与订单模式、市场节奏、个人状态一致。V088继续动态推止损；V090因时间晚/状态差改用固定止盈。不是盘中任意切换。 |
| JH-CON-002 | 1:1 的适用范围 | RESOLVED_NOT_UNIVERSAL | 不同订单模式、趋势强弱和空间允许不同目标，1:1不是所有Family统一硬门槛。 |
| JH-CON-003 | ABC B 回调根数 | RESOLVED_SOURCE_EXPLICIT | V024两条独立放弃规则保持不变。 |
| JH-CON-004 | 左侧 vs 右侧入场 | RESOLVED_CONTEXTUAL_VARIANTS | 确认程度、评分、市场阶段和风险分配决定进入方式。 |
| JH-CON-005 | 趋势初期 vs 非初期退出 | POSSIBLE_CONTEXT_RESOLUTION | 阶段影响持有/保护利润；V093再次明确非初期降低预期，但阶段机器定义仍UNKNOWN。 |
| JH-CON-006 | 不同Family的仓位规则 | POSSIBLE_CONTEXT_RESOLUTION | 震荡0.5×、ABC分份、评分、左侧缩仓、无共振轻仓、以损定仓、计划内分仓并存，可能由统一风险预算+质量修正解释，但母规则仍未给全。 |
| JH-CON-007 | 评分开仓阈值 `>3` vs `>=3` | SOL_REVIEW_REQUIRED / SOURCE_INTERNAL_LANGUAGE_CONFLICT | V030同片段仍无法唯一确定3分是否允许开仓。 |
| JH-CON-008 | 剥头皮教学很多 vs 本人平时少做 | RESOLVED_NON_CORE_DEMONSTRATION_MODE | V074明确本人当前主做日内波段/微波段；V084/V086的短单不改变NON_CORE定位。 |
| JH-CON-009 | “震荡” vs “弱趋势/内部偏向”是否必须唯一分类 | RESOLVED_ACTION_OVERLAP_ALLOWED | V090再次出现1H弱多与5m震荡下沿共享低多许可，继续支持重叠分类。 |
| JH-CON-010 | “应变” vs “盘中不要分析/灵机一动” | RESOLVED_SYSTEM_ARCHITECTURE | 构建阶段预案，盘中客观识别条件并切换既有方案；V093由突破回踩预案切换到强势浅回调续势属于依据新信息重分类。 |
| JH-CON-011 | 强反向运动是否等于趋势已反转 | RESOLVED_STAGED_RECLASSIFICATION | V090的1H内部空头N只削弱原多头结构、尚未否认，再次支持分阶段重分类。 |
| JH-CON-012 | 止损/亏损是否等于交易失败 | RESOLVED_PROCESS_VS_OUTCOME | V084盈利但本人认为执行很差；V089明确正常亏损是成本、违规亏损是罚款；V092说明违规盈利也会强化坏习惯。 |
| JH-CON-013 | “裸K”定位 vs 使用均线/指标 | RESOLVED_AUXILIARY_NOT_CORE | K线/价格仍为核心直接信息，均线/指标只作辅助，不创建指标Family。 |
| JH-CON-014 | 多周期共振是否所有订单硬门槛 | RESOLVED_NOT_UNIVERSAL_QUALITY_MODIFIER | 无共振仍可做独立周期但降质量/轻仓；本批无反证。 |
| JH-CON-015 | 做多偏向是否等于看到多信号就必须进 | RESOLVED_FILTER_NOT_TRIGGER | V088再次明确位置/偏向先过滤反向信号，但同向仍需独立触发。 |
| JH-CON-016 | 早期“内部N/内部结构”用于管理/触发 vs V069“内部结构不给交易机会” | SOL_REVIEW_REQUIRED / POSSIBLE_TERMINOLOGY_SCOPE_CONFLICT | V090继续把1H内部空头N用于“削弱/重分类”而非直接进场，支持其确认作用；但早期用词范围仍需统一。 |
| JH-CON-017 | “不同周期本质相同” vs 周期会影响交易结果 | RESOLVED_AGGREGATION_VS_COST | 聚合尺度改变结构可见性、频率、成本和执行状态，不冲突。 |
| JH-CON-018 | 动态跟随利润 vs 剥头皮/微波段按目标退出 | RESOLVED_ORDER_MODE_DEPENDENT | 订单模式在进场前定义，退出按原模式评价；V086也说明高R可由成本端优化而非无限延长持仓。 |
| JH-CON-019 | V079近期高低点止损 vs “进场K收盘价止损” | SOL_REVIEW_REQUIRED / SOURCE_INTERNAL_TEXT_VISUAL_CONFLICT | 课件/口语与同页图示/后续案例不一致，不能唯一解释。 |
| JH-CON-020 | 突破交易 vs 回调交易谁更优 | RESOLVED_MARKET_RHYTHM_DEPENDENT | 强势/低回调市场更适合突破，弱趋势/深回调市场更适合回调；无绝对优劣。 |
| JH-CON-021 | “上涨趋势不做空/下跌趋势不做多” vs Family B反转交易 | RESOLVED_TREND_INTACT_VS_TRANSITION | V085针对仍完整趋势中为抓唯一顶底而逆势的低概率行为；Family B要求原趋势已衰弱/末期并出现新方向接管证据，因此不是在完整趋势中盲目逆势。 |
| JH-CON-022 | 强势市场更适合突破 vs V093强势市场抓浅回调转折 | RESOLVED_PHASE_DEPENDENT | 强势失衡的启动/破位阶段更偏Family C；突破完成、趋势已建立且只给浅回调时，可由Family A浅回调续势接管。两个手法对应不同阶段，不冲突。 |

当前开放核心项：`JH-CON-005/006/007/016/019`。007和019属于明确来源内部冲突；016需继续统一“内部结构/内部N”术语范围。

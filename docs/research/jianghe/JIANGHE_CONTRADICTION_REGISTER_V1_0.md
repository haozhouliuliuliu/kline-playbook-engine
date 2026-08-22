# 江河交易员 Contradiction Register V1.0（001–099 Final）

`RESOLVED_*` 表示来源语境足以解释或已确认其为来源内部冲突；不代表相关机器阈值已经完成。

| contradiction_id | 主题 | V1.0状态 | 来源化结论 |
|---|---|---|---|
| JH-CON-001 | 固定止盈 vs 动态结构离场 | RESOLVED_CONTEXTUAL_ALTERNATIVES | V017正式把固定RR、关键位置/空间、动态市场结构列为三种可用退出方式；本人偏动态，但没有绝对优劣，需与订单模式一致。 |
| JH-CON-002 | 1:1适用范围 | RESOLVED_NOT_UNIVERSAL | 不同模式、趋势强弱、空间可用不同目标；1:1不是全Family硬门槛。 |
| JH-CON-003 | ABC B回调根数 | RESOLVED_SOURCE_EXPLICIT | 既有V024两条独立放弃规则保持。 |
| JH-CON-004 | 左侧 vs 右侧入场 | RESOLVED_CONTEXTUAL_VARIANTS | 确认程度、评分、阶段、风险分配决定。 |
| JH-CON-005 | 趋势初期 vs 非初期退出 | **RESOLVED_STAGE_DEPENDENT** | V017明确：趋势初期可右侧退出给空间；非初期可更早/左侧退出降低风险。统一阶段机器算法仍UNKNOWN。 |
| JH-CON-006 | 不同Family仓位规则 | **PARTIALLY_RESOLVED_QUALITY_RISK_HIERARCHY** | 震荡0.5×、评分、左侧缩仓、无共振轻仓、以损定仓、状态缩仓、V099质量分层可由“风险预算+质量修正”解释大部分，但统一母公式未被来源给全。 |
| JH-CON-007 | 评分开仓阈值 `>3` vs `>=3` | **RESOLVED_AS_SOURCE_INTERNAL_INCONSISTENCY / MACHINE_BOUNDARY_NOT_PINNED** | V030同段同时说“高于3分才开”和“3分使用3000美元仓位”。不替作者选择边界。 |
| JH-CON-008 | 剥头皮教学很多 vs 本人平时少做 | RESOLVED_NON_CORE_DEMONSTRATION_MODE | 保持NON_CORE。 |
| JH-CON-009 | 震荡 vs 弱趋势/内部偏向是否必须唯一分类 | RESOLVED_ACTION_OVERLAP_ALLOWED | 可重叠分类并共享同方向许可。 |
| JH-CON-010 | “应变” vs “盘中不要分析/灵机一动” | RESOLVED_SYSTEM_ARCHITECTURE | 盘前构建预案；盘中依据客观条件切已有方案，不临场造理由。 |
| JH-CON-011 | 强反向运动是否等于趋势已反转 | RESOLVED_STAGED_RECLASSIFICATION | 先削弱/重分类，再等新方向接管。 |
| JH-CON-012 | 止损/亏损是否等于交易失败 | RESOLVED_PROCESS_VS_OUTCOME | 过程质量与结果分离。 |
| JH-CON-013 | “裸K” vs 使用均线/指标 | RESOLVED_AUXILIARY_NOT_CORE | 价格/K线是核心；均线/指标只辅助。 |
| JH-CON-014 | 多周期共振是否所有订单硬门槛 | RESOLVED_NOT_UNIVERSAL_QUALITY_MODIFIER | 单周期允许，但质量/仓位降级。 |
| JH-CON-015 | 做多偏向是否等于看到多信号就必须进 | RESOLVED_FILTER_NOT_TRIGGER | 偏向/位置过滤方向，同向仍需独立触发。 |
| JH-CON-016 | 早期“内部N/内部结构”用法 vs V069“不提供交易机会” | **RESOLVED_ROLE_SCOPE_INTERNAL_CONFIRMATION_NOT_ENTRY** | 同周期内部结构可用于确认外部结构、强弱、重分类、管理/防守；不独立给交易许可。要低周期触发必须切到真实低周期重识别。V018进一步支持。 |
| JH-CON-017 | 不同周期本质相同 vs 周期影响结果 | RESOLVED_AGGREGATION_VS_COST | 同一价格过程不同聚合；结构可见性、频率、成本、状态不同。 |
| JH-CON-018 | 动态跟随利润 vs 剥头皮/微波段目标退出 | RESOLVED_ORDER_MODE_DEPENDENT | 订单模式进场前定义；退出按原模式评价。 |
| JH-CON-019 | V079近期高低点止损 vs 进场K收盘价止损 | **RESOLVED_AS_SOURCE_INTERNAL_TEXT_VISUAL_CONFLICT / CLOSE_STOP_NOT_MACHINE_ELIGIBLE** | 文字/口语与同源图示/案例冲突。稳定保留结构/近期高低点止损；收盘价分支不机器化。 |
| JH-CON-020 | 突破交易 vs 回调交易谁更优 | RESOLVED_MARKET_RHYTHM_DEPENDENT | 强势/低回调更适合突破，弱趋势/深回调更适合回调，无绝对优劣。 |
| JH-CON-021 | 上涨不做空/下跌不做多 vs Family B反转 | RESOLVED_TREND_INTACT_VS_TRANSITION | Family B要求原趋势已衰弱/被否认且新方向接管，不是完整趋势中盲目逆势。 |
| JH-CON-022 | 强势市场更适合突破 vs 强势市场抓浅回调 | RESOLVED_PHASE_DEPENDENT | 启动/破位阶段偏C；突破后强趋势浅回调可由A接管。 |

## Final open contradiction count

严格意义的“待Sol解释矛盾”已经为0。

仍未机器锁定的是：
- JH-CON-006背后的统一风险母公式；
- JH-CON-007的3分边界；
- JH-CON-019的收盘价止损语义。

它们已被正确分类为**来源不足/来源内部冲突**，不是继续等待项目自行猜解的矛盾。

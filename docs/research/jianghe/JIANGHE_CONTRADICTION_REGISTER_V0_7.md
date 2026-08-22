# 江河交易员表面矛盾登记 V0.7（001–083）

`RESOLVED_*` 只表示来源语境足以解释，不代表相关机器阈值已经完成。

| contradiction_id | 主题 | 当前状态 | 来源化结论 |
|---|---|---|---|
| JH-CON-001 | 固定止盈 vs 动态结构离场 | RESOLVED_CONTEXTUAL_ALTERNATIVES | 既有三类退出保持。V074/V080/V081进一步明确：退出方式与进场前订单类型、市场节奏一致；微波段可动态或有限空间退出，剥头皮按更敏感尺度退出。不是盘中任意切换。 |
| JH-CON-002 | 1:1 的适用范围 | RESOLVED_NOT_UNIVERSAL | 既有结论保持。不同订单模式、趋势强弱和空间允许不同目标，1:1不是所有Family统一硬门槛。 |
| JH-CON-003 | ABC B 回调根数 | RESOLVED_SOURCE_EXPLICIT | V024两条独立放弃规则保持不变。 |
| JH-CON-004 | 左侧 vs 右侧入场 | RESOLVED_CONTEXTUAL_VARIANTS | 既有结论保持。V077继续展示左侧强弱转换进入与后续新信号重进，确认程度和风险分配决定进入方式。 |
| JH-CON-005 | 趋势初期 vs 非初期退出 | POSSIBLE_CONTEXT_RESOLUTION | 阶段影响持有/保护利润，但阶段机器定义仍UNKNOWN。 |
| JH-CON-006 | 不同Family的仓位规则 | POSSIBLE_CONTEXT_RESOLUTION | 震荡0.5×、ABC分份、评分、左侧缩仓、无共振轻仓、以损定仓、计划内分仓并存，可能由统一风险预算+质量修正解释，但母规则仍未给全。 |
| JH-CON-007 | 评分开仓阈值 `>3` vs `>=3` | SOL_REVIEW_REQUIRED / SOURCE_INTERNAL_LANGUAGE_CONFLICT | V030同片段仍无法唯一确定3分是否允许开仓。 |
| JH-CON-008 | 剥头皮教学很多 vs 本人平时少做 | RESOLVED_NON_CORE_DEMONSTRATION_MODE | V040/V043已显示非核心；V074进一步明确本人当前主做日内波段/微波段，大量剥头皮内容部分受直播/视频展示效率影响。因此保持NON_CORE，不创建Family E。 |
| JH-CON-009 | “震荡” vs “弱趋势/内部偏向”是否必须唯一分类 | RESOLVED_ACTION_OVERLAP_ALLOWED | 既有重叠分类保持；V077再次出现1H宽幅震荡/弱空共享上方高空许可。 |
| JH-CON-010 | “应变” vs “盘中不要分析/灵机一动” | RESOLVED_SYSTEM_ARCHITECTURE | 构建阶段预案，盘中识别条件并切换既有方案。V078再次强调未来不可预测，要预先考虑涨/跌后的动作。 |
| JH-CON-011 | 强反向运动是否等于趋势已反转 | RESOLVED_STAGED_RECLASSIFICATION | 既有分阶段重分类保持；V078的平衡/失衡与强弱转换继续支持先读取控制权变化、再判断是否形成新结构。 |
| JH-CON-012 | 止损/亏损是否等于交易失败 | RESOLVED_PROCESS_VS_OUTCOME | 维持概率成本/风险控制解释。V083以无止损重仓偶然暴赚作为hard negative进一步支持“结果好≠过程正确”。 |
| JH-CON-013 | “裸K”定位 vs 使用均线/指标 | RESOLVED_AUXILIARY_NOT_CORE | V078明确：K线/价格是主要直接信息，指标只是辅助而非决策依据；本人有时会使用均线，某些环境还会利用指标滞后。故V061/V069的均线使用与裸K核心不冲突。参数和调用条件仍UNKNOWN。 |
| JH-CON-014 | 多周期共振是否所有订单硬门槛 | RESOLVED_NOT_UNIVERSAL_QUALITY_MODIFIER | V058/V060已确认无共振仍可做独立周期但降质量/轻仓；本批无反证。 |
| JH-CON-015 | 做多偏向是否等于看到多信号就必须进 | RESOLVED_FILTER_NOT_TRIGGER | 偏向仍是方向过滤器，不是自动触发器。V075/V078进一步要求市场节奏、位置与当下行为共同满足。 |
| JH-CON-016 | 早期“内部N/内部结构”用于管理/触发 vs V069“内部结构不给交易机会” | SOL_REVIEW_REQUIRED / POSSIBLE_TERMINOLOGY_SCOPE_CONFLICT | V069强措辞仍需与早期来源术语统一。V078说明大小周期是同一价格过程的不同聚合，但并未解决“同周期内部结构”是否可独立触发的问题。 |
| JH-CON-017 | “不同周期本质相同” vs 周期会影响交易结果 | RESOLVED_AGGREGATION_VS_COST | V072/V078共同支持：价格过程相同，但聚合尺度改变可见结构、频率、成本和执行状态，因此不冲突。 |
| JH-CON-018 | 动态跟随利润 vs 剥头皮/微波段按目标退出 | RESOLVED_ORDER_MODE_DEPENDENT | V073/V074/V080/V081共同明确：订单模式在进场前定义，退出按原模式评价。事后行情继续运行不能重写原规则。 |
| JH-CON-019 | V079近期高低点止损 vs “进场K收盘价止损” | SOL_REVIEW_REQUIRED / SOURCE_INTERNAL_TEXT_VISUAL_CONFLICT | V079课件/口语先说止损通常放近期高低点；同页又写若近期高低点就是当前进场K，可把止损放该K收盘价。但同页图示及随后实际案例仍把止损画在K线极值之外。当前不能唯一解释“收盘价”真实适用含义，不升级为规则。 |
| JH-CON-020 | 突破交易 vs 回调交易谁更优 | RESOLVED_MARKET_RHYTHM_DEPENDENT | V075明确二者无绝对优劣：强势/低回调市场更适合突破，弱趋势/深回调市场更适合回调。方法优劣取决于市场节奏和个人体系，而非固定排名。 |

当前开放核心项：`JH-CON-005/006/007/016/019`。其中007和019属于明确来源内部冲突；016需要继续回查早期“内部结构/内部N”术语范围。

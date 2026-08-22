# 江河交易员表面矛盾登记 V0.5（001–063）

`RESOLVED_*` 只表示来源语境足以解释，不代表机器阈值已完成。

| contradiction_id | 主题 | 当前状态 | 来源化结论 |
|---|---|---|---|
| JH-CON-001 | 固定止盈 vs 动态结构离场 | RESOLVED_CONTEXTUAL_ALTERNATIVES | V017明确三种退出且本人偏好动态；V057/V059/V060/V061继续显示弱趋势、独立周期、加仓后风险变化等场景可改用更保守固定/实体参考目标。不是任意切换，而是情境化方法。 |
| JH-CON-002 | 1:1 的适用范围 | RESOLVED_NOT_UNIVERSAL | 既有结论保持；V063最终不足1:1也因震荡中动能失效主动退出，再次证明不是所有订单硬门槛。 |
| JH-CON-003 | ABC B 回调根数 | RESOLVED_SOURCE_EXPLICIT | V024两条独立放弃规则保持不变。 |
| JH-CON-004 | 左侧 vs 右侧入场 | RESOLVED_CONTEXTUAL_VARIANTS | 既有结论保持；V055/V061继续显示可按确认程度和评分调整进入时机/仓位。 |
| JH-CON-005 | 趋势初期 vs 非初期退出 | POSSIBLE_CONTEXT_RESOLUTION | 阶段影响持有/保护利润，但阶段机器定义仍UNKNOWN。 |
| JH-CON-006 | 不同Family的仓位规则 | POSSIBLE_CONTEXT_RESOLUTION | 震荡0.5×、ABC分份、评分、左侧缩仓、无共振轻仓、低评分0.5×、两次半仓尝试并存，可能由统一风险预算+质量修正解释，但母规则仍未给全。 |
| JH-CON-007 | 评分开仓阈值 `>3` vs `>=3` | SOL_REVIEW_REQUIRED / SOURCE_INTERNAL_LANGUAGE_CONFLICT | V030同片段仍无法唯一确定3分是否允许开仓。保持Sol review项。 |
| JH-CON-008 | 剥头皮教学很多 vs 本人平时少做 | RESOLVED_NON_CORE_DEMONSTRATION_MODE | 维持非核心执行模式，不创建Family E。 |
| JH-CON-009 | “震荡” vs “弱趋势”是否必须唯一分类 | RESOLVED_ACTION_OVERLAP_ALLOWED | V062再次出现大空背景与宽幅震荡同时支持高位空，继续证明可保留重叠分类。 |
| JH-CON-010 | “应变” vs “盘中不要灵机一动” | RESOLVED_SYSTEM_ARCHITECTURE | 构建阶段预案，盘中识别条件并切换方案；不等于临场发明理由。 |
| JH-CON-011 | 强反向运动是否等于趋势已反转 | RESOLVED_STAGED_RECLASSIFICATION | V055再次区分“强反向推动/破发力点”与“完整高低点下降结构”，强化分阶段重分类。 |
| JH-CON-012 | 止损/亏损是否等于交易失败 | RESOLVED_PROCESS_VS_OUTCOME | 维持概率成本/风险控制解释。V061首单止损后新条件再进进一步支持。 |
| JH-CON-013 | “裸K”定位 vs V061使用均线 | POSSIBLE_CONTEXT_RESOLUTION | V061原视频明确把“触碰均线”作为重进场辅助证据；V056只是反对把指标/量化当作不劳而获捷径，并未声明永远不用指标。当前最保守解释是均线可作为辅助证据，但是否属于稳定系统模块仍UNKNOWN。 |
| JH-CON-014 | 多周期共振是否所有订单硬门槛 | RESOLVED_NOT_UNIVERSAL_QUALITY_MODIFIER | V058明确1H/5m无良好共振时可做5m独立周期；V060进一步说明这种单质量较低、一般轻仓。因此共振是质量加分项而不是普遍硬准入门槛。 |
| JH-CON-015 | 做多偏向是否等于看到多信号就必须进 | RESOLVED_FILTER_NOT_TRIGGER | V054明确：建立做多偏向后，多信号不一定做，但空信号一定不做。偏向是方向过滤器，不是自动触发器。 |

当前仍开放的核心项为 `JH-CON-005/006/007/013`。其中007是明确来源内部语言冲突；013需要后续来源确定均线的稳定系统地位。

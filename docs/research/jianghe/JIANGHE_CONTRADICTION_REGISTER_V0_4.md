# 江河交易员表面矛盾登记 V0.4（001–053）

`RESOLVED_*` 只表示来源语境足以解释，不代表相关机器阈值已经完成。

| contradiction_id | 主题 | 当前状态 | 来源化结论 |
|---|---|---|---|
| JH-CON-001 | 固定止盈 vs 动态结构离场 | RESOLVED_CONTEXTUAL_ALTERNATIVES | V017明确三种退出且本人偏好动态；V034/V036/V042/V047继续显示可按案例/市场状态切换。V050进一步要求进场模式与利润/退出尺度一致，因此不是盘中随意换方法。 |
| JH-CON-002 | 1:1 的适用范围 | RESOLVED_NOT_UNIVERSAL | V020已确认是案例空间预期；后续1:1.3、其他短目标也只属于相应案例/模式。 |
| JH-CON-003 | ABC B 回调根数 | RESOLVED_SOURCE_EXPLICIT | V024两条独立放弃规则保持不变：连续≥3根同向回调K；或≤3根快速回到/破坏A起始区域。 |
| JH-CON-004 | 左侧 vs 右侧入场 | RESOLVED_CONTEXTUAL_VARIANTS | V029/V032已解释；V038/V045继续显示早期/左侧确认可轻仓，右侧更多确认后再进入或加仓。 |
| JH-CON-005 | 趋势初期 vs 非初期退出 | POSSIBLE_CONTEXT_RESOLUTION | 阶段影响持有/保护利润，但阶段机器定义仍UNKNOWN。 |
| JH-CON-006 | 不同Family的仓位规则 | POSSIBLE_CONTEXT_RESOLUTION | 0.5×震荡、ABC分份、评分、左侧/剥头皮缩仓、V048状态不专注缩仓可由统一风险理念+情境修正解释，但母规则未给全。 |
| JH-CON-007 | 评分开仓阈值 `>3` vs `>=3` | SOL_REVIEW_REQUIRED / SOURCE_INTERNAL_LANGUAGE_CONFLICT | V030同片段仍无法唯一确定3分是否允许开仓。保持唯一Sol review项。 |
| JH-CON-008 | 剥头皮教学很多 vs 本人平时少做 | RESOLVED_NON_CORE_DEMONSTRATION_MODE | V040系统教学；V043明确平常少做、不特别擅长；V050只进一步说明订单模式管理。因此仍为非核心执行模式，不创建Family E。 |
| JH-CON-009 | “震荡” vs “弱趋势”是否必须唯一分类 | RESOLVED_ACTION_OVERLAP_ALLOWED | V042已允许合理重叠；V052再次明确弱空与震荡前期可共享上方关键区高空许可。若不同合理分类导向同一动作，可以先使用共同许可并等新信息再分类。 |
| JH-CON-010 | “应变” vs “盘中不要灵机一动” | RESOLVED_SYSTEM_ARCHITECTURE | V050明确：构建阶段预先设计条件/预案，盘中客观识别触发并调用方案。应变是预案切换，不是盘中即兴发明理由。 |
| JH-CON-011 | 强反向运动是否等于趋势已反转 | RESOLVED_STAGED_RECLASSIFICATION | V045/V050均明确：强反向运动可以先否定局部推进、形成止跌/弱化/大分歧，但在新方向高低点延续未形成前不能直接升级成完整高周期趋势反转。 |
| JH-CON-012 | 止损/亏损是否等于交易失败 | RESOLVED_PROCESS_VS_OUTCOME | V049明确止损/亏损是概率交易中的中性成本和风险控制；执行是否正确要看是否遵守体系和可控风险，而不是单笔盈亏。 |

当前仍开放的核心项是 `JH-CON-005/006/007`。其中007属于明确来源内部语言冲突，不能由工程或模型自行选择阈值。

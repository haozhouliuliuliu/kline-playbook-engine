# 江河交易员表面矛盾登记 V0.2（001–033）

`RESOLVED_*` 只表示来源语境已足以解释该项，不代表相关机器阈值已经完成。

| contradiction_id | 主题 | 当前状态 | 来源化结论 |
|---|---|---|---|
| JH-CON-001 | 固定止盈 vs 动态结构离场 | RESOLVED_CONTEXTUAL_ALTERNATIVES | V017 明确讨论三种退出：固定盈亏比、固定空间/目标、动态跟随市场；江河本人偏好动态跟随。它们是不同方法/语境，不是互相否定。 |
| JH-CON-002 | 1:1 的适用范围 | RESOLVED_NOT_UNIVERSAL | V020 先明确“不预设止盈”，随后说“至少拿个1:1应该不是问题”；因此 1:1 是该案例空间预期，不是统一固定 TP 或全 Family 硬门槛。 |
| JH-CON-003 | ABC B 回调根数 | RESOLVED_SOURCE_EXPLICIT | V024 明确：B 出现连续 ≥3 根同方向回调 K 则放弃；另若 B 在 ≤3 根内快速回到/破坏 A 起始区域也放弃。不得反推 B 总长度最多 2 根。 |
| JH-CON-004 | 左侧 vs 右侧入场 | RESOLVED_CONTEXTUAL_VARIANTS | V029 明确展示低周期 N 修复后的偏右侧进场；V032 明确展示背景较强时允许偏左侧入场并缩小仓位。两者是确认程度与风险不同的执行变体。 |
| JH-CON-005 | 趋势初期 vs 非初期退出 | POSSIBLE_CONTEXT_RESOLUTION | 来源持续表明阶段影响持有/保护利润，但“初期/末期”的统一判定仍 UNKNOWN，暂不进一步冻结。 |
| JH-CON-006 | 不同 Family 的仓位规则 | POSSIBLE_CONTEXT_RESOLUTION | 震荡 0.5×、ABC 分份/加仓、左侧缩仓、评分仓位并存，可能由统一风险理念 + Family/质量修正解释；缺完整母规则。 |
| JH-CON-007 | 评分开仓阈值 `>3` vs `>=3` | SOL_REVIEW_REQUIRED / SOURCE_INTERNAL_LANGUAGE_CONFLICT | V030 00:03:12.860 说“高于三分才开”，随后说“低于三分不交易”，又在 00:03:21.120 举“评分三分使用3000美元仓位”。来源内部无法唯一确定 3 分本身是否允许开仓。 |

当前只有 `JH-CON-005/006/007` 仍需要后续来源补证，其中 007 是明确的来源内部语言冲突，不允许工程端自行选择阈值。

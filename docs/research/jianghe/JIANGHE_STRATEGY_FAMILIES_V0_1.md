# 江河交易员策略家族规格 V0.1

本文件是来源整理规格，不是机器策略或交易授权。字段为 `UNKNOWN` 时不得以项目参数替代。

## JH-FAMILY-A：趋势关键位回调延续

| 字段 | 来源化规格 |
|---|---|
| applicable_market | 趋势，尤其是弱趋势/回调语境；精确强弱阈值 UNKNOWN |
| preconditions | 已识别趋势与关键位置；ABC 变体需 A 段后出现弱 B 回调 |
| location | 趋势关键位、回调结束附近 |
| trigger | 顺向确认 K 收盘，或突破其高/低点条件单 |
| no_trade | B 过深/连续同向回调过多、无确认、位置差、趋势末期空间不足 |
| stop_or_invalidation | 回调/入场结构极值外；宽止损可在 A 波段起始点外；精确选择 UNKNOWN |
| management / exit | 约 50% 回撤、最多两次加仓、风险约三份均只保留来源局部语境；退出看后续结构 |
| position_risk | 止损宽则降低仓位、止损窄则可增加头寸；统一算法 UNKNOWN |
| timeframes | 高周期定环境/位置，低周期定触发；具体组合 UNKNOWN |
| positive_cases / failed_cases | JH-CASE-024-001 / B 过深或连续回调的边界待核 |
| hard_negatives | 单独 N 字、单根 K、无位置的回调 |
| explicit_numeric_rules | A 段通常连续 ≥4 根同向 K，其中 ≥2 根趋势型 K（`JH-CLM-024-001`） |
| human_discretion_fields | 关键区域、回调深浅、趋势质量、空间 |
| unknown_fields | B 根数精确语义、加仓比例、统一风险比例 |
| linked_claim_ids | JH-CLM-002-002, JH-CLM-005-001, JH-CLM-024-001, JH-CLM-024-002, JH-CLM-028-001 |

## JH-FAMILY-B：趋势衰弱反转 / 高周期回调

| 字段 | 来源化规格 |
|---|---|
| applicable_market | 旧趋势末期或衰弱；精确阶段算法 UNKNOWN |
| preconditions | 无法创新极值、强反向价格行为、原防守位可能被破 |
| location | 旧趋势防守位、关键高低点 |
| trigger | 反方向确认；精确时点 UNKNOWN |
| no_trade | 逆强趋势、只有单一形态、没有失效证据 |
| stop_or_invalidation | 原交易逻辑被否认；结构另一侧止损 |
| management / exit | 到新关键区域观察市场反应；固定/动态退出的家族级关系 UNKNOWN |
| position_risk | 评分/止损距离影响仓位，但完整算法 UNKNOWN |
| timeframes | 高周期回调与低周期触发协调；数值组合 UNKNOWN |
| positive_cases / failed_cases | JH-CASE-012-001、JH-CASE-005-001 / 无独立来源化失败案例 |
| hard_negatives | 小周期反转不自动等于大周期反转 |
| explicit_numeric_rules | UNKNOWN |
| human_discretion_fields | 防守位、反向 K 强度、衰弱程度 |
| unknown_fields | 阶段、反转确认、止损精确位置 |
| linked_claim_ids | JH-CLM-005-002, JH-CLM-012-001, JH-CLM-020-002 |

## JH-FAMILY-C：多周期确认突破

| 字段 | 来源化规格 |
|---|---|
| applicable_market | 强趋势或大结构/震荡空间突破 |
| preconditions | 价格真正离开原空间，收 K/跟随，小周期趋势或 N 字二次确认 |
| location | 大结构、震荡边界、突破后回踩位置 |
| trigger | 突破后离开原空间，再看小周期确认；第二/第三进入场只保留语义 |
| no_trade | 影线刺破、未拉开距离、无跟随、小周期无二次确认 |
| stop_or_invalidation | 快速收回原空间是失败证据；精确止损 UNKNOWN |
| management / exit | 趋势有效继续持有；到关键区观察反应 |
| position_risk | UNKNOWN |
| timeframes | 大周期结构 + 小周期确认；具体组合 UNKNOWN |
| positive_cases / failed_cases | JH-CASE-023-001 / JH-CASE-027-002 是原震荡逻辑的失效/切换例 |
| hard_negatives | 突破边界却没有距离/跟随，不是真突破 |
| explicit_numeric_rules | UNKNOWN |
| human_discretion_fields | “拉开距离”、跟随质量、趋势强度 |
| unknown_fields | 距离阈值、二次确认机器定义、第三进场条件 |
| linked_claim_ids | JH-CLM-015-001, JH-CLM-023-001, JH-CLM-027-002, JH-CLM-028-001 |

## JH-FAMILY-D：震荡边界反转

| 字段 | 来源化规格 |
|---|---|
| applicable_market | 已确认震荡，包括宽幅震荡；规则/扩散/压缩的机器分类 UNKNOWN |
| preconditions | 只在上、下边界；一推/二推后出现动能不足或不能创新极值，再等反向确认 |
| location | 震荡上下边界 |
| trigger | 二推不能创新极值 + 反向确认；精确触发 UNKNOWN |
| no_trade | 震荡中间区域、没有二推/反向确认、成功突破后继续做震荡 |
| stop_or_invalidation | 结构另一侧；真突破时停止震荡逻辑并重新分类 |
| management / exit | 不预设止盈的案例存在；震荡中更主动保护利润/不贪的语境存在 |
| position_risk | 震荡仓位相对常规仓位较轻；“半仓”范围待 Sol 固定 |
| timeframes | 至少存在 15m 宽震荡案例；统一组合 UNKNOWN |
| positive_cases / failed_cases | JH-CASE-021-001 / JH-CASE-027-001 |
| hard_negatives | 震荡中间漂亮信号；突破后仍坚持区间反转 |
| explicit_numeric_rules | 震荡半仓有来源证据，但适用范围 UNKNOWN |
| human_discretion_fields | 边界、二推动能不足、真突破识别 |
| unknown_fields | 半仓范围、止盈模型、成功突破阈值 |
| linked_claim_ids | JH-CLM-020-001, JH-CLM-021-001, JH-CLM-021-002, JH-CLM-021-003, JH-CLM-027-001, JH-CLM-027-002 |

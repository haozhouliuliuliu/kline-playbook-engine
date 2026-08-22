# 江河交易员案例库增量 044–053 V0.4

案例只用于保存来源语义、执行链和边界。任何盈利、R倍数或账户结果都只是 `SOURCE_CASE_CONTENT`，不是策略有效性证据。

## JH-CASE-045-001 — 1H止跌候选 → 5m二推失败多单

| 字段 | 内容 |
|---|---|
| source | 045 / BV1SPPczVEBe / 约 00:01:04–00:04:31 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 1H此前下跌后出现强反弹；来源只先认定止跌/弱化，不直接认定完整多头反转 |
| higher_timeframe_context | 1H |
| execution_timeframe | 5m |
| location | 前低/低点测试区域 |
| setup | 强反弹降低继续单边下跌的概率；5m再次测试低点时空头两次进攻无法有效创新低 |
| trigger | 二次向下失败后出现反向阳线/确认，建立多单 |
| stop_or_invalidation | 下方结构极值之外 |
| management / exit | 先看上方区域；市场强可按高周期空间管理，弱则接受小周期利润 |
| why_valid | 高周期先出现止跌候选，低周期再提供真实二推失败/反向确认，而不是高周期到位直接做多 |
| hard_negative | 一段强反弹本身不等于完整趋势反转；若5m仍强势创新低并有跟随则不满足 |
| linked_claim_ids | JH-CLM-045-001, JH-CLM-045-002, JH-CLM-045-003, JH-CLM-045-004 |
| linked_family_id | JH-FAMILY-B / JH-FAMILY-D |
| review_status | READY |

## JH-CASE-047-001 — 震荡上沿空预案未触发 → 真突破切多 → 新确认加仓

| 字段 | 内容 |
|---|---|
| source | 047 / BV1cXc9z6Esr / 约 00:00:28–00:08:20 |
| case_type | NO_TRADE → REGIME_SWITCH → POSITIVE_EXAMPLE |
| market_context | 5m外部震荡，内部低点抬高、多方略占优 |
| higher_timeframe_context | 5m区间 |
| execution_timeframe | 1m |
| location | 5m震荡上沿；突破后回调区域 |
| initial_plan | 到上沿后切1m，等待反向推进/二推不破再做空 |
| no_trade | 1m空头条件没有出现，所以原上沿空单不执行 |
| transition | 市场反而强势向上突破并立即有跟随，原D预案失效，重新分类为真突破/多头延续 |
| trigger | 等第一段多头推动回调结束，由1m新确认做多 |
| entry_and_add | 首笔后价格回成本区不自动加；只有新的独立确认出现后才增加第二笔风险 |
| stop_or_invalidation | 各笔按对应结构失效处理 |
| management | 两笔分仓；先减一笔，剩余仓位继续观察内部N和多头动能 |
| exit | 内部N/多头动能明显转弱后退出剩余仓位 |
| why_valid | 完整体现“预案未触发就不做 + 新信息改变市场分类 + 新条件才新增风险” |
| hard_negative | 到上沿本身≠空；回成本区≠加仓；真突破后仍机械坚持震荡空属于错误语境 |
| linked_claim_ids | JH-CLM-047-001, JH-CLM-047-002, JH-CLM-047-003, JH-CLM-047-004, JH-CLM-047-005 |
| linked_family_id | JH-FAMILY-D → JH-FAMILY-C → JH-FAMILY-A |
| review_status | READY |

## JH-CASE-050-001 — 日线关键区只观察，不接飞刀

| 字段 | 内容 |
|---|---|
| source | 050 / BV1imAAzfEHM / 约 00:00:35–00:06:20 |
| case_type | NO_TRADE / CONDITIONAL_PLAN |
| market_context | 日线强上涨后连续强下跌，形成大分歧；局部多头被否定，但不足以自动定义高周期空头趋势 |
| higher_timeframe_context | 1D |
| lower_timeframe_context | 1H；必要时进一步5m |
| location | 日线强涨与强跌交汇形成的关键区域 |
| setup | 高周期到位后1H仍处强空推进 |
| no_trade | 仅因到达高周期关键区不能直接做多；1H空头未减弱时继续等待 |
| required_evidence | 至少等待1H空头弱化/二推不破，或再切5m寻找明确反向条件 |
| system_process | 来源明确“主观构建系统、客观执行”；若系统没有触发，即使行情走掉也不追 |
| linked_claim_ids | JH-CLM-050-001, JH-CLM-050-002, JH-CLM-050-003, JH-CLM-050-004 |
| linked_family_id | JH-FAMILY-B |
| hard_negative | 高周期到位≠入场；不能做多≠自动可以做空 |
| review_status | READY |

## JH-CASE-052-001 — 弱空/震荡前期共享高空许可 → 1H→5m二推失败空单

| 字段 | 内容 |
|---|---|
| source | 052 / BV128XTB8ExJ / 约 00:00:00–00:04:56 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 原强空逐渐转为弱空；也可合理解释为震荡前期 |
| higher_timeframe_context | 1H |
| execution_timeframe | 5m |
| context_evidence | 回调频率/深度增加；向下仅影线略破前低且没有良好跟随 |
| shared_plan | 两种合理分类都优先等待上方最近空头发力/关键区域找空；不到该位置则不做 |
| location | 1H最近空头发力区域/上方高价值区 |
| trigger | 到位后切5m；上涨动能减弱，第二次向上推动不能有效创新高，随后做空 |
| stop_or_invalidation | 前高上方 |
| management | 目标1看最近下方发力点；目标2看原趋势结构低点 |
| exit | 具体执行按结构/目标反应；双目标只属于本案例 |
| why_valid | 方向、动能、位置和低周期确认共同成立；不是因为“仍然下跌”就直接空 |
| hard_negative | 只知道方向不够；不到上方区域不做；若上破并形成强多头结构则原高空预案失效 |
| linked_claim_ids | JH-CLM-052-001, JH-CLM-052-002, JH-CLM-052-003, JH-CLM-052-004 |
| linked_family_id | JH-FAMILY-A / JH-FAMILY-D |
| review_status | READY |

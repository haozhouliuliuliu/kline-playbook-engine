# 江河交易员案例库增量 054–063 V0.5

本文件仅保存来源化案例。盈利、R 倍数、账户结果只属于 `SOURCE_CASE_CONTENT`，不得作为策略有效性证据。

## JH-CASE-054-001 — 1H强突破背景下的5m防守位回调多单

| 字段 | 内容 |
|---|---|
| source | 054 / BV1heXfBUEqs / 约 00:00:57–00:07:44 |
| case_type | POSITIVE_EXAMPLE |
| higher_timeframe_context | 1H上破旧空间并有强跟随，建立做多偏向；上方仍有左侧关键高点 |
| execution_timeframe | 5m |
| setup | 5m已形成弱上涨N，回到下方防守位 |
| trigger | 防守位未失守，等待向上确认K收盘；不接快速下探长针 |
| stop_or_invalidation | 5m防守位下方；防守位被有效打破则放弃 |
| management | 无固定TP；至少看上方目标/前高区域 |
| exit | 连续两次上试不能创新高 + 较大阴线 + 1H左侧关键高点压制 |
| linked_claim_ids | JH-CLM-054-001..004 |
| family | JH-FAMILY-A / JH-FAMILY-C |
| hard_negative | 回调过深；防守位失守；只有长针没有向上确认；逆做空信号 |

## JH-CASE-055-001 — 强1H下跌背景下的小周期转折空单

| 字段 | 内容 |
|---|---|
| source | 055 / BV1JX9KBSEHU / 约 00:00:51–00:05:09 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 原1H上涨被强下跌破坏，但完整1H下降高低点延续尚未完全形成 |
| setup | 强下跌动能提供空头背景；5m等待回抽/二推不破而不是追空 |
| trigger | 二推不破型空单；来源明确说模型不够标准、评分不高 |
| position_risk | 0.5×平时仓位 |
| stop_or_invalidation | 上方结构；若当前关键位失守则继续观察更上方区域，而非硬扛 |
| management | 不预设固定TP |
| exit | 动能减弱并到第一目标区附近；约1:2仅为案例 |
| linked_claim_ids | JH-CLM-055-001..005 |
| family | JH-FAMILY-B |
| hard_negative | 仅破发力点就当完整下降趋势；直接追空导致止损过宽/RR过低 |

## JH-CASE-057-001 — 1H横向底部 + 5m弱上涨防守位低多

| 字段 | 内容 |
|---|---|
| source | 057 / BV1u4D7BxEQr / 约 00:00:08–00:05:08 |
| case_type | POSITIVE_EXAMPLE |
| higher_timeframe_context | 1H横向运动底部 |
| execution_timeframe | 5m |
| setup | 5m上涨打破左侧下跌发力点并形成上涨N；上方近期高点较近，不追多 |
| location | 上涨发力/防守位；另有更低的上涨起始区域 |
| trigger | 回踩防守位后因回撤动能偏强额外等两根K；连续下探不延续后收K进多 |
| stop_or_invalidation | 防守位/下方结构 |
| management | 直接设前高实体区域目标，不追求影线极值 |
| exit | 预设目标触发；案例约1:3 |
| linked_claim_ids | JH-CLM-057-001..004 |
| family | JH-FAMILY-A / JH-FAMILY-D背景 |

## JH-CASE-058-001 — 无双周期共振的5m宽幅震荡上沿空单

| 字段 | 内容 |
|---|---|
| source | 058 / BV1sLQwBrEts / 约 00:00:20–00:04:25 |
| case_type | POSITIVE_EXAMPLE |
| timeframe | 5m独立周期；1H没有形成可用共振 |
| market_context | 既能创新高又能创新低，但两边都无跟随并快速收回 → 宽幅震荡 |
| location | 上方关键高点 |
| trigger | 饱满实体阴线吞没 |
| stop_or_invalidation | 上方结构 |
| management | 第一预期目标区；未预设统一TP |
| exit | 到第一目标区且执行者准备健身，主动离场；约1:2仅为案例 |
| linked_claim_ids | JH-CLM-058-001..004 |
| family | JH-FAMILY-D |
| note | 外部时间安排属于实际执行因素，不是市场技术规则 |

## JH-CASE-059-001 — 1H强突破后的5m二推不破多单 + 新确认加仓

| 字段 | 内容 |
|---|---|
| source | 059 / BV1hWDQBxEU9 / 约 00:00:04–00:06:13 |
| case_type | POSITIVE_EXAMPLE |
| higher_timeframe_context | 1H强突破前高并有一根阳线跟随，只找多 |
| setup | 小周期浅回调；二推不破作为回调结束证据 |
| trigger | 二推不破确认K收盘进多 |
| stop_or_invalidation | 前低下方；若回调很深且加速则交易前直接放弃 |
| reference_target | 主周期前高的实体开/收盘区域，而不是影线极值 |
| add_position | 回成本区再次出现大实体阳线、动能/节奏增强后才加仓 |
| risk_adjustment | 加仓后把两单统一设相同结构止损和前高参考目标，避免新增风险无限扩张 |
| hard_negative | 大阳线之后没有跟随且下一根马上收反向K，是明显减分信号 |
| linked_claim_ids | JH-CLM-059-001..004 |
| family | JH-FAMILY-A / JH-FAMILY-C |

## JH-CASE-060-001 — 无1H共振的5m独立周期轻仓多单

| 字段 | 内容 |
|---|---|
| source | 060 / BV1zYQ4BKEGy / 约 00:00:19–00:04:02 |
| case_type | POSITIVE_EXAMPLE |
| timeframe | 5m独立周期 |
| setup | 5m强势打破前一段下跌起始点，建立做多偏向；最早大转折错过后等待二推不破 |
| trigger | 回撤后二推不破做多 |
| position_risk | 因1H没有可参考背景/无双周期共振，整体轻仓 |
| stop_or_invalidation | 前低下方 |
| management | 不预设固定TP；观察强弱变化 |
| exit | 原强动能变成弱多、无法继续创新高；同时该单本就低质量，不强求大目标；个人健身安排是额外因素 |
| linked_claim_ids | JH-CLM-060-001..003 |
| family | JH-FAMILY-A / JH-FAMILY-B转折语境 |

## JH-CASE-061-001 — 强突破低评分多单：半仓止损后新条件半仓重进

| 字段 | 内容 |
|---|---|
| source | 061 / BV1V1dhBEELG / 约 00:00:08–00:05:16 |
| case_type | FAILED_EXAMPLE → SECOND_CHANCE |
| setup | 5m宽幅区间强突破、拉开距离、大实体跟随；两根弱阴回调 + 长影后大阳吞没 |
| penalty_factors | 1H原空头结构未完全转变；左侧近处关键位可能压制 |
| first_entry | 多单，0.5×平时仓位；后被止损 |
| new_evidence | 回到支阻互换区域；明确触碰均线；长下影 + 小趋势阳K |
| second_entry | 新条件成立后再次0.5×多单，不是摊平旧单 |
| aggregate_risk | 来源明确两次半仓合计约等于平时一笔订单的风险规模 |
| management | 因强势预期已降级，降低盈利标准并预设前高目标 |
| linked_claim_ids | JH-CLM-061-001..005 |
| family | JH-FAMILY-A / JH-FAMILY-C |
| note | 均线只在本例被明确作为辅助证据；未证明其为核心必需规则 |

## JH-CASE-062-001 — 复杂内部结构重新分类后的高位排斥空单

| 字段 | 内容 |
|---|---|
| source | 062 / BV1asowBPEUE / 约 00:00:32–00:05:40 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 大级别空头未被完全破坏，内部衍生小N先被多头破坏，随后内部多头又被破坏且均无持续延续 → 宽幅震荡/大空背景重叠 |
| setup | 前方高点处上涨先减速/回撤，不是一鼓作气上冲 |
| trigger | 空头吞没确认后做空 |
| stop_or_invalidation | 上方高点 |
| management | 下方有两个参考目标；强阴快速下跌后再等1–2根K观察是否跟随 |
| exit | 后续没有跟随、开始回撤后退出 |
| linked_claim_ids | JH-CLM-062-001..004 |
| family | JH-FAMILY-D / JH-FAMILY-B背景 |
| hard_negative | 不标准小N只能参考，不能直接下单；内部结构不能越权替代更大结构 |

## JH-CASE-063-001 — 暴跌+暴涨宽幅震荡下沿确认多单

| 字段 | 内容 |
|---|---|
| source | 063 / BV1yZoGBnErD / 约 00:00:25–00:02:45 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 三根阴线加速创新低却无跟随，随后连续大阳又创新高；两边都能创新极值 → 宽幅震荡 |
| location | 区间下沿 |
| setup | 下跌到底部先减弱；长下影形成排斥 |
| trigger | 仍不立即进，等大阳线吞没此前阴线后做多 |
| stop_or_invalidation | 下方结构 |
| management | 三个预期参考位，但没有预设固定TP |
| exit | 第三次向上尝试仍缺乏强跟随，震荡环境下谨慎退出；不足1:1仅为案例结果 |
| linked_claim_ids | JH-CLM-063-001..003 |
| family | JH-FAMILY-D |

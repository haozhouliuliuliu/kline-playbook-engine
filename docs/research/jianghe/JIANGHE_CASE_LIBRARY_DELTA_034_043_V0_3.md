# 江河交易员案例库增量 034–043 V0.3

仅保存来源语义和边界；盈利、R 倍数与账户结果只属于 `SOURCE_CASE_CONTENT`，不是策略有效性证据。

## JH-CASE-034-001 — 强突破后的弱回调延续多单

| 字段 | 内容 |
|---|---|
| source | 034 / BV1iS6KByEL1 / 约 00:00:14–00:03:54 |
| case_type | POSITIVE_EXAMPLE |
| market_context | N 结构延续后强势突破，随后反向回调明显减弱 |
| setup | 突破有跟随；回调阴线实体逐步缩小；价格没有回到旧空间；上方没有近端参考阻力 |
| trigger | 顺向恢复后多单；精确进场K在原视频订单框附近 |
| stop_or_invalidation | 下方K线极值外留少量空间 |
| management | 新推动-回撤-推动形成发力点后上移止损 |
| exit | 前高附近二推动能不足/不能有效突破后离场 |
| linked_claim_ids | JH-CLM-034-001, JH-CLM-034-002 |
| family | JH-FAMILY-A / JH-FAMILY-C |
| hard_negative | 只有突破、没有跟随；回调重新进入旧空间；前方近端强阻力 |

## JH-CASE-034-002 — 震荡下沿吞没多单

| 字段 | 内容 |
|---|---|
| source | 034 / BV1iS6KByEL1 / 约 00:04:31–00:07:19 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 原多头防守被破后没有空头延续，随后又破前高；来源重新分类为震荡 |
| location | 震荡下方关键低点 |
| trigger | 下沿出现阳线吞没后做多 |
| stop_or_invalidation | 下方结构极值 |
| management | 预设上方目标；初始仓轻，保留回成本区出现二次确认后的加仓机会 |
| exit | 触发预设目标，案例约 1:1.3 |
| linked_claim_ids | JH-CLM-034-003, JH-CLM-034-004 |
| family | JH-FAMILY-D |
| boundary | 1:1.3 是案例，不是统一震荡目标 |

## JH-CASE-036-001 — 主趋势恢复的弱回调多单

| 字段 | 内容 |
|---|---|
| source | 036 / BV11SfRBCEbm / 约 00:00:04–00:04:52 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 大一级别健康上涨；次级下跌回调弱 |
| setup | 空头回撤由实体转长下影，未回原空间；顺向阳线完全吞没 |
| trigger | 吞没确认后多单 |
| stop_or_invalidation | 下方结构 |
| management | 原本偏动态退出；未采纳过弱的早期信号，后因利润回撤改为前高预设目标 |
| exit | 前高附近触发预设止盈 |
| linked_claim_ids | JH-CLM-036-001, JH-CLM-036-002 |
| family | JH-FAMILY-A / JH-FAMILY-C |
| note | 该案例强化“主趋势/次趋势”区分与退出方法可按情境切换 |

## JH-CASE-036-002 — 窄压缩争夺后空头重新取得控制

| 字段 | 内容 |
|---|---|
| source | 036 / BV11SfRBCEbm / 约 00:05:11–00:10:31 |
| case_type | NO_TRADE → POSITIVE_EXAMPLE |
| initial_context | 强下跌到关键位；双底、阳线等局部反转形态出现但空头仍强 |
| no_trade | 窄压缩空间过小，双方仍争夺；不直接做多，也不直接做区间高空低多 |
| transition | 连贯较大实体阴线向下打破压缩区，显示空头重新掌控 |
| trigger | 弱阳反抽后带上影阴线，市价轻仓做空 |
| stop_or_invalidation | 前高上方 |
| exit | 二推不能继续创新低，动能减弱后离场 |
| linked_claim_ids | JH-CLM-036-003, JH-CLM-036-004 |
| family | JH-FAMILY-C / 趋势延续语境 |
| boundary | “空间太小”仍无统一机器阈值 |

## JH-CASE-038-001 — 动能转折左侧轻仓多单

| 字段 | 内容 |
|---|---|
| source | 038 / BV1raFxz4ECQ / 约 00:04:53–00:11:33 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 一分钟强下跌逐步转弱 |
| setup | 动能线斜率改变；第一确认线外收K |
| trigger | 左侧可先轻仓进入；更谨慎右侧版本需再等一次空头发力转弱并打破新的动能线 |
| position_risk | 左侧轻仓，后续新的右侧确认可作为加仓机会 |
| management | 本来出现加仓机会，但因在外、精神状态不专注，拒绝加仓 |
| exit | 因执行者状态/环境提前结束；技术上原计划可继续看更高区域 |
| linked_claim_ids | JH-CLM-038-002, JH-CLM-038-003 |
| family | JH-FAMILY-B（低周期反转/修复语境） |
| hard_negative | 动能线触碰本身不构成交易；未站到确认线外则继续等待 |

## JH-CASE-039-001 — 高周期高价值区到低周期行情初期空单

| 字段 | 内容 |
|---|---|
| source | 039 / BV1xGcxzPECD / 约 00:00:37–00:07:30 |
| case_type | POSITIVE_EXAMPLE |
| timeframe | 1H 定环境/区域，5m 执行；来源同时推荐 4H+15m、15m+1m |
| higher_timeframe_context | 1H 震荡上方高价值区域 |
| setup | 5m 上涨来到高价值区后无法创新高，盘整向下突破 |
| trigger | 第一次反抽失败、第二次细小反抽再失败后，阴线收K做空 |
| stop_or_invalidation | 前方高点上方 |
| management | 不预设静态TP；先观察下方关键发力点，若不破则退出，若破则认定新下跌更成立并移动止损继续追踪 |
| exit | 下一高价值区域出现二推不破后离场 |
| linked_claim_ids | JH-CLM-039-001, JH-CLM-039-002, JH-CLM-039-003 |
| family | JH-FAMILY-B |
| hard_negative | 大周期到位但小周期没有真实衰弱/突破/反抽失败，不能直接空 |

## JH-CASE-040-001 — 15m→1m 剥头皮演示

| 字段 | 内容 |
|---|---|
| source | 040 / BV1MSZTBLEVq / 约 00:07:17–00:11:35 |
| case_type | OTHER |
| provenance | JIANGHE_DEMONSTRATION / NON_CORE_MODE |
| higher_timeframe_context | 15m 下方高价值区域 |
| execution_timeframe | 1m |
| setup | 1m 空头结构仍在，但动能线斜率转缓；变形二推新低缺乏跟随并快速收回 |
| trigger | 再画更细动能线，价格打破原斜率并收K后进多 |
| stop_or_invalidation | 下方结构 |
| management | 上行后移动止损 |
| exit | 上行二推无法创新高时离场 |
| linked_claim_ids | JH-CLM-040-003, JH-CLM-040-004 |
| family | NONE — 暂列 `SCALPING_EXECUTION_MODE`，不创建 Family E |
| reason | V043 明确说江河平常不太做、也不特别擅长剥头皮 |

## JH-CASE-042-001 — 弱空/震荡重叠区域的动态空单

| 字段 | 内容 |
|---|---|
| source | 042 / BV1ZQfqBEE1j / 约 00:03:45–00:07:41 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 可合理解释为弱空，也可解释为震荡；两者都在上方找空 |
| location | 上一段上涨结束与下一段下跌起始的交界/防守区域 |
| trigger | 到位后出现明确排斥再做空 |
| stop_or_invalidation | 上方结构止损 |
| management | 第一预期位没有排斥，反而向下爆发，因此不退出；两根微弱阳线不足以否认下跌 |
| exit | 更晚出现新的弱整理/反应后结束 |
| linked_claim_ids | JH-CLM-042-001, JH-CLM-042-002, JH-CLM-042-003 |
| family | JH-FAMILY-D / JH-FAMILY-A 的重叠语境 |
| note | 案例同时把“应变”落到实际持仓管理上 |

## JH-CASE-043-001 — 5m关键区→1m剥头皮空

| 字段 | 内容 |
|---|---|
| source | 043 / BV1WyftBAEgr / 约 00:01:21–00:03:19 |
| case_type | POSITIVE_EXAMPLE |
| provenance | NON_CORE_SCALPING_DEMO |
| setup | 5m 高价值交易区；1m 强上涨后动能减弱、二推不创新高、动能线被破 |
| trigger | 窄整理向下突破后做空 |
| stop_or_invalidation | 上方结构 |
| management / exit | 到第一预期位快速离场 |
| linked_claim_ids | JH-CLM-043-002 |
| family | NONE — `SCALPING_EXECUTION_MODE` |

## JH-CASE-043-002 — 剥头皮第一单止损后独立重进

| 字段 | 内容 |
|---|---|
| source | 043 / BV1WyftBAEgr / 约 00:04:16–00:09:18 |
| case_type | FAILED_EXAMPLE → SECOND_CHANCE |
| setup | 下方区域、动能减弱、无法继续创新低 |
| first_entry | 多单；整理向下破后触发结构止损 |
| new_evidence | 下破只是长影线测试/清扫，没有形成真正突破，窄幅震荡仍成立 |
| second_entry | 重新按区间底部做多；这是新条件，不是为了摊平旧亏损 |
| exit | 第二单到区间上方目标盈利离场 |
| linked_claim_ids | JH-CLM-043-003 |
| family | JH-FAMILY-D / `SCALPING_EXECUTION_MODE` |
| hard_negative | 若出现真正向下突破，则不能再次沿用底部做多逻辑 |

## JH-CASE-043-003 — 15m关键位下的1m剥头皮空与条件加仓

| 字段 | 内容 |
|---|---|
| source | 043 / BV1WyftBAEgr / 约 00:09:32–00:11:58 |
| case_type | POSITIVE_EXAMPLE |
| higher_timeframe_context | 15m 关键区域 |
| execution_timeframe | 1m |
| setup | 强上涨后深回调，二次推动不能强势创新高 |
| trigger | 横向减弱后向下爆发，做空 |
| add_condition | 若价格回成本区，仍不能创新高，并出现明确排斥 + 新进场信号，才允许加仓 |
| risk_management | 原仓可打平离场，新增仓单独博弈下方波动 |
| linked_claim_ids | JH-CLM-043-004 |
| family | NONE — `SCALPING_EXECUTION_MODE` |
| boundary | 回成本区本身绝不是加仓理由 |

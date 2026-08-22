# 江河交易员策略家族规格 V0.8（001–093）

本文件是来源化研究规格，不是机器策略或交易授权。核心 Family 仍只有 A–D。`UNKNOWN` 不得自行补参数。

## JH-FAMILY-A：趋势关键位回调延续

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 已确认趋势/突破后的延续环境；弱趋势常适合等回调，强趋势已形成后也可等非常浅的回调/小转折继续参与 |
| preconditions | 方向偏向明确；前一推动有质量；反向回调相对弱，不能快速深度否定原推动；V086/V093继续强化“强推动→弱回调→顺向恢复” |
| location | 趋势防守/发力位、突破后回踩区、第二推动前的浅回调区 |
| trigger | 顺向确认K、吞没、二推失败后恢复；V086典型为弱阴回调无跟随后被阳线实体吞没；V093第一份看1m强阳收K、第二份等5m收K |
| no_trade | 回调过深/反向加速、无确认、位置差、空间不足；第一反向K不等于回调已经结束 |
| stop_or_invalidation | 回调/入场结构极值外；防守失守；原趋势被反向持续跟随否认 |
| management | 新结构形成可推进止损；非趋势初期降低预期；不能继续创新极值可退出 |
| position_risk | 以损定仓母公式适用；评分/共振/左侧/独立周期可修正仓位；统一账户比例UNKNOWN |
| timeframes | 高周期定环境/方向，低周期优化触发；5m→1m反复出现 |
| explicit_numeric_rules | 既有ABC数字保持；本批无新增Family A统一数字 |
| human_discretion_fields | 回调深浅、强弱强质量、关键位、剩余空间、趋势阶段 |
| unknown_fields | 强弱阈值、趋势阶段机器算法、统一风险比例 |

## JH-FAMILY-B：趋势衰弱反转 / 高周期回调

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 原趋势末期/衰弱，或高周期关键区中的低周期反向机会 |
| preconditions | 原方向先减弱/失去创新能力；新方向仍需真实跟随/爆发，不能只凭原方向变弱 |
| location | 高周期关键/参考位、原趋势防守区、震荡边界附近的高价值位置 |
| trigger | 无法创新极值、盘整破位、反抽失败、强反向K；V090内部空头N仅先削弱1H上涨，不直接等于完整反转 |
| no_trade | 趋势仍完整时为了唯一顶/底机会逆势；只看到第一反向K；新方向无跟随 |
| stop_or_invalidation | 新方向无法延续或原方向恢复；结构另一侧止损 |
| management | 根据订单模式决定尺度；若反转单迟迟不推进，可主动结束 |
| position_risk | 左侧/低质量可缩仓；统一比例UNKNOWN |
| timeframes | 高周期给位置/环境，低周期给真实强弱和执行 |
| explicit_numeric_rules | 无新增统一数字 |
| human_discretion_fields | 转弱质量、第二次博弈、主动退出时点 |
| unknown_fields | 反转阶段算法、爆发阈值、统一仓位规则 |

## JH-FAMILY-C：多周期确认突破

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 强趋势或结构/震荡空间的真实突破，尤其失衡启动阶段 |
| preconditions | 价格真正离开旧空间；实体突破和同向跟随；回调不能快速否定突破 |
| location | 外部边界、发力/防守点、突破后回踩区 |
| trigger | 强突破+跟随+低周期确认；V086新增“碾压式突破”高质量概念 |
| no_trade | 影线刺破、无跟随、快速收回、消耗过大后质量不足；仅有形态名不交易 |
| stop_or_invalidation | 重新进入旧空间、突破结构失效、结构另一侧 |
| management | 突破完成并形成强趋势后，可转入Family A式浅回调续势；不是新Family |
| position_risk | 以损定仓；可分阶段进入；统一质量折扣UNKNOWN |
| timeframes | 外部周期定突破，小周期确认；同周期内部结构不能冒充小周期外部结构 |
| explicit_numeric_rules | 无统一突破距离/跟随阈值 |
| human_discretion_fields | 碾压式/消耗式、跟随质量、回调强弱 |
| unknown_fields | 突破距离/速度/跟随阈值、碾压式机器定义 |

## JH-FAMILY-D：震荡边界反转

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 已确认震荡/宽幅震荡；双向都可走出显著运动但都缺乏持续延续 |
| preconditions | 只在外部上下高价值边界；允许高周期弱趋势与低周期震荡共享同一方向许可 |
| location | 外部最高/最低区；V084以最近上下发力点定边界；V093称其可视为盈亏切换交界 |
| trigger | 边界二推/多推失败、吞没、强弱转换；V084下沿空头减弱+多头增强；V093上沿先反向强K后仍等第二次确认 |
| no_trade | 中间区域、只到边界无确认、第一反向K不足、真突破后仍坚持反转 |
| stop_or_invalidation | 外部边界真实突破并持续跟随；结构另一侧止损 |
| management | 相对主动；新结构可推进止损；若迟迟不向预期方向推进可主动退出 |
| position_risk | 既有0.5×震荡版本保留；以损定仓母公式可约束总风险；统一规则UNKNOWN |
| timeframes | 外部周期定区间，小周期只细化触发；V090有1H弱多+5m震荡共享低多许可 |
| explicit_numeric_rules | V021 `0.5×REGULAR_POSITION_SIZE`仍仅保留其来源语境 |
| human_discretion_fields | 外部边界、二推质量、主动退出时点、盈亏交界区 |
| unknown_fields | 宽幅边界算法、统一退出公式、位置画法 |

## Family间切换

- D外部区间真突破后可切C。
- C完成强突破并进入稳定强趋势后，如果市场不再给深回踩，可切入A的“浅回调/小转折续势”执行。
- 高周期弱趋势与低周期震荡若给出相同方向许可，可保留重叠分类，不必强行先选唯一标签。
- B只在原趋势衰弱/否认并有反向接管证据时生效，不能把强趋势中的普通浅回调误认为反转。

## NON-FAMILY：SCALPING_EXECUTION_MODE

仍为 `NON_CORE_EXECUTION_MODE`。V084/V086/部分V093存在短单或超短线案例，但不改变V074所确认的本人日常主战场仍偏日内波段/微波段。

## AUXILIARY_TOOL_USAGE

均线及其他指标继续为辅助证据，核心决策仍以价格/K线、结构、位置、动能和市场状态为主。

# 江河交易员策略家族规格 V0.2（001–033）

本文件是来源化研究规格，不是机器策略或交易授权。`UNKNOWN` 不得用项目参数补齐。四个家族仍为 A–D；029–033 没有足够证据创建新家族。

## JH-FAMILY-A：趋势关键位回调延续

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 已识别趋势，尤其弱趋势/回调型节奏；强弱阈值仍 UNKNOWN |
| preconditions | 趋势方向明确；存在关键/防守区域；回调不得快速否定原推进 |
| location | 趋势关键位、波段/内部 N 防守、回调结束附近 |
| trigger | 顺向确认 K 收盘或突破其高/低点条件单；V029 有内部空头 N 被修复为多头 N 后右侧做多实例 |
| no_trade | 无确认、位置差、趋势末期空间不足；ABC 中 B 连续 ≥3 根同方向回调 K 时放弃；B 在 ≤3 根内快速回到/破坏 A 起始区域时放弃 |
| stop_or_invalidation | 回调/入场结构极值外；ABC 宽止损可在 A 起始点外；形成新内部防守后可推进止损 |
| management / exit | 趋势仍有效则跟踪；节奏明显转弱或出现反向结构可保护利润；V029 展示内部 N 防守逐步移动止损 |
| position_risk | 止损宽则减仓，止损窄可提高头寸；ABC 可初始仓 + 最多 2 次加仓，总风险约分三份的来源语境；统一账户比例 UNKNOWN |
| timeframes | 高周期环境/位置 + 低周期内部结构/触发；V029 是“看大做小”明确实例 |
| explicit_numeric_rules | ABC A：连续 ≥4 根同方向 K，至少 2 根趋势型 K；双向适用，来源称适用于足够流动市场和不同周期。ABC B 的两条明确放弃条件见上 |
| human_discretion_fields | 关键区边界、回调质量、内部 N/防守选择、趋势强弱和剩余空间 |
| unknown_fields | 超大 K 变形精确阈值、统一风险比例、加仓精确比例 |

## JH-FAMILY-B：趋势衰弱反转 / 高周期回调

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 原趋势末期/衰弱，或高周期主趋势中的反向回调；阶段算法 UNKNOWN |
| preconditions | 原方向无法继续创新极值、动能/节奏转弱；必要时结合原防守位是否被破 |
| location | 原趋势防守、显著高低点、高周期关键区域 |
| trigger | 强反向行为 + 原方向结构被否认；精确统一时点仍 UNKNOWN |
| no_trade | 逆强趋势直接赌反转；只有局部 lower-high/lower-low 但主要高周期防守未破；只有单一形态 |
| stop_or_invalidation | 原反转/回调假设被新一轮原趋势延续否认；结构另一侧止损 |
| management / exit | 反向高周期回调属于较小目标/不贪的来源语境；到关键区看反应 |
| position_risk | V029 对高周期逆主趋势的回调交易强调小 RR/不贪；完整家族仓位算法 UNKNOWN |
| timeframes | 必须区分主高周期趋势与低周期反向结构；低周期转向不能自动称高周期反转 |
| explicit_numeric_rules | UNKNOWN |
| human_discretion_fields | 主要防守位、趋势是否真的衰弱、反向行为强度 |
| unknown_fields | 反转阶段算法、统一止损与仓位模型 |

## JH-FAMILY-C：多周期确认突破

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 强趋势或大结构/震荡空间的真实突破 |
| preconditions | 价格离开原空间、同方向推进/跟随，低周期结构能够确认突破而非只刺破 |
| location | 大结构边界、震荡边界、突破后回踩区域 |
| trigger | 离开原空间 + 同向跟随 + 小周期趋势/N 结构确认；V029 有“强推进突破 + 好跟随 + 与原空间拉开距离”的成功突破实例 |
| no_trade | 仅影线刺破、未拉开距离、无跟随、快速收回原空间、低周期无法确认 |
| stop_or_invalidation | 快速重新进入原空间是重要失败线索；精确统一止损 UNKNOWN |
| management / exit | 趋势有效继续持有；形成新内部 N/防守后推进止损；节奏明显变化时可保护利润 |
| position_risk | 初次/后续进入可分阶段，但统一仓位算法 UNKNOWN |
| timeframes | 大周期负责边界/方向，小周期负责确认与执行 |
| explicit_numeric_rules | 当前无统一突破距离/跟随数值阈值 |
| human_discretion_fields | “拉开足够距离”、跟随质量、内部 N 质量、趋势强度 |
| unknown_fields | 距离阈值、跟随阈值、二次/第三进入场的完整机器定义 |

## JH-FAMILY-D：震荡边界反转

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 已确认震荡/宽幅震荡；其他震荡细分类机器边界 UNKNOWN |
| preconditions | 只在上下边界寻找机会；到边界后仍要等待推动衰弱/无法创新极值和反向确认 |
| location | 震荡上沿/下沿；中间区域明确不做 |
| trigger | 二推/多推不能创新极值、动能不足 + 反向确认 K；V032 有上沿多次上推失败后空头收 K 做空实例 |
| no_trade | 区间中间、仅到边界无确认、成功真突破后仍坚持震荡反转 |
| stop_or_invalidation | 结构另一侧；真突破后停止震荡逻辑并重新分类到突破/趋势 |
| management / exit | 震荡订单更可采用固定区间目标或主动保护；也存在不预设 TP 案例。V032 第一单按震荡目标先落袋，真突破后再切换 C，而非把原单强行延长 |
| position_risk | V021 经 Sol 复核：该系统版本明确为常规仓位的 0.5×；V032 左侧更激进入场也明确缩小仓位 |
| timeframes | 至少存在 15m 宽震荡以及更低周期内部结构执行 |
| explicit_numeric_rules | `RANGE_POSITION_SIZE = 0.5 × REGULAR_POSITION_SIZE`（V021 source-version）；不等于账户绝对风险比例 |
| human_discretion_fields | 区间边界、二推动能强弱、真突破判定、左侧背景是否足够强 |
| unknown_fields | 常规仓位绝对定义、统一止盈模型、真突破精确阈值 |

## Family 间切换

来源显示 Family 并非互斥静态标签，而是随市场重新分类切换：

- D（震荡边界）若出现成功真突破 → 停止震荡逻辑，可切换 C。
- A/C 的强趋势若节奏明显弱化且主要防守未破 → 先重新评估为弱化/震荡候选，不应直接跳到 B 的高周期反转。
- V032 明确演示：先按震荡逻辑完成一段利润；之后确认真突破，再用突破逻辑处理后续行情。

这些切换语义仍依赖市场分类，不代表已经拥有完全可执行的自动状态机。

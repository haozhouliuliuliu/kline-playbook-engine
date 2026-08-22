# 江河交易员策略家族规格 V0.3（001–043）

本文件是来源化研究规格，不是机器策略或交易授权。核心 Family 仍只有 A–D。V040/V043 的剥头皮单独登记为非核心执行模式，不创建 Family E。

## JH-FAMILY-A：趋势关键位回调延续

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 已识别趋势，尤其回调型/较弱趋势节奏；强弱机器阈值 UNKNOWN |
| preconditions | 趋势方向明确；有关键/防守区域；原推进较强，反向回调相对弱且不能快速否定原推进 |
| location | 趋势关键位、波段/内部 N 防守、回调结束区域 |
| trigger | 顺向确认 K；V034/V036 加强“突破有跟随 + 回调实体缩小/不回旧空间 + 顺向恢复”链 |
| no_trade | 无确认、位置差、末期空间不足；ABC 两条 B 放弃规则；强反向回调重新进入旧空间时降低/否定质量 |
| stop_or_invalidation | 回调/入场结构极值外；ABC 可选 A 起始点外宽止损；新 N/发力结构形成后可推进止损 |
| management / exit | 趋势有效则跟踪；新防守形成移动止损；二推不能继续创新极值或节奏明显反转时退出 |
| position_risk | 止损宽减仓，止损窄可提高头寸；ABC 初始仓+最多两次加仓；统一账户风险 UNKNOWN |
| timeframes | 高周期环境/位置 + 低周期内部结构/触发；V039 推荐 4H+15m、1H+5m、15m+1m |
| explicit_numeric_rules | 既有 ABC A/B 数字边界；没有新增统一回调百分比 |
| human_discretion_fields | 关键/参考位、弱回调质量、内部 N、防守点、趋势强弱、剩余空间 |
| unknown_fields | 超大 K 变形、统一风险比例、加仓比例、强弱趋势阈值 |

## JH-FAMILY-B：趋势衰弱反转 / 高周期回调

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 原趋势末期/衰弱，或高周期主趋势中的反向回调 |
| preconditions | 到高价值区后原方向不能继续创新极值/动能衰弱；低周期必须出现真实转变证据 |
| location | 原趋势防守、显著高低点、高周期交易/参考关键区域 |
| trigger | V039：5m 上涨到 1H 高价值上区 → 不创新高/盘整下破 → 两次多头反抽失败 → 阴线收 K 做空 |
| no_trade | 逆强趋势赌反转；只到高周期关键区；只见双底/阳线；主要防守未破、原方向仍强 |
| stop_or_invalidation | 反转假设被原方向新延续否认；结构另一侧止损 |
| management / exit | 到下一关键/发力位看是否有效突破；不破可退出，破位形成新趋势可推进止损继续持有 |
| position_risk | 逆主趋势回调语境偏小目标/不贪；完整家族仓位算法 UNKNOWN |
| timeframes | 高周期给区域，低周期负责真实反应；V039推荐组合可作为来源配置 |
| explicit_numeric_rules | 无统一反转数字阈值 |
| human_discretion_fields | 高价值区、防守位、衰弱程度、反抽失败质量、二推质量 |
| unknown_fields | 反转阶段算法、统一动能阈值、统一仓位模型 |

## JH-FAMILY-C：多周期确认突破

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 强趋势或大结构/震荡空间的真实突破 |
| preconditions | 离开原空间、同方向推进/跟随；反向回调弱且最好不重新进入旧空间 |
| location | 大结构/震荡边界、突破后回踩区域、前方参考位空间 |
| trigger | 强突破 + 跟随 + 离开旧空间；再由低周期 N/确认 K 执行。V034/V036 强化弱回调后顺向恢复 |
| no_trade | 影线刺破、无跟随、未拉开距离、快速收回旧空间、前方近端阻力过近、小周期确认不足 |
| stop_or_invalidation | 重新进入旧空间/原突破结构失效；结构另一侧止损 |
| management / exit | 新 N/发力结构形成后推进止损；继续突破且目标位无排斥则持有；二推失败/动能弱化可退出 |
| position_risk | 可分阶段进入；统一仓位算法 UNKNOWN |
| timeframes | 高周期边界/方向 + 低周期确认；V039推荐 4H+15m、1H+5m、15m+1m |
| explicit_numeric_rules | 仍无统一突破距离、跟随强度数值 |
| human_discretion_fields | 拉开距离、跟随质量、内部 N、近端参考阻力、趋势强度 |
| unknown_fields | 距离阈值、跟随阈值、完整二次/第三进场规则 |

## JH-FAMILY-D：震荡边界反转

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 已确认震荡/宽幅震荡；V034 补充“既能创出新低又能创出新高”可作震荡语义 |
| preconditions | 只在上下边界；到位后仍等待推动衰弱/不能创新极值/吞没等反向确认 |
| location | 震荡上沿/下沿；中间不做 |
| trigger | 二推/多推不能创新极值 + 反向确认 K，或边界明确吞没；V034 有下沿阳线吞没实例 |
| no_trade | 区间中间、只到边界无确认、成功真突破后仍坚持区间反转 |
| stop_or_invalidation | 结构另一侧；真突破后停止 D 并重新分类 |
| management / exit | 可用区间目标或主动保护；也存在不预设 TP；V034 1:1.3 仅为单案例 |
| position_risk | V021 0.5×常规仓位仍为明确 source-version；V034 再出现很轻初始仓，为二次确认加仓留空间 |
| timeframes | 当前/高周期定区间，低周期可做边界触发 |
| explicit_numeric_rules | `0.5 × REGULAR_POSITION_SIZE`；1:1.3 不升级为规则 |
| human_discretion_fields | 区间分类、边界、二推动能、吞没质量、真突破 |
| unknown_fields | 常规仓位绝对风险、统一止盈、区间分类机器阈值 |

## Family 间切换

- D 真突破后可切换 C。
- A/C 强趋势节奏弱化但主要防守未破时，先考虑弱化/震荡候选，不自动跳到 B。
- B 的高周期关键区必须由低周期真实结构确认，不能“到位即反转”。
- V042 允许多个合理标签；当不同分类共享同一许可时，可先使用共同条件，再随新信息重新分类。

## NON-FAMILY：SCALPING_EXECUTION_MODE

V040/V043 证明江河会教学和演示剥头皮，但 V043 明确自述平常不太做且不特别擅长，因此当前：

```text
STATUS=NON_CORE_EXECUTION_MODE
FAMILY_E=NO
```

来源化特征：快进快出、初始仓轻、低 RR；只在高价值位置参与；常见 15m/5m 定位置 → 1m 执行；动能线斜率变化/不能创新极值可作线索；回成本区只有出现新的独立进场信号才允许加仓，不能盲目摊平；V040 的示例金额不是永久资金规则。

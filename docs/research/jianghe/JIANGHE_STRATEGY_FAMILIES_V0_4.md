# 江河交易员策略家族规格 V0.4（001–053）

本文件是来源化研究规格，不是机器策略或交易授权。核心 Family 仍只有 A–D；V040/V043 的剥头皮继续作为 `SCALPING_EXECUTION_MODE / NON_CORE`，不创建 Family E。

## JH-FAMILY-A：趋势关键位回调延续

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 已识别趋势，尤其回调型/弱趋势节奏；强弱机器阈值仍 UNKNOWN |
| preconditions | 趋势方向明确；有关键/防守/发力区域；原推进有质量；回调相对弱且不能快速否定原推进 |
| location | 趋势关键位、内部N防守、最近发力位置、回调结束区 |
| trigger | 顺向确认K、二推失败后的顺趋势恢复、或低周期结构确认；V047真突破后等待第一推动回调结束再做多；V052弱空/震荡前期在上方发力区等待5m二推失败做空 |
| no_trade | 无确认、位置差、末期空间不足；ABC两条B放弃规则；只知道趋势方向但动能/位置不满足；突破后直接追而无预案 |
| stop_or_invalidation | 回调/入场结构极值外；ABC宽止损可在A起始点外；新结构形成后可推进止损 |
| management / exit | 趋势有效则跟踪；可以分批退出；新内部N/动能明显变弱可结束剩余仓位 |
| position_risk | 止损宽减仓；ABC初始仓+最多2次加仓；V047只有成本区出现新确认才增加第二笔 |
| timeframes | 高周期环境/位置 + 低周期执行；新增V052 `1H→5m`、V047 `5m→1m` |
| explicit_numeric_rules | 既有ABC A/B数字边界；没有新增统一回调百分比 |
| human_discretion_fields | 强弱趋势、发力/防守位、二推质量、剩余空间、订单模式 |
| unknown_fields | 统一风险、强弱阈值、回调质量、加仓比例 |

## JH-FAMILY-B：趋势衰弱反转 / 高周期回调

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 原趋势末期/衰弱，或高周期主趋势中的反向回调/止跌候选 |
| preconditions | 原方向不再顺畅创新极值、动能减弱；高周期关键区只提供候选，不等于反转 |
| location | 原趋势防守、显著高低点、高周期关键区、前低/前高测试区域 |
| trigger | V045：1H只先确认止跌，5m再次测试前低时空头两次进攻失败并收阳后做多；V050：日线关键区后至少等1H空头减弱/二推不破，再考虑本级别或更小周期做多 |
| no_trade | 逆强趋势接飞刀；强反向K就直接宣布趋势翻转；高周期到位无低周期反应；只有W/N形态 |
| stop_or_invalidation | 反转假设被原方向新延续否认；结构另一侧止损 |
| management / exit | 可按高周期预期延展，也可在低周期不够强时只取小周期利润；必须匹配进场模式 |
| position_risk | 左侧/早期确认通常更轻；统一比例UNKNOWN |
| timeframes | 典型 `1H→5m`、`1D→1H→5m`；高周期给环境/区域，低周期证明弱化与反向触发 |
| explicit_numeric_rules | 无统一反转数字阈值 |
| human_discretion_fields | “止跌”与完整反转边界、二推失败质量、关键区、强弱 |
| unknown_fields | 反转阶段算法、统一动能阈值、左/右侧风险比例 |

## JH-FAMILY-C：多周期确认突破

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 强趋势或大结构/震荡空间的真实突破 |
| preconditions | 价格离开原空间、有同向推进和跟随；反向回调不能迅速否定突破 |
| location | 大结构/震荡边界、突破后回踩区域、前方参考空间 |
| trigger | 强突破 + 跟随 + 离开旧空间 → 低周期等待回调结束/二推失败后顺突破；V047是完整实时实例 |
| no_trade | 影线刺破、无跟随、未离开旧空间、快速收回；原D反转条件没出现时不提前赌；直接上破后若不属于预案也可不追 |
| stop_or_invalidation | 重新进入旧空间/突破结构失效；结构另一侧止损 |
| management / exit | 新结构形成推进止损；可分批退出；内部N/动能明显转弱时保护剩余利润 |
| position_risk | 可以分仓/分阶段进入；第二笔必须由新的独立确认触发 |
| timeframes | 大周期边界/方向 + 低周期确认；V047 `5m→1m` |
| explicit_numeric_rules | 仍无统一突破距离、跟随强度阈值 |
| human_discretion_fields | 拉开距离、跟随质量、低周期二推、内部N、前方空间 |
| unknown_fields | 距离阈值、跟随阈值、完整多次进场机器规则 |

## JH-FAMILY-D：震荡边界反转

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 已确认震荡/宽幅震荡，或V052所示的弱趋势/震荡前期重叠状态 |
| preconditions | 只在上下边界/高价值区域；到位后仍等待推动衰弱、不能创新极值、吞没或反向确认 |
| location | 震荡上沿/下沿；弱空/震荡前期可共享上方发力区高空许可；中间不做 |
| trigger | 二推/多推不能创新极值 + 反向确认K；V047原计划为上沿1m二推失败空；V052为上方关键区5m上涨衰弱+二推失败空 |
| no_trade | 中间区域、只到边界无确认、真突破后仍坚持震荡反转；原预案未触发则放弃 |
| stop_or_invalidation | 结构另一侧；真突破后停止D并重新分类 |
| management / exit | 可用区间/结构目标或动态保护；V052示例有最近发力点和原结构低点两层目标，仅属案例 |
| position_risk | V021 0.5×常规仓位仍为明确source-version；状态不专注时来源会进一步避免大仓位 |
| timeframes | 当前/高周期定区间或边界，低周期做二推/反向确认；V047 `5m→1m`、V052 `1H→5m` |
| explicit_numeric_rules | `0.5 × REGULAR_POSITION_SIZE`仍保留；V052双目标不是统一数字规则 |
| human_discretion_fields | 区间分类、边界、二推质量、弱趋势/震荡重叠、真突破 |
| unknown_fields | 常规仓位绝对风险、区间机器阈值、统一退出 |

## Family 间切换

- `D → C`：震荡边界反转预案未触发，而市场出现真实强突破+跟随时，停止D，切C；V047是完整实时案例。
- `C → A`：突破确认后，后续第一推动回调结束可转为趋势延续型进入。
- `A/C → 弱化/震荡候选`：强趋势节奏减弱但主要防守未破，不直接跳到B；先重新分类。
- `B`：高周期关键区必须由低周期真实衰弱/反向证据确认，不能“到位即反转”。
- `A/D重叠`：V052表明弱空与震荡前期可能共享“上方关键区高空”许可；分类差异主要影响反向处理和目标预期。
- `LONG_INVALID != SHORT_VALID`：V050明确多空许可必须独立满足，不能将某Family的失败自动反向映射成另一个Family的入场。

## 跨 Family 执行约束

V050新增一个当前对所有Family都重要的来源约束：

```text
ENTRY_MODE
→ RISK_HORIZON
→ PROFIT_HORIZON
→ EXIT_STYLE
```

剥头皮信号、日内/波段信号不能在进场后因情绪任意互换。精确的模式分类仍 `UNKNOWN`。

## NON-FAMILY：SCALPING_EXECUTION_MODE

状态不变：

```text
STATUS=NON_CORE_EXECUTION_MODE
FAMILY_E=NO
```

来源化特征：高价值位置 + 1m级别动能/结构确认、轻仓、较短利润尺度、快进快出。V050进一步说明：如果以剥头皮信号进场，就应按剥头皮的成本/利润尺度管理，不能临时期待波段利润。

# 江河交易员策略家族规格 V0.6（001–073）

本文件是来源化研究规格，不是机器策略或交易授权。核心 Family 仍只有 A–D。`UNKNOWN` 不得自行补参数。

## JH-FAMILY-A：趋势关键位回调延续

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 已识别趋势/突破后的延续环境；弱趋势更适合回调，强推动后也可等第一段浅弱回调 |
| preconditions | 外部方向/偏向明确；原推动有足够质量；回调相对浅弱，不能快速否定原推动 |
| location | 趋势防守/发力位、内部N回调区、突破后回踩区 |
| trigger | 顺向确认K、吞没、二推失败后恢复；V067新增反向实体缩小+影线增加→顺向实体增强的视觉链 |
| no_trade | 回调过深/加速反向、无确认、位置差、空间不足；弱多背景禁止追多 |
| stop_or_invalidation | 回调/入场结构极值外；防守失守；原推动被反向持续跟随否认 |
| management | 新结构形成可推进止损；前方关键位二推失败/动能减弱可退出 |
| position_risk | 止损宽减仓；评分、共振、左侧/独立周期可修正仓位；统一账户风险UNKNOWN |
| timeframes | 高周期/外部结构定环境，低周期执行；V069明确同周期内部结构不能直接当下一周期外部结构 |
| explicit_numeric_rules | 既有ABC数字边界保持；本批无新增统一数字 |
| human_discretion_fields | 内外结构划分、回调深浅、二推质量、关键位、剩余空间 |
| unknown_fields | 内外结构机器算法、强弱趋势阈值、统一风险比例 |

## JH-FAMILY-B：趋势衰弱反转 / 高周期回调

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 原趋势末期/衰弱，或高周期关键区中的低周期反向机会 |
| preconditions | 原方向减弱且处于高价值位置；新方向还需出现真实跟随/爆发，不能只凭旧方向变弱 |
| location | 高周期关键/参考位、原趋势防守区、震荡上/下半部高价值位置 |
| trigger | 无法创新极值、盘整破位、反抽失败、强反向K；V068新增“旧方向减弱→新方向爆发/加速”质量要求 |
| no_trade | 只看到原方向减弱但新方向无跟随；位置已接近另一边界时不追 |
| stop_or_invalidation | 新方向无法延续或原方向重新恢复；结构另一侧止损 |
| management | 短线/剥头皮可无爆发先退出，后续新爆发作为新机会；订单尺度需与进场前定义一致 |
| position_risk | 左侧/低质量/独立周期可缩仓；统一比例UNKNOWN |
| timeframes | 高周期给位置，低周期给真实强弱；V068为5m→1m实例 |
| explicit_numeric_rules | 无新增统一数字 |
| human_discretion_fields | “爆发/加速”强度、转弱质量、边界距离 |
| unknown_fields | 爆发阈值、反转阶段算法、统一仓位规则 |

## JH-FAMILY-C：多周期确认突破

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 强趋势或结构/震荡空间的真实突破；外部宽幅震荡内部也可出现局部压缩突破机会 |
| preconditions | 离开旧空间、同向推进/跟随；回调相对弱；不能把本周期内部结构直接当交易许可 |
| location | 外部边界、内部压缩区、突破后回踩区、前方参考位 |
| trigger | 强突破+跟随+低周期确认；V067内部压缩突破后，以反向动能减弱+顺向实体增强收K执行 |
| no_trade | 影线刺破、无跟随、快速收回、反向回调过强；内部结构本身不给交易许可 |
| stop_or_invalidation | 重新进入旧空间、原突破结构失效、结构另一侧 |
| management | 新N/发力结构推进止损；前方关键位动能减弱/二推失败可退出 |
| position_risk | 可分阶段进入；无共振/低质量可轻仓；统一算法UNKNOWN |
| timeframes | 每个周期必须识别自己的外部结构；不能把5m内部结构冒充1m外部结构 |
| explicit_numeric_rules | 无统一突破距离、跟随强度数字 |
| human_discretion_fields | 内部压缩质量、跟随、外部/内部边界、回调强弱 |
| unknown_fields | 突破距离阈值、跟随阈值、内部/外部结构机器定义 |

## JH-FAMILY-D：震荡边界反转

| 字段 | 当前来源化规格 |
|---|---|
| applicable_market | 已确认震荡/宽幅震荡；双向可创新极值但均无持续跟随是稳定来源语义 |
| preconditions | 波段只在外部上下边界；允许外部震荡同时存在内部弱多/弱空偏向 |
| location | 外部最高点/最低点区域；波段中间不做主周期D订单 |
| trigger | 边界二推/多推失败、反抽不能创新极值、吞没、强弱转换；V066上沿打破→反抽失败空；V073下沿测试不破→减弱/加速多 |
| no_trade | 中间区域、只到边界无确认、真突破后仍坚持反转；弱多内部偏向下不做空、不追多 |
| stop_or_invalidation | 外部边界真实突破并持续跟随；结构另一侧止损 |
| management | 更主动，不要求拿满区间；目标只是参考，斜率/动能衰弱可提前离场 |
| position_risk | 既有0.5×常规仓位来源版本保持；统一账户风险UNKNOWN |
| timeframes | 外部主周期定区间；中间若要交易可切小周期重新识别其外部结构做非核心短线 |
| explicit_numeric_rules | V021 `0.5×REGULAR_POSITION_SIZE`仍保留；本批1:2多仅为案例 |
| human_discretion_fields | 外部边界、内部偏向、二推失败、斜率、宽幅区间质量 |
| unknown_fields | 宽幅边界机器算法、内部偏向阈值、统一退出公式 |

## Family 间切换与结构层级

- D外部区间真突破后可切换C。
- 外部震荡内部弱多/弱空，只改变方向过滤与边界优先级，不自动把外部分类改成趋势。
- V069明确：`SAME_TF_INTERNAL_STRUCTURE != LOWER_TF_EXTERNAL_STRUCTURE`。要使用更小周期交易，必须切到该周期重新识别其外部结构。
- V067表明外部边界附近可恢复主周期Family逻辑；外部中间区域若参与，更多采用更小周期、非核心的剥头皮执行模式。

## NON-FAMILY：SCALPING_EXECUTION_MODE

仍为 `NON_CORE_EXECUTION_MODE`，不创建 Family E。

V073进一步明确其边界：

```text
进场前定义为剥头皮
→ 按剥头皮的停滞/目标尺度退出
→ 事后价格继续走远不能反推“卖飞”
```

相反，若进场前定义为微波段，则应按微波段预期管理。订单类型不能因事后结果切换。

## AUXILIARY_TOOL_USAGE：均线

V061已出现均线辅助重进场；V069再次明确可以加一根均线辅助观察震荡：价格/K线反复上下缠绕且无法持续站在均线上或下方，是震荡特征之一。

当前结论仍是：

```text
MA_STATUS=AUXILIARY_TOOL_USAGE
CORE_REQUIRED=NO
FAMILY_E=NO
```

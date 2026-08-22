# 江河交易员案例库增量 064–073 V0.6

只保存来源语义与边界。盈利、RR、账户结果只属于 `SOURCE_CASE_CONTENT`，不是策略有效性证据。

## JH-CASE-066-001 — 宽幅震荡上沿二推失败空单

| 字段 | 内容 |
|---|---|
| source | 066 / BV1Vp9SBFEx2 / 约 00:00:33–00:02:27 |
| case_type | POSITIVE_EXAMPLE |
| market_context | 上方创新高、随后下方创新低，但两个方向均无结构性延续/跟随，按宽幅震荡处理 |
| location | 外部上方最高点区域 |
| setup | 上沿第一次向下打破后反抽无法创新高，形成来源称“二推不破” |
| trigger | 反抽失败后做空 |
| stop_or_invalidation | 上方高点外 |
| management | 第一目标中间次低点，第二目标外部最低点；途中观察实际反应，不要求拿满区间 |
| exit | 下跌斜率由陡转缓且仍处宽幅震荡背景，第二目标前主动离场 |
| linked_claim_ids | JH-CLM-066-001, JH-CLM-066-002, JH-CLM-066-003 |
| family | JH-FAMILY-D |
| hard_negative | 只到上沿无向下确认；二推继续创新高；真趋势形成持续跟随 |
| boundary | 案例约1:2多，不升级为统一RR规则 |

## JH-CASE-067-001 — 外部宽幅震荡中的内部压缩突破多

| 字段 | 内容 |
|---|---|
| source | 067 / BV1x1RNBbERa / 约 00:00:20–00:04:37 |
| case_type | POSITIVE_EXAMPLE / MODE_SWITCH |
| market_context | 原上涨末端N被破后向下无延续，随后向上也无延续；外部按宽幅震荡处理 |
| internal_context | 外部区间中存在内部压缩小区间，随后向上突破 |
| trigger | 突破后回调中空方实体缩小、影线增加；顺向阳线实体增强，收K做多 |
| stop_or_invalidation | 下方结构 |
| management | 前方高点作为关键反应区；二推不破/动能减弱时敏感退出 |
| exit | 前高附近出现弱二推失败后离场 |
| mode_switch | 之后5m中间区域节奏转差，不再做5m波段单；中间改用1m剥头皮，到外部上下边界再切回5m主周期逻辑 |
| linked_claim_ids | JH-CLM-067-001, JH-CLM-067-002, JH-CLM-067-003, JH-CLM-067-004 |
| family | JH-FAMILY-C / JH-FAMILY-D；1m部分为NON_CORE_SCALPING_EXECUTION_MODE |
| hard_negative | 内部突破无跟随；顺向恢复确认不存在；把外部中间区域当5m高价值交易区 |

## JH-CASE-068-001 — 5m关键点下的1m转弱空头爆发

| 字段 | 内容 |
|---|---|
| source | 068 / BV12QRaBuEC8 / 约 00:00:30–00:02:45 |
| case_type | POSITIVE_EXAMPLE / EARLY_EXIT_AND_RETRY |
| higher_timeframe_context | 5m前高关键节点 |
| execution_timeframe | 1m |
| setup | 关键点附近多头减弱，价格位于上半部高位 |
| first_attempt | 空头虽增强但没有来源期望的“爆发/加速”，因此来源倾向先退出 |
| second_condition | 后续出现明显空头加速/爆发，可再次参与 |
| no_trade | 接近下方底部后不再继续追同类空头行为 |
| linked_claim_ids | JH-CLM-068-001, JH-CLM-068-002 |
| family | JH-FAMILY-B / NON_CORE_SCALPING_EXECUTION_MODE |
| ambiguity | “爆发/加速”没有固定量化阈值 |

## JH-CASE-073-001 — 1m宽幅震荡下沿剥头皮多与模式一致性退出

| 字段 | 内容 |
|---|---|
| source | 073 / BV1WoLA6dEC4 / 约 00:02:29–00:06:16 |
| case_type | POSITIVE_EXAMPLE / EXECUTION_DISCIPLINE |
| market_context | 创新高无延续后回落；随后既不能创新高也不能创新低，按震荡处理 |
| location | 震荡下方区域 |
| setup | 再次测试下沿但没有真实突破，随后向上收回；出现来源描述的“减弱→加速” |
| trigger | 下沿确认后做多 |
| order_mode | 1m剥头皮 |
| management | 按剥头皮尺度观察价格停滞并退出；不能因为事后继续上涨而改写原订单类型 |
| counterfactual | 如果进场前定义为微波段，则应按更远预期位管理；中途按剥头皮尺度走反而才是执行变形 |
| linked_claim_ids | JH-CLM-073-001, JH-CLM-073-002 |
| family | JH-FAMILY-D / NON_CORE_SCALPING_EXECUTION_MODE |
| hard_negative | 事后看到继续上涨就把剥头皮单改成波段单；根据结果反复重写退出规则 |

## Video 065 处理边界

`065 / BV1GSozBrE9e / 短线交易实录` 当前本地 MP4 可正常查看，但没有 SRT，抽样画面也没有稳定可读取的烧录语义字幕。视频主要展示多屏行情/订单变化。当前不从纯视觉订单结果反推江河的进场原因、止损逻辑或管理规则，因此：

```text
SEMANTIC_STATUS=NEEDS_LOCAL_ASR_OR_DIRECT_AUDIO_REVIEW
CLAIM_COUNT=0
CASE_COUNT=0
```

这不是来源缺失，也不是故障；只是当前语义证据不足。
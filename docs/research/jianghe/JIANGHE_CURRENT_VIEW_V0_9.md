# 江河交易员当前研究视图 V0.9

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..099
ANALYZED_AVAILABLE=95
PENDING_SEMANTIC_REVIEW=065,099
PARTIAL_NO_NATIVE_SRT_REVIEW=048
BLOCKED_LOCAL_MEDIA=007
BLOCKED_PAID_GATE=022
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
EVIDENCE_STAGE=PRELIMINARY_SOURCE_INTERPRETATION_EVIDENCE
```

## 当前权威组合

V0.9 不删除旧证据。读取优先级：

1. `JIANGHE_TRADER_DOSSIER_V0_9.md`：001–099 当前累计14项视图，其中099尚未完成Sol语义复核。
2. `JIANGHE_CLAIM_LEDGER_DELTA_094_098_V0_9.jsonl`：本批094–098新增claim。
3. `JIANGHE_CASE_LIBRARY_DELTA_094_098_V0_9.md`：本批新增case。
4. `JIANGHE_CORPUS_GAP_AUDIT_PLAN_V0_9.md`：007/022/048/065/099及全量字幕/媒体重新机械审计计划。
5. V0.8及更早全部claim/case/family/system/unknown/contradiction/review artifacts继续有效。

## V0.9关键变化

- V094把“上头/情绪失控”的处理明确转向**事前制度约束**，而不是依赖临场自控：设置当日最大可动用交易资金上限、明确交易规则、逻辑评分，只在规则条件满足后执行。
- V095继续强化高周期宽幅震荡/高抛低吸与多周期共振：4H由强转弱、无法创新高后更偏宽幅震荡；临近下方关键区域不盲目追空，应等待更低周期真实信号；案例继续使用1H/5m/1m层级。
- V096把交易者资格进一步拆到**市场事实、账户资金变化、心理/行为反应**的分离：不能让账户盈亏直接驱动平仓、报复性交易或频繁下单。
- V097给出“交换公式”来源哲学：先问愿意付出/损失什么，再问想得到什么；交易是用可接受、可控制的已知成本去交换不确定的可能性。
- V098继续以实盘案例强化：关键区域到达后等待企稳/第二次发力或低周期确认，再执行；多周期位置与小周期细化进场继续作为同一链条，而不是位置到达即交易。
- V099按Owner说明无SRT，但本轮Sol会话未收到099 MP4，因此不得补猜；进入本地语料审计与ASR/直接音频复核流程。

## 当前核心Family

仍只有：
- `JH-FAMILY-A` 趋势关键位回调延续
- `JH-FAMILY-B` 趋势衰弱反转 / 高周期回调
- `JH-FAMILY-C` 多周期确认突破
- `JH-FAMILY-D` 震荡边界反转

V094/V096/V097主要补风险、执行纪律与交易者状态，不创建新Family。V095/V098主要补既有Family和多周期执行证据，不创建Family E。

## 当前必须补齐的语料缺口

- 007：本地媒体曾标记损坏，需要重新验证源视频是否仍可下载、是否只是本地文件损坏。
- 022：付费/充电门控，当前保持`UNAVAILABLE_PAID_GATED`，不得购买来绕过研究边界。
- 048：此前无SRT，仅依据原视频可直接读取的烧录文字建立有限语义，完整音频尚未系统转写。
- 065：无SRT，完整语义待本地免费ASR或直接音频复核。
- 099：Owner明确无SRT；本轮未收到MP4，需在本地语料中确认媒体完整性并生成可供Sol复核的转写/证据包。
- 全量字幕数量曾出现90与89的不一致，必须按BVID重新机械审计，而不能依赖目录文件数。

## 解释边界

- `SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION`。
- SRT只用于导航；图表相关claim必须回到原视频语言+同时间画面。
- 没有来源固定的数字继续保持`UNKNOWN`。
- 盈利、RR、账户结果仅为`SOURCE_CASE_CONTENT`，不是validity evidence。
- 当前`SOURCE_ONLY_VERIFIED=NO`，不授权outcome testing、validation/final访问或真钱动作。

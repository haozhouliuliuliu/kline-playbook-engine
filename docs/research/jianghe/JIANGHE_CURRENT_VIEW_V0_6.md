# 江河交易员当前研究视图 V0.6

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..073
ANALYZED_AVAILABLE=70
PENDING_SEMANTIC_REVIEW=065
BLOCKED_LOCAL_MEDIA=007
BLOCKED_PAID_GATE=022
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
EVIDENCE_STAGE=PRELIMINARY_SOURCE_INTERPRETATION_EVIDENCE
```

## 当前权威组合

V0.6 不删除旧证据。按以下优先级读取：

1. `JIANGHE_TRADER_DOSSIER_V0_6.md`：001–073累计14项视图。
2. `JIANGHE_STRATEGY_FAMILIES_V0_6.md`：Family A–D、结构层级与非核心执行模式。
3. `JIANGHE_SYSTEM_PROCESS_V0_6.md`：构建/执行/复盘、内外结构、周期/样本与订单模式。
4. 历史claim ledger（V0.1–V0.5）。
5. `JIANGHE_CLAIM_LEDGER_DELTA_064_073_V0_6.jsonl`：本批新增claim。
6. 历史case library + `JIANGHE_CASE_LIBRARY_DELTA_064_073_V0_6.md`。
7. 历史source index + `JIANGHE_SOURCE_INDEX_DELTA_064_073_V0_6.csv`。
8. `JIANGHE_UNKNOWN_REGISTER_V0_6.md`、`JIANGHE_CONTRADICTION_REGISTER_V0_6.md`、`JIANGHE_EVIDENCE_REVIEW_QUEUE_V0_6.csv`。

## V0.6 关键变化

- V066/V067/V069继续稳定宽幅震荡：双向可创新极值，但两个方向都缺乏持续跟随。
- V069首次非常明确地区分本周期内部/外部结构：内部结构只用于确认外部结构，不直接提供本周期波段交易机会，也不能冒充下一小周期外部结构。
- V069确认外部震荡可同时存在内部弱多/弱空偏向；弱多语境下不做空、不追多，只等下半部低多条件。
- V067补强弱回调视觉链：反向实体缩小、影线增加，再由顺向实体增强确认。
- V068补强“旧方向减弱≠新方向已经触发”：新方向最好还要爆发/加速；无跟随可先退出。
- V070进一步钉死系统架构：主观设计/复盘在盘前盘后，盘中只识别既有条件并执行，不能临场给想做的订单找理由。
- V072把周期问题拆为两层：不同周期是同一价格过程的不同聚合；周期仍会改变样本量、交易成本、时间/机会成本与执行状态。
- V073再次确认订单模式必须在进场前定义；剥头皮单不能因为事后行情继续上涨就改成波段单。
- V065无SRT且抽样无稳定烧录语义字幕：当前保持 `PENDING_SEMANTIC_REVIEW`，不从纯视觉订单结果反推策略。

## 当前核心 Family

仍只有：

- `JH-FAMILY-A` 趋势关键位回调延续
- `JH-FAMILY-B` 趋势衰弱反转 / 高周期回调
- `JH-FAMILY-C` 多周期确认突破
- `JH-FAMILY-D` 震荡边界反转

`SCALPING_EXECUTION_MODE`仍是非核心模式；均线仍只登记为`AUXILIARY_TOOL_USAGE`。

## 解释边界

- `SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION`。
- SRT只用于导航；图表相关claim已回原视频同时间画面核对。
- V065当前没有语言锚点，不产出语义claim/case。
- 没有来源固定的数字、距离、斜率、爆发强度或结构算法继续保持`UNKNOWN`。
- 视频中的盈利、RR、账户结果只属于`SOURCE_CASE_CONTENT`，不是validity evidence。
- 当前`SOURCE_ONLY_VERIFIED=NO`，不授权outcome testing、validation/final访问或真钱动作。

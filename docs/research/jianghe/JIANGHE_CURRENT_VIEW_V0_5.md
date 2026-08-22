# 江河交易员当前研究视图 V0.5

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..063
ANALYZED_AVAILABLE=61
BLOCKED_LOCAL_MEDIA=007
BLOCKED_PAID_GATE=022
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
EVIDENCE_STAGE=PRELIMINARY_SOURCE_INTERPRETATION_EVIDENCE
```

## 当前权威组合

V0.5 不删除旧证据。按以下优先级读取：

1. `JIANGHE_TRADER_DOSSIER_V0_5.md`：001–063累计14项视图。
2. `JIANGHE_STRATEGY_FAMILIES_V0_5.md`：当前Family A–D、Family切换及辅助工具边界。
3. `JIANGHE_SYSTEM_PROCESS_V0_5.md`：系统构建、偏向过滤、共振质量、风险拆分与复盘过程。
4. `JIANGHE_SOL_REVIEW_RESOLUTION_V0_2.md`：V0.1七项Sol复核结论。
5. 历史claim：V0.1基础 + V0.2补充/029–033 + V0.3 034–043 + V0.4 044–053。
6. `JIANGHE_CLAIM_LEDGER_DELTA_054_063_V0_5.jsonl`：本批39条新增claim。
7. 历史case library + `JIANGHE_CASE_LIBRARY_DELTA_054_063_V0_5.md`：本批9个新增案例。
8. 历史source index + `JIANGHE_SOURCE_INDEX_DELTA_054_063_V0_5.csv`。
9. `JIANGHE_UNKNOWN_REGISTER_V0_5.md`、`JIANGHE_CONTRADICTION_REGISTER_V0_5.md`、`JIANGHE_EVIDENCE_REVIEW_QUEUE_V0_5.csv`。

## V0.5关键变化

- V054明确“交易偏向是过滤器，不是自动触发器”：多头偏向下，多信号仍需完整条件，空信号直接过滤。
- V054/V059进一步强化强推动/突破后的浅弱回调延续链，回调过深/加速可直接否定交易许可。
- V055再次区分“打破发力点”与“完整下降趋势高低点延续”；极强反向动能可作为切小周期抓转折的背景，但阈值仍UNKNOWN。
- V058/V060明确：没有双周期共振时仍可做单周期交易；V060把这类订单降级为较低质量、轻仓。多周期共振因此是质量修正而非普遍硬门槛。
- V057/V059重复确认：主周期前高/前低参考位通常偏向K线实体开收盘区域，而非追求影线极值；适用范围仍需继续补证据。
- V055/V061都出现低评分/减分项使用0.5×常规仓位。V061进一步明确两个0.5×独立尝试的合计风险约等于平时一笔订单。
- V059继续钉死“回成本区≠加仓”；必须出现新的增强型独立进场理由。
- V061原视频明确出现均线作为重进场辅助证据。当前登记为 `AUXILIARY_TOOL_USAGE`，不创建指标Family，也不证明均线是核心必需规则。
- V058/V063继续稳定宽幅震荡定义：双向均能创新极值，但两边都缺乏持续跟随/快速收回；边界仍需反向确认。
- V062强化复杂结构层级：不标准衍生小N只能参考；内部多空互破且无延续时可重新分类为宽幅震荡，并与更大空头背景共享高位空许可。

## 当前核心Family

仍只有：

- `JH-FAMILY-A` 趋势关键位回调延续
- `JH-FAMILY-B` 趋势衰弱反转 / 高周期回调
- `JH-FAMILY-C` 多周期确认突破
- `JH-FAMILY-D` 震荡边界反转

`SCALPING_EXECUTION_MODE`仍为非核心模式；V061均线仅为辅助工具使用，不创建Family E。

## 解释边界

- `SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION`。
- SRT只用于导航；图表相关claim已回原视频核对同时间语言和画面。
- 没有来源固定的数字、评分、距离、斜率、回调深浅阈值继续保持`UNKNOWN`。
- 视频中的盈利、RR、账户结果只属于`SOURCE_CASE_CONTENT`，不是validity evidence。
- 当前`SOURCE_ONLY_VERIFIED=NO`，所以证据仍为preliminary，不授权outcome testing、validation/final访问或真钱动作。

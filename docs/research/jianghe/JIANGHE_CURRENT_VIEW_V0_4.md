# 江河交易员当前研究视图 V0.4

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..053
ANALYZED_AVAILABLE=51
BLOCKED_LOCAL_MEDIA=007
BLOCKED_PAID_GATE=022
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
EVIDENCE_STAGE=PRELIMINARY_SOURCE_INTERPRETATION_EVIDENCE
```

## 当前权威组合

V0.4 不删除旧证据。按以下优先级读取：

1. `JIANGHE_TRADER_DOSSIER_V0_4.md`：001–053 累计14项视图。
2. `JIANGHE_STRATEGY_FAMILIES_V0_4.md`：当前Family A–D + 非核心剥头皮执行模式。
3. `JIANGHE_SYSTEM_PROCESS_V0_4.md`：系统构建、盘中执行、风险评价、学习与复盘过程。
4. `JIANGHE_SOL_REVIEW_RESOLUTION_V0_2.md`：V0.1七项Sol复核结论。
5. `JIANGHE_CLAIM_LEDGER_V0_1.jsonl` + `JIANGHE_CLAIM_LEDGER_SUPPLEMENT_RESOLVED_V0_2.jsonl`：001–028基础/补充。
6. `JIANGHE_CLAIM_LEDGER_DELTA_029_033_V0_2.jsonl`。
7. `JIANGHE_CLAIM_LEDGER_DELTA_034_039_V0_3.jsonl` + `JIANGHE_CLAIM_LEDGER_DELTA_040_043_V0_3.jsonl`。
8. `JIANGHE_CLAIM_LEDGER_DELTA_044_053_V0_4.jsonl`：044–053新增38条claim。
9. V0.1 case library + 029–033 delta + 034–043 delta + `JIANGHE_CASE_LIBRARY_DELTA_044_053_V0_4.md`。
10. `JIANGHE_UNKNOWN_REGISTER_V0_4.md`、`JIANGHE_CONTRADICTION_REGISTER_V0_4.md`、`JIANGHE_EVIDENCE_REVIEW_QUEUE_V0_4.csv`。
11. V0.1 source index + 029–033 delta + 034–043 delta + `JIANGHE_SOURCE_INDEX_DELTA_044_053_V0_4.csv`。

## V0.4关键变化

- V045/V050：强反向运动可以先形成止跌/弱化/大分歧，但不自动等于完整高周期趋势反转。
- V045：新增 `1H→5m` 止跌候选 + 低点二推失败多单案例。
- V046：明确胜率、频率、盈亏比的系统设计取舍；这是来源观点，不升级成项目统计学定理。
- V047：完整演示 `D震荡反转预案未触发 → 真突破切C → 回调确认按A顺多 → 成本区只有新确认才加仓 → 分批+动态退出`。
- V048：无SRT。只采用原视频开头可直接读取的烧录文字：环境导致不专注时避免开大仓位；不对音频或后续旅行画面补猜交易语义。
- V049：图形/画线是信息压缩而非市场因果；止损/亏损是中性风险成本；系统需兼顾市场规律、交易规则和个人诉求。
- V050：把“应变”钉实为预先构建条件/行动预案、盘中客观识别触发并调用；新增 `LONG_INVALID != SHORT_VALID` 和订单模式/利润尺度一致性。
- V051：新增战略复盘与战术复盘双层闭环；战术动作可结构化为 `CONTINUE / IMPROVE / STOP / START`。
- V052：弱空/震荡前期可以共享上方关键区高空许可；新增 `1H→5m` 二推失败空单案例。
- V053：技术流派不按名称排高低；以个人适配和底层机制为主，学习路径为模仿→适配/融合→形成自己的体系。
- 核心Family仍只有A–D；没有新增Family E。
- V030评分3分边界仍是唯一Sol review queue项。

## 解释边界

- `SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION`。
- SRT只用于导航；图表相关claim必须回到原视频同时间语言和画面。
- V048没有SRT，因此只使用可直接看见的烧录文字，不根据未转写音频猜测。
- 未被来源固定的数字、画区、动能强弱、风险比例和评分边界保持 `UNKNOWN`。
- 视频中的盈利、R倍数、账户曲线和战绩只属于 `SOURCE_CASE_CONTENT`，不是validity evidence。
- 当前 `SOURCE_ONLY_VERIFIED=NO`，因此仍不允许升级为PRIMARY-ready，也不授权outcome testing、validation/final access、真钱或实盘动作。

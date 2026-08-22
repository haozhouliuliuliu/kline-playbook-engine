# 江河交易员当前研究视图 V0.7

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..083
ANALYZED_AVAILABLE=80
PENDING_SEMANTIC_REVIEW=065
BLOCKED_LOCAL_MEDIA=007
BLOCKED_PAID_GATE=022
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
EVIDENCE_STAGE=PRELIMINARY_SOURCE_INTERPRETATION_EVIDENCE
```

## 当前权威组合

V0.7不删除旧证据。按以下优先级读取：

1. `JIANGHE_TRADER_DOSSIER_V0_7.md`：001–083累计14项视图。
2. `JIANGHE_STRATEGY_FAMILIES_V0_7.md`：当前Family A–D、Family切换、剥头皮/指标边界。
3. `JIANGHE_SYSTEM_PROCESS_V0_7.md`：系统构建、市场节奏、K线强弱、风险、订单模式、学习/复盘过程。
4. `JIANGHE_SOL_REVIEW_RESOLUTION_V0_2.md`：V0.1七项Sol复核结论。
5. 历史claim：V0.1基础 + V0.2补充/029–033 + V0.3 034–043 + V0.4 044–053 + V0.5 054–063 + V0.6 064–073。
6. `JIANGHE_CLAIM_LEDGER_DELTA_074_083_V0_7.jsonl`：本批40条新增claim。
7. 历史case library + `JIANGHE_CASE_LIBRARY_DELTA_074_083_V0_7.md`：本批8个新增案例。
8. 历史source index + `JIANGHE_SOURCE_INDEX_DELTA_074_083_V0_7.csv`。
9. `JIANGHE_UNKNOWN_REGISTER_V0_7.md`、`JIANGHE_CONTRADICTION_REGISTER_V0_7.md`、`JIANGHE_EVIDENCE_REVIEW_QUEUE_V0_7.csv`。

## V0.7关键变化

- V074再次明确本人核心日常交易仍为日内波段/微波段；剥头皮大量出现在直播/视频中含内容展示效率因素，仍不升级为核心Family。
- V075把“市场节奏→交易手法”钉得更实：强势/低回调环境更适合突破，弱趋势/深回调环境更适合回调；只做熟悉节奏与为多种节奏准备方案不存在天然高低。
- V076/V078进一步确认：形态/画线只是市场信息压缩，不能把形态名当交易许可。
- V078是高密度基础课程：正式补充趋势型/非趋势型K的50%来源定义、K线相对强弱、时间周期聚合、平衡/失衡、历史+当下、强弱转换信号、对抗态NO_TRADE、发力点语义；并明确均线/指标可作为辅助但不是核心决策依据。
- V079正式给出以损定仓公式 `仓位=可承受亏损/(止损点数×每点价值)`；2%/1%均为教学示例，不升级统一账户风险。V079同时产生“进场K收盘价止损”与图示/案例不一致的新review项。
- V080进一步钉死订单模式一致性：是否卖飞应按进场前计划评价；来源建议大量历史回测建立系统信心，但这只是source process观点，不构成项目outcome-test授权。
- V081明确 `ENTRY_SPLIT != ADDITIONAL_RISK_ADD`：计划10手拆成5+5只是分批进入，不等于新增风险式加仓。
- V082给出学习层级和完整交易执行链：趋势→位置→信号→结构止损→按止损空间算仓→目标→RR。
- V083继续把无止损/重仓梭哈偶然暴赚登记为hard negative；“70%技术/30%人”仅保留为修辞性来源比例，不机器化。

## 当前核心Family

仍只有：

- `JH-FAMILY-A` 趋势关键位回调延续
- `JH-FAMILY-B` 趋势衰弱反转 / 高周期回调
- `JH-FAMILY-C` 多周期确认突破
- `JH-FAMILY-D` 震荡边界反转

`SCALPING_EXECUTION_MODE`仍为非核心模式；均线/其他指标为`AUXILIARY_TOOL_USAGE`，不创建Family E。

## 当前开放复核项

- V030评分开仓边界 `>3` vs `>=3`。
- V065无SRT，等待本地免费ASR或直接音频语义复核。
- V069“同周期内部结构只确认外部结构”的术语范围，与早期内部N/内部结构用法需要统一。
- V079“进场K收盘价止损”文本与图示/后续案例冲突。
- V078趋势型/非趋势型K在恰好50/50时定义边界重叠。

## 解释边界

- `SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION`。
- SRT只用于导航；图表相关claim需回原视频核对同时间语言和画面。
- 没有来源固定的数字、评分、距离、斜率、回调深浅阈值继续保持`UNKNOWN`。
- 视频中的盈利、RR、账户结果只属于`SOURCE_CASE_CONTENT`，不是validity evidence。
- 当前`SOURCE_ONLY_VERIFIED=NO`，所以证据仍为preliminary，不授权outcome testing、validation/final访问或真钱动作。

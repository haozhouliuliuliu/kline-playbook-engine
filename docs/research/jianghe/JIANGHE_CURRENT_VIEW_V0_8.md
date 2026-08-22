# 江河交易员当前研究视图 V0.8

```text
TRADER_ID=JIANGHE_TRADER
SOURCE_SCOPE=001..093
ANALYZED_AVAILABLE=90
PENDING_SEMANTIC_REVIEW=065
BLOCKED_LOCAL_MEDIA=007
BLOCKED_PAID_GATE=022
SOURCE_ONLY_VERIFIED=NO
PRIMARY_ELIGIBLE=NO
EVIDENCE_STAGE=PRELIMINARY_SOURCE_INTERPRETATION_EVIDENCE
```

## 当前权威组合

V0.8不删除旧证据。按以下优先级读取：

1. `JIANGHE_TRADER_DOSSIER_V0_8.md`：001–093累计14项视图。
2. `JIANGHE_STRATEGY_FAMILIES_V0_8.md`：当前Family A–D、Family阶段切换及非核心执行模式边界。
3. `JIANGHE_SYSTEM_PROCESS_V0_8.md`：系统构建、概率/风险、市场节奏、执行与复盘过程。
4. `JIANGHE_SOL_REVIEW_RESOLUTION_V0_2.md`：V0.1七项Sol复核结论。
5. 历史claim：V0.1基础 + V0.2补充/029–033 + V0.3 034–043 + V0.4 044–053 + V0.5 054–063 + V0.6 064–073 + V0.7 074–083。
6. `JIANGHE_CLAIM_LEDGER_DELTA_084_093_V0_8.jsonl`：本批42条新增claim。
7. 历史case library + `JIANGHE_CASE_LIBRARY_DELTA_084_093_V0_8.md`：本批10个新增case。
8. 历史source index + `JIANGHE_SOURCE_INDEX_DELTA_084_093_V0_8.csv`。
9. `JIANGHE_UNKNOWN_REGISTER_V0_8.md`、`JIANGHE_CONTRADICTION_REGISTER_V0_8.md`、`JIANGHE_EVIDENCE_REVIEW_QUEUE_V0_8.csv`。

## V0.8关键变化

- V084/V089/V092继续强化 `OUTCOME != EXECUTION_QUALITY`：盈利也可能是差执行，亏损可以是模式内正常成本；复盘应区分正常成本与违规“罚款”。
- V085再次钉死 `LONG_INVALID != SHORT_VALID`，并明确学习技术的目标是减少系统外交易，而非提高交易覆盖率。
- V086新增“碾压式突破 vs 消耗式突破”，并明确提高RR可以从压缩进场成本入手；极短时间的大R被来源描述为小概率市场配合，不应常态化。
- V088再次确认位置/偏向是过滤器，不是自动触发器；新结构形成后可动态推进止损保护利润。
- V090提供1H弱多与5m震荡下沿共享低多许可的重叠分类实例；影线假破无实体/跟随不视为真突破；个人状态可影响持仓管理。
- V091补充来源市场观：市场是多主体合力，重点是用市场反应验证当下共识，而不是用自己的判断定义市场。该观点只作source market model。
- V093新增强势阶段切换：强势失衡/突破启动更偏Family C；突破完成、趋势建立且只给浅回调时，可由Family A浅回调续势接管，不创建Family E。
- V093新增“真空区域”来源概念：左侧缺少明显关键位/共识位时阻力可能更小；机器定义保持UNKNOWN。
- 本批新增42条详细claim与10个正式case。

## 当前核心Family

仍只有：

- `JH-FAMILY-A` 趋势关键位回调延续
- `JH-FAMILY-B` 趋势衰弱反转 / 高周期回调
- `JH-FAMILY-C` 多周期确认突破
- `JH-FAMILY-D` 震荡边界反转

`SCALPING_EXECUTION_MODE`仍为非核心模式；均线/其他指标继续为`AUXILIARY_TOOL_USAGE`，不创建Family E。

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

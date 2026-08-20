# RASCHKE_NR7_PLAYBOOK_CONTRACT_DRAFT_V0_1

> 状态：有效草案 / NOT_MACHINE_READY
>
> 构建器：`tools/build_raschke_nr7_playbook_contract_draft.py`
>
> 机器可读证据：`docs/evidence/RASCHKE_NR7_PLAYBOOK_CONTRACT_DRAFT_V0_1.json`
>
> 来源证据：`docs/evidence/HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_NR7_SEMANTIC_V0_1.json`

## 分层边界

```text
SOURCE CLAIM
!=
PROJECT / AI INTERPRETATION
!=
MACHINE OPERATIONALIZATION
```

V0.1 把已接受的 SOURCE_ONLY 证据中的全部 23 条来源声明（`C-RAS-NR7-SEM-001..023`）机械翻译进 Playbook Contract 草案。来源声明、项目解释、机器实现三层严格分离；`UNKNOWN` 保持 `UNKNOWN`。

下列内容只在来源实际固定的范围内保留为来源事实：

- NR7 日为过去七根柱中最窄范围的柱（日线柱；七柱回看长度固定，包含/排他对齐未定）；
- NR7 日后一天以早盘区间（第一 45 分钟 / 第一小时两个来源允许变体）挂止损单包围；
- 买入止损单在早盘区间高点上方、卖出止损单在早盘区间低点下方（偏移量未定）；
- 价格化的趋势日定义（一端开盘、对端收盘、区间扩张、稳定抬高的高点/低点）；
- 定性的确认组件（15 分钟大柱、成交量、龙头股、趋势性时段）与定性的离场/管理意图（持有至收盘 / 加仓 / 部分隔夜）；
- 明确的 no-trade / 失败上下文（猜突破约 90% 错误；区间中段不买；波动率极值处旗形失效；Eaton 无交易示例）。

V0.1 没有把旧项目解释提升为来源事实，没有为 NR7 引入任何 Holy Grail 止损语义（摆动低点、ATR、跟踪止损等一律未导入），没有建立机器实现层，也没有选定任何 PRIMARY（唯一主解释）。

## 明确未解决项

- `INITIAL_STOP`：来源未固定初始保护止损（`NOT_PINNED`）；
- `POST_ENTRY_INVALIDATION`：来源未建立成交后失效边界（集成修正 IC-1：对侧 bracket 仅是入场放置，不是来源止损/失效）；
- `EARLY_MORNING_RANGE_PRIMARY_45MIN_VS_60MIN`：45 分钟与 60 分钟均为来源允许变体，无唯一来源依据 PRIMARY；
- `ENTRY_OFFSET_OR_TICK_CONVENTION`：相对早盘区间高/低的偏移量未定；
- `UNTRIGGERED_OPPOSITE_ORDER_CANCELLATION`：一侧成交后对侧未触发单的处置未定（OCO 为项目约定）；
- `SIMULTANEOUS_OR_SAME_BAR_TRIGGER_HANDLING`：同柱双触发的处置未定；
- `CONFIRMATION_THRESHOLDS`：15 分钟“大柱”、成交量“显著增加”阈值未定；
- `EXIT_OR_TARGET_CONVENTION` / `END_OF_SESSION_HANDLING`：目标价、收盘处理为定性管理原则，非确定性规则；
- `NO_TRADE_GATE`：无确定性 no-trade 门槛；
- `SINGLE_OPERATING_TIMEFRAME`：多时间框架来源未固定单一操作时间框架；
- `CHINESE_FUTURES_DAILY_BAR_BOUNDARY`：中国期货日线柱边界 / 会话边界构建为受治理元数据项目约定。

## 不可观测输入

NYSE TICK、涨跌广度（advancing minus declining）、TIKI 与美股龙头确认属于来源确认性“障碍”输入，当前中国期货 1 分钟 OHLCV 语料不拥有，记录为 `NOT_OBSERVABLE_WITH_CURRENT_DATA`，不做任何 K 线代理。来源明确其为确认性障碍而非 NR7 bracket 入场触发器。

## 确定性验证结果

当前验证器必须返回以下阻塞族：

- `UNRESOLVED_CRITICAL_AMBIGUITY`；
- `REQUIRED_INPUT_NOT_FULLY_OBSERVABLE`；
- `CLAIM_PRIMARY_MISSING`；
- `MACHINE_OPERATIONALIZATION_MISSING`；
- `MULTIPLE_TIMEFRAMES_UNRESOLVED`。

```text
NR7_MACHINE_READY=NO
PRIMARY_FREEZE_READY=NO
STRATEGY_IDENTITY_CREATED=NO
OUTCOME_TEST_REGISTERED=NO
CANDIDATE_OUTCOME_DATA_USED=NO
```

Holy Grail 相关文件仅作为结构实现参考；本草案未导入任何 Holy Grail 交易语义。

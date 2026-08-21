# HOLY_GRAIL_MACHINE_OPERATIONALIZATION_ENGINEERING_V0_1

> 版本：0.1
> 日期：2026-08-21
> 角色：Holy Grail V0.4 机器操作化工程实现与机器就绪评估证据
> 分支：`preoutcome/holy-grail-v04-machine-ready`
> 结果依据：**未使用任何候选结果 / PnL / Sharpe / 胜率 / 交易次数证据。`CANDIDATE_OUTCOME_USED=NO`。**

## 0. 目的

本文件记录 Holy Grail V0.4 机器操作化的工程实现（`src/holy_grail_machine.py`）与
机器就绪（MACHINE_READY）评估。它复用既有通用组件，不重复造轮子，且不产生任何候选结果。

## 1. 复用的既有组件

```text
src/technical_features     1 分钟会话权威聚合（零聚合）、Decimal/6dp ROUND_HALF_UP
                           数值政策、Wilder ADX、SMA 种子 EMA、点时特征身份
src/stop_order_execution   完成柱保守停损触发 + 最小 OCO 生命周期（RestingStopOrder /
                           evaluate_stop_order / 身份绑定）
src/data_substrate          CompletedBar / SessionMetadata / 会话窗口权威
src/historical_data         NormalizedHistoricalBar 归一化柱
src/playbook_contract       PlaybookContract / MachineOperationalization /
                           validate_contract（机器就绪权威）
```

Holy Grail 专用逻辑（背景/触碰/入场/摆动/跟踪/时序/对称/身份）在
`src/holy_grail_machine.py` 中作为**唯一的机器约定实现**，全部是 Owner 批准的
PROJECT INFERRED 约定，绝不重写为来源声明。

## 2. 机器语义实现要点

### BASE = 1_MINUTE（PROJECT_INFERRED）

- 机器只接受 `kind=INTRADAY, interval_seconds=60` 的聚合（`HolyGrailMachineParameters.base_timeframe=1MIN`）；
- 任何 5/15/30/60/120 分钟聚合在 `evaluate()` 入口失败关闭；
- 30/60/120 分钟保持来源备选身份（解释分支 `SOURCE-PINNED-MULTI-TIMEFRAME-CONCEPT` 与
  `OWNER-APPROVED-TIMEFRAME-BASE-BRANCH`），不被提升为 PRIMARY。

### ADX = 14 / >30 / 1_STEP rising（PROJECT_INFERRED_VERSIONED_NON_OUTCOME）

- 14 周期 Wilder ADX，Decimal 算术、6dp `ROUND_HALF_UP`（复用 `compute_adx`）；
- 初始回撤前背景柱 `c`：`ADX[c] > 30` 且 `ADX[c] > ADX[c-1]`（单步上升）；
- 触碰柱本身不要求上升（`TOUCH_BAR_RISING_REQUIRED=NO`）；
- 只使用已完成柱的 ADX 序列，无前视（`_adx_context` 只读 `c` 与 `c-1`）。

### EMA = 20 / close / prior-completed-bar available

- 触碰判定 `BAR_LOW_LE_EMA_PRIOR_LE_BAR_HIGH`：`bar.low <= EMA_prior <= bar.high`，
  `EMA_prior` 为先前完成柱已可得的 EMA；当前柱收盘不得判定同一柱触碰；
- `CURRENT_BAR_CLOSE_LOOKAHEAD=FORBIDDEN`。

### 入场（buy/sell stop above/below previous-bar high/low）

- 多头：`buy stop = prior.high + 1 tick`；空头镜像：`sell stop = prior.low - 1 tick`
  （1 tick 为 PROJECT_INFERRED 严格"above/below"偏移，无新增距离参数）；
- 触碰柱本身若已越过入场止损价，则同柱顺序不可观察，失败关闭为
  `ENTRY_AMBIGUOUS_INTRABAR_SEQUENCE`（GATE-04）；
- 入场单从触碰柱之后一柱开始驻留；后续完成柱触发即成交（参考价 = 入场止损价）。

### 摆动 = L1_R1 分形枢轴（PROJECT_INFERRED_VERSIONED_NON_OUTCOME）

- 多头摆动低点：`low[t] < low[t-1]` 且 `low[t] < low[t+1]`；空头镜像摆动高点：
  `high[t] > high[t-1]` 且 `high[t] > high[t+1]`；
- 枢轴 `t` 只有在右侧确认柱（`t+1`）完成后方可观察；同柱可用=NO；
- 相等边界（equal-low/equal-high）不构成枢轴（严格比较，确定性）。

### 初始保护停损绑定（GATE-05 完成柱保守时序）

- 成交后绑定"新形成"的已确认摆动低点/高点（多头 sell stop / 空头 buy stop）；
- 若成交时无已确认枢轴，则如实记录 `PROTECTIVE_STOP_PENDING`（停损生效延迟），
  直到第一个已确认枢轴出现才解析——**不伪造"成交即有停损"**；
- 停损触发用完成柱保守模型（成交后下一柱起驻留）。

### 摆动跟踪（SWING_BASED_TRAILING，PROJECT_INFERRED）

- 只用**新确认**枢轴；同一枢轴不重复处理；
- `MONOTONIC_TIGHTEN_ONLY=YES`：多头停损只升（`STOP_RAISED`）不降；空头停损只降
  （`STOP_LOWERED`）不升；
- 更差枢轴忽略（不放松停损）；停损替换记录为 `STOP_REPLACED`（OCO/替换交互确定化）；
- 不增加 ATR / 百分比 / 固定 tick / 保本 / EMA 距离 / Chandelier / 固定-R 等新距离参数。

### 确定性事件排序与身份绑定

- 事件按完成柱序号非降排列；`HolyGrailEventSequence.identity_id` 绑定
  参数身份、机器身份、实现字节身份、特征字节身份、聚合流身份、时间框架身份、事件序列；
- `HolyGrailMachineParameters.identity_id` 绑定全部 Owner 批准绑定值；
- `MachineOperationalization`（契约机器层）的 `code_hash` = `src/holy_grail_machine.py`
  的真实 sha256，`environment_hash` = 确定性环境绑定，`required_feature_versions` 绑定
  通用特征实现身份与机器特征版本，`parameter_identities` 绑定参数身份。

## 3. 测试覆盖（对抗性测试矩阵）

`tests/test_holy_grail_machine_operationalization.py`（35 项）+ 
`tests/test_raschke_holy_grail_v04_machine_ready.py`（19 项）：

- **BASE**：非 1 分钟聚合被拒；1 分钟零聚合；30/60/120 保持来源备选；
- **ADX**：>30 上升成立；>30 平/降不成立；<30 上升不成立；触碰柱下降不影响已成立背景；
  只读已完成柱、无前视；
- **Swing**：L1R1 精确确认（确认柱后才可见）；相等边界不构成枢轴；长/空镜像对称；
- **Trailing**：多头只升；空头只降；更差枢轴忽略（无放松）；同一枢轴不重复；仅新确认枢轴；
  停损替换一致；pending 解析后触发一致；回放确定性；
- **Latency**：无已确认枢轴时 `PROTECTIVE_STOP_PENDING`，首个枢轴解析，解析后触发；
- **Identity**：参数/机器/实现/特征/序列身份稳定且版本化；
- **契约**：V0.3 不可变、来源声明逐字保留、层分离、27 条声明各恰一个 PRIMARY、
  MACHINE_READY 无 blocker、最终决策无结果访问。

## 4. 机器就绪评估（Phase 5）

### V0.3 遗留 4 个 blocker 的关闭状态

```text
HOLY_GRAIL_BASE_TO_MACHINE_INTERVAL   = 1_MINUTE    CLOSED（PROJECT_INFERRED）
HOLY_GRAIL_ADX_RISING_WINDOW          = 1_STEP      CLOSED（PROJECT_INFERRED_VERSIONED_NON_OUTCOME）
HOLY_GRAIL_SWING_CONFIRMATION_COUNTS  = L1_R1       CLOSED（PROJECT_INFERRED_VERSIONED_NON_OUTCOME）
HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION = SWING_BASED_TRAILING  CLOSED（PROJECT_INFERRED）
```

四项全部由 Owner 2026-08-21 绑定批准关闭，无其他未解决的 machine semantic。

### 结论

```text
HOLY_GRAIL_PLAYBOOK_CURRENT_VERSION=V0_4
HOLY_GRAIL_MACHINE_READY=YES
HOLY_GRAIL_PRIMARY_FREEZE_READY=YES
STRATEGY_IDENTITY_CREATED=NO
OUTCOME_TEST_REGISTERED=NO
CANDIDATE_OUTCOME_DATA_USED=NO
RESEARCH_FIREWALL_UNLOCKED=NO
```

`MACHINE_READY=YES` 表示确定性、来源忠实、可版本化的机器约定已齐备（`validate_contract`
通过，无 blocker）；`PRIMARY_FREEZE_READY=YES` 仅表示语义可冻结，冻结本身是未来显式动作。

### StrategyIdentity / outcome registration 保持未开放

按现有 protocol / authority 判断，仍有 Research Wave / 统计画像 / canonical 前置未满足：

```text
PRE_CANDIDATE_CANONICAL_REVALIDATION_REQUIRED=YES（REVALIDATION=COMPLETE_FAIL；ROOT_CAUSE=MIXED）
CANDIDATE_USE_OF_CURRENT_CANONICAL_CORPUS=NOT_AUTHORIZED
REAL_COMMON_STATISTICAL_PROFILE=NOT_ADOPTED
PERFORMANCE_RESEARCH_STARTED=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
```

因此 **StrategyIdentity 创建与 outcome registration 保持未开放**，ResearchFirewall 未解锁。

## 5. 范围与合规

```text
MODIFIES_HOLY_GRAIL_V0_3=NO
MODIFIES_FROZEN_PROTOCOL=NO
MODIFIES_PROPOSAL_BRANCH=NO
MODIFIES_REVIEW_BRANCH=NO
MODIFIES_MAIN=NO
CREATES_V0_4=YES
CANDIDATE_OUTCOME_USED=NO
VALIDATION/HOLDOUT_ACCESS=NOT_AUTHORIZED
SHADOW/FORWARD=NOT_AUTHORIZED
BROKER/REAL_MONEY=NOT_AUTHORIZED
```

# HOLY_GRAIL_MACHINE_OPERATIONALIZATION_OWNER_APPROVAL_2026-08-21

> 版本：0.1
> 日期：2026-08-21
> 角色：正式 Owner 批准证据（FORMAL_OWNER_APPROVAL_EVIDENCE）
> 仓库：`haozhouliuliuliu/kline-playbook-engine`
> 状态：`OWNER_APPROVED_BINDING`
> 机器可读证据：`docs/evidence/HOLY_GRAIL_MACHINE_OPERATIONALIZATION_OWNER_APPROVAL_2026-08-21.json`
> 结果依据：**未使用任何候选结果 / PnL / Sharpe / 胜率 / 交易次数证据。`CANDIDATE_OUTCOME_USED=NO`。**

## 0. 目的与性质

本文件是 Owner 于 **2026-08-21** 对 project-brain 推荐方案的**明确批准**的正式证据。它把
`CURRENT_STATE.md` 中正式记录的 4 个 Holy Grail 机器化阻断项从 `OPEN` / `NOT_ADOPTED`
**绑定关闭**为确定值。这些值是**新的绑定 Owner 批准**，后续不再就这四项询问 Owner。

```text
OWNER_APPROVAL_BINDING=YES
CANDIDATE_OUTCOME_USED=NO
VALIDATION/HOLDOUT_ACCESS=NOT_AUTHORIZED
SHADOW/FORWARD=NOT_AUTHORIZED
BROKER/REAL_MONEY=NOT_AUTHORIZED
RESEARCH_FIREWALL_UNLOCKED=NO
```

## 1. 引用的既有 authority（本文件不重写，仅引用）

```text
已集成 Holy Grail：V0.3
  - docs/evidence/RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_3.json / .md
  - docs/evidence/RASCHKE_HOLY_GRAIL_INTERPRETATION_STATUS_V0_3.md
  - 集成 commit（main）：07977875215ce2501da5bf4ef277f6c202dae3cf
Owner decision proposal：
  - docs/reviews/HOLY_GRAIL_MACHINE_OPERATIONALIZATION_OWNER_DECISION_PACKAGE_V0_1.md / .json
  - 分支 preoutcome/holy-grail-machine-decision-v01，commit add754ee9a983e18f597d463a07de7e7b5ffb78a
Independent adversarial review：
  - docs/reviews/HOLY_GRAIL_MACHINE_OPERATIONALIZATION_DECISION_PACKAGE_ADVERSARIAL_REVIEW_V0_1.md / .json
  - 分支 review/holy-grail-machine-decision-adversarial-v01
  - VERDICT=PASS；CRITICAL_FINDINGS=0；HIGH_FINDINGS=0
```

## 2. Owner 批准的四项绑定决定

以下每项都是 **PROJECT INTERPRETATION / PROJECT INFERRED 机器约定**，**绝不是 SOURCE CLAIM（来源原文）**。
来源只固定了概念（`SOURCE_NOT_PINNED`）；具体绑定值由 Owner 批准的本项目推断确定。

```text
# 1. BASE → 机器周期
HOLY_GRAIL_BASE_TO_MACHINE_INTERVAL=1_MINUTE
分类=PROJECT_INFERRED

# 2. ADX 上升窗口
HOLY_GRAIL_ADX_RISING_WINDOW=1_STEP
分类=PROJECT_INFERRED_VERSIONED_NON_OUTCOME

# 3. 摆动左右确认计数
HOLY_GRAIL_SWING_CONFIRMATION_COUNTS=L1_R1
分类=PROJECT_INFERRED_VERSIONED_NON_OUTCOME

# 4. 跟踪止损机器定义
HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION=SWING_BASED_TRAILING
分类=PROJECT_INFERRED

# 4b. 跟踪分类
TRAILING_CLASSIFICATION=PROJECT_INFERRED
```

### 各项的分层与依据

#### 1) `BASE_TO_MACHINE_INTERVAL=1_MINUTE`

- **SOURCE CLAIM 层**：来源从未给 "BASE"（基础图）赋任何具体分钟值；来源显式命名的较高时间框架备选只有 30/60/120 分钟。
- **OWNER-APPROVED PROJECT INTERPRETATION 层（本决定）**：BASE=1 分钟。理由：项目拥有 1 分钟原生规范底稿
  （零聚合假设）；FGH-GATE-04/GATE-05 的时序语义以 1 分钟分辨率表述；因果干净、无前视。
- **独立对抗性审查**：`BASE_1MIN_VERDICT=PROJECT_INFERRED_BUT_DEFENSIBLE`（确认型 Owner 门；措辞有轻微
  OVERSTATED 修正——不是"最贴近来源主图"，而是"给定现有 authority 下最少新增假设的机器约定"）。
- **30/60/120 分钟备选**：保持来源备选身份，**不**被提升为新的 PRIMARY。

#### 2) `ADX_RISING_WINDOW=1_STEP`

- **SOURCE CLAIM 层**：`SR-V0-M01` 步骤 1 "The 14-period ADX must initially be greater than 30 and rising"。
  来源未规定"rising"的测量窗口/斜率算法。
- **OWNER-APPROVED PROJECT INTERPRETATION 层（本决定）**：在初始回撤前背景柱 `t` 评估 `ADX[t] > ADX[t-1]`
  （单步上升，零额外参数，最小字面读法）。触碰柱不要求上升。
- **独立对抗性审查**：`ADX_1STEP_VERDICT=PROJECT_INFERRED_BUT_DEFENSIBLE`；在 GATE-02
  `EXPLICIT_VERSIONED_INFERRED` 框架内为版本化非结果参数，project brain 可绑定并在集成时 ratify。
- 分类 `PROJECT_INFERRED_VERSIONED_NON_OUTCOME`：属于已批准语义框架内的版本化非结果选择，不是来源事实，
  不用于结果调优。

#### 3) `SWING_CONFIRMATION_COUNTS=L1_R1`

- **SOURCE CLAIM 层**：`SR-V0-M01` 步骤 4 "enter a protective sell stop at the newly formed swing low"。
  来源固定了"新形成的摆动低点"参考概念，未规定枢轴算法或左右确认柱数。
- **OWNER-APPROVED PROJECT INTERPRETATION 层（本决定）**：L=1, R=1（3 柱分形）：
  `low[t] < low[t-1]` 且 `low[t] < low[t+1]`；枢轴 `t` 在 `t+1` 完成后方可确认；同柱可用=NO；
  空头镜像为摆动高点 `high[t] > high[t-1]` 且 `high[t] > high[t+1]`。
- **独立对抗性审查**：`SWING_L1R1_VERDICT=PROJECT_INFERRED_BUT_DEFENSIBLE`（最小结构分形 / 更少新增假设；
  两者同属 source-unpinned 项目推断；因果干净）。在已批准分形框架内为版本化非结果参数。
- 分类 `PROJECT_INFERRED_VERSIONED_NON_OUTCOME`：同上。

#### 4) `TRAILING_STOP_MACHINE_DEFINITION=SWING_BASED_TRAILING`

- **SOURCE CLAIM 层**：`SR-V0-M01` 步骤 4 两个独立陈述：
  陈述 A（初始保护停损）："Once filled, enter a protective sell stop at the newly formed swing low."
  陈述 B（跟踪）："Trail stops as profits grow."（跟踪参考未指定）。
  来源**未 pin** 任何确定性跟踪算法（`SOURCE_DOES_NOT_PIN_TRAILING_ALGORITHM=YES`）。
- **OWNER-APPROVED PROJECT INTERPRETATION 层（本决定）**：采用 **SWING_BASED_TRAILING**——
  盈利扩大时把保护停损上移到最近一个**已确认摆动低点**；复用来源自身已批准的"摆动低点"概念；无新增距离参数；
  `MONOTONIC_TIGHTEN_ONLY=YES`（多头停损只升不降；空头停损只降不升）；更差枢轴忽略；同一枢轴不重复处理。
  **这是两个独立来源陈述拼接成的语义连贯项目推断，绝不是来源声明。**
- **独立对抗性审查**：`SWING_TRAILING_VERDICT=PROJECT_INFERRED_BUT_DEFENSIBLE`（仅当 Owner 关闭阻断项时；
  硬门）。本 Owner 批准即为关闭该硬门的新 Owner 决定。
- 分类 `PROJECT_INFERRED`：保持显式标注并版本化。

## 3. 不得写成来源声明的约束

本批准**不**授权任何后续工件把上述 4 项写为 SOURCE CLAIM。任何机器化实现必须保持三层边界：

```text
SOURCE CLAIM（来源原文真正支持什么）
!=
OWNER-APPROVED PROJECT INTERPRETATION（Owner 已批准的项目解释 / INFERRED 机器约定）
!=
MACHINE OPERATIONALIZATION（机器实现层）
```

上述 4 项全部属于第二层（PROJECT INTERPRETATION），其中 2/3 项进一步标注为
`PROJECT_INFERRED_VERSIONED_NON_OUTCOME`（版本化非结果参数）。

## 4. 结果边界

```text
CANDIDATE_OUTCOME_USED=NO
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
RESEARCH_FIREWALL_UNLOCKED=NO
```

本批准只决定 4 个机器化语义绑定值；它**不**解锁任何候选结果 / 回测 / 验证 / 最终留出 / 影子 / 实盘访问。

## 5. 范围声明

```text
MODIFIES_HOLY_GRAIL_V0_3=NO
MODIFIES_FROZEN_PROTOCOL=NO
MODIFIES_PROPOSAL_BRANCH=NO
MODIFIES_REVIEW_BRANCH=NO
MODIFIES_MAIN=NO
CREATES_V0_4=YES（本工作包在 preoutcome/holy-grail-v04-machine-ready 分支上构建 V0.4）
```

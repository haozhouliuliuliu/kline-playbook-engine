# HOLY_GRAIL_MACHINE_OPERATIONALIZATION_OWNER_DECISION_PACKAGE_V0_1

> 版本：0.1
> 日期：2026-08-21
> 角色：pre-outcome（看结果前）研究 / Owner 决策准备 —— **决策包（decision package），不含任何语义冻结**
> 仓库：`haozhouliuliuliu/kline-playbook-engine`
> 分支：`preoutcome/holy-grail-machine-decision-v01`
> 基线：`ec50649a9e1c27380a14f6d997f3e641bb9a6ea8`（origin/main）
> 状态：`PROPOSAL_ONLY_NOT_ADOPTED`（本文件只压缩选项并给出推荐；采纳必须由 Owner 显式批准）
> 结果依据：**未使用任何候选结果 / PnL / Sharpe / 胜率 / 交易次数证据。`CANDIDATE_OUTCOME_USED=NO`。**

```text
PURPOSE=把 Holy Grail 机器化的 4 个正式未解决项压缩成 Owner 能用最少选择完成的决策包
DECISION_STATUS=PROPOSAL_ONLY_NOT_ADOPTED
CANDIDATE_OUTCOME_USED=NO
VALIDATION/HOLDOUT_ACCESS=NOT_AUTHORIZED
SHADOW/FORWARD=NOT_AUTHORIZED
BROKER/REAL_MONEY=NOT_AUTHORIZED
MODIFIES_FROZEN_PROTOCOL=NO
MODIFIES_MAIN=NO
CREATES_V0_4=NO
SETS_MACHINE_READY=NO
```

## 0. 目的与边界

本决策包处理 `CURRENT_STATE.md` 中正式记录的 4 个正常结果前操作化前提：

```text
HOLY_GRAIL_BASE_TO_MACHINE_INTERVAL=OPEN
HOLY_GRAIL_ADX_RISING_WINDOW=OPEN_VERSIONED_NON_OUTCOME_CHOICE
HOLY_GRAIL_SWING_CONFIRMATION_COUNTS=OPEN_VERSIONED_NON_OUTCOME_CHOICE
HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION=NOT_ADOPTED
```

目标不是无限研究，而是**压缩**：让每一项都明确分层（来源事实 / 已批准解释 / 引擎能力 / 非结果选项 / 因果与忠实度后果 / 推荐 / 备选 / 未知），
并给出 Owner 用最少选择即可关闭的决策块。

本文件**不修改**：
- Holy Grail V0.3（`RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_3.*`、`RASCHKE_HOLY_GRAIL_INTERPRETATION_STATUS_V0_3.md`）；
- `CURRENT_STATE.md`、`00_READ_FIRST.md`；
- 冻结协议（`HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` 等）；
- Owner 批准证据（`FGH_SEMANTIC_GATE_OWNER_APPROVAL_2026-08-20.md` 等）。

本文件**不创建 V0.4**，**不设置 MACHINE_READY**，**不替 Owner 冻结任何研究语义**。

### 分层边界（沿用协议 v1.0）

```text
SOURCE CLAIM（来源原文真正支持什么）
!=
OWNER-APPROVED PROJECT INTERPRETATION（Owner 已批准的项目解释 / INFERRED 机器约定）
!=
MACHINE OPERATIONALIZATION（机器实现层；本包只准备语义，不实现）
```

### A / B 分类原则（本包对每一项的判断）

- **A 类（普通工程选择）**：project brain / engineering 可依据既有 authority 自动决定。本包判定：**所有通用机器机制**
  （参数化的 EMA/ADX 计算、柱间聚合、枢轴检测、止损/OCO 机制、6dp `ROUND_HALF_UP` 数值政策、完成柱保守时序）都是 A 类，
  可在决策前由工程构建为参数化通用机制，且不冻结绑定值。
- **B 类（新研究语义，须 Owner 决定）**：本包 4 个阻断项各自的**绑定值**（BASE 具体机器周期、ADX 上升窗口、摆动左右确认计数、
  跟踪止损机器定义）都是 B 类——它们影响结果语义，`CURRENT_STATE` 显式把它们列为 OPEN / NOT_ADOPTED，且 Owner 批准未委托给项目脑。

**Owner 最终只面对真正不可代替的研究语义选择**；普通工程问题（机制、数值政策、聚合实现）不在本包推给 Owner。

---

## 1. 总览表

| 阻断项 | 当前正式状态 | 推荐选择（PROJECT INFERRED） | 备选 | OWNER_DECISION_REQUIRED |
|---|---|---|---|---|
| 1 BASE→MACHINE_INTERVAL | `OPEN` | **BASE=1-minute**（最小任意性、原生底稿、与已批准 1m 时序一致） | 5m/15m（无来源依据）；保留 OPEN | **YES**（确认或另选；单选接受） |
| 2 ADX_RISING_WINDOW | `OPEN_VERSIONED_NON_OUTCOME_CHOICE` | **window=1 步**（`ADX[t]>ADX[t-1]`，在初始背景柱评估） | N=3 单调上升（更稳健） | **YES**（二选一） |
| 3 SWING_CONFIRMATION_COUNTS | `OPEN_VERSIONED_NON_OUTCOME_CHOICE` | **L=1, R=1**（3 柱分形，最小任意性、响应"新形成"） | L=2, R=2（5 柱标准分形，更稳健） | **YES**（二选一） |
| 4 TRAILING_STOP_MACHINE_DEFINITION | `NOT_ADOPTED` | **保持 NOT_ADOPTED（fail-closed 默认）**；若 Owner 要关闭该阻断项，则选 **摆动低点跟踪（PROJECT INFERRED）** | 固定距离跟踪（发明算法、隐藏参数）；保留 NOT_ADOPTED | **YES**（三选一） |

> 每一项的 `OWNER_DECISION_REQUIRED=YES` 都只对应一个语义绑定值；工程机制全部 A 类，无需 Owner 决策。

---

## 2. 阻断项 1 —— HOLY_GRAIL_BASE_TO_MACHINE_INTERVAL

### SOURCE FACT（来源原文真正支持什么）

- `SR-V0-M05`（Traders Toolbox，2004-03）原文含义："价格先回撤到 20 柱 EMA……然后同样的回撤会依次出现在 **30 分钟图、60 分钟图、120 分钟图**……每次回撤在该时间框架上都必须先有 14 柱 ADX>30。"
- `SR-V0-M01`（Short Term Trading Strategies，1997-08）四条买入规则基于**周期**（14 周期 ADX、20 周期 EMA），对柱时间框架本身是中性的（bar-timeframe-agnostic）。
- 来源**从未给 "BASE"（基础图）赋任何具体分钟值**。来源显式命名的较高时间框架备选只有 30/60/120 分钟；BASE 隐含在 30 分钟以下（或至少是主图），但其确切周期未说明。
- SOURCE_ONLY 会话记录："No single operating timeframe is uniquely pinned for the whole loop."

### OWNER-APPROVED PROJECT INTERPRETATION（Owner 已批准的解释）

- `FGH_SEMANTIC_GATE_OWNER_APPROVAL_2026-08-20`（GATE-06，OWNER_APPROVED_BINDING）：
  `PRIMARY_TIMEFRAME_BRANCH=BASE`；`SOURCE_ALTERNATIVES=30MIN,60MIN,120MIN`；`BASE_TO_MACHINE_INTERVAL=EXPLICIT_BEFORE_MACHINE_READY`。
- `RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_3`：`BASE_TO_MACHINE_INTERVAL=OPEN`（本工件不做 1m/5m/15m/30m 映射）。
- GATE-04/GATE-05 的时序语义均以 **"1 分钟分辨率"** 表述（`INTRABAR_ORDERING=NOT_OBSERVABLE_AT_1M`、同柱事件失败关闭为 `AMBIGUOUS_INTRABAR_SEQUENCE`）。

### CURRENT ENGINE CONSTRAINT（现有引擎已能表达什么）

- 规范数据底稿为 **1 分钟粒度**（`CANONICAL_GRANULARITY=1-minute`）：1m 柱零聚合直接可得。
- 30/60/120 分钟可由 1m 因果聚合导出（FGH-GATE-06 非结果矩阵记为 `OBSERVABLE_NOW`；D-02 窗口权威），但 Holy Grail 专用柱间聚合尚未在 `src/` 实现。
- 已批准的完成柱保守时序 / 同柱歧义失败关闭机制在语义上以 1m 为基准。
- `StrategyIdentity` 需要单一 `timeframe_scope`（Package C P-05 桥接约束）。

### NON-OUTCOME OPTIONS（完全不看结果时的合理选项）

- **O1：BASE = 1-minute**（项目原生 1m 底稿；零聚合假设；与已批准 1m 时序一致；最小任意性）。
- **O2：BASE = 5-minute 或 15-minute**（常见盘中图表；但**无任何来源依据**，纯任意选择，且需新增聚合假设）。
- **O3：保留 OPEN**（本包不映射，继续阻断 MACHINE_READY）。
- （30/60/120 分钟**不**作为 BASE 选项：它们已被批准为来源"较高时间框架备选"，不是 BASE 本身；BASE 隐含在 30 分钟以下。）

### LOOKAHEAD / CAUSALITY CONSEQUENCE（前视/因果影响）

- 任何机器周期都必须由**已完成的更低粒度柱**因果聚合（柱收盘后下一柱才可用）。1m 是原生因果边界，无聚合误差。
- 若选 5m/15m，需额外固定聚合对齐规则（会话边界、夜盘跨日），属于新增任意性；聚合本身可实现为因果通用机制（A 类），但**周期值**是 B 类语义选择。

### SOURCE-FAITHFULNESS CONSEQUENCE（来源忠实度影响）

- 来源未固定 BASE 分钟值；因此任何具体映射都是 **PROJECT INFERRED 机器约定**，绝不能重标签为来源声明。
- BASE→1m 是"最小任意性 + 原生底稿"的推断，最贴近来源"主图"概念；5m/15m 无来源依据，忠实度更低。
- 30/60/120 作为来源备选保持不变，本选择不消除它们。

### ENGINEERING CONSEQUENCE（工程实现影响）

- BASE=1m：无需新增聚合；EMA/ADX/摆动/触发直接消费 1m 规范柱；与已批准 1m 同柱时序一致。工程量最小。
- BASE=5m/15m：需新增确定性柱间聚合 + 身份绑定，工程量更大，且引入额外任意 DOF。

### RECOMMENDED CHOICE（仅凭来源、简单性、因果正确性）

```text
RECOMMENDED=BASE_TO_MACHINE_INTERVAL=1_MINUTE
LABEL=PROJECT_INFERRED（来源未固定；最小任意性机器约定）
```

理由：来源仅隐含 BASE 为 30 分钟以下主图；项目拥有 1 分钟原生规范底稿；1m 是唯一**零聚合假设**的选择，
与已批准的 1m 分辨率时序语义（GATE-04/05）内部一致，且因果干净、无前视。这不是"通过回测选周期"，而是最小任意性的非结果工程/语义推断。

### ALTERNATIVES

- BASE=5m / 15m（PROJECT INFERRED；无来源依据，需额外聚合任意性）。
- 保留 OPEN（继续阻断，直到 Owner 另有决定）。

### WHAT REMAINS UNKNOWN（仍未知）

- 来源从未说明 Raschke 实际基础图的分钟值；无从由来源唯一确定 1/3/5/10/15 分钟中的哪一个。
- 30/60/120 分钟备选的具体机器化仍属更高时间框架确认（非本阻断项范围）。

### OWNER_DECISION_REQUIRED

```text
OWNER_DECISION_REQUIRED=YES
DECISION_TYPE=确认推荐（1-minute）或从<30分钟整数倍菜单另选
SINGLE_ACCEPTANCE=YES
```

---

## 3. 阻断项 2 —— HOLY_GRAIL_ADX_RISING_WINDOW

### SOURCE FACT（来源原文真正支持什么）

- `SR-V0-M01` 步骤 1："The 14-period ADX must **initially** be greater than 30 **and rising**."
- `SR-V0-M01` 步骤 2：回撤到 20 周期 EMA "usually accompanied by a **turndown in ADX**"（回撤阶段 ADX 通常回落）。
- 来源**没有**给"rising"规定任何测量窗口或斜率算法；只有"上升"这一概念是显式的。
- `SR-V0-M05`："each retracement has to be preceded by a 14-bar ADX reading above 30 on that time frame"（此处只要求 >30 水平，未重述 rising 窗口）。

### OWNER-APPROVED PROJECT INTERPRETATION（Owner 已批准的解释）

- `FGH-GATE-02`（OWNER_APPROVED_BINDING）：`ADX_PERIOD=14`；`ADX_THRESHOLD=>30`；`ADX_CONTEXT=INITIAL_PRE_PULLBACK`；
  `TOUCH_BAR_RISING_REQUIRED=NO`；`OLD_TOUCH_BAR_ONE_STEP_RULE=NOT_AUTHORITY`；`ADX_RISING_WINDOW=EXPLICIT_VERSIONED_INFERRED`。
- 上升测试用**显式确定性窗口**，标记为 `INFERRED`；精确窗口长度仍开放（`OPEN_VERSIONED_NON_OUTCOME_CHOICE`）。

### CURRENT ENGINE CONSTRAINT（现有引擎已能表达什么）

- 数值政策已批准：Wilder ADX 初始化（`WILDER_SMA_DX`）、Decimal 算术、6dp `ROUND_HALF_UP`、版本化身份绑定（FGH-GATE-03）。
- ADX 计算与"上升"判定可参数化实现（A 类通用机制）；窗口长度作为绑定值由本阻断项决定。

### NON-OUTCOME OPTIONS（完全不看结果时的合理选项；只列来源/工程上合理的确定性定义）

- **定义 A（window=1，单步）**：在初始背景柱 `t`，`ADX[t] > ADX[t-1]`。字面"上升"= 最近一步向上；**零额外参数，最小任意性**。
- **定义 B（window=3，连续单调）**：`ADX[t] > ADX[t-1] > ADX[t-2] > ADX[t-3]`。对单柱噪声更稳健，但引入一个固定窗口参数（N=3）。
- **定义 C（window=3，净上升）**：`ADX[t] > ADX[t-3]`。备选稳健读法（起点到终点的净变化）。
- （不枚举大量参数；只有上面三种来源/工程上自然的最小集合。）

> 背景柱定义（"初始背景"在哪个柱评估）是 A 类工程时序细节：推荐约定为**触碰柱之前最后一个已完成的柱**（严格先于 EMA 触碰柱），因果可用且符合"回撤前初始背景"语义。窗口长度才是本阻断项的 B 类语义选择。

### LOOKAHEAD / CAUSALITY CONSEQUENCE（前视/因果影响）

- 上升判定只在**背景柱（触碰柱之前已完成）** 用已完成 ADX 序列评估，无前视。
- 触碰柱本身不要求上升（已批准），因此 ADX 在回撤期自然回落不会误杀已成立的初始背景。

### SOURCE-FAITHFULNESS CONSEQUENCE（来源忠实度影响）

- 任何窗口都是 **PROJECT INFERRED 机器约定**，不是来源声明；来源只固定"初始 >30 且上升"概念。
- 定义 A 是字面最小读法，最贴近"rising"一词；定义 B/C 是更保守的工程稳健读法。旧"触碰柱上 ADX[t]>ADX[t-1]"规则已确认 `NOT_AUTHORITY`，本包不复活它。

### ENGINEERING CONSEQUENCE（工程实现影响）

- 定义 A 实现最简单（单步比较，无窗口参数），身份绑定最少。
- 定义 B/C 需要参数化窗口并纳入特征身份哈希；实现仍是通用机制（A 类），绑定值（window=1 或 3）由本阻断项决定。

### RECOMMENDED CHOICE（仅凭来源、简单性、因果正确性）

```text
RECOMMENDED=ADX_RISING_WINDOW=1_STEP（ADX[t]>ADX[t-1]，在初始背景柱评估）
LABEL=PROJECT_INFERRED（来源未固定窗口；最小任意性）
```

理由：来源只表达"上升"概念，最字面、零额外参数的确定性定义是单步上升；它满足 `EXPLICIT_VERSIONED_INFERRED` 要求，
因果干净、可复现、隐藏自由度最小。若 Owner 更看重对单柱噪声的稳健性，可改选定义 B（N=3 连续单调）。

### ALTERNATIVES

- 定义 B（window=3 连续单调）——更稳健，加一个固定参数。
- 定义 C（window=3 净上升）——备选读法。
- 保持 OPEN——继续阻断 MACHINE_READY。

### WHAT REMAINS UNKNOWN（仍未知）

- 来源未规定"上升"的斜率测量窗口；1 步 vs 多步在来源层面不可区分。
- 背景柱的精确定义（触碰柱前第几根）属工程时序细节，需在实现时版本化绑定（A 类）。

### OWNER_DECISION_REQUIRED

```text
OWNER_DECISION_REQUIRED=YES
DECISION_TYPE=二选一：定义 A（window=1，推荐）或定义 B（window=3 单调）
SINGLE_ACCEPTANCE=YES
```

---

## 4. 阻断项 3 —— HOLY_GRAIL_SWING_CONFIRMATION_COUNTS

### SOURCE FACT（来源原文真正支持什么）

- `SR-V0-M01` 步骤 4："Once filled, enter a protective **sell stop at the newly formed swing low**."（空头镜像为摆动高点。）
- 来源固定了"新形成的摆动低点"这一**参考概念**，但**没有**规定任何软件枢轴算法，也没有左右确认柱数。

### OWNER-APPROVED PROJECT INTERPRETATION（Owner 已批准的解释）

- Owner 批准（2026-08-20）：`SWING_DEFINITION=FRACTAL_PIVOT_EXPLICIT_CONFIRMATION`；`RIGHT_SIDE_CONFIRMATION_REQUIRED=YES`；
  `SAME_BAR_AVAILABILITY=NO`；`SHORT_SIDE=MIRROR_SWING_HIGH`；`SWING_CONFIRMATION_COUNTS=EXPLICIT_VERSIONED_NON_OUTCOME_CHOICE`。
- 只缺**左右确认柱数**（`OPEN_VERSIONED_NON_OUTCOME_CHOICE`）。

### CURRENT ENGINE CONSTRAINT（现有引擎已能表达什么）

- 引擎尚无枢轴检测实现；FGH 决定定义了语义（分形、右确认、同柱不可用），确认计数将作为版本化参数绑定进特征身份。
- 已批准的完成柱保守时序 / 同柱歧义失败关闭机制（GATE-05）约束停损激活时序。

### NON-OUTCOME OPTIONS（完全不看结果时的合理选项）

- **选项 A（最小约定）：L=1, R=1（3 柱分形）**——`low[t] < low[t-1]` 且 `low[t] < low[t+1]`。
  枢轴在柱 `t`，右侧确认完成于柱 `t+R = t+1`。**最小任意性（一个局部极值至少需要每侧 1 柱），响应"新形成"最及时。**
- **选项 B（标准分形）：L=2, R=2（5 柱分形）**——`low[t]` 低于左右各 2 柱。更稳健（对单柱噪声不敏感），但确认更慢（`t+2` 才可用），且计数更大是工程惯例而非来源事实。

### LOOKAHEAD / CAUSALITY CONSEQUENCE（前视/因果影响）

- 因果可用性：枢轴在柱 `t`，只有右侧 R 根确认柱完成后（柱 `t+R`）才可观察；**同柱可用禁止**（已批准）。
- 停损放置延迟：保护停损参考（新形成摆动低点）在 `t+R` 才可放置。若入场成交早于首个被确认摆动低点，则**从成交到首个确认枢轴之间存在停损空窗**，
  该延迟必须如实记录，不得伪造"成交即有停损"。
- 选择 R 越大，停损生效越晚（对已持有仓位风险越大）；R=1 延迟最小。

### SOURCE-FAITHFULNESS CONSEQUENCE（来源忠实度影响）

- 左右计数都是 **PROJECT INFERRED 机器约定**，不是来源事实；来源只固定"新形成的摆动低点"概念。
- 不能因为"常见技术分析习惯"（如 2-2 标准分形）就冒充来源事实；选项 A/B 都明确标记为 PROJECT INFERENCE。

### ENGINEERING CONSEQUENCE（工程实现影响）

- 分形枢轴检测可实现为参数化通用机制（A 类）；`(L,R)` 作为版本化绑定值纳入特征身份哈希。
- 停损激活时序与 GATE-05 的完成柱保守时序衔接：枢轴在 `t+R` 可用后，其停损在下一个已完成柱开始生效（沿用完成柱语义）。

### RECOMMENDED CHOICE（仅凭来源、简单性、因果正确性）

```text
RECOMMENDED=SWING_CONFIRMATION_COUNTS=L1_R1（3柱分形）
LABEL=PROJECT_INFERRED（来源未固定计数；最小任意性）
```

理由：来源要求"**新形成**的摆动低点"，强调时效性；`(1,1)` 是最小任意性的确定性分形（一个局部极值至少需要每侧 1 柱），
停损延迟最小、因果干净、可复现。若 Owner 更看重稳健性，可改选 `(2,2)`。

### ALTERNATIVES

- `(L=2, R=2)` 5 柱标准分形——更稳健，确认更慢。
- 保持 OPEN——继续阻断 MACHINE_READY。

### WHAT REMAINS UNKNOWN（仍未知）

- 来源未规定摆动识别的柱数；`(1,1)` vs `(2,2)` 在来源层面不可区分。
- "新形成摆动低点"在入场时通常指回撤期间/刚形成的低点；其与入场成交的先后关系受 GATE-04/05 同柱歧义失败关闭约束，属于已批准语义，不在此重复。

### OWNER_DECISION_REQUIRED

```text
OWNER_DECISION_REQUIRED=YES
DECISION_TYPE=二选一：(L=1,R=1)（推荐）或 (L=2,R=2)
SINGLE_ACCEPTANCE=YES
```

---

## 5. 阻断项 4 —— HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION

### 有限来源复核（bounded source check；只读已有 source bundle 与项目已保存/讨论过的 Raschke 官方/近官方来源）

来源证据包：`HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_HOLY_GRAIL_V0_1.json`（SB-RASCHKE-HOLY-GRAIL-SEMANTIC-V1）及其 SOURCE_ONLY 会话。

| 材料 | 相关原文/含义 | 是否 pin 确定性跟踪算法 |
|---|---|---|
| `SR-V0-M01`（1997-08）步骤 4 | "Trail stops as profits grow."（盈利增长时跟踪止损） | **否**——只有概念 |
| `SR-V0-M04`（2000-08） | "the minute the market gives back more than it should, you get out on the first reaction or pause"；"take at least half off at a price objective" | **否**——定性 give-back 管理 / 定性部分止盈，非跟踪算法 |
| `SR-V0-M05`（2004-03） | "By then you should be looking for a top." | **否**——定性顶部背景 |
| bundle 付费备选 | Trading Sardines（2015 书）、Street Smarts（书）——**未购买、未授权、不可作为证据** | 未验证的潜在可能，非来源事实 |
| SOURCE_ONLY 会话 | "trailing mechanics (swing/MA/distance-based) not source-pinned" | 明确记录：机制未 pin |

### 结论

```text
SOURCE_DOES_NOT_PIN_TRAILING_ALGORITHM=YES
```

来源只支持 "trail as profits grow" 概念；**没有任何 ATR / 百分比 / EMA / 保本 / 摆动 / Chandelier / 固定 R 步长算法** 出现在已接受的来源证据中。
任何确定性跟踪规则都只能是 Owner 明确选择的 **PROJECT INFERRED** 约定，绝不可能是来源声明。

### SOURCE FACT（来源原文真正支持什么）

- 仅 `SR-V0-M01` 步骤 4 "Trail stops as profits grow."；以及 `SR-V0-M04` 定性的"给回过多即离场/首次反应或停顿离场"（管理原则，非确定性算法）。

### OWNER-APPROVED PROJECT INTERPRETATION（Owner 已批准的解释）

- Owner 批准（2026-08-20）：`APPROVE_TRAILING_STOP=OPTION_A_NO_MACHINE_TRAILING_UNTIL_SOURCE_PINNED`；
  `TRAILING_STOP_MACHINE_DEFINITION=NOT_ADOPTED_UNTIL_SOURCE_PINNED_OR_NEW_OWNER_DECISION`；
  `OUTCOME_TUNING_FOR_TRAILING=FORBIDDEN`。
- 即：**除非来源被固定，或 Owner 作出新的显式决定并提供确定性规则**，否则 PRIMARY 不机器跟踪。

### CURRENT ENGINE CONSTRAINT（现有引擎已能表达什么）

- 通用停损/OCO 机制已集成（`FGH_GENERIC_STOP_OCO_CORE=INTEGRATED_ACCEPTED`），停损是参数化通用机制（A 类）。
- 但**跟踪止损的绑定定义**尚未采纳；引擎目前只能表达"初始保护停损"，不能表达任何跟踪环。
- 摆动低点分形定义（阻断项 3）一旦选定，可作为跟踪参考的可复用基础。

### NON-OUTCOME OPTIONS（完全不看结果时的合理选项；候选类别数量最少、彼此语义明显不同）

- **类别 1：NO_MACHINE_TRAILING（保持 NOT_ADOPTED，fail-closed）**——PRIMARY 退出仅由初始保护停损（摆动低点）+ 可选变体构成；
  跟踪止损继续作为开放研究前提。**零发明机制**，与当前绑定状态一致。这不是"结果调优"，而是诚实的失败关闭。
- **类别 2：SWING-BASED TRAILING（PROJECT INFERRED）**——盈利扩大时，把保护停损**上移到最近一个已确认摆动低点**（复用阻断项 3 的分形定义）。
  理由：复用了来源自身已有的"摆动低点"概念（已是 Owner 批准的 INFERRED 约定），确定性、因果干净、**无新增距离参数**。
  **注意：这仍不是来源声明**——来源只说"盈利增长时跟踪止损"，从未说"跟踪到最近摆动低点"。该循环是项目推断。
- **类别 3：FIXED-DISTANCE TRAILING（PROJECT INFERRED）**——以固定距离（固定 tick / 固定点数，或 ATR 倍数等）跟踪入场后最高点。
  语义上与类别 2 明显不同，但**完全发明**，且距离值是一个隐藏自由度参数（任意性最大）；ATR 不在来源中。

### LOOKAHEAD / CAUSALITY CONSEQUENCE（前视/因果影响）

- 任何跟踪都必须只用**已确认**的参考（如已确认摆动低点 / 已完成柱的最高点），禁止用当前柱未完成数据。
- 类别 2 只使用 `t+R` 才可用的已确认枢轴，无前视；类别 3 使用已完成柱极值，无前视但需固定极值窗口。

### SOURCE-FAITHFULNESS CONSEQUENCE（来源忠实度影响）

- 来源未固定任何算法；**类别 2/3 都不是来源声明**，必须显式标记 PROJECT INFERRED。
- 类别 2 因复用来源自身"摆动低点"概念而最贴近来源语义；类别 3 语义上完全外生（发明参数）。
- 若 Owner 选择类别 1，则忠实度最高（不发明），代价是 PRIMARY 在跟踪轴上保持 NOT_MACHINE_READY。

### ENGINEERING CONSEQUENCE（工程实现影响）

- 通用跟踪止损机制可实现为参数化通用机制（A 类），绑定定义（无 / 摆动 / 固定距离）由本阻断项决定。
- 类别 2 复用阻断项 3 的枢轴输出，工程复用度最高；类别 3 需要新增极值窗口与距离参数并纳入身份哈希。

### RECOMMENDED CHOICE（仅凭来源、简单性、因果正确性）

```text
RECOMMENDED_DEFAULT=KEEP_TRAILING_STOP_NOT_ADOPTED（类别1，fail-closed，与当前绑定状态一致）
RECOMMENDED_IF_CLOSING_BLOCKER=SWING_BASED_TRAILING（类别2，PROJECT_INFERRED）
```

理由：来源无法 pin 确定性跟踪算法（`SOURCE_DOES_NOT_PIN_TRAILING_ALGORITHM`），因此**诚实的默认是保持 NOT_ADOPTED**；
若 Owner 决定在本次关闭该阻断项，类别 2（摆动低点跟踪）是唯一复用来源自身概念、无新增距离参数、确定性且因果干净的 PROJECT INFERRED 选择。
本包**不替 Owner 冻结**；类别 1 与类别 2 都是合法 Owner 选择。

### ALTERNATIVES

- 类别 3（固定距离跟踪）——发明算法 + 隐藏距离参数；仅当 Owner 明确需要时。
- 保持 NOT_ADOPTED（类别 1）——PRIMARY 在跟踪轴保持 NOT_MACHINE_READY，等待未来来源或 Owner 决定。

### WHAT REMAINS UNKNOWN（仍未知）

- 是否存在未记录的官方/付费来源能 pin 跟踪机制（Trading Sardines、Street Smarts 未购买、未授权，**不能**作为证据）。
- 类别 2 中"最近已确认摆动低点"与初始停损的关系（初始停损即首次摆动低点，随后上移到更新的摆动低点）是推断细节，需在实现时版本化绑定。

### OWNER_DECISION_REQUIRED

```text
OWNER_DECISION_REQUIRED=YES
DECISION_TYPE=三选一：类别1（保持NOT_ADOPTED，推荐默认）/ 类别2（摆动低点跟踪，推荐若关闭）/ 类别3（固定距离跟踪）
SINGLE_ACCEPTANCE=YES
```

---

## 6. A / B 分类汇总

| 阻断项 | A 类（工程可自动决定；通用机制） | B 类（Owner 必须决定；语义绑定值） |
|---|---|---|
| BASE→INTERVAL | 柱间聚合实现、完成柱因果对齐、30/60/120 备选聚合机制 | **BASE 具体机器周期**（推荐 1m） |
| ADX RISING | Wilder ADX 计算、Decimal/6dp ROUND_HALF_UP、背景柱时序细节（触碰前最后一根已完成柱） | **上升窗口**（window=1 或 3） |
| SWING COUNTS | 分形枢轴检测通用机制、停损激活时序（完成柱语义） | **左右确认计数**（1-1 或 2-2） |
| TRAILING | 通用跟踪/停损/OCO 机制 | **跟踪止损机器定义**（类别 1/2/3） |

> 原则：**不要把普通工程问题推给 Owner**。Owner 最终只面对 4 个语义绑定选择（第 7 节），其中第 1 项是"确认推荐"、第 2/3 项是"二选一"、第 4 项是"三选一"。

---

## 7. 最终 Owner 决策块（PROPOSAL ONLY —— 未被本文件批准）

Owner 可逐行确认。以下均为 `PROPOSAL_ONLY_NOT_ADOPTED`；采纳后需写入新版本化工件并更新状态（不由本包完成）。

```text
PROPOSAL_ONLY_NOT_ADOPTED=YES
CANDIDATE_OUTCOME_USED=NO

# 1. BASE→机器周期（确认推荐，或从<30分钟整数倍菜单另选）
DECIDE_HOLY_GRAIL_BASE_TO_MACHINE_INTERVAL=1_MINUTE   [备选：5_MINUTE / 15_MINUTE / KEEP_OPEN]

# 2. ADX 上升窗口（二选一）
DECIDE_HOLY_GRAIL_ADX_RISING_WINDOW=1_STEP            [备选：3_STEP_MONOTONIC]

# 3. 摆动左右确认计数（二选一）
DECIDE_HOLY_GRAIL_SWING_CONFIRMATION_COUNTS=L1_R1     [备选：L2_R2]

# 4. 跟踪止损机器定义（三选一）
DECIDE_HOLY_GRAIL_TRAILING_STOP_MACHINE_DEFINITION=KEEP_NOT_ADOPTED
   [备选：SWING_BASED_TRAILING（推荐若关闭）/ FIXED_DISTANCE_TRAILING]
```

任何未设置的行保持该阻断项开放，并继续阻断 Holy Grail `MACHINE_READY` / `PRIMARY`。本文件不冻结任何决定。

---

## 8. 验证记录

```text
CANDIDATE_OUTCOME_USED=NO
VALIDATION/HOLDOUT_ACCESS=NOT_AUTHORIZED
SHADOW/FORWARD=NOT_AUTHORIZED
BROKER/REAL_MONEY=NOT_AUTHORIZED
PRODUCTION_CODE_CHANGED=NO
TESTS_CHANGED=NO
GIT_DIFF_CHECK=PENDING（提交前执行 git diff --check）
SOURCE_BUNDLE_REVIEWED=HUMAN_PLAYBOOK_SOURCE_BUNDLE_RASCHKE_HOLY_GRAIL_V0_1.json
SOURCE_ONLY_SESSION_REVIEWED=HUMAN_PLAYBOOK_SOURCE_ONLY_SESSION_RASCHKE_HOLY_GRAIL_V0_1.json
AUTHORITY_REVIEWED=AGENTS.md / OWNER_COLLABORATION_CONTRACT.md / ARCHITECTURE_BASELINE.md / CURRENT_STATE.md /
  00_READ_FIRST.md / RESEARCH_DIRECTION.md / KNOWN_LIMITATIONS_AND_TECH_DEBT.md /
  HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md / FGH_SEMANTIC_GATE_OWNER_APPROVAL_2026-08-20.md /
  RASCHKE_HOLY_GRAIL_PLAYBOOK_CONTRACT_DRAFT_V0_3.* / RASCHKE_HOLY_GRAIL_INTERPRETATION_STATUS_V0_3.md
```

## 9. 来源锚点

```text
M01 (1997-08, AIQ Opening Bell, Short Term Trading Strategies):
  step1 "The 14-period ADX must initially be greater than 30 and rising."
  step2 "Look for a retracement in price to the 20-period exponential moving average,
         usually accompanied by a turndown in ADX."
  step3 "When price touches the 20-period moving average, put a buy stop above the high
         of the previous bar."
  step4 "Once filled, enter a protective sell stop at the newly formed swing low.
         Trail stops as profits grow."
M04 (2000-08, Active Trader, The Rituals of Trading):
  "the minute the market gives back more than it should, you get out on the first
   reaction or pause"; "take at least half off at a price objective when continuation
   is uncertain."
M05 (2004-03, Active Trader, Traders Toolbox):
  "...price first pulls back to the 20-bar EMA... then the same retracement will occur
   on the 30-minute chart, then the 60-minute chart, then the 120-minute time frame.
   By then you should be looking for a top. But each retracement has to be preceded by
   a 14-bar ADX reading above 30 on that time frame."
```

```text
SOURCE_STATUS_SUMMARY=
  BASE machine interval       : SOURCE_NOT_PINNED -> PROJECT_INFERRED (recommend 1m)
  ADX rising window           : SOURCE_NOT_PINNED -> PROJECT_INFERRED (window=1 or 3)
  Swing confirmation counts   : SOURCE_NOT_PINNED -> PROJECT_INFERRED (L1R1 or L2R2)
  Trailing machine definition : SOURCE_NOT_PINNED -> SOURCE_DOES_NOT_PIN_TRAILING_ALGORITHM
```

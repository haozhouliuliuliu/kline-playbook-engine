# COMMON_STATISTICAL_PROFILE_OWNER_DECISION_PACKAGE_V0_1

> Version: 0.1
> Date: 2026-08-21
> Role: project-brain（项目脑）Owner 决策压缩包 — 统一统计标准接受路线
> Repository: `haozhouliuliuliu/kline-playbook-engine`
> Official main base: `e87315dd622689eb165dbe81f1728c868cc06a26`
> Branch: `preoutcome/stat-profile-owner-decision-v01`
> Status: `DECISION_PREPARATION_ONLY / NOT_ADOPTED / NO_OUTCOME_DATA_USED`
> Authority chain: frozen `HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`, frozen `HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`, `HUMAN_PLAYBOOK_HISTORICAL_V1_EVIDENCE_POLICY_V1_0.md`, `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_ADJUDICATION_V0_3.md`, independent review `parallel/stat-profile-inference-resolution-r04` @ `dd84dba7d37a2dd00ab8480c7f79ccfd37b7b118`

```text
CURRENT_BLOCKER=STATISTICAL_POSITIVE_ACCEPTANCE_PATH_UNDECIDED
    (no defensible general-domain strong-FWER positive-PASS inference exists at the frozen
     6-month cohort lengths; PROFILE_0_4_DRAFTABLE=NO; Owner research-design gate open)

VIABLE_ROUTES=ROUTE_A (preserve frozen 12/6/6 + strong-FWER; historical positive PASS
             structurally unavailable; IE is the honest result)
             + ROUTE_D (move positive-acceptance evidence to future genuinely-unseen
               Shadow/Forward; the only defensible strong-FWER PASS path)
             + ROUTE_B (change cohort length / new chronology; NEW protocol version +
               Owner research-design gate; new historical data likely required and NOT
               demonstrated sufficient)  [conditional Owner option only]
             + ROUTE_C (restricted admissible domain; parked — no independently-justified
               non-outcome gate currently exists)  [parked]
             ROUTE_E (weaken strong-FWER or outcome-calibrated thresholds) = FORBIDDEN

RECOMMENDED_ROUTE=ROUTE_A_NOW + ROUTE_D_FORWARD
    (keep frozen 12/6/6 as the governed historical exam/diagnostics structure;
     designate future Shadow/Forward as the statistical positive-acceptance path)

RECOMMENDED_REASON=statistical honesty and strong-FWER preserved with zero protocol
    disruption and zero new historical data; the historical cohorts keep their valid
    roles (negative evidence, failure discovery, procedural-integrity exam) without
    pretending to be a general-domain acceptance gate; a defensible strong-FWER PASS
    is only achievable on genuinely-unseen forward data, which is exactly what Shadow
    provides; no outcome leakage and no overfitting risk

OWNER_DECISIONS_REQUIRED=1 PRIMARY (approve A+D) + 1 CONTINGENCY (authorize Route B
    design package) — see §8. All ordinary engineering/statistical implementation
    decisions remain project-brain scope and are NOT Owner questions.

PROTOCOL_VERSION_CHANGE_REQUIRED=NO for recommended A+D (Protocol v1.0 + 12/6/6 stay
    frozen; IE-only is already the evidence-policy default disposition and needs only
    Owner approval for profile-lock intent, not a protocol version bump).
    =YES only if Route B or C is chosen (new protocol version + Owner research-design gate).

NEW_DATA_REQUIRED=NO for recommended A+D. =YES (likely) for Route B.

IMPACT_ON_TIME_TO_SHADOW=NEUTRAL_TO_FAVORABLE. Does not block Shadow; Shadow becomes the
    acceptance engine. Statistical acceptance of any playbook then requires forward
    evidence accumulation AFTER Shadow activation (Shadow itself remains a later,
    separately authorized gate).

CANDIDATE_OUTCOME_USED=NO
```

This document is a single, complete Owner decision-compression package. It makes **no**
production change, locks **no** profile, adopts **nothing**, and unlocks **no**
outcome-bearing access. Its purpose is to reduce the genuinely Owner-level research-design
choice to the smallest set of decisions the Owner must make, and to keep every ordinary
statistical/engineering implementation decision inside project-brain scope.

---

## 0. Baseline and decision basis

### 0.1 Tree

Created fresh from official `origin/main` `e87315d` as
`preoutcome/stat-profile-owner-decision-v01` in an independent worktree.

```text
MAIN_HEAD=e87315dd622689eb165dbe81f1728c868cc06a26
BRANCH=preoutcome/stat-profile-owner-decision-v01
```

### 0.2 Decision inputs read (never candidate outcome)

- `AGENTS.md`, `OWNER_COLLABORATION_CONTRACT.md`, `CURRENT_STATE.md`
- frozen `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- frozen `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- active `docs/research/HUMAN_PLAYBOOK_HISTORICAL_V1_EVIDENCE_POLICY_V1_0.md`
- `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`
- `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADVERSARIAL_REVIEW.md`
- `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_PARALLEL_REVIEW_ADJUDICATION_V0_2.md`
- `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_ADJUDICATION_V0_3.md`
- independent inference-resolution review `parallel/stat-profile-inference-resolution-r04`
  @ `dd84dba7d37a2dd00ab8480c7f79ccfd37b7b118`
  (`HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_REVIEW.md` + its
  reproducibility support script)
- `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE.md` (0.3)
- `docs/reviews/FGH_SEMANTIC_GATE_OWNER_DECISION_PROPOSAL_V0_1.md` (format precedent)

### 0.3 No candidate outcome

No real Human Playbook candidate run, candidate PnL / equity / expectancy / Sharpe /
win-loss / VALIDATION result / historical-final result was inspected or used. No
large-scale re-simulation was performed: the accepted inference-resolution review
(`dd84dba`) was checked for a clear computational error and none was found, so its
findings are used as accepted advisory evidence rather than re-run.

### 0.4 Frozen facts that bound every route

```text
CHRONOLOGY=FROZEN_12_6_6
DEVELOPMENT = 2024-01-01..2024-12-31  (≈242 authoritative trading days / 52 weeks)
VALIDATION  = 2025-01-01..2025-06-30  (≈117 trading days / 27 weeks)
HISTORICAL_FINAL = 2025-07-01..2025-12-31 (≈126 trading days / 27 weeks)
CANONICAL_CORPUS=2024-01-01..2025-12-31 (cu,al,ni,au,ag,rb; 1-minute; accepted)
ESTIMAND=event-weighted per-trade mean theta=E[S_d]/E[C_d] (pinned)
ACCEPTANCE_TARGET=strong per-hypothesis FWER <= 0.05 (Holm over locked wave denominator)
NO_OUTCOME_TUNING=REQUIRED
NO_ARBITRARY_GATES=REQUIRED
INSUFFICIENT_EVIDENCE=frozen legitimate result
SHADOW_FORWARD=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
PROFILE_0_4_DRAFTABLE=NO (with current inference evidence)
```

### 0.5 Accepted blocker (from the accepted review + adjudication)

At D≈117/126 trading days, **no defensible general-domain per-hypothesis inference
exists** that controls strong-FWER ≤ 0.05 across the realistic regime space (strong
serial persistence; left-skewed, realistic trading-PnL score shapes) while preserving the
pinned estimand, reaching Holm-relevant tails (α/M down to 0.0025), and using no
arbitrary gates and no outcome tuning. Investigated families (asymptotic
self-normalization, wild-bootstrap self-normalization, block bootstrap, weekly/grouped,
subsampling, admissible-domain gating) were all falsified or unusable at these lengths.
`INSUFFICIENT_EVIDENCE` is the only honest sign-unresolved result. The problem does **not**
disappear at D=242 (one year) for some regimes (left-skew size ≈0.09). No clear
computational error was found in this evidence, so it is used as-is.

---

## 1. ROUTE A — 保持冻结 12/6/6 + strong-FWER（历史正 PASS 结构性不可得）

### 1.1 内容

- 保持 `12/6/6` 切分、Protocol v1.0、strong-FWER ≤ 0.05、逐交易事件加权估计量全部不变。
- 明确接受：在一般统计适用域下，6 个月历史 cohort 无法提供可辩护的 positive-PASS 推断；
  诚实的 sign-unresolved 结果就是 `INSUFFICIENT_EVIDENCE`。

### 1.2 对项目的意义

1. **没有候选能靠历史 6 个月 cohort 获得一般域统计 PASS。** 这不等于"没有 edge"，而是
   "本 cohort / 本 profile 无法以 strong-FWER 且可辩护的方式解析该 claim"。
2. **历史 cohort 的角色改为**：负向证据 / 失败发现（conservative bound 的 FAIL 方向安全：
   假 FAIL 只是错过机会，不是假接受）、受治理诊断、证据累积、以及"过程完整性考试"
   （防内部调参）。它们**不再承担一般域接受门槛**。
3. **流水线继续推进**：source 提取、SOURCE_ONLY、确定性 operationalization、工程、测试
   全部照常（无需 candidate-outcome 访问）。
4. **"已验证 playbook" 里程碑推迟**到未来真正未见的前向证据（见 Route D）。
5. **研究政策含义**：把 v1 接受设计明确设为"IE-only"是一个研究政策决策；按前序裁决
   （Inference-Resolution Adjudication §5），在 profile lock 前需要 Owner 明确批准——
   这就是本包 Q1 的第一部分。它**不要求**协议版本变更（IE 本就是冻结合法结果）。

### 1.3 评价

| 维度 | 结论 |
|---|---|
| statistical honesty | 高（诚实 IE，不伪造统计保证） |
| overfitting control | 高（零新增自由度、零 outcome 泄漏） |
| time-to-shadow | 中性（不阻塞 Shadow；但历史正接受被推迟到前向路径） |
| need for new data | 无 |
| protocol disruption | 无 |
| future extensibility | 高（稳定的停驻态，未来任何路径都可在此基础上叠加） |

---

## 2. ROUTE B — 改变 validation/final cohort 长度或 chronology（新协议版本 + Owner 研究设计门）

### 2.1 触发条件

任何改变冻结切分 / 冻结协议语义的做法都会触发：**新 frozen protocol 版本 + 正常 Owner
research-design gate + 独立对抗审查**（Protocol v1.0 §19、Chronological Split §4、
Historical-v1 Evidence Policy §6）。

### 2.2 是否需要新增历史年份数据

- 现有 canonical corpus 固定为 `2024-01-01..2025-12-31`。**任何把验证/最终窗口延伸到
  2025-12-31 之外（向前或向后）的方案都需要新增历史数据获取**。
- 新增获取在当前治理下并不轻松：
  - `E-06`：exchange 级 schedule / current-rate backfill 现状为
    `CURRENT_RATE_BACKFILL=FORBIDDEN`、`EXCHANGE_LEVEL_SCHEDULE=INSUFFICIENT_EVIDENCE`；
  - `E-07`：TqSdk 历史 main 映射 `LOGIN_REQUIRED`，项目 fail-closed，禁止自行替代
    （`FAIL_CLOSED_PREREQUISITE`）；
  - `LIMIT-001`：历史涨跌停元数据缺失（数据治理缺口）。
- **仅在现有 2024–2025 corpus 内部重新切分**不产生"新数据"，但（a）仍属改变冻结切分，
  需要新协议版本；（b）**未证明充分**：接受证据显示 D=242（约一年）在某些 regime 下
  size 仍 ≈0.09，单纯把 6 个月加到 12 个月**不能治愈** inference 有效性问题；
  （c）要真正修复持久性/偏度问题通常需要多年数据，而多年数据在 E-06/E-07/LIMIT-001
  未解决前无法可靠获取。

### 2.3 会不会破坏当前 2024–2025 corpus 设计

- 改变切分会改变 cohort 语义与身份绑定。**同一 corpus 已作为 2024-2025 完整范围被处置
  （确定性 operationalization、引擎 sanity、source 工作）**；把它外层年份重新命名为
  "validation/final" 会带来"已被当作开发语境处置过的数据再次以 unseen 身份出场"的
  风险——unseen integrity 必须以清晰的"首次接触时间戳 + 从未被设计期检视"来论证，
  而当前 corpus 不满足这种干净的未见叙事。
- 结论：Route B 是**合法但高成本、未证明充分**的 Owner 选项；只有 Owner 明确想要一条
  历史接受路径、且接受新数据获取治理负担时才有意义。

### 2.4 评价

| 维度 | 结论 |
|---|---|
| statistical honesty | 中（诚实目标，但被接受证据质疑：单纯加长不治愈） |
| overfitting control | 中（重新切分/新数据引入新的设计选择自由度；best-of 变体风险） |
| time-to-shadow | 推迟（新协议 + 新数据 + 新构建周期） |
| need for new data | 有（大概率；且受 E-06/E-07/LIMIT-001 阻断） |
| protocol disruption | 高（新协议版本 + Owner research-design gate + 独立对抗审查） |
| future extensibility | 中（扩展历史，但治理/获取成本高且不确定） |
| no outcome leakage | 需严格 unseen 设计；现有 corpus 已处置过，风险高于 Route A/D |

---

## 3. ROUTE C — 受限统计适用域（restricted admissible domain）

### 3.1 合法条件

只有能建立 **non-outcome、non-arbitrary、pre-registered、independently justified** 的
domain gate（适用域门）才合法。

### 3.2 现在还缺什么证据

- 独立审查（`dd84dba` §8.1）已明确：**目前不存在**这样的门。
  - 对 lag-1 自相关 ρ̂ 或偏度的 cutoff **没有独立方法学正当性**——没有定理声明
    "SN 有限样本 pivotal 近似在 ρ≤c、D=117 时充分"；size 膨胀是谱形/偏度的平滑函数，
    不是任何可辩护 c 处的阶跃。
  - 从合成 operating-characteristic 表挑 c = 在合成 fixture 上调参（被禁止）。
  - 用观测 score 的估计 DGP 仿真来"认证"域 = **循环认证**且 outcome-shaped。
- 不能事后用 rho/skew 等 outcome diagnostics 决定是否适用——这正是被禁止的循环。

### 3.3 结论

Route C 目前 **parked（停驻）**。它缺的不是工程实现，而是"独立、pre-registered 的域
有效性证明"这类研究问题。除非未来出现一个有独立理论依据的门（例如一个新定理或一个
在给定域上能证明 size 控制的上界），否则不能作为可选路线包装。若未来采用并改变接受
语义，则同样需要新协议版本。

### 3.4 评价

| 维度 | 结论 |
|---|---|
| statistical honesty | 未建立（门无独立论证，循环风险） |
| overfitting control | 中（循环认证风险） |
| time-to-shadow | 中性（parked） |
| need for new data | 无（但需要研究证明） |
| protocol disruption | 中（若改变接受语义需新协议版本） |
| future extensibility | 低（目前 parked） |
| no outcome leakage | 高（若门真为 pre-registered） |

---

## 4. ROUTE D — 把最强正证据移到未来真正前向 Shadow/Forward

### 4.1 历史各 cohort 仍能承担的角色

```text
DEVELOPMENT:
  实现调试、预注册探索、确定性 operationalization 验证、
  非 outcome 的信号/事件频率测量（仅用于设计 sufficiency 程序）。
  不能产生接受。

VALIDATION:
  受保护的考试 cohort，用于失败发现与负向证据；
  conservative bound 的 FAIL 方向安全（假 FAIL=错过机会，不是假接受）；
  不能产生一般域 PASS（无 size-valid 推断）。

HISTORICAL_FINAL:
  一次性受保护考试 cohort，用于"过程完整性"考试（防内部调参）；
  与 VALIDATION 相同的推断/功效限制；不能产生一般域 PASS。
```

### 4.2 未来 Shadow/Forward 如何成为更强的 genuinely-unseen 证据

- 冻结协议与证据政策明确：`PROJECT_GOVERNED_HISTORICAL_HOLDOUT != PROSPECTIVE_GENUINELY_UNSEEN_DATA`。
- Shadow/Forward 产生的是**设计时真正未见**的前向 outcome——这是唯一能干净满足
  "strong-FWER ≤ 0.05、无 outcome 泄漏、无任意门"的接受证据类别（证据政策 §6 候选类别之首）。
- 前向数据天然提高功效与推断充分性，且不改变历史 12/6/6 的任何语义。

### 4.3 注意

- **Shadow 当前仍未授权**（`PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED`）。本包**不激活**
  Shadow；只把"Shadow 作为统计接受路径"列为 Owner 决策，并允许后续在**独立 Shadow gate**
  下准备 Shadow 设计/风险包。
- 代价：任何 playbook 的统计接受都要求 Shadow 启动后**前向证据累积时间**（wall-clock）。
  这是获得可辩护 PASS 所支付的真实时间成本。

### 4.4 评价

| 维度 | 结论 |
|---|---|
| statistical honesty | 高（真正未见，最强证据完整性） |
| overfitting control | 高（设计期无法看到前向结果） |
| time-to-shadow | 中性偏优（Shadow 成为接受引擎而非事后附加；接受仍需前向累积） |
| need for new data | 无（使用未来自然产生的前向数据） |
| protocol disruption | 无（历史 12/6/6 与协议不变；Shadow 为独立后续授权） |
| future extensibility | 高（前向数据可复用、可扩展，可叠加更长窗口） |
| no outcome leakage | 高（真正未见） |

---

## 5. ROUTE E — 弱化 strong-FWER 或 outcome-calibrated thresholds（禁止）

- **不是普通可选路线。** 项目已多次明确裁决：`STRONG_FWER_ACCEPTANCE_TARGET=UNCHANGED`、
  "Weakening the project error-rate target is REJECTED"、`no outcome-calibrated thresholds`。
- 用 candidate outcome 校准阈值违反"no outcome tuning"，且按 Protocol v1.0 §8，被校准的
  cohort 将**永久 burned/exposed**，不能再作为同 lineage 下的干净证据。
- 结论：`ROUTE_E=FORBIDDEN`。不作为可选路线包装，不提供给 Owner 作为选项。

---

## 6. 路线评价总矩阵

| 评价标准 | A 保持 12/6/6 | B 改窗口/新数据 | C 受限域 | D Shadow/Forward | E 弱化/校准 |
|---|:---:|:---:|:---:|:---:|:---:|
| statistical honesty | 高 | 中 | 未建立 | 高 | 违反 |
| overfitting control | 高 | 中 | 中 | 高 | 违反 |
| time-to-shadow | 中性 | 推迟 | 中性(parked) | 中性偏优 | n/a |
| need for new historical data | 无 | 有(大概率) | 无 | 无 | n/a |
| protocol disruption | 无 | 高 | 中 | 无 | 违反 |
| future extensibility | 高 | 中 | 低 | 高 | n/a |
| no outcome leakage | 高 | 需严格 unseen | 高(若 pre-registered) | 高 | 违反 |

---

## 7. 项目脑推荐（PROJECT-BRAIN RECOMMENDATION）

```text
RECOMMENDED_ROUTE=ROUTE_A_NOW + ROUTE_D_FORWARD
```

- **立即处置（Route A）**：保留冻结 12/6/6 作为受治理的历史考试/诊断结构；历史 cohort
  不承担一般域正 PASS 门槛；v1 接受设计明确为 IE-only disposition（需要 Owner 批准
  这一研究政策意图，协议版本不变）。
- **接受路径（Route D）**：把可辩护的 strong-FWER 正接受证据移到未来真正未见的前向
  Shadow/Forward 数据；这是在不弱化目标、不发明任意门、无 outcome 泄漏前提下，唯一
  可辩护的接受路径。

**不要单纯选"最快"。** 选择标准权重：统计诚实与无 outcome 泄漏为**硬约束**（不可交易），
过拟合控制与协议扰动次之，time-to-shadow 与新增数据需求再次。A+D 在所有硬约束上得分
最高，且不阻塞 Shadow、不需要新历史数据、不需要协议版本变更——它是当前证据下唯一
"诚实且可辩护"的组合，而非权宜之计。

---

## 8. Owner 决策最小化（≤ 2 个问题）

统计/工程实现问题（power-envelope 数值、sufficiency 程序、block/bootstrap 细节、决策
评估器、机器可读 profile 结构、counting taxonomy 实现等）全部由项目脑决定，**不**甩给
Owner。

### Q1（唯一必要决策）

```text
DECISION_ID=STAT-PROFILE-ACCEPTANCE-PATH
QUESTION=采纳推荐路线 A+D？
  (1) 接受历史 v1 为 IE-only disposition：冻结 12/6/6 保留为受治理的历史考试/诊断
      结构，不作为一般域正 PASS 依据；
  (2) 指定未来 Shadow/Forward 前向数据为统计正接受路径（授权后续在独立 Shadow gate
      下准备 Shadow 设计/风险包；本包不激活 Shadow）。
OPTION_A=APPROVE（推荐）——按 A+D 执行
OPTION_B=REJECT——走备用 Q2（Route B 研究设计包）
PROJECT_BRAIN_RECOMMENDATION=OPTION_A
```

### Q2（仅当 Owner 拒绝 Q1 时的备用决策）

```text
DECISION_ID=STAT-PROFILE-ROUTE-B-DESIGN-PACKAGE
QUESTION=是否授权一个研究设计包探索 Route B（更长/新数据窗口或新协议版本）？
  前提：接受需要新 frozen protocol 版本 + Owner research-design gate + 独立对抗审查；
  接受需要新增历史数据（大概率，且受 E-06/E-07/LIMIT-001 阻断）；
  接受"单纯加长到一年不治愈 inference 有效性"这一现有证据风险。
OPTION_A=NOT_NOW（推荐）——维持 A+D
OPTION_B=YES——授权 Route B 设计包（不即时批准任何具体窗口/阈值/模式）
```

---

## 9. 决策后的授权状态（本包自身不改变任何状态）

决策生效前（当前状态不变）：

```text
AUTHORIZED:
  source 发现/出处；SOURCE_ONLY 真实 claim 提取；
  确定性非 outcome operationalization/测试；非候选工程与证据工作；
  统计 review 证据的只读/可复现检查。
NOT_AUTHORIZED:
  锁定 Common Statistical Profile v1 为 IE-only（需 Owner 批准）；
  起草带虚构推断语义的 0.4；candidate PnL/equity/expectancy/Sharpe/win-loss 检视；
  VALIDATION / historical-final 访问；改变 12/6/6 或冻结协议语义；
  Shadow/Forward 自动化交易；真实资金/经纪商执行。
```

---

## 10. 最终 Owner 批准块（PROPOSAL ONLY — NOT adopted）

Owner 可原样复制以下块。它**不由本文档批准**；每行前缀
`PROPOSAL_ONLY_NOT_ADOPTED` 记录推荐选项，Owner 必须决策后才能成为 adoption。

```text
PROPOSAL_ONLY_NOT_ADOPTED=YES

# 统计接受路径（推荐提案）
APPROVE_STAT_PROFILE_ACCEPTANCE_PATH=OPTION_A
  (1) 历史 v1 = IE-only disposition：冻结 12/6/6 保留为受治理历史考试/诊断结构，
      不作为一般域正 PASS 依据；
  (2) 指定未来 Shadow/Forward 前向数据为统计正接受路径；
      授权后续在独立 Shadow gate 下准备 Shadow 设计/风险包（本包不激活 Shadow）。
APPROVE_ROUTE_B_DESIGN_PACKAGE=NOT_NOW（推荐；若拒绝 Q1 则改选 YES）
```

任何一行 Owner 不批准，对应 gate 保持开启，并继续阻止 Common Statistical Profile v1
在一般域上的统计正接受。本文档不冻结任何决定；只有 Owner 能把提案变成 adoption。

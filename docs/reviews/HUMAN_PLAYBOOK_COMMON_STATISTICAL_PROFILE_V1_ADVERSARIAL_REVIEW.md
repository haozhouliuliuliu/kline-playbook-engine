# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADVERSARIAL_REVIEW

> Reviewer role: **INDEPENDENT ADVERSARIAL STATISTICAL REVIEWER** (parallel audit line)
> Branch: `parallel/stat-profile-review`
> Date: 2026-08-19
> Status: `ADVERSARIAL_REVIEW_COMPLETE / ADVISORY_ONLY / CANDIDATE_NOT_LOCKED`
> Reviewed package: `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md` (commit `6ef668f`)
> Companion evidence read: `docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_DESIGN_EVIDENCE.md`
> Capability audit read read-only: `git show origin/parallel/stat-engine-audit:docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md`
> Authority docs read: `AGENTS.md`, `00_READ_FIRST.md`, `OWNER_COLLABORATION_CONTRACT.md`, `ARCHITECTURE_BASELINE.md`, `RESEARCH_DIRECTION.md`, `CURRENT_STATE.md`, `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`, `HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`, `HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`, `HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`, `HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md` (authority index).
> Code read: `src/research_firewall.py`, `src/validation_runner.py`, `src/portfolio_semantics.py`.

## Independence attestation

- This review was formed **without** reading `ENGINE_COMPATIBILITY_CROSSWALK` (the other parallel audit line). No such file exists in this worktree and it was not consulted.
- The candidate was **not modified**. Frozen Protocol v1.0, the 12/6/6 chronology, and the Selection Firewall requirements were **not modified**.
- No real Human Playbook was run, no candidate PnL / equity / expectancy / Sharpe / win-loss inspected, VALIDATION and HISTORICAL FINAL were not opened, no statistical evaluator was implemented, no real playbook was selected.
- All numeric arguments below are arithmetic on pre-registered formulas and the canonical trading calendar (non-outcome metadata), consistent with the design evidence's own method.

---

## 执行摘要（中文）

审查结论：**GO_WITH_REQUIRED_CHANGES**。

候选的方向正确：预注册、确定性、全族统一、search-freedom 单调、INSUFFICIENT_EVIDENCE 作为冻结合法结果、避免 Sharpe/参数挖掘/FDR 等经典陷阱、用 trade 级实现回避了引擎缺失的 portfolio-day 序列。但**当前形态不能锁定**，存在 3 个 CRITICAL：

1. **没有功效分析，门槛本身检测不到自己的经济地板**。用正态近似算出的“80% 功效最小可检测单笔 edge”（N=60、σ=30bp 时约 9.6bp；σ=20bp 约 6.4bp）是 2bp 经济地板的 3–5 倍；加上 Holm 分母和 2× 成本压力后，6 个月 VALIDATION 实际只能接受“极强、高频、低波动”的 playbook。这把“严格验证”变成了“几乎必然 INSUFFICIENT_EVIDENCE/FAIL”的空转装置，并把 HUMAN_PLAYBOOK_FIRST 真正研究的“人类频率、稀疏”的 playbook 系统性排除（协议允许稀疏排除，但阈值没有绑定任何可检测效应目标，无法判断这种保守是“正确”还是“空转”）。
2. **ESS = N / max(1, 2H−1) 是未经证明的启发式，且内嵌了一个与候选自述矛盾的隐式自相关模型**。在“一周期收益 IID、H 日重叠收益”这一最自然的精确模型下，均值方差膨胀因子是 H（ESS=N/H），而 2H−1 对应的是 ρ=(H−1)/H 的 AR(1) 近似。公式方向保守（更严），但被当作“无需估计自相关函数的确定性转换”是假精确，且直接决定 S7 生死。
3. **主 estimand 尚未完整定义**：partial close、pyramiding/add-to-position、forced liquidation 的 round-trip 语义未定；跨周持仓全部归到 exit week，破坏了 block bootstrap 对多周持仓依赖的保持（仅在 L≥持仓时部分缓解）。这些选择会实质改变 r_t、H、block 归属，属于统计设计层面不完整，不能留给工程 delta。

其余 HIGH 包括：60/30/8/30/50%/75%/25% 全是无理论的工程启发式且与候选自己“30 不够”的论证自相矛盾；2× 成本压力对边际 playbook 生死攸关但任意；缺少“时间窗级 PnL 集中度”检查；LIMIT-001 数据缺口没有定义决策表结果；多重比较计数规则既可能过罚（nuisance/相关网格）又鼓励少报；Romano-Wolf 被错误描述为“只为 argmax”。

**本审查未冻结任何内容，未修改 candidate，未修改 Protocol v1.0。** 所有必需修改都落在 profile 自身的数字/定义/方法上（profile 尚未冻结，允许在 lock 前修改），**不触碰任何冻结语义**，因此候选可以在不改 Protocol v1.0 的前提下修正后锁定。

---

## 1. REVIEW_VERDICT

```text
REVIEW_VERDICT = GO_WITH_REQUIRED_CHANGES
```

理由：

- 方向（确定性、预注册、全族统一、fail-closed、INSUFFICIENT_EVIDENCE、trade 级 estimand 避开缺失的 portfolio-day 序列）在对抗审查后仍然成立；没有发现需要 NO_GO 的冻结语义冲突。
- 但存在 3 个 CRITICAL（C-1 功效/假精确、C-2 ESS 公式、C-3 estimand 定义不完整）和 6 个 HIGH。这些不是“换个数字更好看”，而是会实质改变接受行为或让统计声明无法辩护的缺陷，必须在 lock 前修复。
- 全部 CRITICAL/HIGH 修复都在 profile 自身的可改范围内（profile 是 CANDIDATE_NOT_LOCKED，Protocol v1.0 明确允许在首个 outcome 前设计/审查/修改 profile），因此**可以在不改变冻结 Protocol v1.0 / 12/6/6 的前提下修正后锁定**。

---

## 2. CRITICAL（不修则不能锁定 profile）

### C-1 — 没有功效分析；门槛检测不到自己的经济地板；6 个月 cohort 的“严格验证”可能空转

攻击目标：§6/§7/§10 的组合（ESS、week-block bootstrap、one-sided α=0.05、MIN_ECONOMIC_EDGE=2bp、Holm、2× stress）。

**量化（正态近似，仅示意；bootstrap 同量级）：**

```text
one-sided α=0.05、power=0.80 的最小可检测单笔 edge（bp，H=1 即 ESS=N）：

N=60   σ=10bp: 显著需 2.12  80%功效需 3.21
N=60   σ=20bp: 显著需 4.25  80%功效需 6.42
N=60   σ=30bp: 显著需 6.37  80%功效需 9.63
N=90   σ=30bp: 显著需 5.20  80%功效需 7.86
N=150  σ=30bp: 显著需 4.03  80%功效需 6.09
N=242  σ=30bp: 显著需 3.17  80%功效需 4.80
```

- 对 N=60、σ=20–30bp（日内单笔收益的典型离散度），80% 功效需要真实 edge 约 6.4–9.6bp——是 2bp 经济地板的 3–5 倍。也就是说 **MIN_ECONOMIC_EDGE=2bp 是一个死条款**：在现实波动下没有任何现实 playbook 能“显著”到触发这个地板，真正起作用的门槛是显著性本身，而显著性要求一个不切实际的大 edge。
- 加上 Holm（wave 分母 M 会进一步缩 α）和 2× cost stress（再吃掉 1bp+），可接受的 edge 更高。**结论：6 个月 VALIDATION 下，profile 现实上只能接受“极强 edge + 高频率 + 低波动”的 playbook；对一切现实候选返回 INSUFFICIENT_EVIDENCE 或 FAIL。**
- 这不是“保守得正确”，而是“没有可检测效应目标的严格=空转”：没有 power envelope，读者无法区分“没有 edge”与“这个 gate 永远不可能通过”。这正好落在任务要求攻击的“过度保守 / 假精确 / 把统计上无法证明的任务包装成严格验证”上。

**要求：** 在 profile 文档中发布 **power envelope**（预注册、无 outcome 即可计算：给定 N、ESS、σ 的 80% 功效最小可检测 edge 表），并明确 `INSUFFICIENT_EVIDENCE` 的语义是“本 cohort 无法检测本 profile 要求的效应量”，而不是“没有 edge”。同时把 MIN_ECONOMIC_EDGE 与经济意义论证分离（地板是“经济意义下限”，功效是“能否检测到它”——两者必须都成立且被明确陈述）。

### C-2 — ESS = N / max(1, 2H−1) 是未经证明的启发式，且内嵌一个自相矛盾的隐式自相关模型

攻击目标：§7 S7、§8.2、§18 item 1。

- **模型依赖，不是确定性事实。** 设一周期收益 IID、H 日重叠收益 R_t = y_t+…+y_{t+H−1}。则 Var(R_t)=Hσ²，Cov(R_t,R_{t+k})=(H−k)σ²，均值方差 = H²σ²/N。把它等同为 N/H 个“独立 H 日观测”的均值方差（=Hσ²/(N/H)=H²σ²/N），得到 **ESS = N/H**。而 2H−1 对应的是 AR(1) 近似 ρ=(H−1)/H 的均值方差膨胀因子 (1+ρ)/(1−ρ)=2H−1。两个模型给出 H 与 2H−1，差近 2 倍。
- 候选声称“无需估计自相关函数”的确定性转换，实际内嵌了一个**未声明的 AR(1) 自相关模型**（且它比精确的重叠 IID 模型更保守）。自相关结构未知时，任何固定因子都是模型选择；把它当作“有效样本量”精确到 1 位小数是**假精确**。
- 2H−1 直接决定 S7：H=2 → ESS=N/3，H=3 → N/5，H=5 → N/9。N=150、H=3 时 ESS=30 恰好卡线；N=240、H=5 时 ESS≈26.7 → S7 FAIL。**一个中位持仓 5 天的 playbook 要在 117 个交易日里完成 ≥240 笔成交才能过 S7**——对 HUMAN_PLAYBOOK_FIRST 的对象来说这是结构性不可能。
- 附带问题：H 用**中位**持仓（对长尾持仓不稳健）、以**交易日**计（受 TD-001 权威选择影响）、未定义 partial-close 时 H 怎么算（入场到最后平仓？还是加权腿？）。

**要求：** 移除 ESS 作为确定性 sufficiency 门槛，让 week-block bootstrap 承担依赖感知的 uncertainty（重叠已由 block 结构处理），或用有推导的保守替代（如 N/H 并注明模型假设），或改为“bootstrap 方差比”作为结构诊断。**不能再以 2H−1 作为精确 ESS。**

### C-3 — 主 estimand 未完整定义：partial close / pyramiding / forced liquidation / 跨周归属

攻击目标：§4 全部 + §6 block 归属。

- **partial close**：候选说“一个 round trip = 开仓并完全平仓，gross PnL = 各次平仓腿 realized 之和”，但 holding horizon H 与 week 归属用什么时间点未定义（最终平仓日？入场到最后平仓的加权？）。一个 week1 开、week3 平的持仓，其全部 PnL 记到 exit week 的 block 里——而它真实依赖 week1–3 的价格路径。block bootstrap 只有在 block 长度 ≥ 该持仓跨度时才能部分保留这种依赖，且用 **median**（不是 max/90 分位）会让 ≥50% 的持仓超出 block 覆盖（候选 §17.8 自己承认这是残余风险，但用 ESS 来“缓解”——而 ESS 本身是 C-2 的假精确）。
- **pyramiding / add-to-position**：同一个 position_id 下的加仓算一个 trade（entry notional 求和）还是多个？加仓后 H 怎么算？候选只说了“sum over legs that opened”，没有定义 identity 边界（`position_id` vs `position_request_id`）——这正是引擎的模糊区。
- **forced liquidation**：R1 说 forced-liquidation/breach>0 → FAIL，但 forced liquidation 是否计入 round-trip 样本、其 realized PnL 是否进 r_t，未定义。（R1 已 FAIL，样本里有没有它不影响结果，但定义必须明确。）
- 这些不是纯工程问题：**它们改变 r_t、H、block 归属，即改变统计量本身**。capability audit 确认引擎“trade boundaries are inferable from the transition stream, not materialized”——因此候选把 round-trip 定义留给工程 delta 是在把统计设计委托给实现者。

**要求：** 在 profile 文档中（不依赖任何工程实现）写死 round-trip 语义：partial-close 的 H/week 归属规则、pyramiding 的 trade 边界、forced liquidation 的样本规则、跨周持仓的 block 归属（建议按 exit week 归属并强制 L 覆盖持仓 90 分位，或采用“持仓期所有周共享归属”并在 profile 层固定）。这些必须在 lock 前定义，不能留到 evaluator 实现时再定。

---

## 3. HIGH（应在 lock 前解决）

### H-1 — 60/30/8/30/50%/75%/25% 全是工程启发式，且与候选自己的“30 不够”论证自相矛盾

- 每个数字都无理论依据（候选承认是 “v1 pre-registered choices”）：60、30、8 是频率/广度启发；ESS≥30 是 CLT 启发——**而候选 §18.1 刚攻击过“30 trades rule of thumb”**，然后自己用 ESS≥30。即便 ESS 是“有效独立事件”，30 个独立事件对 one-sided 检验 + 地板 + Holm + 2× stress 的功效也远不够（见 C-1）。
- S5（day≤50%）在 N=60、D=30 边界上几乎冗余：30 个不同日 + 其余 30 笔集中在一天 → 31/60=51.7%>50% → S5 实际把 D 推到 ≥31（一致但多一个 knob）。
- 没有 power 目标的数字组合不可辩护地冻结。**要求：** 要么用预注册功效分析校准（让门槛达到“能检测到自身地板”），要么简化为最小耦合集合（见 §12 RECOMMENDED_SIMPLIFIED_V1），并明确哪些是“engineering heuristic、可被替代”哪些是“power-based、不可替代”。

### H-2 — 2× cost stress 对边际 playbook 生死攸关但任意；fee 与 slippage 风险结构被混为一谈

- 任意固定倍数=治理选择（候选承认），但 2× 是“**总成本**乘 2”：fee（近确定性、可精确到 1 位小数）与 slippage（随机、依赖流动性/波动/手数）风险结构完全不同，乘同一个数不合理。
- 关键攻击：**一个真实 edge 3bp、成本 1bp 的 playbook，base net=2bp、stress net=1bp；2× 直接决定它生或死**。倍数改成 1.5×/3× 都会翻转一批边际 playbook。这使接受与否被一个未绑定任何测量依据的数字主导。
- forced liquidation 成本是尾事件，不属于稳态成本流，不应被 2× 覆盖。
- **要求：** 固定 2× 是最简单的 v1（可保留），但必须：(a) 要求 base 成本模型本身保守（base 乐观则 2× 仍乐观）；(b) 增加**强制报告的 cost-sensitivity 诊断**（1.5×/2×/3× 下的结论带），不让接受变成一个数字悬崖；(c) 文档写明倍数是治理常数而非测量。tick-based slippage stress（加 N ticks）是更经济的替代，但不比 2× 简单，列为 v1.1 候选。

### H-3 — 缺少“时间窗级 PnL 集中度”：一个短有利窗口撑起全部 edge 未被捕获

- day/week 集中度按**笔数**定义（结构、非 outcome，严格定义——这是优点），但**一个周末/两周的有利 regime 贡献 80% PnL** 这种情况，只要笔数分散就不被 S5/S6 捕获。
- R2（单笔 |r_t|≤40%Σ|r_t|）只覆盖单笔极端赢家，不覆盖“单个时间窗”集中。候选威胁模型列了 “one-lucky-trade edge”，但只在单笔层处理。
- **要求：** 增加 **outcome-based 时间窗 PnL 集中度 robust 检查**（如“最大单周 |净PnL| ≤ 预注册分数 × Σ|PnL|”，阈值在 lock 前定，不按 outcome 调），放在 risk 步而非 sufficiency 步。这是对 C-1/H-1 的补充：避免“一个窗口的运气被 6 个月 gate 包装成 edge”。

### H-4 — LIMIT-001 数据缺口没有定义决策表结果

- capability audit：真实 corpus 上 price-limit-bound 合约的 confirmatory PnL 目前 **fail-closed 被 block**（缺 governed 历史限价事实）。候选 §10 决策表只有 PASS/FAIL/INSUFFICIENT_EVIDENCE/INTEGRITY_FAIL，**没有 DATA_BLOCKED 状态**。
- 如果 VALIDATION 因缺限价事实跑不出来，该 hypothesis 应得什么结果？按现状可能被误判为 FAIL 或无法归类。
- **要求：** 增加 `DATA_BLOCKED / INSUFFICIENT_EVIDENCE (data-gap)` 结果，并规定 LIMIT-001/TD-002/TD-001 的激活条件在进入 VALIDATION 前必须满足（Protocol v1.0 §15 已要求，profile 必须把它变成可执行结果）。

### H-5 — 多重比较计数规则既可能过罚又可能被少报钻空子

- 现状：`每个 outcome-tested branch = 1`，FAIL/INSUFFICIENT 永留分母。优点是可审计、单调。缺点：
  - **过罚**：同一机制下 3 instrument × 2 timeframe × 5 parameter 点 = 30 个“hypothesis”，高度相关，Holm 下几乎全灭；若这些只是 nuisance implementation 或同一搜索事件内的网格点，全算独立假设是过度惩罚。
  - **少报**：反方向，把整个网格声明为“一个 hypothesis”会洗掉 search freedom（“网格内挑最佳”就是 data snooping）。Protocol §7 要求“independently falsifiable operationalized hypotheses”为计数单位，但没有给“搜索事件 vs 分支 vs nuisance 实现”的 taxonomy。
- **要求（可审计、难钻空子的 counting rule，见 §9 MULTIPLICITY_VERDICT）**：明确搜索事件（pre-registered 网格/范围 = 1 个分母单位，但网格内“选中点”必须先声明、best-of 必须在 validation/holdout 单独确认或做 RC 校正）、真分支（不同机制解释 = +1）、scope 扩展（超出 claim 的 instrument/timeframe = +1）、nuisance 实现（须证明 outcome 中性，否则视为搜索事件）。全部 outcome-informed 的事后改动 = 新 wave。

### H-6 — Romano-Wolf 被错误描述为“只为 argmax”；相关分支下 Holm 可能无谓地弱

- 候选 §9/§16 说 RW “only for best-of reporting, v1 forbids argmax so not needed”——**这是对 RW 的误解**。Romano-Wolf stepdown 是“对一组预注册假设做联合推断、在任意相关下控制 FWER”的标准方法，正是 whole-wave 的问题；它并不是只有“report the best”时才需要。White Reality Check / SPA 才是“best of many vs benchmark”那一族。
- 对高度相关的 wave（同一 family 多个分支），Holm 正确但可能过保守 → 与 H-5 过罚叠加，接受概率趋零。
- **要求：** 修正对 RW 的描述；明确定义错误率目标（见 §9）；选择 (a) 相关分支族内**预合并**减少 M，或 (b) 把 RW stepdown（共享 week-block 重采样下同时计算全部 M 个检验统计量）作为 v1 或明确的 v1.1 升级。**不自动上复杂方案**：v1 保留 Holm，但必须给出“何时升级 RW”的可判定条件（如 wave 内预计相关分支数 > 阈值）。

---

## 4. MEDIUM（应在 lock 前明确，不阻塞）

- **M-1 (E, one-sided test)**：one-sided 对“接受正 edge 的 playbook”这一决策是合理的，KEEP。但必须(a)文档写明 one-sided 是决策导向选择，不是“无 downside 证据”；(b)把 two-sided CI 作为强制诊断报告；(c)downside 由 R1/R2/R3 承担，测试本身不承担——已成立但要显式陈述。
- **M-2 (D, circular wrap)**：6 个月 cohort 的 circular wrap 把 cohort 首尾（真实相隔约 6 个月，且跨越 12/6/6 的 VALIDATION→FINAL 边界）连成相邻，是建模伪影。文档必须承认该伪影并量化影响（或用边界感知 block）。
- **M-3 (D, B=10000 假精确)**：W_active=8（最小允许）时 distinct 重采样数据集只有 6435 < 10000（L=1）；p 值分辨率被夸大。B 应设为 min(10000, 依赖 distinct 空间) 或文档说明分辨率。
- **M-4 (D, median H 用于 block 长度)**：median 对长尾持仓不稳健，≥50% 持仓的跨度 > L；要求用 max 或 90 分位持仓决定 L，并写死“L 必须覆盖持有跨度”的规则。
- **M-5 (J, 无全局 max drawdown)**：候选不做全局统一 max DD 是**正确避免假精确**（不同持仓周期的 DD 语义不同；家庭专属预注册 cap 是正确位置）。但应增加**强制风险诊断块**（max DD、最差周、最大单笔亏损、峰值杠杆、margin 近失守次数）作为报告而非 gate。
- **M-6 (L, final-holdout 复用同表)**：FINAL 也是 27 周、同一张（功效弱）表；C-1 的 power envelope 必须同样适用于 FINAL；且“final p-values corrected against the same wave denominator”需精确（同一 M？还是每个 cohort 各自 M？）。

---

## 5. OVER_GOVERNANCE

反向攻击：规则是否太多 / 重复防同一风险 / 假精确 / 可否删。

- **O-1 — sufficiency knob 过多且部分冗余。** S1..S8 有 8 个互锁阈值。S5 在 N=60/D=30 边界几乎冗余（见 H-1）；S7 ESS 与 bootstrap 对测试重复处理重叠（只作为 pre-gate 才有意义，而 2H−1 又是假精确）；S8 open_ratio 更像数据质量检查而非 sufficiency。可删到最小集合（见 §12）。
- **O-2 — B=10000 是装饰性数字。** 见 M-3；1000 在 W≥12 时已足够，W=8 时 10000 也达不到 6435 以外的分辨率。
- **O-3 — 任意常数堆叠。** 60/30/8/30/50%/75%/25%/2bp/2×/40%/4/0.05/10000 有 13 个自由 knob，每个都“看起来精确”，但没有一个绑定测量或功效目标。建议收敛到单一 power-based 校准源。
- **O-4 — 结构性结论。** 候选 §19 拒绝重型方法（Bayesian/ABL/HAC/PBO）是对的；残余 over-governance 不在方法复杂度，而在**互锁阈值数量**。目标不是“越严格越好”；修复方向是减少门槛并把剩余门槛绑定功效目标。

---

## 6. PRIMARY_ESTIMAND_VERDICT

**VERDICT = MODIFY（核心可保留，但定义不完整，必须修完才能锁）**

逐条攻击（A1–A9）：

1. **为什么按 trade 等权而非时间/资本 exposure？** 候选未给出论证，只说“notional-normalized，pooling meaningful”。等权 per-trade 测的是“给定出手时，决策质量”；它**不回答“这个 playbook 值不值得配置资本”**（资本生产力、turnover、闲置时间都被排除）。作为 common acceptance 的“经济 edge”，这是可辩护的**决策质量代理**，但必须显式声明它不测量资本层面的经济性，并作为诊断报告 capital productivity。KEEP 但限定解释。
2. **高频小 trade 是否获得更多权重？** 是——等权意味着高频 playbook 贡献更多观测 → 更多统计功效。这不是偏差（样本就是决策序列），但它让 sufficiency gate 天然偏向高频，配合 C-1 使“可接受”几乎只可能是高频强 edge。要显式承认这一偏向。
3. **大仓位 vs 小仓位等权是否合理？** r_t 已按 entry notional 归一化，量级可比；但固定成本在小仓位上更重（r_t 已含 cost，公平），且 sizing 被排除意味着“会用 20% 资本”和“会用 2% 资本”的 playbook 被同权。作为决策质量代理合理；作为资本回报代理不合理。KEEP，声明限制。
4. **partial close 怎么定义 round-trip？** 未完整定义（见 C-3）。必须在 profile 层写死：一个 position 从开仓到完全平仓 = 一个 trade，gross=各平仓腿 realized 之和，H 与 week 归属用明确规则（建议：H=入场到最终平仓的交易日数；week=exit trading day 的 ISO week；partial-close 腿不单独成 trade）。
5. **pyramiding/add-to-position 怎么算？** 未定义。建议：同一 position_id 生命周期内的加仓 = 同一 trade，entry notional=所有开仓腿求和，H 取加权；重新开仓（完全平掉再开）= 新 trade。身份边界用引擎 `position_id`（不是 `position_request_id`）。
6. **forced liquidation 怎么算？** 未定义 + R1 已 FAIL。建议：forced liquidation 计入 round-trip 样本（其 realized PnL 进 r_t），同时触发 R1 FAIL；文档写明样本含它、结果由 R1 决定。
7. **长期持仓跨多个 regime 是否隐藏时间风险？** 是。单笔 r_t 把跨 regime 的 20 日持仓压缩成一个观测，无法分解 regime 贡献。对“applicability”类声明是硬限制，必须记录为局限，并用 H-3 的时间窗集中度检查补充。
8. **zero-trade days 被排除是否让“长期不动、偶尔赚一笔”看起来过好？** 候选排除零交易日的做法（不 impute 0）对 per-trade estimand 是**正确的**（impute 0 会偏置均值并向零压缩有效事件数）。但必须显式声明：estimand 是“出手条件下的决策质量”，**不含机会成本**；加上 S2/S3 保证 30 个不同日/8 个活跃周，单点暴富会被 D 日/W 周门槛拦截。此条 KEEP。
9. **该 estimand 是否对应经济意义上的 edge？** 部分。它是决策 edge 的合理代理，但不是资本/时间维度上的经济 edge。若项目要回答 Protocol §9 的“economic edge”，需要(a)显式把“经济意义”定义为 per-decision 质量 + 地板，或(b)增加资本生产力诊断。建议 v1 保持 per-trade + 地板 + 明确解释，把 value-weighted/capital-productivity 作为 family 预注册诊断（候选已允许）。

**替代方案：** 若项目想要资本/时间维度的 edge，可用“每交易日平均净收益 / 平均占用 notional”（time-weighted）或 value-weighted mean 作为主 estimand；但它们在 6 个月、稀疏数据下更难推断（更少独立单元），且需要缺失的 portfolio-day 序列（capability audit：medium delta）。**v1 建议保持 per-trade equal-weight + 修正定义 + 明确解释，不做主 estimand 替换。**

---

## 7. SUFFICIENCY_VERDICT

**VERDICT = MODIFY（方向对，数字必须绑定功效目标并删冗余）**

逐条（B）：

- **N≥60**：无理论依据；约 1 笔/2 个交易日（117 日），对日内可行、对“每月几笔”的人类 playbook 结构不可能。作为“避免稀疏 tricks”的启发合理，但必须与功率目标耦合（见 C-1）。
- **days≥30 / weeks≥8**：广度启发，合理但与 N 冗余耦合（N=60 已隐含 ≥8 周/≥30 日的上限部分）。KEEP 但解释为“广度下限”。
- **W≥4L**：bootstrap 稳定性门，合理（保证 block 数 ≥ 4）。KEEP。
- **ESS≥30**：见 C-2（公式假精确）+ H-1（30 是 CLT 启发）。**应移除或用 N/H 替代。**
- **day≤50% / week≤75%**：按笔数定义严格，但 S5 在边界近乎冗余（51.7% vs 50%），S6 有效。作为结构（非 outcome）门槛 KEEP；把 outcome 版（H-3）放到 risk。
- **open_ratio≤25%**：更像是数据质量/实现完整性检查（cohort 结束时未平仓占比），作为 sufficiency 谓词可接受但应注明是“实现完整”而非“统计充分”。
- **24 个月下大量 playbook 永久 INSUFFICIENT？** 是——而且是**系统性**的：对 HUMAN_PLAYBOOK_FIRST 的人类频率对象，N≥60（且 H≥2 时 ESS 需要 N≥90–240）在 6 个月 cohort 内几乎必然 INSUFFICIENT。**Protocol 明确允许稀疏 INSUFFICIENT，所以这不是冻结语义违规**；但 profile 必须(a)发布 power envelope，(b)显式回答“这种保守是正确还是过度”——答案取决于项目是否接受“v1 只能验证高频强 edge，其余全走 Shadow/Forward”。若项目希望 v1 能产出可验证的人类 playbook，当前数字过度。
- **稀疏 Human Playbook First 是否被系统性排除？** 是（H-1/C-1 的后果）。这是与 RESEARCH_DIRECTION 的最大张力，必须由 Owner/project 显式决策，不能由数字默认决定。

**L. 24-month reality（关键项）：** 12/6/6 是冻结治理选择，不保证统计功效（Protocol §10 已声明）。候选把“严格验证”包装在 6 个月 cohort 上，但没有声明**可检测效应包络**：现实上只能检测“强、高频、低波动”的 edge。**必须明确：什么时候接受 INSUFFICIENT_EVIDENCE**——(1) sufficiency 失败（候选已做）；(2) LIMIT-001 数据缺口（候选未定义，H-4）；(3) power envelope 显示 cohort 在乐观结构假设下也检测不到地板（候选未发布，C-1）。三者都应是合法 INSUFFICIENT_EVIDENCE，而不是 FAIL；且 6 个月数据**不能**被用来“证明无 edge”（缺乏拒绝能力），只能证明“检测不到”。

---

## 8. UNCERTAINTY_METHOD_VERDICT

**VERDICT = MODIFY（week-block 方向合理，但 block 长度/归属/B/功效有具体问题）**

### C. ESS（已详述 C-2）：**VERDICT = REMOVE（或替换为有推导的 N/H 保守式）**

### D. Week-block bootstrap（逐条）：

1. **为什么 calendar week 是正确 block unit？** 没有理论依据——7 日是人类日历构造，不是依赖结构；中国期货夜盘/节假日使“周”长度不规则。**但它简单、确定、可审计，且能保留同周跨品种 contemporaneous 依赖**（这是它的最强论据）。作为 v1 工程简化可辩护，但必须承认“week 是便利 cluster，不是依赖结构的事实单位”。
2. **为什么最大只允许 4 周？** 为 6 个月 cohort 稳定性；与 C-1 一致（L=4 需要 W≥16，VALIDATION 27 周可达）。但 4 周上限意味着超过 4 周持仓的依赖不被 block 覆盖，只能靠 ESS（假精确）兜底。要求文档写明该限制。
3. **L 与 Hmedian 的公式？** L=min(max(1,ceil(H/5)),4) 无理论；/5 是“一周 5 个交易日”的换算，cap=4 是稳定性。它确实让 L≈持仓周数（合理方向），但用 median（M-4）不稳健。
4. **只有 8 个 active weeks 时 bootstrap 是否可靠？** W=8、L=1 时 m=8，distinct 重采样 6435（<10000），分布粗糙、p 值分辨率有限（M-3）；且 8 个周对“周间变异”的估计高度不确定。S4 允许 W=8 且 L=1，是 profile 的最弱配置。
5. **sparse/event-based returns 放 week block 是否适合？** 事件稀疏时多数周无交易；候选只用 active weeks 重采样，与 per-trade estimand 内部一致（不 impute），但对“时间上稀疏的 edge”没有时间维度信息。可接受，须声明。
6. **跨周 trade 怎么归属？** exit-week 归属（C-3/M-4）：多周持仓的 PnL 全部记到平仓周，破坏 block 对多周依赖的保持，仅在 L≥跨度时部分缓解。**这是 D 的最大具体缺陷，必须修。**
7. **同周多品种高度相关怎么办？** 由 week block 完整保留（所有品种同周同进退）——这是该方法的最大优点，KEEP。
8. **circular block 是否引入不合理 year-boundary adjacency？** 是（M-2），6 个月 cohort 首尾相隔约 6 个月且跨 VALIDATION/FINAL 边界。伪影必须文档化。
9. **validation 只有 27 周，统计能力如何？** 低（C-1）。27 周、N=60、σ=20–30bp 时，80% 功效最小可检测 edge 6.4–9.6bp。power envelope 必须发布。

**E. One-sided test（verdict）：** **KEEP**（决策导向合理），强制 two-sided CI 诊断 + 显式 downside 归属（M-1）。不产生“偏向发现正收益”的偏差——负/零 edge 在决策表里就是 FAIL；但要避免把它误读为“证明无 downside”。

---

## 9. MULTIPLICITY_VERDICT

**VERDICT = MODIFY（Holm 保留为 v1 默认，但计数规则 + 错误率目标必须补全）**

### F. Holm 对比：

- **whole-wave 高度相关假设下 Holm 是否过度保守？** 是。Holm 在任意相关下控制 FWER（有效），但阈值不利用相关结构 → 相关分支越多越弱；与 H-5 过罚叠加，wave 内分支多时接受概率趋零。
- **Human Playbook First 同时测几十个 claim 是否几乎全灭？** 是——M=20 时最小 p 阈值 0.0025，加上 C-1 的低功效，几乎必然全灭。这是“逐 playbook 声明 + 全 wave FWER + 低功效”的组合结果，必须让项目显式接受或调整。
- **Romano-Wolf 是否明显更合适？** 对**相关**wave 是（H-6）：共享 week-block 重采样下可同时算全部 M 统计量并做 stepdown，比 Holm 更接近问题且功效更高。但实现复杂度更高，需要 wave 内所有假设共享同一重采样结构（可行：它们在同一日历上）。**不是自动推荐**——v1 若预期 wave 内相关分支少，Holm 足够；若预期多，应预合并分支或上 RW。
- **White Reality Check / SPA 是否更贴近？** 它们是“best of many vs benchmark”问题。v1 禁止 argmax 报告，所以不是主工具；但**作为 wave 级 robust 诊断**（“本 wave 最优者是否显著优于基准，考虑选择效应”）很有价值。需要定义基准（per-trade 基准=0 最自然）；**不要**作为 v1 gate（复杂度+基准自由度=搜索面）。
- **FDR 为什么不适合？** 候选论证正确：接受一个 playbook 是可交易的逐决策行为，错误率应是逐决策 FWER，而不是“发现集合中假阳性比例”。FDR 适用于“批量筛选、后续再过滤”的场景；本项目验收即用。KEEP 候选的 FDR 拒绝。
- **项目想接受“至少一个有效 playbook”还是逐 playbook 声明？** 必须显式回答，因为它改变错误率定义：
  - 若目标是“wave 内至少一个有效”：全局检验（max statistic / RC 风格）定义 FWER at wave level。
  - 若目标是“逐 playbook 声明、通过者即可交易”：per-hypothesis FWER（Holm/RW）。
  Protocol §9 的 common acceptance contract 是 per-family 的 → 默认 per-hypothesis FWER。**候选应把这一目标写死**，并说明 wave 级“至少一个”不是目标（避免被误读为需要全局检验）。
- **v1 推荐：KEEP Holm** + (a) 计数 taxonomy（H-5）减少过罚；(b) 相关分支族内预合并；(c) 显式错误率目标；(d) 文档化 RW 作为相关 wave 的升级路径（判据：wave 内预注册相关分支数 > 阈值）；(e) wave 级 RC 风格 best-of 诊断（报告，非 gate）。

### G. 可审计计数规则（推荐）：

```text
COUNTING_UNIT = HYPOTHESIS_TEST_ID_V1
- 真分支（不同机制/解释，可独立证伪）         = +1 每分支
- 一个 pre-registered 搜索事件内的参数/周期/范围网格 = +1（网格本身；选中点须在 outcome 前声明，
  且必须在 validation/holdout 单独确认或做 best-of 校正，否则该网格按 M 个点计数）
- scope 扩张（超出 source claim 的 instrument/timeframe/context） = +1 每扩张
- PRIMARY（每个 claim 一个）                 = +1
- nuisance 实现变体（同语义不同代码）         = 0；必须证明 outcome 中性，否则视为搜索事件
- FAIL / INSUFFICIENT_EVIDENCE              = 永久留分母
- outcome 后新增任何假设                     = 新 wave / search event（冻结）
```

这个规则：对“网格点全当独立假设”的过罚（H-5）给出答案（网格=1 但强制 best-of 校正，防止洗 search freedom）；对“少报分支”给出答案（真分支/scope 扩张必须逐个 +1，且计数单位机器可校验）。

---

## 10. COST_STRESS_VERDICT

**VERDICT = MODIFY（固定 2× 可保留为最简单 v1，但必须加 base 保守性 + sensitivity 诊断 + 风险结构拆分）**

- **为什么 2×**：无测量依据，治理常数（候选承认）。KEEP 作为最简单统一方案，但这是“治理选择”不是“测量”。
- **fee 和 slippage 都乘 2 合理吗？** 不合理地混同：fee 近确定性，slippage 随机、结构不同。建议拆分文档说明，或至少 sensitivity 诊断区分二者。
- **exchange fee / broker fee / slippage 风险结构不同**：正确观察；固定 2× 忽略之。
- **forced liquidation cost 怎么办？** 尾事件，不是稳态成本流；由 R1 处理（FAIL），不进稳态 stress。文档写明。
- **小收益 playbook 是否被任意倍数决定生死？** 是（H-2 的核心）。缓解：保守 base 模型 + 报告 1.5×/2×/3× 结论带，使接受不是一个数字悬崖。
- **比较**：固定 2×（最简单、统一）/ tick-based slippage stress（更经济、需 tick 元数据与 N 的选择）/ percentage stress（粗）/ family-specific pre-registration（最现实但引入 per-family 自由度=搜索面）。**选最简单安全方案 = 固定 2× + 保守 base + sensitivity 诊断**；tick-based 列为 v1.1 候选，family-specific 成本模型须作为预注册诊断而非 gate。

---

## 11. ENGINE_COMPATIBILITY_VERDICT

**VERDICT = MODIFY（大部分是工程前提，候选已正确记录；但有 3 处统计设计层面不完整）**

用 capability audit 攻击 candidate：

- **round-trip ledger 缺失**：工程前提（audit：small delta）。候选 §4.3/§15 诚实记录。**但** round-trip 语义（partial close/pyramiding/forced liquidation/跨周归属）是统计设计（C-3），不能委托给工程。→ 工程前提 + 设计不完整各占一半。
- **TD-002 partial-close equity path**：候选主 estimand 用 **realized** PnL，不消费 intermediate equity path → **对主统计量稳健**（audit 确认 realized 不受污染）；但 risk 诊断（drawdown/M-5）会受影响，必须声明并先修 TD-002 再启用 DD 诊断。→ 工程前提（对主路径），设计声明缺失（对诊断）。
- **multi-day portfolio series 缺失**：候选选择 trade 级 estimand **刻意避开**了这一 medium delta——设计匹配引擎现实（优点），但代价是“资本维度经济 edge”无法回答（A9）。→ 设计选择（可辩护），需显式声明局限。
- **hypothesis/wave join 间接**：工程前提（audit：small delta，经 experiment→OutcomeTestRegistration）。候选需要 per-hypothesis 分组；在 evaluator 实现时必须物化 join。→ 工程前提。
- **LIMIT-001 block**：真实 corpus confirmatory PnL 对 price-limit-bound 合约 fail-closed 被 block。候选决策表**无 DATA_BLOCKED 结果**（H-4）。→ 设计不完整（必须补结果状态）。
- **holding duration / weekly aggregation 尚需 delta**：工程前提（audit：small）。H_median 与 exit_week 依赖它；注意 TD-001 权威选择会影响交易日计数。

**结论：** 6 项中 4 项是工程前提（候选已正确记录为 ENGINEERING_DELTA），2 项（round-trip 语义、DATA_BLOCKED 结果）是**统计设计本身定义不完整**，必须在 lock 前补入 profile 文档。

---

## 12. MINIMUM_REQUIRED_CHANGES

锁定前必须完成（按优先级）：

1. **C-1**：在 profile 文档发布 power envelope（N/ESS/σ → 80% 功效最小可检测 edge），并显式定义 INSUFFICIENT_EVIDENCE 为“本 cohort 检测不到本 profile 要求的效应量”。
2. **C-2**：移除 ESS= N/(2H−1) 作为精确门槛；改用 bootstrap 承担重叠、或 N/H 保守式（注明模型），或“bootstrap 方差比”结构诊断。
3. **C-3**：在 profile 文档写死 round-trip 语义（partial close / pyramiding / forced liquidation / 跨周 block 归属 / H 定义）。
4. **H-3**：增加 outcome-based 时间窗 PnL 集中度 robust 检查（阈值 lock 前定）。
5. **H-4**：增加 DATA_BLOCKED / INSUFFICIENT_EVIDENCE (data-gap) 决策结果；LIMIT-001/TD-002/TD-001 激活条件在 VALIDATION 前必须满足。
6. **H-5/G**：写死可审计计数 taxonomy（搜索事件/真分支/scope 扩张/nuisance）+ 网格 best-of 校正规则。
7. **H-6/F**：修正 RW 描述；显式错误率目标（per-hypothesis FWER）；给出“何时升级 RW”的可判定条件。
8. **H-1**：把 60/30/8/30 校准到功效目标或按 §13 简化；删除或替换 2H−1 ESS。
9. **H-2**：base 成本保守性 + 强制 cost-sensitivity 诊断带（1.5×/2×/3× 报告）。
10. **M-1..M-6**：one-sided+two-sided CI 诊断；circular-wrap 伪影文档化；B 与 distinct 空间对齐；block 长度用 max/90 分位；强制风险诊断块；FINAL power envelope 一致化。

## 13. RECOMMENDED_SIMPLIFIED_V1

一个更简单、确定性、不过度拟合的 v1（在 C-1..C-3 修复后）：

```text
ESTIMAND     : 平均单笔净收益 / 开仓名义本金（completed round trips；语义按 §12#3 写死）
SUFFICIENCY  : N>=60 且 D_days>=30 且 W_active>=8 且 open_ratio<=0.25
               （删除 S5/S6 计数集中度、删除 ESS；计数集中度不负责 outcome 问题）
UNCERTAINTY  : one-sided circular week-block bootstrap, alpha=0.05,
               B = min(10000, distinct-resample-space 上限), 固定 seed；
               block 长度 L = min(max(1, ceil(H_p90 / 5)), 4)（用 90 分位持仓，非 median）；
               发布 power envelope 表
RISK         : R1 强平/保证金穿仓 >0 -> FAIL
               R2 单笔 |r_t| > 40% Σ|r_t| -> FAIL
               R3 单周 |净PnL| 集中度 > 预注册分数 -> FAIL（阈值 lock 前定，非 outcome 调）
               + 强制风险诊断块（max DD/最差周/最大单笔亏损/峰值杠杆）——报告，非 gate
EDGE FLOOR   : MIN_ECONOMIC_EDGE = 2bp（经济意义地板；与功效包络分开声明）
COST STRESS  : 固定 2×（总成本）必须通过；强制报告 1.5×/2×/3× 敏感度带
MULTIPLICITY : Holm（α=0.05, one-sided, whole-wave denominator M）
               + 计数 taxonomy（§9 G）
               + 相关分支族内预合并
               + wave 级 best-of 诊断（RC 风格，报告非 gate）
DATA GAP     : DATA_BLOCKED / INSUFFICIENT_EVIDENCE(data-gap) 作为合法结果
```

这比候选减少约一半的互锁阈值（去掉 ESS、S5/S6 计数集中度、B=10000 假精确、2H−1），同时保留所有核心防线（block bootstrap、Holm、2× stress、R1/R2/R3、地板、INSUFFICIENT_EVIDENCE）。功效目标由 power envelope 单一来源驱动，避免“13 个自由 knob 的假精确”。

## 14. strongest argument against candidate

**候选作为一个“严格验证”装置，其自身门槛让它几乎不可能接受任何现实 playbook，且把这种空转包装成严谨：** 在 6 个月 VALIDATION、现实日内波动（σ=20–30bp）下，80% 功效需要真实单笔 edge ≈6.4–9.6bp（H=1）到 11–21bp（H≥2 经 2H−1 ESS 折损后），是 2bp 经济地板的 3–10 倍；叠加 Holm 分母与 2× 成本压力后更高。同时 N≥60 + ESS≥30 结构性排除 HUMAN_PLAYBOOK_FIRST 真正研究的“人类频率、稀疏”对象。加上 ESS 公式本身是内嵌 AR(1) 模型的假精确（精确重叠 IID 模型给 N/H 而非 N/(2H−1)），以及 estimand 对 partial close/pyramiding/forced liquidation/跨周归属未定义——候选呈现的是“看起来精确、实则既检测不到、又定义不全”的统计门槛。**安全靠空转买到，严谨被 13 个任意常数伪造。**

## 15. strongest argument for candidate

**候选是预注册、确定性、全族统一、outcome-free、search-freedom 单调的 fail-closed 门槛，正确避开了所有经典陷阱，且设计匹配引擎现实：** 它拒绝 Sharpe（Lo 2002 的短样本不可靠）、拒绝 IID bootstrap（会低估依赖）、拒绝 per-product 投票（伪独立）、拒绝 FDR（逐决策 FWER）、拒绝 post-hoc 阈值；它用 week block 保留同周跨品种 contemporaneous 依赖；trade 级 realized-PnL estimand 天然避开 TD-002 的 equity-path 污染和缺失的 portfolio-day 序列；INSUFFICIENT_EVIDENCE 是冻结合法结果且不放松；一切数字在 candidate 时（outcome 前）固定并绑定不可变 identity。**如果项目能接受“v1 只验证高频强 edge、其余诚实返回 INSUFFICIENT_EVIDENCE 并等 Shadow/Forward”，候选的骨架是安全、可审计、协议忠实的。**

## 16. 能否在不改 Protocol v1.0 的前提下锁定候选

**可以。**

- 所有必需修改（§12）都落在 profile 自身的数字、公式、定义、决策表结果上；profile 当前是 `CANDIDATE_NOT_LOCKED`，Protocol v1.0 §8/§16 明确允许在首个 candidate outcome 前设计、独立审查、修改并锁定 profile。
- 冻结语义（SOURCE CLAIM ≠ 解释 ≠ 机器化、PRIMARY、RESEARCH_WAVE whole-wave 分母、12/6/6、INSUFFICIENT_EVIDENCE、CAT1/2/3、historical holdout≠prospective unseen、pre-outcome gate）**均未被触碰**。C-1..C-3/H-1..H-6 的修复不需要改变任何冻结语义；其中“相关分支预合并”“网格 best-of 校正”“wave 级 best-of 诊断”都只是 Protocol §7 既有规则（whole-wave 分母、search-freedom 记账、independently falsifiable hypotheses）的实现细节，不改变语义。
- 唯一需要项目显式决策（非语义变更）的是 **H-1/L 的张力**：是否接受“v1 只能验证高频强 edge、人类频率 playbook 走 INSUFFICIENT_EVIDENCE + Shadow/Forward”。这是研究政策问题，应在 lock 前由 Owner/project 显式确认，但不需要修改冻结协议文本。

```text
REVIEW_VERDICT            = GO_WITH_REQUIRED_CHANGES
CRITICAL                  = 3 (C-1, C-2, C-3)
HIGH                      = 6 (H-1 .. H-6)
MEDIUM                    = 6 (M-1 .. M-6)
OVER_GOVERNANCE           = 4 (O-1 .. O-4)
PRIMARY_ESTIMAND_VERDICT  = MODIFY
SUFFICIENCY_VERDICT       = MODIFY
UNCERTAINTY_METHOD_VERDICT= MODIFY
MULTIPLICITY_VERDICT      = MODIFY
COST_STRESS_VERDICT       = MODIFY
ENGINE_COMPATIBILITY_VERDICT = MODIFY
CANDIDATE_LOCKABLE_WITHOUT_PROTOCOL_CHANGE = YES (after §12 changes)
```

# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_REVIEW

> Role: **THIRD STATISTICAL LANE — COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_REVIEWER**
> Worktree: `kline-playbook-engine-inference-resolution-r04` (isolated, from `origin/main` `83e8aa4`)
> Branch: `parallel/stat-profile-inference-resolution-r04`
> Date: 2026-08-19
> Status: `RESOLUTION_REVIEW_COMPLETE / ADVISORY / CANDIDATE_0_3_NOT_LOCKABLE / NO_CANDIDATE_OUTCOME_DATA_USED`
> Scope: narrow inference-resolution / tie-break after two independent reviews + project-brain adjudication (`HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_PARALLEL_REVIEW_ADJUDICATION_V0_2.md`)
> Reproducibility: `docs/reviews/support/stat_profile_inference_resolution.py` (numpy only, deterministic seeds)

## 执行摘要（中文）

审查结论：**NO_LOCKABLE_V1_INFERENCE**。

在冻结的 6 个月 cohort（VALIDATION D=117、FINAL D=126）上，**不存在一个可辩护的、无任意 knob 的、能保留 event-weighted per-round-trip estimand、在 Holm 相关尾部控制 strong-FWER ≤ 0.05 的逐假设推断方法**。具体地：

1. **候选 0.3 的 Shao 自归一化（渐近 pivotal 校准）在强持续性与左偏下确实反保守**——两条独立 lane 已确认，本审查复现：AR(1) ρ=0.95 时 one-sided size ≈ 0.12–0.13（名义 0.05），Holm 相关尾部（α=0.0025）≈ 0.031–0.034（13–14 倍名义）；左偏（5% at −19 / 95% at +1，均值 0）size ≈ 0.08–0.10、尾部 ≈ 6–12 倍名义。**即使“温和左偏”（10% at −1 / 90% at +1/9）也把 size 推高到 ≈0.077–0.085**——这不是病态 fixture，正是交易 PnL 的典型形状。更极端但同样现实的“rare extreme losses”（1% 天 @ −20，均值 0）使 ~29% 的零假设序列（未出现极端损失日者）在**所有水平**都被误拒。
2. **本审查新的决定性证据：wild bootstrap（Rademacher 与 Gaussian）校准并不能修复该问题。** 对同一 T_SN 统计量做 fixed-b wild bootstrap（零假设下受限重采样），在强持久性与左偏下仍然反保守（ρ=0.95 size ≈ 0.13–0.15、尾部 ≈ 0.034–0.038；左偏 size ≈ 0.08–0.10、尾部 ≈ 0.031）。原因在理论上清楚：wild bootstrap 是为**异方差**（Wu 1986）设计的，它随机化符号从而破坏时间序列的依赖结构，无法复现持久序列的部分和路径形状。**任何基于 T_SN 自身形状的 bootstrap 校准都继承同一反保守性。**
3. **其他方法族在本审查的合成测试中同样无法满足约束**：block bootstrap 有 block-length knob（项目脑已因短样本敏感性拒绝 MBB 方向）且 block 长度敏感；weekly/grouped 方法只有 27 个周观测并对周间依赖假设近似独立（强日度持久性下失败）；subsampling 的 p 值分辨率只有 ~1/88 ≈ 0.011，无法支撑 Holm 的 α/M=0.0025–0.01 尾部；而“admissible-domain 门”要么需要任意 ρ̂/skew 阈值（adjudication 明确拒绝），要么需要 outcome-based 循环认证（不被允许）。
4. **结论：在冻结 cohort 长度 + strong-FWER 目标 + 禁止任意门 + 禁止 outcome 调优 + 禁止弱化错误率 的共同约束下，v1 没有可锁定的一般域逐假设推断。** 诚实的后果是：6 个月 cohort 下，per-hypothesis 的统计 PASS 无法被辩护；`INSUFFICIENT_EVIDENCE` 是唯一诚实结果；要获得可辩护的 PASS，项目必须走 Owner 门改变至少一个冻结约束（如更长的评估窗口/池化 cohort），或明确接受受限 admissible domain 及其门（需独立论证而非 reviewer 示例），或把接受性证据移到未来 Shadow/Forward 数据。

**本审查未修改 candidate 0.3、CURRENT_STATE、冻结 Protocol v1.0、12/6/6、生产代码或测试。** 未使用任何候选 outcome / PnL / equity / Sharpe / win-loss / VALIDATION / historical-final 数据。

---

## 1. INDEPENDENCE_AND_SCOPE

- This is the **third statistical lane**, an inference-resolution / tie-break package, not a blinded independent lane. Per the task, the two prior review artifacts and the project-brain adjudication **may be and were read**; neither reviewer is treated as authority over this resolution.
- Work was performed in an isolated worktree created from `origin/main` `83e8aa4` on a fresh branch; no existing worktree/branch was modified; `main` was not pushed.
- Read artifacts (both lanes + adjudication):
  - `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_PARALLEL_REVIEW_ADJUDICATION_V0_2.md` (project-brain authority for this task)
  - Lane A: `parallel/stat-profile-delta-review-r03` @ `cbfc1ae` → `HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_TARGETED_DELTA_REVIEW.md`
  - Lane B: `parallel/stat-profile-sn-falsification-r03` @ `a4008df` → `HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_SELF_NORMALIZATION_SECOND_REVIEW.md`
  - `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE.md` (candidate 0.3)
  - `docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_EVIDENCE.md`
- Not consulted: `ENGINE_COMPATIBILITY_CROSSWALK` is not needed for this inference-resolution question and was not read in this lane.

## 2. AUTHORITY_READ

- `AGENTS.md`, `OWNER_COLLABORATION_CONTRACT.md`, `ARCHITECTURE_BASELINE.md`, `CURRENT_STATE.md`, `RESEARCH_DIRECTION.md`, `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md` (FROZEN)
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md` (FROZEN 12/6/6)
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md` (FROZEN)
- `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`
- `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_PARALLEL_REVIEW_ADJUDICATION_V0_2.md`
- Lane A and Lane B review artifacts (see §1)
- `docs/reviews/HANDOFF_THIRD_PASS_FAILURE_MODE_REVIEW_2026-08-19.md`
- Code interfaces: `src/research_firewall.py` (`CommonStatisticalProfile`, `ResearchWaveManifest`, `OutcomeTestRegistration`, `PreOutcomeGate`) — confirmed the profile/wave/denominator binding surfaces needed for a future implementation.

## 3. PRIMARY_LITERATURE

- **Shao (2010)** JRSS-B 72(3):343–366 + **corrigendum** 72(5):695–696 — the self-normalized scalar-mean pivot `T_inf = B(1)/sqrt(int_0^1 (B(r)-rB(1))^2 dr)`; asymptotic, weak-dependence/FCLT based; corrigendum strengthens the remainder condition (trivial for the direct linear score). Both lanes and the design evidence verified this; this review independently reproduced the signed-pivot quantiles (q95 ≈ 5.31–5.33).
- **Holm (1979)** Scand. J. Statist. 6(2):65–70 — step-down FWER; valid under arbitrary dependence **given valid per-hypothesis p-values**.
- **Romano & Wolf (2005)** Econometrica 73(4):1237–1282 — stepdown for a family under dependence; not argmax-only; not needed if per-hypothesis p-values are valid, cannot repair invalid ones.
- **Wu (1986)** Ann. Statist. 14:1261–1350 — wild bootstrap; designed for **heteroskedasticity**, not serial dependence.
- **Künsch (1989)** Ann. Statist. 17(3):1217–1241 — moving-block bootstrap for dependent data (the block-length knob is the obstacle at D≈120).
- **Politis & Romano (1994)** JASA 89:1303–1313 — stationary bootstrap (has a mean-block-length parameter).
- **Politis, Romano & Wolf (1999)** *Subsampling*, Springer — subsampling valid under very weak conditions; p-value resolution ~1/(D−b+1) (the Holm-tail obstacle).
- **Cameron, Gelbach & Miller (2008)** Rev. Econ. Statist. 90(3):414–427 — wild cluster bootstrap for few clusters (the weekly approach; between-cluster dependence is its limit).
- **Efron (1979)**; **Bickel & Freedman (1981)**; **Singh (1981)**; **Hall (1992)** — bootstrap is asymptotically consistent but provides **no general finite-sample guarantee**; the finite-sample accuracy is what fails at D=117 under persistence/skew.
- Verification status: Shao/Holm/RW bibliographic identity verified via the two prior lanes and the design evidence; Wu/Künsch/PRW/PRW-subsampling/CGM are standard established references (direction of their design goals is well-known); no paywalled full text was re-retrieved in this lane; the decisive evidence here is the synthetic falsification, not a literature quote.

## 4. ADJUDICATED_FACTS_ACCEPTED

Accepted from `PARALLEL_REVIEW_ADJUDICATION_V0_2` (not reopened without proof):

1. **Count-return independence is NOT a project requirement.** The population target is `theta = E[S_d]/E[C_d]` = event-weighted per-trade mean; the null is `E[S_d] <= 0`. This review generates null processes with `E[S_d] = 0` exactly, so the falsification below attacks the inference procedure, not the estimand.
2. **Finite-sample anti-conservatism of self-normalized p-values at D≈117/126 IS the blocker** (strong persistence; left-skew).
3. **Strong-FWER ≤ 0.05 is NOT weakened.**
4. **No reviewer-derived numeric gates** (rho/skew/ESS/B thresholds) are adopted; arbitrary cutoffs are rejected.
5. Holm remains the default multiplicity method **only if per-hypothesis p-values are defensible**.
6. Zero right-censoring, LOTO/LOWO, no universal 2 bp / 2x gates, `DATA_BLOCKED`, `INSUFFICIENT_EVIDENCE` as frozen legitimate result, and machine-consistent `hypothesis_test_id` counting are retained as accepted v1 governance facts.
7. Confidence-bound inversion must fail closed to `INSUFFICIENT_EVIDENCE` when no unique valid root exists in the pre-registered search domain.

## 5. METHODS_EVALUATED

The task requires evaluating method families A–F. Each was assessed on: (i) estimand preservation, (ii) size control at D=117/126 across a realistic regime space (persistence, skew, sparsity, heteroskedasticity, clusters, rare losses), (iii) Holm-tail resolution, (iv) power/resolution, (v) number of arbitrary knobs, (vi) implementability.

- **A. Shao self-normalization + deterministic validity envelope / fail-closed diagnostics.** The method itself is mathematically correct as a limit law. The envelope idea fails because no non-arbitrary cutoff can separate "valid" from "anti-conservative" without outcome-based circularity (§8). Evaluated: REJECT.
- **B. Studentized moving/block bootstrap or subsampling.** Block bootstrap preserves dependence but has a block-length knob and short-sample fragility (project brain already rejected a weekly-MBB direction for size inflation). Subsampling has unusable Holm resolution (~1/88). Evaluated (block_bt L=5/10/15; subsampling resolution analysis): REJECT.
- **C. Fixed-group / grouped-time (weekly) inference.** Weekly aggregation (G≈27 weeks) reduces skew and within-week dependence but assumes weeks are approximately independent units; under strong daily persistence the weekly scores remain autocorrelated and the method is anti-conservative; G=27 is few observations. Evaluated (week_t, week_wild): REJECT for the general domain.
- **D. Small-sample robust mean procedures preserving the same estimand.** Trimmed means / medians / winsorized estimators change the estimand (rejected by the project's estimand-pinning). Robust *variance* (Huber-White) does not handle serial dependence. Bounded-support concentration bounds require an unrealistic bounded-return assumption (explicitly rejected by the task). REJECT.
- **E. Intersection rule (PASS requires agreement of two inference procedures).** The intersection's size is ≤ the more conservative member, so it could in principle rescue PASS *if one member were provably conservative*. Falsification shows the natural members (asymptotic SN, wild-bootstrap SN) are all anti-conservative in the same regimes, and no provably-conservative member with Holm resolution exists (§8). REJECT as a v1 construction.
- **F. Wild-bootstrap calibration of the self-normalized statistic (fixed-b wild bootstrap; the natural "no-knob bootstrap refinement" of the candidate).** This was the strongest *new* candidate: it preserves the estimand, has no block-length/bandwidth knob, and its bootstrap critical values adapt to the observed dependence/shape. **Falsification is decisive: it does NOT control size** (§7, §11). REJECT.
- **G. (Additional) Asymptotic SN (candidate 0.3) — baseline.** Confirmed anti-conservative under persistence and left-skew (both lanes + this review). REJECT as a strong-FWER basis.

## 6. METHODS_REJECTED (with reasons)

| Method | Primary defect under the frozen constraints |
| --- | --- |
| Asymptotic SN (candidate 0.3) | anti-conservative at D=117/126 under strong persistence (size 0.12–0.15 at ρ=0.95) and left-skew (size 0.08–0.10; Holm tail 6–14× nominal); rare-loss shape rejects ~29% of null series |
| Wild-bootstrap SN (Rademacher / Gaussian) | empirically anti-conservative in the same regimes (tail 0.031–0.038 at α=0.0025; new finding); wild bootstrap is designed for heteroskedasticity, not serial dependence, so it cannot reproduce the persistence-driven partial-sum shape |
| Block bootstrap (mean, L=5/10/15) | block-length knob; L-sensitive even for IID (size 0.063–0.085); worse than SN under persistence (ρ=0.95 size 0.24–0.31) |
| Weekly grouped t / wild cluster | only G≈27 units; assumes between-week independence, which fails under daily persistence (week_t size 0.30–0.62 at ρ=0.8–0.95; week_wild 0.15–0.32) |
| Subsampling | p-value resolution ≈ 1/(D−b+1) ≈ 0.011 at b≈30 → cannot reach Holm thresholds 0.005–0.0025 for M ≥ 10 |
| Trimmed/median/robust-location mean | changes the estimand (prohibited) |
| Bounded-support concentration bounds (Hoeffding-type) | requires a false bounded-return assumption (prohibited) |
| Admissible-domain gate (rho/skew diagnostics) | cutoff has no independent justification; outcome-based circular certification is not allowed |

## 7. RECOMMENDED_METHOD

```text
RECOMMENDATION = NO_LOCKABLE_V1_INFERENCE
```

No single defensible inference procedure exists at D=117/126 for the general evidence domain under the frozen constraints (strong FWER ≤ 0.05, no arbitrary gates, no outcome tuning, estimand pinned, no bounded-return assumption, Holm-relevant tail resolution required). The three candidate families that were serious (asymptotic SN, wild-bootstrap SN, grouped-time weekly) are all falsified; the remaining theoretically-valid method (subsampling) has unusable Holm resolution.

The rationale for each of the three allowed labels:

- **KEEP_GUARDED_SELF_NORMALIZATION**: not defensible. (a) The asymptotic SN p-values are anti-conservative under the two realistic regimes; (b) the wild-bootstrap "guard" that would avoid arbitrary cutoffs is empirically anti-conservative too; (c) a deterministic rho/skew gate would need arbitrary cutoffs (adjudication rejects), and no non-arbitrary gate can be justified (§8).
- **REPLACE_SELF_NORMALIZATION**: cannot be honestly named. There is no replacement that satisfies all constraints with controlled size at D=117/126 across the plausible regime space. Naming one would mean either inventing an arbitrary knob or making an unjustified claim.
- **NO_LOCKABLE_V1_INFERENCE**: the technically correct result. The frozen 6-month cohort cannot support a defensible general-purpose strong-FWER per-hypothesis test; the honest outcome is `INSUFFICIENT_EVIDENCE` for the sign-unresolved case, and any statistical `PASS` at v1 would rest on anti-conservative p-values.

## 8. EXACT_INFERENCE_DEFINITION

**Not supplied — because no defensible exact definition exists at the frozen cohort lengths.** This is the substance of the resolution. The closest a defensible v1 could get is a *conditional* statement, which fails for the following reasons:

### 8.1 Why the "conditional on admissible domain" framing does not rescue v1

The task asks (Section 6) whether the only honest statement is `strong FWER <= 0.05 CONDITIONAL ON a locked admissible inference domain`, and whether that domain can be evaluated without circular outcome tuning. The answer is **no**:

1. The anti-conservative regimes (strong persistence; left-skew) are defined on the **daily score process** `Z_d = S_d`, which is outcome-shaped. Checking whether a hypothesis lies in the domain means inspecting its score process.
2. The task permits a diagnostic gate that sees the score process **only if** the cutoff has independent methodological justification and is locked pre-outcome. But:
   - A cutoff on lag-1 autocorrelation `rho_hat` or a skewness measure has **no independent methodological justification**: there is no theorem stating "the SN finite-sample pivotal approximation is adequate for `rho <= c`" for any c at D=117. The inflation is a smooth function of the whole spectral shape and skewness, not a step function at any defensible c.
   - Choosing c from the synthetic operating-characteristic table is **tuning on synthetic fixtures**, which the task forbids ("Do NOT tune a method on one synthetic family and then report the same family as validation").
   - Certifying the domain by simulating the estimated DGP of the observed score is **circular** (the DGP estimate at D=117 is itself uncertain and is outcome-shaped) and needs a tolerance knob.
3. Therefore the admissible domain cannot be evaluated pre-outcome without circularity or arbitrary cutoffs, and the "conditional" statement is not operational.

### 8.2 The estimand and statistic are not the problem

The estimand (`theta = E[S_d]/E[C_d]`), the daily-score representation (including zero-exit days), the ratio-of-means identity, the linearity of `Z_d(theta0)`, and the decision logic (`PASS / FAIL / INSUFFICIENT_EVIDENCE / DATA_BLOCKED`) are all coherent and are **retained** as the correct frame. The blocker is strictly the **finite-sample error control of the per-hypothesis p-value** at D≈117/126.

## 9. ASSUMPTIONS

Any viable candidate would need, at minimum, one of the following (all non-certifiable at D=117/126 without outcome-shaped inspection):

- Weak dependence + FCLT + positive long-run variance + finite moments (SN and bootstrap refinements) — **violated in finite sample** for persistent / left-skewed daily scores at D≈120.
- A block length that covers the dependence scale (block bootstrap) — a knob with no outcome-free justification and short-sample fragility.
- Between-block independence (weekly/grouped) — **violated** under strong daily persistence and multi-week holding overlap.
- Exchangeability of blocks (permutation/randomization) — not verifiable under dependence.
- Bounded returns (Hoeffding-type) — explicitly rejected.

None of these can be certified without either (a) inspecting the candidate score process with an arbitrary cutoff, or (b) assuming a specific DGP.

## 10. ERROR_CONTROL_SEMANTICS

Precise meanings of `strong FWER <= 0.05` under the frozen constraints:

- **Exact finite-sample guarantee**: NOT achievable for a general dependent, skewed, unbounded daily-score process at D=117/126 (no such test exists without a distributional model or a bound).
- **Asymptotic guarantee under stated process assumptions**: achievable (SN, bootstrap, etc.), but the finite-sample approximation at D=117/126 is **materially anti-conservative** for realistic persistence/skew — i.e., the asymptotic guarantee does not translate into the claimed finite-sample error rate.
- **Empirical operating-characteristic evidence**: this is what a locked profile could honestly provide (the size tables), but it would then be a *documented* ~7–15% (and tail up to 3–20×) one-sided error rate under the realistic regimes — which is **not** the project's strong-FWER ≤ 0.05 target.
- **Heuristic diagnostics** (LOTO/LOWO, structural reports): conservative by construction, but they are not p-value procedures and cannot repair an anti-conservative p-value; they can only demote a would-be PASS to IE.

**Conclusion:** the only honest v1 error-control statement is `strong FWER <= 0.05` **conditional on an admissible domain that cannot be operationalized without arbitrary cutoffs or circular certification**. Since neither is acceptable, the strong-FWER claim cannot be honestly made at v1 cohort lengths, and `INSUFFICIENT_EVIDENCE` is the only defensible sign-unresolved outcome.

## 11. SYNTHETIC_FALSIFICATION

Reproducibility: `docs/reviews/support/stat_profile_inference_resolution.py` (numpy only). Deterministic seed `20260819`; R = null replications; B = bootstrap resamples. One-sided rejection fraction at nominal α (target = α). MC SE at α=0.05 for R=1200 is ~0.0063; for the R=5000 tail focus at α=0.0025 it is ~0.0007.

Pivot calibration (independent, this lane): signed-pivotal quantiles `q95=5.307, q97.5=6.705, q99=8.603, q99.5=9.943, q99.75=11.314` (200k paths × 1000-grid) — consistent with Lane A (5.327) and the candidate smoke (5.335) within MC error.

### 11.1 Size at α=0.05 (R=1200, B=999); D = frozen cohort trading days

| daily-score null (E[S_d]=0) | sn_asy D117 | sn_asy D126 | sn_wild_r D117 | sn_wild_r D126 |
| --- | ---: | ---: | ---: | ---: |
| iid_gauss | 0.051 | 0.041 | 0.052 | 0.040 |
| ar1_0.30 | 0.062 | 0.059 | 0.060 | 0.059 |
| ar1_0.60 | 0.059 | 0.059 | 0.058 | 0.058 |
| **ar1_0.80** | **0.072** | **0.066** | **0.077** | **0.062** |
| **ar1_0.95** | **0.130** | **0.123** | **0.147** | **0.130** |
| **left_skew_sev** | **0.087** | **0.079** | **0.079** | **0.085** |
| **left_skew_mild** | **0.077** | **0.085** | **0.073** | **0.085** |
| right_skew | 0.021 | 0.044 | 0.017 | 0.038 |
| t3 | 0.039 | 0.039 | 0.046 | 0.040 |
| t2 | 0.045 | 0.048 | 0.050 | 0.052 |
| garch | 0.049 | 0.051 | 0.053 | 0.054 |
| sparse_pois (λ=0.5) | 0.054 | 0.065 | 0.058 | 0.061 |
| bursty | 0.038 | 0.045 | 0.051 | 0.056 |
| week_cluster | 0.053 | 0.056 | 0.054 | 0.055 |
| var_change (3×) | 0.020 | 0.030 | 0.041 | 0.052 |
| **rare_loss (1% @ −20)** | **0.293** | **0.293** | **0.293** | **0.293** |
| persist_leftskew | 0.096 | 0.117 | 0.090 | 0.113 |
| persist_sparse | 0.072 | 0.083 | 0.076 | 0.087 |

### 11.2 Holm-relevant tail: rejection at α=0.0025 (M≈20 first-Holm threshold); R=5000

| null | sn_asy D117 | sn_asy D126 | sn_wild_r D117 | sn_wild_r D126 |
| --- | ---: | ---: | ---: | ---: |
| ar1_0.80 | 0.009 (3.6×) | 0.007 (2.8×) | 0.007 (2.8×) | 0.007 (2.8×) |
| **ar1_0.95** | **0.034 (13.6×)** | **0.031 (12.4×)** | **0.038 (15.2×)** | **0.034 (13.6×)** |
| **left_skew_sev** | **0.016 (6.4×)** | **0.016 (6.4×)** | **0.031 (12.4×)** | **0.031 (12.4×)** |
| left_skew_mild | 0.009 (3.6×) | 0.008 (3.2×) | 0.007 (2.8×) | 0.005 (2.0×) |
| **persist_leftskew** | **0.031 (12.4×)** | **0.022 (8.8×)** | **0.026 (10.4×)** | **0.019 (7.6×)** |

### 11.3 D=242 (≈ one year) convergence — the problem does NOT disappear with 2× data

| null | sn_asy | sn_wild_r | sn_wild_g |
| --- | ---: | ---: | ---: |
| iid_gauss | 0.051 | 0.053 | 0.051 |
| ar1_0.80 | 0.058 | 0.063 | 0.058 |
| **ar1_0.95** | **0.100** | **0.108** | **0.104** |
| **left_skew_sev** | **0.093** | **0.086** | **0.091** |
| left_skew_mild | 0.070 | 0.068 | 0.068 |

### 11.4 Block bootstrap (percentile, null-imposed, R=600) — L-sensitive and worse under persistence

| null | block_bt_5 D117 | block_bt_10 D117 | block_bt_15 D117 |
| --- | ---: | ---: | ---: |
| iid_gauss | 0.063 | 0.078 | 0.085 |
| ar1_0.80 | 0.173 | 0.123 | 0.122 |
| **ar1_0.95** | **0.305** | **0.262** | **0.237** |
| left_skew_sev | 0.137 | 0.133 | 0.130 |

### 11.5 Weekly grouped methods (G≈27 weeks; R=2000) — assume between-week independence, fail under daily persistence

| null | week_t VAL | week_t FIN | week_wild VAL | week_wild FIN |
| --- | ---: | ---: | ---: | ---: |
| iid_gauss | 0.091 | 0.105 | 0.046 | 0.054 |
| ar1_0.60 | 0.188 | 0.184 | 0.100 | 0.091 |
| **ar1_0.80** | **0.318** | **0.299** | **0.148** | **0.154** |
| **ar1_0.95** | **0.615** | **0.592** | **0.316** | **0.296** |
| left_skew_sev | 0.146 | 0.138 | 0.093 | 0.118 |
| sparse_pois | 0.098 | 0.093 | 0.046 | 0.053 |

### 11.6 Interpretation (falsification, not tuning)

1. **Well-calibrated regimes** (both SN variants): iid, mild/moderate AR(1) (ρ ≤ 0.6), symmetric heavy tails (t2/t3), GARCH heteroskedasticity, sparse compound counts, bursty counts, week-cluster dependence. These confirm the candidate's method is not broken in the "benign" part of the space.
2. **Anti-conservative regime 1 — strong persistence:** AR(1) ρ=0.95 inflates one-sided size to ~0.12–0.15 (2.5–3× nominal) and the Holm tail (α=0.0025) to ~0.031–0.038 (12–15× nominal).
3. **Anti-conservative regime 2 — left-skew (the realistic trading-PnL shape):** even **mild** left-skew (10% @ −1 / 90% @ +1/9) inflates size to ~0.077–0.085; severe (5% @ −19 / 95% @ +1) to ~0.08–0.10; the Holm tail inflates to 6–12× nominal. The `rare_loss` fixture (1% @ −20 / 99% @ +0.202, E=0) shows the mechanism at its extreme: ~29% of null series (those without an extreme-loss day, P ≈ 0.99^117 ≈ 0.31) have an almost-degenerate normalizer and are rejected at **every** level — the same mechanism Lane A described, at its strongest. The S4 guard catches the fully-degenerate case only, not the near-degenerate case.
4. **New decisive finding — wild bootstrap does NOT rescue the method:** `sn_wild_r` (Rademacher) and `sn_wild_g` (Gaussian) reproduce essentially the same anti-conservatism in both dangerous regimes (e.g., ρ=0.95 tail 0.034–0.038; left-skew_sev tail 0.031). The wild bootstrap is designed for heteroskedasticity (Wu 1986); it randomizes signs and thereby **destroys the serial-dependence structure** of the partial-sum path, so the bootstrap critical values do not reproduce the observed statistic's persistent-path distribution. A bootstrap of the same T_SN statistic inherits the same finite-sample defect.
5. **Alternatives fail on other axes:** block bootstrap is block-length sensitive and is *worse* than SN under persistence (blocks too short); weekly methods assume between-week independence and are *catastrophically* anti-conservative under daily persistence (week_t size 0.30–0.62 at ρ=0.8–0.95); subsampling cannot reach Holm tails (resolution ~1/88).
6. **D=242 does not cure it:** left-skew size remains ~0.09 at a full year of trading days, so even pooling ~359 days would not fully restore the strong-FWER claim; the shape problem is not purely a 117-day artifact.

## 12. HOLM_TAIL_BEHAVIOR

Holm over a wave with `M` hypotheses uses per-hypothesis thresholds `alpha/(M-i+1)`. For M ∈ {5, 10, 20} the smallest thresholds are 0.01, 0.005, 0.0025. The tail-focus table (11.2) shows the empirical one-sided rejection of the SN p-values at exactly these levels under the dangerous processes is 2.8–15× the nominal. **Consequences:**

- Holm **cannot repair** these p-values: FWER ≤ α requires per-hypothesis size ≤ α/M, which fails by 3–15× in the dangerous regimes.
- For a wave of M ≥ 10, the effective false-PASS risk for a null playbook under left-skew or strong persistence is ~0.02–0.05 **at the single-hypothesis level**, not 0.005–0.0025. Multiplied across a wave, the actual FWER is far above 0.05.
- The wild-bootstrap variant does not improve the Holm tail (same or worse inflation).
- Subsampling has unusable resolution at these thresholds (see §13), so no Holm-compatible conservative fallback exists at the frozen lengths.

**Conclusion:** the per-hypothesis p-values that Holm would consume are not defensible at Holm-relevant tails for the realistic regime space. This is the direct technical reason the strong-FWER target cannot be honestly met by candidate 0.3 or its bootstrap refinements at D=117/126.

## 13. POWER_AND_RESOLUTION

### 13.1 Power (IID standardized alternatives, one-sided 5%, R=1200)

| D | 0.1σ | 0.2σ | 0.3σ |
| --- | ---: | ---: | ---: |
| 117 | 0.235 | 0.575 | 0.812 |
| 126 | 0.256 | 0.597 | 0.842 |

`sn_asy`, `sn_wild_r`, `sn_wild_g` are nearly identical in power (within 0.003). So the wild bootstrap does not pay a power penalty — it simply fails to restore size. Under strong dependence power collapses further (Lane B: AR(1) ρ=0.9, 0.3σ → ~0.15), i.e., the same regime that breaks size also destroys power.

**Interpretation:** at the frozen lengths a real edge of ~0.2–0.3 per-day-score σ is detectable with ~0.58–0.84 power *in the IID case only*. Low power is not itself a defect — the honest state is `INSUFFICIENT_EVIDENCE` — but it means most real (small/moderate) edges will be IE in a 6-month cohort even if the inference were valid.

### 13.2 Holm resolution of subsampling

Subsampling (Politis–Romano–Wolf) is the one theoretically valid method under very weak dependence, but with block `b` the p-value resolution is `1/(D−b+1)`. At D=117, b=20–30 → resolution ≈ 0.011–0.010. This is below 0.05 (usable for M=1) but **above** the Holm thresholds for M ≥ 5 (0.01) and M ≥ 10 (0.005) — i.e., subsampling p-values cannot even take values ≤ 0.005–0.01, making Holm rejection impossible for realistic waves. **Rejected for the Holm requirement** ("unusable resolution under Holm").

### 13.3 Detectability statement

The valid state when the frozen cohort cannot resolve the claim is `INSUFFICIENT_EVIDENCE`; low power is never converted into `FAIL`. But because no size-valid inference exists at the frozen lengths (not merely low power), the statistical `PASS` path is unavailable for the general domain — which is the substance of `PROFILE_0_4_DRAFTABLE = NO`.

## 14. FAIL_CLOSED_RULES

Retained (accepted adjudication, not reopened): zero right-censoring → IE; LOTO/LOWO sign fragility → IE; non-degenerate normalizer / missing calibration artifact → IE/DATA_BLOCKED; `DATA_BLOCKED` for governed-fact gaps (LIMIT-001); sign-unresolved → IE (never automatic FAIL). **Additional consequence of this resolution:** because no defensible per-hypothesis PASS inference exists at the frozen lengths, the statistical `PASS` path cannot be honestly executed for the general domain; hypotheses whose sign is not resolvable — which, given the low power and the anti-conservative regimes, is the expected case — must return `INSUFFICIENT_EVIDENCE`. This is consistent with Protocol v1.0 (IE is a frozen legitimate result), but it means v1 produces **no positive acceptance** until a frozen constraint changes or longer/prospective data arrives.

## 15. CONFIDENCE_BOUND_RULE

The adjudicated rule (no unique valid root in the pre-registered search domain → `INSUFFICIENT_EVIDENCE`) is retained as the deterministic inversion governance. However, because the per-hypothesis p-values / pivotal quantiles that feed the inversion are anti-conservative at D=117/126, the resulting bounds are **narrower than honest** under the realistic regimes; a bound-based `FAIL` (upper bound ≤ 0) is safe in direction (a false FAIL is a missed opportunity, not a false acceptance) but a bound-based `PASS` is not. This review therefore requires that any v1 CI be labeled as a *diagnostic*, not a PASS basis, unless a frozen-constraint change makes a valid inference available.

## 16. IMPLEMENTATION_DELTA

Candidate 0.3 §13's engineering deltas (round-trip ledger keyed by `position_id`, daily `(S_d,C_d)` materialization, calibration artifact binding, Holm over the locked denominator, LOTO/LOWO, decision evaluator, machine-readable profile) remain the correct implementation surface **if and when** a defensible inference is adopted. This resolution adds **no** new implementation requirement, because the recommendation is that no inference be locked as a PASS basis at the frozen lengths. If a future (post-constraint-change) inference is adopted, it must be implemented as a bounded, deterministic, identity-bound evaluator and re-attacked before lock — per the adjudication.

## 17. FROZEN_PROTOCOL_CONFLICT

```text
FROZEN_PROTOCOL_CONFLICT = NO
```

The blocker is a profile-level inference-validity issue, not a frozen-research-semantic conflict. The resolution does **not** change Protocol v1.0, the 12/6/6 chronology, the estimand, the counting taxonomy, or any access state. The `INSUFFICIENT_EVIDENCE`-only consequence is protocol-consistent.

## 18. NO_CANDIDATE_OUTCOME_DATA_USED

```text
REAL_HUMAN_PLAYBOOK_RUN=NO
CANDIDATE_PNL_INSPECTION=NO
RETURNS_INSPECTION=NO
EXPECTANCY_INSPECTION=NO
SHARPE_INSPECTION=NO
WIN_LOSS_INSPECTION=NO
EQUITY_INSPECTION=NO
DRAWDOWN_INSPECTION=NO
VALIDATION_ACCESS=NO
HISTORICAL_FINAL_HOLDOUT_ACCESS=NO
THRESHOLD_TUNING_ON_CANDIDATE_OUTCOMES=NO
CANONICAL_MARKET_RETURN_CALIBRATION=NO
```

All quantitative work used algebra, primary-literature facts, and synthetic stochastic fixtures only. Calendar metadata (trading-day and ISO-week structure per frozen cohort) was read from `CANONICAL_TRADING_CALENDAR.json` as non-outcome metadata. Deterministic seeds only.

## 19. PROFILE_0_4_DRAFTABLE

```text
PROFILE_0_4_DRAFTABLE = NO
```

Because the recommendation is `NO_LOCKABLE_V1_INFERENCE`, this review does **not** supply exact pre-outcome inference definitions for candidate 0.4: any such definition would require either an arbitrary knob (block length, gate cutoff), a weakened error-rate claim, or a circular certification — all of which are outside this review's mandate. The project brain should not draft candidate 0.4's inference section from this review's absence; it should first resolve the frozen-constraint question below.

## 20. MINIMUM_REQUIRED_NEXT_ACTION

The project must decide one of the following (each is a material change requiring either an Owner gate or an explicitly scoped design-and-independent-attack package; none is silently decidable inside the current frozen constraints):

1. **Owner-gated frozen-constraint change to obtain a longer evaluation window** (e.g., pooling DEVELOPMENT+VALIDATION ≈ 359 trading days for the acceptance inference). This improves but does **not** fully solve the problem — §11.3 shows left-skew size ≈ 0.09 and AR(1) ρ=0.95 ≈ 0.10 even at D=242 — so it is necessary but not sufficient; it also requires changing the frozen acceptance-cohort semantics.
2. **Owner-gated acceptance of a bounded error-rate claim** (e.g., "nominal 5% under the working model with documented 7–15% one-sided size and up to 15× tail inflation under strong persistence/left-skew") — explicitly rejected by the current adjudication; only an Owner decision could override it.
3. **A scoped, pre-outcome, independently-attacked admissible-domain design**: define the domain by a *locked* operational rule whose cutoff is chosen by a bounded pre-outcome power/size design task (not by one reviewer's example values), state exactly which score-process shapes are excluded, and require the gate to fail closed (IE). This review judges that no such cutoff currently has independent justification (§8.1), so this path carries a high risk of reproducing the rejected "reviewer example band" pattern; it must not be adopted merely to unblock.
4. **Accept the IE-only v1**: lock a profile whose inference is explicitly "the 6-month cohort cannot resolve the sign with a defensible strong-FWER claim; per-hypothesis PASS is not available at v1 cohort lengths; acceptance evidence is deferred to future Shadow/Forward or a longer new wave." This is fully protocol-consistent, honest, and is the default consequence of this review.

Recommended default: **option 4** (IE-only v1, protocol-consistent), with option 1 as the only path that can restore a positive-acceptance capability — and option 1 is an Owner-gated frozen-semantics decision, not an implementation choice.

---

## 21. CRITICAL / HIGH SUMMARY

```text
CRITICAL = 2
  C-1  No defensible per-hypothesis inference exists at D=117/126 for the general
       evidence domain under the frozen constraints -> NO_LOCKABLE_V1_INFERENCE.
  C-2  The wild-bootstrap calibration of the SN statistic (the natural no-knob fix)
       is empirically anti-conservative in the same regimes; a bootstrap of the same
       statistic inherits the same finite-sample defect (new falsification).

HIGH = 3
  H-1  The admissible-domain gate cannot be given non-arbitrary cutoffs; "guarded SN"
       is not operational without circularity or reviewer-example-style thresholds.
  H-2  Alternative families (block bootstrap, weekly grouped, subsampling) each fail on
       size, resolution, or a block-length/between-block-dependence knob -> no replacement
       can be named.
  H-3  D=242 (one year) does not cure left-skew (size ~0.09) or strong persistence
       (size ~0.10); a longer window is necessary but not sufficient.

FROZEN_PROTOCOL_CONFLICT = NO
NO_CANDIDATE_OUTCOME_DATA_USED = YES
PROFILE_0_4_DRAFTABLE = NO
```

## 22. FINAL DECISION

```text
RECOMMENDATION            = NO_LOCKABLE_V1_INFERENCE
RECOMMENDED_METHOD        = NONE (no defensible replacement at the frozen cohort lengths)
PROFILE_0_4_DRAFTABLE     = NO
CRITICAL                  = 2
HIGH                      = 3
FROZEN_PROTOCOL_CONFLICT  = NO
NO_CANDIDATE_OUTCOME_DATA_USED = YES
```

This review is advisory and resolves the inference question only. It does not modify candidate 0.3, `CURRENT_STATE`, any frozen authority, production code, or tests. `main` was not pushed.


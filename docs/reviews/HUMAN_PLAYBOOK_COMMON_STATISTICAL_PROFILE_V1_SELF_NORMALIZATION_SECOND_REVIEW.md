# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_SELF_NORMALIZATION_SECOND_REVIEW

> Date: 2026-08-19
> Role: `SECOND_INDEPENDENT_STATISTICAL_FALSIFICATION_REVIEWER`
> Worktree: `kline-playbook-engine-sn-falsification-r03` (isolated, from `origin/main` `6823d8f`)
> Branch: `parallel/stat-profile-sn-falsification-r03`
> Review target: `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE.md` (v1.0-revision-candidate-0.3)
> Support script: `docs/reviews/support/stat_profile_sn_r03_falsification.py`
> Frozen authority unchanged: Research Protocol v1.0 + frozen 12/6/6 chronology + Selection Firewall requirements

```text
INDEPENDENCE_ATTESTATION = SECOND_REVIEWER_LANE / NO_CROSS_LANE_READ
NO_CANDIDATE_OUTCOME_DATA_USED = YES
FROZEN_PROTOCOL_CONFLICT = NO
VERDICT = GO_WITH_REQUIRED_CHANGES
CRITICAL_COUNT = 1
HIGH_COUNT = 1
MEDIUM_COUNT = 4
LOW_COUNT = 3
CANDIDATE_LOCKABLE = NO
```

This is the second independent review lane, focused exclusively on the statistical mathematics,
self-normalization, pivotal calibration and short-sample falsification of revision candidate-0.3.
It does not read, cite or await any other targeted review lane's product; it does not adjudicate
the candidate's numeric choices; it does not modify the candidate, any frozen authority, the
candidate evidence, production `src/`, `tests/`, `CURRENT_STATE.md`, or `00_READ_FIRST.md`.

---

## INDEPENDENCE_ATTESTATION

- I worked only in the isolated worktree `kline-playbook-engine-sn-falsification-r03` created from
  `origin/main` @ `6823d8f73d69def126e22482960e00b85543f570`.
- I did not read or reference any other reviewer lane's branch/worktree product
  (e.g., `parallel/stat-profile-delta-review-r03`, `parallel/stat-profile-review`), and I did not
  search for unreviewed branches.
- Verdict and severity levels below are derived independently from the authorities listed in
  `AUTHORITY_READ`, the primary literature, and my own math + synthetic simulation.

## NO_CANDIDATE_OUTCOME_DATA_USED

```text
REAL_HUMAN_PLAYBOOK_RUN=NO
CANDIDATE_PNL_INSPECTION=NO
RETURNS_INSPECTION=NO
EXPECTANCY_INSPECTION=NO
WIN_LOSS_INSPECTION=NO
SHARPE_INSPECTION=NO
EQUITY_INSPECTION=NO
DRAWDOWN_INSPECTION=NO
VALIDATION_ACCESS=NO
HISTORICAL_FINAL_HOLDOUT_ACCESS=NO
THRESHOLD_TUNING_ON_CANDIDATE_OUTCOMES=NO
CANONICAL_MARKET_RETURN_CALIBRATION=NO
```

All quantitative work used algebra, primary literature, and synthetic stochastic fixtures only
(see `SYNTHETIC_TEST_MATRIX`). No parameter, threshold or critical value was tuned to make any
fixture pass; all thresholds are pre-registered in the support script.

## FROZEN_PROTOCOL_CONFLICT

`NO`. The candidate does not change Research Protocol v1.0, the frozen 12/6/6 chronology, Human
Playbook First, PRIMARY/wave/multiplicity semantics, or access state. The review found no required
fix that forces a frozen-semantics change.

## VERDICT

`GO_WITH_REQUIRED_CHANGES`.

The core inference construction (daily score + Shao-style scalar self-normalization + signed
Brownian pivot) is mathematically sound: the pivotal law is correctly stated, the corrigendum
reading is correct for the linear sample-mean case, and the candidate's smoke-test critical value
(`q95 ≈ 5.335`) is independently confirmed to be the correct one-sided 5% threshold. Finite-sample
size is acceptable under IID, moderate serial dependence (rho ≤ 0.5), heavy tails, ARCH,
sparse/bursty event processes, week-clustering and single extreme shocks, and conservative under a
variance-regime break.

However, the candidate is **not lockable as-is** because:

1. **(CRITICAL)** The daily-score test targets the **count-weighted mean** `E[S_d]/E[C_d]`, which
   equals the declared equal-weight per-trade estimand `E[r_i]` (§3.3) **only under
   count–return independence** — an unstated assumption. Under a plausible positive correlation
   between daily event count and the day's per-trade return level, my synthetic null test rejects
   at **73% (strong) / 13% (mild)** at D=117 while the per-trade mean is exactly zero.
2. **(HIGH)** Strong persistence in the daily score inflates size at six-month lengths:
   AR(1) rho=0.80 → ~6.6–7.0%, rho=0.95 → ~12–13% at D≈117–126 (nominal 5%). The candidate
   acknowledged the residual risk; the required fail-closed/diagnostic boundary is not yet defined.

These two items are `REQUIRED_DEFECT_FIX` and must be resolved before profile lock. The remaining
findings are required editorial/implementation pinning (M-1..M-4) or advisory (L-1..L-3).

## AUTHORITY_READ

- `AGENTS.md`, `OWNER_COLLABORATION_CONTRACT.md`, `CURRENT_STATE.md`, `RESEARCH_DIRECTION.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`
- `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE.md` (review target)
- `docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_EVIDENCE.md`
- Historical background only (not replacement authority): `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md`,
  `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADVERSARIAL_REVIEW.md`

## PRIMARY_LITERATURE_READ

- **Shao, X. (2010).** "A Self-Normalized Approach to Confidence Interval Construction in Time
  Series." *JRSS-B* 72(3), 343–366. DOI `10.1111/j.1467-9868.2009.00737.x`. Bibliographic identity
  verified via Crossref; abstract confirms: asymptotically distribution-free self-normalized
  statistic, normalizing matrix from recursive estimates, no user-chosen smoothing parameter, and
  stationary-time-series scope.
- **Shao, X. (2010).** "Corrigendum: A Self-Normalized Approach to Confidence Interval Construction
  in Time Series." *JRSS-B* 72(5), 695–696. DOI `10.1111/j.1467-9868.2010.00754.x`. Existence and
  bibliographic identity verified via Crossref.
- **Holm, S. (1979).** "A Simple Sequentially Rejective Multiple Test Procedure." *Scand. J.
  Statist.* 6(2), 65–70. (FWER step-down; no independence requirement.)
- **Romano, J.P. & Wolf, M. (2005).** *Econometrica* 73(4), 1237–1282. (Corrected interpretation:
  resampling stepdown for a family, not argmax-only.)

Note: full text of the two Shao papers is paywalled; the corrigendum's precise wording was not
directly retrievable. The candidate's description of the corrigendum (Assumptions 1–2 insufficient
for the general theorem; strengthened remainder condition) is consistent with the known
literature and with the independent math in `MATHEMATICAL_FINDINGS`, where the linear sample-mean
remainder is identically zero.

---

## MATHEMATICAL_FINDINGS

### Estimand and daily-score representation

- Declared estimand (§3.3): `theta = E[r_i]`, equal weight per completed round trip after notional
  normalization; `theta_hat = sum_i r_i / N`.
- Daily-score representation (§6): `C_d = # eligible round trips exiting on d`, `S_d = sum of r_i
  exiting on d`, `theta_hat = sum_d S_d / sum_d C_d`. Because `C_d` is a **count**, `sum_d C_d = N`
  and `sum_d S_d = sum_i r_i`, so the sample estimate is exactly the equal-weight mean. The
  document is internally consistent (equal weight per trade, **not** notional-weighted).
- `Z_d(theta0) = S_d − theta0·C_d` is **exactly linear** in the data, so testing
  `E[Z_d(theta0)] = 0` is a valid linearized test of the ratio null `E[S_d]/E[C_d] = theta0`
  without delta-method remainder terms. This is the correct and elegant way to avoid the
  classical ratio-estimator nonlinearity.

### Critical mathematical gap (CRITICAL)

`E[Z_d(theta0)] = E[S_d] − theta0·E[C_d]`, and by iterated expectation
`E[S_d] = E[C_d · E[r_i | C_d]]`. Therefore `E[Z_d(theta0)] = 0` at `theta0 = E[r_i]` **only if**
`E[C_d · E[r_i | C_d]] = E[C_d]·E[r_i]`, i.e., **only if the daily event count `C_d` is
uncorrelated with the day's per-trade return level** `E[r_i | C_d]`. Otherwise the test's effective
null is the **count-weighted mean** `E[C_d·E[r_i|C_d]]/E[C_d]`, which differs from the declared
per-trade estimand `E[r_i]`.

- The candidate's §6.2 justification ("If the ratio estimand equals theta0 and the long-run mean
  daily trade count is positive, then the population mean of Z_d is zero") correctly characterizes
  the **ratio** estimand but does **not** connect that ratio to the declared per-trade estimand.
  The connecting condition (count–return independence) is unstated.
- Consequence: if a playbook trades more on days with more favorable average per-trade returns,
  the daily-score test can massively over-reject the null that the per-trade mean is zero.
- Synthetic confirmation (per-trade mean exactly zero by construction):
  - strong count–return corr (a=0.7,b=0.5): `E[Z_d]=+0.45`, one-sided 5% rejection = **0.73** (D=117);
  - mild (a=0.3,b=0.2): `E[Z_d]=+0.065`, rejection = **0.13** (D=117);
  - weak (a=0.1,b=0.05): `E[Z_d]=+0.005`, rejection = 0.053 (fine).
  - The effect is monotone and grows with D (0.73→0.76→0.93→0.99 at D=117/126/242/500).
- This is not a finite-sample artifact; it is a systematic mismatch between the tested quantity and
  the declared estimand. Severity: **CRITICAL** — it affects the statistical validity of the
  primary acceptance test and therefore lockability.
- Minimum required fix (designer's choice, not selected here): (a) explicitly state the
  count–return-independence assumption and a deterministic pre-registered count–return dependence
  diagnostic that fail-closes (`INSUFFICIENT_EVIDENCE`/`DATA_BLOCKED`) when the dependence is
  material; or (b) re-pin the estimand as the count-weighted/day-aggregated quantity in §3.3 and
  justify it; or (c) adopt a count-robust test at the trade level. Option (a) is the smallest
  change that preserves the candidate's structure.

### Zero-exit days

`(S_d, C_d) = (0,0)` days enter the full authoritative sequence. Asymptotically these contribute
the `−rB(1)` tilt in the partial-sum pivot, which is handled correctly; finite-sample sparse
simulations (Poisson λ=0.2, 0.5) show size ≈ 4.6–5.4%, so including zero days is correct and is
not a defect. Confirmed.

### Same-day cross-product / multi-trade aggregation

Aggregating all exits on a trading day into one `Z_d` preserves same-day contemporaneous
dependence (all products in one day move together in the partial-sum process). Week-cluster
simulation (J) shows acceptable size, so this aggregation is reasonable for the dependence
representation. Confirmed.

### Entry-notional weighting (item E of the review task)

The document uses `C_d = count` and `S_d = sum of r_i` (already notional-normalized per trade),
so the estimand stays equal-weight per round trip. A PnL/notional variant
(`S_d = Σ net realized PnL`, `C_d = Σ entry notional`) would be a different, notional-weighted
estimand and must **not** be silently substituted. See finding M-3.

---

## CORRIGENDUM_FINDINGS

- The corrected remainder condition in the corrigendum concerns the **general** (nonlinear)
  parameter case of Shao's Theorem. For the candidate's direct scalar sample mean of the daily
  score, the statistic is exactly linear in `Z_d`, so the linearization remainder is **identically
  zero** and the strengthened remainder condition is trivially satisfied. The candidate's reading
  is correct.
- The nontrivial assumptions remain and are **not** provable from a six-month cohort:
  stationarity of the daily score process; weak dependence / FCLT behavior; finite moments;
  **positive long-run variance**; no structural break at the mean; and (for the test's validity
  for the declared estimand) count–return independence (finding CRITICAL).
- The candidate already states these are assumptions of the method, not certified facts. That is
  honest and correct. What is missing is a **fail-closed boundary** for the cases where the
  assumptions visibly fail in-sample (persistence; count–return dependence).

## PIVOTAL_CALIBRATION_FINDINGS

- The signed limiting pivotal is correctly stated:
  `T_infinity = B(1) / sqrt(∫₀¹(B(r)−rB(1))²dr)`, symmetric, with `T_infinity² = U_1`
  (the Brownian-bridge L2 norm in the denominator; `B(r)−rB(1)` is a standard Brownian bridge,
  independent of `B(1)`). Confirmed by first principles.
- **Independent calibration** (200,000 Brownian paths, 500-step grid, seed 20260819):
  - signed-T quantiles: p=0.90 → 3.889; **p=0.95 → 5.331**; p=0.975 → 6.723; p=0.99 → 8.604.
  - `P(T ≥ 5.336) = 0.0499` ⇒ the candidate's smoke-test `q95 = 5.335` **is** the correct
    one-sided 5% threshold. No calibration-level defect. (The commonly-misremembered
    "U_1 95% ≈ 28.5" is in fact the **90%** quantile of U_1 = 5.33² ≈ 28.4; the 95% quantile of
    U_1 is 6.72² ≈ 45.2. An implementer must use the **signed** pivot CDF as specified, not a
    `U_1`/`|T|` table, to avoid an anti-conservative factor-of-two error.)
- One-sided p-value: `p_plus = P(T_infinity ≥ T_SN(0))` (upper tail of the signed pivot) — correct
  direction for the positive-edge null (reject for large positive `T_SN`). Lower/upper one-sided
  bounds and two-sided interval are obtained by deterministic inversion of `T_SN(theta0)` against
  the same signed CDF; because `V_D(theta0)` depends on `theta0`, numeric bracket/root inversion is
  required (candidate says this). Direction of inversion verified: `T_SN(theta0)` is decreasing in
  `theta0`, `p_plus(theta0)` is increasing, so the lower bound solves `p_plus = α` and the upper
  bound solves `p_plus = 1−α` — correct.
- **Monte Carlo tail resolution is a hard limit at small Holm alpha.** For the smallest Holm
  threshold `α/M`, the calibration must resolve tails of size `α/M`. For M=20 → 0.0025; the
  "plus-one" formula `(1 + #exceedances)/(B+1)` is correct and must be used. B must be sized so the
  MC standard error at `α/M` is acceptable (≈10–20% relative): B ≈ 10⁵–10⁶ for M=20–50. The
  candidate's list of artifact fields is good and must additionally pin: the B-vs-M sizing rule,
  the full signed empirical CDF (sorted draws) or a high-resolution tail grid, and the MC error
  budget at `α/M`. See finding M-2.

## SYNTHETIC_TEST_MATRIX

All size runs: nominal one-sided 5%, threshold = correct signed-pivot 5% value (5.331, from Part 0);
R = 5,000 per cell; MC SE ≈ `sqrt(0.05·0.95/5000) ≈ 0.0031`; fixed seed 20260819. D = authoritative
trading days (117 = VALIDATION H1-2025, 126 = FINAL H2-2025, 242 = DEVELOPMENT 2024, 500 = asymptotic
reference). Support script: `docs/reviews/support/stat_profile_sn_r03_falsification.py`.

| # | process | 117 | 126 | 242 | 500 |
|---|---------|------|------|------|------|
| A | iid Gaussian | 0.0454 | 0.0502 | 0.0540 | 0.0536 |
| B | AR(1) rho=0.20 | 0.0476 | 0.0522 | 0.0558 | 0.0544 |
| B | AR(1) rho=0.50 | 0.0532 | 0.0570 | 0.0588 | 0.0558 |
| B | AR(1) rho=0.80 | **0.0656** | **0.0700** | **0.0658** | 0.0586 |
| B | AR(1) rho=0.95 | **0.1298** | **0.1200** | **0.0984** | 0.0696 |
| C | Student-t df=5 | 0.0498 | 0.0470 | 0.0488 | 0.0492 |
| C | Student-t df=3 | 0.0488 | 0.0454 | 0.0458 | 0.0418 |
| C | Student-t df=2 (infinite variance) | 0.0448 | 0.0446 | 0.0494 | 0.0450 |
| D | ARCH(1) (α=0.5) | 0.0436 | 0.0496 | 0.0526 | 0.0502 |
| E | sparse Poisson λ=0.5 | 0.0532 | 0.0540 | 0.0524 | 0.0488 |
| E | sparse Poisson λ=0.2 | 0.0474 | 0.0518 | 0.0496 | 0.0456 |
| F | bursty (2-state Markov counts) | 0.0508 | 0.0490 | 0.0478 | 0.0516 |
| G | count–return correlation | **0.7302** | **0.7578** | **0.9318** | **0.9936** |
| H | variance regime break (1→3) | 0.0242 | 0.0238 | 0.0254 | 0.0248 |
| I | 1 extreme shock (±12σ) | 0.0464 | 0.0410 | 0.0470 | 0.0522 |
| J | week-cluster (common within-week factor) | 0.0546 | 0.0562 | 0.0530 | 0.0490 |

## FINITE_SAMPLE_RESULTS

- **Cross-validation:** IID n=117 reproduces the candidate's smoke value 0.0454 exactly; AR(1)
  rho=0.80–0.85 trend matches the candidate's 0.0838 at rho=0.85. The candidate's smoke test is
  confirmed reproducible.
- **Well-calibrated (acceptable):** IID; AR(1) rho ≤ 0.5; heavy tails (t3/t5, and even t2 with
  infinite variance — the self-normalizer is ratio-robust); ARCH; sparse Poisson (λ=0.2, 0.5);
  bursty counts; week-clustering; single extreme shock. All within ~±1–2 SE of 5%.
- **Conservative:** variance-regime break → ~2.4% (under-rejection, a power loss, not a false-positive risk).
- **Size inflation (HIGH):** AR(1) rho=0.80 → 6.6–7.0%; rho=0.95 → **12–13%** at D≈117–126; decays
  to ~7% at D=500. Strong persistence is the dominant finite-sample failure mode, exactly as the
  candidate flagged, and is worse at the upper end than the candidate's smoke (which stopped at
  rho=0.85 → 8.4%).
- **Size collapse / estimand drift (CRITICAL):** count–return correlation → 73–99% rejection while
  per-trade mean is zero (see MATHEMATICAL_FINDINGS and the supplementary run below).

### Supplementary count–return mechanism check (D=117, R=4,000, threshold 5.331)

| parameters | E[Z_d] (mean daily score) | one-sided 5% rejection |
|---|---|---|
| a=0.7, b=0.5 | +0.4492 | 0.7265 |
| a=0.3, b=0.2 | +0.0651 | 0.1298 |
| a=0.1, b=0.05 | +0.0049 | 0.0532 |

`E[r_i]=0` by construction in every row; the inflation is driven by `E[Z_d] ≠ 0` (count-weighted
mean ≠ per-trade mean).

## POWER / DETECTABILITY (synthetic standardized alternatives, R=2,000)

One-sided 5%, threshold 5.331. "σ" = per-day-score sigma for direct processes; per-trade sigma for
sparse (total trades ≈ λ·D).

| process | D | 0.1σ | 0.2σ | 0.3σ |
|---|---|---|---|---|
| IID | 117 | 0.248 | 0.576 | 0.835 |
| IID | 126 | 0.255 | 0.588 | 0.849 |
| IID | 242 | 0.378 | 0.820 | 0.973 |
| AR(1) rho=0.5 | 117 | 0.135 | 0.263 | 0.434 |
| AR(1) rho=0.5 | 126 | 0.142 | 0.266 | 0.445 |
| AR(1) rho=0.5 | 242 | 0.177 | 0.389 | 0.637 |
| AR(1) rho=0.9 | 117 | 0.107 | 0.127 | 0.149 |
| AR(1) rho=0.9 | 126 | 0.103 | 0.122 | 0.145 |
| AR(1) rho=0.9 | 242 | 0.095 | 0.118 | 0.145 |
| sparse Poisson λ=0.5 | 117 | 0.165 | 0.361 | 0.596 |
| sparse Poisson λ=0.5 | 126 | 0.180 | 0.384 | 0.617 |
| sparse Poisson λ=0.5 | 242 | 0.238 | 0.559 | 0.831 |

Findings:
- At D≈117–126, the method detects ~0.3σ edges with ~0.83 power (IID), ~0.43–0.45 (moderate
  dependence), ~0.15 (strong dependence rho=0.9). Small edges (≤0.2σ) are detected only weakly.
- Strong persistence simultaneously inflates size and destroys power — the worst combination.
- Sparse event processes (λ=0.5) sit between IID and moderate-dependence power.
- **Low power ≠ no edge.** A playbook with a real but small edge will frequently return
  `INSUFFICIENT_EVIDENCE` in a 6-month cohort; the candidate's `INSUFFICIENT_EVIDENCE` semantics
  are consistent with this capacity reality. This is a capacity statement, not evidence against a
  playbook, and the candidate says so correctly.

## MULTIPLICITY_FINDINGS

- `ERROR_RATE_TARGET = strong FWER ≤ 0.05`; family = `ResearchWaveManifest.tested_hypothesis_test_ids`;
  counting unit = one `hypothesis_test_id`. This is machine-consistent with the firewall.
- Counting taxonomy is conservative and sound: separately outcome-inspected parameter points,
  outcome-tested alternatives, and independently decidable scope variants are each counted; a
  shared `parameter_search_identity` is explicitly not laundering-safe. FAIL/INSUFFICIENT/DATA_BLOCKED
  remain permanently in the denominator. Confirmed.
- **Holm is sufficient for v1** as the minimum reliable scheme: it strongly controls FWER under
  arbitrary dependence, is deterministic, and is auditable. Romano-Wolf is not required for v1
  (it may be more powerful under correlation but adds a resampling implementation; it remains a
  documented later refinement). No requirement to adopt it.
- Validity caveat (prerequisite, not a new defect): Holm is valid **conditional on** the per-
  hypothesis p-values being valid. The CRITICAL (count–return) and HIGH (persistence) per-
  hypothesis issues therefore must be fixed before Holm inherits validity. Holm does not rescue
  miscalibrated individual p-values.

## PASS_FAIL_INSUFFICIENT_FINDINGS

- Decision states and fixed order (DATA_BLOCKED → INTEGRITY_FAIL → INSUFFICIENT_EVIDENCE →
  FAIL → PASS) are coherent and align with the adjudication (H-4).
- FAIL semantics: "Holm does not reject AND unadjusted one-sided 95% upper bound ≤ 0 → FAIL".
  This does require the support floors (S1–S4) to have passed, so FAIL is not merely
  "not significant". A mildly negative or unresolved-sign cohort returns INSUFFICIENT_EVIDENCE.
  Sound.
- **Asymmetry (MEDIUM, M-1):** PASS uses **Holm-adjusted** p-values while FAIL uses the
  **unadjusted** one-sided 95% upper bound. Because Holm lowers the effective per-hypothesis
  level to α/(M−i+1), a hypothesis can be non-significant for PASS (adjusted) while its unadjusted
  upper bound is also ≤ 0, making FAIL easier to reach than PASS in multiplicity-adjusted terms.
  This is defensible for v1 (FAIL is a per-hypothesis negative conclusion; Holm protects against
  false PASS, and false-negative control is not Holm's purpose), but the asymmetry must be
  **explicitly stated and justified in the locked profile**. The alternative — using a
  multiplicity-consistent (simultaneous) upper bound for FAIL — is stricter and more symmetric but
  not required for v1. Required: document the asymmetry; do not silently mix levels.

## ROBUSTNESS_FINDINGS

- LOTO/LOWO sign robustness: deterministic, address the real "one trade / one narrow window
  carries the sign" failure mode, and replace arbitrary concentration percentages. **Keep as hard
  acceptance guards** (returning INSUFFICIENT_EVIDENCE, not FAIL) for v1.
- They are **not calibrated statistical tests** (no distributional claims) and should be labeled as
  such. At small N (e.g., 20) LOTO gives each trade ~1/N leverage, so LOTO/LOWO create **implicit
  breadth requirements** that overlap the N≥20 / weeks≥6 floors and the self-normalized test; the
  interaction should be documented. They are not redundant with the SN test (the SN test does not
  specifically isolate a single-trade sign flip), so they add value.
- No candidate-outcome calibration was used in assessing them (forbidden and unnecessary).

## SUPPORT FLOORS (labels per review task)

| Floor | Label | Rationale |
|---|---|---|
| N_completed ≥ 20 | **C (governance-only heuristic)** | No statistical law; the SN test's own low power is what prevents "few trades = strong evidence". 20 is not a CLT/power threshold. Correctly labeled by the candidate. |
| active_exit_weeks ≥ 6 | **C (governance, mild algorithmic flavor)** | Prevents concentration in a few clusters; but 6 is arbitrary. Not a statistical law. |
| right_censored == 0 | **B/C (algorithmic/governance strictness)** | Prevents completion bias without inventing a censoring model (defensible), but will systematically yield INSUFFICIENT_EVIDENCE for multi-day playbooks whose positions span cohort boundaries. This coverage consequence should be stated in the profile. |
| V_D(0) finite and > 0 | **B (algorithmically necessary)** | Division guard; nondegeneracy, not a sufficiency claim. |
| locked calibration artifact present | **B (algorithmically necessary) / C (governance)** | Infrastructure; missing → DATA_BLOCKED (correct). |

No floor is `mathematically necessary` (A), none is `redundant` (D) in a harmful sense, none is
`harmful` (E). The candidate's labeling of 20/6 as reviewable governance floors is accurate and
must be preserved.

## MINIMUM_REQUIRED_CHANGES (REQUIRED_DEFECT_FIX — not optional)

1. **[CRITICAL] Count–return dependence.** Candidate §6.1–6.2. Add an explicit statement of the
   count–return-independence condition and a deterministic pre-registered count–return dependence
   diagnostic with a fail-closed boundary (`INSUFFICIENT_EVIDENCE`/`DATA_BLOCKED`) when the
   dependence is material — or, as the designer's alternative, re-pin §3.3's estimand as the
   count-weighted/day-aggregated quantity and justify it. Without this, the test can reject a
   true-null per-trade mean at 13–73% (D=117) under plausible count–return correlation.
2. **[HIGH] Persistence fail-closed boundary.** Candidate §6/§15.3. Add a pre-registered
   persistence diagnostic on the daily score (e.g., AR(1)-style estimate or a simple lag-1
   autocorrelation with a pre-registered threshold) that fail-closes (INSUFFICIENT_EVIDENCE /
   DATA_BLOCKED) for strongly persistent score processes, given measured size inflation to
   12–13% at rho=0.95 and 6.6–7% at rho=0.80 over six-month lengths.
3. **[MEDIUM, required editorial] FAIL/PASS multiplicity asymmetry.** Candidate §11 Step 4.
   Explicitly state and justify that PASS uses Holm-adjusted p-values while FAIL uses an
   unadjusted one-sided 95% upper bound, or switch FAIL to a multiplicity-consistent bound.
4. **[MEDIUM, required implementation pin] Pivotal calibration artifact.** Candidate §6.4. Pin
   B-vs-M sizing (B large enough that MC SE at α/M ≈ 10–20% relative), store the full signed
   empirical CDF (or a high-resolution tail grid), use `(1 + #exceedances)/(B+1)`, use the signed
   pivot CDF (not a U_1/|T| table — quantile-mix trap documented above), and record algorithm
   version, RNG, seed, grid, B, MC error policy, and SHA256.
5. **[MEDIUM, required pin] C_d = count, not notional.** Candidate §6.1. Pin `C_d` as the round-
   trip count and `S_d` as the sum of per-trade net returns; explicitly forbid the PnL/notional
   variant (a silently different notional-weighted estimand). This also documents the
   review-prompt/document discrepancy so implementers do not drift.

## OPTIONAL_SUGGESTIONS_NOT_AUTHORITY

- Consider a Romano-Wolf stepdown as a later, more powerful refinement under correlation (not
  required for v1; Holm suffices).
- Consider a count-robust trade-level test (e.g., a robust cluster/block procedure at the trade or
  week level) as an alternative to the daily-score route — an option for the designer, not a
  requirement.
- Consider whether `active_exit_weeks ≥ 6` should be revisited once the persistence/robustness
  diagnostics are in place (governance tuning, not a statistical law).
- Keep LOTO/LOWO as hard guards but label them explicitly as non-statistical robustness heuristics.

These are reviewer preferences, not project authority.

## THINGS ALREADY VERIFIED AS CORRECT (to protect against regression)

- Pivotal law statement and `T_infinity² = U_1`; signed-pivot one-sided 5% threshold ≈ 5.33
  (candidate's 5.335 confirmed).
- Corrigendum reading for the linear sample-mean case (remainder exactly zero).
- Ratio-of-means ↔ equal-weight-per-trade sample equivalence (C_d = count).
- Zero-exit-day handling; same-day cross-product aggregation; week-cluster behavior.
- Robustness to heavy tails (including infinite-variance t2), ARCH, sparse/bursty counts, and
  single extreme shocks in the tested null fixtures.
- Holm sufficiency for v1 and the machine-consistent denominator.

## CHECKS

- `git diff --check` clean.
- Full suite unaffected (no `src/`, no `tests/`, no candidate, no frozen authority changed):
  `python -m unittest discover -s tests -v` re-run below.
- Only two files added by this lane: this review and `docs/reviews/support/stat_profile_sn_r03_falsification.py`.

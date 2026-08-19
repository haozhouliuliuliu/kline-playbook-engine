# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_TARGETED_DELTA_REVIEW

> Reviewer role: **INDEPENDENT TARGETED DELTA STATISTICAL REVIEWER** (isolated review worktree)
> Branch: `parallel/stat-profile-delta-review-r03`
> Date: 2026-08-19
> Reviewed package: `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE.md` (`v1.0-revision-candidate-0.3`) at `6823d8f73d69def126e22482960e00b85543f570`
> Companion evidence: `docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_EVIDENCE.md`
> Scope: **targeted delta review only** — attack materially changed statistical definitions (A–J in the task), not a full-project review.

```text
REVIEW_VERDICT             = GO_WITH_REQUIRED_CHANGES
CRITICAL                   = 1
HIGH                       = 2
MEDIUM                     = 4
LOW                        = 4
FROZEN_PROTOCOL_CONFLICT   = NO
CANDIDATE_LOCKABLE         = YES (after the required changes in §8)
NO_CANDIDATE_OUTCOME_DATA_USED = YES
BLOCKER                    = C-1 (self-normalized p-value validity / error-rate guarantee)
```

---

## 1. Independence attestation

- This review was performed in an isolated worktree (`kline-playbook-engine-delta-review-r03`) on
  branch `parallel/stat-profile-delta-review-r03` created from `origin/main` (`6823d8f`). `main`
  was not pushed or modified. No existing worktree/user file was deleted, reset, or overwritten.
- The reviewer did **not** read the parallel `INDEPENDENT_ADVERSARIAL_REVIEW` conclusions as
  authority; that document and the first candidate are treated as **historical context only**
  (the task explicitly forbids treating the prior reviewer's `RECOMMENDED_SIMPLIFIED_V1`, N>=60,
  thresholds, 2x cost, Holm, block formulas, volatility examples, or ESS replacements as accepted
  authority).
- The revision candidate, `CURRENT_STATE`, frozen Protocol v1.0, frozen 12/6/6, production code,
  and tests were **not modified**. This is review only.
- No real Human Playbook candidate was run; no candidate PnL / equity / expectancy / Sharpe /
  win-loss was inspected or generated; VALIDATION and the historical final holdout were **not**
  accessed; no canonical market price/outcome series was used for calibration. All quantitative
  work used synthetic random fixtures (deterministic seed) and algebra only.
- The prior reviewer's rejected `RECOMMENDED_SIMPLIFIED_V1` and its numbers are **not** treated as
  authority here; every numerical conclusion in this review is derived independently.

## 2. Files / authority read

Authority (binding):
- `AGENTS.md`, `00_READ_FIRST.md`, `OWNER_COLLABORATION_CONTRACT.md`, `ARCHITECTURE_BASELINE.md`,
  `CURRENT_STATE.md`, `RESEARCH_DIRECTION.md`, `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`,
  `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`,
  `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`,
  `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`,
  `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`,
  `docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md`,
  `docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ENGINE_COMPATIBILITY_CROSSWALK.md`.

Primary review targets:
- `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE.md`
- `docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_EVIDENCE.md`

Historical context only (NOT authority for replacement rules):
- `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md`
- `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADVERSARIAL_REVIEW.md`

Code inspected (as needed for engine compatibility, §7):
- `src/research_firewall.py`, `src/validation_runner.py` (grep/read for `position_id`,
  `realized_pnl_change`, `position_trading_day`, `SessionMetadata.trading_day_at`,
  `_apply_capital_constraints`, mark/liquidation facts).

Primary statistical source verified:
- Xiaofeng Shao, *A Self-Normalized Approach to Confidence Interval Construction in Time Series*,
  JRSS-B 72(3):343–366 (DOI 10.1111/j.1467-9868.2009.00737.x); **corrigendum** JRSS-B
  72(5):695–696 (DOI 10.1111/j.1467-9868.2010.00754.x). Both paper and corrigendum, plus the
  author's "arXiv version (with correction)", are listed on Xiaofeng Shao's official University of
  Illinois page (publish.illinois.edu/xshao/publications/). Method facts used in this review are
  the standard fixed-b/self-normalized scalar-mean pivot (see §5B).

## 3. Review verdict

**GO_WITH_REQUIRED_CHANGES.** The revision direction is materially improved and the math of the
core method is correct, but the profile cannot be locked as-is: the self-normalized one-sided
p-values that feed Holm are **anti-conservative under realistic daily-score shapes** (left-skew
and strong persistence), and this is **worse at the Holm-relevant tail** — so the stated
`strong FWER <= 0.05` target (§8.1 of the candidate) is not honestly achieved. That is the single
CRITICAL. Two HIGHs (zero right-censoring consequence; confidence-bound inversion uniqueness) and
four MEDIUMs must also be pinned before lock. All required changes are inside the not-yet-frozen
profile; none touch frozen Protocol v1.0 / 12/6/6 semantics.

## 4. Severity counts

```text
CRITICAL = 1   C-1
HIGH     = 2   H-1, H-2
MEDIUM   = 4   M-1, M-2, M-3, M-4
LOW      = 4   L-1, L-2, L-3, L-4
```

## 5. Mathematical / statistical findings

### A. Estimand / daily score — VERDICT: CORRECT (one wording fix, LOW)

- **Representation check.** With `C_d` = count of completed round trips exiting on day d and
  `S_d` = sum of their net returns, the estimator
  `theta_hat = sum_d S_d / sum_d C_d` is a **ratio-of-means** estimator. In the population limit
  (LLN for a stationary count/return process with `E[C_d] > 0`),
  `E[S_d]/E[C_d] = E[C_d * rbar_d]/E[C_d]`, which is exactly the **count-weighted per-trade mean**
  — i.e., the per-trade expectation over the random draw of a trade. This identity holds **even
  when daily event counts are stochastic and correlated with return shocks**. Therefore the
  candidate's §6.2 statement is correct: `E[Z_d(theta0)] = E[S_d] - theta0*E[C_d] = 0` at
  `theta0 = theta`, and the boundary test `Z_d(0) = S_d` is a valid test of `theta <= 0`
  (sign-equivalent to the per-trade mean when `E[C_d] > 0`). **No hidden stochastic-count error in
  the point estimator.**
- **Zero-exit days / same-day clustering / product correlation.** Zero-exit days are correctly
  retained as `(S_d,C_d)=(0,0)`; the compound daily score automatically pools same-day,
  cross-product clustering (no per-product pseudo-independence). This is correct and simpler than
  the first candidate.
- **Wording fix (LOW, L-1):** §3.3 writes `theta = E[sum of net normalized round-trip returns /
  number of round trips]`. This is loose. State the estimand precisely as the ratio of
  expectations `theta = E[S_d]/E[C_d]` (the count-weighted per-trade mean), which is what
  `theta_hat` estimates. The math is right; the sentence invites misreading as an average of a
  random ratio.

### B. Self-normalization — VERDICT: FORMULAS CORRECT; ASSUMPTIONS NON-CERTIFIABLE (C-1, M-4)

- **Formula verification.** The candidate's scalar self-normalizer matches Shao (2010) for the
  sample mean exactly:
  `A_t = sum_{j<=t}(Z_j - Z_bar)`, `V_D = D^-2 sum_t A_t^2`,
  `T_SN = sqrt(D) Z_bar / sqrt(V_D)`, with limiting law
  `T_inf = B(1)/sqrt(int_0^1 (B(r) - r B(1))^2 dr)`. The signed pivot is symmetric; its square is
  the `U_1` law of Shao (2010). Verified.
- **Corrigendum claim.** The candidate claims the direct sample-mean score makes the corrigendum's
  strengthened remainder condition trivial. This is **correct**: for a purely linear statistic the
  linearization remainder is identically zero; the corrigendum concerned the general (nonlinear)
  case. Verified against the paper/corrigendum record.
- **Remaining assumptions (candidate lists them correctly):** (i) the daily score process
  `Z_d(theta0) = S_d - theta0 C_d` is weakly dependent and satisfies a functional CLT with (ii)
  positive long-run variance, and (iii) sufficient moments. These are **not certifiable** from a
  117–126-day cohort. The candidate states this honestly; the gap is that it provides **no
  operating-characteristics (size) analysis and no fail-closed boundary** for the two regimes that
  my synthetic tests show are anti-conservative (persistence, left-skew) — see **C-1**. 
  Importantly, my tests show structural **variance nonstationarity is conservative** (size
  0.023–0.026, tail 0.001–0.003), so a missing "stationarity gate" is a **power/interpretation**
  issue, not a false-PASS risk — see **M-4**.

### C. Pivotal calibration / p-values / confidence bounds — VERDICT: DEFENSIBLE; PIN MC ERROR POLICY (M-3)

- **Signed pivotal relationship.** `p_plus = P(T_inf >= T_SN(0))` is a valid one-sided p-value for
  `H0: theta <= 0`. The pivot is symmetric, so one-sided upper/lower bounds and the two-sided 95%
  interval are all obtained by deterministic inversion of the **same** signed-pivotal CDF — a
  coherent construction. Verified.
- **Independent calibration check.** With a 1000-step Brownian grid and 200,000 paths (seed
  20260819), I obtain (mean of 5 independent runs): `q95 = 5.327 ± 0.013`, `q97.5 = 6.746 ±
  0.026`, `q99 = 8.614 ± 0.031`, `q99.75 = 11.434 ± 0.118`. The candidate's smoke `q95 = 5.335`
  (500-step grid) is **within Monte-Carlo error** of my value — verified, not decorative.
- **MC error policy (required, M-3):** the candidate lists `MONTE_CARLO_ERROR_POLICY` as a field
  but pins no tolerance. Requirement: the locked artifact must guarantee the empirical-CDF
  standard error at every operating quantile used by Holm (q95 … q99.75, i.e., one-sided levels
  0.05 down to 0.05/M) is ≤ 1e-3 absolute in p (equivalently relative error ≤ ~5% at α and at the
  most stringent Holm threshold), with grid resolution ≥ 1000, replications ≥ 2×10^5, fixed seed,
  and a sha256 identity; runtime must consume the locked artifact only (candidate already says
  this).
- **Smallest defensible replacement / refinement (illustrative, LOW, L-4):** the empirical-CDF
  Brownian-grid approach is acceptable. An alternative that removes grid discretization bias is
  the Karhunen–Loève representation `Q = sum_k chi^2_1/(pi^2 k^2)` with `T = Z/sqrt(Q)`,
  `Z ~ N(0,1) independent`; it is a refinement, not a required replacement.

### D. Synthetic finite-sample falsification — see §6 (full protocol, seeds, replication counts, results)

### E. Sufficiency / censoring — VERDICT: MIXED (keep 20/6/S4; H-1 on censoring)

- **N >= 20 (S1):** defensible as an explicit governance floor ("not a CLT threshold" — candidate
  says this correctly). My sparse-Poisson tests show the floor does **not** materially distort
  size (filtered vs unfiltered differences within Monte-Carlo noise, ~0.005 at R=5000), so it is
  neither harmful nor redundant. KEEP as a governance floor.
- **>= 6 active exit weeks (S2):** defensible breadth floor, deterministic, no knob. KEEP.
- **Nondegenerate normalizer (S4):** necessary; my rare-event tests show `V_D = 0` occurs exactly
  when no events occur in the realized series ((1-p)^n), which correctly routes to
  `INSUFFICIENT_EVIDENCE`. KEEP.
- **Zero right-censoring (S3):** see **H-1**.

### F. PASS / FAIL / INSUFFICIENT_EVIDENCE — VERDICT: COHERENT (subject to C-1; one note, LOW)

The three-way logic — multiplicity-adjusted positive evidence → proceed toward PASS; positive test
does not reject but unadjusted one-sided upper bound ≤ 0 → FAIL; otherwise → INSUFFICIENT_EVIDENCE
— is statistically coherent and consistent with frozen Protocol v1.0 (`INSUFFICIENT_EVIDENCE` is a
frozen legitimate result; `FAIL` requires negative evidence; unresolved sign is IE, not FAIL).
- Note (LOW, L-3): the FAIL path uses the **unadjusted** upper bound while PASS uses
  Holm-adjusted p. This asymmetry is intentional and safe: a false FAIL is a missed opportunity
  (not a false acceptance), so multiplicity control on the rejection direction is not required.
  State this explicitly in the profile so it is not read as an inconsistency.
- The validity of the whole chain rests on the per-hypothesis p-values being valid — which is
  exactly what C-1 attacks.

### G. Robustness (LOTO / LOWO) — VERDICT: KEEP (LOW, L-2)

- **No false-acceptance risk:** both guards only push a would-be PASS to `INSUFFICIENT_EVIDENCE`;
  they never convert a non-rejection into PASS or FAIL. They are conservative by construction.
- **Algebraic property:** `LOTO_MIN_MEAN > 0` iff `max_i r_i < N * mean(r)`; LOWO is the same at
  the week level. So they are deterministic "no single event / no single week carries the whole
  mean" checks with no tuned concentration percentage — a clean replacement for the first
  candidate's R2 and the prior reviewer's unaccepted H-3 threshold.
- **Known property (document, do not change):** their severity scales with N (strict for small N,
  lax for large N), and LOWO is very strong at the S2 minimum (6 active weeks). Both effects only
  cost power (more IE), which is acceptable for a v1 governance instrument. KEEP; add one sentence
  to §9.2 noting the N-scaling property.

### H. Economic materiality / execution friction — VERDICT: DEFENSIBLE (M-1)

- **Removal of the universal 2 bp floor:** defensible. Under realistic per-trade dispersion, any
  statistically significant edge is already far above 2 bp (this was the prior review's C-1
  point), so the floor was a redundant, false-precision knob. Removing it and separating
  materiality (= positive net edge after exact pre-registered base costs) from detectability (the
  §7 envelope) is correct.
- **Removal of the universal 2x hard gate:** defensible in direction — additive fee and fill-price
  slippage are structurally different objects (the crosswalk confirms slippage lives in gross, not
  in the fee term), so a uniform 2x was a false-universal statement. Replacing it with
  base-cost inference + mandatory gross/fee/net diagnostics + fee break-even multiplier + "slippage
  stress = separate identity-bound execution rerun" is coherent and does not invent a new arbitrary
  threshold.
- **Required clarification (MEDIUM, M-1):** because the 2x safety net is gone, the profile must
  explicitly require that the pre-registered base execution/capital/offset-cost assumptions are
  **conservative (validated), not merely pre-registered**, and state that any later finding that
  base costs were optimistic is an outcome-affecting artifact change (new profile lineage), not a
  silent post-outcome repair. The fee-break-even multiplier must stay a mandatory report (it is).

### I. Multiplicity — VERDICT: KEEP Holm; one implementation mapping required (M-2)

- **Error-rate target** `strong FWER <= 0.05` is the correct target for per-playbook consequential
  acceptance. **But** the achieved FWER is bounded by the validity of the per-hypothesis p-values
  — see C-1. Holm itself is the simplest defensible v1 method: strongly controls FWER under
  arbitrary dependence, deterministic, auditable; Romano–Wolf can exploit joint dependence and be
  more powerful for strongly correlated waves but adds a shared-resampling implementation. For v1
  with modest expected wave sizes, **Holm remains the correct simplest choice**; keep the
  corrected Romano–Wolf description (the candidate now states it correctly) as the documented
  upgrade path. No change required here.
- **Denominator** = `len(ResearchWaveManifest.tested_hypothesis_test_ids)` is machine-consistent;
  `FAIL / INSUFFICIENT_EVIDENCE / DATA_BLOCKED` remain in the permanent denominator — correct and
  frozen-consistent.
- **Parameter-point counting (MEDIUM, M-2):** §8.3's rule — "each outcome-inspected parameter
  point is a separately counted hypothesis unless a separately pre-registered within-search
  correction exists" — is the right conservative direction, but it must be mapped to the firewall
  registration model before lock: the firewall binds a parameter grid through
  `parameter_search_identity` on one `hypothesis_test_id`. The profile must state unambiguously
  that (a) `parameter_search_identity` is a **search-identity binding, not a count unit**; (b) each
  outcome-inspected parameter point must be a **separate `hypothesis_test_id` / registration**;
  (c) "inspected" includes **any outcome exposure of the point**, even if only the best point is
  reported (so a grid run that exposes outcomes for 30 points counts 30 unless a within-search
  correction is separately pre-registered — and none is in v1). No frozen semantic changes needed;
  this is profile-level counting taxonomy + implementation mapping.

### J. Engine compatibility — VERDICT: COMPATIBLE (no missing primitive)

Confirmed by code inspection (`src/validation_runner.py`, `src/research_firewall.py`):
- `CapitalSnapshot.position_id` is the deterministic round-trip key (preserved across adds/partial
  closes, regenerated after full close) — matches §3.1.
- `CapitalTransition.realized_pnl_change` is per-order exact realized PnL, separate from
  `charged_costs` — matches §3.2; the cost-source single-source guard is required and present.
- `CapitalSnapshot.position_trading_day` + `SessionMetadata.trading_day_at` are the authoritative
  trading-day path (TD-001 discipline is satisfied by the design).
- Mark-to-market transitions, forced-liquidation requirements, and maintenance-breach facts exist
  and are the correct source for R1 (the design already says to use engine facts, not a
  reconstructed equity path — correct, avoids TD-002).
- The revised design does **not** depend on the missing multi-day portfolio/equity series, and it
  keeps TD-002 out of the primary estimand (realized-level only) and LIMIT-001 as `DATA_BLOCKED`
  (present, §11 Step 0) — all consistent with the capability audit and crosswalk.
- No engine primitive is assumed that does not exist. The round-trip ledger and day/week helpers
  remain small engineering deltas (recorded, not implemented).

---

## 6. Synthetic finite-sample falsification — protocol and results

Reproducibility script: `docs/reviews/support/stat_profile_delta_review_synthetic.py` (committed
with this review). **Dependency: numpy only** (documented). Deterministic seed
`np.random.default_rng(20260819)`. Calibration: 200,000 Brownian paths, 1000-step grid. Null-size
rows: R = 5,000 replications per (case, length); length set {117, 126, 242}. Target size 0.0500.

### 6.1 Pivotal calibration (independent verification)

| Quantile | Mean | Monte-Carlo sd (5 runs) | Candidate smoke |
| --- | --- | --- | --- |
| q95 (one-sided 5%) | 5.327 | 0.013 | 5.335 (500-step grid) — consistent |
| q97.5 | 6.746 | 0.026 | — |
| q99 (one-sided 1%) | 8.614 | 0.031 | — |
| q99.75 (one-sided 0.25%) | 11.434 | 0.118 | — |

### 6.2 Null size (rejection fraction at q95; target 0.0500)

| Case | n=117 | n=126 | n=242 |
| --- | ---: | ---: | ---: |
| IID Gaussian | 0.050 | 0.052 | 0.053 |
| AR(1) ρ=0.30 | 0.055 | 0.057 | 0.049 |
| AR(1) ρ=0.60 | 0.063 | 0.056 | 0.057 |
| AR(1) ρ=0.85 | **0.079** | **0.074** | 0.063 |
| GARCH-like (α=0.10, β=0.85) | 0.053 | 0.047 | 0.053 |
| Heavy tail t_3 | 0.047 | 0.047 | 0.050 |
| Sparse Poisson λ=0.2, unfiltered | 0.052 | 0.051 | 0.052 |
| Sparse Poisson λ=0.2, N≥20 filtered | 0.047 | 0.052 | 0.056 |
| Sparse Poisson λ=0.5, unfiltered | 0.051 | 0.052 | 0.048 |
| Sparse Poisson λ=0.5, N≥20 filtered | 0.050 | 0.050 | 0.051 |
| Sparse Poisson λ=1.0, unfiltered | 0.055 | 0.047 | 0.050 |
| Sparse Poisson λ=1.0, N≥20 filtered | 0.049 | 0.051 | 0.048 |
| Bursty counts (5% Poisson 10) | 0.040 | 0.044 | 0.053 |
| Count–return correlated | 0.046 | 0.054 | 0.046 |
| Structural variance change 3x (hi 2nd half) | 0.025 | 0.023 | 0.026 |
| Structural variance change 1/3x (hi 1st half) | 0.025 | 0.023 | 0.023 |
| Extreme rare events (p=0.03, σ=30) | 0.032 | 0.033 | 0.046 |
| **Left-skew mean-zero (5% at −19 / 95% at +1)** | **0.085** | **0.084** | 0.077 |
| **Left-skew MILD mean-zero (10% at −3 / 90% at +⅓)** | **0.075** | **0.080** | 0.071 |
| Right-skew mean-zero (5% at +19 / 95% at −1) | 0.024 | 0.029 | 0.036 |

### 6.3 Holm-relevant tail size (rejection at q99, one-sided 1%; target 0.0100)

| Case | n=117 | n=126 | n=242 |
| --- | ---: | ---: | ---: |
| IID Gaussian | 0.010 | 0.012 | 0.009 |
| AR(1) ρ=0.85 | 0.023 | 0.024 | 0.017 |
| Left-skew mean-zero (5% −19 / 95% +1) | **0.033** | **0.033** | 0.026 |
| Structural variance change 3x | 0.001 | 0.003 | 0.001 |

### 6.4 Power sanity and pathology

- IID Gaussian + positive mean μ: μ=0.2 → 0.575/0.595/0.812; μ=0.5 → 0.989/0.994/1.000;
  μ=1.0 → 1.000 (n=117/126/242).
- Left-skew **positive** mean (5% −19 / 95% +2, E=0.95): 0.602/0.624/0.806 — power is retained.
- Right-skew positive mean (5% +19 / 95% −0.5, E=0.475): 0.213/0.226/0.404 (lower power; the
  skew direction that is conservative).
- Clustered profitable weeks (positive trades only in ISO weeks 5/12/19, rest no trades; n=126):
  SN test power = 0.77. Note: this concentrated-profitable-week case would be routed to
  `INSUFFICIENT_EVIDENCE` by LOWO (deleting a profitable week flips the mean), which is the
  intended time-concentration guard — so the reported power is the test's, not the profile's
  PASS rate.

### 6.5 Interpretation (falsification, not tuning)

1. **Size is near nominal under IID, mild/moderate persistence (ρ≤0.6), GARCH, symmetric heavy
   tails, sparse/compound counts, bursty counts, and count–return dependence.** The candidate's
   method is not obviously broken in these regimes.
2. **Anti-conservative regime 1 — strong persistence:** ρ=0.85 inflates one-sided size to
   0.063–0.079 (≈1.3–1.6× nominal) and tail size to 0.017–0.024 (≈1.7–2.4× nominal). Confirms the
   candidate's own flagged residual threat.
3. **Anti-conservative regime 2 — left-skew (NEW, decisive):** mean-zero **mild** left-skew
   (10% at −3) already inflates size to 0.071–0.080; severe left-skew (5% at −19) to 0.077–0.085;
   and the **Holm-relevant tail** at q99 inflates to 0.026–0.033 — i.e., **3× the nominal 1%**.
   Left-skewed daily scores (rare large losses) are the **typical shape of trading PnL**. This is
   the strongest reason the nominal FWER claim cannot be locked as-is.
4. **Right-skew and structural variance change are conservative** (size 0.02–0.04): they do not
   create false PASSes but do reduce power.
5. **The S1 (N≥20) floor does not materially distort size** in the tested sparse cases
   (filtered vs unfiltered differences within MC noise) — a useful negative result.
6. **Degenerate-normalizer rate** matches the "no events occurred" probability, correctly routing
   extremely sparse realizations to `INSUFFICIENT_EVIDENCE` (S4).

---

## 7. Engine-compatibility findings

No new incompatibilities beyond the accepted audit/crosswalk. The revised design relies only on
primitives that exist: `position_id` round-trip lifecycle, `realized_pnl_change`,
`position_trading_day` + `SessionMetadata.trading_day_at`, mark/liquidation/breach facts. TD-001
(use `SessionMetadata` only) is honored; TD-002 is kept out of the primary estimand (realized-level
only) and out of R1 (use engine mark/breach facts); LIMIT-001 is correctly modeled as
`DATA_BLOCKED`. The round-trip ledger and day/week helpers remain small engineering deltas
(recorded in the candidate §13; not implemented, per instruction).

## 8. Minimum required changes (before lock)

**C-1 (CRITICAL)** — Candidate §6 (self-normalized test) and §8.1 (`strong FWER <= 0.05`).
- Failure mode: the per-hypothesis one-sided p-values are anti-conservative under the two
  realistic daily-score shapes that matter for trading PnL — strong persistence (size 1.3–1.6×,
  tail 1.7–2.4× nominal) and left-skew (size 1.4–1.7×, tail up to 3× nominal at q99, the
  Holm-relevant region). Holm cannot repair anti-conservative per-hypothesis p-values, so the
  stated strong-FWER ≤ 0.05 guarantee is not honestly met under those shapes.
- Why it affects validity/lockability: the profile's central quantitative promise is a controlled
  per-decision error rate; the calibration artifact would be presented as exact when it is
  anti-conservative for realistic PnL shapes.
- Minimum required change (choose one; the candidate must not silently pick neither):
  - (a) Add a **deterministic, pre-registered shape/dependence gate** on the daily score:
    lag-1 autocorrelation and a robust skewness/outlier measure (e.g., `(mean−median)/MAD` or the
    fraction of days with `|S_d|` beyond a MAD-scaled bound), with pre-registered flag bands; if
    flagged → `INSUFFICIENT_EVIDENCE` (safe bucket) for that hypothesis, and the p-value is not
    relied on at face value. This is O(n) and adds no framework; or
  - (b) Explicitly publish the operating-characteristics size table (this review §6.2–6.3 plus the
    candidate's smoke) in the profile and **weaken the error-rate claim** to "nominal 5% under the
    working model, with documented 7–8% one-sided false-rejection (and up to ~3× tail inflation)
    under strong persistence/left-skew"; the project then accepts that weaker guarantee as the v1
    nominal rate.
  Either way, the exact calibration artifact, MC-error policy (M-3), and the size behavior must be
  identity-bound and locked together.

**H-1 (HIGH)** — Candidate §4 (zero right-censoring, S3).
- Failure mode: `S3` makes **any** in-cohort position still open at cohort end return
  `INSUFFICIENT_EVIDENCE` for the whole hypothesis. For any continuously-operating multi-day-hold
  playbook there will almost always be an open position at a 6-month cohort boundary, so v1
  becomes a de-facto **intraday-only / boundary-closed** evaluator.
- Why it affects lockability: it materially defines the profile's scope and interacts with
  `RESEARCH_DIRECTION` (Human Playbook First often involves multi-day holds); this must be an
  explicit decision, not an accidental consequence.
- Minimum required change: keep `S3` as the v1 governance floor (its completion-bias motivation is
  sound), but require (i) an explicit statement in the profile that v1 evaluates only playbooks
  with zero in-cohort right-censoring (intraday or boundary-closed), (ii) the mandatory
  right-censor count + their realized PnL diagnostic (already in §11 reporting), and (iii) an
  explicit project/owner acknowledgment that multi-day-hold playbooks will be
  `INSUFFICIENT_EVIDENCE` in v1 (research-policy statement, not a frozen-semantic change). The
  deterministic cohort-end-close treatment is an **illustrative alternative** for a future profile
  version, not a v1 requirement.

**H-2 (HIGH)** — Candidate §6.4 (confidence-bound inversion).
- Failure mode: `T_SN(theta0)` is a rational function of `theta0` whose denominator
  `V_D(theta0) = D^-2 sum_t (A_t^S - theta0 A_t^C)^2` is quadratic in `theta0`; monotonicity in
  `theta0` is not guaranteed, so a "deterministic bracket/root rule" can be non-unique or have no
  solution. The FAIL path ("unadjusted one-sided upper bound ≤ 0") and the CI diagnostics depend on
  this inversion.
- Minimum required change: pin the inversion rule before lock — a pre-registered bracket/root
  algorithm, and a fail-closed rule: if no root or non-unique root is found in the pre-registered
  bracket, return `INSUFFICIENT_EVIDENCE` for that bound (never a fabricated bound).

**M-1 (MEDIUM)** — Candidate §10: state that base execution/capital/offset-cost assumptions must be
**conservative (validated), not merely pre-registered**; any later finding that they were optimistic
is an outcome-affecting artifact change (new profile lineage), and fee-break-even stays a mandatory
report.

**M-2 (MEDIUM)** — Candidate §8.3: map the parameter-point counting rule to the firewall
registration model — `parameter_search_identity` is a search-identity binding, not a count unit;
each outcome-inspected parameter point = separate `hypothesis_test_id`; "inspected" includes any
outcome exposure even if only the best point is reported.

**M-3 (MEDIUM)** — Candidate §6.4: pin the Monte-Carlo error policy — empirical-CDF standard error
≤ 1e-3 absolute in p at all Holm-operating quantiles (q95…q99.75), grid ≥ 1000, replications ≥
2×10^5, fixed seed, sha256 identity; runtime consumes the locked artifact only.

**M-4 (MEDIUM)** — Candidate §6.3: document that structural nonstationarity (variance/regime
change) is **conservative** in this test (size 0.023–0.026, tail 0.001–0.003 — power loss, not
false PASS), and add a deterministic variance-ratio diagnostic (first-half vs second-half score
variance) as a mandatory report (optional gate).

## 9. Reviewer suggestions that are NOT authority (do not treat as required)

- **L-1:** reword §3.3 to the precise ratio-of-expectations estimand (math unchanged).
- **L-2:** keep LOTO/LOWO; add one sentence documenting their N-scaling severity property.
- **L-3:** state explicitly that the FAIL path is intentionally unadjusted for multiplicity
  (false-FAIL is a missed opportunity, not a false acceptance).
- **L-4:** Karhunen–Loève `Q = sum_k chi^2_1/(pi^2 k^2)` is an optional refinement over the
  Brownian-grid empirical CDF (removes grid discretization bias); not required.
- **Optional:** a wave-level "best-of" diagnostic (White-reality-check-style) as a report-only
  cross-check is acceptable but must not become a v1 gate (adds a benchmark definition).
- These are reviewer preferences; the profile may adopt or ignore them.

## 10. Verdict contract fields

```text
VERDICT                    = GO_WITH_REQUIRED_CHANGES
CRITICAL                   = 1
HIGH                       = 2
MEDIUM                     = 4
LOW                        = 4
FROZEN_PROTOCOL_CONFLICT   = NO
CANDIDATE_LOCKABLE         = YES (after §8 required changes; all are profile-level, no frozen
                             Protocol v1.0 / 12/6/6 change)
NO_CANDIDATE_OUTCOME_DATA_USED = YES
BLOCKER                    = C-1 (self-normalized p-value validity / error-rate guarantee)
```

All findings are **required defect fixes or explicitly-flagged policy decisions**; none require a
change to frozen research semantics. The revision candidate is not locked by this review; the next
step after adjudication of this review is the ordinary profile-lock engineering package, still
before any candidate outcome access.

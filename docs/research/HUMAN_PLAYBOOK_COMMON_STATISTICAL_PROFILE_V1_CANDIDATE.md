# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE

> Work package: `COMMON_STATISTICAL_PROFILE_V1_DESIGN_AND_INDEPENDENT_REVIEW` — Phase 1 only
> Phase: `DESIGN_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE`
> Role: statistical design engineer (NOT a frozen research-semantics decision maker)
> Date: 2026-08-19
>
> ```text
> COMMON_STATISTICAL_PROFILE_V1_STATUS = CANDIDATE_NOT_LOCKED
> COMMON_STATISTICAL_PROFILE_V1_VERSION = v1.0-candidate
> NO_CANDIDATE_OUTCOME_DATA_USED = YES
> NO_VALIDATION_ACCESS = YES
> NO_HISTORICAL_FINAL_HOLDOUT_ACCESS = YES
> SEMANTIC_CONFLICT = NONE
> ENGINEERING_DELTA = REQUIRED (see §Implementation identity & required deltas)
> NEXT_STAGE = INDEPENDENT_ADVERSARIAL_REVIEW_OF_COMMON_STATISTICAL_PROFILE_V1
> ```

This document is a **candidate** statistical design. It is **not locked**. It does not modify
Research Protocol v1.0, the frozen 12/6/6 chronology, or any other frozen research semantics.
It was produced without running any real Human Playbook candidate, without inspecting any
candidate PnL / equity / expectancy / Sharpe / win-loss, and without opening VALIDATION or the
historical final holdout.

---

## 1. Scope

This candidate defines the project-wide `COMMON_STATISTICAL_PROFILE_V1` that must answer
Protocol v1.0 §9's four common acceptance questions for **every** playbook family:

1. **Economic edge** — after pre-registered costs/slippage, does the PRIMARY branch show
   positive net economic edge with uncertainty treated explicitly?
2. **Evidence sufficiency** — does it meet the locked project-wide sufficiency procedure
   using event counts, distinct trading days and dependence-aware aggregation/cluster
   treatment?
3. **Risk/failure constraints** — do the required pre-registered risk/failure checks pass?
4. **Research integrity** — were chronology/exposure/search/wave rules preserved?

Design goals (from the task): simple, implementable, auditable, resistant to multiple
testing, handles time/product correlation, permits `INSUFFICIENT_EVIDENCE`, and fits the
24-month historical reality. It is deliberately **not** a complex statistics paper.

Design constraints honored:
- no playbook may select the easiest statistical method that happens to pass;
- families with structurally different playbooks are not forced to report meaningless
  false-precision metrics;
- six products are **not** treated as six independent samples;
- no profile rule may be decided after looking at candidate outcomes.

## 2. Frozen authority (do not modify)

```text
RESEARCH_PROTOCOL_VERSION = 1.0
RESEARCH_PROTOCOL_STATUS  = FROZEN_BINDING

DEVELOPMENT   : 2024-01-01 .. 2024-12-31
VALIDATION    : 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT : 2025-07-01 .. 2025-12-31

SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION
PRIMARY_BRANCH (exactly one source-justified primary per claim before outcome testing)
RESEARCH_WAVE (immutable denominator; whole-wave multiplicity)
INSUFFICIENT_EVIDENCE (frozen legitimate result)
historical holdout != prospective genuinely unseen
CAT1 / CAT2 / CAT3 validation revision classes
pre-outcome statistical-profile lock (required before first candidate outcome test)
```

Authorities read for this design:
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_FINAL_ACCEPTANCE_V1_2.md`
- `docs/evidence/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0.md`

None of the frozen semantics above is changed by this candidate. If any future design
requirement forced a change to frozen research semantics, this document would flag it as
`SEMANTIC_CONFLICT` instead of silently changing it. **No such conflict was found.**

## 3. Threat model

The profile must resist the concrete ways a research process can manufacture a false
acceptance:

- **Metric shopping**: each family picking its own easiest statistic/threshold.
- **Snooping / post-hoc rules**: deciding sufficiency, uncertainty, multiplicity, or stress
  after looking at candidate outcomes.
- **Pseudo-independence**: counting products, days, or sources as independent when they are
  correlated.
- **Denominator games**: reporting only winners, or adding hypotheses after outcomes.
- **Sparse-data tricks**: pretending a handful of trades is "enough".
- **One-lucky-trade edge**: a single extreme trade carrying the whole profit.
- **Cost optimism**: edge that exists only because fees/slippage are understated.
- **Over-engineering**: adopting complex machinery that cannot be audited and that quietly
  embeds more researcher freedom.

The countermeasures are: one fixed estimand, one fixed deterministic uncertainty method, a
deterministic sufficiency gate, wave-level Holm multiplicity with a permanent denominator,
a fixed pre-registered cost-stress multiplier, deterministic risk checks, and a fully
deterministic decision table. All numbers are fixed in this document at candidate time.

## 4. Primary estimand

> **PRIMARY_ESTIMAND = mean per-trade net return on entry notional, over completed
> round-trip trades in the evaluation cohort.**
> Symbol: $\theta = E[r_t]$, where
> $r_t = \dfrac{\text{gross realized PnL}_t - \text{total cost}_t}{\text{entry notional}_t}$.

### 4.1 Definition of a trade (sample unit)

- A **completed round trip** is a position that is opened and fully closed inside the
  evaluation cohort (entry and exit timestamps both within cohort boundaries), attributed
  to one concrete contract (one product), with realized PnL settled.
- `entry notional_t = Σ_j (fill_price_entry_j × contract_multiplier_j × quantity_j)` over
  the legs that opened the position. For a simple one-leg entry this is
  `fill_price × multiplier × quantity`.
- `gross realized PnL_t` = sum of realized PnL deltas across the round trip's closing
  transitions (including partial closes) before costs.
- `total cost_t` = entry + exit fees and slippage charged to that trade under the
  pre-registered `ExecutionAssumptions` / `CapitalMarginAssumptions`
  (`charged_costs` / `total_cost` semantics in `src/validation_runner.py`).

### 4.2 Properties and explicit answers

- **Unit**: dimensionless CNY/CNY, i.e., return per unit of notional. Reported in basis
  points of notional (1 bp = 0.0001) for readability.
- **Normalization**: dividing by entry notional makes the estimand comparable across
  products with different contract multipliers (cu, al, ni, au, ag, rb) and across playbooks
  with different typical position sizes. No other scaling is applied.
- **Zero-trading days**: days with no completed trade contribute **zero observations**; they
  are not imputed as 0% returns. Imputing no-trade days as zero returns would bias the mean
  toward zero and inflate the effective event count. Calendar-day/week counts enter only the
  **sufficiency** gate, never the primary sample.
- **Multi-product merge**: all completed round trips across products are pooled into one
  sample with **equal weight per trade**. There is **no per-product estimate followed by a
  vote** (see §Attack analysis, item 4). Per-trade returns are already notional-normalized,
  so pooling is meaningful.
- **Overlapping positions**: overlapping round trips are allowed and each contributes one
  observation. Overlap is handled by the dependence treatment (week-block resampling) and by
  the effective-sample-size adjustment, not by dropping trades.
- **Why arbitrary starting capital cannot create a false conclusion**: the estimand is a
  per-trade return on notional; it is invariant to the choice of starting capital and to
  per-trade lot sizing. Total PnL and the equity curve are **reporting diagnostics only**
  and are never the primary test statistic. (If a family uses capital-dependent sizing, the
  resulting trade set is "the edge conditional on trades actually taken"; capital-constrained
  non-entries are recorded as a diagnostic and are not part of the primary sample — a
  documented limitation, not a hidden assumption.)

### 4.3 Implementation prerequisite (honest statement)

The current engine can produce, deterministically, per-fill `ExecutionOutcome`
(`fill_price`, `total_cost`), per-transition `CapitalTransition`
(`realized_pnl_change`, `required_cost`, before/after `CapitalSnapshot`), per-position
attribution with `concrete_contract_id` and `position_trading_day`, and portfolio-level
`AttributedPosition` / `StrategySleeve` / `PortfolioReconciliation`. **There is no
ready-made round-trip ledger** that groups fills into completed round trips and computes
`r_t` as defined above. This is a **required engineering delta** (see §11); this candidate
does not pretend the estimand is already available.

## 5. Cost / friction treatment

- **Base cost**: every outcome run uses the **pre-registered** `ExecutionAssumptions`
  (`synthetic_fee`, `synthetic_slippage`, `fill_rule=NEXT_TRADABLE_OBSERVATION`) and the
  pre-registered capital/margin assumptions bound in the evaluation. These are fixed before
  any outcome exposure and are part of the run's identity.
- **Cost-stress rule (adopted)**: a fixed multiplier `STRESS_COST_MULTIPLIER = 2.0`,
  fixed at profile lock time. It acts by recomputing each trade's net return with the cost
  term doubled:
  $r_t^{\text{stress}} = \dfrac{\text{gross}_t - 2 \times \text{cost}_t}{\text{entry notional}_t}$.
  The **stress test must also pass** the same Holm-adjusted one-sided test (same sufficiency,
  same bootstrap, same seed) for a `PASS`.
- The multiplier is **not** chosen by looking at results; it is a constant of the profile
  identity. Changing it requires a new profile version. Because any fixed number is
  arbitrary, the protection is that it is pre-registered, immutable, and identical for all
  families.
- Why 2×: a conventional, auditable "costs are twice as bad as assumed" scenario. A playbook
  whose edge exists only because cost assumptions are optimistic fails under stress.

## 6. Uncertainty / precision method

> **UNCERTAINTY_METHOD = circular moving-block bootstrap over calendar weeks**
> (Politis & Romano 1992 circular block bootstrap applied to week blocks), one-sided,
> α = 0.05, B = 10,000, deterministic seed.

Precise algorithm (fully deterministic):

1. **Ordering**: sort all completed round trips by exit timestamp (tie-break: entry
   timestamp, then request id).
2. **Block key**: each trade's block is the ISO calendar week of its **exit trading day**
   (`exit_week`). Only weeks that contain at least one completed trade are "active weeks".
   `W_active` = number of distinct active weeks in the cohort.
3. **Block length (deterministic algorithm)**:
   `L_weeks = min( max(1, ceil(H_median / 5)), 4 )`,
   where `H_median` = median holding horizon of the cohort's completed trades, in trading
   days (a non-outcome structural fact about trade duration — measurable without PnL).
   Rationale: a block must cover typical holding-horizon autocorrelation; ~5 trading days
   per week. Cap at 4 weeks to keep the bootstrap stable in a 6-month cohort.
4. **Resampling**: `m = ceil(W_active / L_weeks)` blocks are drawn per bootstrap sample;
   each block is `L_weeks` consecutive active weeks **on a circle** (the chronological list
   of active weeks wraps from last to first — circular block bootstrap, avoiding edge
   effects). A week selected more than once contributes its trades more than once.
5. **Statistic**: for each bootstrap sample, compute the mean of all per-trade returns in
   the resampled week set. Repeat B = 10,000 times.
6. **One-sided test**: $H_0: \theta \le 0$ vs $H_1: \theta > 0$.
   $p = \dfrac{1 + \#\{b^* \le 0\}}{B+1}$; reject $H_0$ at α if $p \le \alpha$.
   The one-sided lower bound is the α-quantile of the bootstrap distribution of the mean.
7. **RNG seed rule**: `seed = int(sha256(f"CSPV1:{profile_identity}:{hypothesis_test_id}:{cohort}").hexdigest()[:16], 16) % 2**32`, using the standard-library `random.Random(seed)` (no external dependency; bit-for-bit reproducible). The exact generator is part of the profile spec.
8. **Small-sample behavior**: the bootstrap is **only run after** the sufficiency gate
   passes, which guarantees `W_active ≥ 8` and `W_active ≥ 4 × L_weeks`. If sufficiency
   fails, the result is `INSUFFICIENT_EVIDENCE` before any bootstrap output. No
   "case-by-case" decisions exist anywhere in the method.

Why this method: it is the simplest defensible way to (a) handle irregular trade times,
(b) preserve within-week temporal dependence, (c) preserve contemporaneous cross-product
dependence (all products' trades in a resampled week move together), and (d) handle
overlapping positions — with one unified, conservative mechanism and no per-family tuning.

## 7. Evidence sufficiency

> **SUFFICIENCY_RULE (one sentence)**: a cohort is evaluable (may return PASS/FAIL) only if,
> in the evaluation cohort, it has ≥ 60 completed trades spread over ≥ 30 distinct trading
> days and ≥ 8 active weeks, with low time concentration (≤ 50% of trades in one day,
> ≤ 75% in one week), effective sample size ≥ 30 after a holding-horizon variance-inflation
> adjustment, and ≥ 75% of positions completed by cohort end; otherwise the cohort returns
> `INSUFFICIENT_EVIDENCE`.

Deterministic predicates (all must hold for the evaluation cohort):

```text
S1  N_trades        >= 60        completed round trips in the cohort
S2  D_days          >= 30        distinct trading days with >= 1 completed trade
S3  W_active        >= 8         distinct active weeks (weeks with >= 1 completed trade)
S4  W_active        >= 4 * L_weeks   enough blocks for the chosen block length
S5  day_concentration  <= 0.50   max trades in a single trading day / N_trades
S6  week_concentration <= 0.75   max trades in a single week / N_trades
S7  ESS             >= 30        ESS = N_trades / max(1, 2 * H_median - 1)
S8  open_ratio      <= 0.25      positions still open at cohort end / total positions
```

Notes:
- **Holding-horizon effect on effective independence (S7)**: the classic variance-inflation
  factor for overlapping H-day returns is approximately `2H − 1`. `H_median = 1`
  (same-day/intraday) gives `ESS = N`; `H_median = 3` gives `ESS = N/5`. This converts
  holding horizon into effective independent events deterministically, without estimating an
  autocorrelation function.
- **Time concentration (S5, S6)**: prevents a few clustered days/weeks from manufacturing
  "breadth". Concentration is measured on trade **counts** (non-outcome structure), not PnL.
- **Extreme-sparse playbooks**: any failing predicate ⇒ `INSUFFICIENT_EVIDENCE`, no
  threshold relaxation, no date changes, no post-result hypothesis addition (frozen).
- Grounding (canonical trading calendar, metadata only): VALIDATION = 117 trading days /
  27 ISO weeks; DEVELOPMENT = 242 days / 52 weeks; FINAL = 126 days / 27 weeks. So
  `N ≥ 60` in VALIDATION means ≥ ~1 completed trade per 2 trading days — achievable for an
  intraday playbook, structurally not achievable for a few-trades-per-month playbook (which
  is the intended honest outcome).
- These numbers are **v1 pre-registered choices**, explicitly subject to the independent
  adversarial review before lock; after lock they are immutable for the profile lineage.

## 8. Dependence handling

Dependence is handled by exactly three deterministic mechanisms; no method is chosen
post-outcome:

1. **Week-block resampling (uncertainty)**: the circular block bootstrap resamples whole
   weeks, so same-product temporal dependence (within and across the block), multi-product
   contemporaneous correlation, and overlapping positions inside a week are preserved in the
   resampling distribution. There is **no** assumption that 6 products = 6 independent
   samples.
2. **Effective-sample-size adjustment (sufficiency)**: holding-horizon overlap is converted
   into fewer effective independent events via `ESS = N / max(1, 2H − 1)`.
3. **Whole-wave multiplicity (Holm FWER)**: hypotheses within the same research wave — even
   highly correlated ones — are penalized together; Holm controls family-wise error under
   arbitrary dependence.

Explicitly not assumed independent:
- trades of the same product across time (block structure + ESS);
- trades of different products on the same day (week block preserves contemporaneous
  dependence);
- hypotheses in the same research wave (Holm);
- multiple similar Human Playbook sources (see §Attack analysis, item 10).

## 9. Whole-wave multiplicity

> **MULTIPLICITY_METHOD = Holm (1979) step-down family-wise error control at α = 0.05 over
> the wave's permanent tested denominator M.**

- **alpha**: α = 0.05 (one-sided, matching §6).
- **correction family**: the whole research wave — all hypotheses in the locked wave
  manifest's permanent tested denominator. This is the frozen whole-wave multiplicity unit.
- **hypothesis counting rule**: each independently falsifiable operationalized hypothesis
  that is scheduled for outcome testing = exactly one `hypothesis_test_id` in the
  denominator (this is already the machine counting unit of `ResearchWaveManifest` /
  `OutcomeTestRegistration`):
  - PRIMARY branch = 1;
  - every outcome-tested alternative branch = 1;
  - every instrument/timeframe/context/parameter branch that is outcome-tested = 1;
  - `FAIL` and `INSUFFICIENT_EVIDENCE` hypotheses **remain permanently in the denominator**;
  - purely deterministic non-outcome work (operationalization tests, engine sanity,
    unit tests) is **not** outcome-tested and is not in the denominator (but becomes a
    counted search event if later outcome-exposed).
- **alternative-branch rule**: an outcome-tested alternative cannot rescue a failed PRIMARY
  as "validation of the source claim" (frozen). A separately passing alternative is a
  **separate accepted hypothesis** with its own claim identity; it is not called validation
  of the original source claim, and it still needs its own sufficiency + Holm + risk +
  integrity gates over the same denominator.
- **Holm step-down**: order the M one-sided p-values ascending; reject H(i) if
  p(i) ≤ α/(M − i + 1) for all j ≤ i. (Illustrative thresholds, α=0.05: M=10 → smallest
  threshold 0.005, largest 0.05; M=20 → 0.0025 … 0.05.)
- **Monotonicity (search freedom cannot make acceptance easier)**: adding a hypothesis
  before wave lock increases M and makes Holm thresholds stricter; adding after any outcome
  test requires a new wave/search event (frozen) and can never dilute the existing
  denominator.
- **No winner-only reporting**: reporting must disclose the full denominator M and every
  hypothesis outcome (PASS/FAIL/INSUFFICIENT_EVIDENCE).
- **Why Holm and not something else**:
  - FDR (Benjamini-Hochberg) is **rejected** for acceptance: acceptance of a playbook is a
    per-decision consequential act (you may trade it), so the correct error rate is
    per-decision family-wise error, not a controlled fraction of false discoveries among
    many claims (see §Attack analysis, item 5).
  - White (2000) reality check / Romano-Wolf (2005) stepdown control FWER for the
    **maximum over a set** of statistics (the "best of many" data-snooping problem). v1
    does **not** report argmax survivors: every outcome-tested branch is a pre-registered,
    separately counted hypothesis. Holm over the pre-registered hypotheses is therefore the
    correct and simplest match. Romano-Wolf stepdown is the documented future refinement if
    best-of reporting is ever adopted (v1 forbids it).
  - Holm is uniformly more powerful than Bonferroni, valid under arbitrary dependence,
    deterministic, and auditable — the simplest safe v1 default (see §Attack analysis,
    item 6).

## 10. Common acceptance decision table

Deterministic, evaluated in a fixed order. No "差不多 / 边缘通过 / 研究员判断" exists.

```text
For a hypothesis h in a locked wave, on the VALIDATION cohort:

Step 0 (wave-level, checked FIRST, overrides everything):
  INTEGRITY check  -> if violated: INTEGRITY_FAIL

Step 1: SUFFICIENCY gate (S1..S8)
  any predicate fails              -> INSUFFICIENT_EVIDENCE

Step 2: MANDATORY RISK checks
  R1 forced-liquidation/breach > 0 -> FAIL
  R2 single-trade concentration    -> FAIL   (max |r_t| / sum|r_t| > 0.40)

Step 3: ECONOMIC EDGE (base costs)
  Holm-adjusted one-sided p_h <= tau_h   AND
  Holm-adjusted one-sided lower bound >= MIN_ECONOMIC_EDGE (2 bp of notional per trade)
  else                               -> FAIL

Step 4: COST-STRESS (2x costs)
  Holm-adjusted one-sided p_h^stress <= tau_h
  else                               -> FAIL

Step 5: all of the above passed      -> PASS
```

Decision summary:

| Condition | Verdict |
| --- | --- |
| Integrity violation (Step 0) | `INTEGRITY_FAIL` |
| Sufficiency fails (Step 1) | `INSUFFICIENT_EVIDENCE` |
| Risk fails (Step 2) | `FAIL` |
| No base economic edge / below economic floor (Step 3) | `FAIL` |
| No edge under 2× cost stress (Step 4) | `FAIL` |
| All pass | `PASS` |

Ordering rationale: integrity is checked first because a tainted result is not a statistical
result at all. Sufficiency precedes significance so a nominally-significant but tiny sample
can never pass. Risk precedes significance so a high-risk profile cannot pass on edge alone.
Economic floor precedes stress so economically trivial edges fail before stress is even
needed.

`MIN_ECONOMIC_EDGE = 2 bp` of notional per trade (0.0002): an economic-significance floor
required by the protocol's "economic edge" question (see §Attack analysis, item 8). It is
pre-registered and immutable for the profile lineage.

## 11. Risk / failure constraints

**Project-wide mandatory checks (apply to all families, all in the table above):**
- cost-stress pass at fixed 2× (§5);
- no forced liquidation / maintenance-margin breach in the evaluation cohort under the
  pre-registered capital assumptions (R1);
- single-trade concentration ≤ 40% of absolute net PnL (R2) — one extreme winner cannot
  carry the edge (see §Attack analysis, item 9);
- economic floor ≥ 2 bp/notion per trade (Step 3).

**Family-specific pre-registered additional constraints:**
- explicitly **not** frozen project-wide: a single arbitrary max-drawdown number, since
  drawdown meaning differs across intraday vs. multi-day playbooks and an arbitrary global
  number would be exactly the kind of false-precision metric the task warns against.
- A family **may** register additional constraints (e.g., a family-specific drawdown cap,
  regime checks, value-weighted diagnostics) **in the wave manifest before any outcome
  exposure**. Such constraints may only **add** restrictions, may **not** replace any common
  statistical threshold, and may **not** be changed after outcome exposure (frozen).

## 12. DEVELOPMENT / VALIDATION / HISTORICAL FINAL behavior

One immutable profile identity governs all three stages; no stage may change the rules.

- **DEVELOPMENT (2024-01-01..2024-12-31)**: the same estimand, sufficiency, dependence and
  multiplicity machinery is computed, but development output is **pre-registered
  diagnostic / development analysis only** and can never yield `PASS`. It is used to:
  detect implementation defects (CAT1, with deterministic evidence), verify the hypothesis
  is worth taking to validation, and perform pre-registered exploratory analysis within wave
  rules. Development results may **not** be used to alter the statistical rules or thresholds
  before validation (profile is frozen before development); a strong development result does
  not substitute for validation.
- **VALIDATION (2025-01-01..2025-06-30)**: the **acceptance cohort**. The decision table
  (§10) produces the primary verdict and the wave-level Holm multiplicity is computed here.
- **PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT (2025-07-01..2025-12-31)**: a one-shot
  confirmatory exam. `FINAL_ACCEPTED` requires (a) a separate, explicitly registered
  final-holdout unlock authority (frozen; none registered by default), (b) the **same**
  sufficiency + risk + economic-edge + stress checks independently satisfied on the final
  cohort, and (c) the final-cohort p-values corrected against the **same** wave denominator.
  Otherwise `FINAL_REJECTED`; `FINAL_VOID_IMPLEMENTATION_DEFECT` changes the conclusion and
  never restores holdout status (frozen).
- **Forbidden**: development-sees-results → change statistical rules → validation. The
  profile, its numbers, and its identity are immutable across all three stages.
- **Access reality in this task**: VALIDATION and HISTORICAL FINAL remain locked; this
  candidate only defines how they will be evaluated once separately authorized.

## 13. INSUFFICIENT_EVIDENCE rules

- Triggered **only** by the deterministic sufficiency gate (§7, S1..S8) or by the firewall's
  pre-existing denial paths. There is no discretionary trigger.
- `INSUFFICIENT_EVIDENCE` is a frozen legitimate result, not a failure and not a retry
  license: no relaxed thresholds, no changed dates, no added post-result hypotheses.
- The hypothesis stays permanently in the wave denominator.
- Sparse families are expected to receive `INSUFFICIENT_EVIDENCE` in a 6-month validation
  cohort; the honest forward path is future genuinely-prospective Shadow/Forward data or a
  **new wave** with more data (a new search event), never re-examining the same cohort as
  clean evidence.

## 14. Implementation identity / schema

Current interface reality (`src/research_firewall.py`):

- `CommonStatisticalProfile` already carries `profile_id`, `profile_version`,
  `uncertainty_precision_method`, `evidence_sufficiency_procedure`, `dependence_handling`,
  `multiplicity_decision_rule`, `common_acceptance_procedure`, optional
  `test_only_marker`, and a deterministic `profile_identity` hash. **The five method fields
  are strings**; the candidate must encode the full numeric spec into those fields (e.g., a
  canonical machine-readable reference + hash of the numeric profile document) so that
  `profile_identity` is a stable, verifiable lock.
- `ResearchWaveManifest` binds `statistical_profile_id`, `statistical_profile_identity`,
  `multiplicity_counting_unit_identity`, and the permanent tested denominator. It is already
  sufficient to bind a real profile; the counting-unit identity needs a canonical value
  (e.g., `HYPOTHESIS_TEST_ID_V1`) defined and locked.
- `OutcomeTestRegistration` binds the exact profile id/identity and counting-unit identity
  per hypothesis. Already sufficient — no schema change needed for identity binding.
- `PreOutcomeGate` requires `COMMON_STATISTICAL_PROFILE=LOCKED` and a non-`TEST_ONLY`
  profile for real (non-synthetic) DEVELOPMENT grants; VALIDATION / FINAL remain hard-denied.
  Registering this candidate with `test_only_marker=None` after independent review and lock
  is the intended path (it does **not** by itself open VALIDATION/FINAL).

**Engine outcome semantics available today** (verified by reading code): `CapitalSnapshot`
(`realized_pnl`, `unrealized_pnl`, `equity`, `charged_costs`, `starting_capital`, `state_at`,
`position_trading_day`, `concrete_contract_id`), `CapitalTransition`
(`realized_pnl_change`, `required_cost`, `before`/`after`), `ExecutionOutcome`
(`fill_price`, `total_cost`), `MarkToMarketTransition`, `ValidationRunResult`,
portfolio `CandidateOutcome` / `AttributedPosition` / `StrategySleeve` /
`SharedCapitalState` / `PortfolioReconciliation`. These are the building blocks of the
round-trip ledger; the aggregation layer does not exist yet.

## 15. Required engineering deltas (recorded; NOT implemented in this phase)

Per Protocol v1.0 §16 these are ordinary implementation items, but the task explicitly says
**not** to implement them before independent review. They are recorded here as requirements:

1. **Round-trip ledger / trade-return extractor** — deterministic grouping of fills into
   completed round trips; computation of `r_t` (net return on entry notional), holding
   horizon (trading days), exit ISO week, product/contract identity, open/closed status,
   per-trade cost; cohort classification. Unit-tested on synthetic fixtures.
2. **Common statistical evaluator** — deterministic implementation of: sufficiency gate
   (S1..S8), circular week-block bootstrap (B=10,000, fixed seed rule), Holm step-down over
   the wave denominator, cost-stress recompute (2×), economic floor, and the decision table.
   Unit-tested on synthetic fixtures only.
3. **Canonical numeric profile document** — a versioned machine-readable
   `COMMON_STATISTICAL_PROFILE_V1` containing every number in this candidate; its sha256 is
   bound into the `CommonStatisticalProfile` method fields so `profile_identity` locks the
   exact numbers.
4. **Counting-unit identity** — canonical `multiplicity_counting_unit_identity`
   (`HYPOTHESIS_TEST_ID_V1`) definition + lock tests.
5. **Deterministic RNG wrapper** — stdlib-only seeded PRNG guaranteeing bit-for-bit
   reproducibility of every bootstrap result across runs/environments.
6. **Tests** — synthetic-fixture tests for the ledger, evaluator, sufficiency, bootstrap
   reproducibility, Holm behavior, decision-table order, and cost-stress.

No changes to frozen research semantics are required. No `OutcomeTestRegistration` /
`ResearchWaveManifest` schema changes are required for identity binding (only content of
profile fields and the new evaluator). This is an ordinary engineering delta, not a
frozen-semantics change.

## 16. Primary statistical references

The candidate does **not** decorate a pre-decided conclusion with paper names; each reference
below plays a specific role and its limits are stated. Verification status is in the design
evidence file.

| Paper / title | Author(s) | Year | What it supports here | What it does NOT prove |
| --- | --- | --- | --- | --- |
| The Jackknife and the Bootstrap for General Stationary Observations, Ann. Statist. 17(3):1217–1241 | H.R. Künsch | 1989 | Foundation of block bootstrap for dependent stationary data; resampling contiguous blocks preserves dependence. | Does not tell us the right block length or cluster definition for trade data. |
| A Circular Block-Resampling Procedure for Stationary Data, in Exploring the Limits of Bootstrap, Wiley, 263–270 | D.N. Politis, J.P. Romano | 1992 | Circular block bootstrap avoids edge effects — basis of our week-block resampling. | Does not specify the block unit (weeks vs days) for trading data. |
| The Stationary Bootstrap, JASA 89(428):1303–1313 | D.N. Politis, J.P. Romano | 1994 | Alternative dependent bootstrap with variable block length. | We deliberately choose fixed circular week blocks for v1 simplicity; stationary bootstrap is deferred. |
| Automatic Block-Length Selection for the Dependent Bootstrap, Econometric Reviews 23(1):53–70 | D.N. Politis, H. White | 2004 | Formal data-driven block-length selection exists. | We do NOT use it for v1: it needs spectral-density estimation, is more complex, and has a published correction (Patton, Politis, White 2009). Over-governance for v1. |
| Subsampling, Springer | D.N. Politis, J.P. Romano, M. Wolf | 1999 | General theory of resampling for dependent data and block choice. | Not needed for the v1 decision path beyond the block bootstrap. |
| A Simple Sequentially Rejective Multiple Test Procedure, Scand. J. Statist. 6(2):65–70 | S. Holm | 1979 | Step-down FWER control valid under arbitrary dependence — our multiplicity method. | Holm can be conservative under strong correlation; it does not guarantee high power (accepted for v1). |
| A Reality Check for Data Snooping, Econometrica 68(5):1097–1126 | H. White | 2000 | Data snooping: testing whether the best of many rules beats a benchmark is harder than testing one rule. | Does not apply directly because v1 forbids argmax reporting; every branch is a pre-registered counted hypothesis. |
| Stepwise Multiple Testing as Formalized Data Snooping, Econometrica 73(4):1237–1282 | J.P. Romano, M. Wolf | 2005 | Stepdown methods that control FWER for the maximum statistic under dependence. | Documented future refinement for best-of reporting; v1 does not need it. |
| Data-Snooping, Technical Trading Rule Performance, and the Bootstrap, J. Finance 54(5):1647–1691 | R. Sullivan, A. Timmermann, H. White | 1999 | Reality-check bootstrap for technical trading rules; demonstrates how snooping inflates apparent performance. | Confirms the threat model; does not prescribe a specific v1 estimator. |
| Controlling the False Discovery Rate, JRSS-B 57(1):289–300 | Y. Benjamini, Y. Hochberg | 1995 | Defines FDR. | Cited to justify **why FDR is rejected** for per-playbook acceptance decisions. |
| The Statistics of Sharpe Ratios, Fin. Anal. J. 58(4):36–52 | A.W. Lo | 2002 | Sharpe ratio's sampling distribution is unreliable for short/skewed samples. | Supports rejecting Sharpe as the common primary metric; does not say Sharpe is always wrong. |
| A Simple, Positive Semi-Definite, Heteroskedasticity and Autocorrelation Consistent Covariance Matrix, Econometrica 55(3):703–708 | W.K. Newey, K.D. West | 1987 | HAC variance estimation for autocorrelated/heteroskedastic data. | We deliberately choose week-block bootstrap over HAC for v1 (simpler, no bandwidth/prewhitening choices). |
| Bootstrap-Based Improvements for Inference with Clustered Errors, Rev. Econ. Statist. 90(3):414–427 | A.C. Cameron, J.B. Gelbach, D.L. Miller | 2008 | Cluster bootstrap improves inference when errors are clustered (e.g., by time). | Supports clustering; our cluster unit (week) is a design choice, not prescribed by the paper. |
| Pseudo-Mathematics and Financial Charlatanism: The Effects of Backtest Overfitting on Out-of-Sample Performance, Notices Amer. Math. Soc. 61(5):458–471 | D.H. Bailey, J. Borwein, M. López de Prado, Q.J. Zhu | 2014 | Backtest overfitting inflates in-sample performance; multiple testing across configurations is a key driver. | Confirms the multiplicity threat; the PBO/deflated-Sharpe machinery is deliberately not adopted for v1 (over-governance). |

All references above are primary journal/book sources or the authors' own pages. No blog or
second-hand trading article is used as statistical authority.

## 17. Strongest counterarguments (and the candidate's answer)

1. **The week-block bootstrap with a holding-horizon block-length rule is ad hoc, not the
   Politis-White optimum.** Accepted. The ABL estimator needs spectral-density estimation,
   has a published correction, and adds fragility. v1 prefers a simple, conservative,
   deterministic rule. If review demands it, this is a v1.1 candidate change — before lock
   only.
2. **The 2× cost-stress multiplier is arbitrary.** Any fixed number is arbitrary; the
   protection is that it is pre-registered, immutable, and identical for all families, and
   the stress gate is hard (must also pass).
3. **Equal weighting per trade ignores sizing/value weighting.** Accepted limitation.
   Value-weighted versions are permitted only as family-specific pre-registered diagnostics,
   never as the common primary.
4. **MIN_ECONOMIC_EDGE = 2 bp per trade is arbitrary.** It operationalizes the protocol's
   "economic edge" question; it is pre-registered and subject to independent review before
   lock. It answers "statistically significant but economically trivial" with `FAIL`.
5. **Holm over the whole wave can be very conservative for correlated branches.**
   Conservatism is deliberate for v1 acceptance (per-decision FWER). Romano-Wolf stepdown is
   the documented refinement if the review wants more power while keeping FWER.
6. **The sufficiency thresholds (60/30/8/ESS≥30) may be too strict for some valid playbooks.**
   That is the intended consequence of a 6-month validation cohort under the frozen 12/6/6;
   `INSUFFICIENT_EVIDENCE` is the frozen honest outcome for sparse playbooks.
7. **The primary estimand ignores capital-constrained skipped trades.** Recorded as a
   diagnostic; the estimand is "edge conditional on trades actually taken". This is a
   documented limitation, not hidden.
8. **Week blocks may not capture autocorrelation longer than L_weeks.** Residual risk,
   mitigated by the ESS variance-inflation adjustment and conservative sufficiency.
9. **A real profile could be "designed to pass" via the sufficiency/economic numbers.**
   Mitigated because the numbers are fixed at candidate time (before any outcome), reviewed
   independently, and bound into an immutable identity hash; any post-outcome change creates
   a new profile lineage and never restores unseen status (frozen).

## 18. Attack analysis (explicit review of easy-to-get-wrong designs)

1. **"At least 30 trades" rule of thumb — insufficient.** 30 is a CLT heuristic for IID data.
   It ignores autocorrelation/overlap (effective n much smaller), ignores cross-sectional
   correlation, gives no power guarantee, and ignores concentration. The candidate replaces
   it with ESS ≥ 30 + distinct-days ≥ 30 + active-weeks ≥ 8 + concentration caps + block
   length, all deterministic.
2. **Sharpe as the common primary acceptance metric — rejected.** Sharpe is sensitive to
   return frequency, to whether zero-trade days are included (metric-shopping surface), not
   robust across products/playbooks, and unreliable for short/skewed samples (Lo 2002). v1
   uses per-trade net return with explicit bootstrap uncertainty; Sharpe is allowed only as a
   family-specific pre-registered diagnostic.
3. **Plain IID bootstrap — unsafe here.** It resamples individual trades as if independent,
   understating variance under autocorrelation, overlap, and cross-product contemporaneous
   correlation → anti-conservative. The candidate uses week-block (cluster) resampling.
4. **Per-product significance then "vote" — pseudo-independence.** Correlated products would
   be double-counted and hypotheses multiplied without proper counting. The candidate pools
   trades at the hypothesis level; week blocks keep contemporaneous dependence intact. No
   per-product votes.
5. **FDR too lenient for accepting a real playbook.** Acceptance is a per-decision
   consequential act; FDR controls the expected fraction of false discoveries among many, not
   the per-decision error rate. v1 uses Holm FWER.
6. **Holm conservative but simplest safe v1.** Yes — valid under arbitrary dependence,
   step-down (more powerful than Bonferroni), deterministic, auditable. Acceptable
   conservatism for v1.
7. **6-month validation for sparse strategies.** ~117 trading days / 27 weeks. A playbook
   needs ≥60 completed trades across ≥30 days and ≥8 weeks with low concentration — an
   intraday playbook can reach this; sparse playbooks correctly return `INSUFFICIENT_EVIDENCE`
   (frozen consequence, not a bug).
8. **Statistically significant but economically tiny.** Handled by the economic floor: the
   Holm-adjusted one-sided lower bound must be ≥ 2 bp/notion per trade; otherwise `FAIL`.
9. **One extreme winner supports all profit.** Handled by the single-trade concentration risk
   check (largest |r_t| ≤ 40% of Σ|r_t|) plus the per-trade mean being diluted by the big
   winner; the concentration check is mandatory.
10. **Multiple similar Human Playbook sources form implicit multiplicity.** Protocol §4
    lineage review merges mechanism-similar playbooks into one family/lineage; similar
    playbooks from different sources are not independent confirmations, they count as related
    hypotheses under the same wave's Holm family, and a "second source" never relaxes
    multiplicity or sufficiency.

## 19. Over-governance check

Explicitly **not adopted for v1** (would violate "simplest but safe enough"):

- large Bayesian hierarchical models (data too small, hard to audit);
- multi-level complex models;
- automatic bootstrap hyperparameter tuning (Politis-White ABL deferred; fixed deterministic
  rule used instead);
- dynamic/adaptive method selection based on outcomes (forbidden by the frozen pre-outcome
  design);
- one bespoke statistical algorithm per family (one common method; families may only add
  pre-registered constraints);
- rules that only work after seeing outcomes;
- HAC with data-driven bandwidth/prewhitening for v1 (week-block bootstrap covers the same
  dependence more simply);
- reality-check / stepdown-over-argmax (only needed for best-of reporting, which v1 forbids);
- FDR (rejected, see §9/§18);
- deflated-Sharpe / PBO machinery (Bailey et al. 2014) as a v1 gate (confirms the threat but
  adds estimation layers; the multiplicity + economic floor + risk checks cover the v1 need).

v1 uses exactly: one estimand, week-block bootstrap, deterministic sufficiency, Holm,
cost-stress, concentration and liquidation checks, and a deterministic decision table.

## 20. Open questions (for the independent adversarial review)

1. Should `MIN_ECONOMIC_EDGE` be 2 bp, or higher/lower? (Decidable only before lock.)
2. Should the primary be value-weighted per trade rather than equal-weighted? (Candidate
   says no for v1; reviewer may argue.)
3. Are the sufficiency numbers 60 / 30 / 8 / ESS 30 appropriate for 6-month validation?
   (Candidate grounding: VALIDATION = 117 days / 27 weeks.)
4. Should the block-length rule use median or mean holding horizon, and is the `2H−1`
   variance-inflation formula the right ESS adjustment? 
5. Is a 2× cost stress the right fixed multiplier, or should it be cost-model-specific?
   (Candidate: fixed 2× for uniformity.)
6. Should Sharpe remain a family diagnostic, and should any diagnostic be promoted to a
   common check?
7. Is Holm over the whole wave acceptable, or should Romano-Wolf stepdown be adopted before
   lock?
8. Should `open_ratio ≤ 0.25` be a sufficiency predicate (as chosen) or a risk check?
9. Should the final-holdout exam require its own sufficiency on 126 days / 27 weeks, or use
   a pooled-dev+validation sufficiency? (Candidate: final stands alone, same table.)

## 21. Candidate verdict

```text
COMMON_STATISTICAL_PROFILE_V1 = CANDIDATE / NOT_LOCKED
DESIGN_VERDICT = DESIGNED_CANDIDATE
NO_CANDIDATE_OUTCOME_DATA_USED = YES
SEMANTIC_CONFLICT = NONE
ENGINEERING_DELTA = REQUIRED (round-trip ledger, evaluator, profile doc, tests)
NEXT_STAGE = INDEPENDENT_ADVERSARIAL_REVIEW_OF_COMMON_STATISTICAL_PROFILE_V1
```

This document is a design candidate only. It does **not**: write a real locked profile to
any registry, construct a real research wave, run a candidate backtest, claim an outcome
test, open VALIDATION, or open the historical final holdout. The next stage is the
independent adversarial review of this candidate; only after that review, Owner/project
acceptance, and lock may this become the binding `COMMON_STATISTICAL_PROFILE_V1`.

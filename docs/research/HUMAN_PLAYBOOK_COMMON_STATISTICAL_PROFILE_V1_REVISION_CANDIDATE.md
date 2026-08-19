# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE

> Date: 2026-08-19
> Work package: `COMMON_STATISTICAL_PROFILE_V1_REVISION_AFTER_PARALLEL_REVIEW`
> Status: `REVISION_CANDIDATE / NOT_LOCKED / TARGETED_DELTA_REVIEW_REQUIRED`
> Supersedes for active design review only: `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md`
> Frozen authority unchanged: Research Protocol v1.0 + frozen 12/6/6 chronology
> Adjudication authority: `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`

```text
COMMON_STATISTICAL_PROFILE_V1_REVISION_VERSION=v1.0-revision-candidate-0.2
NO_CANDIDATE_OUTCOME_DATA_USED=YES
NO_VALIDATION_ACCESS=YES
NO_HISTORICAL_FINAL_HOLDOUT_ACCESS=YES
FROZEN_PROTOCOL_CONFLICT=NO
CANDIDATE_LOCKABLE_NOW=NO
NEXT_REQUIRED_STAGE=TARGETED_INDEPENDENT_DELTA_REVIEW
```

This document revises the first Common Statistical Profile candidate only. It does not change
Research Protocol v1.0, the frozen chronology, Human Playbook First, the Selection Firewall,
PRIMARY-branch semantics, Research Wave semantics, or any access state. No real Human Playbook
candidate outcome, candidate PnL, equity, expectancy, Sharpe, win/loss, VALIDATION result, or
historical-final result was inspected or used.

---

## 1. Design objective

The profile must answer the frozen common contract for every registered Human Playbook hypothesis:

1. **Economic edge:** is the PRIMARY branch positively profitable after the exact pre-registered
   base execution costs/slippage, with uncertainty treated explicitly?
2. **Evidence sufficiency:** is there enough temporally distributed governed evidence for the
   chosen dependence-aware inference to be credible?
3. **Risk/failure:** did mandatory execution/risk failure conditions occur, and is the apparent
   edge robust to one trade or one time window carrying the sign?
4. **Integrity:** were chronology, exposure, PRIMARY, scope/search identity, Research Wave and
   multiplicity rules preserved?

The revised v1 objective is deliberately narrower than the first candidate: use the smallest
common statistical machinery that can falsify weak evidence without introducing a large set of
arbitrary hard thresholds.

---

## 2. Explicit adjudication changes from the first candidate

The following first-candidate rules are **removed** from the lock candidate:

- `ESS=N/max(1,2H-1)` as a hard sufficiency gate;
- fixed hard `N>=60`, `D_days>=30`, `W_active>=8`, 50% day concentration, 75% week
  concentration and `open_ratio<=0.25` as a combined sufficiency system;
- `MIN_ECONOMIC_EDGE=2 bp` as an extra universal economic floor;
- `2x cost` as a universal hard execution-friction gate;
- the claim that Romano-Wolf stepdown matters only for argmax/best-of reporting;
- circular first/last-cohort block wrapping.

The revised candidate replaces them with:

- one explicit round-trip identity and cohort-boundary rule;
- a weekly influence representation plus non-circular moving-block bootstrap;
- a small set of minimum support/algorithmic floors, clearly labeled governance choices rather
  than statistical laws;
- a no-outcome standardized power/detectability envelope;
- a three-way evidence interpretation (`PASS / FAIL / INSUFFICIENT_EVIDENCE`) plus separate
  `DATA_BLOCKED` and `INTEGRITY_FAIL` states;
- leave-one-trade and leave-one-week robustness guards instead of arbitrary PnL concentration
  percentages;
- base-cost inference plus break-even diagnostics instead of a universal `2x` hard gate;
- a machine-consistent one-`hypothesis_test_id` multiplicity taxonomy.

---

## 3. Primary estimand and round-trip identity

### 3.1 One `position_id` = one observation

A completed round trip is exactly one engine `position_id` lifecycle:

```text
flat -> first open -> optional add/open legs -> optional partial closes -> terminal close -> flat
```

Rules:

- one `position_id` = one statistical observation;
- multiple opening/add legs remain inside that observation;
- partial-close legs are aggregated and never increase `N`;
- terminal full close ends the observation;
- forced liquidation is a terminal close, remains in the observation, and separately triggers
  the mandatory risk/failure rule in §9;
- a concrete-contract roll cannot silently continue a position; contract A and contract B are
  separate round trips with separate `position_id`s;
- a new flat -> open cycle is a new observation even on the same instrument/day.

This is the exact identity already compatible with the existing deterministic engine lifecycle.

### 3.2 Per-round-trip quantities

For round trip `i`:

```text
entry_notional_i = sum over OPEN/ADD legs of
                   abs(fill_price * contract_multiplier * opened_quantity)

gross_realized_i = sum of CapitalTransition.realized_pnl_change
                   over all REDUCE/CLOSE/FORCED_LIQUIDATION legs

additive_fee_i    = sum of CapitalTransition.required_cost exactly once
                   over the round-trip transitions

r_i               = (gross_realized_i - additive_fee_i) / entry_notional_i
```

`entry_notional_i` must be positive. A zero/invalid denominator is `DATA_BLOCKED`, not silently
repaired.

**Cost-source guard:** the ledger consumes one authoritative additive-fee source. It must not sum
both `ExecutionOutcome.total_cost` and capital charged-cost deltas for the same fill.

**Slippage is not additive fee.** In the current engine, synthetic slippage changes the fill price
and is therefore already embedded in `gross_realized_i`. It must never be described as part of the
post-hoc additive `additive_fee_i` term.

### 3.3 Primary estimand

```text
PRIMARY_ESTIMAND = theta = mean_i(r_i)
```

Equal weighting is per completed round trip, after each trade is normalized by its own gross entry
notional. This is a **per-decision quality estimand**: it asks whether taken trades have positive
net edge after pre-registered base friction. It is not a capital-productivity, annualized-return,
turnover, opportunity-cost or portfolio-growth estimand. Those may be diagnostics later but do not
replace the common v1 estimand.

Zero-trade days are not fabricated as 0% trades. Inactivity is instead represented in the weekly
inference series in §6.

---

## 4. Cohort and boundary semantics

A round trip is eligible for a cohort only when both:

```text
first_open_trading_day is inside the cohort
terminal_close_trading_day is inside the same cohort
```

Trading-day authority is **only** `SessionMetadata` / governed session facts. The bootstrap
`NormalizedSessionCalendar` is not a valid business authority (TD-001 guard).

Boundary rules:

- a position opened before cohort start is left-censored and excluded from the cohort estimator;
- a position opened inside the cohort but still open at cohort end is right-censored;
- **any right-censored in-cohort position makes the cohort `INSUFFICIENT_EVIDENCE`** for that
  hypothesis under v1, because selecting only completed positions could create outcome-dependent
  completion bias;
- no post-cohort price/outcome may be read merely to finish a cohort trade;
- no validation/final data may be borrowed backward into an earlier cohort.

This zero-right-censor rule is intentionally strict and has no percentage knob. A future profile
may adopt a formally justified censoring method, but v1 does not invent one.

---

## 5. Holding horizon and multi-week semantics

For completed round trip `i`:

```text
H_days_i = number of distinct authoritative trading days from first open through terminal close,
           inclusive; same-trading-day round trip => H_days_i = 1

span_weeks_i = number of distinct ISO calendar weeks touched by those authoritative trading days,
               inclusive
```

Report:

```text
H_days_median
H_days_p90
span_weeks_p90
```

Percentiles use deterministic nearest-rank ordering. Holding horizon is a structural diagnostic;
it is **not** converted into a guessed effective sample size.

For the primary point statistic, the full round-trip return is attributed to the ISO week of the
**terminal close trading day** (`exit_week`). This is an accounting attribution, not a claim that
all economic dependence arose in the exit week.

Dependence inference therefore uses a block length tied to observed structural holding span:

```text
L_weeks = max(1, span_weeks_p90)
```

This directly replaces the first candidate's `2H-1` ESS heuristic and the `H/5` approximation.
It uses actual project trading-day/week identity and makes the remaining limitation explicit:
trades in the longest 10% holding-span tail may exceed the chosen block length. `H_days_max` and
`span_weeks_max` are mandatory diagnostics so that tail dependence is visible rather than hidden.

---

## 6. Dependence-aware uncertainty: weekly influence moving-block bootstrap

### 6.1 Weekly influence series

Let `W` be the complete ordered sequence of ISO calendar weeks intersecting the cohort, including
weeks with zero completed exits. Let `N` be the number of eligible completed round trips.

For each week `w`:

```text
x_w = (W / N) * sum(r_i for eligible trades whose terminal close is in week w)
```

Then exactly:

```text
mean_w(x_w) = mean_i(r_i) = theta_hat
```

This representation preserves the per-trade point estimand while forcing time concentration and
zero-exit weeks into the uncertainty calculation. Cross-product exits in the same week remain in
one time cluster rather than being treated as independent products.

### 6.2 Non-circular moving-block bootstrap

Use a standard moving-block bootstrap over the ordered weekly influence series:

1. `theta_hat = mean(x_w)`.
2. Null-center the weekly series: `y_w = x_w - theta_hat`.
3. Form every contiguous **non-circular** block of length `L_weeks`.
4. For each bootstrap replication, draw blocks with replacement, concatenate in draw order, and
   truncate to exactly `W` weeks.
5. `delta_b = mean(resampled y_w)` is one null-centered sampling-error draw.
6. Use a deterministic project seed:

```text
seed = sha256("CSPV1R02|profile_identity|hypothesis_test_id|cohort") -> uint32
```

7. Use `B=49,999` replications. This is an engineering Monte-Carlo budget, not a claim of exact
   p-value precision. Report `B`, seed and the integer exceedance count.

One-sided positive-edge p-value:

```text
p_plus = (1 + count(delta_b >= theta_hat)) / (B + 1)
```

Basic bootstrap intervals from the same centered error distribution:

```text
one-sided 95% lower bound: LB95 = theta_hat - q_0.95(delta)
one-sided 95% upper bound: UB95 = theta_hat - q_0.05(delta)
two-sided 95% interval:     [theta_hat - q_0.975(delta), theta_hat - q_0.025(delta)]
```

Quantiles use one deterministic nearest-rank definition in the eventual machine profile.

This is an asymptotic dependence-aware procedure, not a finite-sample proof. Targeted independent
review must specifically attack the weekly influence construction, null centering, p-value and
interval construction, and `L_weeks=span_weeks_p90` choice before lock.

### 6.3 Minimum support / algorithmic sufficiency floors

All must hold before a cohort may return a statistical `PASS` or evidence-based `FAIL`:

```text
S1  N_completed_round_trips >= 20
S2  distinct_active_exit_weeks >= 6
S3  W_calendar_weeks >= 4 * L_weeks
S4  right_censored_in_cohort_positions == 0
S5  bootstrap_error_distribution is finite and non-degenerate
```

Failure of S1-S5 => `INSUFFICIENT_EVIDENCE`, not `FAIL`.

**Interpretation of 20 / 6 / 4:** these are deliberately small v1 governance/algorithmic support
floors to prevent a handful of observations or fewer than several dependence-length blocks from
being packaged as strong evidence. They are **not CLT thresholds, not power guarantees, and not
claims that 20 trades or 6 weeks are statistically sufficient in general**. Detectability is
handled by the actual resampled uncertainty and the capacity envelope in §7. These three numbers
remain candidate choices until the targeted delta review accepts or replaces them.

No fixed `D_days`, count-concentration percentage, `open_ratio`, or ESS threshold survives from the
first candidate.

---

## 7. Detectability / power capacity — separate from economic materiality

### 7.1 Economic materiality

For common v1, economic materiality is defined narrowly and audibly:

> **positive expected net per-round-trip return after the exact pre-registered base execution
> costs and slippage.**

There is no extra universal `2 bp` floor in the revised candidate. A tiny positive edge is not
accepted merely because its point estimate is positive; it must survive dependence-aware inference,
whole-wave multiplicity, and the robustness guards in §9. Economic magnitude in bp/trade and
break-even cost margin are always reported.

### 7.2 No-outcome standardized capacity envelope

Before any candidate outcome is inspected, the project can state an **optimistic IID normal
approximation** for planning only:

```text
MDE_80 / sigma ~= [ z_(1 - 0.05/M) + z_0.80 ] / sqrt(N)
```

where `M` is the locked Research Wave hypothesis count. This uses the most stringent first Holm
threshold `0.05/M`, ignores time dependence, and therefore is an optimistic lower-bound style
planning diagnostic rather than the acceptance test.

| N | M=1 | M=5 | M=20 |
| ---: | ---: | ---: | ---: |
| 20 | 0.556 sigma | 0.708 sigma | 0.816 sigma |
| 40 | 0.393 sigma | 0.501 sigma | 0.577 sigma |
| 60 | 0.321 sigma | 0.409 sigma | 0.471 sigma |
| 120 | 0.227 sigma | 0.289 sigma | 0.333 sigma |
| 240 | 0.161 sigma | 0.204 sigma | 0.236 sigma |

The table intentionally uses **standardized effect / sigma**, not invented project volatility
values. Real block dependence, sparse weeks and robustness constraints can only make detection
harder.

Consequences:

- `INSUFFICIENT_EVIDENCE` means the governed evidence/profile cannot resolve the required claim;
  it never means "edge proven absent";
- a large Research Wave can materially reduce power before any outcomes are seen;
- if a planned wave has obviously unacceptable capacity, redesign must occur **before** outcome
  exposure; outcomes may never be used to tune this profile or its thresholds.

---

## 8. Whole-wave multiplicity

### 8.1 Error-rate target

```text
ERROR_RATE_TARGET = strong family-wise error rate (FWER) <= 0.05
FAMILY = all outcome-registered hypothesis_test_id values in one locked RESEARCH_WAVE
DECISION_TARGET = individual playbook/hypothesis acceptance, not merely "at least one winner"
```

### 8.2 v1 method: Holm step-down

The revised candidate keeps **Holm step-down** as the v1 candidate method because it:

- strongly controls FWER without requiring independence among hypotheses;
- is deterministic and easy to audit;
- consumes ordinary per-hypothesis p-values;
- does not require a joint cross-hypothesis resampling implementation before the project has
  evidence that the extra complexity is necessary.

Holm is still **not locked** until targeted review passes.

Corrected Romano-Wolf statement: Romano-Wolf stepdown is a valid resampling-based multiple-testing
approach for a family of hypotheses and can exploit dependence among test statistics; it is not
limited to argmax/best-of reporting. It may be more powerful than Holm for correlated hypotheses.
It remains a future refinement candidate, not a current v1 requirement.

### 8.3 Machine-consistent counting taxonomy

The statistical denominator is exactly the locked Research Wave denominator:

```text
M = len(ResearchWaveManifest.tested_hypothesis_test_ids)
COUNTING_UNIT = one hypothesis_test_id
```

One `hypothesis_test_id` is required for every outcome-inspected hypothesis that could receive its
own project conclusion.

Count separately:

- each PRIMARY branch outcome test;
- each outcome-tested alternative interpretation;
- each instrument/timeframe/context variant if it is outcome-tested and can be separately
  accepted/rejected;
- each parameterization whose candidate outcome is inspected separately.

A parameter grid/search is **not** laundering-safe merely because it has one
`parameter_search_identity`. For v1 simplicity, if candidate outcomes for multiple parameter points
are inspected, each inspected point must be represented by a counted hypothesis unless a separate
pre-registered within-search max-statistic correction is explicitly designed and identity-bound.
No such within-grid correction is part of v1.

Do not count:

- deterministic unit/integration implementation checks that never inspect candidate outcomes;
- nuisance code refactors proven outcome-equivalent under the same frozen artifact identity.

Any outcome-informed new branch/scope/parameterization after first look is a new wave/search event
under the frozen protocol. `FAIL`, `INSUFFICIENT_EVIDENCE` and `DATA_BLOCKED` registrations remain
in the immutable wave denominator.

---

## 9. Robustness and failure guards

### 9.1 Mandatory execution/risk failure

```text
R1: any forced liquidation or maintenance-margin breach in the evaluated cohort -> FAIL
```

Forced-liquidation PnL remains in the round-trip sample; the risk fact independently prevents
acceptance. Use authoritative engine breach/liquidation facts, not a reconstructed equity path that
could be polluted by TD-002.

No global max-drawdown threshold is introduced in common v1. Equity/drawdown diagnostics cannot be
final-quality until TD-002 is repaired and a multi-day portfolio/equity path exists where required.

### 9.2 One-event / one-window edge fragility

A hypothesis may not `PASS` if its positive mean changes sign when one event or one exit week is
removed.

Compute:

```text
LOTO_MIN_MEAN = minimum mean(r) after deleting each single trade once
LOWO_MIN_MEAN = minimum mean(r) after deleting each active exit week once
```

For `PASS`:

```text
LOTO_MIN_MEAN > 0
LOWO_MIN_MEAN > 0
```

If the statistical positive-edge test would otherwise pass but either robustness condition fails,
return `INSUFFICIENT_EVIDENCE`, not `FAIL`: the evidence is too concentrated to resolve a durable
positive-edge claim.

This replaces the first candidate's arbitrary 40% single-trade PnL concentration threshold and the
reviewer's proposed but unaccepted time-window percentage threshold. It has no tuned concentration
percentage.

---

## 10. Cost and slippage treatment

### 10.1 Base acceptance path

Every outcome evaluation uses the exact pre-registered execution/capital/offset-cost assumption
identities. Base net return already includes:

- additive fees/offset costs through `additive_fee_i`;
- slippage through the executed fill prices embedded in `gross_realized_i`.

Changing base fee/slippage assumptions after outcome exposure creates a new outcome-affecting
artifact/search event under existing frozen rules.

### 10.2 No universal `2x friction` hard gate

The revised candidate removes the universal `2x cost` hard gate because additive fees and slippage
are structurally different and the first candidate had no measurement basis for treating fee
doubling as universal friction doubling.

Mandatory economic diagnostics instead include:

```text
gross_return_mean = mean(gross_realized_i / entry_notional_i)
fee_return_mean   = mean(additive_fee_i / entry_notional_i)
net_return_mean   = gross_return_mean - fee_return_mean
```

If `fee_return_mean > 0`, report the analytic additive-fee break-even multiplier:

```text
fee_break_even_multiplier = gross_return_mean / fee_return_mean
```

This is a diagnostic margin, not a hard threshold.

Any slippage stress must be a separately identity-bound execution rerun because slippage changes
fill prices and can change fill eligibility/trade count. It cannot be emulated by multiplying the
additive fee term. Such sensitivity runs are diagnostic unless a future pre-outcome profile version
explicitly makes one a hard gate.

---

## 11. Decision states and fixed decision order

The evaluator uses the following ordered states:

```text
DATA_BLOCKED
INTEGRITY_FAIL
INSUFFICIENT_EVIDENCE
FAIL
PASS
```

### Step 0 — DATA / ENGINE GOVERNANCE

Return `DATA_BLOCKED` before statistical evaluation if a required governed fact or trusted engine
primitive is unavailable. Current concrete examples:

- LIMIT-001 blocks affected real confirmatory execution when required historical price-limit facts
  are missing;
- wrong/non-authoritative trading-day semantics are not silently substituted for
  `SessionMetadata`;
- invalid/missing round-trip denominator/cost/contract identity cannot be guessed.

`DATA_BLOCKED` is not evidence against the playbook and remains in the pre-registered wave
accounting.

TD-002 does **not** block the revised primary trade-level estimand because final realized round-trip
PnL is not polluted; it does block any final-quality diagnostic that depends on the corrupted
partial-close equity/unrealized path.

### Step 1 — INTEGRITY

Any frozen chronology/exposure/PRIMARY/scope/search/wave/profile identity violation ->
`INTEGRITY_FAIL`.

### Step 2 — MINIMUM SUPPORT / CENSORING

Any S1-S5 failure from §6.3 -> `INSUFFICIENT_EVIDENCE`.

### Step 3 — MANDATORY RISK

Any R1 forced-liquidation/maintenance breach -> `FAIL`.

### Step 4 — POSITIVE-EDGE INFERENCE

Compute each hypothesis `p_plus`, then apply Holm over the complete locked wave.

If Holm rejects `H0: theta <= 0`, continue to Step 5.

If Holm does not reject:

- if the one-sided 95% upper bound `UB95 <= 0`, return `FAIL` (evidence supports non-positive
  mean net edge under the common estimand);
- otherwise return `INSUFFICIENT_EVIDENCE` (the cohort/profile cannot resolve the sign).

This is the central semantic correction from the first candidate: **failure to prove positive edge
is not automatically evidence of no edge.**

### Step 5 — CONCENTRATION ROBUSTNESS

If `LOTO_MIN_MEAN <= 0` or `LOWO_MIN_MEAN <= 0` -> `INSUFFICIENT_EVIDENCE`.

Otherwise -> `PASS` for the statistical common contract of that cohort.

Mandatory reporting for any evaluated hypothesis:

- `theta_hat` in raw return and bp/trade;
- one-sided LB95 / UB95 and two-sided 95% interval;
- raw `p_plus`, Holm rank/threshold/adjusted result;
- `N`, active exit weeks, `L_weeks`, holding-span diagnostics;
- right-censored count;
- LOTO/LOWO minima;
- forced-liquidation/margin-breach facts;
- gross/fee/net return means and fee break-even multiplier;
- full wave denominator `M` and every registered terminal/disposition state.

---

## 12. DEVELOPMENT / VALIDATION / HISTORICAL FINAL behavior

The same locked profile identity must govern all stages. No stage may silently change the method.

### DEVELOPMENT

Candidate outcome access remains unauthorized today. When a real profile/wave is later locked and
DEVELOPMENT access is granted by the pre-outcome gate, this evaluator may produce development
statistics for the frozen artifact. Development evidence does not itself create project acceptance
and may not be used to change this locked statistical profile after seeing results.

### VALIDATION

Currently `LOCKED`. When separately authorized under frozen prerequisites, VALIDATION is the first
protected acceptance cohort. CAT1/CAT2/CAT3 revision rules remain exactly as frozen in Protocol
v1.0.

### PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT

Currently `LOCKED`. A separate final-holdout unlock authority is required. The final cohort stands
on its own under the same profile; it is not pooled with DEVELOPMENT/VALIDATION to manufacture
sufficiency. Exposure remains irreversible.

Future Shadow/Forward remains a separate, later-authorized genuinely prospective path.

---

## 13. Implementation identity and engineering deltas after design acceptance

Do **not** implement the full evaluator before this revision survives targeted independent review.
After acceptance, the ordinary engineering package should provide:

1. deterministic round-trip ledger keyed by `position_id`;
2. exact entry-notional/gross-realized/additive-fee attribution with one cost source;
3. `SessionMetadata`-only holding-day/week helpers and TD-001 isolation;
4. cohort boundary/censoring classification;
5. weekly influence-series materialization;
6. deterministic non-circular moving-block bootstrap + seed/quantile implementation;
7. Holm step-down over the locked `hypothesis_test_id` denominator;
8. LOTO/LOWO robustness calculations;
9. `DATA_BLOCKED / INTEGRITY_FAIL / INSUFFICIENT_EVIDENCE / FAIL / PASS` evaluator;
10. canonical machine-readable profile document whose exact content hash is bound into
    `CommonStatisticalProfile.profile_identity`;
11. synthetic/non-candidate tests only until a real profile is locked and the pre-outcome gate
    authorizes candidate DEVELOPMENT outcomes.

LIMIT-001 governed historical price-limit facts remain a separate data/governance prerequisite for
affected real confirmatory execution. TD-002 must be fixed before final-quality equity/drawdown path
evidence is used.

No new statistics framework or external runtime dependency is required by this candidate.

---

## 14. Primary statistical references and exact claims

- **Künsch (1989), The Annals of Statistics 17(3), 1217–1241, DOI
  `10.1214/aos/1176347265`** — foundational block-bootstrap treatment for dependent stationary
  observations. Supports contiguous-block resampling as a dependence-aware approach; does not
  prescribe this project's weekly representation or block length.
- **Politis & Romano (1992), A Circular Block-Resampling Procedure for Stationary Data** — supports
  block resampling for stationary dependent data and the circular variant. This revision deliberately
  uses **non-circular** blocks to avoid joining the frozen cohort's first and last weeks.
- **Holm (1979), Scandinavian Journal of Statistics 6(2), 65–70** — sequentially rejective
  multiple testing with family-wise type-I error protection. Supports the simple v1 whole-wave FWER
  method; does not solve power limitations.
- **Romano & Wolf (2005), Econometrica 73(4), 1237–1282, DOI
  `10.1111/j.1468-0262.2005.00615.x`** — stepwise multiple testing with FWER control that can use
  the joint dependence structure and is not limited to argmax/best-of reporting. Supports correcting
  the first candidate's description and retaining Romano-Wolf as a potential more-powerful future
  refinement.
- **Lahiri (2003), Resampling Methods for Dependent Data, Springer** — general reference for
  bootstrap/resampling under dependent observations; does not make the small 24-month project sample
  magically large or validate any project-specific threshold.

References justify method families, not project-specific numeric choices. The targeted delta review
must still decide whether the v1 weekly influence/bootstrap construction and small support floors are
acceptable for this project.

---

## 15. Targeted-delta review questions

The next independent reviewer should focus only on the materially changed definitions:

1. Is `x_w=(W/N)*sum(exit-week r_i)` a defensible way to retain the per-trade estimand while
   putting inactivity/time clustering into inference?
2. Is null-centered non-circular moving-block bootstrap as specified a valid enough v1 test/CI path,
   or is a studentized/restricted alternative necessary?
3. Is `L_weeks=span_weeks_p90` defensible, and is `W>=4L` enough/too much/too little?
4. Are the minimal `N>=20` and six-active-week floors acceptable as explicit governance floors, or
   should one/both be removed/replaced?
5. Does zero right-censoring avoid more bias than it creates for multi-day playbooks?
6. Is the three-way evidence interpretation correct: positive evidence -> PASS, sufficiently
   negative evidence -> FAIL, unresolved sign -> INSUFFICIENT_EVIDENCE?
7. Does LOTO/LOWO sign robustness adequately replace arbitrary concentration percentages for v1?
8. Is removing both the 2 bp universal floor and the universal 2x hard cost gate defensible given
   that base returns are already net of pre-registered realistic execution friction?
9. Is the v1 counting taxonomy sufficiently conservative against parameter-grid/search laundering?
10. Is Holm the correct simplest v1 choice given the corrected Romano-Wolf interpretation?

The reviewer must not treat the prior reviewer's `RECOMMENDED_SIMPLIFIED_V1` as authority and must
not inspect candidate outcomes.

---

## 16. Revision candidate verdict

```text
COMMON_STATISTICAL_PROFILE_V1=REVISION_CANDIDATE_NOT_LOCKED
PROFILE_DIRECTION=KEEP
ADJUDICATED_CRITICALS_ADDRESSED_IN_DESIGN=YES
ADJUDICATED_HIGHS_ADDRESSED_IN_DESIGN=YES
NO_CANDIDATE_OUTCOME_DATA_USED=YES
FROZEN_PROTOCOL_CONFLICT=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
NEXT_STAGE=TARGETED_INDEPENDENT_DELTA_REVIEW
```

This document is not project acceptance and does not lock a statistical profile. It is the bounded
revision candidate that now requires independent targeted review before any lock/implementation
acceptance decision.

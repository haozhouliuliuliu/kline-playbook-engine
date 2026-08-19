# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE

> Date: 2026-08-19
> Work package: `COMMON_STATISTICAL_PROFILE_V1_REVISION_AFTER_PARALLEL_REVIEW`
> Status: `REVISION_CANDIDATE / NOT_LOCKED / TARGETED_DELTA_REVIEW_REQUIRED`
> Supersedes for active design review only: `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md`
> Frozen authority unchanged: Research Protocol v1.0 + frozen 12/6/6 chronology
> Adjudication authority: `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`

```text
COMMON_STATISTICAL_PROFILE_V1_REVISION_VERSION=v1.0-revision-candidate-0.3
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

The prior revision draft (`candidate-0.2`) briefly proposed a weekly moving-block bootstrap. A
synthetic-only methodological smoke test found unacceptable short-sample sensitivity under simple
serial-dependence fixtures, so that method was rejected **before independent review and before any
candidate outcome**. `candidate-0.3` replaces it with a tuning-parameter-free self-normalized test
over the complete authoritative trading-day sequence.

---

## 1. Design objective

The profile must answer the frozen common contract for every registered Human Playbook hypothesis:

1. **Economic edge:** is the PRIMARY branch positively profitable after the exact pre-registered
   base execution costs/slippage, with uncertainty treated explicitly?
2. **Evidence sufficiency:** is there enough temporally distributed governed evidence for the
   dependence-aware inference to be credible?
3. **Risk/failure:** did mandatory execution/risk failure conditions occur, and is the apparent
   edge robust to one trade or one narrow time window carrying the sign?
4. **Integrity:** were chronology, exposure, PRIMARY, scope/search identity, Research Wave and
   multiplicity rules preserved?

The revised v1 objective is deliberately narrow: use the smallest common statistical machinery
that can distinguish positive evidence, negative evidence and unresolved evidence without a large
set of arbitrary hard thresholds.

---

## 2. Explicit adjudication changes from the first candidate

The following first-candidate rules are **removed** from the lock candidate:

- `ESS=N/max(1,2H-1)` as a hard sufficiency gate;
- hard `N>=60`, `D_days>=30`, `W_active>=8`, 50% day concentration, 75% week concentration and
  `open_ratio<=0.25` as an interacting sufficiency system;
- `MIN_ECONOMIC_EDGE=2 bp` as an extra universal economic floor;
- `2x cost` as a universal hard execution-friction gate;
- the claim that Romano-Wolf stepdown matters only for argmax/best-of reporting;
- circular/non-circular block-bootstrap choice and all block-length tuning.

The revised candidate replaces them with:

- one explicit round-trip identity and cohort-boundary rule;
- a complete trading-day score process including zero-exit days;
- Shao-style scalar self-normalization for a ratio estimand, which requires no bandwidth/block
  length;
- a small set of support floors explicitly labeled governance choices rather than statistical
  laws;
- a no-outcome standardized detectability envelope;
- `PASS / FAIL / INSUFFICIENT_EVIDENCE` evidence interpretation plus separate `DATA_BLOCKED` and
  `INTEGRITY_FAIL` states;
- leave-one-trade and leave-one-week robustness guards instead of tuned PnL concentration
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

This is compatible with the existing deterministic engine lifecycle recorded by the accepted
engine audit/crosswalk.

### 3.2 Per-round-trip quantities

For round trip `i`:

```text
entry_notional_i = sum over OPEN/ADD legs of
                   abs(fill_price * contract_multiplier * opened_quantity)

gross_realized_i = sum of CapitalTransition.realized_pnl_change
                   over all REDUCE/CLOSE/FORCED_LIQUIDATION legs

additive_fee_i    = sum of one authoritative charged/required-cost source exactly once
                   over the round-trip transitions

r_i               = (gross_realized_i - additive_fee_i) / entry_notional_i
```

`entry_notional_i` must be positive. Missing/invalid denominator, cost or contract identity is
`DATA_BLOCKED`; it is never silently imputed.

**Cost-source guard:** the ledger must not sum both `ExecutionOutcome.total_cost` and
capital charged-cost deltas for the same fill.

**Slippage is not additive fee.** In the current engine, synthetic slippage changes fill price and
is already embedded in `gross_realized_i`. It must not be mislabeled as part of the post-hoc
additive fee term.

### 3.3 Primary estimand

```text
PRIMARY_ESTIMAND = theta = E[sum of net normalized round-trip returns / number of round trips]
SAMPLE_ESTIMATE  = theta_hat = sum_i(r_i) / N
```

Equal weighting is per completed round trip after notional normalization. This is a **per-decision
quality estimand**: it asks whether taken trades have positive net edge after pre-registered base
friction. It is not a capital-productivity, annualized-return, turnover, opportunity-cost or
portfolio-growth estimand. Those may be diagnostics later but do not replace common v1.

Zero-trade days are not fabricated as 0% trades. They enter the time-series inference correctly
through a zero daily trade count and zero daily return sum in §6.

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
  hypothesis in v1, because selecting only completed positions can create completion bias;
- no post-cohort price/outcome may be read merely to finish a cohort trade;
- no Validation/final data may be borrowed backward into an earlier cohort.

This zero-right-censor rule is intentionally strict and has no percentage knob. A future profile
may adopt a formally justified censoring procedure; v1 does not invent one.

---

## 5. Holding horizon and multi-week semantics

For completed round trip `i`:

```text
H_days_i = number of distinct authoritative trading days from first open through terminal close,
           inclusive; same-trading-day round trip => H_days_i = 1

span_weeks_i = number of distinct ISO calendar weeks touched by those authoritative trading days,
               inclusive
```

Mandatory structural diagnostics:

```text
H_days_median
H_days_p90
H_days_max
span_weeks_p90
span_weeks_max
```

Percentiles use deterministic nearest-rank ordering. Holding horizon is not converted into a guessed
ESS and does not select a bootstrap block length. Multi-day positions can induce dependence in the
daily score process; the self-normalizer in §6 is chosen specifically to avoid pretending that a
fixed horizon-to-ESS conversion is exact.

For day/week concentration diagnostics and leave-one-window robustness, the full round-trip `r_i`
is attributed to the authoritative terminal-close trading day/week. This is an accounting
attribution, not a claim that all economic dependence arose at exit.

---

## 6. Dependence-aware inference: complete trading-day score + self-normalization

### 6.1 Complete daily score process

Let `D` be the full ordered sequence of authoritative trading days in the evaluated cohort,
including days with no completed exits.

For each trading day `d`:

```text
C_d = number of eligible round trips whose terminal close trading day is d
S_d = sum(r_i for those eligible round trips)
```

No-exit trading day:

```text
C_d = 0
S_d = 0
```

Then:

```text
N = sum_d C_d
sum_d S_d = sum_i r_i
theta_hat = sum_d S_d / sum_d C_d
```

This is a ratio-of-means representation. It preserves the per-trade point estimand without treating
products as independent samples, while the complete chronological day sequence retains inactivity
and time clustering.

### 6.2 Score process for testing any candidate theta0

For a candidate value `theta0`, define the scalar daily score:

```text
Z_d(theta0) = S_d - theta0 * C_d
```

If the ratio estimand equals `theta0` and the long-run mean daily trade count is positive, then the
population mean of `Z_d(theta0)` is zero. This avoids treating the realized `N` as a fixed design
quantity inside the time-series variance calculation.

For the positive-edge null `H0: theta <= 0`, the boundary test uses `theta0=0`, so:

```text
Z_d(0) = S_d
```

### 6.3 Scalar self-normalized statistic

For the ordered score series `Z_1,...,Z_D` at a fixed `theta0`:

```text
Z_bar(theta0) = D^-1 * sum_d Z_d(theta0)

A_t(theta0) = sum_{j=1}^t [Z_j(theta0) - Z_bar(theta0)]

V_D(theta0) = D^-2 * sum_{t=1}^D A_t(theta0)^2

T_SN(theta0) = sqrt(D) * Z_bar(theta0) / sqrt(V_D(theta0))
```

If `V_D(theta0) <= 0`, non-finite, or numerically degenerate, the result is
`INSUFFICIENT_EVIDENCE`, not a fabricated infinite t-statistic.

For the simple sample-mean score, the linearization remainder is exactly zero. The required
statistical assumption is therefore the functional central-limit behavior / weak-dependence
condition for the daily score process plus positive long-run variance; this is an assumption of the
inference method, not something the project can certify from a short cohort.

Under the corrected Shao (2010) self-normalization result for the scalar mean case, the limiting
signed pivotal variable is:

```text
T_infinity = B(1) / sqrt( integral_0^1 [B(r) - r B(1)]^2 dr )
```

and `T_infinity^2 = U_1` in the paper's notation. The distribution is symmetric and does not
contain an estimated long-run variance or user-chosen bandwidth/block length.

### 6.4 Pivotal calibration artifact

Holm needs ordinary per-hypothesis p-values. Before profile lock, the project must create and
independently verify a **candidate-outcome-free immutable pivotal calibration artifact** for the
signed `T_infinity` distribution.

The locked artifact must record at least:

```text
PIVOTAL_LAW = Brownian-motion functional above
CALIBRATION_GENERATOR_VERSION
RNG_ALGORITHM_AND_VERSION
SEED
BROWNIAN_GRID_RESOLUTION
MONTE_CARLO_REPLICATIONS
EMPIRICAL_CDF / TAIL LOOKUP REPRESENTATION
MONTE_CARLO_ERROR_POLICY
SHA256
```

For observed `T_SN(0)`:

```text
p_plus = P(T_infinity >= T_SN(0))
```

computed only from the locked calibration artifact. Runtime must not regenerate a different
calibration or tune simulation settings per hypothesis.

Two-sided and one-sided confidence bounds for `theta` are obtained by deterministic inversion of
`T_SN(theta0)` against the same locked signed-pivotal CDF. Because `V_D(theta0)` changes with
`theta0`, bounds are solved numerically by a deterministic bracket/root rule that is also part of
the eventual machine profile identity.

`candidate-0.3` does **not** pretend the calibration artifact already exists. Its exact numerical
generation/error policy is a pre-lock statistical implementation detail that the targeted
independent review must approve before profile lock.

### 6.5 Minimum support / algorithmic floors

All must hold before a cohort may return a statistical `PASS` or evidence-based `FAIL`:

```text
S1  N_completed_round_trips >= 20
S2  distinct_active_exit_weeks >= 6
S3  right_censored_in_cohort_positions == 0
S4  V_D(0) is finite and strictly positive
S5  locked pivotal calibration artifact is present and identity-matched
```

Failure of S1-S5 => `INSUFFICIENT_EVIDENCE` except a missing/mismatched required governed artifact,
which is `DATA_BLOCKED` when the missing object is infrastructure/data authority rather than sample
support.

**Interpretation of 20 / 6:** these are deliberately small v1 governance support floors intended to
prevent a handful of completed observations or a few isolated weeks from being packaged as strong
evidence. They are **not CLT thresholds, power guarantees, or claims of general statistical
sufficiency**. They remain candidate choices until targeted review accepts/removes/replaces them.
Actual uncertainty comes from the daily score path and self-normalization; detectability is reported
separately in §7.

No fixed distinct-day minimum, count-concentration percentage, open-ratio percentage, ESS threshold
or block-count threshold survives from the first candidate.

---

## 7. Detectability / capacity — separate from economic materiality

### 7.1 Economic materiality

For common v1, economic materiality is defined narrowly:

> **positive expected net per-round-trip return after the exact pre-registered base execution costs
> and slippage.**

There is no extra universal `2 bp` floor in this revision. A tiny positive point estimate cannot
pass merely by being positive; it must survive the dependence-aware test, whole-wave multiplicity
and robustness guards. Economic magnitude in bp/trade and break-even cost margins are mandatory
reports.

### 7.2 No-outcome standardized planning envelope

Before candidate outcomes, an **optimistic IID normal approximation** can be published for capacity
planning only:

```text
MDE_80 / sigma ~= [z_(1 - 0.05/M) + z_0.80] / sqrt(N)
```

where `M` is the locked Research Wave hypothesis count. It uses the most stringent first Holm
threshold `0.05/M` and ignores serial dependence, time clustering, censoring and robustness guards;
it therefore describes an optimistic planning envelope, not the acceptance test.

| N | M=1 | M=5 | M=20 |
| ---: | ---: | ---: | ---: |
| 20 | 0.556 sigma | 0.708 sigma | 0.816 sigma |
| 40 | 0.393 sigma | 0.501 sigma | 0.577 sigma |
| 60 | 0.321 sigma | 0.409 sigma | 0.471 sigma |
| 120 | 0.227 sigma | 0.289 sigma | 0.333 sigma |
| 240 | 0.161 sigma | 0.204 sigma | 0.236 sigma |

The table intentionally uses standardized effect / sigma, not invented project volatility values.
Real dependence can make detection harder.

Consequences:

- `INSUFFICIENT_EVIDENCE` means the governed cohort/profile cannot resolve the claim; it never
  means edge proven absent;
- larger Research Waves reduce capacity before any outcomes are seen;
- if a planned wave has obviously inadequate capacity, redesign must occur **before** outcome
  exposure; candidate outcomes may never tune this profile or its thresholds.

---

## 8. Whole-wave multiplicity

### 8.1 Error-rate target

```text
ERROR_RATE_TARGET = strong family-wise error rate (FWER) <= 0.05
FAMILY = all outcome-registered hypothesis_test_id values in one locked RESEARCH_WAVE
DECISION_TARGET = individual playbook/hypothesis acceptance, not merely "at least one winner"
```

### 8.2 v1 candidate method: Holm step-down

`candidate-0.3` keeps **Holm step-down** as the v1 candidate because it:

- strongly controls FWER without requiring independent hypothesis tests;
- is deterministic and auditable once ordinary p-values exist;
- avoids a joint cross-hypothesis resampling implementation before the project has evidence that
  the extra complexity is worth it.

Holm is still **not locked** until targeted independent review passes.

Corrected Romano-Wolf statement: Romano-Wolf stepdown is a resampling-based multiple-testing method
for a family of hypotheses that can exploit dependence among test statistics while controlling
FWER; it is not limited to argmax/best-of reporting. It may be more powerful than Holm for strongly
correlated hypotheses. It remains a future refinement candidate, not a current v1 requirement.

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
- each instrument/timeframe/context variant if outcome-tested and separately decidable;
- each parameterization whose candidate outcome is inspected separately.

A parameter grid/search is **not** laundering-safe merely because it shares one
`parameter_search_identity`. For v1 simplicity, if multiple parameter-point candidate outcomes are
inspected, each inspected point must be represented by a counted hypothesis unless a separate
pre-registered within-search max-statistic/multiple-testing correction is designed and
identity-bound. No such within-grid correction is part of v1.

Do not count:

- deterministic unit/integration implementation checks that never inspect candidate outcomes;
- nuisance code refactors proven outcome-equivalent under the same frozen artifact identity.

Any outcome-informed new branch/scope/parameterization after first look is a new wave/search event
under frozen Protocol v1.0. `FAIL`, `INSUFFICIENT_EVIDENCE` and `DATA_BLOCKED` registrations remain
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

A hypothesis may not `PASS` if its positive sample mean changes sign when one event or one exit week
is removed.

Compute:

```text
LOTO_MIN_MEAN = minimum mean(r) after deleting each single round trip once
LOWO_MIN_MEAN = minimum mean(r) after deleting each active terminal-close ISO week once
```

For `PASS`:

```text
LOTO_MIN_MEAN > 0
LOWO_MIN_MEAN > 0
```

If the multiplicity-adjusted positive-edge test would otherwise pass but either robustness
condition fails, return `INSUFFICIENT_EVIDENCE`, not `FAIL`: the available evidence is too
concentrated to resolve a durable positive-edge claim.

This replaces the first candidate's arbitrary 40% single-trade PnL concentration threshold and the
prior reviewer's proposed-but-unaccepted time-window percentage threshold. It has no tuned
concentration percentage.

---

## 10. Cost and slippage treatment

### 10.1 Base acceptance path

Every outcome evaluation uses the exact pre-registered execution/capital/offset-cost assumption
identities. Base net return includes:

- additive fees/offset costs through `additive_fee_i`;
- slippage through executed fill prices embedded in `gross_realized_i`.

Changing base fee/slippage assumptions after outcome exposure creates a new outcome-affecting
artifact/search event under existing frozen rules.

### 10.2 No universal `2x friction` hard gate

This revision removes the universal `2x cost` hard gate because additive fees and slippage are
structurally different and no measurement basis justified treating fee doubling as universal
friction doubling.

Mandatory diagnostics:

```text
gross_return_mean = mean(gross_realized_i / entry_notional_i)
fee_return_mean   = mean(additive_fee_i / entry_notional_i)
net_return_mean   = gross_return_mean - fee_return_mean
```

If `fee_return_mean > 0`, report:

```text
fee_break_even_multiplier = gross_return_mean / fee_return_mean
```

This is an economic-margin diagnostic, not a hard pass threshold.

Any slippage stress must be a separately identity-bound execution rerun because slippage changes
fill prices and can alter fills/trade count. It cannot be emulated by multiplying additive fees.
Such sensitivity runs are diagnostics unless a future pre-outcome profile version explicitly makes
one a hard gate.

---

## 11. Decision states and fixed decision order

The evaluator uses:

```text
DATA_BLOCKED
INTEGRITY_FAIL
INSUFFICIENT_EVIDENCE
FAIL
PASS
```

### Step 0 — DATA / ENGINE GOVERNANCE

Return `DATA_BLOCKED` before statistical evaluation if a required governed fact or trusted engine
primitive is unavailable. Current examples:

- LIMIT-001 blocks affected real confirmatory execution when required historical price-limit facts
  are missing;
- wrong/non-authoritative trading-day semantics are not substituted for `SessionMetadata`;
- invalid/missing round-trip denominator/cost/contract identity is not guessed;
- required locked pivotal-calibration identity is missing/mismatched.

`DATA_BLOCKED` is not evidence against the playbook and remains in Research Wave accounting.

TD-002 does **not** block the revised primary trade-level estimand because final realized round-trip
PnL is not polluted; it does block final-quality diagnostics that depend on the corrupted
partial-close equity/unrealized path.

### Step 1 — INTEGRITY

Any frozen chronology/exposure/PRIMARY/scope/search/wave/profile identity violation ->
`INTEGRITY_FAIL`.

### Step 2 — MINIMUM SUPPORT / CENSORING

Any sample-support S1-S4 failure from §6.5 -> `INSUFFICIENT_EVIDENCE`.

### Step 3 — MANDATORY RISK

Any R1 forced-liquidation/maintenance breach -> `FAIL`.

### Step 4 — POSITIVE-EDGE INFERENCE

For every hypothesis, compute raw one-sided `p_plus` from the locked signed-SN pivotal calibration;
then apply Holm across the complete locked wave.

If Holm rejects `H0: theta <= 0`, continue to Step 5.

If Holm does not reject:

- if the unadjusted one-sided 95% upper confidence bound for `theta` is `<=0`, return `FAIL`
  (the cohort provides evidence for non-positive mean net edge under this estimand);
- otherwise return `INSUFFICIENT_EVIDENCE` (the cohort/profile cannot resolve the sign).

Failure to prove positive edge is therefore **not automatically FAIL**.

### Step 5 — CONCENTRATION ROBUSTNESS

If `LOTO_MIN_MEAN <= 0` or `LOWO_MIN_MEAN <= 0` -> `INSUFFICIENT_EVIDENCE`.

Otherwise -> `PASS` for the common statistical contract of that cohort.

Mandatory reporting for any evaluated hypothesis:

- `theta_hat` in raw return and bp/trade;
- self-normalized one-sided lower/upper bounds and two-sided 95% interval;
- raw `p_plus`, Holm rank/threshold/adjusted result;
- `N`, active exit days/weeks, all cohort trading days;
- holding-horizon/span diagnostics;
- right-censored count;
- LOTO/LOWO minima;
- forced-liquidation/margin-breach facts;
- gross/fee/net return means and fee break-even multiplier;
- pivotal calibration identity;
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
3. `SessionMetadata`-only cohort trading-day sequence and TD-001 isolation;
4. cohort boundary/censoring classification;
5. daily `(S_d,C_d)` score materialization including zero-exit trading days;
6. deterministic self-normalized statistic + confidence-bound inversion;
7. immutable signed-pivotal calibration artifact + generator/evidence + identity binding;
8. Holm step-down over locked `hypothesis_test_id` denominator;
9. LOTO/LOWO robustness calculations;
10. `DATA_BLOCKED / INTEGRITY_FAIL / INSUFFICIENT_EVIDENCE / FAIL / PASS` evaluator;
11. canonical machine-readable profile whose exact content/calibration hashes bind into
    `CommonStatisticalProfile.profile_identity`;
12. synthetic/non-candidate tests only until a real profile is locked and the pre-outcome gate
    authorizes candidate DEVELOPMENT outcomes.

LIMIT-001 governed historical price-limit facts remain a separate data/governance prerequisite for
affected real confirmatory execution. TD-002 must be fixed before final-quality equity/drawdown path
evidence is used.

No new statistics framework or external runtime dependency is required by this candidate.

---

## 14. Statistical references and exact claims

### Shao 2010 + corrigendum

Xiaofeng Shao, **A Self-Normalized Approach to Confidence Interval Construction in Time Series**,
*Journal of the Royal Statistical Society Series B* 72(3), 343–366, DOI
`10.1111/j.1467-9868.2009.00737.x`; corrigendum 72(5), 695–696, DOI
`10.1111/j.1467-9868.2010.00754.x`.

Relevant claim: the method forms a random normalization from recursive/cumulative estimates and
obtains an asymptotically pivotal limit without direct long-run-variance estimation or a chosen
bandwidth. In the scalar sample-mean case the normalizer reduces to the cumulative-demeaned-sum
formula used in §6. The corrigendum strengthens the remainder condition needed for the general
theorem. In this revision's direct sample-mean score application the linearization remainder is
zero, but the functional-CLT/weak-dependence and positive-long-run-variance assumptions still
matter.

This reference does **not** prove that the project's six-month score process is stationary, that
finite-sample size is exact, or that the candidate support floors are correct.

### Holm 1979

Sture Holm, **A Simple Sequentially Rejective Multiple Test Procedure**, *Scandinavian Journal of
Statistics* 6(2), 65–70.

Supports the simple sequentially rejective FWER procedure without an independence requirement among
hypotheses. It does not solve power limitations.

### Romano & Wolf 2005

Joseph P. Romano and Michael Wolf, **Stepwise Multiple Testing as Formalized Data Snooping**,
*Econometrica* 73(4), 1237–1282, DOI `10.1111/j.1468-0262.2005.00615.x`.

Supports the correction that resampling stepdown applies to a family of hypotheses and can exploit
joint dependence; it is not argmax-only. This revision does not adopt Romano-Wolf.

### Block-bootstrap literature retained as rejected-alternative context

Künsch (1989) and Politis/Romano block-resampling work remain relevant references for dependent
resampling, but `candidate-0.3` does not use block bootstrap because its block-length choice was an
avoidable free knob in this short-cohort setting and the synthetic-only smoke test did not justify
the drafted weekly MBB path.

References justify method families, not project-specific numerical support floors.

---

## 15. Targeted-delta review questions

The next independent reviewer should focus only on materially changed definitions:

1. Is the ratio estimand represented correctly by the complete daily `(S_d,C_d)` process?
2. Is testing `Z_d(theta0)=S_d-theta0*C_d` with scalar self-normalization a valid enough v1 path
   for the expected weak-dependence conditions, including the 2010 corrigendum?
3. Does the candidate overclaim stationarity/FCLT plausibility for a six-month futures score
   process, and what fail-closed/diagnostic boundary is needed if not?
4. Is the signed pivotal calibration/p-value approach statistically and numerically defensible,
   and what Monte-Carlo error policy must be frozen?
5. Are `N>=20` and six active exit weeks acceptable as explicit support floors, or should one/both
   be removed/replaced?
6. Does zero right-censoring avoid more bias than it creates for multi-day playbooks?
7. Is the evidence interpretation sound: positive multiplicity-adjusted evidence -> candidate
   PASS; sufficiently negative evidence -> FAIL; unresolved sign -> INSUFFICIENT_EVIDENCE?
8. Does LOTO/LOWO sign robustness adequately replace arbitrary concentration percentages for v1?
9. Is removing both the extra 2 bp universal floor and universal 2x hard-cost gate defensible when
   base outcomes are already net of identity-bound execution friction?
10. Is the v1 parameter/search counting taxonomy conservative enough against grid/search
    laundering?
11. Is Holm the correct simplest v1 choice given the corrected Romano-Wolf interpretation?
12. Do synthetic size/pathology tests reveal a failure mode large enough to reject self-normalized
    v1 before any candidate outcome access?

The reviewer must not treat the prior reviewer's `RECOMMENDED_SIMPLIFIED_V1` as authority and must
not inspect candidate outcomes.

---

## 16. Revision candidate verdict

```text
COMMON_STATISTICAL_PROFILE_V1=REVISION_CANDIDATE_NOT_LOCKED
PROFILE_DIRECTION=KEEP
ADJUDICATED_CRITICALS_ADDRESSED_IN_DESIGN=YES
ADJUDICATED_HIGHS_ADDRESSED_IN_DESIGN=YES
WEEKLY_MBB_DRAFT=REJECTED_PRE_OUTCOME_AFTER_SYNTHETIC_SMOKE_TEST
CURRENT_INFERENCE_CANDIDATE=DAILY_SCORE_SELF_NORMALIZATION
NO_CANDIDATE_OUTCOME_DATA_USED=YES
FROZEN_PROTOCOL_CONFLICT=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
NEXT_STAGE=TARGETED_INDEPENDENT_DELTA_REVIEW
```

This document is not project acceptance and does not lock a statistical profile. It now requires a
bounded independent targeted review before any lock or evaluator-implementation acceptance decision.

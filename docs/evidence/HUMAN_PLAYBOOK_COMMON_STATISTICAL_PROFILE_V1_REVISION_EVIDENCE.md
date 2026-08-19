# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_EVIDENCE

> Date: 2026-08-19
> Work package: `COMMON_STATISTICAL_PROFILE_V1_REVISION_AFTER_PARALLEL_REVIEW`
> Evidence for: `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE.md`
> Status: `REVISION_EVIDENCE_COMPLETE / NO_CANDIDATE_OUTCOME / TARGETED_REVIEW_REQUIRED`

## 1. Outcome-data integrity statement

This revision used no candidate-quality outcome data.

```text
REAL_HUMAN_PLAYBOOK_RUN=NO
CANDIDATE_PNL_INSPECTION=NO
EQUITY_CURVE_INSPECTION=NO
EXPECTANCY_INSPECTION=NO
SHARPE_INSPECTION=NO
WIN_LOSS_INSPECTION=NO
DEVELOPMENT_OUTCOME_CALIBRATION=NO
VALIDATION_ACCESS=NO
HISTORICAL_FINAL_HOLDOUT_ACCESS=NO
THRESHOLD_TUNING_ON_CANDIDATE_OUTCOMES=NO
```

Quantitative work was restricted to:
- algebra on candidate estimator/inference definitions;
- standardized no-outcome normal-approximation capacity arithmetic;
- synthetic stochastic fixtures generated independently of the canonical market corpus and all
  Human Playbook candidates;
- accepted engine-interface/evidence inspection;
- primary statistical literature/source verification.

No candidate-return variance, actual candidate trade frequency, candidate holding distribution,
canonical price path or candidate PnL was used to choose the revised rules.

## 2. Authority inspected

Binding/current authority used:
- `OWNER_COLLABORATION_CONTRACT.md`
- `ARCHITECTURE_BASELINE.md`
- `CURRENT_STATE.md`
- `RESEARCH_DIRECTION.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`
- `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_FINAL_ACCEPTANCE_V1_2.md`
- `docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md`
- `docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ENGINE_COMPATIBILITY_CROSSWALK.md`
- `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADVERSARIAL_REVIEW.md`
- `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`
- `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`

The prior independent review remains advisory. The project-brain adjudication is authority for
which findings became revision requirements.

## 3. Adjudication requirement -> candidate-0.3 response

| Adjudicated requirement | Revision response |
| --- | --- |
| Separate economic materiality from detectability | Materiality = positive net per-round-trip edge after pre-registered base friction; separate no-outcome standardized capacity envelope; unresolved sign is `INSUFFICIENT_EVIDENCE`, not automatic FAIL |
| Remove `2H-1` ESS hard gate | Removed completely; holding/span retained only as structural diagnostics; no deterministic ESS replacement |
| Pin round-trip semantics | One engine `position_id` = one observation; adds/partial closes aggregated; forced liquidation terminal; roll creates separate round trips |
| Pin holding/multi-week treatment | Inclusive authoritative trading-day/week-span definitions; final round-trip return assigned to terminal-close day/week for score/window accounting; dependence handled by tuning-free daily-score self-normalization rather than a horizon-derived block length |
| Justify/simplify sufficiency thresholds | First-candidate eight-knob sufficiency reduced to `N>=20`, six active exit weeks, zero right censoring, nondegenerate SN normalizer and valid calibration; 20/6 explicitly remain reviewable governance floors, not statistical laws |
| Distinguish fee vs slippage stress | Additive fee and fill-price slippage separated; universal `2x friction` hard gate removed; analytic fee break-even diagnostic; slippage stress requires a separate identity-bound execution rerun |
| Guard one event/window carrying edge | Leave-one-trade-out and leave-one-active-week-out sign robustness replace arbitrary PnL fractions |
| Add `DATA_BLOCKED` | First-class state before statistical decision; LIMIT-001 is current concrete example |
| Multiplicity machine consistency | Denominator exactly equals locked `hypothesis_test_id` set; separately inspected parameter points/branches/scopes are separately counted unless an explicit pre-registered within-search correction exists |
| Correct Romano-Wolf | Corrected: stepdown can control FWER for a family and exploit joint dependence; not argmax-only; still not adopted for v1 |

## 4. Why the first candidate was not patched in place

The first candidate is preserved because it was independently reviewed at commit
`6ef668fd7214fcef2f12b71cb3e9ea2a36bfcaf7`. Replacing it in place would destroy the clean audit
link between reviewed proposal, review findings and adjudicated revision.

The revision therefore lives in a new document, preserving:
- original candidate;
- independent review target;
- adjudication trail;
- materially changed revision candidate.

## 5. Engine-compatibility facts used

No new code-capability claim was invented. The revision relies on accepted audit/crosswalk facts:

- `position_id` is deterministic across adds/partial closes and changes after a full close;
- realized PnL and additive charged costs are available per transition;
- concrete-contract identity and contract-roll discipline are available;
- `SessionMetadata` is the authoritative trading-day path;
- round-trip ledger/day aggregation helpers are small deltas, not present today;
- execution records require a join to hypothesis/wave identity;
- TD-002 does not corrupt final realized round-trip totals but does corrupt partial-close
  equity/unrealized/drawdown path snapshots;
- LIMIT-001 is fail-closed missing governed price-limit data for affected real confirmatory
  execution, not silent fill corruption.

The revision deliberately avoids depending on the missing multi-day portfolio/equity series.

## 6. Why weekly moving-block bootstrap candidate-0.2 was rejected before review

`candidate-0.2` proposed a complete-week influence series plus non-circular moving-block bootstrap.
Before sending that method to an external independent reviewer, the project brain ran synthetic-only
null fixtures with serial dependence. The smoke test showed materially inflated one-sided false
positive rates in some moderate/high-dependence short-series cases relative to nominal 5%.

Because the frozen Validation/Final cohorts contain only roughly half a year of trading time, the
project brain rejected that drafted method rather than defend a convenient block-length choice with
false precision.

Important boundaries:
- no Human Playbook candidate was run;
- no canonical market price/outcome series was used;
- no threshold was tuned to make a project candidate pass;
- the rejected weekly-MBB draft never became locked/accepted project semantics.

This is ordinary pre-outcome falsification of a statistical design prerequisite.

## 7. Self-normalization source verification

### Shao 2010 original paper

Xiaofeng Shao, **A Self-Normalized Approach to Confidence Interval Construction in Time Series**,
*Journal of the Royal Statistical Society Series B* 72(3), 343–366,
DOI `10.1111/j.1467-9868.2009.00737.x`.

Verified method facts:
- the paper proposes a self-normalized confidence/test construction for stationary dependent time
  series that avoids direct long-run-variance estimation and user-chosen bandwidth/block length;
- the normalization is built from recursive/cumulative estimates;
- for scalar sample-mean inference, the normalizer reduces to

```text
W_n = n^-2 * sum_t [sum_{j<=t}(X_j - X_bar)]^2
```

- the squared statistic has the pivotal Brownian functional `U_1` limit;
- the paper explicitly states the method is asymptotic and relies on weak-dependence/FCLT-style
  assumptions; it is not a finite-sample exact test.

### Shao 2010 corrigendum

Xiaofeng Shao, **Corrigendum: A Self-Normalized Approach to Confidence Interval Construction in
Time Series**, *JRSS-B* 72(5), 695–696, DOI `10.1111/j.1467-9868.2010.00754.x`.

The corrigendum explicitly states the original Assumptions 1 and 2 were insufficient for theorem 1
and strengthens the remainder requirement. This correction is binding on how the project describes
the method.

For the revision's direct scalar **sample mean of the daily score `Z_d(theta0)`**, the statistic is
exactly linear and the linearization remainder is zero, so the corrected remainder condition is
trivially satisfied. The nontrivial assumptions remain the daily-score functional CLT / weak
dependence and positive long-run variance. The project does not claim those are proven by a short
six-month sample.

### Holm 1979

Sture Holm, **A Simple Sequentially Rejective Multiple Test Procedure**, *Scandinavian Journal of
Statistics* 6(2), 65–70.

Used for the simple v1 candidate whole-wave FWER rule. Holm's validity under dependence of
hypotheses does not make individual SN p-values valid if the time-series model fails; these are
separate requirements.

### Romano & Wolf 2005

Joseph P. Romano and Michael Wolf, **Stepwise Multiple Testing as Formalized Data Snooping**,
*Econometrica* 73(4), 1237–1282, DOI `10.1111/j.1468-0262.2005.00615.x`.

Verified correction: the method is a stepwise multiple-testing/FWER approach that can exploit the
joint dependence structure. It is not restricted to argmax/best-of reporting. This evidence
corrects the first candidate but does not adopt Romano-Wolf for v1.

## 8. Candidate-0.3 daily-score ratio formulation

For complete authoritative trading days `d` in a cohort:

```text
C_d = eligible completed round-trip count exiting on d
S_d = sum of per-round-trip normalized net returns exiting on d

theta_hat = sum_d S_d / sum_d C_d
Z_d(theta0) = S_d - theta0*C_d
```

At the null boundary `theta0=0`, `Z_d=S_d`. The sign of the ratio estimand equals the sign of
`E[S_d]` when expected daily trade count is positive, while the general `Z_d(theta0)` form supports
confidence-bound inversion without treating realized `N` as fixed.

This formulation also retains no-exit days as `(S_d,C_d)=(0,0)` and preserves same-day
cross-product clustering.

## 9. Synthetic-only self-normalization smoke test

Purpose: detect obvious finite-sample size failure before independent review. These are not project
market assumptions and not acceptance evidence.

### 9.1 Pivotal smoke calibration

A private test generated 200,000 Brownian paths with a 500-step grid only to obtain an approximate
signed-pivotal 95th percentile for smoke testing:

```text
approx q95(T_infinity) = 5.335
```

This number is **not** the future locked pivotal calibration. The real profile must bind an audited
higher-quality immutable calibration artifact and Monte-Carlo error policy after targeted review.

### 9.2 Simple Gaussian AR(1) null series

For each `(n,rho)`, 5,000 synthetic zero-mean AR(1) series were tested with the approximate q95.
Empirical one-sided rejection fractions:

| n | rho=0.00 | rho=0.30 | rho=0.60 | rho=0.85 |
| ---: | ---: | ---: | ---: | ---: |
| 117 | 0.0454 | 0.0578 | 0.0560 | 0.0838 |
| 126 | 0.0498 | 0.0512 | 0.0504 | 0.0734 |
| 242 | 0.0522 | 0.0526 | 0.0456 | 0.0674 |

Interpretation:
- calibration is materially closer to nominal 5% than the rejected short weekly-MBB smoke path in
  the tested mild/moderate dependence fixtures;
- strong persistence (`rho=0.85`) still causes visible size inflation, especially at six-month
  lengths;
- therefore self-normalization is a **candidate for independent attack, not accepted truth**.

### 9.3 Sparse-event synthetic null series

A separate smoke fixture used Poisson daily event counts with mean 0.2, zero-event days retained,
and a serially correlated latent zero-mean return shock. Runs with fewer than 20 total synthetic
trades were excluded only to mimic the candidate support floor.

Empirical one-sided rejection fractions:

| n | rho=0.00 | rho=0.30 | rho=0.60 | rho=0.85 |
| ---: | ---: | ---: | ---: | ---: |
| 117 | 0.0445 | 0.0485 | 0.0514 | 0.0651 |
| 126 | 0.0486 | 0.0474 | 0.0459 | 0.0609 |
| 242 | 0.0472 | 0.0510 | 0.0530 | 0.0550 |

Again these are synthetic falsification fixtures, not a model of real candidate returns. They show
that the candidate is not obviously broken under several simple sparse short-memory cases, while
strong persistence remains a residual threat the targeted reviewer must attack.

## 10. Detectability-envelope arithmetic

For one-sided `alpha=0.05`, target power 0.80, and optimistic IID normal approximation using the
most stringent first Holm threshold `0.05/M`:

```text
MDE_80 / sigma = [z_(1 - 0.05/M) + z_0.80] / sqrt(N)
```

| N | M=1 | M=5 | M=20 |
| ---: | ---: | ---: | ---: |
| 20 | 0.556 | 0.708 | 0.816 |
| 40 | 0.393 | 0.501 | 0.577 |
| 60 | 0.321 | 0.409 | 0.471 |
| 120 | 0.227 | 0.289 | 0.333 |
| 240 | 0.161 | 0.204 | 0.236 |

This is planning arithmetic only. It ignores serial dependence and robustness gates and uses no
invented project sigma/bp value.

## 11. Remaining high-risk candidate choices requiring independent attack

1. ratio estimand via complete daily `(S_d,C_d)` process;
2. stationarity/FCLT plausibility and failure boundary for the daily score;
3. signed self-normalized pivot and confidence-bound inversion;
4. immutable Brownian-pivotal calibration artifact and Monte-Carlo error policy;
5. `N>=20` and six active exit weeks support floors;
6. zero right-censoring;
7. PASS/FAIL/INSUFFICIENT sign logic;
8. LOTO/LOWO sign robustness;
9. removing the extra 2bp and universal 2x hard gates;
10. separate-count treatment of outcome-inspected parameter points absent a within-search
   correction;
11. Holm rather than Romano-Wolf for the first locked profile;
12. finite-sample behavior under strong persistence, heavy tails, volatility clustering,
   nonstationarity and sparse bursts.

These are exactly why `candidate-0.3` remains NOT_LOCKED.

## 12. Tool decision

```text
TOOL_DECISION=USE_EXISTING
```

No new statistics framework, paid API, orchestration layer or project runtime dependency is needed.
A bounded independent reviewer is the correct next capability because the remaining uncertainty is
statistical-design validity, not missing infrastructure.

## 13. Revision evidence verdict

```text
REVISION_EVIDENCE=COMPLETE
REVISION_VERSION=v1.0-revision-candidate-0.3
WEEKLY_MBB_DRAFT=REJECTED_PRE_OUTCOME
CURRENT_INFERENCE_CANDIDATE=DAILY_SCORE_SELF_NORMALIZATION
SYNTHETIC_FALSIFICATION_SMOKE_TEST=COMPLETE
NO_CANDIDATE_OUTCOME_DATA_USED=YES
NO_FROZEN_SEMANTIC_CHANGE=YES
PROFILE_LOCKED=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
NEXT_REQUIRED_STAGE=TARGETED_INDEPENDENT_DELTA_REVIEW
```

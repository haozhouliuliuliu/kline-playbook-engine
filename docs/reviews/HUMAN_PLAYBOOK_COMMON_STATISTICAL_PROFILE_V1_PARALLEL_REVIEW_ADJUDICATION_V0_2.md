# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_PARALLEL_REVIEW_ADJUDICATION_V0_2

> Date: 2026-08-19
> Role: project-brain adjudication after two independent reviewer lanes
> Scope: Common Statistical Profile v1 revision candidate 0.3 only
> Frozen authority unchanged: Research Protocol v1.0 / frozen 12-6-6 / Human Playbook First

```text
ADJUDICATION_STATUS=COMPLETE
PROFILE_0_3_LOCKABLE=NO
FROZEN_PROTOCOL_CONFLICT=NO
OWNER_GATE_REQUIRED_NOW=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
NEXT_PACKAGE=COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_AFTER_TWO_REVIEWS
TOOL_DECISION=USE_EXISTING
```

## 1. Independent evidence adjudicated

### Lane A — targeted delta review

```text
BRANCH=parallel/stat-profile-delta-review-r03
COMMIT=cbfc1ae6e6b833292181252d3d4fe14014a22fae
ARTIFACT=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_TARGETED_DELTA_REVIEW.md
VERDICT=GO_WITH_REQUIRED_CHANGES
CRITICAL=1
HIGH=2
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

### Lane B — second self-normalization falsification review

```text
BRANCH=parallel/stat-profile-sn-falsification-r03
COMMIT=a4008dfaf6996d13f269077f8e4c537857d18ab9
ARTIFACT=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_SELF_NORMALIZATION_SECOND_REVIEW.md
VERDICT=GO_WITH_REQUIRED_CHANGES
CRITICAL=1
HIGH=1
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

Both reviews are advisory evidence. This adjudication decides which findings become project revision requirements.

## 2. Direct adjudication of the reviewer conflict: count-return correlation

Lane B's CRITICAL finding is **REJECTED**.

Candidate 0.3 defines:

```text
C_d = number of eligible completed round trips exiting on day d
S_d = sum of their per-round-trip normalized returns r_i
theta_hat = sum_d S_d / sum_d C_d = sum_i r_i / N
```

The population target corresponding to a uniformly sampled trade/event is:

```text
theta = E[S_d] / E[C_d]
```

This is the event-weighted per-trade mean. It does **not** require daily event count to be independent of daily return level.

Lane B's synthetic process was:

```text
L ~ N(0,1)
C | L ~ Poisson(lambda * exp(aL))
E[r | L] = bL
```

The review asserted `E[r_i]=0` because `E[L]=0`. That is the wrong sampling measure for a randomly selected trade: high-count days contribute more trades. Under the event-weighted per-trade distribution,

```text
E_trade[r]
= E[C * bL] / E[C]
= b * E[L exp(aL)] / E[exp(aL)]
= a * b
```

Therefore the review's own cases have true per-trade targets:

```text
a=0.7, b=0.5 -> theta=0.35
a=0.3, b=0.2 -> theta=0.06
a=0.1, b=0.05 -> theta=0.005
```

The reported positive daily score means and high rejection rates are therefore expected under a positive true per-trade edge; they are not false-positive evidence. No count-return-independence assumption is added to the profile.

Accepted editorial clarification: candidate 0.4 must state the population estimand precisely as `theta=E[S_d]/E[C_d]`, equivalent to the event-weighted mean of one completed round trip, and must pin `C_d` as a count and `S_d` as the sum of already normalized per-trade returns. A PnL/notional variant would be a different estimand and is prohibited unless separately versioned.

## 3. Accepted blocker: finite-sample anti-conservatism of self-normalized p-values

Lane A's CRITICAL is **ACCEPTED**. Lane B's persistence HIGH independently supports the same risk.

Synthetic-only evidence shows that at the frozen six-month cohort lengths the current Shao-style self-normalized signed-pivot test can be materially anti-conservative under strong serial persistence. Lane A additionally found anti-conservative behavior under left-skewed daily-score distributions, including larger inflation in Holm-relevant tails.

Consequences:

1. Candidate 0.3 cannot honestly claim that the resulting finite-sample per-hypothesis p-values support the project's `strong FWER <= 0.05` acceptance target across the intended evidence domain.
2. Holm cannot repair invalid or materially anti-conservative input p-values.
3. This is a profile-level inference defect, not a frozen Protocol v1.0 conflict.
4. `INSUFFICIENT_EVIDENCE` remains the safe fail-closed state when the locked inference validity conditions are not met.

### Remedy adjudication

Lane A proposed either a pre-registered shape/dependence gate or weakening the error-rate claim.

- **Weakening the project error-rate target is REJECTED.** The project keeps the strong-FWER target for accepted candidate claims.
- **A deterministic fail-closed inference-validity envelope is a valid direction, but no numeric skew/autocorrelation threshold from reviewer examples is adopted.** Reviewer example bands are not authority and cannot be tuned on candidate outcomes.
- A replacement or guarded inference procedure must be selected pre-outcome and then independently attacked before lock.

This unresolved inference choice is the sole current statistical blocker.

## 4. Other findings

### ACCEPTED REQUIRED

1. **Confidence-bound inversion must fail closed.** `V_D(theta0)` depends on `theta0`; if a pre-registered inversion algorithm finds no unique valid root in its locked search domain, the bound is unavailable and the result routes to `INSUFFICIENT_EVIDENCE`, never a fabricated bound.
2. **Multiplicity mapping must be machine-consistent.** `parameter_search_identity` is a search identity, not a multiplicity counting unit. Every separately outcome-inspected parameter point/branch/scope capable of its own conclusion requires a separately counted `hypothesis_test_id` unless a distinct within-search correction is pre-registered before any outcome exposure.
3. **PASS/FAIL level asymmetry must be explicit.** PASS is protected by whole-wave Holm; the negative FAIL path may use an unadjusted one-sided upper bound because the project-wide false-acceptance control target is on PASS. The profile must state this deliberately; unresolved sign remains `INSUFFICIENT_EVIDENCE`.
4. **C_d/S_d identity must be pinned.** `C_d=count of completed exits`; `S_d=sum of normalized per-round-trip returns`. No silent PnL/notional substitution.
5. **LOTO/LOWO remain non-statistical conservative robustness guards.** They may demote a statistical PASS candidate to `INSUFFICIENT_EVIDENCE`; they are not p-value procedures and must not be described as such.
6. **Base execution assumptions cannot be merely arbitrary pre-registration.** The eventual locked profile must bind the evidence/status of the base fee/slippage/execution assumptions and fail closed where a required execution fact is unavailable. No reviewer-proposed universal bp or multiplier threshold is adopted.

### ACCEPTED AS DISCLOSURE / REPORTING, NOT NEW HARD GATES

1. Zero right-censoring is retained as the current safe v1 candidate rule because v1 has no justified censoring model. The profile must explicitly disclose that any in-cohort position still open at cohort end prevents statistical PASS/FAIL for that cohort and yields `INSUFFICIENT_EVIDENCE`. This is a coverage limitation, not evidence against the playbook and not an intraday-only research-direction rule.
2. Structural variance/nonstationarity diagnostics may be mandatory reports, but no numeric variance-ratio gate is adopted from reviewer examples.
3. Exact Monte-Carlo/grid calibration tolerances remain open until the inference procedure is resolved. Reviewer values such as grid>=1000, B>=200000, or p-SE<=1e-3 are evidence proposals, not accepted constants.

### REJECTED / NOT ADOPTED

- Count-return-independence as a requirement for the declared event-weighted per-trade estimand.
- Weakening the strong-FWER acceptance target.
- Any reviewer-suggested numerical skewness, autocorrelation, variance-ratio, sample-size, calibration-grid or Monte-Carlo thresholds without separate pre-outcome justification.
- Romano-Wolf adoption for v1; Holm remains the simplest candidate method if valid per-hypothesis p-values can be supplied.

## 5. Protected correct findings

The two reviews independently support retaining these parts of candidate 0.3 unless later evidence overturns them:

- one `position_id` = one completed round-trip observation;
- adds/partial closes aggregate inside that observation;
- forced liquidation is terminal and separately triggers risk/failure handling;
- concrete-contract roll creates separate round trips;
- zero-exit authoritative trading days remain in the inference time process;
- self-normalizer algebra and signed Brownian pivotal relationship are mathematically correct under their asymptotic conditions;
- Shao corrigendum's nonlinear remainder issue is trivial for the direct linear sample-mean score, while weak-dependence/FCLT and finite-sample adequacy remain genuine assumptions;
- `INSUFFICIENT_EVIDENCE` is not FAIL;
- DATA_BLOCKED remains distinct from both;
- no universal 2bp edge floor and no universal 2x friction gate are reinstated;
- Holm remains the leading simple multiplicity candidate, conditional on valid per-hypothesis p-values.

## 6. Project decision

```text
CANDIDATE_0_3_DIRECTION=KEEP_BUT_REVISE
CANDIDATE_0_3_LOCKABLE=NO
PRIMARY_BLOCKER=PER_HYPOTHESIS_INFERENCE_FINITE_SAMPLE_VALIDITY
COUNT_RETURN_CRITICAL=REJECTED_AS_FIXTURE_TARGET_ERROR
STRONG_PERSISTENCE_RISK=ACCEPTED
LEFT_SKEW_SIZE_RISK=ACCEPTED
OWNER_GATE_REQUIRED_NOW=NO
FROZEN_PROTOCOL_CONFLICT=NO
```

The next bounded package is not evaluator implementation. It is a narrow, pre-outcome inference-resolution exercise: determine the smallest deterministic procedure or fail-closed validity envelope that preserves the common per-trade estimand and the strong-FWER acceptance target at the frozen cohort lengths without arbitrary outcome-tuned thresholds. After that resolution, project brain will produce candidate 0.4 and request only a targeted final attack on the materially changed inference definitions.

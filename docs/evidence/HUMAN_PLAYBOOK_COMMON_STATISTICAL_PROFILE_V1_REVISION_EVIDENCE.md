# HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_EVIDENCE

> Date: 2026-08-19
> Work package: `COMMON_STATISTICAL_PROFILE_V1_REVISION_AFTER_PARALLEL_REVIEW`
> Evidence for: `docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE.md`
> Status: `REVISION_EVIDENCE_COMPLETE / NO_CANDIDATE_OUTCOME`

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

The only quantitative work performed was:
- algebra on the candidate estimator/inference definitions;
- standardized no-outcome normal-approximation power arithmetic;
- reading project code/evidence interfaces already accepted by the engine audit/crosswalk;
- primary statistical literature/source verification.

No candidate-return variance, actual candidate trade frequency, candidate holding distribution or
candidate PnL was used to choose the revised rules.

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

The independent review remains advisory. The project-brain adjudication is the authority for which
review findings became revision requirements.

## 3. Adjudication requirement -> revision mapping

| Adjudicated requirement | Revision response |
| --- | --- |
| Separate economic materiality from detectability | Base materiality = positive net edge after pre-registered base friction; separate standardized no-outcome MDE/power envelope; `INSUFFICIENT_EVIDENCE` explicitly means unresolved claim, not no edge |
| Remove `2H-1` ESS hard gate | Removed completely; holding duration retained as structural diagnostic; dependence block length uses actual p90 calendar-week span |
| Pin round-trip semantics | One engine `position_id` = one observation; adds/partial closes aggregated; forced liquidation terminal; roll creates separate round trips |
| Pin holding/multi-week treatment | Inclusive authoritative trading-day horizon + week-span definitions; full return exits into terminal-close week; p90 week span drives block length; max span reported |
| Justify/simplify sufficiency thresholds | Eight interacting first-candidate thresholds reduced to three small support floors plus zero censoring/nondegeneracy; numbers explicitly labeled governance choices, not statistical laws |
| Distinguish fee vs slippage stress | Additive fee and fill-price slippage separated; universal `2x friction` hard gate removed; analytic fee break-even diagnostic; slippage stress requires separate execution rerun identity |
| Guard one event/window carrying edge | Replaced arbitrary PnL fractions with leave-one-trade-out and leave-one-active-week-out positive-sign robustness conditions |
| Add `DATA_BLOCKED` | Added first-class state before integrity/statistical decisions; LIMIT-001 is the current concrete example |
| Multiplicity machine consistency | Denominator exactly equals locked `hypothesis_test_id` set; outcome-inspected parameter points/branches/scopes that can receive separate conclusions are separately counted unless a separately frozen within-search correction exists |
| Correct Romano-Wolf | Corrected: resampling stepdown can control FWER for a family and exploit dependence; not argmax-only; still deferred from simple v1 |

## 4. Why the first candidate was not patched in place

The first candidate is preserved as historical design evidence because it was independently reviewed
at commit `6ef668fd7214fcef2f12b71cb3e9ea2a36bfcaf7`. Replacing it in place would make it harder to audit
what the reviewer actually reviewed.

The revision therefore lives in a new document. This preserves:
- the original proposal;
- the independent review target;
- the adjudication trail;
- the materially changed revision candidate.

## 5. Engine-compatibility facts used

No new code-capability claim was invented. The revision relies on accepted crosswalk/audit facts:

- `position_id` is deterministic across adds/partial closes and changes after a full close;
- realized PnL and additive charged costs are available per transition;
- concrete-contract identity and contract-roll discipline are available;
- `SessionMetadata` is the authoritative trading-day path;
- round-trip ledger/day-week helpers are small deltas, not present today;
- execution records require a join to hypothesis/wave identity;
- TD-002 does not corrupt final realized round-trip totals but does corrupt partial-close
  equity/unrealized/drawdown path snapshots;
- LIMIT-001 is fail-closed missing governed price-limit data for affected real confirmatory
  execution, not silent fill corruption.

The revision deliberately does not depend on the missing multi-day portfolio/equity series.

## 6. Statistical method verification

Primary/statistical sources rechecked for the exact method claims:

### Künsch 1989

Hans R. Künsch, **The Jackknife and the Bootstrap for General Stationary Observations**, *The Annals
of Statistics* 17(3), 1217–1241, DOI `10.1214/aos/1176347265`.

Used only for the general proposition that contiguous-block resampling is a standard way to handle
weakly dependent stationary observations. It does not validate the project's weekly influence
representation, `span_weeks_p90` block length, or small support floors.

### Politis & Romano 1992

D. N. Politis and J. P. Romano, **A Circular Block-Resampling Procedure for Stationary Data**.
Stanford Statistics technical-report record `EFS NSF 370` (report dated 1991; publication cited in
the first candidate as 1992).

Used to confirm the block-resampling family and to distinguish circular from non-circular designs.
The revision intentionally removes circular first/last-cohort wrapping because it would create an
artificial adjacency across the frozen cohort boundary.

### Holm 1979

Sture Holm, **A Simple Sequentially Rejective Multiple Test Procedure**, *Scandinavian Journal of
Statistics* 6(2), 65–70.

Used for the simple sequentially rejective FWER procedure. The key relevant property is strong
protection against type-I familywise error without needing an independence assumption among the
individual hypotheses. This supports Holm as the simple v1 candidate but says nothing about whether
this project has adequate power.

### Romano & Wolf 2005

Joseph P. Romano and Michael Wolf, **Stepwise Multiple Testing as Formalized Data Snooping**,
*Econometrica* 73(4), 1237–1282, DOI `10.1111/j.1468-0262.2005.00615.x`.

The paper proposes a stepwise multiple-testing method that asymptotically controls FWER and can use
the joint dependence structure of test statistics. It explicitly presents the method in a
multiple-strategy setting but notes broader multiple-testing applicability. This directly falsifies
the first candidate's over-narrow claim that Romano-Wolf is only relevant to argmax/best-of
reporting.

The revision does **not** adopt Romano-Wolf; it corrects the description and keeps it as a possible
future refinement if Holm's conservatism becomes a pre-outcome capacity problem worth the added
joint-resampling complexity.

### Lahiri 2003

S. N. Lahiri, **Resampling Methods for Dependent Data**, Springer Series in Statistics.

Used as a general dependent-resampling reference. It does not provide a magic finite-sample
threshold for this 24-month project and is not used to justify `N=20`, six active weeks, or `4L`.

## 7. Detectability-envelope arithmetic

The revision publishes an outcome-free standardized planning envelope rather than assuming a
project return volatility.

For one-sided `alpha=0.05`, target power 0.80, and conservative first Holm threshold `0.05/M`:

```text
MDE_80 / sigma = [z_(1 - 0.05/M) + z_0.80] / sqrt(N)
```

Computed values:

| N | M=1 | M=5 | M=20 |
| ---: | ---: | ---: | ---: |
| 20 | 0.556 | 0.708 | 0.816 |
| 40 | 0.393 | 0.501 | 0.577 |
| 60 | 0.321 | 0.409 | 0.471 |
| 120 | 0.227 | 0.289 | 0.333 |
| 240 | 0.161 | 0.204 | 0.236 |

This calculation is deliberately labeled optimistic IID planning arithmetic. It ignores the real
block dependence, time concentration and other acceptance guards. It is not an accepted outcome
model and no illustrative bp/sigma value is promoted to project fact.

## 8. Remaining candidate choices requiring independent attack

The project brain considers the following the highest-risk remaining design choices:

1. weekly influence representation `x_w=(W/N)*sum(exit-week r_i)`;
2. null-centered basic moving-block bootstrap rather than a studentized/bootstrap-t alternative;
3. p90 calendar-week span as block length;
4. `N>=20`, six active exit weeks and `W>=4L` support floors;
5. zero right-censoring;
6. three-way PASS/FAIL/INSUFFICIENT sign logic;
7. LOTO/LOWO sign robustness;
8. removing the extra 2 bp and universal 2x hard gates;
9. separate-count v1 treatment of every outcome-inspected parameter point unless an explicit
   within-search correction exists;
10. Holm rather than Romano-Wolf for the first locked profile.

These items are exactly why the revision remains `NOT_LOCKED` and requires a targeted independent
delta review. The review should not reopen already frozen Protocol v1.0/12/6/6 semantics.

## 9. Tool decision

```text
TOOL_DECISION=USE_EXISTING
```

No new statistics framework, paid API, orchestration layer or project runtime dependency is needed
to create or review this candidate. Existing GitHub/repository evidence plus a bounded independent
reviewer are sufficient.

## 10. Revision evidence verdict

```text
REVISION_EVIDENCE=COMPLETE
NO_CANDIDATE_OUTCOME_DATA_USED=YES
NO_FROZEN_SEMANTIC_CHANGE=YES
REVISED_CANDIDATE_CREATED=YES
PROFILE_LOCKED=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
NEXT_REQUIRED_STAGE=TARGETED_INDEPENDENT_DELTA_REVIEW
```

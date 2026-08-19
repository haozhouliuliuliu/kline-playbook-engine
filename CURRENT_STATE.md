# CURRENT_STATE

## Project phase

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE_BASELINE=Skeleton_v1.0
ARCHITECTURE_STATUS=ACCEPTED
ADOPTED_CONTRACT_VERSION=3.1
CURRENT_BLOCKER=PER_HYPOTHESIS_INFERENCE_FINITE_SAMPLE_VALIDITY
CURRENT_WORK_PACKAGE=COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_AFTER_TWO_REVIEWS
CURRENT_WORK_PACKAGE_STATUS=PARALLEL_REVIEWS_ADJUDICATED_INFERENCE_RESOLUTION_REQUIRED
CURRENT_WORK_PACKAGE_AUTHORITY=docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md
CURRENT_WORK_PACKAGE_ADJUDICATION=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_PARALLEL_REVIEW_ADJUDICATION_V0_2.md
CONVERSATION_HANDOFF_STATUS=TAKEOVER_ACCEPTED
OWNER_ACTION=NONE
```

## Binding direction / anti-regression

```text
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
RESEARCH_DIRECTION_STATUS=OWNER_APPROVED
RESEARCH_ROUTE_ANTI_REGRESSION=HUMAN_PLAYBOOK_FIRST_NO_DATA_FIRST_KLINE_MINING
PROHIBITED_DEFAULT_RESEARCH_ROUTE=UNCONSTRAINED_KLINE_INDICATOR_PATTERN_PARAMETER_MINING
```

Binding route remains:

```text
traceable human trading experience
-> source-faithful AI extraction and structuring
-> versioned Playbook Contract
-> deterministic/versioned machine operationalization
-> governed historical validation of applicability and failure conditions
-> strict validation / protected-holdout governance
-> accepted or rejected playbook
```

No strategy/result/parameter/failure-history facts may be imported from another project.

## Frozen Research Protocol v1.0

```text
RESEARCH_PROTOCOL_VERSION=1.0
RESEARCH_PROTOCOL_STATUS=FROZEN_BINDING
CHRONOLOGICAL_SPLIT_STATUS=FROZEN_12_6_6
DEVELOPMENT=2024-01-01..2024-12-31
VALIDATION=2025-01-01..2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT=2025-07-01..2025-12-31
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
PERFORMANCE_RESEARCH_STARTED=NO
REAL_CLAIM_EXTRACTION_STARTED=NO
REAL_CLAIM_EXTRACTION_ENVIRONMENT=VERIFIED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
```

`INSUFFICIENT_EVIDENCE` remains a frozen legitimate result. Material changes to frozen research semantics or chronology require a new protocol version, material independent review and Owner gate.

## Pre-outcome firewall

```text
PREOUTCOME_FIREWALL_IMPLEMENTATION=COMPLETE_VERIFIED_ACCEPTED
SOURCE_ONLY_CLAIM_EXTRACTION_RUNNER=VERIFIED
RESEARCH_WAVE_IDENTITY_BINDING=VERIFIED
STATISTICAL_PROFILE_INTERFACE=VERIFIED
PRE_OUTCOME_GATE_STATUS=VERIFIED_FAIL_CLOSED
HISTORICAL_FINAL_HOLDOUT_LOCK=ENFORCED
FIREWALL_TESTS=54
FULL_TESTS_BASELINE=235_OK_3_SKIPPED
```

`src/research_firewall.py` remains the single owner of new pre-outcome access rules.

## Common Statistical Profile v1

Historical first candidate remains superseded and not locked.

Revision candidate 0.3:

```text
REVISION_CANDIDATE_VERSION=v1.0-revision-candidate-0.3
REVISION_CANDIDATE_DOC=docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE.md
REVISION_CANDIDATE_STATUS=KEEP_BUT_REVISE_NOT_LOCKABLE
NO_CANDIDATE_OUTCOME_DATA_USED=YES
CURRENT_INFERENCE_CANDIDATE=DAILY_SCORE_SELF_NORMALIZATION
```

Two independent review lanes completed from main baseline `6823d8f73d69def126e22482960e00b85543f570`:

```text
TARGETED_DELTA_REVIEW_BRANCH=parallel/stat-profile-delta-review-r03
TARGETED_DELTA_REVIEW_COMMIT=cbfc1ae6e6b833292181252d3d4fe14014a22fae
TARGETED_DELTA_REVIEW_VERDICT=GO_WITH_REQUIRED_CHANGES
SECOND_SN_REVIEW_BRANCH=parallel/stat-profile-sn-falsification-r03
SECOND_SN_REVIEW_COMMIT=a4008dfaf6996d13f269077f8e4c537857d18ab9
SECOND_SN_REVIEW_VERDICT=GO_WITH_REQUIRED_CHANGES
```

Project-brain adjudication:

```text
PARALLEL_REVIEW_ADJUDICATION=COMPLETE
PARALLEL_REVIEW_ADJUDICATION_DOC=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_PARALLEL_REVIEW_ADJUDICATION_V0_2.md
PROFILE_0_3_LOCKABLE=NO
FROZEN_PROTOCOL_CONFLICT=NO
COUNT_RETURN_CRITICAL=REJECTED_AS_FIXTURE_TARGET_ERROR
STRONG_PERSISTENCE_RISK=ACCEPTED
LEFT_SKEW_SIZE_RISK=ACCEPTED
PRIMARY_BLOCKER=PER_HYPOTHESIS_INFERENCE_FINITE_SAMPLE_VALIDITY
```

The rejected count-return finding used the wrong sampling measure: under the reviewer's own process `C|L ~ Poisson(lambda*exp(aL))`, `E[r|L]=bL`, a uniformly sampled trade has mean `E[C*bL]/E[C]=a*b`, not zero. Count-return independence is therefore not added as a project requirement. Candidate 0.4 must state the estimand precisely as the event-weighted per-trade mean `theta=E[S_d]/E[C_d]` and pin `C_d` as count / `S_d` as sum of already normalized per-trade returns.

The actual blocker is finite-sample p-value anti-conservatism at six-month cohort lengths under strong persistence and left-skewed daily-score processes. Holm cannot repair invalid input p-values. The project does not weaken its strong-FWER acceptance target and does not adopt reviewer-proposed numeric shape/autocorrelation thresholds without separate pre-outcome justification.

Other accepted revision requirements:
- confidence-bound inversion must be deterministic and fail closed on missing/non-unique roots;
- parameter-search identity is not a multiplicity count unit; every separately outcome-inspected point/branch/scope capable of its own conclusion needs its own counted `hypothesis_test_id` unless a pre-registered within-search correction exists;
- PASS/Holm vs negative FAIL-bound asymmetry must be explicit;
- LOTO/LOWO remain non-statistical conservative robustness guards;
- zero right-censoring remains the current safe v1 candidate rule and must be disclosed as a coverage limitation yielding `INSUFFICIENT_EVIDENCE`, not evidence against a playbook;
- base execution assumptions and unavailable execution facts must be evidence-bound/fail-closed; no universal 2bp or 2x threshold is reinstated;
- exact pivotal calibration constants remain open until the inference procedure is resolved.

## Canonical historical corpus

```text
CANONICAL_DATASET_ACCEPTED=YES
CANONICAL_PRODUCTS=cu,al,ni,au,ag,rb
CANONICAL_COVERAGE=2024-01-01..2025-12-31
CANONICAL_GRANULARITY=1-minute
CONCRETE_CONTRACTS=212
NORMALIZED_ROWS=15280452
CANONICAL_CORPUS_IDENTITY=1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8
CROSS_SOURCE_RESULT=32841_MATCH/0_MISMATCH/0_NOT_COMPARABLE/139_NOT_AVAILABLE
```

Corpus construction created no project-recorded strategy-family DEVELOPMENT/VALIDATION/historical-final exposure.

## Authorization boundaries

AUTHORIZED NOW:
- source discovery/provenance;
- controlled source-faithful claim extraction in verified SOURCE_ONLY;
- deterministic non-outcome operationalization/tests;
- Common Statistical Profile design/review work without candidate outcomes;
- synthetic/non-candidate statistical and engine sanity tests;
- isolated independent review.

NOT AUTHORIZED:
- data-first K-line/chart-pattern/indicator/rule/parameter mining as project route;
- candidate PnL/equity/expectancy/Sharpe/win-loss or equivalent candidate-quality inspection;
- Validation access;
- historical final-holdout access;
- frozen 12/6/6 or protocol semantic changes without new protocol/Owner gate;
- Shadow automated trading, real-money/broker actions, live discretionary LLM critical path;
- new paid commitments or permanent risk-rule changes without Owner approval.

## Tools / lanes

```text
TOOL_DECISION=USE_EXISTING
PAID_CHAT_RELAY_ORCHESTRATOR=NOT_ADOPTED_CURRENTLY
BRITTLE_VSCODE_UI_CHAT_AUTOMATION=NOT_ADOPTED_CURRENTLY
CURRENT_DS_RELAY_MODE=OWNER_MANUAL_RELAY_WHEN_LOCAL_AGENT_IS_NEEDED
```

No new framework/API is justified. A third independent lane is now justified narrowly as an inference-resolution/tie-break lane because the first two reviews disagreed on one mathematical finding and jointly exposed a real finite-sample validity blocker. Main remains the sole integration lane.

## Known limitations / tech debt

- `TD-001`: trusted day/week statistics must use `SessionMetadata`.
- `TD-002`: partial-close equity/unrealized/drawdown path snapshots unsafe; final realized round-trip totals not corrupted.
- `LIMIT-001`: missing governed historical price-limit facts fail closed for affected confirmatory execution.
- `DECISION-001`: live AI scene-recognition mode remains Owner-gated/unresolved.

Round-trip ledger, holding/day aggregation and hypothesis/wave joins remain small engineering deltas. Full evaluator implementation still waits until the statistical profile survives inference resolution and targeted final review.

## Verification status

Latest code-bearing baseline remains:

```text
python -m unittest discover -s tests -v
235 tests OK
3 skipped
exit 0
```

The second independent review separately reported the same 235 OK / 3 skipped baseline in its isolated worktree. No production/test code has changed in this statistical adjudication package.

## Current next action

```text
CURRENT_NEXT_ACTION=RESOLVE_COMMON_STATISTICAL_PROFILE_V1_PER_HYPOTHESIS_INFERENCE
CURRENT_NEXT_ACTION_AUTHORITY=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_PARALLEL_REVIEW_ADJUDICATION_V0_2.md
PROFILE_STATUS=REVISION_REQUIRED_NOT_LOCKED
TOOL_DECISION=USE_EXISTING
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
OWNER_ACTION=NONE
```

The next bounded package must decide the smallest pre-outcome inference procedure or deterministic fail-closed validity envelope that preserves the event-weighted per-trade estimand and strong-FWER acceptance target at the frozen cohort lengths. It must not tune against candidate outcomes. After that, project brain will write candidate 0.4 and request only a final targeted attack on materially changed inference definitions.

## Progress estimates — engineering estimates, not evidence facts

| Stage / domain | Status | Estimate |
| --- | --- | ---: |
| Architecture / Bootstrap | Skeleton v1.0 accepted | 100% |
| Data Substrate | canonical corpus accepted | ~90% |
| Strategy Catalog | identity/playbook foundations; real extracted playbooks not yet built | ~58% |
| Backtest & Validation | engine/firewall substantial; profile inference blocker identified | ~66% |
| Human Playbook Research Loop | protocol/source/firewall ready; real claim extraction not started | ~44% |
| Trading Loop | early deterministic foundations | ~15% |
| Ledger / Observability | foundational pieces only | ~25% |
| Overall project | research-foundation stage | ~46% |

Owner approval remains required only for the established major gates. No new Owner decision is required for the current inference-resolution package.
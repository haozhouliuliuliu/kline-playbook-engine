# CURRENT_STATE

## Project phase

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE_BASELINE=Skeleton_v1.0
ARCHITECTURE_STATUS=ACCEPTED
ADOPTED_CONTRACT_VERSION=3.1
CURRENT_BLOCKER=OWNER_RESEARCH_DESIGN_DECISION_AFTER_NO_DEFENSIBLE_LOCKABLE_V1_PASS_INFERENCE
CURRENT_WORK_PACKAGE=COMMON_STATISTICAL_PROFILE_V1_ACCEPTANCE_PATH_OWNER_GATE
CURRENT_WORK_PACKAGE_STATUS=INFERENCE_RESOLUTION_COMPLETE_OWNER_DECISION_REQUIRED
CURRENT_WORK_PACKAGE_AUTHORITY=docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md
CURRENT_WORK_PACKAGE_ADJUDICATION=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_ADJUDICATION_V0_3.md
CONVERSATION_HANDOFF_STATUS=TAKEOVER_ACCEPTED
OWNER_ACTION=REQUIRED
OWNER_DECISION_REQUIRED=OPTION_A_OR_OPTION_B
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

## Common Statistical Profile v1 — current state

Historical first candidate remains superseded and not locked.

Revision candidate 0.3:

```text
REVISION_CANDIDATE_VERSION=v1.0-revision-candidate-0.3
REVISION_CANDIDATE_DOC=docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE.md
REVISION_CANDIDATE_STATUS=NOT_LOCKABLE
PROFILE_0_4_DRAFTABLE=NO
NO_CANDIDATE_OUTCOME_DATA_USED=YES
CURRENT_INFERENCE_CANDIDATE=DAILY_SCORE_SELF_NORMALIZATION_REJECTED_AS_PASS_BASIS
```

### Parallel review history

Two independent review lanes completed from main baseline `6823d8f73d69def126e22482960e00b85543f570`:

```text
TARGETED_DELTA_REVIEW_BRANCH=parallel/stat-profile-delta-review-r03
TARGETED_DELTA_REVIEW_COMMIT=cbfc1ae6e6b833292181252d3d4fe14014a22fae
TARGETED_DELTA_REVIEW_VERDICT=GO_WITH_REQUIRED_CHANGES
SECOND_SN_REVIEW_BRANCH=parallel/stat-profile-sn-falsification-r03
SECOND_SN_REVIEW_COMMIT=a4008dfaf6996d13f269077f8e4c537857d18ab9
SECOND_SN_REVIEW_VERDICT=GO_WITH_REQUIRED_CHANGES
```

Project-brain adjudication v0.2 remains binding:

```text
COUNT_RETURN_CRITICAL=REJECTED_AS_FIXTURE_TARGET_ERROR
STRONG_PERSISTENCE_RISK=ACCEPTED
LEFT_SKEW_SIZE_RISK=ACCEPTED
PRIMARY_BLOCKER=PER_HYPOTHESIS_INFERENCE_FINITE_SAMPLE_VALIDITY
```

The rejected count-return finding used the wrong sampling measure: under the reviewer's own process `C|L ~ Poisson(lambda*exp(aL))`, `E[r|L]=bL`, a uniformly sampled realized trade has mean `E[C*bL]/E[C]=a*b`, not zero. Count-return independence is not a project requirement. The estimand is the event-weighted per-trade mean `theta=E[S_d]/E[C_d]`, with `C_d` equal to completed-round-trip count and `S_d` equal to the sum of already normalized per-trade returns.

### Third-lane inference resolution

```text
INFERENCE_RESOLUTION_BRANCH=parallel/stat-profile-inference-resolution-r04
INFERENCE_RESOLUTION_COMMIT=dd84dba7d37a2dd00ab8480c7f79ccfd37b7b118
INFERENCE_RESOLUTION_RECOMMENDATION=NO_LOCKABLE_V1_INFERENCE
INFERENCE_RESOLUTION_PROFILE_0_4_DRAFTABLE=NO
INFERENCE_RESOLUTION_NO_CANDIDATE_OUTCOME_DATA_USED=YES
INFERENCE_RESOLUTION_FROZEN_PROTOCOL_CONFLICT=NO
PROJECT_BRAIN_ADJUDICATION_DOC=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_ADJUDICATION_V0_3.md
GENERAL_DOMAIN_POSITIVE_PASS_INFERENCE=NO_DEFENSIBLE_LOCKABLE_METHOD_IDENTIFIED
```

Project-brain wording is intentionally narrower than an impossibility theorem: the evidence establishes that no defensible lockable method was identified among the investigated inference families under the current frozen constraints; it does not prove that no conceivable method can ever exist.

Accepted inference-resolution facts:
- Shao-style self-normalization is not lockable as a PASS basis at approximately 117/126 trading days because finite-sample type-I error is materially anti-conservative under strong persistence and left-skewed score processes, including Holm-relevant tails;
- Holm cannot repair invalid per-hypothesis p-values;
- tested wild-bootstrap self-normalization does not solve the same problem;
- examined block-bootstrap, weekly/grouped and subsampling alternatives are not adopted because they fail current size/resolution/short-sample/no-arbitrary-knob requirements;
- no independently justified operational cutoff was identified for a guarded/admissible-domain self-normalization design;
- extending the window alone is not demonstrated sufficient;
- the project's strong-FWER acceptance target is not weakened.

Methods/status not adopted:

```text
ASYMPTOTIC_SELF_NORMALIZATION=REJECTED_AS_PASS_BASIS
WILD_BOOTSTRAP_SELF_NORMALIZATION=REJECTED_AS_PASS_BASIS
MOVING_BLOCK_BOOTSTRAP=NOT_ADOPTED
WEEKLY_GROUPED_INFERENCE=NOT_ADOPTED
SUBSAMPLING=NOT_ADOPTED_FOR_HOLM_PASS
ARBITRARY_SHAPE_OR_AUTOCORRELATION_GATE=NOT_ADOPTED
WEAKENED_NOMINAL_ERROR_RATE=NOT_ADOPTED
```

These are current-package decisions, not permanent universal bans.

Other adjudicated profile facts remain unchanged:
- confidence-bound inversion must be deterministic and fail closed on missing/non-unique roots;
- parameter-search identity is not a multiplicity count unit; every separately outcome-inspected point/branch/scope capable of its own conclusion needs its own counted `hypothesis_test_id` unless a pre-registered within-search correction exists;
- PASS/Holm vs negative FAIL-bound asymmetry must be explicit if any future valid inference uses it;
- LOTO/LOWO remain non-statistical conservative robustness guards;
- zero right-censoring remains the current safe v1 candidate rule and is a coverage limitation yielding `INSUFFICIENT_EVIDENCE`;
- base execution assumptions and unavailable execution facts remain evidence-bound/fail-closed;
- no universal 2bp or 2x threshold is reinstated.

## Owner research-design gate

The current statistical package has exhausted the safe technical next step and now requires an Owner decision.

### OPTION_A — preserve 12/6/6 and accept IE-only historical v1

```text
OPTION_A=PRESERVE_FROZEN_12_6_6_ACCEPT_IE_ONLY_HISTORICAL_V1
```

Meaning:
- keep Protocol v1.0 and 12/6/6 unchanged;
- do not claim a statistically defensible positive PASS from the six-month historical cohorts under the current general-domain profile;
- continue Human Playbook source extraction, deterministic operationalization and engineering;
- positive acceptance requires a later separately authorized evidence path, most plausibly genuinely prospective Shadow/Forward evidence or another future Owner-approved design.

This is protocol-consistent because `INSUFFICIENT_EVIDENCE` is already a frozen legitimate result, but intentionally making historical v1 IE-only is a material research-policy choice and is not silently adopted.

### OPTION_B — authorize redesign of positive-acceptance evidence path

```text
OPTION_B=AUTHORIZE_NEW_POSITIVE_ACCEPTANCE_EVIDENCE_DESIGN_PACKAGE
```

Meaning:
- authorize a new bounded research-design package aimed at restoring a defensible positive-acceptance path;
- it may investigate longer/prospective evidence windows or a rigorously justified admissible-domain design;
- this authorization does not approve any specific pooling rule, longer window, threshold or prospective trading mode;
- any frozen chronology/semantic change still requires new protocol version, material independent review and Owner approval.

### Project-brain recommendation

```text
PROJECT_BRAIN_RECOMMENDATION=OPTION_A
PROJECT_BRAIN_RECOMMENDATION_CONFIDENCE=MEDIUM_HIGH
```

Reason: preserve the frozen governance and statistical integrity rather than manufacture a PASS path using arbitrary knobs. This recommendation does not authorize future Shadow/Forward execution.

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
- non-candidate engineering/evidence work that cannot bias the Owner acceptance-path decision;
- synthetic/non-candidate statistical reproducibility inspection.

NOT AUTHORIZED:
- locking an IE-only Common Statistical Profile v1 before Owner approval;
- drafting candidate 0.4 with invented inference semantics;
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
ADDITIONAL_STATISTICAL_REVIEW_LANE=NOT_JUSTIFIED_BEFORE_OWNER_DECISION
```

No new framework/API is justified. The blocker is now a research-design decision, not lack of another reviewer.

## Known limitations / tech debt

- `TD-001`: trusted day/week statistics must use `SessionMetadata`.
- `TD-002`: partial-close equity/unrealized/drawdown path snapshots unsafe; final realized round-trip totals not corrupted.
- `LIMIT-001`: missing governed historical price-limit facts fail closed for affected confirmatory execution.
- `DECISION-001`: live AI scene-recognition mode remains Owner-gated/unresolved.

Round-trip ledger, holding/day aggregation and hypothesis/wave joins remain small engineering deltas. Full evaluator implementation waits for the Owner acceptance-path decision and a subsequently lockable profile design.

## Verification status

Latest code-bearing baseline in main remains:

```text
python -m unittest discover -s tests -v
235 tests OK
3 skipped
exit 0
```

The inference-resolution lane independently reported `235 OK / 3 skipped`, exit 0, from its isolated worktree. Its commit `dd84dba7...` is exactly one commit ahead of baseline `83e8aa4...` and adds only the review artifact and synthetic support script. No production/test code changed.

## Current next action

```text
CURRENT_NEXT_ACTION=OWNER_DECISION_COMMON_STATISTICAL_PROFILE_V1_ACCEPTANCE_PATH
CURRENT_NEXT_ACTION_AUTHORITY=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_ADJUDICATION_V0_3.md
OWNER_DECISION_REQUIRED=OPTION_A_OR_OPTION_B
PROFILE_STATUS=BLOCKED_AT_RESEARCH_DESIGN_GATE
TOOL_DECISION=USE_EXISTING
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
OWNER_ACTION=REQUIRED
```

No additional statistical reviewer lane should be opened before the Owner decision.

## Progress estimates — engineering estimates, not evidence facts

| Stage / domain | Status | Estimate |
| --- | --- | ---: |
| Architecture / Bootstrap | Skeleton v1.0 accepted | 100% |
| Data Substrate | canonical corpus accepted | ~90% |
| Strategy Catalog | identity/playbook foundations; real extracted playbooks not yet built | ~58% |
| Backtest & Validation | engine/firewall substantial; acceptance-path Owner gate | ~66% |
| Human Playbook Research Loop | protocol/source/firewall ready; real claim extraction not started | ~44% |
| Trading Loop | early deterministic foundations | ~15% |
| Ledger / Observability | foundational pieces only | ~25% |
| Overall project | research-foundation stage | ~46% |

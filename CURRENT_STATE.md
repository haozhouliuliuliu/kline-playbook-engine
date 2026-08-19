# CURRENT_STATE

## Project phase

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE_BASELINE=Skeleton_v1.0
ARCHITECTURE_STATUS=ACCEPTED
ADOPTED_CONTRACT_VERSION=3.1
ADOPTED_CONTRACT_SHA256=3b5ceaaa3696375b941fd2aaba95615cf9352dcada3696b60137650bf690101e
CURRENT_BLOCKER=TARGETED_INDEPENDENT_STATISTICAL_DELTA_REVIEW_PENDING
CURRENT_WORK_PACKAGE=COMMON_STATISTICAL_PROFILE_V1_REVISION_AFTER_PARALLEL_REVIEW
CURRENT_WORK_PACKAGE_STATUS=REVISION_CANDIDATE_0_3_COMPLETE_TARGETED_REVIEW_REQUIRED
CURRENT_WORK_PACKAGE_AUTHORITY=docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md
CURRENT_WORK_PACKAGE_ADJUDICATION=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md
CONVERSATION_HANDOFF_STATUS=TAKEOVER_ACCEPTED
FRESH_CONVERSATION_TAKEOVER_ACCEPTANCE=APPROVED
PROJECT_EXECUTION_DURING_TAKEOVER_CHECK=RELEASED
OWNER_ACTION=NONE
```

The fresh-conversation takeover was accepted on 2026-08-19. The temporary read-only takeover pause is released. The approval changed no research semantics and unlocked no dataset cohort.

## Binding direction / anti-regression

```text
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
RESEARCH_DIRECTION_STATUS=OWNER_APPROVED
RESEARCH_ROUTE_ANTI_REGRESSION=HUMAN_PLAYBOOK_FIRST_NO_DATA_FIRST_KLINE_MINING
PROHIBITED_DEFAULT_RESEARCH_ROUTE=UNCONSTRAINED_KLINE_INDICATOR_PATTERN_PARAMETER_MINING
```

Binding route:

```text
traceable human trading experience
-> source-faithful AI extraction and structuring
-> versioned Playbook Contract
-> deterministic/versioned machine operationalization
-> governed historical validation of applicability and failure conditions
-> strict validation / protected-holdout governance
-> accepted or rejected playbook
```

Skeleton v1.0 remains accepted. Generic architecture wording that AI may find candidate ideas does not authorize data-first K-line/chart-pattern/indicator/rule/parameter mining. A move back toward that route is an Owner-gated research-direction change.

## Research Protocol v1.0 — FROZEN / BINDING

Authorities:
- `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
- `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`

```text
RESEARCH_PROTOCOL_VERSION=1.0
RESEARCH_PROTOCOL_STATUS=FROZEN_BINDING
CHRONOLOGICAL_SPLIT_STATUS=FROZEN_12_6_6
PERFORMANCE_RESEARCH_STARTED=NO
REAL_CLAIM_EXTRACTION_STARTED=NO
REAL_CLAIM_EXTRACTION_ENVIRONMENT=VERIFIED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
```

Frozen chronology:

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
```

`PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT != PROSPECTIVE_GENUINELY_UNSEEN_DATA`.
`INSUFFICIENT_EVIDENCE` remains a frozen legitimate result. Material changes to frozen research semantics or chronology require a new protocol version, material independent adversarial review, and the normal Owner gate.

Frozen safeguards include source/interpretation/operationalization separation; exactly one source-justified PRIMARY before outcome testing; ambiguity stop; lineage/exposure inheritance; SOURCE_ONLY technical denial; immutable Research Wave denominator; common statistical profile lock before first candidate outcome; dependence-aware evidence sufficiency; CAT1/CAT2/CAT3 validation revision rules; irreversible historical-final exposure.

## Pre-outcome research firewall — ACCEPTED

Implementation evidence: `docs/evidence/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0.md`

Final acceptance: `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_FINAL_ACCEPTANCE_V1_2.md`

```text
PREOUTCOME_FIREWALL_IMPLEMENTATION=COMPLETE_VERIFIED_ACCEPTED
SOURCE_ONLY_CLAIM_EXTRACTION_RUNNER=VERIFIED
RESEARCH_WAVE_IDENTITY_BINDING=VERIFIED
STATISTICAL_PROFILE_INTERFACE=VERIFIED
PRE_OUTCOME_GATE_STATUS=VERIFIED_FAIL_CLOSED
HISTORICAL_FINAL_HOLDOUT_LOCK=ENFORCED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
FIREWALL_TESTS=54
FULL_TESTS=235_OK
FULL_TESTS_SKIPPED=3
```

`src/research_firewall.py` is the single owner of new pre-outcome access rules. Candidate access is identity-bound to exact hypothesis/wave/profile/SOURCE_ONLY/PRIMARY/scope/search registration; callers cannot self-assert lock booleans.

## Common Statistical Profile v1 — active state

First candidate remains historical design evidence:

```text
ORIGINAL_CANDIDATE_DOC=docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md
ORIGINAL_CANDIDATE_COMMIT=6ef668fd7214fcef2f12b71cb3e9ea2a36bfcaf7
ORIGINAL_CANDIDATE_STATUS=SUPERSEDED_FOR_ACTIVE_DESIGN_NOT_LOCKED
```

Integrated pre-revision evidence:
- engine capability audit: `docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md`;
- compatibility crosswalk: `docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ENGINE_COMPATIBILITY_CROSSWALK.md`;
- adversarial review: `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADVERSARIAL_REVIEW.md`, `GO_WITH_REQUIRED_CHANGES`, 3 CRITICAL / 6 HIGH;
- adjudication: `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`.

Adjudicated requirements remain binding for this package: separate materiality/detectability; remove `2H-1` ESS; pin `position_id` round-trip semantics; pin holding/multi-week handling; simplify/justify sufficiency; separate fee/slippage; guard one event/window concentration; add `DATA_BLOCKED`; align multiplicity with Research Wave identity; correct Romano-Wolf.

### Revision candidate 0.3

```text
REVISION_CANDIDATE_VERSION=v1.0-revision-candidate-0.3
REVISION_CANDIDATE_DOC=docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE.md
REVISION_CANDIDATE_COMMIT=aa99e92c959341eefa0077f6d1a2fa3be92a927f
REVISION_EVIDENCE_DOC=docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_EVIDENCE.md
REVISION_EVIDENCE_COMMIT=055466d819b19078a54cb220f327200f04fd48b9
REVISION_CANDIDATE_STATUS=NOT_LOCKED_TARGETED_DELTA_REVIEW_REQUIRED
NO_CANDIDATE_OUTCOME_DATA_USED=YES
CURRENT_INFERENCE_CANDIDATE=DAILY_SCORE_SELF_NORMALIZATION
WEEKLY_MBB_DRAFT=REJECTED_PRE_OUTCOME_AFTER_SYNTHETIC_SMOKE_TEST
```

Key revision choices, all still candidate until independent delta review:
- one engine `position_id` = one round-trip observation; adds/partial closes aggregated; forced liquidation terminal; concrete-contract roll creates separate round trips;
- primary estimand remains equal-weight mean per-round-trip net return on entry notional, explicitly interpreted as per-decision quality rather than capital productivity;
- complete authoritative trading-day process `(S_d,C_d)` includes zero-exit days; `theta_hat=sum S/sum C`;
- inference candidate uses scalar daily score `Z_d(theta0)=S_d-theta0*C_d` with Shao-style self-normalization, avoiding an ESS heuristic and a user-chosen block length;
- exact signed-pivotal calibration artifact is not yet accepted/built and must be independently reviewed before profile lock;
- candidate support floors are `N>=20` and at least six active exit weeks, plus zero right-censoring and nondegenerate self-normalizer; these are explicit reviewable governance floors, not statistical laws;
- no universal 2bp extra edge floor and no universal 2x friction hard gate; base execution assumptions remain identity-bound, with break-even diagnostics and separately identity-bound slippage sensitivity if later used;
- LOTO/LOWO sign robustness guards one trade or one week carrying the apparent edge;
- disposition states: `DATA_BLOCKED / INTEGRITY_FAIL / INSUFFICIENT_EVIDENCE / FAIL / PASS`;
- Holm remains the simple v1 multiplicity candidate, not locked; Romano-Wolf description is corrected and remains a possible later refinement;
- every separately outcome-inspected parameter point/branch/scope that can receive its own conclusion is separately counted unless a distinct pre-registered within-search correction is designed.

Synthetic-only smoke evidence in the revision evidence file found the self-normalized candidate reasonably calibrated in several mild/moderate short-memory fixtures but still visibly liberal under extreme persistence at six-month lengths. This is a required independent-review attack surface, not acceptance evidence.

Reviewer replacement numbers/methods from the previous review remain advisory only and are not project authority.

## Canonical historical corpus — ACCEPTED

```text
CANONICAL_PRODUCTS=cu,al,ni,au,ag,rb
CANONICAL_COVERAGE=2024-01-01..2025-12-31
CANONICAL_GRANULARITY=1-minute
CONCRETE_CONTRACTS=212
NORMALIZED_ROWS=15280452
CANONICAL_CORPUS_IDENTITY=1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8
CROSS_SOURCE_RESULT=32841_MATCH/0_MISMATCH/0_NOT_COMPARABLE/139_NOT_AVAILABLE
```

Corpus construction created no project-recorded strategy-family DEVELOPMENT/VALIDATION/historical-final exposure.

## Human Playbook source layer

```text
FIRST_WAVE_SOURCE_LAYER_RESULT=GO
PROJECT_LED_DISCOVERY=PRIMARY
OWNER_SUPPLIED_MATERIAL=SUPPLEMENTAL
```

Completed source dossiers include Peter Brandt, Al Brooks, Linda Raschke, Adam Grimes, Brett Steenbarger, Steidlmayer -> Dalton Market Profile lineage, and skeptical/counter-evidence methods. China-first derivative leads remain provenance-limited as recorded in the source authorities.

## Current authorization boundaries

AUTHORIZED NOW:
- source discovery/provenance;
- controlled real source-faithful claim extraction in verified SOURCE_ONLY;
- deterministic non-outcome operationalization/tests;
- Common Statistical Profile revision/review/implementation work without candidate outcomes;
- synthetic/non-candidate statistical and engine sanity tests;
- isolated independent review under the collaboration/worktree rules.

NOT AUTHORIZED:
- data-first K-line/chart-pattern/indicator/rule/parameter mining as project research route;
- candidate PnL/equity/expectancy/Sharpe/win-loss or equivalent candidate-quality inspection before revised profile independent acceptance + lock + real wave + firewall pass;
- Validation access;
- historical final-holdout unlock;
- changing frozen 12/6/6 or research semantics without new protocol/Owner gate;
- Shadow automated trading;
- real-money/broker orders;
- discretionary live LLM critical path;
- new paid commitments;
- permanent RiskGate semantics without Owner approval;
- large orchestration/microservices expansion;
- importing strategy conclusions/results/parameters from other projects.

## Tools / execution workflow

```text
TOOL_DECISION=USE_EXISTING
TOOL_DECISION_SCOPE=COMMON_STATISTICAL_PROFILE_V1_TARGETED_DELTA_REVIEW
PAID_CHAT_RELAY_ORCHESTRATOR=NOT_ADOPTED_CURRENTLY
BRITTLE_VSCODE_UI_CHAT_AUTOMATION=NOT_ADOPTED_CURRENTLY
CURRENT_DS_RELAY_MODE=OWNER_MANUAL_RELAY_WHEN_LOCAL_AGENT_IS_NEEDED
```

No new tool gap is demonstrated. DeepSeek V4 Flash is an Owner-side local reviewer/worker capability, not a project-adopted runtime dependency. Safe repository-only work remains GPT-owned; the next step specifically needs an independent statistical reviewer, so a bounded local review lane is appropriate.

## Known limitations / technical debt

- `TD-001`: new trusted day/week statistics must use `SessionMetadata`, not bootstrap calendar semantics.
- `TD-002`: partial-close unrealized/equity/drawdown path snapshots are unsafe; final realized round-trip totals are not corrupted.
- `LIMIT-001`: missing governed historical price-limit facts fail closed for affected real confirmatory execution; data/governance blocker, not silent fill corruption.
- `DECISION-001`: live AI scene-recognition mode remains unresolved / Owner-gated.

Engine facts: round-trip ledger, holding/day aggregation and hypothesis/wave joins remain small engineering deltas; multi-day portfolio/equity series remains a medium delta. Full evaluator implementation waits until the statistical profile survives targeted review.

## Verification status

Latest code-bearing verification baseline remains:

```text
python -m unittest discover -s tests -v
235 tests OK
3 skipped
exit 0
```

No production/test code changed in the takeover or statistical-design revision commits. The synthetic method smoke tests were private research calculations and are recorded in the revision evidence; they are not a rerun of the project code suite.

## Current next action

```text
CURRENT_NEXT_ACTION=TARGETED_INDEPENDENT_DELTA_REVIEW_COMMON_STATISTICAL_PROFILE_V1_REVISION_0_3
CURRENT_NEXT_ACTION_AUTHORITY=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md
REVIEW_TARGET=docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_CANDIDATE.md
REVIEW_EVIDENCE=docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_REVISION_EVIDENCE.md
PROFILE_STATUS=REVISION_CANDIDATE_NOT_LOCKED
TOOL_DECISION=USE_EXISTING
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
OWNER_ACTION=NONE
```

The review is deliberately targeted only at materially changed statistical definitions. It must not reopen frozen Protocol v1.0/12/6/6, must not inspect candidate outcomes, and must not treat the prior reviewer's proposed replacement numbers as authority. After the review returns, project brain will adjudicate the delta and either revise again or accept/lock the profile under existing authority.

## Progress estimates — engineering estimates, not evidence facts

| Stage / domain | Status | Estimate |
| --- | --- | ---: |
| Architecture / Bootstrap | Skeleton v1.0 accepted | 100% |
| Data Substrate | canonical corpus accepted; execution metadata debt remains | ~90% |
| Strategy Catalog | identity/playbook foundations; real extracted playbooks not yet built | ~58% |
| Backtest & Validation | engine + firewall substantial; profile awaiting delta review | ~66% |
| Human Playbook Research Loop | protocol/source/firewall ready; real claim extraction not started | ~44% |
| Trading Loop | early deterministic foundations only | ~15% |
| Ledger / Observability | foundational evidence/ledger pieces only | ~25% |
| Overall project | research-foundation stage | ~46% |

Percentages are conservative engineering estimates, not evidence facts and not derived from test counts.

## Owner decision gates

Owner approval remains required for changes to frozen research semantics/chronology, historical-final unlock, new paid commitments, irreversible external actions, authenticated acquisition with material new data-flow risk, permanent risk rules, real-money/broker actions, and live critical-path changes.

No new research/product semantic Owner action is currently required.

# CURRENT_STATE

## Project phase

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE_BASELINE=Skeleton_v1.0
ARCHITECTURE_STATUS=ACCEPTED
ADOPTED_CONTRACT_VERSION=3.1
CURRENT_BLOCKER=NONE
CURRENT_WORK_PACKAGE=TARGETED_SOURCE_SEMANTIC_COMPLETION_STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION_V0_1
CURRENT_WORK_PACKAGE_STATUS=READY_TO_START_IN_VERIFIED_SOURCE_ONLY
CURRENT_WORK_PACKAGE_AUTHORITY=docs/research/HUMAN_PLAYBOOK_CLAIM_CORPUS_TRIAGE_V0_1.md
CURRENT_RESEARCH_POLICY=docs/research/HUMAN_PLAYBOOK_HISTORICAL_V1_EVIDENCE_POLICY_V1_0.md
SOURCE_ACQUISITION_POLICY=docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md
CONVERSATION_HANDOFF_STATUS=TAKEOVER_ACCEPTED
OWNER_ACTION=NONE
```

## Binding research direction / anti-regression

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
-> governed historical validation of applicability/failure
-> strict validation/protected-holdout governance
-> accepted/rejected playbook only when a separately authorized defensible acceptance path exists
```

No strategy/results/parameters/failure-history facts may be imported from another project.

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
REAL_CLAIM_EXTRACTION_STARTED=YES
REAL_CLAIM_EXTRACTION_ENVIRONMENT=VERIFIED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
```

`INSUFFICIENT_EVIDENCE` remains a frozen legitimate result. Material changes to frozen research semantics or chronology require a new protocol version, material independent review and Owner gate.

## Owner Option A — APPROVED

Authorities:
- `docs/evidence/HUMAN_PLAYBOOK_HISTORICAL_V1_IE_ONLY_OWNER_APPROVAL_2026-08-19.md`
- `docs/research/HUMAN_PLAYBOOK_HISTORICAL_V1_EVIDENCE_POLICY_V1_0.md`

```text
OWNER_DECISION=OPTION_A_APPROVED
FROZEN_12_6_6=PRESERVED
STRONG_FWER_ACCEPTANCE_TARGET=UNCHANGED
HISTORICAL_V1_GENERAL_DOMAIN_POSITIVE_PASS=UNAVAILABLE_CURRENTLY
STATISTICAL_POSITIVE_ACCEPTANCE_PACKAGE=PARKED
```

The project does not lower the statistical standard or invent arbitrary gates merely to manufacture a historical PASS. This does not authorize longer windows, pooling, Shadow/Forward, weaker error-rate claims or new statistical thresholds.

## Common Statistical Profile v1 — parked

```text
REVISION_CANDIDATE_VERSION=v1.0-revision-candidate-0.3
REVISION_CANDIDATE_STATUS=NOT_LOCKABLE_AS_PASS_BASIS
PROFILE_0_4_DRAFTABLE=NO_WITH_CURRENT_INFERENCE_EVIDENCE
CURRENT_INFERENCE_CANDIDATE=NONE_ADOPTED_FOR_POSITIVE_PASS
```

Durable statistical-review evidence:

```text
TARGETED_DELTA_REVIEW_COMMIT=cbfc1ae6e6b833292181252d3d4fe14014a22fae
SECOND_SN_REVIEW_COMMIT=a4008dfaf6996d13f269077f8e4c537857d18ab9
INFERENCE_RESOLUTION_COMMIT=dd84dba7d37a2dd00ab8480c7f79ccfd37b7b118
PARALLEL_REVIEW_ADJUDICATION=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_PARALLEL_REVIEW_ADJUDICATION_V0_2.md
INFERENCE_RESOLUTION_ADJUDICATION=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_ADJUDICATION_V0_3.md
```

Current inference facts: Shao-style self-normalization is not lockable as a positive-PASS basis at the investigated six-month lengths under strong persistence/left-skew; Holm cannot repair invalid per-hypothesis p-values; investigated wild/block/grouped/subsampling alternatives are not adopted; no arbitrary shape/autocorrelation gate or weakened nominal error-rate is adopted. This is not an impossibility theorem for all future methods.

## Pre-outcome research firewall

```text
PREOUTCOME_FIREWALL_IMPLEMENTATION=COMPLETE_VERIFIED_ACCEPTED
SOURCE_ONLY_POLICY=VERIFIED
SOURCE_ONLY_CLAIM_EXTRACTION_RUNNER=VERIFIED
REAL_CLAIM_EXTRACTION_ENVIRONMENT=VERIFIED
RESEARCH_WAVE_IDENTITY_BINDING=VERIFIED
STATISTICAL_PROFILE_INTERFACE=VERIFIED
PRE_OUTCOME_GATE_STATUS=VERIFIED_FAIL_CLOSED
HISTORICAL_FINAL_HOLDOUT_LOCK=ENFORCED
FIREWALL_TESTS=54
FULL_TESTS_BASELINE=235_OK_3_SKIPPED
```

`src/research_firewall.py` remains the single owner of new pre-outcome access rules.

## Claim extraction authority

Active schema:
`docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`

```text
SOURCE_CLAIM != PROJECT_AI_INTERPRETATION != MACHINE_OPERATIONALIZATION
CLAIM_STATUS=EXPLICIT|INFERRED|UNKNOWN
UNKNOWN_OVER_GUESSING=REQUIRED
EXACTLY_ONE_SOURCE_JUSTIFIED_PRIMARY_BEFORE_ANY_FUTURE_OUTCOME_TEST=REQUIRED
AMBIGUOUS_PRIMARY=STOP
```

Every real extraction session must be bound to a verified SOURCE_ONLY session/source-bundle identity. No extraction may silently invent unavailable K-line proxies or inspect protected-period market outcomes.

## Source acquisition / data budget policy

```text
SOURCE_ACQUISITION_DEFAULT=FREE_PUBLIC_UNAUTHENTICATED_FIRST
PAID_SOURCE_PURCHASE_DEFAULT=NO
EXISTING_MARKET_DATA_DEFAULT_BOUNDARY=CANONICAL_1MIN_OHLCV_PLUS_GOVERNED_METADATA
PAYWALL_OR_DRM_BYPASS=FORBIDDEN
```

Paid sources/data may be listed as optional candidates but are not purchased, subscribed to or treated as the default blocker. When an adequate public source exists, use it. Missing data surfaces are recorded as not/partially observable rather than replaced by invented OHLCV proxies.

## Real claim extraction Wave 1 — ACCEPTED

Integration review:
`docs/reviews/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_1_INTEGRATION_REVIEW_V0_1.md`

```text
WAVE_1_BRANCH=parallel/claim-extraction-wave1-public
WAVE_1_COMMIT=b68da256bbc493ac6e1de0fe02b7fde5a0396ddf
WAVE_1_SOURCE=SRC-GRIMES/MAT-GRIMES-MARKETLIFE
WAVE_1_SOURCE_ACCESS=FREE_PUBLIC_UNAUTHENTICATED
WAVE_1_CLAIMS=15
WAVE_1_EXPLICIT=13
WAVE_1_INFERRED=2
WAVE_1_SOURCE_ONLY_VERIFIED=YES
WAVE_1_PROTECTED_OUTCOME_DENIAL=PASS
WAVE_1_NO_CANDIDATE_OUTCOME_DATA_USED=YES
WAVE_1_STATUS=ACCEPTED_WITH_INTEGRATION_CORRECTIONS
```

Durable corrections:
- `C-W1-009` remains source-faithful but `PRIMARY_NOT_YET_JUSTIFIED` because swing identification and tolerance are not source-pinned;
- `C-W1-011` remains `PARTIALLY_OBSERVABLE`; the worker's `LIMIT-001` cross-reference was rejected as unrelated.

Accepted Wave 1 post-review counts:

```text
OBSERVABLE_NOW=1
PARTIALLY_OBSERVABLE=3
NOT_OBSERVABLE_WITH_CURRENT_DATA=1
NOT_APPLICABLE=10
PRIMARY_CANDIDATES=0
PRIMARY_NOT_YET_JUSTIFIED=15
```

## Real claim extraction Wave 2 — ACCEPTED

Integration review:
`docs/reviews/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_WAVE_2_INTEGRATION_REVIEW_V0_1.md`

Worker evidence:

```text
WAVE_2_BRANCH=parallel/claim-extraction-wave2-steenbarger-public
WAVE_2_COMMIT=c0fef50bb3b0f5a97c7bdf472d5a9e2d9339273a
WAVE_2_SOURCE=SRC-STEENBARGER/MAT-STEENBARGER-TRADERFEED
WAVE_2_SOURCE_BUNDLE=SB-W2-PUBLIC-STEENBARGER-V1
WAVE_2_SOURCE_ACCESS=FREE_PUBLIC_UNAUTHENTICATED
WAVE_2_CLAIMS=18
WAVE_2_EXPLICIT=18
WAVE_2_INFERRED=0
WAVE_2_SOURCE_ONLY_VERIFIED=YES
WAVE_2_PROTECTED_OUTCOME_DENIAL=PASS
WAVE_2_NO_CANDIDATE_OUTCOME_DATA_USED=YES
WAVE_2_STATUS=ACCEPTED_WITH_INTEGRATION_CORRECTIONS
```

Integration corrections:
- worker claim that `HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md` and Wave 1 integration review were absent at baseline `04f5ecb...` is rejected; both files are present at that exact commit. This was a local lookup/environment error, not a project fact;
- `C-W2-016`: source explicitly supports sector non-confirmation as counterevidence in the example, but not the generalized rule `sector non-confirmation -> treat day as range day`; applicability remains example-specific / not fully pinned;
- `C-W2-018`: explicit source claim is only that the hard trade is about preparation; exact preparation components are not pinned by that sentence and are not promoted as EXPLICIT.

Accepted Wave 2 post-review counts:

```text
OBSERVABLE_NOW=5
PARTIALLY_OBSERVABLE=9
NOT_OBSERVABLE_WITH_CURRENT_DATA=2
NOT_APPLICABLE=2
PRIMARY_CANDIDATES=0
PRIMARY_NOT_YET_JUSTIFIED=18
```

The worker commit changed only four intended Wave 2 artifacts. No repository memory file was committed; any local-agent memory is not a project authority.

## Cross-wave claim corpus triage

Authority:
`docs/research/HUMAN_PLAYBOOK_CLAIM_CORPUS_TRIAGE_V0_1.md`

```text
REAL_CLAIM_EXTRACTION_WAVES_ACCEPTED=2
TOTAL_CLAIMS=33
TOTAL_EXPLICIT=31
TOTAL_INFERRED=2
TOTAL_UNKNOWN=0
TOTAL_OBSERVABLE_NOW=6
TOTAL_PARTIALLY_OBSERVABLE=12
TOTAL_NOT_OBSERVABLE_WITH_CURRENT_DATA=3
TOTAL_NOT_APPLICABLE=12
TOTAL_PRIMARY_CANDIDATES=0
TOTAL_PRIMARY_NOT_YET_JUSTIFIED=33
```

Project-brain decision:

```text
FIRST_PLAYBOOK_CONTRACT_CANDIDATE_FAMILY=STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION
CANDIDATE_FAMILY_STATUS=SOURCE_SEMANTIC_COMPLETION_REQUIRED_NOT_PRIMARY_NOT_OPERATIONALIZED
SELECTION_BASIS=SOURCE_COMPLETENESS_PLUS_EXISTING_DATA_COMPATIBILITY_NOT_EXPECTED_PERFORMANCE
```

Target claims: Wave 2 `C-W2-006`, `C-W2-008`, `C-W2-017`; supporting context `C-W2-002`, `C-W2-003`, `C-W2-009`.

The next package must determine from official free/public source evidence whether a faithful price/volume false-breakout/range-reversion playbook can be stated using the current data surface. It may not simply delete TICK/Market Delta/sector confirmation from the human method and call the remainder source-equivalent. If the source does not support a faithful current-data formulation, the correct result is `SOURCE_FAITHFUL_PRICE_VOLUME_PLAYBOOK_DRAFTABLE=NO`.

## Human Playbook source layer

```text
FIRST_WAVE_SOURCE_LAYER_RESULT=GO
PROJECT_LED_DISCOVERY=PRIMARY
OWNER_SUPPLIED_MATERIAL=SUPPLEMENTAL
```

Registered/completed source layer includes Brandt, Brooks, Raschke, Grimes, Steenbarger, Steidlmayer -> Dalton Market Profile lineage and skeptical/counter-evidence methods. China-first leads retain their recorded provenance limitations; 青泽 remains bibliographic-level only without authorized text/sample; competition rankings remain discovery-only.

Source authorities:
- `docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md`
- `docs/research/HUMAN_PLAYBOOK_SOURCE_LAYER_FIRST_WAVE_CLOSEOUT.md`

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

## Current authorization boundaries

AUTHORIZED NOW:
- free/public source discovery and provenance;
- controlled real source-faithful claim extraction / semantic completion in verified SOURCE_ONLY;
- claim/interpretation/lineage/exposure evidence work;
- deterministic non-outcome operationalization/tests where source meaning is adequately pinned;
- non-candidate engineering that cannot bias a future acceptance design;
- synthetic/non-candidate sanity/reproducibility work.

NOT AUTHORIZED:
- data-first K-line/chart-pattern/indicator/rule/parameter mining as project route;
- candidate PnL/equity/expectancy/Sharpe/win-loss or equivalent candidate-quality inspection;
- Validation access;
- historical final-holdout access;
- Shadow/Forward trading/evidence collection without later authority;
- changing frozen 12/6/6 or Protocol semantics without new version/review/Owner gate;
- real-money/broker actions;
- discretionary live-LLM critical path;
- new paid commitments;
- permanent risk-rule changes without Owner approval.

## Tools / execution workflow

```text
TOOL_DECISION=USE_EXISTING
TOOL_DECISION_SCOPE=TARGETED_SOURCE_SEMANTIC_COMPLETION_STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION_V0_1
PAID_CHAT_RELAY_ORCHESTRATOR=NOT_ADOPTED_CURRENTLY
BRITTLE_VSCODE_UI_CHAT_AUTOMATION=NOT_ADOPTED_CURRENTLY
CURRENT_DS_RELAY_MODE=OWNER_MANUAL_RELAY_WHEN_LOCAL_AGENT_IS_NEEDED
```

No new framework/API is justified. The existing verified SOURCE_ONLY runner and free/public web acquisition are sufficient. Local DeepSeek is justified only for project-owned SOURCE_ONLY execution that the GitHub integration lane cannot emulate.

## Known limitations / tech debt

- `TD-001`: trusted day/week statistics must use `SessionMetadata`.
- `TD-002`: partial-close equity/unrealized/drawdown path snapshots unsafe; final realized round-trip totals not corrupted.
- `LIMIT-001`: missing governed historical price-limit facts fail closed for affected confirmatory execution.
- `DECISION-001`: live AI scene-recognition mode remains Owner-gated/unresolved.

Statistical evaluator/round-trip-ledger implementation is not the current priority while the positive-acceptance path is parked.

## Verification status

Latest code-bearing main baseline remains:

```text
python -m unittest discover -s tests -v
235 tests OK
3 skipped
exit 0
```

Wave 2 independently reported `tests.test_research_firewall`: 54 OK and the full suite: 235 OK / 3 skipped / exit 0. Its commit changed no production `src/` or tests.

## Current next action

```text
CURRENT_NEXT_ACTION=TARGETED_SOURCE_SEMANTIC_COMPLETION_FOR_STEENBARGER_FALSE_BREAKOUT_RANGE_REVERSION
CURRENT_NEXT_ACTION_AUTHORITY=docs/research/HUMAN_PLAYBOOK_CLAIM_CORPUS_TRIAGE_V0_1.md
TARGET_OUTPUT=SOURCE_FAITHFUL_PRICE_VOLUME_PLAYBOOK_DRAFTABLE_YES_OR_NO
SOURCE_SCOPE=OFFICIAL_FREE_PUBLIC_PRE_2024_TRADERFEED_ONLY
NO_BROAD_WAVE_3_YET=YES
REAL_CLAIM_EXTRACTION_STARTED=YES
PROFILE_STATUS=POSITIVE_ACCEPTANCE_PATH_PARKED_NOT_LOCKED
TOOL_DECISION=USE_EXISTING
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
OWNER_ACTION=NONE
```

Do not start a third broad source wave yet. First determine whether the selected Steenbarger false-breakout/range-reversion family can be source-faithfully completed into a current-data-compatible non-outcome Playbook Contract. A negative result is acceptable and should redirect source selection rather than trigger proxy invention.

## Progress estimates — engineering estimates, not evidence facts

| Stage / domain | Status | Estimate |
| --- | --- | ---: |
| Architecture / Bootstrap | Skeleton v1.0 accepted | 100% |
| Data Substrate | canonical corpus accepted | ~90% |
| Strategy Catalog | 2 real claim waves accepted; first Playbook Contract candidate selected | ~66% |
| Backtest & Validation | engine/firewall substantial; positive acceptance path parked | ~66% |
| Human Playbook Research Loop | 33 claims triaged; semantic completion target selected | ~57% |
| Trading Loop | early deterministic foundations | ~15% |
| Ledger / Observability | foundational pieces only | ~25% |
| Overall project | research-foundation stage | ~52% |

Percentages are conservative engineering estimates, not evidence facts.

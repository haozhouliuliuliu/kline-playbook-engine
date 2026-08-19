# CURRENT_STATE

## Project phase

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE_BASELINE=Skeleton_v1.0
ARCHITECTURE_STATUS=ACCEPTED
ADOPTED_CONTRACT_VERSION=3.1
CURRENT_BLOCKER=NONE
CURRENT_WORK_PACKAGE=REAL_SOURCE_FAITHFUL_CLAIM_EXTRACTION_WAVE_1
CURRENT_WORK_PACKAGE_STATUS=READY_TO_START_IN_VERIFIED_SOURCE_ONLY
CURRENT_WORK_PACKAGE_AUTHORITY=docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md
CURRENT_RESEARCH_POLICY=docs/research/HUMAN_PLAYBOOK_HISTORICAL_V1_EVIDENCE_POLICY_V1_0.md
OWNER_OPTION_A_APPROVAL=docs/evidence/HUMAN_PLAYBOOK_HISTORICAL_V1_IE_ONLY_OWNER_APPROVAL_2026-08-19.md
CONVERSATION_HANDOFF_STATUS=TAKEOVER_ACCEPTED
OWNER_ACTION=NONE
```

## Binding research direction

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
-> accepted or rejected playbook when a separately authorized defensible acceptance path exists
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

## Owner Option A — APPROVED

Authority:
- `docs/evidence/HUMAN_PLAYBOOK_HISTORICAL_V1_IE_ONLY_OWNER_APPROVAL_2026-08-19.md`
- `docs/research/HUMAN_PLAYBOOK_HISTORICAL_V1_EVIDENCE_POLICY_V1_0.md`

```text
OWNER_DECISION=OPTION_A_APPROVED
FROZEN_12_6_6=PRESERVED
STRONG_FWER_ACCEPTANCE_TARGET=UNCHANGED
HISTORICAL_V1_GENERAL_DOMAIN_POSITIVE_PASS=UNAVAILABLE_CURRENTLY
STATISTICAL_POSITIVE_ACCEPTANCE_PACKAGE=PARKED
```

The project will not lower the statistical standard or invent arbitrary gates merely to manufacture a historical PASS. This decision does not authorize longer windows, pooling, Shadow/Forward, weaker error-rate claims, or any new statistical threshold.

## Common Statistical Profile v1 — parked after inference resolution

```text
REVISION_CANDIDATE_VERSION=v1.0-revision-candidate-0.3
REVISION_CANDIDATE_STATUS=NOT_LOCKABLE_AS_PASS_BASIS
PROFILE_0_4_DRAFTABLE=NO_WITH_CURRENT_INFERENCE_EVIDENCE
CURRENT_INFERENCE_CANDIDATE=NONE_ADOPTED_FOR_POSITIVE_PASS
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
```

Parallel review / adjudication evidence remains durable:

```text
TARGETED_DELTA_REVIEW_COMMIT=cbfc1ae6e6b833292181252d3d4fe14014a22fae
SECOND_SN_REVIEW_COMMIT=a4008dfaf6996d13f269077f8e4c537857d18ab9
PARALLEL_REVIEW_ADJUDICATION=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_PARALLEL_REVIEW_ADJUDICATION_V0_2.md
INFERENCE_RESOLUTION_COMMIT=dd84dba7d37a2dd00ab8480c7f79ccfd37b7b118
INFERENCE_RESOLUTION_ADJUDICATION=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_INFERENCE_RESOLUTION_ADJUDICATION_V0_3.md
```

Accepted current inference facts:
- the count-return reviewer CRITICAL was rejected as a fixture-target error; the estimand remains the event-weighted per-trade mean `theta=E[S_d]/E[C_d]`;
- Shao-style self-normalization is not lockable as a positive-PASS basis at the six-month cohort lengths under the investigated general-domain regimes;
- strong persistence and left-skew finite-sample anti-conservatism are real threats;
- Holm cannot repair invalid per-hypothesis p-values;
- investigated wild-bootstrap, block-bootstrap, weekly/grouped and subsampling alternatives are not adopted;
- no arbitrary shape/autocorrelation cutoff is adopted;
- no weakened nominal error-rate claim is adopted;
- this is not an impossibility theorem for all conceivable future methods.

Other adjudicated profile facts remain durable design evidence: `position_id` round-trip identity; adds/partial closes aggregated; forced liquidation terminal; zero right-censoring as current safe coverage rule; `DATA_BLOCKED`; LOTO/LOWO as conservative non-statistical robustness guards; parameter-search identity not a multiplicity count unit; no universal 2bp or 2x friction threshold.

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

## Claim extraction authority / boundary

Active schema:
`docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`

```text
SOURCE_CLAIM != PROJECT_AI_INTERPRETATION != MACHINE_OPERATIONALIZATION
CLAIM_STATUS=EXPLICIT|INFERRED|UNKNOWN
UNKNOWN_OVER_GUESSING=REQUIRED
EXACTLY_ONE_SOURCE_JUSTIFIED_PRIMARY_BEFORE_ANY_FUTURE_OUTCOME_TEST=REQUIRED
AMBIGUOUS_PRIMARY=STOP
```

Every real extraction session must be tied to a verified SOURCE_ONLY session/bundle identity. No real extraction may silently invent unavailable K-line proxies or inspect protected-period market outcomes.

## Human Playbook source layer

```text
FIRST_WAVE_SOURCE_LAYER_RESULT=GO
PROJECT_LED_DISCOVERY=PRIMARY
OWNER_SUPPLIED_MATERIAL=SUPPLEMENTAL
```

Completed/registered source layer includes Brandt, Brooks, Raschke, Grimes, Steenbarger, Steidlmayer->Dalton Market Profile lineage and skeptical/counter-evidence methods. China-first leads retain their recorded provenance limitations; 青泽 remains bibliographic-level only without authorized text/sample; competition rankings remain discovery-only.

Source authority:
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

## Authorization boundaries

AUTHORIZED NOW:
- source discovery/provenance;
- controlled real source-faithful claim extraction in verified SOURCE_ONLY;
- claim/interpretation/lineage/exposure evidence work;
- deterministic non-outcome operationalization/tests;
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
TOOL_DECISION_SCOPE=REAL_SOURCE_FAITHFUL_CLAIM_EXTRACTION_WAVE_1
PAID_CHAT_RELAY_ORCHESTRATOR=NOT_ADOPTED_CURRENTLY
BRITTLE_VSCODE_UI_CHAT_AUTOMATION=NOT_ADOPTED_CURRENTLY
CURRENT_DS_RELAY_MODE=OWNER_MANUAL_RELAY_WHEN_LOCAL_AGENT_IS_NEEDED
```

No new framework/API is justified. The existing verified SOURCE_ONLY runner plus existing repository evidence are the required capabilities. A local DeepSeek lane is justified only to execute the project-owned SOURCE_ONLY environment / local source bundle work that the GitHub integration lane cannot safely emulate.

## Known limitations / tech debt

- `TD-001`: trusted day/week statistics must use `SessionMetadata`.
- `TD-002`: partial-close equity/unrealized/drawdown path snapshots unsafe; final realized round-trip totals not corrupted.
- `LIMIT-001`: missing governed historical price-limit facts fail closed for affected confirmatory execution.
- `DECISION-001`: live AI scene-recognition mode remains Owner-gated/unresolved.

Statistical evaluator/round-trip-ledger implementation is not the current priority while the positive-acceptance path is parked.

## Verification status

Latest code-bearing baseline recorded in main:

```text
python -m unittest discover -s tests -v
235 tests OK
3 skipped
exit 0
```

The inference-resolution lane independently reported the same 235 OK / 3 skipped baseline. No production/test code changed in the Owner Option A policy package.

## Current next action

```text
CURRENT_NEXT_ACTION=EXECUTE_FIRST_REAL_SOURCE_FAITHFUL_CLAIM_EXTRACTION_WAVE_IN_VERIFIED_SOURCE_ONLY
CURRENT_NEXT_ACTION_AUTHORITY=docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md
SOURCE_SELECTION_BASIS=TRACEABLE_SOURCE_QUALITY_AND_ANCHORABILITY_NOT_EXPECTED_STRATEGY_PERFORMANCE
REAL_CLAIM_EXTRACTION_STARTED=NO
PROFILE_STATUS=POSITIVE_ACCEPTANCE_PATH_PARKED_NOT_LOCKED
TOOL_DECISION=USE_EXISTING
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
OWNER_ACTION=NONE
```

The first extraction wave should use an already-admitted traceable source with material that can be legally/technically provided to the verified SOURCE_ONLY runner. Source choice must be based on provenance, anchor quality, failure/negative-evidence visibility and observability coverage—not expected backtest performance.

## Progress estimates — engineering estimates, not evidence facts

| Stage / domain | Status | Estimate |
| --- | --- | ---: |
| Architecture / Bootstrap | Skeleton v1.0 accepted | 100% |
| Data Substrate | canonical corpus accepted | ~90% |
| Strategy Catalog | identity/playbook foundations; real claim extraction next | ~60% |
| Backtest & Validation | engine/firewall substantial; positive acceptance path parked | ~66% |
| Human Playbook Research Loop | protocol/source/firewall ready; real extraction ready to start | ~48% |
| Trading Loop | early deterministic foundations | ~15% |
| Ledger / Observability | foundational pieces only | ~25% |
| Overall project | research-foundation stage | ~47% |

Percentages are conservative engineering estimates, not evidence facts.

# CURRENT_STATE

## Project phase

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE_BASELINE=Skeleton_v1.0
ARCHITECTURE_STATUS=ACCEPTED
ADOPTED_CONTRACT_VERSION=3.1
CURRENT_BLOCKER=FULL_PROJECT_SECOND_PASS_AUDIT_FINDINGS
CURRENT_WORK_PACKAGE=FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026_08_20
CURRENT_WORK_PACKAGE_STATUS=FINDINGS_COMPLETE_REPAIR_NOT_YET_PLANNED
CURRENT_WORK_PACKAGE_AUTHORITY=docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md
CURRENT_RESEARCH_POLICY=docs/research/HUMAN_PLAYBOOK_HISTORICAL_V1_EVIDENCE_POLICY_V1_0.md
SOURCE_ACQUISITION_POLICY=docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md
OWNER_ACTION=NONE
```

The second-pass audit intentionally traced the repository from data/metadata foundations through source evidence, Playbook/Strategy identity, firewall, validation/execution, round-trip evidence and the latest unmerged F/G/H branches. It continued after defects were found. No repair package or outcome access was created by the audit.

## Binding research direction / access boundary

```text
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
RESEARCH_DIRECTION_STATUS=OWNER_APPROVED
SOURCE_CLAIM != PROJECT_AI_INTERPRETATION != MACHINE_OPERATIONALIZATION
UNKNOWN_OVER_GUESSING=REQUIRED
EXACTLY_ONE_SOURCE_JUSTIFIED_PRIMARY_BEFORE_ANY_FUTURE_OUTCOME_TEST=REQUIRED
AMBIGUOUS_PRIMARY=STOP
RESEARCH_PROTOCOL_VERSION=1.0
RESEARCH_PROTOCOL_STATUS=FROZEN_BINDING
CHRONOLOGICAL_SPLIT_STATUS=FROZEN_12_6_6
DEVELOPMENT=2024-01-01..2024-12-31
VALIDATION=2025-01-01..2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT=2025-07-01..2025-12-31
PERFORMANCE_RESEARCH_STARTED=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
```

Important second-pass distinction:

```text
VALIDATION_POLICY=LOCKED
VALIDATION_RUNNER_TECHNICAL_LOCK=NOT_ENFORCED
```

The existing validation runner still uses the legacy coarse access path and can produce `VALIDATION_CONFIRMED` without the authoritative candidate pre-outcome gate. No project-recorded real candidate use of that path was found.

## Owner Option A / statistical acceptance

```text
OWNER_DECISION=OPTION_A_APPROVED
FROZEN_12_6_6=PRESERVED
STRONG_FWER_ACCEPTANCE_TARGET=UNCHANGED
HISTORICAL_V1_GENERAL_DOMAIN_POSITIVE_PASS=UNAVAILABLE_CURRENTLY
STATISTICAL_POSITIVE_ACCEPTANCE_PACKAGE=PARKED
CURRENT_INFERENCE_CANDIDATE=NONE_ADOPTED_FOR_POSITIVE_PASS
```

The second-pass audit found that the current `StatisticalProfileRegistry` can technically lock an arbitrary non-TEST_ONLY profile object; therefore registry lock state by itself is not proof of an Owner-approved real profile. This does not change the Owner policy above: no real positive-PASS profile is adopted.

## Canonical data / cost boundary

Recorded accepted corpus facts remain:

```text
CANONICAL_DATASET_ACCEPTED=YES
CANONICAL_PRODUCTS=cu,al,ni,au,ag,rb
CANONICAL_COVERAGE=2024-01-01..2025-12-31
CANONICAL_GRANULARITY=1-minute
CONCRETE_CONTRACTS=212
NORMALIZED_ROWS=15280452
CANONICAL_CORPUS_IDENTITY=1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8
CROSS_SOURCE_RESULT=32841_MATCH/0_MISMATCH/0_NOT_COMPARABLE/139_NOT_AVAILABLE
SOURCE_ACQUISITION_DEFAULT=FREE_PUBLIC_UNAUTHENTICATED_FIRST
PAID_SOURCE_PURCHASE_DEFAULT=NO
EXISTING_MARKET_DATA_DEFAULT_BOUNDARY=CANONICAL_1MIN_OHLCV_PLUS_GOVERNED_METADATA
```

Second-pass qualification:

```text
CANONICAL_PRICE_VALUES_REVOKED=NO
CANONICAL_INTRADAY_COMPLETENESS_PROOF=REAUDIT_REQUIRED
CANONICAL_PROVENANCE_LINKS=GAPS_FOUND
CONCRETE_CONTRACT_RESEARCH_MAPPING_RULE=NOT_FROZEN
HISTORICAL_REALISTIC_MARGIN_FEE_AUTHORITY=NOT_IMPLEMENTED_FOR_CANDIDATE_QUALITY
```

The audit found that truncated/entirely absent session coverage can escape the current missing-bar proof path, and canonical storage has a raw-artifact identity semantic mismatch. This is a proof/provenance defect; it is not evidence that the 15,280,452 stored OHLC rows are numerically wrong.

## Pre-outcome firewall / SOURCE_ONLY state after second-pass audit

Previous `COMPLETE_VERIFIED_ACCEPTED` wording is downgraded.

```text
PREOUTCOME_FIREWALL_CORE_LOGIC=IMPLEMENTED
PREOUTCOME_GATE_INTERNAL_IDENTITY_CHECKS=IMPLEMENTED
PREOUTCOME_GATE_CONNECTED_TO_VALIDATION_RUNNER=NO
COHORT_BOUND_TO_ACTUAL_DATA_ARTIFACT=NO
PRIMARY_SCOPE_SEARCH_BOUND_TO_ACTUAL_PLAYBOOK_STRATEGY_ARTIFACT=NO
FIREWALL_REGISTRIES_DURABLY_RESTORED_AFTER_RESTART=NO
SOURCE_ONLY_API_PROTECTED_OUTCOME_DENIAL=IMPLEMENTED
SOURCE_ONLY_PROJECT_ISSUED_ATTESTATION=NOT_SECURELY_ENFORCED
SOURCE_ONLY_PROCESS_SANDBOX=NOT_IMPLEMENTED
LINEAGE_RENAMING_TECHNICALLY_PREVENTED=NO
HISTORICAL_FINAL_STATE_DURABLE_ACROSS_RESTART=NO
```

No finding proves that prior SOURCE_ONLY workers actually accessed protected market outcomes. It changes what the project's `VERIFIED` label can legitimately claim.

## Human Playbook research state

Accepted source-research history remains evidence, with provenance/verification qualifications from the second-pass audit:
- Grimes Wave 1: integration review accepted with corrections; raw wave artifacts remain on worker branch;
- Steenbarger Wave 2: integration review accepted with corrections; raw wave artifacts remain on worker branch;
- Steenbarger false-breakout: accepted negative semantic result;
- Raschke NR7: accepted negative semantic result;
- Raschke Holy Grail: accepted as source-semantically draftable, not machine-ready.

Current family:

```text
FAMILY=RASCHKE_HOLY_GRAIL_PULLBACK
PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES
PLAYBOOK_MACHINE_READY=NO
PRIMARY_FREEZE_READY=NO
CURRENT_PROJECT_PRODUCT_TRANSFER=INFERRED
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

Additional second-pass gaps include:

```text
EMA_TOUCH_CAUSAL_REFERENCE=NOT_FROZEN
ADX_SOURCE_SEQUENCE_TO_MACHINE_TIME=NOT_FROZEN
EMA_ALGORITHM_SEED_WARMUP_ROUNDING=NOT_IN_INTERPRETATION_FREEZE
ADX_ALGORITHM_INITIALIZATION_ROUNDING=NOT_IN_INTERPRETATION_FREEZE
SWING_LOW_HIGH_MACHINE_DEFINITION=UNRESOLVED_CRITICAL
TRAILING_STOP_MACHINE_DEFINITION=UNRESOLVED_CRITICAL
EXIT_ON_NEW_HIGHS_MACHINE_DEFINITION=UNRESOLVED_CRITICAL
OPERATING_TIMEFRAME=UNRESOLVED_CRITICAL
TOUCH_THEN_ENTRY_SAME_BAR_SEQUENCE=UNRESOLVED
ENTRY_THEN_PROTECTIVE_STOP_SAME_BAR_SEQUENCE=UNRESOLVED
```

Source bundle identities do not currently bind exact fetched HTML/PDF byte hashes. Wave 1/2 SOURCE_ONLY raw evidence is branch-referenced rather than self-contained on main.

## Playbook Contract / Strategy identity state

The generic Playbook Contract code remains merged, but its prior acceptance status is qualified:

```text
PLAYBOOK_CONTRACT_CORE=MERGED_IMPLEMENTED
SOURCE_INTERPRETATION_MACHINE_STRUCTURAL_SEPARATION=IMPLEMENTED
PROTOCOL_COMPLETE_PRIMARY_ENFORCEMENT=NO
FIELD_LEVEL_CRITICAL_AMBIGUITY_DERIVATION=NO
PARTIALLY_OBSERVABLE_REQUIRED_INPUT_BLOCKS_MACHINE_READY=NO
UNKNOWN_PROJECT_TRANSFER_BLOCKS_MACHINE_READY=NO
ACTUAL_CODE_ENVIRONMENT_DATA_ARTIFACT_ATTESTATION=NO
```

Critical protocol mismatch: current validator requires exactly one PRIMARY interpretation across the entire contract, while frozen Protocol v1.0 requires source-faithful claim/interpretation ambiguity to be resolved at the relevant claim level before outcome testing.

## Execution / capital / ledger state after second pass

Previously merged work remains useful but is no longer treated as defect-free:

```text
TD001_SINGLE_TRADING_DAY_AUTHORITY=RESOLVED_AS_DESIGN_OWNER
TD002_PARTIAL_CLOSE_REMARK=RESOLVED_FOR_THAT_PATH
ADD_POSITION_UNREALIZED_RESET_BUG=OPEN_CONFIRMED
FORCED_LIQUIDATION_NEXT_TRADING_DAY_GAP=OPEN_CONFIRMED
FORCED_LIQUIDATION_OFFSET_FEE_GAP=OPEN_CONFIRMED
GENERIC_CLOSE_TODAY_PLUS_PREVIOUS_SPLIT=UNSUPPORTED
MULTIPRODUCT_HETEROGENEOUS_MULTIPLIER_PORTFOLIO=UNSUPPORTED
ROUND_TRIP_LEDGER=MERGED_IMPLEMENTED_WITH_NEW_IDENTITY_INPUT_GAPS
```

`RoundTripLedger.active_official_trading_days` still means official days represented by lifecycle transitions, not guaranteed complete inclusive holding-day coverage.

## Latest parallel lanes F/G/H

```text
LANE_F_BRANCH=parallel/holy-grail-playbook-contract-draft-v01
LANE_F_COMMIT=9fe53a2104e78e51f09f56c3bc73d2f6c930e536
LANE_F=NOT_MERGED / PRIMARY_FREEZE_READY_NO / SECOND_PASS_CAUSAL_GAPS_FOUND

LANE_G_BRANCH=parallel/pit-feature-timeframe-core-v01
LANE_G_COMMIT=ae16f7cd0b38aadc783bd8957c7b03a7ac123d37
LANE_G=NOT_MERGED / CORRECTIONS_REQUIRED

LANE_H_BRANCH=parallel/stop-trigger-observation-v01
LANE_H_COMMIT=8244935ed3be32394910a6fb745017b31e194b6a
LANE_H=NOT_MERGED / CORRECTIONS_REQUIRED

COMBINED_F_G_H_REGRESSION=NOT_RUN
```

The full finding inventory and propagation chains are in:
`docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md`.

## Parallel-work policy

```text
PARALLEL_EXECUTION_STRATEGY=KEEP
MAX_ACTIVE_LANES=3
MAIN=SOLE_INTEGRATION_LANE
MANDATORY_POST_PARALLEL_ADVERSARIAL_AUDIT=YES
MANDATORY_COMBINED_REGRESSION_BEFORE_MAIN=YES
TOOL_DECISION=USE_EXISTING
NEW_TOOL_REQUIRED=NO
```

The second-pass audit shows that branch-local green tests are not sufficient evidence for cross-module safety.

## Progress estimate status

The earlier planning estimate `FULL_PROJECT_ENGINEERING_PROGRESS_ESTIMATE=~63_PERCENT` is now stale because it counted several merged modules as fully accepted when the second-pass audit found material cross-binding and execution defects.

```text
PREVIOUS_63_PERCENT_ESTIMATE=WITHDRAWN_AS_STALE
NEW_PROGRESS_ESTIMATE=NOT_REISSUED_IN_FINDINGS_ONLY_AUDIT
```

This audit records correctness status only; it does not manufacture a new percentage before the findings are reclassified into accepted / repair-required / design-gap work.

## Current authorization / next action

No outcome access is authorized.

```text
CURRENT_NEXT_ACTION=SECOND_PASS_FINDINGS_RECORDED_NO_REPAIR_PROMPTS_IN_THIS_AUDIT
OWNER_ACTION=NONE
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
```

# CURRENT_STATE

## Project phase

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE_BASELINE=Skeleton_v1.0
ARCHITECTURE_STATUS=ACCEPTED
ADOPTED_CONTRACT_VERSION=3.1
CURRENT_BLOCKER=PREOUTCOME_INTEGRATION_CORRECTIONS_F_G_H
CURRENT_WORK_PACKAGE=PARALLEL_WORK_PACKAGE_2026_08_20_V0_3_POST_PARALLEL_AUDIT
CURRENT_WORK_PACKAGE_STATUS=PAUSED_FOR_CORRECTION_AND_COMBINED_REGRESSION
CURRENT_WORK_PACKAGE_AUTHORITY=docs/reviews/PARALLEL_WORK_PACKAGE_2026-08-20_V0_3_ADVERSARIAL_AUDIT.md
CURRENT_RESEARCH_POLICY=docs/research/HUMAN_PLAYBOOK_HISTORICAL_V1_EVIDENCE_POLICY_V1_0.md
SOURCE_ACQUISITION_POLICY=docs/research/HUMAN_PLAYBOOK_SOURCE_ACQUISITION_POLICY_V1_0.md
OWNER_ACTION=NONE
```

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
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
```

Frozen chronology/research semantics changes require a new protocol version, material independent review and Owner gate.

## Owner Option A / statistical acceptance

```text
OWNER_DECISION=OPTION_A_APPROVED
FROZEN_12_6_6=PRESERVED
STRONG_FWER_ACCEPTANCE_TARGET=UNCHANGED
HISTORICAL_V1_GENERAL_DOMAIN_POSITIVE_PASS=UNAVAILABLE_CURRENTLY
STATISTICAL_POSITIVE_ACCEPTANCE_PACKAGE=PARKED
CURRENT_INFERENCE_CANDIDATE=NONE_ADOPTED_FOR_POSITIVE_PASS
```

Historical v1 may legitimately end `INSUFFICIENT_EVIDENCE`; no arbitrary statistical gate is introduced to manufacture a PASS.

## Canonical data / cost boundary

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
PAYWALL_OR_DRM_BYPASS=FORBIDDEN
```

Missing inputs are recorded as not/partially observable; no invented OHLCV proxy is authorized.

## Pre-outcome firewall

```text
PREOUTCOME_FIREWALL_IMPLEMENTATION=COMPLETE_VERIFIED_ACCEPTED
SOURCE_ONLY_POLICY=VERIFIED
SOURCE_ONLY_CLAIM_EXTRACTION_RUNNER=VERIFIED
RESEARCH_WAVE_IDENTITY_BINDING=VERIFIED
PRE_OUTCOME_GATE_STATUS=VERIFIED_FAIL_CLOSED
HISTORICAL_FINAL_HOLDOUT_LOCK=ENFORCED
```

`src/research_firewall.py` remains the sole new candidate-outcome access-rule owner.

## Human Playbook research state

Accepted history:
- Grimes Wave 1: accepted with integration corrections;
- Steenbarger Wave 2: accepted with integration corrections;
- Steenbarger false-breakout semantic completion: accepted negative result / stopped as current-data candidate;
- Raschke NR7: accepted negative semantic-completion result;
- Raschke Holy Grail: accepted as source-semantically draftable.

Current family:

```text
FAMILY=RASCHKE_HOLY_GRAIL_PULLBACK
PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES
PLAYBOOK_MACHINE_READY=NO
PRIMARY_FREEZE_READY=NO
SOURCE_STOP_BOUNDARY_CONCEPT=EXPLICITLY_PINNED
SOURCE_STOP_MACHINE_OPERATIONALIZATION=PARTIALLY_PINNED
SOURCE_SUPPORTS_CURRENT_PROJECT_PRODUCTS=UNKNOWN
CURRENT_PROJECT_PRODUCT_TRANSFER=INFERRED
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

Known pre-outcome semantic gaps include:

```text
EMA_PRICE_INPUT=NOT_SOURCE_PINNED
EMA_TOUCH_CAUSAL_REFERENCE=NOT_FROZEN
NEWLY_FORMED_SWING_LOW_HIGH_MACHINE_DEFINITION=UNRESOLVED_CRITICAL
TRAILING_STOP_MACHINE_DEFINITION=UNRESOLVED_CRITICAL
EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION=UNRESOLVED_CRITICAL
OPERATING_TIMEFRAME=UNRESOLVED_CRITICAL
PROTECTIVE_STOP_SAME_BAR_CHRONOLOGY=NOT_FROZEN
CURRENT_PROJECT_PRODUCT_TRANSFER=INFERRED
```

Lane F branch `parallel/holy-grail-playbook-contract-draft-v01` / commit `9fe53a2104e78e51f09f56c3bc73d2f6c930e536` is NOT merged. Its honest `PRIMARY_FREEZE_READY=NO` result is directionally accepted, but its interpretation-freeze artifact requires causal correction before becoming authority: same-bar EMA-touch timing must not use a current-bar close-derived EMA, and same-bar post-fill protective-stop risk must not be silently discarded.

## Accepted engineering state on main

### Playbook Contract core

```text
PLAYBOOK_CONTRACT_CORE=MERGED_ACCEPTED
SOURCE_INTERPRETATION_MACHINE_SEPARATION=ENFORCED
AMBIGUITY_FAIL_CLOSED=YES
OBSERVABILITY_FAIL_CLOSED=YES
ZERO_PARAMETER_STRATEGY_SUPPORT=YES
ZERO_REQUIRED_FEATURE_VERSION_SUPPORT=YES
RESEARCH_FIREWALL_REMAINS_SOLE_ACCESS_OWNER=YES
```

### Execution evidence TD-001 / TD-002

```text
TD001=RESOLVED
SESSION_METADATA_SINGLE_TRADING_DAY_AUTHORITY=YES
TD002=RESOLVED
PARTIAL_CLOSE_REMAINING_POSITION_REMARKED_AT_CLOSE_FILL=YES
```

### Completed round-trip ledger

```text
ROUND_TRIP_LEDGER=MERGED_ACCEPTED
ONE_POSITION_ID_ONE_COMPLETED_ROUND_TRIP=YES
ADDS_AND_PARTIAL_CLOSES_DO_NOT_INFLATE_N=YES
FORCED_LIQUIDATION_TERMINAL=YES
GROSS_REALIZED_PNL_AUTHORITY=CapitalTransition.realized_pnl_change
ADDITIVE_COST_AUTHORITY=CapitalTransition.required_cost
TRADING_DAY_WEEK_AUTHORITY=SessionMetadata
```

`active_official_trading_days` means official days represented by supplied lifecycle transitions, not guaranteed full inclusive holding-day coverage.

## Post-parallel adversarial audit of F/G/H

Authority:
`docs/reviews/PARALLEL_WORK_PACKAGE_2026-08-20_V0_3_ADVERSARIAL_AUDIT.md`

```text
PARALLEL_EXECUTION_STRATEGY=KEEP
MAX_ACTIVE_LANES=3
MANDATORY_POST_PARALLEL_ADVERSARIAL_AUDIT=YES
MANDATORY_COMBINED_REGRESSION_BEFORE_MAIN=YES
LANE_F=REVISION_REQUIRED_BEFORE_FREEZE_AUTHORITY
LANE_G=INTEGRATION_BLOCKED_CORRECTIONS_REQUIRED
LANE_H=INTEGRATION_BLOCKED_CORRECTIONS_REQUIRED
COMBINED_F_G_H_REGRESSION=NOT_YET_RUN
```

### Lane G corrections required

Worker:
`parallel/pit-feature-timeframe-core-v01` / `ae16f7cd0b38aadc783bd8957c7b03a7ac123d37`.

Blocking findings:
- daily aggregation can emit a complete daily bar without proving all expected minute constituents exist;
- completely absent session windows can disappear from intraday completeness evidence;
- unsupported/non-integral timeframe-to-base relationships and constituent duration are not fully guarded;
- EMA/ADX feature identity does not bind the full historical dependency chain;
- feature computation can be called on only the complete aggregates while silently ignoring reported incomplete buckets.

Lane G is not merged.

### Lane H corrections required

Worker:
`parallel/stop-trigger-observation-v01` / `8244935ed3be32394910a6fb745017b31e194b6a`.

Blocking findings:
- `evaluate_stop_group()` can consume a one-shot `bars` generator on the first order, leaving later orders with no bars;
- trigger-result identities do not bind exact source-bar/evaluated-sequence provenance strongly enough.

Integration limitation:
- same-bar OCO ambiguity is detected, but full OCO cancellation after an earlier unambiguous trigger is deliberately not implemented and must not be represented as complete bracket lifecycle execution.

Lane H is not merged.

## Progress estimate

Planning estimate, not acceptance evidence:

```text
FULL_PROJECT_ENGINEERING_PROGRESS_ESTIMATE=~63_PERCENT
PRE_OUTCOME_RESEARCH_AND_VALIDATION_FOUNDATION=~75_PERCENT
RAW_IMPLEMENTATION_IF_UNACCEPTED_F_G_H_COUNTED=~66_PERCENT
```

Only accepted-main capabilities count toward the ~63% full-project figure. Unaccepted branches with known correctness defects are not counted as completed engineering.

The remaining full-project gap is dominated by:
- no frozen machine-ready real Playbook / StrategyIdentity yet;
- PIT feature/timeframe layer not yet accepted;
- stop-trigger layer not yet accepted;
- live `TradingState`, RiskGate, OMS, broker adapter, reconciliation, safety/kill-switch and durable live control path remain largely unimplemented;
- owner-facing observability/control remains incomplete;
- candidate DEVELOPMENT outcome research has not started and remains locked.

## Tool / execution policy

```text
TOOL_DECISION=USE_EXISTING
NEW_TOOL_REQUIRED=NO
PARALLEL_EXECUTION=ENABLED_AFTER_CORRECTIONS
MAIN=SOLE_INTEGRATION_LANE
```

Parallel independent construction remains preferred. The optimization after this audit is mandatory cross-lane adversarial review plus one combined integration regression before main acceptance.

## Current authorization / next action

AUTHORIZED NOW:
- correct Lane G generic PIT aggregation/feature provenance defects using synthetic data;
- correct Lane H iterable/provenance defects using synthetic data;
- revise Lane F causal interpretation without outcome access;
- run a combined corrected F+G+H isolated integration regression.

NOT AUTHORIZED:
- candidate DEVELOPMENT outcome backtest;
- candidate PnL/returns/win-rate/Sharpe/equity/drawdown inspection;
- Validation/final holdout access;
- paid data/source commitments;
- real-money/broker actions.

```text
CURRENT_NEXT_ACTION=CORRECT_F_G_H_THEN_RUN_ONE_COMBINED_INTEGRATION_REGRESSION
OWNER_ACTION=NONE
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
```

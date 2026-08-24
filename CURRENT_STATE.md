# CURRENT_STATE

> Mutable project-state authority. Current GitHub `main` is the only dynamic project fact source.

## Current phase

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
CURRENT_ADOPTED_ARCHITECTURE=Skeleton_v1.0_PLUS_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1
ARCHITECTURE_STATUS=ACCEPTED
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
RESEARCH_DIRECTION_STATUS=OWNER_APPROVED
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
CURRENT_WORK_PACKAGE=STAGE_A_V0_3_CAPABILITY_FIRST_MODEL_COMPARISON__DESIGN_AND_MINIMAL_IMPLEMENTATION
NEXT_NORMAL_PHASE=V0_3_OFFLINE_CLOSURE__THEN_DEEPSEEK_FIRST_MATCHED_CAPABILITY_CALL
OWNER_ACTION=NONE_UNTIL_V0_3_OFFLINE_READY
TOOL_DECISION=USE_EXISTING
```

Current Stage-A research-design authority:
`docs/reviews/JIANGHE_STAGE_A_V0_3_CAPABILITY_FIRST_OWNER_DECISION.md`.

Current non-executable comparison plan:
`docs/evidence/JIANGHE_STAGE_A_CAPABILITY_COMPARISON_PLAN_V0_3.json`.

## Owner selection objective

```text
SELECTION_PRIORITY_1=JIANGHE_CORRECTNESS_AND_CAPABILITY
SELECTION_PRIORITY_2=ACTUAL_CNY_COST
SELECTION_PRIORITY_3=ACTUAL_TIME_LATENCY
FAIRNESS_PRINCIPLE=SAME_MATERIAL__SAME_QUESTION__DIFFERENT_MODEL_BRAIN
```

Formatting convenience, strict JSON compliance, reasoning-token count, or a uniform completion ceiling are not Jianghe capability substitutes.

## Current paid-call state

```text
PAID_CALLS_CURRENTLY_PAUSED=YES__V0_3_OFFLINE_CLOSURE_NOT_COMPLETE
NEXT_EXPLICIT_PAID_SLOT=NONE
FUTURE_FIRST_V0_3_PROVIDER=DEEPSEEK
FUTURE_FIRST_V0_3_SLOT=NEW_IDENTITY_REQUIRED
OLD_NEXT_KIMI_1=SUPERSEDED__NOT_EXECUTED
OLD_V0_2_LIVE_WORKFLOW=RETIRED__FAIL_CLOSED_BEFORE_CREDENTIALS
AUTOMATIC_RETRY=FORBIDDEN
AUTOMATIC_NEXT_SLOT=FORBIDDEN
```

No V0.3 provider call is authorized for execution merely because the Owner approved the V0.3 research design. The offline request/evidence/adapter path and new V0.3 slot identity must close first.

## Immutable historical live state

V0.1/V0.2 history remains evidence and accounting authority for calls already made:

```text
HISTORICAL_LIVE_CALLS=2
HISTORICAL_STAGE_A_ACCOUNTED_CNY=0.270021
HISTORICAL_DEEPSEEK_ACCOUNTED_CNY=0.219222
HISTORICAL_MINIMAX_ACCOUNTED_CNY=0.050799
HISTORICAL_KIMI_ACCOUNTED_CNY=0
V0_2_PLAN_IDENTITY=9736e1cf75372ec13f524a971ee1d1c036a1d5e6ac51b250a6890a9ecf76d913
V0_2_REMOTE_REF=refs/heads/stage-a-live-state-v0-2
V0_2_REMOTE_HEAD_AFTER_ATTEMPT_002=ea1364e04e378781d8cf9f1b43a9ce3f0ef1679e
```

### Attempt 001 — DeepSeek V0.1

Authority: `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_001_DEEPSEEK_ADJUDICATION_V0_1.md`.

```text
PROVIDER=DEEPSEEK
MODEL=deepseek-v4-flash-vision-exp
OLD_SLOT=1
ACCOUNTED_CNY=0.219222
EVIDENCE_IDENTITY=d36c1fbbb1cd639e48a6f049f7df1be3bb95d9f346d75bbb85e25451fba9dc55
OLD_SLOT_STATUS=ATTEMPTED__NON_RETRYABLE__NO_REPLACEMENT_CALL
V0_1_PROVIDER_RESPONSE_CONTRACT_DEFECT=YES
DEEPSEEK_CAPABILITY_FATAL_FROM_ATTEMPT_001=NO
```

The request reached a 2xx provider JSON response, but the V0.1 evidence contract did not retain enough safe response-envelope facts to score the final response. A future V0.3 DeepSeek call uses a new identity; old `DEEPSEEK:1` is never rerun.

### Attempt 002 — MiniMax V0.2

Authority: `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_002_MINIMAX_ADJUDICATION_V0_1.md`.

```text
PROVIDER=MINIMAX
MODEL=MiniMax-M3
OLD_SLOT=1
HTTP_STATUS_CLASS=2xx
RESOLVED_MODEL=MiniMax-M3
FINISH_REASON=length
FINAL_CONTENT_STATE=TEXT_NONEMPTY
PROMPT_TOKENS=7999
COMPLETION_TOKENS=1024
REASONING_TOKEN_COUNT=914
LATENCY_MS=10364
ACCOUNTED_CNY=0.050799
TERMINAL_STATUS=NON_SCOREABLE_NORMALIZER
OLD_SLOT_STATUS=ATTEMPTED__NON_RETRYABLE
MINIMAX_V0_2_OPERATIONAL_FATAL_STOP=HISTORICAL_TRUE
MINIMAX_V0_3_JIANGHE_CAPABILITY_FAIL=NO_EVIDENCE
```

The V0.2 frozen funnel's elimination remains immutable historical experiment semantics. Under the Owner-approved V0.3 correction, truncation/normalizer failure does not establish Jianghe capability failure.

## Current capability candidates

```text
DEEPSEEK_CAPABILITY_STATUS=CANDIDATE__FAIR_V0_3_EVALUATION_REQUIRED
MINIMAX_CAPABILITY_STATUS=CANDIDATE__FAIR_V0_3_EVALUATION_REQUIRED
KIMI_CAPABILITY_STATUS=CANDIDATE__FAIR_V0_3_EVALUATION_REQUIRED
VERIFIED_PROVIDER=NONE
ADOPTED_PROVIDER=NONE
FAIR_MATCHED_THREE_MODEL_EVIDENCE=NONE_YET
```

The first future paid V0.3 provider is DeepSeek. Then obtain matched MiniMax and Kimi answers using the same governed fixture/material. This ordering does not give DeepSeek different information.

## V0.3 capability contract

```text
NON_SCOREABLE_NORMALIZER_IS_CAPABILITY_FATAL=NO
UNIFORM_1024_CAPABILITY_GATE=RETIRED
PRODUCTION_JSON_REQUIRED_FOR_CAPABILITY_SCORE=NO
PROVIDER_SPECIFIC_SUFFICIENT_COMPLETION_HEADROOM=REQUIRED
PROVIDER_NATIVE_RECOMMENDED_REASONING=ALLOWED
RAW_FINAL_ANSWER_EVIDENCE=REQUIRED__SECRET_SAFE__NO_CHAIN_OF_THOUGHT
NORMALIZED_EVALUATION_VIEW=REQUIRED__IDENTITY_BOUND
NORMALIZATION_ADAPTER=FORMAT_ONLY__NO_SEMANTIC_REPAIR
```

Matched comparison keeps the same Jianghe material, context-selection principle, question, visual bytes, structured observation, visible history, outcome/future ban, no-tools/search rule, and trading-decision task. Only provider-required wire syntax and provider-native reasoning configuration may differ.

Capability scoring covers Jianghe principle accuracy, market structure, visual reading, WAIT/NO_TRADE discipline, no invented rules/thresholds, uncertainty honesty, visual/structured consistency, hard negatives, stability, and source-supported conclusions. Actual CNY and actual latency are compared after answer quality.

## Authorization and budget

```text
OWNER_PAID_CALL_DECISION=AUTHORIZED_FOR_BOUND_PROJECT_FIDELITY_RESEARCH__EXECUTION_PAUSED_BY_V0_3_OFFLINE_GATE
PAID_CALL_AUTHORIZATION_ID=OWNER-PAID-JIANGHE-FIDELITY-20260824-V01
PAID_CALL_AUTHORIZATION_EXPIRES=2026-08-31T00:00:00+08:00
TOTAL_API_SPEND_HARD_CAP_CNY=100.00
CURRENT_PROJECT_ACCOUNTED_CNY=0.270021
V0_3_STAGE_A_CNY18_CAP=NOT_APPLICABLE__HISTORICAL_V0_1_V0_2_DESIGN_ONLY
V0_3_CNY6_PER_PROVIDER_CAP=NOT_APPLICABLE__HISTORICAL_V0_1_V0_2_DESIGN_ONLY
V0_3_FIXED_5_CALLS_PER_PROVIDER=NOT_APPLICABLE__HISTORICAL_V0_1_V0_2_DESIGN_ONLY
AUTOMATIC_RECHARGE=FORBIDDEN
NEW_RECHARGE_REQUIRED=NO
```

Cost/time/token use are measurements, not capability gates. CNY100 remains the project-wide API hard ceiling. Any recharge is a separate Owner cash action.

## Pre-live research / knowledge state

```text
PRE_SPEND_REPAIR_REAUDIT=PASS
BSP_001_TO_005=CLOSED
RSP_001_TO_002=CLOSED
LIMIT_015=RESOLVED
LIMIT_012=ACTIVE__V0_3_CAPABILITY_FIRST_OFFLINE_CLOSURE__NO_FAIR_MATCHED_MODEL_EVIDENCE_YET
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
JIANGHE_PRIMARY_CLAIM_MANIFEST_IDENTITY=f767253dc4c2d1b17f57b9adfdc903907a97df8d4697dbe0fae0f603427dbf36
```

## Locks

```text
OUTCOME_ACCESS=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

## Exact next work

1. Complete only the minimal V0.3 offline implementation: provider-specific sufficient completion headroom; safe raw-final preservation; format-only normalization; separate operational versus capability status; new V0.3 request/slot/ledger identity; deterministic CNY100 guard.
2. Recheck all three current first-party provider contracts while freezing those exact configurations.
3. Run zero-network/focused tests and canonical suite; do not use provider credentials during closure.
4. After project-brain offline closure, create exactly one explicit new V0.3 DeepSeek capability slot and execute it once.
5. After evidence review, obtain matched MiniMax and Kimi answers on the same governed material; compare correctness/Jianghe fidelity, actual CNY, and actual time.

Do not reopen a whole-repository rolling audit.
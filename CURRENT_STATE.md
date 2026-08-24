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
CURRENT_WORK_PACKAGE=STAGE_A_V0_1_PROVIDER_RESPONSE_CONTRACT_ADJUDICATION
NEXT_NORMAL_PHASE=OWNER_DECISION_ON_EXPLICIT_STAGE_A_V0_2_PROVIDER_RESPONSE_COMPATIBILITY_CORRECTION
OWNER_ACTION=DECIDE_STAGE_A_V0_2_PROVIDER_RESPONSE_COMPATIBILITY_CORRECTION
TOOL_DECISION=USE_EXISTING
```

## Current material checkpoint

```text
LAST_MATERIAL_STATE_COMMIT=72f96d200f8ed8d3f6da042597344f828b54ae25
PR_26_MERGE_COMMIT=a6f8cc99641a37c628264cb57b30a75c4537aa4a
PR_29_MERGE_COMMIT=72f96d200f8ed8d3f6da042597344f828b54ae25
PR_30_STATE_SYNC_MERGE_COMMIT=07cb7f01ae69365943cb4be6b30b711635c2b1e5
STAGE_A_FROZEN_PLAN_IDENTITY=7d6a1838962345c36dd3449f27adfd6c7d18c4988b5e3e2cb4bc65acb52b2fd4
STAGE_A_FROZEN_STIMULUS=36x5m__12x15m__3x1H__JH-FIX-C-001
STAGE_A_SINGLE_SLOT_RUNNER=INTEGRATED
STAGE_A_EVIDENCE_EXPORTER=INTEGRATED__SECRET_FAIL_CLOSED__BSP_003_PRESERVED
STAGE_A_LIVE_LANE=INTEGRATED__PROJECT_BRAIN_ACCEPTED
STAGE_A_REMOTE_LEDGER=INTEGRATED
STAGE_A_REMOTE_CAS=INTEGRATED
STAGE_A_REMOTE_REREAD_VERIFICATION=INTEGRATED
STAGE_A_CRASH_ACCOUNTING=INTEGRATED
STAGE_A_SINGLE_SLOT_LIVE_WORKFLOW=INTEGRATED
STAGE_A_FIXED_REMOTE_REF=refs/heads/stage-a-live-state-v0-1
REMOTE_STATE_BOOTSTRAP=COMPLETE__EMPTY_STATE_CREATED_ONCE_AND_REREAD_VERIFIED
REMOTE_STATE_BOOTSTRAP_HEAD=bc39535a03484a6830d2e9d03b1a7ddd537edc9f
```

Frozen plan authority: `docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_1.json`.
Live-lane closure: `docs/reviews/JIANGHE_STAGE_A_LIVE_LANE_INTEGRATION_CLOSURE_V0_1.md`.

## First real Stage-A attempt

Authority: `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_001_DEEPSEEK_ADJUDICATION_V0_1.md`.

```text
STAGE_A_STATUS=STARTED__ATTEMPT_001_RECORDED__PAUSED_FOR_PROTOCOL_ADJUDICATION
LIVE_CALLS=1
PAID_SPEND_CNY=0.219222
PAID_SPEND_SEMANTICS=CONSERVATIVE_STAGE_A_ACCOUNTING__NOT_PROVIDER_ACTUAL_BILLING
PROVIDER_ACTUAL_BILLED_CNY=UNKNOWN
ATTEMPT_001_WORKFLOW_RUN_ID=32709432759
ATTEMPT_001_EXECUTION_MAIN_SHA=07cb7f01ae69365943cb4be6b30b711635c2b1e5
ATTEMPT_001_PROVIDER=DEEPSEEK
ATTEMPT_001_MODEL=deepseek-v4-flash-vision-exp
ATTEMPT_001_SLOT=1
ATTEMPT_001_TRACK=OPERATIONAL_PROVIDER
ATTEMPT_001_REMOTE_START_HEAD=eb184e0baaca6fad435c08a7ae045a4c118dfb8d
ATTEMPT_001_REMOTE_TERMINAL_HEAD=daa5eae090ab60f340e6502e02719fb3bba015d0
ATTEMPT_001_EVIDENCE_IDENTITY=d36c1fbbb1cd639e48a6f049f7df1be3bb95d9f346d75bbb85e25451fba9dc55
ATTEMPT_001_TERMINAL_STATUS=TRANSPORT_FAILURE
ATTEMPT_001_ERROR_TYPE=ProviderResponseError
ATTEMPT_001_ERROR_MESSAGE=provider_response_content_is_not_text
ATTEMPT_001_AUTOMATIC_RETRY=FORBIDDEN
DEEPSEEK_SLOT_1=ATTEMPTED__NON_RETRYABLE
SECOND_LIVE_SLOT_AFTER_ATTEMPT_001=NOT_RUN
```

The durable ledger proves both `NETWORK_ATTEMPT_STARTED` and `ATTEMPT_TERMINAL`. The provider request reached a 2xx JSON response before final-content extraction failed. The surviving safe evidence does not preserve resolved model, provider request id, usage, finish reason or the exact null/empty/non-string content state, so those facts remain `UNKNOWN` and must not be guessed.

## Attempt-001 provider-contract adjudication

```text
DEEPSEEK_MODEL_ID=deepseek-v4-flash-vision-exp__CURRENT_FIRST_PARTY_MODEL
DEEPSEEK_ENDPOINT=https://api.deepseek.com/chat/completions__CURRENT_FIRST_PARTY_ROUTE
DEEPSEEK_PROVIDER_FATAL_FAIL=NOT_YET_ADJUDICATED
V0_1_PROVIDER_RESPONSE_CONTRACT_DEFECT=OPEN
FURTHER_PAID_STAGE_A_CALLS=PAUSED_PENDING_OWNER_RESEARCH_DESIGN_DECISION
```

Bounded post-attempt audit findings:
- current DeepSeek JSON Output guidance requires JSON guidance plus an example shape, recommends sufficient `max_tokens`, and explicitly warns that JSON Output may occasionally return empty `content`;
- DeepSeek thinking defaults to enabled and returns reasoning separately from final `content`;
- frozen V0.1 DeepSeek uses `response_format=json_object`, `max_tokens=400`, and leaves thinking/effort at provider defaults while the shared prompt has no concrete JSON-output example;
- Kimi Open Platform's current visual Chat Completions and `json_schema` Structured Output surface remain valid; K3 is a current visual reasoning model, but its reasoning/output-budget configuration must remain governed rather than tuned ad hoc;
- MiniMax OpenAI-compatible reasoning output has a documented split-reasoning format; leaving thinking inline creates a foreseeable incompatibility with the project's strict JSON normalizer.

Because the Owner-approved Stage-A V0.1 protocol froze prompt/context/schema/inference-configuration identities before the first paid call and forbids silent post-response provider-specific prompt improvement, these issues cannot be silently patched under the same V0.1 research identity.

Project-brain recommendation:

```text
RECOMMENDATION=EXPLICIT_STAGE_A_V0_2_PROVIDER_RESPONSE_COMPATIBILITY_CORRECTION
V0_1_ATTEMPT_001_HISTORY=PRESERVE__NO_RETRY__ACCOUNTED_CNY_0_219222
V0_2_SCOPE=OUTPUT_CONTRACT__THINKING_SEPARATION__SAFE_2XX_RESPONSE_EVIDENCE__OUTPUT_TOKEN_BUDGET__REFREEZE_FUTURE_UNATTEMPTED_CALLS
FIXTURE_CHANGE=NO
OHLC_STIMULUS_CHANGE=NO
JIANGHE_SEMANTICS_CHANGE=NO
OUTCOME_ACCESS_CHANGE=NO
BUDGET_CAP_CHANGE=NO
```

This is a new research-design version and therefore requires explicit Owner approval before implementation or any further paid Stage-A call.

## Pre-live / pre-spend closure state

```text
PRE_LIVE_FIDELITY_GATE_REAUDIT=PASS
PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT=PASS
SOURCE_ONLY_REPOSITORY_BYTE_AUTHORITY=EXACT_COMMITTED_GIT_BLOB_BYTES
PRE_SPEND_REPAIR_REAUDIT=PASS
BSP-001=CLOSED
BSP-002=CLOSED
BSP-003=CLOSED
BSP-004=CLOSED
BSP-005=CLOSED
RSP-001=CLOSED
RSP-002=CLOSED
LIMIT_015=RESOLVED
LIMIT_012=ACTIVE__REAL_MODEL_JIANGHE_FIDELITY_IN_PROGRESS__NO_SCOREABLE_MODEL_EVIDENCE_YET
```

## Owner paid-call authorization

```text
OWNER_PAID_CALL_DECISION=AUTHORIZED
PAID_CALL_AUTHORIZATION_ID=OWNER-PAID-JIANGHE-FIDELITY-20260824-V01
PAID_CALL_AUTHORIZATION_EXPIRES=2026-08-31T00:00:00+08:00
AUTHORIZED_PROVIDER_MODELS=KIMI:kimi-k3,DEEPSEEK:deepseek-v4-flash-vision-exp,MINIMAX:MiniMax-M3
AUTHORIZED_API_SPEND_HARD_CAP_CNY=100.00
AUTHORIZED_EXECUTION_ORDER=STAGE_A_FIRST
STAGE_A_MAX_SPEND_CNY=18.00
STAGE_A_MAX_CALLS=15
MAX_STAGE_A_CALLS_PER_PROVIDER=5
MAX_STAGE_A_SPEND_PER_PROVIDER_CNY=6.00
AUTOMATIC_SEMANTIC_RETRY=FORBIDDEN
AUTOMATIC_BUDGET_EXTENSION=FORBIDDEN
NEW_RECHARGE_OR_TOPUP=NOT_AUTHORIZED_WITHOUT_SPECIFIC_AMOUNT_OWNER_CONFIRMATION
SPEND_GATE=PAUSED_FOR_PROTOCOL_ADJUDICATION__AUTHORIZATION_ITSELF_REMAINS_VALID
```

Existing funded balances may be consumed only through the authorized funnel after the current protocol decision. No new recharge is required for current Stage-A balances.

## Stage-A input protocol

Authority: `docs/reviews/JIANGHE_STAGE_A_INPUT_AND_VISUAL_STIMULUS_PROTOCOL_OWNER_DECISION_V0_1.md`.

```text
STAGE_A_INPUT_PROTOCOL=OWNER_APPROVED__V0_1_FROZEN
QUALIFICATION_FIXTURE=JH-FIX-C-001
TRACK_ISOLATION=YES
SYNTHETIC_OHLC_FROM_VISIBLE_INFORMATION_ONLY=YES
SAME_UNDERLYING_OBSERVATION_FOR_VISUAL_STRUCTURED_DUAL=YES
V0_1_MAX_OUTPUT_TOKENS_PER_CALL=400
V0_1_FUTURE_CALLS=PAUSED_PENDING_V0_2_DECISION
```

Frozen V0.1 tracks remain `OPERATIONAL_PROVIDER`, `SEMANTIC`, `VISUAL`, `STRUCTURED`, and `DUAL_INPUT`. Attempt 001 does not authorize any change to fixture semantics, bars, scoring, outcome access or provider ranking.

## Provider / pricing state

```text
KIMI_K3=CANDIDATE__NOT_VERIFIED__NOT_ADOPTED
DEEPSEEK_V4_FLASH_VISION_EXP=CANDIDATE__EXPERIMENTAL__ATTEMPT_001_UNSCOREABLE__NOT_VERIFIED__NOT_ADOPTED
MINIMAX_M3=CANDIDATE__NOT_VERIFIED__NOT_ADOPTED
FINAL_APPROVED_PROVIDER_SET=NOT_DECIDED
```

Pricing authorities remain:
- `docs/evidence/JIANGHE_PROVIDER_PRICING_AUTHORITY_V0_1.json`
- `docs/reviews/PROVIDER_PRICING_FALLBACK_POLICY_V0_1.md`
- `docs/reviews/DOMESTIC_PROVIDER_PRICING_REFRESH_V0_1.md`
- `docs/reviews/DEEPSEEK_V4_FLASH_VISION_EXP_FIRST_PARTY_CORRECTION_V0_1.md`

Frozen V0.1 five-slot worst-case ceilings were:

```text
KIMI=5.57772_CNY
DEEPSEEK=0.775968_CNY
MINIMAX=1.0885308_CNY
```

Any V0.2 output-token/configuration correction must recompute and re-freeze future-call ceilings before another provider network request; it may not expand the existing CNY6/provider, CNY18 Stage-A or CNY100 total caps.

## Credential / funding state

```text
GITHUB_ENVIRONMENT=stage-a-readiness__MAIN_RESTRICTED
MOONSHOT_API_KEY=CONFIGURED__VALUE_NOT_READ
DEEPSEEK_API_KEY=CONFIGURED__VALUE_NOT_READ
MINIMAX_API_KEY=CONFIGURED__VALUE_NOT_READ
CREDENTIAL_VALUE_EXPOSURE=NONE
EXISTING_PROVIDER_BALANCE_EVIDENCE_CLASS=OWNER_CONFIRMED__NOT_MACHINE_VERIFIED_ALL_THREE
OWNER_REPORTED_WALLET_BALANCES_CNY=KIMI:10,DEEPSEEK:10,MINIMAX:10
NEW_RECHARGE_REQUIRED=NO
```

## RMB100 funnel

Authority: `docs/reviews/JIANGHE_RMB100_REAL_MODEL_FIDELITY_FUNNEL_V0_1.md`.

```text
STAGE_A_MAX=18_CNY__15_CALLS
TOP1_STABILITY_MAX=42_CNY__12_CALLS
TOP2_COMPARISON_MAX=28_CNY__8_CALLS
TIE_RESERVE_MAX=12_CNY__4_CALLS
TOTAL_API_SPEND_CAP=100_CNY
MAX_TOTAL_CALLS=39
UNUSED_BUDGET=REMAINS_UNSPENT
NO_AUTO_EXTENSION=YES
```

No Stage-B call is permitted until Stage-A evidence and ranking are committed.

## Jianghe knowledge / product locks

```text
KNOWLEDGE_PACK_VERSION=JIANGHE_V1_1
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
JIANGHE_PRIMARY_CLAIM_MANIFEST_IDENTITY=f767253dc4c2d1b17f57b9adfdc903907a97df8d4697dbe0fae0f603427dbf36
JIANGHE_PRIMARY_CLAIM_MANIFEST_RECORDS=352
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
OUTCOME_ACCESS=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

## Exact next work

1. Obtain Owner decision on explicit Stage-A V0.2 provider-response compatibility correction.
2. If approved, keep Attempt 001 immutable and non-retryable; do not erase its CNY0.219222 conservative accounting.
3. Build one bounded V0.2 correction across all three provider contracts before another paid call: common output contract, governed thinking/final-answer separation, adequate common output budget, and safe 2xx mechanical response evidence even when final content is unusable.
4. Recompute/re-freeze all affected future unattempted payload/inference/budget identities; do not change fixture, OHLC stimulus, Jianghe semantics, scoring, outcome locks or hard budget caps.
5. Run focused adversarial + canonical Linux suite; then project-brain closure review.
6. Only then resume with one explicit unattempted Stage-A slot; no automatic next slot.

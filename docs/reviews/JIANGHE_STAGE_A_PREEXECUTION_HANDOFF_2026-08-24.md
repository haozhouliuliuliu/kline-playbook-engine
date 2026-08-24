# JIANGHE STAGE-A PRE-EXECUTION HANDOFF — 2026-08-24

> Status: `CURRENT_PREEXECUTION_CHECKPOINT`
> Canonical authority remains current GitHub `main`. This file is the compact execution handoff immediately before credential/existing-balance readiness and the first paid Stage-A call.

## 1. Current material checkpoint

```text
LAST_MATERIAL_STATE_COMMIT=744c79dab19d8ac5ddb4e941dcd24bee4fa82895
OWNER_PAID_CALL_DECISION=AUTHORIZED
PAID_CALL_AUTHORIZATION_ID=OWNER-PAID-JIANGHE-FIDELITY-20260824-V01
PAID_CALL_AUTHORIZATION_EXPIRES=2026-08-31T00:00:00+08:00
AUTHORIZED_PROVIDER_MODELS=KIMI:kimi-k3,DEEPSEEK:deepseek-v4-flash-vision-exp,MINIMAX:MiniMax-M3
TOTAL_HARD_API_SPEND_CAP_CNY=100.00
STAGE_A_MAX_SPEND_CNY=18.00
STAGE_A_MAX_CALLS=15
MAX_STAGE_A_CALLS_PER_PROVIDER=5
MAX_STAGE_A_SPEND_PER_PROVIDER_CNY=6.00
NEW_RECHARGE_OR_TOPUP=NOT_AUTHORIZED_WITHOUT_SPECIFIC_AMOUNT_OWNER_CONFIRMATION
LIVE_CALLS=0
PAID_SPEND_CNY=0
OUTCOME_ACCESS=NO
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

No provider/model is project `VERIFIED` or `ADOPTED` yet. `LIMIT-012` remains active until real-model Jianghe fidelity evidence exists.

## 2. Owner-approved Stage-A protocol is implemented and frozen

Binding design authority:

- `docs/reviews/JIANGHE_STAGE_A_INPUT_AND_VISUAL_STIMULUS_PROTOCOL_OWNER_DECISION_V0_1.md`

Frozen machine plan:

- `docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_1.json`
- `plan_identity=7d6a1838962345c36dd3449f27adfd6c7d18c4988b5e3e2cb4bc65acb52b2fd4`

Frozen design:

```text
QUALIFICATION_FIXTURE=JH-FIX-C-001
TRACK_ISOLATION=YES
SYNTHETIC_OHLC_FROM_VISIBLE_INFORMATION_ONLY=YES
SYNTHETIC_OHLC=FROZEN__36x5m__12x15m__3x1H
SAME_UNDERLYING_OBSERVATION_FOR_VISUAL_STRUCTURED_DUAL=YES
FREEZE_ALL_STIMULUS_IDENTITIES_BEFORE_FIRST_PAID_CALL=YES
```

Tracks:

```text
OPERATIONAL_PROVIDER = minimum governed smoke request for exact model/API/schema/usage/evidence verification
SEMANTIC = fixture visible-information text only; no image; no structured market artifact
VISUAL = deterministic K-line image only; no answer-bearing fixture prose; no structured artifact
STRUCTURED = governed structured observation only; no image; no answer-bearing fixture prose
DUAL_INPUT = same-observation deterministic image + governed structured observation
```

All three providers receive semantically identical governed content for a given track; provider-specific syntax differs only where their API contracts require it.

The frozen synthetic stimulus uses normalized prices around 100 and contains no real/canonical candidate market data, hidden future, PnL/outcome/result labels or answer-revealing chart labels. Visual, structured and dual tracks bind one identical underlying observation.

## 3. Persistent single-slot execution boundary is integrated

Current implementation:

- `src/jianghe_stage_a_runner.py`
- `tools/run_jianghe_stage_a_slot.py`

Operational guarantees:

```text
ONE_PROCESS=ONE_FROZEN_PROVIDER_SLOT
FROZEN_PLAN_BYTE_REBUILD_CHECK=REQUIRED_BEFORE_CREDENTIAL_LOOKUP
REQUEST_IDENTITY_PAYLOAD_STIMULUS_RATE_CARD_BOUNDS=EXACT_FROZEN_SLOT_MATCH_REQUIRED
PERSISTENT_JOURNAL=HASH_CHAINED_JSONL
NETWORK_ATTEMPT_STARTED=FSYNC_BEFORE_TRANSPORT_INVOCATION
AUTOMATIC_RETRY_AFTER_NETWORK_START=FORBIDDEN
STARTED_SLOT=PERMANENTLY_NON_RETRYABLE_AUTOMATICALLY
CRASH_OR_INCOMPLETE_ATTEMPT=FULL_FROZEN_WORST_CASE_ACCOUNTING_ON_RESTART
PERSISTED_CAPS=CNY100_PROJECT__CNY18_STAGE_A__CNY6_PROVIDER__15_TOTAL_CALLS__5_PROVIDER_CALLS
STALE_EXECUTION_LOCK=FAIL_CLOSED__MANUAL_INSPECTION_REQUIRED
PROVIDER_RESOLVED_MODEL_DRIFT=TERMINAL_NON_SCOREABLE__FULL_WORST_CASE_ACCOUNTED
NORMALIZER_FAILURE=NON_SCOREABLE__NO_RETRY
CREDENTIAL_SERIALIZATION=FORBIDDEN
RUNTIME_STATE=.runtime/jianghe_stage_a__GIT_IGNORED
```

No second evaluation stack was introduced.

## 4. Non-billable provider readiness boundary is integrated

Current implementation:

- `src/jianghe_provider_readiness.py`
- `tools/check_jianghe_provider_readiness.py`

Behavior:

```text
FROZEN_PLAN_REBUILD_AND_BYTE_VERIFY=BEFORE_READINESS_CHECK
MISSING_CREDENTIAL=ZERO_NETWORK
KIMI=OFFICIAL_GET_/v1/users/me/balance_ONLY
DEEPSEEK=OFFICIAL_GET_/user/balance_ONLY
MINIMAX_PAYGO=NO_VERIFIED_READ_ONLY_BALANCE_API__UNKNOWN_WITH_ZERO_NETWORK
BALANCE_REQUEST_RETRY=FORBIDDEN
MODEL_ENDPOINT_AS_BALANCE_PROBE=FORBIDDEN
DEEPSEEK_NON_CNY_ONLY=UNKNOWN__NO_FX_GUESS
CREDENTIAL_VALUE_SERIALIZATION_OR_OUTPUT=FORBIDDEN
INSUFFICIENT_CNY_BALANCE=REPORT_EXACT_FROZEN_STAGE_A_SHORTFALL_ONLY
RECHARGE_OR_FUNDING_ACTION=NONE
```

The checker is deliberately separate from the model transport. It cannot convert a readiness probe into a model completion request.

## 5. Offline verification is complete

PR #24 / merged tree verification:

```text
STAGE_A_FOCUSED_TESTS=PASS__44_TESTS
CANONICAL_FULL_SUITE=PASS__1273_TESTS__27_SKIPPED
DIFF_HYGIENE=PASS
LIVE_CALLS=0
PAID_SPEND_CNY=0
```

Coverage includes plan-byte drift, wrong 96→36 stimulus materialization, journal tampering, stale locks, crash recovery, persistent cap accounting, duplicate frozen-slot prevention, missing-credential zero-network behavior, provider-model drift, malformed model output, terminal HTTP failure without retry, Kimi/DeepSeek read-only endpoint routing, MiniMax zero-network unresolved behavior, auth/readiness failure handling, exact frozen shortfall computation and credential non-exposure.

## 6. Credential / existing-balance readiness is now the only normal pre-network step

The current project-brain execution environment was checked without printing secret values:

```text
MOONSHOT_API_KEY=NOT_AVAILABLE_IN_CURRENT_RUNTIME
DEEPSEEK_API_KEY=NOT_AVAILABLE_IN_CURRENT_RUNTIME
MINIMAX_API_KEY=NOT_AVAILABLE_IN_CURRENT_RUNTIME
CREDENTIAL_VALUE_EXPOSURE=NONE
EXISTING_PROVIDER_BALANCE=NOT_VERIFIED__BLOCKED_BY_MISSING_CREDENTIALS
NEW_RECHARGE_REQUIRED=NOT_DETERMINED
```

This does **not** imply any provider requires funding. It means this execution environment cannot authenticate the required read-only checks.

Current read-only/non-billable readiness policy:

```text
KIMI=GET https://api.moonshot.cn/v1/users/me/balance
DEEPSEEK=GET https://api.deepseek.com/user/balance
MINIMAX_PAYGO=NO_VERIFIED_READ_ONLY_BALANCE_API__KEEP_UNRESOLVED_WITH_ZERO_NETWORK
MINIMAX_TOKEN_PLAN=mmx quota EXISTS__NOT_EQUIVALENT_TO_PAYGO_BALANCE
```

Never send a billable MiniMax model request merely to infer whether funds exist.

## 7. Exact next execution sequence

```text
1. Fetch current main HEAD and refresh runtime brief/current state.
2. Make the already-existing provider credentials available to the secure execution environment without committing or printing them.
3. Run tools/check_jianghe_provider_readiness.py; it rebuilds and byte-verifies the committed frozen plan before credential use.
4. Query Kimi existing CNY balance through the official read-only balance endpoint only.
5. Query DeepSeek existing CNY balance through the official read-only balance endpoint only.
6. Resolve MiniMax pay-as-you-go funding only through an official non-billable account/quota surface; if none is machine-accessible, keep MiniMax balance readiness UNKNOWN rather than probing with a model call.
7. If any NEW recharge/top-up is genuinely required, return provider + exact frozen shortfall amount + reason to Owner and stop funding action.
8. If existing credentials/funds suffice, execute Stage A only through the frozen single-slot runner: max 5 calls/provider, max CNY6/provider, max CNY18 Stage A, shared CNY100 total ledger.
9. Persist evidence after every attempted slot; a durable NETWORK_ATTEMPT_STARTED event forbids automatic retry.
10. Commit Stage-A evidence and ranking before any Stage-B call.
```

## 8. Existing pre-spend closures remain binding

```text
BSP-001..005=CLOSED
RSP-001..002=CLOSED
PRE_SPEND_REPAIR_REAUDIT=PASS
LIMIT_015=RESOLVED
LIMIT_012=ACTIVE__REAL_MODEL_JIANGHE_FIDELITY_NOT_YET_RUN
```

Do not weaken content-addressed Jianghe context, closed-world observations, evaluator-side scoring, exact model authorization, budget caps, raw response/usage evidence, outcome firewall or credential secrecy.

## 9. Tool decision

```text
TOOL_DECISION=USE_EXISTING
```

No new framework is required. Credential availability is an execution-environment boundary, not a reason to introduce another provider abstraction or model-evaluation stack.

## 10. Safety checkpoint

```text
STAGE_A=AUTHORIZED__OFFLINE_PREEXECUTION_COMPLETE__BLOCKED_BEFORE_NETWORK_ON_CREDENTIAL_EXISTING_BALANCE_READINESS
LIVE_CALLS=0
PAID_SPEND_CNY=0
OUTCOME_ACCESS=NO
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

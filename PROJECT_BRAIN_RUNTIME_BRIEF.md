# PROJECT_BRAIN_RUNTIME_BRIEF

As of: `2026-08-27`

## Mandatory refresh

Before substantive project work:

1. refresh GitHub `main` HEAD;
2. read `PROJECT_DIRECTION.md`;
3. read `CURRENT_STATE.md`;
4. read task-specific authority/evidence;
5. for spend/execution, additionally refresh the exact executable smoke authority and Owner decision;
6. never infer current project facts from chat history or obsolete material.

## Current headline

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

`MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1 = COMPLETE`

`LOCAL_WORKSTATION_ACCEPTANCE = PASS`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_PREPAYMENT_READY`

`MODEL_COGNITIVE_SCOPE = TRADING_ONLY`

`WAKE_POLICY = EVERY_NEW_CLOSED_5M_BAR`

`PAPER_EXECUTION = DEFERRED`

`DEEPSEEK_HARNESS = ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

`DEPLOYMENT = LOCAL_WORKSTATION_FIRST`

## Current evidence state

Offline V0.1 preexecution gates are complete:

`docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`

`V0_1_OFFLINE_PREEXECUTION_GATES = PASS`

`FULL_EXACT_SLICE_MOCK_DRY_RUN = PASS`

Exact sealed replay:

- product `cu`
- contract `SHFE.cu2406`
- 2 burn-in + 20 measurement days
- 1998 governed 5m wakes
- one persistent trader
- R1 verified
- R2 `NOT_OBSERVED` permitted by frozen design
- real provider calls `0`

## Provider smoke boundary

Owner decision:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_OWNER_DECISION.md`

Machine authority:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`

The smoke preparation is complete and merged:

`PROVIDER_SMOKE_PREPARATION = READY`

Frozen smoke scope:

- first 3 governed wakes of the sealed slice only;
- exact model `deepseek-v4-flash-vision-exp`;
- exactly four causal PNGs per request: `4H / 1H / 15m / 5m`;
- exactly one provider request per wake;
- `maxRetries = 0`;
- no hidden second request;
- forced project-owned restart after successful call 2, before call 3;
- call 4 impossible;
- full 1998-call replay unauthorized.

Paid-safety guards include:

- authority must be ACTIVE before credentials/network capability;
- execution-critical working tree must match the full bound execution commit;
- prompt/context/renderer/API-key identities must match authority;
- paid production endpoint cannot be overridden;
- Harness result must report exact provider/model, 4 images and 1 request;
- ACTIVE `max_spend_cny` must be positive and finite.

Pinned Harness:

- version `0.1.1-rc.2`;
- commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`;
- project fail-closed patch under `integrations/deepseek-harness/`;
- retry policy `mode: normal`, `maxRetries: 0`.

Final smoke-preparation CI passed Repository CI and DeepSeek Harness Dynamic Admission including the dedicated one-wake/one-request/four-image bridge gate.

## Exact next task

`NEXT_TASK = OWNER_PAYMENT_CONFIRMATION_FOR_THREE_CALL_PROVIDER_SMOKE`

Current machine authority is still:

`status = PENDING_OWNER_PAYMENT_CONFIRMATION`

`owner_payment_confirmation = false`

`max_spend_cny = PENDING_OWNER_CONFIRMATION`

Therefore:

`REAL_DEEPSEEK_PROVIDER_CALLS = PAUSED`

`NEXT_EXPLICIT_PAID_SLOT = THREE_CALL_PROVIDER_SMOKE__PENDING_OWNER_PAYMENT_CONFIRMATION`

Do not perform additional offline research gates before asking for the payment/execution decision. If the Owner approves, activate only the bounded three-call smoke authority with the explicitly approved CNY ceiling, then execute the three-call smoke exactly once and fail closed on the first error.

## Current locks

- three-call provider smoke: pending Owner payment confirmation
- full 1998-call replay: locked
- learning/policy promotion: locked
- validation/holdout: locked
- shadow: locked
- broker/account: locked
- real money: locked

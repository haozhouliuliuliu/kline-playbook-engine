# CURRENT_STATE

As of: `2026-08-27`

## Mission

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

Target: one persistent, auditable, Jianghe-grounded DeepSeek China-futures trader whose deterministic operational mechanics remain project-owned and whose model cognition is reserved for trading.

## Active work package

Owner-approved replay authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

Provider-smoke Owner decision:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_OWNER_DECISION.md`

Machine-readable smoke authority:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_PREPAYMENT_READY`

`NEXT_TASK = OWNER_PAYMENT_CONFIRMATION_FOR_THREE_CALL_PROVIDER_SMOKE`

## Frozen V0.1 experiment

- product: `cu`
- concrete contract: `SHFE.cu2406`
- prior history: 20 eligible trading days
- burn-in: `2024-04-10`, `2024-04-11`
- measurement: 20 trading days through `2024-05-14`
- replay days: `22`
- exact slice identity: `347291481968b1884635a11aa1da985d9aad1b3fb854a16087bbca662bd85a06`
- exact slice seal: `e9bbd232fd05d320a24c80ac5570a94abdf6d4c3a167cdd5c46f4426a6c84156`
- wake policy: `EVERY_NEW_CLOSED_5M_BAR`
- governed wakes: `1998`
- observation stack: `4H / 1H / 15m / 5m`
- `PAPER_EXECUTION = DEFERRED`
- no adaptive/event-driven wake optimization in V0.1
- no amount PnL/win-rate/outcome labels in model decision context
- no outcome-driven rerun
- no learning or policy promotion

## Offline preexecution result

Formal evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`

`V0_1_OFFLINE_PREEXECUTION_GATES = PASS`

`FULL_EXACT_SLICE_MOCK_DRY_RUN = PASS`

Owner-workstation real-corpus mock result:

- replay days: `22`
- governed sessions: `87`
- `step = wake = request = mock-call = 1998`
- R1 phase-boundary restart: `VERIFIED`
- R2 active-state restart coverage: `NOT_OBSERVED` as permitted by the frozen design
- real provider calls: `0`
- provider call authorized: `false`

The pre-provider implementation now includes and tests:

- strict trading-only prompt/context contract;
- append-only/versioned hypothesis revision history;
- deterministic outcome-blind exact-slice selector;
- formal D01/D02 qualification with 116 failed partitions excluded and 32,864 qualified;
- fixed 5m wake ledger and replay orchestrator;
- causal 4H/1H/15m/5m context construction;
- persistent working memory / journal / hypothesis state;
- intent-only lifecycle state;
- restart, leakage, request-count and audit gates;
- exact-slice full mock/no-provider lifecycle rehearsal.

## Provider smoke preparation

`PROVIDER_SMOKE_PREPARATION = READY`

Current merged provider-smoke execution path is zero-cost prepared and CI-verified:

- exact first 3 governed 5m wakes only;
- `max_provider_calls = 3`;
- `max_retries = 0`;
- exactly 4 deterministic PNG inputs per call: `4H / 1H / 15m / 5m`;
- one governed wake -> exactly one Harness model request;
- no hidden stale-file second request;
- forced project-owned restart after successful call 2 before call 3;
- exact provider/model/image/request assertions after every call;
- execution-critical source bound to full 40-hex execution commit before network capability exists;
- live prompt/context/renderer/API-key identities bound before network capability exists;
- provider endpoint override allowed only for explicit loopback tests;
- ACTIVE spend field must be a positive finite CNY value;
- fourth provider call impossible by construction;
- full 1998-call replay explicitly unauthorized.

Pinned Harness:

- version `0.1.1-rc.2`
- commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project fail-closed patch under `integrations/deepseek-harness/`

GitHub CI on the final smoke-preparation head passed both:

- Repository CI
- DeepSeek Harness Dynamic Admission, including the one-wake/one-request/four-image smoke bridge test

## Current smoke authority

The machine-readable authority remains deliberately inactive:

`status = PENDING_OWNER_PAYMENT_CONFIRMATION`

`owner_payment_confirmation = false`

`max_provider_calls = 3`

`max_retries = 0`

`images_per_call = 4`

`max_spend_cny = PENDING_OWNER_CONFIRMATION`

`full_replay_authorized = false`

`full_replay_1998_calls_authorized = false`

Therefore:

`REAL_DEEPSEEK_PROVIDER_CALLS = PAUSED`

`NEXT_EXPLICIT_PAID_SLOT = THREE_CALL_PROVIDER_SMOKE__PENDING_OWNER_PAYMENT_CONFIRMATION`

No real provider request may occur until the Owner explicitly confirms the smoke spend/execution authority. The proposed preparation ceiling is CNY `3.00`; it is not yet authorization and is not a provider-side guaranteed cap.

## Knowledge and governance boundary

- `JIANGHE_CANON`: source-grounded and read-only.
- `PROJECT_VALIDATED_POLICY`: independently validated project extensions.
- `DS_HYPOTHESIS_MEMORY`: non-executable candidate ideas.
- `DS_WORKING_MEMORY`: persistent current market state.
- `DS_JOURNAL`: auditable reflection, not source truth or policy.

Promotion remains locked:

`OBSERVATION -> HYPOTHESIS -> COUNTEREXAMPLE SEARCH -> DEVELOPMENT EVIDENCE -> INDEPENDENT VALIDATION -> PROJECT_VALIDATED_POLICY`

## Current locks

- real provider smoke: `PENDING_OWNER_PAYMENT_CONFIRMATION`
- full 1998-call provider replay: locked
- learning/policy promotion: locked
- validation/holdout: locked
- shadow: locked
- broker/account: locked
- real money: locked

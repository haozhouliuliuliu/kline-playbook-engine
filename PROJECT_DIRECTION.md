# PROJECT_DIRECTION

As of: `2026-08-27`

This file is the binding current product and research direction for `kline-playbook-engine`.

## 1. Mission

Build one persistent, single-purpose China-futures AI trader whose active model source is DeepSeek, whose initial trading foundation is Jianghe's documented experience, and whose long-run improvement comes from governed memory, chronological replay, reflection, falsifiable hypothesis generation, counterexample search and independent validation.

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

## 2. Product loop

`observe market -> retrieve relevant knowledge and experience -> reason -> decide -> record -> learn under governance`

Hard risk, broker/account truth, order lifecycle, reconciliation, safety, provider routing, replay scheduling and other deterministic operational mechanics remain project-owned systems.

## 3. Single-purpose model boundary

`MODEL_COGNITIVE_SCOPE = TRADING_ONLY`

DeepSeek is the Jianghe trader, not the project operator.

The project system pre-resolves wake timing, replay clock, data eligibility, contract mapping, session validity, chart construction, context assembly, storage, retries, audit, response validation, provider routing, experiment scheduling and cost accounting.

DeepSeek's cognition is limited to the trading task: understand the current causal market, apply Jianghe evidence and permitted memory, identify setup/state/levels/triggers/invalidation, choose the permitted trading action, and express uncertainty without inventing missing information.

## 4. Knowledge hierarchy

- `JIANGHE_CANON`: source-grounded Jianghe claims/cases/unknowns; read-only to the trader.
- `PROJECT_VALIDATED_POLICY`: project extensions that passed required independent validation.
- `DS_HYPOTHESIS_MEMORY`: DeepSeek candidate ideas; never executable policy.
- `DS_WORKING_MEMORY`: persistent current market state, regions, triggers and open questions.
- `DS_JOURNAL`: auditable reflection/self-critique; not market fact or Jianghe canon.

Promotion path:

`OBSERVATION -> HYPOTHESIS -> COUNTEREXAMPLE SEARCH -> DEVELOPMENT EVIDENCE -> INDEPENDENT VALIDATION -> PROJECT_VALIDATED_POLICY`

Profit alone does not prove reasoning correctness; loss alone does not prove reasoning error.

## 5. Context and trader identity

Each DeepSeek call receives a bounded, auditable context assembled from stable trading contract, relevant Jianghe canon, validated project policy, working memory, bounded journal/hypothesis memory, causal multi-timeframe observation/charts and task-specific audited tool results.

`JiangheAITraderIdentity` binds outcome-affecting model/version, prompts, context-selection policy, memory schema/policy, chart renderer, observation schema, wake policy, decision schema/normalizer, mechanical guards, inference configuration and tool capability set. Material changes create a new trader version/descendant with exposure lineage preserved.

## 6. Observation baseline

Active stack:

`4H / 1H / 15m / 5m`

4H role:

`BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`

Future information is unavailable before its governed availability time. Working memory persists forward. Do not turn the historical corpus into independent stateless prompt exams.

## 7. Active work package

Replay authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

Provider-smoke decision:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_OWNER_DECISION.md`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_PREPAYMENT_READY`

The sealed V0.1 replay remains:

- one persistent trader;
- product `cu`, contract `SHFE.cu2406`;
- 20 prior eligible trading days;
- 2 burn-in + 20 measurement trading days;
- exact `1998` governed closed-5m wakes;
- `WAKE_POLICY = EVERY_NEW_CLOSED_5M_BAR`;
- causal `4H / 1H / 15m / 5m` observation;
- intent-only lifecycle state;
- `PAPER_EXECUTION = DEFERRED`;
- no amount PnL/win-rate/outcome labels in model decision context;
- no outcome-driven rerun;
- no learning or policy promotion.

## 8. Offline completion

Formal evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`

`V0_1_OFFLINE_PREEXECUTION_GATES = PASS`

`FULL_EXACT_SLICE_MOCK_DRY_RUN = PASS`

The full exact-slice real-corpus mock rehearsal produced:

`step = wake = request = mock-call = 1998`

with R1 restart verified, R2 coverage recorded according to the frozen rule, and zero real provider calls.

No additional offline research gate is required before the bounded real-provider smoke decision.

## 9. Provider smoke direction

The next possible paid action is not the full replay. It is one bounded execution-integrity smoke slot:

`FIRST_3_GOVERNED_5M_WAKES_OF_THE_SEALED_SLICE`

Hard scope:

- maximum real provider model requests: `3`;
- retries: `0`;
- four causal PNG images per request: `4H / 1H / 15m / 5m`;
- one wake -> exactly one Harness model request;
- forced project-owned restart after successful call 2 before call 3;
- any execution, schema, image, identity, persistence or accounting failure stops immediately;
- no replacement wake or re-ask;
- call 4 forbidden;
- full 1998-call replay remains unauthorized.

Machine authority:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`

Current authority remains inactive:

`status = PENDING_OWNER_PAYMENT_CONFIRMATION`

`owner_payment_confirmation = false`

`max_spend_cny = PENDING_OWNER_CONFIRMATION`

The proposed preparation ceiling is CNY `3.00`; this is not current authorization and is not a provider-side guaranteed cap.

## 10. Harness and paid-safety boundary

`DEEPSEEK_HARNESS = ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

Use only:

- version `0.1.1-rc.2`
- commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project fail-closed patch under `integrations/deepseek-harness/`
- retry policy `maxRetries: 0`

Provider-smoke execution is fail-closed unless authority, execution code, prompt/context/renderer identities, exact first-three wakes and positive finite spend ceiling all match. Production paid execution may not override the official provider endpoint.

## 11. Current authorization boundary

`NEXT_TASK = OWNER_PAYMENT_CONFIRMATION_FOR_THREE_CALL_PROVIDER_SMOKE`

`REAL_DEEPSEEK_PROVIDER_CALLS = PAUSED`

`NEXT_EXPLICIT_PAID_SLOT = THREE_CALL_PROVIDER_SMOKE__PENDING_OWNER_PAYMENT_CONFIRMATION`

Still locked:

- full 1998-call provider replay
- learning/policy promotion
- validation/holdout
- shadow
- broker/account
- real money

If the Owner approves the bounded smoke payment/execution authority, execute only that three-call slot and stop on the first failure. The outcome of that smoke determines whether the project may ask for a later full-replay spend decision; it does not itself authorize the full replay.

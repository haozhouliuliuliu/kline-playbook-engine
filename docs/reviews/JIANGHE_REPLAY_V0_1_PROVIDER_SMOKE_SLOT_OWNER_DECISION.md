# JIANGHE REPLAY V0.1 PROVIDER SMOKE SLOT — OWNER DECISION

Status: `APPROVED_FOR_PREPARATION__NOT_AUTHORIZED_TO_SPEND`

Date: `2026-08-26`

Work package: `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

## Owner decision

The Owner directs the project to prepare one very small real-provider smoke slot before considering the full `1998`-request replay.

The project must stop immediately before the first action that can incur DeepSeek/provider cost. A separate final Owner payment/execution confirmation is required before any real provider request.

Therefore:

`SMOKE_SLOT_RESERVED = YES`

`REAL_PROVIDER_EXECUTION_AUTHORIZED = NO`

`NEXT_EXPLICIT_PAID_SLOT = THREE_CALL_PROVIDER_SMOKE__PENDING_OWNER_PAYMENT_CONFIRMATION`

## Purpose

This smoke slot is an execution-path integrity probe only. It is not a profitability test and does not adjudicate Jianghe trading quality.

It must test, with the same sealed replay inputs intended for the later live replay:

1. real DeepSeek API connectivity through the admitted pinned Harness path;
2. exact model `deepseek-v4-flash-vision-exp`;
3. actual causal 4H / 1H / 15m / 5m PNG visual input;
4. strict structured response compatibility with the project normalizer;
5. one governed wake -> exactly one provider model request;
6. zero retries and zero hidden second model requests;
7. project-owned persistent trader state across sequential calls;
8. one deliberate project-owned restart after the second successful smoke call, followed by a third call that proves state continuity.

## Exact bounded scope

The smoke uses the already sealed V0.1 historical slice:

- product: `cu`
- concrete contract: `SHFE.cu2406`
- exact slice seal identity: `e9bbd232fd05d320a24c80ac5570a94abdf6d4c3a167cdd5c46f4426a6c84156`
- slice identity: `347291481968b1884635a11aa1da985d9aad1b3fb854a16087bbca662bd85a06`
- first replay day: `2024-04-10`

Smoke wake selection is mechanical and outcome-blind:

`FIRST_3_GOVERNED_5M_WAKES_OF_THE_SEALED_SLICE`

No wake may be skipped, replaced, re-asked or selected by looking at the market path or response quality.

Hard request bound:

`MAX_REAL_PROVIDER_MODEL_REQUESTS = 3`

Restart rule:

`FORCED_PROJECT_STATE_RESTART_AFTER_SUCCESSFUL_CALL_2__BEFORE_CALL_3`

Any failed provider request, image/request construction failure, response-schema failure, identity mismatch, persistence failure or request-accounting failure stops the smoke immediately. There is no automatic retry and no replacement wake.

## Visual-input requirement

Each admitted smoke request must carry the same causal market facts used by the replay runtime and actual deterministic PNG visual stimulus for all four active timeframes:

`4H / 1H / 15m / 5m`

The PNG content hashes and visual provenance identities must be derived from the exact causally visible bars at that wake. A text-only or metadata-only smoke does not satisfy this slot.

## Harness / model lock

Only the adopted path is admissible:

- Harness version: `0.1.1-rc.2`
- Harness commit: `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project fail-closed transport patch: `integrations/deepseek-harness/`
- project provider adapter route: `deepseek`
- provider endpoint: official DeepSeek endpoint only for paid production smoke; test endpoint override is loopback-only
- model: `deepseek-v4-flash-vision-exp`
- retry policy: `maxRetries = 0`
- model substitution: forbidden
- hidden second chat request: forbidden fail-closed

The provider bridge uses the Harness single-request adapter stream surface directly rather than the general agent loop, so auxiliary model work such as compaction, title generation or tool-loop continuation cannot add ungoverned model requests.

## Cost boundary

The previous rough planning assumption was approximately CNY `0.10` per call, implying approximately CNY `0.30` for three calls. That is only an estimate; actual billing depends on provider usage.

For preparation purposes only, reserve a conservative proposed smoke spend ceiling:

`PROPOSED_SMOKE_SPEND_CEILING_CNY = 3.00`

This is **not** a provider-side guaranteed monetary cap and is **not** current authorization to spend. The project hard-enforces the three-model-request ceiling; actual token usage and billing-relevant usage must be recorded after each successful response.

Before the first real request, the machine-readable executable authority must be switched from `PENDING_OWNER_PAYMENT_CONFIRMATION` to `ACTIVE`, set `owner_payment_confirmation=true`, bind a positive finite `max_spend_cny`, and retain all frozen code/model/wake/image/request guards.

## Still forbidden

This decision does not authorize:

- any real provider request yet;
- the full `1998`-request replay;
- retries or outcome-driven re-asking;
- sample/date/product replacement;
- paper execution or historical fill claims;
- learning or policy promotion;
- validation/holdout;
- shadow;
- broker/account actions;
- real money trading.

## Completion of preparation

The zero-cost preparation is complete and CI-verified on current main. The machine-readable authority remains:

`status = PENDING_OWNER_PAYMENT_CONFIRMATION`

`owner_payment_confirmation = false`

`max_provider_calls = 3`

`max_retries = 0`

`images_per_call = 4`

`full_replay_1998_calls_authorized = false`

The next action is the final Owner payment/execution confirmation. No additional offline research gate is required before that confirmation.

# JIANGHE REPLAY V0.1 PROVIDER SMOKE RETEST — OWNER PAYMENT / EXECUTION AUTHORITY

Status: `OWNER_APPROVED__CONDITIONAL_ON_REPAIR_AND_RESEAL`

Date: `2026-08-27`

Work package: `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

Response-contract authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_RESPONSE_CONTRACT_CLARIFICATION_OWNER_DECISION_2026-08-27.md`

Prior fail-closed evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`

## Owner payment / execution decision

The original paid smoke slot is consumed by its fail-closed first real call and must not be resumed or treated as having "two calls left".

The Owner instead authorizes **one new, independent three-call provider-smoke retest slot** after the approved response-contract clarification and required offline verification are complete.

```text
AUTHORIZED_PAID_SLOT = THREE_CALL_PROVIDER_SMOKE_RETEST_AFTER_RESPONSE_CONTRACT_CLARIFICATION
OWNER_PAYMENT_CONFIRMATION = TRUE
MAX_PROVIDER_CALLS = 3
MAX_RETRIES = 0
MAX_SPEND_CNY = 3.00
FULL_V0_1_1998_CALL_REPLAY_AUTHORIZED = FALSE
```

The one real request consumed by the old failed slot is historical evidence and does **not** reduce this new slot from three calls to two. Across both historical slots, the project may therefore have one old failed request plus at most three requests under this new authority.

## Exact scientific scope

The retest remains an execution-path integrity probe, not a profitability test.

It must use:

- provider: `deepseek`;
- model: `deepseek-v4-flash-vision-exp`;
- adopted DeepSeek Harness pin from `TOOL_REGISTRY.md`;
- the same sealed V0.1 product/contract/slice;
- the same exact first three governed wake identities;
- exactly four causal PNGs per admitted request (`4H / 1H / 15m / 5m`);
- exactly one provider request per governed wake;
- `maxRetries = 0`;
- forced project-owned restart after successful call 2 before call 3;
- no call 4;
- no replacement wake;
- no outcome-driven re-asking.

The retest starts from a clean pre-smoke project state corresponding to the beginning of `call_1`. The rejected raw response from the old slot must not enter model-visible working memory or trading context.

## New machine authority required

This Owner authority is not itself sufficient for network capability.

Before the first retest request, the integration lane must generate/reseal a **new** machine-readable authority against the repaired execution-critical code and new prompt identity.

Requirements:

- machine authority version/identity must distinguish this retest from the consumed V0.1 smoke slot;
- `status = ACTIVE` only after all repair verification gates pass;
- `owner_payment_confirmation = true`;
- `max_provider_calls = 3`;
- `max_retries = 0`;
- `max_spend_cny = 3.00`;
- `full_replay_authorized = false`;
- `full_replay_1998_calls_authorized = false`;
- exact execution-code commit must be bound;
- new prompt contract identity and prompt hashes must be bound;
- context policy, renderer, model, Harness, slice and wake identities must remain explicitly bound;
- production endpoint and credential identity guards remain fail-closed.

The current old-slot machine authority must remain terminal/non-executable until replaced by the correctly generated new retest authority.

## Pre-network gates

Before creating provider/network capability, the execution lane must verify:

1. current GitHub `main` and `CURRENT_STATE.md` still point to this retest;
2. all response-contract clarification tests pass;
3. provider-smoke focused tests pass;
4. loopback/mock full three-call rehearsal passes, including restart after call 2;
5. fail-closed usage/evidence persistence test passes;
6. repository authority-consistency checks pass;
7. full normal regression passes;
8. `DEEPSEEK_API_KEY` availability is checked only as `SET / UNSET`;
9. the new machine authority exactly matches the current execution-critical working tree.

Any mismatch stops before provider capability is created.

## Execution and terminal rule

The new slot attempts the exact three wakes in order:

```text
call_1 -> call_2 -> forced restart -> call_3 -> STOP
```

If any request, normalization, persistence, identity, restart, request-accounting, cost or other governed guard fails, stop immediately with zero retry and close/consume this new slot.

After either 3/3 success or fail-closed termination:

- write immutable evidence;
- make the machine slot terminal/non-executable;
- update only `CURRENT_STATE.md` for volatile state;
- do not automatically start the full V0.1 replay.

## Still not authorized

This authority does not authorize:

- full V0.1 `1998` provider replay;
- a fourth request within the retest;
- automatic retry/re-run after a retest failure;
- post-V0.1 CU/RB paid replay;
- historical execution/PnL semantic changes;
- SHADOW;
- PAPER/account connection;
- broker/account actions;
- permanent numeric risk rules;
- real money/funding/orders;
- learning/policy promotion.

## Outcome — retest completed 3/3, slot closed

Executed `2026-08-27`. Result: `PASS (3/3)`.

- real provider calls attempted: `3`; normalized: `3`; retries: `0`; hidden: `0`
- forced project-owned restart after call 2: `VERIFIED`
- execution evidence: `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_2026-08-27.md`
- fresh retest machine authority transitioned to terminal `REVOKED`:

`authority_identity = cc29bc494c787ef94dc560e1c6d2d74075df8d7a8d0c3950efc304af59204f3e`

`THIS FRESH THREE-CALL RETEST SLOT CANNOT BE ACCIDENTALLY RE-RUN`

The full V0.1 `1998`-call replay remains unauthorized; next step is smoke
adjudication / preparation of an Owner decision for the full sealed V0.1.

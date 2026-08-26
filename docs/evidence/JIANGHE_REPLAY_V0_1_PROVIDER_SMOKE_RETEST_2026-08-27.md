# JIANGHE REPLAY V0.1 PROVIDER SMOKE RETEST — EXECUTION EVIDENCE

Status: `PASS (3/3)`

Date: `2026-08-27`

Work package: `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

Retest authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_EXECUTION_AUTHORITY_2026-08-27.md`

Response-contract clarification authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_RESPONSE_CONTRACT_CLARIFICATION_OWNER_DECISION_2026-08-27.md`

This is an execution-path integrity probe. It does **not** evaluate profitability
and does **not** adjudicate Jianghe trading quality.

## Execution identities

- execution starting `main` HEAD: `0990fb46b3a41649e103b8e1eae7814e0bf65c94`
- fresh retest machine authority: `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_SLOT.json`
  - version: `KPE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_V0_1`
  - status at execution: `ACTIVE`
  - authority identity: `93ab34e088bdece221625dee23d30ee6d4330137365a19def154e52940ff368c`
  - execution_code_commit: `4cf9600d834dd7df9e0526b2583a07e42a4b996e`
  - prompt contract: `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_2`, identity `d5fd8384864bc4e0b2ff5198d21f0c4c522a33662babb1b13824c87d5420bac2`
- Harness: version `0.1.1-rc.2`, commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project transport patch: `integrations/deepseek-harness/` (`NO_HIDDEN_STALE_CHAT_RETRY`, maxRetries `0`)
- provider: `deepseek`; endpoint: official DeepSeek paid production endpoint (no base-url override)
- model: `deepseek-v4-flash-vision-exp`
- trader identity: `bf233fb7e166b7ca7a36e46dfab50428092a265a6cb2a6a8d2d5a4606241e8a4`
- runtime contract identity: `7558180f75b9c497ada10886b7ed9f32d159ee3c332827c50e95b8834f7728ab`

## Sealed slice / wakes

- slice identity: `347291481968b1884635a11aa1da985d9aad1b3fb854a16087bbca662bd85a06`
- exact slice seal identity: `e9bbd232fd05d320a24c80ac5570a94abdf6d4c3a167cdd5c46f4426a6c84156`
- product / contract: `cu` / `SHFE.cu2406`
- context policy identity: `98262c9ab0614b4145fe56cb8746a44d754d03a38a25584aba810991cd666371`
- renderer identity: `JIANGHE_VISUAL_RENDERER_V0_1:2397764a0f3e2b453456fd8735caeb59881d19ea5a2399fc91fb7e7307525851`
- constructed causal bars: 4H=164, 1H=286, 15m=1270, 5m=3810
- canonical fixed-5m preflight identity: `e4d29a5f6001302811c78be76565ef3095325fd46d28811c88591b6e375750a8`

## Per-call result (exact order)

Sequence executed: `call_1 -> call_2 -> forced project-owned restart -> call_3 -> STOP`.

| call | wake identity | request id | raw response sha256 | finish | input | output | reasoning | cacheRead | decision identity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| call_1 | `4000fa69…e1105` | `req-c9ade84dcb9d4aa089c775fb785c13fc` | `cb0295488a1e99d94084be65998d2f8788c52a681ba0f4cf5e6a4b6cd24234e0` | stop | 13955 | 10917 | 10474 | 0 | `2f4432b1…ef6a5` |
| call_2 | `b4785ee8…3962` | `req-e50137d3958e48ef96ba3297c0a3a355` | `f6fe44b8770a689dc307bb9b17c2e3e96e22e2fcf0549041d13a9cfe4140ce3e` | stop | 14307 | 4739 | 4263 | 768 | `e3a2f91b…2bf9` |
| call_3 | `149e93dc…e94b` | `req-8634d66056ac467488fb99d530e97584` | `5ccb73cc9f70bb3673ced9a955c548525e02d23c53a8caecbddbaf53bded04ab` | stop | 14671 | 10571 | 10010 | 1536 | `5011041c…deb5b` |

Each admitted call carried exactly four deterministic causal PNGs (`4H / 1H / 15m / 5m`);
PNG SHA-256 per call match the preflight/rendered bundle (see runner evidence artifact).

## Fail-closed observability (repair verified)

- `MODEL_PROVIDER_RESPONSE_METADATA` audit events: `3` (provider/model/finish_reason/token_usage
  durably persisted before normalization for every received response)
- `MODEL_RESPONSE_RAW`: `3`; `MODEL_RESPONSE_NORMALIZED`: `3`; `MODEL_RESPONSE_REJECTED`: `0`
- `MODEL_REQUEST_PREPARED_OFFLINE`: `3`
- `REPLAY_RESTART_VERIFIED`: `1`; `REPLAY_STATE_SEALED`: `1`; `REPLAY_FINALIZED`: `1`

The provider did not expose a request id through the pinned bridge replay state, so
`provider_request_id` is recorded as `null` (never fabricated).

## Restart continuity

Forced project-owned restart after successful call 2 before call 3:

- restart sealed identity: `d946c402ff87aaaafe2af647fec60ddc0da5f85b4538ad850a31e249b767c288`
- `restart_continuity_result = VERIFIED`
- persistent trader identity unchanged (`bf233fb7…`); persisted working state, memory,
  request accounting and audit lineage continuous across the reopen.

## Request accounting

- real provider model requests attempted: `3`
- real provider model requests normalized: `3`
- retries: `0`
- hidden/auxiliary second requests: `0`
- call 4: `NO` (impossible by construction)
- full 1998-call replay executed: `NO`
- request accounting: `PASS`

## Cost

Exact provider token usage per call is recorded above. The exact
`deepseek-v4-flash-vision-exp` tariff is not independently verified, so the
following is a labeled reference estimate only using the public
`deepseek-v4-flash` tariff (input cache-miss CNY 1.00 / 1M, cache-hit CNY 0.02 / 1M,
output CNY 2.00 / 1M):

- approximate total estimated charge: **~ CNY 0.09** (well below the `CNY 3.00` ceiling)

The Owner can confirm the exact bill in the DeepSeek usage console.

## Adjudication

- `PROVIDER_PATH_INTEGRITY`: `PASS`
- `SCHEMA_COMPATIBILITY`: `PASS` (all 3 responses conform to the strict
  `JIANGHE_RUNTIME_RESPONSE_V0_1` array-shaped `numeric_claims` contract)
- `REQUEST_ACCOUNTING`: `PASS`
- `STATE_CONTINUITY`: `PASS` (forced restart after call 2 verified)
- `TRADING_QUALITY`: `NOT EVALUATED` (out of scope)

`SMOKE_RETEST_RESULT = 3/3 PASS`

## Slot closure

The fresh three-call retest slot is consumed/closed and terminal. The fresh
machine authority has been transitioned to `REVOKED` and cannot be re-run without
a new Owner paid authority. The full V0.1 `1998`-call replay remains unauthorized.

Next step is limited to smoke adjudication / preparation of an Owner decision for
the full sealed V0.1 replay. No automatic 1998-call replay was started.

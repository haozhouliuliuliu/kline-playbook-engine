# JIANGHE REPLAY V0.1 — POST-REPAIR THREE-CALL PROVIDER REVALIDATION EXECUTION EVIDENCE

Status: `PASS (3/3)`

Date: `2026-08-27`

Work package: `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

Revalidation authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION_OWNER_DECISION_2026-08-27.md`

This is an execution-path / model-contract revalidation, not a profitability test. It does **not** establish profitability, execution quality or long-term edge.

## Execution identities

- execution `main` HEAD: `24f81e2f9498730e2ed65902cc086b9211b28eb2`
- fresh V0_3 RETEST machine authority: `docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_SLOT_V0_3.json`
  - version: `KPE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_V0_3`
  - ACTIVE authority identity at execution: `b4299115aab90c19c2cb108b263be2555544fdbfaf215a4bc4708b14faa8f97a`
  - status after slot: `REVOKED` (terminal; never reused)
  - execution_code_commit: `24f81e2f9498730e2ed65902cc086b9211b28eb2`
  - Owner CNY ceiling: `OWNER_CNY_CEILING_WAIVED` (no numeric cap invented)
  - prompt contract: `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`
- Harness: version `0.1.1-rc.2`, commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project transport patch: `integrations/deepseek-harness/` (`NO_HIDDEN_STALE_CHAT_RETRY`, maxRetries `0`)
- provider: `deepseek`; production endpoint only (no base-url override, no test flag)
- model: `deepseek-v4-flash-vision-exp`
- trader identity: `39ea5818636e94a4e707a6615d2017dee48dce2e79efcef8b6783015814653ba`
- runtime contract identity: `4edae4cd9273ae2da633f2976825b10cb81e1a984155ac7b9588b6e8f642fa31`

## Sealed slice / wakes

- slice identity: `347291481968b1884635a11aa1da985d9aad1b3fb854a16087bbca662bd85a06`
- exact slice seal identity: `e9bbd232fd05d320a24c80ac5570a94abdf6d4c3a167cdd5c46f4426a6c84156`
- product / contract: `cu` / `SHFE.cu2406`
- context policy identity: `98262c9ab0614b4145fe56cb8746a44d754d03a38a25584aba810991cd666371`
- renderer identity: `JIANGHE_VISUAL_RENDERER_V0_1:2397764a0f3e2b453456fd8735caeb59881d19ea5a2399fc91fb7e7307525851`
- canonical fixed-5m preflight identity: `e4d29a5f6001302811c78be76565ef3095325fd46d28811c88591b6e375750a8`
- constructed causal bars: 4H=164, 1H=286, 15m=1270, 5m=3810
- verified canonical dataset: manifest `7510a4a943e85c9be256e62971b5a64d64e9976c2b01c9f5d0fe07b1c6c8d324`, corpus `1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8`, 32,980 partitions

## Per-call result (exact order)

Sequence executed: `call_1 -> call_2 -> forced project-owned restart -> call_3 -> STOP`.

| call | close time (+08) | logical wake identity | runtime wake identity | request id | finish | decision identity | PNGs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| call_1 | 2024-04-09 21:05 | `1c3ef378…14d5b6` | `1435a96a…b220e57` | `req-9fe7695740a242eb8bfb6ed0a0b7a212` | stop | `3db420e2…55e7ce` | 4 |
| call_2 | 2024-04-09 21:10 | `a840d882…10b7d62` | `61e12be1…fa51a655e` | `req-c60ae36953d34c9f9c7e2199dbc63d3b` | stop | `934c787b…40bb17` | 4 |
| call_3 | 2024-04-09 21:15 | `94221314…cddb296b` | `3f57e610…b1989ce` | `req-41beb8e82fb6449abc3014a64f3ccbd4` | stop | `3a7d0c6b…67ff910` | 4 |

Each admitted call carried exactly four deterministic causal PNGs (4H / 1H / 15m / 5m); PNG SHA-256 per call match the persisted preflight/rendered bundle. Visual artifact identities are preserved per call.

Full machine evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_RUN_2026-08-27.json`

## Provider metadata / token usage (durable)

| call | input | output | reasoning | cacheRead | cacheWrite |
| --- | --- | --- | --- | --- | --- |
| call_1 | 14515 | 14042 | 13266 | 0 | 0 |
| call_2 | 16679 | 11959 | 10891 | 640 | 0 |
| call_3 | 18443 | 2087 | 1123 | 2048 | 0 |

Provider metadata (`MODEL_PROVIDER_RESPONSE_METADATA` audit events: 3) durably persisted before normalization. `provider_request_id` is `null` (the pinned bridge did not expose a request id; never fabricated).

## Fail-closed observability

- `MODEL_PROVIDER_RESPONSE_METADATA`: `3`
- `MODEL_RESPONSE_RAW`: `3`; `MODEL_RESPONSE_NORMALIZED`: `3`; `MODEL_RESPONSE_REJECTED`: `0`
- `MODEL_REQUEST_PREPARED_OFFLINE`: `3`
- `REPLAY_RESTART_VERIFIED`: `1`; `REPLAY_STATE_SEALED`: `1`; `REPLAY_FINALIZED`: `1`
- `DS_WORKING_MEMORY_MUTATION`: `33`; `DS_JOURNAL_APPEND`: `1`
- `REPLAY_INTENT_POSITION`: `3` (all `WAIT`/`WATCH`, intent-only, no execution)

## Durable provider-attempt accounting

- durable attempt ledger: `provider_attempts.sqlite3` (state dir)
- `provider_attempt_count = 3`, all `RESULT_RECEIVED`
- each attempt bound to ACTIVE authority identity, exact logical+runtime wake identities, close time, request_id, `retry_count = 0`
- `known_result_count = 3`, `unknown_after_attempt_start_count = 0`, `unresolved_attempt_started_count = 0`
- `slot_requires_adjudication = false`

## Request accounting

- real provider model requests attempted: `3`
- real provider model requests normalized: `3`
- retries: `0`
- hidden/auxiliary second requests: `0`
- call 4: `NO` (impossible by construction)
- full 1998-call replay executed: `NO`
- request accounting: `PASS`

## Restart continuity

Forced project-owned restart after successful call 2 before call 3:

- restart sealed identity: `8c684715cc0b968b3df300cdf59c331aa791afc9c1443bafdded636ef396d3d5`
- `restart_continuity_result = VERIFIED`
- persistent trader identity unchanged; working state, memory, request accounting and audit lineage continuous across the reopen
- final state identity: `b82ff8c26740fea5c8a8612f369b01f8ae52c925daf38c80fa2fd753e90f2068`

## Structured-memory continuity (causal)

The persisted `DS_WORKING_MEMORY` carried model-supplied structured fields: `current_market_hypothesis`, `timeframe_trend_view`, `key_location_hypotheses`, `expected_trigger`, `invalidation_hypothesis`, `open_questions` (plus `directional_bias`, `attention_mode`, `last_meaningful_decision`).

Proven from `MODEL_REQUEST_PREPARED_OFFLINE` context payloads:

- **call_1**: working memory empty (SCAN, no hypothesis) — causal baseline;
- **call_2**: received accepted call_1 state (WATCH, hypothesis non-empty, 4 key-location hypotheses, `last_meaningful_decision=WAIT`);
- **call_3** (after forced restart): received accepted call_2 state (WATCH, full state preserved).

## Decision / source fidelity

- All three decisions normalize under `JIANGHE_RUNTIME_RESPONSE_V0_2` with strict output-enum enforcement and `source_references` to Jianghe canon claims (e.g., `JH-CLM-034-003`, `JH-CLM-042-002`).
- No future/outcome/PnL leakage: causal context index built from prior/burn-in/measurement windows only; all decisions are intent-only (`WAIT`/`WATCH`), no paper/real execution.
- Jianghe/source-fidelity evaluation is performed OFFLINE only; no fourth provider call was made.

## Machine authority terminalization

The V0_3 RETEST authority was terminalized to `REVOKED` immediately after the slot. It is never reused. Historical slots remain terminal and never reactivated.

## Cost

Owner CNY ceiling explicitly waived for this exact slot (`OWNER_CNY_CEILING_WAIVED`). Actual token usage retained above; no numeric spend cap was fabricated.

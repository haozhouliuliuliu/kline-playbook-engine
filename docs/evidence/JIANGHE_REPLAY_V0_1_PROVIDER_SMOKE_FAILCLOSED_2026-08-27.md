# JIANGHE REPLAY V0.1 PROVIDER SMOKE — FAIL-CLOSED EXECUTION EVIDENCE

Status: `STOPPED FAIL-CLOSED`

Date: `2026-08-27`

Work package: `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

Adjudication: `FAIL_CLOSED__PROVIDER_RESPONSE_SCHEMA_MISMATCH`

This three-call smoke is an execution-path integrity probe only. This evidence does **not** evaluate profitability and does **not** adjudicate Jianghe trading quality.

## Execution identities

- execution starting `main` HEAD: `c77f5ce82a0a8cf40b27260722b4026ccc1477bd`
- authority file: `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`
- authority identity (at execution time): `8583694f4164c7983f40d784bf21e5582b1ae7c96ca7b1fef902abf155fae905`
- code/execution identity: `execution_code_commit = 547a14e10e24dbb2eab01aa6d4e35b151aa1ddcb`
- Harness identity: version `0.1.1-rc.2`, commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project transport patch: `integrations/deepseek-harness/` (`NO_HIDDEN_STALE_CHAT_RETRY`, maxRetries `0`)
- provider: `deepseek`
- endpoint: official DeepSeek paid production endpoint (no base-url override)
- model: `deepseek-v4-flash-vision-exp`
- retry policy: `maxRetries = 0`
- images per call: exactly `4` (causal 4H / 1H / 15m / 5m PNGs)

## Admitted wake / single real call

The smoke opened the first governed session and drove `call_1` exactly. The runner failed closed inside `record_model_response` (response normalization) and stopped immediately. No `call_2`, no `call_3`, no retry, no replacement wake.

- admitted wake: `call_1`
- wake identity: `edef4350b093f450e9b0ddd59e9288657aee1613acceaa9e60b154152c4f8ef3`
- close time: `2024-04-09T13:05:00.000000+00:00`
- request id: `req-b80ee9db0b404c4aba07e049ff2b3bea`
- occurred at (decision time): `2024-04-09T13:05:00+00:00`
- PNG SHA-256 (4 deterministic causal charts actually attached to the request):
  - `2d8879e3acad0e48be99805d0628ac4d0593e90ed6b32bec100fa9a2120219df`
  - `8274da4f11b8e6acf0a40c06c344d2562752f50798743de9b36fc7e405b5f942`
  - `f9e5b22b0a61258f81da9cf8d7395ae469b6e59ba4a4abbbabbc278c6b0e2074`
  - `4ef00403ff8b3719ad1ac7a390dccaf60a69d19c8457934b7634a1c94aad400e`

The `call_2` and `call_3` PNG bundles were deterministically rendered but never transmitted; the smoke stopped before them.

## Root cause

The single real provider response was valid JSON with the required top-level keys, but the `numeric_claims` field was emitted as a JSON **object** (a label->value map) instead of the frozen `JIANGHE_RUNTIME_RESPONSE_V0_1` schema's required JSON **array** of `{claim, value, unit, source_reference}` records.

- response raw SHA-256: `63c0d9f78769ba34c534df2466432ebc407e0483130c683bb99a40806fefecc1`
- normalizer rejection: `numeric_claims 必须是 JSON 数组`
- audit trace: `MODEL_REQUEST_PREPARED_OFFLINE` (1) -> `MODEL_RESPONSE_RAW` (1) -> `MODEL_RESPONSE_REJECTED` (1)

The runner, Harness bridge and project normalizer all behaved as designed; the fail-closed path caught the non-conforming response before any persistence mutation and stopped the smoke. The frozen V0.1 prompt/context/renderer/schema were not modified to accommodate the provider output.

## Request accounting

- real provider model requests attempted: `1`
- real provider model requests normalized/succeeded: `0`
- retries: `0`
- hidden/auxiliary second requests: `0`
- call 4: `NO` (never possible; transport exhausts at 3 by construction)
- full 1998-call replay executed: `NO`
- request accounting result: `PASS` (exactly 1 request, correctly bounded, fail-closed on rejection)

## State / restart

- forced restart after successful call 2: `NOT REACHED` (call 2 was never reached)
- persistent trader state continuity: `NOT REACHED`
- trader identity (unchanged, pre-existing): `44039ae0212235b451ecae788901741cffce95c2436eb2f4a10e8d01422a34e9`
- no decision was persisted (no `MODEL_RESPONSE_NORMALIZED`, no working-memory mutation beyond the rejected-call audit)

## Cost

- exact provider token usage for the single call was not persisted (the bridge result carried usage in memory but the process exited on the fail-closed path before evidence serialization)
- reference estimate only (public `deepseek-v4-flash` tariff is not the verified `deepseek-v4-flash-vision-exp` tariff): far below the `CNY 3.00` ceiling; the historical `~CNY 0.10 per call` planning assumption remains a labeled estimate
- the exact bill, if needed, is provider-account evidence rather than a reconstructed project value

## Adjudication

- `PROVIDER_PATH_INTEGRITY`: `PASS` (endpoint reached, exactly 1 request, 4 PNGs, 0 retries, 0 hidden requests)
- `STATE_CONTINUITY`: `NOT REACHED`
- `REQUEST_ACCOUNTING`: `PASS`
- `SCHEMA_COMPATIBILITY`: `FAIL` (provider `numeric_claims` shape mismatch vs frozen schema)
- `TRADING_QUALITY`: `NOT EVALUATED` (out of scope for this smoke)

`SMOKE_RESULT = STOPPED FAIL-CLOSED`

The original three-call paid slot is consumed/closed and must not be re-run under its old authority. Any future real provider retest requires a new explicit Owner paid authority. Full V0.1 `1998`-call replay remains unauthorized.

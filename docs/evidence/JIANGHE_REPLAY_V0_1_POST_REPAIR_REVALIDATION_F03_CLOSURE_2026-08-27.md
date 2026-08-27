# Jianghe Replay V0.1 — Post-repair Provider Revalidation F-03 Closure

Status: `F03_OFFLINE_REPAIR_VERIFIED__EXECUTION_STILL_LOCKED`

Date: `2026-08-27`

Scope: bounded offline closure of Codex independent-review finding **F-03** plus the exact Owner-authority cost-waiver schema repair required by the same future three-call slot, all under existing Owner authority. `PROVIDER_CALLS = 0` and `PAID_SPEND = 0` for this entire package. No DeepSeek/provider/API request, no paid call, no credential read, no ACTIVE provider slot, no full V0.1 replay, and no rewrite of historical provider evidence or historical terminal machine authorities.

## F-03 cause

The parent runner durably binds wake + request before transport, and the real Harness bridge launches a child process that may issue the real provider request and only later writes `result.json`. If the subprocess times out, the child exits without a result file, the result cannot be decoded/accepted, or the parent-child handoff fails after launch, the previous code raised before `SmokeHarnessTransport` appended a `SmokeBridgeResult`, so terminal evidence could incorrectly report `provider_call_count = 0` / `network_request_count = 0` even though the child may already have attempted/sent a real provider request.

## Exact durable attempt-start mechanism

New execution-critical module `src/replay_v0_1_provider_attempt_ledger.py` owns the provider-attempt state machine:

```text
ATTEMPT_STARTED -> RESULT_RECEIVED
                -> UNKNOWN_AFTER_ATTEMPT_START
```

- `SmokeHarnessTransport.execute` durably records `ATTEMPT_STARTED` (bound to authority identity, call/sequence, logical wake-selection identity, runtime wake identity, close time, request_id, `retry_count = 0`) immediately before invoking the one-shot bridge that launches the child. If persistence of `ATTEMPT_STARTED` fails, the exception propagates before `bridge.execute`, so the child process is NOT launched.
- On a valid bridge result, the attempt transitions to `RESULT_RECEIVED` and persists all mechanically available non-secret metadata (provider, model, provider_request_id, request_count, image_count, finish_reason, token_usage, bridge status). No unavailable metadata is fabricated.
- On any post-attempt-start failure (subprocess timeout, missing result file, malformed/undecodable result, or equivalent handoff failure), the attempt transitions to `UNKNOWN_AFTER_ATTEMPT_START` with a reason.

The ledger references (does not duplicate) the durable `Fixed5MWakeLedger` wake/request binding and is the single clear owner of provider-attempt accounting. It is stored at `state_dir/provider_attempts.sqlite3` and survives restart/persistence (it is a file).

## Exact UNKNOWN_AFTER_ATTEMPT_START semantics

`UNKNOWN_AFTER_ATTEMPT_START` means the project cannot prove whether the provider received/completed the request. It is NEVER represented as zero provider/network calls: terminal evidence reports:

- `provider_attempt_count` = total attempts started;
- `provider_attempt_state` = per-call attempt state map;
- `unknown_after_attempt_start_count`;
- `known_result_count` (confirmed `RESULT_RECEIVED` completions);
- `slot_requires_adjudication = true` when any attempt is unknown;
- compatibility `provider_call_count` / `network_request_count` = total attempts started when the attempt ledger is present (conservative upper bound), with clearly documented semantics. When no attempt ledger exists (mock/no-network path), they fall back to the transport's recorded calls.

No unknown started attempt is presented as "nothing happened".

## Terminal-barrier behavior

An `UNKNOWN_AFTER_ATTEMPT_START` immediately terminates the slot:

- no retry, no replacement wake, no next call, no call 4, no automatic rerun;
- the transport sets an explicit `_unknown_attempt_blocked` flag so any further `execute` raises a clear terminal-barrier error before any child launch;
- the runner's exception-driven loop stops before the next wake;
- terminal evidence sets `slot_requires_adjudication = true` so the slot is separately adjudicated.

No distributed-locking infrastructure was added; the barrier is the narrowest robust local mechanism consistent with the current single-user architecture.

## Timeout / no-result / malformed / valid tests

Added deterministic zero-network regressions in `tests/test_replay_v0_1_provider_smoke.py`:

1. `ProviderAttemptLedgerTests` — durable ATTEMPT_STARTED before any result; valid transition to RESULT_RECEIVED; transition to UNKNOWN_AFTER_ATTEMPT_START; terminal states cannot transition; retry_count must be zero.
2. `SmokeHarnessTransportAttemptTests` — attempt-start persisted before child launch; attempt-persistence failure prevents child launch (launch count 0); child timeout → UNKNOWN + exact wake/request/authority identity retained + no zero accounting + no second child launch; no-result-after-launch → UNKNOWN; malformed result → UNKNOWN; valid result → RESULT_RECEIVED with normal path unchanged.
3. `ProviderAttemptEvidenceTests` — terminal evidence distinguishes no-attempt-ever-started (zero, not adjudication), known result, and unknown-after-attempt-start (non-zero, `slot_requires_adjudication`); an unknown attempt in a real driven orchestrator run stops before call 2 and produces terminal evidence with `provider_attempt_count = 1`, `unknown_after_attempt_start_count = 1`, `provider_call_count = 1`, `admitted_wake_count = 1`.
4. `CostWaiverAuthorityTests` — forward waiver authority loads; ACTIVE requires owner payment confirmation; explicit sentinel required; deleting `max_spend_cny` from an old authority still fails; waiver cannot be applied to historical V0_2; old numeric ACTIVE rules remain strict; historical terminal authorities remain readable.

## New forward authority version / Owner cost-waiver encoding

`src/replay_v0_1_smoke_authority.py` adds forward versions:

- `SMOKE_AUTHORITY_VERSION_V0_3` / `SMOKE_RETEST_AUTHORITY_VERSION_V0_3`;
- explicit ceiling modes `CNY_CEILING_MODE_NUMERIC` and `CNY_CEILING_MODE_WAIVED`, with sentinel `OWNER_CNY_CEILING_WAIVED`.

Only the forward V0_3 form may encode `OWNER_CNY_CEILING_WAIVED` (both `cny_ceiling_mode` and `max_spend_cny` must be the explicit sentinel). It still requires `owner_payment_confirmation = true`, `max_provider_calls = 3`, `max_retries = 0`, `images_per_call = 4`, `restart_after_call = 2`, two identities for all three wakes, and full replay false. No CNY budget calculator was added; token/usage evidence is retained after execution. `PROJECT_DIRECTION.md` default cost doctrine was not changed.

### Historical authority compatibility

- Historical V0_1 behavior unchanged; existing V0_2 behavior unchanged;
- historical terminal authorities remain readable and immutable;
- the forward `cny_ceiling_mode` field is included in the canonical payload (and identity) ONLY for V0_3 authorities, so historical V0_1/V0_2 identities are byte-identical;
- missing/invalid `max_spend_cny` is never silently interpreted as a waiver.

## F-01 / F-02 non-regression

- F-01: preflight carries logical + runtime identity from actual `ReplayStepBinding`; pre-call guard and post-drive verification independently check both; PASS evidence retains both; logical-only/runtime-only tampering rejected — all preserved (existing tests pass).
- F-02: request-bound wake survives response-normalization failure; first malformed response records exactly one admitted/request-bound wake; later malformed response records every actually request-bound wake; no fabricated decision identity — all preserved (existing tests pass).

## No semantic drift

Unchanged: product/slice, wake policy, provider/model, renderer, context-selection semantics, Jianghe trading semantics, persistent-memory semantics, `retry = 0`, restart after call 2, active response schema `JIANGHE_RUNTIME_RESPONSE_V0_2`, active prompt `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`. Full V0.1 execution authority untouched.

## Execution-critical binding

`src/replay_v0_1_smoke_guard.py::EXECUTION_CRITICAL_PATHS` now includes `src/replay_v0_1_provider_attempt_ledger.py`. A regression proves the new module is in the binding surface and that working-tree drift on it is detected.

## Verification

- Focused suites: `tests.test_replay_v0_1_provider_smoke` (62 tests) plus wake-identity, wake-ledger, integrity, restart, structured-memory, normalizer, prompt, orchestrator, runtime suites — all pass.
- Full suite: `python -m unittest discover -s tests` — `632` tests OK (`8` skipped).
- `python -m compileall -q src tools tests` — PASS.
- `python tools/check_authority_consistency.py` — `AUTHORITY_CONSISTENCY = PASS`.
- `git diff --check` — PASS.
- `test_execution_code_bound_passes_at_clean_head` passes on the committed tree by construction.

## Implementation commit

- Implementation + tests: commit `6dd6a5aae6686ea2edac5a236bc9bd734727a44b`
- Evidence + current-state record (this file / `CURRENT_STATE.md`): follow-up commit containing this artifact.

## Execution state

- `PROVIDER_CALLS = 0`; `PAID_SPEND = 0`; no machine authority was created/resealed/activated.
- Owner three-call revalidation remains REQUIRED with `MAX_PROVIDER_CALLS = 3`, `MAX_RETRIES = 0`, and `CNY_CEILING = OWNER_WAIVED_FOR_THIS_EXACT_SLOT`.
- `FULL_V0_1_1998_CALL_REPLAY` remains LOCKED.
- Execution remains LOCKED pending a fresh independent high-assurance review of the F-03 closure and the forward authority waiver path, then a newly resealed forward V0_3 two-identity machine authority, then final immediate pre-execution refresh/verification.

This offline repair does NOT claim the real-provider path has been revalidated.

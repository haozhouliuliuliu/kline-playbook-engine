# Jianghe Replay V0.1 — F-02 Closure Final Independent Pre-execution Review

Status: `BLOCKED_BY_MATERIAL_PREEXECUTION_DEFECT`

Date: `2026-08-27`

Review baseline: current GitHub `main` commit
`b77ca4bedf7c6c0e9ea1ad0526c8b583587ed054`.

No provider/API request, secret read, authority creation/reseal/activation,
paid call, full V0.1 execution, historical-evidence rewrite, or
`CURRENT_STATE.md` modification occurred during this review.

## Verdict

`BLOCKED_BY_MATERIAL_PREEXECUTION_DEFECT`

F-01 and F-02 are independently closed, including the requested real
no-network failure windows. Per the Owner's in-review clarification, the CNY
3.00 ceiling need not be mechanically enforced and is not a defect in this
review. The complete paid path is nevertheless not acceptable for fresh slot
preparation because a real request may be issued by the child bridge process
and then become unaccounted if that process times out or fails before writing
its result file.

The previous three-call / zero-retry / CNY 3.00 authority was unconsumed at the
review baseline. The Owner subsequently superseded the CNY ceiling for this exact
three-call revalidation; that later scoped Owner decision is canonical on current
main and does not change this review's F-03 finding.

This review does not activate or execute a slot, and full V0.1 remains locked.

## F-01 independently reconfirmed closed

- Preflight emits ordered `call_1`/`call_2`/`call_3` entries containing both
  identities and close time directly from `ReplayStepBinding`.
- The guard runs after wake registration and before request preparation,
  request binding, and transport execution. Logical and runtime identity checks
  are separate and fail closed.
- Post-drive verification rechecks both identities, count, and ordering.
- Tamper coverage rejects logical-only and runtime-only mismatch, swapped
  logical identities, wrong logical identity at the same close time, reordered
  bindings, and an unknown fourth sequence.
- PASS evidence retains both identities.

## F-02 independently closed

The repair uses the existing durable `Fixed5MWakeLedger` request-binding state,
not a second competing state store. Request binding occurs before transport; the
ledger holds the logical identity, runtime identity, close time, request ID,
sequence, and `retry_count = 0`.

I independently ran the real deterministic failure path in the provider-smoke
test suite:

1. A malformed first response after transport gives one durable bound wake,
   both identities and request ID, no decision identity, and no fabricated
   future wake.
2. A malformed later response after one prior success gives two durable bound
   wakes; only the successful first wake has a decision identity, while the
   failed second wake has both identities and no fabricated decision identity.

The terminal failure-evidence builder reads bound wakes from the ledger, so the
admitted/request-bound count now matches actual calls in those cases.

## Material defect — F-03: child-bridge loss can hide an already-sent request

The runner binds the governed wake in the durable ledger before transport, so
the wake pair itself survives a failure. But the real `HarnessOneShotBridge`
starts a child process which can call the provider and only afterwards write
`result.json`. If `subprocess.run(..., timeout=300)` raises, or the child exits
without the result file after issuing a request, `HarnessOneShotBridge.execute`
raises before returning a `SmokeBridgeResult`.

`SmokeHarnessTransport.execute()` appends to `transport.calls` only after
`bridge.execute()` returns. The terminal evidence therefore derives
`provider_call_count` and `network_request_count` as zero from
`len(transport.calls)`, even though the ledger shows one request-bound wake and
the child may already have sent the provider request. There is no durable
`NETWORK_ATTEMPT_STARTED`-equivalent record before child-process launch, no
unknown-attempt accounting state, and no timeout/no-result regression test.

This ambiguity is material: a later operator cannot distinguish “no request
left the machine” from “request left but the bridge result was lost.” It could
lead to incorrect accounting and an unsafe retry/reseal decision after a paid
attempt. The zero-retry rule cannot correct an unknown attempt after the fact.

## Required repair before fresh machine-authority preparation

1. Before launching the real bridge child process, durably record a
   request-attempt-started event bound to the wake pair, request ID, authority
   identity and zero-retry policy. It must be readable by the terminal path.
2. On a bridge timeout, missing result file, invalid result, or parent/child
   handoff failure after launch, terminal evidence must report the attempt as
   `UNKNOWN_AFTER_ATTEMPT_START` (or an equivalently fail-closed state), retain
   both wake identities, and never report it as zero network/provider calls.
3. Make the state an explicit terminal barrier: it must consume/close the
   attempted slot and forbid retry, replacement wake, reseal-as-unattempted, or
   subsequent call until separately adjudicated.
4. Retain any available stdout/stderr/result metadata without treating their
   absence as proof that no request occurred; never expose secrets.
5. Add deterministic tests for child timeout and no-result-after-launch. Assert
   durable attempt-start evidence, accurate non-zero/unknown attempt accounting,
   no call 2, and no permitted rerun. Re-run independent pre-execution review
   before any authority is resealed.

## Other paid-boundary results

- Future two-identity authorities still require both identities; historical
  runtime-only terminal authorities remain immutable and cannot be pending/active.
- Execution-code binding covers the real ledger, orchestrator, authority,
  bridge, guard, renderer, preflight, runner, and Harness bridge/patch files.
- ACTIVE authority is checked before bridge construction, credential access, or
  network capability. The credential seam is only `DEEPSEEK_API_KEY`; no value
  was read.
- Production endpoint override is not accepted through the loopback-only test
  override mechanism.
- Transport has exactly three four-image bundles, zero retries, and refuses a
  fourth request. Restart remains after call 2; provider metadata survives
  normalization failure; active response/prompt contracts remain V0.2/V0.3.
- Structured memory, model-visible carry-forward, restart continuity, future
  leakage, and outcome/PnL rejection remain covered by the passing offline
  suites.

## Verification performed

- Required focused deterministic suites: `91` passed.
- Full suite: `python -m unittest discover -s tests -v` — `607` passed,
  `8` skipped.
- `python -m compileall -q src tools tests` — passed.
- `python tools/check_authority_consistency.py` —
  `AUTHORITY_CONSISTENCY = PASS`.
- `git diff --check` — passed.

No provider/network test was run.

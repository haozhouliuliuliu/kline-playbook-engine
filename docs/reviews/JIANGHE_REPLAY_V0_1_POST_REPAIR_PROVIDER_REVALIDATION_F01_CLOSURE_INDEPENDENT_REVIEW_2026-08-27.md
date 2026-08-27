# Jianghe Replay V0.1 — F-01 Closure Independent Review

Status: `BLOCKED_BY_MATERIAL_PREEXECUTION_DEFECT`

Date: `2026-08-27`

Review baseline: current GitHub `main` commit
`943cb5b307ef5e45156e37fc6f2816945c29c75e`.

No provider/API request, credential read, machine-authority creation/reseal,
slot activation, paid call, full replay, historical-evidence rewrite, or
`CURRENT_STATE.md` modification was performed.

## Verdict

`BLOCKED_BY_MATERIAL_PREEXECUTION_DEFECT`

The original F-01 identity-propagation defect is repaired in the normal path:
preflight uses the actual governed `ReplayStepBinding`; the pre-call guard and
post-drive check independently verify both identities; and successful evidence
retains both identities. However, the new fail-closed evidence path still loses
the identity pair of the current wake if its provider request has already
occurred but `run_wake_step()` fails before returning a complete
`ReplayStepBinding`.

Therefore the implementation cannot yet meet the required durable
post-provider-failure observability rule, and a new V0.2 two-identity machine
authority must not be prepared/resealed from this revision.

## F-01 normal-path closure findings

The following portions of F-01 are independently confirmed:

1. `tools/preflight_replay_v0_1_provider_smoke.py` builds the ordered
   `call_1`, `call_2`, `call_3` blueprint directly from actual
   `ReplayStepBinding` objects. Each entry includes
   `logical_wake_selection_identity`, runtime `wake_identity`, and
   `close_time`; no second identity formula is used.
2. `src/replay_v0_1_orchestrator.py::run_wake_step()` registers the governed
   wake and then invokes the optional wake guard before observation/model
   request construction, request binding, or transport execution.
3. `tools/run_replay_v0_1_provider_smoke.py` independently compares logical
   and runtime identities. It rejects either single-field mismatch, swapped
   logical identities, wrong logical identity at an unchanged close time,
   reordered bindings, and an unknown fourth sequence.
4. PASS evidence contains both identities for every completed call.
5. V0.2 authority validation still requires both identities; historical
   runtime-only authorities remain readable only as terminal `REVOKED` records
   and cannot become `PENDING`/`ACTIVE`.
6. Execution-commit binding covers the changed execution paths, including
   `src/replay_v0_1_orchestrator.py`,
   `tools/preflight_replay_v0_1_provider_smoke.py`, and
   `tools/run_replay_v0_1_provider_smoke.py`.

No trading semantics, slice, wake policy, provider/model, context/renderer
semantics, response schema, prompt, retry policy, or restart-after-call-2
behavior was changed by the F-01 repair. Active contracts remain
`JIANGHE_RUNTIME_RESPONSE_V0_2` and
`KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`.

## Material defect — F-02: fail-closed evidence omits an already-requested wake

`ReplayV01Orchestrator.run_wake_step()` performs these relevant operations in
order:

1. registers the governed wake;
2. passes the pre-call identity guard;
3. prepares and binds the model request;
4. executes the transport/provider request;
5. records/normalizes the response;
6. only at the very end appends a `ReplayStepBinding`.

The runner updates its local `bindings` only **after**
`orchestrator.run_wake_step(step)` returns successfully. If the provider has
returned a malformed response and normalization/recording raises at step 5,
the request has already happened but the current wake has not reached step 6.
The outer failure handler then writes:

- `admitted_wake_count = len(bindings)`; and
- `admitted_wakes = _build_admitted_wake_evidence(bindings)`.

Consequently, it records only prior fully completed decisions and omits the
logical/runtime identity pair of the current admitted, request-bound wake. For
a first-call schema failure this creates `provider_call_count = 1` but an empty
`admitted_wakes` array; for a later failure it omits the final actually
requested call. Provider/request metadata may remain in local runtime state,
but the terminal fail-closed evidence required for the slot does not
reconstruct the identity pair of every actually admitted wake.

This violates the required condition: after call N fails after admission,
fail-closed evidence must retain both identities for all actually admitted
wakes up to N, without fabricating a future/unadmitted wake.

The current test named
`test_fail_closed_evidence_after_admitted_wake_retains_both_identities` only
passes preconstructed completed bindings to the evidence helper. It does not
exercise the real failure interval after transport execution and before
`ReplayStepBinding` append. The full suite therefore cannot detect F-02.

## Required repair before fresh V0.2 authority preparation

1. Persist or expose an admitted/request-bound wake record immediately after
   pre-call admission and request binding, before transport execution. That
   record must carry both identities, close time, sequence/call identity, and
   request identifier as available.
2. Build fail-closed `admitted_wakes` from those actually admitted/request-bound
   records (or an equivalently durable ledger export), not only from completed
   `ReplayStepBinding` objects.
3. Keep unadmitted wakes absent. Do not invent a decision identity or provider
   result for a wake whose response normalization failed.
4. Add a deterministic no-network regression that makes the first and a later
   transport response fail strict normalization after the transport has been
   called. Assert terminal evidence has the exact admitted wake count and both
   logical/runtime identities for every requested wake, with no extra record.
5. Re-run focused and full deterministic verification and obtain a fresh
   independent review before any V0.2 machine authority is resealed.

## Verification performed

- Required focused suites: `88` tests passed.
- Full suite: `python -m unittest discover -s tests -v` — `604` passed,
  `8` skipped.
- `python -m compileall -q src tools tests` — passed.
- `python tools/check_authority_consistency.py` —
  `AUTHORITY_CONSISTENCY = PASS`.
- `git diff --check` — passed.

No network/provider test was run.

## Authorization boundary

The Owner-approved `MAX_SPEND_CNY = 3.00`, three-call, zero-retry envelope was
not reconsidered and is not consumed by this review. This review does not
authorize authority reseal, slot activation, provider execution, or the full
V0.1 replay.

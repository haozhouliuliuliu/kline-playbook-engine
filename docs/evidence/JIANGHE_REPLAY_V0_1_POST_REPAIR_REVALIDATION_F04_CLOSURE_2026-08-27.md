# Jianghe Replay V0.1 — Post-repair Provider Revalidation F-04 Closure

Status: `F04_OFFLINE_REPAIRED__FRESH_INDEPENDENT_REVIEW_REQUIRED`

Date: `2026-08-27`

Scope: zero-provider-call repair of the material ordinary defect identified by the first fresh independent review of the F-03 closure. This document records no ACTIVE slot, no provider request, no credential read, no paid spend, and no historical-authority mutation.

## Finding

After a real bridge child returned a result, `SmokeHarnessTransport` could fail while durably changing `ATTEMPT_STARTED` to `RESULT_RECEIVED`. If the compensating `UNKNOWN_AFTER_ATTEMPT_START` write also failed, the row remained `ATTEMPT_STARTED`; the in-process transport had not set its terminal barrier and could launch call 2. Terminal evidence conservatively counted that row as an attempt but did not require adjudication.

## Repair

Execution commit: `12d7000801a3711e5e7ac22400a315a2c66e0d16`.

- `SmokeHarnessTransport` now sets its in-process terminal barrier before every best-effort post-launch unknown transition. Therefore a failed unknown-state write cannot permit a second child launch in the same process.
- Failure to persist `RESULT_RECEIVED` sets the same terminal barrier, attempts the unknown transition without masking the persistence error, and raises a fail-closed terminal error. The durable start record remains conservative evidence if that secondary transition also fails.
- `ProviderAttemptLedger.unresolved_attempt_started_count()` exposes durable starts without a terminal handoff state.
- Runner evidence retains the actual ledger state, counts residual `ATTEMPT_STARTED` rows as nonzero unresolved attempts, and sets `slot_requires_adjudication = true` for either explicit unknown or unresolved start. It does not fabricate whether the provider received the request.

## Regression and verification

The new deterministic double-failure regression uses a normal one-shot bridge result plus a ledger proxy that persists `ATTEMPT_STARTED` but rejects both terminal writes. It proves one child launch, residual attempted state, terminal blocking of the second call, no retry, and no replacement wake. A separate evidence regression proves a residual start yields nonzero attempt accounting and adjudication required.

Completed with no provider/network call:

- `python -m unittest tests.test_replay_v0_1_provider_smoke -v` — 66 passing;
- `python -m compileall -q src tools tests` — passing;
- `python tools/check_authority_consistency.py` — `AUTHORITY_CONSISTENCY = PASS`;
- `git diff --check` — passing.

The exact three-call revalidation remains locked pending a new independent high-assurance review on a freshly refreshed canonical `main`.

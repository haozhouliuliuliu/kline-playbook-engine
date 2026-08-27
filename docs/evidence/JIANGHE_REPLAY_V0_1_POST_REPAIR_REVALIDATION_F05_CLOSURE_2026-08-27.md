# Jianghe Replay V0.1 — Post-repair Revalidation F-05 Closure (offline)

Status: `OFFLINE_REPAIRED__ZERO_PROVIDER_ATTEMPT__FRESH_INDEPENDENT_REVIEW_REQUIRED_BEFORE_PAID_EXECUTION`

Date: `2026-08-27`

Work package: `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

## Scope

Close the material pre-execution defect discovered at the final gate of the
post-repair three-call revalidation, immediately before any real execution.
This document records **zero provider attempts, zero credential reads, zero
network requests, zero paid spend**, and no historical-authority mutation.

## Exact defect (F-05)

On the committed tree at the pre-execution gate (after dataset restoration,
final zero-cost preflight PASS, and V0_3 authority activation), running the
real harness path of the smoke runner:

```text
python tools/run_replay_v0_1_provider_smoke.py --transport harness ... (ACTIVE V0_3 authority)
```

failed before any bridge child launch with:

```text
NameError: name 'timezone' is not defined
```

Root cause: `tools/run_replay_v0_1_provider_smoke.py` constructs the durable
provider-attempt identities (`attempt_identities`) with
`binding.close_time.astimezone(timezone.utc)`, but the module never imported
`timezone`. The path is only reachable with `--transport harness` (the real
provider bridge), so the mock/fake-transport unit tests never executed it and
prior F-01..F-04 reviews / the F-04 independent review did not catch it.

## Why zero provider attempts

The `NameError` occurs while building `attempt_identities` in the runner, before
`SmokeHarnessTransport` is constructed and before any `ATTEMPT_STARTED` ledger
write or bridge child launch. The durable attempt ledger
(`provider_attempts.sqlite3`) in the run state directory recorded **0 rows in
`provider_attempts`**. No provider capability, network client, or credential
read was ever reached.

## Repair (offline, execution-critical)

Commit `c5338aa` (execution-critical change):

1. add `from datetime import timezone` to `tools/run_replay_v0_1_provider_smoke.py`;
2. extract the harness attempt-identity construction into a module-level,
   unit-testable helper `_build_attempt_identities(authority)`;
3. `main()` calls `_build_attempt_identities(authority)`.

Deterministic regression added in `tests/test_replay_v0_1_provider_smoke.py`:

- `ProviderAttemptEvidenceTests.test_harness_attempt_identity_construction_is_timezone_aware`
  — asserts exactly three attempt identities, exact call/sequence names, both
  wake identities, and timezone-aware `+00:00` close times matching the
  authority wake bindings (UTC, microseconds).

## Verification (deterministic, zero cost)

- `python -m unittest tests.test_replay_v0_1_provider_smoke` — 67 passing;
- `python -m unittest discover -s tests` — 636 passing, 8 skipped, exit 0;
- `python -m compileall -q src tools tests` — passing;
- `python tools/check_authority_consistency.py` — `AUTHORITY_CONSISTENCY = PASS`;
- `git diff --check` — clean.

## Authority state after this repair

- The V0_3 RETEST authority was activated only transiently for the failed
  pre-execution attempt; the slot was not consumed (0 provider attempts).
- The authority file is restored to the committed non-ACTIVE form
  (`PENDING_OWNER_PAYMENT_CONFIRMATION`, identity `24d2409a…c94d`).
- Because execution-critical code changed (F-05 fix), the machine authority must
  be re-sealed/activated against the new execution commit only after a fresh
  isolated high-assurance review, per `PROJECT_GOVERNANCE.md` and the Owner
  three-call revalidation authority.

## Next gate (mandatory)

A fresh isolated high-assurance independent review of the F-05 closure and the
updated execution commit is required before any paid provider call. The exactly
once three-call slot (max 3 calls, 0 retries, no call 4, no replacement wake,
Owner CNY-ceiling waiver) remains authorized by the Owner but is LOCKED pending
that review.

# Jianghe Replay V0.1 — Post-repair Provider Revalidation F-04 Closure Independent Review

Verdict: `ACCEPTABLE_FOR_FRESH_THREE_CALL_SLOT_PREPARATION`

Date: `2026-08-27`

Review basis: fresh isolated LANE B worktree created from canonical `main` commit `66d2530f3c3633e130e5d57922b4a725e7bf8aef`. The reviewer did not trust LANE A's summary, did not modify authority/state files, did not create or activate a machine slot, did not read or output a credential, and made zero provider/network calls.

## Scope independently inspected

- exact Owner three-call authority, F-03/F-04 closure evidence, and current state;
- the actual runner -> `SmokeHarnessTransport` -> `HarnessOneShotBridge` -> TypeScript bridge -> result/normalization path;
- strict production bridge signature (no fake-only `attempt_identity` argument);
- F-01 two-identity preflight, pre-call and post-drive proof;
- F-02 request-bound wake evidence on normalization rejection;
- F-03/F-04 durable start, known result, unknown/residual-start terminal behavior and evidence reconstruction;
- V0.3 explicit scoped CNY-waiver serialization while preserving historical V0.1/V0.2 numeric behavior;
- execution-code binding, credential/network gate, four-PNG bound, zero retries, restart after call 2, and hard prohibition of a fourth call.

## Independent result

`ATTEMPT_STARTED` is durable before child launch. Explicit unknown attempts and residual durable starts without a terminal handoff are both nonzero attempted calls requiring adjudication. The post-result persistence double-failure regression proves the transport blocks a second child launch even when neither terminal ledger write succeeds. The strict bridge-signature regression proves ledger metadata is retained in the parent and not passed to the production bridge. No material pre-execution defect remained in the inspected surface.

## Independent checks

- `python -m unittest tests.test_replay_v0_1_provider_smoke -v` — 66 passing;
- `python -m unittest discover -s tests -v` — passing, exit 0;
- `python -m compileall -q src tools tests` — passing;
- `python tools/check_authority_consistency.py` — `AUTHORITY_CONSISTENCY = PASS`;
- `git diff --check` — passing; isolated worktree clean.

This acceptance does not activate a slot or authorize any call beyond the existing Owner-approved exact three-call revalidation. Final zero-cost preflight, a fresh V0.3 authority, and the immediate consequential-action check remain required before execution.

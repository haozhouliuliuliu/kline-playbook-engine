# Jianghe Replay V0.1 — Post-repair Provider Revalidation Independent Review

Status: `BLOCKED_BY_MATERIAL_PREEXECUTION_DEFECT`

Date: `2026-08-27`

Reviewer scope: independent, pre-execution review of current GitHub `main` at
`133f55400ab03bde1ef8c23b57ddd24f0b201f07`. No provider/API request, secret
read, provider-slot activation, spend, historical-evidence rewrite, or
`CURRENT_STATE.md` change was performed.

## Verdict

`BLOCKED_BY_MATERIAL_PREEXECUTION_DEFECT`

The repaired response/prompt/memory implementation is substantially correct in
the deterministic offline path, but the real-provider preparation path does
not prove the required logical wake-selection identity. A fresh V0_2
two-identity authority therefore cannot yet safely prepare a paid three-call
slot.

This review does not authorize a provider call or the full V0.1 replay.

## Current authority check

- The Owner has already required the fresh revalidation:
  `POST_REPAIR_REAL_PROVIDER_REVALIDATION = REQUIRED`.
- It remains execution-locked until a fresh exact positive CNY ceiling and a
  newly resealed machine authority exist.
- The new authority must bind three logical/runtime identity pairs, three
  maximum calls, zero retries, four images per call, and restart after call 2.
- Historical runtime-only terminal authorities remain immutable and may not be
  reactivated.

These statements were checked against
`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION_OWNER_DECISION_2026-08-27.md`,
`CURRENT_STATE.md`, and the current machine-authority implementation.

## Material finding — F-01: logical identity is absent from preflight and runtime proof

The two-identity contract is correctly represented in the core data model:

- `src/fixed_5m_wake_ledger.py` derives
  `logical_wake_selection_identity` only from selection-invariant inputs;
- `ReplayStepBinding` in `src/replay_v0_1_orchestrator.py` carries both
  `logical_wake_selection_identity` and runtime `wake_identity`;
- `src/replay_v0_1_smoke_authority.py` requires both identities on all three
  wakes for future V0_2 PENDING/ACTIVE authority, while keeping historical
  runtime-only authorities terminal-only.

However, the boundary that drives a real provider slot drops the logical side:

1. `tools/preflight_replay_v0_1_provider_smoke.py` emits each `smoke_wakes`
   blueprint item with `wake_identity` and `close_time`, but omits
   `logical_wake_selection_identity`.
2. `tools/run_replay_v0_1_provider_smoke.py::_verify_smoke_wake_bindings()`
   compares only `binding.wake_identity` to the authority. It never compares
   `binding.logical_wake_selection_identity` to
   `expected.logical_wake_selection_identity`.
3. The runner PASS evidence emits `wake_identity` for each call but omits the
   actual logical identity. Consequently, the resulting durable evidence cannot
   establish that the three calls used the intended same logical opportunities.

This contradicts the revalidation decision's explicit acceptance requirement
that both identities match the fresh authority and that the logical identities
match the intended same first-three opportunities. Runtime identity alone
cannot substitute for that proof because it deliberately changes when the
approved prompt/trader/runtime identity changes.

The focused runner test only tests runtime wake binding, so it cannot detect
this omission. The full test suite passing does not discharge this
execution-critical requirement.

## Required correction before any fresh slot is prepared

1. Add `logical_wake_selection_identity` to each preflight `smoke_wakes`
   blueprint record, sourced from the actual `ReplayStepBinding`.
2. In `_verify_smoke_wake_bindings()`, fail closed unless both the actual
   logical identity and runtime identity exactly equal their respective sealed
   authority values for calls 1–3.
3. Include both identities in every PASS and fail-closed evidence record that
   reports an admitted wake, so post-run evidence can prove the pair.
4. Add deterministic regression tests that independently tamper the logical
   identity while leaving the runtime identity intact, and confirm the runner
   rejects it; also assert preflight and emitted evidence retain both fields.
5. Re-run the required deterministic checks and conduct a fresh independent
   pre-execution review on the repaired execution path. Only after that review
   may a new V0_2 PENDING authority be resealed; ACTIVE still separately needs
   the Owner's positive finite CNY ceiling and payment confirmation.

## Other audit results

### Response contract and memory

`JIANGHE_RUNTIME_RESPONSE_V0_2` is active and strict. The six required
CURRENT STATE SNAPSHOT fields are present, have strict allowed types, reject
missing/unknown/malformed forms, and remain distinct from frozen V0.1
identities. Recursive outcome/PnL/self-evaluation rejection remains in place.

The accepted normalized fields are projected directly into
`DS_WORKING_MEMORY`; no rationale parsing is used. They are explicitly
replaced/cleared by the next accepted snapshot, exposed in the next request,
and survive the tested store reopen/restart path. The forced restart after call
2 is implemented before call 3.

### Prompt and source fidelity

The active prompt is `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`. It requires the
full snapshot, explicit carry-forward/revision/clearing semantics, strict JSON
serialization, conservative handling of insufficient evidence, project-owned
scheduling, and no hidden reasoning. Its template is structurally unambiguous
for the required fields.

The JH-CLM-034-002 correction is evaluator-side, registry-grounded, and
classifies the known management-to-pre-entry misuse as a finding. It does not
rewrite historical responses or add a generalized semantic classifier.

### Historical compatibility and active stale-constant check

Historical terminal runtime-only authorities remain readable and cannot be
PENDING/ACTIVE. No migration silently upgrades historical wake hashes. The
active preflight and runner import `RESPONSE_SCHEMA_VERSION`,
`NORMALIZER_IDENTITY`, and `TRADING_ONLY_PROMPT_CONTRACT` from the active
modules, so their prompt/schema/trader bindings target V0.2/V0.3 rather than
the historical V0.1/V0.2 constants. The Harness bridge keeps one request,
exactly four PNG images, and zero retries.

The missing logical-identity propagation described in F-01 is the exception:
it prevents the otherwise active path from establishing the full required
two-identity observability claim.

## Deterministic verification performed

- Focused structured-memory, normalizer, prompt, wake-identity,
  provider-smoke authority/runner, restart-continuity, source-fidelity, and
  replay-integrity tests: `97` passed.
- Canonical full suite: `python -m unittest discover -s tests -v` — `590`
  passed, `8` skipped.
- `python tools/check_authority_consistency.py` —
  `AUTHORITY_CONSISTENCY = PASS`.
- `python -m compileall -q src tools tests` — passed.
- `git diff --check` — passed.

No provider/network test was run.

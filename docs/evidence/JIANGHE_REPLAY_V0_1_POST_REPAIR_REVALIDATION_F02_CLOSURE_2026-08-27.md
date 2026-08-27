# Jianghe Replay V0.1 — Post-repair Provider Revalidation F-02 Closure

Status: `F02_OFFLINE_REPAIR_VERIFIED__EXECUTION_STILL_LOCKED`

Date: `2026-08-27`

Scope: bounded offline closure of Codex independent-review finding **F-02** under existing Owner authority. `PROVIDER_CALLS = 0` for this entire package. No DeepSeek/provider/API request, no paid call, no credential read, no ACTIVE provider slot, no full V0.1 replay, and no rewrite of historical provider evidence or historical terminal machine authorities.

## F-02 cause

If a provider request has already happened but strict response normalization/recording fails before `run_wake_step()` appends a complete `ReplayStepBinding`, the terminal fail-closed evidence was built only from prior completed bindings and omitted the current already-requested wake. A first-call malformed response could therefore show one provider request but zero admitted-wake identity records, and a later failure could omit the final actually-requested wake.

## Exact repair

The runner's terminal FAIL evidence is now based on actually request-bound wakes read from the existing durable wake ledger, not only on completed `ReplayStepBinding` objects.

- `src/fixed_5m_wake_ledger.py`: added the narrow public read seam `bound_wakes()` on both `Fixed5MWakeLedger` and the read-only `WakeLedgerArchive`. A wake counts as admitted/request-bound only when it has a non-null bound `request_id` (durably persisted by `bind_request()` before transport execution). Unbound/future wakes never appear. No second competing admission ledger was created.
- `tools/run_replay_v0_1_provider_smoke.py`:
  - `_read_bound_wakes(state_dir)` reads all actually request-bound wakes from `state_dir/wake_ledger.sqlite3` via the archive;
  - `_build_bound_wake_evidence(bound_wakes, completed_bindings)` retains per admitted wake: `call`/`sequence`, `logical_wake_selection_identity`, `wake_identity`, `close_time`, `request_id`, `retry_count`; `decision_identity`/`observation_identity` are included ONLY when a completed binding (a normalized decision) actually exists — nothing is fabricated;
  - `_assemble_fail_evidence(...)` builds the terminal FAIL payload from those request-bound wakes (`admitted_wake_count`, `admitted_wakes`), with `provider_call_count` from the actual transport call list and `retry_count = 0`.

The durable request-bound source used is the existing `Fixed5MWakeLedger` (via `WakeLedgerArchive`), which persists both identities, close time, sequence, `request_id` and `retry_count` before transport execution.

## Required behavior now proven

- First provider call occurs → malformed response fails normalization → `provider_call_count = 1`, `admitted_wake_count = 1`, `admitted_wakes` contains the exact `call_1` logical/runtime/request identity, no `call_2`.
- `call_1` succeeds → `call_2` provider request occurs → `call_2` response fails normalization → `provider_call_count = 2`, `admitted_wake_count = 2`, evidence contains exact `call_1` + `call_2` records, no `call_3`.
- No retry, no replacement wake, no call 4, no fabricated decision identity.

## Regressions (real failure window, zero network)

Added `ProviderSmokeFailClosedEvidenceTests` in `tests/test_replay_v0_1_provider_smoke.py`, driving the real orchestrator with a scripted no-network transport:

- `test_first_call_post_transport_normalization_failure` — call_1 passes the wake guard, request is bound, transport invoked exactly once, malformed strict-schema response fails normalization, exactly one admitted/request-bound wake with both identities + `request_id` retained, no decision identity fabricated, no second call.
- `test_later_call_post_transport_normalization_failure` — call_1 valid (decision identity present), call_2 malformed, exactly two request-bound wakes retained, call_2 must not fabricate a decision identity, no call_3.
- `test_bound_wakes_survive_restart_model` — the durable request-bound ledger is a file; reopening it after the runtime is closed (restart/persistence model) yields the same wake identity pairs.

Existing F-01 regressions remain: runtime-only tamper rejected, logical-only tamper rejected, swapped logical identities rejected, unadmitted future wakes absent, no retries, no replacement wake, no call 4, historical terminal authorities unchanged, future PENDING/ACTIVE V0_2 authority still requires both identities.

## Paid-boundary sweep

Inspected the complete future paid provider boundary (Owner authority, `PROJECT_DIRECTION` cost requirements, authority loader, smoke guard, bridge, runner). Verified no directly coupled pre-execution defect:

- `MAX_PROVIDER_CALLS = 3` — authority requires exactly 3; runner drives exactly three wakes; transport forbids a fourth request.
- `MAX_RETRIES = 0` — authority requires 0; no retry path anywhere.
- `MAX_SPEND_CNY = 3.00` — Owner-approved envelope carried by the exact authority; ACTIVE requires a positive finite ceiling; no tariff semantics invented.
- stop-before-next-request — any failure raises and stops the loop before the next request.
- exactly 4 images — transport + bridge enforce.
- official production endpoint — no `--base-url` override unless an explicit test-only loopback flag.
- credential only from `DEEPSEEK_API_KEY` — guard + bridge enforce.
- no hidden request — bridge/transport enforce exactly one request per wake.
- execution-code commit binding — `verify_execution_code_bound` covers every modified execution-critical file (`src/fixed_5m_wake_ledger.py`, `tools/run_replay_v0_1_provider_smoke.py`; both already in `EXECUTION_CRITICAL_PATHS`). No new execution-critical module was introduced.
- ACTIVE authority gate before credential/network construction — `assert_smoke_authority_active` at step 1 plus `HarnessOneShotBridge` construction-time enforcement.
- terminal slot closure after success/failure — the runner writes terminal PASS/FAIL evidence with fresh state-dir/output hygiene; slot revocation after the run follows the established project-brain governance step (both historical slots were closed this way and are enforced `REVOKED` by the authority-consistency checker). No mechanically-resolvable runner defect requiring a new Owner semantic decision was found.

## Verification

Focused suites: `tests.test_replay_v0_1_provider_smoke` (38 tests), `tests.test_wake_identity_separation`, `tests.test_fixed_5m_wake_ledger`, `tests.test_replay_integrity`, `tests.test_replay_restart_continuity`, `tests.test_jianghe_structured_memory`, `tests.test_jianghe_response_normalizer`, `tests.test_jianghe_trading_only_prompt`, `tests.test_replay_v0_1_orchestrator` — all pass.

```text
python -m unittest discover -s tests
607 tests: OK (8 skipped)

python -m compileall -q src tools tests   # PASS
python tools/check_authority_consistency.py  # AUTHORITY_CONSISTENCY = PASS
git diff --check                            # PASS
```

`test_execution_code_bound_passes_at_clean_head` passes on the committed tree by construction.

## Implementation commit

- Implementation + tests: commit `92db7bec33733a65861728f6c156b52b3367acce`
- Evidence + current-state record (this file / `CURRENT_STATE.md`): follow-up commit containing this artifact.

## Unchanged contracts / execution state

- Active response schema remains `JIANGHE_RUNTIME_RESPONSE_V0_2`; active prompt remains `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`; F-01 normal-path behavior is preserved unchanged.
- `PROVIDER_CALLS = 0`; no machine authority was created, resealed or activated.
- Owner revalidation envelope remains `MAX_PROVIDER_CALLS = 3`, `MAX_RETRIES = 0`, `MAX_SPEND_CNY = 3.00` (approved, unconsumed).
- Execution remains `LOCKED` pending a fresh independent high-assurance review of this F-02 closure, then a newly resealed V0_2 two-identity machine authority, then final immediate pre-execution refresh/verification.
- `FULL_V0_1_1998_CALL_REPLAY` remains `LOCKED`.

This offline repair does NOT claim the real-provider path has been revalidated.

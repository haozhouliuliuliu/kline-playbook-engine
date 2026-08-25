# Replay V0.1 Fixed-5m Wake / Orchestrator / Restart / Integrity Engineering Evidence

Status: `WORKER_BRANCH_EVIDENCE` (not an authority document; reports parallel engineering work)

Date: `2026-08-26`

Worker branch: `work/replay-v0-1-fixed-5m-wake-ledger`

Owner authority: `docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

This document records the mechanical replay lifecycle engineering completed on top of
the prior offline-preexecution branch. It implements no research semantics, changes no
frozen prompt/decision contract, touches no Jianghe canon, and makes no provider call.

## 1. Scope and boundary

Built on the prior worker branch (`work/replay-v0-1-offline-preexecution`) which already
provided: the frozen trading-only prompt contract, the append-only hypothesis revision
history, the V0.1 runtime adapter and the outcome-blind deterministic slice selector.

This worker adds the mechanical lifecycle only:

- A. Fixed-5m wake ledger.
- B. Forward-only replay orchestrator.
- C. Restart continuity (Owner gates R1 and R2).
- D. Deterministic integrity gates.

Also fixed a cross-platform defect inherited from the prior branch: SQLite connections
were never closed (per-call `with conn` never closes), causing Windows temp-directory
cleanup to fail with `WinError 32`. All connections are now explicitly closed; the
mismatched-trader store constructor now closes its handle on the (fail-closed) rejection.
No guard was weakened.

## 2. A — Fixed-5m wake ledger (`src/fixed_5m_wake_ledger.py`)

`Fixed5MWakeLedger` implements `WAKE_POLICY = EVERY_NEW_CLOSED_5M_BAR` per governed session.

- The ledger is bound to one governed session with an exact expected 5m-close schedule.
- Each `register_closed_5m(close_time)` produces exactly one wake; the close must match the
  next scheduled close, be on the 5m grid, and be strictly forward.
- Fail-closed violations: off-grid (1m bars never wake), duplicate wake, out-of-order/time
  regression, missing wake (a skip in the schedule), extra wake past the schedule.
- 15m/1H/4H refreshes are context only: the schedule contains only 5m closes, so a
  higher-timeframe close at the same timestamp never creates an extra request.
- `bind_request(wake_identity, request_id, retry_count=0)` enforces one wake → one request
  and one request → one wake; retry count is fixed at zero; unknown wake / reused request /
  duplicate binding all fail closed.
- `close_session()` requires every scheduled wake to exist and be bound (missing/unbound
  fails). `verify_complete()` re-checks without mutation.
- Records are append-only and persisted (per-session rows in one SQLite file), so restart
  continuity is verifiable. `WakeLedgerArchive` is a read-only reconstruction over all
  sessions used by the integrity auditor.

## 3. B — Forward-only orchestrator (`src/replay_v0_1_orchestrator.py`)

`ReplayV01Orchestrator` drives one persistent trader forward through a sealed slice.

- Reuses the single existing `ReplayClock` (no second contradictory clock) and the frozen
  `validate_transition` guard; mirrors the `JiangheMarketReplay` invariants (reject past
  observations, decision must bind the current observation, no clock regression).
- `GovernedWakeStep` binds trading day, session, the newly closed 5m bar and its causal
  context bars. `run_wake_step` advances the clock, registers the wake, builds the
  observation, prepares one request, binds wake→request, runs the (mock) transport,
  records/normalizes the response, and applies the legal decision-state transition.
- Every step produces a `ReplayStepBinding` binding observation identity, wake identity,
  request identity and decision identity.
- Future reads are impossible by construction: the orchestrator rejects any context bar
  whose `available_at` or `close_time` exceeds the decision time, and `JiangheObservation`
  itself rejects future bars. Mapping identity comes only from the sealed slice.
- Model transport is a protocol (`ReplayModelTransport`); the only admitted transports are
  mocks (`SyntheticScriptedTransport`). `NoProviderTransport` fails closed, and the runtime
  contract keeps `provider_call_authorized = False`, so real provider execution stays locked.
- `IntentPositionLifecycle` records each decision-state transition append-only (no fill /
  PnL / execution claim; ENTER is intent-only).

## 4. C — Restart continuity (R1 and R2)

`ReplayStateSealer` computes a deterministic state identity over the portable export,
hypothesis revision history, and the wake archive. `restart()` seals → cleanly closes the
runtime/store → reopens from the same project-owned state → proves exact identity
continuity; drift fails closed.

- R1 (`phase_boundary_restart`): mandatory restart between burn-in day 2 and measurement.
  Working memory, journal, hypotheses, hypothesis revisions, audit and wake history must be
  byte-identical after reopen (no reset). Trader identity continuity is enforced by the
  store itself.
- R2: after measurement day 3, the first persisted `WATCH` / `CANDIDATE` / `IN_POSITION`
  triggers a restart before the next 5m wake. If the whole window produces no active state,
  the result records `ACTIVE_STATE_RESTART_COVERAGE = NOT_OBSERVED`; the historical slice is
  never replaced.

## 5. D — Integrity gates (`src/replay_integrity.py`)

`ReplayIntegrityAuditor` reconstructs evidence from the append-only audit, the wake archive
and persisted working memory and runs outcome-blind, deterministic gates:

- `future_leakage` — every prepared request's observation bars are available ≤ decision time
  and close ≤ exchange time; decision times never regress.
- `duplicate_missing_wake` — one wake per scheduled 5m close, no duplicates, no gaps.
- `duplicate_missing_request` — every wake has exactly one bound request, every prepared
  request is bound 1:1, exactly one raw + one normalized response per request, retries zero.
- `identity_drift` — single trader identity, stable runtime contract, slice-bound
  product/contract/mapping.
- `clock_regression` — monotonic audit timeline and per-request ordering.
- `restart_continuity` — seals precede verified restarts; final state identity is
  deterministically reconstructable.
- `memory_reset` — monotonic mutation history matching audited mutations; final attention
  mode matches the last recorded decision state.
- `illegal_state_transition` — every decision-state event passes the frozen transition guard.
- `hypothesis_self_promotion` — no hypothesis/revision is executable policy; no policy or
  canon write event.
- `audit_reconstruction_completeness` — prepared == raw == normalized == intent == wakes ==
  bindings, and every intent event carries its identity bindings.

## 6. Validation

- `python -m compileall -q src tests tools` — pass.
- `python -m unittest discover -s tests` — pass (491 tests, 8 skipped).
- Focused suites all pass:
  - `tests.test_fixed_5m_wake_ledger` (13)
  - `tests.test_replay_v0_1_orchestrator` (9)
  - `tests.test_replay_restart_continuity` (4)
  - `tests.test_replay_integrity` (11)
- `git diff --check` — clean.

## 7. Known limitations / not in scope

- The orchestrator consumes pre-built causal steps; 1m→5m/15m/1H/4H causal aggregation and
  canonical-corpus data provisioning are a separate data-layer integration concern (the
  sealed slice already fixes their partition identities).
- Multiple governed sessions per trading day are supported by the day-index model; the
  R2 condition window is defined as "after measurement day 3" (measurement day ≥ 4,
  configurable).
- Paper execution, real fills, PnL and execution realism remain explicitly deferred.
- No real DeepSeek/provider call is possible from this code; provider execution stays
  locked behind a later exact execution authority.

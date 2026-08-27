# PAPER LIVE CAUSAL CONTEXT — FLASH WORKER EVIDENCE — 2026-08-27

Status: `WORKER_DELIVERY__OFFLINE_ONLY__PENDING_PROJECT_BRAIN_INTEGRATION`

Worker branch:

`flash/paper-live-context-v01-20260827`

Base for this worker package (latest project-brain integration head at worker
start, safe ff-only):

`61f47c87d89035f856021ef1e7235f2815f34076`

This is worker evidence only; it is not canonical fact. Accepted facts are
written to canonical GitHub authority/evidence by the integration lane.

## 1. Scope

Flash worker package per the Owner offline PAPER prebuild decision
(`docs/reviews/JIANGHE_PAPER_PREBUILD_PARALLEL_ENGINEERING_OWNER_DECISION_2026-08-27.md`)
and the handoff status
(`docs/evidence/JIANGHE_PAPER_PREBUILD_ENGINEERING_STATUS_2026-08-27.md`):

- live 1m substrate aggregation to 5m / 15m / 1H / 4H;
- session-aware causal completeness;
- 5m wake/context emission;
- restart/reconnect continuity at the market/context layer;
- deterministic tests/fault cases;
- future `PaperWakeJournal` integration seam.

The codex worker owns external order/recovery scope; it is untouched here.

## 2. What was implemented

New files on the worker branch (no existing file was modified):

- `src/paper_live_causal_context.py` — the live causal context layer:
  - `paper_live_aggregation_policy_document()` /
    `paper_live_aggregation_policy_identity()` — explicit PAPER-specific
    aggregation-policy identity
    (`KPE_PAPER_LIVE_AGGREGATION_POLICY_V0_1`), explicitly NOT an
    Owner-approved permanent PAPER policy (`owner_approved_permanent_paper_policy = False`,
    `provider_call_authorized = False`).
  - `LiveSessionCalendar` — session resolver from canonical calendar + schedule
    authority: official `trading_day_at`, governed expected 1m starts,
    next-expected-minute continuity, per-trading-day session windows, public
    `trading_days` / `next_trading_day_after` / `previous_trading_day_before`.
  - `LiveCausalBar` — deterministic closed aggregation bar with stable identity
    and a `completed_bar` view for `MarketContext`-style consumers.
  - `LiveCausalWake` — newly completed governed 5m wake with stable
    `wake_identity` / `bar_identity` / `logical_wake_selection_identity`.
  - `LiveCausalContextBuilder` — streaming bootstrap/observe engine with
    checkpoint (snapshot / from_checkpoint), reconnect catch-up, fail-closed
    gap handling, and a durable wake-journal integration seam
    (`wake_already_journaled` / `admit_wake_to_journal`).
- `tests/test_paper_live_causal_context.py` — deterministic coverage (30 tests).

Reused without modification: `src/data_substrate.py` (CompletedBar / BarQuality /
SessionMetadata surface), `src/live_market_data.py` (LiveClosedBar),
`src/replay_v0_1_canonical_feed.py` (governed window construction via
`governed_windows_for_days`), `src/paper_wake_journal.py` (journal seam target).

## 3. Aggregation semantics (explicit PAPER policy, not frozen)

- 5m / 15m / 1H: contiguous official session-window grid; a session break
  disconnects immediately; a shortened trailing bucket is never a complete bar.
- 4H: Asia/Shanghai civil 4-hour grid (`floor(hour/4)*4`); only official
  trading minutes of one official trading day inside that grid; lunch-break
  minutes are not missing minutes; no cross official trading day; complete only
  when every governed minute of the grid is closed and causally available.
- Window counts for context serving: 4H=2, 1H=3, 15m=12, 5m=36 (mechanically
  matching the frozen Jianghe four-timeframe input shape; kept explicit and
  separately identifiable as PAPER policy).

## 4. Invariants proven

The builder proves (each covered by at least one deterministic test):

- timezone-aware timestamps only;
- explicit exchange and concrete contract identity (`LIVE_CAUSAL_CROSS_CONTRACT`);
- official trading-day/session attribution from canonical calendar authority
  (`LIVE_MINUTE_OUTSIDE_GOVERNED_SESSION`, `LIVE_CAUSAL_TRADING_DAY_MISMATCH`);
- only completely CLOSED 1m bars admitted (`LIVE_MINUTE_NOT_CLOSED`);
- finite valid OHLCV;
- causal `available_at` (`LIVE_MINUTE_NOT_YET_CAUSAL`, no future bar);
- no duplicate minute (`LIVE_CAUSAL_DUPLICATE_MINUTE_CONFLICT`);
- no out-of-order minute (`LIVE_CAUSAL_OUT_OF_ORDER`);
- no unexplained missing minute (`LIVE_CAUSAL_MINUTE_GAP`, fail closed, no
  state mutation);
- no cross-contract aggregation; no cross-trading-day contamination;
- session breaks are never filled or bridged (no 5m/15m/1H bar spans a break);
- incomplete higher-timeframe buckets are never emitted;
- 5m wake path: deterministic complete governed 5m bar; no wake before close;
  no duplicate wake after repeated polling; no bootstrap storm of historical
  wakes; stable wake/context identity; exact restart duplicate prevention.

## 5. Bootstrap / restart / reconnect

- `bootstrap` absorbs a historical closed-bar serial to establish
  state/watermark without emitting historical wakes. Only newly completed
  governed 5m bars after bootstrap can produce new live wakes.
- `snapshot` / `from_checkpoint` persist: last accepted minute identity/time,
  all admitted minutes (deterministic rebuild), processed + emitted 5m bar
  ends, last emitted wake, bootstrap flag, policy/calendar/session authority
  identities. Restore re-validates continuity and rejects tampered checkpoints.
- After restart/reconnect: contiguous governed continuation from the checkpoint
  watermark reconstructs deterministically and continues; an unexplained gap
  fails closed (`LIVE_CAUSAL_MINUTE_GAP`) and mutates no state; an accepted 5m
  wake is never re-dispatched.

## 6. Tests / results

Focused suite:

`python -m unittest tests.test_paper_live_causal_context` — 30 tests OK.

Coverage includes: continuous 1m -> 5m; 15m aggregation; 1H aggregation;
4H aggregation; incomplete bucket suppression; 4H incomplete grid suppression;
duplicate 1m; out-of-order 1m; missing 1m; unfinished 1m; future-bar; bootstrap
suppression; repeated-poll idempotency; restart deterministic rebuild; no
duplicate 5m wake after restore; reconnect catch-up; unresolved reconnect gap
fail-closed; session break (no bridging); night/day transition; trading-day
transition; no cross-trading-day contamination; higher-timeframe causal
availability; deterministic identity after rebuild; stable identity across
independent builds; wake-journal seam; context serving + insufficient-history
fail-closed; checkpoint tamper rejection.

Full repository verification:

- `python -m unittest discover -s tests` — PASS;
- `python -m compileall -q src tools tests` — PASS;
- `python tools/check_authority_consistency.py` — `AUTHORITY_CONSISTENCY = PASS`;
- `git diff --check` — PASS.

## 7. Zero external action

This package performed ZERO:

- DeepSeek/provider calls;
- account login / credential reads;
- TqKq/TqSim connection or real-time external subscription requiring account
  action;
- submit/cancel/replace or broker/account mutation;
- real money.

No sizing, execution price policy, SHFE close-today policy, permanent numeric
risk limit or final PAPER contract whitelist was bound or invented.

## 8. Remaining integration assumptions

- The integration lane should review/diff this branch and integrate the Flash
  scope into `integration/paper-readiness-v01-20260827`.
- The wake journal seam expects the existing `PaperWakeJournal` contract
  (`observe` / `has_bar`); no schema change was made.
- `LiveCausalBar.completed_bar` is `MarketContext`-compatible; wiring the live
  wake into the trader/context path is an integration-lane responsibility.
- `LiveSessionCalendar` reuses the canonical schedule/calendar JSON authorities
  (cu, and other products in the schedule) via `governed_windows_for_days`.
- The first trading day of the canonical calendar cannot resolve a night
  window (no previous trading day); this is outside normal live operation and
  is a documented calendar-authority boundary, not a worker defect.

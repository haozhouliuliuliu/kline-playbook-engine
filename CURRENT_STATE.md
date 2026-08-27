# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = POST_REPAIR_THREE_CALL_REVALIDATION__PROJECT_BRAIN_ADJUDICATED_PASS__FULL_V0_1_TECHNICALLY_READY__AWAITING_EXACT_OWNER_PAID_EXECUTION_AUTHORITY`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PRE_FULL_V0_1_REVALIDATION_CLOSED__FULL_REPLAY_EXECUTION_OWNER_GATE`

`NEXT_TASK = OWNER_DECISION_ON_EXACT_FULL_V0_1_PROVIDER_EXECUTION_AUTHORITY__THEN_FRESH_MACHINE_AUTHORITY_PREFLIGHT_AND_FULL_FROZEN_V0_1_RUN`

Active model-visible contracts:

- response schema: `JIANGHE_RUNTIME_RESPONSE_V0_2`;
- trading-only prompt: `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`.

## Project-brain adjudication

Canonical adjudication:

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_THREE_CALL_PROJECT_BRAIN_ADJUDICATION_2026-08-27.md`

Current adjudicated results:

- `FULL_V0_1_TECHNICAL_READINESS = PASS`;
- `SYSTEM_READY_FOR_FROZEN_V0_1_LIFECYCLE_REPLAY = YES`;
- `STRUCTURED_TRADING_MEMORY_LIVE_REVALIDATION = PASS`;
- `POST_REPAIR_REVALIDATION_RESTART_CONTINUITY = VERIFIED`;
- `TRADER_BEHAVIOR_ACCEPTABLE_FOR_PROCEEDING_TO_V0_1 = PRELIMINARY_YES`;
- `RISK_COMPATIBLE = NOT_TESTED`;
- `PROFITABILITY_EVIDENCE = NONE`;
- `LONG_TERM_EDGE_EVIDENCE = NONE`.

The post-repair three-call run closes the pre-full-V0.1 provider/model-contract revalidation gate. It does not establish profitability or long-term edge.

The prior structured-memory blocker (`MEM-01`) is now closed on the real provider path: call 2 received accepted call-1 structured state, and call 3 received accepted call-2 structured state after the forced project-owned restart.

The post-repair execution summary does not include a separate full normalized-decision/raw-response extraction comparable to the earlier historical retest decision package. That is an evidence-packaging limitation, not a frozen V0.1 lifecycle-integrity blocker. The full V0.1 run must preserve complete per-wake normalized decision/state/source-reference evidence prospectively.

## Closed post-repair three-call revalidation

Exact Owner authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION_OWNER_DECISION_2026-08-27.md`

Execution evidence:

- `docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_EXECUTION_2026-08-27.md`;
- `docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_RUN_2026-08-27.json`.

Terminal machine authority:

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_SLOT_V0_3.json`

Observed execution facts:

- exactly `3` real provider requests / attempts;
- exactly `3` accepted normalized decisions;
- `0` retries;
- `0` hidden/auxiliary requests;
- no call 4;
- exactly `4` governed causal PNGs per call;
- both logical and runtime wake identities matched the sealed authority;
- provider attempt ledger: `3 RESULT_RECEIVED`, `0 unknown`, `0 unresolved`;
- restart continuity: `VERIFIED`;
- slot terminalized to `REVOKED` and never reusable.

Historical F-01 through F-05 repair/review evidence remains canonical historical support. No additional review is pending for the consumed three-call slot.

## Frozen V0.1 authority

Frozen research authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

Current frozen semantics remain unchanged:

- product / contract: `cu` / `SHFE.cu2406`;
- outcome-blind deterministic sealed slice;
- `20` prior causal trading days + `2` burn-in days + `20` measurement days;
- wake on every newly closed governed 5m bar;
- exactly one request per admitted wake;
- retries `0`;
- persistent trader identity and causal memory;
- mandatory burn-in boundary restart and conditional active-state restart;
- intent-only lifecycle, no historical fills/PnL/execution claims;
- no outcome/PnL/future leakage;
- no policy self-promotion.

V0.1 remains a lifecycle/memory/audit experiment, not a profitability backtest.

## Full V0.1 execution state

`FULL_V0_1_1998_CALL_REPLAY = LOCKED_PENDING_EXACT_OWNER_PAID_EXECUTION_AUTHORITY`

`FULL_V0_1_TECHNICAL_READINESS = PASS`

`FULL_V0_1_REAL_PROVIDER_EXECUTION_AUTHORITY = NONE_ACTIVE`

`FULL_V0_1_MACHINE_AUTHORITY = NONE_ACTIVE`

No full-V0.1 provider request is currently authorized.

Before any full-V0.1 real provider request, the project requires a new exact Owner execution authority and a fresh machine-readable authority bound to the exact execution commit and frozen experiment identities. The consumed three-call authority may never be reused or extended.

## Provider execution state

`ORIGINAL_THREE_CALL_SMOKE = CONSUMED__FAILCLOSED_AFTER_ONE_REAL_REQUEST`

`ORIGINAL_SMOKE_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`HISTORICAL_THREE_CALL_RETEST = CONSUMED__COMPLETED_3OF3_PASS`

`HISTORICAL_THREE_CALL_RETEST_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION = COMPLETED_3OF3__PROJECT_BRAIN_ADJUDICATED_PASS__SLOT_CLOSED`

`POST_REPAIR_REVALIDATION_MACHINE_AUTHORITY = REVOKED__TERMINAL__NEVER_REUSE`

`POST_REPAIR_REVALIDATION_PROVIDER_CALLS = 3__ALL_RESULT_RECEIVED`

`POST_REPAIR_REVALIDATION_PROVIDER_ATTEMPTS = 3__0_UNKNOWN__0_UNRESOLVED`

`POST_REPAIR_REVALIDATION_RETRIES = 0`

`POST_REPAIR_REVALIDATION_HIDDEN_REQUESTS = 0`

`POST_REPAIR_REVALIDATION_CNY_CEILING = OWNER_WAIVED_FOR_THAT_CONSUMED_EXACT_SLOT`

`CANONICAL_DATASET_LOCAL_AVAILABILITY = ORIGINAL_ACCEPTED_DATASET_FOUND_AND_VERIFIED`

`REAL_DEEPSEEK_PROVIDER_CALLS = NO_CURRENT_ACTIVE_SLOT`

`FUTURE_PROVIDER_SLOT_WAKE_IDENTITY_REPAIR = TWO_IDENTITY_PATH_VERIFIED`

`STRUCTURED_TRADING_MEMORY_FIDELITY_REPAIR = LIVE_PROVIDER_REVALIDATED`

`ACTIVE_RESPONSE_SCHEMA = JIANGHE_RUNTIME_RESPONSE_V0_2`

`ACTIVE_PROMPT_CONTRACT = KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`

## Current locks

- original smoke, historical retest, and post-repair revalidation slots: `CONSUMED / CLOSED / NEVER REACTIVATE`;
- full V0.1 real provider replay before a new exact Owner paid/provider execution authority: `LOCKED`;
- full V0.1 before a fresh exact machine authority and immediate consequential-action verification: `LOCKED`;
- retries, duplicate wakes, hidden second requests and outcome-driven re-asking: `LOCKED`;
- changing frozen V0.1 research semantics without Owner authority: `LOCKED`;
- post-V0.1 CU/RB provider replay: `LOCKED` until full V0.1 closes and is adjudicated;
- historical execution/PnL semantics: `NOT_YET_APPROVED`;
- learning/policy promotion: `LOCKED`;
- SHADOW/PAPER/broker/account/real money/permanent numeric risk/automatic expansion: `LOCKED`.

## Post-V0.1 route

Approved roadmap authority:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

Only after full frozen V0.1 completes and is adjudicated does the approved sequence move to:

`CU chronological historical replay -> RB chronological historical replay -> focused CU/RB comparison -> conditional RB supplementation -> PAPER`.

## Continuity rule for the next integration lane

Before substantive work or any provider action, refresh current `main`, read `PROJECT_BRAIN_RUNTIME_BRIEF.md`, `PROJECT_GOVERNANCE.md`, `PROJECT_DIRECTION.md`, this file, `TOOL_REGISTRY.md`, the frozen V0.1 Owner decision, and the project-brain adjudication above.

The post-repair three-call revalidation has already been consumed and adjudicated PASS. Do not rerun it. The next consequential boundary is a new exact Owner paid/provider execution authority for the full frozen V0.1 replay. No provider call is authorized until that new authority and a matching fresh machine authority exist.
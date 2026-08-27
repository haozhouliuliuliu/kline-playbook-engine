# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = OFFLINE_PAPER_PREBUILD_ENGINEERING__PARALLEL_WORKERS_PREPARED__INTEGRATION_PR56_ACTIVE__NO_EXTERNAL_PAPER_ACTION`

`CURRENT_WORK_PACKAGE = PAPER_PREBUILD_OFFLINE_ENGINEERING_V0_1`

`WORK_PACKAGE_PHASE = PARALLEL_IMPLEMENTATION__WORKER_BRANCHES_READY__INTEGRATION_AND_FINAL_CONSOLIDATED_AUDIT_PENDING`

`NEXT_TASK = RUN_FLASH_LIVE_CAUSAL_CONTEXT_BRANCH_AND_CODEX_ORDER_RECOVERY_BRANCH__INTEGRATE_BOTH_INTO_PR56__COMPLETE_FAKE_END_TO_END_PAPER_RUNTIME__THEN_ONE_CONSOLIDATED_TARGETED_PAPER_READINESS_AUDIT_AND_REPAIR`

Current offline-prebuild Owner authority:

`docs/reviews/JIANGHE_PAPER_PREBUILD_PARALLEL_ENGINEERING_OWNER_DECISION_2026-08-27.md`

Current handoff/status evidence:

`docs/evidence/JIANGHE_PAPER_PREBUILD_ENGINEERING_STATUS_2026-08-27.md`

The Owner has temporarily deferred full frozen V0.1 paid execution in order to prebuild outcome-independent PAPER infrastructure. This sequencing change does not close, waive, alter or replace the frozen V0.1 experiment or the approved historical -> PAPER promotion route.

Active model-visible contracts remain:

- response schema: `JIANGHE_RUNTIME_RESPONSE_V0_2`;
- trading-only prompt: `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`.

## Offline PAPER prebuild integration state

`PAPER_PREBUILD_MODE = OFFLINE_ONLY`

`PAPER_INTEGRATION_PR = 56`

`PAPER_INTEGRATION_BRANCH = integration/paper-readiness-v01-20260827`

`PAPER_INTEGRATION_HEAD_OBSERVED = 61f47c87d89035f856021ef1e7235f2815f34076`

`PAPER_INTEGRATION_CI = PASS__REPOSITORY_CI_RUN_151__HEAD_61f47c87d89035f856021ef1e7235f2815f34076`

`PAPER_CONNECT_AUTHORITY = NONE_ACTIVE`

`PAPER_ORDER_AUTHORITY = NONE_ACTIVE`

`PAPER_ACCOUNT_LOGIN = NOT_AUTHORIZED`

`PAPER_EXTERNAL_ORDER_ACTION = NOT_AUTHORIZED`

`BROKER_ACCOUNT_MUTATION = NOT_AUTHORIZED`

`REAL_MONEY = NOT_AUTHORIZED`

No PAPER account credential needs to be read for the current package. No external account login, market subscription requiring account action, submit, cancel, replace or broker/account mutation is authorized.

Current integration-branch capability already observed includes:

- restored project-owned PAPER/runtime orchestration capability seam;
- broker-neutral live closed-bar normalization with bootstrap/watermark/sequence checks;
- broker-neutral market-context work for live input;
- separate machine gates for PAPER connection vs external order actions;
- result-dependent activation profile that cannot become ACTIVE with missing policy bindings;
- broker/account truth mirror and reconciliation-ready snapshots;
- durable external order submit-attempt journal with UNKNOWN fail-closed semantics;
- durable real-time wake journal with dispatch-start persistence and restart duplicate prevention;
- pure fail-closed PAPER supervisor separating connect / observe / order readiness;
- broker-neutral TqSdk PAPER candidate adapter and offline-testable driver;
- deterministic tests and successful repository CI at the observed integration head.

These are integration-branch facts, not canonical-main runtime capabilities until accepted and merged.

## Parallel worker state

Exactly one integration lane remains:

`integration/paper-readiness-v01-20260827`

Pre-created isolated worker branches:

- `flash/paper-live-context-v01-20260827`;
- `codex/paper-order-recovery-v01-20260827`.

`FLASH_WORKER_SCOPE = LIVE_1M_TO_5M_15M_1H_4H_CAUSAL_CONTEXT__SESSION_COMPLETENESS__WAKE_CONTEXT_CONTINUITY__OFFLINE_ONLY`

`CODEX_WORKER_SCOPE = EXTERNAL_PAPER_SUBMIT_CANCEL_REPLACE_RESTART_UNKNOWN_RECOVERY__DUPLICATE_PREVENTION__HIGH_ASSURANCE_OFFLINE_ONLY`

`WORKER_BRANCHES_MAY_NOT_EDIT = main__CURRENT_STATE__OWNER_AUTHORITY__integration/paper-readiness-v01-20260827__OTHER_WORKER_WORKTREE`

Workers must inspect branch divergence first. If an assigned pre-created branch has no worker-specific commits and is merely behind the integration branch, it may be fast-forwarded to the latest integration head before edits. Unknown work must never be overwritten.

Worker reports are not canonical facts. The integration lane must inspect diffs/tests and integrate accepted changes.

## Open outcome-independent PAPER engineering gaps

The package remains incomplete. Current known gaps to close before the final consolidated audit include:

1. real-time causal 1m substrate -> 5m wake + 15m / 1H / 4H context construction with governed session boundaries and causal availability;
2. market/context restart and reconnect continuity without duplicate wakes;
3. submit/cancel/replace attempt accounting and restart recovery against broker truth;
4. robust UNKNOWN execution-state handling that blocks new risk until resolved;
5. partial-fill/cancel/reject/order snapshot lifecycle coverage;
6. final startup/runtime composition proving `authority -> connect eligibility -> broker/account reconciliation -> market bootstrap -> sequence clean -> trader observation ready -> order gate separately ready`;
7. fake end-to-end PAPER runtime/fault-injection drill with no real account or external order action;
8. one consolidated targeted PAPER-readiness adversarial audit/repair package after implementation integration.

Result-dependent settings remain intentionally unbound and fail-closed until later evidence/Owner decisions:

- sizing / lot policy;
- execution price policy;
- SHFE/INE close-offset policy where inventory-day semantics matter;
- permanent numeric risk limits;
- final PAPER contract whitelist.

## TqSdk role boundary

`TOOL_REGISTRY.md` currently adopts TqSdk only for historical concrete-contract 1m research data acquisition at runtime `3.10.1`.

`TQSDK_PAPER_ROLE = CANDIDATE_ENGINEERING_ONLY__NOT_YET_VERIFIED_OR_ADOPTED_FOR_EXTERNAL_PAPER`

Current offline candidate code must not be interpreted as permission to connect/login/order. Before the first actual PAPER account connection, the proposed PAPER runtime/API/credential seam must be separately verified and the tool-role status updated through the canonical tooling process.

## Full frozen V0.1 state — temporarily deferred, not waived

Canonical project-brain adjudication:

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_THREE_CALL_PROJECT_BRAIN_ADJUDICATION_2026-08-27.md`

Frozen research authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

Current adjudicated facts remain:

- `FULL_V0_1_TECHNICAL_READINESS = PASS`;
- `SYSTEM_READY_FOR_FROZEN_V0_1_LIFECYCLE_REPLAY = YES`;
- `STRUCTURED_TRADING_MEMORY_LIVE_REVALIDATION = PASS`;
- `POST_REPAIR_REVALIDATION_RESTART_CONTINUITY = VERIFIED`;
- `TRADER_BEHAVIOR_ACCEPTABLE_FOR_PROCEEDING_TO_V0_1 = PRELIMINARY_YES`;
- `RISK_COMPATIBLE = NOT_TESTED`;
- `PROFITABILITY_EVIDENCE = NONE`;
- `LONG_TERM_EDGE_EVIDENCE = NONE`.

`FULL_V0_1_EXECUTION_SCHEDULING = OWNER_TEMPORARILY_DEFERRED_WHILE_OUTCOME_INDEPENDENT_PAPER_PREBUILD_PROCEEDS`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED_PENDING_EXACT_OWNER_PAID_EXECUTION_AUTHORITY`

`FULL_V0_1_REAL_PROVIDER_EXECUTION_AUTHORITY = NONE_ACTIVE`

`FULL_V0_1_MACHINE_AUTHORITY = NONE_ACTIVE`

No full-V0.1 provider request is currently authorized. The consumed three-call authority may never be reused or extended.

Frozen V0.1 semantics remain unchanged, including:

- product / contract: `cu` / `SHFE.cu2406`;
- outcome-blind deterministic sealed slice;
- `20` prior causal trading days + `2` burn-in days + `20` measurement days;
- wake on every newly closed governed 5m bar;
- exactly one request per admitted wake;
- retries `0`;
- persistent trader identity and causal memory;
- mandatory governed restarts;
- intent-only lifecycle, no historical fills/PnL/execution claims;
- no outcome/PnL/future leakage;
- no policy self-promotion.

## Closed post-repair three-call revalidation

Exact historical Owner authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION_OWNER_DECISION_2026-08-27.md`

Execution evidence:

- `docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_EXECUTION_2026-08-27.md`;
- `docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_RUN_2026-08-27.json`.

Terminal machine authority:

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_SLOT_V0_3.json`

Observed historical facts remain:

- exactly `3` real provider requests / attempts;
- exactly `3` accepted normalized decisions;
- `0` retries;
- `0` hidden/auxiliary requests;
- no call 4;
- exactly `4` governed causal PNGs per call;
- both logical and runtime wake identities matched;
- provider attempt ledger: `3 RESULT_RECEIVED`, `0 unknown`, `0 unresolved`;
- restart continuity: `VERIFIED`;
- slot terminalized to `REVOKED` and never reusable.

## Current locks

- all consumed historical smoke/retest/revalidation slots: `CONSUMED / CLOSED / NEVER REACTIVATE`;
- full V0.1 real provider replay without a new exact Owner paid/provider execution authority and fresh machine authority: `LOCKED`;
- changing frozen V0.1 research semantics without Owner authority: `LOCKED`;
- post-V0.1 CU/RB provider replay before full V0.1 closes/adjudicates: `LOCKED`;
- historical execution/PnL semantics until separately frozen: `NOT_YET_APPROVED`;
- learning/policy promotion: `LOCKED`;
- PAPER external connect/login: `LOCKED`;
- PAPER external submit/cancel/replace/account mutation: `LOCKED`;
- real broker/account action: `LOCKED`;
- real money: `LOCKED`;
- permanent numeric risk rules: `LOCKED`;
- automatic product/position expansion: `LOCKED`.

Offline PAPER engineering under the exact prebuild Owner decision is permitted despite the external-action locks above.

## Approved post-V0.1 route remains unchanged

Roadmap authority:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

Formal promotion sequence remains:

`FULL FROZEN V0.1 CLOSURE -> CU chronological historical replay -> RB chronological historical replay -> focused CU/RB comparison -> conditional RB supplementation -> REAL-TIME PAPER`

The current prebuild package accelerates infrastructure only; it does not skip that sequence.

## Continuity rule for the next conversation / integration lane

Before substantive work:

1. refresh current GitHub `main`;
2. read `PROJECT_BRAIN_RUNTIME_BRIEF.md`;
3. read `PROJECT_GOVERNANCE.md`;
4. read `PROJECT_DIRECTION.md`;
5. read this `CURRENT_STATE.md`;
6. read `docs/reviews/JIANGHE_PAPER_PREBUILD_PARALLEL_ENGINEERING_OWNER_DECISION_2026-08-27.md`;
7. read `docs/evidence/JIANGHE_PAPER_PREBUILD_ENGINEERING_STATUS_2026-08-27.md`;
8. inspect current PR #56 and actual worker branch heads/CI before trusting the recorded observed hashes above;
9. read `TOOL_REGISTRY.md` when TqSdk/provider/credential/tool role matters.

Do not infer worker completion from chat. Do not merge worker branches from reports alone. Do not perform any account login/connect/order action until a later exact Owner authority explicitly opens that consequential boundary.

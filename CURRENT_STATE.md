# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-28`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = OFFLINE_PAPER_PREBUILD__CODEX_REPAIR_PR66_FINAL_STOP_GRANULARITY_REPAIR_RECEIVED__PROJECT_BRAIN_REVALIDATION__FINAL_WAKE_DURABILITY_ORDERING_REPAIR_REQUIRED__NO_EXTERNAL_PAPER_ACTION`

`CURRENT_WORK_PACKAGE = PAPER_PREBUILD_OFFLINE_ENGINEERING_V0_1`

`WORK_PACKAGE_PHASE = POST_AUDIT_CODEX_REPAIR__PROJECT_BRAIN_REVALIDATION__FINAL_WAKE_DURABILITY_ORDERING_REPAIR_REQUIRED`

`NEXT_TASK = CODEX_PRESERVE_DURABLE_5M_WAKE_ADMISSION_BEFORE_ANY_1M_STOP_EXTERNAL_MUTATION_CAN_ABORT_PROCESSING__CLOSE_UNKNOWN_SUBMIT_FAILURE_PATH_WITHOUT_DUPLICATE_STOP_OR_WAKE__THEN_PROJECT_BRAIN_REVALIDATE_AND_ACCEPT_OR_BLOCK`

Current feature-freeze / audit Owner decision:

`docs/reviews/JIANGHE_PAPER_FEATURE_FREEZE_AND_INDEPENDENT_AUDIT_OWNER_DECISION_2026-08-28.md`

Underlying offline-prebuild Owner authority:

`docs/reviews/JIANGHE_PAPER_PREBUILD_PARALLEL_ENGINEERING_OWNER_DECISION_2026-08-27.md`

Exact feature-freeze evidence:

`docs/evidence/JIANGHE_PAPER_PREBUILD_FEATURE_FREEZE_2026-08-28.md`

## PAPER feature-freeze / audit / repair state

`PAPER_PREBUILD_MODE = OFFLINE_ONLY`

`PAPER_INTEGRATION_PR = 56`

`PAPER_INTEGRATION_BRANCH = integration/paper-readiness-v01-20260827`

`PAPER_FEATURE_FROZEN_HEAD = 31f8e7cc435d04e9c3b4e951454601906dddf874`

`PAPER_FEATURE_FROZEN_HEAD_CI = PASS__REPOSITORY_CI_RUN_184__LINUX_AND_WINDOWS`

`PAPER_LAST_FEATURE_PR = 64__MERGED`

`PAPER_FEATURE_SCOPE = FROZEN__POST_FREEZE_CHANGES_ONLY_FOR_AUDIT_FINDINGS_OR_EXPLICIT_OWNER_REOPEN`

`PAPER_TOTAL_AUDIT_STATUS = COMPLETE__PROJECT_BRAIN_INDEPENDENT_FINDINGS_ONLY_AUDIT_PERFORMED`

`PAPER_TOTAL_AUDIT_REVIEWER = PROJECT_BRAIN`

`PAPER_TOTAL_AUDIT_OUTPUT_MODE = FINDINGS_ONLY__NO_STANDALONE_ACTIVE_TREE_TOMBSTONE_REQUIRED_BY_OWNER`

`CODEX_REPAIR_PR = 66`

`CODEX_REPAIR_BRANCH = codex/paper-total-audit-repair-v01-20260828`

`CODEX_REPAIR_HEAD = acf6a0fe89fc472a664055a33bfbca5565137e86`

`CODEX_REPAIR_HEAD_CI = PASS__REPOSITORY_CI_RUN_191__LINUX_AND_WINDOWS__844_TESTS__12_SKIPPED_ON_LINUX`

`CODEX_REPAIR_STATUS = FINAL_STOP_GRANULARITY_REPAIR_SUBMITTED__GOVERNED_1M_STOP_TRIGGER_VERIFIED__ONE_WAKE_DURABILITY_ORDERING_REGRESSION_REMAINS`

`PROJECT_BRAIN_CLOSURE_STATUS = BLOCKED_PENDING_FINAL_WAKE_DURABILITY_ORDERING_REPAIR`

`PAPER_FINAL_ACCEPTANCE = NOT_YET_ACCEPTED`

The project brain completed the Owner-required independent consolidated findings-only audit and continues to revalidate Codex repair PR #66 from actual code and CI rather than worker completion claims. The latest repair head `acf6a0fe89fc472a664055a33bfbca5565137e86` passed Repository CI #191 on Linux and Windows; the Linux run reports 844 tests with 12 skips. The intended STOP-granularity closure is substantively correct: durable protective STOP directives are now evaluated from newly accepted governed causal 1-minute bars while the DeepSeek cognition wake remains 5-minute, and the new 1-minute path preserves freshness, contract identity, duplicate prevention and restartable conditional state.

Final acceptance remains held because project-brain failure-path revalidation found one ordering regression at the boundary between 1-minute protective execution and 5-minute cognition durability. `LiveCausalContextBuilder.observe()` can admit a minute and mark the resulting 5-minute wake as emitted before `PaperRuntimeCoordinator.process_closed_minutes()` durably admits that wake to `PaperWakeJournal`. The coordinator now evaluates/submits a triggered 1-minute STOP before it writes returned 5-minute wakes to the wake journal. If that same minute is a 5-minute wake boundary and the broker submission becomes UNKNOWN or raises, the runtime can abort after the builder has advanced but before the cognition wake is durably journaled. Transport rollback restores its own market watermark but does not roll back the already-mutated causal builder, so an in-process retry or a persisted checkpoint can silently lose that cognition wake. The remaining repair is bounded to preserving durable 5-minute wake continuity before any 1-minute STOP external mutation can abort processing, while retaining 1-minute STOP evaluation, UNKNOWN/no-blind-retry semantics, and duplicate prevention. Per Owner direction, no permanent standalone findings tombstone is required in the active tree.

## External PAPER / consequential-action locks

`PAPER_CONNECT_AUTHORITY = NONE_ACTIVE`

`PAPER_ORDER_AUTHORITY = NONE_ACTIVE`

`PAPER_ACCOUNT_LOGIN = NOT_AUTHORIZED`

`PAPER_EXTERNAL_ORDER_ACTION = NOT_AUTHORIZED`

`BROKER_ACCOUNT_MUTATION = NOT_AUTHORIZED`

`REAL_MONEY = NOT_AUTHORIZED`

Audit/repair/revalidation do not authorize external connectivity or account/order mutation. No PAPER credential needs to be read for the current task.

Current locks remain:

- PAPER external connect/login: `LOCKED`;
- PAPER external submit/cancel/replace/account mutation: `LOCKED`;
- real broker/account action: `LOCKED`;
- real money: `LOCKED`;
- paid provider execution without a separate exact Owner/machine authority: `LOCKED`;
- changing frozen V0.1 research semantics without Owner authority: `LOCKED`;
- post-V0.1 CU/RB provider replay before full V0.1 closes/adjudicates: `LOCKED`;
- learning/policy self-promotion: `LOCKED`;
- permanent numeric risk rules: `LOCKED`;
- automatic product/position expansion: `LOCKED`.

## Result-dependent activation boundary

The outcome-independent infrastructure intentionally does not freeze or invent:

- sizing / lot policy;
- execution-price policy;
- SHFE/INE close-today vs close-yesterday policy where required;
- permanent numeric risk limits;
- final PAPER contract whitelist.

These remain later evidence/Owner-decision bindings and must fail closed until separately approved.

## TqSdk PAPER role boundary

Tool/provider/runtime status is owned by `TOOL_REGISTRY.md`.

`TQSDK_PAPER_ROLE = CANDIDATE_ENGINEERING_ONLY__NOT_YET_VERIFIED_OR_ADOPTED_FOR_EXTERNAL_PAPER`

Offline candidate code and passing fake tests do not grant permission to connect/login/order. The current repair mechanically anchors external-PAPER role preflight to the canonical TqSdk registry entry, so caller-created role bindings, installed runtime or credential presence cannot promote the role. Before the first actual PAPER connection, the proposed TqSdk PAPER runtime/API/credential seam must still be separately verified and, if accepted, adopted through the canonical tooling process.

## Full frozen V0.1 remains deferred, not waived

Current project-brain adjudication:

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_THREE_CALL_PROJECT_BRAIN_ADJUDICATION_2026-08-27.md`

Frozen research authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

`FULL_V0_1_EXECUTION_SCHEDULING = OWNER_TEMPORARILY_DEFERRED_WHILE_PAPER_PREBUILD_ACCEPTANCE_WORK_PROCEEDS`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED_PENDING_EXACT_OWNER_PAID_EXECUTION_AUTHORITY`

`FULL_V0_1_REAL_PROVIDER_EXECUTION_AUTHORITY = NONE_ACTIVE`

`FULL_V0_1_MACHINE_AUTHORITY = NONE_ACTIVE`

The PAPER prebuild sequencing does not close, waive or alter the frozen V0.1 experiment.

## Approved research/promotion route unchanged

Roadmap authority:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

Formal sequence remains:

`FULL FROZEN V0.1 CLOSURE -> CU chronological historical replay -> RB chronological historical replay -> focused CU/RB comparison -> conditional RB supplementation -> REAL-TIME PAPER`

The feature-frozen prebuild accelerates infrastructure only and does not skip that route.

## Continuity rule for the next conversation

Before substantive project work:

1. refresh current GitHub `main`;
2. read `PROJECT_BRAIN_RUNTIME_BRIEF.md`;
3. read `PROJECT_GOVERNANCE.md`;
4. read `PROJECT_DIRECTION.md`;
5. read this `CURRENT_STATE.md`;
6. read `docs/reviews/JIANGHE_PAPER_FEATURE_FREEZE_AND_INDEPENDENT_AUDIT_OWNER_DECISION_2026-08-28.md`;
7. read `docs/evidence/JIANGHE_PAPER_PREBUILD_FEATURE_FREEZE_2026-08-28.md`;
8. inspect repair PR #66 and its actual current head/diff/CI, with special attention to the remaining wake-durability ordering closure under a simultaneous 1-minute STOP trigger and broker submit UNKNOWN/exception at a 5-minute wake boundary;
9. after repair closure, inspect integration PR #56 and run project-brain final acceptance before any merge-to-main decision;
10. read `TOOL_REGISTRY.md` when TqSdk/provider/credential/tool role matters.

Do not infer repair acceptance from a worker report or green CI alone. Do not begin any external PAPER/provider/broker action without a later exact Owner authority.
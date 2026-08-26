# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = THREE_CALL_PROVIDER_SMOKE_RETEST_RESEALED__PRE_EXECUTION`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_RETEST_RESEALED__PRE_EXECUTION`

`NEXT_TASK = EXECUTE_FRESH_THREE_CALL_PROVIDER_SMOKE_RETEST`

The original slot was consumed by its fail-closed first real request. The response-contract clarification (prompt V0_2) and fail-closed observability repair are implemented, tested, rehearsed and a fresh independent retest machine authority has been resealed and is ACTIVE.

## Current exact task authorities and evidence

Frozen V0.1 replay authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

Original provider-smoke design authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_OWNER_DECISION.md`

Consumed original payment/execution authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_EXECUTION_AUTHORITY_2026-08-27.md`

Response-contract clarification authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_RESPONSE_CONTRACT_CLARIFICATION_OWNER_DECISION_2026-08-27.md`

Fresh retest payment/execution authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_EXECUTION_AUTHORITY_2026-08-27.md`

Current machine-readable authority file (old slot, terminal):

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`

Fresh retest machine-readable authority file (ACTIVE):

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_SLOT.json`

Fail-closed real-provider evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`

Offline preexecution evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`

Approved post-V0.1 roadmap:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

## Provider execution state

`ORIGINAL_THREE_CALL_SMOKE = CONSUMED__FAILCLOSED_AFTER_ONE_REAL_REQUEST`

`ORIGINAL_SMOKE_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`FRESH_THREE_CALL_RETEST_OWNER_AUTHORITY = APPROVED`

`FRESH_THREE_CALL_RETEST_MACHINE_AUTHORITY = ACTIVE`

`REAL_DEEPSEEK_PROVIDER_CALLS = AUTHORIZED_FOR_FRESH_THREE_CALL_RETEST_ONLY`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

The original failed request is immutable evidence and is not treated as one of the three calls in the separately authorized fresh retest. The retest begins from the same first sealed wake using a clean pre-smoke state. The fresh retest machine authority (`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_SLOT.json`, version `KPE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_V0_1`) is bound to the repaired execution commit and the V0_2 prompt identity; the old slot JSON stays `REVOKED` and is never flipped back to its old `ACTIVE` identity.

## Current locks

- original three-call smoke slot: `CONSUMED / CLOSED`;
- any retry or continuation under the old slot: `LOCKED`;
- fresh three-call retest provider execution: `ACTIVE__EXACT_THREE_CALL_SLOT_ONLY`;
- fourth call, automatic retry or replacement wake inside the retest: `LOCKED`;
- full V0.1 1998-call provider replay: `LOCKED`;
- post-V0.1 CU/RB provider replay: `LOCKED`;
- historical execution/PnL semantics: `NOT_YET_APPROVED`;
- learning/policy promotion: `LOCKED`;
- SHADOW: `LOCKED`;
- PAPER/account connection: `LOCKED`;
- broker/account actions/writes: `LOCKED`;
- permanent numeric risk rules: `LOCKED`;
- real money/capital funding/real orders: `LOCKED`;
- automatic product, position-size or capital expansion: `LOCKED`.

## Continuity rule for the next integration lane

Before substantive work or any provider action, refresh current `main`, read `PROJECT_BRAIN_RUNTIME_BRIEF.md`, then this file and the exact authorities/evidence above. Do not merge the stale pre-governance `CURRENT_STATE.md` from the fail-closed worker branch.

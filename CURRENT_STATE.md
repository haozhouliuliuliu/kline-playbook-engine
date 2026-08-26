# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = PROVIDER_SMOKE_RESPONSE_CONTRACT_REPAIR_AND_RETEST_PREPARATION`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_FAILCLOSED__REPAIR_AUTHORIZED__RETEST_PREEXECUTION`

`NEXT_TASK = IMPLEMENT_RESPONSE_CONTRACT_CLARIFICATION_AND_RESEAL_FRESH_THREE_CALL_RETEST`

The first real provider smoke attempt consumed its original slot and stopped fail-closed on a provider response-schema mismatch. The Owner has approved a serialization-contract clarification and a separate fresh three-call retest after offline repair verification and exact machine-authority resealing.

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

Current machine-readable authority file:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`

Fail-closed real-provider evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`

Offline preexecution evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`

Approved post-V0.1 roadmap:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

## Provider execution state

`ORIGINAL_THREE_CALL_SMOKE = CONSUMED__FAILCLOSED_AFTER_ONE_REAL_REQUEST`

`ORIGINAL_SMOKE_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`FRESH_THREE_CALL_RETEST_OWNER_AUTHORITY = APPROVED__CONDITIONAL_ON_REPAIR_AND_RESEAL`

`FRESH_THREE_CALL_RETEST_MACHINE_AUTHORITY = NOT_YET_ACTIVE`

`REAL_DEEPSEEK_PROVIDER_CALLS = PAUSED_UNTIL_REPAIR_VERIFIED_AND_NEW_MACHINE_AUTHORITY_ACTIVE`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

The original failed request is immutable evidence and is not treated as one of the three calls in the separately authorized fresh retest. The retest must begin from the same first sealed wake using a clean pre-smoke state, but only after the response-contract clarification, fail-closed observability repair, tests, mock/loopback rehearsal and exact resealing are complete.

The currently committed machine JSON remains the terminal old-slot authority (`status = REVOKED`). It must not be flipped back to the old `ACTIVE` identity. The integration lane must generate a new retest authority identity/version bound to the repaired execution-code commit and new prompt identity before any credential/network capability is created.

## Current locks

- original three-call smoke slot: `CONSUMED / CLOSED`;
- any retry or continuation under the old slot: `LOCKED`;
- fresh three-call retest provider execution: `PAUSED_PENDING_REPAIR_VERIFICATION_AND_NEW_MACHINE_AUTHORITY`;
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

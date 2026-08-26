# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = PROVIDER_SMOKE_OWNER_HOLD`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_READY__OWNER_HOLD_BEFORE_FIRST_CALL`

`NEXT_TASK = WAIT_FOR_OWNER_EXPLICIT_RESUME_OF_THREE_CALL_PROVIDER_SMOKE`

The Owner has explicitly stopped the provider smoke for now while governance/context continuity is repaired. Do not delegate or resume the smoke in a fresh conversation.

Current hold authority:

`docs/reviews/PROJECT_GOVERNANCE_OWNERSHIP_REPAIR_OWNER_DECISION_2026-08-27.md`

## Current exact task authorities

Current frozen replay authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

Provider-smoke design authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_OWNER_DECISION.md`

Previously approved exact payment/execution authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_EXECUTION_AUTHORITY_2026-08-27.md`

Machine-readable exact slot authority:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`

Offline preexecution evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`

Approved post-V0.1 roadmap:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

## Provider execution state

The exact three-call smoke slot was previously approved and machine-sealed, but a newer Owner instruction now places execution on hold before the first provider call.

`PROVIDER_SMOKE_EXECUTION = OWNER_HOLD_BEFORE_FIRST_CALL`

`PROVIDER_CALLS_DURING_CURRENT_HOLD = 0`

`THREE_CALL_SMOKE_SLOT = APPROVED_BUT_NOT_CURRENTLY_EXECUTABLE_DUE_TO_OWNER_HOLD`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

The hold does not consume, widen or rewrite the previously sealed slot. A later explicit Owner instruction is required to resume it.

## Current locks

- three-call provider smoke execution: `OWNER_HOLD_BEFORE_FIRST_CALL`;
- full V0.1 1998-call provider replay: `LOCKED`;
- post-V0.1 CU/RB paid replays: `LOCKED`;
- historical execution/PnL semantics: `NOT_YET_APPROVED`;
- learning/policy promotion: `LOCKED`;
- SHADOW: `LOCKED`;
- PAPER/account connection: `LOCKED`;
- broker/account actions/writes: `LOCKED`;
- permanent numeric risk rules: `LOCKED`;
- real money/capital funding/real orders: `LOCKED`;
- automatic product, position-size or capital expansion: `LOCKED`.

## Current continuity facts

- current GitHub `main` is the dynamic project fact source;
- `PROJECT_GOVERNANCE.md` owns stable governance/authority ownership;
- `PROJECT_DIRECTION.md` owns product/research direction;
- `ARCHITECTURE_BASELINE.md` owns long-lived architecture;
- `TOOL_REGISTRY.md` owns provider/tool/runtime status, pins and credential-location contract;
- exact execution permission is owned by the exact Owner execution authority plus machine-readable authority;
- this file alone owns the current phase/locks/next-task summary.

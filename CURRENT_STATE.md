# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = THREE_CALL_PROVIDER_SMOKE_EXECUTION_READY`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_ACTIVE__EXACT_THREE_CALL_SLOT`

`NEXT_TASK = EXECUTE_THREE_CALL_PROVIDER_SMOKE`

The Owner has explicitly resumed the exact previously approved three-call DeepSeek provider smoke after governance/context continuity repair.

Current resume authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RESUME_OWNER_DECISION_2026-08-27.md`

## Current exact task authorities

Current frozen replay authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

Provider-smoke design authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_OWNER_DECISION.md`

Payment/execution authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_EXECUTION_AUTHORITY_2026-08-27.md`

Owner resume authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RESUME_OWNER_DECISION_2026-08-27.md`

Current machine-readable slot authority:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`

Offline preexecution evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`

Approved post-V0.1 roadmap:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

## Provider execution state

`PROVIDER_SMOKE_EXECUTION = OWNER_APPROVED__READY_TO_EXECUTE`

`THREE_CALL_SMOKE_MACHINE_AUTHORITY_STATUS = ACTIVE`

`THREE_CALL_SMOKE_SLOT = AUTHORIZED_FOR_EXACT_THREE_CALL_EXECUTION_ONLY`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

Exact paid boundary remains:

- provider: `deepseek`;
- model: `deepseek-v4-flash-vision-exp`;
- max provider calls: `3`;
- max retries: `0`;
- max spend: `CNY 3.00`;
- exactly 4 causal PNGs per call;
- exactly one provider request per governed wake;
- forced project-owned restart after successful call 2 before call 3;
- call 4 forbidden;
- full 1998-call replay unauthorized.

Credential location remains the Windows current-user environment variable `DEEPSEEK_API_KEY`; secret values must not be printed, logged or committed.

The machine JSON is `ACTIVE` for this exact slot. Before execution, the runner must still pass the pre-network code/prompt/context/renderer/authority guards. Any mismatch fails closed before provider capability is created.

After 3/3 completion or any fail-closed terminal result, this exact paid slot is consumed/closed. A retry or re-run requires new explicit Owner paid authority.

## Current locks

- three-call provider smoke execution: `ACTIVE__EXACT_SLOT_ONLY`;
- fourth provider call/retry/replacement wake: `LOCKED`;
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

## Current continuity facts

- current GitHub `main` is the dynamic project fact source;
- `PROJECT_GOVERNANCE.md` owns stable governance/authority ownership;
- `PROJECT_DIRECTION.md` owns product/research direction;
- `ARCHITECTURE_BASELINE.md` owns long-lived architecture;
- `TOOL_REGISTRY.md` owns provider/tool/runtime status, pins and credential-location contract;
- exact paid/external execution permission is owned by the applicable Owner execution authority plus machine-readable authority;
- this file alone owns the current activity/phase/locks/next-task summary.

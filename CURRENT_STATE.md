# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = SMOKE_ADJUDICATION_ACCEPTED__LOCAL_DECISION_EVIDENCE_EXTRACTION`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_RETEST_ACCEPTED__DECISION_CONTENT_REVIEW_NEXT`

`NEXT_TASK = EXTRACT_AND_REVIEW_THREE_CALL_NORMALIZED_DECISIONS__THEN_OWNER_DECIDE_FULL_V0_1`

The fresh independent three-call provider-smoke retest completed 3/3 PASS on 2026-08-27. An independent high-assurance review accepted the retest for its narrow provider-path/schema/restart/request-accounting claims and found no true wake-selection/protocol violation. The differing V0.1/V0.2 runtime wake hashes are an identity-layer wording defect caused by the approved prompt/trader-identity change, not a different logical wake selection. No paid rerun is required for that issue.

Before any new future provider slot is resealed, the project must prospectively distinguish stable logical wake-selection identity from runtime wake identity. Historical slots/evidence remain immutable.

The immediate task is read-only/local evidence extraction and review of the three successful DeepSeek normalized trading judgments and resulting project-owned state transitions. This task must not make a provider request or use future/PnL outcome information.

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

Fresh retest machine-readable authority file (terminal, REVOKED after 3/3):

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_SLOT.json`

Fresh retest execution evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_2026-08-27.md`

Independent wake-identity / retest acceptability review:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_WAKE_IDENTITY_INDEPENDENT_REVIEW_2026-08-27.md`

Fail-closed real-provider evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`

Offline preexecution evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`

Approved post-V0.1 roadmap:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

## Provider execution state

`ORIGINAL_THREE_CALL_SMOKE = CONSUMED__FAILCLOSED_AFTER_ONE_REAL_REQUEST`

`ORIGINAL_SMOKE_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`FRESH_THREE_CALL_RETEST_OWNER_AUTHORITY = APPROVED__CONSUMED`

`FRESH_THREE_CALL_RETEST_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`REAL_DEEPSEEK_PROVIDER_CALLS = RETEST_COMPLETED_3OF3__SLOT_CLOSED__NO_AUTHORITY_TO_RERUN`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

`FUTURE_PROVIDER_SLOT_WAKE_IDENTITY_REPAIR = REQUIRED_BEFORE_ANY_NEW_SLOT_RESEAL`

Both the original slot and fresh retest slot are terminal/consumed. A further real provider attempt requires a new explicit Owner paid authority. The full V0.1 1998-call replay remains unauthorized and must not be started automatically.

## Current locks

- original three-call smoke slot: `CONSUMED / CLOSED`;
- any retry or continuation under the old slot: `LOCKED`;
- fresh three-call retest provider execution: `CONSUMED / CLOSED (3/3 PASS)`;
- fourth call, automatic retry or replacement wake inside the retest: `LOCKED`;
- any new provider slot reseal before logical/runtime wake-identity forward repair: `LOCKED`;
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

Before substantive work or any provider action, refresh current `main`, read `PROJECT_BRAIN_RUNTIME_BRIEF.md`, then this file and the exact authorities/evidence above.

For the immediate local decision-evidence extraction, do not call any provider and do not infer missing decision content from hashes. Inspect only retained local runner output / project-owned persistent state from the already completed successful retest, match it to the committed request/wake/decision identities, and persist a derived evidence artifact without secrets or future/PnL outcome data. If the retained local artifacts are unavailable, record that evidence gap and do not rerun the provider.

# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = THREE_CALL_DECISION_REVIEW_COMPLETED__MEMORY_FIDELITY_REPAIR_REQUIRED`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_ACCEPTED__PRE_FULL_V0_1_OFFLINE_REPAIR`

`NEXT_TASK = REPAIR_STRUCTURED_TRADING_MEMORY_AND_LOGICAL_RUNTIME_WAKE_IDENTITY__OFFLINE_VERIFY__THEN_OWNER_DECIDE_PROVIDER_REVALIDATION_AND_FULL_V0_1`

The fresh independent three-call provider-smoke retest completed 3/3 PASS on 2026-08-27. Independent high-assurance review accepted the retest for its narrow provider-path/schema/restart/request-accounting claims and found no true wake-selection/protocol violation. The differing V0.1/V0.2 runtime wake hashes are an identity-layer wording defect caused by the approved prompt/trader-identity change, not a different logical wake selection. No paid rerun is required for that historical discrepancy.

The three successful DeepSeek decisions were recovered from retained local state without any new provider call. Project-brain trading-quality review found the three-call behavior preliminarily coherent and appropriately cautious, with two bounded model-quality findings: one Jianghe claim was used outside its canonical management meaning, and call 2 imprecisely described the first night-session bar's open/high/close values.

A material forward lifecycle gap was also found: important trader-owned state such as current market hypothesis, key locations/watch state, expected trigger and invalidation is stated in model rationale but is not preserved as first-class structured working memory by the current projection/persistence path. Because V0.1 is specifically a persistent-trader lifecycle experiment, this must be repaired and deterministically verified before the Owner is asked to authorize the full paid replay.

Before any new future provider slot is resealed, the project must also prospectively distinguish stable logical wake-selection identity from runtime wake identity. Historical slots/evidence remain immutable.

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

Recovered three-call normalized decision evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_DECISIONS_2026-08-27.md`

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_DECISIONS_2026-08-27.json`

Independent wake-identity / retest acceptability review:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_WAKE_IDENTITY_INDEPENDENT_REVIEW_2026-08-27.md`

Three-call trading-quality / memory-fidelity review:

`docs/reviews/JIANGHE_REPLAY_V0_1_THREE_CALL_TRADING_QUALITY_REVIEW_2026-08-27.md`

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

`STRUCTURED_TRADING_MEMORY_FIDELITY_REPAIR = REQUIRED_BEFORE_FULL_V0_1`

Both the original slot and fresh retest slot are terminal/consumed. A further real provider attempt requires a new explicit Owner paid authority. The full V0.1 1998-call replay remains unauthorized and must not be started automatically.

## Current locks

- original three-call smoke slot: `CONSUMED / CLOSED`;
- any retry or continuation under the old slot: `LOCKED`;
- fresh three-call retest provider execution: `CONSUMED / CLOSED (3/3 PASS)`;
- fourth call, automatic retry or replacement wake inside the retest: `LOCKED`;
- any new provider slot reseal before logical/runtime wake-identity forward repair: `LOCKED`;
- full V0.1 before structured trading-memory fidelity repair and offline verification: `LOCKED`;
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

The immediate work is offline engineering only: repair structured trading-memory fidelity and the prospective logical/runtime wake-identity separation, then run focused and broad deterministic verification. Do not call any provider during this repair. If a repair changes the model-visible response/prompt contract, any later real-provider revalidation requires a new exact Owner paid authority plus a newly resealed machine authority before network execution.

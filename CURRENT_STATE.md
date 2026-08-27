# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = MEMORY_AND_WAKE_IDENTITY_OFFLINE_REPAIR_COMPLETED__OFFLINE_VERIFIED`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PRE_FULL_V0_1_OFFLINE_REPAIR_VERIFIED__AWAITING_PROVIDER_REVALIDATION_ADJUDICATION`

`NEXT_TASK = PROJECT_BRAIN_OR_HIGH_ASSURANCE_ADJUDICATION__WHETHER_A_SMALL_NEW_PAID_PROVIDER_REVALIDATION_IS_REQUIRED_BEFORE_ASKING_OWNER_ABOUT_FULL_V0_1`

An offline repair package (2026-08-27) implemented already-approved V0.1 semantics with zero provider calls and passed focused + broad deterministic verification. Historical smoke evidence and terminal machine authorities were not altered.

The three successful DeepSeek decisions were recovered from retained local state without any new provider call. Project-brain trading-quality review found the three-call behavior preliminarily coherent and appropriately cautious, with two bounded model-quality findings: one Jianghe claim was used outside its canonical management meaning, and call 2 imprecisely described the first night-session bar's open/high/close values.

A material forward lifecycle gap was also found: important trader-owned state such as current market hypothesis, key locations/watch state, expected trigger and invalidation is stated in model rationale but is not preserved as first-class structured working memory by the current projection/persistence path. Because V0.1 is specifically a persistent-trader lifecycle experiment, this was repaired offline and deterministically verified before the Owner is asked to authorize the full paid replay.

The 2026-08-27 offline repair package (documented below) completed BOTH forward requirements:

- structured trading-memory fidelity = `OFFLINE VERIFIED`;
- logical/runtime wake identity separation = `OFFLINE VERIFIED`.

The repair advanced the model-visible response contract to `JIANGHE_RUNTIME_RESPONSE_V0_2` and the trading-only prompt contract to `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`. Historical V0.1/V0.2 prompt/schema constants and both historical smoke slots remain immutable. Because the model-visible prompt/schema contract changed, any later real-provider revalidation requires a new exact Owner paid authority plus a newly resealed two-identity machine authority before network execution.

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

Offline memory & wake-identity repair evidence (this package):

`docs/evidence/JIANGHE_REPLAY_V0_1_PRE_FULL_REPLAY_MEMORY_AND_WAKE_IDENTITY_REPAIR_2026-08-27.md`

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

`FUTURE_PROVIDER_SLOT_WAKE_IDENTITY_REPAIR = REQUIRED_BEFORE_ANY_NEW_SLOT_RESEAL__OFFLINE_VERIFIED`

`STRUCTURED_TRADING_MEMORY_FIDELITY_REPAIR = REQUIRED_BEFORE_FULL_V0_1__OFFLINE_VERIFIED`

`ACTIVE_RESPONSE_SCHEMA = JIANGHE_RUNTIME_RESPONSE_V0_2`

`ACTIVE_PROMPT_CONTRACT = KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`

Both the original slot and fresh retest slot are terminal/consumed. A further real provider attempt requires a new explicit Owner paid authority. The full V0.1 1998-call replay remains unauthorized and must not be started automatically. Any future provider slot must use the new two-identity (logical + runtime) wake authority contract.

## Current locks

- original three-call smoke slot: `CONSUMED / CLOSED`;
- any retry or continuation under the old slot: `LOCKED`;
- fresh three-call retest provider execution: `CONSUMED / CLOSED (3/3 PASS)`;
- fourth call, automatic retry or replacement wake inside the retest: `LOCKED`;
- any new provider slot reseal (now requiring the two-identity logical+runtime wake contract) before a new exact Owner paid authority: `LOCKED`;
- full V0.1 1998-call provider replay: `LOCKED` (structured-memory repair offline-verified, but real-provider revalidation adjudication and Owner authority are still required);
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

The immediate next step is offline adjudication only: the project brain / a high-assurance review must decide whether a small new paid provider revalidation is required (the active prompt/schema contract is now V0_3/V0_2) before the Owner is asked about authorizing the full V0.1 1998-call replay. Do not call any provider, create a paid authority, activate a provider slot, or decide Owner spending permission during that adjudication. If a repair changes the model-visible response/prompt contract again, any later real-provider revalidation requires a new exact Owner paid authority plus a newly resealed two-identity machine authority before network execution.

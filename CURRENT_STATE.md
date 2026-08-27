# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION_OWNER_REQUIRED__PREEXECUTION_ASSURANCE`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = POST_REPAIR_REAL_PROVIDER_REVALIDATION_REQUIRED__PENDING_INDEPENDENT_REVIEW_AND_EXACT_SPEND`

`NEXT_TASK = INDEPENDENT_HIGH_ASSURANCE_REVIEW__THEN_PREPARE_FRESH_TWO_IDENTITY_THREE_CALL_SLOT__THEN_OWNER_BIND_EXACT_SPEND`

An offline repair package (2026-08-27) implemented already-approved V0.1 semantics with zero provider calls and passed focused + broad deterministic verification. Historical smoke evidence and terminal machine authorities were not altered.

The three successful historical DeepSeek decisions were recovered from retained local state without any new provider call. Project-brain trading-quality review found the three-call behavior preliminarily coherent and appropriately cautious, with two bounded model-quality findings: one Jianghe claim was used outside its canonical management meaning, and call 2 imprecisely described the first night-session bar's open/high/close values.

The material forward lifecycle gap found by that review has been repaired offline and deterministically verified:

- structured trading-memory fidelity = `OFFLINE VERIFIED`;
- logical/runtime wake identity separation = `OFFLINE VERIFIED`.

The repair advanced the model-visible response contract to `JIANGHE_RUNTIME_RESPONSE_V0_2` and the trading-only prompt contract to `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`. Historical V0.1/V0.2 prompt/schema constants and both historical smoke slots remain immutable.

The Owner has now explicitly required a fresh real-provider three-call post-repair revalidation. This resolves the prior adjudication question: the revalidation is required, not optional. It is a new provider slot, not a continuation or replay of either historical terminal slot.

Before any new provider request, the repaired model-visible contract and two-identity provider-smoke path must receive independent high-assurance review, the exact execution commit must pass deterministic preflight, a fresh V0_2 two-identity machine authority must be resealed, and an explicit positive numerical CNY spend ceiling must be approved by the Owner. Until all of those are true, no credential/network capability may be activated.

## Current exact task authorities and evidence

Frozen V0.1 replay authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

Original provider-smoke design authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_OWNER_DECISION.md`

Consumed original payment/execution authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_EXECUTION_AUTHORITY_2026-08-27.md`

Response-contract clarification authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_RESPONSE_CONTRACT_CLARIFICATION_OWNER_DECISION_2026-08-27.md`

Consumed fresh historical retest payment/execution authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_EXECUTION_AUTHORITY_2026-08-27.md`

Current machine-readable authority file (old slot, terminal):

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`

Historical retest machine-readable authority file (terminal, REVOKED after 3/3):

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_SLOT.json`

Historical retest execution evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_2026-08-27.md`

Recovered historical three-call normalized decision evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_DECISIONS_2026-08-27.md`

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_DECISIONS_2026-08-27.json`

Independent wake-identity / historical retest acceptability review:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_WAKE_IDENTITY_INDEPENDENT_REVIEW_2026-08-27.md`

Three-call trading-quality / memory-fidelity review:

`docs/reviews/JIANGHE_REPLAY_V0_1_THREE_CALL_TRADING_QUALITY_REVIEW_2026-08-27.md`

Offline memory & wake-identity repair evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PRE_FULL_REPLAY_MEMORY_AND_WAKE_IDENTITY_REPAIR_2026-08-27.md`

Current Owner-required post-repair three-call revalidation decision:

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION_OWNER_DECISION_2026-08-27.md`

Fail-closed original real-provider evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`

Offline preexecution evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`

Approved post-V0.1 roadmap:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

## Provider execution state

`ORIGINAL_THREE_CALL_SMOKE = CONSUMED__FAILCLOSED_AFTER_ONE_REAL_REQUEST`

`ORIGINAL_SMOKE_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`HISTORICAL_THREE_CALL_RETEST = CONSUMED__COMPLETED_3OF3_PASS`

`HISTORICAL_THREE_CALL_RETEST_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION = REQUIRED__NOT_YET_ACTIVE`

`POST_REPAIR_REVALIDATION_INDEPENDENT_REVIEW = REQUIRED__PENDING`

`POST_REPAIR_REVALIDATION_MACHINE_AUTHORITY = NOT_YET_RESEALED`

`POST_REPAIR_REVALIDATION_MAX_SPEND_CNY = NOT_YET_BOUND`

`REAL_DEEPSEEK_PROVIDER_CALLS = NO_CURRENT_ACTIVE_SLOT`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

`FUTURE_PROVIDER_SLOT_WAKE_IDENTITY_REPAIR = OFFLINE_VERIFIED__TWO_IDENTITY_FORM_REQUIRED`

`STRUCTURED_TRADING_MEMORY_FIDELITY_REPAIR = OFFLINE_VERIFIED`

`ACTIVE_RESPONSE_SCHEMA = JIANGHE_RUNTIME_RESPONSE_V0_2`

`ACTIVE_PROMPT_CONTRACT = KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`

The historical original smoke and historical three-call retest slots are terminal/consumed and may never be reactivated. The Owner-required post-repair three-call revalidation must use a newly resealed V0_2 two-identity authority. Full V0.1 remains unauthorized and must not start automatically.

## Current locks

- original three-call smoke slot: `CONSUMED / CLOSED`;
- any retry or continuation under the original slot: `LOCKED`;
- historical successful three-call retest: `CONSUMED / CLOSED (3/3 PASS)`;
- any retry or continuation under the historical retest slot: `LOCKED`;
- post-repair three-call provider revalidation execution before independent review: `LOCKED`;
- post-repair three-call provider revalidation execution before fresh V0_2 logical+runtime two-identity machine authority reseal: `LOCKED`;
- post-repair three-call provider revalidation execution before explicit positive Owner-approved `MAX_SPEND_CNY`: `LOCKED`;
- fourth call, automatic retry, replacement wake or outcome-driven re-asking in the future revalidation: `LOCKED`;
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

The immediate next step is independent high-assurance review of the offline repair and the new two-identity provider-smoke execution path. That review must execute zero provider requests and must not alter historical evidence. After an acceptable review, prepare and deterministically preflight a fresh PENDING V0_2 two-identity three-call machine authority on the exact current execution commit. Do not activate it or construct provider/network capability until the Owner has approved an explicit positive numerical CNY spend ceiling and the authority is revalidated immediately before execution.

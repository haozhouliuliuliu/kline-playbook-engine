# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION__F01_NORMAL_PATH_VERIFIED__F02_FAILCLOSED_EVIDENCE_REPAIR_REQUIRED`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = POST_REPAIR_REAL_PROVIDER_REVALIDATION_REQUIRED__BLOCKED_BY_F02_POST_PROVIDER_FAILURE_OBSERVABILITY_DEFECT`

`NEXT_TASK = REPAIR_F02_ADMITTED_REQUEST_BOUND_WAKE_EVIDENCE__OFFLINE_VERIFY__FRESH_INDEPENDENT_REVIEW__THEN_RESEAL_AND_RUN_APPROVED_3CALL_SLOT`

The structured trading-memory and logical/runtime wake-identity offline repair remains offline-verified. Active model-visible contracts remain:

- response schema: `JIANGHE_RUNTIME_RESPONSE_V0_2`;
- trading-only prompt: `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`.

The Owner explicitly requires a fresh post-repair three-call real-provider revalidation and has approved the exact paid envelope:

- `MAX_PROVIDER_CALLS = 3`;
- `MAX_RETRIES = 0`;
- `MAX_SPEND_CNY = 3.00`.

That approval remains valid and unconsumed for this exact revalidation but does not bypass fail-closed pre-execution assurance.

Codex independently confirmed the original F-01 normal-path repair: preflight carries both identities from actual governed `ReplayStepBinding`; the pre-call guard and post-drive verification independently enforce logical/runtime identity equality; PASS evidence retains both identities; future V0_2 authority rules remain intact.

The same fresh review found a new material blocker (`F-02`): if a provider request has already occurred but strict response normalization/recording fails before `run_wake_step()` appends a complete `ReplayStepBinding`, terminal fail-closed evidence is built only from prior completed bindings and omits the current already-requested wake. Therefore a first-call malformed response can show one provider request but zero admitted-wake identity records, and a later failure can omit the final actually requested wake.

Required repair under existing authority:

1. persist or expose an admitted/request-bound wake record after identity admission and request binding but before transport execution;
2. record at minimum logical wake-selection identity, runtime wake identity, close time, sequence/call identity, and request identifier as available;
3. build fail-closed admitted-wake evidence from those actually admitted/request-bound records, not only completed decisions;
4. do not fabricate future/unadmitted wakes or a decision identity/provider result when normalization failed;
5. add deterministic no-network tests for first-call and later-call malformed provider responses after transport invocation;
6. rerun focused + broad deterministic verification;
7. obtain a fresh independent high-assurance review;
8. only after an acceptable review, reseal the new exact V0_2 two-identity machine authority bound to the exact execution commit and the already approved CNY 3.00 ceiling, then perform immediate pre-execution refresh/verification and run the three calls.

No provider call has been made under this post-repair revalidation authority yet and no new machine slot has been created/resealed/activated.

## Current exact task authorities and evidence

Frozen V0.1 replay authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

Original provider-smoke design authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_OWNER_DECISION.md`

Consumed original payment/execution authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_EXECUTION_AUTHORITY_2026-08-27.md`

Response-contract clarification authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_RESPONSE_CONTRACT_CLARIFICATION_OWNER_DECISION_2026-08-27.md`

Consumed historical retest payment/execution authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_EXECUTION_AUTHORITY_2026-08-27.md`

Original historical machine authority (terminal):

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`

Historical retest machine authority (terminal):

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_SLOT.json`

Historical retest execution evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_2026-08-27.md`

Recovered historical three-call normalized decisions:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_DECISIONS_2026-08-27.md`

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_DECISIONS_2026-08-27.json`

Historical wake-identity independent review:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_RETEST_WAKE_IDENTITY_INDEPENDENT_REVIEW_2026-08-27.md`

Three-call trading-quality / memory-fidelity review:

`docs/reviews/JIANGHE_REPLAY_V0_1_THREE_CALL_TRADING_QUALITY_REVIEW_2026-08-27.md`

Offline memory & wake-identity repair evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_PRE_FULL_REPLAY_MEMORY_AND_WAKE_IDENTITY_REPAIR_2026-08-27.md`

Current Owner-required revalidation + exact spend authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION_OWNER_DECISION_2026-08-27.md`

Initial independent pre-execution review (F-01 finding):

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_PROVIDER_REVALIDATION_INDEPENDENT_REVIEW_2026-08-27.md`

F-01 offline closure evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_F01_CLOSURE_2026-08-27.md`

Fresh F-01 closure independent review (F-02 finding):

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_PROVIDER_REVALIDATION_F01_CLOSURE_INDEPENDENT_REVIEW_2026-08-27.md`

Approved post-V0.1 roadmap:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

## Provider execution state

`ORIGINAL_THREE_CALL_SMOKE = CONSUMED__FAILCLOSED_AFTER_ONE_REAL_REQUEST`

`ORIGINAL_SMOKE_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`HISTORICAL_THREE_CALL_RETEST = CONSUMED__COMPLETED_3OF3_PASS`

`HISTORICAL_THREE_CALL_RETEST_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION = OWNER_REQUIRED__SPEND_APPROVED__EXECUTION_BLOCKED_BY_F02`

`POST_REPAIR_REVALIDATION_INDEPENDENT_REVIEW = F01_NORMAL_PATH_ACCEPTED__F02_MATERIAL_DEFECT_OPEN`

`POST_REPAIR_REVALIDATION_MACHINE_AUTHORITY = NOT_YET_RESEALED`

`POST_REPAIR_REVALIDATION_MAX_SPEND_CNY = 3.00__OWNER_APPROVED`

`POST_REPAIR_REVALIDATION_PROVIDER_CALLS = 0`

`REAL_DEEPSEEK_PROVIDER_CALLS = NO_CURRENT_ACTIVE_SLOT`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

`FUTURE_PROVIDER_SLOT_WAKE_IDENTITY_REPAIR = TWO_IDENTITY_NORMAL_PATH_VERIFIED__F02_FAILCLOSED_EVIDENCE_REQUIRED`

`STRUCTURED_TRADING_MEMORY_FIDELITY_REPAIR = OFFLINE_VERIFIED`

`ACTIVE_RESPONSE_SCHEMA = JIANGHE_RUNTIME_RESPONSE_V0_2`

`ACTIVE_PROMPT_CONTRACT = KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`

## Current locks

- original smoke and historical retest slots: `CONSUMED / CLOSED / NEVER REACTIVATE`;
- post-repair three-call execution before F-02 repair: `LOCKED`;
- post-repair three-call execution before a fresh acceptable independent review: `LOCKED`;
- post-repair three-call execution before a fresh exact V0_2 logical+runtime two-identity machine authority: `LOCKED`;
- fourth call, retry, replacement wake or outcome-driven re-asking: `LOCKED`;
- full V0.1 1998-call replay: `LOCKED`;
- post-V0.1 CU/RB provider replay: `LOCKED`;
- historical execution/PnL semantics: `NOT_YET_APPROVED`;
- learning/policy promotion: `LOCKED`;
- SHADOW/PAPER/broker/account/real money/permanent numeric risk/automatic expansion: `LOCKED`.

## Continuity rule for the next integration lane

Before substantive work or any provider action, refresh current `main`, read `PROJECT_BRAIN_RUNTIME_BRIEF.md`, this file, and the exact task authorities/evidence above.

The immediate next step is routine offline engineering closure of F-02 under existing authority. This repair must produce zero provider calls. After deterministic verification, obtain a fresh independent high-assurance review. If and only if that review returns acceptable, reseal the new exact V0_2 two-identity machine authority using the already Owner-approved maximum spend of CNY 3.00, then perform the final immediate pre-execution refresh/verification before any credential/network capability is used.

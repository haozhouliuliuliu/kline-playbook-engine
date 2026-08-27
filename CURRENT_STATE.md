# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION__F01_OFFLINE_REPAIR_VERIFIED__EXECUTION_LOCKED_AWAITING_FRESH_REVIEW`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = POST_REPAIR_REAL_PROVIDER_REVALIDATION_REQUIRED__F01_REPAIRED_OFFLINE__FRESH_INDEPENDENT_REVIEW_PENDING`

`NEXT_TASK = FRESH_INDEPENDENT_HIGH_ASSURANCE_REVIEW_OF_F01_CLOSURE__THEN_RESEAL_V02_TWO_IDENTITY_MACHINE_AUTHORITY__THEN_RUN_APPROVED_3CALL_SLOT`

The structured trading-memory and logical/runtime wake-identity offline repair remains offline-verified. Active model-visible contracts remain:

- response schema: `JIANGHE_RUNTIME_RESPONSE_V0_2`;
- trading-only prompt: `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`.

The Owner explicitly requires a fresh post-repair three-call real-provider revalidation and has approved the exact paid envelope:

- `MAX_PROVIDER_CALLS = 3`;
- `MAX_RETRIES = 0`;
- `MAX_SPEND_CNY = 3.00`.

That approval is valid for this exact revalidation but does not bypass fail-closed pre-execution assurance.

The independent Codex pre-execution review found one material blocker (`F-01`): the real-provider boundary did not carry/prove the logical wake-selection identity end to end. An offline repair under existing authority has now closed F-01 deterministically with zero provider calls:

1. provider-smoke preflight smoke-wakes blueprint now carries `logical_wake_selection_identity`, `wake_identity` and `close_time` per call_1/2/3, sourced from the actual `ReplayStepBinding`;
2. the real runner fails closed on BOTH identities (independent checks) via a pre-call guard and post-drive verification;
3. PASS and fail-closed admitted-wake evidence durably record both identities;
4. deterministic tamper/regression coverage proves logical-only mismatch is rejected and preflight/evidence retain both fields.

No provider call has been made under this post-repair revalidation authority yet, no machine slot was activated or resealed, and the identity model / trading semantics / active prompt-schema contract were not changed.

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

Current independent pre-execution review (blocked by F-01):

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_PROVIDER_REVALIDATION_INDEPENDENT_REVIEW_2026-08-27.md`

F-01 offline closure evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_F01_CLOSURE_2026-08-27.md`

Approved post-V0.1 roadmap:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

## Provider execution state

`ORIGINAL_THREE_CALL_SMOKE = CONSUMED__FAILCLOSED_AFTER_ONE_REAL_REQUEST`

`ORIGINAL_SMOKE_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`HISTORICAL_THREE_CALL_RETEST = CONSUMED__COMPLETED_3OF3_PASS`

`HISTORICAL_THREE_CALL_RETEST_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION = OWNER_REQUIRED__SPEND_APPROVED__F01_REPAIRED_OFFLINE__EXECUTION_LOCKED_AWAITING_FRESH_REVIEW`

`POST_REPAIR_REVALIDATION_INDEPENDENT_REVIEW = F01_CLOSED_OFFLINE__FRESH_REVIEW_PENDING`

`POST_REPAIR_REVALIDATION_MACHINE_AUTHORITY = NOT_YET_RESEALED`

`POST_REPAIR_REVALIDATION_MAX_SPEND_CNY = 3.00__OWNER_APPROVED`

`POST_REPAIR_REVALIDATION_PROVIDER_CALLS = 0`

`REAL_DEEPSEEK_PROVIDER_CALLS = NO_CURRENT_ACTIVE_SLOT`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

`FUTURE_PROVIDER_SLOT_WAKE_IDENTITY_REPAIR = CORE_MODEL_AND_REAL_PATH_F01_OFFLINE_VERIFIED__FRESH_REVIEW_PENDING`

`STRUCTURED_TRADING_MEMORY_FIDELITY_REPAIR = OFFLINE_VERIFIED`

`ACTIVE_RESPONSE_SCHEMA = JIANGHE_RUNTIME_RESPONSE_V0_2`

`ACTIVE_PROMPT_CONTRACT = KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`

## Current locks

- original smoke and historical retest slots: `CONSUMED / CLOSED / NEVER REACTIVATE`;
- post-repair three-call execution before a fresh acceptable independent review of F-01 closure: `LOCKED`;
- post-repair three-call execution before a fresh exact V0_2 logical+runtime two-identity machine authority: `LOCKED`;
- fourth call, retry, replacement wake or outcome-driven re-asking: `LOCKED`;
- full V0.1 1998-call replay: `LOCKED`;
- post-V0.1 CU/RB provider replay: `LOCKED`;
- historical execution/PnL semantics: `NOT_YET_APPROVED`;
- learning/policy promotion: `LOCKED`;
- SHADOW/PAPER/broker/account/real money/permanent numeric risk/automatic expansion: `LOCKED`.

## Continuity rule for the next integration lane

Before substantive work or any provider action, refresh current `main`, read `PROJECT_BRAIN_RUNTIME_BRIEF.md`, this file, and the exact task authorities/evidence above.

The immediate next step is a fresh independent high-assurance review of the F-01 offline closure. That review is the gate before resealing the new exact V0_2 two-identity machine authority (using the already Owner-approved maximum spend of CNY 3.00) and performing the final immediate pre-execution refresh/verification before any credential/network capability is used. No provider call, slot activation, or reseal may occur before that review returns acceptable.

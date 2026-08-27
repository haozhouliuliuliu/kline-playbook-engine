# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION__F01_AND_F02_VERIFIED__F03_CHILD_BRIDGE_UNKNOWN_ATTEMPT_ACCOUNTING_REPAIR_REQUIRED`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = POST_REPAIR_REAL_PROVIDER_REVALIDATION_REQUIRED__BLOCKED_BY_F03_UNKNOWN_AFTER_ATTEMPT_START_ACCOUNTING_DEFECT`

`NEXT_TASK = REPAIR_F03_DURABLE_PROVIDER_ATTEMPT_START_AND_UNKNOWN_ATTEMPT_TERMINALIZATION__OFFLINE_VERIFY__FRESH_INDEPENDENT_REVIEW__THEN_RESEAL_AND_RUN_APPROVED_3CALL_SLOT`

Active model-visible contracts remain:

- response schema: `JIANGHE_RUNTIME_RESPONSE_V0_2`;
- trading-only prompt: `KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`.

The Owner still requires one fresh three-call real-provider revalidation.

Current exact hard execution envelope:

- `MAX_PROVIDER_CALLS = 3`;
- `MAX_RETRIES = 0`;
- no call 4;
- no replacement wake;
- no outcome-driven re-asking.

### Scoped cost decision for this exact slot

The Owner explicitly superseded the earlier `MAX_SPEND_CNY = 3.00` requirement for this exact three-call revalidation.

`POST_REPAIR_REVALIDATION_CNY_CEILING = OWNER_WAIVED_FOR_THIS_EXACT_SLOT`

No fixed CNY ceiling and no per-request CNY budget guard are required for this slot. Actual provider token/usage accounting must still be retained. This is a scoped exception only; it does not modify the stable default cost doctrine for future paid packages in `PROJECT_DIRECTION.md`.

## Current repair/review findings

`F01_LOGICAL_RUNTIME_IDENTITY_PATH = INDEPENDENTLY_VERIFIED_CLOSED`

`F02_REQUEST_BOUND_WAKE_FAILCLOSED_EVIDENCE = INDEPENDENTLY_VERIFIED_CLOSED`

Fresh independent high-assurance review of the F-02 closure found material blocker `F-03`:

- the parent runner durably binds wake + request before transport;
- the real Harness bridge then launches a child process;
- the child may reach/send the provider request but the parent can time out or fail before receiving/writing the result artifact;
- current `transport.calls` accounting is appended only after the child returns a `SmokeBridgeResult`;
- therefore timeout/no-result after child launch can be incorrectly reported as zero provider/network calls even though a paid attempt may have occurred.

Required F-03 repair under existing authority:

1. durably record an attempt-started state before launching the real bridge child process, bound to exact authority + wake identities + request_id + zero-retry policy;
2. timeout / missing result / invalid result / parent-child handoff failure after attempt start must produce `UNKNOWN_AFTER_ATTEMPT_START` or equivalent fail-closed state;
3. unknown attempt must never be represented as zero calls/zero network activity;
4. unknown attempt is a terminal barrier for this slot: no retry, no replacement wake, no later call, no automatic reseal-as-unattempted;
5. retain available non-secret diagnostics without treating missing output as proof of no request;
6. add deterministic timeout and no-result-after-launch regressions;
7. obtain a fresh independent high-assurance review after repair;
8. only after acceptable review may a new forward two-identity machine authority be resealed and activated.

No provider call has been made under this post-repair revalidation authority yet. No new machine slot has been created/resealed/activated.

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

Current Owner-required revalidation authority (including scoped CNY-ceiling waiver):

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION_OWNER_DECISION_2026-08-27.md`

Initial independent pre-execution review (F-01 finding):

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_PROVIDER_REVALIDATION_INDEPENDENT_REVIEW_2026-08-27.md`

F-01 offline closure evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_F01_CLOSURE_2026-08-27.md`

F-01 closure independent review (F-02 finding):

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_PROVIDER_REVALIDATION_F01_CLOSURE_INDEPENDENT_REVIEW_2026-08-27.md`

F-02 offline closure evidence:

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_F02_CLOSURE_2026-08-27.md`

F-02 closure independent review (F-03 finding):

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_PROVIDER_REVALIDATION_F02_CLOSURE_INDEPENDENT_REVIEW_2026-08-27.md`

Approved post-V0.1 roadmap:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

## Provider execution state

`ORIGINAL_THREE_CALL_SMOKE = CONSUMED__FAILCLOSED_AFTER_ONE_REAL_REQUEST`

`ORIGINAL_SMOKE_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`HISTORICAL_THREE_CALL_RETEST = CONSUMED__COMPLETED_3OF3_PASS`

`HISTORICAL_THREE_CALL_RETEST_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION = OWNER_REQUIRED__CALL_BOUNDED__CNY_CEILING_WAIVED_FOR_EXACT_SLOT__EXECUTION_BLOCKED_BY_F03`

`POST_REPAIR_REVALIDATION_INDEPENDENT_REVIEW = F01_AND_F02_ACCEPTED__F03_MATERIAL_DEFECT_OPEN`

`POST_REPAIR_REVALIDATION_MACHINE_AUTHORITY = NOT_YET_RESEALED`

`POST_REPAIR_REVALIDATION_PROVIDER_CALLS = 0`

`REAL_DEEPSEEK_PROVIDER_CALLS = NO_CURRENT_ACTIVE_SLOT`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

`FUTURE_PROVIDER_SLOT_WAKE_IDENTITY_REPAIR = TWO_IDENTITY_PATH_VERIFIED`

`STRUCTURED_TRADING_MEMORY_FIDELITY_REPAIR = OFFLINE_VERIFIED`

`ACTIVE_RESPONSE_SCHEMA = JIANGHE_RUNTIME_RESPONSE_V0_2`

`ACTIVE_PROMPT_CONTRACT = KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`

## Current locks

- original smoke and historical retest slots: `CONSUMED / CLOSED / NEVER REACTIVATE`;
- post-repair three-call execution before F-03 repair + fresh acceptable independent review: `LOCKED`;
- post-repair three-call execution before a fresh exact forward two-identity machine authority: `LOCKED`;
- retry, replacement wake, outcome-driven re-asking, call 4: `LOCKED`;
- an `UNKNOWN_AFTER_ATTEMPT_START` state, once recorded during real execution, must terminate the slot and forbid automatic continuation/rerun;
- full V0.1 1998-call replay: `LOCKED`;
- post-V0.1 CU/RB provider replay: `LOCKED`;
- historical execution/PnL semantics: `NOT_YET_APPROVED`;
- learning/policy promotion: `LOCKED`;
- SHADOW/PAPER/broker/account/real money/permanent numeric risk/automatic expansion: `LOCKED`.

## Continuity rule for the next integration lane

Before substantive work or any provider action, refresh current `main`, read `PROJECT_BRAIN_RUNTIME_BRIEF.md`, this file, and the exact task authorities/evidence above.

The immediate next step is ordinary offline engineering closure of F-03 under existing authority. Provider calls must remain zero during the repair. After deterministic verification, obtain a fresh independent high-assurance review. Only if that review returns acceptable may the project reseal a new forward two-identity machine authority and execute the already Owner-approved exact three-call / zero-retry slot. This exact slot has no fixed CNY ceiling by current Owner decision. Full V0.1 remains locked.

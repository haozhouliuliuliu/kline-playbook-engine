# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION__F01_F02_F03_F04_VERIFIED__INDEPENDENT_REVIEW_ACCEPTED__AWAITING_FINAL_PREFLIGHT_AND_FRESH_V03_RESEAL`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = POST_REPAIR_REAL_PROVIDER_REVALIDATION_REQUIRED__INDEPENDENT_REVIEW_ACCEPTED__FINAL_ZERO_COST_PREFLIGHT_AND_FRESH_V03_RESEAL_REQUIRED`

`NEXT_TASK = FINAL_ZERO_COST_PREFLIGHT__RESEAL_FRESH_FORWARD_V03_AUTHORITY__CONSEQUENTIAL_CHECK__ACTIVATE_AND_RUN_APPROVED_3CALL_SLOT_ONCE`

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

No fixed CNY ceiling and no per-request CNY budget guard are required for this slot. Actual provider token/usage accounting must still be retained. This is a scoped exception only; it does not modify the stable default cost doctrine for future paid packages in `PROJECT_DIRECTION.md`. The forward machine-authority form (V0_3) now explicitly encodes the waiver (`OWNER_CNY_CEILING_WAIVED`) instead of fabricating a numeric ceiling; historical and existing V0_2 numeric-spend behavior is unchanged.

## Current repair/review findings

`F01_LOGICAL_RUNTIME_IDENTITY_PATH = INDEPENDENTLY_VERIFIED_CLOSED`

`F02_REQUEST_BOUND_WAKE_FAILCLOSED_EVIDENCE = INDEPENDENTLY_VERIFIED_CLOSED`

`F03_CHILD_BRIDGE_UNKNOWN_ATTEMPT_ACCOUNTING = OFFLINE_VERIFIED_CLOSED`

`F04_POST_RESULT_LEDGER_PERSISTENCE_FAILURE_BARRIER = OFFLINE_REPAIRED__FRESH_REVIEW_PENDING`

F-03 has been repaired offline under existing authority with zero provider calls:

1. a durable provider-attempt ledger (`src/replay_v0_1_provider_attempt_ledger.py`) records `ATTEMPT_STARTED` bound to authority identity, call/sequence, both wake identities, close time, request_id and `retry_count = 0` BEFORE the real bridge child process is launched; if persistence fails the child is not launched;
2. timeout / missing result / malformed result / post-launch handoff failure transitions the attempt to `UNKNOWN_AFTER_ATTEMPT_START`, never represented as zero calls, and reports `provider_attempt_count` / `unknown_after_attempt_start_count` / `known_result_count` / `provider_attempt_state` / `slot_requires_adjudication`;
3. an unknown attempt is a terminal barrier: no retry, no replacement wake, no later call, no call 4, no automatic reseal-as-unattempted;
4. safe non-secret diagnostics are retained without treating absent output as proof of no request;
5. deterministic timeout / no-result / malformed / valid / persistence-failure / terminal-barrier / evidence-distinction regressions were added and pass.

The forward V0_3 machine-authority form (`KPE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_V0_3` / `..._RETEST_V0_3`) now explicitly encodes the Owner CNY-ceiling waiver; historical V0_1/V0_2 authority behavior and identities are unchanged, and the waiver cannot be accidentally applied to historical versions.

The first fresh independent review of the F-03 closure found a further ordinary persistence-window defect before any provider action: failure to record `RESULT_RECEIVED` (and a subsequent failure to record `UNKNOWN_AFTER_ATTEMPT_START`) could leave a durable `ATTEMPT_STARTED` row while allowing a second child launch in the same process. It is repaired offline at execution commit `12d7000801a3711e5e7ac22400a315a2c66e0d16`: the transport sets its terminal barrier before any best-effort unknown transition, result persistence failure also terminally blocks the transport, and terminal evidence treats residual `ATTEMPT_STARTED` rows as nonzero unresolved attempts requiring adjudication. No provider call, credential read, active slot, or machine-authority reseal occurred during this repair. A fresh independent review remains mandatory.

No provider call has been made under this post-repair revalidation authority yet. No new machine slot has been created/resealed/activated. Execution remains locked pending a fresh independent high-assurance review.

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

F-03 offline closure evidence (including the forward V0_3 cost-waiver authority):

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_F03_CLOSURE_2026-08-27.md`

F-04 offline closure evidence (post-result persistence terminal barrier):

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_F04_CLOSURE_2026-08-27.md`

Accepted fresh independent high-assurance review of F-03/F-04 and V0.3 path:

`docs/reviews/JIANGHE_REPLAY_V0_1_POST_REPAIR_PROVIDER_REVALIDATION_F04_CLOSURE_INDEPENDENT_REVIEW_2026-08-27.md`

Approved post-V0.1 roadmap:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

## Provider execution state

`ORIGINAL_THREE_CALL_SMOKE = CONSUMED__FAILCLOSED_AFTER_ONE_REAL_REQUEST`

`ORIGINAL_SMOKE_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`HISTORICAL_THREE_CALL_RETEST = CONSUMED__COMPLETED_3OF3_PASS`

`HISTORICAL_THREE_CALL_RETEST_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION = OWNER_REQUIRED__CALL_BOUNDED__CNY_CEILING_WAIVED_FOR_EXACT_SLOT__F01_F02_F03_F04_VERIFIED__INDEPENDENT_REVIEW_ACCEPTED__FINAL_PREFLIGHT_RESEAL_AND_ACTIVATION_PENDING`

`POST_REPAIR_REVALIDATION_INDEPENDENT_REVIEW = ACCEPTABLE_FOR_FRESH_THREE_CALL_SLOT_PREPARATION__F01_F02_F03_F04_COVERED`

`POST_REPAIR_REVALIDATION_MACHINE_AUTHORITY = NOT_YET_RESEALED`

`POST_REPAIR_REVALIDATION_PROVIDER_CALLS = 0`

`POST_REPAIR_REVALIDATION_CNY_CEILING = OWNER_WAIVED_FOR_THIS_EXACT_SLOT`

`REAL_DEEPSEEK_PROVIDER_CALLS = NO_CURRENT_ACTIVE_SLOT`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

`FUTURE_PROVIDER_SLOT_WAKE_IDENTITY_REPAIR = TWO_IDENTITY_PATH_VERIFIED`

`STRUCTURED_TRADING_MEMORY_FIDELITY_REPAIR = OFFLINE_VERIFIED`

`ACTIVE_RESPONSE_SCHEMA = JIANGHE_RUNTIME_RESPONSE_V0_2`

`ACTIVE_PROMPT_CONTRACT = KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`

## Current locks

- original smoke and historical retest slots: `CONSUMED / CLOSED / NEVER REACTIVATE`;
- post-repair three-call execution before final zero-cost preflight, fresh exact forward V0_3 two-identity authority and immediate consequential-action verification: `LOCKED`;
- post-repair three-call execution before a fresh exact forward V0_3 two-identity machine authority: `LOCKED`;
- retry, replacement wake, outcome-driven re-asking, call 4: `LOCKED`;
- an `UNKNOWN_AFTER_ATTEMPT_START` state, once recorded during real execution, must terminate the slot and forbid automatic continuation/rerun;
- full V0.1 1998-call replay: `LOCKED`;
- post-V0.1 CU/RB provider replay: `LOCKED`;
- historical execution/PnL semantics: `NOT_YET_APPROVED`;
- learning/policy promotion: `LOCKED`;
- SHADOW/PAPER/broker/account/real money/permanent numeric risk/automatic expansion: `LOCKED`.

## Continuity rule for the next integration lane

Before substantive work or any provider action, refresh current `main`, read `PROJECT_BRAIN_RUNTIME_BRIEF.md`, this file, and the exact task authorities/evidence above.

The fresh independent high-assurance review accepted the F-03/F-04 closure and forward V0_3 cost-waiver authority path at `66d2530f3c3633e130e5d57922b4a725e7bf8aef`, with zero provider/network calls. The next steps are final zero-cost preflight, resealing a new exact forward V0_3 two-identity machine authority (explicitly encoding the Owner CNY-ceiling waiver), and immediate final pre-execution refresh/verification before any credential/network capability is used. No provider call or slot activation may occur before those steps complete. This exact slot has no fixed CNY ceiling by current Owner decision. Full V0.1 remains locked.

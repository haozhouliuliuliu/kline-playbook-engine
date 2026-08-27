# CURRENT_STATE

`DYNAMIC_STATE_OWNER = CURRENT_STATE.md`

As of: `2026-08-27`

This file is the single canonical owner for volatile project state: current activity, work package, phase, locks, execution hold state and next task.

Stable product direction, architecture, tooling and governance live in their own canonical owners and must not copy these values back out of this file.

## Current activity

`CURRENT_ACTIVITY = POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION__F01_F02_F03_F04_VERIFIED__F05_RUNNER_TIMESTAMP_DEFECT_FOUND_AND_REPAIRED_OFFLINE__CANONICAL_DATASET_FOUND_AND_VERIFIED__FINAL_PREFLIGHT_PASS_ZERO_COST__V03_AUTHORITY_NONACTIVE__EXECUTION_LOCKED_PENDING_FRESH_REVIEW__NO_PROVIDER_ATTEMPT`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = POST_REPAIR_REAL_PROVIDER_REVALIDATION_REQUIRED__INDEPENDENT_REVIEW_ACCEPTED__F05_EXECUTION_CRITICAL_DEFECT_FOUND_AND_REPAIRED_OFFLINE__FRESH_INDEPENDENT_REVIEW_REQUIRED_BEFORE_ANY_PAID_EXECUTION`

`NEXT_TASK = FRESH_INDEPENDENT_HIGH_ASSURANCE_REVIEW_OF_F05_CLOSURE_AND_UPDATED_EXECUTION_COMMIT__THEN_RESEAL_ACTIVATE_AND_RUN_APPROVED_3CALL_SLOT_ONCE`

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

`F04_POST_RESULT_LEDGER_PERSISTENCE_FAILURE_BARRIER = OFFLINE_REPAIRED__INDEPENDENT_REVIEW_ACCEPTED`

`F05_RUNNER_HARNESS_ATTEMPT_IDENTITY_TIMESTAMP_DEFECT = OFFLINE_REPAIRED__FRESH_INDEPENDENT_REVIEW_REQUIRED`

F-03 has been repaired offline under existing authority with zero provider calls:

1. a durable provider-attempt ledger (`src/replay_v0_1_provider_attempt_ledger.py`) records `ATTEMPT_STARTED` bound to authority identity, call/sequence, both wake identities, close time, request_id and `retry_count = 0` BEFORE the real bridge child process is launched; if persistence fails the child is not launched;
2. timeout / missing result / malformed result / post-launch handoff failure transitions the attempt to `UNKNOWN_AFTER_ATTEMPT_START`, never represented as zero calls, and reports `provider_attempt_count` / `unknown_after_attempt_start_count` / `known_result_count` / `provider_attempt_state` / `slot_requires_adjudication`;
3. an unknown attempt is a terminal barrier: no retry, no replacement wake, no later call, no call 4, no automatic reseal-as-unattempted;
4. safe non-secret diagnostics are retained without treating absent output as proof of no request;
5. deterministic timeout / no-result / malformed / valid / persistence-failure / terminal-barrier / evidence-distinction regressions were added and pass.

The forward V0_3 machine-authority form (`KPE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_V0_3` / `..._RETEST_V0_3`) now explicitly encodes the Owner CNY-ceiling waiver; historical V0_1/V0_2 authority behavior and identities are unchanged, and the waiver cannot be accidentally applied to historical versions.

The first fresh independent review of the F-03 closure found a further ordinary persistence-window defect before any provider action: failure to record `RESULT_RECEIVED` (and a subsequent failure to record `UNKNOWN_AFTER_ATTEMPT_START`) could leave a durable `ATTEMPT_STARTED` row while allowing a second child launch in the same process. It is repaired offline at execution commit `12d7000801a3711e5e7ac22400a315a2c66e0d16`: the transport sets its terminal barrier before any best-effort unknown transition, result persistence failure also terminally blocks the transport, and terminal evidence treats residual `ATTEMPT_STARTED` rows as nonzero unresolved attempts requiring adjudication. No provider call, credential read, active slot, or machine-authority reseal occurred during this repair. A fresh independent review remains mandatory.

At the final pre-execution gate, after dataset restoration and a zero-cost preflight PASS, a further material pre-execution defect (F-05) was found and repaired offline: `tools/run_replay_v0_1_provider_smoke.py` constructed the harness `attempt_identities` with `timezone.utc` without importing `timezone`, raising `NameError` before any bridge child launch. The path is only reachable with `--transport harness`, so prior mock/fake-transport unit tests and reviews did not exercise it. Repair commit `c5338aa` adds the import and extracts `_build_attempt_identities(authority)` with a deterministic timezone-aware regression. The durable attempt ledger recorded **0 provider attempts**; no provider/network/credential activity occurred. Because this is an execution-critical change, the exactly-once three-call slot must wait for a fresh isolated high-assurance review of the F-05 closure before reseal/activation/execution.

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

F-05 offline closure evidence (runner harness attempt-identity timestamp defect, zero provider attempt):

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_F05_CLOSURE_2026-08-27.md`

Final zero-cost preflight failure evidence (no provider attempt):

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_FINAL_PREFLIGHT_BLOCKER_2026-08-27.md`

Canonical dataset local restoration verification (original dataset found + identity verified, no rebuild):

`docs/evidence/JIANGHE_CANONICAL_DATASET_LOCAL_RESTORATION_VERIFICATION_2026-08-27.md`

Final zero-cost preflight PASS evidence (explicit dataset paths, deterministic blueprint):

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_FINAL_PREFLIGHT_2026-08-27.md`

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_FINAL_PREFLIGHT_BLUEPRINT_2026-08-27.json`

Fresh forward V0_3 two-identity RETEST machine authority (non-ACTIVE):

`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_SLOT_V0_3.json`

Approved post-V0.1 roadmap:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

## Provider execution state

`ORIGINAL_THREE_CALL_SMOKE = CONSUMED__FAILCLOSED_AFTER_ONE_REAL_REQUEST`

`ORIGINAL_SMOKE_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`HISTORICAL_THREE_CALL_RETEST = CONSUMED__COMPLETED_3OF3_PASS`

`HISTORICAL_THREE_CALL_RETEST_MACHINE_AUTHORITY = REVOKED__TERMINAL`

`POST_REPAIR_THREE_CALL_PROVIDER_REVALIDATION = OWNER_REQUIRED__CALL_BOUNDED__CNY_CEILING_WAIVED_FOR_EXACT_SLOT__F01_F02_F03_F04_VERIFIED__F05_REPAIRED_OFFLINE__DATASET_RESTORED_AND_VERIFIED__FINAL_PREFLIGHT_PASS_ZERO_COST__V03_AUTHORITY_NONACTIVE__EXECUTION_LOCKED_PENDING_FRESH_REVIEW__NO_PROVIDER_ATTEMPT`

`POST_REPAIR_REVALIDATION_INDEPENDENT_REVIEW = ACCEPTABLE_FOR_FRESH_THREE_CALL_SLOT_PREPARATION__F01_F02_F03_F04_COVERED__F05_FRESH_REVIEW_PENDING`

`POST_REPAIR_REVALIDATION_MACHINE_AUTHORITY = AUTHORED_NON_ACTIVE__REQUIRES_RESEAL_AGAINST_F05_EXECUTION_COMMIT_AFTER_FRESH_REVIEW`

`POST_REPAIR_REVALIDATION_PROVIDER_CALLS = 0`

`POST_REPAIR_REVALIDATION_PROVIDER_ATTEMPTS = 0`

`POST_REPAIR_REVALIDATION_CNY_CEILING = OWNER_WAIVED_FOR_THIS_EXACT_SLOT`

`CANONICAL_DATASET_LOCAL_AVAILABILITY = ORIGINAL_ACCEPTED_DATASET_FOUND_AND_VERIFIED`

`REAL_DEEPSEEK_PROVIDER_CALLS = NO_CURRENT_ACTIVE_SLOT`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

`FUTURE_PROVIDER_SLOT_WAKE_IDENTITY_REPAIR = TWO_IDENTITY_PATH_VERIFIED`

`STRUCTURED_TRADING_MEMORY_FIDELITY_REPAIR = OFFLINE_VERIFIED`

`ACTIVE_RESPONSE_SCHEMA = JIANGHE_RUNTIME_RESPONSE_V0_2`

`ACTIVE_PROMPT_CONTRACT = KPE_JIANGHE_TRADING_ONLY_PROMPT_V0_3`

## Current locks

- original smoke and historical retest slots: `CONSUMED / CLOSED / NEVER REACTIVATE`;
- post-repair three-call execution before a fresh isolated high-assurance review of the F-05 closure and updated execution commit: `LOCKED`;
- post-repair three-call execution before resealing/activating the fresh exact forward V0_3 two-identity machine authority against the F-05 execution commit: `LOCKED`;
- retry, replacement wake, outcome-driven re-asking, call 4: `LOCKED`;
- an `UNKNOWN_AFTER_ATTEMPT_START` state, once recorded during real execution, must terminate the slot and forbid automatic continuation/rerun;
- full V0.1 1998-call replay: `LOCKED`;
- post-V0.1 CU/RB provider replay: `LOCKED`;
- historical execution/PnL semantics: `NOT_YET_APPROVED`;
- learning/policy promotion: `LOCKED`;
- SHADOW/PAPER/broker/account/real money/permanent numeric risk/automatic expansion: `LOCKED`.

## Continuity rule for the next integration lane

Before substantive work or any provider action, refresh current `main`, read `PROJECT_BRAIN_RUNTIME_BRIEF.md`, this file, and the exact task authorities/evidence above.

The fresh independent high-assurance review accepted the F-03/F-04 closure and forward V0_3 cost-waiver authority path. The original accepted canonical dataset was located in the local `data/canonical/` directory and mechanically verified against the accepted manifest/corpus identities (manifest `7510a4a9…d324`, corpus `1d03fd23…74a8`, 32,980 partitions/parquet, exact `cu`/`SHFE.cu2406` frozen slice). The final zero-cost preflight passed deterministically against the verified dataset with explicit `--manifest`/`--parquet-root` paths, producing the persisted blueprint (`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_FINAL_PREFLIGHT_BLUEPRINT_2026-08-27.json`) with exactly three governed wakes (logical + runtime identities, exact close times, 4 PNGs each) and `real_provider_calls = 0`. A non-ACTIVE V0_3 RETEST authority (`docs/evidence/JIANGHE_REPLAY_V0_1_POST_REPAIR_REVALIDATION_SLOT_V0_3.json`, identity `24d2409a…c94d`) explicitly encodes the Owner CNY-ceiling waiver.

At the final pre-execution gate a further material pre-execution defect (F-05) was found and repaired offline at commit `c5338aa`: the runner's harness attempt-identity construction used `timezone.utc` without importing `timezone` (`NameError` before any bridge child launch; durable attempt ledger recorded 0 provider attempts). Because this is an execution-critical change, the exactly-once three-call slot must wait for a fresh isolated high-assurance review of the F-05 closure; only after that review returns acceptable may the project reseal/activate the fresh V0_3 authority against the updated execution commit and run the approved three-call slot. No provider call, credential read, slot activation, or reseal has occurred. Full V0.1 remains locked.

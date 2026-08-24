# JIANGHE STAGE-A LIVE LANE INTEGRATION CLOSURE V0.1

Status: `INTEGRATED__PROJECT_BRAIN_ACCEPTED`
Date: 2026-08-24
Tool decision: `USE_EXISTING`

## Integrated authority

```text
PR_29_MERGE_COMMIT=72f96d200f8ed8d3f6da042597344f828b54ae25
LAST_MATERIAL_STATE_COMMIT=72f96d200f8ed8d3f6da042597344f828b54ae25
STAGE_A_LIVE_LANE=INTEGRATED__PROJECT_BRAIN_ACCEPTED
STAGE_A_REMOTE_LEDGER=INTEGRATED
STAGE_A_REMOTE_CAS=INTEGRATED
STAGE_A_REMOTE_REREAD_VERIFICATION=INTEGRATED
STAGE_A_CRASH_ACCOUNTING=INTEGRATED
STAGE_A_SINGLE_SLOT_LIVE_WORKFLOW=INTEGRATED
STAGE_A_FIXED_REMOTE_REF=refs/heads/stage-a-live-state-v0-1
```

The merged lane is explicit single-slot, manual `workflow_dispatch` only, `main` only, and uses the protected `stage-a-readiness` environment. Provider/model selection remains frozen-plan governed. The lane durably writes and re-reads `NETWORK_ATTEMPT_STARTED` before provider transport. An incomplete start remains attempted, non-retryable and conservatively accounted at the full frozen worst-case ceiling.

## One-time bootstrap

The fixed remote state ref must exist before the production live workflow is used. Bootstrap is separate from the live workflow and requires zero provider credentials, zero provider calls and CNY0 spend.

```text
REMOTE_STATE_BOOTSTRAP=REQUIRED_ONCE_BEFORE_FIRST_CALL
REMOTE_STATE_BOOTSTRAP_METHOD=GitRemoteLedgerStore.compare_and_swap(expected_head=None,ledger_bytes=RemoteExecutionLedger.empty(plan).to_bytes())
REMOTE_STATE_BOOTSTRAP_VERIFICATION=store.load(plan)__EXACT_HEAD__EXACT_EMPTY_LEDGER_BYTES__ZERO_EVENTS__ZERO_ATTEMPTS__ZERO_ACCOUNTED_CNY
NAMED_initialize_empty_state_WRAPPER=NOT_REQUIRED
FORCE_PUSH=FORBIDDEN
```

If the fixed ref already exists, it must not be overwritten or bootstrapped again. It must be loaded and fully verified. Non-empty or invalid state stops execution.

## Verified Linux evidence

GitHub Actions run `32703991488` was read from GitHub rather than inferred from local state.

```text
HEAD_SHA=1d74e60bb857bc593887f2121fd2df516331914c
FOCUSED_TESTS=PASS__114_OF_114__LINUX_CI_PASS
FULL_CI=PASS__RUN_32703991488__1343_TESTS__27_SKIPPED__CANONICAL_LINUX_FULL_SUITE
DIFF_HYGIENE=PASS__ORIGIN_MAIN_TO_HEAD
LIVE_CALLS=0
PAID_SPEND=CNY_0
BSP_003_PRESERVED=YES
RESEARCH_SEMANTICS_CHANGED=NO
```

## Current execution boundary

```text
CURRENT_WORK_PACKAGE=RMB100_STAGE_A__FIRST_LIVE_SLOT_EXECUTION_AND_EVIDENCE_REVIEW
NEXT_NORMAL_PHASE=bootstrap_empty_remote_state_then_execute_one_explicit_authorized_stage_a_slot
STAGE_A_NETWORK_EXECUTION=AUTHORIZED_FOR_ONE_EXPLICIT_SLOT_AFTER_SUCCESSFUL_EMPTY_REMOTE_STATE_BOOTSTRAP__NO_AUTOMATIC_NEXT_SLOT
STAGE_A_STATUS=AUTHORIZED__LIVE_LANE_INTEGRATED__REMOTE_STATE_BOOTSTRAP_PENDING__NOT_STARTED
LIVE_CALLS=0
PAID_SPEND_CNY=0
```

The accepted lane changes no frozen Stage-A input, provider pricing, evaluator semantics, research semantics, budget, retry rule, outcome boundary, Validation/Final/Shadow lock, broker boundary or real-money boundary.

```text
AUTOMATIC_RETRY=FORBIDDEN
AUTOMATIC_BUDGET_EXTENSION=FORBIDDEN
OUTCOME_ACCESS=NO
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

# JIANGHE Stage-A V0.2 Integration and Remote Bootstrap Closure V0.1

Status: `COMPLETE__READY_FOR_ONE_EXPLICIT_NEXT_LIVE_SLOT`
Date: 2026-08-24

## Integrated implementation

```text
PR_31=MERGED
PR_31_MERGE_COMMIT=84fd0da93286801f4fa123a1165dbc84170cadb6
V0_2_PLAN_IDENTITY=9736e1cf75372ec13f524a971ee1d1c036a1d5e6ac51b250a6890a9ecf76d913
V0_2_COMMON_MAX_COMPLETION_TOKENS=1024
V0_2_FUTURE_EXECUTABLE_CALLS=14
V0_1_HISTORY_MUTATED=NO
```

PR #31 passed the Linux Stage-A Offline CI at head `8dbd2e986843a6d2a1d641e886771b168ed1ecf2`, including the deterministic V0.1/V0.2 plan checks, focused/adversarial Stage-A tests, canonical Linux full suite and diff hygiene. No provider call or paid spend occurred during implementation.

## Carry-forward baseline

Attempt 001 remains immutable:

```text
PROVIDER=DEEPSEEK
SLOT=1
EVIDENCE_IDENTITY=d36c1fbbb1cd639e48a6f049f7df1be3bb95d9f346d75bbb85e25451fba9dc55
LIVE_CALLS_CARRY_FORWARD=1
STAGE_ACCOUNTED_CNY_CARRY_FORWARD=0.219222
DEEPSEEK_PROVIDER_ATTEMPTS_CARRY_FORWARD=1
AUTOMATIC_RETRY=FORBIDDEN
REPLACEMENT_CALL=FORBIDDEN
```

## V0.2 durable state bootstrap

The fixed production ref was initialized once using the merged repository implementation, without provider credentials or model transport:

```text
REMOTE_REF=refs/heads/stage-a-live-state-v0-2
REMOTE_HEAD=48ff66cf7424c6ba99581fb25f6ae5dc6e790385
LEDGER_SCHEMA=JIANGHE_STAGE_A_REMOTE_EXECUTION_LEDGER_V0_2
LEDGER_PLAN_IDENTITY=9736e1cf75372ec13f524a971ee1d1c036a1d5e6ac51b250a6890a9ecf76d913
LEDGER_PLAN_SHA256=613b581c3e9a99f910b572c2415d828a131ca694dfe3c1c42706a97443204c6a
LEDGER_CARRY_FORWARD_IDENTITY=997296a2690539577f8684b268bddce26e1b9f299b64de574faf53c3fdbfefd2
NEW_V0_2_EVENTS=0
```

The empty V0.2 event list does **not** reset project accounting: the plan-bound carry-forward baseline still represents DeepSeek Slot 1, one live attempt and CNY0.219222 conservative Stage-A accounting.

Bootstrap used no provider secrets, no model endpoint and no paid action. V0.1 remote state remains immutable.

## Current execution boundary

```text
STAGE_A_STATUS=STARTED__V0_2_READY_FOR_NEXT_EXPLICIT_SLOT
LIVE_CALLS=1
PAID_SPEND_CNY=0.219222
PAID_SPEND_SEMANTICS=CONSERVATIVE_STAGE_A_ACCOUNTING__NOT_PROVIDER_ACTUAL_BILLING
NEXT_CALL_MODE=ONE_EXPLICIT_SLOT_ONLY
AUTOMATIC_NEXT_SLOT=FORBIDDEN
AUTOMATIC_RETRY=FORBIDDEN
OUTCOME_ACCESS=NO
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

The project brain may now authorize one unattempted V0.2 Stage-A slot under the existing Owner paid-call authorization and unchanged CNY100 / Stage-A CNY18 / provider CNY6 caps.

# PROJECT_BRAIN_RUNTIME_BRIEF

> Compact live pointer for the project brain. Current GitHub `main` remains the sole dynamic fact source.

## Mandatory runtime rule

Before every substantive project reply after takeover:
1. fetch current `main` HEAD;
2. fetch this file from current `main`;
3. do not use chat memory as mutable project authority;
4. for state/architecture/locks/next work/worker/model/provider/tool questions, refresh `CURRENT_STATE.md` and named authority;
5. for live Stage-A state, also refresh `refs/heads/stage-a-live-state-v0-2` before stating attempted slots/current remote head/accounting;
6. fresh conversations read `00_READ_FIRST.md` first and complete its read-only takeover; `PROJECT_HANDOFF_CURRENT.md` is read last.

## Handoff readiness

```text
FRESH_CONVERSATION_HANDOFF=READY
TAKEOVER_BOOTSTRAP=00_READ_FIRST.md
HANDOFF_CONTINUITY_POINTER=PROJECT_HANDOFF_CURRENT.md__READ_LAST
CHAT_MEMORY_AS_AUTHORITY=FORBIDDEN
FIRST_TAKEOVER_TURN=READ_ONLY__REPORT_THEN_WAIT_FOR_OWNER_ACCEPTANCE
```

## Current live pointer

```text
LAST_MATERIAL_STATE_COMMIT=f26531e52259e82989c1202b55056eb3e282c039
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE=Skeleton_v1.0_PLUS_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
CURRENT_WORK_PACKAGE=RMB100_STAGE_A__V0_2_LIVE_FIDELITY_EXECUTION
NEXT_NORMAL_PHASE=KIMI_OPERATIONAL_PROVIDER_SMOKE__EVIDENCE_REVIEW__THEN_NEXT_DECISION
OWNER_ACTION=RUN_ONLY_KIMI_SLOT_1_WHEN_REQUESTED_BY_PROJECT_BRAIN
TOOL_DECISION=USE_EXISTING
LIMIT_012=ACTIVE__REAL_MODEL_JIANGHE_FIDELITY_IN_PROGRESS__NO_SCOREABLE_MODEL_EVIDENCE_YET
```

`LAST_MATERIAL_STATE_COMMIT` points to the latest substantive attempt/evidence adjudication. Later handoff/governance-only commits may advance `main` without changing that marker.

## Stage-A V0.2 execution state

```text
PR_31_V0_2_MERGE_COMMIT=84fd0da93286801f4fa123a1165dbc84170cadb6
V0_2_PLAN_IDENTITY=9736e1cf75372ec13f524a971ee1d1c036a1d5e6ac51b250a6890a9ecf76d913
V0_2_REMOTE_REF=refs/heads/stage-a-live-state-v0-2
V0_2_REMOTE_HEAD=ea1364e04e378781d8cf9f1b43a9ce3f0ef1679e
LIVE_CALLS=2
PAID_SPEND_CNY=0.270021
PAID_SPEND_SEMANTICS=CONSERVATIVE_ACCOUNTING__ACTUAL_PROVIDER_WALLET_BILL_UNKNOWN
AUTOMATIC_RETRY=FORBIDDEN
AUTOMATIC_NEXT_SLOT=FORBIDDEN
```

The remote head above was current after Attempt 002 at handoff preparation. A fresh conversation must still reread the remote ref before treating that SHA as current.

## Attempt 001 — DeepSeek immutable history

Authority: `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_001_DEEPSEEK_ADJUDICATION_V0_1.md`.

```text
PROVIDER=DEEPSEEK
MODEL=deepseek-v4-flash-vision-exp
SLOT=1
TRACK=OPERATIONAL_PROVIDER
ACCOUNTED_CNY=0.219222
EVIDENCE_IDENTITY=d36c1fbbb1cd639e48a6f049f7df1be3bb95d9f346d75bbb85e25451fba9dc55
SCOREABLE=NO__V0_1_PROVIDER_RESPONSE_CONTRACT_DEFECT
AUTOMATIC_RETRY=FORBIDDEN
REPLACEMENT_CALL=FORBIDDEN
DEEPSEEK_FATAL_FAIL=NOT_ADJUDICATED_FROM_ATTEMPT_001
```

Do not reinterpret Attempt 001 as proof that the DeepSeek model/route is unavailable. The request reached 2xx provider JSON, but V0.1 failed to preserve enough safe response-envelope evidence for adjudication.

## Attempt 002 — MiniMax fatal stop

Authority: `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_002_MINIMAX_ADJUDICATION_V0_1.md`.

```text
PROVIDER=MINIMAX
MODEL=MiniMax-M3
SLOT=1
TRACK=OPERATIONAL_PROVIDER
TERMINAL_STATUS=NON_SCOREABLE_NORMALIZER
HTTP_STATUS_CLASS=2xx
RESOLVED_MODEL=MiniMax-M3
PROVIDER_REQUEST_ID=06db5dc323f11955ace313c34f79795a
FINISH_REASON=length
FINAL_CONTENT_STATE=TEXT_NONEMPTY
PROMPT_TOKENS=7999
COMPLETION_TOKENS=1024
REASONING_TOKEN_COUNT=914
LATENCY_MS=10364
ACCOUNTED_CNY=0.050799
CUMULATIVE_STAGE_A_ACCOUNTED_CNY=0.270021
EVIDENCE_IDENTITY=8a5f9792a9e41c32bcd16ce6121f1c47dade7185848d4386c9750dc002488bb6
ERROR=raw_response 必须是合法 JSON 对象
MINIMAX_FATAL_FAIL=YES__UNSCOREABLE_NORMALIZED_RESPONSE
MINIMAX_STAGE_A_STATUS=ELIMINATED
MINIMAX_FURTHER_STAGE_A_CALLS=FORBIDDEN
MINIMAX_STAGE_B_BUDGET=NONE
AUTOMATIC_RETRY=FORBIDDEN
```

MiniMax transport/model resolution worked. Elimination is specifically the frozen Stage-A funnel consequence of an unscoreable normalized response; it is not a claim that the MiniMax API is unavailable.

## Remaining provider state

```text
KIMI_K3=CANDIDATE__NO_REAL_ATTEMPT_YET
KIMI_REMAINING_SLOTS=1,2,3,4,5
DEEPSEEK_V4_FLASH_VISION_EXP=CANDIDATE__ATTEMPT_001_UNSCOREABLE_DUE_V0_1_PROTOCOL_DEFECT
DEEPSEEK_REMAINING_SLOTS=2,3,4,5
MINIMAX_M3=ELIMINATED__NO_FURTHER_STAGE_A_CALLS
NEXT_EXPLICIT_SLOT=KIMI:1
```

No provider/model is `VERIFIED` or `ADOPTED` yet. No scoreable real-model Jianghe fidelity evidence exists yet.

## Authorization / caps

```text
OWNER_PAID_CALL_DECISION=AUTHORIZED
PAID_CALL_AUTHORIZATION_ID=OWNER-PAID-JIANGHE-FIDELITY-20260824-V01
PAID_CALL_AUTHORIZATION_EXPIRES=2026-08-31T00:00:00+08:00
TOTAL_HARD_API_SPEND_CAP_CNY=100.00
STAGE_A_MAX_SPEND_CNY=18.00
STAGE_A_MAX_CALLS=15
MAX_STAGE_A_CALLS_PER_PROVIDER=5
MAX_STAGE_A_SPEND_PER_PROVIDER_CNY=6.00
CURRENT_STAGE_A_ACCOUNTED_CNY=0.270021
DEEPSEEK_ACCOUNTED_CNY=0.219222
MINIMAX_ACCOUNTED_CNY=0.050799
KIMI_ACCOUNTED_CNY=0
NEW_RECHARGE_REQUIRED=NO
```

Owner-reported wallet balances at the latest funded checkpoint were CNY10 each for Kimi/DeepSeek/MiniMax. Do not confuse wallet funding with API-consumption accounting and do not request recharge without current evidence that it is needed.

## Closed pre-spend work

```text
PRE_SPEND_REPAIR_REAUDIT=PASS
BSP_001_TO_005=CLOSED
RSP_001_TO_002=CLOSED
LIMIT_015=RESOLVED
```

Do not reopen a rolling whole-repo audit by default.

## Locks

```text
OUTCOME_ACCESS=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

## Exact next work after takeover acceptance

1. Refresh current `main`, this brief, `CURRENT_STATE.md`, the V0.2 frozen plan and the live V0.2 remote ledger.
2. Confirm no newer authority supersedes `NEXT_EXPLICIT_SLOT=KIMI:1`.
3. If unchanged, Owner manually dispatches `.github/workflows/stage-a-live-slot.yml` on `main` for `KIMI` slot `1`, exactly once.
4. Never rerun DeepSeek:1 or MiniMax:1; never dispatch another MiniMax Stage-A slot.
5. Project brain reads Kimi:1 durable ledger/evidence and adjudicates before any later paid call.

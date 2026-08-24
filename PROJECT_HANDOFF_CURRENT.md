# PROJECT_HANDOFF_CURRENT

> Derived continuity pointer only. **handoff != authority**.
> Current GitHub `main`, `PROJECT_BRAIN_RUNTIME_BRIEF.md`, `CURRENT_STATE.md`, the current V0.2 frozen plan, durable live ledger, and formal attempt adjudications always win.

## Fresh-conversation rule

A fresh project-brain conversation must:

1. read `00_READ_FIRST.md` first;
2. fetch current `main` HEAD;
3. complete the active read-only takeover sequence declared there;
4. read this handoff **last**;
5. report understanding / contradictions and then stop for Owner acceptance before executing new work.

Do not reconstruct mutable project state from this file alone.

## Handoff checkpoint — 2026-08-24 after Attempt 002

The project is no longer pre-spend or pre-live. Real-model Stage A has **started**.

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
CURRENT_WORK_PACKAGE=RMB100_STAGE_A__V0_2_LIVE_FIDELITY_EXECUTION
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
STAGE_A_STATUS=STARTED__ATTEMPTS_001_AND_002_RECORDED__MINIMAX_ELIMINATED
LIMIT_012=ACTIVE__NO_SCOREABLE_MODEL_EVIDENCE_YET
LIVE_CALLS=2
STAGE_A_ACCOUNTED_CNY=0.270021
OUTCOME_ACCESS=NO
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

Current detailed mutable authority:

- `PROJECT_BRAIN_RUNTIME_BRIEF.md`
- `CURRENT_STATE.md`
- `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`

## What changed during the outgoing conversation

### 1. Pre-spend / live-lane engineering was closed

The conversation inherited an already authorized Stage-A funnel and finished the missing execution-safety path:

- PR #26 evidence export integrated.
- PR #28 state/readiness authority sync merged.
- PR #29 crash-resilient live execution lane merged.
- project-brain live-lane acceptance contract merged.
- GitHub Environment `stage-a-readiness` has the three provider secret names configured and is main-restricted; secret values were never read into project evidence.
- Owner reported Kimi / DeepSeek / MiniMax wallet balances as CNY10 each; this is Owner-reported balance evidence, not machine-verification of every provider and not API-consumption spend.
- Fixed remote write-ahead state, CAS/non-force concurrency protection, remote byte reread verification, secret-free ledger/evidence and single-slot manual workflow are integrated.

Historical live-lane acceptance authority:

- `docs/reviews/JIANGHE_STAGE_A_LIVE_LANE_PROJECT_BRAIN_ACCEPTANCE_CONTRACT_V0_1.md`

### 2. First real paid attempt — DeepSeek Slot 1

Attempt 001 was a real DeepSeek paid-model request:

```text
WORKFLOW_RUN_ID=32709432759
PROVIDER=DEEPSEEK
MODEL=deepseek-v4-flash-vision-exp
SLOT=1
TRACK=OPERATIONAL_PROVIDER
ACCOUNTED_CNY=0.219222
EVIDENCE_IDENTITY=d36c1fbbb1cd639e48a6f049f7df1be3bb95d9f346d75bbb85e25451fba9dc55
TERMINAL_STATUS=TRANSPORT_FAILURE
AUTOMATIC_RETRY=FORBIDDEN
REPLACEMENT_CALL=FORBIDDEN
```

Important interpretation:

- the request reached a 2xx provider JSON response;
- the requested DeepSeek model/route is valid current first-party API surface;
- V0.1 constructed provider evidence only after successful final-content extraction, so it lost the exact content null/empty/non-text distinction, resolved model, request id, usage and finish reason;
- therefore Attempt 001 **must not** be used to claim DeepSeek itself fatally failed;
- DeepSeek Slot 1 is nevertheless permanently attempted/non-retryable and its CNY0.219222 conservative accounting is immutable.

Authority:

- `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_001_DEEPSEEK_ADJUDICATION_V0_1.md`

### 3. Owner approved Stage-A V0.2 provider-response compatibility correction

After Attempt 001, the project did a bounded three-provider contract audit rather than patching only DeepSeek. Owner explicitly approved the new V0.2 research-design version so testing could continue quickly without erasing the first attempt.

V0.2 changes only provider-response compatibility / output-budget mechanics. Jianghe semantics, fixture, synthetic OHLC, visual bytes, structured observation, track isolation, scoring, provider/model set, hard budgets and outcome locks remain unchanged.

Key V0.2 contract:

```text
COMMON_MAX_COMPLETION_TOKENS=1024
KIMI:kimi-k3=reasoning_effort_max__strict_json_schema__1024
DEEPSEEK:deepseek-v4-flash-vision-exp=thinking_enabled__reasoning_effort_max__json_object__1024
MINIMAX:MiniMax-M3=thinking_adaptive__reasoning_split_true__1024
SAFE_2XX_MECHANICAL_RESPONSE_EVIDENCE=REQUIRED
RAW_REASONING_TEXT_IN_SAFE_EVIDENCE=FORBIDDEN
AUTOMATIC_RETRY=FORBIDDEN
```

Authorities:

- `docs/reviews/JIANGHE_STAGE_A_V0_2_PROVIDER_RESPONSE_COMPATIBILITY_OWNER_DECISION.md`
- `docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_2.json`
- `docs/reviews/JIANGHE_STAGE_A_V0_2_INTEGRATION_AND_REMOTE_BOOTSTRAP_CLOSURE_V0_1.md`

PR #31 merged V0.2 implementation:

```text
PR_31_MERGE_COMMIT=84fd0da93286801f4fa123a1165dbc84170cadb6
V0_2_PLAN_IDENTITY=9736e1cf75372ec13f524a971ee1d1c036a1d5e6ac51b250a6890a9ecf76d913
V0_2_PLAN_SHA256=613b581c3e9a99f910b572c2415d828a131ca694dfe3c1c42706a97443204c6a
V0_2_REMOTE_REF=refs/heads/stage-a-live-state-v0-2
```

V0.1 plan/ref remain immutable history.

### 4. V0.2 remote state was initialized and then used for Attempt 002

V0.2 bootstrap started at an empty event list but mechanically carried Attempt 001 forward through the plan baseline. It never reset calls/spend to zero.

Current V0.2 remote head after Attempt 002:

```text
V0_2_REMOTE_REF=refs/heads/stage-a-live-state-v0-2
V0_2_REMOTE_HEAD=ea1364e04e378781d8cf9f1b43a9ce3f0ef1679e
```

Always refresh this ref before stating current attempt/accounting facts. Do not rely on the older bootstrap head in the integration-closure document.

### 5. Second real paid attempt — MiniMax Slot 1

Attempt 002 was a real MiniMax-M3 call under V0.2. It proved the transport/model route works but failed the frozen qualification contract:

```text
PROVIDER=MINIMAX
MODEL=MiniMax-M3
SLOT=1
TRACK=OPERATIONAL_PROVIDER
HTTP_STATUS_CLASS=2xx
RESOLVED_MODEL=MiniMax-M3
PROVIDER_REQUEST_ID=06db5dc323f11955ace313c34f79795a
FINISH_REASON=length
FINAL_CONTENT_STATE=TEXT_NONEMPTY
PROMPT_TOKENS=7999
COMPLETION_TOKENS=1024
REASONING_TOKEN_COUNT=914
LATENCY_MS=10364
ATTEMPT_ACCOUNTED_CNY=0.050799
EVIDENCE_IDENTITY=8a5f9792a9e41c32bcd16ce6121f1c47dade7185848d4386c9750dc002488bb6
TERMINAL_STATUS=NON_SCOREABLE_NORMALIZER
NORMALIZED_DECISION_IDENTITY=null
```

The output hit the 1024-token ceiling (`finish_reason=length`); 914 completion tokens were reported as reasoning. Final content was non-empty but not valid governed JSON, so the strict normalizer could not score it.

The frozen RMB100 funnel explicitly lists an `unscoreable normalized response` as a Stage-A **fatal stop**. Therefore project-brain adjudication is:

```text
MINIMAX_FATAL_FAIL=YES
MINIMAX_STAGE_A_STATUS=ELIMINATED
MINIMAX_FURTHER_STAGE_A_CALLS=FORBIDDEN
MINIMAX_STAGE_B_BUDGET=NONE
MINIMAX_SLOT_1=ATTEMPTED__NON_RETRYABLE
```

This does **not** mean the MiniMax API/model is unavailable. It means MiniMax-M3 failed this frozen Stage-A qualification contract and is eliminated under a pre-existing rule.

Authority:

- `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_002_MINIMAX_ADJUDICATION_V0_1.md`

## Current provider state

```text
KIMI_K3=CANDIDATE__NO_REAL_ATTEMPT_YET
KIMI_REMAINING_SLOTS=1,2,3,4,5
DEEPSEEK_V4_FLASH_VISION_EXP=CANDIDATE__ATTEMPT_001_UNSCOREABLE_DUE_V0_1_PROTOCOL_DEFECT
DEEPSEEK_REMAINING_SLOTS=2,3,4,5
MINIMAX_M3=ELIMINATED
MINIMAX_REMAINING_SLOTS=NONE
FINAL_APPROVED_PROVIDER_SET=NOT_DECIDED
```

No candidate is `VERIFIED` or `ADOPTED` yet. There is still no scoreable real-model Jianghe fidelity evidence.

## Current exact next action

The next explicit paid slot currently named by authority is:

```text
PROVIDER=KIMI
MODEL=kimi-k3
SLOT=1
TRACK=OPERATIONAL_PROVIDER
FROZEN_WORST_CASE_CNY=1.62756
```

Execution rule:

1. after fresh takeover Owner acceptance, refresh current main/runtime/current state and V0.2 remote ledger;
2. confirm no newer authority supersedes this next-slot choice;
3. Owner manually dispatches `.github/workflows/stage-a-live-slot.yml` on `main` for `KIMI`, slot `1`, **exactly once**;
4. regardless of green/red result, do not rerun;
5. project brain immediately reads durable start/terminal/safe evidence and adjudicates scoreability/fatal-stop state before any later paid call.

Do not automatically run Kimi Slot 2 or a DeepSeek future slot.

## Current budget / authorization

```text
OWNER_PAID_CALL_DECISION=AUTHORIZED
PAID_CALL_AUTHORIZATION_ID=OWNER-PAID-JIANGHE-FIDELITY-20260824-V01
PAID_CALL_AUTHORIZATION_EXPIRES=2026-08-31T00:00:00+08:00
TOTAL_API_SPEND_HARD_CAP_CNY=100.00
STAGE_A_TOTAL_CAP_CNY=18.00
STAGE_A_TOTAL_MAX_CALLS=15
MAX_CALLS_PER_PROVIDER=5
MAX_STAGE_A_SPEND_PER_PROVIDER_CNY=6.00
LIVE_CALLS=2
CURRENT_STAGE_A_ACCOUNTED_CNY=0.270021
DEEPSEEK_ACCOUNTED_CNY=0.219222
MINIMAX_ACCOUNTED_CNY=0.050799
KIMI_ACCOUNTED_CNY=0
NEW_RECHARGE_REQUIRED=NO
```

`PAID_SPEND_CNY` here is conservative Stage-A accounting, not proof of exact provider wallet billing. Owner previously reported current wallet balances of CNY10 each for Kimi, DeepSeek and MiniMax. Do not ask for recharge unless current authority/balance evidence later shows it is necessary.

## Current hard locks

The Stage-A paid-call authorization does **not** imply any of the following:

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

AI remains the Jianghe-style market-reading/trading-decision brain. Deterministic infrastructure owns hard risk, orders, execution truth, reconciliation and safety.

## Closed historical work that must not be reopened by default

```text
PRE_SPEND_REPAIR_REAUDIT=PASS
BSP-001..005=CLOSED
RSP-001..002=CLOSED
LIMIT-015=RESOLVED
```

Do not reopen a whole-repo rolling audit. Historical findings/closure remain preserved in their review artifacts and Git history.

## Worker / tool state

```text
TOOL_DECISION=USE_EXISTING
MAIN_INTEGRATION_LANE=ONE_ONLY
CODEX=USE_FOR_HIGH_VALUE_CROSS_MODULE_OR_RESEARCH_DESIGN_IMPLEMENTATION
WORKBUDDY=LOCAL_ONLY_NO_GITHUB_IN_CURRENT_SETUP
PARALLEL_WORKERS_DIFFERENT_WORKTREES=YES
```

During the outgoing conversation Codex/Sol was used for the heavy live-lane and V0.2 engineering. The next normal step does **not** require another worker package unless the next real attempt itself exposes a new correctness/research-design issue.

## Takeover warning about stale artifacts

The following artifacts are historical checkpoints and must not override current mutable state:

- `docs/reviews/JIANGHE_STAGE_A_PREEXECUTION_HANDOFF_2026-08-24.md` — pre-first-call history.
- `docs/reviews/JIANGHE_STAGE_A_V0_2_INTEGRATION_AND_REMOTE_BOOTSTRAP_CLOSURE_V0_1.md` — valid integration/bootstrap evidence, but its bootstrap remote head predates Attempt 002.
- old `PROJECT_HANDOFF_CURRENT.md` content before this rewrite — obsolete.

For live attempt count, current conservative accounting, provider elimination and next slot, use current `CURRENT_STATE.md`, current remote ledger and current attempt adjudications.

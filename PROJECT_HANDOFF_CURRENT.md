# PROJECT_HANDOFF_CURRENT

> Derived continuity pointer only. **handoff != authority**. Current `main`, `PROJECT_BRAIN_RUNTIME_BRIEF.md`, `CURRENT_STATE.md`, the V0.3 Owner decision/plan, and immutable historical attempt evidence always win.

## Fresh-conversation rule

Read `00_READ_FIRST.md` first, complete its read-only takeover order, and read this file **last**. Report understanding/contradictions and stop for Owner acceptance before executing new work.

## Handoff checkpoint — 2026-08-25 downloaded-Kline DeepSeek pilot complete

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
CURRENT_WORK_PACKAGE=JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_COMPLETE
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
CURRENT_STAGE_A_AUTHORITY=docs/reviews/JIANGHE_STAGE_A_V0_3_CAPABILITY_FIRST_OWNER_DECISION.md
CURRENT_COMPARISON_PLAN=docs/evidence/JIANGHE_STAGE_A_CAPABILITY_COMPARISON_PLAN_V0_3.json
CURRENT_FROZEN_PLAN=docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_3.json
V0_3_CLOSURE_AUTHORITY=docs/reviews/JIANGHE_STAGE_A_V0_3_OFFLINE_CLOSURE_V0_1.md
PILOT_ID=JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_V0_1
PILOT_VERDICT=REVIEW_BEFORE_EXPAND
PILOT_SAMPLE_COUNT=5
PILOT_NETWORK_CALLS=5
PILOT_AUTOMATIC_RETRIES=0
PILOT_SCOREABLE_COUNT=5
PILOT_TOTAL_FACTUAL_ERRORS=2
PILOT_TOTAL_INVENTED_RULES=0
PILOT_TOTAL_ACCOUNTED_CNY=0.672282
CURRENT_PROJECT_ACCOUNTED_CNY=3.1609662
PILOT_REMOTE_REF=refs/heads/downloaded-kline-pilot-state-v0-1
PILOT_REMOTE_HEAD=3aa33628a0c2d0d598aea8bba8babea093e75a50
V0_3_OFFLINE_CLOSURE=PASS
V0_3_NETWORK_PROVIDER_CALLS_TOTAL=4
PAID_CALLS_CURRENTLY_PAUSED=YES__DOWNLOADED_KLINE_PILOT_REVIEW
NEXT_EXPLICIT_PAID_SLOT=NONE__NO_FOURTH_PROVIDER
COMPLETED_PROVIDERS=DEEPSEEK__MINIMAX__KIMI
PENDING_PROVIDER=NONE
DEEPSEEK_NATIVE_VISION_MODEL_EXISTS=YES
V0_3_REMOTE_REF=refs/heads/stage-a-live-state-v0-3
TOOL_DECISION=USE_EXISTING
LIMIT_012=RESOLVED__THREE_PROVIDER_MATCHED_EVIDENCE_COMPLETE
```

The bounded five-case DeepSeek pilot is complete. All attempts are terminal,
scoreable and non-retried. DKL-DS-003 contains two confirmed data-fidelity errors:
the answer used the penultimate 5m bar as the final bar and then reported a false
15m/5m volume mismatch. The binding pilot authority is
`docs/reviews/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_V0_1.md`; the machine summary
is `docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_SUMMARY_V0_1.json`.

The three-provider result is complete. Quality ranking is
`DEEPSEEK > KIMI > MINIMAX`; DeepSeek is the current leading provider for the
downloaded-K-line evaluation. Selection confidence is
`PROVISIONAL__ONE_MATCHED_FIXTURE`, and no provider is permanently adopted.
Authority is
`docs/reviews/JIANGHE_STAGE_A_V0_3_THREE_PROVIDER_MATCHED_CAPABILITY_COMPARISON_V0_1.md`.

Kimi's matched result is `CAPABILITY_SCOREABLE`, adjudicated `PASS`, and carries
`PASS__WITH_MATERIAL_QUALITY_DEFECTS` quality status: `FAMILY=C`,
`ACTION=NO_TRADE`, `DIRECTION=NONE`. It cost CNY0.61002; project accounted total
is CNY2.4886842.
Evidence identity is `a20d602fcda2c47da34654b770a11d89239ab182a2ac2258736e74f138427fe7`
and remote head is `eef1f6a5a58757d2e071ba9413a133c4b24b6dbb`. It correctly rejected the
trade and invented no fixed rule, but misclassified the current family and made
two detailed structured-data claims that conflict with the governed observations.

MiniMax's matched result is `CAPABILITY_SCOREABLE` and adjudicated
`PASS__WITH_MATERIAL_QUALITY_DEFECTS`: `FAMILY=NONE`, `ACTION=WAIT`,
`DIRECTION=NONE`. It cost CNY0.1085952; project accounted total is CNY1.8786642.
Evidence identity is `0552d05848ae94b9c9a311432e88faed2dbefc4ad1ffc29ea0f8ae4f30d97b1a`
and remote head is `f0c619d0743c25cc62a755f24829280545778f77`.

MiniMax's safe decision matches DeepSeek's no-trade conclusion, but its answer
invented a fixed two-close rule and contained material 1H/body and post-poke
range/count errors. That was the two-provider checkpoint; Kimi is now complete and
the three-provider authority above supersedes it. The shared runner's
placeholder/live-payload START reservation defect was repaired and focused-tested.

DeepSeek's successful result is `CAPABILITY_SCOREABLE` and substantively adjudicated
`PASS`: `FAMILY=NONE`, `ACTION=NO_TRADE`, `DIRECTION=NONE`. Its attempt cost is
CNY0.110874 and project accounted total is CNY1.770069. Evidence identity is
`dd6c10adf138b6bad5babbca4ac675c749b4888680a91bcb108f29f01fbc600d`;
the remote ledger head is `d0ff1a727e276691bac2a63b8367cf73e5a8d438`.

The first real call (`...MATCHED_001`) is an immutable transport failure caused by
the repaired terminal-write defect and was conservatively charged CNY1.389174.
The successful independent call is `...MATCHED_002`. There were no automatic
retries. At that DeepSeek checkpoint MiniMax and Kimi had not run. See
`docs/reviews/JIANGHE_STAGE_A_V0_3_DEEPSEEK_CAPABILITY_MATCHED_002_ADJUDICATION_V0_1.md`.

## Binding Owner objective

```text
1=JIANGHE_CORRECTNESS_AND_CAPABILITY
2=ACTUAL_CNY_COST
3=ACTUAL_TIME_LATENCY
FAIRNESS=SAME_MATERIAL__SAME_QUESTION__DIFFERENT_MODEL_BRAIN
```

The model-selection target is the model that best understands and applies Jianghe to the same market evidence; cost and time are compared after capability. JSON obedience, low token use, or integration convenience are not substitutes for answer quality.

## What V0.3 corrected

V0.1/V0.2 over-coupled output-format mechanics with capability elimination. Current V0.3 semantics are:

```text
NON_SCOREABLE_NORMALIZER_IS_CAPABILITY_FATAL=NO
TRUNCATION_IS_CAPABILITY_FATAL=NO
LONG_REASONING_IS_CAPABILITY_FATAL=NO
PROVIDER_FORMAT_DIFFERENCE_IS_CAPABILITY_FATAL=NO
UNIFORM_1024_CAPABILITY_GATE=RETIRED
PRODUCTION_JSON_REQUIRED_FOR_CAPABILITY_SCORE=NO
```

Output/integration failures remain evidence, but only substantive Jianghe semantic failure may count as Jianghe capability failure.

## MiniMax Attempt 002 reinterpretation

Immutable historical facts remain: MiniMax-M3 old slot 1 reached 2xx, resolved correctly, used 7999 prompt tokens and 1024 completion tokens, reported 914 reasoning tokens, ended `finish_reason=length`, returned non-empty final content, and failed the strict normalizer. It cost CNY0.050799 conservatively and is never rerun.

```text
MINIMAX_V0_2_OPERATIONAL_FATAL_STOP=HISTORICAL_TRUE
MINIMAX_V0_3_JIANGHE_CAPABILITY_FAIL=NO_EVIDENCE
MINIMAX_V0_3_CAPABILITY_STATUS=CANDIDATE__FAIR_EVALUATION_REQUIRED
```

The old V0.2 `ELIMINATED` status cannot be used as current capability rejection.

## DeepSeek Attempt 001

DeepSeek old slot 1 remains a real, CNY0.219222 accounted, non-retryable V0.1 attempt. It reached 2xx provider JSON but V0.1 did not preserve sufficient safe response-envelope evidence. It never established a DeepSeek capability fatal fail.

V0.3 restarts the matched comparison **with DeepSeek first**, but only with a new V0.3 request/slot identity. Old `DEEPSEEK:1` is never rerun.

## Current capability candidates

```text
DEEPSEEK=CANDIDATE__V0_3_CAPABILITY_PASS
MINIMAX=CANDIDATE__V0_3_CAPABILITY_PASS_WITH_MATERIAL_QUALITY_DEFECTS
KIMI=CANDIDATE__V0_3_CAPABILITY_PASS_WITH_MATERIAL_QUALITY_DEFECTS
VERIFIED_PROVIDERS=DEEPSEEK__MINIMAX__KIMI
ADOPTED_PROVIDER=NONE__NO_PERMANENT_ADOPTION
STAGE_A_CURRENT_LEADING_PROVIDER=DEEPSEEK
```

The former `KIMI:1` next action is superseded and must not be executed.

## Engineering safety state

The historical `.github/workflows/stage-a-live-slot.yml` V0.2 paid lane has been retired. It now fails closed before credentials or provider transport. This prevents stale authority from accidentally spending on Kimi or rerunning any V0.2 slot.

V0.3 preserves the valuable infrastructure: Jianghe knowledge identities, same-material identities, visual/structured observation, outcome firewall, paid-call ledger, duplicate prevention, secret protection, request/evidence identities, cost accounting, provider adapters, and latency/usage evidence.

The V0.3 plan is executable and the DeepSeek matched capability pass is complete.
Its provider-specific completion headroom, safe raw-final-answer evidence,
identity-bound format-only normalized evaluation view, separated statuses, and
remote-ledger identities are now evidenced. No large unrelated engineering program
is authorized.

## Fair exam contract

Kimi / DeepSeek / MiniMax must receive the same Jianghe material, context-selection principle, question, K-line visual bytes, structured observation, visible history, outcome/future prohibition, no-tools/search rule, and trading-decision task. Provider-required wire syntax and provider-native recommended reasoning may differ.

Each provider gets enough provider-specific output headroom to normally finish reasoning plus final answer. Tokens, latency and actual CNY are recorded; they are comparison measurements, not automatic capability failures.

Capability answers may be valid JSON, markdown-wrapped JSON, provider-native structured output, or readable structured text if semantics are complete. Preserve secret-safe `MODEL_RAW_FINAL_ANSWER` and identity-bound `NORMALIZED_EVALUATION_VIEW`; never persist hidden chain-of-thought. The adapter may change format only, never repair or reinterpret semantics.

## Capability score focus

Score Jianghe principle accuracy, market structure, K-line visual reading, WAIT/NO_TRADE discipline, no invented rules/thresholds, UNKNOWN honesty, visual/structured consistency, hard negatives, stability, and whether the conclusion is actually supported by Jianghe material. Then compare actual CNY and actual time/latency.

## Budget / historical accounting

```text
HISTORICAL_V0_1_V0_2_LIVE_CALLS=2
V0_3_NETWORK_CALLS=4
CURRENT_PROJECT_ACCOUNTED_CNY=3.1609662
TOTAL_API_HARD_CAP_CNY=100.00
V0_1_V0_2_STAGE_A_CNY18_LIMIT=HISTORICAL_ONLY_FOR_V0_3
V0_1_V0_2_CNY6_PER_PROVIDER_LIMIT=HISTORICAL_ONLY_FOR_V0_3
V0_1_V0_2_FIVE_CALLS_PER_PROVIDER=HISTORICAL_ONLY_FOR_V0_3
AUTOMATIC_RECHARGE=FORBIDDEN
NEW_RECHARGE_REQUIRED=NO
```

The old per-stage/per-provider/five-call limits do not gate V0.3 capability comparison. CNY100 remains the total project API hard ceiling. Recharge remains a separate Owner cash action.

Historical V0.2 remote authority remains unchanged for old accounting:

```text
V0_2_PLAN_IDENTITY=9736e1cf75372ec13f524a971ee1d1c036a1d5e6ac51b250a6890a9ecf76d913
V0_2_REMOTE_REF=refs/heads/stage-a-live-state-v0-2
V0_2_REMOTE_HEAD_AFTER_ATTEMPT_002=ea1364e04e378781d8cf9f1b43a9ce3f0ef1679e
```

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

## Exact next work

1. Review DKL-DS-003's final-bar indexing and cross-timeframe volume-accounting defects.
2. Freeze the smallest corrective prompt/evaluation change; never rerun any pilot attempt.
3. Re-review the pilot before authorizing any larger downloaded-Kline batch.

Do not reopen the closed pre-spend whole-repository rolling audit.

Handoff last synchronized after the downloaded-Kline pilot authority, evidence,
budget and next-work pointers were finalized on 2026-08-25.

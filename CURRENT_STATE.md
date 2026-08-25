# CURRENT_STATE

> Mutable project-state authority. Current GitHub `main` is the only dynamic project fact source.

## Current phase

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
CURRENT_ADOPTED_ARCHITECTURE=Skeleton_v1.0_PLUS_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1
ARCHITECTURE_STATUS=ACCEPTED
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
RESEARCH_DIRECTION_STATUS=OWNER_APPROVED
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
CURRENT_WORK_PACKAGE=JIANGHE_DOWNLOADED_KLINE_PILOT_DEFECT_REVIEW_COMPLETE
NEXT_NORMAL_PHASE=DOWNLOADED_KLINE_INPUT_PROTOCOL_DECISION
OWNER_ACTION=DECIDE_V0_2_INPUT_SCOPE_THEN_AUTHORIZE_OR_DECLINE_FRESH_SMALL_PILOT
TOOL_DECISION=USE_EXISTING
```

## Downloaded-Kline DeepSeek pilot (2026-08-25)

```text
PILOT_ID=JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_V0_1
PILOT_STATUS=COMPLETE
PILOT_VERDICT=REVIEW_BEFORE_EXPAND
PILOT_SAMPLE_COUNT=5
NETWORK_CALLS=5
AUTOMATIC_RETRIES=0
SCOREABLE_COUNT=5
COMPLETE_OUTPUT_COUNT=5
TOTAL_FACTUAL_ERRORS=2
TOTAL_INVENTED_RULES=0
TOTAL_UNSUPPORTED_JIANGHE_CLAIMS=0
TOTAL_ACCOUNTED_CNY_THIS_PILOT=0.672282
PROJECT_ACCOUNTED_CNY_AFTER=3.1609662
REMOTE_LEDGER_HEAD=3aa33628a0c2d0d598aea8bba8babea093e75a50
PILOT_PLAN_IDENTITY=e4dd70c8938995ec57715abc28bcf1784d9a1e4d2c6bd7e61add83a224d8582a
SUMMARY_EVIDENCE_IDENTITY=78355db024882c21fdb172cce35a504b47b4c8a41d39f5748b64ae6efb673289
OUTCOME_ACCESS=NO
FUTURE_ACCESS=NO
```

Authority: `docs/reviews/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_V0_1.md` and
`docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_SUMMARY_V0_1.json`.
All five calls completed and were scoreable with no model mismatch, truncation,
automatic retry or invented Jianghe rule. DKL-DS-003 made two mechanically
confirmed data errors: it treated the penultimate 5m bar as the final bar and
then fabricated a volume mismatch. The historical pilot verdict remains immutable;
the V0.2 interface repair is ready for a new independent small pilot only, never a
rerun or larger batch.

## Downloaded-Kline DKL-DS-003 closure (2026-08-25)

```text
FORENSIC_VERDICT=MULTI_CAUSAL_DEFECTS_FIXED
FORENSIC_AUTHORITY=docs/reviews/JIANGHE_DOWNLOADED_KLINE_DKL_DS_003_FORENSIC_REVIEW_V0_1.md
TIMEFRAME_REVIEW_AUTHORITY=docs/reviews/JIANGHE_TIMEFRAME_INPUT_SCOPE_EVIDENCE_REVIEW_V0_1.md
NEW_INPUT_CONTRACT_VERSION=DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2
NEW_INPUT_CONTRACT_SCHEMA_IDENTITY=0057b11939c71f10fa7094db119f5b280e74edd13cb2bb7d40cc29a418c4c68a
HISTORICAL_PILOT_VERDICT_UNCHANGED=YES
PILOT_REVIEW_RESOLUTION=READY_FOR_FRESH_PILOT_V0_2
LARGE_BATCH_AUTHORIZED=NO
THIS_CLOSURE_NETWORK_CALLS=0
THIS_CLOSURE_PAID_PROVIDER_CALLS=0
PROJECT_ACCOUNTED_CNY_AFTER=3.1609662
JIANGHE_HIGHER_TIMEFRAME_EVIDENCE_STATUS=UNRESOLVED_IN_CURRENT_PRIMARY_EVIDENCE
```

Canonical data, session aggregation, structured artifact, renderer and evaluator
are correct. The model made factual errors while V0.1 also lacked explicit
order/latest-bar/exact-bucket semantics; V0.2 repairs only those generic input
semantics. Current source-backed evidence includes 4H usage, but PRIMARY freeze is
not requested, so no 4H/daily input is added in this closure.

## Stage-A V0.3 three-provider matched comparison (2026-08-25)

```text
THREE_PROVIDER_MATCHED_COMPARISON=COMPLETE
DEEPSEEK=COMPLETE__PASS
MINIMAX=COMPLETE__PASS_WITH_MATERIAL_QUALITY_DEFECTS
KIMI=COMPLETE__PASS_WITH_MATERIAL_QUALITY_DEFECTS
QUALITY_RANK_1=DEEPSEEK
QUALITY_RANK_2=KIMI
QUALITY_RANK_3=MINIMAX
STAGE_A_CURRENT_LEADING_PROVIDER=DEEPSEEK
STAGE_A_SELECTION_CONFIDENCE=PROVISIONAL__ONE_MATCHED_FIXTURE
ADOPTED_PROVIDER=NONE__NO_PERMANENT_ADOPTION
NEXT_VALIDATION=DOWNLOADED_KLINE_EVALUATION
```

Authority:
`docs/reviews/JIANGHE_STAGE_A_V0_3_THREE_PROVIDER_MATCHED_CAPABILITY_COMPARISON_V0_1.md`.
DeepSeek leads on the binding quality-first order. Kimi reached the safe conclusion
but misclassified the current family and made two detailed data errors. MiniMax was
cheapest and fastest but also invented a fixed two-close rule and made material
visual/data errors. This is one matched-fixture selection signal, not overall
accuracy, trading performance or permanent provider adoption.

## Stage-A V0.3 Kimi paid capability result (2026-08-25)

```text
RESULT_SCOPE=FIRST_MATCHED_FIXTURE_RESULT
KIMI_V0_3_CAPABILITY=PASS
KIMI_QUALITY_STATUS=PASS__WITH_MATERIAL_QUALITY_DEFECTS
KIMI_SLOT_ID=V0_3:KIMI:CAPABILITY_MATCHED_001
KIMI_TERMINAL_STATUS=CAPABILITY_SCOREABLE
KIMI_EVIDENCE_IDENTITY=a20d602fcda2c47da34654b770a11d89239ab182a2ac2258736e74f138427fe7
KIMI_NORMALIZED_VIEW_IDENTITY=edcf6bcc7fa8da4b83d8ca8d2f3bbb537ce16de6cf5433ecb2ab9aa42e311f66
KIMI_ATTEMPT_ACCOUNTED_CNY=0.61002
PROJECT_ACCOUNTED_CNY_AFTER=2.4886842
V0_3_REMOTE_HEAD=eef1f6a5a58757d2e071ba9413a133c4b24b6dbb
NETWORK_CALLS_MADE=1
AUTOMATIC_RETRIES=0
NEXT_RECOMMENDATION=DOWNLOADED_KLINE_EVALUATION_WITH_DEEPSEEK
```

Authority:
`docs/reviews/JIANGHE_STAGE_A_V0_3_KIMI_CAPABILITY_MATCHED_001_ADJUDICATION_V0_1.md`.
Kimi correctly rejected the trade and the unconfirmed 103 probe, preserved
directional uncertainty, and invented no fixed rule. Its pass carries material
defects: `FAMILY=C` despite no current setup, a non-monotonic high sequence called
progressively lower, and a last-ten-close range that omits a 101.0 close.

## Stage-A V0.3 MiniMax paid capability result (2026-08-25)

```text
RESULT_SCOPE=FIRST_MATCHED_FIXTURE_RESULT
MINIMAX_V0_3_CAPABILITY=PASS__WITH_MATERIAL_QUALITY_DEFECTS
MINIMAX_SLOT_ID=V0_3:MINIMAX:CAPABILITY_MATCHED_001
MINIMAX_TERMINAL_STATUS=CAPABILITY_SCOREABLE
MINIMAX_EVIDENCE_IDENTITY=0552d05848ae94b9c9a311432e88faed2dbefc4ad1ffc29ea0f8ae4f30d97b1a
MINIMAX_NORMALIZED_VIEW_IDENTITY=0ebe2ceccbe6b1242f94e349757400a9dd891ef7917005694250bfb09ffa5a47
MINIMAX_ATTEMPT_ACCOUNTED_CNY=0.1085952
PROJECT_ACCOUNTED_CNY_AFTER=1.8786642
V0_3_REMOTE_HEAD=f0c619d0743c25cc62a755f24829280545778f77
NETWORK_CALLS_MADE=1
AUTOMATIC_RETRIES=0
HISTORICAL_NEXT_RECOMMENDATION=RUN_KIMI_NEXT__NOW_COMPLETED
```

Authority:
`docs/reviews/JIANGHE_STAGE_A_V0_3_MINIMAX_CAPABILITY_MATCHED_001_ADJUDICATION_V0_1.md`.
MiniMax correctly produced `FAMILY=NONE`, `ACTION=WAIT`, `DIRECTION=NONE` and
rejected the unconfirmed 103 wick. Its pass carries material fidelity defects:
an invented fixed two-close rule, an incorrect 1H candle-body description, and an
incorrect post-poke 5m range/count. This was the two-provider checkpoint; Kimi is
now complete and the three-provider authority above supersedes its next pointer.

The shared runner was repaired after the call so the durable START reservation now
uses the same actual governed-prompt token bound and current rate card as the
transport reservation. This closes the CNY0.016884 placeholder/live-payload
reservation mismatch before any possible Kimi call.

## Stage-A V0.3 DeepSeek paid capability checkpoint (2026-08-25)

```text
DEEPSEEK_V0_3_CAPABILITY=PASS
SUCCESSFUL_SLOT_ID=V0_3:DEEPSEEK:CAPABILITY_MATCHED_002
SUCCESSFUL_TERMINAL_STATUS=CAPABILITY_SCOREABLE
SUCCESSFUL_EVIDENCE_IDENTITY=dd6c10adf138b6bad5babbca4ac675c749b4888680a91bcb108f29f01fbc600d
SUCCESSFUL_NORMALIZED_VIEW_IDENTITY=e17058ef8cc9557c232f9574ceba874f71324ae3a438a6ac7ddb9090432ea6df
SUCCESSFUL_ATTEMPT_ACCOUNTED_CNY=0.110874
PROJECT_ACCOUNTED_CNY_AFTER=1.770069
V0_3_REMOTE_HEAD=d0ff1a727e276691bac2a63b8367cf73e5a8d438
NETWORK_CALLS_MADE=2
AUTOMATIC_RETRIES=0
NEXT_RECOMMENDATION=RUN_MINIMAX_NEXT
```

Authority:
`docs/reviews/JIANGHE_STAGE_A_V0_3_DEEPSEEK_CAPABILITY_MATCHED_002_ADJUDICATION_V0_1.md`.
The successful model answer is `FAMILY=NONE`, `ACTION=NO_TRADE`,
`DIRECTION=NONE`: it recognized a narrow consolidation after failed sweeps, rejected
an unconfirmed breakout, preserved uncertainty, and did not force a trade. At this
historical checkpoint MiniMax and Kimi had not run; the MiniMax result above now
supersedes that execution-state pointer.

The first two workflow dispatches failed before provider transport and cost CNY0.
The first real V0.3 call (`...MATCHED_001`) lost terminal evidence after START due
to a runner defect; it is conservatively closed with its full CNY1.389174
reservation and never rerun. Focused repairs were verified before the independent
successful `...MATCHED_002` call. These were explicit attempts, not automatic
retries.

## Stage-A V0.3 capability-first offline closure (2026-08-25, historical checkpoint)

```text
V0_3_OFFLINE_CLOSURE=PASS__AWAITING_PROJECT_BRAIN_REVIEW
V0_3_CLOSURE_AUTHORITY=docs/reviews/JIANGHE_STAGE_A_V0_3_OFFLINE_CLOSURE_V0_1.md
PF-001=RETRACTED_BY_OWNER_FIRST_PARTY_EVIDENCE
PF-002=RETRACTED_BY_OWNER_FIRST_PARTY_EVIDENCE
DEEPSEEK_NATIVE_VISION_MODEL_EXISTS=YES
V0_3_PLAN_IDENTITY=2a7897926fcf94ef58bd26b002a0cd3dbcd408c26af5a21ac6eb8a611f0887c3
COMMON_EXAM_IDENTITY=7521af411b5df17d27ced17c27a2db34e776ba85a97070f7634e3a197bf3c4e8
DEEPSEEK_SLOT_ID=V0_3:DEEPSEEK:CAPABILITY_MATCHED_001
MINIMAX_SLOT_ID=V0_3:MINIMAX:CAPABILITY_MATCHED_001
KIMI_SLOT_ID=V0_3:KIMI:CAPABILITY_MATCHED_001
REMOTE_REF=refs/heads/stage-a-live-state-v0-3
HISTORICAL_PROJECT_ACCOUNTED_CNY=0.270021
PAID_PROVIDER_CALLS_AT_OFFLINE_CHECKPOINT=0
```
The V0.3 capability-first offline closure closed all confirmed PF-003..PF-015 and
NF-001..NF-004 findings. It created the shared headed capability-answer contract,
the three-tier COMMON_EXAM / PROVIDER_INFERENCE_CONFIG / ATTEMPT identities, the
format-only capability adapter, the CNY100 ledger carrying 0.270021 forward, the
V0.3 transport with a full terminal-status taxonomy, the deterministic frozen V0.3
plan, the crash-safe `stage-a-live-state-v0-3` lane, and the manual main-only V0.3
workflow. This paragraph records the pre-execution checkpoint; the later paid
result above supersedes its former execution gate.

Current Stage-A research-design authority:
`docs/reviews/JIANGHE_STAGE_A_V0_3_CAPABILITY_FIRST_OWNER_DECISION.md`.

Current preflight failure audit:
`docs/reviews/JIANGHE_STAGE_A_V0_3_PREFLIGHT_FAILURE_AUDIT_V0_1.md`.

Current non-executable comparison plan:
`docs/evidence/JIANGHE_STAGE_A_CAPABILITY_COMPARISON_PLAN_V0_3.json`.

## Owner selection objective

```text
SELECTION_PRIORITY_1=JIANGHE_CORRECTNESS_AND_CAPABILITY
SELECTION_PRIORITY_2=ACTUAL_CNY_COST
SELECTION_PRIORITY_3=ACTUAL_TIME_LATENCY
FAIRNESS_PRINCIPLE=SAME_MATERIAL__SAME_QUESTION__DIFFERENT_MODEL_BRAIN
```

Formatting convenience, strict JSON compliance, reasoning-token count, or a uniform completion ceiling are not Jianghe capability substitutes.

## Current paid-call state

```text
PAID_CALLS_CURRENTLY_PAUSED=YES__DOWNLOADED_KLINE_INPUT_PROTOCOL_DECISION
NEXT_EXPLICIT_PAID_SLOT=NONE__NO_FOURTH_PROVIDER
COMPLETED_PROVIDERS=DEEPSEEK__MINIMAX__KIMI
PENDING_PROVIDER=NONE
DEEPSEEK_CURRENT_FIRST_PARTY_NATIVE_VISUAL_ROUTE=VERIFIED__VISION_EXP_DIRECT_IMAGE_INPUT
DEEPSEEK_NATIVE_VISION_MODEL_EXISTS=YES
OLD_NEXT_KIMI_1=SUPERSEDED__NOT_EXECUTED
OLD_V0_2_LIVE_WORKFLOW=RETIRED__FAIL_CLOSED_BEFORE_CREDENTIALS
AUTOMATIC_RETRY=ZERO_USED
AUTOMATIC_NEXT_SLOT=FORBIDDEN
```

The V0.3 offline closure closed all preflight blockers and minted the executable
machinery. DeepSeek's matched capability result is now recorded above. Do not use
a VS Code/Copilot vision proxy and score that output as native DeepSeek K-line
visual reading; the V0.3 path sends the canonical PNG bytes directly via the
first-party image_url/base64 contract.

## Immutable historical live state

V0.1/V0.2 history remains evidence and accounting authority for calls already made:

```text
HISTORICAL_LIVE_CALLS=2
HISTORICAL_STAGE_A_ACCOUNTED_CNY=0.270021
HISTORICAL_DEEPSEEK_ACCOUNTED_CNY=0.219222
HISTORICAL_MINIMAX_ACCOUNTED_CNY=0.050799
HISTORICAL_KIMI_ACCOUNTED_CNY=0
V0_2_PLAN_IDENTITY=9736e1cf75372ec13f524a971ee1d1c036a1d5e6ac51b250a6890a9ecf76d913
V0_2_REMOTE_REF=refs/heads/stage-a-live-state-v0-2
V0_2_REMOTE_HEAD_AFTER_ATTEMPT_002=ea1364e04e378781d8cf9f1b43a9ce3f0ef1679e
```

### Attempt 001 — DeepSeek V0.1

Authority: `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_001_DEEPSEEK_ADJUDICATION_V0_1.md`.

```text
PROVIDER=DEEPSEEK
MODEL=deepseek-v4-flash-vision-exp
OLD_SLOT=1
ACCOUNTED_CNY=0.219222
EVIDENCE_IDENTITY=d36c1fbbb1cd639e48a6f049f7df1be3bb95d9f346d75bbb85e25451fba9dc55
OLD_SLOT_STATUS=ATTEMPTED__NON_RETRYABLE__NO_REPLACEMENT_CALL
V0_1_PROVIDER_RESPONSE_CONTRACT_DEFECT=YES
DEEPSEEK_CAPABILITY_FATAL_FROM_ATTEMPT_001=NO
```

The request reached a 2xx provider JSON response, but the V0.1 evidence contract did not retain enough safe response-envelope facts to score the final response. A future V0.3 DeepSeek call, if a valid current route is verified, uses a new identity; old `DEEPSEEK:1` is never rerun.

### Attempt 002 — MiniMax V0.2

Authority: `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_002_MINIMAX_ADJUDICATION_V0_1.md`.

```text
PROVIDER=MINIMAX
MODEL=MiniMax-M3
OLD_SLOT=1
HTTP_STATUS_CLASS=2xx
RESOLVED_MODEL=MiniMax-M3
FINISH_REASON=length
FINAL_CONTENT_STATE=TEXT_NONEMPTY
PROMPT_TOKENS=7999
COMPLETION_TOKENS=1024
REASONING_TOKEN_COUNT=914
LATENCY_MS=10364
ACCOUNTED_CNY=0.050799
TERMINAL_STATUS=NON_SCOREABLE_NORMALIZER
OLD_SLOT_STATUS=ATTEMPTED__NON_RETRYABLE
MINIMAX_V0_2_OPERATIONAL_FATAL_STOP=HISTORICAL_TRUE
MINIMAX_V0_3_JIANGHE_CAPABILITY_FAIL=NO_EVIDENCE
```

The V0.2 frozen funnel's elimination remains immutable historical experiment semantics. Under the Owner-approved V0.3 correction, truncation/normalizer failure does not establish Jianghe capability failure.

## Current capability candidates

```text
DEEPSEEK_CAPABILITY_STATUS=CANDIDATE__V0_3_CAPABILITY_PASS
MINIMAX_CAPABILITY_STATUS=CANDIDATE__V0_3_CAPABILITY_PASS_WITH_MATERIAL_QUALITY_DEFECTS
KIMI_CAPABILITY_STATUS=CANDIDATE__V0_3_CAPABILITY_PASS_WITH_MATERIAL_QUALITY_DEFECTS
VERIFIED_PROVIDERS=DEEPSEEK__MINIMAX__KIMI
ADOPTED_PROVIDER=NONE__NO_PERMANENT_ADOPTION
STAGE_A_CURRENT_LEADING_PROVIDER=DEEPSEEK
FAIR_MATCHED_THREE_MODEL_EVIDENCE=COMPLETE
```

Owner ordering was DeepSeek first. First-party evidence confirms
`deepseek-v4-flash-vision-exp` natively accepts image input (base64 `image_url`
data URL is documented method #1). The successful DeepSeek paid slot is
`V0_3:DEEPSEEK:CAPABILITY_MATCHED_002`; see the current result section above.

## V0.3 capability contract

```text
NON_SCOREABLE_NORMALIZER_IS_CAPABILITY_FATAL=NO
UNIFORM_1024_CAPABILITY_GATE=RETIRED
PRODUCTION_JSON_REQUIRED_FOR_CAPABILITY_SCORE=NO
PROVIDER_SPECIFIC_SUFFICIENT_COMPLETION_HEADROOM=REQUIRED
PROVIDER_NATIVE_RECOMMENDED_REASONING=ALLOWED
RAW_FINAL_ANSWER_EVIDENCE=REQUIRED__SECRET_SAFE__NO_CHAIN_OF_THOUGHT
NORMALIZED_EVALUATION_VIEW=REQUIRED__IDENTITY_BOUND
NORMALIZATION_ADAPTER=FORMAT_ONLY__NO_SEMANTIC_REPAIR
```

Matched comparison keeps the same Jianghe material, context-selection principle, question, visual bytes, structured observation, visible history, outcome/future ban, no-tools/search rule, and trading-decision task. Only provider-required wire syntax and provider-native reasoning configuration may differ. A second model used as a vision proxy is not provider-required wire syntax and is not allowed to masquerade as the tested model brain.

Capability scoring covers Jianghe principle accuracy, market structure, visual reading, WAIT/NO_TRADE discipline, no invented rules/thresholds, uncertainty honesty, visual/structured consistency, hard negatives, stability, and source-supported conclusions. Actual CNY and actual latency are compared after answer quality.

## Authorization and budget

```text
OWNER_PAID_CALL_DECISION=AUTHORIZED_FOR_BOUND_PROJECT_FIDELITY_RESEARCH__DEEPSEEK_EXECUTED
PAID_CALL_AUTHORIZATION_ID=OWNER-PAID-JIANGHE-FIDELITY-20260824-V01
PAID_CALL_AUTHORIZATION_EXPIRES=2026-08-31T00:00:00+08:00
TOTAL_API_SPEND_HARD_CAP_CNY=100.00
CURRENT_PROJECT_ACCOUNTED_CNY=3.1609662
MAX_REMAINING_UNDER_CONSERVATIVE_PROJECT_ACCOUNTING_CNY=96.8390338
V0_3_STAGE_A_CNY18_CAP=NOT_APPLICABLE__HISTORICAL_V0_1_V0_2_DESIGN_ONLY
V0_3_CNY6_PER_PROVIDER_CAP=NOT_APPLICABLE__HISTORICAL_V0_1_V0_2_DESIGN_ONLY
V0_3_FIXED_5_CALLS_PER_PROVIDER=NOT_APPLICABLE__HISTORICAL_V0_1_V0_2_DESIGN_ONLY
AUTOMATIC_RECHARGE=FORBIDDEN
NEW_RECHARGE_REQUIRED=NO
```

Cost/time/token use are measurements, not capability gates. CNY100 remains the project-wide API hard ceiling. V0.3 must carry historical CNY0.270021 into its project ledger rather than resetting project spend to zero. Any recharge is a separate Owner cash action.

## Pre-live research / knowledge state

```text
PRE_SPEND_REPAIR_REAUDIT=PASS
BSP_001_TO_005=CLOSED
RSP_001_TO_002=CLOSED
LIMIT_015=RESOLVED
LIMIT_012=RESOLVED__THREE_PROVIDER_MATCHED_EVIDENCE_COMPLETE
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
JIANGHE_PRIMARY_CLAIM_MANIFEST_IDENTITY=f767253dc4c2d1b17f57b9adfdc903907a97df8d4697dbe0fae0f603427dbf36
```

## Locks

```text
OUTCOME_ACCESS=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

## Exact next work

1. Review DKL-DS-003's final-bar indexing and cross-timeframe volume-accounting defects.
2. Decide the smallest prompt/evaluation repair; do not rerun any of the five immutable attempts.
3. Re-review the frozen pilot evidence before authorizing a larger downloaded-Kline batch.

Do not reopen a whole-repository rolling audit.

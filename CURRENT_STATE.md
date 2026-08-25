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
CURRENT_WORK_PACKAGE=JIANGHE_STAGE_A_V0_3_DEEPSEEK_CAPABILITY_PASS
NEXT_NORMAL_PHASE=owner_review_then_run_V0_3_MINIMAX_matched_capability_slot
OWNER_ACTION=REVIEW_DEEPSEEK_V0_3_PAID_RESULT
TOOL_DECISION=USE_EXISTING
```

## Stage-A V0.3 DeepSeek paid capability result (2026-08-25)

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
an unconfirmed breakout, preserved uncertainty, and did not force a trade. MiniMax
and Kimi have not run. No provider is finally adopted until the matched comparison
is complete.

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
PAID_CALLS_CURRENTLY_PAUSED=YES__DEEPSEEK_PASS_RECORDED__AWAITING_OWNER_NEXT_PROVIDER_DECISION
NEXT_EXPLICIT_PAID_SLOT=NONE_UNTIL_OWNER_DIRECTS_MINIMAX
COMPLETED_FIRST_V0_3_PROVIDER=DEEPSEEK
COMPLETED_SUCCESSFUL_V0_3_SLOT=V0_3:DEEPSEEK:CAPABILITY_MATCHED_002
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
MINIMAX_CAPABILITY_STATUS=CANDIDATE__FAIR_V0_3_EVALUATION_REQUIRED
KIMI_CAPABILITY_STATUS=CANDIDATE__FAIR_V0_3_EVALUATION_REQUIRED
VERIFIED_PROVIDER=DEEPSEEK
ADOPTED_PROVIDER=NONE
FAIR_MATCHED_THREE_MODEL_EVIDENCE=DEEPSEEK_COMPLETE__MINIMAX_KIMI_PENDING
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
CURRENT_PROJECT_ACCOUNTED_CNY=1.770069
MAX_REMAINING_UNDER_CONSERVATIVE_PROJECT_ACCOUNTING_CNY=98.229931
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
LIMIT_012=ACTIVE__DEEPSEEK_MATCHED_EVIDENCE_PASS__MINIMAX_AND_KIMI_NOT_YET_RUN
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

1. Owner reviews the DeepSeek V0.3 paid adjudication and preserved evidence.
2. If comparison continues, execute the matched MiniMax slot next on the same common exam; do not rerun either DeepSeek slot.
3. Stop after MiniMax for explicit review unless the Owner separately directs Kimi.
4. After matched candidates exist, compare Jianghe correctness first, then actual CNY and latency; only then adopt a provider.

Do not reopen a whole-repository rolling audit.

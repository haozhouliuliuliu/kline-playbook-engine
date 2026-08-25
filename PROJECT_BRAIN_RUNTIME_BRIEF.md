# PROJECT_BRAIN_RUNTIME_BRIEF

> Compact live pointer for the project brain. Current GitHub `main` remains the sole dynamic fact source.

## Mandatory runtime rule

Before every substantive project reply after takeover:
1. fetch current `main` HEAD;
2. fetch this file from current `main`;
3. do not use chat memory as mutable project authority;
4. for state/architecture/locks/next work/worker/model/provider/tool questions, refresh `CURRENT_STATE.md` and the named authority;
5. for historical attempt/accounting facts, refresh the relevant immutable attempt authority and ledger ref when needed;
6. fresh conversations read `00_READ_FIRST.md` first and `PROJECT_HANDOFF_CURRENT.md` last.

## Current live pointer

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE=Skeleton_v1.0_PLUS_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
CURRENT_WORK_PACKAGE=JIANGHE_DOWNLOADED_KLINE_PILOT_DEFECT_REVIEW_COMPLETE
NEXT_NORMAL_PHASE=DOWNLOADED_KLINE_INPUT_PROTOCOL_DECISION
OWNER_ACTION=DECIDE_V0_2_INPUT_SCOPE_THEN_AUTHORIZE_OR_DECLINE_FRESH_SMALL_PILOT
TOOL_DECISION=USE_EXISTING
LIMIT_012=RESOLVED__THREE_PROVIDER_MATCHED_EVIDENCE_COMPLETE
LIMIT_013=OPEN__OWNER_DECISION_REQUIRED
CURRENT_THREE_PROVIDER_COMPARISON=docs/reviews/JIANGHE_STAGE_A_V0_3_THREE_PROVIDER_MATCHED_CAPABILITY_COMPARISON_V0_1.md
CURRENT_DOWNLOADED_KLINE_PILOT=docs/reviews/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_V0_1.md
CURRENT_DOWNLOADED_KLINE_PILOT_SUMMARY=docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_SUMMARY_V0_1.json
CURRENT_FORENSIC_AUTHORITY=docs/reviews/JIANGHE_DOWNLOADED_KLINE_DKL_DS_003_FORENSIC_REVIEW_V0_1.md
CURRENT_TIMEFRAME_AUTHORITY=docs/reviews/JIANGHE_TIMEFRAME_INPUT_SCOPE_EVIDENCE_REVIEW_V0_1.md
```

## Current provider-selection state

```text
THREE_PROVIDER_MATCHED_COMPARISON=COMPLETE
QUALITY_RANK_1=DEEPSEEK
QUALITY_RANK_2=KIMI
QUALITY_RANK_3=MINIMAX
DEEPSEEK=CANDIDATE__V0_3_CAPABILITY_PASS
KIMI=CANDIDATE__V0_3_CAPABILITY_PASS_WITH_MATERIAL_QUALITY_DEFECTS
MINIMAX=CANDIDATE__V0_3_CAPABILITY_PASS_WITH_MATERIAL_QUALITY_DEFECTS
VERIFIED_PROVIDERS=DEEPSEEK__MINIMAX__KIMI
STAGE_A_CURRENT_LEADING_PROVIDER=DEEPSEEK
ADOPTED_PROVIDER=NONE__NO_PERMANENT_ADOPTION
```

Selection order remains Jianghe correctness/capability first, actual CNY second,
and actual latency third. The one matched synthetic fixture plus the first real
K-line pilot are selection signals, not proof of permanent provider superiority.

## Downloaded-Kline pilot and forensic closure

```text
PILOT_ID=JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_V0_1
PILOT_STATUS=COMPLETE
PILOT_VERDICT=REVIEW_BEFORE_EXPAND__HISTORICAL_IMMUTABLE
PILOT_SAMPLE_COUNT=5
NETWORK_CALLS=5
AUTOMATIC_RETRIES=0
SCOREABLE_COUNT=5
TOTAL_FACTUAL_ERRORS=2
TOTAL_INVENTED_RULES=0
TOTAL_UNSUPPORTED_JIANGHE_CLAIMS=0
TOTAL_ACCOUNTED_CNY_THIS_PILOT=0.672282
PROJECT_ACCOUNTED_CNY_AFTER=3.1609662
PILOT_REVIEW_RESOLUTION=READY_FOR_FRESH_PILOT_V0_2
LARGE_BATCH_AUTHORIZED=NO
FORENSIC_VERDICT=MULTI_CAUSAL_DEFECTS_FIXED
NEW_INPUT_CONTRACT_VERSION=DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2
NEW_INPUT_CONTRACT_SCHEMA_IDENTITY=0057b11939c71f10fa7094db119f5b280e74edd13cb2bb7d40cc29a418c4c68a
```

DKL-DS-003's canonical data, session aggregation, structured artifact, renderer and
evaluator were correct. DeepSeek made two factual errors while the V0.1 interface
also lacked explicit order/latest-closed-bar/exact-bucket semantics. The V0.2
contract fixes only those generic provider-neutral input semantics. Historical
attempts remain immutable and are never rerun.

## Timeframe evidence state

```text
CURRENT_TEST_TIMEFRAMES=1H__15M__5M
CURRENT_1H_15M_5M_IS_TEST_PROTOCOL=YES
CAN_WE_CONCLUDE_JIANGHE_ONLY_USES_1H_AND_BELOW=NO
JIANGHE_HIGHER_TIMEFRAME_EVIDENCE_STATUS=UNRESOLVED_IN_CURRENT_PRIMARY_EVIDENCE
SOURCE_BACKED_HIGHER_TIMEFRAME_SUPPORT=JH-CLM-039-001__JH-CLM-012-SP01__JH-CLM-012-SP02__JH-CLM-095-001__JH-CLM-095-003
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
```

Current source-backed material includes `4H+15m`, `1H+5m`, `15m+1m`, and
`4H→1H→5m` examples. This is enough to reject the statement that Jianghe only uses
1H and below, but not enough to freeze 4H/daily as mandatory input. Adding any
higher-timeframe paid input requires the Owner's next input-protocol research
decision.

## Paid-call state and budget

```text
PAID_CALLS_CURRENTLY_PAUSED=YES__DOWNLOADED_KLINE_INPUT_PROTOCOL_DECISION
NEXT_EXPLICIT_PAID_SLOT=NONE
CURRENT_PROJECT_ACCOUNTED_CNY=3.1609662
TOTAL_HARD_API_SPEND_CAP_CNY=100.00
MAX_REMAINING_UNDER_CONSERVATIVE_PROJECT_ACCOUNTING_CNY=96.8390338
AUTOMATIC_RETRY=FORBIDDEN
AUTOMATIC_NEXT_SLOT=FORBIDDEN
AUTOMATIC_RECHARGE=FORBIDDEN
NEW_RECHARGE_REQUIRED=NO
```

The prior Stage-A V0.1/V0.2/V0.3 paid attempts and the five downloaded-Kline V0.1
pilot attempts are immutable evidence. Do not infer a current executable slot from
historical plan files.

## Current locks

```text
OUTCOME_ACCESS=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

## GitHub connector 404 rule

```text
SINGLE_CONNECTOR_404_MEANS_DELETED=NO
RETRY_AUTHENTICATED_SPECIFIC_READ=REQUIRED
CORROBORATE_BEFORE_DECLARING_DELETION=REQUIRED
REFETCH_BLOB_SHA_BEFORE_WRITE_RETRY=REQUIRED
DISAGREEMENT=FAIL_CLOSED__REPORT_ACCESS_UNCERTAINTY
```

## Exact next work

1. Owner decides the V0.2 downloaded-Kline input scope.
2. That decision must explicitly consider whether the existing source-backed 4H evidence should enter a separately frozen higher-timeframe input protocol.
3. Until that decision: no paid provider call, no historical-attempt rerun, no large batch, and no outcome/validation/holdout/shadow/broker/real-money expansion.
4. If the Owner authorizes a fresh pilot, freeze a **new independent small V0.2 plan** using `DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2`; never reuse historical V0.1 attempt identities.

Do not reopen a rolling whole-repository audit.
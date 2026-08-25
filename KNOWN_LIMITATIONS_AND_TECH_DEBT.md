# KNOWN_LIMITATIONS_AND_TECH_DEBT

> Current unresolved limitations only. Resolved/historical findings remain in accepted evidence and Git history.

## LIMIT-001 — Historical price-limit operative metadata is incomplete

```text
STATUS=DEFERRED
CURRENT_BLOCKER=NO_FOR_CURRENT_NON_OUTCOME_CAPABILITY_WORK
ACTIVATE_BEFORE=confirmatory historical execution claims full price-limit non-fill realism
AUTHORITY=docs/research/HISTORICAL_PRICE_LIMIT_METADATA_AUTHORITY_PREP_V0_1.md
```

Do not infer historical operative limits from current rules or outcomes.

## LIMIT-003 — Continuous historical exchange fee / margin schedule is incomplete

```text
STATUS=DEFERRED
CURRENT_BLOCKER=NO_FOR_CURRENT_NON_OUTCOME_CAPABILITY_WORK
ACTIVATE_BEFORE=historical candidate evaluation claims realistic China-futures fees/margins
AUTHORITY=docs/research/E06_HISTORICAL_FEE_MARGIN_EVIDENCE_ASSESSMENT_V0_2.md
```

Current-rate backfill or inferred historical values remain forbidden without new authority.

## LIMIT-006 — Prospective Shadow statistical profile is not lockable yet

```text
STATUS=DEFERRED_RESEARCH_POLICY
CURRENT_BLOCKER=NO_FOR_CURRENT_NON_OUTCOME_CAPABILITY_PRIMARY_PREP
ACTIVATE_BEFORE=prospective Shadow/Forward candidate evidence
AUTHORITY=docs/research/HUMAN_PLAYBOOK_STATISTICAL_ACCEPTANCE_ROUTE_POLICY_V1_0.md
```

## LIMIT-007 — Portfolio candidate-outcome authority is not implemented

```text
STATUS=DEFERRED_ARCHITECTURE
CURRENT_BLOCKER=NO
ACTIVATE_BEFORE=multi-strategy portfolio candidate-performance evaluation
PORTFOLIO_CANDIDATE_OUTCOME_AUTHORITY=NOT_IMPLEMENTED
```

## LIMIT-008 — SOURCE_ONLY / local state do not prove hostile-process tamper resistance

```text
STATUS=DEFERRED_THREAT_MODEL_LIMIT
CURRENT_BLOCKER=NO
SOURCE_ONLY_OS_PROCESS_SANDBOX=NOT_PROVEN_NOT_CLAIMED
LOCAL_PRIVATE_STATE_TAMPER_PROOFING=NOT_PROVEN_NOT_CLAIMED
```

## LIMIT-012 — Fair real-model Jianghe capability comparison

```text
STATUS=RESOLVED__THREE_PROVIDER_MATCHED_EVIDENCE_COMPLETE
PRIORITY=HISTORICAL
CURRENT_BLOCKER=NO
CURRENT_RESEARCH_VERSION=STAGE_A_V0_3_CAPABILITY_FIRST_MODEL_COMPARISON
CURRENT_AUTHORITY=docs/reviews/JIANGHE_STAGE_A_V0_3_CAPABILITY_FIRST_OWNER_DECISION.md
CURRENT_PLAN=docs/evidence/JIANGHE_STAGE_A_CAPABILITY_COMPARISON_PLAN_V0_3.json
CURRENT_FROZEN_PLAN=docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_3.json
V0_3_OFFLINE_CLOSURE=COMPLETE
V0_3_CLOSURE_AUTHORITY=docs/reviews/JIANGHE_STAGE_A_V0_3_OFFLINE_CLOSURE_V0_1.md
PAID_CALLS_CURRENTLY_PAUSED=YES__FINAL_CHANCE_V0_2_PLAN_NOT_MATERIALIZED
FAIR_MATCHED_THREE_MODEL_EVIDENCE=COMPLETE
DEEPSEEK_STATUS=CURRENT_LEADING_PROVIDER__NO_PERMANENT_ADOPTION
MINIMAX_STATUS=CANDIDATE__FINAL_MATCHED_OPPORTUNITY_APPROVED
KIMI_STATUS=CANDIDATE__FINAL_MATCHED_OPPORTUNITY_APPROVED
NEXT_EXPLICIT_PAID_SLOT=NONE
```

The historical V0.3 three-provider matched comparison is complete. Its binding quality order is DeepSeek > Kimi > MiniMax, with no permanent provider adoption. Historical attempts remain immutable.

The Owner corrected the old V0.1/V0.2 research-design error in which output-format / normalizer compatibility and a uniform 1024-token completion ceiling had become too entangled with model-capability elimination.

Current anti-regression rule:

```text
NON_SCOREABLE_NORMALIZER != JIANGHE_CAPABILITY_FAIL
TRUNCATION != JIANGHE_CAPABILITY_FAIL
LONG_REASONING != JIANGHE_CAPABILITY_FAIL
PROVIDER_FORMAT_DIFFERENCE != JIANGHE_CAPABILITY_FAIL
```

Historical Attempt 001 remains immutable: DeepSeek old slot 1 was actually attempted and accounted CNY0.219222, is non-retryable, and did not establish a DeepSeek capability fatal fail.

Historical Attempt 002 remains immutable: MiniMax old slot 1 returned 2xx, resolved MiniMax-M3, consumed 1024 completion tokens including 914 reported reasoning tokens, ended `finish_reason=length`, and produced non-empty but non-normalizable final content. The old V0.2 operational elimination remains historical truth, but it is not current evidence that MiniMax failed Jianghe capability.

```text
MINIMAX_V0_2_OPERATIONAL_FATAL_STOP=HISTORICAL_TRUE
MINIMAX_V0_3_JIANGHE_CAPABILITY_FAIL=NO_EVIDENCE
```

## LIMIT-013 — Downloaded-Kline V0.2 input protocol / timeframe scope

```text
STATUS=RESOLVED__OWNER_APPROVED_V0_2_PROTOCOL
CURRENT_BLOCKER=NO
AUTHORITY=docs/reviews/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_OWNER_DECISION_V0_2.md
TIMEFRAME_AUTHORITY=docs/reviews/JIANGHE_HIGHER_TIMEFRAME_BOUNDED_EVIDENCE_REVIEW_V0_2.md
INPUT_CONTRACT=DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2
INPUT_CONTRACT_SCHEMA_IDENTITY=0057b11939c71f10fa7094db119f5b280e74edd13cb2bb7d40cc29a418c4c68a
TEST_STACK=4H/1H/15m/5m
FOUR_HOUR_REPRESENTATION=SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1
```

The Owner approved 4H as a source-backed context layer for the next bounded test. It is not a permanent Jianghe timeframe doctrine. Daily / weekly / monthly are not included in this round because the bounded current evidence did not establish a sufficiently explicit role.

The generic V0.2 contract remains unchanged. 4H is carried separately and is forbidden from participating in exact cross-timeframe volume reconciliation.

## LIMIT-014 — Fresh final-chance plan is not materialized

```text
STATUS=RESOLVED__FOUR_FRESH_CASES_MATERIALIZED_AND_VERIFIED
CURRENT_BLOCKER=NO_FOR_MATERIALIZATION_GATE__PRE_SEND_GATE_STILL_PENDING
PLAN_SPEC=docs/evidence/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_SPEC_V0_2.json
MATERIALIZED_PLAN=docs/evidence/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_V0_2.json
MATERIALIZATION_STATUS=MATERIALIZED__AWAITING_PRESEND_REVIEW
NEXT_EXPLICIT_PAID_SLOT=NONE
```

The V0.2 four-case plan is materialized and verified from the accepted local canonical corpus. Four fresh deterministic case identities and twelve matched non-executable slots exist and are committed.

This resolution closes only the materialization gate. Pricing / budget / authorization / pre-send review is still not complete, and no paid call may occur before that review creates an explicit slot.

Historical V0.1 cases or attempts may not be reused to bypass this limitation.

## LIMIT-016 — Permanent Jianghe timeframe doctrine remains unknown

```text
STATUS=DEFERRED_SEMANTIC_SCOPE
CURRENT_BLOCKER=NO_FOR_CURRENT_V0_2_TEST
ACTIVATE_BEFORE=claiming a permanent mandatory Jianghe timeframe stack
```

The V0.2 experimental `4H / 1H / 15m / 5m` stack must not be promoted into permanent strategy doctrine without separate semantic authority.

## Current PRIMARY prerequisite

```text
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=INTEGRATED_PRE_FREEZE_IDENTITY_BOUND__FIXED_RUBRIC_REAUDIT_PASS
JIANGHE_PRIMARY_BRANCH_REGISTRY_V0_5=INTEGRATED_PRE_FREEZE_NON_FINAL_FIXED_RUBRIC_REAUDIT_PASS
JIANGHE_PRIMARY_REGISTRY_DECLARED_READY_COUNT=340
JIANGHE_PRIMARY_REGISTRY_STOP_COUNT=12
JIANGHE_PRIMARY_PROJECT_BRAIN_ACCEPTED_READY_COUNT=340
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
NEXT_GATE=OWNER_FREEZE_DECISION_AFTER_FAIR_REAL_MODEL_CAPABILITY_EVIDENCE
```

## Maintenance rule

Keep only unresolved items that can still affect a future decision. Do not reopen the closed pre-spend whole-repository audit; BSP-001..005, RSP-001..002 and historical LIMIT-015 remain closed/resolved in historical authority.

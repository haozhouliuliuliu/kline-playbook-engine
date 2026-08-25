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
PAID_CALLS_CURRENTLY_PAUSED=YES__DOWNLOADED_KLINE_INPUT_PROTOCOL_DECISION
FAIR_MATCHED_THREE_MODEL_EVIDENCE=COMPLETE
DEEPSEEK_STATUS=CURRENT_LEADING_PROVIDER__NO_PERMANENT_ADOPTION
MINIMAX_STATUS=CANDIDATE__PASS_WITH_MATERIAL_QUALITY_DEFECTS
KIMI_STATUS=CANDIDATE__PASS_WITH_MATERIAL_QUALITY_DEFECTS
NEXT_EXPLICIT_PAID_SLOT=NONE
```

The V0.3 three-provider matched comparison is complete. Its binding quality order
is DeepSeek > Kimi > MiniMax, with no permanent provider adoption. LIMIT-012 is
therefore resolved; the current blocker is instead the separate downloaded-Kline
pilot review recorded in current state.

The Owner corrected a research-design error in V0.1/V0.2: output-format/normalizer compatibility and a uniform 1024-token completion ceiling had become too entangled with model-capability elimination.

## LIMIT-013 — Downloaded-Kline V0.2 input protocol still needs an Owner scope decision

```text
STATUS=OPEN__OWNER_DECISION_REQUIRED
CURRENT_BLOCKER=NO_FOR_OFFLINE_FORENSIC_CLOSURE
ACTIVATE_BEFORE=ANY_FRESH_DOWNLOADED_KLINE_V0_2_PAID_PILOT
AUTHORITY=docs/reviews/JIANGHE_DOWNLOADED_KLINE_DKL_DS_003_FORENSIC_REVIEW_V0_1.md
TIMEFRAME_AUTHORITY=docs/reviews/JIANGHE_TIMEFRAME_INPUT_SCOPE_EVIDENCE_REVIEW_V0_1.md
```

The generic V0.2 contract explicitly marks bar order/latest closed bars and exact
cross-timeframe volume buckets. It has no paid validation yet. Source-backed Jianghe
material contains 4H examples, while the PRIMARY semantic freeze remains unrequested;
the Owner must decide the next input scope before a fresh small pilot. No rerun and no
large batch are authorized.

Current anti-regression rule:

```text
NON_SCOREABLE_NORMALIZER != JIANGHE_CAPABILITY_FAIL
TRUNCATION != JIANGHE_CAPABILITY_FAIL
LONG_REASONING != JIANGHE_CAPABILITY_FAIL
PROVIDER_FORMAT_DIFFERENCE != JIANGHE_CAPABILITY_FAIL
```

Historical Attempt 001 remains immutable: DeepSeek old slot 1 was actually attempted and accounted CNY0.219222, is non-retryable, and did not establish a DeepSeek capability fatal fail.

Historical Attempt 002 remains immutable: MiniMax old slot 1 returned 2xx, resolved MiniMax-M3, consumed 1024 completion tokens including 914 reported reasoning tokens, ended `finish_reason=length`, and produced non-empty but non-normalizable final content. The old V0.2 funnel's operational elimination remains historical V0.2 truth, but it is **not current evidence that MiniMax failed Jianghe capability**.

```text
MINIMAX_V0_2_OPERATIONAL_FATAL_STOP=HISTORICAL_TRUE
MINIMAX_V0_3_JIANGHE_CAPABILITY_FAIL=NO_EVIDENCE
```

The previous `KIMI:1` next slot is superseded and must not be executed. The V0.2 live workflow is retired fail-closed before credentials/provider transport.

V0.3 must compare the three models on the same Jianghe material/question/visual/structured observation/visible history and outcome/tool restrictions, while allowing provider-required wire syntax and provider-native recommended reasoning. Each provider receives sufficient completion headroom for a complete final answer. Production JSON is not required for capability scoring; safe raw final answer and an identity-bound, format-only normalized evaluation view are required, with no persisted hidden reasoning text.

Final selection order is Jianghe correctness/capability, then actual CNY cost, then actual time/latency. Token usage and integration convenience remain diagnostics rather than automatic capability gates.

Historical V0.1/V0.2 CNY18 Stage-A, CNY6/provider and fixed-five-calls/provider limits are not V0.3 capability gates. The project-wide CNY100 API hard cap remains binding, unused budget remains unspent, and recharge is never automatic.

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

Keep only unresolved items that can still affect a future decision. Do not reopen the closed pre-spend whole-repository audit; BSP-001..005, RSP-001..002 and LIMIT-015 remain closed/resolved in historical authority.

# KNOWN_LIMITATIONS_AND_TECH_DEBT

> Current unresolved limitations only.
> Resolved items, abandoned source lines, old repair programs and historical negative screens are intentionally removed from this active index; their evidence remains in Git history and durable review/evidence artifacts.

## LIMIT-001 — Historical price-limit operative metadata is incomplete

```text
STATUS=DEFERRED
CURRENT_BLOCKER=NO_FOR_CURRENT_NON_OUTCOME_FIDELITY_WORK
ACTIVATE_BEFORE=confirmatory historical execution claims full price-limit non-fill realism
AUTHORITY=docs/research/HISTORICAL_PRICE_LIMIT_METADATA_AUTHORITY_PREP_V0_1.md
```

The base-rule authority exists, but full day-by-day operative 2024–2025 price-limit facts and special-day rules are not fully governed. Do not infer historical limits from current rules or fill gaps from outcomes.

## LIMIT-003 — Continuous 2024–2025 exchange fee / margin schedule is incomplete

```text
STATUS=DEFERRED
CURRENT_BLOCKER=NO_FOR_CURRENT_NON_OUTCOME_FIDELITY_WORK
ACTIVATE_BEFORE=historical candidate evaluation claims realistic China-futures fees/margins
AUTHORITY=docs/research/E06_HISTORICAL_FEE_MARGIN_EVIDENCE_ASSESSMENT_V0_2.md
E06_FINAL_JUDGMENT=PARTIALLY_BUILDABLE_WITH_GAPS
```

Current-rate backfill, third-party substitution and inferred historical values remain forbidden without new authority.

## LIMIT-006 — Prospective Shadow statistical profile is not lockable yet

```text
STATUS=DEFERRED_RESEARCH_POLICY
CURRENT_BLOCKER=NO_FOR_CURRENT_NON_OUTCOME_FIDELITY_PRIMARY_PREP
ACTIVATE_BEFORE=prospective Shadow/Forward candidate evidence
AUTHORITY=docs/research/HUMAN_PLAYBOOK_STATISTICAL_ACCEPTANCE_ROUTE_POLICY_V1_0.md
PROSPECTIVE_SHADOW_STATISTICAL_PROFILE=NOT_LOCKABLE_UNDER_CURRENT_ASSUMPTION_AUTHORITY
PROSPECTIVE_PROCESS_ASSUMPTION_DESIGN=NO_GOVERNABLE_A_B_ASSUMPTION_FOUND
```

This is a research-design limitation, not an execution-engineering defect. Do not manufacture a real-looking statistical profile from test-only machinery.

## LIMIT-007 — Portfolio candidate-outcome authority is not implemented

```text
STATUS=DEFERRED_ARCHITECTURE
CURRENT_BLOCKER=NO
ACTIVATE_BEFORE=multi-strategy portfolio candidate-performance evaluation
PORTFOLIO_CANDIDATE_OUTCOME_AUTHORITY=NOT_IMPLEMENTED
```

Do not remove this fail-closed boundary as an incidental implementation change.

## LIMIT-008 — SOURCE_ONLY / local state do not prove hostile-process tamper resistance

```text
STATUS=DEFERRED_THREAT_MODEL_LIMIT
CURRENT_BLOCKER=NO
SOURCE_ONLY_OS_PROCESS_SANDBOX=NOT_PROVEN_NOT_CLAIMED
LOCAL_PRIVATE_STATE_TAMPER_PROOFING=NOT_PROVEN_NOT_CLAIMED
```

Project API/session denial and material binding were verified for the currently bound bundle, but this does not prove OS sandboxing, resistance to malicious local introspection, cryptographic tamper protection, or absence of latent model knowledge.

## LIMIT-012 — Real-model Jianghe fidelity qualification is in progress and no model is yet qualified

```text
STATUS=ACTIVE
PRIORITY=HIGHEST_CURRENT_MODEL_SELECTION_BLOCKER
CURRENT_BLOCKER=YES_FOR_MODEL_ADOPTION_AND_PRIMARY_PROMOTION
REAL_MODEL_FIDELITY_EVALUATION=STARTED__STAGE_A_V0_2_ACTIVE
STAGE_A_PLAN_IDENTITY=9736e1cf75372ec13f524a971ee1d1c036a1d5e6ac51b250a6890a9ecf76d913
LIVE_CALLS=2
STAGE_A_ACCOUNTED_CNY=0.270021
SCOREABLE_MODEL_EVIDENCE=NONE_YET
KIMI_STATUS=CANDIDATE__NO_REAL_ATTEMPT_YET
DEEPSEEK_STATUS=CANDIDATE__ATTEMPT_001_UNSCOREABLE_DUE_V0_1_PROTOCOL_DEFECT__SLOT_1_NON_RETRYABLE
MINIMAX_STATUS=ELIMINATED__ATTEMPT_002_FATAL_STOP__NO_FURTHER_STAGE_A_CALLS
NEXT_EXPLICIT_SLOT=KIMI:1
AUTOMATIC_RETRY=FORBIDDEN
AUTOMATIC_NEXT_SLOT=FORBIDDEN
```

Current authorities:

- `docs/reviews/JIANGHE_RMB100_REAL_MODEL_FIDELITY_FUNNEL_V0_1.md`
- `docs/reviews/JIANGHE_STAGE_A_V0_2_PROVIDER_RESPONSE_COMPATIBILITY_OWNER_DECISION.md`
- `docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_2.json`
- `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_001_DEEPSEEK_ADJUDICATION_V0_1.md`
- `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_002_MINIMAX_ADJUDICATION_V0_1.md`

Attempt 001 reached the DeepSeek provider but V0.1 did not preserve enough safe 2xx response-envelope evidence to score the final response. The slot is immutable/non-retryable, but that attempt was not adjudicated as a DeepSeek provider fatal fail because the project-side V0.1 provider-response contract was defective. The Owner approved V0.2 to correct future response-contract handling without erasing Attempt 001.

Attempt 002 reached MiniMax-M3 successfully at the API level (`2xx`, exact resolved model and usage preserved) but terminated at the 1024-token completion ceiling with an unscoreable normalized response. The pre-existing funnel explicitly lists an unscoreable normalized response as a Stage-A fatal stop, so MiniMax is eliminated from this funnel and receives no further Stage-A/Stage-B budget.

The next bounded work is not another infrastructure project: execute exactly one unattempted `KIMI:1` operational-provider smoke under the current authorization, then read durable evidence and adjudicate before any later call.

Provider/model choice remains based on Jianghe fidelity, stability, UNKNOWN honesty, no-invention behavior and operational validity — never candidate returns/PnL.

`LIMIT-015` is resolved and intentionally absent from this unresolved-only index. Its frozen findings and accepted repair closure remain preserved in:

- `docs/reviews/JIANGHE_PRE_SPEND_DOUBLE_AUDIT_CONSOLIDATED_FINDINGS_V0_1.md`
- `docs/reviews/JIANGHE_PRE_SPEND_BATCHED_REPAIR_CLOSURE_V0_1.md`

## Current PRIMARY prerequisite

```text
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=INTEGRATED_PRE_FREEZE_IDENTITY_BOUND__FIXED_RUBRIC_REAUDIT_PASS
JIANGHE_PRIMARY_BRANCH_REGISTRY_V0_5=INTEGRATED_PRE_FREEZE_NON_FINAL_FIXED_RUBRIC_REAUDIT_PASS
JIANGHE_PRIMARY_REGISTRY_DECLARED_READY_COUNT=340
JIANGHE_PRIMARY_REGISTRY_STOP_COUNT=12
JIANGHE_PRIMARY_PROJECT_BRAIN_ACCEPTED_READY_COUNT=340
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
NEXT_GATE=OWNER_FREEZE_DECISION_AFTER_REAL_MODEL_FIDELITY_EVIDENCE
```

The V0.5 registry passed its independent fixed-rubric re-audit and the original pre-live gate passed. Those resolved results remain in durable review evidence and Git history rather than this active unresolved index.

## Maintenance rule

Keep only unresolved items that can still affect a future decision. Once an item is resolved or leaves the current route, remove it from this active index and preserve the accepted resolution in its evidence/review + Git history. Do not retain `RESOLVED` sections here as context ballast.

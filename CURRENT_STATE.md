# CURRENT_STATE

> Mutable project-state authority. Keep this file current and compact.
> Historical stages, rejected/deferred playbooks, old integration logs, and superseded progress estimates belong in Git history or their durable evidence/review artifacts, not here.

## Current phase

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
CURRENT_ADOPTED_ARCHITECTURE=Skeleton_v1.0_PLUS_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1
ARCHITECTURE_STATUS=ACCEPTED
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
RESEARCH_DIRECTION_STATUS=OWNER_APPROVED
STRATEGY_SOURCE_EXPANSION=PAUSED_FOR_V1
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
CURRENT_WORK_PACKAGE=NONE_ACTIVE
NEXT_NORMAL_PHASE=CLAIM_LEVEL_PRIMARY_MAPPING_PLUS_REAL_MODEL_FIDELITY_CANDIDATE_EVALUATION_WITHOUT_CANDIDATE_OUTCOMES
OWNER_ACTION=NONE_FOR_ORDINARY_PRE_OUTCOME_ENGINEERING
TOOL_DECISION=USE_EXISTING
```

## Current product / strategy boundary

The current product is a constrained **Jianghe AI Trader**:

```text
causal market observation
-> Jianghe AI discretionary interpretation
-> constrained TradeIntent
-> deterministic RiskGate
-> OMS / STOP-OCO / execution
-> broker facts / reconciliation
-> Safety
-> Ledger
```

Current binding behavior:

```text
AI_TRADING_BRAIN=JIANGHE_KNOWLEDGE_CONSTRAINED
AI_ALLOWED_FAMILIES=A,B,C,D,NONE
UNKNOWN_OR_CONTRADICTION=NO_TRADE_OR_WAIT
UNFAMILIAR_MARKET=NO_TRADE
DETERMINISTIC_RISK_EXECUTION_SAFETY=AUTHORITATIVE
AI_MAY_NOT_CHANGE_HARD_RISK_LIMITS=YES
```

Authority: `docs/architecture/ADR_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1.md`.

## Jianghe knowledge / research status

```text
JIANGHE_SOURCE_DISTILLATION=V1_1_EXHAUSTIVE_SECOND_PASS_COMPLETE
JIANGHE_SOURCE_ONLY_VERIFIED=YES
JIANGHE_PRIMARY_ELIGIBLE=NO
KNOWLEDGE_PACK_VERSION=JIANGHE_V1_1
KNOWLEDGE_PACK_IDENTITY=3f2ddbf9c007b3246661088986a35b84258bdc984ed5fa82dace59074495a9d5
JIANGHE_PRIMARY_PREPARATION_SCHEMA_V0_1=INTEGRATED_PRE_FREEZE_NON_OUTCOME
JIANGHE_PRIMARY_CLAIM_MANIFEST_IDENTITY=60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940
JIANGHE_PRIMARY_CLAIM_MANIFEST_RECORDS=352
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=NOT_COMPLETE
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
JIANGHE_PRIMARY_NEXT_GATE=COMPLETE_352_CLAIM_LEVEL_SOURCE_JUSTIFIED_PRIMARY_MAPPING_PLUS_REAL_MODEL_FIDELITY_EVIDENCE_WITHOUT_OUTCOMES
JIANGHE_PRIMARY_SEMANTICS=SOURCE_JUSTIFIED_AI_INTERPRETATION_BRANCH_NOT_FIXED_RULE_MACHINE
```

For the Jianghe AI Trader, PRIMARY does **not** mean converting Jianghe into a rigid threshold strategy. It means freezing the source-justified interpretation branch plus the complete versioned AI Trader identity and deterministic hard-risk/execution envelope before any outcome-bearing test. The integrated preparation contract uses one versioned PRIMARY branch object per claim so cross-cutting risk, management, multi-timeframe, no-trade, process and UNKNOWN semantics are not collapsed into four family summaries. Final semantic freeze remains Owner-gated.

Current Jianghe source authority starts at:
`docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md`.

PRIMARY preparation authorities:
- `docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_V0_1.md`
- `docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_SCHEMA_V0_1.json`

SOURCE_ONLY verification authority:
`docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.md` + `.json`.

## Jianghe AI engineering status

```text
JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1=INTEGRATED_NON_OUTCOME
JIANGHE_AI_OBSERVATION_REPLAY_V0_2=INTEGRATED_SYNTHETIC_NON_OUTCOME
JIANGHE_AI_REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
JIANGHE_AI_REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
JIANGHE_AI_REAL_MODEL_FIDELITY_REQUIRED_TRACKS=SEMANTIC,VISUAL,STRUCTURED,DUAL_INPUT,OPERATIONAL_PROVIDER
JIANGHE_AI_REPLAY_HISTORICAL_BASELINE=COMPLETED_1_MINUTE_BAR
JIANGHE_AI_SUB_MINUTE_LIVE_CAPABILITY=NOT_VALIDATED_NOT_EQUIVALENT_TO_1M_REPLAY
```

Integrated components include causal multi-timeframe observations, rolling market state,
standardized chart rendering, AI-hypothesis annotations, wake events, persistent working memory,
forward-only replay, model-latency accounting, fidelity fixtures, and semantic scoring.

Real-model evaluation must not select a trading brain from text-only reasoning. It must separately test Jianghe semantic fidelity, standardized-chart visual observation, matching structured OHLCV interpretation, visual/structured consistency, and governable provider/model callability/latency — all without candidate outcomes.

Authorities:
- `docs/research/JIANGHE_AI_TRADER_RESEARCH_PROTOCOL_V0_1.md`
- `docs/research/jianghe/JIANGHE_AI_FIDELITY_BENCHMARK_V0_1.md`
- `docs/evidence/JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1.md`
- `docs/reviews/JIANGHE_AI_FIDELITY_AND_REPLAY_INTEGRATION_REVIEW_V0_1.md`

## Data authority relevant to the next phase

```text
CANONICAL_PRODUCTS=cu,al,ni,au,ag,rb
CANONICAL_COVERAGE=2024-01-01..2025-12-31
CANONICAL_GRANULARITY=1-minute
CANONICAL_CORPUS_IDENTITY=1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8
CANONICAL_QUALIFIED_ELIGIBILITY_VIEW_V1=ADOPTED
CANONICAL_ELIGIBILITY_VIEW_IDENTITY=fb30bfaf0433df02b4ee7d1e781b25473c7271495924859c1d781b87e036c822
CANONICAL_ELIGIBLE_PARTITIONS=32768
CANONICAL_ELIGIBLE_D01_D02=32768_PASS_0_FAIL
E07_MAIN_MAPPING=COMPLETE_FOR_2024_2025_WINDOW_WIRED_FAIL_CLOSED_VERIFIED
CANDIDATE_USE_OF_CURRENT_CANONICAL_CORPUS=NOT_AUTHORIZED
```

The Qualified Eligibility View is data-readiness authority only. It does **not** unlock candidate outcomes.

## Current authorization locks

```text
PERFORMANCE_RESEARCH_STARTED=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
```

No project-recorded real candidate outcome exposure has been established.

## Active future gates / limitations

Only currently relevant unresolved items are indexed in `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`.
The important ones are:

```text
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=NOT_COMPLETE
JIANGHE_AI_REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
JIANGHE_AI_REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
E06_CONTINUOUS_HISTORICAL_EXCHANGE_FEE_MARGIN_SCHEDULE=INSUFFICIENT_EVIDENCE
HISTORICAL_PRICE_LIMIT_OPERATIVE_METADATA=INCOMPLETE_FOR_FULL_CONFIRMATORY_REALISM
PROSPECTIVE_SHADOW_STATISTICAL_PROFILE=NOT_LOCKABLE_UNDER_CURRENT_ASSUMPTION_AUTHORITY
PORTFOLIO_CANDIDATE_OUTCOME_AUTHORITY=NOT_IMPLEMENTED
SOURCE_ONLY_OS_PROCESS_SANDBOX=NOT_PROVEN_NOT_CLAIMED
LOCAL_PRIVATE_STATE_TAMPER_PROOFING=NOT_PROVEN_NOT_CLAIMED
```

The prospective statistical-design limitation is a future candidate-evidence gate. It does not block the current non-outcome real-model fidelity / PRIMARY preparation phase.

## Next normal work

Two bounded lanes may proceed without candidate outcomes:

1. **Claim-level PRIMARY mapping** — review all 352 source-bound claims under `JIANGHE_PRIMARY_BRANCH_PREPARATION_V0_1`, choose exactly one source-justified interpretation branch per claim or an explicit fail-closed STOP disposition, preserve UNKNOWN/conflicts, predeclare alternatives, bind deterministic identities, and use no outcome information. No PRIMARY freeze/promotion occurs merely because the draft mapping is complete.
2. **Real-model fidelity candidate evaluation** — compare candidate models on the integrated Jianghe non-outcome foundation across semantic + visual + structured + dual-input + operational-provider tracks; select by Jianghe fidelity, stability, UNKNOWN honesty, no-invention behavior, governable callability and latency, not by PnL.

A model/provider remains `CANDIDATE` until project evidence verifies it. No model is currently `ADOPTED_JIANGHE_DECISION_MODEL`.

## Authority hygiene

- `PROJECT_BRAIN_RUNTIME_BRIEF.md` is the compact live refresh surface for the project brain.
- `00_READ_FIRST.md` owns takeover/read order.
- `PROJECT_HANDOFF_CURRENT.md` is a pointer-only derived handoff and never overrides this file.
- Jianghe V1.1 source-distillation documents own source semantics/completeness only; mutable SOURCE_ONLY / PRIMARY / authorization state is centralized here and in the runtime brief.
- Historical playbooks, old repair programs, negative source screens, prior integration logs and superseded estimates remain preserved in Git/evidence but are intentionally excluded from this current-state file.

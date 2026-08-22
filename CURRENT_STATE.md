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
NEXT_NORMAL_PHASE=REAL_MODEL_FIDELITY_CANDIDATE_EVALUATION_PLUS_SOURCE_JUSTIFIED_PRIMARY_BRANCH_WORK_WITHOUT_CANDIDATE_OUTCOMES
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
JIANGHE_PRIMARY_NEXT_GATE=SOURCE_JUSTIFIED_PRIMARY_BRANCHES_PLUS_REAL_MODEL_FIDELITY_EVIDENCE_WITHOUT_OUTCOMES
```

Current Jianghe source authority starts at:
`docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md`.

SOURCE_ONLY verification authority:
`docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.md` + `.json`.

## Jianghe AI engineering status

```text
JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1=INTEGRATED_NON_OUTCOME
JIANGHE_AI_OBSERVATION_REPLAY_V0_2=INTEGRATED_SYNTHETIC_NON_OUTCOME
JIANGHE_AI_REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
JIANGHE_AI_REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
JIANGHE_AI_REPLAY_HISTORICAL_BASELINE=COMPLETED_1_MINUTE_BAR
JIANGHE_AI_SUB_MINUTE_LIVE_CAPABILITY=NOT_VALIDATED_NOT_EQUIVALENT_TO_1M_REPLAY
```

Integrated components include causal multi-timeframe observations, rolling market state,
standardized chart rendering, AI-hypothesis annotations, wake events, persistent working memory,
forward-only replay, model-latency accounting, fidelity fixtures, and semantic scoring.

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

1. **Real-model fidelity candidate evaluation** — compare candidate models on the integrated Jianghe non-outcome fidelity fixtures; select by Jianghe fidelity, stability, UNKNOWN honesty, and no-invention behavior, not by PnL.
2. **Source-justified PRIMARY branch work** — define/freeze the source-justified interpretation branches required by the existing research governance without inspecting candidate performance.

A model/provider remains `CANDIDATE` until project evidence verifies it. No model is currently `ADOPTED_JIANGHE_DECISION_MODEL`.

## Authority hygiene

- `PROJECT_BRAIN_RUNTIME_BRIEF.md` is the compact live refresh surface for the project brain.
- `00_READ_FIRST.md` owns takeover/read order.
- `PROJECT_HANDOFF_CURRENT.md` is a pointer-only derived handoff and never overrides this file.
- Historical playbooks, old repair programs, negative source screens, prior integration logs and superseded estimates remain preserved in Git/evidence but are intentionally excluded from this current-state file.

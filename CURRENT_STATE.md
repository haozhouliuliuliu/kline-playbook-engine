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
CURRENT_WORK_PACKAGE=JIANGHE_PRIMARY_MAPPING_AND_REAL_MODEL_FIDELITY_PREOUTCOME
NEXT_NORMAL_PHASE=integrate claim-level semantic mapping + real-model Jianghe fidelity without candidate outcomes
OWNER_ACTION=NONE_FOR_ORDINARY_PREOUTCOME_ENGINEERING
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
JIANGHE_SOURCE_SEMANTICS_CHANGED_BY_HYGIENE=NO
HISTORICAL_PRE_HYGIENE_SOURCE_ONLY_VERIFICATION=PASS
JIANGHE_SOURCE_ONLY_VERIFIED_CURRENT_ACTIVE_BUNDLE=YES
JIANGHE_PRIMARY_ELIGIBLE=NO
KNOWLEDGE_PACK_VERSION=JIANGHE_V1_1
HISTORICAL_PRE_HYGIENE_KNOWLEDGE_PACK_IDENTITY=3f2ddbf9c007b3246661088986a35b84258bdc984ed5fa82dace59074495a9d5
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
JIANGHE_PRIMARY_PREPARATION_SCHEMA_V0_1=INTEGRATED_PRE_FREEZE_NON_OUTCOME__CURRENT_IDENTITY_BINDING_AVAILABLE__MAPPING_SEMANTIC_AUDIT_PENDING_INTEGRATION
JIANGHE_PRIMARY_CLAIM_MANIFEST_IDENTITY=60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940
JIANGHE_PRIMARY_CLAIM_MANIFEST_RECORDS=352
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=NOT_COMPLETE
JIANGHE_PRIMARY_FINAL_BRANCH_IDENTITIES=NOT_ASSERTED_PENDING_CLAIM_LEVEL_SEMANTIC_MAPPING
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
JIANGHE_PRIMARY_NEXT_GATE=COMPLETE_352_CLAIM_LEVEL_SOURCE_JUSTIFIED_MAPPING_PLUS_REAL_MODEL_FIDELITY_WITHOUT_OUTCOMES
JIANGHE_PRIMARY_SEMANTICS=SOURCE_JUSTIFIED_AI_INTERPRETATION_BRANCH_NOT_FIXED_RULE_MACHINE
```

The V1.1 source semantics remain complete and unchanged (`JIANGHE_SOURCE_SEMANTICS_CHANGED_BY_HYGIENE=NO`). The current active bundle identity was deterministically rebuilt from current `main` by the canonical builders (`e079c225...`), and current active-bundle SOURCE_ONLY verification is `YES` with all technical denials PASS. The old `3f2ddbf9...` identity and pre-hygiene SOURCE_ONLY PASS remain valid **historical pre-hygiene evidence**, preserved in the hygiene review and execution evidence; they are no longer the current active-bundle identity.

For the Jianghe AI Trader, PRIMARY does **not** mean converting Jianghe into a rigid threshold strategy. The integrated pre-freeze preparation still uses one source-justified branch object per claim, but final branch identities must bind the rebuilt current knowledge-pack identity. Final semantic freeze remains Owner-gated.

Authorities:
- source view: `docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md`
- identity-rebind review: `docs/reviews/JIANGHE_AUTHORITY_HYGIENE_IDENTITY_REBIND_REVIEW_V0_1.md`
- PRIMARY preparation: `docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_V0_1.md` + schema JSON
- historical pre-hygiene SOURCE_ONLY evidence: `docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.md` + `.json`

## Jianghe AI engineering status

```text
JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1=INTEGRATED_NON_OUTCOME__CURRENT_IDENTITY_METADATA_REBOUND__REAL_MODEL_EVALUATION_NOT_STARTED
JIANGHE_AI_OBSERVATION_REPLAY_V0_2=INTEGRATED_SYNTHETIC_NON_OUTCOME
JIANGHE_AI_REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
JIANGHE_AI_REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
JIANGHE_AI_REAL_MODEL_FIDELITY_REQUIRED_TRACKS=SEMANTIC,VISUAL,STRUCTURED,DUAL_INPUT,OPERATIONAL_PROVIDER
JIANGHE_AI_REPLAY_HISTORICAL_BASELINE=COMPLETED_1_MINUTE_BAR
JIANGHE_AI_SUB_MINUTE_LIVE_CAPABILITY=NOT_VALIDATED_NOT_EQUIVALENT_TO_1M_REPLAY
```

The fidelity fixtures/replay semantics remain non-outcome and intact; fixture metadata is rebound to the current knowledge-pack identity `e079c225...`. Real-model fidelity evaluation has not started.

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

Current highest-priority blocker is `LIMIT-012` in `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`:

```text
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
CURRENT_ACTIVE_SOURCE_ONLY_VERIFICATION=YES
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=NOT_COMPLETE
JIANGHE_AI_REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
JIANGHE_AI_REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
```

Historical fee/margin, price-limit realism, future Shadow statistical profile, portfolio candidate authority, OS sandboxing and local tamper resistance remain deferred limitations as indexed there.

## Next normal work

The identity/evidence rebind under existing semantics is complete: the current V1.1 knowledge-pack artifact and SOURCE_ONLY evidence were deterministically rebuilt from current `main`, all active dependencies now bind the current identity `e079c225...`, and current active-bundle SOURCE_ONLY verification is `YES` with all technical denials PASS.

Two non-outcome lanes are now current:
- **352 claim-level PRIMARY mapping** — one source-justified branch or explicit STOP per claim; no outcome use; no automatic semantic freeze. Identity binding is available; the semantic mapping audit awaits integration.
- **Real-model fidelity candidate evaluation** — semantic + visual + structured + dual-input + operational-provider, selected by Jianghe fidelity rather than PnL; fixture metadata is rebound to the current identity; real-model evaluation has not started.

No model/provider is currently adopted.

## Authority hygiene

- `PROJECT_BRAIN_RUNTIME_BRIEF.md` is the compact live refresh surface.
- `00_READ_FIRST.md` owns takeover/read order.
- `PROJECT_HANDOFF_CURRENT.md` is derived only.
- Jianghe V1.1 source-distillation documents own source semantics/completeness only; mutable readiness is centralized here and in the runtime brief.
- Historical pre-hygiene identities/evidence must be labeled historical and must not be silently reused as current active identities.

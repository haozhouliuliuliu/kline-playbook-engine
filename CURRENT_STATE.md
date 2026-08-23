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
CURRENT_WORK_PACKAGE=JIANGHE_BOUNDED_LIVE_MODEL_FIDELITY_PROBE_APPROVAL_PREPARATION
NEXT_NORMAL_PHASE=owner_approval_then_bounded_real_model_fidelity_probe
OWNER_ACTION=BOUNDED_LIVE_MODEL_FIDELITY_PROBE_APPROVAL_REQUIRED
TOOL_DECISION=USE_EXISTING
```

## Pre-live fidelity gate audit（当前裁决）

```text
PRE_LIVE_FIDELITY_GATE_REAUDIT=PASS
PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT=PASS
LIVE_MODEL_PROVIDER_PROBE=AWAITING_OWNER_BOUNDED_PROBE_APPROVAL
PAID_MODEL_SPEND=NOT_AUTHORIZED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
OUTCOME_ACCESS=NO
PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT_AUTHORITY=docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT_V0_1.md
PRIMARY_CURATED_QUALITY_GATE_V0_5=docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_GATE_V0_5.json
PRELIVE_AUDIT_AUTHORITY=docs/reviews/JIANGHE_PRE_LIVE_FIDELITY_GATE_AUDIT_V0_1.md
PRELIVE_REAUDIT_AUTHORITY=docs/reviews/JIANGHE_PRE_LIVE_FIDELITY_GATE_REAUDIT_V0_1.md
```

The engineering evidence-chain findings from the pre-live audit have been repaired and integrated on the current main lineage: strict fidelity-evaluator evidence handling, deterministic visual rendering plus adversarial repair, governed observation/replay identity, AI research-object identity, strict runtime normalizer, provider evidence contract, and candidate prompt package. No real provider/model call has occurred.

The independent WorkBuddy read-only audit under the fixed R1–R8 rubric recorded `PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT=PASS` for the exact V0.5 candidate commit, and the full original pre-live gate re-audit closed all 27 findings (G-01..G-03, H-01..H-13, O-01..O-03, N-01..N-04, P-01..P-04) with concrete code/artifact/test evidence in the integration tree, giving `PRE_LIVE_FIDELITY_GATE_REAUDIT=PASS`. The candidate prompt package was mechanically rebound to the PRIMARY V0.5 scope with recomputed identities.

`PRE_LIVE_FIDELITY_GATE_REAUDIT=PASS` does **not** authorize any real provider/model call, paid spend, candidate outcomes, Validation/Final/Shadow, Broker, or real-money activity. It only closes the original pre-live audit blocker. The next normal phase is a bounded real-model fidelity probe **only after Owner approval** covering credentials / data egress / paid spend; that approval does not unlock candidate outcomes. Final PRIMARY semantic freeze remains a separate Owner decision after real-model fidelity evidence.

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

## Jianghe knowledge / PRIMARY status

```text
JIANGHE_SOURCE_DISTILLATION=V1_1_EXHAUSTIVE_SECOND_PASS_COMPLETE
JIANGHE_SOURCE_SEMANTICS_CHANGED_BY_HYGIENE=NO
JIANGHE_SOURCE_ONLY_VERIFIED_CURRENT_ACTIVE_BUNDLE=YES
KNOWLEDGE_PACK_VERSION=JIANGHE_V1_1
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
JIANGHE_PRIMARY_CLAIM_MANIFEST_IDENTITY=60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940
JIANGHE_PRIMARY_CLAIM_MANIFEST_RECORDS=352
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=INTEGRATED_PRE_FREEZE_IDENTITY_BOUND__FIXED_RUBRIC_REAUDIT_PASS
JIANGHE_PRIMARY_BRANCH_REGISTRY_V0_5=INTEGRATED_PRE_FREEZE_NON_FINAL_FIXED_RUBRIC_REAUDIT_PASS
JIANGHE_PRIMARY_REGISTRY_DECLARED_READY_COUNT=340
JIANGHE_PRIMARY_REGISTRY_STOP_COUNT=12
JIANGHE_PRIMARY_PROJECT_BRAIN_ACCEPTED_READY_COUNT=340
JIANGHE_PRIMARY_CURATED_Q01_SOL_REVIEW_READY_CONFLICT_COUNT=0_RESOLVED_BY_V0_5
JIANGHE_PRIMARY_CURATED_Q02_TEMPLATE_EVIDENCE_PROBLEM=RESOLVED_BY_V0_5_FIXED_RUBRIC_REAUDIT
JIANGHE_PRIMARY_BRANCH_IDENTITIES_DETERMINISTIC=YES_FOR_CURRENT_NON_FINAL_REGISTRY
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
JIANGHE_PRIMARY_NEXT_GATE=OWNER_FREEZE_DECISION_AFTER_REAL_MODEL_FIDELITY_EVIDENCE
```

The V0.5 registry is a complete identity-bound pre-freeze artifact whose curated-quality repair has passed the independent fixed R1–R8 re-audit (`PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT=PASS`, 352 total / 340 READY / 12 STOP). `340 READY` is now project-brain accepted as the re-audited non-final population. `PRIMARY_ELIGIBLE=NO` remains: acceptance of curated quality does not create PRIMARY eligibility, freeze, outcome access, or model/provider adoption.

Authorities:
- source view: `docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md`
- PRIMARY preparation: `docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_V0_1.md` + schema JSON
- current non-final registry: `docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_5.md` + JSONL + curated review `..._V0_5.jsonl`
- fixed-rubric re-audit: `docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT_V0_1.md`
- repair review: `docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_REPAIR_V0_2.md`
- SOURCE_ONLY evidence: `docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.md` + `.json`

## Jianghe AI engineering status

```text
JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1=INTEGRATED_NON_OUTCOME__CURRENT_IDENTITY_METADATA_REBOUND
JIANGHE_AI_FIDELITY_EVALUATION_HARNESS_V0_1=INTEGRATED_OFFLINE_PROVIDER_NEUTRAL__PRELIVE_EVIDENCE_REPAIRED
JIANGHE_AI_OBSERVATION_REPLAY_V0_2=INTEGRATED_SYNTHETIC_NON_OUTCOME__OBSERVATION_IDENTITY_BOUND
JIANGHE_AI_VISUAL_RENDERER=INTEGRATED_V0_1_DETERMINISTIC_PROVIDER_NEUTRAL__ADVERSARIAL_80_OF_80_PASS
JIANGHE_AI_RUNTIME_NORMALIZER=INTEGRATED_V0_1_STRICT_VERSIONED_DETERMINISTIC
JIANGHE_AI_PROVIDER_EVIDENCE_CONTRACT=INTEGRATED_CANDIDATE_LIVE_DISABLED
JIANGHE_AI_LIVE_FIDELITY_PROMPT_PACKAGE=INTEGRATED_CANDIDATE_PRE_LIVE_NON_OUTCOME_NOT_ADOPTED__PRIMARY_SCOPE_REBOUND_TO_V0_5
JIANGHE_AI_REAL_MODEL_PROVIDER=LIVE_TRANSPORT_NOT_IMPLEMENTED_NOT_VERIFIED_NOT_ADOPTED
JIANGHE_AI_REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
JIANGHE_AI_REAL_MODEL_FIDELITY_REQUIRED_TRACKS=SEMANTIC,VISUAL,STRUCTURED,DUAL_INPUT,OPERATIONAL_PROVIDER
JIANGHE_AI_REPLAY_HISTORICAL_BASELINE=COMPLETED_1_MINUTE_BAR
JIANGHE_AI_SUB_MINUTE_LIVE_CAPABILITY=NOT_VALIDATED_NOT_EQUIVALENT_TO_1M_REPLAY
```

The current main now contains the repaired offline evidence chain needed to support a future bounded live fidelity probe. That does **not** authorize such a probe. The pre-live blocker and the PRIMARY curated-quality blocker are both closed; a bounded real-provider fidelity probe remains Owner-gated for credentials, data egress and paid spend.

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
LIVE_MODEL_PROVIDER_PROBE=AWAITING_OWNER_BOUNDED_PROBE_APPROVAL
PAID_MODEL_SPEND=NOT_AUTHORIZED
OUTCOME_ACCESS=NO
```

No project-recorded real candidate outcome exposure has been established.

## Active future gates / limitations

The original pre-live gate blocker is closed by `PRE_LIVE_FIDELITY_GATE_REAUDIT=PASS`, and the PRIMARY curated-quality blocker is closed by `PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT=PASS` (see `docs/reviews/JIANGHE_PRE_LIVE_FIDELITY_GATE_REAUDIT_V0_1.md` and `docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT_V0_1.md`). `LIMIT-013` and `LIMIT-014` are resolved in `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`. `LIMIT-012` remains the longer-horizon limitation that no real-model Jianghe fidelity evaluation has yet been run.

Historical fee/margin, price-limit realism, future Shadow statistical profile, portfolio candidate authority, OS sandboxing and local tamper resistance remain deferred limitations as indexed in `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`.

## Next normal work

The PRIMARY V0.5 curated-quality repair is integrated and the full pre-live gate re-audit has passed. The current package is **Owner-gated preparation for one bounded real-model fidelity probe** (still non-outcome):

- prepare the exact bounded live fidelity probe request for Owner approval (credentials / data egress / paid spend scope);
- the probe uses the integrated non-outcome Jianghe fidelity fixtures, the candidate pre-live prompt package now rebound to PRIMARY V0.5, the strict runtime normalizer, the provider evidence contract, and the deterministic identity/replay chain;
- real-model fidelity is evaluated on semantic / visual / structured / dual-input / operational-provider tracks only;
- model selection is based on Jianghe fidelity, stability, UNKNOWN honesty and no-invention behavior — not candidate returns.

No provider/model call, candidate outcome access, or paid spend occurs until Owner approval. `LIVE_MODEL_PROVIDER_PROBE=AWAITING_OWNER_BOUNDED_PROBE_APPROVAL`. Final PRIMARY semantic freeze remains a separate Owner decision after real-model fidelity evidence.

No model/provider is currently VERIFIED or ADOPTED.

## Authority hygiene

- `PROJECT_BRAIN_RUNTIME_BRIEF.md` is the compact live refresh surface.
- `00_READ_FIRST.md` owns takeover/read order.
- `PROJECT_HANDOFF_CURRENT.md` is derived only.
- Jianghe V1.1 source-distillation documents own source semantics/completeness only; mutable readiness is centralized here and in the runtime brief.
- Historical pre-hygiene identities/evidence must be labeled historical and must not be silently reused as current active identities.

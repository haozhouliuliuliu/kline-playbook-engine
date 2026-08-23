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
CURRENT_WORK_PACKAGE=JIANGHE_PRIMARY_CURATED_QUALITY_REPAIR_PRE_FREEZE
NEXT_NORMAL_PHASE=re_review_352_claims_and_rebuild_primary_registry_then_independent_pre_live_gate_reaudit
OWNER_ACTION=NONE_UNTIL_PRIMARY_QUALITY_REPAIR_AND_PRELIVE_REAUDIT_PASS
TOOL_DECISION=USE_EXISTING
```

## Pre-live fidelity gate audit（当前裁决）

```text
PRE_LIVE_FIDELITY_GATE_AUDIT=NOT_READY_REPAIR_REQUIRED
LIVE_MODEL_PROVIDER_PROBE=BLOCKED_PENDING_PRIMARY_CURATED_QUALITY_REPAIR
PAID_MODEL_SPEND=NOT_AUTHORIZED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
OUTCOME_ACCESS=NO
PRIMARY_CURATED_QUALITY_AUDIT=FAIL_CLOSED_MATERIAL_FINDINGS
PRIMARY_CURATED_QUALITY_AUTHORITY=docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_AUDIT_V0_1.md
PRELIVE_AUDIT_AUTHORITY=docs/reviews/JIANGHE_PRE_LIVE_FIDELITY_GATE_AUDIT_V0_1.md
```

The engineering evidence-chain findings from the pre-live audit have been repaired and integrated on the current main lineage: strict fidelity-evaluator evidence handling, deterministic visual rendering plus adversarial repair, governed observation/replay identity, AI research-object identity, strict runtime normalizer, provider evidence contract, and candidate prompt package. No real provider/model call has occurred.

The gate remains fail-closed because the independent PRIMARY curated-quality audit found material issues: five records simultaneously declare `SOL_REVIEW_REQUIRED` and `READY_FOR_PRIMARY_FREEZE`, and the existing 352-record review artifact does not provide credible claim-specific evidence that a substantive per-claim review occurred. The current registry is therefore a mechanically valid pre-freeze artifact, not an accepted freeze-ready semantic set.

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
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=INTEGRATED_PRE_FREEZE_IDENTITY_BOUND__CURATED_QUALITY_REPAIR_REQUIRED
JIANGHE_PRIMARY_BRANCH_REGISTRY_V0_3=INTEGRATED_PRE_FREEZE_NON_FINAL
JIANGHE_PRIMARY_REGISTRY_DECLARED_READY_COUNT=340
JIANGHE_PRIMARY_REGISTRY_STOP_COUNT=12
JIANGHE_PRIMARY_PROJECT_BRAIN_ACCEPTED_READY_COUNT=NOT_ESTABLISHED_PENDING_CURATED_QUALITY_REPAIR
JIANGHE_PRIMARY_CURATED_Q01_SOL_REVIEW_READY_CONFLICT_COUNT=5
JIANGHE_PRIMARY_CURATED_Q02_TEMPLATE_EVIDENCE_PROBLEM=CONFIRMED
JIANGHE_PRIMARY_BRANCH_IDENTITIES_DETERMINISTIC=YES_FOR_CURRENT_NON_FINAL_REGISTRY
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
JIANGHE_PRIMARY_NEXT_GATE=CURATED_QUALITY_REPAIR_THEN_PRELIVE_GATE_REAUDIT
```

The current registry remains useful as a complete identity-bound scaffold, but `340 READY` is only the registry's present mechanical declaration. It is **not** project-brain accepted as the freeze-ready population. The repair may legitimately change READY/STOP counts. No target count is to be preserved.

Authorities:
- source view: `docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md`
- PRIMARY preparation: `docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_V0_1.md` + schema JSON
- current non-final registry: `docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_3.md` + JSONL
- curated-quality audit: `docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_AUDIT_V0_1.md`
- SOURCE_ONLY evidence: `docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.md` + `.json`

## Jianghe AI engineering status

```text
JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1=INTEGRATED_NON_OUTCOME__CURRENT_IDENTITY_METADATA_REBOUND
JIANGHE_AI_FIDELITY_EVALUATION_HARNESS_V0_1=INTEGRATED_OFFLINE_PROVIDER_NEUTRAL__PRELIVE_EVIDENCE_REPAIRED
JIANGHE_AI_OBSERVATION_REPLAY_V0_2=INTEGRATED_SYNTHETIC_NON_OUTCOME__OBSERVATION_IDENTITY_BOUND
JIANGHE_AI_VISUAL_RENDERER=INTEGRATED_V0_1_DETERMINISTIC_PROVIDER_NEUTRAL__ADVERSARIAL_80_OF_80_PASS
JIANGHE_AI_RUNTIME_NORMALIZER=INTEGRATED_V0_1_STRICT_VERSIONED_DETERMINISTIC
JIANGHE_AI_PROVIDER_EVIDENCE_CONTRACT=INTEGRATED_CANDIDATE_LIVE_DISABLED
JIANGHE_AI_LIVE_FIDELITY_PROMPT_PACKAGE=INTEGRATED_CANDIDATE_PRE_LIVE_NON_OUTCOME_NOT_ADOPTED
JIANGHE_AI_REAL_MODEL_PROVIDER=LIVE_TRANSPORT_NOT_IMPLEMENTED_NOT_VERIFIED_NOT_ADOPTED
JIANGHE_AI_REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
JIANGHE_AI_REAL_MODEL_FIDELITY_REQUIRED_TRACKS=SEMANTIC,VISUAL,STRUCTURED,DUAL_INPUT,OPERATIONAL_PROVIDER
JIANGHE_AI_REPLAY_HISTORICAL_BASELINE=COMPLETED_1_MINUTE_BAR
JIANGHE_AI_SUB_MINUTE_LIVE_CAPABILITY=NOT_VALIDATED_NOT_EQUIVALENT_TO_1M_REPLAY
```

The current main now contains the repaired offline evidence chain needed to support a future bounded live fidelity probe. That does **not** authorize such a probe. The remaining pre-live blocker is the PRIMARY curated-quality repair and subsequent independent gate re-audit.

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
LIVE_MODEL_PROVIDER_PROBE=BLOCKED_PENDING_PRIMARY_CURATED_QUALITY_REPAIR
PAID_MODEL_SPEND=NOT_AUTHORIZED
OUTCOME_ACCESS=NO
```

No project-recorded real candidate outcome exposure has been established.

## Active future gates / limitations

The immediate blocker is the PRIMARY curated-quality finding recorded in `docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_AUDIT_V0_1.md`. `LIMIT-013` remains active until the same pre-live gate is re-audited and passes. `LIMIT-012` remains the longer-horizon limitation that no real-model Jianghe fidelity evaluation has yet been run.

Historical fee/margin, price-limit realism, future Shadow statistical profile, portfolio candidate authority, OS sandboxing and local tamper resistance remain deferred limitations as indexed in `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`.

## Next normal work

The current package is a **full claim-level PRIMARY curated quality repair**, still pre-freeze and non-outcome:

- re-review all 352 claim records against source authority rather than template inheritance;
- resolve the five `SOL_REVIEW_REQUIRED` / READY contradictions by actual source review, not status rewriting;
- replace template-only rationale/interpretation/operationalization with claim-specific reasoning where justified;
- preserve UNKNOWN, contradictions, observability gaps and STOP dispositions when the source does not justify resolution;
- rebuild deterministic non-final registry identities from the repaired curated data;
- independently adversarially re-audit the repaired registry before any Owner freeze request or live model probe.

No provider/model call or candidate outcome access occurs in this package. Only after the PRIMARY quality repair **and** the full pre-live gate re-audit pass may the project request Owner approval for a bounded real-provider fidelity probe covering credentials/data egress/paid spend. That approval does **not** unlock candidate outcomes. Final PRIMARY semantic freeze remains a separate Owner decision after real-model fidelity evidence.

No model/provider is currently VERIFIED or ADOPTED.

## Authority hygiene

- `PROJECT_BRAIN_RUNTIME_BRIEF.md` is the compact live refresh surface.
- `00_READ_FIRST.md` owns takeover/read order.
- `PROJECT_HANDOFF_CURRENT.md` is derived only.
- Jianghe V1.1 source-distillation documents own source semantics/completeness only; mutable readiness is centralized here and in the runtime brief.
- Historical pre-hygiene identities/evidence must be labeled historical and must not be silently reused as current active identities.

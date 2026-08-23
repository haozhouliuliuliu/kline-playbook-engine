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
CURRENT_WORK_PACKAGE=JIANGHE_PRE_LIVE_FIDELITY_GATE_AUDIT_REPAIR
NEXT_NORMAL_PHASE=repair_pre_live_identity_fidelity_provider_normalizer_and_visual_findings_then_rerun_gate_audit
OWNER_ACTION=NONE_UNTIL_REAUDIT_PASSES_AND_LIVE_PROBE_APPROVAL_IS_REQUESTED
TOOL_DECISION=USE_EXISTING
```

## Pre-live fidelity gate audit（当前裁决）

```text
PRE_LIVE_FIDELITY_GATE_AUDIT=NOT_READY_REPAIR_REQUIRED
LIVE_MODEL_PROVIDER_PROBE=BLOCKED_PENDING_AUDIT_REPAIR
PAID_MODEL_SPEND=NOT_AUTHORIZED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
OUTCOME_ACCESS=NO
AUTHORITY=docs/reviews/JIANGHE_PRE_LIVE_FIDELITY_GATE_AUDIT_V0_1.md
```

Live probe 前发现证据链缺口（G-01..G-03、H-01..H-08、H-09..H-13、
O-01..O-03、N-01..N-04、P-01..P-04），详见审计文件。修复完成并重新运行
gate audit 之前，`LIVE_MODEL_PROVIDER_PROBE` 保持 BLOCKED。

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
HISTORICAL_PRE_HYGIENE_SOURCE_ONLY_VERIFICATION=PASS
JIANGHE_SOURCE_ONLY_VERIFIED_CURRENT_ACTIVE_BUNDLE=YES
KNOWLEDGE_PACK_VERSION=JIANGHE_V1_1
HISTORICAL_PRE_HYGIENE_KNOWLEDGE_PACK_IDENTITY=3f2ddbf9c007b3246661088986a35b84258bdc984ed5fa82dace59074495a9d5
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
JIANGHE_PRIMARY_CLAIM_MANIFEST_IDENTITY=60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940
JIANGHE_PRIMARY_CLAIM_MANIFEST_RECORDS=352
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=COMPLETE_PRE_FREEZE_IDENTITY_BOUND
JIANGHE_PRIMARY_BRANCH_REGISTRY_V0_3=INTEGRATED_PRE_FREEZE_NON_FINAL
JIANGHE_PRIMARY_READY_FOR_FREEZE_COUNT=340
JIANGHE_PRIMARY_STOP_SOURCE_AMBIGUOUS_COUNT=2
JIANGHE_PRIMARY_STOP_SOURCE_CONFLICT_COUNT=5
JIANGHE_PRIMARY_STOP_OBSERVABILITY_GAP_COUNT=5
JIANGHE_PRIMARY_STOP_IDENTITY_INCOMPLETE_COUNT=0
JIANGHE_PRIMARY_BRANCH_IDENTITIES_DETERMINISTIC=YES
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
JIANGHE_PRIMARY_NEXT_GATE=REAL_MODEL_FIDELITY_EVIDENCE_THEN_OWNER_PRIMARY_FREEZE_DECISION
JIANGHE_PRIMARY_SEMANTICS=SOURCE_JUSTIFIED_AI_INTERPRETATION_BRANCH_NOT_FIXED_RULE_MACHINE
```

The 352-claim identity-bound pre-freeze registry is integrated. `STOP_*` records remain first-class fail-closed results; no UNKNOWN or contradiction was guessed away. Deterministic branch identities do **not** mean deterministic market decisions, and they do not constitute the Owner-gated PRIMARY semantic freeze.

Authorities:
- source view: `docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md`
- PRIMARY preparation: `docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_PREPARATION_V0_1.md` + schema JSON
- identity-bound registry: `docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_3.md` + JSONL
- SOURCE_ONLY evidence: `docs/evidence/JIANGHE_V1_1_SOURCE_ONLY_VERIFICATION_V0_1.md` + `.json`

## Jianghe AI engineering status

```text
JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1=INTEGRATED_NON_OUTCOME__CURRENT_IDENTITY_METADATA_REBOUND
JIANGHE_AI_FIDELITY_EVALUATION_HARNESS_V0_1=INTEGRATED_OFFLINE_PROVIDER_NEUTRAL
JIANGHE_AI_OBSERVATION_REPLAY_V0_2=INTEGRATED_SYNTHETIC_NON_OUTCOME
JIANGHE_AI_VISUAL_RENDERER=IN_PREPARATION_NOT_INTEGRATED
JIANGHE_AI_REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
JIANGHE_AI_REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
JIANGHE_AI_REAL_MODEL_FIDELITY_REQUIRED_TRACKS=SEMANTIC,VISUAL,STRUCTURED,DUAL_INPUT,OPERATIONAL_PROVIDER
JIANGHE_AI_REPLAY_HISTORICAL_BASELINE=COMPLETED_1_MINUTE_BAR
JIANGHE_AI_SUB_MINUTE_LIVE_CAPABILITY=NOT_VALIDATED_NOT_EQUIVALENT_TO_1M_REPLAY
```

The provider-neutral offline fidelity harness is integrated and reuses the existing Jianghe fidelity scorer. It makes no model/network calls and does not select or adopt a provider. Real-model fidelity remains blocked on a governed provider seam plus standardized visual input, followed by an Owner-authorized live probe because provider access may involve credentials, data egress and paid spend.

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
LIVE_MODEL_PROVIDER_PROBE=BLOCKED_PENDING_AUDIT_REPAIR
PAID_MODEL_SPEND=NOT_AUTHORIZED
OUTCOME_ACCESS=NO
```

No project-recorded real candidate outcome exposure has been established.

## Active future gates / limitations

Current highest-priority blocker remains `LIMIT-012` in `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`:

```text
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
CURRENT_ACTIVE_SOURCE_ONLY_VERIFICATION=YES
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=COMPLETE_PRE_FREEZE_IDENTITY_BOUND
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
JIANGHE_AI_REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
JIANGHE_AI_REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
```

Historical fee/margin, price-limit realism, future Shadow statistical profile, portfolio candidate authority, OS sandboxing and local tamper resistance remain deferred limitations as indexed there.

## Next normal work

Current package is the pre-live fidelity gate audit repair, which must stay fail-closed and offline:

- **fidelity evaluator evidence completeness** — outcome contamination fail-closed
  (PROCESSING_STATUS=ERROR / EVIDENCE_ELIGIBLE=NO), strict response schema,
  exact corpus binding, failed-call non-scoreable, strict types, typed input
  provenance per track, metadata allowlist + recursive contamination scan,
  deterministic report identity, and separation of processing_status /
  evidence_completeness / evidence_eligibility;
- **visual renderer import + independent review** — port WorkBuddy visual renderer
  by file/hash (no branch-ancestry merge), then review for pure stdlib, no network,
  no system font/clock/random, deterministic artifact identities, no PnL/outcome,
  provider-neutral;
- **real-model firewall tests** — prove the new paths reject unknown outcome fields,
  contamination, corpus mismatch, missing provenance, etc., without any real model call.

No provider/model call or candidate outcome access occurs in this package. After the
repair and a re-run of the gate audit confirm no remaining evidence gaps, the next
Owner gate is a bounded real-provider fidelity probe (credentials/data egress/paid
spend). That approval does **not** unlock candidate outcomes. After real-model
fidelity evidence supports a model/provider, the final PRIMARY semantic freeze
remains a separate Owner decision before any outcome-bearing candidate research.

No model/provider is currently VERIFIED or ADOPTED.

## Authority hygiene

- `PROJECT_BRAIN_RUNTIME_BRIEF.md` is the compact live refresh surface.
- `00_READ_FIRST.md` owns takeover/read order.
- `PROJECT_HANDOFF_CURRENT.md` is derived only.
- Jianghe V1.1 source-distillation documents own source semantics/completeness only; mutable readiness is centralized here and in the runtime brief.
- Historical pre-hygiene identities/evidence must be labeled historical and must not be silently reused as current active identities.

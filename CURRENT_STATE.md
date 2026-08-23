# CURRENT_STATE

> Mutable project-state authority. Keep this file current and compact.
> Historical stages and superseded proposals belong in Git history or durable review artifacts.

## Current phase

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
CURRENT_ADOPTED_ARCHITECTURE=Skeleton_v1.0_PLUS_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1
ARCHITECTURE_STATUS=ACCEPTED
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
RESEARCH_DIRECTION_STATUS=OWNER_APPROVED
STRATEGY_SOURCE_EXPANSION=PAUSED_FOR_V1
JIANGHE_V1=SOLE_CURRENT_TRADING_KNOWLEDGE_SOURCE
CURRENT_WORK_PACKAGE=JIANGHE_PRE_SPEND_CONSOLIDATED_REPAIR_REQUIRED
NEXT_NORMAL_PHASE=fresh_project_brain_takeover_then_verify_frozen_findings_refresh_provider_costs_owner_select_provider_then_one_batched_repair
OWNER_ACTION=NONE_FOR_ORDINARY_REPAIR__FINAL_PROVIDER_SELECTION_AND_ANY_PAID_CALL_REMAIN_OWNER_GATED
TOOL_DECISION=USE_EXISTING
```

## Current pre-live / spend gates

```text
PRE_LIVE_FIDELITY_GATE_REAUDIT=PASS
PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT=PASS
PRE_SPEND_DOUBLE_AUDIT=COMPLETE_FAIL_REPAIR_REQUIRED
PRE_SPEND_CONSOLIDATED_FINDINGS=FROZEN
PRE_SPEND_BLOCKER_BEFORE_SPEND_COUNT=5
PRE_SPEND_REPAIR_RECOMMENDED_COUNT=2
SPEND_GATE=CLOSED
LIVE_MODEL_PROVIDER_PROBE=BLOCKED_PENDING_PRESPEND_REPAIR_REAUDIT_AND_FINAL_PROVIDER_SELECTION
PAID_MODEL_SPEND=NOT_AUTHORIZED
TOTAL_HARD_SPEND_CAP_CNY_IF_LATER_APPROVED=100.00
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
OUTCOME_ACCESS=NO
```

Current authorities:
- consolidated pre-spend findings: `docs/reviews/JIANGHE_PRE_SPEND_DOUBLE_AUDIT_CONSOLIDATED_FINDINGS_V0_1.md`
- Owner-requested two-review plan: `docs/reviews/JIANGHE_PRE_SPEND_DOUBLE_AUDIT_PLAN_V0_1.md`
- Owner live-probe scope revision: `docs/reviews/JIANGHE_LIVE_PROBE_OWNER_SCOPE_REVISION_V0_2.md`
- pre-live re-audit: `docs/reviews/JIANGHE_PRE_LIVE_FIDELITY_GATE_REAUDIT_V0_1.md`
- PRIMARY fixed-rubric re-audit: `docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT_V0_1.md`
- superseded historical approval proposal: `docs/reviews/JIANGHE_BOUNDED_LIVE_MODEL_FIDELITY_PROBE_APPROVAL_PACKAGE_V0_1.md`

The original 27-item pre-live audit and PRIMARY V0.5 fixed R1–R8 re-audit remain PASS. The later Owner-requested pre-spend assurance review is now complete and found concrete blockers. This is not a reopening of PRIMARY prose/template standards.

The dated double-audit plan still contains `PENDING` text because it is the historical plan document. Current completion status is owned by this file and the consolidated findings authority.

## Frozen current pre-spend findings

```text
BSP-001=BLOCKER__MISSING_CONTENT_ADDRESSED_JIANGHE_CONTEXT_IN_SPEND_ELIGIBLE_REQUEST
BSP-002=BLOCKER__STRUCTURED_INPUT_NOT_STRICT_CLOSED_WORLD_CANONICAL_OBSERVATION_ARTIFACT
BSP-003=BLOCKER__MODEL_DECLARED_PRINCIPLE_REFERENCES_CAN_BECOME_POSITIVE_SCORING_EVIDENCE
BSP-004=BLOCKER__REAL_PROVIDER_TRANSPORT_NOT_IMPLEMENTED
BSP-005=BLOCKER__RMB100_HARD_CAP_NOT_CODE_ENFORCED
RSP-001=REPAIR_RECOMMENDED__OMS_SIDE_EFFECTS_PRECEDE_AUTHORITATIVE_TRADINGSTATE_EVENT_ADMISSION
RSP-002=REPAIR_RECOMMENDED__SAME_INTENT_ID_DIFFERENT_CONTENT_CAN_SILENTLY_COLLAPSE
```

Full evidence, acceptance invariants, non-findings and closure rules live only in:
`docs/reviews/JIANGHE_PRE_SPEND_DOUBLE_AUDIT_CONSOLIDATED_FINDINGS_V0_1.md`.

The finding set and non-negotiable acceptance invariants are frozen. Exact implementation design is deliberately **not** frozen; the next fresh project brain must independently refresh current `main`, verify the findings, and choose the simplest correct repair. Do not restart open-ended review cycles without new concrete correctness/evidence/security/cost evidence.

## Owner provider / cost scope

```text
ANTHROPIC_CLAUDE=EXCLUDED_BY_OWNER
GOOGLE_GEMINI=EXCLUDED_BY_OWNER
OPENAI_GPT_5_6_SOL=CANDIDATE_RETAINED
XAI_GROK_4_6=CANDIDATE_UNDER_OWNER_CONSIDERATION
KIMI_K3=CANDIDATE_UNDER_OWNER_CONSIDERATION
DEEPSEEK_V4_FLASH_VISION_EXP=CANDIDATE_UNDER_OWNER_CONSIDERATION__EXPERIMENTAL
FINAL_APPROVED_PROVIDER_SET=NOT_DECIDED
NO_MODEL_OR_PROVIDER_VERIFIED=YES
NO_MODEL_OR_PROVIDER_ADOPTED=YES
```

The previous USD 100 / OpenAI+Anthropic+Gemini proposal is superseded for execution. The Owner's binding budget ceiling is **RMB 100 total**, with no automatic extension.

Before recommending the final provider set, the next project brain must recheck current first-party provider/model capability and direct pricing because those facts are time-sensitive. Final provider/model selection and any paid external call remain Owner decisions.

DeepSeek `deepseek-v4-flash-vision-exp` remains an experimental candidate; prior price reconnaissance is not sufficient authority for a future spend decision without a fresh first-party recheck.

## Product / strategy boundary

```text
AI_ROLE=JIANGHE_STYLE_MARKET_READING_AND_TRADE_DECISION
MECHANICAL_ROLE=HARD_RISK_ORDER_EXECUTION_RECONCILIATION_SAFETY
AI_ALLOWED_FAMILIES=A,B,C,D,NONE
UNKNOWN_OR_UNFAMILIAR=WAIT_OR_NO_TRADE
DETERMINISTIC_RISK_EXECUTION_SAFETY=AUTHORITATIVE
AI_MAY_NOT_CHANGE_HARD_RISK_LIMITS=YES
INITIAL_MODEL_SELECTION_TARGET=JIANGHE_FIDELITY_NOT_PROFIT
REAL_MODEL_SELECTION_MUST_INCLUDE_VISUAL_KLINE_EYES=YES
```

## Jianghe knowledge / PRIMARY

```text
JIANGHE_SOURCE_DISTILLATION=V1_1_EXHAUSTIVE_SECOND_PASS_COMPLETE
JIANGHE_SOURCE_ONLY_VERIFIED_CURRENT_ACTIVE_BUNDLE=YES
KNOWLEDGE_PACK_VERSION=JIANGHE_V1_1
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2
JIANGHE_PRIMARY_CLAIM_MANIFEST_IDENTITY=60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940
JIANGHE_PRIMARY_CLAIM_MANIFEST_RECORDS=352
JIANGHE_PRIMARY_BRANCH_REGISTRY_V0_5=INTEGRATED_PRE_FREEZE_NON_FINAL_FIXED_RUBRIC_REAUDIT_PASS
JIANGHE_PRIMARY_PROJECT_BRAIN_ACCEPTED_READY_COUNT=340
JIANGHE_PRIMARY_REGISTRY_STOP_COUNT=12
JIANGHE_PRIMARY_BRANCH_IDENTITIES_DETERMINISTIC=YES_FOR_CURRENT_NON_FINAL_REGISTRY
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
```

## Jianghe AI engineering

```text
JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1=INTEGRATED_NON_OUTCOME__CURRENT_IDENTITY_METADATA_REBOUND
JIANGHE_AI_FIDELITY_EVALUATION_HARNESS_V0_1=INTEGRATED_OFFLINE_PROVIDER_NEUTRAL__PRELIVE_EVIDENCE_REPAIRED__BSP003_REPAIR_REQUIRED_BEFORE_SPEND
JIANGHE_AI_OBSERVATION_REPLAY_V0_2=INTEGRATED_SYNTHETIC_NON_OUTCOME__OBSERVATION_IDENTITY_BOUND
JIANGHE_AI_VISUAL_RENDERER=INTEGRATED_V0_1_DETERMINISTIC_PROVIDER_NEUTRAL__ADVERSARIAL_80_OF_80_PASS
JIANGHE_AI_RUNTIME_NORMALIZER=INTEGRATED_V0_1_STRICT_VERSIONED_DETERMINISTIC
JIANGHE_AI_PROVIDER_EVIDENCE_CONTRACT=INTEGRATED_CANDIDATE_LIVE_DISABLED__PRESPEND_REPAIR_REQUIRED
JIANGHE_AI_LIVE_FIDELITY_PROMPT_PACKAGE=INTEGRATED_CANDIDATE_PRE_LIVE_NON_OUTCOME_NOT_ADOPTED__PRIMARY_SCOPE_REBOUND_TO_V0_5__BSP001_CONTEXT_MATERIAL_BINDING_REQUIRED
JIANGHE_AI_REAL_MODEL_PROVIDER=LIVE_TRANSPORT_NOT_IMPLEMENTED_NOT_VERIFIED_NOT_ADOPTED
JIANGHE_AI_REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
JIANGHE_AI_REAL_MODEL_FIDELITY_REQUIRED_TRACKS=SEMANTIC,VISUAL,STRUCTURED,DUAL_INPUT,OPERATIONAL_PROVIDER
JIANGHE_AI_REPLAY_HISTORICAL_BASELINE=COMPLETED_1_MINUTE_BAR
JIANGHE_AI_SUB_MINUTE_LIVE_CAPABILITY=NOT_VALIDATED_NOT_EQUIVALENT_TO_1M_REPLAY
```

## Data / authorization locks

```text
CANONICAL_PRODUCTS=cu,al,ni,au,ag,rb
CANONICAL_COVERAGE=2024-01-01..2025-12-31
CANONICAL_GRANULARITY=1-minute
CANONICAL_CORPUS_IDENTITY=1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8
CANDIDATE_USE_OF_CURRENT_CANONICAL_CORPUS=NOT_AUTHORIZED
PERFORMANCE_RESEARCH_STARTED=NO
VALIDATION_ACCESS=LOCKED_BY_PROJECT_POLICY
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
LIVE_CALLS=0
PAID_SPEND=0
OUTCOME_ACCESS=NO
```

`LIMIT-012` remains active because no real-model Jianghe fidelity evaluation has occurred. `LIMIT-015` is the highest current pre-spend blocker and points to the frozen consolidated findings. Resolved historical LIMIT-013/LIMIT-014 remain preserved in their durable review evidence/Git history and are no longer active limitation entries.

## Next normal work

1. Fresh project brain performs the read-only takeover from current `main`; Owner accepts takeover before work begins.
2. Re-read the frozen consolidated finding authority and independently verify BSP-001..005 and RSP-001..002 against current source. This is verification, not a new open-ended audit.
3. Refresh first-party capability/pricing for the remaining provider/model candidates and present a final cost/capability recommendation.
4. Owner selects the final provider/model set and bounded probe scope. This is the next major Owner decision.
5. After selection, execute **one batched repair package** covering every still-valid BSP/RSP finding, including selected-provider transport and code-level hard budget enforcement. Ordinary engineering choices inside the package do not require repeated Owner approval.
6. Run focused/adversarial regression for every finding, canonical full suite `python -m unittest discover -s tests -v`, and the finding-specific re-audit. Do not restart broad rolling review/fix cycles.
7. Update formal finding/state authority with CLOSED/PASS evidence.
8. Only after all five BSP blockers are CLOSED can a separate explicit Owner authorization enable bounded paid provider calls. Outcome access, PRIMARY semantic freeze, broker access and real money remain separately locked.

No provider/model is currently VERIFIED or ADOPTED.

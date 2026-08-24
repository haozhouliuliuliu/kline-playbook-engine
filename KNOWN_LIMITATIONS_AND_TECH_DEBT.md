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

## LIMIT-012 — Real-model Jianghe fidelity evaluation has not been run

```text
STATUS=ACTIVE
PRIORITY=HIGHEST_CURRENT_MODEL_SELECTION_BLOCKER
CURRENT_BLOCKER=YES_FOR_MODEL_ADOPTION_AND_PRIMARY_PROMOTION
REAL_MODEL_PROVIDER_LIVE_TRANSPORT=IMPLEMENTED_FOR_AUTHORIZED_TARGET_SET__NOT_LIVE_VERIFIED__NOT_ADOPTED
REAL_MODEL_FIDELITY_EVALUATION=AUTHORIZED__NOT_STARTED
FIDELITY_CORPUS=INTEGRATED_NON_OUTCOME__CURRENT_IDENTITY_METADATA_REBOUND
FIDELITY_EVALUATION_HARNESS=INTEGRATED_OFFLINE_PROVIDER_NEUTRAL__PRELIVE_EVIDENCE_REPAIRED
VISUAL_RENDERER=INTEGRATED_V0_1_DETERMINISTIC_PROVIDER_NEUTRAL__ADVERSARIAL_80_OF_80_PASS
OBSERVATION_REPLAY=INTEGRATED_SYNTHETIC_NON_OUTCOME__OBSERVATION_IDENTITY_BOUND
RUNTIME_NORMALIZER=INTEGRATED_V0_1_STRICT_VERSIONED_DETERMINISTIC
STAGE_A_INPUT_PROTOCOL=OWNER_APPROVED__FROZEN_FOR_STAGE_A
STAGE_A_STATUS=AUTHORIZED__INPUT_PROTOCOL_APPROVED__NOT_STARTED
LIVE_CALLS=0
PAID_SPEND_CNY=0
```

The current first real-model step is the bounded non-outcome Stage-A fidelity funnel. Provider/model choice is based on Jianghe fidelity, stability, UNKNOWN honesty and no-invention behavior — not candidate returns.

Current pre-execution checkpoint:

- `docs/reviews/JIANGHE_STAGE_A_PREEXECUTION_HANDOFF_2026-08-24.md`
- `docs/reviews/JIANGHE_STAGE_A_INPUT_AND_VISUAL_STIMULUS_PROTOCOL_OWNER_DECISION_V0_1.md`

Before the first paid Stage-A request, the project must finish the frozen input-track runtime generalization, generate/freeze the exact `JH-FIX-C-001` synthetic OHLC stimulus and machine-readable Stage-A plan, and pass focused/full-suite/diff-hygiene verification. Then it may check credential presence and existing balance/credits. New recharge/top-up remains separately Owner-gated by exact amount.

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

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

Project API/session denial and material binding were verified for the previously bound bundle, but this does not prove OS sandboxing, resistance to malicious local introspection, cryptographic tamper protection, or absence of latent model knowledge.

## LIMIT-012 — Real-model Jianghe fidelity evaluation has not been run

```text
STATUS=ACTIVE_NEXT_PHASE_AFTER_IDENTITY_REBIND
PRIORITY=HIGH
CURRENT_BLOCKER=YES_FOR_MODEL_ADOPTION_AND_PRIMARY_PROMOTION
REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
FIDELITY_CORPUS=INTEGRATED_NON_OUTCOME
OBSERVATION_REPLAY=INTEGRATED_SYNTHETIC_NON_OUTCOME
AUTHORITY=docs/reviews/JIANGHE_AI_FIDELITY_AND_REPLAY_INTEGRATION_REVIEW_V0_1.md
```

The model-selection step must use the integrated non-outcome Jianghe fidelity fixtures. Provider/model choice is based on Jianghe fidelity, stability, UNKNOWN honesty and no-invention behavior — not candidate returns. Current fixture metadata that references the pre-hygiene knowledge-pack identity must be rebound before it can serve as the current model-evaluation identity.

## LIMIT-013 — Jianghe active bundle identity must be rebound after authority hygiene

```text
STATUS=ACTIVE_BLOCKER
PRIORITY=HIGHEST_CURRENT
CURRENT_BLOCKER=YES_FOR_CURRENT_SOURCE_ONLY_ASSERTION_FINAL_PRIMARY_BRANCH_IDENTITIES_AND_REAL_MODEL_FIDELITY_IDENTITY
HISTORICAL_PRE_HYGIENE_KNOWLEDGE_PACK_IDENTITY=3f2ddbf9c007b3246661088986a35b84258bdc984ed5fa82dace59074495a9d5
HISTORICAL_PRE_HYGIENE_SOURCE_ONLY_VERIFICATION=PASS
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY=REBIND_REQUIRED
CURRENT_ACTIVE_SOURCE_ONLY_VERIFICATION=REVERIFY_REQUIRED
AUTHORITY=docs/reviews/JIANGHE_AUTHORITY_HYGIENE_IDENTITY_REBIND_REVIEW_V0_1.md
```

Authority-hygiene edits removed mutable SOURCE_ONLY/PRIMARY/current-authorization fields from Jianghe source-distillation documents. Jianghe source semantics did not change, but existing builders bind raw repository bytes, so the active knowledge-pack and SOURCE_ONLY bundle identities changed. Under the existing identity semantics, the deterministic builders and evidence must be regenerated and all active dependent identities synchronized before current SOURCE_ONLY=YES or final claim-level PRIMARY branch identities are asserted again.

This repair must not redesign identity semantics. A change to what the knowledge-pack identity means would be a separate research-governance decision.

## Current PRIMARY prerequisite

```text
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=NOT_COMPLETE
JIANGHE_PRIMARY_FINAL_BRANCH_IDENTITIES=BLOCKED_ON_LIMIT_013_REBIND
NEXT_GATE=REBIND_CURRENT_JIANGHE_IDENTITY_THEN_COMPLETE_352_CLAIM_LEVEL_SOURCE_JUSTIFIED_PRIMARY_MAPPING_PLUS_REAL_MODEL_FIDELITY_EVIDENCE_WITHOUT_OUTCOMES
```

Historical SOURCE_ONLY verification does not automatically create current active-bundle SOURCE_ONLY verification or PRIMARY eligibility.

## Maintenance rule

Keep only unresolved items that can still affect a future decision. Once an item is resolved or leaves the current route, remove it from this active index and preserve the accepted resolution in its evidence/review + Git history. Do not retain `RESOLVED` sections here as context ballast.

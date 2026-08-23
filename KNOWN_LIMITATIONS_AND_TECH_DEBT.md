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
PRIORITY=HIGH_FUTURE_AFTER_PRELIVE_GATE
CURRENT_BLOCKER=YES_FOR_MODEL_ADOPTION_AND_PRIMARY_PROMOTION
REAL_MODEL_PROVIDER_LIVE_TRANSPORT=NOT_IMPLEMENTED_NOT_VERIFIED_NOT_ADOPTED
REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
FIDELITY_CORPUS=INTEGRATED_NON_OUTCOME__CURRENT_IDENTITY_METADATA_REBOUND
FIDELITY_EVALUATION_HARNESS=INTEGRATED_OFFLINE_PROVIDER_NEUTRAL__PRELIVE_EVIDENCE_REPAIRED
VISUAL_RENDERER=INTEGRATED_V0_1_DETERMINISTIC_PROVIDER_NEUTRAL__ADVERSARIAL_80_OF_80_PASS
OBSERVATION_REPLAY=INTEGRATED_SYNTHETIC_NON_OUTCOME__OBSERVATION_IDENTITY_BOUND
PROVIDER_EVIDENCE_CONTRACT=INTEGRATED_CANDIDATE_LIVE_DISABLED
RUNTIME_NORMALIZER=INTEGRATED_V0_1_STRICT_VERSIONED_DETERMINISTIC
```

The model-selection step must use the integrated non-outcome Jianghe fidelity fixtures. Provider/model choice is based on Jianghe fidelity, stability, UNKNOWN honesty and no-invention behavior — not candidate returns. The offline evidence chain is integrated, but no real provider/model has been called or verified. A future live probe remains Owner-gated for credentials, data egress and paid spend.

## LIMIT-013 — Pre-live fidelity gate audit blocker (RESOLVED)

```text
STATUS=RESOLVED_BY_INTEGRATION_2026-08-23
CURRENT_BLOCKER=NO
PRE_LIVE_FIDELITY_GATE_REAUDIT=PASS
LIVE_MODEL_PROVIDER_PROBE=AWAITING_OWNER_BOUNDED_PROBE_APPROVAL
OUTCOME_ACCESS=NO
RESOLUTION=docs/reviews/JIANGHE_PRE_LIVE_FIDELITY_GATE_REAUDIT_V0_1.md
CLOSING_EVIDENCE=all 27 original findings (G-01..G-03, H-01..H-13, O-01..O-03, N-01..N-04, P-01..P-04) CLOSED with concrete code/artifact/test evidence; full suite 1195 tests 0 failures 0 errors; firewalls pass.
```

Pre-live audit blocker is closed only because Gate C passed in full. Real-model fidelity itself remains the later `LIMIT-012`.

## LIMIT-014 — PRIMARY curated review quality (RESOLVED)

```text
STATUS=RESOLVED_BY_V0_5_FIXED_RUBRIC_INDEPENDENT_REAUDIT_2026-08-23
CURRENT_BLOCKER=NO
AUDIT_STATUS=PASS
PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT=PASS
RESOLUTION=docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT_V0_1.md
CANDIDATE_COMMIT=08dc196e1a889c9d17070a767a24a41aab2f17d6
TOTAL_RECORDS=352
REGISTRY_DECLARED_READY_COUNT=340
REGISTRY_STOP_COUNT=12
PROJECT_BRAIN_ACCEPTED_READY_COUNT=340
Q01_SOL_REVIEW_READY_CONFLICT_COUNT=0_RESOLVED_BY_V0_5
Q02_TEMPLATE_EVIDENCE_PROBLEM=RESOLVED_BY_V0_5_FIXED_RUBRIC_REAUDIT
PRIMARY_FREEZE=NO
OUTCOME_ACCESS=NO
```

The V0.5 curated-quality repair (exact candidate commit above) passed the independent fixed R1–R8 re-audit (`AUDITOR_ROLE=INDEPENDENT_LOCAL_WORKBUDDY_READ_ONLY`). `PRIMARY_ELIGIBLE=NO` remains; this resolution does not create PRIMARY eligibility, freeze, outcome access, or model/provider adoption.

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

Current active-bundle SOURCE_ONLY verification is `YES`, and the V0.5 registry passed the independent fixed-rubric re-audit. Neither creates PRIMARY eligibility. Final PRIMARY semantic freeze remains an Owner decision after real-model fidelity evidence.

## Maintenance rule

Keep only unresolved items that can still affect a future decision. Once an item is resolved or leaves the current route, remove it from this active index and preserve the accepted resolution in its evidence/review + Git history. Do not retain `RESOLVED` sections here as context ballast.

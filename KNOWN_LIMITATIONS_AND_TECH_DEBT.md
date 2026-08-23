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

## LIMIT-013 — Pre-live fidelity gate audit remains NOT_READY

```text
STATUS=ACTIVE
PRIORITY=HIGHEST_CURRENT_GATE
CURRENT_BLOCKER=YES_FOR_LIVE_MODEL_PROVIDER_PROBE_AND_PRIMARY_PROMOTION
PRE_LIVE_FIDELITY_GATE_AUDIT=NOT_READY_REPAIR_REQUIRED
LIVE_MODEL_PROVIDER_PROBE=BLOCKED_PENDING_PRIMARY_CURATED_QUALITY_REPAIR
OUTCOME_ACCESS=NO
AUTHORITY=docs/reviews/JIANGHE_PRE_LIVE_FIDELITY_GATE_AUDIT_V0_1.md
```

The original engineering evidence-chain findings have been repaired and integrated: evaluator evidence completeness, deterministic/adversarially repaired visual rendering, observation/replay identity binding, AI research-object identity, strict runtime normalizer, provider evidence contract and candidate prompt package are all on the current main lineage. LIMIT-013 remains active because the gate must not flip to PASS until LIMIT-014 is repaired and the same full gate audit is independently re-run.

## LIMIT-014 — PRIMARY curated review quality is not accepted

```text
STATUS=ACTIVE
PRIORITY=HIGHEST_CURRENT
CURRENT_BLOCKER=YES_FOR_PRELIVE_GATE_AND_PRIMARY_FREEZE_READINESS
AUDIT_STATUS=FAIL_CLOSED_MATERIAL_FINDINGS
AUTHORITY=docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_AUDIT_V0_1.md
TOTAL_RECORDS=352
REGISTRY_DECLARED_READY_COUNT=340
REGISTRY_STOP_COUNT=12
PROJECT_BRAIN_ACCEPTED_READY_COUNT=NOT_ESTABLISHED_PENDING_CURATED_QUALITY_REPAIR
Q01_SOL_REVIEW_READY_CONFLICT_COUNT=5
Q02_TEMPLATE_EVIDENCE_PROBLEM=CONFIRMED
PRIMARY_FREEZE=NO
OUTCOME_ACCESS=NO
```

The current identity-bound registry is mechanically complete and deterministic, but its semantic-review evidence is not sufficient for freeze readiness. Five records simultaneously declare `SOL_REVIEW_REQUIRED` and `READY_FOR_PRIMARY_FREEZE`. More broadly, the existing review artifact can be generated from templated rationale/interpolation patterns and therefore does not establish that 352 substantive claim-specific reviews occurred. This does **not** prove all 340 READY semantics are wrong; it means the project may not treat them as accepted freeze-ready semantics without a real per-claim re-review. The repair may change READY/STOP counts; no target count is to be preserved.

## Current PRIMARY prerequisite

```text
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=INTEGRATED_PRE_FREEZE_IDENTITY_BOUND__CURATED_QUALITY_REPAIR_REQUIRED
JIANGHE_PRIMARY_REGISTRY_DECLARED_READY_COUNT=340
JIANGHE_PRIMARY_REGISTRY_STOP_COUNT=12
JIANGHE_PRIMARY_PROJECT_BRAIN_ACCEPTED_READY_COUNT=NOT_ESTABLISHED_PENDING_CURATED_QUALITY_REPAIR
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
NEXT_GATE=CURATED_QUALITY_REPAIR_THEN_PRELIVE_GATE_REAUDIT
```

Current active-bundle SOURCE_ONLY verification is `YES`, but neither source verification nor a mechanically complete registry creates PRIMARY eligibility. The next accepted artifact must be built from substantive claim-specific review and independently re-audited.

## Maintenance rule

Keep only unresolved items that can still affect a future decision. Once an item is resolved or leaves the current route, remove it from this active index and preserve the accepted resolution in its evidence/review + Git history. Do not retain `RESOLVED` sections here as context ballast.

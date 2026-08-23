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
PRIORITY=HIGHEST_CURRENT
CURRENT_BLOCKER=YES_FOR_MODEL_ADOPTION_AND_PRIMARY_PROMOTION
REAL_MODEL_PROVIDER=NOT_IMPLEMENTED
REAL_MODEL_FIDELITY_EVALUATION=NOT_STARTED
FIDELITY_CORPUS=INTEGRATED_NON_OUTCOME__CURRENT_IDENTITY_METADATA_REBOUND
FIDELITY_EVALUATION_HARNESS=INTEGRATED_OFFLINE_PROVIDER_NEUTRAL
VISUAL_RENDERER=IN_PREPARATION_NOT_INTEGRATED
OBSERVATION_REPLAY=INTEGRATED_SYNTHETIC_NON_OUTCOME
AUTHORITY=docs/reviews/JIANGHE_AI_FIDELITY_AND_REPLAY_INTEGRATION_REVIEW_V0_1.md
```

The model-selection step must use the integrated non-outcome Jianghe fidelity fixtures. Provider/model choice is based on Jianghe fidelity, stability, UNKNOWN honesty and no-invention behavior — not candidate returns. The offline evaluation harness is integrated; real-model evaluation remains blocked on governed visual input plus provider/model invocation capability and an Owner-authorized live probe.

## LIMIT-013 — Pre-live fidelity gate audit is NOT_READY (evidence-chain gaps)

```text
STATUS=ACTIVE
PRIORITY=HIGHEST_CURRENT
CURRENT_BLOCKER=YES_FOR_LIVE_MODEL_PROVIDER_PROBE_AND_PRIMARY_PROMOTION
PRE_LIVE_FIDELITY_GATE_AUDIT=NOT_READY_REPAIR_REQUIRED
LIVE_MODEL_PROVIDER_PROBE=BLOCKED_PENDING_AUDIT_REPAIR
OUTCOME_ACCESS=NO
AUTHORITY=docs/reviews/JIANGHE_PRE_LIVE_FIDELITY_GATE_AUDIT_V0_1.md
```

Live probe 前发现证据链缺口（GLOBAL G-01..G-03、FIDELITY H-01..H-08、
PROVIDER H-09..H-13、OBSERVATION O-01..O-03、NORMALIZER/PROMPT N-01..N-04、
PROCESS P-01..P-04）。修复目标：fidelity evaluator evidence completeness
（outcome contamination fail-closed、strict schema、corpus binding、
failed-call non-scoreable、strict types、typed provenance、metadata allowlist+scan、
deterministic report_identity、三态分离）、visual renderer 按文件/hash 独立搬运与
review、real-model firewall tests。全部离线且 fail-closed，不访问任何 protected
artifact，不做任何真实模型调用。

## Current PRIMARY prerequisite

```text
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_CLAIM_LEVEL_MAPPING=COMPLETE_PRE_FREEZE_IDENTITY_BOUND
JIANGHE_PRIMARY_READY_FOR_FREEZE_COUNT=340
JIANGHE_PRIMARY_STOP_COUNT=12
JIANGHE_PRIMARY_BRANCH_IDENTITIES_DETERMINISTIC=YES
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
NEXT_GATE=REAL_MODEL_FIDELITY_EVIDENCE_THEN_OWNER_PRIMARY_FREEZE_DECISION
```

Current active-bundle SOURCE_ONLY verification is `YES`, and the claim-level pre-freeze registry is complete. Neither fact alone creates PRIMARY eligibility. The 12 STOP records remain explicit fail-closed results rather than missing work.

## Maintenance rule

Keep only unresolved items that can still affect a future decision. Once an item is resolved or leaves the current route, remove it from this active index and preserve the accepted resolution in its evidence/review + Git history. Do not retain `RESOLVED` sections here as context ballast.

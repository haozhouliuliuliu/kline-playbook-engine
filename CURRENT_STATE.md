# CURRENT_STATE

## Project phase

```text
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE_BASELINE=Skeleton_v1.0
ARCHITECTURE_STATUS=ACCEPTED
ADOPTED_CONTRACT_VERSION=3.1
ADOPTED_CONTRACT_SHA256=3b5ceaaa3696375b941fd2aaba95615cf9352dcada3696b60137650bf690101e
CURRENT_BLOCKER=NONE
CURRENT_WORK_PACKAGE=COMMON_STATISTICAL_PROFILE_V1_REVISION_AFTER_PARALLEL_REVIEW
CURRENT_WORK_PACKAGE_STATUS=REVISION_IN_PROGRESS_AFTER_TAKEOVER_ACCEPTANCE
CURRENT_WORK_PACKAGE_AUTHORITY=docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md
CURRENT_WORK_PACKAGE_ADJUDICATION=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md
CONVERSATION_HANDOFF_STATUS=TAKEOVER_ACCEPTED
FRESH_CONVERSATION_FIRST_TURN=READ_ONLY_TAKEOVER_VERIFICATION_COMPLETE
FRESH_CONVERSATION_TAKEOVER_ACCEPTANCE=APPROVED
TAKEOVER_ACCEPTED_DATE=2026-08-19
PROJECT_EXECUTION_DURING_TAKEOVER_CHECK=RELEASED
THIRD_PASS_HANDOFF_REVIEW=docs/reviews/HANDOFF_THIRD_PASS_FAILURE_MODE_REVIEW_2026-08-19.md
OWNER_ACTION=NONE
```

The Owner accepted the fresh-conversation takeover report on 2026-08-19. The temporary read-only takeover pause is released. Normal project execution resumes under the existing authority and authorization boundaries; the takeover approval changes no research semantics and unlocks no dataset cohort.

## Binding research direction

```text
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
RESEARCH_DIRECTION_STATUS=OWNER_APPROVED
RESEARCH_DIRECTION_AUTHORITY=RESEARCH_DIRECTION.md
RESEARCH_ROUTE_ANTI_REGRESSION=HUMAN_PLAYBOOK_FIRST_NO_DATA_FIRST_KLINE_MINING
PROHIBITED_DEFAULT_RESEARCH_ROUTE=UNCONSTRAINED_KLINE_INDICATOR_PATTERN_PARAMETER_MINING
```

Binding route:

```text
traceable human trading experience
-> AI-assisted source-faithful extraction and structuring
-> versioned Playbook Contract
-> deterministic/versioned machine operationalization
-> governed historical validation of applicability and failure conditions
-> strict validation / protected-holdout governance
-> accepted or rejected playbook
```

Skeleton v1.0 remains accepted. `RESEARCH_DIRECTION.md` specializes its broad Research Loop wording: generic language that AI may find candidate ideas does not authorize data-first K-line/chart-pattern/indicator/rule/parameter mining. Any future move back toward that route is an Owner-gated research-direction change.

Live boundary remains:

```text
LIVE_AI_SCENE_RECOGNITION_MODE=UNDECIDED
LIVE_DISCRETIONARY_LLM_CRITICAL_PATH=NOT_AUTHORIZED
OWNER_GATE_REQUIRED_FOR_LIVE_AI_SEMANTICS=YES
```

## Research Protocol v1.0 — FROZEN / BINDING

Authorities:
- Owner approval: `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
- Binding protocol: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- Binding chronology: `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- Binding Selection Firewall requirements: `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- Active claim schema: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`

```text
RESEARCH_PROTOCOL_VERSION=1.0
RESEARCH_PROTOCOL_STATUS=FROZEN_BINDING
RESEARCH_PROTOCOL_FREEZE_EXECUTION_STATUS=COMPLETE
CHRONOLOGICAL_SPLIT_STATUS=FROZEN_12_6_6
OWNER_FREEZE_DECISION=APPROVED
PERFORMANCE_RESEARCH_STARTED=NO
REAL_CLAIM_EXTRACTION_STARTED=NO
REAL_CLAIM_EXTRACTION_ENVIRONMENT=VERIFIED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
```

Frozen chronology:

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
```

`PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT != PROSPECTIVE_GENUINELY_UNSEEN_DATA`.
The 12/6/6 split is a governance/audit choice, not a promise of statistical power. `INSUFFICIENT_EVIDENCE` remains a frozen legitimate result. Material changes to frozen research semantics or chronology require a new protocol version, material independent adversarial review, and the normal Owner gate.

Frozen safeguards include:
- `SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION`;
- `EXPLICIT / INFERRED / UNKNOWN`;
- exactly one source-justified PRIMARY branch before candidate outcome testing;
- ambiguity stops instead of outcome-guided interpretation mining;
- lineage/mechanism/exposure inheritance survives renaming;
- SOURCE_ONLY interpretation with technical denial of protected-period project market-outcome retrieval;
- immutable Research Wave tested denominator and whole-wave multiplicity accounting;
- common statistical profile locked before first candidate outcome-bearing performance backtest;
- dependence-aware evidence sufficiency;
- CAT1/CAT2/CAT3 validation revision rules;
- irreversible historical-final exposure;
- future Shadow/Forward as the stronger prospective unseen path under later authority.

## Pre-outcome research firewall — ACCEPTED

Implementation evidence: `docs/evidence/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0.md`

Final acceptance: `docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_FINAL_ACCEPTANCE_V1_2.md`

```text
PREOUTCOME_FIREWALL_IMPLEMENTATION=COMPLETE_VERIFIED_ACCEPTED
IDENTITY_BINDING=VERIFIED
PRIMARY_SCOPE_SEARCH_CROSS_BINDING=VERIFIED
SOURCE_ONLY_POLICY=VERIFIED
SOURCE_ONLY_CLAIM_EXTRACTION_RUNNER=VERIFIED
REAL_CLAIM_EXTRACTION_ENVIRONMENT=VERIFIED
RESEARCH_WAVE_IDENTITY_BINDING=VERIFIED
STATISTICAL_PROFILE_INTERFACE=VERIFIED
PRE_OUTCOME_GATE_STATUS=VERIFIED_FAIL_CLOSED
HISTORICAL_FINAL_HOLDOUT_LOCK=ENFORCED
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
FIREWALL_TESTS=54
FULL_TESTS=235_OK
FULL_TESTS_SKIPPED=3
```

`src/research_firewall.py` is the single owner of the new pre-outcome access rules. Candidate access is identity-bound to the exact hypothesis/wave/profile/SOURCE_ONLY/PRIMARY/scope/search registration; callers cannot self-assert lock booleans. SOURCE_ONLY is a project-owned application control, not a cryptographic sandbox; model latent historical knowledge remains a disclosed residual risk.

## Common Statistical Profile v1 — current bottleneck

Protocol v1.0 requires one project-wide common statistical profile to be independently reviewed and locked before the first real candidate outcome-bearing performance backtest.

First candidate:

```text
COMMON_STATISTICAL_PROFILE_V1_STATUS=CANDIDATE_REVISION_REQUIRED_NOT_LOCKED
STATISTICAL_PROFILE_DESIGN_COMMIT=6ef668fd7214fcef2f12b71cb3e9ea2a36bfcaf7
STATISTICAL_PROFILE_DESIGN_DOC=docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

Integrated evidence:
- engine capability audit: `docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md`;
- engine compatibility crosswalk: `docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ENGINE_COMPATIBILITY_CROSSWALK.md`;
- independent adversarial review: `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADVERSARIAL_REVIEW.md`, verdict `GO_WITH_REQUIRED_CHANGES`, 3 CRITICAL / 6 HIGH;
- project-brain adjudication: `docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`.

Adjudicated state:

```text
PROFILE_V1_CANDIDATE_DIRECTION=KEEP
CURRENT_CANDIDATE_LOCKABLE=NO
FROZEN_PROTOCOL_CONFLICT=NO
OWNER_GATE_REQUIRED_NOW=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
```

Binding revision requirements from adjudication:
1. separate economic materiality from statistical detectability/power interpretation;
2. remove `ESS=N/max(1,2H-1)` as a deterministic hard sufficiency gate;
3. pin one engine `position_id` = one completed round-trip observation; aggregate adds and partial closes; forced liquidation terminal; concrete-contract roll creates separate round trips;
4. explicitly define holding-horizon and multi-week dependence treatment;
5. justify or simplify fixed sufficiency thresholds rather than treating candidate heuristics as accepted facts;
6. distinguish additive fee stress from slippage/friction stress;
7. add a simple predeclared guard against one event/narrow time window carrying the apparent edge;
8. add explicit `DATA_BLOCKED` or equivalent distinct from `FAIL` and `INSUFFICIENT_EVIDENCE`;
9. make statistical multiplicity counting machine-consistent with frozen Research Wave/search identities;
10. correct the Romano-Wolf description; Holm remains a leading simple candidate, not locked.

Reviewer replacement numbers/methods are advisory only. In particular, `N>=60`, exact day/week minima, a `2x` cost gate, Holm as final method, the review block-length formula, illustrative volatility/sigma values, and any exact ESS replacement are not accepted/frozen project facts.

## Canonical BALANCED historical corpus — ACCEPTED

```text
CANONICAL_DATASET_BUILT=YES
CANONICAL_DATASET_ACCEPTED=YES
CANONICAL_PRODUCTS=cu,al,ni,au,ag,rb
CANONICAL_COVERAGE=2024-01-01..2025-12-31
CANONICAL_GRANULARITY=1-minute
CONCRETE_CONTRACTS=212
PLAN_PARTITIONS=32980
ACQUIRED_PARTITIONS=32980
NORMALIZED_PARTITIONS=32980
NORMALIZED_ROWS=15280452
PARQUET_FILES=32980
CANONICAL_CORPUS_IDENTITY=1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8
CROSS_SOURCE_SUMMARY_IDENTITY=cee702ea6cd79e62ec49bf7f1f632f70e5b0a7a577ba455e09597cce9d16d4ae
CROSS_SOURCE_RESULT=32841_MATCH/0_MISMATCH/0_NOT_COMPARABLE/139_NOT_AVAILABLE
```

Authorities:
- `docs/evidence/SOURCE_AND_SCOPE_OWNER_APPROVAL.md`
- `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`
- `docs/evidence/CANONICAL_CORPUS_IDENTITY.json`
- `docs/evidence/CANONICAL_FULL_CROSS_SOURCE.json`

Corpus construction itself created no project-recorded strategy-family development/validation/historical-final exposure.

## Human Playbook source layer

```text
FIRST_WAVE_SOURCE_LAYER_RESULT=GO
PROJECT_LED_DISCOVERY=PRIMARY
OWNER_SUPPLIED_MATERIAL=SUPPLEMENTAL
```

Completed source dossiers cover Peter Brandt, Al Brooks, Linda Raschke, Adam Grimes, Brett Steenbarger, Steidlmayer -> Dalton Market Profile lineage, and skeptical/counter-evidence methods including White, Sullivan/Timmermann/White, and Bailey et al.

China-first current state:
- 青泽: identity/bibliography verified; no full dossier without authorized text/sample;
- 期货日报实盘大赛: `DISCOVERY_ONLY`;
- 付爱民、王少多、张亚楠: discovery leads only; provenance pinning incomplete.

## Current authorization boundaries

AUTHORIZED NOW:
- source discovery/provenance;
- controlled real source-faithful claim extraction inside the verified SOURCE_ONLY environment under Claim Schema v1.0;
- deterministic non-outcome operationalization/tests;
- revision/review/implementation work for `COMMON_STATISTICAL_PROFILE_V1` without candidate outcome inspection;
- non-candidate/dummy engine-sanity tests;
- safe isolated parallel engineering/review work under the Owner collaboration contract and `AGENTS.md`.

NOT AUTHORIZED:
- data-first automatic K-line/chart-pattern/indicator/rule/parameter strategy mining as the project's research route;
- candidate PnL/equity/expectancy/Sharpe/win-loss or equivalent candidate-quality inspection until the revised profile is independently reviewed, locked, identity-bound into a real Research Wave, and the pre-outcome gate passes;
- Validation access before frozen prerequisites;
- historical final-holdout unlock;
- changing frozen 12/6/6 or frozen research semantics without new protocol/Owner gate;
- unconstrained strategy/indicator/rule/parameter mining;
- Shadow automated trading;
- real-money trading or broker orders;
- discretionary LLM live critical path;
- new paid commitments;
- permanent RiskGate semantics without Owner approval;
- large multi-agent orchestration / knowledge graph / microservices expansion;
- importing strategy conclusions/results/parameters from other projects;
- bypassing paywalls/DRM/platform permissions;
- authenticated browser-cookie acquisition without separate review;
- redistribution of copyrighted raw source material.

## Tools / execution workflow

```text
TOOL_DECISION=USE_EXISTING
TOOL_DECISION_SCOPE=COMMON_STATISTICAL_PROFILE_V1_REVISION_AFTER_PARALLEL_REVIEW
PAID_CHAT_RELAY_ORCHESTRATOR=NOT_ADOPTED_CURRENTLY
BRITTLE_VSCODE_UI_CHAT_AUTOMATION=NOT_ADOPTED_CURRENTLY
CURRENT_DS_RELAY_MODE=OWNER_MANUAL_RELAY_WHEN_LOCAL_AGENT_IS_NEEDED
```

No new tool gap is demonstrated. Project-level capability lifecycle (`CANDIDATE / VERIFIED / ADOPTED`) is distinct from the cross-project Tool Registry catalog taxonomy (`CANDIDATE / APPROVED / DEFERRED / REJECTED / RETIRED`). Repository/CURRENT_STATE/runtime facts decide what this project actually uses.

Project-local adopted capabilities remain:
- TqSdk 3.10.1 — historical concrete-contract 1-minute research data only;
- PyArrow/Parquet 25.0.1 — normalized canonical storage;
- SQLite — rebuildable canonical catalog/index;
- Raw JSON + SHA256 provenance — authoritative raw evidence mechanism.

DeepSeek V4 Flash is a currently available Owner-side local worker capability, not a project-adopted runtime dependency. GPT should do safe repo-only documentation/state/research integration directly when connected tools suffice; local workers are for code/tests/runtime or genuinely useful independent review.

## Known limitations / technical debt

Authority: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`.

- `TD-001`: duplicate session/trading-day responsibility. New trusted day/week statistics must use `SessionMetadata`; do not consume the bootstrap calendar as business authority.
- `TD-002`: partial-close snapshot temporarily clears unrealized PnL. It corrupts partial-close equity/unrealized/drawdown path snapshots, not final realized round-trip totals.
- `LIMIT-001`: governed historical price-limit facts are incomplete. Affected real confirmatory PnL generation fails closed; this is a data/governance blocker, not silent fill corruption.
- `DECISION-001`: live AI scene-recognition implementation remains unresolved and Owner-gated.

Engine capability facts relevant to the current profile work:
- realized PnL, costs, instrument/contract identity, timestamps/trading-day identity, and deterministic `position_id` lifecycle are available and tested;
- round-trip ledger, holding duration, day/week aggregation, and hypothesis/wave execution joins are small engineering deltas;
- multi-day portfolio/equity series is a medium delta;
- LIMIT-001 must be resolved before affected real confirmatory execution claims price-limit realism.

## Parallel-work operating state

- isolated worktrees/branches for independent workers;
- one integration lane owns `main` and shared authority/state;
- parallel workers do not push `main` or independently edit shared authority unless assigned;
- normally use 2–3 high-value lanes;
- do not parallelize work whose meaning depends on an unresolved upstream semantic decision;
- inspect `git worktree list`, target branch, and remote state before creating/reusing a local worktree.

The prior statistical engine-audit and independent-review outputs are integrated to `main`. Their remote branches may still exist. Owner-machine worktree presence is unknown until inspected locally.

## Verification status

Last canonical code-bearing verification reported by the statistical lanes:

```text
python -m unittest discover -s tests -v
235 tests OK
3 skipped
exit 0
```

Later changes through the accepted takeover were documentation/state/review-integration or repository-identity changes only; no production/test code changed. Therefore `235 OK / 3 skipped` remains the latest code-bearing verification baseline. It is not a claim that the latest documentation-only HEAD was rerun locally.

## Current next action

```text
CURRENT_NEXT_ACTION=REVISE_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE_FROM_ADJUDICATED_REVIEW
CURRENT_NEXT_ACTION_AUTHORITY=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md
PROFILE_STATUS=CANDIDATE_REVISION_REQUIRED_NOT_LOCKED
TOOL_DECISION=USE_EXISTING
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
REAL_CLAIM_EXTRACTION_ENVIRONMENT=VERIFIED
OWNER_ACTION=NONE
```

The takeover gate is complete, so this package is now in progress. Revise the Common Statistical Profile candidate and its design evidence coherently without candidate outcomes, then obtain a targeted independent delta review only over materially changed statistical definitions. Do not repeat the entire project review. Full statistical evaluator/round-trip-ledger implementation follows profile acceptance, except for independently useful non-semantic helpers that cannot bias the design decision.

## Progress estimates — engineering estimates, not evidence facts

| Stage / domain | Status | Estimate |
| --- | --- | ---: |
| Architecture / Bootstrap | Skeleton v1.0 accepted | 100% |
| Data Substrate | canonical corpus accepted; execution metadata debt remains | ~90% |
| Strategy Catalog | Playbook/identity foundations present; real extracted playbooks not yet built | ~58% |
| Backtest & Validation | engine + firewall substantial; statistical profile/evaluator incomplete | ~64% |
| Human Playbook Research Loop | protocol/source/firewall ready; real claim extraction not started | ~43% |
| Trading Loop | early deterministic foundations only | ~15% |
| Ledger / Observability | foundational evidence/ledger pieces only | ~25% |
| Overall project | research-foundation stage | ~45% |

Percentages are conservative engineering estimates, not evidence facts and not derived from test counts.

## Owner decision gates

Owner approval remains required for:
- future changes to frozen research semantics or chronology;
- historical final-holdout unlock;
- new paid commitments;
- irreversible external actions;
- authenticated acquisition with material new data-flow risk;
- permanent risk rules;
- real-money/broker actions;
- live critical-path changes.

No new research/product semantic Owner action is currently required.

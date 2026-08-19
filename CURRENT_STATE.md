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
CURRENT_WORK_PACKAGE_STATUS=ADJUDICATION_COMPLETE_REVISION_REQUIRED
CURRENT_WORK_PACKAGE_AUTHORITY=docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md
CURRENT_WORK_PACKAGE_ADJUDICATION=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md
CONVERSATION_HANDOFF_STATUS=THIRD_PASS_READY_AWAITING_OWNER_ACCEPTANCE
FRESH_CONVERSATION_FIRST_TURN=READ_ONLY_TAKEOVER_VERIFICATION
PROJECT_EXECUTION_DURING_TAKEOVER_CHECK=PROHIBITED
THIRD_PASS_HANDOFF_REVIEW=docs/reviews/HANDOFF_THIRD_PASS_FAILURE_MODE_REVIEW_2026-08-19.md
OWNER_ACTION=NONE
```

`OWNER_ACTION=NONE` means no new research/product semantic decision is currently required. Separately, the fresh-conversation handoff is intentionally waiting for the Owner to verify the new conversation's takeover report before normal execution resumes.

## Binding research direction

```text
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
RESEARCH_DIRECTION_STATUS=OWNER_APPROVED
RESEARCH_DIRECTION_AUTHORITY=RESEARCH_DIRECTION.md
RESEARCH_ROUTE_ANTI_REGRESSION=HUMAN_PLAYBOOK_FIRST_NO_DATA_FIRST_KLINE_MINING
PROHIBITED_DEFAULT_RESEARCH_ROUTE=UNCONSTRAINED_KLINE_INDICATOR_PATTERN_PARAMETER_MINING
```

Primary route:

```text
traceable human trading experience
-> AI-assisted extraction and structuring
-> versioned Playbook Contract
-> point-in-time market-scene representation / recognition
-> historical validation of applicability and failure conditions
-> strict validation / protected-holdout governance
-> accepted or rejected playbook
```

Human sources create hypotheses, not accepted truth. Skeleton v1.0 remains binding, but its broad Research Loop language is specialized by the later Owner-approved Human Playbook First direction. Generic architecture wording such as "AI may find candidate ideas" does **not** authorize automatic data-first K-line/chart-pattern/indicator mining.

Live boundary remains:

```text
LIVE_AI_SCENE_RECOGNITION_MODE=UNDECIDED
LIVE_DISCRETIONARY_LLM_CRITICAL_PATH=NOT_AUTHORIZED
OWNER_GATE_REQUIRED_FOR_LIVE_AI_SEMANTICS=YES
```

## Research Protocol v1.0 — FROZEN / BINDING

Owner decision on 2026-08-19: `按 v0.3 推荐冻结`.

Authorities:
- Owner approval: `docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`
- Binding protocol: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
- Binding chronology: `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`
- Binding Selection Firewall requirements: `docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`
- Active claim schema: `docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`

State:

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
```

Frozen chronology:

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
PROSPECTIVE_GENUINELY_UNSEEN: future Shadow/Forward cohorts, NOT_AUTHORIZED
```

The 12/6/6 split is a governance/audit choice, not a promise of statistical power. `INSUFFICIENT_EVIDENCE` is a frozen legitimate result. Historical holdout is project-governed historical evidence, not proof that humans/models had zero prior knowledge. Material changes to frozen semantics or chronology require a new protocol version, independent adversarial review, and the normal Owner gate.

## Frozen protocol safeguards — compact index

Protocol v1.0 freezes at least:
- `SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION`;
- `EXPLICIT / INFERRED / UNKNOWN`;
- exactly one source-justified PRIMARY branch before candidate outcome testing;
- ambiguity stops instead of mining alternatives;
- lineage/mechanism/exposure inheritance survives renaming;
- effective-content-date source-example exposure;
- observability/surrogate pre-justification;
- negative/near-miss/no-trade/counterexample preservation;
- immutable RESEARCH_WAVE denominator and whole-wave multiplicity accounting;
- SOURCE_ONLY interpretation with technical denial of protected-period market outcome retrieval;
- human/AI latent historical knowledge as disclosed residual threat-model risk;
- common statistical profile locked before first candidate outcome-bearing performance backtest;
- dependence-aware evidence sufficiency;
- `INSUFFICIENT_EVIDENCE` as legitimate result;
- CAT1/CAT2/CAT3 validation revision rules;
- irreversible historical-final exposure;
- future Shadow/Forward as the stronger prospective unseen path under later authority.

## Pre-outcome research firewall — ACCEPTED

Implementation evidence:
`docs/evidence/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_IMPLEMENTATION_V1_0.md`

Acceptance:
`docs/reviews/HUMAN_PLAYBOOK_PREOUTCOME_FIREWALL_FINAL_ACCEPTANCE_V1_2.md`

Accepted implementation state:

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

Important boundary:
- SOURCE_ONLY is a project-owned application control, not a cryptographic sandbox;
- model latent historical knowledge remains a disclosed residual risk;
- in-memory registry objects are execution machinery, not the sole durable authority; real research locks/exposures must also be materialized in project evidence/state artifacts.

## Common Statistical Profile v1 — current state

Protocol v1.0 requires a project-wide common statistical profile before the first real candidate outcome-bearing performance backtest.

### Candidate design

```text
COMMON_STATISTICAL_PROFILE_V1_STATUS=CANDIDATE_REVISION_REQUIRED_NOT_LOCKED
STATISTICAL_PROFILE_DESIGN_COMMIT=6ef668fd7214fcef2f12b71cb3e9ea2a36bfcaf7
STATISTICAL_PROFILE_DESIGN_DOC=docs/research/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_CANDIDATE.md
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

The first candidate proposed a completed-round-trip net-return estimand, dependence-aware resampling, project-wide sufficiency rules, Holm whole-wave FWER control, risk/failure checks, and deterministic decision rules. It is **not accepted or locked**.

### Engine capability audit — integrated

```text
STATISTICAL_ENGINE_CAPABILITY_AUDIT=COMPLETE
ORIGINAL_PARALLEL_AUDIT_COMMIT=c34cebde4307eb2d532886ed8da94e2985323ede
MAIN_CHERRYPICK_COMMIT=4946b0db2692a06ff6965efedb242156ab52e886
AUDIT_DOC=docs/evidence/HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1.md
```

Accepted engine facts:
- realized PnL, costs, contract/instrument identity, timestamps/trading-day identity, and deterministic position lifecycle are available and tested;
- round-trip ledger/open-close materialization is missing but is a small delta;
- day/week/instrument-day aggregations are small deltas;
- multi-day portfolio/equity series is a medium delta;
- execution records require a join to hypothesis/wave identities;
- TD-002 corrupts partial-close equity/unrealized/drawdown path snapshots but not final realized round-trip totals;
- TD-001 requires future day/week statistics to use `SessionMetadata`, not the bootstrap calendar;
- LIMIT-001 is a fail-closed data/governance blocker for affected real confirmatory PnL, not a silent fill error.

### Engine-compatibility crosswalk — COMPLETE / advisory evidence / integrated to main

```text
CROSSWALK_ORIGINAL_BRANCH=parallel/stat-engine-audit
CROSSWALK_ORIGINAL_COMMIT=05ad7f9a94c1a6b885402a4417a0d095dbfa7c56
CROSSWALK_MAIN_INTEGRATION_COMMIT=4b2c882331f855c730d125517e6b7fd563025055
CROSSWALK_DOC=docs/evidence/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ENGINE_COMPATIBILITY_CROSSWALK.md
CROSSWALK_VERDICT=BROADLY_COMPATIBLE_WITH_SMALL_DELTAS_AND_DESIGN_AMBIGUITIES
```

The worker itself did not push `main`; after project-brain adjudication, the integration lane merged the read-only evidence to `main`. It found no frozen-protocol conflict, but identified unresolved round-trip counting, holding-horizon, open-ratio, cost-stress, and multiplicity-counting definitions.

### Independent adversarial statistical review — COMPLETE / advisory evidence / integrated to main

```text
ADVERSARIAL_REVIEW_ORIGINAL_BRANCH=parallel/stat-profile-review
ADVERSARIAL_REVIEW_ORIGINAL_COMMIT=5e78605d312ee2e6c22e82dc4d91d651eacac4b2
ADVERSARIAL_REVIEW_MAIN_INTEGRATION_COMMIT=4650e5fe24e4ac50377a2e7440b81921c57c0a87
ADVERSARIAL_REVIEW_DOC=docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADVERSARIAL_REVIEW.md
REVIEW_VERDICT=GO_WITH_REQUIRED_CHANGES
CRITICAL_COUNT=3
HIGH_COUNT=6
```

The reviewer itself did not push `main`, did not read the parallel crosswalk, did not inspect candidate outcomes, and did not alter frozen authority. After adjudication, the integration lane merged the review document to `main` as durable evidence.

Main CRITICAL findings accepted by project-brain adjudication:
1. current candidate lacks a defensible power/detectability interpretation and risks false precision;
2. `ESS=N/max(1,2H-1)` must not remain a deterministic hard sufficiency gate;
3. round-trip/partial-close/add/forced-liquidation/holding/block semantics are incomplete and must be pinned before lock.

### Project-brain adjudication — COMPLETE

Authority:
`docs/reviews/HUMAN_PLAYBOOK_COMMON_STATISTICAL_PROFILE_V1_ADJUDICATION_V0_1.md`

```text
PROFILE_V1_CANDIDATE_DIRECTION=KEEP
CURRENT_CANDIDATE_LOCKABLE=NO
FROZEN_PROTOCOL_CONFLICT=NO
OWNER_GATE_REQUIRED_NOW=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
```

Accepted revision requirements include:
- separate economic materiality from statistical detectability;
- remove the current `2H-1` ESS hard gate;
- pin one `position_id` = one round-trip observation; aggregate adds/partial closes; forced liquidation terminal; concrete-contract roll creates separate round trips;
- explicitly pin holding-horizon and multi-week dependence treatment;
- justify/simplify fixed sufficiency thresholds rather than treating them as accepted facts;
- distinguish additive fee stress from slippage/friction stress;
- add a simple guard against one event/narrow time window carrying the edge;
- add explicit `DATA_BLOCKED` (or equivalent) distinct from FAIL and INSUFFICIENT_EVIDENCE;
- make statistical multiplicity counting machine-consistent with frozen Research Wave/search identities;
- correct the Romano-Wolf description; Holm remains a leading simple candidate, not locked.

Reviewer replacement methods/numbers are advisory evidence, not accepted project semantics. In particular, do not treat `N>=60`, exact day/week minima, a `2x` cost gate, Holm as final method, the review block-length formula, illustrative volatility/sigma values, or any exact ESS replacement as frozen/accepted facts.

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

The corpus itself created no project-recorded strategy-family development/validation/historical-final exposure.

## Human Playbook source layer

```text
FIRST_WAVE_SOURCE_LAYER_RESULT=GO
PROJECT_LED_DISCOVERY=PRIMARY
OWNER_SUPPLIED_MATERIAL=SUPPLEMENTAL
```

Completed source dossiers cover:
- Peter Brandt;
- Al Brooks;
- Linda Raschke;
- Adam Grimes;
- Brett Steenbarger;
- Steidlmayer -> Dalton Market Profile lineage;
- skeptical/counter-evidence methods: White, Sullivan/Timmermann/White, Bailey et al.

China-first current state:
- 青泽: identity/bibliography verified; no full dossier without authorized text/sample;
- 期货日报实盘大赛: `DISCOVERY_ONLY`;
- 付爱民、王少多、张亚楠: discovery leads only; provenance pinning incomplete.

Authorities:
- `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`
- `docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md`
- `docs/research/HUMAN_PLAYBOOK_SOURCE_LAYER_FIRST_WAVE_CLOSEOUT.md`
- `docs/research/CHINA_FIRST_SOURCE_DISCOVERY_WAVE_1.md`

## Current authorization boundaries

AUTHORIZED NOW:
- source discovery/provenance;
- controlled real source-faithful claim extraction inside the verified SOURCE_ONLY environment under Claim Schema v1.0;
- deterministic non-outcome operationalization/tests;
- revision/review/implementation work for `COMMON_STATISTICAL_PROFILE_V1` without candidate outcome inspection;
- non-candidate/dummy engine-sanity tests;
- safe parallel engineering/review work in isolated worktrees under the Owner collaboration contract and `AGENTS.md`.

NOT_AUTHORIZED:
- data-first automatic K-line/chart-pattern/indicator/rule/parameter strategy mining as the project's research route;
- candidate PnL/equity/expectancy/Sharpe/win-loss or equivalent candidate-quality inspection until the revised real common statistical profile is independently reviewed, locked, identity-bound into a real research wave, and the frozen pre-outcome gate passes;
- validation access before frozen prerequisites;
- historical final-holdout unlock;
- changing frozen 12/6/6 without a new protocol/Owner gate;
- changing frozen research semantics without a new protocol/Owner gate;
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

During the current fresh-conversation takeover check, **all project advancement is additionally paused**. The new conversation may read/verify/report only until the Owner accepts the takeover.

## Tools / capability / current execution workflow

```text
TOOL_DECISION=USE_EXISTING
TOOL_DECISION_SCOPE=COMMON_STATISTICAL_PROFILE_V1_REVISION_AFTER_PARALLEL_REVIEW
PAID_CHAT_RELAY_ORCHESTRATOR=NOT_ADOPTED_CURRENTLY
BRITTLE_VSCODE_UI_CHAT_AUTOMATION=NOT_ADOPTED_CURRENTLY
CURRENT_DS_RELAY_MODE=OWNER_MANUAL_RELAY_WHEN_LOCAL_AGENT_IS_NEEDED
```

No new tool gap is demonstrated. Existing repository evidence/code/tests, primary statistical literature, GPT project-brain adjudication, and the Owner's existing VS Code DeepSeek V4 Flash capability are sufficient for the next bounded package. The Owner explicitly declined adding a new paid OpenAI API solely to automate ChatGPT↔DeepSeek message relay; future new paid APIs/services remain an Owner gate. UI-click/clipboard automation is not the current plan because it is brittle.

When GPT can safely perform repository-only documentation/state/review-integration work through connected GitHub tools, it should do so directly instead of consuming a DS worker. DS remains appropriate for local code/tests/runtime work and bounded independent review.

Tool-status taxonomy must not be conflated:
- project-level external capability status uses `CANDIDATE / VERIFIED / ADOPTED`;
- the cross-project `TOOL_REGISTRY.md` uses its own catalog taxonomy such as `CANDIDATE / APPROVED / DEFERRED / REJECTED / RETIRED`;
- repository/CURRENT_STATE project facts decide what this project actually uses.

Project-local adopted capabilities remain:
- TqSdk 3.10.1 — historical concrete-contract 1-minute research data only;
- PyArrow/Parquet 25.0.1 — normalized canonical storage;
- SQLite — rebuildable canonical catalog/index;
- Raw JSON + SHA256 provenance — authoritative raw evidence mechanism.

Source-acquisition pilot status remains:
- video-to-skill overall CANDIDATE; local multimodal pipeline VERIFIED; anonymous YouTube/Bilibili adapters unverified due 403/412;
- book-to-skill DEFERRED / REFERENCE;
- Docling v2.120.3 VERIFIED for Windows document/layout extraction; NOT ADOPTED;
- video-transcribe-skill VERIFIED for local/offline Chinese no-caption fallback; NOT ADOPTED.

## Known limitations / technical debt

Authority: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`.

Current material items:
- TD-001 duplicate session/trading-day responsibility;
- TD-002 partial-close unrealized-PnL simplification;
- LIMIT-001 historical price-limit metadata incomplete;
- DECISION-001 live AI scene-recognition unresolved / Owner-gated;
- ACQ-LIMIT-001 anonymous YouTube 403 / Bilibili yt-dlp 412;
- SOURCE-LIMIT-001 青泽 bibliographic provenance only;
- SOURCE-LIMIT-002 China-first derivative interview leads incomplete provenance.

Activation boundaries:
- TD-001 must be isolated/consolidated before new trusted day/week statistic code can accidentally consume the wrong calendar authority;
- TD-002 must be fixed before final-quality equity/drawdown path evidence depends on partial-close snapshots;
- LIMIT-001 must be resolved/bound before affected real confirmatory PnL claims can be generated.

## Parallel-work operating state

Owner collaboration explicitly prefers safe parallelism when work is genuinely independent.

Project rules:
- isolated worktrees/branches for parallel workers;
- one integration lane owns `main` and shared authority/state;
- parallel workers do not push `main` or independently edit shared authority unless assigned;
- normally keep concurrency to 2–3 high-value lanes;
- when multiple independent lanes are already ready and Owner is manually relaying prompts, provide all runnable prompts together rather than one lane per conversation turn;
- do not parallelize tasks whose meaning depends on an unresolved research-semantic decision or Owner gate;
- before creating a new worktree/branch, inspect existing `git worktree list` and branch state instead of blindly recreating names.

The statistical review/audit evidence is now integrated to `main`. Local review worktrees may still exist on the Owner machine and do not need destructive cleanup for handoff; future workers must inspect before reusing or creating worktrees.

## Verification status

Last canonical code verification reported by all three statistical lanes:

```text
python -m unittest discover -s tests -v
235 tests OK
3 skipped
exit 0
```

All main changes after that verification, including second/third-pass handoff/state corrections and the two review-evidence integrations, are documentation/state/authority-only; no production/test code changed. Therefore `235 OK / 3 skipped` remains the latest code-bearing verification baseline, not a claim that a new code suite was required after doc-only merges.

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

This is the recorded next project package **after conversation takeover is accepted**. During the current takeover-verification turn it must not be executed.

After takeover acceptance, the next package should revise the Common Statistical Profile candidate and design evidence in one coherent pass, without candidate outcomes, then run a targeted delta independent review over only the materially changed statistical definitions. Do not repeat the entire project review. Statistical evaluator/round-trip-ledger implementation should follow acceptance of the revised profile, except for purely non-semantic helpers that are independently useful and cannot bias the profile decision.

## Progress estimates (engineering estimates, not evidence facts)

```text
ARCHITECTURE_BOOTSTRAP=100%
DATA_SUBSTRATE≈90%
STRATEGY_CATALOG≈58%
BACKTEST_VALIDATION≈64%
HUMAN_PLAYBOOK_RESEARCH_LOOP≈43%
TRADING_LOOP≈15%
LEDGER_OBSERVABILITY≈25%
OVERALL_PROJECT≈45%
```

These percentages are deliberately conservative and do not use test counts as the denominator.

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
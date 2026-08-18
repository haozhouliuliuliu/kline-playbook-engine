# CURRENT_STATE

## Project phase

PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE_BASELINE=Skeleton_v1.0
ARCHITECTURE_STATUS=ACCEPTED
ADOPTED_CONTRACT_VERSION=3.1
ADOPTED_CONTRACT_SHA256=3b5ceaaa3696375b941fd2aaba95615cf9352dcada3696b60137650bf690101e
BOOTSTRAP_ACCEPTANCE=GO
BOOTSTRAP_ACCEPTANCE_EVIDENCE=docs/evidence/BOOTSTRAP_ACCEPTANCE.md
CURRENT_BLOCKER=NONE
CURRENT_WORK_PACKAGE=HUMAN_PLAYBOOK_PREOUTCOME_RESEARCH_FIREWALL_IMPLEMENTATION

## Binding research direction

RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
RESEARCH_DIRECTION_STATUS=OWNER_APPROVED
RESEARCH_DIRECTION_AUTHORITY=RESEARCH_DIRECTION.md

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

Human sources create hypotheses, not accepted truth. Skeleton v1.0 remains binding.

LIVE_AI_SCENE_RECOGNITION_MODE=UNDECIDED
LIVE_DISCRETIONARY_LLM_CRITICAL_PATH=NOT_AUTHORIZED
OWNER_GATE_REQUIRED_FOR_LIVE_AI_SEMANTICS=YES

## Research Protocol v1.0 — FROZEN

Owner decision on 2026-08-19:

`按 v0.3 推荐冻结`

Owner approval evidence:
`docs/evidence/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_OWNER_FREEZE_2026-08-19.md`

Binding protocol:
`docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`

Binding chronology:
`docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`

Binding Selection Firewall requirements:
`docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md`

Active claim schema:
`docs/research/HUMAN_PLAYBOOK_CLAIM_EXTRACTION_SCHEMA_V1_0.md`

State:

```text
RESEARCH_PROTOCOL_VERSION=1.0
RESEARCH_PROTOCOL_STATUS=FROZEN_BINDING
RESEARCH_PROTOCOL_FREEZE_EXECUTION_STATUS=COMPLETE
CHRONOLOGICAL_SPLIT_STATUS=FROZEN_12_6_6
OWNER_FREEZE_DECISION=APPROVED
PERFORMANCE_RESEARCH_STARTED=NO
REAL_CLAIM_EXTRACTION_STARTED=NO
CLAIM_EXTRACTION_SCHEMA_STATUS=ACTIVE_V1_0_PENDING_SOURCE_ONLY_READINESS
```

Material research-semantic changes now require a new protocol version, material independent adversarial review, and the normal Owner research-semantic gate.

## Frozen protocol safeguards

Protocol v1.0 freezes:
- `SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION`;
- `EXPLICIT / INFERRED / UNKNOWN`;
- exactly one source-justified PRIMARY branch before candidate outcome testing;
- ambiguity stops instead of mining alternatives for a winner;
- branch/scope/search identities locked before outcome testing;
- alternatives cannot rescue a failed PRIMARY as validation of the source claim;
- lineage/mechanism/exposure inheritance survives renaming;
- effective-content-date source-example exposure;
- observability/surrogate pre-justification;
- negative/near-miss/no-trade/counterexample preservation;
- immutable RESEARCH_WAVE denominator and whole-wave multiplicity accounting;
- `PROJECT_GOVERNED_HISTORICAL_HOLDOUT != PROSPECTIVE_GENUINELY_UNSEEN_DATA`;
- SOURCE_ONLY interpretation with technical denial of protected-period market outcome retrieval;
- human/AI latent historical knowledge treated as disclosed residual threat-model risk, not falsely certified absent;
- project-wide common statistical profile locked before first candidate outcome-bearing performance backtest;
- common acceptance contract with dependence-aware evidence sufficiency;
- `INSUFFICIENT_EVIDENCE` as legitimate result;
- CAT1/CAT2/CAT3 validation revision rules;
- irreversible historical-final exposure;
- future Shadow/Forward as the stronger prospective unseen path under later authority.

## Frozen chronology

```text
DEVELOPMENT: 2024-01-01 .. 2024-12-31
VALIDATION: 2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT: 2025-07-01 .. 2025-12-31
PROSPECTIVE_GENUINELY_UNSEEN: future Shadow/Forward cohorts, NOT_AUTHORIZED
```

The frozen split is `12/6/6`.

It is an audit/governance choice and does not guarantee statistical power. Sparse families may return `INSUFFICIENT_EVIDENCE`; split boundaries may not be changed after outcomes are viewed to rescue evidence.

## Pre-outcome gate — implementation pending

Research Protocol v1.0 is semantically frozen, but current code does **not** yet implement the full gate.

Repository reality:
- `src/strategy_evidence.py` has append-only strategy/evidence identities and a simple `FinalUnseenFirewall` that denies `DatasetClass.FINAL_UNSEEN`;
- it does not yet implement SOURCE_ONLY technical denial, immutable RESEARCH_WAVE manifests, common-statistical-profile locks, or the new historical-final state model.

Before the first candidate outcome-bearing performance backtest, all must be technically true and verified:

```text
SOURCE_ONLY_CONTROLS=ACTIVE_AND_VERIFIED
COMMON_STATISTICAL_PROFILE=LOCKED
MULTIPLICITY_COUNTING_UNIT=LOCKED
RESEARCH_WAVE=LOCKED
PRIMARY_SCOPE_SEARCH_IDENTITIES=LOCKED
```

Until this gate is implemented and passes:

```text
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
```

Allowed now:
- implement/test SOURCE_ONLY controls;
- implement research-wave/profile/firewall machinery;
- source discovery/provenance;
- non-candidate engine sanity tests;
- non-outcome operationalization/tests;
- after SOURCE_ONLY controls are verified, controlled real source-faithful claim extraction under Claim Schema v1.0.

Forbidden now:
- candidate PnL/equity/expectancy/Sharpe/win-loss or equivalent performance inspection.

## Canonical BALANCED corpus — ACCEPTED

CANONICAL_DATASET_BUILT=YES
CANONICAL_DATASET_ACCEPTED=YES
CANONICAL_DATASET_STATUS=ACCEPTED
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

Authorities:
- `docs/evidence/SOURCE_AND_SCOPE_OWNER_APPROVAL.md`;
- `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`;
- `docs/evidence/CANONICAL_CORPUS_IDENTITY.json`;
- `docs/evidence/CANONICAL_FULL_CROSS_SOURCE.json`.

The corpus itself created no project-recorded strategy-family development/validation/historical-final exposure.

## Source layer

FIRST_WAVE_SOURCE_LAYER_RESULT=GO

Completed source dossiers cover:
- Peter Brandt;
- Al Brooks;
- Linda Raschke;
- Adam Grimes;
- Brett Steenbarger;
- Steidlmayer -> Dalton Market Profile lineage;
- skeptical/counter-evidence methods: White, Sullivan/Timmermann/White, Bailey et al.

China-first:
- 青泽: identity/bibliography verified; no full dossier without authorized text/sample;
- 期货日报实盘大赛: DISCOVERY_ONLY;
- 付爱民、王少多、张亚楠: discovery leads only; provenance pinning incomplete.

Source authorities:
- `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`;
- `docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md`;
- `docs/research/HUMAN_PLAYBOOK_SOURCE_LAYER_FIRST_WAVE_CLOSEOUT.md`;
- `docs/research/CHINA_FIRST_SOURCE_DISCOVERY_WAVE_1.md`.

## Current boundaries

NOT_AUTHORIZED:
- candidate outcome-bearing performance backtest before the frozen pre-outcome gate is implemented and locked;
- validation access before its frozen prerequisites;
- historical final-holdout unlock;
- changing the frozen 12/6/6 split without a new protocol/Owner gate;
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

## Tools / capability

```text
TOOL_DECISION=USE_EXISTING
TOOL_DECISION_SCOPE=HUMAN_PLAYBOOK_PREOUTCOME_RESEARCH_FIREWALL_IMPLEMENTATION
```

No new tool gap is demonstrated. The Owner's existing VS Code DeepSeek Flash-family capability may perform bounded engineering implementation/review but cannot change frozen research semantics.

Source-acquisition status:
- video-to-skill overall CANDIDATE; local multimodal pipeline VERIFIED; anonymous YouTube/Bilibili adapters unverified due 403/412;
- book-to-skill DEFERRED / REFERENCE;
- Docling v2.120.3 VERIFIED for Windows document/layout extraction; NOT ADOPTED;
- video-transcribe-skill VERIFIED for local/offline Chinese no-caption fallback; NOT ADOPTED.

Project-local adopted capabilities:
- TqSdk 3.10.1 — historical concrete-contract 1-minute research data only;
- PyArrow/Parquet 25.0.1 — normalized canonical storage;
- SQLite — rebuildable canonical catalog/index;
- Raw JSON + SHA256 provenance — authoritative raw evidence mechanism.

## Known limitations / technical debt

Authority: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`.

Current non-blocking items:
- TD-001 duplicate session/trading-day responsibility; activate before affected confirmatory/backtest/production/live semantics;
- TD-002 partial-close unrealized-PnL simplification; activate before PnL-sensitive confirmatory evidence is final quality;
- LIMIT-001 historical price-limit metadata incomplete; activate before price-limit non-fill realism is claimed;
- DECISION-001 live AI scene-recognition unresolved / Owner-gated;
- ACQ-LIMIT-001 anonymous YouTube 403 / Bilibili yt-dlp 412;
- SOURCE-LIMIT-001 青泽 bibliographic provenance only;
- SOURCE-LIMIT-002 China-first derivative interview leads incomplete provenance.

TD-001/TD-002/LIMIT-001 did not block semantic protocol freeze. They must activate before affected evidence claims rely on their semantics.

## Current next action

```text
CURRENT_NEXT_ACTION=IMPLEMENT_AND_VERIFY_HUMAN_PLAYBOOK_PREOUTCOME_RESEARCH_FIREWALL
CURRENT_NEXT_ACTION_AUTHORITY=docs/research/HUMAN_PLAYBOOK_SELECTION_FIREWALL_REQUIREMENTS_V1_0.md
NEXT_AFTER_GATE_SOURCE_ONLY=BEGIN_CONTROLLED_REAL_CLAIM_EXTRACTION_V1_0
OWNER_ACTION=NONE
```

The immediate bounded engineering package is to implement and verify:
- SOURCE_ONLY technical denial/session evidence;
- immutable research-wave manifest/lock;
- common statistical-profile identity/lock interface (exact independently reviewed numerical profile may be completed in the same pre-outcome program before candidate outcomes);
- pre-outcome fail-closed gate;
- historical-final state naming/lock semantics without unlocking it;
- tests proving candidate outcomes remain inaccessible until the required locks are present.

No repeated Owner approval is required for this ordinary implementation work under frozen Protocol v1.0.

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

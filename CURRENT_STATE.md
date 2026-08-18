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
CURRENT_WORK_PACKAGE=TARGETED_FINAL_PREFREEZE_ADVERSARIAL_DELTA_REVIEW

## Binding research direction

RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
RESEARCH_DIRECTION_STATUS=OWNER_APPROVED
RESEARCH_DIRECTION_AUTHORITY=RESEARCH_DIRECTION.md

Primary research route:

```text
traceable human trading experience
-> AI-assisted extraction and structuring
-> versioned Playbook Contract
-> point-in-time market-scene representation / recognition
-> historical validation of applicability and failure conditions
-> strict validation / protected-holdout governance
-> accepted or rejected playbook
```

Human sources create hypotheses, not accepted truth. The project is not an unconstrained indicator/rule/parameter-mining engine.

LIVE_AI_SCENE_RECOGNITION_MODE=UNDECIDED
LIVE_DISCRETIONARY_LLM_CRITICAL_PATH=NOT_AUTHORIZED
OWNER_GATE_REQUIRED_FOR_LIVE_AI_SEMANTICS=YES

Skeleton v1.0 remains binding and is not reopened by this protocol work.

## Protocol state

The first Human Playbook source-layer wave is COMPLETE / GO at source-only level.
The non-frozen Claim Extraction schema exists and has NOT been applied to real trading logic.

Protocol history:
- v0.1 input package received independent adversarial review: `GO_WITH_REQUIRED_CHANGES` (3 CRITICAL, 6 HIGH);
- project brain adjudicated that review;
- revised freeze candidate v0.2 and Owner decision package v0.1 were created;
- the Owner then explicitly requested one final omission/error/forgetfulness recap before automatic approval;
- that recap found three **new material research-semantics gaps** not sufficiently covered by the first independent review.

Final pre-freeze gap review:
`docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_FINAL_PREFREEZE_GAP_REVIEW_V0_1.md`

Current state:

```text
PROTOCOL_INPUT_V0_2_STATUS=SUPERSEDED_AS_IMMEDIATE_FREEZE_CANDIDATE_PENDING_DELTA_REVIEW
OWNER_DECISION_PACKAGE_V0_1_STATUS=HOLD_PENDING_DELTA_REVIEW
OWNER_AUTO_APPROVAL_CONDITION=NOT_SATISFIED_NEW_MATERIAL_GAPS_FOUND
RESEARCH_PROTOCOL_FREEZE_REQUIRED_BEFORE_STRATEGY_RESEARCH=YES
RESEARCH_PROTOCOL_FREEZE_EXECUTION_STATUS=NOT_EXECUTED
STRATEGY_RESEARCH_STARTED=NO
CLAIM_EXTRACTION_SCHEMA_STATUS=ACTIVE_DRAFT_NON_FROZEN_NOT_APPLIED
```

No concrete playbook, split, final unlock, live-AI semantics, or permanent risk rule has been frozen by the preparation/review work.

## New material gaps found in final recap

### GAP-A — historical holdout vs exogenous human/AI knowledge

The project begins in 2026 against historical 2024-2025 data. Repository locks and source-example audits do not prove that humans or current AI models lack prior knowledge of 2025 market outcomes.

Required correction under review:
- distinguish `PROJECT_GOVERNED_HISTORICAL_HOLDOUT` from `PROSPECTIVE_GENUINELY_UNSEEN_DATA`;
- treat future Shadow/Forward data as the genuinely prospective unseen path;
- use a source-only interpretation process with no protected-market outcome retrieval/browsing and log model/prompt/tool context;
- explicit retrieval/citation of protected-period outcomes during claim design creates exposure;
- latent model memory cannot be proven absent, so historical holdout evidence must not be overstated as epistemically unseen to all researchers/models.

### GAP-B — family/claim/wave-level multiplicity

Skeleton v1.0 requires search freedom to include strategy count. v0.2 governs branch-level freedom strongly but does not explicitly freeze multiplicity across many different Human Playbooks/claims.

Required correction under review:
- pre-register each outcome-bearing `RESEARCH_WAVE_ID`;
- count tested playbook families, separately testable claims, branches, instruments, timeframes, contexts and parameter/search ranges;
- preserve rejected/failed/insufficient families in the denominator;
- adding families/claims after outcome inspection creates a new wave/search event;
- project-wide statistical controls must consider full wave multiplicity when material.

### GAP-C — common statistical profile freeze timing

v0.2 allowed the exact project-wide confidence/precision/event-sufficiency implementation to be finalized before validation. That may be too late if development performance backtests have already been observed.

Required correction under review:

```text
COMMON_STATISTICAL_PROFILE_V1
must be independently reviewed + versioned + locked
BEFORE THE FIRST OUTCOME-BEARING PERFORMANCE BACKTEST
```

Before that profile is frozen, source/claim extraction, PRIMARY interpretation, observability review, deterministic operationalization and non-outcome tests may proceed; candidate PnL/expectancy/Sharpe/win-rate/equity comparisons may not.

## Prior safeguards that still survive the final recap

Still recommended, subject to targeted delta review:
- source claim != AI/project interpretation != machine operationalization;
- `EXPLICIT / INFERRED / UNKNOWN`;
- exactly one source-justified PRIMARY branch before outcome testing;
- ambiguous source meaning stops rather than mining alternatives;
- branch/AI-spec/scope/search identity locked before testing;
- alternatives cannot rescue a failed primary as validation of the original claim;
- common acceptance contract; no family metric shopping;
- product count is not assumed equal to independent sample count;
- `INSUFFICIENT_EVIDENCE` is valid;
- source-example exposure uses effective content/version date plus example-date audit;
- lineage/mechanism identity and exposure survive renaming;
- surrogates require source/measurement justification before outcome testing;
- validation CAT1/CAT2/CAT3 fail-safe;
- historical final-holdout exposure is irreversible;
- final-inspired descendants require genuinely new prospective evidence.

The prior recommendation `12/6/6` is not rejected, but its semantics must distinguish historical locked holdout from genuinely prospective unseen data:

```text
DEVELOPMENT                  2024-01-01 .. 2024-12-31
VALIDATION                   2025-01-01 .. 2025-06-30
PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT
                             2025-07-01 .. 2025-12-31
PROSPECTIVE_GENUINELY_UNSEEN future Shadow/Forward cohorts
```

No split is frozen yet.

## Canonical BALANCED corpus (accepted)

CANONICAL_DATASET_BUILT=YES
CANONICAL_DATASET_ACCEPTED=YES
CANONICAL_DATASET_STATUS=ACCEPTED
SCALE_DECISION=APPROVED_FULL_BALANCED_CORPUS
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

Authority:
- `docs/evidence/SOURCE_AND_SCOPE_OWNER_APPROVAL.md`
- `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`
- `docs/evidence/CANONICAL_CORPUS_IDENTITY.json`
- `docs/evidence/CANONICAL_FULL_CROSS_SOURCE.json`

The accepted corpus itself created no project-recorded strategy-family development/validation/final-holdout exposure.

## Source-layer state

FIRST_WAVE_SOURCE_LAYER_RESULT=GO

Completed source dossiers cover:
- Peter Brandt;
- Al Brooks;
- Linda Raschke;
- Adam Grimes;
- Brett Steenbarger;
- Steidlmayer -> Dalton Market Profile lineage cluster;
- skeptical/counter-evidence methods cluster: White, Sullivan/Timmermann/White, Bailey et al.

China-first status:
- 青泽: identity/bibliography verified; no full dossier without authorized text/sample;
- 期货日报实盘大赛: DISCOVERY_ONLY;
- 付爱民、王少多、张亚楠: discovery leads only; provenance pinning incomplete.

Source-layer authorities:
- `docs/research/HUMAN_PLAYBOOK_SOURCE_DOSSIER_V0_2.md`
- `docs/research/HUMAN_PLAYBOOK_SOURCE_MATERIAL_INVENTORY.md`
- `docs/research/HUMAN_PLAYBOOK_SOURCE_LAYER_FIRST_WAVE_CLOSEOUT.md`
- `docs/research/CHINA_FIRST_SOURCE_DISCOVERY_WAVE_1.md`

## Current boundaries

NOT_AUTHORIZED:
- concrete K-line/playbook strategy conclusions;
- applying Claim Extraction schema to real trading logic before protocol freeze;
- concrete buy/sell rule extraction as project claims;
- any outcome-bearing candidate performance backtest under the unfrozen protocol;
- large-scale strategy mining or unconstrained indicator/rule/parameter search;
- automatic parameter optimization outside a frozen protocol;
- converting fuzzy source language into machine thresholds before protocol authority;
- validation or historical final-holdout access under an unfrozen protocol;
- final-holdout unlock;
- Shadow automated trading;
- real-money trading;
- real broker order submission;
- discretionary LLM buy/sell decisions in live critical path;
- new paid commitments;
- permanent RiskGate semantics without Owner approval;
- large multi-agent research orchestration;
- knowledge graph build-out;
- microservices/distributed architecture;
- importing strategy conclusions/results/parameters from other projects;
- treating generated summaries/Skills as source authority;
- bypassing paywalls/DRM/platform permissions;
- authenticated browser-cookie acquisition without separate credential/data-flow review;
- redistribution of copyrighted raw source material.

## Current architecture

Top-level domains remain:
1. Data Substrate
2. Strategy Catalog
3. Backtest & Validation Engine
4. Research Loop
5. Trading Loop
6. Ledger
7. Observability & Control

See `ARCHITECTURE_BASELINE.md` for binding details.

## Current tools / capability decision

```text
TOOL_DECISION=USE_EXISTING
TOOL_DECISION_SCOPE=TARGETED_FINAL_PREFREEZE_DELTA_REVIEW
```

No new tool gap is demonstrated.

A DeepSeek Flash-family model remains available in Owner VS Code and may perform the required targeted independent adversarial delta review. It may critique/propose alternatives but may NOT freeze research semantics.

Source acquisition statuses remain:
- video-to-skill: overall CANDIDATE; local multimodal pipeline VERIFIED; anonymous YouTube/Bilibili URL adapters unverified due 403/412;
- book-to-skill: DEFERRED / REFERENCE;
- Docling v2.120.3: VERIFIED for Windows document/layout extraction; NOT ADOPTED;
- video-transcribe-skill: VERIFIED for local/offline Chinese no-caption fallback; NOT ADOPTED.

Project-local adopted capabilities:
- TqSdk 3.10.1 — historical concrete-contract 1-minute research data only;
- PyArrow/Parquet 25.0.1 — normalized canonical storage;
- SQLite — rebuildable canonical catalog/index;
- Raw JSON + SHA256 provenance — authoritative raw evidence mechanism.

## Known limitations / technical debt

Authority: `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`.

Current non-blocking items:
- TD-001 duplicate session/trading-day responsibility; activate before affected backtest/production/live authority;
- TD-002 partial-close unrealized-PnL simplification; activate before PnL-sensitive confirmatory evidence is final quality;
- LIMIT-001 historical price-limit metadata incomplete; activate before price-limit non-fill realism is claimed;
- DECISION-001 live AI scene-recognition implementation unresolved / Owner-gated;
- ACQ-LIMIT-001 anonymous YouTube 403 / Bilibili yt-dlp 412 in tested Windows environment;
- SOURCE-LIMIT-001 青泽 has bibliographic provenance only;
- SOURCE-LIMIT-002 several China-first interview leads remain derivative until provenance is pinned.

None blocks the targeted delta review.

## Current next action

```text
CURRENT_NEXT_ACTION=TARGETED_INDEPENDENT_ADVERSARIAL_DELTA_REVIEW_OF_FINAL_PREFREEZE_GAPS
CURRENT_NEXT_ACTION_AUTHORITY=docs/reviews/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_FINAL_PREFREEZE_GAP_REVIEW_V0_1.md
REVIEWER_ROLE=ADVISORY_NOT_AUTHORITY
OWNER_ACTION=RUN_TARGETED_DELTA_REVIEW_IN_EXISTING_VSCODE_DEEPSEEK_FLASH
```

After the targeted review, project brain must adjudicate only these new deltas, revise the protocol/Owner decision package if needed, and then re-evaluate whether the Owner's conditional automatic approval can safely execute.

## Owner decision gates

Owner approval remains required for frozen research semantics, paid commitments, irreversible external actions, authenticated acquisition with material new data-flow risk, permanent risk rules, real-money/broker actions, or live critical-path changes.

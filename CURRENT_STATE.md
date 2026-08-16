# CURRENT_STATE

## Project phase
PROJECT_PHASE=RESEARCH_FOUNDATION
ARCHITECTURE_BASELINE=Skeleton_v1.0
ARCHITECTURE_STATUS=ACCEPTED
ADOPTED_CONTRACT_VERSION=3.1
ADOPTED_CONTRACT_SHA256=3b5ceaaa3696375b941fd2aaba95615cf9352dcada3696b60137650bf690101e
LAST_KNOWN_GOOD=b6d1961dca5b4c879bc7deb6406f3c63723b04d4
BOOTSTRAP_ACCEPTANCE=GO
BOOTSTRAP_ACCEPTANCE_EVIDENCE=docs/evidence/BOOTSTRAP_ACCEPTANCE.md
CURRENT_BLOCKER=NONE

## Current objective
Execute the Owner-approved canonical research dataset build and source
acceptance package: record the Owner source/scope decision durably (done in
`docs/evidence/SOURCE_AND_SCOPE_OWNER_APPROVAL.md`), then build and accept the
BALANCED canonical research corpus on `ds/canonical-dataset-build` without
exposing any partial canonical-dataset claims on `main`.

## Owner source/scope decision (final, recorded durably)
OWNER_APPROVAL=YES
OWNER_SOURCE_APPROVAL=TQSDK
TQSDK_STATUS=ADOPTED
TQSDK_ADOPTION_SCOPE=historical concrete-contract 1-minute research data only
TQSDK_VERIFIED_RUNTIME=3.10.1
OWNER_DATASET_SCOPE_APPROVAL=BALANCED
PAID_CONTINUITY_AUTHORIZED=NO
PAID_CONTINUITY_OWNER_GATE=REQUIRED_IF_NEEDED_LATER
CANONICAL_DATASET_BUILT=NO
CANONICAL_DATASET_ACCEPTED=NO

Authority record: `docs/evidence/SOURCE_AND_SCOPE_OWNER_APPROVAL.md`.
Adoption does NOT authorize broker connectivity, live/Shadow trading, order
submission, or future paid renewal; TqSdk runtime compatibility is frozen to
the verified `3.10.1` identity until re-verified.

## Current boundaries
NOT_AUTHORIZED:
- concrete K-line strategy conclusions;
- large-scale strategy mining;
- automatic parameter optimization;
- final-unseen evaluation;
- Shadow automated trading;
- real-money trading;
- real broker order submission;
- large multi-agent research orchestration;
- knowledge graph build-out;
- microservices/distributed architecture.

## Current architecture
Top-level responsibility domains:
1. Data Substrate
2. Strategy Catalog
3. Backtest & Validation Engine
4. Research Loop
5. Trading Loop
6. Ledger
7. Observability & Control

See ARCHITECTURE_BASELINE.md for binding architecture details.

## Tool/open-source status
No candidate is automatically adopted.

Known categories:
- execution backbone candidate: VeighNa / vn.py
- fast screening candidate: vectorbt
- data/simulation candidates: TqSdk, openctp, SimNow
- storage baseline candidates: SQLite, Parquet; DuckDB optional
- later/reference only: NautilusTrader, STUMPY, RD-Agent, Qlib, TradingAgents, MiroFish, Freqtrade, Jesse, LEAN

Current project-specific source status:
- TqSdk: ADOPTED (Owner-approved, scoped). `TQSDK_ADOPTION_SCOPE=historical
  concrete-contract 1-minute research data only`;
  `TQSDK_VERIFIED_RUNTIME=3.10.1`. Adoption does not authorize broker
  connectivity, live/Shadow trading, order submission, or paid renewal; runtime
  compatibility is frozen to the verified `3.10.1` identity. See
  `docs/evidence/SOURCE_AND_SCOPE_OWNER_APPROVAL.md`.
- SHFE official annual raw: VERIFIED for official-origin/hash/daily-statistical
  reference use only; not minute/Tick data and not ADOPTED as the canonical
  research source.

Real TqSdk samples recorded (raw in ignored `data/raw/historical/`, non-secret provenance in `docs/evidence/REAL_HISTORICAL_DATA_SUBSTRATE_FEASIBILITY.md`):
- Bounded probe: `SHFE.ni2509` 1-min, 2025-06-16 10:00-10:40, 26 bars, `DataVersionIdentity=cd4a306f6310fc4e59d5f8b7d340e8b8acd054bb22b364f1ba35ac13def12b0b`.
- Full trading day: `SHFE.ni2509` 1-min, trading day 2025-06-16 (night 2025-06-13 21:00 through day 2025-06-16 15:00), 465 bars, `DataVersionIdentity=724e16537247eb1af233d12a92c9d07d926bff84944abe96c0e5eb518b424fdc`.

All external components must progress through:
CANDIDATE → VERIFIED → ADOPTED

## Current local capability facts
These are environment facts, not project dependencies or adoption decisions.

- VS Code is available on the Owner's Windows workstation and is used for repository work.
- A DeepSeek Flash-family model API is connected in the Owner's VS Code environment and may be considered as an independent reviewer when an actual review need justifies it.
- Do not use the DeepSeek reviewer for routine small code changes merely to obtain a second opinion; prefer deterministic tests and repository evidence first.
- Ponytail was found globally installed in Codex and was disabled/removed from active global discovery on 2026-08-15, with a reversible backup retained outside active discovery. A fresh Codex process/restart is required before relying on absence from runtime context.

## Current next action
CURRENT_NEXT_ACTION=CANONICAL_RESEARCH_DATASET_BUILD_AND_SOURCE_ACCEPTANCE_PACKAGE

## Current acceptance

PROJECT_BOOTSTRAP is formally accepted at
`b6d1961dca5b4c879bc7deb6406f3c63723b04d4`. The acceptance record is
`docs/evidence/BOOTSTRAP_ACCEPTANCE.md`.

## Current tool decision

TOOL_DECISION=ADD_TOOL

The approved BALANCED scope creates a real normalized-storage/catalog gap. The
stage-level storage decision for the canonical build:
- RAW_ARTIFACT_STORAGE: keep ignored JSON raw artifacts + SHA256 provenance
  (existing mechanism remains authoritative raw evidence).
- NORMALIZED_BAR_STORAGE: evaluate and, if a local probe succeeds, adopt
  PyArrow/Parquet for normalized canonical bar storage.
- MANIFEST/METADATA: SQLite (stdlib `sqlite3`) as a rebuildable local
  catalog/index; committed immutable manifests/evidence remain the durable
  provenance authority.
- RESEARCH_QUERY_ENGINE: DuckDB remains DEFERRED/CANDIDATE; not installed.
- No pandas is added merely for convenience.

TqSdk adoption is scoped to historical concrete-contract 1-minute research
data only and does not adopt a broker/order capability.

## Completed research-foundation evidence

- Incremental clean-room reuse classification is recorded in
  `docs/reuse/STEEL_REUSE_AUDIT.md`; no old-project source code or processed
  Gate1 dataset was copied.
- The vendor-neutral historical provenance, raw-artifact, normalizer and
  data-version contracts are implemented in `src/historical_data.py`.
- Fixed-duration historical PIT normalization reuses the existing
  `CompletedBar.available_at` and `CompletedBar.is_visible_at` semantics.
- Deterministic synthetic quality-gate tests are in
  `tests/test_historical_data.py`.
- The SHFE official annual reference recheck is recorded in
  `docs/evidence/SHFE_OFFICIAL_RAW_RECHECK_MANIFEST.json`.
- Package findings, the successful real probe, real provenance, real-sample
  PIT/quality results, and the exact SHFE cross-source match are recorded in
  `docs/evidence/REAL_HISTORICAL_DATA_SUBSTRATE_FEASIBILITY.md`.
- Real TqSdk `3.10.1` samples (`SHFE.ni2509` 1-min bounded and full trading
  day 2025-06-16) passed the existing normalization path, real-sample PIT
  normalization, all real quality gates, and the SHFE daily cross-source
  check. DataVersionIdentity values are recorded in CURRENT_STATE and in the
  evidence file. No research-ready canonical dataset is built yet.
- The Owner source/scope decision (TqSdk ADOPTED, BALANCED scope, no paid
  continuity) is recorded durably in
  `docs/evidence/SOURCE_AND_SCOPE_OWNER_APPROVAL.md`; `main` was
  fast-forwarded to the accepted readiness HEAD
  `238c230207250b3a02cd22dea658898a9a982e53` and pushed.

## Current Owner action

OWNER_ACTION=NONE

## Owner decision gates
Owner-level approval is required only for genuinely new product/research direction, frozen experiment semantics, permanent risk rules, paid commitments, real-money/broker actions, or irreversible external actions.

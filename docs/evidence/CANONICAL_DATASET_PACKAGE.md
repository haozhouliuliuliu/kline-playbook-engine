# Canonical Dataset Package — Evidence (Phase 12)

> **STATUS / SUPERSESSION (read first)** — This document preserves the
> historical pre-acceptance OWNER_GATE package and is retained for auditability.
> The scale guardrail was subsequently approved
> (SCALE_DECISION=APPROVED_FULL_BALANCED_CORPUS), and the complete canonical
> BALANCED corpus was later BUILT and ACCEPTED. This package's
> `FINAL=OWNER_GATE` status is therefore superseded. Final current status
> authority: `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`. Final corpus
> identity authority: `docs/evidence/CANONICAL_CORPUS_IDENTITY.json`
> (`1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8`).

Status of the Owner-approved CANONICAL_RESEARCH_DATASET_BUILD_AND_SOURCE_ACCEPTANCE_PACKAGE.

```text
SOURCE_OWNER_APPROVAL=YES
TQSDK_STATUS=ADOPTED
DATASET_SCOPE_OWNER_APPROVAL=BALANCED
PAID_CONTINUITY_AUTHORIZED=NO
```

## 1. Owner decision record

Recorded durably in `docs/evidence/SOURCE_AND_SCOPE_OWNER_APPROVAL.md` (committed
on `main`, governance commit `6ee1cb9`).

- OWNER_SOURCE_APPROVAL=TQSDK
- TQSDK_STATUS=ADOPTED
- TQSDK_ADOPTION_SCOPE=historical concrete-contract 1-minute research data only
- TQSDK_VERIFIED_RUNTIME=3.10.1
- OWNER_DATASET_SCOPE_APPROVAL=BALANCED
- PAID_CONTINUITY_AUTHORIZED=NO
- PAID_CONTINUITY_OWNER_GATE=REQUIRED_IF_NEEDED_LATER

Adoption does NOT authorize broker connectivity, live/Shadow trading, order
submission, or future paid renewal. TqSdk runtime compatibility is frozen to
the verified `3.10.1` identity; a different runtime requires re-verification
and a new identity.

## 2. Foundation

- main fast-forwarded to accepted readiness HEAD `238c230207250b3a02cd22dea658898a9a982e53` and pushed (FOUNDATION_MERGED=PASS).
- Governance/source-adoption commit `6ee1cb9` on main, pushed.
- Worktree/remote verified clean; no history rewrite; no force push.

## 3. BALANCED corpus definition

`docs/evidence/CANONICAL_DATASET_BALANCED_DEFINITION.md` and
`docs/evidence/CANONICAL_BALANCED_UNIVERSE.json`.

- Coverage: 2024-01-01 .. 2025-12-31 (two complete calendar years).
- Product universe (6, evidence-based, no strategy criteria):
  `cu`, `al`, `ni`, `au`, `ag`, `rb`.
- Granularity: 1-minute concrete-contract bars.
- Contract inventory rule: PIT-complete listed concrete-contract universe,
  data-driven (no future-information preselection); research/main-contract
  selection rule deferred to the later research-protocol freeze.
- Concrete-contract count in the governed universe: **212**
  (36 each for cu/al/ni/ag/rb, 32 for au).
- Official trading days: 242 (2024), 243 (2025).

## 4. Governed official metadata

Committed governed metadata fixtures (each fact binds source URL, retrieval
timestamp, effective period, schema/version):

- `CANONICAL_TRADING_CALENDAR.json` — trading days + official night-closed
  trading days bound to the verified SHFE official annual raw and the official
  annual 休市安排 announcements (OFFICIAL_AVAILABLE). Identity `5892a946…`
  (v2, includes night-closed days).
- `CANONICAL_CONTRACT_UNIVERSE.json` — listed concrete contracts with
  first/last official trading day (OFFICIAL_AVAILABLE).
- `CANONICAL_SESSION_SCHEDULES.json` — official day/night session schedules
  bound to the official SHFE trading-hours page, effective period
  2024-01-01..2025-12-31 (OFFICIAL_AVAILABLE).
- `CANONICAL_CONTRACT_SPECS.json` — tick, multiplier, quote unit, contract
  months, price limit bound to official SHFE contract-text pages, with explicit
  effective periods and binding notices (OFFICIAL_AVAILABLE).

### Correction notice (project-lead review, before large acquisition)

The build-branch v1 evidence marked GOVERNED_METADATA=PASS too early: the
contract specs recorded values and page/publication dates but did NOT prove
effective coverage over the entire 2024–2025 window (al 2024-07-12, rb
2024-09-24, ni 2025-10-31), and the 2024/2025 night-closed days were only
PENDING_OFFICIAL_BINDING. GPT/project-lead review identified
HISTORICAL_METADATA_EFFECTIVE_PERIOD_BINDING as a material blocker.

Correction performed (before any large corpus acquisition):

- **Contract-spec historical effective periods**: verified from official SHFE
  material that, for every approved product, tick/multiplier/quote unit and the
  session schedule were stable across 2024–2025. The in-window contract-text
  revisions were delivery-grade/delivery-detail changes only:
  - al: 上期所公告[2024]105号 (2024-07-12) — 铝合约修订版，仅交割品级；
  - rb: 上期所公告[2024]116号 (2024-07-29) — 螺纹钢/线材合约及交割细则修订版，仅交割品级；
  - base values set by 上期所公告[2023]2号 (2023-01-17) for cu/ag/ni and
    [2020]134号 for au, effective before the window.
  Each product's spec now records explicit effective_start/effective_end,
  source_resource_identity, binding notice, retrieved_at, classification.
- **Night-closed days**: resolved from the official annual 休市安排
  announcements — 上期所公告[2023]127号 (2023-12-26, 2024) and
  上期所公告[2024]204号 (2024-12-23, 2025). 2024: 7 night-closed trading days;
  2025: 6. `TradingCalendar` now carries these and no expected bar is generated
  for a closed night.
- **Fail-closed metadata authority**: the build planner fails closed when no
  effective period covers a trading day, multiple conflicting effective
  periods cover it, session authority is unresolved, or contract
  listing/expiry is inconsistent with the trading day (deterministic tests).

No large canonical data was acquired under the defective metadata (the scale
probe of 24 partitions used the raw TqSdk path, not the canonical corpus).
Only after this actual effective-period validation succeeds is
GOVERNED_METADATA restored to PASS.

GOVERNED_METADATA=PASS (after correction; validated effective periods)

Remaining recorded limitation (not required to normalize/validate the bar
corpus in this package):
- Price-limit history is DEFERRED.

## 5. Storage tool admission

- RAW_ARTIFACT_STORAGE: existing ignored JSON raw + SHA256 provenance retained.
- NORMALIZED_BAR_STORAGE: PyArrow/Parquet real local probe PASSED
  (Decimal/timezone/nullable-OI preserved; canonical partitioned layout;
  write/read logical equality via select+cast). PYARROW_STATUS=ADOPTED, tested
  PyArrow 25.0.1 (pinned canonical-build dependency).
- MANIFEST/METADATA: SQLite (stdlib `sqlite3`) rebuildable catalog.
  SQLITE_CATALOG=PASS. SQLite is NOT the historical truth authority; committed
  immutable manifests/evidence remain the durable provenance authority.
- RESEARCH_QUERY_ENGINE: DuckDB remains DEFERRED; not installed.
- No pandas added.

TOOL_DECISION=ADD_TOOL

## 6. Canonical storage schema

`src/canonical_storage.py` — canonical-normalized-bar-v1 schema (provider,
source, exchange, concrete contract, product, trading_day, bar start/end,
historical available_at, OHLC decimal128(24,4), volume, open interest start/end,
raw artifact identity/hash, source identity, DataVersionIdentity, contract
metadata identity, session metadata identity, normalizer/schema version).
Partition layout: `exchange/product/contract/year/month`
(PARQUET_STORAGE_VERSION=parquet-partitioned-v1). No silent price rounding; no
forward-fill; no synthetic bars.

## 7. Acquisition / resume engine

`src/historical_acquisition.py` (accepted foundation) + `tools/build_canonical_dataset.py`:

- TqSdk 3.10.1 runtime-version bound; local hidden TqAuth only; no stored
  credentials; no broker/order APIs.
- sequential/conservative source access; bounded transient retry; auth failures
  fail closed.
- atomic raw writes (.partial -> replace); collision-safe partition identities.
- idempotent resume/checkpoint (manifest persists after every partition); a
  paused/interrupted run never invalidates accepted partitions and never
  duplicates accepted data.
- resumable bounded batches; dry-run plan generation verified (32,912 planned
  partitions from governed listing windows).

## 8. Scale probe and guardrail (why the large acquisition is GATED)

Real bounded probe (24 partitions, one TqSdk session, 2026-08-16; the Owner
trial is ACTIVE and returned real 2024 and 2025 data):

- TqSdk returns the full session bar skeleton even for ultra-thin far-month
  contracts (465 rows for 21:00–01:00 products, 555 for 21:00–02:30, 345 for
  21:00–23:00), with volume=0 on empty minutes.
- Measured average raw partition size ≈ 79.6 KB.

Refined projection for the full bias-free corpus (32,841 traded partitions):
- raw storage ≈ **2.615 GB**;
- bars ≈ **15.4 M**;
- 3× readiness guardrail ≈ 1.32 GB → **EXCEEDED ≈ 1.98×**;
- 5 GB absolute cap → not exceeded.

Per the Owner guardrail, the large acquisition is **STOPPED before acquisition**
and the exact projected scale is reported to GPT/project lead. The corpus is
NOT built/accepted (`CANONICAL_CORPUS_IDENTITY=NONE`). All definition,
metadata, storage, engine, and identity work is committed on
`ds/canonical-dataset-build` so the build can proceed immediately once the
scale decision is made. No paid continuity is authorized.

## 9. Quality / cross-source tooling

`src/cross_source_check.py` — per concrete-contract/day classification
(MATCH / MISMATCH / NOT_COMPARABLE / NOT_AVAILABLE) for open/high/low/close/
volume/open interest where semantics match; conflicts never averaged; mismatches
remain durable evidence. Implemented + tested with deterministic fixtures; not
run against a built corpus (none built).

## 10. Canonical corpus identity

`src/canonical_identity.py` — immutable CanonicalCorpusIdentity binds approved
source identity, product universe, coverage, inventory rule, raw manifest root,
governed metadata root, normalizer/schema, Parquet storage version, accepted
partition identities, quality and cross-source summaries. Not minted for the
corpus yet (`CANONICAL_CORPUS_IDENTITY=NONE` because no corpus is built).
Building/acquiring the corpus does NOT expose it to any strategy lineage; no
development/validation/final-unseen split is created.

## 11. Honest status

The deterministic canonical-data work is complete and verified. The large raw
acquisition is gated by the Owner's scale guardrail and is reported to the
project lead. This package does not fake success and does not mark the
canonical dataset built or accepted.

```text
FINAL=OWNER_GATE
CANONICAL_CORPUS_IDENTITY=NONE
PROJECTED_RAW_GB=2.615
PROJECTED_BARS=15445905
PROJECTED_TRADED_PARTITIONS=32841
PAID_CONTINUITY_AUTHORIZED=NO
```

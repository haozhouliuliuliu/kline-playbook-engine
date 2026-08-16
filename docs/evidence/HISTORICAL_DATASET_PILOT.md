# Historical Dataset Acquisition Pilot

PILOT_ONLY=YES
TQSDK_STATUS=VERIFIED
TQSDK_ADOPTED=NO
CANONICAL_DATASET_ACCEPTED=NO
STRATEGY_RESEARCH_STARTED=NO

Verification time: `2026-08-16T14:20:00Z`
Starting HEAD: `53339c4f06efe5272261e7cc3fd00de76a6f5929` (branch `ds/canonical-dataset-pilot`)
Formal next action (unchanged): `CANONICAL_RESEARCH_DATASET_BUILD_AND_SOURCE_ACCEPTANCE_PACKAGE`

## Purpose

This is a bounded capability pilot, not source adoption and not the formal
canonical research dataset package. It demonstrates that the previously
verified single-day TqSdk real-data path generalizes into a small reusable,
project-owned acquisition boundary with a deterministic dataset manifest,
idempotent resume, real quality validation, and SHFE cross-source sampling.

No strategy research, parameter search, final-unseen use, Shadow/live trading,
broker/order API, or paid purchase/subscription occurred. No credentials were
stored in the repo, config, evidence, logs, or manifests; the TqSdk account
password was entered locally with hidden input and existed only in memory.

## Acquisition boundary (project-owned)

- `src/historical_acquisition.py`:
  - `SourceAdapter` ABC + `TqSdkSourceAdapter` (TqSdk imported lazily and only
    in the adapter; project runtime does not depend on TqSdk);
  - `AcquisitionRequest` (concrete contracts only; pseudo MAIN/CONTINUOUS and
    non-concrete symbols are rejected by `validate_concrete_symbol`);
  - `DatasetBuilder` (idempotent resume, atomic raw writes via `.partial` +
    rename, no download manager);
  - `credentials_from_terminal` (hidden `getpass`; no persistence).
- `src/historical_manifest.py`:
  - `ManifestPartition` and `DatasetManifest` with deterministic ordering and a
    stable manifest identity; corrupt or tampered manifests fail closed.
- Existing vendor-neutral `SourceIdentity` / `RawArtifact` / `NormalizerIdentity`
  / `DataVersionIdentity` in `src/historical_data.py` remain authoritative and
  unchanged; the builder calls them directly.

## Pilot sample

Two SHFE commodity products, chosen only for data availability,
concrete-contract lifecycle, session coverage, official cross-check
availability, and engineering diversity (different tick size and different
night-session length). No profitability/strategy relevance.

| Contract | Tick | Night session | Days | Bars/day | Partitions |
| --- | --- | --- | --- | --- | --- |
| `SHFE.ni2509` (nickel) | 10 | 21:00-01:00 | 2025-06-16..06-20 | 465 | 5 |
| `SHFE.rb2510` (rebar) | 1 | 21:00-23:00 | 2025-06-16..06-20 | 345 | 5 |

Total: 10 concrete-contract/date partitions, 4050 one-minute bars,
~708 KB raw. Raw files are in the ignored `data/raw/historical/` location
(`SHFE.<contract>.60s.<trading-day>.json`) and are not committed.

Actual TqSdk version used: `3.10.1` (isolated reversible venv at
`%LOCALAPPDATA%\Temp\kline-playbook-tqsdk-probe\`; not added to project
dependencies).

## Manifest

`docs/evidence/HISTORICAL_DATASET_PILOT.manifest.json`

- `MANIFEST_IDENTITY=eb20798fcfcf95cff1fcc2131284f8fa3c9e1b3b797ccc4c340dad78cafc037c`
- `schema_version=kline-playbook-dataset-manifest-v1`
- Every partition binds: provider (`TQSDK`), api version (`3.10.1`), contract,
  exchange, requested coverage, returned coverage, granularity (`60`),
  retrieval timestamp, raw byte size, raw SHA256, request identity (no auth),
  normalizer identity, session metadata version, `DataVersionIdentity`,
  normalized batch identity, and quality status.
- Ordering is deterministic (sorted by contract/requested start); repeated
  manifest construction over identical raw artifacts yields the identical
  identity. A corrupt/tampered manifest fails closed on load.

## Quality gates

All 10 partitions passed the existing project-owned normalization and quality
path (`normalize_tqsdk_historical_bars` with per-contract session metadata and
minimum tick). Every partition `quality_status=PASS`.

Verified on every partition: concrete-contract identity; timezone-aware
timestamps; deterministic strict chronology; duplicate/out-of-order rejection;
positive, tick-compatible OHLC; non-negative volume/OI; `SessionMetadata`
trading-day assignment (night session attributed to the correct trading day);
expected recess vs unexpected gap (all expected bars present,
`missing_expected_starts=[]`); no interpolation/forward fill;
`available_at = start + 60 s` PIT; raw SHA256 binding; repeat normalization
identity (deterministic `DataVersionIdentity`).

## Cross-source sampling

`docs/evidence/HISTORICAL_DATASET_PILOT.cross_source.json`

Daily aggregates from the 10 pilot partitions were compared against the SHFE
official 2025-06 workbook daily references (read-only reference extraction).

| Result | Count |
| --- | --- |
| MATCH | 10 |
| MISMATCH | 0 |
| NOT_COMPARABLE | 0 |
| NOT_AVAILABLE | 0 |

Every compared partition matched the official daily reference exactly on open,
high, low, close, volume, and open interest. No providers were averaged; there
were no mismatches to preserve or explain. The `ni2509` 2025-06-16 row also
matches the previously committed independent reference.

## Idempotent resume

The builder was rerun over the completed pilot. It re-acquired nothing, made no
TqSdk connection, required no credential input, and produced the identical
manifest identity (`eb20798f...`). Raw writes are atomic (temp + rename);
interrupted `.partial` files are never accepted as complete; a conflicting raw
file for a recorded partition fails closed (`RawPartitionConflictError`).

## Anomalies

No data anomalies were found. One transient TLS/network error occurred on the
earlier feasibility full-day probe (`SSL: UNEXPECTED_EOF_WHILE_READING`
against the TqSdk name service); it was a connection-setup hiccup, not an
authentication or entitlement failure, and a bounded connect retry succeeded.
The pilot run itself connected cleanly.

## Storage / tool conclusion

`TOOL_DECISION=USE_EXISTING`

The pilot uses stdlib JSON raw files (ignored) plus committed JSON manifest and
cross-source artifacts, with the existing project modules. This is adequate for
a small pilot.

Recorded capability gap for the full canonical dataset (not resolved here):
- no columnar storage for large normalized bars (Parquet candidate);
- no analysis/query engine (DuckDB optional candidate);
- no durable ledger/metadata store (SQLite candidate).

These remain `CANDIDATE` in `TOOL_REGISTRY.md` and are **not** installed by this
pilot. Recommendation for project-lead review at the formal
`CANONICAL_RESEARCH_DATASET_BUILD_AND_SOURCE_ACCEPTANCE_PACKAGE`: evaluate a
SQLite-backed manifest/ledger and Parquet normalized storage, with DuckDB only
if a real analysis need appears.

## Limitations

- Pilot scope only: 2 products, 5 days each, one granularity, mid-June 2025.
- TqSdk remains `VERIFIED`, not `ADOPTED`; it is not frozen as the permanent
  canonical source.
- The formal next action is unchanged and is not started here.
- Raw data is not committed; the committed manifest/cross-source JSON are the
  durable non-secret records.
- Session metadata for the pilot is contract-specific and hand-defined; the
  formal dataset package must establish a governed session metadata source.

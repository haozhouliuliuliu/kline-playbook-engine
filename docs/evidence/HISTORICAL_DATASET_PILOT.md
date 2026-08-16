# Historical Dataset Acquisition Pilot (Hardened)

PILOT_ONLY=YES
TQSDK_STATUS=VERIFIED
TQSDK_ADOPTED=NO
CANONICAL_DATASET_ACCEPTED=NO
STRATEGY_RESEARCH_STARTED=NO

Verification time: `2026-08-16T15:10:00Z`
Starting pilot HEAD (v1): `40530abed9cd80d15a7b02e8f455288b92a1ae2c`
Hardening HEAD: this commit on `ds/canonical-dataset-pilot`
Formal next action (unchanged): `CANONICAL_RESEARCH_DATASET_BUILD_AND_SOURCE_ACCEPTANCE_PACKAGE`

## Purpose

This is a bounded capability pilot, not source adoption and not the formal
canonical research dataset package. It demonstrates that the previously
verified single-day TqSdk real-data path generalizes into a small reusable,
project-owned acquisition boundary with a deterministic dataset manifest,
idempotent resume, real quality validation, and SHFE cross-source sampling.

This revision incorporates the GPT/project-lead review of pilot v1. The
original v1 design issues are not hidden; each finding and its resolution is
recorded below.

No strategy research, parameter search, final-unseen use, Shadow/live trading,
broker/order API, or paid purchase/subscription occurred. No credentials were
stored in the repo, config, evidence, logs, or manifests; the TqSdk account
password was entered locally with hidden input and existed only in memory.

## GPT/project-lead review findings and resolutions

1. **False vendor-neutrality.** v1 `DatasetBuilder` hard-coded TQSDK
   provider/source/endpoint and called the TqSdk normalizer directly.
   Resolved: `SourceSpecification` (provider, source type, endpoint, raw
   schema, version, normalizer, availability rule, request parameter names) and
   `decode()` now come from the adapter; `DatasetBuilder` is generic. A
   non-TqSdk `FakeAdapter(provider="FAKE")` test proves the manifest carries
   `FAKE` provenance and never `TQSDK`.
2. **Calendar inference.** v1 runner inferred "Monday night = prior Friday
   evening" from weekdays. Resolved: no weekday/weekend/holiday inference
   exists in the foundation or runner; runtime consumes only explicit, versioned
   `SessionMetadata` from the committed PILOT_FIXTURE
   `HISTORICAL_DATASET_PILOT.sessions.json`. The 10 real partitions' session
   windows are explicit facts in that fixture, labeled `PILOT_FIXTURE` (not
   claimed as official authority).
3. **Contract metadata evidence binding.** v1 used free-form labels such as
   `shfe-ni2509-contract-v1`. Resolved: `ContractMetadataFact` produces a
   deterministic identity binding exchange, concrete contract, minimum tick,
   effective period, session metadata version, evidence reference, and an
   honest `VERIFIED_OFFICIAL`/`PILOT_FIXTURE` classification. The pilot facts
   are classified `PILOT_FIXTURE`; nothing unverified is claimed as official.
4. **Partition identity / resume collision.** v1 key omitted `requested_end`
   and timezone. Resolved: partition key is now
   (provider, contract, granularity, timezone, trading day, requested_start,
   requested_end); raw filenames are provider+coverage-tag collision-safe.
   Same start + different end (and vice versa), different provider, and
   timezone changes cannot silently skip; they create distinct partitions or
   fail closed. Tests cover each case.
5. **Retry classification.** v1 retried any exception up to three times.
   Resolved: `is_transient_network_error` + `retry_decision` only retry clearly
   transient transport/network failures (requests/urllib3 transport errors and
   builtin connection/timeout), bounded. Authentication/entitlement/
   configuration failures fail closed with no retry. Deterministic
   dependency-injection tests prove auth-style failures get one attempt and
   transient failures are bounded (no infinite retry).
6. **Cross-source evidence binding.** v1 said only "SHFE official workbook".
   Resolved: `HISTORICAL_DATASET_PILOT.cross_source.json` (schema v2) durably
   binds the TqSdk manifest identity, per-partition data-version/raw hashes,
   the committed SHFE recheck manifest SHA256, the official ZIP SHA256, and the
   exact workbook member SHA256. 10 MATCH / 0 MISMATCH / 0 NOT_COMPARABLE /
   0 NOT_AVAILABLE were re-validated from the on-disk raw (no re-download).
7. **Manifest hardening.** The manifest now fails closed on: wrong recorded
   identity; duplicate logical partitions; request identity conflicting with
   declared request parameters; request parameters contradicting declared
   coverage/contract; sensitive parameter names; returned coverage outside
   requested coverage.
8. **Pilot evidence.** This document truthfully records the findings above.
9. **Source-acceptance preparation.** `SOURCE_ACCEPTANCE_RECOMMENDATION` below
   is a technical recommendation only; it is not an adoption decision.
10. **Verification.** See the verification section below.
11. **Git.** One coherent hardening commit on `ds/canonical-dataset-pilot`;
    `main` remains at `53339c4f06efe5272261e7cc3fd00de76a6f5929`.

## Acquisition boundary (project-owned)

- `src/historical_acquisition.py`:
  - `SourceSpecification` (immutable source/provider facts) and
    `SourceAdapter` ABC (`source_specification`, `acquire`, `decode`, `close`);
  - `TqSdkSourceAdapter` (TqSdk imported lazily; only transient network errors
    are retried, bounded; `decode` owns the TqSdk normalization);
  - `AcquisitionRequest` (concrete contracts only; pseudo MAIN/CONTINUOUS and
    non-concrete symbols rejected by `validate_concrete_symbol`);
  - `ContractMetadataFact` + `ContractConfig` (evidence-bound metadata);
  - `DatasetBuilder` (generic idempotent resume, atomic raw writes via
    `.partial` + rename, no download manager, no provider hard-coding);
  - `credentials_from_terminal` (hidden `getpass`; no persistence).
- `src/historical_manifest.py`:
  - `ManifestPartition` / `DatasetManifest` with deterministic ordering,
    provider-aware partition keys, and fail-closed hardening (findings 4, 7).
- Existing vendor-neutral `SourceIdentity` / `RawArtifact` / `NormalizerIdentity`
  / `DataVersionIdentity` in `src/historical_data.py` remain authoritative and
  unchanged.

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
~708 KB raw. Raw files are in the ignored `data/raw/historical/` location with
collision-safe names
(`<provider>.<contract>.<granularity>s.<trading-day>.<coverage-tag>.json`) and
are not committed.

Session windows are defined explicitly in
`docs/evidence/HISTORICAL_DATASET_PILOT.sessions.json` (classified
`PILOT_FIXTURE`, not official session authority). Actual TqSdk version used:
`3.10.1` (isolated reversible venv at
`%LOCALAPPDATA%\Temp\kline-playbook-tqsdk-probe\`; not added to project
dependencies).

## Manifest

`docs/evidence/HISTORICAL_DATASET_PILOT.manifest.json`

- `MANIFEST_IDENTITY=cdbaae338707f5e77182274e5ee162b6015228f34c84f35d4a148a543dc38f03`
- `schema_version=kline-playbook-dataset-manifest-v2` (hardened schema; v1 was
  `...-v1` with identity `eb20798f...`). The raw data and raw SHA256 values are
  preserved; the manifest identity changed because the schema and the
  evidence-bound contract metadata identity changed.
- Every partition binds: provider (`TQSDK`), api version (`3.10.1`), contract,
  exchange, granularity (`60`), timezone, trading day, requested coverage,
  returned coverage, retrieval timestamp, raw byte size, raw SHA256, request
  identity (no auth), request parameters, normalizer identity, session metadata
  version, contract metadata identity (evidence-bound), `DataVersionIdentity`,
  normalized batch identity, and quality status.
- Ordering is deterministic and repeated construction over identical raw
  artifacts yields the identical identity. A corrupt, tampered, inconsistent,
  or duplicate-partition manifest fails closed on load.

## Quality gates

All 10 partitions passed the existing project-owned normalization and quality
path (`normalize_tqsdk_historical_bars` with per-contract explicit session
metadata and minimum tick). Every partition `quality_status=PASS` in the
hardened manifest (re-validated during migration; no data was re-downloaded).

Verified on every partition: concrete-contract identity; timezone-aware
timestamps; deterministic strict chronology; duplicate/out-of-order rejection;
positive, tick-compatible OHLC; non-negative volume/OI; `SessionMetadata`
trading-day assignment (night session attributed to the correct trading day);
expected recess vs unexpected gap (all expected bars present,
`missing_expected_starts=[]`); no interpolation/forward fill;
`available_at = start + 60 s` PIT; raw SHA256 binding; repeat normalization
identity (deterministic `DataVersionIdentity`).

## Cross-source sampling

`docs/evidence/HISTORICAL_DATASET_PILOT.cross_source.json` (schema v2)

Durably binds: the TqSdk manifest identity
`cdbaae338707f5e77182274e5ee162b6015228f34c84f35d4a148a543dc38f03`, each
compared partition's `data_version_id` and `raw_sha256`, the committed SHFE
recheck manifest (`docs/evidence/SHFE_OFFICIAL_RAW_RECHECK_MANIFEST.json`,
SHA256 recorded in the cross-source file), the official ZIP SHA256
(`af199136...`), and the exact workbook member SHA256.

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

The hardened builder was rerun over the completed pilot. It re-acquired
nothing, made no TqSdk connection, required no credential input, and produced
the identical hardened manifest identity (`cdbaae33...`). Raw writes are atomic
(temp + rename); interrupted `.partial` files are never accepted as complete; a
conflicting raw file for a recorded partition fails closed
(`RawPartitionConflictError`); a changed request (same start + different end,
same end + different start, different provider, or timezone change) is never
silently skipped.

## Anomalies

No data anomalies were found. One transient TLS/network error occurred on the
earlier feasibility full-day probe (`SSL: UNEXPECTED_EOF_WHILE_READING`
against the TqSdk name service); it was a connection-setup hiccup, not an
authentication or entitlement failure, and the bounded connect retry succeeded.
The pilot runs connected cleanly.

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
- Session and contract metadata are classified `PILOT_FIXTURE`; they are not
  official session/contract authority and must be governed/verified before a
  canonical dataset is built.
- TqSdk remains `VERIFIED`, not `ADOPTED`; it is not frozen as the permanent
  canonical source.
- The formal next action is unchanged and is not started here.
- Raw data is not committed; the committed manifest/cross-source JSON are the
  durable non-secret records.

## SOURCE-ACCEPTANCE RECOMMENDATION (technical, not a decision)

`SOURCE_ACCEPTANCE_RECOMMENDATION=ACCEPT_TQSDK_AS_CANONICAL_CANDIDATE`

Rationale (technical only): the current Owner trial authenticated, real
concrete-contract intraday data was returned, provenance/raw hashes were
recorded, real data passed the existing normalization path and PIT
normalization, all real quality gates passed, and the SHFE cross-source check
matched exactly (10/10) against a durable official reference. TqSdk is
therefore a technically suitable canonical-research-data candidate.

Caveats before any formal adoption decision: session/contract metadata are
`PILOT_FIXTURE` (official session/tick verification recommended), only 2
products / 5 trading days / one period were tested, and a governed session
metadata source is required. This is only a recommendation; the final source
adoption decision remains with GPT/project lead and, as applicable, the Owner.
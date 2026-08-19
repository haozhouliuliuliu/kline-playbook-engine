# PACKAGE_D_CANONICAL_COMPLETENESS_PROVENANCE_ENGINEERING_V0_1

> Date: 2026-08-20
> Role: Package D repair worker (production repair, not a preflight probe)
> Task: `PACKAGE_D_CANONICAL_COMPLETENESS_PROVENANCE_V0_1`
> Spec: `docs/reviews/PARALLEL_PACKAGE_C_D_F_ACTUAL_REPAIR_SPEC_V0_1.md` (Package D)
> Parent audit: `docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md` (Part C, D-01..D-08)
> Preflight: `prep/package-d-canonical-reproduction-v01` @ `8ffea4472cdd24257b612c5a9050bff9f567ec8a` (D-01..D-08 reproduced)
> Branch: `repair/package-d-canonical-provenance-v01`
> Baseline: latest `origin/main`
> Baseline HEAD: `e8ccab103a43c464aef6cc02f9566083e7acd922`

## Scope and constraints honored

- D-01..D-08 fixed together in this one package; no D1/D2/D3 multi-round split.
- No canonical corpus was rebuilt; `CANONICAL_CORPUS_IDENTITY` unchanged.
- No acceptance result was rewritten; `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md` untouched.
- No claim is made that existing accepted OHLC prices are wrong; no concrete-contract mapping rule or candidate data changed.
- No real 2024/2025 candidate market corpus was read; all tests use synthetic in-memory / temp-dir fixtures.
- `CURRENT_STATE.md` was not modified (integration-owned authority).
- No merge/push of `main`.

## Fix inventory (D-01..D-08)

### D-01 — truncated coverage can never be PASS

- `ManifestPartition.__post_init__` (`src/historical_manifest.py`) now fails closed when `quality_status == "PASS"` and `returned_start != requested_start` or `returned_end != requested_end`. A partial returned response may still be recorded, but never as PASS (enforced at construction and at load).
- `DatasetBuilder._acquire_partition` (`src/historical_acquisition.py`) computes quality from the actual returned coverage vs requested coverage: truncated coverage yields `ANOMALY:returned_coverage_truncated[...]`, never PASS, and never stretches returned coverage to look like requested coverage.
- `reevaluate_manifest` (`tools/build_canonical_dataset.py`) uses the same non-PASS quality rule.
- Tests: `tests/test_package_d_canonical_repair.py::D01TruncatedCoverageCannotBePASSTests`.

### D-02 — expected completeness enumerated from session authority

- `SessionMetadata.expected_bar_starts_between(exchange, instrument, coverage_start, coverage_end, interval)` added (`src/data_substrate.py`): enumerates every expected complete bar start directly from the authoritative session windows over a declared coverage range, independent of observed bars.
- `normalize_tqsdk_historical_bars` (`src/historical_data.py`) now computes `missing = expected - observed` over the whole artifact coverage from session authority, instead of only iterating `observed_by_day`. An entirely absent session window that the artifact coverage claims now enters missing evidence. A fully empty raw payload remains invalid and can never PASS; no synthetic bars are generated.
- Tests: `tests/test_package_d_canonical_repair.py::D02SessionAuthorityCompletenessTests`.

### D-03 — canonical raw artifact identity

- `normalize_and_store_partition` (`tools/build_canonical_dataset.py`) now sets `CanonicalRow.raw_artifact_identity_id = bar.raw_artifact_identity_id` (the `RawArtifact.identity_id` carried by the normalized bar), never `partition.raw_sha256`. Raw SHA remains a separate provenance fact.
- Tests: `tests/test_package_d_canonical_repair.py::D03RawArtifactIdentityTests` (row semantics + end-to-end builder via pyarrow).

### D-04 — missing volume is not zero

- `CanonicalRow.volume` is now `int | None` (`src/canonical_storage.py`): `None` is valid (unknown/missing) and preserved into Parquet; non-None must be a non-negative integer.
- Canonical schema definition documents `volume` as `int64 nullable`; the PyArrow schema is already nullable int64.
- Builder conversion (`tools/build_canonical_dataset.py`) preserves `None -> None`, never `None -> 0`.
- Tests: `tests/test_package_d_canonical_repair.py::D04NullableVolumeTests` (incl. pyarrow-gated write/read round-trip).

### D-05 — SessionMetadata content identity

- `SessionMetadata.__init__(authority_reference, windows)` (`src/data_substrate.py`) now computes its public `version` (and `identity` alias) deterministically as a hash of `authority_reference` + canonical exact windows `(exchange, instrument, trading_day, start, end, kind)`. Same caller label + different windows can no longer share a version.
- `build_session_metadata` (`src/metadata_authority.py`) supplies an authority reference binding `TradingCalendar.identity()`, `ProductSessionSchedule.identity()`, concrete contract, and the effective night-closed day set (explicit override when supplied), so calendar/night-closed fact changes change the identity.
- No metadata registry was created; downstream consumers (`DataVersionIdentity`, manifest, round-trip future consumers) use the computed `SessionMetadata.version`.
- Downstream builders/tests migrated to the computed identity (`tools/pilot_build_dataset.py`, `tests/test_historical_data.py`, `tests/test_historical_acquisition.py`).
- Tests: `tests/test_package_d_canonical_repair.py::D05SessionMetadataContentIdentityTests`.

### D-06 — metadata byte provenance is explicit

- `GovernedSource` (`src/metadata_authority.py`) now binds one or more exact artifact SHA256 values: `artifact_sha256s` (tuple) in addition to the retained single `artifact_sha256` form. All exact hashes are canonical sorted unique and participate in the source identity; changing one bound hash changes the identity.
- `OFFICIAL_AVAILABLE` / `ARCHIVED_OFFICIAL` require at least one exact artifact hash; sources without recorded exact bytes must be explicitly `OFFICIAL_PARTIAL` or `PENDING_OFFICIAL_BINDING` and can never pretend to be exact-byte-bound.
- Loaders (`tools/build_canonical_dataset.py`):
  - calendar: binds the committed per-year `artifact_sha256s` (2024/2025) from `CANONICAL_TRADING_CALENDAR.json` → `OFFICIAL_AVAILABLE` byte-bound;
  - session schedules / contract specs: no historical byte hash exists in committed evidence → explicitly `OFFICIAL_PARTIAL`, no invented hash, no re-download.
- No external refetch; no canonical acceptance rewrite. Future canonical identities may change when a corpus is rebuilt; committed acceptance evidence is not rewritten.
- Tests: `tests/test_package_d_canonical_repair.py::D06GovernedSourceByteProvenanceTests`.

### D-07 — mixed partition write is rejected before any file is written

- `write_partition_table` (`src/canonical_storage.py`) now computes `(exchange, product, concrete_contract, year, month)` for every row and raises `ValueError` unless all rows map to exactly one logical partition — before any parquet file is written. No post-write root scan is used to repair inventory.
- Tests: `tests/test_package_d_canonical_repair.py::D07MixedPartitionWriteTests` (asserts no `.parquet` produced on failure).

### D-08 — TqSdk runtime mismatch diagnostic preserves the actual version

- `TqSdkSourceAdapter._check_runtime_version` (`src/historical_acquisition.py`) captures the actual runtime version in a local variable before clearing/resetting adapter state, and reports that real wrong version in the error message (never `None`).
- Tests: `tests/test_package_d_canonical_repair.py::D08RuntimeVersionDiagnosticTests`.

## Focused regression tests

`tests/test_package_d_canonical_repair.py` — 22 focused tests covering D-01..D-08 with synthetic/temp fixtures only; Parquet-dependent assertions are capability-gated on pyarrow (skip in a stdlib-only environment).

- D01: truncated PASS constructor fail; builder no longer emits truncated PASS; full-coverage PASS still accepted.
- D02: two session windows, second with zero bars, artifact coverage covers both → missing evidence includes the second window; same-day in-window gaps still reported.
- D03: `RawArtifact.identity_id != raw_sha`; canonical row stores identity_id (row + pyarrow-gated builder end-to-end).
- D04: `volume=None` write/read stays `None`; zero/positive valid; negative fails.
- D05: same authority label + different windows → different version; calendar/night-closed fact changes change identity; deterministic.
- D06: changing one bound hash changes identity; multi-hash canonical sorted unique; `OFFICIAL_AVAILABLE` without hash fails; no-hash sources explicitly partial/not byte-bound.
- D07: mixed partition rejected before any file written; temp root produces no parquet; single partition unaffected.
- D08: mismatch error contains the real wrong version (`9.9.9`), adapter state cleared.

## Validation

- Focused tests: `python -m unittest tests.test_package_d_canonical_repair -v` → 22 tests OK (pyarrow 25.0.1 available).
- Full default suite: `python -m unittest discover -s tests -v` → 378 tests OK (was 356 pre-repair on this baseline), pyarrow capability exercised in this environment.
- `python -m compileall -q src tools tests` → clean.
- `git diff --check` → clean.
- D-06 loader smoke check against committed evidence: calendar `OFFICIAL_AVAILABLE` with both per-year hashes bound; schedules/specs `OFFICIAL_PARTIAL`; `SessionMetadata.version` is a 64-char content identity.

## Boundaries preserved

```text
CANONICAL_CORPUS_REBUILT=NO
CANONICAL_ACCEPTANCE_REWRITTEN=NO
REAL_CANDIDATE_DATA_USED=NO
CURRENT_STATE_CHANGED=NO
CONCRETE_CONTRACT_MAPPING_RULE_CHANGED=NO
CANDIDATE_DATA_CHANGED=NO
```

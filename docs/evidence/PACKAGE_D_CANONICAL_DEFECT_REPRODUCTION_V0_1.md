# PACKAGE_D_CANONICAL_DEFECT_REPRODUCTION_V0_1

> Date: 2026-08-20
> Role: preflight reproduction worker (NOT the Package D fix engineer)
> Task: `PACKAGE_D_PREFLIGHT_CANONICAL_DEFECT_REPRODUCTION_V0_1`
> Scope: prove each of D-01..D-08 from `docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md` (Part C) on the current real code. No repair, no redesign, no corpus rebuild, no real-data read.
> Branch: `prep/package-d-canonical-reproduction-v01`
> Baseline: `origin/main`
> Baseline HEAD: `07b84958c96db85f7a984a1e7712be5ba37d65d0`
> Diagnostic tool: `tools/reproduce_package_d_findings.py`

## Methodology and constraints honored

- Only D-01..D-08 were investigated. No other findings were studied.
- Every dynamic reproduction used synthetic in-memory fixtures or temporary directories. No 2024/2025 real candidate market corpus was read.
- No production source file was modified.
- No canonical corpus was rebuilt; no data registry was created; no `DatasetBuilder` was refactored; no metadata model was rewritten.
- No failing test was added to the default suite (`python -m unittest discover -s tests` remains green at 318 tests / OK).
- The diagnostic tool always exits 0; per-finding outcomes are reported as `REPRODUCED` / `AUDIT_FINDING_INACCURATE` / `NOT_REPRODUCED` / `REPRO_ERROR`.

---

## D-01 — Acquisition may mark a truncated returned coverage as PASS

- STATUS=REPRODUCED
- ROOT_FUNCTIONS:
  - `ManifestPartition.__post_init__` (`src/historical_manifest.py`): only enforces "returned coverage must lie within requested coverage", not equality with it.
  - `_reconstruct_and_normalize` / `normalize_and_store_partition` (`tools/build_canonical_dataset.py`): build `RawArtifact` with `coverage_start/end = partition.returned_start/end` (the returned, not requested, coverage).
  - `normalize_tqsdk_historical_bars` (`src/historical_data.py`): `covered_expected` filters expected starts to `artifact.coverage_start <= start and start + interval <= artifact.coverage_end`.
  - Quality expression `"PASS" if not batch.missing_expected_starts else ...` in `DatasetBuilder._acquire_partition` (`src/historical_acquisition.py`) and in `normalize_and_store_partition` / `reevaluate_manifest` (`tools/build_canonical_dataset.py`).
- MINIMAL_TRIGGER: requested interval `09:00 -> 09:10`; provider/manifest returns only `09:03 -> 09:10` (internally continuous bars); artifact coverage equals the returned coverage.
- ACTUAL_BEHAVIOR (measured): `missing_expected_starts == ()`, `quality == "PASS"`, and the manifest accepts the truncated returned coverage. The missing head `09:00..09:02` produces no evidence.
- EXPECTED_INVARIANT: a partition may be marked PASS only when the returned coverage equals the requested coverage (or, equivalently, when every requested-interval session bar is present); the missing computation must be performed over the full requested interval, never bounded by the returned coverage.
- BLAST_RADIUS: canonical acceptance completeness proof for the requested interval. Does not alter recorded OHLC values; it does not prove the accepted corpus is factually incomplete.
- FIX_DEPENDENCY: none (self-contained canonical-pipeline completeness logic; no Package B/C dependency).

## D-02 — Entirely absent trading days / session windows disappear from missing-bar evidence

- STATUS=REPRODUCED (two probes: absent window within a day, and fully absent expected day)
- ROOT_FUNCTIONS:
  - `normalize_tqsdk_historical_bars` (`src/historical_data.py`): missing starts are computed only from `observed_by_day.items()` — a day/window with zero observed bars is never enumerated.
  - `NormalizedHistoricalBatch.__post_init__` (`src/historical_data.py`): requires at least one bar, so a fully-empty expected day cannot even be represented as a batch.
- MINIMAL_TRIGGER: `SessionMetadata` declares two windows `09:00-09:05` and `10:00-10:05`; the input contains only the first window's complete bars; returned coverage spans only the first window. (Second probe: an expected trading day with zero observed bars at all.)
- ACTUAL_BEHAVIOR (measured): the second window produces zero missing evidence (`missing_expected_starts == ()`). The existing `SessionMetadata.missing_bar_starts(...)` API *can* express the absent window/day (returns all expected starts when given `observed_starts=()`), but the normalizer never calls it for days/windows with no observed bars. A fully-empty expected day has no evidence object at all.
- EXPECTED_INVARIANT: missing-bar evidence must be enumerated for every expected trading day/window declared by session authority (via `SessionMetadata.expected_bar_starts`), regardless of whether any bar was observed.
- BLAST_RADIUS: canonical completeness evidence only; same root failure mode later reproduced in Lane G completeness defects (L-06/L-07). No market-value impact.
- FIX_DEPENDENCY: none.

## D-03 — Canonical stored `raw_artifact_identity_id` is the raw SHA, not `RawArtifact.identity_id`

- STATUS=REPRODUCED
- ROOT_FUNCTIONS (exact assignment chain):
  1. `src/historical_data.py` → `normalize_tqsdk_historical_bars`, `bars.append(...)`: `NormalizedHistoricalBar.raw_artifact_identity_id = artifact.identity_id` (correct semantic — `RawArtifact.identity_id`).
  2. `tools/build_canonical_dataset.py` → `normalize_and_store_partition`: `CanonicalRow(..., raw_artifact_identity_id=partition.raw_sha256, ...)` (defect — stores the raw byte SHA).
- MINIMAL_TRIGGER: any accepted partition reaching canonical storage (identity_id != raw_sha256 always holds by construction).
- ACTUAL_BEHAVIOR (measured): `CanonicalRow.raw_artifact_identity_id == raw_sha256`, and `!= artifact.identity_id` and `!= NormalizedHistoricalBar.raw_artifact_identity_id`. Example: `raw_sha256=d51edc43…`, `RawArtifact.identity_id=ce140f01…`.
- EXPECTED_INVARIANT: `CanonicalRow.raw_artifact_identity_id` must equal the `RawArtifact.identity_id` carried by `NormalizedHistoricalBar.raw_artifact_identity_id` (`artifact.identity_id`), not the raw byte SHA.
- BLAST_RADIUS: the provenance-meaning of the identity column in canonical Parquet rows; OHLC values are not altered. Accepted-corpus rows carry the same mismatch by the same code path (no corpus re-read required to know the column is populated from `partition.raw_sha256`).
- FIX_DEPENDENCY: none.

## D-04 — Missing normalized volume is silently stored as zero

- STATUS=REPRODUCED (generic canonical path)
- ROOT_FUNCTIONS:
  - `tools/build_canonical_dataset.py` → `normalize_and_store_partition`: `volume=int(bar.volume) if bar.volume is not None else 0`.
  - `CanonicalRow.__post_init__` (`src/canonical_storage.py`): accepts `0` (non-negative int), so the collapse passes validation.
- MINIMAL_TRIGGER: a normalized bar with `volume is None` (e.g., a raw record with no `volume` field) reaching canonical row conversion.
- ACTUAL_BEHAVIOR (measured): `NormalizedHistoricalBar.volume=None` → `CanonicalRow.volume == 0` → stored parquet `volume == 0`. Unknown/missing volume is collapsed into known zero volume.
- EXPECTED_INVARIANT: a `None`/missing volume must remain distinguishable from a real zero in canonical storage (nullable int64 volume column or an explicit missing indicator).
- BLAST_RADIUS: the generic canonical path is unsafe for missing volume. Accepted 15,280,452-row impact = **NOT_ESTABLISHED** — no real corpus was read and the audit itself found no evidence that accepted TqSdk rows had missing volume.
- FIX_DEPENDENCY: none.

## D-05 — `SessionMetadata.version` does not uniquely bind actual session windows / calendar facts

- STATUS=REPRODUCED
- ROOT_FUNCTIONS:
  - `SessionMetadata.__init__` (`src/data_substrate.py`): `version` is an opaque required caller string with no binding to the actual `windows`.
  - `build_session_metadata` (`src/metadata_authority.py`): `SessionMetadata(schedule.identity(), windows)` — version comes from `ProductSessionSchedule.identity()`.
- MINIMAL_TRIGGER: (a) two `SessionMetadata` with different window sets but the same caller-supplied `version="same-version"`; (b) one `ProductSessionSchedule` identity used with two `TradingCalendar`s that differ only in the official night-closed set.
- ACTUAL_BEHAVIOR (measured): (a) both versions equal `"same-version"` while expected-start counts differ (60 vs 120); (b) `version == schedule.identity()` for both calendars while generated window counts differ (7 vs 6) because of the night-closed set. The version does not bind the concrete generated windows, `TradingCalendar` identity, or the night-closed-day set.
- EXPECTED_INVARIANT: the session metadata identity must be a deterministic hash of the actual generated windows plus the calendar/night-closed authority facts it was built from, so identical version ⇒ identical windows/calendar authority.
- BLAST_RADIUS: downstream code treats `session_metadata_version` as the session identity; the binding is weaker than the real authority surface. No price/data impact.
- FIX_DEPENDENCY: none.

## D-06 — Governed metadata sources are value-bound but not byte-bound

- STATUS=REPRODUCED (inventory only; nothing was re-downloaded, no hash was added)
- ROOT_FUNCTIONS:
  - `load_calendar`, `load_schedules`, `load_specs` (`tools/build_canonical_dataset.py`): construct `GovernedSource(..., artifact_sha256=None, ...)` for calendar/schedule/spec.
  - `GovernedSource` (`src/metadata_authority.py`): models a single `artifact_sha256: str | None`; cannot carry the calendar's per-year hash set.
- MINIMAL_TRIGGER: any canonical build / identity computation that consumes governed metadata.
- ACTUAL_BEHAVIOR (inventory from committed evidence JSON + current loaders):

  | metadata | URL / reference present | byte hash in committed JSON | runtime `artifact_sha256` | runtime byte-binding |
  |---|---|---|---|---|
  | trading_calendar | yes | yes (per-year `artifact_sha256s` 2024/2025) | `None` | NOT_BYTE_BOUND |
  | session_schedules | yes (`source_url`) | no | `None` | NOT_BYTE_BOUND |
  | contract_specs | yes (`source_url`) | no (no `content_hash`) | `None` | NOT_BYTE_BOUND |
  | contract_universe | yes (`source.url`) | yes (per-year `artifact_sha256s`) | no runtime `GovernedSource` at all | NOT_BYTE_BOUND |

  Note: calendar/universe committed JSON *does* record per-year hashes, but the current runtime model/loaders bind no byte hash (single-sha field, set to `None`). Schedules/specs have no committed byte hash at all.
- EXPECTED_INVARIANT: every governed metadata source that enters a canonical identity must bind the exact retrieved official source bytes (single hash or a governed per-year hash set), or be explicitly classified as not byte-bound.
- BLAST_RADIUS: `governed_metadata_root_identity` and the corpus root identity bind modeled values + URLs, not exact official source bytes; metadata fact reproducibility.
- FIX_DEPENDENCY: none.

## D-07 — `write_partition_table` does not reject mixed logical partitions and under-reports inventory

- STATUS=REPRODUCED
- ROOT_FUNCTIONS: `write_partition_table` (`src/canonical_storage.py`): writes via `pq.write_to_dataset(..., partition_cols=PARTITION_COLUMNS)` but builds the returned file inventory only from `sample = row_list[0]`'s partition directory.
- MINIMAL_TRIGGER: one call with rows spanning two different logical hive partitions (e.g., `product=ni/year=2026/month=8` and `product=al/year=2026/month=9`).
- ACTUAL_BEHAVIOR (measured, temp dir): both partition directories are actually written (2 files across 2 partitions), but the returned `files` inventory contains only the first-row partition's file (1 file). The second partition is missing from the reported inventory.
- EXPECTED_INVARIANT: the returned inventory must cover every partition directory actually written, or the function must reject mixed logical partitions (prefer the latter for a partition-oriented API).
- BLAST_RADIUS: storage inventory accuracy. The current canonical build calls it one manifest partition at a time, so accepted-build impact was **NOT_ESTABLISHED** (consistent with the audit).
- FIX_DEPENDENCY: none.

## D-08 — TqSdk runtime-version mismatch diagnostic loses the actual runtime version

- STATUS=REPRODUCED
- ROOT_FUNCTIONS: `TqSdkSourceAdapter._check_runtime_version` (`src/historical_acquisition.py`) — sets `self._version = None` *before* formatting the mismatch message.
- MINIMAL_TRIGGER: any runtime version different from `verified_runtime_version` (probe used `"WRONG_RUNTIME_9.9.9"` vs verified `"3.10.1"`).
- ACTUAL_BEHAVIOR (measured): error message is `TqSdk runtime version None does not match the verified compatibility version '3.10.1'; …` — the actual runtime version (`9.9.9`) is lost and printed as `None`. The existing test `test_connect_runtime_version_mismatch_fails_closed` only asserts `"does not match the verified"`, so it does not catch the loss.
- EXPECTED_INVARIANT: the mismatch diagnostic must report the actual captured runtime version (the value observed before reset), not `None`.
- BLAST_RADIUS: diagnostics/auditability only; no market-value impact.
- FIX_DEPENDENCY: none.

---

## Reproduction tool output (captured 2026-08-20)

```
D01=REPRODUCED
D02=REPRODUCED
D02b=REPRODUCED
D03=REPRODUCED
D04=REPRODUCED
D05=REPRODUCED
D06=REPRODUCED
D07=REPRODUCED
D08=REPRODUCED
```

(D02b is the supplementary "expected trading day with zero observed bars" minimal probe required by the task.)

## Verification performed

- `python tools/reproduce_package_d_findings.py` → all D-01..D-08 `REPRODUCED`, exit 0.
- `python -m unittest discover -s tests` → 318 tests, OK (3 skipped), unchanged from baseline.
- `git diff --check` → clean (see task report).

## Final status block

```text
PACKAGE_D_PRODUCTION_FIX_PERFORMED=NO
CANONICAL_CORPUS_REBUILT=NO
REAL_CANDIDATE_DATA_USED=NO
```

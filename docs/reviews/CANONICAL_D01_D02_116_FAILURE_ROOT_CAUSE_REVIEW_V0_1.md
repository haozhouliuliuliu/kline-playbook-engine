# CANONICAL_D01_D02_116_FAILURE_ROOT_CAUSE_REVIEW_V0_1

> Date: 2026-08-21
> Branch: `review/canonical-116-root-cause-v01`
> Baseline evidence commits: `a9e306550c5dc47695e4c27c1812de4c3cad5641` (revalidate), `e98df52a427a23c85fac70125a1f20dbd5f2a353` (qualify)
> Role: independent root-cause reviewer of the 116 canonical D-01/D-02 integrity failures
> Constraints: STRICTLY NO `main` writes; no TqSdk login; no re-download; no outcome access.

```text
STATUS=COMPLETE
DISTINCT_FAILED_CONTRACTS=116
FIRST_PARTITION_FAILURE_COUNT=116
FIRST_LISTING_DAY_COUNT=116
NIGHT_BOUNDARY_PATTERN_COUNT=116
ROOT_CAUSE_VERDICT=MIXED_ROOT_CAUSES
CRITICAL_FINDINGS=2
HIGH_FINDINGS=4
RECOMMENDED_REPAIR=RE_AUTHORIZE_TARGETED_REACQUISITION_WITH_FIRST_DAY_SCOPE_OR_GOVERNED_EXCEPTION
```

## 1. Scope and method

This review determines the root cause of the 116 canonical D-01 (`RETURNED_COVERAGE_TRUNCATED`)
/ D-02 (`MISSING_EXPECTED_BARS`) failures recorded in
`docs/evidence/CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json` and diagnosed in
`docs/evidence/CANONICAL_D01_D02_TARGETED_REPAIR_QUALIFICATION_V0_1.json`.

Method is strictly read-only and synthetic:

- accepted manifest: `C:\Users\H\Documents\kline-playbook-engine\data\canonical\manifest.json` (32,980 partitions);
- accepted raw historical JSON: `C:\Users\H\Documents\kline-playbook-engine\data\raw\historical\` (32,983 files);
- committed evidence JSON (revalidation, qualification, universe, session schedules, cross-source);
- source code: `src/historical_acquisition.py`, `src/data_substrate.py`, `src/metadata_authority.py`,
  `tools/build_canonical_dataset.py`, `tools/revalidate_canonical_corpus.py`,
  `tools/qualify_canonical_d01_d02_repair.py`.

No credentials, no login, no download, no outcome data were used. No corpus artifact was modified.

## 2. Verified deterministic facts

The following numbers were recomputed directly from the accepted manifest, raw files, and committed evidence:

| Fact | Value | Source of computation |
|---|---|---|
| failure_partitions count | 116 | revalidation JSON |
| distinct failed contracts | 116 (each exactly 1 failure) | manifest + revalidation |
| distinct (contract, trading_day) | 116 (no duplicates) | manifest + revalidation |
| failure == first manifest partition of its contract | 116/116 | manifest ordering |
| failure trading_day == governed first trading day | 116/116 | `CANONICAL_CONTRACT_UNIVERSE.json` |
| failure requested_start == prev-day 21:00 | 116/116 | revalidation JSON |
| all truncated partitions in corpus (any day) | 116 (exactly the failures) | manifest |
| requested-at-21:00 partitions with exact 21:00 return | 31,980 | manifest |
| requested-at-21:00 partitions with truncated return | 116 | manifest |
| failures with clean 2nd trading-day partition | 116/116 | manifest |
| missing_region_shape | PREFIX_ONLY=87, MULTIPLE_REGIONS=29 | qualification JSON |
| missing_session_class | NIGHT_ONLY=87, BOTH_DAY_AND_NIGHT=29 | qualification JSON |
| truncation_shape | START_ONLY=116 | qualification JSON |
| missing_starts_at_requested_boundary | True=116 | qualification JSON |
| listing_effective_coverage | WITHIN_GOVERNED_LISTING_COVERAGE=116 | qualification JSON |
| returned-start offset (minutes) | 70 distinct values, min 1, max 3959 | revalidation JSON |
| returned_start within night window | 85 | raw files |
| returned_start at/after day 09:00 (no night bars) | 31 | raw files |
| old-manifest quality_status of the 116 | PASS=116 (truncation masked) | manifest |
| clean newly-listed first-day partitions | 28 | manifest |

## 3. Answers to the mandated key checks

### 3.1 Does the 116 correspond exactly to 116 distinct concrete contracts, one failure each?

**Yes.** 116 failures, 116 distinct contracts, 116 distinct (contract, trading_day) tuples, no duplicates,
no contract has more than one failed partition. Product split: `{ag:14, al:22, au:19, cu:21, ni:23, rb:17}`.

### 3.2 Per-contract structural checks

- **Failure is the first partition in the manifest**: 116/116 — every failure is the earliest
  manifest partition of its contract.
- **Near listing/effective start**: 116/116 — every failure trading_day equals the governed
  `first_trading_day` from `CANONICAL_CONTRACT_UNIVERSE.json`.
- **requested_start includes the previous-evening 21:00 night session**: 116/116 — every request is
  `prev_trading_day 21:00 -> trading_day 15:00`.
- **provider returned_start**: NOT uniform. 85 failures have returned_start inside the night window
  (partial night data present, offset 1–61 minutes typical, ragged up to the night end); 31 failures
  have returned_start at/after day 09:00 (no night bars at all).
- **should the first-night session exist?**: The repo authority (`build_session_metadata`) asserts it
  does (it emits a NIGHT window for the first trading day). The provider's own stored data contains
  night bars for 85 of the 116 (real volume, e.g. `cu2504` night 21:11→01:00 with non-zero volume), and
  for 28 clean newly-listed contracts the full first night is present. For the 31 no-night cases the
  repo evidence cannot distinguish "first night session genuinely absent" from "provider lacks the
  data"; this is recorded as an unresolved ambiguity, not guessed.

### 3.3 Are all 87 NIGHT_ONLY missing on the contract's first effective trading day?

**Yes.** All 116 failures (including all 87 NIGHT_ONLY) are on the governed first trading day.
All 87 NIGHT_ONLY are PREFIX_ONLY: only the leading portion of the first night session is missing
(e.g. `cu2504` missing 21:00–21:10, 11 bars).

### 3.4 What are the 29 BOTH_DAY_AND_NIGHT / MULTIPLE_REGIONS extra missing regions?

Each of the 29 has the **entire** first-night session missing (240 bars for cu/al/ni, 120 for rb)
**plus** a leading portion of the first day session (and sometimes nearly the whole first day):

- typical: night 21:00–00:59 (240 bars) + day 09:00–09:3x prefix;
- severe (7 nickel contracts): night 21:00–00:59 + 09:00–10:14 + 10:30–11:29 + 13:30–14:5x,
  leaving only the final minutes (several return only the last bar at 14:59, e.g. `ni2511` = 1 bar).

Product clustering of the 29: `{ni:15, al:8, cu:5, rb:1}`; au and ag have zero MULTIPLE_REGIONS
(all their failures are NIGHT_ONLY partial-night truncation).

### 3.5 Does the current SessionMetadata over-generate a "night session before the first listing day"?

**Yes — this is a real code-level defect.** `src/metadata_authority.py::session_windows_for_trading_day`
unconditionally emits the preceding-night window for every trading day (given a previous trading day
exists and the day is not night-closed), with **no listing-boundary (`first_trading_day`) awareness**.
Additionally `tools/build_canonical_dataset.py::build_contract_configs` builds each contract's
SessionMetadata over the full spec effective period (`2024-01-01..2025-12-31`), not over the contract's
governed `first_trading_day..last_trading_day` window, so pre-listing trading-day windows enter the
metadata identity. Verified example: `cu2504` first trading day `2024-04-16` has an authoritative
NIGHT window `2024-04-15 21:00 -> 2024-04-16 01:00`.

### 3.6 Did the old acquisition planner request this window from TqSdk?

**Yes — real code-level defect.** `tools/build_canonical_dataset.py::build_requests` requests
`prev 21:00 -> day 15:00` for the first trading day with no first-trading-day special case (it only
special-cases a missing previous trading day and officially night-closed days). Every one of the 116
failures therefore requested the first-night window.

### 3.7 Would re-downloading the same request return the same truncation?

**High-confidence inference: yes for the majority (not empirically verified — re-download is
forbidden).** Evidence: (a) acquisition was retrospective (2026-08-16/17), long after the coverage
window; (b) truncated and clean first-day partitions are fully interleaved in acquisition time with no
batch/network clustering; (c) 31,980 regular-day partitions return exactly from 21:00 while only
first-day partitions truncate; (d) 2nd trading days of all 116 failed contracts are clean. The
truncation is therefore a property of the provider's stored historical data, not of the acquisition
process. The ragged offsets (70 distinct values) indicate variable provider-side data quality rather
than a single fixed provider rule.

## 4. Hypothesis evaluation

| Hypothesis | Verdict | Evidence |
|---|---|---|
| A. Random acquisition truncation | REJECTED | 0/31,980 regular-day truncations; clean/truncated fully interleaved in acquisition time; no timing correlation |
| B. TqSdk fixed provider truncation | PARTIAL (provider-side data truncation yes; "fixed" no) | truncation is stored-data-side and first-day-specific, but offsets are ragged (70 distinct values), not a fixed rule |
| C. Contract first-trading-day / listing boundary | PARTIAL (context, not cause) | all failures are first trading days, but 28 newly-listed contracts have clean first days, so first-day alone is not sufficient; missing day-session bars are not a listing boundary |
| D. Night-session authority overgeneration | PARTIAL — real secondary defect | `session_windows_for_trading_day` / `build_session_metadata` / `build_contract_configs` have no listing-boundary awareness; cannot explain the day-session gaps (e.g. `al2501` missing 09:00–10:44, `ni2511` = 1 bar) |
| E. Acquisition planner / request bug | PARTIAL — real secondary defect | `build_requests` requests the first-night window unconditionally; cannot explain missing day-session data that no planner change could recover |
| F. Other deterministic cause | N/A | the observed product clustering (ni/al/cu severe, au/ag mild) is consistent with provider-side data-quality variance, not a single project rule |

## 5. Root-cause verdict: MIXED_ROOT_CAUSES

**Primary cause — PROVIDER_REPEATABLE_TRUNCATION (dominant, irreducible).** The TqSdk data center's
stored historical data for the first trading day of these 116 contracts is incomplete/truncated:
ragged leading data loss that in 29 cases also removes most of the first day session. This is a
stored-data property (retrospective fetch, no acquisition-process correlation, 0 regular-day cases),
so re-requesting the same windows would very likely reproduce the truncation. It is irreducible in the
sense that no planner or authority change can make the provider return day-session bars it does not
store (e.g. `al2501` missing 09:00–10:44, `ni2511` returning a single bar).

**Secondary cause — LISTING_SESSION_AUTHORITY_DEFECT / ACQUISITION_PLANNER_DEFECT (real project-side
code defects).** The project session authority and the acquisition planner both unconditionally assume
a full first-trading-day night session, with no listing-boundary awareness, so the completeness
expectation for first days overstates what the provider can supply. The old acquisition builder masked
the truncation by recording all 116 partitions as PASS, which is why the incomplete corpus passed
acceptance unnoticed.

The verdict therefore is **MIXED_ROOT_CAUSES**: provider repeatable truncation of first-trading-day
data (primary) plus session-authority/planner listing-boundary defects (secondary).

## 6. Code-level defects (for project brain adjudication; NOT modified here)

1. `src/metadata_authority.py::session_windows_for_trading_day` — no `first_trading_day`
   (listing/effective-start) boundary input; unconditionally emits the first trading day's
   preceding-night window. Required fix: accept a governed listing/effective-start boundary and
   suppress the night window for any trading day whose preceding-night session would fall before the
   contract's effective start.
2. `src/metadata_authority.py::build_session_metadata` — callers supply all coverage-window trading
   days; the authority has no per-contract listing-boundary input.
3. `tools/build_canonical_dataset.py::build_contract_configs` — builds SessionMetadata over
   `spec.effective_start..spec.effective_end` (full coverage) instead of the contract's governed
   `first_trading_day..last_trading_day`; pre-listing windows enter the metadata identity. Required
   fix: pass the governed universe bounds into `build_session_metadata`.
4. `tools/build_canonical_dataset.py::build_requests` — no first-trading-day handling; requests
   `prev 21:00 -> day 15:00` for the first trading day. Required fix: for the first trading day, either
   request day-session-only (`09:00-15:00`) or bind first-night existence to verified authority before
   requesting it.
5. Old acquisition builder masked truncation as PASS. The repaired `_acquire_partition` now flags
   `returned_coverage_truncated`; the accepted corpus still contains the masked records.

## 7. Recommended repair (subject to project brain + Owner gate)

- The 116 failures are **not** fixable by re-requesting the identical windows: the provider lacks the
  data (especially the day-session gaps in the 29 severe cases).
- Recommended path: re-authorize a **targeted re-acquisition** under corrected first-day scope
  (day-session-only requests for first trading days, `09:00-15:00`) and compare what the provider
  returns; if the provider still cannot supply the missing first-day bars, record the 116 first-day
  partitions as **governed data-availability exceptions** (expected coverage re-scoped to the
  provider-returned first-day coverage) instead of silently PASS, and update the corpus completeness
  authority accordingly. Cross-source daily OHLC for all failing cu first days already MATCHes the
  SHFE official annual raw, so the daily record is not contradicted by official data.
- The prior qualification was BLOCKED on `TQSDK_EXISTING_AUTH_NOT_AVAILABLE`; no targeted
  re-acquisition occurred, so no repaired PASS exists to validate against.

## 8. Status

```text
STATUS=COMPLETE
DISTINCT_FAILED_CONTRACTS=116
FIRST_PARTITION_FAILURE_COUNT=116
FIRST_LISTING_DAY_COUNT=116
NIGHT_BOUNDARY_PATTERN_COUNT=116
ROOT_CAUSE_VERDICT=MIXED_ROOT_CAUSES
CRITICAL_FINDINGS=2
HIGH_FINDINGS=4
RECOMMENDED_REPAIR=RE_AUTHORIZE_TARGETED_REACQUISITION_WITH_FIRST_DAY_SCOPE_OR_GOVERNED_EXCEPTION
REVIEW_IDENTITY=f7b0492dad5e43c832c03b0b2ac1ad05825f56ba93f9626f1dd8556790ddf98a
COMMIT=<filled-after-commit>
PUSH=<filled-after-push>
```

## 9. Reproducibility

- `python tools/verify_116_final.py` recomputes every aggregate cited in section 2 from the accepted
  manifest, raw files, and committed evidence.
- `python tools/write_116_review_json.py` regenerates
  `docs/reviews/CANONICAL_D01_D02_116_FAILURE_ROOT_CAUSE_REVIEW_V0_1.json` (identity
  `f7b0492dad5e43c832c03b0b2ac1ad05825f56ba93f9626f1dd8556790ddf98a`).
- Both are strictly read-only; neither modifies any corpus artifact or `src/`.

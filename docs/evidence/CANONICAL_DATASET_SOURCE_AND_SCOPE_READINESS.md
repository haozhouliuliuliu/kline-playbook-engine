# Canonical Dataset Source and Scope Readiness

PILOT_ONLY=YES
TQSDK_STATUS=VERIFIED
TQSDK_ADOPTED=NO
CANONICAL_DATASET_ACCEPTED=NO
STRATEGY_RESEARCH_STARTED=NO

Verification time: `2026-08-16T16:00:00Z`
Branch: `ds/canonical-dataset-pilot`
Formal next action (unchanged): `CANONICAL_RESEARCH_DATASET_BUILD_AND_SOURCE_ACCEPTANCE_PACKAGE`

This document is the single decision-ready dossier for the formal canonical
research dataset package. It is engineering analysis only. It does not adopt a
source, does not freeze research/dataset semantics, and does not mark the
formal package complete. Final source adoption and dataset-scope decisions
remain with GPT/project lead and, as applicable, the Owner.

## 1. Last acquisition hardening (this package)

- **TqSdk runtime-version binding.** `TqSdkSourceAdapter` now declares a
  verified compatibility runtime version (`3.10.1`). If the actually imported
  runtime version differs, `_connect` fails closed with an explicit error and
  closes the connection; it is never retried and never silently continues under
  the `tqsdk-3.10.1...` source/normalizer identity. Tests cover a matching
  version (succeeds) and a mismatched version (fails closed, one attempt).
- **Narrow transient retry classification.** `is_transient_network_error` now
  retries only a narrow set of requests/urllib3 transport errors plus builtin
  `ConnectionError`/`TimeoutError`. The previous broad `OSError` fallback was
  removed, so file/config/certificate-setup and other deterministic local
  failures (including plain `OSError`, `FileNotFoundError`, and builtin
  `ssl.SSLError`) are never retried. Bounded retries are retained. Tests cover
  the refined classification.

## 2. Foundation acceptance readiness

Review of the nine foundation files on this branch (from `main` `53339c4` to
current HEAD), including the two hardening changes above:

- `src/historical_acquisition.py` — generic `SourceAdapter`/`SourceSpecification`
  boundary, `TqSdkSourceAdapter` (version-bound, lazy TqSdk), `DatasetBuilder`
  (no provider hard-coding), `ContractMetadataFact`, transient-only bounded
  retry.
- `src/historical_manifest.py` — deterministic `ManifestPartition`/`DatasetManifest`
  with fail-closed hardening.
- `tests/test_historical_acquisition.py`, `tests/test_historical_manifest.py` —
  deterministic tests (provider boundary, collision safety, retry, manifest
  hardening, resume).
- `tools/pilot_build_dataset.py` — pilot runner consuming only the explicit
  session fixture.
- Evidence artifacts: `HISTORICAL_DATASET_PILOT.md`, `.manifest.json`,
  `.cross_source.json`, `.sessions.json`.

Full suite (`python -m unittest discover -s tests -v`): **126 passed**.
`compileall` clean; all committed JSON validated; raw hashes verified; secret
scan clean; `git diff --check` clean. No blocker was found.

`FOUNDATION_RECOMMENDATION=MERGE_READY`

Merge itself is not performed by this package (Owner/GPT gate remains).

## 3. Canonical source acceptance readiness

### TqSdk (minute-data candidate)

| Item | Recorded fact |
| --- | --- |
| Current verified API/runtime version | `3.10.1` (adapter is runtime-version bound) |
| Historical minute capability actually proved | `TqApi.get_kline_data_series` with `duration_seconds=60` returned real concrete-contract 1-minute bars: `SHFE.ni2509` + `SHFE.rb2510`, 10 partitions, 4050 bars, all `quality=PASS` |
| Concrete-contract semantics | Concrete contracts only; pseudo MAIN/CONTINUOUS rejected by the acquisition boundary; night-session bars returned and attributed to the correct trading day |
| PIT timestamp semantics | K-line `datetime` is the interval start (Beijing-time Unix ns); `available_at = start + 60 s`; retrieval time is never historical PIT time (proved on real data) |
| Authentication requirements | `TqAuth(account, password)` at runtime; hidden local input; in-memory only; no persistence |
| Trial/entitlement status | Owner's existing trial; professional historical API returned data (entitlement PASS) |
| Reproducibility constraints | Identical requests return byte-identical responses (proved); deterministic manifest; resume without re-download |
| Local raw preservation capability | Raw JSON in ignored `data/raw/historical/` with SHA256 binding; re-validation without re-download via manifest resume |
| Important failure modes | Transient TLS/network during connect (bounded retry); auth/entitlement/config failures (no retry, fail closed); runtime-version mismatch (fail closed, no retry); trial expiry |
| When the current trial expires | New authentication will fail; already-acquired local raw + manifest remain usable for research; new/re-downloaded data requires renewed access |
| Future paid access required to extend/re-download | For NEW or EXTENDED coverage after expiry, yes (paid subscription or a renewed trial); for already-acquired periods, no |

Explicit separation:

- `TECHNICALLY_SUITABLE=YES` — TqSdk is technically suitable as the canonical
  minute-data candidate (real data, PIT, quality, 10/10 SHFE cross-source match).
- `PAID_CONTINUITY_DECISION=PENDING` — whether to commit to future paid
  continuity is a separate Owner decision; nothing was purchased, upgraded,
  recharged, or committed.

### SHFE official annual/statistical raw

`VERIFIED` reference authority for the daily/statistical facts actually proved
(see `SHFE_OFFICIAL_RAW_RECHECK_MANIFEST.json`). It is **not** a minute-data
provider. Role: daily-aggregate cross-check / reference only.

## 4. Governed contract / session metadata plan

Before a canonical dataset is frozen, each metadata class must be sourced from
official primary sources where available and versioned (schema + artifact hash).
The pilot currently uses `PILOT_FIXTURE`; the formal package must replace the
fixture with governed, official-bound metadata.

| Planned metadata | Planned source | Classification |
| --- | --- | --- |
| Trading calendar | SHFE official trading calendar (annual/monthly) | OFFICIAL_AVAILABLE |
| Night-session schedule by product / effective period | SHFE official product trading hours; historical effective-period schedules need verification per period | OFFICIAL_PARTIAL |
| Minimum tick | SHFE official contract specifications (current); historical changes need verification | OFFICIAL_PARTIAL |
| Contract multiplier | SHFE official contract specifications (current); historical changes need verification | OFFICIAL_PARTIAL |
| Listing / expiry | Exchange listing schedules (official); historical schedules need archival binding | OFFICIAL_PARTIAL |
| Price-limit metadata (needed later) | SHFE daily/contractual price limits (official); historical daily archive needs binding | OFFICIAL_PARTIAL |
| Concrete contract identity | Derived from exchange product code + listing/expiry | OFFICIAL_AVAILABLE |
| Daily reference (cross-check) | SHFE official annual raw (committed recheck manifest) | OFFICIAL_AVAILABLE |

No historical rules are invented. The plan binds each source to a committed
official artifact (with SHA256) before freezing; anything that cannot be bound
is kept explicit as `PILOT_FIXTURE` or marked unresolved. A large full
historical metadata warehouse is **not** built in this package.

## 5. Dataset scale estimation (three engineering options)

Empirical basis (this pilot): 10 partitions, 4050 bars, 708,458 bytes raw →
≈ 405 bars/partition, ≈ 175 bytes/bar raw JSON, ≈ 71 KB/partition. Trading days
≈ 245/year. Figures below are order-of-magnitude engineering estimates.

### MINIMAL — "research-foundation core metals, front contract"
- Universe concept: 4 SHFE products (e.g., ni, cu, al, rb); one front concrete
  contract per product.
- Inclusion: most active concrete contract per product (concrete only, no MAIN).
- Years: ~1.
- Trading-day/partition count: ~980.
- Minute bars: ~0.4M.
- Raw JSON: ~70 MB.
- Normalized columnar: ~15-30 MB.
- Acquisition time/risk: ~1k calls; hours; low-moderate risk.
- Research coverage: session/PIT foundation, methodology, limited strategy work.

### BALANCED — "core metals + near contracts, 2 years"
- Universe concept: ~6 SHFE products (e.g., ni, cu, al, rb, au, ag).
- Inclusion: front 2 active concrete contracts per product.
- Years: ~2.
- Trading-day/partition count: ~5,900.
- Minute bars: ~2.4M.
- Raw JSON: ~420 MB.
- Normalized columnar: ~100-150 MB.
- Acquisition time/risk: ~5.9k calls; ~1-2 days; moderate risk; TqSdk caching helps.
- Research coverage: good breadth for strategy/validation foundations.

### BROAD — "SHFE/INE broad universe, 5 years, all active concrete contracts"
- Universe concept: ~10 SHFE/INE products.
- Inclusion: all active concrete contracts per product.
- Years: ~5.
- Trading-day/partition count: ~37,000.
- Minute bars: ~15M.
- Raw JSON: ~2.6 GB.
- Normalized columnar: ~0.6-1.2 GB.
- Acquisition time/risk: ~37k calls; multiple days; higher risk (rate limits,
  sustained access required).
- Research coverage: broad multi-year multi-product research; heavier infra.

No product was selected based on prior steel strategy/PnL; only
engineering/research-coverage considerations were used.

## 6. Storage applicability review

Roles evaluated separately (nothing installed):

| Role | MINIMAL | BALANCED | BROAD | Recommended mechanism |
| --- | --- | --- | --- | --- |
| RAW_ARTIFACT_STORAGE | JSON OK | JSON OK | JSON OK | JSON (ignored dir + SHA256 manifest) — keep |
| NORMALIZED_BAR_STORAGE | stdlib OK | gap appears | gap | Parquet |
| MANIFEST/METADATA_LEDGER | JSON OK | gap appears | gap | SQLite |
| RESEARCH_QUERY_ENGINE | not needed | optional | recommended | DuckDB (optional) |

`STORAGE_REVIEW=ADD_TOOL` for the recommended (BALANCED) scope:
- `Parquet` → NORMALIZED_BAR_STORAGE;
- `SQLite` → MANIFEST/METADATA_LEDGER;
- `DuckDB` (optional) → RESEARCH_QUERY_ENGINE;
- JSON raw artifacts are retained (RAW_ARTIFACT_STORAGE).

For MINIMAL, `USE_EXISTING` would suffice. No tool is adopted/installed by this
package; the formal package may add them only under the allowed authority.

## 7. Development / validation / final-unseen preparation

No final-unseen data is chosen or unlocked, and no chronological split is
created here. Before GPT/Owner can freeze a future split, the canonical dataset
must establish:
- earliest reliable coverage (data availability start);
- product coverage continuity (holidays/gaps documented);
- source anomalies (recorded, not silently corrected);
- contract mapping availability (governed roll rule for a per-product research
  series built from concrete contracts);
- structural regime changes (tick/limit/session-schedule changes over time);
- sufficient chronological length for the intended research window.

The existing `FinalUnseenFirewall` remains authoritative.

## 8. One recommended plan (recommendation only)

`RECOMMENDED_SOURCE=TQSDK`

`RECOMMENDED_DATASET_SCOPE=BALANCED`

`RECOMMENDED_STORAGE=JSON(raw) + PARQUET(normalized) + SQLITE(manifest/ledger); DuckDB optional`

Rationale: TqSdk is the only minute-capable source that is `VERIFIED` with real
data, PIT semantics, quality gates, and an exact 10/10 SHFE daily cross-source
match. BALANCED gives a research-useful breadth (2.4M bars, ~420 MB raw) with
moderate acquisition time/risk and matches the storage-recommendation
threshold. SHFE official raw remains the daily cross-check reference, not the
minute source.

Principal alternative: SHFE official raw as the canonical minute source — not
possible (it is daily/statistical only). Other minute candidates (openctp,
SimNow) are unproven and are not preferred while TqSdk is VERIFIED and
cross-checked.

## 9. Owner decision dossier

Everything above is a technical recommendation. The material decisions for
GPT/Owner are:

1. Approve / reject TqSdk as the canonical minute-data source (source adoption).
2. Approve / change the recommended dataset scope (MINIMAL / BALANCED / BROAD).
3. Approve / reject any future paid continuity commitment if actually required
   (e.g., to extend or re-download data after the current trial expires).

Formal `CURRENT_STATE` changes are deferred until after this adjudication; this
branch only adds pilot/readiness evidence and does not mark the formal package
complete.

```text
FOUNDATION_RECOMMENDATION=MERGE_READY
SOURCE_ACCEPTANCE_RECOMMENDATION=ACCEPT_TQSDK_AS_CANONICAL_CANDIDATE
RECOMMENDED_SOURCE=TQSDK
RECOMMENDED_DATASET_SCOPE=BALANCED
RECOMMENDED_STORAGE=JSON(raw)+PARQUET(normalized)+SQLITE(manifest/ledger);DuckDB optional
PAID_CONTINUITY_REQUIRED=UNKNOWN
OWNER_DECISION_REQUIRED=YES

OWNER_DECISION_OPTIONS=
1. Approve/reject TqSdk as the canonical minute-data source (adoption).
2. Approve/change the recommended dataset scope (MINIMAL/BALANCED/BROAD).
3. Approve/reject any future paid continuity commitment if actually required.
```

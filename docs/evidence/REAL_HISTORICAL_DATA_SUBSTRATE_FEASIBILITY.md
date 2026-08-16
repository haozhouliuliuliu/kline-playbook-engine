# Real Historical Data Substrate Feasibility

Verification time: `2026-08-16T13:48:45.4091315Z`
Starting HEAD: `a1ef58ccd3b129f32a4662590fbfe35b726ca9b5`
Package outcome: `FULL_SUCCESS`
Tool decision: `ADD_TOOL`

## Conclusion

The Owner-authenticated real TqSdk probe succeeded under the current trial. A bounded concrete-contract one-minute sample and the complete `2025-06-16` trading day for `SHFE.ni2509` were returned by the current TqSdk `3.10.1` professional historical API. Both real samples pass the existing project-owned normalization path, real-sample PIT normalization, and every quality gate. The daily aggregate computed from the 465 one-minute bars matches the committed SHFE official daily reference exactly on all six fields (open, high, low, close, volume, open interest). TqSdk advances from `CANDIDATE` to `VERIFIED`; it is not `ADOPTED` as the canonical research source.

No purchase, recharge, subscription, broker connection, order, strategy, parameter search, final-unseen access, or Shadow/live action occurred. Credentials were entered locally in the terminal through a hidden `getpass` prompt and were never echoed, logged, written to disk, or committed; `TqAuth` existed only in memory and vanished when each probe process exited. Large raw market data remains only in the ignored `data/raw/historical/` location and is not committed.

## Real probe provenance (non-secret)

| Item | Bounded probe | Full trading-day probe |
| --- | --- | --- |
| Provider | `TQSDK` | `TQSDK` |
| Actual TqSdk version | `3.10.1` | `3.10.1` |
| API | `TqApi.get_kline_data_series` | `TqApi.get_kline_data_series` |
| Concrete contract | `SHFE.ni2509` | `SHFE.ni2509` |
| Granularity | `60 s` | `60 s` |
| Request coverage (Beijing) | `2025-06-16 10:00:00` to `10:40:00` | `2025-06-13 21:00:00` to `2025-06-16 15:00:00` |
| Returned coverage (bar starts) | `2025-06-16 10:00:00` to `10:40:00` | `2025-06-13 21:00:00` to `2025-06-16 14:59:00` |
| Rows returned | `26` | `465` |
| Raw schema identity | `tqsdk-kline-records-json-v1` | `tqsdk-kline-records-json-v1` |
| Raw fields | `id, datetime, open, high, low, close, volume, open_oi, close_oi, symbol` | same |
| Retrieval timestamp (UTC) | `2026-08-16T13:37:41.7497639Z` | `2026-08-16T13:46:38.5015087Z` |
| Raw file size (bytes) | `4575` | `81651` |
| Raw SHA256 | `5a2095ca23c093fc4c327ee6f996d0de8019ed8981fa39b0dd759c1dede41304` | `d934f4f717077f773df17a1aa0c02ea8bc69484c93f22adde82beed3a1ad8885` |
| Request identity | `c9ea6bf7f061262a1e9deb79c6dca3dbb698ef28ef522bb42d0b91e9cb59afe4` | `ad894f46c2459166dba35566df701c3197eef9692b2840bd7eca2a1d506beb1d` |
| DataVersionIdentity | `cd4a306f6310fc4e59d5f8b7d340e8b8acd054bb22b364f1ba35ac13def12b0b` | `724e16537247eb1af233d12a92c9d07d926bff84944abe96c0e5eb518b424fdc` |
| Normalized batch identity | `4e37a5f149cd738f430df0062b02284c23cf9c6f9a859d9bc2e542ee680af461` | `50f3452f67694fba3a5cd2f61aedcc3431ae353b7818591ee26fa20f80b27f18` |
| Raw file (ignored location) | `data/raw/historical/SHFE.ni2509.1min.bounded_2025-06-16_1000-1040.json` | `data/raw/historical/SHFE.ni2509.1min.trading_day_2025-06-16.json` |

Request identities exclude all authentication data; `SourceIdentity` rejects sensitive request-parameter names. The non-secret request-parameter tuples were `("duration_seconds","60"),("end_dt","<end>"),("start_dt","<start>"),("symbol","SHFE.ni2509")` with `<end>/<start>` as in the coverage column above.

## Probe procedure (reproducible, non-secret)

- TqSdk `3.10.1` was installed only in an isolated reversible venv at `%LOCALAPPDATA%\Temp\kline-playbook-tqsdk-probe\`; it was **not** added to the project dependency set.
- A local interactive probe read the account (visible terminal input) and the password (hidden `getpass`), constructed `TqAuth` only in memory, opened `TqApi(auth=...)` with no broker account, and called `get_kline_data_series(symbol="SHFE.ni2509", duration_seconds=60, start_dt=..., end_dt=...)`.
- No order/trading API was used.
- The returned DataFrame was converted to the project raw JSON schema and written to the ignored `data/raw/historical/` location; the SHA256 was computed over the exact stored bytes.
- One transient TLS/network error (`SSL: UNEXPECTED_EOF_WHILE_READING` against the `api.shinnytech.com` name service) occurred on the first full-day attempt during connection setup. It was not an authentication failure (the same trial account had authenticated minutes earlier). A bounded connect retry (3 attempts) succeeded on the relaunch.

## Current TqSdk facts

| Fact | Evidence | Result |
| --- | --- | --- |
| Project/system installation | Python import and package metadata lookup under Python `3.12.10` | Not installed; TqSdk used only in the isolated probe venv |
| Current official package | `pip index versions tqsdk` in the isolated venv | `3.10.1` (latest available, matching prior evidence) |
| Official API | `TqApi.get_kline_data_series` | Professional-only static DataFrame; one-minute uses `duration_seconds=60`; `date` arguments mean trading dates |
| K-line timestamp | Current official docs/wheel source and real responses | Beijing-time Unix nanoseconds at the K-line interval start (confirmed on real data: bars step by exactly 60 s, recess bars absent) |
| Real current trial auth | Owner entered credentials locally in the terminal via `getpass` | `PASS` (same trial account authenticated both probes) |
| Real current trial call | Bounded and full-day `get_kline_data_series` calls returned data | `PASS` |
| Professional historical entitlement | Real `get_kline_data_series` returned rows under the current trial | `PASS` (entitlement not denied) |
| Actual version used by a current real call | The venv that produced the real responses | `3.10.1` |

Current primary sources:

- TqSdk API: <https://doc.shinnytech.com/tqsdk/latest/reference/tqsdk.api.html>
- TqSdk professional features: <https://doc.shinnytech.com/tqsdk/latest/profession.html>
- Official source repository: <https://github.com/shinnytech/tqsdk-python>

The old backup proves only that an older project once called `get_kline_data_series` and `get_tick_data_series`. A backup artifact labels a version as `3.10.1`, but the current task authority explicitly warns that the later Professional-run version is unknown. This project therefore records the old version attribution as disputed and does not inherit it.

## SHFE official annual raw recheck

The three local ZIP files still exist. Their SHA256 values were recomputed and match the supplied prior values. Each current official URL returned HTTP `200`, `application/zip`, and the same content length as the local file. Details are committed in `docs/evidence/SHFE_OFFICIAL_RAW_RECHECK_MANIFEST.json`.

The SHFE official data page describes these as statistical/historical data. Independent ZIP/workbook inspection found concrete-contract daily rows with columns including date, OHLC, settlement, volume, amount, and open interest. They are not minute or Tick files. The official data navigation is <https://www.shfe.com.cn/eng/reports/index.html>.

One comparison anchor was independently read from the 2025 June workbook: `SHFE.ni2509`, trading date `2025-06-16`, daily open `120400`, high `120600`, low `119420`, close `120070`, volume `10431`, OI `26672`. It is preserved as an official daily aggregate reference and was used for the cross-source comparison below.

## Project-owned contract

`src/historical_data.py` adds:

- `SourceIdentity`: provider, source type, endpoint/resource identity, provider dataset/version if exposed, source retrieval timestamp, and a deterministic non-secret request identity;
- `RawArtifact`: exchange, concrete contract, requested coverage, granularity, timezone, raw schema identity, raw SHA256, and source identity binding;
- `NormalizerIdentity`: adapter/parser, normalized schema, and availability-rule versions;
- `DataVersionIdentity`: deterministic binding of source identities, raw artifacts/hashes, concrete instruments, coverage, granularity, timezone, session metadata, normalizer, historical availability rule, and optional contract metadata identity;
- `NormalizedHistoricalBar` and `NormalizedHistoricalBatch`: immutable associations from normalized bars to raw artifact and data-version identities;
- `normalize_tqsdk_historical_bars`: the small TqSdk-shaped adapter into the existing Data Substrate.

Sensitive request-parameter names are rejected so credentials cannot enter committed provenance. Raw payload bytes must match their artifact SHA256 before parsing. The ignored canonical raw location is `data/raw/historical/`; no large raw data is committed.

## Historical PIT semantics

Four timestamps remain distinct:

1. `source_event_at`: TqSdk K-line `datetime`, documented as interval start;
2. `CompletedBar.start` / `CompletedBar.end`: explicit fixed-duration interval;
3. `CompletedBar.available_at`: conservative historical rule `start + duration`;
4. `SourceIdentity.retrieved_at`: machine retrieval time, never used as historical PIT availability.

The adapter reuses `CompletedBar.available_at` and `CompletedBar.is_visible_at`; it does not create a second PIT system. The rule is versioned as `bar-start-plus-duration-v1`. Real-path `PIT_NORMALIZATION=PASS` is established below on both real samples: the TqSdk K-line `datetime` is the interval start, and the bar is invisible before `available_at = start + 60 s` and visible at/after it.

## Real-sample PIT and quality-gate evidence

Both real raw files were validated by running them through the existing project path (`normalize_tqsdk_historical_bars` with the real session metadata for trading day `2025-06-16` and the `ni2509` minimum tick of `10`). Result of the bounded sample: `26` bars, `missing_expected_starts=[]` (the 10:15-10:30 recess is an expected absence, not a gap). Result of the full trading day: `465` bars, `missing_expected_starts=[]` (every published-session one-minute bar present).

Verified on the real samples:

- timezone-aware normalized timestamps (`Asia/Shanghai`);
- concrete-contract identity `SHFE.ni2509` throughout;
- strictly ordered, duplicate-free bars;
- positive, internally consistent OHLC, all tick-compatible with the `10` minimum tick;
- non-negative volume and start/end open interest;
- `SessionMetadata.trading_day_at` assigns the night session (2025-06-13 21:00-2025-06-14 01:00) to trading day `2025-06-16`;
- session-boundary handling: recess bars absent, no unexpected gap reported;
- no interpolation or forward fill (`source_event_at` always equals bar start);
- raw SHA256 binding (normalization refuses a payload that does not match the artifact hash);
- deterministic `DataVersionIdentity`; repeated normalization yields the identical batch identity;
- PIT: invisible one second before `available_at`, visible at `available_at`, `available_at = start + 60 s`, and `source_retrieved_at` (2026-08-16) is never the historical PIT time (2025-06-16).

`QUALITY_GATES=PASS` and `PIT_NORMALIZATION=PASS` on the real samples.

## Quality-gate evidence

Focused command: `python -m unittest tests.test_historical_data -v`

Result at implementation checkpoint: `7 tests passed`.

Covered behavior:

- timezone-aware source/start/end/availability/retrieval timestamps;
- strict deterministic order;
- duplicate and reversed/out-of-order rejection;
- positive, consistent OHLC;
- non-negative volume and start/end OI when supplied;
- concrete-contract and exchange consistency;
- existing `SessionMetadata.trading_day_at` assignment;
- planned recess excluded from gap detection;
- unexpected expected-session bar reported as missing;
- no interpolation or forward-fill;
- payload hash, artifact, data-version, session, normalizer, availability-rule and optional contract-metadata binding;
- repeated parse produces the same batch identity;
- no visibility before justified `available_at`;
- claimed-coverage enforcement;
- optional minimum-price-tick compatibility when a contract metadata identity is supplied.

These are deterministic implementation tests. Real-sample `QUALITY_GATES=PASS` and `PIT_NORMALIZATION=PASS` are now established above on both real TqSdk samples under the Owner's current trial.

## Cross-source check

`CROSS_SOURCE_CHECK=PASS`. The daily aggregate was computed from the 465 one-minute bars of the full `2025-06-16` trading day (`open` = first bar open, `close` = last bar close, `high`/`low` = extremes, `volume` = sum of bar volumes, `open interest` = last bar `close_oi`). It matches the committed SHFE official daily reference exactly:

| Field | SHFE official reference | TqSdk one-minute aggregate |
| --- | --- | --- |
| open | 120400 | 120400 |
| high | 120600 | 120600 |
| low | 119420 | 119420 |
| close | 120070 | 120070 |
| volume | 10431 | 10431 |
| open interest | 26672 | 26672 |

No averaging of providers was performed; the two values are identical, so there is no discrepancy to preserve or explain.

## Provider decisions

| Provider/tool | Status | Exact claim |
| --- | --- | --- |
| TqSdk | `VERIFIED` | Under the current Owner trial with TqSdk `3.10.1`: authentication, real concrete-contract one-minute data, provenance/raw hash, normalization, PIT, quality, and cross-source checks all PASS |
| SHFE official annual raw | `VERIFIED` | Current official URL/size/hash and daily concrete-contract workbook nature re-verified for provenance/reference use |

Neither source is `ADOPTED`. `VERIFIED` does not mean `ADOPTED`; TqSdk is not frozen as the permanent canonical research source by this package.

## Current blocker and next action

`CURRENT_BLOCKER=NONE`

`CURRENT_NEXT_ACTION=CANONICAL_RESEARCH_DATASET_BUILD_AND_SOURCE_ACCEPTANCE_PACKAGE`

That package is **not started** by this task. Real-sample `DataVersionIdentity` values for the two real probes are recorded in the provenance table above.

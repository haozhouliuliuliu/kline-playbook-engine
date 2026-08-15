# Real Historical Data Substrate Feasibility

Verification time: `2026-08-15T18:00:52.9255493Z`
Starting HEAD: `f16d447419abed887a1897eedea73234a7c20f8c`
Package outcome: `OWNER_GATE`
Tool decision: `ADD_TOOL`

## Conclusion

The project-owned, vendor-neutral provenance, data-version, fixed-duration historical PIT, and quality-gate layer is implemented and deterministically tested. The current Owner TqSdk trial was not re-verified because this machine has no installed TqSdk runtime and no currently usable secure authentication state. Therefore no current real sample, real data-version identity, real-sample PIT PASS, or cross-source comparison is claimed.

The exact minimum action is:

`OWNER_ACTION=Authenticate the Owner's existing TqSdk trial locally without sharing credentials in chat.`

No purchase, recharge, subscription, broker connection, order, strategy, parameter search, final-unseen access, or Shadow/live action occurred.

## Current TqSdk facts

| Fact | Evidence | Result |
| --- | --- | --- |
| Project/system installation | Python import and package metadata lookup under Python `3.12.10` | Not installed |
| Existing non-secret auth discovery | TqSdk-related environment-variable names, Windows Credential Manager target names, and TqSdk/auth-related local path names were checked without printing values | No currently usable auth state found |
| Current official package candidate | `pip index versions tqsdk` and a no-dependency temporary wheel download | `3.10.1` |
| Inspected wheel | `tqsdk-3.10.1-py3-none-any.whl`, SHA256 `0e50a876e8fc3d36726b0a7ff0ad7916e68a5e5b64da9bd61823725fca80985f`; temporary copy removed | Metadata says Python `>=3.9`; source contains both professional historical APIs |
| Official API | `TqApi.get_kline_data_series` | Professional-only static DataFrame; one-minute uses `duration_seconds=60`; `date` arguments mean trading dates |
| K-line timestamp | Current official docs and wheel source | Beijing-time Unix nanoseconds at the K-line interval start |
| Tick timestamp | Current official docs and wheel source | Beijing-time Unix nanoseconds for the exchange-emitted Tick time |
| Real current trial call | Requires local Owner authentication | `OWNER_GATE` |
| Actual version used by a current real call | No current call occurred | `UNKNOWN` |

Current primary sources:

- TqSdk API: <https://doc.shinnytech.com/tqsdk/latest/reference/tqsdk.api.html>
- TqSdk professional features: <https://doc.shinnytech.com/tqsdk/latest/profession.html>
- Official source repository: <https://github.com/shinnytech/tqsdk-python>

The old backup proves only that an older project once called `get_kline_data_series` and `get_tick_data_series`. A backup artifact labels a version as `3.10.1`, but the current task authority explicitly warns that the later Professional-run version is unknown. This project therefore records the old version attribution as disputed and does not inherit it.

## SHFE official annual raw recheck

The three local ZIP files still exist. Their SHA256 values were recomputed and match the supplied prior values. Each current official URL returned HTTP `200`, `application/zip`, and the same content length as the local file. Details are committed in `docs/evidence/SHFE_OFFICIAL_RAW_RECHECK_MANIFEST.json`.

The SHFE official data page describes these as statistical/historical data. Independent ZIP/workbook inspection found concrete-contract daily rows with columns including date, OHLC, settlement, volume, amount, and open interest. They are not minute or Tick files. The official data navigation is <https://www.shfe.com.cn/eng/reports/index.html>.

One future comparison anchor was independently read from the 2025 June workbook: `SHFE.ni2509`, trading date `2025-06-16`, daily open `120400`, high `120600`, low `119420`, close `120070`, volume `10431`, OI `26672`. It is preserved only as an official daily aggregate reference. Because no current TqSdk sample exists, `CROSS_SOURCE_CHECK=NOT_AVAILABLE`.

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

The adapter reuses `CompletedBar.available_at` and `CompletedBar.is_visible_at`; it does not create a second PIT system. The rule is versioned as `bar-start-plus-duration-v1`. Synthetic tests prove that the bar is invisible before the end timestamp. Since actual current 1-minute returned rows could not be inspected under the Owner's trial, real-path `PIT_NORMALIZATION=UNPROVED` and the dataset is not research-ready.

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

These are deterministic implementation tests, not proof that a current TqSdk real sample passes them. Real-sample `QUALITY_GATES=UNPROVED` until local authentication permits the bounded probe.

## Provider decisions

| Provider/tool | Status | Exact claim |
| --- | --- | --- |
| TqSdk | `CANDIDATE` | Current official package/API path inspected; current Owner-trial entitlement and real one-minute response not re-verified |
| SHFE official annual raw | `VERIFIED` | Current official URL/size/hash and daily concrete-contract workbook nature re-verified for provenance/reference use |

Neither source is `ADOPTED`. TqSdk may proceed to source acceptance only after the current local trial successfully supplies the bounded concrete-contract one-minute sample and that sample passes PIT, provenance, quality, and cross-source checks.

## Remaining blocker and next action

`CURRENT_NEXT_ACTION=HISTORICAL_DATA_SOURCE_OWNER_GATE`

`CURRENT_BLOCKER=Current TqSdk trial authentication is not available to this process through an existing safe local mechanism.`

After the Owner authenticates locally, the same bounded real probe should use one non-continuous SHFE contract, preferably `SHFE.ni2509`, `duration_seconds=60`, a small interval crossing a session boundary, and no order/trading calls.

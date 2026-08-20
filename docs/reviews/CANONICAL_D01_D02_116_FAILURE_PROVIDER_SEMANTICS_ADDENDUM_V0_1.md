# CANONICAL_D01_D02_116_FAILURE_PROVIDER_SEMANTICS_ADDENDUM_V0_1

> Date: 2026-08-21
> Branch: `review/canonical-116-root-cause-v01`
> Supersedes nothing. This is a **narrow supplementary source review** on top of
> `docs/reviews/CANONICAL_D01_D02_116_FAILURE_ROOT_CAUSE_REVIEW_V0_1.md`.
> Scope: TqSdk official / first-party materials only (official docs, official source/docstrings,
> official GitHub / official examples). No blogs/forums used as authority.
> Constraints honored: no `main` writes; no TqSdk login; no install; no download; no 32980 recompute;
> no candidate-outcome research.

```text
ADDENDUM_STATUS=COMPLETE
Q1_ZERO_VOLUME_BAR_BEFORE_FIRST_TRADE=NOT_VERBATIM_OFFICIAL_STRONG_INFERENCE_NO_BARS_BEFORE_FIRST_AVAILABLE_BAR
Q2_RETURNED_START_LATER_THAN_REQUESTED_START=OFFICIALLY_SUPPORTED
Q3_BAR_EVERY_MINUTE_GUARANTEED=NO_OFFICIALLY_SKIPPED_WHEN_NO_TRADE
Q4_RANGE_VS_AVAILABILITY_SEMANTICS=REQUESTED_RANGE_IS_FILTER_RETURNS_EXISTING_BARS
Q5_NO_BARS_BEFORE_LISTING_FIRST_TRADE=OFFICIALLY_SUPPORTED
ORIGINAL_PHRASE_REFINEMENT=NO_BAR_BEFORE_FIRST_AVAILABLE_TRADE
REVIEW_IDENTITY=4250d993048c12f019be9735c4fb14edf15872afda2932792f7340b104c9fa8d
```

## 1. Question and method

The prior review proved that all 116 canonical D-01/D-02 failures occur on the concrete contract's
first trading day, that 87 are leading-night-prefix missing and 29 additionally lose the leading part
of the first day session, and that `returned_start` is likely the provider's first available
historical bar. What it did **not** formally prove is **why** the provider does not supply the leading
one-minute bars.

This addendum answers that question using only TqSdk official / first-party material:

- official docs: `doc.shinnytech.com/tqsdk/latest/` (intro, `usage/mddatas`, `reference/tqsdk.api`,
  `reference/tqsdk.tools.download`);
- official source/docstrings: `github.com/shinnytech/tqsdk-python` (`tqsdk/api.py`,
  `tqsdk/data_series.py`);
- official examples: `tqsdk/demo/example/vwap.py`.

The API actually used by the project is `TqApi.get_kline_data_series` (per
`src/historical_acquisition.py` `SourceSpecification` endpoint
`TqApi.get_kline_data_series`), which is the API documented in `reference/tqsdk.api.html`.

## 2. Official evidence base (quoted, with sources)

| ID | Official statement (verbatim / near-verbatim) | Source |
|---|---|---|
| E1 | 提供当前所有可交易合约**从上市开始**的全部Tick数据和K线数据 — data coverage starts **from listing** | `doc.shinnytech.com/tqsdk/latest/intro.html`, "功能要点" |
| E2 | 例如 cu1805 13:00-13:30 **不交易**, 因此 IC1803 在 13:00-13:30 之间的K线数据**会被跳过** — a non-trading period produces **no K-line bars** | `reference/tqsdk.tools.download.html` (DataDownloader doc) |
| E3 | 如果任意一个合约在某个时刻**没有数据**, 则该时刻那条数据**被跳过**, 现象表现为 **K 线不连续** — a time with no data is skipped; K-lines can be **non-continuous** | `usage/mddatas.html` / `tqsdk/api.py` (get_kline_serial multi-contract note) |
| E4 | 下载的数据应该是 [start_dt, end_dt）；… 当前 id 已超出 last_id 或k线数据的时间已经超过用户限定的右端 → 返回 — the download returns **only the bars the server stores** inside the requested range, paging by K-line id, **without synthesizing missing minutes** | `tqsdk/data_series.py` (`DataSeries._download_data`), `tqsdk/api.py` (`get_kline_data_series` / `_get_data_series`) |
| E5 | 由于可能有节假日导致部分天并没有填满整个预设交易时间段，因此去除缺失部分交易时段的日期 — official example explicitly handles days whose trading-time slots are **not fully filled** | `tqsdk/demo/example/vwap.py` |

## 3. Answers to the five questions

### Q1 — Does TqSdk emit 0-volume bars for an open-but-not-yet-traded session, or does the series start at the first real bar/trade?

**Not verbatim-documented; strong official-semantics inference that the series starts at the first
available bar and emits no bars before it.**

- The official docs contain no sentence that explicitly says "the series starts at the first trade /
  first bar of a newly listed contract".
- However, the official semantics unambiguously state that non-trading periods produce **no bars**
  (E2: bars skipped), that a time with no data is skipped and K-lines can be non-continuous (E3),
  and that the download returns only bars the server stores within the range with no synthesis of
  missing minutes (E4). Data coverage starts from listing (E1).
- Consequence supported by the official semantics: minutes before the first available bar of a
  contract's first session have **no bars**; the series begins at the first available bar.
- Consistency check against the accepted raw corpus (observed, not official): e.g. `cu2504` first
  night returns from 21:11 with `volume=1` and then emits zero-volume bars from 21:12 onward — i.e.
  no bars before the first available bar, but continuous bars (including zero-volume) once the series
  has started. This matches "series starts at the first available bar" rather than "0-volume bars are
  synthesized for every minute from session open".

### Q2 — For a newly listed contract, can `returned_start` be later than `requested_start`?

**Yes — officially supported as a direct consequence of E2 + E4 + E1.**

`get_kline_data_series` returns the bars the provider stores within `[start_dt, end_dt)` (E4).
Because non-trading periods produce no bars (E2) and data exists only from listing onward (E1), a
newly listed contract whose first session has no trade until late will have no bars at the requested
start; the first returned bar (and thus `returned_start`) will be later. There is no verbatim
one-liner, but the semantics directly imply it.

### Q3 — Does TqSdk guarantee a bar for every minute of a trading session?

**No.** Officially stated: non-trading periods are skipped (E2); a time with no data is skipped and
K-lines can be non-continuous (E3); official example code handles days whose trading-time slots are
not fully filled (E5). TqSdk does **not** guarantee a bar per minute.

### Q4 — Requested time range vs. actually returned availability semantics

The official semantics are: `start_dt` / `end_dt` define the requested range; `get_kline_data_series`
returns the provider's stored K-line bars that fall inside that range (E4). The range is a **filter
window**, not a guarantee of full population. If the provider has no bar at the range start (no trade,
not yet listed) the series begins later; if no bar at the range end it ends earlier.

### Q5 — Do historical series have no bars before an instrument's listing / first trade?

**Yes — officially supported.** TqSdk provides all tick/K-line data "从上市开始" — **from listing**
(E1). Combined with E2/E3 (no-trade → no bar; non-continuous K-lines), historical series have no bars
before the instrument is listed / before trading occurs.

## 4. Re-evaluation of the original review's phrase

Original review phrasing (quoted):

> "provider data is incomplete/truncated" … Primary cause — PROVIDER_REPEATABLE_TRUNCATION.

That phrasing implies the provider **lost** bars it should have supplied. Under the official TqSdk
semantics documented above, the leading missing minutes are better characterized as:

- **`NO_BAR_BEFORE_FIRST_AVAILABLE_TRADE`** — the provider's historical series for these contracts
  starts at the first available bar; minutes before the first available bar/trade of the first
  trading day contain **no bars by the provider's data semantics** (E1, E2, E3, E4), not because of
  data loss and not because of random truncation.

Assessment of the three candidate labels:

| Candidate | Verdict | Basis |
|---|---|---|
| `PROVIDER_DATA_INCOMPLETE` | REJECTED as primary | implies stored data was lost/truncated relative to what the provider should hold; official semantics say no-trade periods simply have no bars (E2/E3/E4), not that bars were lost |
| **`NO_BAR_BEFORE_FIRST_AVAILABLE_TRADE`** | **ACCEPTED as the refined primary characterization** | best supported by official semantics: series starts at the first available bar; no bars before it; reproducible on re-download because those bars do not exist in the provider's series |
| `UNRESOLVED_PROVIDER_AVAILABILITY_SEMANTICS` | used only as a residual note for the exact leading-edge boundary | the official docs do not contain a verbatim sentence describing the first-session leading-edge rule; for that narrow sub-question the strict answer is `INSUFFICIENT_OFFICIAL_EVIDENCE` |

### Impact on the original verdict

- **No conflict; the original `MIXED_ROOT_CAUSES` verdict stands.**
- The refinement changes only the *characterization* of the primary component: from
  "PROVIDER_REPEATABLE_TRUNCATION (data incomplete/truncated)" to
  "NO_BAR_BEFORE_FIRST_AVAILABLE_TRADE (provider series starts at the first available bar per
  official TqSdk semantics; leading minutes absent by design, reproducible on re-download)".
- The secondary findings are **reinforced, not weakened**: the project's session authority
  (`session_windows_for_trading_day`) and acquisition planner (`build_requests`) expected full
  first-trading-day coverage including the leading minutes that the provider's series does not
  contain by design. The completeness expectation therefore over-stated what the provider supplies,
  and the old builder masked the discrepancy as PASS.
- `RECOMMENDED_REPAIR` is unchanged and is now better justified: re-requesting the identical windows
  will reproduce the same leading-absent bars (they do not exist in the provider's series); the
  repair must either re-scope first-day expected coverage (e.g. first-available-bar-onward or
  day-session-only) or obtain the leading minutes from a different authoritative source if they
  genuinely traded at the exchange.

## 5. Conclusion

```text
ADDENDUM_RESULT=COMPLETE
Q1=PARTIAL_OFFICIAL_STRONG_INFERENCE
Q2=OFFICIALLY_SUPPORTED
Q3=NO_OFFICIALLY_SUPPORTED
Q4=OFFICIALLY_DOCUMENTED_FILTER_SEMANTICS
Q5=OFFICIALLY_SUPPORTED
ORIGINAL_PHRASE_REFINEMENT=NO_BAR_BEFORE_FIRST_AVAILABLE_TRADE
ORIGINAL_VERDICT_IMPACT=NO_CONFLICT_MIXED_ROOT_CAUSES_STANDS
RESIDUAL_GAP=EXACT_FIRST_SESSION_LEADING_EDGE_NOT_VERBATIM_OFFICIAL
```

The only strict `INSUFFICIENT_OFFICIAL_EVIDENCE` item is the verbatim mechanism of the first-session
leading edge; the overall semantic direction is unambiguous and supported by official TqSdk
documentation and source.

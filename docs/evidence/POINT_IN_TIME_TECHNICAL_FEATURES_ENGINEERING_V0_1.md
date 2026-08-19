# POINT_IN_TIME_TECHNICAL_FEATURES_ENGINEERING_V0_1

> Version: 0.1 (final engineering state)
> Date: 2026-08-20
> Status: IMPLEMENTED_AND_TESTED / ENGINEERING_VERIFIED / GENERIC
> Work package: Lane G of the 2026-08-20 three-lane pre-outcome package — `POINT_IN_TIME_TECHNICAL_FEATURES`
> Architecture addendum: `docs/architecture/POINT_IN_TIME_TECHNICAL_FEATURES_V0_1.md`
> Tool decision: `USE_EXISTING` (no new tool adopted)
> Base: origin/main `64771245acf5e445adc59eb5ef71afcb0ef00777`

## 1. Authority and boundaries

Ordinary generic engineering under the 2026-08-20 parallel work package Lane G
(`docs/research/PARALLEL_WORK_PACKAGE_2026-08-20_V0_3.md`). It is independent of
whether Raschke Holy Grail reaches PRIMARY or outcome testing.

Binding boundaries preserved:

```text
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
PERFORMANCE_RESEARCH_STARTED=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
NO_CANDIDATE_OUTCOME_DATA_USED=YES
REAL_CANDIDATE_DATA_USED=NO
```

Frozen facts preserved unchanged: `SOURCE CLAIM != PROJECT/AI INTERPRETATION
!= MACHINE OPERATIONALIZATION`; the 12/6/6 split; the pre-outcome firewall
fail-closed state. This lane modifies no frozen research semantics and no
existing source module's behavior (the only existing-module change is the
additive `SessionMetadata.window_at` accessor in `src/data_substrate.py`).

## 2. Implementation owner / module

Single owner of the generic point-in-time feature layer:
`src/technical_features.py`.

Reused (not replaced) existing machinery: `NormalizedHistoricalBar`,
`CompletedBar`, `BarQuality`, `SessionWindow`, `SessionMetadata` from
`src/data_substrate.py` / `src/historical_data.py`.

New surface:

```text
TimeframeSpec            explicit, versioned aggregation spec (INTRADAY / DAILY)
AggregatedBar            point-in-time aggregate (identity + availability)
IncompleteBucket         fail-closed record of a bucket with missing constituents
AggregationResult        aggregates + incomplete buckets
TimeframeAggregator      session-aware aggregation from 1-minute bars
visible_aggregates        availability-filter helper
EMASpec -> compute_ema    deterministic EMA (FeatureValue per aggregate)
wilder_directional_movement  raw TR / +DM / -DM per aggregate
compute_adx              deterministic Welles Wilder ADX (ADXValue per aggregate)
FeatureValue / ADXValue  versioned feature values with full identity binding
visible_features          availability-filter helper for feature values
```

No second historical-data model is introduced. The module never reads the
canonical candidate corpus and imports no outcome-access machinery.

## 3. Design decisions

### 3.1 Session-aware aggregation

- Intraday buckets align from each explicit `SessionWindow.start`; a bucket is
  emitted only when every required 1-minute constituent bar exists.
- Breaks (session break, lunch/night) are never bridged; a 60m request over two
  30m windows separated by a lunch break yields zero aggregates.
- Daily aggregation groups by the official `trading_day` (night bars opening
  for a later official day are aggregated with that day's day session), never
  by the civil calendar date.

### 3.2 Point-in-time availability

- `AggregatedBar.available_at = max(constituent CompletedBar.available_at)`.
- EMA/ADX values compute their availability as the latest `available_at` over
  the whole prefix they depend on, so a delayed later constituent cannot
  retroactively "make available" an earlier feature value.

### 3.3 EMA

- First EMA = SMA of the first `period` observations; then
  `alpha = 2/(period+1)` recursive update.
- Warmup: status `INSUFFICIENT_HISTORY` (value `None`) before `period`
  observations.

### 3.4 Welles Wilder ADX

- Raw TR/+DM/-DM per `wilder_directional_movement`.
- Wilder smoothing (sum-seed then decay), never an EMA-style substitution.
- +DI/-DI from smoothed values; DX from the smoothed +DM/-DM directly
  (algebraically identical to the DI ratio form, without inheriting DI output
  quantization).
- First ADX = simple average of the first `period` DX values; recursive update
  `ADX_t = (ADX_(t-1)*(period-1) + DX_t)/period`.
- Warmup (period P): first ADX at aggregate index `2*P - 1`; earlier values are
  `INSUFFICIENT_HISTORY`. Zero directional denominators fail closed as
  `UNDEFINED`.

### 3.5 Numeric determinism

- Exact `Decimal` for OHLCV aggregation.
- Derived ratios quantized to `0.000001` (`ROUND_HALF_UP`) as documented
  ENGINEERING FEATURE SEMANTICS. Period 2 hand-computed ADX fixture and period 3
  hand-computed EMA fixture are exact.

## 4. Verification

Focused suite:

```text
python -m unittest tests.test_technical_features -v
Ran 35 tests in 0.146s  OK
```

Full canonical verification path:

```text
python -m unittest discover -s tests -v
Ran 338 tests in 1.683s  OK (skipped=3)
```

`git diff --check` clean. No `CURRENT_STATE.md` change (integration-owned).

## 5. Required-capability mapping

| Requirement | Coverage |
| --- | --- |
| 1m -> 5m OHLCV correctness | `test_one_minute_to_five_minute_ohlcv_correctness` |
| 1m -> 30m correctness | `test_one_minute_to_thirty_minute_correctness` |
| no bridging session break | `test_session_break_is_never_bridged`, `test_lunch_break_is_never_bridged_to_fill_a_sixty_minute_bucket` |
| night session uses official trading day | `test_night_session_uses_official_trading_day` |
| daily aggregation follows official trading day, not civil date | `test_daily_aggregation_follows_official_trading_day_not_civil_date` |
| missing constituent minute fails closed | `test_missing_constituent_minute_fails_closed` |
| aggregate available_at respects latest constituent | `test_aggregate_available_at_respects_latest_constituent` |
| future bar cannot affect earlier aggregate | `test_future_bar_cannot_affect_earlier_aggregate`, `test_future_availability_does_not_earlier_visibility` |
| EMA known hand-computed sequence | `test_ema_known_hand_computed_sequence` |
| EMA insufficient-history behavior | `test_ema_insufficient_history_behavior` |
| EMA identity changes with price field/period | `test_ema_identity_changes_with_price_field_and_period` |
| Wilder TR/+DM/-DM hand cases | `test_wilder_tr_plus_dm_minus_dm_hand_cases` |
| Wilder ADX hand-computed fixture | `test_adx_hand_computed_fixture` |
| ADX insufficient-history behavior | `test_adx_insufficient_history_behavior` |
| ADX no future leakage | `test_adx_no_future_leakage` |
| feature identity stable for equivalent evidence | `test_ema_identity_stable_for_equivalent_evidence`, `test_adx_identity_changes_with_period_and_evidence` |
| feature identity changes with algorithm/input | `test_feature_value_identity_binds_algorithm_version`, `test_feature_identity_changes_with_input_evidence` |
| input ordering strictly validated | `SeriesValidationTests` (out-of-order, duplicate, outside sessions, overlap, mixed timeframe) |
| volume UNKNOWN preserved (not fabricated zero) | `test_volume_unknown_is_preserved_not_fabricated_as_zero` |

## 6. Engineering semantic declarations (not source claims)

The following are recorded as project machine conventions, not as Raschke or
any other human-source claims:

- EMA initialization: first EMA = SMA of the first `period` observations;
  recursive alpha = 2/(period+1).
- ADX initialization: first ADX = simple average of the first `period` DX
  values; recursive Wilder update.
- ADX warmup: first ADX at aggregate index `2*period - 1`.
- Feature output quantization: 6 decimal places, `ROUND_HALF_UP`.
- Degenerate (zero-denominator) ADX input fails closed as `UNDEFINED`.

These are generic engineering semantics; the Raschke source 20 EMA / 14 ADX
remain later contract inputs.

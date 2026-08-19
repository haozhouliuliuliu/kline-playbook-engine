# POINT_IN_TIME_TECHNICAL_FEATURES_V0_1

> Version: 0.1
> Date: 2026-08-20
> Status: ARCHITECTURE_ADDENDUM / GENERIC_ENGINEERING (Lane G of the 2026-08-20 three-lane pre-outcome package)
> Scope: deterministic session-aware timeframe aggregation + EMA + Welles Wilder ADX + versioned feature identities, all point-in-time
> Parent: `ARCHITECTURE_BASELINE.md` (Skeleton v1.0 — not redesigned)

## 1. Purpose

Skeleton v1.0 requires a data substrate that owns "tick/bar and
multi-timeframe generation" and "point-in-time availability boundaries", and
a research loop that may build deterministic non-outcome operationalization
machinery. The Architecture Baseline also states that any feature definition
must be versioned (`feature_version`) and subject to leakage controls.

This addendum defines the smallest deterministic **generic point-in-time
technical feature layer** required before any real machine Playbook can run:

```text
completed 1-minute NormalizedHistoricalBar
  -> session-aware timeframe aggregation (explicit intervals)
  -> point-in-time EMA
  -> point-in-time Welles Wilder ADX
  -> versioned feature identities / availability boundaries
```

It is deliberately independent of any specific human-source playbook (for
example Raschke Holy Grail) and of whether that playbook ever reaches PRIMARY
or outcome testing. It is NOT strategy research, parameter optimization, or
candidate outcome inspection.

## 2. Boundaries

```text
NO_CANDIDATE_DATA_USED=YES
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

- Only synthetic/non-candidate bars are used in tests.
- No candidate signals, candidate returns, PnL, or performance charts.
- The module never reads the canonical real 2024/2025 candidate corpus.
- No period/price-field is selected or tuned from performance; they are always
  explicit caller inputs. The Raschke source 20 EMA / 14 ADX are later contract
  inputs, never hard-coded research selection here.

## 3. Reused structures (no second historical-data model)

The layer reuses the existing governed structures and introduces no competing
data model:

| Existing structure | Reuse |
| --- | --- |
| `NormalizedHistoricalBar` | 1-minute completed input bars (OHLCV + `identity_id`) |
| `CompletedBar` | start/end/trading_day/`available_at` visibility semantics |
| `SessionWindow` | explicit session start/end/kind; bucket alignment source |
| `SessionMetadata` | official trading-day identity; `window_at` accessor (additive) |
| `BarQuality` | partial/reconnect quality preserved on constituent bars |

`SessionMetadata.window_at` was added as a small public accessor so bucket
alignment uses the explicit session-window start; no exchange session is ever
inferred from weekday/civil time.

## 4. Timeframe aggregation

`TimeframeSpec(name, kind, interval_seconds, aggregation_version)` supports:

- `kind="INTRADAY"` with arbitrary positive `interval_seconds`
  (5m/15m/30m/60m/120m are tested but are not hard-coded limits);
- `kind="DAILY"` — one aggregate per official trading day.

Intraday rules:

- buckets align from each explicit session-window start;
- buckets never bridge an exchange session break;
- lunch/night breaks are never bridged merely to fill a bucket;
- a bucket is emitted only when every required constituent bar exists
  (missing constituents are recorded as `IncompleteBucket`, fail closed);
- no silent filling of missing 1-minute bars.

Daily rules:

- one aggregate per official `trading_day` over all of its valid session
  windows (night + day belong to the same official trading day);
- never uses the civil calendar date as the daily grouping key.

OHLCV aggregation for a valid aggregate:

```text
open   = first constituent open
high   = max constituent high
low    = min constituent low
close  = last constituent close
volume = sum of constituent volumes when ALL are present
       = None / volume_status=UNKNOWN when any constituent volume is absent
```

Missing volume is preserved as explicit `UNKNOWN`, never fabricated as zero.

## 5. Point-in-time availability

An aggregated bar is NOT visible before all its constituent completed bars are
available:

```text
AggregatedBar.available_at = max(constituent CompletedBar.available_at)
```

`AggregatedBar.is_visible_at(t)` and `visible_aggregates(aggregates, t)` make
the boundary explicit. A feature at time T may use only aggregate bars whose
availability <= T. No future constituent bar leaks into OHLC, volume, EMA,
ADX, or feature identity.

## 6. Aggregated bar identity

`AggregatedBar.identity_id` binds deterministically:

- source normalized bar identities (`source_bar_identities`, sorted);
- exchange, concrete instrument;
- official trading day;
- timeframe/aggregation spec identity (name + kind + interval + version);
- session metadata version;
- aggregate OHLCV;
- aggregate start/end;
- aggregate `available_at`.

Equivalent input evidence produces the same identity; changed source evidence
changes it.

## 7. EMA

Deterministic generic EMA. Inputs are explicit:

```text
period
price_field  (open | high | low | close)
feature_version
```

Initialization rule (recorded as ENGINEERING FEATURE SEMANTICS, not a Raschke
source claim):

```text
first EMA = SMA of the first `period` observations
subsequent:
  alpha = 2 / (period + 1)
  EMA_t = alpha * price_t + (1 - alpha) * EMA_(t-1)
```

Before `period` observations the status is `INSUFFICIENT_HISTORY` (value
`None`); a silent zero/NaN is never treated as a feature.

## 8. Welles Wilder ADX

Deterministic standard Welles Wilder directional-movement semantics. Feature
spec includes `period` and `feature_version`; the engine supports an explicit
period (default test period 14 is never hard-coded).

Documented exactly:

```text
TR    = max(high - low, |high - prev_close|, |low - prev_close|)
+DM   = high - prev_high  when positive and > (prev_low - low), else 0
-DM   = prev_low - low    when positive and > (high - prev_high), else 0
Wilder smoothing: first smoothed value = sum of first `period` raw values;
                  S_t = S_(t-1) - S_(t-1)/period + raw_t
+DI   = 100 * S_plus / S_tr
-DI   = 100 * S_minus / S_tr
DX    = 100 * |S_plus - S_minus| / (S_plus + S_minus)
ADX init: first ADX = simple average of the first `period` DX values
ADX update: ADX_t = (ADX_(t-1) * (period - 1) + DX_t) / period
```

Warmup rule (off-by-one exact), with period P:

```text
raw TR/+DM/-DM      from aggregate index 1
Wilder smoothed     from aggregate index P
+DI / -DI / DX      from aggregate index P
first ADX           at aggregate index 2*P - 1
```

Before that, status is `INSUFFICIENT_HISTORY`. When a directional denominator
is zero (degenerate input), DI/DX/ADX are `UNDEFINED` (fail closed), never a
fabricated value. An EMA-style smoothing is never substituted for Wilder
smoothing.

## 9. Feature identity

Every emitted feature value binds:

- feature type (`EMA` | `ADX`);
- algorithm/version (`sma-seed-recursive-v1` | `wilder-directional-movement-v1`);
- explicit parameters (e.g., `period`, `price_field`);
- `feature_version`;
- timeframe aggregation identity (timeframe spec + session metadata version);
- source aggregate identity;
- availability boundary (`available_at`);
- status and value.

Changing `period`, `price_field`, algorithm, input evidence, or timeframe
changes the identity. Equivalent evidence produces the same identity.

## 10. Numeric policy

- OHLCV aggregation is exact `Decimal` arithmetic (no rounding).
- Derived EMA/ADX ratios use `Decimal` with an explicit documented output
  quantization: 6 decimal places, `ROUND_HALF_UP`. This is an engineering
  convention for deterministic reproducible output (ENGINEERING FEATURE
  SEMANTICS); it is not market-data rounding and never touches stored prices.

## 11. Input policy

Input series (bars or aggregates) must be strictly ordered, timezone-aware,
and duplicate/overlap-free. Ambiguous chronology is rejected, never silently
reordered or accepted.

## 12. Artifacts

```text
src/technical_features.py            implementation (single owner)
tests/test_technical_features.py     35 tests, synthetic/non-candidate bars only
docs/evidence/POINT_IN_TIME_TECHNICAL_FEATURES_ENGINEERING_V0_1.md   engineering evidence
```

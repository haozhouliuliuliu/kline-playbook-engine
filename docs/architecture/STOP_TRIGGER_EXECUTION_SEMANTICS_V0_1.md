# STOP Trigger Execution Semantics v0.1 (Architecture)

> Status: CANDIDATE (Lane H engineering artifact, not yet integrated to `main`)
> Lane: `parallel/stop-trigger-observation-v01`
> Role: GENERIC_STOP_TRIGGER_EXECUTION_ENGINEER
> Base: `origin/main` = `64771245acf5e445adc59eb5ef71afcb0ef00777`

## 1. Purpose

The existing validation runner executes only `NEXT_TRADABLE_OBSERVATION`
market-like execution: `OrderSpecification` carries quantity/action/direction
but has no explicit stop trigger or stop-price semantics.  This document
defines a smallest reusable layer that converts a RESTING STOP ORDER plus future
completed OHLC bars into an existing-compatible `ExecutionObservation`.

This is **generic deterministic execution engineering**.  It is NOT:

- candidate strategy logic;
- trailing-stop strategy design;
- a backtest;
- outcome inspection;
- Holy Grail-specific stop calculation (no swing-low identification, no trailing
  rule invention, no profit-target logic).

## 2. Engineering execution assumption (versioned)

The trigger rule below is recorded as an **ENGINEERING EXECUTION ASSUMPTION**
(`STOP_MARKET_TRIGGER_MODEL_V0_1`), not as human-source semantics.  It is a
deterministic machine convention for turning completed OHLC bars into a
stop-trigger execution reference price without inventing an intrabar tick path.

## 3. Data model

New module: `src/stop_order_execution.py`

| Type | Role |
| --- | --- |
| `StopSide` | `BUY_STOP` / `SELL_STOP` |
| `RestingStopOrder` | explicit resting stop: `request_id`, `side`, `stop_price`, `active_at`, `trigger_model_version`, `instrument`, optional `concrete_contract_id`, optional `oco_group_id` |
| `StopTriggerResult` | deterministic result: outcome, sequence certainty, triggering bar identity, reference execution price, deterministic `identity_id` |
| `evaluate_stop_order(...)` | evaluate one resting stop against ordered completed bars; first eligible trigger wins |
| `evaluate_stop_group(...)` | evaluate a set of stops, failing closed on same-bar OCO ambiguity |
| `stop_trigger_result_to_execution_observation(...)` | bridge an unambiguous trigger into the existing `ExecutionObservation` |

`RestingStopOrder` requirements:

- `request_id`, `side`, `stop_price`, `active_at`, `trigger_model_version`,
  `instrument` are required.
- `stop_price` must be a positive `Decimal`.
- `active_at` must be timezone-aware.
- When contract metadata is available, `stop_price` must be on the contract
  minimum tick (validated at evaluation time against the supplied
  `ContractSpecification`; an off-tick stop is rejected with `ValueError`).
- The order binds to exactly one concrete instrument space:
  `concrete_contract_id` when set, else `instrument`.  Supplied bars must match
  that binding.

## 4. Point-in-time activation

A stop order may only evaluate bars occurring AFTER it became active.  A bar
that was already completed/known before `active_at` can never trigger the stop.

For one completed bar relative to `active_at`:

```text
bar.end <= active_at          -> bar already finished before/at activation
                                 -> NOT ELIGIBLE (never triggers)
active_at < bar.start         -> order strictly active before the bar's trigger
                                 interval -> ELIGIBLE
active_at == bar.start        -> boundary case (see 7 below)
bar.start < active_at < bar.end -> order became active INSIDE the bar
                                 -> see 7 below
```

Chronology is explicit.  The first eligible trigger wins; no same-decision
future bar access; an optional `cutoff_at` restricts evaluation to bars that are
already available (`bar.available_at <= cutoff_at`), so a future bar cannot be
visible too early.

## 5. Basic trigger rule

Using `NormalizedHistoricalBar` (the existing authoritative OHLC-bearing type;
no fake OHLC structure is created):

```text
BUY_STOP : trigger if eligible bar.high >= stop_price
SELL_STOP: trigger if eligible bar.low  <= stop_price
```

## 6. Gap-through reference price (STOP-MARKET bar rule)

`STOP_MARKET_TRIGGER_MODEL_V0_1` reference price for an eligible bar:

```text
BUY_STOP:
  - if bar.open >= stop_price: reference execution price = bar.open
  - elif bar.high >= stop_price: reference execution price = stop_price
  - else: no trigger

SELL_STOP:
  - if bar.open <= stop_price: reference execution price = bar.open
  - elif bar.low <= stop_price: reference execution price = stop_price
  - else: no trigger
```

The reference price then enters the existing execution/slippage layer.  No
synthetic slippage is added twice: `ExecutionAssumptions.synthetic_slippage`
remains the single downstream slippage authority.

## 7. Unknown intrabar time and fail-closed ambiguity

OHLC bars do not identify the exact intrabar path.  The module never fabricates
a tick sequence and never invents an exact intra-minute timestamp.  The trigger
evidence preserves: bar start, bar end, bar `available_at`, trigger side, stop
level, reference execution price, and sequence certainty.

### 7.1 Same-bar activation ambiguity

If an order becomes active INSIDE a bar (`bar.start < active_at < bar.end`) and
the threshold was crossed somewhere in that bar, OHLC alone cannot establish
whether the threshold was crossed before or after activation.  The module FAILS
CLOSED with `AMBIGUOUS_INTRABAR_SEQUENCE`; it never assumes the favorable
ordering.

If the threshold was NOT crossed in the straddling bar, the stop could not have
triggered at any point in that bar, so there is no ambiguity and evaluation
continues.

### 7.2 Boundary activation (`active_at == bar.start`)

The open print is coincident with activation:

- If the OPEN crossed the threshold (BUY_STOP `open >= stop`, SELL_STOP
  `open <= stop`), the module cannot establish whether the order was already
  resting before the open print -> FAIL CLOSED with
  `AMBIGUOUS_INTRABAR_SEQUENCE`.
- Otherwise any later high/low crossing is strictly after activation and is a
  genuine unambiguous trigger.

## 8. OCO / two-sided ambiguity

If two resting stops in the same OCO/bracket group (`oco_group_id`) can both
trigger inside the same minimum-resolution bar and there is no finer path, the
module does NOT arbitrarily choose one.  `evaluate_stop_group` returns
`AMBIGUOUS_INTRABAR_SEQUENCE` for the conflicting orders (and any order whose
first trigger is at or after the conflict bar, since the group state is then
unknowable).  This is especially important for future bracket-entry /
protective-stop logic.

The group evaluator detects same-bar trigger ambiguity only; it does NOT
implement one-cancels-other cancellation semantics (that is downstream
strategy/position logic).  Orders with no `oco_group_id` are evaluated
independently with no cross-order ambiguity.

## 9. Higher-timeframe strategies use the underlying 1-minute path

The project owns 1-minute bars.  A future 30m/60m strategy should use the
underlying 1-minute path for stop triggering when that path is available, rather
than using higher-timeframe OHLC and guessing intrabar ordering.  The trigger
layer consumes generic ordered `NormalizedHistoricalBar` inputs (1-minute or
otherwise) and remains independently usable, so a higher-timeframe strategy can
feed the underlying 1-minute bars directly.

## 10. Protective stops share the same mechanism

Entry stops and protective exit stops use the SAME generic trigger mechanism.
A long position's protective `SELL_STOP` and a short position's protective
`BUY_STOP` both flow through `evaluate_stop_order` and the same bridge.  This
lane does NOT decide how a trailing stop moves, how a swing low is found, or
profit-target logic; it only evaluates a stop level that has already been
supplied.

## 11. ExecutionObservation bridge

On an unambiguous trigger, `stop_trigger_result_to_execution_observation`
emits the existing `ExecutionObservation` with:

- the same request identity;
- the authoritative bar availability timestamp (`bar.available_at`);
- the deterministic reference execution price (no slippage applied here);
- tradable state (`True`);
- the concrete contract identity where the order is bound.

`ExecutionAssumptions.synthetic_slippage` / `synthetic_fee` remain the single
downstream slippage and additive-cost authorities.  No double slippage, no
double cost.

## 12. Price limit / contract facts

The stop-trigger layer is NOT a second price-limit authority.  `ContractSpecification`
minimum tick / price-limit facts / session metadata remain owned by
`src.contract_semantics` and `src.data_substrate`.  Where contract metadata is
supplied the module validates stop-price tick conformance; final price-limit
enforcement stays in the existing runner.

## 13. Boundaries

- Synthetic/non-candidate bars only.
- No candidate PnL, canonical outcome inspection, parameter optimization,
  Validation, or final holdout access.
- No Holy Grail-specific stop calculation, trailing rule invention, or frozen
  Protocol change.
- `NO_CANDIDATE_OUTCOME_DATA_USED=YES`.

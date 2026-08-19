# Completed Round-Trip Ledger v0.1 (Architecture)

> Status: CANDIDATE (Lane D engineering artifact, not yet integrated to `main`)
> Lane: `parallel/completed-round-trip-ledger-v01`
> Role: COMPLETED_ROUND_TRIP_LEDGER_ENGINEER
> Base: `origin/main` = `2b197f9b1a72471cbd338e6392d920bf48b58cd1`

## 1. Purpose

The project needs a canonical completed-trade evidence unit so that downstream
Playbook evidence, validation reporting, statistical-profile implementation, and
observability can reason about **completed trades** instead of raw order or
transition records.

This ledger is **mandatory generic execution infrastructure**. It is independent
of which Human Playbook family eventually survives.

## 2. Binding identity rule

```text
ONE position_id  ==  ONE completed round trip
```

- `OPEN` begins a round trip with a fresh `position_id`.
- `ADD` keeps the **same** `position_id` and therefore the **same** round trip.
- `PARTIAL CLOSE` keeps the **same** `position_id`, aggregates into the **same**
  round trip, and leaves the round trip **OPEN** until quantity reaches zero.
- `FORCED LIQUIDATION` is a terminal close of the **same** round trip with
  `forced_liquidation=True`.
- `FULL NATURAL CLOSE` is a terminal close.
- A later new position must receive a **distinct** `position_id` and therefore a
  **distinct** round trip.

The ledger **never counts a partial close as a separate trade**. Counting partial
closes as separate trades would inflate `N` and corrupt later statistics. This is
the central correctness property of the module.

## 3. Relationship to the existing lifecycle

The ledger does **not** invent a second position lifecycle. It consumes the exact
authoritative transition records already produced by the existing lifecycle:

- `src.validation_runner.CapitalTransition` / `CapitalSnapshot` are the input
  evidence stream (the same records consumed by `src.portfolio_semantics`).
- The `position_id` lifecycle (OPEN / ADD / partial CLOSE / full CLOSE / forced
  liquidation) is owned by `ChronologicalValidationRunner._apply_capital_constraints`
  and `_evaluate_forced_liquidation`; the ledger only **groups and aggregates**
  that evidence.

No strategy, backtest, ranking, or statistical logic lives in this module.

## 4. Data model

New module: `src/round_trip_ledger.py`

- `CompletedRoundTrip` — immutable frozen record of one completed round trip.
- `RoundTripLedger` — immutable container of completed round trips plus the set
  of still-open `position_id`s that were **not** materialized as completed.
- `RoundTripMaterializer` — groups an ordered authoritative transition stream by
  `position_id`, enforces lifecycle integrity, aggregates quantities / PnL /
  costs, resolves official trading day/week, and emits a deterministic ledger
  identity.

`CompletedRoundTrip` captures (where available):

| Field | Source authority |
| --- | --- |
| `position_id` | existing snapshot identity (binding key) |
| `instrument` | snapshot `position_instrument` |
| `concrete_contract_id` | snapshot `concrete_contract_id` |
| `direction` | snapshot `position_direction` |
| `opened_at` | OPEN transition `after.state_at` |
| `terminal_closed_at` | terminal transition `after.state_at` |
| `terminal_reason` | `FULL_CLOSE` / `FORCED_LIQUIDATION` |
| `forced_liquidation` | terminal transition type |
| `opening_transition_references` | OPEN + ADD transition `reference_id`s |
| `reducing_transition_references` | CLOSE + liquidation transition `reference_id`s |
| `source_transition_references` / `source_outcome_references` | ordered evidence refs |
| `total_opened_quantity` / `total_closed_quantity` | summed `quantity_change` |
| `average_open_price` | terminal `before.average_open_price` (weighted basis) |
| `gross_realized_pnl` | summed `realized_pnl_change` over reducing transitions |
| `charged_costs` | summed `required_cost` over all transitions |
| `entry/exit_official_trading_day` | `SessionMetadata.trading_day_at` |
| `entry/exit_official_trading_week` | `SessionMetadata.trading_week_at` |
| `active_official_trading_days` | official days with lifecycle activity |
| `ledger_identity` | deterministic sha256 over ordered evidence |
| `net_realized_result` | derived property = gross − charged (not a new authority) |

## 5. Cost / PnL authority (single path, no double counting)

The project already distinguishes execution cost (`ExecutionOutcome.total_cost`)
from capital-charged cost (`CapitalTransition.required_cost`). After inspecting
both, the ledger chooses **one** authoritative additive-cost path:

```text
ADDITIVE_COST_AUTHORITY = CapitalTransition.required_cost
```

- Every filled transition is charged **exactly once** via `required_cost`
  (`OPEN`/`ADD`: synthetic fee; `CLOSE`: synthetic fee + offset fee; forced
  liquidation: synthetic fee).
- `ExecutionOutcome.total_cost` (constrained) is used **only as a cross-check**;
  when supplied, the materializer fails closed if it disagrees with
  `required_cost`. It is never a second summation source.
- **Slippage is already embedded in the fill price** and therefore in gross
  realized PnL. It is **not** added again as a fee.
- `gross_realized_pnl` = sum of `CapitalTransition.realized_pnl_change` over the
  round trip's reducing transitions (OPEN/ADD contribute zero).
- `net_realized_result = gross_realized_pnl - charged_costs` is a derived
  property because both inputs are authoritative; it is not a new authority.

## 6. Official trading day / week authority

TD-001 is resolved (merged from `parallel/execution-evidence-td001-td002-v01`).
`SessionMetadata` is the single trusted trading-day authority.

- When `SessionMetadata` + `exchange` are supplied to the materializer, every
  lifecycle timestamp is mapped through `trading_day_at` and `trading_week_at`.
- Weekly attribution derives from the **official trading-day identity**, never
  from the raw civil timestamp (a Friday 21:30 night-session fill is attributed
  to the Monday official trading day and that day's ISO week).
- The resolved official day must agree with the snapshot's `position_trading_day`;
  a mismatch fails closed.
- A timestamp outside any published session window fails closed instead of
  guessing a missing day.
- Without `SessionMetadata`, the ledger falls back to the snapshot
  `position_trading_day` (itself SessionMetadata-derived upstream) and derives
  the week from that official day's ISO calendar.

### Active / holding-day information

`active_official_trading_days` reports **only** the official trading days on
which lifecycle activity (transitions) is recorded — derived faithfully from
authoritative transition data. It is **not** an inclusive holding-period day
count. Computing inclusive active days (including no-event holding days) requires
an explicit event/mark stream dependency; that dependency is **not** guessed and
fails closed rather than fabricating missing days.

## 7. Lifecycle integrity rules (fail closed)

The materializer enforces, rather than assumes:

- A new `position_id` must begin with an OPEN from a flat state.
- A `position_id` cannot be reopened after its round trip completes.
- A transition cannot move between `position_id`s.
- A round trip cannot silently merge unrelated contract positions (instrument
  identity is invariant) and cannot change direction.
- A terminal close must be a `POSITION_CLOSE` or `FORCED_LIQUIDATION` transition.
- A completed round trip must have a balanced quantity identity
  (`total_closed == total_opened`).
- A flat no-op transition cannot charge cost or realize PnL.
- Transitions must be in lifecycle (chronological) order.
- Rolls do not silently merge unrelated contract positions; each round trip is
  bound to exactly one contract/direction.

## 8. Integration boundary

The ledger is deliberately decoupled:

- It is usable later by Playbook evidence, validation reporting,
  statistical-profile implementation, and observability — but **no consumer is
  implemented in this lane**.
- It is not coupled to Raschke, Grimes, or any candidate family.
- It locks **no statistical threshold** and performs **no performance ranking**.

## 9. Boundaries of this lane

- Synthetic / non-candidate fixtures only.
- No canonical candidate outcomes, no cross-strategy PnL comparison, no ranking,
  no parameter search, no validation/historical-final access, no statistical
  acceptance thresholds, no frozen Protocol changes.
- `CURRENT_STATE.md` is not modified.
- `NO_CANDIDATE_OUTCOME_DATA_USED=YES`.

# HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1

> Version: 1.0
> Date: 2026-08-19
> Status: AUDIT_COMPLETE / READ_ONLY / NO_CANDIDATE_OUTCOME / NO_STATISTICAL_STANDARD_SELECTED
> Work package: `HUMAN_PLAYBOOK_STATISTICAL_ENGINE_CAPABILITY_AUDIT_V1` (parallel worker)
> Branch: `parallel/stat-engine-audit`
> Audit type: engineering capability audit of the existing code — what statistical inputs it can
> reliably produce today, and what it cannot.
> Companion worker (not consulted for conclusions): `COMMON_STATISTICAL_PROFILE_V1_CANDIDATE`
> Frozen authority unchanged: `docs/research/HUMAN_PLAYBOOK_RESEARCH_PROTOCOL_V1_0.md`
> Frozen chronology unchanged: `docs/research/HUMAN_PLAYBOOK_CHRONOLOGICAL_SPLIT_V1_0.md`

This audit is read-only. It does not run a real Human Playbook, does not inspect candidate PnL,
expectancy, Sharpe, win/loss, does not open validation or the historical final holdout, and does not
select any numeric statistical standard. It reports only what the current project code can and cannot
reliably produce as statistical input. `COMMON_STATISTICAL_PROFILE_V1` numeric/method choices are
left to its designer.

---

## EXECUTIVE_VERDICT

The current code reliably produces and is regression-tested on the following statistical inputs at
the **single-position lifecycle** and **single-decision-point portfolio** level:

- realized PnL, cash balance, charged transaction/execution costs;
- unrealized PnL and equity along the **mark-to-market path** (no partial close);
- instrument identity, concrete contract identity, point-in-time contract mapping/roll identity;
- timestamps and trading-day identity (authoritative `SessionMetadata` path only);
- per-order realized PnL contribution (`CapitalTransition.realized_pnl_change`);
- single-decision-point simultaneous cross-instrument / same-direction separate sleeve positions
  with shared-capital reconciliation (portfolio layer).

It does **not** currently produce, as materialized statistics:

- equity curve over multiple days, drawdown path, portfolio-day aggregation, portfolio aggregate
  return percentage, turnover aggregation, holding duration, active/no-trade day aggregation,
  exposure-duration fields, per-hypothesis/per-wave event counts.

These are all **derivable with small engineering deltas** from already-recorded facts (timestamps,
trading-day identity, transitions, evidence records), except the multi-day portfolio/equity series,
which requires a medium delta (a multi-day portfolio loop does not exist today).

Three known technical-debt items pollute or block specific statistics:

- **TD-001** (duplicate trading-day authority) is a drift risk: it only pollutes trading-day
  aggregation if a consumer wrongly uses the bootstrap calendar instead of `SessionMetadata`.
- **TD-002** (partial-close unrealized-PnL zeroing) concretely pollutes the equity/unrealized path,
  drawdown, intermediate holding-period mark series, and portfolio aggregate **at partial-close
  snapshots only**; it does not pollute realized PnL of the closed portion or final realized totals.
- **LIMIT-001** (ungoverned historical price-limit metadata) does **not** silently pollute — the
  execution semantics fail closed when a required limit fact is missing. It **blocks** producing
  contract-bound confirmatory PnL over the real corpus until governed facts are bound.

Verdict: `CODE_CAPABILITY = MOSTLY_SINGLE-POSITION-LIFECYCLE_READY`; `DAY_SERIES_AND_AGGREGATE_STATS = NOT_MATERIALIZED_BUT_DERIVABLE`; `MULTI_DAY_PORTFOLIO_SERIES = REQUIRES_MEDIUM_DELTA`; `NO_UNSAFE_SILENT_PNL = TRUE` (fail-closed execution).

---

## 1. Supported statistical primitives (SUPPORTED_AND_TESTED)

Each row names the code anchor and the regression test that proves it.

| # | Primitive | Code anchor | Test evidence |
|---|-----------|-------------|---------------|
| 1 | **realized PnL** | `CapitalSnapshot.realized_pnl`, `CapitalTransition.realized_pnl_change` (`src/validation_runner.py`); partial-close realized uses `(fill_price - average_open_price) * qty * multiplier * sign` | `tests/test_position_capital_lifecycle.py` (`realized_pnl == Decimal("-64.0")`, liquidation realizes once), `tests/test_capital_margin_constraints.py`, `tests/test_portfolio_semantics.py` (sleeve/shared realized reconciliation) |
| 4 | **cash balance** | `CapitalSnapshot.cash_balance = starting_capital + realized_pnl - charged_costs` | exercised by equity tests and portfolio reconciliation tests; deterministic identity in `reference_id` |
| 5 | **transaction / execution costs** | `ExecutionAssumptions.synthetic_fee`, `synthetic_slippage`; `OffsetCostAssumptions.close_today_fee_per_unit` / `close_previous_fee_per_unit`; accumulated in `CapitalSnapshot.charged_costs` | `tests/test_contract_execution_semantics.py` (offset-sensitive cost identity), `tests/test_execution_realism.py` (assumption identity/costs deterministic and outcome-affecting), `tests/test_capital_margin_constraints.py` |
| 10 | **instrument identity** | `CompletedBar.instrument`, `CapitalSnapshot.position_instrument`, `PortfolioCandidate.requested_symbol`, `ExecutionObservation` contract binding | cross-cutting (`test_validation_runner`, `test_contract_execution_semantics`, `test_portfolio_semantics`) |
| 11 | **concrete contract identity** | `ContractMaster`, `ContractMappingSchedule`, `ContractResolution` (`src/contract_semantics.py`); `concrete_contract_id`, `contract_identity_id`, `mapping_entry_identity_id` on `CapitalSnapshot` / `ExecutionOutcome` / `AttributedPosition` | `tests/test_contract_execution_semantics.py` (master identity, PIT main resolution, roll cannot silently replace open contract, pseudo-symbol rejected, on-tick/in-limit fill binding) |
| 12 | **timestamps / trading-day identity** | `CompletedBar.trading_day`, `CapitalSnapshot.position_trading_day`, `SessionMetadata.trading_day_at(exchange, instrument, ts)` (`src/data_substrate.py`); today/previous quantity buckets and close-today/close-previous offsets | `tests/test_contract_execution_semantics.py` (`trading_day_transition_ages_today_bucket_using_session_authority`, close-offset bucket checks, `bar trading day is inconsistent with explicit contract session metadata` fail-closed) |
| 15a | **per-event PnL contribution** (realized, per order) | `CapitalTransition.realized_pnl_change` on every order execution; `POSITION_TRANSITION` evidence with `CREATED_OR_INCREASED` / `CLOSED_OR_REDUCED` | position lifecycle tests assert exact `realized_pnl_change`; evidence binding tests assert transition references |
| 14a | **simultaneous cross-instrument positions (single decision point)** | `PortfolioCoordinator.evaluate` (`src/portfolio_semantics.py`): multiple candidates at one `decision_at` across instruments/strategies, shared capital, per-sleeve attribution, `reconcile_portfolio` | `tests/test_portfolio_semantics.py` (same-direction separate sleeves reconcile; shared capital avoids double spending; identity/policy sensitive) |
| 13a | **same-direction overlapping positions (single decision point)** | `same_direction_rule = "ALLOW_SEPARATE"` → two strategies hold separate positions on the same contract; opposing opens at same `decision_at` arbitrated `FIRST_DIRECTION_WINS` | `tests/test_portfolio_semantics.py` (opposing-intent loser never executes; separate attribution) |

Additional supported-and-tested guarantees that are statistical prerequisites:

- Deterministic replay: identical inputs → identical snapshots, transitions, liquidation, evidence
  identities (`test_identical_history_produces_identical_snapshots_and_evidence`,
  `test_identical_confirmatory_runs_have_identical_execution_evidence`,
  `test_repeated_history_has_identical_mapping_execution_position_and_evidence`).
- Chronological enforcement: inputs/observations/marks must be strictly ordered; reordering fails
  closed (`test_impossible_input_order_fails_closed_instead_of_reordering`).
- Identity binding: assumptions, contract, mapping, session, offset-cost identities are
  outcome-affecting and versioned.

---

## 2. Supported but incomplete primitives (SUPPORTED_BUT_INCOMPLETE)

| # | Primitive | What exists | What is missing |
|---|-----------|-------------|-----------------|
| 2 | **unrealized PnL** | Mark path recomputes `unrealized_pnl` from `average_open_price` (`_apply_marks`), tested | TD-002: partial close writes `unrealized_pnl = 0` for the remaining quantity; intermediate state is misleading until next mark |
| 3 | **equity** | `equity = cash_balance + unrealized_pnl`, tested on mark path | Inherits TD-002 zeroing at partial-close snapshots; no day-series equity curve |
| 6 | **trade / open-close boundaries** | `POSITION_TRANSITION` evidence + `CapitalTransition.transition_type` (`POSITION_CLOSE` / `FORCED_LIQUIDATION`) and `quantity_change` sign identify open/add/partial-reduce/full-close; partial close supported | No consolidated trade record pairing open → close; no trade id; boundaries are inferable from the transition stream, not materialized |
| 13 | **overlapping positions (over time)** | Only same-direction separate sleeves at a single decision point | No multi-day overlap track; no overlapping-exposure index; opposing opens across days are not modeled |
| 14 | **simultaneous cross-instrument positions (over time)** | Only single-decision-point batch | No multi-day portfolio state engine carrying simultaneous positions forward with daily marks |
| 15 | **per-event return / PnL contribution** | Per-order realized `realized_pnl_change` and per-mark unrealized deltas (before/after snapshots) recoverable | "Return" as a ratio is not computed; execution events are not directly keyed by hypothesis/wave/family (join required via experiment → `OutcomeTestRegistration`) |

---

## 3. Derivable with small engineering delta (DERIVABLE_WITH_SMALL_ENGINEERING_DELTA)

The base facts are already recorded; only aggregation/materialization code is missing. None of these
require a statistics framework.

| # | Primitive | Required delta |
|---|-----------|----------------|
| 7 | **holding duration** | Open-fill `evaluated_at` and close-fill `evaluated_at` (or mark/eligible timestamps) exist per transition; add a pure function over trade boundaries |
| 8 | **active trading days** | `trading_day` identity exists on bars/snapshots/events; add distinct-day aggregation |
| 9 | **no-trade days** | Requires the instrument trading calendar (`SessionMetadata` windows) plus event days; add set-difference aggregation |
| 16 | **portfolio aggregate return** | Shared/sleeve realized+unrealized PnL already aggregate at a decision point; add return-percentage and portfolio-day aggregation |
| 18 | **turnover** | Per-transition quantities and charged costs exist; add notional/quantity turnover aggregation (basis definition is a profile decision, not a code gap) |
| 19 | **exposure duration** | Open/close timestamps exist per transition; add duration field. Multi-position overlap exposure duration is not covered here |
| 20 | **event count** | `ExecutionEvent`, transitions, and `EvidenceLedger` records exist and are ordered; add per-hypothesis/per-wave grouping (requires the join in §6) |

---

## 4. Not currently supported (NOT_CURRENTLY_SUPPORTED)

| # | Primitive | Why |
|---|-----------|-----|
| 17 | **drawdown path** | Requires a day-series equity curve across the portfolio; no multi-day portfolio loop and no drawdown function exists anywhere in `src/` (verified by search: no `drawdown`/`equity_curve`/`turnover`/`holding_*`/`sharpe`/`expectancy`/`win_rate`/`max_drawdown`/`annualized` symbols) |

---

## 5. Unsafe primitives (UNSAFE_DUE_TO_KNOWN_TECH_DEBT)

These are not merely incomplete — consuming them as final-quality evidence today is unsafe:

- **Equity and unrealized PnL at a partial-close snapshot** (TD-002). After a partial close the
  remaining position's `unrealized_pnl` is force-zeroed, so equity collapses to the cash level at
  that instant. Using this snapshot in an equity curve or drawdown path is wrong until a coherent
  mark-preservation/re-mark semantic is decided and implemented.
- **Trading-day identity taken from `bootstrap_semantics.NormalizedSessionCalendar`** (TD-001). The
  accepted authoritative path is `SessionMetadata.trading_day_at`; the bootstrap calendar is a
  feasibility fixture. Consuming it as a trading-day authority can map one timestamp to a
  conflicting trading day and silently corrupt all day-level aggregation (holding days, active days,
  no-trade days, instrument-day/portfolio-day units). The authoritative `SessionMetadata` path is
  safe and tested.
- **Contract-bound confirmatory PnL over the real corpus while required price-limit facts are
  missing** (LIMIT-001). This is currently **blocked, not silently wrong**: `_visible_limit_fact`
  raises when a `price_limit_rule_identity`-bound contract has no exactly-one PIT fact. Do not treat
  an absence of governed facts as permission to fill through a limit.

---

## 6. TD-001 / TD-002 / LIMIT-001 impact analysis (precise)

### TD-001 — duplicate session/trading-day responsibility

`NormalizedSessionCalendar.trading_day_at` (`src/bootstrap_semantics.py:46`) and
`SessionMetadata.trading_day_at` (`src/data_substrate.py`) both map a timestamp to a trading day.

- **Which statistics it can pollute:** timestamps / trading-day identity (12), active trading days
  (8), no-trade days (9), holding duration in trading days (7), and any instrument-day /
  portfolio-day / calendar-week aggregation (candidate units).
- **Current exposure:** none in the accepted path — `ChronologicalValidationRunner._resolve_contracts`
  and `_apply_capital_constraints` use `SessionMetadata` and additionally fail closed on
  `"completed-bar trading day is inconsistent with explicit contract session metadata"` and on
  backward trading-day movement. The bootstrap calendar is not consumed by validation/portfolio code.
- **Precise verdict:** TD-001 is a **drift risk, not an active polluter**. It becomes a polluter only
  if new statistics code (e.g., day-aggregation helpers) picks the bootstrap calendar instead of
  `SessionMetadata`. Required before any day-level statistic is trusted: retire/isolate the bootstrap
  calendar and add a regression proving one timestamp cannot map to conflicting trading days.

### TD-002 — partial-close snapshot clears unrealized PnL

In `_apply_capital_constraints`, a partial close (`remaining_quantity > 0`) writes
`unrealized_pnl = Decimal("0")` on the remaining position and updates `position_request_id`; a later
mark recomputes unrealized for the remaining quantity.

- **equity curve:** polluted at the partial-close snapshot — equity drops by the entire remaining
  position's unrealized PnL at that instant (an artificial discontinuity).
- **drawdown:** if computed from that equity path, a spurious drawdown spike is created at the
  partial-close snapshot.
- **holding-period return:** the closed portion's realized return is correct (`fill_price -
  average_open_price`). The remaining position's final realized total is also correct because
  `average_open_price` is preserved and the final close recomputes from it. What is wrong is the
  **intermediate mark series**: the remaining position's unrealized/equity time series has an
  artificial zero at the partial-close instant, so any holding-period *path* (e.g., daily
  instrument-day returns) is corrupted at that point.
- **event-level realized PnL:** NOT polluted — the partial-close event's `realized_pnl_change` is
  exact for the closed quantity.
- **portfolio aggregate:** polluted at the partial-close snapshot — `StrategySleeve` and
  `SharedCapitalState` aggregate `unrealized_pnl` from positions, so a zeroed remaining position
  drags the aggregate down until the next mark.
- **Precise verdict:** TD-002 pollutes **equity path, drawdown path, intermediate holding-period mark
  series, and portfolio aggregate at partial-close snapshots only**. It does not pollute realized
  PnL (closed portion) or final realized totals. Activate-before: any equity/drawdown/daily-return
  evidence used for confirmatory or final acceptance.

### LIMIT-001 — historical price-limit metadata not fully governed

The canonical dataset deferred full historical price-limit facts; execution semantics require an
exactly-one PIT fact for any contract bound to `price_limit_rule_identity`.

- **Which statistics it affects:** realized PnL (1), unrealized PnL (2), equity (3), cash (4), costs
  (5), trade boundaries (6), holding duration (7), event count (20) — but only in the sense that
  **producing them for the real corpus on price-limit-bound contracts is currently blocked**
  (fail closed) rather than silently wrong.
- **Precise verdict:** LIMIT-001 does **not** silently pollute any statistic. It is a **blocking
  data gap** for real historical confirmatory execution over price-limit-bound instruments. Synthetic
  facts are fully tested and work. Before any confirmatory backtest claims realistic Chinese-futures
  price-limit non-fill realism over 2024–2025, governed limit facts must be bound by effective
  period and execution must fail closed when the required fact is missing (already the code behavior).

---

## 7. Available time / instrument / event identities (for dependence-aware inference)

Index | Status | Where it is bound
------|--------|-------------------
**time** | BOUND (ordered event log, not a stats-grade series) | `ExecutionEvent.timestamp`, `decision_at`, `evaluated_at`, `available_at`, `observed_at`, `state_at`, `resolved_at` — all timezone-aware; chronology enforced fail-closed |
**trading day** | BOUND | `CompletedBar.trading_day`, `CapitalSnapshot.position_trading_day`, `SessionMetadata.trading_day_at`; `today_quantity`/`previous_quantity` buckets; `CloseOffset.CLOSE_TODAY/CLOSE_PREVIOUS` |
**instrument** | BOUND | `bar.instrument`, `position_instrument`, `requested_symbol`, `research_symbol` |
**contract** | BOUND | `concrete_contract_id`, `contract_identity_id`, `contract_master_identity_id`, `mapping_schedule_identity_id`, `mapping_entry_identity_id` |
**family (contract)** | BOUND at contract level | `ContractSpecification.product_family` |
**family (research)** | BOUND at strategy level | `StrategyIdentity.family_id`, `research_lineage_id` |
**hypothesis** | BOUND at firewall, NOT on execution records | `hypothesis_test_id` in `OutcomeTestRegistration` / `WaveHypothesisBinding` (`src/research_firewall.py`); join to execution via `experiment_identity_id` |
**wave** | BOUND at firewall, NOT on execution records | `research_wave_id` in `ResearchWaveManifest` / `OutcomeTestRegistration`; join via experiment |
**overlapping exposure** | **MISSING** | No overlapping-exposure index or multi-day overlap record exists |

Key gap for dependence-aware inference: execution-level records (`ExecutionEvent`,
`CapitalTransition`, `MarkToMarketTransition`) carry `request_id` / `observation_id`, not
`hypothesis_test_id` / `wave_id` / `family_id`. The join exists (transition.reference_id →
`EvidenceRecord.fact_reference` → experiment → `OutcomeTestRegistration`), but it is indirect and
must be materialized before per-hypothesis/per-wave/per-family event grouping is reliable.

---

## 8. Candidate analysis units — support matrix

Unit | Can the code reliably generate it today? | Minimum engineering delta
-----|-----------------------------------------|--------------------------
**trade-level** | Facts recorded; no trade object | Small: materialize open→close pairing (incl. partial close) from `POSITION_TRANSITION` / `CapitalTransition` into trade records with open/close timestamps, quantity, realized, costs |
**event-level** | Yes — ordered `ExecutionEvent` + transitions | Small: group events; add hypothesis/wave/family join (§7) |
**trading-day-level** | Facts recorded; no aggregation | Small: aggregate by `trading_day` (single-instrument runs); TD-001 authority check |
**calendar-week-level** | Derivable | Small: `date.isocalendar()` mapping + aggregation; no week index exists today |
**instrument-day-level** | Facts recorded (single-instrument runs carry both) | Small: composite `instrument × trading_day` aggregation; multi-day cross-instrument series still missing |
**portfolio-day-level** | **Not currently** — portfolio is single-decision-point batch | Medium: multi-day portfolio loop carrying positions forward with daily marks + daily aggregation; no such engine exists |

The audit does **not** decide which unit the profile must use — it only reports that trade/event/day/
week/instrument-day units need small deltas and portfolio-day needs a medium delta.

---

## 9. Minimum engineering deltas (recorded, not built — no statistics framework)

1. **Trade-record materialization** — pair opens/closes (incl. partial) into trade records with
   open/close timestamps, quantity, realized, costs. (small)
2. **Multi-day portfolio/equity series builder** — carry positions across days with daily marks,
   producing per-day equity/cash/PnL rows; prerequisite for drawdown, portfolio-day aggregation,
   turnover, exposure duration. (medium)
3. **Event → hypothesis/wave/family join index** — enrich execution/transition records with
   `hypothesis_test_id` / `wave_id` / `family_id`, or provide a join view via experiment →
   `OutcomeTestRegistration`. (small)
4. **Day/week aggregation helpers** — pure functions over `trading_day`/date; no semantics. (small)
5. **TD-001 consolidation** — single trading-day authority (`SessionMetadata`); isolate/retire
   bootstrap `NormalizedSessionCalendar`; regression: one timestamp → one trading day. (small-medium)
6. **TD-002 mark-preservation semantic** — decide and implement re-mark at partial close under a new
   explicit semantic/version before equity/drawdown final-quality use. (small-medium)
7. **LIMIT-001 data binding** — bind governed historical price-limit facts by effective period for
   the corpus before real confirmatory execution claims. (data/governance)

No new statistics framework is proposed. Items 1, 3, 4 are pure aggregation/join helpers; items 5–7
are existing debt resolutions already required by `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`.

---

## 10. What the COMMON_STATISTICAL_PROFILE_V1 designer may safely assume

- Deterministic, regression-tested single-position-lifecycle arithmetic: realized PnL, unrealized
  PnL (mark path), equity, cash, charged costs — all `Decimal`, all identity-bound, replay-stable.
- Versioned, outcome-affecting execution/offset/capital assumption identities.
- Trading-day identity authoritative from `SessionMetadata` (never the bootstrap calendar).
- Instrument, concrete contract, and point-in-time mapping/roll identity are reliable and tested.
- Chronological ordering of inputs/observations/marks is enforced (fail closed on reorder).
- Fail-closed execution: missing price-limit facts raise rather than silently fill.
- Per-order realized PnL contribution and per-mark unrealized deltas are recoverable.
- Single-decision-point portfolio aggregates reconcile to attributed positions (tested).
- The frozen cohort index (`classify_cohort`, 12/6/6) and research-wave/profile/counting-unit
  identity/lock machinery exist and are gate-tested.

## 11. What it must NOT assume

- No day-series equity, no drawdown, no portfolio-day aggregation, no turnover %, no holding
  duration, no active/no-trade-day counts, no Sharpe/expectancy/win-rate/annualized — none are
  computed anywhere in `src/`.
- Must not assume execution events are directly keyed by hypothesis/wave/family — a join is required.
- Must not consume trading-day identity from `bootstrap_semantics` (TD-001).
- Must not treat unrealized/equity at partial-close snapshots as final-quality (TD-002); must not
  build the profile's equity/drawdown on that path until the mark-preservation semantic is fixed.
- Must not assume the portfolio coordinator provides multi-day state — it is a single-decision-point
  batch; portfolio-day units need a medium delta.
- Must not assume real historical confirmatory PnL on price-limit-bound contracts until LIMIT-001
  governed facts are bound (today it blocks, it does not silently fill).
- Must not assume any per-hypothesis/per-wave event counts or dependence (overlapping-exposure)
  index exists — the overlapping-exposure index is missing entirely.

---

## 12. Tests / evidence

- Baseline and final full suite: `python -m unittest discover -s tests -v`
  - Result: `Ran 235 tests in ~0.6s — OK (skipped=3)` (matches `CURRENT_STATE.md`:
    `FULL_TESTS=235_OK`, `FULL_TESTS_SKIPPED=3`, `FIREWALL_TESTS=54`).
- Targeted evidence for supported primitives:
  - `tests/test_position_capital_lifecycle.py` — realized/unrealized PnL, equity, cash, costs,
    maintenance breach, forced liquidation, identity binding, deterministic replay.
  - `tests/test_contract_execution_semantics.py` — contract identity, PIT mapping/roll, close
    offsets, price-limit fail-closed, trading-day aging.
  - `tests/test_capital_margin_constraints.py` — sequential fills, insufficient-margin non-fill.
  - `tests/test_execution_realism.py` — assumption identity, costs, lookahead fail-closed.
  - `tests/test_portfolio_semantics.py` — simultaneous candidates, shared capital, sleeves,
    reconciliation, conflict arbitration.
  - `tests/test_validation_runner.py` — chronology, replay determinism, FAST-vs-CONFIRMATORY.
  - `tests/test_research_firewall.py` — hypothesis/wave/profile/counting-unit identity and locks.
- This audit added **no production code and no tests**: no delta was implemented, and no new
  statistics framework was created. It is an evidence document only.
- Static check: `git diff --check` clean (see commit).

## 13. Scope and non-claims

- This audit did not choose a counting unit, thresholds, uncertainty method, or dependence rule for
  `COMMON_STATISTICAL_PROFILE_V1`; those remain with its designer.
- No real candidate outcome data was produced, inspected, or committed.
- `VALIDATION`, `PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT`, and `SHADOW_FORWARD` remain locked;
  candidate outcome-bearing performance backtests remain `NOT_AUTHORIZED`.
- Frozen Protocol v1.0, the 12/6/6 chronology, and all frozen research semantics are unchanged.

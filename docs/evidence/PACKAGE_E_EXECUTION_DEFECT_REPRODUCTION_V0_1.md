# PACKAGE_E_EXECUTION_DEFECT_REPRODUCTION_V0_1

> Task: `PACKAGE_E_PREFLIGHT_EXECUTION_DEFECT_REPRODUCTION_V0_1`
> Role: defect reproduction only. NOT a repair task.
> Date: 2026-08-20
> Findings authority: `docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md`
> Repair-plan authority: `docs/reviews/FULL_PROJECT_SECOND_PASS_REPAIR_PLAN_V0_1.md`
> Reproduction script: `tools/reproduce_package_e_findings.py`

```text
STATUS=PREFLIGHT_DEFECT_REPRODUCTION_COMPLETE
PRODUCTION_CODE_CHANGED=NO
NO_CANDIDATE_OUTCOME_DATA_USED=YES
BOOTSTRAP_E13_SCOPE=BOOTSTRAP_FIXTURE_ONLY
```

Every finding below was reproduced on the real `origin/main` code with a
synthetic, lowest-level trigger. No `src/*.py` file was modified. No new trading
semantics were decided.

## Reproduction method

All scenarios are synthetic. Each finding was reproduced by calling the most
direct authoritative class/function:

- `ChronologicalValidationRunner._apply_capital_constraints` (static) — ADD/OPEN
  margin admission, bucket resolution, offset-fee close path;
- `ChronologicalValidationRunner._apply_marks` (static) — maintenance breach and
  positive-unrealized mark;
- `ChronologicalValidationRunner._evaluate_forced_liquidation` (static) — forced
  liquidation path;
- `PortfolioCoordinator._resolve_candidates` (static) — portfolio structural
  contract-multiplier representation check (the candidate-outcome path itself is
  not reopened; Package A already fails it closed);
- `RoundTripMaterializer` / `RoundTripLedger` — round-trip evidence identity;
- `bootstrap_semantics.TradingState` — cross-trading-day chronology gap (fixture
  only).

No candidate firewall outcome path was exercised, and no candidate market data
was read.

---

## E-01 — ADD resets unrealized PnL to zero

- **FINDING**: HIGH / CONFIRMED_DEFECT. When adding to an already open
  position, the new `CapitalSnapshot` is constructed with `unrealized_pnl=0`
  regardless of the existing position's mark relative to the new fill.
- **REPRO_STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `ChronologicalValidationRunner._apply_capital_constraints`,
  OPEN/ADD branch: `next_snapshot = CapitalSnapshot(..., unrealized_pnl=Decimal("0"), ...)`.
- **MINIMAL_TRIGGER**: LONG 1 lot @100 with a valid mark @110 (existing
  `unrealized_pnl=+10`); then ADD 1 lot @110 through the capital-constraints
  path.
- **CURRENT_BEHAVIOR**:
  - mark @110 -> existing `unrealized_pnl=10`;
  - ADD transition after -> `unrealized_pnl=0`, `cash=99.50`,
    `reserved_margin=21.0`, `quantity=2`, `average_open_price=105`;
  - a fully lifecycle-reachable two-ADD path (no explicit mark) also reports
    `unrealized_pnl=0` after the second fill at 110, while the first tranche's
    fair value at that fill price is +10;
  - the short mirror (shared ADD branch) also resets to 0.
- **FUTURE_INVARIANT**: after an ADD fill, the earlier tranche's unrealized PnL
  relative to the current fill/mark must be carried (or deterministically
  re-marked), never silently cleared to zero; the equity path must not contain a
  spurious intermediate zero.
- **DEPENDENCY**: TD-002 partial-close re-marking already sets nonzero
  `unrealized_pnl` on the remaining position; an ADD after such a state would
  wipe it. No candidate-outcome dependency.
- **NOTES**: In the full `run()` lifecycle, ADD after an applied mark is
  additionally rejected by the guard
  `if current.latest_mark_reference is not None: raise` ("cannot add to a
  position after mark-to-market in the minimum lifecycle"). That guard is a
  separate hardening behavior; it does not contradict the ADD branch itself
  unconditionally writing `unrealized_pnl=0`. The reproduction reaches the ADD
  branch directly with the marked position's positive unrealized carried in the
  snapshot and the mark reference unset, which is the only state space the ADD
  branch accepts.

---

## E-02 — Forced liquidation cannot cleanly cross to the next official trading day

- **FINDING**: HIGH / CONFIRMED_DEFECT. Forced-liquidation execution checks the
  execution observation trading day against the snapshot `position_trading_day`;
  the declared rule is "next tradable observation", which may legitimately be
  the next official trading day after a session-end breach.
- **REPRO_STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `ChronologicalValidationRunner._evaluate_forced_liquidation`:
  `trading_day = session_metadata.trading_day_at(...); if trading_day !=
  snapshot.position_trading_day: raise ValueError("forced-liquidation observation
  is outside the position trading day")`. The liquidation path performs no
  today/previous bucket aging.
- **MINIMAL_TRIGGER**: contract-bound LONG position on official trading day D1
  (`2025-06-16`); maintenance breach mark at the D1 session tail (`09:55`); next
  tradable observation on official trading day D2 (`2025-06-17 09:05`), mapped
  through `SessionMetadata` (not a raw civil guess).
- **CURRENT_BEHAVIOR**: `session.trading_day_at(obs) = 2025-06-17`,
  `snapshot.position_trading_day = 2025-06-16`; the liquidation path raises
  `ValueError: forced-liquidation observation is outside the position trading
  day` instead of aging and accepting the next official trading day.
- **FUTURE_INVARIANT**: a forced liquidation eligible at the next tradable
  observation must be accepted when that observation belongs to the next
  official trading day, performing the same bucket aging (today -> previous) used
  by ordinary order processing.
- **DEPENDENCY**: `SessionMetadata` / official trading-day authority (TD-001);
  contract master active-lifetime window.
- **NOTES**: The forced-liquidation requirement was generated by
  `_apply_marks` (real breach), and the observation request/contract bindings all
  matched; only the trading-day check rejected the D2 observation.

---

## E-03 — Forced liquidation omits close-today/close-previous offset fees

- **FINDING**: HIGH / COST_DEFECT. Forced liquidation charges only the synthetic
  execution fee; it does not apply `OffsetCostAssumptions` or resolve
  close-today/close-previous cost semantics.
- **REPRO_STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `ChronologicalValidationRunner._evaluate_forced_liquidation`
  — outcome `total_cost = execution_assumptions.synthetic_fee`; transition
  `required_cost = execution_assumptions.synthetic_fee`; neither
  `resolved_close_offset` nor `offset_cost_assumption_id` is set.
- **MINIMAL_TRIGGER**: China-futures-style contract-bound position with a
  `today` bucket (today=1, previous=0); `OffsetCostAssumptions` with
  close-today fee (1) clearly different from close-previous fee (2); compare an
  ordinary `CLOSE_TODAY` with a filled forced liquidation.
- **CURRENT_BEHAVIOR**:
  - ordinary `CLOSE_TODAY` 1 lot: `total_cost=1.25` (0.25 synthetic fee + 1.00
    close-today fee), `resolved_close_offset=CLOSE_TODAY`,
    `offset_cost_assumption_id=<set>`;
  - forced liquidation 1 lot: `total_cost=0.25` (synthetic fee only),
    `resolved_close_offset=None`, `offset_cost_assumption_id=None`.
- **FUTURE_INVARIANT**: forced liquidation must resolve the applicable
  close-today/close-previous offset cost against the position buckets and record
  the resolved offset + offset-cost-assumption identity, so round-trip charged
  costs are complete.
- **DEPENDENCY**: `OffsetCostAssumptions`; contract `offset_fee_metadata_identity`.
- **NOTES**: This task does not decide the future fee numbers; it only proves the
  forced path currently omits the offset-fee component.

---

## E-04 — Generic CLOSE cannot split one close across today + previous buckets

- **FINDING**: HIGH / SCOPE_LIMITATION. If a requested generic close quantity
  exceeds each individual bucket but is <= their combined quantity, the runner
  fails instead of deterministically splitting across both buckets.
- **REPRO_STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `ChronologicalValidationRunner._apply_capital_constraints`,
  generic-close resolution: `if today_quantity >= q: CLOSE_TODAY elif
  previous_quantity >= q: CLOSE_PREVIOUS else: raise ValueError("generic close
  cannot deterministically resolve across position buckets")`.
- **MINIMAL_TRIGGER**: today=1, previous=1, generic close quantity=2 (combined
  quantity exactly sufficient, neither bucket individually sufficient).
- **CURRENT_BEHAVIOR**:
  - today=1, previous=2, close=2 -> `resolved_offset=CLOSE_PREVIOUS`, succeeds
    (previous bucket individually sufficient);
  - today=1, previous=1, close=2 -> raises `generic close cannot deterministically
    resolve across position buckets`.
  The exact failing shape is: `today < q` AND `previous < q` AND
  `today + previous >= q`.
- **FUTURE_INVARIANT**: a generic close with quantity <= today+previous must
  deterministically split across today and previous buckets (bounded by each
  bucket) instead of failing.
- **DEPENDENCY**: `OffsetCostAssumptions` per-bucket fee semantics; today/previous
  bucket aging.
- **NOTES**: The audit's illustrative pair was not assumed; the actual failing
  combination was determined against the real code.

---

## E-05 — One CapitalMarginAssumptions cannot express heterogeneous multipliers

- **FINDING**: HIGH / SCOPE_LIMITATION. `PortfolioRequest` carries one
  `CapitalMarginAssumptions.contract_multiplier`, and every resolved contract
  must match it; one portfolio evaluation cannot represent products with
  different multipliers.
- **REPRO_STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `PortfolioRequest` (single `capital_assumptions`) and
  `PortfolioCoordinator._resolve_candidates`: `if contract is None or
  contract.contract_multiplier != request.capital_assumptions.contract_multiplier:
  raise ValueError("portfolio contract multiplier is inconsistent with capital
  assumptions")`.
- **MINIMAL_TRIGGER**: instrument A multiplier 5, instrument B multiplier 10, in
  one `ContractMaster`; one `PortfolioRequest` with two candidates (one per
  instrument) and a single multiplier.
- **CURRENT_BEHAVIOR**:
  - single multiplier 5 over A(5)+B(10) -> raises "portfolio contract multiplier
    is inconsistent with capital assumptions" (B rejected);
  - single multiplier 10 over A(5)+B(10) -> raises the same error (A rejected).
  No single multiplier value can legally represent both members in one request.
- **FUTURE_INVARIANT**: a portfolio evaluation must be able to carry
  per-instrument (or otherwise heterogeneous) contract-multiplier/capital
  semantics where the resolved members genuinely differ.
- **DEPENDENCY**: contract master; contract mapping resolution; capital-margin
  model. The candidate-outcome portfolio path is NOT reopened (Package A keeps it
  fail-closed); only the structural representation limitation is reproduced.
- **NOTES**: This task only proves the scope limitation; it does not design a
  per-instrument margin map.

---

## E-08 — Add/open margin admission uses available_capital, not equity-aware resources

- **FINDING**: MEDIUM/HIGH / RESOURCE_SEMANTICS_GAP. The add/open capacity check
  uses `available_capital` (cash minus reserved margin), which excludes unrealized
  PnL; no existing authority decides that `available_resources` is wrong/right.
- **REPRO_STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `ChronologicalValidationRunner._apply_capital_constraints`:
  `if current.available_capital < required_margin + required_cost:` ->
  `INSUFFICIENT_MARGIN`.
- **MINIMAL_TRIGGER**: existing position with material unrealized PnL
  (`available_capital=89.75`, `available_resources=109.75`); ADD whose required
  margin+cost (100.25) lies strictly between the two.
- **CURRENT_BEHAVIOR**: `CURRENT_AUTHORITY_USED=available_capital`; the ADD is
  rejected as `INSUFFICIENT_MARGIN` even though `available_resources` is
  sufficient. `CORRECT_POLICY=UNRESOLVED_BY_EXISTING_AUTHORITY`.
- **FUTURE_INVARIANT**: the margin-admission resource definition must be frozen by
  project authority before repair; whichever is chosen must be a single
  consistent authority.
- **DEPENDENCY**: TD-002 re-marking (which makes the divergence material);
  capital/margin model.
- **NOTES**:
  ```text
  SEMANTIC_AUTHORITY_REQUIRED=YES
  ```
  This finding is NOT treated as an ordinary bug. It is a semantic-unfrozen
  question; this task neither decides nor fixes `available_capital` vs
  `available_resources`.

---

## E-09 — RoundTripMaterializer silently overwrites duplicate execution outcomes by request_id

- **FINDING**: HIGH / ROUND_TRIP_EVIDENCE_GAP. `execution_outcomes` is converted
  to a dict keyed by request ID with no duplicate rejection; multiple outcomes
  with the same request ID silently overwrite one another before cost
  cross-checking.
- **REPRO_STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `RoundTripMaterializer.materialize`:
  `outcomes_by_request = {outcome.request_id: outcome for outcome in
  execution_outcomes}`.
- **MINIMAL_TRIGGER**: two `ExecutionOutcome` with the same `request_id="dup-1"`
  but different `total_cost` (1 vs 2), both on a completed round trip whose OPEN
  and CLOSE transitions carry `required_cost=2`.
- **CURRENT_BEHAVIOR**: materialization succeeds; every "dup-1" transition
  resolves to the LAST outcome; the round trip's `source_outcome_references`
  contain only the last outcome's reference and never the first.
  Verdict: `FIRST_LOST` (the last outcome silently overwrites the first).
- **FUTURE_INVARIANT**: duplicate request_id execution outcomes must be rejected
  (or explicitly de-duplicated with a defined rule), never silently collapsed
  before cost cross-checking, so round-trip evidence cannot silently drop a
  conflicting cost outcome.
- **DEPENDENCY**: `CapitalTransition.required_cost` cross-check
  (`_cross_check_cost`).
- **NOTES**: Because the retained outcome matches `required_cost`, the silent
  overwrite is observable only as evidence loss, not as an immediate error.

---

## E-10 — Round-trip identity omits derived session-authority semantics

- **FINDING**: HIGH / ROUND_TRIP_IDENTITY_GAP. `ledger_identity` binds
  transition/outcome references and terminal reason but not SessionMetadata
  identity/version or derived entry/exit day/week/active-day values.
- **REPRO_STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `RoundTripMaterializer._finalize` identity input
  `{position_id, terminal_reason, forced_liquidation,
  ordered_transition_references, ordered_outcome_references}`; derived
  `entry/exit_official_trading_day/week` and `active_official_trading_days` are
  NOT in the identity.
- **MINIMAL_TRIGGER**: identical open/close transitions; two `SessionMetadata`
  authorities that map the same civil timestamps to different official trading
  days (positions not contract-bound, so no snapshot-day consistency guard
  fires).
- **CURRENT_BEHAVIOR**:
  - authority A -> entry/exit day `2025-06-16`, week `(2025, 25)`;
  - authority B -> entry/exit day `2025-06-23`, week `(2025, 26)`;
  - `ledger_identity` is identical under both authorities
    (`4c3b414e...51205`).
- **FUTURE_INVARIANT**: round-trip identity should bind the session-authority
  identity/version (and/or derived day/week facts) so a change in trading-day
  attribution authority cannot leave identity unchanged while derived fields
  change.
- **DEPENDENCY**: `SessionMetadata` (TD-001 authority); round-trip evidence
  identity.
- **NOTES**: This is a synthetic authority-divergence scenario; the snapshot
  `position_trading_day` is deliberately unset so both authorities can be
  materialized without the snapshot-vs-session consistency guard firing. In real
  runner output the day is always set, but the identity-binding gap (version not
  in identity) still holds.

---

## E-11 — Completed round trips are ordered by position_id, not chronology

- **FINDING**: MEDIUM / ORDERING_GAP. `RoundTripLedger` requires (and enforces)
  lexical position-id ordering, which is deterministic but not trade chronology.
- **REPRO_STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `RoundTripLedger.__post_init__` (`tuple(sorted(ordered_ids))
  == ordered_ids`) and `RoundTripMaterializer.materialize`
  (`completed_sorted = tuple(sorted(completed, key=lambda trip: trip.position_id))`).
- **MINIMAL_TRIGGER**: two completed round trips with position_id "z-position"
  completing at 10:00 and "a-position" completing at 11:00.
- **CURRENT_BEHAVIOR**: ledger output order is `["a-position", "z-position"]`
  (lexical by position_id), while chronological completion order is
  z (10:00) then a (11:00).
- **FUTURE_INVARIANT**: ledger output should either preserve trade chronology or
  explicitly document that order is NOT chronological; downstream consumers must
  not assume time order.
- **DEPENDENCY**: completed round-trip materialization.
- **NOTES**: This task does not decide the future sort; it only records the
  current meaning (lexical id ordering).

---

## E-12 — Open positions contribute only IDs to RoundTripLedger identity

- **FINDING**: MEDIUM/HIGH / OPEN-EVIDENCE_IDENTITY_GAP. For still-open
  positions, ledger identity contains only `open_position_ids`, not their current
  transition/state evidence.
- **REPRO_STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `RoundTripLedger.identity_id` includes only
  `open_position_ids` (strings); `RoundTripMaterializer.materialize` returns
  `open_ids = tuple(sorted(accumulators))`.
- **MINIMAL_TRIGGER**: same position_id "e12-pos" still open; stream A = 1 lot
  @100 (state 09:30); stream B = 2 lots @105 (state 09:45); neither completed.
- **CURRENT_BEHAVIOR**: both ledgers report `open_position_ids=("e12-pos",)` and
  identical `identity_id` (`5bf13de0...bffb81`) despite different quantity and
  transition evidence.
- **FUTURE_INVARIANT**: open-position identity should bind current state /
  transition evidence so material changes to an incomplete position alter the
  ledger identity.
- **DEPENDENCY**: round-trip ledger identity.
- **NOTES**: only the identity gap is reproduced; no new open-position state model
  is designed here.

---

## E-13 — Bootstrap TradingState has no cross-trading-day chronology barrier

- **FINDING**: MEDIUM/HIGH / LIVE-STATE_FIXTURE_GAP. The feasibility `TradingState`
  tracks sequence independently per trading day; a new day's sequence can apply
  while a prior day's gap remains buffered, and the missing prior-day event can
  later mutate the shared position after future-day state already applied.
- **REPRO_STATUS**: `REPRODUCED`
- **ROOT_FUNCTION**: `bootstrap_semantics.TradingState.ingest` /
  `_expected_sequence` keyed by `trading_day` only; no global cross-day
  chronology barrier.
- **MINIMAL_TRIGGER**: D1 seq1 applied; D1 seq3 buffered (seq2 missing); D2 seq1
  applied; then D1 seq2 arrives late.
- **CURRENT_BEHAVIOR**:
  - position after D2 applied = 2;
  - late D1 seq2/3 still apply and move the shared position to 5 (D1 seq2 +1,
    D1 seq3 +2) after D2 state was already applied.
- **FUTURE_INVARIANT**: cross-trading-day event application must enforce a
  chronology/sequencing barrier so a missing prior-day event cannot mutate
  position after a future day has already applied (idempotent, ordered, or
  fail-closed handling).
- **DEPENDENCY**: none (self-contained fixture).
- **NOTES**:
  ```text
  BOOTSTRAP_FIXTURE_ONLY=YES
  ```
  This module is an explicit feasibility fixture, not the production trading
  engine. The reproduction does not claim the live production TradingState is
  broken; it only confirms the fixture's gap.

---

## Summary of reproduction statuses

```text
E01=REPRODUCED
E02=REPRODUCED
E03=REPRODUCED
E04=REPRODUCED
E05=REPRODUCED
E08=REPRODUCED
E09=REPRODUCED
E10=REPRODUCED
E11=REPRODUCED
E12=REPRODUCED
E13=REPRODUCED
AUDIT_FINDING_INACCURATE=NONE

E08_SEMANTIC_AUTHORITY_REQUIRED=YES
BOOTSTRAP_E13_SCOPE=BOOTSTRAP_FIXTURE_ONLY
PRODUCTION_CODE_CHANGED=NO
NO_CANDIDATE_OUTCOME_DATA_USED=YES
```

## Scope boundaries honored

- No `src/*.py` modification (reproduction only).
- `main` not pushed; work isolated to
  `prep/package-e-execution-reproduction-v01`.
- `CURRENT_STATE.md` not modified.
- No new trading semantics decided (E-08 and E-10 left unresolved by design).
- E-06 (realistic historical fee/margin authority) and E-07 (concrete-contract
  research mapping) were NOT investigated; they are separate research/evidence
  design prerequisites per the repair plan.
- The default test suite was not altered; the reproduction is a standalone
  diagnostic script.

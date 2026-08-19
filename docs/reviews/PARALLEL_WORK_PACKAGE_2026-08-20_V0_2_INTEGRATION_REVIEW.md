# PARALLEL_WORK_PACKAGE_2026-08-20_V0_2_INTEGRATION_REVIEW

> Date: 2026-08-20
> Status: ACCEPTED_WITH_INTEGRATION_CLARIFICATIONS
> Package authority: `docs/research/PARALLEL_WORK_PACKAGE_2026-08-20_V0_2.md`

## Verdict

All three lanes are accepted and merged to `main`:

- Lane B/B2 — generic Playbook Contract core: ACCEPTED;
- Lane D — completed round-trip ledger: ACCEPTED;
- Lane E — Raschke Holy Grail semantic completion: ACCEPTED AS SOURCE-SEMANTICALLY DRAFTABLE, NOT MACHINE-READY.

No candidate outcome data was used by these lanes. Candidate outcome access, Validation and historical final holdout remain locked.

## Lane B/B2

Worker final commit: `b25f6feb12aaf7689df348d82af2a2b07f8862a0`.

Accepted facts:

- generic SOURCE / INTERPRETATION / MACHINE separation;
- deterministic contract identity;
- fail-closed provenance, ambiguity, observability and scope checks;
- deterministic bridge to existing `StrategyIdentity`;
- `ResearchFirewall` remains the sole candidate-outcome access-rule owner;
- valid zero-parameter fixed-rule strategies are supported;
- valid zero-required-feature-version strategies are supported;
- empty/non-empty mismatches remain fail-closed.

Main merge: `cd966503f80e3916464ca74e7df5ebe5402da940`.

## Lane D

Worker final commit: `5b58469cde94c00f7d6442c29de21674ed1a3b6d`.

Accepted facts:

```text
ONE_POSITION_ID_ONE_COMPLETED_ROUND_TRIP=YES
ADDS_AND_PARTIAL_CLOSES_DO_NOT_INFLATE_N=YES
FORCED_LIQUIDATION_IS_TERMINAL=YES
GROSS_REALIZED_PNL_AUTHORITY=CapitalTransition.realized_pnl_change
ADDITIVE_COST_AUTHORITY=CapitalTransition.required_cost
TRADING_DAY_WEEK_AUTHORITY=SessionMetadata
```

Integration clarification:

`CompletedRoundTrip.active_official_trading_days` currently records official trading days represented by lifecycle transitions supplied to the materializer. It is NOT evidence that every official trading day elapsed during a multi-day holding period has been enumerated. Any later statistic requiring full inclusive holding-day coverage must derive that coverage from authoritative session/event data rather than silently treating the current transition-day set as complete.

Main merge: `f3bd1cd4cc842b9bd3d3d8c08e4d4bbc7c62d042`.

## Lane E — Raschke Holy Grail

Worker final commit: `2650184c28d99140d8157de95400d2856166aaf2`.

Accepted decision:

```text
FAMILY=RASCHKE_HOLY_GRAIL_PULLBACK
PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES
PLAYBOOK_MACHINE_READY=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
```

Independent project-brain source verification against Linda Raschke's official free/public material supports the core source loop:

- 14-period ADX initially greater than 30 and rising;
- retracement to a 20-period exponential moving average;
- when price touches the EMA, place a buy stop above the previous bar high (sells reversed);
- after fill, place a protective stop at the newly formed swing low and trail stops as profits grow;
- later official material describes buying the first retracement to the 20-period EMA after ADX rises above 30 and looking to exit on a push to new highs.

The semantic YES means the source provides a recognizable complete trading-loop skeleton. It does NOT mean the machine semantics are complete.

Mandatory pre-outcome interpretation work remains for at least:

```text
EMA_PRICE_INPUT=NOT_SOURCE_PINNED
EMA_TOUCH_BAR_SEMANTICS=PARTIALLY_PINNED
ENTRY_ABOVE_PREVIOUS_HIGH_TICK_OFFSET=PARTIALLY_PINNED
NEWLY_FORMED_SWING_LOW_MACHINE_DEFINITION=PARTIALLY_PINNED
TRAILING_STOP_MACHINE_DEFINITION=PARTIALLY_PINNED
EXIT_ON_PUSH_TO_NEW_HIGHS_MACHINE_DEFINITION=PARTIALLY_PINNED
OPERATING_TIMEFRAME=NOT_UNIQUELY_PINNED
CURRENT_PROJECT_PRODUCT_TRANSFER=INFERRED
```

Clarification on stop/invalidation:

```text
SOURCE_STOP_BOUNDARY_CONCEPT=EXPLICITLY_PINNED
SOURCE_STOP_MACHINE_OPERATIONALIZATION=PARTIALLY_PINNED
```

The source explicitly identifies the newly formed swing low as the protective-stop reference. The source does not mechanically define how software identifies that swing low. Therefore this field may not be treated as fully machine-pinned.

All machine-facing interpretations must be predeclared and versioned before any candidate outcome access. They may not be selected, tuned or rescued after observing candidate performance. If critical interpretation ambiguity remains unresolved, the candidate remains `NOT_MACHINE_READY` / `AMBIGUOUS_STOP`.

Main merge: `34a4502ed20a64247ea908c4e0ae7ad7101a6df8`.

## Next integration boundary

The project is now ready for parallel pre-outcome work on:

1. a real Holy Grail Playbook Contract draft / interpretation freeze;
2. generic point-in-time technical-feature and timeframe aggregation infrastructure;
3. generic stop-order/protective-stop trigger semantics.

These are independent pre-outcome roads. None authorizes candidate performance inspection.

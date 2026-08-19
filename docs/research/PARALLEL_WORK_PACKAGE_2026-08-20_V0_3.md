# PARALLEL_WORK_PACKAGE_2026-08-20_V0_3

> Date: 2026-08-20
> Status: ACTIVE / PRE_OUTCOME / THREE INDEPENDENT LANES
> Main: sole integration lane
> Tool decision: USE_EXISTING

## Objective

Advance the project from a source-semantic Playbook candidate to deterministic, versioned pre-outcome machinery without inspecting candidate performance.

Parallelization rule:

```text
PARALLEL_EXECUTION=ENABLED
MAX_ACTIVE_LANES=3
PARALLELISM_CRITERION=INDEPENDENT_MUST_DO_WORK_NOT_DEPENDENT_ON_OTHER_LANE_RESULT
MAIN=SOLE_INTEGRATION_LANE
```

All lanes use isolated worktrees/branches. A failure or delay in one lane does not block accepted independent lanes.

## Binding boundaries

```text
RESEARCH_DIRECTION=HUMAN_PLAYBOOK_FIRST
PERFORMANCE_RESEARCH_STARTED=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
NO_CANDIDATE_OUTCOME_DATA_USED=YES_REQUIRED
```

Mandatory separation:

```text
SOURCE_CLAIM != PROJECT_AI_INTERPRETATION != MACHINE_OPERATIONALIZATION
```

Project interpretation and machine conventions may be predeclared before outcome access, but they must be labeled, versioned, deterministic and must not be selected/tuned using candidate outcomes. Critical unresolved ambiguity remains fail-closed.

## Accepted prerequisites

- Raschke Holy Grail semantic completion: `PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES`, `PLAYBOOK_MACHINE_READY=NO`;
- generic Playbook Contract core merged;
- completed round-trip ledger merged;
- SOURCE_ONLY / ResearchFirewall remains fail-closed;
- existing market-data budget remains canonical 1-minute OHLCV + governed metadata; no paid data purchase is authorized.

Integration review: `docs/reviews/PARALLEL_WORK_PACKAGE_2026-08-20_V0_2_INTEGRATION_REVIEW.md`.

## Lane F — Holy Grail Playbook Contract draft / interpretation freeze

```text
TYPE=CANDIDATE_SPECIFICATION_PREOUTCOME
TARGET=REAL_VERSIONED_PLAYBOOK_CONTRACT_DRAFT_PLUS_PRIMARY_READINESS_DECISION
OUTCOME_ACCESS=FORBIDDEN
```

Use the merged Raschke Holy Grail source-semantic evidence and `src/playbook_contract.py` to instantiate the real SOURCE + INTERPRETATION contract layers.

Resolve, without outcomes, the smallest deterministic project interpretation for machine-facing gaps where a non-outcome justification is defensible. Examples include EMA price input, touch semantics, tick-above reference, swing-low identification, trailing/target semantics, timeframe and Chinese-futures transfer.

Decision rule:

- do not force a PRIMARY;
- if critical interpretation alternatives cannot be justified without outcome selection, return `PRIMARY_FREEZE_READY=NO` / `AMBIGUOUS_STOP`;
- if one predeclared interpretation package is defensible, return `PRIMARY_FREEZE_READY=YES` and bind every inferred convention/version explicitly;
- do not add a MachineOperationalization unless all required machine dependencies actually exist and are versioned; a source/interpretation contract may remain `NOT_MACHINE_READY`.

## Lane G — point-in-time technical feature / timeframe layer

```text
TYPE=GENERIC_ENGINEERING
TARGET=VERSIONED_PIT_TIMEFRAME_AGGREGATION_PLUS_EMA_WILDER_ADX
OUTCOME_ACCESS=FORBIDDEN
```

Build generic, candidate-independent infrastructure over `NormalizedHistoricalBar` / governed session metadata:

- deterministic session-aware aggregation from 1-minute bars to higher timeframes;
- no bridging of session breaks;
- official trading-day identity, not civil-date inference;
- aggregate availability only after all constituent bars are completed/available;
- deterministic EMA feature;
- deterministic Welles Wilder ADX feature;
- explicit warmup / insufficient-history behavior;
- feature specification/version identities and hashes;
- synthetic fixtures only; no real candidate outcome inspection.

The module must not choose candidate parameters based on performance. It may support arbitrary explicit periods; source-specific 20 EMA / 14 ADX are later contract inputs, not hard-coded research selection.

## Lane H — generic stop-order / protective-stop execution semantics

```text
TYPE=GENERIC_EXECUTION_ENGINEERING
TARGET=VERSIONED_STOP_TRIGGER_OBSERVATION_LAYER
OUTCOME_ACCESS=FORBIDDEN
```

The current validation runner supports generic `NEXT_TRADABLE_OBSERVATION` market-like execution observations but no explicit stop trigger/order-price semantics.

Build the smallest reusable layer that can turn pre-existing stop orders plus completed OHLC bars into deterministic execution observations without inventing intrabar sequence.

Required behavior:

- explicit BUY_STOP / SELL_STOP semantics;
- stop price must be on contract tick where contract metadata is available;
- first eligible future bar only; no same-decision lookahead;
- gap-through behavior explicitly versioned;
- stop trigger based on bar high/low only when order was already active;
- use underlying 1-minute path for higher-timeframe strategies when available rather than guessing higher-timeframe intrabar order;
- if one-minute data still cannot resolve two conflicting triggers in the same bar, fail closed / emit explicit sequence ambiguity rather than choose a favorable ordering;
- protective stops and entry stops use the same generic trigger semantics;
- do not implement candidate-specific trailing logic in this lane;
- output should bridge cleanly into existing `ExecutionObservation` / validation execution pipeline rather than duplicate capital/position lifecycle.

All tests use synthetic/non-candidate bars.

## Integration order

If all lanes complete together, preferred project-brain review order:

```text
G -> H -> F
```

Reason: generic feature/execution infrastructure can be accepted independently; Lane F contract readiness is then adjudicated against the actual merged machine capabilities. Lane F may still be integrated as a `NOT_MACHINE_READY` research artifact if its interpretation result is valid.

## Tool decision

```text
TOOL_DECISION=USE_EXISTING
NEW_TOOL_REQUIRED=NO
PAID_SOURCE_OR_DATA_PURCHASE=NO
```

No new framework is justified for these bounded tasks.

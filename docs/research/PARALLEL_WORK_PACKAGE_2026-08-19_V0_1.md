# PARALLEL_WORK_PACKAGE_2026-08-19_V0_1

> Date: 2026-08-19
> Status: ACTIVE / NON_FROZEN / PRE_OUTCOME
> Integration owner: project brain / main
> Parallelism rule: run work in parallel only when completion is useful regardless of the other lanes' results.

## 1. Decision

```text
PARALLEL_EXECUTION=ENABLED
MAX_ACTIVE_LANES=3
PARALLELISM_CRITERION=INDEPENDENT_MUST_DO_WORK_NOT_DEPENDENT_ON_OTHER_LANE_RESULT
MAIN=SOLE_INTEGRATION_LANE
TOOL_DECISION=USE_EXISTING
OWNER_ACTION=RUN_THREE_PROVIDED_LOCAL_AGENT_PROMPTS
```

This plan intentionally avoids using parallel workers merely to duplicate the same research question. The three lanes repair different road segments that the project must eventually connect.

## 2. Shared safety boundary

All lanes branch independently from the same current `origin/main` descendant and must never push `main`.

Shared forbidden work:
- candidate outcome inspection/backtesting;
- PnL/Sharpe/win-rate/equity or equivalent candidate-quality inspection;
- Validation access;
- historical-final access;
- data-first K-line/indicator/pattern/parameter mining;
- paid commitments;
- changing frozen Protocol v1.0 / 12-6-6 semantics;
- real-money or broker actions.

Synthetic fixtures and non-candidate engineering tests are allowed.

## 3. Lane A — Raschke NR7 targeted semantic completion

```text
LANE=A
PACKAGE=RASCHKE_NR7_TARGETED_SEMANTIC_COMPLETION_V0_1
TYPE=SOURCE_RESEARCH
DEPENDENCY=RASCHKE_SCREEN_ACCEPTED
INDEPENDENT_OF_LANE_B=YES
INDEPENDENT_OF_LANE_C=YES
OUTCOME_ACCESS=FORBIDDEN
```

Purpose: decide whether the selected `RASCHKE_NR7_RANGE_CONTRACTION_TREND_DAY_BREAKOUT` family has enough source-faithful semantics to become a later Playbook Contract candidate.

Must resolve without outcome data:
- NR7 daily-bar/session definition;
- source-permitted 45m vs 60m early-range alternatives;
- bracket entry semantics;
- bracket/order cancellation semantics if source evidence exists;
- stop/invalidation (integration correction: NOT currently source-pinned);
- exit/target;
- volume/breadth role;
- timeframe and instrument-transfer boundary;
- failure/no-trade context.

Output must be `PLAYBOOK_SEMANTICALLY_DRAFTABLE=YES|NO`. It must not force a YES.

## 4. Lane B — generic Playbook Contract engineering foundation

```text
LANE=B
PACKAGE=PLAYBOOK_CONTRACT_CORE_ENGINEERING_V0_1
TYPE=ENGINEERING
DEPENDENCY=NONE_ON_RASCHKE_RESULT
INDEPENDENT_OF_LANE_A=YES
INDEPENDENT_OF_LANE_C=YES_BY_FILE_SCOPE
OUTCOME_ACCESS=FORBIDDEN
```

Purpose: build/audit the generic versioned contract layer required by the binding architecture route:

```text
source-faithful claim
-> project interpretation
-> machine operationalization
-> StrategyIdentity / StrategyCatalog
```

This lane must reuse rather than replace existing `src/strategy_evidence.py`, `StrategyIdentity`, `StrategyCatalog`, `ResearchFirewall`, contract/session metadata and canonical hashing patterns.

Required properties:
- immutable/versioned contract identity;
- explicit source claim references and SOURCE_ONLY/source-bundle identities;
- source vs interpretation vs machine-operation separation;
- observability requirements and unavailable-input fail-closed state;
- lineage, instrument/timeframe scope and transfer status;
- unresolved ambiguity must block machine-ready state;
- no method may itself authorize outcome access;
- deterministic canonical identity/hash;
- synthetic unit tests only.

The implementation must remain non-frozen infrastructure: it may represent research semantics but may not redefine frozen Protocol v1.0.

## 5. Lane C — mandatory execution evidence tech-debt repair

```text
LANE=C
PACKAGE=EXECUTION_EVIDENCE_TD001_TD002_REPAIR_V0_1
TYPE=ENGINEERING
DEPENDENCY=NONE_ON_SOURCE_FAMILY_RESULT
INDEPENDENT_OF_LANE_A=YES
INDEPENDENT_OF_LANE_B=YES_BY_FILE_SCOPE
OUTCOME_ACCESS=FORBIDDEN
```

Purpose: repair the two already-recorded engineering debts that will be required for trustworthy future evidence regardless of which human playbook survives.

### TD-001

Trusted trading-day/week logic must use `SessionMetadata` as the official authority. Locate duplicate/parallel trading-day logic, consolidate or delegate it, and add deterministic cross-midnight/night-session/day-week fixtures.

### TD-002

Partial-close intermediate position snapshots must not incorrectly set the remaining open position's `unrealized_pnl=0` until a later mark. Repair the state/equity path so partial-close transitions preserve/calculate a correct remaining-position valuation under explicit deterministic mark semantics. Closed realized totals must remain unchanged.

Add regression tests for:
- add -> partial close -> remaining position;
- partial close with favorable/adverse mark;
- full close terminal state;
- equity/unrealized/drawdown path consistency;
- realized-PnL invariance.

No canonical candidate market data may be used; synthetic fixtures only.

## 6. Merge strategy

Workers push only their isolated branches. Project brain reviews and integrates to `main`.

Preferred integration order if all finish together:
1. Lane C engineering repair (existing tech debt, lowest semantic coupling);
2. Lane B Playbook Contract core (generic infrastructure);
3. Lane A semantic result (source/research artifact, then connect to Lane B only after acceptance).

This order is operational, not a dependency claim. If one lane is delayed or fails, the other accepted lanes can still integrate.

## 7. Tool decision

```text
TOOL_DECISION=USE_EXISTING
NEW_TOOL_REQUIRED=NO
PARALLEL_WORKTREES=3
```

Existing Git/worktree, Python/unittest, verified SOURCE_ONLY and current local DeepSeek path are sufficient. No paid API or new orchestration framework is justified.

## 8. Stop conditions

A lane must stop/escalate only for:
- frozen research-semantic change;
- new product/research direction;
- paid commitment;
- real-money/broker action;
- irreversible external action;
- genuine ambiguity that cannot be resolved by current authority/tests.

Ordinary implementation/test/documentation defects are fixed autonomously inside the lane.
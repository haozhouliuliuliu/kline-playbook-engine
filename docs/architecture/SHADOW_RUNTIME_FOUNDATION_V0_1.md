# SHADOW_RUNTIME_FOUNDATION_V0_1

> Version: 0.1 (final engineering state)
> Date: 2026-08-21
> Status: IMPLEMENTED_AND_TESTED / ENGINEERING_VERIFIED / GENERIC
> Work package: `SHADOW_RUNTIME_FOUNDATION_V0_1` — deterministic paper trading runtime foundation
> Evidence: `docs/evidence/SHADOW_RUNTIME_FOUNDATION_V0_1.md`
> Tool decision: `USE_EXISTING` (no new tool adopted; Python standard library only)
> Branch: `preoutcome/shadow-runtime-foundation-v01` (base `main` `e87315dd622689eb165dbe81f1728c868cc06a26`)

## 1. Scope

This addendum documents the deterministic paper-trading runtime chain implemented
for the Shadow Runtime Foundation. It is ordinary engineering under
`ARCHITECTURE_BASELINE.md` (Skeleton v1.0) section 5 "Trading Loop" — every
component below is already required by the accepted baseline; no new research
semantics, no candidate strategy outcome, no real broker, no real money.

The chain:

```text
Tick/Bar
-> MarketContext
-> Strategy.intent
-> deterministic conflict resolution
-> RiskGate
-> OMS
-> BrokerAdapter (interface)
-> PaperBrokerAdapter (deterministic paper)
-> broker events
-> reconciliation
-> TradingState (sole real-time mutable owner)
-> Safety
-> RuntimeLedger (immutable, replayable)
```

## 2. Components (new modules)

| Module | Role |
| --- | --- |
| `src/market_context.py` | `MarketContext`: one completed-bar causal context, staleness test, contract/session binding |
| `src/intent.py` | `StrategyIntent`, `ConflictResolver` (deterministic batch conflict resolution) |
| `src/risk_gate.py` | `RiskGate` + `RiskRuleSet` (FIXTURE-ONLY numbers; no permanent limits) |
| `src/runtime_events.py` | `BrokerEvent` (event_id/stream/sequence), `BrokerEventLog` projection, violations |
| `src/trading_state.py` | `TradingState` (sole mutable owner): account/positions/orders, broker event application (dedup, idempotent, strict sequencing), accounting, marks |
| `src/broker_adapter.py` | project-owned `BrokerAdapter` interface + snapshot vocabulary |
| `src/paper_broker.py` | deterministic `PaperBrokerAdapter` + snapshot fixture (no network) |
| `src/order_management.py` | OMS: order lifecycle (submit/cancel/replace), broker-fact confirmation |
| `src/reconciliation.py` | local state vs broker snapshot; fail closed on mismatch |
| `src/safety.py` | `SafetyGate` + `KillSwitch`; persistent vs transient violations |
| `src/runtime_ledger.py` | immutable chained `RuntimeLedger` (audit/replay) |
| `src/runtime_recovery.py` | `RuntimePersistedState`, capture/rebuild (crash/restart) |
| `src/shadow_runtime.py` | `ShadowRuntime` orchestrator wiring the full chain |

Reused existing semantics (not re-invented): `ContractSpecification`,
`ContractMaster`, `OrderAction`, `PositionDirection`, `CloseOffset`,
`OffsetCostAssumptions` (`src/contract_semantics.py`); `CompletedBar`,
`SessionMetadata` (`src/data_substrate.py`); `NormalizedHistoricalBar`
(`src/historical_data.py`). The runtime does NOT import `src.validation_runner`
or `src.research_firewall`, so it never grants candidate outcome access.

## 3. Key invariants

- **TradingState is the sole authoritative mutable local real-time state owner.**
  Strategies receive immutable `MarketContext`/`TradingState` views; all broker
  facts are applied through `TradingState.apply_broker_event`.
- **Broker events**: unique `event_id`, idempotent application, deduplication,
  strict per-stream sequence (`OUT_OF_ORDER` / `SEQUENCE_GAP` /
  `DUPLICATE_EVENT_ID_DIFFERENT_CONTENT` / `INVALID_CONTENT` all fail closed into
  recorded violations and are surfaced to Safety). Snapshot events
  (account/position/order) are reconciliation inputs, not local overwrites.
- **Broker/exchange facts override local inference** (OMS consumes broker events;
  reconciliation compares local vs broker truth and fails closed).
- **Safety overrides strategies** and covers: stale/missing market data, broker
  disconnect, duplicate/inconsistent orders, account/position/order mismatch,
  clock/session anomaly, kill switch.
- **Ledger is immutable and chained** (each record binds the previous identity);
  `verify_chain()` recomputes the whole chain for audit; restart rebuilds state
  from `RuntimePersistedState` + broker snapshot, and a ledger tail mismatch
  fails closed.
- **Risk/margin/cost numbers are FIXTURE-ONLY.** No permanent real-money risk
  limit, fee or margin schedule is introduced; freezing real-money limits
  remains an Owner gate.

## 4. Boundaries

- Real TqSdk/CTP/SimNow trading, real broker credentials, and any real-money
  sizing are `EXTERNAL_BROKER_GATED` — not implemented.
- Candidate strategy outcome usage (Holy Grail/NR7 and any other candidate) is
  forbidden; only TEST_ONLY fake strategies are wired into the runtime.
- A live discretionary LLM decision layer and automatic Shadow startup are not
  implemented (future Owner-gated research/architecture decisions).

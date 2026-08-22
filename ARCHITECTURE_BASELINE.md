# ARCHITECTURE_BASELINE

## Status
Baseline: Skeleton v1.0
State: ACCEPTED
Purpose: Initial architecture baseline for a clean-room China commodity futures intraday automated trading project.

This architecture does not define concrete K-line strategies, books, indicators, social-media sources, or final trading playbooks.

## Current adopted architecture amendment

Skeleton v1.0 remains accepted historical baseline. The Owner-approved current architecture is additionally governed by `docs/architecture/ADR_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1.md`.

```text
CURRENT_ADOPTED_ARCHITECTURE=Skeleton_v1.0_PLUS_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1
JIANGHE_AI_MAY_PROPOSE_CONSTRAINED_TRADE_INTENT=YES
DETERMINISTIC_RISK_AND_EXECUTION_OWNERSHIP=UNCHANGED
```

The amendment deliberately preserves Data Substrate, ResearchFirewall, RiskGate, OMS, STOP/OCO, TradingState, PaperBroker, Safety, reconciliation and Ledger. It changes only the product decision layer: a versioned Jianghe AI Trader may interpret point-in-time market observations and propose a constrained intent; it never owns capital, positions, broker facts, risk hard limits, order lifecycle or safety overrides.

## Historical Skeleton v1.0 content

The following original Skeleton v1.0 sections are preserved verbatim for history. Where they
conflict with the adopted amendment above, the ADR is the current authority.

## Core principles
- AI operates mainly in the offline research layer.
- The live trading critical path does not rely on discretionary LLM decisions.
- Important facts and mutable state have one clear owner.
- Backtest/validation must prevent repeated holdout leakage and automated overfitting.
- Third-party frameworks are candidates until explicitly verified and adopted.

## 1. Data Substrate
Owns normalized market and contract semantics:
- instrument/contract master;
- China futures trading calendar and night-session semantics;
- tick/bar and multi-timeframe generation;
- contract multiplier/tick/limit metadata;
- margin, fee, close-today/close-yesterday and other cost metadata;
- contract mapping, main/continuous/roll metadata;
- point-in-time availability boundaries;
- data-quality checks;
- normalized historical storage;
- live market-data recording;
- versioned cost/slippage metadata contract.

All downstream components consume the same normalized data semantics.

## 2. Strategy Catalog
A strategy follows a Playbook Contract rather than a custom programming language.

Each strategy should have at least:
- family_id and lineage/parent relation;
- version;
- provenance/source;
- applicable instruments;
- timeframe;
- typed parameters;
- parameter hash;
- required MarketContext;
- deterministic intent interface;
- exit logic;
- code hash;
- environment/dependency hash;
- lifecycle state;
- data-exposure history.

Meaningful logic or parameter changes create a new immutable version.

## 3. Backtest & Validation Engine
One validation system may provide:
- FAST MODE for inexpensive rejection of large candidate pools;
- CONFIRMATORY MODE for chronological/event-driven verification with realistic trading semantics.

Both modes must execute the same strategy artifact/code hash. Fast mode may reject but cannot establish final validity.

Confirmatory validation should progressively model:
- timestamps/session semantics;
- orders and execution timing;
- costs and slippage;
- capital and margin;
- multiple strategy interaction;
- price-limit non-fill conditions;
- contract mapping/roll;
- insufficient-margin and forced-liquidation paths where relevant.

### Selection Firewall
The firewall is code-enforced, not just logged.

Minimum requirements:
- development / validation / final-unseen separation;
- technical denial of final-unseen access before explicit unlock;
- once observed, data permanently loses unseen status for the research family and descendants;
- family lineage prevents laundering exposure by renaming family_id;
- total search freedom records strategy × parameters × instruments × timeframe × context/regime;
- large automated searches require reasonable multiple-testing / overfitting controls;
- final candidates require correlation / false-diversification checks;
- future Shadow/Forward data supplies continuing genuinely unseen evidence.

## 4. Research Loop
Offline only.

AI may:
- find candidate ideas;
- organize knowledge;
- implement strategy drafts;
- write tests;
- analyze experiments;
- find bugs;
- red-team hypotheses;
- explain results.

AI may not:
- make discretionary live buy/sell decisions;
- change live sizing/stops/strategy logic;
- inspect final-unseen results and silently tune the same version;
- approve its own research as valid without independent/explicit validation.

MVP does not require multi-agent orchestration, knowledge graphs, RD-Agent/Qlib/TradingAgents/MiroFish integration, or automatic pattern discovery.

## 5. Trading Loop
Conceptual chain:
Tick/Bar → MarketContext → Strategy.intent() → deterministic conflict resolution → RiskGate → OMS → Execution → broker reports → reconciliation → Safety → Ledger.

### TradingState
TradingState is the only authoritative mutable local real-time state owner.
Strategies receive immutable snapshots for intent computation.

Broker events require:
- unique event_id;
- idempotent application;
- deduplication;
- defined out-of-order handling;
- sequence/trading-day conventions.

Broker/exchange facts override local inference.
Crash/restart must rebuild state from persistent facts plus broker reconciliation.

### Risk ownership
RiskGate owns versioned:
- per-strategy risk rules;
- portfolio capital allocation;
- portfolio risk budgets;
- total risk limits.

### Safety
Safety overrides strategies and must cover at least:
- stale/missing market data;
- broker disconnect;
- duplicate/order inconsistency;
- account/position mismatch;
- margin/risk abnormality;
- clock/session abnormality;
- kill switch.

External execution frameworks must sit behind a thin project-owned Broker Adapter. Core business logic must not bind directly to third-party private data structures.

## 6. Ledger
Immutable factual history.

Initial storage may use:
- SQLite for metadata/experiments/orders/fills/lifecycle/safety/reconciliation;
- Parquet for market and large analytical datasets;
- optional DuckDB for local analysis.

Record at least:
- experiment identity;
- research family and strategy version;
- code/parameter/environment hashes;
- feature_version and data version;
- dataset exposure;
- validation result/rejection reason;
- intent/order/cancel/fill;
- position transition;
- safety/reconciliation events;
- lifecycle transitions.

Ledger records what happened; it does not own live mutable state.

## 7. Observability & Control
Owner-facing control surface should eventually show:
- instruments scanned;
- active strategies;
- signals and executed trades;
- reason for each trade;
- positions;
- PnL and drawdown/risk;
- suspended strategies;
- data/broker/reconciliation health;
- system exceptions;
- kill switch.

MVP should avoid distributed observability infrastructure unless proven necessary.

## MarketContext / Regime
MVP does not require a standalone central Regime Router.
Data/context may expose causal, point-in-time features such as volatility, trend strength, volume state, time-of-day, and gap/session state.

Feature definitions must be versioned (`feature_version`).
If a central Regime Router is introduced later, it becomes a separately versioned research object subject to out-of-sample and leakage controls.

## Open-source position at baseline
Candidate only unless formally verified/adopted:
- Primary execution backbone candidate: VeighNa / vn.py
- Fast screening candidate: vectorbt
- Data/simulation candidates: TqSdk, openctp, SimNow
- Phase-2/reference: NautilusTrader, STUMPY, RD-Agent, Qlib, TradingAgents, MiroFish, Freqtrade, Jesse, QuantConnect LEAN
- Lightweight storage: SQLite, Parquet, optional DuckDB
- Deferred until proven need: DVC, MLflow, Optuna, Prometheus/Grafana, knowledge graph, multi-agent orchestration, microservices/distributed architecture

## Architecture acceptance
Skeleton v1.0 was accepted after independent engineering/open-source, statistical-overfitting, complexity, and final clean-room architecture reviews.

Do not reopen the whole architecture without a concrete fatal flaw. Exact defects may be fixed without redesigning the project.

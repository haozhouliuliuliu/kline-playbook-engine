# ARCHITECTURE_BASELINE

## Status

```text
CURRENT_ADOPTED_ARCHITECTURE=Skeleton_v1.0_PLUS_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1
STATE=ACCEPTED
```

This file contains the **current consolidated architecture only**. Historical Skeleton wording is preserved in Git history and accepted evidence; it is not repeated here because contradictory historical wording must not pollute the active project-brain context.

Binding decision-layer detail:
`docs/architecture/ADR_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1.md`.

## 1. Core architecture

```text
Market Data
-> Rolling Market State
-> Multi-Timeframe Observation
-> Jianghe AI Decision Layer
-> constrained TradeIntent
-> deterministic RiskGate
-> OMS / STOP-OCO
-> Execution / Broker Adapter
-> Broker Reports
-> Reconciliation
-> Safety
-> Ledger
```

The central product split is deliberate:

- **AI owns market interpretation and discretionary trade proposals within the Jianghe knowledge boundary.**
- **Deterministic systems own hard risk, order lifecycle, broker/account truth, reconciliation and safety.**

## 2. Data substrate

The data layer owns normalized, point-in-time market and contract facts:

- concrete instrument / contract identity;
- China-futures trading calendar and night-session semantics;
- 1m bars and causal higher-timeframe aggregation;
- tick / multiplier / limit / fee / margin metadata when governed;
- contract mapping / roll authority;
- `available_at` and completeness semantics;
- historical storage and live market-data recording;
- data-quality and provenance identities.

Downstream components must consume the same normalized semantics. Future information may not enter an observation or replay snapshot.

## 3. Jianghe knowledge and AI decision layer

Jianghe V1 is the sole current trading knowledge source unless `CURRENT_STATE.md` changes that direction.

The AI decision layer may:

- read causal structured OHLCV and standardized charts;
- maintain versioned working memory and AI annotations;
- interpret market state, timeframe-specific trend, location, relative strength and execution-timeframe behavior;
- classify A / B / C / D / NONE;
- output WAIT / NO_TRADE / WATCH / CANDIDATE / ENTER / MANAGE / EXIT;
- propose a constrained trade intent and invalidation logic.

It must allow `NO_TRADE` when the market is unfamiliar, source evidence is UNKNOWN/contradictory, or Jianghe permission conditions are not met.

The AI does **not** own:

- capital truth;
- position truth;
- broker truth;
- hard risk limits;
- order lifecycle truth;
- Safety overrides.

## 4. Versioned AI Trader identity

The research object is not merely a model name. `JiangheAITraderIdentity` binds outcome-affecting components including:

- Jianghe knowledge-pack identity;
- model provider / model version;
- system and decision prompt identities;
- context-selection policy;
- memory policy;
- chart renderer;
- observation schema;
- wake policy;
- decision schema / normalizer;
- inference configuration;
- tool capability set;
- Jianghe family scope.

A material change creates a new version/descendant and inherits prior exposure as required by research governance.

## 5. Observation / attention / replay

The AI does not receive occasional large retrospective packages. Market state is continuous; `JiangheObservation` is the point-in-time snapshot created when the AI is awakened.

Supported attention semantics include SCAN / WATCH / CANDIDATE / IN_POSITION. Wake events may include new closed bars, price entry/exit from AI watch regions, invalidation touches, order/position events, safety events and session events.

Historical V1 replay has a hard evidence boundary:

```text
HISTORICAL_BASELINE=COMPLETED_1_MINUTE_BAR
NO_SYNTHETIC_SUB_MINUTE_PATH_FROM_1M_OHLC=YES
```

Any future live use of partial-bar / sub-minute information is a different capability/version and cannot be claimed equivalent to 1m historical replay.

## 6. Working memory and audit

AI working memory is persistent within the governed replay/session and mutation-audited. It may retain:

- market hypotheses;
- timeframe-specific trend views;
- directional bias;
- watch / key / invalidation regions;
- active family hypothesis;
- expected trigger;
- UNKNOWN/open questions;
- prior meaningful decisions and state transitions.

AI annotations are hypotheses, never market facts.

Every real model call must be auditable with observation identity, raw/normalized response, timing/latency chain, decision identity and memory mutation evidence.

## 7. TradingState / RiskGate / execution

`TradingState` is the only authoritative mutable local realtime state owner.

`RiskGate` owns versioned hard limits and may reject AI intents. The AI cannot enlarge its own capital/risk allowance or bypass safety.

OMS / STOP-OCO / Broker Adapter / reconciliation remain deterministic project-owned execution infrastructure. Broker/exchange facts override local inference. Crash/restart must rebuild from persistent facts plus broker reconciliation.

## 8. Safety

Safety is fail-closed and overrides the AI and execution path for at least:

- stale/missing market data;
- broker disconnect;
- duplicate/order inconsistency;
- account/position mismatch;
- abnormal margin/risk;
- clock/session abnormality;
- kill switch.

## 9. Research / validation firewall

Human-playbook/source governance and candidate outcome access remain separate from implementation readiness.

The project preserves:

- SOURCE / AI interpretation / project operationalization separation;
- point-in-time data rules;
- family/version lineage and exposure inheritance;
- development / validation / final-holdout separation;
- technical denial of protected outcome access before authorization;
- search-freedom / multiplicity governance;
- genuinely unseen future Shadow/Forward evidence when later authorized.

Current authorization values live only in `CURRENT_STATE.md` / `PROJECT_BRAIN_RUNTIME_BRIEF.md`; this architecture file grants no outcome, Shadow, broker or real-money permission by itself.

## 10. Ledger / observability

Ledger stores immutable factual history for identities, exposures, decisions, intents, orders, fills, position transitions, safety/reconciliation events and lifecycle changes. It does not own live mutable state.

Owner-facing observability should ultimately expose what the AI is watching, why a trade was proposed/rejected, positions/orders, risk/safety health and a kill switch without forcing the Owner to inspect internal engineering details.

## 11. Tool policy

External execution frameworks, model providers, agent frameworks and open-source tools remain `CANDIDATE` until this project verifies/adopts them. Core business logic must remain behind project-owned interfaces.

Current architecture does not require a vector database, knowledge graph, multi-agent runtime, message queue, microservices or distributed infrastructure merely because those tools exist.

# ARCHITECTURE_BASELINE

Status: `CURRENT_ARCHITECTURE`

Product direction authority: `PROJECT_DIRECTION.md`

Current work package / locks / next task: `CURRENT_STATE.md`

Execution/promotion detail:

`docs/architecture/JIANGHE_EXECUTION_AND_PROMOTION_ARCHITECTURE_V0_1.md`

This file owns long-lived architecture only. It must not carry current work-package, current phase, paid-slot or next-task values.

## Core runtime

```text
Market Data
-> Rolling Market State
-> Attention / Wake Policy
-> Causal Multi-Timeframe Observation
-> Context Assembler
   -> Jianghe Canon
   -> Project-Validated Policy
   -> DeepSeek Working Memory
   -> Retrieved Analogues / Cases
-> DeepSeek Trader
-> Decision Normalizer + Mechanical Guards
-> constrained TradeIntent
-> deterministic RiskGate
-> OMS / Execution Adapter
-> Reconciliation / Safety / Immutable Ledger
```

DeepSeek interprets markets and proposes discretionary intent.

Deterministic project code owns capital/risk limits, broker/account truth, order lifecycle, reconciliation, safety, request accounting and kill-switch behavior.

## Model/runtime boundary

The active product model source is DeepSeek. Exact provider/model status, Harness pin, retry semantics and credential seam are owned by:

`TOOL_REGISTRY.md`

The runtime shell may host sessions, tools and UI, but it does not own core trader semantics. Trader cognition, project memory, evidence and policy remain project-owned and portable.

Deployment baseline is local-workstation first unless later architecture authority changes it.

## Observation semantics

The current Jianghe observation design uses causal multi-timeframe context. Exact active timeframes and replay-specific aggregation rules are governed by the applicable frozen task authority/protocol.

Long-lived rules:

- decision-time observation must be causal;
- future bars may not enter the current observation;
- historical replay and real-time operation must preserve the same information-availability principle;
- chart rendering is project-owned and auditable;
- model-visible annotations/hypotheses are not market facts.

## Persistent trader state

Project-owned persistent state may include:

- attention/state;
- timeframe interpretations;
- hypotheses;
- key/watch/invalidation regions;
- family/setup candidate;
- expected trigger;
- open questions;
- meaningful prior decisions;
- journal;
- hypothesis memory;
- validated-policy references.

Every mutation is attributable and auditable. Restart must preserve governed working state.

## Knowledge separation

- `JIANGHE_CANON` — read-only source truth;
- `PROJECT_VALIDATED_POLICY` — independently validated extensions;
- `DS_HYPOTHESIS_MEMORY` — candidate ideas only;
- `DS_WORKING_MEMORY` — current market state/hypotheses;
- `DS_JOURNAL` — reflection, never source truth.

## Execution-mode architecture direction

Future execution modes share the same cognition/risk/OMS contracts:

`EXECUTION_MODE = SHADOW / PAPER / REAL`

- `SHADOW`: no external order; diagnostics/fault isolation/safe degradation; not a mandatory promotion stage;
- `PAPER`: real-time end-to-end execution semantics through a paper/simulation account;
- `REAL`: real broker/account adapter under exact external-risk authority.

Normal product-level promotion direction is:

`HISTORICAL REPLAY -> REAL-TIME PAPER -> CONSTRAINED REAL MONEY`

Switching PAPER -> REAL should primarily change account/execution authority and adapter configuration, not trader cognition.

## OMS/reconciliation boundary

Each order intent must be idempotently bound to trader/wake/decision/risk/order identities.

Restart/reconnect must reconstruct account/order truth before new risk.

Truth hierarchy:

`BROKER/PAPER ACCOUNT -> PROJECT OMS LEDGER -> PROJECT POSITION STATE -> MODEL-VISIBLE POSITION SUMMARY`

Unknown order/position/account state means no new risk and fail-closed adjudication.

## Deterministic risk boundary

RiskGate has final veto.

Required controls for consequential execution include product whitelist, position limits, add-on permission, risk limits, margin/headroom, duplicate prevention, reconciliation, data/provider/runtime health and kill-switch state.

Permanent numeric limits are not defined by architecture and require Owner authority before real-money use.

## Current-state pointer

For current implementation phase, execution hold/permission, locks and next task, read only:

`CURRENT_STATE.md`

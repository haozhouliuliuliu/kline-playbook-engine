# RESEARCH_DIRECTION

## Status

```text
STATUS=OWNER_APPROVED
PROJECT_RESEARCH_PARADIGM=HUMAN_PLAYBOOK_FIRST
CURRENT_PRODUCT_DIRECTION=JIANGHE_AI_TRADER
```

This file defines the current binding research direction. Mutable readiness, locks and next work live in `CURRENT_STATE.md`.

## 1. Strategy source direction

The project learns trading judgment from attributable human trading experience rather than discovering a strategy by searching historical PnL.

For V1:

```text
CURRENT_TRADING_KNOWLEDGE_SOURCE=JIANGHE_V1_1
STRATEGY_SOURCE_EXPANSION=PAUSED
```

The Jianghe corpus is the knowledge boundary for the current trading brain. Additional traders/strategies are not part of the current normal work unless a later Owner-approved direction change reopens source expansion.

## 2. Current research route

```text
traceable Jianghe source material
-> source-faithful claims / cases / UNKNOWN / contradictions
-> versioned Jianghe knowledge pack
-> versioned Jianghe AI Trader identity
-> causal observation + working memory + fidelity evaluation
-> source-justified PRIMARY preparation
-> governed candidate outcome research only after explicit gates
-> protected validation / final-holdout governance
-> genuinely unseen Shadow/Forward evidence when later authorized
```

The project must preserve the distinction:

```text
SOURCE CLAIM
!=
AI / PROJECT INTERPRETATION
!=
IMPLEMENTED DECISION POLICY
```

Missing or contradictory source meaning stays UNKNOWN. The AI must be allowed to WAIT / NO_TRADE rather than invent a rule.

## 3. What the Jianghe AI is for

The product goal is not to compress Jianghe into a rigid indicator grid. The AI decision layer is intended to interpret the same kinds of contextual information Jianghe uses, including:

- timeframe-specific market state and trend;
- directional bias;
- key location and remaining space;
- relative strength / weakening / follow-through;
- actual execution-timeframe behavior;
- A/B/C/D family permission;
- no-trade conditions, invalidation and management.

The AI is constrained by the Jianghe knowledge pack. It is not a general-purpose free-form trading agent.

Deterministic infrastructure remains responsible for hard risk, orders, execution truth, reconciliation and Safety.

## 4. Fidelity before profitability

The first real-model question is:

> **Does the model reason like Jianghe under the source-derived constraints?**

Model/provider comparison must therefore begin with the non-outcome fidelity corpus and evaluate, at minimum:

- market-state interpretation;
- A/B/C/D/NONE classification;
- no-trade discipline;
- location != trigger;
- weakening != reversal;
- false vs confirmed breakout semantics;
- multi-timeframe discipline;
- UNKNOWN/contradiction honesty;
- decision stability;
- unjustified invention rate.

Historical profit, win rate, Sharpe, expectancy or later price movement must not be used to choose the initial Jianghe decision model.

## 5. Historical replay role

Historical 1-minute data is used to simulate a trader moving forward through time, not to hand the AI a retrospective chart.

The replay must preserve:

- forward-only time;
- no future bars;
- persistent session working memory;
- AI-created watch/key/invalidation regions;
- model latency;
- causal multi-timeframe aggregation;
- the distinction between AI hypotheses and market facts.

The current historical evidence cannot prove sub-minute decision behavior. Any future live sub-minute capability is a different version/capability.

## 6. Prohibited default route

The following remains outside the current authorized research direction:

```text
large indicator / chart-pattern / rule / parameter universe
-> historical outcome search
-> select winners
-> retrofit Jianghe or another human narrative afterward
```

A promising backtest, tool capability or model suggestion cannot silently change this direction.

## 7. Evidence / validation standards remain binding

Human Playbook First does not weaken evidence standards. Applicable controls remain governed by the frozen research protocol and current AI Trader protocol, including:

- provenance and source identity;
- SOURCE_ONLY boundaries;
- PRIMARY interpretation governance;
- point-in-time information;
- lineage and exposure inheritance;
- search-freedom / multiplicity controls;
- development / validation / final-holdout separation;
- execution realism when outcome research is later authorized;
- future genuinely unseen evidence.

This file itself authorizes no candidate outcome access, Validation, Final, Shadow, broker or real-money action.

## 8. Current architecture relationship

The current architecture is defined by:

- `ARCHITECTURE_BASELINE.md`;
- `docs/architecture/ADR_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1.md`.

The AI may propose a constrained trade intent. RiskGate, OMS, TradingState, broker reconciliation and Safety retain deterministic authority over execution and hard-risk truth.

## 9. Mutable state rule

Do not infer current readiness or next action from this direction file. Always read current `main` + `PROJECT_BRAIN_RUNTIME_BRIEF.md`, then `CURRENT_STATE.md` when the answer depends on mutable project facts.

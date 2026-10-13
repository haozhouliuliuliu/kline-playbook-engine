# JIANGHE EXECUTION AND PROMOTION ARCHITECTURE V0.1

Status: `CURRENT_FUTURE_ARCHITECTURE_DIRECTION`

Date: `2026-08-27`

Authority:

`docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`

This architecture applies to post-V0.1 execution/promotion design. It does not activate paper, shadow, broker/account, or real-money permissions.

## 1. Core separation

The system separates three concerns:

```text
TRADER COGNITION
DETERMINISTIC EXECUTION/RISK
EVIDENCE/PROMOTION GOVERNANCE
```

DeepSeek owns trading judgment. Project code owns causal market construction, risk, orders, account truth, reconciliation, fail-closed behavior and promotion evidence.

## 2. Shared real-time pipeline

Target runtime:

```text
Real-Time Market Data
-> Session/Calendar Validator
-> Causal 1m substrate + 5m wake + 15m/1H/4H context
-> Jianghe Context Assembler
-> Persistent DeepSeek Trader
-> Response Normalizer / State-Legality Guards
-> TradeIntent
-> Deterministic Risk Engine
-> OMS / Order Idempotency Layer
-> Execution Adapter
-> Order / Fill / Position / Account Reconciliation
-> Persistent Working Memory / Journal / Audit Ledger
```

The same cognition and risk/order interfaces should serve SHADOW, PAPER and REAL. Mode changes should be adapter/authority changes, not trader rewrites.

## 3. Execution modes

### `EXECUTION_MODE = SHADOW`

Purpose: diagnostic cognition-only or no-order mode.

- real-time ingestion and trader cognition may run;
- no external order is admitted;
- may be used for fault isolation, incident reproduction or safe degradation;
- not a mandatory promotion stage.

### `EXECUTION_MODE = PAPER`

Purpose: real-time end-to-end execution rehearsal without real money.

- real-time market data;
- real cognition;
- deterministic risk;
- real OMS/order lifecycle semantics;
- paper/simulation account adapter;
- acknowledgements/fills/partial fills/cancel/reject as supported;
- position/account reconciliation;
- same MANAGE/EXIT lifecycle expected for REAL.

### `EXECUTION_MODE = REAL`

Purpose: explicitly authorized constrained real-money execution.

- same trader core;
- same deterministic risk/OMS/reconciliation contracts;
- real broker/account adapter;
- external writes only under exact Owner authority;
- fail-closed on any unresolved state uncertainty.

## 4. Idempotency and duplicate-order prevention

Every intended order must bind at least:

- trader identity;
- product/contract;
- governed wake identity;
- normalized decision identity;
- intent identity;
- risk-admission identity;
- client order identity;
- execution mode.

The OMS must reject a second order generated from the same admitted intent/wake unless an explicitly modeled replace/cancel transition permits it.

Restart/reconnect must reconstruct order state from immutable project ledger plus execution/account truth before new risk is admitted.

## 5. Reconciliation hierarchy

Execution truth is resolved in this order:

```text
BROKER/PAPER ACCOUNT TRUTH
-> PROJECT OMS / IMMUTABLE ORDER LEDGER
-> PROJECT POSITION STATE
-> MODEL-VISIBLE POSITION SUMMARY
```

DeepSeek never overrides broker/account truth.

If reconciliation cannot determine whether an order filled or a position exists:

`UNKNOWN_EXECUTION_STATE -> NO_NEW_RISK + FAIL_CLOSED + HUMAN/PROJECT ADJUDICATION`

## 6. Deterministic risk boundary

Risk engine vetoes discretionary intent.

Required future inputs include:

- authorized product whitelist;
- max position;
- allowed add-on behavior;
- per-trade risk limit;
- daily risk limit;
- cumulative/drawdown limit;
- margin/headroom requirement;
- account availability/reconciliation status;
- data freshness;
- provider/trader runtime health;
- kill-switch status.

No model output may relax a deterministic risk rule.

Numeric permanent limits are not defined by this architecture and require Owner authority before REAL.

## 7. Kill-switch semantics

Kill switch must support at least:

- deny all new entries;
- cancel working orders where safe/authorized;
- preserve/reconcile existing position truth;
- allow only separately approved risk-reducing/exit handling when the system can prove order/account state;
- create immutable incident/audit evidence.

Automatic “continue trading through uncertainty” is forbidden.

Potential triggers include:

- stale/missing/out-of-order market data;
- provider/model mismatch;
- repeated/duplicate wake/request anomaly;
- response normalization failure;
- execution adapter error;
- unknown order state;
- position/account mismatch;
- margin/headroom violation;
- risk-limit breach;
- restart identity mismatch;
- manual Owner/operator kill.

## 8. Paper evidence model

Paper evidence must keep separate ledgers for:

- causal market ingestion;
- model decisions;
- risk decisions;
- order lifecycle;
- fills/partial fills/cancels/rejects;
- position/account reconciliation;
- restarts/reconnects;
- provider/data/execution faults;
- fault-injection drills;
- trading outcomes.

Fault-injection evidence must never be mislabeled as naturally occurring trader behavior.

An `EFFECTIVE_TRADING_DAY` requires the intended real-time stack to have been available for the governed session coverage and any integrity anomaly to be resolved/adjudicated.

## 9. Paper exit review matrix

Paper exit is a review, not an automatic timer.

Required review dimensions:

```text
TIME_COVERAGE
MARKET_DATA_INTEGRITY
TRADER_STATE_CONTINUITY
NATURAL_LIFECYCLE_EVENT_COVERAGE
ORDER_LIFECYCLE_COVERAGE
RECONCILIATION
FAULT_PATH_COVERAGE
DUPLICATE_PREVENTION
RISK_REJECTION
AUDIT_COMPLETENESS
TRADER_BEHAVIOR
PROFITABILITY_EVIDENCE
```

Approximately 10 effective trading days is the earliest review point, not a pass condition.

If event coverage remains insufficient after 20 or more days, paper remains open until evidence is sufficient or the Owner changes direction.

## 10. Historical-to-paper continuity

Historical high-speed replay and real-time paper share:

- trader identity semantics;
- causal observation contracts;
- wake policy authority;
- memory/state schemas;
- decision schema/normalizer;
- deterministic risk interface;
- audit identities.

Historical replay may use a separately governed historical execution evaluator. Paper/real execution use live execution adapters and live account reconciliation. Historical fills must never be confused with broker truth.

## 11. Capital adequacy service

Before REAL, a deterministic capital-adequacy analysis should consume:

- contract spec/multiplier/tick data;
- margin schedule;
- actual Jianghe entry-to-invalidation distances observed in historical/paper evidence;
- fees/slippage assumptions and observations;
- one-lot loss distribution under those invalidations;
- gap/stress scenarios;
- account capital envelope;
- proposed risk-rule candidates.

Outputs should include:

- one-lot required margin;
- one-lot stop-risk distribution;
- one-lot risk/capital ratio;
- margin/headroom ratio;
- stress loss estimate;
- minimum viable capital under each proposed risk policy;
- PASS/FAIL/INSUFFICIENT_EVIDENCE.

The service does not set permanent risk limits; it informs the Owner decision.

## 12. Initial constrained real target

Future candidate only:

```text
ACCOUNT_CAPITAL_ENVELOPE ~= FIXED_MODEST
PRODUCT = RB
MAX_POSITION = 1 LOT
NO_AUTOMATIC_ADD_ON
```

The capital envelope is not the risk budget. If one lot is too large for the approved risk constraints, the system must not trade.

## 13. Promotion state model

Suggested evidence states:

```text
SYSTEM_READY = YES/NO/INSUFFICIENT
TRADER_BEHAVIOR_ACCEPTABLE = YES/NO/INSUFFICIENT
RISK_COMPATIBLE = YES/NO/INSUFFICIENT
EVIDENCE_SUFFICIENT = YES/NO
PROFITABILITY_EVIDENCE = FAVORABLE/UNFAVORABLE/MIXED/INSUFFICIENT
LONG_TERM_EDGE_EVIDENCE = NOT_ESTABLISHED/DEVELOPING/ESTABLISHED
```

A short historical or paper window normally cannot establish long-term edge.

Promotion requires the explicit authority appropriate to the next external-risk stage even when all engineering evidence is green.

## 14. Cost accounting interface

Every paid model request should record when available:

- provider/model;
- request/wake identity;
- input tokens;
- cache-read/cache-write tokens;
- output tokens;
- reasoning tokens;
- provider request id;
- model usage timestamp;
- estimated charge under the authority's pricing snapshot;
- cumulative slot usage/cost estimate.

Before the next request, the provider gate checks:

```text
REQUEST_COUNT < AUTHORIZED_MAX_REQUESTS
AND
ESTIMATED_CUMULATIVE_COST + CONSERVATIVE_NEXT_REQUEST_RESERVE <= AUTHORIZED_SPEND_CEILING
```

If exact provider billing is not synchronously available, request-count authority remains the hard primary boundary.

## 15. Current locks

This architecture grants no execution permission.

Current locks remain whatever `CURRENT_STATE.md` and the exact current work-package authority state. At adoption time:

- V0.1 three-call provider smoke: pending Owner payment confirmation;
- full V0.1 provider replay: locked;
- PAPER: locked/deferred;
- SHADOW: locked;
- broker/account: locked;
- REAL: locked;
- real money/capital funding: locked.
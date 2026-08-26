# JIANGHE POST-V0.1 HISTORICAL -> PAPER -> CONSTRAINED REAL-MONEY ROADMAP — OWNER DECISION V0.1

Status: `APPROVED_DIRECTION__POST_V0_1_ONLY`

Date: `2026-08-27`

Product: `JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

This authority records the Owner-approved staged direction **after** closure of the current `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`. It does not alter, replace, or reopen the frozen semantics of the current V0.1 work package.

## 1. Governing headline

The post-V0.1 validation path is:

```text
CURRENT V0.1 CLOSURE
-> CU ~1 trading month chronological historical capability replay
-> RB ~1 trading month chronological historical capability replay
-> CU/RB focused comparative analysis
-> conditional RB regime supplementation only if evidence gaps remain
-> REAL-TIME PAPER EXECUTION
-> constrained RMB ~100,000 account / RB / max 1 lot real-money candidate
-> evidence-governed later widening, if separately approved
```

The product-level combination is:

```text
HISTORICAL HIGH-SPEED REPLAY
+
REAL-TIME PAPER EXECUTION
+
MINIMAL-CONSTRAINED REAL-MONEY VALIDATION
```

An independent shadow-trading stage is **not** a mandatory promotion stage. `SHADOW` remains an optional diagnostic / fault-isolation execution mode.

## 2. Current V0.1 is frozen and must not be contaminated

The current work package remains `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1` under its existing Owner authority.

The following remain unchanged:

- outcome-blind deterministic V0.1 product/window selection;
- sealed product `cu` and concrete contract `SHFE.cu2406`;
- 20 prior-history trading days;
- 2 burn-in + 20 measurement trading days;
- exactly 1998 governed closed-5m wakes for the sealed slice;
- causal `4H / 1H / 15m / 5m` observation semantics;
- fixed one-wake/one-request policy;
- intent-only lifecycle;
- `PAPER_EXECUTION = DEFERRED` inside V0.1;
- V0.1 is lifecycle/restart/memory/audit integrity research, not a profitability gate;
- no outcome-driven rerun, sample replacement, or post-hoc window selection.

The new CU/RB roadmap starts only after formal V0.1 closure.

## 3. V0.1 closure gate

V0.1 may be declared `CLOSED` only after all of the following are formally evidenced:

1. offline preexecution gates remain `PASS`;
2. the bounded three-call provider smoke, if separately paid-authorized, completes under its exact authority or fails closed and is formally adjudicated;
3. a separate Owner authority opens the full sealed V0.1 provider replay before any such paid calls;
4. the sealed provider replay executes at most once under the frozen V0.1 design, with zero outcome-driven rerun;
5. exact wake/request accounting, identity continuity, causal-data integrity, memory/restart continuity, state legality, retrieval attribution, audit reconstruction and zero policy self-promotion are adjudicated;
6. final V0.1 evidence explicitly separates `REPLAY_INTEGRITY` from `TRADER_REASONING_QUALITY`;
7. any observed losses, missed trades, WAIT frequency or poor decisions are recorded as trading evidence and are not silently converted into replay-integrity failures;
8. final closure authority/evidence is written to GitHub.

Current paid authority does **not** authorize item 3 or 4.

## 4. Post-V0.1 historical capability research

The first two post-V0.1 paid historical work packages are CU then RB. Other products are not default members of this route.

### 4.1 Common research principles

Both CU and RB packages must be:

- chronological;
- causal and future-blind;
- one persistent trader within each run;
- deterministic in window selection;
- outcome-blind at selection time;
- separately sealed before provider execution;
- auditable at every wake;
- protected from model-visible future fills, future PnL and post-hoc outcome labels.

The same frozen cognitive configuration should be used for CU and RB unless a later approved authority explicitly creates a new trader descendant. Product-specific working memory is isolated per run so CU experience does not silently preload RB and vice versa.

### 4.2 Deterministic one-month window selection

The roadmap adopts this selection rule for the initial CU/RB capability packages:

`POST_V0_1_FORWARD_FIRST_ELIGIBLE_ALIGNED_WINDOW_V0_1`

Fixed anchor:

- start scanning strictly after the current V0.1 measurement end (`2024-05-14`) in the accepted canonical corpus;
- inspect only calendar, contract mapping, partition completeness, session metadata and other eligibility facts;
- never inspect Jianghe decisions, profitability, price-path attractiveness, volatility labels, trend/range labels, or later outcomes when selecting the initial windows.

CU selection:

1. require at least 20 prior eligible trading days for causal context;
2. find the first forward eligible block consisting of 2 burn-in trading days plus 20 measurement trading days;
3. require one unchanged governed concrete contract across the 22 replay days;
4. seal all dates, mapping identities, partition identities and slice identity before provider calls.

RB selection:

1. first attempt to use the exact same 22 trading dates selected for CU, if RB satisfies all eligibility and unchanged-contract requirements;
2. if aligned dates are ineligible, scan forward from the same fixed anchor and select the first eligible 2+20 block by the same metadata-only rule;
3. record whether the comparison is `CALENDAR_ALIGNED` or `NONALIGNED_FIRST_ELIGIBLE`.

This rule exists to avoid post-hoc selection while preferring an aligned CU/RB comparison when mechanically possible.

### 4.3 Research questions

The initial CU/RB historical packages evaluate at least:

- stable causal market reading across a continuous month;
- reasonableness of `WAIT / WATCH / ENTER / MANAGE / EXIT` behavior;
- unsupported over-trading or excessive inactivity;
- consistency between stated trigger/invalidation and later action;
- exit behavior when a thesis is invalidated;
- usefulness and correctness of persistent working memory;
- state/personality/method drift;
- cross-market transfer between CU and RB;
- whether Jianghe behavior reflects general price-action ability or product dependence;
- execution-aware trade behavior once a separately governed historical execution evaluator is approved.

Profitability becomes legitimate **evidence** in these post-V0.1 capability studies, but is never the sole gate.

### 4.4 Historical execution/PnL evaluation boundary

Post-V0.1 capability research may add a deterministic historical execution/PnL evaluator only under a dedicated work-package authority that freezes its mechanics before paid replay.

Requirements:

- model decisions are made before system-side fill/PnL calculation;
- model decision context never receives future bars or future execution results;
- fill, fees, slippage, margin and PnL logic are project-owned and auditable;
- trading-cognition evidence and execution/PnL evidence are stored as separate dimensions;
- no execution outcome may trigger a same-wake re-ask or outcome-driven rerun.

Exact fill/slippage semantics are **not frozen by this roadmap** and require a later research-design authority.

## 5. CU/RB focused comparative analysis

After both initial monthly packages finish, produce one formal comparative review before adding more paid history.

The review must distinguish:

- `SYSTEM_INTEGRITY`;
- `TRADER_COGNITION_QUALITY`;
- `BEHAVIORAL_CONSISTENCY`;
- `EXECUTION_COMPATIBILITY` if an evaluator exists;
- `PROFITABILITY_EVIDENCE`;
- `GENERALIZATION_EVIDENCE`;
- `EVIDENCE_GAPS`.

The comparison must not declare RB the best or most profitable product merely because RB is the likely first real-money candidate under an approximately RMB 100,000 capital envelope.

## 6. Conditional RB regime supplementation

Additional RB historical scenarios are **conditional**, not automatic.

They may be proposed only if the CU/RB comparative review records a concrete unresolved evidence gap, for example:

- insufficient behavioral coverage;
- insufficient trade/lifecycle event coverage;
- unresolved regime sensitivity;
- unresolved invalidation/exit behavior;
- unresolved RB capital-adequacy behavior;
- unresolved robustness to trend/range/volatility/reversal environments.

Before any supplemental paid replay, a separate regime-selection authority must freeze a machine-readable classifier and selection method **before** looking at Jianghe performance in candidate windows.

Permitted target families include:

- trend;
- range;
- rapid rise;
- rapid fall;
- high volatility;
- low volatility;
- false breakout / fast reversal.

The supplemental selector may use predeclared market-path statistics to find informative regimes, but may not use Jianghe profit/loss, trade quality, or response attractiveness to choose windows. Exact regime formulas/thresholds are a later research-design decision and must be sealed before selection.

No open-ended rule such as “add more samples until confidence feels good” is permitted.

## 7. Product scope after V0.1

Default post-V0.1 research priority:

1. CU;
2. RB;
3. conditional RB supplemental scenarios if justified.

AU, AG, AL and NI are not part of the default paid path. They are not permanently excluded.

A third product may be proposed only when CU/RB evidence leaves a material question that cannot be answered without broader cross-market validation. Such expansion requires a new work-package decision and paid-call authority.

## 8. Real-time execution architecture direction

After historical research passes its review, the default next stage is `REAL-TIME PAPER`, not a mandatory standalone shadow stage.

Target execution modes:

```text
EXECUTION_MODE = SHADOW
EXECUTION_MODE = PAPER
EXECUTION_MODE = REAL
```

Normal promotion path:

```text
HISTORICAL REPLAY
-> REAL-TIME PAPER
-> CONSTRAINED REAL MONEY
```

`SHADOW` is retained for diagnostics, fault isolation, safe degradation and cognition-vs-execution troubleshooting.

Paper should reuse the eventual real execution chain as far as practical:

```text
real-time market data
-> causal bar/session construction
-> Jianghe cognition
-> normalized TradeIntent
-> deterministic risk engine
-> order generation / OMS
-> execution adapter
-> PAPER account
-> acknowledgement / fill / partial-fill / cancel / reject lifecycle
-> position + account reconciliation
-> Jianghe MANAGE / EXIT lifecycle
-> immutable audit/evidence
```

Switching from PAPER to REAL should primarily change execution/account authority and adapter configuration, not rewrite the trader core.

## 9. PAPER EXIT GATES

Paper readiness is **evidence-based**, not day-count based.

Minimum time reference:

`MIN_EFFECTIVE_TRADING_DAYS = approximately 10`

An effective trading day counts only when the intended real-time ingestion/execution stack was operational for the governed sessions and no unresolved integrity failure invalidates the day.

`TIME_COVERAGE != SUFFICIENT_EVIDENCE`

Paper exit review must cover at least the following gate families:

### 9.1 Market-data and causal-time gates

- no missing/duplicate/out-of-order governed bars;
- session/day/night transitions correct;
- stale data detected and fail-closed;
- causal higher-timeframe availability correct;
- reconnect/restart preserves causal sequence.

### 9.2 Trader/execution-state gates

- model state and execution state reconcile;
- `ENTER / MANAGE / EXIT` receives real lifecycle coverage;
- no duplicate order from repeated wake/reconnect/restart;
- intent, order, fill, position and account identities remain attributable.

### 9.3 Order-lifecycle gates

- acknowledgement handling;
- fills;
- partial fills if the simulator supports them;
- cancel path;
- reject/error path;
- unknown-order-state handling;
- deterministic risk rejection path.

Natural market activity need not produce every engineering failure mode. Controlled fault-injection drills may cover reconnect/reject/cancel/provider/data failures, but such drills must be labeled separately from natural trader behavior evidence.

### 9.4 Reconciliation and operational gates

- position reconciliation;
- account/cash/margin reconciliation;
- restart continuity;
- duplicate-order prevention after restart;
- provider/API failure fail-closed;
- market-data failure fail-closed;
- execution-adapter failure fail-closed;
- complete audit evidence.

### 9.5 Evidence-sufficiency gate

At least one end-to-end natural or simulator-supported lifecycle must be observed from `ENTER` through execution state to `MANAGE/EXIT` and final reconciliation before real-money review.

The review must also judge whether actual decision/trade/event coverage is sufficient to support the claimed readiness conclusions.

Ten effective trading days may be enough **only if** event coverage and all gates are sufficient. Twenty days with too few meaningful decisions/trades/events is not an automatic pass; paper continues or the evidence gap is escalated.

## 10. Shadow diagnostic mode

Shadow is architectural capability, not default promotion bureaucracy.

Permitted future uses include:

- isolate cognition from execution faults;
- run real-time market ingestion + cognition while disabling order submission;
- diagnose paper/broker adapter failures;
- safe degradation during execution uncertainty;
- targeted operational incident reproduction.

Current `shadow` lock remains in force until a future execution work package explicitly opens it.

## 11. Constrained real-money candidate

The first real-money candidate, **subject to future explicit Owner authority**, is:

```text
CAPITAL_ENVELOPE ~= RMB 100,000
PRODUCT = RB
MAX_POSITION = 1 LOT
```

This means:

- approximately RMB 100,000 is the account/capital envelope, **not** a risk allowance;
- RB only;
- maximum one lot;
- no automatic product expansion;
- no automatic pyramiding/add-on;
- deterministic risk engine has final veto;
- broker/account truth and reconciliation are mandatory;
- any uncertainty in model/provider/data/order/account state defaults to no new risk / fail-closed behavior.

RB is a **candidate** because one-lot granularity may fit the Owner's capital envelope better. This does not establish that RB is the most profitable, most stable, or permanently best product.

## 12. CAPITAL ADEQUACY / MINIMUM VIABLE CAPITAL framework

Before any real-money authority, perform a formal RB one-lot capital-adequacy analysis using actual Jianghe behavior and current contract/execution facts.

At minimum evaluate:

```text
one_lot_stop_risk
= contract value sensitivity to Jianghe's actual invalidation distance
+ conservative slippage
+ commissions/fees
```

and:

- initial/maintenance margin usage;
- margin headroom after one lot;
- Jianghe's observed invalidation-distance distribution;
- fees/slippage sensitivity;
- observed and stress drawdown behavior;
- overnight/session-gap exposure where applicable;
- operational reserve/headroom;
- one-lot risk as a fraction of the RMB 100,000 capital envelope.

`MINIMUM_VIABLE_CAPITAL` is the capital level at which the smallest tradable unit can satisfy the separately approved risk constraints with adequate operational/margin headroom.

If one RB lot violates approved risk constraints, the correct action is `NO TRADE / CAPITAL INADEQUATE`; the project must not loosen risk rules merely to force participation.

## 13. Risk, kill-switch and reconciliation requirements

Before real-money execution, project-owned deterministic mechanics must include:

- per-trade risk gate;
- daily risk gate;
- cumulative/drawdown risk gate;
- margin/headroom gate;
- max-position gate;
- product whitelist;
- duplicate-order prevention;
- order-state reconciliation;
- position reconciliation;
- account/cash/margin reconciliation;
- reconnect/restart recovery;
- explicit kill switch;
- stale-data/provider failure handling;
- unknown-order/account state fail-closed behavior;
- immutable order/risk/audit ledger.

This roadmap does **not** freeze permanent numeric per-trade/daily/drawdown limits. Those are permanent risk rules and require a later explicit Owner decision before real-money use.

## 14. Promotion framework

Promotion reviews must explicitly separate these propositions:

1. `SYSTEM_READY` — ingestion, provider, execution, persistence, reconciliation and safety work correctly;
2. `TRADER_BEHAVIOR_ACCEPTABLE` — Jianghe's decisions and lifecycle behavior are sufficiently coherent for the bounded next stage;
3. `RISK_COMPATIBLE` — smallest permitted position fits approved capital/risk limits;
4. `EVIDENCE_SUFFICIENT` — enough relevant events have occurred to justify the claim;
5. `PROFITABILITY_EVIDENCE` — observed outcome evidence is favorable/unfavorable/uncertain;
6. `LONG_TERM_EDGE_EVIDENCE` — stronger statistical evidence of durable edge, which short windows cannot establish.

Paper profit alone does not authorize real money. Ten no-loss days do not authorize real money. Conversely, the project does not require a short paper window to prove long-term statistical edge before a minimal constrained real-money validation can ever be considered.

Any real-money promotion requires an explicit Owner decision after review of all five readiness dimensions: cognition quality, execution correctness, risk compatibility, operational reliability and evidence sufficiency.

## 15. Widening after constrained real money

Passing the initial RB one-lot stage does not automatically widen authority.

Future proposals may include:

- longer real-money observation;
- higher but bounded sizing;
- add-on/pyramiding permission;
- a second product;
- CU;
- a larger capital envelope.

This roadmap freezes no numeric widening schedule. Every widening step requires evidence and a new Owner authority for any material risk/product/capital change.

## 16. Provider/cost budget framework

Cost is governed per paid work package, not by a blanket roadmap budget.

Current official DeepSeek public pricing for `deepseek-v4-flash` is a reference input only. The active project model is `deepseek-v4-flash-vision-exp`; unless DeepSeek publishes an exact price for that model, the project must not claim the public flash price is the exact vision-exp billing rate.

For every future paid replay:

1. estimate governed wake/request count from the sealed schedule;
2. use real smoke/full-replay `usage` ledger to estimate input/output/cache usage per request;
3. publish low/base/conservative cost estimates;
4. bind a hard request-count ceiling to the exact sealed work package;
5. obtain an explicit Owner-approved CNY spend ceiling;
6. record actual usage and billing-relevant fields after every admitted response;
7. before each next request, compare accumulated spend/usage plus a conservative next-call reserve against the approved ceiling;
8. stop before issuing the next request if the remaining budget is insufficient;
9. never use an outcome-driven rerun to consume remaining budget.

If provider billing is asynchronous or the exact model tariff is unavailable, monetary stop-before-overrun cannot be guaranteed to the cent. In that case the hard request cap is the primary enforceable bound and the CNY ceiling is implemented conservatively from observed usage.

“CU + RB costs about CNY 400” is therefore a planning hypothesis, not authority or verified fact.

## 17. Autonomous work vs Owner decisions

### Project brain may autonomously proceed with

- ordinary engineering and tests within an already approved work package;
- deterministic data/window eligibility tooling;
- no-provider dry runs;
- evidence capture and consistency checks;
- replay/paper analysis under frozen protocols;
- fault-injection tests that do not affect external accounts;
- documentation/state synchronization;
- cost estimation from recorded usage;
- bug fixes that do not change trading/research semantics or permanent risk rules.

### Explicit Owner authority remains required for

- each new paid provider execution slot / spend ceiling;
- a new research design that freezes materially new experimental semantics;
- historical execution/fill/PnL semantics before they become research authority;
- paper broker/account connection or external account writes;
- any broker/account action;
- permanent numeric risk rules;
- real-money activation;
- actual capital funding/deposit;
- any real order;
- product expansion;
- position-size/add-on widening;
- materially larger capital envelope;
- irreversible external actions.

## 18. Current authorization boundary remains unchanged

This roadmap is a **future-direction authority**, not execution authority.

At the time this document is adopted, current V0.1 remains at:

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_PREPAYMENT_READY`

The only next possible paid slot remains the separately bounded three-call V0.1 smoke, and it is still pending final Owner payment confirmation.

This roadmap does not authorize:

- the three-call smoke itself;
- the full 1998-call V0.1 replay;
- CU/RB post-V0.1 paid replays;
- paper execution/account connection;
- shadow execution;
- broker actions;
- real money;
- RMB 100,000 funding;
- any permanent numeric risk parameter.

## 19. Exact current next task

The current exact task remains:

`OWNER_PAYMENT_CONFIRMATION_FOR_THREE_CALL_PROVIDER_SMOKE`

No post-V0.1 implementation should jump ahead of the current V0.1 closure path.
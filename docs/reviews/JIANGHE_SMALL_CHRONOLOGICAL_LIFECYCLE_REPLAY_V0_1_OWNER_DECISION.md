# JIANGHE SMALL CHRONOLOGICAL LIFECYCLE REPLAY V0.1 — OWNER DECISION

Status: `APPROVED`

Date: `2026-08-26`

Approved work package:

`SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

This authority supersedes the candidate-only status of the reviewed design. It opens the offline engineering, test, deterministic slice-selection and no-provider dry-run work required to prepare the replay. It does **not** itself authorize a real DeepSeek/provider call.

## 1. Research purpose

V0.1 tests whether one fixed `JiangheAITraderIdentity` can move causally forward through one bounded real historical segment as one persistent trader, with stable identity, persistent memory, attributable Jianghe retrieval, legal state transitions, exact request accounting, restart continuity and zero policy self-promotion.

V0.1 is not a profitability backtest, not learning, not validation/holdout, not adaptive-wake optimization, not contract-roll research and not execution-quality research.

Profit or loss is not a PASS/FAIL criterion.

## 2. Owner research-quality rule

`NO_ARTIFICIAL_CALL_CAP__NO_WASTEFUL_CALLS`

There is no artificial DeepSeek call-count ceiling when calls are scientifically useful. Cost and request count must be recorded, but cost minimization must not distort the experiment.

Forbidden waste includes duplicate retries, hidden second requests, outcome-driven re-asking, repeated same-state requests merely to seek a nicer answer, and unnecessary parallel variants.

## 3. Fixed V0.1 wake policy

`WAKE_POLICY = EVERY_NEW_CLOSED_5M_BAR`

- each newly available closed 5m bar during governed sessions creates exactly one model wake;
- 15m/1H/4H context refreshes become visible only when causally available and do not create duplicate requests at the same timestamp;
- completed 1m bars remain the historical substrate but do not themselves create model wakes;
- V0.1 does not add adaptive/event-driven extra model wakes;
- exactly one admitted model request per governed wake;
- retries remain zero and hidden second requests remain forbidden.

Adaptive wake may be studied later as its own variable. V0.1 isolates trader lifecycle quality from wake-policy quality.

## 4. Outcome-blind deterministic historical slice

Use only the accepted canonical corpus and governed E07 point-in-time mapping machinery.

Product ordering is the accepted canonical order:

`cu -> al -> ni -> au -> ag -> rb`

Start with `cu`; if no eligible V0.1 window exists, move through that order mechanically.

The selector must:

1. scan forward from the beginning of the accepted 2024 corpus;
2. require at least 20 prior eligible trading days for causal chart/context history;
3. select the first subsequent contiguous window containing 2 burn-in trading days plus 20 measurement trading days;
4. require one unchanged point-in-time mapped concrete contract across the 22 replay days;
5. require complete required canonical partitions and governed session metadata;
6. inspect only mapping, eligibility, calendar, completeness and governed metadata facts;
7. never inspect price path, returns, volatility, trade outcome, news label, profitability or whether a period looks calm/extreme/trending/ranging.

The exact product, contract, dates, mapping identity, partition identities and slice identity must be sealed before any provider execution.

Contract-roll behavior is deferred.

## 5. Burn-in and measurement

Burn-in: `2 trading days`.

- same trader identity and fixed 5m wake policy as measurement;
- working memory, governed journal and non-executable hypotheses may accumulate;
- ENTER may be recorded as intent, but no execution/position fill claim is made;
- no reset at the burn-in/measurement boundary.

Measurement: `20 trading days`.

- continue the exact same trader identity and state;
- no prompt/model/context-policy mutation during the run;
- no manual memory cleanup after inconvenient decisions;
- no outcome-driven rerun.

## 6. V0.1 execution boundary

`PAPER_EXECUTION = DEFERRED`

V0.1 records normalized `ENTER / MANAGE / EXIT` intent and only the minimal project-owned intent-position lifecycle state needed to preserve legal decision-state semantics.

V0.1 does not claim historical fills, slippage, partial fills, broker truth, floating amount PnL, cumulative return or execution realism.

Paper execution must be a later separate work package.

## 7. Owner single-purpose cognitive-scope decision

`MODEL_COGNITIVE_SCOPE = TRADING_ONLY`

DeepSeek is the Jianghe trader, not the project operator.

The project system must remove mechanically decidable or operational concerns from the model's cognitive workload wherever possible. The model must not spend reasoning capacity deciding or troubleshooting matters that the project can deterministically supply.

### System-owned responsibilities — NOT DeepSeek responsibilities

The project/runtime owns and determines:

- when the model wakes;
- replay clock and time progression;
- historical slice selection;
- contract mapping and data eligibility;
- session/calendar validity;
- which bars are causally available;
- chart construction and renderer rules;
- tool registration and safe tool arguments;
- context assembly and bounded retrieval limits;
- memory persistence mechanics;
- database/storage/restart mechanics;
- provider routing;
- retries and failure handling;
- request accounting and cost logging;
- audit logging;
- response schema validation/normalization;
- experiment duration and PASS/FAIL gates;
- paper/broker/account/risk mechanics;
- project governance and policy promotion.

DeepSeek must not be asked to redesign, debug, schedule or manage any of those systems during a trading decision.

### DeepSeek-owned cognitive task

At each governed wake, DeepSeek should spend its reasoning budget only on the current trading task:

1. understand the current causal 4H/1H/15m/5m market picture within the adopted timeframe roles;
2. retrieve and apply relevant Jianghe evidence and already permitted memory;
3. determine current market state, important locations, active setup/family if any, direction/bias if any, expected trigger and invalidation;
4. choose the allowed normalized trading action/state for the current moment;
5. update only permitted working memory/journal/hypothesis fields when warranted;
6. state uncertainty explicitly rather than invent missing information.

### Prompt-discipline rule

The model prompt must be strict about **scope**, not predetermined market conclusions.

It must tell DeepSeek, in substance:

- you are a single-purpose Jianghe China-futures trader;
- operational/runtime facts supplied by the project are already the governing environment and are not your task to redesign;
- do not discuss project management, software engineering, API operation, scheduling, personal-life analogies, entertainment, unrelated news speculation, provider cost, experiment design or other non-trading topics;
- do not search for hidden/future data or infer unavailable facts;
- do not solve missing trading evidence by guessing;
- if required trading evidence is genuinely insufficient or contradictory, declare the uncertainty and use the permitted WAIT/NO_TRADE/WATCH-style outcome rather than inventing a system fix;
- use only the supplied causal market evidence, Jianghe canon, permitted validated policy, permitted memories and audited project tools;
- return only the required structured response schema and concise decision rationale/source references needed for audit.

The project should minimize free-form meta-instructions at runtime. Stable instructions belong in the frozen system/decision prompt identities; machine-resolvable facts should be supplied as structured context instead of being left for the model to infer.

This cognitive-scope decision is intended to reduce distraction and engineering-style model errors without constraining legitimate Jianghe trading judgment inside the approved trading domain.

## 8. Model-visible outcome boundary

V0.1 decision context must not expose:

- floating amount PnL;
- cumulative PnL/return;
- win rate;
- previous-trade win/loss labels;
- future fills/results;
- future bars;
- future contract mapping;
- future metadata state;
- post-hoc regime labels;
- post-replay human annotations.

The current frozen Jianghe knowledge pack may be used against historical market data; this is a test of today's fixed trader knowledge on past causal market evolution, not a simulation of what knowledge existed historically.

## 9. Memory policy

`DS_WORKING_MEMORY`: may mutate causally and must remain reconstructable.

`DS_JOURNAL`: may accumulate under governed write triggers such as meaningful state transition, end-of-session reflection, restart checkpoint and explicit hypothesis falsification/retirement. V0.1 journal does not receive PnL/outcome feedback.

`DS_HYPOTHESIS_MEMORY`: may create/revise falsifiable candidate hypotheses and mark them `FALSIFIED` or `RETIRED`, but remains non-executable and may never self-promote into active policy or rewrite `JIANGHE_CANON`.

## 10. Mandatory pre-replay engineering prerequisite

Current prototype storage does not preserve the full prior hypothesis body as a first-class append-only revision history when an existing hypothesis is revised.

Before real V0.1 provider execution, implement and test a project-owned append-only/versioned hypothesis revision history that reconstructs:

- exact before state;
- exact after state;
- timestamp;
- observation/request provenance;
- trader identity;
- revision reason.

This is an engineering prerequisite, not a Jianghe semantic change.

## 11. Restart gates

R1 — mandatory phase-boundary restart after burn-in day 2:

- seal/export state identities;
- cleanly close runtime/store/Harness process;
- reopen from the same project-owned state;
- prove exact trader/state continuity;
- begin measurement without reset.

R2 — active-state coverage restart:

- after measurement day 3, the first persisted `WATCH`, `CANDIDATE` or `IN_POSITION` state triggers a restart before the next 5m wake;
- if no such state occurs, record `ACTIVE_STATE_RESTART_COVERAGE = NOT_OBSERVED`; do not replace the historical slice.

## 12. Experiment-invalidating failures

Any confirmed instance invalidates the run as lifecycle evidence:

- future-data/visual/mapping/metadata leakage;
- trader identity drift;
- missing or duplicate governed wake/request;
- hidden retry/request/model substitution;
- memory reset/corruption/non-causal mutation;
- forbidden/unattributable retrieval;
- illegal state transition;
- unreconstructable outcome-affecting step;
- mandatory restart continuity failure;
- journal/hypothesis/replay result changing active policy or Jianghe canon.

Bad trades, contradictory trading interpretation, missed trades, NO_TRADE frequency, loss and poor strategy quality are not replay-integrity failures. They are trading-quality/reasoning evidence.

## 13. Current authorization boundary

This Owner decision authorizes:

- formal authority synchronization;
- offline engineering;
- tests;
- deterministic slice selector;
- prompt/context contract implementation;
- hypothesis revision-history repair;
- replay orchestrator implementation;
- mock/no-provider dry runs;
- leakage/audit invariant checks.

It does **not** yet authorize:

- a real DeepSeek/provider replay call;
- learning/policy promotion;
- validation/holdout;
- shadow;
- broker/account actions;
- real money.

Current paid-call state remains `PAUSED` with `NEXT_EXPLICIT_PAID_SLOT = NONE` until a later exact provider-execution authority is created after offline gates pass.

## 14. Exact next work

`NEXT_TASK = IMPLEMENT_V0_1_OFFLINE_REPLAY_PREEXECUTION_GATES`

Engineering should proceed autonomously under this approved design until the package reaches the exact first real-provider-call boundary.
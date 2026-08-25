# CANDIDATE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1

Status: `CANDIDATE__OWNER_DECISION_REQUIRED__NO_EXECUTION_PERMISSION`

Integrated revision: `2`

Prepared from main: `83b97f90e62783911eaf23c08ac3d287b5e320b2`

Candidate branch: `research/candidate-small-chronological-lifecycle-replay-v0-1`

## 1. Purpose

The minimal persistent DeepSeek trader prototype is complete and locally accepted. The next scientifically useful step is a small chronological lifecycle replay whose purpose is to prove that one fixed governed trader can move forward through real historical market time as one continuous identity.

This is not a profitability backtest, not a wake-efficiency optimization study, not learning, not validation/holdout, and not execution-quality research.

Primary question:

> Can one fixed `JiangheAITraderIdentity` walk forward through a bounded real historical slice with causal observations, persistent memory, attributable Jianghe retrieval, exact request accounting, restart continuity, legal state transitions and zero policy self-promotion?

This document incorporates an independent external red-team design review and then resolves its proposals against current repository facts. It remains a candidate only. It grants zero real DeepSeek/provider execution permission.

## 2. Design principle: isolate the trader lifecycle first

V0.1 should change as few independent variables as possible.

Therefore V0.1 deliberately does **not** simultaneously optimize:

- attention-state adaptive wake compression;
- paper execution realism;
- profitability;
- cross-product generalization;
- contract-roll continuity;
- outcome-driven learning;
- policy promotion.

Owner research-quality direction:

`NO_ARTIFICIAL_CALL_CAP__NO_WASTEFUL_CALLS`

There is no artificial DeepSeek call ceiling if additional calls are scientifically useful. Cost/request count must still be logged, and duplicate/retry/re-ask waste remains forbidden.

## 3. Wake policy — fixed 5m lifecycle baseline

V0.1 recommendation:

`WAKE_POLICY = EVERY_NEW_CLOSED_5M_BAR`

Rules:

1. during governed trading sessions, each newly available closed `5m` bar creates exactly one model wake;
2. closed `15m`, `1H` and `4H` context refreshes become visible causally when available but do not create duplicate requests at the same timestamp;
3. canonical completed `1m` bars remain the historical substrate used to construct causal higher-timeframe observations, but do not create model wakes in V0.1;
4. session/order/watch/invalidation events are audited but do **not** add a second price-event-driven model wake in V0.1;
5. exactly one admitted model request per governed 5m wake;
6. zero retry, zero hidden second request, zero outcome-driven re-ask, zero silent model substitution.

### Why V0.1 rejects adaptive wake

Attention-state adaptive wake is likely a later product direction, but using it in the first lifecycle replay creates a confound: if the trader misses a market transition, the experiment cannot cleanly distinguish trader reasoning failure from wake-policy failure.

V0.1 first tests the driver on a regular 5m observation schedule. A later work package may test the intelligent alarm clock.

## 4. Historical slice — outcome-blind deterministic selection

Use only the accepted canonical corpus and the governed point-in-time E07 mapping seam.

### Product ordering

Use the accepted product order as recorded in `docs/evidence/CANONICAL_BALANCED_UNIVERSE.json`:

`cu -> al -> ni -> au -> ag -> rb`

Start with `cu`. This is a predeclared mechanical convention, not a claim that copper is easier, more profitable, or more Jianghe-compatible.

If no eligible V0.1 window exists for `cu`, move through the above order until one exists. The selector must not inspect price paths, returns, volatility, known profitability, or visually interesting periods.

### Window rule

For the first eligible product:

1. scan forward from the beginning of the accepted 2024 corpus;
2. require at least 20 prior eligible trading days for causal chart/context history;
3. select the first subsequent contiguous window with:
   - 2 burn-in trading days;
   - 20 measurement trading days;
   - one unchanged E07 point-in-time mapped concrete contract throughout the 22 replay days;
   - complete required canonical partitions and governed session metadata;
4. selector may inspect only mapping, eligibility, calendar, partition/data completeness and governed metadata facts;
5. selector must not inspect prices, returns, trade outcomes, news labels, or whether a period looks calm/extreme/trending/ranging.

The exact product, contract, trading days, E07 mapping identity, partition identities and slice identity must be sealed before any real provider request.

### Why V0.1 does not exclude “extreme events”

Excluding a period because a human later recognizes it as extreme is an outcome-adjacent selection rule and adds subjective sample curation. V0.1 excludes a date only for governed data/mapping/metadata eligibility reasons, not because the market looked difficult.

### Why V0.1 avoids contract roll

Contract-roll continuity is important but is a separate system variable. V0.1 proves one continuous trader on one governed concrete-contract segment first.

## 5. Burn-in and measurement

### Burn-in — 2 trading days

- same trader identity as measurement;
- same fixed 5m wakes;
- real causal DeepSeek reasoning allowed only after a separate provider-execution authority exists;
- `DS_WORKING_MEMORY`, governed journal and candidate hypotheses may accumulate;
- ENTER is recorded as an intent but execution/position activation is disabled during burn-in;
- no reset at the burn-in/measurement boundary;
- no performance interpretation.

Purpose: establish non-empty market memory before the measured lifecycle period without fabricating memory offline.

### Measurement — 20 trading days

- continue exact identity and persistent state;
- fixed 5m wake policy remains unchanged;
- normalized decisions may traverse existing legal attention/decision transitions;
- no post-hoc prompt/model/context-policy mutation;
- no manual memory cleanup after inconvenient decisions;
- no outcome-driven rerun.

Twenty days are for lifecycle/debug coverage, not a statistical edge claim.

## 6. V0.1 execution semantics — intent-only, no paper fill engine

Integrated recommendation after red-team review:

`PAPER_EXECUTION = DEFERRED`

V0.1 records normalized `ENTER / MANAGE / EXIT` intent and the resulting governed trader attention/state transition, but does not claim historical fills, slippage, partial fills, amount PnL, cumulative return or execution realism.

A minimal project-owned **intent-position lifecycle state** may exist only to preserve legal `IN_POSITION -> MANAGE/EXIT` state-machine semantics. It must not claim broker/exchange fill truth and must not expose amount PnL.

Why defer paper execution:

- execution simulation is a separate research/engineering system;
- fill/slippage semantics would create a second failure source;
- V0.1 must distinguish “the AI thought badly” from “the replay/execution simulator was wrong”;
- current goal is continuous cognition/state/audit, not execution fidelity.

Paper execution should become its own later work package after lifecycle integrity is proved.

## 7. Model-visible context boundary

At each governed 5m wake, DeepSeek may receive only information causally available by that replay time under the fixed trader/context identity.

Allowed:

- frozen read-only `JIANGHE_CANON`;
- already active `PROJECT_VALIDATED_POLICY` only;
- current `DS_WORKING_MEMORY`;
- bounded `DS_JOURNAL` retrieval;
- bounded non-executable `DS_HYPOTHESIS_MEMORY` retrieval;
- causal `4H / 1H / 15m / 5m` observation/charts;
- attributable tool results available at the current replay time;
- intent-position state required for legal MANAGE/EXIT lifecycle reasoning.

Forbidden from model decision context in V0.1:

- amount floating PnL;
- cumulative PnL/return;
- win rate;
- “this previous trade won/lost” outcome labels;
- future execution results;
- future bars;
- future/main-contract mapping facts;
- future metadata state;
- post-hoc market-regime labels;
- post-replay human annotations.

V0.1 journal and hypothesis generation are **process-only**: they do not receive PnL/outcome feedback. Outcome-based reflection belongs to a later governed learning design.

### Jianghe knowledge dates are not market leakage

V0.1 evaluates the current frozen Jianghe knowledge pack against historical market data. Jianghe material does not need to have existed by the historical market date, because the claim is not “simulate what the trader knew in 2024”; the claim is “test today’s fixed trader knowledge causally against past market evolution.”

The Jianghe pack identity must be frozen before the replay and may not mutate during the run.

## 8. Memory policy

### `DS_WORKING_MEMORY`

Allowed to mutate causally at governed wakes. All changes remain attributable to observation/trader identity and must remain reconstructable.

### `DS_JOURNAL`

Full journal records may accumulate in project storage, but writing is governed rather than unlimited.

Candidate journal write triggers:

- meaningful attention/decision state transition;
- end-of-session reflection;
- explicit restart checkpoint record;
- explicit hypothesis falsification/retirement reflection.

No PnL/outcome reflection in V0.1.

Model context remains bounded. Current runtime already retrieves journal with a bounded default rather than injecting the full journal every call.

### `DS_HYPOTHESIS_MEMORY`

Allowed lifecycle actions:

- create falsifiable candidate hypothesis;
- revise statement/falsifier/evidence references;
- mark `FALSIFIED` or `RETIRED`;
- remain non-executable.

Forbidden:

- direct or automatic promotion to active policy;
- outcome-only promotion;
- mutation of `JIANGHE_CANON`;
- hidden conversion of a candidate hypothesis into system prompt/policy.

## 9. New repository-verified prerequisite: hypothesis revision history

Independent red-team review correctly identified a real audit gap in the current prototype implementation.

Current repository behavior:

- the `hypotheses` table stores one current row per `hypothesis_id` and updates that row on revision;
- runtime audit records a hypothesis PUT with new identity/status;
- the complete prior hypothesis body is not preserved as a first-class revision history in final portable export/audit.

Therefore real V0.1 replay must not start until a project-owned append-only/versioned hypothesis revision history is implemented and tested.

Required property:

> For every hypothesis revision, the project must reconstruct the exact before state, exact after state, timestamp, observation/request provenance, trader identity and revision reason.

This is an engineering prerequisite, not a change to Jianghe trading semantics.

## 10. Restart tests

V0.1 requires deliberate process restart, not only natural uninterrupted execution.

### R1 — mandatory phase-boundary restart

After the final governed wake of burn-in day 2:

1. seal/export state identities;
2. cleanly close the project runtime/store/Harness process;
3. reopen from the same project-owned state directory;
4. verify exact trader identity and governed state continuity;
5. start measurement without reset.

This checkpoint is independent of market outcome.

### R2 — active-state coverage checkpoint

After measurement day 3, the first decision that leaves the trader in `WATCH`, `CANDIDATE` or `IN_POSITION` triggers a second deliberate restart **after the decision/state is fully persisted and before the next 5m market wake**.

If no such state ever occurs in the 20-day window, record:

`ACTIVE_STATE_RESTART_COVERAGE = NOT_OBSERVED`

That is a coverage limitation, not permission to choose a prettier historical window after seeing results.

## 11. Provider execution seam required before any paid replay

Current prototype runtime intentionally has no real transport and hard-locks provider authorization false.

Before a real V0.1 run, a separate reviewed execution seam must preserve:

- `MODEL_SOURCE = DEEPSEEK_ONLY`;
- `CURRENT_MODEL = deepseek-v4-flash-vision-exp`;
- pinned Harness `0.1.1-rc.2` / `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`;
- mandatory project fail-closed patch;
- `maxRetries = 0`;
- no hidden second request;
- exact prompt/model/inference configuration identity;
- append-only request/response audit;
- one request per governed 5m wake;
- local workstation execution;
- fail-closed behavior on provider/transport/normalization error.

No design document itself grants provider permission.

## 12. Leakage checklist

Real execution admission must mechanically or independently verify at least:

### Market data / timeframe

- no observation bar available after replay decision time;
- no future bar hidden in chart input;
- no incomplete higher-timeframe bar represented as a completed bar;
- no off-by-one/timezone/session-boundary leak;
- no invented sub-minute path;
- 4H role remains bounded to the already adopted scope.

### Contract mapping / metadata

- E07 mapping resolved only from governed point-in-time schedule;
- no post-hoc volume/OI/main-contract fallback;
- no future contract mapping visible early;
- no future trading-day/session metadata visible early;
- no post-hoc regime/event label used in slice selection or context.

### Knowledge / retrieval

- Jianghe pack frozen before run;
- retrieval limited to admitted read-only corpus;
- exact retrieved items/identities attributable;
- no replay outcome written into Jianghe canon or active policy.

### Memory / journal / hypotheses

- mutation timestamp never exceeds current replay time;
- no manual state reset/edit;
- journal never treated as fact/policy;
- hypothesis remains non-executable;
- exact hypothesis revision chain reconstructable;
- no outcome/PnL feedback enters V0.1 model context.

### Requests / transport

- wake count equals admitted request count;
- exactly one raw response per request;
- no hidden retry;
- no model substitution;
- no outcome-driven re-asking;
- provider failure is recorded and fails closed.

### Human/research process

- slice sealed before provider execution;
- run length sealed before provider execution;
- no early stop because results look good;
- no extension because results look bad;
- no replacement slice because the model traded poorly;
- any rerun after integrity failure is a new explicitly identified run, never a hidden overwrite.

## 13. PASS / FAIL gates

### Automatic experiment-invalidating failures

Any confirmed instance of the following invalidates the run as lifecycle evidence:

- `CAUSALITY_FAILURE` — future information/visual/mapping/metadata leak;
- `IDENTITY_FAILURE` — outcome-affecting trader identity drift;
- `WAKE_FAILURE` — missing or duplicate governed 5m wake/request;
- `TRANSPORT_FAILURE` — hidden request/retry/substitution or unbound response;
- `MEMORY_FAILURE` — state reset/corruption/non-causal mutation;
- `RETRIEVAL_FAILURE` — forbidden/unattributable/unbounded knowledge access;
- `STATE_MACHINE_FAILURE` — illegal attention/decision transition;
- `AUDIT_FAILURE` — cannot reconstruct any outcome-affecting step;
- `RESTART_FAILURE` — mandatory R1 cannot preserve exact governed state continuity;
- `POLICY_BOUNDARY_FAILURE` — hypothesis/journal/replay result changes active policy or Jianghe canon.

### Not an experiment-integrity failure

- bad market call;
- contradictory interpretation;
- missed trade;
- too many NO_TRADE decisions;
- loss/descriptive negative outcome;
- poor strategy quality.

Those are classified as `TRADER_REASONING_ERROR` or later trading-quality evidence, not as a failure of the replay machinery.

## 14. V0.1 success evidence

Before the project can claim `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1 = PASS`, evidence must prove:

1. exact frozen trader identity;
2. exact frozen slice/mapping/partition identities;
3. exact 5m wake schedule derivation;
4. exact wake count = exact provider request count;
5. zero hidden extra requests/retries;
6. zero future-data/visual/mapping leak;
7. complete request/response/retrieval/tool/memory audit;
8. working-memory continuity across the whole run;
9. mandatory R1 restart continuity;
10. R2 active-state restart result or explicit `NOT_OBSERVED` coverage limitation;
11. complete hypothesis revision history;
12. journal/policy/knowledge boundaries preserved;
13. strict output enum preserved;
14. no 4H exact volume reconciliation preserved;
15. final Harness-independent portable export reconstructs project-owned state;
16. provider request count and actual cost recorded descriptively;
17. no hidden rerun/replacement slice.

## 15. What V0.1 cannot prove

Even a perfect PASS does not establish:

- profitable edge;
- long-run profitability;
- six-product generalization;
- regime robustness;
- adaptive wake superiority;
- contract-roll correctness;
- paper execution fidelity;
- validated learning;
- safe shadow/live trading;
- broker/account readiness;
- production reliability.

## 16. Explicitly deferred variables

Do not add these to V0.1:

- attention-state adaptive wake compression;
- every-1m DeepSeek calling;
- event-driven intraday extra model wakes;
- paper fill/slippage engine;
- amount PnL feedback to the model;
- cumulative performance feedback;
- outcome-based journal learning;
- hypothesis-to-policy promotion;
- contract roll;
- multiple products in parallel;
- validation/holdout;
- shadow;
- broker/account;
- real money.

## 17. Proposed work sequence after Owner adoption

1. freeze this research design as formal work-package authority;
2. implement hypothesis revision-history prerequisite;
3. implement deterministic outcome-blind slice selector;
4. implement 5m chronological replay orchestrator and intent-position lifecycle state;
5. add mechanical leakage/request-count/restart assertions;
6. run full exact-slice no-provider mock/dry rehearsal;
7. independently audit the rehearsal and seal exact slice identity;
8. implement/review the explicit DeepSeek provider execution seam;
9. obtain exact paid execution authority for the adopted run;
10. run once: 2 burn-in days + 20 measurement days, no resets/re-asks;
11. seal raw lifecycle evidence before interpreting trader reasoning;
12. perform system-integrity review first;
13. only if integrity PASS, perform trader-reasoning review;
14. stop and decide the next separate research package.

## 18. Integrated reviewer decision matrix

### Adopted from external red-team review

- first replay is lifecycle integrity, not profitability;
- single product, bounded continuous slice;
- burn-in separated from measurement;
- deliberate restart test;
- no model-visible PnL/cumulative return;
- failure taxonomy separates system integrity from trader reasoning;
- no outcome-driven rerun;
- future-leakage checklist must include mapping/metadata/memory/journal/hypothesis/request paths;
- paper execution deferred to reduce confounding;
- hypothesis revision history is a real repository prerequisite.

### Rejected for V0.1

- selecting `rb` because it seems likely to fit Jianghe better: unsupported by current project authority;
- excluding known extreme periods: adds subjective/outcome-adjacent sample curation;
- unrestricted journal writing: unnecessary and can create self-amplifying context noise;
- attention-state adaptive wake in V0.1: scientifically useful later, but confounds the first lifecycle proof.

## 19. Owner decision required

This candidate defines a new research design and therefore requires explicit Owner adoption before it can become active authority.

The requested adoption bundle is:

- one product, mechanically selected from accepted product order;
- first eligible outcome-blind 22-day slice;
- 2 burn-in + 20 measurement days;
- exact fixed closed-5m model wake baseline;
- intent-only lifecycle, no paper fills/PnL;
- working memory enabled;
- governed process-only journal enabled;
- candidate hypothesis creation/revision/falsification enabled only after append-only revision history is implemented;
- R1 mandatory phase-boundary restart + R2 active-state restart coverage;
- no learning/policy promotion;
- no validation/shadow/broker/real money;
- no provider call until later exact execution authority is opened.

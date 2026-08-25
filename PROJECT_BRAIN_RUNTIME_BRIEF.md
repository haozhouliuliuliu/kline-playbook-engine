# PROJECT_BRAIN_RUNTIME_BRIEF

As of: `2026-08-26`

## Mandatory refresh

Before substantive project work:

1. refresh GitHub `main` HEAD;
2. read `PROJECT_DIRECTION.md`;
3. read `CURRENT_STATE.md`;
4. read task-specific authority/evidence;
5. for spend/execution, additionally refresh paid authorization, ledger/evidence and exact executable-slot authority;
6. never infer current project facts from chat history or obsolete material.

## Current headline

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

`MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1 = COMPLETE`

`LOCAL_WORKSTATION_ACCEPTANCE = PASS`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = OFFLINE_PREEXECUTION_ENGINEERING`

`MODEL_COGNITIVE_SCOPE = TRADING_ONLY`

`WAKE_POLICY = EVERY_NEW_CLOSED_5M_BAR`

`PAPER_EXECUTION = DEFERRED`

`DEEPSEEK_HARNESS = ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

`DEPLOYMENT = LOCAL_WORKSTATION_FIRST`

Owner authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

## Active V0.1 purpose

Prove one fixed persistent Jianghe DeepSeek trader can move causally through one bounded real historical segment with:

- stable trader identity;
- persistent working memory;
- bounded attributable Jianghe retrieval;
- exact request/wake accounting;
- zero future leakage;
- legal state transitions;
- restart continuity;
- auditable journal/hypothesis activity;
- zero self-promotion into active policy.

This is not a profitability test and not learning.

## Single-purpose DeepSeek boundary

DeepSeek should reason only about trading.

The project system owns wake timing, replay clock, historical slice selection, data/mapping/session validity, chart construction, context assembly, storage/restart mechanics, retries, provider routing, audit, schema normalization, experiment control, cost accounting and governance.

Prompt implementation must keep those operational concerns out of the model's trading cognition. The model should receive structured, causally valid trading context and return only the required normalized trading judgment. Missing or contradictory trading evidence is handled by explicit uncertainty / permitted WAIT-NO_TRADE-WATCH behavior, not by inventing operational fixes.

## Frozen V0.1 design

- accepted product order: `cu -> al -> ni -> au -> ag -> rb`;
- deterministic outcome-blind first eligible product/window;
- at least 20 prior eligible trading days of causal history;
- 2 burn-in trading days + 20 measurement trading days;
- no governed concrete-contract change inside the 22 replay days;
- fixed one model wake per new closed 5m bar;
- 15m/1H/4H context refreshes only when causally available, with no duplicate same-time request;
- no adaptive/event-driven wake study in V0.1;
- intent-only ENTER/MANAGE/EXIT lifecycle, no paper fill engine;
- no amount PnL/cumulative return/win-rate/outcome labels in model decision context;
- no outcome-driven rerun;
- journal is governed and outcome-blind;
- hypotheses remain non-executable;
- append-only/versioned hypothesis revision history is a pre-provider prerequisite;
- mandatory R1 phase-boundary restart and R2 active-state restart coverage;
- leakage/identity/wake/transport/memory/retrieval/state/audit/policy-boundary failures invalidate replay integrity;
- bad trade or loss alone does not invalidate replay integrity.

## Exact next work

`NEXT_TASK = IMPLEMENT_V0_1_OFFLINE_REPLAY_PREEXECUTION_GATES`

Proceed autonomously with:

1. strict trading-only prompt/context contract;
2. hypothesis revision-history repair + tests;
3. deterministic slice selector;
4. fixed-5m replay orchestrator/wake ledger;
5. causal context/runtime wiring;
6. intent-position lifecycle state;
7. restart tests;
8. leakage/request-count/audit gates;
9. exact-slice mock/no-provider dry run;
10. pre-execution evidence seal.

Stop at the exact first real-provider-call boundary unless later authority explicitly opens it.

## Harness authority

Use only:

- Harness version `0.1.1-rc.2`;
- upstream commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`;
- project fail-closed patch from `integrations/deepseek-harness/`;
- retry policy `mode: normal`, `maxRetries: 0`.

Prototype evidence remains:

- `docs/evidence/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_AUTOMATED_GATE_EVIDENCE_2026-08-26.md`
- `docs/evidence/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_WINDOWS_LOCAL_ACCEPTANCE_REPAIR_2026-08-26.md`
- `docs/evidence/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_LOCAL_WORKSTATION_ACCEPTANCE_2026-08-26.md`

## Current locks

- real DeepSeek/provider calls: `PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- learning/policy promotion: locked
- validation/holdout: locked
- shadow: locked
- broker/account: locked
- real money: locked

No current authority authorizes a provider call or real trading.
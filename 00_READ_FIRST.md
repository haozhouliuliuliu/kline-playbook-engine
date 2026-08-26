# 00_READ_FIRST

Canonical repository: `haozhouliuliuliu/kline-playbook-engine`

GitHub current `main` is the only dynamic project fact source.

## Fresh-conversation takeover

A fresh project brain must read the stable governance/architecture/tooling layer and the current dynamic work-package layer. Do not treat a state snapshot alone as sufficient project context.

Read in this order:

1. `00_READ_FIRST.md`
2. `AGENTS.md`
3. `ARCHITECTURE_BASELINE.md`
4. `TOOL_REGISTRY.md`
5. `PROJECT_DIRECTION.md`
6. `PROJECT_BRAIN_RUNTIME_BRIEF.md`
7. `CURRENT_STATE.md`
8. `docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`
9. `docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT_OWNER_DECISION.md`
10. `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`
11. `docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`
12. `docs/reviews/JIANGHE_POST_V0_1_HISTORICAL_PAPER_REAL_MONEY_ROADMAP_OWNER_DECISION_V0_1.md`
13. when execution/paper/real architecture is relevant: `docs/architecture/JIANGHE_EXECUTION_AND_PROMOTION_ARCHITECTURE_V0_1.md`

`AGENTS.md` supplies stable operating/governance rules. `ARCHITECTURE_BASELINE.md` supplies the current project architecture boundary. `TOOL_REGISTRY.md` supplies current project-scoped tool/framework/provider capability status and revalidation boundaries. `PROJECT_DIRECTION.md`, `PROJECT_BRAIN_RUNTIME_BRIEF.md` and `CURRENT_STATE.md` supply current dynamic product/work-package state. Task-specific Owner decisions and evidence then determine the exact frozen semantics and authorization boundary.

Do not use chat, stale branches, deleted dated handoffs or obsolete authority as current project facts.

## Current headline

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = PROVIDER_SMOKE_FAILCLOSED__SLOT_CLOSED`

`MODEL_COGNITIVE_SCOPE = TRADING_ONLY`

`WAKE_POLICY = EVERY_NEW_CLOSED_5M_BAR`

`PAPER_EXECUTION = DEFERRED` inside current V0.1.

`DEEPSEEK_HARNESS = ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

`DEPLOYMENT = LOCAL_WORKSTATION_FIRST`

## Current V0.1 facts

The current V0.1 is frozen and must not be changed by the later CU/RB roadmap.

Sealed V0.1:

- product `cu`;
- concrete contract `SHFE.cu2406`;
- 20 prior-history trading days;
- 2 burn-in + 20 measurement days;
- exactly 1998 governed closed-5m wakes;
- causal `4H / 1H / 15m / 5m` observation;
- one persistent trader;
- intent-only lifecycle;
- no paper fills/PnL inside V0.1;
- no learning or policy promotion.

Offline preexecution gates and the exact-slice real-corpus mock rehearsal are `PASS`.

## Current provider-smoke boundary

Three-call provider-smoke preparation is complete and CI-verified.

Frozen smoke scope:

- first 3 governed wakes only;
- exact model `deepseek-v4-flash-vision-exp`;
- exactly 4 causal PNGs per request;
- exactly 1 provider request per wake;
- `maxRetries = 0`;
- forced project-owned restart after successful call 2 before call 3;
- call 4 forbidden;
- full 1998-call replay unauthorized.

Real three-call provider smoke STOPPED FAIL-CLOSED on `2026-08-27`:

`docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`

Machine authority is terminal (slot consumed/closed):

`status = REVOKED`

`owner_payment_confirmation = true`

`max_spend_cny = 3.00`

`max_provider_calls = 3`

`max_retries = 0`

`full_replay_1998_calls_authorized = false`

`authority_identity = 6622351c707538c0db881cf69e1dbd388ae2f1c339d478e67932c65d247b3ce9`

Therefore:

`REAL_DEEPSEEK_PROVIDER_CALLS = STOPPED__SLOT_CLOSED__NO_AUTHORITY_TO_RERUN`

`NEXT_EXPLICIT_PAID_SLOT = NEW_OWNER_AUTHORITY_REQUIRED`

`FULL_V0_1_1998_CALL_REPLAY = LOCKED`

## Post-V0.1 approved direction

The later roadmap is approved **for after V0.1 closure only**:

```text
V0.1 closure
-> CU ~1 trading month chronological historical capability replay
-> RB ~1 trading month chronological historical capability replay
-> CU/RB comparative analysis
-> conditional RB regime supplementation only if evidence gaps justify it
-> REAL-TIME PAPER
-> constrained RMB ~100,000 / RB / max 1 lot real-money candidate
-> later widening only by evidence + new authority
```

Normal promotion path:

`HISTORICAL REPLAY -> REAL-TIME PAPER -> CONSTRAINED REAL MONEY`

A standalone shadow stage is not mandatory. `SHADOW` remains an optional diagnostic/fault-isolation mode.

RMB 100,000 is a capital envelope, not a risk budget. RB is a first real-money candidate, not a claim that RB is the most profitable or best product.

## Current locks

Still locked unless a later exact authority explicitly opens them:

- current three-call provider smoke: CLOSED/REVOKED after fail-closed (evidence `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`); any re-run needs a new Owner paid authority;
- full V0.1 1998-call replay;
- post-V0.1 CU/RB paid replays;
- learning/policy promotion;
- historical execution/PnL semantics until separately approved;
- SHADOW execution;
- PAPER execution/account connection;
- broker/account actions;
- permanent numeric risk rules;
- real money / capital funding / real orders;
- automatic product or position-size expansion.

## Exact current next task

`NEXT_TASK = OWNER_DECISION_REQUIRED_AFTER_FAILCLOSED_PROVIDER_SMOKE`

Do not jump to post-V0.1 implementation before current V0.1 closes.

## First takeover report

A fresh project brain first performs read-only takeover and reports only:

- current `main` HEAD;
- whether stable governance/architecture/tooling and dynamic core authority agree;
- project-scoped `CANDIDATE / VERIFIED / ADOPTED` tool/runtime statuses relevant to current work;
- product/model/Harness pin;
- current V0.1 work package, phase and frozen sealed design;
- current three-call smoke status and paid boundary;
- post-V0.1 approved roadmap headline;
- current paper/shadow/broker/real-money locks;
- exact next task;
- contradictions, if any.

Then stop for Owner confirmation before making new changes in that fresh conversation.
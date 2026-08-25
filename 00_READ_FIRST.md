# 00_READ_FIRST

Canonical repository: `haozhouliuliuliu/kline-playbook-engine`

GitHub current `main` is the only dynamic project fact source.

## Fresh-conversation takeover

Read in this order:

1. `00_READ_FIRST.md`
2. `PROJECT_DIRECTION.md`
3. `PROJECT_BRAIN_RUNTIME_BRIEF.md`
4. `CURRENT_STATE.md`

Then read task-specific authority/evidence. For the active work package, mandatory authority is:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

Do not use deleted dated handoffs or chat as project authority.

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

## V0.1 purpose

Prove that one fixed persistent Jianghe DeepSeek trader can move causally through a bounded real historical slice with stable identity, persistent memory, attributable retrieval, legal state transitions, restart continuity, exact request accounting and zero policy self-promotion.

This is not a profitability test and not learning.

The model is a single-purpose trader. Operational/runtime work such as wake scheduling, replay time, data eligibility, mapping, chart construction, storage, retries, audit, experiment control and provider routing is project-system responsibility and should not consume DeepSeek trading cognition.

## Runtime shell

Use only pinned DeepSeek Harness:

- version `0.1.1-rc.2`
- commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project fail-closed patch under `integrations/deepseek-harness/`
- general retry `maxRetries: 0`

## Current authorization / locks

Authorized now:

- offline V0.1 engineering and tests;
- deterministic historical-slice selector;
- strict prompt/context contract;
- append-only hypothesis revision-history repair;
- replay orchestrator;
- mock/no-provider dry runs;
- leakage/audit gate implementation.

Still locked:

- real DeepSeek/provider replay calls: `PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- learning/policy promotion: locked
- validation/holdout: locked
- shadow: locked
- broker/account: locked
- real money: locked

## Exact next work

`NEXT_TASK = IMPLEMENT_V0_1_OFFLINE_REPLAY_PREEXECUTION_GATES`

Proceed autonomously with approved offline engineering. Stop at the exact first real-provider-call boundary unless a later execution authority opens it.

## First takeover report

A fresh project brain first performs read-only takeover and reports:

- current `main` HEAD;
- whether the four takeover files agree;
- product/model/Harness pin;
- active V0.1 work package and phase;
- V0.1 frozen headline design;
- current provider/learning/live locks;
- exact next task;
- contradictions, if any.

Then stop for Owner confirmation before making new changes in that fresh conversation.
# PROJECT_DIRECTION

As of: `2026-08-26`

This file is the binding current product and research direction for `kline-playbook-engine`.

## 1. Mission

Build one persistent, single-purpose China-futures AI trader whose active model source is DeepSeek, whose initial trading foundation is Jianghe's documented experience, and whose long-run improvement comes from governed memory, chronological replay, reflection, falsifiable hypothesis generation, counterexample search and independent validation.

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

## 2. Product loop

`observe market -> retrieve relevant knowledge and experience -> reason -> decide -> record -> learn under governance`

Hard risk, broker/account truth, order lifecycle, reconciliation, safety, provider routing, replay scheduling and other deterministic operational mechanics remain project-owned systems.

## 3. Single-purpose model boundary

`MODEL_COGNITIVE_SCOPE = TRADING_ONLY`

DeepSeek is the Jianghe trader, not the project operator.

The project system should pre-resolve mechanically decidable operational work such as wake timing, replay clock, data eligibility, contract mapping, session validity, chart construction, context assembly, storage, retries, audit, response validation, provider routing, experiment scheduling and cost accounting.

DeepSeek's cognition should be spent only on the trading task: understand the current causal market, apply Jianghe evidence and permitted memory, identify setup/state/levels/triggers/invalidation, choose the permitted trading action, and express uncertainty without inventing missing information.

Prompts must be strict about scope and output contract, not about predetermined market conclusions. Machine-resolvable facts should be passed as structured context rather than left for DeepSeek to infer.

## 4. Knowledge hierarchy

- `JIANGHE_CANON`: source-grounded Jianghe claims/cases/unknowns; read-only to the trader.
- `PROJECT_VALIDATED_POLICY`: project extensions that passed required independent validation.
- `DS_HYPOTHESIS_MEMORY`: DeepSeek candidate ideas; never executable policy.
- `DS_WORKING_MEMORY`: persistent current market state, regions, triggers and open questions.
- `DS_JOURNAL`: auditable reflection/self-critique; not market fact or Jianghe canon.

Promotion path:

`OBSERVATION -> HYPOTHESIS -> COUNTEREXAMPLE SEARCH -> DEVELOPMENT EVIDENCE -> INDEPENDENT VALIDATION -> PROJECT_VALIDATED_POLICY`

Profit alone does not prove reasoning correctness; loss alone does not prove reasoning error.

## 5. Context and trader identity

Each DeepSeek call receives a bounded, auditable context assembled from stable trading contract, relevant Jianghe canon, validated project policy, working memory, bounded journal/hypothesis memory, causal multi-timeframe observation/charts and task-specific audited tool results.

`JiangheAITraderIdentity` binds outcome-affecting model/version, prompts, context-selection policy, memory schema/policy, chart renderer, observation schema, wake policy, decision schema/normalizer, mechanical guards, inference configuration and tool capability set. Material changes create a new trader version/descendant with exposure lineage preserved.

## 6. Observation baseline

Active stack:

`4H / 1H / 15m / 5m`

4H role:

`BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`

Future information is unavailable before its governed availability time. Working memory persists forward. Do not turn the historical corpus into independent stateless prompt exams.

## 7. Active work package

Owner-approved authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = OFFLINE_PREEXECUTION_ENGINEERING`

V0.1 frozen design headline:

- one persistent trader;
- deterministic outcome-blind first eligible product/window selection;
- product order `cu -> al -> ni -> au -> ag -> rb`;
- at least 20 prior eligible trading days for causal chart/context history;
- 2 burn-in trading days + 20 measurement trading days;
- one unchanged governed concrete contract across the 22 replay days;
- `WAKE_POLICY = EVERY_NEW_CLOSED_5M_BAR`;
- no event/adaptive wake optimization in V0.1;
- `PAPER_EXECUTION = DEFERRED`;
- no amount PnL/win-rate/outcome labels in model decision context;
- working memory active;
- journal governed and outcome-blind in V0.1;
- hypothesis memory remains non-executable;
- append-only hypothesis revision history is mandatory before real replay;
- mandatory restart continuity gates;
- replay integrity and trader reasoning quality are separate evidence dimensions;
- no learning/policy promotion in V0.1.

## 8. Current implementation sequence

Proceed autonomously through:

1. strict single-purpose system/decision prompt contract;
2. append-only/versioned hypothesis revision-history implementation and tests;
3. deterministic outcome-blind V0.1 slice selector;
4. replay orchestrator and fixed 5m wake ledger;
5. causal observation/context wiring to the persistent runtime;
6. intent-only lifecycle state required for legal ENTER/MANAGE/EXIT reasoning;
7. restart checkpoints;
8. leakage/request-count/audit invariants;
9. mock/no-provider dry run on the exact selected slice;
10. seal pre-execution evidence.

Then stop at the exact first real-provider-call boundary unless a later provider-execution authority opens it.

## 9. Mechanical guards and Harness

- `STRICT_OUTPUT_ENUM_ENFORCEMENT = IMPLEMENTED_AND_CI_VERIFIED`
- `NO_4H_EXACT_VOLUME_RECONCILIATION = IMPLEMENTED_AND_CI_VERIFIED`

`DEEPSEEK_HARNESS = ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

Use only:

- version `0.1.1-rc.2`
- commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project fail-closed patch under `integrations/deepseek-harness/`
- retry policy `maxRetries: 0`

`DEPLOYMENT = LOCAL_WORKSTATION_FIRST`

The unpatched stale-file recovery path is not admissible because it can issue a hidden second request.

## 10. Current locks

Authorized: V0.1 offline engineering, tests, selector, mock/dry-run and pre-execution evidence.

Still locked:

- real provider calls: `PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- learning/policy promotion
- validation/holdout
- shadow
- broker/account
- real money

## 11. Success definition

The project succeeds when it produces an auditable DeepSeek futures trader that begins with high-fidelity Jianghe reasoning, remembers what it is watching and why, receives only causally valid and task-relevant context, is protected from operational distractions that the system can deterministically handle, learns without corrupting source truth, promotes only independently validated improvements, and keeps deterministic operational/risk/safety responsibilities outside AI discretion.
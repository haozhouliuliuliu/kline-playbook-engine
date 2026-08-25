# PROJECT_DIRECTION

As of: `2026-08-26`

This file is the binding current product and research direction for `kline-playbook-engine`.

# 1. Mission

Build one persistent, single-purpose China-futures AI trader whose active model source is DeepSeek, whose initial trading foundation is Jianghe's documented experience, and whose long-run improvement comes from governed memory, replay, reflection, falsifiable hypothesis generation, counterexample search and independent validation.

Canonical product identity:

`JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

Current model:

`deepseek-v4-flash-vision-exp`

# 2. Product loop

The product operates as:

`observe market -> retrieve relevant knowledge and experience -> reason -> decide -> record -> learn under governance`

It must:

- follow futures markets causally through time;
- view standardized multi-timeframe K-line data and charts;
- preserve working state across calls and restarts;
- retrieve bounded relevant Jianghe evidence and prior experience;
- record decisions, memory mutations and journal entries;
- retain current hypotheses, key/watch/invalidation regions and open questions;
- generate falsifiable trading hypotheses from accumulated experience;
- search for counterexamples before promoting an idea;
- activate an experience-derived policy only after independent project validation;
- remain able to return `WAIT` / `NO_TRADE` when evidence is incomplete or contradictory.

Hard risk, broker/account truth, order lifecycle truth, reconciliation, safety and kill-switch behavior remain deterministic project systems.

# 3. Knowledge hierarchy

The runtime preserves five distinct layers.

## `JIANGHE_CANON`

Source-grounded Jianghe claims, cases, contradictions and unknowns. Read-only to the trader. Provenance remains traceable and source uncertainty remains uncertainty.

## `PROJECT_VALIDATED_POLICY`

Project extensions that have passed the required evidence and validation process. They are labeled as project policy rather than Jianghe source truth.

## `DS_HYPOTHESIS_MEMORY`

DeepSeek-generated candidate ideas. They may guide research and attention but are not executable policy.

## `DS_WORKING_MEMORY`

Persistent current market state, including active hypotheses, timeframe interpretations, key/watch/invalidation regions, setup candidate, expected trigger, open questions and prior decisions still relevant.

## `DS_JOURNAL`

Auditable reflection and self-critique. Journal content is not market fact, Jianghe canon or validated policy.

# 4. Context and memory

Persistent memory is external and project-owned.

Each DeepSeek call receives a deliberately assembled bounded context from:

1. stable trading contract;
2. relevant Jianghe canon;
3. relevant validated project policy;
4. current working memory;
5. useful analogous historical cases/decisions;
6. current causal market observation and charts;
7. task-specific tool results.

The context-selection policy is versioned and auditable because it can change trader behavior.

# 5. Learning lifecycle

Experience-derived trading ideas follow:

`OBSERVATION -> HYPOTHESIS -> COUNTEREXAMPLE SEARCH -> DEVELOPMENT EVIDENCE -> INDEPENDENT VALIDATION -> PROJECT_VALIDATED_POLICY`

A hypothesis must be falsifiable and record its identity, statement, market/setup scope, source status, motivating examples, known counterexamples, falsification condition and discovery-data exposure lineage.

Repeated redesign after observing results is additional discovery exposure and remains recorded.

A materially philosophy-changing or Jianghe-contradicting policy promotion requires explicit Owner research approval.

# 6. Process correctness and outcome

The project keeps these separate:

- `PROCESS_CORRECTNESS`: whether the decision followed information available at decision time and current governed policy;
- `OUTCOME`: what happened later;
- `RISK/EXECUTION_RESULT`: the result under a defined execution model.

Profit alone does not prove reasoning correctness, and loss alone does not prove reasoning error.

# 7. Chronological replay

Historical replay simulates one persistent trader moving forward through time.

Requirements:

- future information is unavailable before its governed availability time;
- working memory persists forward;
- decisions and notes become later experience according to the memory policy;
- deterministic attention logic controls when DeepSeek is awakened;
- replay uses causal market observations rather than independent stateless prompt exams.

Conceptual attention states:

`SCAN -> WATCH -> CANDIDATE -> IN_POSITION`

Potential wake events include meaningful bar close, watch-region entry/exit, setup transition, breakout/failure candidate, invalidation and session events.

# 8. Observation semantics

Current active view stack:

`4H / 1H / 15m / 5m`

4H role:

`BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`

Historical replay baseline uses completed 1-minute bars and does not invent sub-minute paths from 1-minute OHLC.

# 9. Mechanical guards

Mandatory current guards:

## `STRICT_OUTPUT_ENUM_ENFORCEMENT`

Machine fields such as action, direction and family use exact allowed enum values. Explanatory text lives in separate fields.

## `NO_4H_EXACT_VOLUME_RECONCILIATION`

4H volume is not exactly reconciled against overlapping lower-timeframe volume, and such equality is not used as a trading fact under the current 4H contract.

# 10. Trader identity

`JiangheAITraderIdentity` binds outcome-affecting components including:

- Jianghe knowledge identity;
- project-validated policy identity;
- DeepSeek model/version;
- prompts;
- context-selection policy;
- memory policy/schema;
- chart renderer;
- observation schema;
- wake policy;
- decision schema/normalizer;
- mechanical guards;
- inference configuration;
- tool capability set.

A material change creates a new trader version/descendant and preserves exposure lineage.

# 11. DeepSeek Harness admission

`DEEPSEEK_HARNESS = CANDIDATE_FOR_PROJECT_ADMISSION`

A pinned build must prove:

- exact selected DeepSeek model route;
- K-line image/vision support;
- persistent session/state across restart;
- project-owned memory integration;
- project-owned K-line/retrieval tools;
- auditable raw requests/responses and memory mutations;
- no silent retry, model change or prompt mutation;
- portability of core trader logic.

Harness, when verified, is only a runtime shell. Trading knowledge, memory schema, validation semantics, evidence and hard-risk logic remain project-owned.

# 12. Owner-facing workstation

The useful product surface includes:

- synchronized 4H / 1H / 15m / 5m charts;
- current DeepSeek interpretation;
- current setup/family/action;
- key/watch/invalidation regions;
- what the trader is waiting for;
- relevant Jianghe evidence/cases retrieved;
- working memory;
- recent decisions and journal entries;
- hypothesis and validation status;
- deterministic system/risk/safety status when those lanes are authorized.

UI packaging is secondary to correct persistent-trader behavior.

# 13. Current implementation order

1. finish `STRICT_OUTPUT_ENUM_ENFORCEMENT`;
2. finish `NO_4H_EXACT_VOLUME_RECONCILIATION`;
3. verify a pinned DeepSeek Harness version/commit;
4. build the smallest persistent trader proving exact model + vision + memory + Jianghe retrieval + K-line tools + journal + audit;
5. run a small chronological lifecycle replay to find architecture and memory errors;
6. design and authorize broader historical replay/research after trader identity is stable;
7. keep validation/holdout, shadow, broker/account and real-money lanes closed until their own authorities exist.

# 14. Success definition

The project succeeds when it produces an auditable DeepSeek futures trader that:

- begins with high-fidelity Jianghe reasoning;
- remembers what it is watching and why;
- retrieves bounded relevant source and experience;
- learns from audited experience without corrupting source truth;
- generates and falsifies candidate trading hypotheses;
- promotes only independently validated improvements;
- remains causally honest;
- preserves deterministic risk and safety authority outside AI discretion;
- can eventually demonstrate on protected evidence whether its matured policy improves on its initial source-grounded baseline.

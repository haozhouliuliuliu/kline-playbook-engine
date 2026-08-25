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

The trader must follow futures markets causally through time, preserve working state across calls/restarts, retrieve bounded Jianghe evidence and prior experience, record decisions and memory mutations, generate falsifiable hypotheses, search for counterexamples, and activate experience-derived policy only after independent project validation.

Hard risk, broker/account truth, order lifecycle, reconciliation, safety and kill-switch behavior remain deterministic project systems.

## 3. Knowledge hierarchy

- `JIANGHE_CANON`: source-grounded Jianghe claims/cases/unknowns; read-only to the trader.
- `PROJECT_VALIDATED_POLICY`: project extensions that passed the required validation process.
- `DS_HYPOTHESIS_MEMORY`: DeepSeek-generated candidate ideas; not executable policy.
- `DS_WORKING_MEMORY`: persistent current market state, hypotheses, regions, expected trigger and open questions.
- `DS_JOURNAL`: auditable reflection/self-critique; not market fact or Jianghe canon.

Experience-derived ideas follow:

`OBSERVATION -> HYPOTHESIS -> COUNTEREXAMPLE SEARCH -> DEVELOPMENT EVIDENCE -> INDEPENDENT VALIDATION -> PROJECT_VALIDATED_POLICY`

Profit alone does not prove reasoning correctness; loss alone does not prove reasoning error.

## 4. Context and trader identity

Each DeepSeek call receives a bounded, auditable context assembled from stable trading contract, relevant Jianghe canon, validated project policy, working memory, useful historical analogues, current causal multi-timeframe observation/charts, and task-specific tool results.

`JiangheAITraderIdentity` binds outcome-affecting model/version, prompts, context-selection policy, memory schema/policy, chart renderer, observation schema, wake policy, decision schema/normalizer, mechanical guards, inference configuration and tool capability set. Material changes create a new trader version/descendant with exposure lineage preserved.

## 5. Observation and replay

Current active stack: `4H / 1H / 15m / 5m`.

4H role: `BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`.

Historical replay must simulate one persistent trader moving forward through time. Future information is unavailable before its governed availability time. Working memory persists forward. Deterministic attention/wake logic controls model calls.

Do not turn the historical corpus into mass independent stateless prompt exams.

## 6. Mechanical guards

- `STRICT_OUTPUT_ENUM_ENFORCEMENT = IMPLEMENTED_AND_CI_VERIFIED`
- `NO_4H_EXACT_VOLUME_RECONCILIATION = IMPLEMENTED_AND_CI_VERIFIED`

## 7. DeepSeek Harness runtime shell

`DEEPSEEK_HARNESS = ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

Use only:

- version `0.1.1-rc.2`
- commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project fail-closed patch under `integrations/deepseek-harness/`
- retry policy `maxRetries: 0`

`DEPLOYMENT = LOCAL_WORKSTATION_FIRST`

Harness is the local runtime/workbench shell, not the owner of trading intelligence. A localhost browser UI is allowed. Public/cloud deployment is outside the current work package.

Trading knowledge, memory schema, context-selection policy, trader identity, evidence semantics, historical data and deterministic risk/safety logic remain project-owned and portable.

The unpatched upstream stale-file recovery behavior is not admissible because it can issue a hidden second chat-completions request.

## 8. Current implementation order

Current work package:

`MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1`

Build the smallest local prototype proving exact model/vision path, restart-surviving working memory, bounded read-only Jianghe retrieval, project-owned K-line tools, journal/hypothesis memory, complete audit and the existing guards.

Then run a small chronological lifecycle replay to debug memory/runtime behavior.

Only after the trader identity is stable should the project design broader historical replay and governed experience-learning validation.

Do not build a polished generic/public website first.

## 9. Locks

Validation/holdout, shadow, broker/account and real-money lanes remain locked until their own authorities exist. Paid provider calls require current execution authority.

## 10. Success definition

The project succeeds when it produces an auditable DeepSeek futures trader that begins with high-fidelity Jianghe reasoning, remembers what it is watching and why, retrieves bounded relevant source/experience, learns without corrupting source truth, generates and falsifies candidate hypotheses, promotes only independently validated improvements, remains causally honest, and keeps deterministic risk/safety outside AI discretion.

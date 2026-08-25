# CURRENT_STATE

As of: `2026-08-26`

## Mission

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

Target: one persistent, auditable, Jianghe-grounded DeepSeek China-futures trader whose operational distractions are handled deterministically by the project system and whose model cognition is reserved for trading.

## Knowledge boundary

- `JIANGHE_CANON`: source-grounded and read-only.
- `PROJECT_VALIDATED_POLICY`: independently validated project extensions.
- `DS_HYPOTHESIS_MEMORY`: DeepSeek candidate ideas; never executable policy.
- `DS_WORKING_MEMORY`: persistent current market state, regions, triggers and open questions.
- `DS_JOURNAL`: reflection/self-critique; not source truth or policy.

Promotion path remains:

`OBSERVATION -> HYPOTHESIS -> COUNTEREXAMPLE SEARCH -> DEVELOPMENT EVIDENCE -> INDEPENDENT VALIDATION -> PROJECT_VALIDATED_POLICY`

No replay result or model opinion may bypass that governance path.

## Observation/runtime baseline

Active stack:

`4H / 1H / 15m / 5m`

4H role:

`BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`

Mandatory guards:

- `STRICT_OUTPUT_ENUM_ENFORCEMENT = IMPLEMENTED_AND_CI_VERIFIED`
- `NO_4H_EXACT_VOLUME_RECONCILIATION = IMPLEMENTED_AND_CI_VERIFIED`

## DeepSeek Harness

`DEEPSEEK_HARNESS = ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

`PINNED_HARNESS_VERSION = 0.1.1-rc.2`

`PINNED_HARNESS_COMMIT = b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`

`DEPLOYMENT = LOCAL_WORKSTATION_FIRST`

Use the pinned Harness only with the project fail-closed patch under `integrations/deepseek-harness/` and `maxRetries: 0`.

## Completed prototype

`MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1 = COMPLETE`

`PROTOTYPE_12_OBJECTIVE_AUTOMATED_GATE = PASS`

`NATIVE_WINDOWS_PROJECT_ACCEPTANCE_CI = PASS`

`LOCAL_WORKSTATION_ACCEPTANCE = PASS`

Formal evidence:

- `docs/evidence/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_AUTOMATED_GATE_EVIDENCE_2026-08-26.md`
- `docs/evidence/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_WINDOWS_LOCAL_ACCEPTANCE_REPAIR_2026-08-26.md`
- `docs/evidence/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_LOCAL_WORKSTATION_ACCEPTANCE_2026-08-26.md`

Implemented prototype capabilities include project-owned SQLite working/journal/hypothesis state, restart persistence, bounded read-only Jianghe retrieval, causal 4H/1H/15m/5m observation/charts, audited tools, strict response normalization, prompt/tool identity binding and Harness-independent portable export.

A separate non-acceptance Windows cleanup limitation remains recorded in the Windows repair evidence: one deliberately rejected mismatched-trader constructor can retain a SQLite handle until cleanup/GC and cause immediate same-process temp-directory deletion to hit `WinError 32`. It is not a current V0.1 blocker unless replay engineering touches that failure path.

## Historical data foundation

Accepted canonical corpus:

- 2024-01-01..2025-12-31
- product order `cu/al/ni/au/ag/rb`
- 32,980 partitions
- 212 contracts
- 15,280,452 normalized 1-minute rows
- corpus identity `1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8`

Authority:

`docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`

Point-in-time research-symbol -> concrete-contract runtime mapping remains governed by the existing E07 machinery; no post-hoc volume/OI fallback is allowed.

## Active work package

Owner-approved authority:

`docs/reviews/JIANGHE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1_OWNER_DECISION.md`

`CURRENT_WORK_PACKAGE = SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

`WORK_PACKAGE_PHASE = OFFLINE_PREEXECUTION_ENGINEERING`

`NEXT_TASK = IMPLEMENT_V0_1_OFFLINE_REPLAY_PREEXECUTION_GATES`

### Frozen experiment headline

- deterministic outcome-blind first eligible product/window;
- start from canonical product order `cu -> al -> ni -> au -> ag -> rb`;
- at least 20 prior eligible trading days of causal chart/context history;
- 2 burn-in trading days + 20 measurement trading days;
- unchanged governed concrete contract across the 22 replay days;
- `WAKE_POLICY = EVERY_NEW_CLOSED_5M_BAR`;
- no adaptive/event-driven wake optimization in V0.1;
- `PAPER_EXECUTION = DEFERRED`;
- no amount PnL/cumulative return/win-rate/previous-win-loss labels in model decision context;
- no outcome-driven rerun;
- no learning or policy promotion.

## Model cognitive scope

`MODEL_COGNITIVE_SCOPE = TRADING_ONLY`

Owner direction is explicit: reduce non-trading mental load on DeepSeek as far as the project can deterministically handle it.

Project/system responsibilities include:

- wake scheduling;
- replay clock/time progression;
- data/mapping/session eligibility;
- chart construction;
- bounded context assembly;
- storage/restart mechanics;
- provider routing/retry/failure handling;
- audit/request accounting/cost logging;
- schema normalization;
- experiment control;
- governance/risk/broker mechanics.

DeepSeek's task is limited to current trading cognition: read the supplied causal market context, apply Jianghe evidence and permitted memory, identify state/levels/setup/triggers/invalidation, choose the permitted trading action/state, and declare uncertainty instead of inventing missing facts.

Prompt strictness must reduce meta/engineering distraction without predetermining legitimate trading conclusions.

## Memory/restart prerequisites for V0.1

`DS_WORKING_MEMORY`: active and causally mutable.

`DS_JOURNAL`: governed writes only; no V0.1 PnL/outcome reflection.

`DS_HYPOTHESIS_MEMORY`: non-executable; may create/revise/falsify/retire candidates only.

Repository-verified audit gap to repair before real provider replay:

- the current hypothesis store updates one current row per hypothesis;
- full previous hypothesis bodies are not first-class append-only revisions in final portable evidence.

Required pre-provider fix:

`APPEND_ONLY_HYPOTHESIS_REVISION_HISTORY = REQUIRED`

Restart requirements:

- R1 after burn-in day 2, before measurement;
- R2 after measurement day 3 at the first persisted WATCH/CANDIDATE/IN_POSITION state, before the next 5m wake; otherwise record `ACTIVE_STATE_RESTART_COVERAGE = NOT_OBSERVED`.

## Current authorization boundary

Authorized now:

- authority/status synchronization;
- offline engineering and tests;
- strict trading-only prompt/context contract;
- hypothesis revision-history repair;
- deterministic slice selector;
- replay orchestrator and wake ledger;
- intent-only lifecycle state;
- restart/leakage/audit invariants;
- mock/no-provider dry run;
- pre-execution evidence.

Still locked:

- real DeepSeek/provider replay calls: `PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- learning/policy promotion: locked
- validation/holdout: locked
- shadow: locked
- broker/account: locked
- real money: locked

No current authority permits a real provider call.
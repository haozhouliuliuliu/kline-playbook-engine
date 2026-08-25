# CURRENT_STATE

As of: `2026-08-26`

## Mission

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

Target: one persistent, auditable, Jianghe-trained, evidence-improving DeepSeek China-futures trader.

Jianghe source truth is read-only. DeepSeek may accumulate working memory, journal records and falsifiable hypotheses, but active policy is governed by the project.

## Knowledge boundary

- `JIANGHE_CANON`: source-grounded and read-only.
- `PROJECT_VALIDATED_POLICY`: independently validated project extensions.
- `DS_HYPOTHESIS_MEMORY`: DeepSeek candidate ideas; not executable policy.
- `DS_WORKING_MEMORY`: persistent current market state and active hypotheses.
- `DS_JOURNAL`: reflection/self-critique; not source truth.

Promotion path:

`OBSERVATION -> HYPOTHESIS -> COUNTEREXAMPLE SEARCH -> DEVELOPMENT EVIDENCE -> INDEPENDENT VALIDATION -> PROJECT_VALIDATED_POLICY`

PnL and process correctness remain separate evidence dimensions.

## Observation/runtime baseline

Active stack: `4H / 1H / 15m / 5m`

4H role: `BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`

Mandatory guards:

- `STRICT_OUTPUT_ENUM_ENFORCEMENT = IMPLEMENTED_AND_CI_VERIFIED`
- `NO_4H_EXACT_VOLUME_RECONCILIATION = IMPLEMENTED_AND_CI_VERIFIED`

## DeepSeek Harness

`DEEPSEEK_HARNESS = ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

`PINNED_HARNESS_VERSION = 0.1.1-rc.2`

`PINNED_HARNESS_COMMIT = b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`

`DEPLOYMENT = LOCAL_WORKSTATION_FIRST`

Use the pinned Harness only with the project fail-closed DeepSeek transport patch in `integrations/deepseek-harness/` and general retry configuration `maxRetries: 0`.

Dynamic admission on PR #41 head `e4b0e3ef972ed3c8685ab71318f4c1a885a7ccd4` passed:

- `project-dynamic-admission = success`
- repository `test = success`

PR #41 merged to main as `16021908b3226c6e9598f8030ddc5f2805825b1a`.

The dynamic gate proved pinned selected-model/vision support, project fail-closed stale-file behavior with no hidden second chat request, zero configured general retries, project memory/tool context and audit integration, SQLite session persistence across restart, and unaffected DeepSeek image serialization/config behavior.

The first prototype is local. A localhost browser UI is allowed; public/cloud deployment is not part of this work package. Project memory, trader state, market data and K-line tools remain project-owned/local unless a later authority changes that boundary.

## Historical data foundation

Accepted canonical corpus:

- 2024-01-01..2025-12-31
- cu/al/ni/au/ag/rb
- 32,980 partitions
- 212 contracts
- 15,280,452 normalized 1-minute rows
- corpus identity `1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8`

Authority: `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`

Do not start broad replay until the persistent trader prototype identity is stable.

## Current work package

`CURRENT_WORK_PACKAGE = MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1`

Exact next task:

`docs/reviews/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_HANDOFF_2026-08-26.md`

The prototype must prove the local persistent-trader spine only; it is not a polished product, broad replay, public website or new research-design exercise.

## Locks

- paid provider calls: `PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- validation/holdout: locked
- shadow: locked
- broker/account: locked
- real money: locked

Offline/no-network testing is preferred. Any real DeepSeek API call requires current executable authority before execution.

# PROJECT_BRAIN_RUNTIME_BRIEF

As of: `2026-08-25`

Purpose: keep each substantive project reply grounded in current `main` without forcing every new project brain to ingest obsolete history.

## Mandatory refresh

Before any substantive answer about current state, architecture, model, tools, experiments, workers or next work:

1. refresh GitHub `main` HEAD;
2. read `PROJECT_DIRECTION.md`;
3. read `CURRENT_STATE.md`;
4. read only the specific current authority/evidence needed for the question;
5. for spend/execution, additionally refresh paid authorization, ledger/evidence and exact executable-slot authority;
6. never infer current project facts from chat history or obsolete documents.

## Current headline

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

`CURRENT_WORK_PACKAGE = JIANGHE_PERSISTENT_DEEPSEEK_TRADER_FOUNDATION_V0_1`

`DEEPSEEK_HARNESS = CANDIDATE_FOR_PROJECT_ADMISSION`

`TOOL_DECISION = ADD_TOOL__VERIFY_DEEPSEEK_HARNESS`

## Product direction

Build one persistent, auditable, single-purpose futures trader that:

- starts from Jianghe source-grounded experience;
- preserves persistent working memory and journal across calls/restarts;
- retrieves relevant Jianghe knowledge instead of rereading an unbounded corpus every call;
- uses causal K-line data/charts and project-owned tools;
- may generate and refine new trading hypotheses from accumulated experience;
- may not rewrite Jianghe source truth or self-promote an unvalidated hypothesis;
- only promotes experience-derived policy after counterexample search and independent validation;
- keeps hard risk, broker/account truth, order lifecycle and safety deterministic.

Full binding direction:

`PROJECT_DIRECTION.md`

## Current exact next work

1. finish DeepSeek exact-enum guard;
2. finish no-4H-exact-volume-reconciliation guard;
3. verify a pinned DeepSeek Harness version/commit for exact selected model + vision + persistence + project-owned memory/tool/audit integration;
4. build the smallest persistent-trader prototype;
5. run a small chronological lifecycle replay to debug memory/runtime behavior;
6. only then design broad historical replay and experience-learning validation.

Do not run mass stateless K-line API calls first.

Do not build a polished generic website first.

Do not reopen MiniMax/Kimi model selection.

## Data foundation

Accepted historical corpus exists and is ready for later chronological replay:

`docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`

- 2024-01-01..2025-12-31
- cu/al/ni/au/ag/rb
- 32,980 partitions
- 15,280,452 normalized 1-minute rows

## Current locks

- `PAID_CALLS = PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- validation/holdout = locked
- shadow = locked
- broker/account = locked
- real money = locked

No current implementation step authorizes real trading.

## Active-context hygiene

Fresh takeover should stay small. Obsolete plans, provider-selection history and superseded handoff text must not remain in the active takeover path merely for historical preservation. Git history is the historical record.

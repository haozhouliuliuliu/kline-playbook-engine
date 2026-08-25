# CURRENT_STATE

As of: `2026-08-25`

This file contains current facts only. Obsolete plans belong in Git history, not in active takeover context.

## Current mission

Canonical direction:

`PROJECT_DIRECTION.md`

Target:

`A PERSISTENT, AUDITABLE, JIANGHE-TRAINED, EVIDENCE-IMPROVING DEEPSEEK FUTURES TRADER`

The project is building one persistent DeepSeek-based futures trader. It begins from Jianghe's documented experience and may later improve beyond the initial Jianghe-only baseline through governed memory, hypothesis generation, falsification and independent validation.

## Model

- sole active model source: DeepSeek
- current selected model line: `deepseek-v4-flash-vision-exp`
- MiniMax: excluded from the Jianghe model candidate set
- Kimi: excluded from the Jianghe model candidate set
- no MiniMax/Kimi reserve, fallback or maintenance budget
- no generic multi-provider runtime is required

Binding model decision:

`docs/reviews/JIANGHE_DEEPSEEK_SOLE_ACTIVE_MODEL_OWNER_DECISION_V0_1.md`

## Jianghe / learning boundary

- Jianghe remains the initial expert/source foundation.
- Jianghe source truth is read-only to the AI.
- DeepSeek may maintain persistent working memory and journal entries.
- DeepSeek may generate new falsifiable trading hypotheses.
- DeepSeek may not promote its own hypotheses directly into active trading policy.
- New experience-derived policy must pass counterexample search, development evidence and independent validation before promotion.
- PnL is not equivalent to reasoning correctness.
- Source truth, DeepSeek hypotheses and project-validated extensions must remain separately labeled.

Detailed binding direction:

`PROJECT_DIRECTION.md`

## Current architecture

Core split remains:

`Market Data -> Rolling Market State -> Observation -> DeepSeek Jianghe Trader -> constrained TradeIntent -> deterministic RiskGate -> OMS/Execution -> Reconciliation/Safety/Ledger`

AI owns market interpretation and proposed discretionary intent.

Deterministic project systems own hard risk, broker/account truth, order lifecycle, reconciliation and safety.

Current active observation stack:

`4H / 1H / 15m / 5m`

4H current role:

`BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`

Known DeepSeek guards that must remain:

- `STRICT_OUTPUT_ENUM_ENFORCEMENT`
- `NO_4H_EXACT_VOLUME_RECONCILIATION`

## Historical data foundation

Accepted canonical historical corpus:

- source scope: TqSdk historical concrete-contract 1-minute data
- coverage: `2024-01-01..2025-12-31`
- products: `cu, al, ni, au, ag, rb`
- partitions: `32,980`
- contracts: `212`
- normalized rows: `15,280,452`
- corpus identity: `1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8`

Authority:

`docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`

This corpus is intended to become the chronological replay environment after the persistent trader identity is stable. Do not turn it into a mass of stateless independent prompt calls.

## Completed selection

Provider/model selection is closed for the current direction.

Operational consequence:

`DEEPSEEK_ONLY`

Do not reopen or repeat provider selection without a new explicit Owner decision.

## Current work package

`CURRENT_WORK_PACKAGE = JIANGHE_PERSISTENT_DEEPSEEK_TRADER_FOUNDATION_V0_1`

Exact next sequence:

1. finish the two narrow DeepSeek mechanical guards;
2. evaluate a pinned DeepSeek Harness version/commit against exact model + vision + persistence + project-owned memory/tool/audit requirements;
3. if Harness passes, adopt it only as the runtime shell; if it fails, use the thinnest project-owned equivalent without changing product direction;
4. build the smallest persistent trader prototype proving exact DeepSeek model path, chart/vision input, persistent working memory, Jianghe retrieval, K-line tools, structured journal/hypothesis memory and complete audit;
5. run a small chronological lifecycle replay to debug memory and runtime semantics;
6. only after that trader identity is stable, design broader historical replay and governed experience-learning research.

## DeepSeek Harness status

`DEEPSEEK_HARNESS = CANDIDATE_FOR_PROJECT_ADMISSION`

Tool decision for the new work package:

`ADD_TOOL__VERIFY_DEEPSEEK_HARNESS`

Do not call Harness adopted until a pinned build passes project-specific verification.

Core trading knowledge, memory schema, evidence and decision semantics remain project-owned and portable even if Harness is used.

## Current execution / research locks

- paid provider calls: `PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- protected future/outcome research access: locked unless a new protocol authorizes it
- validation/holdout: locked
- shadow: locked
- broker/account: locked
- real money: locked

No current step requires a paid model call merely to implement this direction.

## Current accounting

Historical paid-research accounting after the completed provider round:

`PROJECT_ACCOUNTED_CNY = 20.9075330`

Historical hard cap:

`100.00 CNY`

This is a factual record, not new spend authorization.

## Immediate repository-maintenance requirement

The active takeover surface is too large and contains obsolete provider-selection/process material.

After this direction is safely merged, clean the active tree so a new project brain can take over from a small current set of files.

Repository cleanup must:

- keep current truth, accepted source evidence and necessary runtime/code;
- remove obsolete active handoff/planning documents rather than stacking new corrections on top;
- remove MiniMax/Kimi runtime adapters/workflows/tests that no longer serve current DeepSeek-only operation;
- remove cross-project/tool/process material from the fresh-conversation takeover path when it is not current project authority;
- preserve recoverability through Git history instead of keeping obsolete text in active context.

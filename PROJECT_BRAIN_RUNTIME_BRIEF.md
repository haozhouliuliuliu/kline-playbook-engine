# PROJECT_BRAIN_RUNTIME_BRIEF

As of: `2026-08-26`

## Mandatory refresh

Before substantive project work:

1. refresh GitHub `main` HEAD;
2. read `PROJECT_DIRECTION.md`;
3. read `CURRENT_STATE.md`;
4. read only the current task authority/evidence needed;
5. for spend/execution, additionally refresh paid authorization, ledger/evidence and exact executable-slot authority;
6. never infer current project facts from chat history or deleted/obsolete material.

## Current headline

`PRODUCT = JIANGHE_PERSISTENT_DEEPSEEK_TRADER`

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

`MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1 = COMPLETE`

`PROTOTYPE_12_OBJECTIVE_AUTOMATED_GATE = PASS`

`NATIVE_WINDOWS_PROJECT_ACCEPTANCE_CI = PASS`

`LOCAL_WORKSTATION_ACCEPTANCE = PASS`

`CURRENT_WORK_PACKAGE = NONE__AWAITING_EXPLICIT_NEXT_WORK_PACKAGE`

`DEEPSEEK_HARNESS = ADOPTED_FOR_LOCAL_PROTOTYPE_RUNTIME_SHELL`

`DEPLOYMENT = LOCAL_WORKSTATION_FIRST`

`TOOL_DECISION = USE_EXISTING__PINNED_DEEPSEEK_HARNESS`

## Harness authority

Use only:

- Harness version `0.1.1-rc.2`
- upstream commit `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project fail-closed patch from `integrations/deepseek-harness/`
- retry policy `mode: normal`, `maxRetries: 0`

Harness admission was established on PR #41. Prototype PR #42 re-proved the project-required Harness properties on final head `bb38a103457b9075f7f9a7d74715a054a8d166d4`:

- Repository CI run `32891952828` = success; 437 tests, 12 skipped, 0 failed.
- DeepSeek Harness Dynamic Admission run `32891952918` = success.

PR #42 merged to main as `361649965685282af0f04b854f14195c9ce66e65`.

Windows repair PR #43 merged as `22c88215ea90ff618bd8457fceabf2deb13e2226`; native Windows acceptance CI run `32896485036` passed on final head `98b707f7efbf65b4648d2f5763d1c825517dbb74`.

Formal evidence:

- `docs/evidence/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_AUTOMATED_GATE_EVIDENCE_2026-08-26.md`
- `docs/evidence/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_WINDOWS_LOCAL_ACCEPTANCE_REPAIR_2026-08-26.md`
- `docs/evidence/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_LOCAL_WORKSTATION_ACCEPTANCE_2026-08-26.md`

Harness is a local runtime/workbench shell. Core trader logic, memory schema, Jianghe knowledge, evidence semantics and deterministic risk/safety remain project-owned and portable.

## Closed prototype proof

The Owner-workstation final acceptance on repaired `main` passed with:

- Python `3.11.9`;
- Node `22.19.0`;
- pnpm `11.7.0`;
- offline core probe exit code `0`;
- `provider_call_made = false`;
- all thirteen offline summary checks true;
- summary SHA-256 `25CEAFBF6B38A504B7DF3FCD871BFB18DBCCB322DCB88828C7FBA391614B66A9`;
- local DB/charts/manifests present;
- Harness Gates A-D all pass;
- real DeepSeek/provider calls `0`;
- no tracked project files modified by local acceptance.

## Exact next work

There is no active implementation/research work package.

`NEXT_TASK = STOP__AWAIT_EXPLICIT_NEXT_WORK_PACKAGE`

Do not start chronological replay, broad replay, learning, validation/holdout, shadow, broker/account or real-money work from the completed prototype package.

A later Owner-approved/explicitly defined work package may open the next engineering or research phase. Until then, preserve the completed prototype state and current locks.

## Current locks

- `PAID_CALLS = PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- validation/holdout = locked
- shadow = locked
- broker/account = locked
- real money = locked

No current authority authorizes a provider call or real trading.

## Handoff hygiene

The dated prototype handoff was only valid while the prototype package remained open. Completion requires its deletion; current conversations should use this runtime brief, `PROJECT_DIRECTION.md`, `CURRENT_STATE.md`, and formal evidence instead of any deleted handoff snapshot.

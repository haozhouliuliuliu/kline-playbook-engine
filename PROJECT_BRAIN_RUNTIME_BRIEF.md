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

`CURRENT_WORK_PACKAGE = MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1`

`PROTOTYPE_12_OBJECTIVE_AUTOMATED_GATE = PASS`

`LOCAL_WORKSTATION_ACCEPTANCE = PENDING`

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

Formal automated gate evidence:

`docs/evidence/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_AUTOMATED_GATE_EVIDENCE_2026-08-26.md`

Harness is a local runtime/workbench shell. Do not interpret adoption as permission to move trader memory/data to cloud or build a public service. Core trader logic, memory schema, Jianghe knowledge, evidence semantics and deterministic risk/safety remain project-owned.

## Exact next work

Read:

`docs/reviews/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_HANDOFF_2026-08-26.md`

The prototype code is already merged. Do not rebuild it from scratch.

The only remaining work-package step is Owner-workstation offline acceptance:

1. pull current `main` on the Owner workstation;
2. run `python tools/run_persistent_deepseek_trader_offline_probe.py` using a local project-owned state directory;
3. make no DeepSeek/provider call and do not use an API key;
4. return `offline-probe-summary.json` and terminal evidence;
5. verify all summary `checks` are `true` and `provider_call_made` is `false`;
6. only then finalize authority, delete the dated handoff, and stop.

Do not start chronological replay/learning, broad replay, validation, shadow, broker/account or real-money work in this package.

## Current locks

- `PAID_CALLS = PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- validation/holdout = locked
- shadow = locked
- broker/account = locked
- real money = locked

No current handoff step authorizes a provider call or real trading.

## Handoff hygiene

The dated prototype handoff remains the current task handoff while local workstation acceptance is pending. When local acceptance passes and the work package is formally closed, delete that file instead of appending a superseding history section.

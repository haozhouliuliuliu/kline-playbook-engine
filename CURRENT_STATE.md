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

Harness admission was established by PR #41 and remains binding. The prototype implementation re-proved the required Harness properties on PR #42 final head `bb38a103457b9075f7f9a7d74715a054a8d166d4`:

- Repository CI run `32891952828` = `success`; 437 tests, 12 skipped, 0 failed.
- DeepSeek Harness Dynamic Admission run `32891952918` = `success`.
- fail-closed vision transport/no hidden stale-file second request = pass.
- exact project provider/model route plus project memory/tool/audit integration = pass using no-network mock transport.
- durable Harness SQLite persistence contract = pass.
- DeepSeek image serialization/dynamic config regression = pass.

## Minimal persistent trader prototype

PR #42 merged to `main` as:

`361649965685282af0f04b854f14195c9ce66e65`

Implemented project-owned prototype spine:

- local SQLite `DS_WORKING_MEMORY`, `DS_JOURNAL`, `DS_HYPOTHESIS_MEMORY` and append-only audit;
- process-style close/reopen working-memory persistence;
- bounded attributable read-only Jianghe canon retrieval;
- exact model/Harness runtime contract with provider execution locked;
- causal `4H / 1H / 15m / 5m` observation + deterministic PNG chart context;
- project-owned audited tool registry;
- strict response normalization and existing mechanical guards;
- prompt/tool identity binding to `JiangheAITraderIdentity`;
- Harness-independent complete portable export without bounded-query truncation;
- local no-provider-call acceptance probe at `tools/run_persistent_deepseek_trader_offline_probe.py`.

Formal automated evidence:

`docs/evidence/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_AUTOMATED_GATE_EVIDENCE_2026-08-26.md`

`PROTOTYPE_12_OBJECTIVE_AUTOMATED_GATE = PASS`

## Windows local-acceptance repair

The Owner's first Windows workstation attempt proved all four local Harness gates with zero real provider calls, but exposed a project-side Windows path-separator defect in Jianghe canon retrieval. The offline probe failed before producing its local artifacts.

PR #43 repaired the cross-platform path representation without changing Jianghe/trading semantics and merged to `main` as:

`22c88215ea90ff618bd8457fceabf2deb13e2226`

Final PR #43 head:

`98b707f7efbf65b4648d2f5763d1c825517dbb74`

Repository CI run `32896485036` passed on that final head:

- Linux full repository `test` = success;
- native Windows `windows-prototype` = success;
- Windows Jianghe path regression = success;
- Windows prototype acceptance regression = success;
- native Windows offline CLI probe = success with `DEEPSEEK_API_KEY=''`, `provider_call_made == false`, and every probe `checks` value true.

Repair evidence:

`docs/evidence/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_WINDOWS_LOCAL_ACCEPTANCE_REPAIR_2026-08-26.md`

A separate non-acceptance Windows cleanup finding remains recorded there: a deliberately rejected mismatched-trader database constructor can retain its SQLite handle until Python cleanup/GC, causing same-process immediate temporary-directory deletion to receive `WinError 32`. The identity mismatch itself remains fail-closed. This does not redefine or weaken any of the twelve prototype objectives.

`NATIVE_WINDOWS_PROJECT_ACCEPTANCE_CI = PASS`

`LOCAL_WORKSTATION_ACCEPTANCE = PENDING`

The work package is therefore not closed yet. The dated handoff remains active until the repaired current `main` passes the Owner workstation offline acceptance rerun and its summary is reviewed.

## Historical data foundation

Accepted canonical corpus:

- 2024-01-01..2025-12-31
- cu/al/ni/au/ag/rb
- 32,980 partitions
- 212 contracts
- 15,280,452 normalized 1-minute rows
- corpus identity `1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8`

Authority: `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`

Do not start broad replay until the persistent trader prototype work package is formally closed and a next work package is defined.

## Current work package

`CURRENT_WORK_PACKAGE = MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1`

Current task handoff:

`docs/reviews/MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_HANDOFF_2026-08-26.md`

Exact next task:

1. Owner workstation pulls repaired current `main`.
2. Use Python 3.11 and a fresh local project-owned state directory.
3. Force the acceptance process `DEEPSEEK_API_KEY` empty without exposing any prior value.
4. Run `python tools/run_persistent_deepseek_trader_offline_probe.py --state-dir <fresh-local-state-dir>`.
5. Verify exit code zero, `provider_call_made == false`, every `checks` value true, and the local DB/summary/four PNG charts/manifests exist.
6. Return `offline-probe-summary.json` plus terminal/artifact evidence for project review.
7. If local acceptance passes, finalize authority, delete the dated handoff, and stop before replay/learning.

The existing local Harness installation may be reused only if its HEAD is still the pinned commit and the project patch remains applied. No real DeepSeek call is part of this acceptance.

## Locks

- paid provider calls: `PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- validation/holdout: locked
- shadow: locked
- broker/account: locked
- real money: locked

No current authority permits a real DeepSeek provider call. Local acceptance is explicitly offline/no-provider-call.

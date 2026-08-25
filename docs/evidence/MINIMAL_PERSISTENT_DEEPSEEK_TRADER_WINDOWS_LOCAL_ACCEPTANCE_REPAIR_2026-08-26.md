# MINIMAL_PERSISTENT_DEEPSEEK_TRADER_WINDOWS_LOCAL_ACCEPTANCE_REPAIR_2026-08-26

Status: `CURRENT_WORK_PACKAGE_EVIDENCE`

## Scope

This evidence records the first Owner-workstation Windows acceptance attempt for `MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1`, the project defect it exposed, and the subsequent project repair and native-Windows revalidation.

It does **not** declare Owner-workstation acceptance complete. The Owner workstation must rerun the repaired `main` before `LOCAL_WORKSTATION_ACCEPTANCE` may become `PASS`.

No real DeepSeek/provider call was authorized or made in this repair sequence. Replay/learning remained out of scope.

## Owner-workstation first attempt

The Owner supplied a local Windows acceptance report after running the prescribed offline deployment/acceptance procedure.

Machine/runtime facts reported:

- Windows 11 x64;
- Python `3.11.9` with `tzdata==2026.3`;
- Node `22.19.0`;
- pnpm `11.7.0`;
- project main at `037693ea296cf51b77a9c9ce49e72102cb98d936`;
- pinned Harness at `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`;
- project fail-closed Harness patch applied;
- `DEEPSEEK_API_KEY` forced empty;
- real provider calls = `0`.

Owner-workstation Harness local gates all passed:

- fail-closed stale-file/hidden-second-request gate = pass;
- exact project provider/model route plus no-network project memory/tool/audit gate = pass;
- targeted durable Harness SQLite persistence contract = pass;
- DeepSeek serialization/dynamic-config regression = pass.

The project offline core probe failed before creating its state artifacts with:

`ValueError: JIANGHE_CANON retrieval is restricted to docs/research/jianghe/`

## Root cause

`default_jianghe_canon_paths()` legitimately produced native Windows repo-relative paths containing `\` separators. `JiangheCanonRetriever` converted the allowlist entry through `Path` and then compared its string form against the forward-slash prefix `docs/research/jianghe/`.

On Windows, the native string representation therefore failed the allowlist prefix check even though the file was inside the governed Jianghe subtree.

This was a cross-platform representation defect. It did not change Jianghe source semantics, retrieval bounds, model choice, prompt semantics, trading semantics or the read-only knowledge boundary.

## Repair

PR #43: `fix: unblock Windows local prototype acceptance`

Final PR head:

`98b707f7efbf65b4648d2f5763d1c825517dbb74`

Merged to `main` as:

`22c88215ea90ff618bd8457fceabf2deb13e2226`

The repair:

- canonicalizes both Windows and POSIX separator inputs to one forward-slash repo-relative representation before allowlist checks and identities;
- preserves fail-closed rejection of Windows drive paths, UNC paths, POSIX absolute paths and traversal;
- bumps retriever identity version to `KPE_JIANGHE_CANON_RETRIEVER_V0_2` because the canonical path representation is outcome-affecting identity material;
- adds host-independent regression tests that simulate Windows backslash input even when Linux CI is running;
- adds a native `windows-latest` prototype acceptance CI lane using Python `3.11` and `tzdata==2026.3`.

## Native Windows revalidation

Repository CI run:

`32896485036`

Final head:

`98b707f7efbf65b4648d2f5763d1c825517dbb74`

Results:

- Linux full repository `test` job = `success`;
- native Windows `windows-prototype` job = `success`;
- Windows cross-platform Jianghe retrieval regressions = `success`;
- Windows prototype acceptance regression tests = `success`;
- native Windows `tools/run_persistent_deepseek_trader_offline_probe.py` = `success`;
- the Windows CLI probe ran with `DEEPSEEK_API_KEY=''` and its workflow verifies `provider_call_made == false` plus every summary `checks` value equals `true`.

This establishes that the original Owner-workstation probe blocker is repaired on native Windows without a provider call.

## Separate Windows cleanup finding

During the first broad native-Windows test attempt, one non-acceptance test exposed a separate resource-lifetime issue:

`PersistentDeepSeekTraderPrototypeTests.test_database_rejects_a_different_trader_identity`

The store correctly rejects opening an existing database with a different trader identity, but the constructor-failure path can leave the SQLite connection alive until Python cleanup/GC. On Windows, a test that immediately deletes the same temporary directory in the same process can therefore receive `WinError 32`.

This finding is **not** treated as evidence that a mismatched identity is accepted; the identity check remains fail-closed. It also did not block the native Windows offline acceptance probe, which passed after the path repair.

Classification for the current work package:

`KNOWN_LIMITATION = WINDOWS_SQLITE_CONSTRUCTOR_FAILURE_RESOURCE_LIFETIME`

It is not a reason to weaken or remove the trader-identity fail-closed check. It remains a normal engineering cleanup item and must not be used to redefine the twelve prototype objectives.

## Current acceptance state

`PROTOTYPE_12_OBJECTIVE_AUTOMATED_GATE = PASS`

`NATIVE_WINDOWS_PROJECT_ACCEPTANCE_CI = PASS`

`LOCAL_WORKSTATION_ACCEPTANCE = PENDING`

The only remaining work-package action is for the Owner workstation to pull repaired current `main` and rerun the no-provider-call local acceptance probe (and return its summary/evidence). Only after that succeeds may authority be finalized and the dated handoff deleted.

## Locked boundaries

- paid provider calls remain paused;
- `NEXT_EXPLICIT_PAID_SLOT = NONE`;
- no real DeepSeek API call;
- no replay/learning;
- validation/holdout remains locked;
- shadow remains locked;
- broker/account remains locked;
- real money remains locked.

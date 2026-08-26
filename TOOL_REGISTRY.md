# TOOL_REGISTRY

Status: `CURRENT`

Scope: `KLINE_PLAYBOOK_ENGINE_PROJECT_ONLY`

This registry records material external tools, frameworks, provider/runtime surfaces and storage capabilities that are relevant to the current `kline-playbook-engine` project.

It is **not** a cross-project software catalog. Unrelated global candidates do not belong here.

Actual runtime/config/lockfiles and task-specific Owner authority remain authoritative for exact enabled versions and permissions. Presence in this registry never grants provider spend, broker/account access, paper execution or real-money authority.

## Status semantics

Use only:

- `CANDIDATE` — plausible for a project role but not yet verified sufficiently for that role;
- `VERIFIED` — actually tested against project requirements, but not necessarily selected as the active project path;
- `ADOPTED` — formally selected for the stated project role and scope.

A status is always scoped to the stated role. `ADOPTED` for one narrow role does not imply blanket authorization for another role.

## 1. DeepSeek provider / active model source

### DeepSeek provider API

`STATUS = ADOPTED`

Role:

`SOLE_ACTIVE_PROVIDER_SOURCE_FOR_JIANGHE_TRADING_MODEL`

Current model:

`deepseek-v4-flash-vision-exp`

Authority:

- `PROJECT_DIRECTION.md`
- `PROJECT_BRAIN_RUNTIME_BRIEF.md`
- `CURRENT_STATE.md`

Important boundary:

Provider/model adoption does **not** authorize paid calls. Current executable provider permissions are governed separately by the exact work-package Owner decision and machine-readable spend authority.

Current paid state:

`REAL_DEEPSEEK_PROVIDER_CALLS = PAUSED`

`NEXT_EXPLICIT_PAID_SLOT = THREE_CALL_PROVIDER_SMOKE__PENDING_OWNER_PAYMENT_CONFIRMATION`

## 2. DeepSeek Harness

`STATUS = ADOPTED`

Role:

`LOCAL_PROTOTYPE_RUNTIME_SHELL_AND_GOVERNED_PROVIDER_BRIDGE`

Pinned identity:

- version: `0.1.1-rc.2`
- commit: `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project fail-closed transport patch: `integrations/deepseek-harness/`
- general retry policy: `maxRetries = 0`

Authority/evidence:

- `PROJECT_DIRECTION.md`
- `ARCHITECTURE_BASELINE.md`
- `PROJECT_BRAIN_RUNTIME_BRIEF.md`
- repository Harness admission workflows/tests

Adopted scope:

- localhost/local-workstation runtime shell;
- governed DeepSeek provider request bridge;
- session/tool/UI hosting around project-owned trader semantics.

Not adopted as owner of:

- trader cognition semantics;
- project memory truth;
- data eligibility;
- risk;
- broker/account truth;
- OMS/reconciliation;
- governance.

Revalidation trigger:

Any Harness version/commit change, provider protocol change, retry semantics change, image/request serialization change, or failure of project admission tests.

## 3. TqSdk

`STATUS = ADOPTED`

Role:

`HISTORICAL_CONCRETE_CONTRACT_1M_RESEARCH_DATA_ACQUISITION_ONLY`

Verified runtime:

`tqsdk = 3.10.1`

Authority/evidence:

- `docs/evidence/SOURCE_AND_SCOPE_OWNER_APPROVAL.md`
- `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`
- canonical corpus/source identity evidence

Adopted scope:

- historical concrete-contract 1-minute research data acquisition for the accepted canonical corpus.

Explicitly not implied:

- broker connectivity;
- live/shadow/paper execution;
- order submission;
- paid renewal/continuity;
- pseudo MAIN/CONTINUOUS symbol use.

Current paid continuity:

`PAID_CONTINUITY_AUTHORIZED = NO`

Revalidation trigger:

Runtime/API/entitlement behavior changes materially, source identity changes, or a different TqSdk runtime is proposed.

## 4. PyArrow / Parquet

`STATUS = ADOPTED`

Role:

`CANONICAL_NORMALIZED_BAR_STORAGE_AND_REPLAY_READ_PATH`

Authority/evidence:

- `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`
- canonical dataset package/schema evidence
- Owner-workstation exact-slice mock dry-run evidence

Accepted corpus facts include:

- storage: partitioned Parquet;
- canonical normalized schema with Decimal OHLC and Asia/Shanghai timezone;
- logical write/read equality gate;
- 32,980 canonical Parquet partitions in the accepted corpus.

Exact runtime/version compatibility for a given execution remains governed by the code/environment and the evidence for that execution. Do not infer blanket compatibility across untested PyArrow versions.

Revalidation trigger:

Schema/storage version change, material PyArrow runtime change, or replay-read compatibility failure.

## 5. SQLite / Python stdlib sqlite3

`STATUS = ADOPTED`

Roles:

- rebuildable canonical manifest/catalog indexing where applicable;
- project-owned persistent trader state;
- governed wake ledger / audit-supporting local state.

Authority/evidence:

- `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`
- current replay runtime/code/tests;
- `docs/evidence/JIANGHE_REPLAY_V0_1_PREEXECUTION_EVIDENCE_2026-08-26.md`

Truth boundary:

SQLite is a local deterministic persistence/index mechanism. It does not replace immutable canonical evidence, broker/paper account truth, or GitHub authority.

Revalidation trigger:

Persistent-state schema change, ledger schema change, restart/reconciliation failure, or migration to another storage engine.

## 6. faster-whisper

`STATUS = ADOPTED`

Role:

`LOCAL_ASR_FOR_SOURCE_EVIDENCE_TRANSPORT_WHEN_NATIVE_SUBTITLE_UNAVAILABLE`

Verified identity:

- package: `faster-whisper 1.2.1`
- model: `Systran/faster-whisper-small`
- execution profile: CPU / `int8`
- verification evidence commit: `1027ea40d65ff7d86e9f65ea8bd38654fd654377`

Adopted scope:

- local, free ASR transport for source review only when native subtitles are unavailable;
- preserve timestamped transcript and low-confidence disclosure;
- ASR output is evidence transport, not semantic authority.

Revalidation trigger:

Model identity, package/runtime version, CPU/int8 configuration, timestamp-validation rule, or source-review workflow changes materially.

## 7. DuckDB

`STATUS = CANDIDATE`

Role:

`OPTIONAL_RESEARCH_QUERY_ENGINE`

Activation:

`DEFERRED_UNTIL_A_REAL_CURRENT_QUERY_CAPABILITY_GAP_IS_DEMONSTRATED`

It is not currently installed/adopted as required project infrastructure.

Revalidation trigger:

A concrete research-query workload demonstrates that current Parquet/Python/SQLite paths are materially insufficient.

## 8. GitHub Actions repository verification

`STATUS = ADOPTED`

Role:

`REPOSITORY_CI_AND_DEEPSEEK_HARNESS_DYNAMIC_ADMISSION`

Current workflows include:

- `.github/workflows/ci.yml`
- `.github/workflows/deepseek-harness-admission.yml`
- `.github/workflows/deepseek-harness-dynamic-admission.yml`

These workflows are verification infrastructure only. A green workflow does not itself grant paid/provider, broker/account or real-money authority.

Revalidation trigger:

Workflow semantics, runner platform, dependency/runtime pin, or Harness admission path changes materially.

## 9. Local worker/helper surfaces

WorkBuddy and local VS Code/worker helpers are not project authority by themselves.

`AGENTS.md` governs worker/worktree/integration-lane rules.

A worker report can provide evidence for integration review, but accepted project facts, tool adoption and permissions must be written into current GitHub authority/evidence.

## Registry maintenance rule

When a material tool/framework/provider capability is proposed, verified, adopted, replaced or retired for this project:

1. record its project role and scope here when it remains relevant to active/future project operation;
2. keep exact pins and execution permissions in their authoritative config/decision/evidence files;
3. never treat this registry as spend or external-action authorization;
4. update `00_READ_FIRST.md` only when the registry's role in fresh takeover changes;
5. remove obsolete active entries rather than accumulating tombstone narratives; Git history preserves prior states.

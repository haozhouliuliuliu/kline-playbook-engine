# TOOL_REGISTRY

Status: `CURRENT`

Scope: `KLINE_PLAYBOOK_ENGINE_PROJECT_ONLY`

This registry is the canonical owner for material project tools/frameworks/providers, their scoped `CANDIDATE / VERIFIED / ADOPTED` status, adopted pins, credential-location seams and revalidation triggers.

It does **not** own current work-package state, current locks, current paid-slot state or `NEXT_TASK`. Those live only in `CURRENT_STATE.md`.

Presence of a credential or tool on the Owner workstation never grants project adoption or execution authority.

## Status semantics

- `CANDIDATE` — plausible for a project role, not yet sufficiently verified;
- `VERIFIED` — tested against project requirements for the stated role;
- `ADOPTED` — formally selected for the stated project role/scope.

Status is role-scoped. `ADOPTED` for one role never implies blanket permission for another role.

## 0. Owner workstation credential convention

`LOCAL_PROVIDER_SECRET_STORE = WINDOWS_CURRENT_USER_ENVIRONMENT_VARIABLES`

Provider secrets used from the Owner workstation are expected to be stored as Windows **user environment variables**, not repository files.

Known user-level variable names observed on the Owner workstation include:

- `ANTHROPIC_API_KEY`;
- `DASHSCOPE_API_KEY`;
- `DEEPSEEK_API_KEY`;
- `GEMINI_API_KEY`;
- `SILICONFLOW_API_KEY`.

These names record only where secrets are kept. Their presence does **not** mean those providers are adopted by this project.

Secret handling rules:

- never commit secret values;
- never print/echo/log/serialize secret values;
- never ask the Owner to paste a secret into project authority;
- runtime availability checks may report only non-secret states such as `SET / UNSET`;
- provider code loads the required value only at execution time;
- a missing variable is an execution blocker, not a reason to move secrets into Git or chat.

## 1. DeepSeek provider / active model source

`STATUS = ADOPTED`

Role:

`SOLE_ACTIVE_PROVIDER_SOURCE_FOR_JIANGHE_TRADING_MODEL`

Selected model line:

`deepseek-v4-flash-vision-exp`

Credential seam:

`CREDENTIAL_ENV = DEEPSEEK_API_KEY`

`CREDENTIAL_LOCATION = WINDOWS_CURRENT_USER_ENVIRONMENT_VARIABLES`

Provider/model adoption does **not** authorize paid calls. Exact current execution permission is governed by `CURRENT_STATE.md` plus the applicable exact Owner/machine execution authority.

Revalidation trigger:

Provider protocol/model-generation/authentication/request-response behavior changes materially, or the governed provider path fails.

## 2. DeepSeek Harness

`STATUS = ADOPTED`

Role:

`LOCAL_PROTOTYPE_RUNTIME_SHELL_AND_GOVERNED_PROVIDER_BRIDGE`

Pinned identity:

- version: `0.1.1-rc.2`;
- commit: `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`;
- project fail-closed transport patch: `integrations/deepseek-harness/`;
- general retry policy: `maxRetries = 0`.

Adopted scope:

- localhost/local-workstation runtime shell;
- governed DeepSeek provider request bridge;
- session/tool/UI hosting around project-owned trader semantics.

Not adopted as owner of trader cognition, memory truth, data eligibility, risk, OMS/reconciliation, broker/account truth or governance.

Revalidation trigger:

Harness version/commit, provider protocol, retry semantics, image/request serialization or admission behavior changes materially.

## 3. TqSdk

`STATUS = ADOPTED`

Role:

`HISTORICAL_CONCRETE_CONTRACT_1M_RESEARCH_DATA_ACQUISITION_ONLY`

Verified runtime:

`tqsdk = 3.10.1`

Authority/evidence:

- `docs/evidence/SOURCE_AND_SCOPE_OWNER_APPROVAL.md`;
- `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`.

Adopted scope is historical concrete-contract 1-minute research data acquisition for the accepted canonical corpus.

Adoption does not imply broker connectivity, live/shadow/paper execution, order submission, paid continuity or pseudo MAIN/CONTINUOUS symbol use.

Revalidation trigger:

Runtime/API/entitlement behavior or source identity changes materially, or another TqSdk runtime is proposed.

## 4. PyArrow / Parquet

`STATUS = ADOPTED`

Role:

`CANONICAL_NORMALIZED_BAR_STORAGE_AND_REPLAY_READ_PATH`

Authority/evidence:

- `docs/evidence/CANONICAL_DATASET_ACCEPTANCE.md`;
- canonical dataset/schema evidence;
- accepted replay evidence.

Revalidation trigger:

Schema/storage version change, material PyArrow runtime change or replay-read compatibility failure.

## 5. SQLite / Python stdlib sqlite3

`STATUS = ADOPTED`

Roles:

- rebuildable canonical manifest/catalog indexing where applicable;
- project-owned persistent trader state;
- governed wake ledger / audit-supporting local state.

SQLite is a local deterministic persistence/index mechanism. It does not replace immutable canonical evidence, broker/paper account truth or GitHub authority.

Revalidation trigger:

Persistent-state/ledger schema change, restart/reconciliation failure or storage-engine migration.

## 6. faster-whisper

`STATUS = ADOPTED`

Role:

`LOCAL_ASR_FOR_SOURCE_EVIDENCE_TRANSPORT_WHEN_NATIVE_SUBTITLE_UNAVAILABLE`

Verified identity:

- package: `faster-whisper 1.2.1`;
- model: `Systran/faster-whisper-small`;
- execution profile: CPU / `int8`;
- verification evidence commit: `1027ea40d65ff7d86e9f65ea8bd38654fd654377`.

ASR output is evidence transport, not semantic authority.

Revalidation trigger:

Model/package/runtime/configuration or timestamp-validation workflow changes materially.

## 7. DuckDB

`STATUS = CANDIDATE`

Role:

`OPTIONAL_RESEARCH_QUERY_ENGINE`

Activation:

`DEFERRED_UNTIL_A_REAL_CURRENT_QUERY_CAPABILITY_GAP_IS_DEMONSTRATED`

Revalidation trigger:

A concrete workload demonstrates current Parquet/Python/SQLite paths are materially insufficient.

## 8. GitHub Actions repository verification

`STATUS = ADOPTED`

Role:

`REPOSITORY_CI_AND_DEEPSEEK_HARNESS_DYNAMIC_ADMISSION`

Workflow surfaces include:

- `.github/workflows/ci.yml`;
- `.github/workflows/deepseek-harness-admission.yml`;
- `.github/workflows/deepseek-harness-dynamic-admission.yml`.

A green workflow is verification evidence only; it grants no paid/provider/broker/real-money authority.

Revalidation trigger:

Workflow semantics, runner platform, dependency/runtime pin or Harness admission path changes materially.

## 9. VS Code DeepSeek Flash worker

`STATUS = ADOPTED`

Role:

`DEFAULT_LOCAL_IMPLEMENTATION_AND_PARALLEL_WORKER`

Stable worker/model family:

`VS CODE DEEPSEEK FLASH WORKER` (`deepseek-v4-flash` family; no volatile exact
build is hard-coded here unless separately pinned by an exact authority)

Adopted scope:

- ordinary authorized engineering;
- tests, bug fixing and documentation;
- Git/GitHub work;
- local repository/file/runtime inspection;
- local-machine tasks;
- data work;
- bounded parallel implementation on independent scopes.

It may act as the integration lane only when explicitly assigned.

Worker availability grants no project authority, paid permission, provider
permission, broker/account permission or real-money permission.

Revalidation trigger:

material change to VS Code agent behavior, DeepSeek Flash worker family,
local/GitHub permissions, or repository interaction behavior.

## 10. Codex worker

`STATUS = ADOPTED`

Role:

`HIGH_ASSURANCE_CRITICAL_ENGINEERING_AND_REVIEW_WORKER`

Stable worker/model family:

`CODEX WORKER` (no volatile Codex model name is hard-coded here; the exact
model/reasoning choice is selected per task by the project brain, consistent
with the adopted parent contract)

Adopted scope (difficult/high-criticality work where stronger implementation or
independent assurance is materially useful):

- critical architecture;
- difficult correctness problems;
- fragile runtime/infrastructure;
- hard debugging;
- evidence-critical implementation;
- research-semantics-sensitive implementation/review;
- consequential-action safety boundaries;
- major migration/refactor;
- independent factual/adversarial review when stronger assurance is warranted.

Codex is not the default worker for routine engineering.

Worker availability grants no project authority, paid permission, provider
permission, broker/account permission or real-money permission.

Revalidation trigger:

material change to Codex agent behavior, local/GitHub permissions, or repository
interaction behavior.

## 11. Worker surface status rule

Both worker surfaces are implementation/helper capabilities, not
project-management or authority owners.

`AGENTS.md` governs worker routing, worktree/integration procedure and worker-prompt
discipline.

Worker reports are evidence candidates; accepted facts must be written into canonical
GitHub authority/evidence by the integration lane.

## Registry maintenance rule

When a material capability is proposed, verified, adopted, replaced or retired:

1. record only its project role/scope/status/pin/credential seam/revalidation rule here;
2. keep current phase/locks/paid state out of this registry;
3. keep exact spend/execution permission in exact Owner/machine authority;
4. remove obsolete active entries instead of preserving tombstones; Git history keeps history.

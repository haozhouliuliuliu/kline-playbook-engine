# DEEPSEEK_HARNESS_ADMISSION_V0_1

As of: `2026-08-26`

Status: `CANDIDATE_STATIC_QUALIFIED__PROJECT_DYNAMIC_GATES_PENDING`

This review evaluates DeepSeek Harness only as a runtime shell for `JIANGHE_PERSISTENT_DEEPSEEK_TRADER`.

It does not authorize a provider call, paid spend, Validation/Holdout access, Shadow, broker/account access or real-money execution.

## 1. Pinned candidate

Upstream repository:

`deepseek-ai/deepseek-harness`

Pinned commit:

`b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`

Pinned release/package version:

`0.1.1-rc.2`

Pinned toolchain declared by upstream root package:

- Node: `^22.19.0 || >=24.0.0`
- pnpm: `11.7.0`

No floating `master`, `main`, `latest` or unpinned package version is admissible for the project.

## 2. Static admission findings

| Requirement | Current finding | Evidence at pinned commit |
|---|---|---|
| Exact selected model route | PASS_STATIC | `packages/llm/llm-deepseek/README.md`, `packages/llm/llm-deepseek/src/*` advertise `deepseek-v4-flash-vision-exp` on provider route `deepseek-official`. |
| Vision/image input | PASS_STATIC | The exact model advertises `inputModalities: [text, image]`; DeepSeek adapter owns deterministic image request normalization and image limits. |
| Durable trace/audit spine | PASS_STATIC | `packages/core/session/README.md` defines an append-only event-sourced session log; `docs/architecture.md` states model-visible input must be logged/reconstructable. |
| Restart-capable persistence seam | PASS_STATIC | `packages/session/session-persistence-sqlite/README.md` provides opt-in SQLite `SessionPersistence` and restores exact logical `SessionEvent[]`. |
| Project-owned tools/context extension | PASS_STATIC | `docs/architecture.md` exposes `ctx.tools`, `agent.inject()`, `SessionEventMap`, profile patches and out-of-tree plugins. |
| Project-owned non-session memory storage seam | PASS_STATIC | `packages/storage/storage-sqlite/README.md` exposes host-side SQLite domain KV storage that contributes no model prompt by itself. |
| General model-request retry can be disabled | PASS_STATIC_WITH_REQUIRED_CONFIG | `packages/llm/llm/src/retry-policy.ts` defaults to five retries but explicitly accepts normal mode `maxRetries = 0`. Project admission requires zero. |
| No silent image-specific second request | OPEN_BLOCKING_DYNAMIC_GATE | DeepSeek adapter contains Files-API resolution/fallback and stale/missing file-id recovery behavior. This must not create an unlogged second provider request in the project configuration. |
| Project-owned bounded memory survives restart | OPEN_DYNAMIC_GATE | Harness supplies the seams, but the project-specific working-memory/journal/hypothesis implementation has not yet been proven. |
| Project-owned K-line/retrieval tools + audit | OPEN_DYNAMIC_GATE | The tool seam is present, but the project plugin must prove exact registration, execution and durable audit behavior. |
| Portability of core trader logic | OPEN_DYNAMIC_GATE | The persistent trader core must remain project-owned and runnable behind another thin shell if Harness is removed. |

## 3. Mandatory project configuration if Harness is admitted

The DeepSeek route must use the exact model:

`deepseek-v4-flash-vision-exp`

General retry policy must be explicitly frozen to:

```yaml
retryPolicy:
  mode: normal
  maxRetries: 0
```

Omitting `retryPolicy` is forbidden because the pinned Harness default is five eligible retries.

The project must also fail closed if any image-specific Files-API recovery path can issue a second chat-completions request without a durable project-visible retry/attempt record. A hidden second provider request is incompatible with the current audit requirement even if the upstream behavior is intended as recovery.

## 4. Why Harness is still only CANDIDATE

The upstream architecture is a good fit for the project because the model adapter, tool registry, session log, persistence and loop are separable plugins rather than a monolithic agent implementation.

That architectural fit is not enough for adoption. The project must prove its own composition rather than infer correctness from upstream documentation.

`VERIFIED` therefore requires all of the following on the exact pinned commit:

1. focused upstream tests for the exact DeepSeek adapter/model/image path;
2. retry-policy verification proving `maxRetries: 0` resolves to zero retries;
3. SQLite session persistence tests;
4. agent/tool/session focused tests;
5. a project-owned no-network integration probe proving persistent working memory survives process/context restart;
6. a project-owned tool probe proving K-line/retrieval tools are registered through the Harness seam and are audit-visible;
7. a project-owned audit probe proving model/provider/request envelope, tool activity and memory mutation can be reconstructed;
8. a fail-closed resolution of the image stale-file internal resend concern.

The first four items are automated by `.github/workflows/deepseek-harness-admission.yml` without any provider credential or provider API call. Items 5-8 remain project dynamic admission gates after that workflow passes.

## 5. Admission states

Allowed state progression:

`CANDIDATE -> CANDIDATE_STATIC_QUALIFIED__PROJECT_DYNAMIC_GATES_PENDING -> VERIFIED -> ADOPTED`

Rules:

- `CANDIDATE_STATIC_QUALIFIED__PROJECT_DYNAMIC_GATES_PENDING` means the pinned upstream build and seams look technically admissible and focused upstream tests pass; it does not mean the project integration works.
- `VERIFIED` requires the project-owned dynamic probes above.
- `ADOPTED` may be declared only after verification and only as the runtime shell.
- Jianghe canon, memory schema, context-selection policy, trader identity, evidence semantics and deterministic risk/safety logic remain project-owned regardless of runtime shell.

## 6. Current conclusion

`DEEPSEEK_HARNESS = CANDIDATE_STATIC_QUALIFIED__PROJECT_DYNAMIC_GATES_PENDING`

`PINNED_HARNESS_COMMIT = b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`

`PINNED_HARNESS_VERSION = 0.1.1-rc.2`

`PAID_PROVIDER_CALLS_REQUIRED_FOR_THIS_REVIEW = NO`

`TOOL_DECISION = ADD_TOOL__VERIFY_DEEPSEEK_HARNESS`

No current lock changes.
# JIANGHE STAGE-A V0.3 PREFLIGHT FAILURE AUDIT V0.1

Status: `PREFLIGHT_BLOCKED__NO_PAID_CALL__DISPOSITIONS_UPDATED_BY_V0_3_OFFLINE_CLOSURE`
Date: 2026-08-25
Tool decision: `USE_EXISTING`

## Disposition update (2026-08-25)

```text
PF-001=RETRACTED_BY_OWNER_FIRST_PARTY_EVIDENCE
PF-002=RETRACTED_BY_OWNER_FIRST_PARTY_EVIDENCE
PF-003..PF-015=CLOSED_BY_V0_3_OFFLINE_CLOSURE
NF-001..NF-004=CLOSED_BY_V0_3_OFFLINE_CLOSURE
CLOSURE_AUTHORITY=docs/reviews/JIANGHE_STAGE_A_V0_3_OFFLINE_CLOSURE_V0_1.md
```
PF-001/PF-002 are formally retracted on Owner first-party evidence (the vision-exp
model exists and natively accepts image input). All remaining preflight findings
were closed by the deterministic V0.3 offline closure; see the closure authority
for exact implementation and test evidence. The original audit body below remains
the historical record of the pre-closure blockers and is not rewritten.

## Purpose

This is a bounded pre-failure audit before completing the V0.3 capability-first offline closure. It exists to prevent another paid attempt from discovering predictable request, provider, evidence, workflow, or accounting defects only after money has been spent.

No provider call was made by this audit.

## Executive finding

V0.3 is **not yet safe to execute**. The largest blocker is not JSON or output length: the current first-party DeepSeek V4 API surface is text-only, while the Owner-approved matched capability contract requires the same K-line visual bytes to reach each tested model brain.

Current first-party DeepSeek documentation lists `deepseek-v4-flash` / `deepseek-v4-pro` for Chat Completions and explicitly documents image/file input as unsupported for Responses API. DeepSeek's own VS Code/Copilot integration states that DeepSeek V4 is text-only and that image handling is proxied through another installed Copilot vision model before a text description is sent to DeepSeek. Such a proxy cannot be scored as native DeepSeek K-line visual reading under `SAME_MATERIAL / SAME_QUESTION / DIFFERENT_MODEL_BRAIN`.

The repository still binds `deepseek-v4-flash-vision-exp` in the current generic provider spec. That model id is not in the current first-party DeepSeek Chat Completions model list and must not be silently reused as a current supported visual route.

## Blocking findings

### PF-001 — DeepSeek current first-party V4 route does not satisfy the native-visual matched exam

Severity: `BLOCKER__RESEARCH_FAIRNESS`

Required before any DeepSeek V0.3 paid call:

- verify a current first-party DeepSeek model/route that natively consumes the governed K-line image bytes; or
- obtain a new Owner research-design decision changing the common exam so DeepSeek is not falsely credited with another model's vision output.

Forbidden workaround: use the VS Code vision proxy and score the resulting answer as DeepSeek native K-line visual accuracy.

### PF-002 — Current provider model binding is stale for DeepSeek

Severity: `BLOCKER__MODEL_IDENTITY`

Current repository code binds `deepseek-v4-flash-vision-exp`; current DeepSeek first-party Chat Completions documentation lists `deepseek-v4-flash` and `deepseek-v4-pro`.

V0.3 must bind an explicitly current model id and require the provider-resolved model identity to match the frozen intended model/alias semantics before scoring.

### PF-003 — V0.2 strict output formatting is still embedded in the current transport

Severity: `BLOCKER__CAPABILITY_EXAM_CONTAMINATION`

Current generic transport still applies:

- Kimi: strict `json_schema` output;
- DeepSeek: `json_object` output;
- MiniMax: no equivalent strict JSON constraint.

The V0.3 capability pass must not impose unequal output-format constraints. The common capability answer request should use the same simple semantic headings/text contract for all providers. Structured production formatting occurs only after raw final-answer preservation through a deterministic format-only adapter.

### PF-004 — Current Stage-A request object cannot express V0.3

Severity: `BLOCKER__PRE_NETWORK`

`StageAInputRequest` currently:

- constrains `max_output_tokens` to `1..2000`;
- requires the old frozen runtime JSON schema;
- accepts only V0.1/V0.2 request-contract versions.

A V0.3 request/identity type is required. Merely increasing provider max tokens would either fail pre-network or retain the old capability-format coupling.

### PF-005 — Current Stage-A budget envelope still enforces historical CNY18/CNY6 limits

Severity: `BLOCKER__WRONG_RESEARCH_CONTRACT`

`StageABudgetEnvelope` still freezes CNY18 total and CNY6/provider. V0.3 must not reuse it. The project-wide CNY100 hard cap remains binding.

### PF-006 — New CNY100 ledger must carry historical spend forward

Severity: `BLOCKER__HARD_CAP_ACCOUNTING`

The generic `CnyBudgetLedger` initializes spent amount at zero. V0.3 cannot create a fresh zero-spend project ledger because historical conservative project accounting already equals CNY0.270021.

The V0.3 executable ledger must cryptographically/durably carry that amount forward, leaving at most CNY99.729979 of the Owner hard cap under current conservative accounting.

### PF-007 — V0.3 durable evidence must preserve final answer without preserving hidden reasoning

Severity: `BLOCKER__EVIDENCE_BOUNDARY`

Current Stage-A safe evidence intentionally stores hashes/mechanical facts but omits raw final text. V0.3 requires `MODEL_RAW_FINAL_ANSWER` plus an identity-bound normalized view.

The new evidence path must persist only the provider's final answer content and must not persist the full raw provider response when that response contains `reasoning_content`, `reasoning_details`, or equivalent hidden reasoning. MiniMax should retain `reasoning_split=true`; Kimi/DeepSeek reasoning fields must be excluded from durable final-answer evidence.

### PF-008 — Common-exam identity and provider-inference identity must be separated

Severity: `BLOCKER__FAIRNESS_PROOF`

Provider-specific completion headroom is allowed in V0.3. Therefore a single request identity that includes output-token ceiling cannot prove `SAME_MATERIAL / SAME_QUESTION` across providers.

V0.3 must have at least:

1. a provider-neutral common capability-exam identity binding Jianghe material, question, visual bytes, structured observation and point-in-time boundary;
2. a provider-specific inference-configuration identity binding model, reasoning controls, output headroom and wire syntax;
3. an attempt identity binding both.

### PF-009 — MiniMax image transport must use a first-party documented form

Severity: `BLOCKER__INPUT_ACCEPTANCE`

Current MiniMax-M3 first-party OpenAI-compatible documentation confirms native image understanding and documents `image_url` with an HTTPS URL. The current repository transport sends a base64 data URL. First-party documentation reviewed in this audit did not establish that MiniMax-M3 accepts the base64 data-URL form used by the repository.

Before execution, freeze a documented MiniMax visual transport that preserves the exact governed PNG bytes. Provider-required wire syntax may differ while image-byte identity remains the same.

Kimi K3 first-party documentation explicitly supports local base64 data URLs, so the current Kimi image representation is compatible with current documentation.

### PF-010 — Output headroom and network timeout must be independent

Severity: `HIGH__OPERATIONAL`

Increasing output headroom without increasing the current 60-second HTTP timeout can convert a token-truncation failure into a timeout failure. V0.3 must use a bounded but sufficient request/network timeout and workflow timeout appropriate to reasoning models. Latency is a measured result, not a capability gate.

### PF-011 — Cost comparison needs cache-aware accounting

Severity: `HIGH__METRIC_CORRECTNESS`

Current first-party DeepSeek, Kimi and MiniMax documentation exposes caching effects. A single flat input-token price can be conservative for spend guarding, but it is not necessarily exact `ACTUAL_CNY_COST` when cached tokens are present.

V0.3 must distinguish:

- conservative pre-call reservation / hard-cap accounting; and
- post-call observed/billing-derived cost metric, using provider-reported cached-token fields and current first-party pricing semantics when available.

If exact provider wallet billing cannot be established, the comparison must label the number as calculated/conservative rather than falsely naming it exact billed CNY.

### PF-012 — Finish/result state must not be encoded only as workflow failure

Severity: `HIGH__SEMANTIC_SEPARATION`

The historical MiniMax run ended with process exit code 2 because `NON_SCOREABLE_NORMALIZER` was treated as a terminal runner error. V0.3 needs separate states for infrastructure/transport failure, complete capability answer, output-incomplete/truncated answer, and adapter/format incompatibility.

A format/adapter failure must preserve the complete raw final answer and must not become a Jianghe capability fail. A true infrastructure failure may still make the workflow/job fail.

### PF-013 — New workflow must use current Node24-capable GitHub Actions majors

Severity: `MEDIUM__CI_MAINTENANCE`

The historical screenshot warning came from `actions/checkout@v4` and `actions/setup-python@v5` being forced onto Node24 after Node20 deprecation. It did not cause the MiniMax exit-code-2 result.

The future V0.3 workflow should use current GitHub-maintained Node24-capable action majors verified at implementation time (current upstream documentation shows checkout/setup-python v7) and pin the intended Python version.

The retired V0.2 workflow no longer loads checkout/setup-python or credentials, so no historical workflow repair is required.

### PF-014 — Authorization/pricing/model authorities must be fresh at execution time

Severity: `HIGH__PRE_NETWORK`

The current Owner paid-call authorization expires at `2026-08-31T00:00:00+08:00`. V0.3 preflight must fail closed if authorization, rate card, model id, or pricing authority has expired/drifted before the first network attempt. No automatic extension/recharge is permitted.

### PF-015 — Provider result must prove intended model identity

Severity: `HIGH__MODEL_IDENTITY`

A 2xx response is insufficient if the provider resolves to an unintended model/alias. V0.3 must record requested and resolved model ids and enforce the frozen model-resolution policy before accepting the answer into matched capability evidence.

## Existing engineering that passed this audit and should be retained

- Jianghe source/context projection keeps expected answer/rubric/hidden future out of model context.
- canonical structured observation and visual hashes bind the same observation.
- outcome/future-field scan remains fail-closed.
- provider tools are not provided for the governed model call.
- MiniMax `reasoning_split=true` is the correct direction for separating final answer from reasoning.
- the historical V0.2 paid workflow is currently retired and fails before credentials/provider transport.

## GitHub 404 handling finding

`404 Not Found` means the requested server/resource route was not exposed as found for that request. It does **not** prove that a repository file or original URL was deleted.

Observed causes relevant to this project include wrong/unsupported ref or path, private-resource/permission masking, connector action scope differences, and transient connector/API behavior. During the preceding authority update, a 404 occurred on an existing `00_READ_FIRST.md` update; an immediate authenticated refetch showed the file still existed and the retry succeeded. During this audit, connector reads of some previously existing paths/refs also returned 404 while other current-main files remained accessible.

Runtime rule for project-brain GitHub access:

- never interpret one connector 404 as deletion;
- retry by authenticated file/ref read using the most specific supported connector action;
- corroborate deletion through current main/tree/history or another authenticated route before changing project facts;
- before an update, refetch the current blob SHA;
- if repeated authenticated reads disagree, fail closed and report connector access uncertainty instead of inventing repository state.

This GitHub-connector issue is separate from provider HTTP status and separate from the historical MiniMax workflow exit code.

## Historical screenshot adjudication

### Red box — exit code 2

The red result is an old V0.2 runner semantic: provider response evidence ended at `NON_SCOREABLE_NORMALIZER`, and the process returned exit code 2. It is not evidence that Node.js caused the provider call to fail, and it is not a second MiniMax API failure.

V0.3 must replace this coupling with explicit operational/capability/output-format states as required by PF-012.

### Yellow box — Node20 deprecation

The yellow message is a GitHub Actions runtime deprecation warning. It did not produce exit code 2. It should be eliminated in the new V0.3 workflow by using current Node24-capable action majors; the historical V0.2 run/evidence is not rewritten.

## Required zero-network closure gate

No V0.3 paid workflow becomes executable until all applicable blockers above are closed by deterministic tests/evidence, including:

- current first-party provider/model/visual-input contract frozen;
- DeepSeek visual-fairness blocker resolved by a valid current route or new Owner research-design decision;
- common-exam identity equality across providers;
- provider-specific inference identities and sufficient completion headroom;
- no strict-JSON capability bias;
- raw-final / no-CoT durable evidence tests;
- format-only adapter adversarial tests;
- historical CNY0.270021 carry-forward and CNY100 hard guard tests;
- timeout/finish-state tests;
- requested/resolved model identity tests;
- MiniMax visual transport verification;
- cache-aware cost-measurement semantics;
- current GitHub Actions runtime versions;
- focused zero-network tests plus canonical suite.

Only after this closure may a new V0.3 paid attempt identity be minted.

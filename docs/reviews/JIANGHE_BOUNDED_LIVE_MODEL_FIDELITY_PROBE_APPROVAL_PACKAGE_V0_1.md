# 江河受限真实模型 Fidelity Probe Owner 批准包 V0.1

> Status: `AWAITING_OWNER_APPROVAL`  
> Date: 2026-08-23  
> Scope: one bounded, non-outcome, real-provider Jianghe fidelity probe after `PRE_LIVE_FIDELITY_GATE_REAUDIT=PASS`.  
> This document does **not** authorize network calls, credentials, paid spend, candidate outcomes, PRIMARY freeze, provider/model adoption, Broker, or real money.

## 1. Current authority

```text
PRE_LIVE_FIDELITY_GATE_REAUDIT=PASS
PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT=PASS
JIANGHE_PRIMARY_BRANCH_REGISTRY_V0_5=INTEGRATED_PRE_FREEZE_NON_FINAL_FIXED_RUBRIC_REAUDIT_PASS
JIANGHE_PRIMARY_PROJECT_BRAIN_ACCEPTED_READY_COUNT=340
JIANGHE_PRIMARY_ELIGIBLE=NO
JIANGHE_PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
LIVE_MODEL_PROVIDER_PROBE=AWAITING_OWNER_BOUNDED_PROBE_APPROVAL
PAID_MODEL_SPEND=NOT_AUTHORIZED
OUTCOME_ACCESS=NO
```

Binding repo authorities:

- `CURRENT_STATE.md`
- `PROJECT_BRAIN_RUNTIME_BRIEF.md`
- `docs/reviews/JIANGHE_PRE_LIVE_FIDELITY_GATE_REAUDIT_V0_1.md`
- `docs/reviews/JIANGHE_PRIMARY_CURATED_QUALITY_FIXED_RUBRIC_REAUDIT_V0_1.md`
- `docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_1.json`
- `docs/reviews/JIANGHE_REAL_MODEL_PROVIDER_CANDIDATE_REVIEW_V0_1.md`

The purpose of this probe is **Jianghe fidelity evidence**, not profit, P&L, win rate, Sharpe, expectancy, or outcome selection.

## 2. Project-brain recommendation

Approve one bounded comparative live probe against three exact provider/model candidates:

| Provider | API surface | Exact requested model | Why included |
| --- | --- | --- | --- |
| OpenAI | Responses API | `gpt-5.6-sol` | Current stable frontier OpenAI model; supports image input and structured outputs. |
| Anthropic | Messages API | `claude-fable-5` | Current highest-capability generally available Claude model; current Claude models support image input; structured outputs available. |
| Google | Gemini GenerateContent API | `gemini-3.7-flash` | Current GA stable Gemini model with image input, structured outputs and configurable thinking; chosen over preview Pro models to avoid preview drift. |

DeepSeek is **not** included because the current project provider review does not establish the mandatory visual-input / dual-input capability needed for this fidelity gate.

No alias substitution is allowed. If an exact requested model is unavailable, that provider is skipped and the project returns to the Owner/project brain; it is not silently replaced.

External reconnaissance date: 2026-08-23. Official documentation checked before this package:

- OpenAI model/pricing: `https://developers.openai.com/api/docs/models/gpt-5.6-sol`, `https://openai.com/api/pricing/`
- Anthropic model/version/pricing: `https://platform.claude.com/docs/en/about-claude/models/overview`, `https://platform.claude.com/docs/en/about-claude/models/model-ids-and-versions`, `https://platform.claude.com/docs/en/about-claude/pricing`, `https://platform.claude.com/docs/en/build-with-claude/structured-outputs`
- Gemini model/pricing: `https://ai.google.dev/gemini-api/docs/models/gemini-3.7-flash`, `https://ai.google.dev/gemini-api/docs/pricing`

These external facts are candidate probe-selection evidence only; they do not make any provider/model `VERIFIED` or `ADOPTED`.

## 3. Exact probe envelope

### 3.1 Calls

The project may make at most:

```text
PROVIDERS=3
SMOKE_CALLS=1_PER_PROVIDER
SCORED_FIXTURES=8_PREDECLARED_NON_OUTCOME_FIXTURES
CONTENT_TRACKS=SEMANTIC,VISUAL,STRUCTURED,DUAL_INPUT
REPEATS_PER_CONTENT_TRACK=2_IDENTICAL_REQUESTS
OPERATIONAL_PROVIDER_FIXTURES=2_PER_PROVIDER
OPERATIONAL_PROVIDER_REPEATS=2
NORMAL_PLANNED_CALLS_PER_PROVIDER=69
NORMAL_PLANNED_CALLS_TOTAL=207
NETWORK_RETRY_ALLOWANCE=MAX_1_RETRY_PER_PROVIDER_FOR_TRANSPORT_429_OR_5XX_ONLY
ABSOLUTE_BILLABLE_REQUEST_CAP=210
```

The exact eight fixture IDs must be predeclared in a machine-readable probe plan **before the first network call**, selected without outcome access to cover A/B/C/D/NONE plus hard-negative / UNKNOWN-honesty / contradiction-preservation behavior. Selection may not change after observing model responses.

A retry is permitted only for an explicit transport-layer 429 or 5xx failure. Schema failure, refusal, malformed output, model mismatch, evidence mismatch, or fidelity failure is recorded as evidence and is **not** retried to improve the score.

### 3.2 Inference configuration

All provider-specific inference configuration must be identity-bound before calls.

Recommended initial settings:

```text
OPENAI_MODEL=gpt-5.6-sol
OPENAI_REASONING_EFFORT=high
OPENAI_TOOLS=DISABLED
OPENAI_WEB_SEARCH=DISABLED

ANTHROPIC_MODEL=claude-fable-5
ANTHROPIC_THINKING=PROVIDER_DEFAULT_ADAPTIVE
ANTHROPIC_TOOLS=DISABLED

GEMINI_MODEL=gemini-3.7-flash
GEMINI_THINKING_LEVEL=high
GEMINI_TOOLS=DISABLED
GEMINI_SEARCH_GROUNDING=DISABLED

TEMPERATURE_OR_SAMPLING_OVERRIDE=NONE_UNLESS_REQUIRED_BY_PROVIDER_CONTRACT
MAX_MODEL_OUTPUT_TOKENS=2000
```

Repeated calls use identical request content/configuration. The purpose of repeats is to observe stability, not to cherry-pick the best answer.

## 4. Data egress explicitly requested for Owner approval

The following project data may leave the local machine and be sent to the approved API providers, and **only** these categories:

1. the current candidate pre-live system prompt / decision prompt / response schema;
2. the minimal Jianghe V1.1 + PRIMARY V0.5 context selected by the governed context-selection package for the chosen fixture;
3. the eight predeclared **synthetic, non-outcome** fidelity fixtures;
4. deterministic `image/png` chart renders for VISUAL / DUAL_INPUT tracks;
5. governed structured observation JSON for STRUCTURED / DUAL_INPUT tracks;
6. non-sensitive probe-session identifiers needed for evidence binding.

Explicitly forbidden from egress:

```text
CANDIDATE_OUTCOMES
FUTURE_PRICE_OR_FUTURE_BAR_DATA
VALIDATION_OR_FINAL_HOLDOUT
SHADOW_FORWARD_DATA
CANDIDATE_PNL_WIN_RATE_SHARPE_EXPECTANCY
BROKER_OR_ACCOUNT_DATA
REAL_MONEY_DATA
PERSONAL_USER_DATA
API_KEYS_OR_OTHER_CREDENTIALS
RAW_SOURCE_VIDEO_FILES
UNNECESSARY_FULL_CORPUS_EXPORTS
```

No provider-native web search, file search, code execution, computer use, grounding, MCP, or external tool is enabled in the probe.

## 5. Credential handling

Owner approval authorizes use of provider API credentials only under these controls:

- provider/project-scoped API keys where available;
- keys supplied locally through environment variables or equivalent secret storage;
- never committed to Git, prompt artifacts, test fixtures, logs, raw-response evidence, or screenshots;
- no credential value may appear in exception text;
- if a credential leak is detected, the probe stops immediately and that credential must be revoked/rotated before any continuation;
- if the Owner does not have an account/key for one approved provider, that provider is skipped — no unapproved provider/model substitution.

Suggested environment-variable names:

```text
OPENAI_API_KEY
ANTHROPIC_API_KEY
GEMINI_API_KEY
```

This package does not authorize creating a new paid account, adding a payment method, buying prepaid credits, or accepting new commercial terms on the Owner's behalf. Any such account action remains an explicit Owner action.

## 6. Spend envelope

Recommended approval:

```text
TOTAL_HARD_SPEND_CAP_USD=100.00
EXPECTED_SPEND_BELOW_CAP=YES
CALL_CAP=210
NO_AUTOMATIC_BUDGET_EXTENSION=YES
```

The hard cap is cumulative across all three providers. The project must compute a running cost estimate from returned usage and the provider rate card captured at probe start. Calls stop before the next request if that request could reasonably cause the cumulative estimate to exceed the remaining budget.

Current public standard-rate reference at package preparation time:

- OpenAI `gpt-5.6-sol`: approximately `$5 / 1M input`, `$30 / 1M output`;
- Anthropic `claude-fable-5`: approximately `$10 / 1M input`, `$50 / 1M output`;
- Google `gemini-3.7-flash`: introductory paid rate approximately `$0.75 / 1M input`, `$3.75 / 1M output` through 2026-12-31.

Rates must be rechecked immediately before implementation. A price change does not expand the `$100` cap.

For Google, the probe must use a paid API tier where the provider states submitted content is not used to improve products; do not use the free tier for this project probe. For OpenAI API and Anthropic commercial API, provider documentation currently states inputs/outputs are not used for model training by default unless the customer explicitly opts in. Data retention is provider-specific and should not be interpreted as zero retention unless the account is separately eligible/configured for it.

## 7. Required local evidence capture

For every billable request, capture without credentials:

```text
provider_identity
api_surface_and_version
endpoint_semantics_identity
requested_model_selector_identity
provider_resolved_model_or_version
capability_identity
prompt_package_identity
context_selection_identity
runtime_normalizer_identity
evaluator_extractor_identity
observation_identity
visual_artifact_identity_if_applicable
structured_artifact_identity_if_applicable
request_identity
provider_response_id
raw_response_sha256
normalized_response_identity
usage_identity
request_at
response_at
latency_ms
processing_status
evidence_completeness
evidence_eligibility
```

Raw response content may be retained in the private project evidence area for reproducibility, but authentication headers, keys and unnecessary provider/account metadata must be stripped. Any evidence that cannot be bound to the governed request becomes non-scoreable.

## 8. Mandatory stop conditions

The entire probe stops immediately if any of the following occurs:

1. protected outcome / future / P&L data is discovered in a request payload;
2. a credential or secret is written to a repository file/log/evidence artifact;
3. an unapproved provider, model, endpoint or tool would be invoked;
4. requested/resolved model identity violates the approved drift policy;
5. visual and structured inputs cannot be proved to share the same governed observation;
6. provider response evidence cannot be identity-bound or normalizer/evaluator separation fails;
7. cumulative requests reach `210`;
8. cumulative estimated spend reaches the `$100` hard cap;
9. the provider requires a new account/payment/terms action not already performed by the Owner;
10. any code path would access candidate outcomes, Validation, Final, Shadow, Broker, or real-money surfaces.

A provider-specific failure stops that provider. A project-wide firewall/evidence failure stops all providers.

## 9. What this approval does not authorize

Even if the Owner approves this package, it does **not** authorize:

- provider/model `ADOPTED` status;
- final model selection;
- PRIMARY semantic freeze;
- candidate outcome backtest;
- Validation / Final / Shadow access;
- Broker/account trading action;
- real-money activity;
- more than 210 requests or more than `$100` spend;
- sending additional data categories;
- substituting another model/provider.

The probe returns a non-outcome evidence package comparing Jianghe fidelity, stability, UNKNOWN honesty, no-invention behavior, visual vs structured vs dual-input behavior, and provider-operational evidence quality. Any later adoption/freeze/outcome decision remains separately gated.

## 10. Owner decision requested

Recommended decision:

```text
APPROVE_BOUNDED_LIVE_MODEL_FIDELITY_PROBE_V0_1=YES
APPROVED_PROVIDERS=OPENAI,ANTHROPIC,GOOGLE_GEMINI
APPROVED_MODELS=gpt-5.6-sol,claude-fable-5,gemini-3.7-flash
APPROVED_DATA_EGRESS=SECTION_4_ONLY
APPROVED_BILLABLE_REQUEST_CAP=210
APPROVED_TOTAL_SPEND_CAP_USD=100.00
OUTCOME_ACCESS=NO
PRIMARY_FREEZE=NO
```

If approved, implementation must first create a machine-readable frozen probe plan and real-provider adapters, run all offline/firewall tests, and only then make the bounded calls. No call occurs merely because this approval package exists.

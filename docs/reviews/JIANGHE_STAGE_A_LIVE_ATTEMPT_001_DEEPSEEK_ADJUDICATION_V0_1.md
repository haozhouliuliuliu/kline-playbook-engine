# JIANGHE STAGE-A LIVE ATTEMPT 001 — DEEPSEEK ADJUDICATION V0.1

Status: `LIVE_ATTEMPT_RECORDED__PROVIDER_FATAL_FAIL_NOT_YET_ADJUDICATED`
Date: 2026-08-24
Tool decision: `USE_EXISTING`

## 1. Durable execution facts

```text
WORKFLOW_RUN_ID=32709432759
WORKFLOW=.github/workflows/stage-a-live-slot.yml
EXECUTION_MAIN_SHA=07cb7f01ae69365943cb4be6b30b711635c2b1e5
PROVIDER=DEEPSEEK
REQUESTED_MODEL=deepseek-v4-flash-vision-exp
SLOT=1
TRACK=OPERATIONAL_PROVIDER
REMOTE_START_HEAD=eb184e0baaca6fad435c08a7ae045a4c118dfb8d
REMOTE_TERMINAL_HEAD=daa5eae090ab60f340e6502e02719fb3bba015d0
EVIDENCE_IDENTITY=d36c1fbbb1cd639e48a6f049f7df1be3bb95d9f346d75bbb85e25451fba9dc55
TERMINAL_STATUS=TRANSPORT_FAILURE
ERROR_TYPE=ProviderResponseError
ERROR_MESSAGE=provider response content is not text
STAGE_A_ACCOUNTED_CNY=0.219222
PROVIDER_ACTUAL_BILLED_CNY=UNKNOWN
AUTOMATIC_RETRY=FORBIDDEN
OUTCOME_ACCESS=NO
```

The fixed remote ledger contains both `NETWORK_ATTEMPT_STARTED` and `ATTEMPT_TERMINAL`. The slot is permanently attempted for automatic execution purposes and must not be rerun.

The workflow reached a 2xx JSON provider response before the runtime raised the content-shape error: the runtime only calls `_extract_text()` after a successful HTTP status and successful top-level JSON decode. The surviving safe evidence does not retain the provider-resolved model, request id, usage, finish reason, content-null/empty distinction, or reasoning metadata because `ProviderInvocationEvidence` is currently constructed only after successful content extraction. Those facts are therefore `UNKNOWN` for Attempt 001 and must not be reconstructed or guessed.

## 2. First-party contract recheck after Attempt 001

The requested DeepSeek model and route remain valid current first-party surfaces. `deepseek-v4-flash-vision-exp` is a current experimental image-capable model; the route is `https://api.deepseek.com/chat/completions`.

Current DeepSeek JSON Output guidance:
- `response_format={"type":"json_object"}` is supported;
- the prompt should contain JSON guidance and an example of the desired JSON shape;
- `max_tokens` must be large enough to avoid truncation;
- the provider explicitly warns that JSON Output can occasionally return empty `content`.

Current DeepSeek thinking guidance:
- thinking defaults to enabled;
- reasoning is returned separately in `reasoning_content`;
- normal requests default to high reasoning effort unless explicitly changed.

First-party authorities:
- https://api-docs.deepseek.com/zh-cn/
- https://api-docs.deepseek.com/zh-cn/guides/json_mode/
- https://api-docs.deepseek.com/zh-cn/guides/thinking_mode/
- https://github.com/deepseek-ai/deepseek-harness

## 3. Project-side V0.1 configuration finding

The frozen DeepSeek V0.1 payload uses:

```text
response_format=json_object
max_tokens=400
thinking=OMITTED__PROVIDER_DEFAULT_APPLIES
reasoning_effort=OMITTED__PROVIDER_DEFAULT_APPLIES
```

The common prompt requests strict JSON but does not include the concrete JSON-output example that current DeepSeek JSON Output guidance asks for.

Therefore Attempt 001 does **not** establish that the DeepSeek model/route is inherently unusable. It establishes that the exact frozen V0.1 provider/request configuration produced an unusable final-content shape under the project's parser. Because the response body is not durably recoverable, the exact provider-side reason for the null/empty/non-string content cannot be proven post hoc.

```text
DEEPSEEK_MODEL_EXISTS=YES
DEEPSEEK_ROUTE_VALID=YES
DEEPSEEK_SLOT_1_RETRY=FORBIDDEN
DEEPSEEK_PROVIDER_FATAL_FAIL=NOT_YET_ADJUDICATED
V0_1_PROVIDER_RESPONSE_CONTRACT_DEFECT=OPEN
```

## 4. Cross-provider bounded audit finding

Before spending another Stage-A call, all three provider response contracts must be treated together rather than patched one at a time.

- Kimi Open Platform supports the current `/v1/chat/completions` visual input and Structured Output / JSON Schema surface. K3 is a current visual reasoning model. Its reasoning effort and output-token budget remain part of the frozen inference configuration and must be checked as a fairness/configuration decision rather than tuned after seeing answers.
- DeepSeek requires the correction described above.
- MiniMax's OpenAI-compatible reasoning format can place thinking material inline in `content` unless its documented split-reasoning format is requested. Feeding inline thinking tags into the current strict JSON normalizer creates a foreseeable non-scoreable failure mode.

This is a bounded provider-contract audit triggered by Attempt 001. It does not reopen Jianghe semantics, fixture selection, OHLC stimulus, expected answers, scoring rules, outcome access, or the RMB100 budget design.

## 5. Governance consequence

The Owner-approved Stage-A V0.1 protocol froze prompt/context/schema/inference-configuration identities before the first paid call and forbids silent provider-specific prompt improvement after observing responses. Consequently the project brain must not silently change thinking controls, JSON-output prompting, or the output-token ceiling and then continue under the V0.1 identity.

The safe options are:

```text
A=STRICT_V0_1__ADJUDICATE_ATTEMPT_001_UNSCOREABLE_AND_CONTINUE_ONLY_WITH_UNCHANGED_V0_1_FOR_OTHER_PROVIDERS
B=EXPLICIT_STAGE_A_V0_2_PROVIDER_RESPONSE_COMPATIBILITY_CORRECTION__PRESERVE_ATTEMPT_001_AS_NON_RETRYABLE_SPEND__REFREEZE_ONLY_FUTURE_UNATTEMPTED_CALLS
```

Project-brain recommendation: `B`, because the defect is in the experiment/provider response contract and the same bounded audit identified a foreseeable MiniMax compatibility problem. This recommendation is a new research-design version and therefore requires explicit Owner approval before implementation or further paid calls.

## 6. Locks preserved

```text
LIVE_PROVIDER_ATTEMPTS=1
STAGE_A_ACCOUNTED_CNY=0.219222
PROVIDER_ACTUAL_BILLED_CNY=UNKNOWN
DEEPSEEK_SLOT_1_AUTOMATIC_RETRY=FORBIDDEN
SECOND_PAID_SLOT_AFTER_ATTEMPT_001=NOT_YET_RUN
OUTCOME_ACCESS=NO
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
BSP_003=PRESERVED
```

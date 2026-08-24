# JIANGHE STAGE-A V0.2 PROVIDER RESPONSE COMPATIBILITY — OWNER DECISION

Status: `OWNER_APPROVED__IMPLEMENTATION_AUTHORIZED__NO_PAID_CALL_UNTIL_OFFLINE_CLOSURE`
Date: 2026-08-24
Owner approval time: `2026-08-24T17:14:00+08:00`
Tool decision: `USE_EXISTING`

## 1. Owner decision

The Owner explicitly approved the project-brain recommendation to create an explicit Stage-A V0.2 provider-response compatibility correction after the first real V0.1 attempt exposed an experiment-side response-contract defect.

```text
APPROVE_STAGE_A_V0_2_PROVIDER_RESPONSE_COMPATIBILITY_CORRECTION=YES
IMPLEMENT_NOW=YES
GOAL=RESUME_REAL_STAGE_A_AS_SOON_AS_OFFLINE_CLOSURE_PASSES
```

This approval is a research-design version decision. It does not expand the existing provider set, paid-call authorization, Stage-A call count, budget caps, outcome access, or downstream validation/broker/real-money permissions.

## 2. Attempt 001 is immutable history

Authority: `docs/reviews/JIANGHE_STAGE_A_LIVE_ATTEMPT_001_DEEPSEEK_ADJUDICATION_V0_1.md`.

```text
V0_1_PLAN_IDENTITY=7d6a1838962345c36dd3449f27adfd6c7d18c4988b5e3e2cb4bc65acb52b2fd4
ATTEMPT_001_PROVIDER=DEEPSEEK
ATTEMPT_001_MODEL=deepseek-v4-flash-vision-exp
ATTEMPT_001_SLOT=1
ATTEMPT_001_TRACK=OPERATIONAL_PROVIDER
ATTEMPT_001_EVIDENCE_IDENTITY=d36c1fbbb1cd639e48a6f049f7df1be3bb95d9f346d75bbb85e25451fba9dc55
ATTEMPT_001_ACCOUNTED_CNY=0.219222
ATTEMPT_001_AUTOMATIC_RETRY=FORBIDDEN
ATTEMPT_001_REPLACEMENT_CALL=FORBIDDEN
```

V0.2 must carry this attempt forward mechanically. It may not delete, reclassify away, refund, reset, or rerun it.

## 3. Hard caps remain unchanged and include Attempt 001

```text
TOTAL_API_SPEND_HARD_CAP_CNY=100.00
STAGE_A_TOTAL_CAP_CNY=18.00
STAGE_A_TOTAL_MAX_CALLS=15__INCLUDING_V0_1_ATTEMPT_001
MAX_CALLS_PER_PROVIDER=5__INCLUDING_V0_1_ATTEMPT_001
MAX_STAGE_A_SPEND_PER_PROVIDER_CNY=6.00__INCLUDING_V0_1_ATTEMPT_001
AUTOMATIC_RETRY=FORBIDDEN
AUTOMATIC_BUDGET_EXTENSION=FORBIDDEN
```

Therefore V0.2 has at most 14 future executable calls. DeepSeek has at most four future calls because `DEEPSEEK:1` is already attempted.

No extra operational-smoke replacement call is created. The existing funnel already states that a production-like call may contribute evidence to more than one track. A later successful DeepSeek V0.2 content-track call may therefore supply mechanical route/model/schema/usage evidence for the operational-provider criterion without changing that content track's evaluator focus.

## 4. Frozen research content that does not change

```text
QUALIFICATION_FIXTURE=JH-FIX-C-001__UNCHANGED
SYNTHETIC_OHLC=UNCHANGED
PNG_BYTES=UNCHANGED
STRUCTURED_OBSERVATION=UNCHANGED
TRACK_ISOLATION=UNCHANGED
JIANGHE_KNOWLEDGE_SCOPE=UNCHANGED
SCORING_RULES=UNCHANGED
EXPECTED_ANSWER_ACCESS=NO
OUTCOME_ACCESS=NO
PROVIDER_SET=UNCHANGED
MODEL_SET=UNCHANGED
```

V0.2 is only a provider-response/output-contract correction.

## 5. Common V0.2 output contract

All three providers receive the same response semantics and same non-answer-bearing JSON output-shape guidance. Provider-specific syntax is allowed only where required by the official API contract.

```text
COMMON_MAX_COMPLETION_TOKENS=1024
COMMON_FINAL_ANSWER_FORMAT=ONE_JSON_OBJECT_ONLY
COMMON_REASONING_POLICY=REASONING_ALLOWED__FINAL_CONTENT_SEPARATED_FROM_REASONING_WHERE_PROVIDER_SUPPORTS_SEPARATION
COMMON_JSON_SHAPE_GUIDANCE=YES__SAME_NON_ANSWER_BEARING_GUIDANCE_FOR_ALL_PROVIDERS
COMMON_TOOLS=DISABLED
COMMON_RETRY=ZERO
```

`1024` is the default probe output ceiling already defined by `JIANGHE_RMB100_REAL_MODEL_FIDELITY_FUNNEL_V0_1.md`; V0.1's narrower 400-token implementation is superseded for future unattempted V0.2 calls.

The JSON guidance must be provider-neutral and must not encode a fixture answer, family preference, direction preference, expected action, or scoring hint. Prefer a deterministic field-shape/schema block plus explicit instruction that any placeholder values are syntax-only and must not be copied as the market decision.

The exact added prompt bytes become part of the new prompt/request/payload identities and must be identical across providers for the same track except provider-required wire syntax.

## 6. Provider-specific official wire configuration

### Kimi K3

Current first-party Kimi documentation states that `kimi-k3` always reasons and supports `reasoning_effort`, native vision, JSON mode and structured output.

V0.2 intent:

```text
KIMI_MODEL=kimi-k3
KIMI_THINKING=ALWAYS_ON_BY_PROVIDER_MODEL
KIMI_REASONING_EFFORT=max
KIMI_FINAL_OUTPUT=content
KIMI_RESPONSE_FORMAT=STRICTEST_CURRENT_FIRST_PARTY_STRUCTURED_OUTPUT_SUPPORTED_BY_EXISTING_RUNTIME
KIMI_MAX_COMPLETION_TOKENS=1024
```

Do not weaken Kimi from the already integrated strict structured-output surface unless current first-party API verification proves the existing syntax stale.

### DeepSeek V4 Flash Vision Exp

Current first-party DeepSeek documentation confirms thinking defaults enabled, exposes `thinking` and `reasoning_effort`, and returns reasoning separately in `reasoning_content`. JSON Output requires `response_format=json_object`, JSON guidance/example in the prompt, sufficient `max_tokens`, and may still occasionally return empty `content`.

V0.2 intent:

```text
DEEPSEEK_MODEL=deepseek-v4-flash-vision-exp
DEEPSEEK_THINKING=enabled
DEEPSEEK_REASONING_EFFORT=max
DEEPSEEK_FINAL_OUTPUT=content_ONLY
DEEPSEEK_REASONING_FIELD=reasoning_content__MECHANICAL_METADATA_ONLY_NOT_NORMALIZED_AS_FINAL_JSON
DEEPSEEK_RESPONSE_FORMAT=json_object
DEEPSEEK_MAX_TOKENS=1024
```

An empty/non-text final `content` after a valid 2xx response is a mechanically preserved non-scoreable provider response under V0.2, not a transport-connectivity failure.

### MiniMax M3

Current first-party MiniMax M3 documentation confirms native image/video input, `thinking` control, default adaptive thinking, `reasoning_split`, and `max_completion_tokens`. `reasoning_split=true` separates thinking into `reasoning_content` / `reasoning_details` instead of leaving `<think>...</think>` inside final `content`.

V0.2 intent:

```text
MINIMAX_MODEL=MiniMax-M3
MINIMAX_THINKING={type:adaptive}
MINIMAX_REASONING_SPLIT=true
MINIMAX_FINAL_OUTPUT=content_ONLY
MINIMAX_MAX_COMPLETION_TOKENS=1024
MINIMAX_STREAM=false
```

The exact current first-party wire shape must be rechecked during implementation; stale M2.x-only syntax must not be inferred for M3.

First-party references:
- https://www.kimi.ai/help/kimi-api/api-model-selection
- https://www.kimi.ai/help/kimi-api/api-model-capabilities
- https://api-docs.deepseek.com/zh-cn/guides/thinking_mode/
- https://api-docs.deepseek.com/zh-cn/guides/json_mode/
- https://platform.minimaxi.com/docs/api-reference/text-chat-openai

## 7. Safe 2xx response evidence is mandatory

V0.1 lost useful mechanical facts when final-content extraction failed. V0.2 must preserve secret-safe structural evidence for any successfully decoded 2xx provider JSON **before** final-content normalization decides scoreability.

At minimum, where present and valid:

```text
http_2xx=true
provider_request_id
requested_model_id
resolved_model_id
finish_reason
usage.prompt_tokens
usage.completion_tokens
provider-specific reasoning-token count if exposed
final_content_state=TEXT_NONEMPTY|TEXT_EMPTY|NULL|MISSING|NON_TEXT
final_content_sha256_if_text
reasoning_present=true|false|unknown
reasoning_length_or_provider_reported_token_count_if_available
latency_ms
```

Do not persist chain-of-thought text to Git. Do not expose credentials. Do not require raw provider reasoning for evaluator judgment. Raw provider body remains local/ephemeral under existing secret guards unless an existing safe artifact contract explicitly allows it.

A 2xx response with unusable final content must be distinguishable from HTTP/transport failure.

## 8. V0.2 plan and remote state migration

V0.1 remote state remains immutable historical evidence:

```text
V0_1_REMOTE_REF=refs/heads/stage-a-live-state-v0-1
V0_1_REMOTE_REF_MUTATION_AFTER_V0_2=FORBIDDEN
```

V0.2 must use a new fixed governed ref, recommended:

```text
V0_2_REMOTE_REF=refs/heads/stage-a-live-state-v0-2
CALLER_SELECTED_REMOTE_REF=FORBIDDEN
```

The V0.2 frozen plan/ledger must carry forward Attempt 001 as immutable baseline accounting and attempted-slot state, mechanically bound to the V0.1 plan/evidence/remote-state identities. At minimum:

```text
CARRY_FORWARD_ATTEMPTED_SLOT=DEEPSEEK:1
CARRY_FORWARD_ACCOUNTED_CNY=0.219222
CARRY_FORWARD_PROVIDER_ACCOUNTED_CNY_DEEPSEEK=0.219222
CARRY_FORWARD_LIVE_CALL_COUNT=1
CARRY_FORWARD_EVIDENCE_IDENTITY=d36c1fbbb1cd639e48a6f049f7df1be3bb95d9f346d75bbb85e25451fba9dc55
```

Any V0.2 budget/call-count calculation begins from those carried values. `DEEPSEEK:1` must be non-executable in V0.2.

V0.2 must create a new machine-readable frozen-plan identity and all affected prompt/request/payload/inference/budget identities before another provider call.

## 9. Budget rule

The V0.2 builder must recompute exact worst-case costs from the exact new payload bytes and the current pricing authority. It must fail closed if any existing cap is exceeded.

A rough pre-build check using only the output-ceiling increase from 400 to 1024, before accounting for any new prompt bytes, gives five-slot ceilings approximately:

```text
KIMI≈5.88972_CNY
DEEPSEEK≈0.804048_CNY
MINIMAX≈1.1409468_CNY
```

These are **not** frozen V0.2 ceilings. Exact values must come from deterministic rebuild after the final common output-contract bytes are fixed. Kimi's CNY6/provider cap is tight; if the exact common guidance makes Kimi exceed CNY6, reduce prompt overhead without weakening semantics. Do not increase the CNY6 cap and do not silently lower the common output ceiling below 1024 without project-brain review.

## 10. Acceptance before the next paid call

Required:

```text
FIRST_PARTY_PROVIDER_CONTRACT_RECHECK=PASS
V0_2_PLAN_DETERMINISTIC_REBUILD=PASS
V0_2_CARRY_FORWARD_ATTEMPT_001=PASS
DEEPSEEK_SLOT_1_NON_EXECUTABLE=PASS
REMOTE_V0_1_IMMUTABLE=PASS
REMOTE_V0_2_FIXED_REF=PASS
SAFE_2XX_MECHANICAL_EVIDENCE=PASS
THINKING_FINAL_SEPARATION=PASS
SECRET_GUARDS=PASS
ZERO_NETWORK_TESTS=PASS
FOCUSED_ADVERSARIAL_TESTS=PASS
CANONICAL_LINUX_FULL_SUITE=PASS
DIFF_HYGIENE=PASS
LIVE_CALLS_DURING_IMPLEMENTATION=0
PAID_SPEND_DURING_IMPLEMENTATION=CNY0
```

After project-brain closure, resume with one explicit unattempted Stage-A slot only. No automatic next slot.

## 11. Locks preserved

```text
OUTCOME_ACCESS=NO
CANDIDATE_OUTCOME_BACKTEST=NOT_AUTHORIZED
PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_HOLDOUT_ACCESS=LOCKED
PROSPECTIVE_SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
BSP_003=PRESERVED
TOOL_DECISION=USE_EXISTING
```

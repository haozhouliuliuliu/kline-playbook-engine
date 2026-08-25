# DeepSeek V4 Flash Vision Exp 第一方事实纠正 V0.1

> Status: `COMPLETE__PROVIDER_FACT_CORRECTED`
> Date: 2026-08-24
> Scope: correct the time-sensitive DeepSeek provider/model fact and preserve the Owner's pricing/performance reconfirmation. This does not authorize paid calls or claim project Jianghe-fidelity verification.

## Executive correction

```text
PRIOR_CONCLUSION=DEEPSEEK_V4_FLASH_VISION_EXP_NOT_FIRST_PARTY_VERIFIABLE
PRIOR_CONCLUSION_STATUS=SUPERSEDED
MODEL_ID=deepseek-v4-flash-vision-exp
STATUS=EXPERIMENTAL_API_MODEL
RELEASE_DATE=2026-08-21
DIRECT_API=YES
IMAGE_INPUT=YES
TEXT_INPUT=YES
TEXT_OUTPUT=YES
PROVIDER_VERIFIED_BY_PROJECT_LIVE_CALL=NO
ADOPTED=NO
PAID_CALL_AUTHORIZATION=NO
```

The earlier exclusion relied on stale documentation that pre-dated the August 21 launch. It must not be used to classify the current experimental Vision Exp model as text-only.

## First-party evidence

### 1. DeepSeek official Harness repository

DeepSeek's official repository `deepseek-ai/deepseek-harness` records the launch-era release at commit:

```text
b150a551b8d465e31e418e1b2eaf5e79bbb7d28e
release: dsh@0.1.1-rc.2
2026-08-21T12:03:37Z
```

Its `packages/llm/llm-deepseek/README.md` includes the model catalog entry:

```yaml
- id: deepseek-v4-flash-vision-exp
  name: DeepSeek-V4-Flash-Vision-Exp
  inputModalities: [text, image]
```

The same launch-era catalog advertises the image-capable experimental model alongside the standard V4 Flash/Pro entries and documents a roughly 1,000,000-token default context-window setting.

First-party repository evidence:
- https://github.com/deepseek-ai/deepseek-harness
- https://github.com/deepseek-ai/deepseek-harness/blob/b150a551b8d465e31e418e1b2eaf5e79bbb7d28e/packages/llm/llm-deepseek/README.md

### 2. DeepSeek API vision / pricing material

First-party launch material points to:
- https://api-docs.deepseek.com/guides/vision
- https://api-docs.deepseek.com/quick_start/pricing/

The project-captured launch behavior is:

```text
MODEL_ID=deepseek-v4-flash-vision-exp
MODALITY=text+image -> text
API_SURFACES=Chat Completions, Responses API, Anthropic-compatible Messages
IMAGE_INPUT_PATHS=base64, public URL, Files API file_id
IMAGE_BILLING=ordinary input tokens
IMAGE_TOKEN_CEILING=approximately up to 384 tokens per image after provider resizing
FILES_API=AVAILABLE
CONTEXT≈1,000,000 tokens
MAX_OUTPUT≈384,000 tokens
```

The model is explicitly experimental. That creates drift/deprecation risk but is not itself a reason to exclude it from a bounded Jianghe-fidelity comparison.

## Owner reconfirmation — 2026-08-24

The Owner independently rechecked the current release and reconfirmed:

```text
DIRECT_IMAGE_INPUT=YES
PRICE_RELATION_TO_V4_FLASH=SAME
BASE_PERFORMANCE_RELATION_TO_V4_FLASH=SAME
ADDED_CAPABILITY=MULTIMODAL
```

For project governance, the price/performance relationship above is a provider/Owner-level product fact. It is **not** a project Jianghe-fidelity `VERIFIED` result and does not make the model `ADOPTED`; those statuses still require the separately authorized real-model fidelity probe.

## Pricing correction and spend-guard rule

Vision Exp is treated as using the V4 Flash rate card. The captured schedule is:

```text
OFF_PEAK_CACHE_HIT_CNY_PER_MTOK=0.05
PEAK_CACHE_HIT_CNY_PER_MTOK=0.10
OFF_PEAK_CACHE_MISS_CNY_PER_MTOK=1.50
PEAK_CACHE_MISS_CNY_PER_MTOK=3.00
OFF_PEAK_OUTPUT_CNY_PER_MTOK=4.50
PEAK_OUTPUT_CNY_PER_MTOK=9.00
```

Images are tokenized and billed as input, with the captured ceiling around 384 visual tokens per image.

The executable CNY100 hard-cap guard deliberately uses the expensive side:

```text
BUDGET_INPUT_RATE_CNY_PER_MTOK=3.00
BUDGET_OUTPUT_RATE_CNY_PER_MTOK=9.00
BUDGET_IMAGE_INPUT_TOKENS_PER_IMAGE=384
CACHE_DISCOUNT_CREDITED=NO
OFF_PEAK_DISCOUNT_CREDITED=NO
```

This inheritance is governed by `docs/reviews/PROVIDER_PRICING_FALLBACK_POLICY_V0_1.md`. A missing separately indexed experimental-model tariff page therefore does not block work when the same-family price relation is established, while the guard still reserves against the more expensive applicable rate.

## Project implications

The candidate satisfies the project's hard minimum of direct visual K-line input.

Two candidate-specific risks remain for the real fidelity probe:

1. **Experimental identity/drift:** the `-exp` model may change or be superseded. Transport evidence must preserve both requested and provider-resolved model identity.
2. **Visual compression:** the approximately 384-token visual ceiling may degrade fine K-line labels, wick detail or dense chart structure. This is a reason to test actual Jianghe visual fidelity, not to exclude the candidate before testing.

Provider-side JSON Output/tool support exists, but the project does not assume a strict JSON-Schema guarantee equivalent to Kimi's strongest surface. The project strict runtime normalizer remains authoritative.

## Corrected candidate status

```text
KIMI_K3=CANDIDATE
DEEPSEEK_V4_FLASH_VISION_EXP=CANDIDATE__EXPERIMENTAL__FIRST_PARTY_DOCUMENTED_DIRECT_VISUAL_API
MINIMAX_M3=CANDIDATE
FINAL_APPROVED_PROVIDER_SET=NOT_DECIDED
NO_PROVIDER_VERIFIED_BY_PROJECT_LIVE_CALL=YES
NO_PROVIDER_ADOPTED=YES
LIVE_CALLS=0
PAID_SPEND=0
```

This correction does not authorize external spend, outcome access, PRIMARY semantic freeze, Validation, historical Final, Shadow/Forward, broker access, or real money.

## V0.3 offline-closure disposition (2026-08-25)

```text
PF-001=RETRACTED_BY_OWNER_FIRST_PARTY_EVIDENCE
PF-002=RETRACTED_BY_OWNER_FIRST_PARTY_EVIDENCE
DEEPSEEK_CURRENT_FIRST_PARTY_NATIVE_VISUAL_ROUTE=VERIFIED__VISION_EXP_DIRECT_IMAGE_INPUT
DEEPSEEK_NATIVE_VISION_MODEL_EXISTS=YES
```
The earlier text-only inferences about `deepseek-v4-flash-vision-exp` are not current
project facts. First-party `api-docs.deepseek.com` documentation confirms:
- `deepseek-v4-flash-vision-exp` is a current experimental multimodal model;
- base64 data-URL `image_url` is documented image input method #1 for Chat Completions;
- images are accepted only in `user` messages;
- `max_tokens` is the completion field; thinking mode returns `reasoning_content`.

This disposition does not authorize a paid call on its own; execution remains
gated by the V0.3 offline closure (`docs/reviews/JIANGHE_STAGE_A_V0_3_OFFLINE_CLOSURE_V0_1.md`)
and the project brain.

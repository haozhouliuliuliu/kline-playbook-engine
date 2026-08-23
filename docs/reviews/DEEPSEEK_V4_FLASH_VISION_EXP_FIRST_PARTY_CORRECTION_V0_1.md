# DeepSeek V4 Flash Vision Exp 第一方事实纠正 V0.1

> Status: `COMPLETE__PROVIDER_FACT_CORRECTED`
> Date: 2026-08-24
> Scope: correct only the time-sensitive DeepSeek provider/model fact in the 2026-08-24 provider refresh. This does not reopen the frozen pre-spend findings, select a provider, authorize paid calls, or claim project fidelity verification.

## Executive correction

```text
PRIOR_CONCLUSION=DEEPSEEK_V4_FLASH_VISION_EXP_NOT_FIRST_PARTY_VERIFIABLE
PRIOR_CONCLUSION_STATUS=SUPERSEDED
DEEPSEEK_V4_FLASH_VISION_EXP=FIRST_PARTY_DOCUMENTED_CURRENT_API_CANDIDATE
MODEL_ID=deepseek-v4-flash-vision-exp
STATUS=EXPERIMENTAL_API_MODEL
RELEASE_DATE=2026-08-21
DIRECT_API=YES
IMAGE_INPUT=YES
TEXT_INPUT=YES
TEXT_OUTPUT=YES
PROVIDER_VERIFIED_BY_LIVE_CALL=NO
ADOPTED=NO
PAID_CALL_AUTHORIZATION=NO
```

The earlier provider refresh relied on stale crawled documentation that pre-dated the August 21 launch. It must not be used to downgrade the current Vision Exp candidate or to infer that the current direct image-capable model is text-only.

## First-party evidence

### 1. DeepSeek official Harness repository

DeepSeek's official repository `deepseek-ai/deepseek-harness` at the launch-era release records the model catalog entry:

```yaml
- id: deepseek-v4-flash-vision-exp
  name: DeepSeek-V4-Flash-Vision-Exp
  inputModalities: [text, image]
```

The launch-era model catalog therefore establishes the direct image-capable experimental candidate independently from older text-only route prose.

First-party repository:
- https://github.com/deepseek-ai/deepseek-harness
- launch-era release evidence previously captured by this project

### 2. DeepSeek API vision documentation / launch material

Current launch material points to DeepSeek's first-party vision guide:

- https://api-docs.deepseek.com/guides/vision
- https://api-docs.deepseek.com/quick_start/pricing/

The documented candidate behavior captured by the project is:

```text
MODEL_ID=deepseek-v4-flash-vision-exp
MODALITY=text+image -> text
API_SURFACES=Chat Completions, Responses API, Anthropic-compatible Messages
IMAGE_INPUT_PATHS=base64, public URL, Files API file_id
IMAGE_BILLING=ordinary input tokens
IMAGE_TOKEN_CEILING=up to approximately 384 tokens per image after provider resizing
FILES_API=AVAILABLE
CONTEXT≈1,000,000 tokens
MAX_OUTPUT≈384,000 tokens
```

The launch is experimental. Experimental status is a drift/deprecation risk to preserve in evidence, not a reason to exclude the candidate from a bounded Jianghe-fidelity comparison.

## Owner reconfirmation — 2026-08-24

The Owner rechecked the current DeepSeek release and reconfirmed all of the following for the implementation/probe scope:

```text
DIRECT_IMAGE_INPUT=YES
PRICE_RELATION_TO_V4_FLASH=SAME
BASE_PERFORMANCE_RELATION_TO_V4_FLASH=SAME
ADDED_CAPABILITY=MULTIMODAL
```

This reconfirmation supersedes the later stale-harness detour that incorrectly treated DeepSeek's current direct route as text-only.

For project governance, these are provider/Owner-level product facts. The performance statement is **not** a project Jianghe-fidelity `VERIFIED` result and does not make the model `ADOPTED`. Those statuses still require the separately authorized real-model fidelity probe.

## Pricing correction and spend-guard rule

Vision Exp uses the V4 Flash rate card. The captured schedule is:

```text
OFF_PEAK_CACHE_HIT_CNY_PER_MTOK=0.05
PEAK_CACHE_HIT_CNY_PER_MTOK=0.10
OFF_PEAK_CACHE_MISS_CNY_PER_MTOK=1.50
PEAK_CACHE_MISS_CNY_PER_MTOK=3.00
OFF_PEAK_OUTPUT_CNY_PER_MTOK=4.50
PEAK_OUTPUT_CNY_PER_MTOK=9.00
```

Images are tokenized and billed as input, with the captured visual-token ceiling around 384 tokens per image.

For the executable CNY100 hard-cap guard, the project deliberately uses the conservative expensive side:

```text
BUDGET_INPUT_RATE_CNY_PER_MTOK=3.00
BUDGET_OUTPUT_RATE_CNY_PER_MTOK=9.00
BUDGET_IMAGE_INPUT_TOKENS_PER_IMAGE=384
CACHE_DISCOUNT_CREDITED=NO
OFF_PEAK_DISCOUNT_CREDITED=NO
```

This inheritance is governed by `docs/reviews/PROVIDER_PRICING_FALLBACK_POLICY_V0_1.md`. It prevents a missing separately indexed experimental-model price page from blocking work when the same-family price relation is established, while still reserving against the more expensive applicable rate.

## Capability implications for this project

The model satisfies the project's hard minimum of direct visual K-line input. It must not be excluded merely because older standard-route documentation or standard V4 Flash/Pro material is text-only.

Two candidate-specific caveats remain relevant to the later fidelity probe:

1. **Experimental identity/drift:** the `-exp` model may change or be superseded. Transport evidence must preserve requested and provider-resolved model identity.
2. **Visual compression:** the approximately 384-token visual bound may degrade fine K-line labels, wick detail or dense chart structure. This is a reason to test Jianghe visual fidelity, not to exclude the candidate before testing.

Provider-side JSON Output / tool support exists, but a first-party strict JSON-Schema guarantee equivalent to the strongest Kimi surface is not assumed. The project strict normalizer remains the authoritative output boundary.

## Corrected candidate status

```text
KIMI_K3=CANDIDATE
DEEPSEEK_V4_FLASH_VISION_EXP=CANDIDATE__EXPERIMENTAL__DIRECT_VISUAL_API
MINIMAX_M3=CANDIDATE
FINAL_APPROVED_PROVIDER_SET=NOT_DECIDED
NO_PROVIDER_VERIFIED_BY_PROJECT_LIVE_CALL=YES
NO_PROVIDER_ADOPTED=YES
LIVE_CALLS=0
PAID_SPEND=0
```

This correction does not authorize external spend, outcome access, PRIMARY semantic freeze, Validation, historical Final, Shadow/Forward, broker access, or real money.

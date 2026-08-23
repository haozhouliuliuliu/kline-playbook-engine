# DeepSeek V4 Flash Vision Exp 第一方事实纠正 V0.1

> Status: `COMPLETE__PROVIDER_FACT_CORRECTED`
> Date: 2026-08-24
> Scope: correct only the time-sensitive DeepSeek provider/model fact in the 2026-08-24 provider refresh. This does not reopen the frozen pre-spend findings, start repair work, select a provider, or authorize paid calls.

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

The Owner was correct that this model had only just been released. The earlier provider refresh relied on a stale crawled `/models` page that pre-dated the August 21 launch and therefore incorrectly treated the model as not first-party-verifiable.

## First-party evidence

### 1. DeepSeek official Harness repository

DeepSeek's official repository `deepseek-ai/deepseek-harness` is current at commit:

```text
b150a551b8d465e31e418e1b2eaf5e79bbb7d28e
release: dsh@0.1.1-rc.2
2026-08-21T12:03:37Z
```

Its official `packages/llm/llm-deepseek/README.md` states that the default model catalog includes:

```yaml
- id: deepseek-v4-flash-vision-exp
  name: DeepSeek-V4-Flash-Vision-Exp
  inputModalities: [text, image]
```

and explicitly says omission of the custom model list advertises `deepseek-v4-flash`, `deepseek-v4-pro`, and the image-capable `deepseek-v4-flash-vision-exp`, with a 1,000,000-token context-window default.

First-party repository:
- https://github.com/deepseek-ai/deepseek-harness
- https://github.com/deepseek-ai/deepseek-harness/blob/b150a551b8d465e31e418e1b2eaf5e79bbb7d28e/packages/llm/llm-deepseek/README.md

### 2. DeepSeek API vision documentation / launch material

Current launch-day material points to DeepSeek's first-party vision guide:

- https://api-docs.deepseek.com/guides/vision
- https://api-docs.deepseek.com/quick_start/pricing/

The current documented model behavior is:

```text
MODEL_ID=deepseek-v4-flash-vision-exp
MODALITY=text+image -> text
API_SURFACES=Chat Completions, Responses API, Anthropic-compatible Messages
IMAGE_INPUT_PATHS=base64, public URL, Files API file_id
IMAGE_BILLING=ordinary input tokens
IMAGE_TOKEN_CEILING=up to 384 tokens per image after provider resizing
FILES_API=AVAILABLE
CONTEXT≈1,000,000 tokens
MAX_OUTPUT≈384,000 tokens
```

The launch is explicitly experimental. That affects drift/deprecation governance, but experimental status is not itself a reason to exclude the model from a bounded fidelity comparison.

## Pricing correction

Launch-day material reports that Vision Exp uses the same rate card as V4 Flash. The currently reported direct CNY schedule is:

```text
OFF_PEAK_CACHE_HIT_CNY_PER_MTOK=0.05
PEAK_CACHE_HIT_CNY_PER_MTOK=0.10
OFF_PEAK_CACHE_MISS_CNY_PER_MTOK=1.50
PEAK_CACHE_MISS_CNY_PER_MTOK=3.00
OFF_PEAK_OUTPUT_CNY_PER_MTOK=4.50
PEAK_OUTPUT_CNY_PER_MTOK=9.00
```

Images are tokenized and billed as input, with a published ceiling around 384 image tokens per image. This makes the candidate materially cheaper than the other retained visual providers for image-heavy probe traffic.

These are time-sensitive prices and must still be fetched from the live first-party rate authority again when implementing BSP-005 and immediately before any separately authorized paid call.

## Capability implications for this project

The model now satisfies the project's hard minimum of **direct visual K-line input**. It therefore must not be excluded merely because standard V4 Flash/Pro are text-only.

Two candidate-specific caveats remain relevant to the later fidelity probe:

1. **Experimental identity/drift:** the `-exp` model may change or be superseded. The provider transport must preserve requested and provider-resolved model identity rather than treating the slug as an immutable research snapshot.
2. **Visual compression:** DeepSeek documents aggressive image-token bounding, approximately up to 384 visual tokens per image after resizing. Fine K-line labels or dense chart detail may be degraded. This is a reason to test actual Jianghe visual fidelity, not a reason to exclude the candidate before testing.

Provider-side JSON Output / tool support is documented, but a first-party strict JSON-Schema guarantee equivalent to the strongest OpenAI/xAI/Kimi surfaces is not established by this correction. The existing strict project runtime normalizer remains the authoritative output boundary regardless of provider.

## Corrected candidate status

```text
OPENAI_GPT_5_6_SOL=CANDIDATE
XAI_GROK_4_6=CANDIDATE
KIMI_K3=CANDIDATE
DEEPSEEK_V4_FLASH_VISION_EXP=CANDIDATE__EXPERIMENTAL__FIRST_PARTY_DOCUMENTED_VISUAL_API

FINAL_APPROVED_PROVIDER_SET=NOT_DECIDED
NO_PROVIDER_VERIFIED_BY_PROJECT_LIVE_CALL=YES
NO_PROVIDER_ADOPTED=YES
```

This correction invalidates only the earlier DeepSeek exclusion. It does not alter BSP-001..005 / RSP-001..002, does not authorize implementation work beyond ordinary state correction, and does not authorize external spend.
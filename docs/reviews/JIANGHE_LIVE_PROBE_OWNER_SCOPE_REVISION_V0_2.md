# 江河真实模型 Fidelity Probe — Owner 范围修订 V0.2

> Status: `OWNER_SCOPE_REVISED__FINAL_PROVIDER_SET_PENDING`
> Date: 2026-08-23
> This file supersedes the executable scope proposed in `JIANGHE_BOUNDED_LIVE_MODEL_FIDELITY_PROBE_APPROVAL_PACKAGE_V0_1.md`. V0.1 remains historical evidence only and is **not authorized for execution**.

## Owner binding decisions

```text
ANTHROPIC_CLAUDE=EXCLUDED_BY_OWNER
GOOGLE_GEMINI=EXCLUDED_BY_OWNER
TOTAL_HARD_SPEND_CAP_CNY=100.00
LIVE_CALLS_BEFORE_DOUBLE_AUDIT=0
PAID_SPEND_BEFORE_FINAL_OWNER_PROVIDER_SELECTION=0
OUTCOME_ACCESS=NO
PRIMARY_FREEZE=NO
```

The Owner has not yet approved a final provider/model set. The following models are only under cost/capability consideration:

```text
OPENAI_GPT_5_6_SOL=CANDIDATE_RETAINED_FROM_PRIOR_PACKAGE
XAI_GROK_4_6=CANDIDATE_UNDER_OWNER_CONSIDERATION
KIMI_K3=CANDIDATE_UNDER_OWNER_CONSIDERATION
DEEPSEEK_V4_FLASH_VISION_EXP=CANDIDATE_UNDER_OWNER_CONSIDERATION__EXPERIMENTAL
```

No model/provider is VERIFIED or ADOPTED by this document.

## Current external reconnaissance — cost/capability only

### xAI Grok 4.6

Official xAI documentation checked 2026-08-23:
- https://docs.x.ai/developers/models/grok-4.6
- https://docs.x.ai/developers/pricing
- https://x.ai/news/grok-4-6

Current published direct-API short-context rates:

```text
INPUT_USD_PER_1M=2.00
CACHED_INPUT_USD_PER_1M=0.50
OUTPUT_USD_PER_1M=6.00
LONG_CONTEXT_THRESHOLD=200K
LONG_CONTEXT_INPUT_USD_PER_1M=4.00
LONG_CONTEXT_OUTPUT_USD_PER_1M=12.00
MODALITIES=TEXT_IMAGE_INPUT__TEXT_OUTPUT
STRUCTURED_OUTPUTS=SUPPORTED
```

### Kimi K3

Official Kimi documentation checked 2026-08-23:
- https://www.kimi.ai/help/kimi-api/api-model-selection
- https://www.kimi.ai/help/kimi-api/api-model-capabilities
- https://www.kimi.ai/resources/kimi-k3-pricing
- https://www.kimi.ai/help/kimi-api/api-pricing

Current published rates:

```text
INPUT_CACHE_HIT_USD_PER_1M=0.30
INPUT_CACHE_MISS_USD_PER_1M=3.00
OUTPUT_USD_PER_1M=15.00
CONTEXT=1M
NATIVE_VISUAL_UNDERSTANDING=YES
JSON_MODE=YES
STRUCTURED_OUTPUTS=YES
K3_ALWAYS_REASONING=YES
VISION_IMAGE_BILLING=1024_INPUT_TOKENS_PER_IMAGE
```

### DeepSeek V4-Flash-Vision-Exp

Current release evidence points to DeepSeek's 2026-08-21 official release URL:
- https://api-docs.deepseek.com/news/news260821/
- https://api-docs.deepseek.com/quick_start/pricing/
- https://api-docs.deepseek.com/updates/

The current web cache of DeepSeek's direct pricing/change-log pages is stale relative to the Aug-21 vision release and does not yet expose the new model in the fetched table. Multiple current sources linking the official release report:

```text
MODEL_ID=deepseek-v4-flash-vision-exp
STATUS=EXPERIMENTAL
TEXT_IMAGE_INPUT=YES
TEXT_OUTPUT=YES
CONTEXT=1M
MAX_OUTPUT=384K
IMAGE_TOKEN_CEILING=384_INPUT_TOKENS_PER_IMAGE
RESPONSES_API=REPORTED_SUPPORTED
JSON_OUTPUT=REPORTED_SUPPORTED
```

Current reported direct-DeepSeek RMB rates after the vision release are:

```text
OFF_PEAK_CACHE_HIT_CNY_PER_1M=0.05
OFF_PEAK_CACHE_MISS_CNY_PER_1M=1.50
OFF_PEAK_OUTPUT_CNY_PER_1M=4.50
PEAK_CACHE_HIT_CNY_PER_1M=0.10
PEAK_CACHE_MISS_CNY_PER_1M=3.00
PEAK_OUTPUT_CNY_PER_1M=9.00
```

These DeepSeek rates are `PROVISIONAL_PENDING_FRESH_FIRST_PARTY_RECHECK` because the directly fetched official pricing page is not yet synchronized in the current cache. No spend decision may rely on them until the exact direct-API rate card is rechecked immediately before implementation.

The 384-token image ceiling is economically attractive but may reduce fine visual detail. For this project, low price is not sufficient: K-line visual fidelity must be measured before any production consideration.

## Cost policy

The Owner's hard cap is RMB, not USD:

```text
TOTAL_HARD_SPEND_CAP_CNY=100.00
NO_AUTOMATIC_BUDGET_EXTENSION=YES
NO_PROVIDER_SPECIFIC_OVERRUN=YES
```

The final probe plan must allocate the RMB 100 cap across only the finally approved providers. The original V0.1 `USD 100` envelope is superseded and prohibited.

## Additional Owner-required pre-spend reviews

Before any provider adapter is allowed to make a real request, two additional read-only review rounds are required against the same frozen `main` commit:

1. whole-system / architecture / redundancy review;
2. fine-grained regression / dead-code / authority-hygiene / cost-path review.

These reviews are not permitted to alter the repository while auditing. Findings are consolidated first; if repair is genuinely required, there will be one batched repair decision rather than repeated rolling fixes.

## Final state

```text
FINAL_APPROVED_PROVIDER_SET=NOT_DECIDED
LIVE_MODEL_PROVIDER_PROBE=BLOCKED_PENDING_OWNER_REQUESTED_DOUBLE_AUDIT_AND_FINAL_PROVIDER_SELECTION
LIVE_CALLS=0
PAID_SPEND=0
OUTCOME_ACCESS=NO
PRIMARY_FREEZE=NO
```

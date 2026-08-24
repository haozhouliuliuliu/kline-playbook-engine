# PROVIDER PRICING FALLBACK POLICY V0.1

Status: `OWNER_APPROVED__PRE_SPEND_BUDGET_GUARD_POLICY`
Date: 2026-08-24
Scope: provider/model pricing authority used only for pre-call worst-case budget reservation.

## Purpose

A newly released or experimental model must not be excluded from the Jianghe fidelity probe merely because a separately indexed exact tariff page is temporarily unavailable, provided its billing unit and a conservative same-vendor price bound can be established.

This policy does not authorize any paid call, provider adoption, outcome access, broker action, or real-money trading.

## Owner-approved fallback rule

When the exact target-model tariff is unavailable or not separately indexed, the spend guard may use a public tariff from the same vendor and same model family or a clearly comparable sibling tier only when all of the following hold:

1. the target model's billing unit is known and executable before network;
2. the fallback relationship is explicitly documented by the provider or confirmed by the Owner from current provider material;
3. the guard selects the more expensive applicable rate rather than the cheapest plausible rate;
4. cache-hit, off-peak, launch, promotional, coupon, prepaid-plan, or other discounts are not credited unless they are unavoidable parts of the published standard tariff;
5. image or other multimodal billing is independently bounded rather than silently treated as free;
6. the fallback source, target model, selected rate and rationale are committed to repository evidence with a bounded validity window.

If the billing unit itself cannot be bounded, or no defensible same-vendor relationship exists, the request remains fail-closed before network.

## Current application

### DeepSeek V4 Flash Vision Exp

Owner reconfirmed that `deepseek-v4-flash-vision-exp` has the same base performance and price as V4 Flash, with multimodal input added. The project therefore uses the V4 Flash peak/cache-miss schedule as the conservative spend guard:

```text
INPUT_CNY_PER_MTOK=3.00
OUTPUT_CNY_PER_MTOK=9.00
CACHE_OR_OFFPEAK_DISCOUNT_CREDITED=NO
IMAGE_INPUT_BOUND=384_INPUT_TOKENS_PER_IMAGE
```

The performance relationship is a provider/Owner-level fact. It is not a project Jianghe-fidelity `VERIFIED` result.

### MiniMax M3

Current first-party pay-as-you-go pricing publishes CNY token rates directly. For the spend guard the project deliberately selects the more expensive standard `>512k` input tier:

```text
INPUT_CNY_PER_MTOK=4.20
OUTPUT_CNY_PER_MTOK=16.80
CACHE_DISCOUNT_CREDITED=NO
IMAGE_BILLING=INPUT_TOKENS
```

The exact serialized multimodal request is already included in the conservative input upper-bound policy, so no invented fixed image-token conversion is introduced.

### Kimi K3

Kimi K3 uses its exact current target rate and therefore does not require fallback pricing. Current first-party help also states each vision image is billed as a fixed 1024 input tokens.

## Safety invariants

```text
TOTAL_HARD_SPEND_CAP_CNY=100.00
AUTOMATIC_SEMANTIC_RETRY=FORBIDDEN
PROVIDER_LOCAL_BUDGET_BYPASS=FORBIDDEN
UNKNOWN_BILLING_UNIT=FAIL_CLOSED
STALE_RATE_AUTHORITY=FAIL_CLOSED
PAID_CALL_AUTHORIZATION=SEPARATE_OWNER_GATE
```

This policy is a budget-conservatism rule only. It must not be used to infer model quality, fidelity, provider verification, or provider adoption.

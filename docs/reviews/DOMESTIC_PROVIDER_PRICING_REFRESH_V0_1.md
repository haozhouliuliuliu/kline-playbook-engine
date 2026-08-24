# DOMESTIC PROVIDER PRICING REFRESH V0.1

Status: `COMPLETE__THREE_TARGET_SPEND_GUARDS_READY__PAID_CALLS_STILL_NOT_AUTHORIZED`
Date: 2026-08-24
Scope: Kimi K3, DeepSeek V4 Flash Vision Exp, MiniMax M3
Outcome/PnL access: NO
Live provider calls: 0
Paid spend: CNY 0
Tool decision: USE_EXISTING

## Conclusion

The three Owner-confirmed domestic implementation targets now have executable conservative pre-call cost bounds under the existing single shared CNY100 ledger.

This removes provider-specific pricing lookup as a technical blocker. It does **not** authorize any provider call, verify Jianghe fidelity, select a winner, or adopt a provider/model.

## Owner pricing fallback rule

Authority: `docs/reviews/PROVIDER_PRICING_FALLBACK_POLICY_V0_1.md`.

When an exact experimental/new target tariff is not separately indexed, the project may use a same-vendor same-family/sibling-tier public tariff as a conservative fallback. The hard guard uses the more expensive applicable rate and credits no cache, off-peak, launch or promotional discount.

Fallback pricing may replace an unavailable exact tariff. It may not invent an unknown billing unit.

## Executable rate cards

### Kimi K3

```text
MODEL=kimi-k3
INPUT_CNY_PER_MTOK=20.00
OUTPUT_CNY_PER_MTOK=100.00
IMAGE_BILLING_MODE=FIXED_INPUT_TOKENS_PER_IMAGE
FIXED_INPUT_TOKENS_PER_IMAGE=1024
PRICING_BASIS=EXACT_TARGET_RATE
```

### DeepSeek V4 Flash Vision Exp

```text
MODEL=deepseek-v4-flash-vision-exp
DIRECT_VISUAL=YES
INPUT_CNY_PER_MTOK=3.00
OUTPUT_CNY_PER_MTOK=9.00
IMAGE_BILLING_MODE=FIXED_INPUT_TOKENS_PER_IMAGE
FIXED_INPUT_TOKENS_PER_IMAGE=384
PRICING_BASIS=V4_FLASH_SAME_PRICE_INHERITANCE__OWNER_RECONFIRMED
CACHE_OR_OFFPEAK_DISCOUNT_CREDITED=NO
```

The Owner reconfirmed current direct image support and the same price/base-performance relationship to V4 Flash, with multimodality added. That performance statement remains a provider/Owner-level fact, not a project fidelity `VERIFIED` result.

### MiniMax M3

```text
MODEL=MiniMax-M3
INPUT_CNY_PER_MTOK=4.20
OUTPUT_CNY_PER_MTOK=16.80
IMAGE_BILLING_MODE=INPUT_TOKENS
PRICING_BASIS=EXACT_M3_PAYGO__MORE_EXPENSIVE_GT_512K_TIER
DISCOUNT_CREDITED=NO
```

For M3 the pre-network guard does not invent a fixed image-token number. The exact serialized multimodal request includes the base64 image data, and the existing conservative `UTF8 payload bytes x2 + 8192` policy is used as the input-token upper bound. This is deliberately pessimistic.

## Runtime changes

`src/jianghe_prespend_runtime.py` now:

1. accepts exact spend-guard rate cards and Owner-approved conservative same-family inheritance;
2. loads fixed-per-image and ordinary-input-token image billing modes;
3. preserves unknown billing modes as fail-closed;
4. uses MiniMax's current `max_completion_tokens` request field;
5. keeps the committed Owner paid-call authorization artifact as a separate mandatory gate;
6. keeps one shared CNY100 ledger with no provider-local bypass;
7. keeps zero automatic semantic retries.

## Verification

A branch-only deterministic materialization gate executed:

```text
apply exact asserted source patch
python -m py_compile src/jianghe_prespend_runtime.py tests/test_jianghe_prespend_repair.py
python -m unittest tests.test_jianghe_prespend_repair -v
python -m unittest discover -s tests -v
git diff --check
```

The temporary patch applicator and workflow delete themselves only after all steps succeed. Both are absent from the final repair branch, and the final runtime/test blobs contain the intended materialized changes.

Adversarial coverage includes:

- DeepSeek inherited peak-rate card loads with CNY3/CNY9 and 384 fixed image tokens;
- MiniMax high-tier card loads with CNY4.20/CNY16.80 and `INPUT_TOKENS` image billing;
- MiniMax payload uses `max_completion_tokens`;
- DeepSeek and MiniMax can pass pricing/bounds validation but, with no credential, cancel before the HTTP seam and spend CNY0;
- CNY100 remains the maximum shared ledger cap;
- previous authorization, context, structured-input, evidence and runtime fail-closed tests remain in the full suite.

## Gates unchanged

```text
PAID_MODEL_SPEND=NOT_AUTHORIZED
LIVE_CALLS=0
PAID_SPEND=0
OUTCOME_ACCESS=NO
PRIMARY_SEMANTIC_FREEZE=NOT_REQUESTED
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY=NOT_AUTHORIZED
NO_PROVIDER_VERIFIED_BY_PROJECT_LIVE_CALL=YES
NO_PROVIDER_ADOPTED=YES
```

The next normal step after integration is to compute and commit the exact CNY100 qualification/stability funnel, then present that bounded plan to the Owner for a **separate explicit paid-call authorization**.

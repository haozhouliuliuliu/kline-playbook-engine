# PROVIDER PRICING FALLBACK POLICY V0.1

Status: OWNER_APPROVED__PRESPEND_COST_POLICY
Date: 2026-08-24
Scope: Jianghe real-model fidelity probe spend guard only
Hard project ceiling: CNY 100 total
Paid-call authorization: NOT GRANTED by this policy

## Decision

The project must not stall merely because an experimental/new target model lacks a separately indexed exact price page when a sufficiently close same-vendor pricing basis is available.

Pricing authority selection order is:

1. exact current first-party target-model tariff;
2. explicit first-party statement that the target inherits another model/tier tariff;
3. same-vendor, same-family or sibling-tier public tariff approved by the Owner as a conservative fallback.

When a fallback is used, the hard budget guard MUST use the more expensive applicable public tier/rate. Cache-hit discounts, off-peak discounts, temporary launch discounts, promotional credits and optimistic assumptions MUST NOT reduce the reserved worst-case cost.

## Non-negotiable safety boundary

Fallback pricing may substitute for an unavailable exact tariff. It may NOT invent an unknown billing unit.

Before a provider can be spend-eligible, the project must still know enough to upper-bound the charge before network access, for example:

- text/output billed by tokens;
- image billed as input tokens, or a conservative fixed per-image token ceiling;
- any required currency conversion basis.

If the billing unit itself cannot be bounded, the request remains fail-closed before network.

Every rate card must bind its repository pricing authority identity, provider/model, endpoint, currency, selected conservative rates, image-billing mode, validity window, authority URLs, and the pricing-basis/fallback rule used.

## Current application

### Kimi K3

Use the exact current Kimi K3 CNY tariff already captured by repository authority. Do not credit cache discounts in the hard-cap reservation. Each image is reserved as 1024 input tokens under the captured Kimi image-billing authority.

### DeepSeek V4 Flash Vision Exp

Owner reconfirmed on 2026-08-24 that `deepseek-v4-flash-vision-exp` directly accepts images, has the same price and base performance as V4 Flash, and adds multimodal capability. This is consistent with the existing project correction authority that records the Vision Exp model and its launch-day V4 Flash pricing relationship.

For the spend guard, inherit V4 Flash pricing and deliberately use the expensive peak/cache-miss side:

- input: CNY 3.00 / MTok;
- output: CNY 9.00 / MTok;
- image tokens: billed as input tokens;
- conservative visual ceiling: 384 input tokens per image.

No cache-hit or off-peak discount is credited.

The statement that product/base performance matches Flash and adds multimodality is a provider/Owner-level product fact. It is NOT a project fidelity `VERIFIED` or `ADOPTED` result. Real Jianghe fidelity still requires the later governed probe.

### MiniMax M3

Use the current first-party M3 token tariff, but reserve against the more expensive >512K tier even when the actual request is smaller:

- input: CNY 4.20 / MTok;
- output: CNY 16.80 / MTok.

M3 accepts image input and the language model is token-billed. Because a separate fixed image-token conversion is not required for this mode, the spend guard must cover the exact serialized multimodal request (including base64 image bytes) with the repository's conservative payload-token upper-bound policy. No separate optimistic image discount is allowed.

## Gates unchanged

This policy does NOT:

- authorize any paid API call;
- verify or adopt any provider/model;
- open outcome/PnL access;
- freeze PRIMARY semantics;
- open Validation or historical Final;
- authorize Shadow/Forward, broker access or real money;
- raise the shared CNY 100 hard cap.

A committed Owner paid-call authorization artifact remains a separate mandatory gate.

TOOL_DECISION=USE_EXISTING

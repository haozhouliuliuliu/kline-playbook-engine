# DEEPSEEK PROVIDER PRICING REFERENCE — 2026-08-27

Status: `REFERENCE_ONLY__ACTIVE_VISION_EXP_EXACT_TARIFF_NOT_VERIFIED`

Checked: `2026-08-27`

Official source checked: DeepSeek API Docs — Models & Pricing (`https://api-docs.deepseek.com/zh-cn/quick_start/pricing/`).

## Public tariff visible on the official page

For public model `deepseek-v4-flash`, the official page currently lists prices per 1M tokens:

- input, cache hit: CNY `0.02` / 1M tokens;
- input, cache miss: CNY `1.00` / 1M tokens;
- output: CNY `2.00` / 1M tokens.

The official page states billing is based on token usage and prices may change.

## Project model caveat

Current project model:

`deepseek-v4-flash-vision-exp`

The checked public pricing page does **not** list a separate exact tariff for `deepseek-v4-flash-vision-exp`.

Therefore:

`PUBLIC_DEEPSEEK_V4_FLASH_TARIFF != VERIFIED_EXACT_VISION_EXP_TARIFF`

The project must not multiply public flash price by token usage and call the result the exact provider bill unless the active model's tariff is independently verified.

## Cost-governance rule

For paid project work:

1. seal exact governed wake/request count before execution;
2. record provider/model and all available token-usage fields per request;
3. use the public tariff only as a labeled reference estimate where appropriate;
4. derive empirical request-cost estimates from the first real smoke/full-replay ledger and any provider billing evidence available to the Owner;
5. bind every paid slot to an explicit Owner-approved CNY ceiling plus hard request-count ceiling;
6. apply stop-before-next-request logic using accumulated usage/cost plus a conservative next-call reserve;
7. if billing is asynchronous or the exact active-model tariff is unknown, treat the hard request cap as the primary enforceable limit.

The historical rough assumption `~CNY 0.10 per call` remains a planning assumption only.

Likewise, `CU + RB ~CNY 400` is not a verified project fact and does not authorize spend.
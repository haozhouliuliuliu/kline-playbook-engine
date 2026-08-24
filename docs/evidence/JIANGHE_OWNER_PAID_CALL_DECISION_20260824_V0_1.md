# JIANGHE OWNER PAID-CALL DECISION 2026-08-24 V0.1

Status: `OWNER_AUTHORIZED__BOUNDED_NON_OUTCOME_RMB100_FIDELITY_FUNNEL`
Decision time: 2026-08-24T08:36:00+08:00
Owner decision text in chat: `授权`
Authority interpreted against: `docs/reviews/JIANGHE_RMB100_REAL_MODEL_FIDELITY_FUNNEL_V0_1.md`

## Authorized scope

The Owner explicitly authorizes the bounded real-model Jianghe fidelity funnel previously presented by the project brain.

```text
PAID_MODEL_API_CALLS=AUTHORIZED_WITHIN_THIS_CLOSED_WORLD_SCOPE
PROVIDERS=KIMI_K3,DEEPSEEK_V4_FLASH_VISION_EXP,MINIMAX_M3
TOTAL_API_SPEND_HARD_CAP_CNY=100.00
STAGE_A_FIRST=YES
AUTOMATIC_SEMANTIC_RETRY=FORBIDDEN
AUTOMATIC_BUDGET_EXTENSION=FORBIDDEN
OUTCOME_OR_PNL_ACCESS=NO
VALIDATION_ACCESS=LOCKED
HISTORICAL_FINAL_ACCESS=LOCKED
SHADOW_FORWARD=NOT_AUTHORIZED
BROKER_ACCESS=NOT_AUTHORIZED
REAL_MONEY_TRADING=NOT_AUTHORIZED
PRIMARY_SEMANTIC_FREEZE=NOT_AUTHORIZED
```

The CNY100 amount is an API-consumption ceiling, not a spending target. Unused budget remains unspent.

## Funding / recharge boundary

This authorization does **not** authorize an unknown or open-ended account recharge/top-up.

Before any provider requires a new recharge, prepaid purchase, subscription, or other separate cash funding action, the project must determine the specific required amount and return to the Owner for that cash action. Existing account balance, granted credits, or already-funded balance may be consumed only through the authorized API funnel and remains subject to the same CNY100 API-spend hard cap.

No credential, payment instrument, secret, or account identifier belongs in repository evidence.

## Execution sequence

1. Recheck current rate-card freshness and current provider funding/balance requirements.
2. Commit the closed-world paid-call authorization artifact.
3. Execute Stage A only first.
4. Record request identity, provider/model identity, raw response, usage, latency, budget reconciliation, and fidelity evidence after every call.
5. Stop any provider immediately on a fatal qualification failure.
6. Commit Stage-A evidence and ranking before any Stage-B call.
7. Stage B, if reached, remains within the already authorized CNY100 funnel and cannot exceed its fixed envelopes.

This decision does not make any model `VERIFIED` or `ADOPTED`; those statuses depend on the resulting governed fidelity evidence.

# JIANGHE REPLAY V0.1 PROVIDER SMOKE — OWNER RESUME DECISION

Status: `OWNER_APPROVED__RESUME_EXACT_EXISTING_SLOT`

Date: `2026-08-27`

Work package: `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

## Owner instruction

The Owner explicitly resumes the previously approved exact three-call DeepSeek provider smoke after the governance/context-continuity repair.

This decision removes only the temporary `OWNER_HOLD_BEFORE_FIRST_CALL` introduced by:

`docs/reviews/PROJECT_GOVERNANCE_OWNERSHIP_REPAIR_OWNER_DECISION_2026-08-27.md`

It does not create a new research design and does not widen the paid slot.

## Exact resumed boundary

The resumed authority remains exactly the existing payment/execution authority:

`docs/reviews/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_EXECUTION_AUTHORITY_2026-08-27.md`

Therefore:

```text
AUTHORIZED_PAID_SLOT = THREE_CALL_PROVIDER_SMOKE
MAX_PROVIDER_CALLS = 3
MAX_RETRIES = 0
MAX_SPEND_CNY = 3.00
FULL_V0_1_1998_CALL_REPLAY_AUTHORIZED = FALSE
```

The same three sealed governed wakes, same model, same four causal chart images per request, same forced restart after successful call 2, same one-wake/one-request rule and same call-4 prohibition remain binding.

## Reseal against current main

Owner resume is being integrated from canonical `main` HEAD:

`0043b97642a0f6b85e9a9f978298bd6aa64841e3`

The governance repair changed authority/navigation/state files but did not change the provider-smoke execution-critical paths. The executable code binding therefore remains the already verified execution-code commit:

`547a14e10e24dbb2eab01aa6d4e35b151aa1ddcb`

The project guard compares the current execution-critical working-tree blobs against that commit before any credential/network capability is created.

The machine-readable authority is resealed from `REVOKED` back to `ACTIVE` without changing any other frozen slot field. Deterministic authority identity returns to:

`8583694f4164c7983f40d784bf21e5582b1ae7c96ca7b1fef902abf155fae905`

## Secret location

The DeepSeek credential is read only at execution time from the Owner workstation Windows current-user environment variable:

`DEEPSEEK_API_KEY`

The secret value must never be printed, logged, committed or pasted into authority/chat.

## Still locked

This resume does **not** authorize:

- a fourth provider call;
- any retry or replacement wake;
- full V0.1 1998-call replay;
- post-V0.1 paid CU/RB replay;
- SHADOW/PAPER;
- broker/account action;
- real money;
- learning/policy promotion;
- permanent risk-rule change.

After the exact three-call smoke completes or fails closed, the slot is consumed/closed and another real provider attempt requires a new explicit Owner paid authority.

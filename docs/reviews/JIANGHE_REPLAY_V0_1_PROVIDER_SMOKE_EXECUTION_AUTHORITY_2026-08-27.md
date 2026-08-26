# JIANGHE REPLAY V0.1 PROVIDER SMOKE — OWNER PAYMENT / EXECUTION AUTHORITY

Status: `APPROVED_FOR_EXECUTION`

Date: `2026-08-27`

Work package: `SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_V0_1`

## Owner payment confirmation

The Owner has confirmed payment and execution for one exact, sealed provider-smoke slot.

```
OWNER_PAYMENT_CONFIRMATION = TRUE

AUTHORIZED_PAID_SLOT =
THREE_CALL_PROVIDER_SMOKE

MAX_PROVIDER_CALLS = 3

MAX_RETRIES = 0

MAX_SPEND_CNY = 3.00

FULL_V0_1_1998_CALL_REPLAY_AUTHORIZED = FALSE
```

This authority covers exactly:

`JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT`

It must not be interpreted as any larger paid permission.

## Exact execution facts

- provider: `deepseek`
- model: `deepseek-v4-flash-vision-exp`
- Harness version: `0.1.1-rc.2`
- Harness commit: `b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`
- project transport patch: `integrations/deepseek-harness/`
- provider endpoint: official DeepSeek paid production endpoint only
- retry policy: `maxRetries = 0`
- smoke wakes: the three sealed first-governed wakes (`call_1`, `call_2`, `call_3`) from the frozen machine authority
- images per call: exactly `4` (causal 4H / 1H / 15m / 5m PNGs)
- one governed wake -> exactly one provider model request
- forced project-owned restart after successful call 2 before call 3
- call 4 forbidden
- cost guard executes before each next request; stop before exceeding `CNY 3.00`

## Hard boundaries (not authorized)

- full V0.1 `1998`-call replay: `NO`
- fourth provider call: `NO`
- retry: `NO`
- replacement wake: `NO`
- outcome-driven re-ask: `NO`
- post-V0.1 CU paid replay: `NO`
- RB paid replay: `NO`
- SHADOW: `NO`
- PAPER: `NO`
- broker/account: `NO`
- real money: `NO`
- learning/policy promotion: `NO`
- permanent risk rule change: `NO`

## Machine authority

The machine-readable executable authority has been switched from
`PENDING_OWNER_PAYMENT_CONFIRMATION` to `ACTIVE`:

- file: `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_SLOT.json`
- `status = ACTIVE`
- `owner_payment_confirmation = true`
- `max_spend_cny = 3.00`
- `max_provider_calls = 3`
- `max_retries = 0`
- `full_replay_authorized = false`
- `full_replay_1998_calls_authorized = false`
- `execution_code_commit = 547a14e10e24dbb2eab01aa6d4e35b151aa1ddcb` (includes the provider-smoke runner wake-binding verification and export-before-close fixes)
- `authority_identity = 8583694f4164c7983f40d784bf21e5582b1ae7c96ca7b1fef902abf155fae905`
  (recomputed by the project's deterministic authority-generation mechanism;
  all frozen product/contract/slice/wake/model/Harness/prompt/context/renderer
  identities and guards are unchanged)

## Adjudication boundary

This three-call smoke is an execution-path integrity probe only. It does not
evaluate profitability and does not adjudicate Jianghe trading quality.

After the smoke completes (3/3 success or fail-closed), this paid slot is
consumed/closed. Any future real provider retry or re-run requires a new Owner
paid authority. The next step after a successful smoke is limited to:

`SMOKE ADJUDICATION / PREPARE OWNER DECISION FOR FULL SEALED V0.1`

The full `1998`-call replay remains unauthorized under this authority.

## Outcome — slot consumed and closed

Executed `2026-08-27`. Result: `STOPPED FAIL-CLOSED`.

- real provider calls attempted: `1` (call 1 only; stopped during normalization)
- real provider calls normalized: `0`
- retries: `0`; hidden second requests: `0`; call 4: `NO`
- root cause: provider emitted `numeric_claims` as a JSON object instead of the
  frozen `JIANGHE_RUNTIME_RESPONSE_V0_1` array schema
- fail-closed evidence: `docs/evidence/JIANGHE_REPLAY_V0_1_PROVIDER_SMOKE_FAILCLOSED_2026-08-27.md`

The machine authority has been transitioned to the terminal `REVOKED` status:

`status = REVOKED`

`authority_identity = 6622351c707538c0db881cf69e1dbd388ae2f1c339d478e67932c65d247b3ce9`

`THIS THREE-CALL PAID SLOT CANNOT BE ACCIDENTALLY RE-RUN`

Any new real provider retry/re-run requires a new Owner paid authority.

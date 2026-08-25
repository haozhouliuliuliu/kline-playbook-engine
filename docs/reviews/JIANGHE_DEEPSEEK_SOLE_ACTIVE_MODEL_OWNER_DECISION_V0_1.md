# Jianghe DeepSeek Model Authority

As of: `2026-08-26`

Status:

`OWNER_DECISION__DEEPSEEK_ONLY`

## Current model authority

`MODEL_SOURCE = DEEPSEEK_ONLY`

`CURRENT_MODEL = deepseek-v4-flash-vision-exp`

This is the sole active model source and model line for the current Jianghe persistent-trader product.

A change of model source or a material DeepSeek model-generation change requires a new explicit Owner decision.

## Current engineering requirements

The DeepSeek integration preserves these mandatory guards:

- `STRICT_OUTPUT_ENUM_ENFORCEMENT`
- `NO_4H_EXACT_VOLUME_RECONCILIATION`

The current implementation sequence is governed by `PROJECT_DIRECTION.md` and `CURRENT_STATE.md`.

## Current locks

- `PAID_CALLS = PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- validation/holdout = locked
- shadow = locked
- broker/account = locked
- real money = locked

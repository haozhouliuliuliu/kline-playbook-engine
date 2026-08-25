# CURRENT_STATE

As of: `2026-08-25`

## Canonical project phase

- `PHASE = RESEARCH_FOUNDATION`
- `ARCHITECTURE = Skeleton_v1.0_PLUS_JIANGHE_AI_TRADER_DECISION_LAYER_V0_1`
- `RESEARCH_DIRECTION = HUMAN_PLAYBOOK_FIRST`
- Jianghe V1 remains the sole current trading-knowledge source.
- No broker, account, shadow, validation, holdout, or real-money lane is unlocked.

## Historical foundation

Historical three-provider matched evidence and the Downloaded-Kline V0.1 pilot remain immutable evidence.

Historical shared paid-research ledger before the V0.2 final-chance round:

`PROJECT_ACCOUNTED_CNY = 3.1609662`

Hard cap:

`100.00 CNY`

The provider-neutral lower-stack clarification contract remains frozen as:

- `DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2`
- schema identity `0057b11939c71f10fa7094db119f5b280e74edd13cb2bb7d40cc29a418c4c68a`

## V0.2 final-chance protocol and execution closure

Owner decision authority:

`docs/reviews/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_OWNER_DECISION_V0_2.md`

Frozen test stack:

`4H / 1H / 15m / 5m`

4H remains background / state / key-zone / location / remaining-space context only and uses:

`SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1`

Materialized plan:

`docs/evidence/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_V0_2.json`

- `PILOT_PLAN_IDENTITY = 34640cd6de7dd9f5069ad902e0e7c125b78aa7a5400475b4531ba318f3469340`
- `PLAN_FILE_SHA256 = f72d16567b0f481551eda85cda3f5e67ba7c31a5504943e80e148540830cecbc`

Remote live ledger:

`refs/heads/final-chance-live-state-v0-2`

Final remote ledger head:

`899f578cda41e534fe584d027bab3cd15c5fbb1d`

Execution facts:

- `TOTAL_NETWORK_ATTEMPTS = 12`
- `TOTAL_TERMINAL_ATTEMPTS = 12`
- `UNIQUE_ATTEMPTED_SLOTS = 12`
- `AUTOMATIC_RETRIES = 0`
- `AUTOMATIC_NEXT = 0`
- DeepSeek: 4 attempts, 3 scoreable + 1 output-contract not-scoreable
- MiniMax: 4 attempts, 4 scoreable
- Kimi: 4 attempts, 2 scoreable + 1 not-scoreable + 1 infrastructure failure
- Kimi slot 12 failed with `RemoteDisconnected` after a real network attempt; no retry was performed.

Current shared hard-cap accounting after the round:

`PROJECT_ACCOUNTED_CNY = 20.9075330`

The original frozen three-provider PK remains:

`THREE_PROVIDER_PK_VERDICT = NOT_FINALIZABLE`

Historical attempt identities remain immutable.

## Current model selection

Historical adjudication:

`docs/reviews/JIANGHE_FINAL_CHANCE_V0_2_DS_MINIMAX_OWNER_ADJUDICATION_V0_1.md`

Later binding Owner decision:

`docs/reviews/JIANGHE_DEEPSEEK_SOLE_ACTIVE_MODEL_OWNER_DECISION_V0_1.md`

Current state:

- DeepSeek `deepseek-v4-flash-vision-exp` = `SOLE_ACTIVE_MODEL_CANDIDATE_FOR_JIANGHE`
- MiniMax `MiniMax-M3` = `EXCLUDED_FROM_JIANGHE_MODEL_CANDIDATE_SET`
- Kimi `kimi-k3` = `EXCLUDED_FROM_JIANGHE_MODEL_CANDIDATE_SET`
- MiniMax is no longer a reserve/fallback candidate.
- No further MiniMax/Kimi selection-testing budget is authorized under the current direction.

This freezes the current Jianghe model-selection direction. It does not by itself authorize production, shadow, broker, account, or real-money use of DeepSeek.

## Current work package

`CURRENT_WORK_PACKAGE = JIANGHE_DEEPSEEK_SELECTED_LANE_HARDENING_V0_1`

Required narrow hardening:

1. exact output enum enforcement;
2. explicit prohibition / validation against 4H exact cross-timeframe volume reconciliation.

No additional paid provider call is required for model selection.

## Paid-call state

- `PAID_CALLS = PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- no current executable paid slot exists;
- historical final-chance attempts may not be retried under consumed identities.

## Locks

- outcome access: `LOCKED`
- future access: `LOCKED`
- validation access: `LOCKED`
- holdout access: `LOCKED`
- shadow execution: `LOCKED`
- broker/account action: `LOCKED`
- real money: `LOCKED`

## Exact next work

1. harden the selected DeepSeek lane against the two observed mechanical failure modes;
2. run focused regression tests plus normal repository CI;
3. do not run more provider calls merely to re-litigate model selection;
4. any new broader validation/research design, including a persistent DeepSeek trading workspace/harness direction, remains a separate Owner product/research gate until explicitly approved.

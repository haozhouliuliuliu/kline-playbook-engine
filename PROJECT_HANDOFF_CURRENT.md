# PROJECT_HANDOFF_CURRENT

As of: `2026-08-25`

This file is a handoff snapshot and must be read after the current formal authorities.

## Current breakpoint

The Downloaded-Kline Final-Chance V0.2 live round has executed.

Frozen test stack remains:

`4H / 1H / 15m / 5m`

4H representation:

`SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1`

4H semantic role:

`BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`

## Execution closure

Remote ledger:

`refs/heads/final-chance-live-state-v0-2`

Final remote ledger head:

`899f578cda41e534fe584d027bab3cd15c5fbb1d`

- 12 unique slots attempted;
- 12 network attempts;
- 12 terminal records;
- zero retries;
- zero automatic-next behavior;
- Kimi fourth slot ended in `INFRASTRUCTURE_FAILURE` after the network attempt;
- no Kimi retry occurred;
- current project hard-cap accounting: `20.9075330 CNY`;
- `NEXT_EXPLICIT_PAID_SLOT = NONE`.

The original frozen three-provider PK remains `NOT_FINALIZABLE` because one Kimi capability answer is absent.

## Current model decision

Historical correctness review:

`docs/reviews/JIANGHE_FINAL_CHANCE_V0_2_DS_MINIMAX_OWNER_ADJUDICATION_V0_1.md`

Binding later Owner decision:

`docs/reviews/JIANGHE_DEEPSEEK_SOLE_ACTIVE_MODEL_OWNER_DECISION_V0_1.md`

Current provider/model state:

- DeepSeek `deepseek-v4-flash-vision-exp` = `SOLE_ACTIVE_MODEL_CANDIDATE_FOR_JIANGHE`
- MiniMax `MiniMax-M3` = `EXCLUDED_FROM_JIANGHE_MODEL_CANDIDATE_SET`
- Kimi `kimi-k3` = `EXCLUDED_FROM_JIANGHE_MODEL_CANDIDATE_SET`
- MiniMax is no longer reserve/fallback.
- No further MiniMax/Kimi selection-testing budget is authorized under the current direction.

Why DeepSeek remains active:

- stronger handling of the new 4H/session semantics across the four matched cases;
- MiniMax repeatedly treated completed civil-grid 4H context as incomplete or introduced unsupported session/liquidity and 4H-volume interpretations;
- DeepSeek's observed problems are narrow mechanical defects: one bad 4H volume reconciliation and one strict enum-format failure.

## Current work package

`JIANGHE_DEEPSEEK_SELECTED_LANE_HARDENING_V0_1`

Current authorized engineering continuation:

1. exact output enum enforcement;
2. blocking 4H exact cross-timeframe volume reconciliation;
3. focused tests + normal CI.

No additional provider call is needed for model selection.

A persistent DeepSeek futures-trading workspace/harness or broader historical replay program is a new product/research stage and needs explicit Owner direction before implementation/large-scale execution.

## Locks

- outcome/future: locked
- validation/holdout: locked
- shadow: locked
- broker/account: locked
- real money: locked
- `PAID_CALLS = PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`

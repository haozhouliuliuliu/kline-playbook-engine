# Jianghe DeepSeek Sole Active Model Owner Decision V0.1

As of: `2026-08-25`

## Status

`OWNER_DECISION__MODEL_SELECTION_SCOPE_FROZEN`

## Decision

After the completed V0.2 final-chance execution and the formal DeepSeek-vs-MiniMax correctness adjudication, the Owner made the following follow-on provider-selection decision:

- DeepSeek `deepseek-v4-flash-vision-exp` = `SOLE_ACTIVE_MODEL_CANDIDATE_FOR_JIANGHE`
- MiniMax `MiniMax-M3` = `EXCLUDED_FROM_JIANGHE_MODEL_CANDIDATE_SET`
- Kimi `kimi-k3` = `EXCLUDED_FROM_JIANGHE_MODEL_CANDIDATE_SET`
- MiniMax is no longer a reserve/fallback candidate and receives no further Jianghe selection-testing budget under the current product direction.
- Kimi remains excluded and receives no retry.

This decision supersedes the earlier *future selection status* in `JIANGHE_FINAL_CHANCE_V0_2_DS_MINIMAX_OWNER_ADJUDICATION_V0_1.md`, where MiniMax was retained as a verified reserve. It does not alter or rewrite the historical V0.2 evidence or that adjudication's factual findings.

## Rationale

The Owner accepts the project-brain conclusion that DeepSeek's observed defects are primarily narrow, mechanically hardenable failure modes:

1. strict enum/output-contract discipline;
2. prohibited 4H exact cross-timeframe volume reconciliation.

MiniMax's observed defects were instead more closely tied to market/context interpretation under the newly introduced 4H/session representation, including completed-bucket maturity confusion, unsupported session/liquidity interpretation, and inappropriate 4H-volume inference.

The project therefore treats DeepSeek's error profile as more suitable for continued engineering hardening and long-run Jianghe specialization.

## What this does and does not freeze

This decision freezes the **current Jianghe model-selection direction**: do not re-open DeepSeek-vs-MiniMax-vs-Kimi selection without a new explicit Owner decision.

It does **not** claim that DeepSeek is already production-approved for shadow, broker, account, or real-money execution. Those stages remain separately gated by research, validation, safety, and execution authorities.

If a materially new future model generation is ever considered, that is a new research/model-selection decision rather than an automatic revival of MiniMax or Kimi.

## Current next work

Continue only with the DeepSeek lane:

1. harden strict enum output behavior;
2. harden against 4H exact cross-timeframe volume reconciliation;
3. design the next research/validation stage only after explicit Owner approval;
4. no provider calls are authorized by this decision.

## Locks

- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- `PAID_CALLS = PAUSED`
- outcome/future access = locked
- validation/holdout = locked
- shadow = locked
- broker/account = locked
- real money = locked

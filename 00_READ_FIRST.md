# 00_READ_FIRST

Canonical repository: `haozhouliuliuliu/kline-playbook-engine`

GitHub current `main` is the only dynamic project fact source.

## Fresh-conversation takeover order

Read in this order:

1. `00_READ_FIRST.md`
2. `PROJECT_BRAIN_RUNTIME_BRIEF.md`
3. `CURRENT_STATE.md`
4. `OWNER_COLLABORATION_CONTRACT.md`
5. `ARCHITECTURE_BASELINE.md`
6. `AGENTS.md`
7. `CROSS_PROJECT_OPERATING_CONTRACT.md`
8. `TOOL_REGISTRY.md`
9. current work-package authorities:
   - `docs/reviews/JIANGHE_FINAL_CHANCE_V0_2_DS_MINIMAX_OWNER_ADJUDICATION_V0_1.md`
   - `docs/reviews/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_OWNER_DECISION_V0_2.md`
   - `docs/reviews/JIANGHE_HIGHER_TIMEFRAME_BOUNDED_EVIDENCE_REVIEW_V0_2.md`
   - `docs/evidence/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_SPEC_V0_2.json`
   - `docs/evidence/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_V0_2.json`
10. live execution evidence only if relevant:
   - branch `refs/heads/final-chance-live-state-v0-2`
   - ledger `final-chance-live-ledger-v0-2.json`
11. paid / execution authorities only if relevant:
   - `docs/evidence/JIANGHE_PAID_CALL_AUTHORIZATION_CURRENT.json`
12. `KNOWN_LIMITATIONS_AND_TECH_DEBT.md`
13. `PROJECT_HANDOFF_CURRENT.md` **last**

## Current takeover headline

The V0.2 `4H / 1H / 15m / 5m` final-chance round has executed.

Execution closure:

- 12 unique slots attempted;
- 12 network attempts;
- 0 retries;
- remote ledger head `899f578cda41e534fe584d027bab3cd15c5fbb1d`;
- Kimi slot 12 ended in a preserved infrastructure failure;
- original three-provider frozen PK therefore remains `NOT_FINALIZABLE`.

The Owner then narrowed the current provider selection to DeepSeek vs MiniMax and excluded Kimi from the current selection without retry.

Post-execution adjudication:

- DeepSeek `deepseek-v4-flash-vision-exp` = `SELECTED_FOR_NEXT_RESEARCH_LANE`
- MiniMax `MiniMax-M3` = `VERIFIED_RUNNER_UP_RESERVE`
- Kimi `kimi-k3` = `EXCLUDED_FROM_CURRENT_SELECTION`
- permanent provider adoption is not frozen.

Current work package:

`JIANGHE_DEEPSEEK_SELECTED_LANE_HARDENING_V0_1`

The narrow observed DeepSeek defects to harden are:

1. strict output enum compliance;
2. prohibition of 4H exact cross-timeframe volume reconciliation.

Current paid state:

`PAID_CALLS = PAUSED`

`NEXT_EXPLICIT_PAID_SLOT = NONE`

No more provider call is required merely to choose DeepSeek vs MiniMax.

## Fresh-conversation first report

On a brand-new conversation, perform a read-only takeover first and report:

- current main HEAD;
- current phase/state;
- current locks;
- final-chance live-attempt closure;
- current provider selection status;
- exact next explicit slot, if any;
- contradictions found.

Do not perform a paid provider call during takeover.

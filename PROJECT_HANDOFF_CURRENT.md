# PROJECT_HANDOFF_CURRENT

As of: `2026-08-25`

This file is a handoff snapshot and must be read after the current formal authorities.

## Current breakpoint

The Owner-approved V0.2 final-chance protocol has been designed and implemented offline.

Frozen protocol:

`4H / 1H / 15m / 5m`

4H engineering representation:

`SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1`

4H semantic role:

`BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY`

Generic lower-stack input contract remains unchanged:

`DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2`

Provider set:

1. DeepSeek benchmark
2. MiniMax M3 final matched opportunity
3. Kimi K3 final matched opportunity

Target:

`4 fresh real cases x 3 providers = 12 matched calls`

## What is complete

- bounded higher-timeframe evidence review;
- Owner decision authority;
- machine-readable fail-closed plan spec;
- session-aware 4H builder semantics;
- fresh-case deterministic selection design excluding historical V0.1 partitions;
- portable reconstruction / verification design;
- pre-frozen correctness domination rule;
- unit tests for 4H break semantics, incomplete-bucket exclusion, plan-spec identity, and elimination logic.

## What is not complete

`MATERIALIZED_PLAN = NONE`

The accepted canonical corpus is local data and is not stored in GitHub. Therefore the four fresh cases have not yet been produced in this lane.

No new provider call has occurred.

## Paid state

- historical project accounted CNY: `3.1609662`
- hard cap: `100.00 CNY`
- `PAID_CALLS = PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- automatic retry: forbidden
- automatic next slot: forbidden

The existing paid-call authorization is necessary but not sufficient to create a slot.

## Exact next step

On the host containing the accepted canonical corpus, run:

`python tools/build_jianghe_downloaded_kline_final_chance_plan_v0_2.py --materialize`

Then:

1. verify the emitted four-case plan with `--check-plan`;
2. run the repository offline test suite;
3. commit/review the portable materialized evidence;
4. refresh current ledger, paid authorization, and provider pricing;
5. perform pre-send payload/budget review;
6. freeze the first explicit paid slot only if every gate passes.

Do not call any provider before that pre-send review.

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
- unit tests for 4H break semantics, incomplete-bucket exclusion, plan-spec identity, and elimination logic;
- four fresh cases materialized and verified (`MATERIALIZED__AWAITING_PRESEND_REVIEW`).

## What is not complete

The V0.2 materialized plan exists and is verified (`MATERIALIZED__AWAITING_PRESEND_REVIEW`).

Still not complete:

- paid authorization refresh
- shared ledger refresh
- provider pricing / rate-card refresh
- payload / budget review
- worst-case CNY reservation
- explicit first paid-slot freeze

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

The four-case plan is materialized and verified. The next step is pre-send review only:

1. refresh current ledger, paid authorization, and provider pricing;
2. perform pre-send payload/budget review;
3. reserve worst-case CNY;
4. freeze the first explicit paid slot only if every gate passes.

Do not call any provider before that pre-send review.

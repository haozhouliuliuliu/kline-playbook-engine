# Jianghe Downloaded-Kline Final-Chance Owner Decision V0.2

Status: `OWNER_APPROVED__OFFLINE_IMPLEMENTATION_AUTHORIZED`
Decision date: `2026-08-25`

This authority records the Owner-approved continuation after the downloaded-Kline V0.1 forensic review and the higher-timeframe bounded evidence review.

## Approved research direction

The next fresh matched pilot may use:

`4H / 1H / 15m / 5m`

The 4H addition is approved only as a **test-protocol context layer** supported by current Jianghe source evidence. It is not a permanent Jianghe doctrine.

Daily / weekly / monthly are not included in this round because the bounded current evidence review did not establish a sufficiently explicit role for them.

## Approved provider comparison

The fresh pilot will compare, case-for-case:

1. `DEEPSEEK / deepseek-v4-flash-vision-exp` — current benchmark.
2. `MINIMAX / MiniMax-M3` — final matched opportunity.
3. `KIMI / kimi-k3` — final matched opportunity.

Every provider must receive the same case material and the same question for a given case. Historical V0.1 or V0.3 attempt identities must not be reused.

## Fresh-case requirement

The V0.2 pilot must use four fresh deterministic real-market cases from the accepted canonical corpus.

Historical V0.1 selected partitions are excluded when the historical plan authority is available. Selection is metadata-only and must not use future, outcome, PnL, validation, holdout, or shadow information.

## 4H engineering representation

The approved project test representation is:

`SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1`

Meaning:

- use the official session authority;
- group official expected 1m trading minutes by civil four-hour grid;
- non-trading breaks do not count as missing constituents;
- never combine different official trading days in one bucket;
- expose only complete, already-visible buckets at the decision time;
- 4H is excluded from the exact cross-timeframe volume-reconciliation rule in `DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2`.

This is a deterministic **project representation** for the experiment. It is not asserted to be Jianghe's personal chart-vendor bar-boundary convention.

## Input-contract preservation

The existing generic input contract remains unchanged:

- version: `DOWNLOADED_KLINE_INPUT_CONTRACT_V0_2`
- schema identity: `0057b11939c71f10fa7094db119f5b280e74edd13cb2bb7d40cc29a418c4c68a`

4H semantics are carried in a separate higher-timeframe descriptor. The lower `1H / 15m / 5m` projection continues to use the existing V0.2 contract.

## Evaluation rule frozen before provider calls

Correctness severities:

`NONE < MINOR < MATERIAL < CRITICAL`

Frozen dimensions include market facts, latest closed bar, cross-timeframe relations, correct 4H role, Jianghe source fidelity, family/setup interpretation, breakout/invalidation logic, invented fixed rules or unsupported Jianghe claims, and uncertainty / WAIT / NO_TRADE discipline.

A candidate may be automatically eliminated only when it is **dominated by DeepSeek**:

- the candidate is not better on any frozen correctness dimension; and
- it has either a worse worst-severity or more `MATERIAL/CRITICAL` errors.

`MIXED`, `PARITY`, or any candidate correctness advantage does not authorize automatic elimination.

Provider choice priority remains:

`JIANGHE_CORRECTNESS_AND_CAPABILITY -> ACTUAL_CNY -> ACTUAL_TIME`

## Spend / execution boundary

This decision authorizes offline implementation under the already-governed paid-research program. It does not manufacture a paid slot.

Until a real four-case plan is materialized from the accepted local canonical corpus and passes pre-send review:

- `PAID_CALLS = PAUSED`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`
- automatic retry is forbidden
- automatic next-slot progression is forbidden

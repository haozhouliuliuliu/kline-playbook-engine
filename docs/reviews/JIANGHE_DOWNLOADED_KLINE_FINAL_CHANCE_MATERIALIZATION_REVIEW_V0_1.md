# Jianghe Downloaded-Kline Final-Chance Materialization Review V0.1

Status: `MATERIALIZED__AWAITING_PRESEND_REVIEW`
Review date: `2026-08-25`
Plan authority: `docs/evidence/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_V0_2.json`
Plan spec authority: `docs/evidence/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_SPEC_V0_2.json`

This review records only facts that have already occurred and been verified offline. It does not authorize any paid provider call.

## Verification summary

- `MATERIALIZATION = PASS`
- `PLAN_SPEC_CHECK = PASS`
- `CHECK_PLAN = PASS`
- `PILOT_PLAN_IDENTITY = 34640cd6de7dd9f5069ad902e0e7c125b78aa7a5400475b4531ba318f3469340`
- `PLAN_FILE_SHA256 = f72d16567b0f481551eda85cda3f5e67ba7c31a5504943e80e148540830cecbc`
- `STATUS = MATERIALIZED__AWAITING_PRESEND_REVIEW`
- `NEXT_EXPLICIT_PAID_SLOT = null`

## Plan structure (verified)

- `samples = 4` (fresh deterministic real-market cases)
- `provider_slots = 12`
- `products = 4` distinct: `ni`, `cu`, `ag`, `rb` (all SHFE)
- provider counts: `DEEPSEEK = 4`, `MINIMAX = 4`, `KIMI = 4`
- per-sample timeframe counts: `4H = 2`, `1H = 3`, `15m = 12`, `5m = 36`
- `HISTORICAL_V01_PARTITION_REUSE = NO`
- `HISTORICAL_ATTEMPT_IDENTITY_REUSE = NO`
- `OUTCOME_ACCESS = NO`
- `FUTURE_ACCESS = NO`
- `VALIDATION_ACCESS = LOCKED`
- every provider slot: `execution_eligible = false`
- `AUTOMATIC_RETRY = FORBIDDEN`
- `AUTOMATIC_NEXT_SLOT = FORBIDDEN`
- `next_explicit_paid_slot = null`

## Fresh cases

| sample_id | product | exchange | trading_day | decision_time |
|---|---|---|---|---|
| `DKL-FC-001` | `ni` | `SHFE` | `2024-02-23` | `2024-02-23T15:00:00+08:00` |
| `DKL-FC-002` | `cu` | `SHFE` | `2024-07-31` | `2024-07-31T15:00:00+08:00` |
| `DKL-FC-003` | `ag` | `SHFE` | `2025-05-21` | `2025-05-21T15:00:00+08:00` |
| `DKL-FC-004` | `rb` | `SHFE` | `2025-10-20` | `2025-10-20T15:00:00+08:00` |

Canonical corpus identity:

`1d03fd230b4603715b7ea01e13c4e21eb30b8118d0270571d136b17c886774a8`

Each case carries a distinct `parquet_artifact_identity`, so no historical V0.1 partition is reused.

## Local canonical-host baseline

- `FULL_SUITE = 1424 tests / 0 failures / 0 errors`
- `COMPILEALL = PASS`
- `DIFF_CHECK = PASS`
- `JIANGHE_TARGETED_TESTS = 5/5 PASS`

The previous 8 local full-suite failures were a Windows CRLF/LF checkout-byte old deterministic-artifact problem (working-tree byte reads produced different hashes from the committed LF blobs). This was fixed by PR #33 and merged into main.

## Scope boundary

`MATERIALIZATION` only closes the gate: "the local canonical corpus has not yet produced a plan". It does not authorize paid calls.

## Still required before any paid call

1. paid authorization refresh
2. shared ledger refresh
3. provider pricing / rate-card refresh
4. payload review
5. worst-case CNY reservation
6. explicit slot freeze

## Resource accounting

- `PROVIDER_CALLS = 0`
- `PAID_CALLS = 0`
- `NEXT_EXPLICIT_PAID_SLOT = NONE`

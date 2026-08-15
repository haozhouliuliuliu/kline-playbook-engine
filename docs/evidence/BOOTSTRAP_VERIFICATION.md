# Bootstrap Verification Evidence

Date: 2026-08-15
Phase: PROJECT_BOOTSTRAP
Architecture: Skeleton v1.0 (unchanged)

## Scope

This package performs only the cheapest deterministic feasibility checks requested by `CURRENT_STATE.md`:

1. China futures trading-day / night-session semantics can be represented explicitly without treating calendar date as trading day.
2. Broker events can be handled with unique `event_id`, idempotency, deduplication, explicit out-of-order handling, and trading-day sequence conventions.
3. `TradingState` can remain the sole mutable real-time owner while `Ledger` remains append-only factual history.

This is a feasibility fixture, not frozen production protocol and not a trading strategy.

## External factual basis used for the time/session fixture

Primary exchange sources inspected:

- Shanghai Futures Exchange Trading Rules: defines a trading day with continuous trading as beginning in the previous workday's continuous-trading period and ending with the current day's day session.
  https://edu.shfe.com.cn/TradingAssistant/RulesIntroduction/518.html
- SHFE notice for cast aluminum alloy futures (2025-05-26): gives day sessions and a continuous-trading period of 21:00 to next-day 01:00, and states that the continuous session is not held on the first workday before statutory holidays.
  https://www.shfe.com.cn/publicnotice/notice/202505/t20250526_827862.html

The test fixture uses these semantics only to prove the normalized representation. It does **not** claim that all Chinese exchanges/products share one schedule. Exact product/exchange calendars remain data-substrate metadata to be sourced and versioned later.

## Deterministic policies exercised

### Session semantics
- Session intervals are explicit timezone-aware facts.
- Each interval carries its authoritative `trading_day`.
- A Friday-night/after-midnight interval may map to Monday's trading day when that interval is explicitly present.
- Missing sessions are not inferred from weekday patterns.

### Broker event feasibility policy
- Identical repeat of the same `event_id` is idempotently ignored.
- Reuse of an `event_id` with different payload fails closed.
- Higher sequence arriving early is buffered.
- Once the missing sequence arrives, contiguous buffered events apply in sequence.
- An unseen stale sequence fails closed rather than being silently replayed.

These are bootstrap feasibility semantics only; production broker/exchange-specific sequence and reconciliation rules remain subject to later formal design and real adapter evidence.

### TradingState / Ledger boundary
- Only `TradingState` mutates current positions.
- State application emits immutable transition facts.
- `Ledger` appends those facts and exposes immutable records.
- Repeated broker events produce no duplicate transition.

## Tool/dependency result

- New trading framework installed: NO
- New third-party Python dependency installed: NO
- Broker connection used: NO
- Strategy mining/backtest run: NO
- Real-money action: NO
- Project tool status changed: NO

Canonical verification command:

`python -m unittest discover -s tests -v`

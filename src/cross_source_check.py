"""SHFE official cross-source checker for the canonical corpus.

For each comparable concrete-contract/trading-day record, classifies:

- MATCH: all comparable daily fields agree exactly;
- MISMATCH: at least one comparable field differs (durable evidence, never
  silently discarded);
- NOT_COMPARABLE: semantics cannot be compared (e.g., missing OI on one side);
- NOT_AVAILABLE: no official daily row exists for this contract/day.

Daily fields compared: open, high, low, close, volume, and open interest where
semantics match.  Conflicting providers are never averaged.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from hashlib import sha256
import json
from typing import Iterable


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class DailyAggregate:
    """Daily aggregate derived from normalized bars for one contract/day."""

    contract: str
    trading_day: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    open_interest: Decimal | None

    def __post_init__(self) -> None:
        prices = (self.open, self.high, self.low, self.close)
        if any(type(v) is not Decimal or not v.is_finite() or v <= 0 for v in prices):
            raise ValueError("daily aggregate OHLC must be positive finite Decimals")
        if self.low > min(self.open, self.close) or self.high < max(self.open, self.close) or self.low > self.high:
            raise ValueError("daily aggregate OHLC is inconsistent")
        if type(self.volume) is not int or self.volume < 0:
            raise ValueError("daily aggregate volume must be a non-negative integer")
        if self.open_interest is not None and (
            type(self.open_interest) is not Decimal or not self.open_interest.is_finite() or self.open_interest < 0
        ):
            raise ValueError("daily aggregate open interest must be a non-negative finite Decimal")


@dataclass(frozen=True)
class OfficialDailyRow:
    """Official SHFE daily quotation row for one contract/day."""

    contract: str
    trading_day: date
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int
    open_interest: Decimal | None


def aggregate_daily_from_bars(contract: str, trading_day: date, bars: Iterable) -> DailyAggregate:
    """Aggregate normalized bars (with .open/.high/.low/.close/.volume) to daily."""
    bar_list = sorted(bars, key=lambda b: b.completed_bar.start)
    if not bar_list:
        raise ValueError("cannot aggregate an empty bar set")
    oi_end = None
    # Use the last bar's close_oi (end-of-day open interest) when available.
    last = bar_list[-1]
    if hasattr(last, "open_interest_end") and last.open_interest_end is not None:
        oi_end = last.open_interest_end
    return DailyAggregate(
        contract=contract,
        trading_day=trading_day,
        open=bar_list[0].open,
        high=max(b.high for b in bar_list),
        low=min(b.low for b in bar_list),
        close=last.close,
        volume=sum(int(b.volume) for b in bar_list if b.volume is not None),
        open_interest=oi_end,
    )


def compare_daily(aggregate: DailyAggregate, official: OfficialDailyRow | None) -> dict:
    """Classify one contract/day comparison."""
    if official is None:
        return {
            "contract": aggregate.contract,
            "day": aggregate.trading_day.isoformat(),
            "result": "NOT_AVAILABLE",
            "detail": "no official daily row for this contract/day",
        }
    if official.contract != aggregate.contract:
        raise ValueError("official row contract disagrees with aggregate")
    fields = ["open", "high", "low", "close", "volume"]
    mismatches: list[str] = []
    for field in fields:
        a = getattr(aggregate, field)
        b = getattr(official, field)
        if str(a) != str(b):
            mismatches.append(field)
    oi_comparable = aggregate.open_interest is not None and official.open_interest is not None
    if oi_comparable:
        if str(aggregate.open_interest) != str(official.open_interest):
            mismatches.append("open_interest")
    if mismatches:
        return {
            "contract": aggregate.contract,
            "day": aggregate.trading_day.isoformat(),
            "result": "MISMATCH",
            "mismatched_fields": mismatches,
            "aggregate": {f: str(getattr(aggregate, f)) for f in fields},
            "official": {f: str(getattr(official, f)) for f in fields},
            "aggregate_open_interest": str(aggregate.open_interest) if aggregate.open_interest is not None else None,
            "official_open_interest": str(official.open_interest) if official.open_interest is not None else None,
        }
    if not oi_comparable:
        return {
            "contract": aggregate.contract,
            "day": aggregate.trading_day.isoformat(),
            "result": "NOT_COMPARABLE",
            "detail": "open interest semantics not comparable on both sides",
        }
    return {
        "contract": aggregate.contract,
        "day": aggregate.trading_day.isoformat(),
        "result": "MATCH",
        "fields": {f: str(getattr(aggregate, f)) for f in fields},
        "open_interest": str(aggregate.open_interest),
    }


def cross_source_summary(comparisons: Iterable[dict]) -> dict:
    comps = list(comparisons)
    counts = {"MATCH": 0, "MISMATCH": 0, "NOT_COMPARABLE": 0, "NOT_AVAILABLE": 0}
    for c in comps:
        counts[c["result"]] += 1
    return {
        "compared_records": len(comps),
        "counts": counts,
        "summary_identity": canonical_hash(comps),
    }

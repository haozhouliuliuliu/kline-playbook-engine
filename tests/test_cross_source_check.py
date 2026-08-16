"""Tests for the SHFE official cross-source checker."""

from __future__ import annotations

import unittest
from datetime import date
from decimal import Decimal

from src.cross_source_check import (
    DailyAggregate,
    OfficialDailyRow,
    aggregate_daily_from_bars,
    compare_daily,
    cross_source_summary,
)


class _Bar:
    """Mirrors NormalizedHistoricalBar's surface used by aggregation."""

    def __init__(self, start, open_, high, low, close, volume, oi_end=None):
        self.completed_bar = type("CB", (), {"start": start})()
        self.open = open_
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.open_interest_end = oi_end


class DailyAggregateTests(unittest.TestCase):
    def test_aggregate_from_bars(self) -> None:
        from datetime import datetime
        from zoneinfo import ZoneInfo

        CN = ZoneInfo("Asia/Shanghai")
        bars = [
            _Bar(datetime(2025, 6, 18, 9, 0, tzinfo=CN), Decimal("100"), Decimal("105"), Decimal("99"), Decimal("102"), 10, Decimal("50")),
            _Bar(datetime(2025, 6, 18, 9, 1, tzinfo=CN), Decimal("102"), Decimal("108"), Decimal("101"), Decimal("107"), 20, Decimal("52")),
        ]
        agg = aggregate_daily_from_bars("SHFE.au2508", date(2025, 6, 18), bars)
        self.assertEqual(agg.open, Decimal("100"))
        self.assertEqual(agg.high, Decimal("108"))
        self.assertEqual(agg.low, Decimal("99"))
        self.assertEqual(agg.close, Decimal("107"))
        self.assertEqual(agg.volume, 30)
        self.assertEqual(agg.open_interest, Decimal("52"))

    def test_empty_bars_fail(self) -> None:
        with self.assertRaises(ValueError):
            aggregate_daily_from_bars("SHFE.au2508", date(2025, 6, 18), [])


class CompareDailyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.agg = DailyAggregate(
            "SHFE.au2508", date(2025, 6, 18),
            Decimal("786.26"), Decimal("788.00"), Decimal("785.90"), Decimal("787.44"),
            1234, Decimal("1000"),
        )

    def test_match(self) -> None:
        official = OfficialDailyRow(
            "SHFE.au2508", date(2025, 6, 18),
            Decimal("786.26"), Decimal("788.00"), Decimal("785.90"), Decimal("787.44"),
            1234, Decimal("1000"),
        )
        self.assertEqual(compare_daily(self.agg, official)["result"], "MATCH")

    def test_mismatch_is_durable(self) -> None:
        official = OfficialDailyRow(
            "SHFE.au2508", date(2025, 6, 18),
            Decimal("786.26"), Decimal("788.00"), Decimal("785.90"), Decimal("787.44"),
            1200, Decimal("1000"),
        )
        result = compare_daily(self.agg, official)
        self.assertEqual(result["result"], "MISMATCH")
        self.assertIn("volume", result["mismatched_fields"])

    def test_not_available(self) -> None:
        result = compare_daily(self.agg, None)
        self.assertEqual(result["result"], "NOT_AVAILABLE")

    def test_not_comparable_when_oi_missing(self) -> None:
        agg = DailyAggregate(
            "SHFE.au2508", date(2025, 6, 18),
            Decimal("786.26"), Decimal("788.00"), Decimal("785.90"), Decimal("787.44"),
            1234, None,
        )
        official = OfficialDailyRow(
            "SHFE.au2508", date(2025, 6, 18),
            Decimal("786.26"), Decimal("788.00"), Decimal("785.90"), Decimal("787.44"),
            1234, None,
        )
        self.assertEqual(compare_daily(agg, official)["result"], "NOT_COMPARABLE")

    def test_summary_counts(self) -> None:
        official = OfficialDailyRow(
            "SHFE.au2508", date(2025, 6, 18),
            Decimal("786.26"), Decimal("788.00"), Decimal("785.90"), Decimal("787.44"),
            1234, Decimal("1000"),
        )
        summary = cross_source_summary([
            compare_daily(self.agg, official),
            compare_daily(self.agg, None),
        ])
        self.assertEqual(summary["counts"]["MATCH"], 1)
        self.assertEqual(summary["counts"]["NOT_AVAILABLE"], 1)
        self.assertEqual(len(summary["summary_identity"]), 64)


if __name__ == "__main__":
    unittest.main()

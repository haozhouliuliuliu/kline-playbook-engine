"""Tests for the governed metadata authority (canonical dataset)."""

from __future__ import annotations

import unittest
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.data_substrate import SessionMetadata, SessionWindow
from src.metadata_authority import (
    ContractSpec,
    ContractUniverseEntry,
    GovernedSource,
    ProductSessionSchedule,
    TradingCalendar,
    build_session_metadata,
    session_windows_for_trading_day,
)

CN = ZoneInfo("Asia/Shanghai")


def _source(cls: str = "OFFICIAL_AVAILABLE") -> GovernedSource:
    return GovernedSource(
        resource_identity="res",
        url="https://example.com/official",
        retrieved_at=datetime(2026, 8, 16, tzinfo=CN),
        artifact_sha256="a" * 64,
        schema_version="v1",
        classification=cls,
        effective_period_start=date(2024, 1, 1),
        effective_period_end=date(2025, 12, 31),
    )


class GovernedSourceTests(unittest.TestCase):
    def test_identity_is_deterministic(self) -> None:
        self.assertEqual(_source().identity(), _source().identity())

    def test_bad_classification_fails(self) -> None:
        with self.assertRaises(ValueError):
            _source(cls="NOT_REAL")

    def test_bad_hash_fails(self) -> None:
        with self.assertRaises(ValueError):
            GovernedSource(
                resource_identity="r", url="u", retrieved_at=datetime(2026, 1, 1, tzinfo=CN),
                artifact_sha256="zzz", schema_version="v", classification="OFFICIAL_AVAILABLE",
                effective_period_start=date(2024, 1, 1), effective_period_end=date(2024, 12, 31),
            )


class ContractSpecTests(unittest.TestCase):
    def test_spec_identity_binds_facts(self) -> None:
        spec = ContractSpec(
            "SHFE", "au", "AU", Decimal("0.02"), "yuan/gram", Decimal("1000"), "gram/lot",
            "yuan/gram", "1-12", "3", _source(),
        )
        self.assertEqual(len(spec.identity()), 64)
        other = ContractSpec(
            "SHFE", "au", "AU", Decimal("0.04"), "yuan/gram", Decimal("1000"), "gram/lot",
            "yuan/gram", "1-12", "3", _source(),
        )
        self.assertNotEqual(spec.identity(), other.identity())

    def test_bad_tick_fails(self) -> None:
        with self.assertRaises(ValueError):
            ContractSpec(
                "SHFE", "au", "AU", Decimal("0"), "yuan/gram", Decimal("1000"), "gram/lot",
                "yuan/gram", "1-12", "3", _source(),
            )


class CalendarTests(unittest.TestCase):
    def setUp(self) -> None:
        days = [date(2024, 1, 2) + timedelta(days=i) for i in range(5)]
        self.calendar = TradingCalendar("v1", days, _source())

    def test_trading_days_between(self) -> None:
        out = self.calendar.trading_days(date(2024, 1, 2), date(2024, 1, 4))
        self.assertEqual(out, (date(2024, 1, 2), date(2024, 1, 3), date(2024, 1, 4)))

    def test_previous_trading_day(self) -> None:
        self.assertEqual(self.calendar.previous_trading_day(date(2024, 1, 4)), date(2024, 1, 3))

    def test_identity(self) -> None:
        self.assertEqual(len(self.calendar.identity()), 64)


class SessionWindowTests(unittest.TestCase):
    def setUp(self) -> None:
        days = [date(2024, 6, 17) + timedelta(days=i) for i in range(5)]  # Mon-Fri
        self.calendar = TradingCalendar("v1", days, _source())
        self.schedule = ProductSessionSchedule(
            "SHFE", "cu", date(2024, 1, 1), date(2025, 12, 31),
            ((time(9, 0), time(10, 15)), (time(13, 30), time(15, 0))),
            (time(21, 0), time(1, 0)), timezone="Asia/Shanghai", source=_source(),
        )

    def test_night_window_belongs_to_trading_day(self) -> None:
        day = date(2024, 6, 18)  # Tuesday
        windows = session_windows_for_trading_day(self.calendar, self.schedule, "SHFE.cu2407", day)
        night = [w for w in windows if w.kind == "night"]
        self.assertEqual(len(night), 1)
        # night starts 21:00 previous trading day (Monday) and ends 01:00 on day
        self.assertEqual(night[0].start, datetime(2024, 6, 17, 21, 0, tzinfo=CN))
        self.assertEqual(night[0].end, datetime(2024, 6, 18, 1, 0, tzinfo=CN))
        self.assertEqual(night[0].trading_day, day)
        day_windows = [w for w in windows if w.kind == "day"]
        self.assertEqual(len(day_windows), 2)

    def test_night_closed_day_has_no_night_window(self) -> None:
        day = date(2024, 6, 18)
        windows = session_windows_for_trading_day(
            self.calendar, self.schedule, "SHFE.cu2407", day, night_closed_days=frozenset({day})
        )
        self.assertFalse(any(w.kind == "night" for w in windows))
        self.assertEqual(len([w for w in windows if w.kind == "day"]), 2)

    def test_non_trading_day_fails(self) -> None:
        with self.assertRaises(ValueError):
            session_windows_for_trading_day(self.calendar, self.schedule, "SHFE.cu2407", date(2024, 6, 16))

    def test_build_session_metadata(self) -> None:
        days = self.calendar.trading_days(date(2024, 6, 17), date(2024, 6, 19))
        meta = build_session_metadata(self.calendar, self.schedule, "SHFE.cu2407", days)
        self.assertIsInstance(meta, SessionMetadata)
        self.assertTrue(meta.version)

    def test_expected_bar_starts_count(self) -> None:
        days = self.calendar.trading_days(date(2024, 6, 18), date(2024, 6, 18))
        meta = build_session_metadata(self.calendar, self.schedule, "SHFE.cu2407", days)
        starts = meta.expected_bar_starts("SHFE", "SHFE.cu2407", date(2024, 6, 18), timedelta(minutes=1))
        # night 21:00 -> 01:00 = 240 min; day 09:00->10:15 = 75; 13:30->15:00 = 90
        self.assertEqual(len(starts), 240 + 75 + 90)

    def test_monday_without_previous_day_has_no_night(self) -> None:
        days = self.calendar.trading_days(date(2024, 6, 17), date(2024, 6, 17))
        meta = build_session_metadata(self.calendar, self.schedule, "SHFE.cu2407", days)
        starts = meta.expected_bar_starts("SHFE", "SHFE.cu2407", date(2024, 6, 17), timedelta(minutes=1))
        self.assertEqual(len(starts), 75 + 90)


class ContractUniverseEntryTests(unittest.TestCase):
    def test_entry(self) -> None:
        entry = ContractUniverseEntry(
            "SHFE", "cu", "SHFE.cu2407", date(2024, 1, 1), date(2024, 7, 15), _source()
        )
        self.assertEqual(len(entry.identity()), 64)

    def test_reversed_boundary_fails(self) -> None:
        with self.assertRaises(ValueError):
            ContractUniverseEntry(
                "SHFE", "cu", "SHFE.cu2407", date(2024, 7, 15), date(2024, 1, 1), _source()
            )


if __name__ == "__main__":
    unittest.main()

import unittest
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from src.data_substrate import BarQuality, CompletedBar, SessionMetadata, SessionWindow


CN = ZoneInfo("Asia/Shanghai")
DAY = date(2025, 6, 16)
FIVE_MINUTES = timedelta(minutes=5)


def at(hour: int, minute: int, day: date = DAY) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=CN)


class DataSubstrateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = SessionMetadata(
            "fixture-1",
            [
                SessionWindow("SHFE", "AD", DAY, at(21, 0, date(2025, 6, 13)), at(1, 0, date(2025, 6, 14)), "night"),
                SessionWindow("SHFE", "AD", DAY, at(9, 0), at(9, 10), "day"),
                SessionWindow("SHFE", "AD", DAY, at(10, 30), at(10, 40), "day"),
            ],
        )
        self.day_metadata = SessionMetadata(
            "fixture-1",
            [
                SessionWindow("SHFE", "AD", DAY, at(9, 0), at(9, 10), "day"),
                SessionWindow("SHFE", "AD", DAY, at(10, 30), at(10, 40), "day"),
            ],
        )

    def test_night_session_has_explicit_next_trading_day(self):
        self.assertEqual(self.metadata.trading_day_at("SHFE", "AD", at(21, 30, date(2025, 6, 13))), DAY)

    def test_scheduled_recess_is_not_reported_as_gap(self):
        observed = [at(9, 0), at(9, 5), at(10, 30), at(10, 35)]
        self.assertEqual(self.day_metadata.missing_bar_starts("SHFE", "AD", DAY, FIVE_MINUTES, observed), ())

    def test_missing_expected_bar_is_a_gap(self):
        observed = [at(9, 0), at(9, 5), at(10, 30)]
        self.assertEqual(
            self.day_metadata.missing_bar_starts("SHFE", "AD", DAY, FIVE_MINUTES, observed),
            (at(10, 35),),
        )

    def test_partial_and_reconnect_quality_remain_distinguishable(self):
        bar = CompletedBar("AD2508", DAY, at(9, 0), at(9, 5), at(9, 5), BarQuality(partial=True, reconnect_gap=True))
        self.assertTrue(bar.quality.partial)
        self.assertTrue(bar.quality.reconnect_gap)

    def test_unfinished_bar_cannot_be_visible_as_completed(self):
        with self.assertRaisesRegex(ValueError, "unfinished"):
            CompletedBar("AD2508", DAY, at(9, 0), at(9, 5), at(9, 4))

    def test_completed_bar_is_visible_only_at_its_availability_time(self):
        bar = CompletedBar("AD2508", DAY, at(9, 0), at(9, 5), at(9, 5))
        self.assertFalse(bar.is_visible_at(at(9, 4)))
        self.assertTrue(bar.is_visible_at(at(9, 5)))


if __name__ == "__main__":
    unittest.main()

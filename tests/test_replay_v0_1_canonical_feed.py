from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
import json
from pathlib import Path
import unittest

from src.replay_v0_1_canonical_feed import (
    ReplayMinuteBar,
    build_fixed_5m_preflight,
    governed_windows_for_days,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _authority():
    calendar_payload = json.loads((REPO_ROOT / "docs/evidence/CANONICAL_TRADING_CALENDAR.json").read_text(encoding="utf-8"))
    session_payload = json.loads((REPO_ROOT / "docs/evidence/CANONICAL_SESSION_SCHEDULES.json").read_text(encoding="utf-8"))
    calendar = tuple(
        date.fromisoformat(item)
        for year in sorted(calendar_payload["trading_days"])
        for item in calendar_payload["trading_days"][year]
    )
    night_closed = frozenset(
        date.fromisoformat(item)
        for values in calendar_payload["night_closed_trading_days"].values()
        for item in values
    )
    return calendar, night_closed, session_payload["products"]


def _candidate_replay_days(calendar):
    return tuple(day for day in calendar if date(2024, 4, 10) <= day <= date(2024, 5, 14))


def _minutes_for_windows(windows, *, contract="SHFE.cu2406", future_delay_minutes=0):
    rows = []
    for window in windows:
        for index in range(window.expected_minute_count):
            start = window.start + timedelta(minutes=index)
            end = start + timedelta(minutes=1)
            base = Decimal("70000") + Decimal(index)
            rows.append(
                ReplayMinuteBar(
                    product="cu",
                    concrete_contract=contract,
                    trading_day=window.trading_day,
                    start=start,
                    end=end,
                    available_at=end + timedelta(minutes=future_delay_minutes),
                    open=base,
                    high=base + Decimal("2"),
                    low=base - Decimal("2"),
                    close=base + Decimal("1"),
                    volume=Decimal("3"),
                    partition_identity=f"partition-{window.trading_day.isoformat()}",
                    session_authority_identity=window.session_authority_identity,
                )
            )
    return rows


class ReplayV01CanonicalFeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.calendar, cls.night_closed, cls.sessions = _authority()

    def test_current_cu_candidate_has_1998_governed_fixed_5m_wakes(self) -> None:
        replay_days = _candidate_replay_days(self.calendar)
        self.assertEqual(len(replay_days), 22)
        windows = governed_windows_for_days(
            product="cu",
            replay_days=replay_days,
            trading_calendar=self.calendar,
            night_closed_days=self.night_closed,
            session_schedule=self.sessions,
        )
        by_day = {day: 0 for day in replay_days}
        for window in windows:
            by_day[window.trading_day] += window.expected_wake_count
        self.assertEqual(by_day[date(2024, 5, 6)], 45)
        self.assertTrue(all(count == 93 for day, count in by_day.items() if day != date(2024, 5, 6)))
        self.assertEqual(sum(by_day.values()), 1998)

    def test_night_session_for_monday_uses_previous_trading_day_not_weekend_span(self) -> None:
        windows = governed_windows_for_days(
            product="cu",
            replay_days=(date(2024, 4, 15),),
            trading_calendar=self.calendar,
            night_closed_days=self.night_closed,
            session_schedule=self.sessions,
        )
        night = windows[0]
        self.assertEqual(night.kind, "night")
        self.assertEqual(night.start.isoformat(), "2024-04-12T21:00:00+08:00")
        self.assertEqual(night.end.isoformat(), "2024-04-13T01:00:00+08:00")

    def test_complete_real_schedule_day_builds_exact_93_wakes_without_bridging_breaks(self) -> None:
        day = date(2024, 4, 10)
        windows = governed_windows_for_days(
            product="cu",
            replay_days=(day,),
            trading_calendar=self.calendar,
            night_closed_days=self.night_closed,
            session_schedule=self.sessions,
        )
        rows = _minutes_for_windows(windows)
        preflight = build_fixed_5m_preflight(
            product="cu",
            concrete_contract="SHFE.cu2406",
            replay_days=(day,),
            windows=windows,
            minute_bars=rows,
        )
        self.assertEqual(preflight.minute_count, 465)
        self.assertEqual(preflight.expected_minute_count, 465)
        self.assertEqual(len(preflight.wake_bars), 93)
        self.assertEqual(preflight.expected_wake_count, 93)
        # 10:15-10:30 is a governed break; no five-minute bar may bridge it.
        pairs = {(item.start.isoformat(), item.end.isoformat()) for item in preflight.wake_bars}
        self.assertNotIn(("2024-04-10T10:15:00+08:00", "2024-04-10T10:20:00+08:00"), pairs)

    def test_missing_governed_minute_fails_closed(self) -> None:
        day = date(2024, 4, 10)
        windows = governed_windows_for_days(
            product="cu", replay_days=(day,), trading_calendar=self.calendar,
            night_closed_days=self.night_closed, session_schedule=self.sessions,
        )
        rows = _minutes_for_windows(windows)
        rows.pop(17)
        with self.assertRaisesRegex(ValueError, "missing 1 governed minute bars"):
            build_fixed_5m_preflight(
                product="cu", concrete_contract="SHFE.cu2406", replay_days=(day,),
                windows=windows, minute_bars=rows,
            )

    def test_late_historical_availability_fails_closed(self) -> None:
        day = date(2024, 4, 10)
        windows = governed_windows_for_days(
            product="cu", replay_days=(day,), trading_calendar=self.calendar,
            night_closed_days=self.night_closed, session_schedule=self.sessions,
        )
        rows = _minutes_for_windows(windows)
        target = rows[4]
        rows[4] = ReplayMinuteBar(
            product=target.product,
            concrete_contract=target.concrete_contract,
            trading_day=target.trading_day,
            start=target.start,
            end=target.end,
            available_at=target.end + timedelta(seconds=1),
            open=target.open,
            high=target.high,
            low=target.low,
            close=target.close,
            volume=target.volume,
            partition_identity=target.partition_identity,
            session_authority_identity=target.session_authority_identity,
        )
        with self.assertRaisesRegex(ValueError, "leak past the fixed 5m wake close"):
            build_fixed_5m_preflight(
                product="cu", concrete_contract="SHFE.cu2406", replay_days=(day,),
                windows=windows, minute_bars=rows,
            )


if __name__ == "__main__":
    unittest.main()

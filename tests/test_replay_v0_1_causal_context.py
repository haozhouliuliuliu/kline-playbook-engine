from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path
import unittest
from zoneinfo import ZoneInfo

from src.replay_v0_1_canonical_feed import (
    ReplayMinuteBar,
    build_fixed_5m_preflight,
    governed_windows_for_days,
)
from src.replay_v0_1_canonical_steps import (
    build_governed_wake_step,
    canonical_5m_to_observation_bar,
)
from src.replay_v0_1_causal_context import (
    CONTEXT_WINDOW_COUNTS,
    FOUR_HOUR_AGGREGATION_VERSION,
    LOWER_AGGREGATION_VERSION,
    CanonicalCausalContextIndex,
    context_policy_document,
    context_policy_identity,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Asia/Shanghai")
CONTRACT = "SHFE.cu2406"


def _authority():
    calendar_payload = json.loads(
        (REPO_ROOT / "docs/evidence/CANONICAL_TRADING_CALENDAR.json").read_text(encoding="utf-8")
    )
    session_payload = json.loads(
        (REPO_ROOT / "docs/evidence/CANONICAL_SESSION_SCHEDULES.json").read_text(encoding="utf-8")
    )
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


def _prior_days(calendar):
    return tuple(day for day in calendar if day < date(2024, 4, 10))[-8:]


def _replay_days(calendar):
    return tuple(day for day in calendar if date(2024, 4, 10) <= day <= date(2024, 5, 14))


def _minutes_for_windows(windows, *, contract=CONTRACT, future_delays=None):
    future_delays = future_delays or {}
    rows = []
    for window in windows:
        for index in range(window.expected_minute_count):
            start = window.start + timedelta(minutes=index)
            end = start + timedelta(minutes=1)
            delay = future_delays.get(start, 0)
            base = Decimal("70000") + Decimal(index % 60)
            rows.append(
                ReplayMinuteBar(
                    product="cu",
                    concrete_contract=contract,
                    trading_day=window.trading_day,
                    start=start,
                    end=end,
                    available_at=end + timedelta(minutes=delay),
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


def _build_world(days, *, future_delays=None):
    calendar, night_closed, sessions = _authority()
    windows = governed_windows_for_days(
        product="cu",
        replay_days=days,
        trading_calendar=calendar,
        night_closed_days=night_closed,
        session_schedule=sessions,
    )
    rows = _minutes_for_windows(windows, future_delays=future_delays)
    index = CanonicalCausalContextIndex.build(
        product="cu",
        concrete_contract=CONTRACT,
        windows=windows,
        minute_bars=rows,
    )
    return windows, rows, index


def _replay_preflight(windows_all, rows_all, replay_days):
    replay_windows = tuple(item for item in windows_all if item.trading_day in replay_days)
    replay_rows = tuple(item for item in rows_all if item.trading_day in replay_days)
    return build_fixed_5m_preflight(
        product="cu",
        concrete_contract=CONTRACT,
        replay_days=replay_days,
        windows=replay_windows,
        minute_bars=replay_rows,
    )


def _wake_at(preflight, *, day: date, hour: int, minute: int):
    target = datetime(day.year, day.month, day.day, hour, minute, tzinfo=TZ)
    for wake in preflight.wake_bars:
        if wake.trading_day == day and wake.end == target:
            return wake
    raise AssertionError(f"no governed wake ending at {target.isoformat()}")


def _count_by_timeframe(context):
    counts = {"4H": 0, "1H": 0, "15m": 0, "5m": 0}
    for bar in context:
        counts[bar.timeframe] += 1
    return counts


class ReplayV01CausalContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.calendar, cls.night_closed, cls.sessions = _authority()
        cls.prior = _prior_days(cls.calendar)
        cls.replay = _replay_days(cls.calendar)
        cls.bound = cls.prior + cls.replay
        cls.windows, cls.rows, cls.index = _build_world(cls.bound)
        cls.preflight = _replay_preflight(cls.windows, cls.rows, cls.replay)

    def test_context_window_counts_are_frozen(self) -> None:
        self.assertEqual(CONTEXT_WINDOW_COUNTS, {"4H": 2, "1H": 3, "15m": 12, "5m": 36})

    def test_aggregation_versions_are_exact(self) -> None:
        self.assertEqual(FOUR_HOUR_AGGREGATION_VERSION, "SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1")
        self.assertEqual(LOWER_AGGREGATION_VERSION, "SESSION_AUTHORITY_CONTIGUOUS_WINDOW_GRID_V0_1")
        policy = context_policy_document()
        self.assertEqual(policy["four_hour_aggregation_version"], "SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1")
        self.assertEqual(policy["lower_aggregation_version"], "SESSION_AUTHORITY_CONTIGUOUS_WINDOW_GRID_V0_1")
        self.assertEqual(policy["context_window_counts"], {"4H": 2, "1H": 3, "15m": 12, "5m": 36})
        self.assertIs(policy["provider_call_authorized"], False)
        self.assertEqual(context_policy_identity(), context_policy_identity())

    def test_cu_real_schedule_1h_bars_never_bridge_the_break(self) -> None:
        day = date(2024, 4, 10)
        windows = governed_windows_for_days(
            product="cu", replay_days=(day,), trading_calendar=self.calendar,
            night_closed_days=self.night_closed, session_schedule=self.sessions,
        )
        rows = _minutes_for_windows(windows)
        index = CanonicalCausalContextIndex.build(
            product="cu", concrete_contract=CONTRACT, windows=windows, minute_bars=rows,
        )
        day_one_hour = tuple(
            bar for bar in index.one_hour_bars if bar.start.hour >= 9
        )
        ranges = {(bar.start.isoformat(), bar.end.isoformat()) for bar in day_one_hour}
        self.assertIn(("2024-04-10T09:00:00+08:00", "2024-04-10T10:00:00+08:00"), ranges)
        self.assertIn(("2024-04-10T10:30:00+08:00", "2024-04-10T11:30:00+08:00"), ranges)
        self.assertIn(("2024-04-10T13:30:00+08:00", "2024-04-10T14:30:00+08:00"), ranges)
        # no 1H bar may span the 10:15-10:30 governed break
        for bar in index.one_hour_bars:
            if bar.start.hour < 9:
                continue
            self.assertFalse(bar.start < datetime(2024, 4, 10, 10, 30, tzinfo=TZ)
                             and bar.end > datetime(2024, 4, 10, 10, 15, tzinfo=TZ))
        # no 15m bar may span the break either
        for bar in index.fifteen_minute_bars:
            if bar.start.hour < 9:
                continue
            self.assertFalse(bar.start < datetime(2024, 4, 10, 10, 30, tzinfo=TZ)
                             and bar.end > datetime(2024, 4, 10, 10, 15, tzinfo=TZ))

    def test_civil_4h_grid_spans_lunch_break_without_missing_minutes(self) -> None:
        day = date(2024, 4, 10)
        windows = governed_windows_for_days(
            product="cu", replay_days=(day,), trading_calendar=self.calendar,
            night_closed_days=self.night_closed, session_schedule=self.sessions,
        )
        rows = _minutes_for_windows(windows)
        index = CanonicalCausalContextIndex.build(
            product="cu", concrete_contract=CONTRACT, windows=windows, minute_bars=rows,
        )
        four = index.four_hour_bars
        morning = next(
            bar for bar in four
            if bar.trading_day == day and bar.start.isoformat().startswith("2024-04-10T09:00")
        )
        self.assertEqual(morning.end.isoformat(), "2024-04-10T11:30:00+08:00")
        starts = {item.isoformat() for item in morning.source_minute_starts}
        self.assertIn("2024-04-10T09:00:00+08:00", starts)
        self.assertIn("2024-04-10T10:30:00+08:00", starts)
        self.assertIn("2024-04-10T11:29:00+08:00", starts)
        # lunch-break minutes are not missing; they are simply not official trading
        self.assertNotIn("2024-04-10T10:15:00+08:00", starts)
        self.assertEqual(morning.available_at, morning.end)
        afternoon = next(
            bar for bar in four
            if bar.trading_day == day and bar.start.isoformat().startswith("2024-04-10T13:30")
        )
        self.assertEqual(afternoon.end.isoformat(), "2024-04-10T15:00:00+08:00")

    def test_current_4h_is_not_prematurely_visible_at_1000_wake(self) -> None:
        day = date(2024, 4, 10)
        wake = _wake_at(self.preflight, day=day, hour=10, minute=0)
        context = self.index.context_for_wake(wake)
        four_hour = [bar for bar in context if bar.timeframe == "4H"]
        self.assertEqual(len(four_hour), CONTEXT_WINDOW_COUNTS["4H"])
        for bar in four_hour:
            self.assertLessEqual(bar.close_time, wake.available_at)
        # the current trading day's 09:00-11:30 4H bar must not be visible at 10:00
        self.assertFalse(
            any(
                bar.close_time == datetime(2024, 4, 10, 11, 30, tzinfo=TZ)
                for bar in four_hour
            )
        )

    def test_final_wake_context_respects_window_limits(self) -> None:
        final_day = self.replay[-1]
        last_wake = self.preflight.wake_bars[-1]
        self.assertEqual(last_wake.trading_day, final_day)
        context = self.index.context_for_wake(last_wake)
        counts = _count_by_timeframe(context)
        self.assertEqual(counts, CONTEXT_WINDOW_COUNTS)
        self.assertEqual(len(context), sum(CONTEXT_WINDOW_COUNTS.values()))
        # the two newest 4H bars of the final day close at 11:30 and 15:00
        four_hour = [bar for bar in context if bar.timeframe == "4H"]
        self.assertEqual(
            tuple(bar.close_time for bar in four_hour),
            (
                datetime(2024, 5, 14, 11, 30, tzinfo=TZ),
                datetime(2024, 5, 14, 15, 0, tzinfo=TZ),
            ),
        )

    def test_latest_5m_equals_canonical_wake_observation(self) -> None:
        final_day = self.replay[-1]
        last_wake = self.preflight.wake_bars[-1]
        self.assertEqual(last_wake.trading_day, final_day)
        context = self.index.context_for_wake(last_wake)
        expected = canonical_5m_to_observation_bar(last_wake)
        self.assertEqual(context[-1], expected)
        # the index's own 5m bar for the wake bucket must agree field by field
        index_wake_bar = next(
            bar for bar in self.index.five_minute_bars
            if bar.start == last_wake.start and bar.end == last_wake.end
        )
        self.assertEqual(index_wake_bar.to_observation_bar(), expected)

    def test_context_passes_build_governed_wake_step_for_full_final_day(self) -> None:
        final_day = self.replay[-1]
        day_wakes = tuple(
            wake for wake in self.preflight.wake_bars if wake.trading_day == final_day
        )
        self.assertGreaterEqual(len(day_wakes), 90)
        for wake in day_wakes:
            context = self.index.context_for_wake(wake)
            step = build_governed_wake_step(wake, context_bars=context)
            self.assertEqual(step.wake_bar, canonical_5m_to_observation_bar(wake))
            self.assertEqual(len(step.context_bars), sum(CONTEXT_WINDOW_COUNTS.values()))

    def test_missing_governed_minute_fails_closed(self) -> None:
        day = date(2024, 4, 10)
        windows = governed_windows_for_days(
            product="cu", replay_days=(day,), trading_calendar=self.calendar,
            night_closed_days=self.night_closed, session_schedule=self.sessions,
        )
        rows = _minutes_for_windows(windows)
        rows.pop(17)
        with self.assertRaisesRegex(ValueError, "missing .* governed 1m"):
            CanonicalCausalContextIndex.build(
                product="cu", concrete_contract=CONTRACT, windows=windows, minute_bars=rows,
            )

    def test_future_available_at_never_enters_early_context(self) -> None:
        # delay the first minute of the last prior day by 10 days
        delay_day = self.prior[-1]
        target_minute = next(
            minute for minute in self.rows
            if minute.trading_day == delay_day
            and minute.start.hour == 9 and minute.start.minute == 0
        )
        future_delays = {target_minute.start: 10 * 24 * 60}
        _, _, delayed_index = _build_world(self.bound, future_delays=future_delays)
        first_wake = self.preflight.wake_bars[0]
        self.assertEqual(first_wake.trading_day, self.replay[0])
        context = delayed_index.context_for_wake(first_wake)
        delayed_bucket_start = target_minute.start
        for bar in context:
            self.assertLessEqual(bar.available_at, first_wake.available_at)
            self.assertLessEqual(bar.close_time, first_wake.available_at)
        # the 5m bar that would start with the delayed minute must be absent
        self.assertFalse(
            any(
                bar.timeframe == "5m" and bar.open_time == delayed_bucket_start
                for bar in context
            )
        )


if __name__ == "__main__":
    unittest.main()

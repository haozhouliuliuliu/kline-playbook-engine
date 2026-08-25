from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import unittest

from src.jianghe_ai_trader import ObservationBar
from src.replay_v0_1_canonical_feed import (
    CanonicalFiveMinutePreflight,
    GovernedSessionWindow,
    ReplayFiveMinuteBar,
)
from src.replay_v0_1_canonical_steps import (
    build_governed_session_steps,
    build_governed_wake_step,
    canonical_5m_to_observation_bar,
    sessionize_preflight,
)

TZ = timezone.utc
DAY = date(2024, 4, 10)


def _window(start: datetime, ordinal: int) -> GovernedSessionWindow:
    return GovernedSessionWindow(
        trading_day=DAY,
        kind="day",
        ordinal=ordinal,
        start=start,
        end=start + timedelta(minutes=10),
        session_authority_identity="session-authority",
    )


def _wake(window: GovernedSessionWindow, offset_minutes: int) -> ReplayFiveMinuteBar:
    start = window.start + timedelta(minutes=offset_minutes)
    end = start + timedelta(minutes=5)
    return ReplayFiveMinuteBar(
        product="cu",
        concrete_contract="SHFE.cu2406",
        trading_day=DAY,
        session_window_identity=window.identity,
        start=start,
        end=end,
        available_at=end,
        open=Decimal("70000"),
        high=Decimal("70020"),
        low=Decimal("69990"),
        close=Decimal("70010"),
        volume=Decimal("15"),
        partition_identity="partition-1",
        source_minute_starts=tuple(start + timedelta(minutes=index) for index in range(5)),
    )


def _context_for(wake: ReplayFiveMinuteBar) -> tuple[ObservationBar, ...]:
    result = []
    for timeframe, duration in (
        ("4H", timedelta(hours=4)),
        ("1H", timedelta(hours=1)),
        ("15m", timedelta(minutes=15)),
    ):
        result.append(
            ObservationBar(
                timeframe=timeframe,
                open_time=wake.end - duration,
                close_time=wake.end,
                available_at=wake.end,
                open_price="69900",
                high_price="70100",
                low_price="69800",
                close_price="70010",
                volume="100",
                is_closed=True,
            )
        )
    result.append(canonical_5m_to_observation_bar(wake))
    return tuple(result)


class CanonicalReplayStepAdapterTests(unittest.TestCase):
    def test_canonical_5m_projection_preserves_governed_bar(self) -> None:
        window = _window(datetime(2024, 4, 10, 9, 0, tzinfo=TZ), 0)
        wake = _wake(window, 0)
        projected = canonical_5m_to_observation_bar(wake)
        self.assertEqual(projected.timeframe, "5m")
        self.assertEqual(projected.open_time, wake.start)
        self.assertEqual(projected.close_time, wake.end)
        self.assertEqual(projected.available_at, wake.available_at)
        self.assertEqual(projected.open_price, "70000")
        self.assertEqual(projected.high_price, "70020")
        self.assertEqual(projected.low_price, "69990")
        self.assertEqual(projected.close_price, "70010")
        self.assertEqual(projected.volume, "15")
        self.assertTrue(projected.is_closed)

    def test_sessionize_preflight_preserves_governed_window_order(self) -> None:
        first = _window(datetime(2024, 4, 10, 9, 0, tzinfo=TZ), 0)
        second = _window(datetime(2024, 4, 10, 10, 30, tzinfo=TZ), 1)
        wakes = (
            _wake(first, 0), _wake(first, 5),
            _wake(second, 0), _wake(second, 5),
        )
        preflight = CanonicalFiveMinutePreflight(
            product="cu",
            concrete_contract="SHFE.cu2406",
            replay_days=(DAY,),
            windows=(first, second),
            wake_bars=wakes,
            minute_count=20,
            expected_minute_count=20,
            expected_wake_count=4,
        )
        sessions = sessionize_preflight(preflight)
        self.assertEqual(tuple(item.session_identity for item in sessions), (first.identity, second.identity))
        self.assertEqual(tuple(len(item.wake_bars) for item in sessions), (2, 2))

    def test_governed_step_requires_full_active_stack(self) -> None:
        window = _window(datetime(2024, 4, 10, 9, 0, tzinfo=TZ), 0)
        wake = _wake(window, 0)
        with self.assertRaisesRegex(ValueError, "4H/1H/15m/5m"):
            build_governed_wake_step(
                wake,
                context_bars=(canonical_5m_to_observation_bar(wake),),
            )

    def test_governed_step_rejects_future_context(self) -> None:
        window = _window(datetime(2024, 4, 10, 9, 0, tzinfo=TZ), 0)
        wake = _wake(window, 0)
        context = list(_context_for(wake))
        context[0] = ObservationBar(
            timeframe="4H",
            open_time=wake.end - timedelta(hours=4),
            close_time=wake.end,
            available_at=wake.end + timedelta(minutes=5),
            open_price="69900",
            high_price="70100",
            low_price="69800",
            close_price="70010",
            volume="100",
            is_closed=True,
        )
        with self.assertRaisesRegex(ValueError, "future context availability"):
            build_governed_wake_step(wake, context_bars=tuple(context))

    def test_governed_step_binds_exact_canonical_wake_and_prefix_only_history(self) -> None:
        window = _window(datetime(2024, 4, 10, 9, 0, tzinfo=TZ), 0)
        wakes = (_wake(window, 0), _wake(window, 5))
        preflight = CanonicalFiveMinutePreflight(
            product="cu",
            concrete_contract="SHFE.cu2406",
            replay_days=(DAY,),
            windows=(window,),
            wake_bars=wakes,
            minute_count=10,
            expected_minute_count=10,
            expected_wake_count=2,
        )
        session = sessionize_preflight(preflight)[0]
        seen_history_lengths: list[int] = []

        def builder(wake: ReplayFiveMinuteBar, visible_history: tuple[ReplayFiveMinuteBar, ...]):
            seen_history_lengths.append(len(visible_history))
            self.assertIs(visible_history[-1], wake)
            self.assertLessEqual(max(item.end for item in visible_history), wake.end)
            return _context_for(wake)

        steps = build_governed_session_steps(session, context_builder=builder)
        self.assertEqual(seen_history_lengths, [1, 2])
        self.assertEqual(len(steps), 2)
        self.assertEqual(steps[0].session_identity, window.identity)
        self.assertEqual(steps[1].wake_bar.close_time, wakes[1].end)
        self.assertEqual(
            tuple(item.timeframe for item in steps[1].context_bars),
            ("4H", "1H", "15m", "5m"),
        )


if __name__ == "__main__":
    unittest.main()

"""Deterministic tests for the live causal context worker package.

Covers the Flash worker scope: live 1m substrate aggregation to
5m/15m/1H/4H, session-aware causal completeness, 5m wake/context emission,
bootstrap suppression, restart/reconnect continuity and the durable wake
journal integration seam. All tests are offline; no provider or network action.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from zoneinfo import ZoneInfo

from src.data_substrate import BarQuality, CompletedBar
from src.live_market_data import LiveClosedBar
from src.paper_live_causal_context import (
    ACTIVE_TIMEFRAMES,
    CONTEXT_WINDOW_COUNTS,
    LiveCausalBar,
    LiveCausalContextBuilder,
    LiveCausalWake,
    LiveSessionCalendar,
    paper_live_aggregation_policy_document,
    paper_live_aggregation_policy_identity,
)
from src.paper_wake_journal import PaperWakeJournal

REPO_ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Asia/Shanghai")
EXCHANGE = "SHFE"
INSTRUMENT = "cu2406"
CONTRACT = "SHFE.cu2406"
PRODUCT = "cu"
TARGET_DAY = date(2024, 4, 10)
_ONE_MINUTE = timedelta(minutes=1)


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


def _calendar() -> LiveSessionCalendar:
    calendar, night_closed, sessions = _authority()
    return LiveSessionCalendar(
        product=PRODUCT,
        trading_calendar=calendar,
        night_closed_days=night_closed,
        session_schedule=sessions,
    )


def _prior_days(calendar, count: int = 3) -> tuple[date, ...]:
    return tuple(day for day in calendar if day < TARGET_DAY)[-count:]


def _live_minute(start: datetime, *, price: str | None = None) -> LiveClosedBar:
    start = start.astimezone(TZ)
    end = start + _ONE_MINUTE
    base = Decimal(price) if price is not None else Decimal("70000") + Decimal(start.minute % 60)
    trading_day = _CALENDAR.trading_day_at(start)
    if trading_day is None:
        raise AssertionError(f"minute {start.isoformat()} is outside governed sessions")
    completed = CompletedBar(
        instrument=INSTRUMENT, trading_day=trading_day, start=start, end=end,
        available_at=end, quality=BarQuality(),
    )
    return LiveClosedBar(
        exchange=EXCHANGE, concrete_instrument=INSTRUMENT, completed_bar=completed,
        observed_at=end, source="TEST_LIVE",
        open=base, high=base + Decimal("2"), low=base - Decimal("2"),
        close=base + Decimal("1"), volume=Decimal("3"),
        open_interest_start=None, open_interest_end=None,
    )


def _minutes_for_days(days, *, until: datetime | None = None) -> list[LiveClosedBar]:
    bars: list[LiveClosedBar] = []
    for day in days:
        for window in _CALENDAR.session_windows_for(day):
            cursor = window.start
            while cursor < window.end:
                if until is not None and cursor >= until:
                    break
                bars.append(_live_minute(cursor))
                cursor += _ONE_MINUTE
    return bars


def _day_minutes(days, *, until: datetime | None = None) -> list[LiveClosedBar]:
    """Only day-window governed minutes (no night session minutes)."""
    bars: list[LiveClosedBar] = []
    for day in days:
        for window in _CALENDAR.session_windows_for(day):
            if window.kind != "day":
                continue
            cursor = window.start
            while cursor < window.end:
                if until is not None and cursor >= until:
                    break
                bars.append(_live_minute(cursor))
                cursor += _ONE_MINUTE
    return bars


def _new_builder() -> LiveCausalContextBuilder:
    return LiveCausalContextBuilder(
        exchange=EXCHANGE, concrete_instrument=INSTRUMENT, product=PRODUCT, calendar=_CALENDAR
    )


def _morning_until() -> datetime:
    return datetime(TARGET_DAY.year, TARGET_DAY.month, TARGET_DAY.day, 9, 15, tzinfo=TZ)


def _five_minute_bars(bars: tuple[LiveCausalBar, ...]) -> tuple[LiveCausalBar, ...]:
    return tuple(item for item in bars if item.timeframe == "5m")


def _fifteen_minute_bars(bars: tuple[LiveCausalBar, ...]) -> tuple[LiveCausalBar, ...]:
    return tuple(item for item in bars if item.timeframe == "15m")


def _one_hour_bars(bars: tuple[LiveCausalBar, ...]) -> tuple[LiveCausalBar, ...]:
    return tuple(item for item in bars if item.timeframe == "1H")


def _four_hour_bars(bars: tuple[LiveCausalBar, ...]) -> tuple[LiveCausalBar, ...]:
    return tuple(item for item in bars if item.timeframe == "4H")


_CALENDAR = _calendar()


class PolicyTests(unittest.TestCase):
    def test_policy_is_explicit_and_not_owner_approved(self) -> None:
        document = paper_live_aggregation_policy_document()
        self.assertEqual(document["policy_version"], "KPE_PAPER_LIVE_AGGREGATION_POLICY_V0_1")
        self.assertEqual(document["lower_aggregation_rule"], "SESSION_AUTHORITY_CONTIGUOUS_WINDOW_GRID_V0_1")
        self.assertEqual(document["four_hour_rule"], "SESSION_AUTHORITY_CIVIL_4H_GRID_V0_1")
        self.assertEqual(document["four_hour_role"], "BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY")
        self.assertEqual(document["context_window_counts"], CONTEXT_WINDOW_COUNTS)
        self.assertIs(document["owner_approved_permanent_paper_policy"], False)
        self.assertIs(document["provider_call_authorized"], False)
        self.assertEqual(paper_live_aggregation_policy_identity(), paper_live_aggregation_policy_identity())


class StreamingAggregationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.builder = _new_builder()

    def test_continuous_1m_to_5m_wake(self) -> None:
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=_morning_until()), observed_at=_morning_until())
        self.assertEqual(self.builder.watermark_start, datetime(2024, 4, 10, 9, 14, tzinfo=TZ))
        wakes = self.builder.observe(
            _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 20, tzinfo=TZ)),
            observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ),
        )
        self.assertEqual(len(wakes), 1)
        wake = wakes[0]
        self.assertEqual(wake.bar.start, datetime(2024, 4, 10, 9, 15, tzinfo=TZ))
        self.assertEqual(wake.bar.end, datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        self.assertEqual(wake.bar.timeframe, "5m")
        self.assertEqual(wake.bar.volume, Decimal("15"))
        # deterministic identities
        self.assertTrue(wake.wake_identity)
        self.assertTrue(wake.bar_identity)
        self.assertNotEqual(wake.wake_identity, wake.bar_identity)
        self.assertEqual(wake.observed_at, datetime(2024, 4, 10, 9, 20, tzinfo=TZ))

    def test_no_wake_before_close(self) -> None:
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=_morning_until()), observed_at=_morning_until())
        wakes = self.builder.observe(
            _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 19, tzinfo=TZ)),
            observed_at=datetime(2024, 4, 10, 9, 19, tzinfo=TZ),
        )
        # 09:15-09:19 is only 4 of 5 governed minutes -> no wake yet
        self.assertEqual(len(wakes), 0)
        bars = self.builder.complete_bars()
        self.assertNotIn(datetime(2024, 4, 10, 9, 15, tzinfo=TZ), [bar.start for bar in _five_minute_bars(bars)])

    def test_fifteen_minute_aggregation(self) -> None:
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 15, tzinfo=TZ)), observed_at=datetime(2024, 4, 10, 9, 15, tzinfo=TZ))
        fifteen = _fifteen_minute_bars(self.builder.complete_bars())
        bar = next(item for item in fifteen if item.start == datetime(2024, 4, 10, 9, 0, tzinfo=TZ))
        self.assertEqual(bar.end, datetime(2024, 4, 10, 9, 15, tzinfo=TZ))
        self.assertEqual(len(bar.source_minute_starts), 15)

    def test_one_hour_aggregation(self) -> None:
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 10, 0, tzinfo=TZ)), observed_at=datetime(2024, 4, 10, 10, 0, tzinfo=TZ))
        one_hour = _one_hour_bars(self.builder.complete_bars())
        bar = next(item for item in one_hour if item.start == datetime(2024, 4, 10, 9, 0, tzinfo=TZ))
        self.assertEqual(bar.end, datetime(2024, 4, 10, 10, 0, tzinfo=TZ))
        self.assertEqual(len(bar.source_minute_starts), 60)

    def test_four_hour_aggregation_spans_lunch_break(self) -> None:
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,)), observed_at=datetime(2024, 4, 10, 15, 0, tzinfo=TZ))
        four = _four_hour_bars(self.builder.complete_bars())
        morning = next(item for item in four if item.start == datetime(2024, 4, 10, 9, 0, tzinfo=TZ))
        self.assertEqual(morning.end, datetime(2024, 4, 10, 11, 30, tzinfo=TZ))
        self.assertEqual(len(morning.source_minute_starts), 135)  # 75 morning + 60 post-break

    def test_incomplete_bucket_suppression(self) -> None:
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 10, 0, tzinfo=TZ)), observed_at=datetime(2024, 4, 10, 10, 0, tzinfo=TZ))
        bars = self.builder.complete_bars()
        starts = [bar.start for bar in _five_minute_bars(bars)]
        self.assertNotIn(datetime(2024, 4, 10, 10, 0, tzinfo=TZ), starts)
        wakes = self.builder.observe(
            _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 10, 5, tzinfo=TZ)),
            observed_at=datetime(2024, 4, 10, 10, 5, tzinfo=TZ),
        )
        self.assertEqual(len(wakes), 1)
        self.assertEqual(wakes[0].bar.start, datetime(2024, 4, 10, 10, 0, tzinfo=TZ))

    def test_four_hour_incomplete_grid_suppressed(self) -> None:
        # morning pre-break only: 4H grid [08:00-12:00) is missing 10:30-11:29
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 10, 15, tzinfo=TZ)), observed_at=datetime(2024, 4, 10, 10, 15, tzinfo=TZ))
        four = _four_hour_bars(self.builder.complete_bars())
        self.assertNotIn(datetime(2024, 4, 10, 9, 0, tzinfo=TZ), [bar.start for bar in four])

    def test_no_bar_spans_a_governed_break(self) -> None:
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,)), observed_at=datetime(2024, 4, 10, 15, 0, tzinfo=TZ))
        break_start = datetime(2024, 4, 10, 10, 15, tzinfo=TZ)
        break_end = datetime(2024, 4, 10, 10, 30, tzinfo=TZ)
        for bar in self.builder.complete_bars():
            if bar.timeframe not in ("5m", "15m", "1H"):
                continue
            self.assertFalse(bar.start < break_end and bar.end > break_start,
                             f"{bar.timeframe} bar spans the 10:15-10:30 governed break: "
                             f"{bar.start.isoformat()}->{bar.end.isoformat()}")
        one_hour = _one_hour_bars(self.builder.complete_bars())
        ranges = {(bar.start, bar.end) for bar in one_hour}
        self.assertIn((datetime(2024, 4, 10, 9, 0, tzinfo=TZ), datetime(2024, 4, 10, 10, 0, tzinfo=TZ)), ranges)
        self.assertIn((datetime(2024, 4, 10, 10, 30, tzinfo=TZ), datetime(2024, 4, 10, 11, 30, tzinfo=TZ)), ranges)

    def test_no_cross_trading_day_contamination(self) -> None:
        self.builder.bootstrap(_minutes_for_days(_prior_days(_CALENDAR.trading_days, 2) + (TARGET_DAY,)), observed_at=datetime(2024, 4, 10, 15, 0, tzinfo=TZ))
        for bar in self.builder.complete_bars():
            days = set()
            for minute_start in bar.source_minute_starts:
                days.add(_CALENDAR.trading_day_at(minute_start))
            self.assertEqual(days, {bar.trading_day})

    def test_bootstrap_suppresses_historical_wakes(self) -> None:
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 10, 0, tzinfo=TZ)), observed_at=datetime(2024, 4, 10, 10, 0, tzinfo=TZ))
        self.assertEqual(self.builder.emitted_wake_count, 0)
        wakes = self.builder.observe(
            _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 10, 5, tzinfo=TZ)),
            observed_at=datetime(2024, 4, 10, 10, 5, tzinfo=TZ),
        )
        self.assertEqual(len(wakes), 1)
        self.assertEqual(wakes[0].bar.start, datetime(2024, 4, 10, 10, 0, tzinfo=TZ))

    def test_repeated_poll_idempotency(self) -> None:
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=_morning_until()), observed_at=_morning_until())
        new_bars = _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        first = self.builder.observe(new_bars, observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        self.assertEqual(len(first), 1)
        second = self.builder.observe(new_bars, observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        self.assertEqual(len(second), 0)

    def test_higher_timeframe_causal_availability(self) -> None:
        # until 11:29 the 4H morning grid is incomplete -> no 4H bar visible
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 11, 29, tzinfo=TZ)), observed_at=datetime(2024, 4, 10, 11, 29, tzinfo=TZ))
        four = _four_hour_bars(self.builder.complete_bars())
        self.assertNotIn(datetime(2024, 4, 10, 9, 0, tzinfo=TZ), [bar.start for bar in four])
        wakes = self.builder.observe(
            _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 11, 30, tzinfo=TZ)),
            observed_at=datetime(2024, 4, 10, 11, 30, tzinfo=TZ),
        )
        self.assertEqual(len(wakes), 1)
        four_after = _four_hour_bars(self.builder.complete_bars())
        morning = next(bar for bar in four_after if bar.start == datetime(2024, 4, 10, 9, 0, tzinfo=TZ))
        self.assertEqual(morning.available_at, datetime(2024, 4, 10, 11, 30, tzinfo=TZ))

    def test_night_day_transition_continuity(self) -> None:
        # night session of TARGET_DAY closes at 01:00; next governed is 09:00 day
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 1, 0, tzinfo=TZ)), observed_at=datetime(2024, 4, 10, 1, 0, tzinfo=TZ))
        self.assertEqual(self.builder.last_accepted_minute_start, datetime(2024, 4, 10, 0, 59, tzinfo=TZ))
        wakes = self.builder.observe(
            _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 5, tzinfo=TZ)),
            observed_at=datetime(2024, 4, 10, 9, 5, tzinfo=TZ),
        )
        self.assertEqual(len(wakes), 1)
        self.assertEqual(wakes[0].bar.start, datetime(2024, 4, 10, 9, 0, tzinfo=TZ))

    def test_trading_day_transition_continuity(self) -> None:
        # day of TARGET_DAY closes 15:00; next governed is 21:00 night of next trading day
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 15, 0, tzinfo=TZ)), observed_at=datetime(2024, 4, 10, 15, 0, tzinfo=TZ))
        self.assertEqual(self.builder.last_accepted_minute_start, datetime(2024, 4, 10, 14, 59, tzinfo=TZ))
        next_trading_day = _CALENDAR.next_trading_day_after(TARGET_DAY)
        night_start = next(
            window for window in _CALENDAR.session_windows_for(next_trading_day) if window.kind == "night"
        ).start
        wakes = self.builder.observe(
            [_live_minute(night_start + timedelta(minutes=i)) for i in range(5)],
            observed_at=night_start + timedelta(minutes=5),
        )
        self.assertEqual(len(wakes), 1)
        self.assertEqual(wakes[0].bar.trading_day, next_trading_day)


class FailClosedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.builder = _new_builder()

    def test_duplicate_minute_conflict(self) -> None:
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=_morning_until()), observed_at=_morning_until())
        bars = _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        self.builder.observe(bars, observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        conflict = _live_minute(datetime(2024, 4, 10, 9, 16, tzinfo=TZ), price="99999")
        with self.assertRaisesRegex(ValueError, "LIVE_CAUSAL_DUPLICATE_MINUTE_CONFLICT"):
            self.builder.observe([conflict], observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))

    def test_out_of_order_minute(self) -> None:
        bar_late = _live_minute(datetime(2024, 4, 10, 9, 1, tzinfo=TZ))
        bar_early = _live_minute(datetime(2024, 4, 10, 9, 0, tzinfo=TZ))
        with self.assertRaisesRegex(ValueError, "LIVE_CAUSAL_OUT_OF_ORDER"):
            self.builder.observe([bar_late, bar_early], observed_at=datetime(2024, 4, 10, 9, 2, tzinfo=TZ))
        self.assertEqual(self.builder.accepted_minute_count, 0)

    def test_missing_minute_fails_closed(self) -> None:
        self.builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=_morning_until()), observed_at=_morning_until())
        skipped = [
            bar
            for bar in _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
            if bar.completed_bar.start != datetime(2024, 4, 10, 9, 15, tzinfo=TZ)
        ]
        with self.assertRaisesRegex(ValueError, "LIVE_CAUSAL_MINUTE_GAP"):
            self.builder.observe(skipped, observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        self.assertEqual(self.builder.last_accepted_minute_start, datetime(2024, 4, 10, 9, 14, tzinfo=TZ))

    def test_unfinished_minute_rejected(self) -> None:
        bar = _live_minute(datetime(2024, 4, 10, 9, 0, tzinfo=TZ))
        with self.assertRaisesRegex(ValueError, "LIVE_MINUTE_NOT_CLOSED"):
            self.builder.observe([bar], observed_at=datetime(2024, 4, 10, 8, 59, tzinfo=TZ))

    def test_future_available_at_rejected(self) -> None:
        start = datetime(2024, 4, 10, 9, 0, tzinfo=TZ)
        end = start + _ONE_MINUTE
        completed = CompletedBar(
            instrument=INSTRUMENT, trading_day=TARGET_DAY, start=start, end=end,
            available_at=end + timedelta(minutes=5), quality=BarQuality(),
        )
        bar = LiveClosedBar(
            exchange=EXCHANGE, concrete_instrument=INSTRUMENT, completed_bar=completed,
            observed_at=end + timedelta(minutes=8), source="TEST_LIVE",
            open=Decimal("70000"), high=Decimal("70002"), low=Decimal("69998"),
            close=Decimal("70001"), volume=Decimal("3"),
            open_interest_start=None, open_interest_end=None,
        )
        with self.assertRaisesRegex(ValueError, "LIVE_MINUTE_NOT_YET_CAUSAL"):
            self.builder.observe([bar], observed_at=end + timedelta(minutes=3))

    def test_cross_contract_rejected(self) -> None:
        start = datetime(2024, 4, 10, 9, 0, tzinfo=TZ)
        end = start + _ONE_MINUTE
        completed = CompletedBar(
            instrument="rb9999", trading_day=TARGET_DAY, start=start, end=end,
            available_at=end, quality=BarQuality(),
        )
        bar = LiveClosedBar(
            exchange="SHFE", concrete_instrument="rb9999", completed_bar=completed,
            observed_at=end, source="TEST_LIVE",
            open=Decimal("3500"), high=Decimal("3502"), low=Decimal("3498"),
            close=Decimal("3501"), volume=Decimal("3"),
            open_interest_start=None, open_interest_end=None,
        )
        with self.assertRaisesRegex(ValueError, "LIVE_CAUSAL_CROSS_CONTRACT"):
            self.builder.observe([bar], observed_at=end)


class RestartReconnectTests(unittest.TestCase):
    def _build_history(self) -> tuple[LiveCausalContextBuilder, tuple[LiveCausalWake, ...]]:
        builder = _new_builder()
        calendar, night_closed, sessions = _authority()
        calendar_tuple = tuple(day for day in calendar if day <= TARGET_DAY)
        history_days = tuple(day for day in calendar_tuple if day < TARGET_DAY)[-3:] + (TARGET_DAY,)
        builder.bootstrap(
            _minutes_for_days(history_days, until=_morning_until()),
            observed_at=_morning_until(),
        )
        wakes = builder.observe(
            _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 20, tzinfo=TZ)),
            observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ),
        )
        return builder, wakes

    def _checkpoint_at_0914(self) -> dict[str, object]:
        """Checkpoint whose last accepted minute is 09:14 (no live wake yet)."""
        builder = _new_builder()
        calendar, night_closed, sessions = _authority()
        calendar_tuple = tuple(day for day in calendar if day <= TARGET_DAY)
        history_days = tuple(day for day in calendar_tuple if day < TARGET_DAY)[-3:] + (TARGET_DAY,)
        builder.bootstrap(
            _minutes_for_days(history_days, until=_morning_until()),
            observed_at=_morning_until(),
        )
        self.assertEqual(builder.last_accepted_minute_start, datetime(2024, 4, 10, 9, 14, tzinfo=TZ))
        return builder.snapshot()

    def test_restart_deterministic_rebuild(self) -> None:
        builder, wakes = self._build_history()
        self.assertEqual(len(wakes), 1)
        checkpoint = builder.snapshot()
        restored = LiveCausalContextBuilder.from_checkpoint(checkpoint, calendar=_CALENDAR)
        self.assertEqual(
            [bar.identity for bar in builder.complete_bars()],
            [bar.identity for bar in restored.complete_bars()],
        )
        self.assertEqual(builder.last_accepted_minute_start, restored.last_accepted_minute_start)
        self.assertEqual(builder.emitted_wake_count, restored.emitted_wake_count)
        self.assertEqual(builder.last_emitted_wake.wake_identity, restored.last_emitted_wake.wake_identity)
        # no duplicate wake after restore when nothing new arrives
        self.assertEqual(len(restored.observe([], observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))), 0)

    def test_no_duplicate_5m_wake_after_restore(self) -> None:
        builder, _ = self._build_history()
        restored = LiveCausalContextBuilder.from_checkpoint(builder.snapshot(), calendar=_CALENDAR)
        new_bars = _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 25, tzinfo=TZ))
        wakes = restored.observe(new_bars, observed_at=datetime(2024, 4, 10, 9, 25, tzinfo=TZ))
        self.assertEqual(len(wakes), 1)
        self.assertEqual(wakes[0].bar.start, datetime(2024, 4, 10, 9, 20, tzinfo=TZ))

    def test_reconnect_catch_up(self) -> None:
        restored = LiveCausalContextBuilder.from_checkpoint(self._checkpoint_at_0914(), calendar=_CALENDAR)
        # minutes missed while disconnected (contiguous governed continuation from 09:14)
        catch_up = [
            bar
            for bar in _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
            if bar.completed_bar.start >= datetime(2024, 4, 10, 9, 15, tzinfo=TZ)
        ]
        wakes = restored.observe(catch_up, observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        self.assertEqual(len(wakes), 1)
        self.assertEqual(wakes[0].bar.end, datetime(2024, 4, 10, 9, 20, tzinfo=TZ))

    def test_unresolved_reconnect_gap_fails_closed(self) -> None:
        checkpoint = self._checkpoint_at_0914()
        restored = LiveCausalContextBuilder.from_checkpoint(checkpoint, calendar=_CALENDAR)
        before = restored.snapshot()
        # skip governed minute 09:15 -> an unexplained gap
        skipped = [
            bar
            for bar in _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
            if bar.completed_bar.start >= datetime(2024, 4, 10, 9, 15, tzinfo=TZ)
            and bar.completed_bar.start != datetime(2024, 4, 10, 9, 15, tzinfo=TZ)
        ]
        with self.assertRaisesRegex(ValueError, "LIVE_CAUSAL_MINUTE_GAP"):
            restored.observe(skipped, observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        self.assertEqual(restored.snapshot(), before)

    def test_checkpoint_tamper_rejected(self) -> None:
        builder, _ = self._build_history()
        checkpoint = builder.snapshot()
        checkpoint = dict(checkpoint)
        checkpoint["session_authority_identity"] = "tampered"
        with self.assertRaisesRegex(ValueError, "session_authority_identity mismatch"):
            LiveCausalContextBuilder.from_checkpoint(checkpoint, calendar=_CALENDAR)


class ContextAndJournalTests(unittest.TestCase):
    def test_context_for_wake(self) -> None:
        builder = _new_builder()
        calendar, night_closed, sessions = _authority()
        calendar_tuple = tuple(day for day in calendar if day <= TARGET_DAY)
        history_days = tuple(day for day in calendar_tuple if day < TARGET_DAY)[-3:] + (TARGET_DAY,)
        builder.bootstrap(_minutes_for_days(history_days, until=_morning_until()), observed_at=_morning_until())
        wakes = builder.observe(
            _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 20, tzinfo=TZ)),
            observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ),
        )
        self.assertEqual(len(wakes), 1)
        context = builder.context_for_wake(wakes[0])
        counts = {tf: 0 for tf in ACTIVE_TIMEFRAMES}
        for bar in context:
            counts[bar.timeframe] += 1
        self.assertEqual(counts, CONTEXT_WINDOW_COUNTS)
        self.assertEqual(context[-1].identity, wakes[0].bar.identity)
        self.assertTrue(builder.context_identity(context))

    def test_context_insufficient_history_fails_closed(self) -> None:
        # day-only partial history (no night session) is too short for the full stack
        builder = _new_builder()
        builder.bootstrap(_day_minutes((TARGET_DAY,), until=_morning_until()), observed_at=_morning_until())
        wakes = builder.observe(
            _day_minutes((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 20, tzinfo=TZ)),
            observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ),
        )
        self.assertEqual(len(wakes), 1)
        with self.assertRaisesRegex(ValueError, "LIVE_CAUSAL_CONTEXT_INSUFFICIENT_HISTORY"):
            builder.context_for_wake(wakes[0])

    def test_wake_journal_seam(self) -> None:
        builder = _new_builder()
        builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=_morning_until()), observed_at=_morning_until())
        wakes = builder.observe(
            _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 20, tzinfo=TZ)),
            observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ),
        )
        wake = wakes[0]
        with TemporaryDirectory() as tmp:
            journal = PaperWakeJournal(Path(tmp) / "wakes.sqlite3")
            self.assertFalse(builder.wake_already_journaled(wake, journal=journal))
            record = builder.admit_wake_to_journal(
                wake, journal=journal, trader_identity="trader-live", concrete_contract_id=CONTRACT
            )
            self.assertEqual(record.bar_identity, wake.bar_identity)
            self.assertTrue(builder.wake_already_journaled(wake, journal=journal))
            # exact re-observation is idempotent: same record, no duplicate row
            again = builder.admit_wake_to_journal(
                wake, journal=journal, trader_identity="trader-live", concrete_contract_id=CONTRACT
            )
            self.assertEqual(again.wake_identity, record.wake_identity)
            self.assertEqual(len(journal.pending_observations()), 1)
            journal.close()

    def test_wake_identity_is_stable_and_context_identity_stable(self) -> None:
        builder = _new_builder()
        builder.bootstrap(_minutes_for_days((TARGET_DAY,), until=_morning_until()), observed_at=_morning_until())
        bars = _minutes_for_days((TARGET_DAY,), until=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        wakes_a = builder.observe(bars, observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        builder_b = _new_builder()
        builder_b.bootstrap(_minutes_for_days((TARGET_DAY,), until=_morning_until()), observed_at=_morning_until())
        wakes_b = builder_b.observe(bars, observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        self.assertEqual(wakes_a[0].wake_identity, wakes_b[0].wake_identity)
        self.assertEqual(wakes_a[0].bar_identity, wakes_b[0].bar_identity)
        self.assertEqual(wakes_a[0].logical_wake_selection_identity, wakes_b[0].logical_wake_selection_identity)


if __name__ == "__main__":
    unittest.main()

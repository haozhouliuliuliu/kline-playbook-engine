"""Mechanical replay-vs-live causal-context equivalence regression tests.

Feeds the SAME deterministic synthetic 1m fixture through both the frozen
historical replay implementation (``CanonicalCausalContextIndex`` /
``replay_v0_1_causal_context``) and the streaming live PAPER implementation
(``LiveCausalContextBuilder`` / ``paper_live_causal_context``), then compares
their closed-bar geometry and served context at the same causal information
cutoff.

These tests prove (or reject) that future real-time PAPER observations show
DeepSeek the same time structure as the already-governed historical replay:

- governed session boundaries / trading-day attribution;
- 5m / 15m / 1H / 4H bucket boundaries;
- lunch/session break handling; night -> day and trading-day transitions;
- OHLCV aggregation and ``available_at`` semantics;
- no future leakage; context window counts; newest 5m bar == wake bar;
- wake only after a complete governed 5m close; duplicate wake suppression;
- restart/reconnect continuity;
- missing / duplicate / out-of-order 1m fail-closed behavior.

All tests are offline; no provider, broker, account, credential or network
action.
"""

from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path
import unittest
from zoneinfo import ZoneInfo

from src.data_substrate import BarQuality, CompletedBar
from src.live_market_data import LiveClosedBar
from src.paper_live_causal_context import (
    ACTIVE_TIMEFRAMES,
    CONTEXT_WINDOW_COUNTS,
    LiveCausalContextBuilder,
    LiveSessionCalendar,
)
from src.replay_v0_1_canonical_feed import (
    ReplayFiveMinuteBar,
    ReplayMinuteBar,
    build_fixed_5m_preflight,
    governed_windows_for_days,
)
from src.replay_v0_1_causal_context import CanonicalCausalContextIndex
from src.replay_v0_1_canonical_steps import canonical_5m_to_observation_bar

REPO_ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Asia/Shanghai")
EXCHANGE = "SHFE"
INSTRUMENT = "cu2406"
CONTRACT = "SHFE.cu2406"
PRODUCT = "cu"
_ONE_MINUTE = timedelta(minutes=1)
TARGET_DAY = date(2024, 4, 10)


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


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _replay_minute_rows(windows, *, contract=CONTRACT) -> list[ReplayMinuteBar]:
    """Deterministic 1m fixture identical to the replay causal-context test."""
    rows: list[ReplayMinuteBar] = []
    for window in windows:
        for index in range(window.expected_minute_count):
            start = window.start + timedelta(minutes=index)
            end = start + _ONE_MINUTE
            base = Decimal("70000") + Decimal(index % 60)
            rows.append(
                ReplayMinuteBar(
                    product=PRODUCT,
                    concrete_contract=contract,
                    trading_day=window.trading_day,
                    start=start,
                    end=end,
                    available_at=end,
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


def _to_live_closed_bar(minute: ReplayMinuteBar) -> LiveClosedBar:
    """Lossless conversion of one fixture minute to the live closed-bar shape."""
    completed = CompletedBar(
        instrument=INSTRUMENT,
        trading_day=minute.trading_day,
        start=minute.start,
        end=minute.end,
        available_at=minute.available_at,
        quality=BarQuality(),
    )
    return LiveClosedBar(
        exchange=EXCHANGE,
        concrete_instrument=INSTRUMENT,
        completed_bar=completed,
        observed_at=minute.available_at,
        source="EQ_FIXTURE",
        open=minute.open,
        high=minute.high,
        low=minute.low,
        close=minute.close,
        volume=minute.volume,
        open_interest_start=None,
        open_interest_end=None,
    )


class EquivalenceWorld:
    """One shared deterministic world fed through both implementations."""

    def __init__(self) -> None:
        calendar, night_closed, sessions = _authority()
        # 6 prior trading days keep the suite fast while still covering the
        # weekend-gap night session (2024-04-01) and a night-closed day
        # (2024-04-08), plus full-context history for the target wakes.
        prior = tuple(day for day in calendar if day < TARGET_DAY)[-6:]
        days = prior + (TARGET_DAY, date(2024, 4, 11))
        windows = governed_windows_for_days(
            product=PRODUCT,
            replay_days=days,
            trading_calendar=calendar,
            night_closed_days=night_closed,
            session_schedule=sessions,
        )
        rows = _replay_minute_rows(windows)
        self.calendar = calendar
        self.night_closed = night_closed
        self.sessions = sessions
        self.days = days
        self.windows = windows
        self.replay_rows = rows
        self.live_rows = [_to_live_closed_bar(row) for row in rows]
        self.index = CanonicalCausalContextIndex.build(
            product=PRODUCT,
            concrete_contract=CONTRACT,
            windows=windows,
            minute_bars=rows,
        )
        self.preflight = build_fixed_5m_preflight(
            product=PRODUCT,
            concrete_contract=CONTRACT,
            replay_days=days,
            windows=windows,
            minute_bars=rows,
        )
        self.live_calendar = LiveSessionCalendar(
            product=PRODUCT,
            trading_calendar=calendar,
            night_closed_days=night_closed,
            session_schedule=sessions,
        )

    def new_builder(self) -> LiveCausalContextBuilder:
        return LiveCausalContextBuilder(
            exchange=EXCHANGE,
            concrete_instrument=INSTRUMENT,
            product=PRODUCT,
            calendar=self.live_calendar,
        )

    def live_minutes_up_to(self, cutoff: datetime) -> list[LiveClosedBar]:
        """Every governed 1m bar whose close is at/before ``cutoff``."""
        return [bar for bar in self.live_rows if bar.completed_bar.end <= cutoff]

    def live_minutes_in_bucket(self, start: datetime, end: datetime) -> list[LiveClosedBar]:
        return [
            bar
            for bar in self.live_rows
            if start <= bar.completed_bar.start < end
        ]


_WORLD: EquivalenceWorld | None = None


def _world() -> EquivalenceWorld:
    global _WORLD
    if _WORLD is None:
        _WORLD = EquivalenceWorld()
    return _WORLD


def _bar_shape(bar) -> tuple[object, ...]:
    """Full deterministic bar geometry for replay/live closed-bar comparison."""
    if hasattr(bar, "open_time"):  # ObservationBar
        return (
            bar.timeframe,
            bar.open_time.isoformat(),
            bar.close_time.isoformat(),
            bar.available_at.isoformat(),
            bar.open_price,
            bar.high_price,
            bar.low_price,
            bar.close_price,
            bar.volume,
        )
    # CausalContextBar or LiveCausalBar
    return (
        bar.timeframe,
        bar.start.isoformat(),
        bar.end.isoformat(),
        bar.available_at.isoformat(),
        _decimal_text(bar.open),
        _decimal_text(bar.high),
        _decimal_text(bar.low),
        _decimal_text(bar.close),
        _decimal_text(bar.volume),
    )


def _replay_visible_bars(world: EquivalenceWorld, cutoff: datetime) -> tuple:
    all_bars = (
        list(world.index.five_minute_bars)
        + list(world.index.fifteen_minute_bars)
        + list(world.index.one_hour_bars)
        + list(world.index.four_hour_bars)
    )
    return tuple(
        bar
        for bar in all_bars
        if bar.available_at <= cutoff and bar.end <= cutoff
    )


def _replay_wake_at(world: EquivalenceWorld, *, start: datetime) -> ReplayFiveMinuteBar:
    for wake in world.preflight.wake_bars:
        if wake.start == start:
            return wake
    raise AssertionError(f"no replay wake starting at {start.isoformat()}")


class CompleteBarEquivalenceTests(unittest.TestCase):
    """Same fixture, same cutoff: identical closed-bar geometry."""

    def _compare_at(self, cutoff: datetime) -> None:
        world = _world()
        builder = world.new_builder()
        builder.bootstrap(world.live_minutes_up_to(cutoff), observed_at=cutoff)
        live_shapes = {_bar_shape(bar) for bar in builder.complete_bars()}
        replay_shapes = {_bar_shape(bar) for bar in _replay_visible_bars(world, cutoff)}
        only_live = sorted(live_shapes - replay_shapes)
        only_replay = sorted(replay_shapes - live_shapes)
        self.assertEqual(
            only_live, [],
            f"at {cutoff.isoformat()} live emits {len(only_live)} bars replay does not",
        )
        self.assertEqual(
            only_replay, [],
            f"at {cutoff.isoformat()} replay emits {len(only_replay)} bars live does not",
        )
        self.assertEqual(len(live_shapes), len(replay_shapes))

    def test_equivalence_at_night_close_20240410(self) -> None:
        self._compare_at(datetime(2024, 4, 10, 1, 0, tzinfo=TZ))

    def test_equivalence_at_first_day_wake_20240410(self) -> None:
        self._compare_at(datetime(2024, 4, 10, 9, 5, tzinfo=TZ))

    def test_equivalence_at_mid_morning_20240410(self) -> None:
        self._compare_at(datetime(2024, 4, 10, 10, 0, tzinfo=TZ))

    def test_equivalence_at_pre_break_20240410(self) -> None:
        self._compare_at(datetime(2024, 4, 10, 10, 15, tzinfo=TZ))

    def test_equivalence_at_morning_4h_complete_20240410(self) -> None:
        self._compare_at(datetime(2024, 4, 10, 11, 30, tzinfo=TZ))

    def test_equivalence_at_afternoon_open_20240410(self) -> None:
        self._compare_at(datetime(2024, 4, 10, 13, 30, tzinfo=TZ))

    def test_equivalence_at_day_close_20240410(self) -> None:
        self._compare_at(datetime(2024, 4, 10, 15, 0, tzinfo=TZ))

    def test_equivalence_at_next_night_open_20240410(self) -> None:
        self._compare_at(datetime(2024, 4, 10, 21, 0, tzinfo=TZ))

    def test_equivalence_at_next_night_close_20240411(self) -> None:
        self._compare_at(datetime(2024, 4, 11, 1, 0, tzinfo=TZ))

    def test_equivalence_at_next_day_close_20240411(self) -> None:
        self._compare_at(datetime(2024, 4, 11, 15, 0, tzinfo=TZ))

    def test_night_session_across_weekend_gap_not_suppressed(self) -> None:
        """Regression: trading day 2024-04-01 night (03-29 21:00 -> 03-30 01:00)
        spans a weekend; the live builder must still emit its bars exactly like
        the frozen replay (no silent suppression from the coverage scan bound).
        """
        world = _world()
        cutoff = datetime(2024, 4, 10, 1, 0, tzinfo=TZ)
        builder = world.new_builder()
        builder.bootstrap(world.live_minutes_up_to(cutoff), observed_at=cutoff)
        live_night = {
            _bar_shape(bar)
            for bar in builder.complete_bars()
            if bar.trading_day == date(2024, 4, 1) and bar.timeframe == "5m"
            and bar.start.isoformat().startswith("2024-03-29T21:00")
        }
        replay_night = {
            _bar_shape(bar)
            for bar in _replay_visible_bars(world, cutoff)
            if bar.trading_day == date(2024, 4, 1) and bar.timeframe == "5m"
            and bar.start.isoformat().startswith("2024-03-29T21:00")
        }
        self.assertTrue(replay_night, "fixture must contain the weekend-gap night 5m bars")
        self.assertEqual(live_night, replay_night)


class WakeContextEquivalenceTests(unittest.TestCase):
    """At the same wake, the served 4H/1H/15m/5m context is identical."""

    def _context_shapes(self, wake_start: datetime) -> tuple[tuple[object, ...], ...]:
        world = _world()
        replay_wake = _replay_wake_at(world, start=wake_start)
        cutoff = replay_wake.available_at
        builder = world.new_builder()
        # Absorb everything strictly before the wake bucket, then stream the
        # wake bucket so the live builder emits exactly that governed wake.
        builder.bootstrap(
            world.live_minutes_up_to(replay_wake.start),
            observed_at=cutoff,
        )
        wakes = builder.observe(
            world.live_minutes_in_bucket(replay_wake.start, replay_wake.end),
            observed_at=cutoff,
        )
        self.assertEqual(len(wakes), 1, "live must emit exactly one wake for the bucket")
        live_context = builder.context_for_wake(wakes[0])
        replay_context = world.index.context_for_wake(replay_wake)
        return tuple(_bar_shape(bar) for bar in live_context), tuple(
            _bar_shape(bar) for bar in replay_context
        )

    def test_context_equivalence_first_wake_20240410(self) -> None:
        live, replay = self._context_shapes(datetime(2024, 4, 10, 9, 0, tzinfo=TZ))
        self.assertEqual(live, replay)
        self.assertEqual(len(live), sum(CONTEXT_WINDOW_COUNTS.values()))

    def test_context_equivalence_mid_morning_20240410(self) -> None:
        live, replay = self._context_shapes(datetime(2024, 4, 10, 10, 0, tzinfo=TZ))
        self.assertEqual(live, replay)

    def test_context_equivalence_end_of_morning_20240410(self) -> None:
        # 11:30 wake is when the morning 4H bar becomes causally available.
        live, replay = self._context_shapes(datetime(2024, 4, 10, 11, 25, tzinfo=TZ))
        self.assertEqual(live, replay)

    def test_context_equivalence_day_close_20240410(self) -> None:
        live, replay = self._context_shapes(datetime(2024, 4, 10, 14, 55, tzinfo=TZ))
        self.assertEqual(live, replay)

    def test_context_equivalence_night_open_20240411(self) -> None:
        live, replay = self._context_shapes(datetime(2024, 4, 10, 21, 0, tzinfo=TZ))
        self.assertEqual(live, replay)

    def test_context_equivalence_night_close_20240411(self) -> None:
        live, replay = self._context_shapes(datetime(2024, 4, 11, 0, 55, tzinfo=TZ))
        self.assertEqual(live, replay)

    def test_context_equivalence_next_day_open_20240411(self) -> None:
        live, replay = self._context_shapes(datetime(2024, 4, 11, 9, 0, tzinfo=TZ))
        self.assertEqual(live, replay)

    def test_context_counts_and_newest_five_equal_wake(self) -> None:
        world = _world()
        wake_start = datetime(2024, 4, 10, 10, 0, tzinfo=TZ)
        replay_wake = _replay_wake_at(world, start=wake_start)
        cutoff = replay_wake.available_at
        builder = world.new_builder()
        builder.bootstrap(world.live_minutes_up_to(replay_wake.start), observed_at=cutoff)
        wakes = builder.observe(
            world.live_minutes_in_bucket(replay_wake.start, replay_wake.end),
            observed_at=cutoff,
        )
        context = builder.context_for_wake(wakes[0])
        counts = {tf: 0 for tf in ACTIVE_TIMEFRAMES}
        for bar in context:
            counts[bar.timeframe] += 1
        self.assertEqual(counts, CONTEXT_WINDOW_COUNTS)
        # newest visible 5m bar is exactly the wake bar, matching the replay.
        self.assertEqual(context[-1].identity, wakes[0].bar.identity)
        replay_context = world.index.context_for_wake(replay_wake)
        self.assertEqual(replay_context[-1], canonical_5m_to_observation_bar(replay_wake))
        # no future leakage: every context bar must be causally available.
        for bar in context:
            self.assertLessEqual(bar.available_at, cutoff)
            self.assertLessEqual(bar.end, cutoff)


class WakeEmissionEquivalenceTests(unittest.TestCase):
    """The live builder emits exactly the frozen replay's governed 5m wake set."""

    def test_emitted_wake_set_matches_replay_preflight(self) -> None:
        world = _world()
        builder = world.new_builder()
        # Stream the whole world chronologically; every newly completed governed
        # 5m bar becomes exactly one live wake.
        last_end = world.live_rows[-1].completed_bar.end
        wakes = builder.observe(world.live_rows, observed_at=last_end)
        emitted = {(wake.bar.start, wake.bar.end) for wake in wakes}
        replay = {(wake.start, wake.end) for wake in world.preflight.wake_bars}
        self.assertEqual(emitted, replay)
        self.assertEqual(len(wakes), len(replay), "each governed 5m bar wakes exactly once")
        self.assertEqual(builder.emitted_wake_count, len(replay))

    def test_no_duplicate_wake_on_repeated_poll(self) -> None:
        world = _world()
        builder = world.new_builder()
        last_end = world.live_rows[-1].completed_bar.end
        first = builder.observe(world.live_rows, observed_at=last_end)
        second = builder.observe(world.live_rows, observed_at=last_end)
        self.assertEqual(len(second), 0)
        self.assertEqual(len(first), len(world.preflight.wake_bars))

    def test_no_wake_before_complete_governed_5m_close(self) -> None:
        world = _world()
        builder = world.new_builder()
        bucket_start = datetime(2024, 4, 10, 9, 15, tzinfo=TZ)
        bucket_end = datetime(2024, 4, 10, 9, 20, tzinfo=TZ)
        # bootstrap through the 09:14-09:15 minute, then stream only the first
        # 4 of 5 governed minutes of the 09:15 bucket -> no wake may be emitted
        # before the complete governed 5m close.
        builder.bootstrap(
            world.live_minutes_up_to(datetime(2024, 4, 10, 9, 15, tzinfo=TZ)),
            observed_at=datetime(2024, 4, 10, 9, 15, tzinfo=TZ),
        )
        partial = world.live_minutes_in_bucket(
            bucket_start, datetime(2024, 4, 10, 9, 19, tzinfo=TZ)
        )
        self.assertEqual(len(partial), 4)
        self.assertEqual(len(builder.observe(partial, observed_at=datetime(2024, 4, 10, 9, 19, tzinfo=TZ))), 0)
        # the 5th governed minute closes the bucket -> exactly one wake, whose
        # geometry matches the frozen replay's 09:15-09:20 wake bar.
        complete = world.live_minutes_in_bucket(bucket_start, bucket_end)
        wakes = builder.observe(complete, observed_at=bucket_end)
        self.assertEqual(len(wakes), 1)
        self.assertEqual((wakes[0].bar.start, wakes[0].bar.end), (bucket_start, bucket_end))
        replay_wake = _replay_wake_at(world, start=bucket_start)
        self.assertEqual(
            (replay_wake.start, replay_wake.end), (bucket_start, bucket_end)
        )


class RestartContinuityEquivalenceTests(unittest.TestCase):
    """Restart/reconnect must preserve the same replay-equivalent state."""

    def test_restart_preserves_replay_equivalence(self) -> None:
        world = _world()
        builder = world.new_builder()
        mid = datetime(2024, 4, 10, 9, 20, tzinfo=TZ)
        builder.bootstrap(world.live_minutes_up_to(mid), observed_at=mid)
        checkpoint = builder.snapshot()
        restored = LiveCausalContextBuilder.from_checkpoint(checkpoint, calendar=world.live_calendar)
        # Re-observing the already-bootstrapped 09:15-09:20 bucket must not
        # duplicate a wake after restart.
        consumed_bucket = world.live_minutes_in_bucket(
            datetime(2024, 4, 10, 9, 15, tzinfo=TZ), mid
        )
        self.assertEqual(
            len(restored.observe(consumed_bucket, observed_at=mid)), 0,
            "no duplicate wake for a bucket already consumed before restart",
        )
        final = datetime(2024, 4, 11, 15, 0, tzinfo=TZ)
        wakes = restored.observe(world.live_minutes_up_to(final), observed_at=final)
        # Restored builder + remaining stream equals a fresh builder fed
        # everything, and both equal the frozen replay at the final cutoff.
        fresh = world.new_builder()
        fresh.bootstrap(world.live_minutes_up_to(final), observed_at=final)
        restored_shapes = {_bar_shape(bar) for bar in restored.complete_bars()}
        fresh_shapes = {_bar_shape(bar) for bar in fresh.complete_bars()}
        replay_shapes = {_bar_shape(bar) for bar in _replay_visible_bars(world, final)}
        self.assertEqual(restored_shapes, fresh_shapes)
        self.assertEqual(restored_shapes, replay_shapes)
        # The newly streamed wakes are exactly the replay's post-restart wake bars.
        replay_post = {
            (wake.start, wake.end)
            for wake in world.preflight.wake_bars
            if wake.start >= mid
        }
        emitted = {(wake.bar.start, wake.bar.end) for wake in wakes}
        self.assertEqual(emitted, replay_post)


class FailClosedEquivalenceTests(unittest.TestCase):
    """Both implementations fail closed on the same corrupted 1m substrate."""

    def test_missing_governed_minute_fails_closed_both_sides(self) -> None:
        world = _world()
        missing_start = datetime(2024, 4, 10, 9, 15, tzinfo=TZ)
        rows = [row for row in world.replay_rows if row.start != missing_start]
        with self.assertRaisesRegex(ValueError, "missing .* governed 1m"):
            CanonicalCausalContextIndex.build(
                product=PRODUCT,
                concrete_contract=CONTRACT,
                windows=world.windows,
                minute_bars=rows,
            )
        builder = world.new_builder()
        fed = world.live_minutes_up_to(datetime(2024, 4, 10, 9, 20, tzinfo=TZ))
        fed = [bar for bar in fed if bar.completed_bar.start != missing_start]
        with self.assertRaisesRegex(ValueError, "LIVE_CAUSAL_MINUTE_GAP"):
            builder.bootstrap(fed, observed_at=datetime(2024, 4, 10, 9, 20, tzinfo=TZ))

    def test_duplicate_minute_fails_closed_both_sides(self) -> None:
        world = _world()
        duplicate_start = datetime(2024, 4, 10, 9, 16, tzinfo=TZ)
        duplicated = [
            row
            for row in world.replay_rows
            if row.start == duplicate_start or row.start < duplicate_start
        ]
        duplicated.append(next(row for row in world.replay_rows if row.start == duplicate_start))
        with self.assertRaisesRegex(ValueError, "duplicate canonical minute start"):
            CanonicalCausalContextIndex.build(
                product=PRODUCT,
                concrete_contract=CONTRACT,
                windows=world.windows,
                minute_bars=duplicated,
            )
        builder = world.new_builder()
        fed = world.live_minutes_up_to(datetime(2024, 4, 10, 9, 17, tzinfo=TZ))
        # Re-inject the 09:16 bar with different (self-consistent) OHLCV after it
        # was admitted -> the live builder must fail closed.
        conflict = LiveClosedBar(
            exchange=EXCHANGE,
            concrete_instrument=INSTRUMENT,
            completed_bar=CompletedBar(
                instrument=INSTRUMENT,
                trading_day=date(2024, 4, 10),
                start=duplicate_start,
                end=duplicate_start + _ONE_MINUTE,
                available_at=duplicate_start + _ONE_MINUTE,
                quality=BarQuality(),
            ),
            observed_at=duplicate_start + _ONE_MINUTE,
            source="EQ_FIXTURE",
            open=Decimal("99999"),
            high=Decimal("100001"),
            low=Decimal("99997"),
            close=Decimal("99999"),
            volume=Decimal("3"),
            open_interest_start=None,
            open_interest_end=None,
        )
        fed.append(conflict)
        with self.assertRaisesRegex(ValueError, "LIVE_CAUSAL_DUPLICATE_MINUTE_CONFLICT"):
            builder.bootstrap(fed, observed_at=datetime(2024, 4, 10, 9, 17, tzinfo=TZ))

    def test_identical_re_delivery_is_idempotent_and_still_equivalent(self) -> None:
        """An identical repeated closed 1m bar is deduped, not treated as a
        different minute; the resulting bars still equal the replay."""
        world = _world()
        cutoff = datetime(2024, 4, 10, 10, 0, tzinfo=TZ)
        fed = world.live_minutes_up_to(cutoff)
        builder = world.new_builder()
        builder.bootstrap(fed, observed_at=cutoff)
        # An identical re-poll across a separate observe() is deduped (no new
        # admitted minute, no duplicate wake) and the bars still equal replay.
        self.assertEqual(len(builder.observe(fed, observed_at=cutoff)), 0)
        self.assertEqual(builder.accepted_minute_count, len(fed))
        replay_shapes = {_bar_shape(bar) for bar in _replay_visible_bars(world, cutoff)}
        live_shapes = {_bar_shape(bar) for bar in builder.complete_bars()}
        self.assertEqual(live_shapes, replay_shapes)

    def test_out_of_order_minute_fails_closed_live(self) -> None:
        """The live stream is order-enforcing (governed replay input is already
        ordered), so out-of-order delivery fails closed rather than silently
        accepting a non-causal sequence."""
        world = _world()
        builder = world.new_builder()
        early = world.live_minutes_in_bucket(
            datetime(2024, 4, 10, 9, 0, tzinfo=TZ), datetime(2024, 4, 10, 9, 1, tzinfo=TZ)
        )
        late = world.live_minutes_in_bucket(
            datetime(2024, 4, 10, 9, 1, tzinfo=TZ), datetime(2024, 4, 10, 9, 2, tzinfo=TZ)
        )
        with self.assertRaisesRegex(ValueError, "LIVE_CAUSAL_OUT_OF_ORDER"):
            builder.observe(late + early, observed_at=datetime(2024, 4, 10, 9, 2, tzinfo=TZ))
        self.assertEqual(builder.accepted_minute_count, 0)


if __name__ == "__main__":
    unittest.main()

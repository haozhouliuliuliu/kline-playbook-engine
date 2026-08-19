"""Tests for the generic point-in-time technical feature layer (Lane G).

All fixtures are synthetic/non-candidate bars; no real candidate corpus or
candidate outcome data is used anywhere in this file.
"""

import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.data_substrate import BarQuality, CompletedBar, SessionMetadata, SessionWindow
from src.historical_data import NormalizedHistoricalBar
from src.technical_features import (
    ADXValue,
    ADX_ALGORITHM_VERSION,
    AggregatedBar,
    AggregationResult,
    EMA_ALGORITHM_VERSION,
    FEATURE_TYPE_ADX,
    FEATURE_TYPE_EMA,
    FeatureValue,
    IncompleteBucket,
    STATUS_INSUFFICIENT_HISTORY,
    STATUS_READY,
    STATUS_UNDEFINED,
    STATUS_UNKNOWN,
    TimeframeAggregator,
    TimeframeSpec,
    VOLUME_STATUS_COMPLETE,
    VOLUME_STATUS_UNKNOWN,
    compute_adx,
    compute_ema,
    visible_aggregates,
    visible_features,
    wilder_directional_movement,
)

CN = ZoneInfo("Asia/Shanghai")
UTC = ZoneInfo("UTC")
DAY = date(2025, 6, 16)  # Monday (official trading day)
FRIDAY = date(2025, 6, 13)
SATURDAY = date(2025, 6, 14)
RETRIEVED_AT = datetime(2026, 8, 16, 2, 0, tzinfo=UTC)

SPEC_5M = TimeframeSpec("5m", "INTRADAY", 300, "v1")
SPEC_15M = TimeframeSpec("15m", "INTRADAY", 900, "v1")
SPEC_30M = TimeframeSpec("30m", "INTRADAY", 1800, "v1")
SPEC_60M = TimeframeSpec("60m", "INTRADAY", 3600, "v1")
SPEC_120M = TimeframeSpec("120m", "INTRADAY", 7200, "v1")
SPEC_DAILY = TimeframeSpec("daily", "DAILY", None, "v1")


def at(hour: int, minute: int, day: date = DAY) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=CN)


SESSIONS = SessionMetadata(
    "shfe-cu-session-fixture-v1",
    [
        SessionWindow("SHFE", "SHFE.cu2501", DAY, at(21, 0, FRIDAY), at(1, 0, SATURDAY), "night"),
        SessionWindow("SHFE", "SHFE.cu2501", DAY, at(9, 0), at(10, 15), "day"),
        SessionWindow("SHFE", "SHFE.cu2501", DAY, at(10, 30), at(11, 30), "day"),
    ],
)

BREAK_SESSIONS = SessionMetadata(
    "shfe-cu-break-fixture-v1",
    [
        SessionWindow("SHFE", "SHFE.cu2501", DAY, at(9, 0), at(9, 10), "day"),
        SessionWindow("SHFE", "SHFE.cu2501", DAY, at(10, 30), at(10, 40), "day"),
    ],
)

LUNCH_SESSIONS = SessionMetadata(
    "shfe-cu-lunch-fixture-v1",
    [
        SessionWindow("SHFE", "SHFE.cu2501", DAY, at(9, 0), at(9, 30), "day"),
        SessionWindow("SHFE", "SHFE.cu2501", DAY, at(10, 0), at(10, 30), "day"),
    ],
)

LONG_DAY_SESSIONS = SessionMetadata(
    "shfe-cu-long-day-fixture-v1",
    [SessionWindow("SHFE", "SHFE.cu2501", DAY, at(9, 0), at(11, 30), "day")],
)


def make_bar(
    start: datetime,
    end: datetime,
    open_price,
    high,
    low,
    close,
    *,
    volume=None,
    available_at: datetime | None = None,
    trading_day: date | None = None,
    sessions: SessionMetadata = SESSIONS,
) -> NormalizedHistoricalBar:
    if available_at is None:
        available_at = end
    if trading_day is None:
        trading_day = sessions.trading_day_at("SHFE", "SHFE.cu2501", start)
    if trading_day is None:
        raise AssertionError("fixture bar falls outside published sessions")
    completed = CompletedBar("SHFE.cu2501", trading_day, start, end, available_at, BarQuality())
    return NormalizedHistoricalBar(
        "SHFE",
        "SHFE.cu2501",
        start,
        RETRIEVED_AT,
        completed,
        Decimal(str(open_price)),
        Decimal(str(high)),
        Decimal(str(low)),
        Decimal(str(close)),
        None if volume is None else Decimal(str(volume)),
        None,
        None,
        "raw-fixture-v1",
        "data-fixture-v1",
    )


def ramp_bars(
    start: datetime,
    count: int,
    *,
    step: int = 1,
    volume=1,
    available_delta: timedelta = timedelta(0),
    sessions: SessionMetadata = SESSIONS,
) -> list[NormalizedHistoricalBar]:
    bars = []
    for index in range(count):
        bar_start = start + timedelta(minutes=index)
        bar_end = bar_start + timedelta(minutes=1)
        base = step * index
        bars.append(
            make_bar(
                bar_start,
                bar_end,
                100 + base,
                102 + base,
                99 + base,
                101 + base,
                volume=volume,
                available_at=bar_end + available_delta,
                sessions=sessions,
            )
        )
    return bars


def make_aggregate(
    index: int,
    open_price,
    high,
    low,
    close,
    *,
    start: datetime | None = None,
    volume=None,
    available_at: datetime | None = None,
    spec: TimeframeSpec = SPEC_5M,
    session_version: str = "shfe-cu-session-fixture-v1",
) -> AggregatedBar:
    if start is None:
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN) + timedelta(minutes=5 * index)
    end = start + timedelta(minutes=5)
    if available_at is None:
        available_at = end
    return AggregatedBar(
        exchange="SHFE",
        concrete_instrument="SHFE.cu2501",
        trading_day=DAY,
        timeframe_spec=spec,
        session_metadata_version=session_version,
        session_kind="day",
        start=start,
        end=end,
        open=Decimal(str(open_price)),
        high=Decimal(str(high)),
        low=Decimal(str(low)),
        close=Decimal(str(close)),
        volume=None if volume is None else Decimal(str(volume)),
        volume_status=VOLUME_STATUS_UNKNOWN if volume is None else VOLUME_STATUS_COMPLETE,
        available_at=available_at,
        source_bar_identities=(f"src-{index}",),
    )


def flat_aggregates(closes: list) -> list[AggregatedBar]:
    """Chronological aggregates whose OHLC are all equal to each close."""
    return [
        make_aggregate(index, value, value, value, value, volume=Decimal("1"))
        for index, value in enumerate(closes)
    ]


class TimeframeAggregationTests(unittest.TestCase):
    def test_one_minute_to_five_minute_ohlcv_correctness(self):
        aggregator = TimeframeAggregator(SESSIONS)
        bars = ramp_bars(at(9, 0), 10)
        result = aggregator.aggregate(bars, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertIsInstance(result, AggregationResult)
        self.assertEqual(len(result.aggregates), 2)
        first, second = result.aggregates
        self.assertEqual(first.start, at(9, 0))
        self.assertEqual(first.end, at(9, 5))
        self.assertEqual(first.open, Decimal("100"))
        self.assertEqual(first.high, Decimal("106"))
        self.assertEqual(first.low, Decimal("99"))
        self.assertEqual(first.close, Decimal("105"))
        self.assertEqual(first.volume, Decimal("5"))
        self.assertEqual(first.volume_status, VOLUME_STATUS_COMPLETE)
        self.assertEqual(first.trading_day, DAY)
        self.assertEqual(second.start, at(9, 5))
        self.assertEqual(second.end, at(9, 10))
        self.assertEqual(second.open, Decimal("105"))
        self.assertEqual(second.high, Decimal("111"))
        self.assertEqual(second.low, Decimal("104"))
        self.assertEqual(second.close, Decimal("110"))
        self.assertEqual(second.volume, Decimal("5"))

    def test_one_minute_to_thirty_minute_correctness(self):
        aggregator = TimeframeAggregator(SESSIONS)
        bars = ramp_bars(at(9, 0), 60)
        result = aggregator.aggregate(bars, spec=SPEC_30M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(result.aggregates), 2)
        first, second = result.aggregates
        self.assertEqual(first.start, at(9, 0))
        self.assertEqual(first.end, at(9, 30))
        self.assertEqual(first.open, Decimal("100"))
        self.assertEqual(first.high, Decimal("131"))
        self.assertEqual(first.low, Decimal("99"))
        self.assertEqual(first.close, Decimal("130"))
        self.assertEqual(second.start, at(9, 30))
        self.assertEqual(second.end, at(10, 0))
        self.assertEqual(second.open, Decimal("130"))
        self.assertEqual(second.close, Decimal("160"))

    def test_session_break_is_never_bridged(self):
        aggregator = TimeframeAggregator(BREAK_SESSIONS)
        bars = ramp_bars(at(9, 0), 10, sessions=BREAK_SESSIONS)
        bars += ramp_bars(at(10, 30), 10, sessions=BREAK_SESSIONS)
        result = aggregator.aggregate(bars, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(result.aggregates), 4)
        starts = [item.start for item in result.aggregates]
        self.assertEqual(starts, [at(9, 0), at(9, 5), at(10, 30), at(10, 35)])
        # No aggregate may span the 09:09 -> 10:30 break.
        self.assertFalse(any(item.start < at(10, 30) < item.end for item in result.aggregates))
        self.assertEqual(result.incomplete_buckets, ())

    def test_lunch_break_is_never_bridged_to_fill_a_sixty_minute_bucket(self):
        aggregator = TimeframeAggregator(LUNCH_SESSIONS)
        bars = ramp_bars(at(9, 0), 30, sessions=LUNCH_SESSIONS)
        bars += ramp_bars(at(10, 0), 30, sessions=LUNCH_SESSIONS)
        result = aggregator.aggregate(bars, spec=SPEC_60M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        # Each window is only 30 minutes; a 60m bucket cannot be completed
        # inside one session window, and bridging the lunch break is forbidden.
        self.assertEqual(result.aggregates, ())
        self.assertEqual(result.incomplete_buckets, ())

    def test_night_session_uses_official_trading_day(self):
        aggregator = TimeframeAggregator(SESSIONS)
        bars = ramp_bars(at(21, 0, FRIDAY), 10)
        result = aggregator.aggregate(bars, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(result.aggregates), 2)
        for item in result.aggregates:
            self.assertEqual(item.trading_day, DAY)  # official Monday, not civil Friday
        self.assertEqual(result.aggregates[0].start, at(21, 0, FRIDAY))

    def test_daily_aggregation_follows_official_trading_day_not_civil_date(self):
        aggregator = TimeframeAggregator(SESSIONS)
        night = ramp_bars(at(21, 0, FRIDAY), 5)
        day = ramp_bars(at(9, 0), 5)
        result = aggregator.aggregate(night + day, spec=SPEC_DAILY, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(result.aggregates), 1)
        daily = result.aggregates[0]
        # Keyed by the official trading day (Monday), even though it contains
        # civil-Friday night bars and civil-Monday day bars.
        self.assertEqual(daily.trading_day, DAY)
        self.assertEqual(daily.start, at(21, 0, FRIDAY))
        self.assertEqual(daily.end, at(9, 5))
        self.assertEqual(daily.open, Decimal("100"))
        self.assertEqual(daily.close, Decimal("105"))
        self.assertEqual(daily.high, Decimal("106"))
        self.assertEqual(daily.low, Decimal("99"))
        self.assertEqual(daily.volume, Decimal("10"))
        self.assertEqual(daily.volume_status, VOLUME_STATUS_COMPLETE)
        self.assertIsNone(daily.session_kind)

    def test_missing_constituent_minute_fails_closed(self):
        # Window 09:00-09:10 holds exactly two 5m buckets; 09:04 is absent.
        aggregator = TimeframeAggregator(BREAK_SESSIONS)
        bars = [
            make_bar(at(9, m), at(9, m + 1), 100, 102, 99, 101, volume=1, sessions=BREAK_SESSIONS)
            for m in range(5)
            if m != 4
        ]
        bars += [
            make_bar(at(9, m), at(9, m + 1), 100, 102, 99, 101, volume=1, sessions=BREAK_SESSIONS)
            for m in range(5, 10)
        ]
        result = aggregator.aggregate(bars, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(result.aggregates), 1)
        self.assertEqual(result.aggregates[0].start, at(9, 5))
        self.assertEqual(len(result.incomplete_buckets), 1)
        bucket = result.incomplete_buckets[0]
        self.assertIsInstance(bucket, IncompleteBucket)
        self.assertEqual(bucket.start, at(9, 0))
        self.assertEqual(bucket.end, at(9, 5))
        self.assertEqual(bucket.missing_constituent_starts, (at(9, 4),))
        self.assertEqual(bucket.present_constituent_count, 4)

    def test_generic_interval_support_15m_30m_60m_120m_daily(self):
        aggregator = TimeframeAggregator(LONG_DAY_SESSIONS)
        bars = ramp_bars(at(9, 0), 150, sessions=LONG_DAY_SESSIONS)
        fifteen = aggregator.aggregate(bars, spec=SPEC_15M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(fifteen.aggregates), 10)
        thirty = aggregator.aggregate(bars, spec=SPEC_30M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(thirty.aggregates), 5)
        sixty = aggregator.aggregate(bars, spec=SPEC_60M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(sixty.aggregates), 2)
        self.assertEqual(sixty.aggregates[0].start, at(9, 0))
        self.assertEqual(sixty.aggregates[1].start, at(10, 0))
        one_twenty = aggregator.aggregate(bars, spec=SPEC_120M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(one_twenty.aggregates), 1)
        self.assertEqual(one_twenty.aggregates[0].start, at(9, 0))
        daily = aggregator.aggregate(bars, spec=SPEC_DAILY, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(daily.aggregates), 1)
        self.assertEqual(daily.aggregates[0].trading_day, DAY)

    def test_volume_unknown_is_preserved_not_fabricated_as_zero(self):
        aggregator = TimeframeAggregator(SESSIONS)
        bars = []
        for index in range(5):
            bar_start = at(9, 0) + timedelta(minutes=index)
            volume = None if index == 2 else 7
            bars.append(
                make_bar(bar_start, bar_start + timedelta(minutes=1), 100, 102, 99, 101, volume=volume)
            )
        result = aggregator.aggregate(bars, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(result.aggregates), 1)
        aggregate = result.aggregates[0]
        self.assertIsNone(aggregate.volume)
        self.assertEqual(aggregate.volume_status, VOLUME_STATUS_UNKNOWN)


class AggregationIdentityAndAvailabilityTests(unittest.TestCase):
    def test_aggregate_available_at_respects_latest_constituent(self):
        aggregator = TimeframeAggregator(SESSIONS)
        bars = ramp_bars(at(9, 0), 5, available_delta=timedelta(minutes=10))
        result = aggregator.aggregate(bars, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(result.aggregates), 1)
        self.assertEqual(result.aggregates[0].available_at, at(9, 5) + timedelta(minutes=10))
        self.assertEqual(result.aggregates[0].start, at(9, 0))
        self.assertEqual(result.aggregates[0].end, at(9, 5))

    def test_aggregate_identity_deterministic_and_sensitive_to_source_evidence(self):
        aggregator = TimeframeAggregator(SESSIONS)
        bars = ramp_bars(at(9, 0), 10)
        first = aggregator.aggregate(bars, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        repeated = aggregator.aggregate(bars, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(first.aggregates[0].identity_id, repeated.aggregates[0].identity_id)

        # Equivalent input evidence (same bar objects) -> same aggregate identity.
        self.assertEqual(first.aggregates[0].identity_id, first.aggregates[0].identity_id)

        # Changed constituent evidence -> changed identity.
        changed = list(bars)
        original = changed[3]
        changed[3] = make_bar(
            original.completed_bar.start,
            original.completed_bar.end,
            900,
            902,
            899,
            901,
            volume=original.volume,
            available_at=original.completed_bar.available_at,
        )
        changed_result = aggregator.aggregate(changed, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertNotEqual(first.aggregates[0].identity_id, changed_result.aggregates[0].identity_id)

        # Changed timeframe spec -> changed identity.
        other_spec = TimeframeSpec("5m", "INTRADAY", 300, "v2")
        other_result = aggregator.aggregate(bars, spec=other_spec, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertNotEqual(first.aggregates[0].identity_id, other_result.aggregates[0].identity_id)

    def test_future_bar_cannot_affect_earlier_aggregate(self):
        aggregator = TimeframeAggregator(SESSIONS)
        bars = ramp_bars(at(9, 0), 10)
        baseline = aggregator.aggregate(bars, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        first_baseline = baseline.aggregates[0]
        self.assertEqual(first_baseline.end, at(9, 5))

        # Change only a later bar (09:08) to an extreme value.
        altered = list(bars)
        later = altered[8]
        altered[8] = make_bar(
            later.completed_bar.start,
            later.completed_bar.end,
            5000,
            5002,
            4999,
            5001,
            volume=later.volume,
            available_at=later.completed_bar.available_at,
        )
        altered_result = aggregator.aggregate(altered, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        altered_first = altered_result.aggregates[0]
        self.assertEqual(altered_first.open, first_baseline.open)
        self.assertEqual(altered_first.high, first_baseline.high)
        self.assertEqual(altered_first.low, first_baseline.low)
        self.assertEqual(altered_first.close, first_baseline.close)
        self.assertEqual(altered_first.volume, first_baseline.volume)
        self.assertEqual(altered_first.identity_id, first_baseline.identity_id)

    def test_future_availability_does_not_earlier_visibility(self):
        aggregator = TimeframeAggregator(SESSIONS)
        bars = ramp_bars(at(9, 0), 10, available_delta=timedelta(0))
        delayed = make_bar(
            at(9, 9),
            at(10, 0),
            100,
            102,
            99,
            101,
            volume=Decimal("1"),
            available_at=at(10, 0) + timedelta(hours=1),
        )
        bars[9] = delayed
        result = aggregator.aggregate(bars, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        self.assertEqual(len(result.aggregates), 2)
        first, second = result.aggregates
        self.assertEqual(first.available_at, at(9, 5))
        self.assertEqual(second.available_at, at(11, 0))
        # At 09:06 only the first aggregate is available.
        self.assertEqual(visible_aggregates(result.aggregates, at(9, 6)), (first,))
        # The second aggregate must not be visible before its latest constituent.
        self.assertEqual(visible_aggregates(result.aggregates, at(10, 30)), (first,))
        self.assertEqual(visible_aggregates(result.aggregates, at(11, 0)), (first, second))


class EMATests(unittest.TestCase):
    def test_ema_known_hand_computed_sequence(self):
        values = compute_ema(flat_aggregates([1, 2, 3, 4, 5]), period=3, price_field="close")
        self.assertEqual(len(values), 5)
        self.assertEqual(values[0].status, STATUS_INSUFFICIENT_HISTORY)
        self.assertIsNone(values[0].value)
        self.assertEqual(values[1].status, STATUS_INSUFFICIENT_HISTORY)
        self.assertIsNone(values[1].value)
        self.assertEqual(values[2].status, STATUS_READY)
        self.assertEqual(values[2].value, Decimal("2"))
        self.assertEqual(values[3].value, Decimal("3"))
        self.assertEqual(values[4].value, Decimal("4"))
        # Availability boundary binds the source aggregate.
        self.assertEqual(values[4].source_aggregate_identity, flat_aggregates([1, 2, 3, 4, 5])[4].identity_id)

    def test_ema_insufficient_history_behavior(self):
        short = compute_ema(flat_aggregates([1, 2]), period=3, price_field="close")
        self.assertEqual([item.status for item in short], [STATUS_INSUFFICIENT_HISTORY, STATUS_INSUFFICIENT_HISTORY])
        self.assertTrue(all(item.value is None for item in short))
        boundary = compute_ema(flat_aggregates([1, 2, 3]), period=3, price_field="close")
        self.assertEqual(
            [item.status for item in boundary],
            [STATUS_INSUFFICIENT_HISTORY, STATUS_INSUFFICIENT_HISTORY, STATUS_READY],
        )
        self.assertEqual(boundary[2].value, Decimal("2"))

    def test_ema_no_future_leakage(self):
        closes = [1, 2, 3, 4, 5, 6, 7, 8]
        full = compute_ema(flat_aggregates(closes), period=3, price_field="close")
        prefix = compute_ema(flat_aggregates(closes[:4]), period=3, price_field="close")
        self.assertEqual(full[3].value, prefix[3].value)
        # A later close cannot change an earlier EMA value or identity.
        altered = compute_ema(flat_aggregates([1, 2, 3, 4, 999]), period=3, price_field="close")
        for index in range(4):
            self.assertEqual(full[index].value, altered[index].value)
            self.assertEqual(full[index].feature_identity, altered[index].feature_identity)

    def test_ema_identity_changes_with_price_field_and_period(self):
        closes = [1, 2, 3, 4, 5]
        base = compute_ema(flat_aggregates(closes), period=3, price_field="close")
        other_period = compute_ema(flat_aggregates(closes), period=4, price_field="close")
        other_field = compute_ema(flat_aggregates(closes), period=3, price_field="open")
        ready_base = [item for item in base if item.status == STATUS_READY]
        ready_period = [item for item in other_period if item.status == STATUS_READY]
        ready_field = [item for item in other_field if item.status == STATUS_READY]
        self.assertTrue(ready_base)
        self.assertTrue(ready_period)
        self.assertTrue(ready_field)
        self.assertNotEqual(ready_base[0].feature_identity, ready_period[0].feature_identity)
        self.assertNotEqual(ready_base[0].feature_identity, ready_field[0].feature_identity)

    def test_ema_identity_stable_for_equivalent_evidence(self):
        closes = [1, 2, 3, 4, 5]
        first = compute_ema(flat_aggregates(closes), period=3, price_field="close")
        repeated = compute_ema(flat_aggregates(closes), period=3, price_field="close")
        self.assertEqual(
            [item.feature_identity for item in first],
            [item.feature_identity for item in repeated],
        )
        self.assertEqual(first[2].feature_identity, repeated[2].feature_identity)

    def test_ema_binds_timeframe_aggregation_identity(self):
        closes = [1, 2, 3, 4, 5]
        five = compute_ema(flat_aggregates(closes, ), period=3, price_field="close")
        aggregates_60 = [
            make_aggregate(index, value, value, value, value, spec=SPEC_60M)
            for index, value in enumerate(closes)
        ]
        sixty = compute_ema(aggregates_60, period=3, price_field="close")
        self.assertNotEqual(five[4].timeframe_aggregation_identity, sixty[4].timeframe_aggregation_identity)
        self.assertNotEqual(five[4].feature_identity, sixty[4].feature_identity)


class WilderAdxTests(unittest.TestCase):
    ADX_FIXTURE = [
        (100, 102, 99, 101),
        (101, 105, 100, 104),
        (104, 106, 102, 103),
        (103, 104, 99, 100),
        (100, 108, 99, 107),
    ]

    def adx_bars(self, count: int = 5):
        return [
            make_aggregate(index, *self.ADX_FIXTURE[index % len(self.ADX_FIXTURE)])
            for index in range(count)
        ]

    def test_wilder_tr_plus_dm_minus_dm_hand_cases(self):
        tr, plus_dm, minus_dm = wilder_directional_movement(self.adx_bars())
        self.assertEqual(
            tr,
            (None, Decimal("5"), Decimal("4"), Decimal("5"), Decimal("9")),
        )
        self.assertEqual(
            plus_dm,
            (None, Decimal("3"), Decimal("1"), Decimal("0"), Decimal("4")),
        )
        self.assertEqual(
            minus_dm,
            (None, Decimal("0"), Decimal("0"), Decimal("3"), Decimal("0")),
        )

    def test_adx_hand_computed_fixture(self):
        values = compute_adx(self.adx_bars(), period=2)
        self.assertEqual(len(values), 5)
        # Warmup: first ADX appears at aggregate index 2*period-1 == 3.
        self.assertEqual(
            [item.status for item in values],
            [
                STATUS_INSUFFICIENT_HISTORY,
                STATUS_INSUFFICIENT_HISTORY,
                STATUS_INSUFFICIENT_HISTORY,
                STATUS_READY,
                STATUS_READY,
            ],
        )
        self.assertEqual(values[0].adx, None)
        self.assertEqual(values[1].adx, None)
        self.assertEqual(values[2].adx, None)
        # DI/DX diagnostics are available from the first smoothed value.
        self.assertEqual(values[2].plus_di, Decimal("44.444444"))
        self.assertEqual(values[2].minus_di, Decimal("0"))
        self.assertEqual(values[2].dx, Decimal("100"))
        self.assertEqual(values[3].adx, Decimal("60"))
        self.assertEqual(values[3].plus_di, Decimal("21.052632"))
        self.assertEqual(values[3].minus_di, Decimal("31.578947"))
        self.assertEqual(values[3].dx, Decimal("20"))
        self.assertEqual(values[4].adx, Decimal("56.923077"))
        self.assertEqual(values[4].plus_di, Decimal("36.363636"))
        self.assertEqual(values[4].minus_di, Decimal("10.909091"))
        self.assertEqual(values[4].dx, Decimal("53.846154"))

    def test_adx_insufficient_history_behavior(self):
        values = compute_adx(self.adx_bars()[:5], period=3)
        # first_adx_index == 5 with only 5 aggregates -> all insufficient.
        self.assertEqual(len(values), 5)
        self.assertTrue(all(item.status == STATUS_INSUFFICIENT_HISTORY for item in values))
        self.assertTrue(all(item.adx is None for item in values))

    def test_adx_no_future_leakage(self):
        full = compute_adx(self.adx_bars(), period=2)
        prefix = compute_adx(self.adx_bars()[:4], period=2)
        self.assertEqual(full[3].adx, prefix[3].adx)
        # Change only the last bar's price: earlier ADX values must not move.
        altered_bars = list(self.adx_bars())
        altered_bars[4] = make_aggregate(4, 200, 208, 199, 207)
        altered = compute_adx(altered_bars, period=2)
        for index in range(4):
            self.assertEqual(full[index].adx, altered[index].adx)
            self.assertEqual(full[index].feature_identity, altered[index].feature_identity)
        self.assertNotEqual(full[4].adx, altered[4].adx)

    def test_adx_identity_changes_with_period_and_evidence(self):
        # Ten aggregates give READY ADX values for both period=2 and period=3.
        base = compute_adx(self.adx_bars(10), period=2)
        other_period = compute_adx(self.adx_bars(10), period=3)
        ready_base = [item for item in base if item.status == STATUS_READY]
        ready_period = [item for item in other_period if item.status == STATUS_READY]
        self.assertTrue(ready_base)
        self.assertTrue(ready_period)
        self.assertNotEqual(ready_base[0].feature_identity, ready_period[0].feature_identity)
        # Same evidence -> stable identity.
        repeated = compute_adx(self.adx_bars(10), period=2)
        self.assertEqual(
            [item.feature_identity for item in base],
            [item.feature_identity for item in repeated],
        )

    def test_adx_undefined_when_directional_denominator_is_zero(self):
        flat = [make_aggregate(index, 100, 100, 100, 100) for index in range(8)]
        values = compute_adx(flat, period=2)
        # With all-flat OHLC, TR is zero so +DI/-DI/DX cannot be computed.
        # Warmup (before first_adx_index == 3) stays INSUFFICIENT_HISTORY;
        # once the ADX would be due it fails closed as UNDEFINED, never 0.
        self.assertTrue(all(item.adx is None for item in values))
        self.assertEqual([item.status for item in values[:3]], [STATUS_INSUFFICIENT_HISTORY] * 3)
        self.assertEqual([item.status for item in values[3:]], [STATUS_UNDEFINED] * 5)


class FeatureIdentityTests(unittest.TestCase):
    def test_feature_value_identity_binds_algorithm_version(self):
        closes = [1, 2, 3, 4, 5]
        values = compute_ema(flat_aggregates(closes), period=3, price_field="close")
        ready = [item for item in values if item.status == STATUS_READY][0]
        other = FeatureValue(
            feature_type=FEATURE_TYPE_EMA,
            algorithm_version="different-algorithm-v9",
            parameters=(("period", 3), ("price_field", "close")),
            feature_version=ready.feature_version,
            timeframe_aggregation_identity=ready.timeframe_aggregation_identity,
            source_aggregate_identity=ready.source_aggregate_identity,
            available_at=ready.available_at,
            status=ready.status,
            value=ready.value,
        )
        self.assertNotEqual(ready.feature_identity, other.feature_identity)
        # Changing feature type also changes identity.
        adx_values = compute_adx(flat_aggregates(closes), period=2)
        self.assertTrue(any(item.feature_type == FEATURE_TYPE_ADX for item in adx_values))

    def test_feature_identity_changes_with_input_evidence(self):
        base = compute_ema(flat_aggregates([1, 2, 3, 4, 5]), period=3, price_field="close")
        changed = compute_ema(flat_aggregates([1, 2, 3, 4, 6]), period=3, price_field="close")
        self.assertNotEqual(base[4].feature_identity, changed[4].feature_identity)
        self.assertNotEqual(base[4].source_aggregate_identity, changed[4].source_aggregate_identity)


class SeriesValidationTests(unittest.TestCase):
    def test_aggregation_rejects_out_of_order_bars(self):
        aggregator = TimeframeAggregator(SESSIONS)
        bars = ramp_bars(at(9, 0), 5)
        with self.assertRaisesRegex(ValueError, "strictly ordered"):
            aggregator.aggregate(
                [bars[2], bars[0], bars[1], bars[3], bars[4]],
                spec=SPEC_5M,
                exchange="SHFE",
                concrete_instrument="SHFE.cu2501",
            )

    def test_aggregation_rejects_duplicate_starts(self):
        aggregator = TimeframeAggregator(SESSIONS)
        bars = ramp_bars(at(9, 0), 5)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            aggregator.aggregate(
                bars + [bars[0]],
                spec=SPEC_5M,
                exchange="SHFE",
                concrete_instrument="SHFE.cu2501",
            )

    def test_aggregation_rejects_bars_outside_published_sessions(self):
        aggregator = TimeframeAggregator(SESSIONS)
        bars = ramp_bars(at(9, 0), 5)
        # Civil 12:00 is outside every published session; the trading day is
        # forced so the fixture itself constructs, then the aggregator must
        # fail closed.
        stray = make_bar(at(12, 0), at(12, 1), 100, 102, 99, 101, trading_day=DAY)
        with self.assertRaisesRegex(ValueError, "outside published sessions"):
            aggregator.aggregate(
                bars + [stray],
                spec=SPEC_5M,
                exchange="SHFE",
                concrete_instrument="SHFE.cu2501",
            )

    def test_ema_rejects_out_of_order_aggregates(self):
        bars = flat_aggregates([1, 2, 3, 4, 5])
        with self.assertRaisesRegex(ValueError, "strictly ordered"):
            compute_ema([bars[2], bars[0], bars[1], bars[3], bars[4]], period=3, price_field="close")

    def test_adx_rejects_overlapping_aggregates(self):
        bars = flat_aggregates([1, 2, 3, 4, 5])
        overlapping = [
            make_aggregate(0, 1, 1, 1, 1, start=at(9, 0)),
            make_aggregate(1, 2, 2, 2, 2, start=at(9, 2)),  # overlaps [09:00,09:05)
        ]
        with self.assertRaisesRegex(ValueError, "must not overlap"):
            compute_adx([overlapping[0], overlapping[1]], period=2)

    def test_ema_rejects_mixed_timeframe_aggregates(self):
        bars = [
            make_aggregate(0, 1, 1, 1, 1, spec=SPEC_5M),
            make_aggregate(1, 2, 2, 2, 2, spec=SPEC_60M),
        ]
        with self.assertRaisesRegex(ValueError, "one timeframe aggregation identity"):
            compute_ema(bars, period=3, price_field="close")


class VisibilityTests(unittest.TestCase):
    def test_visible_features_respect_availability_boundary(self):
        closes = [1, 2, 3, 4, 5]
        values = compute_ema(flat_aggregates(closes), period=3, price_field="close")
        third_start = flat_aggregates(closes)[2].available_at
        visible = visible_features(values, third_start)
        self.assertEqual(len(visible), 3)
        self.assertTrue(all(item.available_at <= third_start for item in visible))

    def test_aggregate_visibility_matches_completed_bar_semantics(self):
        aggregator = TimeframeAggregator(SESSIONS)
        bars = ramp_bars(at(9, 0), 5)
        result = aggregator.aggregate(bars, spec=SPEC_5M, exchange="SHFE", concrete_instrument="SHFE.cu2501")
        aggregate = result.aggregates[0]
        self.assertFalse(aggregate.is_visible_at(at(9, 4, FRIDAY)))
        self.assertTrue(aggregate.is_visible_at(aggregate.available_at))


if __name__ == "__main__":
    unittest.main()

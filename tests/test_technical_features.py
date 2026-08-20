import unittest
from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from src.data_substrate import CompletedBar, SessionMetadata, SessionWindow
from src.historical_data import NormalizedHistoricalBar
from src.strategy_evidence import ArtifactBinding
from src.technical_features import (
    FEATURE_IMPLEMENTATION_BINDING,
    AggregationResult,
    FeatureNumericPolicy,
    STATUS_READY,
    TimeframeAggregator,
    TimeframeSpec,
    compute_adx,
    compute_ema,
)


CN = ZoneInfo("Asia/Shanghai")
DAY = date(2025, 1, 6)
TEST_ONLY_NUMERIC_POLICY = FeatureNumericPolicy(
    ema_seed_method="SMA",
    adx_initialization_method="WILDER_SMA_DX",
    internal_precision_policy="FULL_DECIMAL",
    output_quantum=Decimal("0.000001"),
    rounding_mode="ROUND_HALF_UP",
)


def at(hour: int, minute: int) -> datetime:
    return datetime(2025, 1, 6, hour, minute, tzinfo=CN)


def make_sessions(*, second_instrument: str | None = None) -> SessionMetadata:
    windows = [
        SessionWindow("SHFE", "cu2502", DAY, at(9, 0), at(9, 3), "DAY_1"),
        SessionWindow("SHFE", "cu2502", DAY, at(10, 0), at(10, 3), "DAY_2"),
    ]
    if second_instrument is not None:
        windows.append(
            SessionWindow("SHFE", second_instrument, DAY, at(9, 0), at(9, 3), "DAY_1")
        )
    return SessionMetadata("synthetic-session-authority-v1", windows)


def make_bar(
    start: datetime,
    close: Decimal,
    *,
    instrument: str = "cu2502",
    exchange: str = "SHFE",
    raw_identity: str | None = None,
) -> NormalizedHistoricalBar:
    return NormalizedHistoricalBar(
        exchange=exchange,
        concrete_instrument=instrument,
        source_event_at=start + timedelta(minutes=1),
        source_retrieved_at=start + timedelta(minutes=1),
        completed_bar=CompletedBar(
            instrument=instrument,
            trading_day=DAY,
            start=start,
            end=start + timedelta(minutes=1),
            available_at=start + timedelta(minutes=1),
        ),
        open=close,
        high=close + Decimal("1"),
        low=close - Decimal("1"),
        close=close,
        volume=Decimal("1"),
        open_interest_start=Decimal("10"),
        open_interest_end=Decimal("11"),
        raw_artifact_identity_id=raw_identity or f"raw-{instrument}-{start.isoformat()}",
        data_version_id="synthetic-data-v1",
    )


def complete_minute_bars() -> tuple[NormalizedHistoricalBar, ...]:
    starts = (at(9, 0), at(9, 1), at(9, 2), at(10, 0), at(10, 1), at(10, 2))
    return tuple(make_bar(start, Decimal(100 + index)) for index, start in enumerate(starts))


def linear_sessions(count: int, *, authority: str = "linear-authority-v1") -> SessionMetadata:
    return SessionMetadata(
        authority,
        (SessionWindow("SHFE", "cu2502", DAY, at(9, 0), at(9, 0) + timedelta(minutes=count), "DAY"),),
    )


def linear_bars(count: int, *, first_raw_identity: str = "raw-first") -> tuple[NormalizedHistoricalBar, ...]:
    return tuple(
        make_bar(
            at(9, 0) + timedelta(minutes=index),
            Decimal(100 + index),
            raw_identity=first_raw_identity if index == 0 else f"raw-{index}",
        )
        for index in range(count)
    )


def linear_aggregation(
    count: int,
    *,
    first_raw_identity: str = "raw-first",
    authority: str = "linear-authority-v1",
) -> AggregationResult:
    sessions = linear_sessions(count, authority=authority)
    return TimeframeAggregator(sessions).aggregate(
        linear_bars(count, first_raw_identity=first_raw_identity),
        spec=TimeframeSpec("1MIN", "INTRADAY", 60, "test-aggregation-v1"),
        exchange="SHFE",
        concrete_instrument="cu2502",
        coverage_start=at(9, 0),
        coverage_end=at(9, 0) + timedelta(minutes=count),
    )


def aggregate(
    bars: tuple[NormalizedHistoricalBar, ...],
    *,
    sessions: SessionMetadata | None = None,
    seconds: int = 180,
) -> AggregationResult:
    authority = sessions or make_sessions()
    return TimeframeAggregator(authority).aggregate(
        bars,
        spec=TimeframeSpec("3MIN", "INTRADAY", seconds, "test-aggregation-v1"),
        exchange="SHFE",
        concrete_instrument="cu2502",
        coverage_start=at(9, 0),
        coverage_end=at(10, 3),
    )


class TimeframeAggregationTests(unittest.TestCase):
    def test_missing_whole_expected_session_is_explicit_incomplete_evidence(self):
        first_session_only = tuple(
            make_bar(at(9, minute), Decimal(100 + minute)) for minute in range(3)
        )
        sessions = make_sessions()

        result = aggregate(first_session_only, sessions=sessions)

        self.assertEqual(1, len(result.aggregates))
        self.assertEqual(1, len(result.incomplete_buckets))
        missing = result.incomplete_buckets[0]
        self.assertEqual((at(10, 0), at(10, 1), at(10, 2)), missing.expected_constituent_starts)
        self.assertEqual((), missing.actual_constituent_starts)
        self.assertEqual(180, missing.timeframe_duration_seconds)
        self.assertEqual(sessions.version, result.session_metadata_version)

    def test_complete_bucket_proves_constituents_bounds_and_duration(self):
        result = aggregate(complete_minute_bars())

        self.assertTrue(result.complete)
        self.assertEqual(2, len(result.aggregates))
        first = result.aggregates[0]
        self.assertEqual((at(9, 0), at(9, 1), at(9, 2)), first.expected_constituent_starts)
        self.assertEqual(first.expected_constituent_starts, first.actual_constituent_starts)
        self.assertEqual(at(9, 0), first.start)
        self.assertEqual(at(9, 3), first.end)
        self.assertEqual(180, first.timeframe_duration_seconds)

    def test_session_shortened_bucket_never_becomes_complete_by_bar_count(self):
        result = aggregate(complete_minute_bars(), seconds=120)

        shortened = [item for item in result.incomplete_buckets if item.boundary_shortened]
        self.assertEqual(2, len(shortened))
        self.assertTrue(all(item.timeframe_duration_seconds == 120 for item in shortened))
        self.assertTrue(all(len(item.expected_constituent_starts) == 1 for item in shortened))

    def test_non_integral_timeframe_and_wrong_source_duration_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "exact multiple"):
            aggregate(complete_minute_bars(), seconds=90)

        first = make_bar(at(9, 0), Decimal("100"))
        wrong_completed = replace(first.completed_bar, end=at(9, 2), available_at=at(9, 2))
        wrong_duration = replace(first, completed_bar=wrong_completed)
        with self.assertRaisesRegex(ValueError, "duration"):
            aggregate((wrong_duration,))

    def test_mixed_concrete_contract_stream_fails_closed(self):
        sessions = make_sessions(second_instrument="cu2503")
        mixed = (
            make_bar(at(9, 0), Decimal("100")),
            make_bar(at(9, 1), Decimal("101"), instrument="cu2503"),
        )
        with self.assertRaisesRegex(ValueError, "one exchange and concrete instrument"):
            aggregate(mixed, sessions=sessions)

    def test_daily_partial_day_is_incomplete(self):
        sessions = make_sessions()
        result = TimeframeAggregator(sessions).aggregate(
            tuple(make_bar(at(9, minute), Decimal(100 + minute)) for minute in range(3)),
            spec=TimeframeSpec("1DAY", "DAILY", None, "test-daily-v1"),
            exchange="SHFE",
            concrete_instrument="cu2502",
            coverage_start=at(9, 0),
            coverage_end=at(10, 3),
        )

        self.assertEqual((), result.aggregates)
        self.assertEqual(1, len(result.incomplete_buckets))
        self.assertEqual((at(10, 0), at(10, 1), at(10, 2)), result.incomplete_buckets[0].missing_constituent_starts)


class FeatureComputationTests(unittest.TestCase):
    def test_gap_evidence_cannot_be_dropped_or_computed_as_continuous(self):
        incomplete = aggregate(complete_minute_bars()[:-1])

        with self.assertRaisesRegex(ValueError, "continuity"):
            compute_ema(
                incomplete,
                period=2,
                price_field="close",
                numeric_policy=TEST_ONLY_NUMERIC_POLICY,
                feature_version="test-ema-v1",
            )
        with self.assertRaisesRegex(ValueError, "AggregationResult"):
            compute_ema(
                incomplete.aggregates,
                period=2,
                price_field="close",
                numeric_policy=TEST_ONLY_NUMERIC_POLICY,
                feature_version="test-ema-v1",
            )
        with self.assertRaises(TypeError):
            AggregationResult(
                aggregates=incomplete.aggregates,
                incomplete_buckets=(),
                expected_bucket_identities=tuple(item.bucket_identity for item in incomplete.aggregates),
                exchange=incomplete.exchange,
                concrete_instrument=incomplete.concrete_instrument,
                timeframe_spec=incomplete.timeframe_spec,
                session_metadata_version=incomplete.session_metadata_version,
                coverage_start=incomplete.coverage_start,
                coverage_end=incomplete.coverage_end,
            )

    def test_earlier_source_evidence_changes_dependency_identity_even_when_value_is_same(self):
        first = linear_aggregation(5, first_raw_identity="raw-first-a")
        changed = linear_aggregation(5, first_raw_identity="raw-first-b")

        first_ema = compute_ema(
            first,
            period=2,
            price_field="close",
            numeric_policy=TEST_ONLY_NUMERIC_POLICY,
            feature_version="test-ema-v1",
        )
        changed_ema = compute_ema(
            changed,
            period=2,
            price_field="close",
            numeric_policy=TEST_ONLY_NUMERIC_POLICY,
            feature_version="test-ema-v1",
        )

        self.assertEqual(first_ema[-1].value, changed_ema[-1].value)
        self.assertNotEqual(
            first_ema[-1].dependency_prefix_identity,
            changed_ema[-1].dependency_prefix_identity,
        )
        self.assertNotEqual(first_ema[-1].feature_identity, changed_ema[-1].feature_identity)

    def test_feature_identity_binds_actual_implementation_bytes(self):
        result = linear_aggregation(3)
        feature = compute_ema(
            result,
            period=2,
            price_field="close",
            numeric_policy=TEST_ONLY_NUMERIC_POLICY,
            feature_version="test-ema-v1",
        )[-1]
        source_bytes = Path(FEATURE_IMPLEMENTATION_BINDING.artifact_reference).read_bytes()
        changed_binding = ArtifactBinding.from_bytes(
            artifact_kind="feature",
            artifact_reference=FEATURE_IMPLEMENTATION_BINDING.artifact_reference,
            content=source_bytes + b"\n# synthetic byte change",
            declared_version=FEATURE_IMPLEMENTATION_BINDING.declared_version,
        )

        self.assertEqual(FEATURE_IMPLEMENTATION_BINDING.identity_id, feature.implementation_artifact_identity)
        self.assertNotEqual(FEATURE_IMPLEMENTATION_BINDING.identity_id, changed_binding.identity_id)
        self.assertNotEqual(
            feature.feature_identity,
            replace(feature, implementation_artifact_identity=changed_binding.identity_id).feature_identity,
        )

    def test_numeric_policy_and_session_authority_enter_feature_identity(self):
        first = linear_aggregation(3, authority="authority-a")
        changed_authority = linear_aggregation(3, authority="authority-b")
        alternate_policy = FeatureNumericPolicy(
            ema_seed_method="SMA",
            adx_initialization_method="WILDER_SMA_DX",
            internal_precision_policy="FULL_DECIMAL",
            output_quantum=Decimal("0.000001"),
            rounding_mode="ROUND_HALF_EVEN",
        )

        first_value = compute_ema(
            first,
            period=2,
            price_field="close",
            numeric_policy=TEST_ONLY_NUMERIC_POLICY,
            feature_version="test-ema-v1",
        )[-1]
        authority_value = compute_ema(
            changed_authority,
            period=2,
            price_field="close",
            numeric_policy=TEST_ONLY_NUMERIC_POLICY,
            feature_version="test-ema-v1",
        )[-1]
        policy_value = compute_ema(
            first,
            period=2,
            price_field="close",
            numeric_policy=alternate_policy,
            feature_version="test-ema-v1",
        )[-1]

        self.assertNotEqual(first.session_metadata_version, changed_authority.session_metadata_version)
        self.assertNotEqual(first_value.feature_identity, authority_value.feature_identity)
        self.assertEqual(first_value.value, policy_value.value)
        self.assertNotEqual(first_value.feature_identity, policy_value.feature_identity)

    def test_appending_future_bars_does_not_change_existing_feature_identities(self):
        sessions = linear_sessions(6)
        aggregator = TimeframeAggregator(sessions)
        spec = TimeframeSpec("1MIN", "INTRADAY", 60, "test-aggregation-v1")
        first_five = aggregator.aggregate(
            linear_bars(5),
            spec=spec,
            exchange="SHFE",
            concrete_instrument="cu2502",
            coverage_start=at(9, 0),
            coverage_end=at(9, 5),
        )
        with_future = aggregator.aggregate(
            linear_bars(6),
            spec=spec,
            exchange="SHFE",
            concrete_instrument="cu2502",
            coverage_start=at(9, 0),
            coverage_end=at(9, 6),
        )

        first_features = compute_ema(
            first_five,
            period=2,
            price_field="close",
            numeric_policy=TEST_ONLY_NUMERIC_POLICY,
            feature_version="test-ema-v1",
        )
        future_features = compute_ema(
            with_future,
            period=2,
            price_field="close",
            numeric_policy=TEST_ONLY_NUMERIC_POLICY,
            feature_version="test-ema-v1",
        )

        self.assertEqual(
            tuple(item.feature_identity for item in first_features),
            tuple(item.feature_identity for item in future_features[:5]),
        )

    def test_generic_ema_and_wilder_adx_require_explicit_periods_and_policy(self):
        result = linear_aggregation(8)

        ema = compute_ema(
            result,
            period=2,
            price_field="close",
            numeric_policy=TEST_ONLY_NUMERIC_POLICY,
            feature_version="test-ema-v1",
        )
        adx = compute_adx(
            result,
            period=2,
            numeric_policy=TEST_ONLY_NUMERIC_POLICY,
            feature_version="test-adx-v1",
        )

        self.assertEqual(STATUS_READY, ema[-1].status)
        self.assertEqual(STATUS_READY, adx[-1].status)
        self.assertEqual(("period", 2), adx[-1].parameters[0])
        with self.assertRaisesRegex(ValueError, "positive integer"):
            compute_ema(
                result,
                period=0,
                price_field="close",
                numeric_policy=TEST_ONLY_NUMERIC_POLICY,
                feature_version="test-ema-v1",
            )


if __name__ == "__main__":
    unittest.main()

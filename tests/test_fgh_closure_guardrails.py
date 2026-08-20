import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.data_substrate import CompletedBar, SessionMetadata, SessionWindow
from src.historical_data import NormalizedHistoricalBar
from src.technical_features import (
    AggregationResult,
    FeatureNumericPolicy,
    TimeframeAggregator,
    TimeframeSpec,
    compute_adx,
    compute_ema,
)


CN = ZoneInfo("Asia/Shanghai")
DAY = date(2025, 1, 6)
POLICY = FeatureNumericPolicy(
    ema_seed_method="SMA",
    adx_initialization_method="WILDER_SMA_DX",
    internal_precision_policy="FULL_DECIMAL",
    output_quantum=Decimal("0.000001"),
    rounding_mode="ROUND_HALF_UP",
)


def at(minute: int) -> datetime:
    return datetime(2025, 1, 6, 9, minute, tzinfo=CN)


def make_bar(minute: int) -> NormalizedHistoricalBar:
    start = at(minute)
    close = Decimal(100 + minute)
    return NormalizedHistoricalBar(
        exchange="SHFE",
        concrete_instrument="cu2502",
        source_event_at=start + timedelta(minutes=1),
        source_retrieved_at=start + timedelta(minutes=1),
        completed_bar=CompletedBar(
            instrument="cu2502",
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
        raw_artifact_identity_id=f"closure-raw-{minute}",
        data_version_id="closure-synthetic-data-v1",
    )


def aggregate(minutes: tuple[int, ...]) -> AggregationResult:
    sessions = SessionMetadata(
        "closure-session-authority-v1",
        (SessionWindow("SHFE", "cu2502", DAY, at(0), at(4), "DAY"),),
    )
    return TimeframeAggregator(sessions).aggregate(
        tuple(make_bar(minute) for minute in minutes),
        spec=TimeframeSpec("1MIN", "INTRADAY", 60, "closure-aggregation-v1"),
        exchange="SHFE",
        concrete_instrument="cu2502",
        coverage_start=at(0),
        coverage_end=at(4),
    )


def forge_clean_envelope(incomplete: AggregationResult) -> AggregationResult:
    return AggregationResult._from_aggregation(
        aggregates=incomplete.aggregates,
        incomplete_buckets=(),
        expected_bucket_identities=tuple(
            item.bucket_identity for item in incomplete.aggregates
        ),
        exchange=incomplete.exchange,
        concrete_instrument=incomplete.concrete_instrument,
        timeframe_spec=incomplete.timeframe_spec,
        session_metadata_version=incomplete.session_metadata_version,
        coverage_start=incomplete.coverage_start,
        coverage_end=incomplete.coverage_end,
    )


class FGHClosureGuardrailTests(unittest.TestCase):
    def test_manual_clean_envelope_cannot_enter_any_feature_computation(self):
        incomplete = aggregate((0, 1, 3))
        self.assertTrue(incomplete.incomplete_buckets)

        forged = forge_clean_envelope(incomplete)
        self.assertTrue(forged.complete)

        with self.assertRaisesRegex(ValueError, "not issued"):
            compute_ema(
                forged,
                period=2,
                price_field="close",
                numeric_policy=POLICY,
                feature_version="closure-ema-v1",
            )
        with self.assertRaisesRegex(ValueError, "not issued"):
            compute_adx(
                forged,
                period=2,
                numeric_policy=POLICY,
                feature_version="closure-adx-v1",
            )

    def test_aggregator_issued_complete_result_computes_normally(self):
        complete = aggregate((0, 1, 2, 3))

        self.assertTrue(complete.complete)
        self.assertEqual(
            4,
            len(
                compute_ema(
                    complete,
                    period=2,
                    price_field="close",
                    numeric_policy=POLICY,
                    feature_version="closure-ema-v1",
                )
            ),
        )
        self.assertEqual(
            4,
            len(
                compute_adx(
                    complete,
                    period=2,
                    numeric_policy=POLICY,
                    feature_version="closure-adx-v1",
                )
            ),
        )

    def test_aggregator_issued_incomplete_result_still_fails_continuity(self):
        incomplete = aggregate((0, 1, 3))

        with self.assertRaisesRegex(ValueError, "continuity"):
            compute_ema(
                incomplete,
                period=2,
                price_field="close",
                numeric_policy=POLICY,
                feature_version="closure-ema-v1",
            )
        with self.assertRaisesRegex(ValueError, "continuity"):
            compute_adx(
                incomplete,
                period=2,
                numeric_policy=POLICY,
                feature_version="closure-adx-v1",
            )


if __name__ == "__main__":
    unittest.main()

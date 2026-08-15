import unittest
from dataclasses import replace
from datetime import date, datetime
from decimal import Decimal
import json
from zoneinfo import ZoneInfo

from src.data_substrate import SessionMetadata, SessionWindow
from src.historical_data import (
    DataVersionIdentity,
    NormalizerIdentity,
    RawArtifact,
    SourceIdentity,
    normalize_tqsdk_historical_bars,
)


CN = ZoneInfo("Asia/Shanghai")
UTC = ZoneInfo("UTC")


def nanoseconds(timestamp: datetime) -> int:
    return int(timestamp.timestamp() * 1_000_000_000)


class HistoricalDataIdentityTests(unittest.TestCase):
    def test_data_version_is_deterministic_and_changes_with_outcome_affecting_inputs(self):
        source = SourceIdentity(
            provider="TQSDK",
            source_type="PROFESSIONAL_HISTORICAL_API",
            endpoint_identity="TqApi.get_kline_data_series",
            provider_dataset_version=None,
            retrieved_at=datetime(2026, 8, 16, 2, 0, tzinfo=UTC),
            request_parameters=(
                ("duration_seconds", "60"),
                ("end_dt", "2025-06-16"),
                ("start_dt", "2025-06-16"),
                ("symbol", "SHFE.ni2509"),
            ),
        )
        artifact = RawArtifact.from_bytes(
            payload=b"raw-provider-response",
            exchange="SHFE",
            concrete_instrument="SHFE.ni2509",
            coverage_start=datetime(2025, 6, 13, 21, 0, tzinfo=CN),
            coverage_end=datetime(2025, 6, 16, 15, 0, tzinfo=CN),
            granularity_seconds=60,
            timezone="Asia/Shanghai",
            raw_schema_identity="tqsdk-kline-dataframe-v1",
            source_identity_id=source.identity_id,
        )
        normalizer = NormalizerIdentity(
            adapter_version="tqsdk-3.10.1-fixed-bar-adapter-v1",
            normalized_schema_version="completed-historical-bar-v1",
            availability_rule_version="bar-start-plus-duration-v1",
        )
        first = DataVersionIdentity(
            source_identities=(source,),
            raw_artifacts=(artifact,),
            normalizer=normalizer,
            session_metadata_version="shfe-session-fixture-v1",
            historical_availability_rule="bar-start-plus-duration-v1",
            contract_metadata_identity="ni2509-contract-fixture-v1",
        )
        repeated = DataVersionIdentity(
            source_identities=(source,),
            raw_artifacts=(artifact,),
            normalizer=normalizer,
            session_metadata_version="shfe-session-fixture-v1",
            historical_availability_rule="bar-start-plus-duration-v1",
            contract_metadata_identity="ni2509-contract-fixture-v1",
        )
        changed_session = DataVersionIdentity(
            source_identities=(source,),
            raw_artifacts=(artifact,),
            normalizer=normalizer,
            session_metadata_version="shfe-session-fixture-v2",
            historical_availability_rule="bar-start-plus-duration-v1",
            contract_metadata_identity="ni2509-contract-fixture-v1",
        )

        self.assertEqual(first.identity_id, repeated.identity_id)
        self.assertNotEqual(first.identity_id, changed_session.identity_id)

        changed_artifact = RawArtifact.from_bytes(
            payload=b"different-raw-provider-response",
            exchange=artifact.exchange,
            concrete_instrument=artifact.concrete_instrument,
            coverage_start=artifact.coverage_start,
            coverage_end=artifact.coverage_end,
            granularity_seconds=artifact.granularity_seconds,
            timezone=artifact.timezone,
            raw_schema_identity=artifact.raw_schema_identity,
            source_identity_id=source.identity_id,
        )
        changed_normalizer = NormalizerIdentity(
            "tqsdk-fixed-bar-adapter-v2",
            normalizer.normalized_schema_version,
            normalizer.availability_rule_version,
        )
        variants = (
            DataVersionIdentity((source,), (changed_artifact,), normalizer, first.session_metadata_version, first.historical_availability_rule, first.contract_metadata_identity),
            DataVersionIdentity((source,), (replace(artifact, coverage_end=datetime(2025, 6, 16, 14, 59, tzinfo=CN)),), normalizer, first.session_metadata_version, first.historical_availability_rule, first.contract_metadata_identity),
            DataVersionIdentity((source,), (replace(artifact, granularity_seconds=300),), normalizer, first.session_metadata_version, first.historical_availability_rule, first.contract_metadata_identity),
            DataVersionIdentity((source,), (artifact,), changed_normalizer, first.session_metadata_version, first.historical_availability_rule, first.contract_metadata_identity),
            DataVersionIdentity((source,), (artifact,), normalizer, first.session_metadata_version, first.historical_availability_rule, "ni2509-contract-fixture-v2"),
        )
        for variant in variants:
            self.assertNotEqual(first.identity_id, variant.identity_id)

        changed_source = replace(source, retrieved_at=datetime(2026, 8, 16, 2, 1, tzinfo=UTC))
        source_bound_artifact = replace(artifact, source_identity_id=changed_source.identity_id)
        source_variant = DataVersionIdentity(
            (changed_source,),
            (source_bound_artifact,),
            normalizer,
            first.session_metadata_version,
            first.historical_availability_rule,
            first.contract_metadata_identity,
        )
        self.assertNotEqual(first.identity_id, source_variant.identity_id)

    def test_source_identity_rejects_secret_bearing_request_parameters(self):
        with self.assertRaisesRegex(ValueError, "credentials"):
            SourceIdentity(
                "TQSDK",
                "PROFESSIONAL_HISTORICAL_API",
                "TqApi.get_kline_data_series",
                None,
                datetime(2026, 8, 16, 2, 0, tzinfo=UTC),
                (("password", "test-only-value"),),
            )


class HistoricalBarNormalizationTests(unittest.TestCase):
    def context(self, records, windows, coverage_start, coverage_end):
        payload = json.dumps(records, separators=(",", ":"), sort_keys=True).encode("utf-8")
        source = SourceIdentity(
            "TQSDK",
            "PROFESSIONAL_HISTORICAL_API",
            "TqApi.get_kline_data_series",
            None,
            datetime(2026, 8, 16, 2, 0, tzinfo=UTC),
            (("duration_seconds", "60"), ("symbol", "SHFE.ni2509")),
        )
        artifact = RawArtifact.from_bytes(
            payload=payload,
            exchange="SHFE",
            concrete_instrument="SHFE.ni2509",
            coverage_start=coverage_start,
            coverage_end=coverage_end,
            granularity_seconds=60,
            timezone="Asia/Shanghai",
            raw_schema_identity="tqsdk-kline-records-json-v1",
            source_identity_id=source.identity_id,
        )
        normalizer = NormalizerIdentity(
            "tqsdk-3.10.1-fixed-bar-adapter-v1",
            "completed-historical-bar-v1",
            "bar-start-plus-duration-v1",
        )
        data_version = DataVersionIdentity(
            (source,),
            (artifact,),
            normalizer,
            "shfe-ni-session-v1",
            "bar-start-plus-duration-v1",
            "ni2509-contract-v1",
        )
        sessions = SessionMetadata("shfe-ni-session-v1", windows)
        return payload, artifact, data_version, sessions

    @staticmethod
    def record(start, close=120010):
        return {
            "id": nanoseconds(start),
            "datetime": nanoseconds(start),
            "open": 120000,
            "high": 120020,
            "low": 119990,
            "close": close,
            "volume": 32,
            "open_oi": 1010,
            "close_oi": 1012,
        }

    def test_tqsdk_bar_uses_existing_completed_bar_and_keeps_distinct_timestamps(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 9, 1, tzinfo=CN)
        records = [
            {
                "id": 1,
                "datetime": nanoseconds(start),
                "open": 120000,
                "high": 120020,
                "low": 119990,
                "close": 120010,
                "volume": 32,
                "open_oi": 1010,
                "close_oi": 1012,
            }
        ]
        payload = json.dumps(records, separators=(",", ":"), sort_keys=True).encode("utf-8")
        retrieved_at = datetime(2026, 8, 16, 2, 0, tzinfo=UTC)
        source = SourceIdentity(
            "TQSDK",
            "PROFESSIONAL_HISTORICAL_API",
            "TqApi.get_kline_data_series",
            None,
            retrieved_at,
            (("duration_seconds", "60"), ("symbol", "SHFE.ni2509")),
        )
        artifact = RawArtifact.from_bytes(
            payload=payload,
            exchange="SHFE",
            concrete_instrument="SHFE.ni2509",
            coverage_start=start,
            coverage_end=end,
            granularity_seconds=60,
            timezone="Asia/Shanghai",
            raw_schema_identity="tqsdk-kline-records-json-v1",
            source_identity_id=source.identity_id,
        )
        normalizer = NormalizerIdentity(
            "tqsdk-3.10.1-fixed-bar-adapter-v1",
            "completed-historical-bar-v1",
            "bar-start-plus-duration-v1",
        )
        data_version = DataVersionIdentity(
            (source,),
            (artifact,),
            normalizer,
            "shfe-ni-session-v1",
            "bar-start-plus-duration-v1",
            "ni2509-contract-v1",
        )
        sessions = SessionMetadata(
            "shfe-ni-session-v1",
            [SessionWindow("SHFE", "SHFE.ni2509", date(2025, 6, 16), start, end, "day")],
        )

        batch = normalize_tqsdk_historical_bars(
            payload,
            artifact=artifact,
            data_version=data_version,
            sessions=sessions,
            minimum_price_tick=Decimal("10"),
        )

        bar = batch.bars[0]
        self.assertEqual(bar.source_event_at, start)
        self.assertEqual(bar.completed_bar.start, start)
        self.assertEqual(bar.completed_bar.end, end)
        self.assertEqual(bar.completed_bar.available_at, end)
        self.assertEqual(bar.source_retrieved_at, retrieved_at)
        self.assertFalse(bar.completed_bar.is_visible_at(datetime(2025, 6, 16, 9, 0, 59, tzinfo=CN)))
        self.assertTrue(bar.completed_bar.is_visible_at(end))
        self.assertEqual((bar.open, bar.high, bar.low, bar.close), tuple(map(Decimal, ("120000", "120020", "119990", "120010"))))
        self.assertEqual((bar.volume, bar.open_interest_start, bar.open_interest_end), tuple(map(Decimal, ("32", "1010", "1012"))))
        self.assertEqual(bar.data_version_id, data_version.identity_id)

    def test_expected_recess_is_not_a_gap_but_missing_session_bar_is_reported(self):
        trading_day = date(2025, 6, 16)
        morning_start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        morning_end = datetime(2025, 6, 16, 9, 2, tzinfo=CN)
        late_start = datetime(2025, 6, 16, 10, 30, tzinfo=CN)
        late_end = datetime(2025, 6, 16, 10, 32, tzinfo=CN)
        missing_start = datetime(2025, 6, 16, 10, 31, tzinfo=CN)
        windows = [
            SessionWindow("SHFE", "SHFE.ni2509", trading_day, morning_start, morning_end, "day"),
            SessionWindow("SHFE", "SHFE.ni2509", trading_day, late_start, late_end, "day"),
        ]
        records = [
            self.record(morning_start),
            self.record(datetime(2025, 6, 16, 9, 1, tzinfo=CN)),
            self.record(late_start),
        ]
        payload, artifact, data_version, sessions = self.context(
            records,
            windows,
            morning_start,
            late_end,
        )

        batch = normalize_tqsdk_historical_bars(
            payload,
            artifact=artifact,
            data_version=data_version,
            sessions=sessions,
            minimum_price_tick=Decimal("10"),
        )

        self.assertEqual(batch.missing_expected_starts, (missing_start,))
        self.assertEqual(len(batch.bars), len(records))
        repeated = normalize_tqsdk_historical_bars(
            payload,
            artifact=artifact,
            data_version=data_version,
            sessions=sessions,
            minimum_price_tick=Decimal("10"),
        )
        self.assertEqual(batch.identity_id, repeated.identity_id)

    def test_duplicate_and_out_of_order_source_bars_fail_closed(self):
        trading_day = date(2025, 6, 16)
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        second = datetime(2025, 6, 16, 9, 1, tzinfo=CN)
        end = datetime(2025, 6, 16, 9, 2, tzinfo=CN)
        windows = [SessionWindow("SHFE", "SHFE.ni2509", trading_day, start, end, "day")]
        cases = (
            ("duplicate", [self.record(start), self.record(start)]),
            ("out-of-order", [self.record(second), self.record(start)]),
        )
        for message, records in cases:
            with self.subTest(message=message):
                payload, artifact, data_version, sessions = self.context(records, windows, start, end)
                with self.assertRaisesRegex(ValueError, message):
                    normalize_tqsdk_historical_bars(
                        payload,
                        artifact=artifact,
                        data_version=data_version,
                        sessions=sessions,
                    )

    def test_invalid_market_facts_contract_and_coverage_fail_closed(self):
        trading_day = date(2025, 6, 16)
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        second = datetime(2025, 6, 16, 9, 1, tzinfo=CN)
        end = datetime(2025, 6, 16, 9, 2, tzinfo=CN)
        full_window = [SessionWindow("SHFE", "SHFE.ni2509", trading_day, start, end, "day")]

        invalid_ohlc = self.record(start)
        invalid_ohlc["high"] = 120000
        negative_volume = self.record(start)
        negative_volume["volume"] = -1
        wrong_contract = self.record(start)
        wrong_contract["symbol"] = "SHFE.cu2509"
        off_tick = self.record(start, close=120011)
        cases = (
            ("OHLC", invalid_ohlc, full_window, start, end, None),
            ("non-negative", negative_volume, full_window, start, end, None),
            ("contract identity", wrong_contract, full_window, start, end, None),
            ("minimum tick", off_tick, full_window, start, end, Decimal("10")),
            ("claimed coverage", self.record(second), full_window, start, second, None),
            (
                "published sessions",
                self.record(second),
                [SessionWindow("SHFE", "SHFE.ni2509", trading_day, start, second, "day")],
                start,
                end,
                None,
            ),
        )
        for message, record, windows, coverage_start, coverage_end, tick in cases:
            with self.subTest(message=message):
                payload, artifact, data_version, sessions = self.context(
                    [record],
                    windows,
                    coverage_start,
                    coverage_end,
                )
                with self.assertRaisesRegex(ValueError, message):
                    normalize_tqsdk_historical_bars(
                        payload,
                        artifact=artifact,
                        data_version=data_version,
                        sessions=sessions,
                        minimum_price_tick=tick,
                    )

    def test_raw_payload_must_match_the_bound_artifact_hash(self):
        trading_day = date(2025, 6, 16)
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 9, 1, tzinfo=CN)
        windows = [SessionWindow("SHFE", "SHFE.ni2509", trading_day, start, end, "day")]
        payload, artifact, data_version, sessions = self.context([self.record(start)], windows, start, end)

        with self.assertRaisesRegex(ValueError, "artifact hash"):
            normalize_tqsdk_historical_bars(
                payload + b" ",
                artifact=artifact,
                data_version=data_version,
                sessions=sessions,
            )


if __name__ == "__main__":
    unittest.main()

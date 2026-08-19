"""Focused regression tests for Package D canonical completeness/provenance.

Reproduces then closes D-01..D-08 from:
- docs/reviews/FULL_PROJECT_SECOND_PASS_ADVERSARIAL_AUDIT_2026-08-20.md (Part C)
- docs/reviews/PARALLEL_PACKAGE_C_D_F_ACTUAL_REPAIR_SPEC_V0_1.md (Package D)

Rules:
- synthetic in-memory / temp-dir fixtures only;
- no canonical corpus rebuild;
- no real candidate market data read;
- Parquet-dependent assertions are capability-gated on pyarrow (skip in a
  stdlib-only environment), matching the repository's existing skip mechanism.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from src.canonical_storage import (
    CanonicalRow,
    read_partition_table,
    write_partition_table,
)
from src.data_substrate import SessionMetadata, SessionWindow
from src.historical_acquisition import (
    AcquisitionError,
    AcquisitionRequest,
    AcquisitionResult,
    ContractConfig,
    ContractMetadataFact,
    DatasetBuilder,
    SourceAdapter,
    SourceSpecification,
    TqSdkSourceAdapter,
)
from src.historical_data import (
    DataVersionIdentity,
    NormalizerIdentity,
    NormalizedHistoricalBar,
    RawArtifact,
    SourceIdentity,
    normalize_tqsdk_historical_bars,
)
from src.historical_manifest import ManifestPartition, canonical_hash
from src.metadata_authority import (
    GovernedSource,
    ProductSessionSchedule,
    TradingCalendar,
    build_session_metadata,
)

try:
    import pyarrow  # noqa: F401, PLC0415

    HAVE_PYARROW = True
except Exception:  # noqa: BLE001 - stdlib-only environment
    HAVE_PYARROW = False

CN = ZoneInfo("Asia/Shanghai")
UTC = ZoneInfo("UTC")
_ONE_MINUTE = timedelta(minutes=1)


def _nanoseconds(timestamp: datetime) -> int:
    return int(timestamp.timestamp() * 1_000_000_000)


def _record(start: datetime, *, volume: int | None = 32, symbol: str = "SHFE.ni2509") -> dict:
    record = {
        "id": _nanoseconds(start),
        "datetime": _nanoseconds(start),
        "open": 120000,
        "high": 120020,
        "low": 119990,
        "close": 120010,
        "volume": volume,
        "open_oi": 1010,
        "close_oi": 1012,
        "symbol": symbol,
    }
    if volume is None:
        record.pop("volume")
    return record


def _normalizer() -> NormalizerIdentity:
    return NormalizerIdentity(
        "tqsdk-3.10.1-fixed-bar-adapter-v1",
        "completed-historical-bar-v1",
        "bar-start-plus-duration-v1",
    )


def _source(retrieved_at: datetime | None = None) -> SourceIdentity:
    return SourceIdentity(
        "TQSDK",
        "PROFESSIONAL_HISTORICAL_API",
        "TqApi.get_kline_data_series",
        None,
        retrieved_at or datetime(2026, 8, 20, 2, 0, tzinfo=UTC),
        (
            ("duration_seconds", "60"),
            ("end_dt", "2026-08-20"),
            ("start_dt", "2026-08-20"),
            ("symbol", "SHFE.ni2509"),
        ),
    )


def _payload(records: list[dict]) -> bytes:
    return json.dumps(records, separators=(",", ":")).encode("utf-8")


def _artifact(
    records: list[dict],
    coverage_start: datetime,
    coverage_end: datetime,
) -> RawArtifact:
    return RawArtifact.from_bytes(
        payload=_payload(records),
        exchange="SHFE",
        concrete_instrument="SHFE.ni2509",
        coverage_start=coverage_start,
        coverage_end=coverage_end,
        granularity_seconds=60,
        timezone="Asia/Shanghai",
        raw_schema_identity="tqsdk-kline-records-json-v1",
        source_identity_id=_source().identity_id,
    )


def _canonical_row(
    *,
    trading_day: date,
    bar_start: datetime,
    bar_end: datetime,
    volume: int | None,
    raw_artifact_identity_id: str,
    contract: str = "SHFE.ni2509",
    product: str = "ni",
) -> CanonicalRow:
    return CanonicalRow(
        provider="TQSDK",
        source_type="PROFESSIONAL_HISTORICAL_API",
        exchange="SHFE",
        concrete_contract=contract,
        product=product,
        trading_day=trading_day,
        bar_start=bar_start,
        bar_end=bar_end,
        historical_available_at=bar_end,
        open=Decimal("120000"),
        high=Decimal("120020"),
        low=Decimal("119990"),
        close=Decimal("120010"),
        volume=volume,
        open_interest_start=1010,
        open_interest_end=1012,
        raw_artifact_identity_id=raw_artifact_identity_id,
        source_identity_id="src-fixture-v1",
        data_version_id="dv-fixture-v1",
        contract_metadata_identity="cm-fixture-v1",
        session_metadata_identity="sm-fixture-v1",
        normalizer_identity="norm-fixture-v1",
    )


class D01TruncatedCoverageCannotBePASSTests(unittest.TestCase):
    def _partition(self, *, returned_start: datetime, returned_end: datetime,
                   quality_status: str, **overrides) -> ManifestPartition:
        requested_start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        requested_end = datetime(2026, 8, 20, 10, 0, tzinfo=CN)
        request_parameters = (
            ("duration_seconds", "60"),
            ("end_dt", requested_end.isoformat()),
            ("start_dt", requested_start.isoformat()),
            ("symbol", "SHFE.ni2509"),
        )
        payload = _payload([_record(requested_start)])
        return ManifestPartition(
            provider="TQSDK",
            api_version="3.10.1",
            contract="SHFE.ni2509",
            exchange="SHFE",
            granularity_seconds=60,
            timezone="Asia/Shanghai",
            trading_day=date(2026, 8, 20),
            requested_start=requested_start,
            requested_end=requested_end,
            returned_start=returned_start,
            returned_end=returned_end,
            retrieved_at=datetime(2026, 8, 20, 2, 0, tzinfo=UTC),
            raw_bytes=len(payload),
            raw_sha256=hashlib.sha256(payload).hexdigest(),
            request_identity=canonical_hash(request_parameters),
            request_parameters=request_parameters,
            normalizer_identity=_normalizer().identity_id,
            session_metadata_version="shfe-ni-session-v1",
            contract_metadata_identity="cm-fixture-v1",
            data_version_id="dv-fixture-v1",
            normalized_batch_id="nb-fixture-v1",
            quality_status=quality_status,
            **overrides,
        )

    def test_truncated_PASS_partition_fails_at_construction(self) -> None:
        requested_start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        requested_end = datetime(2026, 8, 20, 10, 0, tzinfo=CN)
        # Provider returns only 09:03..10:00 (head missing) yet quality says PASS.
        with self.assertRaisesRegex(ValueError, "full requested coverage"):
            self._partition(
                returned_start=datetime(2026, 8, 20, 9, 3, tzinfo=CN),
                returned_end=requested_end,
                quality_status="PASS",
            )
        # Truncated tail as well.
        with self.assertRaisesRegex(ValueError, "full requested coverage"):
            self._partition(
                returned_start=requested_start,
                returned_end=datetime(2026, 8, 20, 9, 30, tzinfo=CN),
                quality_status="PASS",
            )

    def test_truncated_non_PASS_partition_is_still_recordable(self) -> None:
        requested_start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        requested_end = datetime(2026, 8, 20, 10, 0, tzinfo=CN)
        partition = self._partition(
            returned_start=datetime(2026, 8, 20, 9, 3, tzinfo=CN),
            returned_end=requested_end,
            quality_status="ANOMALY:returned_coverage_truncated",
        )
        self.assertNotEqual(partition.quality_status, "PASS")
        # And the recorded returned coverage is NOT stretched to the requested.
        self.assertNotEqual(partition.returned_start, partition.requested_start)

    def test_full_coverage_PASS_still_accepted(self) -> None:
        requested_start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        requested_end = datetime(2026, 8, 20, 10, 0, tzinfo=CN)
        partition = self._partition(
            returned_start=requested_start,
            returned_end=requested_end,
            quality_status="PASS",
        )
        self.assertEqual(partition.quality_status, "PASS")

    def test_builder_never_writes_truncated_PASS(self) -> None:
        """DatasetBuilder must produce a non-PASS quality for truncated coverage."""

        class TruncatingAdapter(SourceAdapter):
            @property
            def source_specification(self) -> SourceSpecification:
                return SourceSpecification(
                    provider="FAKE",
                    source_type="FAKE_HISTORICAL_API",
                    endpoint_identity="FakeSource.get_kline_series",
                    raw_schema_identity="fake-kline-records-json-v1",
                    provider_dataset_version=None,
                    normalizer=_normalizer(),
                )

            def acquire(self, request: AcquisitionRequest) -> AcquisitionResult:
                # Return only 09:30..10:00 even though 09:00..10:00 was requested.
                returned_start = datetime(2026, 8, 20, 9, 30, tzinfo=CN)
                returned_end = datetime(2026, 8, 20, 10, 0, tzinfo=CN)
                starts = []
                cursor = returned_start
                while cursor + _ONE_MINUTE <= returned_end:
                    starts.append(cursor)
                    cursor += _ONE_MINUTE
                records = [_record(s) for s in starts]
                return AcquisitionResult(
                    request=request,
                    payload=_payload(records),
                    returned_start=returned_start,
                    returned_end=returned_end,
                    rows=len(records),
                    provider_version="fake-1.0",
                )

            def decode(self, payload, *, artifact, data_version, sessions, minimum_price_tick):
                return normalize_tqsdk_historical_bars(
                    payload,
                    artifact=artifact,
                    data_version=data_version,
                    sessions=sessions,
                    minimum_price_tick=minimum_price_tick,
                )

            def close(self) -> None:
                pass

        requested_start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        requested_end = datetime(2026, 8, 20, 10, 0, tzinfo=CN)
        request = AcquisitionRequest(
            exchange="SHFE",
            concrete_instrument="SHFE.ni2509",
            trading_day=date(2026, 8, 20),
            granularity_seconds=60,
            requested_start=requested_start,
            requested_end=requested_end,
            timezone="Asia/Shanghai",
        )
        sessions = SessionMetadata(
            "shfe-ni-session-v1",
            [
                SessionWindow(
                    "SHFE", "SHFE.ni2509", date(2026, 8, 20),
                    requested_start, requested_end, "day",
                )
            ],
        )
        fact = ContractMetadataFact(
            exchange="SHFE",
            concrete_instrument="SHFE.ni2509",
            minimum_price_tick=Decimal("10"),
            session_metadata_version=sessions.version,
            effective_start=date(2026, 8, 20),
            effective_end=date(2026, 8, 20),
            evidence_reference="tests/test_fixture",
            evidence_classification="PILOT_FIXTURE",
        )
        contracts = {
            "SHFE.ni2509": ContractConfig(
                concrete_instrument="SHFE.ni2509",
                minimum_price_tick=Decimal("10"),
                metadata_fact=fact,
                sessions=sessions,
            )
        }
        with tempfile.TemporaryDirectory() as tmp:
            raw_dir = Path(tmp) / "raw"
            manifest_path = Path(tmp) / "manifest.json"
            builder = DatasetBuilder(
                adapter=TruncatingAdapter(),
                raw_dir=raw_dir,
                manifest_path=manifest_path,
                schema_version="package-d-fixture-manifest-v1",
                contracts=contracts,
                retrieved_at_provider=lambda: datetime(2026, 8, 20, 2, 0, tzinfo=UTC),
            )
            manifest = builder.build([request])
        partition = manifest.partitions[0]
        self.assertNotEqual(partition.quality_status, "PASS")
        self.assertIn("returned_coverage_truncated", partition.quality_status)


class D02SessionAuthorityCompletenessTests(unittest.TestCase):
    def test_entire_absent_session_window_enters_missing_evidence(self) -> None:
        """Two session windows; the second has zero bars; artifact coverage
        claims both; missing evidence must include the second window."""
        trading_day = date(2026, 8, 20)
        window_a_start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        window_a_end = datetime(2026, 8, 20, 9, 5, tzinfo=CN)
        window_b_start = datetime(2026, 8, 20, 10, 0, tzinfo=CN)
        window_b_end = datetime(2026, 8, 20, 10, 5, tzinfo=CN)
        windows = [
            SessionWindow("SHFE", "SHFE.ni2509", trading_day, window_a_start, window_a_end, "day"),
            SessionWindow("SHFE", "SHFE.ni2509", trading_day, window_b_start, window_b_end, "day"),
        ]
        sessions = SessionMetadata("shfe-ni-session-v1", windows)
        # Raw payload contains ONLY window A's complete bars.
        records = [
            _record(window_a_start + timedelta(minutes=offset)) for offset in range(5)
        ]
        # Artifact coverage claims BOTH windows (09:00..10:05).
        artifact = _artifact(records, window_a_start, window_b_end)
        data_version = DataVersionIdentity(
            (_source(),),
            (artifact,),
            _normalizer(),
            sessions.version,
            "bar-start-plus-duration-v1",
            "ni2509-contract-fixture-v1",
        )
        batch = normalize_tqsdk_historical_bars(
            _payload(records),
            artifact=artifact,
            data_version=data_version,
            sessions=sessions,
            minimum_price_tick=Decimal("10"),
        )
        window_b_expected = sessions.expected_bar_starts_between(
            "SHFE", "SHFE.ni2509", window_b_start, window_b_end, _ONE_MINUTE
        )
        self.assertTrue(window_b_expected)
        for start in window_b_expected:
            self.assertIn(
                start,
                batch.missing_expected_starts,
                f"zero-bar window B start {start.isoformat()} must be missing evidence",
            )

    def test_same_day_windows_still_report_in_window_gaps(self) -> None:
        trading_day = date(2026, 8, 20)
        window_start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        window_end = datetime(2026, 8, 20, 9, 5, tzinfo=CN)
        windows = [
            SessionWindow("SHFE", "SHFE.ni2509", trading_day, window_start, window_end, "day"),
        ]
        sessions = SessionMetadata("shfe-ni-session-v1", windows)
        # Drop one interior bar (09:02) from an otherwise complete window.
        records = [
            _record(window_start + timedelta(minutes=offset))
            for offset in range(5)
            if offset != 2
        ]
        artifact = _artifact(records, window_start, window_end)
        data_version = DataVersionIdentity(
            (_source(),),
            (artifact,),
            _normalizer(),
            sessions.version,
            "bar-start-plus-duration-v1",
            "ni2509-contract-fixture-v1",
        )
        batch = normalize_tqsdk_historical_bars(
            _payload(records),
            artifact=artifact,
            data_version=data_version,
            sessions=sessions,
            minimum_price_tick=Decimal("10"),
        )
        missing_bar = window_start + timedelta(minutes=2)
        self.assertIn(missing_bar, batch.missing_expected_starts)


class D03RawArtifactIdentityTests(unittest.TestCase):
    def test_raw_artifact_identity_is_not_the_raw_sha(self) -> None:
        trading_day = date(2026, 8, 20)
        start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        end = datetime(2026, 8, 20, 9, 1, tzinfo=CN)
        records = [_record(start)]
        artifact = _artifact(records, start, end)
        self.assertNotEqual(artifact.identity_id, artifact.raw_sha256)
        # NormalizedHistoricalBar.raw_artifact_identity_id is the RawArtifact
        # identity, not the raw SHA.
        completed = _completed_bar(start, end)
        bar = NormalizedHistoricalBar(
            "SHFE",
            "SHFE.ni2509",
            start,
            datetime(2026, 8, 20, 2, 0, tzinfo=UTC),
            completed,
            Decimal("120000"), Decimal("120020"), Decimal("119990"), Decimal("120010"),
            Decimal("32"), Decimal("1010"), Decimal("1012"),
            artifact.identity_id,
            "dv-fixture-v1",
        )
        self.assertEqual(bar.raw_artifact_identity_id, artifact.identity_id)
        # Canonical row must store the raw artifact identity, never raw SHA.
        row = _canonical_row(
            trading_day=trading_day,
            bar_start=start,
            bar_end=end,
            volume=32,
            raw_artifact_identity_id=bar.raw_artifact_identity_id,
        )
        self.assertEqual(row.raw_artifact_identity_id, artifact.identity_id)
        self.assertNotEqual(row.raw_artifact_identity_id, artifact.raw_sha256)

    @unittest.skipUnless(HAVE_PYARROW, "pyarrow not available in this environment")
    def test_builder_stores_raw_artifact_identity_not_raw_sha(self) -> None:
        from tools.build_canonical_dataset import (  # noqa: PLC0415
            SOURCE_SPEC,
            normalize_and_store_partition,
        )

        trading_day = date(2026, 8, 20)
        requested_start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        requested_end = datetime(2026, 8, 20, 9, 5, tzinfo=CN)
        records = [
            _record(requested_start + timedelta(minutes=offset)) for offset in range(5)
        ]
        payload = _payload(records)
        retrieved_at = datetime(2026, 8, 20, 2, 0, tzinfo=UTC)
        request_parameters = (
            ("duration_seconds", "60"),
            ("end_dt", requested_end.isoformat()),
            ("start_dt", requested_start.isoformat()),
            ("symbol", "SHFE.ni2509"),
        )
        sessions = SessionMetadata(
            "shfe-ni-session-v1",
            [
                SessionWindow(
                    "SHFE", "SHFE.ni2509", trading_day, requested_start, requested_end, "day",
                )
            ],
        )
        # Reconstruct source/artifact/data-version exactly as the builder does
        # so the recorded data_version_id / session_metadata_version are
        # consistent and the raw file hash matches the partition.
        source = SourceIdentity(
            "TQSDK", SOURCE_SPEC.source_type, SOURCE_SPEC.endpoint_identity,
            SOURCE_SPEC.provider_dataset_version, retrieved_at, request_parameters,
        )
        raw_sha = hashlib.sha256(payload).hexdigest()
        artifact = RawArtifact(
            "SHFE", "SHFE.ni2509", requested_start, requested_end, 60, "Asia/Shanghai",
            SOURCE_SPEC.raw_schema_identity, raw_sha, source.identity_id,
        )
        data_version = DataVersionIdentity(
            (source,), (artifact,), SOURCE_SPEC.normalizer, sessions.version,
            SOURCE_SPEC.availability_rule, "cm-fixture-v1",
        )
        partition = ManifestPartition(
            provider="TQSDK",
            api_version="3.10.1",
            contract="SHFE.ni2509",
            exchange="SHFE",
            granularity_seconds=60,
            timezone="Asia/Shanghai",
            trading_day=trading_day,
            requested_start=requested_start,
            requested_end=requested_end,
            returned_start=requested_start,
            returned_end=requested_end,
            retrieved_at=retrieved_at,
            raw_bytes=len(payload),
            raw_sha256=raw_sha,
            request_identity=canonical_hash(request_parameters),
            request_parameters=request_parameters,
            normalizer_identity=SOURCE_SPEC.normalizer.identity_id,
            session_metadata_version=sessions.version,
            contract_metadata_identity="cm-fixture-v1",
            data_version_id=data_version.identity_id,
            normalized_batch_id="nb-fixture-v1",
            quality_status="PASS",
        )
        coverage_tag = canonical_hash(
            ("Asia/Shanghai", requested_start.isoformat(), requested_end.isoformat())
        )[:12]
        raw_name = f"TQSDK.SHFE.ni2509.60s.{trading_day.isoformat()}.{coverage_tag}.json"
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            raw_dir = tmp_path / "raw"
            raw_dir.mkdir(parents=True)
            (raw_dir / raw_name).write_bytes(payload)
            parquet_dir = tmp_path / "parquet"
            normalize_and_store_partition(
                partition,
                raw_dir,
                parquet_dir,
                sessions,
                "cm-fixture-v1",
                Decimal("10"),
            )
            table = read_partition_table(parquet_dir)
            stored = table.column("raw_artifact_identity_id").to_pylist()
            self.assertTrue(stored)
            for value in stored:
                self.assertEqual(value, artifact.identity_id)
                self.assertNotEqual(value, artifact.raw_sha256)


def _completed_bar(start: datetime, end: datetime):
    from src.data_substrate import BarQuality, CompletedBar  # noqa: PLC0415

    return CompletedBar("SHFE.ni2509", start.date(), start, end, end, BarQuality())


class D04NullableVolumeTests(unittest.TestCase):
    def test_none_volume_is_valid_and_never_collapsed_to_zero(self) -> None:
        trading_day = date(2026, 8, 20)
        start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        end = datetime(2026, 8, 20, 9, 1, tzinfo=CN)
        row = _canonical_row(
            trading_day=trading_day,
            bar_start=start,
            bar_end=end,
            volume=None,
            raw_artifact_identity_id="artifact-fixture-v1",
        )
        self.assertIsNone(row.volume)
        self.assertIsNone(row.to_pylist_row()["volume"])
        self.assertIsNone(row.to_stable_dict()["volume"])

    def test_zero_and_positive_volumes_remain_valid(self) -> None:
        trading_day = date(2026, 8, 20)
        start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        end = datetime(2026, 8, 20, 9, 1, tzinfo=CN)
        for volume in (0, 1, 100):
            with self.subTest(volume=volume):
                row = _canonical_row(
                    trading_day=trading_day,
                    bar_start=start,
                    bar_end=end,
                    volume=volume,
                    raw_artifact_identity_id="artifact-fixture-v1",
                )
                self.assertEqual(row.volume, volume)

    def test_negative_volume_fails(self) -> None:
        trading_day = date(2026, 8, 20)
        start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        end = datetime(2026, 8, 20, 9, 1, tzinfo=CN)
        with self.assertRaisesRegex(ValueError, "volume"):
            _canonical_row(
                trading_day=trading_day,
                bar_start=start,
                bar_end=end,
                volume=-1,
                raw_artifact_identity_id="artifact-fixture-v1",
            )

    @unittest.skipUnless(HAVE_PYARROW, "pyarrow not available in this environment")
    def test_none_volume_write_read_stays_none(self) -> None:
        trading_day = date(2026, 8, 20)
        start = datetime(2026, 8, 20, 9, 0, tzinfo=CN)
        end = datetime(2026, 8, 20, 9, 1, tzinfo=CN)
        row = _canonical_row(
            trading_day=trading_day,
            bar_start=start,
            bar_end=end,
            volume=None,
            raw_artifact_identity_id="artifact-fixture-v1",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "parquet"
            write_partition_table(root, [row])
            table = read_partition_table(root)
            stored = table.column("volume").to_pylist()
            self.assertEqual(stored, [None])


class D05SessionMetadataContentIdentityTests(unittest.TestCase):
    def test_same_authority_label_different_windows_differ(self) -> None:
        day = date(2026, 8, 20)
        window_a = SessionWindow(
            "SHFE", "SHFE.ni2509", day,
            datetime(2026, 8, 20, 9, 0, tzinfo=CN),
            datetime(2026, 8, 20, 10, 0, tzinfo=CN),
            "day",
        )
        window_b = SessionWindow(
            "SHFE", "SHFE.ni2509", day,
            datetime(2026, 8, 20, 9, 0, tzinfo=CN),
            datetime(2026, 8, 20, 11, 0, tzinfo=CN),
            "day",
        )
        sm_a = SessionMetadata("same-version", [window_a])
        sm_b = SessionMetadata("same-version", [window_b])
        self.assertNotEqual(sm_a.version, sm_b.version)
        self.assertEqual(sm_a.identity, sm_a.version)
        self.assertEqual(sm_b.identity, sm_b.version)

    def test_version_is_deterministic(self) -> None:
        day = date(2026, 8, 20)
        windows = [
            SessionWindow(
                "SHFE", "SHFE.ni2509", day,
                datetime(2026, 8, 20, 9, 0, tzinfo=CN),
                datetime(2026, 8, 20, 10, 0, tzinfo=CN),
                "day",
            )
        ]
        self.assertEqual(
            SessionMetadata("ref", windows).version,
            SessionMetadata("ref", windows).version,
        )

    def test_builder_version_binds_calendar_and_night_closed_authority(self) -> None:
        source = GovernedSource(
            resource_identity="SHFE official trading-hours page",
            url="https://www.shfe.com.cn/services/calenderandholidays/tradinghours/",
            retrieved_at=datetime(2026, 8, 16, 16, 0, tzinfo=CN),
            artifact_sha256="a" * 64,
            schema_version="shfe-trading-hours-v1",
            classification="OFFICIAL_AVAILABLE",
            effective_period_start=date(2024, 1, 1),
            effective_period_end=date(2025, 12, 31),
        )
        schedule = ProductSessionSchedule(
            "SHFE", "cu", date(2024, 1, 1), date(2025, 12, 31),
            ((time(9, 0), time(10, 15)), (time(10, 30), time(11, 30)), (time(13, 30), time(15, 0))),
            (time(21, 0), time(1, 0)),
            timezone="Asia/Shanghai",
            source=source,
        )
        cal_source = GovernedSource(
            resource_identity="SHFE official annual raw",
            url="https://www.shfe.com.cn/eng/reports/StatisticalData/Annualdata/HistoricalData/downloadhistory/",
            retrieved_at=datetime(2026, 8, 16, 16, 0, tzinfo=CN),
            artifact_sha256="b" * 64,
            schema_version="shfe-official-annual-daily-v2",
            classification="OFFICIAL_AVAILABLE",
            effective_period_start=date(2024, 1, 1),
            effective_period_end=date(2025, 12, 31),
        )
        day1 = date(2024, 1, 2)
        day2 = date(2024, 1, 3)
        cal_normal = TradingCalendar("v1", [day1, day2], cal_source, night_closed_trading_days=())
        cal_closed = TradingCalendar("v1", [day1, day2], cal_source, night_closed_trading_days={day2})
        days = [day1, day2]
        normal = build_session_metadata(cal_normal, schedule, "SHFE.cu2401", days)
        closed = build_session_metadata(cal_closed, schedule, "SHFE.cu2401", days)
        self.assertNotEqual(normal.version, closed.version)
        # Explicit night-closed override on the same calendar also changes it.
        overridden = build_session_metadata(
            cal_normal, schedule, "SHFE.cu2401", days,
            night_closed_days=frozenset({day2}),
        )
        self.assertNotEqual(normal.version, overridden.version)
        self.assertNotEqual(normal.version, schedule.identity())


class D06GovernedSourceByteProvenanceTests(unittest.TestCase):
    def _source(self, classification: str = "OFFICIAL_AVAILABLE",
                artifact_sha256: str | None = "a" * 64,
                artifact_sha256s: tuple[str, ...] = ()) -> GovernedSource:
        return GovernedSource(
            resource_identity="res",
            url="https://example.com/official",
            retrieved_at=datetime(2026, 8, 16, tzinfo=CN),
            artifact_sha256=artifact_sha256,
            artifact_sha256s=artifact_sha256s,
            schema_version="v1",
            classification=classification,
            effective_period_start=date(2024, 1, 1),
            effective_period_end=date(2025, 12, 31),
        )

    def test_changing_one_bound_hash_changes_identity(self) -> None:
        self.assertNotEqual(self._source().identity(), self._source(artifact_sha256="b" * 64).identity())

    def test_multi_hash_is_canonical_sorted_unique_and_bound(self) -> None:
        source = self._source(
            artifact_sha256=None,
            artifact_sha256s=("b" * 64, "a" * 64, "b" * 64),
            classification="OFFICIAL_PARTIAL",
        )
        self.assertEqual(source.exact_sha256s, ("a" * 64, "b" * 64))
        self.assertTrue(source.byte_bound)
        # Reordered hash set -> same identity (canonical sorted unique).
        self.assertEqual(
            source.identity(),
            self._source(
                artifact_sha256=None,
                artifact_sha256s=("a" * 64, "b" * 64),
                classification="OFFICIAL_PARTIAL",
            ).identity(),
        )

    def test_available_without_byte_hash_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "exact artifact SHA256"):
            self._source(artifact_sha256=None, classification="OFFICIAL_AVAILABLE")
        with self.assertRaisesRegex(ValueError, "exact artifact SHA256"):
            self._source(artifact_sha256=None, classification="ARCHIVED_OFFICIAL")

    def test_no_hash_is_explicitly_partial_not_exact_bound(self) -> None:
        partial = self._source(artifact_sha256=None, classification="OFFICIAL_PARTIAL")
        self.assertFalse(partial.byte_bound)
        self.assertEqual(partial.exact_sha256s, ())
        pending = self._source(artifact_sha256=None, classification="PENDING_OFFICIAL_BINDING")
        self.assertFalse(pending.byte_bound)


class D07MixedPartitionWriteTests(unittest.TestCase):
    @unittest.skipUnless(HAVE_PYARROW, "pyarrow not available in this environment")
    def test_mixed_partition_is_rejected_before_any_file_is_written(self) -> None:
        trading_day_a = date(2026, 8, 20)
        trading_day_b = date(2026, 9, 18)
        row_a = _canonical_row(
            trading_day=trading_day_a,
            bar_start=datetime(2026, 8, 20, 9, 0, tzinfo=CN),
            bar_end=datetime(2026, 8, 20, 9, 1, tzinfo=CN),
            volume=32,
            raw_artifact_identity_id="artifact-a",
        )
        row_b = _canonical_row(
            trading_day=trading_day_b,
            bar_start=datetime(2026, 9, 18, 9, 0, tzinfo=CN),
            bar_end=datetime(2026, 9, 18, 9, 1, tzinfo=CN),
            volume=40,
            raw_artifact_identity_id="artifact-b",
            contract="SHFE.al2609",
            product="al",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "parquet"
            with self.assertRaisesRegex(ValueError, "multiple canonical partitions"):
                write_partition_table(root, [row_a, row_b])
            parquet_files = sorted(root.rglob("*.parquet"))
            self.assertEqual(parquet_files, [], "no parquet may be written for a mixed partition")

    @unittest.skipUnless(HAVE_PYARROW, "pyarrow not available in this environment")
    def test_single_partition_write_is_unaffected(self) -> None:
        trading_day = date(2026, 8, 20)
        row_a = _canonical_row(
            trading_day=trading_day,
            bar_start=datetime(2026, 8, 20, 9, 0, tzinfo=CN),
            bar_end=datetime(2026, 8, 20, 9, 1, tzinfo=CN),
            volume=32,
            raw_artifact_identity_id="artifact-a",
        )
        row_b = _canonical_row(
            trading_day=trading_day,
            bar_start=datetime(2026, 8, 20, 9, 1, tzinfo=CN),
            bar_end=datetime(2026, 8, 20, 9, 2, tzinfo=CN),
            volume=33,
            raw_artifact_identity_id="artifact-a",
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "parquet"
            facts = write_partition_table(root, [row_a, row_b])
            self.assertEqual(facts["row_count"], 2)
            self.assertGreater(facts["file_count"], 0)


class D08RuntimeVersionDiagnosticTests(unittest.TestCase):
    def test_mismatch_error_reports_the_real_wrong_version(self) -> None:
        class _Probe(TqSdkSourceAdapter):
            def __init__(self):
                super().__init__(
                    credentials_provider=lambda: ("acct", "pw"),
                    verified_runtime_version="3.10.1",
                )

            def _build_auth(self, account, password):
                return object()

            def _open_api(self, auth):
                self._version = "9.9.9"
                self._api = object()
                return self._api

        probe = _Probe()
        with self.assertRaisesRegex(AcquisitionError, "9.9.9"):
            probe._connect()
        self.assertIsNone(probe._api)
        self.assertIsNone(probe._version)


if __name__ == "__main__":
    unittest.main()

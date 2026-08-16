import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
import json
from pathlib import Path
import tempfile
from zoneinfo import ZoneInfo

from src.data_substrate import SessionMetadata, SessionWindow
from src.historical_acquisition import (
    AcquisitionError,
    AcquisitionRequest,
    AcquisitionResult,
    ContractConfig,
    ContractMetadataFact,
    DatasetBuilder,
    InvalidConcreteSymbolError,
    RawPartitionConflictError,
    SourceAdapter,
    SourceSpecification,
    TqSdkSourceAdapter,
    is_transient_network_error,
    retry_decision,
    validate_concrete_symbol,
)
from src.historical_data import NormalizerIdentity, normalize_tqsdk_historical_bars

CN = ZoneInfo("Asia/Shanghai")
UTC = ZoneInfo("UTC")

FAKE_NORMALIZER = NormalizerIdentity(
    "fake-adapter-v1",
    "completed-historical-bar-v1",
    "bar-start-plus-duration-v1",
)


def ns(ts):
    return int(ts.timestamp() * 1_000_000_000)


def make_request(contract, exchange, day, start, end, granularity=60, timezone="Asia/Shanghai"):
    return AcquisitionRequest(
        exchange=exchange,
        concrete_instrument=contract,
        trading_day=day,
        granularity_seconds=granularity,
        requested_start=start,
        requested_end=end,
        timezone=timezone,
    )


class FakeAdapter(SourceAdapter):
    """Deterministic non-TqSdk adapter (provider FAKE by default)."""

    def __init__(self, provider="FAKE", provider_version="fake-1.0"):
        self.calls = []
        self._provider = provider
        self._provider_version = provider_version

    @property
    def source_specification(self) -> SourceSpecification:
        return SourceSpecification(
            provider=self._provider,
            source_type="FAKE_HISTORICAL_API",
            endpoint_identity="FakeSource.get_kline_series",
            raw_schema_identity="fake-kline-records-json-v1",
            provider_dataset_version=None,
            normalizer=FAKE_NORMALIZER,
        )

    def acquire(self, request):
        self.calls.append(request.partition_key)
        interval = timedelta(seconds=request.granularity_seconds)
        starts = []
        cursor = request.requested_start
        while cursor + interval <= request.requested_end:
            starts.append(cursor)
            cursor += interval
        if not starts:
            raise AcquisitionError("no bars in coverage")
        records = []
        for index, start in enumerate(starts):
            records.append(
                {
                    "id": index + 1,
                    "datetime": ns(start),
                    "open": 100000,
                    "high": 100010,
                    "low": 99990,
                    "close": 100000,
                    "volume": 10,
                    "open_oi": 1000,
                    "close_oi": 1000,
                    "symbol": request.concrete_instrument,
                }
            )
        payload = json.dumps(records, separators=(",", ":")).encode("utf-8")
        return AcquisitionResult(
            request=request,
            payload=payload,
            returned_start=starts[0],
            returned_end=starts[-1] + interval,
            rows=len(records),
            provider_version=self._provider_version,
        )

    def decode(self, payload, *, artifact, data_version, sessions, minimum_price_tick):
        return normalize_tqsdk_historical_bars(
            payload,
            artifact=artifact,
            data_version=data_version,
            sessions=sessions,
            minimum_price_tick=minimum_price_tick,
        )

    def close(self):
        pass


def build_once(adapter, requests, raw_dir, manifest_path):
    # One explicit session window per (contract, trading day) spanning the
    # union of requested coverages (avoids overlapping-window rejection).
    per_day: dict[tuple, list] = {}
    for request in requests:
        per_day.setdefault((request.concrete_instrument, request.trading_day), []).append(request)
    specs: dict[str, dict] = {}
    for (contract, day), day_requests in per_day.items():
        spec = specs.setdefault(contract, {"windows": [], "tick": "10"})
        start = min(r.requested_start for r in day_requests)
        end = max(r.requested_end for r in day_requests)
        spec["windows"].append(
            SessionWindow(day_requests[0].exchange, contract, day, start, end, "day")
        )
    contracts = {}
    for contract, spec in specs.items():
        sessions = SessionMetadata(f"{contract}-test-v1", spec["windows"])
        fact = ContractMetadataFact(
            exchange="SHFE",
            concrete_instrument=contract,
            minimum_price_tick=Decimal(spec["tick"]),
            session_metadata_version=f"{contract}-test-v1",
            effective_start=date(2025, 6, 16),
            effective_end=date(2025, 6, 20),
            evidence_reference="tests/test_fixture",
            evidence_classification="PILOT_FIXTURE",
        )
        contracts[contract] = ContractConfig(
            concrete_instrument=contract,
            minimum_price_tick=Decimal(spec["tick"]),
            metadata_fact=fact,
            sessions=sessions,
        )
    builder = DatasetBuilder(
        adapter=adapter,
        raw_dir=raw_dir,
        manifest_path=manifest_path,
        schema_version="kline-playbook-dataset-manifest-v1",
        contracts=contracts,
        retrieved_at_provider=lambda: datetime(2026, 8, 16, 14, 0, tzinfo=UTC),
    )
    return builder.build(requests)


class ConcreteSymbolValidationTests(unittest.TestCase):
    def test_rejects_pseudo_main_continuous_and_non_concrete_symbols(self):
        for symbol in (
            "SHFE.ni",
            "SHFE.niMAIN",
            "SHFE.niCONTINUOUS",
            "KQ.m@SHFE.ni",
            "KQ.i@SHFE.ni",
            "SHFE.ni888",
            "SHFE.cu000",
            "rb2510",
            "SHFE.ni25099",
            "",
        ):
            with self.subTest(symbol=symbol):
                with self.assertRaises(InvalidConcreteSymbolError):
                    validate_concrete_symbol(symbol)
        self.assertEqual(validate_concrete_symbol("SHFE.ni2509"), "SHFE.ni2509")

    def test_request_rejects_pseudo_symbols(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 11, 0, tzinfo=CN)
        with self.assertRaises(InvalidConcreteSymbolError):
            make_request("SHFE.niMAIN", "SHFE", date(2025, 6, 16), start, end)


class GenericSourceBoundaryTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raw_dir = Path(self._tmp.name) / "raw"
        self.manifest_path = Path(self._tmp.name) / "manifest.json"

    def test_non_tqsdk_adapter_keeps_its_own_provider_identity(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 11, 0, tzinfo=CN)
        request = make_request("SHFE.ni2509", "SHFE", date(2025, 6, 16), start, end)
        adapter = FakeAdapter(provider="FAKE", provider_version="fake-1.0")
        manifest = build_once(adapter, [request], self.raw_dir, self.manifest_path)
        partition = manifest.partitions[0]
        self.assertEqual(partition.provider, "FAKE")
        self.assertEqual(partition.api_version, "fake-1.0")
        self.assertNotEqual(partition.provider, "TQSDK")
        self.assertEqual(partition.normalizer_identity, FAKE_NORMALIZER.identity_id)
        raw = self.manifest_path.read_bytes().lower()
        self.assertNotIn(b"tqsdk", raw)


class PartitionIdentityCollisionTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raw_dir = Path(self._tmp.name) / "raw"
        self.manifest_path = Path(self._tmp.name) / "manifest.json"

    def test_identical_request_rerun_skips(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 11, 0, tzinfo=CN)
        request = make_request("SHFE.ni2509", "SHFE", date(2025, 6, 16), start, end)
        adapter = FakeAdapter()
        first = build_once(adapter, [request], self.raw_dir, self.manifest_path)
        second = build_once(adapter, [request], self.raw_dir, self.manifest_path)
        self.assertEqual(len(adapter.calls), 1, "identical rerun must skip")
        self.assertEqual(first.identity(), second.identity())

    def test_same_start_different_end_does_not_silently_skip(self):
        day = date(2025, 6, 16)
        base = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        short = make_request("SHFE.ni2509", "SHFE", day, base, base + timedelta(hours=2))
        long = make_request("SHFE.ni2509", "SHFE", day, base, base + timedelta(hours=3))
        adapter = FakeAdapter()
        build_once(adapter, [short], self.raw_dir, self.manifest_path)
        build_once(adapter, [long], self.raw_dir, self.manifest_path)
        self.assertEqual(len(adapter.calls), 2, "changed requested_end must not skip")
        self.assertEqual(len(list(self.raw_dir.glob("*.json"))), 2, "raw filenames must not collide")

    def test_same_end_different_start_does_not_silently_skip(self):
        day = date(2025, 6, 16)
        end = datetime(2025, 6, 16, 11, 0, tzinfo=CN)
        early = make_request("SHFE.ni2509", "SHFE", day, datetime(2025, 6, 16, 9, 0, tzinfo=CN), end)
        late = make_request("SHFE.ni2509", "SHFE", day, datetime(2025, 6, 16, 9, 30, tzinfo=CN), end)
        adapter = FakeAdapter()
        build_once(adapter, [early], self.raw_dir, self.manifest_path)
        build_once(adapter, [late], self.raw_dir, self.manifest_path)
        self.assertEqual(len(adapter.calls), 2, "changed requested_start must not skip")
        self.assertEqual(len(list(self.raw_dir.glob("*.json"))), 2, "raw filenames must not collide")

    def test_different_provider_does_not_collide(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 11, 0, tzinfo=CN)
        request = make_request("SHFE.ni2509", "SHFE", date(2025, 6, 16), start, end)
        build_once(FakeAdapter(provider="FAKE"), [request], self.raw_dir, self.manifest_path)
        other_manifest = Path(self._tmp.name) / "other.json"
        build_once(FakeAdapter(provider="OTHER"), [request], self.raw_dir, other_manifest)
        self.assertEqual(len(list(self.raw_dir.glob("*.json"))), 2, "providers must not share a raw file")

    def test_timezone_change_does_not_collide(self):
        day = date(2025, 6, 16)
        cn = make_request(
            "SHFE.ni2509", "SHFE", day,
            datetime(2025, 6, 16, 9, 0, tzinfo=CN), datetime(2025, 6, 16, 11, 0, tzinfo=CN),
            timezone="Asia/Shanghai",
        )
        utc = make_request(
            "SHFE.ni2509", "SHFE", day,
            datetime(2025, 6, 16, 9, 0, tzinfo=UTC), datetime(2025, 6, 16, 11, 0, tzinfo=UTC),
            timezone="UTC",
        )
        adapter = FakeAdapter()
        build_once(adapter, [cn, utc], self.raw_dir, self.manifest_path)
        self.assertEqual(len(adapter.calls), 2, "timezone change must not skip")
        self.assertEqual(len(list(self.raw_dir.glob("*.json"))), 2, "raw filenames must not collide")

    def test_tampered_raw_fails_closed(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 11, 0, tzinfo=CN)
        request = make_request("SHFE.ni2509", "SHFE", date(2025, 6, 16), start, end)
        adapter = FakeAdapter()
        build_once(adapter, [request], self.raw_dir, self.manifest_path)
        raw_path = self.raw_dir / request.raw_file_name("FAKE")
        raw_path.write_bytes(raw_path.read_bytes() + b" ")
        with self.assertRaises(RawPartitionConflictError):
            build_once(adapter, [request], self.raw_dir, self.manifest_path)


class RetryClassificationTests(unittest.TestCase):
    @staticmethod
    def _fake_error(module, name):
        return type(name, (Exception,), {"__module__": module})("boom")

    def test_is_transient_network_error_classification(self):
        for err in (
            self._fake_error("requests.exceptions", "SSLError"),
            self._fake_error("requests.exceptions", "ConnectionError"),
            self._fake_error("urllib3.exceptions", "ProtocolError"),
            self._fake_error("urllib3.exceptions", "MaxRetryError"),
            TimeoutError("timeout"),
            ConnectionError("conn"),
            OSError("os"),
        ):
            with self.subTest(err=type(err).__name__):
                self.assertTrue(is_transient_network_error(err))
        for err in (
            self._fake_error("requests.exceptions", "HTTPError"),
            self._fake_error("requests.exceptions", "InvalidJSONError"),
            self._fake_error("tqsdk.exceptions", "TqsdkError"),
            ValueError("config"),
        ):
            with self.subTest(err=type(err).__name__):
                self.assertFalse(is_transient_network_error(err))

    def test_retry_decision_is_bounded_and_classified(self):
        transient = self._fake_error("requests.exceptions", "SSLError")
        non_transient = self._fake_error("requests.exceptions", "HTTPError")
        self.assertEqual(retry_decision(1, 3, transient)[0], True)
        self.assertEqual(retry_decision(3, 3, transient)[0], False, "max attempts reached")
        self.assertEqual(retry_decision(1, 3, non_transient)[0], False, "auth-style never retried")


class _ProbeAdapter(TqSdkSourceAdapter):
    """TqSdk adapter stub for deterministic connect/retry tests."""

    def __init__(self, error, *, max_connect_attempts=3, succeed_after=None):
        super().__init__(
            credentials_provider=lambda: ("acct", "pw"),
            max_connect_attempts=max_connect_attempts,
        )
        self.error = error
        self.calls = 0
        self.succeed_after = succeed_after

    def _build_auth(self, account, password):
        return object()

    def _open_api(self, auth):
        self.calls += 1
        if self.succeed_after is not None and self.calls > self.succeed_after:
            self._api = object()
            self._version = "fake"
            return self._api
        raise self.error


class TqSdkConnectRetryTests(unittest.TestCase):
    @staticmethod
    def _fake_error(module, name):
        return type(name, (Exception,), {"__module__": module})("boom")

    def test_connect_auth_style_failure_gets_no_retry(self):
        adapter = _ProbeAdapter(self._fake_error("requests.exceptions", "HTTPError"))
        with self.assertRaisesRegex(AcquisitionError, "non-transient"):
            adapter._connect()
        self.assertEqual(adapter.calls, 1, "authentication-style failure must not be retried")

    def test_connect_transient_failure_is_bounded(self):
        adapter = _ProbeAdapter(
            self._fake_error("requests.exceptions", "SSLError"),
            max_connect_attempts=3,
        )
        with self.assertRaisesRegex(AcquisitionError, "max attempts"):
            adapter._connect()
        self.assertEqual(adapter.calls, 3, "transient retry must be bounded, not infinite")

    def test_connect_recovers_after_transient_failure(self):
        adapter = _ProbeAdapter(
            self._fake_error("requests.exceptions", "SSLError"),
            max_connect_attempts=3,
            succeed_after=2,
        )
        adapter._connect()
        self.assertEqual(adapter.calls, 3)
        self.assertIsNotNone(adapter._api)


class DatasetBuilderTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.raw_dir = Path(self._tmp.name) / "raw"
        self.manifest_path = Path(self._tmp.name) / "manifest.json"

    def test_idempotent_rerun_skips_and_keeps_identity(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 11, 0, tzinfo=CN)
        request = make_request("SHFE.ni2509", "SHFE", date(2025, 6, 16), start, end)
        adapter = FakeAdapter()
        first = build_once(adapter, [request], self.raw_dir, self.manifest_path)
        second = build_once(adapter, [request], self.raw_dir, self.manifest_path)
        self.assertEqual(len(adapter.calls), 1, "rerun must not re-acquire")
        self.assertEqual(first.identity(), second.identity())
        self.assertEqual(first.partitions[0].quality_status, "PASS")

    def test_partial_artifact_is_never_accepted(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 11, 0, tzinfo=CN)
        request = make_request("SHFE.ni2509", "SHFE", date(2025, 6, 16), start, end)
        adapter = FakeAdapter()
        raw_path = self.raw_dir / request.raw_file_name("FAKE")
        partial_path = Path(str(raw_path) + ".partial")
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        partial_path.write_bytes(b"partial-interrupted-content")
        manifest = build_once(adapter, [request], self.raw_dir, self.manifest_path)
        self.assertEqual(len(adapter.calls), 1)
        self.assertFalse(partial_path.exists(), "partial file must be replaced")
        self.assertTrue(raw_path.exists())
        self.assertEqual(manifest.partitions[0].quality_status, "PASS")

    def test_multiple_contracts_and_days_are_deterministic(self):
        def req(contract, day):
            start = datetime(2025, 6, day, 9, 0, tzinfo=CN)
            end = datetime(2025, 6, day, 11, 0, tzinfo=CN)
            return make_request(contract, "SHFE", date(2025, 6, day), start, end)

        requests = [
            req("SHFE.rb2510", 16),
            req("SHFE.rb2510", 17),
            req("SHFE.ni2509", 17),
            req("SHFE.ni2509", 16),
        ]
        adapter = FakeAdapter()
        first = build_once(adapter, requests, self.raw_dir, self.manifest_path)
        second = build_once(adapter, requests, self.raw_dir, self.manifest_path)
        self.assertEqual(len(first.partitions), 4)
        self.assertEqual(first.identity(), second.identity())
        contracts = [p.contract for p in first.partitions]
        self.assertEqual(contracts, sorted(contracts))
        self.assertIn("SHFE.ni2509", contracts)
        self.assertIn("SHFE.rb2510", contracts)

    def test_manifest_is_credential_free(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 11, 0, tzinfo=CN)
        request = make_request("SHFE.ni2509", "SHFE", date(2025, 6, 16), start, end)
        adapter = FakeAdapter()
        build_once(adapter, [request], self.raw_dir, self.manifest_path)
        raw = self.manifest_path.read_bytes().lower()
        for token in (b"password", b"secret", b"token", b"credential", b"auth"):
            self.assertNotIn(token, raw)
        self.assertRegex(
            json.loads(raw.decode("utf-8"))["partitions"][0]["request_identity"],
            r"^[0-9a-f]{64}$",
        )

    def test_data_version_identity_is_deterministic_via_authoritative_path(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 11, 0, tzinfo=CN)
        request = make_request("SHFE.ni2509", "SHFE", date(2025, 6, 16), start, end)
        adapter = FakeAdapter()
        first = build_once(adapter, [request], self.raw_dir, self.manifest_path)
        second = build_once(adapter, [request], self.raw_dir, self.manifest_path)
        self.assertEqual(
            first.partitions[0].data_version_id,
            second.partitions[0].data_version_id,
        )
        self.assertRegex(first.partitions[0].data_version_id, r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
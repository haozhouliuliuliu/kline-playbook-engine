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
    DatasetBuilder,
    InvalidConcreteSymbolError,
    RawPartitionConflictError,
    SourceAdapter,
    validate_concrete_symbol,
)
from src.historical_data import NormalizerIdentity

CN = ZoneInfo("Asia/Shanghai")
UTC = ZoneInfo("UTC")


def ns(ts):
    return int(ts.timestamp() * 1_000_000_000)


def make_request(contract, exchange, day, start, end, granularity=60):
    return AcquisitionRequest(
        exchange=exchange,
        concrete_instrument=contract,
        trading_day=day,
        granularity_seconds=granularity,
        requested_start=start,
        requested_end=end,
    )


NORMALIZER = NormalizerIdentity(
    "tqsdk-3.10.1-fixed-bar-adapter-v1",
    "completed-historical-bar-v1",
    "bar-start-plus-duration-v1",
)


class FakeAdapter(SourceAdapter):
    """Deterministic adapter that emits valid bars over the requested coverage."""

    def __init__(self):
        self.calls = []

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
            provider_version="tqsdk-3.10.1",
        )

    def close(self):
        pass


def build_once(adapter, requests, raw_dir, manifest_path):
    # Accumulate one SessionMetadata per contract covering all its requests.
    specs: dict[str, dict] = {}
    for request in requests:
        spec = specs.setdefault(
            request.concrete_instrument,
            {"windows": [], "tick": "10", "meta": f"{request.concrete_instrument}-contract-v1"},
        )
        spec["windows"].append(
            SessionWindow(
                request.exchange,
                request.concrete_instrument,
                request.trading_day,
                request.requested_start,
                request.requested_end,
                "day",
            )
        )
    contracts = {}
    for contract, spec in specs.items():
        sessions = SessionMetadata(f"{contract}-test-v1", spec["windows"])
        contracts[contract] = ContractConfig(
            concrete_instrument=contract,
            minimum_price_tick=Decimal(spec["tick"]),
            contract_metadata_identity=spec["meta"],
            sessions=sessions,
        )
    builder = DatasetBuilder(
        adapter=adapter,
        raw_dir=raw_dir,
        manifest_path=manifest_path,
        schema_version="kline-playbook-dataset-manifest-v1",
        normalizer=NORMALIZER,
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

    def test_conflicting_raw_fails_closed(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 11, 0, tzinfo=CN)
        request = make_request("SHFE.ni2509", "SHFE", date(2025, 6, 16), start, end)
        adapter = FakeAdapter()
        build_once(adapter, [request], self.raw_dir, self.manifest_path)
        raw_path = self.raw_dir / request.raw_file_name
        tampered = raw_path.read_bytes() + b" "
        raw_path.write_bytes(tampered)
        with self.assertRaises(RawPartitionConflictError):
            build_once(adapter, [request], self.raw_dir, self.manifest_path)

    def test_partial_artifact_is_never_accepted(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = datetime(2025, 6, 16, 11, 0, tzinfo=CN)
        request = make_request("SHFE.ni2509", "SHFE", date(2025, 6, 16), start, end)
        adapter = FakeAdapter()
        raw_path = self.raw_dir / request.raw_file_name
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
        raw = self.manifest_path.read_bytes()
        for token in (b"password", b"secret", b"token", b"credential", b"auth"):
            self.assertNotIn(token.lower(), raw.lower())
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

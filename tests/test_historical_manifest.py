import unittest
from dataclasses import replace
from datetime import date, datetime, timedelta
from pathlib import Path
import tempfile
from zoneinfo import ZoneInfo

from src.historical_manifest import DatasetManifest, ManifestPartition, canonical_hash

CN = ZoneInfo("Asia/Shanghai")


def standard_request(contract, start, end, granularity=60):
    """Non-secret request parameters using the standard parameter names."""
    parameters = (
        ("duration_seconds", str(granularity)),
        ("end_dt", end.isoformat()),
        ("start_dt", start.isoformat()),
        ("symbol", contract),
    )
    return parameters, canonical_hash(parameters)


def partition(contract, day, start_hour=9, start_minute=0, offset_minutes=0):
    start = datetime(2025, 6, day, start_hour, start_minute, tzinfo=CN) + timedelta(minutes=offset_minutes)
    end = start + timedelta(hours=4)
    parameters, request_identity = standard_request(contract, start, end)
    return ManifestPartition(
        provider="FAKE",
        api_version="fake-1.0",
        contract=contract,
        exchange=contract.split(".")[0],
        granularity_seconds=60,
        timezone="Asia/Shanghai",
        trading_day=date(2025, 6, day),
        requested_start=start,
        requested_end=end,
        returned_start=start,
        returned_end=end,
        retrieved_at=datetime(2026, 8, 16, 13, 0, tzinfo=ZoneInfo("UTC")),
        raw_bytes=1234,
        raw_sha256="a" * 64,
        request_identity=request_identity,
        request_parameters=parameters,
        normalizer_identity="c" * 64,
        session_metadata_version="shfe-test-session-v1",
        contract_metadata_identity="d" * 64,
        data_version_id="e" * 64,
        normalized_batch_id="f" * 64,
        quality_status="PASS",
    )


class ManifestIdentityTests(unittest.TestCase):
    def test_manifest_identity_is_deterministic_and_order_independent(self):
        a = partition("SHFE.ni2509", 16)
        b = partition("SHFE.rb2510", 16)
        first = DatasetManifest("manifest-schema-v1", (a, b))
        reversed_entries = DatasetManifest("manifest-schema-v1", (b, a))
        repeated = DatasetManifest("manifest-schema-v1", (a, b))
        self.assertEqual(first.identity(), reversed_entries.identity())
        self.assertEqual(first.identity(), repeated.identity())
        self.assertEqual(first.partitions[0].contract, "SHFE.ni2509")
        self.assertEqual(first.partitions[1].contract, "SHFE.rb2510")

    def test_manifest_identity_changes_with_outcome_affecting_fields(self):
        a = partition("SHFE.ni2509", 16)
        for variant in (
            replace(a, raw_sha256="f" * 64),
            replace(a, trading_day=date(2025, 6, 17)),
            replace(a, timezone="UTC"),
            replace(a, provider="OTHER"),
            replace(a, contract_metadata_identity="0" * 64),
        ):
            with self.subTest(variant=variant):
                self.assertNotEqual(
                    DatasetManifest("manifest-schema-v1", (a,)).identity(),
                    DatasetManifest("manifest-schema-v1", (variant,)).identity(),
                )

    def test_partition_key_accounts_for_requested_end_timezone_provider(self):
        a = partition("SHFE.ni2509", 16)
        longer_end = a.requested_start + timedelta(hours=6)
        params, req_id = standard_request("SHFE.ni2509", a.requested_start, longer_end)
        same_start_longer = replace(
            a,
            requested_end=longer_end,
            returned_end=longer_end,
            request_parameters=params,
            request_identity=req_id,
        )
        different_timezone = replace(a, timezone="UTC")
        different_provider = replace(a, provider="OTHER")
        keys = {
            a.partition_key,
            same_start_longer.partition_key,
            different_timezone.partition_key,
            different_provider.partition_key,
        }
        self.assertEqual(len(keys), 4, "same start + different end / timezone / provider must not collide")

    def test_manifest_rejects_duplicate_partitions(self):
        a = partition("SHFE.ni2509", 16)
        with self.assertRaisesRegex(ValueError, "unique"):
            DatasetManifest("manifest-schema-v1", (a, a))

    def test_manifest_rejects_request_identity_conflicting_with_parameters(self):
        a = partition("SHFE.ni2509", 16)
        # dataclasses.replace re-runs __post_init__ on the frozen dataclass.
        with self.assertRaisesRegex(ValueError, "request identity conflicts"):
            replace(a, request_identity="0" * 64)

    def test_manifest_rejects_request_parameter_contradicting_coverage(self):
        a = partition("SHFE.ni2509", 16)
        with self.assertRaisesRegex(ValueError, "contradicts"):
            replace(a, requested_end=a.requested_end + timedelta(hours=2))

    def test_manifest_rejects_sensitive_request_parameter(self):
        start = datetime(2025, 6, 16, 9, 0, tzinfo=CN)
        end = start + timedelta(hours=4)
        sensitive = (
            ("password", "x"),
            ("symbol", "SHFE.ni2509"),
        )
        base = partition("SHFE.ni2509", 16)
        with self.assertRaisesRegex(ValueError, "credentials"):
            replace(
                base,
                request_parameters=sensitive,
                request_identity=canonical_hash(sensitive),
            )

    def test_manifest_rejects_returned_coverage_outside_requested(self):
        a = partition("SHFE.ni2509", 16)
        with self.assertRaisesRegex(ValueError, "returned coverage"):
            replace(a, returned_end=a.requested_end + timedelta(hours=1))

    def test_manifest_load_save_roundtrip_and_corruption_fails_closed(self):
        a = partition("SHFE.ni2509", 16)
        b = partition("SHFE.rb2510", 17)
        manifest = DatasetManifest("manifest-schema-v1", (a, b))
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            DatasetManifest.save(manifest, path)
            loaded = DatasetManifest.load(path)
            self.assertEqual(loaded.identity(), manifest.identity())
            self.assertEqual(len(loaded.partitions), 2)

            raw = path.read_bytes()
            corrupted = raw.replace(b"PASS", b"FAIL")
            path.write_bytes(corrupted)
            with self.assertRaises(ValueError):
                DatasetManifest.load(path)


if __name__ == "__main__":
    unittest.main()
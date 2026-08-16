import unittest
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
from zoneinfo import ZoneInfo

from src.historical_manifest import DatasetManifest, ManifestPartition

CN = ZoneInfo("Asia/Shanghai")


def partition(contract, day, start_hour=9, start_minute=0, offset_minutes=0):
    start = datetime(2025, 6, day, start_hour, start_minute, tzinfo=CN) + timedelta(minutes=offset_minutes)
    end = start + timedelta(hours=4)
    return ManifestPartition(
        provider="TQSDK",
        api_version="tqsdk-3.10.1",
        contract=contract,
        exchange=contract.split(".")[0],
        granularity_seconds=60,
        requested_start=start,
        requested_end=end,
        returned_start=start,
        returned_end=end,
        retrieved_at=datetime(2026, 8, 16, 13, 0, tzinfo=ZoneInfo("UTC")),
        raw_bytes=1234,
        raw_sha256="a" * 64,
        request_identity="b" * 64,
        normalizer_identity="c" * 64,
        session_metadata_version="shfe-test-session-v1",
        data_version_id="d" * 64,
        normalized_batch_id="e" * 64,
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
        changed_hash = replace(a, raw_sha256="f" * 64)
        self.assertNotEqual(
            DatasetManifest("manifest-schema-v1", (a,)).identity(),
            DatasetManifest("manifest-schema-v1", (changed_hash,)).identity(),
        )

    def test_manifest_rejects_duplicate_partitions(self):
        a = partition("SHFE.ni2509", 16)
        with self.assertRaisesRegex(ValueError, "unique"):
            DatasetManifest("manifest-schema-v1", (a, a))

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

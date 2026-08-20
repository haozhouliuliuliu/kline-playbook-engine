from __future__ import annotations

from datetime import date, datetime, timedelta
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

from src.data_substrate import SessionMetadata, SessionWindow
from src.historical_manifest import canonical_hash
from tools.revalidate_canonical_corpus import build_result, manifest_inventory_partitions, revalidate_partition


CN = ZoneInfo("Asia/Shanghai")


def _at(hour: int, minute: int) -> datetime:
    return datetime(2024, 1, 2, hour, minute, tzinfo=CN)


def _sessions(*, second_window: bool = False) -> SessionMetadata:
    windows = [SessionWindow("SHFE", "SHFE.ni2401", date(2024, 1, 2), _at(9, 0), _at(9, 3), "day")]
    if second_window:
        windows.append(SessionWindow("SHFE", "SHFE.ni2401", date(2024, 1, 2), _at(10, 0), _at(10, 2), "day"))
    return SessionMetadata("synthetic-current-authority", windows)


def _record(start: datetime) -> dict[str, object]:
    return {"datetime": int(start.timestamp() * 1_000_000_000), "symbol": "SHFE.ni2401"}


def _partition(payload: bytes, sessions: SessionMetadata, *, requested_end: datetime | None = None, returned_end: datetime | None = None, recorded_session: str | None = None, quality: str = "PASS") -> dict[str, object]:
    requested_start = _at(9, 0)
    requested_end = requested_end or _at(9, 3)
    return {
        "provider": "TQSDK", "api_version": "3.10.1", "contract": "SHFE.ni2401", "exchange": "SHFE",
        "granularity_seconds": 60, "timezone": "Asia/Shanghai", "trading_day": "2024-01-02",
        "requested_coverage_start": requested_start.isoformat(), "requested_coverage_end": requested_end.isoformat(),
        "returned_coverage_start": requested_start.isoformat(), "returned_coverage_end": (returned_end or requested_end).isoformat(),
        "retrieved_at": _at(16, 0).isoformat(), "raw_bytes": len(payload), "raw_sha256": sha256(payload).hexdigest(),
        "request_identity": "request", "request_parameters": [], "normalizer_identity": "normalizer",
        "session_metadata_version": recorded_session or sessions.version, "contract_metadata_identity": "metadata",
        "data_version_id": "data", "normalized_batch_id": "batch", "quality_status": quality,
    }


def _write_raw(raw_directory: Path, partition: dict[str, object], payload: bytes) -> None:
    tag = canonical_hash((partition["timezone"], partition["requested_coverage_start"], partition["requested_coverage_end"]))[:12]
    name = f"{partition['provider']}.{partition['contract']}.{partition['granularity_seconds']}s.{partition['trading_day']}.{tag}.json"
    raw_directory.mkdir(parents=True, exist_ok=True)
    (raw_directory / name).write_bytes(payload)


class CanonicalCorpusRevalidationTests(unittest.TestCase):
    def _check(self, records: list[dict[str, object]], **partition_options: object):
        sessions = _sessions(second_window=bool(partition_options.pop("second_window", False)))
        payload = json.dumps(records).encode("utf-8")
        partition = _partition(payload, sessions, **partition_options)
        with tempfile.TemporaryDirectory() as temporary:
            raw_directory = Path(temporary) / "raw"
            _write_raw(raw_directory, partition, payload)
            return revalidate_partition(partition, raw_directory, sessions)

    def test_full_returned_coverage_is_eligible(self) -> None:
        check = self._check([_record(_at(9, 0)), _record(_at(9, 1)), _record(_at(9, 2))])
        self.assertTrue(check.passed)

    def test_truncated_returned_coverage_fails(self) -> None:
        check = self._check([_record(_at(9, 0)), _record(_at(9, 1))], returned_end=_at(9, 2))
        self.assertIn("D01_RETURNED_COVERAGE_TRUNCATED", check.reasons)
        self.assertIn("D02_MISSING_EXPECTED_BARS", check.reasons)

    def test_absent_expected_session_window_fails(self) -> None:
        sessions = _sessions(second_window=True)
        payload = json.dumps([_record(_at(9, 0)), _record(_at(9, 1)), _record(_at(9, 2))]).encode("utf-8")
        partition = _partition(payload, sessions, requested_end=_at(10, 2))
        with tempfile.TemporaryDirectory() as temporary:
            raw_directory = Path(temporary) / "raw"
            _write_raw(raw_directory, partition, payload)
            check = revalidate_partition(partition, raw_directory, sessions)
        self.assertEqual(check.missing_expected_bars, 2)
        self.assertIn("D02_MISSING_EXPECTED_BARS", check.reasons)

    def test_missing_expected_minute_fails(self) -> None:
        check = self._check([_record(_at(9, 0)), _record(_at(9, 2))])
        self.assertEqual(check.missing_expected_bars, 1)
        self.assertIn("D02_MISSING_EXPECTED_BARS", check.reasons)

    def test_legacy_session_identity_is_explicitly_revalidated_not_migrated(self) -> None:
        check = self._check([_record(_at(9, 0)), _record(_at(9, 1)), _record(_at(9, 2))], recorded_session="legacy-label")
        self.assertEqual(check.recorded_session_identity, "legacy-label")
        self.assertNotEqual(check.recorded_session_identity, check.current_session_identity)
        self.assertTrue(check.session_identity_changed)

    def test_non_pass_partition_is_not_admissible(self) -> None:
        check = self._check([_record(_at(9, 0)), _record(_at(9, 1)), _record(_at(9, 2))], quality="ANOMALY:test")
        self.assertIn("NON_PASS_PARTITION_NOT_ADMISSIBLE", check.reasons)

    def test_result_identity_is_deterministic(self) -> None:
        check = self._check([_record(_at(9, 0)), _record(_at(9, 1)), _record(_at(9, 2))])
        manifest = {"schema_version": "v1", "manifest_identity": "recorded", "partitions": [_partition(b"[]", _sessions())]}
        # Use a fully deterministic manifest identity fixture separate from the check input.
        first = build_result(manifest, [check], None)
        second = build_result(manifest, [check], None)
        self.assertEqual(first["revalidation_identity"], second["revalidation_identity"])

    def test_manifest_inventory_excludes_unrelated_raw_files(self) -> None:
        manifest_partition = _partition(b"[]", _sessions())
        document = {"schema_version": "v1", "partitions": [manifest_partition]}
        # The inventory helper receives only the manifest.  A raw directory's
        # unrelated JSON files cannot silently expand the canonical inventory.
        self.assertEqual(manifest_inventory_partitions(document), [manifest_partition])

    def test_revalidation_surface_has_no_outcome_api_dependency(self) -> None:
        import tools.revalidate_canonical_corpus as module

        self.assertNotIn("research_firewall", module.__dict__)
        self.assertNotIn("validation_runner", module.__dict__)


if __name__ == "__main__":
    unittest.main()

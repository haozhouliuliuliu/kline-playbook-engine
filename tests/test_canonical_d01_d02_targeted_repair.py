from __future__ import annotations

from datetime import date, datetime, timedelta
import json
from pathlib import Path
import tempfile
import unittest
from zoneinfo import ZoneInfo

from src.historical_acquisition import AcquisitionRequest, AcquisitionResult
from tools.qualify_canonical_d01_d02_repair import (
    EXPECTED_TARGET_COUNT,
    compare_overlapping_values,
    has_historical_provider_value_drift,
    load_failure_inventory,
    qualify_candidate,
    validate_repair_storage,
)


CN = ZoneInfo("Asia/Shanghai")


def _record(start: datetime, *, close: float = 3.0, volume: int | None = 7) -> dict:
    return {
        "datetime": int(start.timestamp() * 1_000_000_000),
        "symbol": "SHFE.cu2501",
        "open": 1.0,
        "high": 4.0,
        "low": 0.5,
        "close": close,
        "volume": volume,
        "open_oi": 10,
        "close_oi": 11,
    }


class _Sessions:
    def __init__(self, starts: list[datetime]) -> None:
        self.starts = starts

    def expected_bar_starts_between(self, exchange, contract, start, end, interval):
        self.last_call = (exchange, contract, start, end, interval)
        return [item for item in self.starts if start <= item and item + interval <= end]


class TargetedRepairTests(unittest.TestCase):
    def setUp(self) -> None:
        self.start = datetime(2025, 1, 2, 9, 0, tzinfo=CN)
        self.end = self.start + timedelta(minutes=2)
        self.request = AcquisitionRequest("SHFE", "SHFE.cu2501", date(2025, 1, 2), 60, self.start, self.end)
        self.sessions = _Sessions([self.start, self.start + timedelta(minutes=1)])

    def test_inventory_comes_only_from_recorded_116_failures(self) -> None:
        root = Path(__file__).resolve().parents[1]
        inventory = load_failure_inventory(root / "docs/evidence/CANONICAL_CORPUS_REVALIDATION_D01_D02_V0_1.json")
        self.assertEqual(EXPECTED_TARGET_COUNT, len(inventory))
        self.assertTrue(all("D01_RETURNED_COVERAGE_TRUNCATED" in item["reasons"] for item in inventory))

    def test_passing_partition_cannot_be_selected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "failures.json"
            path.write_text(json.dumps({"revalidation_result": "FAIL_REPAIRED_COMPLETENESS", "failure_partitions": [{"partition_identity": "x", "reasons": []}] * EXPECTED_TARGET_COUNT}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_failure_inventory(path)

    def test_repair_raw_root_must_be_disjoint_from_historical_root(self) -> None:
        historical = Path("C:/accepted/raw/historical")
        with self.assertRaises(ValueError):
            validate_repair_storage(historical, historical)
        with self.assertRaises(ValueError):
            validate_repair_storage(historical / "candidate", historical)
        self.assertEqual(Path("C:/repair/raw").resolve(), validate_repair_storage(Path("C:/repair/raw"), historical))

    def test_d01_exact_boundaries_and_d02_expected_sessions_pass(self) -> None:
        payload = json.dumps([_record(self.start), _record(self.start + timedelta(minutes=1))]).encode()
        result = AcquisitionResult(self.request, payload, self.start, self.end, 2, "3.10.1")
        self.assertEqual("REPAIRED_PASS", qualify_candidate({}, result, self.sessions))

    def test_same_truncated_provider_response_remains_d01_failure(self) -> None:
        payload = json.dumps([_record(self.start + timedelta(minutes=1))]).encode()
        result = AcquisitionResult(self.request, payload, self.start + timedelta(minutes=1), self.end, 1, "3.10.1")
        self.assertEqual("STILL_D01_TRUNCATED", qualify_candidate({}, result, self.sessions))

    def test_missing_expected_session_bar_remains_d02_failure(self) -> None:
        payload = json.dumps([_record(self.start)]).encode()
        result = AcquisitionResult(self.request, payload, self.start, self.end, 1, "3.10.1")
        self.assertEqual("STILL_D02_MISSING", qualify_candidate({}, result, self.sessions))

    def test_equal_overlapping_ohlc_passes(self) -> None:
        payload = json.dumps([_record(self.start)]).encode()
        comparison = compare_overlapping_values(payload, payload, "Asia/Shanghai", "SHFE.cu2501")
        self.assertEqual(4, comparison["overlapping_ohlc_values_compared"])
        self.assertEqual(0, comparison["overlapping_ohlc_mismatch_count"])

    def test_ohlc_mismatch_is_detected_as_provider_drift_input(self) -> None:
        old_payload = json.dumps([_record(self.start)]).encode()
        new_payload = json.dumps([_record(self.start, close=9.0)]).encode()
        comparison = compare_overlapping_values(old_payload, new_payload, "Asia/Shanghai", "SHFE.cu2501")
        self.assertEqual(1, comparison["overlapping_ohlc_mismatch_count"])
        self.assertTrue(has_historical_provider_value_drift(comparison))

    def test_nullable_volume_is_not_converted_to_zero(self) -> None:
        old_payload = json.dumps([_record(self.start, volume=None)]).encode()
        new_payload = json.dumps([_record(self.start, volume=0)]).encode()
        comparison = compare_overlapping_values(old_payload, new_payload, "Asia/Shanghai", "SHFE.cu2501")
        self.assertEqual(0, comparison["nullable_volume_values_compared"])
        self.assertEqual(0, comparison["nullable_volume_mismatch_count"])

    def test_no_outcome_or_validation_dependency(self) -> None:
        source = Path(__file__).resolve().parents[1] / "tools/qualify_canonical_d01_d02_repair.py"
        content = source.read_text(encoding="utf-8").lower()
        self.assertNotIn("outcome", "\n".join(line for line in content.splitlines() if line.startswith("from ") or line.startswith("import ")))
        self.assertNotIn("validation", "\n".join(line for line in content.splitlines() if line.startswith("from ") or line.startswith("import ")))


if __name__ == "__main__":
    unittest.main()

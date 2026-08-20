from __future__ import annotations

from datetime import date, datetime, time, timedelta
import json
from pathlib import Path
import unittest
from zoneinfo import ZoneInfo

from src.historical_acquisition import AcquisitionRequest, AcquisitionResult
from tools.probe_canonical_first_day_provider import _qualify, _request_for, select_probe_targets
from tools.build_canonical_dataset import build_contract_configs, load_calendar, load_schedules, load_specs, load_universe, load_universe_bounds
from tools.write_canonical_first_day_scope_adjudication import build_adjudication


CN = ZoneInfo("Asia/Shanghai")


class _Sessions:
    def expected_bar_starts_between(self, exchange, contract, start, end, interval):
        return [start + index * interval for index in range(int((end - start) / interval))]


def _payload(starts: list[datetime]) -> bytes:
    return json.dumps([
        {"datetime": int(item.timestamp() * 1_000_000_000), "symbol": "SHFE.cu2501", "open": 1, "high": 2, "low": 0, "close": 1}
        for item in starts
    ]).encode()


class FirstDayProviderProbeTests(unittest.TestCase):
    def test_selection_is_deterministic_and_covers_both_shapes(self) -> None:
        root = Path(__file__).resolve().parents[1]
        selected = select_probe_targets(root / "docs/evidence/CANONICAL_D01_D02_TARGETED_REPAIR_QUALIFICATION_V0_1.json")
        self.assertEqual(6, len(selected))
        self.assertEqual({"PREFIX_ONLY", "MULTIPLE_REGIONS"}, {item["probe_shape"] for item in selected})
        self.assertGreaterEqual(len({item["product"] for item in selected}), 3)

    def test_request_b_is_day_only_diagnostic(self) -> None:
        target = {"contract": "SHFE.cu2501", "trading_day": "2025-01-02", "requested_start": "2025-01-01T21:00:00+08:00", "requested_end": "2025-01-02T15:00:00+08:00"}
        request = _request_for(target, "B")
        self.assertEqual(datetime.combine(date(2025, 1, 2), time(9, 0), tzinfo=CN), request.requested_start)
        self.assertEqual(datetime.combine(date(2025, 1, 2), time(15, 0), tzinfo=CN), request.requested_end)

    def test_exact_day_payload_is_complete(self) -> None:
        start = datetime(2025, 1, 2, 9, 0, tzinfo=CN)
        end = start + timedelta(minutes=2)
        request = AcquisitionRequest("SHFE", "SHFE.cu2501", date(2025, 1, 2), 60, start, end)
        result = AcquisitionResult(request, _payload([start, start + timedelta(minutes=1)]), start, end, 2, "3.10.1")
        self.assertEqual((True, 2, 0), _qualify(result, _Sessions()))

    def test_truncated_provider_response_is_not_complete(self) -> None:
        start = datetime(2025, 1, 2, 9, 0, tzinfo=CN)
        end = start + timedelta(minutes=2)
        request = AcquisitionRequest("SHFE", "SHFE.cu2501", date(2025, 1, 2), 60, start, end)
        result = AcquisitionResult(request, _payload([start + timedelta(minutes=1)]), start + timedelta(minutes=1), end, 1, "3.10.1")
        self.assertEqual((False, 1, 1), _qualify(result, _Sessions()))

    def test_concrete_contract_session_authority_uses_governed_listing_bounds(self) -> None:
        bounds = load_universe_bounds()
        contract = "SHFE.cu2504"
        first_day, last_day = bounds["cu"][contract]
        configs = build_contract_configs(load_calendar(), load_universe(), bounds, load_specs(), load_schedules())
        config = configs[contract]
        self.assertEqual(first_day, config.metadata_fact.effective_start)
        self.assertEqual(last_day, config.metadata_fact.effective_end)
        self.assertFalse(any(window.trading_day < first_day for window in config.sessions._windows))
        first_day_nights = [window for window in config.sessions._windows if window.trading_day == first_day and window.kind == "night"]
        self.assertEqual(1, len(first_day_nights))
        self.assertLess(first_day_nights[0].start.date(), first_day)

    def test_path_c_adjudication_never_permits_provider_coverage_laundering(self) -> None:
        probe = {
            "result": "FIRST_DAY_PROVIDER_DATA_UNAVAILABLE",
            "selected_target_count": 6,
            "totals": {
                "ORIGINAL_REQUEST_REPEATABLE_TRUNCATION": 6,
                "DAY_ONLY_COMPLETE": 3,
                "DAY_ONLY_STILL_TRUNCATED": 3,
                "OVERLAPPING_OHLC_VALUES_COMPARED": 11496,
                "OVERLAPPING_OHLC_MISMATCH_COUNT": 0,
            },
        }
        evidence = build_adjudication(probe)
        self.assertFalse(evidence["targeted_116_reacquisition_permitted"])
        self.assertFalse(evidence["repaired_corpus_materialization_permitted"])


if __name__ == "__main__":
    unittest.main()

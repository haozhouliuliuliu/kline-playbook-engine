"""Offline tests for current DeepSeek-only mechanical guards."""

from __future__ import annotations

import unittest

from src.deepseek_mechanical_guards import (
    NO_4H_EXACT_VOLUME_RECONCILIATION,
    assert_no_4h_exact_volume_reconciliation,
)


class No4HExactVolumeReconciliationTests(unittest.TestCase):
    def test_raw_4h_and_lower_timeframe_volume_are_allowed(self) -> None:
        payload = {
            "panels": [
                {"timeframe": "4H", "ohlcv": {"volume": "12345"}},
                {"timeframe": "1H", "ohlcv": {"volume": "3000"}},
                {"timeframe": "15m", "ohlcv": {"volume": "700"}},
            ]
        }
        assert_no_4h_exact_volume_reconciliation(payload)

    def test_derived_4h_component_volume_sum_is_rejected(self) -> None:
        payload = {
            "cross_timeframe_volume_comparisons": [
                {
                    "target_timeframe": "4H",
                    "component_timeframe": "1H",
                    "component_volume_sum": "12345",
                    "volume_match": True,
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, NO_4H_EXACT_VOLUME_RECONCILIATION):
            assert_no_4h_exact_volume_reconciliation(payload)

    def test_4h_nested_scope_is_rejected(self) -> None:
        payload = {
            "4H": {
                "latest_bar": {"volume": "12345"},
                "volume_reconciliation": {"against": "1H", "exact_volume_match": True},
            }
        }
        with self.assertRaisesRegex(ValueError, NO_4H_EXACT_VOLUME_RECONCILIATION):
            assert_no_4h_exact_volume_reconciliation(payload)

    def test_lower_timeframe_reconciliation_is_not_redefined_by_this_guard(self) -> None:
        payload = {
            "target_timeframe": "1H",
            "component_timeframe": "15m",
            "component_volume_sum": "1000",
            "volume_match": True,
        }
        assert_no_4h_exact_volume_reconciliation(payload)


if __name__ == "__main__":
    unittest.main()

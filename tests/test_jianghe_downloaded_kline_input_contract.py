from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import unittest

from src.jianghe_downloaded_kline_input_contract import (
    DownloadedKlineInputContractV02,
    INPUT_CONTRACT_SCHEMA_IDENTITY,
    INPUT_CONTRACT_VERSION,
)
from src.jianghe_downloaded_kline_pilot import reconstruct_sample
from src.jianghe_ai_trader import JiangheObservation, ObservationBar, ObservationIdentity
from src.jianghe_prespend_runtime import CanonicalStructuredObservationArtifact


class DownloadedKlineInputContractV02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).resolve().parents[1]
        plan = json.loads((root / "docs/evidence/JIANGHE_DOWNLOADED_KLINE_DEEPSEEK_PILOT_PLAN_V0_1.json").read_text(encoding="utf-8"))
        cls.sample = next(item for item in plan["samples"] if item["sample_id"] == "DKL-DS-003")
        cls.observation, cls.structured, cls.visual, cls.hashes = reconstruct_sample(cls.sample)

    def _contract(self) -> dict[str, object]:
        return DownloadedKlineInputContractV02.from_observation(self.observation, self.structured).payload()

    def test_latest_and_penultimate_bars_are_explicit_and_distinct(self) -> None:
        payload = self._contract()
        contracts = {item["timeframe"]: item for item in payload["timeframe_contracts"]}
        latest = contracts["5m"]["latest_closed_bar"]
        penultimate = contracts["5m"]["penultimate_bar"]
        self.assertEqual(INPUT_CONTRACT_VERSION, payload["input_contract_version"])
        self.assertEqual(INPUT_CONTRACT_SCHEMA_IDENTITY, payload["input_contract_schema_identity"])
        self.assertEqual("OLDEST_TO_NEWEST", contracts["5m"]["bar_order"])
        self.assertEqual(35, latest["index"])
        self.assertEqual(34, penultimate["index"])
        self.assertEqual("2025-03-25T14:55:00+08:00", latest["open_time"])
        self.assertEqual("20", latest["ohlcv"]["volume"])
        self.assertEqual("2025-03-25T14:50:00+08:00", penultimate["open_time"])
        self.assertEqual("29", penultimate["ohlcv"]["volume"])

    def test_closed_available_and_decision_boundary_are_enforced(self) -> None:
        payload = self._contract()
        self.assertTrue(all(
            item["latest_closed_bar"]["is_closed"]
            and item["latest_closed_bar"]["available_at"] <= payload["decision_time"]
            and item["latest_closed_bar"]["close_time"] <= payload["decision_time"]
            for item in payload["timeframe_contracts"]
        ))
        altered = deepcopy(self.sample)
        altered["visible_bars"][-1]["available_at"] = (
            self.observation.identity.decision_time + timedelta(minutes=1)
        ).isoformat()
        with self.assertRaisesRegex(ValueError, "post-decision"):
            reconstruct_sample(altered)

    def test_exact_5m_to_15m_volume_mapping_matches(self) -> None:
        payload = self._contract()
        exact = next(
            item for item in payload["cross_timeframe_volume_comparisons"]
            if item["target_timeframe"] == "15m"
            and item["target_bar_index"] == 11
            and item["component_timeframe"] == "5m"
        )
        self.assertTrue(exact["comparison_permitted"])
        self.assertEqual("MATCH", exact["comparison_status"])
        self.assertEqual([33, 34, 35], exact["component_bar_indexes"])
        self.assertEqual(["5", "29", "20"], exact["component_volumes"])
        self.assertEqual("54", exact["component_volume_sum"])
        self.assertEqual("54", exact["target_volume"])

    def test_session_break_or_missing_bucket_is_never_declared_a_mismatch(self) -> None:
        payload = self._contract()
        not_comparable = [
            item for item in payload["cross_timeframe_volume_comparisons"]
            if item["comparison_status"].startswith("NOT_COMPARABLE")
        ]
        self.assertTrue(not_comparable)
        self.assertTrue(all(item["comparison_permitted"] is False for item in not_comparable))

    def test_visual_and_structured_artifacts_are_bound_to_the_same_source(self) -> None:
        self.assertEqual(self.observation.identity.identity, self.structured.source_observation_identity)
        self.assertEqual(self.observation.identity.identity, self.visual.source_observation_identity)
        self.assertEqual(self.sample["png_sha256"], self.hashes["png_sha256"])

    def test_contract_is_generic_not_a_dkl_ds_003_answer_hint(self) -> None:
        zone = timezone(timedelta(hours=8))
        decision_time = datetime(2026, 1, 2, 9, 15, tzinfo=zone)
        def bar(minutes: int, volume: str) -> ObservationBar:
            start = datetime(2026, 1, 2, 9, minutes, tzinfo=zone)
            return ObservationBar(
                timeframe="5m", open_time=start, close_time=start + timedelta(minutes=5),
                available_at=start + timedelta(minutes=5), open_price="100", high_price="102",
                low_price="99", close_price="101", volume=volume, is_closed=True,
            )
        aggregate = ObservationBar(
            timeframe="15m", open_time=datetime(2026, 1, 2, 9, 0, tzinfo=zone),
            close_time=decision_time, available_at=decision_time, open_price="100", high_price="102",
            low_price="99", close_price="101", volume="6", is_closed=True,
        )
        observation = JiangheObservation(
            identity=ObservationIdentity(
                decision_time=decision_time, exchange_time=decision_time, product="demo",
                concrete_contract="SHFE.demo1", mapping_identity="demo-mapping", session_identity="demo-session",
            ),
            bars=(bar(0, "1"), bar(5, "2"), bar(10, "3"), aggregate),
            visible_metadata=(("session", "UNKNOWN"),),
        )
        structured = CanonicalStructuredObservationArtifact.from_observation(observation)
        payload = DownloadedKlineInputContractV02.from_observation(observation, structured).payload()
        latest_5m = next(item for item in payload["timeframe_contracts"] if item["timeframe"] == "5m")["latest_closed_bar"]
        exact = next(item for item in payload["cross_timeframe_volume_comparisons"] if item["target_timeframe"] == "15m")
        self.assertEqual("2026-01-02T09:10:00+08:00", latest_5m["open_time"])
        self.assertEqual("3", latest_5m["ohlcv"]["volume"])
        self.assertEqual("MATCH", exact["comparison_status"])
        self.assertEqual("6", exact["component_volume_sum"])


if __name__ == "__main__":
    unittest.main()

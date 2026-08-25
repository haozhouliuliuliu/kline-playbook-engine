from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import json
from pathlib import Path
import unittest

from src.data_substrate import BarQuality, CompletedBar, SessionMetadata, SessionWindow
from src.historical_data import NormalizedHistoricalBar
from src.jianghe_downloaded_kline_input_contract import INPUT_CONTRACT_SCHEMA_IDENTITY
from src.jianghe_downloaded_kline_final_chance import (
    EVALUATION_DIMENSIONS,
    FOUR_HOUR_AGGREGATION_VERSION,
    SampleNotEligible,
    adjudicate_candidate_against_deepseek,
    build_four_hour_context,
    build_plan_spec,
    verify_plan_spec,
)


ZONE = timezone(timedelta(hours=8))
DAY = date(2026, 1, 2)
CONTRACT = "SHFE.demo2601"


def _minute_rows(windows: tuple[tuple[datetime, datetime], ...]) -> tuple[NormalizedHistoricalBar, ...]:
    result = []
    index = 0
    for start, end in windows:
        cursor = start
        while cursor + timedelta(minutes=1) <= end:
            price = Decimal("100") + Decimal(index) / Decimal("100")
            completed = CompletedBar(
                instrument=CONTRACT,
                trading_day=DAY,
                start=cursor,
                end=cursor + timedelta(minutes=1),
                available_at=cursor + timedelta(minutes=1),
                quality=BarQuality(),
            )
            result.append(
                NormalizedHistoricalBar(
                    exchange="SHFE",
                    concrete_instrument=CONTRACT,
                    source_event_at=completed.end,
                    source_retrieved_at=completed.available_at,
                    completed_bar=completed,
                    open=price,
                    high=price + Decimal("1"),
                    low=price - Decimal("1"),
                    close=price + Decimal("0.25"),
                    volume=Decimal("1"),
                    open_interest_start=Decimal("10"),
                    open_interest_end=Decimal("11"),
                    raw_artifact_identity_id=f"raw-{index}",
                    data_version_id="test-v1",
                )
            )
            cursor += timedelta(minutes=1)
            index += 1
    return tuple(result)


class FinalChancePilotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.windows = (
            (datetime(2026, 1, 2, 9, 0, tzinfo=ZONE), datetime(2026, 1, 2, 10, 0, tzinfo=ZONE)),
            (datetime(2026, 1, 2, 10, 30, tzinfo=ZONE), datetime(2026, 1, 2, 11, 30, tzinfo=ZONE)),
            (datetime(2026, 1, 2, 13, 30, tzinfo=ZONE), datetime(2026, 1, 2, 15, 0, tzinfo=ZONE)),
        )
        session_windows = tuple(
            SessionWindow(
                exchange="SHFE",
                instrument=CONTRACT,
                trading_day=DAY,
                start=start,
                end=end,
                kind="DAY",
            )
            for start, end in self.windows
        )
        self.sessions = SessionMetadata("synthetic-session-authority", session_windows)
        self.rows = _minute_rows(self.windows)

    def test_committed_plan_spec_matches_code(self) -> None:
        root = Path(__file__).resolve().parents[1]
        committed = json.loads(
            (root / "docs/evidence/JIANGHE_DOWNLOADED_KLINE_FINAL_CHANCE_PLAN_SPEC_V0_2.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(committed["plan_spec_identity"], verify_plan_spec(committed))

    def test_plan_spec_is_fail_closed_and_preserves_v02_contract_identity(self) -> None:
        spec = build_plan_spec()
        self.assertEqual("PLAN_NOT_MATERIALIZED", spec["status"])
        self.assertIsNone(spec["next_explicit_paid_slot"])
        self.assertEqual(["4H", "1H", "15m", "5m"], spec["timeframe_stack"])
        self.assertEqual(
            "0057b11939c71f10fa7094db119f5b280e74edd13cb2bb7d40cc29a418c4c68a",
            INPUT_CONTRACT_SCHEMA_IDENTITY,
        )
        self.assertEqual(INPUT_CONTRACT_SCHEMA_IDENTITY, spec["input_contract_schema_identity"])
        self.assertFalse(spec["four_hour_representation"]["cross_timeframe_volume_comparison_eligible"])
        self.assertFalse(spec["four_hour_representation"]["jianghe_permanent_doctrine"])

    def test_4h_grid_uses_official_minutes_and_does_not_treat_break_as_gap(self) -> None:
        bars, descriptors = build_four_hour_context(
            self.rows,
            sessions=self.sessions,
            exchange="SHFE",
            concrete_instrument=CONTRACT,
            trading_day=DAY,
            decision_time=datetime(2026, 1, 2, 15, 0, tzinfo=ZONE),
        )
        self.assertEqual(2, len(bars))
        self.assertEqual("4H", bars[0].timeframe)
        self.assertEqual(datetime(2026, 1, 2, 9, 0, tzinfo=ZONE), bars[0].open_time)
        self.assertEqual(datetime(2026, 1, 2, 11, 30, tzinfo=ZONE), bars[0].close_time)
        self.assertEqual(datetime(2026, 1, 2, 13, 30, tzinfo=ZONE), bars[1].open_time)
        self.assertEqual(datetime(2026, 1, 2, 15, 0, tzinfo=ZONE), bars[1].close_time)
        self.assertEqual(120, descriptors[0].expected_constituent_count)
        self.assertEqual(90, descriptors[1].expected_constituent_count)
        self.assertEqual(FOUR_HOUR_AGGREGATION_VERSION, descriptors[0].aggregation_version)
        self.assertFalse(descriptors[0].volume_comparison_eligible)
        self.assertEqual("120", bars[0].volume)
        self.assertEqual("90", bars[1].volume)

    def test_4h_current_incomplete_grid_bucket_is_not_exposed(self) -> None:
        with self.assertRaisesRegex(SampleNotEligible, "two complete visible 4H"):
            build_four_hour_context(
                self.rows,
                sessions=self.sessions,
                exchange="SHFE",
                concrete_instrument=CONTRACT,
                trading_day=DAY,
                decision_time=datetime(2026, 1, 2, 14, 0, tzinfo=ZONE),
            )

    def test_deepseek_domination_rule_is_correctness_only_and_pre_frozen(self) -> None:
        deepseek = {dimension: "NONE" for dimension in EVALUATION_DIMENSIONS}
        candidate = dict(deepseek)
        candidate["MARKET_FACTUAL_CORRECTNESS"] = "MATERIAL"
        result = adjudicate_candidate_against_deepseek(deepseek, candidate)
        self.assertEqual("DOMINATED_BY_DEEPSEEK", result["verdict"])
        self.assertTrue(result["automatic_elimination"])

        deepseek_mixed = dict(deepseek)
        deepseek_mixed["JIANGHE_SOURCE_FIDELITY"] = "MINOR"
        candidate_mixed = dict(deepseek)
        candidate_mixed["MARKET_FACTUAL_CORRECTNESS"] = "MATERIAL"
        result = adjudicate_candidate_against_deepseek(deepseek_mixed, candidate_mixed)
        self.assertEqual("MIXED_OR_CANDIDATE_ADVANTAGE", result["verdict"])
        self.assertFalse(result["automatic_elimination"])


if __name__ == "__main__":
    unittest.main()

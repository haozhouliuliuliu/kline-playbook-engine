from __future__ import annotations

from datetime import date, timedelta
from dataclasses import fields
import unittest

from src.replay_v0_1_selector import (
    BURN_IN_TRADING_DAYS,
    MEASUREMENT_TRADING_DAYS,
    PRIOR_HISTORY_TRADING_DAYS,
    PRODUCT_ORDER,
    ReplayMappingFact,
    ReplayPartitionFact,
    select_v0_1_slice,
)


def _days(count: int = 70) -> tuple[date, ...]:
    start = date(2024, 1, 2)
    return tuple(start + timedelta(days=index) for index in range(count))


def _facts(calendar, *, product: str, contract: str):
    mappings = tuple(
        ReplayMappingFact(product, calendar[index], contract, f"map-{product}-{index}")
        for index in range(20, 42)
    )
    partitions = tuple(
        ReplayPartitionFact(
            product, contract, calendar[index],
            f"part-{product}-{contract}-{index}", f"session-{index}",
        )
        for index in range(len(calendar))
    )
    return mappings, partitions


class ReplayV01SelectorTests(unittest.TestCase):
    def test_selector_inputs_have_no_market_outcome_fields(self) -> None:
        forbidden = {
            "open", "high", "low", "close", "price", "return", "returns", "pnl",
            "profit", "loss", "volatility", "regime", "news", "outcome", "win_rate",
        }
        for cls in (ReplayMappingFact, ReplayPartitionFact):
            names = {item.name.lower() for item in fields(cls)}
            self.assertTrue(names.isdisjoint(forbidden), names & forbidden)

    def test_first_eligible_cu_window_is_selected_mechanically(self) -> None:
        calendar = _days()
        mappings, partitions = _facts(calendar, product="cu", contract="SHFE.cu2405")
        selected = select_v0_1_slice(
            trading_calendar=calendar, mappings=mappings, partitions=partitions
        )
        self.assertEqual(selected.product, "cu")
        self.assertEqual(selected.concrete_contract, "SHFE.cu2405")
        self.assertEqual(len(selected.prior_history_days), PRIOR_HISTORY_TRADING_DAYS)
        self.assertEqual(len(selected.burn_in_days), BURN_IN_TRADING_DAYS)
        self.assertEqual(len(selected.measurement_days), MEASUREMENT_TRADING_DAYS)
        self.assertEqual(selected.prior_history_days, calendar[:20])
        self.assertEqual(selected.burn_in_days, calendar[20:22])
        self.assertEqual(selected.measurement_days, calendar[22:42])
        self.assertEqual(len(selected.partition_identities), 42)
        self.assertEqual(len(selected.session_identities), 42)

    def test_selector_skips_roll_window_and_uses_first_later_unchanged_contract(self) -> None:
        calendar = _days(80)
        mappings = tuple(
            ReplayMappingFact(
                "cu",
                calendar[index],
                "SHFE.cu2405" if index < 30 else "SHFE.cu2406",
                f"map-{index}",
            )
            for index in range(20, 80)
        )
        partitions = tuple(
            ReplayPartitionFact(
                "cu", "SHFE.cu2406", calendar[index], f"part-{index}", f"session-{index}"
            )
            for index in range(10, 80)
        )
        selected = select_v0_1_slice(
            trading_calendar=calendar, mappings=mappings, partitions=partitions
        )
        self.assertEqual(selected.concrete_contract, "SHFE.cu2406")
        self.assertEqual(selected.burn_in_days[0], calendar[30])

    def test_selector_falls_forward_in_canonical_product_order(self) -> None:
        calendar = _days()
        cu_mappings, _ = _facts(calendar, product="cu", contract="SHFE.cu2405")
        al_mappings, al_partitions = _facts(calendar, product="al", contract="SHFE.al2405")
        selected = select_v0_1_slice(
            trading_calendar=calendar,
            mappings=cu_mappings + al_mappings,
            partitions=al_partitions,
        )
        self.assertEqual(PRODUCT_ORDER[:2], ("cu", "al"))
        self.assertEqual(selected.product, "al")

    def test_ineligible_partition_rejects_earliest_window(self) -> None:
        calendar = _days(80)
        mappings = tuple(
            ReplayMappingFact("cu", calendar[index], "SHFE.cu2405", f"map-{index}")
            for index in range(20, 80)
        )
        partitions = tuple(
            ReplayPartitionFact(
                "cu", "SHFE.cu2405", calendar[index], f"part-{index}", f"session-{index}",
                eligible=index != 0,
            )
            for index in range(80)
        )
        selected = select_v0_1_slice(
            trading_calendar=calendar, mappings=mappings, partitions=partitions
        )
        self.assertEqual(selected.burn_in_days[0], calendar[21])

    def test_duplicate_mapping_fact_fails_closed(self) -> None:
        calendar = _days()
        mapping = ReplayMappingFact("cu", calendar[20], "SHFE.cu2405", "map-20")
        with self.assertRaises(ValueError):
            select_v0_1_slice(
                trading_calendar=calendar, mappings=(mapping, mapping), partitions=()
            )

    def test_no_eligible_slice_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            select_v0_1_slice(trading_calendar=_days(), mappings=(), partitions=())


if __name__ == "__main__":
    unittest.main()

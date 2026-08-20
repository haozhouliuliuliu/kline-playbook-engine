"""Tests for the FAIL-CLOSED canonical build planner (metadata authority)."""

from __future__ import annotations

import unittest
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.metadata_authority import (
    ContractSpec,
    GovernedSource,
    ProductSessionSchedule,
    TradingCalendar,
)
from tools.build_canonical_dataset import (
    COVERAGE_START,
    COVERAGE_END,
    build_requests,
)

CN = ZoneInfo("Asia/Shanghai")


def _source() -> GovernedSource:
    return GovernedSource(
        resource_identity="r", url="https://example.com/official",
        retrieved_at=datetime(2026, 8, 16, tzinfo=CN),
        artifact_sha256="a" * 64, schema_version="v1", classification="OFFICIAL_AVAILABLE",
        effective_period_start=date(2024, 1, 1), effective_period_end=date(2025, 12, 31),
    )


def _calendar() -> TradingCalendar:
    days = []
    d = date(2024, 6, 17)
    for _ in range(5):  # Mon-Fri
        days.append(d)
        d += timedelta(days=1)
    return TradingCalendar("v1", days, _source())


def _specs() -> dict[str, ContractSpec]:
    return {
        "cu": ContractSpec(
            "SHFE", "cu", "CU", Decimal("10"), "yuan/ton", Decimal("5"), "ton/lot",
            "yuan/ton", "1-12", "3", binding_notice="n",
            effective_start=date(2024, 1, 1), effective_end=date(2025, 12, 31), source=_source(),
        )
    }


def _schedules() -> dict[str, ProductSessionSchedule]:
    return {
        "cu": ProductSessionSchedule(
            "SHFE", "cu", date(2024, 1, 1), date(2025, 12, 31),
            ((time(9, 0), time(10, 15)), (time(13, 30), time(15, 0))),
            (time(21, 0), time(1, 0)), timezone="Asia/Shanghai", source=_source(),
        )
    }


def _universe(cu_contracts=None) -> dict[str, list[str]]:
    universe = {p: [] for p in ("cu", "al", "ni", "au", "ag", "rb")}
    if cu_contracts:
        universe["cu"] = list(cu_contracts)
    return universe


def _bounds(cu_bounds=None) -> dict:
    bounds = {}
    if cu_bounds:
        bounds["cu"] = cu_bounds
    return bounds


class FailClosedPlannerTests(unittest.TestCase):
    def test_valid_plan(self) -> None:
        calendar = _calendar()
        universe = _universe(["SHFE.cu2407"])
        bounds = _bounds({"SHFE.cu2407": (date(2024, 6, 17), date(2024, 6, 21))})
        requests = build_requests(
            calendar, universe, bounds, specs=_specs(), schedules=_schedules()
        )
        # Mon 17 (day-only window, no prev day) + Tue 18 .. Fri 21
        self.assertEqual(len(requests), 5)
        self.assertEqual(requests[0].trading_day, date(2024, 6, 17))

    def test_no_effective_spec_period_fails_closed(self) -> None:
        calendar = _calendar()
        universe = _universe(["SHFE.cu2407"])
        bounds = _bounds({"SHFE.cu2407": (date(2024, 6, 17), date(2024, 6, 21))})
        specs = _specs()
        specs["cu"] = ContractSpec(
            "SHFE", "cu", "CU", Decimal("10"), "yuan/ton", Decimal("5"), "ton/lot",
            "yuan/ton", "1-12", "3", binding_notice="n",
            effective_start=date(2026, 1, 1), effective_end=date(2026, 12, 31), source=_source(),
        )
        with self.assertRaises(ValueError):
            build_requests(calendar, universe, bounds, specs=specs, schedules=_schedules())

    def test_conflicting_spec_periods_fail_closed(self) -> None:
        calendar = _calendar()
        universe = _universe(["SHFE.cu2407"])
        bounds = _bounds({"SHFE.cu2407": (date(2024, 6, 17), date(2024, 6, 21))})

        def make(tick: str) -> ContractSpec:
            return ContractSpec(
                "SHFE", "cu", "CU", Decimal(tick), "yuan/ton", Decimal("5"), "ton/lot",
                "yuan/ton", "1-12", "3", binding_notice="n",
                effective_start=date(2024, 1, 1), effective_end=date(2025, 12, 31), source=_source(),
            )

        specs = {
            "cu": make("10"),
            "cu_b": make("20"),  # same product, conflicting value, same effective period
        }
        with self.assertRaises(ValueError):
            build_requests(calendar, universe, bounds, specs=specs, schedules=_schedules())

    def test_unresolved_session_authority_fails_closed(self) -> None:
        calendar = _calendar()
        universe = _universe(["SHFE.cu2407"])
        bounds = _bounds({"SHFE.cu2407": (date(2024, 6, 17), date(2024, 6, 21))})
        schedules = {
            "cu": ProductSessionSchedule(
                "SHFE", "cu", date(2026, 1, 1), date(2026, 12, 31),
                ((time(9, 0), time(10, 15)),), None, timezone="Asia/Shanghai", source=_source(),
            )
        }
        with self.assertRaises(ValueError):
            build_requests(calendar, universe, bounds, specs=_specs(), schedules=schedules)

    def test_listing_expiry_inconsistent_fails_closed(self) -> None:
        calendar = _calendar()
        universe = _universe(["SHFE.cu2407"])
        # internally inconsistent bounds (last before first) must fail closed
        bounds = _bounds({"SHFE.cu2407": (date(2024, 6, 21), date(2024, 6, 17))})
        with self.assertRaises(ValueError):
            build_requests(calendar, universe, bounds, specs=_specs(), schedules=_schedules())

    def test_zero_overlap_is_valid_empty(self) -> None:
        calendar = _calendar()
        universe = _universe(["SHFE.cu2407"])
        # contract bounds outside the corpus calendar -> valid empty plan
        bounds = _bounds({"SHFE.cu2407": (date(2025, 1, 1), date(2025, 1, 31))})
        requests = build_requests(calendar, universe, bounds, specs=_specs(), schedules=_schedules())
        self.assertEqual(requests, [])


if __name__ == "__main__":
    unittest.main()

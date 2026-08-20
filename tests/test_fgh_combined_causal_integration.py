import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.data_substrate import CompletedBar, SessionMetadata, SessionWindow
from src.historical_data import NormalizedHistoricalBar
from src.playbook_contract import MachineReadiness, validate_contract
from src.research_firewall import Cohort, ResearchFirewall
from src.stop_order_execution import (
    COMPLETED_BAR_AVAILABILITY_CONSERVATIVE,
    SUPPORTED_TRIGGER_MODEL_VERSION,
    RestingStopOrder,
    StopSide,
    StopTriggerOutcome,
    evaluate_stop_group,
    stop_trigger_result_to_execution_observation,
)
from src.strategy_evidence import EvidenceLedger, StrategyCatalog
from src.technical_features import (
    FEATURE_IMPLEMENTATION_BINDING,
    FeatureNumericPolicy,
    TimeframeAggregator,
    TimeframeSpec,
    compute_adx,
    compute_ema,
)
from tools.build_raschke_holy_grail_playbook_contract_draft import build_contract


CN = ZoneInfo("Asia/Shanghai")
DAY = date(2025, 1, 6)
POLICY = FeatureNumericPolicy(
    ema_seed_method="SMA",
    adx_initialization_method="WILDER_SMA_DX",
    internal_precision_policy="FULL_DECIMAL",
    output_quantum=Decimal("0.000001"),
    rounding_mode="ROUND_HALF_UP",
)


def at(minute: int) -> datetime:
    return datetime(2025, 1, 6, 9, minute, tzinfo=CN)


def synthetic_bar(index: int, *, first_raw_identity: str = "raw-first") -> NormalizedHistoricalBar:
    start = at(index)
    close = Decimal(100 + index)
    return NormalizedHistoricalBar(
        exchange="SHFE",
        concrete_instrument="cu2502",
        source_event_at=start + timedelta(minutes=1),
        source_retrieved_at=start + timedelta(minutes=1),
        completed_bar=CompletedBar(
            instrument="cu2502",
            trading_day=DAY,
            start=start,
            end=start + timedelta(minutes=1),
            available_at=start + timedelta(minutes=1),
        ),
        open=close,
        high=close + Decimal("1"),
        low=close - Decimal("1"),
        close=close,
        volume=Decimal("1"),
        open_interest_start=Decimal("10"),
        open_interest_end=Decimal("11"),
        raw_artifact_identity_id=(first_raw_identity if index == 0 else f"raw-{index}"),
        data_version_id="combined-synthetic-data-v1",
    )


def aggregate_bars(
    bars: tuple[NormalizedHistoricalBar, ...], sessions: SessionMetadata
):
    return TimeframeAggregator(sessions).aggregate(
        bars,
        spec=TimeframeSpec("1MIN", "INTRADAY", 60, "combined-synthetic-aggregation-v1"),
        exchange="SHFE",
        concrete_instrument="cu2502",
        coverage_start=at(0),
        coverage_end=at(8),
    )


def stop_order(request_id: str, side: StopSide, price: str) -> RestingStopOrder:
    return RestingStopOrder(
        request_id=request_id,
        side=side,
        stop_price=Decimal(price),
        active_at=at(0) - timedelta(seconds=1),
        trigger_model_version=SUPPORTED_TRIGGER_MODEL_VERSION,
        instrument="cu2502",
        concrete_contract_id="cu2502",
        oco_group_id="combined-oco",
    )


class FGHCombinedCausalIntegrationTests(unittest.TestCase):
    def test_full_synthetic_chain_preserves_identity_chronology_and_firewall_locks(self):
        sessions = SessionMetadata(
            "combined-synthetic-session-authority-v1",
            (SessionWindow("SHFE", "cu2502", DAY, at(0), at(8), "DAY"),),
        )
        bars = tuple(synthetic_bar(index) for index in range(8))
        aggregation = aggregate_bars(bars, sessions)
        ema = compute_ema(
            aggregation,
            period=2,
            price_field="close",
            numeric_policy=POLICY,
            feature_version="combined-test-ema-v1",
        )
        adx = compute_adx(
            aggregation,
            period=2,
            numeric_policy=POLICY,
            feature_version="combined-test-adx-v1",
        )

        # A/D: SessionMetadata authority and actual feature implementation bytes propagate.
        self.assertEqual(sessions.version, aggregation.session_metadata_version)
        self.assertEqual(
            FEATURE_IMPLEMENTATION_BINDING.identity_id,
            ema[-1].implementation_artifact_identity,
        )
        self.assertEqual(
            FEATURE_IMPLEMENTATION_BINDING.identity_id,
            adx[-1].implementation_artifact_identity,
        )

        # B: a missing expected bar remains explicit and blocks feature continuity.
        incomplete = aggregate_bars(bars[:-1], sessions)
        with self.assertRaisesRegex(ValueError, "continuity"):
            compute_ema(
                incomplete,
                period=2,
                price_field="close",
                numeric_policy=POLICY,
                feature_version="combined-test-ema-v1",
            )

        # C: changed early evidence changes the full dependency identity even when prices do not.
        changed_bars = tuple(
            synthetic_bar(index, first_raw_identity="raw-first-changed") for index in range(8)
        )
        changed_aggregation = aggregate_bars(changed_bars, sessions)
        changed_ema = compute_ema(
            changed_aggregation,
            period=2,
            price_field="close",
            numeric_policy=POLICY,
            feature_version="combined-test-ema-v1",
        )
        self.assertEqual(ema[-1].value, changed_ema[-1].value)
        self.assertNotEqual(
            ema[-1].dependency_prefix_identity,
            changed_ema[-1].dependency_prefix_identity,
        )

        contract = build_contract()
        readiness = validate_contract(contract)
        self.assertEqual(MachineReadiness.NOT_MACHINE_READY, readiness.readiness)

        orders = (
            stop_order("entry-buy", StopSide.BUY_STOP, "106.5"),
            stop_order("protective-sell", StopSide.SELL_STOP, "95"),
        )
        tuple_group = evaluate_stop_group(orders, bars)
        generator_group = evaluate_stop_group(orders, (item for item in bars))

        # E/F/G/H: identical materialization, evaluated bars, OCO cancellation, honest chronology.
        self.assertEqual(tuple_group.identity_id, generator_group.identity_id)
        by_request = {item.request_id: item for item in tuple_group.results}
        self.assertEqual(StopTriggerOutcome.TRIGGERED, by_request["entry-buy"].outcome)
        self.assertEqual(StopTriggerOutcome.CANCELLED, by_request["protective-sell"].outcome)
        self.assertTrue(by_request["entry-buy"].evaluated_bar_identities)
        self.assertIn(
            by_request["entry-buy"].triggering_bar_identity,
            by_request["entry-buy"].evaluated_bar_identities,
        )
        observation = stop_trigger_result_to_execution_observation(by_request["entry-buy"])
        self.assertEqual(
            COMPLETED_BAR_AVAILABILITY_CONSERVATIVE,
            by_request["entry-buy"].observation_model,
        )
        self.assertFalse(by_request["entry-buy"].exchange_resting_chronology_claimed)
        self.assertEqual(by_request["entry-buy"].bar_available_at, observation.available_at)

        # I/J/K/L: unresolved Holy Grail creates no strategy/outcome object; protected gates stay locked.
        catalog = StrategyCatalog()
        ledger = EvidenceLedger()
        firewall = ResearchFirewall(ledger)
        validation_decision = firewall.gate.evaluate(
            cohort=Cohort.VALIDATION,
            source_only_verified=True,
            statistical_profile_locked=True,
            statistical_profile_test_only=True,
            multiplicity_counting_unit_locked=True,
            research_wave_locked=True,
            primary_scope_search_identities_locked=True,
            synthetic_fixture=True,
        )
        self.assertEqual((), catalog.records)
        self.assertEqual((), firewall.tests.registrations)
        self.assertEqual((), ledger.records)
        self.assertFalse(validation_decision.allowed)
        self.assertTrue(firewall.final_state.is_locked)
        self.assertIsNone(firewall.final_state.unlock_authority)


if __name__ == "__main__":
    unittest.main()

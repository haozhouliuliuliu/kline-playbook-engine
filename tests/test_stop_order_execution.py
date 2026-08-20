import unittest
from dataclasses import replace
from datetime import date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

from src.data_substrate import CompletedBar
from src.historical_data import NormalizedHistoricalBar
from src.stop_order_execution import (
    COMPLETED_BAR_AVAILABILITY_CONSERVATIVE,
    STOP_TRIGGER_IMPLEMENTATION_BINDING,
    SUPPORTED_TRIGGER_MODEL_VERSION,
    RestingStopOrder,
    StopSide,
    StopTriggerOutcome,
    evaluate_stop_group,
    evaluate_stop_order,
    stop_trigger_result_to_execution_observation,
)
from src.strategy_evidence import ArtifactBinding


CN = ZoneInfo("Asia/Shanghai")
DAY = date(2025, 1, 6)


def at(minute: int) -> datetime:
    return datetime(2025, 1, 6, 9, minute, tzinfo=CN)


def bar(
    minute: int,
    *,
    open_price: str = "100",
    high: str = "101",
    low: str = "99",
    close: str = "100",
    raw_identity: str | None = None,
) -> NormalizedHistoricalBar:
    start = at(minute)
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
        open=Decimal(open_price),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=Decimal("1"),
        open_interest_start=Decimal("10"),
        open_interest_end=Decimal("11"),
        raw_artifact_identity_id=raw_identity or f"raw-{minute}",
        data_version_id="synthetic-data-v1",
    )


def order(
    request_id: str,
    side: StopSide,
    stop_price: str,
    *,
    group: str | None = "oco-1",
) -> RestingStopOrder:
    return RestingStopOrder(
        request_id=request_id,
        side=side,
        stop_price=Decimal(stop_price),
        active_at=at(0) - timedelta(seconds=1),
        trigger_model_version=SUPPORTED_TRIGGER_MODEL_VERSION,
        instrument="cu2502",
        concrete_contract_id="cu2502",
        oco_group_id=group,
    )


class StopGroupTests(unittest.TestCase):
    def test_one_shot_generator_and_tuple_produce_identical_group_result(self):
        orders = (
            order("buy", StopSide.BUY_STOP, "105"),
            order("sell", StopSide.SELL_STOP, "95"),
        )
        bars = (bar(0), bar(1, high="106"))

        tuple_result = evaluate_stop_group(orders, bars)
        generator_result = evaluate_stop_group(orders, (item for item in bars))

        self.assertEqual(tuple_result, generator_result)
        self.assertEqual(tuple_result.identity_id, generator_result.identity_id)

    def test_first_unambiguous_trigger_cancels_sibling_before_later_touch(self):
        orders = (
            order("buy", StopSide.BUY_STOP, "105"),
            order("sell", StopSide.SELL_STOP, "95"),
        )
        bars = (
            bar(0),
            bar(1, high="106"),
            bar(2, high="102", low="94"),
        )

        group = evaluate_stop_group(orders, bars)
        by_request = {item.request_id: item for item in group.results}

        self.assertEqual(StopTriggerOutcome.TRIGGERED, by_request["buy"].outcome)
        self.assertEqual(StopTriggerOutcome.CANCELLED, by_request["sell"].outcome)
        self.assertEqual("buy", by_request["sell"].cancelled_by_request_id)
        self.assertEqual(1, len(group.cancellation_evidence))
        self.assertEqual(
            group.cancellation_evidence[0].identity_id,
            by_request["sell"].cancellation_evidence_identity,
        )
        self.assertNotIn(bars[2].identity_id, group.evaluated_bar_identities)

    def test_same_bar_both_touch_is_ambiguous_not_arbitrarily_ordered(self):
        orders = (
            order("buy", StopSide.BUY_STOP, "105"),
            order("sell", StopSide.SELL_STOP, "95"),
        )

        group = evaluate_stop_group(orders, (bar(0, high="106", low="94"),))

        self.assertTrue(
            all(
                item.outcome is StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE
                for item in group.results
            )
        )
        self.assertEqual((), group.cancellation_evidence)
        self.assertTrue(all(item.ambiguity_with == ("buy", "sell") for item in group.results))


class StopOrderEvidenceTests(unittest.TestCase):
    def test_not_triggered_identity_binds_changed_earlier_evaluated_bar(self):
        resting = order("buy", StopSide.BUY_STOP, "110", group=None)
        first_sequence = (
            bar(0, raw_identity="raw-first-a"),
            bar(1),
        )
        changed_sequence = (
            bar(0, raw_identity="raw-first-b"),
            bar(1),
        )

        first = evaluate_stop_order(resting, first_sequence)
        changed = evaluate_stop_order(resting, changed_sequence)

        self.assertEqual(StopTriggerOutcome.NOT_TRIGGERED, first.outcome)
        self.assertEqual(StopTriggerOutcome.NOT_TRIGGERED, changed.outcome)
        self.assertNotEqual(first.evaluated_sequence_identity, changed.evaluated_sequence_identity)
        self.assertNotEqual(first.identity_id, changed.identity_id)

    def test_trigger_result_binds_triggering_bar_and_actual_implementation(self):
        resting = order("buy", StopSide.BUY_STOP, "105", group=None)
        triggering = bar(1, high="106")

        result = evaluate_stop_order(resting, (bar(0), triggering))

        self.assertEqual(StopTriggerOutcome.TRIGGERED, result.outcome)
        self.assertEqual(triggering.identity_id, result.triggering_bar_identity)
        self.assertEqual(
            STOP_TRIGGER_IMPLEMENTATION_BINDING.identity_id,
            result.trigger_model_artifact_identity,
        )

    def test_trigger_model_version_mismatch_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            RestingStopOrder(
                request_id="bad-model",
                side=StopSide.BUY_STOP,
                stop_price=Decimal("105"),
                active_at=at(0),
                trigger_model_version="CALLER_INVENTED_MODEL",
                instrument="cu2502",
            )

    def test_changed_trigger_code_bytes_change_artifact_identity(self):
        source_bytes = Path(STOP_TRIGGER_IMPLEMENTATION_BINDING.artifact_reference).read_bytes()
        changed = ArtifactBinding.from_bytes(
            artifact_kind="code",
            artifact_reference=STOP_TRIGGER_IMPLEMENTATION_BINDING.artifact_reference,
            content=source_bytes + b"\n# synthetic byte change",
            declared_version=STOP_TRIGGER_IMPLEMENTATION_BINDING.declared_version,
        )

        self.assertNotEqual(STOP_TRIGGER_IMPLEMENTATION_BINDING.identity_id, changed.identity_id)

    def test_completed_bar_observation_never_claims_exchange_resting_chronology(self):
        resting = order("buy", StopSide.BUY_STOP, "105", group=None)
        triggering = bar(1, high="106")

        result = evaluate_stop_order(resting, (triggering,))
        observation = stop_trigger_result_to_execution_observation(result)

        self.assertEqual(COMPLETED_BAR_AVAILABILITY_CONSERVATIVE, result.observation_model)
        self.assertFalse(result.exchange_resting_chronology_claimed)
        self.assertEqual(triggering.completed_bar.available_at, observation.observed_at)
        self.assertEqual(triggering.completed_bar.available_at, observation.available_at)

    def test_activation_inside_touching_bar_is_ambiguous(self):
        resting = replace(
            order("buy", StopSide.BUY_STOP, "105", group=None),
            active_at=at(0) + timedelta(seconds=30),
        )

        result = evaluate_stop_order(resting, (bar(0, high="106"),))

        self.assertEqual(StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE, result.outcome)


if __name__ == "__main__":
    unittest.main()

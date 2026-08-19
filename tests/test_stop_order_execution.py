import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.contract_semantics import (
    CloseOffset,
    ContractMappingEntry,
    ContractMappingSchedule,
    ContractMaster,
    ContractSpecification,
    OffsetCostAssumptions,
    OrderAction,
)
from src.data_substrate import BarQuality, CompletedBar
from src.historical_data import NormalizedHistoricalBar
from src.strategy_evidence import (
    DatasetClass,
    EvidenceLedger,
    ExperimentIdentity,
    FinalUnseenFirewall,
    LifecycleState,
    StrategyIdentity,
    TypedParameter,
)
from src.stop_order_execution import (
    STOP_MARKET_TRIGGER_MODEL_V0_1,
    RestingStopOrder,
    SequenceCertainty,
    StopSide,
    StopTriggerOutcome,
    evaluate_stop_group,
    evaluate_stop_order,
    stop_trigger_result_to_execution_observation,
)
from src.validation_runner import (
    CapitalMarginAssumptions,
    CapitalSnapshot,
    ChronologicalValidationRunner,
    ExecutionAssumptions,
    FillStatus,
    OrderSpecification,
    ValidationDisposition,
    ValidationInput,
    ValidationMode,
)


CN = ZoneInfo("Asia/Shanghai")
DAY = date(2025, 6, 16)


def at(hour, minute, second=0):
    return datetime(DAY.year, DAY.month, DAY.day, hour, minute, second, tzinfo=CN)


def make_bar(
    start,
    open_,
    high,
    low,
    close,
    *,
    instrument="TEST",
    available_at=None,
):
    end = start + timedelta(minutes=1)
    if available_at is None:
        available_at = end
    completed = CompletedBar(instrument, DAY, start, end, available_at, BarQuality())
    return NormalizedHistoricalBar(
        exchange="SYNTH_EX",
        concrete_instrument=instrument,
        source_event_at=start,
        source_retrieved_at=end,
        completed_bar=completed,
        open=open_,
        high=high,
        low=low,
        close=close,
        volume=Decimal("0"),
        open_interest_start=None,
        open_interest_end=None,
        raw_artifact_identity_id="raw-fixture-v1",
        data_version_id="data-fixture-v1",
    )


def make_stop(
    request_id,
    side,
    stop_price,
    active_at,
    *,
    instrument="TEST",
    concrete=None,
    oco=None,
):
    return RestingStopOrder(
        request_id=request_id,
        side=side,
        stop_price=stop_price,
        active_at=active_at,
        trigger_model_version=STOP_MARKET_TRIGGER_MODEL_V0_1,
        instrument=instrument,
        concrete_contract_id=concrete,
        oco_group_id=oco,
    )


def make_contract(instrument="TEST", tick=Decimal("0.5")):
    return ContractSpecification(
        exchange="SYNTH_EX",
        product_family="SYNTH",
        instrument_id=instrument,
        listed_at=at(0, 0),
        deactivated_at=at(0, 0) + timedelta(days=365),
        contract_multiplier=Decimal("1"),
        minimum_price_tick=tick,
        currency="SYNTH",
        unit="SYNTH_UNIT",
        price_limit_rule_identity=None,
        offset_fee_metadata_identity="offset-fixture-v1",
        metadata_version="synthetic-contract-metadata-v1",
    )


def make_strategy():
    return StrategyIdentity(
        research_lineage_id="stop-trigger-lineage-fixture",
        family_id="neutral-stop-trigger-family",
        strategy_version="1.0",
        source="deterministic-synthetic-stop-fixture",
        applicable_instruments=("TEST",),
        timeframe="1m",
        parameters=(TypedParameter("window", "int", 3),),
        code_hash="stop-trigger-code-fixture-v1",
        environment_hash="stop-trigger-environment-fixture-v1",
        required_feature_versions=("stop-context-fixture-v1",),
        lifecycle_state=LifecycleState.DRAFT,
        data_exposure_history_reference="stop-exposure-fixture-v1",
    )


class StopOrderEvaluationTests(unittest.TestCase):
    def test_buy_stop_no_trigger(self):
        order = make_stop("buy-1", StopSide.BUY_STOP, Decimal("105"), at(9, 0))
        bars = (
            make_bar(at(9, 1), Decimal("100"), Decimal("104"), Decimal("99"), Decimal("103")),
            make_bar(at(9, 2), Decimal("103"), Decimal("104"), Decimal("101"), Decimal("102")),
        )
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.NOT_TRIGGERED)
        self.assertIs(result.sequence_certainty, SequenceCertainty.UNAMBIGUOUS)
        self.assertIsNone(result.reference_execution_price)

    def test_buy_stop_normal_trigger(self):
        order = make_stop("buy-2", StopSide.BUY_STOP, Decimal("105"), at(9, 0))
        bars = (
            make_bar(at(9, 1), Decimal("100"), Decimal("104"), Decimal("99"), Decimal("103")),
            make_bar(at(9, 2), Decimal("101"), Decimal("107"), Decimal("100"), Decimal("106")),
        )
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.TRIGGERED)
        self.assertEqual(result.reference_execution_price, Decimal("105"))
        self.assertEqual(result.bar_start, at(9, 2))
        self.assertEqual(result.bar_available_at, at(9, 3))

    def test_buy_stop_gap_through(self):
        order = make_stop("buy-3", StopSide.BUY_STOP, Decimal("105"), at(9, 0))
        bars = (make_bar(at(9, 1), Decimal("107"), Decimal("108"), Decimal("106"), Decimal("107")),)
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.TRIGGERED)
        self.assertEqual(result.reference_execution_price, Decimal("107"))

    def test_sell_stop_no_trigger(self):
        order = make_stop("sell-1", StopSide.SELL_STOP, Decimal("95"), at(9, 0))
        bars = (
            make_bar(at(9, 1), Decimal("100"), Decimal("102"), Decimal("96"), Decimal("101")),
            make_bar(at(9, 2), Decimal("101"), Decimal("103"), Decimal("97"), Decimal("102")),
        )
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.NOT_TRIGGERED)
        self.assertIsNone(result.reference_execution_price)

    def test_sell_stop_normal_trigger(self):
        order = make_stop("sell-2", StopSide.SELL_STOP, Decimal("95"), at(9, 0))
        bars = (
            make_bar(at(9, 1), Decimal("100"), Decimal("102"), Decimal("96"), Decimal("101")),
            make_bar(at(9, 2), Decimal("101"), Decimal("102"), Decimal("94"), Decimal("97")),
        )
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.TRIGGERED)
        self.assertEqual(result.reference_execution_price, Decimal("95"))
        self.assertEqual(result.bar_start, at(9, 2))

    def test_sell_stop_gap_through(self):
        order = make_stop("sell-3", StopSide.SELL_STOP, Decimal("95"), at(9, 0))
        bars = (make_bar(at(9, 1), Decimal("93"), Decimal("95"), Decimal("92"), Decimal("94")),)
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.TRIGGERED)
        self.assertEqual(result.reference_execution_price, Decimal("93"))

    def test_off_tick_stop_rejected_when_contract_metadata_supplied(self):
        contract = make_contract("TEST", Decimal("0.5"))
        off_tick = make_stop("off-tick", StopSide.BUY_STOP, Decimal("100.25"), at(9, 0))
        with self.assertRaisesRegex(ValueError, "off-tick stop price"):
            evaluate_stop_order(off_tick, (), contract=contract)
        on_tick = make_stop("on-tick", StopSide.BUY_STOP, Decimal("100.5"), at(9, 0))
        result = evaluate_stop_order(on_tick, (), contract=contract)
        self.assertIs(result.outcome, StopTriggerOutcome.NOT_TRIGGERED)

    def test_contract_binding_mismatch_rejected(self):
        contract = make_contract("OTHER", Decimal("0.5"))
        order = make_stop("mismatch", StopSide.BUY_STOP, Decimal("100.5"), at(9, 0))
        with self.assertRaisesRegex(ValueError, "contract binding disagrees"):
            evaluate_stop_order(order, (), contract=contract)

    def test_pre_activation_bar_cannot_trigger(self):
        order = make_stop("pre-act", StopSide.BUY_STOP, Decimal("105"), at(9, 3))
        bars = (
            make_bar(at(9, 0), Decimal("100"), Decimal("110"), Decimal("99"), Decimal("108")),
            make_bar(at(9, 1), Decimal("108"), Decimal("112"), Decimal("105"), Decimal("110")),
            make_bar(at(9, 2), Decimal("100"), Decimal("104"), Decimal("99"), Decimal("102")),
        )
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.NOT_TRIGGERED)
        # A later eligible bar must be the only possible trigger source.
        bars_with_later = bars + (
            make_bar(at(9, 3), Decimal("102"), Decimal("106"), Decimal("101"), Decimal("105")),
        )
        later = evaluate_stop_order(order, bars_with_later)
        self.assertIs(later.outcome, StopTriggerOutcome.TRIGGERED)
        self.assertEqual(later.bar_start, at(9, 3))

    def test_future_bar_not_visible_too_early(self):
        order = make_stop("future", StopSide.BUY_STOP, Decimal("105"), at(9, 0))
        trigger_bar = make_bar(at(9, 2), Decimal("101"), Decimal("107"), Decimal("100"), Decimal("106"))
        bars = (
            make_bar(at(9, 1), Decimal("100"), Decimal("104"), Decimal("99"), Decimal("103")),
            trigger_bar,
        )
        hidden = evaluate_stop_order(order, bars, cutoff_at=at(9, 2, 30))
        self.assertIs(hidden.outcome, StopTriggerOutcome.NOT_TRIGGERED)
        visible = evaluate_stop_order(order, bars)
        self.assertIs(visible.outcome, StopTriggerOutcome.TRIGGERED)
        self.assertEqual(visible.bar_start, at(9, 2))

    def test_first_eligible_trigger_wins(self):
        order = make_stop("first", StopSide.BUY_STOP, Decimal("105"), at(9, 0))
        bars = (
            make_bar(at(9, 1), Decimal("100"), Decimal("106"), Decimal("99"), Decimal("105")),
            make_bar(at(9, 2), Decimal("107"), Decimal("110"), Decimal("105"), Decimal("109")),
        )
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.TRIGGERED)
        self.assertEqual(result.bar_start, at(9, 1))
        self.assertEqual(result.reference_execution_price, Decimal("105"))

    def test_exact_same_evidence_gives_deterministic_identity_and_result(self):
        order = make_stop("det", StopSide.BUY_STOP, Decimal("105"), at(9, 0))
        bars = (
            make_bar(at(9, 1), Decimal("100"), Decimal("104"), Decimal("99"), Decimal("103")),
            make_bar(at(9, 2), Decimal("101"), Decimal("107"), Decimal("100"), Decimal("106")),
        )
        first = evaluate_stop_order(order, bars)
        second = evaluate_stop_order(order, bars)
        self.assertEqual(first, second)
        self.assertEqual(first.identity_id, second.identity_id)
        different = make_stop("det", StopSide.BUY_STOP, Decimal("106"), at(9, 0))
        changed = evaluate_stop_order(different, bars)
        self.assertNotEqual(first.identity_id, changed.identity_id)

    def test_same_bar_activation_ambiguity_fails_closed(self):
        order = make_stop("inside", StopSide.BUY_STOP, Decimal("105"), at(9, 1, 30))
        bars = (make_bar(at(9, 1), Decimal("100"), Decimal("107"), Decimal("99"), Decimal("106")),)
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE)
        self.assertIs(result.sequence_certainty, SequenceCertainty.AMBIGUOUS_INTRABAR_SEQUENCE)
        self.assertIsNone(result.reference_execution_price)
        self.assertEqual(result.bar_start, at(9, 1))

    def test_boundary_open_crossing_does_not_assume_favorable_ordering(self):
        # active_at == bar.start and the OPEN already crossed the stop: the
        # open print is coincident with activation, so we fail closed rather
        # than assume the order caught the open.
        order = make_stop("boundary", StopSide.BUY_STOP, Decimal("105"), at(9, 1))
        bars = (make_bar(at(9, 1), Decimal("107"), Decimal("108"), Decimal("106"), Decimal("107")),)
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE)

    def test_boundary_open_not_crossed_is_unambiguous(self):
        # active_at == bar.start but the open did NOT cross: any later crossing
        # (high/low) is strictly after activation, so the trigger is real.
        order = make_stop("boundary2", StopSide.BUY_STOP, Decimal("105"), at(9, 1))
        bars = (make_bar(at(9, 1), Decimal("102"), Decimal("107"), Decimal("101"), Decimal("106")),)
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.TRIGGERED)
        self.assertEqual(result.reference_execution_price, Decimal("105"))

    def test_straddling_bar_without_crossing_is_not_ambiguous(self):
        # The order becomes active inside the bar but the threshold was never
        # reached, so the stop could not have triggered at any point.
        order = make_stop("straddle-no", StopSide.BUY_STOP, Decimal("105"), at(9, 1, 30))
        bars = (make_bar(at(9, 1), Decimal("100"), Decimal("104"), Decimal("99"), Decimal("103")),)
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.NOT_TRIGGERED)
        self.assertIs(result.sequence_certainty, SequenceCertainty.UNAMBIGUOUS)

    def test_opposing_oco_stops_both_touched_in_one_bar_ambiguous(self):
        buy = make_stop("oco-buy", StopSide.BUY_STOP, Decimal("105"), at(9, 0), oco="oco-1")
        sell = make_stop("oco-sell", StopSide.SELL_STOP, Decimal("95"), at(9, 0), oco="oco-1")
        bars = (make_bar(at(9, 1), Decimal("100"), Decimal("107"), Decimal("93"), Decimal("100")),)
        results = evaluate_stop_group((buy, sell), bars)
        self.assertEqual(len(results), 2)
        for result in results:
            self.assertIs(result.outcome, StopTriggerOutcome.AMBIGUOUS_INTRABAR_SEQUENCE)
            self.assertIs(result.sequence_certainty, SequenceCertainty.AMBIGUOUS_INTRABAR_SEQUENCE)
            self.assertEqual(result.bar_start, at(9, 1))
            self.assertIn("oco-buy", result.ambiguity_with)
            self.assertIn("oco-sell", result.ambiguity_with)

    def test_oco_single_side_touch_has_no_ambiguity(self):
        buy = make_stop("oco-buy", StopSide.BUY_STOP, Decimal("105"), at(9, 0), oco="oco-2")
        sell = make_stop("oco-sell", StopSide.SELL_STOP, Decimal("90"), at(9, 0), oco="oco-2")
        bars = (make_bar(at(9, 1), Decimal("100"), Decimal("107"), Decimal("93"), Decimal("100")),)
        results = evaluate_stop_group((buy, sell), bars)
        by_request = {result.request_id: result for result in results}
        self.assertIs(by_request["oco-buy"].outcome, StopTriggerOutcome.TRIGGERED)
        self.assertIs(by_request["oco-sell"].outcome, StopTriggerOutcome.NOT_TRIGGERED)

    def test_oco_both_touch_in_different_bars_has_no_same_bar_ambiguity(self):
        buy = make_stop("oco-buy", StopSide.BUY_STOP, Decimal("105"), at(9, 0), oco="oco-3")
        sell = make_stop("oco-sell", StopSide.SELL_STOP, Decimal("95"), at(9, 0), oco="oco-3")
        bars = (
            make_bar(at(9, 1), Decimal("100"), Decimal("107"), Decimal("99"), Decimal("105")),
            make_bar(at(9, 2), Decimal("101"), Decimal("103"), Decimal("94"), Decimal("97")),
        )
        results = evaluate_stop_group((buy, sell), bars)
        by_request = {result.request_id: result for result in results}
        self.assertIs(by_request["oco-buy"].outcome, StopTriggerOutcome.TRIGGERED)
        self.assertEqual(by_request["oco-buy"].bar_start, at(9, 1))
        self.assertIs(by_request["oco-sell"].outcome, StopTriggerOutcome.TRIGGERED)
        self.assertEqual(by_request["oco-sell"].bar_start, at(9, 2))

    def test_group_rejects_mixed_oco_identities(self):
        buy = make_stop("a", StopSide.BUY_STOP, Decimal("105"), at(9, 0), oco="oco-a")
        sell = make_stop("b", StopSide.SELL_STOP, Decimal("95"), at(9, 0), oco="oco-b")
        bars = (make_bar(at(9, 1), Decimal("100"), Decimal("107"), Decimal("93"), Decimal("100")),)
        with self.assertRaisesRegex(ValueError, "cannot mix"):
            evaluate_stop_group((buy, sell), bars)

    def test_higher_timeframe_use_consumes_underlying_one_minute_bars(self):
        # A 30m/60m strategy would aggregate, but stop triggering must consume
        # the underlying ordered 1-minute path when available.
        order = make_stop("htf", StopSide.BUY_STOP, Decimal("105"), at(9, 0))
        bars = (
            make_bar(at(9, 1), Decimal("100"), Decimal("102"), Decimal("99"), Decimal("101")),
            make_bar(at(9, 2), Decimal("101"), Decimal("103"), Decimal("100"), Decimal("102")),
            make_bar(at(9, 3), Decimal("102"), Decimal("104"), Decimal("101"), Decimal("103")),
            make_bar(at(9, 4), Decimal("103"), Decimal("107"), Decimal("102"), Decimal("106")),
            make_bar(at(9, 5), Decimal("106"), Decimal("108"), Decimal("104"), Decimal("107")),
        )
        result = evaluate_stop_order(order, bars)
        self.assertIs(result.outcome, StopTriggerOutcome.TRIGGERED)
        self.assertEqual(result.bar_start, at(9, 4))
        self.assertEqual(result.reference_execution_price, Decimal("105"))

    def test_bridge_rejects_non_triggered_result(self):
        order = make_stop("no-bridge", StopSide.BUY_STOP, Decimal("105"), at(9, 0))
        bars = (make_bar(at(9, 1), Decimal("100"), Decimal("104"), Decimal("99"), Decimal("103")),)
        result = evaluate_stop_order(order, bars)
        with self.assertRaisesRegex(ValueError, "only an unambiguous trigger"):
            stop_trigger_result_to_execution_observation(result)


class StopTriggerPipelineBridgeTests(unittest.TestCase):
    def setUp(self):
        self.strategy = make_strategy()
        self.experiment = ExperimentIdentity.from_strategy(
            self.strategy, "stop-data-fixture-v1", "stop-exposure-fixture-v1"
        )
        self.execution_assumptions = ExecutionAssumptions("synthetic-stop-execution-v1", Decimal("0.5"), Decimal("0.25"))
        self.capital_assumptions = CapitalMarginAssumptions("synthetic-stop-capital-v1", Decimal("1"), Decimal("0.1"), "SYNTH")
        self.capital_snapshot = CapitalSnapshot(Decimal("100"))
        self.offset_costs = OffsetCostAssumptions("synthetic-offset-cost-v1", Decimal("1"), Decimal("2"))

    def run_confirmatory(self, inputs, observations, order_specs, *, cutoff, offset_costs=None):
        ledger = EvidenceLedger()
        runner = ChronologicalValidationRunner(ledger, FinalUnseenFirewall(ledger))
        return runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            artifact_identity_id=self.strategy.identity_id,
            artifact_code_hash=self.strategy.code_hash,
            dataset_class=DatasetClass.VALIDATION,
            inputs=inputs,
            disposition=ValidationDisposition.CONFIRMED,
            execution_observations=observations,
            execution_cutoff_at=cutoff,
            execution_assumptions=self.execution_assumptions,
            order_specifications=order_specs,
            capital_snapshot=self.capital_snapshot,
            capital_margin_assumptions=self.capital_assumptions,
            offset_cost_assumptions=offset_costs,
        )

    def test_bridged_observation_flows_through_existing_pipeline(self):
        # Strategy sees bar A (09:00-09:01) and at 09:01 places a BUY_STOP 105.
        input_bar = make_bar(at(9, 0), Decimal("100"), Decimal("102"), Decimal("99"), Decimal("101"))
        entry_input = ValidationInput("stop-entry-1", input_bar.completed_bar, at(9, 1))
        order = make_stop("stop-entry-1", StopSide.BUY_STOP, Decimal("105"), at(9, 1))
        trigger_bar = make_bar(at(9, 1), Decimal("101"), Decimal("107"), Decimal("100"), Decimal("106"))
        result = evaluate_stop_order(order, (trigger_bar,))
        self.assertIs(result.outcome, StopTriggerOutcome.TRIGGERED)
        observation = stop_trigger_result_to_execution_observation(result)
        self.assertEqual(observation.request_id, "stop-entry-1")
        self.assertEqual(observation.price, Decimal("105"))
        self.assertEqual(observation.available_at, at(9, 2))
        self.assertTrue(observation.tradable)

        run_result = self.run_confirmatory(
            (entry_input,),
            (observation,),
            (OrderSpecification("stop-entry-1", Decimal("1")),),
            cutoff=at(9, 5),
        )
        outcome = run_result.execution_outcomes[0]
        self.assertIs(outcome.status, FillStatus.FILLED)
        self.assertEqual(outcome.fill_price, Decimal("105.5"))
        self.assertEqual(outcome.total_cost, Decimal("0.25"))

    def test_no_duplicate_slippage(self):
        # The bridge emits the deterministic reference price; slippage is
        # applied exactly once by the runner.
        input_bar = make_bar(at(9, 0), Decimal("100"), Decimal("102"), Decimal("99"), Decimal("101"))
        entry_input = ValidationInput("no-slip-1", input_bar.completed_bar, at(9, 1))
        order = make_stop("no-slip-1", StopSide.BUY_STOP, Decimal("105"), at(9, 1))
        trigger_bar = make_bar(at(9, 1), Decimal("101"), Decimal("107"), Decimal("100"), Decimal("106"))
        observation = stop_trigger_result_to_execution_observation(evaluate_stop_order(order, (trigger_bar,)))
        self.assertEqual(observation.price, Decimal("105"))
        run_result = self.run_confirmatory(
            (entry_input,),
            (observation,),
            (OrderSpecification("no-slip-1", Decimal("1")),),
            cutoff=at(9, 5),
        )
        outcome = run_result.execution_outcomes[0]
        self.assertIs(outcome.status, FillStatus.FILLED)
        self.assertEqual(outcome.fill_price, Decimal("105") + self.execution_assumptions.synthetic_slippage)

    def test_no_duplicate_cost_authority(self):
        # OPEN then protective CLOSE through the stop bridge: each transition is
        # charged exactly once by the runner's single cost path.
        entry_bar = make_bar(at(9, 0), Decimal("100"), Decimal("102"), Decimal("99"), Decimal("101"))
        entry_input = ValidationInput("open-1", entry_bar.completed_bar, at(9, 1))
        open_order = make_stop("open-1", StopSide.BUY_STOP, Decimal("105"), at(9, 1))
        open_trigger = make_bar(at(9, 1), Decimal("101"), Decimal("107"), Decimal("100"), Decimal("106"))
        open_observation = stop_trigger_result_to_execution_observation(
            evaluate_stop_order(open_order, (open_trigger,))
        )

        close_input_bar = make_bar(at(9, 2), Decimal("106"), Decimal("107"), Decimal("104"), Decimal("106"))
        close_input = ValidationInput("close-1", close_input_bar.completed_bar, at(9, 3))
        protective = make_stop("close-1", StopSide.SELL_STOP, Decimal("102"), at(9, 3))
        close_trigger = make_bar(at(9, 3), Decimal("104"), Decimal("105"), Decimal("101"), Decimal("103"))
        close_observation = stop_trigger_result_to_execution_observation(
            evaluate_stop_order(protective, (close_trigger,))
        )

        run_result = self.run_confirmatory(
            (entry_input, close_input),
            (open_observation, close_observation),
            (
                OrderSpecification("open-1", Decimal("1")),
                OrderSpecification(
                    "close-1",
                    Decimal("1"),
                    action=OrderAction.CLOSE,
                    close_offset=CloseOffset.CLOSE_TODAY,
                ),
            ),
            cutoff=at(9, 5),
            offset_costs=self.offset_costs,
        )
        outcomes = {outcome.request_id: outcome for outcome in run_result.execution_outcomes}
        self.assertIs(outcomes["open-1"].status, FillStatus.FILLED)
        self.assertIs(outcomes["close-1"].status, FillStatus.FILLED)
        self.assertEqual(outcomes["open-1"].total_cost, self.execution_assumptions.synthetic_fee)
        self.assertEqual(
            outcomes["close-1"].total_cost,
            self.execution_assumptions.synthetic_fee + self.offset_costs.close_today_fee_per_unit,
        )

    def test_long_protective_sell_stop_and_short_protective_buy_stop_share_generic_path(self):
        long_protective = make_stop("long-exit", StopSide.SELL_STOP, Decimal("98"), at(9, 0))
        short_protective = make_stop("short-exit", StopSide.BUY_STOP, Decimal("102"), at(9, 0))
        long_bar = make_bar(at(9, 1), Decimal("100"), Decimal("101"), Decimal("97"), Decimal("99"))
        short_bar = make_bar(at(9, 1), Decimal("100"), Decimal("103"), Decimal("99"), Decimal("101"))
        long_result = evaluate_stop_order(long_protective, (long_bar,))
        short_result = evaluate_stop_order(short_protective, (short_bar,))
        self.assertIs(long_result.outcome, StopTriggerOutcome.TRIGGERED)
        self.assertIs(short_result.outcome, StopTriggerOutcome.TRIGGERED)
        self.assertEqual(long_result.reference_execution_price, Decimal("98"))
        self.assertEqual(short_result.reference_execution_price, Decimal("102"))
        long_observation = stop_trigger_result_to_execution_observation(long_result)
        short_observation = stop_trigger_result_to_execution_observation(short_result)
        self.assertEqual(long_observation.request_id, "long-exit")
        self.assertEqual(short_observation.request_id, "short-exit")

    def test_contract_bound_stop_bridges_concrete_contract_identity(self):
        contract = make_contract("TEST", Decimal("0.5"))
        order = make_stop(
            "contract-stop",
            StopSide.BUY_STOP,
            Decimal("105"),
            at(9, 0),
            concrete="TEST",
        )
        bars = (make_bar(at(9, 1), Decimal("101"), Decimal("107"), Decimal("100"), Decimal("106")),)
        result = evaluate_stop_order(order, bars, contract=contract)
        self.assertIs(result.outcome, StopTriggerOutcome.TRIGGERED)
        observation = stop_trigger_result_to_execution_observation(result)
        self.assertEqual(observation.concrete_contract_id, "TEST")


if __name__ == "__main__":
    unittest.main()

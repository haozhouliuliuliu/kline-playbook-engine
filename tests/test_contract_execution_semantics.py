import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.contract_semantics import (
    CloseOffset,
    ContractMappingEntry,
    ContractMappingSchedule,
    ContractMaster,
    ContractResolver,
    ContractSpecification,
    OffsetCostAssumptions,
    OrderAction,
    PriceLimitFact,
)
from src.data_substrate import CompletedBar, SessionMetadata, SessionWindow
from src.strategy_evidence import (
    DatasetClass,
    EvidenceLedger,
    ExperimentIdentity,
    FinalUnseenFirewall,
    LifecycleState,
    StrategyIdentity,
    TypedParameter,
)
from src.validation_runner import (
    CapitalMarginAssumptions,
    CapitalSnapshot,
    ChronologyError,
    ChronologicalValidationRunner,
    ExecutionAssumptions,
    ExecutionObservation,
    FillStatus,
    MarkObservation,
    OrderSpecification,
    ValidationDisposition,
    ValidationInput,
    ValidationMode,
)


CN = ZoneInfo("Asia/Shanghai")
DAY_1 = date(2025, 6, 16)
DAY_2 = date(2025, 6, 17)
DAY_3 = date(2025, 6, 18)


def at(day, hour, minute):
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=CN)


def make_input(request_id, symbol, trading_day, decision_at):
    return ValidationInput(
        request_id,
        CompletedBar(
            symbol,
            trading_day,
            decision_at - timedelta(minutes=5),
            decision_at,
            decision_at,
        ),
        decision_at,
    )


def make_strategy():
    return StrategyIdentity(
        research_lineage_id="contract-lifecycle-lineage-fixture",
        family_id="neutral-contract-lifecycle-family",
        strategy_version="1.0",
        source="deterministic-synthetic-contract-fixture",
        applicable_instruments=("A", "B", "SYNTH_MAIN"),
        timeframe="5m",
        parameters=(TypedParameter("window", "int", 3),),
        code_hash="contract-lifecycle-code-fixture-v1",
        environment_hash="contract-lifecycle-environment-fixture-v1",
        required_feature_versions=("contract-context-fixture-v1",),
        lifecycle_state=LifecycleState.DRAFT,
        data_exposure_history_reference="contract-exposure-fixture-v1",
    )


class ContractExecutionSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.strategy = make_strategy()
        self.experiment = ExperimentIdentity.from_strategy(
            self.strategy,
            "contract-data-fixture-v1",
            "contract-exposure-fixture-v1",
        )
        self.execution_assumptions = ExecutionAssumptions(
            "synthetic-contract-execution-v1",
            Decimal("0.5"),
            Decimal("0.25"),
        )
        self.capital_assumptions = CapitalMarginAssumptions(
            "synthetic-contract-capital-v1",
            Decimal("1"),
            Decimal("0.1"),
            "SYNTH",
            Decimal("0.05"),
        )
        self.offset_costs = OffsetCostAssumptions(
            "synthetic-offset-cost-v1",
            Decimal("1"),
            Decimal("2"),
        )
        self.contract_a = self.make_contract("A", at(DAY_1, 8, 0), at(DAY_3, 0, 0))
        self.contract_b = self.make_contract("B", at(DAY_1, 9, 30), at(DAY_3, 0, 0))
        self.master = ContractMaster("synthetic-master-v1", (self.contract_a, self.contract_b))
        self.mapping_a = ContractMappingEntry(
            "SYNTH_MAIN",
            "A",
            at(DAY_1, 8, 0),
            at(DAY_1, 10, 0),
            at(DAY_1, 8, 0),
            "synthetic-roll-v1",
        )
        self.mapping_b = ContractMappingEntry(
            "SYNTH_MAIN",
            "B",
            at(DAY_1, 10, 0),
            at(DAY_3, 0, 0),
            at(DAY_1, 9, 59),
            "synthetic-roll-v1",
        )
        self.schedule = ContractMappingSchedule(
            "synthetic-schedule-v1",
            ("SYNTH_MAIN",),
            (self.mapping_a, self.mapping_b),
        )
        self.sessions = SessionMetadata(
            "synthetic-contract-sessions-v1",
            (
                SessionWindow("SYNTH_EX", "A", DAY_1, at(DAY_1, 9, 0), at(DAY_1, 11, 0), "DAY"),
                SessionWindow("SYNTH_EX", "B", DAY_1, at(DAY_1, 9, 0), at(DAY_1, 11, 0), "DAY"),
                SessionWindow("SYNTH_EX", "A", DAY_2, at(DAY_1, 21, 0), at(DAY_1, 23, 0), "NIGHT"),
                SessionWindow("SYNTH_EX", "B", DAY_2, at(DAY_1, 21, 0), at(DAY_1, 23, 0), "NIGHT"),
            ),
        )
        self.limit_facts = (
            self.make_limit("A", self.contract_a, DAY_1, at(DAY_1, 8, 50)),
            self.make_limit("B", self.contract_b, DAY_1, at(DAY_1, 8, 50)),
            self.make_limit("A", self.contract_a, DAY_2, at(DAY_1, 20, 50)),
            self.make_limit("B", self.contract_b, DAY_2, at(DAY_1, 20, 50)),
        )

    def make_contract(self, instrument, listed_at, deactivated_at, tick=Decimal("0.5")):
        return ContractSpecification(
            exchange="SYNTH_EX",
            product_family="SYNTH_PRODUCT",
            instrument_id=instrument,
            listed_at=listed_at,
            deactivated_at=deactivated_at,
            contract_multiplier=Decimal("1"),
            minimum_price_tick=tick,
            currency="SYNTH",
            unit="SYNTH_UNIT",
            price_limit_rule_identity="synthetic-limit-rule-v1",
            offset_fee_metadata_identity=self.offset_costs.identity_id,
            metadata_version="synthetic-contract-metadata-v1",
        )

    def make_limit(
        self,
        instrument,
        contract,
        trading_day,
        available_at,
        *,
        lower=Decimal("90"),
        upper=Decimal("110"),
        locked=False,
    ):
        return PriceLimitFact(
            f"limit-{instrument}-{trading_day.isoformat()}-{locked}",
            instrument,
            contract.identity_id,
            trading_day,
            lower,
            upper,
            available_at,
            available_at,
            "synthetic-limit-rule-v1",
            locked,
        )

    def observation(self, request_id, timestamp, price, contract, tradable=True):
        return ExecutionObservation(
            request_id,
            timestamp,
            timestamp,
            price,
            tradable=tradable,
            concrete_contract_id=contract,
        )

    def run_case(
        self,
        inputs,
        observations,
        specifications,
        *,
        master=None,
        schedule=None,
        sessions=None,
        limit_facts=None,
        dataset=DatasetClass.VALIDATION,
        mark_observations=(),
        forced_liquidation_observations=(),
    ):
        ledger = EvidenceLedger()
        runner = ChronologicalValidationRunner(ledger, FinalUnseenFirewall(ledger))
        result = runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            artifact_identity_id=self.strategy.identity_id,
            artifact_code_hash=self.strategy.code_hash,
            dataset_class=dataset,
            inputs=inputs,
            disposition=ValidationDisposition.CONFIRMED,
            execution_observations=observations,
            execution_cutoff_at=inputs[-1].decision_at + timedelta(minutes=30),
            execution_assumptions=self.execution_assumptions,
            order_specifications=specifications,
            capital_snapshot=CapitalSnapshot(Decimal("100")),
            capital_margin_assumptions=self.capital_assumptions,
            contract_master=master or self.master,
            contract_mapping_schedule=schedule or self.schedule,
            session_metadata=sessions or self.sessions,
            price_limit_facts=self.limit_facts if limit_facts is None else limit_facts,
            offset_cost_assumptions=self.offset_costs,
            mark_observations=mark_observations,
            forced_liquidation_observations=forced_liquidation_observations,
        )
        return result, ledger

    def test_contract_master_identity_is_deterministic_and_outcome_affecting(self):
        same = ContractMaster(
            "synthetic-master-v1",
            (
                self.make_contract("A", at(DAY_1, 8, 0), at(DAY_3, 0, 0)),
                self.make_contract("B", at(DAY_1, 9, 30), at(DAY_3, 0, 0)),
            ),
        )
        changed = ContractMaster(
            "synthetic-master-v1",
            (
                self.make_contract("A", at(DAY_1, 8, 0), at(DAY_3, 0, 0), Decimal("1")),
                self.contract_b,
            ),
        )
        self.assertEqual(self.master.identity_id, same.identity_id)
        self.assertNotEqual(self.master.identity_id, changed.identity_id)
        self.assertEqual(self.master, same)
        self.assertNotEqual(self.master, changed)
        self.assertNotEqual(self.contract_a.identity_id, changed.get("A").identity_id)

    def test_main_resolves_point_in_time_and_future_roll_does_not_change_earlier_resolution(self):
        resolver = ContractResolver(self.master, self.schedule)
        before_roll = resolver.resolve("request-1", "SYNTH_MAIN", at(DAY_1, 9, 5))
        after_roll = resolver.resolve("request-2", "SYNTH_MAIN", at(DAY_1, 10, 5))
        repeated = ContractResolver(self.master, self.schedule).resolve(
            "request-1",
            "SYNTH_MAIN",
            at(DAY_1, 9, 5),
        )
        self.assertEqual(before_roll.concrete_instrument_id, "A")
        self.assertEqual(after_roll.concrete_instrument_id, "B")
        self.assertEqual(before_roll, repeated)
        self.assertEqual(before_roll.mapping_entry_identity_id, self.mapping_a.identity_id)

    def test_unavailable_or_ambiguous_mapping_fails_closed(self):
        unavailable_entry = ContractMappingEntry(
            "SYNTH_MAIN",
            "A",
            at(DAY_1, 8, 0),
            at(DAY_1, 10, 0),
            at(DAY_1, 9, 30),
            "unavailable-v1",
        )
        unavailable_schedule = ContractMappingSchedule(
            "unavailable-schedule-v1",
            ("SYNTH_MAIN",),
            (unavailable_entry,),
        )
        with self.assertRaisesRegex(ValueError, "exactly one"):
            ContractResolver(self.master, unavailable_schedule).resolve(
                "request-1",
                "SYNTH_MAIN",
                at(DAY_1, 9, 5),
            )

        overlapping = ContractMappingEntry(
            "SYNTH_MAIN",
            "B",
            at(DAY_1, 9, 0),
            at(DAY_1, 10, 30),
            at(DAY_1, 8, 55),
            "ambiguous-v1",
        )
        ambiguous_schedule = ContractMappingSchedule(
            "ambiguous-schedule-v1",
            ("SYNTH_MAIN",),
            (self.mapping_a, overlapping),
        )
        with self.assertRaisesRegex(ValueError, "exactly one"):
            ContractResolver(self.master, ambiguous_schedule).resolve(
                "request-1",
                "SYNTH_MAIN",
                at(DAY_1, 9, 5),
            )

    def test_pseudo_symbol_cannot_be_used_as_execution_contract(self):
        input_item = make_input("request-1", "SYNTH_MAIN", DAY_1, at(DAY_1, 9, 5))
        with self.assertRaisesRegex(ValueError, "not a pseudo-symbol"):
            self.run_case(
                (input_item,),
                (self.observation("request-1", at(DAY_1, 9, 6), Decimal("100"), "SYNTH_MAIN"),),
                (OrderSpecification("request-1", Decimal("1")),),
            )

    def test_pre_listing_and_post_expiry_execution_fail_closed(self):
        pre_listing = make_input("request-1", "B", DAY_1, at(DAY_1, 9, 5))
        with self.assertRaisesRegex(ValueError, "not active"):
            self.run_case(
                (pre_listing,),
                (self.observation("request-1", at(DAY_1, 9, 6), Decimal("100"), "B"),),
                (OrderSpecification("request-1", Decimal("1")),),
            )

        post_expiry = make_input("request-2", "A", DAY_3, at(DAY_3, 9, 5))
        with self.assertRaisesRegex(ValueError, "not active"):
            self.run_case(
                (post_expiry,),
                (self.observation("request-2", at(DAY_3, 9, 6), Decimal("100"), "A"),),
                (OrderSpecification("request-2", Decimal("1")),),
            )

    def test_on_tick_in_limit_price_fills_and_binds_concrete_contract(self):
        input_item = make_input("request-1", "SYNTH_MAIN", DAY_1, at(DAY_1, 9, 5))
        result, _ = self.run_case(
            (input_item,),
            (self.observation("request-1", at(DAY_1, 9, 6), Decimal("100"), "A"),),
            (OrderSpecification("request-1", Decimal("1")),),
        )
        outcome = result.execution_outcomes[0]
        snapshot = result.final_capital_snapshot
        self.assertEqual(outcome.status, FillStatus.FILLED)
        self.assertEqual(outcome.fill_price, Decimal("100.5"))
        self.assertEqual(outcome.concrete_contract_id, "A")
        self.assertIsNotNone(outcome.price_limit_fact_id)
        self.assertEqual(snapshot.position_instrument, "A")
        self.assertEqual(snapshot.concrete_contract_id, "A")
        self.assertEqual(snapshot.contract_identity_id, self.contract_a.identity_id)
        self.assertEqual(snapshot.mapping_entry_identity_id, self.mapping_a.identity_id)

    def test_off_tick_price_is_not_filled_without_rounding(self):
        input_item = make_input("request-1", "SYNTH_MAIN", DAY_1, at(DAY_1, 9, 5))
        result, _ = self.run_case(
            (input_item,),
            (self.observation("request-1", at(DAY_1, 9, 6), Decimal("100.25"), "A"),),
            (OrderSpecification("request-1", Decimal("1")),),
        )
        self.assertEqual(result.execution_outcomes[0].status, FillStatus.NOT_FILLED)
        self.assertEqual(result.execution_outcomes[0].reason, "OFF_TICK_PRICE")
        self.assertIsNone(result.execution_outcomes[0].fill_price)

    def test_outside_or_locked_limit_does_not_fill_and_missing_fact_fails_closed(self):
        input_item = make_input("request-1", "SYNTH_MAIN", DAY_1, at(DAY_1, 9, 5))
        outside, _ = self.run_case(
            (input_item,),
            (self.observation("request-1", at(DAY_1, 9, 6), Decimal("111"), "A"),),
            (OrderSpecification("request-1", Decimal("1")),),
        )
        self.assertEqual(outside.execution_outcomes[0].reason, "OUTSIDE_PRICE_LIMIT")

        locked_fact = self.make_limit(
            "A",
            self.contract_a,
            DAY_1,
            at(DAY_1, 8, 50),
            locked=True,
        )
        locked, _ = self.run_case(
            (input_item,),
            (self.observation("request-1", at(DAY_1, 9, 6), Decimal("100"), "A"),),
            (OrderSpecification("request-1", Decimal("1")),),
            limit_facts=(locked_fact,),
        )
        self.assertEqual(locked.execution_outcomes[0].reason, "LOCKED_PRICE_LIMIT")

        with self.assertRaisesRegex(ValueError, "price-limit metadata"):
            self.run_case(
                (input_item,),
                (self.observation("request-1", at(DAY_1, 9, 6), Decimal("100"), "A"),),
                (OrderSpecification("request-1", Decimal("1")),),
                limit_facts=(),
            )

    def test_roll_does_not_mutate_a_and_b_open_is_a_distinct_position_fact(self):
        inputs = (
            make_input("open-a", "SYNTH_MAIN", DAY_1, at(DAY_1, 9, 5)),
            make_input("close-a", "A", DAY_1, at(DAY_1, 10, 5)),
            make_input("open-b", "SYNTH_MAIN", DAY_1, at(DAY_1, 10, 10)),
        )
        observations = (
            self.observation("open-a", at(DAY_1, 9, 6), Decimal("100"), "A"),
            self.observation("close-a", at(DAY_1, 10, 6), Decimal("101"), "A"),
            self.observation("open-b", at(DAY_1, 10, 11), Decimal("102"), "B"),
        )
        specifications = (
            OrderSpecification("open-a", Decimal("1")),
            OrderSpecification("close-a", Decimal("1"), OrderAction.CLOSE, CloseOffset.CLOSE_TODAY),
            OrderSpecification("open-b", Decimal("1")),
        )
        result, ledger = self.run_case(inputs, observations, specifications)
        open_a, close_a, open_b = result.capital_transitions
        self.assertEqual(open_a.after.concrete_contract_id, "A")
        self.assertEqual(close_a.before.concrete_contract_id, "A")
        self.assertEqual(close_a.after.position_quantity, Decimal("0"))
        self.assertEqual(open_b.after.concrete_contract_id, "B")
        self.assertNotEqual(open_a.after.position_id, open_b.after.position_id)
        self.assertEqual(result.contract_resolutions[0].mapping_entry_identity_id, self.mapping_a.identity_id)
        self.assertEqual(result.contract_resolutions[2].mapping_entry_identity_id, self.mapping_b.identity_id)
        position_facts = [record.fact_reference for record in ledger.records if record.event_type == "POSITION_TRANSITION"]
        self.assertEqual(len(position_facts), 3)
        self.assertEqual(len(set(position_facts)), 3)

    def test_roll_cannot_silently_replace_open_a_with_b(self):
        inputs = (
            make_input("open-a", "SYNTH_MAIN", DAY_1, at(DAY_1, 9, 5)),
            make_input("open-b", "SYNTH_MAIN", DAY_1, at(DAY_1, 10, 5)),
        )
        observations = (
            self.observation("open-a", at(DAY_1, 9, 6), Decimal("100"), "A"),
            self.observation("open-b", at(DAY_1, 10, 6), Decimal("102"), "B"),
        )
        with self.assertRaisesRegex(ValueError, "cannot silently change"):
            self.run_case(
                inputs,
                observations,
                (
                    OrderSpecification("open-a", Decimal("1")),
                    OrderSpecification("open-b", Decimal("1")),
                ),
            )

    def test_trading_day_transition_ages_today_bucket_using_session_authority(self):
        inputs = (
            make_input("open-a", "A", DAY_1, at(DAY_1, 9, 5)),
            make_input("close-previous", "A", DAY_2, at(DAY_1, 21, 5)),
        )
        observations = (
            self.observation("open-a", at(DAY_1, 9, 6), Decimal("100"), "A"),
            self.observation("close-previous", at(DAY_1, 21, 6), Decimal("101"), "A"),
        )
        specifications = (
            OrderSpecification("open-a", Decimal("2")),
            OrderSpecification(
                "close-previous",
                Decimal("1"),
                OrderAction.CLOSE,
                CloseOffset.CLOSE_PREVIOUS,
            ),
        )
        result, _ = self.run_case(inputs, observations, specifications)
        close_transition = result.capital_transitions[1]
        final = result.final_capital_snapshot
        self.assertEqual(close_transition.aged_quantity, Decimal("2"))
        self.assertEqual(close_transition.resolved_close_offset, CloseOffset.CLOSE_PREVIOUS)
        self.assertEqual(result.execution_outcomes[1].total_cost, Decimal("2.25"))
        self.assertEqual(final.today_quantity, Decimal("0"))
        self.assertEqual(final.previous_quantity, Decimal("1"))
        self.assertEqual(final.position_quantity, Decimal("1"))
        self.assertEqual(final.position_trading_day, DAY_2)

    def test_close_offsets_cannot_substitute_position_buckets(self):
        same_day_inputs = (
            make_input("open-a", "A", DAY_1, at(DAY_1, 9, 5)),
            make_input("wrong-previous", "A", DAY_1, at(DAY_1, 9, 10)),
        )
        same_day_observations = (
            self.observation("open-a", at(DAY_1, 9, 6), Decimal("100"), "A"),
            self.observation("wrong-previous", at(DAY_1, 9, 11), Decimal("101"), "A"),
        )
        with self.assertRaisesRegex(ValueError, "previous-day position bucket"):
            self.run_case(
                same_day_inputs,
                same_day_observations,
                (
                    OrderSpecification("open-a", Decimal("1")),
                    OrderSpecification(
                        "wrong-previous",
                        Decimal("1"),
                        OrderAction.CLOSE,
                        CloseOffset.CLOSE_PREVIOUS,
                    ),
                ),
            )

        next_day_inputs = (
            make_input("open-a", "A", DAY_1, at(DAY_1, 9, 5)),
            make_input("wrong-today", "A", DAY_2, at(DAY_1, 21, 5)),
        )
        next_day_observations = (
            self.observation("open-a", at(DAY_1, 9, 6), Decimal("100"), "A"),
            self.observation("wrong-today", at(DAY_1, 21, 6), Decimal("101"), "A"),
        )
        with self.assertRaisesRegex(ValueError, "today's position bucket"):
            self.run_case(
                next_day_inputs,
                next_day_observations,
                (
                    OrderSpecification("open-a", Decimal("1")),
                    OrderSpecification(
                        "wrong-today",
                        Decimal("1"),
                        OrderAction.CLOSE,
                        CloseOffset.CLOSE_TODAY,
                    ),
                ),
            )

    def test_offset_sensitive_cost_identity_and_result_are_deterministic(self):
        same = OffsetCostAssumptions(
            "synthetic-offset-cost-v1",
            Decimal("1"),
            Decimal("2"),
        )
        changed = OffsetCostAssumptions(
            "synthetic-offset-cost-v1",
            Decimal("1.5"),
            Decimal("2"),
        )
        self.assertEqual(self.offset_costs.identity_id, same.identity_id)
        self.assertNotEqual(self.offset_costs.identity_id, changed.identity_id)

        inputs = (
            make_input("open-a", "A", DAY_1, at(DAY_1, 9, 5)),
            make_input("close-today", "A", DAY_1, at(DAY_1, 9, 10)),
        )
        observations = (
            self.observation("open-a", at(DAY_1, 9, 6), Decimal("100"), "A"),
            self.observation("close-today", at(DAY_1, 9, 11), Decimal("101"), "A"),
        )
        specifications = (
            OrderSpecification("open-a", Decimal("1")),
            OrderSpecification("close-today", Decimal("1"), OrderAction.CLOSE, CloseOffset.CLOSE_TODAY),
        )
        result, _ = self.run_case(inputs, observations, specifications)
        close_outcome = result.execution_outcomes[1]
        self.assertEqual(close_outcome.total_cost, Decimal("1.25"))
        self.assertEqual(close_outcome.offset_cost_assumption_id, self.offset_costs.identity_id)
        self.assertEqual(close_outcome.resolved_close_offset, CloseOffset.CLOSE_TODAY)

    def test_later_order_decision_cannot_precede_prior_capital_state(self):
        inputs = (
            make_input("open-a", "A", DAY_1, at(DAY_1, 9, 5)),
            make_input("increase-a", "A", DAY_1, at(DAY_1, 9, 10)),
        )
        observations = (
            self.observation("open-a", at(DAY_1, 9, 20), Decimal("100"), "A"),
            self.observation("increase-a", at(DAY_1, 9, 21), Decimal("100"), "A"),
        )
        specifications = (
            OrderSpecification("open-a", Decimal("1")),
            OrderSpecification("increase-a", Decimal("1")),
        )

        with self.assertRaisesRegex(ChronologyError, "order decision must follow"):
            self.run_case(inputs, observations, specifications)

    def test_repeated_history_has_identical_mapping_execution_position_and_evidence(self):
        inputs = (make_input("open-a", "SYNTH_MAIN", DAY_1, at(DAY_1, 9, 5)),)
        observations = (self.observation("open-a", at(DAY_1, 9, 6), Decimal("100"), "A"),)
        specifications = (OrderSpecification("open-a", Decimal("1")),)
        first, first_ledger = self.run_case(inputs, observations, specifications)
        second, second_ledger = self.run_case(inputs, observations, specifications)
        self.assertEqual(first.contract_resolutions, second.contract_resolutions)
        self.assertEqual(first.execution_outcomes, second.execution_outcomes)
        self.assertEqual(first.capital_transitions, second.capital_transitions)
        self.assertEqual(first.final_capital_snapshot, second.final_capital_snapshot)
        self.assertEqual(
            [record.record_id for record in first_ledger.records],
            [record.record_id for record in second_ledger.records],
        )

    def test_evidence_binds_contract_mapping_limit_offset_and_existing_identities(self):
        inputs = (
            make_input("open-a", "SYNTH_MAIN", DAY_1, at(DAY_1, 9, 5)),
            make_input("close-a", "A", DAY_1, at(DAY_1, 9, 10)),
        )
        observations = (
            self.observation("open-a", at(DAY_1, 9, 6), Decimal("100"), "A"),
            self.observation("close-a", at(DAY_1, 9, 11), Decimal("101"), "A"),
        )
        specifications = (
            OrderSpecification("open-a", Decimal("1")),
            OrderSpecification("close-a", Decimal("1"), OrderAction.CLOSE, CloseOffset.CLOSE_TODAY),
        )
        result, ledger = self.run_case(inputs, observations, specifications)
        resolution_record = next(record for record in ledger.records if record.event_type == "CONTRACT_RESOLVED")
        open_record, close_record = [record for record in ledger.records if record.event_type == "EXECUTION_FILLED"]
        open_outcome = result.execution_outcomes[0]
        self.assertEqual(resolution_record.experiment, self.experiment)
        self.assertIn(self.master.identity_id, resolution_record.evidence_reference)
        self.assertIn(self.schedule.identity_id, resolution_record.evidence_reference)
        self.assertEqual(open_outcome.contract_master_identity_id, self.master.identity_id)
        self.assertEqual(open_outcome.mapping_schedule_identity_id, self.schedule.identity_id)
        self.assertEqual(open_outcome.mapping_entry_identity_id, self.mapping_a.identity_id)
        self.assertIn(self.master.identity_id, open_record.evidence_reference)
        self.assertIn(self.schedule.identity_id, open_record.evidence_reference)
        self.assertIn(self.mapping_a.identity_id, open_record.evidence_reference)
        self.assertIn(self.execution_assumptions.identity_id, close_record.evidence_reference)
        self.assertIn(self.capital_assumptions.identity_id, close_record.evidence_reference)
        self.assertIn(self.offset_costs.identity_id, close_record.evidence_reference)
        self.assertIn("close_offset:CLOSE_TODAY", close_record.evidence_reference)
        self.assertIsNotNone(close_record.fact_reference)
        self.assertIn(result.contract_resolutions[0].identity_id, result.validation_record.evidence_reference)

    def test_forced_liquidation_cannot_bypass_concrete_contract_binding(self):
        input_item = make_input("open-a", "SYNTH_MAIN", DAY_1, at(DAY_1, 9, 5))
        opening_observation = self.observation("open-a", at(DAY_1, 9, 6), Decimal("100"), "A")
        opening, _ = self.run_case(
            (input_item,),
            (opening_observation,),
            (OrderSpecification("open-a", Decimal("1")),),
        )
        snapshot = opening.final_capital_snapshot
        mark = MarkObservation(
            "adverse-mark",
            snapshot.position_id,
            snapshot.position_request_id,
            "A",
            at(DAY_1, 9, 10),
            at(DAY_1, 9, 10),
            Decimal("0.5"),
        )
        breached, _ = self.run_case(
            (input_item,),
            (opening_observation,),
            (OrderSpecification("open-a", Decimal("1")),),
            mark_observations=(mark,),
        )
        requirement = breached.liquidation_requirement
        wrong_contract_observation = self.observation(
            requirement.request_id,
            at(DAY_1, 9, 12),
            Decimal("100"),
            "B",
        )
        with self.assertRaisesRegex(ValueError, "concrete contract"):
            self.run_case(
                (input_item,),
                (opening_observation,),
                (OrderSpecification("open-a", Decimal("1")),),
                mark_observations=(mark,),
                forced_liquidation_observations=(wrong_contract_observation,),
            )

    def test_final_unseen_is_denied_before_contract_resolution(self):
        input_item = make_input("request-1", "SYNTH_MAIN", DAY_1, at(DAY_1, 9, 5))
        result, ledger = self.run_case(
            (input_item,),
            (self.observation("request-1", at(DAY_1, 9, 6), Decimal("100"), "SYNTH_MAIN"),),
            (OrderSpecification("request-1", Decimal("1")),),
            dataset=DatasetClass.FINAL_UNSEEN,
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.contract_resolutions, ())
        self.assertEqual([record.event_type for record in ledger.records], ["DATASET_ACCESS_DENIED"])


if __name__ == "__main__":
    unittest.main()

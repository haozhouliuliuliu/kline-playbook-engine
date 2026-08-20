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
from src.research_firewall import TEST_ONLY_SYNTHETIC_DATA_VERSION
from src.strategy_evidence import DatasetClass, EvidenceLedger
from src.validation_runner import (
    CapitalMarginAssumptions,
    CapitalSnapshot,
    ChronologyError,
    ChronologicalValidationRunner,
    ExecutionAssumptions,
    ExecutionObservation,
    ExecutionOutcome,
    FillStatus,
    MarkObservation,
    OrderSpecification,
    ValidationDisposition,
    ValidationMode,
)
from tests.synthetic_fixture import (
    build_synthetic_firewall,
    make_experiment,
    make_strategy,
    make_validation_input,
)


CN = ZoneInfo("Asia/Shanghai")
DAY_1 = date(2024, 6, 17)
DAY_2 = date(2024, 6, 18)
DAY_3 = date(2024, 6, 19)


def at(day, hour, minute):
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=CN)


def make_input(request_id, symbol, trading_day, decision_at, data_version=TEST_ONLY_SYNTHETIC_DATA_VERSION):
    return make_validation_input(
        request_id,
        CompletedBar(
            symbol,
            trading_day,
            decision_at - timedelta(minutes=5),
            decision_at,
            decision_at,
        ),
        decision_at,
        data_version=data_version,
    )


class ContractExecutionSemanticsTests(unittest.TestCase):
    def setUp(self):
        self.strategy = make_strategy(
            research_lineage_id="contract-lifecycle-lineage-fixture",
            family_id="neutral-contract-lifecycle-family",
            source="deterministic-synthetic-contract-fixture",
            applicable_instruments=("A", "B", "SYNTH_MAIN"),
            data_exposure_history_reference="contract-exposure-fixture-v1",
        )
        self.experiment = make_experiment(
            self.strategy,
            dataset_exposure_reference="contract-exposure-fixture-v1",
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
        dataset=DatasetClass.DEVELOPMENT,
        mark_observations=(),
        forced_liquidation_observations=(),
        capital_snapshot=None,
    ):
        ledger = EvidenceLedger()
        firewall, hypothesis_test_id = build_synthetic_firewall(
            ledger, self.strategy, self.experiment
        )
        runner = ChronologicalValidationRunner(ledger, firewall)
        result = runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            dataset_class=dataset,
            inputs=inputs,
            disposition=ValidationDisposition.CONFIRMED,
            hypothesis_test_id=hypothesis_test_id,
            execution_observations=observations,
            execution_cutoff_at=inputs[-1].decision_at + timedelta(minutes=30),
            execution_assumptions=self.execution_assumptions,
            order_specifications=specifications,
            capital_snapshot=capital_snapshot if capital_snapshot is not None else CapitalSnapshot(Decimal("100")),
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

    def test_generic_close_across_buckets_fails_closed_and_explicit_bucket_orders_flat(self):
        # E-04: build today_quantity=1 and previous_quantity=1, then a generic
        # CLOSE total=2 cannot be satisfied wholly by either bucket and must
        # fail closed with the explicit error. The upper layer then emits
        # explicit CLOSE_TODAY + CLOSE_PREVIOUS child orders (two independent
        # transitions with their own offset fees) to flatten. The engine never
        # auto-generates the split or a synthetic child order.
        opening_inputs = (
            make_input("open-day1", "A", DAY_1, at(DAY_1, 9, 5)),
            make_input("open-day2", "A", DAY_2, at(DAY_1, 21, 5)),
        )
        opening_observations = (
            self.observation("open-day1", at(DAY_1, 9, 6), Decimal("100"), "A"),
            self.observation("open-day2", at(DAY_1, 21, 6), Decimal("100"), "A"),
        )
        opening_specifications = (
            OrderSpecification("open-day1", Decimal("1")),
            OrderSpecification("open-day2", Decimal("1")),
        )
        opening, _ = self.run_case(opening_inputs, opening_observations, opening_specifications)
        position = opening.final_capital_snapshot
        self.assertEqual(position.today_quantity, Decimal("1"))
        self.assertEqual(position.previous_quantity, Decimal("1"))

        generic_outcome = ExecutionOutcome(
            "generic-close",
            FillStatus.FILLED,
            at(DAY_1, 22, 6),
            self.execution_assumptions.identity_id,
            Decimal("101"),
            Decimal("0.25"),
            "FILLED",
        )
        generic_spec = OrderSpecification("generic-close", Decimal("2"), OrderAction.CLOSE, CloseOffset.CLOSE)
        generic_input = make_input("generic-close", "A", DAY_2, at(DAY_1, 22, 5))
        with self.assertRaisesRegex(ValueError, "GENERIC_CLOSE_REQUIRES_EXPLICIT_BUCKET_CHILD_ORDERS"):
            ChronologicalValidationRunner._apply_capital_constraints(
                (generic_outcome,),
                (generic_spec,),
                (generic_input,),
                position,
                self.capital_assumptions,
                self.execution_assumptions,
                offset_cost_assumptions=self.offset_costs,
            )

        # Two explicit bucket child orders, each a separate transition.
        explicit_specs = (
            OrderSpecification("close-today", Decimal("1"), OrderAction.CLOSE, CloseOffset.CLOSE_TODAY),
            OrderSpecification("close-previous", Decimal("1"), OrderAction.CLOSE, CloseOffset.CLOSE_PREVIOUS),
        )
        explicit_inputs = (
            make_input("close-today", "A", DAY_2, at(DAY_1, 22, 5)),
            make_input("close-previous", "A", DAY_2, at(DAY_1, 22, 10)),
        )
        explicit_outcomes = (
            ExecutionOutcome(
                "close-today",
                FillStatus.FILLED,
                at(DAY_1, 22, 6),
                self.execution_assumptions.identity_id,
                Decimal("101"),
                Decimal("0.25"),
                "FILLED",
            ),
            ExecutionOutcome(
                "close-previous",
                FillStatus.FILLED,
                at(DAY_1, 22, 11),
                self.execution_assumptions.identity_id,
                Decimal("101"),
                Decimal("0.25"),
                "FILLED",
            ),
        )
        _, transitions = ChronologicalValidationRunner._apply_capital_constraints(
            explicit_outcomes,
            explicit_specs,
            explicit_inputs,
            position,
            self.capital_assumptions,
            self.execution_assumptions,
            offset_cost_assumptions=self.offset_costs,
        )
        self.assertEqual(len(transitions), 2)
        self.assertEqual(transitions[0].resolved_close_offset, CloseOffset.CLOSE_TODAY)
        self.assertEqual(transitions[1].resolved_close_offset, CloseOffset.CLOSE_PREVIOUS)
        final = transitions[1].after
        self.assertEqual(final.position_quantity, Decimal("0"))
        self.assertEqual(final.today_quantity, Decimal("0"))
        self.assertEqual(final.previous_quantity, Decimal("0"))
        # Both explicit closes use the same fill price/base cost, so the
        # offset-fee difference (close_previous 2 vs close_today 1) is exactly 1.
        self.assertEqual(transitions[1].required_cost - transitions[0].required_cost, Decimal("1"))
        # charged_costs accumulates both explicit closes' costs.
        self.assertEqual(
            final.charged_costs,
            position.charged_costs + transitions[0].required_cost + transitions[1].required_cost,
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


class ForcedLiquidationCrossDayOffsetRepairTests(unittest.TestCase):
    """E-02 / E-03: forced liquidation may cross to the next official trading
    day (with ordinary bucket aging) and must resolve close-today/close-previous
    offset fees against the effective buckets with a fail-closed identity check."""

    DAY_1 = date(2024, 6, 17)
    DAY_2 = date(2024, 6, 18)
    DAY_3 = date(2024, 6, 19)

    def setUp(self):
        self.strategy = make_strategy(
            research_lineage_id="package-e-contract-lineage-fixture",
            family_id="neutral-package-e-contract-family",
            source="deterministic-synthetic-contract-fixture",
            applicable_instruments=("A",),
            data_exposure_history_reference="package-e-contract-exposure-fixture-v1",
        )
        self.experiment = make_experiment(
            self.strategy,
            dataset_exposure_reference="package-e-contract-exposure-fixture-v1",
        )
        self.execution_assumptions = ExecutionAssumptions(
            "package-e-contract-execution-v1", Decimal("0"), Decimal("0.25")
        )
        self.capital_assumptions = CapitalMarginAssumptions(
            "package-e-contract-capital-v1", Decimal("1"), Decimal("0.1"), "SYNTH", Decimal("0.05")
        )
        self.offset_costs = OffsetCostAssumptions(
            "package-e-offset-v1", Decimal("1"), Decimal("2")
        )
        self.contract_a = ContractSpecification(
            exchange="SYNTH_EX",
            product_family="SYNTH_PRODUCT",
            instrument_id="A",
            listed_at=at(self.DAY_1, 8, 0),
            deactivated_at=at(self.DAY_3, 0, 0),
            contract_multiplier=Decimal("1"),
            minimum_price_tick=Decimal("0.5"),
            currency="SYNTH",
            unit="SYNTH_UNIT",
            price_limit_rule_identity="synthetic-limit-rule-v1",
            offset_fee_metadata_identity=self.offset_costs.identity_id,
            metadata_version="synthetic-contract-metadata-v1",
        )
        self.master = ContractMaster("synthetic-master-v1", (self.contract_a,))
        self.mapping_a = ContractMappingEntry(
            "SYNTH_MAIN",
            "A",
            at(self.DAY_1, 8, 0),
            at(self.DAY_3, 0, 0),
            at(self.DAY_1, 8, 0),
            "synthetic-roll-v1",
        )
        self.schedule = ContractMappingSchedule(
            "synthetic-schedule-v1", ("SYNTH_MAIN",), (self.mapping_a,)
        )
        self.sessions = SessionMetadata(
            "synthetic-contract-sessions-v1",
            (
                SessionWindow("SYNTH_EX", "A", self.DAY_1, at(self.DAY_1, 9, 0), at(self.DAY_1, 11, 0), "DAY"),
                SessionWindow("SYNTH_EX", "A", self.DAY_2, at(self.DAY_1, 21, 0), at(self.DAY_1, 23, 0), "NIGHT"),
            ),
        )
        self.limit_facts = (
            PriceLimitFact(
                "limit-A-d1", "A", self.contract_a.identity_id, self.DAY_1,
                Decimal("30"), Decimal("120"), at(self.DAY_1, 8, 50), at(self.DAY_1, 8, 50),
                "synthetic-limit-rule-v1", False,
            ),
            PriceLimitFact(
                "limit-A-d2", "A", self.contract_a.identity_id, self.DAY_2,
                Decimal("30"), Decimal("120"), at(self.DAY_1, 20, 50), at(self.DAY_1, 20, 50),
                "synthetic-limit-rule-v1", False,
            ),
        )

    def observation(self, request_id, timestamp, price, contract="A"):
        return ExecutionObservation(
            request_id, timestamp, timestamp, Decimal(price), concrete_contract_id=contract
        )

    def run_case(
        self,
        inputs,
        observations,
        specifications,
        *,
        mark=None,
        liquidation_observations=(),
        cutoff=None,
        starting_capital=Decimal("20"),
        offset_costs=None,
    ):
        ledger = EvidenceLedger()
        firewall, hypothesis_test_id = build_synthetic_firewall(
            ledger, self.strategy, self.experiment
        )
        runner = ChronologicalValidationRunner(ledger, firewall)
        result = runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            dataset_class=DatasetClass.DEVELOPMENT,
            inputs=inputs,
            disposition=ValidationDisposition.CONFIRMED,
            hypothesis_test_id=hypothesis_test_id,
            execution_observations=observations,
            execution_cutoff_at=(
                cutoff if cutoff is not None else inputs[-1].decision_at + timedelta(minutes=30)
            ),
            execution_assumptions=self.execution_assumptions,
            order_specifications=specifications,
            capital_snapshot=CapitalSnapshot(starting_capital),
            capital_margin_assumptions=self.capital_assumptions,
            contract_master=self.master,
            contract_mapping_schedule=self.schedule,
            session_metadata=self.sessions,
            price_limit_facts=self.limit_facts,
            offset_cost_assumptions=self.offset_costs if offset_costs is None else offset_costs,
            mark_observations=() if mark is None else (mark,),
            forced_liquidation_observations=tuple(liquidation_observations),
        )
        return result

    def open_breach_liquidation(self, *, liquidation_at, starting_capital=Decimal("20"), offset_costs=None):
        """Run OPEN -> breach mark -> forced liquidation and return the result."""
        opening_input = make_input("open-1", "A", self.DAY_1, at(self.DAY_1, 9, 5))
        opening_observation = self.observation("open-1", at(self.DAY_1, 9, 6), "100")
        opening_spec = OrderSpecification("open-1", Decimal("1"))
        opened = self.run_case(
            (opening_input,),
            (opening_observation,),
            (opening_spec,),
            starting_capital=starting_capital,
            offset_costs=offset_costs,
        )
        snapshot = opened.final_capital_snapshot
        mark = MarkObservation(
            "breach-mark",
            snapshot.position_id,
            snapshot.position_request_id,
            "A",
            at(self.DAY_1, 10, 50),
            at(self.DAY_1, 10, 50),
            Decimal("40"),
        )
        breached = self.run_case(
            (opening_input,),
            (opening_observation,),
            (opening_spec,),
            mark=mark,
            cutoff=at(self.DAY_1, 21, 30),
            starting_capital=starting_capital,
            offset_costs=offset_costs,
        )
        requirement = breached.liquidation_requirement
        self.assertIsNotNone(requirement)
        observation = self.observation(requirement.request_id, liquidation_at, "39")
        return self.run_case(
            (opening_input,),
            (opening_observation,),
            (opening_spec,),
            mark=mark,
            liquidation_observations=(observation,),
            cutoff=liquidation_at + timedelta(minutes=30),
            starting_capital=starting_capital,
            offset_costs=offset_costs,
        )

    def test_today_only_forced_liquidation_resolves_close_today_fee(self):
        # Breach and liquidation both on DAY_1: today=1, previous=0.
        result = self.open_breach_liquidation(liquidation_at=at(self.DAY_1, 10, 55))
        outcome = result.liquidation_outcome.execution_outcome
        transition = result.liquidation_outcome.capital_transition
        self.assertEqual(outcome.status, FillStatus.FILLED)
        self.assertEqual(outcome.total_cost, Decimal("1.25"))  # 0.25 fee + 1.00 close-today
        self.assertEqual(outcome.resolved_close_offset, CloseOffset.CLOSE_TODAY)
        self.assertEqual(outcome.offset_cost_assumption_id, self.offset_costs.identity_id)
        self.assertEqual(transition.required_cost, Decimal("1.25"))
        self.assertEqual(transition.resolved_close_offset, CloseOffset.CLOSE_TODAY)
        self.assertEqual(transition.aged_quantity, Decimal("0"))

    def test_d1_to_d2_aging_forced_liquidation_resolves_close_previous_fee(self):
        # Breach at DAY_1 session tail; liquidation on DAY_2 night (official
        # DAY_2).  The today bucket ages to previous, so the whole position is
        # closed as CLOSE_PREVIOUS with the close-previous fee.
        result = self.open_breach_liquidation(liquidation_at=at(self.DAY_1, 21, 5))
        outcome = result.liquidation_outcome.execution_outcome
        transition = result.liquidation_outcome.capital_transition
        self.assertEqual(outcome.status, FillStatus.FILLED)
        self.assertEqual(outcome.total_cost, Decimal("2.25"))  # 0.25 fee + 2.00 close-previous
        self.assertEqual(outcome.resolved_close_offset, CloseOffset.CLOSE_PREVIOUS)
        self.assertEqual(outcome.offset_cost_assumption_id, self.offset_costs.identity_id)
        self.assertEqual(transition.required_cost, Decimal("2.25"))
        self.assertEqual(transition.resolved_close_offset, CloseOffset.CLOSE_PREVIOUS)
        # E-02: the full DAY_1 today bucket aged to previous exactly once.
        self.assertEqual(transition.aged_quantity, Decimal("1"))
        self.assertEqual(result.final_capital_snapshot.charged_costs, Decimal("2.50"))

    def test_mixed_bucket_forced_liquidation_resolves_full_close_fee(self):
        # OPEN 1 @100 on DAY_1 (today=1), ADD 1 @102 on DAY_2 night (today->1
        # previous, then +1 today), then breach and full liquidation on DAY_2.
        # Effective today=1, previous=1 -> CLOSE with close-today + close-previous.
        opening_input = make_input("open-1", "A", self.DAY_1, at(self.DAY_1, 9, 5))
        opening_observation = self.observation("open-1", at(self.DAY_1, 9, 6), "100")
        opening_spec = OrderSpecification("open-1", Decimal("1"))
        add_input = make_input("add-1", "A", self.DAY_2, at(self.DAY_1, 21, 5))
        add_observation = self.observation("add-1", at(self.DAY_1, 21, 6), "102")
        add_spec = OrderSpecification("add-1", Decimal("1"))
        inputs = (opening_input, add_input)
        observations = (opening_observation, add_observation)
        specifications = (opening_spec, add_spec)
        dry_run = self.run_case(inputs, observations, specifications, starting_capital=Decimal("100"))
        snapshot = dry_run.final_capital_snapshot
        self.assertEqual(snapshot.today_quantity, Decimal("1"))
        self.assertEqual(snapshot.previous_quantity, Decimal("1"))
        mark = MarkObservation(
            "breach-mark",
            snapshot.position_id,
            snapshot.position_request_id,
            "A",
            at(self.DAY_1, 21, 10),
            at(self.DAY_1, 21, 10),
            Decimal("40"),
        )
        breached = self.run_case(
            inputs, observations, specifications, mark=mark, starting_capital=Decimal("100")
        )
        requirement = breached.liquidation_requirement
        self.assertIsNotNone(requirement)
        observation = self.observation(requirement.request_id, at(self.DAY_1, 21, 12), "39")
        result = self.run_case(
            inputs,
            observations,
            specifications,
            mark=mark,
            liquidation_observations=(observation,),
            cutoff=at(self.DAY_1, 21, 30),
            starting_capital=Decimal("100"),
        )
        outcome = result.liquidation_outcome.execution_outcome
        transition = result.liquidation_outcome.capital_transition
        self.assertEqual(outcome.status, FillStatus.FILLED)
        self.assertEqual(outcome.total_cost, Decimal("3.25"))  # 0.25 + 1*1 + 1*2
        self.assertEqual(outcome.resolved_close_offset, CloseOffset.CLOSE)
        self.assertEqual(transition.required_cost, Decimal("3.25"))
        self.assertEqual(transition.resolved_close_offset, CloseOffset.CLOSE)
        # No further aging: the liquidation observation is on the position day.
        self.assertEqual(transition.aged_quantity, Decimal("0"))
        # OPEN 0.25 + ADD 0.25 + liquidation 3.25 charged exactly once.
        self.assertEqual(result.final_capital_snapshot.charged_costs, Decimal("3.75"))

    def test_forced_liquidation_offset_assumption_mismatch_fails_closed(self):
        mismatched = OffsetCostAssumptions("package-e-offset-mismatch-v1", Decimal("9"), Decimal("9"))
        self.assertNotEqual(mismatched.identity_id, self.offset_costs.identity_id)
        with self.assertRaisesRegex(ValueError, "offset-cost assumption identity is inconsistent"):
            self.open_breach_liquidation(
                liquidation_at=at(self.DAY_1, 10, 55),
                offset_costs=mismatched,
            )


if __name__ == "__main__":
    unittest.main()

import unittest
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.data_substrate import CompletedBar
from src.contract_semantics import PositionDirection
from src.strategy_evidence import DatasetClass, EvidenceLedger
from src.validation_runner import (
    CapitalMarginAssumptions,
    CapitalSnapshot,
    ChronologicalValidationRunner,
    ExecutionAssumptions,
    ExecutionObservation,
    ExecutionOutcome,
    FillStatus,
    OrderSpecification,
    ValidationDisposition,
    ValidationMode,
)
from tests.synthetic_fixture import (
    DEVELOPMENT_DAY,
    build_synthetic_firewall,
    make_experiment,
    make_strategy,
    make_validation_input,
)


CN = ZoneInfo("Asia/Shanghai")
DAY = DEVELOPMENT_DAY


def at(hour, minute):
    return datetime(DAY.year, DAY.month, DAY.day, hour, minute, tzinfo=CN)


class CapitalMarginConstraintTests(unittest.TestCase):
    def setUp(self):
        self.strategy = make_strategy(
            research_lineage_id="capital-lineage-fixture",
            family_id="neutral-capital-family",
        )
        self.experiment = make_experiment(self.strategy)
        self.execution_assumptions = ExecutionAssumptions("synthetic-v1", Decimal("1.5"), Decimal("0.25"))
        self.capital_assumptions = CapitalMarginAssumptions("capital-v1", Decimal("1"), Decimal("0.1"), "SYNTH")
        self.input = make_validation_input(
            "request-1",
            CompletedBar("TEST", DAY, at(9, 0), at(9, 5), at(9, 5)),
            at(9, 5),
            data_version=self.experiment.data_version,
        )

    def runner(self):
        ledger = EvidenceLedger()
        firewall, hypothesis_test_id = build_synthetic_firewall(ledger, self.strategy, self.experiment)
        return ChronologicalValidationRunner(ledger, firewall), ledger, hypothesis_test_id

    def confirm(self, snapshot, inputs=None, observations=None, specifications=None, dataset=DatasetClass.DEVELOPMENT):
        runner, ledger, hypothesis_test_id = self.runner()
        inputs = inputs or (self.input,)
        observations = observations if observations is not None else (ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100")),)
        specifications = specifications or tuple(OrderSpecification(item.request_id, Decimal("1")) for item in inputs)
        result = runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            dataset_class=dataset,
            inputs=inputs,
            disposition=ValidationDisposition.CONFIRMED,
            hypothesis_test_id=hypothesis_test_id,
            execution_observations=observations,
            execution_cutoff_at=at(9, 15),
            execution_assumptions=self.execution_assumptions,
            order_specifications=specifications,
            capital_snapshot=snapshot,
            capital_margin_assumptions=self.capital_assumptions,
        )
        return result, ledger

    def test_sufficient_capital_fills_and_reserves_margin_with_cost(self):
        result, _ = self.confirm(CapitalSnapshot(Decimal("100")))
        outcome, transition = result.execution_outcomes[0], result.capital_transitions[0]
        self.assertEqual(outcome.status, FillStatus.FILLED)
        self.assertEqual(transition.required_margin, Decimal("10.15"))
        self.assertEqual(transition.after.reserved_margin, Decimal("10.15"))
        self.assertEqual(transition.after.charged_costs, Decimal("0.25"))
        self.assertEqual(transition.after.available_capital, Decimal("89.60"))

    def test_insufficient_margin_is_not_filled_and_does_not_mutate_capital(self):
        snapshot = CapitalSnapshot(Decimal("10.39"))
        result, ledger = self.confirm(snapshot)
        outcome, transition = result.execution_outcomes[0], result.capital_transitions[0]
        self.assertEqual(outcome.status, FillStatus.NOT_FILLED)
        self.assertEqual(outcome.reason, "INSUFFICIENT_MARGIN")
        self.assertEqual(transition.before, snapshot)
        self.assertEqual(transition.after, snapshot)
        self.assertEqual(ledger.records[-2].event_type, "EXECUTION_NOT_FILLED")

    def test_sequential_fills_use_prior_capital_snapshot(self):
        second_bar = CompletedBar("TEST", DAY, at(9, 5), at(9, 10), at(9, 10))
        second_input = make_validation_input(
            "request-2", second_bar, at(9, 10), data_version=self.experiment.data_version
        )
        inputs = (self.input, second_input)
        observations = (
            ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100")),
            ExecutionObservation("request-2", at(9, 11), at(9, 11), Decimal("100")),
        )
        result, _ = self.confirm(CapitalSnapshot(Decimal("20.50")), inputs=inputs, observations=observations)
        self.assertEqual([outcome.status for outcome in result.execution_outcomes], [FillStatus.FILLED, FillStatus.NOT_FILLED])
        self.assertEqual(result.execution_outcomes[1].reason, "INSUFFICIENT_MARGIN")
        self.assertEqual(result.capital_transitions[1].before, result.capital_transitions[0].after)
        self.assertEqual(result.capital_transitions[1].after, result.capital_transitions[1].before)

    def test_invalid_order_and_capital_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            OrderSpecification("request-1", Decimal("0"))
        with self.assertRaises(ValueError):
            OrderSpecification("request-1", Decimal("-1"))
        with self.assertRaises(ValueError):
            CapitalMarginAssumptions("x", Decimal("0"), Decimal("0.1"), "SYNTH")
        with self.assertRaises(ValueError):
            CapitalMarginAssumptions("x", Decimal("1"), Decimal("0"), "SYNTH")
        with self.assertRaises(ValueError):
            CapitalSnapshot(Decimal("-1"))

    def test_capital_assumption_identity_and_evidence_binding_are_deterministic(self):
        same = CapitalMarginAssumptions("capital-v1", Decimal("1"), Decimal("0.1"), "SYNTH")
        changed = CapitalMarginAssumptions("capital-v1", Decimal("2"), Decimal("0.1"), "SYNTH")
        self.assertEqual(self.capital_assumptions.identity_id, same.identity_id)
        self.assertNotEqual(self.capital_assumptions.identity_id, changed.identity_id)
        first, first_ledger = self.confirm(CapitalSnapshot(Decimal("100")))
        second, second_ledger = self.confirm(CapitalSnapshot(Decimal("100")))
        self.assertEqual(first.execution_outcomes, second.execution_outcomes)
        self.assertEqual(first.validation_record.record_id, second.validation_record.record_id)
        reference = f"execution:{self.execution_assumptions.identity_id};capital:{self.capital_assumptions.identity_id}"
        self.assertEqual(first.validation_record.evidence_reference, reference)
        self.assertEqual(first_ledger.records[-2].experiment, self.experiment)
        self.assertEqual(second_ledger.records[-2].evidence_reference, reference)

    def test_final_unseen_is_denied_before_capital_evaluation(self):
        result, ledger = self.confirm(CapitalSnapshot(Decimal("100")), dataset=DatasetClass.FINAL_UNSEEN)
        self.assertFalse(result.allowed)
        self.assertEqual(result.execution_outcomes, ())
        self.assertEqual(result.capital_transitions, ())
        self.assertEqual(ledger.records[0].event_type, "DATASET_ACCESS_DENIED")

    def _open_snapshot(self, starting_capital, unrealized_pnl, position_id):
        return CapitalSnapshot(
            starting_capital=starting_capital,
            unrealized_pnl=unrealized_pnl,
            position_quantity=Decimal("1"),
            average_open_price=Decimal("90"),
            position_instrument="TEST",
            position_id=position_id,
            position_request_id=f"req-{position_id}",
            execution_assumption_id=self.execution_assumptions.identity_id,
            capital_assumption_id=self.capital_assumptions.identity_id,
            state_at=at(9, 0),
            today_quantity=Decimal("1"),
            previous_quantity=Decimal("0"),
            position_direction=PositionDirection.LONG,
        )

    def apply_admission(self, snapshot):
        # Exercise the open/add admission decision in
        # _apply_capital_constraints directly against an already-open
        # position snapshot (the offline runner requires a flat start).
        outcome = ExecutionOutcome(
            "request-1",
            FillStatus.FILLED,
            at(9, 6),
            self.execution_assumptions.identity_id,
            Decimal("100"),
            Decimal("0.25"),
            "FILLED",
        )
        specification = OrderSpecification("request-1", Decimal("1"))
        item = make_validation_input(
            "request-1",
            CompletedBar("TEST", DAY, at(9, 0), at(9, 5), at(9, 5)),
            at(9, 5),
            data_version=self.experiment.data_version,
        )
        constrained, transitions = ChronologicalValidationRunner._apply_capital_constraints(
            (outcome,),
            (specification,),
            (item,),
            snapshot,
            self.capital_assumptions,
            self.execution_assumptions,
        )
        return constrained[0], transitions[0]

    def test_e08_positive_unrealized_pnl_cannot_finance_new_admission(self):
        # E-08 case A: cash-based available_capital is insufficient while
        # available_resources (equity-based) is sufficient because of a large
        # positive unrealized PnL. Admission must still fail on
        # available_capital; floating profit cannot finance a new position.
        snapshot = self._open_snapshot(Decimal("5"), Decimal("1000"), "pos-a")
        required = Decimal("10.25")
        self.assertLess(snapshot.available_capital, required)
        self.assertGreaterEqual(snapshot.available_resources, required)
        outcome, transition = self.apply_admission(snapshot)
        self.assertEqual(outcome.status, FillStatus.NOT_FILLED)
        self.assertEqual(outcome.reason, "INSUFFICIENT_MARGIN")
        self.assertEqual(transition.after, snapshot)

    def test_e08_negative_unrealized_pnl_does_not_reduce_admission_capacity(self):
        # E-08 case B: available_capital is sufficient even though
        # available_resources is insufficient due to a large negative
        # unrealized PnL. Open/add admission is still decided by
        # available_capital (frozen semantic); it is not silently switched to
        # an equity model.
        snapshot = self._open_snapshot(Decimal("100"), Decimal("-1000"), "pos-b")
        required = Decimal("10.25")
        self.assertGreaterEqual(snapshot.available_capital, required)
        self.assertLess(snapshot.available_resources, required)
        outcome, _ = self.apply_admission(snapshot)
        self.assertEqual(outcome.status, FillStatus.FILLED)

    def test_e08_margin_admission_resource_binds_available_capital_only(self):
        # E-08 case C: CapitalMarginAssumptions identity is bound to
        # AVAILABLE_CAPITAL_ONLY; no other runtime admission-resource option is
        # supported, and the field participates in the identity.
        self.assertEqual(self.capital_assumptions.margin_admission_resource, "AVAILABLE_CAPITAL_ONLY")
        same = CapitalMarginAssumptions("capital-v1", Decimal("1"), Decimal("0.1"), "SYNTH")
        self.assertEqual(self.capital_assumptions.identity_id, same.identity_id)
        with self.assertRaisesRegex(ValueError, "unsupported margin admission resource"):
            CapitalMarginAssumptions(
                "capital-v1",
                Decimal("1"),
                Decimal("0.1"),
                "SYNTH",
                margin_admission_resource="EQUITY",
            )
        # Prove the field is part of identity: a raw object carrying a
        # different resource hashes differently even though no valid
        # constructor allows it (frozen single-value semantic).
        raw = object.__new__(CapitalMarginAssumptions)
        object.__setattr__(raw, "model_version", "capital-v1")
        object.__setattr__(raw, "contract_multiplier", Decimal("1"))
        object.__setattr__(raw, "initial_margin_rate", Decimal("0.1"))
        object.__setattr__(raw, "currency", "SYNTH")
        object.__setattr__(raw, "maintenance_margin_rate", Decimal("0.05"))
        object.__setattr__(raw, "breach_rule", "EQUITY_BELOW_MAINTENANCE_REQUIREMENT")
        object.__setattr__(raw, "liquidation_rule_version", "FULL_POSITION_NEXT_TRADABLE_OBSERVATION_V1")
        object.__setattr__(raw, "margin_admission_resource", "EQUITY")
        self.assertNotEqual(raw.identity_id, self.capital_assumptions.identity_id)


if __name__ == "__main__":
    unittest.main()

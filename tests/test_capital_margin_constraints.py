import unittest
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.data_substrate import CompletedBar
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
    ChronologicalValidationRunner,
    ExecutionAssumptions,
    ExecutionObservation,
    FillStatus,
    OrderSpecification,
    ValidationDisposition,
    ValidationInput,
    ValidationMode,
)


CN = ZoneInfo("Asia/Shanghai")
DAY = date(2025, 6, 16)


def at(hour, minute):
    return datetime(DAY.year, DAY.month, DAY.day, hour, minute, tzinfo=CN)


def make_strategy():
    return StrategyIdentity(
        research_lineage_id="capital-lineage-fixture",
        family_id="neutral-capital-family",
        strategy_version="1.0",
        source="deterministic-fixture",
        applicable_instruments=("TEST",),
        timeframe="5m",
        parameters=(TypedParameter("window", "int", 3),),
        code_hash="code-fixture-v1",
        environment_hash="environment-fixture-v1",
        required_feature_versions=("context-fixture-v1",),
        lifecycle_state=LifecycleState.DRAFT,
        data_exposure_history_reference="exposure-fixture-v1",
    )


class CapitalMarginConstraintTests(unittest.TestCase):
    def setUp(self):
        self.strategy = make_strategy()
        self.experiment = ExperimentIdentity.from_strategy(self.strategy, "data-fixture-v1", "exposure-fixture-v1")
        self.execution_assumptions = ExecutionAssumptions("synthetic-v1", Decimal("1.5"), Decimal("0.25"))
        self.capital_assumptions = CapitalMarginAssumptions("capital-v1", Decimal("1"), Decimal("0.1"), "SYNTH")
        self.input = ValidationInput("request-1", CompletedBar("TEST", DAY, at(9, 0), at(9, 5), at(9, 5)), at(9, 5))

    def runner(self):
        ledger = EvidenceLedger()
        return ChronologicalValidationRunner(ledger, FinalUnseenFirewall(ledger)), ledger

    def confirm(self, snapshot, inputs=None, observations=None, specifications=None, dataset=DatasetClass.VALIDATION):
        runner, ledger = self.runner()
        inputs = inputs or (self.input,)
        observations = observations if observations is not None else (ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100")),)
        specifications = specifications or tuple(OrderSpecification(item.request_id, Decimal("1")) for item in inputs)
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
        second_input = ValidationInput("request-2", second_bar, at(9, 10))
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


if __name__ == "__main__":
    unittest.main()

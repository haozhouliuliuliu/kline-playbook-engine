import unittest
from datetime import date, datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.data_substrate import CompletedBar
from src.strategy_evidence import DatasetClass, EvidenceLedger
from src.validation_runner import (
    ChronologicalValidationRunner,
    CapitalMarginAssumptions,
    CapitalSnapshot,
    ChronologyError,
    ExecutionAssumptions,
    ExecutionObservation,
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


class ExecutionRealismTests(unittest.TestCase):
    def setUp(self):
        self.strategy = make_strategy(
            research_lineage_id="execution-lineage-fixture",
            family_id="neutral-execution-family",
        )
        self.experiment = make_experiment(self.strategy)
        self.ledger = EvidenceLedger()
        self.firewall, self.hypothesis_test_id = build_synthetic_firewall(
            self.ledger, self.strategy, self.experiment
        )
        self.runner = ChronologicalValidationRunner(self.ledger, self.firewall)
        self.input = make_validation_input(
            "request-1",
            CompletedBar("TEST", DAY, at(9, 0), at(9, 5), at(9, 5)),
            at(9, 5),
            data_version=self.experiment.data_version,
        )
        self.assumptions = ExecutionAssumptions("synthetic-v1", Decimal("1.5"), Decimal("0.25"))
        self.capital_assumptions = CapitalMarginAssumptions("capital-fixture-v1", Decimal("1"), Decimal("0.1"), "SYNTH")
        self.capital_snapshot = CapitalSnapshot(Decimal("100"))

    def confirm(self, observations=(), cutoff=at(9, 10), assumptions=None):
        return self.runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            artifact_identity_id=self.strategy.identity_id,
            artifact_code_hash=self.strategy.code_hash,
            dataset_class=DatasetClass.DEVELOPMENT,
            inputs=(self.input,),
            disposition=ValidationDisposition.CONFIRMED,
            hypothesis_test_id=self.hypothesis_test_id,
            execution_observations=observations,
            execution_cutoff_at=cutoff,
            execution_assumptions=assumptions or self.assumptions,
            order_specifications=(OrderSpecification("request-1", Decimal("1")),),
            capital_snapshot=self.capital_snapshot,
            capital_margin_assumptions=self.capital_assumptions,
        )

    def test_later_independently_available_observation_fills_after_eligibility(self):
        result = self.confirm((ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100")),))
        outcome = result.execution_outcomes[0]
        self.assertEqual(outcome.status, FillStatus.FILLED)
        self.assertEqual(outcome.fill_price, Decimal("101.5"))
        self.assertEqual(outcome.total_cost, Decimal("0.25"))
        self.assertEqual(result.events[-1].event_type, "FILLED")
        self.assertGreater(outcome.evaluated_at, self.input.decision_at)

    def test_same_decision_lookahead_and_impossible_cutoff_fail_closed(self):
        with self.assertRaisesRegex(ChronologyError, "independently available"):
            self.confirm((ExecutionObservation("request-1", at(9, 5), at(9, 5), Decimal("100")),))
        self.ledger = EvidenceLedger()
        self.firewall, self.hypothesis_test_id = build_synthetic_firewall(
            self.ledger, self.strategy, self.experiment
        )
        self.runner = ChronologicalValidationRunner(self.ledger, self.firewall)
        with self.assertRaisesRegex(ChronologyError, "cutoff cannot precede"):
            self.confirm(cutoff=at(9, 4))

    def test_assumption_identity_and_costs_are_deterministic_and_outcome_affecting(self):
        same = ExecutionAssumptions("synthetic-v1", Decimal("1.5"), Decimal("0.25"))
        changed = ExecutionAssumptions("synthetic-v1", Decimal("2.0"), Decimal("0.25"))
        self.assertEqual(self.assumptions.identity_id, same.identity_id)
        self.assertNotEqual(self.assumptions.identity_id, changed.identity_id)

    def test_no_observation_and_nontradable_observation_are_not_filled(self):
        no_observation = self.confirm()
        self.assertEqual(no_observation.execution_outcomes[0].status, FillStatus.NOT_FILLED)
        self.assertEqual(no_observation.execution_outcomes[0].reason, "NO_OBSERVATION")

        ledger = EvidenceLedger()
        firewall, hypothesis_test_id = build_synthetic_firewall(ledger, self.strategy, self.experiment)
        runner = ChronologicalValidationRunner(ledger, firewall)
        result = runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            artifact_identity_id=self.strategy.identity_id,
            artifact_code_hash=self.strategy.code_hash,
            dataset_class=DatasetClass.DEVELOPMENT,
            inputs=(self.input,),
            disposition=ValidationDisposition.CONFIRMED,
            hypothesis_test_id=hypothesis_test_id,
            execution_observations=(ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100"), tradable=False),),
            execution_cutoff_at=at(9, 10),
            execution_assumptions=self.assumptions,
            order_specifications=(OrderSpecification("request-1", Decimal("1")),),
            capital_snapshot=self.capital_snapshot,
            capital_margin_assumptions=self.capital_assumptions,
        )
        self.assertEqual(result.execution_outcomes[0].status, FillStatus.NOT_FILLED)
        self.assertEqual(result.execution_outcomes[0].reason, "NOT_TRADABLE")

    def test_confirmed_evidence_requires_and_records_execution_assumption_binding(self):
        with self.assertRaisesRegex(ValueError, "requires execution assumptions"):
            self.runner.run(
                mode=ValidationMode.CONFIRMATORY,
                strategy=self.strategy,
                experiment=self.experiment,
                artifact_identity_id=self.strategy.identity_id,
                artifact_code_hash=self.strategy.code_hash,
                dataset_class=DatasetClass.VALIDATION,
                inputs=(self.input,),
                disposition=ValidationDisposition.CONFIRMED,
            )
        result = self.confirm((ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100")),))
        reference = f"execution:{self.assumptions.identity_id};capital:{self.capital_assumptions.identity_id}"
        self.assertEqual(result.validation_record.evidence_reference, reference)
        self.assertEqual(self.ledger.records[-2].evidence_reference, reference)

    def test_identical_confirmatory_runs_have_identical_execution_evidence(self):
        observation = (ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100")),)
        first = self.confirm(observation)
        second_ledger = EvidenceLedger()
        second_firewall, second_hypothesis = build_synthetic_firewall(
            second_ledger, self.strategy, self.experiment
        )
        second_runner = ChronologicalValidationRunner(second_ledger, second_firewall)
        second = second_runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            artifact_identity_id=self.strategy.identity_id,
            artifact_code_hash=self.strategy.code_hash,
            dataset_class=DatasetClass.DEVELOPMENT,
            inputs=(self.input,),
            disposition=ValidationDisposition.CONFIRMED,
            hypothesis_test_id=second_hypothesis,
            execution_observations=observation,
            execution_cutoff_at=at(9, 10),
            execution_assumptions=self.assumptions,
            order_specifications=(OrderSpecification("request-1", Decimal("1")),),
            capital_snapshot=self.capital_snapshot,
            capital_margin_assumptions=self.capital_assumptions,
        )
        self.assertEqual(first.execution_outcomes, second.execution_outcomes)
        self.assertEqual(first.validation_record.record_id, second.validation_record.record_id)


if __name__ == "__main__":
    unittest.main()

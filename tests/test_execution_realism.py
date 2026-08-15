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
    ChronologicalValidationRunner,
    ChronologyError,
    ExecutionAssumptions,
    ExecutionObservation,
    FillStatus,
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
        research_lineage_id="execution-lineage-fixture",
        family_id="neutral-execution-family",
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


class ExecutionRealismTests(unittest.TestCase):
    def setUp(self):
        self.strategy = make_strategy()
        self.experiment = ExperimentIdentity.from_strategy(self.strategy, "data-fixture-v1", "exposure-fixture-v1")
        self.ledger = EvidenceLedger()
        self.runner = ChronologicalValidationRunner(self.ledger, FinalUnseenFirewall(self.ledger))
        self.input = ValidationInput("request-1", CompletedBar("TEST", DAY, at(9, 0), at(9, 5), at(9, 5)), at(9, 5))
        self.assumptions = ExecutionAssumptions("synthetic-v1", Decimal("1.5"), Decimal("0.25"))

    def confirm(self, observations=(), cutoff=at(9, 10), assumptions=None):
        return self.runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            artifact_identity_id=self.strategy.identity_id,
            artifact_code_hash=self.strategy.code_hash,
            dataset_class=DatasetClass.VALIDATION,
            inputs=(self.input,),
            disposition=ValidationDisposition.CONFIRMED,
            execution_observations=observations,
            execution_cutoff_at=cutoff,
            execution_assumptions=assumptions or self.assumptions,
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
        self.runner = ChronologicalValidationRunner(self.ledger, FinalUnseenFirewall(self.ledger))
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
        runner = ChronologicalValidationRunner(ledger, FinalUnseenFirewall(ledger))
        result = runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            artifact_identity_id=self.strategy.identity_id,
            artifact_code_hash=self.strategy.code_hash,
            dataset_class=DatasetClass.VALIDATION,
            inputs=(self.input,),
            disposition=ValidationDisposition.CONFIRMED,
            execution_observations=(ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100"), tradable=False),),
            execution_cutoff_at=at(9, 10),
            execution_assumptions=self.assumptions,
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
        self.assertEqual(result.validation_record.evidence_reference, self.assumptions.identity_id)
        self.assertEqual(self.ledger.records[-2].evidence_reference, self.assumptions.identity_id)

    def test_identical_confirmatory_runs_have_identical_execution_evidence(self):
        observation = (ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100")),)
        first = self.confirm(observation)
        second_ledger = EvidenceLedger()
        second_runner = ChronologicalValidationRunner(second_ledger, FinalUnseenFirewall(second_ledger))
        second = second_runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            artifact_identity_id=self.strategy.identity_id,
            artifact_code_hash=self.strategy.code_hash,
            dataset_class=DatasetClass.VALIDATION,
            inputs=(self.input,),
            disposition=ValidationDisposition.CONFIRMED,
            execution_observations=observation,
            execution_cutoff_at=at(9, 10),
            execution_assumptions=self.assumptions,
        )
        self.assertEqual(first.execution_outcomes, second.execution_outcomes)
        self.assertEqual(first.validation_record.record_id, second.validation_record.record_id)


if __name__ == "__main__":
    unittest.main()

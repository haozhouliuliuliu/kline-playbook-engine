import unittest
from decimal import Decimal
from datetime import date, datetime
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
    CapitalMarginAssumptions,
    CapitalSnapshot,
    ChronologyError,
    ExecutionAssumptions,
    ExecutionObservation,
    OrderSpecification,
    ValidationDisposition,
    ValidationInput,
    ValidationMode,
)


CN = ZoneInfo("Asia/Shanghai")
DAY = date(2025, 6, 16)


def at(hour, minute):
    return datetime(DAY.year, DAY.month, DAY.day, hour, minute, tzinfo=CN)


def strategy():
    return StrategyIdentity(
        research_lineage_id="validation-lineage-fixture",
        family_id="neutral-validation-family",
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


class ValidationRunnerTests(unittest.TestCase):
    def setUp(self):
        self.strategy = strategy()
        self.experiment = ExperimentIdentity.from_strategy(self.strategy, "data-fixture-v1", "exposure-fixture-v1")
        self.ledger = EvidenceLedger()
        self.runner = ChronologicalValidationRunner(self.ledger, FinalUnseenFirewall(self.ledger))
        self.bar = CompletedBar("TEST", DAY, at(9, 0), at(9, 5), at(9, 5))
        self.assumptions = ExecutionAssumptions("synthetic-v1", Decimal("1.5"), Decimal("0.25"))
        self.capital_assumptions = CapitalMarginAssumptions("capital-fixture-v1", Decimal("1"), Decimal("0.1"), "SYNTH")
        self.capital_snapshot = CapitalSnapshot(Decimal("100"))

    def execute(self, mode=ValidationMode.CONFIRMATORY, dataset=DatasetClass.VALIDATION, inputs=None, disposition=None, observations=(), cutoff=None, assumptions=None, specifications=(), capital_snapshot=None, capital_assumptions=None):
        return self.runner.run(
            mode=mode,
            strategy=self.strategy,
            experiment=self.experiment,
            artifact_identity_id=self.strategy.identity_id,
            artifact_code_hash=self.strategy.code_hash,
            dataset_class=dataset,
            inputs=inputs or (ValidationInput("request-1", self.bar, at(9, 5)),),
            disposition=disposition,
            execution_observations=observations,
            execution_cutoff_at=cutoff,
            execution_assumptions=assumptions,
            order_specifications=specifications,
            capital_snapshot=capital_snapshot,
            capital_margin_assumptions=capital_assumptions,
        )

    def test_runner_reuses_existing_completed_bar_availability(self):
        with self.assertRaisesRegex(ChronologyError, "unavailable"):
            self.execute(inputs=(ValidationInput("request-1", self.bar, at(9, 4)),))

    def test_visible_input_intent_order_fill_chain_has_explicit_equal_timestamp_order(self):
        result = self.execute()
        self.assertEqual(
            [event.event_type for event in result.events],
            ["VISIBLE_MARKET_INPUT", "STRATEGY_INTENT", "ORDER_CREATED", "FILL_ELIGIBLE"],
        )
        self.assertTrue(all(event.timestamp == at(9, 5) for event in result.events))

    def test_impossible_input_order_fails_closed_instead_of_reordering(self):
        later = CompletedBar("TEST", DAY, at(9, 5), at(9, 10), at(9, 10))
        with self.assertRaisesRegex(ChronologyError, "strictly chronological"):
            self.execute(inputs=(ValidationInput("request-2", later, at(9, 10)), ValidationInput("request-1", self.bar, at(9, 5))))

    def test_identical_replays_are_deterministic(self):
        first = self.execute()
        second_ledger = EvidenceLedger()
        second_runner = ChronologicalValidationRunner(second_ledger, FinalUnseenFirewall(second_ledger))
        second = second_runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            artifact_identity_id=self.strategy.identity_id,
            artifact_code_hash=self.strategy.code_hash,
            dataset_class=DatasetClass.VALIDATION,
            inputs=(ValidationInput("request-1", self.bar, at(9, 5)),),
        )
        self.assertEqual(first.events, second.events)
        self.assertEqual(first.access_record.record_id, second.access_record.record_id)

    def test_artifact_identity_or_code_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.runner.run(
                mode=ValidationMode.FAST,
                strategy=self.strategy,
                experiment=self.experiment,
                artifact_identity_id="other-artifact",
                artifact_code_hash=self.strategy.code_hash,
                dataset_class=DatasetClass.DEVELOPMENT,
                inputs=(),
            )

    def test_fast_can_reject_but_cannot_confirm(self):
        rejected = self.execute(mode=ValidationMode.FAST, dataset=DatasetClass.DEVELOPMENT, disposition=ValidationDisposition.REJECTED)
        self.assertEqual(rejected.validation_record.event_type, "VALIDATION_REJECTED")
        with self.assertRaisesRegex(ValueError, "cannot establish"):
            self.execute(mode=ValidationMode.FAST, dataset=DatasetClass.DEVELOPMENT, disposition=ValidationDisposition.CONFIRMED)

    def test_fast_and_confirmatory_modes_bind_the_same_strategy_artifact(self):
        fast = self.execute(mode=ValidationMode.FAST, dataset=DatasetClass.DEVELOPMENT)
        confirmatory = self.execute(mode=ValidationMode.CONFIRMATORY, dataset=DatasetClass.VALIDATION)
        self.assertEqual(fast.access_record.experiment.strategy_identity_id, self.strategy.identity_id)
        self.assertEqual(confirmatory.access_record.experiment.code_hash, self.strategy.code_hash)

    def test_confirmatory_mode_can_emit_confirmed_result_bound_to_existing_experiment(self):
        observation = ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100"))
        result = self.execute(disposition=ValidationDisposition.CONFIRMED, observations=(observation,), cutoff=at(9, 10), assumptions=self.assumptions, specifications=(OrderSpecification("request-1", Decimal("1")),), capital_snapshot=self.capital_snapshot, capital_assumptions=self.capital_assumptions)
        self.assertEqual(result.validation_record.event_type, "VALIDATION_CONFIRMED")
        self.assertEqual(result.validation_record.experiment, self.experiment)
        self.assertEqual(self.ledger.records[-1], result.validation_record)

    def test_final_unseen_is_denied_through_runner_before_execution(self):
        result = self.execute(dataset=DatasetClass.FINAL_UNSEEN)
        self.assertFalse(result.allowed)
        self.assertEqual(result.events, ())
        self.assertIsNone(result.validation_record)
        self.assertEqual(result.access_record.event_type, "DATASET_ACCESS_DENIED")
        self.assertEqual(len(self.ledger.records), 1)


if __name__ == "__main__":
    unittest.main()

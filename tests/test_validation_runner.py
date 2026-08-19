import inspect
import unittest
from decimal import Decimal
from datetime import date, datetime
from zoneinfo import ZoneInfo

from src.data_substrate import CompletedBar
from src.research_firewall import TEST_ONLY_SYNTHETIC_DATA_VERSION
from src.strategy_evidence import DatasetClass, EvidenceLedger, ExperimentIdentity
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


class ValidationRunnerTests(unittest.TestCase):
    def setUp(self):
        self.strategy = make_strategy(
            research_lineage_id="validation-lineage-fixture",
            family_id="neutral-validation-family",
        )
        self.experiment = make_experiment(self.strategy)
        self.ledger = EvidenceLedger()
        self.firewall, self.hypothesis_test_id = build_synthetic_firewall(
            self.ledger, self.strategy, self.experiment
        )
        self.runner = ChronologicalValidationRunner(self.ledger, self.firewall)
        self.bar = CompletedBar("TEST", DAY, at(9, 0), at(9, 5), at(9, 5))
        self.assumptions = ExecutionAssumptions("synthetic-v1", Decimal("1.5"), Decimal("0.25"))
        self.capital_assumptions = CapitalMarginAssumptions("capital-fixture-v1", Decimal("1"), Decimal("0.1"), "SYNTH")
        self.capital_snapshot = CapitalSnapshot(Decimal("100"))

    def execute(self, mode=ValidationMode.CONFIRMATORY, dataset=DatasetClass.DEVELOPMENT, inputs=None, disposition=None, observations=(), cutoff=None, assumptions=None, specifications=(), capital_snapshot=None, capital_assumptions=None, hypothesis_test_id=None):
        return self.runner.run(
            mode=mode,
            strategy=self.strategy,
            experiment=self.experiment,
            artifact_identity_id=self.strategy.identity_id,
            artifact_code_hash=self.strategy.code_hash,
            dataset_class=dataset,
            inputs=inputs or (make_validation_input("request-1", self.bar, at(9, 5), data_version=self.experiment.data_version),),
            disposition=disposition,
            hypothesis_test_id=hypothesis_test_id if hypothesis_test_id is not None else self.hypothesis_test_id,
            execution_observations=observations,
            execution_cutoff_at=cutoff,
            execution_assumptions=assumptions,
            order_specifications=specifications,
            capital_snapshot=capital_snapshot,
            capital_margin_assumptions=capital_assumptions,
        )

    def test_runner_reuses_existing_completed_bar_availability(self):
        with self.assertRaisesRegex(ChronologyError, "unavailable"):
            self.execute(inputs=(make_validation_input("request-1", self.bar, at(9, 4), data_version=self.experiment.data_version),))

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
            self.execute(inputs=(
                make_validation_input("request-2", later, at(9, 10), data_version=self.experiment.data_version),
                make_validation_input("request-1", self.bar, at(9, 5), data_version=self.experiment.data_version),
            ))

    def test_identical_replays_are_deterministic(self):
        first = self.execute()
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
            inputs=(make_validation_input("request-1", self.bar, at(9, 5), data_version=self.experiment.data_version),),
            hypothesis_test_id=second_hypothesis,
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
        confirmatory = self.execute(mode=ValidationMode.CONFIRMATORY, dataset=DatasetClass.DEVELOPMENT)
        self.assertEqual(fast.access_record.experiment.strategy_identity_id, self.strategy.identity_id)
        self.assertEqual(confirmatory.access_record.experiment.code_hash, self.strategy.code_hash)

    # A3: a full identity-bound TEST_ONLY DEVELOPMENT synthetic fixture passes the
    # authoritative pre-outcome gate and produces a synthetic confirmatory result.
    def test_synthetic_confirmatory_fixture_produces_confirmed_result(self):
        observation = ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100"))
        result = self.execute(
            disposition=ValidationDisposition.CONFIRMED,
            observations=(observation,),
            cutoff=at(9, 10),
            assumptions=self.assumptions,
            specifications=(OrderSpecification("request-1", Decimal("1")),),
            capital_snapshot=self.capital_snapshot,
            capital_assumptions=self.capital_assumptions,
        )
        self.assertTrue(result.allowed)
        self.assertEqual(result.access_record.event_type, "PRE_OUTCOME_GATE_GRANTED")
        self.assertEqual(result.access_record.outcome, "GRANTED")
        self.assertEqual(result.validation_record.event_type, "VALIDATION_CONFIRMED")
        self.assertEqual(result.validation_record.experiment, self.experiment)
        self.assertEqual(len(result.execution_outcomes), 1)
        self.assertEqual(result.execution_outcomes[0].status, FillStatus.FILLED)
        self.assertEqual(self.ledger.records[-1], result.validation_record)

    # A1/A2: the old CONFIRMATORY + VALIDATION + legacy coarse-grant path can no
    # longer produce VALIDATION_CONFIRMED; DATASET_ACCESS_GRANTED is never a
    # candidate authorization.
    def test_legacy_validation_confirmatory_path_cannot_confirm(self):
        validation_day = date(2025, 1, 15)
        validation_bar = CompletedBar(
            "TEST",
            validation_day,
            datetime(2025, 1, 15, 9, 0, tzinfo=CN),
            datetime(2025, 1, 15, 9, 5, tzinfo=CN),
            datetime(2025, 1, 15, 9, 5, tzinfo=CN),
        )
        result = self.execute(
            dataset=DatasetClass.VALIDATION,
            inputs=(make_validation_input("request-1", validation_bar, datetime(2025, 1, 15, 9, 5, tzinfo=CN), data_version=self.experiment.data_version),),
            disposition=ValidationDisposition.CONFIRMED,
            observations=(ExecutionObservation("request-1", datetime(2025, 1, 15, 9, 6, tzinfo=CN), datetime(2025, 1, 15, 9, 6, tzinfo=CN), Decimal("100")),),
            cutoff=datetime(2025, 1, 15, 9, 10, tzinfo=CN),
            assumptions=self.assumptions,
            specifications=(OrderSpecification("request-1", Decimal("1")),),
            capital_snapshot=self.capital_snapshot,
            capital_assumptions=self.capital_assumptions,
        )
        self.assertFalse(result.allowed)
        self.assertIsNone(result.validation_record)
        self.assertEqual(result.events, ())
        self.assertEqual(result.execution_outcomes, ())
        self.assertEqual(result.access_record.event_type, "PRE_OUTCOME_GATE_DENIED")
        self.assertNotIn("VALIDATION_CONFIRMED", [record.event_type for record in self.ledger.records])

    # A5: a real 2025 validation bar cannot execute even if the caller claims
    # DatasetClass.DEVELOPMENT; the cohort derives from the actual date.
    def test_validation_date_cannot_pass_as_development_dataset(self):
        validation_bar = CompletedBar(
            "TEST",
            date(2025, 3, 1),
            datetime(2025, 3, 1, 9, 0, tzinfo=CN),
            datetime(2025, 3, 1, 9, 5, tzinfo=CN),
            datetime(2025, 3, 1, 9, 5, tzinfo=CN),
        )
        with self.assertRaisesRegex(ValueError, "does not match the actual input data cohort"):
            self.execute(
                dataset=DatasetClass.DEVELOPMENT,
                inputs=(make_validation_input("request-1", validation_bar, datetime(2025, 3, 1, 9, 5, tzinfo=CN), data_version=self.experiment.data_version),),
                disposition=ValidationDisposition.CONFIRMED,
                observations=(ExecutionObservation("request-1", datetime(2025, 3, 1, 9, 6, tzinfo=CN), datetime(2025, 3, 1, 9, 6, tzinfo=CN), Decimal("100")),),
                cutoff=datetime(2025, 3, 1, 9, 10, tzinfo=CN),
                assumptions=self.assumptions,
                specifications=(OrderSpecification("request-1", Decimal("1")),),
                capital_snapshot=self.capital_snapshot,
                capital_assumptions=self.capital_assumptions,
            )

    # A6: one confirmatory run spanning DEVELOPMENT + VALIDATION dates fails closed.
    def test_mixed_cohort_inputs_fail_closed(self):
        validation_bar = CompletedBar(
            "TEST",
            date(2025, 1, 2),
            datetime(2025, 1, 2, 9, 0, tzinfo=CN),
            datetime(2025, 1, 2, 9, 5, tzinfo=CN),
            datetime(2025, 1, 2, 9, 5, tzinfo=CN),
        )
        with self.assertRaisesRegex(ValueError, "multiple research cohorts"):
            self.execute(
                dataset=DatasetClass.DEVELOPMENT,
                inputs=(
                    make_validation_input("request-1", self.bar, at(9, 5), data_version=self.experiment.data_version),
                    make_validation_input("request-2", validation_bar, datetime(2025, 1, 2, 9, 5, tzinfo=CN), data_version=self.experiment.data_version),
                ),
                disposition=ValidationDisposition.CONFIRMED,
                observations=(ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100")),),
                cutoff=datetime(2025, 1, 2, 9, 10, tzinfo=CN),
                assumptions=self.assumptions,
                specifications=(OrderSpecification("request-1", Decimal("1")),),
                capital_snapshot=self.capital_snapshot,
                capital_assumptions=self.capital_assumptions,
            )

    # A7: ValidationInput.data_version_id != ExperimentIdentity.data_version must
    # fail closed before any execution.
    def test_validation_input_data_version_mismatch_fails_before_execution(self):
        mismatched = make_validation_input("request-1", self.bar, at(9, 5), data_version="data-v2")
        self.assertNotEqual(mismatched.data_version_id, self.experiment.data_version)
        with self.assertRaisesRegex(ValueError, "data_version"):
            self.runner.run(
                mode=ValidationMode.CONFIRMATORY,
                strategy=self.strategy,
                experiment=self.experiment,
                artifact_identity_id=self.strategy.identity_id,
                artifact_code_hash=self.strategy.code_hash,
                dataset_class=DatasetClass.DEVELOPMENT,
                inputs=(mismatched,),
                disposition=ValidationDisposition.CONFIRMED,
                execution_observations=(ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100")),),
                execution_cutoff_at=at(9, 10),
                execution_assumptions=self.assumptions,
                order_specifications=(OrderSpecification("request-1", Decimal("1")),),
                capital_snapshot=self.capital_snapshot,
                capital_margin_assumptions=self.capital_assumptions,
            )
        # No gate record, no execution record, no confirmation.
        self.assertEqual(self.ledger.records, ())

    # A12: ChronologicalValidationRunner.run no longer accepts a caller-supplied
    # synthetic_fixture boolean.
    def test_runner_run_has_no_caller_synthetic_boolean(self):
        params = set(inspect.signature(self.runner.run).parameters)
        self.assertNotIn("synthetic_fixture", params)

    # A16: input.data_version_id == TEST_ONLY_SYNTHETIC_DATA_VERSION while
    # experiment.data_version is an ordinary value must fail closed before any
    # execution (the governed synthetic version cannot mask a real experiment).
    def test_synthetic_input_version_with_ordinary_experiment_fails_closed(self):
        ordinary_strategy = make_strategy(
            research_lineage_id="validation-lineage-fixture",
            family_id="neutral-validation-family",
        )
        ordinary_experiment = make_experiment(ordinary_strategy, data_version="real-development-data-v1")
        mismatched = make_validation_input(
            "request-1", self.bar, at(9, 5), data_version=TEST_ONLY_SYNTHETIC_DATA_VERSION
        )
        self.assertEqual(mismatched.data_version_id, TEST_ONLY_SYNTHETIC_DATA_VERSION)
        self.assertNotEqual(mismatched.data_version_id, ordinary_experiment.data_version)
        with self.assertRaisesRegex(ValueError, "data_version"):
            self.runner.run(
                mode=ValidationMode.CONFIRMATORY,
                strategy=ordinary_strategy,
                experiment=ordinary_experiment,
                artifact_identity_id=ordinary_strategy.identity_id,
                artifact_code_hash=ordinary_strategy.code_hash,
                dataset_class=DatasetClass.DEVELOPMENT,
                inputs=(mismatched,),
                disposition=ValidationDisposition.CONFIRMED,
                execution_observations=(ExecutionObservation("request-1", at(9, 6), at(9, 6), Decimal("100")),),
                execution_cutoff_at=at(9, 10),
                execution_assumptions=self.assumptions,
                order_specifications=(OrderSpecification("request-1", Decimal("1")),),
                capital_snapshot=self.capital_snapshot,
                capital_margin_assumptions=self.capital_assumptions,
            )
        # No gate record, no execution record, no confirmation.
        self.assertEqual(self.ledger.records, ())

    def test_final_unseen_is_denied_through_runner_before_execution(self):
        result = self.execute(dataset=DatasetClass.FINAL_UNSEEN)
        self.assertFalse(result.allowed)
        self.assertEqual(result.events, ())
        self.assertIsNone(result.validation_record)
        self.assertEqual(result.access_record.event_type, "DATASET_ACCESS_DENIED")
        self.assertEqual(len(self.ledger.records), 1)


if __name__ == "__main__":
    unittest.main()

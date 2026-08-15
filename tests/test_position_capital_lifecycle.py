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
    ChronologyError,
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
DAY = date(2025, 6, 16)


def at(hour, minute):
    return datetime(DAY.year, DAY.month, DAY.day, hour, minute, tzinfo=CN)


def make_strategy():
    return StrategyIdentity(
        research_lineage_id="position-lifecycle-lineage-fixture",
        family_id="neutral-position-lifecycle-family",
        strategy_version="1.0",
        source="deterministic-synthetic-fixture",
        applicable_instruments=("TEST",),
        timeframe="5m",
        parameters=(TypedParameter("window", "int", 3),),
        code_hash="position-lifecycle-code-fixture-v1",
        environment_hash="position-lifecycle-environment-fixture-v1",
        required_feature_versions=("position-context-fixture-v1",),
        lifecycle_state=LifecycleState.DRAFT,
        data_exposure_history_reference="position-exposure-fixture-v1",
    )


class PositionCapitalLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.strategy = make_strategy()
        self.experiment = ExperimentIdentity.from_strategy(
            self.strategy,
            "position-data-fixture-v1",
            "position-exposure-fixture-v1",
        )
        self.execution_assumptions = ExecutionAssumptions(
            "synthetic-position-execution-v1",
            Decimal("1.5"),
            Decimal("0.25"),
        )
        self.capital_assumptions = CapitalMarginAssumptions(
            "synthetic-position-capital-v1",
            Decimal("1"),
            Decimal("0.1"),
            "SYNTH",
            Decimal("0.05"),
        )
        self.validation_input = ValidationInput(
            "request-1",
            CompletedBar("TEST", DAY, at(9, 0), at(9, 5), at(9, 5)),
            at(9, 5),
        )

    def run_case(
        self,
        *,
        mark=None,
        initial_tradable=True,
        liquidation_observations=(),
        dataset=DatasetClass.VALIDATION,
        capital_assumptions=None,
        initial_snapshot=None,
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
            inputs=(self.validation_input,),
            disposition=ValidationDisposition.CONFIRMED,
            execution_observations=(
                ExecutionObservation(
                    "request-1",
                    at(9, 6),
                    at(9, 6),
                    Decimal("100"),
                    tradable=initial_tradable,
                ),
            ),
            execution_cutoff_at=at(9, 30),
            execution_assumptions=self.execution_assumptions,
            order_specifications=(OrderSpecification("request-1", Decimal("1")),),
            capital_snapshot=initial_snapshot or CapitalSnapshot(Decimal("20")),
            capital_margin_assumptions=capital_assumptions or self.capital_assumptions,
            mark_observations=(() if mark is None else (mark,)),
            forced_liquidation_observations=liquidation_observations,
        )
        return result, ledger

    def filled_snapshot(self):
        result, _ = self.run_case()
        return result.final_capital_snapshot

    def mark_for(
        self,
        snapshot,
        price,
        *,
        observation_id="mark-1",
        position_id=None,
        request_id=None,
        instrument=None,
        observed_at=at(9, 10),
        available_at=at(9, 10),
    ):
        return MarkObservation(
            observation_id,
            position_id or snapshot.position_id,
            request_id or snapshot.position_request_id,
            instrument or snapshot.position_instrument,
            observed_at,
            available_at,
            price,
        )

    def adverse_mark_and_requirement(self):
        snapshot = self.filled_snapshot()
        mark = self.mark_for(snapshot, Decimal("40"))
        result, _ = self.run_case(mark=mark)
        return mark, result.liquidation_requirement

    def test_fill_creates_position_and_no_fill_creates_none(self):
        filled, _ = self.run_case()
        snapshot = filled.final_capital_snapshot
        self.assertEqual(snapshot.position_instrument, "TEST")
        self.assertEqual(snapshot.position_request_id, "request-1")
        self.assertEqual(snapshot.position_quantity, Decimal("1"))
        self.assertEqual(snapshot.average_open_price, Decimal("101.5"))
        self.assertEqual(snapshot.execution_assumption_id, self.execution_assumptions.identity_id)
        self.assertEqual(snapshot.capital_assumption_id, self.capital_assumptions.identity_id)

        not_filled, _ = self.run_case(initial_tradable=False)
        self.assertEqual(not_filled.execution_outcomes[0].status, FillStatus.NOT_FILLED)
        self.assertEqual(not_filled.final_capital_snapshot.position_quantity, Decimal("0"))
        self.assertIsNone(not_filled.final_capital_snapshot.position_id)

    def test_later_available_mark_updates_unrealized_pnl_and_equity(self):
        snapshot = self.filled_snapshot()
        mark = self.mark_for(snapshot, Decimal("100"))
        result, _ = self.run_case(mark=mark)
        marked = result.final_capital_snapshot
        self.assertEqual(marked.unrealized_pnl, Decimal("-1.5"))
        self.assertEqual(marked.equity, Decimal("18.25"))
        self.assertEqual(marked.available_resources, Decimal("8.10"))
        self.assertEqual(result.mark_transitions[0].maintenance_requirement, Decimal("5.00"))

    def test_unavailable_or_pre_position_mark_fails_closed(self):
        snapshot = self.filled_snapshot()
        future_mark = self.mark_for(
            snapshot,
            Decimal("100"),
            observed_at=at(9, 31),
            available_at=at(9, 31),
        )
        with self.assertRaisesRegex(ChronologyError, "unavailable"):
            self.run_case(mark=future_mark)

        early_mark = self.mark_for(
            snapshot,
            Decimal("100"),
            observed_at=at(9, 6),
            available_at=at(9, 6),
        )
        with self.assertRaisesRegex(ChronologyError, "after the position"):
            self.run_case(mark=early_mark)

    def test_maintenance_identity_is_deterministic_and_outcome_affecting(self):
        same = CapitalMarginAssumptions(
            "synthetic-position-capital-v1",
            Decimal("1"),
            Decimal("0.1"),
            "SYNTH",
            Decimal("0.05"),
        )
        changed = CapitalMarginAssumptions(
            "synthetic-position-capital-v1",
            Decimal("1"),
            Decimal("0.1"),
            "SYNTH",
            Decimal("0.04"),
        )
        self.assertEqual(self.capital_assumptions.identity_id, same.identity_id)
        self.assertNotEqual(self.capital_assumptions.identity_id, changed.identity_id)

    def test_healthy_margin_creates_no_liquidation(self):
        snapshot = self.filled_snapshot()
        result, ledger = self.run_case(mark=self.mark_for(snapshot, Decimal("100")))
        self.assertFalse(result.mark_transitions[0].breached)
        self.assertIsNone(result.liquidation_requirement)
        self.assertIsNone(result.liquidation_outcome)
        self.assertNotIn("FORCED_LIQUIDATION_REQUIRED", [record.event_type for record in ledger.records])

    def test_adverse_mark_breaches_before_liquidation_eligibility(self):
        mark, requirement = self.adverse_mark_and_requirement()
        result, ledger = self.run_case(mark=mark)
        self.assertTrue(result.mark_transitions[0].breached)
        self.assertEqual(requirement.breach_at, mark.available_at)
        event_types = [event.event_type for event in result.events]
        self.assertLess(
            event_types.index("MAINTENANCE_MARGIN_BREACH"),
            event_types.index("FORCED_LIQUIDATION_REQUIRED"),
        )
        self.assertIn("MAINTENANCE_MARGIN_BREACH", [record.event_type for record in ledger.records])

    def test_later_tradable_observation_closes_position_and_reconciles_capital(self):
        mark, requirement = self.adverse_mark_and_requirement()
        observation = ExecutionObservation(
            requirement.request_id,
            at(9, 12),
            at(9, 12),
            Decimal("39"),
        )
        result, _ = self.run_case(mark=mark, liquidation_observations=(observation,))
        outcome = result.liquidation_outcome.execution_outcome
        transition = result.liquidation_outcome.capital_transition
        final = result.final_capital_snapshot
        self.assertEqual(outcome.status, FillStatus.FILLED)
        self.assertEqual(outcome.fill_price, Decimal("37.5"))
        self.assertEqual(transition.before, result.mark_transitions[-1].after)
        self.assertEqual(transition.released_margin, Decimal("10.15"))
        self.assertEqual(transition.realized_pnl_change, Decimal("-64.0"))
        self.assertEqual(final.position_quantity, Decimal("0"))
        self.assertEqual(final.reserved_margin, Decimal("0"))
        self.assertEqual(final.realized_pnl, Decimal("-64.0"))
        self.assertEqual(final.unrealized_pnl, Decimal("0"))
        self.assertEqual(final.charged_costs, Decimal("0.50"))
        self.assertEqual(final.available_capital, Decimal("-44.50"))

    def test_missing_or_nontradable_liquidation_observation_never_fabricates_fill(self):
        mark, requirement = self.adverse_mark_and_requirement()
        missing, _ = self.run_case(mark=mark)
        self.assertEqual(missing.liquidation_outcome.execution_outcome.status, FillStatus.NOT_FILLED)
        self.assertEqual(missing.liquidation_outcome.execution_outcome.reason, "NO_OBSERVATION")
        self.assertIsNone(missing.liquidation_outcome.capital_transition)
        self.assertEqual(missing.final_capital_snapshot.position_quantity, Decimal("1"))

        nontradable = ExecutionObservation(
            requirement.request_id,
            at(9, 12),
            at(9, 12),
            Decimal("39"),
            tradable=False,
        )
        unresolved, _ = self.run_case(mark=mark, liquidation_observations=(nontradable,))
        self.assertEqual(unresolved.liquidation_outcome.execution_outcome.reason, "NOT_TRADABLE")
        self.assertIsNone(unresolved.liquidation_outcome.capital_transition)
        self.assertEqual(unresolved.final_capital_snapshot.position_quantity, Decimal("1"))

        unavailable = ExecutionObservation(
            requirement.request_id,
            at(9, 31),
            at(9, 31),
            Decimal("39"),
        )
        after_cutoff, _ = self.run_case(mark=mark, liquidation_observations=(unavailable,))
        self.assertEqual(after_cutoff.liquidation_outcome.execution_outcome.reason, "OBSERVATION_AFTER_CUTOFF")
        self.assertIsNone(after_cutoff.liquidation_outcome.capital_transition)

    def test_liquidation_realizes_and_releases_exactly_once(self):
        mark, requirement = self.adverse_mark_and_requirement()
        observation = ExecutionObservation(requirement.request_id, at(9, 12), at(9, 12), Decimal("39"))
        result, _ = self.run_case(mark=mark, liquidation_observations=(observation,))
        liquidation_transitions = [
            transition
            for transition in result.capital_transitions
            if transition.transition_type == "FORCED_LIQUIDATION"
        ]
        self.assertEqual(len(liquidation_transitions), 1)
        self.assertEqual(liquidation_transitions[0].released_margin, Decimal("10.15"))
        self.assertEqual(liquidation_transitions[0].after.realized_pnl, Decimal("-64.0"))
        with self.assertRaisesRegex(ValueError, "at most one"):
            self.run_case(mark=mark, liquidation_observations=(observation, observation))

    def test_identical_history_produces_identical_snapshots_and_evidence(self):
        mark, requirement = self.adverse_mark_and_requirement()
        observation = ExecutionObservation(requirement.request_id, at(9, 12), at(9, 12), Decimal("39"))
        first, first_ledger = self.run_case(mark=mark, liquidation_observations=(observation,))
        second, second_ledger = self.run_case(mark=mark, liquidation_observations=(observation,))
        self.assertEqual(first.final_capital_snapshot, second.final_capital_snapshot)
        self.assertEqual(first.capital_transitions, second.capital_transitions)
        self.assertEqual(first.mark_transitions, second.mark_transitions)
        self.assertEqual(
            [record.record_id for record in first_ledger.records],
            [record.record_id for record in second_ledger.records],
        )

    def test_evidence_binds_experiment_assumptions_mark_position_and_liquidation(self):
        mark, requirement = self.adverse_mark_and_requirement()
        observation = ExecutionObservation(requirement.request_id, at(9, 12), at(9, 12), Decimal("39"))
        result, ledger = self.run_case(mark=mark, liquidation_observations=(observation,))
        lifecycle_records = [
            record
            for record in ledger.records
            if record.event_type
            in {
                "POSITION_TRANSITION",
                "MARK_TO_MARKET",
                "MAINTENANCE_MARGIN_BREACH",
                "FORCED_LIQUIDATION_REQUIRED",
                "FORCED_LIQUIDATION_FILLED",
            }
        ]
        self.assertTrue(lifecycle_records)
        for record in lifecycle_records:
            self.assertEqual(record.experiment, self.experiment)
            self.assertIn(self.execution_assumptions.identity_id, record.evidence_reference)
            self.assertIn(self.capital_assumptions.identity_id, record.evidence_reference)
            self.assertIsNotNone(record.fact_reference)
        self.assertIn(mark.reference_id, result.validation_record.evidence_reference)
        self.assertIn(result.liquidation_outcome.reference_id, result.validation_record.evidence_reference)

    def test_wrong_mark_or_liquidation_binding_fails_closed(self):
        snapshot = self.filled_snapshot()
        wrong_marks = (
            self.mark_for(snapshot, Decimal("40"), position_id="wrong-position"),
            self.mark_for(snapshot, Decimal("40"), request_id="wrong-request"),
            self.mark_for(snapshot, Decimal("40"), instrument="WRONG"),
        )
        for mark in wrong_marks:
            with self.subTest(mark=mark):
                with self.assertRaises(ValueError):
                    self.run_case(mark=mark)

        mark, requirement = self.adverse_mark_and_requirement()
        wrong_observation = ExecutionObservation("wrong-request", at(9, 12), at(9, 12), Decimal("39"))
        with self.assertRaisesRegex(ValueError, "does not match"):
            self.run_case(mark=mark, liquidation_observations=(wrong_observation,))

        early_observation = ExecutionObservation(
            requirement.request_id,
            requirement.eligible_at,
            requirement.eligible_at,
            Decimal("39"),
        )
        with self.assertRaisesRegex(ChronologyError, "later than"):
            self.run_case(mark=mark, liquidation_observations=(early_observation,))

    def test_position_requires_fill_and_liquidation_requires_breach(self):
        snapshot = self.filled_snapshot()
        healthy_mark = self.mark_for(snapshot, Decimal("100"))
        invented_liquidation = ExecutionObservation(
            "invented-liquidation",
            at(9, 12),
            at(9, 12),
            Decimal("99"),
        )
        with self.assertRaisesRegex(ValueError, "without a maintenance breach"):
            self.run_case(mark=healthy_mark, liquidation_observations=(invented_liquidation,))

        with self.assertRaisesRegex(ValueError, "valid prior filled position"):
            self.run_case(mark=healthy_mark, initial_tradable=False)

        fabricated_snapshot = CapitalSnapshot(
            starting_capital=Decimal("20"),
            reserved_margin=Decimal("1"),
            position_quantity=Decimal("1"),
            average_open_price=Decimal("10"),
            position_instrument="TEST",
            position_id="fabricated-position",
            position_request_id="fabricated-request",
            execution_assumption_id=self.execution_assumptions.identity_id,
            capital_assumption_id=self.capital_assumptions.identity_id,
            state_at=at(9, 4),
        )
        with self.assertRaisesRegex(ValueError, "requires a valid fill"):
            self.run_case(initial_snapshot=fabricated_snapshot)

    def test_inconsistent_assumption_identity_and_invalid_mark_arithmetic_fail_closed(self):
        snapshot = self.filled_snapshot()
        mark = self.mark_for(snapshot, Decimal("100"))
        changed_assumptions = CapitalMarginAssumptions(
            "synthetic-position-capital-v2",
            Decimal("1"),
            Decimal("0.1"),
            "SYNTH",
            Decimal("0.05"),
        )
        with self.assertRaisesRegex(ValueError, "identity does not match"):
            ChronologicalValidationRunner._apply_marks(
                (mark,),
                snapshot,
                at(9, 30),
                changed_assumptions,
            )
        with self.assertRaisesRegex(ValueError, "positive Decimal"):
            self.mark_for(snapshot, Decimal("0"))

    def test_final_unseen_remains_denied_before_lifecycle(self):
        snapshot = self.filled_snapshot()
        result, ledger = self.run_case(
            mark=self.mark_for(snapshot, Decimal("40")),
            dataset=DatasetClass.FINAL_UNSEEN,
        )
        self.assertFalse(result.allowed)
        self.assertEqual(result.mark_transitions, ())
        self.assertIsNone(result.final_capital_snapshot)
        self.assertEqual([record.event_type for record in ledger.records], ["DATASET_ACCESS_DENIED"])


if __name__ == "__main__":
    unittest.main()

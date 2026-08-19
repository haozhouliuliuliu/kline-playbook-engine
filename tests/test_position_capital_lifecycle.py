import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.contract_semantics import CloseOffset, OffsetCostAssumptions, OrderAction, PositionDirection
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
        direction=PositionDirection.LONG,
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
            order_specifications=(
                OrderSpecification("request-1", Decimal("1"), direction=direction),
            ),
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

    def run_lifecycle(
        self,
        *,
        prices,
        quantities,
        actions,
        directions=None,
        offsets=None,
        starting_capital=Decimal("100"),
        slippage=Decimal("1.5"),
        fee=Decimal("0.25"),
        close_today_fee=Decimal("1"),
        close_previous_fee=Decimal("2"),
        mark=None,
    ):
        """Run a full deterministic multi-step OPEN/ADD/CLOSE lifecycle.

        ``prices``/``quantities``/``actions`` are parallel sequences; each
        order receives a distinct request id and strictly increasing
        decision/observation times.
        """
        execution_assumptions = ExecutionAssumptions(
            "synthetic-position-execution-v1",
            slippage,
            fee,
        )
        offset_costs = OffsetCostAssumptions(
            "synthetic-offset-cost-v1",
            close_today_fee,
            close_previous_fee,
        )
        directions = list(directions or [PositionDirection.LONG] * len(quantities))
        offsets = list(offsets or [None] * len(quantities))
        inputs = []
        observations = []
        specifications = []
        for index, (price, quantity, action, direction, offset) in enumerate(
            zip(prices, quantities, actions, directions, offsets)
        ):
            request_id = f"request-{index + 1}"
            decision_at = at(9, 5) + timedelta(minutes=2 * index)
            inputs.append(
                ValidationInput(
                    request_id,
                    CompletedBar(
                        "TEST",
                        DAY,
                        decision_at - timedelta(minutes=5),
                        decision_at,
                        decision_at,
                    ),
                    decision_at,
                )
            )
            observations.append(
                ExecutionObservation(
                    request_id,
                    decision_at + timedelta(minutes=1),
                    decision_at + timedelta(minutes=1),
                    Decimal(price),
                )
            )
            specifications.append(
                OrderSpecification(
                    request_id,
                    Decimal(quantity),
                    action=action,
                    close_offset=offset if action is OrderAction.CLOSE else None,
                    direction=direction,
                )
            )
        ledger = EvidenceLedger()
        runner = ChronologicalValidationRunner(ledger, FinalUnseenFirewall(ledger))
        result = runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            artifact_identity_id=self.strategy.identity_id,
            artifact_code_hash=self.strategy.code_hash,
            dataset_class=DatasetClass.VALIDATION,
            inputs=tuple(inputs),
            disposition=ValidationDisposition.CONFIRMED,
            execution_observations=tuple(observations),
            execution_cutoff_at=at(9, 30),
            execution_assumptions=execution_assumptions,
            order_specifications=tuple(specifications),
            capital_snapshot=CapitalSnapshot(starting_capital),
            capital_margin_assumptions=self.capital_assumptions,
            mark_observations=(() if mark is None else (mark,)),
            offset_cost_assumptions=offset_costs,
        )
        return result, ledger

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

    def test_short_position_uses_sell_side_fill_and_inverse_mark_to_market(self):
        opened, _ = self.run_case(direction=PositionDirection.SHORT)
        snapshot = opened.final_capital_snapshot
        self.assertEqual(snapshot.average_open_price, Decimal("98.5"))
        self.assertIs(snapshot.position_direction, PositionDirection.SHORT)

        mark = self.mark_for(snapshot, Decimal("97"))
        marked, _ = self.run_case(mark=mark, direction=PositionDirection.SHORT)
        self.assertEqual(marked.final_capital_snapshot.unrealized_pnl, Decimal("1.5"))

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
            position_trading_day=DAY,
            today_quantity=Decimal("1"),
            position_direction=PositionDirection.LONG,
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

    # ------------------------------------------------------------------
    # TD-002: after a PARTIAL CLOSE the remaining open position must keep a
    # correct deterministic valuation under an explicit mark-price semantic
    # (the close fill price), instead of temporarily clearing unrealized PnL
    # to zero until a later mark.
    # ------------------------------------------------------------------

    def test_partial_close_preserves_remaining_quantity_and_revalues_remaining(self):
        result, _ = self.run_lifecycle(
            prices=(100, 110, 112),
            quantities=(2, 1, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE_TODAY, CloseOffset.CLOSE_TODAY),
        )
        partial = result.capital_transitions[1].after
        final = result.final_capital_snapshot
        # Remaining quantity is preserved, not fabricated.
        self.assertEqual(partial.position_quantity, Decimal("1"))
        self.assertEqual(partial.today_quantity, Decimal("1"))
        self.assertEqual(partial.average_open_price, Decimal("101.5"))
        # Partial close realizes 1 unit at 108.5 vs avg open 101.5.
        self.assertEqual(partial.realized_pnl, Decimal("7"))
        # Remaining unit is re-marked at the close fill price, so its
        # unrealized PnL is nonzero (not cleared).
        self.assertEqual(partial.unrealized_pnl, Decimal("7"))
        self.assertEqual(partial.equity, Decimal("112.5"))
        # Full close ends flat with zero remaining unrealized.
        self.assertEqual(final.position_quantity, Decimal("0"))
        self.assertEqual(final.unrealized_pnl, Decimal("0"))
        self.assertEqual(final.realized_pnl, Decimal("16"))
        self.assertEqual(final.charged_costs, Decimal("2.75"))
        self.assertEqual(final.equity, Decimal("113.25"))

    def test_optional_add_then_partial_close_preserves_correct_remaining_quantity(self):
        result, _ = self.run_lifecycle(
            prices=(100, 104, 110, 112),
            quantities=(1, 1, 1, 1),
            actions=(OrderAction.OPEN, OrderAction.OPEN, OrderAction.CLOSE, OrderAction.CLOSE),
            offsets=(None, None, CloseOffset.CLOSE_TODAY, CloseOffset.CLOSE_TODAY),
        )
        added = result.capital_transitions[1].after
        partial = result.capital_transitions[2].after
        final = result.final_capital_snapshot
        self.assertEqual(added.average_open_price, Decimal("103.5"))
        self.assertEqual(added.position_quantity, Decimal("2"))
        self.assertEqual(partial.position_quantity, Decimal("1"))
        self.assertEqual(partial.realized_pnl, Decimal("5"))
        self.assertEqual(partial.unrealized_pnl, Decimal("5"))
        self.assertEqual(partial.equity, Decimal("108.25"))
        self.assertEqual(final.position_quantity, Decimal("0"))
        self.assertEqual(final.unrealized_pnl, Decimal("0"))

    def test_short_partial_close_favorable_mark_is_consistent(self):
        short = PositionDirection.SHORT
        result, _ = self.run_lifecycle(
            prices=(100, 90),
            quantities=(2, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE),
            directions=(short, short),
            offsets=(None, CloseOffset.CLOSE_TODAY),
        )
        partial = result.capital_transitions[1].after
        self.assertEqual(partial.average_open_price, Decimal("98.5"))
        self.assertEqual(partial.position_quantity, Decimal("1"))
        self.assertEqual(partial.realized_pnl, Decimal("7"))
        self.assertEqual(partial.unrealized_pnl, Decimal("7"))

    def test_adverse_partial_close_leaves_negative_remaining_unrealized(self):
        result, _ = self.run_lifecycle(
            prices=(100, 90),
            quantities=(2, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE_TODAY),
        )
        partial = result.capital_transitions[1].after
        self.assertEqual(partial.position_quantity, Decimal("1"))
        self.assertEqual(partial.realized_pnl, Decimal("-13"))
        self.assertEqual(partial.unrealized_pnl, Decimal("-13"))

    def test_partial_close_does_not_create_artificial_equity_jump(self):
        # Zero transaction costs isolate the mark-to-market from fees.
        full_close, _ = self.run_lifecycle(
            prices=(100, 110),
            quantities=(2, 2),
            actions=(OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE_TODAY),
            slippage=Decimal("0"),
            fee=Decimal("0"),
            close_today_fee=Decimal("0"),
            close_previous_fee=Decimal("0"),
        )
        partial_then_full, _ = self.run_lifecycle(
            prices=(100, 110, 110),
            quantities=(2, 1, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE_TODAY, CloseOffset.CLOSE_TODAY),
            slippage=Decimal("0"),
            fee=Decimal("0"),
            close_today_fee=Decimal("0"),
            close_previous_fee=Decimal("0"),
        )
        after_partial = partial_then_full.capital_transitions[1].after
        after_full = partial_then_full.final_capital_snapshot
        # Marking the whole position at the close price yields the same equity
        # whether it is closed in one order or partly then fully closed.
        self.assertEqual(after_partial.unrealized_pnl, Decimal("10"))
        self.assertEqual(after_partial.equity, Decimal("120"))
        self.assertEqual(full_close.final_capital_snapshot.equity, Decimal("120"))
        self.assertEqual(after_full.equity, Decimal("120"))

    def test_realized_pnl_and_transaction_costs_unaffected_by_unrealized_fix(self):
        result, _ = self.run_lifecycle(
            prices=(100, 110, 112),
            quantities=(2, 1, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE_TODAY, CloseOffset.CLOSE_TODAY),
        )
        partial_transition = result.capital_transitions[1]
        full_transition = result.capital_transitions[2]
        # Realized PnL changes are driven only by the close fill price.
        self.assertEqual(partial_transition.realized_pnl_change, Decimal("7"))
        self.assertEqual(partial_transition.quantity_change, Decimal("-1"))
        self.assertEqual(partial_transition.resolved_close_offset, CloseOffset.CLOSE_TODAY)
        # Transaction-cost semantics are unchanged: synthetic fee + per-unit
        # close-today offset fee.
        self.assertEqual(partial_transition.required_cost, Decimal("1.25"))
        self.assertEqual(full_transition.realized_pnl_change, Decimal("9"))
        self.assertEqual(full_transition.required_cost, Decimal("1.25"))
        self.assertEqual(result.final_capital_snapshot.realized_pnl, Decimal("16"))

    def test_later_mark_after_partial_close_revalues_remaining_quantity(self):
        base, _ = self.run_lifecycle(
            prices=(100, 110),
            quantities=(2, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE_TODAY),
        )
        after_partial = base.capital_transitions[1].after
        mark = MarkObservation(
            "mark-after-partial",
            after_partial.position_id,
            after_partial.position_request_id,
            after_partial.position_instrument,
            at(9, 14),
            at(9, 14),
            Decimal("115"),
        )
        marked, _ = self.run_lifecycle(
            prices=(100, 110),
            quantities=(2, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE_TODAY),
            mark=mark,
        )
        marked_after = marked.mark_transitions[0].after
        final = marked.final_capital_snapshot
        # The later mark revalues the REMAINING quantity (1), not the old
        # pre-close quantity (2).
        self.assertEqual(marked_after.position_quantity, Decimal("1"))
        self.assertEqual(marked_after.unrealized_pnl, Decimal("13.5"))
        self.assertEqual(final.realized_pnl, Decimal("7"))
        self.assertEqual(final.equity, Decimal("119.0"))


if __name__ == "__main__":
    unittest.main()

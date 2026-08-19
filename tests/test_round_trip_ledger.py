import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.contract_semantics import (
    CloseOffset,
    OffsetCostAssumptions,
    OrderAction,
    PositionDirection,
)
from src.data_substrate import CompletedBar, SessionMetadata, SessionWindow
from src.round_trip_ledger import (
    TERMINAL_REASON_FORCED_LIQUIDATION,
    TERMINAL_REASON_FULL_CLOSE,
    CompletedRoundTrip,
    RoundTripLedger,
    RoundTripMaterializer,
)
from src.strategy_evidence import DatasetClass, EvidenceLedger
from src.validation_runner import (
    CapitalMarginAssumptions,
    CapitalSnapshot,
    CapitalTransition,
    ChronologicalValidationRunner,
    ExecutionAssumptions,
    ExecutionObservation,
    FillStatus,
    MarkObservation,
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


def at(hour, minute, day=DAY):
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=CN)


def run_lifecycle(
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
    liquidation_observations=(),
    initial_snapshot=None,
):
    """Run a full deterministic multi-step OPEN/ADD/CLOSE lifecycle.

    Mirrors the authoritative runner lifecycle used by the position-capital
    tests.  ``prices``/``quantities``/``actions`` are parallel sequences; each
    order receives a distinct request id and strictly increasing times.
    Returns the ``ValidationRunResult``.
    """
    execution_assumptions = ExecutionAssumptions(
        "synthetic-round-trip-execution-v1",
        slippage,
        fee,
    )
    capital_assumptions = CapitalMarginAssumptions(
        "synthetic-round-trip-capital-v1",
        Decimal("1"),
        Decimal("0.1"),
        "SYNTH",
        Decimal("0.05"),
    )
    offset_costs = OffsetCostAssumptions(
        "synthetic-round-trip-offset-v1",
        close_today_fee,
        close_previous_fee,
    )
    strategy = make_strategy(
        research_lineage_id="round-trip-ledger-lineage-fixture",
        family_id="neutral-round-trip-ledger-family",
        source="deterministic-synthetic-fixture",
        code_hash="round-trip-ledger-code-fixture-v1",
        environment_hash="round-trip-ledger-environment-fixture-v1",
        required_feature_versions=("round-trip-context-fixture-v1",),
        data_exposure_history_reference="round-trip-exposure-fixture-v1",
    )
    experiment = make_experiment(
        strategy,
        dataset_exposure_reference="round-trip-exposure-fixture-v1",
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
            make_validation_input(
                request_id,
                CompletedBar(
                    "TEST",
                    DAY,
                    decision_at - timedelta(minutes=5),
                    decision_at,
                    decision_at,
                ),
                decision_at,
                data_version=experiment.data_version,
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
    firewall, hypothesis_test_id = build_synthetic_firewall(ledger, strategy, experiment)
    runner = ChronologicalValidationRunner(ledger, firewall)
    result = runner.run(
        mode=ValidationMode.CONFIRMATORY,
        strategy=strategy,
        experiment=experiment,
        artifact_identity_id=strategy.identity_id,
        artifact_code_hash=strategy.code_hash,
        dataset_class=DatasetClass.DEVELOPMENT,
        inputs=tuple(inputs),
        disposition=ValidationDisposition.CONFIRMED,
        hypothesis_test_id=hypothesis_test_id,
        execution_observations=tuple(observations),
        execution_cutoff_at=at(9, 30),
        execution_assumptions=execution_assumptions,
        order_specifications=tuple(specifications),
        capital_snapshot=initial_snapshot or CapitalSnapshot(starting_capital),
        capital_margin_assumptions=capital_assumptions,
        mark_observations=(() if mark is None else (mark,)),
        forced_liquidation_observations=tuple(liquidation_observations),
        offset_cost_assumptions=offset_costs,
    )
    return result


def materialize(result, session_metadata=None, exchange=None):
    materializer = RoundTripMaterializer(session_metadata, exchange)
    outcomes = result.execution_outcomes
    if result.liquidation_outcome is not None and result.liquidation_outcome.execution_outcome is not None:
        outcomes = outcomes + (result.liquidation_outcome.execution_outcome,)
    return materializer.materialize(result.capital_transitions, outcomes)


def hand_built_snapshot(
    *,
    position_id=None,
    quantity=Decimal("0"),
    average_open_price=Decimal("0"),
    instrument=None,
    direction=None,
    state_at=None,
    trading_day=None,
    realized=Decimal("0"),
    unrealized=Decimal("0"),
    charged=Decimal("0"),
    reserved=Decimal("0"),
    request_id=None,
    concrete_contract_id=None,
):
    return CapitalSnapshot(
        starting_capital=Decimal("100"),
        reserved_margin=reserved,
        charged_costs=charged,
        realized_pnl=realized,
        unrealized_pnl=unrealized,
        position_quantity=quantity,
        average_open_price=average_open_price,
        position_instrument=instrument,
        position_id=position_id,
        position_request_id=request_id,
        execution_assumption_id="exec-assumption-v1" if position_id else None,
        capital_assumption_id="cap-assumption-v1" if position_id else None,
        state_at=state_at,
        concrete_contract_id=concrete_contract_id,
        contract_identity_id="contract-identity-v1" if concrete_contract_id else None,
        contract_master_identity_id="master-v1" if concrete_contract_id else None,
        position_trading_day=trading_day,
        today_quantity=quantity,
        previous_quantity=Decimal("0"),
        position_direction=direction,
    )


def hand_built_open(position_id, *, instrument="TEST", state_at, trading_day, quantity=Decimal("2"), price=Decimal("101.5"), cost=Decimal("0.25")):
    before = hand_built_snapshot(state_at=state_at)
    after = hand_built_snapshot(
        position_id=position_id,
        quantity=quantity,
        average_open_price=price,
        instrument=instrument,
        direction=PositionDirection.LONG,
        state_at=state_at,
        trading_day=trading_day,
        charged=cost,
        reserved=Decimal("10"),
        request_id="open-1",
    )
    return CapitalTransition(
        "open-1",
        before,
        after,
        Decimal("10"),
        cost,
        quantity_change=quantity,
        transition_type="ORDER_EXECUTION",
    )


def hand_built_close(position_id, *, instrument="TEST", state_at, trading_day, quantity=Decimal("2"), average_open_price=Decimal("101.5"), fill=Decimal("108.5"), realized=Decimal("7"), cost=Decimal("1.25"), released=Decimal("10")):
    before = hand_built_snapshot(
        position_id=position_id,
        quantity=quantity,
        average_open_price=average_open_price,
        instrument=instrument,
        direction=PositionDirection.LONG,
        state_at=state_at,
        trading_day=trading_day,
        charged=Decimal("0.25"),
        reserved=released,
        request_id="close-1",
    )
    after = hand_built_snapshot(
        state_at=state_at,
        realized=realized,
        charged=Decimal("0.25") + cost,
    )
    return CapitalTransition(
        "close-1",
        before,
        after,
        Decimal("0"),
        cost,
        quantity_change=-quantity,
        realized_pnl_change=realized,
        released_margin=released,
        transition_type="POSITION_CLOSE",
    )


class CompletedRoundTripTests(unittest.TestCase):
    """Required scenario coverage: one position_id == one completed round trip."""

    def test_open_full_close_is_exactly_one_round_trip(self):
        result = run_lifecycle(
            prices=(100, 110),
            quantities=(1, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE),
        )
        ledger = materialize(result)
        self.assertEqual(ledger.completed_count, 1)
        self.assertEqual(ledger.open_position_ids, ())
        trip = ledger.completed_round_trips[0]
        self.assertEqual(trip.total_opened_quantity, Decimal("1"))
        self.assertEqual(trip.total_closed_quantity, Decimal("1"))
        self.assertEqual(trip.terminal_reason, TERMINAL_REASON_FULL_CLOSE)
        self.assertFalse(trip.forced_liquidation)

    def test_open_add_full_close_is_exactly_one_round_trip(self):
        result = run_lifecycle(
            prices=(100, 105, 110),
            quantities=(2, 3, 5),
            actions=(OrderAction.OPEN, OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, None, CloseOffset.CLOSE),
        )
        ledger = materialize(result)
        self.assertEqual(ledger.completed_count, 1)
        trip = ledger.completed_round_trips[0]
        self.assertEqual(trip.total_opened_quantity, Decimal("5"))
        self.assertEqual(trip.total_closed_quantity, Decimal("5"))
        self.assertEqual(len(trip.opening_transition_references), 2)

    def test_open_partial_close_full_close_is_exactly_one_round_trip(self):
        result = run_lifecycle(
            prices=(100, 110, 112),
            quantities=(2, 1, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE, CloseOffset.CLOSE),
        )
        ledger = materialize(result)
        self.assertEqual(ledger.completed_count, 1)
        trip = ledger.completed_round_trips[0]
        self.assertEqual(trip.total_opened_quantity, Decimal("2"))
        self.assertEqual(trip.total_closed_quantity, Decimal("2"))
        self.assertEqual(len(trip.reducing_transition_references), 2)

    def test_open_add_multiple_partial_closes_full_close_is_exactly_one_round_trip(self):
        result = run_lifecycle(
            prices=(100, 102, 105, 106, 108),
            quantities=(3, 2, 1, 2, 2),
            actions=(
                OrderAction.OPEN,
                OrderAction.OPEN,
                OrderAction.CLOSE,
                OrderAction.CLOSE,
                OrderAction.CLOSE,
            ),
            offsets=(None, None, CloseOffset.CLOSE, CloseOffset.CLOSE, CloseOffset.CLOSE),
        )
        ledger = materialize(result)
        self.assertEqual(ledger.completed_count, 1)
        trip = ledger.completed_round_trips[0]
        self.assertEqual(trip.total_opened_quantity, Decimal("5"))
        self.assertEqual(trip.total_closed_quantity, Decimal("5"))
        self.assertEqual(len(trip.opening_transition_references), 2)
        self.assertEqual(len(trip.reducing_transition_references), 3)

    def test_forced_liquidation_is_terminal_completed_round_trip(self):
        opened = run_lifecycle(
            prices=(100,),
            quantities=(1,),
            actions=(OrderAction.OPEN,),
            starting_capital=Decimal("20"),
        ).capital_transitions[0].after
        mark = MarkObservation(
            "mark-1",
            opened.position_id,
            opened.position_request_id,
            opened.position_instrument,
            at(9, 10),
            at(9, 10),
            Decimal("40"),
        )
        with_mark = run_lifecycle(
            prices=(100,),
            quantities=(1,),
            actions=(OrderAction.OPEN,),
            starting_capital=Decimal("20"),
            mark=mark,
        )
        requirement = with_mark.liquidation_requirement
        self.assertIsNotNone(requirement)
        observation = ExecutionObservation(
            requirement.request_id,
            at(9, 12),
            at(9, 12),
            Decimal("39"),
        )
        result = run_lifecycle(
            prices=(100,),
            quantities=(1,),
            actions=(OrderAction.OPEN,),
            starting_capital=Decimal("20"),
            mark=mark,
            liquidation_observations=(observation,),
        )
        ledger = materialize(result)
        self.assertEqual(ledger.completed_count, 1)
        trip = ledger.completed_round_trips[0]
        self.assertTrue(trip.forced_liquidation)
        self.assertEqual(trip.terminal_reason, TERMINAL_REASON_FORCED_LIQUIDATION)
        self.assertEqual(trip.total_opened_quantity, Decimal("1"))
        self.assertEqual(trip.total_closed_quantity, Decimal("1"))
        self.assertEqual(trip.gross_realized_pnl, Decimal("-64"))

    def test_long_and_short_round_trips(self):
        long_result = run_lifecycle(
            prices=(100, 110),
            quantities=(1, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE),
            directions=(PositionDirection.LONG, PositionDirection.LONG),
        )
        long_trip = materialize(long_result).completed_round_trips[0]
        self.assertIs(long_trip.direction, PositionDirection.LONG)

        short_result = run_lifecycle(
            prices=(100, 90),
            quantities=(1, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE),
            directions=(PositionDirection.SHORT, PositionDirection.SHORT),
        )
        short_trip = materialize(short_result).completed_round_trips[0]
        self.assertIs(short_trip.direction, PositionDirection.SHORT)
        self.assertEqual(short_trip.gross_realized_pnl, Decimal("7"))

    def test_partial_closes_do_not_inflate_trade_count(self):
        partial = run_lifecycle(
            prices=(100, 110, 112),
            quantities=(2, 1, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE, CloseOffset.CLOSE),
        )
        single = run_lifecycle(
            prices=(100, 112),
            quantities=(2, 2),
            actions=(OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE),
        )
        partial_ledger = materialize(partial)
        single_ledger = materialize(single)
        # Partial closes aggregate into the SAME single round trip: N == 1,
        # identical to a single full close, never 2 trades.
        self.assertEqual(partial_ledger.completed_count, 1)
        self.assertEqual(single_ledger.completed_count, 1)

    def test_gross_realized_pnl_equals_aggregation_of_authoritative_realized_transitions(self):
        result = run_lifecycle(
            prices=(100, 102, 105, 106, 108),
            quantities=(3, 2, 1, 2, 2),
            actions=(
                OrderAction.OPEN,
                OrderAction.OPEN,
                OrderAction.CLOSE,
                OrderAction.CLOSE,
                OrderAction.CLOSE,
            ),
            offsets=(None, None, CloseOffset.CLOSE, CloseOffset.CLOSE, CloseOffset.CLOSE),
        )
        trip = materialize(result).completed_round_trips[0]
        reducing_transitions = [
            transition
            for transition in result.capital_transitions
            if transition.quantity_change < 0
        ]
        expected_gross = sum(
            (transition.realized_pnl_change for transition in reducing_transitions),
            Decimal("0"),
        )
        self.assertEqual(trip.gross_realized_pnl, expected_gross)
        self.assertEqual(trip.gross_realized_pnl, Decimal("14"))
        # Final realized PnL on the flat snapshot is the same realized total.
        self.assertEqual(result.final_capital_snapshot.realized_pnl, Decimal("14"))

    def test_cost_charged_exactly_once(self):
        result = run_lifecycle(
            prices=(100, 105, 110),
            quantities=(2, 3, 5),
            actions=(OrderAction.OPEN, OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, None, CloseOffset.CLOSE),
        )
        trip = materialize(result).completed_round_trips[0]
        transitions = result.capital_transitions
        expected = sum((transition.required_cost for transition in transitions), Decimal("0"))
        self.assertEqual(trip.charged_costs, expected)
        # Cross-check: the single additive-cost authority agrees with the
        # constrained execution outcomes (each filled execution charged once).
        outcome_total = sum(
            (
                outcome.total_cost
                for outcome in result.execution_outcomes
                if outcome.status is FillStatus.FILLED and outcome.total_cost is not None
            ),
            Decimal("0"),
        )
        self.assertEqual(trip.charged_costs, outcome_total)
        self.assertEqual(trip.charged_costs, Decimal("5.75"))
        self.assertEqual(trip.gross_realized_pnl, Decimal("20"))
        self.assertEqual(trip.net_realized_result, Decimal("14.25"))

    def test_full_close_total_quantity_identity_is_balanced(self):
        result = run_lifecycle(
            prices=(100, 102, 105, 106, 108),
            quantities=(3, 2, 1, 2, 2),
            actions=(
                OrderAction.OPEN,
                OrderAction.OPEN,
                OrderAction.CLOSE,
                OrderAction.CLOSE,
                OrderAction.CLOSE,
            ),
            offsets=(None, None, CloseOffset.CLOSE, CloseOffset.CLOSE, CloseOffset.CLOSE),
        )
        trip = materialize(result).completed_round_trips[0]
        self.assertEqual(trip.total_opened_quantity, trip.total_closed_quantity)
        self.assertEqual(trip.total_opened_quantity, Decimal("5"))

    def test_incomplete_open_position_is_not_materialized_as_completed(self):
        result = run_lifecycle(
            prices=(100, 110),
            quantities=(2, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE),
        )
        ledger = materialize(result)
        self.assertEqual(ledger.completed_count, 0)
        self.assertEqual(len(ledger.open_position_ids), 1)
        self.assertEqual(result.final_capital_snapshot.position_quantity, Decimal("1"))

    def test_distinct_position_ids_remain_distinct_round_trips(self):
        result = run_lifecycle(
            prices=(100, 110, 105, 112),
            quantities=(1, 1, 1, 1),
            actions=(
                OrderAction.OPEN,
                OrderAction.CLOSE,
                OrderAction.OPEN,
                OrderAction.CLOSE,
            ),
            offsets=(None, CloseOffset.CLOSE, None, CloseOffset.CLOSE),
        )
        ledger = materialize(result)
        self.assertEqual(ledger.completed_count, 2)
        first, second = ledger.completed_round_trips
        self.assertNotEqual(first.position_id, second.position_id)
        self.assertEqual(len({first.position_id, second.position_id}), 2)

    def test_deterministic_identity_is_stable_for_equivalent_ordered_evidence(self):
        kwargs = dict(
            prices=(100, 105, 110),
            quantities=(2, 3, 5),
            actions=(OrderAction.OPEN, OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, None, CloseOffset.CLOSE),
        )
        first = materialize(run_lifecycle(**kwargs))
        second = materialize(run_lifecycle(**kwargs))
        self.assertEqual(first.identity_id, second.identity_id)
        self.assertEqual(
            first.completed_round_trips[0].ledger_identity,
            second.completed_round_trips[0].ledger_identity,
        )

    def test_material_change_to_evidence_changes_identity(self):
        base = dict(
            prices=(100, 105, 110),
            quantities=(2, 3, 5),
            actions=(OrderAction.OPEN, OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, None, CloseOffset.CLOSE),
        )
        baseline = materialize(run_lifecycle(**base)).completed_round_trips[0]
        changed = dict(base)
        changed["prices"] = (100, 105, 112)
        altered = materialize(run_lifecycle(**changed)).completed_round_trips[0]
        self.assertNotEqual(altered.ledger_identity, baseline.ledger_identity)


class RoundTripDayWeekTests(unittest.TestCase):
    """SessionMetadata is the single official trading-day/week authority (TD-001)."""

    MONDAY = date(2025, 6, 16)
    FRIDAY = date(2025, 6, 13)

    def setUp(self):
        self.session = SessionMetadata(
            "round-trip-session-v1",
            (
                SessionWindow(
                    "SHFE",
                    "CU2507",
                    self.MONDAY,
                    datetime(2025, 6, 13, 21, 0, tzinfo=CN),
                    datetime(2025, 6, 14, 1, 0, tzinfo=CN),
                    "NIGHT",
                ),
                SessionWindow(
                    "SHFE",
                    "CU2507",
                    self.MONDAY,
                    datetime(2025, 6, 16, 9, 0, tzinfo=CN),
                    datetime(2025, 6, 16, 15, 30, tzinfo=CN),
                    "DAY",
                ),
            ),
        )

    def test_entry_and_exit_trading_day_use_session_metadata(self):
        pos = "round-trip-position-1"
        opened_at = datetime(2025, 6, 16, 9, 36, tzinfo=CN)
        closed_at = datetime(2025, 6, 16, 10, 36, tzinfo=CN)
        open_transition = hand_built_open(
            pos, state_at=opened_at, trading_day=self.MONDAY, instrument="CU2507"
        )
        close_transition = hand_built_close(
            pos,
            state_at=closed_at,
            trading_day=self.MONDAY,
            quantity=Decimal("2"),
            instrument="CU2507",
        )
        ledger = RoundTripMaterializer(self.session, "SHFE").materialize(
            (open_transition, close_transition)
        )
        trip = ledger.completed_round_trips[0]
        # Official day resolved through SessionMetadata, not the raw timestamp.
        self.assertEqual(
            trip.entry_official_trading_day,
            self.session.trading_day_at("SHFE", "CU2507", opened_at),
        )
        self.assertEqual(
            trip.exit_official_trading_day,
            self.session.trading_day_at("SHFE", "CU2507", closed_at),
        )
        self.assertEqual(trip.entry_official_trading_day, self.MONDAY)
        self.assertEqual(trip.exit_official_trading_day, self.MONDAY)
        monday_week = (self.MONDAY.isocalendar()[0], self.MONDAY.isocalendar()[1])
        self.assertEqual(trip.entry_official_trading_week, monday_week)
        self.assertEqual(trip.exit_official_trading_week, monday_week)

    def test_night_session_timestamp_maps_to_official_trading_day_and_week(self):
        pos = "round-trip-position-night"
        # Civil Friday 21:36 belongs to the night session that opens for the
        # official trading day Monday 2025-06-16.
        opened_at = datetime(2025, 6, 13, 21, 36, tzinfo=CN)
        closed_at = datetime(2025, 6, 16, 9, 36, tzinfo=CN)
        open_transition = hand_built_open(
            pos,
            state_at=opened_at,
            trading_day=self.MONDAY,
            instrument="CU2507",
        )
        close_transition = hand_built_close(
            pos,
            state_at=closed_at,
            trading_day=self.MONDAY,
            quantity=Decimal("2"),
            instrument="CU2507",
        )
        ledger = RoundTripMaterializer(self.session, "SHFE").materialize(
            (open_transition, close_transition)
        )
        trip = ledger.completed_round_trips[0]
        # Official day follows the trading-day identity, NOT the civil date.
        self.assertEqual(trip.entry_official_trading_day, self.MONDAY)
        self.assertNotEqual(trip.entry_official_trading_day, self.FRIDAY)
        # Weekly attribution follows the official day's ISO week (week 25 for
        # Monday 2025-06-16), not the civil Friday week (week 24).
        monday_week = (self.MONDAY.isocalendar()[0], self.MONDAY.isocalendar()[1])
        friday_week = (self.FRIDAY.isocalendar()[0], self.FRIDAY.isocalendar()[1])
        self.assertEqual(trip.entry_official_trading_week, monday_week)
        self.assertNotEqual(trip.entry_official_trading_week, friday_week)

    def test_session_metadata_with_runner_output_uses_official_day(self):
        # Integration: transitions produced by the authoritative runner are
        # mapped through SessionMetadata and must agree with the snapshot days.
        result = run_lifecycle(
            prices=(100, 110),
            quantities=(1, 1),
            actions=(OrderAction.OPEN, OrderAction.CLOSE),
            offsets=(None, CloseOffset.CLOSE),
        )
        day_session = SessionMetadata(
            "round-trip-day-v1",
            (
                SessionWindow(
                    "SHFE",
                    "TEST",
                    DAY,
                    at(9, 0),
                    at(15, 30),
                    "DAY",
                ),
            ),
        )
        ledger = materialize(result, session_metadata=day_session, exchange="SHFE")
        trip = ledger.completed_round_trips[0]
        self.assertEqual(trip.entry_official_trading_day, DAY)
        self.assertEqual(trip.exit_official_trading_day, DAY)


class RoundTripLedgerGuardTests(unittest.TestCase):
    """Fail-closed lifecycle integrity and determinism guards."""

    def test_incomplete_position_is_reported_but_not_completed(self):
        pos = "round-trip-position-open"
        opened_at = datetime(2025, 6, 16, 9, 36, tzinfo=CN)
        open_transition = hand_built_open(
            pos, state_at=opened_at, trading_day=DAY, quantity=Decimal("2")
        )
        ledger = RoundTripMaterializer().materialize((open_transition,))
        self.assertEqual(ledger.completed_count, 0)
        self.assertEqual(ledger.open_position_ids, (pos,))

    def test_reopening_completed_position_id_fails_closed(self):
        pos = "round-trip-position-reused"
        opened_at = datetime(2025, 6, 16, 9, 36, tzinfo=CN)
        closed_at = datetime(2025, 6, 16, 10, 36, tzinfo=CN)
        open_transition = hand_built_open(pos, state_at=opened_at, trading_day=DAY)
        close_transition = hand_built_close(
            pos, state_at=closed_at, trading_day=DAY, quantity=Decimal("2")
        )
        reopened = hand_built_open(pos, state_at=datetime(2025, 6, 16, 11, 36, tzinfo=CN), trading_day=DAY)
        with self.assertRaisesRegex(ValueError, "ONE position_id == ONE"):
            RoundTripMaterializer().materialize((open_transition, close_transition, reopened))

    def test_merging_unrelated_contract_positions_fails_closed(self):
        pos = "round-trip-position-roll"
        opened_at = datetime(2025, 6, 16, 9, 36, tzinfo=CN)
        open_transition = hand_built_open(pos, state_at=opened_at, trading_day=DAY, instrument="CU2507")
        # A second contract instrument must not silently merge into the same round trip.
        add_after = hand_built_snapshot(
            position_id=pos,
            quantity=Decimal("3"),
            average_open_price=Decimal("103"),
            instrument="CU2509",
            direction=PositionDirection.LONG,
            state_at=datetime(2025, 6, 16, 10, 0, tzinfo=CN),
            trading_day=DAY,
            charged=Decimal("0.50"),
            reserved=Decimal("15"),
            request_id="add-1",
        )
        add_transition = CapitalTransition(
            "add-1",
            hand_built_snapshot(
                position_id=pos,
                quantity=Decimal("2"),
                average_open_price=Decimal("101.5"),
                instrument="CU2507",
                direction=PositionDirection.LONG,
                state_at=datetime(2025, 6, 16, 9, 40, tzinfo=CN),
                trading_day=DAY,
                charged=Decimal("0.25"),
                reserved=Decimal("10"),
                request_id="open-1",
            ),
            add_after,
            Decimal("5"),
            Decimal("0.25"),
            quantity_change=Decimal("1"),
            transition_type="ORDER_EXECUTION",
        )
        with self.assertRaisesRegex(ValueError, "merge unrelated contract positions"):
            RoundTripMaterializer().materialize((open_transition, add_transition))

    def test_out_of_order_transitions_fail_closed(self):
        pos = "round-trip-position-order"
        opened_at = datetime(2025, 6, 16, 9, 36, tzinfo=CN)
        closed_at = datetime(2025, 6, 16, 10, 36, tzinfo=CN)
        open_transition = hand_built_open(pos, state_at=opened_at, trading_day=DAY)
        close_transition = hand_built_close(
            pos, state_at=closed_at, trading_day=DAY, quantity=Decimal("2")
        )
        with self.assertRaisesRegex(ValueError, r"lifecycle \(chronological\) order"):
            RoundTripMaterializer().materialize((close_transition, open_transition))

    def test_outcome_cost_mismatch_fails_closed(self):
        pos = "round-trip-position-cost"
        opened_at = datetime(2025, 6, 16, 9, 36, tzinfo=CN)
        open_transition = hand_built_open(pos, state_at=opened_at, trading_day=DAY)
        from src.validation_runner import ExecutionOutcome

        mismatched = ExecutionOutcome(
            "open-1",
            FillStatus.FILLED,
            opened_at,
            "exec-assumption-v1",
            Decimal("101.5"),
            Decimal("99"),
            "TRADABLE_OBSERVATION",
        )
        with self.assertRaisesRegex(ValueError, "single additive-cost authority"):
            RoundTripMaterializer().materialize((open_transition,), (mismatched,))

    def test_session_day_outside_published_windows_fails_closed(self):
        session = SessionMetadata(
            "round-trip-session-narrow-v1",
            (
                SessionWindow(
                    "SHFE",
                    "TEST",
                    DAY,
                    datetime(2025, 6, 16, 9, 0, tzinfo=CN),
                    datetime(2025, 6, 16, 10, 0, tzinfo=CN),
                    "DAY",
                ),
            ),
        )
        pos = "round-trip-position-window"
        opened_at = datetime(2025, 6, 16, 9, 36, tzinfo=CN)
        closed_at = datetime(2025, 6, 16, 11, 36, tzinfo=CN)
        open_transition = hand_built_open(pos, state_at=opened_at, trading_day=DAY)
        close_transition = hand_built_close(
            pos, state_at=closed_at, trading_day=DAY, quantity=Decimal("2")
        )
        with self.assertRaisesRegex(ValueError, "fail closed instead of guessing"):
            RoundTripMaterializer(session, "SHFE").materialize((open_transition, close_transition))

    def test_session_day_inconsistent_with_snapshot_fails_closed(self):
        pos = "round-trip-position-inconsistent"
        opened_at = datetime(2025, 6, 16, 9, 36, tzinfo=CN)
        # Snapshot claims a different official day than SessionMetadata resolves.
        open_transition = hand_built_open(
            pos, state_at=opened_at, trading_day=date(2025, 6, 15)
        )
        with self.assertRaisesRegex(ValueError, "inconsistent"):
            RoundTripMaterializer(self.session_for_test(), "SHFE").materialize((open_transition,))

    @staticmethod
    def session_for_test():
        return SessionMetadata(
            "round-trip-session-guard-v1",
            (
                SessionWindow(
                    "SHFE",
                    "TEST",
                    date(2025, 6, 16),
                    datetime(2025, 6, 16, 9, 0, tzinfo=CN),
                    datetime(2025, 6, 16, 15, 30, tzinfo=CN),
                    "DAY",
                ),
            ),
        )

    def test_flat_noop_transition_cannot_carry_cost_or_pnl(self):
        pos = "round-trip-position-noop"
        opened_at = datetime(2025, 6, 16, 9, 36, tzinfo=CN)
        open_transition = hand_built_open(pos, state_at=opened_at, trading_day=DAY)
        # A transition with no position identity must be a pure flat no-op.
        bad_flat = CapitalTransition(
            "noop-1",
            hand_built_snapshot(state_at=opened_at),
            hand_built_snapshot(state_at=opened_at),
            Decimal("0"),
            Decimal("1"),
            realized_pnl_change=Decimal("2"),
        )
        with self.assertRaisesRegex(ValueError, "flat no-op"):
            RoundTripMaterializer().materialize((open_transition, bad_flat))


if __name__ == "__main__":
    unittest.main()

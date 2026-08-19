"""Package E execution/capital/round-trip defect reproduction.

PACKAGE_E_PREFLIGHT_EXECUTION_DEFECT_REPRODUCTION_V0_1

This script is a DEFECT REPRODUCTION task, not a repair.  It:
- does NOT modify any production source under ``src/``;
- does NOT decide any new trading semantics;
- uses synthetic data only (no candidate market data, no firewall outcome path);
- calls the lowest-level authoritative classes/functions directly:
  ``ChronologicalValidationRunner._apply_capital_constraints`` /
  ``_apply_marks`` / ``_evaluate_forced_liquidation``,
  ``RoundTripMaterializer`` / ``RoundTripLedger``,
  ``bootstrap_semantics.TradingState``,
  and ``PortfolioCoordinator._resolve_candidates`` (structural check only).

Output convention (per finding):
    E<NN>=REPRODUCED
    E<NN>=NOT_REPRODUCED
    E<NN>=AUDIT_FINDING_INACCURATE

Exit code is always 0 when the script completes its diagnostics; a finding that
does not reproduce is reported as AUDIT_FINDING_INACCURATE rather than as an
error, and the default test suite is never touched.

Usage:
    python tools/reproduce_package_e_findings.py
"""

from __future__ import annotations

import os
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

# Allow ``python tools/reproduce_package_e_findings.py`` from the repo root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.bootstrap_semantics import BrokerEvent, TradingState  # noqa: E402
from src.contract_semantics import (  # noqa: E402
    CloseOffset,
    ContractMappingSchedule,
    ContractMaster,
    ContractSpecification,
    OffsetCostAssumptions,
    OrderAction,
    PositionDirection,
)
from src.data_substrate import CompletedBar, SessionMetadata, SessionWindow  # noqa: E402
from src.portfolio_semantics import (  # noqa: E402
    PortfolioCandidate,
    PortfolioConflictPolicy,
    PortfolioCoordinator,
    PortfolioMember,
    PortfolioRequest,
    SharedCapitalPolicy,
)
from src.round_trip_ledger import RoundTripLedger, RoundTripMaterializer  # noqa: E402
from src.strategy_evidence import (  # noqa: E402
    DatasetClass,
    ExperimentIdentity,
    LifecycleState,
    StrategyIdentity,
    TypedParameter,
)
from src.validation_runner import (  # noqa: E402
    CapitalMarginAssumptions,
    CapitalSnapshot,
    CapitalTransition,
    ChronologicalValidationRunner,
    ExecutionAssumptions,
    ExecutionObservation,
    ExecutionOutcome,
    FillStatus,
    ForcedLiquidationRequirement,
    MarkObservation,
    OrderSpecification,
    ValidationDisposition,
    ValidationInput,
    ValidationMode,
)

CN = ZoneInfo("Asia/Shanghai")

# Synthetic official trading days (2025-06-16 is a Monday).
D1 = date(2025, 6, 16)
D2 = date(2025, 6, 17)
D3 = date(2025, 6, 18)
D_MONDAY_NEXT = date(2025, 6, 23)  # next Monday (week 26 vs week 25 for D1)

RESULTS: dict[str, str] = {}


def at(day: date, hour: int, minute: int) -> datetime:
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=CN)


def finish(key: str, status: str) -> None:
    RESULTS[key] = status
    print(f"{key}={status}")


# ---------------------------------------------------------------------------
# Shared synthetic fixtures
# ---------------------------------------------------------------------------

def execution_assumptions() -> ExecutionAssumptions:
    return ExecutionAssumptions("repro-exec-v1", Decimal("0.5"), Decimal("0.25"))


def capital_assumptions(contract_multiplier: Decimal = Decimal("1")) -> CapitalMarginAssumptions:
    return CapitalMarginAssumptions(
        "repro-capital-v1",
        contract_multiplier,
        Decimal("0.1"),
        "SYNTH",
        Decimal("0.05"),
    )


def offset_costs() -> OffsetCostAssumptions:
    # close-today and close-previous fees deliberately differ.
    return OffsetCostAssumptions(
        "repro-offset-v1",
        Decimal("1"),
        Decimal("2"),
    )


def make_input(request_id: str, instrument: str, trading_day: date, decision_at: datetime) -> ValidationInput:
    return ValidationInput(
        request_id,
        CompletedBar(
            instrument,
            trading_day,
            decision_at - timedelta(minutes=5),
            decision_at,
            decision_at,
        ),
        decision_at,
        "repro-data-v1",
    )


def make_filled_outcome(
    request_id: str,
    evaluated_at: datetime,
    exec_assumption_id: str,
    fill_price: Decimal,
    total_cost: Decimal,
    cap_assumption_id: str,
) -> ExecutionOutcome:
    return ExecutionOutcome(
        request_id,
        FillStatus.FILLED,
        evaluated_at,
        exec_assumption_id,
        fill_price,
        total_cost,
        "TRADABLE_OBSERVATION",
        cap_assumption_id,
    )


def make_open_snapshot(
    *,
    position_id: str,
    request_id: str,
    instrument: str,
    quantity: Decimal,
    average_open_price: Decimal,
    state_at: datetime,
    exec_assumptions: ExecutionAssumptions,
    cap_assumptions: CapitalMarginAssumptions,
    trading_day: date | None = D1,
    direction: PositionDirection = PositionDirection.LONG,
    unrealized: Decimal = Decimal("0"),
    today: Decimal | None = None,
    previous: Decimal = Decimal("0"),
    reserved: Decimal | None = None,
    charged: Decimal = Decimal("0.25"),
    realized: Decimal = Decimal("0"),
    concrete_contract_id: str | None = None,
    contract_identity_id: str | None = None,
    contract_master_identity_id: str | None = None,
    mapping_schedule_identity_id: str | None = None,
    mapping_entry_identity_id: str | None = None,
) -> CapitalSnapshot:
    if today is None:
        today = quantity
    if reserved is None:
        reserved = average_open_price * quantity * cap_assumptions.contract_multiplier * cap_assumptions.initial_margin_rate
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
        execution_assumption_id=exec_assumptions.identity_id,
        capital_assumption_id=cap_assumptions.identity_id,
        state_at=state_at,
        concrete_contract_id=concrete_contract_id,
        contract_identity_id=contract_identity_id,
        contract_master_identity_id=contract_master_identity_id,
        mapping_schedule_identity_id=mapping_schedule_identity_id,
        mapping_entry_identity_id=mapping_entry_identity_id,
        position_trading_day=trading_day,
        today_quantity=today,
        previous_quantity=previous,
        position_direction=direction,
    )


# ---------------------------------------------------------------------------
# E-01: ADD resets unrealized PnL to zero
# ---------------------------------------------------------------------------

def reproduce_e01() -> str:
    exec_a = execution_assumptions()
    cap_a = capital_assumptions()

    # Existing position: LONG 1 lot @ 100.
    snapshot = make_open_snapshot(
        position_id="e01-pos",
        request_id="e01-open",
        instrument="TEST",
        quantity=Decimal("1"),
        average_open_price=Decimal("100"),
        state_at=at(D1, 9, 5),
        exec_assumptions=exec_a,
        cap_assumptions=cap_a,
    )

    # 1) Prove existing unrealized is positive with a valid mark @ 110.
    mark = MarkObservation(
        "e01-mark", "e01-pos", "e01-open", "TEST",
        at(D1, 9, 6), at(D1, 9, 6), Decimal("110"),
    )
    mark_transitions, _ = ChronologicalValidationRunner._apply_marks(
        (mark,), snapshot, at(D1, 9, 30), cap_a,
    )
    marked = mark_transitions[-1].after
    print("[E-01] mark@110 -> existing unrealized_pnl =", marked.unrealized_pnl)
    existing_positive = marked.unrealized_pnl == Decimal("10")

    # 2) ADD 1 lot @ 110 through the lowest-level capital transition path.
    # The snapshot carries the positive unrealized of the marked state.  The
    # latest_mark_reference is left unset because the full-lifecycle runner
    # additionally blocks ADD-after-mark (a separate guard); the ADD branch
    # itself unconditionally writes unrealized_pnl=0 (see NOTES in evidence).
    add_snapshot = make_open_snapshot(
        position_id="e01-pos",
        request_id="e01-open",
        instrument="TEST",
        quantity=Decimal("1"),
        average_open_price=Decimal("100"),
        state_at=at(D1, 9, 5),
        exec_assumptions=exec_a,
        cap_assumptions=cap_a,
        unrealized=Decimal("10"),  # same positive value the mark produced
    )
    add_outcome = make_filled_outcome(
        "e01-add", at(D1, 9, 11), exec_a.identity_id, Decimal("110"), Decimal("0.25"), cap_a.identity_id,
    )
    add_spec = OrderSpecification("e01-add", Decimal("1"))  # OPEN / ADD
    add_input = make_input("e01-add", "TEST", D1, at(D1, 9, 10))
    constrained, transitions = ChronologicalValidationRunner._apply_capital_constraints(
        (add_outcome,), (add_spec,), (add_input,), add_snapshot, cap_a, exec_a,
    )
    after = transitions[0].after
    print("[E-01] ADD transition after -> unrealized_pnl =", after.unrealized_pnl)
    print(
        "[E-01] cash=", after.cash_balance,
        "reserved_margin=", after.reserved_margin,
        "quantity=", after.position_quantity,
        "average_open_price=", after.average_open_price,
    )
    reset_to_zero = after.unrealized_pnl == 0

    # 3) Supporting lifecycle-reachable path (no mark): two sequential ADDs.
    # At the second fill price the first tranche already has unrealized gain,
    # but the snapshot reports 0.
    reachable = make_open_snapshot(
        position_id="e01-pos-b",
        request_id="e01-open-b",
        instrument="TEST",
        quantity=Decimal("1"),
        average_open_price=Decimal("100"),
        state_at=at(D1, 9, 5),
        exec_assumptions=exec_a,
        cap_assumptions=cap_a,
    )
    add_outcome_b = make_filled_outcome(
        "e01-add-b", at(D1, 9, 11), exec_a.identity_id, Decimal("110"), Decimal("0.25"), cap_a.identity_id,
    )
    add_spec_b = OrderSpecification("e01-add-b", Decimal("1"))
    add_input_b = make_input("e01-add-b", "TEST", D1, at(D1, 9, 10))
    _, transitions_b = ChronologicalValidationRunner._apply_capital_constraints(
        (add_outcome_b,), (add_spec_b,), (add_input_b,), reachable, cap_a, exec_a,
    )
    after_b = transitions_b[0].after
    print(
        "[E-01] two-ADD reachable path -> after unrealized_pnl =", after_b.unrealized_pnl,
        "(first tranche fair value at 110 = +10)",
    )

    # 4) Short mirror (the ADD branch is shared for both directions).
    short_snapshot = make_open_snapshot(
        position_id="e01-pos-short",
        request_id="e01-open-short",
        instrument="TEST",
        quantity=Decimal("1"),
        average_open_price=Decimal("100"),
        state_at=at(D1, 9, 5),
        exec_assumptions=exec_a,
        cap_assumptions=cap_a,
        direction=PositionDirection.SHORT,
        unrealized=Decimal("-10"),  # mark @ 90 for a short
    )
    short_outcome = make_filled_outcome(
        "e01-add-short", at(D1, 9, 11), exec_a.identity_id, Decimal("90"), Decimal("0.25"), cap_a.identity_id,
    )
    short_spec = OrderSpecification("e01-add-short", Decimal("1"), direction=PositionDirection.SHORT)
    short_input = make_input("e01-add-short", "TEST", D1, at(D1, 9, 10))
    _, transitions_short = ChronologicalValidationRunner._apply_capital_constraints(
        (short_outcome,), (short_spec,), (short_input,), short_snapshot, cap_a, exec_a,
    )
    after_short = transitions_short[0].after
    print("[E-01] short mirror after -> unrealized_pnl =", after_short.unrealized_pnl)

    if existing_positive and reset_to_zero and after_short.unrealized_pnl == 0:
        return "REPRODUCED"
    return "AUDIT_FINDING_INACCURATE"


# ---------------------------------------------------------------------------
# E-02: forced liquidation cannot cleanly cross to the next official trading day
# ---------------------------------------------------------------------------

def _shfe_contract(offset_meta_identity: str) -> ContractSpecification:
    return ContractSpecification(
        exchange="SHFE",
        product_family="CU",
        instrument_id="CU2507",
        listed_at=at(D1, 8, 0),
        deactivated_at=at(D3, 0, 0),
        contract_multiplier=Decimal("1"),
        minimum_price_tick=Decimal("0.5"),
        currency="CNY",
        unit="TON",
        price_limit_rule_identity=None,
        offset_fee_metadata_identity=offset_meta_identity,
        metadata_version="repro-contract-v1",
    )


def reproduce_e02() -> str:
    exec_a = execution_assumptions()
    cap_a = capital_assumptions()
    contract = _shfe_contract(offset_costs().identity_id)
    master = ContractMaster("repro-master-e02", (contract,))
    sessions = SessionMetadata(
        "repro-sessions-e02",
        (
            SessionWindow("SHFE", "CU2507", D1, at(D1, 9, 0), at(D1, 10, 0), "DAY"),
            SessionWindow("SHFE", "CU2507", D2, at(D2, 9, 0), at(D2, 10, 0), "DAY"),
        ),
    )

    # Contract-bound LONG position opened on official trading day D1.
    snapshot = make_open_snapshot(
        position_id="e02-pos",
        request_id="e02-open",
        instrument="CU2507",
        quantity=Decimal("1"),
        average_open_price=Decimal("100"),
        state_at=at(D1, 9, 5),
        exec_assumptions=exec_a,
        cap_assumptions=cap_a,
        trading_day=D1,
        concrete_contract_id="CU2507",
        contract_identity_id=contract.identity_id,
        contract_master_identity_id=master.identity_id,
        mapping_schedule_identity_id="repro-mapping-schedule-e02",
        mapping_entry_identity_id="repro-mapping-entry-e02",
    )

    # Maintenance breach near the D1 session tail.
    mark = MarkObservation(
        "e02-mark", "e02-pos", "e02-open", "CU2507",
        at(D1, 9, 55), at(D1, 9, 55), Decimal("0.2"),
    )
    mark_transitions, requirement = ChronologicalValidationRunner._apply_marks(
        (mark,), snapshot, at(D1, 9, 59), cap_a,
    )
    if requirement is None:
        print("[E-02] mark did not breach maintenance; cannot build requirement")
        return "AUDIT_FINDING_INACCURATE"
    final = mark_transitions[-1].after
    print("[E-02] breach eligible_at =", requirement.eligible_at)

    # The declared rule is FULL_POSITION_NEXT_TRADABLE_OBSERVATION_V1:
    # the next tradable observation is the D2 official trading-day session.
    observation = ExecutionObservation(
        requirement.request_id,
        at(D2, 9, 5),
        at(D2, 9, 5),
        Decimal("100"),
        tradable=True,
        concrete_contract_id="CU2507",
    )
    d2_trading_day = sessions.trading_day_at("SHFE", "CU2507", at(D2, 9, 5))
    print("[E-02] observation session trading day =", d2_trading_day)
    print("[E-02] snapshot.position_trading_day =", final.position_trading_day)

    try:
        ChronologicalValidationRunner._evaluate_forced_liquidation(
            requirement,
            (observation,),
            final,
            at(D2, 9, 30),
            exec_a,
            cap_a,
            master,
            sessions,
        )
        print("[E-02] liquidation accepted a next-trading-day observation")
        return "AUDIT_FINDING_INACCURATE"
    except ValueError as exc:
        if "outside the position trading day" in str(exc):
            print("[E-02] liquidation path REJECTED the D2 observation:", exc)
            return "REPRODUCED"
        print("[E-02] unexpected error:", exc)
        return "AUDIT_FINDING_INACCURATE"


# ---------------------------------------------------------------------------
# E-03: forced liquidation omits close-today/close-previous offset fees
# ---------------------------------------------------------------------------

def reproduce_e03() -> str:
    exec_a = execution_assumptions()
    cap_a = capital_assumptions()
    offset = offset_costs()
    contract = _shfe_contract(offset.identity_id)
    master = ContractMaster("repro-master-e03", (contract,))
    sessions = SessionMetadata(
        "repro-sessions-e03",
        (SessionWindow("SHFE", "CU2507", D1, at(D1, 9, 0), at(D1, 10, 0), "DAY"),),
    )

    # --- ordinary CLOSE_TODAY cost components ---
    close_snapshot = make_open_snapshot(
        position_id="e03-pos",
        request_id="e03-open",
        instrument="TEST",
        quantity=Decimal("1"),
        average_open_price=Decimal("100"),
        state_at=at(D1, 9, 5),
        exec_assumptions=exec_a,
        cap_assumptions=cap_a,
        today=Decimal("1"),
        previous=Decimal("0"),
    )
    close_outcome = make_filled_outcome(
        "e03-close", at(D1, 9, 11), exec_a.identity_id, Decimal("101"), Decimal("0.25"), cap_a.identity_id,
    )
    close_spec = OrderSpecification(
        "e03-close", Decimal("1"), OrderAction.CLOSE, CloseOffset.CLOSE_TODAY,
    )
    close_input = make_input("e03-close", "TEST", D1, at(D1, 9, 10))
    constrained, _ = ChronologicalValidationRunner._apply_capital_constraints(
        (close_outcome,), (close_spec,), (close_input,), close_snapshot, cap_a, exec_a,
        offset_cost_assumptions=offset,
    )
    ordinary = constrained[0]
    print(
        "[E-03] ordinary CLOSE total_cost =", ordinary.total_cost,
        "resolved_close_offset =", ordinary.resolved_close_offset,
        "offset_cost_assumption_id =", ordinary.offset_cost_assumption_id,
    )

    # --- forced liquidation cost components ---
    forced_snapshot = make_open_snapshot(
        position_id="e03-pos-liq",
        request_id="e03-open-liq",
        instrument="CU2507",
        quantity=Decimal("1"),
        average_open_price=Decimal("100"),
        state_at=at(D1, 9, 5),
        exec_assumptions=exec_a,
        cap_assumptions=cap_a,
        trading_day=D1,
        today=Decimal("1"),
        previous=Decimal("0"),
        concrete_contract_id="CU2507",
        contract_identity_id=contract.identity_id,
        contract_master_identity_id=master.identity_id,
        mapping_schedule_identity_id="repro-mapping-schedule-e03",
        mapping_entry_identity_id="repro-mapping-entry-e03",
    )
    requirement = ForcedLiquidationRequirement(
        "e03-liq",
        "e03-pos-liq",
        "CU2507",
        Decimal("1"),
        at(D1, 9, 0),
        at(D1, 9, 0),
        "e03-mark-ref",
        cap_a.identity_id,
        contract.identity_id,
        master.identity_id,
        "repro-mapping-entry-e03",
    )
    observation = ExecutionObservation(
        "e03-liq", at(D1, 9, 30), at(D1, 9, 30), Decimal("101"),
        tradable=True, concrete_contract_id="CU2507",
    )
    forced = ChronologicalValidationRunner._evaluate_forced_liquidation(
        requirement, (observation,), forced_snapshot, at(D1, 9, 59),
        exec_a, cap_a, master, sessions,
    )
    forced_outcome = forced.execution_outcome
    print(
        "[E-03] forced liquidation status =", forced_outcome.status.value,
        "total_cost =", forced_outcome.total_cost,
        "resolved_close_offset =", forced_outcome.resolved_close_offset,
        "offset_cost_assumption_id =", forced_outcome.offset_cost_assumption_id,
    )

    forced_only_synthetic_fee = (
        forced_outcome.status is FillStatus.FILLED
        and forced_outcome.total_cost == Decimal("0.25")
        and forced_outcome.total_cost != ordinary.total_cost
        and forced_outcome.resolved_close_offset is None
        and forced_outcome.offset_cost_assumption_id is None
    )
    if forced_only_synthetic_fee:
        return "REPRODUCED"
    return "AUDIT_FINDING_INACCURATE"


# ---------------------------------------------------------------------------
# E-04: generic CLOSE cannot split across today + previous buckets
# ---------------------------------------------------------------------------

def reproduce_e04() -> str:
    exec_a = execution_assumptions()
    cap_a = capital_assumptions()
    offset = offset_costs()

    def run_generic_close(today: Decimal, previous: Decimal, close_qty: Decimal):
        snapshot = make_open_snapshot(
            position_id="e04-pos",
            request_id="e04-open",
            instrument="TEST",
            quantity=today + previous,
            average_open_price=Decimal("100"),
            state_at=at(D1, 9, 5),
            exec_assumptions=exec_a,
            cap_assumptions=cap_a,
            today=today,
            previous=previous,
        )
        outcome = make_filled_outcome(
            "e04-close", at(D1, 9, 11), exec_a.identity_id, Decimal("101"), Decimal("0.25"), cap_a.identity_id,
        )
        spec = OrderSpecification("e04-close", close_qty, OrderAction.CLOSE, CloseOffset.CLOSE)
        inp = make_input("e04-close", "TEST", D1, at(D1, 9, 10))
        return ChronologicalValidationRunner._apply_capital_constraints(
            (outcome,), (spec,), (inp,), snapshot, cap_a, exec_a,
            offset_cost_assumptions=offset,
        )

    # Case 1: today=1, previous=2, close=2 -> previous bucket individually
    # sufficient -> current code resolves CLOSE_PREVIOUS and succeeds.
    case1_ok = True
    case1_offset = None
    try:
        constrained, _ = run_generic_close(Decimal("1"), Decimal("2"), Decimal("2"))
        case1_offset = constrained[0].resolved_close_offset
    except ValueError as exc:
        case1_ok = False
        print("[E-04] case today=1/previous=2/close=2 raised:", exc)
    print("[E-04] case today=1/previous=2/close=2 -> resolved_offset =", case1_offset, "succeeded =", case1_ok)

    # Case 2: today=1, previous=1, close=2 -> neither bucket individually
    # sufficient, combined quantity exactly sufficient -> current code FAILS.
    case2_error = None
    try:
        run_generic_close(Decimal("1"), Decimal("1"), Decimal("2"))
    except ValueError as exc:
        case2_error = str(exc)
    print("[E-04] case today=1/previous=1/close=2 ->", case2_error or "succeeded")

    if case2_error is not None and "cannot deterministically resolve across position buckets" in case2_error:
        return "REPRODUCED"
    return "AUDIT_FINDING_INACCURATE"


# ---------------------------------------------------------------------------
# E-05: one CapitalMarginAssumptions cannot express heterogeneous multipliers
# ---------------------------------------------------------------------------

def reproduce_e05() -> str:
    exec_a = execution_assumptions()
    offset = offset_costs()
    sessions = SessionMetadata(
        "repro-sessions-e05",
        (
            SessionWindow("SYNTH_EX", "A", D1, at(D1, 9, 0), at(D1, 11, 0), "DAY"),
            SessionWindow("SYNTH_EX", "B", D1, at(D1, 9, 0), at(D1, 11, 0), "DAY"),
        ),
    )
    contract_a = ContractSpecification(
        exchange="SYNTH_EX", product_family="SYNTH", instrument_id="A",
        listed_at=at(D1, 8, 0), deactivated_at=at(D3, 0, 0),
        contract_multiplier=Decimal("5"), minimum_price_tick=Decimal("1"),
        currency="SYNTH", unit="SYNTH_UNIT", price_limit_rule_identity=None,
        offset_fee_metadata_identity=offset.identity_id, metadata_version="repro-contract-v1",
    )
    contract_b = ContractSpecification(
        exchange="SYNTH_EX", product_family="SYNTH", instrument_id="B",
        listed_at=at(D1, 8, 0), deactivated_at=at(D3, 0, 0),
        contract_multiplier=Decimal("10"), minimum_price_tick=Decimal("1"),
        currency="SYNTH", unit="SYNTH_UNIT", price_limit_rule_identity=None,
        offset_fee_metadata_identity=offset.identity_id, metadata_version="repro-contract-v1",
    )
    master = ContractMaster("repro-master-e05", (contract_a, contract_b))
    schedule = ContractMappingSchedule("repro-schedule-e05", ("X",), ())

    strategy = StrategyIdentity(
        research_lineage_id="repro-lineage-e05",
        family_id="repro-family-e05",
        strategy_version="1.0",
        source="deterministic-synthetic-fixture",
        applicable_instruments=("A", "B"),
        timeframe="5m",
        parameters=(TypedParameter("window", "int", 3),),
        code_hash="repro-code-e05",
        environment_hash="repro-env-e05",
        required_feature_versions=("repro-context-e05",),
        lifecycle_state=LifecycleState.DRAFT,
        data_exposure_history_reference="repro-exposure-e05",
    )
    experiment = ExperimentIdentity.from_strategy(
        strategy, "repro-data-v1", "repro-exposure-e05",
    )
    member = PortfolioMember(strategy, experiment)

    def build_request(multiplier: Decimal, capital_assumption_id: str) -> PortfolioRequest:
        candidates = []
        for index, symbol in enumerate(("A", "B")):
            request_id = f"e05-{symbol}"
            decision_at = at(D1, 9, 5 + index)
            inp = make_input(request_id, symbol, D1, decision_at)
            observation = ExecutionObservation(
                request_id, at(D1, 9, 6 + index), at(D1, 9, 6 + index), Decimal("100"),
            )
            spec = OrderSpecification(request_id, Decimal("1"), OrderAction.OPEN, direction=PositionDirection.LONG)
            candidates.append(
                PortfolioCandidate(
                    strategy.identity_id,
                    experiment.experiment_id,
                    inp,
                    spec,
                    observation,
                    PositionDirection.LONG,
                    exec_a.identity_id,
                    capital_assumption_id,
                )
            )
        return PortfolioRequest(
            mode=ValidationMode.CONFIRMATORY,
            dataset_class=DatasetClass.DEVELOPMENT,
            members=(member,),
            candidates=tuple(candidates),
            starting_capital=Decimal("100"),
            conflict_policy=PortfolioConflictPolicy("repro-conflict-policy-v1"),
            shared_capital_policy=SharedCapitalPolicy("repro-shared-capital-policy-v1"),
            contract_master=master,
            contract_mapping_schedule=schedule,
            session_metadata=sessions,
            price_limit_facts=(),
            execution_assumptions=exec_a,
            capital_assumptions=capital_assumptions(multiplier),
            offset_cost_assumptions=offset,
            execution_cutoff_at=at(D1, 12, 0),
        )

    # Single multiplier 5 -> instrument B (multiplier 10) is structurally rejected.
    cap5 = capital_assumptions(Decimal("5"))
    request5 = build_request(Decimal("5"), cap5.identity_id)
    members_by_strategy = {strategy.identity_id: member}
    err5 = None
    try:
        PortfolioCoordinator._resolve_candidates(request5, members_by_strategy)
    except ValueError as exc:
        err5 = str(exc)
    print("[E-05] multiplier=5 over A(5)+B(10) ->", err5 or "resolved")

    # Single multiplier 10 -> instrument A (multiplier 5) is structurally rejected.
    cap10 = capital_assumptions(Decimal("10"))
    request10 = build_request(Decimal("10"), cap10.identity_id)
    err10 = None
    try:
        PortfolioCoordinator._resolve_candidates(request10, members_by_strategy)
    except ValueError as exc:
        err10 = str(exc)
    print("[E-05] multiplier=10 over A(5)+B(10) ->", err10 or "resolved")

    if (
        err5 is not None and "contract multiplier is inconsistent with capital assumptions" in err5
        and err10 is not None and "contract multiplier is inconsistent with capital assumptions" in err10
    ):
        return "REPRODUCED"
    return "AUDIT_FINDING_INACCURATE"


# ---------------------------------------------------------------------------
# E-08: add/open margin admission uses available_capital, not available_resources
# ---------------------------------------------------------------------------

def reproduce_e08() -> str:
    exec_a = execution_assumptions()
    cap_a = capital_assumptions()

    # Existing position with material unrealized PnL (+20 at mark 120).
    snapshot = make_open_snapshot(
        position_id="e08-pos",
        request_id="e08-open",
        instrument="TEST",
        quantity=Decimal("1"),
        average_open_price=Decimal("100"),
        state_at=at(D1, 9, 5),
        exec_assumptions=exec_a,
        cap_assumptions=cap_a,
        unrealized=Decimal("20"),
    )
    available_capital = snapshot.available_capital
    available_resources = snapshot.available_resources
    print("[E-08] available_capital =", available_capital)
    print("[E-08] available_resources =", available_resources)

    # ADD 1 lot @ 1000 -> required margin + cost = 1000*0.1 + 0.25 = 100.25.
    add_outcome = make_filled_outcome(
        "e08-add", at(D1, 9, 11), exec_a.identity_id, Decimal("1000"), Decimal("0.25"), cap_a.identity_id,
    )
    add_spec = OrderSpecification("e08-add", Decimal("1"))
    add_input = make_input("e08-add", "TEST", D1, at(D1, 9, 10))
    constrained, _ = ChronologicalValidationRunner._apply_capital_constraints(
        (add_outcome,), (add_spec,), (add_input,), snapshot, cap_a, exec_a,
    )
    outcome = constrained[0]
    required = Decimal("100.25")
    print("[E-08] required margin+cost =", required)
    print("[E-08] outcome status =", outcome.status.value, "reason =", outcome.reason)
    print("[E-08] CURRENT_AUTHORITY_USED=available_capital")
    print("[E-08] CORRECT_POLICY=UNRESOLVED_BY_EXISTING_AUTHORITY")

    rejected_by_available_capital = (
        outcome.status is FillStatus.NOT_FILLED and outcome.reason == "INSUFFICIENT_MARGIN"
    )
    divergence = available_capital < required <= available_resources
    if rejected_by_available_capital and divergence:
        return "REPRODUCED"
    return "AUDIT_FINDING_INACCURATE"


# ---------------------------------------------------------------------------
# Round-trip hand-built transition helpers
# ---------------------------------------------------------------------------

def _hand_snapshot(
    *,
    position_id: str | None,
    quantity: Decimal,
    average_open_price: Decimal,
    instrument: str | None,
    direction: PositionDirection | None,
    state_at: datetime | None,
    trading_day: date | None,
    realized: Decimal = Decimal("0"),
    charged: Decimal = Decimal("0"),
    reserved: Decimal = Decimal("0"),
    request_id: str | None = None,
) -> CapitalSnapshot:
    return CapitalSnapshot(
        starting_capital=Decimal("100"),
        reserved_margin=reserved,
        charged_costs=charged,
        realized_pnl=realized,
        unrealized_pnl=Decimal("0"),
        position_quantity=quantity,
        average_open_price=average_open_price,
        position_instrument=instrument,
        position_id=position_id,
        position_request_id=request_id,
        execution_assumption_id="exec-assumption-v1" if position_id else None,
        capital_assumption_id="cap-assumption-v1" if position_id else None,
        state_at=state_at,
        position_trading_day=trading_day,
        today_quantity=quantity,
        previous_quantity=Decimal("0"),
        position_direction=direction,
    )


def hand_open(
    position_id: str,
    *,
    request_id: str = "open-1",
    instrument: str = "TEST",
    state_at: datetime,
    trading_day: date | None = D1,
    quantity: Decimal = Decimal("1"),
    price: Decimal = Decimal("101.5"),
    cost: Decimal = Decimal("0.25"),
) -> CapitalTransition:
    before = _hand_snapshot(position_id=None, quantity=Decimal("0"), average_open_price=Decimal("0"),
                            instrument=None, direction=None, state_at=state_at, trading_day=None)
    after = _hand_snapshot(position_id=position_id, quantity=quantity, average_open_price=price,
                           instrument=instrument, direction=PositionDirection.LONG, state_at=state_at,
                           trading_day=trading_day, charged=cost, reserved=Decimal("10"), request_id=request_id)
    return CapitalTransition(
        request_id, before, after, Decimal("10"), cost,
        quantity_change=quantity, transition_type="ORDER_EXECUTION",
    )


def hand_close(
    position_id: str,
    *,
    request_id: str = "close-1",
    instrument: str = "TEST",
    state_at: datetime,
    trading_day: date | None = D1,
    quantity: Decimal = Decimal("1"),
    average_open_price: Decimal = Decimal("101.5"),
    fill: Decimal = Decimal("108.5"),
    realized: Decimal = Decimal("7"),
    cost: Decimal = Decimal("1.25"),
    released: Decimal = Decimal("10"),
) -> CapitalTransition:
    before = _hand_snapshot(position_id=position_id, quantity=quantity, average_open_price=average_open_price,
                            instrument=instrument, direction=PositionDirection.LONG, state_at=state_at,
                            trading_day=trading_day, charged=Decimal("0.25"), reserved=released, request_id=request_id)
    after = _hand_snapshot(position_id=None, quantity=Decimal("0"), average_open_price=Decimal("0"),
                           instrument=None, direction=None, state_at=state_at, trading_day=None,
                           realized=realized, charged=Decimal("0.25") + cost)
    return CapitalTransition(
        request_id, before, after, Decimal("0"), cost,
        quantity_change=-quantity, realized_pnl_change=realized, released_margin=released,
        transition_type="POSITION_CLOSE",
    )


# ---------------------------------------------------------------------------
# E-09: duplicate request_id execution outcomes silently overwrite
# ---------------------------------------------------------------------------

def reproduce_e09() -> str:
    exec_a = execution_assumptions()
    cap_a = capital_assumptions()
    first = ExecutionOutcome(
        "dup-1", FillStatus.FILLED, at(D1, 9, 5), exec_a.identity_id,
        Decimal("101.5"), Decimal("1"), "TRADABLE_OBSERVATION", cap_a.identity_id,
    )
    second = ExecutionOutcome(
        "dup-1", FillStatus.FILLED, at(D1, 9, 5), exec_a.identity_id,
        Decimal("101.5"), Decimal("2"), "TRADABLE_OBSERVATION", cap_a.identity_id,
    )
    # Both the OPEN and the terminal CLOSE carry request_id "dup-1" and an
    # authoritative required_cost of 2, which matches ONLY the second outcome.
    # If the first outcome were retained by the request_id-keyed dict, the cost
    # cross-check would raise; materialize succeeding therefore proves the LAST
    # one wins and the FIRST is silently lost.
    open_transition = hand_open(
        "dup-pos", request_id="dup-1", state_at=at(D1, 9, 5), trading_day=D1,
        quantity=Decimal("1"), price=Decimal("101.5"), cost=Decimal("2"),
    )
    close_transition = hand_close(
        "dup-pos", request_id="dup-1", state_at=at(D1, 9, 40), trading_day=D1,
        quantity=Decimal("1"), average_open_price=Decimal("101.5"),
        fill=Decimal("108.5"), realized=Decimal("7"), cost=Decimal("2"),
    )
    ledger = RoundTripMaterializer().materialize(
        (open_transition, close_transition), (first, second),
    )
    trip = ledger.completed_round_trips[0]
    retained = trip.source_outcome_references
    print("[E-09] first.reference_id =", first.reference_id)
    print("[E-09] second.reference_id =", second.reference_id)
    print("[E-09] retained source_outcome_references =", retained)
    # Every transition with request_id "dup-1" resolves to the LAST outcome;
    # the FIRST outcome's evidence never appears anywhere in the round trip.
    first_lost = (
        first.reference_id not in retained
        and bool(retained)
        and all(ref == second.reference_id for ref in retained)
    )
    if first_lost:
        print("[E-09] verdict: FIRST_LOST (last outcome silently overwrites the first)")
        return "REPRODUCED"
    print("[E-09] verdict: unexpected retention shape:", retained)
    return "AUDIT_FINDING_INACCURATE"


# ---------------------------------------------------------------------------
# E-10: round-trip identity omits derived session-authority semantics
# ---------------------------------------------------------------------------

def reproduce_e10() -> str:
    pos = "e10-pos"
    opened_at = at(D1, 9, 30)
    closed_at = at(D1, 10, 30)
    open_transition = hand_open(
        pos, request_id="e10-open", state_at=opened_at, trading_day=None,
        quantity=Decimal("2"), price=Decimal("101.5"), cost=Decimal("0.25"),
    )
    close_transition = hand_close(
        pos, request_id="e10-close", state_at=closed_at, trading_day=None,
        quantity=Decimal("2"), average_open_price=Decimal("101.5"),
        fill=Decimal("108.5"), realized=Decimal("14"), cost=Decimal("1.25"),
    )
    transitions = (open_transition, close_transition)

    session_a = SessionMetadata(
        "repro-session-authority-A",
        (SessionWindow("SHFE", "TEST", D1, at(D1, 9, 0), at(D1, 11, 0), "DAY"),),
    )
    session_b = SessionMetadata(
        "repro-session-authority-B",
        # Same civil window, but a different official trading-day attribution.
        (SessionWindow("SHFE", "TEST", D_MONDAY_NEXT, at(D1, 9, 0), at(D1, 11, 0), "DAY"),),
    )
    ledger_a = RoundTripMaterializer(session_a, "SHFE").materialize(transitions)
    ledger_b = RoundTripMaterializer(session_b, "SHFE").materialize(transitions)
    trip_a = ledger_a.completed_round_trips[0]
    trip_b = ledger_b.completed_round_trips[0]
    print("[E-10] authority-A entry/exit day =", trip_a.entry_official_trading_day, trip_a.exit_official_trading_day,
          "week =", trip_a.entry_official_trading_week)
    print("[E-10] authority-B entry/exit day =", trip_b.entry_official_trading_day, trip_b.exit_official_trading_day,
          "week =", trip_b.entry_official_trading_week)
    print("[E-10] ledger_identity A =", trip_a.ledger_identity)
    print("[E-10] ledger_identity B =", trip_b.ledger_identity)
    derived_differ = (
        (trip_a.entry_official_trading_day, trip_a.exit_official_trading_day)
        != (trip_b.entry_official_trading_day, trip_b.exit_official_trading_day)
    )
    identity_same = trip_a.ledger_identity == trip_b.ledger_identity
    if derived_differ and identity_same:
        return "REPRODUCED"
    return "AUDIT_FINDING_INACCURATE"


# ---------------------------------------------------------------------------
# E-11: completed round trips ordered by position_id, not chronology
# ---------------------------------------------------------------------------

def reproduce_e11() -> str:
    z_open = hand_open("z-position", request_id="z-open", state_at=at(D1, 9, 30), trading_day=D1)
    z_close = hand_close("z-position", request_id="z-close", state_at=at(D1, 10, 0), trading_day=D1)
    a_open = hand_open("a-position", request_id="a-open", state_at=at(D1, 10, 30), trading_day=D1)
    a_close = hand_close("a-position", request_id="a-close", state_at=at(D1, 11, 0), trading_day=D1)
    ledger = RoundTripMaterializer().materialize((z_open, z_close, a_open, a_close))
    order = [trip.position_id for trip in ledger.completed_round_trips]
    print("[E-11] chronological completion order: z-position (10:00) then a-position (11:00)")
    print("[E-11] ledger output order:", order)
    if order == ["a-position", "z-position"]:
        return "REPRODUCED"
    return "AUDIT_FINDING_INACCURATE"


# ---------------------------------------------------------------------------
# E-12: open positions contribute only IDs to RoundTripLedger identity
# ---------------------------------------------------------------------------

def reproduce_e12() -> str:
    pos = "e12-pos"
    stream_a = hand_open(
        pos, request_id="e12-open-a", state_at=at(D1, 9, 30), trading_day=D1,
        quantity=Decimal("1"), price=Decimal("100"),
    )
    stream_b = hand_open(
        pos, request_id="e12-open-b", state_at=at(D1, 9, 45), trading_day=D1,
        quantity=Decimal("2"), price=Decimal("105"),
    )
    ledger_a = RoundTripMaterializer().materialize((stream_a,))
    ledger_b = RoundTripMaterializer().materialize((stream_b,))
    print("[E-12] stream A open_position_ids =", ledger_a.open_position_ids,
          "identity =", ledger_a.identity_id)
    print("[E-12] stream B open_position_ids =", ledger_b.open_position_ids,
          "identity =", ledger_b.identity_id)
    same_open_ids = (
        ledger_a.open_position_ids == ledger_b.open_position_ids == (pos,)
    )
    if same_open_ids and ledger_a.identity_id == ledger_b.identity_id:
        return "REPRODUCED"
    return "AUDIT_FINDING_INACCURATE"


# ---------------------------------------------------------------------------
# E-13: bootstrap TradingState has no cross-trading-day chronology barrier
# ---------------------------------------------------------------------------

def reproduce_e13() -> str:
    ts = TradingState()
    ts.ingest(BrokerEvent("e1", D1, 1, "TEST", 1))   # D1 seq1 applied -> TEST=1
    buffered = ts.ingest(BrokerEvent("e3", D1, 3, "TEST", 2))  # D1 seq3 buffered (gap)
    ts.ingest(BrokerEvent("e4", D2, 1, "TEST", 1))   # D2 seq1 applied -> TEST=2
    pos_after_d2 = ts.position("TEST")
    late = ts.ingest(BrokerEvent("e2", D1, 2, "TEST", 1))  # D1 seq2 arrives later
    pos_final = ts.position("TEST")
    print("[E-13] D1 seq1 applied; D1 seq3 buffered (seq2 gap); D2 seq1 applied")
    print("[E-13] position after D2 applied =", pos_after_d2)
    print("[E-13] late D1 seq2/3 applied =", late.applied)
    print("[E-13] position after late D1 seq2/3 =", pos_final)
    if late.applied and pos_final != pos_after_d2:
        return "REPRODUCED"
    return "AUDIT_FINDING_INACCURATE"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    checks = [
        ("E01", reproduce_e01),
        ("E02", reproduce_e02),
        ("E03", reproduce_e03),
        ("E04", reproduce_e04),
        ("E05", reproduce_e05),
        ("E08", reproduce_e08),
        ("E09", reproduce_e09),
        ("E10", reproduce_e10),
        ("E11", reproduce_e11),
        ("E12", reproduce_e12),
        ("E13", reproduce_e13),
    ]
    for key, fn in checks:
        try:
            finish(key, fn())
        except Exception as exc:  # noqa: BLE001 - a diagnostic failure must not abort the run
            print(f"[{key}] exception during reproduction: {type(exc).__name__}: {exc}")
            finish(key, "AUDIT_FINDING_INACCURATE")

    print()
    print("E08_SEMANTIC_AUTHORITY_REQUIRED=YES")
    print("BOOTSTRAP_E13_SCOPE=BOOTSTRAP_FIXTURE_ONLY")
    print("PRODUCTION_CODE_CHANGED=NO")
    print("NO_CANDIDATE_OUTCOME_DATA_USED=YES")

    inaccurate = [k for k, v in RESULTS.items() if v == "AUDIT_FINDING_INACCURATE"]
    if inaccurate:
        print()
        print("AUDIT_FINDING_INACCURATE:", ", ".join(inaccurate))

    # Diagnostic completeness is the deliverable; exit 0 regardless.
    return 0


if __name__ == "__main__":
    sys.exit(main())

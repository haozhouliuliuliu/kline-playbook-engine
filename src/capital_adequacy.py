"""Deterministic one-lot capital-adequacy primitives (additive, offline-only).

This module builds the RB one-lot capital-adequacy calculator that future
REAL/PAPER bindings can consume. It computes, when all required inputs are
supplied:

- one-lot notional / tick value;
- one-lot margin usage;
- Jianghe invalidation-distance price move and pre-fee/slippage stop risk;
- conservative slippage cost and commission/fee cost (from supplied inputs);
- one-lot stop risk;
- optional gap/stress loss from a supplied stress scenario;
- capital fraction consumed by stop/stress risk;
- margin headroom and operational reserve/headroom;
- PASS / FAIL / INSUFFICIENT_EVIDENCE against externally supplied approved
  risk constraints;
- minimum viable capital only when a sufficient approved constraint set is
  supplied.

Permanent-risk boundary: this module chooses NO permanent numeric risk value.
Capital, slippage, stress, fees, margin and every approved constraint are
explicit inputs.  Missing required facts produce INSUFFICIENT_EVIDENCE with
structured reason codes, never fabricated zeros.  A risk-increasing claim is
never PASS when any required input or approved constraint is missing
(fail closed).

No orders, no broker/account action, no live acquisition, no paid calls, no
credentials, no permanent numeric risk choices.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

from src.contract_facts import ContractFacts, current_use_eligibility


class AdequacyDecision(str, Enum):
    """Deterministic adequacy decision vocabulary."""

    PASS = "PASS"
    FAIL = "FAIL"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class AdequacyReasonCode(str, Enum):
    """Structured reason codes (not free text) for an adequacy decision."""

    OK = "OK"
    # missing / unknown / not-current inputs
    CONTRACT_FACTS_MISSING = "CONTRACT_FACTS_MISSING"
    CONTRACT_FACTS_NOT_CURRENT = "CONTRACT_FACTS_NOT_CURRENT"
    REFERENCE_PRICE_MISSING = "REFERENCE_PRICE_MISSING"
    INVALIDATION_DISTANCE_MISSING = "INVALIDATION_DISTANCE_MISSING"
    MARGIN_FACTS_MISSING = "MARGIN_FACTS_MISSING"
    MARGIN_FACT_UNRESOLVABLE = "MARGIN_FACT_UNRESOLVABLE"
    FEE_FACTS_MISSING = "FEE_FACTS_MISSING"
    CAPITAL_MISSING = "CAPITAL_MISSING"
    SLIPPAGE_ASSUMPTION_MISSING = "SLIPPAGE_ASSUMPTION_MISSING"
    APPROVED_CONSTRAINTS_MISSING = "APPROVED_CONSTRAINTS_MISSING"
    APPROVED_CONSTRAINTS_INSUFFICIENT = "APPROVED_CONSTRAINTS_INSUFFICIENT"
    # supplied approved constraint violations (FAIL)
    STOP_RISK_EXCEEDS_APPROVED_LIMIT = "STOP_RISK_EXCEEDS_APPROVED_LIMIT"
    CAPITAL_FRACTION_EXCEEDS_APPROVED_LIMIT = "CAPITAL_FRACTION_EXCEEDS_APPROVED_LIMIT"
    MARGIN_HEADROOM_BELOW_APPROVED = "MARGIN_HEADROOM_BELOW_APPROVED"
    OPERATIONAL_RESERVE_BELOW_APPROVED = "OPERATIONAL_RESERVE_BELOW_APPROVED"
    STRESS_LOSS_EXCEEDS_APPROVED_LIMIT = "STRESS_LOSS_EXCEEDS_APPROVED_LIMIT"
    CAPITAL_BELOW_APPROVED_MINIMUM = "CAPITAL_BELOW_APPROVED_MINIMUM"
    MINIMUM_VIABLE_CAPITAL_INFEASIBLE = "MINIMUM_VIABLE_CAPITAL_INFEASIBLE"


def _positive_decimal(value: object, name: str) -> Decimal:
    if type(value) is not Decimal or not value.is_finite() or value <= 0:
        raise ValueError(f"{name} must be a positive finite Decimal")
    return value


def _fraction_decimal(value: object, name: str) -> Decimal:
    if type(value) is not Decimal or not value.is_finite() or value <= Decimal("0") or value > Decimal("1"):
        raise ValueError(f"{name} must be a finite Decimal in (0, 1]")
    return value


@dataclass(frozen=True)
class ApprovedRiskConstraints:
    """Externally supplied approved risk constraints (all optional inputs).

    None of these values is chosen by this module; each is an explicit input
    that later Owner authority supplies.  ``None`` means "not supplied".
    """

    max_one_lot_stop_risk: Decimal | None = None
    max_capital_fraction_at_risk: Decimal | None = None
    min_margin_headroom: Decimal | None = None
    min_operational_reserve: Decimal | None = None
    min_capital: Decimal | None = None

    def __post_init__(self) -> None:
        for value, name in (
            (self.max_one_lot_stop_risk, "approved max one-lot stop risk"),
            (self.min_margin_headroom, "approved min margin headroom"),
            (self.min_operational_reserve, "approved min operational reserve"),
            (self.min_capital, "approved min capital"),
        ):
            if value is not None:
                _positive_decimal(value, name)
        if self.max_capital_fraction_at_risk is not None:
            _fraction_decimal(self.max_capital_fraction_at_risk, "approved max capital fraction at risk")

    @property
    def supplied(self) -> bool:
        return any(
            value is not None
            for value in (
                self.max_one_lot_stop_risk,
                self.max_capital_fraction_at_risk,
                self.min_margin_headroom,
                self.min_operational_reserve,
                self.min_capital,
            )
        )

    @property
    def sufficient_for_adequacy(self) -> bool:
        """Conservative sufficiency: a risk ceiling, margin headroom AND
        operational reserve must all be supplied before a PASS is possible."""
        risk_ceiling = (
            self.max_one_lot_stop_risk is not None
            or self.max_capital_fraction_at_risk is not None
        )
        return (
            risk_ceiling
            and self.min_margin_headroom is not None
            and self.min_operational_reserve is not None
        )


@dataclass(frozen=True)
class SlippageAssumption:
    """Conservative slippage scenario assumption (ticks, supplied input)."""

    ticks: Decimal
    label: str = "conservative_slippage_scenario_assumption"

    def __post_init__(self) -> None:
        if type(self.ticks) is not Decimal or not self.ticks.is_finite() or self.ticks < 0:
            raise ValueError("slippage assumption ticks must be a non-negative finite Decimal")
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("slippage assumption label is required")


@dataclass(frozen=True)
class StressAssumption:
    """Optional gap/stress scenario: an explicit loss OR a price move in ticks."""

    price_move_ticks: Decimal | None = None
    explicit_loss: Decimal | None = None
    label: str = "gap_stress_scenario_assumption"

    def __post_init__(self) -> None:
        if self.price_move_ticks is not None:
            _positive_decimal(self.price_move_ticks, "stress price move ticks")
        if self.explicit_loss is not None:
            _positive_decimal(self.explicit_loss, "stress explicit loss")
        if (self.price_move_ticks is None) == (self.explicit_loss is None):
            raise ValueError("stress assumption requires exactly one of price_move_ticks or explicit_loss")
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("stress assumption label is required")


@dataclass(frozen=True)
class InvalidationObservation:
    """Jianghe invalidation-distance behavior observation (ticks)."""

    distance_ticks: Decimal
    label: str = "jianghe_invalidation_distance_observation"

    def __post_init__(self) -> None:
        _positive_decimal(self.distance_ticks, "invalidation distance ticks")
        if not isinstance(self.label, str) or not self.label.strip():
            raise ValueError("invalidation observation label is required")


@dataclass(frozen=True)
class OneLotCapitalAdequacyInput:
    """All inputs to one one-lot capital-adequacy evaluation.

    Every field that can legitimately be MISSING is optional; the evaluator
    returns INSUFFICIENT_EVIDENCE with a precise reason code instead of
    inventing a value.  ``stress`` is genuinely optional.
    """

    contract_facts: ContractFacts | None = None
    invalidation: InvalidationObservation | None = None
    capital: Decimal | None = None
    slippage: SlippageAssumption | None = None
    approved_constraints: ApprovedRiskConstraints | None = None
    stress: StressAssumption | None = None

    def __post_init__(self) -> None:
        if self.contract_facts is not None and not isinstance(self.contract_facts, ContractFacts):
            raise ValueError("capital-adequacy input contract facts must be a ContractFacts or None")
        if self.invalidation is not None and not isinstance(self.invalidation, InvalidationObservation):
            raise ValueError("capital-adequacy input invalidation must be an InvalidationObservation or None")
        if self.capital is not None:
            _positive_decimal(self.capital, "capital-adequacy input capital")
        if self.slippage is not None and not isinstance(self.slippage, SlippageAssumption):
            raise ValueError("capital-adequacy input slippage must be a SlippageAssumption or None")
        if self.approved_constraints is not None and not isinstance(
            self.approved_constraints, ApprovedRiskConstraints
        ):
            raise ValueError(
                "capital-adequacy input approved constraints must be an ApprovedRiskConstraints or None"
            )
        if self.stress is not None and not isinstance(self.stress, StressAssumption):
            raise ValueError("capital-adequacy input stress must be a StressAssumption or None")


@dataclass(frozen=True)
class OneLotCapitalAdequacyResult:
    """Deterministic adequacy result with structured reason codes."""

    decision: AdequacyDecision
    reason_codes: tuple[AdequacyReasonCode, ...]
    notional_per_lot: Decimal | None = None
    tick_value: Decimal | None = None
    one_lot_margin: Decimal | None = None
    invalidation_price_move: Decimal | None = None
    stop_risk_before_slippage_fees: Decimal | None = None
    slippage_cost: Decimal | None = None
    fee_cost: Decimal | None = None
    one_lot_stop_risk: Decimal | None = None
    stress_loss: Decimal | None = None
    capital_fraction_at_risk: Decimal | None = None
    capital_fraction_at_risk_stress_inclusive: Decimal | None = None
    margin_headroom: Decimal | None = None
    operational_headroom: Decimal | None = None
    minimum_viable_capital: Decimal | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.decision, AdequacyDecision):
            raise ValueError("adequacy result decision must be an AdequacyDecision")
        if not self.reason_codes or not all(
            isinstance(code, AdequacyReasonCode) for code in self.reason_codes
        ):
            raise ValueError("adequacy result requires at least one AdequacyReasonCode")


def _minimum_viable_capital(
    constraints: ApprovedRiskConstraints,
    one_lot_margin: Decimal,
    worst_loss: Decimal,
    capital_fraction_stress_inclusive: Decimal | None,
    capital_fraction_stop_only: Decimal | None,
) -> Decimal | None:
    """Minimum capital satisfying all supplied approved constraints.

    Returns None when the supplied constraint set is insufficient to derive a
    minimum (a PASS requires sufficiency, so this is only reached when the
    constraints are sufficient).  The absolute one-lot stop-risk limit is
    capital-independent; if it is violated the caller already returns FAIL and
    this function is not reached for the infeasible case.
    """
    bounds: list[Decimal] = []
    if constraints.min_margin_headroom is not None:
        bounds.append(one_lot_margin + constraints.min_margin_headroom)
    if constraints.min_operational_reserve is not None:
        bounds.append(one_lot_margin + worst_loss + constraints.min_operational_reserve)
    if constraints.max_capital_fraction_at_risk is not None:
        fraction = capital_fraction_stress_inclusive
        if fraction is None:
            fraction = capital_fraction_stop_only
        if fraction is not None:
            bounds.append(worst_loss / constraints.max_capital_fraction_at_risk)
    if constraints.min_capital is not None:
        bounds.append(constraints.min_capital)
    if not bounds:
        return None
    return max(bounds)


def evaluate_one_lot_capital_adequacy(
    input_: OneLotCapitalAdequacyInput,
) -> OneLotCapitalAdequacyResult:
    """Deterministic, side-effect free one-lot capital-adequacy evaluation."""
    if not isinstance(input_, OneLotCapitalAdequacyInput):
        raise ValueError("capital-adequacy evaluation requires a OneLotCapitalAdequacyInput")

    reasons: list[AdequacyReasonCode] = []

    facts = input_.contract_facts
    if facts is None:
        return OneLotCapitalAdequacyResult(
            decision=AdequacyDecision.INSUFFICIENT_EVIDENCE,
            reason_codes=(AdequacyReasonCode.CONTRACT_FACTS_MISSING,),
        )
    eligible, _ = current_use_eligibility(facts)
    if not eligible:
        reasons.append(AdequacyReasonCode.CONTRACT_FACTS_NOT_CURRENT)

    invalidation = input_.invalidation
    if invalidation is None:
        reasons.append(AdequacyReasonCode.INVALIDATION_DISTANCE_MISSING)

    capital = input_.capital
    if capital is None:
        reasons.append(AdequacyReasonCode.CAPITAL_MISSING)

    slippage = input_.slippage
    if slippage is None:
        reasons.append(AdequacyReasonCode.SLIPPAGE_ASSUMPTION_MISSING)

    reference_price = facts.reference_price
    if reference_price is None:
        reasons.append(AdequacyReasonCode.REFERENCE_PRICE_MISSING)

    margin = facts.margin
    if margin is None:
        reasons.append(AdequacyReasonCode.MARGIN_FACTS_MISSING)

    fee = facts.fee
    if fee is None:
        reasons.append(AdequacyReasonCode.FEE_FACTS_MISSING)

    constraints = input_.approved_constraints
    if constraints is None:
        reasons.append(AdequacyReasonCode.APPROVED_CONSTRAINTS_MISSING)
    elif not constraints.sufficient_for_adequacy:
        reasons.append(AdequacyReasonCode.APPROVED_CONSTRAINTS_INSUFFICIENT)

    # -- derive every computable partial (never fabricate a missing value) --
    tick_value = facts.tick_value
    notional = None if reference_price is None else facts.notional_per_lot(reference_price)

    one_lot_margin = None
    if margin is not None and notional is not None:
        one_lot_margin = margin.one_lot_margin_amount(notional)
        if one_lot_margin is None:
            reasons.append(AdequacyReasonCode.MARGIN_FACT_UNRESOLVABLE)

    invalidation_price_move = None
    stop_risk_before = None
    if invalidation is not None:
        invalidation_price_move = invalidation.distance_ticks * facts.tick_size
        stop_risk_before = invalidation_price_move * facts.multiplier

    slippage_cost = None if slippage is None else slippage.ticks * tick_value

    fee_cost = None
    if fee is not None and notional is not None:
        fee_cost = fee.cost_for(notional)

    one_lot_stop_risk = None
    if (
        stop_risk_before is not None
        and slippage_cost is not None
        and fee_cost is not None
    ):
        one_lot_stop_risk = stop_risk_before + slippage_cost + fee_cost

    stress_loss = None
    if input_.stress is not None:
        if input_.stress.explicit_loss is not None:
            stress_loss = input_.stress.explicit_loss
        else:
            stress_loss = input_.stress.price_move_ticks * tick_value

    worst_loss = one_lot_stop_risk
    if one_lot_stop_risk is not None and stress_loss is not None:
        worst_loss = one_lot_stop_risk + stress_loss

    capital_fraction_stop_only = None
    capital_fraction_stress_inclusive = None
    if capital is not None and one_lot_stop_risk is not None:
        capital_fraction_stop_only = one_lot_stop_risk / capital
        capital_fraction_stress_inclusive = worst_loss / capital

    margin_headroom = None
    operational_headroom = None
    if capital is not None and one_lot_margin is not None:
        margin_headroom = capital - one_lot_margin
        if worst_loss is not None:
            operational_headroom = capital - one_lot_margin - worst_loss

    if reasons:
        return OneLotCapitalAdequacyResult(
            decision=AdequacyDecision.INSUFFICIENT_EVIDENCE,
            reason_codes=tuple(reasons),
            notional_per_lot=notional,
            tick_value=tick_value,
            one_lot_margin=one_lot_margin,
            invalidation_price_move=invalidation_price_move,
            stop_risk_before_slippage_fees=stop_risk_before,
            slippage_cost=slippage_cost,
            fee_cost=fee_cost,
            one_lot_stop_risk=one_lot_stop_risk,
            stress_loss=stress_loss,
            capital_fraction_at_risk=capital_fraction_stop_only,
            capital_fraction_at_risk_stress_inclusive=capital_fraction_stress_inclusive,
            margin_headroom=margin_headroom,
            operational_headroom=operational_headroom,
        )

    # -- all required inputs present: evaluate the supplied approved constraints --
    fail_reasons: list[AdequacyReasonCode] = []

    if (
        constraints.max_one_lot_stop_risk is not None
        and one_lot_stop_risk > constraints.max_one_lot_stop_risk
    ):
        fail_reasons.append(AdequacyReasonCode.STOP_RISK_EXCEEDS_APPROVED_LIMIT)

    if (
        constraints.max_capital_fraction_at_risk is not None
        and capital_fraction_stress_inclusive is not None
        and capital_fraction_stress_inclusive > constraints.max_capital_fraction_at_risk
    ):
        fail_reasons.append(AdequacyReasonCode.CAPITAL_FRACTION_EXCEEDS_APPROVED_LIMIT)

    if (
        constraints.min_margin_headroom is not None
        and margin_headroom is not None
        and margin_headroom < constraints.min_margin_headroom
    ):
        fail_reasons.append(AdequacyReasonCode.MARGIN_HEADROOM_BELOW_APPROVED)

    if (
        constraints.min_operational_reserve is not None
        and operational_headroom is not None
        and operational_headroom < constraints.min_operational_reserve
    ):
        fail_reasons.append(AdequacyReasonCode.OPERATIONAL_RESERVE_BELOW_APPROVED)

    if (
        constraints.max_one_lot_stop_risk is not None
        and stress_loss is not None
        and stress_loss > constraints.max_one_lot_stop_risk
    ):
        fail_reasons.append(AdequacyReasonCode.STRESS_LOSS_EXCEEDS_APPROVED_LIMIT)

    if constraints.min_capital is not None and capital < constraints.min_capital:
        fail_reasons.append(AdequacyReasonCode.CAPITAL_BELOW_APPROVED_MINIMUM)

    if fail_reasons:
        return OneLotCapitalAdequacyResult(
            decision=AdequacyDecision.FAIL,
            reason_codes=tuple(fail_reasons),
            notional_per_lot=notional,
            tick_value=tick_value,
            one_lot_margin=one_lot_margin,
            invalidation_price_move=invalidation_price_move,
            stop_risk_before_slippage_fees=stop_risk_before,
            slippage_cost=slippage_cost,
            fee_cost=fee_cost,
            one_lot_stop_risk=one_lot_stop_risk,
            stress_loss=stress_loss,
            capital_fraction_at_risk=capital_fraction_stop_only,
            capital_fraction_at_risk_stress_inclusive=capital_fraction_stress_inclusive,
            margin_headroom=margin_headroom,
            operational_headroom=operational_headroom,
        )

    minimum_viable_capital = _minimum_viable_capital(
        constraints,
        one_lot_margin,
        worst_loss,
        capital_fraction_stress_inclusive,
        capital_fraction_stop_only,
    )
    return OneLotCapitalAdequacyResult(
        decision=AdequacyDecision.PASS,
        reason_codes=(AdequacyReasonCode.OK,),
        notional_per_lot=notional,
        tick_value=tick_value,
        one_lot_margin=one_lot_margin,
        invalidation_price_move=invalidation_price_move,
        stop_risk_before_slippage_fees=stop_risk_before,
        slippage_cost=slippage_cost,
        fee_cost=fee_cost,
        one_lot_stop_risk=one_lot_stop_risk,
        stress_loss=stress_loss,
        capital_fraction_at_risk=capital_fraction_stop_only,
        capital_fraction_at_risk_stress_inclusive=capital_fraction_stress_inclusive,
        margin_headroom=margin_headroom,
        operational_headroom=operational_headroom,
        minimum_viable_capital=minimum_viable_capital,
    )

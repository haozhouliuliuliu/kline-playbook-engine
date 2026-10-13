"""Deterministic batch / distribution capital-adequacy observation analysis.

This module consumes:

- observed Jianghe invalidation-distance inputs (per observation identity, in
  validated ticks);
- supplied current contract facts for one exact contract;
- supplied scenario assumptions (conservative slippage, optional stress
  scenarios);
- supplied capital envelopes and supplied approved risk constraints;

and produces deterministic descriptive evidence: per-observation
PASS/FAIL/INSUFFICIENT_EVIDENCE decisions, sufficient/insufficient counts,
deterministic min/max/median and clearly-defined quantiles of the one-lot
stop-risk distribution, margin/headroom results per envelope, and an aggregate
decision that fails closed whenever required facts or approved constraints are
absent.

Boundary and ownership:

1. exchange/broker facts  -> ``ContractFacts`` (carries its own FactCategory);
2. scenario assumptions    -> ``SlippageAssumption`` / ``StressAssumption``;
3. observed Jianghe behavior -> ``ObservedInvalidation`` distance observations;
4. approved risk constraints -> ``ApprovedRiskConstraints``.

These four inputs are never conflated: the result echoes the explicit
classification and the underlying one-lot primitive never treats a scenario,
observation or constraint as exchange/broker truth.

Permanent-risk boundary: this module chooses NO permanent numeric risk value.
Every capital envelope, fee/margin/slippage fact, stress scenario and approved
constraint is an explicit input.  No production default capital (e.g. a fixed
modest amount), no RB contract/month, no risk percentage, no reserve, no fee
schedule, no slippage tick count and no stress gap live here.

If quantiles are computed, the exact algorithm is frozen here and in the tests
as generic statistics only (linear interpolation between closest ranks).  A
percentile is descriptive evidence and is never interpreted as an approved
risk limit.

No trading decision, no orders, no broker/account action, no live acquisition,
no paid calls, no credentials, no permanent risk selection and no future
outcome semantics.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum

from src.capital_adequacy import (
    AdequacyDecision,
    AdequacyReasonCode,
    ApprovedRiskConstraints,
    InvalidationObservation,
    OneLotCapitalAdequacyInput,
    SlippageAssumption,
    StressAssumption,
    evaluate_one_lot_capital_adequacy,
)
from src.contract_facts import ContractFacts, ContractIdentity, FactCategory


class BatchReasonCode(str, Enum):
    """Structured reason codes (not free text) for a batch analysis."""

    OK = "OK"
    NO_OBSERVATIONS = "NO_OBSERVATIONS"
    CONTRACT_FACTS_MISSING = "CONTRACT_FACTS_MISSING"
    SLIPPAGE_ASSUMPTION_MISSING = "SLIPPAGE_ASSUMPTION_MISSING"
    APPROVED_CONSTRAINTS_MISSING = "APPROVED_CONSTRAINTS_MISSING"
    APPROVED_CONSTRAINTS_INSUFFICIENT = "APPROVED_CONSTRAINTS_INSUFFICIENT"
    OBSERVATION_INSUFFICIENT = "OBSERVATION_INSUFFICIENT"
    OBSERVATION_FAIL = "OBSERVATION_FAIL"
    DISTRIBUTION_NO_SUFFICIENT_OBSERVATIONS = "DISTRIBUTION_NO_SUFFICIENT_OBSERVATIONS"


def _positive_decimal(value: object, name: str) -> Decimal:
    if type(value) is not Decimal or not value.is_finite() or value <= 0:
        raise ValueError(f"{name} must be a positive finite Decimal")
    return value


def _required_text(value: object, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")


def _strictly_increasing_decimals(values: tuple[Decimal, ...], name: str) -> None:
    if not values:
        raise ValueError(f"{name} must not be empty")
    previous: Decimal | None = None
    for value in values:
        if type(value) is not Decimal or not value.is_finite() or value <= 0 or value >= 1:
            raise ValueError(f"{name} entries must be finite Decimals strictly in (0, 1)")
        if previous is not None and value <= previous:
            raise ValueError(f"{name} entries must be strictly increasing")
        previous = value


def _linear_interpolated_quantile(
    sorted_values: tuple[Decimal, ...], level: Decimal
) -> Decimal:
    """Frozen generic-statistics quantile.

    Method: linear interpolation between closest ranks (the conventional
    ``linear`` method).  ``level`` must be in (0, 1).  This is descriptive
    statistics only; a percentile is never an approved risk limit.
    """
    n = len(sorted_values)
    if n == 0:
        raise ValueError("cannot compute a quantile over an empty series")
    if type(level) is not Decimal or not level.is_finite() or not (Decimal("0") < level < Decimal("1")):
        raise ValueError("quantile level must be a finite Decimal in (0, 1)")
    if n == 1:
        return sorted_values[0]
    h = (Decimal(n) - 1) * level
    lo = int(h)  # floor for non-negative h
    frac = h - Decimal(lo)
    hi = lo if frac == 0 else lo + 1
    lower = sorted_values[lo]
    upper = sorted_values[hi]
    return lower * (Decimal("1") - frac) + upper * frac


@dataclass(frozen=True)
class ObservedInvalidation:
    """One observed Jianghe invalidation-distance input (validated ticks)."""

    observation_id: str
    distance_ticks: Decimal
    label: str = "jianghe_invalidation_distance_observation"

    def __post_init__(self) -> None:
        _required_text(self.observation_id, "observation id")
        _positive_decimal(self.distance_ticks, "invalidation distance ticks")
        _required_text(self.label, "observation label")


@dataclass(frozen=True)
class CapitalAdequacyBatchInput:
    """All inputs to one batch / distribution capital-adequacy analysis.

    Every field that can legitimately be MISSING is optional; the analyzer
    returns INSUFFICIENT_EVIDENCE with a precise reason code instead of
    inventing a value.  ``quantile_levels`` is a generic-statistics
    configuration and is never interpreted as an approved risk limit.
    """

    contract_facts: ContractFacts | None
    observations: tuple[ObservedInvalidation, ...]
    capital_envelopes: tuple[Decimal, ...]
    slippage: SlippageAssumption | None
    approved_constraints: ApprovedRiskConstraints | None
    stress_scenarios: tuple[StressAssumption, ...] = ()
    quantile_levels: tuple[Decimal, ...] = (Decimal("0.25"), Decimal("0.50"), Decimal("0.75"))
    batch_identity: str | None = None
    as_of: datetime | None = None

    def __post_init__(self) -> None:
        if self.contract_facts is not None and not isinstance(self.contract_facts, ContractFacts):
            raise ValueError("batch contract facts must be a ContractFacts or None")
        # Normalize sequence inputs to immutable tuples so callers may supply
        # tuples or lists without changing result determinism.
        object.__setattr__(self, "observations", tuple(self.observations))
        object.__setattr__(self, "capital_envelopes", tuple(self.capital_envelopes))
        object.__setattr__(self, "stress_scenarios", tuple(self.stress_scenarios))
        object.__setattr__(self, "quantile_levels", tuple(self.quantile_levels))
        if not all(isinstance(item, ObservedInvalidation) for item in self.observations):
            raise ValueError("batch observations must all be ObservedInvalidation")
        if not self.capital_envelopes:
            raise ValueError("batch capital envelopes must not be empty")
        if not all(
            type(item) is Decimal and item.is_finite() and item > 0
            for item in self.capital_envelopes
        ):
            raise ValueError("batch capital envelopes must be positive finite Decimals")
        if self.slippage is not None and not isinstance(self.slippage, SlippageAssumption):
            raise ValueError("batch slippage must be a SlippageAssumption or None")
        if self.approved_constraints is not None and not isinstance(
            self.approved_constraints, ApprovedRiskConstraints
        ):
            raise ValueError(
                "batch approved constraints must be an ApprovedRiskConstraints or None"
            )
        if not all(isinstance(item, StressAssumption) for item in self.stress_scenarios):
            raise ValueError("batch stress scenarios must all be StressAssumption")
        _strictly_increasing_decimals(self.quantile_levels, "batch quantile levels")
        if self.batch_identity is not None:
            _required_text(self.batch_identity, "batch identity")
        if self.as_of is not None and self.as_of.tzinfo is None:
            raise ValueError("batch as-of timestamp must be timezone-aware")


@dataclass(frozen=True)
class ObservationDecision:
    """Decision for one observation under one (capital envelope, stress)
    combination."""

    capital_envelope: Decimal
    stress_label: str | None
    decision: AdequacyDecision
    reason_codes: tuple[AdequacyReasonCode, ...]
    margin_headroom: Decimal | None = None
    operational_headroom: Decimal | None = None
    capital_fraction_at_risk: Decimal | None = None
    stress_loss: Decimal | None = None

    def __post_init__(self) -> None:
        _positive_decimal(self.capital_envelope, "observation decision capital envelope")
        if not isinstance(self.decision, AdequacyDecision):
            raise ValueError("observation decision must carry an AdequacyDecision")
        if not self.reason_codes or not all(
            isinstance(code, AdequacyReasonCode) for code in self.reason_codes
        ):
            raise ValueError("observation decision requires at least one AdequacyReasonCode")
        if self.stress_label is not None:
            _required_text(self.stress_label, "observation decision stress label")


@dataclass(frozen=True)
class ObservationResult:
    """Deterministic per-observation evidence.

    ``one_lot_stop_risk`` (and the capital-independent fields) come from the
    base no-stress evaluation and are shared across envelopes; the
    per-envelope/per-stress margin-headroom, operational-headroom and capital
    fractions live in ``decisions``.
    """

    observation_id: str
    distance_ticks: Decimal
    one_lot_stop_risk: Decimal | None
    one_lot_margin: Decimal | None
    fee_cost: Decimal | None
    slippage_cost: Decimal | None
    decisions: tuple[ObservationDecision, ...]

    def __post_init__(self) -> None:
        _required_text(self.observation_id, "observation result id")
        _positive_decimal(self.distance_ticks, "observation result distance ticks")
        if not self.decisions or not all(
            isinstance(item, ObservationDecision) for item in self.decisions
        ):
            raise ValueError("observation result requires at least one ObservationDecision")


@dataclass(frozen=True)
class StopRiskDistribution:
    """Deterministic descriptive statistics of the one-lot stop-risk series.

    Statistics are generic and frozen; percentiles are never interpreted as
    approved risk limits.
    """

    count: int
    min: Decimal
    max: Decimal
    median: Decimal
    quantiles: tuple[tuple[Decimal, Decimal], ...]
    method: str = "LINEAR_INTERPOLATION_BETWEEN_CLOSEST_RANKS"

    def __post_init__(self) -> None:
        if self.count <= 0:
            raise ValueError("stop-risk distribution count must be positive")
        for value, name in (
            (self.min, "distribution min"),
            (self.max, "distribution max"),
            (self.median, "distribution median"),
        ):
            if type(value) is not Decimal or not value.is_finite():
                raise ValueError(f"{name} must be a finite Decimal")
        if self.max < self.min:
            raise ValueError("distribution max must not be below min")
        if not self.quantiles:
            raise ValueError("stop-risk distribution requires at least one quantile")
        if not all(
            len(item) == 2 and type(item[0]) is Decimal and type(item[1]) is Decimal
            for item in self.quantiles
        ):
            raise ValueError("stop-risk distribution quantiles must be (level, value) Decimal pairs")


@dataclass(frozen=True)
class EnvelopeAggregate:
    """Per-capital-envelope descriptive aggregate over all observations.

    ``decision`` is derived from the base no-stress evaluation only;
    stress-scenario decisions remain visible per observation in
    ``ObservationResult.decisions``.
    """

    capital_envelope: Decimal
    pass_count: int
    fail_count: int
    insufficient_count: int
    decision: AdequacyDecision
    reason_codes: tuple[BatchReasonCode, ...]
    min_margin_headroom: Decimal | None = None
    min_operational_headroom: Decimal | None = None
    max_capital_fraction_at_risk: Decimal | None = None

    def __post_init__(self) -> None:
        _positive_decimal(self.capital_envelope, "envelope aggregate capital envelope")
        for name in ("pass_count", "fail_count", "insufficient_count"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"envelope aggregate {name} must be a non-negative int")
        if not isinstance(self.decision, AdequacyDecision):
            raise ValueError("envelope aggregate decision must be an AdequacyDecision")
        if not self.reason_codes or not all(
            isinstance(code, BatchReasonCode) for code in self.reason_codes
        ):
            raise ValueError("envelope aggregate requires at least one BatchReasonCode")


@dataclass(frozen=True)
class CapitalAdequacyBatchResult:
    """Deterministic batch capital-adequacy descriptive evidence."""

    batch_identity: str | None
    contract_identity: ContractIdentity | None
    contract_facts_category: FactCategory | None
    facts_identity: str | None
    observations: tuple[ObservationResult, ...]
    distribution: StopRiskDistribution | None
    sufficient_observation_count: int
    insufficient_observation_count: int
    envelope_aggregates: tuple[EnvelopeAggregate, ...]
    aggregate_decision: AdequacyDecision
    aggregate_reason_codes: tuple[BatchReasonCode, ...]
    input_classification: tuple[str, ...]
    as_of: datetime | None

    def __post_init__(self) -> None:
        for name in ("sufficient_observation_count", "insufficient_observation_count"):
            value = getattr(self, name)
            if type(value) is not int or value < 0:
                raise ValueError(f"batch result {name} must be a non-negative int")
        if not isinstance(self.aggregate_decision, AdequacyDecision):
            raise ValueError("batch result aggregate decision must be an AdequacyDecision")
        if not self.aggregate_reason_codes or not all(
            isinstance(code, BatchReasonCode) for code in self.aggregate_reason_codes
        ):
            raise ValueError("batch result requires at least one BatchReasonCode")
        if not self.input_classification or not all(
            isinstance(item, str) for item in self.input_classification
        ):
            raise ValueError("batch result input classification must be non-empty strings")
        if self.as_of is not None and self.as_of.tzinfo is None:
            raise ValueError("batch result as-of timestamp must be timezone-aware")


def _classify_input(facts: ContractFacts | None) -> tuple[str, ...]:
    return (
        "EXCHANGE_BROKER_FACTS=" + (facts.category.value if facts is not None else "MISSING"),
        "SCENARIO_ASSUMPTIONS=SUPPLIED_SLIPPAGE_AND_STRESS",
        "OBSERVED_JIANGHE=SUPPLIED_INVALIDATION_DISTANCE_TICKS",
        "APPROVED_CONSTRAINTS=SUPPLIED_APPROVED_RISK_CONSTRAINTS",
    )


def _observation_decision(
    envelope: Decimal,
    stress_label: str | None,
    result,
) -> ObservationDecision:
    return ObservationDecision(
        capital_envelope=envelope,
        stress_label=stress_label,
        decision=result.decision,
        reason_codes=result.reason_codes,
        margin_headroom=result.margin_headroom,
        operational_headroom=result.operational_headroom,
        capital_fraction_at_risk=result.capital_fraction_at_risk,
        stress_loss=result.stress_loss,
    )


def evaluate_capital_adequacy_batch(
    input_: CapitalAdequacyBatchInput,
) -> CapitalAdequacyBatchResult:
    """Deterministic, side-effect free batch capital-adequacy analysis."""
    if not isinstance(input_, CapitalAdequacyBatchInput):
        raise ValueError("batch evaluation requires a CapitalAdequacyBatchInput")

    facts = input_.contract_facts
    observations = input_.observations
    envelopes = input_.capital_envelopes
    slippage = input_.slippage
    constraints = input_.approved_constraints
    stress_scenarios = input_.stress_scenarios
    quantile_levels = input_.quantile_levels
    primary_envelope = envelopes[0]

    # -- fail-closed guards before any evaluation --------------------------
    batch_reasons: list[BatchReasonCode] = []
    if facts is None:
        batch_reasons.append(BatchReasonCode.CONTRACT_FACTS_MISSING)
    if not observations:
        batch_reasons.append(BatchReasonCode.NO_OBSERVATIONS)
    if slippage is None:
        batch_reasons.append(BatchReasonCode.SLIPPAGE_ASSUMPTION_MISSING)
    if constraints is None:
        batch_reasons.append(BatchReasonCode.APPROVED_CONSTRAINTS_MISSING)
    elif not constraints.sufficient_for_adequacy:
        batch_reasons.append(BatchReasonCode.APPROVED_CONSTRAINTS_INSUFFICIENT)

    if batch_reasons:
        return CapitalAdequacyBatchResult(
            batch_identity=input_.batch_identity,
            contract_identity=None if facts is None else facts.identity,
            contract_facts_category=None if facts is None else facts.category,
            facts_identity=None if facts is None else facts.identity_id,
            observations=(),
            distribution=None,
            sufficient_observation_count=0,
            insufficient_observation_count=len(observations),
            envelope_aggregates=(),
            aggregate_decision=AdequacyDecision.INSUFFICIENT_EVIDENCE,
            aggregate_reason_codes=tuple(batch_reasons),
            input_classification=_classify_input(facts),
            as_of=input_.as_of,
        )

    # -- evaluate every observation x (envelope, stress) --------------------
    per_observation: list[ObservationResult] = []
    envelope_acc: dict[Decimal, dict[str, object]] = {
        envelope: {
            "pass": 0,
            "fail": 0,
            "insufficient": 0,
            "min_margin_headroom": None,
            "min_operational_headroom": None,
            "max_capital_fraction_at_risk": None,
            "any_insufficient": False,
            "any_fail": False,
        }
        for envelope in envelopes
    }

    for obs in observations:
        invalidation = InvalidationObservation(distance_ticks=obs.distance_ticks, label=obs.label)
        decisions: list[ObservationDecision] = []
        base_primary = None
        for envelope in envelopes:
            base = evaluate_one_lot_capital_adequacy(
                OneLotCapitalAdequacyInput(
                    contract_facts=facts,
                    invalidation=invalidation,
                    capital=envelope,
                    slippage=slippage,
                    approved_constraints=constraints,
                    stress=None,
                )
            )
            if envelope == primary_envelope:
                base_primary = base
            decisions.append(_observation_decision(envelope, None, base))
            for stress in stress_scenarios:
                stressed = evaluate_one_lot_capital_adequacy(
                    OneLotCapitalAdequacyInput(
                        contract_facts=facts,
                        invalidation=invalidation,
                        capital=envelope,
                        slippage=slippage,
                        approved_constraints=constraints,
                        stress=stress,
                    )
                )
                decisions.append(_observation_decision(envelope, stress.label, stressed))

            acc = envelope_acc[envelope]
            if base.decision is AdequacyDecision.PASS:
                acc["pass"] = int(acc["pass"]) + 1
            elif base.decision is AdequacyDecision.FAIL:
                acc["fail"] = int(acc["fail"]) + 1
                acc["any_fail"] = True
            else:
                acc["insufficient"] = int(acc["insufficient"]) + 1
                acc["any_insufficient"] = True
            if base.margin_headroom is not None:
                current = acc["min_margin_headroom"]
                if current is None or base.margin_headroom < current:
                    acc["min_margin_headroom"] = base.margin_headroom
            if base.operational_headroom is not None:
                current = acc["min_operational_headroom"]
                if current is None or base.operational_headroom < current:
                    acc["min_operational_headroom"] = base.operational_headroom
            if base.capital_fraction_at_risk is not None:
                current = acc["max_capital_fraction_at_risk"]
                if current is None or base.capital_fraction_at_risk > current:
                    acc["max_capital_fraction_at_risk"] = base.capital_fraction_at_risk

        per_observation.append(
            ObservationResult(
                observation_id=obs.observation_id,
                distance_ticks=obs.distance_ticks,
                one_lot_stop_risk=base_primary.one_lot_stop_risk,
                one_lot_margin=base_primary.one_lot_margin,
                fee_cost=base_primary.fee_cost,
                slippage_cost=base_primary.slippage_cost,
                decisions=tuple(decisions),
            )
        )

    # -- descriptive stop-risk distribution (base, capital-independent) ----
    sufficient_values: list[Decimal] = []
    for observation in per_observation:
        if observation.one_lot_stop_risk is not None:
            sufficient_values.append(observation.one_lot_stop_risk)
    sorted_values = tuple(sorted(sufficient_values))

    distribution: StopRiskDistribution | None = None
    if sorted_values:
        distribution = StopRiskDistribution(
            count=len(sorted_values),
            min=sorted_values[0],
            max=sorted_values[-1],
            median=_linear_interpolated_quantile(sorted_values, Decimal("0.5")),
            quantiles=tuple(
                (level, _linear_interpolated_quantile(sorted_values, level))
                for level in quantile_levels
            ),
        )

    # -- envelope aggregates ------------------------------------------------
    envelope_aggregates: list[EnvelopeAggregate] = []
    for envelope in envelopes:
        acc = envelope_acc[envelope]
        if acc["any_insufficient"]:
            env_decision = AdequacyDecision.INSUFFICIENT_EVIDENCE
            env_reasons = (BatchReasonCode.OBSERVATION_INSUFFICIENT,)
        elif acc["any_fail"]:
            env_decision = AdequacyDecision.FAIL
            env_reasons = (BatchReasonCode.OBSERVATION_FAIL,)
        else:
            env_decision = AdequacyDecision.PASS
            env_reasons = (BatchReasonCode.OK,)
        envelope_aggregates.append(
            EnvelopeAggregate(
                capital_envelope=envelope,
                pass_count=int(acc["pass"]),
                fail_count=int(acc["fail"]),
                insufficient_count=int(acc["insufficient"]),
                decision=env_decision,
                reason_codes=env_reasons,
                min_margin_headroom=acc["min_margin_headroom"],
                min_operational_headroom=acc["min_operational_headroom"],
                max_capital_fraction_at_risk=acc["max_capital_fraction_at_risk"],
            )
        )

    # -- aggregate decision (base, primary envelope) ------------------------
    primary_acc = envelope_acc[primary_envelope]
    if primary_acc["any_insufficient"]:
        aggregate_decision = AdequacyDecision.INSUFFICIENT_EVIDENCE
        aggregate_reasons = (BatchReasonCode.OBSERVATION_INSUFFICIENT,)
    elif primary_acc["any_fail"]:
        aggregate_decision = AdequacyDecision.FAIL
        aggregate_reasons = (BatchReasonCode.OBSERVATION_FAIL,)
    else:
        aggregate_decision = AdequacyDecision.PASS
        aggregate_reasons = (BatchReasonCode.OK,)

    return CapitalAdequacyBatchResult(
        batch_identity=input_.batch_identity,
        contract_identity=facts.identity,
        contract_facts_category=facts.category,
        facts_identity=facts.identity_id,
        observations=tuple(per_observation),
        distribution=distribution,
        sufficient_observation_count=len(sorted_values),
        insufficient_observation_count=len(observations) - len(sorted_values),
        envelope_aggregates=tuple(envelope_aggregates),
        aggregate_decision=aggregate_decision,
        aggregate_reason_codes=aggregate_reasons,
        input_classification=_classify_input(facts),
        as_of=input_.as_of,
    )


__all__ = [
    "BatchReasonCode",
    "ObservedInvalidation",
    "CapitalAdequacyBatchInput",
    "ObservationDecision",
    "ObservationResult",
    "StopRiskDistribution",
    "EnvelopeAggregate",
    "CapitalAdequacyBatchResult",
    "evaluate_capital_adequacy_batch",
    "_linear_interpolated_quantile",
]

"""Focused tests for the deterministic one-lot capital-adequacy calculator.

All numeric values in this file are synthetic FIXTURE-ONLY numbers for tests.
They are NOT production defaults, NOT permanent risk rules, and NOT the final
RB contract / execution / fee / slippage selection.
"""

import inspect
import re
import unittest
from datetime import datetime, timezone
from decimal import Decimal

from src.capital_adequacy import (
    AdequacyDecision,
    AdequacyReasonCode,
    ApprovedRiskConstraints,
    InvalidationObservation,
    OneLotCapitalAdequacyInput,
    OneLotCapitalAdequacyResult,
    SlippageAssumption,
    StressAssumption,
    evaluate_one_lot_capital_adequacy,
)
from src.contract_facts import (
    FactCategory,
    FactFreshness,
    FactSourceType,
    FeeModel,
    MarginBasis,
    MarginFacts,
    SourceProvenance,
    ContractFacts,
    ContractIdentity,
)

FIXTURE_ONLY = True

NOW = datetime(2026, 1, 15, 3, 30, 0, tzinfo=timezone.utc)


def _source(source_type=FactSourceType.EXCHANGE_OFFICIAL):
    return SourceProvenance(
        source_identity="fixture-source-rb-v0",
        source_type=source_type,
        retrieved_at=NOW,
        source_version="fixture-v0",
        notes="synthetic fixture source",
    )


def _identity():
    return ContractIdentity(exchange="SHFE", product_family="RB", instrument_id="RB2605")


def _current_facts(
    *,
    reference_price=Decimal("3000"),
    margin=None,
    fee=None,
    freshness=FactFreshness.CURRENT,
    is_historical_only=False,
    source_type=FactSourceType.EXCHANGE_OFFICIAL,
):
    return ContractFacts(
        identity=_identity(),
        multiplier=Decimal("10"),
        tick_size=Decimal("1"),
        tick_unit="yuan/ton",
        currency="CNY",
        observed_at=NOW,
        source=_source(source_type),
        category=FactCategory.EXCHANGE_BROKER_FACT,
        freshness=freshness,
        reference_price=reference_price,
        margin=margin,
        fee=fee,
        is_historical_only=is_historical_only,
    )


def _fixture_margin():
    return MarginFacts(
        basis=MarginBasis.PER_LOT_AMOUNT, initial_margin_per_lot=Decimal("4500")
    )


def _fixture_fee():
    return FeeModel(commission_per_lot=Decimal("5"))


def _fixture_constraints(*, min_capital=Decimal("50000")):
    return ApprovedRiskConstraints(
        max_one_lot_stop_risk=Decimal("500"),
        max_capital_fraction_at_risk=Decimal("0.01"),
        min_margin_headroom=Decimal("5000"),
        min_operational_reserve=Decimal("5000"),
        min_capital=min_capital,
    )


def _input(
    *,
    reference_price=Decimal("3000"),
    margin=None,
    fee=None,
    capital=Decimal("100000"),
    invalidation_ticks=Decimal("20"),
    slippage_ticks=Decimal("2"),
    constraints=None,
    stress=None,
    freshness=FactFreshness.CURRENT,
    is_historical_only=False,
    source_type=FactSourceType.EXCHANGE_OFFICIAL,
):
    facts = _current_facts(
        reference_price=reference_price,
        margin=margin,
        fee=fee,
        freshness=freshness,
        is_historical_only=is_historical_only,
        source_type=source_type,
    )
    return OneLotCapitalAdequacyInput(
        contract_facts=facts,
        invalidation=(
            InvalidationObservation(distance_ticks=invalidation_ticks)
            if invalidation_ticks is not None
            else None
        ),
        capital=capital,
        slippage=SlippageAssumption(ticks=slippage_ticks) if slippage_ticks is not None else None,
        approved_constraints=constraints,
        stress=stress,
    )


def _fully_bound():
    return _input(
        margin=_fixture_margin(),
        fee=_fixture_fee(),
        constraints=_fixture_constraints(),
    )


class ArithmeticAndComputationTests(unittest.TestCase):
    def test_exact_unit_tick_multiplier_arithmetic(self):
        result = evaluate_one_lot_capital_adequacy(_fully_bound())
        self.assertEqual(result.decision, AdequacyDecision.PASS)
        self.assertEqual(result.tick_value, Decimal("10"))  # 10 tons/lot * 1 yuan/ton
        self.assertEqual(result.notional_per_lot, Decimal("30000"))  # 3000 * 10

    def test_one_lot_margin_computation_from_supplied_facts(self):
        result = evaluate_one_lot_capital_adequacy(_fully_bound())
        self.assertEqual(result.one_lot_margin, Decimal("4500"))

    def test_invalidation_distance_risk_computation(self):
        result = evaluate_one_lot_capital_adequacy(_fully_bound())
        # 20 ticks * 1 yuan/ton = 20 yuan/ton price move; * 10 tons/lot = 200.
        self.assertEqual(result.invalidation_price_move, Decimal("20"))
        self.assertEqual(result.stop_risk_before_slippage_fees, Decimal("200"))

    def test_slippage_and_fee_aggregation(self):
        result = evaluate_one_lot_capital_adequacy(_fully_bound())
        self.assertEqual(result.slippage_cost, Decimal("20"))  # 2 ticks * 10
        self.assertEqual(result.fee_cost, Decimal("5"))
        self.assertEqual(result.one_lot_stop_risk, Decimal("225"))

    def test_capital_fraction_and_headroom(self):
        result = evaluate_one_lot_capital_adequacy(_fully_bound())
        self.assertEqual(result.margin_headroom, Decimal("95500"))
        self.assertEqual(result.operational_headroom, Decimal("95275"))
        self.assertEqual(result.capital_fraction_at_risk, Decimal("0.00225"))

    def test_stress_explicit_loss_scenario(self):
        stress = StressAssumption(explicit_loss=Decimal("1000"))
        result = evaluate_one_lot_capital_adequacy(
            _input(
                margin=_fixture_margin(),
                fee=_fixture_fee(),
                constraints=_fixture_constraints(),
                stress=stress,
            )
        )
        self.assertEqual(result.stress_loss, Decimal("1000"))
        # worst loss = 225 + 1000 = 1225; fraction 0.01225 exceeds approved 0.01 => FAIL.
        self.assertEqual(result.capital_fraction_at_risk_stress_inclusive, Decimal("0.01225"))
        self.assertEqual(result.decision, AdequacyDecision.FAIL)
        self.assertIn(AdequacyReasonCode.CAPITAL_FRACTION_EXCEEDS_APPROVED_LIMIT, result.reason_codes)

    def test_stress_price_move_scenario(self):
        stress = StressAssumption(price_move_ticks=Decimal("50"))
        result = evaluate_one_lot_capital_adequacy(
            _input(
                margin=_fixture_margin(),
                fee=_fixture_fee(),
                constraints=_fixture_constraints(),
                stress=stress,
            )
        )
        self.assertEqual(result.stress_loss, Decimal("500"))  # 50 ticks * 10
        # worst loss = 225 + 500 = 725; 100000 - 4500 - 725 = 94775
        self.assertEqual(result.operational_headroom, Decimal("94775"))

    def test_missing_invalidation_distance_is_insufficient(self):
        result = evaluate_one_lot_capital_adequacy(
            _input(
                margin=_fixture_margin(),
                fee=_fixture_fee(),
                constraints=_fixture_constraints(),
                invalidation_ticks=None,
            )
        )
        self.assertEqual(result.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.INVALIDATION_DISTANCE_MISSING, result.reason_codes)
        self.assertIsNone(result.one_lot_stop_risk)


class MissingFactFailClosedTests(unittest.TestCase):
    def test_missing_margin_is_insufficient_not_zero(self):
        result = evaluate_one_lot_capital_adequacy(
            _input(fee=_fixture_fee(), constraints=_fixture_constraints())
        )
        self.assertEqual(result.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.MARGIN_FACTS_MISSING, result.reason_codes)
        self.assertIsNone(result.one_lot_margin)
        self.assertIsNone(result.margin_headroom)

    def test_missing_fee_is_insufficient_not_fabricated(self):
        result = evaluate_one_lot_capital_adequacy(
            _input(margin=_fixture_margin(), constraints=_fixture_constraints())
        )
        self.assertEqual(result.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.FEE_FACTS_MISSING, result.reason_codes)
        self.assertIsNone(result.fee_cost)
        self.assertIsNone(result.one_lot_stop_risk)

    def test_missing_reference_price_is_insufficient(self):
        result = evaluate_one_lot_capital_adequacy(
            _input(
                reference_price=None,
                margin=_fixture_margin(),
                fee=_fixture_fee(),
                constraints=_fixture_constraints(),
            )
        )
        self.assertEqual(result.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.REFERENCE_PRICE_MISSING, result.reason_codes)

    def test_missing_capital_is_insufficient(self):
        result = evaluate_one_lot_capital_adequacy(
            _input(
                margin=_fixture_margin(),
                fee=_fixture_fee(),
                constraints=_fixture_constraints(),
                capital=None,
            )
        )
        self.assertEqual(result.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.CAPITAL_MISSING, result.reason_codes)
        self.assertIsNone(result.capital_fraction_at_risk)

    def test_missing_slippage_is_insufficient(self):
        result = evaluate_one_lot_capital_adequacy(
            _input(
                margin=_fixture_margin(),
                fee=_fixture_fee(),
                constraints=_fixture_constraints(),
                slippage_ticks=None,
            )
        )
        self.assertEqual(result.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.SLIPPAGE_ASSUMPTION_MISSING, result.reason_codes)

    def test_stale_facts_are_insufficient(self):
        result = evaluate_one_lot_capital_adequacy(
            _input(
                margin=_fixture_margin(),
                fee=_fixture_fee(),
                constraints=_fixture_constraints(),
                freshness=FactFreshness.STALE,
            )
        )
        self.assertEqual(result.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.CONTRACT_FACTS_NOT_CURRENT, result.reason_codes)

    def test_zero_fee_differs_from_unknown_fee(self):
        zero_fee = _input(
            margin=_fixture_margin(),
            fee=FeeModel(commission_per_lot=Decimal("0")),
            constraints=_fixture_constraints(),
        )
        zero_result = evaluate_one_lot_capital_adequacy(zero_fee)
        self.assertEqual(zero_result.fee_cost, Decimal("0"))
        self.assertEqual(zero_result.decision, AdequacyDecision.PASS)

        unknown_fee = _input(margin=_fixture_margin(), constraints=_fixture_constraints())
        unknown_result = evaluate_one_lot_capital_adequacy(unknown_fee)
        self.assertIsNone(unknown_result.fee_cost)
        self.assertEqual(unknown_result.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)

    def test_historical_facts_are_not_current_truth(self):
        result = evaluate_one_lot_capital_adequacy(
            _input(
                margin=_fixture_margin(),
                fee=_fixture_fee(),
                constraints=_fixture_constraints(),
                freshness=FactFreshness.STALE,
                is_historical_only=True,
                source_type=FactSourceType.HISTORICAL_CANONICAL_METADATA,
            )
        )
        self.assertEqual(result.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.CONTRACT_FACTS_NOT_CURRENT, result.reason_codes)


class DecisionAgainstApprovedConstraintsTests(unittest.TestCase):
    def test_fully_bound_fixture_can_produce_pass(self):
        result = evaluate_one_lot_capital_adequacy(_fully_bound())
        self.assertEqual(result.decision, AdequacyDecision.PASS)
        self.assertEqual(result.reason_codes, (AdequacyReasonCode.OK,))

    def test_stop_risk_exceeding_approved_limit_fails(self):
        constraints = _fixture_constraints()
        constraints = ApprovedRiskConstraints(
            max_one_lot_stop_risk=Decimal("100"),
            max_capital_fraction_at_risk=constraints.max_capital_fraction_at_risk,
            min_margin_headroom=constraints.min_margin_headroom,
            min_operational_reserve=constraints.min_operational_reserve,
            min_capital=constraints.min_capital,
        )
        result = evaluate_one_lot_capital_adequacy(
            _input(margin=_fixture_margin(), fee=_fixture_fee(), constraints=constraints)
        )
        self.assertEqual(result.decision, AdequacyDecision.FAIL)
        self.assertIn(AdequacyReasonCode.STOP_RISK_EXCEEDS_APPROVED_LIMIT, result.reason_codes)

    def test_margin_headroom_below_approved_fails(self):
        constraints = _fixture_constraints(min_capital=Decimal("50000"))
        constraints = ApprovedRiskConstraints(
            max_one_lot_stop_risk=constraints.max_one_lot_stop_risk,
            max_capital_fraction_at_risk=constraints.max_capital_fraction_at_risk,
            min_margin_headroom=Decimal("96000"),
            min_operational_reserve=constraints.min_operational_reserve,
            min_capital=constraints.min_capital,
        )
        result = evaluate_one_lot_capital_adequacy(
            _input(margin=_fixture_margin(), fee=_fixture_fee(), constraints=constraints)
        )
        self.assertEqual(result.decision, AdequacyDecision.FAIL)
        self.assertIn(AdequacyReasonCode.MARGIN_HEADROOM_BELOW_APPROVED, result.reason_codes)

    def test_operational_reserve_below_approved_fails(self):
        constraints = ApprovedRiskConstraints(
            max_one_lot_stop_risk=Decimal("500"),
            max_capital_fraction_at_risk=Decimal("0.01"),
            min_margin_headroom=Decimal("5000"),
            min_operational_reserve=Decimal("96000"),
        )
        result = evaluate_one_lot_capital_adequacy(
            _input(margin=_fixture_margin(), fee=_fixture_fee(), constraints=constraints)
        )
        self.assertEqual(result.decision, AdequacyDecision.FAIL)
        self.assertIn(AdequacyReasonCode.OPERATIONAL_RESERVE_BELOW_APPROVED, result.reason_codes)

    def test_missing_approved_constraint_prevents_false_pass(self):
        result = evaluate_one_lot_capital_adequacy(
            _input(margin=_fixture_margin(), fee=_fixture_fee(), constraints=None)
        )
        self.assertEqual(result.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.APPROVED_CONSTRAINTS_MISSING, result.reason_codes)

    def test_insufficient_approved_constraint_set_prevents_false_pass(self):
        # Only a risk ceiling supplied; margin headroom / operational reserve missing.
        constraints = ApprovedRiskConstraints(max_one_lot_stop_risk=Decimal("500"))
        result = evaluate_one_lot_capital_adequacy(
            _input(margin=_fixture_margin(), fee=_fixture_fee(), constraints=constraints)
        )
        self.assertEqual(result.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.APPROVED_CONSTRAINTS_INSUFFICIENT, result.reason_codes)

    def test_capital_below_approved_minimum_fails(self):
        constraints = _fixture_constraints(min_capital=Decimal("200000"))
        result = evaluate_one_lot_capital_adequacy(
            _input(
                margin=_fixture_margin(),
                fee=_fixture_fee(),
                constraints=constraints,
                capital=Decimal("100000"),
            )
        )
        self.assertEqual(result.decision, AdequacyDecision.FAIL)
        self.assertIn(AdequacyReasonCode.CAPITAL_BELOW_APPROVED_MINIMUM, result.reason_codes)


class MinimumViableCapitalTests(unittest.TestCase):
    def test_minimum_viable_capital_on_pass(self):
        result = evaluate_one_lot_capital_adequacy(_fully_bound())
        self.assertEqual(result.decision, AdequacyDecision.PASS)
        # bounds: 4500+5000=9500; 4500+225+5000=9725; 225/0.01=22500; min_capital 50000
        self.assertEqual(result.minimum_viable_capital, Decimal("50000"))

    def test_minimum_viable_capital_without_min_capital(self):
        constraints = _fixture_constraints(min_capital=None)
        result = evaluate_one_lot_capital_adequacy(
            _input(margin=_fixture_margin(), fee=_fixture_fee(), constraints=constraints)
        )
        self.assertEqual(result.decision, AdequacyDecision.PASS)
        # max(9500, 9725, 22500) = 22500
        self.assertEqual(result.minimum_viable_capital, Decimal("22500"))

    def test_minimum_viable_capital_not_produced_on_fail(self):
        constraints = ApprovedRiskConstraints(
            max_one_lot_stop_risk=Decimal("100"),
            max_capital_fraction_at_risk=Decimal("0.01"),
            min_margin_headroom=Decimal("5000"),
            min_operational_reserve=Decimal("5000"),
        )
        result = evaluate_one_lot_capital_adequacy(
            _input(margin=_fixture_margin(), fee=_fixture_fee(), constraints=constraints)
        )
        self.assertEqual(result.decision, AdequacyDecision.FAIL)
        self.assertIsNone(result.minimum_viable_capital)


class ResultStructureTests(unittest.TestCase):
    def test_reason_codes_are_structured_enum_values(self):
        for result in (
            evaluate_one_lot_capital_adequacy(_fully_bound()),
            evaluate_one_lot_capital_adequacy(
                _input(margin=_fixture_margin(), fee=_fixture_fee(), constraints=None)
            ),
        ):
            self.assertTrue(result.reason_codes)
            for code in result.reason_codes:
                self.assertIsInstance(code, AdequacyReasonCode)

    def test_missing_contract_facts_is_insufficient(self):
        result = evaluate_one_lot_capital_adequacy(OneLotCapitalAdequacyInput())
        self.assertEqual(result.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.CONTRACT_FACTS_MISSING, result.reason_codes)


class NoProductionDefaultsTests(unittest.TestCase):
    def test_no_fixture_numbers_exported_as_production_defaults(self):
        import src.capital_adequacy as module

        defaults = [name for name in vars(module) if name.startswith("DEFAULT_")]
        self.assertEqual(defaults, [])
        source = inspect.getsource(module)
        self.assertNotIn("100000", source)
        self.assertNotIn("100_000", source)
        # No module-level numeric default assignments for slippage/fee/capital/risk.
        self.assertIsNone(
            re.search(
                r"^\s*(?:SLIPPAGE|FEE|CAPITAL|RISK|MARGIN)[A-Z_]*\s*=\s*Decimal",
                source,
                re.MULTILINE,
            )
        )


if __name__ == "__main__":
    unittest.main()

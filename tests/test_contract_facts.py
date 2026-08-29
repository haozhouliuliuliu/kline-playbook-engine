"""Focused tests for the source-aware contract facts schema.

All numeric values in this file are synthetic FIXTURE-ONLY numbers for tests.
They are NOT production defaults and NOT permanent risk rules.
"""

import inspect
import re
import unittest
from dataclasses import replace
from datetime import datetime, timezone
from decimal import Decimal

from src.contract_facts import (
    FactCategory,
    FactFreshness,
    FactSourceType,
    FeeModel,
    MarginBasis,
    MarginFacts,
    PriceLimitFacts,
    SourceProvenance,
    ContractFacts,
    ContractIdentity,
    current_use_eligibility,
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


def _contract(
    *,
    freshness=FactFreshness.CURRENT,
    category=FactCategory.EXCHANGE_BROKER_FACT,
    reference_price=Decimal("3000"),
    margin=None,
    fee=None,
    price_limits=None,
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
        category=category,
        freshness=freshness,
        reference_price=reference_price,
        margin=margin,
        fee=fee,
        price_limits=price_limits,
        is_historical_only=is_historical_only,
    )


class ContractFactsArithmeticTests(unittest.TestCase):
    def test_tick_value_is_multiplier_times_tick(self):
        facts = _contract()
        self.assertEqual(facts.tick_value, Decimal("10"))

    def test_notional_per_lot(self):
        facts = _contract(reference_price=Decimal("3000"))
        self.assertEqual(facts.notional_per_lot(Decimal("3000")), Decimal("30000"))

    def test_reference_price_missing_stays_none(self):
        facts = _contract(reference_price=None)
        self.assertIsNone(facts.reference_price)

    def test_identity_is_sha256(self):
        self.assertRegex(_contract().identity_id, r"^[0-9a-f]{64}$")
        self.assertRegex(_identity().identity_id, r"^[0-9a-f]{64}$")

    def test_identity_binds_every_nested_economic_fact_deterministically(self):
        base = _contract(
            margin=MarginFacts(
                basis=MarginBasis.PER_LOT_AMOUNT,
                initial_margin_per_lot=Decimal("4500"),
                maintenance_margin_per_lot=Decimal("4000"),
                currency="CNY",
            ),
            fee=FeeModel(commission_per_lot=Decimal("5"), currency="CNY"),
            price_limits=PriceLimitFacts(
                lower_price_limit=Decimal("2800"),
                upper_price_limit=Decimal("3200"),
                basis="daily-settlement",
                currency="CNY",
            ),
        )
        same = replace(base)
        margin_changed = replace(
            base,
            margin=replace(base.margin, initial_margin_per_lot=Decimal("4501")),
        )
        fee_changed = replace(
            base,
            fee=replace(base.fee, commission_per_lot=Decimal("6")),
        )
        price_limit_changed = replace(
            base,
            price_limits=replace(base.price_limits, upper_price_limit=Decimal("3201")),
        )

        self.assertEqual(base.identity_id, same.identity_id)
        self.assertNotEqual(base.identity_id, margin_changed.identity_id)
        self.assertNotEqual(base.identity_id, fee_changed.identity_id)
        self.assertNotEqual(base.identity_id, price_limit_changed.identity_id)
        self.assertEqual(base.identity_id, _contract(
            margin=base.margin,
            fee=base.fee,
            price_limits=base.price_limits,
        ).identity_id)


class MarginFactsTests(unittest.TestCase):
    def test_per_lot_margin_amount(self):
        margin = MarginFacts(
            basis=MarginBasis.PER_LOT_AMOUNT, initial_margin_per_lot=Decimal("4500")
        )
        self.assertEqual(margin.one_lot_margin_amount(Decimal("30000")), Decimal("4500"))

    def test_percent_margin_amount(self):
        margin = MarginFacts(
            basis=MarginBasis.PERCENT_OF_CONTRACT_VALUE,
            initial_margin_percent=Decimal("12"),
        )
        self.assertEqual(margin.one_lot_margin_amount(Decimal("30000")), Decimal("3600"))

    def test_missing_initial_margin_returns_none(self):
        margin = MarginFacts(
            basis=MarginBasis.PER_LOT_AMOUNT, maintenance_margin_per_lot=Decimal("3500")
        )
        self.assertIsNone(margin.one_lot_margin_amount(Decimal("30000")))

    def test_unit_conflation_rejected(self):
        with self.assertRaises(ValueError):
            MarginFacts(
                basis=MarginBasis.PER_LOT_AMOUNT,
                initial_margin_per_lot=Decimal("4500"),
                initial_margin_percent=Decimal("12"),
            )
        with self.assertRaises(ValueError):
            MarginFacts(
                basis=MarginBasis.PERCENT_OF_CONTRACT_VALUE,
                initial_margin_per_lot=Decimal("4500"),
            )

    def test_empty_margin_facts_rejected(self):
        with self.assertRaises(ValueError):
            MarginFacts(basis=MarginBasis.PER_LOT_AMOUNT)


class FeeModelTests(unittest.TestCase):
    def test_zero_per_lot_is_explicit_zero(self):
        model = FeeModel(commission_per_lot=Decimal("0"))
        self.assertEqual(model.cost_for(Decimal("30000")), Decimal("0"))

    def test_percent_fee(self):
        model = FeeModel(commission_percent=Decimal("0.01"))
        self.assertEqual(model.cost_for(Decimal("30000")), Decimal("3"))

    def test_both_components_sum(self):
        model = FeeModel(commission_per_lot=Decimal("5"), commission_percent=Decimal("0.01"))
        self.assertEqual(model.cost_for(Decimal("30000")), Decimal("8"))

    def test_unknown_fee_requires_a_component(self):
        with self.assertRaises(ValueError):
            FeeModel()

    def test_unknown_fee_distinct_from_explicit_zero(self):
        unknown = _contract(fee=None)
        zero = _contract(fee=FeeModel(commission_per_lot=Decimal("0")))
        self.assertIsNone(unknown.fee)
        self.assertEqual(zero.fee.cost_for(Decimal("30000")), Decimal("0"))


class PriceLimitFactsTests(unittest.TestCase):
    def test_at_least_one_bound_required(self):
        with self.assertRaises(ValueError):
            PriceLimitFacts(
                lower_price_limit=None,
                upper_price_limit=None,
                basis="PRICE_POINTS",
                currency="CNY",
            )

    def test_supplied_bounds_kept(self):
        limits = PriceLimitFacts(
            lower_price_limit=Decimal("2850"),
            upper_price_limit=Decimal("3150"),
            basis="PRICE_POINTS",
            currency="CNY",
        )
        self.assertEqual(limits.lower_price_limit, Decimal("2850"))
        self.assertEqual(limits.upper_price_limit, Decimal("3150"))


class CurrentUseEligibilityTests(unittest.TestCase):
    def test_current_fact_is_eligible(self):
        ok, why = current_use_eligibility(_contract(freshness=FactFreshness.CURRENT))
        self.assertTrue(ok)
        self.assertEqual(why, "CURRENT")

    def test_stale_fact_not_eligible(self):
        ok, why = current_use_eligibility(_contract(freshness=FactFreshness.STALE))
        self.assertFalse(ok)
        self.assertEqual(why, "STALE")

    def test_unknown_freshness_not_eligible(self):
        ok, why = current_use_eligibility(_contract(freshness=FactFreshness.UNKNOWN))
        self.assertFalse(ok)
        self.assertEqual(why, "UNKNOWN")

    def test_scenario_assumption_not_eligible(self):
        ok, why = current_use_eligibility(_contract(category=FactCategory.SCENARIO_ASSUMPTION))
        self.assertFalse(ok)
        self.assertEqual(why, "NOT_EXCHANGE_BROKER_FACT")

    def test_historical_only_never_eligible(self):
        facts = _contract(
            freshness=FactFreshness.STALE,
            is_historical_only=True,
            source_type=FactSourceType.HISTORICAL_CANONICAL_METADATA,
        )
        ok, why = current_use_eligibility(facts)
        self.assertFalse(ok)
        self.assertEqual(why, "HISTORICAL_ONLY_FACTS_ARE_NOT_CURRENT_TRUTH")


class HistoricalLabelTests(unittest.TestCase):
    def test_historical_only_cannot_be_current(self):
        with self.assertRaises(ValueError):
            _contract(
                freshness=FactFreshness.CURRENT,
                is_historical_only=True,
                source_type=FactSourceType.HISTORICAL_CANONICAL_METADATA,
            )

    def test_historical_metadata_must_be_marked_historical_only(self):
        with self.assertRaises(ValueError):
            _contract(
                freshness=FactFreshness.STALE,
                is_historical_only=False,
                source_type=FactSourceType.HISTORICAL_CANONICAL_METADATA,
            )

    def test_historical_metadata_can_never_be_current_source(self):
        with self.assertRaises(ValueError):
            _contract(
                freshness=FactFreshness.CURRENT,
                is_historical_only=False,
                source_type=FactSourceType.HISTORICAL_CANONICAL_METADATA,
            )


class ProvenanceAndValidationTests(unittest.TestCase):
    def test_naive_retrieval_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            SourceProvenance(
                source_identity="x",
                source_type=FactSourceType.EXCHANGE_OFFICIAL,
                retrieved_at=datetime(2026, 1, 1),
                source_version="v0",
            )

    def test_naive_observed_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            ContractFacts(
                identity=_identity(),
                multiplier=Decimal("10"),
                tick_size=Decimal("1"),
                tick_unit="yuan/ton",
                currency="CNY",
                observed_at=datetime(2026, 1, 1),
                source=_source(),
                category=FactCategory.EXCHANGE_BROKER_FACT,
                freshness=FactFreshness.CURRENT,
            )

    def test_non_positive_multiplier_rejected(self):
        with self.assertRaises(ValueError):
            ContractFacts(
                identity=_identity(),
                multiplier=Decimal("0"),
                tick_size=Decimal("1"),
                tick_unit="yuan/ton",
                currency="CNY",
                observed_at=NOW,
                source=_source(),
                category=FactCategory.EXCHANGE_BROKER_FACT,
                freshness=FactFreshness.CURRENT,
            )

    def test_margin_field_type_enforced(self):
        with self.assertRaises(ValueError):
            _contract(margin=FeeModel(commission_per_lot=Decimal("1")))


class NoProductionDefaultsTests(unittest.TestCase):
    def test_no_fixture_numbers_exported_as_production_defaults(self):
        import src.contract_facts as module

        defaults = [name for name in vars(module) if name.startswith("DEFAULT_")]
        self.assertEqual(defaults, [])
        source = inspect.getsource(module)
        self.assertNotIn("100000", source)
        self.assertNotIn("100_000", source)
        # No module-level numeric default assignments for slippage/fee/margin.
        self.assertIsNone(re.search(r"^\s*(?:SLIPPAGE|FEE|MARGIN|CAPITAL)[A-Z_]*\s*=\s*Decimal", source, re.MULTILINE))


if __name__ == "__main__":
    unittest.main()

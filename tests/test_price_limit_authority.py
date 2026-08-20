import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from src.price_limit_authority import (
    PER_DAY_STATUS_BOUND,
    PER_DAY_STATUS_CONFLICT,
    PER_DAY_STATUS_UNKNOWN,
    BasePriceLimitRule,
    PerDayLimitFact,
    PerDayLimitResolution,
    PriceLimitAuthority,
    PriceLimitAuthorityError,
    PriceLimitSource,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUTHORITY_JSON = PROJECT_ROOT / "docs" / "evidence" / "HISTORICAL_PRICE_LIMIT_AUTHORITY_V0_1.json"

PRODUCTS = ("cu", "al", "ni", "au", "ag", "rb")
BASE_LIMIT_BY_PRODUCT = {"cu": "3", "al": "3", "ni": "4", "au": "3", "ag": "3", "rb": "3"}
WINDOW_START = date(2024, 1, 1)
WINDOW_END = date(2025, 12, 31)


def _test_source(source_id="TST", classification="REPOSITORY_VERIFIED_REFERENCE", sha256=None):
    return PriceLimitSource(
        source_id=source_id,
        authority="deterministic-synthetic-test-reference",
        title="synthetic test source",
        source_url="https://example.invalid/test",
        classification=classification,
        retrieved_at=None,
        artifact_sha256=sha256,
    )


def _bound_official_source():
    return _test_source(source_id="TST-BOUND", classification="EXACT_OFFICIAL_BOUND", sha256="a" * 64)


class LoadedAuthorityTests(unittest.TestCase):
    """Tests against the committed machine-readable authority evidence."""

    @classmethod
    def setUpClass(cls):
        cls.authority = PriceLimitAuthority.from_evidence_json(AUTHORITY_JSON)

    def test_products_complete(self):
        self.assertEqual(set(self.authority.products), set(PRODUCTS))

    def test_window(self):
        self.assertEqual(self.authority.window_start, WINDOW_START)
        self.assertEqual(self.authority.window_end, WINDOW_END)

    def test_authority_identity_is_sha256(self):
        self.assertRegex(self.authority.authority_identity(), r"^[0-9a-f]{64}$")

    def test_committed_identity_matches_computed(self):
        # from_evidence_json already verifies the recorded identity; this guards the guard.
        raw = __import__("json").loads(AUTHORITY_JSON.read_text(encoding="utf-8"))
        self.assertEqual(raw["identity"], self.authority.authority_identity())


class BaseRuleTests(unittest.TestCase):
    """Base contract-text limit is bound for every product across the 2024-2025 window."""

    @classmethod
    def setUpClass(cls):
        cls.authority = PriceLimitAuthority.from_evidence_json(AUTHORITY_JSON)

    def test_base_rule_resolves_each_product(self):
        for product, expected in BASE_LIMIT_BY_PRODUCT.items():
            with self.subTest(product=product):
                for day in (date(2024, 1, 15), date(2024, 7, 1), date(2025, 6, 30), date(2025, 12, 15)):
                    rule = self.authority.base_rule(product, day)
                    self.assertEqual(rule.base_limit_pct, Decimal(expected))
                    self.assertEqual(rule.classification, "BASE_CONTRACT_TEXT_BOUND")
                    self.assertTrue(rule.covers(day))

    def test_base_rule_binding_notice_present(self):
        for product in PRODUCTS:
            rule = self.authority.base_rule(product, date(2024, 6, 17))
            self.assertTrue(rule.binding_notice.strip())
            self.assertTrue(rule.source_references)

    def test_base_rule_missing_product_fails_closed(self):
        with self.assertRaises(PriceLimitAuthorityError):
            self.authority.base_rule("zz", date(2024, 6, 17))

    def test_base_rule_outside_effective_period_fails_closed(self):
        # All products except au start effective 2023-01-17; a 2022 day is uncovered.
        for product in ("cu", "al", "ni", "ag", "rb"):
            with self.subTest(product=product):
                with self.assertRaises(PriceLimitAuthorityError):
                    self.authority.base_rule(product, date(2022, 6, 17))

    def test_au_effective_start_is_2020(self):
        self.assertEqual(self.authority.base_rule("au", date(2020, 12, 1)).effective_start, date(2020, 8, 31))

    def test_base_rule_day_after_window_fails_closed(self):
        with self.assertRaises(PriceLimitAuthorityError):
            self.authority.base_rule("cu", date(2026, 1, 2))


class PerDayFailClosedTests(unittest.TestCase):
    """The critical anti-backfill property: no per-day fact is ever derived from a base rule."""

    @classmethod
    def setUpClass(cls):
        cls.authority = PriceLimitAuthority.from_evidence_json(AUTHORITY_JSON)

    def test_no_bound_per_day_facts_in_committed_authority(self):
        self.assertEqual(self.authority.per_day_fact_count, 0)

    def test_per_day_is_unknown_across_window(self):
        days = (
            date(2024, 1, 15),
            date(2024, 6, 17),
            date(2024, 12, 30),
            date(2025, 1, 3),
            date(2025, 6, 30),
            date(2025, 12, 15),
        )
        for product in PRODUCTS:
            for day in days:
                with self.subTest(product=product, day=day.isoformat()):
                    resolution = self.authority.per_day_resolution(product, day)
                    self.assertEqual(resolution.status, PER_DAY_STATUS_UNKNOWN)
                    self.assertIsNone(resolution.per_day_fact)
                    self.assertEqual(self.authority.per_day_classification(product, day), "UNKNOWN")

    def test_require_per_day_fact_fails_closed_for_real_window(self):
        # Execution simulation cannot claim a real price-limit fill without a bound fact.
        for product in PRODUCTS:
            with self.subTest(product=product):
                with self.assertRaises(PriceLimitAuthorityError):
                    self.authority.require_per_day_fact(product, date(2024, 6, 17))

    def test_base_rule_alone_never_satisfies_per_day(self):
        # Even though base rules are bound, per-day lookup must remain UNKNOWN.
        rule = self.authority.base_rule("cu", date(2024, 6, 17))
        self.assertEqual(rule.base_limit_pct, Decimal("3"))
        self.assertEqual(self.authority.per_day_resolution("cu", date(2024, 6, 17)).status, PER_DAY_STATUS_UNKNOWN)


class SyntheticPerDayBoundTests(unittest.TestCase):
    """The interface can hold future bound per-day facts, clearly labeled as synthetic."""

    def _authority_with_fact(self):
        base = PriceLimitAuthority.from_evidence_json(AUTHORITY_JSON)
        fact = PerDayLimitFact(
            fact_id="TEST-SYNTHETIC-cu-2024-06-17",
            product="cu",
            trading_day=date(2024, 6, 17),
            limit_pct=Decimal("3"),
            adjustment_notice="TEST-SYNTHETIC-NOTICE (not an official fact; interface demonstration only)",
            classification="PER_DAY_ADJUSTMENT_BOUND",
            source_references=("TST-BOUND",),
        )
        sources = list(base._sources.values()) + [_bound_official_source()]
        return PriceLimitAuthority(
            schema_version=base.schema_version,
            exchange=base.exchange,
            window_start=base.window_start,
            window_end=base.window_end,
            rules=[rule for rule in base._rules],
            per_day_facts=(fact,),
            sources=sources,
        )

    def test_bound_fact_returns_bounded_resolution(self):
        authority = self._authority_with_fact()
        resolution = authority.per_day_resolution("cu", date(2024, 6, 17))
        self.assertEqual(resolution.status, PER_DAY_STATUS_BOUND)
        self.assertEqual(resolution.per_day_fact.limit_pct, Decimal("3"))
        self.assertEqual(authority.per_day_classification("cu", date(2024, 6, 17)), "PER_DAY_ADJUSTMENT_BOUND")

    def test_bound_fact_does_not_leak_to_other_days(self):
        authority = self._authority_with_fact()
        self.assertEqual(authority.per_day_resolution("cu", date(2024, 6, 18)).status, PER_DAY_STATUS_UNKNOWN)
        self.assertEqual(authority.per_day_resolution("al", date(2024, 6, 17)).status, PER_DAY_STATUS_UNKNOWN)

    def test_require_returns_bound_fact(self):
        authority = self._authority_with_fact()
        fact = authority.require_per_day_fact("cu", date(2024, 6, 17))
        self.assertEqual(fact.product, "cu")
        self.assertEqual(fact.trading_day, date(2024, 6, 17))

    def test_adding_bound_fact_changes_authority_identity(self):
        base = PriceLimitAuthority.from_evidence_json(AUTHORITY_JSON)
        extended = self._authority_with_fact()
        self.assertNotEqual(base.authority_identity(), extended.authority_identity())


class ConflictTests(unittest.TestCase):
    def test_conflicting_per_day_facts_resolve_conflict(self):
        base = PriceLimitAuthority.from_evidence_json(AUTHORITY_JSON)
        facts = (
            PerDayLimitFact(
                fact_id="TEST-cu-a",
                product="cu",
                trading_day=date(2024, 6, 17),
                limit_pct=Decimal("3"),
                adjustment_notice="TEST-NOTICE-A",
                classification="PER_DAY_ADJUSTMENT_BOUND",
            ),
            PerDayLimitFact(
                fact_id="TEST-cu-b",
                product="cu",
                trading_day=date(2024, 6, 17),
                limit_pct=Decimal("5"),
                adjustment_notice="TEST-NOTICE-B",
                classification="PER_DAY_ADJUSTMENT_BOUND",
            ),
        )
        authority = PriceLimitAuthority(
            schema_version=base.schema_version,
            exchange=base.exchange,
            window_start=base.window_start,
            window_end=base.window_end,
            rules=list(base._rules),
            per_day_facts=facts,
            sources=list(base._sources.values()),
        )
        resolution = authority.per_day_resolution("cu", date(2024, 6, 17))
        self.assertEqual(resolution.status, PER_DAY_STATUS_CONFLICT)
        with self.assertRaises(PriceLimitAuthorityError):
            authority.require_per_day_fact("cu", date(2024, 6, 17))


class SchemaValidationTests(unittest.TestCase):
    def test_source_exact_official_requires_sha256(self):
        with self.assertRaises(ValueError):
            _test_source(source_id="X", classification="EXACT_OFFICIAL_BOUND", sha256=None)

    def test_source_unknown_classification_rejected(self):
        with self.assertRaises(ValueError):
            _test_source(source_id="X", classification="NOT_A_CLASSIFICATION")

    def test_base_rule_rejects_non_positive_limit(self):
        with self.assertRaises(ValueError):
            BasePriceLimitRule(
                product="cu",
                trading_code="CU",
                base_limit_pct=Decimal("0"),
                limit_unit="percent",
                symmetric=True,
                basis="symmetric_percent_of_previous_settlement",
                binding_notice="TEST",
                effective_start=date(2024, 1, 1),
                effective_end=date(2025, 12, 31),
                effective_period_proof="TEST",
                classification="BASE_CONTRACT_TEXT_BOUND",
            )

    def test_base_rule_rejects_inverted_period(self):
        with self.assertRaises(ValueError):
            BasePriceLimitRule(
                product="cu",
                trading_code="CU",
                base_limit_pct=Decimal("3"),
                limit_unit="percent",
                symmetric=True,
                basis="symmetric_percent_of_previous_settlement",
                binding_notice="TEST",
                effective_start=date(2025, 12, 31),
                effective_end=date(2024, 1, 1),
                effective_period_proof="TEST",
                classification="BASE_CONTRACT_TEXT_BOUND",
            )

    def test_per_day_adjustment_bound_requires_notice(self):
        with self.assertRaises(ValueError):
            PerDayLimitFact(
                fact_id="T",
                product="cu",
                trading_day=date(2024, 6, 17),
                limit_pct=Decimal("3"),
                adjustment_notice="   ",
                classification="PER_DAY_ADJUSTMENT_BOUND",
            )

    def test_resolution_bounds(self):
        with self.assertRaises(ValueError):
            PerDayLimitResolution(PER_DAY_STATUS_BOUND, "cu", date(2024, 6, 17), None, "missing fact")
        with self.assertRaises(ValueError):
            PerDayLimitResolution(PER_DAY_STATUS_UNKNOWN, "cu", date(2024, 6, 17), PerDayLimitFact(
                fact_id="T", product="cu", trading_day=date(2024, 6, 17), limit_pct=Decimal("3"),
                adjustment_notice="N", classification="PER_DAY_ADJUSTMENT_BOUND",
            ), None)

    def test_authority_rejects_fact_outside_window(self):
        base = PriceLimitAuthority.from_evidence_json(AUTHORITY_JSON)
        with self.assertRaises(PriceLimitAuthorityError):
            PriceLimitAuthority(
                schema_version=base.schema_version,
                exchange=base.exchange,
                window_start=base.window_start,
                window_end=base.window_end,
                rules=list(base._rules),
                per_day_facts=(
                    PerDayLimitFact(
                        fact_id="T", product="cu", trading_day=date(2026, 1, 2), limit_pct=Decimal("3"),
                        adjustment_notice="N", classification="PER_DAY_ADJUSTMENT_BOUND",
                    ),
                ),
            )

    def test_authority_rejects_unknown_source_reference(self):
        base = PriceLimitAuthority.from_evidence_json(AUTHORITY_JSON)
        with self.assertRaises(PriceLimitAuthorityError):
            PriceLimitAuthority(
                schema_version=base.schema_version,
                exchange=base.exchange,
                window_start=base.window_start,
                window_end=base.window_end,
                rules=list(base._rules),
                per_day_facts=(
                    PerDayLimitFact(
                        fact_id="T", product="cu", trading_day=date(2024, 6, 17), limit_pct=Decimal("3"),
                        adjustment_notice="N", classification="PER_DAY_ADJUSTMENT_BOUND",
                        source_references=("NO-SUCH-SOURCE",),
                    ),
                ),
            )

    def test_authority_identity_stable_for_identical_input(self):
        a = PriceLimitAuthority.from_evidence_json(AUTHORITY_JSON)
        b = PriceLimitAuthority.from_evidence_json(AUTHORITY_JSON)
        self.assertEqual(a.authority_identity(), b.authority_identity())


if __name__ == "__main__":
    unittest.main()

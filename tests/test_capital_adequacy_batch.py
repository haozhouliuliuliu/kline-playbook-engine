"""Focused tests for the batch / distribution capital-adequacy analysis.

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
    SlippageAssumption,
    StressAssumption,
)
from src.capital_adequacy_batch import (
    BatchReasonCode,
    CapitalAdequacyBatchInput,
    CapitalAdequacyBatchResult,
    ObservedInvalidation,
    evaluate_capital_adequacy_batch,
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

_UNSET = object()

NOW = datetime(2026, 1, 15, 3, 30, 0, tzinfo=timezone.utc)


def _source():
    return SourceProvenance(
        source_identity="fixture-source-rb-v0",
        source_type=FactSourceType.EXCHANGE_OFFICIAL,
        retrieved_at=NOW,
        source_version="fixture-v0",
        notes="synthetic fixture source",
    )


def _identity():
    return ContractIdentity(exchange="SHFE", product_family="RB", instrument_id="RB2605")


def _fixture_margin():
    return MarginFacts(basis=MarginBasis.PER_LOT_AMOUNT, initial_margin_per_lot=Decimal("4500"))


def _fixture_fee():
    return FeeModel(commission_per_lot=Decimal("5"))


def _fixture_constraints():
    return ApprovedRiskConstraints(
        max_one_lot_stop_risk=Decimal("500"),
        max_capital_fraction_at_risk=Decimal("0.01"),
        min_margin_headroom=Decimal("5000"),
        min_operational_reserve=Decimal("5000"),
        min_capital=Decimal("50000"),
    )


def _facts(
    *,
    reference_price=Decimal("3000"),
    margin=_UNSET,
    fee=_UNSET,
    freshness=FactFreshness.CURRENT,
):
    if margin is _UNSET:
        margin = _fixture_margin()
    if fee is _UNSET:
        fee = _fixture_fee()
    return ContractFacts(
        identity=_identity(),
        multiplier=Decimal("10"),
        tick_size=Decimal("1"),
        tick_unit="yuan/ton",
        currency="CNY",
        observed_at=NOW,
        source=_source(),
        category=FactCategory.EXCHANGE_BROKER_FACT,
        freshness=freshness,
        reference_price=reference_price,
        margin=margin,
        fee=fee,
    )


def _batch(
    *,
    observations,
    facts=_UNSET,
    envelopes=None,
    slippage=None,
    constraints=_UNSET,
    stress_scenarios=(),
    quantile_levels=None,
    batch_identity="fixture-batch-v0",
    as_of=None,
):
    if facts is _UNSET:
        facts = _facts()
    if envelopes is None:
        envelopes = (Decimal("100000"),)
    if slippage is None:
        slippage = SlippageAssumption(ticks=Decimal("2"))
    if constraints is _UNSET:
        constraints = _fixture_constraints()
    obs = tuple(
        ObservedInvalidation(
            observation_id=f"obs-{index}", distance_ticks=Decimal(str(distance))
        )
        for index, distance in enumerate(observations)
    )
    if quantile_levels is None:
        quantile_levels = (Decimal("0.25"), Decimal("0.50"), Decimal("0.75"))
    return CapitalAdequacyBatchInput(
        contract_facts=facts,
        observations=obs,
        capital_envelopes=envelopes,
        slippage=slippage,
        approved_constraints=constraints,
        stress_scenarios=tuple(stress_scenarios),
        quantile_levels=quantile_levels,
        batch_identity=batch_identity,
        as_of=as_of,
    )


class BatchBasicTests(unittest.TestCase):
    def test_batch_handles_multiple_observations(self):
        result = evaluate_capital_adequacy_batch(_batch(observations=[10, 20, 30]))
        self.assertEqual(len(result.observations), 3)
        self.assertEqual(result.sufficient_observation_count, 3)
        self.assertEqual(result.insufficient_observation_count, 0)
        self.assertEqual(result.aggregate_decision, AdequacyDecision.PASS)
        self.assertEqual(result.aggregate_reason_codes, (BatchReasonCode.OK,))
        self.assertIsInstance(result, CapitalAdequacyBatchResult)

    def test_per_observation_stop_risk(self):
        result = evaluate_capital_adequacy_batch(_batch(observations=[20, 40]))
        stops = [obs.one_lot_stop_risk for obs in result.observations]
        # 20 ticks -> 200 + 20 slippage + 5 fee = 225; 40 -> 400 + 20 + 5 = 425
        self.assertEqual(stops, [Decimal("225"), Decimal("425")])
        self.assertEqual(result.observations[0].one_lot_margin, Decimal("4500"))
        self.assertEqual(result.observations[0].fee_cost, Decimal("5"))
        self.assertEqual(result.observations[0].slippage_cost, Decimal("20"))

    def test_observation_identity_retained(self):
        result = evaluate_capital_adequacy_batch(_batch(observations=[20, 40]))
        self.assertEqual(
            [obs.observation_id for obs in result.observations], ["obs-0", "obs-1"]
        )
        self.assertEqual(
            [obs.distance_ticks for obs in result.observations], [Decimal("20"), Decimal("40")]
        )

    def test_exact_contract_and_batch_identity_echoed(self):
        result = evaluate_capital_adequacy_batch(
            _batch(observations=[20], batch_identity="fixture-batch-v0", as_of=NOW)
        )
        self.assertEqual(result.batch_identity, "fixture-batch-v0")
        self.assertEqual(result.contract_identity.instrument_id, "RB2605")
        self.assertEqual(result.contract_facts_category, FactCategory.EXCHANGE_BROKER_FACT)
        self.assertIsNotNone(result.facts_identity)
        self.assertEqual(result.as_of, NOW)


class DistributionTests(unittest.TestCase):
    def test_distribution_stats_deterministic(self):
        first = evaluate_capital_adequacy_batch(_batch(observations=[10, 20, 30]))
        second = evaluate_capital_adequacy_batch(_batch(observations=[10, 20, 30]))
        self.assertEqual(first.distribution, second.distribution)

    def test_distribution_min_max_median_quantiles(self):
        result = evaluate_capital_adequacy_batch(_batch(observations=[10, 20, 30]))
        dist = result.distribution
        self.assertEqual(dist.count, 3)
        self.assertEqual(dist.min, Decimal("125"))  # 10 ticks -> 100 + 25
        self.assertEqual(dist.max, Decimal("325"))  # 30 ticks -> 300 + 25
        self.assertEqual(dist.median, Decimal("225"))
        self.assertEqual(
            dist.quantiles,
            (
                (Decimal("0.25"), Decimal("175")),
                (Decimal("0.50"), Decimal("225")),
                (Decimal("0.75"), Decimal("275")),
            ),
        )

    def test_even_count_median_is_interpolated_average(self):
        result = evaluate_capital_adequacy_batch(_batch(observations=[20, 40]))
        dist = result.distribution
        self.assertEqual(dist.count, 2)
        self.assertEqual(dist.median, Decimal("325"))  # (225 + 425) / 2
        self.assertEqual(dist.quantiles[0], (Decimal("0.25"), Decimal("275")))
        self.assertEqual(dist.quantiles[2], (Decimal("0.75"), Decimal("375")))

    def test_quantile_algorithm_frozen_as_generic_stats(self):
        from src.capital_adequacy_batch import _linear_interpolated_quantile

        values = (Decimal("10"), Decimal("20"), Decimal("30"), Decimal("40"))
        self.assertEqual(_linear_interpolated_quantile(values, Decimal("0.5")), Decimal("25"))
        self.assertEqual(_linear_interpolated_quantile(values, Decimal("0.25")), Decimal("17.5"))
        with self.assertRaises(ValueError):
            _linear_interpolated_quantile(values, Decimal("1"))
        with self.assertRaises(ValueError):
            _linear_interpolated_quantile(values, Decimal("0"))

    def test_distribution_none_when_no_observation_yields_stop_risk(self):
        # Unknown fee makes stop risk uncomputable (fail closed, not zero).
        facts = _facts(fee=None)
        result = evaluate_capital_adequacy_batch(_batch(observations=[20], facts=facts))
        self.assertIsNone(result.distribution)
        self.assertEqual(result.sufficient_observation_count, 0)
        self.assertEqual(result.insufficient_observation_count, 1)


class FailClosedTests(unittest.TestCase):
    def test_missing_facts_is_aggregate_insufficient(self):
        result = evaluate_capital_adequacy_batch(_batch(observations=[20], facts=None))
        self.assertEqual(result.aggregate_decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(BatchReasonCode.CONTRACT_FACTS_MISSING, result.aggregate_reason_codes)
        self.assertEqual(result.observations, ())
        self.assertIsNone(result.distribution)

    def test_no_observations_is_aggregate_insufficient(self):
        result = evaluate_capital_adequacy_batch(_batch(observations=[]))
        self.assertEqual(result.aggregate_decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(BatchReasonCode.NO_OBSERVATIONS, result.aggregate_reason_codes)

    def test_missing_approved_constraint_no_false_aggregate_pass(self):
        result = evaluate_capital_adequacy_batch(_batch(observations=[20], constraints=None))
        self.assertEqual(result.aggregate_decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(BatchReasonCode.APPROVED_CONSTRAINTS_MISSING, result.aggregate_reason_codes)

    def test_insufficient_approved_constraint_no_false_aggregate_pass(self):
        constraints = ApprovedRiskConstraints(max_one_lot_stop_risk=Decimal("500"))
        result = evaluate_capital_adequacy_batch(_batch(observations=[20], constraints=constraints))
        self.assertEqual(result.aggregate_decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(BatchReasonCode.APPROVED_CONSTRAINTS_INSUFFICIENT, result.aggregate_reason_codes)

    def test_unknown_margin_is_not_zero(self):
        facts = _facts(margin=None)
        result = evaluate_capital_adequacy_batch(_batch(observations=[20], facts=facts))
        obs = result.observations[0]
        # Unknown margin stays None, never a fabricated zero.
        self.assertIsNone(obs.one_lot_margin)
        base = obs.decisions[0]
        self.assertEqual(base.decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.MARGIN_FACTS_MISSING, base.reason_codes)
        self.assertIsNone(base.margin_headroom)
        # Stop risk is margin-independent and therefore still computable.
        self.assertEqual(obs.one_lot_stop_risk, Decimal("225"))

    def test_unknown_fee_is_not_zero(self):
        facts = _facts(fee=None)
        result = evaluate_capital_adequacy_batch(_batch(observations=[20], facts=facts))
        obs = result.observations[0]
        self.assertIsNone(obs.fee_cost)
        self.assertIsNone(obs.one_lot_stop_risk)
        self.assertIn(AdequacyReasonCode.FEE_FACTS_MISSING, obs.decisions[0].reason_codes)

    def test_stale_facts_are_insufficient_not_pass(self):
        facts = _facts(freshness=FactFreshness.STALE)
        result = evaluate_capital_adequacy_batch(_batch(observations=[20], facts=facts))
        obs = result.observations[0]
        self.assertEqual(obs.decisions[0].decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(AdequacyReasonCode.CONTRACT_FACTS_NOT_CURRENT, obs.decisions[0].reason_codes)
        self.assertEqual(result.aggregate_decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)


class DecisionTests(unittest.TestCase):
    def test_per_observation_pass_and_fail(self):
        result = evaluate_capital_adequacy_batch(_batch(observations=[20, 60]))
        decisions = [obs.decisions[0].decision for obs in result.observations]
        self.assertEqual(decisions, [AdequacyDecision.PASS, AdequacyDecision.FAIL])
        self.assertEqual(result.aggregate_decision, AdequacyDecision.FAIL)
        self.assertIn(BatchReasonCode.OBSERVATION_FAIL, result.aggregate_reason_codes)
        # base reasons retained per observation
        self.assertEqual(result.observations[0].decisions[0].reason_codes, (AdequacyReasonCode.OK,))
        self.assertIn(
            AdequacyReasonCode.STOP_RISK_EXCEEDS_APPROVED_LIMIT,
            result.observations[1].decisions[0].reason_codes,
        )

    def test_aggregate_fail_when_any_observation_fails(self):
        result = evaluate_capital_adequacy_batch(_batch(observations=[20, 20, 60]))
        self.assertEqual(result.aggregate_decision, AdequacyDecision.FAIL)
        agg = result.envelope_aggregates[0]
        self.assertEqual(agg.pass_count, 2)
        self.assertEqual(agg.fail_count, 1)
        self.assertEqual(agg.insufficient_count, 0)

    def test_missing_facts_make_observation_insufficient_and_aggregate_insufficient(self):
        facts = _facts(margin=None)
        result = evaluate_capital_adequacy_batch(_batch(observations=[20], facts=facts))
        self.assertEqual(result.aggregate_decision, AdequacyDecision.INSUFFICIENT_EVIDENCE)
        self.assertIn(BatchReasonCode.OBSERVATION_INSUFFICIENT, result.aggregate_reason_codes)


class EnvelopeTests(unittest.TestCase):
    def test_multiple_capital_envelopes(self):
        batch = _batch(
            observations=[20], envelopes=(Decimal("100000"), Decimal("50000"))
        )
        result = evaluate_capital_adequacy_batch(batch)
        self.assertEqual(len(result.envelope_aggregates), 2)
        self.assertEqual(result.envelope_aggregates[0].capital_envelope, Decimal("100000"))
        self.assertEqual(result.envelope_aggregates[1].capital_envelope, Decimal("50000"))
        self.assertEqual(result.envelope_aggregates[0].decision, AdequacyDecision.PASS)
        self.assertEqual(result.envelope_aggregates[1].decision, AdequacyDecision.PASS)

    def test_envelope_aggregate_headroom_and_fraction(self):
        result = evaluate_capital_adequacy_batch(_batch(observations=[20, 40]))
        agg = result.envelope_aggregates[0]
        self.assertEqual(agg.min_margin_headroom, Decimal("95500"))  # 100000 - 4500
        self.assertEqual(agg.min_operational_headroom, Decimal("95075"))
        self.assertEqual(agg.max_capital_fraction_at_risk, Decimal("0.00425"))

    def test_envelope_insufficient_propagates(self):
        facts = _facts(margin=None)
        result = evaluate_capital_adequacy_batch(_batch(observations=[20], facts=facts))
        self.assertEqual(
            result.envelope_aggregates[0].decision, AdequacyDecision.INSUFFICIENT_EVIDENCE
        )
        self.assertIn(
            BatchReasonCode.OBSERVATION_INSUFFICIENT,
            result.envelope_aggregates[0].reason_codes,
        )


class StressScenarioTests(unittest.TestCase):
    def test_stress_scenarios_are_evaluated_per_observation(self):
        stress = StressAssumption(explicit_loss=Decimal("1000"))
        result = evaluate_capital_adequacy_batch(_batch(observations=[20], stress_scenarios=[stress]))
        obs = result.observations[0]
        self.assertEqual(len(obs.decisions), 2)  # base + stress
        base_dec, stress_dec = obs.decisions
        self.assertIsNone(base_dec.stress_label)
        self.assertEqual(base_dec.decision, AdequacyDecision.PASS)
        self.assertEqual(stress_dec.stress_label, stress.label)
        self.assertEqual(stress_dec.stress_loss, Decimal("1000"))
        # worst loss 225 + 1000 = 1225 -> fraction 0.01225 > 0.01 -> FAIL
        self.assertEqual(stress_dec.decision, AdequacyDecision.FAIL)
        self.assertIn(
            AdequacyReasonCode.CAPITAL_FRACTION_EXCEEDS_APPROVED_LIMIT, stress_dec.reason_codes
        )

    def test_stress_price_move_scenario(self):
        stress = StressAssumption(price_move_ticks=Decimal("50"))
        result = evaluate_capital_adequacy_batch(_batch(observations=[20], stress_scenarios=[stress]))
        stress_dec = result.observations[0].decisions[1]
        self.assertEqual(stress_dec.stress_loss, Decimal("500"))  # 50 ticks * 10


class SeparationTests(unittest.TestCase):
    def test_input_classification_four_way_separation(self):
        result = evaluate_capital_adequacy_batch(_batch(observations=[20]))
        self.assertEqual(
            result.input_classification,
            (
                "EXCHANGE_BROKER_FACTS=EXCHANGE_BROKER_FACT",
                "SCENARIO_ASSUMPTIONS=SUPPLIED_SLIPPAGE_AND_STRESS",
                "OBSERVED_JIANGHE=SUPPLIED_INVALIDATION_DISTANCE_TICKS",
                "APPROVED_CONSTRAINTS=SUPPLIED_APPROVED_RISK_CONSTRAINTS",
            ),
        )


class ValidationTests(unittest.TestCase):
    def test_zero_distance_observation_rejected(self):
        with self.assertRaises(ValueError):
            ObservedInvalidation(observation_id="o1", distance_ticks=Decimal("0"))

    def test_negative_distance_observation_rejected(self):
        with self.assertRaises(ValueError):
            ObservedInvalidation(observation_id="o1", distance_ticks=Decimal("-1"))

    def test_empty_capital_envelopes_rejected(self):
        with self.assertRaises(ValueError):
            _batch(observations=[20], envelopes=())

    def test_quantile_level_outside_unit_interval_rejected(self):
        with self.assertRaises(ValueError):
            _batch(observations=[20], quantile_levels=(Decimal("1.5"),))

    def test_non_increasing_quantile_levels_rejected(self):
        with self.assertRaises(ValueError):
            _batch(observations=[20], quantile_levels=(Decimal("0.5"), Decimal("0.25")))

    def test_naive_as_of_rejected(self):
        from datetime import datetime as _datetime

        with self.assertRaises(ValueError):
            _batch(observations=[20], as_of=_datetime(2026, 1, 1))


class NoProductionDefaultsTests(unittest.TestCase):
    def test_no_fixture_numbers_exported_as_production_defaults(self):
        import src.capital_adequacy_batch as module

        defaults = [name for name in vars(module) if name.startswith("DEFAULT_")]
        self.assertEqual(defaults, [])
        source = inspect.getsource(module)
        self.assertNotIn("100000", source)
        self.assertNotIn("100_000", source)
        # No module-level numeric default assignments for slippage/fee/capital/
        # reserve/margin/stress/risk.  Quantile levels are generic statistics.
        self.assertIsNone(
            re.search(
                r"^\s*(?:SLIPPAGE|FEE|CAPITAL|RESERVE|MARGIN|STRESS|RISK)[A-Z_]*\s*=\s*Decimal",
                source,
                re.MULTILINE,
            )
        )


if __name__ == "__main__":
    unittest.main()

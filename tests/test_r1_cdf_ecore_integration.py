"""R1 CDF x E-Core combined integration test.

Proves the merged C/D/F tree plus the accepted Package E-Core (E-01..E-03,
E-09, E-11..E-13) and the new E-10 fix operate as ONE system on a single
integration tree:

A. CDF synthetic Playbook / firewall chain still completes outcome
   registration after the combined integration merge.
B. ONE SessionMetadata is used simultaneously as the canonical/session
   authority (D-05 content-derived ``version``), the E-Core official
   trading-day/week authority in the runner, and the RoundTripMaterializer
   authority (E-10 ``session_metadata_version``).
C. Forced liquidation D1 -> D2: E-02 aging + E-03 offset fees are correct, and
   the completed round trip carries the correct ``session_metadata_version``
   with a recomputable ledger identity.
D. Changing the SessionMetadata authority (D-05 content-derived version)
   changes the round-trip identity even when the derived days coincide.
E. Candidate outcome authorization is NOT opened by this integration test:
   the only registration path is the TEST_ONLY synthetic profile with the
   governed TEST_ONLY data version, and validation/final-holdout candidate
   access remains denied.

No candidate market outcome data is used anywhere in this test.
"""

import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from src.contract_semantics import (
    CloseOffset,
    ContractMappingEntry,
    ContractMappingSchedule,
    ContractMaster,
    ContractSpecification,
    OffsetCostAssumptions,
    OrderAction,
    PriceLimitFact,
)
from src.data_substrate import CompletedBar, SessionMetadata, SessionWindow
from src.playbook_contract import (
    ClaimStatus,
    SourceClaimRef,
    bridge_to_strategy_identity,
    validate_contract,
)
from src.research_firewall import (
    ByteBindingStatus,
    ClaimRecordDraft,
    ClaimRecordOutput,
    ResearchFirewall,
    SourceOnlyClaimExtractionContext,
    TEST_ONLY_SYNTHETIC_DATA_VERSION,
)
from src.round_trip_ledger import (
    TERMINAL_REASON_FORCED_LIQUIDATION,
    RoundTripMaterializer,
)
from src.strategy_evidence import DatasetClass, EvidenceLedger
from src.validation_runner import (
    CapitalMarginAssumptions,
    CapitalSnapshot,
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
    SYNTHETIC_EXPOSURE_REFERENCE,
    SYNTHETIC_HYPOTHESIS_TEST_ID,
    SYNTHETIC_MATERIAL_ANCHOR,
    SYNTHETIC_MATERIAL_ID,
    SYNTHETIC_PARAMETER,
    SYNTHETIC_SESSION_ID,
    SYNTHETIC_SOURCE_ID,
    SYNTHETIC_WAVE_ID,
    build_synthetic_firewall,
    make_approved_bundle,
    make_approved_material_ref,
    make_artifact_bindings,
    make_code_artifact,
    make_contract,
    make_environment_artifact,
    make_experiment,
    make_strategy,
    make_test_only_profile,
    make_validation_input,
    make_wave_manifest,
)

CN = ZoneInfo("Asia/Shanghai")
DAY_1 = date(2024, 6, 17)
DAY_2 = date(2024, 6, 18)
DAY_3 = date(2024, 6, 19)


def at(day, hour, minute):
    return datetime(day.year, day.month, day.day, hour, minute, tzinfo=CN)


def make_input(request_id, symbol, trading_day, decision_at, data_version=TEST_ONLY_SYNTHETIC_DATA_VERSION):
    return make_validation_input(
        request_id,
        CompletedBar(
            symbol,
            trading_day,
            decision_at - timedelta(minutes=5),
            decision_at,
            decision_at,
        ),
        decision_at,
        data_version=data_version,
    )


class R1CDFECoreIntegrationTests(unittest.TestCase):
    """One-tree proof: C/D/F + E-Core + E-10 as a single system."""

    DAY_1 = DAY_1
    DAY_2 = DAY_2
    DAY_3 = DAY_3

    def setUp(self):
        self.strategy = make_strategy(
            research_lineage_id="r1-integration-lineage-fixture",
            family_id="neutral-r1-integration-family",
            source="deterministic-synthetic-r1-fixture",
            applicable_instruments=("A",),
            data_exposure_history_reference="r1-integration-exposure-fixture-v1",
        )
        self.experiment = make_experiment(
            self.strategy,
            dataset_exposure_reference="r1-integration-exposure-fixture-v1",
        )
        self.execution_assumptions = ExecutionAssumptions(
            "r1-integration-execution-v1", Decimal("0"), Decimal("0.25")
        )
        self.capital_assumptions = CapitalMarginAssumptions(
            "r1-integration-capital-v1", Decimal("1"), Decimal("0.1"), "SYNTH", Decimal("0.05")
        )
        self.offset_costs = OffsetCostAssumptions(
            "r1-integration-offset-v1", Decimal("1"), Decimal("2")
        )
        self.contract_a = ContractSpecification(
            exchange="SYNTH_EX",
            product_family="SYNTH_PRODUCT",
            instrument_id="A",
            listed_at=at(self.DAY_1, 8, 0),
            deactivated_at=at(self.DAY_3, 0, 0),
            contract_multiplier=Decimal("1"),
            minimum_price_tick=Decimal("0.5"),
            currency="SYNTH",
            unit="SYNTH_UNIT",
            price_limit_rule_identity="synthetic-limit-rule-v1",
            offset_fee_metadata_identity=self.offset_costs.identity_id,
            metadata_version="synthetic-contract-metadata-v1",
        )
        self.master = ContractMaster("r1-integration-master-v1", (self.contract_a,))
        self.mapping_a = ContractMappingEntry(
            "SYNTH_MAIN",
            "A",
            at(self.DAY_1, 8, 0),
            at(self.DAY_3, 0, 0),
            at(self.DAY_1, 8, 0),
            "r1-integration-roll-v1",
        )
        self.schedule = ContractMappingSchedule(
            "r1-integration-schedule-v1", ("SYNTH_MAIN",), (self.mapping_a,)
        )
        # ONE SessionMetadata used by both the runner and the materializer (B).
        self.sessions = SessionMetadata(
            "r1-integration-session-v1",
            (
                SessionWindow("SYNTH_EX", "A", self.DAY_1, at(self.DAY_1, 9, 0), at(self.DAY_1, 11, 0), "DAY"),
                SessionWindow("SYNTH_EX", "A", self.DAY_2, at(self.DAY_1, 21, 0), at(self.DAY_1, 23, 0), "NIGHT"),
            ),
        )
        self.limit_facts = (
            PriceLimitFact(
                "limit-A-d1", "A", self.contract_a.identity_id, self.DAY_1,
                Decimal("30"), Decimal("120"), at(self.DAY_1, 8, 50), at(self.DAY_1, 8, 50),
                "synthetic-limit-rule-v1", False,
            ),
            PriceLimitFact(
                "limit-A-d2", "A", self.contract_a.identity_id, self.DAY_2,
                Decimal("30"), Decimal("120"), at(self.DAY_1, 20, 50), at(self.DAY_1, 20, 50),
                "synthetic-limit-rule-v1", False,
            ),
        )

    # -- shared fixtures -----------------------------------------------------

    def observation(self, request_id, timestamp, price, contract="A"):
        return ExecutionObservation(
            request_id, timestamp, timestamp, Decimal(price), concrete_contract_id=contract
        )

    def run_case(
        self,
        inputs,
        observations,
        specifications,
        *,
        mark=None,
        liquidation_observations=(),
        cutoff=None,
        starting_capital=Decimal("20"),
        offset_costs=None,
    ):
        ledger = EvidenceLedger()
        firewall, hypothesis_test_id = build_synthetic_firewall(
            ledger, self.strategy, self.experiment
        )
        runner = ChronologicalValidationRunner(ledger, firewall)
        return runner.run(
            mode=ValidationMode.CONFIRMATORY,
            strategy=self.strategy,
            experiment=self.experiment,
            dataset_class=DatasetClass.DEVELOPMENT,
            inputs=inputs,
            disposition=ValidationDisposition.CONFIRMED,
            hypothesis_test_id=hypothesis_test_id,
            execution_observations=observations,
            execution_cutoff_at=(
                cutoff if cutoff is not None else inputs[-1].decision_at + timedelta(minutes=30)
            ),
            execution_assumptions=self.execution_assumptions,
            order_specifications=specifications,
            capital_snapshot=CapitalSnapshot(starting_capital),
            capital_margin_assumptions=self.capital_assumptions,
            contract_master=self.master,
            contract_mapping_schedule=self.schedule,
            session_metadata=self.sessions,
            price_limit_facts=self.limit_facts,
            offset_cost_assumptions=self.offset_costs if offset_costs is None else offset_costs,
            mark_observations=() if mark is None else (mark,),
            forced_liquidation_observations=tuple(liquidation_observations),
        )

    def _register_cdf_chain(self):
        """Reuse the synthetic fixture helpers to run the C/D/F chain once."""
        firewall = ResearchFirewall(EvidenceLedger())
        policy = firewall.source_only
        bundle = make_approved_bundle(
            materials=(
                make_approved_material_ref(exact_bytes=b"r1 combined chain material bytes v1"),
            ),
            content_note="r1 combined chain synthetic bundle",
        )
        self.assertEqual(bundle.byte_binding_status, ByteBindingStatus.EXACT_BYTES_BOUND)
        session = policy.open_verified_session(
            session_id=SYNTHETIC_SESSION_ID,
            model_identity="model-fixture-v1",
            prompt_spec_version="prompt-spec-v1",
            source_bundle_identity=bundle.session_binding_identity,
            source_bundle_hash=bundle.session_binding_hash,
            tool_retrieval_mode="PROJECT_SOURCE_ONLY",
            researcher_model_exposure_note="no known exposure",
        )
        output = ClaimRecordOutput()
        context = SourceOnlyClaimExtractionContext(
            source_bundle=bundle,
            source_only=policy,
            session_id=session.session_id,
            output_surface=output,
        )
        self.assertTrue(context.verified)
        context.record_claim(
            ClaimRecordDraft(
                claim_id="r1-c1",
                source_id=SYNTHETIC_SOURCE_ID,
                material_id=SYNTHETIC_MATERIAL_ID,
                source_anchor=f"{SYNTHETIC_MATERIAL_ANCHOR}:page-1",
                claim_status="EXPLICIT",
                source_excerpt_short_or_paraphrase="synthetic r1 combined chain claim",
                source_only_session_id=session.session_id,
                created_at="2026-08-20T00:00:00Z",
            )
        )
        contract = make_contract(
            source_claims=(
                SourceClaimRef(
                    claim_id="c1",
                    source_id=SYNTHETIC_SOURCE_ID,
                    source_anchor="fixture:book:p1",
                    claim_status=ClaimStatus.EXPLICIT,
                ),
            ),
            source_bundle_identity=bundle.session_binding_identity,
            source_bundle_hash=bundle.session_binding_hash,
            source_only_session_identity=session.session_identity,
        )
        self.assertTrue(validate_contract(contract).ready)
        strategy = bridge_to_strategy_identity(
            contract,
            parameters=(SYNTHETIC_PARAMETER,),
            code_hash=make_code_artifact().sha256,
            environment_hash=make_environment_artifact().sha256,
            required_feature_versions=("feature-v1",),
            data_exposure_history_reference=SYNTHETIC_EXPOSURE_REFERENCE,
        )
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)
        wave = firewall.waves.register(
            make_wave_manifest(
                wave_id=SYNTHETIC_WAVE_ID,
                contract=contract,
                strategy=strategy,
                profile_id=profile.profile_id,
                profile_identity=profile.profile_identity,
                tested_hypothesis_test_ids=(SYNTHETIC_HYPOTHESIS_TEST_ID,),
            )
        )
        experiment = make_experiment(strategy)
        registration = firewall.register_outcome_test(
            hypothesis_test_id=SYNTHETIC_HYPOTHESIS_TEST_ID,
            contract=contract,
            strategy=strategy,
            experiment=experiment,
            artifact_bindings=make_artifact_bindings(),
            source_only_session_id=session.session_id,
            research_wave_id=wave.research_wave_id,
            statistical_profile_id=profile.profile_id,
            multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
        )
        firewall.lock_wave(wave.research_wave_id)
        return firewall, registration, session, experiment, profile, bundle

    # -- A: CDF chain still completes registration ---------------------------

    def test_A_cdf_chain_registration_still_succeeds(self):
        firewall, registration, session, experiment, profile, bundle = self._register_cdf_chain()
        self.assertEqual(registration.source_bundle_identity, bundle.session_binding_identity)
        self.assertEqual(registration.source_bundle_hash, bundle.session_binding_hash)
        self.assertEqual(registration.source_only_session_identity, session.session_identity)
        self.assertIsNotNone(
            firewall._tests.get(SYNTHETIC_HYPOTHESIS_TEST_ID)
        )

    # -- B: one SessionMetadata drives runner + materializer -----------------

    def test_B_one_session_metadata_drives_runner_and_materializer(self):
        input_open = make_input("open-1", "A", self.DAY_1, at(self.DAY_1, 9, 5))
        input_close = make_input("close-1", "A", self.DAY_1, at(self.DAY_1, 9, 55))
        result = self.run_case(
            (input_open, input_close),
            (
                self.observation("open-1", at(self.DAY_1, 9, 6), "100"),
                self.observation("close-1", at(self.DAY_1, 9, 56), "110"),
            ),
            (
                OrderSpecification("open-1", Decimal("1")),
                OrderSpecification("close-1", Decimal("1"), OrderAction.CLOSE, CloseOffset.CLOSE_TODAY),
            ),
        )
        # E-Core official trading day from the SAME SessionMetadata: the open
        # transition's after-snapshot records the runner's official day, and
        # the materializer's session-consistency check accepts it.
        self.assertEqual(result.capital_transitions[0].after.position_trading_day, self.DAY_1)
        # E-10: the SAME SessionMetadata drives the materializer.
        ledger = RoundTripMaterializer(self.sessions, "SYNTH_EX").materialize(
            result.capital_transitions, result.execution_outcomes
        )
        self.assertEqual(ledger.completed_count, 1)
        trip = ledger.completed_round_trips[0]
        self.assertEqual(trip.session_metadata_version, self.sessions.version)
        self.assertEqual(trip.entry_official_trading_day, self.DAY_1)
        self.assertEqual(trip.exit_official_trading_day, self.DAY_1)
        # D-05: version is content-derived (authority + exact windows), never a
        # plain caller label copied into the round trip.
        self.assertEqual(self.sessions.version, self.sessions.identity)
        self.assertNotEqual(self.sessions.version, "r1-integration-session-v1")

    # -- C: forced liquidation D1 -> D2 round trip ---------------------------

    def _forced_liquidation_result(self, *, liquidation_at, starting_capital=Decimal("20")):
        opening_input = make_input("open-1", "A", self.DAY_1, at(self.DAY_1, 9, 5))
        opening_observation = self.observation("open-1", at(self.DAY_1, 9, 6), "100")
        opening_spec = OrderSpecification("open-1", Decimal("1"))
        opened = self.run_case(
            (opening_input,), (opening_observation,), (opening_spec,),
            starting_capital=starting_capital,
        )
        snapshot = opened.final_capital_snapshot
        mark = MarkObservation(
            "breach-mark",
            snapshot.position_id,
            snapshot.position_request_id,
            "A",
            at(self.DAY_1, 10, 50),
            at(self.DAY_1, 10, 50),
            Decimal("40"),
        )
        breached = self.run_case(
            (opening_input,), (opening_observation,), (opening_spec,),
            mark=mark,
            cutoff=at(self.DAY_1, 21, 30),
            starting_capital=starting_capital,
        )
        requirement = breached.liquidation_requirement
        self.assertIsNotNone(requirement)
        observation = self.observation(requirement.request_id, liquidation_at, "39")
        return self.run_case(
            (opening_input,), (opening_observation,), (opening_spec,),
            mark=mark,
            liquidation_observations=(observation,),
            cutoff=liquidation_at + timedelta(minutes=30),
            starting_capital=starting_capital,
        )

    def test_C_forced_liquidation_d1_to_d2_round_trip_binds_session_version(self):
        result = self._forced_liquidation_result(liquidation_at=at(self.DAY_1, 21, 5))
        outcome = result.liquidation_outcome.execution_outcome
        transition = result.liquidation_outcome.capital_transition
        # E-03: offset fee applied to the effective (aged) buckets.
        self.assertEqual(outcome.status, FillStatus.FILLED)
        self.assertEqual(outcome.total_cost, Decimal("2.25"))  # 0.25 fee + 2.00 close-previous
        self.assertEqual(outcome.resolved_close_offset, CloseOffset.CLOSE_PREVIOUS)
        self.assertEqual(transition.required_cost, Decimal("2.25"))
        # E-02: full DAY_1 today bucket aged to previous exactly once.
        self.assertEqual(transition.aged_quantity, Decimal("1"))
        self.assertEqual(result.final_capital_snapshot.charged_costs, Decimal("2.50"))
        # Materialize with the SAME SessionMetadata used by the runner.
        outcomes = result.execution_outcomes + (outcome,)
        ledger = RoundTripMaterializer(self.sessions, "SYNTH_EX").materialize(
            result.capital_transitions, outcomes
        )
        self.assertEqual(ledger.completed_count, 1)
        trip = ledger.completed_round_trips[0]
        self.assertTrue(trip.forced_liquidation)
        self.assertEqual(trip.terminal_reason, TERMINAL_REASON_FORCED_LIQUIDATION)
        self.assertEqual(trip.session_metadata_version, self.sessions.version)
        self.assertEqual(trip.entry_official_trading_day, self.DAY_1)
        self.assertEqual(trip.exit_official_trading_day, self.DAY_2)
        # Ledger identity is recomputable consistently.
        again = RoundTripMaterializer(self.sessions, "SYNTH_EX").materialize(
            result.capital_transitions, outcomes
        )
        self.assertEqual(again.completed_round_trips[0].ledger_identity, trip.ledger_identity)
        self.assertEqual(again.identity_id, ledger.identity_id)

    # -- D: changing session authority changes identity ----------------------

    def test_D_changing_session_authority_changes_round_trip_identity(self):
        input_open = make_input("open-1", "A", self.DAY_1, at(self.DAY_1, 9, 5))
        input_close = make_input("close-1", "A", self.DAY_1, at(self.DAY_1, 9, 55))
        result = self.run_case(
            (input_open, input_close),
            (
                self.observation("open-1", at(self.DAY_1, 9, 6), "100"),
                self.observation("close-1", at(self.DAY_1, 9, 56), "110"),
            ),
            (
                OrderSpecification("open-1", Decimal("1")),
                OrderSpecification("close-1", Decimal("1"), OrderAction.CLOSE, CloseOffset.CLOSE_TODAY),
            ),
        )
        transitions = result.capital_transitions
        outcomes = result.execution_outcomes
        # Same authority label, different windows -> different D-05 content
        # version, while the derived official days still coincide.
        session_v2 = SessionMetadata(
            "r1-integration-session-v1",
            (
                SessionWindow("SYNTH_EX", "A", self.DAY_1, at(self.DAY_1, 8, 45), at(self.DAY_1, 11, 15), "DAY"),
                SessionWindow("SYNTH_EX", "A", self.DAY_2, at(self.DAY_1, 21, 0), at(self.DAY_1, 23, 0), "NIGHT"),
            ),
        )
        self.assertNotEqual(self.sessions.version, session_v2.version)
        trip_v1 = RoundTripMaterializer(self.sessions, "SYNTH_EX").materialize(
            transitions, outcomes
        ).completed_round_trips[0]
        trip_v2 = RoundTripMaterializer(session_v2, "SYNTH_EX").materialize(
            transitions, outcomes
        ).completed_round_trips[0]
        # Derived days coincide, but the round-trip identity must change because
        # the identity binds the D-05 session authority (E-10).
        self.assertEqual(trip_v1.entry_official_trading_day, trip_v2.entry_official_trading_day)
        self.assertEqual(trip_v1.exit_official_trading_day, trip_v2.exit_official_trading_day)
        self.assertNotEqual(trip_v1.ledger_identity, trip_v2.ledger_identity)
        self.assertNotEqual(trip_v1.session_metadata_version, trip_v2.session_metadata_version)

    # -- E: candidate outcome authorization stays closed ---------------------

    def test_E_candidate_outcome_authorization_stays_closed(self):
        firewall, registration, session, experiment, profile, bundle = self._register_cdf_chain()
        # The only registration path is TEST_ONLY synthetic.
        self.assertTrue(profile.is_test_only)
        self.assertEqual(experiment.data_version, TEST_ONLY_SYNTHETIC_DATA_VERSION)
        # Validation cohort candidate outcome access remains denied.
        validation = firewall.request_candidate_outcome_access(
            data_dates=(date(2025, 1, 2),),
            experiment=experiment,
            hypothesis_test_id=SYNTHETIC_HYPOTHESIS_TEST_ID,
        )
        self.assertFalse(validation.allowed)
        # Historical final holdout cohort candidate outcome access also denied.
        holdout = firewall.request_candidate_outcome_access(
            data_dates=(date(2025, 7, 2),),
            experiment=experiment,
            hypothesis_test_id=SYNTHETIC_HYPOTHESIS_TEST_ID,
        )
        self.assertFalse(holdout.allowed)


if __name__ == "__main__":
    unittest.main()

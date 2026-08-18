"""Deterministic regression tests for the identity-bound pre-outcome firewall.

Covers the frozen Selection Firewall requirements (v1.0) after acceptance-review
hardening:
- project-issued SOURCE_ONLY verification (a manual TECHNICALLY_DENIED session is
  not verified without project-issued evidence)
- bounded SOURCE_ONLY claim-extraction runner with technical denial
- immutable RESEARCH_WAVE manifests whose permanent denominator is derived from
  the manifest (no split-brain) with exact profile/counting-unit identity binding
- canonical identity-bound OutcomeTestRegistration
- the single fail-closed pre-outcome gate (identity-binding checks)
- historical final-holdout state machine (no auto-unlock)
- frozen 12/6/6 chronology classification
- legacy FinalUnseenFirewall compatibility
"""

import inspect
import unittest
from dataclasses import FrozenInstanceError
from datetime import date

from src.research_firewall import (
    ApprovedSourceBundle,
    ClaimRecordDraft,
    ClaimRecordOutput,
    Cohort,
    CommonStatisticalProfile,
    FinalHoldoutState,
    FrozenResearchProtocol,
    HistoricalFinalHoldoutStateMachine,
    OutcomeTestRegistration,
    PreOutcomeGate,
    ProtectedMarketAccessMode,
    ResearchFirewall,
    ResearchWaveManifest,
    SourceOnlyClaimExtractionContext,
    SourceOnlySession,
    classify_cohort,
)
from src.strategy_evidence import (
    DatasetClass,
    EvidenceLedger,
    ExperimentIdentity,
    FinalUnseenFirewall,
    LifecycleState,
    StrategyCatalog,
    StrategyIdentity,
    TypedParameter,
)


def strategy(*, family_id="neutral-family", version="1.0", parent_identity_id=None):
    return StrategyIdentity(
        research_lineage_id="research-lineage-fixture",
        family_id=family_id,
        strategy_version=version,
        source="deterministic-fixture",
        applicable_instruments=("TEST",),
        timeframe="5m",
        parameters=(TypedParameter("window", "int", 3),),
        code_hash="code-fixture-v1",
        environment_hash="environment-fixture-v1",
        required_feature_versions=("context-fixture-v1",),
        lifecycle_state=LifecycleState.DRAFT,
        data_exposure_history_reference="exposure-fixture-v1",
        parent_identity_id=parent_identity_id,
    )


def make_test_only_profile(profile_id="profile-test-only-v1"):
    return CommonStatisticalProfile(
        profile_id=profile_id,
        profile_version="0.0-test",
        uncertainty_precision_method="METHOD_NOT_SPECIFIED_TEST_ONLY",
        evidence_sufficiency_procedure="PROCEDURE_NOT_SPECIFIED_TEST_ONLY",
        dependence_handling="HANDLING_NOT_SPECIFIED_TEST_ONLY",
        multiplicity_decision_rule="RULE_NOT_SPECIFIED_TEST_ONLY",
        common_acceptance_procedure="PROCEDURE_NOT_SPECIFIED_TEST_ONLY",
        test_only_marker="TEST_ONLY",
    )


COUNTING_UNIT_IDENTITY = "counting-unit-test-v1"
HYPOTHESIS_TEST_ID = "hypothesis-test-v1"


def make_wave_manifest(
    *,
    wave_id="wave-test-only-v1",
    profile_id="profile-test-only-v1",
    profile_identity=None,
    counting_unit_identity=COUNTING_UNIT_IDENTITY,
    tested_hypothesis_test_ids=(HYPOTHESIS_TEST_ID,),
    created_at="2026-08-19T00:00:00Z",
):
    if profile_identity is None:
        profile_identity = make_test_only_profile(profile_id=profile_id).profile_identity
    return ResearchWaveManifest(
        research_wave_id=wave_id,
        protocol_version="1.0",
        statistical_profile_id=profile_id,
        statistical_profile_identity=profile_identity,
        multiplicity_counting_unit_identity=counting_unit_identity,
        tested_hypothesis_test_ids=tested_hypothesis_test_ids,
        primary_branch_identities=("primary-branch-fixture-v1",),
        declared_outcome_tested_alternatives=(),
        instrument_timeframe_context_scope="TEST_ONLY:instrument=TEST;timeframe=5m;context=TEST",
        parameter_search_ranges="TEST_ONLY:none",
        denominator_counting_semantics="TEST_ONLY:independent-falsifiable-hypotheses",
        created_at=created_at,
    )


def make_open_session(policy, *, session_id="source-only-session-1"):
    return policy.open_verified_session(
        session_id=session_id,
        model_identity="model-fixture-v1",
        prompt_spec_version="prompt-spec-v1",
        source_bundle_identity="bundle-fixture-v1",
        source_bundle_hash="bundle-hash-fixture-v1",
        tool_retrieval_mode="PROJECT_SOURCE_ONLY",
        researcher_model_exposure_note="no known exposure",
    )


def make_registered_firewall(
    ledger,
    *,
    hypothesis_test_id=HYPOTHESIS_TEST_ID,
    session_id="source-only-session-1",
    profile_id="profile-test-only-v1",
    wave_id="wave-test-only-v1",
    family_claim_identity="family-claim-fixture-v1",
    primary_branch_identity="primary-branch-fixture-v1",
    scope_identity="scope-fixture-v1",
    parameter_search_identity="parameter-search-fixture-v1",
    strategy_obj=None,
):
    """Build a fully identity-bound firewall: verified session + TEST_ONLY
    profile + wave + one registered outcome test, with the wave locked."""
    if strategy_obj is None:
        strategy_obj = strategy()
    experiment = ExperimentIdentity.from_strategy(strategy_obj, "data-fixture-v1", "exposure-fixture-v1")
    firewall = ResearchFirewall(ledger)
    session = make_open_session(firewall.source_only, session_id=session_id)
    profile = firewall.profiles.register(make_test_only_profile(profile_id=profile_id))
    firewall.profiles.lock(profile.profile_id)
    wave = firewall.waves.register(
        make_wave_manifest(
            wave_id=wave_id,
            profile_id=profile.profile_id,
            profile_identity=profile.profile_identity,
            tested_hypothesis_test_ids=(hypothesis_test_id,),
        )
    )
    firewall.register_outcome_test(
        hypothesis_test_id=hypothesis_test_id,
        strategy=strategy_obj,
        experiment=experiment,
        family_claim_identity=family_claim_identity,
        primary_branch_identity=primary_branch_identity,
        scope_identity=scope_identity,
        parameter_search_identity=parameter_search_identity,
        source_only_session_id=session.session_id,
        research_wave_id=wave.research_wave_id,
        statistical_profile_id=profile.profile_id,
        multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
    )
    firewall.lock_wave(wave.research_wave_id)
    return firewall, session, profile, wave, experiment


class ChronologyClassificationTests(unittest.TestCase):
    def test_frozen_12_6_6_boundaries(self):
        self.assertEqual(classify_cohort(date(2024, 1, 1)), Cohort.DEVELOPMENT)
        self.assertEqual(classify_cohort(date(2024, 12, 31)), Cohort.DEVELOPMENT)
        self.assertEqual(classify_cohort(date(2025, 1, 1)), Cohort.VALIDATION)
        self.assertEqual(classify_cohort(date(2025, 6, 30)), Cohort.VALIDATION)
        self.assertEqual(
            classify_cohort(date(2025, 7, 1)), Cohort.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT
        )
        self.assertEqual(
            classify_cohort(date(2025, 12, 31)), Cohort.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT
        )
        self.assertEqual(classify_cohort(date(2023, 12, 31)), Cohort.OUT_OF_SCOPE)
        self.assertEqual(classify_cohort(date(2026, 1, 1)), Cohort.SHADOW_FORWARD)

    def test_frozen_constants_are_12_6_6_and_not_modified(self):
        self.assertEqual(FrozenResearchProtocol.RESEARCH_PROTOCOL_VERSION, "1.0")
        self.assertEqual(FrozenResearchProtocol.RESEARCH_PROTOCOL_STATUS, "FROZEN_BINDING")
        self.assertEqual(FrozenResearchProtocol.DEVELOPMENT_START, date(2024, 1, 1))
        self.assertEqual(FrozenResearchProtocol.DEVELOPMENT_END, date(2024, 12, 31))
        self.assertEqual(FrozenResearchProtocol.VALIDATION_START, date(2025, 1, 1))
        self.assertEqual(FrozenResearchProtocol.VALIDATION_END, date(2025, 6, 30))
        self.assertEqual(FrozenResearchProtocol.FINAL_HOLDOUT_START, date(2025, 7, 1))
        self.assertEqual(FrozenResearchProtocol.FINAL_HOLDOUT_END, date(2025, 12, 31))


class SourceOnlyPolicyTests(unittest.TestCase):
    def test_open_verified_session_is_project_verified(self):
        policy = ResearchFirewall(EvidenceLedger()).source_only
        session = make_open_session(policy)
        self.assertTrue(policy.is_verified(session.session_id))
        self.assertIsNotNone(session.verification_evidence)
        self.assertEqual(
            session.session_identity,
            SourceOnlySession(
                session_id="source-only-session-1",
                model_identity="model-fixture-v1",
                prompt_spec_version="prompt-spec-v1",
                source_bundle_identity="bundle-fixture-v1",
                source_bundle_hash="bundle-hash-fixture-v1",
                tool_retrieval_mode="PROJECT_SOURCE_ONLY",
                protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
                researcher_model_exposure_note="no known exposure",
            ).session_identity,
        )

    def test_manually_constructed_technically_denied_session_is_not_verified(self):
        # Test 3: manually constructed TECHNICALLY_DENIED without project-issued
        # verification evidence is NOT VERIFIED.
        policy = ResearchFirewall(EvidenceLedger()).source_only
        policy.record_session(
            SourceOnlySession(
                session_id="manual",
                model_identity="model-fixture-v1",
                prompt_spec_version="prompt-spec-v1",
                source_bundle_identity="bundle-fixture-v1",
                source_bundle_hash="bundle-hash-fixture-v1",
                tool_retrieval_mode="PROJECT_SOURCE_ONLY",
                protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
            )
        )
        self.assertFalse(policy.is_verified("manual"))

    def test_manually_forged_verification_evidence_is_not_verified(self):
        policy = ResearchFirewall(EvidenceLedger()).source_only
        policy.record_session(
            SourceOnlySession(
                session_id="forged",
                model_identity="model-fixture-v1",
                prompt_spec_version="prompt-spec-v1",
                source_bundle_identity="bundle-fixture-v1",
                source_bundle_hash="bundle-hash-fixture-v1",
                tool_retrieval_mode="PROJECT_SOURCE_ONLY",
                protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
                verification_evidence="forged-evidence",
            )
        )
        self.assertFalse(policy.is_verified("forged"))

    def test_prompt_only_instruction_is_not_technical_denial(self):
        policy = ResearchFirewall(EvidenceLedger()).source_only
        policy.record_session(
            SourceOnlySession(
                session_id="s1",
                model_identity="model-fixture-v1",
                prompt_spec_version="prompt-spec-v1",
                source_bundle_identity="bundle-fixture-v1",
                source_bundle_hash="bundle-hash-fixture-v1",
                tool_retrieval_mode="PROJECT_SOURCE_ONLY",
                protected_market_access_mode=ProtectedMarketAccessMode.PROMPT_ONLY,
            )
        )
        self.assertFalse(policy.is_verified("s1"))
        self.assertFalse(policy.is_verified("missing-session"))

    def test_missing_identity_field_is_rejected(self):
        with self.assertRaises(ValueError):
            SourceOnlySession(
                session_id="",
                model_identity="model-fixture-v1",
                prompt_spec_version="prompt-spec-v1",
                source_bundle_identity="bundle-fixture-v1",
                source_bundle_hash="bundle-hash-fixture-v1",
                tool_retrieval_mode="PROJECT_SOURCE_ONLY",
                protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
            )

    def test_protected_market_outcome_request_is_technically_denied(self):
        policy = ResearchFirewall(EvidenceLedger()).source_only
        result = policy.request_protected_market_outcome("s1")
        self.assertEqual(result.outcome, "DENIED")
        self.assertEqual(result.reason, "SOURCE_ONLY_TECHNICAL_DENIAL")
        repeated = policy.request_protected_market_outcome("s1")
        self.assertEqual(repeated, result)
        self.assertEqual(len(policy.denial_records), 2)

    def test_duplicate_session_id_is_rejected(self):
        policy = ResearchFirewall(EvidenceLedger()).source_only
        make_open_session(policy)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            make_open_session(policy)


class ResearchWaveRegistryTests(unittest.TestCase):
    def test_wave_manifest_is_immutable(self):
        firewall = ResearchFirewall(EvidenceLedger())
        manifest = firewall.waves.register(make_wave_manifest())
        with self.assertRaises(FrozenInstanceError):
            manifest.denominator_counting_semantics = "changed"
        with self.assertRaises(FrozenInstanceError):
            manifest.tested_hypothesis_test_ids = ("other-hypothesis",)

    def test_manifest_identity_is_deterministic(self):
        firewall = ResearchFirewall(EvidenceLedger())
        first = firewall.waves.register(make_wave_manifest())
        second = firewall.waves.register(make_wave_manifest(wave_id="wave-2"))
        self.assertEqual(first.manifest_identity, make_wave_manifest().manifest_identity)
        self.assertNotEqual(first.manifest_identity, second.manifest_identity)

    def test_lock_requires_registered_tested_hypothesis(self):
        # Test 6: manifest tested set != registry/binding set -> wave cannot lock.
        firewall = ResearchFirewall(EvidenceLedger())
        wave = firewall.waves.register(make_wave_manifest(tested_hypothesis_test_ids=("h-missing",)))
        with self.assertRaisesRegex(ValueError, "not registered"):
            firewall.lock_wave(wave.research_wave_id)
        self.assertFalse(firewall.waves.is_locked(wave.research_wave_id))

    def test_lock_rejects_registration_pointing_to_another_wave(self):
        firewall = ResearchFirewall(EvidenceLedger())
        profile = firewall.profiles.register(make_test_only_profile())
        wave_a = firewall.waves.register(make_wave_manifest(wave_id="wave-a", tested_hypothesis_test_ids=("h-1",)))
        wave_b = firewall.waves.register(make_wave_manifest(wave_id="wave-b", tested_hypothesis_test_ids=("h-1",)))
        session = make_open_session(firewall.source_only)
        exp = ExperimentIdentity.from_strategy(strategy(), "data-fixture-v1", "exposure-fixture-v1")
        # Register h-1 under wave-b, then try to lock wave-a which also claims h-1.
        firewall.register_outcome_test(
            hypothesis_test_id="h-1",
            strategy=strategy(),
            experiment=exp,
            family_claim_identity="family-1",
            primary_branch_identity="primary-1",
            scope_identity="scope-1",
            parameter_search_identity="param-1",
            source_only_session_id=session.session_id,
            research_wave_id="wave-b",
            statistical_profile_id=profile.profile_id,
            multiplicity_counting_unit_identity=wave_b.multiplicity_counting_unit_identity,
        )
        with self.assertRaisesRegex(ValueError, "another wave"):
            firewall.lock_wave(wave_a.research_wave_id)

    def test_wave_profile_identity_mismatch_is_rejected(self):
        # Test 5: wave/profile identity mismatch -> DENY (registration rejected).
        firewall = ResearchFirewall(EvidenceLedger())
        profile = firewall.profiles.register(make_test_only_profile())
        wave = firewall.waves.register(
            make_wave_manifest(
                wave_id="wave-p",
                profile_id=profile.profile_id,
                profile_identity="wrong-profile-identity",
                tested_hypothesis_test_ids=("h-1",),
            )
        )
        session = make_open_session(firewall.source_only)
        exp = ExperimentIdentity.from_strategy(strategy(), "data-fixture-v1", "exposure-fixture-v1")
        with self.assertRaisesRegex(ValueError, "profile"):
            firewall.register_outcome_test(
                hypothesis_test_id="h-1",
                strategy=strategy(),
                experiment=exp,
                family_claim_identity="family-1",
                primary_branch_identity="primary-1",
                scope_identity="scope-1",
                parameter_search_identity="param-1",
                source_only_session_id=session.session_id,
                research_wave_id="wave-p",
                statistical_profile_id=profile.profile_id,
                multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
            )
        self.assertFalse(firewall.waves.is_locked("wave-p"))

    def test_empty_tested_denominator_cannot_lock(self):
        # Test 7: empty tested denominator -> wave cannot lock (rejected at build).
        with self.assertRaisesRegex(ValueError, "non-empty"):
            make_wave_manifest(tested_hypothesis_test_ids=())

    def test_denominator_derived_from_manifest_and_permanent(self):
        firewall = ResearchFirewall(EvidenceLedger())
        profile = firewall.profiles.register(make_test_only_profile())
        session = make_open_session(firewall.source_only)
        wave = firewall.waves.register(make_wave_manifest(tested_hypothesis_test_ids=("h-1", "h-2")))
        for hyp, family in (("h-1", "family-1"), ("h-2", "family-2")):
            strategy_obj = strategy(family_id=family)
            exp = ExperimentIdentity.from_strategy(strategy_obj, "data-fixture-v1", "exposure-fixture-v1")
            firewall.register_outcome_test(
                hypothesis_test_id=hyp,
                strategy=strategy_obj,
                experiment=exp,
                family_claim_identity=family,
                primary_branch_identity="primary-1",
                scope_identity="scope-1",
                parameter_search_identity="param-1",
                source_only_session_id=session.session_id,
                research_wave_id=wave.research_wave_id,
                statistical_profile_id=profile.profile_id,
                multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
            )
        firewall.lock_wave(wave.research_wave_id)
        self.assertEqual(firewall.waves.denominator(wave.research_wave_id), ("h-1", "h-2"))
        firewall.waves.declare_outcome_test_start(wave.research_wave_id)
        firewall.waves.record_terminal_outcome(wave.research_wave_id, "h-1", "FAIL")
        firewall.waves.record_terminal_outcome(wave.research_wave_id, "h-2", "INSUFFICIENT_EVIDENCE")
        # FAIL / INSUFFICIENT_EVIDENCE stay permanently in the denominator.
        self.assertEqual(firewall.waves.denominator(wave.research_wave_id), ("h-1", "h-2"))
        outcomes = dict(firewall.waves.outcome_records(wave.research_wave_id))
        self.assertEqual(outcomes["h-1"], "FAIL")
        self.assertEqual(outcomes["h-2"], "INSUFFICIENT_EVIDENCE")

    def test_outcome_cannot_be_silently_overwritten(self):
        # Test 10: a second different outcome cannot overwrite the first.
        firewall = ResearchFirewall(EvidenceLedger())
        profile = firewall.profiles.register(make_test_only_profile())
        session = make_open_session(firewall.source_only)
        wave = firewall.waves.register(make_wave_manifest(tested_hypothesis_test_ids=("h-1",)))
        exp = ExperimentIdentity.from_strategy(strategy(), "data-fixture-v1", "exposure-fixture-v1")
        firewall.register_outcome_test(
            hypothesis_test_id="h-1",
            strategy=strategy(),
            experiment=exp,
            family_claim_identity="family-1",
            primary_branch_identity="primary-1",
            scope_identity="scope-1",
            parameter_search_identity="param-1",
            source_only_session_id=session.session_id,
            research_wave_id=wave.research_wave_id,
            statistical_profile_id=profile.profile_id,
            multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
        )
        firewall.lock_wave(wave.research_wave_id)
        firewall.waves.record_terminal_outcome(wave.research_wave_id, "h-1", "FAIL")
        with self.assertRaisesRegex(ValueError, "cannot overwrite"):
            firewall.waves.record_terminal_outcome(wave.research_wave_id, "h-1", "PASS")
        # Idempotent re-record of the same fact is allowed.
        firewall.waves.record_terminal_outcome(wave.research_wave_id, "h-1", "FAIL")
        self.assertEqual(firewall.waves.outcome_records(wave.research_wave_id), (("h-1", "FAIL"),))

    def test_unlocked_wave_cannot_start_outcome_testing(self):
        firewall = ResearchFirewall(EvidenceLedger())
        wave = firewall.waves.register(make_wave_manifest())
        with self.assertRaisesRegex(ValueError, "unlocked wave"):
            firewall.waves.declare_outcome_test_start(wave.research_wave_id)


class StatisticalProfileRegistryTests(unittest.TestCase):
    def test_profile_lock_and_identity_are_deterministic(self):
        registry = ResearchFirewall(EvidenceLedger()).profiles
        profile = registry.register(make_test_only_profile())
        self.assertFalse(registry.is_locked(profile.profile_id))
        self.assertTrue(profile.is_test_only)
        registry.lock(profile.profile_id)
        self.assertTrue(registry.is_locked(profile.profile_id))
        self.assertEqual(profile.profile_identity, make_test_only_profile().profile_identity)

    def test_unknown_profile_lock_is_rejected(self):
        registry = ResearchFirewall(EvidenceLedger()).profiles
        with self.assertRaisesRegex(ValueError, "unknown"):
            registry.lock("missing-profile")

    def test_real_profile_fields_are_not_invented(self):
        # The interface binds method names only; it must not freeze numeric standards.
        profile = make_test_only_profile()
        self.assertEqual(profile.test_only_marker, "TEST_ONLY")
        self.assertEqual(
            profile.profile_identity,
            make_test_only_profile().profile_identity,
        )


class HistoricalFinalHoldoutStateMachineTests(unittest.TestCase):
    def test_default_is_locked_and_never_auto_unlocks(self):
        machine = HistoricalFinalHoldoutStateMachine()
        self.assertTrue(machine.is_locked)
        self.assertEqual(machine.state, FinalHoldoutState.FINAL_HISTORICAL_HOLDOUT_LOCKED)
        with self.assertRaisesRegex(ValueError, "no final-holdout unlock authority"):
            machine.expose("anyone")

    def test_expose_requires_explicit_registered_authority(self):
        machine = HistoricalFinalHoldoutStateMachine()
        machine.register_unlock_authority("owner-gate-1")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            machine.expose("wrong-authority")
        machine.expose("owner-gate-1")
        self.assertTrue(machine.is_exposed)

    def test_void_never_restores_holdout_status(self):
        machine = HistoricalFinalHoldoutStateMachine()
        machine.register_unlock_authority("owner-gate-1")
        machine.expose("owner-gate-1")
        machine.conclude(FinalHoldoutState.FINAL_VOID_IMPLEMENTATION_DEFECT)
        self.assertEqual(machine.state, FinalHoldoutState.FINAL_VOID_IMPLEMENTATION_DEFECT)
        self.assertFalse(machine.is_locked)
        with self.assertRaisesRegex(ValueError, "LOCKED"):
            machine.expose("owner-gate-1")

    def test_terminal_conclusion_requires_exposure(self):
        machine = HistoricalFinalHoldoutStateMachine()
        with self.assertRaisesRegex(ValueError, "EXPOSED"):
            machine.conclude(FinalHoldoutState.FINAL_ACCEPTED)


class IdentityBoundGateTests(unittest.TestCase):
    """The required identity-bound pre-outcome gate regressions."""

    def setUp(self):
        self.ledger = EvidenceLedger()
        self.firewall, self.session, self.profile, self.wave, self.experiment = make_registered_firewall(self.ledger)

    def _grant(self, *, cohort=Cohort.DEVELOPMENT, hypothesis_test_id=HYPOTHESIS_TEST_ID, experiment=None, synthetic_fixture=True):
        return self.firewall.request_candidate_outcome_access(
            cohort=cohort,
            experiment=experiment if experiment is not None else self.experiment,
            hypothesis_test_id=hypothesis_test_id,
            synthetic_fixture=synthetic_fixture,
        )

    # 1. unrelated locked wave cannot authorize an experiment outside its test set
    def test_unrelated_locked_wave_cannot_authorize_other_experiment(self):
        firewall2, _, _, _, experiment2 = make_registered_firewall(
            EvidenceLedger(),
            hypothesis_test_id="h-other",
            session_id="source-only-session-2",
            wave_id="wave-2",
            family_claim_identity="family-other",
            strategy_obj=strategy(family_id="family-other"),
        )
        self.assertTrue(firewall2.waves.is_locked("wave-2"))
        # The first hypothesis cannot be granted to the other wave's experiment.
        access = self._grant(hypothesis_test_id=HYPOTHESIS_TEST_ID, experiment=experiment2)
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "IDENTITY_BINDING:EXPERIMENT_IDENTITY_MISMATCH")
        # And the other wave's hypothesis is not registered in this firewall.
        access2 = self._grant(hypothesis_test_id="h-other", experiment=self.experiment)
        self.assertFalse(access2.allowed)
        self.assertEqual(access2.record.evidence_reference, "IDENTITY_BINDING:UNREGISTERED_HYPOTHESIS_TEST")

    # 2. unrelated verified SOURCE_ONLY session cannot authorize another lineage
    def test_unrelated_verified_session_cannot_authorize_other_lineage(self):
        firewall2, session2, _, _, experiment2 = make_registered_firewall(
            EvidenceLedger(),
            hypothesis_test_id="h-other",
            session_id="source-only-session-2",
            wave_id="wave-2",
            family_claim_identity="family-other",
            strategy_obj=strategy(family_id="family-other"),
        )
        self.assertTrue(firewall2.source_only.is_verified(session2.session_id))
        # session-2's verified status cannot authorize the other lineage's
        # experiment on this firewall's hypothesis.
        access = self._grant(hypothesis_test_id=HYPOTHESIS_TEST_ID, experiment=experiment2)
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "IDENTITY_BINDING:EXPERIMENT_IDENTITY_MISMATCH")

    # 4. authoritative API has no caller-controlled lock booleans
    def test_no_caller_controlled_lock_booleans(self):
        access_params = set(inspect.signature(self.firewall.request_candidate_outcome_access).parameters)
        for forbidden in (
            "multiplicity_counting_unit_locked",
            "primary_scope_search_identities_locked",
            "wave_id",
            "profile_id",
            "source_only_session_id",
        ):
            self.assertNotIn(forbidden, access_params)
        gate_params = set(inspect.signature(self.firewall.evaluate_gate).parameters)
        self.assertNotIn("multiplicity_counting_unit_locked", gate_params)
        self.assertNotIn("primary_scope_search_identities_locked", gate_params)

    # 5. wave/profile identity mismatch -> DENY (adversarial direct registration)
    def test_profile_identity_mismatch_blocks_wave_lock(self):
        firewall = ResearchFirewall(EvidenceLedger())
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)
        wave = firewall.waves.register(make_wave_manifest(tested_hypothesis_test_ids=("h-adv",)))
        session = make_open_session(firewall.source_only)
        exp = ExperimentIdentity.from_strategy(strategy(), "data-fixture-v1", "exposure-fixture-v1")
        # Bypass the validating factory to prove the access-preventing cross-check.
        firewall.tests.register(
            OutcomeTestRegistration(
                hypothesis_test_id="h-adv",
                experiment_identity_id=exp.experiment_id,
                strategy_identity_id=strategy().identity_id,
                research_lineage_id="research-lineage-fixture",
                family_claim_identity="family-1",
                primary_branch_identity="primary-1",
                scope_identity="scope-1",
                parameter_search_identity="param-1",
                source_only_session_id=session.session_id,
                source_only_session_identity=session.session_identity,
                source_bundle_identity=session.source_bundle_identity,
                source_bundle_hash=session.source_bundle_hash,
                research_wave_id=wave.research_wave_id,
                statistical_profile_id=profile.profile_id,
                statistical_profile_identity="wrong-profile-identity",
                multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
                protocol_version="1.0",
            )
        )
        with self.assertRaisesRegex(ValueError, "profile"):
            firewall.lock_wave(wave.research_wave_id)
        self.assertFalse(firewall.waves.is_locked(wave.research_wave_id))

    # 8. exact registered binding -> only synthetic DEVELOPMENT may pass
    def test_exact_registered_binding_permits_synthetic_development_only(self):
        decision = self.firewall.evaluate_gate(
            cohort=Cohort.DEVELOPMENT,
            experiment=self.experiment,
            hypothesis_test_id=HYPOTHESIS_TEST_ID,
            synthetic_fixture=True,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "SYNTHETIC_DEVELOPMENT_OUTCOME_ONLY")
        self.assertTrue(decision.synthetic_only)
        # TEST_ONLY profile refuses a non-synthetic fixture.
        real = self._grant(synthetic_fixture=False)
        self.assertFalse(real.allowed)
        self.assertEqual(real.record.evidence_reference, "TEST_ONLY_PROFILE_REQUIRES_SYNTHETIC_FIXTURE")

    # 9. first granted outcome marks the wave outcome-start durably
    def test_first_grant_marks_wave_outcome_start_durably(self):
        self.assertFalse(self.firewall.waves.has_outcome_test_started(self.wave.research_wave_id))
        access = self._grant()
        self.assertTrue(access.allowed)
        self.assertTrue(self.firewall.waves.has_outcome_test_started(self.wave.research_wave_id))
        started = [r for r in self.ledger.records if r.event_type == "WAVE_OUTCOME_TEST_STARTED"]
        self.assertEqual(len(started), 1)
        # The durable registry fact is idempotent (already declared).
        self.assertFalse(self.firewall.waves.declare_outcome_test_start(self.wave.research_wave_id))
        granted = [r for r in self.ledger.records if r.event_type == "PRE_OUTCOME_GATE_GRANTED"]
        self.assertEqual(len(granted), 1)
        self.assertIn("SYNTHETIC_TEST_ONLY_FIRST_LOOK", granted[0].evidence_reference)

    # 12. legacy FinalUnseenFirewall compatibility remains green
    def test_legacy_final_unseen_firewall_compatibility(self):
        ledger = EvidenceLedger()
        firewall = FinalUnseenFirewall(ledger)
        parent = StrategyCatalog().register(strategy())
        experiment = ExperimentIdentity.from_strategy(parent, "data-fixture-v1", "exposure-fixture-v1")

        development = firewall.request_access(experiment, DatasetClass.DEVELOPMENT)
        validation = firewall.request_access(experiment, DatasetClass.VALIDATION)
        final_legacy = firewall.request_access(experiment, DatasetClass.FINAL_UNSEEN)
        final_canonical = firewall.request_access(experiment, DatasetClass.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT)
        shadow = firewall.request_access(experiment, DatasetClass.SHADOW_FORWARD)

        self.assertTrue(development.allowed)
        self.assertTrue(validation.allowed)
        self.assertEqual(development.record.event_type, "DATASET_ACCESS_GRANTED")
        self.assertEqual(validation.record.event_type, "DATASET_ACCESS_GRANTED")
        self.assertFalse(final_legacy.allowed)
        self.assertFalse(final_canonical.allowed)
        self.assertFalse(shadow.allowed)
        self.assertEqual(final_legacy.record.event_type, "DATASET_ACCESS_DENIED")
        self.assertNotIn(DatasetClass.FINAL_UNSEEN, ledger.exposures_for(parent.research_lineage_id))

    # 13. VALIDATION remains DENIED
    def test_validation_remains_denied(self):
        access = self._grant(cohort=Cohort.VALIDATION)
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "VALIDATION_DEFAULT_DENY_NO_VALIDATION_AUTHORITY")

    # 14. historical final remains DENIED
    def test_historical_final_remains_denied(self):
        access = self._grant(cohort=Cohort.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT)
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "FINAL_HISTORICAL_HOLDOUT_ALWAYS_LOCKED")

    # 15. Shadow/Forward remains DENIED
    def test_shadow_forward_remains_denied(self):
        access = self._grant(cohort=Cohort.SHADOW_FORWARD)
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "SHADOW_FORWARD_NOT_AUTHORIZED")

    # extra: default firewall denies any candidate outcome access
    def test_default_firewall_denies_candidate_outcome_access(self):
        firewall = ResearchFirewall(EvidenceLedger())
        experiment = ExperimentIdentity.from_strategy(strategy(), "data-fixture-v1", "exposure-fixture-v1")
        access = firewall.request_candidate_outcome_access(
            cohort=Cohort.DEVELOPMENT,
            experiment=experiment,
            hypothesis_test_id="never-registered",
            synthetic_fixture=False,
        )
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "IDENTITY_BINDING:UNREGISTERED_HYPOTHESIS_TEST")

    # extra: an unverified session cannot authorize even through a fully locked wave
    def test_unverified_session_cannot_authorize_even_when_wave_locked(self):
        firewall = ResearchFirewall(EvidenceLedger())
        manual = SourceOnlySession(
            session_id="manual-session",
            model_identity="model-fixture-v1",
            prompt_spec_version="prompt-spec-v1",
            source_bundle_identity="bundle-fixture-v1",
            source_bundle_hash="bundle-hash-fixture-v1",
            tool_retrieval_mode="PROJECT_SOURCE_ONLY",
            protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
        )
        firewall.source_only.record_session(manual)
        self.assertFalse(firewall.source_only.is_verified("manual-session"))
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)
        wave = firewall.waves.register(make_wave_manifest(tested_hypothesis_test_ids=("h-1",)))
        exp = ExperimentIdentity.from_strategy(strategy(), "data-fixture-v1", "exposure-fixture-v1")
        firewall.register_outcome_test(
            hypothesis_test_id="h-1",
            strategy=strategy(),
            experiment=exp,
            family_claim_identity="family-1",
            primary_branch_identity="primary-1",
            scope_identity="scope-1",
            parameter_search_identity="param-1",
            source_only_session_id="manual-session",
            research_wave_id=wave.research_wave_id,
            statistical_profile_id=profile.profile_id,
            multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
        )
        firewall.lock_wave(wave.research_wave_id)
        access = firewall.request_candidate_outcome_access(
            cohort=Cohort.DEVELOPMENT,
            experiment=exp,
            hypothesis_test_id="h-1",
            synthetic_fixture=True,
        )
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "IDENTITY_BINDING:SOURCE_ONLY_NOT_VERIFIED")

    # extra: renaming a strategy/family cannot wash lineage/exposure
    def test_renaming_family_preserves_lineage_exposure(self):
        catalog = StrategyCatalog()
        parent = catalog.register(strategy())
        experiment = ExperimentIdentity.from_strategy(parent, "data-fixture-v1", "exposure-fixture-v1")
        self.firewall.legacy_request_access(experiment, DatasetClass.VALIDATION)
        child = catalog.register(
            strategy(family_id="renamed-family", version="2.0", parent_identity_id=parent.identity_id)
        )
        self.assertTrue(self.firewall.has_exposure(child, DatasetClass.VALIDATION))

    # extra: legacy coarse grants are not candidate-outcome authorization
    def test_legacy_coarse_grants_are_not_candidate_outcome_authorization(self):
        ledger = EvidenceLedger()
        firewall = ResearchFirewall(ledger)
        parent = StrategyCatalog().register(strategy())
        experiment = ExperimentIdentity.from_strategy(parent, "data-fixture-v1", "exposure-fixture-v1")
        coarse = firewall.legacy_request_access(experiment, DatasetClass.DEVELOPMENT)
        self.assertTrue(coarse.allowed)
        candidate = firewall.request_candidate_outcome_access(
            cohort=Cohort.DEVELOPMENT,
            experiment=experiment,
            hypothesis_test_id="never-registered",
            synthetic_fixture=False,
        )
        self.assertFalse(candidate.allowed)
        self.assertEqual(candidate.record.event_type, "PRE_OUTCOME_GATE_DENIED")


class SourceOnlyClaimExtractionContextTests(unittest.TestCase):
    """Bounded SOURCE_ONLY claim-extraction runner tests (Test 11)."""

    def _make_runner(self, policy=None, session=None):
        if policy is None:
            policy = ResearchFirewall(EvidenceLedger()).source_only
        if session is None:
            session = make_open_session(policy)
        bundle = ApprovedSourceBundle(
            source_bundle_id="bundle-fixture-v1",
            source_bundle_hash="bundle-hash-fixture-v1",
            source_anchor_reference="fixture:book:edition-1:chapter-1",
        )
        output = ClaimRecordOutput()
        runner = SourceOnlyClaimExtractionContext(
            source_bundle=bundle,
            source_only=policy,
            session_id=session.session_id,
            output_surface=output,
        )
        return runner, output, bundle

    def test_runner_is_verified_and_records_claims(self):
        runner, output, bundle = self._make_runner()
        self.assertTrue(runner.verified)
        draft = ClaimRecordDraft(
            claim_id="claim-1",
            source_id=bundle.source_bundle_id,
            source_anchor="fixture:book:edition-1:chapter-1:page-12",
            claim_status="EXPLICIT",
            source_excerpt_short_or_paraphrase="synthetic fixture claim",
            source_only_session_id=runner.session_id,
            created_at="2026-08-19T00:00:00Z",
        )
        recorded = runner.record_claim(draft)
        self.assertEqual(recorded.claim_id, "claim-1")
        self.assertEqual(len(output.records), 1)

    def test_runner_cannot_access_protected_period_market_outcomes(self):
        # Test 11: the SOURCE_ONLY runner has no market-outcome surface; any
        # protected-period project market outcome request is DENIED + audited.
        runner, _, _ = self._make_runner()
        result = runner.request_protected_market_outcome("some-market-outcome-request")
        self.assertEqual(result.outcome, "DENIED")
        self.assertEqual(result.reason, "SOURCE_ONLY_TECHNICAL_DENIAL")
        self.assertEqual(len(runner.denial_records), 1)
        self.assertFalse(hasattr(runner, "market_data"))
        self.assertFalse(hasattr(runner, "outcomes"))

    def test_runner_does_not_hold_market_or_outcome_surfaces(self):
        runner, _, _ = self._make_runner()
        for forbidden in ("_market", "_outcome", "_validation", "_final"):
            self.assertFalse(
                any(attribute.startswith(forbidden) for attribute in vars(runner)),
                f"runner must not hold {forbidden} surfaces",
            )

    def test_runner_rejects_claim_bound_to_another_session(self):
        runner, output, bundle = self._make_runner()
        draft = ClaimRecordDraft(
            claim_id="claim-x",
            source_id=bundle.source_bundle_id,
            source_anchor="fixture:anchor",
            claim_status="EXPLICIT",
            source_excerpt_short_or_paraphrase="synthetic",
            source_only_session_id="other-session",
            created_at="2026-08-19T00:00:00Z",
        )
        with self.assertRaisesRegex(ValueError, "session"):
            runner.record_claim(draft)


class PreOutcomeGateUnitTests(unittest.TestCase):
    """Direct unit tests of the low-level pure gate (boolean interface).

    The authoritative production path never accepts caller booleans; these tests
    keep the pure gate function itself covered.
    """

    def setUp(self):
        self.gate = PreOutcomeGate()

    def _evaluate(self, cohort=Cohort.DEVELOPMENT, **overrides):
        defaults = dict(
            source_only_verified=True,
            statistical_profile_locked=True,
            statistical_profile_test_only=True,
            multiplicity_counting_unit_locked=True,
            research_wave_locked=True,
            primary_scope_search_identities_locked=True,
            synthetic_fixture=True,
        )
        defaults.update(overrides)
        return self.gate.evaluate(cohort=cohort, **defaults)

    def test_all_satisfied_development_grants_synthetic_only(self):
        decision = self._evaluate()
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "SYNTHETIC_DEVELOPMENT_OUTCOME_ONLY")

    def test_final_always_denied_regardless_of_controls(self):
        decision = self._evaluate(cohort=Cohort.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "FINAL_HISTORICAL_HOLDOUT_ALWAYS_LOCKED")

    def test_missing_control_fails_closed(self):
        decision = self._evaluate(source_only_verified=False)
        self.assertFalse(decision.allowed)
        self.assertIn("SOURCE_ONLY_CONTROLS", decision.reason)


if __name__ == "__main__":
    unittest.main()

"""Deterministic regression tests for the pre-outcome research firewall.

Covers the frozen Selection Firewall requirements (v1.0) implementation:
- SOURCE_ONLY session/policy technical denial
- immutable RESEARCH_WAVE manifests and permanent tested denominator
- common statistical profile identity/lock interface (TEST_ONLY fixtures)
- the single fail-closed pre-outcome gate (all 14 minimum checks)
- historical final-holdout state machine (no auto-unlock)
- frozen 12/6/6 chronology classification
- legacy FinalUnseenFirewall compatibility
"""

import unittest
from dataclasses import FrozenInstanceError
from datetime import date

from src.research_firewall import (
    Cohort,
    CommonStatisticalProfile,
    FinalHoldoutState,
    FrozenResearchProtocol,
    HistoricalFinalHoldoutStateMachine,
    ProtectedMarketAccessMode,
    ResearchFirewall,
    ResearchWaveManifest,
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


def make_wave_manifest(
    wave_id="wave-test-only-v1",
    family_ids=("family-fixture-v1",),
    primary_branches=("primary-branch-fixture-v1",),
    created_at="2026-08-19T00:00:00Z",
):
    return ResearchWaveManifest(
        research_wave_id=wave_id,
        protocol_version="1.0",
        statistical_profile_version="0.0-test",
        tested_family_claim_identities=family_ids,
        primary_branch_identities=primary_branches,
        declared_outcome_tested_alternatives=(),
        instrument_timeframe_context_scope="TEST_ONLY:instrument=TEST;timeframe=5m;context=TEST",
        parameter_search_ranges="TEST_ONLY:none",
        denominator_counting_semantics="TEST_ONLY:independent-falsifiable-hypotheses",
        created_at=created_at,
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


def make_source_only_session(session_id="source-only-session-1"):
    return SourceOnlySession(
        session_id=session_id,
        model_identity="model-fixture-v1",
        prompt_spec_version="prompt-spec-v1",
        source_bundle_identity="bundle-fixture-v1",
        source_bundle_hash="bundle-hash-fixture-v1",
        tool_retrieval_mode="PROJECT_SOURCE_ONLY",
        protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
    )


def make_satisfied_firewall(ledger):
    """Fully-satisfied pre-outcome control stack using TEST_ONLY fixtures only."""
    firewall = ResearchFirewall(ledger)
    session = firewall.source_only.record_session(make_source_only_session())
    profile = firewall.profiles.register(make_test_only_profile())
    firewall.profiles.lock(profile.profile_id)
    wave = firewall.waves.register(make_wave_manifest())
    firewall.waves.add_tested_hypothesis(wave.research_wave_id, "hypothesis-fixture-v1")
    firewall.waves.lock(wave.research_wave_id)
    return firewall, session.session_id, profile.profile_id, wave.research_wave_id


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
    def test_verified_session_records_all_required_fields(self):
        policy = ResearchFirewall(EvidenceLedger()).source_only
        session = policy.record_session(
            SourceOnlySession(
                session_id="s1",
                model_identity="model-fixture-v1",
                prompt_spec_version="prompt-spec-v1",
                source_bundle_identity="bundle-fixture-v1",
                source_bundle_hash="bundle-hash-fixture-v1",
                tool_retrieval_mode="PROJECT_SOURCE_ONLY",
                protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
                researcher_model_exposure_note="no known exposure",
            )
        )
        self.assertTrue(policy.is_verified("s1"))
        self.assertEqual(session.session_identity, session.session_identity)
        again = SourceOnlySession(
            session_id="s1",
            model_identity="model-fixture-v1",
            prompt_spec_version="prompt-spec-v1",
            source_bundle_identity="bundle-fixture-v1",
            source_bundle_hash="bundle-hash-fixture-v1",
            tool_retrieval_mode="PROJECT_SOURCE_ONLY",
            protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
            researcher_model_exposure_note="no known exposure",
        )
        self.assertEqual(again.session_identity, session.session_identity)

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
        policy.record_session(make_source_only_session())
        with self.assertRaisesRegex(ValueError, "duplicate"):
            policy.record_session(make_source_only_session())


class ResearchWaveRegistryTests(unittest.TestCase):
    def test_wave_manifest_is_immutable(self):
        registry = ResearchFirewall(EvidenceLedger()).waves
        manifest = registry.register(make_wave_manifest())
        with self.assertRaises(FrozenInstanceError):
            manifest.denominator_counting_semantics = "changed"

    def test_manifest_identity_is_deterministic(self):
        registry = ResearchFirewall(EvidenceLedger()).waves
        first = registry.register(make_wave_manifest())
        second = registry.register(make_wave_manifest(wave_id="wave-2"))
        self.assertEqual(first.manifest_identity, make_wave_manifest().manifest_identity)
        self.assertNotEqual(first.manifest_identity, second.manifest_identity)

    def test_lock_then_append_is_forbidden(self):
        registry = ResearchFirewall(EvidenceLedger()).waves
        wave = registry.register(make_wave_manifest())
        registry.add_tested_hypothesis(wave.research_wave_id, "h1")
        registry.lock(wave.research_wave_id)
        self.assertTrue(registry.is_locked(wave.research_wave_id))
        with self.assertRaisesRegex(ValueError, "locked wave"):
            registry.add_tested_hypothesis(wave.research_wave_id, "h2")

    def test_append_after_outcome_test_start_requires_new_wave(self):
        registry = ResearchFirewall(EvidenceLedger()).waves
        wave = registry.register(make_wave_manifest())
        registry.add_tested_hypothesis(wave.research_wave_id, "h1")
        registry.lock(wave.research_wave_id)
        registry.declare_outcome_test_start(wave.research_wave_id)
        self.assertTrue(registry.has_outcome_test_started(wave.research_wave_id))
        # The wave is locked before outcome testing starts, so a late hypothesis is
        # rejected (fail closed) and the test set stays immutable.
        with self.assertRaises(ValueError):
            registry.add_tested_hypothesis(wave.research_wave_id, "h2")
        self.assertEqual(registry.denominator(wave.research_wave_id), ("h1",))
        # A new hypothesis requires a new wave / new search event.
        new_wave = registry.register(make_wave_manifest(wave_id="wave-2", family_ids=("family-2",)))
        registry.add_tested_hypothesis(new_wave.research_wave_id, "h2")
        self.assertEqual(registry.denominator(new_wave.research_wave_id), ("h2",))

    def test_denominator_keeps_fail_and_insufficient_evidence(self):
        registry = ResearchFirewall(EvidenceLedger()).waves
        wave = registry.register(make_wave_manifest(family_ids=("f1", "f2")))
        registry.add_tested_hypothesis(wave.research_wave_id, "h1")
        registry.add_tested_hypothesis(wave.research_wave_id, "h2")
        registry.lock(wave.research_wave_id)
        registry.declare_outcome_test_start(wave.research_wave_id)
        registry.record_outcome(wave.research_wave_id, "h1", "FAIL")
        registry.record_outcome(wave.research_wave_id, "h2", "INSUFFICIENT_EVIDENCE")
        self.assertEqual(registry.denominator(wave.research_wave_id), ("h1", "h2"))
        outcomes = dict(registry.denominator_with_outcomes(wave.research_wave_id))
        self.assertEqual(outcomes["h1"], "FAIL")
        self.assertEqual(outcomes["h2"], "INSUFFICIENT_EVIDENCE")

    def test_unlocked_wave_cannot_start_outcome_testing(self):
        registry = ResearchFirewall(EvidenceLedger()).waves
        wave = registry.register(make_wave_manifest())
        with self.assertRaisesRegex(ValueError, "unlocked wave"):
            registry.declare_outcome_test_start(wave.research_wave_id)


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


class PreOutcomeGateTests(unittest.TestCase):
    """The 14 minimum pre-outcome gate checks."""

    def setUp(self):
        self.ledger = EvidenceLedger()
        self.firewall, self.session_id, self.profile_id, self.wave_id = make_satisfied_firewall(self.ledger)

    def _gate(self, **overrides):
        defaults = dict(
            cohort=Cohort.DEVELOPMENT,
            source_only_session_id=self.session_id,
            wave_id=self.wave_id,
            profile_id=self.profile_id,
            multiplicity_counting_unit_locked=True,
            primary_scope_search_identities_locked=True,
            synthetic_fixture=True,
        )
        defaults.update(overrides)
        return self.firewall.evaluate_gate(**defaults)

    def _control(self, decision, name):
        return next(control for control in decision.controls if control.name == name)

    # 1. SOURCE_ONLY missing -> DENY
    def test_missing_source_only_denies(self):
        decision = self._gate(source_only_session_id="does-not-exist")
        self.assertFalse(decision.allowed)
        self.assertFalse(self._control(decision, "SOURCE_ONLY_CONTROLS").satisfied)

    # 2. SOURCE_ONLY unverified -> DENY
    def test_unverified_source_only_denies(self):
        self.firewall.source_only.record_session(
            SourceOnlySession(
                session_id="prompt-only-session",
                model_identity="model-fixture-v1",
                prompt_spec_version="prompt-spec-v1",
                source_bundle_identity="bundle-fixture-v1",
                source_bundle_hash="bundle-hash-fixture-v1",
                tool_retrieval_mode="PROJECT_SOURCE_ONLY",
                protected_market_access_mode=ProtectedMarketAccessMode.PROMPT_ONLY,
            )
        )
        self.assertFalse(self.firewall.source_only.is_verified("prompt-only-session"))
        decision = self._gate(source_only_session_id="prompt-only-session")
        self.assertFalse(decision.allowed)

    # 3. profile missing -> DENY
    def test_missing_statistical_profile_denies(self):
        decision = self._gate(profile_id="does-not-exist")
        self.assertFalse(decision.allowed)
        self.assertFalse(self._control(decision, "COMMON_STATISTICAL_PROFILE").satisfied)

    # 4. profile draft / unlocked -> DENY
    def test_unlocked_statistical_profile_denies(self):
        draft = self.firewall.profiles.register(make_test_only_profile(profile_id="profile-draft"))
        decision = self._gate(profile_id=draft.profile_id)
        self.assertFalse(decision.allowed)

    # 5. wave missing -> DENY
    def test_missing_wave_denies(self):
        decision = self._gate(wave_id="does-not-exist")
        self.assertFalse(decision.allowed)
        self.assertFalse(self._control(decision, "RESEARCH_WAVE").satisfied)

    # 6. wave unlocked -> DENY
    def test_unlocked_wave_denies(self):
        unlocked = self.firewall.waves.register(make_wave_manifest(wave_id="wave-unlocked"))
        decision = self._gate(wave_id=unlocked.research_wave_id)
        self.assertFalse(decision.allowed)

    # 7. PRIMARY/scope/search identities not locked -> DENY
    def test_primary_scope_search_identities_not_locked_denies(self):
        decision = self._gate(primary_scope_search_identities_locked=False)
        self.assertFalse(decision.allowed)
        self.assertFalse(self._control(decision, "PRIMARY_SCOPE_SEARCH_IDENTITIES").satisfied)

    # 8. all satisfied -> synthetic DEVELOPMENT only
    def test_all_satisfied_permits_synthetic_development_only(self):
        decision = self._gate()
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.cohort, Cohort.DEVELOPMENT)
        self.assertTrue(decision.synthetic_only)
        self.assertEqual(decision.reason, "SYNTHETIC_DEVELOPMENT_OUTCOME_ONLY")

        experiment = ExperimentIdentity.from_strategy(strategy(), "data-fixture-v1", "exposure-fixture-v1")
        access = self.firewall.request_candidate_outcome_access(
            cohort=Cohort.DEVELOPMENT,
            experiment=experiment,
            source_only_session_id=self.session_id,
            wave_id=self.wave_id,
            profile_id=self.profile_id,
            multiplicity_counting_unit_locked=True,
            primary_scope_search_identities_locked=True,
            synthetic_fixture=True,
        )
        self.assertTrue(access.allowed)
        self.assertEqual(access.record.event_type, "PRE_OUTCOME_GATE_GRANTED")

    def test_test_only_profile_denies_real_candidate_fixture(self):
        decision = self._gate(synthetic_fixture=False)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "TEST_ONLY_PROFILE_REQUIRES_SYNTHETIC_FIXTURE")

    # 9. VALIDATION still default DENY (no validation authority yet)
    def test_validation_default_deny(self):
        decision = self._gate(cohort=Cohort.VALIDATION)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "VALIDATION_DEFAULT_DENY_NO_VALIDATION_AUTHORITY")

    # 10. HISTORICAL FINAL HOLDOUT always DENY
    def test_historical_final_holdout_always_denied(self):
        decision = self._gate(cohort=Cohort.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "FINAL_HISTORICAL_HOLDOUT_ALWAYS_LOCKED")

    # 11. Shadow/Forward DENY
    def test_shadow_forward_denied(self):
        decision = self._gate(cohort=Cohort.SHADOW_FORWARD)
        self.assertFalse(decision.allowed)
        self.assertEqual(decision.reason, "SHADOW_FORWARD_NOT_AUTHORIZED")

    # 12. locked wave cannot append hypothesis
    def test_locked_wave_cannot_append_hypothesis(self):
        with self.assertRaisesRegex(ValueError, "locked wave"):
            self.firewall.waves.add_tested_hypothesis(self.wave_id, "late-hypothesis")

    # 13. renaming a strategy/family cannot wash lineage/exposure
    def test_renaming_family_preserves_lineage_exposure(self):
        catalog = StrategyCatalog()
        parent = catalog.register(strategy())
        experiment = ExperimentIdentity.from_strategy(parent, "data-fixture-v1", "exposure-fixture-v1")
        self.firewall.legacy_request_access(experiment, DatasetClass.VALIDATION)
        child = catalog.register(
            strategy(family_id="renamed-family", version="2.0", parent_identity_id=parent.identity_id)
        )
        self.assertTrue(self.firewall.has_exposure(child, DatasetClass.VALIDATION))

    # 14. legacy FinalUnseenFirewall behavior must not silently break
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


class ResearchFirewallIntegrationTests(unittest.TestCase):
    def test_default_firewall_denies_candidate_outcome_access(self):
        firewall = ResearchFirewall(EvidenceLedger())
        experiment = ExperimentIdentity.from_strategy(strategy(), "data-fixture-v1", "exposure-fixture-v1")
        access = firewall.request_candidate_outcome_access(
            cohort=Cohort.DEVELOPMENT,
            experiment=experiment,
            source_only_session_id="missing",
            wave_id="missing",
            profile_id="missing",
            multiplicity_counting_unit_locked=False,
            primary_scope_search_identities_locked=False,
            synthetic_fixture=False,
        )
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.event_type, "PRE_OUTCOME_GATE_DENIED")
        self.assertEqual(access.record.outcome, "DENIED")

    def test_candidate_final_holdout_access_is_denied_even_when_controls_satisfied(self):
        firewall, session_id, profile_id, wave_id = make_satisfied_firewall(EvidenceLedger())
        experiment = ExperimentIdentity.from_strategy(strategy(), "data-fixture-v1", "exposure-fixture-v1")
        access = firewall.request_candidate_outcome_access(
            cohort=Cohort.PROJECT_GOVERNED_HISTORICAL_FINAL_HOLDOUT,
            experiment=experiment,
            source_only_session_id=session_id,
            wave_id=wave_id,
            profile_id=profile_id,
            multiplicity_counting_unit_locked=True,
            primary_scope_search_identities_locked=True,
            synthetic_fixture=True,
        )
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.event_type, "PRE_OUTCOME_GATE_DENIED")

    def test_legacy_coarse_grants_are_not_candidate_outcome_authorization(self):
        # A coarse DEVELOPMENT grant through the legacy path must not be usable as
        # candidate-outcome authorization: the authoritative gate still fails closed
        # when the real control stack is absent.
        ledger = EvidenceLedger()
        firewall = ResearchFirewall(ledger)
        parent = StrategyCatalog().register(strategy())
        experiment = ExperimentIdentity.from_strategy(parent, "data-fixture-v1", "exposure-fixture-v1")
        coarse = firewall.legacy_request_access(experiment, DatasetClass.DEVELOPMENT)
        self.assertTrue(coarse.allowed)
        candidate = firewall.request_candidate_outcome_access(
            cohort=Cohort.DEVELOPMENT,
            experiment=experiment,
            source_only_session_id="missing",
            wave_id="missing",
            profile_id="missing",
            multiplicity_counting_unit_locked=False,
            primary_scope_search_identities_locked=False,
            synthetic_fixture=False,
        )
        self.assertFalse(candidate.allowed)
        self.assertEqual(candidate.record.event_type, "PRE_OUTCOME_GATE_DENIED")


if __name__ == "__main__":
    unittest.main()

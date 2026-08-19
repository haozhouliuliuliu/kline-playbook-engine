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
import os
import tempfile
import unittest
from dataclasses import FrozenInstanceError, replace
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
    TEST_ONLY_SYNTHETIC_DATA_VERSION,
    WaveHypothesisBinding,
    _canonical_hash,
    classify_cohort,
)
from src.strategy_evidence import (
    ArtifactBinding,
    DatasetClass,
    EvidenceLedger,
    ExperimentIdentity,
    FinalUnseenFirewall,
    LifecycleState,
    OutcomeArtifactBindings,
    StrategyCatalog,
    StrategyIdentity,
    TypedParameter,
)
from tests.synthetic_fixture import (
    SYNTHETIC_HYPOTHESIS_TEST_ID,
    SYNTHETIC_SESSION_ID,
    build_synthetic_firewall,
    make_artifact_bindings,
    make_code_artifact,
    make_contract,
    make_data_artifact,
    make_environment_artifact,
    make_experiment,
    make_feature_artifact,
    make_open_session,
    make_strategy,
    make_test_only_profile,
    make_wave_manifest,
    make_validation_input,
    synthetic_session_identity,
)


def strategy(*, family_id="neutral-family", version="1.0", parent_identity_id=None):
    """Deterministic synthetic strategy bound to the default synthetic contract."""
    return make_strategy(
        family_id=family_id,
        strategy_version=version,
        parent_identity_id=parent_identity_id,
    )


HYPOTHESIS_TEST_ID = SYNTHETIC_HYPOTHESIS_TEST_ID
COUNTING_UNIT_IDENTITY = "counting-unit-test-v1"
# Bogus/manual binding values used by adversarial tests to prove the wave-lock
# and gate cross-binding checks reject identities that differ from the values
# derived from the actual artifacts.
PRIMARY_BRANCH_IDENTITY = "bogus-primary-identity"
SCOPE_IDENTITY = "bogus-scope-identity"
PARAMETER_SEARCH_IDENTITY = "bogus-parameter-search-identity"


def make_registered_firewall(
    ledger,
    *,
    hypothesis_test_id=HYPOTHESIS_TEST_ID,
    session_id="source-only-session-1",
    profile_id="profile-test-only-v1",
    wave_id="wave-test-only-v1",
    family="neutral-family",
    contract=None,
    strategy_obj=None,
    artifact_bindings=None,
):
    """Build a fully artifact-bound firewall: verified session + TEST_ONLY
    profile + wave (bindings derived from contract/strategy) + one registered
    outcome test bound to the PlaybookContract and artifact bindings, with the
    wave locked."""
    if contract is None:
        contract = make_contract(
            family_id=family,
            source_only_session_identity=synthetic_session_identity(session_id),
        )
    if strategy_obj is None:
        strategy_obj = make_strategy(contract)
    else:
        # A caller-supplied strategy must still be bound to the supplied contract.
        if strategy_obj.playbook_contract_identity != contract.contract_identity:
            raise AssertionError("strategy_obj must be bound to the supplied contract")
    experiment = make_experiment(strategy_obj)
    firewall = ResearchFirewall(ledger)
    session = make_open_session(firewall.source_only, session_id=session_id)
    profile = firewall.profiles.register(make_test_only_profile(profile_id=profile_id))
    firewall.profiles.lock(profile.profile_id)
    wave = firewall.waves.register(
        make_wave_manifest(
            wave_id=wave_id,
            contract=contract,
            strategy=strategy_obj,
            profile_id=profile.profile_id,
            profile_identity=profile.profile_identity,
            tested_hypothesis_test_ids=(hypothesis_test_id,),
        )
    )
    firewall.register_outcome_test(
        hypothesis_test_id=hypothesis_test_id,
        contract=contract,
        strategy=strategy_obj,
        experiment=experiment,
        artifact_bindings=artifact_bindings or make_artifact_bindings(),
        source_only_session_id=session.session_id,
        research_wave_id=wave.research_wave_id,
        statistical_profile_id=profile.profile_id,
        multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
    )
    firewall.lock_wave(wave.research_wave_id)
    return firewall, session, profile, wave, experiment


def register_adversarial_registration(
    firewall,
    wave,
    hypothesis_test_id,
    *,
    primary_branch_identity=None,
    scope_identity=None,
    parameter_search_identity=None,
):
    """Directly register an OutcomeTestRegistration bypassing the validating
    factory, to prove the wave-lock / gate cross-binding checks catch mismatches.
    The default identity values are the wave binding's DERIVED values, so a test
    overrides exactly one field to isolate a mismatch.
    """
    profile = firewall.profiles.get(wave.statistical_profile_id)
    if profile is None:
        raise AssertionError("wave profile must be registered first")
    binding = wave.binding_for(hypothesis_test_id)
    if binding is None:
        raise AssertionError(f"wave has no binding for {hypothesis_test_id}")
    if primary_branch_identity is None:
        primary_branch_identity = binding.primary_branch_identity
    if scope_identity is None:
        scope_identity = binding.scope_identity
    if parameter_search_identity is None:
        parameter_search_identity = binding.parameter_search_identity
    contract = make_contract()
    session = make_open_session(firewall.source_only, session_id=f"adversarial-{hypothesis_test_id}")
    strategy_obj = make_strategy(contract)
    experiment = make_experiment(strategy_obj)
    return firewall.tests.register(
        OutcomeTestRegistration(
            hypothesis_test_id=hypothesis_test_id,
            experiment_identity_id=experiment.experiment_id,
            strategy_identity_id=strategy_obj.identity_id,
            research_lineage_id="research-lineage-fixture",
            playbook_contract_identity=contract.contract_identity,
            family_claim_identity=ResearchFirewall.derive_family_claim_identity(contract),
            primary_branch_identity=primary_branch_identity,
            scope_identity=scope_identity,
            parameter_search_identity=parameter_search_identity,
            source_only_session_id=session.session_id,
            source_only_session_identity=session.session_identity,
            source_bundle_identity=session.source_bundle_identity,
            source_bundle_hash=session.source_bundle_hash,
            code_artifact_identity=make_artifact_bindings().code_artifact.identity_id,
            environment_artifact_identity=make_artifact_bindings().environment_artifact.identity_id,
            data_artifact_identity=make_artifact_bindings().data_artifact.identity_id,
            feature_artifact_identities=tuple(
                artifact.identity_id for artifact in make_artifact_bindings().feature_artifacts
            ),
            research_wave_id=wave.research_wave_id,
            statistical_profile_id=profile.profile_id,
            statistical_profile_identity=profile.profile_identity,
            multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
            protocol_version="1.0",
        )
    )


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
        with self.assertRaises(FrozenInstanceError):
            manifest.hypothesis_bindings = ()

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
        exp = make_experiment(strategy())
        # Register h-1 under wave-b, then try to lock wave-a which also claims h-1.
        firewall.register_outcome_test(
            hypothesis_test_id="h-1",
            contract=make_contract(),
            strategy=strategy(),
            experiment=exp,
            artifact_bindings=make_artifact_bindings(),
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
                contract=make_contract(),
                strategy=strategy(),
                experiment=exp,
                artifact_bindings=make_artifact_bindings(),
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
        # Two distinct families/hypotheses share one wave; each hypothesis is bound
        # to its own contract and strategy (F-06 per-hypothesis derivation).
        contracts = {
            "h-1": make_contract(family_id="family-1"),
            "h-2": make_contract(family_id="family-2"),
        }
        strategies = {hyp: make_strategy(contract) for hyp, contract in contracts.items()}
        bindings = tuple(
            WaveHypothesisBinding(
                hypothesis_test_id=hyp,
                primary_branch_identity=ResearchFirewall.derive_primary_branch_identity(contract),
                scope_identity=ResearchFirewall.derive_scope_identity(contract, strategies[hyp]),
                parameter_search_identity=ResearchFirewall.derive_parameter_search_identity(
                    "TEST_ONLY:none", strategies[hyp]
                ),
            )
            for hyp, contract in contracts.items()
        )
        wave = firewall.waves.register(
            make_wave_manifest(
                tested_hypothesis_test_ids=("h-1", "h-2"),
                bindings=bindings,
            )
        )
        for hyp in ("h-1", "h-2"):
            strategy_obj = strategies[hyp]
            exp = make_experiment(strategy_obj)
            firewall.register_outcome_test(
                hypothesis_test_id=hyp,
                contract=contracts[hyp],
                strategy=strategy_obj,
                experiment=exp,
                artifact_bindings=make_artifact_bindings(),
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
        exp = make_experiment(strategy())
        firewall.register_outcome_test(
            hypothesis_test_id="h-1",
            contract=make_contract(),
            strategy=strategy(),
            experiment=exp,
            artifact_bindings=make_artifact_bindings(),
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

    # -- E-5 PRIMARY/scope/parameter-search cross-binding regressions -----------

    def test_primary_identity_mismatch_fails_wave_lock(self):
        # E-5 test 1: PRIMARY mismatch -> wave lock fails.
        firewall = ResearchFirewall(EvidenceLedger())
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)
        wave = firewall.waves.register(make_wave_manifest(tested_hypothesis_test_ids=("h-1",)))
        register_adversarial_registration(
            firewall,
            wave,
            "h-1",
            primary_branch_identity="different-primary",
            scope_identity=SCOPE_IDENTITY,
            parameter_search_identity=PARAMETER_SEARCH_IDENTITY,
        )
        with self.assertRaisesRegex(ValueError, "PRIMARY identity"):
            firewall.lock_wave(wave.research_wave_id)
        self.assertFalse(firewall.waves.is_locked(wave.research_wave_id))

    def test_scope_identity_mismatch_fails_wave_lock(self):
        # E-5 test 2: scope mismatch -> wave lock fails.
        firewall = ResearchFirewall(EvidenceLedger())
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)
        wave = firewall.waves.register(make_wave_manifest(tested_hypothesis_test_ids=("h-1",)))
        register_adversarial_registration(
            firewall,
            wave,
            "h-1",
            scope_identity="different-scope",
        )
        with self.assertRaisesRegex(ValueError, "scope identity"):
            firewall.lock_wave(wave.research_wave_id)
        self.assertFalse(firewall.waves.is_locked(wave.research_wave_id))

    def test_parameter_search_identity_mismatch_fails_wave_lock(self):
        # E-5 test 3: parameter/search mismatch -> wave lock fails.
        firewall = ResearchFirewall(EvidenceLedger())
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)
        wave = firewall.waves.register(make_wave_manifest(tested_hypothesis_test_ids=("h-1",)))
        register_adversarial_registration(
            firewall,
            wave,
            "h-1",
            parameter_search_identity="different-search",
        )
        with self.assertRaisesRegex(ValueError, "parameter/search identity"):
            firewall.lock_wave(wave.research_wave_id)
        self.assertFalse(firewall.waves.is_locked(wave.research_wave_id))

    def test_binding_missing_a_tested_hypothesis_fails_construction(self):
        # E-5 test 4: binding set missing a tested hypothesis -> construction fails.
        bindings = (
            WaveHypothesisBinding(
                hypothesis_test_id="h-1",
                primary_branch_identity=PRIMARY_BRANCH_IDENTITY,
                scope_identity=SCOPE_IDENTITY,
                parameter_search_identity=PARAMETER_SEARCH_IDENTITY,
            ),
        )
        with self.assertRaisesRegex(ValueError, "exactly match"):
            make_wave_manifest(tested_hypothesis_test_ids=("h-1", "h-2"), bindings=bindings)

    def test_binding_extra_hypothesis_fails_construction(self):
        # E-5 test 5: manifest has an extra hypothesis binding -> construction fails.
        bindings = (
            WaveHypothesisBinding(hypothesis_test_id="h-1", primary_branch_identity="p", scope_identity="s", parameter_search_identity="q"),
            WaveHypothesisBinding(hypothesis_test_id="h-extra", primary_branch_identity="p", scope_identity="s", parameter_search_identity="q"),
        )
        with self.assertRaisesRegex(ValueError, "exactly match"):
            make_wave_manifest(tested_hypothesis_test_ids=("h-1",), bindings=bindings)

    def test_duplicate_hypothesis_binding_fails_construction(self):
        # E-5 test 6: duplicate hypothesis binding -> fails.
        bindings = (
            WaveHypothesisBinding(hypothesis_test_id="h-1", primary_branch_identity="p", scope_identity="s", parameter_search_identity="q"),
            WaveHypothesisBinding(hypothesis_test_id="h-1", primary_branch_identity="p2", scope_identity="s", parameter_search_identity="q"),
        )
        with self.assertRaisesRegex(ValueError, "unique"):
            make_wave_manifest(tested_hypothesis_test_ids=("h-1",), bindings=bindings)

    def test_exact_primary_scope_search_binding_locks(self):
        # E-5 test 7: exact PRIMARY + scope + search binding -> lock succeeds and
        # access-time binding reports PRIMARY_SCOPE_SEARCH_IDENTITIES locked.
        firewall = ResearchFirewall(EvidenceLedger())
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)
        session = make_open_session(firewall.source_only)
        wave = firewall.waves.register(make_wave_manifest(tested_hypothesis_test_ids=("h-1",)))
        exp = ExperimentIdentity.from_strategy(strategy(), TEST_ONLY_SYNTHETIC_DATA_VERSION, "exposure-fixture-v1")
        firewall.register_outcome_test(
            hypothesis_test_id="h-1",
            contract=make_contract(),
            strategy=strategy(),
            experiment=exp,
            artifact_bindings=make_artifact_bindings(),
            source_only_session_id=session.session_id,
            research_wave_id=wave.research_wave_id,
            statistical_profile_id=profile.profile_id,
            multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
        )
        firewall.lock_wave(wave.research_wave_id)
        self.assertTrue(firewall.waves.is_locked(wave.research_wave_id))
        decision = firewall.evaluate_gate(
            data_dates=(date(2024, 6, 16),),
            experiment=exp,
            hypothesis_test_id="h-1",
        )
        self.assertTrue(decision.allowed)
        control = next(c for c in decision.controls if c.name == "PRIMARY_SCOPE_SEARCH_IDENTITIES")
        self.assertTrue(control.satisfied)

    def test_adversarial_primary_mismatch_cannot_lock_nor_authorize(self):
        # E-5 test 8: malformed/adversarial direct registration with PRIMARY
        # mismatch (wave/profile/counting-unit all match) -> cannot lock, and
        # candidate outcome access is impossible.
        firewall = ResearchFirewall(EvidenceLedger())
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)
        wave = firewall.waves.register(make_wave_manifest(tested_hypothesis_test_ids=("h-1",)))
        register_adversarial_registration(
            firewall,
            wave,
            "h-1",
            primary_branch_identity="different-primary",
        )
        with self.assertRaisesRegex(ValueError, "PRIMARY identity"):
            firewall.lock_wave(wave.research_wave_id)
        exp = make_experiment(strategy())
        access = firewall.request_candidate_outcome_access(
            data_dates=(date(2024, 6, 16),),
            experiment=exp,
            hypothesis_test_id="h-1",
        )
        self.assertFalse(access.allowed)
        self.assertIn("WAVE_NOT_LOCKED", access.record.evidence_reference)


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

    def test_test_only_profile_can_lock(self):
        # A8: a TEST_ONLY profile is the only lockable profile (synthetic engine
        # fixtures only).
        registry = ResearchFirewall(EvidenceLedger()).profiles
        profile = registry.register(make_test_only_profile())
        self.assertTrue(profile.is_test_only)
        registry.lock(profile.profile_id)
        self.assertTrue(registry.is_locked(profile.profile_id))

    def test_non_test_only_profile_cannot_be_locked_nor_grant_real_access(self):
        # A9 / F-11: an arbitrary real-looking (non-TEST_ONLY) profile cannot be
        # locked, and therefore cannot produce a real candidate grant.
        real = CommonStatisticalProfile(
            profile_id="profile-real-v1",
            profile_version="1.0",
            uncertainty_precision_method="METHOD_NOT_SPECIFIED",
            evidence_sufficiency_procedure="PROCEDURE_NOT_SPECIFIED",
            dependence_handling="HANDLING_NOT_SPECIFIED",
            multiplicity_decision_rule="RULE_NOT_SPECIFIED",
            common_acceptance_procedure="PROCEDURE_NOT_SPECIFIED",
        )
        self.assertFalse(real.is_test_only)
        registry = ResearchFirewall(EvidenceLedger()).profiles
        registry.register(real)
        with self.assertRaisesRegex(ValueError, "REAL_STATISTICAL_PROFILE_NOT_ADOPTED"):
            registry.lock(real.profile_id)
        self.assertFalse(registry.is_locked(real.profile_id))

        # Even a fully-constructed wave referencing this profile cannot yield a
        # candidate outcome grant once the profile cannot be locked.
        ledger = EvidenceLedger()
        firewall = ResearchFirewall(ledger)
        real2 = CommonStatisticalProfile(
            profile_id="profile-real-v2",
            profile_version="1.0",
            uncertainty_precision_method="METHOD_NOT_SPECIFIED",
            evidence_sufficiency_procedure="PROCEDURE_NOT_SPECIFIED",
            dependence_handling="HANDLING_NOT_SPECIFIED",
            multiplicity_decision_rule="RULE_NOT_SPECIFIED",
            common_acceptance_procedure="PROCEDURE_NOT_SPECIFIED",
        )
        firewall.profiles.register(real2)
        with self.assertRaisesRegex(ValueError, "REAL_STATISTICAL_PROFILE_NOT_ADOPTED"):
            firewall.profiles.lock(real2.profile_id)
        session = make_open_session(firewall.source_only)
        wave = firewall.waves.register(
            make_wave_manifest(
                wave_id="wave-real",
                profile_id=real2.profile_id,
                profile_identity=real2.profile_identity,
                tested_hypothesis_test_ids=("h-real",),
            )
        )
        exp = make_experiment(strategy())
        firewall.register_outcome_test(
            hypothesis_test_id="h-real",
            contract=make_contract(),
            strategy=strategy(),
            experiment=exp,
            artifact_bindings=make_artifact_bindings(),
            source_only_session_id=session.session_id,
            research_wave_id=wave.research_wave_id,
            statistical_profile_id=real2.profile_id,
            multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
        )
        firewall.lock_wave(wave.research_wave_id)
        access = firewall.request_candidate_outcome_access(
            data_dates=(date(2024, 6, 16),),
            experiment=exp,
            hypothesis_test_id="h-real",
        )
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "IDENTITY_BINDING:PROFILE_NOT_LOCKED")

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

    def _grant(self, *, data_dates=(date(2024, 6, 16),), hypothesis_test_id=HYPOTHESIS_TEST_ID, experiment=None):
        return self.firewall.request_candidate_outcome_access(
            data_dates=data_dates,
            experiment=experiment if experiment is not None else self.experiment,
            hypothesis_test_id=hypothesis_test_id,
        )

    # 1. unrelated locked wave cannot authorize an experiment outside its test set
    def test_unrelated_locked_wave_cannot_authorize_other_experiment(self):
        firewall2, _, _, _, experiment2 = make_registered_firewall(
            EvidenceLedger(),
            hypothesis_test_id="h-other",
            session_id="source-only-session-2",
            wave_id="wave-2",
            family="family-other",
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
            family="family-other",
        )
        self.assertTrue(firewall2.source_only.is_verified(session2.session_id))
        # session-2's verified status cannot authorize the other lineage's
        # experiment on this firewall's hypothesis.
        access = self._grant(hypothesis_test_id=HYPOTHESIS_TEST_ID, experiment=experiment2)
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "IDENTITY_BINDING:EXPERIMENT_IDENTITY_MISMATCH")

    # 4. authoritative API has no caller-controlled lock booleans and no
    # caller-supplied cohort (F-04)
    def test_no_caller_controlled_lock_booleans(self):
        access_params = set(inspect.signature(self.firewall.request_candidate_outcome_access).parameters)
        for forbidden in (
            "multiplicity_counting_unit_locked",
            "primary_scope_search_identities_locked",
            "wave_id",
            "profile_id",
            "source_only_session_id",
            "cohort",
        ):
            self.assertNotIn(forbidden, access_params)
        self.assertIn("data_dates", access_params)
        gate_params = set(inspect.signature(self.firewall.evaluate_gate).parameters)
        self.assertNotIn("multiplicity_counting_unit_locked", gate_params)
        self.assertNotIn("primary_scope_search_identities_locked", gate_params)
        self.assertNotIn("cohort", gate_params)
        self.assertIn("data_dates", gate_params)

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
                playbook_contract_identity=make_contract().contract_identity,
                family_claim_identity=ResearchFirewall.derive_family_claim_identity(make_contract()),
                primary_branch_identity="primary-1",
                scope_identity="scope-1",
                parameter_search_identity="param-1",
                source_only_session_id=session.session_id,
                source_only_session_identity=session.session_identity,
                source_bundle_identity=session.source_bundle_identity,
                source_bundle_hash=session.source_bundle_hash,
                code_artifact_identity=make_artifact_bindings().code_artifact.identity_id,
                environment_artifact_identity=make_artifact_bindings().environment_artifact.identity_id,
                data_artifact_identity=make_artifact_bindings().data_artifact.identity_id,
                feature_artifact_identities=tuple(
                    artifact.identity_id for artifact in make_artifact_bindings().feature_artifacts
                ),
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
            data_dates=(date(2024, 6, 16),),
            experiment=self.experiment,
            hypothesis_test_id=HYPOTHESIS_TEST_ID,
        )
        self.assertTrue(decision.allowed)
        self.assertEqual(decision.reason, "SYNTHETIC_DEVELOPMENT_OUTCOME_ONLY")
        self.assertTrue(decision.synthetic_only)

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

    # 13. VALIDATION remains DENIED (derived from actual input dates)
    def test_validation_remains_denied(self):
        access = self._grant(data_dates=(date(2025, 1, 15),))
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "VALIDATION_DEFAULT_DENY_NO_VALIDATION_AUTHORITY")

    # A5: a 2025 validation date cannot be claimed as DEVELOPMENT even on a fully
    # locked synthetic DEVELOPMENT wave; the cohort is derived from the actual
    # date and DENIED.
    def test_validation_date_cannot_be_claimed_as_development(self):
        access = self._grant(data_dates=(date(2025, 1, 15),))
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "VALIDATION_DEFAULT_DENY_NO_VALIDATION_AUTHORITY")

    # A6: one confirmatory request spanning DEVELOPMENT + VALIDATION dates must
    # fail closed.
    def test_mixed_cohort_dates_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "multiple research cohorts"):
            self.firewall.request_candidate_outcome_access(
                data_dates=(date(2024, 6, 16), date(2025, 1, 15)),
                experiment=self.experiment,
                hypothesis_test_id=HYPOTHESIS_TEST_ID,
            )

    # A11: the authoritative candidate API no longer accepts a caller-supplied
    # synthetic_fixture boolean (synthetic status is derived from the governed
    # data version only).
    def test_candidate_api_has_no_caller_synthetic_boolean(self):
        access_params = set(inspect.signature(self.firewall.request_candidate_outcome_access).parameters)
        self.assertNotIn("synthetic_fixture", access_params)
        gate_params = set(inspect.signature(self.firewall.evaluate_gate).parameters)
        self.assertNotIn("synthetic_fixture", gate_params)

    # A13: a full legal TEST_ONLY fixture whose experiment data_version equals the
    # governed TEST_ONLY_SYNTHETIC_DATA_VERSION yields PRE_OUTCOME_GATE_GRANTED.
    def test_governed_synthetic_data_version_grants(self):
        self.assertEqual(self.experiment.data_version, TEST_ONLY_SYNTHETIC_DATA_VERSION)
        access = self._grant()
        self.assertTrue(access.allowed)
        self.assertEqual(access.record.event_type, "PRE_OUTCOME_GATE_GRANTED")
        self.assertEqual(access.record.outcome, "GRANTED")

    # A14: a TEST_ONLY profile with an ordinary (non-governed) data version is
    # DENIED even when every other gate control is satisfied.
    def test_test_only_profile_with_ordinary_data_version_is_denied(self):
        ledger = EvidenceLedger()
        firewall = ResearchFirewall(ledger)
        session = make_open_session(firewall.source_only)
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)
        wave = firewall.waves.register(make_wave_manifest(tested_hypothesis_test_ids=("h-real-data",)))
        strategy_obj = strategy()
        exp = ExperimentIdentity.from_strategy(strategy_obj, "real-development-data-v1", "exposure-fixture-v1")
        firewall.register_outcome_test(
            hypothesis_test_id="h-real-data",
            contract=make_contract(),
            strategy=strategy_obj,
            experiment=exp,
            artifact_bindings=make_artifact_bindings(data_declared_version="real-development-data-v1"),
            source_only_session_id=session.session_id,
            research_wave_id=wave.research_wave_id,
            statistical_profile_id=profile.profile_id,
            multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
        )
        firewall.lock_wave(wave.research_wave_id)
        access = firewall.request_candidate_outcome_access(
            data_dates=(date(2024, 6, 16),),
            experiment=exp,
            hypothesis_test_id="h-real-data",
        )
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "TEST_ONLY_PROFILE_REQUIRES_SYNTHETIC_FIXTURE")

    # A15: a near-match data-version string is not recognized as the governed
    # synthetic data version (exact equality only) -> DENY.
    def test_near_match_synthetic_version_is_not_recognized(self):
        ledger = EvidenceLedger()
        firewall = ResearchFirewall(ledger)
        session = make_open_session(firewall.source_only)
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)
        wave = firewall.waves.register(make_wave_manifest(tested_hypothesis_test_ids=("h-fake-syn",)))
        strategy_obj = strategy()
        exp = ExperimentIdentity.from_strategy(strategy_obj, "TEST_ONLY_SYNTHETIC_DATA_V1_FAKE", "exposure-fixture-v1")
        firewall.register_outcome_test(
            hypothesis_test_id="h-fake-syn",
            contract=make_contract(),
            strategy=strategy_obj,
            experiment=exp,
            artifact_bindings=make_artifact_bindings(data_declared_version="TEST_ONLY_SYNTHETIC_DATA_V1_FAKE"),
            source_only_session_id=session.session_id,
            research_wave_id=wave.research_wave_id,
            statistical_profile_id=profile.profile_id,
            multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
        )
        firewall.lock_wave(wave.research_wave_id)
        access = firewall.request_candidate_outcome_access(
            data_dates=(date(2024, 6, 16),),
            experiment=exp,
            hypothesis_test_id="h-fake-syn",
        )
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "TEST_ONLY_PROFILE_REQUIRES_SYNTHETIC_FIXTURE")

    # 14. historical final remains DENIED
    def test_historical_final_remains_denied(self):
        access = self._grant(data_dates=(date(2025, 7, 1),))
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "FINAL_HISTORICAL_HOLDOUT_ALWAYS_LOCKED")

    # 15. Shadow/Forward remains DENIED
    def test_shadow_forward_remains_denied(self):
        access = self._grant(data_dates=(date(2026, 1, 2),))
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "SHADOW_FORWARD_NOT_AUTHORIZED")

    # extra: default firewall denies any candidate outcome access
    def test_default_firewall_denies_candidate_outcome_access(self):
        firewall = ResearchFirewall(EvidenceLedger())
        experiment = ExperimentIdentity.from_strategy(strategy(), "data-fixture-v1", "exposure-fixture-v1")
        access = firewall.request_candidate_outcome_access(
            data_dates=(date(2024, 6, 16),),
            experiment=experiment,
            hypothesis_test_id="never-registered",
        )
        self.assertFalse(access.allowed)
        self.assertEqual(access.record.evidence_reference, "IDENTITY_BINDING:UNREGISTERED_HYPOTHESIS_TEST")

    # extra: an unverified session cannot register nor authorize (F-07)
    def test_unverified_session_cannot_register_nor_authorize(self):
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
        contract = make_contract()
        strategy_obj = make_strategy(contract)
        exp = make_experiment(strategy_obj)
        with self.assertRaisesRegex(ValueError, "must be verified"):
            firewall.register_outcome_test(
                hypothesis_test_id="h-1",
                contract=contract,
                strategy=strategy_obj,
                experiment=exp,
                artifact_bindings=make_artifact_bindings(),
                source_only_session_id="manual-session",
                research_wave_id=wave.research_wave_id,
                statistical_profile_id=profile.profile_id,
                multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
            )

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
            data_dates=(date(2024, 6, 16),),
            experiment=experiment,
            hypothesis_test_id="never-registered",
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


def build_package_b_context(
    ledger,
    *,
    session_id="source-only-session-1",
    contract=None,
    strategy_obj=None,
    wave_id="wave-test-only-v1",
    bindings=None,
    hypothesis_test_ids=(HYPOTHESIS_TEST_ID,),
    profile_id="profile-test-only-v1",
):
    """Build a full artifact-bound firewall/context for Package B adversarial
    tests, allowing a caller-supplied contract/strategy/binding to be exercised
    against the validating register_outcome_test factory."""
    if contract is None:
        contract = make_contract(source_only_session_identity=synthetic_session_identity(session_id))
    if strategy_obj is None:
        strategy_obj = make_strategy(contract)
    experiment = make_experiment(strategy_obj)
    firewall = ResearchFirewall(ledger)
    session = make_open_session(firewall.source_only, session_id=session_id)
    profile = firewall.profiles.register(make_test_only_profile(profile_id=profile_id))
    firewall.profiles.lock(profile.profile_id)
    wave = firewall.waves.register(
        make_wave_manifest(
            wave_id=wave_id,
            contract=contract,
            strategy=strategy_obj,
            profile_id=profile.profile_id,
            profile_identity=profile.profile_identity,
            tested_hypothesis_test_ids=hypothesis_test_ids,
            bindings=bindings,
        )
    )
    return firewall, session, profile, wave, experiment, contract, strategy_obj


def register_package_b(
    firewall,
    *,
    hypothesis_test_id,
    contract,
    strategy_obj,
    experiment,
    wave,
    profile,
    session,
    artifact_bindings=None,
):
    return firewall.register_outcome_test(
        hypothesis_test_id=hypothesis_test_id,
        contract=contract,
        strategy=strategy_obj,
        experiment=experiment,
        artifact_bindings=artifact_bindings or make_artifact_bindings(),
        source_only_session_id=session.session_id,
        research_wave_id=wave.research_wave_id,
        statistical_profile_id=profile.profile_id,
        multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
    )


class PackageBArtifactLineageGovernanceTests(unittest.TestCase):
    """Package B regression suite (B01..B30).

    All fixtures synthetic. No canonical candidate data. The portfolio
    confirmatory path stays closed (PORTFOLIO_CANDIDATE_OUTCOME_ACCESS_NOT_IMPLEMENTED).
    """

    def setUp(self):
        self.ledger = EvidenceLedger()

    def _make_context(self, **kwargs):
        return build_package_b_context(self.ledger, **kwargs)

    # -- B01..B03: caller PRIMARY/scope/search identity authority is removed. ----

    def test_b01_bogus_primary_rejected_at_registration(self):
        contract = make_contract()
        strategy_obj = make_strategy(contract)
        bogus = WaveHypothesisBinding(
            hypothesis_test_id=HYPOTHESIS_TEST_ID,
            primary_branch_identity="bogus-primary-identity",
            scope_identity=ResearchFirewall.derive_scope_identity(contract, strategy_obj),
            parameter_search_identity=ResearchFirewall.derive_parameter_search_identity(
                "TEST_ONLY:none", strategy_obj
            ),
        )
        firewall, session, profile, wave, experiment, _, _ = self._make_context(bindings=(bogus,))
        with self.assertRaisesRegex(ValueError, "primary identity does not match"):
            register_package_b(
                firewall,
                hypothesis_test_id=HYPOTHESIS_TEST_ID,
                contract=contract,
                strategy_obj=strategy_obj,
                experiment=experiment,
                wave=wave,
                profile=profile,
                session=session,
            )

    def test_b02_bogus_scope_rejected_at_registration(self):
        contract = make_contract()
        strategy_obj = make_strategy(contract)
        bogus = WaveHypothesisBinding(
            hypothesis_test_id=HYPOTHESIS_TEST_ID,
            primary_branch_identity=ResearchFirewall.derive_primary_branch_identity(contract),
            scope_identity="bogus-scope-identity",
            parameter_search_identity=ResearchFirewall.derive_parameter_search_identity(
                "TEST_ONLY:none", strategy_obj
            ),
        )
        firewall, session, profile, wave, experiment, _, _ = self._make_context(bindings=(bogus,))
        with self.assertRaisesRegex(ValueError, "scope identity does not match"):
            register_package_b(
                firewall,
                hypothesis_test_id=HYPOTHESIS_TEST_ID,
                contract=contract,
                strategy_obj=strategy_obj,
                experiment=experiment,
                wave=wave,
                profile=profile,
                session=session,
            )

    def test_b03_bogus_parameter_search_rejected_at_registration(self):
        contract = make_contract()
        strategy_obj = make_strategy(contract)
        bogus = WaveHypothesisBinding(
            hypothesis_test_id=HYPOTHESIS_TEST_ID,
            primary_branch_identity=ResearchFirewall.derive_primary_branch_identity(contract),
            scope_identity=ResearchFirewall.derive_scope_identity(contract, strategy_obj),
            parameter_search_identity="bogus-parameter-search-identity",
        )
        firewall, session, profile, wave, experiment, _, _ = self._make_context(bindings=(bogus,))
        with self.assertRaisesRegex(ValueError, "parameter/search identity does not match"):
            register_package_b(
                firewall,
                hypothesis_test_id=HYPOTHESIS_TEST_ID,
                contract=contract,
                strategy_obj=strategy_obj,
                experiment=experiment,
                wave=wave,
                profile=profile,
                session=session,
            )

    # -- B04: a SOURCE_ONLY session from a different bundle cannot authorize. ----

    def test_b04_session_from_different_bundle_cannot_authorize(self):
        firewall = ResearchFirewall(self.ledger)
        session = firewall.source_only.open_verified_session(
            session_id="source-only-session-1",
            model_identity="model-fixture-v1",
            prompt_spec_version="prompt-spec-v1",
            source_bundle_identity="other-bundle",
            source_bundle_hash="other-hash",
            tool_retrieval_mode="PROJECT_SOURCE_ONLY",
        )
        contract = make_contract(source_only_session_identity=session.session_identity)
        strategy_obj = make_strategy(contract)
        experiment = make_experiment(strategy_obj)
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)
        wave = firewall.waves.register(
            make_wave_manifest(
                contract=contract,
                strategy=strategy_obj,
                profile_id=profile.profile_id,
                profile_identity=profile.profile_identity,
            )
        )
        self.assertTrue(firewall.source_only.is_verified(session.session_id))
        with self.assertRaisesRegex(ValueError, "source bundle identity does not match"):
            register_package_b(
                firewall,
                hypothesis_test_id=HYPOTHESIS_TEST_ID,
                contract=contract,
                strategy_obj=strategy_obj,
                experiment=experiment,
                wave=wave,
                profile=profile,
                session=session,
            )

    # -- B05/B06: strategy must be explicitly bound to the PlaybookContract. -----

    def test_b05_strategy_without_playbook_contract_identity_rejected(self):
        contract = make_contract()
        strategy_obj = make_strategy(contract, playbook_contract_identity=None)
        experiment = make_experiment(strategy_obj)
        firewall, session, profile, wave, _, _, _ = self._make_context(
            contract=contract, strategy_obj=strategy_obj
        )
        self.assertIsNone(strategy_obj.playbook_contract_identity)
        with self.assertRaisesRegex(ValueError, "not bound to this playbook contract"):
            register_package_b(
                firewall,
                hypothesis_test_id=HYPOTHESIS_TEST_ID,
                contract=contract,
                strategy_obj=strategy_obj,
                experiment=experiment,
                wave=wave,
                profile=profile,
                session=session,
            )

    def test_b06_strategy_bound_to_other_contract_rejected(self):
        contract_a = make_contract(contract_id="pb-contract-a")
        contract_b = make_contract(contract_id="pb-contract-b")
        strategy_a = make_strategy(contract_a)
        experiment_a = make_experiment(strategy_a)
        firewall, session, profile, wave, _, _, _ = self._make_context(
            contract=contract_a, strategy_obj=strategy_a
        )
        with self.assertRaisesRegex(ValueError, "not bound to this playbook contract"):
            register_package_b(
                firewall,
                hypothesis_test_id=HYPOTHESIS_TEST_ID,
                contract=contract_b,
                strategy_obj=strategy_a,
                experiment=experiment_a,
                wave=wave,
                profile=profile,
                session=session,
            )

    # -- B07: renaming family while reusing family-claim evidence cannot reset lineage. --

    def test_b07_family_rename_cannot_reset_lineage(self):
        firewall = ResearchFirewall(self.ledger)
        session = make_open_session(firewall.source_only)
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)
        contract_1 = make_contract(
            contract_id="pb-c1", family_id="family-a", research_lineage_id="lineage-a"
        )
        strategy_1 = make_strategy(contract_1)
        experiment_1 = make_experiment(strategy_1)
        contract_2 = make_contract(
            contract_id="pb-c2", family_id="family-b", research_lineage_id="lineage-b"
        )
        strategy_2 = make_strategy(contract_2)
        experiment_2 = make_experiment(strategy_2)
        bindings = (
            WaveHypothesisBinding(
                hypothesis_test_id="h-1",
                primary_branch_identity=ResearchFirewall.derive_primary_branch_identity(contract_1),
                scope_identity=ResearchFirewall.derive_scope_identity(contract_1, strategy_1),
                parameter_search_identity=ResearchFirewall.derive_parameter_search_identity(
                    "TEST_ONLY:none", strategy_1
                ),
            ),
            WaveHypothesisBinding(
                hypothesis_test_id="h-2",
                primary_branch_identity=ResearchFirewall.derive_primary_branch_identity(contract_2),
                scope_identity=ResearchFirewall.derive_scope_identity(contract_2, strategy_2),
                parameter_search_identity=ResearchFirewall.derive_parameter_search_identity(
                    "TEST_ONLY:none", strategy_2
                ),
            ),
        )
        wave = firewall.waves.register(
            make_wave_manifest(
                wave_id="wave-b7",
                tested_hypothesis_test_ids=("h-1", "h-2"),
                bindings=bindings,
                profile_id=profile.profile_id,
                profile_identity=profile.profile_identity,
            )
        )
        # Same derived family-claim evidence (identical source claims), first
        # registration binds lineage-a.
        self.assertEqual(
            ResearchFirewall.derive_family_claim_identity(contract_1),
            ResearchFirewall.derive_family_claim_identity(contract_2),
        )
        register_package_b(
            firewall,
            hypothesis_test_id="h-1",
            contract=contract_1,
            strategy_obj=strategy_1,
            experiment=experiment_1,
            wave=wave,
            profile=profile,
            session=session,
        )
        # A renamed family + new lineage reusing the same family-claim evidence
        # cannot reset lineage (F-08).
        with self.assertRaisesRegex(ValueError, "already bound to a different research lineage"):
            register_package_b(
                firewall,
                hypothesis_test_id="h-2",
                contract=contract_2,
                strategy_obj=strategy_2,
                experiment=experiment_2,
                wave=wave,
                profile=profile,
                session=session,
            )

    # -- B10..B13: actual artifact binding mismatches prevent registration. ------

    def test_b10_code_artifact_mismatch_rejected(self):
        firewall, session, profile, wave, experiment, contract, strategy_obj = self._make_context()
        tampered_code = ArtifactBinding.from_bytes(
            artifact_kind="code",
            artifact_reference="synthetic-strategy-v1",
            content=b"tampered strategy code bytes",
            declared_version="code-v1",
        )
        bindings = OutcomeArtifactBindings(
            code_artifact=tampered_code,
            environment_artifact=make_environment_artifact(),
            data_artifact=make_data_artifact(),
            feature_artifacts=(make_feature_artifact(),),
        )
        with self.assertRaisesRegex(ValueError, "code artifact sha256 does not match"):
            register_package_b(
                firewall,
                hypothesis_test_id=HYPOTHESIS_TEST_ID,
                contract=contract,
                strategy_obj=strategy_obj,
                experiment=experiment,
                wave=wave,
                profile=profile,
                session=session,
                artifact_bindings=bindings,
            )

    def test_b11_environment_artifact_mismatch_rejected(self):
        firewall, session, profile, wave, experiment, contract, strategy_obj = self._make_context()
        tampered_env = ArtifactBinding.from_bytes(
            artifact_kind="environment",
            artifact_reference="synthetic-environment-v1",
            content=b"tampered environment bytes",
            declared_version="env-v1",
        )
        bindings = OutcomeArtifactBindings(
            code_artifact=make_code_artifact(),
            environment_artifact=tampered_env,
            data_artifact=make_data_artifact(),
            feature_artifacts=(make_feature_artifact(),),
        )
        with self.assertRaisesRegex(ValueError, "environment artifact sha256 does not match"):
            register_package_b(
                firewall,
                hypothesis_test_id=HYPOTHESIS_TEST_ID,
                contract=contract,
                strategy_obj=strategy_obj,
                experiment=experiment,
                wave=wave,
                profile=profile,
                session=session,
                artifact_bindings=bindings,
            )

    def test_b12_data_declared_version_mismatch_rejected(self):
        firewall, session, profile, wave, experiment, contract, strategy_obj = self._make_context()
        bindings = make_artifact_bindings(data_declared_version="wrong-data-version-v1")
        with self.assertRaisesRegex(ValueError, "data artifact declared version does not match"):
            register_package_b(
                firewall,
                hypothesis_test_id=HYPOTHESIS_TEST_ID,
                contract=contract,
                strategy_obj=strategy_obj,
                experiment=experiment,
                wave=wave,
                profile=profile,
                session=session,
                artifact_bindings=bindings,
            )

    def test_b13_feature_coverage_missing_or_extra_rejected(self):
        firewall, session, profile, wave, experiment, contract, strategy_obj = self._make_context()
        missing = OutcomeArtifactBindings(
            code_artifact=make_code_artifact(),
            environment_artifact=make_environment_artifact(),
            data_artifact=make_data_artifact(),
            feature_artifacts=(),
        )
        with self.assertRaisesRegex(ValueError, "feature artifact versions do not exactly cover"):
            register_package_b(
                firewall,
                hypothesis_test_id=HYPOTHESIS_TEST_ID,
                contract=contract,
                strategy_obj=strategy_obj,
                experiment=experiment,
                wave=wave,
                profile=profile,
                session=session,
                artifact_bindings=missing,
            )
        extra_artifact = ArtifactBinding.from_bytes(
            artifact_kind="feature",
            artifact_reference="synthetic-feature-v1",
            content=b"synthetic extra feature bytes",
            declared_version="feature-extra",
        )
        extra = OutcomeArtifactBindings(
            code_artifact=make_code_artifact(),
            environment_artifact=make_environment_artifact(),
            data_artifact=make_data_artifact(),
            # feature versions must be sorted+unique; order ("feature-extra", "feature-v1")
            feature_artifacts=(extra_artifact, make_feature_artifact()),
        )
        with self.assertRaisesRegex(ValueError, "feature artifact versions do not exactly cover"):
            register_package_b(
                firewall,
                hypothesis_test_id=HYPOTHESIS_TEST_ID,
                contract=contract,
                strategy_obj=strategy_obj,
                experiment=experiment,
                wave=wave,
                profile=profile,
                session=session,
                artifact_bindings=extra,
            )

    # -- B14..B16: SOURCE_ONLY verification is project-issued (F-10). ------------

    def test_b14_old_fixed_nonce_token_does_not_verify(self):
        policy = ResearchFirewall(EvidenceLedger()).source_only
        # Reconstruct the OLD pre-F-10 deterministic issuer nonce formula.
        old_issuer_nonce = _canonical_hash(("SOURCE_ONLY_PROJECT_ISSUER_V1",))
        old_session_identity = synthetic_session_identity("old-nonce")
        manual = SourceOnlySession(
            session_id="old-nonce",
            model_identity="model-fixture-v1",
            prompt_spec_version="prompt-spec-v1",
            source_bundle_identity="bundle-fixture-v1",
            source_bundle_hash="bundle-hash-fixture-v1",
            tool_retrieval_mode="PROJECT_SOURCE_ONLY",
            protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
            verification_evidence=_canonical_hash((old_issuer_nonce, old_session_identity)),
        )
        policy.record_session(manual)
        self.assertFalse(policy.is_verified("old-nonce"))

    def test_b15_record_session_cannot_promote_to_verified(self):
        policy = ResearchFirewall(EvidenceLedger()).source_only
        issued = policy.open_verified_session(
            session_id="real-issued",
            model_identity="model-fixture-v1",
            prompt_spec_version="prompt-spec-v1",
            source_bundle_identity="bundle-fixture-v1",
            source_bundle_hash="bundle-hash-fixture-v1",
            tool_retrieval_mode="PROJECT_SOURCE_ONLY",
        )
        self.assertTrue(policy.is_verified("real-issued"))
        # A compatibility session that copies the issued token verbatim must not
        # become verified through record_session.
        copied = SourceOnlySession(
            session_id="copy-issued-token",
            model_identity="model-fixture-v1",
            prompt_spec_version="prompt-spec-v1",
            source_bundle_identity="bundle-fixture-v1",
            source_bundle_hash="bundle-hash-fixture-v1",
            tool_retrieval_mode="PROJECT_SOURCE_ONLY",
            protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
            verification_evidence=issued.verification_evidence,
        )
        policy.record_session(copied)
        self.assertFalse(policy.is_verified("copy-issued-token"))

    def test_b16_open_verified_session_is_verified(self):
        policy = ResearchFirewall(EvidenceLedger()).source_only
        session = make_open_session(policy, session_id="b16-session")
        self.assertTrue(policy.is_verified("b16-session"))
        self.assertIn("b16-session", policy.issued_verified_session_ids)

    # -- B17..B24: durable restart reconstruction (F-09). ------------------------

    def _roundtrip(self, firewall):
        handle = tempfile.NamedTemporaryFile(delete=False, suffix=".json", prefix="pkg-b-state-")
        path = handle.name
        handle.close()
        try:
            firewall.save_state(path)
            return ResearchFirewall.load_state(path)
        finally:
            if os.path.exists(path):
                os.remove(path)

    def test_b17_restart_preserves_verified_session(self):
        firewall, session, _, _, _ = make_registered_firewall(self.ledger)
        loaded = self._roundtrip(firewall)
        self.assertTrue(loaded.source_only.is_verified(session.session_id))
        self.assertEqual(
            loaded.source_only.get(session.session_id).session_identity,
            session.session_identity,
        )

    def test_b18_restart_keeps_manual_session_unverified(self):
        firewall = ResearchFirewall(self.ledger)
        firewall.source_only.record_session(
            SourceOnlySession(
                session_id="manual-session",
                model_identity="model-fixture-v1",
                prompt_spec_version="prompt-spec-v1",
                source_bundle_identity="bundle-fixture-v1",
                source_bundle_hash="bundle-hash-fixture-v1",
                tool_retrieval_mode="PROJECT_SOURCE_ONLY",
                protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
            )
        )
        loaded = self._roundtrip(firewall)
        self.assertFalse(loaded.source_only.is_verified("manual-session"))

    def test_b19_restart_preserves_wave_lock(self):
        firewall, _, _, wave, _ = make_registered_firewall(self.ledger)
        self.assertTrue(firewall.waves.is_locked(wave.research_wave_id))
        loaded = self._roundtrip(firewall)
        self.assertTrue(loaded.waves.is_locked(wave.research_wave_id))
        self.assertIn(wave.research_wave_id, loaded.waves.locked_wave_ids)

    def test_b20_restart_preserves_first_look_and_terminal_outcome(self):
        firewall, _, _, wave, experiment = make_registered_firewall(self.ledger)
        access = firewall.request_candidate_outcome_access(
            data_dates=(date(2024, 6, 16),),
            experiment=experiment,
            hypothesis_test_id=HYPOTHESIS_TEST_ID,
        )
        self.assertTrue(access.allowed)
        self.assertTrue(firewall.waves.has_outcome_test_started(wave.research_wave_id))
        firewall.waves.record_terminal_outcome(wave.research_wave_id, HYPOTHESIS_TEST_ID, "FAIL")
        loaded = self._roundtrip(firewall)
        self.assertTrue(loaded.waves.has_outcome_test_started(wave.research_wave_id))
        self.assertEqual(
            loaded.waves.outcome_records(wave.research_wave_id),
            ((HYPOTHESIS_TEST_ID, "FAIL"),),
        )

    def test_b21_restart_preserves_profile_lock(self):
        firewall, _, profile, _, _ = make_registered_firewall(self.ledger)
        self.assertTrue(firewall.profiles.is_locked(profile.profile_id))
        loaded = self._roundtrip(firewall)
        self.assertTrue(loaded.profiles.is_locked(profile.profile_id))

    def test_b22_restart_preserves_evidence_exposure(self):
        firewall, _, _, _, experiment = make_registered_firewall(self.ledger)
        firewall.request_candidate_outcome_access(
            data_dates=(date(2024, 6, 16),),
            experiment=experiment,
            hypothesis_test_id=HYPOTHESIS_TEST_ID,
        )
        original_records = self.ledger.records
        self.assertTrue(original_records)
        loaded = self._roundtrip(firewall)
        self.assertEqual(len(loaded._ledger.records), len(original_records))
        self.assertEqual(loaded._ledger.records, original_records)
        self.assertIn(
            DatasetClass.DEVELOPMENT,
            loaded._ledger.exposures_for(experiment.research_lineage_id),
        )

    def test_b23_restart_preserves_final_holdout_exposed_terminal(self):
        firewall, _, _, _, _ = make_registered_firewall(self.ledger)
        firewall.final_state.register_unlock_authority("owner-gate-1")
        firewall.final_state.expose("owner-gate-1")
        firewall.final_state.conclude(FinalHoldoutState.FINAL_VOID_IMPLEMENTATION_DEFECT)
        loaded = self._roundtrip(firewall)
        self.assertEqual(loaded.final_state.state, FinalHoldoutState.FINAL_VOID_IMPLEMENTATION_DEFECT)
        # Terminal conclusion: no longer locked, never restores holdout status.
        self.assertFalse(loaded.final_state.is_locked)
        self.assertFalse(loaded.final_state.is_exposed)
        self.assertEqual(loaded.final_state.unlock_authority, "owner-gate-1")

    def test_b24_unknown_state_schema_fails_closed(self):
        firewall, _, _, _, _ = make_registered_firewall(self.ledger)
        data = firewall.to_state_dict()
        self.assertEqual(data["state_schema_version"], ResearchFirewall.STATE_SCHEMA_VERSION)
        data["state_schema_version"] = "v999-unknown"
        with self.assertRaisesRegex(ValueError, "unknown state schema version"):
            ResearchFirewall.from_state_dict(data)

    # -- B25..B27: F-12 alternatives must exactly equal the tested denominator. --

    def _wave_with_alternatives(self, declared):
        firewall = ResearchFirewall(self.ledger)
        manifest = replace(
            make_wave_manifest(tested_hypothesis_test_ids=(HYPOTHESIS_TEST_ID,)),
            declared_outcome_tested_alternatives=declared,
        )
        wave = firewall.waves.register(manifest)
        return firewall, wave

    def test_b25_alternatives_missing_fails_wave_lock(self):
        firewall, wave = self._wave_with_alternatives(())
        with self.assertRaisesRegex(ValueError, "exactly equal the tested hypothesis set"):
            firewall.lock_wave(wave.research_wave_id)
        self.assertFalse(firewall.waves.is_locked(wave.research_wave_id))

    def test_b26_alternatives_extra_fails_wave_lock(self):
        firewall, wave = self._wave_with_alternatives(("h-undeclared", HYPOTHESIS_TEST_ID))
        with self.assertRaisesRegex(ValueError, "exactly equal the tested hypothesis set"):
            firewall.lock_wave(wave.research_wave_id)
        self.assertFalse(firewall.waves.is_locked(wave.research_wave_id))

    def test_b27_alternatives_exact_locks(self):
        firewall, session, _, wave, _ = make_registered_firewall(self.ledger)
        self.assertTrue(firewall.waves.is_locked(wave.research_wave_id))
        self.assertEqual(
            wave.declared_outcome_tested_alternatives,
            tuple(sorted(wave.tested_hypothesis_test_ids)),
        )
        self.assertIn(wave.research_wave_id, firewall.waves.locked_wave_ids)
        self.assertEqual(session.session_id, SYNTHETIC_SESSION_ID)

    # -- B29: repeated identical grant/deny is idempotent on the ledger. ---------

    def test_b29_repeated_grant_and_deny_do_not_inflate_ledger(self):
        firewall, _, _, _, experiment = make_registered_firewall(self.ledger)
        grant_1 = firewall.request_candidate_outcome_access(
            data_dates=(date(2024, 6, 16),),
            experiment=experiment,
            hypothesis_test_id=HYPOTHESIS_TEST_ID,
        )
        grant_2 = firewall.request_candidate_outcome_access(
            data_dates=(date(2024, 6, 16),),
            experiment=experiment,
            hypothesis_test_id=HYPOTHESIS_TEST_ID,
        )
        self.assertTrue(grant_1.allowed)
        self.assertTrue(grant_2.allowed)
        granted = [r for r in self.ledger.records if r.event_type == "PRE_OUTCOME_GATE_GRANTED"]
        self.assertEqual(len(granted), 1)
        deny_1 = firewall.request_candidate_outcome_access(
            data_dates=(date(2025, 1, 15),),
            experiment=experiment,
            hypothesis_test_id=HYPOTHESIS_TEST_ID,
        )
        deny_2 = firewall.request_candidate_outcome_access(
            data_dates=(date(2025, 1, 15),),
            experiment=experiment,
            hypothesis_test_id=HYPOTHESIS_TEST_ID,
        )
        self.assertFalse(deny_1.allowed)
        self.assertFalse(deny_2.allowed)
        denied = [r for r in self.ledger.records if r.event_type == "PRE_OUTCOME_GATE_DENIED"]
        self.assertEqual(len(denied), 1)

    # -- B30: current Package A invariants remain green. -------------------------

    def test_b30_package_a_protections_intact(self):
        firewall, _, _, _, experiment = make_registered_firewall(self.ledger)
        # caller cohort/synthetic booleans absent from the authoritative API
        access_params = set(inspect.signature(firewall.request_candidate_outcome_access).parameters)
        self.assertNotIn("synthetic_fixture", access_params)
        self.assertNotIn("cohort", access_params)
        # VALIDATION denied
        validation = firewall.request_candidate_outcome_access(
            data_dates=(date(2025, 1, 15),),
            experiment=experiment,
            hypothesis_test_id=HYPOTHESIS_TEST_ID,
        )
        self.assertFalse(validation.allowed)
        # non-TEST_ONLY profile cannot be locked
        real = CommonStatisticalProfile(
            profile_id="profile-real-b30",
            profile_version="1.0",
            uncertainty_precision_method="METHOD_NOT_SPECIFIED",
            evidence_sufficiency_procedure="PROCEDURE_NOT_SPECIFIED",
            dependence_handling="HANDLING_NOT_SPECIFIED",
            multiplicity_decision_rule="RULE_NOT_SPECIFIED",
            common_acceptance_procedure="PROCEDURE_NOT_SPECIFIED",
        )
        registry = ResearchFirewall(EvidenceLedger()).profiles
        registry.register(real)
        with self.assertRaisesRegex(ValueError, "REAL_STATISTICAL_PROFILE_NOT_ADOPTED"):
            registry.lock(real.profile_id)
        # portfolio confirmatory path remains closed (no outcome retrieval surface)
        self.assertFalse(hasattr(firewall, "portfolio"))
        self.assertFalse(hasattr(firewall, "candidate_outcomes"))


if __name__ == "__main__":
    unittest.main()

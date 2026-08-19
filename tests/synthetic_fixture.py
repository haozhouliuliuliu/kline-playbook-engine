"""Shared minimal legal synthetic CONFIRMATORY fixture for engine-sanity tests.

TEST_ONLY / synthetic only. This fixture never reads the canonical market corpus
and cannot produce real candidate-quality conclusions. It is the ONLY way a
CONFIRMATORY engine-sanity test may pass the pre-outcome gate after Package A
(F-01/F-03/F-04/F-05/F-11):

- DEVELOPMENT trading days (frozen 12/6/6: 2024-01-01..2024-12-31);
- ONE shared ``ResearchFirewall`` instance between the firewall and the runner;
- a verified SOURCE_ONLY session on a project SOURCE_ONLY path;
- a registered + locked TEST_ONLY ``CommonStatisticalProfile``;
- a registered + locked RESEARCH_WAVE;
- an identity-bound ``OutcomeTestRegistration``;
- ``ValidationInput.data_version_id == ExperimentIdentity.data_version``;
- the actual input dates derive to DEVELOPMENT via ``classify_cohort``.
"""

from datetime import date

from src.research_firewall import (
    CommonStatisticalProfile,
    ResearchFirewall,
    ResearchWaveManifest,
    TEST_ONLY_SYNTHETIC_DATA_VERSION,
    WaveHypothesisBinding,
)
from src.strategy_evidence import (
    EvidenceLedger,
    ExperimentIdentity,
    LifecycleState,
    StrategyIdentity,
    TypedParameter,
)
from src.validation_runner import ValidationInput

SYNTHETIC_EXPOSURE_REFERENCE = "exposure-fixture-v1"
SYNTHETIC_HYPOTHESIS_TEST_ID = "hypothesis-test-v1"
SYNTHETIC_SESSION_ID = "source-only-session-1"
SYNTHETIC_WAVE_ID = "wave-test-only-v1"

# A frozen DEVELOPMENT-cohort trading day (2024-01-01..2024-12-31).
DEVELOPMENT_DAY = date(2024, 6, 17)


def make_strategy(**overrides):
    """Build a deterministic synthetic StrategyIdentity with keyword overrides."""
    fields = {
        "research_lineage_id": "research-lineage-fixture",
        "family_id": "neutral-family",
        "strategy_version": "1.0",
        "source": "deterministic-fixture",
        "applicable_instruments": ("TEST",),
        "timeframe": "5m",
        "parameters": (TypedParameter("window", "int", 3),),
        "code_hash": "code-fixture-v1",
        "environment_hash": "environment-fixture-v1",
        "required_feature_versions": ("context-fixture-v1",),
        "lifecycle_state": LifecycleState.DRAFT,
        "data_exposure_history_reference": SYNTHETIC_EXPOSURE_REFERENCE,
    }
    fields.update(overrides)
    return StrategyIdentity(**fields)


def make_experiment(
    strategy: StrategyIdentity,
    *,
    data_version: str = TEST_ONLY_SYNTHETIC_DATA_VERSION,
    dataset_exposure_reference: str = SYNTHETIC_EXPOSURE_REFERENCE,
) -> ExperimentIdentity:
    return ExperimentIdentity.from_strategy(strategy, data_version, dataset_exposure_reference)


def make_test_only_profile(profile_id: str = "profile-test-only-v1") -> CommonStatisticalProfile:
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


def build_synthetic_firewall(
    ledger: EvidenceLedger,
    strategy: StrategyIdentity,
    experiment: ExperimentIdentity,
    *,
    hypothesis_test_id: str = SYNTHETIC_HYPOTHESIS_TEST_ID,
    session_id: str = SYNTHETIC_SESSION_ID,
    wave_id: str = SYNTHETIC_WAVE_ID,
    family_claim_identity: str = "family-claim-fixture-v1",
) -> tuple[ResearchFirewall, str]:
    """Build ONE identity-bound TEST_ONLY DEVELOPMENT firewall with a locked wave.

    The experiment is registered as the single tested hypothesis. The returned
    ``ResearchFirewall`` instance MUST be shared with the runner (F-03).
    """
    firewall = ResearchFirewall(ledger)
    session = firewall.source_only.open_verified_session(
        session_id=session_id,
        model_identity="model-fixture-v1",
        prompt_spec_version="prompt-spec-v1",
        source_bundle_identity="bundle-fixture-v1",
        source_bundle_hash="bundle-hash-fixture-v1",
        tool_retrieval_mode="PROJECT_SOURCE_ONLY",
        researcher_model_exposure_note="synthetic fixture only; no canonical corpus access",
    )
    profile = firewall.profiles.register(make_test_only_profile())
    firewall.profiles.lock(profile.profile_id)
    binding = WaveHypothesisBinding(
        hypothesis_test_id=hypothesis_test_id,
        primary_branch_identity="primary-branch-fixture-v1",
        scope_identity="scope-fixture-v1",
        parameter_search_identity="parameter-search-fixture-v1",
    )
    wave = firewall.waves.register(
        ResearchWaveManifest(
            research_wave_id=wave_id,
            protocol_version="1.0",
            statistical_profile_id=profile.profile_id,
            statistical_profile_identity=profile.profile_identity,
            multiplicity_counting_unit_identity="counting-unit-test-v1",
            tested_hypothesis_test_ids=(hypothesis_test_id,),
            hypothesis_bindings=(binding,),
            declared_outcome_tested_alternatives=(),
            instrument_timeframe_context_scope="TEST_ONLY:instrument=TEST;timeframe=5m;context=TEST",
            parameter_search_ranges="TEST_ONLY:none",
            denominator_counting_semantics="TEST_ONLY:independent-falsifiable-hypotheses",
            created_at="2026-08-19T00:00:00Z",
        )
    )
    firewall.register_outcome_test(
        hypothesis_test_id=hypothesis_test_id,
        strategy=strategy,
        experiment=experiment,
        family_claim_identity=family_claim_identity,
        primary_branch_identity=binding.primary_branch_identity,
        scope_identity=binding.scope_identity,
        parameter_search_identity=binding.parameter_search_identity,
        source_only_session_id=session.session_id,
        research_wave_id=wave.research_wave_id,
        statistical_profile_id=profile.profile_id,
        multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
    )
    firewall.lock_wave(wave.research_wave_id)
    return firewall, hypothesis_test_id


def make_validation_input(
    request_id: str,
    bar,
    decision_at,
    data_version: str = TEST_ONLY_SYNTHETIC_DATA_VERSION,
) -> ValidationInput:
    """Build a ValidationInput bound to the experiment data version (F-05)."""
    return ValidationInput(request_id, bar, decision_at, data_version)

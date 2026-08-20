"""Shared minimal legal synthetic CONFIRMATORY fixture for engine-sanity tests.

TEST_ONLY / synthetic only. This fixture never reads the canonical market corpus
and cannot produce real candidate-quality conclusions. It is the ONLY way a
CONFIRMATORY engine-sanity test may pass the pre-outcome gate after Package A
and Package B:

- DEVELOPMENT trading days (frozen 12/6/6: 2024-01-01..2024-12-31);
- ONE shared ``ResearchFirewall`` instance between the firewall and the runner;
- a verified SOURCE_ONLY session bound to the synthetic source bundle;
- a machine-ready ``PlaybookContract`` with exactly one PRIMARY branch;
- a ``StrategyIdentity`` explicitly bound to that contract
  (``playbook_contract_identity``);
- real byte-derived artifact bindings (code/environment/data/feature) whose
  hashes feed ``code_hash``/``environment_hash`` and whose declared versions
  cover the experiment/feature versions;
- a registered + locked TEST_ONLY ``CommonStatisticalProfile``;
- a registered + locked RESEARCH_WAVE whose PRIMARY/scope/search binding values
  are derived from the actual artifacts (F-06);
- ``ValidationInput.data_version_id == ExperimentIdentity.data_version``;
- the actual input dates derive to DEVELOPMENT via ``classify_cohort``.
"""

from datetime import date

from src.playbook_contract import (
    AmbiguityStatus,
    ClaimStatus,
    InterpretationBranch,
    MachineOperationalization,
    ObservationSurface,
    ObservabilityStatus,
    PlaybookContract,
    SourceClaimRef,
    TransferStatus,
    parameter_identity,
)
from src.research_firewall import (
    ApprovedSourceBundle,
    ApprovedSourceMaterialRef,
    ByteBindingStatus,
    CommonStatisticalProfile,
    ProtectedMarketAccessMode,
    ResearchFirewall,
    ResearchWaveManifest,
    SourceOnlySession,
    TEST_ONLY_SYNTHETIC_DATA_VERSION,
    WaveHypothesisBinding,
)
from src.strategy_evidence import (
    ArtifactBinding,
    EvidenceLedger,
    ExperimentIdentity,
    LifecycleState,
    OutcomeArtifactBindings,
    StrategyIdentity,
    TypedParameter,
)
from src.validation_runner import ValidationInput

SYNTHETIC_EXPOSURE_REFERENCE = "exposure-fixture-v1"
SYNTHETIC_HYPOTHESIS_TEST_ID = "hypothesis-test-v1"
SYNTHETIC_SESSION_ID = "source-only-session-1"
SYNTHETIC_WAVE_ID = "wave-test-only-v1"
SYNTHETIC_SOURCE_BUNDLE_ID = "bundle-fixture-v1"
SYNTHETIC_SOURCE_BUNDLE_HASH = "bundle-hash-fixture-v1"
# Actual source identity (Claim Schema v1.0 source_id) and approved material
# identity used by the synthetic approved source bundle. The bundle id is a
# distinct value so tests can prove bundle-id-as-source-id no longer passes.
SYNTHETIC_SOURCE_ID = "source-fixture-v1"
SYNTHETIC_MATERIAL_ID = "material-fixture-v1"
SYNTHETIC_MATERIAL_ANCHOR = "fixture:book:edition-1:chapter-1"
SYNTHETIC_LINEAGE = "research-lineage-fixture"
SYNTHETIC_FAMILY = "neutral-family"
SYNTHETIC_PARAMETER = TypedParameter("window", "int", 3)
SYNTHETIC_PARAMETER_IDENTITY = parameter_identity(SYNTHETIC_PARAMETER)

# A frozen DEVELOPMENT-cohort trading day (2024-01-01..2024-12-31).
DEVELOPMENT_DAY = date(2024, 6, 17)

# Real synthetic artifact bytes: the artifact sha256 is derived from these bytes.
SYNTHETIC_CODE_BYTES = b"synthetic strategy fixture v1"
SYNTHETIC_ENVIRONMENT_BYTES = b"synthetic environment fixture v1"
SYNTHETIC_DATA_BYTES = b"synthetic data fixture v1"
SYNTHETIC_FEATURE_BYTES = b"synthetic feature fixture v1"


def make_code_artifact() -> ArtifactBinding:
    return ArtifactBinding.from_bytes(
        artifact_kind="code",
        artifact_reference="synthetic-strategy-v1",
        content=SYNTHETIC_CODE_BYTES,
        declared_version="code-v1",
    )


def make_environment_artifact() -> ArtifactBinding:
    return ArtifactBinding.from_bytes(
        artifact_kind="environment",
        artifact_reference="synthetic-environment-v1",
        content=SYNTHETIC_ENVIRONMENT_BYTES,
        declared_version="env-v1",
    )


def make_data_artifact(declared_version: str = TEST_ONLY_SYNTHETIC_DATA_VERSION) -> ArtifactBinding:
    return ArtifactBinding.from_bytes(
        artifact_kind="data",
        artifact_reference="synthetic-data-v1",
        content=SYNTHETIC_DATA_BYTES,
        declared_version=declared_version,
    )


def make_feature_artifact() -> ArtifactBinding:
    return ArtifactBinding.from_bytes(
        artifact_kind="feature",
        artifact_reference="synthetic-feature-v1",
        content=SYNTHETIC_FEATURE_BYTES,
        declared_version="feature-v1",
    )


def make_artifact_bindings(
    data_declared_version: str = TEST_ONLY_SYNTHETIC_DATA_VERSION,
) -> OutcomeArtifactBindings:
    return OutcomeArtifactBindings(
        code_artifact=make_code_artifact(),
        environment_artifact=make_environment_artifact(),
        data_artifact=make_data_artifact(declared_version=data_declared_version),
        feature_artifacts=(make_feature_artifact(),),
    )


def synthetic_session_identity(session_id: str = SYNTHETIC_SESSION_ID) -> str:
    """Deterministic session identity of the standard synthetic SOURCE_ONLY session.

    The session binds the material-derived session binding identity/hash of the
    standard synthetic approved bundle (F-C01), not the legacy bundle id/hash.
    """
    session = SourceOnlySession(
        session_id=session_id,
        model_identity="model-fixture-v1",
        prompt_spec_version="prompt-spec-v1",
        source_bundle_identity=SYNTHETIC_SESSION_BINDING_IDENTITY,
        source_bundle_hash=SYNTHETIC_SESSION_BINDING_HASH,
        tool_retrieval_mode="PROJECT_SOURCE_ONLY",
        protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
        researcher_model_exposure_note="no known exposure",
    )
    return session.session_identity


def make_open_session(policy, *, session_id: str = SYNTHETIC_SESSION_ID) -> SourceOnlySession:
    """Open the standard verified synthetic SOURCE_ONLY session on ``policy``,
    bound to the material-derived session binding identity/hash (F-C01)."""
    return policy.open_verified_session(
        session_id=session_id,
        model_identity="model-fixture-v1",
        prompt_spec_version="prompt-spec-v1",
        source_bundle_identity=SYNTHETIC_SESSION_BINDING_IDENTITY,
        source_bundle_hash=SYNTHETIC_SESSION_BINDING_HASH,
        tool_retrieval_mode="PROJECT_SOURCE_ONLY",
        researcher_model_exposure_note="no known exposure",
    )


def make_approved_material_ref(
    *,
    source_id: str = SYNTHETIC_SOURCE_ID,
    material_id: str = SYNTHETIC_MATERIAL_ID,
    source_anchor_reference: str = SYNTHETIC_MATERIAL_ANCHOR,
    exact_bytes: bytes | None = None,
) -> ApprovedSourceMaterialRef:
    """Synthetic approved source material ref.

    By default historical-unbound (NOT_RECORDED), matching the historical
    evidence posture; pass ``exact_bytes`` to create an exact-byte-bound ref.
    """
    if exact_bytes is None:
        return ApprovedSourceMaterialRef.historical_unbound(
            source_id=source_id,
            material_id=material_id,
            source_anchor_reference=source_anchor_reference,
        )
    return ApprovedSourceMaterialRef.from_bytes(
        source_id=source_id,
        material_id=material_id,
        source_anchor_reference=source_anchor_reference,
        content=exact_bytes,
    )


def make_approved_bundle(
    *,
    source_bundle_id: str = SYNTHETIC_SOURCE_BUNDLE_ID,
    source_bundle_hash: str = SYNTHETIC_SOURCE_BUNDLE_HASH,
    source_anchor_reference: str = SYNTHETIC_MATERIAL_ANCHOR,
    materials: tuple[ApprovedSourceMaterialRef, ...] | None = None,
    content_note: str | None = None,
) -> ApprovedSourceBundle:
    """Synthetic approved source bundle bound to the standard synthetic session."""
    if materials is None:
        materials = (make_approved_material_ref(),)
    return ApprovedSourceBundle(
        source_bundle_id=source_bundle_id,
        source_bundle_hash=source_bundle_hash,
        source_anchor_reference=source_anchor_reference,
        materials=materials,
        content_note=content_note,
    )


# Deterministic material-derived session binding facts of the standard synthetic
# approved bundle. Future SOURCE_ONLY sessions must bind to these, not to the
# legacy recorded bundle id/hash (F-C01).
_SYNTHETIC_APPROVED_BUNDLE = make_approved_bundle()
SYNTHETIC_SESSION_BINDING_IDENTITY = _SYNTHETIC_APPROVED_BUNDLE.session_binding_identity
SYNTHETIC_SESSION_BINDING_HASH = _SYNTHETIC_APPROVED_BUNDLE.session_binding_hash


def make_contract(**overrides) -> PlaybookContract:
    """Build a machine-ready synthetic PlaybookContract bound to the standard
    synthetic source bundle and SOURCE_ONLY session identity."""
    base = dict(
        schema_version="0.1",
        contract_version="0.1.0",
        contract_id="pb-synthetic-fixture-001",
        research_lineage_id=SYNTHETIC_LINEAGE,
        family_id=SYNTHETIC_FAMILY,
        source_claims=(
            SourceClaimRef(
                claim_id="c1",
                source_id=SYNTHETIC_SOURCE_BUNDLE_ID,
                source_anchor="fixture:book:p1",
                claim_status=ClaimStatus.EXPLICIT,
            ),
        ),
        source_bundle_identity=SYNTHETIC_SESSION_BINDING_IDENTITY,
        source_bundle_hash=SYNTHETIC_SESSION_BINDING_HASH,
        source_only_session_identity=synthetic_session_identity(),
        source_scope="deterministic-synthetic-fixture",
        interpretations=(
            InterpretationBranch(
                branch_id="b1",
                source_claim_ids=("c1",),
                source_basis="synthetic price shape",
                transfer_status=TransferStatus.EXPLICIT,
                primary_selected=True,
            ),
        ),
        ambiguity_status=AmbiguityStatus.NONE,
        ambiguity_notes=None,
        primary_required=True,
        source_variant_count=1,
        observation_surfaces=(
            ObservationSurface(
                surface_id="price",
                required=True,
                observability_status=ObservabilityStatus.OBSERVABLE_NOW,
            ),
        ),
        unavailable_inputs=(),
        instrument_scope=("TEST",),
        timeframe_scope=("5m",),
        project_transfer_status=TransferStatus.EXPLICIT,
        machine=MachineOperationalization(
            operationalization_reference="op-ref-v1",
            code_hash=make_code_artifact().sha256,
            environment_hash=make_environment_artifact().sha256,
            required_feature_versions=("feature-v1",),
            parameter_identities=(SYNTHETIC_PARAMETER_IDENTITY,),
        ),
        data_exposure_history_reference=SYNTHETIC_EXPOSURE_REFERENCE,
        parent_contract_id=None,
        created_at="2026-08-19T00:00:00Z",
    )
    base.update(overrides)
    return PlaybookContract(**base)


def _contract_for_facts(
    *,
    lineage: str = SYNTHETIC_LINEAGE,
    family: str = SYNTHETIC_FAMILY,
    source: str | None = None,
    instruments: tuple[str, ...] | None = None,
    timeframe: str | None = None,
    exposure: str | None = None,
    code_hash: str | None = None,
    environment_hash: str | None = None,
    feature_versions: tuple[str, ...] | None = None,
    parameters: tuple[TypedParameter, ...] | None = None,
) -> PlaybookContract:
    """Build a synthetic machine-ready contract consistent with the given
    bridge-relevant strategy facts, so a StrategyIdentity built from those facts
    is genuinely equivalent to a bridge output for this contract (Package C
    C-C03)."""
    return make_contract(
        research_lineage_id=lineage,
        family_id=family,
        source_scope=source if source is not None else "deterministic-synthetic-fixture",
        instrument_scope=(
            tuple(sorted(set(instruments))) if instruments is not None else ("TEST",)
        ),
        timeframe_scope=(timeframe,) if timeframe is not None else ("5m",),
        data_exposure_history_reference=(
            exposure if exposure is not None else SYNTHETIC_EXPOSURE_REFERENCE
        ),
        machine=MachineOperationalization(
            operationalization_reference="op-ref-v1",
            code_hash=code_hash if code_hash is not None else make_code_artifact().sha256,
            environment_hash=(
                environment_hash
                if environment_hash is not None
                else make_environment_artifact().sha256
            ),
            required_feature_versions=(
                tuple(sorted(set(feature_versions)))
                if feature_versions is not None
                else ("feature-v1",)
            ),
            parameter_identities=(
                tuple(sorted({parameter_identity(p) for p in parameters}))
                if parameters is not None
                else (SYNTHETIC_PARAMETER_IDENTITY,)
            ),
        ),
    )


def make_strategy(contract: PlaybookContract | None = None, **overrides) -> StrategyIdentity:
    """Build a synthetic StrategyIdentity explicitly bound to ``contract``.

    The produced strategy is exactly equivalent to a ``bridge_to_strategy_identity``
    output for its contract: it uses the deterministic bridge version string
    ``pc-{contract_version}-{contract_identity}``, the contract machine hashes,
    and canonical scope facts, and ``playbook_contract_identity`` is the contract
    identity, so the strategy can be artifact-bound at registration. When
    ``contract`` is omitted, a consistent contract is built from the
    bridge-relevant overrides (lineage/family/source/instruments/timeframe/
    exposure/machine facts) so a strategy with custom facts is bound to a
    matching contract (Package C C-C03).
    """
    if contract is None:
        lineage = overrides.pop("research_lineage_id", SYNTHETIC_LINEAGE)
        family = overrides.pop("family_id", SYNTHETIC_FAMILY)
        contract = _contract_for_facts(
            lineage=lineage,
            family=family,
            source=overrides.get("source"),
            instruments=overrides.get("applicable_instruments"),
            timeframe=overrides.get("timeframe"),
            exposure=overrides.get("data_exposure_history_reference"),
            code_hash=overrides.get("code_hash"),
            environment_hash=overrides.get("environment_hash"),
            feature_versions=overrides.get("required_feature_versions"),
            parameters=overrides.get("parameters"),
        )
    fields = {
        "research_lineage_id": contract.research_lineage_id,
        "family_id": contract.family_id,
        "strategy_version": f"pc-{contract.contract_version}-{contract.contract_identity}",
        "source": contract.source_scope or contract.family_id,
        "applicable_instruments": tuple(sorted(set(contract.instrument_scope))),
        "timeframe": contract.timeframe_scope[0],
        "parameters": (SYNTHETIC_PARAMETER,),
        "code_hash": contract.machine.code_hash,
        "environment_hash": contract.machine.environment_hash,
        "required_feature_versions": tuple(sorted(set(contract.machine.required_feature_versions))),
        "lifecycle_state": LifecycleState.DRAFT,
        "data_exposure_history_reference": contract.data_exposure_history_reference,
        "playbook_contract_identity": contract.contract_identity,
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


def make_wave_manifest(
    *,
    wave_id: str = SYNTHETIC_WAVE_ID,
    contract: PlaybookContract | None = None,
    strategy: StrategyIdentity | None = None,
    profile_id: str = "profile-test-only-v1",
    profile_identity: str | None = None,
    counting_unit_identity: str = "counting-unit-test-v1",
    tested_hypothesis_test_ids: tuple[str, ...] = (SYNTHETIC_HYPOTHESIS_TEST_ID,),
    bindings: tuple[WaveHypothesisBinding, ...] | None = None,
    parameter_search_ranges: str = "TEST_ONLY:none",
    created_at: str = "2026-08-19T00:00:00Z",
) -> ResearchWaveManifest:
    """Build a wave manifest whose binding values are DERIVED from the actual
    contract + strategy artifacts (F-06). Pass explicit ``bindings`` to simulate a
    bogus/manual binding (must fail registration)."""
    if profile_identity is None:
        profile_identity = make_test_only_profile(profile_id=profile_id).profile_identity
    if contract is None:
        contract = make_contract()
    if strategy is None:
        strategy = make_strategy(contract)
    if bindings is None:
        primary_identity = ResearchFirewall.derive_primary_branch_identity(contract)
        scope_identity = ResearchFirewall.derive_scope_identity(contract, strategy)
        search_identity = ResearchFirewall.derive_parameter_search_identity(
            parameter_search_ranges, strategy
        )
        bindings = tuple(
            WaveHypothesisBinding(
                hypothesis_test_id=hypothesis_test_id,
                primary_branch_identity=primary_identity,
                scope_identity=scope_identity,
                parameter_search_identity=search_identity,
            )
            for hypothesis_test_id in tested_hypothesis_test_ids
        )
    return ResearchWaveManifest(
        research_wave_id=wave_id,
        protocol_version="1.0",
        statistical_profile_id=profile_id,
        statistical_profile_identity=profile_identity,
        multiplicity_counting_unit_identity=counting_unit_identity,
        tested_hypothesis_test_ids=tested_hypothesis_test_ids,
        hypothesis_bindings=bindings,
        declared_outcome_tested_alternatives=tuple(sorted(tested_hypothesis_test_ids)),
        instrument_timeframe_context_scope="TEST_ONLY:instrument=TEST;timeframe=5m;context=TEST",
        parameter_search_ranges=parameter_search_ranges,
        denominator_counting_semantics="TEST_ONLY:independent-falsifiable-hypotheses",
        created_at=created_at,
    )


def build_synthetic_firewall(
    ledger: EvidenceLedger,
    strategy: StrategyIdentity,
    experiment: ExperimentIdentity,
    *,
    contract: PlaybookContract | None = None,
    hypothesis_test_id: str = SYNTHETIC_HYPOTHESIS_TEST_ID,
    session_id: str = SYNTHETIC_SESSION_ID,
    wave_id: str = SYNTHETIC_WAVE_ID,
    artifact_bindings: OutcomeArtifactBindings | None = None,
) -> tuple[ResearchFirewall, str]:
    """Build ONE identity-bound TEST_ONLY DEVELOPMENT firewall with a locked wave.

    Registers the contract + artifact-bound outcome test and locks the wave. The
    returned ``ResearchFirewall`` instance MUST be shared with the runner (F-03).
    """
    firewall = ResearchFirewall(ledger)
    session = make_open_session(firewall.source_only, session_id=session_id)
    if contract is None:
        # Rebuild the exact contract this strategy is bound to from its actual
        # bridge facts (Package C C-C03), so registration sees a contract the
        # strategy is genuinely equivalent to.
        contract = _contract_for_facts(
            lineage=strategy.research_lineage_id,
            family=strategy.family_id,
            source=strategy.source,
            instruments=strategy.applicable_instruments,
            timeframe=strategy.timeframe,
            exposure=strategy.data_exposure_history_reference,
            code_hash=strategy.code_hash,
            environment_hash=strategy.environment_hash,
            feature_versions=strategy.required_feature_versions,
            parameters=strategy.parameters,
        )
    profile = firewall.profiles.register(make_test_only_profile())
    firewall.profiles.lock(profile.profile_id)
    wave = firewall.waves.register(
        make_wave_manifest(
            wave_id=wave_id,
            contract=contract,
            strategy=strategy,
            profile_id=profile.profile_id,
            profile_identity=profile.profile_identity,
            tested_hypothesis_test_ids=(hypothesis_test_id,),
        )
    )
    firewall.register_outcome_test(
        hypothesis_test_id=hypothesis_test_id,
        contract=contract,
        strategy=strategy,
        experiment=experiment,
        artifact_bindings=artifact_bindings or make_artifact_bindings(),
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

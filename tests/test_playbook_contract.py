"""Deterministic regression tests for the generic Playbook Contract core.

Lane B of the 2026-08-19 parallel work package. Covers:

- deterministic canonical contract identity independent of collection ordering;
- immutable version identity (frozen dataclass, stable identity);
- SOURCE CLAIM != PROJECT INTERPRETATION != MACHINE OPERATIONALIZATION separation;
- fail-closed validation:
  - missing source provenance;
  - missing interpretation provenance / unresolvable source basis;
  - unresolved critical ambiguity;
  - non-observable required input / unavailable inputs;
  - silently collapsed source-permitted variants;
  - missing or duplicated PRIMARY;
  - missing machine identities / missing machine operationalization;
  - missing instrument/timeframe scope;
  - an INFERRED transfer mislabeled EXPLICIT;
- StrategyIdentity bridge:
  - preserves lineage / version / parameters / features;
  - changing contract semantic content changes identity;
  - rejects drafts and mismatched machine inputs;
  - duplicate family/version mutation rejected by the existing StrategyCatalog;
  - the module cannot authorize ResearchFirewall outcome access.

All fixtures are synthetic and generic (no candidate-specific family).
"""

import inspect
import unittest
from dataclasses import FrozenInstanceError, replace

from src.playbook_contract import (
    AmbiguityStatus,
    ClaimStatus,
    ContractValidationResult,
    InterpretationBranch,
    MachineOperationalization,
    MachineReadiness,
    ObservationSurface,
    ObservabilityStatus,
    PlaybookContract,
    SourceClaimRef,
    TransferStatus,
    bridge_to_strategy_identity,
    canonical_hash,
    parameter_identity,
    validate_contract,
)
from src.strategy_evidence import (
    LifecycleState,
    StrategyCatalog,
    StrategyIdentity,
    TypedParameter,
)


def source_claim(
    claim_id="c1",
    source_id="s1",
    anchor="book:edition-1:p12",
    status=ClaimStatus.EXPLICIT,
):
    return SourceClaimRef(
        claim_id=claim_id,
        source_id=source_id,
        source_anchor=anchor,
        claim_status=status,
    )


def observation_surface(
    surface_id="price",
    required=True,
    obs=ObservabilityStatus.OBSERVABLE_NOW,
    missing=(),
):
    return ObservationSurface(
        surface_id=surface_id,
        required=required,
        observability_status=obs,
        missing_inputs=missing,
    )


def interpretation(
    branch_id="b1",
    source_claim_ids=("c1",),
    basis="source describes price shape",
    transfer=TransferStatus.EXPLICIT,
    primary=True,
    variant=None,
):
    return InterpretationBranch(
        branch_id=branch_id,
        source_claim_ids=source_claim_ids,
        source_basis=basis,
        transfer_status=transfer,
        primary_selected=primary,
        variant_label=variant,
    )


def machine(
    operationalization_reference="op-ref-v1",
    code_hash="code-hash-v1",
    environment_hash="env-hash-v1",
    required_feature_versions=("feature-v1",),
    parameter_identities=("pid-1",),
):
    return MachineOperationalization(
        operationalization_reference=operationalization_reference,
        code_hash=code_hash,
        environment_hash=environment_hash,
        required_feature_versions=required_feature_versions,
        parameter_identities=parameter_identities,
    )


def contract(**overrides):
    base = dict(
        schema_version="0.1",
        contract_version="0.1.0",
        contract_id="pb-generic-fixture-001",
        research_lineage_id="research-lineage-fixture",
        family_id="fixture-family",
        source_claims=(source_claim(),),
        source_bundle_identity="bundle-id-v1",
        source_bundle_hash="bundle-hash-v1",
        source_only_session_identity="session-id-v1",
        source_scope="deterministic-fixture",
        interpretations=(interpretation(),),
        ambiguity_status=AmbiguityStatus.NONE,
        ambiguity_notes=None,
        primary_required=True,
        source_variant_count=1,
        observation_surfaces=(observation_surface(),),
        unavailable_inputs=(),
        instrument_scope=("cu",),
        timeframe_scope=("5m",),
        project_transfer_status=TransferStatus.EXPLICIT,
        machine=machine(),
        data_exposure_history_reference="exposure-fixture-v1",
        parent_contract_id=None,
        created_at="2026-08-19T00:00:00Z",
    )
    base.update(overrides)
    return PlaybookContract(**base)


def ready_machine_params():
    """(parameters, machine) pair whose parameter identities agree."""
    params = (TypedParameter("window", "int", 3),)
    machine_ids = tuple(parameter_identity(p) for p in params)
    return params, machine_ids


def bridge_kwargs(parameters, code_hash="code-hash-v1"):
    return dict(
        parameters=parameters,
        code_hash=code_hash,
        environment_hash="env-hash-v1",
        required_feature_versions=("feature-v1",),
        data_exposure_history_reference="exposure-fixture-v1",
    )


class PlaybookContractIdentityTests(unittest.TestCase):
    def test_identical_inputs_have_stable_canonical_identity(self):
        self.assertEqual(contract().contract_identity, contract().contract_identity)
        self.assertTrue(contract().contract_identity)
        self.assertTrue(contract().contract_identity.isalnum())

    def test_identity_is_independent_of_collection_input_ordering(self):
        claims = (source_claim("c1"), source_claim("c2", source_id="s2"))
        branches = (
            interpretation("b1", ("c1",)),
            interpretation("b2", ("c2",), transfer=TransferStatus.INFERRED, primary=False),
        )
        surfaces = (
            observation_surface("price"),
            observation_surface("volume", required=False),
        )
        ordered = contract(
            source_claims=claims,
            interpretations=branches,
            observation_surfaces=surfaces,
        )
        reversed_input = contract(
            source_claims=tuple(reversed(claims)),
            interpretations=tuple(reversed(branches)),
            observation_surfaces=tuple(reversed(surfaces)),
        )
        self.assertEqual(ordered.contract_identity, reversed_input.contract_identity)

    def test_contract_is_immutable_and_identity_is_stable(self):
        instance = contract()
        again = contract()
        self.assertEqual(instance.contract_identity, again.contract_identity)
        with self.assertRaises(FrozenInstanceError):
            instance.family_id = "changed"  # type: ignore[misc]

    def test_changing_semantic_content_changes_identity(self):
        base = contract()
        different_interpretation = contract(
            interpretations=(interpretation(basis="source describes a different shape"),)
        )
        different_machine = contract(machine=machine(parameter_identities=("pid-2",)))
        different_claim = contract(source_claims=(source_claim(anchor="video:ts-00:42"),))
        self.assertNotEqual(base.contract_identity, different_interpretation.contract_identity)
        self.assertNotEqual(base.contract_identity, different_machine.contract_identity)
        self.assertNotEqual(base.contract_identity, different_claim.contract_identity)


class PlaybookContractLayerSeparationTests(unittest.TestCase):
    def test_source_interpretation_machine_layers_are_separate(self):
        instance = contract()
        self.assertIsNotNone(instance.source_claims)
        self.assertIsNotNone(instance.interpretations)
        self.assertIsNotNone(instance.machine)
        # Each layer has its own identity and they are mutually distinct.
        self.assertNotEqual(
            instance.source_claims[0].claim_identity,
            instance.interpretations[0].branch_identity,
        )
        self.assertNotEqual(
            instance.interpretations[0].branch_identity,
            instance.machine.machine_identity,
        )
        self.assertNotEqual(
            instance.source_claims[0].claim_identity,
            instance.machine.machine_identity,
        )
        # The contract identity composes all three layers.
        self.assertEqual(
            instance.contract_identity,
            canonical_hash(
                {
                    "schema_version": instance.schema_version,
                    "contract_version": instance.contract_version,
                    "contract_id": instance.contract_id,
                    "research_lineage_id": instance.research_lineage_id,
                    "family_id": instance.family_id,
                    "parent_contract_id": instance.parent_contract_id,
                    "source_claims": tuple(
                        sorted(c.claim_identity for c in instance.source_claims)
                    ),
                    "source_bundle_identity": instance.source_bundle_identity,
                    "source_bundle_hash": instance.source_bundle_hash,
                    "source_only_session_identity": instance.source_only_session_identity,
                    "source_scope": instance.source_scope,
                    "interpretations": tuple(
                        sorted(b.branch_identity for b in instance.interpretations)
                    ),
                    "ambiguity_status": instance.ambiguity_status.value,
                    "ambiguity_notes": instance.ambiguity_notes,
                    "primary_required": instance.primary_required,
                    "source_variant_count": instance.source_variant_count,
                    "observation_surfaces": tuple(
                        sorted(s.surface_identity for s in instance.observation_surfaces)
                    ),
                    "unavailable_inputs": instance.unavailable_inputs,
                    "instrument_scope": instance.instrument_scope,
                    "timeframe_scope": instance.timeframe_scope,
                    "project_transfer_status": instance.project_transfer_status.value,
                    "machine": instance.machine.machine_identity,
                    "data_exposure_history_reference": instance.data_exposure_history_reference,
                    "created_at": instance.created_at,
                }
            ),
        )


class PlaybookContractFailClosedValidationTests(unittest.TestCase):
    def assert_not_ready(self, instance, *expected_blockers):
        result = validate_contract(instance)
        self.assertIsInstance(result, ContractValidationResult)
        self.assertEqual(result.readiness, MachineReadiness.NOT_MACHINE_READY)
        self.assertFalse(result.ready)
        for blocker in expected_blockers:
            self.assertIn(blocker, result.blockers)
        return result

    def test_complete_generic_contract_is_machine_ready(self):
        result = validate_contract(contract())
        self.assertEqual(result.readiness, MachineReadiness.MACHINE_READY)
        self.assertTrue(result.ready)
        self.assertEqual(result.blockers, ())
        self.assertEqual(contract().machine_readiness(), result)

    def test_missing_source_provenance_fails_closed(self):
        self.assert_not_ready(contract(source_claims=()), "SOURCE_REFERENCES_MISSING")
        self.assert_not_ready(
            contract(source_bundle_identity=""),
            "SOURCE_REFERENCES_MISSING",
        )
        self.assert_not_ready(
            contract(source_only_session_identity=""),
            "SOURCE_REFERENCES_MISSING",
        )

    def test_missing_interpretation_provenance_fails_closed(self):
        self.assert_not_ready(
            contract(interpretations=()),
            "INTERPRETATION_PROVENANCE_MISSING",
        )
        self.assert_not_ready(
            contract(interpretations=(interpretation(basis=""),)),
            "INTERPRETATION_PROVENANCE_MISSING",
        )
        self.assert_not_ready(
            contract(interpretations=(interpretation(source_claim_ids=("unknown-claim",)),)),
            "INTERPRETATION_REFERENCES_UNKNOWN_SOURCE_CLAIM",
        )

    def test_unresolved_critical_ambiguity_blocks_machine_readiness(self):
        self.assert_not_ready(
            contract(ambiguity_status=AmbiguityStatus.UNRESOLVED_CRITICAL),
            "UNRESOLVED_CRITICAL_AMBIGUITY",
        )
        resolved = contract(
            ambiguity_status=AmbiguityStatus.RESOLVED,
            ambiguity_notes="source example resolved the choice",
        )
        self.assertTrue(validate_contract(resolved).ready)

    def test_unavailable_required_input_blocks_readiness(self):
        self.assert_not_ready(
            contract(
                observation_surfaces=(
                    observation_surface(
                        obs=ObservabilityStatus.NOT_OBSERVABLE_WITH_CURRENT_DATA,
                        missing=("order-flow",),
                    ),
                ),
            ),
            "REQUIRED_INPUT_NOT_OBSERVABLE",
        )
        self.assert_not_ready(
            contract(unavailable_inputs=("price",)),
            "REQUIRED_INPUT_NOT_OBSERVABLE",
        )
        # A non-required missing surface does not block readiness.
        ok = contract(
            observation_surfaces=(
                observation_surface(
                    required=False,
                    obs=ObservabilityStatus.NOT_OBSERVABLE_WITH_CURRENT_DATA,
                ),
            )
        )
        self.assertTrue(validate_contract(ok).ready)

    def test_multiple_source_permitted_variants_cannot_silently_collapse(self):
        # Declared two source variants but only one branch -> silent collapse.
        self.assert_not_ready(
            contract(source_variant_count=2),
            "SOURCE_VARIANTS_SILENTLY_COLLAPSED",
        )
        # Correctly represented variants pass (exactly one PRIMARY).
        ok = contract(
            source_variant_count=2,
            interpretations=(
                interpretation("b1", ("c1",), variant="A", primary=True),
                interpretation("b2", ("c1",), variant="B", primary=False),
            ),
        )
        self.assertTrue(validate_contract(ok).ready)
        # Inventing a variant the source did not permit also fails closed.
        self.assert_not_ready(
            contract(
                source_variant_count=1,
                interpretations=(
                    interpretation("b1", ("c1",), variant="A", primary=True),
                    interpretation("b2", ("c1",), variant="B", primary=False),
                ),
            ),
            "SOURCE_VARIANTS_INVENTED",
        )

    def test_missing_primary_blocks_when_required(self):
        # P-01: claim-level PRIMARY. A claim whose only interpretation is not
        # primary_selected has no PRIMARY -> blocker.
        self.assert_not_ready(
            contract(interpretations=(interpretation(primary=False),)),
            "CLAIM_PRIMARY_MISSING",
        )

    def test_each_claim_with_exactly_one_primary_is_machine_ready(self):
        # P-01/C02: two claims, each with its own PRIMARY branch -> PRIMARY check
        # passes. The old contract-wide single-PRIMARY rule would have rejected
        # this multi-component contract.
        result = validate_contract(
            contract(
                source_claims=(source_claim("c1"), source_claim("c2", source_id="s2")),
                interpretations=(
                    interpretation("b1", ("c1",), primary=True),
                    interpretation("b2", ("c2",), primary=True),
                ),
            )
        )
        self.assertEqual(result.readiness, MachineReadiness.MACHINE_READY)
        self.assertTrue(result.ready)
        self.assertEqual(result.blockers, ())

    def test_duplicate_primary_for_one_claim_blocks(self):
        # P-01/C03: two PRIMARY branches for the SAME claim -> blocker.
        self.assert_not_ready(
            contract(
                source_claims=(source_claim("c1"),),
                interpretations=(
                    interpretation("b1", ("c1",), primary=True),
                    interpretation("b2", ("c1",), primary=True),
                ),
            ),
            "CLAIM_PRIMARY_MULTIPLE",
        )

    def test_missing_machine_identities_blocks(self):
        self.assert_not_ready(contract(machine=None), "MACHINE_OPERATIONALIZATION_MISSING")
        self.assert_not_ready(
            contract(machine=machine(code_hash="")),
            "MACHINE_IDENTITIES_MISSING",
        )
        self.assert_not_ready(
            contract(machine=machine(environment_hash="")),
            "MACHINE_IDENTITIES_MISSING",
        )
        # Empty parameter/feature sets are legitimate values, not missing identity.
        self.assertTrue(validate_contract(contract(machine=machine(parameter_identities=()))).ready)
        self.assertTrue(
            validate_contract(contract(machine=machine(required_feature_versions=()))).ready
        )

    def test_missing_scope_blocks(self):
        self.assert_not_ready(contract(instrument_scope=()), "SCOPE_MISSING")
        self.assert_not_ready(contract(timeframe_scope=()), "SCOPE_MISSING")

    def test_inferred_transfer_remains_distinguishable_from_explicit(self):
        # A contract with an INFERRED branch declared EXPLICIT is mislabeled.
        self.assert_not_ready(
            contract(
                interpretations=(interpretation(transfer=TransferStatus.INFERRED),),
                project_transfer_status=TransferStatus.EXPLICIT,
            ),
            "INFERRED_TRANSFER_MISLABELED_EXPLICIT",
        )
        # The same contract honestly declared INFERRED stays machine ready.
        ok = contract(
            interpretations=(interpretation(transfer=TransferStatus.INFERRED),),
            project_transfer_status=TransferStatus.INFERRED,
        )
        self.assertTrue(validate_contract(ok).ready)
        self.assertNotEqual(
            contract(project_transfer_status=TransferStatus.EXPLICIT).project_transfer_status,
            ok.project_transfer_status,
        )


class PlaybookContractStrategyBridgeTests(unittest.TestCase):
    def setUp(self):
        self.parameters, self.machine_ids = ready_machine_params()
        self.instance = contract(machine=machine(parameter_identities=self.machine_ids))

    def test_bridge_preserves_lineage_version_parameters_features(self):
        identity = bridge_to_strategy_identity(
            self.instance,
            **bridge_kwargs(self.parameters),
        )
        self.assertIsInstance(identity, StrategyIdentity)
        self.assertEqual(identity.research_lineage_id, self.instance.research_lineage_id)
        self.assertEqual(identity.family_id, self.instance.family_id)
        self.assertTrue(identity.strategy_version.startswith(f"pc-{self.instance.contract_version}"))
        self.assertEqual(identity.parameters, self.parameters)
        self.assertEqual(identity.required_feature_versions, ("feature-v1",))
        self.assertEqual(identity.code_hash, "code-hash-v1")
        self.assertEqual(identity.environment_hash, "env-hash-v1")
        self.assertEqual(identity.applicable_instruments, ("cu",))
        self.assertEqual(identity.data_exposure_history_reference, "exposure-fixture-v1")

    def test_bridge_is_deterministic(self):
        first = bridge_to_strategy_identity(self.instance, **bridge_kwargs(self.parameters))
        second = bridge_to_strategy_identity(self.instance, **bridge_kwargs(self.parameters))
        self.assertEqual(first.identity_id, second.identity_id)

    def test_bridge_sets_playbook_contract_identity(self):
        # Package B P-06/F-07: the bridged StrategyIdentity must carry the exact
        # PlaybookContract identity so register_outcome_test can enforce the
        # strategy -> contract binding without caller-supplied attestation.
        identity = bridge_to_strategy_identity(
            self.instance,
            **bridge_kwargs(self.parameters),
        )
        self.assertEqual(identity.playbook_contract_identity, self.instance.contract_identity)

    def test_changing_contract_content_changes_bridged_strategy_identity(self):
        other = contract(
            contract_id="pb-generic-fixture-002",
            interpretations=(interpretation(basis="different source basis"),),
            machine=machine(parameter_identities=self.machine_ids),
        )
        first = bridge_to_strategy_identity(self.instance, **bridge_kwargs(self.parameters))
        second = bridge_to_strategy_identity(other, **bridge_kwargs(self.parameters))
        self.assertNotEqual(first.strategy_version, second.strategy_version)
        self.assertNotEqual(first.identity_id, second.identity_id)

    def test_bridge_refuses_draft_contract(self):
        draft = contract(machine=None)
        with self.assertRaisesRegex(ValueError, "not machine ready"):
            bridge_to_strategy_identity(draft, **bridge_kwargs(self.parameters))

    def test_bridge_rejects_mismatched_machine_inputs(self):
        with self.assertRaisesRegex(ValueError, "code hash"):
            bridge_to_strategy_identity(
                self.instance,
                **bridge_kwargs(self.parameters, code_hash="different-hash"),
            )
        with self.assertRaisesRegex(ValueError, "parameters do not match"):
            other_params = (TypedParameter("window", "int", 9),)
            bridge_to_strategy_identity(
                self.instance,
                **bridge_kwargs(other_params),
            )

    def test_duplicate_family_version_mutation_rejected_by_existing_catalog(self):
        identity = bridge_to_strategy_identity(self.instance, **bridge_kwargs(self.parameters))
        catalog = StrategyCatalog()
        catalog.register(identity)
        # Reusing the same family/version with different evidence must be rejected.
        forged = replace(identity, parameters=(TypedParameter("window", "int", 9),))
        with self.assertRaisesRegex(ValueError, "cannot be reused"):
            catalog.register(forged)

    def test_zero_parameter_fixed_rule_strategy_bridges(self):
        instance = contract(machine=machine(parameter_identities=()))
        self.assertTrue(validate_contract(instance).ready)
        identity = bridge_to_strategy_identity(
            instance,
            **bridge_kwargs((), code_hash="code-hash-v1"),
        )
        self.assertEqual(identity.parameters, ())
        self.assertEqual(identity.required_feature_versions, ("feature-v1",))

    def test_zero_required_feature_version_strategy_bridges(self):
        instance = contract(
            machine=machine(
                required_feature_versions=(),
                parameter_identities=self.machine_ids,
            )
        )
        self.assertTrue(validate_contract(instance).ready)
        identity = bridge_to_strategy_identity(
            instance,
            parameters=self.parameters,
            code_hash="code-hash-v1",
            environment_hash="env-hash-v1",
            required_feature_versions=(),
            data_exposure_history_reference="exposure-fixture-v1",
        )
        self.assertEqual(identity.required_feature_versions, ())
        self.assertEqual(identity.parameters, self.parameters)

    def test_zero_parameters_and_zero_feature_versions_bridge(self):
        instance = contract(
            machine=machine(required_feature_versions=(), parameter_identities=())
        )
        self.assertTrue(validate_contract(instance).ready)
        identity = bridge_to_strategy_identity(
            instance,
            parameters=(),
            code_hash="code-hash-v1",
            environment_hash="env-hash-v1",
            required_feature_versions=(),
            data_exposure_history_reference="exposure-fixture-v1",
        )
        self.assertEqual(identity.parameters, ())
        self.assertEqual(identity.required_feature_versions, ())

    def test_empty_machine_parameter_set_rejects_nonempty_caller_parameters(self):
        instance = contract(machine=machine(parameter_identities=()))
        self.assertTrue(validate_contract(instance).ready)
        with self.assertRaisesRegex(ValueError, "parameters do not match"):
            bridge_to_strategy_identity(
                instance,
                parameters=(TypedParameter("window", "int", 3),),
                code_hash="code-hash-v1",
                environment_hash="env-hash-v1",
                required_feature_versions=("feature-v1",),
                data_exposure_history_reference="exposure-fixture-v1",
            )

    def test_nonempty_machine_parameter_set_rejects_empty_caller_parameters(self):
        instance = contract(machine=machine(parameter_identities=self.machine_ids))
        self.assertTrue(validate_contract(instance).ready)
        with self.assertRaisesRegex(ValueError, "parameters do not match"):
            bridge_to_strategy_identity(
                instance,
                parameters=(),
                code_hash="code-hash-v1",
                environment_hash="env-hash-v1",
                required_feature_versions=("feature-v1",),
                data_exposure_history_reference="exposure-fixture-v1",
            )

    def test_empty_machine_feature_set_rejects_nonempty_caller_features(self):
        instance = contract(
            machine=machine(
                required_feature_versions=(),
                parameter_identities=self.machine_ids,
            )
        )
        self.assertTrue(validate_contract(instance).ready)
        with self.assertRaisesRegex(ValueError, "required feature versions do not match"):
            bridge_to_strategy_identity(
                instance,
                parameters=self.parameters,
                code_hash="code-hash-v1",
                environment_hash="env-hash-v1",
                required_feature_versions=("feature-v1",),
                data_exposure_history_reference="exposure-fixture-v1",
            )

    def test_nonempty_machine_feature_set_rejects_empty_caller_features(self):
        instance = contract(machine=machine(parameter_identities=self.machine_ids))
        self.assertTrue(validate_contract(instance).ready)
        with self.assertRaisesRegex(ValueError, "required feature versions do not match"):
            bridge_to_strategy_identity(
                instance,
                parameters=self.parameters,
                code_hash="code-hash-v1",
                environment_hash="env-hash-v1",
                required_feature_versions=(),
                data_exposure_history_reference="exposure-fixture-v1",
            )

    def test_playbook_module_cannot_authorize_research_firewall_access(self):
        import src.playbook_contract as playbook_contract

        source = inspect.getsource(playbook_contract)
        # The module must not import the firewall and must expose no outcome API.
        for forbidden_import in (
            "import src.research_firewall",
            "from src.research_firewall",
            "from src import research_firewall",
        ):
            self.assertNotIn(forbidden_import, source)
        for forbidden_api in (
            "request_candidate_outcome_access",
            "request_protected_market_outcome",
            "OutcomeTestRegistration",
        ):
            self.assertNotIn(forbidden_api, source)
        self.assertFalse(hasattr(playbook_contract, "request_candidate_outcome_access"))
        self.assertFalse(hasattr(playbook_contract, "ResearchFirewall"))
        self.assertFalse(hasattr(playbook_contract, "OutcomeTestRegistration"))
        # The module source must state the sole-owner boundary.
        self.assertIn("sole outcome-access owner", source)

        # Bridging alone performs no registration and grants no access.
        identity = bridge_to_strategy_identity(
            self.instance,
            **bridge_kwargs(self.parameters),
        )
        self.assertEqual(identity.lifecycle_state, LifecycleState.DRAFT)
        catalog = StrategyCatalog()
        self.assertEqual(catalog.records, ())
        instance = contract(machine=machine(parameter_identities=self.machine_ids))
        self.assertTrue(validate_contract(instance).ready)
        with self.assertRaisesRegex(ValueError, "required feature versions do not match"):
            bridge_to_strategy_identity(
                instance,
                parameters=self.parameters,
                code_hash="code-hash-v1",
                environment_hash="env-hash-v1",
                required_feature_versions=(),
                data_exposure_history_reference="exposure-fixture-v1",
            )

    def test_playbook_module_cannot_authorize_research_firewall_access(self):
        import src.playbook_contract as playbook_contract

        source = inspect.getsource(playbook_contract)
        # The module must not import the firewall and must expose no outcome API.
        for forbidden_import in (
            "import src.research_firewall",
            "from src.research_firewall",
            "from src import research_firewall",
        ):
            self.assertNotIn(forbidden_import, source)
        for forbidden_api in (
            "request_candidate_outcome_access",
            "request_protected_market_outcome",
            "OutcomeTestRegistration",
        ):
            self.assertNotIn(forbidden_api, source)
        self.assertFalse(hasattr(playbook_contract, "request_candidate_outcome_access"))
        self.assertFalse(hasattr(playbook_contract, "ResearchFirewall"))
        self.assertFalse(hasattr(playbook_contract, "OutcomeTestRegistration"))
        # The module source must state the sole-owner boundary.
        self.assertIn("sole outcome-access owner", source)

        # Bridging alone performs no registration and grants no access.
        identity = bridge_to_strategy_identity(
            self.instance,
            **bridge_kwargs(self.parameters),
        )
        self.assertEqual(identity.lifecycle_state, LifecycleState.DRAFT)
        catalog = StrategyCatalog()
        self.assertEqual(catalog.records, ())


class PlaybookContractPackageCProtocolInvariantTests(unittest.TestCase):
    """Package C protocol invariant regressions (P-01..P-05 / C01..C13).

    Synthetic contracts only. Proves machine-readiness is derived from claim-level
    PRIMARY, ambiguity, observability, transfer and timeframe facts instead of
    caller self-attestation.
    """

    def _two_claim_contract(self, **overrides):
        """Machine-ready two-claim contract: c1->b1 PRIMARY, c2->b2 PRIMARY."""
        base = dict(
            source_claims=(source_claim("c1"), source_claim("c2", source_id="s2")),
            interpretations=(
                interpretation("b1", ("c1",), primary=True),
                interpretation("b2", ("c2",), primary=True),
            ),
        )
        base.update(overrides)
        return contract(**base)

    def assert_not_ready(self, instance, *expected_blockers):
        result = validate_contract(instance)
        self.assertIsInstance(result, ContractValidationResult)
        self.assertEqual(result.readiness, MachineReadiness.NOT_MACHINE_READY)
        self.assertFalse(result.ready)
        for blocker in expected_blockers:
            self.assertIn(blocker, result.blockers)
        return result

    # -- C01: two claims, only C1 has a PRIMARY -> NOT_MACHINE_READY. ----------
    def test_c01_claim_without_primary_not_machine_ready(self):
        instance = self._two_claim_contract(
            interpretations=(
                interpretation("b1", ("c1",), primary=True),
                interpretation("b2", ("c2",), primary=False),
            )
        )
        self.assert_not_ready(instance, "CLAIM_PRIMARY_MISSING")

    # -- C02: each claim exactly one PRIMARY -> PRIMARY check passes. ----------
    def test_c02_each_claim_exactly_one_primary_passes(self):
        result = validate_contract(self._two_claim_contract())
        self.assertEqual(result.readiness, MachineReadiness.MACHINE_READY)
        self.assertTrue(result.ready)
        self.assertEqual(result.blockers, ())

    # -- C03: two PRIMARY branches for one claim -> blocker. -------------------
    def test_c03_duplicate_primary_for_one_claim_blocks(self):
        instance = self._two_claim_contract(
            interpretations=(
                interpretation("b1", ("c1",), primary=True),
                interpretation("b3", ("c1",), primary=True),
                interpretation("b2", ("c2",), primary=True),
            )
        )
        self.assert_not_ready(instance, "CLAIM_PRIMARY_MULTIPLE")

    # -- C04: PRIMARY missing + ambiguity_status=NONE still blocks. ------------
    def test_c04_primary_missing_with_ambiguity_none_still_blocks(self):
        instance = self._two_claim_contract(
            interpretations=(
                interpretation("b1", ("c1",), primary=True),
                interpretation("b2", ("c2",), primary=False),
            ),
            ambiguity_status=AmbiguityStatus.NONE,
        )
        self.assert_not_ready(instance, "CLAIM_PRIMARY_MISSING")

    # -- C05: PRIMARY missing + ambiguity_status=RESOLVED still blocks. --------
    def test_c05_primary_missing_with_ambiguity_resolved_still_blocks(self):
        instance = self._two_claim_contract(
            interpretations=(
                interpretation("b1", ("c1",), primary=True),
                interpretation("b2", ("c2",), primary=False),
            ),
            ambiguity_status=AmbiguityStatus.RESOLVED,
            ambiguity_notes="source resolved the choice",
        )
        self.assert_not_ready(instance, "CLAIM_PRIMARY_MISSING")

    # -- C06: PRIMARY complete + UNRESOLVED_CRITICAL still blocks. -------------
    def test_c06_primary_complete_with_unresolved_critical_blocks(self):
        instance = self._two_claim_contract(
            ambiguity_status=AmbiguityStatus.UNRESOLVED_CRITICAL,
        )
        self.assert_not_ready(instance, "UNRESOLVED_CRITICAL_AMBIGUITY")

    # -- C07: required PARTIALLY_OBSERVABLE -> blocker. ------------------------
    def test_c07_required_partially_observable_blocks(self):
        instance = contract(
            observation_surfaces=(
                observation_surface(
                    obs=ObservabilityStatus.PARTIALLY_OBSERVABLE,
                    missing=("order-flow",),
                ),
            )
        )
        self.assert_not_ready(instance, "REQUIRED_INPUT_NOT_FULLY_OBSERVABLE")

    # -- C08: UNKNOWN project transfer -> blocker. -----------------------------
    def test_c08_unknown_project_transfer_blocks(self):
        instance = contract(project_transfer_status=TransferStatus.UNKNOWN)
        self.assert_not_ready(instance, "PROJECT_TRANSFER_UNKNOWN")
        # INFERRED remains allowed, only as explicitly labeled inferred transfer.
        inferred_ok = contract(
            interpretations=(interpretation(transfer=TransferStatus.INFERRED),),
            project_transfer_status=TransferStatus.INFERRED,
        )
        self.assertTrue(validate_contract(inferred_ok).ready)

    # -- C09: two timeframes -> blocker. ---------------------------------------
    def test_c09_multiple_timeframes_block(self):
        instance = contract(timeframe_scope=("15m", "60m"))
        self.assert_not_ready(instance, "MULTIPLE_TIMEFRAMES_UNRESOLVED")

    # -- C10: bridge refuses multi-timeframe (fail closed). --------------------
    def test_c10_bridge_refuses_multiple_timeframes(self):
        params, machine_ids = ready_machine_params()
        instance = contract(
            timeframe_scope=("15m", "60m"),
            machine=machine(parameter_identities=machine_ids),
        )
        with self.assertRaisesRegex(ValueError, "not machine ready|MULTIPLE_TIMEFRAMES"):
            bridge_to_strategy_identity(instance, **bridge_kwargs(params))

    # -- C11: single timeframe bridges the exact value. ------------------------
    def test_c11_single_timeframe_bridges_exact_value(self):
        params, machine_ids = ready_machine_params()
        instance = contract(machine=machine(parameter_identities=machine_ids))
        identity = bridge_to_strategy_identity(instance, **bridge_kwargs(params))
        self.assertEqual(identity.timeframe, "5m")
        self.assertEqual(identity.timeframe, instance.timeframe_scope[0])

    # -- C12: primary_selection_identity is deterministic. ---------------------
    def test_c12_primary_selection_identity_is_deterministic(self):
        first = self._two_claim_contract()
        second = self._two_claim_contract()
        self.assertEqual(first.primary_selection_identity, second.primary_selection_identity)
        self.assertTrue(first.primary_selection_identity)
        self.assertTrue(first.primary_selection_identity.isalnum())

    # -- C13: changing a claim's PRIMARY changes the identity. -----------------
    def test_c13_changing_claim_primary_changes_identity(self):
        def variant(select_b1: bool):
            return self._two_claim_contract(
                interpretations=(
                    interpretation("b1", ("c1",), primary=select_b1),
                    interpretation("b3", ("c1",), primary=not select_b1),
                    interpretation("b2", ("c2",), primary=True),
                )
            )

        contract_a = variant(True)
        contract_b = variant(False)
        self.assertTrue(validate_contract(contract_a).ready)
        self.assertTrue(validate_contract(contract_b).ready)
        self.assertNotEqual(
            contract_a.primary_selection_identity,
            contract_b.primary_selection_identity,
        )

    # -- C14 companion: incomplete PRIMARY resolution yields no fake identity. --
    def test_c14_primary_selection_identity_raises_when_incomplete(self):
        instance = self._two_claim_contract(
            interpretations=(
                interpretation("b1", ("c1",), primary=True),
                interpretation("b2", ("c2",), primary=False),
            )
        )
        with self.assertRaisesRegex(ValueError, "PRIMARY"):
            _ = instance.primary_selection_identity

    # -- C-C02: duplicate source claim ids fail closed (no fuzzy equivalence). --

    def _duplicate_claim_contract(self):
        return contract(
            source_claims=(
                source_claim("C1", anchor="book:A"),
                source_claim("C1", anchor="book:B"),
            ),
            interpretations=(
                interpretation("b1", ("C1",), primary=True),
            ),
        )

    def test_cc02a_duplicate_claim_id_blocks_machine_readiness(self):
        self.assert_not_ready(
            self._duplicate_claim_contract(), "DUPLICATE_SOURCE_CLAIM_ID"
        )

    def test_cc02b_primary_selection_identity_raises_on_duplicate_claim_ids(self):
        instance = self._duplicate_claim_contract()
        with self.assertRaisesRegex(ValueError, "duplicate source claim ids"):
            _ = instance.primary_selection_identity

    def test_cc02c_single_primary_branch_cannot_cover_duplicate_claim_ids(self):
        # Even one branch referencing ("C1",) with primary_selected=True cannot
        # make a duplicate-claim contract machine-ready.
        instance = self._duplicate_claim_contract()
        result = validate_contract(instance)
        self.assertEqual(result.readiness, MachineReadiness.NOT_MACHINE_READY)
        self.assertIn("DUPLICATE_SOURCE_CLAIM_ID", result.blockers)


if __name__ == "__main__":
    unittest.main()

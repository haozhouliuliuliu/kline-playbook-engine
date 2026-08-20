"""Combined Package C + F + B cross-package integration test.

Proves the three repaired packages operate as ONE closed system after the
C/D/F combined integration merge:

- Package F source evidence: ``ApprovedSourceMaterialRef.from_bytes`` ->
  material-bound ``ApprovedSourceBundle`` -> project-issued SOURCE_ONLY session
  bound to the material-derived ``session_binding_identity``/``session_binding_hash``
  -> a claim record with a legal ``(source_id, material_id)`` pair.
- Package C Playbook bridge: a machine-ready ``PlaybookContract`` bound to that
  same bundle/session, a ``StrategyIdentity`` produced by the REAL deterministic
  ``bridge_to_strategy_identity()``, and ``register_outcome_test()`` requiring
  ``validate_contract()`` MACHINE_READY plus
  ``validate_strategy_against_playbook_contract()``.
- Package B firewall: TEST_ONLY profile lock + wave lock + outcome registration
  through ONE shared ``ResearchFirewall`` instance (single authority).

Two tamper proofs:
- T1: swapping the material bytes invalidates the verified SOURCE_ONLY binding
  for the SAME (old) session.
- T2: manually tampering the bridged ``StrategyIdentity`` timeframe or code hash
  makes outcome registration fail closed before any mutation.

No candidate market outcome data is used anywhere in this test.
"""

import unittest
from dataclasses import replace

from src.playbook_contract import (
    ClaimStatus,
    SourceClaimRef,
    bridge_to_strategy_identity,
    validate_contract,
)
from src.research_firewall import (
    ApprovedSourceBundle,
    ApprovedSourceMaterialRef,
    ByteBindingStatus,
    ClaimRecordDraft,
    ClaimRecordOutput,
    ResearchFirewall,
    SourceOnlyClaimExtractionContext,
    SourceOnlyPolicy,
)
from src.strategy_evidence import EvidenceLedger
from tests.synthetic_fixture import (
    SYNTHETIC_EXPOSURE_REFERENCE,
    SYNTHETIC_HYPOTHESIS_TEST_ID,
    SYNTHETIC_MATERIAL_ANCHOR,
    SYNTHETIC_MATERIAL_ID,
    SYNTHETIC_PARAMETER,
    SYNTHETIC_SESSION_ID,
    SYNTHETIC_SOURCE_ID,
    SYNTHETIC_WAVE_ID,
    make_artifact_bindings,
    make_code_artifact,
    make_contract,
    make_environment_artifact,
    make_experiment,
    make_test_only_profile,
    make_wave_manifest,
)

ORIGINAL_MATERIAL_BYTES = b"cdf combined integration material bytes v1"
TAMPERED_MATERIAL_BYTES = b"tampered material bytes v1"


class CDFCombinedIntegrationTests(unittest.TestCase):
    """F source evidence + C Playbook bridge + B firewall as one chain."""

    def _build_bundle(self, material_bytes: bytes) -> ApprovedSourceBundle:
        material = ApprovedSourceMaterialRef.from_bytes(
            source_id=SYNTHETIC_SOURCE_ID,
            material_id=SYNTHETIC_MATERIAL_ID,
            source_anchor_reference=SYNTHETIC_MATERIAL_ANCHOR,
            content=material_bytes,
        )
        return ApprovedSourceBundle(
            source_bundle_id="cdf-combined-bundle-v1",
            source_bundle_hash="cdf-combined-legacy-recorded-hash",
            source_anchor_reference=SYNTHETIC_MATERIAL_ANCHOR,
            materials=(material,),
            content_note="cdf combined integration synthetic bundle",
        )

    def _open_session(self, policy: SourceOnlyPolicy, bundle: ApprovedSourceBundle):
        # F-C01: the session binds the material-derived bundle binding
        # identity/hash, never the legacy recorded bundle id/hash.
        return policy.open_verified_session(
            session_id=SYNTHETIC_SESSION_ID,
            model_identity="model-fixture-v1",
            prompt_spec_version="prompt-spec-v1",
            source_bundle_identity=bundle.session_binding_identity,
            source_bundle_hash=bundle.session_binding_hash,
            tool_retrieval_mode="PROJECT_SOURCE_ONLY",
            researcher_model_exposure_note="no known exposure",
        )

    def test_combined_chain_and_tamper_proofs(self):
        # ONE shared firewall (Package B F-03).
        firewall = ResearchFirewall(EvidenceLedger())
        policy = firewall.source_only

        # 1. F: exact-byte material ref.
        bundle = self._build_bundle(ORIGINAL_MATERIAL_BYTES)
        self.assertEqual(bundle.byte_binding_status, ByteBindingStatus.EXACT_BYTES_BOUND)

        # 2-3. F: material-bound bundle + project-issued verified session.
        session = self._open_session(policy, bundle)
        self.assertTrue(policy.is_verified(session.session_id))

        # 4. F: claim record with a legal (source_id, material_id) pair.
        output = ClaimRecordOutput()
        context = SourceOnlyClaimExtractionContext(
            source_bundle=bundle,
            source_only=policy,
            session_id=session.session_id,
            output_surface=output,
        )
        self.assertTrue(context.verified)
        draft = ClaimRecordDraft(
            claim_id="cdf-c1",
            source_id=SYNTHETIC_SOURCE_ID,
            material_id=SYNTHETIC_MATERIAL_ID,
            source_anchor=f"{SYNTHETIC_MATERIAL_ANCHOR}:page-1",
            claim_status="EXPLICIT",
            source_excerpt_short_or_paraphrase="synthetic combined chain claim",
            source_only_session_id=session.session_id,
            created_at="2026-08-20T00:00:00Z",
        )
        context.record_claim(draft)
        self.assertEqual(output.records[0].source_id, SYNTHETIC_SOURCE_ID)
        self.assertEqual(output.records[0].material_id, SYNTHETIC_MATERIAL_ID)
        self.assertEqual(output.records[0].claim_status, "EXPLICIT")

        # 5. C: machine-ready PlaybookContract bound to the same bundle/session.
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
        readiness = validate_contract(contract)
        self.assertTrue(readiness.ready, readiness.blockers)

        # 6. C: real deterministic bridge -> StrategyIdentity.
        strategy = bridge_to_strategy_identity(
            contract,
            parameters=(SYNTHETIC_PARAMETER,),
            code_hash=make_code_artifact().sha256,
            environment_hash=make_environment_artifact().sha256,
            required_feature_versions=("feature-v1",),
            data_exposure_history_reference=SYNTHETIC_EXPOSURE_REFERENCE,
        )
        self.assertEqual(strategy.playbook_contract_identity, contract.contract_identity)

        # 7. B: TEST_ONLY profile registered + locked.
        profile = firewall.profiles.register(make_test_only_profile())
        firewall.profiles.lock(profile.profile_id)

        # 8. B: wave whose PRIMARY/scope/search binding is derived from the
        # actual contract + strategy artifacts (F-06).
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

        # 9. B + C: register_outcome_test succeeds only with MACHINE_READY
        # contract, bridge-equivalent strategy, and verified source session.
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
        self.assertEqual(registration.source_bundle_identity, bundle.session_binding_identity)
        self.assertEqual(registration.source_bundle_hash, bundle.session_binding_hash)
        firewall.lock_wave(wave.research_wave_id)

        # T1: swapping material bytes must invalidate the SAME old session's
        # SOURCE_ONLY binding to the (new) bundle.
        tampered_bundle = self._build_bundle(TAMPERED_MATERIAL_BYTES)
        self.assertNotEqual(
            tampered_bundle.session_binding_identity,
            bundle.session_binding_identity,
        )
        tampered_context = SourceOnlyClaimExtractionContext(
            source_bundle=tampered_bundle,
            source_only=policy,
            session_id=session.session_id,
            output_surface=ClaimRecordOutput(),
        )
        self.assertFalse(tampered_context.verified)

        # T2: tampering the bridged StrategyIdentity fails registration closed.
        bad_timeframe = replace(strategy, timeframe="60m")
        with self.assertRaisesRegex(ValueError, "timeframe does not match"):
            firewall.register_outcome_test(
                hypothesis_test_id=SYNTHETIC_HYPOTHESIS_TEST_ID,
                contract=contract,
                strategy=bad_timeframe,
                experiment=experiment,
                artifact_bindings=make_artifact_bindings(),
                source_only_session_id=session.session_id,
                research_wave_id=wave.research_wave_id,
                statistical_profile_id=profile.profile_id,
                multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
            )
        bad_code = replace(strategy, code_hash="0" * 64)
        with self.assertRaisesRegex(ValueError, "code hash does not match"):
            firewall.register_outcome_test(
                hypothesis_test_id=SYNTHETIC_HYPOTHESIS_TEST_ID,
                contract=contract,
                strategy=bad_code,
                experiment=experiment,
                artifact_bindings=make_artifact_bindings(),
                source_only_session_id=session.session_id,
                research_wave_id=wave.research_wave_id,
                statistical_profile_id=profile.profile_id,
                multiplicity_counting_unit_identity=wave.multiplicity_counting_unit_identity,
            )


if __name__ == "__main__":
    unittest.main()

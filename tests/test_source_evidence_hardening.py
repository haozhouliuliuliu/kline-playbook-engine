"""Package F — SOURCE_ONLY source-evidence hardening tests (S-01/S-02/S-04).

Focused regression coverage for:
- forward-only exact byte binding (``ApprovedSourceMaterialRef.from_bytes``);
- explicit historical-unbound representation (``NOT_RECORDED``);
- no caller-supplied-digest exact-byte construction path;
- ``ApprovedSourceBundle`` material refs bound into the bundle identity;
- ``ClaimRecordDraft`` required ``material_id`` and the ``(source_id,
  material_id)`` pair + source-anchor enforcement in
  ``SourceOnlyClaimExtractionContext.record_claim()``;
- protected market-outcome technical denial remains active;
- Package B verification behavior (``open_verified_session`` / ``is_verified``
  / manual ``record_session`` cannot self-verify) stays green.

No candidate outcome data is used; no historical artifact is rewritten.
"""

import inspect
import unittest
from hashlib import sha256

from src.research_firewall import (
    ApprovedSourceBundle,
    ApprovedSourceMaterialRef,
    ByteBindingStatus,
    ClaimRecordDraft,
    ClaimRecordOutput,
    ProtectedMarketAccessMode,
    ResearchFirewall,
    SourceOnlyClaimExtractionContext,
    SourceOnlySession,
)
from src.strategy_evidence import EvidenceLedger
from tests.synthetic_fixture import (
    SYNTHETIC_MATERIAL_ANCHOR,
    SYNTHETIC_MATERIAL_ID,
    SYNTHETIC_SESSION_ID,
    SYNTHETIC_SOURCE_BUNDLE_ID,
    SYNTHETIC_SOURCE_ID,
    make_approved_bundle,
    make_approved_material_ref,
    make_open_session,
)


def _exact_ref(*, content: bytes, material_id: str = "M1") -> ApprovedSourceMaterialRef:
    return ApprovedSourceMaterialRef.from_bytes(
        source_id="SRC-X",
        material_id=material_id,
        source_anchor_reference=material_id,
        content=content,
    )


class SourceEvidenceHardeningTests(unittest.TestCase):
    """F01..F13 — Package F source-evidence hardening acceptance tests."""

    # -- F01 / F02: from_bytes byte binding --------------------------------

    def test_f01_from_bytes_same_bytes_same_identity(self):
        first = _exact_ref(content=b"exact bytes v1")
        second = _exact_ref(content=b"exact bytes v1")
        self.assertEqual(first.material_identity, second.material_identity)
        self.assertEqual(first.fetched_content_sha256, sha256(b"exact bytes v1").hexdigest())
        self.assertEqual(first.fetched_byte_size, len(b"exact bytes v1"))
        self.assertIs(first.byte_binding_status, ByteBindingStatus.EXACT_BYTES_BOUND)

    def test_f02_changed_bytes_changed_material_identity(self):
        first = _exact_ref(content=b"bytes-A")
        second = _exact_ref(content=b"bytes-B")
        self.assertNotEqual(first.material_identity, second.material_identity)
        self.assertNotEqual(first.fetched_content_sha256, second.fetched_content_sha256)

    # -- F03: historical unbound -------------------------------------------

    def test_f03_historical_unbound_explicit_no_hash(self):
        ref = ApprovedSourceMaterialRef.historical_unbound(
            source_id="SRC-X", material_id="M1", source_anchor_reference="M1"
        )
        self.assertIsNone(ref.fetched_content_sha256)
        self.assertIsNone(ref.fetched_byte_size)
        self.assertIs(ref.byte_binding_status, ByteBindingStatus.NOT_RECORDED)

    # -- F04: no caller-digest exact constructor ----------------------------

    def test_f04_no_exact_byte_construction_accepts_caller_digest(self):
        with self.assertRaises(TypeError):
            ApprovedSourceMaterialRef(  # type: ignore[call-arg]
                source_id="SRC-X",
                material_id="M1",
                source_anchor_reference="M1",
                byte_binding_status=ByteBindingStatus.EXACT_BYTES_BOUND,
                fetched_content_sha256="0" * 64,
                fetched_byte_size=10,
            )
        # from_bytes accepts content bytes only: no digest/sha256/size inputs.
        parameters = inspect.signature(ApprovedSourceMaterialRef.from_bytes).parameters
        for forbidden in ("digest", "sha256", "byte_size", "fetched_content_sha256", "fetched_byte_size"):
            self.assertNotIn(forbidden, parameters)
        # from_bytes derives the digest internally from the actual bytes.
        ref = ApprovedSourceMaterialRef.from_bytes(
            source_id="SRC-X", material_id="M1", source_anchor_reference="M1", content=b"x" * 100
        )
        self.assertEqual(ref.fetched_byte_size, 100)

    # -- F05: bundle identity binds exact material bytes --------------------

    def test_f05_exact_material_change_changes_bundle_identity(self):
        bundle_a = ApprovedSourceBundle(
            source_bundle_id="SB-1",
            source_bundle_hash="recorded-hash",
            source_anchor_reference="R",
            materials=(_exact_ref(content=b"bytes-A"),),
        )
        bundle_b = ApprovedSourceBundle(
            source_bundle_id="SB-1",
            source_bundle_hash="recorded-hash",
            source_anchor_reference="R",
            materials=(_exact_ref(content=b"bytes-B"),),
        )
        self.assertNotEqual(bundle_a.bundle_identity, bundle_b.bundle_identity)
        self.assertIs(bundle_a.byte_binding_status, ByteBindingStatus.EXACT_BYTES_BOUND)

    def test_f05b_legacy_unbound_bundle_is_explicitly_not_recorded(self):
        bundle = ApprovedSourceBundle.legacy_unbound(
            source_bundle_id="SB-LEGACY",
            source_bundle_hash="historical-recorded-hash",
            source_anchor_reference="R",
            material_records=(
                {"source_id": "SRC-X", "material_id": "M1", "source_anchor_reference": "M1"},
            ),
        )
        self.assertIs(bundle.byte_binding_status, ByteBindingStatus.NOT_RECORDED)
        # The recorded historical hash is preserved as a historical value, but
        # it can never upgrade materials to exact byte binding.
        self.assertEqual(bundle.source_bundle_hash, "historical-recorded-hash")
        self.assertTrue(
            all(
                material.byte_binding_status is ByteBindingStatus.NOT_RECORDED
                for material in bundle.materials
            )
        )

    # -- F06: ClaimRecordDraft requires material_id -------------------------

    def test_f06_claim_record_draft_requires_material_id(self):
        with self.assertRaises(TypeError):
            ClaimRecordDraft(  # missing material_id -> fail
                claim_id="c1",
                source_id="S",
                source_anchor="A",
                claim_status="EXPLICIT",
                source_excerpt_short_or_paraphrase="p",
                source_only_session_id="s",
                created_at="t",
            )
        draft = ClaimRecordDraft(
            claim_id="c1",
            source_id="S",
            material_id="M",
            source_anchor="A",
            claim_status="EXPLICIT",
            source_excerpt_short_or_paraphrase="p",
            source_only_session_id="s",
            created_at="t",
        )
        self.assertEqual(draft.material_id, "M")

    # -- runner-based pair/anchor enforcement (F07..F10) --------------------

    def _make_runner(self, policy=None, session=None, bundle=None):
        if policy is None:
            policy = ResearchFirewall(EvidenceLedger()).source_only
        if session is None:
            session = make_open_session(policy)
        if bundle is None:
            bundle = make_approved_bundle()
        output = ClaimRecordOutput()
        runner = SourceOnlyClaimExtractionContext(
            source_bundle=bundle,
            source_only=policy,
            session_id=session.session_id,
            output_surface=output,
        )
        return runner, output

    def _draft(
        self,
        *,
        claim_id="c",
        source_id=SYNTHETIC_SOURCE_ID,
        material_id=SYNTHETIC_MATERIAL_ID,
        source_anchor=f"{SYNTHETIC_MATERIAL_ANCHOR}:page-12",
        session_id=SYNTHETIC_SESSION_ID,
    ) -> ClaimRecordDraft:
        return ClaimRecordDraft(
            claim_id=claim_id,
            source_id=source_id,
            material_id=material_id,
            source_anchor=source_anchor,
            claim_status="EXPLICIT",
            source_excerpt_short_or_paraphrase="synthetic claim",
            source_only_session_id=session_id,
            created_at="2026-08-20T00:00:00Z",
        )

    def test_f07_approved_source_material_pair_records(self):
        runner, output = self._make_runner()
        recorded = runner.record_claim(self._draft(claim_id="c-ok", session_id=runner.session_id))
        self.assertEqual(recorded.claim_id, "c-ok")
        self.assertEqual(len(output.records), 1)

    def test_f08_bundle_id_as_source_id_fails(self):
        runner, _ = self._make_runner()
        draft = self._draft(
            claim_id="c-bundle-id",
            source_id=SYNTHETIC_SOURCE_BUNDLE_ID,  # bundle id, not an approved source id
            session_id=runner.session_id,
        )
        with self.assertRaisesRegex(ValueError, "source/material"):
            runner.record_claim(draft)

    def test_f08b_bundle_id_that_is_also_approved_source_id_passes(self):
        policy = ResearchFirewall(EvidenceLedger()).source_only
        session = make_open_session(policy)
        # "unless the bundle id happens to truly also be an approved source_id"
        bundle = make_approved_bundle(
            materials=(make_approved_material_ref(source_id=SYNTHETIC_SOURCE_BUNDLE_ID),)
        )
        runner, _ = self._make_runner(policy=policy, session=session, bundle=bundle)
        recorded = runner.record_claim(
            self._draft(
                claim_id="c-bundle-id-ok",
                source_id=SYNTHETIC_SOURCE_BUNDLE_ID,
                session_id=runner.session_id,
            )
        )
        self.assertEqual(recorded.claim_id, "c-bundle-id-ok")

    def test_f09_unknown_material_fails(self):
        runner, _ = self._make_runner()
        draft = self._draft(
            claim_id="c-unknown-material",
            material_id="not-an-approved-material",
            session_id=runner.session_id,
        )
        with self.assertRaisesRegex(ValueError, "source/material"):
            runner.record_claim(draft)

    def test_f10_anchor_mismatch_fails(self):
        runner, _ = self._make_runner()
        draft = self._draft(
            claim_id="c-anchor-mismatch",
            source_anchor="completely:different:anchor",
            session_id=runner.session_id,
        )
        with self.assertRaisesRegex(ValueError, "anchor"):
            runner.record_claim(draft)

    def test_f10b_descendant_anchor_accepted(self):
        runner, output = self._make_runner()
        recorded = runner.record_claim(
            self._draft(
                claim_id="c-descendant-anchor",
                source_anchor=f"{SYNTHETIC_MATERIAL_ANCHOR}:page-99:line-3",
                session_id=runner.session_id,
            )
        )
        self.assertEqual(recorded.claim_id, "c-descendant-anchor")

    # -- F11: protected market-outcome denial -------------------------------

    def test_f11_protected_market_outcome_request_denied(self):
        runner, _ = self._make_runner()
        result = runner.request_protected_market_outcome("F-11-request")
        self.assertEqual(result.outcome, "DENIED")
        self.assertEqual(result.reason, "SOURCE_ONLY_TECHNICAL_DENIAL")
        self.assertEqual(len(runner.denial_records), 1)

    # -- F12 / F13: Package B verification behavior -------------------------

    def test_f12_open_verified_session_and_is_verified_green(self):
        policy = ResearchFirewall(EvidenceLedger()).source_only
        session = make_open_session(policy)
        self.assertTrue(policy.is_verified(session.session_id))
        self.assertEqual(
            session.protected_market_access_mode,
            ProtectedMarketAccessMode.TECHNICALLY_DENIED,
        )

    def test_f13_manual_record_session_cannot_self_verify(self):
        policy = ResearchFirewall(EvidenceLedger()).source_only
        manual = SourceOnlySession(
            session_id="manual-f13",
            model_identity="model-fixture-v1",
            prompt_spec_version="prompt-spec-v1",
            source_bundle_identity="bundle-fixture-v1",
            source_bundle_hash="bundle-hash-fixture-v1",
            tool_retrieval_mode="PROJECT_SOURCE_ONLY",
            protected_market_access_mode=ProtectedMarketAccessMode.TECHNICALLY_DENIED,
            verification_evidence="forged-evidence",
        )
        policy.record_session(manual)
        self.assertFalse(policy.is_verified("manual-f13"))


if __name__ == "__main__":
    unittest.main()

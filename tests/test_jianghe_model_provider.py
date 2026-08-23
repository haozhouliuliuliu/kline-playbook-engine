"""江河 provider candidate contract 的纯内存、零网络测试。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from dataclasses import asdict, replace
from functools import lru_cache
from hashlib import sha256
import json
import unittest

from src.jianghe_ai_trader import JiangheObservation, ObservationBar, ObservationIdentity
from src.jianghe_fidelity_evaluation import (
    PROCESSING_ERROR,
    evaluate_response_records,
    load_corpus,
    parse_input_evidence,
)
from src.jianghe_model_provider import (
    CapabilityDeclaration,
    CandidateProviderAdapter,
    CandidateStatus,
    FidelityTrack,
    InvocationConfig,
    InvocationTiming,
    JiangheModelRequest,
    LiveInvocationDisabledError,
    ModelDriftPolicy,
    PromptArtifact,
    ProviderIdentity,
    RequestedModelSelectorIdentity,
    ResolvedProviderModelIdentity,
    StructuredInputArtifact,
    VersionBinding,
    VisualArtifact,
    contract_field_names,
)
from src.jianghe_response_normalizer import (
    EVALUATION_EXTRACTOR_IDENTITY,
    EvaluatorSideJudgment,
    JiangheResponseNormalizer,
    NORMALIZER_IDENTITY,
    RESPONSE_SCHEMA_IDENTITY,
)
from src.jianghe_visual_renderer import (
    JiangheVisualRenderer,
    VisualObservationSpec,
    panels_from_observation_bars,
)


UTC = timezone.utc
T0 = datetime(2026, 8, 23, 9, 0, tzinfo=UTC)
T1 = T0 + timedelta(seconds=1)
T2 = T1 + timedelta(milliseconds=250)
T3 = T2 + timedelta(milliseconds=10)


def identity(seed: str) -> str:
    return sha256(seed.encode("utf-8")).hexdigest()


@lru_cache(maxsize=1)
def observation() -> JiangheObservation:
    return JiangheObservation(
        identity=ObservationIdentity(
            decision_time=T0,
            exchange_time=T0,
            product="cu",
            concrete_contract="SHFE.cu2609",
            mapping_identity=identity("mapping-v1"),
            session_identity=identity("session-v1"),
        ),
        bars=(ObservationBar(
            timeframe="1m",
            open_time=T0 - timedelta(minutes=1),
            close_time=T0,
            available_at=T0,
            open_price="100",
            high_price="101",
            low_price="99",
            close_price="100",
            volume="10",
            is_closed=True,
        ),),
    )


def provider() -> ProviderIdentity:
    return ProviderIdentity(
        provider_id="CANDIDATE_PROVIDER",
        api_surface="RESPONSES_STYLE_API",
        api_version="candidate-v1",
        endpoint_semantics_identity="endpoint-semantics-v1",
        official_documentation_urls=("https://example.invalid/docs",),
    )


def capability(provider_identity: ProviderIdentity | None = None) -> CapabilityDeclaration:
    return CapabilityDeclaration(
        provider_identity=provider_identity or provider(),
        declared_at=T0,
        supported_tracks=tuple(FidelityTrack),
        supports_visual_input=True,
        supports_structured_input=True,
        supports_structured_output=True,
        supports_dual_input=True,
        supports_raw_response_capture=True,
        supports_usage_metadata=True,
        supports_resolved_model_reporting=True,
        supports_timing=True,
        supports_environment_credential=True,
        repeatability_controls=("temperature",),
        model_drift_policy=ModelDriftPolicy.ALIAS_MAY_DRIFT,
    )


def visual(observation_identity: str = identity("observation-v1")) -> VisualArtifact:
    return VisualArtifact.from_png(
        observation_identity=observation_identity,
        renderer_identity="JIANGHE_VISUAL_RENDERER_V0_1",
        renderer_config_identity=identity("renderer-config-v1"),
        content=b"\x89PNG\r\n\x1a\nsynthetic",
    )


@lru_cache(maxsize=1)
def integrated_visual() -> VisualArtifact:
    return VisualArtifact.from_canonical_observation(
        observation=observation(),
        renderer=JiangheVisualRenderer(),
    )


def structured(observation_identity: str = identity("observation-v1")) -> StructuredInputArtifact:
    return StructuredInputArtifact.from_payload(
        observation_identity=observation_identity,
        schema_identity=identity("JIANGHE_OBSERVATION_V0_1"),
        payload={"observation_identity": observation_identity, "bars": [{"close": "100"}]},
    )


def selector(
    binding: VersionBinding = VersionBinding.MUTABLE_ALIAS_CANDIDATE_ONLY,
) -> RequestedModelSelectorIdentity:
    return RequestedModelSelectorIdentity(
        provider().identity,
        "candidate-alias" if binding is not VersionBinding.EXACT_SNAPSHOT_PINNED else "candidate-model",
        binding,
        ModelDriftPolicy.ALIAS_MAY_DRIFT
        if binding is not VersionBinding.EXACT_SNAPSHOT_PINNED
        else ModelDriftPolicy.EXACT_SNAPSHOT_REQUIRED,
        None if binding is not VersionBinding.EXACT_SNAPSHOT_PINNED else "snapshot-20260823",
    )


def request(
    *,
    track: FidelityTrack = FidelityTrack.DUAL_INPUT,
    requested_selector: RequestedModelSelectorIdentity | None = None,
) -> JiangheModelRequest:
    provider_identity = provider()
    selected = requested_selector or RequestedModelSelectorIdentity(
        provider_identity.identity,
        "candidate-alias",
        VersionBinding.MUTABLE_ALIAS_CANDIDATE_ONLY,
        ModelDriftPolicy.ALIAS_MAY_DRIFT,
    )
    return JiangheModelRequest(
        provider_identity=provider_identity,
        requested_model_selector=selected,
        capability_declaration=capability(provider_identity),
        invocation_config=InvocationConfig(inference_parameters=(("temperature", "0"),)),
        system_prompt=PromptArtifact("SYSTEM", "system"),
        decision_prompt=PromptArtifact("DECISION", "decision"),
        prompt_package_identity=identity("prompt-package-v1"),
        context_selection_policy_identity=identity("context-policy-v1"),
        response_schema_identity=RESPONSE_SCHEMA_IDENTITY,
        runtime_normalizer_identity=NORMALIZER_IDENTITY,
        evaluation_extractor_identity=EVALUATION_EXTRACTOR_IDENTITY,
        observation_identity=observation().identity.identity,
        observation_available_at=T0,
        model_request_at=T1,
        fidelity_track=track,
        visual_artifact=integrated_visual()
        if track in (FidelityTrack.VISUAL, FidelityTrack.DUAL_INPUT)
        else None,
        structured_input=structured(observation().identity.identity)
        if track in (FidelityTrack.STRUCTURED, FidelityTrack.DUAL_INPUT)
        else None,
    )


def output_text() -> str:
    return json.dumps({
        "schema_version": "JIANGHE_RUNTIME_RESPONSE_V0_1",
        "family": "NONE",
        "action": "WAIT",
        "direction": "NONE",
        "attention_mode": "SCAN",
        "decision_state": "TRIGGER_NOT_READY",
        "rationale": "没有来源支持的触发。",
        "declared_unknown": [],
        "principle_references": ["JH-PRINC-002"],
        "source_references": ["JH-CLAIM-001"],
        "numeric_claims": [],
    }, ensure_ascii=False)


def response_payload(*, resolved_model_id: str = "candidate-model-2026-08-23") -> dict[str, object]:
    return {
        "provider": "CANDIDATE_PROVIDER",
        "resolved_model_id": resolved_model_id,
        "resolved_version_or_snapshot": "snapshot-20260823",
        "response_id": "response-001",
        "output_text": output_text(),
        "usage_metadata": {"input_tokens": 12, "output_tokens": 6, "total_tokens": 18},
    }


class JiangheModelProviderTests(unittest.TestCase):
    def test_integrated_visual_renderer_bridge_preserves_exact_manifest_provenance(self):
        canonical = observation()
        renderer = JiangheVisualRenderer()
        spec = VisualObservationSpec(
            product=canonical.identity.product,
            concrete_contract=canonical.identity.concrete_contract,
            as_of=canonical.identity.decision_time,
            panels=panels_from_observation_bars(canonical.bars),
        )
        rendered = renderer.render(spec)
        artifact = VisualArtifact.from_canonical_observation(
            observation=canonical,
            renderer=renderer,
        )
        self.assertTrue(artifact.integrated_renderer_verified)
        self.assertEqual(artifact.content, rendered.png_bytes)
        self.assertEqual(artifact.mime_type, "image/png")
        self.assertEqual(
            artifact.visual_observation_identity,
            rendered.input_observation_identity,
        )
        self.assertEqual(
            artifact.renderer_config_identity,
            rendered.renderer_config_identity,
        )
        self.assertEqual(
            artifact.visual_artifact_identity,
            rendered.visual_artifact_identity,
        )

    def test_dual_input_requires_same_canonical_observation_identity(self):
        provider_identity = provider()
        visual = VisualArtifact.from_png(
            observation_identity=identity("observation-v1"),
            renderer_identity="JIANGHE_VISUAL_RENDERER_V0_1",
            renderer_config_identity=identity("renderer-config-v1"),
            content=b"\x89PNG\r\n\x1a\nsynthetic",
        )
        structured = StructuredInputArtifact.from_payload(
            observation_identity=identity("observation-v2"),
            schema_identity=identity("JIANGHE_OBSERVATION_V0_1"),
            payload={
                "observation_identity": identity("observation-v2"),
                "bars": [{"close": "100"}],
            },
        )
        with self.assertRaises(ValueError):
            JiangheModelRequest(
                provider_identity=provider_identity,
                requested_model_selector=RequestedModelSelectorIdentity(
                    provider_identity.identity,
                    "candidate-alias",
                    VersionBinding.MUTABLE_ALIAS_CANDIDATE_ONLY,
                    ModelDriftPolicy.ALIAS_MAY_DRIFT,
                ),
                capability_declaration=capability(provider_identity),
                invocation_config=InvocationConfig(),
                system_prompt=PromptArtifact("SYSTEM", "system"),
                decision_prompt=PromptArtifact("DECISION", "decision"),
                prompt_package_identity=identity("prompt-package-v1"),
                context_selection_policy_identity=identity("context-policy-v1"),
                response_schema_identity=RESPONSE_SCHEMA_IDENTITY,
                runtime_normalizer_identity=NORMALIZER_IDENTITY,
                evaluation_extractor_identity=EVALUATION_EXTRACTOR_IDENTITY,
                observation_identity=identity("observation-v1"),
                observation_available_at=T0,
                model_request_at=T1,
                fidelity_track=FidelityTrack.DUAL_INPUT,
                visual_artifact=visual,
                structured_input=structured,
            )

    def test_valid_dual_input_packages_visual_and_structured_provenance(self):
        model_request = request()
        payload = model_request.build_transport_payload()
        visual_input = next(item for item in payload["inputs"] if item["type"] == "visual_artifact")
        structured_input = next(item for item in payload["inputs"] if item["type"] == "structured_input")
        self.assertEqual(visual_input["mime_type"], "image/png")
        self.assertEqual(visual_input["observation_identity"], observation().identity.identity)
        self.assertEqual(structured_input["observation_identity"], observation().identity.identity)
        self.assertEqual(
            visual_input["renderer_config_identity"], integrated_visual().renderer_config_identity
        )

    def test_visual_request_rejects_unverified_manual_renderer_provenance(self):
        with self.assertRaises(ValueError):
            replace(
                request(track=FidelityTrack.VISUAL),
                visual_artifact=visual(observation().identity.identity),
            )

    def test_artifact_compound_identities_are_recomputed_and_forgery_is_rejected(self):
        valid = visual()
        with self.assertRaises(ValueError):
            VisualArtifact.from_png(
                observation_identity=valid.observation_identity,
                renderer_identity=valid.renderer_identity,
                renderer_config_identity=valid.renderer_config_identity,
                content=valid.content,
                declared_visual_artifact_identity="forged",
            )
        valid_structured = structured()
        with self.assertRaises(ValueError):
            StructuredInputArtifact.from_payload(
                observation_identity=valid_structured.observation_identity,
                schema_identity=valid_structured.schema_identity,
                payload=valid_structured.payload,
                declared_artifact_identity="forged",
            )

    def test_requested_alias_and_resolved_provider_model_are_separate_identities(self):
        model_request = request()
        evidence = CandidateProviderAdapter(model_request.capability_declaration).parse_mocked_response(
            request=model_request,
            raw_provider_payload=response_payload(resolved_model_id="resolved-model-snapshot-name"),
            model_response_at=T2,
            normalized_decision_at=T3,
            normalizer=JiangheResponseNormalizer(),
        )
        self.assertEqual(evidence.requested_model_selector.selector, "candidate-alias")
        self.assertEqual(evidence.resolved_model.resolved_model_id, "resolved-model-snapshot-name")
        self.assertNotEqual(
            evidence.requested_model_selector.identity,
            evidence.resolved_model.identity,
        )

    def test_exact_snapshot_binding_rejects_provider_resolution_drift(self):
        provider_identity = provider()
        pinned = RequestedModelSelectorIdentity(
            provider_identity.identity,
            "candidate-model",
            VersionBinding.EXACT_SNAPSHOT_PINNED,
            ModelDriftPolicy.EXACT_SNAPSHOT_REQUIRED,
            "snapshot-20260823",
        )
        model_request = request(requested_selector=pinned)
        with self.assertRaises(ValueError):
            CandidateProviderAdapter(model_request.capability_declaration).parse_mocked_response(
                request=model_request,
                raw_provider_payload=response_payload(resolved_model_id="different-model"),
                model_response_at=T2,
                normalized_decision_at=T3,
                normalizer=JiangheResponseNormalizer(),
            )

    def test_capability_separates_structured_input_from_structured_output(self):
        declaration = capability()
        self.assertTrue(declaration.supports_structured_input)
        self.assertTrue(declaration.supports_structured_output)
        with self.assertRaises(ValueError):
            replace(declaration, supports_structured_input=False)
        changed_surface = replace(
            declaration,
            provider_identity=replace(
                declaration.provider_identity,
                endpoint_semantics_identity="endpoint-semantics-v2",
            ),
        )
        self.assertNotEqual(declaration.identity, changed_surface.identity)

    def test_request_binds_context_response_schema_and_runtime_normalizer(self):
        model_request = request()
        payload = model_request.build_transport_payload()
        self.assertEqual(
            payload["context_selection_policy_identity"], identity("context-policy-v1")
        )
        self.assertEqual(payload["response_schema_identity"], RESPONSE_SCHEMA_IDENTITY)
        self.assertEqual(payload["runtime_normalizer_identity"], NORMALIZER_IDENTITY)
        self.assertNotEqual(
            model_request.identity,
            replace(
                model_request,
                context_selection_policy_identity=identity("context-policy-v2"),
            ).identity,
        )

    def test_response_evidence_identity_binds_usage_timing_raw_and_resolved_model(self):
        model_request = request()
        adapter = CandidateProviderAdapter(model_request.capability_declaration)
        first = adapter.parse_mocked_response(
            request=model_request,
            raw_provider_payload=response_payload(),
            model_response_at=T2,
            normalized_decision_at=T3,
            normalizer=JiangheResponseNormalizer(),
        )
        repeated = adapter.parse_mocked_response(
            request=model_request,
            raw_provider_payload=response_payload(),
            model_response_at=T2,
            normalized_decision_at=T3,
            normalizer=JiangheResponseNormalizer(),
        )
        changed_payload = response_payload()
        changed_payload["usage_metadata"] = {"input_tokens": 13, "output_tokens": 6, "total_tokens": 19}
        changed = adapter.parse_mocked_response(
            request=model_request,
            raw_provider_payload=changed_payload,
            model_response_at=T2,
            normalized_decision_at=T3,
            normalizer=JiangheResponseNormalizer(),
        )
        self.assertEqual(first.identity, repeated.identity)
        self.assertNotEqual(first.identity, changed.identity)
        self.assertEqual(first.timing.latency_ms, 250)

    def test_provider_evidence_maps_losslessly_to_latest_input_evidence(self):
        model_request = request()
        adapter = CandidateProviderAdapter(model_request.capability_declaration)
        response_evidence = adapter.parse_mocked_response(
            request=model_request,
            raw_provider_payload=response_payload(),
            model_response_at=T2,
            normalized_decision_at=T3,
            normalizer=JiangheResponseNormalizer(),
        )
        evidence = model_request.to_input_evidence(response_evidence)
        reparsed = parse_input_evidence(asdict(evidence))
        self.assertEqual(reparsed.observation_identity, model_request.observation_identity)
        self.assertEqual(
            reparsed.visual_artifact_identity,
            model_request.visual_artifact.visual_artifact_identity,
        )
        self.assertEqual(
            reparsed.renderer_config_identity,
            model_request.visual_artifact.renderer_config_identity,
        )
        self.assertEqual(
            reparsed.structured_input_identity,
            model_request.structured_input.artifact_identity,
        )
        self.assertEqual(reparsed.provider_invocation_identity, model_request.identity)
        self.assertEqual(reparsed.provider_response_identity, response_evidence.identity)
        self.assertEqual(reparsed.normalizer_identity, NORMALIZER_IDENTITY)

    def test_malformed_provider_response_becomes_non_scoreable_evaluator_record(self):
        model_request = request()
        adapter = CandidateProviderAdapter(model_request.capability_declaration)
        decision = JiangheResponseNormalizer().normalize(output_text())
        judgment = EvaluatorSideJudgment(decision.identity, (), ())
        result = adapter.build_mocked_evaluation_record(
            request=model_request,
            raw_provider_payload={"provider": "CANDIDATE_PROVIDER"},
            model_response_at=T2,
            normalized_decision_at=T3,
            normalizer=JiangheResponseNormalizer(),
            evaluator_judgment=judgment,
            record_id="provider-failure-record",
            candidate_label="candidate-provider",
            corpus_id="JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1",
            fixture_id="JH-FIX-A-001",
        )
        self.assertFalse(result.record["call_success"])
        self.assertIsNone(result.response_evidence)
        self.assertTrue(result.failure_reason)
        report = evaluate_response_records(load_corpus(), [result.record])
        self.assertEqual(report["processing_status"], PROCESSING_ERROR)
        self.assertEqual(report["admitted_record_total"], 0)
        self.assertEqual(len(report["failed_call_records"]), 1)

    def test_successful_provider_record_requires_evaluator_side_judgment(self):
        model_request = request()
        adapter = CandidateProviderAdapter(model_request.capability_declaration)
        decision = JiangheResponseNormalizer().normalize(output_text())
        judgment = EvaluatorSideJudgment(decision.identity, (), ())
        result = adapter.build_mocked_evaluation_record(
            request=model_request,
            raw_provider_payload=response_payload(),
            model_response_at=T2,
            normalized_decision_at=T3,
            normalizer=JiangheResponseNormalizer(),
            evaluator_judgment=judgment,
            record_id="provider-success-record",
            candidate_label="candidate-provider",
            corpus_id="JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1",
            fixture_id="JH-FIX-A-001",
        )
        self.assertTrue(result.record["call_success"])
        self.assertIsNotNone(result.response_evidence)
        report = evaluate_response_records(load_corpus(), [result.record])
        self.assertEqual(report["admitted_record_total"], 1)

        with self.assertRaises(TypeError):
            adapter.build_mocked_evaluation_record(
                request=model_request,
                raw_provider_payload=response_payload(),
                model_response_at=T2,
                normalized_decision_at=T3,
                normalizer=JiangheResponseNormalizer(),
                evaluator_judgment=None,
                record_id="provider-invalid-judgment",
                candidate_label="candidate-provider",
                corpus_id="JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1",
                fixture_id="JH-FIX-A-001",
            )

    def test_visual_mime_png_signature_and_hash_fail_closed(self):
        with self.assertRaises(ValueError):
            VisualArtifact(
                observation_identity=identity("observation-v1"),
                renderer_identity="renderer-v1",
                renderer_config_identity=identity("config-v1"),
                content=b"not-png",
                mime_type="image/jpeg",
            )
        with self.assertRaises(ValueError):
            VisualArtifact.from_png(
                observation_identity=identity("observation-v1"),
                renderer_identity="renderer-v1",
                renderer_config_identity=identity("config-v1"),
                content=b"\x89PNG\r\n\x1a\nbytes",
                declared_png_sha256="forged",
            )

    def test_live_invocation_and_outcome_fields_fail_closed(self):
        model_request = request()
        adapter = CandidateProviderAdapter(model_request.capability_declaration)
        with self.assertRaises(LiveInvocationDisabledError):
            adapter.invoke(model_request)
        with self.assertRaises(ValueError):
            StructuredInputArtifact.from_payload(
                observation_identity=identity("observation-v1"),
                schema_identity=identity("schema-v1"),
                payload={
                    "observation_identity": identity("observation-v1"),
                    "nested": {"pnl": "forbidden"},
                },
            )
        self.assertFalse({"pnl", "outcome", "profit", "sharpe"} & contract_field_names())

    def test_timing_and_resolved_model_require_strict_values(self):
        with self.assertRaises(ValueError):
            InvocationTiming(T0, T2, T1, T3)
        with self.assertRaises(ValueError):
            ResolvedProviderModelIdentity(provider().identity, "model", "")


if __name__ == "__main__":
    unittest.main()

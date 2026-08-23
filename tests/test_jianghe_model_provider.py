"""江河真实模型 Provider 预备合同的纯模拟测试。

所有测试只构造内存请求/回复，不读取环境变量、不使用 SDK、不建立网络连接。
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import socket
import unittest
from unittest.mock import patch

from src.jianghe_model_provider import (
    CandidateProviderAdapter,
    CandidateStatus,
    CapabilityDeclaration,
    FidelityTrack,
    InvocationConfig,
    InvocationTiming,
    JiangheModelRequest,
    JiangheModelResponse,
    LiveInvocationDisabledError,
    ModelDriftPolicy,
    ModelIdentity,
    PromptArtifact,
    ProviderIdentity,
    StructuredInputArtifact,
    VersionBinding,
    VisualArtifact,
    contract_field_names,
)


UTC = timezone.utc
T0 = datetime(2026, 8, 23, 9, 0, tzinfo=UTC)
T1 = T0 + timedelta(seconds=1)
T2 = T1 + timedelta(milliseconds=250)
T3 = T2 + timedelta(milliseconds=10)


def canonical_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


def make_provider() -> ProviderIdentity:
    return ProviderIdentity(
        provider_id="CANDIDATE_PROVIDER",
        api_surface="CANDIDATE_REST",
        official_documentation_urls=("https://example.invalid/provider-docs",),
    )


def make_capability(provider: ProviderIdentity | None = None) -> CapabilityDeclaration:
    return CapabilityDeclaration(
        provider_identity=provider or make_provider(),
        declared_at=T0,
        supported_tracks=(
            FidelityTrack.SEMANTIC,
            FidelityTrack.VISUAL,
            FidelityTrack.STRUCTURED,
            FidelityTrack.DUAL_INPUT,
            FidelityTrack.OPERATIONAL_PROVIDER,
        ),
        supports_image_input=True,
        supports_structured_json_output=True,
        supports_response_model_identity=True,
        supports_usage_metadata=True,
        supports_environment_credential=True,
        repeatability_controls=("temperature",),
        model_drift_policy=ModelDriftPolicy.ALIAS_MAY_DRIFT,
    )


def make_visual() -> VisualArtifact:
    content = b"synthetic-kline-image-bytes"
    return VisualArtifact(
        identity="chart-artifact-v1",
        renderer_identity="JIANGHE_CHART_RENDERER_V0_1",
        mime_type="image/png",
        content=content,
        content_sha256=sha256(content).hexdigest(),
        available_at=T0,
    )


def make_structured() -> StructuredInputArtifact:
    payload = {
        "observation_identity": "observation-v1",
        "bars": [{"timeframe": "1m", "is_closed": True, "close": "100"}],
    }
    return StructuredInputArtifact(
        identity="structured-observation-v1",
        schema_identity="JIANGHE_OBSERVATION_V0_1",
        payload=payload,
        content_sha256=canonical_hash(payload),
        available_at=T0,
    )


def make_request(
    track: FidelityTrack = FidelityTrack.SEMANTIC,
    *,
    visual: VisualArtifact | None = None,
    structured: StructuredInputArtifact | None = None,
    model: ModelIdentity | None = None,
    config: InvocationConfig | None = None,
) -> JiangheModelRequest:
    provider = make_provider()
    return JiangheModelRequest(
        provider_identity=provider,
        model_identity=model or ModelIdentity("candidate-model", "snapshot-20260823", VersionBinding.PINNED),
        capability_declaration=make_capability(provider),
        invocation_config=config or InvocationConfig(
            inference_parameters=(("temperature", "0"),),
            credential_environment_variable="CANDIDATE_PROVIDER_API_KEY",
        ),
        system_prompt=PromptArtifact("system-prompt-v1", "只根据已提供的观察回答。"),
        decision_prompt=PromptArtifact("decision-prompt-v1", "输出受约束的 JSON 决策。"),
        observation_identity="observation-v1",
        observation_available_at=T0,
        model_request_at=T1,
        fidelity_track=track,
        visual_artifact=visual,
        structured_input=structured,
    )


def mocked_payload(request: JiangheModelRequest) -> dict[str, object]:
    return {
        "provider": request.provider_identity.provider_id,
        "model_id": request.model_identity.model_id,
        "version_or_snapshot": request.model_identity.version_or_snapshot,
        "response_id": "mock-response-001",
        "normalized_response": {"action": "WAIT", "family": "NONE", "reason": "trigger_not_ready"},
        "usage_metadata": {"input_tokens": 12, "output_tokens": 6, "total_tokens": 18},
    }


class CandidateProviderContractTests(unittest.TestCase):
    def test_no_network_default_even_when_socket_is_guarded(self) -> None:
        request = make_request()
        adapter = CandidateProviderAdapter(request.capability_declaration)
        self.assertTrue(adapter.live_invocation_disabled)
        with patch.object(socket, "create_connection", side_effect=AssertionError("测试不得联网")):
            with self.assertRaises(LiveInvocationDisabledError):
                adapter.invoke(request)

    def test_capability_declaration_stays_candidate_and_covers_tracks(self) -> None:
        declaration = make_capability()
        self.assertEqual(declaration.status, CandidateStatus.CANDIDATE)
        self.assertIn(FidelityTrack.VISUAL, declaration.supported_tracks)
        self.assertIn(FidelityTrack.STRUCTURED, declaration.supported_tracks)
        self.assertIn(FidelityTrack.DUAL_INPUT, declaration.supported_tracks)
        self.assertTrue(declaration.identity)
        with self.assertRaises(ValueError):
            CapabilityDeclaration(
                provider_identity=make_provider(),
                declared_at=T0,
                supported_tracks=(FidelityTrack.DUAL_INPUT,),
                supports_image_input=False,
                supports_structured_json_output=True,
                supports_response_model_identity=True,
                supports_usage_metadata=True,
                supports_environment_credential=True,
                repeatability_controls=(),
                model_drift_policy=ModelDriftPolicy.PROVIDER_UNDOCUMENTED,
            )

    def test_version_identity_is_bound_and_missing_version_fails_closed(self) -> None:
        request = make_request()
        self.assertEqual(request.model_identity.version_or_snapshot, "snapshot-20260823")
        with self.assertRaises(ValueError):
            make_request(model=ModelIdentity("candidate-model"))
        with self.assertRaises(ValueError):
            ModelIdentity("candidate-model", None, VersionBinding.PINNED)

    def test_image_request_packaging_binds_identity_hash_and_bytes(self) -> None:
        request = make_request(FidelityTrack.VISUAL, visual=make_visual())
        payload = CandidateProviderAdapter(request.capability_declaration).build_request_payload(request)
        visual_inputs = [item for item in payload["inputs"] if item["type"] == "visual_artifact"]
        self.assertEqual(len(visual_inputs), 1)
        self.assertEqual(visual_inputs[0]["identity"], "chart-artifact-v1")
        self.assertEqual(visual_inputs[0]["content_sha256"], request.visual_artifact.content_sha256)
        self.assertTrue(visual_inputs[0]["content_base64"])

    def test_structured_input_packaging_binds_schema_and_observation(self) -> None:
        structured = make_structured()
        request = make_request(FidelityTrack.STRUCTURED, structured=structured)
        payload = request.build_transport_payload()
        structured_inputs = [item for item in payload["inputs"] if item["type"] == "structured_input"]
        self.assertEqual(structured_inputs[0]["schema_identity"], "JIANGHE_OBSERVATION_V0_1")
        self.assertEqual(structured_inputs[0]["identity"], structured.identity)
        self.assertEqual(payload["observation"]["identity"], "observation-v1")

    def test_dual_input_requires_and_packages_both_artifacts(self) -> None:
        with self.assertRaises(ValueError):
            make_request(FidelityTrack.DUAL_INPUT, visual=make_visual())
        request = make_request(FidelityTrack.DUAL_INPUT, visual=make_visual(), structured=make_structured())
        payload = request.build_transport_payload()
        self.assertEqual({item["type"] for item in payload["inputs"]}, {
            "semantic_prompts", "visual_artifact", "structured_input",
        })

    def test_timing_is_monotonic_and_latency_is_captured(self) -> None:
        timing = InvocationTiming(T0, T1, T2, T3)
        self.assertEqual(timing.latency_ms, 250)
        with self.assertRaises(ValueError):
            InvocationTiming(T0, T2, T1, T3)

    def test_mocked_response_captures_raw_hash_usage_and_latency(self) -> None:
        request = make_request()
        response = CandidateProviderAdapter(request.capability_declaration).parse_mocked_response(
            request=request,
            raw_provider_payload=mocked_payload(request),
            model_response_at=T2,
            normalized_decision_at=T3,
        )
        self.assertEqual(response.raw_response_sha256, sha256(response.raw_response.encode("utf-8")).hexdigest())
        self.assertEqual(response.usage_metadata["total_tokens"], 18)
        self.assertEqual(response.timing.latency_ms, 250)
        self.assertEqual(response.model_identity.identity, request.model_identity.identity)

    def test_malformed_provider_response_fails_closed(self) -> None:
        request = make_request()
        malformed = mocked_payload(request)
        malformed.pop("normalized_response")
        adapter = CandidateProviderAdapter(request.capability_declaration)
        with self.assertRaises(ValueError):
            adapter.parse_mocked_response(
                request=request,
                raw_provider_payload=malformed,
                model_response_at=T2,
                normalized_decision_at=T3,
            )

    def test_missing_response_version_fails_closed_when_required(self) -> None:
        request = make_request()
        payload = mocked_payload(request)
        payload.pop("version_or_snapshot")
        with self.assertRaises(ValueError):
            CandidateProviderAdapter(request.capability_declaration).parse_mocked_response(
                request=request,
                raw_provider_payload=payload,
                model_response_at=T2,
                normalized_decision_at=T3,
            )

    def test_outcome_fields_are_not_part_of_contract_or_normalized_response(self) -> None:
        self.assertFalse({"outcome", "pnl", "profit", "sharpe"} & contract_field_names())
        payload = {"pnl": "forbidden"}
        with self.assertRaises(ValueError):
            StructuredInputArtifact(
                identity="invalid-structured",
                schema_identity="JIANGHE_OBSERVATION_V0_1",
                payload=payload,
                content_sha256=canonical_hash(payload),
                available_at=T0,
            )
        with self.assertRaises(ValueError):
            JiangheModelResponse(
                request_identity="request-v1",
                provider_identity=make_provider(),
                model_identity=ModelIdentity("candidate-model", "snapshot-20260823", VersionBinding.PINNED),
                provider_response_id="response-v1",
                raw_response="{}",
                normalized_response={"outcome": "forbidden"},
                usage_metadata={"input_tokens": 1},
                timing=InvocationTiming(T0, T1, T2, T3),
            )
        request = make_request()
        invalid_raw_payload = mocked_payload(request)
        invalid_raw_payload["pnl"] = "forbidden"
        with self.assertRaises(ValueError):
            CandidateProviderAdapter(request.capability_declaration).parse_mocked_response(
                request=request,
                raw_provider_payload=invalid_raw_payload,
                model_response_at=T2,
                normalized_decision_at=T3,
            )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

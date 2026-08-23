"""Focused adversarial tests for the frozen pre-spend repair package.

No network is used. Provider transports are exercised only through injected
fake HTTP functions and synthetic authorization objects.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import json
import os
import unittest

from src.jianghe_ai_trader import JiangheObservation, ObservationBar, ObservationIdentity
from src.jianghe_prespend_runtime import (
    BudgetGuardError,
    CanonicalStructuredObservationArtifact,
    CnyBudgetLedger,
    DEEPSEEK_VISION_SPEC,
    DomesticProviderTransport,
    FxAuthority,
    HARD_PROJECT_CAP_CNY,
    HttpResponse,
    IMPLEMENTATION_TARGET_SPECS,
    InvocationBounds,
    KIMI_K3_SPEC,
    MINIMAX_M3_SPEC,
    PaidCallAuthorization,
    PaidCallNotAuthorizedError,
    RateCard,
    SelectedContextDocument,
    SelectedJiangheContextArtifact,
    SpendEligibleJiangheRequest,
    VisualInputArtifact,
)


UTC = timezone.utc
NOW = datetime(2026, 8, 24, 1, 0, tzinfo=UTC)


def _observation() -> JiangheObservation:
    bar = ObservationBar(
        timeframe="5m",
        open_time=datetime(2024, 1, 2, 1, 0, tzinfo=UTC),
        close_time=datetime(2024, 1, 2, 1, 5, tzinfo=UTC),
        available_at=datetime(2024, 1, 2, 1, 5, tzinfo=UTC),
        open_price="100", high_price="105", low_price="99", close_price="104",
        volume="1234", is_closed=True,
    )
    identity = ObservationIdentity(
        decision_time=datetime(2024, 1, 2, 1, 5, tzinfo=UTC),
        exchange_time=datetime(2024, 1, 2, 1, 5, tzinfo=UTC),
        product="cu", concrete_contract="cu2403", mapping_identity="mapping-v1",
        session_identity="session-v1",
    )
    return JiangheObservation(
        identity=identity, bars=(bar,), visible_metadata=(("session", "DAY"),)
    )


def _context(selected: str = "位置优先于触发。") -> SelectedJiangheContextArtifact:
    repo_content = "# current authority\n位置优先于触发。\n没有触发就等待。\n"
    doc = SelectedContextDocument.from_repository_document(
        "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md", repo_content, selected
    )
    policy = hashlib.sha256(b"context-policy-v1").hexdigest()
    return SelectedJiangheContextArtifact(policy, (doc,))


def _request(selected: str = "位置优先于触发。") -> SpendEligibleJiangheRequest:
    observation = _observation()
    structured = CanonicalStructuredObservationArtifact.from_observation(observation)
    visual = VisualInputArtifact(
        source_observation_identity=observation.identity.identity,
        renderer_identity="renderer-v1",
        png_bytes=b"\x89PNG\r\n\x1a\nsynthetic-test-only",
    )
    schema = {
        "type": "object", "additionalProperties": False,
        "required": ["family", "action"],
        "properties": {"family": {"type": "string"}, "action": {"type": "string"}},
    }
    return SpendEligibleJiangheRequest(
        system_prompt="只根据江河知识和当前观察回答。",
        decision_prompt="给出严格 JSON。",
        response_schema=schema,
        context=_context(selected), structured_observation=structured,
        visuals=(visual,), max_output_tokens=200,
    )


def _rate(spec, *, currency="CNY", input_price="2", output_price="4"):
    return RateCard(
        provider_id=spec.provider_id, model_id=spec.model_id, currency=currency,
        input_per_million=Decimal(input_price), output_per_million=Decimal(output_price),
        image_tokens_billed_as_input=True,
        authority_uri="https://example.invalid/first-party-rate-card-snapshot",
        effective_at=NOW - timedelta(hours=1), expires_at=NOW + timedelta(hours=1),
    )


class SelectedContextTests(unittest.TestCase):
    def test_selected_material_must_be_exact_repo_substring_and_allowlisted(self):
        with self.assertRaises(ValueError):
            SelectedContextDocument.from_repository_document("docs/other.md", "abc", "abc")
        with self.assertRaises(ValueError):
            SelectedContextDocument.from_repository_document(
                "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md", "真实内容", "不存在的片段"
            )

    def test_request_identity_changes_when_actual_selected_context_changes(self):
        first = _request("位置优先于触发。")
        second = _request("没有触发就等待。")
        self.assertNotEqual(first.context.identity, second.context.identity)
        self.assertNotEqual(first.identity, second.identity)
        self.assertIn("位置优先于触发。", first.common_model_text())


class StructuredObservationTests(unittest.TestCase):
    def test_artifact_can_only_be_generated_from_typed_observation(self):
        with self.assertRaises(TypeError):
            CanonicalStructuredObservationArtifact.from_observation({"bars": []})  # type: ignore[arg-type]

    def test_closed_world_payload_is_deterministic_and_content_bound(self):
        observation = _observation()
        first = CanonicalStructuredObservationArtifact.from_observation(observation)
        second = CanonicalStructuredObservationArtifact.from_observation(observation)
        self.assertEqual(first.serialized_json, second.serialized_json)
        self.assertEqual(first.identity, second.identity)
        payload = json.loads(first.serialized_json)
        self.assertEqual(payload["observation_identity"], observation.identity.identity)
        self.assertEqual(
            set(payload),
            {"artifact_schema_version", "source_observation_schema_version", "observation_identity",
             "observation", "bars", "positions", "active_order_ids", "visible_metadata"},
        )
        serialized_lower = first.serialized_json.lower()
        self.assertNotIn('"pnl"', serialized_lower)
        self.assertNotIn('"future_price"', serialized_lower)


class TransportPayloadTests(unittest.TestCase):
    def test_all_owner_confirmed_providers_send_same_material(self):
        req = _request()
        for spec in IMPLEMENTATION_TARGET_SPECS:
            with self.subTest(provider=spec.provider_id):
                payload = DomesticProviderTransport(spec).build_payload(req)
                encoded = json.dumps(payload, ensure_ascii=False)
                self.assertIn("位置优先于触发。", encoded)
                self.assertIn(req.structured_observation.source_observation_identity, encoded)
                self.assertIn("data:image/png;base64,", encoded)
                self.assertEqual(payload["model"], spec.model_id)

    def test_invoke_fails_before_network_without_owner_paid_authorization(self):
        calls = []
        def fake_post(url, headers, body, timeout):
            calls.append(url)
            raise AssertionError("network seam must not be reached")
        transport = DomesticProviderTransport(KIMI_K3_SPEC, http_post=fake_post)
        with self.assertRaises(PaidCallNotAuthorizedError):
            transport.invoke(
                _request(), authorization=None, budget=CnyBudgetLedger(),
                rate_card=_rate(KIMI_K3_SPEC), bounds=InvocationBounds(1000, 500, 200),
                fx=None, now=NOW,
            )
        self.assertEqual(calls, [])

    def test_fake_authorized_transport_captures_model_request_usage_without_secret_evidence(self):
        seen = []
        def fake_post(url, headers, body, timeout):
            seen.append((url, dict(headers), json.loads(body.decode("utf-8"))))
            response = {
                "id": "provider-request-1", "model": "kimi-k3-resolved-test",
                "choices": [{"message": {"content": '{"family":"NONE","action":"WAIT"}'}}],
                "usage": {"prompt_tokens": 100, "completion_tokens": 20},
            }
            return HttpResponse(200, {}, json.dumps(response).encode("utf-8"))
        previous = os.environ.get("MOONSHOT_API_KEY")
        os.environ["MOONSHOT_API_KEY"] = "secret-test-key"
        try:
            transport = DomesticProviderTransport(KIMI_K3_SPEC, http_post=fake_post)
            ledger = CnyBudgetLedger()
            auth = PaidCallAuthorization(
                authorization_id="TEST_ONLY_SYNTHETIC_AUTH",
                authorization_evidence_sha256=hashlib.sha256(b"synthetic-auth").hexdigest(),
                provider_models=((KIMI_K3_SPEC.provider_id, KIMI_K3_SPEC.model_id),),
                hard_cap_cny=HARD_PROJECT_CAP_CNY, paid_calls_enabled=True,
            )
            evidence = transport.invoke(
                _request(), authorization=auth, budget=ledger,
                rate_card=_rate(KIMI_K3_SPEC), bounds=InvocationBounds(1500, 500, 200),
                fx=None, now=NOW,
            )
            self.assertEqual(len(seen), 1)
            self.assertEqual(seen[0][1]["Authorization"], "Bearer secret-test-key")
            self.assertEqual(evidence.requested_model_id, "kimi-k3")
            self.assertEqual(evidence.resolved_model_id, "kimi-k3-resolved-test")
            self.assertEqual(evidence.provider_request_id, "provider-request-1")
            self.assertEqual(evidence.usage.text_input_tokens, 100)
            self.assertNotIn("secret-test-key", repr(evidence))
            self.assertGreater(ledger.spent_cny, 0)
        finally:
            if previous is None:
                os.environ.pop("MOONSHOT_API_KEY", None)
            else:
                os.environ["MOONSHOT_API_KEY"] = previous


class SharedBudgetTests(unittest.TestCase):
    def test_hard_cap_cannot_be_raised_above_100(self):
        with self.assertRaises(BudgetGuardError):
            CnyBudgetLedger(Decimal("100.01"))

    def test_one_shared_ledger_requires_reconciliation_before_next_provider(self):
        ledger = CnyBudgetLedger()
        first = ledger.reserve(
            KIMI_K3_SPEC, _rate(KIMI_K3_SPEC), InvocationBounds(1000, 500, 200), fx=None, now=NOW
        )
        with self.assertRaises(BudgetGuardError):
            ledger.reserve(
                DEEPSEEK_VISION_SPEC, _rate(DEEPSEEK_VISION_SPEC),
                InvocationBounds(1000, 500, 200), fx=None, now=NOW,
            )
        ledger.reconcile(
            first.reservation_id, text_input_tokens=100, image_tokens=20, output_tokens=20,
            rate_card=_rate(KIMI_K3_SPEC), fx=None, now=NOW,
        )
        second = ledger.reserve(
            DEEPSEEK_VISION_SPEC, _rate(DEEPSEEK_VISION_SPEC),
            InvocationBounds(1000, 500, 200), fx=None, now=NOW,
        )
        self.assertEqual(second.provider_id, "DEEPSEEK")

    def test_usd_rate_card_requires_current_fx_authority(self):
        ledger = CnyBudgetLedger()
        usd = _rate(KIMI_K3_SPEC, currency="USD", input_price="3", output_price="15")
        with self.assertRaises(BudgetGuardError):
            ledger.reserve(KIMI_K3_SPEC, usd, InvocationBounds(1000, 500, 200), fx=None, now=NOW)
        fx = FxAuthority(
            usd_to_cny=Decimal("8"), authority_uri="https://example.invalid/fx-snapshot",
            effective_at=NOW - timedelta(hours=1), expires_at=NOW + timedelta(hours=1),
        )
        reservation = ledger.reserve(
            KIMI_K3_SPEC, usd, InvocationBounds(1000, 500, 200), fx=fx, now=NOW
        )
        self.assertEqual(reservation.fx_identity, fx.identity)

    def test_unknown_usage_consumes_full_reservation_before_next_call(self):
        ledger = CnyBudgetLedger()
        reservation = ledger.reserve(
            MINIMAX_M3_SPEC, _rate(MINIMAX_M3_SPEC), InvocationBounds(1000, 500, 200),
            fx=None, now=NOW,
        )
        reserved = reservation.reserved_cny
        ledger.consume_full_reservation_on_unknown_usage(reservation.reservation_id)
        self.assertEqual(ledger.spent_cny, reserved)
        self.assertEqual(ledger.remaining_cny, HARD_PROJECT_CAP_CNY - reserved)


if __name__ == "__main__":
    unittest.main()

"""Focused adversarial tests for frozen BSP-001..005 repair surfaces.

No real network is used. A positive transport path only runs with an injected fake
HTTP seam and a patched repository-authorization loader.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import json
import os
import unittest
from unittest.mock import patch

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
    ProviderTransportError,
    RateCard,
    SelectedContextDocument,
    SelectedJiangheContextArtifact,
    SpendEligibleJiangheRequest,
    VisualInputArtifact,
    current_context_selection_policy_identity,
    load_current_repository_rate_card,
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


def _context(fixture_id: str = "JH-FIX-A-001") -> SelectedJiangheContextArtifact:
    return SelectedJiangheContextArtifact.from_fixture_id(fixture_id)


def _request(fixture_id: str = "JH-FIX-A-001") -> SpendEligibleJiangheRequest:
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
        context=_context(fixture_id),
        structured_observation=structured,
        visuals=(visual,),
        max_output_tokens=200,
    )


def _rate(spec, *, currency="CNY", input_price="2", output_price="4"):
    return RateCard(
        provider_id=spec.provider_id, model_id=spec.model_id, currency=currency,
        input_per_million=Decimal(input_price), output_per_million=Decimal(output_price),
        image_tokens_billed_as_input=True,
        authority_uri="https://example.invalid/first-party-rate-card-snapshot",
        effective_at=NOW - timedelta(hours=1), expires_at=NOW + timedelta(hours=1),
    )


def _synthetic_auth(spec=KIMI_K3_SPEC) -> PaidCallAuthorization:
    return PaidCallAuthorization(
        authorization_id="TEST_ONLY_SYNTHETIC_AUTH",
        authorization_evidence_sha256=hashlib.sha256(b"synthetic-auth").hexdigest(),
        provider_models=((spec.provider_id, spec.model_id),),
        hard_cap_cny=HARD_PROJECT_CAP_CNY,
        paid_calls_enabled=True,
    )


class SelectedContextTests(unittest.TestCase):
    def test_fixture_selection_is_deterministic_exact_primary_material(self):
        first = _context("JH-FIX-A-001")
        again = _context("JH-FIX-A-001")
        second = _context("JH-FIX-A-002")
        self.assertEqual(first.identity, again.identity)
        self.assertEqual(first.to_payload(), again.to_payload())
        self.assertNotEqual(first.identity, second.identity)
        self.assertNotEqual(first.source_claim_ids, second.source_claim_ids)
        self.assertTrue(first.selection_basis_identity)
        for document in first.documents:
            self.assertTrue(document.repository_path.endswith("JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_5.jsonl"))
            record = json.loads(document.selected_text)
            self.assertIn(record["claim_id"], first.source_claim_ids)
            self.assertNotIn("fixture_id", record)

    def test_request_identity_changes_with_fixture_selected_context(self):
        first = _request("JH-FIX-A-001")
        second = _request("JH-FIX-A-002")
        self.assertNotEqual(first.context.identity, second.context.identity)
        self.assertNotEqual(first.identity, second.identity)
        self.assertIn("JH-CLM-006-SP01", first.common_model_text())

    def test_manual_unrelated_context_cannot_become_spend_eligible(self):
        doc = SelectedContextDocument.from_repository_authority(
            "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md", "UNKNOWN > GUESSING"
        )
        context = SelectedJiangheContextArtifact(current_context_selection_policy_identity(), (doc,))
        request = _request()
        with self.assertRaises(ValueError):
            SpendEligibleJiangheRequest(
                system_prompt=request.system_prompt,
                decision_prompt=request.decision_prompt,
                response_schema=request.response_schema,
                context=context,
                structured_observation=request.structured_observation,
                visuals=request.visuals,
                max_output_tokens=request.max_output_tokens,
            )

    def test_direct_context_forgery_under_real_path_is_rejected(self):
        with self.assertRaises(ValueError):
            SelectedContextDocument(
                repository_path="docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md",
                repository_content_sha256=hashlib.sha256(b"forged").hexdigest(),
                selected_text="UNKNOWN > GUESSING",
            )

    def test_arbitrary_context_policy_identity_is_rejected(self):
        doc = SelectedContextDocument.from_repository_authority(
            "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md", "UNKNOWN > GUESSING"
        )
        with self.assertRaises(ValueError):
            SelectedJiangheContextArtifact(hashlib.sha256(b"attacker-policy").hexdigest(), (doc,))


class StructuredObservationTests(unittest.TestCase):
    def test_artifact_can_only_be_generated_from_typed_observation(self):
        with self.assertRaises(TypeError):
            CanonicalStructuredObservationArtifact.from_observation({"bars": []})  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            CanonicalStructuredObservationArtifact(
                source_observation_identity="0" * 64,
                serialized_json="{}",
                schema_identity="1" * 64,
                identity="2" * 64,
            )

    def test_noncanonical_observation_schema_fails_closed(self):
        forged = replace(_observation(), schema_version="ATTACKER_SCHEMA_V9")
        with self.assertRaises(ValueError):
            CanonicalStructuredObservationArtifact.from_observation(forged)

    def test_closed_world_payload_is_deterministic_content_bound(self):
        observation = _observation()
        first = CanonicalStructuredObservationArtifact.from_observation(observation)
        second = CanonicalStructuredObservationArtifact.from_observation(observation)
        self.assertEqual(first.serialized_json, second.serialized_json)
        self.assertEqual(first.identity, second.identity)
        payload = first.payload()
        self.assertEqual(payload["observation_identity"], observation.identity.identity)
        self.assertEqual(
            set(payload),
            {"artifact_schema_version", "source_observation_schema_version", "observation_identity",
             "observation", "bars", "positions", "active_order_ids", "visible_metadata"},
        )

    def test_unknown_visible_metadata_is_rejected(self):
        base = _observation()
        forged = JiangheObservation(
            identity=ObservationIdentity(
                decision_time=base.identity.decision_time,
                exchange_time=base.identity.exchange_time,
                product=base.identity.product,
                concrete_contract=base.identity.concrete_contract,
                mapping_identity=base.identity.mapping_identity,
                session_identity=base.identity.session_identity,
            ),
            bars=base.bars,
            visible_metadata=(("note", "future outcome disguised as prose"),),
        )
        with self.assertRaises(ValueError):
            CanonicalStructuredObservationArtifact.from_observation(forged)


class TransportTests(unittest.TestCase):
    def test_all_implementation_targets_send_same_governed_material_and_disable_tools(self):
        request = _request()
        for spec in IMPLEMENTATION_TARGET_SPECS:
            with self.subTest(provider=spec.provider_id):
                payload = DomesticProviderTransport(spec).build_payload(request)
                encoded = json.dumps(payload, ensure_ascii=False)
                self.assertIn("JH-CLM-006-SP01", encoded)
                self.assertIn(request.structured_observation.source_observation_identity, encoded)
                self.assertIn("data:image/png;base64,", encoded)
                self.assertEqual(payload["model"], spec.model_id)
                self.assertEqual(payload["tools"], [])

    def test_fabricated_authorization_cannot_reach_network_without_repo_owner_authority(self):
        calls = []
        def fake_post(url, headers, body, timeout):
            calls.append(url)
            raise AssertionError("network seam must not be reached")
        transport = DomesticProviderTransport(KIMI_K3_SPEC, http_post=fake_post)
        auth = _synthetic_auth()
        with self.assertRaises(PaidCallNotAuthorizedError):
            transport.invoke(
                _request(), authorization=auth, budget=CnyBudgetLedger(),
                bounds=InvocationBounds(1, 1, 200), fx=None, now=NOW,
            )
        self.assertEqual(calls, [])

    def test_payload_bound_is_derived_from_exact_bytes_before_network(self):
        calls = []
        def fake_post(url, headers, body, timeout):
            calls.append(url)
            raise AssertionError("network seam must not be reached")
        request = _request()
        transport = DomesticProviderTransport(KIMI_K3_SPEC, http_post=fake_post)
        auth = _synthetic_auth()
        required = transport.conservative_text_input_token_bound(request)
        with patch("src.jianghe_prespend_runtime.load_owner_paid_call_authorization", return_value=auth):
            with self.assertRaises(BudgetGuardError):
                transport.invoke(
                    request, authorization=auth, budget=CnyBudgetLedger(),
                    bounds=InvocationBounds(required - 1, 1024, 200), fx=None, now=NOW,
                )
        self.assertEqual(calls, [])

    def test_fake_authorized_transport_preserves_raw_body_and_all_input_identities(self):
        seen = []
        response = {
            "id": "provider-request-1", "model": "kimi-k3-resolved-test",
            "choices": [{"message": {"content": '{"family":"NONE","action":"WAIT"}'}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 20},
        }
        raw_response = json.dumps(response, ensure_ascii=False)
        def fake_post(url, headers, body, timeout):
            seen.append((url, dict(headers), body))
            return HttpResponse(200, {}, raw_response.encode("utf-8"))
        previous = os.environ.get("MOONSHOT_API_KEY")
        os.environ["MOONSHOT_API_KEY"] = "secret-test-key"
        try:
            request = _request()
            transport = DomesticProviderTransport(KIMI_K3_SPEC, http_post=fake_post)
            auth = _synthetic_auth()
            ledger = CnyBudgetLedger()
            bounds = InvocationBounds(
                transport.conservative_text_input_token_bound(request), 1024, 200
            )
            with patch("src.jianghe_prespend_runtime.load_owner_paid_call_authorization", return_value=auth):
                evidence = transport.invoke(
                    request, authorization=auth, budget=ledger, bounds=bounds, fx=None, now=NOW,
                )
            self.assertEqual(len(seen), 1)
            self.assertEqual(seen[0][1]["Authorization"], "Bearer secret-test-key")
            self.assertEqual(evidence.raw_provider_response_body, raw_response)
            self.assertEqual(evidence.request_identity, request.identity)
            self.assertEqual(evidence.selected_context_identity, request.context.identity)
            self.assertEqual(evidence.structured_observation_identity, request.structured_observation.identity)
            self.assertEqual(evidence.visual_identities, tuple(item.identity for item in request.visuals))
            self.assertEqual(evidence.resolved_model_id, "kimi-k3-resolved-test")
            self.assertNotIn("secret-test-key", repr(evidence))
            self.assertGreater(ledger.spent_cny, 0)
        finally:
            if previous is None:
                os.environ.pop("MOONSHOT_API_KEY", None)
            else:
                os.environ["MOONSHOT_API_KEY"] = previous

    def test_missing_credential_cancels_before_network_without_fake_spend(self):
        previous = os.environ.pop("MOONSHOT_API_KEY", None)
        try:
            request = _request()
            transport = DomesticProviderTransport(KIMI_K3_SPEC)
            auth = _synthetic_auth()
            ledger = CnyBudgetLedger()
            bounds = InvocationBounds(
                transport.conservative_text_input_token_bound(request), 1024, 200
            )
            with patch("src.jianghe_prespend_runtime.load_owner_paid_call_authorization", return_value=auth):
                with self.assertRaises(ProviderTransportError):
                    transport.invoke(
                        request, authorization=auth, budget=ledger, bounds=bounds, fx=None, now=NOW,
                    )
            self.assertEqual(ledger.spent_cny, Decimal("0"))
            self.assertEqual(ledger.remaining_cny, HARD_PROJECT_CAP_CNY)
        finally:
            if previous is not None:
                os.environ["MOONSHOT_API_KEY"] = previous

    def test_caller_supplied_fx_is_not_production_authority(self):
        request = _request()
        transport = DomesticProviderTransport(KIMI_K3_SPEC, http_post=lambda *args: None)  # type: ignore[arg-type]
        auth = _synthetic_auth()
        usd = _rate(KIMI_K3_SPEC, currency="USD", input_price="3", output_price="15")
        fx = FxAuthority(
            usd_to_cny=Decimal("8"), authority_uri="https://example.invalid/fx",
            effective_at=NOW - timedelta(hours=1), expires_at=NOW + timedelta(hours=1),
        )
        with patch("src.jianghe_prespend_runtime.load_owner_paid_call_authorization", return_value=auth), \
             patch("src.jianghe_prespend_runtime.load_current_repository_rate_card", return_value=usd):
            with self.assertRaises(BudgetGuardError):
                transport.invoke(
                    request, authorization=auth, budget=CnyBudgetLedger(),
                    bounds=InvocationBounds(1, 1, 200), fx=fx, now=NOW,
                )


class SharedBudgetTests(unittest.TestCase):
    def test_hard_cap_cannot_be_raised_above_100(self):
        with self.assertRaises(BudgetGuardError):
            CnyBudgetLedger(Decimal("100.01"))

    def test_exact_remaining_boundary_is_allowed_but_over_boundary_is_rejected(self):
        ledger = CnyBudgetLedger()
        exact_rate = _rate(KIMI_K3_SPEC, input_price="100", output_price="100")
        reservation = ledger.reserve(
            KIMI_K3_SPEC, exact_rate, InvocationBounds(999000, 0, 1000), fx=None, now=NOW
        )
        self.assertEqual(reservation.reserved_cny, Decimal("100"))
        self.assertEqual(ledger.remaining_cny, Decimal("0"))

    def test_one_shared_ledger_requires_reconciliation_before_next_provider(self):
        ledger = CnyBudgetLedger()
        first_rate = _rate(KIMI_K3_SPEC)
        first = ledger.reserve(
            KIMI_K3_SPEC, first_rate, InvocationBounds(1000, 500, 200), fx=None, now=NOW
        )
        with self.assertRaises(BudgetGuardError):
            ledger.reserve(
                DEEPSEEK_VISION_SPEC, _rate(DEEPSEEK_VISION_SPEC),
                InvocationBounds(1000, 500, 200), fx=None, now=NOW,
            )
        ledger.reconcile(
            first.reservation_id, text_input_tokens=100, image_tokens=20, output_tokens=20,
            rate_card=first_rate, fx=None, now=NOW,
        )
        second = ledger.reserve(
            DEEPSEEK_VISION_SPEC, _rate(DEEPSEEK_VISION_SPEC),
            InvocationBounds(1000, 500, 200), fx=None, now=NOW,
        )
        self.assertEqual(second.provider_id, "DEEPSEEK")

    def test_unknown_usage_consumes_full_reservation(self):
        ledger = CnyBudgetLedger()
        rate = _rate(MINIMAX_M3_SPEC)
        reservation = ledger.reserve(
            MINIMAX_M3_SPEC, rate, InvocationBounds(1000, 500, 200), fx=None, now=NOW,
        )
        ledger.consume_full_reservation_on_unknown_usage(reservation.reservation_id)
        self.assertEqual(ledger.spent_cny, reservation.reserved_cny)


class CurrentPricingAuthorityTests(unittest.TestCase):
    def test_kimi_repository_pricing_is_current_and_fixed_image_billing(self):
        card = load_current_repository_rate_card(KIMI_K3_SPEC, now=NOW)
        self.assertEqual(card.currency, "CNY")
        self.assertEqual(card.input_per_million, Decimal("20.00"))
        self.assertEqual(card.output_per_million, Decimal("100.00"))
        self.assertEqual(card.image_billing_mode, "FIXED_INPUT_TOKENS_PER_IMAGE")
        self.assertEqual(card.fixed_input_tokens_per_image, 1024)
        self.assertIsNotNone(card.repository_authority_identity)

    def test_unresolved_provider_image_billing_fails_closed_before_network(self):
        for spec in (DEEPSEEK_VISION_SPEC, MINIMAX_M3_SPEC):
            with self.subTest(provider=spec.provider_id):
                with self.assertRaises(BudgetGuardError):
                    load_current_repository_rate_card(spec, now=NOW)

    def test_current_endpoints_are_bound(self):
        self.assertEqual(KIMI_K3_SPEC.endpoint, "https://api.moonshot.cn/v1/chat/completions")
        self.assertEqual(MINIMAX_M3_SPEC.endpoint, "https://api.minimaxi.com/v1/chat/completions")
        self.assertEqual(DEEPSEEK_VISION_SPEC.endpoint, "https://api.deepseek.com/chat/completions")


if __name__ == "__main__":
    unittest.main()

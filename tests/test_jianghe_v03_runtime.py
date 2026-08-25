"""V0.3 capability-first runtime focused tests (zero network, mock HTTP only)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import hashlib
import json
import os
import unittest
from unittest.mock import patch

from src.jianghe_prespend_runtime import (
    DEEPSEEK_VISION_SPEC,
    RateCard,
    SelectedJiangheContextArtifact,
)
from src.jianghe_stage_a_frozen_stimulus import build_frozen_stage_a_stimulus
from src.jianghe_v03_runtime import (
    DEEPSEEK_V03_CONFIG,
    HISTORICAL_PROJECT_ACCOUNTED_CNY,
    KIMI_V03_CONFIG,
    MINIMAX_V03_CONFIG,
    V03AttemptIdentity,
    V03BudgetLedger,
    V03CommonExamIdentity,
    V03HttpResponse,
    V03InvocationEvidence,
    V03ModelMismatchError,
    V03ProviderTransport,
    V03Request,
    V03TerminalStatus,
    v03_capability_answer_contract_identity,
    v03_slot_identity,
)

NOW = datetime(2026, 8, 25, 1, 0, tzinfo=timezone.utc)


def _common_exam(stimulus, context, system_prompt, decision_prompt) -> V03CommonExamIdentity:
    return V03CommonExamIdentity(
        fixture_id="JH-FIX-C-001",
        stimulus_identity=stimulus.identity,
        source_observation_identity=stimulus.observation.identity.identity,
        point_in_time=stimulus.observation.identity.decision_time.isoformat(),
        system_prompt_sha256=hashlib.sha256(system_prompt.encode("utf-8")).hexdigest(),
        decision_prompt_sha256=hashlib.sha256(decision_prompt.encode("utf-8")).hexdigest(),
        capability_answer_contract_identity=v03_capability_answer_contract_identity(),
        selected_context_identity=context.identity,
        model_context_identity=context.model_payload()["model_context_identity"],
        structured_observation_identity=stimulus.structured.identity,
        png_sha256=stimulus.png_sha256,
        visual_artifact_identity=stimulus.visual_artifact_identity,
        renderer_config_identity=stimulus.renderer_config_identity,
    )


def _request(config):
    stimulus = build_frozen_stage_a_stimulus()
    context = SelectedJiangheContextArtifact.from_fixture_id("JH-FIX-C-001")
    system_prompt = "You are bound by Jianghe V1.1."
    decision_prompt = "Use the headed capability answer contract."
    common = _common_exam(stimulus, context, system_prompt, decision_prompt)
    attempt = V03AttemptIdentity(
        common_exam_identity=common.identity,
        provider_inference_config_identity=config.identity,
        slot_identity=v03_slot_identity(config.provider_id),
        model_request_at=NOW.isoformat(),
    )
    return V03Request(
        system_prompt=system_prompt,
        decision_prompt=decision_prompt,
        context=context,
        structured_observation=stimulus.structured,
        visual=stimulus.visual,
        common_exam_identity=common,
        provider_config=config,
        attempt_identity=attempt,
        point_in_time=stimulus.observation.identity.decision_time.isoformat(),
    )


def _rate(config, *, input_cny="3", output_cny="9"):
    return RateCard(
        provider_id=config.provider_id,
        model_id=config.model_id,
        currency="CNY",
        input_per_million=Decimal(input_cny),
        output_per_million=Decimal(output_cny),
        image_tokens_billed_as_input=True,
        authority_uri="https://example.invalid/v03-test-rate-card",
        effective_at=NOW - timedelta(hours=1),
        expires_at=NOW + timedelta(hours=1),
        image_billing_mode="FIXED_INPUT_TOKENS_PER_IMAGE",
        fixed_input_tokens_per_image=384,
    )


def _complete_body(config, content):
    return {
        "id": "req-001",
        "model": config.model_id,
        "choices": [{"finish_reason": "stop", "message": {"content": content}}],
        "usage": {"prompt_tokens": 5000, "completion_tokens": 800},
    }


class V03IdentityTests(unittest.TestCase):
    def test_common_exam_is_provider_neutral(self) -> None:
        stimulus = build_frozen_stage_a_stimulus()
        context = SelectedJiangheContextArtifact.from_fixture_id("JH-FIX-C-001")
        a = _common_exam(stimulus, context, "S", "D")
        b = _common_exam(stimulus, context, "S", "D")
        self.assertEqual(a.identity, b.identity)
        self.assertNotIn("DEEPSEEK", a.identity)
        self.assertNotIn("max_output", a.identity)
        self.assertNotIn("reasoning", a.identity)

    def test_attempt_identity_binds_common_and_provider_config(self) -> None:
        common = _common_exam(
            build_frozen_stage_a_stimulus(),
            SelectedJiangheContextArtifact.from_fixture_id("JH-FIX-C-001"),
            "S", "D",
        )
        attempt = V03AttemptIdentity(
            common_exam_identity=common.identity,
            provider_inference_config_identity=DEEPSEEK_V03_CONFIG.identity,
            slot_identity=v03_slot_identity("DEEPSEEK"),
            model_request_at=NOW.isoformat(),
        )
        self.assertIn("DEEPSEEK", attempt.slot_identity)
        self.assertEqual(common.identity, attempt.common_exam_identity)

    def test_slot_identity_is_v03_namespace(self) -> None:
        self.assertEqual("V0_3:DEEPSEEK:CAPABILITY_MATCHED_001", v03_slot_identity("DEEPSEEK"))
        self.assertEqual("V0_3:MINIMAX:CAPABILITY_MATCHED_001", v03_slot_identity("MINIMAX"))
        self.assertEqual("V0_3:KIMI:CAPABILITY_MATCHED_001", v03_slot_identity("KIMI"))
        with self.assertRaises(ValueError):
            v03_slot_identity("DEEPSEEK:1")

    def test_v03_configs_have_sufficient_headroom_and_timeout(self) -> None:
        for config in (DEEPSEEK_V03_CONFIG, MINIMAX_V03_CONFIG, KIMI_V03_CONFIG):
            self.assertEqual(131072, config.max_output_tokens)
            self.assertEqual(900, config.network_timeout_seconds)
            self.assertFalse(config.stream)
            self.assertEqual((), config.tools)
            self.assertEqual("NONE", config.response_format_policy)


class V03BudgetLedgerTests(unittest.TestCase):
    def test_ledger_carries_historical_spend(self) -> None:
        ledger = V03BudgetLedger()
        self.assertEqual(Decimal("0.270021"), ledger.historical_accounted_cny)
        self.assertEqual(Decimal("0.270021"), ledger.spent_cny)
        self.assertEqual(Decimal("99.729979"), ledger.remaining_cny)

    def test_reserve_reconcile_accounts_conservatively(self) -> None:
        ledger = V03BudgetLedger()
        reservation = ledger.reserve(
            provider_config=DEEPSEEK_V03_CONFIG,
            rate_card=_rate(DEEPSEEK_V03_CONFIG),
            max_text_input_tokens=50000,
            max_image_tokens=384,
            now=NOW,
        )
        self.assertGreater(Decimal(reservation["precall_conservative_reservation_cny"]), 0)
        reconciled = ledger.reconcile(
            usage=__import__("src.jianghe_v03_runtime", fromlist=["V03TokenUsage"]).V03TokenUsage(
                prompt_tokens=4000, cached_input_tokens=0, image_tokens=384,
                reasoning_tokens=100, completion_tokens=800,
            ),
            provider_reported_billed_cny=None,
            now=NOW,
        )
        self.assertTrue(reconciled["calculated_is_conservative"])
        self.assertIsNone(reconciled["provider_reported_billed_cny"])
        self.assertEqual(reconciled["accounted_cny_for_hard_cap"], reconciled["postcall_calculated_cny"])
        self.assertGreater(ledger.spent_cny, Decimal("0.270021"))

    def test_unknown_usage_consumes_full_reservation(self) -> None:
        ledger = V03BudgetLedger()
        ledger.reserve(
            provider_config=DEEPSEEK_V03_CONFIG,
            rate_card=_rate(DEEPSEEK_V03_CONFIG),
            max_text_input_tokens=50000,
            max_image_tokens=384,
            now=NOW,
        )
        ledger.consume_full_reservation_on_unknown_usage()
        self.assertGreater(ledger.spent_cny, Decimal("0.270021"))

    def test_never_exceeds_hard_cap(self) -> None:
        ledger = V03BudgetLedger()
        spent = Decimal("0")
        for _ in range(200):
            reservation = ledger.reserve(
                provider_config=KIMI_V03_CONFIG,
                rate_card=_rate(KIMI_V03_CONFIG),
                max_text_input_tokens=1000,
                max_image_tokens=1024,
                now=NOW,
            )
            ledger.reconcile(
                usage=__import__("src.jianghe_v03_runtime", fromlist=["V03TokenUsage"]).V03TokenUsage(
                    prompt_tokens=1000, cached_input_tokens=0, image_tokens=1024,
                    reasoning_tokens=0, completion_tokens=1000,
                ),
                provider_reported_billed_cny=None,
                now=NOW,
            )
            spent = ledger.spent_cny
        self.assertLessEqual(spent, Decimal("100.00"))


class V03TransportTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["DEEPSEEK_API_KEY"] = "TEST_KEY"

    def test_payloads_have_no_response_format_forcing(self) -> None:
        for config in (DEEPSEEK_V03_CONFIG, MINIMAX_V03_CONFIG, KIMI_V03_CONFIG):
            request = _request(config)
            payload = V03ProviderTransport(config).build_payload(request)
            self.assertEqual(config.model_id, payload["model"])
            self.assertNotIn("response_format", payload)
            self.assertEqual([], payload["tools"])
            self.assertEqual(False, payload["stream"])
            self.assertEqual(131072, payload[config.max_output_field])
            parts = payload["messages"][1]["content"]
            self.assertIn("image_url", {part["type"] for part in parts})

    def test_deepseek_payload_thinking_and_reasoning_effort(self) -> None:
        request = _request(DEEPSEEK_V03_CONFIG)
        payload = V03ProviderTransport(DEEPSEEK_V03_CONFIG).build_payload(request)
        self.assertEqual({"type": "enabled"}, payload["thinking"])
        self.assertEqual("max", payload["reasoning_effort"])
        self.assertIn("max_tokens", payload)

    def test_minimax_payload_reasoning_split(self) -> None:
        request = _request(MINIMAX_V03_CONFIG)
        payload = V03ProviderTransport(MINIMAX_V03_CONFIG).build_payload(request)
        self.assertEqual({"type": "adaptive"}, payload["thinking"])
        self.assertTrue(payload["reasoning_split"])
        self.assertIn("max_completion_tokens", payload)

    def test_kimi_payload_reasoning_effort(self) -> None:
        request = _request(KIMI_V03_CONFIG)
        payload = V03ProviderTransport(KIMI_V03_CONFIG).build_payload(request)
        self.assertEqual("max", payload["reasoning_effort"])
        self.assertIn("max_completion_tokens", payload)

    def test_complete_answer_preserves_raw_final_and_no_reasoning_text(self) -> None:
        final = "MARKET_INTERPRETATION:\nRange structure.\n\nFAMILY:\nNONE\n\nACTION:\nWAIT\n\nEVIDENCE:\nNo trigger.\n"
        request = _request(DEEPSEEK_V03_CONFIG)
        transport = V03ProviderTransport(
            DEEPSEEK_V03_CONFIG,
            http_post=lambda *_: V03HttpResponse(
                200, json.dumps(_complete_body(DEEPSEEK_V03_CONFIG, final)).encode()
            ),
        )
        evidence = transport.invoke(
            request,
            budget=V03BudgetLedger(),
            rate_card=_rate(DEEPSEEK_V03_CONFIG),
            max_image_tokens=384,
            now=NOW,
        )
        self.assertEqual(final, evidence.model_raw_final_answer)
        self.assertEqual(V03TerminalStatus.COMPLETE_CAPABILITY_ANSWER.value, evidence.terminal_status)
        self.assertNotIn("reasoning", evidence.to_durable()["model_raw_final_answer"] or "")

    def test_reasoning_content_is_hashed_not_persisted(self) -> None:
        final = "MARKET_INTERPRETATION:\nBreakout.\n\nFAMILY:\nA\n\nACTION:\nENTER\n\nDIRECTION_IF_APPLICABLE:\nLONG\n\nEVIDENCE:\nPoke.\n"
        body = _complete_body(DEEPSEEK_V03_CONFIG, final)
        body["choices"][0]["message"]["reasoning_content"] = "SECRET_CHAIN_OF_THOUGHT"
        body["usage"]["completion_tokens_details"] = {"reasoning_tokens": 300}
        request = _request(DEEPSEEK_V03_CONFIG)
        transport = V03ProviderTransport(
            DEEPSEEK_V03_CONFIG,
            http_post=lambda *_: V03HttpResponse(200, json.dumps(body).encode()),
        )
        evidence = transport.invoke(
            request,
            budget=V03BudgetLedger(),
            rate_card=_rate(DEEPSEEK_V03_CONFIG),
            max_image_tokens=384,
            now=NOW,
        )
        durable = json.dumps(evidence.to_durable())
        self.assertNotIn("SECRET_CHAIN_OF_THOUGHT", durable)
        self.assertTrue(evidence.reasoning_present)
        self.assertEqual(300, evidence.usage.reasoning_tokens)
        self.assertIsNotNone(evidence.reasoning_sha256)

    def test_empty_content_is_output_empty_not_infra(self) -> None:
        body = _complete_body(DEEPSEEK_V03_CONFIG, None)
        request = _request(DEEPSEEK_V03_CONFIG)
        transport = V03ProviderTransport(
            DEEPSEEK_V03_CONFIG,
            http_post=lambda *_: V03HttpResponse(200, json.dumps(body).encode()),
        )
        evidence = transport.invoke(
            request,
            budget=V03BudgetLedger(),
            rate_card=_rate(DEEPSEEK_V03_CONFIG),
            max_image_tokens=384,
            now=NOW,
        )
        self.assertEqual(V03TerminalStatus.OUTPUT_EMPTY.value, evidence.terminal_status)
        self.assertIsNone(evidence.model_raw_final_answer)

    def test_truncation_is_output_truncated_not_infra(self) -> None:
        body = _complete_body(DEEPSEEK_V03_CONFIG, "MARKET_INTERPRETATION:\nPartial")
        body["choices"][0]["finish_reason"] = "length"
        request = _request(DEEPSEEK_V03_CONFIG)
        transport = V03ProviderTransport(
            DEEPSEEK_V03_CONFIG,
            http_post=lambda *_: V03HttpResponse(200, json.dumps(body).encode()),
        )
        evidence = transport.invoke(
            request,
            budget=V03BudgetLedger(),
            rate_card=_rate(DEEPSEEK_V03_CONFIG),
            max_image_tokens=384,
            now=NOW,
        )
        self.assertEqual(V03TerminalStatus.OUTPUT_TRUNCATED.value, evidence.terminal_status)

    def test_model_mismatch_fails_closed_without_retry(self) -> None:
        body = _complete_body(DEEPSEEK_V03_CONFIG, "MARKET_INTERPRETATION:\nX")
        body["model"] = "some-other-model"
        request = _request(DEEPSEEK_V03_CONFIG)
        transport = V03ProviderTransport(
            DEEPSEEK_V03_CONFIG,
            http_post=lambda *_: V03HttpResponse(200, json.dumps(body).encode()),
        )
        with self.assertRaises(V03ModelMismatchError):
            transport.invoke(
                request,
                budget=V03BudgetLedger(),
                rate_card=_rate(DEEPSEEK_V03_CONFIG),
                max_image_tokens=384,
                now=NOW,
            )

    def test_http_error_consumes_full_reservation(self) -> None:
        request = _request(DEEPSEEK_V03_CONFIG)
        budget = V03BudgetLedger()
        transport = V03ProviderTransport(
            DEEPSEEK_V03_CONFIG,
            http_post=lambda *_: V03HttpResponse(503, b"{}"),
        )
        with self.assertRaises(RuntimeError):
            transport.invoke(
                request,
                budget=budget,
                rate_card=_rate(DEEPSEEK_V03_CONFIG),
                max_image_tokens=384,
                now=NOW,
            )
        self.assertGreater(budget.spent_cny, Decimal("0.270021"))

    def test_requested_and_resolved_model_recorded(self) -> None:
        final = "MARKET_INTERPRETATION:\nX\n"
        request = _request(DEEPSEEK_V03_CONFIG)
        transport = V03ProviderTransport(
            DEEPSEEK_V03_CONFIG,
            http_post=lambda *_: V03HttpResponse(
                200, json.dumps(_complete_body(DEEPSEEK_V03_CONFIG, final)).encode()
            ),
        )
        evidence = transport.invoke(
            request,
            budget=V03BudgetLedger(),
            rate_card=_rate(DEEPSEEK_V03_CONFIG),
            max_image_tokens=384,
            now=NOW,
        )
        self.assertEqual("deepseek-v4-flash-vision-exp", evidence.requested_model_id)
        self.assertEqual("deepseek-v4-flash-vision-exp", evidence.resolved_model_id)

    def test_evidence_durable_has_cost_labels_and_no_raw_body(self) -> None:
        final = "MARKET_INTERPRETATION:\nX\n"
        request = _request(DEEPSEEK_V03_CONFIG)
        transport = V03ProviderTransport(
            DEEPSEEK_V03_CONFIG,
            http_post=lambda *_: V03HttpResponse(
                200, json.dumps(_complete_body(DEEPSEEK_V03_CONFIG, final)).encode()
            ),
        )
        evidence = transport.invoke(
            request,
            budget=V03BudgetLedger(),
            rate_card=_rate(DEEPSEEK_V03_CONFIG),
            max_image_tokens=384,
            now=NOW,
        )
        durable = evidence.to_durable(redact=("test-secret-value",))
        self.assertIn("precall_conservative_reservation_cny", durable)
        self.assertIn("postcall_calculated_cny", durable)
        self.assertIn("provider_reported_billed_cny", durable)
        self.assertIn("accounted_cny_for_hard_cap", durable)
        self.assertFalse(durable["hidden_reasoning_persisted"])
        self.assertFalse(durable["raw_provider_body_persisted"])


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import unittest
from unittest.mock import patch

from src.jianghe_prespend_runtime import (
    BudgetGuardError,
    CnyBudgetLedger,
    HttpResponse,
    KIMI_K3_SPEC,
    PaidCallAuthorization,
    ProviderTransportError,
    RateCard,
)
from src.jianghe_response_normalizer import JiangheResponseNormalizer, RESPONSE_SCHEMA_VERSION
from src.jianghe_stage_a_runtime import (
    ALL_TRACKS,
    QUALIFICATION_FIXTURE_ID,
    STAGE_A_PROVIDER_CAP_CNY,
    STAGE_A_TOTAL_CAP_CNY,
    StageABudgetEnvelope,
    StageAInputTrack,
    StageAProviderTransport,
    build_stage_a_stimulus,
    exact_invocation_bounds,
    make_stage_a_request,
    qualification_visible_information,
    runtime_response_json_schema,
    semantic_fixture_text,
)

UTC = timezone.utc
NOW = datetime(2026, 8, 24, 1, 10, tzinfo=UTC)
ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = ROOT / "docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_1.json"


def _prompts() -> tuple[str, str]:
    payload = json.loads(PROMPT_PATH.read_text(encoding="utf-8"))
    return payload["system_prompt"], payload["decision_prompt"]


def _rate() -> RateCard:
    return RateCard(
        provider_id=KIMI_K3_SPEC.provider_id,
        model_id=KIMI_K3_SPEC.model_id,
        currency="CNY",
        input_per_million=Decimal("1"),
        output_per_million=Decimal("1"),
        image_tokens_billed_as_input=True,
        authority_uri="https://example.invalid/stage-a-rate-test",
        effective_at=NOW - timedelta(hours=1),
        expires_at=NOW + timedelta(hours=1),
        image_billing_mode="FIXED_INPUT_TOKENS_PER_IMAGE",
        fixed_input_tokens_per_image=1024,
    )


def _authorization() -> PaidCallAuthorization:
    return PaidCallAuthorization(
        authorization_id="TEST_STAGE_A_AUTH",
        authorization_evidence_sha256="1" * 64,
        provider_models=((KIMI_K3_SPEC.provider_id, KIMI_K3_SPEC.model_id),),
        hard_cap_cny=Decimal("100.00"),
        paid_calls_enabled=True,
    )


def _fake_response(model: str = KIMI_K3_SPEC.model_id) -> HttpResponse:
    content = json.dumps(
        {
            "schema_version": RESPONSE_SCHEMA_VERSION,
            "family": "NONE",
            "action": "NO_TRADE",
            "direction": "NONE",
            "attention_mode": "WATCH",
            "decision_state": "NO_CONFIRMED_BREAKOUT",
            "rationale": "没有形成可确认的延续触发。",
            "declared_unknown": [],
            "principle_references": [],
            "source_references": [],
            "numeric_claims": [],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )
    body = json.dumps(
        {
            "id": "test-provider-request-1",
            "model": model,
            "choices": [{"message": {"content": content}}],
            "usage": {"prompt_tokens": 100, "completion_tokens": 40, "image_tokens": 0},
        },
        ensure_ascii=False,
    ).encode("utf-8")
    return HttpResponse(200, {}, body)


class StageAStimulusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stimulus = build_stage_a_stimulus()

    def test_fixture_visible_information_is_exact_closed_world(self) -> None:
        visible = qualification_visible_information()
        self.assertEqual(
            {"situation", "timeframes", "market_state", "synthetic_observations"},
            set(visible),
        )
        self.assertEqual(["1H", "15m", "5m"], visible["timeframes"])
        semantic = semantic_fixture_text()
        for forbidden in (
            QUALIFICATION_FIXTURE_ID,
            "hidden_future_information",
            '"expected"',
            '"rubric"',
            '"pass_paths"',
            '"fail_conditions"',
        ):
            self.assertNotIn(forbidden, semantic)

    def test_stimulus_is_deterministic_and_same_observation_bound(self) -> None:
        again = build_stage_a_stimulus()
        self.assertEqual(self.stimulus.identity, again.identity)
        self.assertEqual(self.stimulus.png_sha256, again.png_sha256)
        self.assertEqual(self.stimulus.visual.identity, again.visual.identity)
        self.assertEqual(self.stimulus.structured.identity, again.structured.identity)
        observation_id = self.stimulus.observation.identity.identity
        self.assertEqual(observation_id, self.stimulus.visual.source_observation_identity)
        self.assertEqual(observation_id, self.stimulus.structured.source_observation_identity)

    def test_exact_bar_counts_and_aggregation_share_one_observation(self) -> None:
        bars = self.stimulus.observation.bars
        by_tf = {
            tf: [item for item in bars if item.timeframe == tf]
            for tf in ("5m", "15m", "1H")
        }
        self.assertEqual(96, len(by_tf["5m"]))
        self.assertEqual(32, len(by_tf["15m"]))
        self.assertEqual(8, len(by_tf["1H"]))
        probe = by_tf["5m"][80]
        self.assertEqual("103", probe.high_price)
        self.assertEqual("101.1", probe.close_price)
        self.assertLess(Decimal(probe.close_price), Decimal("102"))
        self.assertTrue(all(Decimal(item.high_price) < Decimal("102") for item in by_tf["5m"][:80]))
        self.assertTrue(all(Decimal(item.high_price) < Decimal("102") for item in by_tf["5m"][81:]))
        self.assertEqual("103", by_tf["15m"][26].high_price)
        self.assertEqual("103", by_tf["1H"][6].high_price)
        self.assertEqual(by_tf["5m"][80].high_price, by_tf["15m"][26].high_price)

    def test_visual_uses_neutral_non_fixture_instrument_identifiers(self) -> None:
        identity = self.stimulus.observation.identity
        self.assertEqual("SYNTH", identity.product)
        self.assertEqual("SYNTH.MKT001", identity.concrete_contract)
        self.assertNotIn("C001", identity.concrete_contract)
        self.assertTrue(self.stimulus.visual.png_bytes.startswith(b"\x89PNG\r\n\x1a\n"))


class StageATrackIsolationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.system_prompt, cls.decision_prompt = _prompts()
        cls.stimulus = build_stage_a_stimulus()

    def _request(self, track: StageAInputTrack):
        return make_stage_a_request(
            track,
            system_prompt=self.system_prompt,
            decision_prompt=self.decision_prompt,
            stimulus=self.stimulus,
        )

    def _payload_text(self, track: StageAInputTrack) -> str:
        transport = StageAProviderTransport(KIMI_K3_SPEC, http_post=lambda *_: _fake_response())
        return transport.payload_bytes(self._request(track)).decode("utf-8")

    def test_all_five_tracks_are_frozen_and_unique(self) -> None:
        self.assertEqual(
            [
                "OPERATIONAL_PROVIDER",
                "SEMANTIC",
                "VISUAL",
                "STRUCTURED",
                "DUAL_INPUT",
            ],
            [item.value for item in ALL_TRACKS],
        )
        identities = {self._request(item).identity for item in ALL_TRACKS}
        self.assertEqual(5, len(identities))

    def test_semantic_has_visible_text_only_no_chart_or_structured_market_state(self) -> None:
        request = self._request(StageAInputTrack.SEMANTIC)
        payload = self._payload_text(StageAInputTrack.SEMANTIC)
        self.assertEqual((), request.visuals)
        self.assertIsNone(request.transmitted_structured_identity)
        self.assertIn("RANGE_WICK_POKE_NO_FOLLOW", payload)
        self.assertNotIn("canonical_observation", payload)
        self.assertNotIn("data:image/png;base64", payload)
        self.assertNotIn(QUALIFICATION_FIXTURE_ID, payload)

    def test_visual_has_chart_only_no_fixture_prose_or_structured_market_state(self) -> None:
        request = self._request(StageAInputTrack.VISUAL)
        payload = self._payload_text(StageAInputTrack.VISUAL)
        self.assertEqual(1, len(request.visuals))
        self.assertIsNone(request.transmitted_structured_identity)
        self.assertIn("data:image/png;base64", payload)
        self.assertNotIn("RANGE_WICK_POKE_NO_FOLLOW", payload)
        self.assertNotIn("上影线刺破上边界", payload)
        self.assertNotIn("canonical_observation", payload)
        self.assertNotIn(QUALIFICATION_FIXTURE_ID, payload)
        self.assertNotIn('"stage_a_input_track"', payload)

    def test_structured_has_structured_only_no_chart_or_fixture_prose(self) -> None:
        request = self._request(StageAInputTrack.STRUCTURED)
        payload = self._payload_text(StageAInputTrack.STRUCTURED)
        self.assertEqual((), request.visuals)
        self.assertEqual(self.stimulus.structured.identity, request.transmitted_structured_identity)
        self.assertIn("canonical_observation", payload)
        self.assertNotIn("data:image/png;base64", payload)
        self.assertNotIn("RANGE_WICK_POKE_NO_FOLLOW", payload)
        self.assertNotIn("上影线刺破上边界", payload)
        self.assertNotIn(QUALIFICATION_FIXTURE_ID, payload)

    def test_dual_has_exact_same_visual_and_structured_identities(self) -> None:
        visual = self._request(StageAInputTrack.VISUAL)
        structured = self._request(StageAInputTrack.STRUCTURED)
        dual = self._request(StageAInputTrack.DUAL_INPUT)
        payload = self._payload_text(StageAInputTrack.DUAL_INPUT)
        self.assertEqual(visual.visuals[0].identity, dual.visuals[0].identity)
        self.assertEqual(structured.transmitted_structured_identity, dual.transmitted_structured_identity)
        self.assertIn("data:image/png;base64", payload)
        self.assertIn("canonical_observation", payload)
        self.assertNotIn("RANGE_WICK_POKE_NO_FOLLOW", payload)
        self.assertNotIn(QUALIFICATION_FIXTURE_ID, payload)

    def test_operational_is_multimodal_smoke_not_answer_prose(self) -> None:
        operational = self._request(StageAInputTrack.OPERATIONAL_PROVIDER)
        payload = self._payload_text(StageAInputTrack.OPERATIONAL_PROVIDER)
        self.assertEqual(1, len(operational.visuals))
        self.assertIsNotNone(operational.transmitted_structured_identity)
        self.assertIn("data:image/png;base64", payload)
        self.assertIn("canonical_observation", payload)
        self.assertNotIn("RANGE_WICK_POKE_NO_FOLLOW", payload)

    def test_runtime_json_schema_matches_strict_normalizer_fields(self) -> None:
        schema = runtime_response_json_schema()
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(set(schema["required"]), set(schema["properties"]))
        raw = _fake_response().body.decode("utf-8")
        content = json.loads(raw)["choices"][0]["message"]["content"]
        normalized = JiangheResponseNormalizer().normalize(content)
        self.assertEqual("NONE", normalized.family.value)
        self.assertEqual("NO_TRADE", normalized.action.value)


class StageABudgetAndTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.system_prompt, cls.decision_prompt = _prompts()
        cls.stimulus = build_stage_a_stimulus()
        cls.request = make_stage_a_request(
            StageAInputTrack.DUAL_INPUT,
            system_prompt=cls.system_prompt,
            decision_prompt=cls.decision_prompt,
            stimulus=cls.stimulus,
            max_output_tokens=800,
        )

    def test_local_stage_caps_fail_closed(self) -> None:
        envelope = StageABudgetEnvelope(
            spent_cny=Decimal("5.50"),
            provider_spent_cny={"KIMI": Decimal("5.50")},
        )
        with self.assertRaises(BudgetGuardError):
            envelope.preflight("KIMI", Decimal("0.51"))
        total = StageABudgetEnvelope(
            spent_cny=Decimal("17.90"),
            provider_spent_cny={
                "KIMI": Decimal("6.00"),
                "DEEPSEEK": Decimal("6.00"),
                "MINIMAX": Decimal("5.90"),
            },
        )
        with self.assertRaises(BudgetGuardError):
            total.preflight("MINIMAX", Decimal("0.11"))
        self.assertEqual(Decimal("18.00"), STAGE_A_TOTAL_CAP_CNY)
        self.assertEqual(Decimal("6.00"), STAGE_A_PROVIDER_CAP_CNY)

    def test_missing_credential_cancels_before_network_and_spends_zero(self) -> None:
        rate = _rate()
        transport = StageAProviderTransport(KIMI_K3_SPEC, http_post=lambda *_: self.fail("network called"))
        bounds = exact_invocation_bounds(transport, self.request, rate_card=rate)
        budget = CnyBudgetLedger()
        stage_budget = StageABudgetEnvelope()
        auth = _authorization()
        with (
            patch("src.jianghe_stage_a_runtime.load_owner_paid_call_authorization", return_value=auth),
            patch("src.jianghe_stage_a_runtime.load_current_repository_rate_card", return_value=rate),
            patch.dict(os.environ, {}, clear=True),
        ):
            with self.assertRaises(ProviderTransportError):
                transport.invoke_stage_a(
                    self.request,
                    authorization=auth,
                    budget=budget,
                    stage_budget=stage_budget,
                    bounds=bounds,
                    now=NOW,
                )
        self.assertEqual(Decimal("0"), budget.spent_cny)
        self.assertEqual(Decimal("0"), stage_budget.spent_cny)
        self.assertTrue(any(item[0].startswith("CANCELLED_BEFORE_NETWORK") for item in budget.history))

    def test_successful_fake_call_preserves_identity_usage_and_stage_budget(self) -> None:
        rate = _rate()
        transport = StageAProviderTransport(KIMI_K3_SPEC, http_post=lambda *_: _fake_response())
        bounds = exact_invocation_bounds(transport, self.request, rate_card=rate)
        budget = CnyBudgetLedger()
        stage_budget = StageABudgetEnvelope()
        auth = _authorization()
        with (
            patch("src.jianghe_stage_a_runtime.load_owner_paid_call_authorization", return_value=auth),
            patch("src.jianghe_stage_a_runtime.load_current_repository_rate_card", return_value=rate),
            patch.dict(os.environ, {KIMI_K3_SPEC.api_key_env: "TEST_ONLY_NOT_SECRET"}, clear=True),
        ):
            evidence = transport.invoke_stage_a(
                self.request,
                authorization=auth,
                budget=budget,
                stage_budget=stage_budget,
                bounds=bounds,
                now=NOW,
            )
        self.assertEqual(self.request.identity, evidence.request_identity)
        self.assertEqual(KIMI_K3_SPEC.model_id, evidence.resolved_model_id)
        self.assertEqual(self.stimulus.structured.identity, evidence.transmitted_structured_observation_identity)
        self.assertEqual((self.stimulus.visual.identity,), evidence.transmitted_visual_identities)
        self.assertGreater(budget.spent_cny, Decimal("0"))
        self.assertEqual(budget.spent_cny, stage_budget.spent_cny)

    def test_http_failure_is_not_retried_and_charges_conservative_reservation(self) -> None:
        rate = _rate()
        calls = {"count": 0}

        def fail_once(*_):
            calls["count"] += 1
            return HttpResponse(500, {}, b"{}")

        transport = StageAProviderTransport(KIMI_K3_SPEC, http_post=fail_once)
        bounds = exact_invocation_bounds(transport, self.request, rate_card=rate)
        budget = CnyBudgetLedger()
        stage_budget = StageABudgetEnvelope()
        auth = _authorization()
        with (
            patch("src.jianghe_stage_a_runtime.load_owner_paid_call_authorization", return_value=auth),
            patch("src.jianghe_stage_a_runtime.load_current_repository_rate_card", return_value=rate),
            patch.dict(os.environ, {KIMI_K3_SPEC.api_key_env: "TEST_ONLY_NOT_SECRET"}, clear=True),
        ):
            with self.assertRaises(ProviderTransportError):
                transport.invoke_stage_a(
                    self.request,
                    authorization=auth,
                    budget=budget,
                    stage_budget=stage_budget,
                    bounds=bounds,
                    now=NOW,
                )
        self.assertEqual(1, calls["count"])
        self.assertGreater(budget.spent_cny, Decimal("0"))
        self.assertEqual(budget.spent_cny, stage_budget.spent_cny)


if __name__ == "__main__":
    unittest.main()

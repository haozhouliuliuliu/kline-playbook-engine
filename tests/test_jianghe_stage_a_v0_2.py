from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.jianghe_prespend_runtime import (
    CnyBudgetLedger,
    DEEPSEEK_VISION_SPEC,
    HttpResponse,
    KIMI_K3_SPEC,
    MINIMAX_M3_SPEC,
    PaidCallAuthorization,
    RateCard,
)
from src.jianghe_stage_a_runtime import (
    StageABudgetEnvelope,
    StageAInputTrack,
    StageAProviderTransport,
    exact_invocation_bounds,
    make_stage_a_request,
)
from src.jianghe_response_normalizer import JiangheResponseNormalizer
from src.jianghe_stage_a_runner import (
    FROZEN_PLAN_PATH,
    SlotAlreadyAttemptedError,
    VerifiedFrozenStageAPlan,
    prepare_frozen_slot,
    StageAExecutionJournal,
    execute_frozen_slot,
)
from src.jianghe_stage_a_remote_ledger import (
    DEFAULT_REMOTE_REF,
    GitRemoteLedgerStore,
    RemoteExecutionLedger,
)
from src.jianghe_stage_a_evidence import canonical_json_bytes
from src.jianghe_source_only_verification import _repository_blob_bytes
from tools.build_jianghe_stage_a_frozen_plan import build_frozen_plan as build_v0_1_plan
from tools.build_jianghe_stage_a_frozen_plan_v0_2 import build_frozen_plan as build_v0_2_plan


NOW = datetime(2026, 8, 24, 9, 30, tzinfo=timezone.utc)


def _request():
    return make_stage_a_request(
        StageAInputTrack.SEMANTIC,
        system_prompt="Return one JSON object only.",
        decision_prompt="Apply the governed Jianghe semantics.",
        max_output_tokens=1024,
    )


def _rate(spec) -> RateCard:
    return RateCard(
        provider_id=spec.provider_id,
        model_id=spec.model_id,
        currency="CNY",
        input_per_million=Decimal("1"),
        output_per_million=Decimal("1"),
        image_tokens_billed_as_input=True,
        authority_uri="https://example.invalid/stage-a-v0-2-test",
        effective_at=NOW - timedelta(hours=1),
        expires_at=NOW + timedelta(hours=1),
    )


def _authorization(spec) -> PaidCallAuthorization:
    return PaidCallAuthorization(
        authorization_id="TEST_STAGE_A_V0_2",
        authorization_evidence_sha256="2" * 64,
        provider_models=((spec.provider_id, spec.model_id),),
        hard_cap_cny=Decimal("100"),
        paid_calls_enabled=True,
    )


class StageAV02ProviderContractTests(unittest.TestCase):
    def test_exact_provider_wire_contracts(self) -> None:
        request = make_stage_a_request(
            StageAInputTrack.VISUAL,
            system_prompt="Return one JSON object only.",
            decision_prompt="Apply the governed Jianghe semantics.",
            max_output_tokens=1024,
        )
        kimi = StageAProviderTransport(KIMI_K3_SPEC).build_payload(request)
        deepseek = StageAProviderTransport(DEEPSEEK_VISION_SPEC).build_payload(request)
        minimax = StageAProviderTransport(MINIMAX_M3_SPEC).build_payload(request)

        self.assertEqual(1024, kimi["max_completion_tokens"])
        self.assertEqual("max", kimi["reasoning_effort"])
        self.assertTrue(kimi["response_format"]["json_schema"]["strict"])
        self.assertEqual([], kimi["tools"])
        self.assertIn(
            "image_url",
            {part["type"] for part in kimi["messages"][1]["content"]},
        )

        self.assertEqual(1024, deepseek["max_tokens"])
        self.assertEqual({"type": "enabled"}, deepseek["thinking"])
        self.assertEqual("max", deepseek["reasoning_effort"])
        self.assertEqual({"type": "json_object"}, deepseek["response_format"])
        self.assertEqual([], deepseek["tools"])

        self.assertEqual(1024, minimax["max_completion_tokens"])
        self.assertEqual({"type": "adaptive"}, minimax["thinking"])
        self.assertTrue(minimax["reasoning_split"])
        self.assertFalse(minimax["stream"])
        self.assertEqual([], minimax["tools"])
        self.assertEqual(kimi["messages"], deepseek["messages"])
        self.assertEqual(kimi["messages"], minimax["messages"])

    def test_deepseek_2xx_null_content_preserves_safe_mechanical_evidence(self) -> None:
        body = {
            "id": "response-1",
            "model": DEEPSEEK_VISION_SPEC.model_id,
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {"content": None, "reasoning_content": "private reasoning"},
                }
            ],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 25,
                "completion_tokens_details": {"reasoning_tokens": 20},
            },
        }
        request = _request()
        rate = _rate(DEEPSEEK_VISION_SPEC)
        auth = _authorization(DEEPSEEK_VISION_SPEC)
        transport = StageAProviderTransport(
            DEEPSEEK_VISION_SPEC,
            http_post=lambda *_: HttpResponse(200, {}, json.dumps(body).encode()),
        )
        bounds = exact_invocation_bounds(transport, request, rate_card=rate)
        budget = CnyBudgetLedger()
        stage_budget = StageABudgetEnvelope()
        with (
            patch("src.jianghe_stage_a_runtime.load_owner_paid_call_authorization", return_value=auth),
            patch("src.jianghe_stage_a_runtime.load_current_repository_rate_card", return_value=rate),
            patch.dict(os.environ, {DEEPSEEK_VISION_SPEC.api_key_env: "TEST_KEY"}, clear=True),
        ):
            evidence = transport.invoke_stage_a(
                request,
                authorization=auth,
                budget=budget,
                stage_budget=stage_budget,
                bounds=bounds,
                now=NOW,
            )

        self.assertEqual("2xx", evidence.http_status_class)
        self.assertEqual("NULL", evidence.final_content_state)
        self.assertIsNone(evidence.raw_response_text)
        self.assertFalse(evidence.provider_response_scoreable)
        self.assertTrue(evidence.reasoning_present)
        self.assertEqual(20, evidence.reasoning_token_count)
        self.assertNotIn("private reasoning", json.dumps(evidence.safe_payload()))
        self.assertNotIn("TEST_KEY", json.dumps(evidence.safe_payload()))

    def test_reasoning_is_never_joined_to_valid_final_content(self) -> None:
        final = '{"schema_version":"JIANGHE_RUNTIME_RESPONSE_V0_1"}'
        body = {
            "id": "response-2",
            "model": DEEPSEEK_VISION_SPEC.model_id,
            "choices": [
                {
                    "finish_reason": "stop",
                    "message": {
                        "content": final,
                        "reasoning_content": "do not normalize this",
                        "reasoning_details": [{"text": "or this"}],
                    },
                }
            ],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }
        request = _request()
        rate = _rate(DEEPSEEK_VISION_SPEC)
        auth = _authorization(DEEPSEEK_VISION_SPEC)
        transport = StageAProviderTransport(
            DEEPSEEK_VISION_SPEC,
            http_post=lambda *_: HttpResponse(200, {}, json.dumps(body).encode()),
        )
        with (
            patch("src.jianghe_stage_a_runtime.load_owner_paid_call_authorization", return_value=auth),
            patch("src.jianghe_stage_a_runtime.load_current_repository_rate_card", return_value=rate),
            patch.dict(os.environ, {DEEPSEEK_VISION_SPEC.api_key_env: "TEST_KEY"}, clear=True),
        ):
            evidence = transport.invoke_stage_a(
                request,
                authorization=auth,
                budget=CnyBudgetLedger(),
                stage_budget=StageABudgetEnvelope(),
                bounds=exact_invocation_bounds(transport, request, rate_card=rate),
                now=NOW,
            )
        self.assertEqual(final, evidence.raw_response_text)
        self.assertNotIn("do not normalize", evidence.raw_response_text)
        self.assertNotIn("or this", evidence.raw_response_text)

    def test_raw_minimax_think_mixed_content_remains_unmodified(self) -> None:
        mixed = '<think>private</think>{"schema_version":"JIANGHE_RUNTIME_RESPONSE_V0_1"}'
        self.assertEqual(mixed, StageAProviderTransport._extract_text({
            "choices": [{"message": {"content": mixed}}]
        }))
        with self.assertRaises(ValueError):
            JiangheResponseNormalizer().normalize(mixed)


class StageAV02PlanAndCarryForwardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        rebuilt = canonical_json_bytes(build_v0_2_plan())
        cls.plan = VerifiedFrozenStageAPlan.load(
            committed_path=FROZEN_PLAN_PATH,
            deterministic_rebuild_bytes=rebuilt,
        )

    def test_v0_1_plan_bytes_still_rebuild_unchanged(self) -> None:
        path = Path(__file__).resolve().parents[1] / "docs/evidence/JIANGHE_STAGE_A_FROZEN_PLAN_V0_1.json"
        self.assertEqual(_repository_blob_bytes(path), canonical_json_bytes(build_v0_1_plan()))

    def test_v0_2_deterministic_plan_carries_attempt_001(self) -> None:
        snapshot = self.plan.carry_forward_snapshot()
        self.assertEqual(1, snapshot.total_attempts)
        self.assertEqual(Decimal("0.219222"), snapshot.stage_accounted_cny)
        self.assertEqual(Decimal("0.219222"), snapshot.provider_accounted_cny["DEEPSEEK"])
        self.assertIn("DEEPSEEK:1", snapshot.attempted_slots)
        self.assertEqual(14, self.plan.payload["future_executable_call_count"])
        self.assertEqual("refs/heads/stage-a-live-state-v0-2", DEFAULT_REMOTE_REF)
        self.assertEqual(15, self.plan.payload["max_total_stage_a_calls"])
        self.assertEqual(5, self.plan.payload["max_calls_per_provider"])
        self.assertEqual("18", self.plan.payload["stage_a_total_cap_cny"])
        self.assertEqual("6", self.plan.payload["stage_a_provider_cap_cny"])

        provider_totals = {
            row["provider_id"]: Decimal(row["five_slot_worst_case_cny"])
            for row in self.plan.payload["providers"]
        }
        self.assertEqual(Decimal("5.97792"), provider_totals["KIMI"])
        self.assertEqual(Decimal("0.810336"), provider_totals["DEEPSEEK"])
        self.assertEqual(Decimal("1.1617368"), provider_totals["MINIMAX"])
        self.assertTrue(all(value <= Decimal("6") for value in provider_totals.values()))
        self.assertEqual(
            Decimal("7.9499928"),
            Decimal(self.plan.payload["stage_a_total_worst_case_including_carry_forward_cny"]),
        )

    def test_v0_2_production_store_rejects_v0_1_or_caller_selected_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "caller-selected"):
                GitRemoteLedgerStore(
                    repository=Path(tmp),
                    remote_ref="refs/heads/stage-a-live-state-v0-1",
                )

    def test_empty_v0_2_remote_events_do_not_reset_accounting(self) -> None:
        snapshot = RemoteExecutionLedger.empty(self.plan).snapshot()
        self.assertEqual(1, snapshot.total_attempts)
        self.assertEqual(Decimal("0.219222"), snapshot.project_accounted_cny)
        self.assertEqual(1, snapshot.provider_attempts["DEEPSEEK"])

    def test_deepseek_slot_1_is_non_executable(self) -> None:
        with self.assertRaisesRegex(
            SlotAlreadyAttemptedError,
            "CARRY_FORWARD_ATTEMPTED__NON_RETRYABLE",
        ):
            prepare_frozen_slot(
                self.plan,
                provider_id="DEEPSEEK",
                slot=1,
                now=NOW,
            )

    def test_null_and_empty_2xx_are_provider_response_terminal_without_retry(self) -> None:
        for content, expected_state in ((None, "NULL"), ("", "TEXT_EMPTY")):
            with self.subTest(state=expected_state), tempfile.TemporaryDirectory() as tmp:
                calls = {"count": 0}

                def post(*_):
                    calls["count"] += 1
                    body = {
                        "id": "terminal-test",
                        "model": DEEPSEEK_VISION_SPEC.model_id,
                        "choices": [{
                            "finish_reason": "stop",
                            "message": {"content": content, "reasoning_content": "private"},
                        }],
                        "usage": {"prompt_tokens": 10, "completion_tokens": 5},
                    }
                    return HttpResponse(200, {}, json.dumps(body).encode())

                journal = StageAExecutionJournal(Path(tmp) / "journal.jsonl", self.plan)
                with patch.dict(
                    os.environ,
                    {DEEPSEEK_VISION_SPEC.api_key_env: "TEST_KEY"},
                    clear=True,
                ):
                    result = execute_frozen_slot(
                        self.plan,
                        journal,
                        provider_id="DEEPSEEK",
                        slot=2,
                        now=NOW,
                        http_post=post,
                    )
                self.assertEqual(1, calls["count"])
                self.assertEqual("NON_SCOREABLE_PROVIDER_RESPONSE", result.status)
                events = journal.verified_events()
                provider_evidence = events[-1]["provider_evidence"]
                self.assertEqual(expected_state, provider_evidence["final_content_state"])
                self.assertNotIn("private", json.dumps(provider_evidence))

    def test_missing_request_id_and_invalid_usage_fail_closed_without_retry(self) -> None:
        cases = (
            (2, {"prompt_tokens": 10, "completion_tokens": 5}, None, "missing-id"),
            (3, None, "response-without-usage", "missing-usage"),
            (4, {"prompt_tokens": "bad", "completion_tokens": 5}, "bad-usage", "bad-usage"),
        )
        for slot, usage, response_id, label in cases:
            with self.subTest(case=label), tempfile.TemporaryDirectory() as tmp:
                calls = {"count": 0}

                def post(*_):
                    calls["count"] += 1
                    body = {
                        "model": DEEPSEEK_VISION_SPEC.model_id,
                        "choices": [{
                            "finish_reason": "stop",
                            "message": {"content": '{"schema_version":"JIANGHE_RUNTIME_RESPONSE_V0_1"}'},
                        }],
                    }
                    if response_id is not None:
                        body["id"] = response_id
                    if usage is not None:
                        body["usage"] = usage
                    return HttpResponse(200, {}, json.dumps(body).encode())

                prepared = prepare_frozen_slot(
                    self.plan, provider_id="DEEPSEEK", slot=slot, now=NOW
                )
                journal = StageAExecutionJournal(Path(tmp) / "journal.jsonl", self.plan)
                with patch.dict(
                    os.environ,
                    {DEEPSEEK_VISION_SPEC.api_key_env: "TEST_KEY"},
                    clear=True,
                ):
                    result = execute_frozen_slot(
                        self.plan,
                        journal,
                        provider_id="DEEPSEEK",
                        slot=slot,
                        now=NOW,
                        http_post=post,
                    )
                self.assertEqual(1, calls["count"])
                self.assertEqual("NON_SCOREABLE_PROVIDER_RESPONSE", result.status)
                self.assertEqual(prepared.worst_case_cny, result.accounted_cny)
                safe_evidence = journal.verified_events()[-1]["provider_evidence"]
                self.assertNotIn("TEST_KEY", json.dumps(safe_evidence))
                if response_id is None:
                    self.assertIsNone(safe_evidence["provider_request_id"])
                if usage is None or label == "bad-usage":
                    self.assertIsNone(safe_evidence["usage"])

    def test_deepseek_malformed_or_non_2xx_remains_transport_failure(self) -> None:
        responses = (
            (2, HttpResponse(200, {}, b"not-json")),
            (3, HttpResponse(503, {}, b"{}")),
        )
        for slot, response in responses:
            with self.subTest(slot=slot), tempfile.TemporaryDirectory() as tmp:
                calls = {"count": 0}

                def post(*_):
                    calls["count"] += 1
                    return response

                prepared = prepare_frozen_slot(
                    self.plan, provider_id="DEEPSEEK", slot=slot, now=NOW
                )
                journal = StageAExecutionJournal(Path(tmp) / "journal.jsonl", self.plan)
                with patch.dict(
                    os.environ,
                    {DEEPSEEK_VISION_SPEC.api_key_env: "TEST_KEY"},
                    clear=True,
                ):
                    result = execute_frozen_slot(
                        self.plan,
                        journal,
                        provider_id="DEEPSEEK",
                        slot=slot,
                        now=NOW,
                        http_post=post,
                    )
                self.assertEqual(1, calls["count"])
                self.assertEqual("TRANSPORT_FAILURE", result.status)
                self.assertEqual(prepared.worst_case_cny, result.accounted_cny)


if __name__ == "__main__":
    unittest.main()

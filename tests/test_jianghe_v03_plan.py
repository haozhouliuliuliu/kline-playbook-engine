"""V0.3 deterministic frozen plan focused tests."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import unittest

from src.jianghe_v03_plan import (
    build_v03_frozen_plan,
    pretty_plan_bytes,
)
from src.jianghe_v03_runtime import (
    HISTORICAL_PROJECT_ACCOUNTED_CNY,
    V03_EXECUTION_ORDER,
    V03ProviderTransport,
    v03_capability_answer_contract_identity,
    v03_slot_identity,
)
from tools.run_jianghe_v03_slot import _build_request, _runtime_worst_case_cny


class V03PlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = build_v03_frozen_plan()

    def test_plan_is_deterministic(self) -> None:
        again = build_v03_frozen_plan()
        self.assertEqual(pretty_plan_bytes(self.plan), pretty_plan_bytes(again))

    def test_plan_identity_present_and_self_consistent(self) -> None:
        identity = self.plan["plan_identity"]
        self.assertIsInstance(identity, str)
        self.assertEqual(64, len(identity))

    def test_common_exam_identity_present(self) -> None:
        self.assertEqual(64, len(self.plan["common_exam_identity"]))
        self.assertIn("png_sha256", self.plan["common_exam"])
        self.assertEqual(64, len(self.plan["common_exam"]["png_sha256"]))
        self.assertTrue(self.plan["common_exam"]["outcome_future_ban"])
        self.assertTrue(self.plan["common_exam"]["production_json_ban"])

    def test_historical_carry_forward_and_hard_cap(self) -> None:
        self.assertEqual(Decimal("0.270021"), Decimal(self.plan["historical_project_accounted_cny"]))
        self.assertEqual(Decimal("100"), Decimal(self.plan["hard_project_cap_cny"]))
        total = Decimal(self.plan["total_worst_case_including_historical_cny"])
        self.assertLessEqual(total, Decimal("100"))
        self.assertEqual(
            Decimal(self.plan["theoretical_max_remaining_cny"]),
            Decimal("100") - Decimal("0.270021"),
        )

    def test_three_v03_slots_and_execution_order(self) -> None:
        self.assertEqual(list(V03_EXECUTION_ORDER), self.plan["execution_order"])
        providers = {row["provider_id"]: row for row in self.plan["providers"]}
        self.assertEqual(set(providers), {"DEEPSEEK", "MINIMAX", "KIMI"})
        for provider_id in V03_EXECUTION_ORDER:
            row = providers[provider_id]
            self.assertEqual(v03_slot_identity(provider_id), row["slot_identity"])
            self.assertEqual(131072, row["max_output_tokens"])
            self.assertEqual(900, row["network_timeout_seconds"])
            self.assertEqual("NONE", row["response_format_policy"])
            self.assertGreater(Decimal(row["worst_case_reservation_cny"]), 0)
            self.assertEqual(64, len(row["provider_inference_config_identity"]))
            self.assertEqual(64, len(row["attempt_identity"]))

    def test_capability_answer_contract_is_shared_and_json_free(self) -> None:
        contract = self.plan["capability_answer_contract"]
        self.assertFalse(contract["production_json_required"])
        self.assertFalse(contract["hint_expected_answer"])
        self.assertEqual("CLEAR_HEADED_TEXT", contract["output_format"])
        self.assertEqual(
            v03_capability_answer_contract_identity(),
            self.plan["prompt_identities"]["capability_answer_contract_identity"],
        )

    def test_no_historical_gates_and_v03_remote_ref(self) -> None:
        self.assertNotIn("stage_a_total_cap_cny", self.plan)
        self.assertNotIn("stage_a_provider_cap_cny", self.plan)
        self.assertNotIn("max_calls_per_provider", self.plan)
        self.assertEqual("FORBIDDEN", self.plan["automatic_retry"])
        self.assertEqual("NO", self.plan["outcome_access"])
        self.assertEqual("refs/heads/stage-a-live-state-v0-3", self.plan["remote_ref"])

    def test_live_runner_builds_the_exact_frozen_common_exam(self) -> None:
        request, _, _, _, _ = _build_request(
            "DEEPSEEK",
            self.plan,
            datetime(2026, 8, 25, tzinfo=timezone.utc),
        )

        self.assertEqual(
            self.plan["common_exam_identity"],
            request.common_exam_identity.identity,
        )
        for field_name in (
            "selected_context_identity",
            "model_context_identity",
            "structured_observation_identity",
            "png_sha256",
            "visual_artifact_identity",
            "renderer_config_identity",
        ):
            self.assertEqual(
                self.plan["common_exam"][field_name],
                getattr(request.common_exam_identity, field_name),
            )

    def test_live_runner_start_uses_current_runtime_reservation(self) -> None:
        now = datetime(2026, 8, 25, tzinfo=timezone.utc)
        request, config, _, rate_card, _ = _build_request("MINIMAX", self.plan, now)
        transport = V03ProviderTransport(config)
        text_bound = transport.conservative_text_input_token_bound(request)

        expected = (
            Decimal(text_bound) * Decimal(rate_card.input_per_million)
            + Decimal(config.max_output_tokens) * Decimal(rate_card.output_per_million)
        ) / Decimal("1000000")

        self.assertEqual(Decimal("2.51055"), expected)
        frozen = next(
            row for row in self.plan["providers"] if row["provider_id"] == "MINIMAX"
        )
        self.assertNotEqual(expected, Decimal(frozen["worst_case_reservation_cny"]))
        self.assertEqual(
            expected,
            _runtime_worst_case_cny(request, transport, config, rate_card, 0),
        )


if __name__ == "__main__":
    unittest.main()

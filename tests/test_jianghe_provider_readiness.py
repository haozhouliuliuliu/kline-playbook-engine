from __future__ import annotations

from decimal import Decimal
import json
from pathlib import Path
import unittest

from src.jianghe_provider_readiness import (
    AUTH_FAILED,
    BALANCE_CHECK_FAILED,
    CREDENTIAL_MISSING,
    DEEPSEEK_BALANCE_ENDPOINT,
    INSUFFICIENT_EXISTING_FUNDS,
    KIMI_BALANCE_ENDPOINT,
    READY_EXISTING_FUNDS,
    UNRESOLVED_NON_CNY_BALANCE,
    UNRESOLVED_NO_READ_ONLY_PAYGO_BALANCE_API,
    check_all_provider_readiness,
    check_provider_readiness,
    required_stage_a_cny,
)
from src.jianghe_stage_a_runner import FROZEN_PLAN_PATH, VerifiedFrozenStageAPlan
from tools.build_jianghe_stage_a_frozen_plan_v0_2 import build_frozen_plan


def _pretty_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")


class ProviderBalanceReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = VerifiedFrozenStageAPlan.load(
            committed_path=FROZEN_PLAN_PATH,
            deterministic_rebuild_bytes=_pretty_bytes(build_frozen_plan()),
        )

    def test_missing_credentials_make_zero_network_calls(self) -> None:
        calls: list[str] = []

        def fake_get(url, headers, timeout):
            calls.append(url)
            raise AssertionError("network must not be reached")

        results = check_all_provider_readiness(
            self.plan,
            credential_lookup=lambda name: None,
            http_get=fake_get,
        )
        self.assertEqual(calls, [])
        self.assertEqual([item.status for item in results], [CREDENTIAL_MISSING] * 3)
        self.assertTrue(all(not item.credential_present for item in results))
        self.assertTrue(all(not item.balance_checked for item in results))
        self.assertTrue(all(not item.model_endpoint_called for item in results))
        self.assertTrue(all(not item.credential_value_exposed for item in results))

    def test_kimi_uses_only_official_read_only_balance_endpoint_and_can_be_ready(self) -> None:
        secret = "kimi-secret-never-output"
        required = required_stage_a_cny(self.plan, "KIMI")
        calls = []

        def fake_get(url, headers, timeout):
            calls.append((url, dict(headers), timeout))
            body = json.dumps(
                {
                    "status": True,
                    "code": 0,
                    "scode": "0x0",
                    "data": {
                        "available_balance": str(required + Decimal("1")),
                        "voucher_balance": "0",
                        "cash_balance": str(required + Decimal("1")),
                    },
                }
            ).encode("utf-8")
            return 200, body

        result = check_provider_readiness(
            self.plan,
            provider_id="KIMI",
            credential_lookup=lambda name: secret,
            http_get=fake_get,
        )
        self.assertEqual(result.status, READY_EXISTING_FUNDS)
        self.assertEqual(result.shortfall_cny, Decimal("0"))
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0], KIMI_BALANCE_ENDPOINT)
        self.assertEqual(calls[0][1]["Authorization"], f"Bearer {secret}")
        rendered = json.dumps(result.to_dict(), sort_keys=True)
        self.assertNotIn(secret, rendered)
        self.assertFalse(result.model_endpoint_called)

    def test_kimi_insufficient_balance_reports_exact_frozen_shortfall_without_funding(self) -> None:
        required = required_stage_a_cny(self.plan, "KIMI")
        existing = Decimal("1.25")

        def fake_get(url, headers, timeout):
            return 200, json.dumps(
                {"status": True, "data": {"available_balance": str(existing)}}
            ).encode("utf-8")

        result = check_provider_readiness(
            self.plan,
            provider_id="KIMI",
            credential_lookup=lambda name: "secret",
            http_get=fake_get,
        )
        self.assertEqual(result.status, INSUFFICIENT_EXISTING_FUNDS)
        self.assertEqual(result.existing_balance_cny, existing)
        self.assertEqual(result.shortfall_cny, required - existing)
        self.assertNotIn("recharge", result.balance_method.lower())

    def test_deepseek_uses_only_official_read_only_balance_endpoint_and_cny_row(self) -> None:
        required = required_stage_a_cny(self.plan, "DEEPSEEK")
        calls = []

        def fake_get(url, headers, timeout):
            calls.append(url)
            return 200, json.dumps(
                {
                    "is_available": True,
                    "balance_infos": [
                        {
                            "currency": "USD",
                            "total_balance": "99",
                            "granted_balance": "0",
                            "topped_up_balance": "99",
                        },
                        {
                            "currency": "CNY",
                            "total_balance": str(required),
                            "granted_balance": "0",
                            "topped_up_balance": str(required),
                        },
                    ],
                }
            ).encode("utf-8")

        result = check_provider_readiness(
            self.plan,
            provider_id="DEEPSEEK",
            credential_lookup=lambda name: "secret",
            http_get=fake_get,
        )
        self.assertEqual(calls, [DEEPSEEK_BALANCE_ENDPOINT])
        self.assertEqual(result.status, READY_EXISTING_FUNDS)
        self.assertEqual(result.existing_balance_cny, required)

    def test_deepseek_non_cny_only_balance_fails_closed_without_fx_guess(self) -> None:
        def fake_get(url, headers, timeout):
            return 200, json.dumps(
                {
                    "is_available": True,
                    "balance_infos": [
                        {
                            "currency": "USD",
                            "total_balance": "100",
                            "granted_balance": "0",
                            "topped_up_balance": "100",
                        }
                    ],
                }
            ).encode("utf-8")

        result = check_provider_readiness(
            self.plan,
            provider_id="DEEPSEEK",
            credential_lookup=lambda name: "secret",
            http_get=fake_get,
        )
        self.assertEqual(result.status, UNRESOLVED_NON_CNY_BALANCE)
        self.assertIsNone(result.existing_balance_cny)
        self.assertIsNone(result.shortfall_cny)

    def test_minimax_paygo_never_uses_model_call_as_balance_probe(self) -> None:
        calls = []

        def fake_get(url, headers, timeout):
            calls.append(url)
            raise AssertionError("MiniMax paygo readiness must remain non-network here")

        result = check_provider_readiness(
            self.plan,
            provider_id="MINIMAX",
            credential_lookup=lambda name: "secret",
            http_get=fake_get,
        )
        self.assertEqual(calls, [])
        self.assertEqual(result.status, UNRESOLVED_NO_READ_ONLY_PAYGO_BALANCE_API)
        self.assertFalse(result.balance_checked)
        self.assertFalse(result.model_endpoint_called)

    def test_auth_failure_is_non_billable_terminal_readiness_result(self) -> None:
        calls = []

        def fake_get(url, headers, timeout):
            calls.append(url)
            return 401, b'{"error":"invalid key"}'

        result = check_provider_readiness(
            self.plan,
            provider_id="KIMI",
            credential_lookup=lambda name: "secret",
            http_get=fake_get,
        )
        self.assertEqual(len(calls), 1)
        self.assertEqual(result.status, AUTH_FAILED)
        self.assertFalse(result.balance_checked)
        self.assertFalse(result.model_endpoint_called)

    def test_non_200_balance_failure_is_not_retried(self) -> None:
        calls = []

        def fake_get(url, headers, timeout):
            calls.append(url)
            return 500, b"{}"

        result = check_provider_readiness(
            self.plan,
            provider_id="DEEPSEEK",
            credential_lookup=lambda name: "secret",
            http_get=fake_get,
        )
        self.assertEqual(len(calls), 1)
        self.assertEqual(result.status, BALANCE_CHECK_FAILED)

    def test_malformed_balance_payload_fails_closed(self) -> None:
        def fake_get(url, headers, timeout):
            return 200, b"not-json"

        result = check_provider_readiness(
            self.plan,
            provider_id="KIMI",
            credential_lookup=lambda name: "secret",
            http_get=fake_get,
        )
        self.assertEqual(result.status, BALANCE_CHECK_FAILED)
        self.assertIsNone(result.existing_balance_cny)

    def test_required_stage_a_amount_is_bound_to_frozen_plan(self) -> None:
        for provider in ("KIMI", "DEEPSEEK", "MINIMAX"):
            expected = Decimal(
                str(self.plan.provider_row(provider)["future_executable_worst_case_cny"])
            )
            self.assertEqual(required_stage_a_cny(self.plan, provider), expected)
            self.assertLessEqual(expected, Decimal("6"))

    def test_readiness_module_contains_no_model_completion_endpoint_literal(self) -> None:
        source = Path("src/jianghe_provider_readiness.py").read_text(encoding="utf-8")
        self.assertNotIn("chat/completions", source)
        self.assertNotIn("invoke_stage_a", source)
        self.assertNotIn("StageAProviderTransport", source)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "jianghe_prespend_runtime.py"
TESTS = ROOT / "tests" / "test_jianghe_prespend_repair.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one old snippet, found {count}")
    return text.replace(old, new, 1)


runtime = RUNTIME.read_text(encoding="utf-8")

runtime = replace_once(
    runtime,
    '''    if entry.get("status") != "VERIFIED_CURRENT_FOR_SPEND_GUARD":\n        raise BudgetGuardError(f"provider pricing is not spend-eligible: {entry.get('status')}")\n''',
    '''    allowed_statuses = {\n        "VERIFIED_CURRENT_FOR_SPEND_GUARD",\n        "OWNER_APPROVED_CONSERVATIVE_FAMILY_INHERITANCE_FOR_SPEND_GUARD",\n    }\n    if entry.get("status") not in allowed_statuses:\n        raise BudgetGuardError(f"provider pricing is not spend-eligible: {entry.get('status')}")\n''',
    "rate-card status policy",
)

runtime = replace_once(
    runtime,
    '''    try:\n        effective_at = datetime.fromisoformat(str(entry["effective_at"]))\n        expires_at = datetime.fromisoformat(str(entry["expires_at"]))\n        fixed_tokens = int(entry["fixed_input_tokens_per_image"])\n    except (KeyError, TypeError, ValueError) as error:\n        raise BudgetGuardError("pricing authority entry is incomplete") from error\n    card = RateCard(\n''',
    '''    try:\n        effective_at = datetime.fromisoformat(str(entry["effective_at"]))\n        expires_at = datetime.fromisoformat(str(entry["expires_at"]))\n        image_billing_mode = str(entry["image_billing_mode"])\n        raw_fixed_tokens = entry.get("fixed_input_tokens_per_image")\n        fixed_tokens = None if raw_fixed_tokens is None else int(raw_fixed_tokens)\n    except (KeyError, TypeError, ValueError) as error:\n        raise BudgetGuardError("pricing authority entry is incomplete") from error\n    card = RateCard(\n''',
    "optional fixed image tokens",
)

runtime = replace_once(
    runtime,
    '''        image_billing_mode=str(entry.get("image_billing_mode")),\n        fixed_input_tokens_per_image=fixed_tokens,\n''',
    '''        image_billing_mode=image_billing_mode,\n        fixed_input_tokens_per_image=fixed_tokens,\n''',
    "validated image billing mode",
)

runtime = replace_once(
    runtime,
    '''                "max_tokens": request.max_output_tokens,\n                "stream": False,\n                "tools": [],\n''',
    '''                "max_completion_tokens": request.max_output_tokens,\n                "stream": False,\n                "tools": [],\n''',
    "MiniMax completion-token field",
)

runtime = replace_once(
    runtime,
    '''        if rate_card.image_billing_mode != "FIXED_INPUT_TOKENS_PER_IMAGE":\n            raise BudgetGuardError("dynamic/ambiguous image billing has no deterministic pre-call bound")\n        expected_image_tokens = len(request.visuals) * int(rate_card.fixed_input_tokens_per_image or 0)\n        if bounds.max_image_tokens != expected_image_tokens:\n            raise BudgetGuardError(\n                "image-token reservation must exactly match the repository billing authority"\n            )\n''',
    '''        if rate_card.image_billing_mode == "FIXED_INPUT_TOKENS_PER_IMAGE":\n            expected_image_tokens = (\n                len(request.visuals) * int(rate_card.fixed_input_tokens_per_image or 0)\n            )\n        elif rate_card.image_billing_mode == "INPUT_TOKENS":\n            # The exact serialized multimodal payload already contains the image data URL.\n            # The X2-bytes+8192 policy therefore supplies a deterministic pre-network\n            # upper bound without inventing a provider-specific fixed image conversion.\n            expected_image_tokens = 0\n        else:\n            raise BudgetGuardError("unknown image billing mode fails closed before network")\n        if bounds.max_image_tokens != expected_image_tokens:\n            raise BudgetGuardError(\n                "image-token reservation must exactly match the repository billing authority"\n            )\n''',
    "input-token image billing",
)

RUNTIME.write_text(runtime, encoding="utf-8", newline="\n")


tests = TESTS.read_text(encoding="utf-8")

tests = replace_once(
    tests,
    '''    def test_unresolved_provider_image_billing_fails_closed_before_network(self):\n        for spec in (DEEPSEEK_VISION_SPEC, MINIMAX_M3_SPEC):\n            with self.subTest(provider=spec.provider_id):\n                with self.assertRaises(BudgetGuardError):\n                    load_current_repository_rate_card(spec, now=NOW)\n\n''',
    '''    def test_deepseek_flash_inherited_peak_rate_is_spend_guard_ready(self):\n        card = load_current_repository_rate_card(DEEPSEEK_VISION_SPEC, now=NOW)\n        self.assertEqual(card.currency, "CNY")\n        self.assertEqual(card.input_per_million, Decimal("3.00"))\n        self.assertEqual(card.output_per_million, Decimal("9.00"))\n        self.assertEqual(card.image_billing_mode, "FIXED_INPUT_TOKENS_PER_IMAGE")\n        self.assertEqual(card.fixed_input_tokens_per_image, 384)\n        self.assertIsNotNone(card.repository_authority_identity)\n\n    def test_minimax_high_tier_input_token_rate_is_spend_guard_ready(self):\n        card = load_current_repository_rate_card(MINIMAX_M3_SPEC, now=NOW)\n        self.assertEqual(card.currency, "CNY")\n        self.assertEqual(card.input_per_million, Decimal("4.20"))\n        self.assertEqual(card.output_per_million, Decimal("16.80"))\n        self.assertEqual(card.image_billing_mode, "INPUT_TOKENS")\n        self.assertIsNone(card.fixed_input_tokens_per_image)\n        self.assertIsNotNone(card.repository_authority_identity)\n\n    def test_minimax_uses_current_completion_token_field(self):\n        payload = DomesticProviderTransport(MINIMAX_M3_SPEC).build_payload(_request())\n        self.assertEqual(payload["max_completion_tokens"], 200)\n        self.assertNotIn("max_tokens", payload)\n\n    def test_deepseek_and_minimax_pass_pricing_and_bounds_before_missing_credential(self):\n        cases = (\n            (DEEPSEEK_VISION_SPEC, "DEEPSEEK_API_KEY", 384),\n            (MINIMAX_M3_SPEC, "MINIMAX_API_KEY", 0),\n        )\n        for spec, env_name, expected_image_tokens in cases:\n            with self.subTest(provider=spec.provider_id):\n                previous = os.environ.pop(env_name, None)\n                calls = []\n                try:\n                    request = _request()\n                    transport = DomesticProviderTransport(\n                        spec, http_post=lambda *args: calls.append(args)  # type: ignore[arg-type]\n                    )\n                    auth = _synthetic_auth(spec)\n                    ledger = CnyBudgetLedger()\n                    bounds = InvocationBounds(\n                        transport.conservative_text_input_token_bound(request),\n                        expected_image_tokens,\n                        request.max_output_tokens,\n                    )\n                    with patch(\n                        "src.jianghe_prespend_runtime.load_owner_paid_call_authorization",\n                        return_value=auth,\n                    ):\n                        with self.assertRaises(ProviderTransportError):\n                            transport.invoke(\n                                request, authorization=auth, budget=ledger, bounds=bounds,\n                                fx=None, now=NOW,\n                            )\n                    self.assertEqual(calls, [])\n                    self.assertEqual(ledger.spent_cny, Decimal("0"))\n                    self.assertEqual(ledger.remaining_cny, HARD_PROJECT_CAP_CNY)\n                finally:\n                    if previous is not None:\n                        os.environ[env_name] = previous\n\n''',
    "current pricing authority tests",
)

TESTS.write_text(tests, encoding="utf-8", newline="\n")

print("PROVIDER_PRICING_PATCH_APPLIED=YES")

from pathlib import Path


def replace_exact(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one old snippet, found {count}")
    p.write_text(text.replace(old, new), encoding="utf-8")


replace_exact(
    "src/jianghe_prespend_runtime.py",
    '    endpoint="https://api.minimaxi.com/v1/text/chatcompletion_v2",\n',
    '    endpoint="https://api.minimaxi.com/v1/chat/completions",\n',
)

replace_exact(
    "src/jianghe_prespend_runtime.py",
    '                    "max_tokens": request.max_output_tokens, "stream": False, "tools": []}\n',
    '                    "max_completion_tokens": request.max_output_tokens, "stream": False, "tools": []}\n',
)

replace_exact(
    "src/jianghe_prespend_runtime.py",
    '        if text_input_tokens + image_tokens > bounds.total_input_tokens or output_tokens > bounds.max_output_tokens:\n',
    '        # OpenAI-compatible prompt_tokens is the total billed prompt/input token count,\n        # including multimodal input. image_tokens is retained only as provider audit detail;\n        # adding it again would double-count visual input.\n        if (text_input_tokens > bounds.total_input_tokens\n                or image_tokens > bounds.max_image_tokens\n                or output_tokens > bounds.max_output_tokens):\n',
)
replace_exact(
    "src/jianghe_prespend_runtime.py",
    '            Decimal(text_input_tokens + image_tokens) * rate_card.input_per_million\n',
    '            Decimal(text_input_tokens) * rate_card.input_per_million\n',
)

marker = '\n\n@dataclass(frozen=True)\nclass FxAuthority:'
insert = r'''

KIMI_K3_RATE_AUTHORITY = "https://platform.kimi.ai/"
MINIMAX_M3_RATE_AUTHORITY = "https://platform.minimax.io/subscribe/token-plan?tab=api-enterprise"
DEEPSEEK_VISION_RATE_AUTHORITY_REQUIRED = "https://api-docs.deepseek.com/"


def conservative_builtin_rate_card(
    spec: ProviderSpec,
    bounds: InvocationBounds,
    *,
    effective_at: datetime,
    expires_at: datetime,
) -> RateCard:
    """Return only rate cards that current first-party evidence fixes unambiguously.

    Kimi uses cache-miss input pricing. MiniMax uses the more expensive >512K
    tier whenever the pre-call total input bound can cross that threshold.
    DeepSeek Vision Exp deliberately has no built-in price: current first-party
    pages available to the project are temporally inconsistent, so a paid call
    must remain blocked until a fresh Vision-specific first-party snapshot is
    formally bound in code/authority.
    """
    if spec == KIMI_K3_SPEC:
        return RateCard(
            provider_id=spec.provider_id,
            model_id=spec.model_id,
            currency="USD",
            input_per_million=Decimal("3.00"),
            output_per_million=Decimal("15.00"),
            image_tokens_billed_as_input=True,
            authority_uri=KIMI_K3_RATE_AUTHORITY,
            effective_at=effective_at,
            expires_at=expires_at,
        )
    if spec == MINIMAX_M3_SPEC:
        if bounds.total_input_tokens <= 512_000:
            input_price, output_price = Decimal("0.30"), Decimal("1.20")
        else:
            input_price, output_price = Decimal("0.60"), Decimal("2.40")
        return RateCard(
            provider_id=spec.provider_id,
            model_id=spec.model_id,
            currency="USD",
            input_per_million=input_price,
            output_per_million=output_price,
            image_tokens_billed_as_input=True,
            authority_uri=MINIMAX_M3_RATE_AUTHORITY,
            effective_at=effective_at,
            expires_at=expires_at,
        )
    if spec == DEEPSEEK_VISION_SPEC:
        raise BudgetGuardError(
            "DeepSeek Vision Exp paid calls require a fresh Vision-specific first-party "
            "pricing snapshot; stale/base-model prices are not spend authority"
        )
    raise BudgetGuardError("provider has no approved conservative rate-card policy")


def validate_rate_card_for_call(
    spec: ProviderSpec, rate_card: RateCard, bounds: InvocationBounds
) -> None:
    """Prevent callers from substituting a cheaper arbitrary rate card."""
    if spec == DEEPSEEK_VISION_SPEC:
        raise BudgetGuardError(
            "DeepSeek Vision Exp pricing authority is not yet independently verified; fail closed"
        )
    expected = conservative_builtin_rate_card(
        spec,
        bounds,
        effective_at=rate_card.effective_at,
        expires_at=rate_card.expires_at,
    )
    comparable = (
        "provider_id", "model_id", "currency", "input_per_million",
        "output_per_million", "image_tokens_billed_as_input", "authority_uri",
    )
    if any(getattr(rate_card, name) != getattr(expected, name) for name in comparable):
        raise BudgetGuardError("rate card does not match the current conservative provider policy")
'''

p = Path("src/jianghe_prespend_runtime.py")
text = p.read_text(encoding="utf-8")
if text.count(marker) != 1:
    raise SystemExit("rate-card insertion marker mismatch")
p.write_text(text.replace(marker, insert + marker), encoding="utf-8")

replace_exact(
    "src/jianghe_prespend_runtime.py",
    '        if bounds.max_output_tokens != request.max_output_tokens:\n            raise BudgetGuardError("request output cap must equal reserved output cap")\n        reservation = budget.reserve(self.spec, rate_card, bounds, fx=fx, now=now)\n',
    '        if bounds.max_output_tokens != request.max_output_tokens:\n            raise BudgetGuardError("request output cap must equal reserved output cap")\n        validate_rate_card_for_call(self.spec, rate_card, bounds)\n        reservation = budget.reserve(self.spec, rate_card, bounds, fx=fx, now=now)\n',
)

replace_exact(
    "src/jianghe_prespend_runtime.py",
    '    "ProviderUsage", "RateCard", "SelectedContextDocument", "SelectedJiangheContextArtifact",\n',
    '    "ProviderUsage", "RateCard", "conservative_builtin_rate_card", "validate_rate_card_for_call",\n    "KIMI_K3_RATE_AUTHORITY", "MINIMAX_M3_RATE_AUTHORITY",\n    "SelectedContextDocument", "SelectedJiangheContextArtifact",\n',
)

# Extend focused tests with provider-contract and rate-card adversarial cases.
p = Path("tests/test_jianghe_prespend_repair.py")
text = p.read_text(encoding="utf-8")
text = text.replace(
    '    RateCard,\n',
    '    RateCard,\n    conservative_builtin_rate_card,\n',
    1,
)
marker = '\n\nif __name__ == "__main__":\n    unittest.main()\n'
if text.count(marker) != 1:
    raise SystemExit("provider focused-test insertion marker mismatch")
addition = r'''

class CurrentProviderContractTests(unittest.TestCase):
    def test_minimax_uses_current_domestic_openai_compatible_endpoint(self):
        self.assertEqual(
            MINIMAX_M3_SPEC.endpoint,
            "https://api.minimaxi.com/v1/chat/completions",
        )
        payload = DomesticProviderTransport(MINIMAX_M3_SPEC).build_payload(_request())
        self.assertIn("max_completion_tokens", payload)
        self.assertNotIn("max_tokens", payload)

    def test_kimi_builtin_rate_is_current_cache_miss_worst_case(self):
        bounds = InvocationBounds(1000, 500, 200)
        rate = conservative_builtin_rate_card(
            KIMI_K3_SPEC, bounds,
            effective_at=NOW - timedelta(hours=1), expires_at=NOW + timedelta(hours=1),
        )
        self.assertEqual(rate.currency, "USD")
        self.assertEqual(rate.input_per_million, Decimal("3.00"))
        self.assertEqual(rate.output_per_million, Decimal("15.00"))

    def test_minimax_builtin_rate_uses_context_threshold_conservatively(self):
        low = conservative_builtin_rate_card(
            MINIMAX_M3_SPEC, InvocationBounds(500_000, 10_000, 200),
            effective_at=NOW - timedelta(hours=1), expires_at=NOW + timedelta(hours=1),
        )
        high = conservative_builtin_rate_card(
            MINIMAX_M3_SPEC, InvocationBounds(500_000, 20_001, 200),
            effective_at=NOW - timedelta(hours=1), expires_at=NOW + timedelta(hours=1),
        )
        self.assertEqual((low.input_per_million, low.output_per_million),
                         (Decimal("0.30"), Decimal("1.20")))
        self.assertEqual((high.input_per_million, high.output_per_million),
                         (Decimal("0.60"), Decimal("2.40")))

    def test_deepseek_vision_unknown_current_price_fails_before_network(self):
        calls = []
        def fake_post(url, headers, body, timeout):
            calls.append(url)
            raise AssertionError("network must remain unreachable while price authority is ambiguous")
        transport = DomesticProviderTransport(DEEPSEEK_VISION_SPEC, http_post=fake_post)
        auth = PaidCallAuthorization(
            authorization_id="TEST_ONLY_SYNTHETIC_AUTH",
            authorization_evidence_sha256=hashlib.sha256(b"synthetic-auth").hexdigest(),
            provider_models=((DEEPSEEK_VISION_SPEC.provider_id, DEEPSEEK_VISION_SPEC.model_id),),
            hard_cap_cny=HARD_PROJECT_CAP_CNY, paid_calls_enabled=True,
        )
        with self.assertRaises(BudgetGuardError):
            transport.invoke(
                _request(), authorization=auth, budget=CnyBudgetLedger(),
                rate_card=_rate(DEEPSEEK_VISION_SPEC),
                bounds=InvocationBounds(1000, 500, 200), fx=None, now=NOW,
            )
        self.assertEqual(calls, [])

    def test_spend_transport_rejects_arbitrary_cheaper_rate_card(self):
        auth = PaidCallAuthorization(
            authorization_id="TEST_ONLY_SYNTHETIC_AUTH",
            authorization_evidence_sha256=hashlib.sha256(b"synthetic-auth").hexdigest(),
            provider_models=((KIMI_K3_SPEC.provider_id, KIMI_K3_SPEC.model_id),),
            hard_cap_cny=HARD_PROJECT_CAP_CNY, paid_calls_enabled=True,
        )
        with self.assertRaises(BudgetGuardError):
            DomesticProviderTransport(KIMI_K3_SPEC, http_post=lambda *args: None).invoke(
                _request(), authorization=auth, budget=CnyBudgetLedger(),
                rate_card=_rate(KIMI_K3_SPEC, currency="USD", input_price="0.01", output_price="0.01"),
                bounds=InvocationBounds(1000, 500, 200),
                fx=FxAuthority(
                    usd_to_cny=Decimal("8"), authority_uri="https://example.invalid/fx-snapshot",
                    effective_at=NOW - timedelta(hours=1), expires_at=NOW + timedelta(hours=1),
                ),
                now=NOW,
            )

    def test_prompt_token_usage_is_not_double_counted_with_image_detail(self):
        ledger = CnyBudgetLedger()
        rate = _rate(KIMI_K3_SPEC, input_price="10", output_price="10")
        reservation = ledger.reserve(
            KIMI_K3_SPEC, rate, InvocationBounds(1000, 500, 200), fx=None, now=NOW
        )
        actual = ledger.reconcile(
            reservation.reservation_id,
            text_input_tokens=100, image_tokens=20, output_tokens=0,
            rate_card=rate, fx=None, now=NOW,
        )
        self.assertEqual(actual, Decimal("0.001"))
'''
p.write_text(text.replace(marker, addition + marker), encoding="utf-8")

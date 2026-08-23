from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "jianghe_prespend_runtime.py"
TEST = ROOT / "tests" / "test_jianghe_prespend_repair.py"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one exact replacement, found {count}: {old[:80]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


# --- Runtime: current identities + exact repository authority for selected context ---
replace_once(
    RUNTIME,
    "import os\nimport re\nimport time\nfrom typing import Callable, Mapping\n",
    "import os\nfrom pathlib import Path\nimport re\nimport time\nfrom typing import Callable, Mapping\n",
)
replace_once(
    RUNTIME,
    "from src.jianghe_ai_trader import JiangheObservation\n",
    "from src.jianghe_ai_trader import JiangheObservation\n"
    "from src.jianghe_source_only_verification import (\n"
    "    ROOT as REPOSITORY_ROOT,\n"
    "    _repository_blob_bytes,\n"
    ")\n",
)
replace_once(
    RUNTIME,
    'CURRENT_PRIMARY_MANIFEST_IDENTITY = (\n    "60d4a1f9069a6dc33d04a82ce544d7525cd4bf2805c5b6e8dd9502d85bf39940"\n)\n',
    'CURRENT_PRIMARY_MANIFEST_IDENTITY = (\n    "f767253dc4c2d1b17f57b9adfdc903907a97df8d4697dbe0fae0f603427dbf36"\n)\n'
    'PRICING_AUTHORITY_PATH = (\n'
    '    REPOSITORY_ROOT / "docs" / "evidence" / "JIANGHE_PROVIDER_PRICING_AUTHORITY_V0_1.json"\n'
    ')\n',
)
replace_once(
    RUNTIME,
    '''_ALLOWED_CONTEXT_PATHS = frozenset(
    {
        "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md",
        "docs/research/jianghe/JIANGHE_STRATEGY_FAMILIES_V1_1.md",
        "docs/research/jianghe/JIANGHE_UNKNOWN_REGISTER_V1_1.md",
        "docs/research/jianghe/JIANGHE_PRIMARY_BRANCH_REGISTRY_V0_5.json",
        "docs/research/jianghe/JIANGHE_PRIMARY_CLAIM_MANIFEST_V0_1.json",
    }
)
''',
    '''_ALLOWED_CONTEXT_PATHS = frozenset(
    {
        "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md",
        "docs/research/jianghe/JIANGHE_STRATEGY_FAMILIES_V1_1.md",
        "docs/research/jianghe/JIANGHE_UNKNOWN_REGISTER_V1_1.md",
        "docs/research/jianghe/primary_mapping_draft_v0_1/JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_5.jsonl",
    }
)
_CONTEXT_SELECTION_POLICY_VERSION = "JIANGHE_CONTEXT_SELECTION_POLICY_V0_2"
_ALLOWED_VISIBLE_METADATA = {"session": frozenset({"DAY", "NIGHT", "UNKNOWN"})}
_AUDIT_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$")
''',
)
replace_once(
    RUNTIME,
    '''def _hash_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


''',
    '''def _hash_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def current_context_selection_policy_identity() -> str:
    """Identity of the only spend-eligible Jianghe context selection policy."""
    return _hash(
        {
            "version": _CONTEXT_SELECTION_POLICY_VERSION,
            "allowed_repository_paths": tuple(sorted(_ALLOWED_CONTEXT_PATHS)),
            "repository_byte_authority": "EXACT_COMMITTED_GIT_BLOB_BYTES",
            "outcome_future_fixture_authority": "FORBIDDEN",
            "selection_semantics": "EXACT_UTF8_SUBSTRING_ONLY",
        }
    )


''',
)
old_context_class = '''@dataclass(frozen=True)
class SelectedContextDocument:
    """One exact excerpt proven to originate from an allow-listed repo authority."""

    repository_path: str
    repository_content_sha256: str
    selected_text: str
    selected_text_sha256: str = field(init=False)
    identity: str = field(init=False)

    @classmethod
    def from_repository_document(
        cls, repository_path: str, repository_content: str, selected_text: str
    ) -> "SelectedContextDocument":
        if repository_path not in _ALLOWED_CONTEXT_PATHS:
            raise ValueError("context source path is not an authorized Jianghe authority")
        _require_text(repository_content, "repository_content")
        _require_text(selected_text, "selected_text")
        if selected_text not in repository_content:
            raise ValueError("selected context must be an exact substring of repository content")
        return cls(
            repository_path=repository_path,
            repository_content_sha256=sha256(repository_content.encode("utf-8")).hexdigest(),
            selected_text=selected_text,
        )

    def __post_init__(self) -> None:
        if self.repository_path not in _ALLOWED_CONTEXT_PATHS:
            raise ValueError("context source path is not authorized")
        _require_sha256(self.repository_content_sha256, "repository_content_sha256")
        _require_text(self.selected_text, "selected_text")
        selected_hash = sha256(self.selected_text.encode("utf-8")).hexdigest()
        object.__setattr__(self, "selected_text_sha256", selected_hash)
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "version": SELECTED_CONTEXT_VERSION,
                    "repository_path": self.repository_path,
                    "repository_content_sha256": self.repository_content_sha256,
                    "selected_text_sha256": selected_hash,
                    "selected_text": self.selected_text,
                }
            ),
        )
'''
new_context_class = '''@dataclass(frozen=True)
class SelectedContextDocument:
    """Exact excerpt re-verified against an allow-listed committed Git blob."""

    repository_path: str
    repository_content_sha256: str
    selected_text: str
    selected_text_sha256: str = field(init=False)
    identity: str = field(init=False)

    @classmethod
    def from_repository_authority(
        cls, repository_path: str, selected_text: str
    ) -> "SelectedContextDocument":
        if repository_path not in _ALLOWED_CONTEXT_PATHS:
            raise ValueError("context source path is not an authorized Jianghe authority")
        _require_text(selected_text, "selected_text")
        blob = _repository_blob_bytes(REPOSITORY_ROOT / repository_path)
        try:
            repository_content = blob.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("authorized Jianghe context must be UTF-8 text") from error
        if selected_text not in repository_content:
            raise ValueError("selected context must be an exact substring of committed repository content")
        return cls(
            repository_path=repository_path,
            repository_content_sha256=sha256(blob).hexdigest(),
            selected_text=selected_text,
        )

    def __post_init__(self) -> None:
        if self.repository_path not in _ALLOWED_CONTEXT_PATHS:
            raise ValueError("context source path is not authorized")
        _require_sha256(self.repository_content_sha256, "repository_content_sha256")
        _require_text(self.selected_text, "selected_text")
        blob = _repository_blob_bytes(REPOSITORY_ROOT / self.repository_path)
        actual_hash = sha256(blob).hexdigest()
        if self.repository_content_sha256 != actual_hash:
            raise ValueError("selected context repository hash does not match committed Git blob")
        try:
            repository_content = blob.decode("utf-8")
        except UnicodeDecodeError as error:
            raise ValueError("authorized Jianghe context must be UTF-8 text") from error
        if self.selected_text not in repository_content:
            raise ValueError("selected context is not present in committed repository authority")
        selected_hash = sha256(self.selected_text.encode("utf-8")).hexdigest()
        object.__setattr__(self, "selected_text_sha256", selected_hash)
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "version": SELECTED_CONTEXT_VERSION,
                    "repository_path": self.repository_path,
                    "repository_content_sha256": actual_hash,
                    "selected_text_sha256": selected_hash,
                    "selected_text": self.selected_text,
                }
            ),
        )
'''
replace_once(RUNTIME, old_context_class, new_context_class)
replace_once(
    RUNTIME,
    '        _require_sha256(self.context_selection_policy_identity, "context_selection_policy_identity")\n',
    '        _require_sha256(self.context_selection_policy_identity, "context_selection_policy_identity")\n'
    '        if self.context_selection_policy_identity != current_context_selection_policy_identity():\n'
    '            raise ValueError("selected context uses an unauthorized selection policy")\n',
)

# --- Runtime: close free-form egress channels in the spend serializer ---
replace_once(
    RUNTIME,
    '''        ident = observation.identity
        payload = {
''',
    '''        ident = observation.identity
        visible = dict(observation.visible_metadata)
        if set(visible) - set(_ALLOWED_VISIBLE_METADATA):
            raise ValueError("spend-eligible observation contains unknown visible metadata")
        for key, value in visible.items():
            if value not in _ALLOWED_VISIBLE_METADATA[key]:
                raise ValueError("spend-eligible visible metadata value is outside closed-world schema")
        for position in observation.positions:
            if position.entry_facts:
                raise ValueError("free-form position entry_facts are not spend-eligible in schema V0.1")
            for identifier in (*position.protective_orders, *position.active_order_ids):
                if not _AUDIT_IDENTIFIER.fullmatch(identifier):
                    raise ValueError("position order identifiers must satisfy the closed-world audit-id grammar")
        for identifier in observation.active_order_ids:
            if not _AUDIT_IDENTIFIER.fullmatch(identifier):
                raise ValueError("active order identifiers must satisfy the closed-world audit-id grammar")
        payload = {
''',
)
replace_once(
    RUNTIME,
    '''                    "quantity": position.quantity,
                    "entry_facts": [list(item) for item in position.entry_facts],
                    "protective_orders": list(position.protective_orders),
''',
    '''                    "quantity": position.quantity,
                    "protective_orders": list(position.protective_orders),
''',
)
replace_once(
    RUNTIME,
    '''                            "active_order_ids", "direction", "entry_facts",
                            "protective_orders", "quantity",
''',
    '''                            "active_order_ids", "direction",
                            "protective_orders", "quantity",
''',
)

# --- Runtime: current domestic endpoints ---
replace_once(RUNTIME, 'endpoint="https://api.moonshot.ai/v1/chat/completions",', 'endpoint="https://api.moonshot.cn/v1/chat/completions",')
replace_once(RUNTIME, 'endpoint="https://api.minimaxi.com/v1/text/chatcompletion_v2",', 'endpoint="https://api.minimaxi.com/v1/chat/completions",')
replace_once(
    RUNTIME,
    '        "https://platform.kimi.ai/",\n        "https://platform.kimi.ai/docs/guide/kimi-k3-quickstart",\n',
    '        "https://platform.kimi.com/",\n        "https://www.kimi.ai/help/kimi-api/api-model-selection",\n        "https://www.kimi.ai/zh-hans/help/kimi-code/cli-getting-started",\n',
)

# --- Runtime: repository-bound production pricing authority ---
replace_once(
    RUNTIME,
    '''class RateCard:
    provider_id: str
    model_id: str
    currency: str
    input_per_million: Decimal
    output_per_million: Decimal
    image_tokens_billed_as_input: bool
    authority_uri: str
    effective_at: datetime
    expires_at: datetime
    identity: str = field(init=False)
''',
    '''class RateCard:
    provider_id: str
    model_id: str
    currency: str
    input_per_million: Decimal
    output_per_million: Decimal
    image_tokens_billed_as_input: bool
    authority_uri: str
    effective_at: datetime
    expires_at: datetime
    image_billing_mode: str = "INPUT_TOKENS"
    fixed_input_tokens_per_image: int | None = None
    repository_authority_identity: str | None = None
    identity: str = field(init=False)
''',
)
replace_once(
    RUNTIME,
    '''        if type(self.image_tokens_billed_as_input) is not bool or not self.image_tokens_billed_as_input:
            raise ValueError("unknown/different image billing semantics fail closed")
        _require_text(self.authority_uri, "authority_uri")
''',
    '''        if type(self.image_tokens_billed_as_input) is not bool or not self.image_tokens_billed_as_input:
            raise ValueError("unknown/different image billing semantics fail closed")
        if self.image_billing_mode not in {"INPUT_TOKENS", "FIXED_INPUT_TOKENS_PER_IMAGE"}:
            raise ValueError("unknown image billing mode fails closed")
        if self.image_billing_mode == "FIXED_INPUT_TOKENS_PER_IMAGE":
            if (
                not isinstance(self.fixed_input_tokens_per_image, int)
                or isinstance(self.fixed_input_tokens_per_image, bool)
                or self.fixed_input_tokens_per_image <= 0
            ):
                raise ValueError("fixed image billing requires positive tokens per image")
        elif self.fixed_input_tokens_per_image is not None:
            raise ValueError("fixed image tokens are only valid for fixed image billing")
        if self.repository_authority_identity is not None:
            _require_sha256(self.repository_authority_identity, "repository_authority_identity")
        _require_text(self.authority_uri, "authority_uri")
''',
)
replace_once(
    RUNTIME,
    '''                    "output_per_million": str(output_price),
                    "image_tokens_billed_as_input": True, "authority_uri": self.authority_uri,
                    "effective_at": _utc(self.effective_at), "expires_at": _utc(self.expires_at),
''',
    '''                    "output_per_million": str(output_price),
                    "image_tokens_billed_as_input": True,
                    "image_billing_mode": self.image_billing_mode,
                    "fixed_input_tokens_per_image": self.fixed_input_tokens_per_image,
                    "repository_authority_identity": self.repository_authority_identity,
                    "authority_uri": self.authority_uri,
                    "effective_at": _utc(self.effective_at), "expires_at": _utc(self.expires_at),
''',
)
pricing_loader = '''

def load_current_repository_rate_card(spec: ProviderSpec, *, now: datetime) -> RateCard:
    """Load the only production-eligible rate card from exact committed evidence."""
    _require_aware(now, "now")
    blob = _repository_blob_bytes(PRICING_AUTHORITY_PATH)
    authority_identity = sha256(blob).hexdigest()
    try:
        payload = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise BudgetGuardError("provider pricing authority is malformed") from error
    if not isinstance(payload, Mapping):
        raise BudgetGuardError("provider pricing authority must be an object")
    if payload.get("artifact_schema_version") != "JIANGHE_PROVIDER_PRICING_AUTHORITY_SCHEMA_V0_1":
        raise BudgetGuardError("provider pricing authority schema is unknown")
    if payload.get("hard_project_cap_cny") != "100.00":
        raise BudgetGuardError("provider pricing authority does not preserve the Owner hard cap")
    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise BudgetGuardError("provider pricing authority has no entries")
    matches = [
        item for item in entries
        if isinstance(item, Mapping)
        and item.get("provider_id") == spec.provider_id
        and item.get("model_id") == spec.model_id
    ]
    if len(matches) != 1:
        raise BudgetGuardError("provider/model has no unique pricing authority")
    entry = matches[0]
    if entry.get("status") != "VERIFIED_CURRENT_FOR_SPEND_GUARD":
        raise BudgetGuardError(f"provider pricing is not spend-eligible: {entry.get('status')}")
    if entry.get("endpoint") != spec.endpoint:
        raise BudgetGuardError("pricing authority endpoint differs from provider transport")
    authorities = entry.get("authorities")
    if not isinstance(authorities, list) or not authorities or not all(
        isinstance(url, str) and url.startswith("https://") for url in authorities
    ):
        raise BudgetGuardError("pricing authority lacks first-party source URLs")
    try:
        effective_at = datetime.fromisoformat(str(entry["effective_at"]))
        expires_at = datetime.fromisoformat(str(entry["expires_at"]))
        fixed_tokens = int(entry["fixed_input_tokens_per_image"])
    except (KeyError, TypeError, ValueError) as error:
        raise BudgetGuardError("pricing authority entry is incomplete") from error
    card = RateCard(
        provider_id=spec.provider_id,
        model_id=spec.model_id,
        currency=str(entry.get("currency")),
        input_per_million=Decimal(str(entry.get("input_per_million"))),
        output_per_million=Decimal(str(entry.get("output_per_million"))),
        image_tokens_billed_as_input=True,
        authority_uri=str(authorities[0]),
        effective_at=effective_at,
        expires_at=expires_at,
        image_billing_mode=str(entry.get("image_billing_mode")),
        fixed_input_tokens_per_image=fixed_tokens,
        repository_authority_identity=authority_identity,
    )
    if not (card.effective_at <= now < card.expires_at):
        raise BudgetGuardError("repository pricing authority is stale or not yet effective")
    return card
'''
replace_once(RUNTIME, '\n\n@dataclass(frozen=True)\nclass FxAuthority:', pricing_loader + '\n\n@dataclass(frozen=True)\nclass FxAuthority:')

# K3 always thinks; pin effort explicitly so transport semantics are auditable.
replace_once(
    RUNTIME,
    '''            return {"model": self.spec.model_id,
                    "messages": [{"role": "system", "content": request.system_prompt},
                                 {"role": "user", "content": multimodal_content}],
                    "max_completion_tokens": request.max_output_tokens,
''',
    '''            return {"model": self.spec.model_id,
                    "messages": [{"role": "system", "content": request.system_prompt},
                                 {"role": "user", "content": multimodal_content}],
                    "reasoning_effort": "max",
                    "max_completion_tokens": request.max_output_tokens,
''',
)

# Production invocation may not accept a caller-authored price card.
replace_once(
    RUNTIME,
    '''    def invoke(self, request: SpendEligibleJiangheRequest, *, authorization: PaidCallAuthorization | None,
               budget: CnyBudgetLedger, rate_card: RateCard, bounds: InvocationBounds,
               fx: FxAuthority | None, now: datetime, timeout_seconds: float = 60.0) -> ProviderInvocationEvidence:
''',
    '''    def invoke(self, request: SpendEligibleJiangheRequest, *, authorization: PaidCallAuthorization | None,
               budget: CnyBudgetLedger, bounds: InvocationBounds,
               fx: FxAuthority | None, now: datetime, timeout_seconds: float = 60.0) -> ProviderInvocationEvidence:
''',
)
replace_once(
    RUNTIME,
    '''        if bounds.max_output_tokens != request.max_output_tokens:
            raise BudgetGuardError("request output cap must equal reserved output cap")
        reservation = budget.reserve(self.spec, rate_card, bounds, fx=fx, now=now)
''',
    '''        if bounds.max_output_tokens != request.max_output_tokens:
            raise BudgetGuardError("request output cap must equal reserved output cap")
        rate_card = load_current_repository_rate_card(self.spec, now=now)
        if rate_card.image_billing_mode == "FIXED_INPUT_TOKENS_PER_IMAGE":
            expected_image_tokens = len(request.visuals) * int(rate_card.fixed_input_tokens_per_image or 0)
            if bounds.max_image_tokens != expected_image_tokens:
                raise BudgetGuardError("image-token reservation must exactly match the repository billing authority")
        else:
            expected_image_tokens = bounds.max_image_tokens
        reservation = budget.reserve(self.spec, rate_card, bounds, fx=fx, now=now)
''',
)
replace_once(
    RUNTIME,
    '''        budget.reconcile(
            reservation.reservation_id, text_input_tokens=usage.text_input_tokens,
            image_tokens=usage.image_tokens, output_tokens=usage.output_tokens,
''',
    '''        conservative_image_tokens = max(usage.image_tokens, expected_image_tokens)
        budget.reconcile(
            reservation.reservation_id, text_input_tokens=usage.text_input_tokens,
            image_tokens=conservative_image_tokens, output_tokens=usage.output_tokens,
''',
)
replace_once(
    RUNTIME,
    '    "CnyBudgetLedger", "DEEPSEEK_VISION_SPEC", "DomesticProviderTransport",\n',
    '    "CnyBudgetLedger", "DEEPSEEK_VISION_SPEC", "DomesticProviderTransport",\n'
    '    "current_context_selection_policy_identity", "load_current_repository_rate_card",\n',
)

# --- Existing focused tests: use real repository authority and production price loader ---
replace_once(TEST, '    RateCard,\n    SelectedContextDocument,\n', '    RateCard,\n    SelectedContextDocument,\n    current_context_selection_policy_identity,\n    load_current_repository_rate_card,\n')
replace_once(
    TEST,
    '''def _context(selected: str = "位置优先于触发。") -> SelectedJiangheContextArtifact:
    repo_content = "# current authority\\n位置优先于触发。\\n没有触发就等待。\\n"
    doc = SelectedContextDocument.from_repository_document(
        "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md", repo_content, selected
    )
    policy = hashlib.sha256(b"context-policy-v1").hexdigest()
    return SelectedJiangheContextArtifact(policy, (doc,))


def _request(selected: str = "位置优先于触发。") -> SpendEligibleJiangheRequest:
''',
    '''def _context(selected: str = "UNKNOWN > GUESSING") -> SelectedJiangheContextArtifact:
    doc = SelectedContextDocument.from_repository_authority(
        "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md", selected
    )
    return SelectedJiangheContextArtifact(current_context_selection_policy_identity(), (doc,))


def _request(selected: str = "UNKNOWN > GUESSING") -> SpendEligibleJiangheRequest:
''',
)
replace_once(
    TEST,
    '''            SelectedContextDocument.from_repository_document("docs/other.md", "abc", "abc")
        with self.assertRaises(ValueError):
            SelectedContextDocument.from_repository_document(
                "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md", "真实内容", "不存在的片段"
            )
''',
    '''            SelectedContextDocument.from_repository_authority("docs/other.md", "abc")
        with self.assertRaises(ValueError):
            SelectedContextDocument.from_repository_authority(
                "docs/research/jianghe/JIANGHE_CURRENT_VIEW_V1_1.md", "不存在的片段"
            )
''',
)
replace_once(TEST, '        first = _request("位置优先于触发。")\n        second = _request("没有触发就等待。")\n', '        first = _request("UNKNOWN > GUESSING")\n        second = _request("SOURCE CLAIM != PROJECT/AI INTERPRETATION != MACHINE OPERATIONALIZATION")\n')
replace_once(TEST, '        self.assertIn("位置优先于触发。", first.common_model_text())\n', '        self.assertIn("UNKNOWN > GUESSING", first.common_model_text())\n')
replace_once(TEST, '                self.assertIn("位置优先于触发。", encoded)\n', '                self.assertIn("UNKNOWN > GUESSING", encoded)\n')
replace_once(
    TEST,
    '''                _request(), authorization=None, budget=CnyBudgetLedger(),
                rate_card=_rate(KIMI_K3_SPEC), bounds=InvocationBounds(1000, 500, 200),
                fx=None, now=NOW,
''',
    '''                _request(), authorization=None, budget=CnyBudgetLedger(),
                bounds=InvocationBounds(1000, 1024, 200), fx=None, now=NOW,
''',
)
replace_once(
    TEST,
    '''                _request(), authorization=auth, budget=ledger,
                rate_card=_rate(KIMI_K3_SPEC), bounds=InvocationBounds(1500, 500, 200),
                fx=None, now=NOW,
''',
    '''                _request(), authorization=auth, budget=ledger,
                bounds=InvocationBounds(1500, 1024, 200), fx=None, now=NOW,
''',
)

append = r'''

class PrespendV02AuthorityTests(unittest.TestCase):
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

    def test_current_context_is_bound_to_corrected_git_blob_manifest(self):
        context = _context()
        self.assertEqual(
            context.primary_manifest_identity,
            "f767253dc4c2d1b17f57b9adfdc903907a97df8d4697dbe0fae0f603427dbf36",
        )

    def test_spend_structured_schema_rejects_unknown_visible_metadata(self):
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

    def test_repository_pricing_is_non_forgeable_and_kimi_image_billing_is_fixed(self):
        card = load_current_repository_rate_card(KIMI_K3_SPEC, now=NOW)
        self.assertEqual(card.currency, "CNY")
        self.assertEqual(card.input_per_million, Decimal("20.00"))
        self.assertEqual(card.output_per_million, Decimal("100.00"))
        self.assertEqual(card.image_billing_mode, "FIXED_INPUT_TOKENS_PER_IMAGE")
        self.assertEqual(card.fixed_input_tokens_per_image, 1024)
        self.assertIsNotNone(card.repository_authority_identity)

    def test_unresolved_provider_image_billing_fails_before_network(self):
        for spec in (DEEPSEEK_VISION_SPEC, MINIMAX_M3_SPEC):
            with self.subTest(provider=spec.provider_id):
                with self.assertRaises(BudgetGuardError):
                    load_current_repository_rate_card(spec, now=NOW)

    def test_kimi_transport_uses_mainland_open_platform_endpoint_and_explicit_effort(self):
        self.assertEqual(KIMI_K3_SPEC.endpoint, "https://api.moonshot.cn/v1/chat/completions")
        payload = DomesticProviderTransport(KIMI_K3_SPEC).build_payload(_request())
        self.assertEqual(payload["reasoning_effort"], "max")

    def test_minimax_transport_uses_current_openai_compatible_endpoint(self):
        self.assertEqual(MINIMAX_M3_SPEC.endpoint, "https://api.minimaxi.com/v1/chat/completions")
'''
text = TEST.read_text(encoding="utf-8")
marker = '\n\nif __name__ == "__main__":\n    unittest.main()\n'
if marker not in text:
    raise SystemExit("test file main marker missing")
TEST.write_text(text.replace(marker, append + marker), encoding="utf-8", newline="\n")

print("PRESPEND_V02_APPLICATOR=PASS")

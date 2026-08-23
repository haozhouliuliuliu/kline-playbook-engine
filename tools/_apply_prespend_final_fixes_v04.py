from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / "src" / "jianghe_prespend_runtime.py"
REPAIR_TEST = ROOT / "tests" / "test_jianghe_prespend_repair.py"
PROVIDER_TEST = ROOT / "tests" / "test_jianghe_model_provider.py"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one replacement, found {count}: {old[:100]!r}")
    path.write_text(text.replace(old, new), encoding="utf-8", newline="\n")


def replace_between(path: Path, start: str, end: str, replacement: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(start) != 1 or text.count(end) < 1:
        raise SystemExit(f"{path}: replacement markers not unique/present: {start!r} -> {end!r}")
    left = text.index(start)
    right = text.index(end, left)
    path.write_text(text[:left] + replacement + text[right:], encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------
# BSP-001 / BSP-004 authority constants and selection-policy identity.
# ---------------------------------------------------------------------------
replace_once(
    RUNTIME,
    '''PRICING_AUTHORITY_PATH = (
    REPOSITORY_ROOT / "docs" / "evidence" / "JIANGHE_PROVIDER_PRICING_AUTHORITY_V0_1.json"
)
''',
    '''PRICING_AUTHORITY_PATH = (
    REPOSITORY_ROOT / "docs" / "evidence" / "JIANGHE_PROVIDER_PRICING_AUTHORITY_V0_1.json"
)
FIDELITY_CORPUS_PATH = (
    REPOSITORY_ROOT / "docs" / "evidence" / "JIANGHE_AI_FIDELITY_FIXTURES_V0_1.json"
)
PRIMARY_REGISTRY_RELATIVE_PATH = (
    "docs/research/jianghe/primary_mapping_draft_v0_1/"
    "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_5.jsonl"
)
PRIMARY_REGISTRY_PATH = REPOSITORY_ROOT / PRIMARY_REGISTRY_RELATIVE_PATH
PAID_CALL_AUTHORITY_PATH = (
    REPOSITORY_ROOT / "docs" / "evidence" / "JIANGHE_PAID_CALL_AUTHORIZATION_CURRENT.json"
)
EXPECTED_FIDELITY_CORPUS_ID = "JIANGHE_AI_FIDELITY_FIXTURE_CORPUS_V0_1"
TEXT_INPUT_BOUND_POLICY_VERSION = "UTF8_PAYLOAD_BYTES_X2_PLUS_8192_V0_1"
''',
)
replace_once(
    RUNTIME,
    '            "selection_semantics": "EXACT_UTF8_SUBSTRING_ONLY",\n',
    '            "selection_semantics": "FIXTURE_SOURCE_ANCHORS_TO_PRIMARY_V0_5_EXACT_JSONL_RECORDS",\n',
)

context_block = r'''def _fixture_context_material(fixture_id: str) -> dict[str, object]:
    """Resolve only fixture source-claim anchors into exact committed PRIMARY records.

    The fixture is used only as a selector. No visible_information, expected answer,
    rubric, hidden-future section, case outcome, or fixture prose is transmitted.
    """
    _require_text(fixture_id, "fixture_id")
    corpus_blob = _repository_blob_bytes(FIDELITY_CORPUS_PATH)
    try:
        corpus = json.loads(corpus_blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ValueError("fidelity corpus authority is malformed") from error
    if not isinstance(corpus, Mapping) or corpus.get("corpus_id") != EXPECTED_FIDELITY_CORPUS_ID:
        raise ValueError("unexpected fidelity corpus authority")
    if corpus.get("knowledge_pack_identity") != CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY:
        raise ValueError("fidelity corpus is not bound to the current Jianghe knowledge pack")
    fixtures = corpus.get("fixtures")
    if not isinstance(fixtures, list):
        raise ValueError("fidelity corpus fixtures are malformed")
    matches = [
        item for item in fixtures
        if isinstance(item, Mapping) and item.get("fixture_id") == fixture_id
    ]
    if len(matches) != 1:
        raise ValueError("fixture_id must resolve to exactly one governed fixture")
    fixture = matches[0]
    anchors = fixture.get("source_anchors")
    if not isinstance(anchors, Mapping):
        raise ValueError("fixture source anchors are missing")
    raw_claim_ids = anchors.get("claims")
    if (
        not isinstance(raw_claim_ids, list)
        or not raw_claim_ids
        or any(not isinstance(value, str) or not value for value in raw_claim_ids)
    ):
        raise ValueError("fixture must declare non-empty source claim anchors")
    claim_ids = tuple(sorted(set(raw_claim_ids)))
    if len(claim_ids) != len(raw_claim_ids):
        raise ValueError("fixture source claim anchors must be unique")

    registry_blob = _repository_blob_bytes(PRIMARY_REGISTRY_PATH)
    try:
        registry_text = registry_blob.decode("utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("PRIMARY registry must be UTF-8") from error
    selected_lines: dict[str, str] = {}
    for line in registry_text.splitlines():
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError("PRIMARY registry JSONL is malformed") from error
        if not isinstance(record, Mapping):
            raise ValueError("PRIMARY registry record must be an object")
        claim_id = record.get("claim_id")
        if claim_id not in claim_ids:
            continue
        if claim_id in selected_lines:
            raise ValueError("PRIMARY registry contains duplicate selected claim_id")
        if record.get("claim_manifest_identity") != CURRENT_PRIMARY_MANIFEST_IDENTITY:
            raise ValueError("selected PRIMARY record has stale claim-manifest identity")
        if record.get("knowledge_pack_identity") != CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY:
            raise ValueError("selected PRIMARY record has stale knowledge-pack identity")
        if record.get("branch_registry_version") != "JIANGHE_PRIMARY_CLAIM_LEVEL_BRANCH_REGISTRY_V0_5":
            raise ValueError("selected PRIMARY record has unexpected registry version")
        selected_lines[str(claim_id)] = line
    missing = tuple(sorted(set(claim_ids) - set(selected_lines)))
    if missing:
        raise ValueError(f"fixture source claims missing from current PRIMARY registry: {missing}")

    documents = tuple(
        SelectedContextDocument.from_repository_authority(
            PRIMARY_REGISTRY_RELATIVE_PATH, selected_lines[claim_id]
        )
        for claim_id in claim_ids
    )
    fixture_identity = _hash(fixture)
    corpus_content_sha256 = sha256(corpus_blob).hexdigest()
    registry_content_sha256 = sha256(registry_blob).hexdigest()
    selection_basis_identity = _hash(
        {
            "policy_identity": current_context_selection_policy_identity(),
            "corpus_id": EXPECTED_FIDELITY_CORPUS_ID,
            "corpus_content_sha256": corpus_content_sha256,
            "fixture_id": fixture_id,
            "fixture_identity": fixture_identity,
            "primary_registry_content_sha256": registry_content_sha256,
            "source_claim_ids": claim_ids,
            "selected_document_identities": tuple(item.identity for item in documents),
        }
    )
    return {
        "documents": documents,
        "fixture_identity": fixture_identity,
        "corpus_content_sha256": corpus_content_sha256,
        "registry_content_sha256": registry_content_sha256,
        "source_claim_ids": claim_ids,
        "selection_basis_identity": selection_basis_identity,
    }


@dataclass(frozen=True)
class SelectedJiangheContextArtifact:
    """Exact governed Jianghe material sent to a spend-eligible model request."""

    context_selection_policy_identity: str
    documents: tuple[SelectedContextDocument, ...]
    knowledge_pack_identity: str = CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY
    primary_manifest_identity: str = CURRENT_PRIMARY_MANIFEST_IDENTITY
    primary_registry_version: str = "JIANGHE_PRIMARY_BRANCH_REGISTRY_V0_5"
    fixture_id: str | None = None
    fixture_identity: str | None = field(init=False, default=None)
    fixture_corpus_content_sha256: str | None = field(init=False, default=None)
    primary_registry_content_sha256: str | None = field(init=False, default=None)
    source_claim_ids: tuple[str, ...] = field(init=False, default=())
    selection_basis_identity: str | None = field(init=False, default=None)
    identity: str = field(init=False)

    @classmethod
    def from_fixture_id(cls, fixture_id: str) -> "SelectedJiangheContextArtifact":
        material = _fixture_context_material(fixture_id)
        return cls(
            current_context_selection_policy_identity(),
            material["documents"],
            fixture_id=fixture_id,
        )

    def __post_init__(self) -> None:
        _require_sha256(self.context_selection_policy_identity, "context_selection_policy_identity")
        if self.context_selection_policy_identity != current_context_selection_policy_identity():
            raise ValueError("selected context uses an unauthorized selection policy")
        if self.knowledge_pack_identity != CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY:
            raise ValueError("selected context is not bound to the current knowledge pack")
        if self.primary_manifest_identity != CURRENT_PRIMARY_MANIFEST_IDENTITY:
            raise ValueError("selected context is not bound to the current PRIMARY manifest")
        if self.primary_registry_version != "JIANGHE_PRIMARY_BRANCH_REGISTRY_V0_5":
            raise ValueError("selected context is not bound to PRIMARY registry V0.5")
        if not self.documents:
            raise ValueError("selected Jianghe context must contain actual material")
        ordered = tuple(sorted(self.documents, key=lambda item: (item.repository_path, item.identity)))
        if len({item.identity for item in ordered}) != len(ordered):
            raise ValueError("selected Jianghe context documents must be unique")
        object.__setattr__(self, "documents", ordered)

        if self.fixture_id is not None:
            material = _fixture_context_material(self.fixture_id)
            expected = tuple(
                sorted(material["documents"], key=lambda item: (item.repository_path, item.identity))
            )
            if tuple(item.identity for item in ordered) != tuple(item.identity for item in expected):
                raise ValueError("selected context differs from deterministic fixture source selection")
            object.__setattr__(self, "fixture_identity", material["fixture_identity"])
            object.__setattr__(self, "fixture_corpus_content_sha256", material["corpus_content_sha256"])
            object.__setattr__(self, "primary_registry_content_sha256", material["registry_content_sha256"])
            object.__setattr__(self, "source_claim_ids", material["source_claim_ids"])
            object.__setattr__(self, "selection_basis_identity", material["selection_basis_identity"])
        object.__setattr__(self, "identity", _hash(self.to_payload(include_identity=False)))

    def to_payload(self, *, include_identity: bool = True) -> dict[str, object]:
        payload: dict[str, object] = {
            "version": SELECTED_CONTEXT_VERSION,
            "knowledge_pack_identity": self.knowledge_pack_identity,
            "primary_manifest_identity": self.primary_manifest_identity,
            "primary_registry_version": self.primary_registry_version,
            "context_selection_policy_identity": self.context_selection_policy_identity,
            "fixture_id": self.fixture_id,
            "fixture_identity": self.fixture_identity,
            "fixture_corpus_content_sha256": self.fixture_corpus_content_sha256,
            "primary_registry_content_sha256": self.primary_registry_content_sha256,
            "source_claim_ids": list(self.source_claim_ids),
            "selection_basis_identity": self.selection_basis_identity,
            "documents": [item.to_payload() for item in self.documents],
        }
        if include_identity:
            payload["selected_context_identity"] = self.identity
        return payload


'''
replace_between(
    RUNTIME,
    '@dataclass(frozen=True)\nclass SelectedJiangheContextArtifact:',
    '@dataclass(frozen=True)\nclass CanonicalStructuredObservationArtifact:',
    context_block,
)

structured_block = r'''@dataclass(frozen=True, init=False)
class CanonicalStructuredObservationArtifact:
    """Closed-world artifact that can only be constructed from JiangheObservation."""

    source_observation_identity: str
    serialized_json: str
    schema_identity: str
    identity: str

    @classmethod
    def from_observation(
        cls, observation: JiangheObservation
    ) -> "CanonicalStructuredObservationArtifact":
        if not isinstance(observation, JiangheObservation):
            raise TypeError("structured artifact must be generated from JiangheObservation")
        if observation.schema_version != "JIANGHE_OBSERVATION_V0_1":
            raise ValueError("spend-eligible observation schema version is not canonical V0.1")
        ident = observation.identity
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
            "artifact_schema_version": STRUCTURED_SCHEMA_VERSION,
            "source_observation_schema_version": observation.schema_version,
            "observation_identity": ident.identity,
            "observation": {
                "decision_time": _utc(ident.decision_time),
                "exchange_time": _utc(ident.exchange_time),
                "product": ident.product,
                "concrete_contract": ident.concrete_contract,
                "mapping_identity": ident.mapping_identity,
                "session_identity": ident.session_identity,
                "content_identity": ident.content_identity,
            },
            "bars": [
                {
                    "timeframe": bar.timeframe,
                    "open_time": _utc(bar.open_time),
                    "close_time": _utc(bar.close_time),
                    "available_at": _utc(bar.available_at),
                    "open_price": bar.open_price,
                    "high_price": bar.high_price,
                    "low_price": bar.low_price,
                    "close_price": bar.close_price,
                    "volume": bar.volume,
                    "is_closed": bar.is_closed,
                }
                for bar in observation.bars
            ],
            "positions": [
                {
                    "direction": position.direction.value,
                    "quantity": position.quantity,
                    "protective_orders": list(position.protective_orders),
                    "active_order_ids": list(position.active_order_ids),
                }
                for position in observation.positions
            ],
            "active_order_ids": list(observation.active_order_ids),
            "visible_metadata": [list(item) for item in observation.visible_metadata],
        }
        _scan_forbidden(payload)
        serialized = _canonical_json(payload)
        schema_identity = _hash(
            {
                "schema_version": STRUCTURED_SCHEMA_VERSION,
                "source_observation_schema_version": "JIANGHE_OBSERVATION_V0_1",
                "closed_world_fields": {
                    "top": tuple(sorted(payload)),
                    "observation": tuple(sorted(payload["observation"])),
                    "bar": tuple(sorted(payload["bars"][0])) if payload["bars"] else (),
                    "position": (
                        tuple(sorted(payload["positions"][0])) if payload["positions"] else (
                            "active_order_ids", "direction", "protective_orders", "quantity"
                        )
                    ),
                },
            }
        )
        artifact = object.__new__(cls)
        object.__setattr__(artifact, "source_observation_identity", ident.identity)
        object.__setattr__(artifact, "serialized_json", serialized)
        object.__setattr__(artifact, "schema_identity", schema_identity)
        object.__setattr__(
            artifact,
            "identity",
            _hash(
                {
                    "schema_identity": schema_identity,
                    "source_observation_identity": ident.identity,
                    "serialized_json_sha256": sha256(serialized.encode("utf-8")).hexdigest(),
                }
            ),
        )
        return artifact

    def payload(self) -> dict[str, object]:
        return json.loads(self.serialized_json)


'''
replace_between(
    RUNTIME,
    '@dataclass(frozen=True)\nclass CanonicalStructuredObservationArtifact:',
    '@dataclass(frozen=True)\nclass VisualInputArtifact:',
    structured_block,
)
replace_once(
    RUNTIME,
    '''        if not isinstance(self.context, SelectedJiangheContextArtifact):
            raise TypeError("context must be SelectedJiangheContextArtifact")
        if not isinstance(self.structured_observation, CanonicalStructuredObservationArtifact):
''',
    '''        if not isinstance(self.context, SelectedJiangheContextArtifact):
            raise TypeError("context must be SelectedJiangheContextArtifact")
        if self.context.fixture_id is None or self.context.selection_basis_identity is None:
            raise ValueError("spend-eligible context must come from deterministic fixture source anchors")
        if not isinstance(self.structured_observation, CanonicalStructuredObservationArtifact):
''',
)

# ---------------------------------------------------------------------------
# BSP-005: reservation cancellation is only permitted before a network attempt.
# ---------------------------------------------------------------------------
replace_once(
    RUNTIME,
    '''    def consume_full_reservation_on_unknown_usage(self, reservation_id: str) -> None:
''',
    '''    def cancel_before_network(self, reservation_id: str, *, reason: str) -> None:
        reservation = self._outstanding
        if reservation is None or reservation.reservation_id != reservation_id:
            raise BudgetGuardError("reservation is missing or mismatched")
        _require_text(reason, "reason")
        self._outstanding = None
        self._history.append((f"CANCELLED_BEFORE_NETWORK:{reason}", reservation_id))

    def consume_full_reservation_on_unknown_usage(self, reservation_id: str) -> None:
''',
)

# ---------------------------------------------------------------------------
# BSP-004: repository-bound Owner authorization, not a caller-fabricated bool/SHA.
# ---------------------------------------------------------------------------
authorization_block = r'''@dataclass(frozen=True)
class PaidCallAuthorization:
    authorization_id: str
    authorization_evidence_sha256: str
    provider_models: tuple[tuple[str, str], ...]
    hard_cap_cny: Decimal
    paid_calls_enabled: bool = False
    repository_authority_identity: str | None = None
    effective_at: datetime | None = None
    expires_at: datetime | None = None
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.authorization_id, "authorization_id")
        _require_sha256(self.authorization_evidence_sha256, "authorization_evidence_sha256")
        if type(self.paid_calls_enabled) is not bool:
            raise ValueError("paid_calls_enabled must be strict bool")
        cap = _decimal(self.hard_cap_cny, "hard_cap_cny", positive=True)
        if cap > HARD_PROJECT_CAP_CNY:
            raise ValueError("authorization may not exceed the project hard cap")
        ordered = tuple(sorted(self.provider_models))
        if not ordered or len(set(ordered)) != len(ordered):
            raise ValueError("authorization provider_models must be unique and non-empty")
        for provider_id, model_id in ordered:
            _require_text(provider_id, "provider_id")
            _require_text(model_id, "model_id")
        if self.repository_authority_identity is not None:
            _require_sha256(self.repository_authority_identity, "repository_authority_identity")
            if self.effective_at is None or self.expires_at is None:
                raise ValueError("repository authorization requires bounded validity")
            _require_aware(self.effective_at, "effective_at")
            _require_aware(self.expires_at, "expires_at")
            if self.expires_at <= self.effective_at:
                raise ValueError("authorization validity window is invalid")
        object.__setattr__(self, "provider_models", ordered)
        object.__setattr__(self, "hard_cap_cny", cap)
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "authorization_id": self.authorization_id,
                    "authorization_evidence_sha256": self.authorization_evidence_sha256,
                    "provider_models": ordered,
                    "hard_cap_cny": str(cap),
                    "paid_calls_enabled": self.paid_calls_enabled,
                    "repository_authority_identity": self.repository_authority_identity,
                    "effective_at": None if self.effective_at is None else _utc(self.effective_at),
                    "expires_at": None if self.expires_at is None else _utc(self.expires_at),
                }
            ),
        )

    def permits(self, spec: ProviderSpec) -> bool:
        return self.paid_calls_enabled and (spec.provider_id, spec.model_id) in self.provider_models


def load_owner_paid_call_authorization(*, now: datetime) -> PaidCallAuthorization:
    """Load the only production authorization from an exact committed Git blob.

    The authority file is intentionally absent while PAID_MODEL_SPEND=NOT_AUTHORIZED.
    A caller-created PaidCallAuthorization can never substitute for this loader.
    """
    _require_aware(now, "now")
    try:
        blob = _repository_blob_bytes(PAID_CALL_AUTHORITY_PATH)
    except ValueError as error:
        raise PaidCallNotAuthorizedError("repository Owner paid-call authorization is absent") from error
    authority_identity = sha256(blob).hexdigest()
    try:
        payload = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PaidCallNotAuthorizedError("Owner paid-call authorization is malformed") from error
    required = {
        "artifact_schema_version", "authorization_id", "owner_decision_evidence_sha256",
        "paid_calls_enabled", "hard_cap_cny", "provider_models", "effective_at", "expires_at",
    }
    if not isinstance(payload, Mapping) or set(payload) != required:
        raise PaidCallNotAuthorizedError("Owner paid-call authorization schema is not closed-world")
    if payload.get("artifact_schema_version") != "JIANGHE_PAID_CALL_AUTHORIZATION_SCHEMA_V0_1":
        raise PaidCallNotAuthorizedError("Owner paid-call authorization schema version is unknown")
    if payload.get("paid_calls_enabled") is not True or payload.get("hard_cap_cny") != "100.00":
        raise PaidCallNotAuthorizedError("Owner paid-call authorization is disabled or cap differs")
    raw_models = payload.get("provider_models")
    if not isinstance(raw_models, list) or not raw_models:
        raise PaidCallNotAuthorizedError("Owner paid-call authorization has no provider models")
    provider_models: list[tuple[str, str]] = []
    for item in raw_models:
        if not isinstance(item, Mapping) or set(item) != {"provider_id", "model_id"}:
            raise PaidCallNotAuthorizedError("Owner provider authorization entry is malformed")
        provider_models.append(
            (_require_text(item.get("provider_id"), "provider_id"), _require_text(item.get("model_id"), "model_id"))
        )
    try:
        effective_at = datetime.fromisoformat(str(payload["effective_at"]))
        expires_at = datetime.fromisoformat(str(payload["expires_at"]))
    except (KeyError, ValueError) as error:
        raise PaidCallNotAuthorizedError("Owner authorization validity is malformed") from error
    auth = PaidCallAuthorization(
        authorization_id=_require_text(payload.get("authorization_id"), "authorization_id"),
        authorization_evidence_sha256=_require_sha256(
            payload.get("owner_decision_evidence_sha256"), "owner_decision_evidence_sha256"
        ),
        provider_models=tuple(provider_models),
        hard_cap_cny=Decimal("100.00"),
        paid_calls_enabled=True,
        repository_authority_identity=authority_identity,
        effective_at=effective_at,
        expires_at=expires_at,
    )
    if not (effective_at <= now < expires_at):
        raise PaidCallNotAuthorizedError("Owner paid-call authorization is stale or not yet effective")
    return auth


'''
replace_between(
    RUNTIME,
    '@dataclass(frozen=True)\nclass PaidCallAuthorization:',
    '@dataclass(frozen=True)\nclass HttpResponse:',
    authorization_block,
)

# ---------------------------------------------------------------------------
# BSP-001/BSP-004 evidence must preserve exact request material identities + raw body.
# ---------------------------------------------------------------------------
evidence_block = r'''@dataclass(frozen=True)
class ProviderInvocationEvidence:
    request_identity: str
    source_observation_identity: str
    selected_context_identity: str
    context_selection_policy_identity: str
    knowledge_pack_identity: str
    primary_manifest_identity: str
    structured_observation_identity: str
    visual_identities: tuple[str, ...]
    provider_spec_identity: str
    requested_model_id: str
    resolved_model_id: str
    provider_request_id: str
    raw_provider_response_body: str
    raw_response_text: str
    usage: ProviderUsage
    latency_ms: int
    rate_card_identity: str
    fx_identity: str | None
    budget_reservation_id: str
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        for name in (
            "request_identity", "source_observation_identity", "selected_context_identity",
            "context_selection_policy_identity", "knowledge_pack_identity", "primary_manifest_identity",
            "structured_observation_identity", "provider_spec_identity", "requested_model_id",
            "resolved_model_id", "provider_request_id", "raw_provider_response_body",
            "raw_response_text", "rate_card_identity", "budget_reservation_id",
        ):
            _require_text(getattr(self, name), name)
        for name in (
            "request_identity", "source_observation_identity", "selected_context_identity",
            "context_selection_policy_identity", "knowledge_pack_identity", "primary_manifest_identity",
            "structured_observation_identity", "provider_spec_identity", "rate_card_identity",
        ):
            _require_sha256(getattr(self, name), name)
        if not self.visual_identities or any(not _SHA256.fullmatch(value) for value in self.visual_identities):
            raise ValueError("visual identities must be non-empty sha256 values")
        if not isinstance(self.latency_ms, int) or self.latency_ms < 0:
            raise ValueError("latency_ms must be non-negative integer")
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "request_identity": self.request_identity,
                    "source_observation_identity": self.source_observation_identity,
                    "selected_context_identity": self.selected_context_identity,
                    "context_selection_policy_identity": self.context_selection_policy_identity,
                    "knowledge_pack_identity": self.knowledge_pack_identity,
                    "primary_manifest_identity": self.primary_manifest_identity,
                    "structured_observation_identity": self.structured_observation_identity,
                    "visual_identities": self.visual_identities,
                    "provider_spec_identity": self.provider_spec_identity,
                    "requested_model_id": self.requested_model_id,
                    "resolved_model_id": self.resolved_model_id,
                    "provider_request_id": self.provider_request_id,
                    "raw_provider_response_sha256": sha256(
                        self.raw_provider_response_body.encode("utf-8")
                    ).hexdigest(),
                    "raw_response_text_sha256": sha256(self.raw_response_text.encode("utf-8")).hexdigest(),
                    "usage": {
                        "text_input_tokens": self.usage.text_input_tokens,
                        "image_tokens": self.usage.image_tokens,
                        "output_tokens": self.usage.output_tokens,
                    },
                    "latency_ms": self.latency_ms,
                    "rate_card_identity": self.rate_card_identity,
                    "fx_identity": self.fx_identity,
                    "budget_reservation_id": self.budget_reservation_id,
                }
            ),
        )


'''
replace_between(
    RUNTIME,
    '@dataclass(frozen=True)\nclass ProviderInvocationEvidence:',
    'class DomesticProviderTransport:',
    evidence_block,
)

transport_block = r'''class DomesticProviderTransport:
    """Selected-provider transport. No retry, no tools, fail-closed by default."""

    def __init__(self, spec: ProviderSpec, *, http_post: HttpPost | None = None) -> None:
        if spec not in IMPLEMENTATION_TARGET_SPECS:
            raise ValueError("provider is outside the current implementation target set")
        self.spec = spec
        self._http_post = http_post or _default_http_post

    def build_payload(self, request: SpendEligibleJiangheRequest) -> dict[str, object]:
        text = request.common_model_text()
        multimodal_content: list[dict[str, object]] = [{"type": "text", "text": text}]
        multimodal_content.extend(
            {"type": "image_url", "image_url": {"url": visual.data_url()}}
            for visual in request.visuals
        )
        if self.spec.payload_style == "KIMI_OPENAI":
            return {
                "model": self.spec.model_id,
                "messages": [
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": multimodal_content},
                ],
                "reasoning_effort": "max",
                "max_completion_tokens": request.max_output_tokens,
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "jianghe_runtime_response",
                        "strict": True,
                        "schema": dict(request.response_schema),
                    },
                },
                "tools": [],
            }
        if self.spec.payload_style == "DEEPSEEK_OPENAI":
            return {
                "model": self.spec.model_id,
                "messages": [
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": multimodal_content},
                ],
                "max_tokens": request.max_output_tokens,
                "response_format": {"type": "json_object"},
                "tools": [],
            }
        if self.spec.payload_style == "MINIMAX_V2":
            return {
                "model": self.spec.model_id,
                "messages": [
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": multimodal_content},
                ],
                "max_tokens": request.max_output_tokens,
                "stream": False,
                "tools": [],
            }
        raise AssertionError("unreachable payload style")

    def payload_bytes(self, request: SpendEligibleJiangheRequest) -> bytes:
        return _canonical_json(self.build_payload(request)).encode("utf-8")

    def conservative_text_input_token_bound(self, request: SpendEligibleJiangheRequest) -> int:
        # Conservative provider-agnostic guard: two token slots per exact UTF-8 payload
        # byte plus fixed protocol overhead. Provider-reported usage above this still
        # trips the post-call full-reservation guard.
        return len(self.payload_bytes(request)) * 2 + 8192

    @staticmethod
    def _extract_text(payload: Mapping[str, object]) -> str:
        choices = payload.get("choices")
        if not isinstance(choices, list) or not choices:
            raise ProviderResponseError("provider response has no choices")
        first = choices[0]
        if not isinstance(first, Mapping):
            raise ProviderResponseError("provider choice is malformed")
        message = first.get("message")
        if not isinstance(message, Mapping):
            raise ProviderResponseError("provider choice has no message")
        content = message.get("content")
        if not isinstance(content, str) or not content:
            raise ProviderResponseError("provider response content is not text")
        return content

    @staticmethod
    def _extract_usage(payload: Mapping[str, object]) -> ProviderUsage:
        usage = payload.get("usage")
        if not isinstance(usage, Mapping):
            raise ProviderResponseError("provider response has no auditable usage")
        prompt, completion = usage.get("prompt_tokens"), usage.get("completion_tokens")
        if not isinstance(prompt, int) or isinstance(prompt, bool) or prompt < 0:
            raise ProviderResponseError("prompt token usage is unavailable")
        if not isinstance(completion, int) or isinstance(completion, bool) or completion < 0:
            raise ProviderResponseError("completion token usage is unavailable")
        image = usage.get("image_tokens", 0)
        if not isinstance(image, int) or isinstance(image, bool) or image < 0:
            raise ProviderResponseError("image token usage is malformed")
        return ProviderUsage(prompt, image, completion)

    def invoke(
        self,
        request: SpendEligibleJiangheRequest,
        *,
        authorization: PaidCallAuthorization | None,
        budget: CnyBudgetLedger,
        bounds: InvocationBounds,
        fx: FxAuthority | None,
        now: datetime,
        timeout_seconds: float = 60.0,
    ) -> ProviderInvocationEvidence:
        if authorization is None:
            raise PaidCallNotAuthorizedError("paid provider call lacks explicit Owner authorization")
        repository_authorization = load_owner_paid_call_authorization(now=now)
        if authorization.identity != repository_authorization.identity:
            raise PaidCallNotAuthorizedError("caller authorization differs from committed Owner authority")
        if not authorization.permits(self.spec):
            raise PaidCallNotAuthorizedError("provider/model is outside committed Owner authorization")
        if authorization.hard_cap_cny != budget.cap_cny:
            raise PaidCallNotAuthorizedError("authorization cap and shared ledger cap differ")
        if bounds.max_output_tokens != request.max_output_tokens:
            raise BudgetGuardError("request output cap must equal reserved output cap")

        rate_card = load_current_repository_rate_card(self.spec, now=now)
        if rate_card.currency != "CNY":
            raise BudgetGuardError("non-CNY production calls require a repository-bound FX authority")
        if fx is not None:
            raise BudgetGuardError("caller-supplied FX authority is not spend-eligible")

        payload_bytes = self.payload_bytes(request)
        required_text_bound = len(payload_bytes) * 2 + 8192
        if bounds.max_text_input_tokens != required_text_bound:
            raise BudgetGuardError(
                "text-input reservation must exactly match the canonical payload bound policy"
            )
        if rate_card.image_billing_mode != "FIXED_INPUT_TOKENS_PER_IMAGE":
            raise BudgetGuardError("dynamic/ambiguous image billing has no deterministic pre-call bound")
        expected_image_tokens = len(request.visuals) * int(rate_card.fixed_input_tokens_per_image or 0)
        if bounds.max_image_tokens != expected_image_tokens:
            raise BudgetGuardError(
                "image-token reservation must exactly match the repository billing authority"
            )

        reservation = budget.reserve(self.spec, rate_card, bounds, fx=None, now=now)
        api_key = os.environ.get(self.spec.api_key_env)
        if not api_key:
            budget.cancel_before_network(reservation.reservation_id, reason="MISSING_CREDENTIAL")
            raise ProviderTransportError("provider credential is unavailable")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        started = time.monotonic()
        try:
            response = self._http_post(self.spec.endpoint, headers, payload_bytes, float(timeout_seconds))
        except Exception:
            budget.consume_full_reservation_on_unknown_usage(reservation.reservation_id)
            raise
        latency_ms = max(0, int((time.monotonic() - started) * 1000))
        if response.status_code < 200 or response.status_code >= 300:
            budget.consume_full_reservation_on_unknown_usage(reservation.reservation_id)
            raise ProviderTransportError(f"provider returned HTTP {response.status_code}")
        try:
            raw_provider_response_body = response.body.decode("utf-8")
            decoded = json.loads(raw_provider_response_body)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            budget.consume_full_reservation_on_unknown_usage(reservation.reservation_id)
            raise ProviderResponseError("provider returned malformed JSON") from error
        if not isinstance(decoded, Mapping):
            budget.consume_full_reservation_on_unknown_usage(reservation.reservation_id)
            raise ProviderResponseError("provider response top level must be an object")
        try:
            raw_text, usage = self._extract_text(decoded), self._extract_usage(decoded)
            resolved_model, provider_request_id = decoded.get("model"), decoded.get("id")
            if not isinstance(resolved_model, str) or not resolved_model:
                raise ProviderResponseError("provider-resolved model identity is missing")
            if not isinstance(provider_request_id, str) or not provider_request_id:
                raise ProviderResponseError("provider request id is missing")
        except ProviderResponseError:
            budget.consume_full_reservation_on_unknown_usage(reservation.reservation_id)
            raise
        conservative_image_tokens = max(usage.image_tokens, expected_image_tokens)
        budget.reconcile(
            reservation.reservation_id,
            text_input_tokens=usage.text_input_tokens,
            image_tokens=conservative_image_tokens,
            output_tokens=usage.output_tokens,
            rate_card=rate_card,
            fx=None,
            now=now,
        )
        return ProviderInvocationEvidence(
            request_identity=request.identity,
            source_observation_identity=request.structured_observation.source_observation_identity,
            selected_context_identity=request.context.identity,
            context_selection_policy_identity=request.context.context_selection_policy_identity,
            knowledge_pack_identity=request.context.knowledge_pack_identity,
            primary_manifest_identity=request.context.primary_manifest_identity,
            structured_observation_identity=request.structured_observation.identity,
            visual_identities=tuple(item.identity for item in request.visuals),
            provider_spec_identity=self.spec.identity,
            requested_model_id=self.spec.model_id,
            resolved_model_id=resolved_model,
            provider_request_id=provider_request_id,
            raw_provider_response_body=raw_provider_response_body,
            raw_response_text=raw_text,
            usage=usage,
            latency_ms=latency_ms,
            rate_card_identity=rate_card.identity,
            fx_identity=None,
            budget_reservation_id=reservation.reservation_id,
        )


'''
replace_between(RUNTIME, 'class DomesticProviderTransport:', '__all__ = [', transport_block)
replace_between(
    RUNTIME,
    '__all__ = [',
    ']\n',
    '''__all__ = [
    "BUDGET_LEDGER_VERSION", "BudgetGuardError", "CanonicalStructuredObservationArtifact",
    "CnyBudgetLedger", "CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY", "CURRENT_PRIMARY_MANIFEST_IDENTITY",
    "DEEPSEEK_VISION_SPEC", "DomesticProviderTransport", "FxAuthority", "HARD_PROJECT_CAP_CNY",
    "current_context_selection_policy_identity", "load_current_repository_rate_card",
    "load_owner_paid_call_authorization", "HttpResponse", "IMPLEMENTATION_TARGET_SPECS",
    "InvocationBounds", "KIMI_K3_SPEC", "MINIMAX_M3_SPEC", "PaidCallAuthorization",
    "PaidCallNotAuthorizedError", "ProviderInvocationEvidence", "ProviderResponseError",
    "ProviderSpec", "ProviderTransportError", "ProviderUsage", "RateCard",
    "SelectedContextDocument", "SelectedJiangheContextArtifact", "SpendEligibleJiangheRequest",
    "TEXT_INPUT_BOUND_POLICY_VERSION", "VisualInputArtifact",
]\n''',
)

# ---------------------------------------------------------------------------
# Replace focused prespend tests with frozen-finding adversarial coverage.
# ---------------------------------------------------------------------------
REPAIR_TEST.write_text(r'''"""Focused adversarial tests for frozen BSP-001..005 repair surfaces.

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
''', encoding="utf-8", newline="\n")

# ---------------------------------------------------------------------------
# BSP-003 compatibility: old provider integration test must use grounded judgment.
# ---------------------------------------------------------------------------
replace_once(
    PROVIDER_TEST,
    '''def identity(seed: str) -> str:
    return sha256(seed.encode("utf-8")).hexdigest()


''',
    '''def identity(seed: str) -> str:
    return sha256(seed.encode("utf-8")).hexdigest()


def grounded_judgment(decision_identity: str, fixture_id: str = "JH-FIX-A-001") -> EvaluatorSideJudgment:
    corpus = load_corpus()
    fixture = next(item for item in corpus["fixtures"] if item["fixture_id"] == fixture_id)
    required: set[str] = set()
    for section in ("pass_paths", "fail_conditions"):
        for entry in fixture["rubric"][section]:
            for constraint in entry["constraints"]:
                if constraint["type"] in {"principle_acknowledged", "principle_violated"}:
                    required.update(constraint["values"])
    adjudications = {
        principle: {
            "status": "NOT_EVIDENCED",
            "evidence": "TEST_ONLY: normalized decision reviewed against fixture principle constraint",
        }
        for principle in sorted(required)
    }
    return EvaluatorSideJudgment.from_fixture(
        decision_identity,
        corpus=corpus,
        fixture=fixture,
        principle_adjudications=adjudications,
        evaluator_evidence=("TEST_ONLY_SYNTHETIC_GROUNDED_REVIEW",),
    )


''',
)
# Only the successful scoring-path test must be grounded. Malformed-response tests do not score.
needle = '''    def test_successful_provider_record_requires_evaluator_side_judgment(self):
        model_request = request()
        adapter = CandidateProviderAdapter(model_request.capability_declaration)
        decision = JiangheResponseNormalizer().normalize(output_text())
        judgment = EvaluatorSideJudgment(decision.identity, (), ())
'''
replacement = '''    def test_successful_provider_record_requires_evaluator_side_judgment(self):
        model_request = request()
        adapter = CandidateProviderAdapter(model_request.capability_declaration)
        decision = JiangheResponseNormalizer().normalize(output_text())
        judgment = grounded_judgment(decision.identity)
'''
replace_once(PROVIDER_TEST, needle, replacement)

print("applied prespend final fixes v04")

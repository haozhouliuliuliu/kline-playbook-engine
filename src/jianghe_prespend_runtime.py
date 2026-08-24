"""Spend-eligible Jianghe provider runtime.

This is the only code path allowed to become a paid model transport. It is
provider-neutral at the research boundary and fail-closed by default:
credentials are resolved only at invocation time, no provider tools/search are
enabled, there are no semantic retries, and every paid attempt requires an
explicit authorization object plus a shared CNY budget reservation.

The older :mod:`src.jianghe_model_provider` adapter intentionally remains
offline-only.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import time
from typing import Callable, Mapping
from urllib import request as urllib_request
from urllib.error import HTTPError, URLError

from src.jianghe_ai_trader import JiangheObservation
from src.jianghe_source_only_verification import (
    ROOT as REPOSITORY_ROOT,
    _repository_blob_bytes,
)


RUNTIME_VERSION = "JIANGHE_PRESPEND_RUNTIME_V0_1"
STRUCTURED_SCHEMA_VERSION = "JIANGHE_CANONICAL_STRUCTURED_OBSERVATION_V0_1"
SELECTED_CONTEXT_VERSION = "JIANGHE_SELECTED_CONTEXT_V0_1"
VISUAL_INPUT_VERSION = "JIANGHE_VISUAL_INPUT_V0_1"
SPEND_REQUEST_VERSION = "JIANGHE_SPEND_ELIGIBLE_REQUEST_V0_1"
BUDGET_LEDGER_VERSION = "JIANGHE_SHARED_CNY_BUDGET_LEDGER_V0_1"
HARD_PROJECT_CAP_CNY = Decimal("100.00")
CURRENT_ACTIVE_KNOWLEDGE_PACK_IDENTITY = (
    "e079c225825e08d5ccca07feddd9a6dbc1a6e07189d033fb1929b0c689e90fd2"
)
CURRENT_PRIMARY_MANIFEST_IDENTITY = (
    "f767253dc4c2d1b17f57b9adfdc903907a97df8d4697dbe0fae0f603427dbf36"
)
PRICING_AUTHORITY_PATH = (
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

_SHA256 = re.compile(r"^[0-9a-f]{64}$")
_ALLOWED_CONTEXT_PATHS = frozenset(
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
_FORBIDDEN_FIELD_NAMES = frozenset(
    {
        "outcome", "candidate_outcome", "pnl", "profit", "profits", "loss", "losses",
        "win_rate", "winrate", "sharpe", "expectancy", "future_price", "future_return",
        "return", "returns", "equity_curve",
    }
)


class PrespendRuntimeError(RuntimeError):
    pass


class PaidCallNotAuthorizedError(PrespendRuntimeError):
    pass


class BudgetGuardError(PrespendRuntimeError):
    pass


class ProviderTransportError(PrespendRuntimeError):
    pass


class ProviderResponseError(PrespendRuntimeError):
    pass


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _hash_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def current_context_selection_policy_identity() -> str:
    """Identity of the only spend-eligible Jianghe context selection policy."""
    return _hash(
        {
            "version": _CONTEXT_SELECTION_POLICY_VERSION,
            "allowed_repository_paths": tuple(sorted(_ALLOWED_CONTEXT_PATHS)),
            "repository_byte_authority": "EXACT_COMMITTED_GIT_BLOB_BYTES",
            "outcome_future_fixture_authority": "FORBIDDEN",
            "selection_semantics": "FIXTURE_SOURCE_ANCHORS_TO_PRIMARY_V0_5_SAFE_SEMANTIC_PROJECTION",
        }
    )


def _require_text(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be non-empty text")
    return value


def _require_sha256(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not _SHA256.fullmatch(value):
        raise ValueError(f"{field_name} must be a lowercase sha256")
    return value


def _require_aware(value: datetime, field_name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


def _utc(value: datetime) -> str:
    return _require_aware(value, "datetime").astimezone(timezone.utc).isoformat(
        timespec="microseconds"
    )


def _decimal(value: object, field_name: str, *, positive: bool = False) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field_name} must be a finite Decimal") from None
    if not result.is_finite() or (positive and result <= 0) or (not positive and result < 0):
        raise ValueError(f"{field_name} has invalid Decimal value")
    return result


def _scan_forbidden(value: object, path: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if not isinstance(key, str):
                raise ValueError(f"{path} key must be text")
            normalized = key.lower().replace("-", "_").replace(" ", "_")
            if normalized in _FORBIDDEN_FIELD_NAMES:
                raise ValueError(f"{path} contains forbidden outcome/future field {key}")
            _scan_forbidden(nested, f"{path}.{key}")
    elif isinstance(value, (list, tuple)):
        for index, nested in enumerate(value):
            _scan_forbidden(nested, f"{path}[{index}]")


_PRIMARY_MODEL_CONTEXT_FIELDS = (
    "claim_category",
    "claim_id",
    "contradiction_ids",
    "family_scope",
    "invalidation_scope",
    "management_or_exit_scope",
    "no_trade_guard",
    "operationalization_interpretation",
    "pre_freeze_disposition",
    "selected_interpretation_text",
    "semantic_mode",
    "source_meaning",
    "unknown_ids",
)
_FORBIDDEN_MODEL_CONTEXT_CATEGORY_MARKERS = ("OUTCOME", "PERFORMANCE", "PNL", "PROFIT", "RETURN")
_FORBIDDEN_MODEL_CONTEXT_VALUE_MARKERS = (
    "candidate_outcome",
    "future_price",
    "future_return",
    "real_candidate_pnl",
    "win_rate",
    "sharpe",
    "expectancy",
    "后续价格路径",
    "任何盈亏结果",
    "任何结果标签",
    "胜率/期望值",
)


def _primary_model_context_projection(record: Mapping[str, object]) -> str:
    """Return the only PRIMARY V0.5 fields allowed to leave the process as model context.

    The full PRIMARY registry record remains local provenance. Review metadata, source-file
    paths, fixture material, historical outcome text and other audit baggage are not sent.
    """
    if not isinstance(record, Mapping):
        raise ValueError("PRIMARY context source record must be an object")
    claim_id = _require_text(record.get("claim_id"), "primary_context.claim_id")
    claim_category = _require_text(record.get("claim_category"), "primary_context.claim_category")
    upper_category = claim_category.upper()
    if any(marker in upper_category for marker in _FORBIDDEN_MODEL_CONTEXT_CATEGORY_MARKERS):
        raise ValueError("outcome/performance claim category is not spend-eligible context")

    def text_or_unknown(name: str) -> str:
        value = record.get(name)
        if value is None:
            return "UNKNOWN"
        return _require_text(value, f"primary_context.{name}")

    def text_list(name: str) -> list[str]:
        value = record.get(name)
        if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
            raise ValueError(f"primary_context.{name} must be a string list")
        if len(set(value)) != len(value):
            raise ValueError(f"primary_context.{name} must be unique")
        return sorted(value)

    projection: dict[str, object] = {
        "claim_category": claim_category,
        "claim_id": claim_id,
        "contradiction_ids": text_list("contradiction_ids"),
        "family_scope": text_list("family_scope"),
        "invalidation_scope": text_or_unknown("invalidation_scope"),
        "management_or_exit_scope": text_or_unknown("management_or_exit_scope"),
        "no_trade_guard": text_or_unknown("no_trade_guard"),
        "operationalization_interpretation": text_or_unknown("operationalization_interpretation"),
        "pre_freeze_disposition": text_or_unknown("pre_freeze_disposition"),
        "selected_interpretation_text": text_or_unknown("selected_interpretation_text"),
        "semantic_mode": text_or_unknown("semantic_mode"),
        "source_meaning": text_or_unknown("source_meaning"),
        "unknown_ids": text_list("unknown_ids"),
    }
    _scan_forbidden(projection, "primary_model_context")
    serialized = _canonical_json(projection)
    lowered = serialized.lower()
    if any(marker.lower() in lowered for marker in _FORBIDDEN_MODEL_CONTEXT_VALUE_MARKERS):
        raise ValueError("selected PRIMARY semantic projection contains forbidden outcome/future material")
    return serialized


@dataclass(frozen=True)
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

    def to_payload(self) -> dict[str, str]:
        return {
            "repository_path": self.repository_path,
            "repository_content_sha256": self.repository_content_sha256,
            "selected_text_sha256": self.selected_text_sha256,
            "selected_text": self.selected_text,
        }


def _fixture_context_material(fixture_id: str) -> dict[str, object]:
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
        payload["model_context_identity"] = (
            self.model_payload()["model_context_identity"]
            if self.fixture_id is not None and self.selection_basis_identity is not None
            else None
        )
        if include_identity:
            payload["selected_context_identity"] = self.identity
        return payload

    def model_payload(self) -> dict[str, object]:
        """Exact context material sent to the model; fixture answers and audit baggage stay local."""
        if self.fixture_id is None or self.selection_basis_identity is None:
            raise ValueError("model context requires deterministic fixture-bound selection")
        projected_documents: list[dict[str, object]] = []
        for item in self.documents:
            if item.repository_path != PRIMARY_REGISTRY_RELATIVE_PATH:
                raise ValueError("spend-eligible model context must project current PRIMARY V0.5 records")
            try:
                record = json.loads(item.selected_text)
            except json.JSONDecodeError as error:
                raise ValueError("selected PRIMARY source record is malformed") from error
            if not isinstance(record, Mapping):
                raise ValueError("selected PRIMARY source record must be an object")
            claim_id = _require_text(record.get("claim_id"), "selected_primary.claim_id")
            if claim_id not in self.source_claim_ids:
                raise ValueError("selected PRIMARY record is outside fixture source anchors")
            projected_text = _primary_model_context_projection(record)
            projected_documents.append(
                {
                    "claim_id": claim_id,
                    "source_record_identity": item.identity,
                    "selected_text": projected_text,
                    "selected_text_sha256": sha256(projected_text.encode("utf-8")).hexdigest(),
                }
            )
        projected_documents.sort(key=lambda value: (str(value["claim_id"]), str(value["source_record_identity"])))
        payload: dict[str, object] = {
            "version": SELECTED_CONTEXT_VERSION,
            "knowledge_pack_identity": self.knowledge_pack_identity,
            "primary_manifest_identity": self.primary_manifest_identity,
            "primary_registry_version": self.primary_registry_version,
            "context_selection_policy_identity": self.context_selection_policy_identity,
            "source_claim_ids": list(self.source_claim_ids),
            "selection_basis_identity": self.selection_basis_identity,
            "documents": projected_documents,
        }
        payload["model_context_identity"] = _hash(payload)
        return payload


@dataclass(frozen=True, init=False)
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


@dataclass(frozen=True)
class VisualInputArtifact:
    source_observation_identity: str
    renderer_identity: str
    png_bytes: bytes
    mime_type: str = "image/png"
    content_sha256: str = field(init=False)
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_sha256(self.source_observation_identity, "source_observation_identity")
        _require_text(self.renderer_identity, "renderer_identity")
        if self.mime_type != "image/png":
            raise ValueError("spend-eligible visual input must be canonical PNG")
        if not isinstance(self.png_bytes, bytes) or not self.png_bytes:
            raise ValueError("png_bytes must be non-empty bytes")
        content_hash = _hash_bytes(self.png_bytes)
        object.__setattr__(self, "content_sha256", content_hash)
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "version": VISUAL_INPUT_VERSION,
                    "source_observation_identity": self.source_observation_identity,
                    "renderer_identity": self.renderer_identity,
                    "mime_type": self.mime_type,
                    "content_sha256": content_hash,
                }
            ),
        )

    def data_url(self) -> str:
        return "data:image/png;base64," + base64.b64encode(self.png_bytes).decode("ascii")


@dataclass(frozen=True)
class SpendEligibleJiangheRequest:
    system_prompt: str
    decision_prompt: str
    response_schema: Mapping[str, object]
    context: SelectedJiangheContextArtifact
    structured_observation: CanonicalStructuredObservationArtifact
    visuals: tuple[VisualInputArtifact, ...]
    max_output_tokens: int
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        _require_text(self.system_prompt, "system_prompt")
        _require_text(self.decision_prompt, "decision_prompt")
        if not isinstance(self.response_schema, Mapping) or not self.response_schema:
            raise ValueError("response_schema must be a non-empty mapping")
        _scan_forbidden(self.response_schema, "response_schema")
        if not isinstance(self.context, SelectedJiangheContextArtifact):
            raise TypeError("context must be SelectedJiangheContextArtifact")
        if self.context.fixture_id is None or self.context.selection_basis_identity is None:
            raise ValueError("spend-eligible context must come from deterministic fixture source anchors")
        if not isinstance(self.structured_observation, CanonicalStructuredObservationArtifact):
            raise TypeError("structured_observation must be canonical")
        if not isinstance(self.max_output_tokens, int) or isinstance(self.max_output_tokens, bool) or self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be a positive integer")
        observation_identity = self.structured_observation.source_observation_identity
        if not self.visuals:
            raise ValueError("real-model fidelity request must include visual K-line input")
        if any(item.source_observation_identity != observation_identity for item in self.visuals):
            raise ValueError("all visual inputs must bind the same canonical observation")
        _canonical_json(self.response_schema)
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "version": SPEND_REQUEST_VERSION,
                    "system_prompt_sha256": sha256(self.system_prompt.encode("utf-8")).hexdigest(),
                    "decision_prompt_sha256": sha256(self.decision_prompt.encode("utf-8")).hexdigest(),
                    "response_schema": self.response_schema,
                    "selected_context_identity": self.context.identity,
                    "model_context_identity": self.context.model_payload()["model_context_identity"],
                    "structured_observation_identity": self.structured_observation.identity,
                    "visual_identities": [item.identity for item in self.visuals],
                    "max_output_tokens": self.max_output_tokens,
                }
            ),
        )

    def common_model_text(self) -> str:
        return _canonical_json(
            {
                "jianghe_context": self.context.model_payload(),
                "canonical_observation": self.structured_observation.payload(),
                "decision_instruction": self.decision_prompt,
            }
        )


@dataclass(frozen=True)
class ProviderSpec:
    provider_id: str
    model_id: str
    endpoint: str
    api_key_env: str
    payload_style: str
    official_authority_urls: tuple[str, ...]

    def __post_init__(self) -> None:
        for name in ("provider_id", "model_id", "endpoint", "api_key_env", "payload_style"):
            _require_text(getattr(self, name), name)
        if not self.endpoint.startswith("https://"):
            raise ValueError("provider endpoint must be https")
        if self.payload_style not in {"KIMI_OPENAI", "DEEPSEEK_OPENAI", "MINIMAX_V2"}:
            raise ValueError("unsupported provider payload style")
        if not self.official_authority_urls or any(
            not url.startswith("https://") for url in self.official_authority_urls
        ):
            raise ValueError("official provider authority URLs are required")

    @property
    def identity(self) -> str:
        return _hash(
            {
                "provider_id": self.provider_id,
                "model_id": self.model_id,
                "endpoint": self.endpoint,
                "payload_style": self.payload_style,
                "official_authority_urls": tuple(sorted(self.official_authority_urls)),
            }
        )


KIMI_K3_SPEC = ProviderSpec(
    provider_id="KIMI", model_id="kimi-k3",
    endpoint="https://api.moonshot.cn/v1/chat/completions",
    api_key_env="MOONSHOT_API_KEY", payload_style="KIMI_OPENAI",
    official_authority_urls=(
        "https://platform.kimi.com/",
        "https://www.kimi.ai/help/kimi-api/api-model-selection",
        "https://www.kimi.ai/zh-hans/help/kimi-code/cli-getting-started",
    ),
)
DEEPSEEK_VISION_SPEC = ProviderSpec(
    provider_id="DEEPSEEK", model_id="deepseek-v4-flash-vision-exp",
    endpoint="https://api.deepseek.com/chat/completions",
    api_key_env="DEEPSEEK_API_KEY", payload_style="DEEPSEEK_OPENAI",
    official_authority_urls=(
        "https://api-docs.deepseek.com/",
        "https://github.com/deepseek-ai/deepseek-harness",
    ),
)
MINIMAX_M3_SPEC = ProviderSpec(
    provider_id="MINIMAX", model_id="MiniMax-M3",
    endpoint="https://api.minimaxi.com/v1/chat/completions",
    api_key_env="MINIMAX_API_KEY", payload_style="MINIMAX_V2",
    official_authority_urls=(
        "https://www.minimax.cn/models/text/m3",
        "https://platform.minimaxi.com/docs/api-reference/api-overview",
    ),
)
IMPLEMENTATION_TARGET_SPECS = (KIMI_K3_SPEC, DEEPSEEK_VISION_SPEC, MINIMAX_M3_SPEC)


@dataclass(frozen=True)
class RateCard:
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

    def __post_init__(self) -> None:
        _require_text(self.provider_id, "provider_id")
        _require_text(self.model_id, "model_id")
        if self.currency not in {"CNY", "USD"}:
            raise ValueError("rate-card currency must be CNY or USD")
        input_price = _decimal(self.input_per_million, "input_per_million", positive=True)
        output_price = _decimal(self.output_per_million, "output_per_million", positive=True)
        if type(self.image_tokens_billed_as_input) is not bool or not self.image_tokens_billed_as_input:
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
        if not self.authority_uri.startswith("https://"):
            raise ValueError("rate-card authority must be https")
        _require_aware(self.effective_at, "effective_at")
        _require_aware(self.expires_at, "expires_at")
        if self.expires_at <= self.effective_at:
            raise ValueError("rate card must have a bounded validity window")
        object.__setattr__(self, "input_per_million", input_price)
        object.__setattr__(self, "output_per_million", output_price)
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "provider_id": self.provider_id, "model_id": self.model_id,
                    "currency": self.currency, "input_per_million": str(input_price),
                    "output_per_million": str(output_price),
                    "image_tokens_billed_as_input": True,
                    "image_billing_mode": self.image_billing_mode,
                    "fixed_input_tokens_per_image": self.fixed_input_tokens_per_image,
                    "repository_authority_identity": self.repository_authority_identity,
                    "authority_uri": self.authority_uri,
                    "effective_at": _utc(self.effective_at), "expires_at": _utc(self.expires_at),
                }
            ),
        )


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
    allowed_statuses = {
        "VERIFIED_CURRENT_FOR_SPEND_GUARD",
        "OWNER_APPROVED_CONSERVATIVE_FAMILY_INHERITANCE_FOR_SPEND_GUARD",
    }
    if entry.get("status") not in allowed_statuses:
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
        image_billing_mode = str(entry["image_billing_mode"])
        raw_fixed_tokens = entry.get("fixed_input_tokens_per_image")
        fixed_tokens = None if raw_fixed_tokens is None else int(raw_fixed_tokens)
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
        image_billing_mode=image_billing_mode,
        fixed_input_tokens_per_image=fixed_tokens,
        repository_authority_identity=authority_identity,
    )
    if not (card.effective_at <= now < card.expires_at):
        raise BudgetGuardError("repository pricing authority is stale or not yet effective")
    return card


@dataclass(frozen=True)
class FxAuthority:
    usd_to_cny: Decimal
    authority_uri: str
    effective_at: datetime
    expires_at: datetime
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        rate = _decimal(self.usd_to_cny, "usd_to_cny", positive=True)
        _require_text(self.authority_uri, "authority_uri")
        if not self.authority_uri.startswith("https://"):
            raise ValueError("FX authority must be https")
        _require_aware(self.effective_at, "effective_at")
        _require_aware(self.expires_at, "expires_at")
        if self.expires_at <= self.effective_at:
            raise ValueError("FX authority must have a bounded validity window")
        object.__setattr__(self, "usd_to_cny", rate)
        object.__setattr__(
            self, "identity",
            _hash({"usd_to_cny": str(rate), "authority_uri": self.authority_uri,
                   "effective_at": _utc(self.effective_at), "expires_at": _utc(self.expires_at)}),
        )


@dataclass(frozen=True)
class InvocationBounds:
    max_text_input_tokens: int
    max_image_tokens: int
    max_output_tokens: int
    transport_retries: int = 0

    def __post_init__(self) -> None:
        for name in ("max_text_input_tokens", "max_image_tokens", "max_output_tokens"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.max_output_tokens <= 0:
            raise ValueError("max_output_tokens must be positive")
        if self.transport_retries != 0:
            raise ValueError("initial spend-eligible runtime permits no automatic retries")

    @property
    def total_input_tokens(self) -> int:
        return self.max_text_input_tokens + self.max_image_tokens


@dataclass(frozen=True)
class BudgetReservation:
    reservation_id: str
    provider_id: str
    model_id: str
    rate_card_identity: str
    fx_identity: str | None
    bounds: InvocationBounds
    reserved_cny: Decimal
    created_at: datetime


class CnyBudgetLedger:
    """One shared fail-closed hard budget across every provider."""

    def __init__(self, cap_cny: Decimal = HARD_PROJECT_CAP_CNY) -> None:
        cap = _decimal(cap_cny, "cap_cny", positive=True)
        if cap > HARD_PROJECT_CAP_CNY:
            raise BudgetGuardError("project hard cap cannot exceed CNY 100")
        self._cap = cap
        self._spent = Decimal("0")
        self._outstanding: BudgetReservation | None = None
        self._history: list[tuple[str, str]] = []

    @property
    def cap_cny(self) -> Decimal:
        return self._cap

    @property
    def spent_cny(self) -> Decimal:
        return self._spent

    @property
    def remaining_cny(self) -> Decimal:
        outstanding = Decimal("0") if self._outstanding is None else self._outstanding.reserved_cny
        return self._cap - self._spent - outstanding

    @property
    def history(self) -> tuple[tuple[str, str], ...]:
        return tuple(self._history)

    def _to_cny(self, amount: Decimal, rate_card: RateCard, fx: FxAuthority | None, now: datetime) -> Decimal:
        _require_aware(now, "now")
        if not (rate_card.effective_at <= now < rate_card.expires_at):
            raise BudgetGuardError("rate card is expired or not yet effective")
        if rate_card.currency == "CNY":
            if fx is not None:
                raise BudgetGuardError("CNY rate card must not carry an FX authority")
            return amount
        if fx is None:
            raise BudgetGuardError("USD pricing requires explicit FX authority")
        if not (fx.effective_at <= now < fx.expires_at):
            raise BudgetGuardError("FX authority is expired or not yet effective")
        return amount * fx.usd_to_cny

    def reserve(self, spec: ProviderSpec, rate_card: RateCard, bounds: InvocationBounds, *,
                fx: FxAuthority | None, now: datetime) -> BudgetReservation:
        if self._outstanding is not None:
            raise BudgetGuardError("previous reservation must be reconciled before another call")
        if rate_card.provider_id != spec.provider_id or rate_card.model_id != spec.model_id:
            raise BudgetGuardError("rate card does not match provider/model")
        if not rate_card.image_tokens_billed_as_input:
            raise BudgetGuardError("image billing semantics are unknown")
        million = Decimal("1000000")
        native = (
            Decimal(bounds.total_input_tokens) * rate_card.input_per_million
            + Decimal(bounds.max_output_tokens) * rate_card.output_per_million
        ) / million
        worst_case_cny = self._to_cny(native, rate_card, fx, now)
        if worst_case_cny <= 0:
            raise BudgetGuardError("worst-case reservation must be positive")
        if self._spent + worst_case_cny > self._cap:
            raise BudgetGuardError("next call would exceed the shared CNY hard cap")
        reservation_id = _hash(
            {"version": BUDGET_LEDGER_VERSION, "provider_spec_identity": spec.identity,
             "rate_card_identity": rate_card.identity, "fx_identity": None if fx is None else fx.identity,
             "bounds": {"max_text_input_tokens": bounds.max_text_input_tokens,
                        "max_image_tokens": bounds.max_image_tokens,
                        "max_output_tokens": bounds.max_output_tokens,
                        "transport_retries": bounds.transport_retries},
             "spent_before": str(self._spent), "reserved_cny": str(worst_case_cny),
             "created_at": _utc(now)}
        )
        reservation = BudgetReservation(
            reservation_id, spec.provider_id, spec.model_id, rate_card.identity,
            None if fx is None else fx.identity, bounds, worst_case_cny, now,
        )
        self._outstanding = reservation
        self._history.append(("RESERVED", reservation_id))
        return reservation

    def reconcile(self, reservation_id: str, *, text_input_tokens: int, image_tokens: int,
                  output_tokens: int, rate_card: RateCard, fx: FxAuthority | None,
                  now: datetime) -> Decimal:
        reservation = self._outstanding
        if reservation is None or reservation.reservation_id != reservation_id:
            raise BudgetGuardError("reservation is missing or mismatched")
        for name, value in (("text_input_tokens", text_input_tokens),
                            ("image_tokens", image_tokens), ("output_tokens", output_tokens)):
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise BudgetGuardError(f"{name} must be a non-negative integer")
        if rate_card.identity != reservation.rate_card_identity:
            raise BudgetGuardError("reconciliation rate card differs from reservation")
        if (None if fx is None else fx.identity) != reservation.fx_identity:
            raise BudgetGuardError("reconciliation FX authority differs from reservation")
        bounds = reservation.bounds
        if text_input_tokens + image_tokens > bounds.total_input_tokens or output_tokens > bounds.max_output_tokens:
            self._spent += reservation.reserved_cny
            self._outstanding = None
            self._history.append(("BOUNDS_BREACH_FULL_RESERVATION_CHARGED", reservation_id))
            raise BudgetGuardError("provider usage exceeded a pre-call bound")
        million = Decimal("1000000")
        native = (
            Decimal(text_input_tokens + image_tokens) * rate_card.input_per_million
            + Decimal(output_tokens) * rate_card.output_per_million
        ) / million
        actual_cny = self._to_cny(native, rate_card, fx, now)
        if actual_cny > reservation.reserved_cny:
            self._spent += reservation.reserved_cny
            self._outstanding = None
            self._history.append(("RESERVATION_UNDERRUN_GUARD_TRIPPED", reservation_id))
            raise BudgetGuardError("actual provider cost exceeded reserved worst-case amount")
        self._spent += actual_cny
        self._outstanding = None
        self._history.append(("RECONCILED", reservation_id))
        return actual_cny

    def cancel_before_network(self, reservation_id: str, *, reason: str) -> None:
        reservation = self._outstanding
        if reservation is None or reservation.reservation_id != reservation_id:
            raise BudgetGuardError("reservation is missing or mismatched")
        _require_text(reason, "reason")
        self._outstanding = None
        self._history.append((f"CANCELLED_BEFORE_NETWORK:{reason}", reservation_id))

    def consume_full_reservation_on_unknown_usage(self, reservation_id: str) -> None:
        reservation = self._outstanding
        if reservation is None or reservation.reservation_id != reservation_id:
            raise BudgetGuardError("reservation is missing or mismatched")
        self._spent += reservation.reserved_cny
        self._outstanding = None
        self._history.append(("UNKNOWN_USAGE_FULL_RESERVATION_CHARGED", reservation_id))


@dataclass(frozen=True)
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


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    headers: Mapping[str, str]
    body: bytes


HttpPost = Callable[[str, Mapping[str, str], bytes, float], HttpResponse]


def _default_http_post(url: str, headers: Mapping[str, str], body: bytes, timeout: float) -> HttpResponse:
    req = urllib_request.Request(url=url, data=body, headers=dict(headers), method="POST")
    try:
        with urllib_request.urlopen(req, timeout=timeout) as response:
            return HttpResponse(int(response.status), {str(k): str(v) for k, v in response.headers.items()}, response.read())
    except HTTPError as error:
        return HttpResponse(int(error.code), {str(k): str(v) for k, v in error.headers.items()}, error.read())
    except URLError as error:
        raise ProviderTransportError(f"provider transport failed: {error.reason}") from error


@dataclass(frozen=True)
class ProviderUsage:
    text_input_tokens: int
    image_tokens: int
    output_tokens: int


@dataclass(frozen=True)
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


class DomesticProviderTransport:
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
            payload = {
                "model": self.spec.model_id,
                "messages": [
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": multimodal_content},
                ],
                "max_tokens": request.max_output_tokens,
                "response_format": {"type": "json_object"},
                "tools": [],
            }
            if getattr(request, "contract_version", None) != "JIANGHE_STAGE_A_REQUEST_V0_1":
                payload["thinking"] = {"type": "enabled"}
                payload["reasoning_effort"] = "max"
            return payload
        if self.spec.payload_style == "MINIMAX_V2":
            payload = {
                "model": self.spec.model_id,
                "messages": [
                    {"role": "system", "content": request.system_prompt},
                    {"role": "user", "content": multimodal_content},
                ],
                "max_completion_tokens": request.max_output_tokens,
                "stream": False,
                "tools": [],
            }
            if getattr(request, "contract_version", None) != "JIANGHE_STAGE_A_REQUEST_V0_1":
                payload["thinking"] = {"type": "adaptive"}
                payload["reasoning_split"] = True
            return payload
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
        if rate_card.image_billing_mode == "FIXED_INPUT_TOKENS_PER_IMAGE":
            expected_image_tokens = (
                len(request.visuals) * int(rate_card.fixed_input_tokens_per_image or 0)
            )
        elif rate_card.image_billing_mode == "INPUT_TOKENS":
            # The exact serialized multimodal payload already contains the image data URL.
            # The X2-bytes+8192 policy therefore supplies a deterministic pre-network
            # upper bound without inventing a provider-specific fixed image conversion.
            expected_image_tokens = 0
        else:
            raise BudgetGuardError("unknown image billing mode fails closed before network")
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


__all__ = [
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
]

"""Offline project runtime spine for MINIMAL_PERSISTENT_DEEPSEEK_TRADER_PROTOTYPE_V0_1.

This module assembles project-owned context, persistence, Jianghe retrieval, tools,
guards and audit.  It intentionally contains no network/provider transport method;
real DeepSeek execution remains impossible until a separate execution authority and
transport seam are introduced.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from uuid import uuid4

from src.deepseek_mechanical_guards import assert_no_4h_exact_volume_reconciliation
from src.jianghe_ai_trader import JiangheAITraderIdentity, JiangheObservation
from src.jianghe_canon_retrieval import JiangheCanonHit, JiangheCanonRetriever
from src.jianghe_response_normalizer import JiangheResponseNormalizer, NormalizedJiangheDecision
from src.persistent_trader_store import PersistentTraderStore, working_memory_to_payload


CURRENT_MODEL = "deepseek-v4-flash-vision-exp"
MODEL_SOURCE = "DEEPSEEK_ONLY"
PINNED_HARNESS_VERSION = "0.1.1-rc.2"
PINNED_HARNESS_COMMIT = "b150a551b8d465e31e418e1b2eaf5e79bbb7d28e"
PROJECT_TRANSPORT_PATCH = "integrations/deepseek-harness/"
GENERAL_MAX_RETRIES = 0
ACTIVE_TIMEFRAMES = ("4H", "1H", "15m", "5m")
RUNTIME_CONTRACT_VERSION = "KPE_PERSISTENT_DEEPSEEK_RUNTIME_CONTRACT_V0_1"
CONTEXT_SCHEMA_VERSION = "KPE_PERSISTENT_DEEPSEEK_CONTEXT_V0_1"


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _text_hash(value: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("prompt text must be non-empty")
    return sha256(value.encode("utf-8")).hexdigest()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("audit time must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _json_compatible(value: object, field_name: str) -> Any:
    try:
        encoded = _canonical_json(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{field_name} must be JSON-compatible") from error
    return json.loads(encoded)


@dataclass(frozen=True)
class DeepSeekHarnessRuntimeContract:
    system_prompt_sha256: str
    decision_prompt_sha256: str
    model_source: str = MODEL_SOURCE
    model_id: str = CURRENT_MODEL
    harness_version: str = PINNED_HARNESS_VERSION
    harness_commit: str = PINNED_HARNESS_COMMIT
    project_transport_patch: str = PROJECT_TRANSPORT_PATCH
    general_max_retries: int = GENERAL_MAX_RETRIES
    deployment: str = "LOCAL_WORKSTATION_FIRST"
    model_substitution: str = "FORBIDDEN"
    prompt_mutation: str = "FORBIDDEN"
    hidden_second_request: str = "FORBIDDEN_FAIL_CLOSED"
    provider_call_authorized: bool = False
    identity: str = field(init=False)

    def __post_init__(self) -> None:
        if self.model_source != MODEL_SOURCE or self.model_id != CURRENT_MODEL:
            raise ValueError("runtime contract must use the sole active DeepSeek model")
        if self.harness_version != PINNED_HARNESS_VERSION or self.harness_commit != PINNED_HARNESS_COMMIT:
            raise ValueError("runtime contract must use the admitted pinned Harness build")
        if self.project_transport_patch != PROJECT_TRANSPORT_PATCH:
            raise ValueError("project fail-closed DeepSeek transport patch is mandatory")
        if type(self.general_max_retries) is not int or self.general_max_retries != 0:
            raise ValueError("general model retries must remain exactly zero")
        if self.deployment != "LOCAL_WORKSTATION_FIRST":
            raise ValueError("prototype deployment must remain local-workstation-first")
        if self.model_substitution != "FORBIDDEN" or self.prompt_mutation != "FORBIDDEN":
            raise ValueError("model substitution and prompt mutation are forbidden")
        if self.hidden_second_request != "FORBIDDEN_FAIL_CLOSED":
            raise ValueError("hidden second request must fail closed")
        if self.provider_call_authorized is not False:
            raise ValueError("current prototype contract must not authorize a provider call")
        for value in (self.system_prompt_sha256, self.decision_prompt_sha256):
            if not isinstance(value, str) or len(value) != 64:
                raise ValueError("prompt identities must be SHA-256 hex strings")
        object.__setattr__(
            self,
            "identity",
            _hash(
                {
                    "version": RUNTIME_CONTRACT_VERSION,
                    "model_source": self.model_source,
                    "model_id": self.model_id,
                    "harness_version": self.harness_version,
                    "harness_commit": self.harness_commit,
                    "project_transport_patch": self.project_transport_patch,
                    "general_max_retries": self.general_max_retries,
                    "deployment": self.deployment,
                    "model_substitution": self.model_substitution,
                    "prompt_mutation": self.prompt_mutation,
                    "hidden_second_request": self.hidden_second_request,
                    "provider_call_authorized": self.provider_call_authorized,
                    "system_prompt_sha256": self.system_prompt_sha256,
                    "decision_prompt_sha256": self.decision_prompt_sha256,
                }
            ),
        )

    @classmethod
    def from_prompts(cls, *, system_prompt: str, decision_prompt: str) -> "DeepSeekHarnessRuntimeContract":
        return cls(_text_hash(system_prompt), _text_hash(decision_prompt))

    def assert_prompts_unchanged(self, *, system_prompt: str, decision_prompt: str) -> None:
        if _text_hash(system_prompt) != self.system_prompt_sha256:
            raise ValueError("system prompt mutation is forbidden")
        if _text_hash(decision_prompt) != self.decision_prompt_sha256:
            raise ValueError("decision prompt mutation is forbidden")

    def to_payload(self) -> dict[str, object]:
        return {
            "runtime_contract_version": RUNTIME_CONTRACT_VERSION,
            "identity": self.identity,
            "model_source": self.model_source,
            "model_id": self.model_id,
            "harness_version": self.harness_version,
            "harness_commit": self.harness_commit,
            "project_transport_patch": self.project_transport_patch,
            "general_max_retries": self.general_max_retries,
            "deployment": self.deployment,
            "model_substitution": self.model_substitution,
            "prompt_mutation": self.prompt_mutation,
            "hidden_second_request": self.hidden_second_request,
            "provider_call_authorized": self.provider_call_authorized,
            "system_prompt_sha256": self.system_prompt_sha256,
            "decision_prompt_sha256": self.decision_prompt_sha256,
        }


@dataclass(frozen=True)
class PreparedModelRequest:
    request_id: str
    created_at: datetime
    trader_identity: str
    observation_identity: str
    model_id: str
    system_prompt: str
    decision_prompt: str
    context: Mapping[str, Any]
    context_sha256: str
    runtime_contract_identity: str


ToolFunction = Callable[[Mapping[str, Any]], Mapping[str, Any]]


class ProjectToolRegistry:
    """Project-owned tool dispatch with append-only audit around every invocation."""

    def __init__(self, store: PersistentTraderStore, *, clock: Callable[[], datetime] = _utc_now) -> None:
        self._store = store
        self._clock = clock
        self._tools: dict[str, ToolFunction] = {}

    @property
    def capability_names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))

    def register(self, name: str, function: ToolFunction) -> None:
        if not isinstance(name, str) or not name or name in self._tools:
            raise ValueError("tool name must be unique and non-empty")
        self._tools[name] = function

    def call(
        self,
        name: str,
        arguments: Mapping[str, Any],
        *,
        observation_identity: str | None = None,
        request_id: str | None = None,
    ) -> Mapping[str, Any]:
        if name not in self._tools:
            raise KeyError(name)
        args = _json_compatible(dict(arguments), "tool arguments")
        assert_no_4h_exact_volume_reconciliation(args)
        call_id = f"tool-{uuid4().hex}"
        started = self._clock()
        self._store.append_audit(
            event_id=f"{call_id}-call",
            occurred_at=started,
            event_kind="TOOL_CALL",
            observation_identity=observation_identity,
            request_id=request_id,
            payload={"call_id": call_id, "tool": name, "arguments": args},
        )
        try:
            raw_result = self._tools[name](args)
            result = _json_compatible(dict(raw_result), "tool result")
            assert_no_4h_exact_volume_reconciliation(result)
        except Exception as error:
            self._store.append_audit(
                event_id=f"{call_id}-error",
                occurred_at=self._clock(),
                event_kind="TOOL_ERROR",
                observation_identity=observation_identity,
                request_id=request_id,
                payload={"call_id": call_id, "tool": name, "error_type": type(error).__name__, "error": str(error)},
            )
            raise
        self._store.append_audit(
            event_id=f"{call_id}-result",
            occurred_at=self._clock(),
            event_kind="TOOL_RESULT",
            observation_identity=observation_identity,
            request_id=request_id,
            payload={"call_id": call_id, "tool": name, "result": result, "result_sha256": _hash(result)},
        )
        return result


def observation_to_context_payload(observation: JiangheObservation) -> dict[str, Any]:
    timeframes = set(observation.timeframes)
    if timeframes != set(ACTIVE_TIMEFRAMES):
        raise ValueError(f"prototype observation must expose active stack {ACTIVE_TIMEFRAMES}; got {sorted(timeframes)}")
    payload = {
        "semantic_class": "CAUSAL_MULTI_TIMEFRAME_MARKET_OBSERVATION",
        "observation_identity": observation.identity.identity,
        "schema_version": observation.schema_version,
        "decision_time": _iso(observation.identity.decision_time),
        "exchange_time": _iso(observation.identity.exchange_time),
        "product": observation.identity.product,
        "concrete_contract": observation.identity.concrete_contract,
        "mapping_identity": observation.identity.mapping_identity,
        "timeframes": list(ACTIVE_TIMEFRAMES),
        "four_hour_role": "BACKGROUND_STATE_KEY_ZONE_POSITION_AND_REMAINING_SPACE_ONLY",
        "bars": [
            {
                "timeframe": bar.timeframe,
                "open_time": _iso(bar.open_time),
                "close_time": _iso(bar.close_time),
                "available_at": _iso(bar.available_at),
                "open": bar.open_price,
                "high": bar.high_price,
                "low": bar.low_price,
                "close": bar.close_price,
                "volume": bar.volume,
                "is_closed": bar.is_closed,
            }
            for bar in observation.bars
        ],
        "charts": [
            {
                "timeframe": chart.timeframe,
                "renderer_identity": chart.renderer_identity,
                "renderer_config_identity": chart.renderer_config_identity,
                "visual_artifact_identity": chart.visual_artifact_identity,
                "render_content_hash": chart.render_content_hash,
                "mime_type": chart.mime_type,
                "partial_bar_marked": chart.partial_bar_marked,
            }
            for chart in observation.charts
        ],
        "visible_metadata": [list(item) for item in observation.visible_metadata],
        "active_order_ids": list(observation.active_order_ids),
    }
    assert_no_4h_exact_volume_reconciliation(payload)
    return payload


def default_jianghe_canon_paths(repo_root: str | Path) -> tuple[str, ...]:
    """Return source-grounded Jianghe artifacts admitted to prototype retrieval.

    Mutable project readiness/review files are intentionally excluded.
    """
    root = Path(repo_root)
    base = root / "docs" / "research" / "jianghe"
    direct = (
        "JIANGHE_CURRENT_VIEW_V1_1.md",
        "JIANGHE_TRADER_DOSSIER_V1_1.md",
        "JIANGHE_STRATEGY_FAMILIES_V1_1.md",
        "JIANGHE_CONTRADICTION_REGISTER_V1_1.md",
        "JIANGHE_UNKNOWN_REGISTER_V1_1.md",
    )
    paths: set[Path] = {base / name for name in direct if (base / name).is_file()}
    for pattern in ("JIANGHE_CLAIM_LEDGER*.jsonl", "JIANGHE_CASE_LIBRARY*.md"):
        paths.update(path for path in base.glob(pattern) if path.is_file())
    salvage = base / "second_pass_salvage"
    if salvage.is_dir():
        paths.update(path for path in salvage.glob("JIANGHE_SECOND_PASS_CLAIM_LEDGER_DELTA_V1_1.part*.jsonl") if path.is_file())
    return tuple(sorted(str(path.relative_to(root)) for path in paths))


class PersistentDeepSeekTraderPrototype:
    """Minimal persistent trader spine with no provider execution capability."""

    def __init__(
        self,
        *,
        trader_identity: JiangheAITraderIdentity,
        store: PersistentTraderStore,
        retriever: JiangheCanonRetriever,
        tools: ProjectToolRegistry,
        runtime_contract: DeepSeekHarnessRuntimeContract,
        clock: Callable[[], datetime] = _utc_now,
    ) -> None:
        if trader_identity.model_provider.casefold() != "deepseek":
            raise ValueError("prototype trader identity must use DeepSeek")
        if trader_identity.model_id_version != CURRENT_MODEL:
            raise ValueError("prototype trader identity must use the sole active model")
        if trader_identity.system_prompt_identity != runtime_contract.system_prompt_sha256:
            raise ValueError("trader identity system prompt does not match runtime contract")
        if trader_identity.decision_prompt_identity != runtime_contract.decision_prompt_sha256:
            raise ValueError("trader identity decision prompt does not match runtime contract")
        if tuple(sorted(trader_identity.tool_capability_set)) != tools.capability_names:
            raise ValueError("trader identity tool capability set does not match runtime registry")
        if store.trader_identity != trader_identity.identity:
            raise ValueError("persistent store must be bound to the same trader identity")
        self.trader_identity = trader_identity
        self.store = store
        self.retriever = retriever
        self.tools = tools
        self.runtime_contract = runtime_contract
        self.clock = clock
        self.normalizer = JiangheResponseNormalizer()

    def assemble_context(
        self,
        *,
        observation: JiangheObservation,
        retrieval_query: str,
        journal_limit: int = 6,
        hypothesis_limit: int = 12,
    ) -> tuple[dict[str, Any], tuple[JiangheCanonHit, ...]]:
        hits = self.retriever.search(retrieval_query)
        memory = self.store.load_working_memory()
        journal = self.store.list_journal(limit=journal_limit)
        hypotheses = self.store.list_hypotheses(limit=hypothesis_limit)
        context = {
            "context_schema_version": CONTEXT_SCHEMA_VERSION,
            "trader_identity": self.trader_identity.identity,
            "runtime_contract_identity": self.runtime_contract.identity,
            "knowledge": {
                "jianghe_canon": [hit.to_context_payload() for hit in hits],
                "project_validated_policy": [],
                "retriever_identity": self.retriever.identity,
            },
            "ds_working_memory": working_memory_to_payload(memory),
            "ds_journal": [
                {
                    "entry_id": item.entry_id,
                    "created_at": _iso(item.created_at),
                    "observation_identity": item.observation_identity,
                    "body": item.body,
                    "tags": list(item.tags),
                    "identity": item.identity,
                    "semantic_class": "DS_JOURNAL_REFLECTION_NOT_FACT_OR_POLICY",
                }
                for item in reversed(journal)
            ],
            "ds_hypothesis_memory": [
                {
                    "hypothesis_id": item.hypothesis_id,
                    "statement": item.statement,
                    "falsifier": item.falsifier,
                    "status": item.status,
                    "evidence_references": list(item.evidence_references),
                    "identity": item.identity,
                    "executable_policy": False,
                }
                for item in reversed(hypotheses)
            ],
            "observation": observation_to_context_payload(observation),
            "tool_capabilities": list(self.tools.capability_names),
        }
        assert_no_4h_exact_volume_reconciliation(context)
        return context, hits

    def prepare_model_request(
        self,
        *,
        observation: JiangheObservation,
        retrieval_query: str,
        system_prompt: str,
        decision_prompt: str,
    ) -> PreparedModelRequest:
        self.runtime_contract.assert_prompts_unchanged(system_prompt=system_prompt, decision_prompt=decision_prompt)
        context, hits = self.assemble_context(observation=observation, retrieval_query=retrieval_query)
        created_at = self.clock()
        request_id = f"req-{uuid4().hex}"
        context_sha = _hash(context)
        request_payload = {
            "request_id": request_id,
            "created_at": _iso(created_at),
            "provider": "deepseek",
            "model": CURRENT_MODEL,
            "provider_call_authorized": False,
            "runtime_contract": self.runtime_contract.to_payload(),
            "trader_identity": self.trader_identity.identity,
            "system_prompt": system_prompt,
            "decision_prompt": decision_prompt,
            "system_prompt_sha256": _text_hash(system_prompt),
            "decision_prompt_sha256": _text_hash(decision_prompt),
            "context": context,
            "context_sha256": context_sha,
            "retrieval_identities": [hit.retrieval_identity for hit in hits],
            "visual_artifact_identities": [
                chart.visual_artifact_identity for chart in observation.charts if chart.visual_artifact_identity is not None
            ],
        }
        self.store.append_audit(
            event_id=f"{request_id}-prepared",
            occurred_at=created_at,
            event_kind="MODEL_REQUEST_PREPARED_OFFLINE",
            observation_identity=observation.identity.identity,
            request_id=request_id,
            payload=request_payload,
        )
        return PreparedModelRequest(
            request_id=request_id,
            created_at=created_at,
            trader_identity=self.trader_identity.identity,
            observation_identity=observation.identity.identity,
            model_id=CURRENT_MODEL,
            system_prompt=system_prompt,
            decision_prompt=decision_prompt,
            context=context,
            context_sha256=context_sha,
            runtime_contract_identity=self.runtime_contract.identity,
        )

    def record_model_response(
        self,
        *,
        request_id: str,
        raw_response: str,
        provider_metadata: Mapping[str, object] | None = None,
    ) -> NormalizedJiangheDecision:
        request_events = [event for event in self.store.audit_for_request(request_id) if event.event_kind == "MODEL_REQUEST_PREPARED_OFFLINE"]
        if len(request_events) != 1:
            raise ValueError("response must bind exactly one reconstructed prepared request")
        if any(event.event_kind == "MODEL_RESPONSE_RAW" for event in self.store.audit_for_request(request_id)):
            raise ValueError("a model request may have only one recorded raw response")
        occurred_at = self.clock()
        response_sha = sha256(raw_response.encode("utf-8")).hexdigest()
        self.store.append_audit(
            event_id=f"{request_id}-raw-response",
            occurred_at=occurred_at,
            event_kind="MODEL_RESPONSE_RAW",
            observation_identity=request_events[0].observation_identity,
            request_id=request_id,
            payload={"raw_response": raw_response, "raw_response_sha256": response_sha},
        )
        # Durably retain the non-secret provider/billing metadata the moment the
        # response arrives, BEFORE normalization, so a schema rejection cannot
        # cause already-received usage/request metadata to be lost.
        if provider_metadata:
            safe_metadata = {
                key: value
                for key, value in provider_metadata.items()
                if key in (
                    "provider", "model", "finish_reason", "provider_request_id",
                    "token_usage", "status", "request_count", "image_count",
                )
                and value is not None
            }
            if safe_metadata:
                self.store.append_audit(
                    event_id=f"{request_id}-provider-metadata",
                    occurred_at=occurred_at,
                    event_kind="MODEL_PROVIDER_RESPONSE_METADATA",
                    observation_identity=request_events[0].observation_identity,
                    request_id=request_id,
                    payload={"raw_response_sha256": response_sha, **safe_metadata},
                )
        try:
            normalized = self.normalizer.normalize(raw_response)
        except ValueError as error:
            self.store.append_audit(
                event_id=f"{request_id}-response-rejected",
                occurred_at=self.clock(),
                event_kind="MODEL_RESPONSE_REJECTED",
                observation_identity=request_events[0].observation_identity,
                request_id=request_id,
                payload={"raw_response_sha256": response_sha, "error": str(error), "strict_output_enum_enforcement": True},
            )
            raise
        self.store.append_audit(
            event_id=f"{request_id}-response-normalized",
            occurred_at=self.clock(),
            event_kind="MODEL_RESPONSE_NORMALIZED",
            observation_identity=request_events[0].observation_identity,
            request_id=request_id,
            payload={
                "normalized_identity": normalized.identity,
                "response_schema_identity": normalized.response_schema_identity,
                "normalizer_identity": normalized.normalizer_identity,
                "family": normalized.family.value,
                "action": normalized.action.value,
                "direction": normalized.direction.value,
                "attention_mode": normalized.attention_mode.value,
                "source_references": list(normalized.source_references),
                "structured_memory": {
                    "current_market_hypothesis": normalized.current_market_hypothesis,
                    "timeframe_trend_view": [list(item) for item in normalized.timeframe_trend_view],
                    "key_location_hypotheses": list(normalized.key_location_hypotheses),
                    "expected_trigger": normalized.expected_trigger,
                    "invalidation_hypothesis": normalized.invalidation_hypothesis,
                    "open_questions": list(normalized.open_questions),
                },
                "strict_output_enum_enforcement": True,
            },
        )
        return normalized

    def mutate_working_memory(
        self,
        *,
        field_name: str,
        new_value: object,
        reason: str,
        observation_identity: str,
    ) -> None:
        now = self.clock()
        before = self.store.load_working_memory()
        after = before.mutate(
            field_name=field_name,
            new_value=new_value,
            reason=reason,
            timestamp=now,
            observation_identity=observation_identity,
            ai_trader_identity=self.trader_identity.identity,
        )
        memory_sha = self.store.save_working_memory(after, updated_at=now)
        mutation = after.mutation_history[-1]
        self.store.append_audit(
            event_id=f"memory-{uuid4().hex}",
            occurred_at=now,
            event_kind="DS_WORKING_MEMORY_MUTATION",
            observation_identity=observation_identity,
            payload={
                "field_name": mutation.field_name,
                "previous_value": mutation.previous_value,
                "new_value": mutation.new_value,
                "reason": mutation.reason,
                "memory_payload_sha256": memory_sha,
            },
        )

    def append_journal(
        self,
        *,
        entry_id: str,
        body: str,
        observation_identity: str | None = None,
        tags: Iterable[str] = (),
    ) -> str:
        now = self.clock()
        entry = self.store.append_journal(
            entry_id=entry_id,
            created_at=now,
            body=body,
            observation_identity=observation_identity,
            tags=tags,
        )
        self.store.append_audit(
            event_id=f"journal-{uuid4().hex}",
            occurred_at=now,
            event_kind="DS_JOURNAL_APPEND",
            observation_identity=observation_identity,
            payload={"entry_id": entry.entry_id, "identity": entry.identity, "semantic_class": "REFLECTION_NOT_FACT_OR_POLICY"},
        )
        return entry.identity

    def put_hypothesis(
        self,
        *,
        hypothesis_id: str,
        statement: str,
        falsifier: str,
        status: str = "CANDIDATE",
        evidence_references: Iterable[str] = (),
    ) -> str:
        now = self.clock()
        existing = {item.hypothesis_id: item for item in self.store.list_hypotheses(limit=200)}
        created_at = existing[hypothesis_id].created_at if hypothesis_id in existing else now
        hypothesis = self.store.put_hypothesis(
            hypothesis_id=hypothesis_id,
            created_at=created_at,
            updated_at=now,
            statement=statement,
            falsifier=falsifier,
            status=status,
            evidence_references=evidence_references,
        )
        self.store.append_audit(
            event_id=f"hypothesis-{uuid4().hex}",
            occurred_at=now,
            event_kind="DS_HYPOTHESIS_MEMORY_PUT",
            payload={
                "hypothesis_id": hypothesis.hypothesis_id,
                "identity": hypothesis.identity,
                "status": hypothesis.status,
                "executable_policy": False,
            },
        )
        return hypothesis.identity

    def portable_export(self) -> dict[str, Any]:
        return self.store.portable_export()


__all__ = [
    "ACTIVE_TIMEFRAMES",
    "CONTEXT_SCHEMA_VERSION",
    "CURRENT_MODEL",
    "DeepSeekHarnessRuntimeContract",
    "GENERAL_MAX_RETRIES",
    "MODEL_SOURCE",
    "PINNED_HARNESS_COMMIT",
    "PINNED_HARNESS_VERSION",
    "PROJECT_TRANSPORT_PATCH",
    "PersistentDeepSeekTraderPrototype",
    "PreparedModelRequest",
    "ProjectToolRegistry",
    "default_jianghe_canon_paths",
    "observation_to_context_payload",
]

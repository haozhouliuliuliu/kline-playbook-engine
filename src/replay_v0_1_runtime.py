"""Replay V0.1 runtime adapter with frozen trading-only cognition boundaries.

This adapter intentionally removes prompt choice and hypothesis-history mechanics
from the replay caller.  Operational systems remain project-owned; DeepSeek receives
the frozen trading-only prompt contract and causal context assembled by the accepted
prototype runtime.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping
from uuid import uuid4

from src.jianghe_ai_trader import JiangheObservation
from src.jianghe_trading_only_prompt import TRADING_ONLY_PROMPT_CONTRACT
from src.persistent_hypothesis_history import VersionedHypothesisLedger
from src.persistent_deepseek_runtime import PreparedModelRequest


REPLAY_V0_1_RUNTIME_VERSION = "KPE_SMALL_CHRONOLOGICAL_LIFECYCLE_REPLAY_RUNTIME_V0_1"
JOURNAL_WRITE_TRIGGERS = frozenset(
    {
        "MEANINGFUL_STATE_TRANSITION",
        "END_OF_SESSION",
        "RESTART_CHECKPOINT",
        "HYPOTHESIS_FALSIFICATION_OR_RETIREMENT",
    }
)


class ReplayV01Runtime:
    """Frozen V0.1 adapter around the accepted persistent trader prototype."""

    def __init__(self, base_runtime: Any) -> None:
        for name in ("runtime_contract", "trader_identity", "store", "clock"):
            if not hasattr(base_runtime, name):
                raise ValueError(f"base runtime is missing required attribute: {name}")
        contract = base_runtime.runtime_contract
        if contract.system_prompt_sha256 != TRADING_ONLY_PROMPT_CONTRACT.system_prompt_sha256:
            raise ValueError("V0.1 runtime contract must bind the frozen trading-only system prompt")
        if contract.decision_prompt_sha256 != TRADING_ONLY_PROMPT_CONTRACT.decision_prompt_sha256:
            raise ValueError("V0.1 runtime contract must bind the frozen trading-only decision prompt")
        if contract.provider_call_authorized is not False:
            raise ValueError("offline V0.1 adapter must not authorize provider calls")
        self.base_runtime = base_runtime
        self.hypothesis_ledger = VersionedHypothesisLedger(
            base_runtime.store.path,
            trader_identity=base_runtime.trader_identity.identity,
        )

    @property
    def trader_identity(self) -> Any:
        return self.base_runtime.trader_identity

    @property
    def store(self) -> Any:
        return self.base_runtime.store

    def close(self) -> None:
        """Cleanly close the underlying persistent store for restart continuity."""
        self.base_runtime.store.close()

    def prepare_model_request(
        self,
        *,
        observation: JiangheObservation,
        retrieval_query: str,
    ) -> PreparedModelRequest:
        """Prepare exactly the frozen V0.1 prompts; callers cannot mutate them."""
        return self.base_runtime.prepare_model_request(
            observation=observation,
            retrieval_query=retrieval_query,
            system_prompt=TRADING_ONLY_PROMPT_CONTRACT.system_prompt,
            decision_prompt=TRADING_ONLY_PROMPT_CONTRACT.decision_prompt,
        )

    def record_model_response(self, *, request_id: str, raw_response: str) -> Any:
        return self.base_runtime.record_model_response(request_id=request_id, raw_response=raw_response)

    def mutate_working_memory(
        self,
        *,
        field_name: str,
        new_value: object,
        reason: str,
        observation_identity: str,
    ) -> None:
        self.base_runtime.mutate_working_memory(
            field_name=field_name,
            new_value=new_value,
            reason=reason,
            observation_identity=observation_identity,
        )

    def append_journal(
        self,
        *,
        entry_id: str,
        body: str,
        trigger: str,
        observation_identity: str | None = None,
        tags: Iterable[str] = (),
    ) -> str:
        if trigger not in JOURNAL_WRITE_TRIGGERS:
            raise ValueError("V0.1 journal write trigger is not allowed")
        governed_tags = tuple(sorted(set(tags) | {f"V0_1_TRIGGER:{trigger}"}))
        return self.base_runtime.append_journal(
            entry_id=entry_id,
            body=body,
            observation_identity=observation_identity,
            tags=governed_tags,
        )

    def put_hypothesis(
        self,
        *,
        hypothesis_id: str,
        statement: str,
        falsifier: str,
        reason: str,
        status: str = "CANDIDATE",
        evidence_references: Iterable[str] = (),
        observation_identity: str | None = None,
        request_id: str | None = None,
    ) -> str:
        occurred_at = self.base_runtime.clock()
        record, revision = self.hypothesis_ledger.put(
            hypothesis_id=hypothesis_id,
            occurred_at=occurred_at,
            statement=statement,
            falsifier=falsifier,
            status=status,
            evidence_references=evidence_references,
            observation_identity=observation_identity,
            request_id=request_id,
            reason=reason,
        )
        self.base_runtime.store.append_audit(
            event_id=f"hypothesis-revision-{uuid4().hex}",
            occurred_at=occurred_at,
            event_kind="DS_HYPOTHESIS_MEMORY_REVISION",
            observation_identity=observation_identity,
            request_id=request_id,
            payload={
                "hypothesis_id": record.hypothesis_id,
                "hypothesis_identity": record.identity,
                "revision_identity": revision.identity,
                "revision_number": revision.revision_number,
                "reason": revision.reason,
                "before_sha256": revision.before_sha256,
                "after_sha256": revision.after_sha256,
                "status": record.status,
                "executable_policy": False,
            },
        )
        return revision.identity

    def call_tool(
        self,
        name: str,
        arguments: Mapping[str, Any],
        *,
        observation_identity: str | None = None,
        request_id: str | None = None,
    ) -> Mapping[str, Any]:
        return self.base_runtime.tools.call(
            name,
            arguments,
            observation_identity=observation_identity,
            request_id=request_id,
        )

    def portable_export(self) -> dict[str, Any]:
        exported = dict(self.base_runtime.portable_export())
        exported["replay_v0_1_runtime_version"] = REPLAY_V0_1_RUNTIME_VERSION
        exported["model_cognitive_scope"] = TRADING_ONLY_PROMPT_CONTRACT.model_cognitive_scope
        exported["prompt_contract"] = {
            "version": TRADING_ONLY_PROMPT_CONTRACT.version,
            "identity": TRADING_ONLY_PROMPT_CONTRACT.identity,
            "system_prompt_sha256": TRADING_ONLY_PROMPT_CONTRACT.system_prompt_sha256,
            "decision_prompt_sha256": TRADING_ONLY_PROMPT_CONTRACT.decision_prompt_sha256,
        }
        exported["hypothesis_revisions"] = self.hypothesis_ledger.portable_export()
        return exported


__all__ = [
    "JOURNAL_WRITE_TRIGGERS",
    "REPLAY_V0_1_RUNTIME_VERSION",
    "ReplayV01Runtime",
]

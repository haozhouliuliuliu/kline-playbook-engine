"""Crash-resilient single-slot Stage-A live orchestration.

This is the only GitHub-hosted live path.  It persists and verifies a remote
write-ahead reservation before entering the existing provider transport.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable, Mapping, Protocol

from src.jianghe_stage_a_evidence import (
    canonical_json_bytes,
    materialize_stage_a_attempt_evidence,
)
from src.jianghe_stage_a_remote_ledger import RemoteLedgerObservedState
from src.jianghe_stage_a_runner import (
    StageAExecutionJournal,
    StageASlotResult,
    VerifiedFrozenStageAPlan,
    _execute_prepared_frozen_slot,
    _preflight_frozen_slot,
)


class RemoteLedgerStore(Protocol):
    def load(self, plan: VerifiedFrozenStageAPlan) -> RemoteLedgerObservedState: ...

    def compare_and_swap(
        self,
        *,
        expected_head: str | None,
        ledger_bytes: bytes,
        evidence_artifacts: Mapping[str, bytes] | None = None,
    ) -> str: ...


class LiveLaneError(RuntimeError):
    pass


@dataclass(frozen=True)
class LiveLaneResult:
    slot_result: StageASlotResult
    remote_start_head: str
    remote_terminal_head: str
    evidence_identity: str


def execute_remote_reserved_slot(
    *,
    plan: VerifiedFrozenStageAPlan,
    store: RemoteLedgerStore,
    state_dir: Path,
    provider_id: str,
    slot: int,
    now: datetime,
    http_post=None,
    credential_lookup: Callable[[str], str | None],
    after_remote_start: Callable[[], None] | None = None,
) -> LiveLaneResult:
    """Execute one slot; every failure after remote start remains non-retryable."""

    observed = store.load(plan)
    baseline = observed.ledger.snapshot()
    prepared, authorization, credential = _preflight_frozen_slot(
        plan,
        provider_id=provider_id,
        slot=slot,
        now=now,
        snapshot=baseline,
        http_post=http_post,
        credential_lookup=credential_lookup,
    )
    reserved = observed.ledger.append_start(
        now=now,
        provider_id=provider_id,
        slot=slot,
        model_id=prepared.provider_spec.model_id,
        request_identity=str(prepared.slot_row["request_identity"]),
        payload_sha256=str(prepared.slot_row["payload_sha256"]),
        worst_case_cny=prepared.worst_case_cny,
    )
    reserved_bytes = reserved.to_bytes()
    start_head = store.compare_and_swap(
        expected_head=observed.head_sha,
        ledger_bytes=reserved_bytes,
    )
    verified = store.load(plan)
    if verified.head_sha != start_head or verified.ledger.to_bytes() != reserved_bytes:
        raise LiveLaneError("remote start could not be verified byte-for-byte")

    if after_remote_start is not None:
        after_remote_start()

    state = Path(state_dir).resolve()
    journal = StageAExecutionJournal(state / "journal.jsonl", plan)
    result = _execute_prepared_frozen_slot(
        plan,
        journal,
        prepared=prepared,
        authorization=authorization,
        credential=credential,
        baseline_snapshot=baseline,
        now=now,
    )

    evidence_path = state / "attempt-evidence.json"
    artifact = materialize_stage_a_attempt_evidence(
        state_dir=state,
        output_path=evidence_path,
    )
    evidence_identity = str(artifact["artifact_identity"])
    attempts = artifact.get("attempts")
    if (
        artifact.get("plan_identity") != plan.plan_identity
        or not isinstance(attempts, list)
        or len(attempts) != 1
        or attempts[0].get("provider_id") != provider_id
        or attempts[0].get("slot") != slot
    ):
        raise LiveLaneError("secret-guarded evidence does not bind the reserved slot")
    terminal = reserved.append_terminal(
        now=now,
        provider_id=provider_id,
        slot=slot,
        status=result.status,
        accounted_cny=result.accounted_cny,
        evidence_identity=evidence_identity,
        evidence_network_start_event_identity=str(
            attempts[0]["network_start_event_identity"]
        ),
        evidence_terminal_event_identity=str(attempts[0]["terminal_event_identity"]),
    )
    evidence_bytes = canonical_json_bytes(artifact)
    terminal_bytes = terminal.to_bytes()
    terminal_head = store.compare_and_swap(
        expected_head=start_head,
        ledger_bytes=terminal_bytes,
        evidence_artifacts={f"evidence-{evidence_identity}.json": evidence_bytes},
    )
    verified_terminal = store.load(plan)
    if (
        verified_terminal.head_sha != terminal_head
        or verified_terminal.ledger.to_bytes() != terminal_bytes
    ):
        raise LiveLaneError("remote terminal could not be verified byte-for-byte")
    return LiveLaneResult(
        slot_result=result,
        remote_start_head=start_head,
        remote_terminal_head=terminal_head,
        evidence_identity=evidence_identity,
    )


__all__ = ["LiveLaneError", "LiveLaneResult", "execute_remote_reserved_slot"]

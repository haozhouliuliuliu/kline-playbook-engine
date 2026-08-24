"""Persistent single-slot execution guard for Jianghe Stage-A.

This module is the execution boundary immediately in front of the already-audited
StageAProviderTransport. It binds every billable attempt to one exact slot in the
committed frozen plan, persists a hash-chained attempt journal, and prevents an
automatic retry after a network attempt has been durably committed.

The journal is intentionally local runtime state. Durable Stage-A evidence is
materialized/committed separately after calls; credentials are never serialized.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import os
from pathlib import Path
from typing import Callable, Mapping, Sequence

from src.jianghe_prespend_runtime import (
    CnyBudgetLedger,
    HARD_PROJECT_CAP_CNY,
    IMPLEMENTATION_TARGET_SPECS,
    ProviderSpec,
    ProviderUsage,
    load_current_repository_rate_card,
    load_owner_paid_call_authorization,
)
from src.jianghe_response_normalizer import JiangheResponseNormalizer
from src.jianghe_source_only_verification import _repository_blob_bytes
from src.jianghe_stage_a_frozen_stimulus import build_frozen_stage_a_stimulus
from src.jianghe_stage_a_runtime import (
    STAGE_A_MAX_CALLS_PER_PROVIDER,
    STAGE_A_PROVIDER_CAP_CNY,
    STAGE_A_TOTAL_CAP_CNY,
    StageABudgetEnvelope,
    StageAInputRequest,
    StageAInputTrack,
    StageAProviderInvocationEvidence,
    StageAProviderTransport,
    exact_invocation_bounds,
    make_stage_a_request,
)

ROOT = Path(__file__).resolve().parents[1]
FROZEN_PLAN_PATH = ROOT / "docs" / "evidence" / "JIANGHE_STAGE_A_FROZEN_PLAN_V0_2.json"
PROMPT_PACKAGE_PATH = (
    ROOT / "docs" / "research" / "jianghe" / "JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_2.json"
)
DEFAULT_STATE_DIR = ROOT / ".runtime" / "jianghe_stage_a"
JOURNAL_SCHEMA_VERSION = "JIANGHE_STAGE_A_EXECUTION_EVENT_V0_1"
LOCK_SCHEMA_VERSION = "JIANGHE_STAGE_A_EXECUTION_LOCK_V0_1"
NETWORK_ATTEMPT_STARTED = "NETWORK_ATTEMPT_STARTED"
ATTEMPT_TERMINAL = "ATTEMPT_TERMINAL"
TERMINAL_STATUSES = frozenset(
    {
        "SUCCESS_NORMALIZED",
        "NON_SCOREABLE_NORMALIZER",
        "NON_SCOREABLE_PROVIDER_RESPONSE",
        "PROVIDER_MODEL_DRIFT",
        "TRANSPORT_FAILURE",
    }
)
_MAX_TOTAL_STAGE_A_CALLS = len(IMPLEMENTATION_TARGET_SPECS) * STAGE_A_MAX_CALLS_PER_PROVIDER

_EVENT_FIELDS = frozenset(
    {
        "artifact_schema_version",
        "sequence",
        "event_type",
        "recorded_at",
        "prev_event_identity",
        "plan_identity",
        "plan_sha256",
        "provider_id",
        "slot",
        "slot_key",
        "request_identity",
        "payload_sha256",
        "worst_case_cny",
        "start_event_identity",
        "status",
        "accounted_cny",
        "provider_evidence",
        "normalized_decision_identity",
        "error_type",
        "error_message",
        "event_identity",
    }
)


class StageAExecutionError(RuntimeError):
    pass


class FrozenPlanMismatchError(StageAExecutionError):
    pass


class JournalIntegrityError(StageAExecutionError):
    pass


class SlotAlreadyAttemptedError(StageAExecutionError):
    pass


class CredentialUnavailableError(StageAExecutionError):
    pass


class ExecutionLockError(StageAExecutionError):
    pass


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _decimal(value: object, field_name: str) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise StageAExecutionError(f"{field_name} must be a finite Decimal") from None
    if not result.is_finite() or result < 0:
        raise StageAExecutionError(f"{field_name} has invalid Decimal value")
    return result


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _require_aware(value: datetime) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise StageAExecutionError("execution timestamp must be timezone-aware")
    return value


def _iso(value: datetime) -> str:
    return _require_aware(value).astimezone(timezone.utc).isoformat(timespec="microseconds")


def _slot_key(provider_id: str, slot: int) -> str:
    return f"{provider_id}:{slot}"


@dataclass(frozen=True)
class VerifiedFrozenStageAPlan:
    payload: Mapping[str, object]
    raw_bytes: bytes
    sha256: str
    plan_identity: str

    @classmethod
    def load(
        cls, *, committed_path: Path, deterministic_rebuild_bytes: bytes
    ) -> "VerifiedFrozenStageAPlan":
        committed = _repository_blob_bytes(committed_path)
        if committed != deterministic_rebuild_bytes:
            raise FrozenPlanMismatchError(
                "committed Stage-A frozen plan differs from deterministic rebuild"
            )
        try:
            payload = json.loads(committed.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise FrozenPlanMismatchError("frozen plan is not valid UTF-8 JSON") from error
        if not isinstance(payload, Mapping):
            raise FrozenPlanMismatchError("frozen plan must be an object")
        declared_identity = payload.get("plan_identity")
        if not isinstance(declared_identity, str) or len(declared_identity) != 64:
            raise FrozenPlanMismatchError("frozen plan identity is missing")
        identity_payload = dict(payload)
        identity_payload.pop("plan_identity", None)
        if _hash(identity_payload) != declared_identity:
            raise FrozenPlanMismatchError("frozen plan identity does not match its content")
        version = payload.get("artifact_schema_version")
        if version not in {"JIANGHE_STAGE_A_FROZEN_PLAN_V0_1", "JIANGHE_STAGE_A_FROZEN_PLAN_V0_2"}:
            raise FrozenPlanMismatchError("frozen plan version is unsupported")
        expected_top = {
            "artifact_schema_version": version,
            "status": (
                "FROZEN_BEFORE_FIRST_PAID_CALL"
                if version.endswith("V0_1")
                else "FROZEN_V0_2_OFFLINE__REMOTE_BOOTSTRAP_PENDING_AFTER_MERGE"
            ),
            "automatic_retry": "FORBIDDEN",
            "outcome_access": "NO",
            "max_calls_per_provider": STAGE_A_MAX_CALLS_PER_PROVIDER,
        }
        for name, expected in expected_top.items():
            if payload.get(name) != expected:
                raise FrozenPlanMismatchError(f"frozen plan invariant drifted: {name}")
        if _decimal(payload.get("stage_a_total_cap_cny"), "stage_a_total_cap_cny") != STAGE_A_TOTAL_CAP_CNY:
            raise FrozenPlanMismatchError("Stage-A total cap drifted")
        if _decimal(payload.get("stage_a_provider_cap_cny"), "stage_a_provider_cap_cny") != STAGE_A_PROVIDER_CAP_CNY:
            raise FrozenPlanMismatchError("Stage-A provider cap drifted")
        if _decimal(payload.get("project_shared_hard_cap_cny"), "project_shared_hard_cap_cny") != HARD_PROJECT_CAP_CNY:
            raise FrozenPlanMismatchError("shared project hard cap drifted")
        expected_tracks = [
            "OPERATIONAL_PROVIDER",
            "SEMANTIC",
            "VISUAL",
            "STRUCTURED",
            "DUAL_INPUT",
        ]
        if payload.get("track_order") != expected_tracks:
            raise FrozenPlanMismatchError("frozen Stage-A track order drifted")
        providers = payload.get("providers")
        if not isinstance(providers, list) or len(providers) != len(IMPLEMENTATION_TARGET_SPECS):
            raise FrozenPlanMismatchError("frozen plan provider set is malformed")
        if version.endswith("V0_2"):
            carry = payload.get("carry_forward")
            expected_carry = {
                "live_calls": 1,
                "project_accounted_cny": "0.219222",
                "stage_accounted_cny": "0.219222",
                "provider_accounted_cny": {"DEEPSEEK": "0.219222"},
                "provider_attempts": {"DEEPSEEK": 1},
                "attempted_slots": ["DEEPSEEK:1"],
                "attempt_001_evidence_identity": "d36c1fbbb1cd639e48a6f049f7df1be3bb95d9f346d75bbb85e25451fba9dc55",
                "automatic_retry": "FORBIDDEN",
                "replacement_call": "FORBIDDEN",
            }
            if (
                carry != expected_carry
                or payload.get("future_executable_call_count") != 14
                or payload.get("max_total_stage_a_calls") != _MAX_TOTAL_STAGE_A_CALLS
            ):
                raise FrozenPlanMismatchError("V0.2 carry-forward baseline drifted")
        return cls(
            payload=payload,
            raw_bytes=committed,
            sha256=sha256(committed).hexdigest(),
            plan_identity=declared_identity,
        )

    def provider_row(self, provider_id: str) -> Mapping[str, object]:
        providers = self.payload.get("providers")
        if not isinstance(providers, list):
            raise FrozenPlanMismatchError("frozen plan provider list is malformed")
        matches = [
            item
            for item in providers
            if isinstance(item, Mapping) and item.get("provider_id") == provider_id
        ]
        if len(matches) != 1:
            raise FrozenPlanMismatchError("provider must resolve exactly once in frozen plan")
        return matches[0]

    def slot_row(self, provider_id: str, slot: int) -> Mapping[str, object]:
        if not isinstance(slot, int) or isinstance(slot, bool) or not 1 <= slot <= STAGE_A_MAX_CALLS_PER_PROVIDER:
            raise FrozenPlanMismatchError("Stage-A slot must be an integer in 1..5")
        provider = self.provider_row(provider_id)
        rows = provider.get("slots")
        if not isinstance(rows, list):
            raise FrozenPlanMismatchError("provider slots are malformed")
        matches = [row for row in rows if isinstance(row, Mapping) and row.get("slot") == slot]
        if len(matches) != 1:
            raise FrozenPlanMismatchError("slot must resolve exactly once in frozen plan")
        return matches[0]

    def carry_forward_snapshot(self) -> "JournalSnapshot":
        carry = self.payload.get("carry_forward")
        if not isinstance(carry, Mapping):
            return JournalSnapshot(frozenset(), Decimal("0"), Decimal("0"), {}, 0, {})
        return JournalSnapshot(
            attempted_slots=frozenset(str(item) for item in carry["attempted_slots"]),
            project_accounted_cny=_decimal(carry["project_accounted_cny"], "carry.project"),
            stage_accounted_cny=_decimal(carry["stage_accounted_cny"], "carry.stage"),
            provider_accounted_cny={
                str(key): _decimal(value, "carry.provider")
                for key, value in carry["provider_accounted_cny"].items()
            },
            total_attempts=int(carry["live_calls"]),
            provider_attempts={str(key): int(value) for key, value in carry["provider_attempts"].items()},
        )


@dataclass(frozen=True)
class JournalSnapshot:
    attempted_slots: frozenset[str]
    project_accounted_cny: Decimal
    stage_accounted_cny: Decimal
    provider_accounted_cny: Mapping[str, Decimal]
    total_attempts: int
    provider_attempts: Mapping[str, int]


class StageAExecutionJournal:
    def __init__(self, path: Path, plan: VerifiedFrozenStageAPlan) -> None:
        self.path = Path(path)
        self.plan = plan

    def _validated_events_from_bytes(self, raw_bytes: bytes) -> list[dict[str, object]]:
        if not isinstance(raw_bytes, bytes):
            raise TypeError("raw_bytes must be bytes")
        try:
            lines = raw_bytes.decode("utf-8").splitlines()
        except UnicodeDecodeError as error:
            raise JournalIntegrityError("execution journal is not UTF-8") from error
        events: list[dict[str, object]] = []
        previous_identity: str | None = None
        starts: dict[str, dict[str, object]] = {}
        terminals: set[str] = set()
        for index, line in enumerate(lines, start=1):
            if not line.strip():
                raise JournalIntegrityError("execution journal contains an empty record")
            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                raise JournalIntegrityError("execution journal contains invalid JSON") from error
            if not isinstance(event, dict) or frozenset(event) != _EVENT_FIELDS:
                raise JournalIntegrityError("execution journal record schema mismatch")
            if event["artifact_schema_version"] != JOURNAL_SCHEMA_VERSION:
                raise JournalIntegrityError("execution journal schema version mismatch")
            if event["sequence"] != index:
                raise JournalIntegrityError("execution journal sequence is not contiguous")
            if event["prev_event_identity"] != previous_identity:
                raise JournalIntegrityError("execution journal hash chain is broken")
            if event["plan_identity"] != self.plan.plan_identity or event["plan_sha256"] != self.plan.sha256:
                raise JournalIntegrityError("execution journal is bound to a different frozen plan")
            declared = event["event_identity"]
            if not isinstance(declared, str) or len(declared) != 64:
                raise JournalIntegrityError("execution journal event identity is invalid")
            identity_payload = dict(event)
            identity_payload.pop("event_identity", None)
            if _hash(identity_payload) != declared:
                raise JournalIntegrityError("execution journal event identity does not match content")
            provider_id = event["provider_id"]
            slot = event["slot"]
            if not isinstance(provider_id, str) or not isinstance(slot, int):
                raise JournalIntegrityError("execution journal provider/slot is malformed")
            key = _slot_key(provider_id, slot)
            if event["slot_key"] != key:
                raise JournalIntegrityError("execution journal slot key mismatch")
            plan_slot = self.plan.slot_row(provider_id, slot)
            if event["request_identity"] != plan_slot.get("request_identity"):
                raise JournalIntegrityError("journal request identity differs from frozen slot")
            if event["payload_sha256"] != plan_slot.get("payload_sha256"):
                raise JournalIntegrityError("journal payload identity differs from frozen slot")
            if _decimal(event["worst_case_cny"], "journal.worst_case_cny") != _decimal(
                plan_slot.get("worst_case_cny"), "plan.worst_case_cny"
            ):
                raise JournalIntegrityError("journal worst-case cost differs from frozen slot")
            event_type = event["event_type"]
            if event_type == NETWORK_ATTEMPT_STARTED:
                if key in starts:
                    raise JournalIntegrityError("a frozen slot has more than one network-start event")
                if any(
                    event[name] is not None
                    for name in (
                        "start_event_identity",
                        "status",
                        "accounted_cny",
                        "provider_evidence",
                        "normalized_decision_identity",
                        "error_type",
                        "error_message",
                    )
                ):
                    raise JournalIntegrityError("network-start event contains terminal-only fields")
                starts[key] = event
            elif event_type == ATTEMPT_TERMINAL:
                if key not in starts:
                    raise JournalIntegrityError("terminal event has no preceding network-start")
                if key in terminals:
                    raise JournalIntegrityError("a frozen slot has more than one terminal event")
                if event["start_event_identity"] != starts[key]["event_identity"]:
                    raise JournalIntegrityError("terminal event does not bind its network-start")
                if event["status"] not in TERMINAL_STATUSES:
                    raise JournalIntegrityError("terminal event status is unsupported")
                accounted = _decimal(event["accounted_cny"], "terminal.accounted_cny")
                worst = _decimal(starts[key]["worst_case_cny"], "start.worst_case_cny")
                if accounted > worst:
                    raise JournalIntegrityError("terminal accounted cost exceeds frozen worst-case")
                terminals.add(key)
            else:
                raise JournalIntegrityError("execution journal event type is unsupported")
            previous_identity = declared
            events.append(event)
        return events

    def _read_events(self) -> list[dict[str, object]]:
        if not self.path.exists():
            return []
        return self._validated_events_from_bytes(self.path.read_bytes())

    def _snapshot_from_verified_events(
        self, events: Sequence[Mapping[str, object]]
    ) -> JournalSnapshot:
        starts: dict[str, dict[str, object]] = {}
        terminals: dict[str, dict[str, object]] = {}
        provider_attempts: dict[str, int] = {}
        for event in events:
            key = str(event["slot_key"])
            if event["event_type"] == NETWORK_ATTEMPT_STARTED:
                starts[key] = dict(event)
                provider = str(event["provider_id"])
                provider_attempts[provider] = provider_attempts.get(provider, 0) + 1
            else:
                terminals[key] = dict(event)
        baseline = self.plan.carry_forward_snapshot()
        provider_spend: dict[str, Decimal] = dict(baseline.provider_accounted_cny)
        total = baseline.stage_accounted_cny
        for key, start in starts.items():
            terminal = terminals.get(key)
            amount = (
                _decimal(terminal["accounted_cny"], "terminal.accounted_cny")
                if terminal is not None
                else _decimal(start["worst_case_cny"], "start.worst_case_cny")
            )
            provider = str(start["provider_id"])
            provider_spend[provider] = provider_spend.get(provider, Decimal("0")) + amount
            total += amount
        if total > STAGE_A_TOTAL_CAP_CNY or total > HARD_PROJECT_CAP_CNY:
            raise JournalIntegrityError("persisted Stage-A accounting exceeds an authorized cap")
        for provider, amount in provider_spend.items():
            if amount > STAGE_A_PROVIDER_CAP_CNY:
                raise JournalIntegrityError(f"persisted provider accounting exceeds CNY6: {provider}")
        total_attempts = baseline.total_attempts + len(starts)
        combined_provider_attempts = dict(baseline.provider_attempts)
        for provider, count in provider_attempts.items():
            combined_provider_attempts[provider] = combined_provider_attempts.get(provider, 0) + count
        if total_attempts > _MAX_TOTAL_STAGE_A_CALLS:
            raise JournalIntegrityError("persisted attempt count exceeds Stage-A maximum")
        if any(value > STAGE_A_MAX_CALLS_PER_PROVIDER for value in combined_provider_attempts.values()):
            raise JournalIntegrityError("persisted provider attempt count exceeds maximum")
        return JournalSnapshot(
            attempted_slots=frozenset((*baseline.attempted_slots, *starts.keys())),
            project_accounted_cny=total,
            stage_accounted_cny=total,
            provider_accounted_cny=dict(provider_spend),
            total_attempts=total_attempts,
            provider_attempts=combined_provider_attempts,
        )

    def snapshot(self) -> JournalSnapshot:
        return self._snapshot_from_verified_events(self._read_events())

    def verified_state_from_bytes(
        self, raw_bytes: bytes
    ) -> tuple[tuple[Mapping[str, object], ...], JournalSnapshot]:
        """Validate one byte snapshot and derive events/accounting from only that snapshot."""

        events = self._validated_events_from_bytes(raw_bytes)
        verified_events = tuple(dict(event) for event in events)
        return verified_events, self._snapshot_from_verified_events(verified_events)

    def verified_events(self) -> tuple[Mapping[str, object], ...]:
        """Return journal events only after the existing integrity checks pass."""

        return tuple(dict(event) for event in self._read_events())

    def _append(self, event: dict[str, object]) -> dict[str, object]:
        existing = self._read_events()
        event["sequence"] = len(existing) + 1
        event["prev_event_identity"] = None if not existing else existing[-1]["event_identity"]
        event["event_identity"] = None
        identity_payload = dict(event)
        identity_payload.pop("event_identity", None)
        event["event_identity"] = _hash(identity_payload)
        if frozenset(event) != _EVENT_FIELDS:
            raise JournalIntegrityError("internal journal record schema mismatch")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        line = _canonical_json(event) + "\n"
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        return event

    def append_network_start(
        self,
        *,
        now: datetime,
        provider_id: str,
        slot: int,
        request_identity: str,
        payload_sha256: str,
        worst_case_cny: Decimal,
    ) -> dict[str, object]:
        key = _slot_key(provider_id, slot)
        if key in self.snapshot().attempted_slots:
            raise SlotAlreadyAttemptedError("frozen Stage-A slot has already started a network attempt")
        return self._append(
            {
                "artifact_schema_version": JOURNAL_SCHEMA_VERSION,
                "sequence": 0,
                "event_type": NETWORK_ATTEMPT_STARTED,
                "recorded_at": _iso(now),
                "prev_event_identity": None,
                "plan_identity": self.plan.plan_identity,
                "plan_sha256": self.plan.sha256,
                "provider_id": provider_id,
                "slot": slot,
                "slot_key": key,
                "request_identity": request_identity,
                "payload_sha256": payload_sha256,
                "worst_case_cny": _decimal_text(worst_case_cny),
                "start_event_identity": None,
                "status": None,
                "accounted_cny": None,
                "provider_evidence": None,
                "normalized_decision_identity": None,
                "error_type": None,
                "error_message": None,
                "event_identity": None,
            }
        )

    def append_terminal(
        self,
        *,
        now: datetime,
        start_event: Mapping[str, object],
        status: str,
        accounted_cny: Decimal,
        provider_evidence: Mapping[str, object] | None,
        normalized_decision_identity: str | None,
        error_type: str | None,
        error_message: str | None,
    ) -> dict[str, object]:
        if status not in TERMINAL_STATUSES:
            raise StageAExecutionError("unsupported terminal status")
        return self._append(
            {
                "artifact_schema_version": JOURNAL_SCHEMA_VERSION,
                "sequence": 0,
                "event_type": ATTEMPT_TERMINAL,
                "recorded_at": _iso(now),
                "prev_event_identity": None,
                "plan_identity": self.plan.plan_identity,
                "plan_sha256": self.plan.sha256,
                "provider_id": start_event["provider_id"],
                "slot": start_event["slot"],
                "slot_key": start_event["slot_key"],
                "request_identity": start_event["request_identity"],
                "payload_sha256": start_event["payload_sha256"],
                "worst_case_cny": start_event["worst_case_cny"],
                "start_event_identity": start_event["event_identity"],
                "status": status,
                "accounted_cny": _decimal_text(accounted_cny),
                "provider_evidence": provider_evidence,
                "normalized_decision_identity": normalized_decision_identity,
                "error_type": error_type,
                "error_message": error_message,
                "event_identity": None,
            }
        )


class StageAExecutionLock:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._fd: int | None = None

    def __enter__(self) -> "StageAExecutionLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self._fd = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError as error:
            raise ExecutionLockError(
                "Stage-A execution lock already exists; stale locks require manual inspection"
            ) from error
        payload = _canonical_json(
            {"artifact_schema_version": LOCK_SCHEMA_VERSION, "pid": os.getpid()}
        ).encode("utf-8")
        os.write(self._fd, payload)
        os.fsync(self._fd)
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._fd is not None:
            os.close(self._fd)
            self._fd = None
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass


@dataclass(frozen=True)
class PreparedFrozenSlot:
    provider_spec: ProviderSpec
    provider_row: Mapping[str, object]
    slot_row: Mapping[str, object]
    request: StageAInputRequest
    transport: StageAProviderTransport
    rate_card: object
    bounds: object
    payload_bytes: bytes
    worst_case_cny: Decimal


@dataclass(frozen=True)
class StageASlotResult:
    provider_id: str
    slot: int
    status: str
    accounted_cny: Decimal
    provider_evidence_identity: str | None
    normalized_decision_identity: str | None
    terminal_event_identity: str


def _find_provider_spec(provider_id: str) -> ProviderSpec:
    matches = [spec for spec in IMPLEMENTATION_TARGET_SPECS if spec.provider_id == provider_id]
    if len(matches) != 1:
        raise FrozenPlanMismatchError("provider is not in the authorized implementation target set")
    return matches[0]


def _prompt_strings(plan: VerifiedFrozenStageAPlan) -> tuple[str, str]:
    prompt_path = (
        ROOT / "docs/research/jianghe/JIANGHE_LIVE_FIDELITY_PROMPT_PACKAGE_V0_1.json"
        if plan.payload.get("artifact_schema_version") == "JIANGHE_STAGE_A_FROZEN_PLAN_V0_1"
        else PROMPT_PACKAGE_PATH
    )
    blob = _repository_blob_bytes(prompt_path)
    if sha256(blob).hexdigest() != plan.payload.get("prompt_package_blob_sha256"):
        raise FrozenPlanMismatchError("prompt package bytes differ from the frozen plan")
    try:
        package = json.loads(blob.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise FrozenPlanMismatchError("prompt package is malformed") from error
    if not isinstance(package, Mapping):
        raise FrozenPlanMismatchError("prompt package must be an object")
    system_prompt = package.get("system_prompt")
    decision_prompt = package.get("decision_prompt")
    if not isinstance(system_prompt, str) or not system_prompt:
        raise FrozenPlanMismatchError("system prompt is missing")
    if not isinstance(decision_prompt, str) or not decision_prompt:
        raise FrozenPlanMismatchError("decision prompt is missing")
    return system_prompt, decision_prompt


def _verify_stimulus(plan: VerifiedFrozenStageAPlan, stimulus) -> None:
    row = plan.payload.get("stimulus")
    if not isinstance(row, Mapping):
        raise FrozenPlanMismatchError("frozen plan stimulus section is malformed")
    expected = {
        "stimulus_identity": stimulus.identity,
        "observation_identity": stimulus.observation.identity.identity,
        "structured_observation_identity": stimulus.structured.identity,
        "visual_input_identity": stimulus.visual.identity,
        "png_sha256": stimulus.png_sha256,
        "recipe_identity": stimulus.recipe_identity,
        "renderer_config_identity": stimulus.renderer_config_identity,
        "renderer_input_identity": stimulus.renderer_input_identity,
        "renderer_visual_artifact_identity": stimulus.visual_artifact_identity,
    }
    for name, value in expected.items():
        if row.get(name) != value:
            raise FrozenPlanMismatchError(f"frozen stimulus identity mismatch: {name}")
    bars = [bar for bar in stimulus.observation.bars if bar.timeframe == "5m"]
    if row.get("fine_5m_bar_count") != len(bars) or len(bars) != 36:
        raise FrozenPlanMismatchError("frozen 5m bar count mismatch")


def _bounds_payload(bounds) -> dict[str, int]:
    return {
        "max_text_input_tokens": bounds.max_text_input_tokens,
        "max_image_tokens": bounds.max_image_tokens,
        "max_output_tokens": bounds.max_output_tokens,
        "transport_retries": bounds.transport_retries,
    }


def prepare_frozen_slot(
    plan: VerifiedFrozenStageAPlan,
    *,
    provider_id: str,
    slot: int,
    now: datetime,
    http_post=None,
) -> PreparedFrozenSlot:
    _require_aware(now)
    spec = _find_provider_spec(provider_id)
    provider_row = plan.provider_row(provider_id)
    if provider_row.get("model_id") != spec.model_id:
        raise FrozenPlanMismatchError("frozen provider model differs from runtime spec")
    if provider_row.get("provider_spec_identity") != spec.identity:
        raise FrozenPlanMismatchError("frozen provider spec identity differs from runtime")
    if provider_row.get("endpoint") != spec.endpoint or provider_row.get("payload_style") != spec.payload_style:
        raise FrozenPlanMismatchError("frozen provider transport metadata drifted")
    slot_row = plan.slot_row(provider_id, slot)
    if slot_row.get("future_executable") is False:
        raise SlotAlreadyAttemptedError("CARRY_FORWARD_ATTEMPTED__NON_RETRYABLE")
    try:
        track = StageAInputTrack(str(slot_row.get("track")))
    except ValueError as error:
        raise FrozenPlanMismatchError("frozen slot track is unsupported") from error
    system_prompt, decision_prompt = _prompt_strings(plan)
    stimulus = build_frozen_stage_a_stimulus()
    _verify_stimulus(plan, stimulus)
    max_output = plan.payload.get("max_output_tokens_per_call")
    if not isinstance(max_output, int) or isinstance(max_output, bool):
        raise FrozenPlanMismatchError("frozen output-token cap is malformed")
    request = make_stage_a_request(
        track,
        system_prompt=system_prompt,
        decision_prompt=decision_prompt,
        max_output_tokens=max_output,
        stimulus=stimulus,
        contract_version=(
            "JIANGHE_STAGE_A_REQUEST_V0_1"
            if plan.payload.get("artifact_schema_version") == "JIANGHE_STAGE_A_FROZEN_PLAN_V0_1"
            else "JIANGHE_STAGE_A_REQUEST_V0_2"
        ),
    )
    transport = (
        StageAProviderTransport(spec, http_post=http_post)
        if http_post is not None
        else StageAProviderTransport(spec)
    )
    rate_card = load_current_repository_rate_card(spec, now=now)
    if provider_row.get("rate_card_identity") != rate_card.identity:
        raise FrozenPlanMismatchError("current rate-card identity differs from frozen plan")
    payload_bytes = transport.payload_bytes(request)
    bounds = exact_invocation_bounds(transport, request, rate_card=rate_card)
    worst_case = StageAProviderTransport._worst_case_cny(rate_card, bounds)
    expected = {
        "request_identity": request.identity,
        "payload_sha256": sha256(payload_bytes).hexdigest(),
        "transmitted_structured_observation_identity": request.transmitted_structured_identity,
        "transmitted_visual_identities": [item.identity for item in request.visuals],
        "bounds": _bounds_payload(bounds),
    }
    for name, value in expected.items():
        if slot_row.get(name) != value:
            raise FrozenPlanMismatchError(f"runtime request differs from frozen slot: {name}")
    if _decimal(slot_row.get("worst_case_cny"), "slot.worst_case_cny") != worst_case:
        raise FrozenPlanMismatchError("runtime worst-case cost differs from frozen slot")
    return PreparedFrozenSlot(
        provider_spec=spec,
        provider_row=provider_row,
        slot_row=slot_row,
        request=request,
        transport=transport,
        rate_card=rate_card,
        bounds=bounds,
        payload_bytes=payload_bytes,
        worst_case_cny=worst_case,
    )


def enforce_persistent_caps(
    snapshot: JournalSnapshot, *, provider_id: str, worst_case_cny: Decimal
) -> None:
    worst = _decimal(worst_case_cny, "worst_case_cny")
    if worst <= 0:
        raise StageAExecutionError("frozen slot worst-case cost must be positive")
    if snapshot.total_attempts >= _MAX_TOTAL_STAGE_A_CALLS:
        raise StageAExecutionError("Stage-A total attempt limit has been reached")
    if snapshot.provider_attempts.get(provider_id, 0) >= STAGE_A_MAX_CALLS_PER_PROVIDER:
        raise StageAExecutionError("Stage-A provider attempt limit has been reached")
    if snapshot.project_accounted_cny + worst > HARD_PROJECT_CAP_CNY:
        raise StageAExecutionError("shared CNY100 project cap would be exceeded")
    if snapshot.stage_accounted_cny + worst > STAGE_A_TOTAL_CAP_CNY:
        raise StageAExecutionError("Stage-A CNY18 cap would be exceeded")
    if snapshot.provider_accounted_cny.get(provider_id, Decimal("0")) + worst > STAGE_A_PROVIDER_CAP_CNY:
        raise StageAExecutionError("Stage-A per-provider CNY6 cap would be exceeded")


def _provider_evidence_payload(
    evidence: StageAProviderInvocationEvidence,
) -> dict[str, object]:
    payload = {
        "identity": evidence.identity,
        "input_track": evidence.input_track.value,
        "request_identity": evidence.request_identity,
        "source_observation_identity": evidence.source_observation_identity,
        "selected_context_identity": evidence.selected_context_identity,
        "context_selection_policy_identity": evidence.context_selection_policy_identity,
        "local_structured_observation_identity": evidence.local_structured_observation_identity,
        "transmitted_structured_observation_identity": evidence.transmitted_structured_observation_identity,
        "transmitted_visual_identities": list(evidence.transmitted_visual_identities),
        "provider_spec_identity": evidence.provider_spec_identity,
        "requested_model_id": evidence.requested_model_id,
        "resolved_model_id": evidence.resolved_model_id,
        "provider_request_id": evidence.provider_request_id,
        "latency_ms": evidence.latency_ms,
        "rate_card_identity": evidence.rate_card_identity,
        "budget_reservation_id": evidence.budget_reservation_id,
        "charged_cny": evidence.charged_cny,
        **evidence.safe_payload(),
    }
    return payload


def _safe_error_message(error: BaseException, credential: str | None) -> str:
    text = str(error)
    if credential:
        text = text.replace(credential, "<REDACTED>")
    return text[:500]


def _preflight_frozen_slot(
    plan: VerifiedFrozenStageAPlan,
    *,
    provider_id: str,
    slot: int,
    now: datetime,
    snapshot: JournalSnapshot,
    http_post=None,
    credential_lookup: Callable[[str], str | None] = os.environ.get,
) -> tuple[PreparedFrozenSlot, object, str]:
    prepared = prepare_frozen_slot(
        plan, provider_id=provider_id, slot=slot, now=now, http_post=http_post
    )
    key = _slot_key(provider_id, slot)
    if key in snapshot.attempted_slots:
        raise SlotAlreadyAttemptedError("frozen Stage-A slot has already been attempted")
    enforce_persistent_caps(
        snapshot, provider_id=provider_id, worst_case_cny=prepared.worst_case_cny
    )
    authorization = load_owner_paid_call_authorization(now=now)
    if not authorization.permits(prepared.provider_spec):
        raise StageAExecutionError(
            "current Owner authorization does not permit this frozen provider/model"
        )
    if authorization.hard_cap_cny != HARD_PROJECT_CAP_CNY:
        raise StageAExecutionError("current Owner authorization hard cap is not CNY100")
    credential = credential_lookup(prepared.provider_spec.api_key_env)
    if not isinstance(credential, str) or not credential:
        raise CredentialUnavailableError(
            f"credential is unavailable for {prepared.provider_spec.provider_id}"
        )
    return prepared, authorization, credential


def _execute_prepared_frozen_slot(
    plan: VerifiedFrozenStageAPlan,
    journal: StageAExecutionJournal,
    *,
    prepared: PreparedFrozenSlot,
    authorization: object,
    credential: str,
    baseline_snapshot: JournalSnapshot,
    now: datetime,
) -> StageASlotResult:
    provider_id = prepared.provider_spec.provider_id
    slot = int(prepared.slot_row["slot"])

    stage_budget = StageABudgetEnvelope(
        spent_cny=baseline_snapshot.stage_accounted_cny,
        provider_spent_cny=dict(baseline_snapshot.provider_accounted_cny),
    )
    # One slot per process. Persistent cumulative accounting is enforced above;
    # the audited in-memory CNY100 ledger still guards this individual call.
    project_budget = CnyBudgetLedger()
    start_event = journal.append_network_start(
        now=now,
        provider_id=provider_id,
        slot=slot,
        request_identity=str(prepared.slot_row["request_identity"]),
        payload_sha256=str(prepared.slot_row["payload_sha256"]),
        worst_case_cny=prepared.worst_case_cny,
    )

    status: str
    accounted: Decimal
    provider_payload: dict[str, object] | None = None
    normalized_identity: str | None = None
    error_type: str | None = None
    error_message: str | None = None

    try:
        evidence = prepared.transport.invoke_stage_a(
            prepared.request,
            authorization=authorization,
            budget=project_budget,
            stage_budget=stage_budget,
            bounds=prepared.bounds,
            now=now,
        )
    except Exception as error:  # terminalize every post-start failure; never auto-retry
        status = "TRANSPORT_FAILURE"
        accounted = prepared.worst_case_cny
        error_type = type(error).__name__
        error_message = _safe_error_message(error, credential)
    else:
        provider_payload = _provider_evidence_payload(evidence)
        if (
            isinstance(evidence.resolved_model_id, str)
            and evidence.resolved_model_id
            and evidence.resolved_model_id != prepared.provider_spec.model_id
        ):
            status = "PROVIDER_MODEL_DRIFT"
            accounted = prepared.worst_case_cny
            error_type = "ProviderResolvedModelMismatch"
            error_message = "provider-resolved model differs from frozen authorized model"
        elif not evidence.provider_response_scoreable:
            status = "NON_SCOREABLE_PROVIDER_RESPONSE"
            accounted = prepared.worst_case_cny if evidence.usage is None else _decimal(
                evidence.charged_cny, "evidence.charged_cny"
            )
            error_type = "ProviderFinalContentUnusable"
            error_message = f"final_content_state={evidence.final_content_state}"
        else:
            actual = _decimal(evidence.charged_cny, "evidence.charged_cny")
            if actual > prepared.worst_case_cny:
                status = "TRANSPORT_FAILURE"
                accounted = prepared.worst_case_cny
                error_type = "ChargedCostExceedsFrozenWorstCase"
                error_message = "provider evidence charge exceeds frozen slot reservation"
            else:
                accounted = actual
                try:
                    normalized = JiangheResponseNormalizer().normalize(
                        evidence.raw_response_text
                    )
                except Exception as error:
                    status = "NON_SCOREABLE_NORMALIZER"
                    error_type = type(error).__name__
                    error_message = _safe_error_message(error, credential)
                else:
                    status = "SUCCESS_NORMALIZED"
                    normalized_identity = normalized.identity

    terminal = journal.append_terminal(
        now=now,
        start_event=start_event,
        status=status,
        accounted_cny=accounted,
        provider_evidence=provider_payload,
        normalized_decision_identity=normalized_identity,
        error_type=error_type,
        error_message=error_message,
    )
    return StageASlotResult(
        provider_id=provider_id,
        slot=slot,
        status=status,
        accounted_cny=accounted,
        provider_evidence_identity=(
            None if provider_payload is None else str(provider_payload["identity"])
        ),
        normalized_decision_identity=normalized_identity,
        terminal_event_identity=str(terminal["event_identity"]),
    )


def execute_frozen_slot(
    plan: VerifiedFrozenStageAPlan,
    journal: StageAExecutionJournal,
    *,
    provider_id: str,
    slot: int,
    now: datetime,
    http_post=None,
    credential_lookup: Callable[[str], str | None] = os.environ.get,
) -> StageASlotResult:
    snapshot = journal.snapshot()
    prepared, authorization, credential = _preflight_frozen_slot(
        plan,
        provider_id=provider_id,
        slot=slot,
        now=now,
        snapshot=snapshot,
        http_post=http_post,
        credential_lookup=credential_lookup,
    )
    return _execute_prepared_frozen_slot(
        plan,
        journal,
        prepared=prepared,
        authorization=authorization,
        credential=credential,
        baseline_snapshot=snapshot,
        now=now,
    )


__all__ = [
    "ATTEMPT_TERMINAL",
    "CredentialUnavailableError",
    "DEFAULT_STATE_DIR",
    "ExecutionLockError",
    "FROZEN_PLAN_PATH",
    "FrozenPlanMismatchError",
    "JournalIntegrityError",
    "JournalSnapshot",
    "NETWORK_ATTEMPT_STARTED",
    "PreparedFrozenSlot",
    "SlotAlreadyAttemptedError",
    "StageAExecutionError",
    "StageAExecutionJournal",
    "StageAExecutionLock",
    "StageASlotResult",
    "VerifiedFrozenStageAPlan",
    "enforce_persistent_caps",
    "execute_frozen_slot",
    "prepare_frozen_slot",
]

"""Secret-free, repository-native Stage-A remote execution ledger.

The dedicated Git ref is a write-ahead safety boundary.  A normal non-force
push is the compare-and-swap operation: a stale parent cannot advance the ref.
Provider transport must remain downstream of a successful write and byte-exact
remote re-read.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Mapping, Sequence

from src.jianghe_prespend_runtime import HARD_PROJECT_CAP_CNY
from src.jianghe_stage_a_evidence import (
    StageAEvidenceError,
    validate_stage_a_attempt_evidence_bytes,
)
from src.jianghe_stage_a_runner import (
    ATTEMPT_TERMINAL,
    NETWORK_ATTEMPT_STARTED,
    JournalSnapshot,
    VerifiedFrozenStageAPlan,
)
from src.jianghe_stage_a_runtime import (
    STAGE_A_MAX_CALLS_PER_PROVIDER,
    STAGE_A_PROVIDER_CAP_CNY,
    STAGE_A_TOTAL_CAP_CNY,
)

LEDGER_SCHEMA_VERSION = "JIANGHE_STAGE_A_REMOTE_EXECUTION_LEDGER_V0_1"
LEDGER_EVENT_SCHEMA_VERSION = "JIANGHE_STAGE_A_REMOTE_EXECUTION_EVENT_V0_1"
DEFAULT_REMOTE_REF = "refs/heads/stage-a-live-state-v0-1"
LEDGER_FILENAME = "stage-a-live-ledger-v0-1.json"
REMOTE_TERMINAL_STATUSES = frozenset(
    {
        "SUCCESS_NORMALIZED",
        "NON_SCOREABLE_NORMALIZER",
        "PROVIDER_MODEL_DRIFT",
        "TRANSPORT_FAILURE",
    }
)
_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_GIT_OID = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
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
        "model_id",
        "slot",
        "slot_key",
        "request_identity",
        "payload_sha256",
        "worst_case_cny",
        "start_event_identity",
        "status",
        "accounted_cny",
        "evidence_identity",
        "evidence_network_start_event_identity",
        "evidence_terminal_event_identity",
        "event_identity",
    }
)


class RemoteLedgerError(RuntimeError):
    pass


class RemoteLedgerIntegrityError(RemoteLedgerError):
    pass


class RemoteLedgerUnavailableError(RemoteLedgerError):
    pass


class RemoteLedgerConflictError(RemoteLedgerError):
    pass


class RemoteLedgerVerificationError(RemoteLedgerError):
    pass


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _identity(value: object) -> str:
    return sha256(_canonical_bytes(value).rstrip(b"\n")).hexdigest()


def _decimal(value: object, name: str) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise RemoteLedgerIntegrityError(f"{name} must be a finite Decimal") from None
    if not result.is_finite() or result < 0:
        raise RemoteLedgerIntegrityError(f"{name} must be non-negative and finite")
    return result


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _iso(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise RemoteLedgerError("remote ledger timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _validate_sha(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise RemoteLedgerIntegrityError(f"{name} must be a lowercase SHA-256")
    return value


@dataclass(frozen=True)
class RemoteLedgerObservedState:
    head_sha: str | None
    ledger: "RemoteExecutionLedger"


class RemoteExecutionLedger:
    def __init__(
        self, plan: VerifiedFrozenStageAPlan, events: Sequence[Mapping[str, object]] = ()
    ) -> None:
        self.plan = plan
        self.events = tuple(dict(event) for event in events)
        self._validate_events()

    @classmethod
    def empty(cls, plan: VerifiedFrozenStageAPlan) -> "RemoteExecutionLedger":
        return cls(plan)

    @classmethod
    def from_bytes(
        cls, plan: VerifiedFrozenStageAPlan, raw_bytes: bytes
    ) -> "RemoteExecutionLedger":
        try:
            payload = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise RemoteLedgerIntegrityError("remote ledger is not valid UTF-8 JSON") from error
        if not isinstance(payload, dict) or frozenset(payload) != frozenset(
            {
                "artifact_schema_version",
                "ledger_identity",
                "plan_identity",
                "plan_sha256",
                "events",
            }
        ):
            raise RemoteLedgerIntegrityError("remote ledger top-level schema mismatch")
        if payload["artifact_schema_version"] != LEDGER_SCHEMA_VERSION:
            raise RemoteLedgerIntegrityError("remote ledger schema version mismatch")
        if payload["plan_identity"] != plan.plan_identity or payload["plan_sha256"] != plan.sha256:
            raise RemoteLedgerIntegrityError("remote ledger is bound to a different frozen plan")
        events = payload["events"]
        if not isinstance(events, list):
            raise RemoteLedgerIntegrityError("remote ledger events must be a list")
        identity_payload = dict(payload)
        declared = identity_payload.pop("ledger_identity")
        if _validate_sha(declared, "ledger_identity") != _identity(identity_payload):
            raise RemoteLedgerIntegrityError("remote ledger identity does not match content")
        return cls(plan, events)

    def payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "artifact_schema_version": LEDGER_SCHEMA_VERSION,
            "ledger_identity": None,
            "plan_identity": self.plan.plan_identity,
            "plan_sha256": self.plan.sha256,
            "events": [dict(event) for event in self.events],
        }
        identity_payload = dict(payload)
        identity_payload.pop("ledger_identity")
        payload["ledger_identity"] = _identity(identity_payload)
        return payload

    def to_bytes(self) -> bytes:
        return _canonical_bytes(self.payload())

    def _validate_events(self) -> None:
        starts: dict[str, Mapping[str, object]] = {}
        terminals: set[str] = set()
        evidence_identities: set[str] = set()
        previous: str | None = None
        for sequence, event in enumerate(self.events, start=1):
            if frozenset(event) != _EVENT_FIELDS:
                raise RemoteLedgerIntegrityError("remote ledger event schema mismatch")
            if event["artifact_schema_version"] != LEDGER_EVENT_SCHEMA_VERSION:
                raise RemoteLedgerIntegrityError("remote ledger event version mismatch")
            if event["sequence"] != sequence or event["prev_event_identity"] != previous:
                raise RemoteLedgerIntegrityError("remote ledger sequence/hash chain is broken")
            try:
                recorded_at = datetime.fromisoformat(str(event["recorded_at"]))
            except ValueError as error:
                raise RemoteLedgerIntegrityError("remote event timestamp is malformed") from error
            if recorded_at.tzinfo is None or recorded_at.utcoffset() is None:
                raise RemoteLedgerIntegrityError("remote event timestamp must be timezone-aware")
            declared = _validate_sha(event["event_identity"], "event_identity")
            identity_payload = dict(event)
            identity_payload.pop("event_identity")
            if declared != _identity(identity_payload):
                raise RemoteLedgerIntegrityError("remote event identity does not match content")
            if event["plan_identity"] != self.plan.plan_identity or event["plan_sha256"] != self.plan.sha256:
                raise RemoteLedgerIntegrityError("remote event frozen-plan binding mismatch")
            provider = event["provider_id"]
            slot = event["slot"]
            if not isinstance(provider, str) or not isinstance(slot, int) or isinstance(slot, bool):
                raise RemoteLedgerIntegrityError("remote event provider/slot is malformed")
            key = f"{provider}:{slot}"
            if event["slot_key"] != key:
                raise RemoteLedgerIntegrityError("remote event slot key mismatch")
            provider_row = self.plan.provider_row(provider)
            slot_row = self.plan.slot_row(provider, slot)
            expected = {
                "model_id": provider_row.get("model_id"),
                "request_identity": slot_row.get("request_identity"),
                "payload_sha256": slot_row.get("payload_sha256"),
            }
            for name, value in expected.items():
                if event[name] != value:
                    raise RemoteLedgerIntegrityError(f"remote event frozen {name} binding mismatch")
            if _decimal(event["worst_case_cny"], "worst_case_cny") != _decimal(
                slot_row.get("worst_case_cny"), "frozen worst_case_cny"
            ):
                raise RemoteLedgerIntegrityError("remote event worst-case binding mismatch")
            if event["event_type"] == NETWORK_ATTEMPT_STARTED:
                if key in starts:
                    raise RemoteLedgerIntegrityError("remote slot has duplicate start")
                if any(
                    event[name] is not None
                    for name in (
                        "start_event_identity",
                        "status",
                        "accounted_cny",
                        "evidence_identity",
                        "evidence_network_start_event_identity",
                        "evidence_terminal_event_identity",
                    )
                ):
                    raise RemoteLedgerIntegrityError("remote start contains terminal fields")
                starts[key] = event
            elif event["event_type"] == ATTEMPT_TERMINAL:
                if key not in starts or key in terminals:
                    raise RemoteLedgerIntegrityError("remote terminal has no unique start")
                if event["start_event_identity"] != starts[key]["event_identity"]:
                    raise RemoteLedgerIntegrityError("remote terminal does not bind its start")
                if event["status"] not in REMOTE_TERMINAL_STATUSES:
                    raise RemoteLedgerIntegrityError("remote terminal status is unsupported")
                evidence_identity = _validate_sha(
                    event["evidence_identity"], "evidence_identity"
                )
                _validate_sha(
                    event["evidence_network_start_event_identity"],
                    "evidence_network_start_event_identity",
                )
                _validate_sha(
                    event["evidence_terminal_event_identity"],
                    "evidence_terminal_event_identity",
                )
                if evidence_identity in evidence_identities:
                    raise RemoteLedgerIntegrityError(
                        "remote terminals cannot share an evidence identity"
                    )
                evidence_identities.add(evidence_identity)
                if _decimal(event["accounted_cny"], "accounted_cny") > _decimal(
                    event["worst_case_cny"], "worst_case_cny"
                ):
                    raise RemoteLedgerIntegrityError("remote terminal exceeds reserved cost")
                terminals.add(key)
            else:
                raise RemoteLedgerIntegrityError("remote event type is unsupported")
            previous = declared
        self.snapshot()

    def snapshot(self) -> JournalSnapshot:
        starts: dict[str, Mapping[str, object]] = {}
        terminals: dict[str, Mapping[str, object]] = {}
        provider_attempts: dict[str, int] = {}
        for event in self.events:
            key = str(event["slot_key"])
            if event["event_type"] == NETWORK_ATTEMPT_STARTED:
                starts[key] = event
                provider = str(event["provider_id"])
                provider_attempts[provider] = provider_attempts.get(provider, 0) + 1
            else:
                terminals[key] = event
        provider_spend: dict[str, Decimal] = {}
        total = Decimal("0")
        for key, start in starts.items():
            terminal = terminals.get(key)
            amount = _decimal(
                start["worst_case_cny"] if terminal is None else terminal["accounted_cny"],
                "remote accounted cost",
            )
            provider = str(start["provider_id"])
            provider_spend[provider] = provider_spend.get(provider, Decimal("0")) + amount
            total += amount
        if total > STAGE_A_TOTAL_CAP_CNY or total > HARD_PROJECT_CAP_CNY:
            raise RemoteLedgerIntegrityError("remote accounting exceeds an authorized cap")
        if any(amount > STAGE_A_PROVIDER_CAP_CNY for amount in provider_spend.values()):
            raise RemoteLedgerIntegrityError("remote provider accounting exceeds CNY6")
        if len(starts) > 15 or any(
            count > STAGE_A_MAX_CALLS_PER_PROVIDER for count in provider_attempts.values()
        ):
            raise RemoteLedgerIntegrityError("remote attempt count exceeds Stage-A limits")
        return JournalSnapshot(
            attempted_slots=frozenset(starts),
            project_accounted_cny=total,
            stage_accounted_cny=total,
            provider_accounted_cny=provider_spend,
            total_attempts=len(starts),
            provider_attempts=provider_attempts,
        )

    def append_start(
        self,
        *,
        now: datetime,
        provider_id: str,
        slot: int,
        model_id: str,
        request_identity: str,
        payload_sha256: str,
        worst_case_cny: Decimal,
    ) -> "RemoteExecutionLedger":
        key = f"{provider_id}:{slot}"
        if key in self.snapshot().attempted_slots:
            raise RemoteLedgerConflictError("remote frozen slot has already been attempted")
        event = self._new_event(
            now=now,
            event_type=NETWORK_ATTEMPT_STARTED,
            provider_id=provider_id,
            model_id=model_id,
            slot=slot,
            request_identity=request_identity,
            payload_sha256=payload_sha256,
            worst_case_cny=worst_case_cny,
            start_event_identity=None,
            status=None,
            accounted_cny=None,
            evidence_identity=None,
            evidence_network_start_event_identity=None,
            evidence_terminal_event_identity=None,
        )
        return RemoteExecutionLedger(self.plan, (*self.events, event))

    def append_terminal(
        self,
        *,
        now: datetime,
        provider_id: str,
        slot: int,
        status: str,
        accounted_cny: Decimal,
        evidence_identity: str,
        evidence_network_start_event_identity: str,
        evidence_terminal_event_identity: str,
    ) -> "RemoteExecutionLedger":
        key = f"{provider_id}:{slot}"
        starts = [e for e in self.events if e["slot_key"] == key and e["event_type"] == NETWORK_ATTEMPT_STARTED]
        terminals = [e for e in self.events if e["slot_key"] == key and e["event_type"] == ATTEMPT_TERMINAL]
        if len(starts) != 1 or terminals:
            raise RemoteLedgerConflictError("remote slot cannot accept a terminal")
        start = starts[0]
        event = self._new_event(
            now=now,
            event_type=ATTEMPT_TERMINAL,
            provider_id=provider_id,
            model_id=str(start["model_id"]),
            slot=slot,
            request_identity=str(start["request_identity"]),
            payload_sha256=str(start["payload_sha256"]),
            worst_case_cny=_decimal(start["worst_case_cny"], "worst_case_cny"),
            start_event_identity=str(start["event_identity"]),
            status=status,
            accounted_cny=accounted_cny,
            evidence_identity=evidence_identity,
            evidence_network_start_event_identity=evidence_network_start_event_identity,
            evidence_terminal_event_identity=evidence_terminal_event_identity,
        )
        return RemoteExecutionLedger(self.plan, (*self.events, event))

    def _new_event(self, **values: object) -> dict[str, object]:
        event = {
            "artifact_schema_version": LEDGER_EVENT_SCHEMA_VERSION,
            "sequence": len(self.events) + 1,
            "event_type": values["event_type"],
            "recorded_at": _iso(values["now"]),
            "prev_event_identity": None if not self.events else self.events[-1]["event_identity"],
            "plan_identity": self.plan.plan_identity,
            "plan_sha256": self.plan.sha256,
            "provider_id": values["provider_id"],
            "model_id": values["model_id"],
            "slot": values["slot"],
            "slot_key": f'{values["provider_id"]}:{values["slot"]}',
            "request_identity": values["request_identity"],
            "payload_sha256": values["payload_sha256"],
            "worst_case_cny": _decimal_text(_decimal(values["worst_case_cny"], "worst_case_cny")),
            "start_event_identity": values["start_event_identity"],
            "status": values["status"],
            "accounted_cny": (
                None
                if values["accounted_cny"] is None
                else _decimal_text(_decimal(values["accounted_cny"], "accounted_cny"))
            ),
            "evidence_identity": values["evidence_identity"],
            "evidence_network_start_event_identity": values[
                "evidence_network_start_event_identity"
            ],
            "evidence_terminal_event_identity": values[
                "evidence_terminal_event_identity"
            ],
            "event_identity": None,
        }
        identity_payload = dict(event)
        identity_payload.pop("event_identity")
        event["event_identity"] = _identity(identity_payload)
        return event


class GitRemoteLedgerStore:
    """A one-file Git ref store whose normal push is the CAS primitive."""

    def __init__(
        self,
        *,
        repository: Path,
        remote: str = "origin",
        remote_ref: str = DEFAULT_REMOTE_REF,
    ) -> None:
        self.repository = Path(repository).resolve()
        self.remote = remote
        self.remote_ref = remote_ref
        if not re.fullmatch(r"refs/heads/[A-Za-z0-9._/-]+", remote_ref):
            raise ValueError("remote_ref must be a full heads ref")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", remote):
            raise ValueError("remote must be a configured Git remote name")

    def _run(self, args: Sequence[str], *, input_bytes: bytes | None = None) -> bytes:
        environment = dict(os.environ)
        environment.setdefault("GIT_AUTHOR_NAME", "Stage-A Live Lane")
        environment.setdefault("GIT_AUTHOR_EMAIL", "stage-a-live@invalid.local")
        environment.setdefault("GIT_COMMITTER_NAME", environment["GIT_AUTHOR_NAME"])
        environment.setdefault("GIT_COMMITTER_EMAIL", environment["GIT_AUTHOR_EMAIL"])
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=self.repository,
                input=input_bytes,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
                env=environment,
            )
        except OSError as error:
            raise RemoteLedgerUnavailableError("Git remote state command is unavailable") from error
        if completed.returncode != 0:
            raise RemoteLedgerUnavailableError("Git remote state command failed")
        return completed.stdout

    def _remote_head(self) -> str | None:
        output = self._run(["ls-remote", "--heads", self.remote, self.remote_ref])
        if not output.strip():
            return None
        rows = output.decode("ascii", errors="strict").splitlines()
        if len(rows) != 1:
            raise RemoteLedgerVerificationError("remote state ref did not resolve uniquely")
        fields = rows[0].split()
        if len(fields) != 2 or fields[1] != self.remote_ref or _GIT_OID.fullmatch(fields[0]) is None:
            raise RemoteLedgerVerificationError("remote state ref response is malformed")
        return fields[0]

    def _read_file_at(self, commit_sha: str, filename: str) -> bytes:
        return self._run(["show", f"{commit_sha}:{filename}"])

    def _tree_entries_at(self, commit_sha: str) -> dict[str, str]:
        entries: dict[str, str] = {}
        for row in self._run(["ls-tree", commit_sha]).decode("utf-8").splitlines():
            try:
                metadata, filename = row.split("\t", 1)
            except ValueError as error:
                raise RemoteLedgerVerificationError(
                    "remote state tree entry is malformed"
                ) from error
            parts = metadata.split()
            if (
                len(parts) != 3
                or parts[0] != "100644"
                or parts[1] != "blob"
                or _GIT_OID.fullmatch(parts[2]) is None
                or (
                    filename != LEDGER_FILENAME
                    and re.fullmatch(r"evidence-[0-9a-f]{64}\.json", filename) is None
                )
                or filename in entries
            ):
                raise RemoteLedgerVerificationError(
                    "remote state tree contains an unsupported or duplicate entry"
                )
            entries[filename] = parts[2]
        if LEDGER_FILENAME not in entries:
            raise RemoteLedgerVerificationError("remote state tree is missing its ledger")
        return entries

    @staticmethod
    def _validate_terminal_evidence_binding(
        *,
        plan: VerifiedFrozenStageAPlan,
        ledger: RemoteExecutionLedger,
        terminal: Mapping[str, object],
        artifact: Mapping[str, object],
    ) -> None:
        key = str(terminal["slot_key"])
        starts = [
            event
            for event in ledger.events
            if event["slot_key"] == key
            and event["event_type"] == NETWORK_ATTEMPT_STARTED
        ]
        attempts = artifact.get("attempts")
        if (
            len(starts) != 1
            or not isinstance(attempts, list)
            or len(attempts) != 1
            or not isinstance(attempts[0], Mapping)
            or artifact.get("attempt_count") != 1
            or artifact.get("source_journal_event_count") != 2
        ):
            raise RemoteLedgerIntegrityError(
                "remote evidence does not represent exactly one terminal attempt"
            )
        start = starts[0]
        attempt = attempts[0]
        expected_artifact = {
            "artifact_identity": terminal["evidence_identity"],
            "plan_identity": plan.plan_identity,
            "plan_sha256": plan.sha256,
            "source_journal_last_event_identity": terminal[
                "evidence_terminal_event_identity"
            ],
            "accounted_cny": terminal["accounted_cny"],
        }
        expected_attempt = {
            "plan_identity": plan.plan_identity,
            "plan_sha256": plan.sha256,
            "provider_id": terminal["provider_id"],
            "requested_model_id": terminal["model_id"],
            "slot": terminal["slot"],
            "slot_key": key,
            "request_identity": terminal["request_identity"],
            "payload_sha256": terminal["payload_sha256"],
            "frozen_worst_case_cny": terminal["worst_case_cny"],
            "accounted_cny": terminal["accounted_cny"],
            "network_start_event_identity": terminal[
                "evidence_network_start_event_identity"
            ],
            "terminal_event_identity": terminal["evidence_terminal_event_identity"],
            "terminal_status": terminal["status"],
        }
        if any(artifact.get(name) != value for name, value in expected_artifact.items()):
            raise RemoteLedgerIntegrityError(
                "remote evidence artifact differs from its terminal binding"
            )
        if any(attempt.get(name) != value for name, value in expected_attempt.items()):
            raise RemoteLedgerIntegrityError(
                "remote evidence attempt differs from its start/terminal binding"
            )

    def load(self, plan: VerifiedFrozenStageAPlan) -> RemoteLedgerObservedState:
        head = self._remote_head()
        if head is None:
            return RemoteLedgerObservedState(None, RemoteExecutionLedger.empty(plan))
        self._run(["fetch", "--no-tags", self.remote, f"{self.remote_ref}:refs/stage-a-live/observed"])
        entries = self._tree_entries_at(head)
        raw = self._read_file_at(head, LEDGER_FILENAME)
        ledger = RemoteExecutionLedger.from_bytes(plan, raw)
        terminals = [
            event for event in ledger.events if event["event_type"] == ATTEMPT_TERMINAL
        ]
        expected_evidence_names = {
            f'evidence-{event["evidence_identity"]}.json' for event in terminals
        }
        actual_evidence_names = set(entries) - {LEDGER_FILENAME}
        if actual_evidence_names != expected_evidence_names:
            raise RemoteLedgerIntegrityError(
                "remote evidence file set differs from terminal identities"
            )
        for terminal in terminals:
            filename = f'evidence-{terminal["evidence_identity"]}.json'
            evidence_bytes = self._read_file_at(head, filename)
            try:
                artifact = validate_stage_a_attempt_evidence_bytes(
                    plan=plan,
                    raw_bytes=evidence_bytes,
                )
            except StageAEvidenceError as error:
                raise RemoteLedgerIntegrityError(
                    "remote terminal evidence failed artifact validation"
                ) from error
            self._validate_terminal_evidence_binding(
                plan=plan,
                ledger=ledger,
                terminal=terminal,
                artifact=artifact,
            )
        return RemoteLedgerObservedState(head, ledger)

    def compare_and_swap(
        self,
        *,
        expected_head: str | None,
        ledger_bytes: bytes,
        evidence_artifacts: Mapping[str, bytes] | None = None,
    ) -> str:
        if self._remote_head() != expected_head:
            raise RemoteLedgerConflictError("remote state head changed before reservation")
        artifacts = dict(evidence_artifacts or {})
        files = {LEDGER_FILENAME: ledger_bytes, **artifacts}
        retained_entries: dict[str, str] = {}
        if expected_head is not None:
            retained_entries.update(self._tree_entries_at(expected_head))
        for filename, content in sorted(files.items()):
            if filename != LEDGER_FILENAME and re.fullmatch(r"evidence-[0-9a-f]{64}\.json", filename) is None:
                raise RemoteLedgerVerificationError("remote evidence filename is invalid")
            blob = self._run(["hash-object", "-w", "--stdin"], input_bytes=content).decode("ascii").strip()
            if _GIT_OID.fullmatch(blob) is None:
                raise RemoteLedgerVerificationError("Git returned an invalid blob identity")
            retained_entries[filename] = blob
        entries = [
            f"100644 blob {blob}\t{filename}\n"
            for filename, blob in sorted(retained_entries.items())
        ]
        tree = self._run(["mktree"], input_bytes="".join(entries).encode("utf-8")).decode("ascii").strip()
        commit_args = ["commit-tree", tree]
        if expected_head is not None:
            commit_args.extend(["-p", expected_head])
        commit_args.extend(["-m", "stage-a: persist remote execution state"])
        commit = self._run(commit_args).decode("ascii").strip()
        try:
            self._run(["push", "--porcelain", self.remote, f"{commit}:{self.remote_ref}"])
        except RemoteLedgerUnavailableError as error:
            raise RemoteLedgerConflictError("remote state CAS push failed") from error
        if self._remote_head() != commit:
            raise RemoteLedgerVerificationError("remote state head differs after CAS push")
        self._run(["fetch", "--no-tags", self.remote, f"{self.remote_ref}:refs/stage-a-live/verified"])
        for filename, expected in files.items():
            if self._read_file_at(commit, filename) != expected:
                raise RemoteLedgerVerificationError("remote state bytes differ after persistence")
        return commit


__all__ = [
    "DEFAULT_REMOTE_REF",
    "GitRemoteLedgerStore",
    "LEDGER_FILENAME",
    "RemoteExecutionLedger",
    "RemoteLedgerConflictError",
    "RemoteLedgerError",
    "RemoteLedgerIntegrityError",
    "RemoteLedgerObservedState",
    "RemoteLedgerUnavailableError",
    "RemoteLedgerVerificationError",
]

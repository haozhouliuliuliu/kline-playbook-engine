"""Crash-resilient single-slot V0.3 live lane.

This is the only GitHub-hosted V0.3 live path. It persists and verifies a remote
write-ahead reservation (ref `refs/heads/stage-a-live-state-v0-3`) before entering
the V0.3 provider transport, and never automatically retries after a network start.

The V0.2 lane/ref/schema/plan identity are untouched. V0.3 uses brand-new plan,
slot, attempt, ledger and evidence identities. Old DEEPSEEK:1 / MINIMAX:1 / KIMI:1
are never accepted as V0.3 executable identities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import os
import re
import subprocess
from typing import Callable, Mapping, Protocol, Sequence

from src.jianghe_prespend_runtime import HARD_PROJECT_CAP_CNY
from src.jianghe_v03_plan import V03_PLAN_VERSION, build_v03_frozen_plan, pretty_plan_bytes
from src.jianghe_v03_runtime import (
    HISTORICAL_PROJECT_ACCOUNTED_CNY,
    V03_REMOTE_REF,
    V03TerminalStatus,
)

LEDGER_SCHEMA_VERSION = "JIANGHE_STAGE_A_V0_3_REMOTE_EXECUTION_LEDGER_V0_1"
LEDGER_EVENT_SCHEMA_VERSION = "JIANGHE_STAGE_A_V0_3_REMOTE_EXECUTION_EVENT_V0_1"
DEFAULT_REMOTE_REF = V03_REMOTE_REF
LEDGER_FILENAME = "stage-a-live-ledger-v0-3.json"
NETWORK_ATTEMPT_STARTED = "NETWORK_ATTEMPT_STARTED"
ATTEMPT_TERMINAL = "ATTEMPT_TERMINAL"
REMOTE_TERMINAL_STATUSES = frozenset(
    status.value for status in V03TerminalStatus
)

_SHA256 = re.compile(r"[0-9a-f]{64}\Z")
_GIT_OID = re.compile(r"[0-9a-f]{40}(?:[0-9a-f]{24})?\Z")
_PROVIDER_CREDENTIAL_ENV_NAMES = frozenset(
    {"MOONSHOT_API_KEY", "DEEPSEEK_API_KEY", "MINIMAX_API_KEY"}
)

_EVENT_FIELDS = frozenset({
    "artifact_schema_version", "sequence", "event_type", "recorded_at",
    "prev_event_identity", "plan_identity", "plan_sha256", "provider_id",
    "slot_identity", "request_identity", "worst_case_cny", "start_event_identity",
    "status", "accounted_cny", "evidence_identity",
    "evidence_network_start_event_identity", "evidence_terminal_event_identity",
    "event_identity",
})


class V03LiveLaneError(RuntimeError):
    pass


class V03LedgerIntegrityError(V03LiveLaneError):
    pass


class V03LedgerConflictError(V03LiveLaneError):
    pass


class V03LedgerUnavailableError(V03LiveLaneError):
    pass


class V03LedgerVerificationError(V03LiveLaneError):
    pass


def _canonical_bytes(value: object) -> bytes:
    return (
        json.dumps(
            value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
        )
        + "\n"
    ).encode("utf-8")


def _identity(value: object) -> str:
    return sha256(_canonical_bytes(value).rstrip(b"\n")).hexdigest()


def _decimal(value: object, name: str) -> Decimal:
    try:
        result = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise V03LedgerIntegrityError(f"{name} must be a finite Decimal") from None
    if not result.is_finite() or result < 0:
        raise V03LedgerIntegrityError(f"{name} must be non-negative and finite")
    return result


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def _iso(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise V03LiveLaneError("V0.3 ledger timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _validate_sha(value: object, name: str) -> str:
    if not isinstance(value, str) or _SHA256.fullmatch(value) is None:
        raise V03LedgerIntegrityError(f"{name} must be a lowercase SHA-256")
    return value


@dataclass(frozen=True)
class V03LedgerObservedState:
    head_sha: str | None
    ledger: "V03RemoteExecutionLedger"


@dataclass(frozen=True)
class V03Snapshot:
    attempted_slots: frozenset[str]
    project_accounted_cny: Decimal
    total_attempts: int


class V03RemoteExecutionLedger:
    """Write-ahead execution ledger bound to the V0.3 plan and identities."""

    def __init__(
        self,
        plan: Mapping[str, object],
        plan_sha256: str,
        events: Sequence[Mapping[str, object]] = (),
    ) -> None:
        if not isinstance(plan, Mapping):
            raise TypeError("plan must be a mapping")
        self.plan = plan
        self.plan_sha256 = plan_sha256
        self.plan_identity = str(plan["plan_identity"])
        self.events = tuple(dict(event) for event in events)
        self._validate_events()

    @classmethod
    def from_bytes(
        cls, plan: Mapping[str, object], plan_sha256: str, raw_bytes: bytes
    ) -> "V03RemoteExecutionLedger":
        try:
            payload = json.loads(raw_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise V03LedgerIntegrityError("V0.3 remote ledger is not valid UTF-8 JSON") from error
        if not isinstance(payload, dict) or frozenset(payload) != frozenset({
            "artifact_schema_version", "ledger_identity", "plan_identity",
            "plan_sha256", "events",
        }):
            raise V03LedgerIntegrityError("V0.3 remote ledger top-level schema mismatch")
        if payload["artifact_schema_version"] != LEDGER_SCHEMA_VERSION:
            raise V03LedgerIntegrityError("V0.3 remote ledger schema version mismatch")
        if (
            payload["plan_identity"] != plan["plan_identity"]
            or payload["plan_sha256"] != plan_sha256
        ):
            raise V03LedgerIntegrityError("V0.3 remote ledger is bound to a different frozen plan")
        events = payload["events"]
        if not isinstance(events, list):
            raise V03LedgerIntegrityError("V0.3 remote ledger events must be a list")
        identity_payload = dict(payload)
        declared = identity_payload.pop("ledger_identity")
        if _validate_sha(declared, "ledger_identity") != _identity(identity_payload):
            raise V03LedgerIntegrityError("V0.3 remote ledger identity does not match content")
        return cls(plan, plan_sha256, events)

    def payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "artifact_schema_version": LEDGER_SCHEMA_VERSION,
            "ledger_identity": None,
            "plan_identity": self.plan_identity,
            "plan_sha256": self.plan_sha256,
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
        previous: str | None = None
        for sequence, event in enumerate(self.events, start=1):
            if frozenset(event) != _EVENT_FIELDS:
                raise V03LedgerIntegrityError("V0.3 remote ledger event schema mismatch")
            if event["artifact_schema_version"] != LEDGER_EVENT_SCHEMA_VERSION:
                raise V03LedgerIntegrityError("V0.3 remote ledger event version mismatch")
            if event["sequence"] != sequence or event["prev_event_identity"] != previous:
                raise V03LedgerIntegrityError("V0.3 remote ledger sequence/hash chain is broken")
            try:
                recorded_at = datetime.fromisoformat(str(event["recorded_at"]))
            except ValueError as error:
                raise V03LedgerIntegrityError("V0.3 remote event timestamp is malformed") from error
            if recorded_at.tzinfo is None or recorded_at.utcoffset() is None:
                raise V03LedgerIntegrityError("V0.3 remote event timestamp must be timezone-aware")
            declared = _validate_sha(event["event_identity"], "event_identity")
            identity_payload = dict(event)
            identity_payload.pop("event_identity")
            if declared != _identity(identity_payload):
                raise V03LedgerIntegrityError("V0.3 remote event identity does not match content")
            if (
                event["plan_identity"] != self.plan_identity
                or event["plan_sha256"] != self.plan_sha256
            ):
                raise V03LedgerIntegrityError("V0.3 remote event frozen-plan binding mismatch")
            provider = event["provider_id"]
            slot_identity = event["slot_identity"]
            if not isinstance(provider, str) or not isinstance(slot_identity, str):
                raise V03LedgerIntegrityError("V0.3 remote event provider/slot is malformed")
            if not slot_identity.startswith(f"V0_3:{provider}:CAPABILITY_MATCHED_"):
                raise V03LedgerIntegrityError("V0.3 remote event slot identity is not a V0.3 slot")
            if event["event_type"] == NETWORK_ATTEMPT_STARTED:
                if slot_identity in starts:
                    raise V03LedgerIntegrityError("V0.3 remote slot has duplicate start")
                if any(
                    event[name] is not None
                    for name in (
                        "start_event_identity", "status", "accounted_cny",
                        "evidence_identity", "evidence_network_start_event_identity",
                        "evidence_terminal_event_identity",
                    )
                ):
                    raise V03LedgerIntegrityError("V0.3 remote start contains terminal fields")
                starts[slot_identity] = event
            elif event["event_type"] == ATTEMPT_TERMINAL:
                if slot_identity not in starts or slot_identity in terminals:
                    raise V03LedgerIntegrityError("V0.3 remote terminal has no unique start")
                if event["start_event_identity"] != starts[slot_identity]["event_identity"]:
                    raise V03LedgerIntegrityError("V0.3 remote terminal does not bind its start")
                if event["status"] not in REMOTE_TERMINAL_STATUSES:
                    raise V03LedgerIntegrityError("V0.3 remote terminal status is unsupported")
                for name in (
                    "evidence_identity", "evidence_network_start_event_identity",
                    "evidence_terminal_event_identity",
                ):
                    _validate_sha(event[name], name)
                if _decimal(event["accounted_cny"], "accounted_cny") > _decimal(
                    event["worst_case_cny"], "worst_case_cny"
                ):
                    raise V03LedgerIntegrityError("V0.3 remote terminal exceeds reserved cost")
                terminals.add(slot_identity)
            else:
                raise V03LedgerIntegrityError("V0.3 remote event type is unsupported")
            previous = declared
        self.snapshot()

    def snapshot(self) -> V03Snapshot:
        starts: dict[str, Mapping[str, object]] = {}
        terminals: dict[str, Mapping[str, object]] = {}
        for event in self.events:
            slot = str(event["slot_identity"])
            if event["event_type"] == NETWORK_ATTEMPT_STARTED:
                starts[slot] = event
            else:
                terminals[slot] = event
        total = HISTORICAL_PROJECT_ACCOUNTED_CNY
        for slot, start in starts.items():
            terminal = terminals.get(slot)
            total += _decimal(
                start["worst_case_cny"] if terminal is None else terminal["accounted_cny"],
                "V0.3 remote accounted cost",
            )
        if total > HARD_PROJECT_CAP_CNY:
            raise V03LedgerIntegrityError("V0.3 remote accounting exceeds the CNY100 hard cap")
        return V03Snapshot(
            attempted_slots=frozenset((*starts.keys(),)),
            project_accounted_cny=total,
            total_attempts=len(starts),
        )

    def append_start(
        self,
        *,
        now: datetime,
        provider_id: str,
        slot_identity: str,
        request_identity: str,
        worst_case_cny: Decimal,
    ) -> "V03RemoteExecutionLedger":
        if slot_identity in self.snapshot().attempted_slots:
            raise V03LedgerConflictError("V0.3 remote slot has already been attempted")
        event = self._new_event(
            now=now,
            event_type=NETWORK_ATTEMPT_STARTED,
            provider_id=provider_id,
            slot_identity=slot_identity,
            request_identity=request_identity,
            worst_case_cny=worst_case_cny,
            start_event_identity=None,
            status=None,
            accounted_cny=None,
            evidence_identity=None,
            evidence_network_start_event_identity=None,
            evidence_terminal_event_identity=None,
        )
        return V03RemoteExecutionLedger(self.plan, self.plan_sha256, (*self.events, event))

    def append_terminal(
        self,
        *,
        now: datetime,
        provider_id: str,
        slot_identity: str,
        status: str,
        accounted_cny: Decimal,
        evidence_identity: str,
        evidence_network_start_event_identity: str,
        evidence_terminal_event_identity: str,
    ) -> "V03RemoteExecutionLedger":
        starts = [
            e for e in self.events
            if e["slot_identity"] == slot_identity and e["event_type"] == NETWORK_ATTEMPT_STARTED
        ]
        terminals = [
            e for e in self.events
            if e["slot_identity"] == slot_identity and e["event_type"] == ATTEMPT_TERMINAL
        ]
        if len(starts) != 1 or terminals:
            raise V03LedgerConflictError("V0.3 remote slot cannot accept a terminal")
        start = starts[0]
        event = self._new_event(
            now=now,
            event_type=ATTEMPT_TERMINAL,
            provider_id=provider_id,
            slot_identity=slot_identity,
            request_identity=str(start["request_identity"]),
            worst_case_cny=_decimal(start["worst_case_cny"], "worst_case_cny"),
            start_event_identity=str(start["event_identity"]),
            status=status,
            accounted_cny=accounted_cny,
            evidence_identity=evidence_identity,
            evidence_network_start_event_identity=evidence_network_start_event_identity,
            evidence_terminal_event_identity=evidence_terminal_event_identity,
        )
        return V03RemoteExecutionLedger(self.plan, self.plan_sha256, (*self.events, event))

    def _new_event(self, **values: object) -> dict[str, object]:
        event: dict[str, object] = {
            "artifact_schema_version": LEDGER_EVENT_SCHEMA_VERSION,
            "sequence": len(self.events) + 1,
            "event_type": values["event_type"],
            "recorded_at": _iso(values["now"]),
            "prev_event_identity": None if not self.events else self.events[-1]["event_identity"],
            "plan_identity": self.plan_identity,
            "plan_sha256": self.plan_sha256,
            "provider_id": values["provider_id"],
            "slot_identity": values["slot_identity"],
            "request_identity": values["request_identity"],
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


class V03RemoteLedgerStore(Protocol):
    def load(self) -> V03LedgerObservedState: ...

    def compare_and_swap(
        self,
        *,
        expected_head: str | None,
        ledger_bytes: bytes,
        evidence_artifacts: Mapping[str, bytes] | None = None,
    ) -> str: ...


class V03GitRemoteLedgerStore:
    """Git CAS store on refs/heads/stage-a-live-state-v0-3 (normal push = CAS)."""

    def __init__(
        self,
        *,
        repository: os.PathLike[str],
        remote: str = "origin",
        remote_ref: str = DEFAULT_REMOTE_REF,
    ) -> None:
        self.repository = os.fspath(repository)
        self.remote = remote
        self.remote_ref = remote_ref
        if remote_ref != DEFAULT_REMOTE_REF:
            raise ValueError("caller-selected V0.3 remote ref is forbidden")
        if not re.fullmatch(r"refs/heads/[A-Za-z0-9._/-]+", remote_ref):
            raise ValueError("remote_ref must be a full heads ref")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", remote):
            raise ValueError("remote must be a configured Git remote name")

    def _run(self, args: Sequence[str], *, input_bytes: bytes | None = None) -> bytes:
        environment = dict(os.environ)
        for credential_name in _PROVIDER_CREDENTIAL_ENV_NAMES:
            environment.pop(credential_name, None)
        environment.setdefault("GIT_AUTHOR_NAME", "V0.3 Live Lane")
        environment.setdefault("GIT_AUTHOR_EMAIL", "v0.3-live@invalid.local")
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
            raise V03LedgerUnavailableError("Git remote state command is unavailable") from error
        if completed.returncode != 0:
            raise V03LedgerUnavailableError("Git remote state command failed")
        return completed.stdout

    def _remote_head(self) -> str | None:
        output = self._run(["ls-remote", "--heads", self.remote, self.remote_ref])
        if not output.strip():
            return None
        rows = output.decode("ascii", errors="strict").splitlines()
        if len(rows) != 1:
            raise V03LedgerVerificationError("V0.3 remote state ref did not resolve uniquely")
        fields = rows[0].split()
        if len(fields) != 2 or fields[1] != self.remote_ref or _GIT_OID.fullmatch(fields[0]) is None:
            raise V03LedgerVerificationError("V0.3 remote state ref response is malformed")
        return fields[0]

    def _read_file_at(self, commit_sha: str, filename: str) -> bytes:
        return self._run(["show", f"{commit_sha}:{filename}"])

    def _tree_entries_at(self, commit_sha: str) -> dict[str, str]:
        entries: dict[str, str] = {}
        for row in self._run(["ls-tree", commit_sha]).decode("utf-8").splitlines():
            try:
                metadata, filename = row.split("\t", 1)
            except ValueError as error:
                raise V03LedgerVerificationError("V0.3 remote tree entry is malformed") from error
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
                raise V03LedgerVerificationError(
                    "V0.3 remote tree contains an unsupported or duplicate entry"
                )
            entries[filename] = parts[2]
        if LEDGER_FILENAME not in entries:
            raise V03LedgerVerificationError("V0.3 remote tree is missing its ledger")
        return entries

    def load(self) -> V03LedgerObservedState:
        head = self._remote_head()
        if head is None:
            raise V03LedgerUnavailableError("V0.3 remote state ref is missing")
        plan = build_v03_frozen_plan()
        plan_bytes = pretty_plan_bytes(plan)
        plan_sha256 = sha256(plan_bytes).hexdigest()
        self._run(["fetch", "--no-tags", self.remote, f"{self.remote_ref}:refs/stage-a-v0-3/observed"])
        entries = self._tree_entries_at(head)
        raw = self._read_file_at(head, LEDGER_FILENAME)
        ledger = V03RemoteExecutionLedger.from_bytes(plan, plan_sha256, raw)
        terminals = [
            event for event in ledger.events if event["event_type"] == ATTEMPT_TERMINAL
        ]
        expected_evidence_names = {
            f'evidence-{event["evidence_identity"]}.json' for event in terminals
        }
        actual_evidence_names = set(entries) - {LEDGER_FILENAME}
        if actual_evidence_names != expected_evidence_names:
            raise V03LedgerIntegrityError(
                "V0.3 remote evidence file set differs from terminal identities"
            )
        return V03LedgerObservedState(head, ledger)

    def compare_and_swap(
        self,
        *,
        expected_head: str | None,
        ledger_bytes: bytes,
        evidence_artifacts: Mapping[str, bytes] | None = None,
    ) -> str:
        if self._remote_head() != expected_head:
            raise V03LedgerConflictError("V0.3 remote state head changed before reservation")
        artifacts = dict(evidence_artifacts or {})
        files = {LEDGER_FILENAME: ledger_bytes, **artifacts}
        retained_entries: dict[str, str] = {}
        if expected_head is not None:
            retained_entries.update(self._tree_entries_at(expected_head))
        for filename, content in sorted(files.items()):
            if filename != LEDGER_FILENAME and re.fullmatch(r"evidence-[0-9a-f]{64}\.json", filename) is None:
                raise V03LedgerVerificationError("V0.3 remote evidence filename is invalid")
            blob = self._run(["hash-object", "-w", "--stdin"], input_bytes=content).decode("ascii").strip()
            if _GIT_OID.fullmatch(blob) is None:
                raise V03LedgerVerificationError("Git returned an invalid blob identity")
            retained_entries[filename] = blob
        entries = [
            f"100644 blob {blob}\t{filename}\n"
            for filename, blob in sorted(retained_entries.items())
        ]
        tree = self._run(["mktree"], input_bytes="".join(entries).encode("utf-8")).decode("ascii").strip()
        commit_args = ["commit-tree", tree]
        if expected_head is not None:
            commit_args.extend(["-p", expected_head])
        commit_args.extend(["-m", "stage-a: persist V0.3 remote execution state"])
        commit = self._run(commit_args).decode("ascii").strip()
        try:
            self._run(["push", "--porcelain", self.remote, f"{commit}:{self.remote_ref}"])
        except V03LedgerUnavailableError as error:
            raise V03LedgerConflictError("V0.3 remote state CAS push failed") from error
        if self._remote_head() != commit:
            raise V03LedgerVerificationError("V0.3 remote state head differs after CAS push")
        self._run(["fetch", "--no-tags", self.remote, f"{self.remote_ref}:refs/stage-a-v0-3/verified"])
        for filename, expected in files.items():
            if self._read_file_at(commit, filename) != expected:
                raise V03LedgerVerificationError("V0.3 remote state bytes differ after persistence")
        return commit


@dataclass(frozen=True)
class V03LiveLaneResult:
    provider_id: str
    slot_identity: str
    terminal_status: str
    accounted_cny: Decimal
    evidence_identity: str
    remote_start_head: str
    remote_terminal_head: str


__all__ = [
    "ATTEMPT_TERMINAL", "DEFAULT_REMOTE_REF", "LEDGER_FILENAME", "NETWORK_ATTEMPT_STARTED",
    "V03GitRemoteLedgerStore", "V03LedgerConflictError", "V03LedgerIntegrityError",
    "V03LedgerObservedState", "V03LedgerUnavailableError", "V03LedgerVerificationError",
    "V03LiveLaneError", "V03LiveLaneResult", "V03RemoteExecutionLedger",
    "V03RemoteLedgerStore", "V03Snapshot",
]

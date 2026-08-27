"""Durable provider-attempt accounting for the V0.1 provider-smoke runner.

Owns ONLY the provider-attempt state machine:

    ATTEMPT_STARTED -> RESULT_RECEIVED
                    -> UNKNOWN_AFTER_ATTEMPT_START

``ATTEMPT_STARTED`` is durably recorded BEFORE the real bridge child process is
launched (the transport records it immediately before invoking the one-shot
bridge that launches the child).  If persistence of ``ATTEMPT_STARTED`` fails,
the child process must NOT be launched.

``RESULT_RECEIVED`` means the bridge returned a result artifact (any bridge
status).  ``UNKNOWN_AFTER_ATTEMPT_START`` means the project cannot prove whether
the provider received/completed the request (timeout, missing result file,
malformed/undecodable result, or equivalent parent-child handoff failure after
attempt start).  An unknown attempt is NEVER represented as zero provider /
network calls.

This ledger references (does not duplicate) the durable ``Fixed5MWakeLedger``
wake/request binding: it records the wake's logical/runtime identity, close
time and request identity together with the authority identity, call/sequence,
zero-retry policy and the attempt state.  It is the single clear owner of
provider-attempt accounting.
"""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Mapping

PROVIDER_ATTEMPT_LEDGER_VERSION = "KPE_REPLAY_V0_1_PROVIDER_ATTEMPT_LEDGER_V0_1"
PROVIDER_ATTEMPT_LEDGER_SCHEMA_VERSION = "KPE_REPLAY_V0_1_PROVIDER_ATTEMPT_STORE_V0_1"

ATTEMPT_STARTED = "ATTEMPT_STARTED"
RESULT_RECEIVED = "RESULT_RECEIVED"
UNKNOWN_AFTER_ATTEMPT_START = "UNKNOWN_AFTER_ATTEMPT_START"
ATTEMPT_STATES = frozenset({ATTEMPT_STARTED, RESULT_RECEIVED, UNKNOWN_AFTER_ATTEMPT_START})
_TERMINAL_ATTEMPT_STATES = frozenset({RESULT_RECEIVED, UNKNOWN_AFTER_ATTEMPT_START})


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _iso_text(value: object, field_name: str) -> str:
    if isinstance(value, str) and value:
        return value
    if isinstance(value, datetime):
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError(f"{field_name} must be timezone-aware")
        return value.astimezone(timezone.utc).isoformat(timespec="microseconds")
    raise ValueError(f"{field_name} must be an ISO datetime or datetime")


def _require_non_empty(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be non-empty")
    return value


@dataclass(frozen=True)
class ProviderAttempt:
    """One provider-attempt record bound to an admitted wake/request."""

    sequence: int
    call: str
    authority_identity: str
    logical_wake_selection_identity: str
    wake_identity: str
    close_time: str
    request_id: str
    retry_count: int
    attempt_state: str
    reason: str | None = None
    result_metadata: tuple[tuple[str, str | None], ...] = ()
    identity: str | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "sequence": self.sequence,
            "call": self.call,
            "authority_identity": self.authority_identity,
            "logical_wake_selection_identity": self.logical_wake_selection_identity,
            "wake_identity": self.wake_identity,
            "close_time": self.close_time,
            "request_id": self.request_id,
            "retry_count": self.retry_count,
            "attempt_state": self.attempt_state,
            "reason": self.reason,
            "result_metadata": dict(self.result_metadata),
            "identity": self.identity,
        }


class ProviderAttemptLedger:
    """Durable append-only-ish provider-attempt journal (one row per sequence)."""

    def __init__(self, path: str | Path, *, authority_identity: str) -> None:
        _require_non_empty(authority_identity, "authority_identity")
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.authority_identity = authority_identity
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS provider_attempt_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS provider_attempts (
                    sequence INTEGER PRIMARY KEY,
                    call TEXT NOT NULL,
                    authority_identity TEXT NOT NULL,
                    logical_wake_selection_identity TEXT NOT NULL,
                    wake_identity TEXT NOT NULL,
                    close_time TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    retry_count INTEGER NOT NULL,
                    attempt_state TEXT NOT NULL,
                    reason TEXT,
                    result_metadata TEXT,
                    updated_at TEXT NOT NULL
                );
                """
            )
            schema = connection.execute(
                "SELECT value FROM provider_attempt_meta WHERE key='schema_version'"
            ).fetchone()
            if schema is not None and schema[0] != PROVIDER_ATTEMPT_LEDGER_SCHEMA_VERSION:
                raise ValueError("unsupported provider attempt ledger schema")
            recorded_authority = connection.execute(
                "SELECT value FROM provider_attempt_meta WHERE key='authority_identity'"
            ).fetchone()
            if recorded_authority is not None and recorded_authority[0] != self.authority_identity:
                raise ValueError("provider attempt ledger belongs to a different authority")
            connection.execute(
                "INSERT OR IGNORE INTO provider_attempt_meta(key, value) VALUES('schema_version', ?)",
                (PROVIDER_ATTEMPT_LEDGER_SCHEMA_VERSION,),
            )
            connection.execute(
                "INSERT OR IGNORE INTO provider_attempt_meta(key, value) VALUES('authority_identity', ?)",
                (self.authority_identity,),
            )
            connection.execute(
                "INSERT OR IGNORE INTO provider_attempt_meta(key, value) VALUES('ledger_version', ?)",
                (PROVIDER_ATTEMPT_LEDGER_VERSION,),
            )

    def record_attempt_started(
        self,
        *,
        sequence: int,
        call: str,
        logical_wake_selection_identity: str,
        wake_identity: str,
        close_time: object,
        request_id: str,
        retry_count: int = 0,
    ) -> ProviderAttempt:
        """Durably record ATTEMPT_STARTED; MUST precede child-process launch.

        Raises on any persistence failure, in which case the caller must NOT
        launch the bridge child process.
        """
        if type(sequence) is not int or sequence < 0:
            raise ValueError("attempt sequence must be a non-negative integer")
        if type(retry_count) is not int or retry_count != 0:
            raise ValueError("provider attempt retry count must be fixed at zero")
        record = ProviderAttempt(
            sequence=sequence,
            call=_require_non_empty(call, "call"),
            authority_identity=self.authority_identity,
            logical_wake_selection_identity=_require_non_empty(
                logical_wake_selection_identity, "logical_wake_selection_identity"
            ),
            wake_identity=_require_non_empty(wake_identity, "wake_identity"),
            close_time=_iso_text(close_time, "close_time"),
            request_id=_require_non_empty(request_id, "request_id"),
            retry_count=retry_count,
            attempt_state=ATTEMPT_STARTED,
        )
        with closing(self._connect()) as connection, connection:
            existing = connection.execute(
                "SELECT attempt_state FROM provider_attempts WHERE sequence=?", (sequence,)
            ).fetchone()
            if existing is not None and existing["attempt_state"] in _TERMINAL_ATTEMPT_STATES:
                raise ValueError(
                    f"attempt {sequence} is already terminal ({existing['attempt_state']})"
                )
            connection.execute(
                """
                INSERT OR REPLACE INTO provider_attempts(
                    sequence, call, authority_identity, logical_wake_selection_identity,
                    wake_identity, close_time, request_id, retry_count, attempt_state,
                    reason, result_metadata, updated_at
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?)
                """,
                (
                    sequence, record.call, record.authority_identity,
                    record.logical_wake_selection_identity, record.wake_identity,
                    record.close_time, record.request_id, record.retry_count,
                    record.attempt_state, _utc_now(),
                ),
            )
        return record

    def _transition(self, *, sequence: int, new_state: str, reason: str | None, metadata: Mapping[str, object] | None) -> ProviderAttempt:
        if new_state not in ATTEMPT_STATES:
            raise ValueError(f"unsupported attempt state {new_state!r}")
        with closing(self._connect()) as connection, connection:
            row = connection.execute(
                "SELECT * FROM provider_attempts WHERE sequence=?", (sequence,)
            ).fetchone()
            if row is None:
                raise ValueError(f"attempt {sequence} was never started")
            if row["attempt_state"] in _TERMINAL_ATTEMPT_STATES:
                raise ValueError(
                    f"attempt {sequence} is already terminal ({row['attempt_state']})"
                )
            if row["attempt_state"] != ATTEMPT_STARTED:
                raise ValueError(f"attempt {sequence} cannot transition from {row['attempt_state']}")
            metadata_json = None
            if metadata is not None:
                metadata_json = json.dumps(
                    {k: v for k, v in metadata.items() if v is not None},
                    ensure_ascii=False, sort_keys=True,
                )
            connection.execute(
                """
                UPDATE provider_attempts
                SET attempt_state=?, reason=?, result_metadata=?, updated_at=?
                WHERE sequence=?
                """,
                (new_state, reason, metadata_json, _utc_now(), sequence),
            )
            row = connection.execute(
                "SELECT * FROM provider_attempts WHERE sequence=?", (sequence,)
            ).fetchone()
        parsed_metadata = tuple()
        if row["result_metadata"]:
            raw = json.loads(row["result_metadata"])
            parsed_metadata = tuple(sorted((str(k), str(v)) for k, v in raw.items()))
        identity = _hash({
            "ledger_version": PROVIDER_ATTEMPT_LEDGER_VERSION,
            "sequence": row["sequence"],
            "call": row["call"],
            "authority_identity": row["authority_identity"],
            "logical_wake_selection_identity": row["logical_wake_selection_identity"],
            "wake_identity": row["wake_identity"],
            "close_time": row["close_time"],
            "request_id": row["request_id"],
            "retry_count": int(row["retry_count"]),
            "attempt_state": row["attempt_state"],
            "reason": row["reason"],
        })
        return ProviderAttempt(
            sequence=int(row["sequence"]),
            call=row["call"],
            authority_identity=row["authority_identity"],
            logical_wake_selection_identity=row["logical_wake_selection_identity"],
            wake_identity=row["wake_identity"],
            close_time=row["close_time"],
            request_id=row["request_id"],
            retry_count=int(row["retry_count"]),
            attempt_state=row["attempt_state"],
            reason=row["reason"],
            result_metadata=parsed_metadata,
            identity=identity,
        )

    def record_result_received(self, *, sequence: int, metadata: Mapping[str, object]) -> ProviderAttempt:
        """Transition ATTEMPT_STARTED -> RESULT_RECEIVED (bridge returned a result)."""
        return self._transition(sequence=sequence, new_state=RESULT_RECEIVED, reason=None, metadata=metadata)

    def record_unknown_after_attempt_start(self, *, sequence: int, reason: str) -> ProviderAttempt:
        """Transition ATTEMPT_STARTED -> UNKNOWN_AFTER_ATTEMPT_START (no trustworthy result)."""
        _require_non_empty(reason, "reason")
        return self._transition(sequence=sequence, new_state=UNKNOWN_AFTER_ATTEMPT_START, reason=reason, metadata=None)

    def attempts(self) -> tuple[ProviderAttempt, ...]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM provider_attempts ORDER BY sequence"
            ).fetchall()
        result = []
        for row in rows:
            parsed_metadata = tuple()
            if row["result_metadata"]:
                raw = json.loads(row["result_metadata"])
                parsed_metadata = tuple(sorted((str(k), str(v)) for k, v in raw.items()))
            result.append(ProviderAttempt(
                sequence=int(row["sequence"]),
                call=row["call"],
                authority_identity=row["authority_identity"],
                logical_wake_selection_identity=row["logical_wake_selection_identity"],
                wake_identity=row["wake_identity"],
                close_time=row["close_time"],
                request_id=row["request_id"],
                retry_count=int(row["retry_count"]),
                attempt_state=row["attempt_state"],
                reason=row["reason"],
                result_metadata=parsed_metadata,
                identity=None,
            ))
        return tuple(result)

    def unknown_after_attempt_start_count(self) -> int:
        return sum(1 for attempt in self.attempts() if attempt.attempt_state == UNKNOWN_AFTER_ATTEMPT_START)

    def result_received_count(self) -> int:
        return sum(1 for attempt in self.attempts() if attempt.attempt_state == RESULT_RECEIVED)

    def portable_export(self) -> dict[str, Any]:
        return {
            "provider_attempt_ledger_version": PROVIDER_ATTEMPT_LEDGER_VERSION,
            "schema_version": PROVIDER_ATTEMPT_LEDGER_SCHEMA_VERSION,
            "authority_identity": self.authority_identity,
            "attempts": [attempt.to_payload() for attempt in self.attempts()],
        }


def provider_attempt_ledger_path_for(state_dir: str | Path) -> Path:
    """Return the project-owned provider-attempt ledger DB path inside a state directory."""
    return Path(state_dir) / "provider_attempts.sqlite3"


__all__ = [
    "ATTEMPT_STARTED",
    "ATTEMPT_STATES",
    "PROVIDER_ATTEMPT_LEDGER_SCHEMA_VERSION",
    "PROVIDER_ATTEMPT_LEDGER_VERSION",
    "RESULT_RECEIVED",
    "UNKNOWN_AFTER_ATTEMPT_START",
    "ProviderAttempt",
    "ProviderAttemptLedger",
    "provider_attempt_ledger_path_for",
]

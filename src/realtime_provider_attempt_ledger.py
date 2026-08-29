"""Durable realtime provider-attempt ledger for future governed 5-minute wakes.

OFFLINE ONLY.  This module owns the provider-attempt state machine for future
realtime wakes:

    ATTEMPT_STARTED -> RESULT_RECEIVED
                    -> UNKNOWN_AFTER_ATTEMPT_START

``ATTEMPT_STARTED`` is durably recorded before any (future) provider request is
made.  If a crash/restart happens after an attempt is admitted but before a
trustworthy result, the attempt remains UNKNOWN and is NEVER silently retried.

Hard guarantees enforced here:

- one governed wake -> at most one admitted provider attempt (``wake_identity``
  is unique); a duplicate/replayed wake cannot create a second admitted attempt;
- retry count is fixed at zero by default;
- the attempt identity binds trader/session, wake, request, provider/model,
  prompt/schema/runtime and the caller-supplied authority identity.

This module performs no provider call, no network action and no DeepSeek
request.  It uses only the project-adopted local SQLite persistence mechanism.
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

REALTIME_PROVIDER_ATTEMPT_LEDGER_VERSION = "KPE_REALTIME_PROVIDER_ATTEMPT_LEDGER_V0_1"
REALTIME_PROVIDER_ATTEMPT_SCHEMA_VERSION = "KPE_REALTIME_PROVIDER_ATTEMPT_STORE_V0_1"

ATTEMPT_STARTED = "ATTEMPT_STARTED"
RESULT_RECEIVED = "RESULT_RECEIVED"
UNKNOWN_AFTER_ATTEMPT_START = "UNKNOWN_AFTER_ATTEMPT_START"
ATTEMPT_STATES = frozenset({ATTEMPT_STARTED, RESULT_RECEIVED, UNKNOWN_AFTER_ATTEMPT_START})
_TERMINAL_ATTEMPT_STATES = frozenset({RESULT_RECEIVED, UNKNOWN_AFTER_ATTEMPT_START})

DEFAULT_RETRY_COUNT = 0
AUTHORITY_IDENTITY_MISMATCH = "AUTHORITY_IDENTITY_MISMATCH"


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")


def _require_non_empty(value: object, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{field_name} must be a non-empty canonical string")
    return value.strip()


class DuplicateWakeAttemptError(Exception):
    """Raised when a wake already owns an admitted provider attempt."""


class AuthorityIdentityMismatchError(ValueError):
    """Raised before admission when an attempt targets another authority."""


@dataclass(frozen=True)
class RealtimeAttemptIdentity:
    """Identity binding for one future realtime provider attempt.

    All values are supplied by the caller (never invented here).  The derived
    ``identity_id`` binds trader/session, wake, request, provider/model,
    prompt/schema/runtime and authority identity.
    """

    trader_identity: str
    session_identity: str
    wake_identity: str
    request_identity: str
    provider_identity: str
    model_identity: str
    prompt_identity: str
    schema_identity: str
    runtime_identity: str
    authority_identity: str

    def __post_init__(self) -> None:
        for name, value in self.__dict__.items():
            object.__setattr__(self, name, _require_non_empty(value, name))

    @property
    def identity_id(self) -> str:
        return _hash(
            {
                "ledger_version": REALTIME_PROVIDER_ATTEMPT_LEDGER_VERSION,
                "trader_identity": self.trader_identity,
                "session_identity": self.session_identity,
                "wake_identity": self.wake_identity,
                "request_identity": self.request_identity,
                "provider_identity": self.provider_identity,
                "model_identity": self.model_identity,
                "prompt_identity": self.prompt_identity,
                "schema_identity": self.schema_identity,
                "runtime_identity": self.runtime_identity,
                "authority_identity": self.authority_identity,
            }
        )


@dataclass(frozen=True)
class RealtimeProviderAttempt:
    """One admitted realtime provider attempt (durable record)."""

    attempt_identity: str
    trader_identity: str
    session_identity: str
    wake_identity: str
    request_identity: str
    provider_identity: str
    model_identity: str
    prompt_identity: str
    schema_identity: str
    runtime_identity: str
    authority_identity: str
    retry_count: int
    attempt_state: str
    reason: str | None = None
    result_metadata: tuple[tuple[str, str | None], ...] = ()
    record_identity: str | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "attempt_identity": self.attempt_identity,
            "trader_identity": self.trader_identity,
            "session_identity": self.session_identity,
            "wake_identity": self.wake_identity,
            "request_identity": self.request_identity,
            "provider_identity": self.provider_identity,
            "model_identity": self.model_identity,
            "prompt_identity": self.prompt_identity,
            "schema_identity": self.schema_identity,
            "runtime_identity": self.runtime_identity,
            "authority_identity": self.authority_identity,
            "retry_count": self.retry_count,
            "attempt_state": self.attempt_state,
            "reason": self.reason,
            "result_metadata": dict(self.result_metadata),
            "record_identity": self.record_identity,
        }


class RealtimeProviderAttemptLedger:
    """Durable append-only-ish realtime provider-attempt journal."""

    def __init__(self, path: str | Path, *, authority_identity: str) -> None:
        self.authority_identity = _require_non_empty(authority_identity, "authority_identity")
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS realtime_provider_attempt_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS realtime_provider_attempts (
                    attempt_identity TEXT PRIMARY KEY,
                    trader_identity TEXT NOT NULL,
                    session_identity TEXT NOT NULL,
                    wake_identity TEXT NOT NULL UNIQUE,
                    request_identity TEXT NOT NULL,
                    provider_identity TEXT NOT NULL,
                    model_identity TEXT NOT NULL,
                    prompt_identity TEXT NOT NULL,
                    schema_identity TEXT NOT NULL,
                    runtime_identity TEXT NOT NULL,
                    authority_identity TEXT NOT NULL,
                    retry_count INTEGER NOT NULL,
                    attempt_state TEXT NOT NULL,
                    reason TEXT,
                    result_metadata TEXT,
                    updated_at TEXT NOT NULL
                );
                """
            )
            schema = connection.execute(
                "SELECT value FROM realtime_provider_attempt_meta WHERE key='schema_version'"
            ).fetchone()
            if schema is not None and schema[0] != REALTIME_PROVIDER_ATTEMPT_SCHEMA_VERSION:
                raise ValueError("unsupported realtime provider attempt ledger schema")
            recorded_authority = connection.execute(
                "SELECT value FROM realtime_provider_attempt_meta WHERE key='authority_identity'"
            ).fetchone()
            if recorded_authority is not None and recorded_authority[0] != self.authority_identity:
                raise ValueError("realtime provider attempt ledger belongs to a different authority")
            connection.execute(
                "INSERT OR IGNORE INTO realtime_provider_attempt_meta(key, value) VALUES('schema_version', ?)",
                (REALTIME_PROVIDER_ATTEMPT_SCHEMA_VERSION,),
            )
            connection.execute(
                "INSERT OR IGNORE INTO realtime_provider_attempt_meta(key, value) VALUES('authority_identity', ?)",
                (self.authority_identity,),
            )
            connection.execute(
                "INSERT OR IGNORE INTO realtime_provider_attempt_meta(key, value) VALUES('ledger_version', ?)",
                (REALTIME_PROVIDER_ATTEMPT_LEDGER_VERSION,),
            )

    def _row_to_attempt(self, row: sqlite3.Row) -> RealtimeProviderAttempt:
        parsed_metadata: tuple[tuple[str, str | None], ...] = ()
        if row["result_metadata"]:
            raw = json.loads(row["result_metadata"])
            parsed_metadata = tuple(sorted((str(k), str(v)) for k, v in raw.items()))
        return RealtimeProviderAttempt(
            attempt_identity=row["attempt_identity"],
            trader_identity=row["trader_identity"],
            session_identity=row["session_identity"],
            wake_identity=row["wake_identity"],
            request_identity=row["request_identity"],
            provider_identity=row["provider_identity"],
            model_identity=row["model_identity"],
            prompt_identity=row["prompt_identity"],
            schema_identity=row["schema_identity"],
            runtime_identity=row["runtime_identity"],
            authority_identity=row["authority_identity"],
            retry_count=int(row["retry_count"]),
            attempt_state=row["attempt_state"],
            reason=row["reason"],
            result_metadata=parsed_metadata,
            record_identity=None,
        )

    def record_attempt_started(
        self, *, identity: RealtimeAttemptIdentity, retry_count: int = DEFAULT_RETRY_COUNT
    ) -> RealtimeProviderAttempt:
        """Durably admit ATTEMPT_STARTED; MUST precede any future provider request.

        A wake may own at most one admitted attempt: re-admitting the same wake
        (duplicate or replayed) raises ``DuplicateWakeAttemptError``.
        """
        if not isinstance(identity, RealtimeAttemptIdentity):
            raise TypeError("realtime attempt identity must be RealtimeAttemptIdentity")
        if identity.authority_identity != self.authority_identity:
            raise AuthorityIdentityMismatchError(
                f"{AUTHORITY_IDENTITY_MISMATCH}:ledger={self.authority_identity}:"
                f"attempt={identity.authority_identity}"
            )
        if type(retry_count) is not int or retry_count != DEFAULT_RETRY_COUNT:
            raise ValueError("realtime provider attempt retry count must remain fixed at zero")
        attempt_identity = identity.identity_id
        with closing(self._connect()) as connection, connection:
            existing = connection.execute(
                "SELECT attempt_identity FROM realtime_provider_attempts WHERE wake_identity=?",
                (identity.wake_identity,),
            ).fetchone()
            if existing is not None:
                raise DuplicateWakeAttemptError(
                    f"wake {identity.wake_identity} already owns an admitted provider attempt"
                )
            connection.execute(
                """
                INSERT INTO realtime_provider_attempts(
                    attempt_identity, trader_identity, session_identity, wake_identity,
                    request_identity, provider_identity, model_identity, prompt_identity,
                    schema_identity, runtime_identity, authority_identity, retry_count,
                    attempt_state, reason, result_metadata, updated_at
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?)
                """,
                (
                    attempt_identity,
                    identity.trader_identity,
                    identity.session_identity,
                    identity.wake_identity,
                    identity.request_identity,
                    identity.provider_identity,
                    identity.model_identity,
                    identity.prompt_identity,
                    identity.schema_identity,
                    identity.runtime_identity,
                    identity.authority_identity,
                    retry_count,
                    ATTEMPT_STARTED,
                    _utc_now(),
                ),
            )
        return RealtimeProviderAttempt(
            attempt_identity=attempt_identity,
            trader_identity=identity.trader_identity,
            session_identity=identity.session_identity,
            wake_identity=identity.wake_identity,
            request_identity=identity.request_identity,
            provider_identity=identity.provider_identity,
            model_identity=identity.model_identity,
            prompt_identity=identity.prompt_identity,
            schema_identity=identity.schema_identity,
            runtime_identity=identity.runtime_identity,
            authority_identity=identity.authority_identity,
            retry_count=retry_count,
            attempt_state=ATTEMPT_STARTED,
        )

    def _transition(
        self,
        *,
        attempt_identity: str,
        new_state: str,
        reason: str | None,
        metadata: Mapping[str, object] | None,
    ) -> RealtimeProviderAttempt:
        if new_state not in ATTEMPT_STATES:
            raise ValueError(f"unsupported attempt state {new_state!r}")
        with closing(self._connect()) as connection, connection:
            row = connection.execute(
                "SELECT * FROM realtime_provider_attempts WHERE attempt_identity=?",
                (attempt_identity,),
            ).fetchone()
            if row is None:
                raise ValueError(f"attempt {attempt_identity} was never started")
            if row["attempt_state"] in _TERMINAL_ATTEMPT_STATES:
                raise ValueError(
                    f"attempt for {row['wake_identity']} is already terminal ({row['attempt_state']})"
                )
            if row["attempt_state"] != ATTEMPT_STARTED:
                raise ValueError(
                    f"attempt for {row['wake_identity']} cannot transition from {row['attempt_state']}"
                )
            metadata_json = None
            if metadata is not None:
                metadata_json = json.dumps(
                    {k: v for k, v in metadata.items() if v is not None},
                    ensure_ascii=False, sort_keys=True,
                )
            connection.execute(
                """
                UPDATE realtime_provider_attempts
                SET attempt_state=?, reason=?, result_metadata=?, updated_at=?
                WHERE attempt_identity=?
                """,
                (new_state, reason, metadata_json, _utc_now(), attempt_identity),
            )
        updated = self.attempt_for_identity(attempt_identity)
        if updated is None:
            raise ValueError(f"attempt {attempt_identity} vanished after transition")
        record_identity = _hash(
            {
                "ledger_version": REALTIME_PROVIDER_ATTEMPT_LEDGER_VERSION,
                "attempt_identity": updated.attempt_identity,
                "wake_identity": updated.wake_identity,
                "retry_count": updated.retry_count,
                "attempt_state": updated.attempt_state,
                "reason": updated.reason,
            }
        )
        return RealtimeProviderAttempt(
            **{
                **updated.to_payload(),
                "record_identity": record_identity,
            }
        )

    def record_result_received(
        self, *, attempt_identity: str, metadata: Mapping[str, object]
    ) -> RealtimeProviderAttempt:
        """Transition ATTEMPT_STARTED -> RESULT_RECEIVED."""
        return self._transition(
            attempt_identity=attempt_identity, new_state=RESULT_RECEIVED, reason=None, metadata=metadata
        )

    def record_unknown_after_attempt_start(
        self, *, attempt_identity: str, reason: str
    ) -> RealtimeProviderAttempt:
        """Transition ATTEMPT_STARTED -> UNKNOWN_AFTER_ATTEMPT_START (no trustworthy result)."""
        _require_non_empty(reason, "reason")
        return self._transition(
            attempt_identity=attempt_identity,
            new_state=UNKNOWN_AFTER_ATTEMPT_START,
            reason=reason,
            metadata=None,
        )

    def attempt_for_identity(self, attempt_identity: str) -> RealtimeProviderAttempt | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM realtime_provider_attempts WHERE attempt_identity=?",
                (attempt_identity,),
            ).fetchone()
        return None if row is None else self._row_to_attempt(row)

    def attempt_for_wake(self, wake_identity: str) -> RealtimeProviderAttempt | None:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT * FROM realtime_provider_attempts WHERE wake_identity=?",
                (wake_identity,),
            ).fetchone()
        return None if row is None else self._row_to_attempt(row)

    def attempts(self) -> tuple[RealtimeProviderAttempt, ...]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM realtime_provider_attempts ORDER BY attempt_identity"
            ).fetchall()
        return tuple(self._row_to_attempt(row) for row in rows)

    def unknown_after_attempt_start_count(self) -> int:
        return sum(1 for attempt in self.attempts() if attempt.attempt_state == UNKNOWN_AFTER_ATTEMPT_START)

    def unresolved_attempt_started_count(self) -> int:
        """Durable starts lacking a terminal handoff; adjudication-required, never an unused slot."""
        return sum(1 for attempt in self.attempts() if attempt.attempt_state == ATTEMPT_STARTED)

    def result_received_count(self) -> int:
        return sum(1 for attempt in self.attempts() if attempt.attempt_state == RESULT_RECEIVED)

    def admitted_attempt_count(self) -> int:
        return len(self.attempts())

    def portable_export(self) -> dict[str, Any]:
        return {
            "realtime_provider_attempt_ledger_version": REALTIME_PROVIDER_ATTEMPT_LEDGER_VERSION,
            "schema_version": REALTIME_PROVIDER_ATTEMPT_SCHEMA_VERSION,
            "authority_identity": self.authority_identity,
            "attempts": [attempt.to_payload() for attempt in self.attempts()],
        }


def realtime_provider_attempt_ledger_path_for(state_dir: str | Path) -> Path:
    """Return the project-owned realtime provider-attempt ledger DB path."""
    return Path(state_dir) / "realtime_provider_attempts.sqlite3"


__all__ = [
    "ATTEMPT_STARTED",
    "ATTEMPT_STATES",
    "AUTHORITY_IDENTITY_MISMATCH",
    "AuthorityIdentityMismatchError",
    "DEFAULT_RETRY_COUNT",
    "DuplicateWakeAttemptError",
    "REALTIME_PROVIDER_ATTEMPT_LEDGER_VERSION",
    "REALTIME_PROVIDER_ATTEMPT_SCHEMA_VERSION",
    "RESULT_RECEIVED",
    "UNKNOWN_AFTER_ATTEMPT_START",
    "RealtimeAttemptIdentity",
    "RealtimeProviderAttempt",
    "RealtimeProviderAttemptLedger",
    "realtime_provider_attempt_ledger_path_for",
]

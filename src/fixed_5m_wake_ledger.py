"""Append-only governed-session wake ledger for replay V0.1.

Implements the fixed V0.1 wake policy ``EVERY_NEW_CLOSED_5M_BAR``:

- each newly closed 5m bar inside one governed session produces exactly one wake;
- the schedule is the session's expected 5m close times, so 1m bars never wake and
  a 15m/1H/4H refresh at the same timestamp is context, never an extra request;
- duplicate / out-of-order / missing / off-grid wakes fail closed;
- exactly one admitted model request may bind to one wake, and one request may
  never bind to more than one wake;
- retry count is fixed at zero.

The ledger is project-owned, Harness-independent and append-only.  It persists
wake records, bindings and the session schedule so restart continuity can be
re-verified from the same state directory.
"""

from __future__ import annotations

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable, Sequence

WAKE_LEDGER_VERSION = "KPE_FIXED_5M_WAKE_LEDGER_V0_1"
WAKE_LEDGER_SCHEMA_VERSION = "KPE_FIXED_5M_WAKE_LEDGER_STORE_V0_1"
FIVE_MINUTES = timedelta(minutes=5)


def _canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _aware(value: datetime, field_name: str) -> datetime:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware")
    return value


def _iso(value: datetime) -> str:
    return _aware(value, "datetime").astimezone(timezone.utc).isoformat(timespec="microseconds")


def _parse_dt(value: object, field_name: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty ISO datetime")
    parsed = datetime.fromisoformat(value)
    return _aware(parsed, field_name)


def _assert_5m_grid(value: datetime, field_name: str) -> None:
    _aware(value, field_name)
    if value.minute % 5 != 0 or value.second != 0 or value.microsecond != 0:
        raise ValueError(f"{field_name} must be aligned to the closed-5m-bar grid")


@dataclass(frozen=True)
class GovernedWake:
    sequence: int
    wake_identity: str
    session_identity: str
    close_time: datetime
    scheduled_close_time: datetime
    trader_identity: str
    request_id: str | None
    retry_count: int

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("wake sequence cannot be negative")
        _aware(self.close_time, "wake.close_time")
        _aware(self.scheduled_close_time, "wake.scheduled_close_time")
        if self.close_time != self.scheduled_close_time:
            raise ValueError("wake close_time must equal its scheduled close time")
        if not self.wake_identity or not self.session_identity or not self.trader_identity:
            raise ValueError("wake identity fields must be non-empty")
        if self.request_id is not None and not self.request_id:
            raise ValueError("wake request_id must be null or non-empty")
        if type(self.retry_count) is not int or self.retry_count != 0:
            raise ValueError("wake/request retry count must be fixed at zero")


@dataclass(frozen=True)
class WakeBinding:
    wake_identity: str
    request_id: str
    session_identity: str
    bound_at: datetime
    retry_count: int


class Fixed5MWakeLedger:
    """Append-only governed-session 5m wake ledger with 1:1 wake<->request binding."""

    def __init__(
        self,
        path: str | Path,
        *,
        trader_identity: str,
        session_identity: str,
        schedule_5m_closes: Sequence[datetime],
    ) -> None:
        if not isinstance(trader_identity, str) or not trader_identity:
            raise ValueError("trader_identity must be non-empty")
        if not isinstance(session_identity, str) or not session_identity:
            raise ValueError("session_identity must be non-empty")
        schedule = tuple(schedule_5m_closes)
        if not schedule:
            raise ValueError("governed session must have at least one scheduled 5m close")
        previous: datetime | None = None
        for item in schedule:
            _assert_5m_grid(item, "schedule_5m_closes entry")
            if previous is not None and item <= previous:
                raise ValueError("schedule_5m_closes must be strictly increasing")
            previous = item
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.trader_identity = trader_identity
        self.session_identity = session_identity
        self._schedule = schedule
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS wake_ledger_meta (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS wake_sessions (
                    session_identity TEXT PRIMARY KEY,
                    trader_identity TEXT NOT NULL,
                    closed INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS wake_schedule (
                    session_identity TEXT NOT NULL,
                    seq INTEGER NOT NULL,
                    close_time TEXT NOT NULL,
                    PRIMARY KEY(session_identity, seq)
                );
                CREATE TABLE IF NOT EXISTS wake_records (
                    session_identity TEXT NOT NULL,
                    sequence INTEGER NOT NULL,
                    wake_identity TEXT NOT NULL UNIQUE,
                    close_time TEXT NOT NULL,
                    scheduled_close_time TEXT NOT NULL,
                    trader_identity TEXT NOT NULL,
                    request_id TEXT,
                    retry_count INTEGER NOT NULL,
                    PRIMARY KEY(session_identity, sequence)
                );
                CREATE TABLE IF NOT EXISTS wake_bindings (
                    session_identity TEXT NOT NULL,
                    wake_identity TEXT NOT NULL UNIQUE,
                    request_id TEXT NOT NULL UNIQUE,
                    bound_at TEXT NOT NULL,
                    retry_count INTEGER NOT NULL,
                    PRIMARY KEY(session_identity, wake_identity)
                );
                """
            )
            schema = connection.execute(
                "SELECT value FROM wake_ledger_meta WHERE key='schema_version'"
            ).fetchone()
            if schema is not None and schema[0] != WAKE_LEDGER_SCHEMA_VERSION:
                raise ValueError("unsupported wake ledger schema")
            existing_trader = connection.execute(
                "SELECT value FROM wake_ledger_meta WHERE key='trader_identity'"
            ).fetchone()
            if existing_trader is not None and existing_trader[0] != self.trader_identity:
                raise ValueError("wake ledger belongs to a different trader identity")
            session_row = connection.execute(
                "SELECT * FROM wake_sessions WHERE session_identity=?",
                (self.session_identity,),
            ).fetchone()
            if session_row is not None and session_row["trader_identity"] != self.trader_identity:
                raise ValueError("governed session wake ledger belongs to a different trader")
            stored_schedule = tuple(
                row["close_time"]
                for row in connection.execute(
                    "SELECT close_time FROM wake_schedule WHERE session_identity=? ORDER BY seq",
                    (self.session_identity,),
                )
            )
            if stored_schedule:
                stored = tuple(_parse_dt(value, "wake_schedule.close_time") for value in stored_schedule)
                if stored != self._schedule:
                    raise ValueError("governed-session wake schedule changed across reopen")
            else:
                connection.executemany(
                    "INSERT INTO wake_schedule(session_identity, seq, close_time) VALUES(?, ?, ?)",
                    [
                        (self.session_identity, index, _iso(item))
                        for index, item in enumerate(self._schedule)
                    ],
                )
            connection.execute(
                "INSERT OR IGNORE INTO wake_sessions(session_identity, trader_identity, closed) "
                "VALUES(?, ?, 0)",
                (self.session_identity, self.trader_identity),
            )
            connection.execute(
                "INSERT OR REPLACE INTO wake_ledger_meta(key, value) VALUES('schema_version', ?)",
                (WAKE_LEDGER_SCHEMA_VERSION,),
            )
            connection.execute(
                "INSERT OR REPLACE INTO wake_ledger_meta(key, value) VALUES('trader_identity', ?)",
                (self.trader_identity,),
            )

    @property
    def schedule(self) -> tuple[datetime, ...]:
        return self._schedule

    def _registered_wake_count(self, connection: sqlite3.Connection) -> int:
        row = connection.execute(
            "SELECT COUNT(*) FROM wake_records WHERE session_identity=?",
            (self.session_identity,),
        ).fetchone()
        return int(row[0])

    def register_closed_5m(self, close_time: datetime) -> GovernedWake:
        """Record one new closed-5m-bar wake; fail closed on any violation."""
        _assert_5m_grid(close_time, "close_time")
        with closing(self._connect()) as connection, connection:
            registered = self._registered_wake_count(connection)
            if registered >= len(self._schedule):
                raise ValueError("no further scheduled 5m wake exists; extra wake rejected")
            scheduled = self._schedule[registered]
            if close_time != scheduled:
                last_row = connection.execute(
                    "SELECT close_time FROM wake_records WHERE session_identity=? "
                    "ORDER BY sequence DESC LIMIT 1",
                    (self.session_identity,),
                ).fetchone()
                if last_row is not None and _parse_dt(last_row["close_time"], "wake.close_time") == close_time:
                    raise ValueError(
                        f"duplicate wake rejected for closed 5m bar {_iso(close_time)}"
                    )
                if last_row is not None and close_time < _parse_dt(
                    last_row["close_time"], "wake.close_time"
                ):
                    raise ValueError(
                        f"out-of-order wake rejected: {_iso(close_time)} precedes "
                        f"already-registered {last_row['close_time']}"
                    )
                raise ValueError(
                    f"missing wake detected: expected scheduled 5m close {_iso(scheduled)} "
                    f"but received {_iso(close_time)}"
                )
            sequence = registered
            wake_identity = _hash(
                {
                    "wake_ledger_version": WAKE_LEDGER_VERSION,
                    "session_identity": self.session_identity,
                    "sequence": sequence,
                    "close_time": _iso(close_time),
                    "trader_identity": self.trader_identity,
                }
            )
            connection.execute(
                """
                INSERT INTO wake_records(
                    session_identity, sequence, wake_identity, close_time,
                    scheduled_close_time, trader_identity, request_id, retry_count
                ) VALUES(?, ?, ?, ?, ?, ?, NULL, 0)
                """,
                (
                    self.session_identity,
                    sequence,
                    wake_identity,
                    _iso(close_time),
                    _iso(scheduled),
                    self.trader_identity,
                ),
            )
        return GovernedWake(
            sequence=sequence,
            wake_identity=wake_identity,
            session_identity=self.session_identity,
            close_time=close_time,
            scheduled_close_time=scheduled,
            trader_identity=self.trader_identity,
            request_id=None,
            retry_count=0,
        )

    def bind_request(self, wake_identity: str, request_id: str, *, retry_count: int = 0) -> WakeBinding:
        """Bind exactly one admitted model request to exactly one governed wake."""
        if not isinstance(request_id, str) or not request_id:
            raise ValueError("request_id must be non-empty")
        if type(retry_count) is not int or retry_count != 0:
            raise ValueError("model request retry count must be fixed at zero")
        with closing(self._connect()) as connection, connection:
            wake_row = connection.execute(
                "SELECT * FROM wake_records WHERE wake_identity=? AND session_identity=?",
                (wake_identity, self.session_identity),
            ).fetchone()
            if wake_row is None:
                raise ValueError("cannot bind a request to an unknown governed wake")
            existing_binding = connection.execute(
                "SELECT * FROM wake_bindings WHERE wake_identity=?",
                (wake_identity,),
            ).fetchone()
            if existing_binding is not None:
                raise ValueError("a governed wake may admit only one model request")
            reused_request = connection.execute(
                "SELECT * FROM wake_bindings WHERE request_id=?",
                (request_id,),
            ).fetchone()
            if reused_request is not None:
                raise ValueError("a model request may bind to only one governed wake")
            bound_at = _parse_dt(wake_row["close_time"], "wake.close_time")
            connection.execute(
                """
                INSERT INTO wake_bindings(
                    session_identity, wake_identity, request_id, bound_at, retry_count
                ) VALUES(?, ?, ?, ?, ?)
                """,
                (self.session_identity, wake_identity, request_id, _iso(bound_at), 0),
            )
            connection.execute(
                "UPDATE wake_records SET request_id=?, retry_count=? "
                "WHERE wake_identity=? AND session_identity=?",
                (request_id, 0, wake_identity, self.session_identity),
            )
        return WakeBinding(
            wake_identity=wake_identity,
            request_id=request_id,
            session_identity=self.session_identity,
            bound_at=bound_at,
            retry_count=0,
        )

    def list_wakes(self) -> tuple[GovernedWake, ...]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM wake_records WHERE session_identity=? ORDER BY sequence",
                (self.session_identity,),
            ).fetchall()
        return tuple(self._wake_from_row(row) for row in rows)

    def unbound_wakes(self) -> tuple[GovernedWake, ...]:
        return tuple(wake for wake in self.list_wakes() if wake.request_id is None)

    def bound_wake_for_request(self, request_id: str) -> GovernedWake | None:
        for wake in self.list_wakes():
            if wake.request_id == request_id:
                return wake
        return None

    def pending_wake_count(self) -> int:
        return len(self._schedule) - len(self.list_wakes())

    def is_closed(self) -> bool:
        with closing(self._connect()) as connection:
            row = connection.execute(
                "SELECT closed FROM wake_sessions WHERE session_identity=?",
                (self.session_identity,),
            ).fetchone()
        return row is not None and int(row["closed"]) == 1

    def close_session(self) -> None:
        """Verify the governed session is wake-complete and fully request-bound."""
        with closing(self._connect()) as connection, connection:
            wakes = tuple(
                self._wake_from_row(row)
                for row in connection.execute(
                    "SELECT * FROM wake_records WHERE session_identity=? ORDER BY sequence",
                    (self.session_identity,),
                ).fetchall()
            )
            if len(wakes) != len(self._schedule):
                missing = [
                    _iso(self._schedule[index]) for index in range(len(wakes), len(self._schedule))
                ]
                raise ValueError(
                    f"governed session closed with missing wakes: {missing}"
                )
            for wake in wakes:
                if wake.request_id is None:
                    raise ValueError(
                        f"governed session closed with an unbound wake {wake.wake_identity}"
                    )
            if self.is_closed():
                raise ValueError("governed session wake ledger is already closed")
            connection.execute(
                "UPDATE wake_sessions SET closed=1 WHERE session_identity=?",
                (self.session_identity,),
            )

    def verify_complete(self) -> None:
        """Fail-closed completeness check without mutating state (reopen-safe)."""
        if self.pending_wake_count() != 0:
            raise ValueError(f"governed session still has {self.pending_wake_count()} pending wakes")
        unbound = self.unbound_wakes()
        if unbound:
            raise ValueError(f"governed session has {len(unbound)} unbound wakes")
        if not self.is_closed():
            raise ValueError("governed session wake ledger has not been closed")

    def portable_export(self) -> dict[str, Any]:
        return {
            "wake_ledger_version": WAKE_LEDGER_VERSION,
            "schema_version": WAKE_LEDGER_SCHEMA_VERSION,
            "trader_identity": self.trader_identity,
            "session_identity": self.session_identity,
            "schedule_5m_closes": [_iso(item) for item in self._schedule],
            "wakes": [
                {
                    "sequence": wake.sequence,
                    "wake_identity": wake.wake_identity,
                    "close_time": _iso(wake.close_time),
                    "scheduled_close_time": _iso(wake.scheduled_close_time),
                    "request_id": wake.request_id,
                    "retry_count": wake.retry_count,
                }
                for wake in self.list_wakes()
            ],
            "closed": self.is_closed(),
        }

    @staticmethod
    def _wake_from_row(row: sqlite3.Row) -> GovernedWake:
        return GovernedWake(
            sequence=int(row["sequence"]),
            wake_identity=row["wake_identity"],
            session_identity=row["session_identity"],
            close_time=_parse_dt(row["close_time"], "wake_records.close_time"),
            scheduled_close_time=_parse_dt(
                row["scheduled_close_time"], "wake_records.scheduled_close_time"
            ),
            trader_identity=row["trader_identity"],
            request_id=row["request_id"],
            retry_count=int(row["retry_count"]),
        )


def wake_ledger_path_for(state_dir: str | Path) -> Path:
    """Return the project-owned wake ledger DB path inside a state directory."""
    return Path(state_dir) / "wake_ledger.sqlite3"


class WakeLedgerArchive:
    """Read-only archive over all governed-session wake ledgers in one DB file.

    Used by integrity/audit reconstruction; it never mutates ledger state.
    """

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def session_identities(self) -> tuple[str, ...]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT DISTINCT session_identity FROM wake_schedule ORDER BY session_identity"
            ).fetchall()
        return tuple(row["session_identity"] for row in rows)

    def schedule(self, session_identity: str) -> tuple[datetime, ...]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT close_time FROM wake_schedule WHERE session_identity=? ORDER BY seq",
                (session_identity,),
            ).fetchall()
        return tuple(_parse_dt(row["close_time"], "wake_schedule.close_time") for row in rows)

    def wakes(self, session_identity: str) -> tuple[GovernedWake, ...]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM wake_records WHERE session_identity=? ORDER BY sequence",
                (session_identity,),
            ).fetchall()
        return tuple(Fixed5MWakeLedger._wake_from_row(row) for row in rows)

    def all_wakes(self) -> tuple[GovernedWake, ...]:
        with closing(self._connect()) as connection:
            rows = connection.execute("SELECT * FROM wake_records ORDER BY sequence").fetchall()
        return tuple(Fixed5MWakeLedger._wake_from_row(row) for row in rows)

    def bindings(self, session_identity: str) -> tuple[WakeBinding, ...]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM wake_bindings WHERE session_identity=? ORDER BY wake_identity",
                (session_identity,),
            ).fetchall()
        return tuple(
            WakeBinding(
                wake_identity=row["wake_identity"],
                request_id=row["request_id"],
                session_identity=row["session_identity"],
                bound_at=_parse_dt(row["bound_at"], "wake_bindings.bound_at"),
                retry_count=int(row["retry_count"]),
            )
            for row in rows
        )

    def all_bindings(self) -> tuple[WakeBinding, ...]:
        with closing(self._connect()) as connection:
            rows = connection.execute("SELECT * FROM wake_bindings ORDER BY wake_identity").fetchall()
        return tuple(
            WakeBinding(
                wake_identity=row["wake_identity"],
                request_id=row["request_id"],
                session_identity=row["session_identity"],
                bound_at=_parse_dt(row["bound_at"], "wake_bindings.bound_at"),
                retry_count=int(row["retry_count"]),
            )
            for row in rows
        )

    def portable_export(self) -> dict[str, Any]:
        """Complete read-only dump of every governed session in the archive."""
        sessions: list[dict[str, Any]] = []
        for session in self.session_identities():
            sessions.append(
                {
                    "session_identity": session,
                    "schedule_5m_closes": [
                        _iso(item) for item in self.schedule(session)
                    ],
                    "wakes": [
                        {
                            "sequence": wake.sequence,
                            "wake_identity": wake.wake_identity,
                            "close_time": _iso(wake.close_time),
                            "scheduled_close_time": _iso(wake.scheduled_close_time),
                            "request_id": wake.request_id,
                            "retry_count": wake.retry_count,
                            "trader_identity": wake.trader_identity,
                        }
                        for wake in self.wakes(session)
                    ],
                    "bindings": [
                        {
                            "wake_identity": binding.wake_identity,
                            "request_id": binding.request_id,
                            "retry_count": binding.retry_count,
                        }
                        for binding in self.bindings(session)
                    ],
                }
            )
        return {
            "wake_ledger_version": WAKE_LEDGER_VERSION,
            "schema_version": WAKE_LEDGER_SCHEMA_VERSION,
            "sessions": sessions,
        }


def default_session_schedule_5m(closes: Iterable[datetime]) -> tuple[datetime, ...]:
    """Normalize a governed session's expected closed-5m-bar times."""
    return tuple(closes)


__all__ = [
    "FIVE_MINUTES",
    "Fixed5MWakeLedger",
    "GovernedWake",
    "WAKE_LEDGER_SCHEMA_VERSION",
    "WAKE_LEDGER_VERSION",
    "WakeBinding",
    "WakeLedgerArchive",
    "default_session_schedule_5m",
    "wake_ledger_path_for",
]

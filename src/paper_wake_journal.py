"""Durable realtime 5m wake journal for future PAPER operation.

This module performs no provider, broker, account or network action.  It records
project-owned realtime wake state so restart/reconnect cannot silently dispatch
the same admitted closed-5m wake twice.

The key fail-closed boundary is ``DISPATCH_STARTED``: once persisted, a crash is
not interpreted as "the model was never asked".  The wake remains unresolved
until separate evidence proves a committed decision or an explicit adjudication
handles the unknown attempt.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

PAPER_WAKE_JOURNAL_SCHEMA_VERSION = "KPE_PAPER_WAKE_JOURNAL_V0_1"
OBSERVED = "OBSERVED"
DISPATCH_STARTED = "DISPATCH_STARTED"
DECISION_COMMITTED = "DECISION_COMMITTED"
SKIPPED = "SKIPPED"
_ALLOWED = frozenset({OBSERVED, DISPATCH_STARTED, DECISION_COMMITTED, SKIPPED})


def _iso(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("paper wake timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")


def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("paper wake journal persisted a naive timestamp")
    return parsed


@dataclass(frozen=True)
class PaperWakeRecord:
    wake_identity: str
    trader_identity: str
    concrete_contract_id: str
    bar_identity: str
    bar_start: datetime
    bar_end: datetime
    observed_at: datetime
    status: str
    request_id: str | None
    decision_identity: str | None
    safe_reason: str | None
    updated_at: datetime


class PaperWakeJournal:
    """SQLite-backed idempotency owner for realtime PAPER cognition wakes."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._initialize()

    def _initialize(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS paper_wakes (
                wake_identity TEXT PRIMARY KEY,
                trader_identity TEXT NOT NULL,
                concrete_contract_id TEXT NOT NULL,
                bar_identity TEXT NOT NULL UNIQUE,
                bar_start TEXT NOT NULL,
                bar_end TEXT NOT NULL,
                observed_at TEXT NOT NULL,
                status TEXT NOT NULL,
                request_id TEXT,
                decision_identity TEXT,
                safe_reason TEXT,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS paper_wake_status_idx
                ON paper_wakes(status, bar_end, wake_identity);
            """
        )
        existing = self._connection.execute(
            "SELECT value FROM metadata WHERE key='schema_version'"
        ).fetchone()
        if existing is not None and existing[0] != PAPER_WAKE_JOURNAL_SCHEMA_VERSION:
            raise ValueError("unsupported paper wake journal schema")
        self._connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES('schema_version', ?)",
            (PAPER_WAKE_JOURNAL_SCHEMA_VERSION,),
        )
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "PaperWakeJournal":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def observe(
        self,
        *,
        wake_identity: str,
        trader_identity: str,
        concrete_contract_id: str,
        bar_identity: str,
        bar_start: datetime,
        bar_end: datetime,
        observed_at: datetime,
    ) -> PaperWakeRecord:
        values = (wake_identity, trader_identity, concrete_contract_id, bar_identity)
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError("paper wake observation requires complete non-empty identities")
        if bar_start.tzinfo is None or bar_end.tzinfo is None or observed_at.tzinfo is None:
            raise ValueError("paper wake observation timestamps must be timezone-aware")
        if bar_end <= bar_start:
            raise ValueError("paper wake bar end must follow bar start")
        if observed_at < bar_end:
            raise ValueError("paper wake cannot observe an unfinished bar")

        existing_wake = self._connection.execute(
            "SELECT * FROM paper_wakes WHERE wake_identity=?", (wake_identity,)
        ).fetchone()
        existing_bar = self._connection.execute(
            "SELECT * FROM paper_wakes WHERE bar_identity=?", (bar_identity,)
        ).fetchone()
        if existing_wake is not None or existing_bar is not None:
            if existing_wake is None or existing_bar is None:
                raise ValueError("PAPER_WAKE_IDENTITY_CONFLICT")
            if existing_wake["wake_identity"] != existing_bar["wake_identity"]:
                raise ValueError("PAPER_WAKE_IDENTITY_CONFLICT")
            record = self._from_row(existing_wake)
            if (
                record.trader_identity != trader_identity
                or record.concrete_contract_id != concrete_contract_id
                or record.bar_identity != bar_identity
                or record.bar_start != bar_start.astimezone(timezone.utc)
                or record.bar_end != bar_end.astimezone(timezone.utc)
            ):
                raise ValueError("PAPER_WAKE_IDENTITY_CONFLICT")
            return record

        observed_text = _iso(observed_at)
        self._connection.execute(
            """
            INSERT INTO paper_wakes(
                wake_identity, trader_identity, concrete_contract_id, bar_identity,
                bar_start, bar_end, observed_at, status, request_id,
                decision_identity, safe_reason, updated_at
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?)
            """,
            (
                wake_identity,
                trader_identity,
                concrete_contract_id,
                bar_identity,
                _iso(bar_start),
                _iso(bar_end),
                observed_text,
                OBSERVED,
                observed_text,
            ),
        )
        self._connection.commit()
        return self.get(wake_identity)

    def mark_dispatch_started(
        self, wake_identity: str, *, request_id: str, at: datetime
    ) -> PaperWakeRecord:
        if not isinstance(request_id, str) or not request_id.strip():
            raise ValueError("paper wake dispatch requires a non-empty request id")
        return self._transition(
            wake_identity,
            expected=(OBSERVED,),
            new_status=DISPATCH_STARTED,
            at=at,
            request_id=request_id,
        )

    def mark_decision_committed(
        self, wake_identity: str, *, decision_identity: str, at: datetime
    ) -> PaperWakeRecord:
        if not isinstance(decision_identity, str) or not decision_identity.strip():
            raise ValueError("paper wake committed decision identity must be non-empty")
        return self._transition(
            wake_identity,
            expected=(DISPATCH_STARTED,),
            new_status=DECISION_COMMITTED,
            at=at,
            decision_identity=decision_identity,
        )

    def mark_skipped(
        self, wake_identity: str, *, safe_reason: str, at: datetime
    ) -> PaperWakeRecord:
        if not isinstance(safe_reason, str) or not safe_reason.strip():
            raise ValueError("paper wake skip requires a non-empty safe reason")
        return self._transition(
            wake_identity,
            expected=(OBSERVED,),
            new_status=SKIPPED,
            at=at,
            safe_reason=safe_reason,
        )

    def unresolved_dispatches(self) -> tuple[PaperWakeRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM paper_wakes WHERE status=? ORDER BY bar_end, wake_identity",
            (DISPATCH_STARTED,),
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def pending_observations(self) -> tuple[PaperWakeRecord, ...]:
        rows = self._connection.execute(
            "SELECT * FROM paper_wakes WHERE status=? ORDER BY bar_end, wake_identity",
            (OBSERVED,),
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def has_bar(self, bar_identity: str) -> bool:
        row = self._connection.execute(
            "SELECT 1 FROM paper_wakes WHERE bar_identity=?", (bar_identity,)
        ).fetchone()
        return row is not None

    def total_count(self) -> int:
        """Read-only total durable wake count (restart preservation)."""
        row = self._connection.execute(
            "SELECT COUNT(*) AS count FROM paper_wakes"
        ).fetchone()
        return int(row["count"])

    def get(self, wake_identity: str) -> PaperWakeRecord:
        row = self._connection.execute(
            "SELECT * FROM paper_wakes WHERE wake_identity=?", (wake_identity,)
        ).fetchone()
        if row is None:
            raise KeyError(wake_identity)
        return self._from_row(row)

    def _transition(
        self,
        wake_identity: str,
        *,
        expected: tuple[str, ...],
        new_status: str,
        at: datetime,
        request_id: str | None = None,
        decision_identity: str | None = None,
        safe_reason: str | None = None,
    ) -> PaperWakeRecord:
        if new_status not in _ALLOWED:
            raise ValueError("unknown paper wake journal status")
        row = self.get(wake_identity)
        if row.status not in expected:
            raise RuntimeError(
                f"PAPER_WAKE_ILLEGAL_TRANSITION:{row.status}->{new_status}"
            )
        self._connection.execute(
            """
            UPDATE paper_wakes
            SET status=?,
                request_id=COALESCE(?, request_id),
                decision_identity=COALESCE(?, decision_identity),
                safe_reason=COALESCE(?, safe_reason),
                updated_at=?
            WHERE wake_identity=?
            """,
            (
                new_status,
                request_id,
                decision_identity,
                safe_reason,
                _iso(at),
                wake_identity,
            ),
        )
        self._connection.commit()
        return self.get(wake_identity)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> PaperWakeRecord:
        status = row["status"]
        if status not in _ALLOWED:
            raise ValueError("paper wake journal contains unknown status")
        return PaperWakeRecord(
            wake_identity=row["wake_identity"],
            trader_identity=row["trader_identity"],
            concrete_contract_id=row["concrete_contract_id"],
            bar_identity=row["bar_identity"],
            bar_start=_parse(row["bar_start"]),
            bar_end=_parse(row["bar_end"]),
            observed_at=_parse(row["observed_at"]),
            status=status,
            request_id=row["request_id"],
            decision_identity=row["decision_identity"],
            safe_reason=row["safe_reason"],
            updated_at=_parse(row["updated_at"]),
        )

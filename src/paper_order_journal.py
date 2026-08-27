"""Durable idempotency journal for future external PAPER orders.

The journal commits ATTEMPT_STARTED before any caller is permitted to invoke the
external broker. A process crash after that point is conservatively recoverable
as an unresolved/unknown attempted submission rather than "not sent".
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

PAPER_ORDER_JOURNAL_SCHEMA_VERSION = "KPE_PAPER_ORDER_JOURNAL_V0_1"
PREPARED = "PREPARED"
ATTEMPT_STARTED = "ATTEMPT_STARTED"
BROKER_ORDER_ID_KNOWN = "BROKER_ORDER_ID_KNOWN"
UNKNOWN_AFTER_SUBMIT = "UNKNOWN_AFTER_SUBMIT"
TERMINAL = "TERMINAL"
_ALLOWED = frozenset({PREPARED, ATTEMPT_STARTED, BROKER_ORDER_ID_KNOWN, UNKNOWN_AFTER_SUBMIT, TERMINAL})

def _iso(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("journal timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")

def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("journal persisted an invalid naive timestamp")
    return parsed

@dataclass(frozen=True)
class PaperOrderAttempt:
    client_request_id: str
    trader_identity: str
    wake_identity: str
    decision_identity: str
    intent_identity: str
    risk_identity: str
    concrete_contract_id: str
    execution_mode: str
    status: str
    broker_order_id: str | None
    prepared_at: datetime
    updated_at: datetime
    safe_reason: str | None

class PaperOrderJournal:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._initialize()

    def _initialize(self) -> None:
        self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY, value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS order_attempts (
                client_request_id TEXT PRIMARY KEY,
                trader_identity TEXT NOT NULL,
                wake_identity TEXT NOT NULL,
                decision_identity TEXT NOT NULL,
                intent_identity TEXT NOT NULL UNIQUE,
                risk_identity TEXT NOT NULL,
                concrete_contract_id TEXT NOT NULL,
                execution_mode TEXT NOT NULL,
                status TEXT NOT NULL,
                broker_order_id TEXT,
                prepared_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                safe_reason TEXT
            );
            CREATE UNIQUE INDEX IF NOT EXISTS order_wake_intent_idx
                ON order_attempts(wake_identity, intent_identity);
        """)
        existing = self._connection.execute(
            "SELECT value FROM metadata WHERE key='schema_version'"
        ).fetchone()
        if existing is not None and existing[0] != PAPER_ORDER_JOURNAL_SCHEMA_VERSION:
            raise ValueError("unsupported paper order journal schema")
        self._connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES('schema_version', ?)",
            (PAPER_ORDER_JOURNAL_SCHEMA_VERSION,),
        )
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()
    def __enter__(self) -> "PaperOrderJournal":
        return self
    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def prepare(self, *, client_request_id: str, trader_identity: str, wake_identity: str,
                decision_identity: str, intent_identity: str, risk_identity: str,
                concrete_contract_id: str, prepared_at: datetime) -> PaperOrderAttempt:
        values = (client_request_id, trader_identity, wake_identity, decision_identity,
                  intent_identity, risk_identity, concrete_contract_id)
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError("paper order prepare requires complete non-empty identities")
        at = _iso(prepared_at)
        try:
            self._connection.execute("""
                INSERT INTO order_attempts(
                    client_request_id, trader_identity, wake_identity,
                    decision_identity, intent_identity, risk_identity,
                    concrete_contract_id, execution_mode, status,
                    broker_order_id, prepared_at, updated_at, safe_reason
                ) VALUES(?, ?, ?, ?, ?, ?, ?, 'PAPER', ?, NULL, ?, ?, NULL)
            """, (client_request_id, trader_identity, wake_identity, decision_identity,
                    intent_identity, risk_identity, concrete_contract_id, PREPARED, at, at))
            self._connection.commit()
        except sqlite3.IntegrityError as error:
            raise ValueError("DUPLICATE_PAPER_ORDER_IDENTITY") from error
        return self.get(client_request_id)

    def mark_attempt_started(self, client_request_id: str, *, at: datetime) -> PaperOrderAttempt:
        return self._transition(client_request_id, expected=(PREPARED,),
                                new_status=ATTEMPT_STARTED, at=at)

    def mark_broker_order_known(self, client_request_id: str, *, broker_order_id: str,
                                at: datetime) -> PaperOrderAttempt:
        if not isinstance(broker_order_id, str) or not broker_order_id.strip():
            raise ValueError("broker order id must be non-empty")
        return self._transition(client_request_id, expected=(ATTEMPT_STARTED,),
                                new_status=BROKER_ORDER_ID_KNOWN, at=at,
                                broker_order_id=broker_order_id)

    def mark_unknown_after_submit(self, client_request_id: str, *, safe_reason: str,
                                  at: datetime) -> PaperOrderAttempt:
        if not isinstance(safe_reason, str) or not safe_reason.strip():
            raise ValueError("unknown submission requires a safe non-secret reason")
        return self._transition(client_request_id, expected=(ATTEMPT_STARTED,),
                                new_status=UNKNOWN_AFTER_SUBMIT, at=at,
                                safe_reason=safe_reason)

    def mark_terminal(self, client_request_id: str, *, safe_reason: str,
                      at: datetime) -> PaperOrderAttempt:
        if not isinstance(safe_reason, str) or not safe_reason.strip():
            raise ValueError("terminal order requires a safe reason")
        return self._transition(client_request_id,
                                expected=(BROKER_ORDER_ID_KNOWN, UNKNOWN_AFTER_SUBMIT),
                                new_status=TERMINAL, at=at, safe_reason=safe_reason)

    def unresolved_attempts(self) -> tuple[PaperOrderAttempt, ...]:
        rows = self._connection.execute(
            "SELECT * FROM order_attempts WHERE status IN (?, ?) ORDER BY prepared_at, client_request_id",
            (ATTEMPT_STARTED, UNKNOWN_AFTER_SUBMIT),
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def expected_client_request_ids(self) -> tuple[str, ...]:
        rows = self._connection.execute(
            "SELECT client_request_id FROM order_attempts ORDER BY client_request_id"
        ).fetchall()
        return tuple(row[0] for row in rows)

    def get(self, client_request_id: str) -> PaperOrderAttempt:
        row = self._connection.execute(
            "SELECT * FROM order_attempts WHERE client_request_id=?", (client_request_id,)
        ).fetchone()
        if row is None:
            raise KeyError(client_request_id)
        return self._from_row(row)

    def _transition(self, client_request_id: str, *, expected: tuple[str, ...],
                    new_status: str, at: datetime, broker_order_id: str | None = None,
                    safe_reason: str | None = None) -> PaperOrderAttempt:
        if new_status not in _ALLOWED:
            raise ValueError("unknown paper order journal status")
        row = self.get(client_request_id)
        if row.status not in expected:
            raise RuntimeError(f"PAPER_ORDER_ILLEGAL_TRANSITION:{row.status}->{new_status}")
        self._connection.execute("""
            UPDATE order_attempts
            SET status=?, broker_order_id=COALESCE(?, broker_order_id),
                updated_at=?, safe_reason=COALESCE(?, safe_reason)
            WHERE client_request_id=?
        """, (new_status, broker_order_id, _iso(at), safe_reason, client_request_id))
        self._connection.commit()
        return self.get(client_request_id)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> PaperOrderAttempt:
        status = row["status"]
        if status not in _ALLOWED:
            raise ValueError("paper order journal contains unknown status")
        return PaperOrderAttempt(
            client_request_id=row["client_request_id"], trader_identity=row["trader_identity"],
            wake_identity=row["wake_identity"], decision_identity=row["decision_identity"],
            intent_identity=row["intent_identity"], risk_identity=row["risk_identity"],
            concrete_contract_id=row["concrete_contract_id"], execution_mode=row["execution_mode"],
            status=status, broker_order_id=row["broker_order_id"],
            prepared_at=_parse(row["prepared_at"]), updated_at=_parse(row["updated_at"]),
            safe_reason=row["safe_reason"],
        )

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

from decimal import Decimal, InvalidOperation

from src.broker_adapter import BrokerOrderInstruction, canonical_decimal

PAPER_ORDER_JOURNAL_SCHEMA_VERSION = "KPE_PAPER_ORDER_JOURNAL_V0_4"
PREPARED = "PREPARED"
ATTEMPT_STARTED = "ATTEMPT_STARTED"
BROKER_ORDER_ID_KNOWN = "BROKER_ORDER_ID_KNOWN"
UNKNOWN_AFTER_SUBMIT = "UNKNOWN_AFTER_SUBMIT"
UNKNOWN_BROKER_ORDER = "UNKNOWN_BROKER_ORDER"
TERMINAL = "TERMINAL"
_ORDER_STATUSES = frozenset({
    PREPARED, ATTEMPT_STARTED, BROKER_ORDER_ID_KNOWN, UNKNOWN_AFTER_SUBMIT,
    UNKNOWN_BROKER_ORDER, TERMINAL,
})

CANCEL_PREPARED = "CANCEL_PREPARED"
CANCEL_ATTEMPT_STARTED = "CANCEL_ATTEMPT_STARTED"
CANCEL_RESOLVED = "CANCEL_RESOLVED"
UNKNOWN_CANCEL = "UNKNOWN_CANCEL"
_CANCEL_STATUSES = frozenset({
    CANCEL_PREPARED, CANCEL_ATTEMPT_STARTED, CANCEL_RESOLVED, UNKNOWN_CANCEL,
})

REPLACE_WAITING_FOR_CANCEL = "REPLACE_WAITING_FOR_CANCEL"
REPLACE_CHILD_SUBMIT_AUTHORIZED = "REPLACE_CHILD_SUBMIT_AUTHORIZED"
REPLACE_CHILD_SUBMIT_ATTEMPT_STARTED = "REPLACE_CHILD_SUBMIT_ATTEMPT_STARTED"
REPLACE_RESOLVED = "REPLACE_RESOLVED"
UNKNOWN_REPLACE = "UNKNOWN_REPLACE"
_REPLACE_STATUSES = frozenset({
    REPLACE_WAITING_FOR_CANCEL, REPLACE_CHILD_SUBMIT_AUTHORIZED,
    REPLACE_CHILD_SUBMIT_ATTEMPT_STARTED, REPLACE_RESOLVED, UNKNOWN_REPLACE,
})

_SAFE_TERMINAL_ORDER_STATUSES = frozenset({"CANCELLED", "FILLED", "REJECTED"})

def _iso(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("journal timestamp must be timezone-aware")
    return value.astimezone(timezone.utc).isoformat(timespec="microseconds")

def _parse(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError("journal persisted an invalid naive timestamp")
    return parsed


def _optional_decimal(value: str | None) -> Decimal | None:
    if value is None:
        return None
    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError) as error:
        raise ValueError("paper order journal persisted an invalid Decimal") from error
    if not parsed.is_finite():
        raise ValueError("paper order journal persisted a non-finite Decimal")
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
    expected_direction: str | None
    expected_action: str | None
    expected_quantity: str | None
    expected_order_type: str | None
    expected_limit_price: str | None
    expected_trigger_price: str | None
    expected_order_role: str | None
    expected_strategy_identity: str | None
    expected_client_order_id: str | None
    expected_parent_order_id: str | None
    expected_oco_group_id: str | None
    expected_replace_generation: int | None
    expected_source_directive_identity: str | None
    execution_mode: str
    status: str
    broker_order_id: str | None
    prepared_at: datetime
    updated_at: datetime
    safe_reason: str | None
    broker_terminal_status: str | None
    broker_filled_quantity: str | None
    broker_snapshot_at: datetime | None


@dataclass(frozen=True)
class PaperCancelAttempt:
    cancel_operation_id: str
    client_request_id: str
    broker_order_id: str
    status: str
    final_order_status: str | None
    prepared_at: datetime
    updated_at: datetime
    safe_reason: str | None


@dataclass(frozen=True)
class PaperReplaceOperation:
    replace_operation_id: str
    original_client_request_id: str
    replacement_generation: int
    replacement_intent_identity: str
    cancel_operation_id: str
    child_client_request_id: str
    status: str
    prepared_at: datetime
    updated_at: datetime
    safe_reason: str | None

class PaperOrderJournal:
    def __init__(self, path: str | Path, *, require_full_envelope: bool = False) -> None:
        if type(require_full_envelope) is not bool:
            raise ValueError("paper order journal envelope requirement must be bool")
        self.require_full_envelope = require_full_envelope
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        self._connection.execute("PRAGMA journal_mode = WAL")
        self._connection.execute("PRAGMA synchronous = FULL")
        self._connection.execute("PRAGMA busy_timeout = 5000")
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
                expected_direction TEXT,
                expected_action TEXT,
                expected_quantity TEXT,
                expected_order_type TEXT,
                expected_limit_price TEXT,
                expected_trigger_price TEXT,
                expected_order_role TEXT,
                expected_strategy_identity TEXT,
                expected_client_order_id TEXT,
                expected_parent_order_id TEXT,
                expected_oco_group_id TEXT,
                expected_replace_generation INTEGER,
                expected_source_directive_identity TEXT,
                execution_mode TEXT NOT NULL,
                status TEXT NOT NULL,
                broker_order_id TEXT,
                prepared_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                safe_reason TEXT,
                broker_terminal_status TEXT,
                broker_filled_quantity TEXT,
                broker_snapshot_at TEXT
            );
            CREATE UNIQUE INDEX IF NOT EXISTS order_wake_intent_idx
                ON order_attempts(wake_identity, intent_identity);
            CREATE TABLE IF NOT EXISTS cancel_attempts (
                cancel_operation_id TEXT PRIMARY KEY,
                client_request_id TEXT NOT NULL REFERENCES order_attempts(client_request_id),
                broker_order_id TEXT NOT NULL,
                status TEXT NOT NULL,
                final_order_status TEXT,
                prepared_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                safe_reason TEXT,
                UNIQUE(client_request_id, broker_order_id)
            );
            CREATE TABLE IF NOT EXISTS replace_operations (
                replace_operation_id TEXT PRIMARY KEY,
                original_client_request_id TEXT NOT NULL REFERENCES order_attempts(client_request_id),
                replacement_generation INTEGER NOT NULL,
                replacement_intent_identity TEXT NOT NULL UNIQUE,
                cancel_operation_id TEXT NOT NULL REFERENCES cancel_attempts(cancel_operation_id),
                child_client_request_id TEXT NOT NULL UNIQUE REFERENCES order_attempts(client_request_id),
                status TEXT NOT NULL,
                prepared_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                safe_reason TEXT,
                UNIQUE(original_client_request_id, replacement_generation)
            );
        """)
        # V0.1/V0.2 journals may exist from an interrupted offline drill.  Their
        # order envelopes are unknowable, so recovery will fail closed below.
        existing_columns = {
            row[1] for row in self._connection.execute("PRAGMA table_info(order_attempts)")
        }
        for column, definition in (
            ("expected_direction", "TEXT"),
            ("expected_action", "TEXT"),
            ("expected_quantity", "TEXT"),
            ("expected_order_type", "TEXT"),
            ("expected_limit_price", "TEXT"),
            ("expected_trigger_price", "TEXT"),
            ("expected_order_role", "TEXT"),
            ("expected_strategy_identity", "TEXT"),
            ("expected_client_order_id", "TEXT"),
            ("expected_parent_order_id", "TEXT"),
            ("expected_oco_group_id", "TEXT"),
            ("expected_replace_generation", "INTEGER"),
            ("expected_source_directive_identity", "TEXT"),
            ("broker_terminal_status", "TEXT"),
            ("broker_filled_quantity", "TEXT"),
            ("broker_snapshot_at", "TEXT"),
        ):
            if column not in existing_columns:
                self._connection.execute(
                    f"ALTER TABLE order_attempts ADD COLUMN {column} {definition}"
                )
        existing = self._connection.execute(
            "SELECT value FROM metadata WHERE key='schema_version'"
        ).fetchone()
        if existing is not None and existing[0] not in (
            "KPE_PAPER_ORDER_JOURNAL_V0_1", "KPE_PAPER_ORDER_JOURNAL_V0_2",
            "KPE_PAPER_ORDER_JOURNAL_V0_3",
            PAPER_ORDER_JOURNAL_SCHEMA_VERSION,
        ):
            raise ValueError("unsupported paper order journal schema")
        self._connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES('schema_version', ?)",
            (PAPER_ORDER_JOURNAL_SCHEMA_VERSION,),
        )
        self._connection.commit()

    def close(self) -> None:
        self._connection.execute("PRAGMA wal_checkpoint(FULL)")
        self._connection.close()
    def __enter__(self) -> "PaperOrderJournal":
        return self
    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def total_count(self) -> int:
        """Read-only total durable order-attempt count (restart preservation)."""
        row = self._connection.execute(
            "SELECT COUNT(*) AS count FROM order_attempts"
        ).fetchone()
        return int(row["count"])

    def prepare(self, *, client_request_id: str, trader_identity: str, wake_identity: str,
                decision_identity: str, intent_identity: str, risk_identity: str,
                concrete_contract_id: str, instruction: BrokerOrderInstruction,
                prepared_at: datetime) -> PaperOrderAttempt:
        values = (client_request_id, trader_identity, wake_identity, decision_identity,
                  intent_identity, risk_identity, concrete_contract_id)
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError("paper order prepare requires complete non-empty identities")
        if not isinstance(instruction, BrokerOrderInstruction):
            raise ValueError("paper order prepare requires BrokerOrderInstruction")
        if (instruction.client_request_id != client_request_id or
                instruction.concrete_contract_id != concrete_contract_id):
            raise ValueError("PAPER_ORDER_PREPARE_INSTRUCTION_IDENTITY_MISMATCH")
        at = _iso(prepared_at)
        try:
            self._connection.execute("""
                INSERT INTO order_attempts(
                    client_request_id, trader_identity, wake_identity,
                    decision_identity, intent_identity, risk_identity,
                    concrete_contract_id, expected_direction, expected_action,
                    expected_quantity, expected_order_type, expected_limit_price,
                    expected_trigger_price, expected_order_role,
                    expected_strategy_identity, expected_client_order_id,
                    expected_parent_order_id, expected_oco_group_id,
                    expected_replace_generation, expected_source_directive_identity,
                    execution_mode, status, broker_order_id, prepared_at, updated_at,
                    safe_reason, broker_terminal_status, broker_filled_quantity,
                    broker_snapshot_at
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                         'PAPER', ?, NULL, ?, ?, NULL, NULL, NULL, NULL)
            """, (client_request_id, trader_identity, wake_identity, decision_identity,
                    intent_identity, risk_identity, concrete_contract_id,
                    instruction.direction.value, instruction.action.value,
                    canonical_decimal(instruction.quantity), instruction.order_type.value,
                    None if instruction.limit_price is None else canonical_decimal(instruction.limit_price),
                    None if instruction.trigger_price is None else canonical_decimal(instruction.trigger_price),
                    instruction.order_role.value, instruction.strategy_identity_id,
                    instruction.client_order_id or instruction.client_request_id,
                    instruction.parent_order_id, instruction.oco_group_id,
                    instruction.replace_generation, instruction.source_directive_identity,
                    PREPARED, at, at))
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
        return self._transition(client_request_id, expected=(ATTEMPT_STARTED, UNKNOWN_AFTER_SUBMIT,
                                                            UNKNOWN_BROKER_ORDER),
                                new_status=BROKER_ORDER_ID_KNOWN, at=at,
                                broker_order_id=broker_order_id)

    def mark_unknown_after_submit(self, client_request_id: str, *, safe_reason: str,
                                  at: datetime) -> PaperOrderAttempt:
        if not isinstance(safe_reason, str) or not safe_reason.strip():
            raise ValueError("unknown submission requires a safe non-secret reason")
        return self._transition(client_request_id, expected=(ATTEMPT_STARTED,),
                                new_status=UNKNOWN_AFTER_SUBMIT, at=at,
                                safe_reason=safe_reason)

    def mark_terminal(
        self,
        client_request_id: str,
        *,
        terminal_status: str,
        filled_quantity: Decimal,
        broker_snapshot_at: datetime,
        safe_reason: str,
        at: datetime,
    ) -> PaperOrderAttempt:
        if not isinstance(safe_reason, str) or not safe_reason.strip():
            raise ValueError("terminal order requires a safe reason")
        if terminal_status not in _SAFE_TERMINAL_ORDER_STATUSES:
            raise ValueError("terminal order status must be broker-confirmed")
        if type(filled_quantity) is not Decimal or not filled_quantity.is_finite() or filled_quantity < 0:
            raise ValueError("terminal filled quantity must be non-negative finite Decimal")
        _iso(broker_snapshot_at)
        return self._transition(
            client_request_id,
            expected=(BROKER_ORDER_ID_KNOWN, UNKNOWN_AFTER_SUBMIT, UNKNOWN_BROKER_ORDER),
            new_status=TERMINAL,
            at=at,
            safe_reason=safe_reason,
            broker_terminal_status=terminal_status,
            broker_filled_quantity=canonical_decimal(filled_quantity),
            broker_snapshot_at=broker_snapshot_at,
        )

    def mark_unknown_broker_order(self, client_request_id: str, *, safe_reason: str,
                                  at: datetime) -> PaperOrderAttempt:
        """Persist that a formerly known order cannot be reconciled to broker truth.

        A missing broker snapshot is deliberately not interpreted as proof that an
        attempted mutation did not happen.  This state must be recovered from a
        later authoritative snapshot before another risk-increasing mutation.
        """
        if not isinstance(safe_reason, str) or not safe_reason.strip():
            raise ValueError("unknown broker order requires a safe non-secret reason")
        return self._transition(
            client_request_id,
            expected=(ATTEMPT_STARTED, UNKNOWN_AFTER_SUBMIT, BROKER_ORDER_ID_KNOWN),
            new_status=UNKNOWN_BROKER_ORDER,
            at=at,
            safe_reason=safe_reason,
        )

    def unresolved_attempts(self) -> tuple[PaperOrderAttempt, ...]:
        rows = self._connection.execute(
            "SELECT * FROM order_attempts WHERE status IN (?, ?, ?) ORDER BY prepared_at, client_request_id",
            (ATTEMPT_STARTED, UNKNOWN_AFTER_SUBMIT, UNKNOWN_BROKER_ORDER),
        ).fetchall()
        return tuple(self._from_row(row) for row in rows)

    def prepare_cancel(self, *, cancel_operation_id: str, client_request_id: str,
                       broker_order_id: str, prepared_at: datetime) -> PaperCancelAttempt:
        """Create one deterministic cancel operation without performing a cancel."""
        values = (cancel_operation_id, client_request_id, broker_order_id)
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError("paper cancel prepare requires complete non-empty identities")
        order = self.get(client_request_id)
        if order.status != BROKER_ORDER_ID_KNOWN or order.broker_order_id != broker_order_id:
            raise RuntimeError("PAPER_CANCEL_REQUIRES_KNOWN_BROKER_ORDER")
        at = _iso(prepared_at)
        existing = self._connection.execute(
            "SELECT * FROM cancel_attempts WHERE cancel_operation_id=?", (cancel_operation_id,)
        ).fetchone()
        if existing is not None:
            record = self._cancel_from_row(existing)
            if record.client_request_id != client_request_id or record.broker_order_id != broker_order_id:
                raise ValueError("PAPER_CANCEL_IDENTITY_CONFLICT")
            return record
        try:
            self._connection.execute("""
                INSERT INTO cancel_attempts(
                    cancel_operation_id, client_request_id, broker_order_id, status,
                    final_order_status, prepared_at, updated_at, safe_reason
                ) VALUES (?, ?, ?, ?, NULL, ?, ?, NULL)
            """, (cancel_operation_id, client_request_id, broker_order_id,
                  CANCEL_PREPARED, at, at))
            self._connection.commit()
        except sqlite3.IntegrityError as error:
            raise ValueError("DUPLICATE_PAPER_CANCEL_IDENTITY") from error
        return self.get_cancel(cancel_operation_id)

    def prepare_cancel_for_broker_order(self, broker_order_id: str, *, at: datetime) -> PaperCancelAttempt:
        if not isinstance(broker_order_id, str) or not broker_order_id.strip():
            raise ValueError("paper cancel requires a non-empty broker order id")
        rows = self._connection.execute(
            "SELECT * FROM order_attempts WHERE broker_order_id=?", (broker_order_id,)
        ).fetchall()
        if len(rows) != 1:
            raise RuntimeError("PAPER_CANCEL_ORDER_IDENTITY_UNRESOLVED")
        order = self._from_row(rows[0])
        operation_id = f"cancel:{order.client_request_id}:{broker_order_id}"
        return self.prepare_cancel(
            cancel_operation_id=operation_id,
            client_request_id=order.client_request_id,
            broker_order_id=broker_order_id,
            prepared_at=at,
        )

    def mark_cancel_attempt_started(self, cancel_operation_id: str, *, at: datetime) -> PaperCancelAttempt:
        return self._cancel_transition(
            cancel_operation_id, expected=(CANCEL_PREPARED,),
            new_status=CANCEL_ATTEMPT_STARTED, at=at,
        )

    def mark_unknown_cancel(self, cancel_operation_id: str, *, safe_reason: str,
                            at: datetime) -> PaperCancelAttempt:
        if not isinstance(safe_reason, str) or not safe_reason.strip():
            raise ValueError("unknown cancellation requires a safe non-secret reason")
        return self._cancel_transition(
            cancel_operation_id, expected=(CANCEL_ATTEMPT_STARTED,),
            new_status=UNKNOWN_CANCEL, at=at, safe_reason=safe_reason,
        )

    def resolve_cancel(self, cancel_operation_id: str, *, final_order_status: str,
                       at: datetime) -> PaperCancelAttempt:
        if final_order_status not in _SAFE_TERMINAL_ORDER_STATUSES:
            raise ValueError("cancel resolution requires an exact terminal broker order status")
        return self._cancel_transition(
            cancel_operation_id, expected=(CANCEL_ATTEMPT_STARTED, UNKNOWN_CANCEL),
            new_status=CANCEL_RESOLVED, at=at, final_order_status=final_order_status,
        )

    def unresolved_cancel_attempts(self) -> tuple[PaperCancelAttempt, ...]:
        rows = self._connection.execute(
            "SELECT * FROM cancel_attempts WHERE status IN (?, ?) ORDER BY prepared_at, cancel_operation_id",
            (CANCEL_ATTEMPT_STARTED, UNKNOWN_CANCEL),
        ).fetchall()
        return tuple(self._cancel_from_row(row) for row in rows)

    def get_cancel(self, cancel_operation_id: str) -> PaperCancelAttempt:
        row = self._connection.execute(
            "SELECT * FROM cancel_attempts WHERE cancel_operation_id=?", (cancel_operation_id,)
        ).fetchone()
        if row is None:
            raise KeyError(cancel_operation_id)
        return self._cancel_from_row(row)

    def prepare_replace(self, *, replace_operation_id: str, original_client_request_id: str,
                        replacement_generation: int, replacement_intent_identity: str,
                        cancel_operation_id: str, child_client_request_id: str,
                        prepared_at: datetime) -> PaperReplaceOperation:
        """Durably bind a cancel-then-submit replacement without authorizing its child.

        The child must already have a normal PREPARED submission journal entry.
        It stays blocked until the exact old cancel operation is broker-resolved
        as CANCELLED, preventing an uncertain old order from coexisting with a
        replacement child.
        """
        values = (replace_operation_id, original_client_request_id,
                  replacement_intent_identity, cancel_operation_id, child_client_request_id)
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError("paper replace requires complete non-empty identities")
        if type(replacement_generation) is not int or replacement_generation <= 0:
            raise ValueError("replacement generation must be a positive integer")
        original = self.get(original_client_request_id)
        child = self.get(child_client_request_id)
        cancel = self.get_cancel(cancel_operation_id)
        if original.client_request_id == child.client_request_id:
            raise ValueError("replacement child must differ from the original order")
        if child.status != PREPARED:
            raise RuntimeError("PAPER_REPLACEMENT_CHILD_MUST_BE_PREPARED")
        if cancel.client_request_id != original.client_request_id:
            raise ValueError("PAPER_REPLACE_CANCEL_ORIGINAL_MISMATCH")
        at = _iso(prepared_at)
        existing = self._connection.execute(
            "SELECT * FROM replace_operations WHERE replace_operation_id=?", (replace_operation_id,)
        ).fetchone()
        if existing is not None:
            record = self._replace_from_row(existing)
            expected = (original_client_request_id, replacement_generation,
                        replacement_intent_identity, cancel_operation_id, child_client_request_id)
            actual = (record.original_client_request_id, record.replacement_generation,
                      record.replacement_intent_identity, record.cancel_operation_id,
                      record.child_client_request_id)
            if actual != expected:
                raise ValueError("PAPER_REPLACE_IDENTITY_CONFLICT")
            return record
        try:
            self._connection.execute("""
                INSERT INTO replace_operations(
                    replace_operation_id, original_client_request_id, replacement_generation,
                    replacement_intent_identity, cancel_operation_id, child_client_request_id,
                    status, prepared_at, updated_at, safe_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL)
            """, (replace_operation_id, original_client_request_id, replacement_generation,
                  replacement_intent_identity, cancel_operation_id, child_client_request_id,
                  REPLACE_WAITING_FOR_CANCEL, at, at))
            self._connection.commit()
        except sqlite3.IntegrityError as error:
            raise ValueError("DUPLICATE_PAPER_REPLACE_IDENTITY") from error
        return self.get_replace(replace_operation_id)

    def authorize_replacement_child(self, replace_operation_id: str, *, at: datetime) -> PaperReplaceOperation:
        record = self.get_replace(replace_operation_id)
        cancel = self.get_cancel(record.cancel_operation_id)
        if record.status != REPLACE_WAITING_FOR_CANCEL:
            raise RuntimeError("PAPER_REPLACEMENT_CHILD_ALREADY_DECIDED")
        if cancel.status != CANCEL_RESOLVED or cancel.final_order_status != "CANCELLED":
            raise RuntimeError("PAPER_REPLACEMENT_CANCEL_NOT_SAFELY_RESOLVED")
        return self._replace_transition(
            replace_operation_id, expected=(REPLACE_WAITING_FOR_CANCEL,),
            new_status=REPLACE_CHILD_SUBMIT_AUTHORIZED, at=at,
        )

    def unresolved_replace_operations(self) -> tuple[PaperReplaceOperation, ...]:
        rows = self._connection.execute(
            "SELECT * FROM replace_operations WHERE status IN (?, ?, ?, ?) ORDER BY prepared_at, replace_operation_id",
            (REPLACE_WAITING_FOR_CANCEL, REPLACE_CHILD_SUBMIT_AUTHORIZED,
             REPLACE_CHILD_SUBMIT_ATTEMPT_STARTED, UNKNOWN_REPLACE),
        ).fetchall()
        return tuple(self._replace_from_row(row) for row in rows)

    def get_replace(self, replace_operation_id: str) -> PaperReplaceOperation:
        row = self._connection.execute(
            "SELECT * FROM replace_operations WHERE replace_operation_id=?", (replace_operation_id,)
        ).fetchone()
        if row is None:
            raise KeyError(replace_operation_id)
        return self._replace_from_row(row)

    def recovery_blockers(self) -> tuple[str, ...]:
        """Machine-visible NO_NEW_RISK causes already persisted in the journal."""
        reasons: list[str] = []
        for attempt in self.unresolved_attempts():
            if attempt.status == UNKNOWN_AFTER_SUBMIT:
                reasons.append("UNKNOWN_SUBMIT")
            elif attempt.status == UNKNOWN_BROKER_ORDER:
                reasons.append("UNKNOWN_BROKER_ORDER")
            else:
                reasons.append("SUBMIT_ATTEMPT_UNRESOLVED")
        if self.unresolved_cancel_attempts():
            reasons.append("UNKNOWN_CANCEL")
        if self.unresolved_replace_operations():
            reasons.append("UNKNOWN_REPLACE")
        return tuple(sorted(set(reasons)))

    def reconcile_broker_orders(self, orders: object, *, observed_at: datetime) -> tuple[str, ...]:
        """Reconcile durable attempts against one complete broker-order snapshot.

        This function performs no broker action.  It only uses supplied
        project-owned snapshots, never treats absence as proof of non-submit,
        and never authorizes a retry.  Callers must fetch account/positions/trades
        separately as required by their broker contract before declaring runtime
        recovery complete.
        """
        if not isinstance(observed_at, datetime) or observed_at.tzinfo is None or observed_at.utcoffset() is None:
            raise ValueError("broker recovery time must be timezone-aware")
        from src.broker_adapter import BrokerOrderSnapshot

        try:
            snapshots = tuple(orders)  # type: ignore[arg-type]
        except TypeError as error:
            raise ValueError("broker recovery orders must be iterable") from error
        if any(not isinstance(item, BrokerOrderSnapshot) for item in snapshots):
            raise ValueError("broker recovery requires BrokerOrderSnapshot values")
        if len({item.order_id for item in snapshots}) != len(snapshots):
            return ("DUPLICATE_BROKER_ORDER_ID",)
        by_request: dict[str, list[BrokerOrderSnapshot]] = {}
        for snapshot in snapshots:
            by_request.setdefault(snapshot.client_request_id, []).append(snapshot)
        blockers: list[str] = []
        rows = self._connection.execute("SELECT * FROM order_attempts ORDER BY prepared_at, client_request_id").fetchall()
        known_request_ids = {row["client_request_id"] for row in rows}
        if any(snapshot.client_request_id not in known_request_ids for snapshot in snapshots):
            # A broker-side order without a project identity may carry position
            # risk.  It is not ignored merely because this process did not send it.
            blockers.append("UNKNOWN_BROKER_ORDER")
        for row in rows:
            attempt = self._from_row(row)
            matches = by_request.get(attempt.client_request_id, [])
            if len(matches) > 1:
                blockers.append("ORDER_IDENTITY_MISMATCH")
                if attempt.status != PREPARED:
                    self._mark_unknown_if_needed(attempt, "DUPLICATE_BROKER_ORDER_FOR_CLIENT_REQUEST", observed_at)
                continue
            if attempt.status == PREPARED:
                if matches:
                    blockers.append("ORDER_IDENTITY_MISMATCH")
                continue
            if not matches:
                if attempt.status == TERMINAL:
                    continue
                self._mark_unknown_if_needed(attempt, "BROKER_ORDER_ABSENT_AFTER_ATTEMPT", observed_at)
                blockers.append("UNKNOWN_BROKER_ORDER")
                continue
            snapshot = matches[0]
            envelope = (
                attempt.expected_direction,
                attempt.expected_action,
                attempt.expected_quantity,
                attempt.expected_order_type,
                attempt.expected_order_role,
                attempt.expected_replace_generation,
            )
            if any(value is None for value in envelope):
                self._mark_unknown_if_needed(
                    attempt, "ORDER_ENVELOPE_MISSING", observed_at
                )
                blockers.append("ORDER_ENVELOPE_MISSING")
                continue
            optional_envelope_mismatch = (
                (snapshot.order_type is not None and snapshot.order_type.value != attempt.expected_order_type)
                or (snapshot.limit_price is not None and snapshot.limit_price != _optional_decimal(attempt.expected_limit_price))
                or (snapshot.trigger_price is not None and snapshot.trigger_price != _optional_decimal(attempt.expected_trigger_price))
                or (snapshot.order_role is not None and snapshot.order_role.value != attempt.expected_order_role)
                or (snapshot.strategy_identity_id is not None and snapshot.strategy_identity_id != attempt.expected_strategy_identity)
                or ((snapshot.client_order_id is not None) and snapshot.client_order_id != attempt.expected_client_order_id)
                or (snapshot.parent_order_id is not None and snapshot.parent_order_id != attempt.expected_parent_order_id)
                or (snapshot.oco_group_id is not None and snapshot.oco_group_id != attempt.expected_oco_group_id)
                or (snapshot.replace_generation is not None and snapshot.replace_generation != attempt.expected_replace_generation)
                or (snapshot.source_directive_identity is not None and snapshot.source_directive_identity != attempt.expected_source_directive_identity)
            )
            full_envelope_missing = self.require_full_envelope and (
                snapshot.order_type is None
                or snapshot.order_role is None
                or snapshot.client_order_id is None
                or snapshot.replace_generation is None
                or (attempt.expected_limit_price is not None and snapshot.limit_price is None)
                or (attempt.expected_trigger_price is not None and snapshot.trigger_price is None)
                or (attempt.expected_strategy_identity is not None and snapshot.strategy_identity_id is None)
                or (attempt.expected_parent_order_id is not None and snapshot.parent_order_id is None)
                or (attempt.expected_oco_group_id is not None and snapshot.oco_group_id is None)
                or (attempt.expected_source_directive_identity is not None and snapshot.source_directive_identity is None)
            )
            if (
                snapshot.concrete_contract_id != attempt.concrete_contract_id
                or snapshot.direction.value != attempt.expected_direction
                or snapshot.action.value != attempt.expected_action
                or canonical_decimal(snapshot.requested_quantity) != attempt.expected_quantity
                or optional_envelope_mismatch
                or full_envelope_missing
            ):
                self._mark_unknown_if_needed(
                    attempt, "BROKER_ORDER_ENVELOPE_MISMATCH", observed_at
                )
                blockers.append("ORDER_ENVELOPE_MISMATCH")
                continue
            if attempt.broker_order_id is not None and snapshot.order_id != attempt.broker_order_id:
                self._mark_unknown_if_needed(attempt, "BROKER_ORDER_IDENTITY_MISMATCH", observed_at)
                blockers.append("ORDER_IDENTITY_MISMATCH")
                continue
            if attempt.status in (ATTEMPT_STARTED, UNKNOWN_AFTER_SUBMIT, UNKNOWN_BROKER_ORDER):
                self.mark_broker_order_known(
                    attempt.client_request_id, broker_order_id=snapshot.order_id, at=observed_at
                )
                attempt = self.get(attempt.client_request_id)
            if snapshot.status in _SAFE_TERMINAL_ORDER_STATUSES and attempt.status != TERMINAL:
                self.mark_terminal(
                    attempt.client_request_id,
                    terminal_status=snapshot.status,
                    filled_quantity=snapshot.filled_quantity,
                    broker_snapshot_at=snapshot.snapshot_at,
                    safe_reason="BROKER_CONFIRMED_" + snapshot.status,
                    at=observed_at,
                )
        cancel_rows = self._connection.execute("SELECT * FROM cancel_attempts ORDER BY prepared_at, cancel_operation_id").fetchall()
        for row in cancel_rows:
            cancel = self._cancel_from_row(row)
            if cancel.status == CANCEL_RESOLVED:
                continue
            matching = [item for item in snapshots if item.order_id == cancel.broker_order_id]
            if len(matching) != 1:
                if cancel.status == CANCEL_ATTEMPT_STARTED:
                    self.mark_unknown_cancel(cancel.cancel_operation_id, safe_reason="CANCEL_ORDER_ABSENT_OR_DUPLICATED", at=observed_at)
                blockers.append("UNKNOWN_CANCEL")
                continue
            status = matching[0].status
            if status in _SAFE_TERMINAL_ORDER_STATUSES:
                self.resolve_cancel(cancel.cancel_operation_id, final_order_status=status, at=observed_at)
            else:
                blockers.append("UNKNOWN_CANCEL")
        return tuple(sorted(set(blockers + list(self.recovery_blockers()))))

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
                    safe_reason: str | None = None,
                    broker_terminal_status: str | None = None,
                    broker_filled_quantity: str | None = None,
                    broker_snapshot_at: datetime | None = None) -> PaperOrderAttempt:
        if new_status not in _ORDER_STATUSES:
            raise ValueError("unknown paper order journal status")
        row = self.get(client_request_id)
        if row.status not in expected:
            raise RuntimeError(f"PAPER_ORDER_ILLEGAL_TRANSITION:{row.status}->{new_status}")
        with self._connection:
            self._connection.execute("""
                UPDATE order_attempts
                SET status=?, broker_order_id=COALESCE(?, broker_order_id),
                    updated_at=?, safe_reason=COALESCE(?, safe_reason),
                    broker_terminal_status=COALESCE(?, broker_terminal_status),
                    broker_filled_quantity=COALESCE(?, broker_filled_quantity),
                    broker_snapshot_at=COALESCE(?, broker_snapshot_at)
                WHERE client_request_id=?
            """, (
                new_status, broker_order_id, _iso(at), safe_reason,
                broker_terminal_status, broker_filled_quantity,
                None if broker_snapshot_at is None else _iso(broker_snapshot_at),
                client_request_id,
            ))
            replacement = self._connection.execute(
                "SELECT * FROM replace_operations WHERE child_client_request_id=?", (client_request_id,)
            ).fetchone()
            if replacement is not None:
                operation = self._replace_from_row(replacement)
                if new_status == ATTEMPT_STARTED:
                    if operation.status != REPLACE_CHILD_SUBMIT_AUTHORIZED:
                        raise RuntimeError("PAPER_REPLACEMENT_CHILD_NOT_AUTHORIZED")
                    self._connection.execute(
                        "UPDATE replace_operations SET status=?, updated_at=? WHERE replace_operation_id=?",
                        (REPLACE_CHILD_SUBMIT_ATTEMPT_STARTED, _iso(at), operation.replace_operation_id),
                    )
                elif new_status == BROKER_ORDER_ID_KNOWN:
                    if operation.status == REPLACE_CHILD_SUBMIT_ATTEMPT_STARTED:
                        self._connection.execute(
                            "UPDATE replace_operations SET status=?, updated_at=? WHERE replace_operation_id=?",
                            (REPLACE_RESOLVED, _iso(at), operation.replace_operation_id),
                        )
                elif new_status == TERMINAL:
                    if operation.status == REPLACE_CHILD_SUBMIT_ATTEMPT_STARTED:
                        self._connection.execute(
                            "UPDATE replace_operations SET status=?, updated_at=? WHERE replace_operation_id=?",
                            (REPLACE_RESOLVED, _iso(at), operation.replace_operation_id),
                        )
                elif new_status in (UNKNOWN_AFTER_SUBMIT, UNKNOWN_BROKER_ORDER):
                    if operation.status == REPLACE_CHILD_SUBMIT_ATTEMPT_STARTED:
                        self._connection.execute(
                            "UPDATE replace_operations SET status=?, updated_at=?, safe_reason=? WHERE replace_operation_id=?",
                            (UNKNOWN_REPLACE, _iso(at), safe_reason or new_status, operation.replace_operation_id),
                        )
        return self.get(client_request_id)

    def _cancel_transition(self, cancel_operation_id: str, *, expected: tuple[str, ...],
                           new_status: str, at: datetime, final_order_status: str | None = None,
                           safe_reason: str | None = None) -> PaperCancelAttempt:
        if new_status not in _CANCEL_STATUSES:
            raise ValueError("unknown paper cancel journal status")
        record = self.get_cancel(cancel_operation_id)
        if record.status not in expected:
            raise RuntimeError(f"PAPER_CANCEL_ILLEGAL_TRANSITION:{record.status}->{new_status}")
        self._connection.execute("""
            UPDATE cancel_attempts
            SET status=?, final_order_status=COALESCE(?, final_order_status),
                updated_at=?, safe_reason=COALESCE(?, safe_reason)
            WHERE cancel_operation_id=?
        """, (new_status, final_order_status, _iso(at), safe_reason, cancel_operation_id))
        self._connection.commit()
        return self.get_cancel(cancel_operation_id)

    def _replace_transition(self, replace_operation_id: str, *, expected: tuple[str, ...],
                            new_status: str, at: datetime, safe_reason: str | None = None) -> PaperReplaceOperation:
        if new_status not in _REPLACE_STATUSES:
            raise ValueError("unknown paper replacement journal status")
        record = self.get_replace(replace_operation_id)
        if record.status not in expected:
            raise RuntimeError(f"PAPER_REPLACE_ILLEGAL_TRANSITION:{record.status}->{new_status}")
        self._connection.execute("""
            UPDATE replace_operations SET status=?, updated_at=?, safe_reason=COALESCE(?, safe_reason)
            WHERE replace_operation_id=?
        """, (new_status, _iso(at), safe_reason, replace_operation_id))
        self._connection.commit()
        return self.get_replace(replace_operation_id)

    def _mark_unknown_if_needed(self, attempt: PaperOrderAttempt, reason: str, at: datetime) -> None:
        if attempt.status in (ATTEMPT_STARTED, UNKNOWN_AFTER_SUBMIT, BROKER_ORDER_ID_KNOWN):
            self.mark_unknown_broker_order(attempt.client_request_id, safe_reason=reason, at=at)

    @staticmethod
    def _from_row(row: sqlite3.Row) -> PaperOrderAttempt:
        status = row["status"]
        if status not in _ORDER_STATUSES:
            raise ValueError("paper order journal contains unknown status")
        return PaperOrderAttempt(
            client_request_id=row["client_request_id"], trader_identity=row["trader_identity"],
            wake_identity=row["wake_identity"], decision_identity=row["decision_identity"],
            intent_identity=row["intent_identity"], risk_identity=row["risk_identity"],
            concrete_contract_id=row["concrete_contract_id"], execution_mode=row["execution_mode"],
            expected_direction=row["expected_direction"], expected_action=row["expected_action"],
            expected_quantity=row["expected_quantity"],
            expected_order_type=row["expected_order_type"],
            expected_limit_price=row["expected_limit_price"],
            expected_trigger_price=row["expected_trigger_price"],
            expected_order_role=row["expected_order_role"],
            expected_strategy_identity=row["expected_strategy_identity"],
            expected_client_order_id=row["expected_client_order_id"],
            expected_parent_order_id=row["expected_parent_order_id"],
            expected_oco_group_id=row["expected_oco_group_id"],
            expected_replace_generation=row["expected_replace_generation"],
            expected_source_directive_identity=row["expected_source_directive_identity"],
            status=status, broker_order_id=row["broker_order_id"],
            prepared_at=_parse(row["prepared_at"]), updated_at=_parse(row["updated_at"]),
            safe_reason=row["safe_reason"],
            broker_terminal_status=row["broker_terminal_status"],
            broker_filled_quantity=row["broker_filled_quantity"],
            broker_snapshot_at=(
                None if row["broker_snapshot_at"] is None else _parse(row["broker_snapshot_at"])
            ),
        )

    @staticmethod
    def _cancel_from_row(row: sqlite3.Row) -> PaperCancelAttempt:
        status = row["status"]
        if status not in _CANCEL_STATUSES:
            raise ValueError("paper cancel journal contains unknown status")
        return PaperCancelAttempt(
            cancel_operation_id=row["cancel_operation_id"],
            client_request_id=row["client_request_id"],
            broker_order_id=row["broker_order_id"],
            status=status,
            final_order_status=row["final_order_status"],
            prepared_at=_parse(row["prepared_at"]),
            updated_at=_parse(row["updated_at"]),
            safe_reason=row["safe_reason"],
        )

    @staticmethod
    def _replace_from_row(row: sqlite3.Row) -> PaperReplaceOperation:
        status = row["status"]
        if status not in _REPLACE_STATUSES:
            raise ValueError("paper replacement journal contains unknown status")
        return PaperReplaceOperation(
            replace_operation_id=row["replace_operation_id"],
            original_client_request_id=row["original_client_request_id"],
            replacement_generation=row["replacement_generation"],
            replacement_intent_identity=row["replacement_intent_identity"],
            cancel_operation_id=row["cancel_operation_id"],
            child_client_request_id=row["child_client_request_id"],
            status=status,
            prepared_at=_parse(row["prepared_at"]),
            updated_at=_parse(row["updated_at"]),
            safe_reason=row["safe_reason"],
        )

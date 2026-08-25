"""Append-only hypothesis revision history for replay V0.1.

This module writes the current hypothesis row and its immutable before/after
revision record in one SQLite transaction. It is intentionally project-owned and
Harness-independent.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable, Mapping

from src.persistent_trader_store import HYPOTHESIS_STATUSES, HypothesisRecord


HYPOTHESIS_REVISION_SCHEMA_VERSION = "KPE_DS_HYPOTHESIS_REVISION_V0_1"


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


def _parse_dt(value: str, field_name: str) -> datetime:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty ISO datetime")
    parsed = datetime.fromisoformat(value)
    return _aware(parsed, field_name)


def _validate_optional_identity(value: str | None, field_name: str) -> None:
    if value is not None and (not isinstance(value, str) or not value):
        raise ValueError(f"{field_name} must be null or a non-empty string")


def _current_payload(
    *,
    hypothesis_id: str,
    created_at: datetime,
    updated_at: datetime,
    trader_identity: str,
    statement: str,
    falsifier: str,
    status: str,
    evidence_references: tuple[str, ...],
) -> dict[str, Any]:
    payload = {
        "hypothesis_id": hypothesis_id,
        "created_at": _iso(created_at),
        "updated_at": _iso(updated_at),
        "trader_identity": trader_identity,
        "statement": statement,
        "falsifier": falsifier,
        "status": status,
        "evidence_references": evidence_references,
        "executable_policy": False,
        "semantic_class": "DS_HYPOTHESIS_MEMORY_NON_EXECUTABLE",
    }
    payload["identity"] = _hash({key: value for key, value in payload.items() if key != "identity"})
    return payload


def _row_payload(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "hypothesis_id": row["hypothesis_id"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "trader_identity": row["trader_identity"],
        "statement": row["statement"],
        "falsifier": row["falsifier"],
        "status": row["status"],
        "evidence_references": tuple(json.loads(row["evidence_references_json"])),
        "identity": row["identity"],
        "executable_policy": False,
        "semantic_class": "DS_HYPOTHESIS_MEMORY_NON_EXECUTABLE",
    }


@dataclass(frozen=True)
class HypothesisRevision:
    sequence: int
    revision_number: int
    hypothesis_id: str
    recorded_at: datetime
    trader_identity: str
    observation_identity: str | None
    request_id: str | None
    reason: str
    before_state: Mapping[str, Any] | None
    after_state: Mapping[str, Any]
    before_sha256: str | None
    after_sha256: str
    identity: str


class VersionedHypothesisLedger:
    """Atomic current-state update plus immutable hypothesis revision ledger."""

    def __init__(self, path: str | Path, *, trader_identity: str) -> None:
        if not isinstance(trader_identity, str) or not trader_identity:
            raise ValueError("trader_identity must be non-empty")
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.trader_identity = trader_identity
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS hypotheses (
                    hypothesis_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    trader_identity TEXT NOT NULL,
                    statement TEXT NOT NULL,
                    falsifier TEXT NOT NULL,
                    status TEXT NOT NULL,
                    evidence_references_json TEXT NOT NULL,
                    identity TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS hypothesis_revisions (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    revision_number INTEGER NOT NULL,
                    hypothesis_id TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    trader_identity TEXT NOT NULL,
                    observation_identity TEXT,
                    request_id TEXT,
                    reason TEXT NOT NULL,
                    before_json TEXT,
                    after_json TEXT NOT NULL,
                    before_sha256 TEXT,
                    after_sha256 TEXT NOT NULL,
                    identity TEXT NOT NULL UNIQUE,
                    UNIQUE(hypothesis_id, revision_number)
                );
                CREATE INDEX IF NOT EXISTS hypothesis_revision_hypothesis_idx
                    ON hypothesis_revisions(hypothesis_id, revision_number);
                """
            )

    def put(
        self,
        *,
        hypothesis_id: str,
        occurred_at: datetime,
        statement: str,
        falsifier: str,
        status: str = "CANDIDATE",
        evidence_references: Iterable[str] = (),
        observation_identity: str | None = None,
        request_id: str | None = None,
        reason: str,
    ) -> tuple[HypothesisRecord, HypothesisRevision]:
        if not hypothesis_id or not statement or not falsifier:
            raise ValueError("hypothesis id, statement and falsifier must be non-empty")
        if status not in HYPOTHESIS_STATUSES:
            raise ValueError("hypothesis status is not allowed; hypotheses cannot self-promote to policy")
        _aware(occurred_at, "occurred_at")
        _validate_optional_identity(observation_identity, "observation_identity")
        _validate_optional_identity(request_id, "request_id")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("hypothesis revision reason must be non-empty")
        refs = tuple(sorted(set(evidence_references)))
        if any(not isinstance(ref, str) or not ref for ref in refs):
            raise ValueError("evidence references must be non-empty strings")

        with self._connect() as connection:
            connection.execute("BEGIN IMMEDIATE")
            existing = connection.execute(
                "SELECT * FROM hypotheses WHERE hypothesis_id=?", (hypothesis_id,)
            ).fetchone()
            before_state = None if existing is None else _row_payload(existing)
            if existing is not None and existing["trader_identity"] != self.trader_identity:
                raise ValueError("hypothesis belongs to a different trader identity")
            created_at = occurred_at if existing is None else _parse_dt(existing["created_at"], "hypothesis.created_at")
            after_state = _current_payload(
                hypothesis_id=hypothesis_id,
                created_at=created_at,
                updated_at=occurred_at,
                trader_identity=self.trader_identity,
                statement=statement,
                falsifier=falsifier,
                status=status,
                evidence_references=refs,
            )
            next_revision = int(
                connection.execute(
                    "SELECT COALESCE(MAX(revision_number), 0) + 1 FROM hypothesis_revisions WHERE hypothesis_id=?",
                    (hypothesis_id,),
                ).fetchone()[0]
            )
            before_json = None if before_state is None else _canonical_json(before_state)
            after_json = _canonical_json(after_state)
            before_sha = None if before_json is None else sha256(before_json.encode("utf-8")).hexdigest()
            after_sha = sha256(after_json.encode("utf-8")).hexdigest()
            revision_identity = _hash(
                {
                    "schema_version": HYPOTHESIS_REVISION_SCHEMA_VERSION,
                    "revision_number": next_revision,
                    "hypothesis_id": hypothesis_id,
                    "recorded_at": _iso(occurred_at),
                    "trader_identity": self.trader_identity,
                    "observation_identity": observation_identity,
                    "request_id": request_id,
                    "reason": reason,
                    "before_sha256": before_sha,
                    "after_sha256": after_sha,
                }
            )
            connection.execute(
                """
                INSERT INTO hypotheses VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(hypothesis_id) DO UPDATE SET
                    updated_at=excluded.updated_at,
                    statement=excluded.statement,
                    falsifier=excluded.falsifier,
                    status=excluded.status,
                    evidence_references_json=excluded.evidence_references_json,
                    identity=excluded.identity
                """,
                (
                    hypothesis_id,
                    after_state["created_at"],
                    after_state["updated_at"],
                    self.trader_identity,
                    statement,
                    falsifier,
                    status,
                    _canonical_json(refs),
                    after_state["identity"],
                ),
            )
            cursor = connection.execute(
                """
                INSERT INTO hypothesis_revisions(
                    revision_number, hypothesis_id, recorded_at, trader_identity,
                    observation_identity, request_id, reason, before_json, after_json,
                    before_sha256, after_sha256, identity
                ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    next_revision,
                    hypothesis_id,
                    _iso(occurred_at),
                    self.trader_identity,
                    observation_identity,
                    request_id,
                    reason,
                    before_json,
                    after_json,
                    before_sha,
                    after_sha,
                    revision_identity,
                ),
            )
            sequence = int(cursor.lastrowid)

        record = HypothesisRecord(
            hypothesis_id=hypothesis_id,
            created_at=created_at,
            updated_at=occurred_at,
            trader_identity=self.trader_identity,
            statement=statement,
            falsifier=falsifier,
            status=status,
            evidence_references=refs,
            identity=str(after_state["identity"]),
        )
        revision = HypothesisRevision(
            sequence=sequence,
            revision_number=next_revision,
            hypothesis_id=hypothesis_id,
            recorded_at=occurred_at,
            trader_identity=self.trader_identity,
            observation_identity=observation_identity,
            request_id=request_id,
            reason=reason,
            before_state=None if before_state is None else dict(before_state),
            after_state=dict(after_state),
            before_sha256=before_sha,
            after_sha256=after_sha,
            identity=revision_identity,
        )
        return record, revision

    def list_revisions(self, *, hypothesis_id: str | None = None) -> tuple[HypothesisRevision, ...]:
        if hypothesis_id is not None and (not isinstance(hypothesis_id, str) or not hypothesis_id):
            raise ValueError("hypothesis_id must be null or a non-empty string")
        with self._connect() as connection:
            if hypothesis_id is None:
                rows = connection.execute(
                    "SELECT * FROM hypothesis_revisions ORDER BY sequence"
                ).fetchall()
            else:
                rows = connection.execute(
                    "SELECT * FROM hypothesis_revisions WHERE hypothesis_id=? ORDER BY revision_number",
                    (hypothesis_id,),
                ).fetchall()
        return tuple(self._revision_from_row(row) for row in rows)

    @staticmethod
    def _revision_from_row(row: sqlite3.Row) -> HypothesisRevision:
        before_json = row["before_json"]
        after_json = row["after_json"]
        before_sha = row["before_sha256"]
        after_sha = row["after_sha256"]
        if before_json is None:
            if before_sha is not None:
                raise ValueError("null hypothesis before state cannot have a hash")
            before_state = None
        else:
            if sha256(before_json.encode("utf-8")).hexdigest() != before_sha:
                raise ValueError("hypothesis before-state hash mismatch")
            before_state = json.loads(before_json)
        if sha256(after_json.encode("utf-8")).hexdigest() != after_sha:
            raise ValueError("hypothesis after-state hash mismatch")
        after_state = json.loads(after_json)
        return HypothesisRevision(
            sequence=int(row["sequence"]),
            revision_number=int(row["revision_number"]),
            hypothesis_id=row["hypothesis_id"],
            recorded_at=_parse_dt(row["recorded_at"], "hypothesis_revision.recorded_at"),
            trader_identity=row["trader_identity"],
            observation_identity=row["observation_identity"],
            request_id=row["request_id"],
            reason=row["reason"],
            before_state=before_state,
            after_state=after_state,
            before_sha256=before_sha,
            after_sha256=after_sha,
            identity=row["identity"],
        )

    def portable_export(self) -> list[dict[str, Any]]:
        return [
            {
                "sequence": item.sequence,
                "revision_number": item.revision_number,
                "hypothesis_id": item.hypothesis_id,
                "recorded_at": _iso(item.recorded_at),
                "observation_identity": item.observation_identity,
                "request_id": item.request_id,
                "reason": item.reason,
                "before_state": None if item.before_state is None else dict(item.before_state),
                "after_state": dict(item.after_state),
                "before_sha256": item.before_sha256,
                "after_sha256": item.after_sha256,
                "identity": item.identity,
                "schema_version": HYPOTHESIS_REVISION_SCHEMA_VERSION,
            }
            for item in self.list_revisions()
        ]


__all__ = [
    "HYPOTHESIS_REVISION_SCHEMA_VERSION",
    "HypothesisRevision",
    "VersionedHypothesisLedger",
]

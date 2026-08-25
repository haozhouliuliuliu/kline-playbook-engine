"""Project-owned local persistence for the minimal persistent DeepSeek trader.

The store intentionally knows nothing about DeepSeek Harness session internals.  It
persists only project-governed trader state: DS_WORKING_MEMORY, DS_JOURNAL,
DS_HYPOTHESIS_MEMORY and an append-only audit trail.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable, Mapping

from src.jianghe_ai_trader import (
    AttentionMode,
    Direction,
    JiangheWorkingMemory,
    MemoryMutation,
    StrategyFamily,
    WatchRegion,
)


STORE_SCHEMA_VERSION = "KPE_PERSISTENT_TRADER_STORE_V0_1"
PORTABLE_EXPORT_VERSION = "KPE_PERSISTENT_TRADER_EXPORT_V0_1"
HYPOTHESIS_STATUSES = frozenset({"CANDIDATE", "FALSIFIED", "RETIRED"})


def _canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
        allow_nan=False,
    )


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


def _strict_keys(payload: Mapping[str, Any], expected: set[str], name: str) -> None:
    actual = set(payload)
    if actual != expected:
        raise ValueError(f"{name} fields mismatch; missing={sorted(expected-actual)}, unknown={sorted(actual-expected)}")


def working_memory_to_payload(memory: JiangheWorkingMemory) -> dict[str, Any]:
    return {
        "attention_mode": memory.attention_mode.value,
        "current_market_hypothesis": memory.current_market_hypothesis,
        "timeframe_trend_view": [list(item) for item in memory.timeframe_trend_view],
        "directional_bias": memory.directional_bias.value,
        "watch_regions": [
            {
                "region_id": region.region_id,
                "lower_bound": region.lower_bound,
                "upper_bound": region.upper_bound,
                "created_at": _iso(region.created_at),
                "expires_at": _iso(region.expires_at),
                "reason": region.reason,
            }
            for region in memory.watch_regions
        ],
        "key_location_hypotheses": list(memory.key_location_hypotheses),
        "active_family_hypothesis": memory.active_family_hypothesis.value,
        "expected_trigger": memory.expected_trigger,
        "invalidation_hypothesis": memory.invalidation_hypothesis,
        "last_meaningful_decision": memory.last_meaningful_decision,
        "open_questions": list(memory.open_questions),
        "annotation_history": [list(item) for item in memory.annotation_history],
        "transition_reason": memory.transition_reason,
        "review_at": _iso(memory.review_at) if memory.review_at is not None else None,
        "mutation_history": [
            {
                "timestamp": _iso(mutation.timestamp),
                "field_name": mutation.field_name,
                "previous_value": mutation.previous_value,
                "new_value": mutation.new_value,
                "reason": mutation.reason,
                "observation_identity": mutation.observation_identity,
                "ai_trader_identity": mutation.ai_trader_identity,
            }
            for mutation in memory.mutation_history
        ],
    }


def _tuple_pairs(value: object, field_name: str) -> tuple[tuple[str, str], ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be an array")
    result: list[tuple[str, str]] = []
    for item in value:
        if (
            not isinstance(item, list)
            or len(item) != 2
            or not isinstance(item[0], str)
            or not isinstance(item[1], str)
        ):
            raise ValueError(f"{field_name} must contain string pairs")
        result.append((item[0], item[1]))
    return tuple(result)


def _string_tuple(value: object, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError(f"{field_name} must be an array of strings")
    return tuple(value)


def working_memory_from_payload(payload: Mapping[str, Any]) -> JiangheWorkingMemory:
    expected = {
        "attention_mode",
        "current_market_hypothesis",
        "timeframe_trend_view",
        "directional_bias",
        "watch_regions",
        "key_location_hypotheses",
        "active_family_hypothesis",
        "expected_trigger",
        "invalidation_hypothesis",
        "last_meaningful_decision",
        "open_questions",
        "annotation_history",
        "transition_reason",
        "review_at",
        "mutation_history",
    }
    _strict_keys(payload, expected, "working_memory")
    raw_regions = payload["watch_regions"]
    if not isinstance(raw_regions, list):
        raise ValueError("watch_regions must be an array")
    regions: list[WatchRegion] = []
    for raw in raw_regions:
        if not isinstance(raw, dict):
            raise ValueError("watch_region must be an object")
        _strict_keys(
            raw,
            {"region_id", "lower_bound", "upper_bound", "created_at", "expires_at", "reason"},
            "watch_region",
        )
        regions.append(
            WatchRegion(
                region_id=str(raw["region_id"]),
                lower_bound=str(raw["lower_bound"]),
                upper_bound=str(raw["upper_bound"]),
                created_at=_parse_dt(raw["created_at"], "watch_region.created_at"),
                expires_at=_parse_dt(raw["expires_at"], "watch_region.expires_at"),
                reason=str(raw["reason"]),
            )
        )

    raw_mutations = payload["mutation_history"]
    if not isinstance(raw_mutations, list):
        raise ValueError("mutation_history must be an array")
    mutations: list[MemoryMutation] = []
    for raw in raw_mutations:
        if not isinstance(raw, dict):
            raise ValueError("memory mutation must be an object")
        _strict_keys(
            raw,
            {
                "timestamp",
                "field_name",
                "previous_value",
                "new_value",
                "reason",
                "observation_identity",
                "ai_trader_identity",
            },
            "memory_mutation",
        )
        previous = raw["previous_value"]
        new = raw["new_value"]
        if previous is not None and not isinstance(previous, str):
            raise ValueError("memory_mutation.previous_value must be string or null")
        if new is not None and not isinstance(new, str):
            raise ValueError("memory_mutation.new_value must be string or null")
        mutations.append(
            MemoryMutation(
                timestamp=_parse_dt(raw["timestamp"], "memory_mutation.timestamp"),
                field_name=str(raw["field_name"]),
                previous_value=previous,
                new_value=new,
                reason=str(raw["reason"]),
                observation_identity=str(raw["observation_identity"]),
                ai_trader_identity=str(raw["ai_trader_identity"]),
            )
        )

    review_at = payload["review_at"]
    return JiangheWorkingMemory(
        attention_mode=AttentionMode(payload["attention_mode"]),
        current_market_hypothesis=payload["current_market_hypothesis"],
        timeframe_trend_view=_tuple_pairs(payload["timeframe_trend_view"], "timeframe_trend_view"),
        directional_bias=Direction(payload["directional_bias"]),
        watch_regions=tuple(regions),
        key_location_hypotheses=_string_tuple(payload["key_location_hypotheses"], "key_location_hypotheses"),
        active_family_hypothesis=StrategyFamily(payload["active_family_hypothesis"]),
        expected_trigger=payload["expected_trigger"],
        invalidation_hypothesis=payload["invalidation_hypothesis"],
        last_meaningful_decision=payload["last_meaningful_decision"],
        open_questions=_string_tuple(payload["open_questions"], "open_questions"),
        annotation_history=_tuple_pairs(payload["annotation_history"], "annotation_history"),
        transition_reason=payload["transition_reason"],
        review_at=None if review_at is None else _parse_dt(review_at, "review_at"),
        mutation_history=tuple(mutations),
    )


@dataclass(frozen=True)
class JournalEntry:
    entry_id: str
    created_at: datetime
    trader_identity: str
    observation_identity: str | None
    body: str
    tags: tuple[str, ...]
    identity: str


@dataclass(frozen=True)
class HypothesisRecord:
    hypothesis_id: str
    created_at: datetime
    updated_at: datetime
    trader_identity: str
    statement: str
    falsifier: str
    status: str
    evidence_references: tuple[str, ...]
    identity: str

    @property
    def executable_policy(self) -> bool:
        return False


@dataclass(frozen=True)
class AuditEvent:
    sequence: int
    event_id: str
    occurred_at: datetime
    event_kind: str
    trader_identity: str
    observation_identity: str | None
    request_id: str | None
    payload: Mapping[str, Any]
    payload_sha256: str


class PersistentTraderStore:
    """SQLite store for project-owned persistent trader state.

    The database is local and portable.  It stores no opaque Harness session state and
    exposes no method that can modify JIANGHE_CANON.
    """

    def __init__(self, path: str | Path, *, trader_identity: str) -> None:
        if not isinstance(trader_identity, str) or not trader_identity:
            raise ValueError("trader_identity must be non-empty")
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.trader_identity = trader_identity
        self._connection = sqlite3.connect(self.path)
        self._connection.row_factory = sqlite3.Row
        self._connection.execute("PRAGMA foreign_keys = ON")
        try:
            self._initialize()
        except Exception:
            # The mismatched-trader / schema failure remains fail-closed (the error
            # is re-raised), but the open handle must not survive to keep Windows
            # temporary-directory cleanup from observing WinError 32.
            self._connection.close()
            self._connection = None  # type: ignore[assignment]
            raise

    def _initialize(self) -> None:
        self._connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS working_memory (
                singleton_id INTEGER PRIMARY KEY CHECK(singleton_id = 1),
                trader_identity TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS journal (
                entry_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                trader_identity TEXT NOT NULL,
                observation_identity TEXT,
                body TEXT NOT NULL,
                tags_json TEXT NOT NULL,
                identity TEXT NOT NULL UNIQUE
            );
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
            CREATE TABLE IF NOT EXISTS audit_events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                occurred_at TEXT NOT NULL,
                event_kind TEXT NOT NULL,
                trader_identity TEXT NOT NULL,
                observation_identity TEXT,
                request_id TEXT,
                payload_json TEXT NOT NULL,
                payload_sha256 TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS audit_request_idx ON audit_events(request_id, sequence);
            """
        )
        existing_schema = self._connection.execute(
            "SELECT value FROM metadata WHERE key='schema_version'"
        ).fetchone()
        if existing_schema is not None and existing_schema[0] != STORE_SCHEMA_VERSION:
            raise ValueError("unsupported persistent trader store schema")
        existing_trader = self._connection.execute(
            "SELECT value FROM metadata WHERE key='trader_identity'"
        ).fetchone()
        if existing_trader is not None and existing_trader[0] != self.trader_identity:
            raise ValueError("database belongs to a different trader identity")
        self._connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES('schema_version', ?)",
            (STORE_SCHEMA_VERSION,),
        )
        self._connection.execute(
            "INSERT OR REPLACE INTO metadata(key, value) VALUES('trader_identity', ?)",
            (self.trader_identity,),
        )
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self) -> "PersistentTraderStore":
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def load_working_memory(self) -> JiangheWorkingMemory:
        row = self._connection.execute(
            "SELECT payload_json, payload_sha256 FROM working_memory WHERE singleton_id=1"
        ).fetchone()
        if row is None:
            return JiangheWorkingMemory()
        payload_json = row["payload_json"]
        if sha256(payload_json.encode("utf-8")).hexdigest() != row["payload_sha256"]:
            raise ValueError("working memory payload hash mismatch")
        payload = json.loads(payload_json)
        if not isinstance(payload, dict):
            raise ValueError("working memory payload must be object")
        return working_memory_from_payload(payload)

    def save_working_memory(self, memory: JiangheWorkingMemory, *, updated_at: datetime) -> str:
        payload = working_memory_to_payload(memory)
        payload_json = _canonical_json(payload)
        payload_sha = sha256(payload_json.encode("utf-8")).hexdigest()
        self._connection.execute(
            """
            INSERT INTO working_memory(singleton_id, trader_identity, payload_json, payload_sha256, updated_at)
            VALUES(1, ?, ?, ?, ?)
            ON CONFLICT(singleton_id) DO UPDATE SET
                trader_identity=excluded.trader_identity,
                payload_json=excluded.payload_json,
                payload_sha256=excluded.payload_sha256,
                updated_at=excluded.updated_at
            """,
            (self.trader_identity, payload_json, payload_sha, _iso(updated_at)),
        )
        self._connection.commit()
        return payload_sha

    def append_journal(
        self,
        *,
        entry_id: str,
        created_at: datetime,
        body: str,
        observation_identity: str | None = None,
        tags: Iterable[str] = (),
    ) -> JournalEntry:
        if not entry_id or not body:
            raise ValueError("journal entry_id and body must be non-empty")
        normalized_tags = tuple(sorted(set(tags)))
        if any(not isinstance(tag, str) or not tag for tag in normalized_tags):
            raise ValueError("journal tags must be non-empty strings")
        payload = {
            "entry_id": entry_id,
            "created_at": _iso(created_at),
            "trader_identity": self.trader_identity,
            "observation_identity": observation_identity,
            "body": body,
            "tags": normalized_tags,
            "semantic_class": "DS_JOURNAL_REFLECTION_NOT_FACT_OR_POLICY",
        }
        identity = _hash(payload)
        self._connection.execute(
            "INSERT INTO journal VALUES(?, ?, ?, ?, ?, ?, ?)",
            (
                entry_id,
                payload["created_at"],
                self.trader_identity,
                observation_identity,
                body,
                _canonical_json(normalized_tags),
                identity,
            ),
        )
        self._connection.commit()
        return JournalEntry(entry_id, created_at, self.trader_identity, observation_identity, body, normalized_tags, identity)

    def list_journal(self, *, limit: int | None = 20) -> tuple[JournalEntry, ...]:
        if limit is not None and not 1 <= limit <= 100:
            raise ValueError("journal limit must be 1..100 or None for complete export")
        if limit is None:
            rows = self._connection.execute(
                "SELECT * FROM journal ORDER BY created_at DESC, entry_id DESC"
            ).fetchall()
        else:
            rows = self._connection.execute(
                "SELECT * FROM journal ORDER BY created_at DESC, entry_id DESC LIMIT ?", (limit,)
            ).fetchall()
        return tuple(
            JournalEntry(
                row["entry_id"],
                _parse_dt(row["created_at"], "journal.created_at"),
                row["trader_identity"],
                row["observation_identity"],
                row["body"],
                tuple(json.loads(row["tags_json"])),
                row["identity"],
            )
            for row in rows
        )

    def put_hypothesis(
        self,
        *,
        hypothesis_id: str,
        created_at: datetime,
        updated_at: datetime,
        statement: str,
        falsifier: str,
        status: str = "CANDIDATE",
        evidence_references: Iterable[str] = (),
    ) -> HypothesisRecord:
        if not hypothesis_id or not statement or not falsifier:
            raise ValueError("hypothesis id, statement and falsifier must be non-empty")
        if status not in HYPOTHESIS_STATUSES:
            raise ValueError("hypothesis status is not allowed; hypotheses cannot self-promote to policy")
        if _aware(updated_at, "updated_at") < _aware(created_at, "created_at"):
            raise ValueError("hypothesis updated_at cannot precede created_at")
        refs = tuple(sorted(set(evidence_references)))
        if any(not isinstance(ref, str) or not ref for ref in refs):
            raise ValueError("evidence references must be non-empty strings")
        payload = {
            "hypothesis_id": hypothesis_id,
            "created_at": _iso(created_at),
            "updated_at": _iso(updated_at),
            "trader_identity": self.trader_identity,
            "statement": statement,
            "falsifier": falsifier,
            "status": status,
            "evidence_references": refs,
            "executable_policy": False,
            "semantic_class": "DS_HYPOTHESIS_MEMORY_NON_EXECUTABLE",
        }
        identity = _hash(payload)
        self._connection.execute(
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
                payload["created_at"],
                payload["updated_at"],
                self.trader_identity,
                statement,
                falsifier,
                status,
                _canonical_json(refs),
                identity,
            ),
        )
        self._connection.commit()
        return HypothesisRecord(
            hypothesis_id, created_at, updated_at, self.trader_identity,
            statement, falsifier, status, refs, identity,
        )

    def list_hypotheses(self, *, limit: int | None = 50) -> tuple[HypothesisRecord, ...]:
        if limit is not None and not 1 <= limit <= 200:
            raise ValueError("hypothesis limit must be 1..200 or None for complete export")
        if limit is None:
            rows = self._connection.execute(
                "SELECT * FROM hypotheses ORDER BY updated_at DESC, hypothesis_id DESC"
            ).fetchall()
        else:
            rows = self._connection.execute(
                "SELECT * FROM hypotheses ORDER BY updated_at DESC, hypothesis_id DESC LIMIT ?", (limit,)
            ).fetchall()
        return tuple(
            HypothesisRecord(
                row["hypothesis_id"],
                _parse_dt(row["created_at"], "hypothesis.created_at"),
                _parse_dt(row["updated_at"], "hypothesis.updated_at"),
                row["trader_identity"],
                row["statement"],
                row["falsifier"],
                row["status"],
                tuple(json.loads(row["evidence_references_json"])),
                row["identity"],
            )
            for row in rows
        )

    def append_audit(
        self,
        *,
        event_id: str,
        occurred_at: datetime,
        event_kind: str,
        payload: Mapping[str, Any],
        observation_identity: str | None = None,
        request_id: str | None = None,
    ) -> AuditEvent:
        if not event_id or not event_kind:
            raise ValueError("audit event id and kind must be non-empty")
        payload_json = _canonical_json(payload)
        payload_sha = sha256(payload_json.encode("utf-8")).hexdigest()
        cursor = self._connection.execute(
            """
            INSERT INTO audit_events(
                event_id, occurred_at, event_kind, trader_identity,
                observation_identity, request_id, payload_json, payload_sha256
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                _iso(occurred_at),
                event_kind,
                self.trader_identity,
                observation_identity,
                request_id,
                payload_json,
                payload_sha,
            ),
        )
        self._connection.commit()
        return AuditEvent(
            int(cursor.lastrowid), event_id, occurred_at, event_kind,
            self.trader_identity, observation_identity, request_id, dict(payload), payload_sha,
        )

    def audit_for_request(self, request_id: str) -> tuple[AuditEvent, ...]:
        rows = self._connection.execute(
            "SELECT * FROM audit_events WHERE request_id=? ORDER BY sequence", (request_id,)
        ).fetchall()
        return tuple(self._audit_from_row(row) for row in rows)

    def list_audit(self) -> tuple[AuditEvent, ...]:
        rows = self._connection.execute("SELECT * FROM audit_events ORDER BY sequence").fetchall()
        return tuple(self._audit_from_row(row) for row in rows)

    @staticmethod
    def _audit_from_row(row: sqlite3.Row) -> AuditEvent:
        payload_json = row["payload_json"]
        if sha256(payload_json.encode("utf-8")).hexdigest() != row["payload_sha256"]:
            raise ValueError("audit payload hash mismatch")
        payload = json.loads(payload_json)
        if not isinstance(payload, dict):
            raise ValueError("audit payload must be an object")
        return AuditEvent(
            int(row["sequence"]),
            row["event_id"],
            _parse_dt(row["occurred_at"], "audit.occurred_at"),
            row["event_kind"],
            row["trader_identity"],
            row["observation_identity"],
            row["request_id"],
            payload,
            row["payload_sha256"],
        )

    def portable_export(self) -> dict[str, Any]:
        """Return complete Harness-independent state for deterministic migration."""
        memory = self.load_working_memory()
        journal = self.list_journal(limit=None)
        hypotheses = self.list_hypotheses(limit=None)
        audit = self.list_audit()
        return {
            "export_version": PORTABLE_EXPORT_VERSION,
            "store_schema_version": STORE_SCHEMA_VERSION,
            "trader_identity": self.trader_identity,
            "harness_opaque_state_included": False,
            "working_memory": working_memory_to_payload(memory),
            "journal": [
                {
                    "entry_id": item.entry_id,
                    "created_at": _iso(item.created_at),
                    "observation_identity": item.observation_identity,
                    "body": item.body,
                    "tags": list(item.tags),
                    "identity": item.identity,
                    "semantic_class": "DS_JOURNAL_REFLECTION_NOT_FACT_OR_POLICY",
                }
                for item in reversed(journal)
            ],
            "hypotheses": [
                {
                    "hypothesis_id": item.hypothesis_id,
                    "created_at": _iso(item.created_at),
                    "updated_at": _iso(item.updated_at),
                    "statement": item.statement,
                    "falsifier": item.falsifier,
                    "status": item.status,
                    "evidence_references": list(item.evidence_references),
                    "identity": item.identity,
                    "executable_policy": False,
                    "semantic_class": "DS_HYPOTHESIS_MEMORY_NON_EXECUTABLE",
                }
                for item in reversed(hypotheses)
            ],
            "audit": [
                {
                    "sequence": item.sequence,
                    "event_id": item.event_id,
                    "occurred_at": _iso(item.occurred_at),
                    "event_kind": item.event_kind,
                    "observation_identity": item.observation_identity,
                    "request_id": item.request_id,
                    "payload": dict(item.payload),
                    "payload_sha256": item.payload_sha256,
                }
                for item in audit
            ],
        }


__all__ = [
    "AuditEvent",
    "HYPOTHESIS_STATUSES",
    "HypothesisRecord",
    "JournalEntry",
    "PORTABLE_EXPORT_VERSION",
    "PersistentTraderStore",
    "STORE_SCHEMA_VERSION",
    "working_memory_from_payload",
    "working_memory_to_payload",
]

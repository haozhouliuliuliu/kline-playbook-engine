"""Immutable, replayable runtime audit ledger for the Shadow Runtime Foundation.

The Ledger is the project's immutable factual history for the runtime chain. It
records at least (Skeleton v1.0 section 6, Trading Loop): intent, order, cancel,
fill, position transition, safety, reconciliation, plus broker events, recovery,
runtime start and kill switch facts.

Properties enforced here:

- append-only and immutable (a record is never mutated after creation);
- chained: every record binds the identity of the previous record, so tampering
  with or silently dropping an earlier record breaks ``verify_chain``;
- replayable: ``records()`` returns the exact deterministic append order and
  ``replay()`` re-walks the chain;
- fail-closed: duplicate sequences, broken chains and inconsistent payloads are
  rejected.

This ledger does NOT own live mutable state and does NOT compute any candidate
performance statistic. Candidate round-trip statistics remain out of scope /
strategy-gated and use the separate offline ``src.round_trip_ledger`` machinery.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json
from typing import Any, Iterable

from src.runtime_events import _canonical_scalar


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


GENESIS_IDENTITY = _canonical_hash({"SHADOW_RUNTIME_LEDGER": "GENESIS"})

RUNTIME_LEDGER_SCHEMA_VERSION = "shadow-runtime-ledger-v0.1"


class RuntimeLedgerRecordKind(str, Enum):
    """Deterministic runtime ledger record vocabulary (Skeleton v1.0 §6)."""

    RUNTIME_START = "RUNTIME_START"
    INTENT = "INTENT"
    ORDER = "ORDER"
    CANCEL = "CANCEL"
    REPLACE = "REPLACE"
    FILL = "FILL"
    POSITION_TRANSITION = "POSITION_TRANSITION"
    SAFETY = "SAFETY"
    RECONCILIATION = "RECONCILIATION"
    BROKER_EVENT = "BROKER_EVENT"
    KILL_SWITCH = "KILL_SWITCH"
    RECOVERY = "RECOVERY"


def ledger_pairs(**kwargs: Any) -> tuple[tuple[str, str], ...]:
    """Canonical sorted ``(key, canonical_value)`` payload for a ledger record."""
    return tuple(
        (key, _canonical_scalar(kwargs[key])) for key in sorted(kwargs)
    )


@dataclass(frozen=True)
class RuntimeLedgerRecord:
    """One immutable, chained factual record."""

    sequence: int
    record_kind: RuntimeLedgerRecordKind
    recorded_at: datetime
    reference_id: str
    payload: tuple[tuple[str, str], ...]
    previous_identity: str
    schema_version: str = RUNTIME_LEDGER_SCHEMA_VERSION

    def __post_init__(self) -> None:
        if type(self.sequence) is not int or self.sequence < 0:
            raise ValueError("runtime ledger record sequence must be a non-negative integer")
        if not isinstance(self.record_kind, RuntimeLedgerRecordKind):
            raise ValueError("runtime ledger record kind must be a RuntimeLedgerRecordKind")
        if self.recorded_at.tzinfo is None:
            raise ValueError("runtime ledger record timestamp must be timezone-aware")
        if not self.reference_id:
            raise ValueError("runtime ledger record requires a reference identity")
        if not isinstance(self.payload, tuple):
            raise ValueError("runtime ledger record payload must be a tuple")
        names = tuple(name for name, _ in self.payload)
        if names != tuple(sorted(names)) or len(names) != len(set(names)):
            raise ValueError("runtime ledger record payload keys must be sorted and unique")
        if self.previous_identity != GENESIS_IDENTITY and len(self.previous_identity) != 64:
            raise ValueError("runtime ledger record chain identity must be a sha256 hex digest")
        if not self.schema_version:
            raise ValueError("runtime ledger record schema version is required")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "sequence": self.sequence,
                "record_kind": self.record_kind.value,
                "recorded_at": self.recorded_at.isoformat(),
                "reference_id": self.reference_id,
                "payload": self.payload,
                "previous_identity": self.previous_identity,
                "schema_version": self.schema_version,
            }
        )


def _ledger_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class RuntimeLedger:
    """Append-only immutable runtime ledger with chain integrity."""

    def __init__(self) -> None:
        self._records: list[RuntimeLedgerRecord] = []
        self._anchor_sequence = 0
        self._anchor_identity = GENESIS_IDENTITY
        self._tail_identity = GENESIS_IDENTITY

    @property
    def tail_identity(self) -> str:
        return self._tail_identity

    @property
    def schema_version(self) -> str:
        return RUNTIME_LEDGER_SCHEMA_VERSION

    @property
    def anchor_sequence(self) -> int:
        return self._anchor_sequence

    @property
    def anchor_identity(self) -> str:
        return self._anchor_identity

    @property
    def next_sequence(self) -> int:
        return self._anchor_sequence + len(self._records)

    def restore_anchor(self, *, sequence: int, identity: str) -> None:
        """Restore an empty ledger to a durably verified chain anchor.

        The caller owns verification of the checkpoint that supplied the anchor.
        Existing records can never be discarded or replaced through this seam.
        """
        if self._records or self._tail_identity != GENESIS_IDENTITY:
            raise ValueError("runtime ledger anchor restore requires a fresh empty ledger")
        if type(sequence) is not int or sequence < 0:
            raise ValueError("runtime ledger anchor sequence must be non-negative")
        if sequence == 0:
            if identity != GENESIS_IDENTITY:
                raise ValueError("runtime ledger genesis anchor identity is invalid")
        elif (
            not isinstance(identity, str)
            or len(identity) != 64
            or any(character not in "0123456789abcdef" for character in identity)
        ):
            raise ValueError("runtime ledger anchor identity must be a sha256 digest")
        self._anchor_sequence = sequence
        self._anchor_identity = identity
        self._tail_identity = identity

    def append(
        self,
        record_kind: RuntimeLedgerRecordKind,
        reference_id: str,
        payload: tuple[tuple[str, str], ...],
        recorded_at: datetime,
    ) -> RuntimeLedgerRecord:
        """Append one immutable record; returns it and advances the chain."""
        record = RuntimeLedgerRecord(
            sequence=self.next_sequence,
            record_kind=record_kind,
            recorded_at=recorded_at,
            reference_id=reference_id,
            payload=payload,
            previous_identity=self._tail_identity,
        )
        self._records.append(record)
        self._tail_identity = record.identity_id
        return record

    def records(self) -> tuple[RuntimeLedgerRecord, ...]:
        """Deterministic append order of every record (replay source)."""
        return tuple(self._records)

    def replay(self) -> tuple[RuntimeLedgerRecord, ...]:
        """Deterministic replay; identical to ``records()`` (append order)."""
        return self.records()

    def verify_chain(self) -> bool:
        """Audit: recompute the whole chain and confirm every link is intact.

        A dropped, reordered or mutated record breaks the chain. Rejecting on a
        broken chain (rather than repairing) is the fail-closed behavior.
        """
        previous = self._anchor_identity
        for index, record in enumerate(self._records, start=self._anchor_sequence):
            if record.sequence != index:
                return False
            if record.previous_identity != previous:
                return False
            previous = record.identity_id
        return previous == self._tail_identity

    def count(self) -> int:
        return len(self._records)

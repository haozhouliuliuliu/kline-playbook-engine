"""Deterministic broker event model for the Shadow Runtime Foundation.

This module is the generic, broker-agnostic event vocabulary of the runtime
chain. It defines what a broker event IS (identity, sequence, stream) and how
an applied-event log is projected, without binding to any real broker private
API. ``BrokerEventLog`` is an immutable projection owned by ``TradingState``
(the sole real-time mutable state owner); the mutable application logic lives
in ``src.trading_state``.

Ordinary engineering under Skeleton v1.0 "Trading Loop": broker events require
- unique ``event_id``;
- idempotent application;
- deduplication;
- defined out-of-order handling;
- sequence / stream conventions.

No real broker, no network, no candidate strategy outcome, no real money.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from hashlib import sha256
import json
from typing import Any


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _canonical_scalar(value: Any) -> str:
    """Stringify one event payload value deterministically for canonical hashing."""
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def event_pairs(**kwargs: Any) -> tuple[tuple[str, str], ...]:
    """Deterministic sorted ``(key, canonical_value)`` payload.

    Keys are sorted and unique; values are canonicalized so that identical
    semantic content always produces the identical tuple and therefore the
    identical event identity.
    """
    return tuple(
        (key, _canonical_scalar(kwargs[key])) for key in sorted(kwargs)
    )


class BrokerConnectionState(str, Enum):
    """Broker-side connection lifecycle (deterministic, no real network)."""

    CONNECTED = "CONNECTED"
    DISCONNECTED = "DISCONNECTED"
    RECONNECTING = "RECONNECTING"


class BrokerEventType(str, Enum):
    """Deterministic broker event vocabulary (generic, broker-agnostic)."""

    ORDER_SUBMITTED = "ORDER_SUBMITTED"
    ORDER_FILLED = "ORDER_FILLED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    ORDER_REJECTED = "ORDER_REJECTED"
    ORDER_REPLACED = "ORDER_REPLACED"
    ACCOUNT_SNAPSHOT = "ACCOUNT_SNAPSHOT"
    POSITION_SNAPSHOT = "POSITION_SNAPSHOT"
    ORDER_SNAPSHOT = "ORDER_SNAPSHOT"
    CONNECTION_STATE = "CONNECTION_STATE"


class BrokerEventViolationKind(str, Enum):
    """Deterministic reason a broker event could not be applied."""

    DUPLICATE_EVENT_ID_DIFFERENT_CONTENT = "DUPLICATE_EVENT_ID_DIFFERENT_CONTENT"
    OUT_OF_ORDER = "OUT_OF_ORDER"
    SEQUENCE_GAP = "SEQUENCE_GAP"
    INVALID_CONTENT = "INVALID_CONTENT"


@dataclass(frozen=True)
class BrokerEvent:
    """One immutable broker fact.

    Fields
    ------
    event_id:
        Unique broker-assigned or deterministic engine-assigned event identity.
        Used for deduplication / idempotent application.
    event_type:
        Deterministic broker event type (generic vocabulary).
    occurred_at:
        Timezone-aware broker timestamp of the fact.
    stream_id:
        Which ordered event stream this event belongs to (e.g. one paper broker).
        Sequence discipline is enforced per stream.
    sequence:
        Non-negative monotonic sequence within ``stream_id`` (0-based).
    order_id:
        Broker order identity when the event concerns an order.
    client_request_id:
        Deterministic engine/client request identity that originated the order.
    payload:
        Canonical sorted ``(key, value)`` pairs; values are already canonical
        strings. Always empty when no extra fact is needed.
    """

    event_id: str
    event_type: BrokerEventType
    occurred_at: datetime
    stream_id: str
    sequence: int
    order_id: str | None = None
    client_request_id: str | None = None
    payload: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.event_id, str) or not self.event_id.strip():
            raise ValueError("broker event_id is required")
        if not isinstance(self.event_type, BrokerEventType):
            raise ValueError("broker event type must be a BrokerEventType")
        if self.occurred_at.tzinfo is None:
            raise ValueError("broker event timestamp must be timezone-aware")
        if not isinstance(self.stream_id, str) or not self.stream_id.strip():
            raise ValueError("broker event stream_id is required")
        if type(self.sequence) is not int or self.sequence < 0:
            raise ValueError("broker event sequence must be a non-negative integer")
        for field, value in (
            ("order_id", self.order_id),
            ("client_request_id", self.client_request_id),
        ):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{field} must be a non-empty string or None")
        if not isinstance(self.payload, tuple):
            raise ValueError("broker event payload must be a tuple")
        names = tuple(name for name, _ in self.payload)
        if names != tuple(sorted(names)) or len(names) != len(set(names)):
            raise ValueError("broker event payload keys must be sorted and unique")

    @property
    def identity_id(self) -> str:
        """Content identity: any semantic change to the event changes the id."""
        return _canonical_hash(
            {
                "event_id": self.event_id,
                "event_type": self.event_type.value,
                "occurred_at": self.occurred_at.isoformat(),
                "stream_id": self.stream_id,
                "sequence": self.sequence,
                "order_id": self.order_id,
                "client_request_id": self.client_request_id,
                "payload": self.payload,
            }
        )


@dataclass(frozen=True)
class BrokerEventViolation:
    """Deterministic record of a broker event that failed application."""

    violation_id: str
    event: BrokerEvent
    kind: BrokerEventViolationKind
    detail: str
    detected_at: datetime

    def __post_init__(self) -> None:
        if not self.violation_id:
            raise ValueError("broker event violation id is required")
        if not isinstance(self.event, BrokerEvent):
            raise ValueError("broker event violation requires a BrokerEvent")
        if not isinstance(self.kind, BrokerEventViolationKind):
            raise ValueError("violation kind must be a BrokerEventViolationKind")
        if not self.detail:
            raise ValueError("broker event violation detail is required")
        if self.detected_at.tzinfo is None:
            raise ValueError("violation detection timestamp must be timezone-aware")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "violation_id": self.violation_id,
                "event": self.event.identity_id,
                "kind": self.kind.value,
                "detail": self.detail,
                "detected_at": self.detected_at.isoformat(),
            }
        )


@dataclass(frozen=True)
class BrokerEventLog:
    """Immutable projection of the applied broker event stream.

    ``TradingState`` owns the mutable log; this frozen dataclass is the
    deterministic snapshot used for identity, audit and restart recovery. It is
    an ordinary projection and cannot be mutated after construction.
    """

    applied_events: tuple[BrokerEvent, ...] = ()
    event_violations: tuple[BrokerEventViolation, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.applied_events, tuple) or not isinstance(
            self.event_violations, tuple
        ):
            raise ValueError("broker event log requires tuples")
        event_ids = tuple(event.event_id for event in self.applied_events)
        if len(event_ids) != len(set(event_ids)):
            raise ValueError("broker event log cannot contain duplicate event ids")
        # Per-stream monotonic sequence check.
        by_stream: dict[str, list[int]] = {}
        for event in self.applied_events:
            by_stream.setdefault(event.stream_id, []).append(event.sequence)
        for stream_id, sequences in by_stream.items():
            if tuple(sorted(sequences)) != tuple(sequences):
                raise ValueError(
                    f"broker event log stream {stream_id} sequences must be monotonic"
                )

    @property
    def applied_event_ids(self) -> tuple[str, ...]:
        return tuple(event.event_id for event in self.applied_events)

    @property
    def stream_high_water(self) -> tuple[tuple[str, int], ...]:
        """Highest applied sequence per stream, ordered by stream_id."""
        maxima: dict[str, int] = {}
        for event in self.applied_events:
            previous = maxima.get(event.stream_id, -1)
            maxima[event.stream_id] = max(previous, event.sequence)
        return tuple(sorted(maxima.items()))

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "applied_events": [event.identity_id for event in self.applied_events],
                "event_violations": [
                    violation.identity_id for violation in self.event_violations
                ],
            }
        )

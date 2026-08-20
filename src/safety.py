"""Safety gate for the Shadow Runtime Foundation.

Skeleton v1.0 §5: Safety overrides strategies and must cover at least stale /
missing market data, broker disconnect, duplicate/order inconsistency,
account/position mismatch, margin/risk abnormality, clock/session abnormality,
and a kill switch.

This module implements a deterministic ``SafetyGate`` over the current
``TradingState``, ``MarketContext``, broker connection state and reconciliation
report. A tripped kill switch is a permanent latch (manual disarm only);
transient violations (stale data / disconnect) clear on positive conditions,
while persistent violations block new order submission (fail closed).

No permanent real-money risk limit is introduced here. No real broker.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json
from typing import Any

from src.market_context import MarketContext
from src.reconciliation import ReconciliationReport
from src.runtime_events import BrokerConnectionState, BrokerEventViolationKind
from src.trading_state import TradingState

SAFETY_SCHEMA_VERSION = "shadow-runtime-safety-v0.1"

CLOCK_SKEW_TOLERANCE_SECONDS = 60


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class SafetyViolationKind(str, Enum):
    """Deterministic safety violation vocabulary."""

    STALE_MARKET_DATA = "STALE_MARKET_DATA"
    BROKER_DISCONNECT = "BROKER_DISCONNECT"
    DUPLICATE_ORDER = "DUPLICATE_ORDER"
    ORDER_INCONSISTENCY = "ORDER_INCONSISTENCY"
    ACCOUNT_MISMATCH = "ACCOUNT_MISMATCH"
    POSITION_MISMATCH = "POSITION_MISMATCH"
    ORDER_MISMATCH = "ORDER_MISMATCH"
    CLOCK_SESSION_ANOMALY = "CLOCK_SESSION_ANOMALY"
    SEQUENCE_VIOLATION = "SEQUENCE_VIOLATION"
    KILL_SWITCH_TRIPPED = "KILL_SWITCH_TRIPPED"


# Persistent violations cannot clear automatically and block trading.
_PERSISTENT_KINDS = frozenset(
    {
        SafetyViolationKind.DUPLICATE_ORDER,
        SafetyViolationKind.ORDER_INCONSISTENCY,
        SafetyViolationKind.ACCOUNT_MISMATCH,
        SafetyViolationKind.POSITION_MISMATCH,
        SafetyViolationKind.ORDER_MISMATCH,
        SafetyViolationKind.CLOCK_SESSION_ANOMALY,
        SafetyViolationKind.SEQUENCE_VIOLATION,
        SafetyViolationKind.KILL_SWITCH_TRIPPED,
    }
)


@dataclass(frozen=True)
class SafetyViolation:
    kind: SafetyViolationKind
    detail: str
    observed_at: datetime

    def __post_init__(self) -> None:
        if not isinstance(self.kind, SafetyViolationKind):
            raise ValueError("safety violation kind must be a SafetyViolationKind")
        if not self.detail:
            raise ValueError("safety violation detail is required")
        if self.observed_at.tzinfo is None:
            raise ValueError("safety violation timestamp must be timezone-aware")

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "kind": self.kind.value,
                "detail": self.detail,
                "observed_at": self.observed_at.isoformat(),
            }
        )


@dataclass(frozen=True)
class KillSwitch:
    """Deterministic kill switch (permanent latch until manual disarm)."""

    armed: bool
    tripped_at: datetime | None = None
    tripped_by: str | None = None

    def __post_init__(self) -> None:
        if type(self.armed) is not bool:
            raise ValueError("kill switch armed must be a bool")
        if self.tripped_at is not None and self.tripped_at.tzinfo is None:
            raise ValueError("kill switch trip timestamp must be timezone-aware")
        if self.tripped_at is None and self.tripped_by is not None:
            raise ValueError("kill switch trip reason requires a trip timestamp")
        if not self.armed and self.tripped_at is not None:
            raise ValueError("a disarmed kill switch cannot remain tripped")

    @property
    def tripped(self) -> bool:
        return self.tripped_at is not None

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "armed": self.armed,
                "tripped_at": None if self.tripped_at is None else self.tripped_at.isoformat(),
                "tripped_by": self.tripped_by,
            }
        )


@dataclass(frozen=True)
class SafetyAssessment:
    assessed_at: datetime
    violations: tuple[SafetyViolation, ...]
    kill_switch: KillSwitch

    def __post_init__(self) -> None:
        if self.assessed_at.tzinfo is None:
            raise ValueError("safety assessment timestamp must be timezone-aware")
        if not isinstance(self.violations, tuple):
            raise ValueError("safety assessment violations must be a tuple")
        if not isinstance(self.kill_switch, KillSwitch):
            raise ValueError("safety assessment requires a KillSwitch")

    @property
    def nominal(self) -> bool:
        return not self.violations

    @property
    def blocking(self) -> bool:
        """Fail closed: block new order submission on any persistent violation."""
        return self.kill_switch.tripped or any(
            violation.kind in _PERSISTENT_KINDS for violation in self.violations
        )

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "assessed_at": self.assessed_at.isoformat(),
                "violations": [item.identity_id for item in self.violations],
                "kill_switch": self.kill_switch.identity_id,
            }
        )


class SafetyGate:
    """Deterministic Safety override gate (Safety overrides strategies)."""

    def __init__(self) -> None:
        self._kill_switch = KillSwitch(armed=True)
        self._violations: list[SafetyViolation] = []

    @property
    def kill_switch(self) -> KillSwitch:
        return self._kill_switch

    @property
    def active_violations(self) -> tuple[SafetyViolation, ...]:
        return tuple(self._violations)

    def is_blocking(self) -> bool:
        """True when a kill switch or persistent violation must block new orders."""
        if self._kill_switch.tripped:
            return True
        return any(
            violation.kind in _PERSISTENT_KINDS
            and violation.kind is not SafetyViolationKind.KILL_SWITCH_TRIPPED
            for violation in self._violations
        )

    def trip_kill_switch(self, reason: str, at: datetime) -> KillSwitch:
        """Permanently latch the kill switch (manual disarm only)."""
        if at.tzinfo is None:
            raise ValueError("kill switch trip timestamp must be timezone-aware")
        if not reason:
            raise ValueError("kill switch trip requires a reason")
        self._kill_switch = KillSwitch(armed=True, tripped_at=at, tripped_by=reason)
        return self._kill_switch

    def disarm_kill_switch(self, reason: str, at: datetime) -> KillSwitch:
        """Explicit recovery action: disarm only after a positive health check."""
        if at.tzinfo is None:
            raise ValueError("kill switch disarm timestamp must be timezone-aware")
        if not reason:
            raise ValueError("kill switch disarm requires a reason")
        self._kill_switch = KillSwitch(armed=True, tripped_at=None, tripped_by=None)
        return self._kill_switch

    def record_violation(self, kind: SafetyViolationKind, detail: str, observed_at: datetime) -> SafetyViolation:
        violation = SafetyViolation(kind=kind, detail=detail, observed_at=observed_at)
        self._violations.append(violation)
        return violation

    def clear_transient_violations(self) -> None:
        """Clear stale-data / disconnect violations after positive conditions."""
        self._violations = [
            item for item in self._violations
            if item.kind not in (SafetyViolationKind.STALE_MARKET_DATA, SafetyViolationKind.BROKER_DISCONNECT)
        ]

    def assess(
        self,
        *,
        state: TradingState,
        clock_now: datetime,
        context: MarketContext | None,
        connection_state: BrokerConnectionState,
        reconciliation: ReconciliationReport | None,
    ) -> SafetyAssessment:
        if not isinstance(state, TradingState):
            raise ValueError("SafetyGate.assess requires a TradingState")
        if clock_now.tzinfo is None:
            raise ValueError("safety clock timestamp must be timezone-aware")
        if not isinstance(connection_state, BrokerConnectionState):
            raise ValueError("safety requires a BrokerConnectionState")

        violations: list[SafetyViolation] = []

        # Kill switch is a permanent latch (recorded every assessment while tripped).
        if self._kill_switch.tripped:
            violations.append(
                SafetyViolation(
                    kind=SafetyViolationKind.KILL_SWITCH_TRIPPED,
                    detail=f"kill switch tripped by: {self._kill_switch.tripped_by}",
                    observed_at=clock_now,
                )
            )

        # Broker disconnect.
        if connection_state is not BrokerConnectionState.CONNECTED:
            violations.append(
                SafetyViolation(
                    kind=SafetyViolationKind.BROKER_DISCONNECT,
                    detail=f"broker connection state: {connection_state.value}",
                    observed_at=clock_now,
                )
            )

        # Stale / missing market data.
        if context is None:
            violations.append(
                SafetyViolation(
                    kind=SafetyViolationKind.STALE_MARKET_DATA,
                    detail="no market context available",
                    observed_at=clock_now,
                )
            )
        else:
            if context.is_stale(clock_now):
                violations.append(
                    SafetyViolation(
                        kind=SafetyViolationKind.STALE_MARKET_DATA,
                        detail="market context evidence is stale by the configured threshold",
                        observed_at=clock_now,
                    )
                )
            if context.observed_at > clock_now:
                violations.append(
                    SafetyViolation(
                        kind=SafetyViolationKind.CLOCK_SESSION_ANOMALY,
                        detail="market context was observed in the future relative to the clock",
                        observed_at=clock_now,
                    )
                )
            if (clock_now - context.available_at).total_seconds() < -CLOCK_SKEW_TOLERANCE_SECONDS:
                violations.append(
                    SafetyViolation(
                        kind=SafetyViolationKind.CLOCK_SESSION_ANOMALY,
                        detail="bar availability is in the future beyond clock skew tolerance",
                        observed_at=clock_now,
                    )
                )
        if clock_now < state.created_at:
            violations.append(
                SafetyViolation(
                    kind=SafetyViolationKind.CLOCK_SESSION_ANOMALY,
                    detail="clock is earlier than the runtime creation time",
                    observed_at=clock_now,
                )
            )

        # Broker event / sequence violations (duplicate order vs sequence).
        for event_violation in state.event_violations():
            if event_violation.kind is BrokerEventViolationKind.DUPLICATE_EVENT_ID_DIFFERENT_CONTENT:
                kind = SafetyViolationKind.DUPLICATE_ORDER
            else:
                kind = SafetyViolationKind.SEQUENCE_VIOLATION
            violations.append(
                SafetyViolation(
                    kind=kind,
                    detail=f"event {event_violation.event.event_id}: {event_violation.detail}",
                    observed_at=clock_now,
                )
            )

        # Reconciliation mismatches (fail closed).
        if reconciliation is not None:
            if not reconciliation.account_match:
                violations.append(
                    SafetyViolation(
                        kind=SafetyViolationKind.ACCOUNT_MISMATCH,
                        detail="local account disagrees with the broker account snapshot",
                        observed_at=clock_now,
                    )
                )
            if not reconciliation.position_match:
                violations.append(
                    SafetyViolation(
                        kind=SafetyViolationKind.POSITION_MISMATCH,
                        detail="local positions disagree with the broker position snapshot",
                        observed_at=clock_now,
                    )
                )
            if not reconciliation.order_match:
                violations.append(
                    SafetyViolation(
                        kind=SafetyViolationKind.ORDER_MISMATCH,
                        detail="local order statuses disagree with the broker order snapshot",
                        observed_at=clock_now,
                    )
                )

        # Merge with previously recorded active violations (persistent ones stay,
        # except the kill-switch violation which is always re-derived fresh from
        # the kill switch state so a disarm can actually unblock).
        existing_persistent = [
            item
            for item in self._violations
            if item.kind in _PERSISTENT_KINDS
            and item.kind is not SafetyViolationKind.KILL_SWITCH_TRIPPED
        ]
        merged = existing_persistent + violations
        self._violations = _dedupe(merged)
        return SafetyAssessment(
            assessed_at=clock_now,
            violations=self.active_violations,
            kill_switch=self._kill_switch,
        )


def _dedupe(violations: list[SafetyViolation]) -> list[SafetyViolation]:
    seen: set[str] = set()
    result: list[SafetyViolation] = []
    for item in violations:
        identity = item.identity_id
        if identity in seen:
            continue
        seen.add(identity)
        result.append(item)
    return result

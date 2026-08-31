"""Deterministic REAL safety state (mode, latches, transitions).

This module owns the *persistent safety* side of the REAL risk/safety
primitives: the safety mode (``NORMAL`` / ``NO_NEW_RISK`` / ``KILL`` /
``UNKNOWN``), the persistent hard-inconsistency latch and the unresolved
external/manual mutation status. It also defines the shared ``HealthState``
vocabulary used by the runtime facts.

Rules:
- every transition carries a reason and a timezone-aware timestamp;
- disarming the kill switch and clearing the hard-inconsistency latch are
  explicit manual actions; they are never auto-cleared by a single healthy
  sample;
- an unresolved external/manual mutation forces ``NO_NEW_RISK`` until
  reconciliation, and resolution never auto-resumes trading (an explicit
  ``resume`` is required);
- ``KILL`` and ``UNKNOWN`` never allow risk increase.

No broker, provider, account or real-money action is performed here.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json
from typing import Any

REAL_SAFETY_STATE_SCHEMA_VERSION = "real-safety-state-v0.1"


def _canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    return sha256(encoded.encode("utf-8")).hexdigest()


class HealthState(str, Enum):
    """Deterministic health vocabulary for reconciliation/market/provider/broker."""

    HEALTHY = "HEALTHY"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class SafetyMode(str, Enum):
    """Persistent safety mode (KILL/UNKNOWN never allow risk increase)."""

    NORMAL = "NORMAL"
    NO_NEW_RISK = "NO_NEW_RISK"
    KILL = "KILL"
    UNKNOWN = "UNKNOWN"


class ExternalMutationStatus(str, Enum):
    """Unresolved external/manual mutation truth (fail closed until reconciled)."""

    RESOLVED = "RESOLVED"
    UNRESOLVED = "UNRESOLVED"
    UNKNOWN = "UNKNOWN"


def mode_allows_risk_increase(mode: SafetyMode) -> bool:
    """Only NORMAL may allow risk increase; everything else fails closed."""
    if not isinstance(mode, SafetyMode):
        raise ValueError("mode must be a SafetyMode")
    return mode is SafetyMode.NORMAL


def _required_timestamp(value: datetime, name: str) -> None:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise ValueError(f"{name} must be a timezone-aware datetime")


@dataclass(frozen=True)
class RealSafetyState:
    """Immutable snapshot of persistent safety state."""

    mode: SafetyMode
    mode_reason: str
    mode_changed_at: datetime
    external_mutation_status: ExternalMutationStatus
    external_mutation_since: datetime | None
    hard_inconsistency_latched: bool
    hard_inconsistency_reason: str | None
    hard_inconsistency_since: datetime | None

    def __post_init__(self) -> None:
        if not isinstance(self.mode, SafetyMode):
            raise ValueError("safety mode must be a SafetyMode")
        if not self.mode_reason:
            raise ValueError("safety mode reason is required")
        _required_timestamp(self.mode_changed_at, "safety mode change timestamp")
        if not isinstance(self.external_mutation_status, ExternalMutationStatus):
            raise ValueError("external mutation status must be an ExternalMutationStatus")
        if type(self.hard_inconsistency_latched) is not bool:
            raise ValueError("hard inconsistency latch must be a bool")
        if self.external_mutation_since is not None:
            _required_timestamp(self.external_mutation_since, "external mutation timestamp")
        if self.hard_inconsistency_since is not None:
            _required_timestamp(self.hard_inconsistency_since, "hard inconsistency timestamp")
        if self.external_mutation_status is ExternalMutationStatus.UNRESOLVED:
            if self.external_mutation_since is None:
                raise ValueError("unresolved external mutation requires a timestamp")
        elif self.external_mutation_since is not None:
            raise ValueError("resolved/unknown external mutation cannot keep a timestamp")
        if self.hard_inconsistency_latched:
            if not self.hard_inconsistency_reason or self.hard_inconsistency_since is None:
                raise ValueError("latched hard inconsistency requires a reason and timestamp")
        else:
            if self.hard_inconsistency_reason is not None or self.hard_inconsistency_since is not None:
                raise ValueError("unlatched hard inconsistency cannot keep a reason/timestamp")

    def allows_risk_increase(self) -> bool:
        """Fail closed: no risk increase outside NORMAL with clean latches."""
        return (
            mode_allows_risk_increase(self.mode)
            and not self.hard_inconsistency_latched
            and self.external_mutation_status is ExternalMutationStatus.RESOLVED
        )

    @property
    def kill_tripped(self) -> bool:
        return self.mode is SafetyMode.KILL

    @property
    def paused(self) -> bool:
        return self.mode is SafetyMode.NO_NEW_RISK

    @property
    def identity_id(self) -> str:
        return _canonical_hash(
            {
                "mode": self.mode.value,
                "mode_reason": self.mode_reason,
                "mode_changed_at": self.mode_changed_at.isoformat(),
                "external_mutation_status": self.external_mutation_status.value,
                "external_mutation_since": (
                    None if self.external_mutation_since is None else self.external_mutation_since.isoformat()
                ),
                "hard_inconsistency_latched": self.hard_inconsistency_latched,
                "hard_inconsistency_reason": self.hard_inconsistency_reason,
                "hard_inconsistency_since": (
                    None if self.hard_inconsistency_since is None else self.hard_inconsistency_since.isoformat()
                ),
            }
        )


class RealSafetyController:
    """Deterministic owner of safety-mode transitions and persistent latches."""

    def __init__(self, now: datetime) -> None:
        _required_timestamp(now, "safety initialization timestamp")
        self._state = RealSafetyState(
            mode=SafetyMode.NORMAL,
            mode_reason="initialized",
            mode_changed_at=now,
            external_mutation_status=ExternalMutationStatus.RESOLVED,
            external_mutation_since=None,
            hard_inconsistency_latched=False,
            hard_inconsistency_reason=None,
            hard_inconsistency_since=None,
        )

    @property
    def state(self) -> RealSafetyState:
        return self._state

    def _transition(self, *, mode: SafetyMode | None = None, reason: str, at: datetime, **changes: Any) -> RealSafetyState:
        _required_timestamp(at, "safety transition timestamp")
        if not reason:
            raise ValueError("safety transition requires a reason")
        payload: dict[str, Any] = {}
        if mode is not None:
            payload["mode"] = mode
            payload["mode_reason"] = reason
            payload["mode_changed_at"] = at
        payload.update(changes)
        new_state = replace(self._state, **payload)
        self._state = new_state
        return new_state

    def trip_kill(self, reason: str, at: datetime) -> RealSafetyState:
        """Hard kill: permanent latch until an explicit manual disarm."""
        return self._transition(mode=SafetyMode.KILL, reason=reason, at=at)

    def disarm_kill(self, reason: str, at: datetime) -> RealSafetyState:
        """Explicit manual disarm of a tripped kill switch (fail closed otherwise)."""
        if self._state.mode is not SafetyMode.KILL:
            raise ValueError("cannot disarm a kill switch that is not tripped")
        target_mode = (
            SafetyMode.NORMAL
            if (
                self._state.external_mutation_status is ExternalMutationStatus.RESOLVED
                and not self._state.hard_inconsistency_latched
            )
            else SafetyMode.NO_NEW_RISK
        )
        return self._transition(mode=target_mode, reason=reason, at=at)

    def pause(self, reason: str, at: datetime) -> RealSafetyState:
        """Enter NO_NEW_RISK: block risk increase, allow proven reduction."""
        return self._transition(mode=SafetyMode.NO_NEW_RISK, reason=reason, at=at)

    def resume(self, reason: str, at: datetime) -> RealSafetyState:
        """Explicit resume from NO_NEW_RISK (never auto-resumed)."""
        if self._state.mode is not SafetyMode.NO_NEW_RISK:
            raise ValueError("cannot resume when no-new-risk is not active")
        if self._state.external_mutation_status is not ExternalMutationStatus.RESOLVED:
            raise ValueError("cannot resume with unresolved external mutation")
        if self._state.hard_inconsistency_latched:
            raise ValueError("cannot resume with a hard inconsistency latched")
        return self._transition(mode=SafetyMode.NORMAL, reason=reason, at=at)

    def set_unknown(self, reason: str, at: datetime) -> RealSafetyState:
        """Enter UNKNOWN when safety state cannot be established (fail closed)."""
        return self._transition(mode=SafetyMode.UNKNOWN, reason=reason, at=at)

    def restore_normal(self, reason: str, at: datetime) -> RealSafetyState:
        """Explicit manual restore from UNKNOWN to NORMAL."""
        if self._state.mode is not SafetyMode.UNKNOWN:
            raise ValueError("cannot restore normal when safety mode is not UNKNOWN")
        return self._transition(mode=SafetyMode.NORMAL, reason=reason, at=at)

    def latch_hard_inconsistency(self, reason: str, at: datetime) -> RealSafetyState:
        """Latch a persistent hard inconsistency (manual clear only)."""
        _required_timestamp(at, "hard inconsistency timestamp")
        if not reason:
            raise ValueError("hard inconsistency latch requires a reason")
        new_state = replace(
            self._state,
            hard_inconsistency_latched=True,
            hard_inconsistency_reason=reason,
            hard_inconsistency_since=at,
        )
        self._state = new_state
        return new_state

    def clear_hard_inconsistency(self, reason: str, at: datetime) -> RealSafetyState:
        """Explicit manual reset of the hard-inconsistency latch."""
        _required_timestamp(at, "hard inconsistency clear timestamp")
        if not reason:
            raise ValueError("hard inconsistency clear requires a reason")
        if not self._state.hard_inconsistency_latched:
            raise ValueError("cannot clear a hard inconsistency that is not latched")
        new_state = replace(
            self._state,
            hard_inconsistency_latched=False,
            hard_inconsistency_reason=None,
            hard_inconsistency_since=None,
        )
        self._state = new_state
        return new_state

    def record_external_mutation(self, reason: str, at: datetime) -> RealSafetyState:
        """Unresolved external/manual mutation forces NO_NEW_RISK until reconciliation.

        KILL/UNKNOWN dominate and are preserved; NORMAL/NO_NEW_RISK become
        NO_NEW_RISK. Resolution requires an explicit ``resolve_external_mutation``
        followed by an explicit ``resume``.
        """
        _required_timestamp(at, "external mutation timestamp")
        if not reason:
            raise ValueError("external mutation record requires a reason")
        current = self._state
        mode = current.mode
        if mode in (SafetyMode.NORMAL, SafetyMode.NO_NEW_RISK):
            mode = SafetyMode.NO_NEW_RISK
        new_state = replace(
            current,
            mode=mode,
            mode_reason=f"external/manual mutation unresolved: {reason}",
            mode_changed_at=at,
            external_mutation_status=ExternalMutationStatus.UNRESOLVED,
            external_mutation_since=at,
        )
        self._state = new_state
        return new_state

    def resolve_external_mutation(self, reason: str, at: datetime) -> RealSafetyState:
        """Explicit reconciliation of an unresolved mutation (no auto-resume)."""
        _required_timestamp(at, "external mutation resolve timestamp")
        if not reason:
            raise ValueError("external mutation resolve requires a reason")
        if self._state.external_mutation_status is not ExternalMutationStatus.UNRESOLVED:
            raise ValueError("cannot resolve an external mutation that is not unresolved")
        new_state = replace(
            self._state,
            external_mutation_status=ExternalMutationStatus.RESOLVED,
            external_mutation_since=None,
        )
        self._state = new_state
        return new_state

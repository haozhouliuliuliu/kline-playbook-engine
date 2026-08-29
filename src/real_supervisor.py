"""Fail-closed health/readiness supervisor for a future realtime REAL session.

OFFLINE ONLY.  The supervisor is deliberately non-consequential: it performs no
login, provider request, market subscription, broker action or order action.  It
composes caller-supplied health facts into deterministic fail-closed gates:

- ``no_new_risk`` (any UNKNOWN/UNHEALTHY input, kill/no-new-risk status, restart
  request, or an expired/revoked/mismatched authority => new risk stops);
- ``can_observe`` (market data / provider / persistence / heartbeat healthy
  enough to feed cognition);
- ``restart_required`` (persistence/journal or reconciliation requires a fresh
  restart).

It does NOT compute risk: no percentages, no position math, no capital or
margin facts.  Permanent numeric risk rules are owned elsewhere and never
embedded here.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json

from src.real_execution_authority import RealAuthoritySource

REAL_SUPERVISOR_SCHEMA_VERSION = "KPE_REAL_SUPERVISOR_V0_1"


class RealHealthInput(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


# UNHEALTHY and UNKNOWN fail closed (block new risk / observation / restart).
_HARD_FAIL_INPUTS = frozenset({RealHealthInput.UNHEALTHY, RealHealthInput.UNKNOWN})


def _hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


def _reasons(values: list[str]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


def _health(value: object, name: str) -> RealHealthInput:
    if not isinstance(value, RealHealthInput):
        raise ValueError(f"supervisor {name} must be RealHealthInput")
    return value


@dataclass(frozen=True)
class RealSupervisorAssessment:
    """Deterministic fail-closed readiness fact set (no risk calculation)."""

    assessed_at: datetime
    heartbeat: RealHealthInput
    market_data_health: RealHealthInput
    provider_health: RealHealthInput
    broker_session_health: RealHealthInput
    reconciliation_health: RealHealthInput
    persistence_health: RealHealthInput
    kill_no_new_risk: bool
    restart_requested: bool
    authority_current: bool
    no_new_risk_blockers: tuple[str, ...]
    observation_blockers: tuple[str, ...]
    restart_blockers: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.assessed_at.tzinfo is None or self.assessed_at.utcoffset() is None:
            raise ValueError("real supervisor assessment time must be timezone-aware")
        if type(self.kill_no_new_risk) is not bool or type(self.restart_requested) is not bool:
            raise ValueError("real supervisor flags must be booleans")
        if type(self.authority_current) is not bool:
            raise ValueError("real supervisor authority_current must be a boolean")
        for name in (
            "no_new_risk_blockers",
            "observation_blockers",
            "restart_blockers",
        ):
            value = getattr(self, name)
            if value != tuple(sorted(set(value))):
                raise ValueError(f"{name} must be sorted and unique")

    @property
    def no_new_risk(self) -> bool:
        return bool(self.no_new_risk_blockers)

    @property
    def can_observe(self) -> bool:
        return not self.observation_blockers

    @property
    def restart_required(self) -> bool:
        return bool(self.restart_blockers)

    @property
    def identity_id(self) -> str:
        return _hash(
            {
                "schema_version": REAL_SUPERVISOR_SCHEMA_VERSION,
                "assessed_at": self.assessed_at.isoformat(),
                "heartbeat": self.heartbeat.value,
                "market_data_health": self.market_data_health.value,
                "provider_health": self.provider_health.value,
                "broker_session_health": self.broker_session_health.value,
                "reconciliation_health": self.reconciliation_health.value,
                "persistence_health": self.persistence_health.value,
                "kill_no_new_risk": self.kill_no_new_risk,
                "restart_requested": self.restart_requested,
                "authority_current": self.authority_current,
                "no_new_risk_blockers": self.no_new_risk_blockers,
                "observation_blockers": self.observation_blockers,
                "restart_blockers": self.restart_blockers,
            }
        )

    def public_lines(self) -> tuple[str, ...]:
        return (
            f"REAL_SUPERVISOR_SCHEMA={REAL_SUPERVISOR_SCHEMA_VERSION}",
            f"REAL_SUPERVISOR_NO_NEW_RISK={self.no_new_risk}",
            f"REAL_SUPERVISOR_CAN_OBSERVE={self.can_observe}",
            f"REAL_SUPERVISOR_RESTART_REQUIRED={self.restart_required}",
            *(f"REAL_SUPERVISOR_BLOCKER_{blocker}=ACTIVE" for blocker in self.no_new_risk_blockers),
            f"REAL_SUPERVISOR_IDENTITY={self.identity_id}",
        )


class RealRuntimeSupervisor:
    """Pure health composition; never computes risk."""

    def __init__(
        self,
        *,
        authority_source: RealAuthoritySource | None = None,
        expected_authority_identity: str | None = None,
    ) -> None:
        if authority_source is not None:
            # structural duck-type check: must expose current() and source_identity
            if not hasattr(authority_source, "current") or not hasattr(authority_source, "source_identity"):
                raise TypeError("real supervisor authority source must implement RealAuthoritySource")
        if expected_authority_identity is not None and (
            not isinstance(expected_authority_identity, str)
            or not expected_authority_identity.strip()
        ):
            raise ValueError("real supervisor expected authority identity must be non-empty when supplied")
        self._authority_source = authority_source
        self._expected_authority_identity = (
            None if expected_authority_identity is None else expected_authority_identity.strip()
        )

    @property
    def authority_source(self) -> RealAuthoritySource | None:
        return self._authority_source

    @property
    def expected_authority_identity(self) -> str | None:
        return self._expected_authority_identity

    def assess(
        self,
        *,
        assessed_at: datetime,
        heartbeat: RealHealthInput = RealHealthInput.HEALTHY,
        market_data_health: RealHealthInput = RealHealthInput.HEALTHY,
        provider_health: RealHealthInput = RealHealthInput.HEALTHY,
        broker_session_health: RealHealthInput = RealHealthInput.HEALTHY,
        reconciliation_health: RealHealthInput = RealHealthInput.HEALTHY,
        persistence_health: RealHealthInput = RealHealthInput.HEALTHY,
        kill_no_new_risk: bool = False,
        restart_requested: bool = False,
    ) -> RealSupervisorAssessment:
        if assessed_at.tzinfo is None or assessed_at.utcoffset() is None:
            raise ValueError("real supervisor clock must be timezone-aware")
        inputs = {
            "heartbeat": _health(heartbeat, "heartbeat"),
            "market_data_health": _health(market_data_health, "market_data_health"),
            "provider_health": _health(provider_health, "provider_health"),
            "broker_session_health": _health(broker_session_health, "broker_session_health"),
            "reconciliation_health": _health(reconciliation_health, "reconciliation_health"),
            "persistence_health": _health(persistence_health, "persistence_health"),
        }
        if type(kill_no_new_risk) is not bool or type(restart_requested) is not bool:
            raise ValueError("real supervisor flags must be booleans")

        authority_current = True
        if self._authority_source is not None:
            authority = self._authority_source.current()
            try:
                authority.require_connect(at=assessed_at)
                authority_current = True
            except (PermissionError, ValueError):
                authority_current = False
        identity_mismatch = False
        if (
            self._authority_source is not None
            and self._expected_authority_identity is not None
        ):
            identity_mismatch = (
                self._authority_source.current().identity_id != self._expected_authority_identity
            )

        no_new_risk: list[str] = []
        for name, value in inputs.items():
            if value is RealHealthInput.UNKNOWN:
                no_new_risk.append(name.upper() + "_UNKNOWN")
            elif value is RealHealthInput.UNHEALTHY:
                no_new_risk.append(name.upper() + "_UNHEALTHY")
        if kill_no_new_risk:
            no_new_risk.append("KILL_NO_NEW_RISK")
        if restart_requested:
            no_new_risk.append("RESTART_REQUESTED")
        if not authority_current:
            no_new_risk.append("REAL_AUTHORITY_NOT_CURRENT")
        if identity_mismatch:
            no_new_risk.append("REAL_AUTHORITY_IDENTITY_MISMATCH")

        observation: list[str] = []
        for name, value in inputs.items():
            if value in _HARD_FAIL_INPUTS and name in (
                "heartbeat",
                "market_data_health",
                "provider_health",
                "persistence_health",
            ):
                observation.append(name.upper() + "_NOT_OK")
        if kill_no_new_risk:
            observation.append("KILL_NO_NEW_RISK")
        if restart_requested:
            observation.append("RESTART_REQUESTED")
        if not authority_current:
            observation.append("REAL_AUTHORITY_NOT_CURRENT")

        restart: list[str] = []
        if restart_requested:
            restart.append("RESTART_REQUESTED")
        if inputs["persistence_health"] in _HARD_FAIL_INPUTS:
            restart.append("PERSISTENCE_REQUIRES_RESTART")
        if inputs["reconciliation_health"] in _HARD_FAIL_INPUTS:
            restart.append("RECONCILIATION_REQUIRES_RESTART")

        return RealSupervisorAssessment(
            assessed_at=assessed_at,
            heartbeat=inputs["heartbeat"],
            market_data_health=inputs["market_data_health"],
            provider_health=inputs["provider_health"],
            broker_session_health=inputs["broker_session_health"],
            reconciliation_health=inputs["reconciliation_health"],
            persistence_health=inputs["persistence_health"],
            kill_no_new_risk=kill_no_new_risk,
            restart_requested=restart_requested,
            authority_current=authority_current,
            no_new_risk_blockers=_reasons(no_new_risk),
            observation_blockers=_reasons(observation),
            restart_blockers=_reasons(restart),
        )


__all__ = [
    "REAL_SUPERVISOR_SCHEMA_VERSION",
    "RealHealthInput",
    "RealRuntimeSupervisor",
    "RealSupervisorAssessment",
]

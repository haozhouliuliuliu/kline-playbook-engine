"""Smallest local REAL runtime controller / lifecycle shell.

OFFLINE ONLY.  This controller consumes the branch's REAL authority / activation
profile / config / preflight and exposes an explicit fail-closed lifecycle:

    OFFLINE -> (preflight) -> READY_TEST -> PAUSED / LOCKED / SHUTDOWN

Hard boundaries preserved here:

- default state is OFFLINE and the controller starts INACTIVE (no new risk);
- ``READY_TEST`` is the ONLY reachable ready state; this shell cannot grant
  external activation (``external_activation_authorized`` is always False);
- positive preflight is required before synthetic ``READY_TEST``;
- connection and order-execution capabilities are INJECTED and INERT: the
  controller stores them and never invokes them;
- expired/revoked/mismatched authority and unresolved caller-supplied
  wake/order/account/reconciliation state fail closed;
- shutdown/pause/no-new-risk transitions are deterministic;
- a test fixture authority is never treated as an external execution authority.

This module performs no login, no broker/account/order action, no provider call
and no network action.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json

from src.real_activation_profile import RealActivationProfile, RealActivationStatus
from src.real_execution_authority import (
    MutableRealAuthoritySource,
    RealAuthoritySource,
    RealAuthorityStatus,
    RealExecutionAuthority,
)
from src.real_preflight import (
    EXTERNAL,
    STRUCTURAL,
    RealDurableState,
    RealPreflightReport,
    run_real_preflight,
)
from src.real_runtime_config import RealRuntimeConfig
from src.real_supervisor import RealHealthInput, RealRuntimeSupervisor, RealSupervisorAssessment

REAL_RUNTIME_CONTROLLER_VERSION = "KPE_REAL_RUNTIME_CONTROLLER_V0_1"

_MODES = frozenset({EXTERNAL, STRUCTURAL})

# States that are never "ready" and always imply no new risk.
_NON_READY_STATES = frozenset(
    {
        "OFFLINE",
        "LOCKED",
        "PREFLIGHT_FAILED",
        "PAUSED",
        "SHUTDOWN",
    }
)


class RealLifecycleState(str, Enum):
    OFFLINE = "OFFLINE"
    LOCKED = "LOCKED"
    PREFLIGHT_FAILED = "PREFLIGHT_FAILED"
    READY_TEST = "READY_TEST"
    PAUSED = "PAUSED"
    SHUTDOWN = "SHUTDOWN"


def _hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False)
    return sha256(encoded.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RealControllerStateSnapshot:
    """Immutable, machine-readable controller state snapshot."""

    version: str
    state: str
    no_new_risk: bool
    test_ready: bool
    external_activation_authorized: bool
    preflight_receipt_ready: bool | None
    fail_closed_blockers: tuple[str, ...]

    @property
    def identity_id(self) -> str:
        return _hash(
            {
                "version": self.version,
                "state": self.state,
                "no_new_risk": self.no_new_risk,
                "test_ready": self.test_ready,
                "external_activation_authorized": self.external_activation_authorized,
                "preflight_receipt_ready": self.preflight_receipt_ready,
                "fail_closed_blockers": self.fail_closed_blockers,
            }
        )


class RealRuntimeController:
    """Local single-owner REAL startup/lifecycle shell (test-ready only)."""

    def __init__(
        self,
        *,
        config: RealRuntimeConfig,
        authority: RealExecutionAuthority | None = None,
        activation_profile: RealActivationProfile | None = None,
        authority_source: RealAuthoritySource | None = None,
        connection: object | None = None,
        order_execution: object | None = None,
        supervisor: RealRuntimeSupervisor | None = None,
        mode: str = STRUCTURAL,
    ) -> None:
        if not isinstance(config, RealRuntimeConfig):
            raise TypeError("real runtime controller requires RealRuntimeConfig")
        if authority is None:
            authority = config.authority
        if activation_profile is None:
            activation_profile = config.activation_profile
        if authority is not None and not isinstance(authority, RealExecutionAuthority):
            raise TypeError("real runtime controller authority must be RealExecutionAuthority")
        if activation_profile is not None and not isinstance(activation_profile, RealActivationProfile):
            raise TypeError("real runtime controller activation profile must be RealActivationProfile")
        if mode not in _MODES:
            raise ValueError("real runtime controller mode must be EXTERNAL or STRUCTURAL")
        if authority_source is None:
            if authority is not None:
                authority_source = MutableRealAuthoritySource(
                    authority, source_identity="REAL_CONTROLLER_STATIC_SOURCE"
                )
        elif not hasattr(authority_source, "current") or not hasattr(authority_source, "source_identity"):
            raise TypeError("real runtime controller authority source must implement RealAuthoritySource")
        self._config = config
        self._authority = authority
        self._activation_profile = activation_profile
        self._authority_source = authority_source
        self._connection = connection
        self._order_execution = order_execution
        self._supervisor = supervisor or RealRuntimeSupervisor(
            authority_source=self._authority_source,
            expected_authority_identity=(
                None if self._authority is None else self._authority.identity_id
            ),
        )
        self._mode = mode
        self._state = RealLifecycleState.OFFLINE
        self._preflight_receipt: RealPreflightReport | None = None
        self._last_assessed_at: datetime | None = None
        self._last_assessment: RealSupervisorAssessment | None = None

    # ------------------------------------------------------------------ state

    @property
    def state(self) -> RealLifecycleState:
        return self._state

    @property
    def config(self) -> RealRuntimeConfig:
        return self._config

    @property
    def authority(self) -> RealExecutionAuthority | None:
        return self._authority

    @property
    def activation_profile(self) -> RealActivationProfile | None:
        return self._activation_profile

    @property
    def authority_source(self) -> RealAuthoritySource | None:
        return self._authority_source

    @property
    def supervisor(self) -> RealRuntimeSupervisor:
        return self._supervisor

    @property
    def connection(self) -> object | None:
        """Injected inert connection capability; never invoked by this shell."""
        return self._connection

    @property
    def order_execution(self) -> object | None:
        """Injected inert order-execution capability; never invoked by this shell."""
        return self._order_execution

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def preflight_receipt(self) -> RealPreflightReport | None:
        return self._preflight_receipt

    @property
    def test_ready(self) -> bool:
        return self._state is RealLifecycleState.READY_TEST

    @property
    def external_activation_authorized(self) -> bool:
        """Always False: this offline shell never grants external activation."""
        return False

    @property
    def no_new_risk(self) -> bool:
        """Fail-closed new-risk gate: True unless test-ready with a clean assessment."""
        if self._state is not RealLifecycleState.READY_TEST:
            return True
        if self._last_assessment is None:
            return True
        return self._last_assessment.no_new_risk

    # ------------------------------------------------------------- preflight

    def preflight(
        self,
        *,
        assessed_at: datetime,
        order_state: RealDurableState,
        wake_state: RealDurableState,
        account_state: RealDurableState,
        reconciliation_state: RealDurableState,
        mode: str | None = None,
    ) -> RealPreflightReport:
        """Read-only REAL preflight (never reaches broker/account)."""
        if mode is None:
            mode = self._mode
        if mode not in _MODES:
            raise ValueError("real controller preflight mode must be EXTERNAL or STRUCTURAL")
        report = run_real_preflight(
            config=self._config,
            activation_profile=self._activation_profile,
            authority=self._authority,
            mode=mode,
            assessed_at=assessed_at,
            order_state=order_state,
            wake_state=wake_state,
            reconciliation_state=reconciliation_state,
        )
        self._preflight_receipt = report
        self._last_assessed_at = assessed_at
        if not report.ready:
            self._state = RealLifecycleState.PREFLIGHT_FAILED
        elif self._state is RealLifecycleState.PREFLIGHT_FAILED:
            self._state = RealLifecycleState.OFFLINE
        return report

    def activate_for_test(self, *, at: datetime | None = None) -> RealLifecycleState:
        """Reach READY_TEST only after a positive preflight and a current authority.

        This is synthetic/structural readiness; it never grants external
        activation.  A missing or blocked preflight, a non-ACTIVE/expired/
        revoked authority, or a synthetic authority in EXTERNAL mode fail
        closed.
        """
        if self._state is RealLifecycleState.SHUTDOWN:
            raise RuntimeError("REAL_CONTROLLER_SHUTDOWN")
        receipt = self._preflight_receipt
        if receipt is None or not receipt.ready:
            self._state = RealLifecycleState.PREFLIGHT_FAILED
            raise PermissionError("REAL_POSITIVE_PREFLIGHT_REQUIRED")
        if self._mode == EXTERNAL and self._authority is not None and self._authority.test_only:
            self._state = RealLifecycleState.PREFLIGHT_FAILED
            raise PermissionError("REAL_SYNTHETIC_AUTHORITY_FORBIDDEN_IN_EXTERNAL")
        if self._authority is not None:
            check_at = at if at is not None else self._last_assessed_at
            try:
                self._authority.require_connect(at=check_at)
            except (PermissionError, ValueError) as error:
                self._state = RealLifecycleState.LOCKED
                raise PermissionError("REAL_AUTHORITY_NOT_CURRENT:" + str(error)) from error
        self._state = RealLifecycleState.READY_TEST
        return self._state

    # ------------------------------------------------------------ transitions

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
        """Read-only supervisor composition; updates the new-risk gate only.

        Does not change the lifecycle state: transitions (pause/shutdown/
        request_restart) remain explicit.  When the assessment reports
        ``no_new_risk``, the controller's ``no_new_risk`` property becomes True
        until a later clean assessment, so new risk stops immediately.
        """
        assessment = self._supervisor.assess(
            assessed_at=assessed_at,
            heartbeat=heartbeat,
            market_data_health=market_data_health,
            provider_health=provider_health,
            broker_session_health=broker_session_health,
            reconciliation_health=reconciliation_health,
            persistence_health=persistence_health,
            kill_no_new_risk=kill_no_new_risk,
            restart_requested=restart_requested,
        )
        self._last_assessment = assessment
        return assessment

    def pause(self) -> RealLifecycleState:
        """Deterministic pause: no new risk until a fresh positive preflight."""
        self._state = RealLifecycleState.PAUSED
        return self._state

    def shutdown(self) -> RealLifecycleState:
        """Deterministic shutdown: terminal, no new risk, no further activation."""
        self._state = RealLifecycleState.SHUTDOWN
        return self._state

    def request_restart(self) -> RealLifecycleState:
        """Restart decision: LOCKED until a fresh preflight/reconciliation.

        Clears the prior preflight receipt so resume/activation requires a
        fresh positive preflight.
        """
        self._state = RealLifecycleState.LOCKED
        self._preflight_receipt = None
        self._last_assessment = None
        return self._state

    # -------------------------------------------------------- fail-closed view

    def fail_closed_blockers(self) -> tuple[str, ...]:
        blockers: list[str] = []
        if self._authority is None:
            blockers.append("REAL_AUTHORITY_UNBOUND")
        elif self._authority.status is not RealAuthorityStatus.ACTIVE:
            blockers.append("REAL_AUTHORITY_NOT_ACTIVE")
        if self._activation_profile is None:
            blockers.append("REAL_ACTIVATION_PROFILE_UNBOUND")
        elif self._activation_profile.status is not RealActivationStatus.ACTIVE:
            blockers.append("REAL_ACTIVATION_PROFILE_NOT_ACTIVE")
        if self._preflight_receipt is None:
            blockers.append("POSITIVE_PREFLIGHT_REQUIRED")
        elif not self._preflight_receipt.ready:
            blockers.append("PREFLIGHT_NOT_READY")
        if self._state in _NON_READY_STATES:
            blockers.append("CONTROLLER_NOT_READY:" + self._state.value)
        if self.no_new_risk:
            blockers.append("NO_NEW_RISK")
        if self._mode == EXTERNAL and self._authority is not None and self._authority.test_only:
            blockers.append("REAL_SYNTHETIC_AUTHORITY_FORBIDDEN_IN_EXTERNAL")
        return tuple(sorted(set(blockers)))

    def snapshot(self) -> RealControllerStateSnapshot:
        return RealControllerStateSnapshot(
            version=REAL_RUNTIME_CONTROLLER_VERSION,
            state=self._state.value,
            no_new_risk=self.no_new_risk,
            test_ready=self.test_ready,
            external_activation_authorized=self.external_activation_authorized,
            preflight_receipt_ready=(
                None if self._preflight_receipt is None else self._preflight_receipt.ready
            ),
            fail_closed_blockers=self.fail_closed_blockers(),
        )


__all__ = [
    "REAL_RUNTIME_CONTROLLER_VERSION",
    "RealControllerStateSnapshot",
    "RealLifecycleState",
    "RealRuntimeController",
]

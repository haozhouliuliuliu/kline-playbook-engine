"""Offline admission control for future realtime provider requests.

OFFLINE ONLY.  This module is the deterministic gate that decides whether one
governed future 5-minute wake may proceed to a single provider attempt.  It
performs NO provider call, NO network action and NO DeepSeek request.  It
composes:

- a durable :class:`RealtimeProviderAttemptLedger` (one admitted attempt per
  wake, zero retries, unknown-after-crash never silently retried), and
- caller-supplied budget/usage facts (never invented here).

Monetary and request ceilings are future authority INPUTS.  No ceiling number
is invented in this module: ``request_count_ceiling`` is ``None`` by default and
``monetary_certainty`` defaults to False (exact tariff unavailable => monetary
certainty UNKNOWN).  A hard request-count ceiling, when supplied, is separately
enforced as a deterministic stop-before-next-request gate.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.realtime_provider_attempt_ledger import (
    ATTEMPT_STARTED,
    AUTHORITY_IDENTITY_MISMATCH,
    DEFAULT_RETRY_COUNT,
    DuplicateWakeAttemptError,
    UNKNOWN_AFTER_ATTEMPT_START,
    RealtimeAttemptIdentity,
    RealtimeProviderAttempt,
    RealtimeProviderAttemptLedger,
)

REALTIME_PROVIDER_CONTROL_VERSION = "KPE_REALTIME_PROVIDER_CONTROL_V0_1"


@dataclass(frozen=True)
class RealtimeBudgetInput:
    """Usage/budget facts supplied by the caller (a future exact authority).

    ``request_count_ceiling`` is a hard request-count ceiling when supplied
    (``None`` means no ceiling, never an invented default number).
    ``monetary_certainty`` is False when the exact tariff is unavailable, which
    makes monetary status UNKNOWN.  ``monetary_stop`` is an explicit caller
    decision that monetary spend must stop.
    """

    admitted_attempt_count: int = 0
    request_count_ceiling: int | None = None
    monetary_certainty: bool = False
    monetary_stop: bool | None = None

    def __post_init__(self) -> None:
        if type(self.admitted_attempt_count) is not int or self.admitted_attempt_count < 0:
            raise ValueError("realtime budget admitted attempt count must be a non-negative integer")
        if self.request_count_ceiling is not None and (
            type(self.request_count_ceiling) is not int or self.request_count_ceiling <= 0
        ):
            raise ValueError("realtime budget request count ceiling must be a positive integer when supplied")
        if type(self.monetary_certainty) is not bool:
            raise ValueError("realtime budget monetary certainty must be a boolean")
        if self.monetary_stop is not None and type(self.monetary_stop) is not bool:
            raise ValueError("realtime budget monetary stop must be a boolean when supplied")

    @property
    def request_count_exhausted(self) -> bool:
        return (
            self.request_count_ceiling is not None
            and self.admitted_attempt_count >= self.request_count_ceiling
        )

    @property
    def monetary_unknown(self) -> bool:
        return not self.monetary_certainty

    @property
    def monetary_exhausted(self) -> bool:
        return self.monetary_stop is True

    @property
    def stop_reasons(self) -> tuple[str, ...]:
        reasons: list[str] = []
        if self.request_count_exhausted:
            reasons.append("REQUEST_COUNT_CEILING_EXHAUSTED")
        if self.monetary_exhausted:
            reasons.append("MONETARY_CEILING_EXHAUSTED")
        return tuple(sorted(set(reasons)))

    @property
    def can_continue(self) -> bool:
        return not self.stop_reasons


@dataclass(frozen=True)
class RealtimeAdmissionResult:
    """Deterministic admission outcome for one wake."""

    wake_identity: str
    admitted: bool
    attempt_identity: str | None = None
    duplicate_wake: bool = False
    unknown_persists: bool = False
    stop_reasons: tuple[str, ...] = ()
    monetary_certainty: bool = False

    def __post_init__(self) -> None:
        for name in ("wake_identity",):
            if not isinstance(getattr(self, name), str) or not getattr(self, name).strip():
                raise ValueError(f"{name} must be non-empty")
        if type(self.admitted) is not bool or type(self.duplicate_wake) is not bool:
            raise ValueError("realtime admission flags must be booleans")
        if type(self.unknown_persists) is not bool or type(self.monetary_certainty) is not bool:
            raise ValueError("realtime admission flags must be booleans")
        if self.attempt_identity is not None and (
            not isinstance(self.attempt_identity, str) or not self.attempt_identity.strip()
        ):
            raise ValueError("attempt identity must be non-empty when supplied")
        if self.stop_reasons != tuple(sorted(set(self.stop_reasons))):
            raise ValueError("stop reasons must be sorted and unique")

    @property
    def stop_before_next_request(self) -> bool:
        return bool(self.stop_reasons)


class RealtimeProviderControl:
    """Offline gate: at most one admitted provider attempt per wake, zero retries.

    Never calls a provider.  ``admit`` is the only path that records an
    admitted attempt; a duplicate/replayed wake and an unknown-persisting prior
    attempt both fail closed with ``admitted=False``.
    """

    def __init__(
        self,
        *,
        ledger: RealtimeProviderAttemptLedger,
        retry_count: int = DEFAULT_RETRY_COUNT,
    ) -> None:
        if not isinstance(ledger, RealtimeProviderAttemptLedger):
            raise TypeError("realtime provider control requires RealtimeProviderAttemptLedger")
        if type(retry_count) is not int or retry_count != DEFAULT_RETRY_COUNT:
            raise ValueError("realtime provider control retry count must remain fixed at zero")
        self._ledger = ledger
        self._retry_count = retry_count

    @property
    def ledger(self) -> RealtimeProviderAttemptLedger:
        return self._ledger

    @property
    def retry_count(self) -> int:
        return self._retry_count

    def admit(
        self,
        *,
        identity: RealtimeAttemptIdentity,
        budget: RealtimeBudgetInput,
    ) -> RealtimeAdmissionResult:
        """Attempt to admit one provider attempt for a governed wake.

        Fails closed (never admits) when the budget says stop, when the wake
        already owns an admitted attempt, or when a prior attempt for the wake
        is unresolved (crash after admit, unknown response): the unknown is
        preserved and NEVER silently retried.
        """
        if not isinstance(identity, RealtimeAttemptIdentity):
            raise TypeError("realtime admission requires RealtimeAttemptIdentity")
        if not isinstance(budget, RealtimeBudgetInput):
            raise TypeError("realtime admission requires RealtimeBudgetInput")
        if identity.authority_identity != self._ledger.authority_identity:
            return RealtimeAdmissionResult(
                wake_identity=identity.wake_identity,
                admitted=False,
                stop_reasons=(AUTHORITY_IDENTITY_MISMATCH,),
                monetary_certainty=budget.monetary_certainty,
            )

        existing = self._ledger.attempt_for_wake(identity.wake_identity)
        if existing is not None:
            unknown_persists = existing.attempt_state in (ATTEMPT_STARTED, UNKNOWN_AFTER_ATTEMPT_START)
            return RealtimeAdmissionResult(
                wake_identity=identity.wake_identity,
                admitted=False,
                attempt_identity=existing.attempt_identity,
                duplicate_wake=True,
                unknown_persists=unknown_persists,
                stop_reasons=budget.stop_reasons,
                monetary_certainty=budget.monetary_certainty,
            )
        if budget.stop_reasons:
            return RealtimeAdmissionResult(
                wake_identity=identity.wake_identity,
                admitted=False,
                stop_reasons=budget.stop_reasons,
                monetary_certainty=budget.monetary_certainty,
            )
        try:
            self._ledger.record_attempt_started(identity=identity, retry_count=self._retry_count)
        except DuplicateWakeAttemptError:
            # A concurrent/duplicate insert lost the race: fail closed.
            existing = self._ledger.attempt_for_wake(identity.wake_identity)
            unknown_persists = existing is not None and existing.attempt_state in (
                ATTEMPT_STARTED,
                UNKNOWN_AFTER_ATTEMPT_START,
            )
            return RealtimeAdmissionResult(
                wake_identity=identity.wake_identity,
                admitted=False,
                attempt_identity=None if existing is None else existing.attempt_identity,
                duplicate_wake=True,
                unknown_persists=unknown_persists,
                stop_reasons=budget.stop_reasons,
                monetary_certainty=budget.monetary_certainty,
            )
        return RealtimeAdmissionResult(
            wake_identity=identity.wake_identity,
            admitted=True,
            attempt_identity=identity.identity_id,
            stop_reasons=budget.stop_reasons,
            monetary_certainty=budget.monetary_certainty,
        )

    def record_result(self, *, attempt_identity: str, metadata: dict[str, object]) -> RealtimeProviderAttempt:
        return self._ledger.record_result_received(attempt_identity=attempt_identity, metadata=metadata)

    def record_unknown(self, *, attempt_identity: str, reason: str) -> RealtimeProviderAttempt:
        return self._ledger.record_unknown_after_attempt_start(
            attempt_identity=attempt_identity, reason=reason
        )

    def attempts(self) -> tuple[RealtimeProviderAttempt, ...]:
        return self._ledger.attempts()

    def unresolved_count(self) -> int:
        return self._ledger.unresolved_attempt_started_count()

    def unknown_count(self) -> int:
        return self._ledger.unknown_after_attempt_start_count()

    def result_count(self) -> int:
        return self._ledger.result_received_count()

    def admitted_attempt_count(self) -> int:
        return self._ledger.admitted_attempt_count()


__all__ = [
    "REALTIME_PROVIDER_CONTROL_VERSION",
    "RealtimeAdmissionResult",
    "RealtimeBudgetInput",
    "RealtimeProviderControl",
]

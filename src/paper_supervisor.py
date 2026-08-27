"""Fail-closed startup/readiness supervisor for future realtime PAPER.

The supervisor is deliberately non-consequential: it performs no login, provider
request, market subscription or order action.  It composes already project-owned
facts into three separate gates:

1. connection eligibility;
2. realtime trader observation eligibility;
3. external PAPER order eligibility.

This separation lets a future exact authority enable account connectivity and
DeepSeek market observation while order submission remains closed until the
activation profile, broker truth, market continuity and order/wake state are all
explicitly clean.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json

from src.paper_activation_profile import PaperActivationProfile
from src.paper_broker_mirror import PaperBrokerTruthMirror
from src.paper_execution_authority import PaperExecutionAuthority
from src.paper_order_journal import PaperOrderJournal
from src.paper_wake_journal import PaperWakeJournal

PAPER_SUPERVISOR_SCHEMA_VERSION = "KPE_PAPER_SUPERVISOR_V0_1"


def _hash(value: object) -> str:
    encoded = json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    )
    return sha256(encoded.encode("utf-8")).hexdigest()


def _reasons(values: list[str]) -> tuple[str, ...]:
    return tuple(sorted(set(values)))


@dataclass(frozen=True)
class PaperSupervisorAssessment:
    assessed_at: datetime
    connect_blockers: tuple[str, ...]
    observation_blockers: tuple[str, ...]
    order_blockers: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.assessed_at.tzinfo is None or self.assessed_at.utcoffset() is None:
            raise ValueError("paper supervisor assessment time must be timezone-aware")
        for name in ("connect_blockers", "observation_blockers", "order_blockers"):
            value = getattr(self, name)
            if value != tuple(sorted(set(value))):
                raise ValueError(f"{name} must be sorted and unique")

    @property
    def can_connect(self) -> bool:
        return not self.connect_blockers

    @property
    def can_observe(self) -> bool:
        return not self.observation_blockers

    @property
    def can_submit_order(self) -> bool:
        return not self.order_blockers

    @property
    def identity_id(self) -> str:
        return _hash(
            {
                "schema_version": PAPER_SUPERVISOR_SCHEMA_VERSION,
                "assessed_at": self.assessed_at.isoformat(),
                "connect_blockers": self.connect_blockers,
                "observation_blockers": self.observation_blockers,
                "order_blockers": self.order_blockers,
            }
        )

    def require_observation_ready(self) -> None:
        if self.observation_blockers:
            raise PermissionError(
                "PAPER_OBSERVATION_NOT_READY:" + ";".join(self.observation_blockers)
            )

    def require_order_ready(self) -> None:
        if self.order_blockers:
            raise PermissionError(
                "PAPER_ORDER_NOT_READY:" + ";".join(self.order_blockers)
            )


class PaperRuntimeSupervisor:
    """Pure readiness composition over exact authority and runtime truth."""

    def __init__(
        self,
        *,
        actual_tqsdk_runtime_version: str,
        authority: PaperExecutionAuthority,
        activation_profile: PaperActivationProfile,
        broker_mirror: PaperBrokerTruthMirror,
        order_journal: PaperOrderJournal,
        wake_journal: PaperWakeJournal,
    ) -> None:
        if not isinstance(actual_tqsdk_runtime_version, str) or not actual_tqsdk_runtime_version.strip():
            raise ValueError("paper supervisor requires actual TqSdk runtime version")
        if not isinstance(authority, PaperExecutionAuthority):
            raise ValueError("paper supervisor requires PaperExecutionAuthority")
        if not isinstance(activation_profile, PaperActivationProfile):
            raise ValueError("paper supervisor requires PaperActivationProfile")
        if not isinstance(broker_mirror, PaperBrokerTruthMirror):
            raise ValueError("paper supervisor requires PaperBrokerTruthMirror")
        if not isinstance(order_journal, PaperOrderJournal):
            raise ValueError("paper supervisor requires PaperOrderJournal")
        if not isinstance(wake_journal, PaperWakeJournal):
            raise ValueError("paper supervisor requires PaperWakeJournal")
        self._actual_tqsdk_runtime_version = actual_tqsdk_runtime_version.strip()
        self._authority = authority
        self._activation_profile = activation_profile
        self._broker_mirror = broker_mirror
        self._order_journal = order_journal
        self._wake_journal = wake_journal

    def assess(
        self,
        *,
        assessed_at: datetime,
        market_bootstrapped: bool,
        market_sequence_ok: bool,
        trader_runtime_ready: bool,
        max_broker_snapshot_age_seconds: int,
        concrete_contract_id: str | None = None,
    ) -> PaperSupervisorAssessment:
        if assessed_at.tzinfo is None or assessed_at.utcoffset() is None:
            raise ValueError("paper supervisor clock must be timezone-aware")
        for value, name in (
            (market_bootstrapped, "market_bootstrapped"),
            (market_sequence_ok, "market_sequence_ok"),
            (trader_runtime_ready, "trader_runtime_ready"),
        ):
            if type(value) is not bool:
                raise ValueError(f"{name} must be bool")
        if type(max_broker_snapshot_age_seconds) is not int or max_broker_snapshot_age_seconds < 0:
            raise ValueError("broker snapshot age must be a non-negative integer")
        if concrete_contract_id is not None and (
            not isinstance(concrete_contract_id, str) or not concrete_contract_id.strip()
        ):
            raise ValueError("paper order contract must be non-empty when supplied")

        connect: list[str] = []
        if self._actual_tqsdk_runtime_version != self._activation_profile.tqsdk_runtime_version:
            connect.append("TQSDK_RUNTIME_VERSION_MISMATCH")
        try:
            self._authority.require_connect()
        except PermissionError:
            connect.append("PAPER_CONNECT_AUTHORITY_INACTIVE")

        observation = list(connect)
        mirror = self._broker_mirror.assess(
            expected_client_request_ids=self._order_journal.expected_client_request_ids(),
            assessed_at=assessed_at,
            max_snapshot_age_seconds=max_broker_snapshot_age_seconds,
        )
        observation.extend(f"BROKER_MIRROR:{reason}" for reason in mirror.reasons)
        if not market_bootstrapped:
            observation.append("LIVE_MARKET_NOT_BOOTSTRAPPED")
        if not market_sequence_ok:
            observation.append("LIVE_MARKET_SEQUENCE_NOT_CLEAN")
        if not trader_runtime_ready:
            observation.append("TRADER_RUNTIME_NOT_READY")
        if self._wake_journal.unresolved_dispatches():
            observation.append("UNRESOLVED_TRADER_WAKE_DISPATCH")

        order = list(observation)
        if concrete_contract_id is None:
            order.append("PAPER_ORDER_CONTRACT_REQUIRED")
        else:
            try:
                self._activation_profile.require_active_for(concrete_contract_id)
            except PermissionError as error:
                order.append(str(error))
            try:
                self._authority.require_order_submit(concrete_contract_id)
            except PermissionError as error:
                order.append(str(error))
        if self._order_journal.unresolved_attempts():
            order.append("UNRESOLVED_PAPER_ORDER_SUBMISSION")

        return PaperSupervisorAssessment(
            assessed_at=assessed_at,
            connect_blockers=_reasons(connect),
            observation_blockers=_reasons(observation),
            order_blockers=_reasons(order),
        )

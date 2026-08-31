"""Machine-verifiable gates for a future REAL broker execution session.

OFFLINE ONLY.  This module is ordinary offline engineering for the future REAL
execution path.  It does not itself authorize any broker/account action, and no
REAL broker transport or REAL authority currently exists in the project.  A
future exact Owner/machine authority must create an ACTIVE value at the
consequential boundary; a missing authority remains a hard activation blocker.

This authority is deliberately kept semantically separate from the accepted
PAPER authority.  It models credential readiness only through an abstract
SET/UNSET-style input (never a name, location or value), because
TOOL_REGISTRY.md does not yet define a Fangzheng real-broker credential seam
and this module must not invent environment-variable names.  It also never
embeds permanent numeric risk rules: risk is referenced through a separate
risk-policy identity and the only numeric field is an optional maximum-position
binding that requires separate approval.

Importing or constructing this module performs zero network, provider,
credential, account-login, order or broker action.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json
from typing import Protocol

REAL_EXECUTION_AUTHORITY_SCHEMA_VERSION = "KPE_REAL_EXECUTION_AUTHORITY_V0_1"

_EXECUTION_MODE = "REAL"

_ORDER_ACTION_CLASSES = frozenset(
    {"ORDER_SUBMIT", "ORDER_CANCEL", "ORDER_REPLACE"}
)


class RealAuthorityStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    DISABLED = "DISABLED"


class RealActionClass(str, Enum):
    """Explicit allowed action classes for a REAL session.

    Order action classes always imply CONNECT.  An ACTIVE authority with no
    action classes grants nothing.
    """

    CONNECT = "CONNECT"
    ORDER_SUBMIT = "ORDER_SUBMIT"
    ORDER_CANCEL = "ORDER_CANCEL"
    ORDER_REPLACE = "ORDER_REPLACE"


class RealCredentialReadiness(str, Enum):
    """Abstract credential readiness; never a name, location or value."""

    UNSPECIFIED = "UNSPECIFIED"
    SET = "SET"
    UNSET = "UNSET"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _require_non_empty_text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{name} must be a non-empty canonical string")
    return value.strip()


@dataclass(frozen=True)
class RealExecutionAuthority:
    """Exact machine gate for future REAL broker/account actions.

    Default construction grants nothing: status defaults to PENDING, action
    classes are empty, and every binding is absent.  Consequential checks fail
    closed unless the authority is ACTIVE, within its bounded validity, with
    the requested action explicitly allowed and the required bindings present.
    """

    authority_id: str
    broker_kind: str
    account_kind: str
    status: RealAuthorityStatus
    execution_mode: str = _EXECUTION_MODE
    broker_adapter_identity: str | None = None
    account_identity: str | None = None
    risk_policy_identity: str | None = None
    executable_identity: str | None = None
    allowed_action_classes: tuple[RealActionClass, ...] = ()
    allowed_contracts: tuple[str, ...] = ()
    credential_readiness: RealCredentialReadiness = RealCredentialReadiness.UNSPECIFIED
    valid_from: datetime | None = None
    expires_at: datetime | None = None
    max_position_lots: int | None = None
    test_only: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "authority_id", _require_non_empty_text(self.authority_id, "real authority id"))
        object.__setattr__(self, "broker_kind", _require_non_empty_text(self.broker_kind, "real broker kind"))
        object.__setattr__(self, "account_kind", _require_non_empty_text(self.account_kind, "real account kind"))
        if self.execution_mode != _EXECUTION_MODE:
            raise ValueError("real execution authority execution_mode must be REAL")
        if not isinstance(self.status, RealAuthorityStatus):
            raise ValueError("real authority status must be explicit")
        if not isinstance(self.credential_readiness, RealCredentialReadiness):
            raise ValueError("real credential readiness must be explicit")
        if type(self.test_only) is not bool:
            raise ValueError("real authority test_only must be a boolean")
        if not isinstance(self.allowed_action_classes, tuple):
            raise ValueError("real allowed action classes must be a tuple")
        for action in self.allowed_action_classes:
            if not isinstance(action, RealActionClass):
                raise ValueError("real allowed action classes must be RealActionClass values")
        if len(self.allowed_action_classes) != len(set(self.allowed_action_classes)):
            raise ValueError("real allowed action classes must be unique")
        if any(action.value in _ORDER_ACTION_CLASSES for action in self.allowed_action_classes):
            if RealActionClass.CONNECT not in self.allowed_action_classes:
                raise ValueError("real order action permission requires connect permission")
        for contract in self.allowed_contracts:
            _require_non_empty_text(contract, "real allowed contract")
        if len(self.allowed_contracts) != len(set(self.allowed_contracts)):
            raise ValueError("real allowed contracts must be unique")
        for value, name in (
            (self.broker_adapter_identity, "real broker-adapter identity"),
            (self.account_identity, "real account identity"),
            (self.risk_policy_identity, "real risk-policy identity"),
            (self.executable_identity, "real executable identity"),
        ):
            if value is not None:
                _require_non_empty_text(value, name)
        for value, name in ((self.valid_from, "valid_from"), (self.expires_at, "expires_at")):
            if value is not None and (
                not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None
            ):
                raise ValueError(f"real authority {name} must be timezone-aware")
        if self.valid_from is not None and self.expires_at is not None and self.expires_at <= self.valid_from:
            raise ValueError("real authority expiry must follow its valid-from time")
        if self.max_position_lots is not None and (
            type(self.max_position_lots) is not int or self.max_position_lots <= 0
        ):
            raise ValueError("real authority max position lots must be a positive integer when bound")
        # Construction remains side-effect-free and can represent incomplete
        # draft authority.  Consequential gates reject every missing binding;
        # preflight reports the same defects before any activation.  An ACTIVE
        # authority must be fully bound so that it never silently degrades.
        if self.status is RealAuthorityStatus.ACTIVE:
            if not self.allowed_action_classes:
                raise ValueError("ACTIVE real authority requires at least one allowed action class")
            if any(value is None for value in (
                self.broker_adapter_identity,
                self.account_identity,
                self.risk_policy_identity,
                self.executable_identity,
                self.valid_from,
                self.expires_at,
            )):
                raise ValueError("ACTIVE real authority requires every required binding")
            if not self.allowed_contracts:
                raise ValueError("ACTIVE real authority requires at least one allowed contract")
            if self.credential_readiness is not RealCredentialReadiness.SET:
                raise ValueError("ACTIVE real authority requires SET credential readiness")

    @property
    def identity_id(self) -> str:
        payload = {
            "schema_version": REAL_EXECUTION_AUTHORITY_SCHEMA_VERSION,
            "authority_id": self.authority_id,
            "broker_kind": self.broker_kind,
            "account_kind": self.account_kind,
            "status": self.status.value,
            "execution_mode": self.execution_mode,
            "broker_adapter_identity": self.broker_adapter_identity,
            "account_identity": self.account_identity,
            "risk_policy_identity": self.risk_policy_identity,
            "executable_identity": self.executable_identity,
            "allowed_action_classes": sorted(action.value for action in self.allowed_action_classes),
            "allowed_contracts": sorted(self.allowed_contracts),
            "credential_readiness": self.credential_readiness.value,
            "valid_from": None if self.valid_from is None else self.valid_from.isoformat(),
            "expires_at": None if self.expires_at is None else self.expires_at.isoformat(),
            "max_position_lots": self.max_position_lots,
            "test_only": self.test_only,
        }
        return sha256(_canonical_json(payload).encode("utf-8")).hexdigest()

    def _require_current(
        self,
        *,
        at: datetime,
        broker_adapter_identity: str | None,
        account_identity: str | None,
    ) -> None:
        if self.status is not RealAuthorityStatus.ACTIVE:
            raise PermissionError("REAL_AUTHORITY_NOT_ACTIVE")
        if self.credential_readiness is not RealCredentialReadiness.SET:
            raise PermissionError("REAL_CREDENTIAL_READINESS_NOT_SET")
        if self.valid_from is None or self.expires_at is None:
            raise PermissionError("REAL_AUTHORITY_NOT_BOUNDED")
        if not isinstance(at, datetime) or at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("real authority check time must be timezone-aware")
        if not (self.valid_from <= at < self.expires_at):
            raise PermissionError("REAL_AUTHORITY_NOT_CURRENT")
        if broker_adapter_identity is not None and (
            self.broker_adapter_identity is None or broker_adapter_identity != self.broker_adapter_identity
        ):
            raise PermissionError("REAL_BROKER_ADAPTER_IDENTITY_NOT_AUTHORIZED")
        if account_identity is not None and (
            self.account_identity is None or account_identity != self.account_identity
        ):
            raise PermissionError("REAL_ACCOUNT_IDENTITY_NOT_AUTHORIZED")

    def require_action(
        self,
        action_class: RealActionClass,
        *,
        at: datetime,
        concrete_contract_id: str | None = None,
        broker_adapter_identity: str | None = None,
        account_identity: str | None = None,
    ) -> None:
        if not isinstance(action_class, RealActionClass):
            raise ValueError("real action class must be explicit")
        if at is None:
            raise ValueError("real authority check requires an assessment time")
        if self.status is not RealAuthorityStatus.ACTIVE:
            raise PermissionError("REAL_AUTHORITY_NOT_ACTIVE")
        if action_class not in self.allowed_action_classes:
            raise PermissionError("REAL_ACTION_NOT_AUTHORIZED:" + action_class.value)
        if action_class.value in _ORDER_ACTION_CLASSES:
            if RealActionClass.CONNECT not in self.allowed_action_classes:
                raise PermissionError("REAL_ORDER_ACTION_REQUIRES_CONNECT")
            self._require_current(
                at=at, broker_adapter_identity=broker_adapter_identity, account_identity=account_identity
            )
            if action_class is RealActionClass.ORDER_SUBMIT:
                if not isinstance(concrete_contract_id, str) or not concrete_contract_id.strip():
                    raise ValueError("real order submit requires a concrete contract")
                if concrete_contract_id not in self.allowed_contracts:
                    raise PermissionError("REAL_CONTRACT_NOT_AUTHORIZED")
            return
        self._require_current(
            at=at, broker_adapter_identity=broker_adapter_identity, account_identity=account_identity
        )

    def require_connect(
        self,
        *,
        at: datetime,
        broker_adapter_identity: str | None = None,
        account_identity: str | None = None,
    ) -> None:
        self.require_action(
            RealActionClass.CONNECT,
            at=at,
            broker_adapter_identity=broker_adapter_identity,
            account_identity=account_identity,
        )

    def require_order_submit(
        self,
        concrete_contract_id: str,
        *,
        at: datetime,
        broker_adapter_identity: str | None = None,
        account_identity: str | None = None,
    ) -> None:
        self.require_action(
            RealActionClass.ORDER_SUBMIT,
            at=at,
            concrete_contract_id=concrete_contract_id,
            broker_adapter_identity=broker_adapter_identity,
            account_identity=account_identity,
        )

    def require_order_cancel(
        self,
        *,
        at: datetime,
        broker_adapter_identity: str | None = None,
        account_identity: str | None = None,
    ) -> None:
        self.require_action(
            RealActionClass.ORDER_CANCEL,
            at=at,
            broker_adapter_identity=broker_adapter_identity,
            account_identity=account_identity,
        )

    def require_order_replace(
        self,
        *,
        at: datetime,
        broker_adapter_identity: str | None = None,
        account_identity: str | None = None,
    ) -> None:
        self.require_action(
            RealActionClass.ORDER_REPLACE,
            at=at,
            broker_adapter_identity=broker_adapter_identity,
            account_identity=account_identity,
        )

    def revoked(self) -> "RealExecutionAuthority":
        """Return the same identity with all permission cleared and status REVOKED."""
        return RealExecutionAuthority(
            authority_id=self.authority_id,
            broker_kind=self.broker_kind,
            account_kind=self.account_kind,
            status=RealAuthorityStatus.REVOKED,
            execution_mode=self.execution_mode,
            broker_adapter_identity=self.broker_adapter_identity,
            account_identity=self.account_identity,
            risk_policy_identity=self.risk_policy_identity,
            executable_identity=self.executable_identity,
            allowed_action_classes=(),
            allowed_contracts=self.allowed_contracts,
            credential_readiness=self.credential_readiness,
            valid_from=self.valid_from,
            expires_at=self.expires_at,
            max_position_lots=self.max_position_lots,
            test_only=self.test_only,
        )

    def disabled(self) -> "RealExecutionAuthority":
        """Return the same identity with all permission cleared and status DISABLED."""
        return RealExecutionAuthority(
            authority_id=self.authority_id,
            broker_kind=self.broker_kind,
            account_kind=self.account_kind,
            status=RealAuthorityStatus.DISABLED,
            execution_mode=self.execution_mode,
            broker_adapter_identity=self.broker_adapter_identity,
            account_identity=self.account_identity,
            risk_policy_identity=self.risk_policy_identity,
            executable_identity=self.executable_identity,
            allowed_action_classes=(),
            allowed_contracts=self.allowed_contracts,
            credential_readiness=self.credential_readiness,
            valid_from=self.valid_from,
            expires_at=self.expires_at,
            max_position_lots=self.max_position_lots,
            test_only=self.test_only,
        )


class RealAuthoritySource(Protocol):
    """Current machine-authority seam checked before every REAL mutation."""

    @property
    def source_identity(self) -> str: ...

    def current(self) -> RealExecutionAuthority: ...


class MutableRealAuthoritySource:
    """Small local authority source used by offline tests and local runtimes.

    Production composition may provide a file-backed or otherwise project-owned
    adapter with the same interface.  The runtime never retains permission from
    an earlier read: callers invoke ``current`` at each consequential action.
    """

    def __init__(self, authority: RealExecutionAuthority, *, source_identity: str) -> None:
        if not isinstance(authority, RealExecutionAuthority):
            raise TypeError("real authority source requires RealExecutionAuthority")
        if not isinstance(source_identity, str) or not source_identity.strip():
            raise ValueError("real authority source requires a stable identity")
        self._authority = authority
        self._source_identity = source_identity.strip()

    @property
    def source_identity(self) -> str:
        return self._source_identity

    def current(self) -> RealExecutionAuthority:
        return self._authority


__all__ = [
    "REAL_EXECUTION_AUTHORITY_SCHEMA_VERSION",
    "MutableRealAuthoritySource",
    "RealActionClass",
    "RealAuthoritySource",
    "RealAuthorityStatus",
    "RealCredentialReadiness",
    "RealExecutionAuthority",
]

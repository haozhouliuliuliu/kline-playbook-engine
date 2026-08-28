"""Machine-verifiable gates for future PAPER connectivity and order submission.

This module is ordinary offline engineering.  It does not itself authorize an
account login or an order.  A future exact Owner/machine authority must create
an ACTIVE value at the consequential boundary.

Secret values are never represented here.  Only credential environment-variable
names / location seams may be carried by an authority object.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json
from typing import Protocol


PAPER_EXECUTION_AUTHORITY_SCHEMA_VERSION = "KPE_PAPER_EXECUTION_AUTHORITY_V0_3"


class PaperAuthorityStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class PaperExecutionAuthority:
    """Exact machine gate for external PAPER actions.

    Connection, submit, cancel and replace are deliberately separate.  An
    action-capable authority always implies connection permission, but submit
    permission cannot silently authorize a distinct broker-account mutation.
    The authority is fail-closed unless it is ACTIVE.
    """

    authority_id: str
    broker_kind: str
    account_kind: str
    status: PaperAuthorityStatus
    allow_connect: bool
    allow_order_submit: bool
    broker_identity: str | None = None
    account_identity: str | None = None
    allow_order_cancel: bool = False
    allow_order_replace: bool = False
    credential_env_names: tuple[str, ...] = ()
    allowed_contracts: tuple[str, ...] = ()
    valid_from: datetime | None = None
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.authority_id.strip() or not self.broker_kind.strip() or not self.account_kind.strip():
            raise ValueError("paper authority requires non-empty identities")
        if not isinstance(self.status, PaperAuthorityStatus):
            raise ValueError("paper authority status must be explicit")
        if any(type(value) is not bool for value in (
            self.allow_connect, self.allow_order_submit, self.allow_order_cancel,
            self.allow_order_replace,
        )):
            raise ValueError("paper authority permissions must be booleans")
        if any((self.allow_order_submit, self.allow_order_cancel, self.allow_order_replace)) and not self.allow_connect:
            raise ValueError("paper order action permission requires connection permission")
        for value, name in (
            (self.broker_identity, "paper broker identity"),
            (self.account_identity, "paper account identity"),
        ):
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be non-empty when supplied")
        for name in self.credential_env_names:
            if not isinstance(name, str) or not name.strip() or name != name.strip():
                raise ValueError("credential environment names must be non-empty canonical strings")
            if "=" in name:
                raise ValueError("credential authority stores environment-variable names, never values")
        if len(self.credential_env_names) != len(set(self.credential_env_names)):
            raise ValueError("credential environment names must be unique")
        for contract in self.allowed_contracts:
            if not isinstance(contract, str) or not contract.strip() or contract != contract.strip():
                raise ValueError("allowed contracts must be non-empty canonical strings")
        if len(self.allowed_contracts) != len(set(self.allowed_contracts)):
            raise ValueError("allowed contracts must be unique")
        for value, name in ((self.valid_from, "valid_from"), (self.expires_at, "expires_at")):
            if value is not None and (not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None):
                raise ValueError(f"paper authority {name} must be timezone-aware")
        if self.valid_from is not None and self.expires_at is not None and self.expires_at <= self.valid_from:
            raise ValueError("paper authority expiry must follow its valid-from time")
        # Construction remains side-effect-free and can represent incomplete
        # draft authority.  Consequential gates below reject every missing
        # binding; preflight reports the same defects before connection.

    @property
    def identity_id(self) -> str:
        payload = {
            "schema_version": PAPER_EXECUTION_AUTHORITY_SCHEMA_VERSION,
            "authority_id": self.authority_id,
            "broker_kind": self.broker_kind,
            "account_kind": self.account_kind,
            "broker_identity": self.broker_identity,
            "account_identity": self.account_identity,
            "status": self.status.value,
            "allow_connect": self.allow_connect,
            "allow_order_submit": self.allow_order_submit,
            "allow_order_cancel": self.allow_order_cancel,
            "allow_order_replace": self.allow_order_replace,
            "credential_env_names": sorted(self.credential_env_names),
            "allowed_contracts": sorted(self.allowed_contracts),
            "valid_from": None if self.valid_from is None else self.valid_from.isoformat(),
            "expires_at": None if self.expires_at is None else self.expires_at.isoformat(),
        }
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        return sha256(encoded.encode("utf-8")).hexdigest()

    def _require_current(
        self,
        *,
        at: datetime | None = None,
        broker_identity: str | None = None,
        account_identity: str | None = None,
    ) -> None:
        if self.status is not PaperAuthorityStatus.ACTIVE:
            raise PermissionError("PAPER_AUTHORITY_NOT_ACTIVE")
        if at is not None and (
            not isinstance(at, datetime) or at.tzinfo is None or at.utcoffset() is None
        ):
            raise ValueError("paper authority check time must be timezone-aware")
        if at is not None and (
            self.valid_from is None
            or self.expires_at is None
            or not (self.valid_from <= at < self.expires_at)
        ):
            raise PermissionError("PAPER_AUTHORITY_NOT_CURRENT")
        if broker_identity is not None and (
            self.broker_identity is None or broker_identity != self.broker_identity
        ):
            raise PermissionError("PAPER_BROKER_IDENTITY_NOT_AUTHORIZED")
        if account_identity is not None and (
            self.account_identity is None or account_identity != self.account_identity
        ):
            raise PermissionError("PAPER_ACCOUNT_IDENTITY_NOT_AUTHORIZED")

    def require_connect(
        self,
        *,
        at: datetime | None = None,
        broker_identity: str | None = None,
        account_identity: str | None = None,
    ) -> None:
        if not self.allow_connect:
            raise PermissionError("PAPER_CONNECT_NOT_AUTHORIZED")
        self._require_current(
            at=at, broker_identity=broker_identity, account_identity=account_identity
        )

    def require_order_submit(
        self,
        concrete_contract_id: str,
        *,
        at: datetime | None = None,
        broker_identity: str | None = None,
        account_identity: str | None = None,
    ) -> None:
        if not self.allow_order_submit:
            raise PermissionError("PAPER_ORDER_SUBMIT_NOT_AUTHORIZED")
        self._require_current(
            at=at, broker_identity=broker_identity, account_identity=account_identity
        )
        if not isinstance(concrete_contract_id, str) or not concrete_contract_id.strip():
            raise ValueError("paper order submit requires a concrete contract")
        if concrete_contract_id not in self.allowed_contracts:
            raise PermissionError("PAPER_CONTRACT_NOT_AUTHORIZED")

    def require_order_cancel(
        self,
        *,
        at: datetime | None = None,
        broker_identity: str | None = None,
        account_identity: str | None = None,
    ) -> None:
        if not self.allow_order_cancel:
            raise PermissionError("PAPER_ORDER_CANCEL_NOT_AUTHORIZED")
        self._require_current(
            at=at, broker_identity=broker_identity, account_identity=account_identity
        )

    def require_order_replace(
        self,
        *,
        at: datetime | None = None,
        broker_identity: str | None = None,
        account_identity: str | None = None,
    ) -> None:
        if not self.allow_order_replace:
            raise PermissionError("PAPER_ORDER_REPLACE_NOT_AUTHORIZED")
        self._require_current(
            at=at, broker_identity=broker_identity, account_identity=account_identity
        )

    def revoked(self) -> "PaperExecutionAuthority":
        return PaperExecutionAuthority(
            authority_id=self.authority_id,
            broker_kind=self.broker_kind,
            account_kind=self.account_kind,
            broker_identity=self.broker_identity,
            account_identity=self.account_identity,
            status=PaperAuthorityStatus.REVOKED,
            allow_connect=False,
            allow_order_submit=False,
            allow_order_cancel=False,
            allow_order_replace=False,
            credential_env_names=self.credential_env_names,
            allowed_contracts=self.allowed_contracts,
            valid_from=self.valid_from,
            expires_at=self.expires_at,
        )


class PaperAuthoritySource(Protocol):
    """Current machine-authority seam checked before every external mutation."""

    @property
    def source_identity(self) -> str: ...

    def current(self) -> PaperExecutionAuthority: ...


class MutablePaperAuthoritySource:
    """Small local authority source used by offline tests and local runtimes.

    Production composition may provide a file-backed or otherwise project-owned
    adapter with the same interface.  The runtime never retains permission from
    an earlier read: callers invoke ``current`` at each consequential action.
    """

    def __init__(self, authority: PaperExecutionAuthority, *, source_identity: str) -> None:
        if not isinstance(authority, PaperExecutionAuthority):
            raise TypeError("paper authority source requires PaperExecutionAuthority")
        if not isinstance(source_identity, str) or not source_identity.strip():
            raise ValueError("paper authority source requires a stable identity")
        self._authority = authority
        self._source_identity = source_identity.strip()

    @property
    def source_identity(self) -> str:
        return self._source_identity

    def current(self) -> PaperExecutionAuthority:
        return self._authority

    def replace(self, authority: PaperExecutionAuthority) -> None:
        if not isinstance(authority, PaperExecutionAuthority):
            raise TypeError("paper authority replacement requires PaperExecutionAuthority")
        if authority.authority_id != self._authority.authority_id:
            raise ValueError("paper authority source cannot change authority id")
        self._authority = authority


__all__ = [
    "PAPER_EXECUTION_AUTHORITY_SCHEMA_VERSION",
    "MutablePaperAuthoritySource",
    "PaperAuthoritySource",
    "PaperAuthorityStatus",
    "PaperExecutionAuthority",
]

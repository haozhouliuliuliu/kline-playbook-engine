"""Machine-verifiable gates for future PAPER connectivity and order submission.

This module is ordinary offline engineering.  It does not itself authorize an
account login or an order.  A future exact Owner/machine authority must create
an ACTIVE value at the consequential boundary.

Secret values are never represented here.  Only credential environment-variable
names / location seams may be carried by an authority object.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json


PAPER_EXECUTION_AUTHORITY_SCHEMA_VERSION = "KPE_PAPER_EXECUTION_AUTHORITY_V0_1"


class PaperAuthorityStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class PaperExecutionAuthority:
    """Exact machine gate for external PAPER actions.

    ``allow_connect`` and ``allow_order_submit`` are deliberately separate.
    An order-capable authority always implies connection permission.  The
    authority is fail-closed unless it is ACTIVE.
    """

    authority_id: str
    broker_kind: str
    account_kind: str
    status: PaperAuthorityStatus
    allow_connect: bool
    allow_order_submit: bool
    credential_env_names: tuple[str, ...] = ()
    allowed_contracts: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.authority_id.strip() or not self.broker_kind.strip() or not self.account_kind.strip():
            raise ValueError("paper authority requires non-empty identities")
        if not isinstance(self.status, PaperAuthorityStatus):
            raise ValueError("paper authority status must be explicit")
        if type(self.allow_connect) is not bool or type(self.allow_order_submit) is not bool:
            raise ValueError("paper authority permissions must be booleans")
        if self.allow_order_submit and not self.allow_connect:
            raise ValueError("paper order permission requires connection permission")
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

    @property
    def identity_id(self) -> str:
        payload = {
            "schema_version": PAPER_EXECUTION_AUTHORITY_SCHEMA_VERSION,
            "authority_id": self.authority_id,
            "broker_kind": self.broker_kind,
            "account_kind": self.account_kind,
            "status": self.status.value,
            "allow_connect": self.allow_connect,
            "allow_order_submit": self.allow_order_submit,
            "credential_env_names": sorted(self.credential_env_names),
            "allowed_contracts": sorted(self.allowed_contracts),
        }
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        return sha256(encoded.encode("utf-8")).hexdigest()

    def require_connect(self) -> None:
        if self.status is not PaperAuthorityStatus.ACTIVE or not self.allow_connect:
            raise PermissionError("PAPER_CONNECT_NOT_AUTHORIZED")

    def require_order_submit(self, concrete_contract_id: str | None = None) -> None:
        if self.status is not PaperAuthorityStatus.ACTIVE or not self.allow_order_submit:
            raise PermissionError("PAPER_ORDER_SUBMIT_NOT_AUTHORIZED")
        if (
            concrete_contract_id
            and self.allowed_contracts
            and concrete_contract_id not in self.allowed_contracts
        ):
            raise PermissionError("PAPER_CONTRACT_NOT_AUTHORIZED")

    def revoked(self) -> "PaperExecutionAuthority":
        return PaperExecutionAuthority(
            authority_id=self.authority_id,
            broker_kind=self.broker_kind,
            account_kind=self.account_kind,
            status=PaperAuthorityStatus.REVOKED,
            allow_connect=False,
            allow_order_submit=False,
            credential_env_names=self.credential_env_names,
            allowed_contracts=self.allowed_contracts,
        )

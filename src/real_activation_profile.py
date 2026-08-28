"""Result-independent activation bindings for a future REAL execution session.

OFFLINE ONLY.  This module is ordinary offline engineering for the future REAL
execution path.  It performs no network, provider, credential, account-login,
order or broker action.

The profile cannot become ACTIVE while any required future binding is absent or
unresolved.  At minimum an ACTIVE REAL profile requires an explicit binding for
the execution authority, the broker adapter/runtime identity, the account
identity, the concrete-contract whitelist, the risk-policy identity and the
persistence/journal/runtime-layout identity.

Result-dependent execution policy categories (sizing, execution price, stop /
conditional order, close-today vs close-yesterday, rollover) are deliberately
NOT frozen here.  They remain UNBOUND/UNKNOWN (``None``) until a later
evidence/Owner-decision binding; explicit UNKNOWN is valid and preferable to a
fabricated default.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from hashlib import sha256
import json

REAL_ACTIVATION_PROFILE_SCHEMA_VERSION = "KPE_REAL_ACTIVATION_PROFILE_V0_1"

_EXECUTION_MODE = "REAL"

# Required activation bindings: absent/unresolved on an ACTIVE profile is an
# error and the profile must fail closed.
REQUIRED_ACTIVATION_BINDING_NAMES = (
    "execution_authority_identity",
    "broker_adapter_identity",
    "account_identity",
    "risk_policy_identity",
    "runtime_layout_identity",
    "allowed_contracts",
)

# Result-dependent policy categories deliberately NOT frozen.  ``None`` means
# UNBOUND / UNKNOWN and is reported by ``unbound_result_dependent_bindings``.
RESULT_DEPENDENT_POLICY_NAMES = (
    "sizing_policy_identity",
    "execution_price_policy_identity",
    "stop_order_policy_identity",
    "close_offset_policy_identity",
    "rollover_policy_identity",
)


class RealActivationStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _require_identity(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{name} must be a non-empty canonical string when supplied")
    return value.strip()


@dataclass(frozen=True)
class RealActivationProfile:
    """Separate REAL activation profile.

    An ACTIVE profile requires every required activation binding.  Result-
    dependent policy identities remain optional and default to UNBOUND/UNKNOWN;
    they are never invented here.
    """

    profile_id: str
    status: RealActivationStatus
    execution_mode: str = _EXECUTION_MODE
    execution_authority_identity: str | None = None
    broker_adapter_identity: str | None = None
    account_identity: str | None = None
    risk_policy_identity: str | None = None
    runtime_layout_identity: str | None = None
    allowed_contracts: tuple[str, ...] = ()
    # Result-dependent policy identities; ``None`` = UNBOUND / UNKNOWN.
    sizing_policy_identity: str | None = None
    execution_price_policy_identity: str | None = None
    stop_order_policy_identity: str | None = None
    close_offset_policy_identity: str | None = None
    rollover_policy_identity: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "profile_id", _require_identity(self.profile_id, "real activation profile id"))
        if not isinstance(self.status, RealActivationStatus):
            raise ValueError("real activation status must be explicit")
        if self.execution_mode != _EXECUTION_MODE:
            raise ValueError("real activation profile execution_mode must be REAL")
        if self.allowed_contracts is None:
            raise ValueError("real activation contracts must be a tuple")
        for contract in self.allowed_contracts:
            _require_identity(contract, "real activation contract")
        if len(self.allowed_contracts) != len(set(self.allowed_contracts)):
            raise ValueError("real activation contracts must be unique")
        for value, name in (
            (self.execution_authority_identity, "real execution-authority identity"),
            (self.broker_adapter_identity, "real broker-adapter identity"),
            (self.account_identity, "real account identity"),
            (self.risk_policy_identity, "real risk-policy identity"),
            (self.runtime_layout_identity, "real runtime-layout identity"),
            (self.sizing_policy_identity, "real sizing-policy identity"),
            (self.execution_price_policy_identity, "real execution-price policy identity"),
            (self.stop_order_policy_identity, "real stop-order policy identity"),
            (self.close_offset_policy_identity, "real close-offset policy identity"),
            (self.rollover_policy_identity, "real rollover policy identity"),
        ):
            if value is not None:
                _require_identity(value, name)
        if self.status is RealActivationStatus.ACTIVE:
            if any(getattr(self, name) is None for name in REQUIRED_ACTIVATION_BINDING_NAMES):
                raise ValueError("ACTIVE real activation requires every required activation binding")
            if not self.allowed_contracts:
                raise ValueError("ACTIVE real activation requires at least one contract")

    @property
    def identity_id(self) -> str:
        payload = {
            "schema_version": REAL_ACTIVATION_PROFILE_SCHEMA_VERSION,
            "profile_id": self.profile_id,
            "status": self.status.value,
            "execution_mode": self.execution_mode,
            "execution_authority_identity": self.execution_authority_identity,
            "broker_adapter_identity": self.broker_adapter_identity,
            "account_identity": self.account_identity,
            "risk_policy_identity": self.risk_policy_identity,
            "runtime_layout_identity": self.runtime_layout_identity,
            "allowed_contracts": sorted(self.allowed_contracts),
            "sizing_policy_identity": self.sizing_policy_identity,
            "execution_price_policy_identity": self.execution_price_policy_identity,
            "stop_order_policy_identity": self.stop_order_policy_identity,
            "close_offset_policy_identity": self.close_offset_policy_identity,
            "rollover_policy_identity": self.rollover_policy_identity,
        }
        return _hash(payload)

    def unbound_result_dependent_bindings(self) -> tuple[str, ...]:
        """Result-dependent policy names still UNBOUND/UNKNOWN on this profile."""
        return tuple(
            name
            for name in RESULT_DEPENDENT_POLICY_NAMES
            if getattr(self, name) is None
        )

    def require_active_for(self, concrete_contract_id: str) -> None:
        if self.status is not RealActivationStatus.ACTIVE:
            raise PermissionError("REAL_ACTIVATION_PROFILE_NOT_ACTIVE")
        if concrete_contract_id not in self.allowed_contracts:
            raise PermissionError("REAL_ACTIVATION_CONTRACT_NOT_ALLOWED")


__all__ = [
    "REAL_ACTIVATION_PROFILE_SCHEMA_VERSION",
    "REQUIRED_ACTIVATION_BINDING_NAMES",
    "RESULT_DEPENDENT_POLICY_NAMES",
    "RealActivationProfile",
    "RealActivationStatus",
]

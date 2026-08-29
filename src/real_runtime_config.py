"""Project-owned local REAL runtime configuration / binding surface.

OFFLINE ONLY.  This module holds the stable, non-secret identities and paths
required to *represent* a future REAL runtime, plus explicit, later-bindable
references to the approved REAL activation profile and REAL execution
authority.  It performs zero network, provider, credential, account-login,
order or broker action.

Result-dependent or not-yet-adopted values are represented as UNBOUND/UNKNOWN,
never as guessed defaults.  In particular this module does NOT invent Fangzheng
credential variable names, a final broker endpoint, a final concrete contract,
permanent risk percentages/amounts, an execution-price policy, a
stop/conditional-order policy, a close-today/close-yesterday policy or a
rollover policy.  Those may only be bound later through an explicitly bound
``RealActivationProfile`` / ``RealExecutionAuthority`` and are reported by
``unbound_result_dependent_bindings()`` until then.

Secret values are never represented in this surface.  Credential readiness is
carried only as an abstract SET/UNSET-style input on the authority object.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from src.real_activation_profile import (
    REAL_ACTIVATION_PROFILE_SCHEMA_VERSION,
    RealActivationProfile,
    RealActivationStatus,
)
from src.real_execution_authority import (
    REAL_EXECUTION_AUTHORITY_SCHEMA_VERSION,
    RealActionClass,
    RealAuthorityStatus,
    RealExecutionAuthority,
)

REAL_RUNTIME_CONFIG_SCHEMA_VERSION = "KPE_REAL_RUNTIME_CONFIG_V0_1"

_EXECUTION_MODE = "REAL"

# Result-dependent execution policy categories that are deliberately NOT frozen
# here and NOT invented by this module.  They may only be bound through an
# explicit activation profile later; ``None`` means UNBOUND/UNKNOWN.
RESULT_DEPENDENT_BINDING_NAMES = (
    "sizing_policy_identity",
    "execution_price_policy_identity",
    "stop_order_policy_identity",
    "close_offset_policy_identity",
    "rollover_policy_identity",
)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip() or value != value.strip():
        raise ValueError(f"{name} must be non-empty canonical text")
    return value.strip()


def _resolve_state_root(value: object) -> Path:
    if isinstance(value, Path):
        path = value
    elif isinstance(value, str) and value.strip():
        path = Path(value)
    else:
        raise ValueError("real runtime state root must be a non-empty path")
    return path.expanduser()


@dataclass(frozen=True)
class RealRuntimeConfig:
    """Stable, non-secret local REAL startup binding surface.

    Result-dependent execution values are intentionally absent (UNBOUND/UNKNOWN).
    They are bound later through ``activation_profile`` (an explicit
    ``RealActivationProfile`` object) and enforced by the REAL preflight /
    authority gates.  Missing required result-dependent bindings remain explicit
    blockers and are reported by ``unbound_result_dependent_bindings()``.
    """

    config_id: str
    state_root: str | Path
    trader_identity: str
    concrete_contract_id: str
    product: str
    exchange: str
    broker_kind: str
    account_kind: str
    execution_mode: str = _EXECUTION_MODE
    account_identity: str | None = None
    runtime_layout_identity: str | None = None

    activation_profile: RealActivationProfile | None = None
    authority: RealExecutionAuthority | None = None

    timezone: str = "Asia/Shanghai"

    def __post_init__(self) -> None:
        object.__setattr__(self, "config_id", _text(self.config_id, "real runtime config id"))
        object.__setattr__(self, "trader_identity", _text(self.trader_identity, "real trader identity"))
        object.__setattr__(
            self, "concrete_contract_id", _text(self.concrete_contract_id, "real concrete contract")
        )
        object.__setattr__(self, "product", _text(self.product, "real product"))
        object.__setattr__(self, "exchange", _text(self.exchange, "real exchange"))
        object.__setattr__(self, "broker_kind", _text(self.broker_kind, "real broker kind"))
        object.__setattr__(self, "account_kind", _text(self.account_kind, "real account kind"))
        object.__setattr__(self, "state_root", _resolve_state_root(self.state_root))
        if self.execution_mode != _EXECUTION_MODE:
            raise ValueError("real runtime config execution_mode must be REAL")
        if self.timezone != "Asia/Shanghai":
            raise ValueError("real runtime config timezone must be Asia/Shanghai")
        if self.account_identity is not None and (
            not isinstance(self.account_identity, str) or not self.account_identity.strip()
        ):
            raise ValueError("real runtime account identity must be non-empty when supplied")
        if self.runtime_layout_identity is not None and (
            not isinstance(self.runtime_layout_identity, str) or not self.runtime_layout_identity.strip()
        ):
            raise ValueError("real runtime layout identity must be non-empty when supplied")
        if self.activation_profile is not None and not isinstance(
            self.activation_profile, RealActivationProfile
        ):
            raise ValueError("real runtime config activation profile must be RealActivationProfile")
        if self.authority is not None and not isinstance(self.authority, RealExecutionAuthority):
            raise ValueError("real runtime config authority must be RealExecutionAuthority")
        # The concrete contract must agree with the declared exchange/product
        # identity (fail closed on an inconsistent contract binding).
        if "." not in self.concrete_contract_id:
            raise ValueError("real concrete contract must include an exchange prefix (EXCHANGE.instrument)")
        contract_exchange, instrument = self.concrete_contract_id.split(".", 1)
        if not instrument:
            raise ValueError("real concrete contract instrument must be non-empty")
        if contract_exchange != self.exchange:
            raise ValueError("real concrete contract exchange disagrees with config exchange")
        if not instrument.startswith(self.product):
            raise ValueError("real concrete contract instrument disagrees with config product")

    # ------------------------------------------------------------------ binding

    @property
    def resolved_state_root(self) -> Path:
        return self.state_root

    def bind_activation_profile(self, profile: RealActivationProfile) -> "RealRuntimeConfig":
        """Return an updated config with an explicitly bound activation profile.

        Result-dependent execution values are bound only through this profile;
        they are never invented by this module.
        """
        if not isinstance(profile, RealActivationProfile):
            raise ValueError("real activation profile must be RealActivationProfile")
        return RealRuntimeConfig(
            config_id=self.config_id,
            state_root=self.state_root,
            trader_identity=self.trader_identity,
            concrete_contract_id=self.concrete_contract_id,
            product=self.product,
            exchange=self.exchange,
            broker_kind=self.broker_kind,
            account_kind=self.account_kind,
            execution_mode=self.execution_mode,
            account_identity=self.account_identity,
            runtime_layout_identity=self.runtime_layout_identity,
            activation_profile=profile,
            authority=self.authority,
            timezone=self.timezone,
        )

    def bind_authority(self, authority: RealExecutionAuthority) -> "RealRuntimeConfig":
        """Return an updated config with an explicitly bound execution authority."""
        if not isinstance(authority, RealExecutionAuthority):
            raise ValueError("real execution authority must be RealExecutionAuthority")
        return RealRuntimeConfig(
            config_id=self.config_id,
            state_root=self.state_root,
            trader_identity=self.trader_identity,
            concrete_contract_id=self.concrete_contract_id,
            product=self.product,
            exchange=self.exchange,
            broker_kind=self.broker_kind,
            account_kind=self.account_kind,
            execution_mode=self.execution_mode,
            account_identity=self.account_identity,
            runtime_layout_identity=self.runtime_layout_identity,
            activation_profile=self.activation_profile,
            authority=authority,
            timezone=self.timezone,
        )

    # ------------------------------------------------------------- completeness

    def unbound_result_dependent_bindings(self) -> tuple[str, ...]:
        """Result-dependent binding names that are still missing / not bound.

        A config with no bound activation profile is treated as fully unbound
        for the result-dependent execution surface.  An ACTIVE profile reports
        only the result-dependent policy identities it still leaves UNBOUND.
        """
        if self.activation_profile is None:
            return RESULT_DEPENDENT_BINDING_NAMES
        return self.activation_profile.unbound_result_dependent_bindings()

    def external_activation_blockers(self) -> tuple[str, ...]:
        """Explicit blockers that prevent a real external REAL activation.

        This is the fail-closed surface for the current canonical state: until
        an ACTIVE REAL activation profile and an ACTIVE REAL connect authority
        are bound, real external activation remains BLOCKED.  Synthetic/offline
        fixtures may bind both to pass the structural preflight without any
        real account/order action.
        """
        blockers: list[str] = []
        if self.activation_profile is None:
            blockers.append("REAL_ACTIVATION_PROFILE_UNBOUND")
        elif self.activation_profile.status is not RealActivationStatus.ACTIVE:
            blockers.append("REAL_ACTIVATION_PROFILE_NOT_ACTIVE")
        else:
            missing = self.unbound_result_dependent_bindings()
            if missing:
                blockers.append("REAL_RESULT_DEPENDENT_BINDINGS_UNBOUND:" + ",".join(sorted(missing)))
        if self.authority is None:
            blockers.append("REAL_CONNECT_AUTHORITY_UNBOUND")
        elif self.authority.status is not RealAuthorityStatus.ACTIVE:
            blockers.append("REAL_CONNECT_AUTHORITY_NOT_ACTIVE")
        elif RealActionClass.CONNECT not in self.authority.allowed_action_classes:
            blockers.append("REAL_CONNECT_AUTHORITY_DENIED")
        return tuple(sorted(set(blockers)))

    # ---------------------------------------------------------------- identity

    @property
    def identity(self) -> str:
        return _hash(
            {
                "schema_version": REAL_RUNTIME_CONFIG_SCHEMA_VERSION,
                "config_id": self.config_id,
                "state_root": str(self.state_root),
                "trader_identity": self.trader_identity,
                "concrete_contract_id": self.concrete_contract_id,
                "product": self.product,
                "exchange": self.exchange,
                "broker_kind": self.broker_kind,
                "account_kind": self.account_kind,
                "execution_mode": self.execution_mode,
                "account_identity": self.account_identity,
                "runtime_layout_identity": self.runtime_layout_identity,
                "timezone": self.timezone,
                "activation_profile": (
                    None
                    if self.activation_profile is None
                    else {
                        "schema_version": REAL_ACTIVATION_PROFILE_SCHEMA_VERSION,
                        "profile_id": self.activation_profile.profile_id,
                        "status": self.activation_profile.status.value,
                        "identity": self.activation_profile.identity_id,
                    }
                ),
                "authority": (
                    None
                    if self.authority is None
                    else {
                        "schema_version": REAL_EXECUTION_AUTHORITY_SCHEMA_VERSION,
                        "authority_id": self.authority.authority_id,
                        "status": self.authority.status.value,
                        "identity": self.authority.identity_id,
                    }
                ),
            }
        )

    @property
    def stable_identity(self) -> str:
        """Identity over the stable, non-volatile config surface only.

        The layout/state-root binding must be deterministic regardless of
        whether an activation profile/authority is currently bound (those are
        volatile runtime gates, not part of the durable state-root identity).
        """
        return _hash(
            {
                "schema_version": REAL_RUNTIME_CONFIG_SCHEMA_VERSION,
                "identity_kind": "STABLE_LAYOUT_BINDING",
                "config_id": self.config_id,
                "state_root": str(self.state_root),
                "trader_identity": self.trader_identity,
                "concrete_contract_id": self.concrete_contract_id,
                "product": self.product,
                "exchange": self.exchange,
                "broker_kind": self.broker_kind,
                "account_kind": self.account_kind,
                "execution_mode": self.execution_mode,
                "account_identity": self.account_identity,
                "runtime_layout_identity": self.runtime_layout_identity,
                "timezone": self.timezone,
            }
        )


__all__ = [
    "REAL_RUNTIME_CONFIG_SCHEMA_VERSION",
    "RESULT_DEPENDENT_BINDING_NAMES",
    "RealRuntimeConfig",
]

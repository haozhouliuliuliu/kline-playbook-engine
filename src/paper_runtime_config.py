"""Project-owned local PAPER runtime configuration / binding surface.

OFFLINE ONLY. This module holds the stable, non-secret identities and paths
required to *start* a future PAPER runtime, plus explicit, later-bindable
references to the approved activation profile and execution authority. It
invents no strategy-result-dependent execution semantics (quantity/sizing,
execution price policy, SHFE/INE close-today vs close-yesterday, permanent
numeric risk limits, final PAPER contract whitelist): those live only inside an
explicitly bound ``PaperActivationProfile`` and are never frozen here.

Importing or constructing this module performs zero network, provider,
credential, account-login, order or broker action. Secret values are never
represented in this surface (only credential environment-variable *names* may be
carried by an authority object, never values).
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path

from src.paper_activation_profile import (
    PAPER_ACTIVATION_PROFILE_SCHEMA_VERSION,
    PaperActivationProfile,
    PaperActivationStatus,
)
from src.paper_execution_authority import (
    PAPER_EXECUTION_AUTHORITY_SCHEMA_VERSION,
    PaperExecutionAuthority,
    PaperAuthorityStatus,
)
from src.paper_runtime_bindings import PaperToolRoleBinding

PAPER_RUNTIME_CONFIG_SCHEMA_VERSION = "KPE_PAPER_RUNTIME_CONFIG_V0_1"

# Result-dependent execution semantics that are deliberately NOT frozen here.
# They may only be bound through an explicit activation profile later.
RESULT_DEPENDENT_BINDING_NAMES = (
    "sizing_policy_identity",
    "execution_price_policy_identity",
    "close_offset_policy_identity",
    "risk_policy_identity",
    "allowed_contracts",
)


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _text(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be non-empty text")
    return value.strip()


def _resolve_state_root(value: object) -> Path:
    if isinstance(value, Path):
        path = value
    elif isinstance(value, str) and value.strip():
        path = Path(value)
    else:
        raise ValueError("paper runtime state root must be a non-empty path")
    return path.expanduser()


@dataclass(frozen=True)
class PaperRuntimeConfig:
    """Stable, non-secret local PAPER startup binding surface.

    Result-dependent execution values are intentionally absent. They are bound
    later through ``activation_profile`` (an explicit ``PaperActivationProfile``
    object) and enforced by the PAPER preflight/authority gates. Missing
    required result-dependent bindings remain explicit blockers: an ACTIVE
    activation profile requires every policy binding, and ``unbound_result_dependent_bindings()``
    reports what is still missing.
    """

    config_id: str
    state_root: str | Path
    trader_identity: str
    concrete_contract_id: str
    product: str
    exchange: str
    tqsdk_runtime_version: str
    broker_kind: str
    account_kind: str
    account_identity: str | None = None

    activation_profile: PaperActivationProfile | None = None
    authority: PaperExecutionAuthority | None = None
    paper_tool_role: PaperToolRoleBinding | None = None

    timezone: str = "Asia/Shanghai"
    symbol: str | None = None
    source_poll_limit: int = 512
    max_source_age_seconds: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "config_id", _text(self.config_id, "paper runtime config id"))
        object.__setattr__(self, "trader_identity", _text(self.trader_identity, "paper trader identity"))
        object.__setattr__(
            self, "concrete_contract_id", _text(self.concrete_contract_id, "paper concrete contract")
        )
        object.__setattr__(self, "product", _text(self.product, "paper product"))
        object.__setattr__(self, "exchange", _text(self.exchange, "paper exchange"))
        object.__setattr__(
            self, "tqsdk_runtime_version", _text(self.tqsdk_runtime_version, "paper runtime version")
        )
        object.__setattr__(self, "broker_kind", _text(self.broker_kind, "paper broker kind"))
        object.__setattr__(self, "account_kind", _text(self.account_kind, "paper account kind"))
        object.__setattr__(self, "state_root", _resolve_state_root(self.state_root))
        if self.timezone != "Asia/Shanghai":
            raise ValueError("paper runtime config timezone must be Asia/Shanghai")
        if type(self.source_poll_limit) is not int or self.source_poll_limit <= 0:
            raise ValueError("paper runtime config source poll limit must be a positive integer")
        if self.max_source_age_seconds is not None and (
            type(self.max_source_age_seconds) is not int or self.max_source_age_seconds <= 0
        ):
            raise ValueError("paper runtime config max source age must be a positive integer")
        if self.symbol is not None and (not isinstance(self.symbol, str) or not self.symbol.strip()):
            raise ValueError("paper runtime config symbol must be non-empty when supplied")
        if self.account_identity is not None and (
            not isinstance(self.account_identity, str) or not self.account_identity.strip()
        ):
            raise ValueError("paper runtime account identity must be non-empty when supplied")
        if self.activation_profile is not None and not isinstance(
            self.activation_profile, PaperActivationProfile
        ):
            raise ValueError("paper runtime config activation profile must be PaperActivationProfile")
        if self.authority is not None and not isinstance(self.authority, PaperExecutionAuthority):
            raise ValueError("paper runtime config authority must be PaperExecutionAuthority")
        if self.paper_tool_role is not None and not isinstance(
            self.paper_tool_role, PaperToolRoleBinding
        ):
            raise ValueError("paper runtime tool role must be PaperToolRoleBinding")
        # The concrete contract must agree with the declared exchange/product
        # identity (fail closed on an inconsistent contract binding).
        if "." not in self.concrete_contract_id:
            raise ValueError("paper concrete contract must include an exchange prefix (EXCHANGE.instrument)")
        contract_exchange, instrument = self.concrete_contract_id.split(".", 1)
        if not instrument:
            raise ValueError("paper concrete contract instrument must be non-empty")
        if contract_exchange != self.exchange:
            raise ValueError("paper concrete contract exchange disagrees with config exchange")
        if not instrument.startswith(self.product):
            raise ValueError("paper concrete contract instrument disagrees with config product")

    # ------------------------------------------------------------------ binding

    @property
    def resolved_state_root(self) -> Path:
        return self.state_root

    def bind_activation_profile(self, profile: PaperActivationProfile) -> "PaperRuntimeConfig":
        """Return an updated config with an explicitly bound activation profile.

        Result-dependent execution values are bound only through this profile;
        they are never invented by this module.
        """
        if not isinstance(profile, PaperActivationProfile):
            raise ValueError("paper activation profile must be PaperActivationProfile")
        return PaperRuntimeConfig(
            config_id=self.config_id,
            state_root=self.state_root,
            trader_identity=self.trader_identity,
            concrete_contract_id=self.concrete_contract_id,
            product=self.product,
            exchange=self.exchange,
            tqsdk_runtime_version=self.tqsdk_runtime_version,
            broker_kind=self.broker_kind,
            account_kind=self.account_kind,
            account_identity=self.account_identity,
            activation_profile=profile,
            authority=self.authority,
            paper_tool_role=self.paper_tool_role,
            timezone=self.timezone,
            symbol=self.symbol,
            source_poll_limit=self.source_poll_limit,
            max_source_age_seconds=self.max_source_age_seconds,
        )

    def bind_authority(self, authority: PaperExecutionAuthority) -> "PaperRuntimeConfig":
        """Return an updated config with an explicitly bound execution authority."""
        if not isinstance(authority, PaperExecutionAuthority):
            raise ValueError("paper execution authority must be PaperExecutionAuthority")
        return PaperRuntimeConfig(
            config_id=self.config_id,
            state_root=self.state_root,
            trader_identity=self.trader_identity,
            concrete_contract_id=self.concrete_contract_id,
            product=self.product,
            exchange=self.exchange,
            tqsdk_runtime_version=self.tqsdk_runtime_version,
            broker_kind=self.broker_kind,
            account_kind=self.account_kind,
            account_identity=self.account_identity,
            activation_profile=self.activation_profile,
            authority=authority,
            paper_tool_role=self.paper_tool_role,
            timezone=self.timezone,
            symbol=self.symbol,
            source_poll_limit=self.source_poll_limit,
            max_source_age_seconds=self.max_source_age_seconds,
        )

    # ------------------------------------------------------------- completeness

    def unbound_result_dependent_bindings(self) -> tuple[str, ...]:
        """Result-dependent binding names that are still missing / not bound.

        A config with no bound activation profile is treated as fully unbound
        for the result-dependent execution surface. An ACTIVE profile by
        definition binds all policy identities and the contract whitelist, so
        nothing further is missing there.
        """
        if self.activation_profile is None:
            return RESULT_DEPENDENT_BINDING_NAMES
        if self.activation_profile.status is not PaperActivationStatus.ACTIVE:
            return RESULT_DEPENDENT_BINDING_NAMES
        return ()

    def external_activation_blockers(self) -> tuple[str, ...]:
        """Explicit blockers that prevent a real external PAPER activation.

        This is the fail-closed surface for the current canonical state: until
        an ACTIVE activation profile and an ACTIVE connect authority are bound,
        real external activation remains BLOCKED. Offline-rehearsal fakes may
        bind both to pass preflight without any real account/order action.
        """
        blockers: list[str] = []
        if self.activation_profile is None:
            blockers.append("ACTIVATION_PROFILE_UNBOUND")
        elif self.activation_profile.status is not PaperActivationStatus.ACTIVE:
            blockers.append("ACTIVATION_PROFILE_NOT_ACTIVE")
        else:
            missing = self.unbound_result_dependent_bindings()
            if missing:
                blockers.append("RESULT_DEPENDENT_BINDINGS_MISSING:" + ",".join(sorted(missing)))
        if self.authority is None:
            blockers.append("PAPER_CONNECT_AUTHORITY_UNBOUND")
        elif self.authority.status is not PaperAuthorityStatus.ACTIVE:
            blockers.append("PAPER_CONNECT_AUTHORITY_NOT_ACTIVE")
        elif not self.authority.allow_connect:
            blockers.append("PAPER_CONNECT_AUTHORITY_DENIED")
        return tuple(sorted(set(blockers)))

    # ---------------------------------------------------------------- identity

    @property
    def identity(self) -> str:
        return _hash(
            {
                "schema_version": PAPER_RUNTIME_CONFIG_SCHEMA_VERSION,
                "config_id": self.config_id,
                "state_root": str(self.state_root),
                "trader_identity": self.trader_identity,
                "concrete_contract_id": self.concrete_contract_id,
                "product": self.product,
                "exchange": self.exchange,
                "tqsdk_runtime_version": self.tqsdk_runtime_version,
                "broker_kind": self.broker_kind,
                "account_kind": self.account_kind,
                "account_identity": self.account_identity,
                "timezone": self.timezone,
                "symbol": self.symbol,
                "source_poll_limit": self.source_poll_limit,
                "max_source_age_seconds": self.max_source_age_seconds,
                "activation_profile": (
                    None
                    if self.activation_profile is None
                    else {
                        "schema_version": PAPER_ACTIVATION_PROFILE_SCHEMA_VERSION,
                        "profile_id": self.activation_profile.profile_id,
                        "status": self.activation_profile.status.value,
                        "identity": self.activation_profile.identity_id,
                    }
                ),
                "authority": (
                    None
                    if self.authority is None
                    else {
                        "schema_version": PAPER_EXECUTION_AUTHORITY_SCHEMA_VERSION,
                        "authority_id": self.authority.authority_id,
                        "status": self.authority.status.value,
                        "identity": self.authority.identity_id,
                    }
                ),
                "paper_tool_role": (
                    None if self.paper_tool_role is None else self.paper_tool_role.identity_id
                ),
            }
        )

    @property
    def stable_identity(self) -> str:
        """Identity over the stable, non-volatile config surface only.

        The layout/state-root binding must be deterministic regardless of
        whether an activation profile/authority is currently bound (those are
        volatile runtime gates, not part of the durable state-root identity).
        This lets a state root be opened by an unbound preflight and later by
        the same runtime with an explicitly bound profile/authority.
        """
        return _hash(
            {
                "schema_version": PAPER_RUNTIME_CONFIG_SCHEMA_VERSION,
                "identity_kind": "STABLE_LAYOUT_BINDING",
                "config_id": self.config_id,
                "state_root": str(self.state_root),
                "trader_identity": self.trader_identity,
                "concrete_contract_id": self.concrete_contract_id,
                "product": self.product,
                "exchange": self.exchange,
                "tqsdk_runtime_version": self.tqsdk_runtime_version,
                "broker_kind": self.broker_kind,
                "account_kind": self.account_kind,
                "account_identity": self.account_identity,
                "timezone": self.timezone,
                "symbol": self.symbol,
                "source_poll_limit": self.source_poll_limit,
                "max_source_age_seconds": self.max_source_age_seconds,
                "paper_tool_role": (
                    None if self.paper_tool_role is None else self.paper_tool_role.identity_id
                ),
            }
        )

    def to_public_document(self) -> dict[str, object]:
        """Non-secret serializable summary for preflight/CLI output.

        Never contains secret values: only identities, statuses and paths.
        """
        return {
            "schema_version": PAPER_RUNTIME_CONFIG_SCHEMA_VERSION,
            "config_id": self.config_id,
            "state_root": str(self.state_root),
            "trader_identity": self.trader_identity,
            "concrete_contract_id": self.concrete_contract_id,
            "product": self.product,
            "exchange": self.exchange,
            "tqsdk_runtime_version": self.tqsdk_runtime_version,
            "broker_kind": self.broker_kind,
            "account_kind": self.account_kind,
            "account_identity": self.account_identity,
            "timezone": self.timezone,
            "symbol": self.symbol,
            "source_poll_limit": self.source_poll_limit,
            "max_source_age_seconds": self.max_source_age_seconds,
            "activation_profile_bound": self.activation_profile is not None,
            "activation_profile_status": (
                None
                if self.activation_profile is None
                else self.activation_profile.status.value
            ),
            "authority_bound": self.authority is not None,
            "authority_status": None if self.authority is None else self.authority.status.value,
            "paper_tool_role_status": (
                None if self.paper_tool_role is None else self.paper_tool_role.status.value
            ),
            "unbound_result_dependent_bindings": sorted(self.unbound_result_dependent_bindings()),
            "external_activation_blockers": list(self.external_activation_blockers()),
            "config_identity": self.identity,
        }


__all__ = [
    "PAPER_RUNTIME_CONFIG_SCHEMA_VERSION",
    "RESULT_DEPENDENT_BINDING_NAMES",
    "PaperRuntimeConfig",
]

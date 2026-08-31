"""Project-owned REAL activation preflight (offline, fail-closed).

OFFLINE ONLY.  This module computes a machine-clear READY / BLOCKED fact set
for a future REAL execution activation.  It performs NO login, NO credential
read, NO provider call, NO network action, NO order/broker mutation and NO
account mutation.  It cannot connect to, or activate against, any broker.

The current canonical project state has NO REAL authority and NO REAL broker
transport, so a real ``EXTERNAL`` preflight correctly reports BLOCKED.  A
``STRUCTURAL`` mode may bind a fully populated TEST_ONLY synthetic fixture
(never real account/order action) and pass preflight to prove the structural
activation surface.  A synthetic authority is always blocked in ``EXTERNAL``
mode so that "tests passed" can never equal "REAL authorized".
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json

from src.real_activation_profile import (
    REQUIRED_ACTIVATION_BINDING_NAMES,
    RealActivationProfile,
    RealActivationStatus,
)
from src.real_execution_authority import (
    RealAuthorityStatus,
    RealCredentialReadiness,
    RealExecutionAuthority,
)
from src.real_runtime_config import RealRuntimeConfig

REAL_PREFLIGHT_SCHEMA_VERSION = "KPE_REAL_PREFLIGHT_V0_1"

EXTERNAL = "EXTERNAL"
STRUCTURAL = "STRUCTURAL"
_MODES = frozenset({EXTERNAL, STRUCTURAL})

PASS = "PASS"
BLOCK = "BLOCK"


class RealDurableState(str, Enum):
    """Durable order/wake/reconciliation state supplied by the caller.

    This is an abstract state marker, never a broker action or a secret.  A
    real activation request must supply CLEAR for every durable state surface;
    NOT_SUPPLIED / UNRESOLVED / UNKNOWN fail closed.
    """

    NOT_SUPPLIED = "NOT_SUPPLIED"
    CLEAR = "CLEAR"
    UNRESOLVED = "UNRESOLVED"
    UNKNOWN = "UNKNOWN"


def _canonical_json(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _hash(value: object) -> str:
    return sha256(_canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class RealPreflightCheck:
    name: str
    status: str  # PASS | BLOCK
    detail: str

    def __post_init__(self) -> None:
        if self.status not in {PASS, BLOCK}:
            raise ValueError("real preflight check status must be PASS or BLOCK")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("real preflight check name must be non-empty")
        if not isinstance(self.detail, str):
            raise ValueError("real preflight check detail must be text")


@dataclass(frozen=True)
class RealPreflightReport:
    mode: str
    overall: str  # READY | BLOCKED
    checks: tuple[RealPreflightCheck, ...]

    def __post_init__(self) -> None:
        if self.mode not in _MODES:
            raise ValueError("real preflight mode must be EXTERNAL or STRUCTURAL")
        if self.overall not in {"READY", "BLOCKED"}:
            raise ValueError("real preflight overall must be READY or BLOCKED")
        if self.overall == "READY" and any(check.status == BLOCK for check in self.checks):
            raise ValueError("READY real preflight cannot contain a BLOCK check")
        if self.overall == "BLOCKED" and all(check.status == PASS for check in self.checks):
            raise ValueError("BLOCKED real preflight requires at least one BLOCK check")

    @property
    def ready(self) -> bool:
        return self.overall == "READY"

    @property
    def blocked(self) -> bool:
        return self.overall == "BLOCKED"

    @property
    def blocked_checks(self) -> tuple[RealPreflightCheck, ...]:
        return tuple(check for check in self.checks if check.status == BLOCK)

    @property
    def identity(self) -> str:
        return _hash(
            {
                "schema_version": REAL_PREFLIGHT_SCHEMA_VERSION,
                "mode": self.mode,
                "overall": self.overall,
                "checks": [
                    {"name": check.name, "status": check.status, "detail": check.detail}
                    for check in self.checks
                ],
            }
        )

    def public_lines(self) -> tuple[str, ...]:
        """Machine-clear lines for CLI/console output. No secret values."""
        return (
            f"REAL_PREFLIGHT_SCHEMA={REAL_PREFLIGHT_SCHEMA_VERSION}",
            f"REAL_PREFLIGHT_MODE={self.mode}",
            f"REAL_PREFLIGHT_OVERALL={self.overall}",
            *(
                f"REAL_PREFLIGHT_CHECK_{check.name}={check.status}:{check.detail}"
                for check in self.checks
            ),
            f"REAL_PREFLIGHT_IDENTITY={self.identity}",
        )


def _check(name: str, blockers: list[str], detail: str) -> RealPreflightCheck:
    if blockers:
        return RealPreflightCheck(name=name, status=BLOCK, detail=";".join(sorted(set(blockers))))
    return RealPreflightCheck(name=name, status=PASS, detail=detail)


def _state_blockers(state: RealDurableState | None, name: str) -> list[str]:
    if state is None or state is RealDurableState.NOT_SUPPLIED:
        return [name + "_NOT_SUPPLIED"]
    if state is RealDurableState.UNRESOLVED:
        return [name + "_UNRESOLVED"]
    if state is RealDurableState.UNKNOWN:
        return [name + "_UNKNOWN"]
    if state is not RealDurableState.CLEAR:
        return [name + "_NOT_CLEAR"]
    return []


def run_real_preflight(
    *,
    config: RealRuntimeConfig,
    activation_profile: RealActivationProfile | None = None,
    authority: RealExecutionAuthority | None = None,
    mode: str = EXTERNAL,
    assessed_at: datetime | None = None,
    order_state: RealDurableState | None = None,
    wake_state: RealDurableState | None = None,
    account_state: RealDurableState | None = None,
    reconciliation_state: RealDurableState | None = None,
) -> RealPreflightReport:
    """Compute a machine-clear READY/BLOCKED fact set for REAL activation.

    Performs no login/connect/order/provider/credential/account action.  This
    is a pure offline structural check over the supplied bindings.
    """
    if not isinstance(config, RealRuntimeConfig):
        raise TypeError("real preflight requires RealRuntimeConfig")
    if mode not in _MODES:
        raise ValueError("real preflight mode must be EXTERNAL or STRUCTURAL")
    if activation_profile is None:
        activation_profile = config.activation_profile
    if authority is None:
        authority = config.authority
    if activation_profile is not None and not isinstance(activation_profile, RealActivationProfile):
        raise TypeError("real preflight activation profile must be RealActivationProfile")
    if authority is not None and not isinstance(authority, RealExecutionAuthority):
        raise TypeError("real preflight authority must be RealExecutionAuthority")
    if assessed_at is not None and (
        not isinstance(assessed_at, datetime)
        or assessed_at.tzinfo is None
        or assessed_at.utcoffset() is None
    ):
        raise ValueError("real preflight assessment time must be timezone-aware")
    for value, name in (
        (order_state, "order"),
        (wake_state, "wake"),
        (account_state, "account"),
        (reconciliation_state, "reconciliation"),
    ):
        if value is not None and not isinstance(value, RealDurableState):
            raise TypeError(f"real preflight {name} state must be RealDurableState")

    checks: list[RealPreflightCheck] = []

    # 1. configuration completeness ------------------------------------------
    config_blockers: list[str] = []
    for name in (
        "config_id",
        "trader_identity",
        "concrete_contract_id",
        "product",
        "exchange",
        "broker_kind",
        "account_kind",
    ):
        if not getattr(config, name):
            config_blockers.append(name.upper() + "_MISSING")
    checks.append(_check("CONFIGURATION_COMPLETE", config_blockers,
                         "all required stable identities are present"))

    # 2. execution mode is REAL and unambiguous -------------------------------
    mode_blockers: list[str] = []
    if config.execution_mode != "REAL":
        mode_blockers.append("CONFIG_EXECUTION_MODE_NOT_REAL")
    if activation_profile is not None and activation_profile.execution_mode != "REAL":
        mode_blockers.append("PROFILE_EXECUTION_MODE_NOT_REAL")
    if authority is not None and authority.execution_mode != "REAL":
        mode_blockers.append("AUTHORITY_EXECUTION_MODE_NOT_REAL")
    checks.append(_check("EXECUTION_MODE_REAL", mode_blockers,
                         "config/profile/authority all declare REAL execution mode"))

    # 3. activation-profile completeness -------------------------------------
    profile_blockers: list[str] = []
    if activation_profile is None:
        profile_blockers.append("ACTIVATION_PROFILE_UNBOUND")
    elif activation_profile.status is not RealActivationStatus.ACTIVE:
        profile_blockers.append("ACTIVATION_PROFILE_NOT_ACTIVE")
    else:
        for name in REQUIRED_ACTIVATION_BINDING_NAMES:
            if getattr(activation_profile, name) is None:
                profile_blockers.append("REQUIRED_BINDING_MISSING:" + name)
    checks.append(_check("ACTIVATION_PROFILE_COMPLETE", profile_blockers,
                         "bound ACTIVE REAL activation profile with every required binding"))

    # 4. result-dependent policies are bound (never invented defaults) ---------
    result_blockers: list[str] = []
    missing = config.unbound_result_dependent_bindings()
    if missing:
        result_blockers.append("RESULT_DEPENDENT_POLICIES_UNBOUND:" + ",".join(sorted(missing)))
    checks.append(_check("RESULT_DEPENDENT_POLICIES_BOUND", result_blockers,
                         "result-dependent execution policies are explicitly bound (no guessed defaults)"))

    # 5. authority state ------------------------------------------------------
    authority_blockers: list[str] = []
    if authority is None:
        authority_blockers.append("REAL_AUTHORITY_UNBOUND")
    elif authority.status is not RealAuthorityStatus.ACTIVE:
        authority_blockers.append("REAL_AUTHORITY_NOT_ACTIVE")
    else:
        if not authority.allowed_action_classes:
            authority_blockers.append("REAL_AUTHORITY_NO_ALLOWED_ACTION")
        if not authority.executable_identity:
            authority_blockers.append("REAL_AUTHORITY_EXECUTABLE_IDENTITY_MISSING")
        if authority.credential_readiness is not RealCredentialReadiness.SET:
            authority_blockers.append("REAL_CREDENTIAL_READINESS_NOT_SET")
        if mode == EXTERNAL and authority.test_only:
            authority_blockers.append("REAL_SYNTHETIC_AUTHORITY_FORBIDDEN_IN_EXTERNAL")
    checks.append(_check("AUTHORITY_STATE", authority_blockers,
                         "ACTIVE REAL authority with explicit action scope and executable identity"))

    # 6. authority/profile/config identity consistency -------------------------
    identity_blockers: list[str] = []
    if authority is not None and activation_profile is not None:
        if (
            activation_profile.execution_authority_identity is None
            or activation_profile.execution_authority_identity != authority.identity_id
        ):
            identity_blockers.append("AUTHORITY_PROFILE_IDENTITY_MISMATCH")
    if config.activation_profile is not None and config.activation_profile is not activation_profile:
        identity_blockers.append("CONFIG_PROFILE_IDENTITY_MISMATCH")
    if config.authority is not None and config.authority is not authority:
        identity_blockers.append("CONFIG_AUTHORITY_IDENTITY_MISMATCH")
    checks.append(_check("AUTHORITY_PROFILE_IDENTITY_CONSISTENT", identity_blockers,
                         "authority/profile/config reference the same identities"))

    # 7. contract identity consistency -----------------------------------------
    contract_blockers: list[str] = []
    if "." in config.concrete_contract_id:
        contract_exchange, instrument = config.concrete_contract_id.split(".", 1)
        if contract_exchange != config.exchange:
            contract_blockers.append("CONTRACT_EXCHANGE_MISMATCH")
        if not instrument.startswith(config.product):
            contract_blockers.append("CONTRACT_PRODUCT_MISMATCH")
    if authority is not None and authority.allowed_contracts:
        if config.concrete_contract_id not in authority.allowed_contracts:
            contract_blockers.append("CONTRACT_NOT_IN_AUTHORITY_WHITELIST")
    if activation_profile is not None and activation_profile.status is RealActivationStatus.ACTIVE:
        try:
            activation_profile.require_active_for(config.concrete_contract_id)
        except PermissionError:
            contract_blockers.append("CONTRACT_NOT_IN_ACTIVATION_WHITELIST")
        if authority is not None and authority.allowed_contracts != activation_profile.allowed_contracts:
            contract_blockers.append("AUTHORITY_PROFILE_CONTRACT_WHITELIST_MISMATCH")
    checks.append(_check("CONTRACT_IDENTITY_CONSISTENT", contract_blockers,
                         "contract/exchange/product identity agrees with authority and profile"))

    # 8. risk-policy reference is bound (never embedded numbers) ----------------
    risk_blockers: list[str] = []
    if authority is None or not authority.risk_policy_identity:
        risk_blockers.append("RISK_POLICY_REFERENCE_UNBOUND")
    if activation_profile is None or not activation_profile.risk_policy_identity:
        risk_blockers.append("RISK_POLICY_PROFILE_UNBOUND")
    elif authority is not None and (
        authority.risk_policy_identity != activation_profile.risk_policy_identity
    ):
        risk_blockers.append("RISK_POLICY_IDENTITY_MISMATCH")
    checks.append(_check("RISK_POLICY_BOUND", risk_blockers,
                         "risk policy is referenced by identity, not embedded as numbers"))

    # 9. broker adapter role / account binding ----------------------------------
    broker_blockers: list[str] = []
    if authority is None or not authority.broker_adapter_identity:
        broker_blockers.append("BROKER_ADAPTER_ROLE_UNBOUND")
    if activation_profile is None or not activation_profile.broker_adapter_identity:
        broker_blockers.append("BROKER_ADAPTER_PROFILE_UNBOUND")
    elif authority is not None and (
        authority.broker_adapter_identity != activation_profile.broker_adapter_identity
    ):
        broker_blockers.append("BROKER_ADAPTER_IDENTITY_MISMATCH")
    if authority is None or not authority.account_identity:
        broker_blockers.append("ACCOUNT_IDENTITY_UNBOUND")
    if activation_profile is None or not activation_profile.account_identity:
        broker_blockers.append("ACCOUNT_PROFILE_UNBOUND")
    elif authority is not None and (
        authority.account_identity != activation_profile.account_identity
    ):
        broker_blockers.append("ACCOUNT_IDENTITY_MISMATCH")
    if authority is not None:
        if authority.broker_kind != config.broker_kind:
            broker_blockers.append("BROKER_KIND_MISMATCH")
        if authority.account_kind != config.account_kind:
            broker_blockers.append("ACCOUNT_KIND_MISMATCH")
    if config.account_identity is not None and authority is not None:
        if authority.account_identity != config.account_identity:
            broker_blockers.append("CONFIG_ACCOUNT_IDENTITY_MISMATCH")
    checks.append(_check("BROKER_ACCOUNT_BINDING", broker_blockers,
                         "broker adapter role and account identity are explicitly bound and consistent"))

    # 10. runtime layout / persistence identity ---------------------------------
    layout_blockers: list[str] = []
    if activation_profile is None or not activation_profile.runtime_layout_identity:
        layout_blockers.append("RUNTIME_LAYOUT_IDENTITY_UNBOUND")
    if config.runtime_layout_identity is not None:
        if activation_profile is None or (
            config.runtime_layout_identity != activation_profile.runtime_layout_identity
        ):
            layout_blockers.append("RUNTIME_LAYOUT_IDENTITY_MISMATCH")
    checks.append(_check("RUNTIME_LAYOUT_BOUND", layout_blockers,
                         "persistence/journal/runtime-layout identity is explicitly bound"))

    # 11. bounded validity / expiry / revocation ---------------------------------
    validity_blockers: list[str] = []
    if authority is None:
        validity_blockers.append("REAL_AUTHORITY_UNBOUND")
    elif authority.status is RealAuthorityStatus.REVOKED:
        validity_blockers.append("REAL_AUTHORITY_REVOKED")
    elif authority.status is RealAuthorityStatus.DISABLED:
        validity_blockers.append("REAL_AUTHORITY_DISABLED")
    elif authority.status is not RealAuthorityStatus.ACTIVE:
        validity_blockers.append("REAL_AUTHORITY_NOT_ACTIVE")
    else:
        if authority.valid_from is None or authority.expires_at is None:
            validity_blockers.append("REAL_AUTHORITY_NOT_BOUNDED")
        if assessed_at is None:
            validity_blockers.append("REAL_AUTHORITY_ASSESSMENT_TIME_REQUIRED")
        elif authority.valid_from is None or authority.expires_at is None:
            validity_blockers.append("REAL_AUTHORITY_NOT_BOUNDED")
        elif not (authority.valid_from <= assessed_at < authority.expires_at):
            validity_blockers.append("REAL_AUTHORITY_EXPIRED_OR_NOT_YET_VALID")
    checks.append(_check("BOUNDED_VALIDITY", validity_blockers,
                         "authority is ACTIVE and current within its bounded validity"))

    # 12. durable account truth is an independent first-class gate ----------------
    account_blockers = _state_blockers(account_state, "ACCOUNT_STATE")
    checks.append(_check(
        "ACCOUNT_DURABLE_STATE_CLEAR",
        account_blockers,
        "caller-supplied durable account truth is CLEAR",
    ))

    # 13. durable order/wake/reconciliation state supplied by caller -------------
    durable_blockers: list[str] = []
    durable_blockers.extend(_state_blockers(order_state, "ORDER_STATE"))
    durable_blockers.extend(_state_blockers(wake_state, "WAKE_STATE"))
    durable_blockers.extend(_state_blockers(reconciliation_state, "RECONCILIATION_STATE"))
    checks.append(_check("DURABLE_STATE_CLEAR", durable_blockers,
                         "caller-supplied order/wake/reconciliation state is CLEAR"))

    # 14. offline-only guarantee --------------------------------------------------
    checks.append(_check(
        "NO_EXTERNAL_ACTION",
        [],
        "offline structural preflight only; no network, broker, account or order action performed",
    ))

    overall = "READY" if all(check.status == PASS for check in checks) else "BLOCKED"
    return RealPreflightReport(mode=mode, overall=overall, checks=tuple(checks))


__all__ = [
    "BLOCK",
    "EXTERNAL",
    "PASS",
    "REAL_PREFLIGHT_SCHEMA_VERSION",
    "STRUCTURAL",
    "RealDurableState",
    "RealPreflightCheck",
    "RealPreflightReport",
    "run_real_preflight",
]

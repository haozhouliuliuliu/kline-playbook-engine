"""TEST_ONLY synthetic REAL activation fixture.

OFFLINE ONLY.  This fixture supplies a fully populated, internally consistent
REAL authority / activation profile / runtime config for structural preflight
and authority tests.  It is explicitly TEST_ONLY (``test_only=True``) and can
never be used for an EXTERNAL REAL activation.  No secret value is present and
no network, broker, account or order action is ever performed.

All policy identities are deterministic TEST_ONLY labels, never project policy.
The concrete contract ``SHFE.rb9999`` is a synthetic placeholder, not the final
RB concrete contract (which remains unbound until a later Owner decision).
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from src.real_activation_profile import RealActivationProfile, RealActivationStatus
from src.real_execution_authority import (
    RealActionClass,
    RealAuthorityStatus,
    RealCredentialReadiness,
    RealExecutionAuthority,
)
from src.real_runtime_config import RealRuntimeConfig

TZ = ZoneInfo("Asia/Shanghai")
EXCHANGE = "SHFE"
INSTRUMENT = "rb9999"
CONTRACT = "SHFE.rb9999"
PRODUCT = "rb"
TRADER_IDENTITY = "SYNTHETIC_REAL_TRADER"
BROKER_KIND = "SYNTHETIC_REAL_BROKER_KIND"
ACCOUNT_KIND = "SYNTHETIC_REAL_ACCOUNT_KIND"
BROKER_ADAPTER_IDENTITY = "SYNTHETIC_REAL_BROKER_ADAPTER"
ACCOUNT_IDENTITY = "SYNTHETIC_REAL_ACCOUNT"
RISK_POLICY_IDENTITY = "SYNTHETIC_REAL_RISK_POLICY"
RUNTIME_LAYOUT_IDENTITY = "SYNTHETIC_REAL_RUNTIME_LAYOUT"
EXECUTABLE_IDENTITY = "SYNTHETIC_REAL_EXECUTABLE"
AUTHORITY_ID = "SYNTHETIC_REAL_AUTHORITY_NOT_PROJECT_AUTHORITY"
PROFILE_ID = "SYNTHETIC_REAL_PROFILE_NOT_PROJECT_POLICY"
CONFIG_ID = "SYNTHETIC_REAL_CONFIG"

VALID_FROM = datetime(2026, 1, 1, tzinfo=TZ)
VALID_UNTIL = datetime(2026, 12, 31, 23, 59, 59, tzinfo=TZ)
ASSESSED_AT = datetime(2026, 6, 1, 9, 0, tzinfo=TZ)

# Result-dependent policy identities are TEST_ONLY synthetic labels only.
SIZING_POLICY_IDENTITY = "SYNTHETIC_REAL_SIZING_POLICY"
EXECUTION_PRICE_POLICY_IDENTITY = "SYNTHETIC_REAL_PRICE_POLICY"
STOP_ORDER_POLICY_IDENTITY = "SYNTHETIC_REAL_STOP_POLICY"
CLOSE_OFFSET_POLICY_IDENTITY = "SYNTHETIC_REAL_CLOSE_OFFSET_POLICY"
ROLLOVER_POLICY_IDENTITY = "SYNTHETIC_REAL_ROLLOVER_POLICY"


def synthetic_authority() -> RealExecutionAuthority:
    """Deterministic TEST_ONLY synthetic REAL authority (never project authority)."""
    return RealExecutionAuthority(
        authority_id=AUTHORITY_ID,
        broker_kind=BROKER_KIND,
        account_kind=ACCOUNT_KIND,
        status=RealAuthorityStatus.ACTIVE,
        execution_mode="REAL",
        broker_adapter_identity=BROKER_ADAPTER_IDENTITY,
        account_identity=ACCOUNT_IDENTITY,
        risk_policy_identity=RISK_POLICY_IDENTITY,
        executable_identity=EXECUTABLE_IDENTITY,
        allowed_action_classes=(
            RealActionClass.CONNECT,
            RealActionClass.ORDER_SUBMIT,
            RealActionClass.ORDER_CANCEL,
            RealActionClass.ORDER_REPLACE,
        ),
        allowed_contracts=(CONTRACT,),
        credential_readiness=RealCredentialReadiness.SET,
        valid_from=VALID_FROM,
        expires_at=VALID_UNTIL,
        max_position_lots=1,
        test_only=True,
    )


def synthetic_profile(authority: RealExecutionAuthority | None = None) -> RealActivationProfile:
    """Deterministic TEST_ONLY synthetic REAL activation profile.

    Fully populated: every required binding plus every result-dependent policy
    identity is present so the structural preflight can pass offline.
    """
    if authority is None:
        authority = synthetic_authority()
    return RealActivationProfile(
        profile_id=PROFILE_ID,
        status=RealActivationStatus.ACTIVE,
        execution_mode="REAL",
        execution_authority_identity=authority.identity_id,
        broker_adapter_identity=BROKER_ADAPTER_IDENTITY,
        account_identity=ACCOUNT_IDENTITY,
        risk_policy_identity=RISK_POLICY_IDENTITY,
        runtime_layout_identity=RUNTIME_LAYOUT_IDENTITY,
        allowed_contracts=(CONTRACT,),
        sizing_policy_identity=SIZING_POLICY_IDENTITY,
        execution_price_policy_identity=EXECUTION_PRICE_POLICY_IDENTITY,
        stop_order_policy_identity=STOP_ORDER_POLICY_IDENTITY,
        close_offset_policy_identity=CLOSE_OFFSET_POLICY_IDENTITY,
        rollover_policy_identity=ROLLOVER_POLICY_IDENTITY,
    )


def synthetic_config(
    authority: RealExecutionAuthority | None = None,
    profile: RealActivationProfile | None = None,
    state_root: str | Path = ".",
) -> RealRuntimeConfig:
    """Deterministic TEST_ONLY synthetic REAL runtime config (fully bound)."""
    if authority is None:
        authority = synthetic_authority()
    if profile is None:
        profile = synthetic_profile(authority)
    return (
        RealRuntimeConfig(
            config_id=CONFIG_ID,
            state_root=state_root,
            trader_identity=TRADER_IDENTITY,
            concrete_contract_id=CONTRACT,
            product=PRODUCT,
            exchange=EXCHANGE,
            broker_kind=BROKER_KIND,
            account_kind=ACCOUNT_KIND,
            account_identity=ACCOUNT_IDENTITY,
            runtime_layout_identity=RUNTIME_LAYOUT_IDENTITY,
        )
        .bind_activation_profile(profile)
        .bind_authority(authority)
    )

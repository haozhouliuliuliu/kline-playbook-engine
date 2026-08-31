"""Deterministic offline REAL activation rehearsal over the startup surfaces.

OFFLINE ONLY.  This module drives the REAL controller / supervisor / preflight
surfaces with TEST_ONLY synthetic fakes only: no account login, no broker
connection, no provider call, no DeepSeek request, no order, no real money.

It proves the five fail-closed guarantees of the REAL prebuild:

1. MISSING_GATES_LOCK — default controller is OFFLINE/LOCKED with no new risk;
2. STRUCTURAL_FIXTURE_REACHES_TEST_READY_ONLY — a structurally complete
   synthetic fixture reaches only READY_TEST and never external activation;
3. AUTHORITY_EXPIRY_MID_SESSION_STOPS_NEW_RISK — revoked/expired authority
   stops new risk immediately;
4. UNKNOWN_RECONCILIATION_BLOCKS — UNKNOWN reconciliation blocks preflight and
   forces no-new-risk/restart;
5. RESTART_REQUIRES_FRESH_PREFLIGHT — restart demands a fresh positive preflight
   and fresh reconciliation before READY_TEST can be reached again.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from zoneinfo import ZoneInfo

from src.real_activation_profile import RealActivationProfile, RealActivationStatus
from src.real_execution_authority import (
    RealActionClass,
    RealAuthorityStatus,
    RealCredentialReadiness,
    RealExecutionAuthority,
)
from src.real_preflight import EXTERNAL, STRUCTURAL, RealDurableState
from src.real_runtime_config import RealRuntimeConfig
from src.real_runtime_controller import RealRuntimeController, RealLifecycleState
from src.real_supervisor import RealHealthInput

REAL_OFFLINE_ACTIVATION_REHEARSAL_VERSION = "KPE_REAL_OFFLINE_ACTIVATION_REHEARSAL_V0_1"

TZ = ZoneInfo("Asia/Shanghai")
EXCHANGE = "SHFE"
INSTRUMENT = "rb9999"
CONTRACT = "SHFE.rb9999"
PRODUCT = "rb"
TRADER_IDENTITY = "REAL_REHEARSAL_TRADER"
BROKER_KIND = "REAL_REHEARSAL_FAKE"
ACCOUNT_KIND = "REAL_REHEARSAL_FAKE"
BROKER_ADAPTER_IDENTITY = "REAL_REHEARSAL_FAKE_BROKER_ADAPTER"
ACCOUNT_IDENTITY = "REAL_REHEARSAL_FAKE_ACCOUNT"
RISK_POLICY_IDENTITY = "REAL_REHEARSAL_FAKE_RISK_POLICY"
RUNTIME_LAYOUT_IDENTITY = "REAL_REHEARSAL_FAKE_RUNTIME_LAYOUT"
EXECUTABLE_IDENTITY = "REAL_REHEARSAL_FAKE_EXECUTABLE"
AUTHORITY_ID = "REAL_REHEARSAL_AUTHORITY_NOT_PROJECT_AUTHORITY"
PROFILE_ID = "REAL_REHEARSAL_PROFILE_NOT_PROJECT_POLICY"
CONFIG_ID = "REAL_REHEARSAL_CONFIG"

VALID_FROM = datetime(2026, 1, 1, tzinfo=TZ)
VALID_UNTIL = datetime(2026, 12, 31, 23, 59, 59, tzinfo=TZ)
ASSESSED_AT = datetime(2026, 6, 1, 9, 0, tzinfo=TZ)


# ---------------------------------------------------------------------- fakes


def rehearsal_authority() -> RealExecutionAuthority:
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


def expired_authority() -> RealExecutionAuthority:
    """TEST_ONLY synthetic REAL authority already outside its bounded validity."""
    return RealExecutionAuthority(
        authority_id=AUTHORITY_ID + "_EXPIRED",
        broker_kind=BROKER_KIND,
        account_kind=ACCOUNT_KIND,
        status=RealAuthorityStatus.ACTIVE,
        execution_mode="REAL",
        broker_adapter_identity=BROKER_ADAPTER_IDENTITY,
        account_identity=ACCOUNT_IDENTITY,
        risk_policy_identity=RISK_POLICY_IDENTITY,
        executable_identity=EXECUTABLE_IDENTITY,
        allowed_action_classes=(RealActionClass.CONNECT,),
        allowed_contracts=(CONTRACT,),
        credential_readiness=RealCredentialReadiness.SET,
        valid_from=datetime(2025, 1, 1, tzinfo=TZ),
        expires_at=datetime(2025, 6, 1, tzinfo=TZ),
        max_position_lots=1,
        test_only=True,
    )


def rehearsal_profile(authority: RealExecutionAuthority) -> RealActivationProfile:
    """Deterministic TEST_ONLY synthetic REAL activation profile (fully populated)."""
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
        sizing_policy_identity="REAL_REHEARSAL_SIZING",
        execution_price_policy_identity="REAL_REHEARSAL_PRICE",
        stop_order_policy_identity="REAL_REHEARSAL_STOP",
        close_offset_policy_identity="REAL_REHEARSAL_CLOSE_OFFSET",
        rollover_policy_identity="REAL_REHEARSAL_ROLLOVER",
    )


def rehearsal_config(state_root: str | Path) -> RealRuntimeConfig:
    """Deterministic TEST_ONLY synthetic REAL runtime config (fully bound)."""
    authority = rehearsal_authority()
    profile = rehearsal_profile(authority)
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


def bare_config(state_root: str | Path) -> RealRuntimeConfig:
    """Deterministic TEST_ONLY REAL runtime config with NO authority/profile bound."""
    return RealRuntimeConfig(
        config_id=CONFIG_ID + "_BARE",
        state_root=state_root,
        trader_identity=TRADER_IDENTITY,
        concrete_contract_id=CONTRACT,
        product=PRODUCT,
        exchange=EXCHANGE,
        broker_kind=BROKER_KIND,
        account_kind=ACCOUNT_KIND,
    )


class RehearsalInertCapability:
    """Injected inert connection/order capability; it must never be invoked."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.invoke_calls = 0

    def invoke(self) -> None:  # pragma: no cover - must never be reached
        self.invoke_calls += 1
        raise AssertionError(f"{self.name} must never be invoked by the offline shell")


class RehearsalSwappableAuthoritySource:
    """TEST_ONLY authority source whose current authority can be swapped mid-session."""

    def __init__(self, authority: RealExecutionAuthority) -> None:
        self._authority = authority
        self._source_identity = "REAL_REHEARSAL_SWAPPABLE_SOURCE"

    @property
    def source_identity(self) -> str:
        return self._source_identity

    def current(self) -> RealExecutionAuthority:
        return self._authority

    def set_authority(self, authority: RealExecutionAuthority) -> None:
        self._authority = authority


# -------------------------------------------------------------------- report


@dataclass(frozen=True)
class RealRehearsalScenario:
    name: str
    status: str  # PASS | FAIL
    detail: str

    def __post_init__(self) -> None:
        if self.status not in {"PASS", "FAIL"}:
            raise ValueError("rehearsal scenario status must be PASS or FAIL")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("rehearsal scenario name must be non-empty")
        if not isinstance(self.detail, str):
            raise ValueError("rehearsal scenario detail must be text")


@dataclass(frozen=True)
class RealRehearsalReport:
    version: str
    overall: str  # PASS | FAIL
    scenarios: tuple[RealRehearsalScenario, ...]

    def __post_init__(self) -> None:
        if self.overall not in {"PASS", "FAIL"}:
            raise ValueError("rehearsal overall must be PASS or FAIL")
        if self.overall == "PASS" and any(s.status == "FAIL" for s in self.scenarios):
            raise ValueError("PASS rehearsal cannot contain a FAIL scenario")
        if self.overall == "FAIL" and all(s.status == "PASS" for s in self.scenarios):
            raise ValueError("FAIL rehearsal requires at least one FAIL scenario")

    @property
    def passed(self) -> bool:
        return self.overall == "PASS"

    def public_lines(self) -> tuple[str, ...]:
        return (
            f"REAL_REHEARSAL_VERSION={self.version}",
            f"REAL_REHEARSAL_OVERALL={self.overall}",
            *(
                f"REAL_REHEARSAL_SCENARIO_{scenario.name}={scenario.status}:{scenario.detail}"
                for scenario in self.scenarios
            ),
        )


def _scenario(name: str, failures: list[str]) -> RealRehearsalScenario:
    if failures:
        return RealRehearsalScenario(name=name, status="FAIL", detail=";".join(failures))
    return RealRehearsalScenario(name=name, status="PASS", detail="ok")


# ---------------------------------------------------------------- scenarios


def _missing_gates_lock(root: Path) -> RealRehearsalScenario:
    failures: list[str] = []
    connection = RehearsalInertCapability("connection")
    order_execution = RehearsalInertCapability("order_execution")
    controller = RealRuntimeController(
        config=bare_config(root), connection=connection, order_execution=order_execution
    )
    if controller.state is not RealLifecycleState.OFFLINE:
        failures.append("default state not OFFLINE")
    if not controller.no_new_risk:
        failures.append("default no_new_risk False")
    if controller.external_activation_authorized:
        failures.append("default external activation authorized")
    if not controller.fail_closed_blockers():
        failures.append("default fail-closed blockers empty")
    try:
        controller.activate_for_test(at=ASSESSED_AT)
        failures.append("activate_for_test succeeded without a positive preflight")
    except PermissionError:
        pass
    if controller.state is not RealLifecycleState.PREFLIGHT_FAILED:
        failures.append("state not PREFLIGHT_FAILED after blocked activation")
    if connection.invoke_calls != 0 or order_execution.invoke_calls != 0:
        failures.append("inert capability invoked")
    return _scenario("MISSING_GATES_LOCK", failures)


def _structural_fixture_reaches_test_ready(root: Path) -> RealRehearsalScenario:
    failures: list[str] = []
    connection = RehearsalInertCapability("connection")
    order_execution = RehearsalInertCapability("order_execution")
    config = rehearsal_config(root)
    controller = RealRuntimeController(
        config=config, connection=connection, order_execution=order_execution, mode=STRUCTURAL
    )
    report = controller.preflight(assessed_at=ASSESSED_AT, order_state=RealDurableState.CLEAR,
                                  wake_state=RealDurableState.CLEAR, account_state=RealDurableState.CLEAR,
                                  reconciliation_state=RealDurableState.CLEAR)
    if not report.ready:
        failures.append("structural preflight not ready for fully bound fixture")
    controller.activate_for_test(at=ASSESSED_AT)
    if controller.state is not RealLifecycleState.READY_TEST:
        failures.append("state not READY_TEST after activation")
    if not controller.test_ready:
        failures.append("test_ready False at READY_TEST")
    if controller.external_activation_authorized:
        failures.append("external activation authorized at READY_TEST")
    if connection.invoke_calls != 0 or order_execution.invoke_calls != 0:
        failures.append("inert capability invoked")
    # A synthetic (test_only) authority in EXTERNAL mode must be blocked.
    external = RealRuntimeController(config=config, mode=EXTERNAL)
    external_report = external.preflight(
        assessed_at=ASSESSED_AT, order_state=RealDurableState.CLEAR,
        wake_state=RealDurableState.CLEAR, account_state=RealDurableState.CLEAR,
        reconciliation_state=RealDurableState.CLEAR,
    )
    if external_report.ready:
        failures.append("synthetic EXTERNAL preflight unexpectedly ready")
    return _scenario("STRUCTURAL_FIXTURE_REACHES_TEST_READY_ONLY", failures)


def _authority_expiry_mid_session_stops_new_risk(root: Path) -> RealRehearsalScenario:
    failures: list[str] = []
    config = rehearsal_config(root)
    source = RehearsalSwappableAuthoritySource(config.authority)
    controller = RealRuntimeController(config=config, authority_source=source, mode=STRUCTURAL)
    report = controller.preflight(assessed_at=ASSESSED_AT, order_state=RealDurableState.CLEAR,
                                  wake_state=RealDurableState.CLEAR, account_state=RealDurableState.CLEAR,
                                  reconciliation_state=RealDurableState.CLEAR)
    if not report.ready:
        failures.append("initial structural preflight not ready")
    controller.activate_for_test(at=ASSESSED_AT)
    if controller.state is not RealLifecycleState.READY_TEST:
        failures.append("state not READY_TEST before mid-session change")
    clean = controller.assess(assessed_at=ASSESSED_AT)
    if clean.no_new_risk:
        failures.append("clean assessment reports no_new_risk")
    if controller.no_new_risk:
        failures.append("controller no_new_risk True while clean")
    # revocation mid-session
    source.set_authority(config.authority.revoked())
    revoked_assessment = controller.assess(assessed_at=ASSESSED_AT)
    if not revoked_assessment.no_new_risk:
        failures.append("revocation did not stop new risk")
    if not controller.no_new_risk:
        failures.append("controller no_new_risk False after revocation")
    # expiry mid-session
    source.set_authority(expired_authority())
    expired_assessment = controller.assess(assessed_at=ASSESSED_AT)
    if not expired_assessment.no_new_risk:
        failures.append("expiry did not stop new risk")
    if not controller.no_new_risk:
        failures.append("controller no_new_risk False after expiry")
    return _scenario("AUTHORITY_EXPIRY_MID_SESSION_STOPS_NEW_RISK", failures)


def _unknown_reconciliation_blocks(root: Path) -> RealRehearsalScenario:
    failures: list[str] = []
    controller = RealRuntimeController(config=rehearsal_config(root), mode=STRUCTURAL)
    report = controller.preflight(
        assessed_at=ASSESSED_AT, order_state=RealDurableState.CLEAR,
        wake_state=RealDurableState.CLEAR, account_state=RealDurableState.CLEAR,
        reconciliation_state=RealDurableState.UNKNOWN,
    )
    if report.ready:
        failures.append("preflight ready despite UNKNOWN reconciliation")
    try:
        controller.activate_for_test(at=ASSESSED_AT)
        failures.append("activate succeeded despite UNKNOWN reconciliation")
    except PermissionError:
        pass
    if controller.state is not RealLifecycleState.PREFLIGHT_FAILED:
        failures.append("state not PREFLIGHT_FAILED despite UNKNOWN reconciliation")
    supervisor = controller.assess(
        assessed_at=ASSESSED_AT, reconciliation_health=RealHealthInput.UNKNOWN
    )
    if not supervisor.no_new_risk:
        failures.append("supervisor no_new_risk False on UNKNOWN reconciliation")
    if not supervisor.restart_required:
        failures.append("supervisor restart not required on UNKNOWN reconciliation")
    return _scenario("UNKNOWN_RECONCILIATION_BLOCKS", failures)


def _restart_requires_fresh_preflight(root: Path) -> RealRehearsalScenario:
    failures: list[str] = []
    controller = RealRuntimeController(config=rehearsal_config(root), mode=STRUCTURAL)
    report = controller.preflight(assessed_at=ASSESSED_AT, order_state=RealDurableState.CLEAR,
                                  wake_state=RealDurableState.CLEAR, account_state=RealDurableState.CLEAR,
                                  reconciliation_state=RealDurableState.CLEAR)
    if not report.ready:
        failures.append("initial preflight not ready")
    controller.activate_for_test(at=ASSESSED_AT)
    if controller.state is not RealLifecycleState.READY_TEST:
        failures.append("state not READY_TEST before restart")
    controller.request_restart()
    if controller.state is not RealLifecycleState.LOCKED:
        failures.append("state not LOCKED after restart request")
    if controller.preflight_receipt is not None:
        failures.append("preflight receipt not cleared on restart")
    try:
        controller.activate_for_test(at=ASSESSED_AT)
        failures.append("activate succeeded without fresh preflight after restart")
    except PermissionError:
        pass
    fresh = controller.preflight(assessed_at=ASSESSED_AT, order_state=RealDurableState.CLEAR,
                                 wake_state=RealDurableState.CLEAR, account_state=RealDurableState.CLEAR,
                                 reconciliation_state=RealDurableState.CLEAR)
    if not fresh.ready:
        failures.append("fresh post-restart preflight not ready")
    controller.activate_for_test(at=ASSESSED_AT)
    if controller.state is not RealLifecycleState.READY_TEST:
        failures.append("state not READY_TEST after fresh preflight")
    # A second restart with UNKNOWN reconciliation must stay blocked.
    controller.request_restart()
    blocked = controller.preflight(
        assessed_at=ASSESSED_AT, order_state=RealDurableState.CLEAR,
        wake_state=RealDurableState.CLEAR, account_state=RealDurableState.CLEAR,
        reconciliation_state=RealDurableState.UNKNOWN,
    )
    if blocked.ready:
        failures.append("post-restart preflight ready despite UNKNOWN reconciliation")
    return _scenario("RESTART_REQUIRES_FRESH_PREFLIGHT", failures)


def run_real_offline_rehearsal() -> RealRehearsalReport:
    """Run every offline REAL activation-rehearsal scenario deterministically."""
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        scenarios = (
            _missing_gates_lock(root),
            _structural_fixture_reaches_test_ready(root),
            _authority_expiry_mid_session_stops_new_risk(root),
            _unknown_reconciliation_blocks(root),
            _restart_requires_fresh_preflight(root),
        )
    overall = "PASS" if all(scenario.status == "PASS" for scenario in scenarios) else "FAIL"
    return RealRehearsalReport(
        version=REAL_OFFLINE_ACTIVATION_REHEARSAL_VERSION,
        overall=overall,
        scenarios=scenarios,
    )


__all__ = [
    "REAL_OFFLINE_ACTIVATION_REHEARSAL_VERSION",
    "ASSESSED_AT",
    "CONTRACT",
    "RehearsalInertCapability",
    "RehearsalSwappableAuthoritySource",
    "RealRehearsalReport",
    "RealRehearsalScenario",
    "bare_config",
    "expired_authority",
    "rehearsal_authority",
    "rehearsal_config",
    "rehearsal_profile",
    "run_real_offline_rehearsal",
]

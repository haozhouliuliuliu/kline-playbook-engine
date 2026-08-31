"""Deterministic offline tests for the REAL runtime controller lifecycle shell.

Proves the controller is locked by default, a structurally complete synthetic
fixture reaches only READY_TEST, expired/revoked/mismatched authority blocks,
UNKNOWN durable inputs block, pause/shutdown/restart transitions are
deterministic, injected connection/order capabilities stay inert, and a test
fixture authority is never treated as external execution authority.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.real_execution_authority import (
    RealAuthorityStatus,
    RealCredentialReadiness,
    RealExecutionAuthority,
)
from src.real_preflight import EXTERNAL, STRUCTURAL, RealDurableState
from src.real_runtime_controller import RealLifecycleState, RealRuntimeController
from tests.real_synthetic_fixture import (
    ASSESSED_AT,
    synthetic_authority,
    synthetic_config,
    synthetic_profile,
)

TZ = ASSESSED_AT.tzinfo


class _InertCapability:
    def __init__(self, name: str) -> None:
        self.name = name
        self.invoke_calls = 0

    def invoke(self) -> None:  # pragma: no cover
        self.invoke_calls += 1
        raise AssertionError(f"{self.name} must never be invoked")


def _bound_controller(state_root: Path, **kwargs: object) -> RealRuntimeController:
    config = synthetic_config(state_root=state_root)
    return RealRuntimeController(
        config=config,
        connection=_InertCapability("connection"),
        order_execution=_InertCapability("order_execution"),
        **kwargs,
    )


def _clean_preflight(controller: RealRuntimeController) -> object:
    return controller.preflight(
        assessed_at=ASSESSED_AT,
        order_state=RealDurableState.CLEAR,
        wake_state=RealDurableState.CLEAR,
        account_state=RealDurableState.CLEAR,
        reconciliation_state=RealDurableState.CLEAR,
    )


class RealRuntimeControllerTests(unittest.TestCase):
    def test_default_controller_is_off_inactive_and_locked(self) -> None:
        with TemporaryDirectory() as tmp:
            controller = _bound_controller(Path(tmp))
            self.assertIs(controller.state, RealLifecycleState.OFFLINE)
            self.assertTrue(controller.no_new_risk)
            self.assertFalse(controller.test_ready)
            self.assertFalse(controller.external_activation_authorized)
            self.assertIn("POSITIVE_PREFLIGHT_REQUIRED", controller.fail_closed_blockers())
            self.assertIn("CONTROLLER_NOT_READY:OFFLINE", controller.fail_closed_blockers())

    def test_structural_fixture_reaches_only_test_ready(self) -> None:
        with TemporaryDirectory() as tmp:
            controller = _bound_controller(Path(tmp))
            report = _clean_preflight(controller)
            self.assertTrue(report.ready)
            controller.activate_for_test(at=ASSESSED_AT)
            self.assertIs(controller.state, RealLifecycleState.READY_TEST)
            self.assertTrue(controller.test_ready)
            self.assertFalse(controller.external_activation_authorized)
            connection = controller.connection
            order_execution = controller.order_execution
            self.assertEqual(connection.invoke_calls, 0)
            self.assertEqual(order_execution.invoke_calls, 0)

    def test_blocked_preflight_prevents_activation(self) -> None:
        with TemporaryDirectory() as tmp:
            controller = _bound_controller(Path(tmp))
            report = controller.preflight(
                assessed_at=ASSESSED_AT,
                order_state=RealDurableState.UNRESOLVED,
                wake_state=RealDurableState.CLEAR,
                account_state=RealDurableState.CLEAR,
                reconciliation_state=RealDurableState.CLEAR,
            )
            self.assertFalse(report.ready)
            self.assertIs(controller.state, RealLifecycleState.PREFLIGHT_FAILED)
            with self.assertRaisesRegex(PermissionError, "REAL_POSITIVE_PREFLIGHT_REQUIRED"):
                controller.activate_for_test(at=ASSESSED_AT)

    def test_unknown_reconciliation_blocks(self) -> None:
        with TemporaryDirectory() as tmp:
            controller = _bound_controller(Path(tmp))
            report = controller.preflight(
                assessed_at=ASSESSED_AT,
                order_state=RealDurableState.CLEAR,
                wake_state=RealDurableState.CLEAR,
                account_state=RealDurableState.CLEAR,
                reconciliation_state=RealDurableState.UNKNOWN,
            )
            self.assertFalse(report.ready)
            self.assertIs(controller.state, RealLifecycleState.PREFLIGHT_FAILED)

    def test_unknown_account_state_reaches_preflight_and_blocks_test_ready(self) -> None:
        with TemporaryDirectory() as tmp:
            controller = _bound_controller(Path(tmp))
            report = controller.preflight(
                assessed_at=ASSESSED_AT,
                order_state=RealDurableState.CLEAR,
                wake_state=RealDurableState.CLEAR,
                account_state=RealDurableState.UNKNOWN,
                reconciliation_state=RealDurableState.CLEAR,
            )

            self.assertFalse(report.ready)
            account_check = next(
                check for check in report.checks if check.name == "ACCOUNT_DURABLE_STATE_CLEAR"
            )
            self.assertIn("ACCOUNT_STATE_UNKNOWN", account_check.detail)
            with self.assertRaisesRegex(PermissionError, "REAL_POSITIVE_PREFLIGHT_REQUIRED"):
                controller.activate_for_test(at=ASSESSED_AT)

    def test_expired_authority_blocks_activation(self) -> None:
        with TemporaryDirectory() as tmp:
            authority = synthetic_authority()
            profile = synthetic_profile(authority)
            config = synthetic_config(authority=authority, profile=profile, state_root=Path(tmp))
            controller = RealRuntimeController(config=config)
            report = controller.preflight(
                assessed_at=datetime(2027, 1, 1, tzinfo=TZ),
                order_state=RealDurableState.CLEAR,
                wake_state=RealDurableState.CLEAR,
                account_state=RealDurableState.CLEAR,
                reconciliation_state=RealDurableState.CLEAR,
            )
            self.assertFalse(report.ready)
            with self.assertRaises(PermissionError):
                controller.activate_for_test(at=datetime(2027, 1, 1, tzinfo=TZ))

    def test_revoked_authority_blocks_activation(self) -> None:
        with TemporaryDirectory() as tmp:
            revoked = synthetic_authority().revoked()
            profile = synthetic_profile(revoked)
            config = synthetic_config(authority=revoked, profile=profile, state_root=Path(tmp))
            controller = RealRuntimeController(config=config)
            report = _clean_preflight(controller)
            self.assertFalse(report.ready)
            self.assertIs(controller.state, RealLifecycleState.PREFLIGHT_FAILED)

    def test_mismatched_authority_source_stops_new_risk(self) -> None:
        with TemporaryDirectory() as tmp:
            authority = synthetic_authority()
            profile = synthetic_profile(authority)
            config = synthetic_config(authority=authority, profile=profile, state_root=Path(tmp))
            other = RealExecutionAuthority(
                authority_id="OTHER_AUTHORITY",
                broker_kind=authority.broker_kind,
                account_kind=authority.account_kind,
                status=RealAuthorityStatus.ACTIVE,
                execution_mode="REAL",
                broker_adapter_identity=authority.broker_adapter_identity,
                account_identity=authority.account_identity,
                risk_policy_identity=authority.risk_policy_identity,
                executable_identity=authority.executable_identity,
                allowed_action_classes=authority.allowed_action_classes,
                allowed_contracts=authority.allowed_contracts,
                credential_readiness=RealCredentialReadiness.SET,
                valid_from=authority.valid_from,
                expires_at=authority.expires_at,
                max_position_lots=authority.max_position_lots,
                test_only=True,
            )

            class _SwappableSource:
                def __init__(self, current: RealExecutionAuthority) -> None:
                    self._current = current

                @property
                def source_identity(self) -> str:
                    return "CONTROLLER_TEST_MISMATCH"

                def current(self) -> RealExecutionAuthority:
                    return self._current

            source = _SwappableSource(authority)
            controller = RealRuntimeController(config=config, authority_source=source)
            _clean_preflight(controller)
            controller.activate_for_test(at=ASSESSED_AT)
            clean = controller.assess(assessed_at=ASSESSED_AT)
            self.assertFalse(clean.no_new_risk)
            # mid-session swap to a valid but different authority identity
            source._current = other
            assessment = controller.assess(assessed_at=ASSESSED_AT)
            self.assertTrue(assessment.no_new_risk)
            self.assertIn("REAL_AUTHORITY_IDENTITY_MISMATCH", assessment.no_new_risk_blockers)
            self.assertTrue(controller.no_new_risk)

    def test_pause_shutdown_and_no_new_risk_transitions(self) -> None:
        with TemporaryDirectory() as tmp:
            controller = _bound_controller(Path(tmp))
            _clean_preflight(controller)
            controller.activate_for_test(at=ASSESSED_AT)
            self.assertIs(controller.state, RealLifecycleState.READY_TEST)
            controller.pause()
            self.assertIs(controller.state, RealLifecycleState.PAUSED)
            self.assertTrue(controller.no_new_risk)
            controller.shutdown()
            self.assertIs(controller.state, RealLifecycleState.SHUTDOWN)
            self.assertTrue(controller.no_new_risk)
            with self.assertRaisesRegex(RuntimeError, "REAL_CONTROLLER_SHUTDOWN"):
                controller.activate_for_test(at=ASSESSED_AT)

    def test_restart_requires_fresh_preflight(self) -> None:
        with TemporaryDirectory() as tmp:
            controller = _bound_controller(Path(tmp))
            _clean_preflight(controller)
            controller.activate_for_test(at=ASSESSED_AT)
            controller.request_restart()
            self.assertIs(controller.state, RealLifecycleState.LOCKED)
            self.assertIn("CONTROLLER_NOT_READY:LOCKED", controller.fail_closed_blockers())
            with self.assertRaises(PermissionError):
                controller.activate_for_test(at=ASSESSED_AT)
            report = _clean_preflight(controller)
            self.assertTrue(report.ready)
            controller.activate_for_test(at=ASSESSED_AT)
            self.assertIs(controller.state, RealLifecycleState.READY_TEST)

    def test_authority_expiry_mid_session_stops_new_risk(self) -> None:
        with TemporaryDirectory() as tmp:
            authority = synthetic_authority()
            profile = synthetic_profile(authority)
            config = synthetic_config(authority=authority, profile=profile, state_root=Path(tmp))

            class _SwappableSource:
                def __init__(self, current: RealExecutionAuthority) -> None:
                    self._current = current

                @property
                def source_identity(self) -> str:
                    return "CONTROLLER_TEST_SWAPPABLE"

                def current(self) -> RealExecutionAuthority:
                    return self._current

            source = _SwappableSource(authority)
            controller = RealRuntimeController(config=config, authority_source=source)
            _clean_preflight(controller)
            controller.activate_for_test(at=ASSESSED_AT)
            clean = controller.assess(assessed_at=ASSESSED_AT)
            self.assertFalse(clean.no_new_risk)
            # expire mid-session
            expired = RealExecutionAuthority(
                authority_id="EXPIRED_AUTHORITY",
                broker_kind=authority.broker_kind,
                account_kind=authority.account_kind,
                status=RealAuthorityStatus.ACTIVE,
                execution_mode="REAL",
                broker_adapter_identity=authority.broker_adapter_identity,
                account_identity=authority.account_identity,
                risk_policy_identity=authority.risk_policy_identity,
                executable_identity=authority.executable_identity,
                allowed_action_classes=authority.allowed_action_classes,
                allowed_contracts=authority.allowed_contracts,
                credential_readiness=RealCredentialReadiness.SET,
                valid_from=datetime(2025, 1, 1, tzinfo=TZ),
                expires_at=datetime(2025, 6, 1, tzinfo=TZ),
                max_position_lots=1,
                test_only=True,
            )
            source._current = expired
            assessment = controller.assess(assessed_at=ASSESSED_AT)
            self.assertTrue(assessment.no_new_risk)
            self.assertTrue(controller.no_new_risk)

    def test_synthetic_authority_never_external(self) -> None:
        with TemporaryDirectory() as tmp:
            controller = _bound_controller(Path(tmp), mode=EXTERNAL)
            report = _clean_preflight(controller)
            self.assertFalse(report.ready)
            self.assertIs(controller.state, RealLifecycleState.PREFLIGHT_FAILED)
            self.assertIn(
                "REAL_SYNTHETIC_AUTHORITY_FORBIDDEN_IN_EXTERNAL", controller.fail_closed_blockers()
            )

    def test_snapshot_is_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            one = _bound_controller(Path(tmp)).snapshot()
            two = _bound_controller(Path(tmp)).snapshot()
            self.assertEqual(one.identity_id, two.identity_id)
            self.assertFalse(one.external_activation_authorized)
            self.assertTrue(one.no_new_risk)


if __name__ == "__main__":
    unittest.main()

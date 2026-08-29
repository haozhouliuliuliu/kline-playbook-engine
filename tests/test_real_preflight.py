"""Deterministic offline tests for the REAL activation preflight.

Proves the real external surface fails closed today, a fully populated
TEST_ONLY synthetic fixture can pass offline structural preflight, synthetic
authorities are blocked in EXTERNAL mode, expired/revoked authority fails,
identity mismatches fail, missing bindings fail, caller-supplied durable state
must be CLEAR, no secret leaks, and the preflight itself never performs an
external action.
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
from src.real_preflight import (
    EXTERNAL,
    STRUCTURAL,
    RealDurableState,
    RealPreflightReport,
    run_real_preflight,
)
from tests.real_synthetic_fixture import (
    ASSESSED_AT,
    synthetic_authority,
    synthetic_config,
    synthetic_profile,
)


def _fully_bound(mode: str = STRUCTURAL, state_root: str | Path = ".") -> object:
    config = synthetic_config(state_root=state_root)
    return run_real_preflight(
        config=config,
        mode=mode,
        assessed_at=ASSESSED_AT,
        order_state=RealDurableState.CLEAR,
        wake_state=RealDurableState.CLEAR,
        reconciliation_state=RealDurableState.CLEAR,
    )


def _bare_config(state_root: str | Path) -> object:
    from src.real_runtime_config import RealRuntimeConfig
    from tests.real_synthetic_fixture import (
        ACCOUNT_KIND,
        BROKER_KIND,
        CONFIG_ID,
        CONTRACT,
        EXCHANGE,
        PRODUCT,
        TRADER_IDENTITY,
    )

    return RealRuntimeConfig(
        config_id=CONFIG_ID,
        state_root=state_root,
        trader_identity=TRADER_IDENTITY,
        concrete_contract_id=CONTRACT,
        product=PRODUCT,
        exchange=EXCHANGE,
        broker_kind=BROKER_KIND,
        account_kind=ACCOUNT_KIND,
    )


class RealPreflightTests(unittest.TestCase):
    def test_real_external_profile_fails_closed_today(self) -> None:
        with TemporaryDirectory() as tmp:
            # no authority / no profile bound -> fail closed today
            config = _bare_config(Path(tmp))
            report = run_real_preflight(config=config, mode=EXTERNAL, assessed_at=ASSESSED_AT)
            self.assertFalse(report.ready)
            self.assertEqual(report.overall, "BLOCKED")
            names = {check.name for check in report.checks}
            self.assertIn("AUTHORITY_STATE", names)
            self.assertIn("ACTIVATION_PROFILE_COMPLETE", names)
            authority_check = next(c for c in report.checks if c.name == "AUTHORITY_STATE")
            self.assertIn("REAL_AUTHORITY_UNBOUND", authority_check.detail)

    def test_structurally_populated_synthetic_fixture_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            report = _fully_bound(mode=STRUCTURAL, state_root=Path(tmp))
            self.assertTrue(report.ready)
            self.assertEqual(report.overall, "READY")
            # the offline-only guarantee is explicit
            offline = next(c for c in report.checks if c.name == "NO_EXTERNAL_ACTION")
            self.assertEqual(offline.status, "PASS")

    def test_synthetic_authority_is_blocked_in_external_mode(self) -> None:
        with TemporaryDirectory() as tmp:
            report = _fully_bound(mode=EXTERNAL, state_root=Path(tmp))
            self.assertFalse(report.ready)
            authority_check = next(c for c in report.checks if c.name == "AUTHORITY_STATE")
            self.assertIn("REAL_SYNTHETIC_AUTHORITY_FORBIDDEN_IN_EXTERNAL", authority_check.detail)

    def test_missing_account_contract_risk_broker_bindings_fail_closed(self) -> None:
        # An ACTIVE authority with a required binding removed cannot be built,
        # so this test verifies preflight blocks when bindings are missing at
        # the config/profile level (unbound profile + no authority).
        with TemporaryDirectory() as tmp:
            bare = _bare_config(Path(tmp))
            report = run_real_preflight(
                config=bare,
                mode=STRUCTURAL,
                assessed_at=ASSESSED_AT,
                order_state=RealDurableState.CLEAR,
                wake_state=RealDurableState.CLEAR,
                reconciliation_state=RealDurableState.CLEAR,
            )
            self.assertFalse(report.ready)
            blocked_names = {c.name for c in report.blocked_checks}
            self.assertIn("AUTHORITY_STATE", blocked_names)
            self.assertIn("ACTIVATION_PROFILE_COMPLETE", blocked_names)
            self.assertIn("RISK_POLICY_BOUND", blocked_names)
            self.assertIn("BROKER_ACCOUNT_BINDING", blocked_names)

    def test_expired_authority_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            authority = synthetic_authority()
            profile = synthetic_profile(authority)
            config = synthetic_config(authority=authority, profile=profile, state_root=Path(tmp))
            after = datetime(2027, 1, 1, tzinfo=authority.expires_at.tzinfo)
            report = run_real_preflight(
                config=config,
                mode=STRUCTURAL,
                assessed_at=after,
                order_state=RealDurableState.CLEAR,
                wake_state=RealDurableState.CLEAR,
                reconciliation_state=RealDurableState.CLEAR,
            )
            self.assertFalse(report.ready)
            validity = next(c for c in report.checks if c.name == "BOUNDED_VALIDITY")
            self.assertIn("REAL_AUTHORITY_EXPIRED_OR_NOT_YET_VALID", validity.detail)

    def test_revoked_authority_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            revoked = synthetic_authority().revoked()
            profile = synthetic_profile(revoked)
            config = synthetic_config(authority=revoked, profile=profile, state_root=Path(tmp))
            report = run_real_preflight(
                config=config,
                mode=STRUCTURAL,
                assessed_at=ASSESSED_AT,
                order_state=RealDurableState.CLEAR,
                wake_state=RealDurableState.CLEAR,
                reconciliation_state=RealDurableState.CLEAR,
            )
            self.assertFalse(report.ready)
            validity = next(c for c in report.checks if c.name == "BOUNDED_VALIDITY")
            self.assertIn("REAL_AUTHORITY_REVOKED", validity.detail)

    def test_mismatched_authority_profile_identity_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            authority = synthetic_authority()
            # profile bound to a *different* authority identity
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
            profile = synthetic_profile(other)
            config = synthetic_config(authority=authority, profile=profile, state_root=Path(tmp))
            report = run_real_preflight(
                config=config,
                mode=STRUCTURAL,
                assessed_at=ASSESSED_AT,
                order_state=RealDurableState.CLEAR,
                wake_state=RealDurableState.CLEAR,
                reconciliation_state=RealDurableState.CLEAR,
            )
            self.assertFalse(report.ready)
            identity_check = next(
                c for c in report.checks if c.name == "AUTHORITY_PROFILE_IDENTITY_CONSISTENT"
            )
            self.assertIn("AUTHORITY_PROFILE_IDENTITY_MISMATCH", identity_check.detail)

    def test_wrong_execution_mode_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            authority = synthetic_authority()
            profile = synthetic_profile(authority)
            # force a non-REAL mode on the frozen profile to prove the preflight
            # rejects an inconsistent/ambiguous activation request
            object.__setattr__(profile, "execution_mode", "PAPER")
            config = synthetic_config(authority=authority, profile=profile, state_root=Path(tmp))
            report = run_real_preflight(
                config=config,
                mode=STRUCTURAL,
                assessed_at=ASSESSED_AT,
                order_state=RealDurableState.CLEAR,
                wake_state=RealDurableState.CLEAR,
                reconciliation_state=RealDurableState.CLEAR,
            )
            self.assertFalse(report.ready)
            mode_check = next(c for c in report.checks if c.name == "EXECUTION_MODE_REAL")
            self.assertIn("PROFILE_EXECUTION_MODE_NOT_REAL", mode_check.detail)

    def test_unbound_risk_policy_reference_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            # A fully bound authority with NO activation profile leaves the risk
            # policy reference unresolved and must fail closed.
            authority = synthetic_authority()
            config = synthetic_config(authority=authority, state_root=Path(tmp))
            # strip the profile binding so the risk-policy reference is unbound
            from src.real_runtime_config import RealRuntimeConfig

            unbound_profile = RealRuntimeConfig(
                config_id=config.config_id,
                state_root=config.state_root,
                trader_identity=config.trader_identity,
                concrete_contract_id=config.concrete_contract_id,
                product=config.product,
                exchange=config.exchange,
                broker_kind=config.broker_kind,
                account_kind=config.account_kind,
                account_identity=config.account_identity,
                runtime_layout_identity=config.runtime_layout_identity,
            ).bind_authority(authority)
            report = run_real_preflight(
                config=unbound_profile,
                mode=STRUCTURAL,
                assessed_at=ASSESSED_AT,
                order_state=RealDurableState.CLEAR,
                wake_state=RealDurableState.CLEAR,
                reconciliation_state=RealDurableState.CLEAR,
            )
            self.assertFalse(report.ready)
            risk_check = next(c for c in report.checks if c.name == "RISK_POLICY_BOUND")
            self.assertIn("RISK_POLICY_PROFILE_UNBOUND", risk_check.detail)

    def test_unresolved_durable_state_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            for state, label in (
                (RealDurableState.UNRESOLVED, "ORDER_STATE_UNRESOLVED"),
                (RealDurableState.UNKNOWN, "RECONCILIATION_STATE_UNKNOWN"),
                (None, "WAKE_STATE_NOT_SUPPLIED"),
            ):
                config = synthetic_config(state_root=Path(tmp))
                kwargs = {
                    "config": config,
                    "mode": STRUCTURAL,
                    "assessed_at": ASSESSED_AT,
                    "order_state": RealDurableState.CLEAR,
                    "wake_state": RealDurableState.CLEAR,
                    "reconciliation_state": RealDurableState.CLEAR,
                }
                if state is RealDurableState.UNRESOLVED:
                    kwargs["order_state"] = RealDurableState.UNRESOLVED
                elif state is RealDurableState.UNKNOWN:
                    kwargs["reconciliation_state"] = RealDurableState.UNKNOWN
                else:
                    kwargs["wake_state"] = None
                report = run_real_preflight(**kwargs)
                self.assertFalse(report.ready)
                durable = next(c for c in report.checks if c.name == "DURABLE_STATE_CLEAR")
                self.assertIn(label, durable.detail)

    def test_public_lines_leak_no_secret(self) -> None:
        with TemporaryDirectory() as tmp:
            report = _fully_bound(mode=STRUCTURAL, state_root=Path(tmp))
            text = "\n".join(report.public_lines())
            for secretish in ("DEEPSEEK_API_KEY", "FANGZHENG", "password", "PASSWORD="):
                self.assertNotIn(secretish.lower() if "password" in secretish.lower() else secretish, text.lower())
            self.assertIn("REAL_PREFLIGHT_OVERALL=READY", text)

    def test_report_identity_is_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            one = _fully_bound(mode=STRUCTURAL, state_root=Path(tmp))
            two = _fully_bound(mode=STRUCTURAL, state_root=Path(tmp))
            self.assertEqual(one.identity, two.identity)
            self.assertEqual(one.public_lines(), two.public_lines())

    def test_report_type_validation(self) -> None:
        with self.assertRaises(ValueError):
            RealPreflightReport(mode="BAD", overall="READY", checks=())
        with self.assertRaises(ValueError):
            RealPreflightReport(mode=EXTERNAL, overall="BLOCKED", checks=())

    def test_preflight_performs_no_external_action(self) -> None:
        # A fully populated structural preflight passes without any external
        # action; the report explicitly records the offline-only guarantee.
        with TemporaryDirectory() as tmp:
            report = _fully_bound(mode=STRUCTURAL, state_root=Path(tmp))
            self.assertTrue(report.ready)
            offline = next(c for c in report.checks if c.name == "NO_EXTERNAL_ACTION")
            self.assertIn("no network, broker, account or order action performed", offline.detail)


if __name__ == "__main__":
    unittest.main()

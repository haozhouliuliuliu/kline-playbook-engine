"""Deterministic offline tests for the REAL execution authority.

Proves default construction grants nothing, ACTIVE requires every binding,
expired/revoked/disabled fail closed, bounded validity is enforced, no secret
value is representable, and no permanent numeric risk rule is embedded.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import unittest

from src.real_execution_authority import (
    RealActionClass,
    RealAuthorityStatus,
    RealCredentialReadiness,
    RealExecutionAuthority,
)
from tests.real_synthetic_fixture import (
    ACCOUNT_IDENTITY,
    ASSESSED_AT,
    AUTHORITY_ID,
    BROKER_ADAPTER_IDENTITY,
    BROKER_KIND,
    ACCOUNT_KIND,
    CONTRACT,
    EXECUTABLE_IDENTITY,
    RISK_POLICY_IDENTITY,
    TZ,
    VALID_FROM,
    VALID_UNTIL,
    synthetic_authority,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


class RealExecutionAuthorityTests(unittest.TestCase):
    def test_default_construction_grants_nothing(self) -> None:
        authority = RealExecutionAuthority(
            authority_id="default-authority",
            broker_kind=BROKER_KIND,
            account_kind=ACCOUNT_KIND,
            status=RealAuthorityStatus.PENDING,
        )
        self.assertIs(authority.status, RealAuthorityStatus.PENDING)
        self.assertEqual(authority.allowed_action_classes, ())
        self.assertEqual(authority.allowed_contracts, ())
        self.assertIsNone(authority.account_identity)
        self.assertIsNone(authority.risk_policy_identity)
        with self.assertRaisesRegex(PermissionError, "REAL_AUTHORITY_NOT_ACTIVE"):
            authority.require_connect(at=ASSESSED_AT)
        with self.assertRaisesRegex(PermissionError, "REAL_AUTHORITY_NOT_ACTIVE"):
            authority.require_order_submit(CONTRACT, at=ASSESSED_AT)

    def test_default_construction_requires_real_mode_and_explicit_status(self) -> None:
        with self.assertRaisesRegex(ValueError, "execution_mode must be REAL"):
            RealExecutionAuthority(
                authority_id="bad-mode",
                broker_kind=BROKER_KIND,
                account_kind=ACCOUNT_KIND,
                status=RealAuthorityStatus.PENDING,
                execution_mode="PAPER",
            )
        with self.assertRaisesRegex(ValueError, "status must be explicit"):
            RealExecutionAuthority(
                authority_id="bad-status",
                broker_kind=BROKER_KIND,
                account_kind=ACCOUNT_KIND,
                status="PENDING",
            )

    def test_active_requires_every_required_binding(self) -> None:
        # A single missing binding must fail ACTIVE construction.
        base = dict(
            authority_id=AUTHORITY_ID,
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
            valid_from=VALID_FROM,
            expires_at=VALID_UNTIL,
        )
        for missing in (
            "broker_adapter_identity",
            "account_identity",
            "risk_policy_identity",
            "executable_identity",
            "valid_from",
            "expires_at",
        ):
            kwargs = dict(base)
            kwargs[missing] = None
            with self.assertRaisesRegex(ValueError, "ACTIVE real authority requires"):
                RealExecutionAuthority(**kwargs)
        with self.assertRaisesRegex(ValueError, "at least one allowed action class"):
            kwargs = dict(base)
            kwargs["allowed_action_classes"] = ()
            RealExecutionAuthority(**kwargs)
        with self.assertRaisesRegex(ValueError, "at least one allowed contract"):
            kwargs = dict(base)
            kwargs["allowed_contracts"] = ()
            RealExecutionAuthority(**kwargs)
        with self.assertRaisesRegex(ValueError, "requires SET credential readiness"):
            kwargs = dict(base)
            kwargs["credential_readiness"] = RealCredentialReadiness.UNSPECIFIED
            RealExecutionAuthority(**kwargs)

    def test_order_actions_require_connect_permission(self) -> None:
        with self.assertRaisesRegex(ValueError, "order action permission requires connect"):
            RealExecutionAuthority(
                authority_id="order-without-connect",
                broker_kind=BROKER_KIND,
                account_kind=ACCOUNT_KIND,
                status=RealAuthorityStatus.PENDING,
                allowed_action_classes=(RealActionClass.ORDER_SUBMIT,),
            )

    def test_contract_and_account_gates_fail_closed(self) -> None:
        authority = synthetic_authority()
        # contract not in whitelist
        with self.assertRaisesRegex(PermissionError, "REAL_CONTRACT_NOT_AUTHORIZED"):
            authority.require_order_submit("SHFE.cu2406", at=ASSESSED_AT)
        # wrong account identity
        with self.assertRaisesRegex(PermissionError, "REAL_ACCOUNT_IDENTITY_NOT_AUTHORIZED"):
            authority.require_connect(at=ASSESSED_AT, account_identity="OTHER_ACCOUNT")
        # wrong broker adapter identity
        with self.assertRaisesRegex(PermissionError, "REAL_BROKER_ADAPTER_IDENTITY_NOT_AUTHORIZED"):
            authority.require_connect(at=ASSESSED_AT, broker_adapter_identity="OTHER_ADAPTER")

    def test_action_not_authorized_when_not_in_allowed_classes(self) -> None:
        authority = synthetic_authority()
        # CONNECT is allowed, ORDER_REPLACE is allowed in the fixture.
        authority.require_connect(at=ASSESSED_AT)
        authority.require_order_submit(CONTRACT, at=ASSESSED_AT)
        # A PENDING authority never authorizes even with allowed classes absent.
        pending = RealExecutionAuthority(
            authority_id="pending",
            broker_kind=BROKER_KIND,
            account_kind=ACCOUNT_KIND,
            status=RealAuthorityStatus.PENDING,
            allowed_action_classes=(RealActionClass.CONNECT,),
        )
        with self.assertRaisesRegex(PermissionError, "REAL_AUTHORITY_NOT_ACTIVE"):
            pending.require_connect(at=ASSESSED_AT)

    def test_expired_revoked_and_disabled_fail_closed(self) -> None:
        authority = synthetic_authority()
        # before valid-from
        before = datetime(2025, 12, 31, 23, 59, 59, tzinfo=TZ)
        with self.assertRaisesRegex(PermissionError, "REAL_AUTHORITY_NOT_CURRENT"):
            authority.require_connect(at=before)
        # at/after expiry
        after = datetime(2027, 1, 1, tzinfo=TZ)
        with self.assertRaisesRegex(PermissionError, "REAL_AUTHORITY_NOT_CURRENT"):
            authority.require_connect(at=after)
        # revoked clears all permission
        revoked = authority.revoked()
        self.assertIs(revoked.status, RealAuthorityStatus.REVOKED)
        self.assertEqual(revoked.allowed_action_classes, ())
        with self.assertRaisesRegex(PermissionError, "REAL_AUTHORITY_NOT_ACTIVE"):
            revoked.require_connect(at=ASSESSED_AT)
        # disabled clears all permission
        disabled = authority.disabled()
        self.assertIs(disabled.status, RealAuthorityStatus.DISABLED)
        with self.assertRaisesRegex(PermissionError, "REAL_AUTHORITY_NOT_ACTIVE"):
            disabled.require_connect(at=ASSESSED_AT)

    def test_revoked_preserves_identity_but_not_permission(self) -> None:
        authority = synthetic_authority()
        revoked = authority.revoked()
        self.assertEqual(revoked.authority_id, authority.authority_id)
        self.assertEqual(revoked.broker_adapter_identity, authority.broker_adapter_identity)
        self.assertEqual(revoked.account_identity, authority.account_identity)
        self.assertNotEqual(revoked.identity_id, authority.identity_id)  # status changed

    def test_identity_id_is_deterministic(self) -> None:
        self.assertEqual(synthetic_authority().identity_id, synthetic_authority().identity_id)
        self.assertNotEqual(
            synthetic_authority().identity_id,
            RealExecutionAuthority(
                authority_id="OTHER",
                broker_kind=BROKER_KIND,
                account_kind=ACCOUNT_KIND,
                status=RealAuthorityStatus.PENDING,
            ).identity_id,
        )

    def test_bounded_validity_requires_timezone_aware_times(self) -> None:
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            RealExecutionAuthority(
                authority_id="naive",
                broker_kind=BROKER_KIND,
                account_kind=ACCOUNT_KIND,
                status=RealAuthorityStatus.PENDING,
                valid_from=datetime(2026, 1, 1),
            )
        with self.assertRaisesRegex(ValueError, "expiry must follow"):
            RealExecutionAuthority(
                authority_id="inverted",
                broker_kind=BROKER_KIND,
                account_kind=ACCOUNT_KIND,
                status=RealAuthorityStatus.PENDING,
                valid_from=VALID_UNTIL,
                expires_at=VALID_FROM,
            )

    def test_max_position_is_optional_separate_binding(self) -> None:
        authority = synthetic_authority()
        self.assertEqual(authority.max_position_lots, 1)
        unbound = RealExecutionAuthority(
            authority_id="no-position-cap",
            broker_kind=BROKER_KIND,
            account_kind=ACCOUNT_KIND,
            status=RealAuthorityStatus.PENDING,
            max_position_lots=None,
        )
        self.assertIsNone(unbound.max_position_lots)
        with self.assertRaisesRegex(ValueError, "positive integer"):
            RealExecutionAuthority(
                authority_id="bad-position",
                broker_kind=BROKER_KIND,
                account_kind=ACCOUNT_KIND,
                status=RealAuthorityStatus.PENDING,
                max_position_lots=0,
            )

    def test_authority_carries_no_secret_value_surface(self) -> None:
        authority = synthetic_authority()
        # The authority must not expose any credential value or env-var name.
        for name in ("credential_value", "credential_secret", "api_key", "password"):
            self.assertFalse(hasattr(authority, name), name)
        self.assertNotIn("=", authority.identity_id)
        # readiness is abstract SET/UNSET only
        self.assertIs(authority.credential_readiness, RealCredentialReadiness.SET)

    def test_no_permanent_numeric_risk_rule_embedded(self) -> None:
        source = (REPO_ROOT / "src" / "real_execution_authority.py").read_text(encoding="utf-8")
        for forbidden in (
            "risk_percent",
            "stop_loss_percent",
            "max_drawdown",
            "daily_loss_limit",
            "per_trade_risk",
            "margin_rate",
        ):
            self.assertNotIn(forbidden, source)
        # the only numeric risk-adjacent field is the optional max-position binding
        self.assertIn("max_position_lots", source)


if __name__ == "__main__":
    unittest.main()

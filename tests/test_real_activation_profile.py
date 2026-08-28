"""Deterministic offline tests for the REAL activation profile.

Proves the profile cannot become ACTIVE while required bindings are absent,
result-dependent policy identities stay UNBOUND/UNKNOWN (never invented), and
the identity / contract gates behave correctly.
"""

from __future__ import annotations

from pathlib import Path
import unittest

from src.real_activation_profile import (
    REQUIRED_ACTIVATION_BINDING_NAMES,
    RESULT_DEPENDENT_POLICY_NAMES,
    RealActivationProfile,
    RealActivationStatus,
)
from tests.real_synthetic_fixture import (
    ACCOUNT_IDENTITY,
    BROKER_ADAPTER_IDENTITY,
    CONTRACT,
    RISK_POLICY_IDENTITY,
    RUNTIME_LAYOUT_IDENTITY,
    synthetic_authority,
    synthetic_profile,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _profile_without(name: str) -> RealActivationProfile:
    profile = synthetic_profile()
    kwargs = {
        "profile_id": profile.profile_id,
        "status": profile.status,
        "execution_mode": profile.execution_mode,
        "execution_authority_identity": profile.execution_authority_identity,
        "broker_adapter_identity": profile.broker_adapter_identity,
        "account_identity": profile.account_identity,
        "risk_policy_identity": profile.risk_policy_identity,
        "runtime_layout_identity": profile.runtime_layout_identity,
        "allowed_contracts": profile.allowed_contracts,
    }
    kwargs[name] = None
    return RealActivationProfile(**kwargs)


class RealActivationProfileTests(unittest.TestCase):
    def test_pending_profile_requires_no_bindings(self) -> None:
        profile = RealActivationProfile(
            profile_id="pending-profile",
            status=RealActivationStatus.PENDING,
            execution_mode="REAL",
        )
        self.assertIs(profile.status, RealActivationStatus.PENDING)
        self.assertEqual(profile.allowed_contracts, ())
        self.assertIsNone(profile.execution_authority_identity)
        with self.assertRaisesRegex(PermissionError, "REAL_ACTIVATION_PROFILE_NOT_ACTIVE"):
            profile.require_active_for(CONTRACT)

    def test_active_profile_cannot_become_active_with_missing_bindings(self) -> None:
        for name in REQUIRED_ACTIVATION_BINDING_NAMES:
            if name == "allowed_contracts":
                # an empty whitelist can never activate
                with self.assertRaisesRegex(ValueError, "at least one contract"):
                    RealActivationProfile(
                        profile_id="no-contracts",
                        status=RealActivationStatus.ACTIVE,
                        execution_mode="REAL",
                        execution_authority_identity=synthetic_authority().identity_id,
                        broker_adapter_identity=BROKER_ADAPTER_IDENTITY,
                        account_identity=ACCOUNT_IDENTITY,
                        risk_policy_identity=RISK_POLICY_IDENTITY,
                        runtime_layout_identity=RUNTIME_LAYOUT_IDENTITY,
                        allowed_contracts=(),
                    )
            else:
                with self.assertRaisesRegex(ValueError, "requires every required activation binding"):
                    _profile_without(name)

    def test_active_profile_requires_real_mode(self) -> None:
        with self.assertRaisesRegex(ValueError, "execution_mode must be REAL"):
            RealActivationProfile(
                profile_id="bad-mode",
                status=RealActivationStatus.PENDING,
                execution_mode="PAPER",
            )

    def test_fully_populated_synthetic_profile_is_active(self) -> None:
        profile = synthetic_profile()
        self.assertIs(profile.status, RealActivationStatus.ACTIVE)
        for name in REQUIRED_ACTIVATION_BINDING_NAMES:
            if name == "allowed_contracts":
                self.assertTrue(profile.allowed_contracts)
            else:
                self.assertIsNotNone(getattr(profile, name))
        # result-dependent policies are all bound in the fully populated fixture
        self.assertEqual(profile.unbound_result_dependent_bindings(), ())

    def test_result_dependent_policies_default_to_unbound_unknown(self) -> None:
        authority = synthetic_authority()
        profile = RealActivationProfile(
            profile_id="unbound-policies-profile",
            status=RealActivationStatus.ACTIVE,
            execution_mode="REAL",
            execution_authority_identity=authority.identity_id,
            broker_adapter_identity=BROKER_ADAPTER_IDENTITY,
            account_identity=ACCOUNT_IDENTITY,
            risk_policy_identity=RISK_POLICY_IDENTITY,
            runtime_layout_identity=RUNTIME_LAYOUT_IDENTITY,
            allowed_contracts=(CONTRACT,),
        )
        # ACTIVE succeeds without result-dependent policies; they are UNBOUND.
        unbound = profile.unbound_result_dependent_bindings()
        self.assertEqual(set(unbound), set(RESULT_DEPENDENT_POLICY_NAMES))
        for name in RESULT_DEPENDENT_POLICY_NAMES:
            self.assertIsNone(getattr(profile, name))

    def test_identity_id_is_deterministic(self) -> None:
        self.assertEqual(synthetic_profile().identity_id, synthetic_profile().identity_id)
        different = RealActivationProfile(
            profile_id="OTHER",
            status=RealActivationStatus.PENDING,
            execution_mode="REAL",
        )
        self.assertNotEqual(synthetic_profile().identity_id, different.identity_id)

    def test_require_active_for_enforces_whitelist(self) -> None:
        profile = synthetic_profile()
        profile.require_active_for(CONTRACT)
        with self.assertRaisesRegex(PermissionError, "REAL_ACTIVATION_CONTRACT_NOT_ALLOWED"):
            profile.require_active_for("SHFE.cu2406")

    def test_contracts_must_be_canonical_and_unique(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-empty canonical"):
            RealActivationProfile(
                profile_id="bad-contract",
                status=RealActivationStatus.PENDING,
                execution_mode="REAL",
                allowed_contracts=("  SHFE.rb9999  ",),
            )
        with self.assertRaisesRegex(ValueError, "must be unique"):
            RealActivationProfile(
                profile_id="dup-contract",
                status=RealActivationStatus.PENDING,
                execution_mode="REAL",
                allowed_contracts=(CONTRACT, CONTRACT),
            )

    def test_no_permanent_numeric_risk_rule_embedded(self) -> None:
        source = (REPO_ROOT / "src" / "real_activation_profile.py").read_text(encoding="utf-8")
        for forbidden in (
            "risk_percent",
            "stop_loss_percent",
            "max_drawdown",
            "daily_loss_limit",
            "per_trade_risk",
            "margin_rate",
        ):
            self.assertNotIn(forbidden, source)
        # risk is referenced by identity only, never a number
        self.assertIn("risk_policy_identity", source)


if __name__ == "__main__":
    unittest.main()

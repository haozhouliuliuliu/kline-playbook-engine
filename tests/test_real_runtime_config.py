"""Deterministic offline tests for the REAL runtime config surface.

Proves result-dependent values stay UNBOUND/UNKNOWN (never guessed defaults),
the execution mode is fixed REAL, bindings are explicit, and external
activation fails closed until an ACTIVE profile/authority is bound.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.real_runtime_config import (
    RESULT_DEPENDENT_BINDING_NAMES,
    RealRuntimeConfig,
)
from src.real_activation_profile import RealActivationProfile, RealActivationStatus
from src.real_execution_authority import RealAuthorityStatus
from tests.real_synthetic_fixture import (
    ACCOUNT_IDENTITY,
    BROKER_ADAPTER_IDENTITY,
    CONFIG_ID,
    CONTRACT,
    EXCHANGE,
    PRODUCT,
    RISK_POLICY_IDENTITY,
    RUNTIME_LAYOUT_IDENTITY,
    TRADER_IDENTITY,
    BROKER_KIND,
    ACCOUNT_KIND,
    synthetic_authority,
    synthetic_profile,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def _bare_config(state_root: Path) -> RealRuntimeConfig:
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


class RealRuntimeConfigTests(unittest.TestCase):
    def test_execution_mode_is_fixed_real(self) -> None:
        with TemporaryDirectory() as tmp:
            config = _bare_config(Path(tmp))
            self.assertEqual(config.execution_mode, "REAL")
        with self.assertRaisesRegex(ValueError, "execution_mode must be REAL"):
            RealRuntimeConfig(
                config_id=CONFIG_ID,
                state_root=".",
                trader_identity=TRADER_IDENTITY,
                concrete_contract_id=CONTRACT,
                product=PRODUCT,
                exchange=EXCHANGE,
                broker_kind=BROKER_KIND,
                account_kind=ACCOUNT_KIND,
                execution_mode="PAPER",
            )

    def test_result_dependent_values_are_unbound_by_default(self) -> None:
        with TemporaryDirectory() as tmp:
            config = _bare_config(Path(tmp))
            self.assertEqual(
                set(config.unbound_result_dependent_bindings()),
                set(RESULT_DEPENDENT_BINDING_NAMES),
            )
            blockers = config.external_activation_blockers()
            self.assertIn("REAL_ACTIVATION_PROFILE_UNBOUND", blockers)
            self.assertIn("REAL_CONNECT_AUTHORITY_UNBOUND", blockers)

    def test_bindings_are_explicit_not_guessed(self) -> None:
        with TemporaryDirectory() as tmp:
            authority = synthetic_authority()
            profile = synthetic_profile(authority)
            config = _bare_config(Path(tmp)).bind_activation_profile(profile).bind_authority(authority)
            self.assertIs(config.activation_profile, profile)
            self.assertIs(config.authority, authority)
            self.assertEqual(config.unbound_result_dependent_bindings(), ())

    def test_contract_exchange_product_consistency(self) -> None:
        with self.assertRaisesRegex(ValueError, "exchange disagrees"):
            RealRuntimeConfig(
                config_id=CONFIG_ID,
                state_root=".",
                trader_identity=TRADER_IDENTITY,
                concrete_contract_id=CONTRACT,
                product=PRODUCT,
                exchange="DCE",
                broker_kind=BROKER_KIND,
                account_kind=ACCOUNT_KIND,
            )
        with self.assertRaisesRegex(ValueError, "disagrees with config product"):
            RealRuntimeConfig(
                config_id=CONFIG_ID,
                state_root=".",
                trader_identity=TRADER_IDENTITY,
                concrete_contract_id=CONTRACT,
                product="cu",
                exchange=EXCHANGE,
                broker_kind=BROKER_KIND,
                account_kind=ACCOUNT_KIND,
            )
        with self.assertRaisesRegex(ValueError, "exchange prefix"):
            RealRuntimeConfig(
                config_id=CONFIG_ID,
                state_root=".",
                trader_identity=TRADER_IDENTITY,
                concrete_contract_id="rb9999",
                product=PRODUCT,
                exchange=EXCHANGE,
                broker_kind=BROKER_KIND,
                account_kind=ACCOUNT_KIND,
            )

    def test_identity_and_stable_identity_are_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            one = _bare_config(Path(tmp))
            two = _bare_config(Path(tmp))
            self.assertEqual(one.identity, two.identity)
            self.assertEqual(one.stable_identity, two.stable_identity)
            self.assertEqual(one.stable_identity, two.stable_identity)
            # binding authority/profile changes the volatile identity, not the stable one
            authority = synthetic_authority()
            profile = synthetic_profile(authority)
            bound = one.bind_activation_profile(profile).bind_authority(authority)
            self.assertNotEqual(one.identity, bound.identity)
            self.assertEqual(one.stable_identity, bound.stable_identity)

    def test_external_activation_blockers_include_unbound_policies(self) -> None:
        with TemporaryDirectory() as tmp:
            authority = synthetic_authority()
            profile = RealActivationProfile(
                profile_id="UNBOUND_RESULT_PROFILE",
                status=RealActivationStatus.ACTIVE,
                execution_mode="REAL",
                execution_authority_identity=authority.identity_id,
                broker_adapter_identity=BROKER_ADAPTER_IDENTITY,
                account_identity=ACCOUNT_IDENTITY,
                risk_policy_identity=RISK_POLICY_IDENTITY,
                runtime_layout_identity=RUNTIME_LAYOUT_IDENTITY,
                allowed_contracts=(CONTRACT,),
            )
            config = _bare_config(Path(tmp)).bind_activation_profile(profile).bind_authority(authority)
            blockers = config.external_activation_blockers()
            self.assertTrue(any("RESULT_DEPENDENT_BINDINGS_UNBOUND" in blocker for blocker in blockers))

    def test_authority_status_must_be_active_for_external_activation(self) -> None:
        with TemporaryDirectory() as tmp:
            profile = synthetic_profile()
            from src.real_execution_authority import RealExecutionAuthority

            pending = RealExecutionAuthority(
                authority_id="pending-authority",
                broker_kind=BROKER_KIND,
                account_kind=ACCOUNT_KIND,
                status=RealAuthorityStatus.PENDING,
                execution_mode="REAL",
            )
            config = (
                _bare_config(Path(tmp))
                .bind_activation_profile(profile)
                .bind_authority(pending)
            )
            blockers = config.external_activation_blockers()
            self.assertIn("REAL_CONNECT_AUTHORITY_NOT_ACTIVE", blockers)

    def test_no_invented_credential_or_endpoint_values(self) -> None:
        source = (REPO_ROOT / "src" / "real_runtime_config.py").read_text(encoding="utf-8")
        for forbidden in (
            "FANGZHENG",
            "FUT_OPEND",
            "CTP_USER",
            "API_KEY",
            "broker_endpoint",
            "broker_addr",
            "https://",
        ):
            self.assertNotIn(forbidden, source)
        # result-dependent policies are explicitly reported as unbound
        self.assertIn("RESULT_DEPENDENT_BINDING_NAMES", source)
        self.assertIn("UNBOUND", source)


if __name__ == "__main__":
    unittest.main()

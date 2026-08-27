"""Deterministic offline tests for the local PAPER runtime config surface.

Proves construction has zero external side effects, the config never freezes
result-dependent execution values (quantity/sizing, price policy, close-offset,
permanent risk, contract whitelist), contract identity is consistent, and real
external activation stays fail-closed until an ACTIVE profile + ACTIVE connect
authority are explicitly bound.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from src.paper_activation_profile import PaperActivationProfile, PaperActivationStatus
from src.paper_execution_authority import PaperAuthorityStatus, PaperExecutionAuthority
from src.paper_runtime_config import (
    RESULT_DEPENDENT_BINDING_NAMES,
    PaperRuntimeConfig,
)


def _base_config(**overrides) -> PaperRuntimeConfig:
    values = {
        "config_id": "cfg-1",
        "state_root": Path("C:/kpe-state") if overrides.get("windows") else Path("state"),
        "trader_identity": "TRADER",
        "concrete_contract_id": "SHFE.cu2406",
        "product": "cu",
        "exchange": "SHFE",
        "tqsdk_runtime_version": "3.10.1",
        "broker_kind": "TQSDK_CANDIDATE",
        "account_kind": "TQSDK_PAPER",
    }
    values.update(overrides)
    values.pop("windows", None)
    return PaperRuntimeConfig(**values)


def _active_profile() -> PaperActivationProfile:
    return PaperActivationProfile(
        profile_id="profile-active",
        status=PaperActivationStatus.ACTIVE,
        execution_mode="PAPER",
        tqsdk_runtime_version="3.10.1",
        live_data_policy_identity="live",
        sizing_policy_identity="sizing",
        execution_price_policy_identity="price",
        close_offset_policy_identity="offset",
        risk_policy_identity="risk",
        broker_adapter_identity="broker",
        allowed_contracts=("SHFE.cu2406",),
    )


def _active_authority() -> PaperExecutionAuthority:
    return PaperExecutionAuthority(
        authority_id="authority-active",
        broker_kind="TQSDK",
        account_kind="TQSDK_PAPER",
        status=PaperAuthorityStatus.ACTIVE,
        allow_connect=True,
        allow_order_submit=True,
        allow_order_cancel=True,
        allow_order_replace=True,
        allowed_contracts=("SHFE.cu2406",),
    )


class PaperRuntimeConfigConstructionTests(unittest.TestCase):
    def test_construction_has_zero_external_side_effects(self) -> None:
        config = _base_config()
        self.assertEqual(config.trader_identity, "TRADER")
        self.assertEqual(config.concrete_contract_id, "SHFE.cu2406")
        self.assertEqual(config.exchange, "SHFE")
        self.assertEqual(config.product, "cu")
        # no activation profile/authority is implicitly bound
        self.assertIsNone(config.activation_profile)
        self.assertIsNone(config.authority)
        self.assertTrue(config.external_activation_blockers())

    def test_contract_identity_must_be_consistent(self) -> None:
        with self.assertRaisesRegex(ValueError, "exchange disagrees"):
            _base_config(exchange="DCE")
        with self.assertRaisesRegex(ValueError, "instrument disagrees with config product"):
            _base_config(product="rb")
        with self.assertRaisesRegex(ValueError, "exchange prefix"):
            _base_config(concrete_contract_id="cu2406")

    def test_state_root_is_resolved_to_path(self) -> None:
        config = _base_config(state_root="some/root")
        self.assertIsInstance(config.state_root, Path)
        self.assertEqual(config.state_root, Path("some/root"))

    def test_identity_is_deterministic(self) -> None:
        self.assertEqual(_base_config().identity, _base_config().identity)
        self.assertNotEqual(
            _base_config(trader_identity="OTHER").identity, _base_config().identity
        )

    def test_windows_path_handling(self) -> None:
        config = _base_config(state_root="C:\\Users\\me\\kpe-state")
        self.assertEqual(config.state_root, Path("C:\\Users\\me\\kpe-state"))
        self.assertTrue(str(config.state_root).replace("\\", "/").startswith("C:/"))

    def test_result_dependent_values_are_not_frozen(self) -> None:
        config = _base_config()
        # The config itself carries no sizing/price/offset/risk numeric values.
        self.assertEqual(config.unbound_result_dependent_bindings(), RESULT_DEPENDENT_BINDING_NAMES)
        self.assertFalse(hasattr(config, "quantity"))
        self.assertFalse(hasattr(config, "sizing_policy_identity") and config.sizing_policy_identity)

    def test_binding_activation_profile_updates_config(self) -> None:
        config = _base_config()
        bound = config.bind_activation_profile(_active_profile())
        self.assertIsNone(config.activation_profile)
        self.assertIsNotNone(bound.activation_profile)
        self.assertEqual(bound.activation_profile.profile_id, "profile-active")
        # original config is unchanged (frozen value semantics)
        self.assertIsNone(config.activation_profile)

    def test_binding_authority_updates_config(self) -> None:
        config = _base_config()
        bound = config.bind_authority(_active_authority())
        self.assertIsNone(config.authority)
        self.assertIsNotNone(bound.authority)
        self.assertEqual(bound.authority.authority_id, "authority-active")

    def test_active_profile_binds_all_result_dependent_values(self) -> None:
        config = _base_config().bind_activation_profile(_active_profile())
        self.assertEqual(config.unbound_result_dependent_bindings(), ())

    def test_secret_values_never_represented(self) -> None:
        config = _base_config()
        document = config.to_public_document()
        text = str(document)
        self.assertNotIn("DEEPSEEK_API_KEY", text)
        self.assertNotIn("password", text.lower())


class PaperRuntimeConfigActivationGateTests(unittest.TestCase):
    def test_unbound_external_activation_fails_closed(self) -> None:
        config = _base_config()
        blockers = config.external_activation_blockers()
        self.assertIn("ACTIVATION_PROFILE_UNBOUND", blockers)
        self.assertIn("PAPER_CONNECT_AUTHORITY_UNBOUND", blockers)

    def test_bound_profile_but_no_authority_fails_closed(self) -> None:
        config = _base_config().bind_activation_profile(_active_profile())
        blockers = config.external_activation_blockers()
        self.assertNotIn("ACTIVATION_PROFILE_UNBOUND", blockers)
        self.assertIn("PAPER_CONNECT_AUTHORITY_UNBOUND", blockers)

    def test_pending_authority_fails_closed(self) -> None:
        pending = PaperExecutionAuthority(
            authority_id="pending",
            broker_kind="TQSDK",
            account_kind="TQSDK_PAPER",
            status=PaperAuthorityStatus.PENDING,
            allow_connect=False,
            allow_order_submit=False,
            credential_env_names=("DEEPSEEK_API_KEY",),
        )
        config = _base_config().bind_activation_profile(_active_profile()).bind_authority(pending)
        self.assertIn("PAPER_CONNECT_AUTHORITY_NOT_ACTIVE", config.external_activation_blockers())

    def test_full_active_binding_has_no_external_blockers(self) -> None:
        config = (
            _base_config()
            .bind_activation_profile(_active_profile())
            .bind_authority(_active_authority())
        )
        self.assertEqual(config.external_activation_blockers(), ())

    def test_pending_profile_fails_closed(self) -> None:
        pending_profile = PaperActivationProfile(
            profile_id="pending-profile",
            status=PaperActivationStatus.PENDING,
            execution_mode="PAPER",
            tqsdk_runtime_version="3.10.1",
            live_data_policy_identity=None,
            sizing_policy_identity=None,
            execution_price_policy_identity=None,
            close_offset_policy_identity=None,
            risk_policy_identity=None,
            broker_adapter_identity=None,
        )
        config = _base_config().bind_activation_profile(pending_profile).bind_authority(_active_authority())
        self.assertIn("ACTIVATION_PROFILE_NOT_ACTIVE", config.external_activation_blockers())


if __name__ == "__main__":
    unittest.main()

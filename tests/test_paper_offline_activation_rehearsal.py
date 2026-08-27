"""Deterministic offline test for the full fake PAPER activation rehearsal.

Proves the strongest feature-completion path before final audit:

    configuration -> persistence open -> assembly -> preflight -> fake connect
    -> broker truth -> market bootstrap -> trader ready -> new live 1m
    -> governed wake/context -> fake cognition -> fake risk/order plan
    -> journal -> fake broker -> reconciliation -> clean shutdown -> restart
    -> reopen durable state -> no duplicate old wake/order.

All actors are deterministic fakes; no real account/order/provider action.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.paper_offline_activation_rehearsal import (
    CONTRACT,
    EXCHANGE,
    INSTRUMENT,
    PRODUCT,
    RUNTIME_VERSION,
    TRADER_IDENTITY,
    rehearsal_authority,
    rehearsal_profile,
    run_offline_activation_rehearsal,
)
from src.paper_runtime_config import PaperRuntimeConfig


class PaperOfflineActivationRehearsalTests(unittest.TestCase):
    def test_full_offline_activation_rehearsal_passes(self) -> None:
        with TemporaryDirectory() as tmp:
            result = run_offline_activation_rehearsal(state_root=Path(tmp))
            self.assertTrue(result.passed, result.public_lines())
            self.assertGreaterEqual(result.wake_count_after_restart, 1)
            self.assertGreaterEqual(result.order_count_after_restart, 1)
            step_names = {step for step, _ in result.steps}
            for expected in (
                "CONFIGURATION",
                "PERSISTENCE_OPEN",
                "ASSEMBLY",
                "PREFLIGHT",
                "FAKE_CONNECT",
                "MARKET_BOOTSTRAP",
                "TRADER_READY",
                "NEW_LIVE_1M_WAKE",
                "JOURNAL_WAKE",
                "JOURNAL_ORDER",
                "RECONCILIATION",
                "CLEAN_SHUTDOWN",
                "RESTART_REOPEN_LAYOUT",
                "RESTORE_CHECKPOINT",
                "RESTART_REOPEN_JOURNALS",
                "RESTART_ASSEMBLY",
                "NO_DUPLICATE_WAKE_ORDER",
                "RESTART_PRESERVES_STATE",
                "RESTART_SHUTDOWN",
            ):
                self.assertIn(expected, step_names)
            for step, status in result.steps:
                self.assertEqual(status, "PASS", f"{step} was not PASS")

    def test_rehearsal_is_deterministic(self) -> None:
        with TemporaryDirectory() as tmp_a, TemporaryDirectory() as tmp_b:
            first = run_offline_activation_rehearsal(state_root=Path(tmp_a))
            second = run_offline_activation_rehearsal(state_root=Path(tmp_b))
            self.assertTrue(first.passed)
            self.assertTrue(second.passed)
            self.assertEqual(first.public_lines(), second.public_lines())

    def test_rehearsal_accepts_explicit_config(self) -> None:
        with TemporaryDirectory() as tmp:
            config = (
                PaperRuntimeConfig(
                    config_id="REHEARSAL_CONFIG",
                    state_root=Path(tmp),
                    trader_identity=TRADER_IDENTITY,
                    concrete_contract_id=CONTRACT,
                    product=PRODUCT,
                    exchange=EXCHANGE,
                    tqsdk_runtime_version=RUNTIME_VERSION,
                    broker_kind="TQSDK_CANDIDATE",
                    account_kind="TQSDK_PAPER",
                    symbol=INSTRUMENT,
                )
                .bind_activation_profile(rehearsal_profile())
                .bind_authority(rehearsal_authority())
            )
            result = run_offline_activation_rehearsal(state_root=config.state_root, config=config)
            self.assertTrue(result.passed, result.public_lines())
            self.assertTrue(result.identity)

    def test_rehearsal_restart_does_not_duplicate_wake_or_order(self) -> None:
        with TemporaryDirectory() as tmp:
            result = run_offline_activation_rehearsal(state_root=Path(tmp))
            checks = "\n".join(result.checks)
            self.assertIn("RESTART_WAKE_RESULTS=0", checks)
            self.assertIn("RESTART_TRADER_CALLS=0", checks)
            self.assertIn("RESTART_BROKER_SUBMITS=0", checks)
            self.assertIn("WAKE_COUNT_BEFORE=1", checks)
            self.assertIn("WAKE_COUNT_AFTER=1", checks)
            self.assertIn("ORDER_COUNT_BEFORE=1", checks)
            self.assertIn("ORDER_COUNT_AFTER=1", checks)


if __name__ == "__main__":
    unittest.main()

"""Deterministic offline tests for the PAPER runtime-state layout.

Proves the deterministic path layout under an explicit state root, safe first
startup initialization, restart reopening existing durable state (never wiping
it), fail-closed identity mismatch on unsafe reopen, deterministic identity, and
Windows-compatible path handling.
"""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.paper_runtime_layout import (
    PAPER_RUNTIME_LAYOUT_SCHEMA_VERSION,
    PaperRuntimeIdentityMismatch,
    PaperRuntimeLayout,
    PaperRuntimeLayoutError,
)


def _layout(state_root: Path, *, trader="TRADER", contract="SHFE.cu2406", config_id="cfg-1"):
    return PaperRuntimeLayout(
        state_root=state_root,
        trader_identity=trader,
        concrete_contract_id=contract,
        config_identity=config_id,
    )


class PaperRuntimeLayoutTests(unittest.TestCase):
    def test_paths_are_deterministic(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            one = _layout(root)
            two = _layout(root)
            self.assertEqual(one.order_journal_path, root / "journals" / "paper_order_journal.sqlite3")
            self.assertEqual(one.wake_journal_path, root / "journals" / "paper_wake_journal.sqlite3")
            self.assertEqual(one.trader_store_path, root / "trader" / "trader_store.sqlite3")
            self.assertEqual(one.runtime_metadata_path, root / "runtime" / "runtime_metadata.json")
            self.assertEqual(one.causal_checkpoint_path, root / "runtime" / "causal_checkpoint.json")
            self.assertEqual(one.identity, two.identity)
            self.assertEqual(one.order_journal_path, two.order_journal_path)

    def test_identity_is_stable_and_sensitive_to_bindings(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            base = _layout(root)
            other_trader = _layout(root, trader="OTHER")
            other_contract = _layout(root, contract="SHFE.rb2406")
            self.assertEqual(base.identity, _layout(root).identity)
            self.assertNotEqual(base.identity, other_trader.identity)
            self.assertNotEqual(base.identity, other_contract.identity)

    def test_first_startup_initializes_safely(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "state"
            layout = _layout(root)
            self.assertFalse(root.exists())
            layout.ensure_initialized()
            self.assertTrue(root.exists())
            self.assertTrue(layout.runtime_metadata_path.exists())
            self.assertEqual(layout.runtime_metadata_path.parent.name, "runtime")
            # idempotent
            layout.ensure_initialized()

    def test_restart_reopens_existing_durable_state(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            layout = _layout(root)
            layout.ensure_initialized()
            # reopen with the identical identity must succeed
            layout.reopen()
            self.assertTrue(layout.runtime_metadata_path.exists())

    def test_identity_mismatch_fails_closed_on_reopen(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = _layout(root)
            original.ensure_initialized()
            # a different trader identity must NOT be able to silently reopen
            imposter = _layout(root, trader="IMPOSTER")
            with self.assertRaisesRegex(PaperRuntimeIdentityMismatch, "IDENTITY_MISMATCH"):
                imposter.reopen()
            # different contract also fails closed
            other_contract = _layout(root, contract="SHFE.rb2406")
            with self.assertRaisesRegex(PaperRuntimeIdentityMismatch, "IDENTITY_MISMATCH"):
                other_contract.reopen()

    def test_durable_state_without_metadata_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            # simulate a tree with durable state but no metadata marker
            (root / "journals").mkdir(parents=True)
            (root / "journals" / "paper_order_journal.sqlite3").write_bytes(b"sqlite")
            layout = _layout(root)
            with self.assertRaisesRegex(PaperRuntimeIdentityMismatch, "WITHOUT_METADATA"):
                layout.ensure_initialized()

    def test_missing_metadata_reopen_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "runtime").mkdir(parents=True)
            layout = _layout(root)
            with self.assertRaisesRegex(PaperRuntimeIdentityMismatch, "METADATA_MISSING"):
                layout.reopen()

    def test_never_overwrites_evidence_or_metadata(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            layout = _layout(root)
            layout.ensure_initialized()
            original_text = layout.runtime_metadata_path.read_text(encoding="utf-8")
            # re-initialize must not overwrite the existing marker
            layout.ensure_initialized()
            self.assertEqual(layout.runtime_metadata_path.read_text(encoding="utf-8"), original_text)

    def test_windows_compatible_paths(self) -> None:
        with TemporaryDirectory() as tmp:
            if os.name == "nt":
                root = Path("C:\\kpe\\state")
                layout = _layout(root)
                self.assertEqual(layout.order_journal_path, Path("C:\\kpe\\state\\journals\\paper_order_journal.sqlite3"))
            else:
                root = Path(tmp)
                layout = _layout(root)
                self.assertEqual(layout.order_journal_path.parent.name, "journals")

    def test_checkpoint_roundtrip(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            layout = _layout(root)
            layout.ensure_initialized()
            payload = {"schema_version": "test", "value": 42}
            layout.write_causal_checkpoint(payload)
            restored = layout.read_causal_checkpoint()
            self.assertEqual(restored, payload)

    def test_missing_checkpoint_fails_closed(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            layout = _layout(root)
            layout.ensure_initialized()
            with self.assertRaisesRegex(PaperRuntimeLayoutError, "CHECKPOINT_MISSING"):
                layout.read_causal_checkpoint()

    def test_layout_schema_version_constant(self) -> None:
        self.assertEqual(PAPER_RUNTIME_LAYOUT_SCHEMA_VERSION, "KPE_PAPER_RUNTIME_LAYOUT_V0_1")


if __name__ == "__main__":
    unittest.main()

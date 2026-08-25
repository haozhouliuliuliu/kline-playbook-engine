from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from src.persistent_hypothesis_history import VersionedHypothesisLedger
from src.persistent_trader_store import PersistentTraderStore


class VersionedHypothesisLedgerTests(unittest.TestCase):
    def _store(self, root: Path) -> tuple[Path, PersistentTraderStore]:
        path = root / "trader.sqlite3"
        return path, PersistentTraderStore(path, trader_identity="trader-1")

    def test_revision_history_preserves_exact_before_after_and_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path, store = self._store(Path(temp))
            ledger = VersionedHypothesisLedger(path, trader_identity="trader-1")
            t0 = datetime(2026, 1, 1, 1, 0, tzinfo=timezone.utc)
            first, r1 = ledger.put(
                hypothesis_id="h-1",
                occurred_at=t0,
                statement="first statement",
                falsifier="first falsifier",
                evidence_references=("source-b", "source-a"),
                observation_identity="obs-1",
                request_id="req-1",
                reason="create from current market evidence",
            )
            self.assertIsNone(r1.before_state)
            self.assertEqual(r1.revision_number, 1)
            self.assertEqual(r1.after_state["statement"], "first statement")
            self.assertEqual(r1.after_state["evidence_references"], ("source-a", "source-b"))
            self.assertEqual(r1.observation_identity, "obs-1")
            self.assertEqual(r1.request_id, "req-1")
            self.assertFalse(first.executable_policy)

            t1 = t0 + timedelta(minutes=5)
            second, r2 = ledger.put(
                hypothesis_id="h-1",
                occurred_at=t1,
                statement="revised statement",
                falsifier="revised falsifier",
                status="FALSIFIED",
                evidence_references=("source-c",),
                observation_identity="obs-2",
                request_id="req-2",
                reason="new causal evidence falsified the original form",
            )
            self.assertEqual(r2.revision_number, 2)
            self.assertEqual(r2.before_state, r1.after_state)
            self.assertEqual(r2.after_state["statement"], "revised statement")
            self.assertEqual(r2.after_state["status"], "FALSIFIED")
            self.assertEqual(r2.after_state["created_at"], r1.after_state["created_at"])
            self.assertNotEqual(r2.before_sha256, r2.after_sha256)
            self.assertNotEqual(first.identity, second.identity)

            current = {item.hypothesis_id: item for item in store.list_hypotheses(limit=None)}["h-1"]
            self.assertEqual(current.statement, "revised statement")
            self.assertEqual(current.status, "FALSIFIED")
            store.close()

            reopened = PersistentTraderStore(path, trader_identity="trader-1")
            try:
                revisions = ledger.list_revisions(hypothesis_id="h-1")
                self.assertEqual([item.revision_number for item in revisions], [1, 2])
                self.assertEqual(revisions[1].before_state, revisions[0].after_state)
                exported = ledger.portable_export()
                self.assertEqual(len(exported), 2)
                self.assertEqual(exported[0]["after_state"]["statement"], "first statement")
                self.assertEqual(exported[1]["before_state"]["statement"], "first statement")
                self.assertEqual(exported[1]["after_state"]["statement"], "revised statement")
                self.assertEqual(
                    reopened.list_hypotheses(limit=None)[0].identity,
                    exported[1]["after_state"]["identity"],
                )
            finally:
                reopened.close()

    def test_policy_self_promotion_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path, store = self._store(Path(temp))
            try:
                ledger = VersionedHypothesisLedger(path, trader_identity="trader-1")
                with self.assertRaises(ValueError):
                    ledger.put(
                        hypothesis_id="h-1",
                        occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                        statement="candidate",
                        falsifier="counterexample",
                        status="VALIDATED_POLICY",
                        reason="forbidden promotion",
                    )
                self.assertEqual(ledger.list_revisions(), ())
                self.assertEqual(store.list_hypotheses(limit=None), ())
            finally:
                store.close()

    def test_revision_requires_explicit_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path, store = self._store(Path(temp))
            try:
                ledger = VersionedHypothesisLedger(path, trader_identity="trader-1")
                with self.assertRaises(ValueError):
                    ledger.put(
                        hypothesis_id="h-1",
                        occurred_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
                        statement="candidate",
                        falsifier="counterexample",
                        reason="",
                    )
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()

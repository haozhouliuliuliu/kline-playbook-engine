from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from src.persistent_trader_store import PersistentTraderStore


class PersistentTraderPortabilityRegressionTests(unittest.TestCase):
    def test_portable_export_includes_records_beyond_bounded_context_limits(self) -> None:
        with tempfile.TemporaryDirectory() as root:
            store = PersistentTraderStore(
                Path(root) / "trader.sqlite3",
                trader_identity="portable-trader-v0-1",
            )
            try:
                base = datetime(2026, 1, 1, tzinfo=timezone.utc)
                for index in range(101):
                    store.append_journal(
                        entry_id=f"journal-{index:03d}",
                        created_at=base + timedelta(seconds=index),
                        body=f"reflection-{index}",
                    )
                for index in range(201):
                    timestamp = base + timedelta(minutes=index)
                    store.put_hypothesis(
                        hypothesis_id=f"hypothesis-{index:03d}",
                        created_at=timestamp,
                        updated_at=timestamp,
                        statement=f"candidate-{index}",
                        falsifier=f"counterexample-{index}",
                    )

                # Context retrieval remains bounded for normal calls.
                self.assertEqual(len(store.list_journal(limit=100)), 100)
                self.assertEqual(len(store.list_hypotheses(limit=200)), 200)

                # Migration/export is different: it must be complete, never silently capped.
                exported = store.portable_export()
                self.assertEqual(len(exported["journal"]), 101)
                self.assertEqual(len(exported["hypotheses"]), 201)
                self.assertEqual(exported["journal"][0]["entry_id"], "journal-000")
                self.assertEqual(exported["journal"][-1]["entry_id"], "journal-100")
                self.assertEqual(exported["hypotheses"][0]["hypothesis_id"], "hypothesis-000")
                self.assertEqual(exported["hypotheses"][-1]["hypothesis_id"], "hypothesis-200")
                self.assertFalse(exported["harness_opaque_state_included"])
            finally:
                store.close()


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from src.jianghe_trading_only_prompt import TRADING_ONLY_PROMPT_CONTRACT
from src.persistent_trader_store import PersistentTraderStore
from src.replay_v0_1_runtime import ReplayV01Runtime


@dataclass
class _Contract:
    system_prompt_sha256: str
    decision_prompt_sha256: str
    provider_call_authorized: bool = False


@dataclass
class _TraderIdentity:
    identity: str = "trader-1"


class _Tools:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object], str | None, str | None]] = []

    def call(self, name, arguments, *, observation_identity=None, request_id=None):
        self.calls.append((name, dict(arguments), observation_identity, request_id))
        return {"ok": True}


class _BaseRuntime:
    def __init__(self, root: Path) -> None:
        self.runtime_contract = _Contract(
            TRADING_ONLY_PROMPT_CONTRACT.system_prompt_sha256,
            TRADING_ONLY_PROMPT_CONTRACT.decision_prompt_sha256,
        )
        self.trader_identity = _TraderIdentity()
        self.store = PersistentTraderStore(root / "state.sqlite3", trader_identity=self.trader_identity.identity)
        self.tools = _Tools()
        self.prepared: dict[str, object] | None = None
        self._clock = datetime(2026, 1, 2, 1, 0, tzinfo=timezone.utc)

    def clock(self):
        return self._clock

    def prepare_model_request(self, **kwargs):
        self.prepared = dict(kwargs)
        return kwargs

    def record_model_response(self, **kwargs):
        return kwargs

    def mutate_working_memory(self, **kwargs):
        self.mutation = kwargs

    def append_journal(self, *, entry_id, body, observation_identity=None, tags=()):
        entry = self.store.append_journal(
            entry_id=entry_id,
            created_at=self._clock,
            body=body,
            observation_identity=observation_identity,
            tags=tags,
        )
        return entry.identity

    def portable_export(self):
        return self.store.portable_export()


class ReplayV01RuntimeTests(unittest.TestCase):
    def test_prepare_request_forces_frozen_prompt_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = _BaseRuntime(Path(temp))
            try:
                runtime = ReplayV01Runtime(base)
                runtime.prepare_model_request(observation=object(), retrieval_query="key zone")
                self.assertEqual(base.prepared["system_prompt"], TRADING_ONLY_PROMPT_CONTRACT.system_prompt)
                self.assertEqual(base.prepared["decision_prompt"], TRADING_ONLY_PROMPT_CONTRACT.decision_prompt)
                self.assertEqual(base.prepared["retrieval_query"], "key zone")
            finally:
                base.store.close()

    def test_mismatched_prompt_contract_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = _BaseRuntime(Path(temp))
            try:
                base.runtime_contract.system_prompt_sha256 = "0" * 64
                with self.assertRaises(ValueError):
                    ReplayV01Runtime(base)
            finally:
                base.store.close()

    def test_hypothesis_revision_is_versioned_and_audited(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = _BaseRuntime(Path(temp))
            try:
                runtime = ReplayV01Runtime(base)
                first_revision = runtime.put_hypothesis(
                    hypothesis_id="h-1",
                    statement="candidate one",
                    falsifier="break below zone",
                    reason="current causal setup",
                    observation_identity="obs-1",
                    request_id="req-1",
                )
                base._clock = datetime(2026, 1, 2, 1, 5, tzinfo=timezone.utc)
                second_revision = runtime.put_hypothesis(
                    hypothesis_id="h-1",
                    statement="candidate revised",
                    falsifier="already falsified",
                    status="FALSIFIED",
                    reason="new closed 5m evidence",
                    observation_identity="obs-2",
                    request_id="req-2",
                )
                self.assertNotEqual(first_revision, second_revision)
                revisions = runtime.hypothesis_ledger.list_revisions(hypothesis_id="h-1")
                self.assertEqual(len(revisions), 2)
                self.assertEqual(revisions[1].before_state, revisions[0].after_state)
                audit = [event for event in base.store.list_audit() if event.event_kind == "DS_HYPOTHESIS_MEMORY_REVISION"]
                self.assertEqual(len(audit), 2)
                self.assertEqual(audit[1].request_id, "req-2")
                exported = runtime.portable_export()
                self.assertEqual(len(exported["hypothesis_revisions"]), 2)
                self.assertEqual(exported["model_cognitive_scope"], "TRADING_ONLY")
            finally:
                base.store.close()

    def test_journal_requires_governed_trigger(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = _BaseRuntime(Path(temp))
            try:
                runtime = ReplayV01Runtime(base)
                with self.assertRaises(ValueError):
                    runtime.append_journal(entry_id="j-1", body="reflection", trigger="EVERY_5M")
                runtime.append_journal(
                    entry_id="j-2",
                    body="end of session reflection",
                    trigger="END_OF_SESSION",
                    observation_identity="obs-1",
                )
                journal = base.store.list_journal(limit=None)
                self.assertEqual(len(journal), 1)
                self.assertIn("V0_1_TRIGGER:END_OF_SESSION", journal[0].tags)
            finally:
                base.store.close()


if __name__ == "__main__":
    unittest.main()

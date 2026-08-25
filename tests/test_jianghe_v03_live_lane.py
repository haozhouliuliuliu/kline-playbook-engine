"""V0.3 live-lane crash-safety and duplicate-call prevention tests (zero network)."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import json
import os
import subprocess
import tempfile
import unittest

from src.jianghe_v03_live_lane import (
    ATTEMPT_TERMINAL,
    DEFAULT_REMOTE_REF,
    LEDGER_FILENAME,
    NETWORK_ATTEMPT_STARTED,
    V03GitRemoteLedgerStore,
    V03LedgerConflictError,
    V03LedgerIntegrityError,
    V03LedgerUnavailableError,
    V03RemoteExecutionLedger,
)
from src.jianghe_v03_plan import build_v03_frozen_plan, pretty_plan_bytes
from src.jianghe_v03_runtime import (
    HISTORICAL_PROJECT_ACCOUNTED_CNY,
    V03TerminalStatus,
    v03_slot_identity,
)

NOW = datetime(2026, 8, 25, 2, 0, tzinfo=timezone.utc)


def _plan():
    plan = build_v03_frozen_plan()
    plan_bytes = pretty_plan_bytes(plan)
    import hashlib
    return plan, hashlib.sha256(plan_bytes).hexdigest(), plan_bytes


class V03RemoteLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan, cls.plan_sha256, cls.plan_bytes = _plan()

    def test_empty_ledger_preserves_historical_spend(self) -> None:
        ledger = V03RemoteExecutionLedger(self.plan, self.plan_sha256)
        snapshot = ledger.snapshot()
        self.assertEqual(Decimal("0.270021"), snapshot.project_accounted_cny)
        self.assertEqual(0, snapshot.total_attempts)

    def test_start_then_terminal_chain(self) -> None:
        ledger = V03RemoteExecutionLedger(self.plan, self.plan_sha256)
        slot = v03_slot_identity("DEEPSEEK")
        started = ledger.append_start(
            now=NOW,
            provider_id="DEEPSEEK",
            slot_identity=slot,
            request_identity="r1",
            worst_case_cny=Decimal("1.39"),
        )
        self.assertIn(slot, started.snapshot().attempted_slots)
        terminal = started.append_terminal(
            now=NOW,
            provider_id="DEEPSEEK",
            slot_identity=slot,
            status=V03TerminalStatus.CAPABILITY_SCOREABLE.value,
            accounted_cny=Decimal("0.05"),
            evidence_identity="a" * 64,
            evidence_network_start_event_identity="b" * 64,
            evidence_terminal_event_identity="c" * 64,
        )
        self.assertEqual(Decimal("0.320021"), terminal.snapshot().project_accounted_cny)

    def test_duplicate_start_rejected(self) -> None:
        ledger = V03RemoteExecutionLedger(self.plan, self.plan_sha256)
        slot = v03_slot_identity("MINIMAX")
        started = ledger.append_start(
            now=NOW, provider_id="MINIMAX", slot_identity=slot,
            request_identity="r2", worst_case_cny=Decimal("2.0"),
        )
        with self.assertRaises(V03LedgerConflictError):
            started.append_start(
                now=NOW, provider_id="MINIMAX", slot_identity=slot,
                request_identity="r2", worst_case_cny=Decimal("2.0"),
            )

    def test_serialization_round_trip(self) -> None:
        ledger = V03RemoteExecutionLedger(self.plan, self.plan_sha256)
        slot = v03_slot_identity("KIMI")
        started = ledger.append_start(
            now=NOW, provider_id="KIMI", slot_identity=slot,
            request_identity="r3", worst_case_cny=Decimal("14.5"),
        )
        raw = started.to_bytes()
        rebuilt = V03RemoteExecutionLedger.from_bytes(self.plan, self.plan_sha256, raw)
        self.assertEqual(raw, rebuilt.to_bytes())

    def test_wrong_plan_binding_rejected(self) -> None:
        ledger = V03RemoteExecutionLedger(self.plan, self.plan_sha256)
        raw = ledger.to_bytes()
        other_plan = dict(self.plan)
        other_plan["plan_identity"] = "f" * 64
        with self.assertRaises(V03LedgerIntegrityError):
            V03RemoteExecutionLedger.from_bytes(other_plan, self.plan_sha256, raw)

    def test_old_slot_semantics_rejected(self) -> None:
        ledger = V03RemoteExecutionLedger(self.plan, self.plan_sha256)
        with self.assertRaises(V03LedgerIntegrityError):
            ledger.append_start(
                now=NOW, provider_id="DEEPSEEK", slot_identity="DEEPSEEK:1",
                request_identity="old", worst_case_cny=Decimal("1"),
            )


class FakeStore:
    """In-memory store implementing the CAS protocol for crash-safety tests."""

    def __init__(self, plan, plan_sha256) -> None:
        self.plan = plan
        self.plan_sha256 = plan_sha256
        self.head = None
        self.ledger = V03RemoteExecutionLedger(plan, plan_sha256)
        self.evidence: dict[str, bytes] = {}
        self.calls = 0

    def load(self):
        self.calls += 1
        return type("Observed", (), {"head_sha": self.head, "ledger": self.ledger})()

    def compare_and_swap(self, *, expected_head, ledger_bytes, evidence_artifacts=None):
        self.calls += 1
        if expected_head != self.head:
            raise V03LedgerConflictError("stale head")
        if evidence_artifacts:
            for name, content in evidence_artifacts.items():
                self.evidence[name] = content
        self.ledger = V03RemoteExecutionLedger.from_bytes(
            self.plan, self.plan_sha256, ledger_bytes
        )
        import hashlib
        self.head = hashlib.sha256(ledger_bytes).hexdigest()
        return self.head


class V03FakeStoreLaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan, cls.plan_sha256, cls.plan_bytes = _plan()

    def test_crash_after_start_keeps_slot_non_retryable(self) -> None:
        store = FakeStore(self.plan, self.plan_sha256)
        slot = v03_slot_identity("DEEPSEEK")
        ledger = store.ledger.append_start(
            now=NOW, provider_id="DEEPSEEK", slot_identity=slot,
            request_identity="r", worst_case_cny=Decimal("1.39"),
        )
        store.compare_and_swap(expected_head=None, ledger_bytes=ledger.to_bytes())
        # Crash here. Re-open: the slot is attempted and must not rerun.
        with self.assertRaises(V03LedgerConflictError):
            store.ledger.append_start(
                now=NOW, provider_id="DEEPSEEK", slot_identity=slot,
                request_identity="r", worst_case_cny=Decimal("1.39"),
            )
        self.assertEqual(Decimal("0.270021") + Decimal("1.39"), store.ledger.snapshot().project_accounted_cny)

    def test_concurrent_same_slot_only_first_reservation_succeeds(self) -> None:
        store = FakeStore(self.plan, self.plan_sha256)
        slot = v03_slot_identity("KIMI")
        base = store.ledger
        ledger_a = base.append_start(
            now=NOW, provider_id="KIMI", slot_identity=slot,
            request_identity="ra", worst_case_cny=Decimal("14.5"),
        )
        ledger_b = base.append_start(
            now=NOW, provider_id="KIMI", slot_identity=slot,
            request_identity="rb", worst_case_cny=Decimal("14.5"),
        )
        head_a = store.compare_and_swap(expected_head=None, ledger_bytes=ledger_a.to_bytes())
        self.assertIsNotNone(head_a)
        # Observer B still holds the stale empty-head expectation and must fail CAS.
        with self.assertRaises(V03LedgerConflictError):
            store.compare_and_swap(expected_head=None, ledger_bytes=ledger_b.to_bytes())


class V03GitStoreTests(unittest.TestCase):
    def _make_remote(self, tmp: str) -> str:
        remote = os.path.join(tmp, "remote.git")
        subprocess.run(["git", "init", "--bare", "-q", remote], check=True)
        return remote

    def test_real_git_cas_rejects_stale_observer(self) -> None:
        plan, plan_sha256, plan_bytes = _plan()
        with tempfile.TemporaryDirectory() as tmp:
            local = os.path.join(tmp, "local")
            remote = self._make_remote(tmp)
            os.makedirs(local)
            subprocess.run(["git", "init", "-q"], cwd=local, check=True)
            subprocess.run(["git", "remote", "add", "origin", remote], cwd=local, check=True)
            store = V03GitRemoteLedgerStore(repository=local, remote="origin")
            with self.assertRaises(V03LedgerUnavailableError):
                store.load()
            slot = v03_slot_identity("DEEPSEEK")
            ledger = V03RemoteExecutionLedger(plan, plan_sha256).append_start(
                now=NOW, provider_id="DEEPSEEK", slot_identity=slot,
                request_identity="r", worst_case_cny=Decimal("1.39"),
            )
            head = store.compare_and_swap(expected_head=None, ledger_bytes=ledger.to_bytes())
            self.assertIsNotNone(head)
            # A stale observer cannot advance the ref.
            stale = V03RemoteExecutionLedger(plan, plan_sha256)
            with self.assertRaises(V03LedgerConflictError):
                store.compare_and_swap(
                    expected_head=None,
                    ledger_bytes=stale.append_start(
                        now=NOW, provider_id="MINIMAX", slot_identity=v03_slot_identity("MINIMAX"),
                        request_identity="r", worst_case_cny=Decimal("2.0"),
                    ).to_bytes(),
                )
            observed = store.load()
            self.assertEqual(slot, list(observed.ledger.snapshot().attempted_slots)[0])

    def test_terminal_without_provider_evidence_round_trips(self) -> None:
        plan, plan_sha256, _ = _plan()
        with tempfile.TemporaryDirectory() as tmp:
            local = os.path.join(tmp, "local")
            remote = self._make_remote(tmp)
            os.makedirs(local)
            subprocess.run(["git", "init", "-q"], cwd=local, check=True)
            subprocess.run(["git", "remote", "add", "origin", remote], cwd=local, check=True)
            store = V03GitRemoteLedgerStore(repository=local, remote="origin")
            slot = v03_slot_identity("DEEPSEEK")
            started = V03RemoteExecutionLedger(plan, plan_sha256).append_start(
                now=NOW,
                provider_id="DEEPSEEK",
                slot_identity=slot,
                request_identity="request",
                worst_case_cny=Decimal("1.389174"),
            )
            start_head = store.compare_and_swap(
                expected_head=None,
                ledger_bytes=started.to_bytes(),
            )
            terminal = started.append_terminal(
                now=NOW,
                provider_id="DEEPSEEK",
                slot_identity=slot,
                status=V03TerminalStatus.TRANSPORT_FAILURE.value,
                accounted_cny=Decimal("1.389174"),
                evidence_identity="0" * 64,
                evidence_network_start_event_identity="0" * 64,
                evidence_terminal_event_identity="0" * 64,
            )
            store.compare_and_swap(
                expected_head=start_head,
                ledger_bytes=terminal.to_bytes(),
            )

            observed = store.load()
            self.assertEqual(1, observed.ledger.snapshot().total_attempts)
            self.assertEqual(2, len(observed.ledger.events))


if __name__ == "__main__":
    unittest.main()

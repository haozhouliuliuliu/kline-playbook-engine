from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from src.jianghe_prespend_runtime import HttpResponse, KIMI_K3_SPEC, PaidCallNotAuthorizedError
from src.jianghe_response_normalizer import RESPONSE_SCHEMA_VERSION
from src.jianghe_stage_a_evidence import SecretExposureError, load_verified_frozen_plan
from src.jianghe_stage_a_live_lane import LiveLaneError, execute_remote_reserved_slot
from src.jianghe_stage_a_remote_ledger import (
    GitRemoteLedgerStore,
    RemoteExecutionLedger,
    RemoteLedgerConflictError,
    RemoteLedgerIntegrityError,
    RemoteLedgerObservedState,
    RemoteLedgerUnavailableError,
    _identity,
)
from src.jianghe_stage_a_runner import (
    CredentialUnavailableError,
    JournalSnapshot,
    SlotAlreadyAttemptedError,
    StageAExecutionError,
    prepare_frozen_slot,
)

NOW = datetime(2026, 8, 24, 2, 30, tzinfo=timezone.utc)


def _content() -> str:
    return json.dumps(
        {
            "schema_version": RESPONSE_SCHEMA_VERSION,
            "family": "NONE",
            "action": "NO_TRADE",
            "direction": "NONE",
            "attention_mode": "WATCH",
            "decision_state": "NO_CONFIRMED_BREAKOUT",
            "rationale": "没有形成可确认的延续触发。",
            "declared_unknown": [],
            "principle_references": [],
            "source_references": [],
            "numeric_claims": [],
        },
        ensure_ascii=False,
        separators=(",", ":"),
    )


def _response(*_args, **_kwargs) -> HttpResponse:
    return HttpResponse(
        200,
        {},
        json.dumps(
            {
                "id": "live-lane-offline-test",
                "model": KIMI_K3_SPEC.model_id,
                "choices": [{"message": {"content": _content()}}],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 40,
                    "image_tokens": 0,
                },
            },
            ensure_ascii=False,
        ).encode("utf-8"),
    )


class FakeStore:
    def __init__(self, plan) -> None:
        self.plan = plan
        self.head = None
        self.ledger = RemoteExecutionLedger.empty(plan)
        self.cas_calls = 0
        self.artifacts: dict[str, bytes] = {}
        self.fail_load = False
        self.fail_cas_at: int | None = None
        self.change_before_cas = False
        self.corrupt_next_verification = False

    def load(self, plan):
        if self.fail_load:
            raise RemoteLedgerUnavailableError("offline injected unavailable")
        if self.corrupt_next_verification and self.head is not None:
            self.corrupt_next_verification = False
            return RemoteLedgerObservedState("f" * 40, self.ledger)
        return RemoteLedgerObservedState(self.head, self.ledger)

    def compare_and_swap(self, *, expected_head, ledger_bytes, evidence_artifacts=None):
        self.cas_calls += 1
        if self.fail_cas_at == self.cas_calls:
            raise RemoteLedgerConflictError("offline injected CAS failure")
        if self.change_before_cas:
            self.change_before_cas = False
            self.head = "e" * 40
        if expected_head != self.head:
            raise RemoteLedgerConflictError("stale head")
        self.ledger = RemoteExecutionLedger.from_bytes(self.plan, ledger_bytes)
        self.head = f"{self.cas_calls:040x}"
        self.artifacts.update(evidence_artifacts or {})
        return self.head


class SnapshotOverrideLedger:
    def __init__(self, source, snapshot) -> None:
        self.source = source
        self._snapshot = snapshot

    def snapshot(self):
        return self._snapshot

    def append_start(self, **kwargs):
        return self.source.append_start(**kwargs)

    def to_bytes(self):
        return self.source.to_bytes()


class StageALiveLaneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_verified_frozen_plan()

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state_dir = Path(self.tmp.name) / "state"
        self.store = FakeStore(self.plan)
        self.network_calls = 0

    def _post(self, *args, **kwargs):
        self.network_calls += 1
        return _response(*args, **kwargs)

    def _run(self, **changes):
        values = {
            "plan": self.plan,
            "store": self.store,
            "state_dir": self.state_dir,
            "provider_id": "KIMI",
            "slot": 2,
            "now": NOW,
            "http_post": self._post,
            "credential_lookup": lambda _name: "TEST_ONLY",
        }
        values.update(changes)
        with patch.dict(os.environ, {KIMI_K3_SPEC.api_key_env: "TEST_ONLY"}, clear=True):
            return execute_remote_reserved_slot(**values)

    def test_remote_state_unavailable_means_zero_network(self) -> None:
        self.store.fail_load = True
        with self.assertRaises(RemoteLedgerUnavailableError):
            self._run()
        self.assertEqual(0, self.network_calls)

    def test_remote_write_failure_means_zero_network(self) -> None:
        self.store.fail_cas_at = 1
        with self.assertRaises(RemoteLedgerConflictError):
            self._run()
        self.assertEqual(0, self.network_calls)

    def test_remote_verification_failure_means_zero_network(self) -> None:
        self.store.corrupt_next_verification = True
        with self.assertRaises(LiveLaneError):
            self._run()
        self.assertEqual(0, self.network_calls)

    def test_concurrent_same_slot_only_one_reservation_succeeds(self) -> None:
        first = self.store.load(self.plan)
        second = self.store.load(self.plan)
        prepared = prepare_frozen_slot(self.plan, provider_id="KIMI", slot=2, now=NOW)
        kwargs = {
            "now": NOW,
            "provider_id": "KIMI",
            "slot": 2,
            "model_id": prepared.provider_spec.model_id,
            "request_identity": str(prepared.slot_row["request_identity"]),
            "payload_sha256": str(prepared.slot_row["payload_sha256"]),
            "worst_case_cny": prepared.worst_case_cny,
        }
        one = first.ledger.append_start(**kwargs)
        two = second.ledger.append_start(**kwargs)
        self.store.compare_and_swap(expected_head=first.head_sha, ledger_bytes=one.to_bytes())
        with self.assertRaises(RemoteLedgerConflictError):
            self.store.compare_and_swap(expected_head=second.head_sha, ledger_bytes=two.to_bytes())

    def test_stale_remote_head_means_zero_network(self) -> None:
        self.store.change_before_cas = True
        with self.assertRaises(RemoteLedgerConflictError):
            self._run()
        self.assertEqual(0, self.network_calls)

    def test_started_slot_retry_is_forbidden(self) -> None:
        self._reserve_only()
        with self.assertRaises(SlotAlreadyAttemptedError):
            self._run()
        self.assertEqual(0, self.network_calls)

    def test_started_without_terminal_accounts_full_worst_case(self) -> None:
        prepared = self._reserve_only()
        snapshot = self.store.ledger.snapshot()
        self.assertEqual(prepared.worst_case_cny, snapshot.stage_accounted_cny)

    def test_crash_immediately_after_remote_start_never_recalls_slot(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "crash after start"):
            self._run(after_remote_start=lambda: (_ for _ in ()).throw(RuntimeError("crash after start")))
        self.assertEqual(0, self.network_calls)
        with self.assertRaises(SlotAlreadyAttemptedError):
            self._run()
        self.assertEqual(0, self.network_calls)

    def test_crash_during_network_keeps_slot_non_retryable(self) -> None:
        def crash(*_args, **_kwargs):
            self.network_calls += 1
            raise KeyboardInterrupt("simulated runner loss")

        with self.assertRaises(KeyboardInterrupt):
            self._run(http_post=crash)
        with self.assertRaises(SlotAlreadyAttemptedError):
            self._run()
        self.assertEqual(1, self.network_calls)

    def test_terminal_persistence_failure_keeps_slot_non_retryable(self) -> None:
        self.store.fail_cas_at = 2
        with self.assertRaises(RemoteLedgerConflictError):
            self._run()
        self.assertEqual(1, self.network_calls)
        with self.assertRaises(SlotAlreadyAttemptedError):
            self._run()
        self.assertEqual(1, self.network_calls)

    def test_evidence_secret_guard_failure_does_not_allow_retry(self) -> None:
        with patch(
            "src.jianghe_stage_a_live_lane.materialize_stage_a_attempt_evidence",
            side_effect=SecretExposureError("offline injected secret guard"),
        ):
            with self.assertRaises(SecretExposureError):
                self._run()
        with self.assertRaises(SlotAlreadyAttemptedError):
            self._run()
        self.assertEqual(1, self.network_calls)

    def test_duplicate_terminal_fails_closed(self) -> None:
        result = self._run()
        with self.assertRaises(RemoteLedgerConflictError):
            self.store.ledger.append_terminal(
                now=NOW,
                provider_id="KIMI",
                slot=2,
                status=result.slot_result.status,
                accounted_cny=result.slot_result.accounted_cny,
                evidence_identity=result.evidence_identity,
            )

    def test_state_hash_tamper_fails_closed(self) -> None:
        self._reserve_only()
        payload = json.loads(self.store.ledger.to_bytes())
        payload["events"][0]["slot"] = 3
        with self.assertRaises(RemoteLedgerIntegrityError):
            RemoteExecutionLedger.from_bytes(self.plan, json.dumps(payload).encode())

    def test_wrong_plan_identity_means_zero_network(self) -> None:
        class WrongPlanStore(FakeStore):
            def load(inner_self, plan):
                raise RemoteLedgerIntegrityError("remote ledger is bound to a different plan")

        self.store = WrongPlanStore(self.plan)
        with self.assertRaises(RemoteLedgerIntegrityError):
            self._run()
        self.assertEqual(0, self.network_calls)

    def test_wrong_request_or_payload_fails_remote_validation(self) -> None:
        self._reserve_only()
        for field in ("request_identity", "payload_sha256"):
            with self.subTest(field=field):
                payload = json.loads(self.store.ledger.to_bytes())
                payload["events"][0][field] = "0" * 64
                event_identity_payload = dict(payload["events"][0])
                event_identity_payload.pop("event_identity")
                payload["events"][0]["event_identity"] = _identity(event_identity_payload)
                ledger_identity_payload = dict(payload)
                ledger_identity_payload.pop("ledger_identity")
                payload["ledger_identity"] = _identity(ledger_identity_payload)
                with self.assertRaises(RemoteLedgerIntegrityError):
                    RemoteExecutionLedger.from_bytes(self.plan, json.dumps(payload).encode())

    def test_wrong_provider_or_model_means_zero_network(self) -> None:
        with self.assertRaises(StageAExecutionError):
            self._run(provider_id="UNKNOWN")
        self.assertEqual(0, self.network_calls)
        self._reserve_only()
        payload = json.loads(self.store.ledger.to_bytes())
        payload["events"][0]["model_id"] = "wrong-model"
        event_identity_payload = dict(payload["events"][0])
        event_identity_payload.pop("event_identity")
        payload["events"][0]["event_identity"] = _identity(event_identity_payload)
        ledger_identity_payload = dict(payload)
        ledger_identity_payload.pop("ledger_identity")
        payload["ledger_identity"] = _identity(ledger_identity_payload)
        with self.assertRaises(RemoteLedgerIntegrityError):
            RemoteExecutionLedger.from_bytes(self.plan, json.dumps(payload).encode())

    def test_budget_cap_exceeded_means_zero_network(self) -> None:
        high = JournalSnapshot(
            attempted_slots=frozenset(),
            project_accounted_cny=Decimal("18"),
            stage_accounted_cny=Decimal("18"),
            provider_accounted_cny={},
            total_attempts=14,
            provider_attempts={},
        )
        self.store.ledger = SnapshotOverrideLedger(self.store.ledger, high)
        with self.assertRaises(StageAExecutionError):
            self._run()
        self.assertEqual(0, self.network_calls)

    def test_expired_authorization_means_zero_network(self) -> None:
        with patch(
            "src.jianghe_stage_a_runner.load_owner_paid_call_authorization",
            side_effect=PaidCallNotAuthorizedError("expired"),
        ):
            with self.assertRaises(PaidCallNotAuthorizedError):
                self._run()
        self.assertEqual(0, self.network_calls)

    def test_missing_credential_means_zero_network(self) -> None:
        with self.assertRaises(CredentialUnavailableError):
            self._run(credential_lookup=lambda _name: None)
        self.assertEqual(0, self.network_calls)

    def test_remote_change_between_preflight_and_reserve_is_detected(self) -> None:
        self.store.change_before_cas = True
        with self.assertRaises(RemoteLedgerConflictError):
            self._run()
        self.assertEqual(0, self.network_calls)

    def test_resume_only_accepts_legally_unattempted_slot(self) -> None:
        self._reserve_only(slot=2)
        result = self._run(slot=3)
        self.assertEqual(3, result.slot_result.slot)
        self.assertEqual(1, self.network_calls)

    def test_evidence_identity_binds_remote_terminal_slot_and_plan(self) -> None:
        result = self._run()
        terminal = self.store.ledger.events[-1]
        self.assertEqual(result.evidence_identity, terminal["evidence_identity"])
        self.assertEqual("KIMI:2", terminal["slot_key"])
        self.assertEqual(self.plan.plan_identity, terminal["plan_identity"])
        self.assertIn(f"evidence-{result.evidence_identity}.json", self.store.artifacts)
        self.assertTrue(all("journal" not in name for name in self.store.artifacts))

    def test_safe_remote_ledger_contains_no_raw_credential_material(self) -> None:
        self._run(credential_lookup=lambda _name: "Bearer SUPER_SECRET_123456")
        encoded = self.store.ledger.to_bytes()
        self.assertNotIn(b"SUPER_SECRET", encoded)
        self.assertNotIn(b"Authorization", encoded)
        self.assertNotIn(b"raw_provider_response", encoded)

    def _reserve_only(self, *, slot: int = 2):
        prepared = prepare_frozen_slot(self.plan, provider_id="KIMI", slot=slot, now=NOW)
        ledger = self.store.ledger.append_start(
            now=NOW,
            provider_id="KIMI",
            slot=slot,
            model_id=prepared.provider_spec.model_id,
            request_identity=str(prepared.slot_row["request_identity"]),
            payload_sha256=str(prepared.slot_row["payload_sha256"]),
            worst_case_cny=prepared.worst_case_cny,
        )
        self.store.compare_and_swap(expected_head=self.store.head, ledger_bytes=ledger.to_bytes())
        return prepared


class GitRemoteLedgerStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = load_verified_frozen_plan()

    def test_real_git_non_force_cas_rejects_stale_observer_and_retains_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            bare = root / "state.git"
            repos = [root / "one", root / "two"]
            subprocess.run(["git", "init", "--bare", str(bare)], check=True, capture_output=True)
            stores = []
            for repo in repos:
                subprocess.run(["git", "init", str(repo)], check=True, capture_output=True)
                subprocess.run(
                    ["git", "-C", str(repo), "remote", "add", "state", str(bare)],
                    check=True,
                    capture_output=True,
                )
                stores.append(GitRemoteLedgerStore(repository=repo, remote="state"))
            observed = [store.load(self.plan) for store in stores]
            prepared_two = prepare_frozen_slot(self.plan, provider_id="KIMI", slot=2, now=NOW)
            prepared_three = prepare_frozen_slot(self.plan, provider_id="KIMI", slot=3, now=NOW)

            def reserve(base, prepared, slot):
                return base.append_start(
                    now=NOW,
                    provider_id="KIMI",
                    slot=slot,
                    model_id=prepared.provider_spec.model_id,
                    request_identity=str(prepared.slot_row["request_identity"]),
                    payload_sha256=str(prepared.slot_row["payload_sha256"]),
                    worst_case_cny=prepared.worst_case_cny,
                )

            first = reserve(observed[0].ledger, prepared_two, 2)
            stale = reserve(observed[1].ledger, prepared_three, 3)
            first_head = stores[0].compare_and_swap(
                expected_head=None, ledger_bytes=first.to_bytes()
            )
            with self.assertRaises(RemoteLedgerConflictError):
                stores[1].compare_and_swap(expected_head=None, ledger_bytes=stale.to_bytes())

            evidence_bytes = b'{"secret_free":true}\n'
            evidence_identity = sha256(evidence_bytes).hexdigest()
            terminal = first.append_terminal(
                now=NOW,
                provider_id="KIMI",
                slot=2,
                status="TRANSPORT_FAILURE",
                accounted_cny=prepared_two.worst_case_cny,
                evidence_identity=evidence_identity,
            )
            terminal_head = stores[0].compare_and_swap(
                expected_head=first_head,
                ledger_bytes=terminal.to_bytes(),
                evidence_artifacts={f"evidence-{evidence_identity}.json": evidence_bytes},
            )
            refreshed = stores[1].load(self.plan)
            next_ledger = reserve(refreshed.ledger, prepared_three, 3)
            next_head = stores[1].compare_and_swap(
                expected_head=terminal_head,
                ledger_bytes=next_ledger.to_bytes(),
            )
            retained = subprocess.run(
                ["git", "-C", str(repos[1]), "show", f"{next_head}:evidence-{evidence_identity}.json"],
                check=True,
                capture_output=True,
            ).stdout
            self.assertEqual(evidence_bytes, retained)


if __name__ == "__main__":
    unittest.main()

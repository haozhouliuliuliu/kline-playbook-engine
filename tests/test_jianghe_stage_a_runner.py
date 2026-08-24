from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.jianghe_prespend_runtime import HttpResponse, KIMI_K3_SPEC
from src.jianghe_source_only_verification import _repository_blob_bytes
from src.jianghe_stage_a_runner import (
    CredentialUnavailableError,
    ExecutionLockError,
    FROZEN_PLAN_PATH,
    FrozenPlanMismatchError,
    JournalIntegrityError,
    JournalSnapshot,
    PROMPT_PACKAGE_PATH,
    SlotAlreadyAttemptedError,
    StageAExecutionJournal,
    StageAExecutionLock,
    VerifiedFrozenStageAPlan,
    _prompt_strings,
    enforce_persistent_caps,
    execute_frozen_slot,
    prepare_frozen_slot,
)
from src.jianghe_stage_a_runtime import build_stage_a_stimulus
from src.jianghe_response_normalizer import RESPONSE_SCHEMA_VERSION
from tools.build_jianghe_stage_a_frozen_plan_v0_2 import build_frozen_plan

NOW = datetime(2026, 8, 24, 2, 30, tzinfo=timezone.utc)


def _pretty_bytes(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False)
        + "\n"
    ).encode("utf-8")


def _plan() -> VerifiedFrozenStageAPlan:
    return VerifiedFrozenStageAPlan.load(
        committed_path=FROZEN_PLAN_PATH,
        deterministic_rebuild_bytes=_pretty_bytes(build_frozen_plan()),
    )


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


def _response(*, model: str = KIMI_K3_SPEC.model_id, content: str | None = None) -> HttpResponse:
    body = json.dumps(
        {
            "id": "runner-test-response-1",
            "model": model,
            "choices": [{"message": {"content": _content() if content is None else content}}],
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 40,
                "image_tokens": 0,
            },
        },
        ensure_ascii=False,
    ).encode("utf-8")
    return HttpResponse(200, {}, body)


class FrozenPlanGuardTests(unittest.TestCase):
    def test_committed_plan_matches_deterministic_rebuild(self) -> None:
        plan = _plan()
        self.assertEqual(
            "9736e1cf75372ec13f524a971ee1d1c036a1d5e6ac51b250a6890a9ecf76d913",
            plan.plan_identity,
        )
        self.assertEqual("SEMANTIC", plan.slot_row("KIMI", 2)["track"])

    def test_plan_byte_drift_fails_closed(self) -> None:
        rebuilt = _pretty_bytes(build_frozen_plan()) + b" "
        with self.assertRaises(FrozenPlanMismatchError):
            VerifiedFrozenStageAPlan.load(
                committed_path=FROZEN_PLAN_PATH,
                deterministic_rebuild_bytes=rebuilt,
            )

    def test_crlf_worktree_cannot_redefine_prompt_repository_byte_authority(self) -> None:
        plan = _plan()
        committed_blob = _repository_blob_bytes(PROMPT_PACKAGE_PATH)
        crlf_worktree_bytes = committed_blob.replace(b"\n", b"\r\n")
        self.assertNotEqual(committed_blob, crlf_worktree_bytes)

        with patch(
            "src.jianghe_stage_a_runner._repository_blob_bytes",
            return_value=committed_blob,
        ) as repository_blob_bytes, patch.object(
            Path, "read_bytes", return_value=crlf_worktree_bytes
        ):
            system_prompt, decision_prompt = _prompt_strings(plan)

        repository_blob_bytes.assert_called_once_with(PROMPT_PACKAGE_PATH)
        self.assertTrue(system_prompt)
        self.assertTrue(decision_prompt)

    def test_runtime_must_materialize_frozen_36_bar_stimulus(self) -> None:
        plan = _plan()
        with patch(
            "src.jianghe_stage_a_runner.build_frozen_stage_a_stimulus",
            return_value=build_stage_a_stimulus(),
        ):
            with self.assertRaises(FrozenPlanMismatchError):
                prepare_frozen_slot(plan, provider_id="KIMI", slot=2, now=NOW)


class JournalTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = _plan()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "journal.jsonl"
        self.journal = StageAExecutionJournal(self.path, self.plan)
        self.prepared = prepare_frozen_slot(
            self.plan, provider_id="KIMI", slot=2, now=NOW
        )

    def _start(self):
        return self.journal.append_network_start(
            now=NOW,
            provider_id="KIMI",
            slot=2,
            request_identity=str(self.prepared.slot_row["request_identity"]),
            payload_sha256=str(self.prepared.slot_row["payload_sha256"]),
            worst_case_cny=self.prepared.worst_case_cny,
        )

    def test_incomplete_network_start_is_full_cost_and_never_retryable(self) -> None:
        self._start()
        snapshot = self.journal.snapshot()
        self.assertEqual(
            Decimal("0.219222") + self.prepared.worst_case_cny,
            snapshot.project_accounted_cny,
        )
        self.assertIn("KIMI:2", snapshot.attempted_slots)
        with self.assertRaises(SlotAlreadyAttemptedError):
            self.journal.append_network_start(
                now=NOW,
                provider_id="KIMI",
                slot=2,
                request_identity=str(self.prepared.slot_row["request_identity"]),
                payload_sha256=str(self.prepared.slot_row["payload_sha256"]),
                worst_case_cny=self.prepared.worst_case_cny,
            )

    def test_hash_chain_tamper_fails_closed(self) -> None:
        self._start()
        text = self.path.read_text(encoding="utf-8")
        self.path.write_text(
            text.replace('"provider_id":"KIMI"', '"provider_id":"KIMO"'),
            encoding="utf-8",
        )
        with self.assertRaises(JournalIntegrityError):
            self.journal.snapshot()

    def test_stale_lock_fails_closed(self) -> None:
        lock = Path(self.tmp.name) / "execution.lock"
        lock.write_text("stale", encoding="utf-8")
        with self.assertRaises(ExecutionLockError):
            with StageAExecutionLock(lock):
                self.fail("lock should not be acquired")


class PersistentCapTests(unittest.TestCase):
    def test_caps_include_persisted_accounting(self) -> None:
        snapshot = JournalSnapshot(
            attempted_slots=frozenset({"KIMI:1"}),
            project_accounted_cny=Decimal("17.90"),
            stage_accounted_cny=Decimal("17.90"),
            provider_accounted_cny={
                "KIMI": Decimal("5.90"),
                "DEEPSEEK": Decimal("6"),
                "MINIMAX": Decimal("6"),
            },
            total_attempts=1,
            provider_attempts={"KIMI": 1},
        )
        with self.assertRaisesRegex(Exception, "CNY18"):
            enforce_persistent_caps(
                snapshot, provider_id="KIMI", worst_case_cny=Decimal("0.11")
            )

    def test_provider_cap_is_independent(self) -> None:
        snapshot = JournalSnapshot(
            attempted_slots=frozenset(),
            project_accounted_cny=Decimal("5.95"),
            stage_accounted_cny=Decimal("5.95"),
            provider_accounted_cny={"KIMI": Decimal("5.95")},
            total_attempts=0,
            provider_attempts={},
        )
        with self.assertRaisesRegex(Exception, "CNY6"):
            enforce_persistent_caps(
                snapshot, provider_id="KIMI", worst_case_cny=Decimal("0.06")
            )


class SingleSlotExecutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.plan = _plan()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def _journal(self, name: str = "journal.jsonl") -> StageAExecutionJournal:
        return StageAExecutionJournal(Path(self.tmp.name) / name, self.plan)

    def test_missing_credential_never_creates_network_start(self) -> None:
        journal = self._journal()
        with self.assertRaises(CredentialUnavailableError):
            execute_frozen_slot(
                self.plan,
                journal,
                provider_id="KIMI",
                slot=2,
                now=NOW,
                http_post=lambda *_: self.fail("network must not be called"),
                credential_lookup=lambda _: None,
            )
        self.assertEqual(frozenset({"DEEPSEEK:1"}), journal.snapshot().attempted_slots)

    def test_success_is_persisted_and_duplicate_slot_is_blocked(self) -> None:
        calls = {"count": 0}

        def post(*_):
            calls["count"] += 1
            return _response()

        journal = self._journal()
        with patch.dict(
            os.environ, {KIMI_K3_SPEC.api_key_env: "TEST_ONLY"}, clear=True
        ):
            result = execute_frozen_slot(
                self.plan,
                journal,
                provider_id="KIMI",
                slot=2,
                now=NOW,
                http_post=post,
            )
        self.assertEqual("SUCCESS_NORMALIZED", result.status)
        self.assertIsNotNone(result.normalized_decision_identity)
        self.assertEqual(1, calls["count"])
        snapshot = journal.snapshot()
        self.assertIn("KIMI:2", snapshot.attempted_slots)
        self.assertGreater(snapshot.project_accounted_cny, Decimal("0"))

        with patch.dict(
            os.environ, {KIMI_K3_SPEC.api_key_env: "TEST_ONLY"}, clear=True
        ):
            with self.assertRaises(SlotAlreadyAttemptedError):
                execute_frozen_slot(
                    self.plan,
                    journal,
                    provider_id="KIMI",
                    slot=2,
                    now=NOW,
                    http_post=post,
                )
        self.assertEqual(1, calls["count"])

    def test_provider_model_drift_is_terminal_and_full_worst_case_accounted(self) -> None:
        journal = self._journal("model-drift.jsonl")
        prepared = prepare_frozen_slot(
            self.plan, provider_id="KIMI", slot=2, now=NOW
        )
        with patch.dict(
            os.environ, {KIMI_K3_SPEC.api_key_env: "TEST_ONLY"}, clear=True
        ):
            result = execute_frozen_slot(
                self.plan,
                journal,
                provider_id="KIMI",
                slot=2,
                now=NOW,
                http_post=lambda *_: _response(model="unexpected-model"),
            )
        self.assertEqual("PROVIDER_MODEL_DRIFT", result.status)
        self.assertIsNone(result.normalized_decision_identity)
        self.assertEqual(prepared.worst_case_cny, result.accounted_cny)
        self.assertEqual(
            Decimal("0.219222") + prepared.worst_case_cny,
            journal.snapshot().project_accounted_cny,
        )

    def test_malformed_semantic_output_is_non_scoreable_without_retry(self) -> None:
        calls = {"count": 0}

        def post(*_):
            calls["count"] += 1
            return _response(content="not-json")

        journal = self._journal("non-scoreable.jsonl")
        with patch.dict(
            os.environ, {KIMI_K3_SPEC.api_key_env: "TEST_ONLY"}, clear=True
        ):
            result = execute_frozen_slot(
                self.plan,
                journal,
                provider_id="KIMI",
                slot=2,
                now=NOW,
                http_post=post,
            )
        self.assertEqual("NON_SCOREABLE_NORMALIZER", result.status)
        self.assertEqual(1, calls["count"])
        self.assertGreater(result.accounted_cny, Decimal("0"))

    def test_http_failure_is_terminal_full_cost_and_never_retried(self) -> None:
        calls = {"count": 0}

        def post(*_):
            calls["count"] += 1
            return HttpResponse(500, {}, b"{}")

        journal = self._journal("transport-failure.jsonl")
        prepared = prepare_frozen_slot(
            self.plan, provider_id="KIMI", slot=2, now=NOW
        )
        with patch.dict(
            os.environ, {KIMI_K3_SPEC.api_key_env: "TEST_ONLY"}, clear=True
        ):
            result = execute_frozen_slot(
                self.plan,
                journal,
                provider_id="KIMI",
                slot=2,
                now=NOW,
                http_post=post,
            )
        self.assertEqual("TRANSPORT_FAILURE", result.status)
        self.assertEqual(prepared.worst_case_cny, result.accounted_cny)
        self.assertEqual(1, calls["count"])


if __name__ == "__main__":
    unittest.main()

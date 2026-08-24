from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha256
import json
import os
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from src.jianghe_prespend_runtime import HttpResponse, KIMI_K3_SPEC, ProviderUsage
from src.jianghe_response_normalizer import RESPONSE_SCHEMA_VERSION
from src.jianghe_stage_a_evidence import (
    EVALUATOR_JUDGMENT_REQUIRED,
    INCOMPLETE_STATUS,
    SecretExposureError,
    StageAEvidenceError,
    build_stage_a_attempt_evidence,
    canonical_json_bytes,
    forbidden_judgment_fields,
    load_verified_frozen_plan,
    materialize_stage_a_attempt_evidence,
)
from src.jianghe_stage_a_runner import (
    JournalIntegrityError,
    StageAExecutionJournal,
    execute_frozen_slot,
    prepare_frozen_slot,
)
from src.jianghe_stage_a_runtime import (
    StageAInputTrack,
    StageAProviderInvocationEvidence,
)

NOW = datetime(2026, 8, 24, 2, 30, tzinfo=timezone.utc)


def _canonical_compact(value: object) -> str:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True, allow_nan=False
    )


def _event_identity(event: dict[str, object]) -> str:
    payload = dict(event)
    payload.pop("event_identity", None)
    return sha256(_canonical_compact(payload).encode("utf-8")).hexdigest()


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
    return HttpResponse(
        200,
        {},
        json.dumps(
            {
                "id": "evidence-test-response-1",
                "model": model,
                "choices": [{"message": {"content": _content() if content is None else content}}],
                "usage": {
                    "prompt_tokens": 100,
                    "completion_tokens": 40,
                    "image_tokens": 0,
                },
            },
            ensure_ascii=False,
        ).encode("utf-8"),
    )


def _provider_payload_with(
    payload: dict[str, object], **changes: object
) -> dict[str, object]:
    changed = dict(payload)
    changed.update(changes)
    usage = changed["usage"]
    assert isinstance(usage, dict)
    evidence = StageAProviderInvocationEvidence(
        input_track=StageAInputTrack(str(changed["input_track"])),
        request_identity=str(changed["request_identity"]),
        source_observation_identity=str(changed["source_observation_identity"]),
        selected_context_identity=str(changed["selected_context_identity"]),
        context_selection_policy_identity=str(changed["context_selection_policy_identity"]),
        local_structured_observation_identity=str(
            changed["local_structured_observation_identity"]
        ),
        transmitted_structured_observation_identity=changed[
            "transmitted_structured_observation_identity"
        ],
        transmitted_visual_identities=tuple(changed["transmitted_visual_identities"]),
        provider_spec_identity=str(changed["provider_spec_identity"]),
        requested_model_id=str(changed["requested_model_id"]),
        resolved_model_id=str(changed["resolved_model_id"]),
        provider_request_id=str(changed["provider_request_id"]),
        raw_provider_response_body=str(changed["raw_provider_response_body"]),
        raw_response_text=str(changed["raw_response_text"]),
        usage=ProviderUsage(**usage),
        latency_ms=int(changed["latency_ms"]),
        rate_card_identity=str(changed["rate_card_identity"]),
        budget_reservation_id=str(changed["budget_reservation_id"]),
        charged_cny=str(changed["charged_cny"]),
    )
    changed["identity"] = evidence.identity
    return changed


class StageAAttemptEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.verified_plan = load_verified_frozen_plan()

    def setUp(self) -> None:
        self.plan = self.verified_plan
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state_dir = Path(self.tmp.name) / "state"
        self.path = self.state_dir / "journal.jsonl"
        self.journal = StageAExecutionJournal(self.path, self.plan)

    def _start(self, *, slot: int = 2):
        prepared = prepare_frozen_slot(self.plan, provider_id="KIMI", slot=slot, now=NOW)
        start = self.journal.append_network_start(
            now=NOW,
            provider_id="KIMI",
            slot=slot,
            request_identity=str(prepared.slot_row["request_identity"]),
            payload_sha256=str(prepared.slot_row["payload_sha256"]),
            worst_case_cny=prepared.worst_case_cny,
        )
        return prepared, start

    def _execute(self, *, content: str | None = None, model: str = KIMI_K3_SPEC.model_id):
        with patch.dict(os.environ, {KIMI_K3_SPEC.api_key_env: "TEST_ONLY"}, clear=True):
            return execute_frozen_slot(
                self.plan,
                self.journal,
                provider_id="KIMI",
                slot=2,
                now=NOW,
                http_post=lambda *_: _response(model=model, content=content),
            )

    def _artifact(self) -> dict[str, object]:
        return build_stage_a_attempt_evidence(plan=self.plan, journal_path=self.path)

    def _rewrite_events(self, mutate) -> None:
        events = [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines()]
        mutate(events)
        previous = None
        for sequence, event in enumerate(events, start=1):
            event["sequence"] = sequence
            event["prev_event_identity"] = previous
            event["event_identity"] = _event_identity(event)
            previous = event["event_identity"]
        self.path.write_text(
            "".join(_canonical_compact(event) + "\n" for event in events),
            encoding="utf-8",
            newline="\n",
        )

    def test_missing_and_empty_journal_fail_closed(self) -> None:
        with self.assertRaisesRegex(StageAEvidenceError, "missing"):
            self._artifact()
        self.path.parent.mkdir(parents=True)
        self.path.write_bytes(b"")
        with self.assertRaisesRegex(StageAEvidenceError, "empty"):
            self._artifact()

    def test_valid_success_requires_evaluator_judgment_without_synthesizing_it(self) -> None:
        result = self._execute()
        artifact = self._artifact()
        attempt = artifact["attempts"][0]
        self.assertEqual("SUCCESS_NORMALIZED", attempt["terminal_status"])
        self.assertEqual(EVALUATOR_JUDGMENT_REQUIRED, attempt["semantic_score_status"])
        self.assertEqual(result.normalized_decision_identity, attempt["normalized_decision_identity"])
        self.assertEqual(_content(), attempt["provider_evidence"]["raw_response_text"])
        encoded = canonical_json_bytes(artifact).decode("utf-8")
        for field in forbidden_judgment_fields():
            self.assertNotIn(f'"{field}"', encoded)

    def test_valid_non_scoreable_terminal_is_preserved_as_ineligible(self) -> None:
        self._execute(content="not-json")
        attempt = self._artifact()["attempts"][0]
        self.assertEqual("NON_SCOREABLE_NORMALIZER", attempt["terminal_status"])
        self.assertEqual("INELIGIBLE_CURRENT_ATTEMPT", attempt["semantic_score_status"])
        self.assertIsNone(attempt["normalized_decision_identity"])
        self.assertIsNotNone(attempt["provider_evidence"])

    def test_provider_model_drift_is_preserved_and_full_cost(self) -> None:
        prepared = prepare_frozen_slot(self.plan, provider_id="KIMI", slot=2, now=NOW)
        self._execute(model="unexpected-model")
        attempt = self._artifact()["attempts"][0]
        self.assertEqual("PROVIDER_MODEL_DRIFT", attempt["terminal_status"])
        self.assertEqual(str(prepared.slot_row["worst_case_cny"]), attempt["accounted_cny"])
        self.assertEqual("unexpected-model", attempt["provider_evidence"]["resolved_model_id"])

    def test_transport_failure_is_preserved_without_fake_success(self) -> None:
        with patch.dict(os.environ, {KIMI_K3_SPEC.api_key_env: "TEST_ONLY"}, clear=True):
            execute_frozen_slot(
                self.plan,
                self.journal,
                provider_id="KIMI",
                slot=2,
                now=NOW,
                http_post=lambda *_: HttpResponse(500, {}, b"{}"),
            )
        attempt = self._artifact()["attempts"][0]
        self.assertEqual("TRANSPORT_FAILURE", attempt["terminal_status"])
        self.assertEqual("INELIGIBLE_CURRENT_ATTEMPT", attempt["semantic_score_status"])
        self.assertIsNone(attempt["provider_evidence"])

    def test_start_without_terminal_is_incomplete_full_cost_and_no_retry(self) -> None:
        prepared, _ = self._start()
        attempt = self._artifact()["attempts"][0]
        self.assertEqual(INCOMPLETE_STATUS, attempt["terminal_status"])
        self.assertEqual(str(prepared.slot_row["worst_case_cny"]), attempt["accounted_cny"])
        self.assertEqual("FORBIDDEN", attempt["automatic_retry"])
        self.assertIsNone(attempt["terminal_event_identity"])

    def test_duplicate_slot_is_rejected_by_existing_journal_validator(self) -> None:
        self._start()

        def duplicate(events):
            events.append(dict(events[0]))

        self._rewrite_events(duplicate)
        with self.assertRaises(JournalIntegrityError):
            self._artifact()

    def test_tampered_event_identity_fails_closed(self) -> None:
        self._start()
        text = self.path.read_text(encoding="utf-8")
        self.path.write_text(text.replace('"event_identity":"', '"event_identity":"0', 1), encoding="utf-8")
        with self.assertRaises(JournalIntegrityError):
            self._artifact()

    def test_wrong_plan_request_payload_and_provider_bindings_fail_closed(self) -> None:
        mutations = (
            lambda event: event.__setitem__("plan_identity", "0" * 64),
            lambda event: event.__setitem__("request_identity", "0" * 64),
            lambda event: event.__setitem__("payload_sha256", "0" * 64),
            lambda event: event.__setitem__("provider_id", "DEEPSEEK"),
        )
        for index, mutation in enumerate(mutations):
            with self.subTest(index=index):
                path = self.state_dir / f"binding-{index}.jsonl"
                journal = StageAExecutionJournal(path, self.plan)
                prepared = prepare_frozen_slot(self.plan, provider_id="KIMI", slot=2, now=NOW)
                journal.append_network_start(
                    now=NOW,
                    provider_id="KIMI",
                    slot=2,
                    request_identity=str(prepared.slot_row["request_identity"]),
                    payload_sha256=str(prepared.slot_row["payload_sha256"]),
                    worst_case_cny=prepared.worst_case_cny,
                )
                event = json.loads(path.read_text(encoding="utf-8"))
                mutation(event)
                if event["provider_id"] == "DEEPSEEK":
                    event["slot_key"] = "DEEPSEEK:2"
                event["event_identity"] = _event_identity(event)
                path.write_text(_canonical_compact(event) + "\n", encoding="utf-8")
                with self.assertRaises(JournalIntegrityError):
                    build_stage_a_attempt_evidence(plan=self.plan, journal_path=path)

    def test_wrong_model_and_track_in_provider_evidence_fail_closed(self) -> None:
        for field, value in (
            ("requested_model_id", "wrong-model"),
            ("input_track", "VISUAL"),
        ):
            with self.subTest(field=field):
                path = self.state_dir / f"provider-{field}.jsonl"
                journal = StageAExecutionJournal(path, self.plan)
                with patch.dict(
                    os.environ, {KIMI_K3_SPEC.api_key_env: "TEST_ONLY"}, clear=True
                ):
                    execute_frozen_slot(
                        self.plan,
                        journal,
                        provider_id="KIMI",
                        slot=2,
                        now=NOW,
                        http_post=lambda *_: _response(),
                    )
                events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
                provider_payload = events[1]["provider_evidence"]
                events[1]["provider_evidence"] = _provider_payload_with(
                    provider_payload, **{field: value}
                )
                events[1]["event_identity"] = _event_identity(events[1])
                path.write_text(
                    "".join(_canonical_compact(event) + "\n" for event in events),
                    encoding="utf-8",
                )
                with self.assertRaises(StageAEvidenceError):
                    build_stage_a_attempt_evidence(plan=self.plan, journal_path=path)

    def test_provider_provenance_identity_mismatch_fails_closed(self) -> None:
        mutations = (
            ("source_observation_identity", "0" * 64),
            ("selected_context_identity", "0" * 64),
            ("context_selection_policy_identity", "0" * 64),
            ("local_structured_observation_identity", "0" * 64),
            ("transmitted_structured_observation_identity", "0" * 64),
            ("transmitted_visual_identities", ["0" * 64]),
        )
        for field, value in mutations:
            with self.subTest(field=field):
                path = self.state_dir / f"provenance-{field}.jsonl"
                journal = StageAExecutionJournal(path, self.plan)
                with patch.dict(
                    os.environ, {KIMI_K3_SPEC.api_key_env: "TEST_ONLY"}, clear=True
                ):
                    execute_frozen_slot(
                        self.plan,
                        journal,
                        provider_id="KIMI",
                        slot=2,
                        now=NOW,
                        http_post=lambda *_: _response(),
                    )
                events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
                provider_payload = events[1]["provider_evidence"]
                events[1]["provider_evidence"] = _provider_payload_with(
                    provider_payload, **{field: value}
                )
                events[1]["event_identity"] = _event_identity(events[1])
                path.write_text(
                    "".join(_canonical_compact(event) + "\n" for event in events),
                    encoding="utf-8",
                )
                with self.assertRaisesRegex(
                    StageAEvidenceError, "differs from frozen slot"
                ):
                    build_stage_a_attempt_evidence(plan=self.plan, journal_path=path)

    def test_accounted_cost_above_frozen_worst_case_fails_closed(self) -> None:
        prepared, start = self._start()
        self.journal.append_terminal(
            now=NOW,
            start_event=start,
            status="TRANSPORT_FAILURE",
            accounted_cny=prepared.worst_case_cny + Decimal("0.01"),
            provider_evidence=None,
            normalized_decision_identity=None,
            error_type="FakeTransportError",
            error_message="offline injected failure",
        )
        with self.assertRaises(JournalIntegrityError):
            self._artifact()

    def test_rebuild_is_byte_identical_and_journal_change_changes_identity(self) -> None:
        prepared, start = self._start()
        first = self._artifact()
        first_bytes = canonical_json_bytes(first)
        self.assertEqual(first_bytes, canonical_json_bytes(self._artifact()))
        self.journal.append_terminal(
            now=NOW,
            start_event=start,
            status="TRANSPORT_FAILURE",
            accounted_cny=prepared.worst_case_cny,
            provider_evidence=None,
            normalized_decision_identity=None,
            error_type="FakeTransportError",
            error_message="offline injected failure",
        )
        second = self._artifact()
        self.assertNotEqual(first["source_journal_sha256"], second["source_journal_sha256"])
        self.assertNotEqual(first["artifact_identity"], second["artifact_identity"])

    def test_materialization_never_rereads_accounting_from_a_different_journal_state(self) -> None:
        prepared, _ = self._start()
        original_events = list(self.journal.verified_events())

        mutated_path = self.state_dir / "mutated-journal.jsonl"
        mutated_journal = StageAExecutionJournal(mutated_path, self.plan)
        mutated_start = mutated_journal.append_network_start(
            now=NOW,
            provider_id="KIMI",
            slot=2,
            request_identity=str(prepared.slot_row["request_identity"]),
            payload_sha256=str(prepared.slot_row["payload_sha256"]),
            worst_case_cny=prepared.worst_case_cny,
        )
        mutated_journal.append_terminal(
            now=NOW,
            start_event=mutated_start,
            status="TRANSPORT_FAILURE",
            accounted_cny=Decimal("0"),
            provider_evidence=None,
            normalized_decision_identity=None,
            error_type="InjectedMutation",
            error_message="must not enter the original snapshot",
        )
        mutated_events = list(mutated_journal.verified_events())

        with patch.object(
            StageAExecutionJournal,
            "_read_events",
            side_effect=(original_events, mutated_events),
        ) as reread:
            artifact = self._artifact()

        self.assertEqual(0, reread.call_count)
        self.assertEqual(str(prepared.worst_case_cny), artifact["accounted_cny"])
        self.assertEqual(
            artifact["accounted_cny"], artifact["attempts"][0]["accounted_cny"]
        )

    def test_journal_byte_mutation_during_materialization_fails_closed(self) -> None:
        prepared, _ = self._start()
        original_bytes = self.path.read_bytes()

        mutated_path = self.state_dir / "changed-journal.jsonl"
        mutated_journal = StageAExecutionJournal(mutated_path, self.plan)
        mutated_start = mutated_journal.append_network_start(
            now=NOW,
            provider_id="KIMI",
            slot=2,
            request_identity=str(prepared.slot_row["request_identity"]),
            payload_sha256=str(prepared.slot_row["payload_sha256"]),
            worst_case_cny=prepared.worst_case_cny,
        )
        mutated_journal.append_terminal(
            now=NOW,
            start_event=mutated_start,
            status="TRANSPORT_FAILURE",
            accounted_cny=Decimal("0"),
            provider_evidence=None,
            normalized_decision_identity=None,
            error_type="InjectedMutation",
            error_message="journal changed during materialization",
        )
        mutated_bytes = mutated_path.read_bytes()
        real_read_bytes = Path.read_bytes
        journal_reads = {"count": 0}

        def changing_read_bytes(path: Path) -> bytes:
            if path == self.path:
                journal_reads["count"] += 1
                return original_bytes if journal_reads["count"] == 1 else mutated_bytes
            return real_read_bytes(path)

        with patch.object(Path, "read_bytes", new=changing_read_bytes):
            with self.assertRaisesRegex(StageAEvidenceError, "changed during"):
                self._artifact()

    def test_secret_like_value_fails_closed_and_never_reaches_output(self) -> None:
        prepared, start = self._start()
        fake_secret = "Bearer TEST_SECRET_123456789"
        self.journal.append_terminal(
            now=NOW,
            start_event=start,
            status="TRANSPORT_FAILURE",
            accounted_cny=prepared.worst_case_cny,
            provider_evidence=None,
            normalized_decision_identity=None,
            error_type="FakeTransportError",
            error_message=f"Authorization: {fake_secret}",
        )
        output = Path(self.tmp.name) / "evidence.json"
        with self.assertRaises(SecretExposureError):
            materialize_stage_a_attempt_evidence(
                state_dir=self.state_dir, output_path=output
            )
        self.assertFalse(output.exists())

    def test_exporter_performs_zero_network_calls(self) -> None:
        self._start()
        output = Path(self.tmp.name) / "evidence.json"
        with patch.object(
            socket,
            "create_connection",
            side_effect=AssertionError("network must not be called"),
        ):
            artifact = materialize_stage_a_attempt_evidence(
                state_dir=self.state_dir, output_path=output
            )
        self.assertEqual(canonical_json_bytes(artifact), output.read_bytes())

    def test_output_cannot_overwrite_source_journal(self) -> None:
        self._start()
        original = self.path.read_bytes()
        with self.assertRaisesRegex(StageAEvidenceError, "cannot overwrite"):
            materialize_stage_a_attempt_evidence(
                state_dir=self.state_dir, output_path=self.path
            )
        self.assertEqual(original, self.path.read_bytes())

    def test_success_requires_normalized_identity(self) -> None:
        self._execute()

        def remove_identity(events):
            events[1]["normalized_decision_identity"] = None

        self._rewrite_events(remove_identity)
        with self.assertRaisesRegex(StageAEvidenceError, "requires"):
            self._artifact()

    def test_non_scoreable_cannot_claim_normalized_success(self) -> None:
        self._execute(content="not-json")

        def add_identity(events):
            events[1]["normalized_decision_identity"] = "a" * 64

        self._rewrite_events(add_identity)
        with self.assertRaisesRegex(StageAEvidenceError, "cannot claim"):
            self._artifact()


if __name__ == "__main__":
    unittest.main()

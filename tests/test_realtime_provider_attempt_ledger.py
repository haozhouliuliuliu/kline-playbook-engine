"""Deterministic offline tests for the realtime provider-attempt ledger.

Proves one wake admits at most one attempt, retry stays zero, the state
machine is strict, UNKNOWN persists across a simulated restart, the authority
binding is enforced, and no provider/network action ever occurs.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.realtime_provider_attempt_ledger import (
    ATTEMPT_STARTED,
    DuplicateWakeAttemptError,
    RESULT_RECEIVED,
    UNKNOWN_AFTER_ATTEMPT_START,
    RealtimeAttemptIdentity,
    RealtimeProviderAttemptLedger,
    realtime_provider_attempt_ledger_path_for,
)

AUTHORITY_IDENTITY = "REALTIME_TEST_AUTHORITY"


def _identity(wake: str = "wake-1", **overrides: object) -> RealtimeAttemptIdentity:
    defaults: dict[str, object] = dict(
        trader_identity="trader-1",
        session_identity="session-1",
        wake_identity=wake,
        request_identity="request-1",
        provider_identity="DEEPSEEK_ONLY",
        model_identity="deepseek-v4-flash-vision-exp",
        prompt_identity="prompt-sha256",
        schema_identity="schema-v1",
        runtime_identity="runtime-v1",
        authority_identity=AUTHORITY_IDENTITY,
    )
    defaults.update(overrides)
    return RealtimeAttemptIdentity(**defaults)


class RealtimeProviderAttemptLedgerTests(unittest.TestCase):
    def test_one_wake_admits_at_most_one_attempt(self) -> None:
        with TemporaryDirectory() as tmp:
            ledger = RealtimeProviderAttemptLedger(
                realtime_provider_attempt_ledger_path_for(tmp), authority_identity=AUTHORITY_IDENTITY
            )
            first = ledger.record_attempt_started(identity=_identity("wake-1"))
            self.assertEqual(first.attempt_state, ATTEMPT_STARTED)
            self.assertEqual(first.retry_count, 0)
            with self.assertRaises(DuplicateWakeAttemptError):
                ledger.record_attempt_started(identity=_identity("wake-1"))
            self.assertEqual(len(ledger.attempts()), 1)
            self.assertEqual(ledger.admitted_attempt_count(), 1)

    def test_retry_count_is_fixed_at_zero(self) -> None:
        with TemporaryDirectory() as tmp:
            ledger = RealtimeProviderAttemptLedger(
                realtime_provider_attempt_ledger_path_for(tmp), authority_identity=AUTHORITY_IDENTITY
            )
            with self.assertRaisesRegex(ValueError, "fixed at zero"):
                ledger.record_attempt_started(identity=_identity("wake-1"), retry_count=1)

    def test_attempt_identity_binds_all_callers(self) -> None:
        identity = _identity("wake-1")
        self.assertEqual(identity.identity_id, _identity("wake-1").identity_id)
        self.assertNotEqual(identity.identity_id, _identity("wake-2").identity_id)
        self.assertNotEqual(
            identity.identity_id, _identity("wake-1", authority_identity="OTHER_AUTHORITY").identity_id
        )
        self.assertNotEqual(
            identity.identity_id, _identity("wake-1", model_identity="other-model").identity_id
        )
        with self.assertRaises(ValueError):
            _identity("wake-1", provider_identity="")

    def test_state_machine_started_to_result(self) -> None:
        with TemporaryDirectory() as tmp:
            ledger = RealtimeProviderAttemptLedger(
                realtime_provider_attempt_ledger_path_for(tmp), authority_identity=AUTHORITY_IDENTITY
            )
            started = ledger.record_attempt_started(identity=_identity("wake-1"))
            result = ledger.record_result_received(
                attempt_identity=started.attempt_identity, metadata={"ok": "true"}
            )
            self.assertEqual(result.attempt_state, RESULT_RECEIVED)
            self.assertEqual(ledger.result_received_count(), 1)
            # a terminal attempt cannot transition again
            with self.assertRaisesRegex(ValueError, "already terminal"):
                ledger.record_result_received(
                    attempt_identity=started.attempt_identity, metadata={"x": "y"}
                )

    def test_state_machine_started_to_unknown(self) -> None:
        with TemporaryDirectory() as tmp:
            ledger = RealtimeProviderAttemptLedger(
                realtime_provider_attempt_ledger_path_for(tmp), authority_identity=AUTHORITY_IDENTITY
            )
            started = ledger.record_attempt_started(identity=_identity("wake-1"))
            unknown = ledger.record_unknown_after_attempt_start(
                attempt_identity=started.attempt_identity, reason="timeout"
            )
            self.assertEqual(unknown.attempt_state, UNKNOWN_AFTER_ATTEMPT_START)
            self.assertEqual(ledger.unknown_after_attempt_start_count(), 1)

    def test_unknown_persists_across_simulated_restart(self) -> None:
        with TemporaryDirectory() as tmp:
            path = realtime_provider_attempt_ledger_path_for(tmp)
            ledger = RealtimeProviderAttemptLedger(path, authority_identity=AUTHORITY_IDENTITY)
            started = ledger.record_attempt_started(identity=_identity("wake-1"))
            ledger.record_unknown_after_attempt_start(
                attempt_identity=started.attempt_identity, reason="response-unknown"
            )
            # simulated restart: reopen the durable ledger
            reopened = RealtimeProviderAttemptLedger(path, authority_identity=AUTHORITY_IDENTITY)
            attempt = reopened.attempt_for_wake("wake-1")
            self.assertIsNotNone(attempt)
            self.assertEqual(attempt.attempt_state, UNKNOWN_AFTER_ATTEMPT_START)
            self.assertEqual(attempt.reason, "response-unknown")

    def test_unresolved_started_persists_and_counts(self) -> None:
        with TemporaryDirectory() as tmp:
            ledger = RealtimeProviderAttemptLedger(
                realtime_provider_attempt_ledger_path_for(tmp), authority_identity=AUTHORITY_IDENTITY
            )
            ledger.record_attempt_started(identity=_identity("wake-1"))
            self.assertEqual(ledger.unresolved_attempt_started_count(), 1)
            self.assertEqual(ledger.unknown_after_attempt_start_count(), 0)

    def test_authority_binding_is_enforced(self) -> None:
        with TemporaryDirectory() as tmp:
            path = realtime_provider_attempt_ledger_path_for(tmp)
            RealtimeProviderAttemptLedger(path, authority_identity=AUTHORITY_IDENTITY)
            with self.assertRaisesRegex(ValueError, "different authority"):
                RealtimeProviderAttemptLedger(path, authority_identity="OTHER_AUTHORITY")

    def test_portable_export_is_consistent(self) -> None:
        with TemporaryDirectory() as tmp:
            ledger = RealtimeProviderAttemptLedger(
                realtime_provider_attempt_ledger_path_for(tmp), authority_identity=AUTHORITY_IDENTITY
            )
            ledger.record_attempt_started(identity=_identity("wake-1"))
            export = ledger.portable_export()
            self.assertEqual(export["authority_identity"], AUTHORITY_IDENTITY)
            self.assertEqual(len(export["attempts"]), 1)
            self.assertEqual(export["attempts"][0]["wake_identity"], "wake-1")

    def test_never_started_transition_fails(self) -> None:
        with TemporaryDirectory() as tmp:
            ledger = RealtimeProviderAttemptLedger(
                realtime_provider_attempt_ledger_path_for(tmp), authority_identity=AUTHORITY_IDENTITY
            )
            with self.assertRaisesRegex(ValueError, "never started"):
                ledger.record_result_received(attempt_identity="missing", metadata={})


if __name__ == "__main__":
    unittest.main()

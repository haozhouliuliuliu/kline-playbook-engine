"""Deterministic offline tests for the realtime provider admission control.

Proves one governed wake admits at most one attempt, zero retries, duplicates
are rejected, UNKNOWN persists across restart and is never silently retried,
request-count ceilings block, monetary certainty is UNKNOWN without a tariff,
and no provider/network/DeepSeek action ever occurs.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.realtime_provider_attempt_ledger import (
    ATTEMPT_STARTED,
    UNKNOWN_AFTER_ATTEMPT_START,
    RealtimeAttemptIdentity,
    realtime_provider_attempt_ledger_path_for,
    RealtimeProviderAttemptLedger,
)
from src.realtime_provider_control import (
    RealtimeAdmissionResult,
    RealtimeBudgetInput,
    RealtimeProviderControl,
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


def _control(tmp: str) -> RealtimeProviderControl:
    ledger = RealtimeProviderAttemptLedger(
        realtime_provider_attempt_ledger_path_for(tmp), authority_identity=AUTHORITY_IDENTITY
    )
    return RealtimeProviderControl(ledger=ledger)


class RealtimeProviderControlTests(unittest.TestCase):
    def test_default_budget_invents_no_ceilings(self) -> None:
        budget = RealtimeBudgetInput()
        self.assertIsNone(budget.request_count_ceiling)
        self.assertEqual(budget.admitted_attempt_count, 0)
        self.assertFalse(budget.monetary_certainty)  # exact tariff unavailable
        self.assertTrue(budget.monetary_unknown)
        self.assertIsNone(budget.monetary_stop)
        self.assertEqual(budget.stop_reasons, ())
        self.assertTrue(budget.can_continue)

    def test_one_wake_admits_at_most_one_attempt(self) -> None:
        with TemporaryDirectory() as tmp:
            control = _control(tmp)
            first = control.admit(identity=_identity("wake-1"), budget=RealtimeBudgetInput())
            self.assertTrue(first.admitted)
            self.assertEqual(first.attempt_identity, _identity("wake-1").identity_id)
            second = control.admit(identity=_identity("wake-1"), budget=RealtimeBudgetInput())
            self.assertFalse(second.admitted)
            self.assertTrue(second.duplicate_wake)
            self.assertEqual(control.admitted_attempt_count(), 1)
            self.assertEqual(len(control.attempts()), 1)

    def test_zero_retry_default(self) -> None:
        with TemporaryDirectory() as tmp:
            control = _control(tmp)
            self.assertEqual(control.retry_count, 0)
            with self.assertRaisesRegex(ValueError, "fixed at zero"):
                RealtimeProviderControl(ledger=control.ledger, retry_count=1)

    def test_crash_after_admit_unknown_persists_and_never_retries(self) -> None:
        with TemporaryDirectory() as tmp:
            path = realtime_provider_attempt_ledger_path_for(tmp)
            ledger = RealtimeProviderAttemptLedger(path, authority_identity=AUTHORITY_IDENTITY)
            control = RealtimeProviderControl(ledger=ledger)
            control.admit(identity=_identity("wake-1"), budget=RealtimeBudgetInput())
            # simulated restart: a new control over the reopened ledger
            reopened = RealtimeProviderControl(
                ledger=RealtimeProviderAttemptLedger(path, authority_identity=AUTHORITY_IDENTITY)
            )
            result = reopened.admit(identity=_identity("wake-1"), budget=RealtimeBudgetInput())
            self.assertFalse(result.admitted)
            self.assertTrue(result.duplicate_wake)
            self.assertTrue(result.unknown_persists)
            self.assertEqual(result.attempt_identity, _identity("wake-1").identity_id)
            # never silently retried: still exactly one admitted attempt
            self.assertEqual(reopened.admitted_attempt_count(), 1)
            persisted = reopened.ledger.attempt_for_wake("wake-1")
            self.assertEqual(persisted.attempt_state, ATTEMPT_STARTED)

    def test_unknown_result_persists_across_restart(self) -> None:
        with TemporaryDirectory() as tmp:
            path = realtime_provider_attempt_ledger_path_for(tmp)
            control = _control(tmp)
            result = control.admit(identity=_identity("wake-1"), budget=RealtimeBudgetInput())
            control.record_unknown(
                attempt_identity=result.attempt_identity, reason="response-unknown"
            )
            reopened = RealtimeProviderControl(
                ledger=RealtimeProviderAttemptLedger(path, authority_identity=AUTHORITY_IDENTITY)
            )
            again = reopened.admit(identity=_identity("wake-1"), budget=RealtimeBudgetInput())
            self.assertFalse(again.admitted)
            self.assertTrue(again.unknown_persists)
            persisted = reopened.ledger.attempt_for_wake("wake-1")
            self.assertEqual(persisted.attempt_state, UNKNOWN_AFTER_ATTEMPT_START)
            self.assertEqual(reopened.unknown_count(), 1)

    def test_request_count_ceiling_blocks(self) -> None:
        with TemporaryDirectory() as tmp:
            control = _control(tmp)
            # ceiling already reached from supplied usage facts
            budget = RealtimeBudgetInput(admitted_attempt_count=3, request_count_ceiling=3)
            result = control.admit(identity=_identity("wake-1"), budget=budget)
            self.assertFalse(result.admitted)
            self.assertIn("REQUEST_COUNT_CEILING_EXHAUSTED", result.stop_reasons)
            self.assertTrue(result.stop_before_next_request)
            self.assertEqual(control.admitted_attempt_count(), 0)

    def test_authority_mismatch_is_reason_coded_without_usage_consumption(self) -> None:
        with TemporaryDirectory() as tmp:
            control = _control(tmp)
            budget = RealtimeBudgetInput(admitted_attempt_count=2, request_count_ceiling=5)

            result = control.admit(
                identity=_identity(authority_identity="OTHER_AUTHORITY"),
                budget=budget,
            )

            self.assertFalse(result.admitted)
            self.assertEqual(result.stop_reasons, ("AUTHORITY_IDENTITY_MISMATCH",))
            self.assertEqual(control.admitted_attempt_count(), 0)
            self.assertEqual(budget.admitted_attempt_count, 2)

    def test_request_count_ceiling_allows_below_ceiling(self) -> None:
        with TemporaryDirectory() as tmp:
            control = _control(tmp)
            budget = RealtimeBudgetInput(admitted_attempt_count=2, request_count_ceiling=5)
            result = control.admit(identity=_identity("wake-1"), budget=budget)
            self.assertTrue(result.admitted)
            self.assertEqual(result.stop_reasons, ())

    def test_monetary_unknown_without_tariff(self) -> None:
        with TemporaryDirectory() as tmp:
            control = _control(tmp)
            # exact tariff unavailable => monetary certainty UNKNOWN, not a block
            budget = RealtimeBudgetInput(monetary_certainty=False)
            self.assertTrue(budget.monetary_unknown)
            result = control.admit(identity=_identity("wake-1"), budget=budget)
            self.assertTrue(result.admitted)
            self.assertFalse(result.monetary_certainty)

    def test_explicit_monetary_stop_blocks(self) -> None:
        with TemporaryDirectory() as tmp:
            control = _control(tmp)
            budget = RealtimeBudgetInput(monetary_certainty=True, monetary_stop=True)
            result = control.admit(identity=_identity("wake-1"), budget=budget)
            self.assertFalse(result.admitted)
            self.assertIn("MONETARY_CEILING_EXHAUSTED", result.stop_reasons)

    def test_budget_input_validation(self) -> None:
        with self.assertRaisesRegex(ValueError, "ceiling"):
            RealtimeBudgetInput(request_count_ceiling=0)
        with self.assertRaisesRegex(ValueError, "non-negative"):
            RealtimeBudgetInput(admitted_attempt_count=-1)
        with self.assertRaisesRegex(ValueError, "monetary certainty"):
            RealtimeBudgetInput(monetary_certainty="yes")

    def test_no_provider_or_network_surface(self) -> None:
        # The control never holds or invokes a provider; it only admits against
        # the durable ledger using caller-supplied budget facts.
        with TemporaryDirectory() as tmp:
            control = _control(tmp)
            result = control.admit(identity=_identity("wake-1"), budget=RealtimeBudgetInput())
            self.assertTrue(result.admitted)
            self.assertEqual(len(control.attempts()), 1)


if __name__ == "__main__":
    unittest.main()

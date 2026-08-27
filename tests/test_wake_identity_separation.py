"""Logical vs runtime wake-identity separation tests.

Required invariant:
    same logical replay selection + changed approved prompt/trader identity
    => SAME logical wake-selection identity
    => DIFFERENT runtime wake identity

The logical identity excludes trader/prompt/runtime identity and is bound only to
selection-invariant fields (logical version, frozen wake-policy identity, sealed
slice identity, governed session identity, ordered sequence, exact close time).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from src.fixed_5m_wake_ledger import (
    WAKE_POLICY_IDENTITY,
    Fixed5MWakeLedger,
    logical_wake_selection_identity,
)

TZ = timezone.utc


def _schedule() -> tuple[datetime, ...]:
    start = datetime(2026, 1, 5, 9, 0, tzinfo=TZ)
    return tuple(start + timedelta(minutes=5 * (index + 1)) for index in range(4))


class WakeIdentitySeparationTests(unittest.TestCase):
    def _open(
        self,
        root: Path,
        *,
        trader: str = "trader-1",
        session: str = "session-1",
        slice_identity: str = "slice-1",
    ) -> Fixed5MWakeLedger:
        return Fixed5MWakeLedger(
            root / "wake_ledger.sqlite3",
            trader_identity=trader,
            session_identity=session,
            schedule_5m_closes=_schedule(),
            wake_policy_identity=WAKE_POLICY_IDENTITY,
            slice_identity=slice_identity,
        )

    def test_logical_identity_stable_across_trader_identity_change(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            schedule = _schedule()
            a = self._open(root / "a", trader="trader-a")
            b = self._open(root / "b", trader="trader-b")
            wakes_a = tuple(a.register_closed_5m(close) for close in schedule)
            wakes_b = tuple(b.register_closed_5m(close) for close in schedule)
            for index in range(len(schedule)):
                with self.subTest(sequence=index):
                    self.assertEqual(
                        wakes_a[index].logical_wake_selection_identity,
                        wakes_b[index].logical_wake_selection_identity,
                        "logical identity must not depend on trader identity",
                    )
                    self.assertNotEqual(
                        wakes_a[index].wake_identity,
                        wakes_b[index].wake_identity,
                        "runtime identity must depend on trader identity",
                    )
            self.assertEqual(
                wakes_a[0].wake_identity,
                wakes_a[0].wake_identity,
            )

    def test_logical_identity_changes_when_wake_policy_identity_changes(self) -> None:
        # Logical identity is bound to the frozen wake-policy identity: changing
        # the policy identity changes the logical identity deterministically.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            schedule = _schedule()
            base = self._open(root / "base")
            wakes_base = tuple(base.register_closed_5m(close) for close in schedule)
            other = Fixed5MWakeLedger(
                root / "other" / "wake_ledger.sqlite3",
                trader_identity="trader-1",
                session_identity="session-1",
                schedule_5m_closes=schedule,
                wake_policy_identity="other-policy",
                slice_identity="slice-1",
            )
            wakes_other = tuple(other.register_closed_5m(close) for close in schedule)
            self.assertNotEqual(
                wakes_base[0].logical_wake_selection_identity,
                wakes_other[0].logical_wake_selection_identity,
            )

    def test_logical_identity_changes_with_sequence_time_slice_and_session(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            schedule = _schedule()
            base = self._open(root / "base")
            wakes = tuple(base.register_closed_5m(close) for close in schedule)
            seq0 = wakes[0].logical_wake_selection_identity
            seq1 = wakes[1].logical_wake_selection_identity
            self.assertNotEqual(seq0, seq1, "ordered sequence must alter logical identity")
            # A different exact close time at the same sequence must differ.
            different_close = logical_wake_selection_identity(
                wake_policy_identity=WAKE_POLICY_IDENTITY,
                slice_identity="slice-1",
                session_identity="session-1",
                sequence=0,
                close_time=schedule[0] + timedelta(minutes=5),
            )
            self.assertNotEqual(seq0, different_close)
            # A different slice identity must differ.
            other_slice = logical_wake_selection_identity(
                wake_policy_identity=WAKE_POLICY_IDENTITY,
                slice_identity="slice-2",
                session_identity="session-1",
                sequence=0,
                close_time=schedule[0],
            )
            self.assertNotEqual(seq0, other_slice)
            # A different governed session identity must differ.
            other_session = logical_wake_selection_identity(
                wake_policy_identity=WAKE_POLICY_IDENTITY,
                slice_identity="slice-1",
                session_identity="session-2",
                sequence=0,
                close_time=schedule[0],
            )
            self.assertNotEqual(seq0, other_session)

    def test_runtime_identity_still_binds_trader_and_requests(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = self._open(root)
            wake = ledger.register_closed_5m(_schedule()[0])
            binding = ledger.bind_request(wake.wake_identity, "req-1")
            self.assertEqual(binding.wake_identity, wake.wake_identity)
            self.assertEqual(binding.retry_count, 0)
            # One request may bind to only one wake; one wake admits one request.
            with self.assertRaises(ValueError):
                ledger.bind_request(wake.wake_identity, "req-2")
            second = ledger.register_closed_5m(_schedule()[1])
            with self.assertRaises(ValueError):
                ledger.bind_request(second.wake_identity, "req-1")

    def test_duplicate_and_missing_wakes_still_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = self._open(root)
            schedule = ledger.schedule
            ledger.register_closed_5m(schedule[0])
            with self.assertRaisesRegex(ValueError, "duplicate wake"):
                ledger.register_closed_5m(schedule[0])
            with self.assertRaisesRegex(ValueError, "missing wake"):
                ledger.register_closed_5m(schedule[2])

    def test_wake_records_carry_both_identities_as_first_class(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ledger = self._open(root)
            wake = ledger.register_closed_5m(_schedule()[0])
            self.assertTrue(wake.wake_identity)
            self.assertTrue(wake.logical_wake_selection_identity)
            self.assertNotEqual(wake.wake_identity, wake.logical_wake_selection_identity)
            export = ledger.portable_export()
            self.assertIn("logical_wake_selection_identity", export["wakes"][0])
            self.assertEqual(
                export["wakes"][0]["logical_wake_selection_identity"],
                wake.logical_wake_selection_identity,
            )


if __name__ == "__main__":
    unittest.main()

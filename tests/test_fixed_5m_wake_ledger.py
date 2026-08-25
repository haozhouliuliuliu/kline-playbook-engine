from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from src.fixed_5m_wake_ledger import Fixed5MWakeLedger, WakeLedgerArchive

TZ = timezone.utc


def _closes(start: datetime, count: int = 4) -> tuple[datetime, ...]:
    return tuple(start + timedelta(minutes=5 * (index + 1)) for index in range(count))


class Fixed5MWakeLedgerTests(unittest.TestCase):
    def _open(
        self,
        root: Path,
        *,
        session: str = "session-1",
        schedule: tuple[datetime, ...] | None = None,
    ) -> Fixed5MWakeLedger:
        return Fixed5MWakeLedger(
            root / "wake_ledger.sqlite3",
            trader_identity="trader-1",
            session_identity=session,
            schedule_5m_closes=schedule if schedule is not None else _closes(
                datetime(2026, 1, 5, 9, 0, tzinfo=TZ)
            ),
        )

    def test_each_closed_5m_bar_produces_exactly_one_wake(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = self._open(Path(temp))
            schedule = ledger.schedule
            wakes = tuple(ledger.register_closed_5m(close) for close in schedule)
            self.assertEqual([wake.close_time for wake in wakes], list(schedule))
            self.assertEqual(len({wake.wake_identity for wake in wakes}), len(schedule))
            self.assertEqual(len(ledger.list_wakes()), len(schedule))
            self.assertEqual(ledger.pending_wake_count(), 0)

    def test_one_minute_bar_never_wakes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = self._open(Path(temp))
            with self.assertRaises(ValueError):
                ledger.register_closed_5m(datetime(2026, 1, 5, 9, 1, tzinfo=TZ))

    def test_duplicate_wake_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = self._open(Path(temp))
            schedule = ledger.schedule
            ledger.register_closed_5m(schedule[0])
            with self.assertRaisesRegex(ValueError, "duplicate wake"):
                ledger.register_closed_5m(schedule[0])

    def test_time_regression_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = self._open(Path(temp))
            schedule = ledger.schedule
            ledger.register_closed_5m(schedule[0])
            with self.assertRaisesRegex(ValueError, "missing wake"):
                ledger.register_closed_5m(schedule[2])  # skips schedule[1]
            with self.assertRaisesRegex(ValueError, "duplicate wake"):
                ledger.register_closed_5m(schedule[0])  # re-register earlier close

    def test_missing_wake_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = self._open(Path(temp))
            schedule = ledger.schedule
            ledger.register_closed_5m(schedule[0])
            with self.assertRaisesRegex(ValueError, "missing wake"):
                ledger.register_closed_5m(schedule[2])

    def test_extra_wake_after_schedule_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = self._open(Path(temp))
            for close in ledger.schedule:
                ledger.register_closed_5m(close)
            with self.assertRaises(ValueError):
                ledger.register_closed_5m(ledger.schedule[-1] + timedelta(minutes=5))

    def test_wake_binds_exactly_one_request_and_request_binds_one_wake(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = self._open(Path(temp))
            wake = ledger.register_closed_5m(ledger.schedule[0])
            ledger.bind_request(wake.wake_identity, "req-1")
            with self.assertRaisesRegex(ValueError, "only one model request"):
                ledger.bind_request(wake.wake_identity, "req-2")
            second = ledger.register_closed_5m(ledger.schedule[1])
            with self.assertRaisesRegex(ValueError, "only one governed wake"):
                ledger.bind_request(second.wake_identity, "req-1")

    def test_request_binding_retry_count_fixed_zero(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = self._open(Path(temp))
            wake = ledger.register_closed_5m(ledger.schedule[0])
            with self.assertRaises(ValueError):
                ledger.bind_request(wake.wake_identity, "req-1", retry_count=1)

    def test_bind_request_to_unknown_wake_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = self._open(Path(temp))
            with self.assertRaises(ValueError):
                ledger.bind_request("unknown-wake", "req-1")

    def test_close_session_requires_all_wakes_and_bindings(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            ledger = self._open(Path(temp))
            with self.assertRaises(ValueError):
                ledger.close_session()  # no wakes registered at all
            wakes = []
            for close in ledger.schedule:
                wakes.append(ledger.register_closed_5m(close))
            with self.assertRaisesRegex(ValueError, "unbound wake"):
                ledger.close_session()
            for index, wake in enumerate(wakes):
                ledger.bind_request(wake.wake_identity, f"req-{index}")
            ledger.close_session()  # now complete
            ledger.verify_complete()

    def test_reopen_preserves_records_and_rejects_schedule_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "wake_ledger.sqlite3"
            schedule = _closes(datetime(2026, 1, 5, 9, 0, tzinfo=TZ))
            ledger = Fixed5MWakeLedger(
                path, trader_identity="trader-1", session_identity="session-1", schedule_5m_closes=schedule
            )
            wakes = []
            for index, close in enumerate(schedule):
                wakes.append(ledger.register_closed_5m(close))
            for index, wake in enumerate(wakes):
                ledger.bind_request(wake.wake_identity, f"req-{index}")
            ledger.close_session()
            reopened = Fixed5MWakeLedger(
                path, trader_identity="trader-1", session_identity="session-1", schedule_5m_closes=schedule
            )
            self.assertEqual(len(reopened.list_wakes()), 4)
            self.assertEqual(reopened.list_wakes()[0].request_id, "req-0")
            self.assertEqual(reopened.list_wakes()[-1].request_id, "req-3")
            self.assertTrue(reopened.is_closed())
            drifted = schedule + (schedule[-1] + timedelta(minutes=5),)
            with self.assertRaises(ValueError):
                Fixed5MWakeLedger(
                    path, trader_identity="trader-1", session_identity="session-1", schedule_5m_closes=drifted
                )

    def test_reopen_rejects_different_trader_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "wake_ledger.sqlite3"
            schedule = _closes(datetime(2026, 1, 5, 9, 0, tzinfo=TZ))
            Fixed5MWakeLedger(
                path, trader_identity="trader-1", session_identity="session-1", schedule_5m_closes=schedule
            )
            with self.assertRaises(ValueError):
                Fixed5MWakeLedger(
                    path, trader_identity="other-trader", session_identity="session-1", schedule_5m_closes=schedule
                )

    def test_archive_reconstructs_all_sessions(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "wake_ledger.sqlite3"
            schedule = _closes(datetime(2026, 1, 5, 9, 0, tzinfo=TZ))
            first = Fixed5MWakeLedger(
                path, trader_identity="trader-1", session_identity="session-1", schedule_5m_closes=schedule
            )
            wakes = []
            for index, close in enumerate(schedule):
                wakes.append(first.register_closed_5m(close))
            for index, wake in enumerate(wakes):
                first.bind_request(wake.wake_identity, f"req-{index}")
            first.close_session()
            archive = WakeLedgerArchive(path)
            self.assertEqual(archive.session_identities(), ("session-1",))
            self.assertEqual(archive.schedule("session-1"), schedule)
            self.assertEqual(len(archive.all_wakes()), 4)
            self.assertEqual(len(archive.all_bindings()), 4)


if __name__ == "__main__":
    unittest.main()

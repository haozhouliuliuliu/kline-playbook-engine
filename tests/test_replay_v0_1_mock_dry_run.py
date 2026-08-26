from __future__ import annotations

from datetime import datetime, time, timezone
from pathlib import Path
import tempfile
import unittest

from src.jianghe_ai_trader import ReplayClock
from src.replay_v0_1_mock_dry_run import DeterministicWaitTransport, drive_full_mock_replay
from src.replay_v0_1_orchestrator import ACTIVE_STATE_RESTART_COVERAGE_NOT_OBSERVED, ReplayV01Orchestrator
from tests.replay_v0_1_synthetic_fixture import ReplayV01RuntimeFixture, build_session_steps, build_slice

TZ = timezone.utc


class ReplayV01FullMockDryRunTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fixture = ReplayV01RuntimeFixture(self.root)
        self.slice_ = build_slice()
        self.days = self.slice_.burn_in_days + self.slice_.measurement_days
        self.transport = DeterministicWaitTransport()
        self.orchestrator = ReplayV01Orchestrator(
            runtime_factory=self.fixture.make_runtime_factory(),
            clock=ReplayClock(datetime.combine(self.days[0], time(9, 0), tzinfo=TZ)),
            slice_=self.slice_, transport=self.transport, state_dir=self.root / "state",
        )

    def tearDown(self) -> None:
        try:
            self.orchestrator.runtime.close()
        except Exception:
            pass
        self.temp.cleanup()

    def _steps(self, *, first_day_count: int = 1):
        result = []
        for index, day in enumerate(self.days):
            result.extend(build_session_steps(
                trading_day=day, session_identity=f"session-{index:02d}",
                start=datetime.combine(day, time(9, 0), tzinfo=TZ),
                count=first_day_count if index == 0 else 1, base_price=100.0 + index,
            ))
        return tuple(result)

    def test_complete_22_day_wait_mock_rehearsal_passes(self) -> None:
        summary = drive_full_mock_replay(
            orchestrator=self.orchestrator, slice_=self.slice_, steps=self._steps(), transport=self.transport
        )
        self.assertEqual((summary.replay_day_count, summary.burn_in_day_count, summary.measurement_day_count), (22, 2, 20))
        self.assertEqual(summary.governed_session_count, 22)
        self.assertEqual((summary.step_count, summary.wake_count, summary.request_count, summary.mock_transport_call_count), (22, 22, 22, 22))
        self.assertTrue(summary.r1_restart_verified)
        self.assertFalse(summary.r2_restart_occurred)
        self.assertEqual(summary.active_state_restart_coverage, ACTIVE_STATE_RESTART_COVERAGE_NOT_OBSERVED)
        self.assertFalse(summary.provider_call_authorized)
        self.assertEqual(summary.result, "PASS")
        self.assertEqual(len(summary.identity), 64)

    def test_missing_replay_day_fails_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "coverage disagrees"):
            drive_full_mock_replay(orchestrator=self.orchestrator, slice_=self.slice_, steps=self._steps()[:-1], transport=self.transport)

    def test_extra_replay_day_fails_closed(self) -> None:
        steps = list(self._steps())
        extra_day = self.days[-1].replace(year=2025)
        steps.extend(build_session_steps(trading_day=extra_day, session_identity="extra-session", start=datetime.combine(extra_day, time(9, 0), tzinfo=TZ), count=1))
        with self.assertRaisesRegex(ValueError, "coverage disagrees"):
            drive_full_mock_replay(orchestrator=self.orchestrator, slice_=self.slice_, steps=tuple(steps), transport=self.transport)

    def test_non_causal_order_within_day_fails_closed(self) -> None:
        steps = list(self._steps(first_day_count=2))
        steps[0], steps[1] = steps[1], steps[0]
        with self.assertRaisesRegex(ValueError, "causal order"):
            drive_full_mock_replay(orchestrator=self.orchestrator, slice_=self.slice_, steps=tuple(steps), transport=self.transport)


if __name__ == "__main__":
    unittest.main()

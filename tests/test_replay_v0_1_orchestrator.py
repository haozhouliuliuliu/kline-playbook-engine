from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from src.jianghe_ai_trader import ObservationBar, ReplayClock
from src.replay_v0_1_orchestrator import (
    ACTIVE_STATE_RESTART_COVERAGE_NOT_OBSERVED,
    ACTIVE_STATE_RESTART_COVERAGE_OBSERVED,
    GovernedWakeStep,
    NoProviderTransport,
    PHASE_BURN_IN,
    PHASE_MEASUREMENT,
    ReplayV01Orchestrator,
    SyntheticScriptedTransport,
)
from src.replay_v0_1_selector import BURN_IN_TRADING_DAYS
from tests.replay_v0_1_synthetic_fixture import (
    ReplayV01RuntimeFixture,
    build_session_steps,
    build_slice,
    valid_response,
)

TZ = timezone.utc
WAIT = valid_response(action="WAIT", attention_mode="SCAN", direction="NONE")
WATCH = valid_response(action="WATCH", attention_mode="WATCH", direction="NONE")
CANDIDATE = valid_response(action="CANDIDATE", attention_mode="CANDIDATE", direction="NONE")
ENTER = valid_response(action="ENTER", attention_mode="IN_POSITION", direction="LONG")
MANAGE = valid_response(action="MANAGE", attention_mode="IN_POSITION", direction="LONG")
EXIT = valid_response(action="EXIT", attention_mode="SCAN", direction="NONE")


def _day_start(day: date, hour: int = 9) -> datetime:
    return datetime.combine(day, time(hour), tzinfo=TZ)


class ReplayV01OrchestratorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fixture = ReplayV01RuntimeFixture(self.root)
        self.slice_ = build_slice()
        self.replay_days = self.slice_.burn_in_days + self.slice_.measurement_days

    def tearDown(self) -> None:
        if hasattr(self, "orchestrator") and self.orchestrator is not None:
            try:
                self.orchestrator.runtime.close()
            except Exception:
                pass
        self.temp.cleanup()

    def _make_orchestrator(
        self,
        *,
        responses: list[str],
        initial_time: datetime | None = None,
        transport=None,
    ) -> ReplayV01Orchestrator:
        start = initial_time if initial_time is not None else _day_start(self.replay_days[0])
        clock = ReplayClock(current_time=start)
        mock = transport if transport is not None else SyntheticScriptedTransport(responses)
        self.orchestrator = ReplayV01Orchestrator(
            runtime_factory=self.fixture.make_runtime_factory(),
            clock=clock,
            slice_=self.slice_,
            transport=mock,
            state_dir=self.root / "state",
        )
        return self.orchestrator

    def _drive_session(
        self,
        *,
        phase: str,
        day_index: int,
        session_identity: str,
        count: int = 4,
    ) -> None:
        trading_day = self.replay_days[day_index]
        steps = build_session_steps(
            trading_day=trading_day,
            session_identity=session_identity,
            start=_day_start(trading_day),
            count=count,
        )
        self.orchestrator.begin_session(
            phase=phase,
            trading_day=trading_day,
            replay_day_index=day_index,
            session_identity=session_identity,
            steps=steps,
        )
        for step in steps:
            self.orchestrator.run_wake_step(step)
        self.orchestrator.end_session()

    def test_single_session_binds_all_step_identities(self) -> None:
        self._make_orchestrator(responses=[WAIT] * 4)
        self._drive_session(phase=PHASE_BURN_IN, day_index=0, session_identity="b1-day", count=4)
        bindings = self.orchestrator.list_step_bindings()
        self.assertEqual(len(bindings), 4)
        for binding in bindings:
            self.assertTrue(binding.wake_identity)
            self.assertTrue(binding.observation_identity)
            self.assertTrue(binding.request_id)
            self.assertTrue(binding.decision_identity)
        wake_ids = {binding.wake_identity for binding in bindings}
        request_ids = {binding.request_id for binding in bindings}
        obs_ids = {binding.observation_identity for binding in bindings}
        self.assertEqual(len(wake_ids), 4)
        self.assertEqual(len(request_ids), 4)
        self.assertEqual(len(obs_ids), 4)
        result = self.orchestrator.finalize()
        self.assertEqual(result.step_count, 4)
        self.assertEqual(result.wake_count, 4)
        self.assertEqual(result.request_count, 4)
        # R2 was never armed because the measurement window was never reached.
        self.assertEqual(result.active_state_restart_coverage, "NOT_ARMED")

    def test_higher_timeframe_refresh_never_adds_extra_request(self) -> None:
        responses = [WAIT] * 6
        self._make_orchestrator(responses=responses)
        trading_day = self.replay_days[0]
        steps = build_session_steps(
            trading_day=trading_day, session_identity="s1", start=_day_start(trading_day), count=6
        )
        self.orchestrator.begin_session(
            phase=PHASE_BURN_IN,
            trading_day=trading_day,
            replay_day_index=0,
            session_identity="s1",
            steps=steps,
        )
        for step in steps:
            self.orchestrator.run_wake_step(step)
        self.orchestrator.end_session()
        result = self.orchestrator.finalize()
        # 6 closed 5m bars -> exactly 6 wakes and 6 requests, never more.
        self.assertEqual(result.step_count, 6)
        self.assertEqual(result.wake_count, 6)
        self.assertEqual(result.request_count, 6)

    def test_future_bar_is_rejected_fail_closed(self) -> None:
        responses = [WAIT]
        self._make_orchestrator(responses=responses)
        trading_day = self.replay_days[0]
        steps = build_session_steps(
            trading_day=trading_day, session_identity="s1", start=_day_start(trading_day), count=2
        )
        self.orchestrator.begin_session(
            phase=PHASE_BURN_IN,
            trading_day=trading_day,
            replay_day_index=0,
            session_identity="s1",
            steps=steps,
        )
        future_bar_close = steps[1].wake_bar.close_time
        leaked = list(steps[0].context_bars) + [
            ObservationBar(
                timeframe="5m",
                open_time=future_bar_close - timedelta(minutes=5),
                close_time=future_bar_close,
                available_at=future_bar_close,
                open_price="1", high_price="2", low_price="0", close_price="1",
                volume="1", is_closed=True,
            )
        ]
        future_step = GovernedWakeStep(
            trading_day=steps[0].trading_day,
            session_identity=steps[0].session_identity,
            wake_bar=steps[0].wake_bar,
            context_bars=tuple(leaked),
        )
        with self.assertRaisesRegex(ValueError, "future-bar leak"):
            self.orchestrator.run_wake_step(future_step)

    def test_only_mock_transport_is_admitted(self) -> None:
        start = _day_start(self.replay_days[0])
        with self.assertRaises(ValueError):
            ReplayV01Orchestrator(
                runtime_factory=self.fixture.make_runtime_factory(),
                clock=ReplayClock(current_time=start),
                slice_=self.slice_,
                transport=NoProviderTransport(),
                state_dir=self.root / "state",
            )

    def test_day_index_cannot_skip_or_regress(self) -> None:
        responses = [WAIT] * 4
        self._make_orchestrator(responses=responses)
        trading_day = self.replay_days[0]
        steps = build_session_steps(
            trading_day=trading_day, session_identity="s1", start=_day_start(trading_day), count=4
        )
        self.orchestrator.begin_session(
            phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
            session_identity="s1", steps=steps,
        )
        with self.assertRaises(ValueError):
            self.orchestrator.begin_session(
                phase=PHASE_BURN_IN, trading_day=self.replay_days[1], replay_day_index=1,
                session_identity="s2", steps=steps,
            )  # previous session still open
        for step in steps:
            self.orchestrator.run_wake_step(step)
        self.orchestrator.end_session()
        with self.assertRaisesRegex(ValueError, "skip"):
            self.orchestrator.begin_session(
                phase=PHASE_MEASUREMENT, trading_day=self.replay_days[2], replay_day_index=2,
                session_identity="s3", steps=steps,
            )

    def test_end_session_fails_when_wakes_missing(self) -> None:
        responses = [WAIT] * 4
        self._make_orchestrator(responses=responses)
        trading_day = self.replay_days[0]
        steps = build_session_steps(
            trading_day=trading_day, session_identity="s1", start=_day_start(trading_day), count=4
        )
        self.orchestrator.begin_session(
            phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
            session_identity="s1", steps=steps,
        )
        with self.assertRaises(ValueError):
            self.orchestrator.end_session()  # no wakes registered yet

    def test_r1_phase_boundary_restart_preserves_state(self) -> None:
        total = 2 * 4 + 4 * 4  # burn-in 2 days + measurement 4 days, 4 wakes each
        self._make_orchestrator(responses=[WAIT] * total)
        self._drive_session(phase=PHASE_BURN_IN, day_index=0, session_identity="b1", count=4)
        self._drive_session(phase=PHASE_BURN_IN, day_index=1, session_identity="b2", count=4)
        memory_before = self.orchestrator.runtime.store.load_working_memory()
        journal_before = len(self.orchestrator.runtime.store.list_journal(limit=None))
        hypotheses_before = len(self.orchestrator.runtime.store.list_hypotheses(limit=None))
        sealed = self.orchestrator.phase_boundary_restart()
        self.assertTrue(sealed)
        # reopen preserved trader identity + memory + journal (no reset)
        self.assertEqual(self.orchestrator.runtime.trader_identity.identity, self.fixture.identity.identity)
        memory_after = self.orchestrator.runtime.store.load_working_memory()
        self.assertEqual(memory_after.attention_mode, memory_before.attention_mode)
        self.assertEqual(memory_after.mutation_history, memory_before.mutation_history)
        self.assertEqual(len(self.orchestrator.runtime.store.list_journal(limit=None)), journal_before)
        self.assertEqual(len(self.orchestrator.runtime.store.list_hypotheses(limit=None)), hypotheses_before)
        for day_index in range(BURN_IN_TRADING_DAYS, BURN_IN_TRADING_DAYS + 4):
            self._drive_session(
                phase=PHASE_MEASUREMENT, day_index=day_index, session_identity=f"m{day_index}", count=4
            )
        result = self.orchestrator.finalize()
        self.assertTrue(result.r1_restart_verified)
        self.assertEqual(result.active_state_restart_coverage, ACTIVE_STATE_RESTART_COVERAGE_NOT_OBSERVED)
        self.assertEqual(result.step_count, total)

    def test_r2_active_state_restart_observed(self) -> None:
        responses = [WAIT] * (2 * 4 + 3 * 4) + [WATCH, WAIT, WAIT]
        self._make_orchestrator(responses=responses)
        for day_index in range(BURN_IN_TRADING_DAYS):
            self._drive_session(phase=PHASE_BURN_IN, day_index=day_index, session_identity=f"b{day_index}", count=4)
        self.orchestrator.phase_boundary_restart()
        # measurement day 1-3 (index 2,3,4): WAIT only (not armed until day 4)
        for day_index in range(BURN_IN_TRADING_DAYS, BURN_IN_TRADING_DAYS + 3):
            self._drive_session(phase=PHASE_MEASUREMENT, day_index=day_index, session_identity=f"m{day_index}", count=4)
        # measurement day 4 (index 5): first wake WATCH -> active state -> R2 restart before next wake
        trading_day = self.replay_days[5]
        steps = build_session_steps(
            trading_day=trading_day, session_identity="r2", start=_day_start(trading_day), count=3
        )
        self.orchestrator.begin_session(
            phase=PHASE_MEASUREMENT, trading_day=trading_day, replay_day_index=5,
            session_identity="r2", steps=steps,
        )
        self.orchestrator.run_wake_step(steps[0])  # WATCH -> restart triggered here
        self.assertEqual(self.orchestrator.active_state_restart_coverage(), ACTIVE_STATE_RESTART_COVERAGE_OBSERVED)
        # after restart the remaining wakes continue on the reopened runtime
        self.orchestrator.run_wake_step(steps[1])
        self.orchestrator.run_wake_step(steps[2])
        self.orchestrator.end_session()
        result = self.orchestrator.finalize()
        self.assertTrue(result.r2_restart_occurred)
        self.assertEqual(result.active_state_restart_coverage, ACTIVE_STATE_RESTART_COVERAGE_OBSERVED)
        triggered = [b for b in self.orchestrator.list_step_bindings() if b.active_state_restart_triggered]
        self.assertEqual(len(triggered), 1)
        self.assertEqual(triggered[0].attention_mode_after, "WATCH")

    def test_r2_not_observed_when_no_active_state(self) -> None:
        total = 2 * 4 + 4 * 4
        self._make_orchestrator(responses=[WAIT] * total)
        for day_index in range(BURN_IN_TRADING_DAYS):
            self._drive_session(phase=PHASE_BURN_IN, day_index=day_index, session_identity=f"b{day_index}", count=4)
        self.orchestrator.phase_boundary_restart()
        for day_index in range(BURN_IN_TRADING_DAYS, BURN_IN_TRADING_DAYS + 4):
            self._drive_session(phase=PHASE_MEASUREMENT, day_index=day_index, session_identity=f"m{day_index}", count=4)
        result = self.orchestrator.finalize()
        self.assertEqual(result.active_state_restart_coverage, ACTIVE_STATE_RESTART_COVERAGE_NOT_OBSERVED)
        self.assertFalse(result.r2_restart_occurred)


if __name__ == "__main__":
    unittest.main()

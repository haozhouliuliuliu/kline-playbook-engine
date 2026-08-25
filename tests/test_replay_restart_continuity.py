from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from src.fixed_5m_wake_ledger import wake_ledger_path_for
from src.jianghe_ai_trader import AttentionMode, JiangheWorkingMemory, ReplayClock
from src.persistent_trader_store import PersistentTraderStore
from src.replay_v0_1_orchestrator import (
    PHASE_BURN_IN,
    ReplayStateSealer,
    ReplayV01Orchestrator,
    SyntheticScriptedTransport,
)
from tests.replay_v0_1_synthetic_fixture import (
    ReplayV01RuntimeFixture,
    build_session_steps,
    build_slice,
    valid_response,
)
from tests.test_replay_v0_1_orchestrator import _day_start

TZ = timezone.utc
WAIT = valid_response(action="WAIT", attention_mode="SCAN", direction="NONE")


class ReplayRestartContinuityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fixture = ReplayV01RuntimeFixture(self.root)
        self.slice_ = build_slice()
        self.replay_days = self.slice_.burn_in_days + self.slice_.measurement_days
        self.orchestrator = None

    def tearDown(self) -> None:
        if self.orchestrator is not None:
            try:
                self.orchestrator.runtime.close()
            except Exception:
                pass
        self.temp.cleanup()

    def _make_orchestrator(self, responses: list[str]) -> ReplayV01Orchestrator:
        clock = ReplayClock(current_time=_day_start(self.replay_days[0]))
        self.orchestrator = ReplayV01Orchestrator(
            runtime_factory=self.fixture.make_runtime_factory(),
            clock=clock,
            slice_=self.slice_,
            transport=SyntheticScriptedTransport(responses),
            state_dir=self.root / "state",
        )
        return self.orchestrator

    def test_seal_identity_is_stable_across_close_and_reopen(self) -> None:
        orch = self._make_orchestrator([WAIT] * 2)
        trading_day = self.replay_days[0]
        steps = build_session_steps(
            trading_day=trading_day, session_identity="s1", start=_day_start(trading_day), count=2
        )
        orch.begin_session(
            phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
            session_identity="s1", steps=steps,
        )
        orch.run_wake_step(steps[0])
        wake_db = wake_ledger_path_for(orch.state_dir)
        sealed = ReplayStateSealer.compute_state_identity(
            runtime=orch.runtime, slice_=self.slice_, wake_archive_path=wake_db
        )
        orch.runtime.close()
        reopened = self.fixture.make_runtime_factory()(lambda: orch.clock.current_time)
        try:
            current = ReplayStateSealer.compute_state_identity(
                runtime=reopened, slice_=self.slice_, wake_archive_path=wake_db
            )
            self.assertEqual(current, sealed)
            ReplayStateSealer.assert_continuity(
                sealed_identity=sealed, runtime=reopened,
                slice_=self.slice_, wake_archive_path=wake_db,
            )
        finally:
            reopened.close()

    def test_seal_detects_state_drift(self) -> None:
        orch = self._make_orchestrator([WAIT] * 2)
        trading_day = self.replay_days[0]
        steps = build_session_steps(
            trading_day=trading_day, session_identity="s1", start=_day_start(trading_day), count=2
        )
        orch.begin_session(
            phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
            session_identity="s1", steps=steps,
        )
        orch.run_wake_step(steps[0])
        wake_db = wake_ledger_path_for(orch.state_dir)
        sealed = ReplayStateSealer.compute_state_identity(
            runtime=orch.runtime, slice_=self.slice_, wake_archive_path=wake_db
        )
        # tamper persisted working memory
        store = orch.runtime.store
        tampered = JiangheWorkingMemory(
            attention_mode=AttentionMode.WATCH,
            current_market_hypothesis="injected drift",
        )
        store.save_working_memory(tampered, updated_at=datetime(2026, 1, 5, 9, 5, tzinfo=TZ))
        with self.assertRaisesRegex(ValueError, "state identity drifted"):
            ReplayStateSealer.assert_continuity(
                sealed_identity=sealed, runtime=orch.runtime,
                slice_=self.slice_, wake_archive_path=wake_db,
            )

    def test_mid_session_restart_reopens_in_flight_wake_ledger(self) -> None:
        orch = self._make_orchestrator([WAIT] * 4)
        trading_day = self.replay_days[0]
        steps = build_session_steps(
            trading_day=trading_day, session_identity="s1", start=_day_start(trading_day), count=3
        )
        orch.begin_session(
            phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
            session_identity="s1", steps=steps,
        )
        orch.run_wake_step(steps[0])
        orch.run_wake_step(steps[1])
        self.assertEqual(len(orch.wake_ledger.list_wakes()), 2)
        sealed = orch.restart()  # mid-session restart reopens the wake ledger
        self.assertTrue(sealed)
        self.assertIsNotNone(orch.wake_ledger)
        self.assertEqual(len(orch.wake_ledger.list_wakes()), 2)
        # the reopened ledger continues the same schedule
        orch.run_wake_step(steps[2])
        self.assertEqual(len(orch.wake_ledger.list_wakes()), 3)
        orch.end_session()
        result = orch.finalize()
        self.assertEqual(result.step_count, 3)

    def test_reopen_with_different_trader_identity_fails_closed(self) -> None:
        orch = self._make_orchestrator([WAIT] * 2)
        trading_day = self.replay_days[0]
        steps = build_session_steps(
            trading_day=trading_day, session_identity="s1", start=_day_start(trading_day), count=2
        )
        orch.begin_session(
            phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=0,
            session_identity="s1", steps=steps,
        )
        orch.run_wake_step(steps[0])
        orch.runtime.close()
        with self.assertRaises(ValueError):
            PersistentTraderStore(
                self.fixture.db_path, trader_identity="different-trader"
            )


if __name__ == "__main__":
    unittest.main()

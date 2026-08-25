from __future__ import annotations

from datetime import datetime, time, timezone
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from src.fixed_5m_wake_ledger import (
    GovernedWake,
    WakeBinding,
    WakeLedgerArchive,
)
from src.jianghe_ai_trader import (
    AttentionMode,
    Direction,
    JiangheWorkingMemory,
    ReplayClock,
    StrategyFamily,
)
from src.persistent_trader_store import AuditEvent
from src.replay_integrity import ReplayIntegrityAuditor
from src.replay_v0_1_orchestrator import (
    PHASE_BURN_IN,
    PHASE_MEASUREMENT,
    ReplayV01Orchestrator,
    ReplayResult,
    SyntheticScriptedTransport,
)
from src.replay_v0_1_runtime import ReplayV01Runtime
from src.replay_v0_1_selector import BURN_IN_TRADING_DAYS, ReplaySlice
from tests.replay_v0_1_synthetic_fixture import (
    ReplayV01RuntimeFixture,
    build_slice,
    valid_response,
)
from tests.test_replay_v0_1_orchestrator import _day_start

TZ = timezone.utc
WAIT = valid_response(action="WAIT", attention_mode="SCAN", direction="NONE")


def _obs_payload(*, decision_time: str, bars: list[dict]) -> dict:
    return {
        "semantic_class": "CAUSAL_MULTI_TIMEFRAME_MARKET_OBSERVATION",
        "observation_identity": "obs-1",
        "decision_time": decision_time,
        "exchange_time": decision_time,
        "product": "cu",
        "concrete_contract": "SHFE.cu2405",
        "mapping_identity": "map-cu-20",
        "timeframes": ["4H", "1H", "15m", "5m"],
        "bars": bars,
    }

def _prepared_event(sequence: int, *, request_id: str = "req-1", trader: str = "trader-1", decision_time: str | None = None, bars: list[dict] | None = None) -> AuditEvent:
    dt = decision_time or "2026-01-05T09:05:00+00:00"
    payload = {
        "request_id": request_id,
        "provider": "deepseek",
        "model": "deepseek-v4-flash-vision-exp",
        "runtime_contract": {"identity": "contract-1"},
        "context": {
            "observation": _obs_payload(
                decision_time=dt,
                bars=bars
                if bars is not None
                else [
                    {
                        "timeframe": "5m",
                        "open_time": "2026-01-05T09:00:00+00:00",
                        "close_time": "2026-01-05T09:05:00+00:00",
                        "available_at": "2026-01-05T09:05:00+00:00",
                    }
                ],
            )
        },
    }
    return AuditEvent(
        sequence, f"req-{request_id}-prepared", datetime.fromisoformat(dt), "MODEL_REQUEST_PREPARED_OFFLINE",
        trader, "obs-1", request_id, payload, "unused",
    )


def _raw_event(sequence: int, *, request_id: str = "req-1", occurred: str = "2026-01-05T09:05:00+00:00") -> AuditEvent:
    return AuditEvent(
        sequence, f"req-{request_id}-raw", datetime.fromisoformat(occurred), "MODEL_RESPONSE_RAW",
        "trader-1", "obs-1", request_id, {"raw_response": "{}", "raw_response_sha256": "x"}, "unused",
    )


def _normalized_event(sequence: int, *, request_id: str = "req-1", occurred: str = "2026-01-05T09:05:00+00:00") -> AuditEvent:
    return AuditEvent(
        sequence, f"req-{request_id}-normalized", datetime.fromisoformat(occurred), "MODEL_RESPONSE_NORMALIZED",
        "trader-1", "obs-1", request_id, {"normalized_identity": "n-1", "action": "WAIT"}, "unused",
    )


def _intent_event(
    sequence: int,
    *,
    request_id: str = "req-1",
    before: str = "SCAN",
    after: str = "SCAN",
    action: str = "WAIT",
    direction: str = "NONE",
    occurred: str = "2026-01-05T09:05:00+00:00",
) -> AuditEvent:
    return AuditEvent(
        sequence, f"intent-{sequence}", datetime.fromisoformat(occurred), "REPLAY_INTENT_POSITION",
        "trader-1", "obs-1", request_id,
        {
            "trading_day": "2026-01-05",
            "session_identity": "s1",
            "observation_identity": "obs-1",
            "wake_identity": "wake-1",
            "request_id": request_id,
            "decision_identity": "d-1",
            "action": action,
            "direction": direction,
            "family": "NONE",
            "attention_mode_before": before,
            "attention_mode_after": after,
            "execution_claim": False,
            "paper_fill_claimed": False,
            "intent_only": True,
        },
        "unused",
    )


class _FakeStore:
    def __init__(
        self,
        *,
        events=(),
        memory=None,
        hypotheses=(),
        trader: str = "trader-1",
    ) -> None:
        self._events = tuple(events)
        self._memory = memory if memory is not None else JiangheWorkingMemory()
        self._hypotheses = tuple(hypotheses)
        self._trader = trader

    def list_audit(self):
        return self._events

    def load_working_memory(self):
        return self._memory

    def list_hypotheses(self, limit=None):
        return self._hypotheses

    def portable_export(self):
        return {
            "export_version": "v0.1",
            "store_schema_version": "v0.1",
            "trader_identity": self._trader,
            "harness_opaque_state_included": False,
            "working_memory": {"attention_mode": self._memory.attention_mode.value},
            "journal": [],
            "hypotheses": [],
            "audit": [
                {
                    "sequence": event.sequence,
                    "event_id": event.event_id,
                    "event_kind": event.event_kind,
                    "occurred_at": event.occurred_at.isoformat(),
                    "trader_identity": event.trader_identity,
                    "payload": dict(event.payload),
                }
                for event in self._events
            ],
        }


class _FakeRuntime:
    def __init__(self, store: _FakeStore, trader: str = "trader-1") -> None:
        self.store = store
        self._identity = SimpleNamespace(identity=trader)

    @property
    def trader_identity(self):
        return self._identity

    def portable_export(self):
        return self.store.portable_export()


class _FakeArchive:
    def __init__(
        self,
        *,
        sessions: dict[str, tuple] | None = None,
        wakes=(),
        bindings=(),
        path: Path | None = None,
    ) -> None:
        self._sessions = sessions if sessions is not None else {}
        self._wakes = tuple(wakes)
        self._bindings = tuple(bindings)
        self.path = path if path is not None else Path(tempfile.gettempdir()) / "no-such-wake.sqlite3"

    def session_identities(self):
        return tuple(self._sessions)

    def schedule(self, session_identity: str):
        return self._sessions[session_identity]

    def wakes(self, session_identity: str):
        return self._wakes

    def all_wakes(self):
        return self._wakes

    def all_bindings(self):
        return self._bindings

    def bindings(self, session_identity: str):
        return self._bindings


class ReplayIntegrityAuditorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.slice_ = build_slice()
        self.replay_days = self.slice_.burn_in_days + self.slice_.measurement_days

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _auditor(self, *, runtime, archive, result=None) -> ReplayIntegrityAuditor:
        return ReplayIntegrityAuditor(runtime=runtime, slice_=self.slice_, wake_archive=archive, result=result)

    def test_full_replay_passes_all_integrity_gates(self) -> None:
        fixture = ReplayV01RuntimeFixture(self.root)
        state_dir = self.root / "state"
        total = 2 * 4 + 4 * 4
        clock = ReplayClock(current_time=_day_start(self.replay_days[0]))
        orchestrator = ReplayV01Orchestrator(
            runtime_factory=fixture.make_runtime_factory(),
            clock=clock,
            slice_=self.slice_,
            transport=SyntheticScriptedTransport([WAIT] * total),
            state_dir=state_dir,
        )
        try:
            for day_index in range(BURN_IN_TRADING_DAYS):
                trading_day = self.replay_days[day_index]
                from tests.replay_v0_1_synthetic_fixture import build_session_steps
                steps = build_session_steps(
                    trading_day=trading_day, session_identity=f"b{day_index}", start=_day_start(trading_day), count=4
                )
                orchestrator.begin_session(
                    phase=PHASE_BURN_IN, trading_day=trading_day, replay_day_index=day_index,
                    session_identity=f"b{day_index}", steps=steps,
                )
                for step in steps:
                    orchestrator.run_wake_step(step)
                orchestrator.end_session()
            orchestrator.phase_boundary_restart()
            for day_index in range(BURN_IN_TRADING_DAYS, BURN_IN_TRADING_DAYS + 4):
                trading_day = self.replay_days[day_index]
                from tests.replay_v0_1_synthetic_fixture import build_session_steps
                steps = build_session_steps(
                    trading_day=trading_day, session_identity=f"m{day_index}", start=_day_start(trading_day), count=4
                )
                orchestrator.begin_session(
                    phase=PHASE_MEASUREMENT, trading_day=trading_day, replay_day_index=day_index,
                    session_identity=f"m{day_index}", steps=steps,
                )
                for step in steps:
                    orchestrator.run_wake_step(step)
                orchestrator.end_session()
            result = orchestrator.finalize()
            archive = WakeLedgerArchive(state_dir / "wake_ledger.sqlite3")
            report = self._auditor(runtime=orchestrator.runtime, archive=archive, result=result).audit()
            self.assertTrue(report.passed, [c for c in report.checks if not c.passed])
            report.assert_passed()
        finally:
            orchestrator.runtime.close()

    def test_future_leakage_gate_detects_future_bar(self) -> None:
        future_bars = [
            {
                "timeframe": "5m",
                "open_time": "2026-01-05T09:10:00+00:00",
                "close_time": "2026-01-05T09:15:00+00:00",
                "available_at": "2026-01-05T09:15:00+00:00",
            }
        ]
        events = [_prepared_event(1, bars=future_bars)]
        store = _FakeStore(events=events)
        report = self._auditor(runtime=_FakeRuntime(store), archive=_FakeArchive()).audit()
        self.assertFalse(report.passed)
        self.assertIn("future_leakage", {c.name for c in report.failed_checks()})

    def test_duplicate_missing_wake_gate_detects_missing_wake(self) -> None:
        schedule = (
            datetime(2026, 1, 5, 9, 5, tzinfo=TZ),
            datetime(2026, 1, 5, 9, 10, tzinfo=TZ),
            datetime(2026, 1, 5, 9, 15, tzinfo=TZ),
        )
        wakes = (
            GovernedWake(
                sequence=0, wake_identity="wake-1", session_identity="s1",
                close_time=schedule[0], scheduled_close_time=schedule[0],
                trader_identity="trader-1", request_id="req-1", retry_count=0,
            ),
        )
        store = _FakeStore(events=[_prepared_event(1), _raw_event(2), _normalized_event(3)])
        archive = _FakeArchive(sessions={"s1": schedule}, wakes=wakes, bindings=())
        report = self._auditor(runtime=_FakeRuntime(store), archive=archive).audit()
        self.assertFalse(report.passed)
        self.assertIn("duplicate_missing_wake", {c.name for c in report.failed_checks()})

    def test_duplicate_missing_request_gate_detects_unbound_wake(self) -> None:
        schedule = (datetime(2026, 1, 5, 9, 5, tzinfo=TZ),)
        wakes = (
            GovernedWake(
                sequence=0, wake_identity="wake-1", session_identity="s1",
                close_time=schedule[0], scheduled_close_time=schedule[0],
                trader_identity="trader-1", request_id=None, retry_count=0,
            ),
        )
        store = _FakeStore(events=[_prepared_event(1), _raw_event(2), _normalized_event(3)])
        archive = _FakeArchive(sessions={"s1": schedule}, wakes=wakes, bindings=())
        report = self._auditor(runtime=_FakeRuntime(store), archive=archive).audit()
        self.assertFalse(report.passed)
        self.assertIn("duplicate_missing_request", {c.name for c in report.failed_checks()})

    def test_identity_drift_gate_detects_foreign_trader(self) -> None:
        events = [_prepared_event(1, trader="other-trader")]
        store = _FakeStore(events=events, trader="trader-1")
        report = self._auditor(runtime=_FakeRuntime(store), archive=_FakeArchive()).audit()
        self.assertFalse(report.passed)
        self.assertIn("identity_drift", {c.name for c in report.failed_checks()})

    def test_clock_regression_gate_detects_rollback(self) -> None:
        events = [
            _prepared_event(1, decision_time="2026-01-05T09:05:00+00:00"),
            _prepared_event(2, request_id="req-2", decision_time="2026-01-05T09:00:00+00:00"),
        ]
        store = _FakeStore(events=events)
        report = self._auditor(runtime=_FakeRuntime(store), archive=_FakeArchive()).audit()
        self.assertFalse(report.passed)
        self.assertIn("clock_regression", {c.name for c in report.failed_checks()})

    def test_illegal_state_transition_gate_detects_bad_transition(self) -> None:
        events = [
            _prepared_event(1),
            _raw_event(2),
            _normalized_event(3),
            _intent_event(4, before="SCAN", after="IN_POSITION", action="ENTER", direction="LONG"),
        ]
        store = _FakeStore(events=events)
        report = self._auditor(runtime=_FakeRuntime(store), archive=_FakeArchive()).audit()
        self.assertFalse(report.passed)
        self.assertIn("illegal_state_transition", {c.name for c in report.failed_checks()})

    def test_hypothesis_self_promotion_gate_detects_promotion(self) -> None:
        fake_hypothesis = SimpleNamespace(
            executable_policy=True, status="CANDIDATE", hypothesis_id="h-1"
        )
        store = _FakeStore(events=[], hypotheses=[fake_hypothesis])
        report = self._auditor(runtime=_FakeRuntime(store), archive=_FakeArchive()).audit()
        self.assertFalse(report.passed)
        self.assertIn("hypothesis_self_promotion", {c.name for c in report.failed_checks()})

    def test_audit_reconstruction_gate_detects_missing_response(self) -> None:
        events = [
            _prepared_event(1),
            _raw_event(2),
            # missing normalized response for req-1
            _intent_event(3),
        ]
        store = _FakeStore(events=events)
        report = self._auditor(runtime=_FakeRuntime(store), archive=_FakeArchive()).audit()
        self.assertFalse(report.passed)
        self.assertIn("audit_reconstruction_completeness", {c.name for c in report.failed_checks()})

    def test_memory_reset_gate_detects_mutation_loss(self) -> None:
        memory = JiangheWorkingMemory().mutate(
            field_name="attention_mode",
            new_value=AttentionMode.WATCH,
            reason="x",
            timestamp=datetime(2026, 1, 5, 9, 5, tzinfo=TZ),
            observation_identity="obs-1",
            ai_trader_identity="trader-1",
        )
        events = [
            _prepared_event(1),
            _raw_event(2),
            _normalized_event(3),
            _intent_event(4, before="SCAN", after="WATCH", action="WATCH"),
        ]
        store = _FakeStore(events=events, memory=memory)
        report = self._auditor(runtime=_FakeRuntime(store), archive=_FakeArchive()).audit()
        self.assertFalse(report.passed)
        self.assertIn("memory_reset", {c.name for c in report.failed_checks()})

    def test_restart_continuity_gate_detects_identity_mismatch(self) -> None:
        events = [
            _prepared_event(1),
            _raw_event(2),
            _normalized_event(3),
            _intent_event(4),
        ]
        store = _FakeStore(events=events)
        archive = _FakeArchive()
        fake_result = ReplayResult(
            orchestrator_version="v0.1",
            slice_identity=self.slice_.identity,
            trader_identity="trader-1",
            step_count=1,
            wake_count=1,
            request_count=1,
            r1_restart_verified=False,
            active_state_restart_coverage="NOT_ARMED",
            r2_restart_occurred=False,
            state_identity="0000000000000000000000000000000000000000000000000000000000000000",
        )
        report = self._auditor(runtime=_FakeRuntime(store), archive=archive, result=fake_result).audit()
        self.assertFalse(report.passed)
        self.assertIn("restart_continuity", {c.name for c in report.failed_checks()})


if __name__ == "__main__":
    unittest.main()

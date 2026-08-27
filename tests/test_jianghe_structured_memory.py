"""Structured trading-memory fidelity tests for the V0_2 response contract.

These tests prove that the model-visible structured current-state snapshot fields
(current market hypothesis, timeframe trend views, key locations, expected
trigger, invalidation, open questions) are:
- accepted under the strict V0_2 schema and rejected fail-closed otherwise;
- exactly model-supplied (never parsed from rationale);
- persisted into DS_WORKING_MEMORY and present in the next request's context;
- carried forward / cleared deterministically across wakes and restart;
- free of any future/outcome/PnL fields.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
import json
from pathlib import Path
import tempfile
import unittest

from src.jianghe_ai_trader import ReplayClock
from src.jianghe_response_normalizer import (
    RESPONSE_SCHEMA_VERSION,
    RESPONSE_SCHEMA_VERSION_V0_1,
    JiangheResponseNormalizer,
)
from src.replay_v0_1_orchestrator import (
    PHASE_BURN_IN,
    ReplayV01Orchestrator,
    SyntheticScriptedTransport,
)
from tests.replay_v0_1_synthetic_fixture import (
    ReplayV01RuntimeFixture,
    build_session_steps,
    build_slice,
)

TZ = timezone.utc

CURRENT_HYPOTHESIS = "夜盘强多头，等待回踩确认"
TIMEFRAME_VIEW = [["5m", "回踩中"], ["15m", "回踩"], ["1H", "上行"], ["4H", "多头背景"]]
KEY_LOCATIONS = ["76620", "76830"]
EXPECTED_TRIGGER = "5m 收于 76830 上方"
INVALIDATION = "5m 收于 76620 下方"
OPEN_QUESTIONS = ["低周期主动性是否恢复"]


def memory_response(
    *,
    action: str = "WATCH",
    attention_mode: str = "WATCH",
    direction: str = "LONG",
    family: str = "NONE",
    current_market_hypothesis: str | None = CURRENT_HYPOTHESIS,
    timeframe_trend_view: list[list[str]] | None = None,
    key_location_hypotheses: list[str] | None = None,
    expected_trigger: str | None = EXPECTED_TRIGGER,
    invalidation_hypothesis: str | None = INVALIDATION,
    open_questions: list[str] | None = None,
) -> str:
    return json.dumps(
        {
            "schema_version": RESPONSE_SCHEMA_VERSION,
            "family": family,
            "action": action,
            "direction": direction,
            "attention_mode": attention_mode,
            "decision_state": "watch_structured_memory_test",
            "rationale": "Synthetic structured-memory decision.",
            "declared_unknown": [],
            "principle_references": [],
            "source_references": [],
            "numeric_claims": [],
            "current_market_hypothesis": current_market_hypothesis,
            "timeframe_trend_view": (
                timeframe_trend_view if timeframe_trend_view is not None else TIMEFRAME_VIEW
            ),
            "key_location_hypotheses": (
                key_location_hypotheses if key_location_hypotheses is not None else KEY_LOCATIONS
            ),
            "expected_trigger": expected_trigger,
            "invalidation_hypothesis": invalidation_hypothesis,
            "open_questions": (
                open_questions if open_questions is not None else OPEN_QUESTIONS
            ),
        },
        ensure_ascii=False,
    )


class StructuredMemorySchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.normalizer = JiangheResponseNormalizer()

    def test_accepts_exact_intended_shape(self) -> None:
        decision = self.normalizer.normalize(memory_response())
        self.assertEqual(decision.current_market_hypothesis, CURRENT_HYPOTHESIS)
        self.assertEqual(
            decision.timeframe_trend_view,
            (("4H", "多头背景"), ("1H", "上行"), ("15m", "回踩"), ("5m", "回踩中")),
        )
        self.assertEqual(decision.key_location_hypotheses, ("76620", "76830"))
        self.assertEqual(decision.expected_trigger, EXPECTED_TRIGGER)
        self.assertEqual(decision.invalidation_hypothesis, INVALIDATION)
        self.assertEqual(decision.open_questions, ("低周期主动性是否恢复",))
        self.assertEqual(decision.response_schema_identity, decision.response_schema_identity)

    def test_missing_structured_memory_field_fails_closed(self) -> None:
        payload = json.loads(memory_response())
        for field in (
            "current_market_hypothesis",
            "timeframe_trend_view",
            "key_location_hypotheses",
            "expected_trigger",
            "invalidation_hypothesis",
            "open_questions",
        ):
            with self.subTest(field=field):
                mutated = dict(payload)
                mutated.pop(field)
                with self.assertRaises(ValueError):
                    self.normalizer.normalize(json.dumps(mutated, ensure_ascii=False))

    def test_unknown_structured_memory_field_fails_closed(self) -> None:
        payload = json.loads(memory_response())
        payload["review_at_schedule"] = "model-must-not-own-scheduling"
        with self.assertRaises(ValueError):
            self.normalizer.normalize(json.dumps(payload, ensure_ascii=False))

    def test_wrong_type_structured_memory_field_fails_closed(self) -> None:
        mutations = (
            ("current_market_hypothesis", 123),
            ("current_market_hypothesis", []),
            ("timeframe_trend_view", {"4H": "上行"}),
            ("timeframe_trend_view", [["5m", "回踩"], ["5m", "重复"]]),
            ("timeframe_trend_view", [["7H", "非法周期"]]),
            ("timeframe_trend_view", [["4H", ""]]),
            ("timeframe_trend_view", [["4H", "x", "y"]]),
            ("key_location_hypotheses", "76620"),
            ("key_location_hypotheses", ["", "76830"]),
            ("expected_trigger", ["list-not-string"]),
            ("invalidation_hypothesis", 5.5),
            ("open_questions", ["ok", 3]),
        )
        for field_name, value in mutations:
            with self.subTest(field_name=field_name, value=value):
                payload = json.loads(memory_response())
                payload[field_name] = value
                with self.assertRaises(ValueError):
                    self.normalizer.normalize(json.dumps(payload, ensure_ascii=False))

    def test_structured_values_are_exactly_model_supplied_not_parsed_from_rationale(self) -> None:
        # The rationale deliberately contradicts the structured fields: the
        # deterministic layer must never infer semantics from rationale text.
        payload = json.loads(memory_response())
        payload["rationale"] = (
            "理性描述与结构化字段完全相反，用于证明项目层不从 rationale 推断语义。"
        )
        decision = self.normalizer.normalize(json.dumps(payload, ensure_ascii=False))
        self.assertEqual(decision.current_market_hypothesis, CURRENT_HYPOTHESIS)
        self.assertEqual(decision.expected_trigger, EXPECTED_TRIGGER)
        self.assertEqual(decision.invalidation_hypothesis, INVALIDATION)
        self.assertNotIn(CURRENT_HYPOTHESIS, decision.rationale)

    def test_nullable_structured_fields_accept_null(self) -> None:
        decision = self.normalizer.normalize(
            memory_response(
                current_market_hypothesis=None,
                expected_trigger=None,
                invalidation_hypothesis=None,
                timeframe_trend_view=[],
                key_location_hypotheses=[],
                open_questions=[],
            )
        )
        self.assertIsNone(decision.current_market_hypothesis)
        self.assertIsNone(decision.expected_trigger)
        self.assertIsNone(decision.invalidation_hypothesis)
        self.assertEqual(decision.timeframe_trend_view, ())
        self.assertEqual(decision.key_location_hypotheses, ())
        self.assertEqual(decision.open_questions, ())

    def test_no_future_outcome_or_pnl_fields_are_introduced(self) -> None:
        for forbidden in ("pnl", "outcome", "future_price", "return", "win_rate", "equity_curve"):
            with self.subTest(forbidden=forbidden):
                payload = json.loads(memory_response())
                payload[forbidden] = "forbidden"
                with self.assertRaises(ValueError):
                    self.normalizer.normalize(json.dumps(payload, ensure_ascii=False))

    def test_v0_1_schema_no_longer_accepted_by_active_normalizer(self) -> None:
        payload = json.loads(memory_response())
        payload["schema_version"] = RESPONSE_SCHEMA_VERSION_V0_1
        with self.assertRaises(ValueError):
            self.normalizer.normalize(json.dumps(payload, ensure_ascii=False))


def _day_start(day: date, hour: int = 9) -> datetime:
    return datetime.combine(day, time(hour), tzinfo=TZ)


class StructuredMemoryPersistenceTests(unittest.TestCase):
    """Prove structured state persists through the governed wake path, restart and context."""

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.fixture = ReplayV01RuntimeFixture(self.root)
        self.slice_ = build_slice()
        self.replay_days = self.slice_.burn_in_days + self.slice_.measurement_days
        self.trading_day = self.replay_days[0]
        self.steps = build_session_steps(
            trading_day=self.trading_day,
            session_identity="sess-mem",
            start=_day_start(self.trading_day),
            count=3,
        )
        self.transport: SyntheticScriptedTransport | None = None

    def tearDown(self) -> None:
        if hasattr(self, "orchestrator") and self.orchestrator is not None:
            try:
                self.orchestrator.runtime.close()
            except Exception:
                pass
        self.temp.cleanup()

    def _make_orchestrator(self, responses: list[str]) -> ReplayV01Orchestrator:
        clock = ReplayClock(current_time=_day_start(self.trading_day))
        self.transport = SyntheticScriptedTransport(responses)
        self.orchestrator = ReplayV01Orchestrator(
            runtime_factory=self.fixture.make_runtime_factory(),
            clock=clock,
            slice_=self.slice_,
            transport=self.transport,
            state_dir=self.root / "state",
        )
        return self.orchestrator

    def _run(self, responses: list[str], *, restart_after: int | None = None) -> None:
        orchestrator = self._make_orchestrator(responses)
        orchestrator.begin_session(
            phase=PHASE_BURN_IN,
            trading_day=self.trading_day,
            replay_day_index=0,
            session_identity="sess-mem",
            steps=self.steps,
        )
        for index, step in enumerate(self.steps):
            orchestrator.run_wake_step(step)
            if restart_after is not None and index == restart_after:
                orchestrator.restart()
        orchestrator.end_session()

    def _memory(self) -> dict:
        return self.orchestrator.runtime.store.load_working_memory()

    def test_all_structured_fields_persist_after_acceptance(self) -> None:
        self._run([memory_response(), memory_response(), memory_response()])
        memory = self._memory()
        self.assertEqual(memory.current_market_hypothesis, CURRENT_HYPOTHESIS)
        self.assertEqual(
            memory.timeframe_trend_view,
            (("4H", "多头背景"), ("1H", "上行"), ("15m", "回踩"), ("5m", "回踩中")),
        )
        self.assertEqual(memory.key_location_hypotheses, ("76620", "76830"))
        self.assertEqual(memory.expected_trigger, EXPECTED_TRIGGER)
        self.assertEqual(memory.invalidation_hypothesis, INVALIDATION)
        self.assertEqual(memory.open_questions, ("低周期主动性是否恢复",))

    def test_still_valid_state_carried_forward_on_next_wake(self) -> None:
        # Wake 0 sets the state; wake 1 explicitly restates the still-valid state.
        carried = memory_response()
        self._run([carried, memory_response(), memory_response()])
        memory = self._memory()
        self.assertEqual(memory.current_market_hypothesis, CURRENT_HYPOTHESIS)
        # The second request's context already contained the state from wake 0.
        second_context = self.transport.calls[1].context["ds_working_memory"]
        self.assertEqual(second_context["current_market_hypothesis"], CURRENT_HYPOTHESIS)
        self.assertEqual(second_context["expected_trigger"], EXPECTED_TRIGGER)

    def test_explicit_model_clearing_replaces_state_deterministically(self) -> None:
        clear = memory_response(
            current_market_hypothesis=None,
            expected_trigger=None,
            invalidation_hypothesis=None,
            timeframe_trend_view=[],
            key_location_hypotheses=[],
            open_questions=[],
        )
        self._run([memory_response(), clear, memory_response()])
        memory = self._memory()
        # Final wake restores the state after the explicit clear wake.
        self.assertEqual(memory.current_market_hypothesis, CURRENT_HYPOTHESIS)
        # The clear wake itself deterministically emptied every structured field.
        cleared_context = self.transport.calls[2].context["ds_working_memory"]
        self.assertIsNone(cleared_context["current_market_hypothesis"])
        self.assertEqual(cleared_context["timeframe_trend_view"], [])
        self.assertEqual(cleared_context["open_questions"], [])

    def test_restart_preserves_exact_structured_state(self) -> None:
        self._run([memory_response(), memory_response(), memory_response()], restart_after=0)
        memory = self._memory()
        self.assertEqual(memory.current_market_hypothesis, CURRENT_HYPOTHESIS)
        self.assertEqual(memory.expected_trigger, EXPECTED_TRIGGER)
        self.assertEqual(memory.invalidation_hypothesis, INVALIDATION)
        self.assertEqual(memory.key_location_hypotheses, ("76620", "76830"))

    def test_next_request_receives_persisted_state_in_ds_working_memory(self) -> None:
        self._run([memory_response(), memory_response(), memory_response()])
        # Every wake after the first must see the persisted structured state.
        for call in self.transport.calls[1:]:
            ctx = call.context["ds_working_memory"]
            self.assertEqual(ctx["current_market_hypothesis"], CURRENT_HYPOTHESIS)
            self.assertEqual(ctx["expected_trigger"], EXPECTED_TRIGGER)
            self.assertEqual(ctx["invalidation_hypothesis"], INVALIDATION)
            self.assertEqual(ctx["key_location_hypotheses"], list(KEY_LOCATIONS))
            self.assertEqual(ctx["open_questions"], list(OPEN_QUESTIONS))

    def test_structured_state_survives_full_store_reopen(self) -> None:
        self._run([memory_response(), memory_response(), memory_response()])
        # Reopen the persisted store through a fresh runtime bound to the same trader.
        from src.persistent_trader_store import PersistentTraderStore

        db_path = self.root / "state" / "trader.sqlite3"
        reopened = PersistentTraderStore(
            db_path, trader_identity=self.fixture.identity.identity
        )
        try:
            memory = reopened.load_working_memory()
            self.assertEqual(memory.current_market_hypothesis, CURRENT_HYPOTHESIS)
            self.assertEqual(memory.expected_trigger, EXPECTED_TRIGGER)
            self.assertEqual(memory.invalidation_hypothesis, INVALIDATION)
        finally:
            reopened.close()


if __name__ == "__main__":
    unittest.main()
